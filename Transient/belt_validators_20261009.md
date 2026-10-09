# Belt validators, 2026-10-09 (FOUNDRY helper)

## 1. LongShade/validation.py STATIC: the validator was stale, not the def
It demanded `MayRequire mandrake.rm.longshade` on RUT_JawaReturnTow; sitting 2 proved live that composed-member ids never load
(members fold into mandrake.rm.biomes). Now `gate_findings()` reads the host package from `src/RimMandrake/Biomes.compose.json`
(the entry for LongShade must exist; the gate must name `about.packageId`). Not loosened: selftest
`src/RimMandrake/LongShade/selftest_longshade_validation.py` plants the folded id, a nonexistent id, a missing gate, and a manifest
that no longer composes LongShade; all fail. STATIC now PASS (0 findings).

## 2. UtinniPatches dump selftest
Cause: tonight's repoint (00:22 PDT, 9b48689f2) made the gate `mandrake.rm.biomes`, which IS active in the load-14 dump (captured
2026-10-09T01:58Z), so the def went from "guard inactive" (skipped) to "checked"; but the def was added/changed after capture, so the
dump cannot contain it. The content is intended; the dump is stale. Fix: `dump_presence_findings` skips a MISSING def whose file's
last commit is newer than the dump's capturedUtc ("changed after dump", counted and named in the skipped dict, never for label
drift). Selftest plants both directions (newer file skipped, older file still lost). The rotsporekit gate removal was not the cause.
Re-capture the dump at the next load and the skip disappears by itself.

## 3. Jawa tow item
Exactly one live item exists: LONGSHADE_JAWATOW_LIVECHECK_1 (no RECHECK duplicate in queue/items). It carries the corrected scene
(S.run(5) before every dry run) and the Peaceful-to-Combat fix; prose line 4 now also says Peaceful else Combat.
