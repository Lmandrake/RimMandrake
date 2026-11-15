## spec
`scene_temperament` (src/RimMandrake/Graffiti/validation.py, component `cleaning_break_open_only_to_clean_freaks`) cannot read whether
`MentalBreakWorker_GraffitiCleaning.BreakCanOccur` (Source/GraffitiCompulsiveClean.cs:14) opens the compulsive cleaning break only to a
neat-2 pawn. `jawa/pawn_force_mental_break` calls `MentalBreaker.TryDoMentalBreak`, which goes straight to `Worker.TryStart` and skips
`BreakCanOccur`, so forcing the break proves the state works but not its gate; a natural break after lowering mood is a random pick among
every minor break. Add a probe to `RM_GraffitiSocialProof` (e.g. `BreakCan "Nick"` -> `BREAKCAN <Nick> cleaning True|False | neat N | due B`)
that answers `DefDatabase<MentalBreakDef>.GetNamed("RM_GraffitiCompulsiveCleaningBreak").Worker.BreakCanOccur(pawn)`, rebuild the DLL, and
replace the component's MISSING TOOL with: true for the clean freak (Neurotic 2), false for the ordinary viewer. Found by
RIMMANDRAKE_SCRIPT_GRAFFITI_MOOD_SCENES_THREE_FOR_SIX_BARS (offline; the live row stays UNRUN until a game runs it).

## acceptance test
Watched failing on the base 2026-11-15 (no BreakCanOccur probe; MISSING TOOL still raised); expected `PASS`:

    grep -q "BreakCanOccur" src/RimMandrake/Graffiti/Source/RM_GraffitiSocialProof.cs && ! grep -q "MISSING TOOL: no probe reads MentalBreakWorker_GraffitiCleaning" src/RimMandrake/Graffiti/validation.py && echo PASS
