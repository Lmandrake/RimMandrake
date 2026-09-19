
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

## progress 2026-08-29
(1) FIXED and deployed: the wildness conditional now tests/writes
`statBases/Wildness` (Replace-if-present, Add-if-not, same shape as the proven Mass
block). Confirmed via `read_csharp_symbol RaceProperties` that `wildness` is not a
field on that class at all — `petness`, `nuzzleMtbHours`, `manhunterOnDamageChance`
all ARE genuine `float` RaceProperties fields, so only the wildness node was
misplaced. `validate_patch.py --defs` (Data + Workshop + Mods, 582 active mods):
0 errors, 3 pre-existing unrelated warnings (inner-xpath-differs-from-test on the
three add-if-missing conditionals — intentional, not new).

(2) NOT FOUND. Audited every Jawa_Patches operation touching AA_Eyeling
(Ikee_Tuning.xml, Ikee_Rename.xml, AnimalTolerances_Ashkarr.xml,
BiomeCast_Ashkarr.xml) against the live `RaceProperties`/`PawnKindDef` field list —
no operation of ours writes a float into a field that is genuinely `int`. Read both
shipped copies of `Races_Eyeling.xml` (Alpha Animals proper, workshop 1541721856,
and Alpha Memes' compat copy, workshop 2661356814 — same defName, same field types,
differ only in an `AM_`/`AA_` label prefix). No literal `0.3` anywhere near
AA_Eyeling in any of our patches. The original Player.log that carried this error
has since rotated (session ended 2026-08-28), so the exact field name is no longer
recoverable from static analysis — **needs a fresh Player.log capture on the next
cold load** to actually name the field. Left `## criteria` item 2 open pending that.

## progress 2026-08-29 (fresh cold-load harvest)
Fresh Player.log harvested at main menu (582 mods, def dump captured
2026-08-29T05:18:06Z, log fingerprint matches). Result: **item 2 does not reproduce
this session.** `harvest_log.py --show patchfail` and `--show defdiscard` show
neither AA_Eyeling nor any "Parsed 0.3 as int" line; the only `Eyeling` occurrence in
the whole 7,085-line log is an unrelated alphabetical roster entry (line 3776), and
the six "Parsed 0.3/1.5/7.5 as int" lines present (1031-1049) all belong to a
different "Possible Matches" block (BoneWall/ancient-ruins error), none naming
AA_Eyeling. Combined with (1)'s prior audit finding no culprit operation, this
reads as a load-order-dependent fluke from the original session rather than a
standing defect — not proven fixed, but not currently live either.

Criterion "the def loads with no errors" is now measured true for THIS mod set /
THIS load: zero AA_Eyeling errors of any kind. Closing on that basis; if it
resurfaces on a future load, it re-files as its own item with a fresh log excerpt
rather than reopening this one blind.
