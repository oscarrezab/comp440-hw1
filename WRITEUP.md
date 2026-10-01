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

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** Start by removing those ratings that have no tags associated. If there are still more than 5 million, remove the movies with the least amount of ratings. This is so that we can map a rating to the tags given and so we discard movies that might skew our understanding of ratings-tags relationships.

**One rule I considered and rejected, and why:** I considered removing them at random, but then this would still retain rows or data points that are not of much useful information for analysis.

**One interesting thing from `data/README.md`:** Keeping only "eligible" users is a very interesting part of the rule which I agree with, it removes users with too few ratings that would make the final table rather sparse.

**How the script's rule differs from mine, and what each keeps that the other drops:** My rule does not consider user-to-rating-count relationships, so there is no guarantee that the users kept have a decent amount ratings made. The script's rule is also more explicit on how related movies, tags, and users are linked. Another big difference is how we chose to reach the 5M ratings count, while I opted to continuously check if we had reduced the dataset size to 5M, whereas the script's rule first reduces the set to less than 5M and then adds back with the random sample as needed.

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** (a)'s share of all 32,000,204 MovieLens ratings: 0.1562, from 5,000,030 pandas rows. The different route: counting rows directly in the raw `ratings.csv.gz` file (not through pandas), which gave 5,000,030 rows and the same 0.1562 share. MATCH.

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** (b)'s rating count of the least-rated kept movie, from `ratings.groupby("movieId").size().min()`: 83. The different route: `np.bincount` over the movieId values, which also gave 83. MATCH.

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** The Silence of the Lambs (1991), movieId 593. I picked it because I think it has many interesting ways of describing it, so I'm curious about analyzing its tags.

**Its most misleading tag in the count-ordered list, and why it misleads:** I think psychology as a tag is rather misleading. Sure, there is a big deal of psychologic analysis we can do on the movie and its characters, but I would not tag it as a mostly psychology-related movie or one that is purely centered on that subject.

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** I learned that there's an additional characteristic of the tags related to how much I liked that in the movie; for example, how much I liked the fact that it is a disturbing film. That's interesting to know because tags appear as suggestions based on the number of times they have been given to the movie, which I believe creates a positive feedback loop where the most given tags might be assigned more and more since they appear first to users. I'm also curious about the effect of showing the users' sentiment towards those tags, perhaps it influences what people think about them, even after having watched the movie.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** I expect the tag count to be much larger in the early 2000s, when people were getting used to the internet and the website was rather "new". I expect very few ratings to have come up in the last five years when compared to those early years. Perhaps an increase between 2019 and 2021 due to COVID-19 lockdowns.
**The figure, what it shows:** I see that there were no tags before around 2006, perhaps because the feature was not implemented. There's an important peak in number of tags applied in 2021, which could indeed have to do with COVID lockdowns. About ratings, the most-rated moments seem to be 1996 (about when the website was created) and 2016, not exactly sure why. We can also note that the number of ratings does not usually match the number of tags applied.

**Two interesting details I learned up close that the counts did not show:** It's very likely that the spikes in number of tags applied can be explained by the fact that few users (maybe even just one) applied a lot of tags in one session. So it's very difficult to explain the relationship between number of ratings and number of tags based on the shown figure. From the taggers' mean rating vs everyone else's table I can somewhat see the sentiment displayed on the website about the tags; for example, cannibalism is displayed in the website in red, meaning it's something people didn't like about the movie, and we can see that in the fact that the tagger's mean is lower (4.03) than the everyone else's mean (4.08).

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** While not quite a contradiction, I did expect the ratings/tags counts to be much greater in the period of 2019 to 2021, but it is not that noticeable, perhaps due to the scale.

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** After grouping similar tags (e.g, psychological, psychology, plurals/singulars, and typos), use the mean rating associated to those tags and see how close or far it is to the a perfect rating (5.0) or the worst rating (0.5). That is, tags associated with a mean rating of 2.75 would earn a score of 0, because they suggest no relationship between the tag and the perceived quality of the movie; whereas a tag associated to a mean rating of 0.5 or 5.0 will get a score of 10. Any values in between should map a linear relationship.

**One definition I considered and rejected, and why:** I considered just picking those tags that map to ratings very close to 5.0, but then that would exclude tags that are strongly associated with negative ratings, which would still be a strong indication of movie quality.

**Which tags I merged as the same tag, which I kept apart, and why:** Fold case, remove whitespace, remove special characters, restrict the merge to tags that co-occur in the same movie, don't merge words that are less than 4 characters long, don't merge tags that are numbers only, collapse obvious typos, and collapse singular/plural variants.

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

Because it seeks to rate higher those tags related to very high or very low ratings, that is in my opinion what suggests that a given tag influenced a rating. This approach, however, does not account for the possibility that negative ratings tend to be very negative, so tags that are related to 0.5 ratings (the lowest in the dataset) will always be ranked higher than those of, for example, a 4.5 rating.

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

593, Silence of the Lambs, The (1991)
2571, Matrix, The (1999)
2959, Fight Club (1999)
2858, American Beauty (1999)
858, Godfather, The (1972)
4226, Memento (2000)
4995, Beautiful Mind, A (2001)
59315, Iron Man (2008)
1721, Titanic (1997)
5349, Spider-Man (2002)

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

593: disturbing, suspense, psychological, serial killer, cannibalism, psychology, Anthony Hopkins, Jodie Foster, great acting, excellent script
2571: sci-fi, artificial intelligence, dystopia, cyberpunk, post-apocalyptic, virtual reality, philosophy, thought-provoking, alternate reality, philosophical
2959: Brad Pitt, Edward Norton, mindfuck, surreal, social commentary, twist ending, dark comedy, philosophy, psychology, thought-provoking
2858: sexuality, dark comedy, surrealism, social commentary, black comedy, great acting, midlife crisis, excellent script, powerful ending, thought-provoking
858: crime, mafia, Mafia, Al Pacino, masterpiece, classic, organized crime, great acting, Marlon Brando, atmospheric
4226: nonlinear, dark, complicated, Mindfuck, mystery, psychological, twist ending, stylized, psychology, memory
4995: mental illness, schizophrenia, true story, math, inspirational, twist ending, genius, psychology, intelligent, mathematics
59315: superhero, action, Marvel, sci-fi, funny, Robert Downey Jr., Iron Man, comic book, technology, Gwyneth Paltrow
1721: romance, love story, Leonardo DiCaprio, drama, disaster, true story, historical, bittersweet, atmospheric, Kate Winslet
5349: superheroes, super-hero, superhero, marvel, Marvel, Tobey Maguire, Willem Dafoe, Kirsten Dunst, New York City, comic book

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** I considered simply picking those that relate to high ratings, but that would neglect the fact that very negative ratings might still be related to some tags.

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** `score()`: 1.61 of 5, over 109 movies, 9 tags compared on the middle one. Popularity: 1.71 of 5, over 110 movies, 12 tags compared on the middle one. Your own order: 1.20 of 5, over 10 movies, 8 tags compared on the middle one. Popularity came closest.

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

The judge skill takes in the student-written criterion `criterion.md`/`criterion_users.md`, guidelines on how the prompt will be written and how to answer (`system.md`), the `judge.py` which is the ranking script, the list of movies to work off of, a description of how the vocabulary of tags is built. It also produces an id-movie-tag csv and a log file. The README describes this file structure, as well as instructions on how to run it, what the expected output is, and the purpose of the output.

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

It will go through every movie in `movies.csv` and my ten movies in the writeup and computes a rating based on the criterion. The output is put into a csv and printed as a log. There are multiple checks to verify that path structures are correct, that movies are listed in the writeup, and that every judgement is made without repo recollection or additional tools.

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

The skill allows for a way to reproduce a method in a way that in can be just grabbed and ready to use, with minimal configuration needed and, when it is needed, the CLI tool should be able to get it or ask the user for it. I may use it for times I want to verify my work and need a rubric-like structure to ensure the same steps are followed for different approaches.

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** It is useful to compare the tags order by count, the order I gave, the judge's order, and the order given by `score()`. What I believe should be removed is the "Tags on this movie" section, as it does not provide very useful information for analysis. Another thing I'd do to make it better is put the comparisons in a table format, such that I can compare the orders side-by-side.

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** The first draft wouldn't let me see different movies easily, since the now-removed table was too long and made the report hard to navigate. I had Claude remove the table altogether, as I didn't find value in it. The changed page now shows a report that is easier to navigate.

**Improvement 2:** The draft would not let me see the difference in rankings and the biggest disagreements for the same movie in the same view (without needing to scroll); it was also a little bit hard to visualize the rankings between methods. I had Claude change the rankings view to be a table that groups the rankings methods that are relevant to a given movie together. The changed page now shows the better visualization.

**Improvement 3:** The previous iteration didn't explicitly show the value for the ranking difference. I had Claude add the missing column and color-code the differences to show positive and negative differences more clearly; I also had it sort the rows by the absolute value of those differences.

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** The Matrix, "bad science", score() rank 59, judge rank 2. I think the gap is there because the judge looked at the term "bad" and implied it was related to a very negative rating, therefore it ranked it very high on position 2, whereas `score()` computed the numeric relationship between that tag and existing ratings.

**Disagreement 2:** Fight Club, "quirky", score() rank 18, judge rank 69. Quirky is a term that can be interpreted either as positive or negative, that's why I think the judge placed it on a very low rank, since there is no evident correlation between the word and an extreme rating. On the other hand, `score()` does have access to those data correlations, so it identified that quirky was somewhat related to extreme ratings, even though it was not put within the top 10.

**Disagreement 3:** Spider-Man, "classic", score() rank 1, judge rank 6. This one has the minimum disagreement of 5. I'd guess that it has to do with the fact that the term "classic" is easily relatable to a positive rating, so this is something the judge inferred and `score()` found.

**One other high-level pattern in the results, and what you think is behind it:** There's a fairly even spread of positive/negative rank differences between the judge and `score()`. I'd assume this shows that it is generally hard for the LLM to infer the relationship between tag and movie rating, so if it's closely or loosely related is almost like flipping a coin.

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** I was very wrong on the tagging rate, it does seem like a solid percentage of the raters tag the movies; I'd say this just proves that my use of a movie rating system is not exactly the same as used by many other users. I don't think I've seen enough data to make me think it is not possible.

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

78105, Prince of Persia: The Sands of Time (2010), 3.5
110102, Captain America: The Winter Soldier (2014), 4
122892, Avengers: Age of Ultron (2015), 4.5
102125, Iron Man 3 (2013), 2.5
95167, Brave (2012), 3
593, Silence of the Lambs, The (1991), 5
91529, Dark Knight Rises, The (2012), 4.5
84152, Limitless (2011), 5
2953, Home Alone 2: Lost in New York (1992), 3.5
1721, Titanic (1997), 4
2571, Matrix, The (1999), 4.5
7254, Butterfly Effect, The (2004), 5
4262, Scarface (1983), 4.5
103042, Man of Steel (2013), 3
6539, Pirates of the Caribbean: The Curse of the Black Pearl (2003), 2.5
89745, Avengers, The (2012), 3.5
53464, Fantastic Four: Rise of the Silver Surfer (2007), 4
8950, Machinist, The (2004), 5
109487, Interstellar (2014), 3.5
68954, Up (2009), 3

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

The best tags for a user include those that are relevant to the genres of the films they have rated either very high or very low (within the top/bottom quartiles). There's no need for a user to have used that tagged for a movie they rated, it is sufficient for them to have rated a movie very positively or very negative. For example, had I ranked a "sci-fi" movie very highly, the most used tags for overall sci-fi films (let's say the top 10) should be considered for the ranking even if I never gave that tag myself. From those considered tags, the ranking will occur depending on a how many movies of that given genre I have rated high/low; the more I have rated of that genre, the highest it should rank. If there are ties, they're then sorted by how many times other users have given that tag to the movie. I thought about using that because that's how I thought about my usage of rating platforms; if I give a very high or very low rating while including a tag, I'd think that tag would have to do a lot with the rating, and the genre of the film would be important too.

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

They generally describe my taste because it's mostly science fiction and dystopian films that I enjoy watching and thinking about rating, regardless of whether I liked them or not. The fact that my guess and the computation are very similar confirms this to me.

**What my user viewer shows and why I chose that (about 100 words):**

My user viewer shows two tables: one that displays, for each genre, the top 10 tags, my average rating, and my ratings count and another one that maps tags with the genres they're each shared across. I wanted this because it sumarizes my ratings and some relevant information about the movie genres and their tags. I think seing shared tags across genres is also helpful to give an idea of why I might like a specific combination of genres.

**What I put in the description column for a person, and why (about 150 words):**

I chose to describe a person based on their most highly-rated genres because, as one watches more and more movies, one tends to watch more of the same genres and that is descriptive of our viewing habits.

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

It asks the judge to weigh favorite genres instead of rating extremes. I also put a big emphasis on the most reviewed genres because I believe someone's thought on a movie are based on what genre of movies they watch the most.

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

Other users were included if they had given a tag that is within the top 10 most used for one of their own genres at least 300 times, which left 125 users plus myself, for 126 people total. For each person, the tags judged are every vocabulary tag that appears in the top 10 most used tags for each of their top 3 highest-rated genres. I chose 300 because that felt like it included a manageable amount of users that also had a great variety of tags given.

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

My `score()` ratings used to be on an arbitrary scale given that they were based on counts, making them hard to compare against the judge ratings. I had Claude normalize these values and now these appear on the visualizer for a side-by-side comparison.

**Improvement 2: the same (about 150 words):**

The previous version didn't explicitly show the difference in rating. Just as with the movies part, I had Claude add a difference column that is color-coded to better visualize differences in judge and `score()` ratings. Adding this allows for quicker and straightforward analysis.

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** When generating the viewer for user results, Claude was confident that the html was generated. This was not the case, since it had ran the script in the text-only mode, without creating an output file. This brings up a common thought that it's always important to triple-check important output, this is an easy case when one can just continue to sak about the file, but what if I'm about to present something and the file is not there? Just making sure at the end can be helpful.

**One call where you overrode Claude, and why:** I don't think I ever found the need to override Claude, since any changes I needed to make could have been done through the CLI.

**What you would hand to Claude sooner next time:** Throughout working on this homework I found myself going through different markdown files in various directories. This might be intuitive for Claude to look for instructions, but not that useful for a human reader, especially when I did not write those files. I'd like to give him context on this issues I'm finding earlier on so we can work on better understanding the structures of different projects or even restructuring some areas. A concern that I continue to have is the idea of giving an agent access to entire projects, perhaps we can talk more about this in class.

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** Claude did not mention the misleading tag before I did.

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** No, because the instructions mark this as my call to make. The only information given is about the axes but nothing about the trends one can see or any patterns that suggest changes in usage or relationships between tags and ratings, or their interactions over time.

**Hours spent:** About 6 hours.

**Anyone who helped you, or "no one":** No one helped me.
