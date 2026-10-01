# STILLSAND_GLARE_BLIND_GOGGLES_1 — glare-blind and sun goggles

Split from `STILLSAND_SUN_FROM_LATITUDE_1` (its spec items 6, 7, verbatim below). Design source and owner rulings are cited on the parent.

Built already by the parent (`STILLSAND_SUN_FROM_LATITUDE_1`): the pinned sky on `RM_Stillsand`, the 85° clamp, the heat kind resolved from sun elevation (`RM_SunHeatExtension.overheadAboveElevationDegrees`, `RM_MapComponent_ShadeGrid.EffectiveHeatKind` / `SunElevationDegrees`), heat by sin(elevation) and the sand glare floor, in `mandrake.rm.creaturebehaviors`. Read the map's sun elevation from `RM_MapComponent_ShadeGrid.SunElevationDegrees`; never re-derive it.

## spec

6. **Glare-blind, race-gated (slate IN).** Owner, typed: *"the sun protection for the eyes is great
   for races that need it, but the Jawa won't need it, but the slaves might"*. Unprotected
   humanlike eyes in full glare slowly take a sight debuff (a hediff on vanilla `Sight`).
   **Immunity is a gene, never a defName list:** a new `RM_GlareAdapted` GeneDef (RM tier) grants
   it, and an RSW patch adds it to the Jawa xenotype (`RSW_RimMandrakeJawa`). Every other race
   or xenotype, slaves included, is affected unless it wears eye protection. Animals are out of
   scope.
7. **Sun goggles.** `RM_SunGoggles`, an eyes-layer apparel that cancels glare-blind. Made from
   `RM_Biosilica` (exists today) at a crafting spot, and from sun glass once
   `STILLSAND_GLASS_LENS_CHAIN_1` lands. Existing goggle headgear in the Armoury (Bothan, light-scan,
   pao hat) also cancels it by a patch-added tag, so nobody has to re-buy what they wear.

Add its Mod Settings toggle (parent item 11) in the owning mod.

## criteria

- A Jawa colonist never gets glare-blind; a non-Jawa slave in full glare does, and goggles clear it.
