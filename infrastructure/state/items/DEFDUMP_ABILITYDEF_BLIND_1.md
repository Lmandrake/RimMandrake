## spec
The def dumper writes `AbilityDef.json` as **`{"defType":"AbilityDef","defs":[],"count":0}`**
— 44 bytes — on a full capture. Measured 2026-08-21 against
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\`,
`capturedUtc 2026-08-21T08:20:20Z`, **578 mods**, `mode: all`, game at the main menu with
the def database fully loaded.

The same capture reports `ThingDef` **24,904**, `PreceptDef` 685, `MemeDef` 136,
`PawnKindDef` 1,736. ⇒ the dumper works; it cannot see this one type.

⛔ **`AbilityDef` is not an empty type in RimWorld.** Vanilla Ideology alone ships nine of
them in `Data/Ideology/Defs/AbilityDefs/Abilities.xml`, and Royalty's psycasts are
AbilityDefs. **Zero is wrong, not sparse.**

🔴 **`AbilityDef` is one of 75 empty def types out of 517 in that capture.** Some of those 75
are legitimately empty; this one is provably not. ⇒ **the fix is not "add AbilityDef" — it
is to find out why a populated type enumerates as empty**, because whatever does that to
`AbilityDef` is probably doing it to some of the other 74.

⭐ **Start from the difference.** `AbilityDef` lives in `Verse`, not `RimWorld`
(`Verse.AbilityDef`), and several of the working types are `RimWorld.*`. A namespace or
assembly-scan assumption in the type walk is the first thing to check.

⚠️ **This is not cosmetic.** It is why `IDEO_ABILITY_DEFS_UNREAD_1` existed at all, and it
forced a hand search of mod XML to answer a question the dump should have answered in one
grep. Any future check of an ability, a psycast or a ritual ability hits the same wall.

## verify
- a fresh capture writes `AbilityDef.json` with a non-zero `count`, and it contains
  `Convert`, `Trial`, `WorkDrive` (vanilla Ideology) and `VME_LeaderConvert` (VME)
- the count of empty def types drops from 75, and the ones that remain empty are checked
  against at least one known-populated example each rather than assumed correct

## criteria
`validate_save_artifact.py` on `src/Jawa/ideoligion/The Salvation.rid` reports
**266/266 resolve** and no ⬜ UNMEASURABLE line.
