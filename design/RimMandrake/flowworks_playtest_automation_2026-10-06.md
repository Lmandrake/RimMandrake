# FlowWorks playtest automation — three GPT reviews, merged (2026-10-06)

Asked by the owner, 2026-10-06, typed: *"I am pretty desperate and need a very strong new approach that will allow an
automated playtesting process to get me most of the way there and make human reviews VERY productive. The current
methods is insanely slow and mostly slowly grinds improvements on its own process and test harness rather than the
game improvement itself."*

**Inputs.** One 1.04 MB bundle (83 files: FlowWorks design, core C#, northstar plan and checkout code, the human
review map and key sheet, bridge timings, skills, lessons, FOUNDRY handoffs, this morning's northstar review) sent
three times to gpt-6.1-sol: run A at high effort, runs B and C at xhigh. Prompt, file list and the three full answers:
`Transient/flowworks_playtest_review_2026-10-06/` (14-day shelf; this file is the durable copy).

## The answer: all three runs agree

1. **Move the playtest into the running game.** A small dev-only C# scenario runner (in the JawaBench companion or
   its own dev assembly) runs concrete *player episodes* on the main thread across ordinary ticks: designate a
   trench → a pawn digs it → liquid enters → someone is trapped → it is ignited → save, reload, continue, compare.
   One bridge call starts it; C# owns execution; each result is written to a JSONL journal the moment it completes.
   Python stops constructing experiments through hundreds of RPCs.
2. **The product of every run is a ranked defect list plus one prepared review save.** Failures are grouped by
   cause and ranked: state loss/crash/wrong liquid → broken player loop → wrong behaviour/performance → visual and
   balance questions. The save holds only what a machine cannot judge.
3. **The owner's sitting is ~8–12 stops, 10–20 minutes,** game loaded and framed, Next/Back plus
   **Accept / Change / Unclear** buttons in game, verdicts written automatically to a decisions file that turns
   "Change" into a work item. He is never asked to start a flood, spawn a fire, wait days or check whether a pump
   works: those are staging work the agents finish first.
4. **Do not build a framework.** No general scenario language, no all-mod harness, no new dashboard or observatory.
5. **Contradicts this morning's northstar review on priority:** repairing the project-wide scoreboard is not the
   next FlowWorks step; FlowWorks' latest run already records matching DLL identity.

### The three approaches each run was asked for (same three in all runs)

| | How | Covers | Cost (GPT estimate, not measured) | Live minutes per run |
|---|---|---|---|---|
| **A. In-game scenario runner** (all three prefer) | C# episodes through real designators, WorkGivers, jobs, Fire, Scribe | Every functional item on the owner's list; stages the visual ones for him | pilot 1–2 agent-days; useful coverage 5–9 | 3–10 warm |
| **B. Offline liquid kernel** | Extract flow/body/donor logic into a pure `RM_FlowKernel.cs`, generate thousands of dig/pour/pump/burn/refill sequences against invariants, shrink failures to seeds | Flow, stocks, depth/fill, viscosity, no-mix, refill arithmetic. Not jobs, rooms, rendering or Scribe | 2-day spike; 6–12 days broad | 0 (plus a short live adapter check) |
| **C. Agent plays bounded missions** | Fixed goals (defensive canal; trap and keep a prisoner; liquid chain + river crossing) through real UI only, action trace, hard deadline | Discoverability, friction, surprises nobody specified. Weak systematic coverage | 2–5 days pilot | 15–40 per episode |

### The four outputs (owner asked for a rigorous evaluation; (a) required)

- **(a) Ranked defects + one review save:** all three runs: *make this THE product.* About 0.5–1 day to adapt the
  existing label/save/decision machinery.
- **(b) Player agent reporting friction:** later, rationed (weekly or per candidate), once A's episodes pass. Kill it
  unless three runs (≤60 live minutes) find something reproducible that A missed.
- **(c) Pass/fail every build:** yes for the offline C# selftests on every build; a small in-game smoke per
  deployed batch; never the full checkout on every build.
- **(d) Layered:** worth it only at different cadences: offline every build, A per candidate, C weekly, full mod
  list once per candidate.

## Code findings the runs made, all 15 CONFIRMED against current source (BENCH, 2026-10-06)

Source-level, not yet reproduced live. Paths are under `src/RimMandrake/FlowWorks/`.

| # | Finding | Evidence |
|---|---|---|
| 1 | Touching natural water and tar can merge into one body carrying one fluid | `Source/RM_LiquidStock.cs:157,168`; tar is tagged Water (`Defs/LiquidTypes/TerrainDefs/RM_Tar.xml:41`) |
| 2 | Scarce-supply allocation order changes after a reload | `Source/RM_MapComponent_Excavation.cs:1058-1062` |
| 3 | Legacy flood writes temporary terrain without updating fill or fluid identity | `Source/Flood_FlowWorks.cs:321-331` |
| 4 | Detonating liquids explode but then burn at the slow rate; no immediate consumption | `Source/RM_LiquidFire.cs:216-222, 336` |
| 5 | Fire's carried accumulator is not saved | `Source/RM_LiquidFire.cs:47-49, 71-77` |
| 6 | The wall-face proof regenerates the mesh before measuring it, so it repairs what it should detect | `Source/RM_NorthstarProofs.cs:155` |
| 7 | Colonists who fall into a pit take no fall damage (only "captured" pawns do), contradicting key-sheet stop 19 | `Source/Superdeep/RM_SuperdeepTrap.cs:56-69, 211, 313` |
| 8 | The visual board ties fill to depth (`max(1, D-1)`), so depth and fill are never shown independently; stop 35 promises a "trace" fill at D2 that cannot exist | `review_map_visuals.py:64-68`; `KEYSHEET.md` ~375 |
| 9 | Sluice: code passes liquid through closed flow doors; the key sheet says a shut sluice holds and opening it floods | `Source/Superdeep/RM_FlowDoors.cs:13-15`; `Flood_FlowWorks.cs:295-300`; `KEYSHEET.md:277-281` |
| 10 | The dig designator refuses non-soil, but the review's granite scenes are made by calling `Deepen()` directly | `Source/Designator_DigCanal.cs:91`; `review_map.py:638` |
| 11 | A SKIP row leaves its component's PASS standing | `validation.py:105,128` |
| 12 | The latest extension run resurrected/restored colonists 18 times | `northstar/extension_result_20261006T041420.json` |
| 13 | The 59-row core has no save/load and no performance row | `northstar/validation_v2.py` `declared_rows()` |
| 14 | The 34-station visual board is 700 bridge calls | `review_map_visuals.station_ops()` (run) |
| 15 | Lip occlusion hides a pawn or item standing on the lip | `Source/Superdeep/RM_PitLipOcclusion.cs:21` |

The owner ruled the two intent questions the same day (typed on a question card):
**#7** — colonists never path in; they fall only when blown or forced in; enemies also fall into a concealed pit
(`FLOWWORKS_PIT_FALL_ONLY_FORCED_1`). **#9** — two doors: a sealed sluice gate (standard) and a metal grate gate that
always passes liquid (`FLOWWORKS_SLUICE_TWO_DOORS_1`).

**Status: no plan adopted.** The owner, 2026-10-06: *"we're going to discuss the results with you first before we
agree to any plan. We'd like to understand all the options presented first. We may have other thoughts."*

## Measured context the runs leaned on

- Latest FlowWorks core run: 251.1 s, 872 bridge calls, 59/59 PASS; pits + promoted phases are 74% of wall time and
  91% of ticks (`validation_v2_result_20261006T040914`), so cutting RPCs alone cannot make it fast.
- 2026-10-01 time ledger: of 210 live minutes, 84.7 failed their own setup gates and 64.0 were lost or voided.
- Since 2026-09-20: 87 FlowWorks commits touched harness/review tooling, 74 touched the mod (path heuristic,
  overlapping). Python around FlowWorks 794 KB vs mod C# 843 KB (the Python includes the liquid generator).

## First week (merged from the three plans)

| Day | Work | Pass test |
|---|---|---|
| 1 | Smallest runner, fixed fixture, results journal; touching-fluid (#1) and reload-allocation (#2) reproducers | Runs without per-step bridge calls; an interrupted run keeps its results and reads INCOMPLETE; removing the no-mix guard turns it red |
| 2 | Real designate → pawn digs → fill in, terrain legality incl. stone (#10), construction, quarry | Making a job's effect a no-op fails the test; original terrain restored; ≥1 real mod defect fixed |
| 3 | Pit/prison: entry, escape attempts, ladder, room, capture, a real lip-service job; first small review save | A warden completes a real job without entering D4; the save reloads with ≥8 judgment questions |
| 4 | Pumps/tanks/converters, real Fire and explosion, extinguishing, refill, two-fluid contact, sluice per the owner's ruling | Accounts balance per fluid; flame lights the eligible fluid and not the control |
| 5 | Save/load continuation and performance; fixed-camera render checks; compact depth×fill board (all 14 legal pairs) | A dropped saved field fails; a suppressed mesh refresh is caught before any forced regeneration |
| 6 | The owner's sitting on the new save | He starts without setup, finishes ≤20 min, verdicts persist by themselves |
| 7 | Candidate on the real mod list; final defects + save pair | Results name the build and list; untested areas show as gaps |

**Kill rule (strictest of the three):** at most two agent-days of runner infrastructure. From day 3, freeze tooling if
over three days it takes more than 30% of agent effort without closing ≥2 game-facing findings, if setup/instrument
failures exceed 20% of live time, or if the review save is still unusable at day 3. On a freeze: spend 48 hours
fixing the top three mod problems with existing tools; a tooling change is allowed only for a named present defect.
Lead measures: **player-facing faults fixed, owner judgments per sitting, invalid live minutes.** Not rows or checks.

## Stop now (agreed by all three runs)

- Counting `shows=` mappings as proof of appearance, and labelling mapped PASS as "works in game".
- The 51-stop feature tour as the routine review; keep it as an inventory only.
- Asking the owner to manufacture stimuli ("spawn fire", "start a flood", "unpause for days").
- Resurrecting or healing subjects between scenarios; a death is a result.
- Forcing a refresh before testing that normal refresh works (#6).
- Treating pumps, prisoner service, bottles and rivers as optional "extensions"; they are shipped behaviour.
- A permanent runtime guard for every discarded theory (`debug_process.md` §2.4); keep the note, guard only real
  recurrences.
- Several copies of defaults/settings/status (`BOOL_DEFAULTS`, `site_spec.SETTINGS`, extension defaults).
- "Keep the bridge busy" as a goal; an idle seat while agents fix mod code is fine.
