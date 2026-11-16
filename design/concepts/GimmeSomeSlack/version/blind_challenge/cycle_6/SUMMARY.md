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
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
