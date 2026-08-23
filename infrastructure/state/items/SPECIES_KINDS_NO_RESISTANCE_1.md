## spec
All 69 generated Star Wars species pawnkinds omit `initialResistanceRange`, and the
field is `FloatRange?` that vanilla dereferences with `.Value` in three places.

MEASURED off the 2026-08-23 11:22 log (`observed/logs/Player.2026-08-23_1122.going-down.log`):
69 lines of `Config error in RimMandrake<Species>_Kind: initial resistance range is
undefined for humanlike pawn kind.` — one per def in
`src/Jawa/RimMandrake_StarWarsRaces/Defs/PawnKindDefs/RimMandrakePawnKinds.xml`.
`grep -c initialResistanceRange` on that file returns **0** against **69** `<PawnKindDef>`.

WHY IT IS NOT COSMETIC. `PawnKindDef.cs:105` declares `public FloatRange? initialResistanceRange;`
and `PawnKindDef.cs:484` is the ConfigErrors that fires. Three call sites take `.Value`
with no null guard:
  - `Pawn_GuestTracker.cs:467` — the made-a-prisoner path. An `InvalidOperationException`
    ("Nullable object must have a value") the moment a pawn of one of these kinds is captured.
  - `ITab_Pawn_Visitor.cs:225` — drawing the prisoner tab.
  - `SanguophageUtility.cs:196` — resistance gain on a feed.

The parent is the problem, not an oversight per def: `BasePlayerPawnKind`
(`Core/Defs/PawnKindDefs_Humanlikes/PawnKinds_Player.xml:4`) sets `initialWillRange` but
NOT `initialResistanceRange`; vanilla `Colonist` supplies its own `13~21`, and `Slave`
`9~15`. Inheriting the base does not get you the field.

## fix
The file is GENERATED — its header says do not hand-edit. The one-line fix belongs in
`src/RimMandrake/Utils/gen_races_mod.py`, emitting `<initialResistanceRange>13~21</initialResistanceRange>`
(vanilla Colonist's value) on every kind, then regenerate and deploy.

## criteria
Next cold load: zero `initial resistance range is undefined` lines in Player.log
(currently 69).

## verify
- log census: `grep -c 'initial resistance range is undefined' observed/logs/Player.2026-08-23_1122.going-down.log` -> 69
- source: `grep -c initialResistanceRange src/Jawa/RimMandrake_StarWarsRaces/Defs/PawnKindDefs/RimMandrakePawnKinds.xml` -> 0, against 69 `<PawnKindDef`
- mechanism read off the decompile at `D:\Luke\dev\reference\rimworld-decompiled\` — PawnKindDef.cs:105/484,
  Pawn_GuestTracker.cs:467, ITab_Pawn_Visitor.cs:225, SanguophageUtility.cs:196.

## Watch out
- 🔑 **The XML is generated.** Editing `RimMandrakePawnKinds.xml` by hand is undone by the
  next `gen_races_mod.py` run. Fix the generator.
- ⚠️ **The ConfigError count is not the exposure.** These kinds are
  `defaultFactionDef PlayerColony`, so whether one is ever CAPTURED depends on whether a
  hostile faction fields them — the equipment/faction layer deployed 2026-08-23 may have
  changed that. A load with zero config errors proves the field is set; it does not prove
  the crash was reachable before.
- ⚠️ `BasePlayerPawnKind` supplies `initialWillRange` and NOT `initialResistanceRange`.
  Anything else generated off that parent has the same hole — check before assuming these
  69 are the whole set.
- The vanilla numbers are `Colonist 13~21`, `Slave 9~15`. Picking Colonist's is a design
  choice, not a fact; DECIDE may want a different range per species.
