# Gimme Some Slack: every conduit is a too-long extension cord

## his words
- 2026-10-10: "We need to move the GimmeSomeSlack hose code/functionality over to FlowWorks. That's the right home, and it allows GimmeSomeSlack to be entirely about cables and conduits and electricity."
- 2026-10-10, on power theft: "If caught, steady goodwill drain (like living too close to a settlement)"
- 2026-10-16: "I think it's because the conduit doesn't go physically under the pump. That's ok my Rimworld rules, and so you show one cable going all the way. But then you draw a second cable that acts disconnected as well."
- 2026-10-22, on pipe poles: "Their own switch."
- 2026-10-23: "the electrical plug is shown going into a pipe slot. Weird. It should favor diagonal approaches sliding underneath, to avoid confusion."
- 2026-10-26: "find out if gimme some slack also has the same problemmatic delay with large numbers of wires and connectors."
- 2026-11-02: "Yes, I want both poles and floor coords. No, I would not reject it, but there's no reason not to do this. It's just art and that's easy. No, I don't much care about savegame continuity"
- 2026-11-02: "The power strips (modern style art) or connectors (other art styles) should appear whenever there are three or four way junctions of conduit. They should appear to host many of the other lines plugging into the power strips and connectors, as the means to join the many cables. Cables should look messy and only loosely follow the conduit in the floor. It should not repeat patterns but appear like real messy cables strewn across the floor."
- 2026-11-02: "they should explain the connectivity if power between the actual conduits and devices and the visual appearance of the wires. But the wires are allowed to get there through a much more circuitous route as overly long extension cables do."
- 2026-11-05, on the root: "Restate Honest: Faithfully represents connectivity but not precise conduit path. For the shock, needs one more line on how a Pawn ever fixes a sparking line: if they approach intending to fix it, they are safe. If they incidentally go over the sparking end with a different job, they (or anyone else) gets shocked."
- 2026-11-05, on Modern junctions: "The right power strip is better for modern look. Junctions work better for industrial."

## does
- [leaf:conduit_invisible] Conduit draws no pipe; only the loose cords show where power goes, and the power overlay still works. OWNER:1793590546413059482
- [leaf:cords_lie_slack] Every cord lies in broad slack loops and coils, much longer than its straight line, never taut. OWNER:1793596860187785113
- [leaf:cords_meet_walls_at_face] Cords pile against walls and end at the wall face, never drawn across a wall or rock. OWNER:1793596860187785113
- [leaf:strip_at_every_junction] Every 3- or 4-way junction has a joining piece with every cord plugged in: Modern draws the long power strip, Industrial the junction box, the other two their connectors. OWNER:1793909100631838579, owed
- [leaf:dense_block_tangle] A dense block of conduit reads as one tangled heap of wires and strips
- [leaf:cords_never_repeat] Cords of the same length do not repeat one shape across a room. OWNER:1793596860187785113
- [leaf:drawing_true_to_grid] The cords tell the truth about the grid: no cord joins two nets, no phantom second cable at an adjacent-fed pump, no plug in a pipe slot. OWNER:1793895896496551063
- [leaf:cut_live_and_dead_ends] A cut leaves two ends and no cord across the gap: the live end sparks, the dead end lies limp
- [leaf:no_stall_on_rewire] Placing, cutting or digging past a wire, or a mast falling, costs at most 20 ms a frame on a 2000-cell base. OWNER:1792999698321800383
- [leaf:spans_above_everything] Sagging overhead lines between masts draw above pawns and buildings. OWNER:1793590546413059482
- [leaf:fallen_span_on_ground] A killed mast or a cut span leaves the wire lying on the ground, live end and dead end distinct
- [leaf:fallen_wire_shocks_crossers] A live fallen wire shocks anyone crossing it on another job; the colonist coming to re-string it is safe. OWNER:1793895896496551063
- [leaf:restring_cut_span] A Wire down alert points at the cut, and a colonist re-strings it as a job. OWNER:1792080489684076824
- [leaf:tap_steals_and_costs_goodwill] A tap clamped on a neighbour's line steals their power; if they see it, goodwill drains steadily. OWNER:1791668362056240097
- [leaf:four_looks_one_run] Four looks told apart by eye, one look per connected run. OWNER:1793590546413059482
- [leaf:settings_switch_cleanly] Every switch really switches, master off restores vanilla art without a restart, and pipe poles have their own switch. OWNER:1792636779179768957
- [leaf:gravship_keeps_connections] After a gravship lands, its cords still explain its real connections. OWNER:1793597165476278817
- [leaf:no_hose_in_gss] No hose, reel or pipe is drawn by this mod. OWNER:1791668361069985398
- [leaf:cord_shape_variation_probe] A shape-distance read between cords, so no-repeat can be measured
- [leaf:walk_scavenger_base] A week of play on the full list with a cut, a re-string, a mid-way reload, a repeat and a second order
- [floor:mod_settings] Superb Mod Settings: every feature has a working switch
- [floor:tick_cost] The rebuild's own cost, measured on the rewire bar
- [advisory] Which look a player picks is taste; none of the four is reject-level on its own

## does not
- [waived:w1] A save made with the mod loading clean after the mod is removed is not promised
- [floor:worldgen] No worldgen of any kind
- [floor:multiplayer] No multiplayer support

## waived
- w1, 2026-11-02: "I don't much care about savegame continuity"

## open
- Nothing core is open: by card 2026-11-05 you picked the workshop floor as showcase 1, OWNER:1793950666234031543

## delegated
- No-repeat is judged by a shape-distance number with a judge agent predicting your eye, since only your eye had judged it
- Showcase 2 is the yard of masts, the most new ground after the workshop floor; theft, the four looks, Mod Settings, the gravship and new-game cleanup are checked by their own scenes
- The lone-rebuild bar is 20 ms a frame, the floor's own tick ceiling

## pruning
- conduit_invisible: his words, little drawn wires over otherwise-invisible conduits, north star conduit_reads_invisible
- cords_lie_slack: his words OWNER:1793596860187785113, realistically sprawling over-length extension cables
- cords_meet_walls_at_face: his words OWNER:1793596860187785113, cables should pile against the wall
- strip_at_every_junction: his words OWNER:1793596860187785113 and his pick OWNER:1793909100631838579
- dense_block_tangle: north star dense_grid_reads_as_tangle, validated by him
- cords_never_repeat: his words OWNER:1793596860187785113, it should not repeat patterns
- drawing_true_to_grid: his root OWNER:1793895896496551063, faithfully represents connectivity
- cut_live_and_dead_ends: his root, sparking where it is live and dead where it is not
- no_stall_on_rewire: his root, a huge base shows no problematic delay
- spans_above_everything: his words OWNER:1793590546413059482, both poles and floor cords
- fallen_span_on_ground: north star downed_span_lies_on_ground, validated by him
- fallen_wire_shocks_crossers: his root OWNER:1793895896496551063, incidental crossers shocked, fixer safe
- restring_cut_span: his card OWNER:1792080489684076824, make it a colonist job
- tap_steals_and_costs_goodwill: his words OWNER:1791668362056240097
- four_looks_one_run: advisory by his words OWNER:1793590546413059482, would not reject it alone
- settings_switch_cleanly: standing ruling, superb Mod Settings; his words OWNER:1792636779179768957
- gravship_keeps_connections: his words OWNER:1793597165476278817
- no_hose_in_gss: his words OWNER:1791668361069985398
- walk_scavenger_base: the mod's one walk leaf, required of every mod
