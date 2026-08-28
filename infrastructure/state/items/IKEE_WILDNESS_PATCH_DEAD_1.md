
## spec
Two live def errors in this session's Player.log (lines ~790 and ~1041), both tracing to
`src/Jawa/Jawa_Patches/Patches/Ikee_Tuning.xml` (game copy identical, deploy in sync):

1. **`<wildness>0.02</wildness> doesn't correspond to any field in type RaceProperties.`**
   Measured in the 1.6 C# source: wildness is a **StatDef** (`RimWorld.StatDefOf.Wildness`,
   `StatWorker_Wildness`) read via `GetStatValueAbstract`, so it lives in the ThingDef's
   `statBases` as `<Wildness>`, never under `<race>`. The patch writes into `<race>`, the
   loader discards the unknown node, and **the Ikee keeps Alpha Animals' shipped wildness 0.2**
   — the "tames instantly" half of the tuning silently never happened. Taming decay
   (`TrainableUtility.DegradationPeriodTicks`) and minimum handling skill both read the stat.
2. **`Parsed 0.3 as int` against `AA_Eyeling`** (Alpha Animals `Races_Eyeling.xml`, with
   Ikee_Tuning.xml in the error's Possible Matches). Some patched value of ours lands a float
   in an int field. Identify which operation and fix the type.

Fix shape for (1): `PatchOperationAdd`/`Replace` on
`Defs/ThingDef[defName="AA_Eyeling"]/statBases` with `<Wildness>0.02</Wildness>` —
check whether AA declares it in statBases (Replace) or inherits it (Add).

## verify
- Player.log after next load carries **zero** `[Def Error]: AA_Eyeling` lines
- live `jawa/get_defs` or stat read shows Wildness 0.02 on AA_Eyeling
- `validate_patch.py --defs` clean, every xpath MATCHING

## criteria
The Ikee tames/stays tame as the tuning intended (wildness 0.02 in the running game), and
the def loads with no errors.
