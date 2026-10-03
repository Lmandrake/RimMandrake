# SCALD_RETURN_GALLERY_1 work log 2026-10-03
Item has no prose; criteria = title + sitting row 4 (the_scald_floor_sitting_agenda_2026-10-02.md) + GPT consult section 4 (the_scald_floor_gpt_consult_2026-10-02.md).
Sitting Q3 (c) = vent fields AND Return Gallery. Mod folder: src/RimMandrake/DivingInteraction (new files + csproj + settings). No Chill files touched.

## Design (deterministic circuit, no hidden-switch matching)
- Hub RM_ReturnGalleryHub (3x3) + 5 branch pipes with outlets (RM_GalleryOutlet) laid on the floor by GenStep_ScaldReturnGallery (order 875, listed on RM_SeaDiveGenerator_TheScald only, same scoping as the vent step).
- Branch roles shuffled per map: 1 true Return (intact, warm, outward), 1 Feed (intact, cold, inward), 2 Broken (burst piece visible at segment k, pressure 0 beyond), 1 Silted (warm, outward, pipes buried beyond k, pressure 20%) = the decoy.
- Evidence on every branch: a colonist probes an outlet (work giver, 600 ticks, any colonist) -> gauge reading (pressure by segment, temperature, flow direction). The physical break/gap sits at the segment the gauge names, so the reading can be checked on foot.
- Solve: hub gizmo "Mark return branch" (only once all 5 are probed) -> pick one. Correct = the warm, outward, FULL-pressure branch: locker releases the rewards. Wrong = latch jams 15000 ticks (a day); readings unchanged; nothing else happens (wasted time only, no catastrophe, never touches anything live).
- Never touches the live trunk, the boil, or any ship system.
## Choices
- No separate "portable diagnostic pump" item: the pump is implicit in the probe job (any colonist, no skill gate). A craftable pump would be an invented recipe; left out, recorded here.
- Rewards: RM_ImmersionSchematic + RM_CathedralHeatLog items. What the schematic UNLOCKS (research/recipe) is an owner/design decision -> blocked part, see item note.
- Toggle: RM_DivingSettings.scaldReturnGalleryEnabled (worldgen-affecting; existing floors keep theirs).
- Placeholder art = vanilla textures; artpipe searched (only unrelated coolant eel hits).

## Result
winbuild DivingInteraction BUILT 0 err (3 new .cs in csproj). validate_patch: only errors are Core ParentName (BuildingBase/ResourceBase) unresolvable because Core is not under --defs (same as RM_SeaDiveHatch); texPath warnings = vanilla bundle paths. validation.py chain scald_return_gallery added (parse-checked, no live run).
Art: hub art queued scald_return_gallery_hub_v1 (Transient/gallery_art.json); other pieces stay tinted placeholders.
Blocked part: schematic unlock -> filed + blocked SCALD_GALLERY_SCHEMATIC_UNLOCK_1 (owner). SCALD_RETURN_GALLERY_1 left in 'doing' (not closed: no commit by me, live run owed).
Owed/unproven live: site found on a real floor map, gizmo shows on a neutral building, probe job, wrong-mark jam. Step is on the hatch Scald generator only (RM_SeabedLayer has no floor generator yet, same as vents).
