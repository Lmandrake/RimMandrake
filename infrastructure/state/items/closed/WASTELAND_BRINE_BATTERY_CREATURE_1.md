# WASTELAND_BRINE_BATTERY_CREATURE_1 — brine-battery pool owner, built

## what

Resolves `COMMISSION_LEDGER_CLEANUP_1` ledger slug
`wasteland:brine-battery-pool-owner-ion-gradient-discharge` — wasteland.md
§4: "The brine batteries. Hypersaline pools over mineral beds are half a
voltaic cell; what lives in them runs on ion gradients and discharges them
as defense. The pool you want to mine has an owner, and the owner is a
capacitor."

## built

`RUT_BrineBattery` (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml`)
— `TurtleLike` body, low MoveSpeed, high armor, wired into `RUT_Wasteland.xml`
wildAnimals at 0.1. See that file's own header for the full checked-donor
trail: no live EMP/zap comp exists anywhere in this repo's own XML to
borrow (the roster's "comps exist in donor C#" claim doesn't hold for the
active mod set — `SW_Electrictick`, the only named candidate, is both cast
elsewhere (`RUT_Scarlands`) and its owning mod is dormant), so this ships
as a plain interim pool-dweller.

## split out

The actual ion-gradient discharge-as-defense mechanic is genuinely new C#
(no donor to borrow), filed separately as `WASTELAND_BRINE_BATTERY_DISCHARGE_1`.

## art

Three facing jobs filed and queued (south/east/north) after a first attempt
(`rutbrinebattery_v1_*`) was refused by the artpipe daemon for using
camera-angle language ("viewed from directly above") instead of naming the
visible surface per facing — refiled as `rutbrinebattery_v2_*` with corrected
front/side/rear-view phrasing.
