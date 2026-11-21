# GimmeSomeSlack 0.1.0 — blind challenge cycle 6 (judge-1794822790)

## Start time
2026-11-16T09:54:54Z (UTC), before any input was opened.

## Changed files to bars
`git diff --name-only 0e6e0c844a origin/main` (blind_challenge excluded) lists 14 files at c991553a4f; locked files
(`tree.json`, `sheet.md`, `scenes.json`) unchanged, so no bar enters scope from a locked line.

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackMod.cs` (the settings header: "flexible pipes and" dropped) | no_hose, no_hose_in_gss, mod_settings |
| `src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll` + `.srchash` (rebuilt from it) | no_hose, no_hose_in_gss, mod_settings (and every bar the DLL carries, byte-for-byte rebuild) |
| `src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py` (decider of T_NO_HOSE) | no_hose, no_hose_in_gss |
| `version/test_table.json`, `version/stage_record.json`, `version/run_spend.jsonl` | records, no bar input (read in lane 2) |
| `journal.md`, `ledger/*` | records (sealed until lane 1) |

Lane-1 scope: no_hose, no_hose_in_gss (offline, most of lane 1), mod_settings (header), plus the AerialMath/ShockRule
kernel bars as spend allowed.

## Lane 1
Lane-1 FAIL rows, each classed Polish with the row named in its fault's evidence: K_DLL_NO_HOSE_TYPES (RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS), K_FALLEN_WIRE_LIES_ON_GROUND (RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER), K_RESTRING_IS_A_JOB (RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME).

Recorded 2026-11-16 ~10:05Z, blind (inputs: bars, settings files, Defs, Patches, the kernels `Source/Aerial/AerialMath.cs`
and `Source/Aerial/ShockRule.cs` (Verse-free, found from the shock bar's words), the shipped surface for the no-hose scan).
`python3 lane1/run_lane1.py` → `lane1/lane1_rows.jsonl`: **85 rows: 33 PASS, 3 FAIL, 3 INFO, 46 UNSETTLED** [measured]
(the 46 are `not_kernel`, one per game-side bar, all stage 6+).

- No-hose scan (`lane1/BlindLane1.py`): Defs (908 values), Patches, 125 texture paths, Languages (none), About, C#
  identifiers and 3108 literals, the settings header, srchash pairing: all PASS; 7 guard rows prove each surface can
  fail (a planted hose texture, def, pipe texPath, C# class, literal, patch, old header each turn their row red).
- Kernel (`lane1/BlindLane1.cs`, seeds from 1794822790): shock table 288 cases, joining-conduit exemption, tap one-way and
  conserved (multi-tap), theft leak swept perDay 0..10, sight 3..30, link rules, spanning forest, auto-link, kind
  switches, slider sweeps, removal plan, watchdog: PASS.
- FAIL `K_DLL_NO_HOSE_TYPES`: the shipped DLL carries hose names from the shared `_Shared/SlackGeometry`
  (`CordKind.Hose`, `LayParams.Hose`, `DrawOrder.HoseQueue`...); GSS's own source names none (row S_CS_NO_HOSE_REEL_IDENTIFIER PASS).
- FAIL `K_FALLEN_WIRE_LIES_ON_GROUND`: 23 of 2917 fallen wires put a ground point inside a wall cell, median 0.024, max
  0.238 cell deep (INFO row `K_INFO_FALLEN_WALL_DEPTH`); smallest: span 4.14 through a wall gap, repro in the row.
- FAIL `K_RESTRING_IS_A_JOB`: `RestringTicks(NaN)` = int.MinValue (`Math.Max(0.1, NaN)` is NaN); 0 and negative give 3000.

## Lane 2 reruns
`lane2/rerun_offline.py` → `lane2/reruns.jsonl` (a later row replaces an earlier one): **27 offline tests, 27 same verdict
as recorded (all PASS), 25 also match the recorded last line** [measured].
- The decider of both offline bars, `T_NO_HOSE` (`selftest_gss_no_hose.py`): **PASS rc 0**, last line `PASS  G0_clean_copy  want=green got=[]`, same as recorded.
- `T_GATE` and `T_CORD_GEOMETRY_OFFLINE` first read FAIL (O3/O3n red; build MSB3027, SelfTest.dll locked by a leftover
  dotnet.exe in my WINBUILD_ROOT); each PASS when rerun alone minutes later. Filed Polish RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK;
  it is the same flake as RIMMANDRAKE_STEADY_GSS_GATE_RED_ONCE_THEN_GREEN (claimed fixed; reopened in the mod ledger).
- Last-line differences, verdict same: `T_MATRIX` 57/57 vs 58/58 (its C2 check SKIPs: this clone lacks the untracked
  `Transient/messy_conduit_live_20261002` shots), `T_GATE` wall-clock digits.

## Planted
`lane2/planted_faults.json`, run by `lane2/plant_faults.py` (WINBUILD_ROOT private, restore on signal): **20 planted, 19 caught**
[measured]; `planted_results.jsonl` ends `tree_clean_after: true`. Caught means a new failing row, never an rc alone.
- Scan surface of the offline bars (Defs x2, Patches, About, settings literals x3, gizmo text, caller CordBuilder, caller
  AerialMaterials, DLL text and type name, srchash x2, the decider itself x2) and kernels (ShockRule x1, AerialMath x3).
- T_NO_HOSE ran on the 16 scan-surface plants: caught 10, missed 6: P05 (About.xml hose claim), P09 (GSS lays cords with
  `LayParams.Hose()`), P11 (DLL UTF-16 gizmo text, a stale-DLL case), P13/P14 (srchash, not its job), all five caught by lane 1; and P15.
- The one fault no suite caught: **P15** (the decider loses its `flexible pipes` clause; all 25 of its PASS lines stay PASS).
- Kernel faults P17-P20 each caught by lane 1 and T_CORE (selftest_gimmesomeslack.py); BITES and SETTINGS see none (not their scope).
- Lane 1's own S_DLL_BUILT_FROM_THIS_SOURCE row reds on every source plant (stale srchash), so a LANE1 catch of a C# plant was read row by row in `planted_results.jsonl`.

## Faults
`lane2/faults.json`: **0 Problem, 6 Polish** [measured: my classification]; none is `miss_of` 5 (the decider changed in cycle 5;
the two kernel ones were already filed by cycles 1 and 2).
| id | bar | what | status |
|---|---|---|---|
| RIMMANDRAKE_GUARD_GSS_NOHOSE_FLEXIBLE_PIPES_CLAUSE_UNMUTATED | no_hose_in_gss | P15 survives every suite: the cycle-5 header clause has no self-mutant | PENDING (new item) |
| RIMMANDRAKE_SCAN_GSS_ABOUT_TEXT_HOSE_CLAIMS_UNREAD | no_hose_in_gss | About.xml hose claim stays green (outside the bar's defs-and-C# scenario) | PENDING (new item) |
| RIMMANDRAKE_SEE_GSS_DLL_HOSE_NAMES_HIDDEN_IN_TAILS | no_hose | DLL holds LayParams.Hose, CordKind.Hose (shared CordLayer.cs), unseen by the byte scan; GSS never calls them | PENDING (new item) |
| RIMMANDRAKE_LIFT_GSS_FALLEN_WIRE_OFF_WALL_CORNER | cords_meet_walls_at_face | 23 of 2917 fallen wires clip a wall, max 0.238 cell | PENDING (cycle 1 item, re-measured) |
| RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_NEVER_IN_GAME | restring_cut_span | RestringTicks(NaN) = int.MinValue | PENDING (cycle 2 item, re-measured) |
| RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK | no_hose | offline rerun false red on a locked SelfTest.dll | PENDING (new item, cause unsettled) |

Why no Problem: GSS ships no hose, reel or pipe of its own [measured: lane 1 scan rows and the decider agree, 0 hits]; every
gap above is in how a future regression would be seen, or sub-cell / unreachable kernel behaviour. The pipe-pole spans GSS's
engine hangs for FlowWorks are the owner-sanctioned seam already filed as RIMMANDRAKE_REWORD_GSS_NO_HOSE_BAR_POLES_DRAW_PIPES.
Each new item carries its acceptance test (`lane2/acceptance_polish.py <case>`), watched fail (rc 1) on c991553a4f.
I first filed RIMMANDRAKE_GUARD_GSS_RESTRING_TICKS_NAN_SPEED_GOES_NEGATIVE and dropped it to the cycle-2 item; its mod-ledger
finding and the one for RIMMANDRAKE_CLEAR_GSS_FALLEN_WIRE_WALL_CLIP_BETWEEN_SAMPLES name those two older items' faults.

Verification (`maturation_dispatch.py judge-verify`, 47 findings claimed fixed): verified 9 I could check offline at c991553a4f
(the six no-hose scan findings by their recorded claim tests, rc 0; statics census; dropped cords vs the overhead master;
the goodwill remainder by my own random-window test); reopened 1 (RIMMANDRAKE_STEADY_GSS_GATE_RED_ONCE_THEN_GREEN, polish: it
recurred); the other 37 are live or have no offline test and were not ruled (owed to Stage 6).

## Fixes
None. `lane2/fixes.jsonl` is empty: no Problem found, so nothing was fixed in this cycle.

## Steward's decisions enacted
- 2026-11-16 1:28 AM PST (Conductor, allow blind cycle 6): enacted by running this cycle; recorded `--per-ruling
  CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` on the run's item (OWNER.jsonl). Its expectation, "Cycle 6 confirms that fix and exits met
  unless it finds a new Problem": confirmed: the cycle-5 header fix holds in source and in the shipped DLL (lane 1
  S_SETTINGS_HEADER_NO_PIPE_HOSE, K_DLL_HEADER_NO_PIPE_HOSE PASS) and the decider catches its regression (P03 CAUGHT).

## Tests edited
`tests_edited.json`: none. No mod test was touched; lane 1 and lane 2 scripts are new judge files under `cycle_6/`.

## Unsettled
- 46 `not_kernel` rows, one per game-side bar, all proving at Stage 6 (deferred, not failures).
- The cause of the orphaned SelfTest process (RIMMANDRAKE_KILL_GSS_ORPHAN_SELFTEST_HOLDING_BUILD_LOCK) [guess ~60%: a Windows child outliving its timed-out WSL parent].
- Whether ground cords really hide a 0.24-cell wall clip under the wall art [guess ~75%]: a Stage 6 look.
- 37 claimed-fixed findings not verifiable offline.

## Exit
```
offline_bars: {no_hose: green, no_hose_in_gss: green}
problems_open: 0
exit_met: true
```

## Owed
- Six Polish items above (none part of passing).
- Stage 6: the 46 game-side bars and the 37 live claims.
