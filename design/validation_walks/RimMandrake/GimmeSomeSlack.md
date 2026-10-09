# GimmeSomeSlack (was MessyConduit) — validation walk
subject: src/RimMandrake/GimmeSomeSlack  (packageId mandrake.rm.gimmesomeslack)
deps: brrainz.harmony (hard modDependency)
list: gimmesomeslack (modset_builder tier: bridge + this mod + all five DLCs)
checkout: src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py  (the ONE live proof; its declared_rows() is the manifest's row list, its northstar/proof_all_*.json the result the report reads)
status-hint: phases 1a/1b/2 + per-build styles of design/RimMandrake/messy_conduit_design_2026-10-02.md (+ messy_conduit_phase2_design_2026-10-02.md, messyconduit_style_per_build_design.md) — conduit made invisible (runtime texPath swap, restorable), machine hookup wires hidden for our conduit only, and a cosmetic SectionLayer that draws loose too-long cords between the nodes of the conduit graph (reduction + A* + canned slack, Verse-free core in Source/Core), with a break readout (live ends spark, dead ends lie limp). Functional script: src/RimMandrake/GimmeSomeSlack/validation.py; the ONE live proof is proof_all.py (owner densification 2026-10-05, design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md).

## must be true
- M1. The cord graph of the current map exists (`RM_MapComponent_CordGraph`), its node census matches the conduit grid (machines, junctions, terminals at every conduit end, a stub where conduit goes into a wall, a wall terminal where it ends inside one), cords are printed into the section meshes, and `PowerConduit`/`WaterproofConduit` render with the fully transparent texture. (validation.py: M1_conduit_transparent, M1_cords_exist, M1_node_census, M1c_end_pieces)
- M2. No cord edge joins two nodes in different `PowerNet`s (on the built scene AND after the M8 break, where a cord across the gap would be one), and no laid cord vertex lies in an unwalkable cell. (M2_cords_only_within_net, M2b_no_vertex_unwalkable; offline O3 asserts both on 7 oracle scenes)
- M3. Vanilla `HiddenConduit` stays invisible and is never drawn as a cord: it is excluded from the target defs and counts as buried conduit (connectivity kept, nothing drawn). (offline: ConduitVisuals target list; live census `texPaths` lists only PowerConduit and WaterproofConduit)
- M4. The same map yields the same cord polylines after a save/load, and the save names no class of ours. (proof_all.py: SL1_save_landed_new_file_only, SL2_save_names_no_class_of_ours, SL3_after_load_census_equal over the session's one save; D2_fresh_builder_same shows a fresh builder reproduces every laid edge on the same map)
- M5. Placing conduit far from a cord does not change that cord's geometry hash, and the rebuild re-plans only the touched edge. (M5_local_invalidation)
- M6. With the mod on, the power overlay still prints its connector lines (`SectionLayer_ThingsPowerGrid` sub-mesh for `MatConnectorLine` non-empty) while the thin hookup wire is suppressed for our conduit. (M6_overlay_lines_intact)
- M7. Master switch off: the layer is not visible and conduit renders with its vanilla atlas again, without a restart; on again restores the invisible conduit and the cords. (M7_off_restores_vanilla, M7b_on_again_invisible)
- M8. Destroying one conduit cell in a powered line gives two terminal ends and no cord across the gap (M2 after the break); the battery side reads live and the far side dead; turning the source off makes the live end read dead within one 250-tick poll. (M8_break_two_ends_live_dead, M8c_source_off_reads_dead_250)
- M10. Overhead lines: masts link into one net across a gap and power a far consumer; unlink/relink, out-of-range / hostile / non-anchor links are refused; a removed middle mast resolves both ends, a killed one drops a live and a dead cord, an explosion cuts a span that restrings; the power tap drains a foreign grid one way and stops when taps are off. (validation_aerial.py: M13a-e, R1-R3, M14-M15b, M19, M19n; matrix MX_A scenes; links and fallen cords survive SL3)
- M10b. A "Wire down" alert lists every player anchor whose wire is cut or lying on the ground, clicking it jumps to the anchor (where Re-string cut wires lives), it clears once the span is re-strung, and the settings toggle (`wireDownAlert`) turns it off. (validation_aerial.py: M15a_wire_down_alert_lists_cut, M15c_wire_down_alert_clears_on_restring; probe `alert`) WIRE_DOWN_ALERT_1
- M11. Hoses: a hose lays as a thick, stiff hose cord round a wall, plumps within its transition when flow is on, never flickers on a fast toggle, collapses only after the release window, re-lays on a stiffness change; it solves a maze and re-routes or retracts with a reason when walled; relay reels chain past one hose's reach without a ring. (validation_hose.py: H1b, H2, H6-H9, maze M1-M5/P1-P2, relay RL2-RL9; matrix MX_H scenes carry width/bend/flat; hose state survives SL3)
- M12. A colonist carries a hose end: the trail follows his walk, drafting drops it with the order kept, the work giver resumes it to the target, a retract winds it in, and the instant lay/reel-in gizmos exist only in dev mode. (validation_hose.py --carry: CR1-CR3, CR5-CR7; a dropped and a carrying reel survive the one save, the carrying one resumes after the load: SL4_carry_states_survive)
- M13. Per-build styles: a picked look reaches the blueprint, frame and building in build and god mode, survives copy and reinstall, spans and conduit runs draw their run's look (largest run wins on a bridge, a split keeps it, a restyle repaints one run), and an unstyled (older) mast, run or reel stores nothing and draws the default look. (validation_style.py S1-S6, S8, S9a-d, S10; validation_style_hose.py R1-R3, R5-R7; every stored style survives SL3)

## the walk
1. [O] `python3 src/RimMandrake/GimmeSomeSlack/validation.py` — O1 files/csproj/textures, O2 settings defaults, O3 C# core SelfTest against the Python oracle (+ --probe must fail every scene), O4 the oracle's own selftest
2. [B] `python3 src/RimMandrake/Utils/modset_builder.py --tier gimmesomeslack --apply`, launch via Steam, then `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live [--no-shots]` from the repo root: offline gate (in WSL), one fresh map, P1-P3 preflight, the reduced matrix (39 scenes), core, aerial, hose, maze, relay, carry, style, style-hose, D1/D2, ONE save + load (SL1-SL4), one log budget Z; one result JSON `northstar/proof_all_*.json` (state read through the mod's probes via `jawa/mod_settings_field`)
3. [B] (the removal check is PAUSED, owner 2026-10-04: *"I don't want to do removal checks regularly"* — walk E1; on request: one cold load onto `--tier flowworks`, then `validation.py --removal-check <the proof_all save>`)
4. [B] record: `python3 -m modcheck.cli record GimmeSomeSlack --result <northstar/proof_all_*.json> --tier gimmesomeslack`
X. [S] (human pass) the look: `python.exe src/RimMandrake/GimmeSomeSlack/human_review.py --build --fresh-map` stages the labelled review map (33 stations + art board M + free build area F, key sheet built in Transient/mc_human_review/ and filed into src/RimMandrake/GimmeSomeSlack/review/ by save_review_map.py; principles: design/RimMandrake/northstar_human_review.md); screenshots under Transient/messy_conduit_live_20261002/ or a keeper save; never a pass bar

## extended
Not run in a basic checkout and never blocks one; run only when requested (design/RimMandrake/debug_process.md §6b).
- E1. Removal: a save made with the mod loads clean without it (nothing of ours is saved) -> `validation.py --removal-check NAME` on a tier without the mod (cold load onto `--tier flowworks`); PAUSED by the owner 2026-10-04 (*"I don't want to do removal checks regularly"*)
- E2. Mod-mod compatibility: other conduit/power-render mods (hidden-conduit, power-grid overlay and wire mods) alongside GimmeSomeSlack -> UNBUILT (no tier or check yet)
- E3. Declared incompatibilities: `About.xml` names every mod known to clash (incompatibleWith / loadAfter), and each one names a reason -> UNBUILT (no check yet)
- E4. FlowWorks pump hookup: once FlowWorks ships `RM_PumpPortable`, a hose reel next to a running pump reads flowing through `FlowWorksPumpFlow` -> UNBUILT (no pump in FlowWorks yet)

## north star
state: DRAFT
validated-hash:

The `state:` line above is authoritative; `design/RimMandrake/north_star_validation_spec.md` defines what each
state means, and a checklist binds only while that line reads VALIDATED. The hash recorded on validation covers
this whole section, so any edit afterwards reverts it to DRAFT until he re-validates. Every bar below was first
drafted by an agent (FOUNDRY helper, 2026-10-05) from his words in this section, for him to cut, reword or keep;
each bar is one claim a player can check by looking, and where each came from is in the provenance table, never
in the bar text, because the bar text is the question the judge is asked.

🔑 **A bar for a feature that is not built yet fails until it is built.** That is the bar doing its job, not a
reason to park it. Motion (sway, whipping ends, spark timing) carries no bar, by his ruling below; the review map
(`human_review.py`) and the state proxies in `validation.py` cover it.

### the experience  (OWNER'S WORDS — verbatim)

The idea, 2026-10-02 (`design/RimMandrake/messy_conduit_design_2026-10-02.md`, top):

> *"I normally hate how they make conduit invisible, but now that I think about it, Jawa should celebrate that. I
> almost want to make it weirder like snakey, ropey loose conduit on the floor. Spawn out a design pass to consider
> how hard it would be to make MESSY CONDUIT, an alternative mod that would make conduit sprawl all over the floor
> in loose wirey mess like it does in real life."*

The overlay and the nodal ruling, 2026-10-02 (same file, §8):

> *"I had wondered if we could actually have little drawn wires decoratively put over otherwise-invisible-conduits
> as usual. So the visible wires would only be aesthetic. … We certainly wouldn't want annoying clipping issues."*

> *"… It's just about cords roughly connecting to/from where they belong. Honestly they don't even need to go over
> where the conduit is... it's really the nodal map of sources, destinations, places where they go into walls,
> places where they emerge, and then corners that they must traverse. … Perhaps we don't need to show it "over the
> wall" after all, we just say "it's in there" and show where it comes out/goes in. … But do let's aim for that
> extra loopy slack look. I'm not going for taught cables. Quite the opposite. Everything is a too-long extension
> cord."*

> *"Yes, conduit that suddenly ends has a "node" at its terminal point that must be reached by a "broken" cord
> lying on the ground. Sparking if live, dead if not. … How to handle a "grid of conduit beneath the ground"
> (ideally a huge tangle of nasty wires and power strips all swirled together terribly)."*

The slack, 2026-10-02 (same file, §8.6), with a photo of an orange extension cord in big loose loops:

> *"Yes, I want it to have much larger excursions that avoid unwalkable areas or even pile up against them. I think
> you know what I'm wanting."*

Phase 2, 2026-10-02 (`design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md` §0):

> *"… I'd like the powerlines included, swaying in the wind, etc. Much of this won't be Northstar testible, I'll
> tell you that up front. Movement/animation is not appropriate for Northstar, unfortunately. But throwing up a
> complex series of well defined power grids and then taking a screenshot to show the various stages of tangling,
> the power line connections, etc. in a combinatorially useful pattern absolutely IS possible and valuable. … The
> flexible water hoses should be much thicker and stiffer than the wires, much like the fire hoses they use. And
> they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not."*

Relay reels, 2026-10-04 (`src/RimMandrake/GimmeSomeSlack/validation_hose.py`, relay section):

> *"So if the hose can only reach 30 cells, how does the player go farther? Maybe they place another reel out there
> to connect to?"*

Style per build, 2026-10-04 (`design/RimMandrake/messyconduit_style_per_build_design.md`, top):

> *"… A single build menu should allow the player to select between these four art styles for the poles, hose
> reels, hoses, and cables somehow. … Obviously a single connected run of conduit no matter how large would be a
> single art style. …"*

Review, 2026-10-05 (`src/RimMandrake/GimmeSomeSlack/Source/Hose/CompHoseReel.cs`, `SetLook`):

> *"reels don't have a choose style option"*

Review, 2026-10-05 — **relayed by FOUNDRY, not his verbatim words; no verbatim text of these is on disk, and he
replaces this paragraph with his own wording:** the hose joiners must look like brass screwed together; the 2x2
reel's hose must attach to its brass outlet nozzle; a hose should look deflated unless it carries liquid, has
somewhere to flow, and is driven by a powered pump.

### must show

**Floor cords — the nodal sprawl**
- [ ] `conduit_reads_invisible` — a conduit run shows no vanilla conduit pipe; only the loose cords show where
      power goes.
- [ ] `cord_lies_slack_in_loops` — a cord between two nodes lies in broad loose loops and excursions, visibly
      much longer than the straight line between its ends.
- [ ] `cord_meets_wall_at_its_face` — where conduit runs into a wall, the cord ends at the wall's face, as if it
      goes in there, and is not drawn across the top of the wall.
- [ ] `dense_grid_reads_as_tangle` — a dense block of conduit reads as one tangled heap of wires and power strips,
      not as tidy parallel lines.
- [ ] `break_live_and_dead_ends_differ` — at a cut in a powered line, the end still on power is visibly
      distinguishable from the dead end lying limp, at normal zoom.

**Overhead lines**
- [ ] `overhead_span_above_everything` — an overhead span between masts is drawn above pawns, buildings and laid
      hoses beneath it, never under them.
- [ ] `downed_span_lies_on_ground` — after a mast is destroyed or a span is cut, the span lies on the ground as a
      fallen cord rather than hanging in the air.

**Hoses**
- [ ] `hose_thicker_stiffer_than_cord` — a laid hose is visibly several times thicker than a power cord and turns
      in wide curves, never in tight loops.
- [ ] `hose_plump_when_flowing_flat_when_not` — a hose carrying flow is drawn round and full, and the same kind of
      hose with no flow is drawn flat.
- [ ] `hose_plumps_only_from_powered_pump` (change) — a hose coupled to a pump is flat in the BEFORE frame with the
      pump unpowered and round in the AFTER frame with the pump powered and liquid flowing.
- [ ] `hose_joiner_reads_brass_screwed_together` — where one hose length meets the next, the joint reads as two
      brass couplings screwed together, with no gap between them.
- [ ] `reel_hose_leaves_brass_outlet_nozzle` — a laid hose leaves its reel from the reel's brass outlet nozzle,
      with a coupling on it, not from under the drum.
- [ ] `reel_laid_and_wound_look_differ` — a reel with its hose laid out looks different from the same reel with
      its hose wound in, and the laid hose visibly runs into the reel.
- [ ] `relay_chain_reads_connected` — a hose that ends on the next reel of a relay chain reads as coupled to it,
      not as two loose hoses lying side by side.

**Styles**
- [ ] `four_styles_distinguishable` — Scrapper, Industrial, Modern and Futuristic poles, reels, hoses and cables
      are distinguishable from each other by looking.
- [ ] `one_run_one_style` — every piece of one connected conduit run draws in a single style, while two separate
      runs side by side can draw in different styles.
- [ ] `reel_offers_choose_style` — a selected hose reel shows a "Choose style" button.

### cannot show

- [ ] `never_taut_straight_cord` — a floor cord pulled taut in a straight line between two nodes.
- [ ] `never_cord_across_impassable` — a cord or hose drawn across a wall, rock or other impassable cell.

### provenance

Every row: drafted by an agent 2026-10-05 from the quote named; nothing here is his ruling until he validates.

| bar | his words it distils |
|---|---|
| `conduit_reads_invisible` | *"little drawn wires decoratively put over otherwise-invisible-conduits"*; *"Jawa should celebrate that"* |
| `cord_lies_slack_in_loops` | *"Everything is a too-long extension cord."*; *"much larger excursions"* |
| `cord_meets_wall_at_its_face` | *"we just say "it's in there" and show where it comes out/goes in"* |
| `dense_grid_reads_as_tangle` | *"a huge tangle of nasty wires and power strips all swirled together terribly"* |
| `break_live_and_dead_ends_differ` | *"Sparking if live, dead if not."* — worded as a state, since sparks are motion |
| `overhead_span_above_everything` | *"I'd like the powerlines included"*; *"the power line connections"* |
| `downed_span_lies_on_ground` | *"a "broken" cord lying on the ground"*, carried to the overhead lines |
| `hose_thicker_stiffer_than_cord` | *"much thicker and stiffer than the wires, much like the fire hoses they use"* |
| `hose_plump_when_flowing_flat_when_not` | *"they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not"* |
| `hose_plumps_only_from_powered_pump` | 2026-10-05 review, relayed (deflated unless liquid + somewhere to flow + powered pump); fails until FlowWorks ships a pump |
| `hose_joiner_reads_brass_screwed_together` | 2026-10-05 review, relayed (joiners look like brass screwed together) |
| `reel_hose_leaves_brass_outlet_nozzle` | 2026-10-05 review, relayed (2x2 reel's hose attaches to its brass outlet nozzle) |
| `reel_laid_and_wound_look_differ` | style-per-build brief: a reel that looks different when its hose is laid out, the hose running into the reel (paraphrased in that design's own text) |
| `relay_chain_reads_connected` | *"Maybe they place another reel out there to connect to?"* |
| `four_styles_distinguishable` | *"select between these four art styles for the poles, hose reels, hoses, and cables"* |
| `one_run_one_style` | *"a single connected run of conduit no matter how large would be a single art style"* |
| `reel_offers_choose_style` | *"reels don't have a choose style option"* |
| `never_taut_straight_cord` | *"I'm not going for taught cables. Quite the opposite."* |
| `never_cord_across_impassable` | *"avoid unwalkable areas or even pile up against them"*; *"We certainly wouldn't want annoying clipping issues."* |
