---
layout: default
title: "The Defensive Touchdown Act: A Data-Driven Proposal to Revalue the Safety"
permalink: /post/safety/
---

# The Defensive Touchdown Act: A Data-Driven Proposal to Revalue the Safety

> November 8, 2026 · Filed by the Ministry of Silly Plots, Office of Scoring Reform · File 2-PT/SAF

<div style="background-color: #f4f4f0; border-left: 4px solid #e2a900; padding: 15px; margin-bottom: 25px;">
  <strong>SUMMARY</strong><br>
  The safety is the only score in which a defense drives an offense backward into its own end zone. It pays two points, the smallest score available from open play. Using 675,997 NFL plays from 2012 to 2025, the Ministry finds that (1) the safety is already worth about 3.8 points once the free kick that follows is priced in, (2) four in five safeties come from the pass rush or run defense, usually finishing off an offense pinned inside its own 10, and (3) the only deliberate use of the safety is to run out the clock. On the principle that a defense which finishes an offense in its own end zone deserves a touchdown's reward, the Ministry proposes that a safety be scored as a <strong>defensive touchdown</strong>, followed by a normal kickoff and, in the final two minutes, a clock reset. The data cannot tell you whether that principle is right. It can tell you what the rule would cost and change, and that is what follows.
</div>

**WHEREAS** a field goal is worth three points and a safety two, although a field goal requires the offense to advance and a safety requires the defense to send it backward through its own end zone;

**WHEREAS** the two points have not been revised in living memory, and no member of this Ministry can recall being consulted;

**WHEREAS** the rules currently reward a team protecting a late lead for having its punter run as far as 34 yards backward and be tackled in his own end zone;

**NOW, THEREFORE,** the Ministry submits the following findings and proposed amendment.

## Finding 1: The scoreboard understates the safety

Every score has two parts: the points, and what happens next. After a touchdown or field goal, the scoring team kicks off and the other team gets the ball. After a safety, the conceding team must free-kick from its own 20, and the *scoring* team gets the ball.

We priced the next possession after every restart since 2012, using expected points (EP) at the first snap of the following drive.

![What each score is worth once the next possession is priced in](/posts/safety/assets/safety_value.png)

| Score | On the scoreboard | Next possession | Net value |
|---|---|---|---|
| Touchdown | 6.96 | opponent receives kickoff (−1.41) | **5.54** |
| Field goal | 3 | opponent receives kickoff (−1.41) | **1.59** |
| Safety (current) | 2 | scorer receives free kick (+1.83) | **3.83** |
| Safety (proposed) | 6.96 | opponent receives kickoff (−1.41) | **5.54** |

*Kickoff values are from 2024–25 (2,476 kickoffs after touchdowns and 1,683 after field goals). Touchdown face value is 6 plus the average try, 2012–25. Free-kick value pools all 185 post-safety free kicks from 2012–25 (standard error 0.06), because there are too few to split by era. The 2024–25 free kicks alone give 1.93 ± 0.43 (21 kicks).*

At 3.83, a safety is worth about 2.4 field goals once each is netted against the possession that follows. The free possession is a real advantage even on the smallest sample. In 2024–25, receiving a free kick was worth 0.51 points more than receiving a kickoff, with a 95% interval of 0.11 to 0.95.

**This is the limit of what the data says.** It says the scoreboard understates the safety by about two points. It does not say a safety should equal a touchdown. That step is the Minister's position: a defense that finishes an offense in its own end zone has done something worth a touchdown, and should be paid like it. Under the Act, the defense's net value rises from 3.83 to 5.54. That matches any touchdown in net value, though not in swing. Measured against where the defense stood before the snap, a safety today gains it 2.9 points, a safety under the Act 4.6, and a pick-six 6.7.

The field goal, meanwhile, has been getting cheaper. Receivers' average starting spot after a field goal has moved from their own 22 (2012–15) to their own 25 (2016–23) to their own 30 (2024–25). The net value of a field goal fell from 2.25 to 1.90 to 1.59. The safety's net value has stayed flat within noise (3.75, 3.86, 3.93 by era).

## Finding 2: Safeties are earned

The Minister's position is that a defense which pushes an offense into its own end zone should be rewarded for doing so. The Ministry checked whether safeties are in fact earned or merely happen.

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

The field position usually comes first, however. **77% of these safeties came on drives that started inside the offense's own 10**, and 31% came on the very first snap of the drive. Only 6% came on drives that began beyond the offense's own 20. The defense usually finishes the job. A punter or kickoff coverage unit usually starts it. The Ministry regards this as teamwork and declines to split the award.

## Finding 3: The only deliberate safety is a clock play

We built a win-probability model from 2012–24 snaps and tested it on 2025. Across all 2025 snaps its Brier score is 0.159, against 0.171 for nflverse's model. In the final 60 seconds (936 snaps) the two are level, at 0.082. We then asked: when a team faces 4th down at its own 1–5 in the fourth quarter, when is conceding a safety better than punting?

In expected points, never. Punting from the 1 or 2 is worth 0.83 points more than conceding. From the 3–5 it is worth 1.17 more, and from the 6–10, 1.42 more. In win probability, conceding wins clearly only when leading by 3 to 7 points in the final 10–45 seconds, the exact cutoff depending on the lead.

![Decision map, current rule vs proposed](/posts/safety/assets/safety_decision_map.png)

That window is mostly clock arithmetic, not football. A punt from deep takes a median of 11 seconds to reach the next snap, and a safety plus free kick takes 12. The map assumes the punter burns another 5 seconds in the end zone before giving himself up. Vary that assumption and the window changes with it:

| Seconds the punter burns | Leads where conceding helps, final 30 s | Largest gain |
|---|---|---|
| 0 | 5 to 7 | 1.7 WP pts |
| 5 (as charted) | 3 to 7 | 4.9 WP pts |
| 10 | 3 to 7 | 11.6 WP pts |

*WP pts = percentage points of win probability.*

Away from the final seconds the left panel has a few isolated light-blue cells, such as +7 at 4:00. These are model noise of about ±3 points, not a strategy.

The league uses the play exactly this way. Since 2012 there have been 11 intentional end-of-game safeties. Every one was by a team leading by 5 to 30 with 63 seconds or less to play. Most were not pinned at all: only 2 of the 11 snapped from inside their own 5, so most fall outside what the map models. The punter snapped from as far out as his own 34 and retreated into the end zone. The best known is Baltimore's in Super Bowl XLVII: up 5 with 12 seconds left, the punter ran 8 seconds off the clock before stepping out of the end zone.

The Ministry does not object to clock management. It objects to a rule under which running in the wrong direction is the correct play.

## The Proposed Amendment

> **Section 1.** A safety shall be scored as a touchdown for the defending team, worth six points.
>
> **Section 2.** The scoring team shall be entitled to a try, as after any touchdown.
>
> **Section 3.** Following the try, the scoring team shall kick off to the team that conceded the safety, under the kickoff rules then in force. The free kick from the 20-yard line is abolished.
>
> **Section 4.** If a safety occurs in the final two minutes of either half, the game clock shall be reset to the time remaining at the snap.
>
> **Section 5.** Nothing in this amendment shall be construed as an endorsement of punters running backward.

## Impact Assessment

| | Current rule | Act (Sections 1–3) | Act with clock reset (Section 4) |
|---|---|---|---|
| Net value to the defense | 3.83 | 5.54 | 5.54 |
| Swing for the defense, vs. pre-snap | 2.9 | 4.6 | 4.6 |
| How much better punting is, from own 1–2 | 0.83 pts | 2.54 pts | 2.54 pts |
| How much better punting is, from own 6–10 | 1.42 pts | 3.13 pts | 3.13 pts |
| Largest WP gain from conceding, any state | 4.9 | 0.1 (noise) | 0.2 (noise) |
| Lead 9+, final 10 s: conceding costs | 0 | 0 to 2.9 WP pts | 0.01 to 3.7 WP pts |

*"How much better punting is" compares expected points after a real punt with expected points after conceding. The current-rule column uses the pooled free-kick value. The Act columns use 2024–25 kickoffs.*

**Consequence, not finding.** Under the Act, conceding costs a team about 7 points instead of 2, so no state rewards it. Sections 1–3 alone leave a few states where conceding is merely free: a lead of 9 or more in the final seconds, when a punt wins too. Section 4 removes the clock time the retreat was buying, and those states turn slightly negative. The intentional safety is abolished in practice, along with the backward run.

**Cost to the league.** The Act adds 1.71 points of net value to each earned safety. At 15.7 earned safeties a season, that is about 27 points a season across all 32 teams.

**Retroactive review.** Applied to the final score alone, the Act would have reversed 20 to 30 results since 2012, depending on what the scoring team did with its try. With the usual extra point, 22 games flip and 8 more go to overtime. Among them is Buffalo at Miami in 2022, Week 3: a Miami punt deflected off an offensive player and left the end zone for a safety, and Buffalo lost 21–19. This is an upper bound and is presented as color. Teams would have played these games differently, and the defense would have kicked off rather than received.

## Objections Considered

**"It makes the goal line too important."** Correct, and measurable. Compare an offense stopped at its own 1 with one stopped in its end zone. Under current rules, that half-yard is worth 1.0 to 3.3 points to the defense, depending on the down. Under the Act, 2.8 to 5.0. Spot-of-ball and forward-progress rulings at the offense's own goal line would carry near-touchdown stakes. The Ministry notes that the opposite goal line has carried such stakes since the invention of the goal line.

**"A sack is not a pick-six."** In swing terms, it still would not be: 4.6 points against 6.7, because a pick-six usually takes the ball from an offense in better shape. The Ministry accepts this and observes that both plays end with the defense in the end zone and the offense in disgrace.

**"Penalties would become touchdowns."** Yes. Intentional grounding (22) and other offensive penalties (22, mostly holding) in the end zone would become 7-point calls, and so would 14 blocked punts that went out of the end zone. Offenses would likely respond by punting earlier, calling safer plays when pinned, and holding less near their own goal line. This analysis does not model those responses. It prices the rule against today's behavior.

**"The free kick is part of the safety's charm."** The free kick is currently the mechanism by which the safety is undervalued. The Ministry is unsentimental about it.

**"Expected points are not points."** Net value credits the scorer with the possession that follows. Under a strict reading of the scoreboard that credit does not exist. This Ministry reads the whole game.

**Samples and limits:**

- Free kicks after a safety: 185 pooled, 21 in 2024–25.
- Punts from a team's own 1–5: 449. Post-safety free kicks used in the decision map: 207.
- End-of-game kickoffs in the Act simulation: 714 real kickoffs by teams trailing by 1–8 in the final five minutes. About half were onside attempts; the kicking team recovered 5.5%.
- Each cell's outcomes are resampled from those real plays and scored with the win-probability model, assuming 2 timeouts each and an even point spread.

**Prior art.** Analysts have long noted that the free kick makes a safety worth more than two points. The Ministry claims no novelty for that observation, only for the paperwork.

## Methods and Data

- **Data:** nflverse play-by-play, 2012–2025 regular and postseason, 675,997 plays in 3,829 games, deduplicated on game and play ID.
- **Restart value:** nflverse expected points at the first snap after each kickoff or free kick, excluding the final two minutes of each half. nflverse's own EPA scores a safety as a flat −2 and leaves out the free kick, so we price the free kick separately.
- **Win probability:** a gradient-boosted classifier, constrained so that more points and better field position can never lower win probability. Trained on 2012–24, tested on 2025, including a separate check on the final 60 seconds.
- **Decision map:** each option's outcomes are resampled from real plays and scored with the model. The retreat-time and clock-reset variants are computed the same way.
- **Code:** `posts/safety/analysis/safety_analysis.py`. Every figure in this post is in `posts/safety/analysis/results.json` or the two decision-grid CSVs beside it.

## Recommendation

The Ministry recommends that the Defensive Touchdown Act be adopted at the next available competition committee meeting or, failing that, the next available Thanksgiving dinner.

*Respectfully submitted,*
*The Office of Scoring Reform, Ministry of Silly Plots*
