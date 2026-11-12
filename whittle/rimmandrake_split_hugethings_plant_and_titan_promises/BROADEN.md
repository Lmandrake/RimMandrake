# Broaden (2026-11-11, CLAUDE_STEVEDESKTOP_OFFLINE5)

**Asked:** Codex CLI (GPT, a different model), read-only. Full question: `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/broaden_question.txt`.
In short: here are the two promises, the acceptance line and what I built; what would a real user try that these demos miss,
and how could a demo pass while the promise is false in ordinary play? Six ranked, each with the observation that exposes it.

**Answer** (verbatim: `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/broaden_answer_codex.txt`):
1. A colonist already pathing through a doorway when the trunk grows across it walks through the trunk.
2. Click the cap edge and walk under the overhang from several sides: selection, collision and picture disagree.
3. Make the titan take an unscripted route: the driver could manufacture destruction at predetermined spots.
4. Cut the doorway plant, then rebuild and replant: the doorway stays impassable after the plant is gone.
5. Interrupt between crossing and death: the crowd arrives on schedule with no remains there.
6. Save and reload mid-growth or mid-crossing in a cluttered save: collision or selection changes.

**What I tried and found (offline; my lane has no game):**
- **#5, read in source:** the crowd cannot come without the remains. Scavengers and campers are made only by
  `CorpseSiteVisitors.DrawScavengers(site, n)` / `MakeCamp(site)`, called from `Building_TitanicCorpseSite` itself
  (lines 125, 129); `TitanValidationHooks.SiteDailyStep` steps only existing sites. The titan driver's CROWD phase is
  also gated on DEATH having found a new corpse site within 12 cells of the death cell, and the fake-bridge selftest
  shows a stuck crossing leaves DEATH and CROWD UNMEASURED with no damage call sent. Not a gap.
- **#3, read in the driver:** the titan's route is staged (spawned, then ordered Goto across the lane), and the driver
  says so in its rows. The destruction is not manufactured: the driver places walls, oaks and a giant and only
  counts them before and after; the breaking comes from the game's wake/clearing patches as the titan walks, sampled
  every 120 ticks with a >12-cell step counted as a teleport. A real *unscripted* route (a passage titan crossing on
  its own) is the stronger demo and is what `PassageArriveNow` gives; it is named in DONE.md as what the live run
  should try second. Not yet seen live.
- #1, #4 and #6 are live-only; #1 and #4 sit with `trunk_doors_live.py` (the door phase the plant showcase runs).
  Recorded for the live round in DONE.md.
