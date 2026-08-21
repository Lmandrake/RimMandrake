## spec
**16 of the 48 authored `Jawa_*` role kinds arrive with NO weapon**, every time.
Spawned all 48 live on the full 577-mod set, read equipment back with
`jawa/pawn_get`, then re-spawned every suspect 5x to separate "always" from
"sometimes". 5/5 bare for all sixteen; `Jawa_Geonosian_Specialist` was a
one-sample fluke and is fine at 5/5 armed.
  DeepDesert: Grunt Specialist · Droid: Grunt Heavy Leader Specialist
  Empire: Grunt Heavy · Helix: Leader · Hutt: Leader
  TradeMoot: Grunt Leader Specialist · Wildsteam: Grunt Heavy Leader
🔴 THE CAUSE IS `weaponMoney`, NOT AN EMPTY TAG. The tags resolve fine —
ORDroidWeapon has 5 weapons, Jawa_IonWeapon 7, KotORBowcaster 3. RimWorld then
filters those by market value against `weaponMoney`, and **not one weapon falls
inside the range** for any of the sixteen. Off the dump (577 mods, matching the
live list, so this census is NOT provisional):
  Jawa_TradeMoot_Grunt    money  120-144   cheapest ion weapon    800
  Jawa_Wildsteam_Grunt    money  200-240   cheapest bowcaster    1250
  Jawa_Helix_Leader       money 2200-2640  cheapest legendary   12000
  Jawa_Hutt_Leader        money 2500-3000  cheapest legendary   12000
  Jawa_DeepDesert_Specialist money 300-360 only weapon           1977
Three kinds have a second defect: `Jawa_Droid_Leader`, `Jawa_Droid_Specialist`
and `Jawa_TradeMoot_Specialist` have **no `weaponTags` field at all**, and both
Droid Grunt and Heavy carry `weaponMoney 0-0`, which no weapon can ever satisfy.
⚠️ Some tagged weapons report no `MarketValue` statBase in the dump (likely
inherited from a parent the dump does not resolve), so for those the exact number
is UNMEASURED — but the live spawn is the authority and it says bare.

## verify
after the fix, re-run the 48-kind sweep; every kind returns non-empty `equipment`.

## criteria
spawn each repaired kind 5x live and read `jawa/pawn_get.equipment`. 5/5 armed,
for all 48. One sample is not enough — that is how Geonosian_Specialist got onto
the suspect list in the first place.

## notes
**from:** CHECK, 2026-08-20, found while refuting 9c02d5. Measured, not inferred.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready — 🔴 THE VALUES ARE A CONTENT CALL. Raising weaponMoney to bracket the real
weapon values is mechanical; deciding whether a Droid Grunt should carry a 5,000
silver weapon is not. Needs DECIDE or the owner.
