# Reddit Posts

## r/dataisbeautiful (Image Post)

**Title:** Is it really tough to beat a team twice? Win rate of the prior-meeting winner in 1,299 same-season NFL rematches [OC]

**Image to upload:** `../assets/rematch_win_rates.png`

**First top-level comment (required, post immediately):**

> **Data sources:**
> - Game results and play-by-play, 1999-2025: nflverse ([schedules](https://github.com/nflverse/nflverse-data/releases/tag/schedules), [play-by-play](https://github.com/nflverse/nflverse-data/releases/tag/pbp))
> - Game results, 1970-1998 (for three-game sweep attempts): [FiveThirtyEight NFL Elo game data](https://github.com/fivethirtyeight/nfl-elo-game)
>
> **Tools:** Python (pandas, statsmodels, matplotlib)
>
> **Method:** Every same-season rematch since 2002 (divisional Game 2s and playoff rematches), plus every three-game sweep attempt since 1970. For each, did the team that won the first meeting win again? Bars are 95% Wilson intervals. "Fluke" winners won Game 1 despite losing the EPA battle, with a turnover margin of +2 or better. "Blowout" winners won by 17+.
>
> A logistic model controlling for team quality (EPA per play, excluding games against that opponent) and home field finds no rematch penalty. If anything, the prior winner does slightly better than expected (+2.8 points, 95% CI -0.2 to +5.8).
>
> Write-up, paper and code: https://sillyplots.com/post/rematch

---

## r/Seahawks (Self Post, today before kickoff)

**Title:** Today the broadcast will tell you it's tough to beat a team twice. We checked 1,299 NFL rematches.

**Body:**

Seattle beat Arizona 31-7 in Week 2. Somewhere around the second quarter today, someone in the booth will note that it's tough to beat a team twice.

We looked at every same-season NFL rematch since 2002, plus every three-game sweep attempt since 1970:

- The team that won the first meeting won the rematch **57.9%** of the time.
- Teams that won the first game by 17+ won **64.9%**. Teams hosting the rematch won **64.5%**. Seattle is both.
- After controlling for team quality and home field, there is no rematch penalty at all.

Our model gives Seattle a **63%** chance today, which is more modest than Vegas (about 78% at -8.5). Neither is "almost impossible."

[chart]

Full write-up: https://sillyplots.com/post/rematch

---

## r/nfl (Self Post, after today's result)

**Title:** "It's tough to beat a team twice" — we tested it on 1,299 NFL rematches. The team that won the first meeting wins 57.9% of the time.

**Body:**

Every January, a broadcaster says it's almost impossible to beat a team three times in one season. We tested it.

**Data:** every divisional Game 2 and playoff rematch from 2002-2025, plus every three-game sweep attempt since 1970 (nflverse and FiveThirtyEight data).

**Findings:**
- The prior-meeting winner won **752-547 (57.9%)**.
- Three-game sweep attempts: **16-9 (64.0%)**. Small sample, but the best record of the lot.
- Controlling for team quality (EPA per play, excluding games against that opponent) and home field, there is **no rematch penalty**. The estimate is slightly positive.
- Where the myth comes from: home field and regression to the mean. Prior winners playing the rematch on the road win only 51.8%. Teams that won Game 1 on a turnover fluke win only 45.2%, exactly what their quality predicts.
- Rematches aren't closer, either. Margins are 0.6 points wider (not significant).

**Field test:** Seattle beat Arizona 31-7 in Week 2. The model gave Seattle 63% in Sunday's rematch. Seattle won 17-3.

[chart]

Write-up, paper (PDF) and code: https://sillyplots.com/post/rematch

---

## r/NFLstatheads / r/sportsanalytics (Self Post, later in the week)

**Title:** Testing "it's tough to beat a team twice" with leave-one-opponent-out EPA (1,299 rematches)

**Body:**

Quick summary of a project testing the broadcast cliché:

- **Sample:** divisional Game 2s and non-divisional playoff rematches 2002-2025, plus three-game sweep attempts 1970-2025. 1,299 games.
- **Quality control:** net EPA per play computed excluding all games against the rematch opponent, so the games being explained don't also explain themselves.
- **Model:** one row per rematch from the prior winner's side: logit(win) = γ + β·ΔEPA + δ·home. γ is the rematch effect.
- **Result:** γ = +0.12 (SE 0.06, p = 0.07), i.e. +2.8 points of win probability. No penalty. My read is that LOOO-EPA throws away the head-to-head games, so the prior result still carries some matchup information. Happy to hear other explanations.
- **Fluke winners** (lost the EPA battle, +2 turnover margin): 45.2%, n = 31. Fluke and blowout indicators both wash out once you control for ΔEPA (p = 0.80 and 0.34).
- **Familiarity:** divisional Game 2 margins are 0.6 points wider than Game 1 (clustered SE, p = 0.10).

Code and data are public; critique welcome: https://github.com/sillyplots/mosp/tree/main/posts/rematch

Write-up: https://sillyplots.com/post/rematch

---

## r/AZCardinals (only if Arizona wins) — NOT NEEDED: Seattle won 17-3

**Title:** Our model gave Arizona a 37% chance today. We'd like to formally attribute the win to that, and not to the difficulty of beating a team twice.

**Body:** Short version of the r/nfl post, leading with the 37%.
