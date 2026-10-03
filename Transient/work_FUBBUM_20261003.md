# FUBBUM 2026-10-03 (started)

## Choices (GELATINOUSSLIME_FUBBUM_HUNTER_1)
- Census: no fubbum in src/ or artpipe (find fubbum: 0). Item's "reuse night pooling" has nothing to reuse: no pooling code in the mod; RM_Gelatid is plain herdAnimal. Hunt = vanilla predator AI; "night pooling" is flavour only. No new behaviour C#.
- Defs/ThingDefs_Races/Fubbum.xml: RM_Fubbum (QuadrupedAnimalWithPaws, bs 0.9, speed 3.6, predator true, maxPreyBodySize 0.6 > gelatid 0.55, < colonist 1.0; manhunter chances 0; SlimeResistantExtension; no flight stats) + PawnKindDef (ecoW 0.8, combatPower 60). All // INVENTED. Vanilla "prey list" is the size ceiling; caveat: small humanlike children under 0.6 are not excluded by that rule (unverified).
- Biome: RM_Fubbum 0.15 inline on wildAnimals.
- Settings: fubbumHunts (default true, checkbox) -> Source/FubbumHunting.cs (new, in csproj) sets race.predator at startup and on WriteSettings. validation.py FIELDS/settings_flip + northstar_mock gain it.
- Validation: new component fubbum_hunter_def (predator, prey ceiling bracket, manhunter 0); unreadable fields -> _unmeasured. Selftest ran (see reply).
- Art: 3 jobs queued from the turn1 CSV row; texPath Things/Pawn/Animal/Fubbum/RM_Fubbum magenta until generated (3 validate_patch texPath WARNs, 0 errors).
- Build: winbuild GelatinousSlime ok.
