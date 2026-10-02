# LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §1 (finding 1) and §4 row 0. Ruled by `design/RimMandrake/biome_mod_architecture.md` §7 Q12.

1. Port the eight invented residents (drinker `RSW_BloodropMoth`, glowbulb `RSW_GlowSlug`, grabber `RSW_BovineBeetle`, soulchime `RSW_FacetMothLarvae`, gembug, megapleura, moss grub, shatterjaw) to `RM_` race and kind defs, wired inline in `RM_LanternDeeps`'s `<wildAnimals>` at today's commonalities, carrying their regen art, labels, descriptions and the `DEEPS_FAUNA_MECHANICS_1/_2` comps.
2. Repoint `MapComponent_LanternDeepDarkness.DeepPredatorKindNames` at the `RM_` drinker and shatterjaw so light draws predators on the free tier.
3. Remove the moved rows (and the two pack-animal rows) from `WildAnimals_LanternDeeps.xml`.

Not here: the glowbulb's second home in the Fever Wood is that biome's sitting row (Q13 shape), not an eviction. This item goes first: the twelve and the darkness mechanic wire against these names.

## verify
- Free tier alone (no SWBestiary): `RM_LanternDeeps` spawns the eight; sustained light draws a drinker or shatterjaw.
- No `RSW_` row left targeting `RM_LanternDeeps`.
