# Saved notes — flow, difficulty, DDA, and usability-testing sample-size math

Compiled 2026-09-11.

## Csikszentmihalyi's flow channel

Source: Wikipedia "Flow (psychology)" article (read via WebFetch — a tertiary
source; treat the underlying claims as CONFIRMED-VIA-SECONDARY, not primary-text-
read). Core model: optimal experience ("flow") occurs when perceived challenge and
perceived skill are both high and roughly balanced. Three named failure states:
- **Apathy** — low challenge, low skill.
- **Boredom** — challenge below the player's skill.
- **Anxiety** — challenge above the player's skill.
No specific numeric ratio for "balanced" is given anywhere in the tertiary source.
Original citations (existence well-established, not re-verified from primary text
this session): Csikszentmihalyi, M. (1975). *Beyond Boredom and Anxiety*; Massimini,
F., Csikszentmihalyi, M., & Carli, M. (1987) — the "eight-channel" flow model paper;
Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience*.

## Dynamic Difficulty Adjustment (DDA)

Source: Wikipedia "Dynamic game difficulty balancing" article (tertiary source,
but unusually rich and specific — read in full via WebFetch).
- Chris Crawford (1982) articulated the underlying principle: "as players work with
  a game, their scores should reflect steady improvement. Beginners should be able
  to make some progress, intermediate people should get intermediate scores, and
  experienced players should get high scores."
- Early implementations: *Gun Fight* (Midway, 1975) placed protective objects for
  disadvantaged players; *Zanac* (1986) adapted enemy AI to the player's rate of
  fire/defense; *Archon*'s computer opponent adapted gradually.
- Concrete named techniques: direct parameter manipulation (enemy HP, spawn rate);
  probabilistic "dynamic scripting" (weighted opponent tactic selection, adapted by
  outcome); ML approaches (neural nets/fuzzy systems estimating "challenge" and
  "curiosity"); genetic-algorithm online coevolution of opponents; full player/
  entertainment models predicting which game variant maximizes enjoyment.
- Real shipped examples with named mechanisms: *Crash Bandicoot* (extra hits/slowed
  obstacles after repeated deaths), *Left 4 Dead*'s "AI Director" (procedurally
  paces zombie frequency/intensity to group performance), *Resident Evil 4*'s
  10-point "Difficulty Scale," *God Hand*'s 4-level dynamic meter tied to dodge/
  attack success, *Mario Kart*'s rubber-band item distribution, *Homeworld*'s
  AI-fleet-size-scales-to-player's-surviving-fleet.
- **Named criticism: "rubber-band effect"** — AI performance visibly speeds up when
  behind / slows when ahead, breaking the fiction of a fair fight and inviting
  exploitation (deliberately underperforming to lower future difficulty). Rollings
  & Adams are cited as emphasizing that DDA should stay concealed from the player,
  since a detected system can be gamed.
- **Real controversy with a citable outcome:** a 2020 US class-action lawsuit
  accused EA of using patented DDA tech in Madden NFL/FIFA/NHL (2017+) to push
  loot-box purchases by secretly weakening high-stat players; EA called it
  "baseless"; plaintiffs voluntarily dismissed in 2021. (Confirms DDA is not just
  academic — it is legally/commercially contested when undisclosed.)
- Zook, A., & Riedl, M. (2012). "A Temporal Data-Driven Player Model for Dynamic
  Difficulty Adjustment." AIIDE 2012. DOI: 10.1609/aiide.v8i1.12504. (Existence
  confirmed via OpenAlex; academic DDA model, not read in full.)

## Nielsen's "5 users" usability heuristic — and its own refutation, with numbers

Source: Wikipedia "Usability testing" article (tertiary, but cites the primary
mechanism and gives real numbers).
- Jakob Nielsen (early 1990s, Sun Microsystems-era) popularized ~5-participant
  usability tests. Verbatim rationale quoted: "once it is found that two or three
  people are totally confused by the home page, little is gained by watching more
  people suffer through the same flawed design."
- **The Nielsen/Landauer formula:** problems found as a function of sample size,
  U = 1 − (1 − p)ⁿ, where p = probability a single session surfaces a given
  problem and n = number of sessions.
- **Direct empirical refutation, CONTESTED but with a real citable source:**
  Faulkner, L. (2003). "Beyond the five-user assumption: Benefits of increased
  sample sizes in usability testing." Behavior Research Methods, Instruments, &
  Computers, 35(3), 379–383. DOI: 10.3758/bf03195514. Open access; 1,078 citations
  (per OpenAlex, at time of lookup — very heavily cited). Per the Wikipedia
  paraphrase of this and related work: some 5-person test groups found only **55%**
  of known usability problems, while **no 20-person group found fewer than 95%.**
  Treat the 55%/95% figures as CONFIRMED-VIA-SECONDARY (Wikipedia's paraphrase of
  Faulkner's empirical result) — worth re-verifying against Faulkner's own tables
  before quoting in a rubric as a hard number, but it is a real, sourced, DOI-backed
  finding, not folklore.
- **Practical read for RimMaster:** "5 testers is enough" is contested precisely
  when problems are unevenly likely to surface (a rare but severe dungeon failure
  mode is exactly the kind of "intractable problem" that decelerates discovery per
  the model) — for a dungeon with several independent failure modes (softlock,
  guardian-skip, loot-starve), budget more than 5 walkthroughs if any one failure
  mode is rare/subtle.

## Validity threats specific to game-based measurement

Gundry, D., & Deterding, S. (2018). "Validity Threats in Quantitative Data
Collection With Games: A Narrative Survey." Simulation & Gaming, 50(3), 302–328.
DOI: 10.1177/1046878118805515. (Full abstract read verbatim.) Identifies three
game-characteristic validity threats: (1) games are complex systems that impede
predictable control/isolation of a single treatment; (2) games are rich in
unwanted variance/diversity; (3) games' social framing can differ from and
interact with the research situation they're meant to represent — plus gamers'
demographic difference from general populations. Explicit conclusion: a "dearth of
methodological studies" versus the "wealth of potential validity threats" — i.e.
the field itself says this is under-studied. Directly supports the brief's warning
that "what players say" (survey) and "what they do" (behavioral/telemetry) can
diverge for game-specific structural reasons, not just ordinary self-report bias.
