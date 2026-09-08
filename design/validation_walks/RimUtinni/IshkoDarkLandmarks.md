# IshkoDarkLandmarks — validation walk
subject: src/RimUtinni/IshkoDarkLandmarks  (packageId: mandrake.rut.ishkolandmarks)
deps: Ludeon.RimWorld.Odyssey (modDependencies + loadAfter, DLC — LandmarkDef is `MayRequire`-gated on it); mandrake.rut.ashkarrlandmarkart (loadAfter, supplies the icon textures these defs reference)
list: minimal+Ludeon.RimWorld.Odyssey+mandrake.rut.ashkarrlandmarkart
status-hint: Three new Odyssey LandmarkDefs for Ishko the Unmaskable — Lightless Sink, Shadowed Overhang, Cold Lava Tube — each anchored on a real TileMutatorDef (Hollow/Chasm/Cavern respectively); placement on the actual planet is deliberately left to the owner.

## must be true

- Three LandmarkDefs exist: `RUT_LightlessSink`, `RUT_ShadowedOverhang`, `RUT_ColdLavaTube`, each `MayRequire="Ludeon.RimWorld.Odyssey"`.
- Each has `category=mountain` and a nonzero `commonality` (0.08, 0.08, 0.06 respectively).
- Each `mutatorChances` block carries exactly one `Required="True"` anchor mutator matching its own TileMutatorDef: `Hollow` for the Sink, `Chasm` for the Overhang, `Cavern` for the Lava Tube.
- Each `iconTexturePath` (`World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, `.../Cavern`) is supplied by `mandrake.rut.ashkarrlandmarkart`, not left pointing at nothing.
- None of the three new defNames collides with an existing curated LandmarkDef, and none is placed anywhere on the live planet yet — placement is out of scope for this mod.

## the walk

1. [L] Player.log after load contains no `Config error in mandrake.rut.ishkolandmarks` and no XML error naming `LandmarkDefs_IshkoDark.xml`; also no "could not load texture" / missing-texture warning naming `World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, or `.../Cavern`
2. [D] def read-back: LandmarkDef `RUT_LightlessSink` exists; category=mountain; commonality=0.08; mutatorChances contains Hollow Required=True
3. [D] def read-back: LandmarkDef `RUT_ShadowedOverhang` exists; category=mountain; commonality=0.08; mutatorChances contains Chasm Required=True
4. [D] def read-back: LandmarkDef `RUT_ColdLavaTube` exists; category=mountain; commonality=0.06; mutatorChances contains Cavern Required=True
5. [B] jawa/get_defs {defType: "LandmarkDef", fields: ["commonality", "category", "iconTexturePath", "mutatorChances"]} filtered to the 3 RUT_ defNames → confirms the RESOLVED defs (Odyssey active, no ConfigError) match steps 2-4, and each `iconTexturePath` is non-empty
6. [B] jawa/world_landmarks_get → none of `RUT_LightlessSink`, `RUT_ShadowedOverhang`, `RUT_ColdLavaTube` appears among the planet's currently-placed landmarks (count=0 each) — confirms placement genuinely was not done here
7. [S] (human pass) once the owner places one of the three, confirm its icon (the reused Ash'karr-styled Hollow/Chasm/Cavern art) reads correctly in the landmark legend and tooltip
