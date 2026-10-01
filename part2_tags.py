"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from load_data import load_all

MY_MOVIE = 593  # The Silence of the Lambs (1991)
REPO = Path(__file__).resolve().parent
FIGURES = REPO / "figures"


def my_ten_movies() -> list[int]:
    """The movieIds in the "My ten movies" slot of WRITEUP.md, in order."""
    text = (REPO / "WRITEUP.md").read_text(encoding="utf-8")
    slot = text.split("**My ten movies")[-1]
    return [int(n) for n in re.findall(r"^\s*(\d+)", slot.split("\n**")[0], re.M)]

# score(movie, tag): the mean rating of the users who applied the tag to the movie,
# mapped linearly onto 0-10 by its distance from the rating scale's midpoint (2.75).
# A tag whose taggers rated the movie right at 2.75 says nothing about quality (score 0);
# one whose taggers rated it at either extreme (0.5 or 5.0) scores 10.
RATING_MIDPOINT = 2.75
RATING_HALF_RANGE = 2.25  # max(5.0 - 2.75, 2.75 - 0.5)

# A rare normalized tag (at most this many applications, dataset-wide) is folded
# into a one-edit-apart neighbor only if that neighbor is at least DOMINANCE times
# more common. Two real, comparably common words are never merged: this is
# deliberately a one-way rare-into-dominant rule, not a mutual clustering, so a
# chain of individually-plausible merges can't drag unrelated common words (e.g.
# "slow", "story") together the way a transitive union-find did in an earlier,
# broken version of this function.
MERGE_RARE_MAX = 10
MERGE_DOMINANCE = 20


def normalize_tag(tag: str) -> str:
    """Fold case and whitespace, drop punctuation, and naively strip a trailing
    plural 's'."""
    s = tag.strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > 3 and s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return s


def _one_edit_apart(a: str, b: str) -> bool:
    """True if a and b differ by exactly one substitution, insertion, deletion,
    or adjacent transposition (Damerau-Levenshtein distance 1)."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diffs = [i for i in range(la) if a[i] != b[i]]
        if len(diffs) == 1:
            return True
        if len(diffs) == 2 and diffs[1] == diffs[0] + 1:
            i = diffs[0]
            return a[i] == b[i + 1] and a[i + 1] == b[i]
        return False
    if la > lb:
        a, b = b, a
    i = j = 0
    skipped = False
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        elif not skipped:
            skipped = True
            j += 1
        else:
            return False
    return True


def _mergeable(s: str) -> bool:
    """Tags under 4 characters and purely numeric tags (years) never merge,
    on either side of a merge."""
    return len(s) >= 4 and not s.replace(" ", "").isdigit()


def clean_tags(tags):
    """Map every raw tag string to a cleaned, merged tag. Returns
    (clean_series, raw_norm_counts, canonical_map). canonical_map only has
    entries for the rare normalized strings that got folded into a dominant
    one-edit-apart neighbor; every other normalized string maps to itself.

    A merge additionally requires the two normalized tags to co-occur: both
    must have been applied to at least one of the same movies. Edit-distance-1
    alone can't tell a typo from a genuinely different, just-rarer word (e.g.
    'face' is one edit from 'farce' but is its own word); requiring the pair
    to share a movie cuts that risk, since unrelated words rarely land on the
    same movie's tag list by chance, though it is not a guarantee."""
    norm = tags["tag"].map(normalize_tag)
    counts = norm.value_counts()
    movies_of = tags.assign(norm=norm).groupby("norm")["movieId"].apply(set)

    buckets = defaultdict(list)
    for key in counts.index:
        buckets[(key[:1], len(key) // 2)].append(key)

    canonical = {}
    for cand in (k for k in counts.index
                 if counts[k] <= MERGE_RARE_MAX and _mergeable(k)):
        best, best_n = None, 0
        for other in buckets[(cand[:1], len(cand) // 2)]:
            if other == cand or counts[other] <= best_n or not _mergeable(other):
                continue
            if (counts[other] >= MERGE_DOMINANCE * max(counts[cand], 1)
                    and _one_edit_apart(cand, other)
                    and movies_of[cand] & movies_of[other]):
                best, best_n = other, counts[other]
        if best is not None:
            canonical[cand] = best

    full_map = {k: canonical.get(k, k) for k in counts.index}
    return norm.map(full_map), counts, full_map


def score(tags_df, ratings_df, movies_df):
    """One row per (movieId, tag), scoring how well the tag describes the movie:
    10 * |mean rating of its taggers - 2.75| / 2.25."""
    clean, *_ = clean_tags(tags_df)
    tagged = tags_df.assign(tag=clean).merge(
        ratings_df[["userId", "movieId", "rating"]], on=["userId", "movieId"])
    mean_rating = tagged.groupby(["movieId", "tag"])["rating"].mean()
    s = 10 * (mean_rating - RATING_MIDPOINT).abs() / RATING_HALF_RANGE
    return s.rename("score").reset_index()


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MY_MOVIE, "title"]
    my_ratings = ratings[ratings.movieId == MY_MOVIE]
    my_tags = tags[tags.movieId == MY_MOVIE]
    print(f"{title} (movieId {MY_MOVIE}): {len(my_ratings):,} ratings, "
          f"{len(my_tags):,} tag applications")
    counts = my_tags["tag"].value_counts()
    for tag, n in counts.items():
        print(f"{n:4d}  {tag}")

    print("== (2) up close ==")
    r_month = (pd.to_datetime(my_ratings["timestamp"], unit="s")
               .dt.to_period("M").value_counts().sort_index())
    t_month = (pd.to_datetime(my_tags["timestamp"], unit="s")
               .dt.to_period("M").value_counts().sort_index())
    print("ratings per month (first 5):")
    print(r_month.head(5).to_string())
    print("ratings per month (last 5):")
    print(r_month.tail(5).to_string())
    print("tag applications per month (first 5):")
    print(t_month.head(5).to_string())
    print("tag applications per month (last 5):")
    print(t_month.tail(5).to_string())

    FIGURES.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    r_x = r_month.index.to_timestamp()
    t_x = t_month.index.to_timestamp()
    ax.fill_between(r_x, r_month.to_numpy(), color="#1b7a3d", alpha=0.35,
                     step="mid", label="ratings")
    ax.plot(t_x, t_month.to_numpy(), color="#b2182b", linewidth=2,
            label="tag applications")
    ax.set_xlabel("date")
    ax.set_ylabel("count per month")
    ax.set_title(f"{title}: when ratings and tags arrived")
    ax.legend()
    fig.text(0.01, -0.02, "When did the tags and the ratings on this movie arrive?",
              ha="left", fontsize=9, style="italic")
    fig.tight_layout()
    fig.savefig(FIGURES / "part2_when.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {FIGURES / 'part2_when.png'}")

    print()
    print("-- who added each tag (heaviest taggers) --")
    by_user = my_tags.groupby("userId").size().sort_values(ascending=False)
    total_tags = len(my_tags)
    for uid, n in by_user.head(10).items():
        print(f"user {uid}: {n} applications, {n / total_tags:.2%} of this movie's tags")

    print()
    print("-- how the taggers rated it, by top tag --")
    top_tags = counts.head(10).index
    for tag in top_tags:
        taggers = pd.Index(my_tags.loc[my_tags["tag"] == tag, "userId"].unique())
        tagger_ratings = my_ratings[my_ratings["userId"].isin(taggers)]["rating"]
        other_ratings = my_ratings[~my_ratings["userId"].isin(taggers)]["rating"]
        print(f"{tag!r}: taggers' mean {tagger_ratings.mean():.2f} "
              f"(n={len(tagger_ratings)}), everyone else's mean "
              f"{other_ratings.mean():.2f} (n={len(other_ratings)})")

    print("== (3) my definition ==")
    scores = score(tags, ratings, movies)
    my_scores = (scores[scores.movieId == MY_MOVIE]
                 .sort_values("score", ascending=False))
    print(f"top 15 rows for {title}:")
    print(my_scores.head(15).to_string(index=False))
    print(f"\n{len(scores):,} (movieId, tag) rows over the whole set, "
          f"{scores.movieId.nunique():,} distinct movies")

    print("== (4) cleaning ==")
    clean, norm_counts, canonical = clean_tags(tags)
    n_raw = tags["tag"].nunique()
    n_clean = clean.nunique()
    print(f"{n_raw:,} distinct raw tag strings in, {n_clean:,} distinct cleaned tags out")
    absorbed_by = defaultdict(list)
    for cand, rep in canonical.items():
        if cand != rep:
            absorbed_by[rep].append(cand)
    merges = [(sum(norm_counts[c] for c in cands), rep, cands)
              for rep, cands in absorbed_by.items()]
    merges.sort(key=lambda m: -m[0])
    print("five mergers that absorbed the most applications:")
    for absorbed, rep, others in merges[:5]:
        print(f"{absorbed:4d} applications merged into {rep!r}, from {others}")

    print("== (5) scores.csv ==")
    judge_movies = pd.read_csv(REPO / "judge" / "movies.csv", keep_default_na=False)
    pairs = set()
    for _, row in judge_movies.iterrows():
        for t in str(row["tags"]).split("|"):
            if t:
                pairs.add((row["id"], t))

    vocab = {w.strip() for w in
             (REPO / "judge" / "vocabulary.txt").read_text().splitlines() if w.strip()}
    mine = my_ten_movies()
    lowered = tags.assign(tag=tags["tag"].str.strip().str.lower())
    on_mine = lowered[lowered["movieId"].isin(mine) & lowered["tag"].isin(vocab)]
    for mid, tag in on_mine[["movieId", "tag"]].drop_duplicates().itertuples(index=False):
        pairs.add((mid, tag))

    scored = scores.set_index(["movieId", "tag"])["score"]
    rows = [{"movieId": m, "tag": t, "score": scored.get((m, t))} for m, t in pairs]
    out = pd.DataFrame(rows).dropna(subset=["score"])
    out.to_csv(REPO / "scores.csv", index=False)
    print(f"{len(pairs):,} (movieId, tag) pairs asked for, {len(out):,} written to scores.csv")

    print("== (6) the four rankings ==")
    from agreement import my_order_lines
    judge_path = REPO / "judge" / "ratings_movies.csv"
    if not judge_path.exists():
        print("judge/ratings_movies.csv is not here yet; run the judge first.")
    else:
        judge_df = pd.read_csv(judge_path, keep_default_na=False)
        mine_order = my_order_lines()
        titles = movies.set_index("movieId")["title"]
        for mid in my_ten_movies():
            print(f"\n{titles.get(mid, mid)} (movieId {mid})")

            by_count = (tags[tags["movieId"] == mid]["tag"]
                        .value_counts().head(10).index.tolist())
            print("the counts:", ", ".join(by_count) if by_count else "(none)")

            own = mine_order.get(mid, [])
            print("your own order:", ", ".join(own) if own else "not written yet")

            j = judge_df[judge_df["id"] == mid].sort_values(
                ["rating", "tag"], ascending=[False, True])
            print("the judge's order:",
                  ", ".join(j["tag"].head(10)) if len(j) else "(not rated)")

            s = (scores[scores["movieId"] == mid]
                 .sort_values(["score", "tag"], ascending=[False, True]))
            print("your score()'s order:",
                  ", ".join(s["tag"].head(10)) if len(s) else "(no scores)")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
