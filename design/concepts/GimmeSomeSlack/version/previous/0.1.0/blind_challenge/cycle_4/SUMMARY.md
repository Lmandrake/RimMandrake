# GimmeSomeSlack 0.1.0 — blind challenge cycle 4

## Start time
2026-11-16T01:54:01Z (2026-11-15 5:54 PM PST), before any mod file was opened.

## Changed files to bars
`git diff --name-only 34f26e4092 origin/main` over the mod's paths (blind_challenge excluded): 7 files. No locked file
(`tree.json`, `sheet.md`, `scenes.json`, `plan.md`, `record.json`, `VERSION.json`, `bars.md`) changed.

| changed file | kind | bars whose inputs it touches (lane-1 scope) |
|---|---|---|
| `journal.md`, `version/run_spend.jsonl`, `version/stage_record.json` | records | none (pipeline records, no bar input) |
| `northstar/selftest_gss_no_hose.py` | test, decider of an offline bar | `no_hose`, `no_hose_in_gss` (both offline: lane 1 spent most here) |
| `Source/SelfTest/CordGeometryChecks.cs`, `Program.cs`, `TheftChecks.cs` | the builder's kernel selftest | the bars its checks decide: cord geometry and theft (`tap_steals_and_costs_goodwill`, `power_theft`; the cord-geometry bars are game-side, `not_kernel` rows); confirmed in lane 2: `T_CORE` (`selftest_gimmesomeslack.py`) decides no offline bar; it supports stage-6 bars, among them `tap_steals_and_costs_goodwill`, `power_theft` and `cords_never_repeat` (TwinLeads now in the default run) |

## Lane 1
Committed blind, before any lane-2 input was opened. Inputs: `tree.json`, `sheet.md`, `plan.md` (grep only), `bars.md`,
`VERSION.json`, the `no_hose` row of `record.json` (its bar text), the four settings files, `Defs/`, `Patches/`, and the
kernel `Source/Aerial/AerialMath.cs` (+ the Verse-free `ConduitPlacementGate.cs`; two constants of `Core/WallMount.cs`
handed over in a stub). `lane1/run_lane1.py` runs it all: **45 rows: 24 PASS, 1 FAIL, 1 INFO, 19 UNSETTLED** [measured].

- Offline bars (`no_hose`, `no_hose_in_gss`): 4 PASS rows (defs+patches, textures, C# declarations and literals, the
  shipped DLL's type table read by a metadata reader) and 1 INFO row: the bar's words say "no hose, reel or pipe is
  drawn by this mod", its oracle and red name hoses and reels only, and GSS does draw the overhead span of FlowWorks pipe
  poles (`AerialLineKind.Pipe`, `PipeMats`), which another bar requires. Read in lane 2.
- Kernel (stage-6 bars): span sag and sway, link rules and auto-link, the watchdog, removal planning (killed /
  dismantled / gravship), re-string ticks, shock truth table, tap conservation, theft spotting, goodwill sweep 0..10,
  kind switches, clamps: PASS.
- **FAIL `fallen_random_lies_on_ground`** (seed 4405): 22 of 2500 random fallen wires put a grounded point inside an
  unwalkable cell, `Blocked` false, deepest 0.114 cell inside the cell edge; shrunk to one wall cell (26,35).
- Settings: every saved setting's field default = Scribe default = `ResetToDefaults` and inside its slider: PASS.
- 19 `not_kernel` rows (UNSETTLED, owed to Stage 6), none naming an offline bar.

## Lane 2 reruns
`lane2/rerun_offline.py` reran all 27 offline tests of `test_table.json` with their recorded commands: **27 of 27 same
verdict (PASS), 24 of 27 same last line** [measured].
- Deciders of the offline bars: `T_NO_HOSE` PASS (matches); after the fix, `lane2/reruns_after_fix.jsonl` PASS.
- `T_CORD_GEOMETRY_OFFLINE` (known red `RIMMANDRAKE_SLACKEN_GSS_SHORT_LEADS_UNDER_BAR`): PASS, 4521/4521 (recorded 4515/4515).
- `T_CORE` and `T_SHOCK_RULE_OFFLINE` (one command): PASS, 4512/4512 (recorded 4508/4508, before cycle 3 added checks).
  Oddity: the same command printed 4514/4514 in the planted-fault baseline minutes later [measured]; the check count
  varies between runs (seeded fuzz, a seed not fixed?), the verdict did not.

## Planted
`lane2/plant_faults.py` (WINBUILD_ROOT private; restores on SIGTERM/SIGINT/SIGHUP; `git diff --quiet` clean after):
**21 planted, 18 caught** [measured], each by a new failing row against the baseline.
- No-hose (offline bars, 7): NH6 (label) and NH7 (texPath) caught by `T_NO_HOSE`; **NH1..NH5 survived the decider**
  (hose texture in `topTexPath`, reel texture in `texturePath`, a FlowWorks hose def type under an innocent defName, an
  `RM_HoseReel` defName literal in C#, a patch xpath into a hose reel): caught only by lane 1. That is the Problem fixed
  below; after the fix `lane2/check_nohose_catches.py` catches 7 of 7.
- Kernel `AerialMath.cs` (5: goodwill carry dropped, days counted per window, tap over the victim's power, a cut span
  falling twice, pipe poles hostage to the power master): all caught by `T_CORE` and lane 1.
- Game-side callers (5): `ShockRule` floor ends under Only-downed-lines and `CompPowerTap` tap rate x10 caught by
  `T_CORE`; **3 survived every offline test**: an idle caught clamp accruing goodwill (`PowerTheftConsequences`), our
  fallen spans biting with the overhead master off (`RM_FallenWireShock`), the max-span slider doubled
  (`AerialLineProfiles.RangeFor`). Their bars prove at Stage 6 (live), so no offline decider was green over them: owed to Stage 6.
- Twin leads (4, the changed `CordGeometryChecks.cs` / `Program.cs`): all caught by `T_CORE`.
- Changed files: `selftest_gss_no_hose.py` (NH1..NH7), `TheftChecks.cs` (K1, K2), `CordGeometryChecks.cs` (T1, T2),
  `Program.cs` (T3, T4). The three records (`journal.md`, `run_spend.jsonl`, `stage_record.json`) carry no behaviour to plant.

## Faults
`lane2/faults.json`, each filed as a rimflow item:
- **Problem** `RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_FIVE_LEFTOVERS_SLIPPED` (no_hose, no_hose_in_gss): the decider read a
  fixed tag list, never tags, xpaths or defName literals; five planted leftovers passed. FIXED `69e7d7f47e`. Not a miss
  (the decider changed in cycle 3).
- Polish `RIMMANDRAKE_TIGHTEN_GSS_FALLEN_WIRE_WALL_CHECK_HALF_STEP` (lane-1 FAIL row `fallen_random_lies_on_ground`):
  the fallen wire's wall check steps 0.2, its drawing 0.1; up to 0.114 cell clipped into a wall, hidden under wall art
  (Conduits altitude). PENDING, `miss_of: 3`.
- Polish `RIMMANDRAKE_CLARIFY_GSS_NOHOSE_BAR_PIPE_POLES_ARE_FLOWWORKS`: the bar's words "no ... pipe is drawn by this mod"
  against GSS drawing FlowWorks pipe-pole spans (required by `settings_switch_cleanly`). NOTED_FOR_CONDUCTOR (wording,
  neutral fixer), `miss_of: 3`.
- Polish `RIMMANDRAKE_CORRECT_GSS_DRIPLOOPS_COMMENT_SAYS_ON_SHIPS_OFF`: a stale "Default ON" comment; behaviour right.
  PENDING, `miss_of: 3`.
Problems 1 (fixed), Polish 3, of them `miss_of: 3`: 3 [measured].

## Fixes
`lane2/fixes.jsonl`: `RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_FIVE_LEFTOVERS_SLIPPED`, red then green with one command,
`python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_4/lane2/check_nohose_catches.py`:
red rc 1 on the parent `46c33d40e2` ("2 of 7 caught"; run at `c1aa831c41`, whose mod tree is byte-identical), green
rc 0 at `69e7d7f47e` ("7 of 7 caught", clean tree green). Item closed at `69e7d7f47e`. Lane 1 rerun after the fix:
`lane2/lane1_rows_after_fix.jsonl` (24 PASS, 1 FAIL: the same Polish row, unfixed by design).

## Steward's decisions enacted
- 2026-11-15 5:51 PM PST, open blind cycle 4: enacted by running this cycle; ledger note with `--per-ruling
  CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER shard).

## Tests edited
`tests_edited.json`: one file, `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py`, strengthened only
(reads every non-prose field and tag, xpaths, RM_ defName literals; mutants M11..M15 added; nothing removed or loosened).
`code_review_status.py check` reads it DIRTY (never marked clean; the editor is not its reviewer).

## Unsettled
- 19 lane-1 `not_kernel` rows (UNSETTLED), every bar named proves at Stage 6; none names an offline bar.
- 3 planted caller faults survive offline (above): owed to Stage 6's live tests.
- Not settled: whether `T_CORE`'s varying check count (4512 / 4514) is a seed left unfixed; the verdict was stable.

## Exit
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: false

A Problem was FIXED in this cycle (the offline bars' decider), so by the rule a new blind judge is owed before a recorded pass.

## Owed
- A new blind judge (cycle 5, the Conductor's call after three in a visit): reads `selftest_gss_no_hose.py` as changed.
- Polish, not part of passing: the fallen-wire half step, the drip-loop comment, the no-hose bar's wording (Conductor).
- Stage 6: the three game-side callers no offline test covers (idle clamp goodwill, fallen span with the master off,
  the max-span slider).
