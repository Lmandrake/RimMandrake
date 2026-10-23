# Rites — validation walk
subject: src/RimUtinni/Rites  (packageId `mandrake.rut.rites`)
deps: mandrake.rut.antiquities (own tier, hard modDependency + loadAfter); Ludeon.RimWorld.Odyssey (Ishko's LandmarkDefs are `MayRequire`-gated on it); mandrake.rut.ashkarrlandmarkart (modDependency + loadAfter, supplies the landmark icons)
list: the `rites` tier (minimal+mandrake.rm.gimmesomeslack+mandrake.rut.antiquities+mandrake.rut.ashkarrlandmarkart)
status-hint: the liturgy research tree — five ResearchProjectDefs chained T0..T4, each tier past the Scrap Shrine gated by a hiddenPrerequisites on an Antiquities stage (visible-locked, not hidden from the tree); plus Ishko's three landmarks (section below).

## must be true
- ResearchTabDef `RUT_Rites` exists, label "the rites".
- Five ResearchProjectDefs chained: RUT_Rites_ScrapShrine (baseCost 400, techLevel Neolithic, no prerequisites) → RUT_Rites_ConduitChoir (1200, Industrial, prereq ScrapShrine, hiddenPrereq RUT_Antiq_Language) → RUT_Rites_GodSpeakerArray (2600, Industrial, prereq ConduitChoir, hiddenPrereq RUT_Antiq_Religion) → RUT_Rites_HullLiturgy (4000, Spacer, prereq GodSpeakerArray, hiddenPrereq RUT_Antiq_Culture) → RUT_Rites_GodsSpeakBack (8000, Ultra, prereq HullLiturgy, hiddenPrereq RUT_Antiq_Voice).
- All five sit on tab RUT_Rites.
- A tier whose hiddenPrerequisite stage is unfinished cannot be started (CanStartNow false) even once its ordinary `prerequisites` are complete — but it still renders in the research tree (greyed), never disappears from VisibleResearchProjects.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.rites"
2. [D] def read-back: ResearchTabDef RUT_Rites exists; label = "the rites"
3. [D] def read-back: ResearchProjectDef RUT_Rites_ScrapShrine — baseCost=400, techLevel=Neolithic, tab=RUT_Rites, no prerequisites
4. [D] def read-back: ResearchProjectDef RUT_Rites_ConduitChoir — baseCost=1200, techLevel=Industrial, prerequisites=[RUT_Rites_ScrapShrine], hiddenPrerequisites=[RUT_Antiq_Language]
5. [D] def read-back: ResearchProjectDef RUT_Rites_GodsSpeakBack — baseCost=8000, techLevel=Ultra, prerequisites=[RUT_Rites_HullLiturgy], hiddenPrerequisites=[RUT_Antiq_Voice]
6. [B] jawa/research_availability {project: "RUT_Rites_ConduitChoir"} before RUT_Antiq_Language finishes → prerequisitesCompleted true (ScrapShrine done) but canStartNow false, unfinished list names RUT_Antiq_Language
7. [B] jawa/research_finish_project {project: "RUT_Antiq_Language"} then jawa/research_availability {project: "RUT_Rites_ConduitChoir"} → canStartNow now true
X. [S] (human pass) confirm a locked-but-visible rite renders greyed in the research tree UI rather than vanishing

## Ishko's landmarks

Three Odyssey LandmarkDefs for Ishko the Unmaskable (Lightless Sink, Shadowed Overhang, Cold Lava Tube), each on a real TileMutatorDef (Hollow, Chasm, Cavern). Their names are principles of his doctrine, not promises about the ground (owner, 2026-10-22). They were their own mod, `mandrake.rut.ishkolandmarks`, until 2026-10-22 (owner: *"It's a concept, not a mod."*; *"I think the Nine Gods belong in Salvation Rites."*); defNames unchanged. Placing them on the planet is the owner's hand; the suite places and removes them only on a throwaway test world. The old mod's 2026-10-07 live GREEN is at a retired package and an old hash: these chains need a fresh `rites` sitting. <!-- walklint-ok: names the retired packageId as history -->

### must be true

Every line is sourced from `Defs/RUT_IshkoLandmarks.xml` or `About/About.xml`. `→ chain.component` is the covering check in `src/RimUtinni/Rites/validation.py`; `→ UNCOVERED: why` is a named boundary. Agent-owned, not hashed.

- Three LandmarkDefs exist: `RUT_LightlessSink`, `RUT_ShadowedOverhang`, `RUT_ColdLavaTube`, each `MayRequire="Ludeon.RimWorld.Odyssey"`. → ishko_source.defs_gated_on_odyssey, ishko_defs.RUT_LightlessSink_resolves, ishko_defs.RUT_ShadowedOverhang_resolves, ishko_defs.RUT_ColdLavaTube_resolves
- Each has `category=mountain` and a nonzero `commonality` (0.08, 0.08, 0.06 respectively). → ishko_defs.RUT_LightlessSink_resolves, ishko_defs.RUT_ShadowedOverhang_resolves, ishko_defs.RUT_ColdLavaTube_resolves
- Each `mutatorChances` block carries exactly one `Required="True"` anchor mutator matching its own TileMutatorDef: `Hollow` for the Sink, `Chasm` for the Overhang, `Cavern` for the Lava Tube. → ishko_defs.RUT_LightlessSink_resolves, ishko_defs.RUT_ShadowedOverhang_resolves, ishko_defs.RUT_ColdLavaTube_resolves
- Placing one on a world tile (the owner's act on the real save) gives that tile our landmark AND its Required anchor mutator. → ishko_placement.RUT_LightlessSink_places_with_anchor, ishko_placement.RUT_ShadowedOverhang_places_with_anchor, ishko_placement.RUT_ColdLavaTube_places_with_anchor
- Each `iconTexturePath` (`World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, `.../Cavern`) is supplied by `mandrake.rut.ashkarrlandmarkart`, not left pointing at nothing. → ishko_source.icons_supplied_by_art_mod; the icon RENDERING in the legend/tooltip → UNCOVERED: visual boundary (debug_process.md §4), and no bridge tool reads `LandmarkDef.Icon` through ContentFinder (`jawa/texture_audit` sweeps ThingDefs only)
- None of the three defNames collides with an existing LandmarkDef: each resolves from `mandrake.rut.rites`. → ishko_defs.RUT_LightlessSink_resolves, ishko_defs.RUT_ShadowedOverhang_resolves, ishko_defs.RUT_ColdLavaTube_resolves

### anti-guessing notes

- RULED OUT: "none of the three is placed on the planet" as a bar. The old `not_placed_on_planet.no_ishko_landmark_placed_yet` read `row["defName"]` from `jawa/world_landmarks_get`, whose rows carry `def` (JawaBenchWorldTools.cs `WorldLandmarksGet`), so it passed whatever the planet held. And a quicktest world is generated: worldgen places LandmarkDefs by commonality (ours 0.06-0.08), so absence is not even true by design there. Placement is the owner's hand on the Ash'karr save, not a property of the mod.
- RULED OUT: `jawa/get_defs` without `deep=true` can show the anchor. `LandmarkDef.mutatorChances` is `List<MutatorChance>` (fields `mutator`, `chance`, `required`; decompiled 1.6), a non-Def object list, which comes back as bare type names unless `deep=true`. The old substring check for `Hollow` could not have passed live. Guard: the mock's `shallow` break reads UNMEASURED, never PASS.
- RULED OUT: placement could leave the anchor to chance. `WorldLandmarks.AddLandmark` adds a mutatorChance when `Rand.Chance(chance) && ((required && forced) || mutator.IsValidTile(..))`, and a `Required` entry has chance 1, so with `forced=true` the anchor is certain; a missing anchor after a forced add is a real defect.

### the walk
I1. [L] Player.log after load contains no `Config error in mandrake.rut.rites` and no XML error naming `RUT_IshkoLandmarks.xml`; also no "could not load texture" / missing-texture warning naming `World/Landmarks/Ashkarr/Hollow`, `.../Chasm`, or `.../Cavern`
I2. [D] def read-back: LandmarkDef `RUT_LightlessSink` exists; category=mountain; commonality=0.08; mutatorChances contains Hollow Required=True
I3. [D] def read-back: LandmarkDef `RUT_ShadowedOverhang` exists; category=mountain; commonality=0.08; mutatorChances contains Chasm Required=True
I4. [D] def read-back: LandmarkDef `RUT_ColdLavaTube` exists; category=mountain; commonality=0.06; mutatorChances contains Cavern Required=True
I5. [B] jawa/get_defs {defs: "LandmarkDef/<name>", fields: "category,commonality,mutatorChances,iconTexturePath", deep: true} for each of the 3 RUT_ defNames → confirms the RESOLVED defs (Odyssey active, no ConfigError) match steps 2-4, and each `iconTexturePath` is non-empty
I6. [B] jawa/world_mutators_get over tiles 0-1999 → three land tiles with no landmark; for each Ishko def, `jawa/world_landmarks_set {action:add, def, tiles, forced:true, checkValid:true}` → expect `added`=1 and the tile read back carrying the def AND its Required anchor mutator (Hollow/Chasm/Cavern); then remove the landmark (and the anchor mutator if the tile did not already have it)
I7. [S] (human pass) once the owner places one of the three, confirm its icon (the reused Ash'karr-styled Hollow/Chasm/Cavern art) reads correctly in the landmark legend and tooltip
