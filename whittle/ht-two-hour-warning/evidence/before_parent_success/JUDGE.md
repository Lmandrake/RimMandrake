# Judgment: RIMMANDRAKE_SET_HUGETHINGS_TREMORS_TWO_HOURS

Reviewed this clone at `f3c6f9346befdd2fd1bdbf14064a09f6291270f2`. The source correction is supported; the required live acceptance is not. O02 is not applicable by the user's declared other-host exception. That exception does not excuse O13.

Review hygiene limitation: I inadvertently opened `evidence/final_inspection.json`, a mixed inspection/summary containing builder conclusions. I excluded it as support and independently inspected the source, original build/deploy output, command receipt and preflight reports below. I did not read DONE.md, BROADEN.md, FINDINGS.md or other-agent runner/broaden outputs. Because of that accidental summary exposure, this review cannot claim the requested completely unexposed review condition.

## Statement bullets

1. **true — shipped initializer, missing-key Scribe default and sanitization fallback are two hours, with player tuning and slider preserved.** In `src/RimMandrake/HugeThings/Source/RM_HugeThingsSettings.cs`, lines 82, 163 and 202 use `2f`; line 164 sanitizes during loading. Lines 403–404 retain the displayed current value and 0.5–24 hour slider. `Source/Kernel/RM_TitanicKernel.cs:34` substitutes the fallback for NaN/infinity and preserves finite in-range values, including six. Finite out-of-range values still clamp to the bounds; this is not a promise that every invalid finite value becomes two. The initializer snapshot used by reset remains at settings lines 422–438. Source commit `54498cc0e84cb828dc4cb47f51e7571137fbfa69` contains these changes. This verdict establishes the shipped source contract, not an observed first-run or absent-key game load.

2. **true — current validation defaults, warning text and titan-event specification agree.** `validation.py:72` uses `2.0`; `Languages/English/Keyed/RM_HugeThings.xml:104` removes “(provisional)” from the warning label and substitutes the current setting. `infrastructure/state/items/TITAN_CAMPS_SCAVENGERS_EVENTS_1.md:23` specifies default two; its settings description explicitly records the owner's two-hour ruling and preserves valid tuning. No provisional-six requirement remains in these current scoped surfaces. Other corpse/camp numbers remain provisional. This is source/text agreement, not an assessment of rendered UI or feel.

3. **cannot tell — deployed DLL's live fallback, WarningTicks result, custom six and exact restoration.** There are no original probe call/results, original field snapshots, restoration readbacks or settings-file before/after hashes in the supplied evidence. `evidence/live_run_1/receipt.json` records deployment followed by failed offline preflight, cleanup and release, with `ok: false`; it contains no launch, live preflight or probe command. The evidence directory has no `live.json` or live-preflight receipt. Thus neither live failure nor live success of the correction is established. Exact restoration was not demonstrated; a probe that never ran does not pass a restoration requirement.

   The proposed `northstar/warning_defaults_live.py` is appropriately narrow in intent: it checks artifact/source identity, discovers schemas, snapshots all 27 numeric fields assigned by `Sanitize` before mutation, tries NaN → Sanitize → two → 5000 ticks and six → Sanitize → six → 15000 ticks, then restores every original field string in `finally`, requiring identical readbacks and unchanged HugeThings settings-file hashes. It avoids another Sanitize during restoration. Those are code paths, not receipts. Source `WarningTicks` at kernel line 227 predicts 5000 for two, and `Titanic/Events/TitanPassage.cs:41` schedules using that conversion; neither proves execution in SteveDesktop's loaded assembly. Persisted valid six is deliberately preserved, not migrated to two.

4. **false — offline checks and artifact provenance are supported, but required preflight is not green and no live preflight exists.** `evidence/static.stdout` reports zero findings; `direct_checks.json` reports the nine source/syntax checks true. Their `.rc` files are zero. Both `selftests.stdout` and `selftests_frozen.stdout` report 1/1 PASS and zero failures/crashes, with zero exit codes. Both also report the selftest changed during the run and was not recordable; these are recorded executions, not stable cached certifications. The selftest exercises planted lint defects, not this live warning contract. The statement's exclusion of complete crossing, arrival, UI-feel and flight acceptance is appropriate and retained here.

## Build, deployment and preflight identity

`evidence/build.stdout` failed for missing Harmony; `build_retry.stdout` ended with 429 compiler errors. Both exit codes are one. The later original `build_stevedesktop.stdout` reports a successful Release build, zero warnings/errors, from source `54498cc0e84c`, with exit zero. Build commit `f3c6f9346befdd2fd1bdbf14064a09f6291270f2` changes only the DLL and its source stamp.

My read-only hash inspection found:

- DLL SHA-256: `e1d1b0623922831d9b3ce52f8da24678b1585e66c6c97c29dca8a3edc50ee5d0`.
- Stamp SHA-256: `f50d0d075358b4c8de39598f937933256ab9e0cdd4d7eab117f24ef1a450317d`.
- All 50 stamp source entries match this clone, and the stamp's DLL hash matches the actual DLL. The project explicitly includes these compiled source files. No tracked scoped changes differ from HEAD.

`evidence/live_run_1/deploy.stdout` names SteveDesktop's `D:/SteamLibrary/steamapps/common/RimWorld/Mods`, applies the DLL, stamp and two language XML files, and reports “VERIFIED in sync”; `deploy.rc` is zero. This supports deployment of the matching pair at that time. It does not identify a subsequently loaded game assembly: the receipt stops before launch. I did not inspect another clone or the live installation directly.

Original preflight receipts are `evidence/live_run_1/preflight_offline.json` (09:44:10Z) and `evidence/preflight_dependency_retry.json` (09:46:41Z), corroborated by their stdout and exit-one receipts:

| Required row | Initial | Retry |
| --- | --- | --- |
| O02 bridge lease | Not applicable | Not applicable |
| O01 game down | PASS | PASS |
| O03 disk space | PASS | PASS |
| O04 ModsConfig intent | PASS | PASS |
| O05 list sane | PASS | PASS |
| O07 known wedgers | PASS | PASS |
| O08 log archive | PASS | PASS |
| O09 companion match | PASS | PASS |
| O12 source load killers | PASS | PASS |
| O13 deploy match | FAIL | FAIL |
| O14 effective def lint | UNMEASURED | PASS |

O14 initially could not import `lxml`; the retry reports clean with unsupported `donor_types` scope. O13 still reports drift in FlowWorks (10 files) and GimmeSomeSlack (46 files), including the latter's DLL/stamp. The retry verdict is explicitly `NO-GO O13`. These are required rows and cannot be waived merely because this correction concerns HugeThings. Optional O06/O11 pass; optional O10 remains unmeasured. O09's PASS is a companion byte match, with its own caveat that no companion source stamp is present; it is not a HugeThings live result. There is no required-live-row report to evaluate.

## Defects and exact limits

The blockers are the remaining required O13 failure and missing live settings/restoration evidence. No scoped source defect was found. A successful build, matching stamp, deployment verification, written probe or filename cannot supply the missing live acceptance. Original cleanup output reports the SteveDesktop guard and lease free; that is lease cleanup, not settings restoration.

This review ran no tests, builds, deploys, ledger commands or bridge/game controls, sent no messages to others, and wrote only this file. It makes no gameplay, crossing, arrival, UI-feel or flight judgment. The accidental summary exposure described above is an additional limitation on the requested review process.

would show: no
