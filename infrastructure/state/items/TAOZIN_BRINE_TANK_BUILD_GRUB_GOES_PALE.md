# TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE

Follow-up of TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO (design: `design/RimStarWars/taozin_split_proposal_2026-10-17.md`).

## spec
1. A brine tank building (SWBestiary or Cuisine) that holds one tamed `RSW_TaozinGrub` (pawn holder, like a
   vanilla cryptosleep casket / Biotech growth vat holder) and consumes `RM_Brine` (Stillsand) to produce
   `RSW_TaozinBrine` (Cuisine, already built) over time. No such mechanism exists in `src/` (searched 2026-10-17:
   brine tank / vivarium / aquarium / terrarium / animal-container: none).
2. Owner colour ruling: a grub kept in brine "for a long period" turns white. Track cumulative brine days per grub
   (a ThingComp on the grub) and switch its body graphic to the white look past a threshold (white art queued as
   its own artpipe job).
3. Mod Settings: on/off for the tank and for the nest genstep (`RM_MechanicGates.Register` on the nest
   GenStepDef's gate key; `RSW_TaozinNest.xml` is not gated today).

## verify
Tank holds a grub, brine in → taozin brine out in game; a grub past the threshold renders white; both switches work.
