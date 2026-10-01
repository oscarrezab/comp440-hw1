"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from load_data import load_all

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

TOP_N_TAGS_PER_GENRE = 10


def _genre_top_tags(tags: pd.DataFrame, movies: pd.DataFrame) -> pd.DataFrame:
    """The TOP_N_TAGS_PER_GENRE most-applied tags for each genre, across every movie that
    carries it. Returns columns genre, tag, genre_tag_count."""
    exploded = movies.assign(genre=movies["genres"].str.split("|")).explode("genre")
    exploded = exploded[exploded["genre"] != "(no genres listed)"]
    joined = tags.merge(exploded[["movieId", "genre"]], on="movieId")
    counts = joined.groupby(["genre", "tag"]).size().rename("genre_tag_count").reset_index()
    return (counts.sort_values("genre_tag_count", ascending=False)
                  .groupby("genre").head(TOP_N_TAGS_PER_GENRE))


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """What tags best describe a user. This one is yours; the handout's Part 3, step 2.

    Per the student's definition: a user's high movies are the top quartile of their own
    ratings, their low movies the bottom quartile (each user's own distribution, via
    pandas `.quantile`; a rating exactly on the boundary counts as qualifying). For every
    genre among a user's high/low movies, the genre's TOP_N_TAGS_PER_GENRE most-applied
    tags (by overall application count, across every movie with that genre) become
    candidates. A candidate tag's raw score is the number of the user's high/low movies
    whose genre contributed it, summed over every qualifying genre it came from. That raw
    score is then min/max-scaled, per user, onto 1-5 and rounded to the nearest integer, so
    it sits on the judge's own 1-5 scale (a user whose raw scores are all equal, including
    one with only one candidate tag, has no basis to rank within itself and gets 3, the
    middle, across the board). Ties are broken by how many times anyone, anywhere, has
    applied that tag (global tag popularity)."""
    exploded = movies.assign(genre=movies["genres"].str.split("|")).explode("genre")
    exploded = exploded[exploded["genre"] != "(no genres listed)"][["movieId", "genre"]]

    q = ratings.groupby("userId")["rating"].quantile([0.25, 0.75]).unstack()
    q.columns = ["low_cut", "high_cut"]
    r = ratings.merge(q, on="userId")
    extreme = r[(r["rating"] >= r["high_cut"]) | (r["rating"] <= r["low_cut"])]
    extreme = extreme.merge(exploded, on="movieId")

    user_genre_counts = (extreme.groupby(["userId", "genre"])["movieId"]
                                 .nunique().rename("n_movies").reset_index())

    genre_tags = _genre_top_tags(tags, movies)
    pairs = user_genre_counts.merge(genre_tags, on="genre")

    tag_popularity = tags.groupby("tag").size().rename("tag_popularity")
    pairs = pairs.merge(tag_popularity, on="tag")

    result = (pairs.groupby(["userId", "tag"])
                    .agg(raw_score=("n_movies", "sum"), tag_popularity=("tag_popularity", "max"))
                    .reset_index())

    group_min = result.groupby("userId")["raw_score"].transform("min")
    group_max = result.groupby("userId")["raw_score"].transform("max")
    span = group_max - group_min
    scaled = (1 + 4 * (result["raw_score"] - group_min) / span).where(span != 0, 3.0)
    result["score"] = scaled.round().astype(int)
    result = result.sort_values(["userId", "score", "tag_popularity"], ascending=[True, False, False])

    me = result[result["userId"] == ME].sort_values(
        ["score", "tag_popularity"], ascending=[False, False])
    print(f"{len(result):,} user-tag row(s), {result['userId'].nunique():,} distinct user(s).")
    print("My top ten tags:")
    for _, row in me.head(10).iterrows():
        print(f"  {row.tag} (score {row.score}, raw {row.raw_score}, "
              f"tag popularity {row.tag_popularity})")

    return result[["userId", "tag", "score"]]


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    score(ratings, tags, movies)


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
