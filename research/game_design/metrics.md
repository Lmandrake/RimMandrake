# Experience metrics for hand-authored dungeon sites (DUNGEON_DESIGN_RESEARCH_1)

The owner's special-attention item: named metrics, defined, and HOW each is measured
or estimated for a pawn-driven, real-time-with-pause tile map (RimWorld). Sources are
cited by SOURCES.md entry number, e.g. [S15] = Left 4 Dead AI systems.

## How to read this catalog

Every metric here is measured one of four ways, in rising cost order:

- **STATIC** — computed from the map/layout alone (room graph, path lengths, turret
  placement). Costs nothing; runs before anything is built in-game.
- **SIM** — measured by scripted play through the bridge: spawn a standard crew,
  run a scripted or AI-driven clear attempt, log events. RimWorld gives us telemetry
  for free (combat log, pawn positions, damage events); patents and papers on
  agent-based difficulty measurement [S26] do exactly this with less tooling than
  we already have.
- **JUDGE** — a structured expert review (rubric with anchored scales), done by an
  agent on a save/screenshot or by the owner playing. Heuristic evaluation is
  validated practice, not a cop-out [S22][S24].
- **ASK** — post-play questionnaire (owner or testers). GEQ-style items [S23], used
  as structured prompts rather than psychometrics.

Rule of thumb: STATIC metrics gate whether a layout is worth building; SIM metrics
gate whether it is worth the owner's time; JUDGE/ASK decide whether it ships.
A dungeon should pass targets at the cheaper tiers before spending the dearer ones.

**Standard crew**: all SIM metrics assume a fixed reference party (e.g. 5 pawns,
fixed gear/skills, saved as a scenario) so numbers are comparable across dungeons
and across revisions. Without a fixed crew, every number is incomparable noise.

---

## A. Duration & pacing

### A1. Time-to-clear (TTC)
Wall-clock (game-time) from map entry to objective for the standard crew.
- STATIC estimate: critical-path tile length ÷ pawn move speed + (encounter count ×
  mean encounter duration). Good to ±50%, enough to catch a 4-hour map.
- SIM: run 3–5 scripted clears; report median and spread.
- Targets: a dungeon visit should fit one play sitting. Skyrim calibrated dungeons
  to ~20–40 min visits [S6]; for RimWorld's slower verbs, 1–3 in-game days for a
  raid-in-and-leave, with the full clear allowed to take longer BY CHOICE.
- The spread matters as much as the median (see F1 skill/luck share).

### A2. Intensity curve shape
Plot intensity over time; judge the SHAPE, not a single number [S15][S17][S18].
- SIM: compute a per-tick intensity proxy from events — weighted sum of: pawn damage
  taken (high), enemy within weapon range (medium), active threat spawned/alerted
  (medium), medical emergency (high), decayed exponentially in quiet periods. This
  is literally L4D's per-survivor intensity estimator [S15] and every input exists
  in RimWorld's event stream.
- Pass criteria (from [S15][S17][S18]):
  - alternating peaks and troughs — never a flatline in either direction;
  - peaks trend upward toward the climax;
  - every peak is followed by a genuine trough (relax phase) — L4D explicitly
    STOPS spawning after a peak; a dungeon needs authored quiet rooms that do the same;
  - the finale is NOT the maximum-intensity point of the whole visit ([S18]:
    save some headroom; exhaustion reads as tedium, not challenge).
- JUDGE fallback: draw the expected beat chart by hand at design time [S16], then
  check the SIM curve against the drawing. A beat that never registers on the curve
  did not happen.

### A3. Downtime ratio (decision drought)
Fraction of TTC in which the player has no meaningful decision pending — pure
walking, hauling, waiting. Busywork is time between meaningful actions [S27].
- SIM: tag each interval: was any input given that changed an outcome? RimWorld
  proxy: intervals where all crew pawns are in Traveling/Hauling jobs and no threat
  is active.
- Target: < 30% of a visit; any single drought > ~2 minutes real time is a finding.
  NOTE: deliberate dread-walks (flesh dungeon corridors) are exempt ONLY if short
  and scored/lit as tension [S28] — friction chosen for effect vs friction by neglect.

### A4. Beat density and variety
Count of distinct beats (encounter, discovery, puzzle, vignette, reward) per
10 minutes, and the variety of beat TYPES in any rolling window [S16][S18].
- STATIC: annotate the layout with its intended beats; count and classify.
- Target: no three consecutive beats of the same type (three fights in a row reads
  as filler; DCSS's no-brainer rule applied to pacing [S13]).

## B. Challenge & fairness

### B1. Expected cost (the difficulty scalar)
What a clear costs the standard crew: casualties (downed/dead), medical days,
resources spent (ammo/meds), colony wealth delta net of loot.
- SIM: median over repeated runs. This is the dungeon's real difficulty number, in
  the game's own currency — comparable to what a raid of N points costs the same
  colony, which anchors dungeon difficulty to RimWorld's existing raid-points scale.
- Target: set per dungeon tier (outer works cheap, core expensive) — the vault's
  concentric structure is EXPLICITLY a rising cost gradient (VAULT_DUNGEON_CONCEPT_1).

### B2. Failure-point heatmap
WHERE runs go wrong: per-cell/per-room counts of pawn downs, deaths, retreats.
- SIM: log positions of every down/death across runs; render on the map [S26].
- Findings: one room owning most deaths = spike to smooth or telegraph harder;
  deaths uniformly everywhere = attrition tuning, not layout, is wrong.

### B3. Telegraphing / fairness index
Every lethal threat must be perceivable before it can kill. Tomb of Horrors is the
canonical NEGATIVE calibration — celebrated as artifact, miserable as experience [S9].
- JUDGE (checklist per threat): Is there a visual/audio/textual cue before first
  damage? Is the cue readable at the zoom level players actually use? Does the cue
  precede the kill by enough time to react at real-time-with-pause speed?
- Target: 100% of instant-lethal threats cued; ambushes allowed but must be
  survivable-by-default on first contact (the L4D rule: surprise, then a fair fight
  [S15]).

### B4. Counterplay availability (no no-brainers, no walls)
For each threat: how many distinct viable answers does the standard crew have?
DCSS states it as constitution: meaningful decisions, no no-brainers [S13].
- JUDGE: enumerate answers per threat (range it down, melee rush, flank via loop,
  avoid entirely via alternate route, environmental counter e.g. temperature/darkness).
- Target: ≥ 2 viable answers per threat, and ≥ 1 that does not require a specific
  item — otherwise the threat is a key in disguise and belongs in the lock-key
  diagram (D2), not the difficulty budget.

### B5. Turtle test (killbox inversion)
RimWorld players win fights by funneling AI into prepared ground [S30]. Inside a
dungeon the SAME instinct appears: camp a doorway, let the garrison feed itself in.
- SIM: script the degenerate strategy (breach one door, hold it, wait) and measure
  whether it beats the intended experience on cost (B1) and time (A1).
- Pass: turtling must be either (a) unrewarded — garrison holds position, does not
  path into the funnel (DOOM's answer: incentives that pull the player forward
  [S19]); or (b) explicitly priced — e.g. the undercave collapse timer [S29] makes
  time itself the cost. A dungeon that is best played as a stationary killbox has
  failed as a dungeon regardless of every other number.

## C. Tedium (the anti-metrics)

### C1. Backtracking cost
Tiles re-traversed with nothing new on them, as a fraction of total tiles walked.
- SIM: count revisited cells with no new content/threat state since last visit.
- Benchmark: Spencer Mansion — a map built ON re-visiting — still averages only ~2
  visits per room [S7]; Wind Waker builds loops so backtracking ≈ 0 [S4].
- Target: revisit fraction < ~30%, and every forced re-traversal should cross at
  least one changed thing (new breach, patrol shift, vignette stage 2). Loops (D1)
  are the structural fix, not shortening the map.

### C2. Grind/scum susceptibility
Does any low-risk, high-time, some-reward loop exist? (Farmable infinite spawns,
re-enterable loot rooms, wait-out-the-turrets.) DCSS treats this as a design bug
by constitution [S13].
- JUDGE: enumerate renewable rewards and their risk; SIM the suspicious ones.
- Target: zero. If a loop must exist (respawning fleshmass), its yield must decay
  or its risk must grow.

### C3. Micromanagement load
Count of player inputs per minute REQUIRED (not chosen) during the visit, especially
non-combat inputs: door micro, haul micro, re-drafting.
- SIM: log input events in attended test play (owner or agent-with-UI).
- Findings threshold: any single required interaction repeated > ~5 times without a
  decision attached is busywork [S27] — automate it, batch it, or delete it.
  Haul-out design matters here: loot extraction is a RimWorld-specific tedium trap;
  a Dark-Souls-style unlockable shortcut to the entrance [S8] is the fix that also
  rewards exploration.

## D. Structure & navigability

### D1. Loop count / route multiplicity
Number of independent cycles in the room graph (graph-theoretic: edges − nodes + 1
per connected component), and number of distinct viable entry→objective routes.
- STATIC: build the room adjacency graph from the layout; count.
- Targets from the corpus: ≥ 2 entrances [S1]; ≥ 1 loop per dungeon "act" [S1][S2];
  a pure tree (0 loops) is acceptable only for a Five-Room-scale site [S5].
  Cyclic generation's insight [S2]: author the loop FIRST and hang rooms off it.

### D2. Linearity index (lock-key)
Draw the Boss Keys diagram [S4][S3]: fraction of the visit during which exactly one
openable "door" (progression option) exists.
- STATIC: from the lock-key graph.
- Findings: near-1.0 = corridor with extra steps (late-Zelda failure mode);
  near-0.0 = players wander unstructured. The celebrated dungeons sit in between:
  2–3 live options at most times, converging before the climax.

### D3. Legibility / mental-map test
Can a player who has cleared half the dungeon point toward the exit and the
objective?
- JUDGE: on the map, check landmark count (≥ 1 unique visible landmark per zone),
  zone palette distinctness, and sight-lines that preview destinations
  (foreshadowing: Undead Burg shows you the bridge before you earn it [S8]).
- ASK: after test play — "sketch the map from memory"; gross topology recalled =
  pass (the concentric vault should be sketchable as three rings).

### D4. Foreshadow-payoff pairs
Count of things SEEN before they are REACHED (visible core behind blast doors,
audible thing behind a wall, world-ender turrets guarding a gate = the loot promise,
VAULT_DUNGEON_CONCEPT_1). Cyclic patterns treat this as a first-class cycle type [S2].
- STATIC: annotate; Target: ≥ 2 per dungeon, ≥ 1 for the central payoff.

## E. Enjoyment & experience (judged/asked)

### E1. GameFlow rubric score
The 8 GameFlow elements (concentration, challenge, skills, control, clear goals,
feedback, immersion, social) scored per-criterion on the revised detailed
heuristics [S22], by a reviewer who has played or watched a full run.
- JUDGE: use as a structured review sheet; report per-element, never one number.
  For a colony-sim dungeon the load-bearing elements are challenge (matches crew
  power?), clear goals (does the player know why they're here?), and feedback
  (does the map show progress?).

### E2. Post-visit experience probe (GEQ-derived)
Short structured ASK after the owner (or a tester) plays: items covering
tension, challenge, positive/negative affect, immersion — the GEQ core dimensions
[S23], reworded for one dungeon visit. Include the two questions that predict
everything: "would you go back in?" and "what will you tell someone about it?"
- The answer to the second is the memorable-moment inventory (E3).

### E3. Set-piece / memorable-moment density
Count of moments a player would retell (the toppled pillar, the thing in the ice,
the room that was a mouth). MDA's aesthetics [S25] name what kinds of fun each
serves — a dungeon should consciously cover ≥ 3 of the 8 (here: challenge,
discovery, narrative, sensation).
- JUDGE at design time (beat chart column [S16]); ASK after play (unprompted recall
  is the only honest measure of memorability).

### E4. Fantasy-fulfillment check
Does the dungeon let the player do the thing its fiction promises? (A vault
promises heist verbs: case it, breach it, grab, run. A flesh dungeon promises
dread + revulsion + the reveal.) MDA: the player meets the game feeling-first [S25].
- JUDGE: one question per dungeon family, answered with evidence from a run.

## F. Replayability & robustness

### F1. Skill/luck share
Run the SAME crew with the SAME strategy N times: outcome variance is the luck
share. Then run better/worse strategies: outcome delta is the skill share.
- SIM only. Target: strategy delta ≫ repeat variance (skill dominates), but repeat
  variance > 0 (structured unpredictability [S15] — patrol timing, wake order
  randomized within authored bounds).

### F2. Strategy-space breadth
Number of qualitatively distinct viable approaches (full clear, raid-in-and-leave,
stealth skim, siege from outside, second-entrance flank). The vault's concentric
proposal explicitly funds this metric.
- JUDGE: enumerate; SIM the top 3 to confirm "viable" means viable.
- Target: ≥ 3 for a major site; each should differ in cost profile (B1), not just
  in route.

### F3. Reveal reliability
For narrative dungeons: does the reveal beat fire on EVERY viable route (F2)?
RimWorld quest signals fail silently (rimworld-quests skill: one bad inSignal kills
a chain with no error).
- SIM: script each strategy from F2; assert the letter/memory-surface event fired.
- Target: 100%. A reveal that only fires on the full-clear route is a defect, not
  a reward.

---

## Minimum instrument set (what to actually build first)

1. **Room-graph extractor** (STATIC): from a layout (savegame or layout XML) →
   adjacency graph → D1 loops, D2 linearity, A1 path estimate. Pure offline analysis.
2. **Standard-crew clear harness** (SIM): bridge script — spawn crew, run strategy
   script, log combat events, downs, positions, timestamps → A1, A2, B1, B2, B5, C1.
   Most of this is existing rimbridge capability plus an event logger.
3. **Review sheets** (JUDGE/ASK): GameFlow-derived rubric + post-visit probe as a
   review-sheets artifact the owner fills after playing — his LOOK, captured as data.

The three tiers deliberately mirror the project's existing practice: offline
analysis before game time, bridge quicktests before owner time, owner judgment as
the final gate.
