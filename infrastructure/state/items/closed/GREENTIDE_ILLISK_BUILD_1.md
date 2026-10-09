# GREENTIDE_ILLISK_BUILD_1 — the Illisk shoal

Child of `GREENTIDE_TERROR_REPLACEMENT_1` (owner, typed 2026-09-23: *"Illisk should be a shoal of toothy
fish (pirahnna essentially) that are crazy fast and nearly unkillable except with explosives."*).

## blocked on owner design

Not buildable without these, all listed open on the parent item:
- **One pawn or many?** The explosives counter only means something if the shoal is many bodies an area
  blast can hit.
- **How "nearly unkillable" is expressed** (armour by damage type, damage factors, regeneration) without
  reading as a bug.
- **Commonality and band** (a shoal denies water, it does not lunge).
- **Odyssey water interaction** for an effectively walled river.

NEXT: put these to the owner as one card, then build in the Greentide mod beside `RM_Vurrak`.

## built 2026-10-09 (owner card 2026-10-08)
`RM_Illisk` (Greentide `Defs/ThingDefs_Races/RM_Illisk.xml`): shoal of 6~12 tiny fast water-seeking predators, roster 1.0 in `RM_Greentide`.
Immunity = `RM_CompShoalHide` (damage scaled by damage def; Bomb whole). NOT armour: Bomb shares the Sharp category with bullets. No Harmony
(ThingWithComps.PreApplyDamage calls the comp before health). Mod Settings: `shoalHideEnabled`, `shoalNonBlastFactor` 0.04 PROVISIONAL.
Art placeholder (dhollock sprite); real art list `infrastructure/artpipe/art_lists/greentide_illisk_2026-10-09.csv`, not yet queued.

## verify
- [ ] Offline: `python3 src/RimMandrake/Greentide/validation.py` static pass (roster, hide comp, Bomb passes, water seeker).
- [ ] Live (bridge free): spawn RM_Illisk x10 on Greentide water; shoot one (damage ~nil), explode a Bomb (dies); `jawa/get_defs PawnKindDef/RM_Illisk` success true.
- [ ] Watch the crossing: does Odyssey water pathing let them reach and bite a wading colonist; tune wildGroupSize / commonality from that.
