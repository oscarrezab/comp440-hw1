"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import gzip

import numpy as np
import pandas as pd

from load_data import DATA, load_all


FULL_ML32M_RATINGS = 32_000_204


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    n_users = ratings["userId"].nunique()
    n_movies = ratings["movieId"].nunique()
    share = len(ratings) / FULL_ML32M_RATINGS
    print(f"ratings.csv: {len(ratings):,} rows")
    print(f"tags.csv: {len(tags):,} rows")
    print(f"movies.csv: {len(movies):,} rows")
    print(f"links.csv: {len(links):,} rows")
    print(f"distinct users: {n_users:,}")
    print(f"distinct movies: {n_movies:,}")
    print(f"share of all {FULL_ML32M_RATINGS:,} MovieLens ratings: {share:.4f}")

    print()
    print("== (b) spread ==")
    ratings_per_user = ratings.groupby("userId").size()
    ratings_per_movie = ratings.groupby("movieId").size()
    tags_per_user = tags.groupby("userId").size()
    tags_per_movie = tags.groupby("movieId").size()
    for label, s in (("ratings per user", ratings_per_user),
                     ("ratings per movie", ratings_per_movie),
                     ("tag applications per user", tags_per_user),
                     ("tag applications per movie", tags_per_movie)):
        print(f"{label}: median {s.median():.1f}, min {s.min()}, max {s.max()}")
    raters = pd.Index(ratings["userId"].unique())
    taggers = pd.Index(tags["userId"].unique())
    raters_who_tagged = raters.isin(taggers).sum()
    print(f"raters who ever applied a tag: {raters_who_tagged:,} "
          f"({raters_who_tagged / len(raters):.4f} of {len(raters):,} raters)")

    print()
    print("== (c) top tags, two ways ==")
    by_count = tags.groupby("tag").size().rename("applications")
    by_users = tags.groupby("tag")["userId"].nunique().rename("distinct_users")
    both = pd.concat([by_count, by_users], axis=1)
    print("-- by number of applications --")
    top_by_count = both.sort_values("applications", ascending=False).head(20)
    for tag, row in top_by_count.iterrows():
        print(f"{tag!r}: {row['applications']:,} applications, "
              f"{row['distinct_users']:,} distinct users")
    print("-- by number of distinct users --")
    top_by_users = both.sort_values("distinct_users", ascending=False).head(20)
    for tag, row in top_by_users.iterrows():
        print(f"{tag!r}: {row['applications']:,} applications, "
              f"{row['distinct_users']:,} distinct users")

    print()
    print("== (d) two checks ==")
    with gzip.open(DATA / "ratings.csv.gz", "rt") as fh:
        raw_rows = sum(1 for _ in fh) - 1  # minus header row
    share_a = len(ratings) / FULL_ML32M_RATINGS
    share_raw = raw_rows / FULL_ML32M_RATINGS
    verdict1 = "MATCH" if raw_rows == len(ratings) else "DIFFER"
    print(f"check 1, share of {FULL_ML32M_RATINGS:,} ratings: "
          f"(a) {share_a:.4f} from {len(ratings):,} pandas rows vs. "
          f"{share_raw:.4f} from {raw_rows:,} rows counted directly in the gzip file "
          f"-> {verdict1}")

    movie_ids = ratings["movieId"].to_numpy()
    bincounts = np.bincount(movie_ids)
    floor_bincount = int(bincounts[bincounts > 0].min())
    floor_b = int(ratings_per_movie.min())
    verdict2 = "MATCH" if floor_b == floor_bincount else "DIFFER"
    print(f"check 2, least-rated kept movie's rating count: "
          f"(b) groupby gives {floor_b} vs. np.bincount gives {floor_bincount} "
          f"-> {verdict2}")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
