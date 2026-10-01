"""User Results Viewer.

Builds one self-contained HTML page for a user: the genres that qualified for them under
`score()` (the genres among their top/bottom-quartile movies), the TOP_N_TAGS_PER_GENRE
most-used tags for each of those genres, and the user's average rating over every movie they
rated in that genre.

    uv run python user_results.py            # writes user_results.html, for userId 999999
    uv run python user_results.py --text     # the same content as plain text
    uv run python user_results.py --user 123 # a different userId

This is a first draft, written to one spec: genres used, each genre's top tags, and the
user's average rating per genre. Nothing else is shown yet.
"""

import argparse
import html
from pathlib import Path

import pandas as pd

from load_data import load_all
from part3_users import ME, TOP_N_TAGS_PER_GENRE, _genre_top_tags, add_me, read_my_ratings, score
from results_viewer import diff_color

REPO = Path(__file__).resolve().parent
JUDGE_RATINGS = REPO / "judge" / "ratings_users.csv"

CSS = """body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }
table { border-collapse: collapse; margin-bottom: 12px; }
th, td { border: 1px solid #999999; padding: 4px 8px; text-align: left; }"""


def build(user_id, ratings, tags, movies):
    """One dict per genre that qualified for this user: its top tags and the user's
    average rating over every movie of theirs in that genre."""
    exploded = movies.assign(genre=movies["genres"].str.split("|")).explode("genre")
    exploded = exploded[exploded["genre"] != "(no genres listed)"][["movieId", "genre"]]

    mine = ratings[ratings["userId"] == user_id]
    if mine.empty:
        return []
    low_cut, high_cut = mine["rating"].quantile([0.25, 0.75])
    extreme = mine[(mine["rating"] >= high_cut) | (mine["rating"] <= low_cut)]
    extreme = extreme.merge(exploded, on="movieId")
    qualifying_genres = sorted(extreme["genre"].unique())

    mine_by_genre = mine.merge(exploded, on="movieId")
    avg_by_genre = mine_by_genre.groupby("genre")["rating"].mean()
    count_by_genre = mine_by_genre.groupby("genre")["movieId"].nunique()

    genre_tags = _genre_top_tags(tags, movies)
    out = []
    for genre in qualifying_genres:
        top_tags = list(genre_tags[genre_tags["genre"] == genre]
                         .sort_values("genre_tag_count", ascending=False)["tag"])
        out.append({
            "genre": genre,
            "tags": top_tags[:TOP_N_TAGS_PER_GENRE],
            "avg_rating": round(float(avg_by_genre.get(genre, float("nan"))), 2),
            "n_ratings": int(count_by_genre.get(genre, 0)),
        })
    return out


def judge_comparison(user_id, ratings, tags, movies):
    """Every tag the judge rated for this user, next to this user's own score().

    Returns a sorted list of (tag, my_score, judge_rating); my_score is None where the
    tag the judge rated isn't one score() returned for this user."""
    if not JUDGE_RATINGS.exists():
        return None
    judge = pd.read_csv(JUDGE_RATINGS, keep_default_na=False)
    judge = judge[judge["id"] == user_id]
    if judge.empty:
        return []
    mine_scores = score(ratings, tags, movies)
    mine_scores = mine_scores[mine_scores["userId"] == user_id].set_index("tag")["score"]
    out = [(row.tag, mine_scores.get(row.tag), row.rating) for row in judge.itertuples()]
    out = [(tag, None if my is None else int(my), judge) for tag, my, judge in out]
    return sorted(out, key=lambda t: abs(t[1] - t[2]) if t[1] is not None else float("inf"))


def shared_tags(genres):
    """tag -> list of qualifying genres whose top list contains it, for every tag that
    shows up in at least two of those genres' top lists."""
    by_tag = {}
    for g in genres:
        for tag in g["tags"]:
            by_tag.setdefault(tag, []).append(g["genre"])
    return {tag: gs for tag, gs in by_tag.items() if len(gs) >= 2}


def comparison_table_html(comparison):
    """Tag, my score(), judge rating, and a signed Difference column (my score() minus the
    judge's rating), shaded green when positive and red when negative, darker the further
    from zero, as `results_viewer.py` shades the movie disagreements."""
    headers = ["Tag", "My score()", "Judge rating", "Difference"]
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    diffs = [None if my is None else my - judge for _, my, judge in comparison]
    max_abs = max((abs(d) for d in diffs if d is not None), default=0)
    rows = []
    for (tag, my, judge), diff in zip(comparison, diffs):
        diff_cell = ("<td></td>" if diff is None else
                     '<td style="background-color: %s">%+d</td>' % (diff_color(diff, max_abs), diff))
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td>%s</tr>" %
                     (html.escape(tag), "" if my is None else my, judge, diff_cell))
    return "<table><tr>%s</tr>%s</table>" % (head, "".join(rows))


def table_html(headers, rows):
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % html.escape(str(c)) for c in row)
                   for row in rows)
    return "<table><tr>%s</tr>%s</table>" % (head, body)


def render(user_id, genres, comparison):
    head = "<title>User Results Viewer v0</title>\n<style>\n%s\n</style>" % CSS
    rows = [(g["genre"], ", ".join(g["tags"]), g["avg_rating"], g["n_ratings"]) for g in genres]
    body = [
        "<h1>User Results Viewer</h1>",
        "<p>userId %d</p>" % user_id,
        table_html(["Genre", "Top %d tags" % TOP_N_TAGS_PER_GENRE, "My average rating",
                    "My ratings in this genre"], rows),
        "<h2>Tags shared across genres</h2>",
        table_html(["Tag", "Genres"],
                   [(tag, ", ".join(sorted(gs))) for tag, gs in sorted(shared_tags(genres).items())]),
    ]
    if comparison is not None:
        body += [
            "<h2>My score() against the judge</h2>",
            comparison_table_html(comparison),
        ]
    body = "\n".join(body)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def render_text(user_id, genres, comparison):
    out = ["User Results Viewer", "userId %d" % user_id, ""]
    for g in genres:
        out.append("%s (avg rating %.2f, %d ratings): %s"
                    % (g["genre"], g["avg_rating"], g["n_ratings"], ", ".join(g["tags"])))
    out.append("")
    out.append("Tags shared across genres:")
    for tag, gs in sorted(shared_tags(genres).items()):
        out.append("  %s: %s" % (tag, ", ".join(sorted(gs))))
    if comparison is not None:
        out.append("")
        out.append("My score() against the judge:")
        for tag, my, judge in comparison:
            diff = "" if my is None else " (%+d)" % (my - judge)
            out.append("  %s: my score %s, judge %s%s" % (tag, "(none)" if my is None else my, judge, diff))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Genres, their top tags, and your average "
                                                  "rating per genre, for one user.")
    parser.add_argument("--user", type=int, default=ME)
    parser.add_argument("--out", default=str(REPO / "user_results.html"))
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()

    ratings, tags, movies, links = load_all()
    mine, _ = read_my_ratings()
    ratings = add_me(ratings, mine)
    genres = build(args.user, ratings, tags, movies)
    comparison = judge_comparison(args.user, ratings, tags, movies)
    if args.text:
        print(render_text(args.user, genres, comparison))
        return
    Path(args.out).write_text(render(args.user, genres, comparison), encoding="utf-8")
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
