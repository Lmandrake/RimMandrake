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
Either raise `fillPercent` to `1.0` (a drill you can hide behind — reads like a
solid rig) or drop `passability` to `PassThroughOnly`/`Standable` (a drill you
step around). The tap already behaves acceptably; match whichever reads right
for a hand-worked vs powered pair.

`src/RimMandrake/FlowWorks/Defs/Drilling/ThingDefs/RM_LiquidDrill.xml`

## criteria
- [ ] Field changed, `validate_patch.py` clean.
- [ ] A cold load shows the line gone, diffed against a baseline the same way
      it was found — not "it should be fixed now".
