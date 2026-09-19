# RM_LiquidDrill: impassable, player-buildable, and shootable over

## measured
Live 620-mod cold load, 2026-09-19. Diffing the distinct config-error lines of
this load against the immediately preceding session's log, this is one of
exactly three new lines:

```
Config error in RM_LiquidDrill: impassable, player-buildable building that can
be shot/seen over.
```

`RM_LiquidTap` does **not** produce it, so it is the drill's own def, not the
shared `RM_LiquidDrillExtension` or the C# class.

## what it means
RimWorld's own `ThingDef.ConfigErrors` refuses the combination
`passability = Impassable` + `fillPercent < 1` on a player-buildable: pawns
cannot walk through it but can shoot and see straight over it, which reads as
a bug to a player taking cover behind one.

## the choice, which is small but is a design call

**Decided: `passability` PassThroughOnly, not `fillPercent` 1.0.** Made and
documented here per this session's own practice (SLIME_STREAM_ROWS_1,
SYSTECH_ELECTRIC_BOLT_1) rather than left for the owner.

Checked precedent before deciding, not from memory: `RM_LiquidTap` (same file,
same C# class, same family) already ships `passability = PassThroughOnly` +
`fillPercent = 0.4` and produces no config error. Then pulled vanilla
`DeepDrill` itself straight from
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Buildings/Buildings_Production.xml`
(this drill's own texPath is a placeholder reuse of that exact def) —
vanilla ships `<passability>PassThroughOnly</passability>` +
`<fillPercent>0.5</fillPercent>`, no `coverEffectiveness` override. So the
walkable-rig shape is both the sibling's own established choice AND vanilla's
own precedent for this exact silhouette class, not a guess.

Raising `fillPercent` to `1.0` instead would have made the powered drill a
solid 2x2 wall while its hand-worked tap sibling stays walkable — an
inconsistent family (same job, same C# class, differing only in scale/power)
and a break from the vanilla building this mod's art explicitly stands in
for. Kept `fillPercent` at `0.8` and `coverEffectiveness` at `0.5` unchanged:
`PassThroughOnly` + `fillPercent < 1` is exactly vanilla `DeepDrill`'s own
combination, so it produces no config error, and the drill still reads as
bulkier/more substantial partial cover than the tap (0.4) — a walkable
installation like the real deep drill, not a bunker wall.

Changed: `src/RimMandrake/FlowWorks/Defs/Drilling/ThingDefs/RM_LiquidDrill.xml`
— `<passability>Impassable</passability>` → `<passability>PassThroughOnly</passability>`.
`fillPercent` (0.8) and `coverEffectiveness` (0.5) untouched.

`validate_patch.py --defs <Data> --defs <Mods> --defs <Workshop>` on this file:
2 pre-existing texPath errors (both `RM_LiquidDrill` and `RM_LiquidTap` report
"no file ... under any Textures/ root scanned" for the reused
`Things/Building/Production/DeepDrill` texPath — vanilla's own DeepDrill art
ships inside an AssetBundle/resources.assets, not as a loose PNG, which this
scanner does not see). Unrelated to this item, present on both sibling defs
before and after this edit, and out of this item's scope (the file's own
banner already flags the art pass as owed a bespoke replacement). No new
errors introduced by the passability change itself.

## criteria
- [x] Field changed, `validate_patch.py` clean of anything related to the
      impassable/fillPercent combo (only pre-existing, unrelated texPath
      errors remain, same on both sibling defs, before and after).
- [ ] A cold load shows the line gone, diffed against a baseline the same way
      it was found — not "it should be fixed now". **Owed** — this change was
      made and validated statically only; no cold load was run this session
      to confirm the config-error line is actually gone from Player.log.
