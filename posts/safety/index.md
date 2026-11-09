---
layout: default
title: "The Defensive Touchdown Act: A Data-Driven Proposal to Revalue the Safety"
permalink: /post/safety/
---

# The Defensive Touchdown Act: A Data-Driven Proposal to Revalue the Safety

> November 9, 2026 · Filed by the Ministry of Silly Plots, Office of Scoring Reform · File 2-PT/SAF

<div style="background-color: #f4f4f0; border-left: 4px solid #e2a900; padding: 15px; margin-bottom: 25px;">
  <strong>SUMMARY</strong><br>
  The Ministry proposes that a safety be scored as a <strong>touchdown for the defense</strong>, followed by a normal kickoff, with the game clock reset if it happens in the final two minutes of a half. A defense that drives an offense backward into its own end zone has done something worth a touchdown, and should be paid like it. Using 675,997 NFL plays from 2012 to 2025, the Ministry finds that the Act (1) rewards defenses that earn safeties, four in five of which come from the pass rush or run defense, (2) corrects a scoreboard that already understates the safety, which is worth about 3.8 points rather than 2, and (3) ends the one deliberate use of the safety: a punter running backward to burn the clock. It would add about 27 points a season across the league and would have changed 20 to 30 results since 2012.
</div>

## The Proposed Amendment

**WHEREAS** a field goal is worth three points and a safety two, although a field goal requires the offense to advance and a safety requires the defense to send it backward through its own end zone;

**WHEREAS** the two points have not been revised in living memory, and no member of this Ministry can recall being consulted;

**WHEREAS** the rules currently reward a team protecting a late lead for having its punter run as far as 34 yards backward and be tackled in his own end zone;

**NOW, THEREFORE,** the Ministry proposes:

> **Section 1.** A safety shall be scored as a touchdown for the defending team, worth six points.
>
> **Section 2.** The scoring team shall be entitled to a try, as after any touchdown.
>
> **Section 3.** Following the try, the scoring team shall kick off to the team that conceded the safety, under the kickoff rules then in force. The free kick from the 20-yard line is abolished.
>
> **Section 4.** If a safety occurs in the final two minutes of either half, the game clock shall be reset to the time remaining at the snap.
>
> **Section 5.** Nothing in this amendment shall be construed as an endorsement of punters running backward.

## The Act at a Glance

| | Current rule | Under the Act |
|---|---|---|
| Points on the scoreboard | 2 | 6 + try (6.96 on average) |
| Who gets the ball next | the defense, by free kick | the offense, by kickoff |
| Net value to the defense | 3.83 | 5.54 |
| Swing for the defense, vs. before the snap | 2.9 | 4.6 |
| How much better punting is than conceding, own 1–2 | 0.83 pts | 2.54 pts |
| Largest win-probability gain from conceding on purpose | 4.9 WP pts | 0.2 WP pts (noise) |
| Extra value across the league per season | — | about 27 points |

*Net value = points scored plus or minus the value of the next possession, in expected points. WP pts = percentage points of win probability. The current-rule column uses all 185 post-safety free kicks from 2012–25; the Act column uses 2024–25 kickoffs.*

The money chart shows the Act's main effect. Each cell compares conceding a safety with punting, for a team facing 4th down at its own 1–5 in the fourth quarter. Blue means conceding wins. Under the current rule there is a blue corner in the final seconds. Under the Act there is none.

![Decision map, current rule vs proposed](/posts/safety/assets/safety_decision_map.png)

## The Case for the Act

### 1. Defenses earn safeties

Of the 220 safeties since 2012 that were not conceded on purpose:

| How it happened | Safeties |
|---|---|
| Sack | 86 |
| Ball carrier stopped in the end zone | 66 |
| Intentional grounding in the end zone | 22 |
| Offensive penalty in the end zone (mostly holding) | 22 |
| Blocked punt | 14 |
| Other | 10 |

Sacks and stopped runs alone account for about two thirds. Counting intentional grounding, which is usually a quarterback under pressure, the pass rush and run defense account for four in five.

The field position usually comes first. 77% of these safeties came on drives that started inside the offense's own 10, and 31% on the very first snap of the drive. Only 6% came on drives that began beyond the offense's own 20. The defense usually finishes the job, after a punter or kickoff coverage unit starts it. The Act pays the defense for the finish; the Ministry regards the rest as teamwork and declines to split the award.

### 2. The scoreboard already understates the safety

Every score has two parts: the points, and what happens next. After a touchdown or field goal, the scoring team kicks off. After a safety, the conceding team must free-kick from its own 20, and the *scoring* team gets the ball.

We priced the next possession after every restart since 2012, using expected points (EP) at the first snap of the following drive.

![What each score is worth once the next possession is priced in](/posts/safety/assets/safety_value.png)

| Score | On the scoreboard | Next possession | Net value |
|---|---|---|---|
| Touchdown | 6.96 | opponent receives kickoff (−1.41) | **5.54** |
| Field goal | 3 | opponent receives kickoff (−1.41) | **1.59** |
| Safety (current) | 2 | scorer receives free kick (+1.83) | **3.83** |
| Safety (under the Act) | 6.96 | opponent receives kickoff (−1.41) | **5.54** |

*Kickoff values: 2024–25 (2,476 kickoffs after touchdowns, 1,683 after field goals). Free-kick value: all 185 post-safety free kicks, 2012–25 (standard error 0.06). The 21 free kicks in 2024–25 alone give 1.93 ± 0.43.*

A safety is already worth about 2.4 field goals once each is netted against the possession that follows. In 2024–25, receiving a free kick was worth 0.51 points more than receiving a kickoff (95% interval 0.11 to 0.95). The field goal has meanwhile been getting cheaper: receivers' average start after a field goal moved from their own 22 (2012–15) to their own 25 (2016–23) to their own 30 (2024–25), and a field goal's net value fell from 2.25 to 1.59.

**What the data does and does not say.** It says the scoreboard understates the safety by about two points. It does not say a safety must equal a touchdown. That is the Act's principle, not its evidence. Under the Act the defense's net value matches any touchdown's. In swing, measured from where the defense stood before the snap, it does not: 4.6 points, against 6.7 for a pick-six, because a pick-six usually takes the ball from an offense in better shape.

### 3. It ends the backward run

We built a win-probability model from 2012–24 snaps and tested it on 2025. Across all 2025 snaps its Brier score is 0.159, against 0.171 for nflverse's model. In the final 60 seconds (936 snaps) the two are level, at 0.082.

Under the current rule, conceding a safety from your own 1–5 is worse than punting in expected points: by 0.83 points from the 1–2, 1.17 from the 3–5, and 1.42 from the 6–10. In win probability it wins only when leading by 3 to 7 points in the final 10–45 seconds, the cutoff depending on the lead.

That window is clock arithmetic. A punt from deep takes a median of 11 seconds to reach the next snap, and a safety plus free kick takes 12. The chart assumes the punter burns another 5 seconds in the end zone. The more time he burns, the more conceding pays:

| Seconds the punter burns | Leads where conceding helps, final 30 s | Largest gain |
|---|---|---|
| 0 | 5 to 7 | 1.7 WP pts |
| 5 (as charted) | 3 to 7 | 4.9 WP pts |
| 10 | 3 to 7 | 11.6 WP pts |

The league uses the play exactly this way. Since 2012 there have been 11 intentional end-of-game safeties, all by teams leading by 5 to 30 with 63 seconds or less left. Only 2 of the 11 snapped from inside their own 5. The rest retreated, from as far out as their own 34. The best known is Baltimore's in Super Bowl XLVII: up 5 with 12 seconds left, the punter ran 8 seconds off the clock before stepping out of the end zone.

Sections 1–3 of the Act make conceding cost about 7 points instead of 2. That leaves no state where it pays: the largest gain anywhere on the grid is 0.1 WP pts, which is noise. A few states remain where conceding is merely free, at leads of 9 or more in the final seconds, when a punt also wins. Section 4 removes the clock time the retreat was buying. With it, those states cost 0.01 to 3.7 WP pts, and the backward run has no purpose left.

Away from the final seconds, the left panel of the chart has a few isolated light-blue cells, such as +7 at 4:00. These are model noise of about ±3 points, not a strategy.

## What the Act Would Cost

**Points.** The Act adds 1.71 points of net value to each earned safety. At 15.7 earned safeties a season, that is about 27 points a season across all 32 teams.

**Results.** Applied to final scores alone, the Act would have reversed 20 to 30 results since 2012, depending on what the scoring team did with its try. With the usual extra point, 22 games flip and 8 more go to overtime. Among them is Buffalo at Miami in 2022, Week 3: a Miami punt deflected off an offensive player and left the end zone for a safety, and Buffalo lost 21–19. This is an upper bound, presented as color. Teams would have played these games differently, and the defense would have kicked off rather than received.

**The goal line.** Compare an offense stopped at its own 1 with one stopped in its end zone. Under current rules, that half-yard is worth 1.0 to 3.3 points to the defense, depending on the down. Under the Act it is worth 2.8 to 5.0. Spot-of-ball and forward-progress rulings at the offense's own goal line would carry near-touchdown stakes. The Ministry notes that the opposite goal line has carried such stakes since the invention of the goal line.

**Penalties.** Intentional grounding (22) and other offensive penalties (22, mostly holding) in the end zone would become 7-point calls. So would the 14 blocked punts that went out of the end zone.

## Objections Considered

**"A sack is not a pick-six."** Agreed: in swing terms it would still be worth 4.6 points against 6.7. The Ministry observes that both plays end with the defense in the end zone and the offense in disgrace.

**"Offenses would adapt."** They would. Teams pinned deep would likely punt earlier, call safer plays, and hold less near their own goal line. This analysis prices the Act against today's behavior and does not model those responses.

**"The free kick is part of the safety's charm."** The free kick is currently the mechanism by which the safety is undervalued. The Ministry is unsentimental about it.

**"Expected points are not points."** Net value credits the scorer with the possession that follows. Under a strict reading of the scoreboard that credit does not exist. This Ministry reads the whole game.

**Prior art.** Analysts have long noted that the free kick makes a safety worth more than two points. The Ministry claims no novelty for that observation, only for the paperwork.

## Methods and Data

- **Data:** nflverse play-by-play, 2012–2025 regular and postseason, 675,997 plays in 3,829 games, deduplicated on game and play ID.
- **Restart value:** nflverse expected points at the first snap after each kickoff or free kick, excluding the final two minutes of each half. nflverse's own EPA scores a safety as a flat −2 and leaves out the free kick, so we price the free kick separately.
- **Win probability:** a gradient-boosted classifier, constrained so that more points and better field position can never lower win probability. Trained on 2012–24, tested on 2025, with a separate check on the final 60 seconds.
- **Decision map:** each option's outcomes are resampled from real plays and scored with the model, assuming 2 timeouts each and an even point spread. Samples:
  - 449 punts from a team's own 1–5.
  - 207 post-safety free kicks.
  - 714 end-of-game kickoffs by teams trailing by 1–8 in the final five minutes, used for the Act. About half were onside attempts; the kicking team recovered 5.5%.
- **Code:** `posts/safety/analysis/safety_analysis.py`. Every figure in this post is in `posts/safety/analysis/results.json` or the two decision-grid CSVs beside it.

## Recommendation

The Ministry recommends that the Defensive Touchdown Act be adopted at the next available competition committee meeting or, failing that, the next available Thanksgiving dinner.

*Respectfully submitted,*
*The Office of Scoring Reform, Ministry of Silly Plots*
