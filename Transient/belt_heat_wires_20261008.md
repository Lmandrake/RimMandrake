# BELT: heat + ticker + wires — 2026-10-08

## 1 TICKER_NEVER_FIRES_FIX_1
DONE 40553e46e (+prose 9244333c0). Lint 0. implemented, owes A1-A5 L1. Selftests 340/343: FeverWood settings check red from FV-1 (b20a31ffc), not this change.

## 2 WETBULB_FOLD_INTO_HEAT_1
DONE 6e6a23f38 (code) + 3c2dcb420 (docs, item prose). Wet-bulb condition/hediff/stat/DryRooms deleted; Greentide ambient offset 8->12 C (landed inside the parent window commit ab5528e34); gear via StuffEffectMultiplierInsulation_Heat 1.4/0.8/0.5; AI scorer Insulation_Heat/40; saved hediff aliases to Heatstroke. Selftests green. implemented, owes A2-A4 L2 + H1 L4. Open: blower still pushes heat into the room.

## 3 FALLEN_WIRE_SHOCK_1
DONE 6d208adca. Shock = knockback (2 cells) + RM_FallenWireShock knock-out (~2 h); weak heart (HeartArteryBlockage / HeartAttack / damaged natural heart) -> vanilla HeartAttack at lethal severity. Ignite: vanilla Filth_Fuel + FlowWorks IgniteNow by reflection, 35%/sweep. Settings: shock, knockback, ignite. implemented, owes A1 L1, A2-A5 L2, H1 L4. Selftests: 2 unrelated reds (FlowWorks northstar settings table missing liquidHeatPush*, placeholder allowlist stale after art installs).
