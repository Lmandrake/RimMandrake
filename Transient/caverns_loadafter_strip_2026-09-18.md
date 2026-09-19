# CAVERNS_LOADAFTER_STRIP_1 — 2026-09-18

## About.xml edits
14 files edited — one `<li>` (case as found) removed from a loadAfter/forceLoadAfter list, files otherwise byte-identical, all re-parsed OK:
- src/RimMandrake/MandrakePatches/About/About.xml (loadAfter)
- src/RimStarWars/Armoury/About/About.xml (loadAfter)
- src/RimUtinni/Doctrine/About/About.xml (loadAfter)
- src/RimUtinni/FungalSoilTrade/About/About.xml (loadAfter)
- src/RimUtinni/PawnFlavor/About/About.xml (loadAfter)
- src/RimUtinni/ResearchRetag/About/About.xml (forceLoadAfter — not one of the 4 named tags but same category; included)
- src/RimUtinni/RotSporeKit/About/About.xml (loadAfter)
- src/RimUtinni/UtinniPatches/About/About.xml (loadAfter)
- src/RimUtinni/AaroxisDendoriaArtOverride/About/About.xml (loadAfter, now empty block)
- src/RimUtinni/BovineBeetleArtOverride/About/About.xml (loadAfter, now empty block)
- src/RimUtinni/CrestedDragonArtOverride/About/About.xml (loadAfter, now empty block)
- src/RimUtinni/FoundryBeetleArtOverride/About/About.xml (loadAfter, now empty block)
- src/RimUtinni/FungalMantisArtOverride/About/About.xml (loadAfter, now empty block)
- src/RimUtinni/PuffmiteArtOverride/About/About.xml (loadAfter, now empty block)

SKIPPED (per instruction, another worker owns it): src/RimUtinni/LanternDeeps/About/About.xml line 28, `<li>BiomesTeam.BiomesCaverns</li>` inside `<loadAfter>`, with an existing comment above it: "CAVERNS_PARITY_BUILD_1: the donor is on the cut path; this entry only orders us after it while it is still installed. Nothing here references it." Not edited.

Not in scope (mentions Caverns only in description prose, no loadAfter/li reference): src/RimStarWars/SWBestiary/About/About.xml line 28 — not edited, not a guard.

Inert guards found (NOT edited, listed for a separate decision) — all in src/RimUtinni/UtinniPatches:
- Defs/BiomeDefs/RUT_CrackedLands.xml:153 `<BMT_Rocktooth MayRequire="biomesteam.biomescaverns">1</BMT_Rocktooth>`
- Defs/BiomeDefs/RUT_CrackedLands.xml:154 `<BMT_Boneblade MayRequire="biomesteam.biomescaverns">1</BMT_Boneblade>`
- Defs/BiomeDefs/RUT_Greentide.xml:223 `<BMT_GiantLeaf MayRequire="biomesteam.biomescaverns">1.0</BMT_GiantLeaf>`
- Patches/BiomeCast_Ashkarr.xml:1070 `PatchOperationConditional MayRequire="sarg.alphabiomes,biomesteam.biomescaverns"`
- Patches/BiomeCast_Ashkarr.xml:1124 `PatchOperationConditional MayRequire="biomesteam.biomescaverns"`
- Patches/BiomeCast_Ashkarr.xml:1178 `PatchOperationConditional MayRequire="mlie.advancedbiomes,biomesteam.biomescaverns"`

## Deploy
Applied (12 mods, plan touched only the edited About.xml + pre-existing unrelated holds/drift):
MandrakePatches, Doctrine, FungalSoilTrade, ResearchRetag, RotSporeKit, UtinniPatches,
AaroxisDendoriaArtOverride, BovineBeetleArtOverride, CrestedDragonArtOverride,
FoundryBeetleArtOverride, FungalMantisArtOverride, PuffmiteArtOverride — all "VERIFIED in sync".

Held (NOT applied — plan touched other undeployed files, a peer's work):
- Armoury: plan also lists new/changed files unrelated to this edit — `+ Defs/ThingDefs/RSW_DesertWraps.xml` and 11 DesertWraps texture PNGs, `~ Defs/Absorbed_KotorWeapons/Absorbed_KotorWeapons_BLOCKED_manifest.txt`, `~ Defs/Absorbed_KotorWeapons/ThingDefs_Apparel/Absorbed_KotorWeapons_Apparel_ImmortalusSithLords.xml`, `~ Defs/ThingDefs/Absorbed_OPTurret.xml`.
- PawnFlavor: plan also lists `~ Patches/PawnFlavorPhase2_ThoughtDef.xml` and `~ Patches/PawnFlavorPhase2_Xenotype.xml`.

## Art-override mods
Six mods exist (all named ones found): AaroxisDendoriaArtOverride, BovineBeetleArtOverride, CrestedDragonArtOverride, FoundryBeetleArtOverride, FungalMantisArtOverride, PuffmiteArtOverride (targets BMT_FleeceSpider). Each ships loose PNGs only, no Defs/Patches (Puffmite also has one label-text Patch), all at the donor's own texPath e.g. `BMT_Caverns/Things/Animal/AaroxisDendoria/AaroxisDendoria_<facing>` — designed to win the donor's own def art by later load order.

Key finding: all six donor creatures ARE already ported into `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/` as RSW_AaroxisDendoria, RSW_BovineBeetle, RSW_CrestedDragon, RSW_FoundryBeetle, RSW_FungalMantis, RSW_FleeceSpider — but the port's ThingDefs declare a DIFFERENT texPath prefix, `swanimals/BiomesTeam/BMT_Caverns/Things/Animal/<Name>/...`, backed by SWBestiary's own copied PNGs at `Textures/swanimals/BiomesTeam/BMT_Caverns/Things/Animal/<Name>/`. That is a distinct file path from the override mods' `BMT_Caverns/Things/Animal/<Name>/...` (no "swanimals/" prefix), so the override art never reached the port even while Caverns was still active — it only ever won the donor's own (now-gone) ThingDef.

Verdicts:
- AaroxisDendoriaArtOverride: DEAD — targets only the donor's own def; RSW_AaroxisDendoria port uses a different texPath, unaffected.
- BovineBeetleArtOverride: DEAD — same reasoning; RSW_BovineBeetle port texPath differs.
- CrestedDragonArtOverride: DEAD — same reasoning; RSW_CrestedDragon port texPath differs.
- FoundryBeetleArtOverride: DEAD — same reasoning; RSW_FoundryBeetle port texPath differs.
- FungalMantisArtOverride: DEAD — same reasoning; RSW_FungalMantis port texPath differs (RotSporeKit explicitly did NOT ingest the fauna, only the claw item name).
- PuffmiteArtOverride: DEAD — same reasoning; RSW_FleeceSpider port texPath differs; its label-text Patch also targets the donor's own def, not ours.

## Open
- Armoury and PawnFlavor About.xml edits are made but UNDEPLOYED — held because their deploy plans carry other undeployed peer work (see Deploy section above). Re-run `deploy_custom_mods.py --mod Armoury` / `--mod PawnFlavor` once that other work is deployed or explicitly excluded.
- Six inert MayRequire/PatchOperationConditional guards in UtinniPatches (listed above) still name `biomesteam.biomescaverns` — left untouched pending a separate decision on whether to strip them now that the mod is retired for good.
- src/RimUtinni/LanternDeeps/About/About.xml:28 still names BiomesTeam.BiomesCaverns in loadAfter — owned by another worker, not touched.
- All six art-override mods verdicted DEAD; nothing deleted (read-only per instructions).
