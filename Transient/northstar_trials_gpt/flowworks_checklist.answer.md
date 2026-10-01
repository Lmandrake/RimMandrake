1. `canal_reads_as_dug_channel`, `never_gravel_path` — overlapping category tests. Replace with: `canal_reads_as_dug_channel` — “a dug channel has a visibly recessed bed and cut earthen walls.” Replace `never_gravel_path` with: “a channel bed with the light pebbled surface and road-like edges of a gravel path.”

2. `canal_partial_fill_distinct`, `fill_tier_legible` — the former is wholly contained in the latter. Replace `canal_partial_fill_distinct` with: “a partly filled canal shows exposed inner wall between its liquid surface and rim.”

3. `canal_fill_spreads_along_itself` — “spread” describes hidden behavior and competes with the advancing-front bar. Replace with: “an incompletely filled channel has one continuous wet reach extending away from its inlet, not an isolated inlet puddle.”

4. `canal_fill_front_watchable` — compound: front movement and water-versus-tar speed. Replace with: “the wet/dry boundary is visibly farther along the same channel in AFTER than BEFORE.” Add bar: `tar_fill_front_lags_water` (change) — “from matching dry starts in BEFORE, water extends visibly farther than tar in AFTER.”

5. `canal_holds_only_the_channel`, `never_liquid_on_open_ground` — inverse duplicates, and both literally catch the natural reservoir. Replace the former with: “the liquid surface ends cleanly at the channel’s inner walls without crossing its rim.” Replace the latter with: “liquid newly appearing in AFTER on undug ground outside both the pre-existing reservoir and channel.”

6. `reservoir_fill_visibly_drops` — compound and incorrectly applies to limitless reservoirs. Replace with: “an enclosed reservoir’s visible liquid level is lower in AFTER than BEFORE.” Add bar: `reservoir_shoreline_recedes` (change) — “the far shoreline of an enclosed small pond has receded in AFTER.”

7. `never_full_reservoir_after_heavy_draw` — exact inverse of the revised reservoir-drop bar. Retire this ID without reuse.

8. `reservoir_fill_visibly_drops` — “reduces in proportion” remains uncovered. Add bar: `reservoir_and_channel_volume_balance` (change) — “the visible reservoir volume lost in AFTER matches the visible canal volume gained.”

9. `canal_fire_reaches_reservoir` — a still image cannot show “reaches.” Replace with: `canal_fire_reaches_reservoir` (change) — “the connected flammable reservoir is unlit in BEFORE and visibly alight in AFTER while channel fire remains visible.”

10. `canal_spent_after_burn` — lacks the dry control needed to prove “not merely dry.” Replace with: “a burned-out channel is visibly distinguishable from an unburned dry channel by persistent scorch residue.”

11. No bar covers “burn for a very long time.” Add bar: `canal_fire_persists` (change) — “the same liquid remains visibly alight in both panels whose visible game clocks are at least one in-game day apart.”

12. `slime_reads_as_viscous_not_water`, `fill_fluid_distinct` — the current slime bar duplicates generic fluid distinction and substitutes “viscous” for the owner’s “slippery.” Replace with: “beside equally full water, slime has a visibly thicker and less transparent surface rather than a recolored water surface.”

13. No bar visually communicates slippery crossing. Add bar: `slime_crossing_reads_as_slipping` (change) — “a pawn entering slime changes from a normal stride in BEFORE to a visibly slipping or off-balance pose in AFTER.”

14. `pit_depth_ladder_legible` — surface is not an excavation. Replace with: “surface and depth-1 through depth-4 cells shown side by side are each visually distinguishable.”

15. Separate depth and fill tests do not prove that both remain readable simultaneously. Add bar: `depth_and_fill_jointly_legible` — “in one mixed view, cells sharing a fill but differing in depth and cells sharing a depth but differing in fill remain distinguishable.”

16. `pawn_rises_and_lowers_with_depth` — one diptych cannot show descent, ascent, and every depth. Replace with: “the same pawn is visibly lower relative to the terrain rim in AFTER after moving to a deeper cell.” Add bar: `pawn_rises_on_shallower_cell` (change) — “the same pawn is visibly higher in AFTER after moving to a shallower cell.” Add bar: `pawn_height_ladder_legible` — “pawns shown on depth-0 through depth-4 cells sit progressively lower at every deeper step.”

17. `pit_reads_as_hole` — compound: darkness, hole identity, and visible wall depth. Replace with: “a superdeep cell reads as a big dark hole at play zoom with labels hidden.” Add bar: `pit_walls_have_visible_depth` — “an empty superdeep pit shows visible wall faces descending from rim to floor, not a flat dark tile.”

18. `pit_not_vanilla_trap` — “nothing in the excavation family” is an unprovable universal. Replace with: “the displayed excavation is visually distinct from the vanilla spike-trap reference shown in the same screenshot.”

19. `pit_trapped_reads_as_trapped` — “unable to get out” is hidden state. Replace with: “the surrounding rim stands visibly roughly one-fifth of the pawn’s height above the top of the occupant’s head.”

20. `pit_covered_invisible` — the judge cannot identify an invisible target in one still. Make it `(change)` and replace with: “BEFORE and AFTER images of the same patch are visually identical at standard play zoom after the superdeep excavation is covered.”

21. `ladder_state_legible` — lowered-versus-absent omits the promised raised state. Replace with: “a raised ladder remains visible beside the rim and is visibly distinguishable from the same ladder lowered into the excavation.”

22. `spikes_read_distinct` — a marker could pass without honoring the spike/camera ruling. Replace with: “at play zoom, at least some of the installed spikes visibly project within the pit.”

23. `never_snared_standing` — three claims form an easy-to-pass conjunction and standing height overlaps `pit_occupant_below_floor`. Replace with: “a trapped pawn shown in an ordinary upright standing pose rather than a fallen or sunk pose.” Add bar: `never_pit_text_label` — “the word ‘Pit’ or another explanatory trap label printed over the excavation.” Add bar: `never_trapped_pawn_camera_pose` — “a trapped pawn posed front-on toward the viewer.”

24. `never_reads_as_building` — fittings could legitimately be buildings. Replace with: “the bare excavation itself, excluding ladders, gates and spikes, reads as a placed building sitting on the floor.”

25. Pumping and tanks have no coverage. Add bar: `pump_draw_visibly_lowers_fill` (change) — “the pumped excavation has a visibly lower fill tier in AFTER.” Add bar: `tank_fill_cost_visible` (change) — “as the tank changes from empty to full, five brimming canal-cell equivalents visibly disappear from the connected excavation.”

26. Stock exhaustion and gradual natural refill have no coverage. Add bar: `empty_reservoir_stops_flow` (change) — “with the reservoir visibly empty, the canal’s wet front remains unchanged between panels whose visible game clocks differ.” Add bar: `reservoir_recharge_progress_visible` (change) — “the depleted reservoir has gained visible liquid in AFTER but remains short of full.”

27. Filled-excavation movement cost has no visual proxy. Add bar: `filled_excavation_reads_as_obstacle` — “a filled excavation reads as substantially harder to cross than surrounding ordinary ground.”

28. `pit_covered_invisible`, `pit_covered_seam_at_max_zoom`, `sluice_gate_state_legible`, `fill_fluid_distinct`, `spikes_read_distinct` — the trial plan’s BLOCKED/park choice contradicts the owner’s binding rule. Replace that disposition with: “Bound; expected NO until the feature can produce the required screenshot.”

Overall verdict: not ready to validate—strong coverage, but several bars remain compound or duplicative, and persistence, pumping, recharge, joint depth/fill, and exact depth/spike promises are not yet fully bound.