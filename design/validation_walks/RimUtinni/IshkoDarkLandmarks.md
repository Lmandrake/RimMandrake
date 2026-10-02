# IshkoDarkLandmarks — validation walk
subject: src/RimUtinni/IshkoDarkLandmarks  (packageId: mandrake.rut.ishkolandmarks)
deps: Ludeon.RimWorld.Odyssey (modDependencies + loadAfter, DLC — LandmarkDef is `MayRequire`-gated on it); mandrake.rut.ashkarrlandmarkart (loadAfter, supplies the icon textures these defs reference)
list: minimal+Ludeon.RimWorld.Odyssey+mandrake.rut.ashkarrlandmarkart
status-hint: Three new Odyssey LandmarkDefs for Ishko the Unmaskable — Lightless Sink, Shadowed Overhang, Cold Lava Tube — each anchored on a real TileMutatorDef (Hollow/Chasm/Cavern respectively); placement on the actual planet is deliberately left to the owner (the suite places and removes them only on a throwaway test world).

## must be true

Every line is sourced from `Defs/LandmarkDefs_IshkoDark.xml` or `About/About.xml`. `→ chain.component` is the covering check in `src/RimUtinni/IshkoDarkLandmarks/validation.py`; `→ UNCOVERED: why` is a named boundary. Agent-owned, not hashed.

- Three LandmarkDefs exist: `RUT_LightlessSink`, `RUT_ShadowedOverhang`, `RUT_ColdLavaTube`, each `MayRequire="Ludeon.RimWorld.Odyssey"`. → source.defs_gated_on_odyssey, defs.RUT_LightlessSink_resolves, defs.RUT_ShadowedOverhang_resolves, defs.RUT_ColdLavaTube_resolves
- Each has `category=mountain` and a nonzero `commonality` (0.08, 0.08, 0.06 respectively). → defs.RUT_LightlessSink_resolves, defs.RUT_ShadowedOverhang_resolves, defs.RUT_ColdLavaTube_resolves
- Each `mutatorChances` block carries exactly one `Required="True"` anchor mutator matching its own TileMutatorDef: `Hollow` for the Sink, `Chasm` for the Overhang, `Cavern` for the Lava Tube. → defs.RUT_LightlessSink_resolves, defs.RUT_ShadowedOverhang_resolves, defs.RUT_ColdLavaTube_resolves
- Placing one on a world tile (the owner's act on the real save) gives that tile our landmark AND its Required anchor mutator. → placement.RUT_LightlessSink_places_with_anchor, placement.RUT_ShadowedOverhang_places_with_anchor, placement.RUT_ColdLavaTube_places_with_anchor
- Each `iconTexturePath` (`World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, `.../Cavern`) is supplied by `mandrake.rut.ashkarrlandmarkart`, not left pointing at nothing. → source.icons_supplied_by_art_mod; the icon RENDERING in the legend/tooltip → UNCOVERED: visual boundary (debug_process.md §4), and no bridge tool reads `LandmarkDef.Icon` through ContentFinder (`jawa/texture_audit` sweeps ThingDefs only)
- None of the three defNames collides with an existing LandmarkDef: each resolves from `mandrake.rut.ishkolandmarks`. → defs.RUT_LightlessSink_resolves, defs.RUT_ShadowedOverhang_resolves, defs.RUT_ColdLavaTube_resolves

## anti-guessing notes

- RULED OUT: "none of the three is placed on the planet" as a bar. The old `not_placed_on_planet.no_ishko_landmark_placed_yet` read `row["defName"]` from `jawa/world_landmarks_get`, whose rows carry `def` (JawaBenchWorldTools.cs `WorldLandmarksGet`), so it passed whatever the planet held. And a quicktest world is generated: worldgen places LandmarkDefs by commonality (ours 0.06-0.08), so absence is not even true by design there. Placement is the owner's hand on the Ash'karr save, not a property of the mod.
- RULED OUT: `jawa/get_defs` without `deep=true` can show the anchor. `LandmarkDef.mutatorChances` is `List<MutatorChance>` (fields `mutator`, `chance`, `required`; decompiled 1.6), a non-Def object list, which comes back as bare type names unless `deep=true`. The old substring check for `Hollow` could not have passed live. Guard: the mock's `shallow` break reads UNMEASURED, never PASS.
- RULED OUT: placement could leave the anchor to chance. `WorldLandmarks.AddLandmark` adds a mutatorChance when `Rand.Chance(chance) && ((required && forced) || mutator.IsValidTile(..))`, and a `Required` entry has chance 1, so with `forced=true` the anchor is certain; a missing anchor after a forced add is a real defect.

## the walk

1. [L] Player.log after load contains no `Config error in mandrake.rut.ishkolandmarks` and no XML error naming `LandmarkDefs_IshkoDark.xml`; also no "could not load texture" / missing-texture warning naming `World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, or `.../Cavern`
2. [D] def read-back: LandmarkDef `RUT_LightlessSink` exists; category=mountain; commonality=0.08; mutatorChances contains Hollow Required=True
3. [D] def read-back: LandmarkDef `RUT_ShadowedOverhang` exists; category=mountain; commonality=0.08; mutatorChances contains Chasm Required=True
4. [D] def read-back: LandmarkDef `RUT_ColdLavaTube` exists; category=mountain; commonality=0.06; mutatorChances contains Cavern Required=True
5. [B] jawa/get_defs {defs: "LandmarkDef/<name>", fields: "category,commonality,mutatorChances,iconTexturePath", deep: true} for each of the 3 RUT_ defNames → confirms the RESOLVED defs (Odyssey active, no ConfigError) match steps 2-4, and each `iconTexturePath` is non-empty
6. [B] jawa/world_mutators_get over tiles 0-1999 → three land tiles with no landmark; for each Ishko def, `jawa/world_landmarks_set {action:add, def, tiles, forced:true, checkValid:true}` → expect `added`=1 and the tile read back carrying the def AND its Required anchor mutator (Hollow/Chasm/Cavern); then remove the landmark (and the anchor mutator if the tile did not already have it)
7. [S] (human pass) once the owner places one of the three, confirm its icon (the reused Ash'karr-styled Hollow/Chasm/Cavern art) reads correctly in the landmark legend and tooltip
