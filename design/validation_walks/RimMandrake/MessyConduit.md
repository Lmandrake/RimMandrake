# MessyConduit — validation walk
subject: src/RimMandrake/MessyConduit  (packageId mandrake.rm.messyconduit)
deps: brrainz.harmony (hard modDependency)
list: messyconduit (modset_builder tier: bridge + this mod + all five DLCs)
status-hint: phase 1a of design/RimMandrake/messy_conduit_design_2026-10-02.md — conduit made invisible (runtime texPath swap, restorable), machine hookup wires hidden for our conduit only, and a cosmetic SectionLayer that draws loose too-long cords between the nodes of the conduit graph (reduction + A* + canned slack, Verse-free core in Source/Core), with a break readout (live ends spark, dead ends lie limp). Functional script: src/RimMandrake/MessyConduit/validation.py.

## must be true
- M1. The cord graph of the current map exists (`RM_MapComponent_CordGraph`), its node census matches the conduit grid (machines, junctions, terminals at every conduit end, a stub where conduit goes into a wall, a wall terminal where it ends inside one), cords are printed into the section meshes, and `PowerConduit`/`WaterproofConduit` render with the fully transparent texture. (validation.py: M1_conduit_transparent, M1_cords_exist, M1_node_census, M1c_end_pieces)
- M2. No cord edge joins two nodes in different `PowerNet`s, and no laid cord vertex lies in an unwalkable cell. (M2_cords_only_within_net, M2b_no_vertex_unwalkable; offline O3 asserts both on 7 oracle scenes)
- M3. Vanilla `HiddenConduit` stays invisible and is never drawn as a cord: it is excluded from the target defs and counts as buried conduit (connectivity kept, nothing drawn). (offline: ConduitVisuals target list; live census `texPaths` lists only PowerConduit and WaterproofConduit)
- M4. The same map yields the same cord polylines after a save/load. (validation.py --save-load NAME: M4_save_load_hash, M4a_save_landed_new_file_only; D1_determinism_fresh_build shows a fresh builder reproduces every edge's geometry hash on the same map)
- M5. Placing conduit far from a cord does not change that cord's geometry hash, and the rebuild re-plans only the touched edge. (M5_local_invalidation)
- M6. With the mod on, the power overlay still prints its connector lines (`SectionLayer_ThingsPowerGrid` sub-mesh for `MatConnectorLine` non-empty) while the thin hookup wire is suppressed for our conduit. (M6_overlay_lines_intact)
- M7. Master switch off: the layer is not visible and conduit renders with its vanilla atlas again, without a restart; on again restores the invisible conduit and the cords. (M7_off_restores_vanilla, M7b_on_again_invisible)
- M8. Destroying one conduit cell in a powered line gives two terminal ends and no cord across the gap; the battery side reads live and the far side dead; turning the source off makes the live end read dead within one 250-tick poll. (M8_break_two_ends_live_dead, M8b_no_cord_across_gap, M8c_source_off_reads_dead_250)
- M9. A save made with the mod loads clean without it (nothing is saved). (validation.py --removal-check NAME on a tier without the mod: M9_remove_mod_clean; --save-load also asserts M9a_save_holds_nothing_of_ours)

## the walk
1. [O] `python3 src/RimMandrake/MessyConduit/validation.py` — O1 files/csproj/textures, O2 settings defaults, O3 C# core SelfTest against the Python oracle (+ --probe must fail every scene), O4 the oracle's own selftest
2. [B] `python3 src/RimMandrake/Utils/modset_builder.py --tier messyconduit --apply`, launch via Steam, then `python.exe src/RimMandrake/MessyConduit/validation.py --live --fresh-map` (~270 ticks; state read through `MessyConduitProbe` via `jawa/mod_settings_field`)
3. [B] `python.exe src/RimMandrake/MessyConduit/validation.py --save-load <NEW_NAME>` on the same map (M4), then ONE cold load onto a tier without the mod (`--tier flowworks`) and `python.exe src/RimMandrake/MessyConduit/validation.py --removal-check <NEW_NAME>` (M9)
4. [B] record: `python3 -m modcheck.cli record MessyConduit --result <validation_result_*.json> --tier messyconduit` (REFUSED while UNBUILT/UNCOVERED bars remain — honest by design)
X. [S] (human pass) the look: screenshots under Transient/messy_conduit_live_20261002/ or a keeper save; never a pass bar
