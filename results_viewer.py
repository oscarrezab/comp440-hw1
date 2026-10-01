"""Results Viewer.

Builds one self-contained HTML page comparing four rankings of the tags on each of your ten
movies, and on the twenty least-rated movies the judge was asked about.  Per movie it shows
the counts, your own order, the
judge's order and your `score()` order, one after another; then the tags people applied to the
movie; then the biggest disagreements between `score()` and the judge.  Open the page in a
browser; --text prints the same content to a terminal.

The `Your score()` column ranks only the tags the judge also rated, so that every column on the
page covers the same set.  It is not your score's own top ten over all of the movie's tags.

    uv run python results_viewer.py            # writes movie_results.html
    uv run python results_viewer.py --text     # the same content as plain text

Your ten movies come from the "My ten movies" slot in `WRITEUP.md`, one movie to a line with
the movieId first.  Your own order comes from the "My own order of the ten most-used tags"
slot, where each movie is one line of the form

    296: quentin tarantino, nonlinear, hit men, dark comedy

with the tags best first.  Both slots are read as bare lines: no bullets, no numbering.  A
bulleted or numbered list reads as nothing, and the page says so.  A movie with no line in the
order slot shows as not written yet.  `agreement.py` holds the parser for the order slot and
this file imports it, so the page and the agreement number read the same lines.

This is a first draft.  It hides things you need in order to read the four rankings, and
finding out what, from the page itself, is part of the assignment.
"""

import argparse
import datetime
import html
import re
from pathlib import Path

import pandas as pd

# One parser for the "My own order" slot, shared with `agreement.py`, so the two never read
# the same lines two different ways.
from agreement import ORDER_FORMAT, my_order_lines

REPO = Path(__file__).resolve().parent

GAP = 5     # how far two ranks must differ before we call the pair a disagreement
TOP = 10    # how many tags to show in each ranked list
SHOWN = 10  # how many disagreements to show per movie

DEFINITION = ("A disagreement is a movie-tag pair whose rank under score() and its rank in the "
              "judge's list differ by at least %d. Every list is ranked best first, with ties "
              "broken alphabetically." % GAP)
CSS = """body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }
table { border-collapse: collapse; margin-bottom: 12px; }
th, td { border: 1px solid #999999; padding: 4px 8px; text-align: left; }"""


def as_date(stamp):
    """A tag application's time, as a date somebody can read."""
    return datetime.datetime.fromtimestamp(int(stamp), datetime.UTC).strftime("%Y-%m-%d")


def ranked(pairs):
    """pairs is a list of (tag, value); the best value gets rank 1, ties alphabetical."""
    order = sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
    return {tag: i + 1 for i, (tag, _) in enumerate(order)}


def my_movies(writeup_path):
    """The movieIds in the "My ten movies" slot of WRITEUP.md, one per line."""
    out = []
    if not Path(writeup_path).exists():
        return out
    inside = False
    for line in Path(writeup_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):
            inside = "My ten movies" in line
            continue
        m = inside and re.match(r"\s*(\d+)", line)
        if m:
            out.append(int(m.group(1)))
    if not out:
        print('No movieIds were found in the "My ten movies" slot of WRITEUP.md, so this page '
              "covers the movies the judge rated instead. That slot is read one movie to a "
              "line, with no bullets and no numbering: the movieId first, then the title, as "
              'in "296, Pulp Fiction (1994)".')
    return out


def my_order(writeup_path):
    """movieId -> the tags in the order you wrote, from the WRITEUP.md slot.

    `agreement.py` owns the parser; this calls it so the page and the number agree."""
    out = my_order_lines(writeup_path)
    if not out:
        print("No movie lines were found in the \"My own order\" slot of WRITEUP.md, so every "
              "movie below shows your order as not written yet.\n" + ORDER_FORMAT)
    return out


def least_rated(judged, rated):
    """The twenty least-rated movies the judge was asked about: the hardest misses."""
    counts = rated.reindex(judged).fillna(0)
    return sorted(counts.sort_values(kind="stable").head(20).index)


def build(scores_path, judge_path, data_dir, writeup_path):
    """Return one dict per movie: your ten first, then the least-rated ones."""
    data_dir = Path(data_dir)
    scores = pd.read_csv(scores_path, keep_default_na=False)
    judge = pd.read_csv(judge_path, keep_default_na=False)
    movies = pd.read_csv(data_dir / "movies.csv", keep_default_na=False)
    tags = pd.read_csv(data_dir / "tags.csv.gz", keep_default_na=False)
    # Tag text arrives free-form. Strip and lowercase once, here, so the applications table
    # speaks the same vocabulary as the ranked lists above it.
    tags = tags.assign(tag=tags["tag"].str.strip().str.lower())
    titles = dict(zip(movies["movieId"], movies["title"]))
    rated = pd.read_csv(data_dir / "ratings.csv.gz", keep_default_na=False,
                        usecols=["movieId"])["movieId"].value_counts()
    judged = sorted(judge["id"].unique())
    wanted = my_movies(writeup_path) or judged
    wanted = wanted + [m for m in least_rated(judged, rated) if m not in set(wanted)]
    mine = my_order(writeup_path)

    out = []
    for movie_id in wanted:
        judge_rows = judge[judge["id"] == movie_id]
        score_rows = scores[scores["movieId"] == movie_id]
        student_score = dict(zip(score_rows["tag"], score_rows["score"]))
        rated_tags = [(row.tag, int(row.rating)) for row in judge_rows.itertuples()
                      if row.tag in student_score]
        if not rated_tags:
            continue
        judge_rank = ranked(rated_tags)
        score_rank = ranked([(tag, student_score[tag]) for tag, _ in rated_tags])
        applied = tags[tags["movieId"] == movie_id]
        counts = applied["tag"].value_counts()
        people = applied["userId"].nunique()
        gaps = [(tag, score_rank[tag], judge_rank[tag], score_rank[tag] - judge_rank[tag])
                for tag in judge_rank
                if abs(score_rank[tag] - judge_rank[tag]) >= GAP]
        gaps.sort(key=lambda g: (-abs(g[3]), g[0]))
        out.append({
            "title": "%s — %s ratings" % (titles.get(movie_id, "movie %d" % movie_id),
                                          "{:,}".format(int(rated.get(movie_id, 0)))),
            "people": people,
            "counts": list(counts.index[:TOP]),
            "mine": mine.get(movie_id, [])[:TOP],
            "judge": sorted(judge_rank, key=lambda t: judge_rank[t])[:TOP],
            "score": sorted(score_rank, key=lambda t: score_rank[t])[:TOP],
            "gaps": gaps[:SHOWN],
            "apps": sorted(((row.tag, row.userId, as_date(row.timestamp))
                            for row in applied.itertuples()),
                           key=lambda app: (app[0], app[2])),
        })
    return out


def table_html(headers, rows):
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % html.escape(str(c)) for c in row)
                   for row in rows)
    return "<table><tr>%s</tr>%s</table>" % (head, body)


def diff_color(diff, max_abs):
    """Background color for a signed rank difference: green for positive, red for
    negative, intensity scaled by how large the difference is relative to the biggest
    one shown for this movie."""
    if max_abs == 0:
        return "transparent"
    intensity = abs(diff) / max_abs
    alpha = 0.15 + 0.65 * intensity
    rgb = "46, 160, 67" if diff > 0 else "217, 48, 37"
    return "rgba(%s, %.2f)" % (rgb, alpha)


def disagreements_table_html(gaps):
    """The biggest disagreements, score() against the judge: tag, each rank, and a
    signed Difference column (score() rank minus judge rank) whose cell is shaded
    green when positive and red when negative, darker the further from zero."""
    headers = ["Tag", "score() rank", "Judge rank", "Difference"]
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    max_abs = max((abs(g[3]) for g in gaps), default=0)
    rows = []
    for tag, score_rank, judge_rank, diff in gaps:
        cells = ["<td>%s</td>" % html.escape(tag),
                 "<td>%d</td>" % score_rank,
                 "<td>%d</td>" % judge_rank,
                 '<td style="background-color: %s">%+d</td>' % (diff_color(diff, max_abs), diff)]
        rows.append("<tr>%s</tr>" % "".join(cells))
    return "<table><tr>%s</tr>%s</table>" % (head, "".join(rows))


def rankings_table(movie):
    """The four rankings (by count, your order, the judge's order, your score()) side by
    side, one row per rank, so the same rank across methods reads as one row."""
    columns = [movie["counts"], movie["mine"], movie["judge"], movie["score"]]
    rows = []
    for rank in range(TOP):
        row = [str(rank + 1)]
        for col in columns:
            if rank < len(col):
                row.append(col[rank])
            else:
                row.append("not written yet" if rank == 0 and not col else "")
        rows.append(row)
    return rows


def render(movies):
    """Build the page."""
    head = "<title>Results Viewer v0</title>\n<style>\n%s\n</style>" % CSS
    body = ["<h1>Results Viewer</h1>", "<p>%s</p>" % html.escape(DEFINITION)]
    for movie in movies:
        body += [
            "<h2>%s</h2>" % html.escape(movie["title"]),
            table_html(["Rank", "By count", "Your order", "The judge's order", "Your score()"],
                       rankings_table(movie)),
            "<p>%d applications by %d people.</p>" % (len(movie["apps"]), movie["people"]),
            "<h3>Biggest disagreements, score() against the judge</h3>",
            disagreements_table_html(movie["gaps"]),
        ]
    body = "\n".join(body)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def table_text(headers, rows):
    if not rows:
        return "    (none)"
    grid = [list(headers)] + [[str(c) for c in row] for row in rows]
    width = [max(len(line[i]) for line in grid) for i in range(len(headers))]
    lines = []
    for i, row in enumerate(grid):
        lines.append("    " + "  ".join(c.ljust(width[j]) for j, c in enumerate(row)).rstrip())
        if i == 0:
            lines.append("    " + "  ".join("-" * w for w in width))
    return "\n".join(lines)


def render_text(movies):
    out = ["Results Viewer", DEFINITION, ""]
    for movie in movies:
        out += [movie["title"],
                table_text(["Rank", "By count", "Your order", "The judge's order",
                            "Your score()"], rankings_table(movie)),
                "  %d applications by %d people." % (len(movie["apps"]), movie["people"]),
                "  Biggest disagreements, score() against the judge",
                table_text(["Tag", "score() rank", "Judge rank", "Difference"],
                           [(tag, sr, jr, "%+d" % diff)
                            for tag, sr, jr, diff in movie["gaps"]]), ""]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Compare four rankings of your movies' tags.")
    parser.add_argument("--scores", default=str(REPO / "scores.csv"))
    parser.add_argument("--judge", default=str(REPO / "judge" / "ratings_movies.csv"))
    parser.add_argument("--data", default=str(REPO / "data"))
    parser.add_argument("--writeup", default=str(REPO / "WRITEUP.md"))
    parser.add_argument("--out", default=str(REPO / "movie_results.html"))
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()

    for path in (args.scores, args.judge):
        if not Path(path).exists():
            raise SystemExit("%s is missing. Part 2 writes scores.csv; the judge writes "
                             "judge/ratings_movies.csv." % Path(path).name)

    movies = build(args.scores, args.judge, args.data, args.writeup)
    if args.text:
        print(render_text(movies))
        return
    Path(args.out).write_text(render(movies), encoding="utf-8")
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
