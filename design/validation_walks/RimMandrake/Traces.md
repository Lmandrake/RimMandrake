# Traces — validation walk
subject: src/RimMandrake/Traces  (packageId mandrake.rm.traces)
deps: none at step 0 (step 1+ depends on mandrake.rm.creaturebehaviors for the TrackGrid)
list: minimal+traces
status-hint: STEP 0 SPIKE — two placeholder filth defs, no C#; design/RimMandrake/event_trace_props_library_design_2026-10-03.md §8 is the build plan.

## must be true
- A filth spawns on a cell whose edifice is a wall (design §2.2 UNMEASURED 1)          → spike.wall_spike_spawns_on_a_wall_cell
- The spike defs resolve and a floor trace spawns (control)                            → spike.floor_spike_spawns
- A wall-cell trace draws above the wall mesh (design §2.2 UNMEASURED 2)               → UNCOVERED: a screenshot is taken; judging it is a viewer's call (§4 boundary)
- A directed trace keeps its heading through save/load                                 → UNCOVERED: needs RM_TraceUtility (step 1)
- A fresh trace becomes its aged def after ageAfterDays                                → UNCOVERED: needs RM_MapComponent_TraceAging (step 1)
- A blaster hit on a wall leaves RM_Trace_BoltScar on the hit face                     → UNCOVERED: step 4 hook not built
- A miss leaves a floor bolt pit                                                       → UNCOVERED: step 4 hook not built
- A destroyed door under hostile fire becomes RM_BreachedDoorway                       → UNCOVERED: step 2/4 not built
- Repair erases a wall scar only by deconstruct+rebuild (owner 2026-10-03: scars REMAIN after repair) → UNCOVERED: step 1 not built
- A roofed outer-door room with no visitors accumulates drift/dust                     → UNCOVERED: step 3 not built
- Walking through dust film lays a TrackGrid print with heading                        → UNCOVERED: step 3/5 not built
- Each Mod Settings toggle off removes its effect                                      → UNCOVERED: no settings until step 1
- Scene and gameplay placements are byte-identical in the save                         → UNCOVERED: needs a save-diff tool (file as item when step 4 lands)
- Traces read as their claim to a viewer                                               → UNCOVERED: owner/blind-reader judgement (§4 boundary)

## anti-guessing notes
- RULED OUT: wall marks via CornerFiller filth show the whole texture — Graphic_Linked samples one 4×4 atlas tile (MaterialAtlasPool.SubMaterialFromAtlas)
