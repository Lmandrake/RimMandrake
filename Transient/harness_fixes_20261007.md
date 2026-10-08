# Harness fixes 2026-10-07 (offline, uncommitted)

Files changed: src/RimMandrake/{Wasteland,MovingDunes,TerminalBiomes,TheRot}/validation.py. Each script's STATIC run passes; none re-run live.

1. Wasteland `_field()`: modExtensions now read with deep=False (class names visible), other fields stay deep. Measures that the live biome/weather carries the named extension class. UNPROVEN live.
2. Wasteland Int32 settings: `_set()` and the settings_roundtrip chain send int(...) for int defaults ('4', not '3.0'); float fields unchanged.
3. MovingDunes: `_proof` default args "x" (ProofMath(string args)); `shipped_defs()` keeps the FULL namespaced tag (RimMandrake.MovingDunes.RM_DuneMaterialDef/...), static kinds check compares short names.
4. c78842824 fixed only Greentide and suite.set_setting; TheRot and TerminalBiomes had their own `_same`/roundtrip still tripping. Fixed both: null reads equal "" (TheRot: string field old=None treated as "", probe value still must round-trip). TerminalBiomes `shipped_defs()` also keeps full tag (RM_DefAliasDef is RimMandrake.EnvironmentalHazards.RM_DefAliasDef) so get_defs can resolve it.
5. 30 s limit: wait_ticks chunks at 2000 per call so the long tick waits (Wasteland 4000 line 1374, 2400, 2200; WeepingStones 2500) are not single calls. Suspect: Wasteland `jawa/ordered_job ... waitTicks=60, timeoutSeconds=60` (steal chain, ~line 1285 and one more) asks the tool to wait up to 60 s, over the 30 s bridge cap; not changed (cause unmeasured). Contagion: no wait over 2000; its gestation kill is 540 s total suite time, not one call. Not split.

Not done: Wasteland breached-cask text and GelatinousSlime DryingBiomes patch are MOD defects (out of scope; 5d0fed851 / af8588a48 already addressed them). run_selftests.py not run (no modcheck code touched).
