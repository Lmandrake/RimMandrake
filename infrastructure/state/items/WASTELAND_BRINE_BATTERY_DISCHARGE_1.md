# WASTELAND_BRINE_BATTERY_DISCHARGE_1 — brine battery's ion-gradient discharge

## what

Split out of `WASTELAND_BRINE_BATTERY_CREATURE_1` (`COMMISSION_LEDGER_CLEANUP_1`,
wasteland sheet): `RUT_BrineBattery` (built,
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml`)
ships today as a plain interim pool-dweller. wasteland.md §4's actual
mechanical ask — "what lives in them runs on ion gradients and discharges
them as defense" — is not built.

## why deferred

Checked this repo's own XML for any absorbed EMP/zap/shock CompProperties
class first (per `RUT_BrineBattery.xml`'s own header) — none exists. The
roster's "EMP/zap comps exist in donor C# to borrow" claim does not hold
for the currently active mod set: the only named candidate
(`SW_Electrictick`) belongs to a dormant mod. This needs either a genuinely
new comp (a damage-on-melee-contact discharge, or an EMP-style burst on
being attacked/mined) or confirmation that a suitable comp exists somewhere
in the live mod set once checked on the Desktop with RimSage.

## scope

- A `CompProperties`-style discharge that fires when the pool owner is
  attacked or handled roughly (mining the pool it sits in is the sheet's
  own "reached into a promising pool for the wrong reason" flavor).
- Should read as a defensive shock, not a ranged attack — the creature
  itself has low MoveSpeed and no offensive tools beyond a weak "discharge"
  melee tool already on the ThingDef.

## needs

offline (design a real comp) or a Desktop RimSage check first to see
whether a usable EMP/shock comp already exists live in the active mod set.
