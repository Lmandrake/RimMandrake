# Done claim

- true: A1 L0: implementation and current specifications agree with the cited owner answer; focused offline checks pass. | evidence: `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/a1_spec_split.txt` `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/a1_selftest_showcases.txt` `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/a1_selftest_showcases_verbose.txt` `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/evidence/a1b_selftest_showcases_selection_probe.txt`
- unseen: A2 L2: Separate restored disposable-site demonstrations support both promises; titan showcase orders crossing, death, crowd. L4 feel remains with owner. | evidence: none: this is an offline lane, the two drivers have never run against a game.
- true: - | evidence: `whittle/rimmandrake_split_hugethings_plant_and_titan_promises/STATEMENT.md` (the three blank `- ` bullets setup wrote: no claim, nothing owed)

What A1 rests on (published `c68c7e8a91f4`, `b231dc0b0b32`):
- `design/validation_walks/RimMandrake/HugeThings.md` `## north star` (DRAFT): his card words verbatim; a must-show
  group for giant plants and a separate one for titans, the titan lines tagged in order crossing → death → crowd;
  cannot-show lines for "one demo for both" and "out of order". The walk's old "never traps a pawn" line, contrary to
  his doorway answer, is replaced by the door-seal line (id already in `validation.py`). `northstar.parse` reads 7
  must-show ids and 2 cannot-show ids (in `a1_spec_split.txt`).
- `About/About.xml` and the Designer record's `root_draft` say two promises, each with its own demo, titan first.
- `northstar/showcase_plants_live.py` and `northstar/showcase_titan_live.py`: separate entrypoints, separate sites and
  snapshot prefixes; `selftest_showcases.py` 5/5 (phase order and stamps; a failed crossing gates death and crowd).
- Ledger: `implemented` at `b231dc0b0b32`, needs=bridge, A2 L2 owed.

## What I'm least sure about
- The drivers are DIRTY (never code-reviewed) and never run live. Helper-listed HARNESS risks for the first run: the T3
  may detour around the wall (detour factor 2.5) or drop its Goto (re-ordered after 600 stalled ticks); T3 walking speed
  vs the 12,000-tick budget; the clock stop list drops death/hurt/hostile_arrival/threat_structure so the run is not
  halted mid-phase (check it hides no real colony harm); whether `list_things` lists rubble; 400-pt bullets may not kill
  a body-size-20 titan, falling back to `KillTitanAt` (labelled STAGED); `trunk_doors_live` demands exactly 17 mods; the
  titan lane (x20..120, z155..175) and plant plot (40,200) are unchecked against the calm site's buildings.
- Round 2 (published `b72e5aa81dda`): `plant_click_selects_picture` now has an instrument,
  `Source/HugePlantSelectionProbe.cs` `ClickPicture(current|x,z)`. It replays vanilla `Plant.Print` (seed, jitter, flip,
  variant, growth-scaled quad), takes the drawn variant's art-measured opaque box, and clicks every cell whose centre is
  on it through `GenUI.ThingsUnderMouse` with the Selector's own parameters. PASS only when every picture cell selects
  the plant, FAIL on any miss, SITE when selection is off. It also clicks a one-cell ring outside the quad (overreach).
- Round 2 found a HARNESS bug in round 1's plant driver: `PLANT_cap_open` sampled cells from `artboard_stage`'s
  `drawRect`, which is `Graphic.drawSize` (1x1 for a giant, because plants scale by `plant.visualSizeRange`). A live run
  would have sampled almost nothing under the cap. Cap samples now come from the probe's picture. Lesson filed.
- The new HugeThings DLL must be deployed before the live run. The probe has only been compiled and exercised through
  the fake bridge, never in a game.
- The crowd today is scavengers and camps; faction-dependent visitor responses are a separate item
  (`RIMMANDRAKE_GIVE_HUGETHINGS_VISITORS_FACTION_RESPONSES`), not built; noted there to add a visitor row to the CROWD
  phase. The CROWD phase is also staged (a forced `SiteDailyStep` with chance 1), as is the titan's spawn, route and,
  if bullets fail, its death; each staged step is labelled in the driver's rows.

## What I did not test
- No live run of either showcase; no captures; no save/load mid-scene; Codex's #1, #4 and #6 (BROADEN.md).
- A titan that crosses on its own through `PassageArriveNow` rather than a spawned and ordered T3.
- L4 feel: reserved for the owner by the statement.
