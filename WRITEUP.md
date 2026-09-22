# HW1 writeup

**Name:** Oscar Reza Bautista
**Date:** 2026-09-22

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** "Rear Window" is a movie I know well, I'd say it's most-used tags would be "classic", "engaging", and "intriguing".

**(1) Why you think so:** "classic" given that it is a very famous film, "engaging" thanks to its great soundtrack that immerses viewers into the diegesis, and "intriguing" because one rarely knows what's happening in different places at a given time.

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** I'd say 10 out of 100

**(2) Why you think so:** It is nothing I've ever done before, so I'm basing it off of my own usage of movie platforms.

**(3) Can one person's tags take over a movie's tag list? Yes or no:** Yes

**(3) Why you think so:** Because, if there were to be no pre-existing tags for the given movie, those added by the user would be the only ones.

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** XXXX

**One rule I considered and rejected, and why:** XXXX

**One interesting thing from `data/README.md`:** XXXX

**How the script's rule differs from mine, and what each keeps that the other drops:** XXXX

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** XXXX

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** XXXX

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** XXXX

**Its most misleading tag in the count-ordered list, and why it misleads:** XXXX

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** XXXX

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** XXXX
**The figure, what it shows:** XXXX

**Two interesting details I learned up close that the counts did not show:** XXXX

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** XXXX

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** XXXX

**One definition I considered and rejected, and why:** XXXX

**Which tags I merged as the same tag, which I kept apart, and why:** XXXX

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

XXXX

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

XXXX

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

XXXX

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** XXXX

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** XXXX

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

XXXX

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

XXXX

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

XXXX

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** XXXX

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** XXXX

**Improvement 2:** XXXX

**Improvement 3:** XXXX

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** XXXX

**Disagreement 2:** XXXX

**Disagreement 3:** XXXX

**One other high-level pattern in the results, and what you think is behind it:** XXXX

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** XXXX

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

XXXX

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

XXXX

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

XXXX

**What my user viewer shows and why I chose that (about 100 words):**

XXXX

**What I put in the description column for a person, and why (about 150 words):**

XXXX

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

XXXX

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

XXXX

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

XXXX

**Improvement 2: the same (about 150 words):**

XXXX

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** XXXX

**One call where you overrode Claude, and why:** XXXX

**What you would hand to Claude sooner next time:** XXXX

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** XXXX

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** XXXX

**Hours spent:** XXXX

**Anyone who helped you, or "no one":** XXXX
