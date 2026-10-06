# RimMandrake FlowWorks — validation walk
subject: src/RimMandrake/FlowWorks  (packageId `mandrake.rm.flowworks`)
feature: canal-flood-engine
deps: Ludeon.RimWorld.Odyssey (Flood is Odyssey-gated in the base game); none third-party
list: minimal+Odyssey     # official DLC, not a workshop mod; check it is in the active list
status-hint: dig a canal cell, let a fluid reservoir prime and then drip + re-flood adjacent terrain on two cadences — species/biome-agnostic engine, water is the one shipped fluid

The reservoir era (`CompFluidReservoir`, `RM_FluidSpring_Test`, `Flood_FluidCanal`) ended with ruling 24
(2026-09-16): a source is a SUPERDEEP cell or a natural body, not a building. Every step below is written against
the depth/fill primitive (`RM_ExcavationDepth` on `RM_MapComponent_Excavation`, stock in `RM_LiquidStock`, bodies in
`RM_LiquidBody`).

## must be true
- `RM_DigCanal` designation exists and `RM_DigCanalJob`/`RM_DigCanalWorkGiver` drive a colonist to actually dig it (`JobDriver_DigCanal`, `WorkGiver_DigCanal`).
- A flooded cell's *underlying* terrain is recoverable — `TerrainGrid.TopTerrainAt` (what remains once the flood drains) must differ from the temporary flood terrain and must not itself be destroyed. `Flood_FlowWorks.SpreadOneTile` writes `SetTempTerrain` + `QueueRemoveTerrain`, never `SetTerrain`, and the flood terrains deliberately carry no `tempTerrain.destroysFloors`.
- A flood that is walled in before its volume runs out destroys itself at `ExpiryTick` = `spawnedTick + 2 * FloodingTicks` rather than ticking into every save.
- `RM_Channel_Empty` (the dug-channel terrain, Diggable/Walkable/Light affordances, not itself water) is what a D=1 dig sets a cell to (`JobDriver_DigCanal`, or `jawa/flowworks_excavation_drive` in tests; `jawa/canal_dig` is a stub that always fails); D=2/3/4 set `RM_Channel_Mid`/`_Deep`/`_Superdeep`.
- Spread IS channel-constrained: `Flood_FlowWorks.CanFloodInto` gates on `RM_MapComponent_Excavation.CanLiquidEnter`, behind the `channelConfinementEnabled` setting, which defaults to **true**. A player who turns it off is choosing the pre-2026-09-16 leak-across-open-ground behaviour deliberately.

## the walk
Densified 2026-10-05 (`design/RimMandrake/northstar_densification_lessons.md`): ONE core live proof, extensions apart.
1. [O] `python3 src/RimMandrake/FlowWorks/northstar/validation_v2.py` — offline tier O1-O10 (defs incl. the four channel path costs, shipped settings, UNBUILT register, geometry, pulse oracle, scene predictions, lint, shared source, pit width), O-NEG (each offline check mutated red) and O-LIVE-NEG (a clean `--mock` live tier is green and every MockBridge fault turns its row red); `python3 src/RimMandrake/FlowWorks/northstar/selftest_extensions.py` (core/extension split and bar/toggle coverage); `python3 src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py offline`
2. [B] `python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply`, launch via Steam, then `python.exe src/RimMandrake/FlowWorks/northstar/validation_v2.py --live --fresh-map` from the repo root: one fresh 250x250 quicktest map, folded preflight rows (L1 fresh map, L2 tier live incl. Player.log + DLL identity + shipped settings, L3 live channel-def path costs, L4 site ready), S state (dig ladder to superdeep, clamp, classification, sink band, sticky, dig-to-depth gate), 0-tick flow phases A/B/C/R against the oracle (G_every_cell_vs_oracle), J pawn jobs (the only ticks: dig, fill-in displacement, engine off/on, cadence clamp, rain toggle), rain, P pit capture/ladder/carve-out, X pawn height, viscosity, fluid identity, cover, liquid fire (X10: lit, persists, burns out to ash), the fluid-switch refusal and ONE log budget (E9); one result JSON `northstar/validation_v2_result_*.json`
3. [B] record: `python3 -m modcheck.cli record FlowWorks --result <northstar/validation_v2_result_*.json> --tier flowworks`
4. [B] (on request, never by the core proof) extensions: `prep_site.py` + `preflight_flowworks.py live` build and check the golden trial site, then `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live [--chains ...]` runs the visual-trial plots (judge screenshots) and the optional-feature chains (fire reaching a reservoir, fire put out by explosion/foam/rain toggles, doors, spikes, ladders OFF, the superdeep prison room + capture down + lip service, the pump, bottle revert, wall faces, dig finds, bottles/tanks/drilling, shores, river steam, swale ...)
X. [S] (human pass) the look and the build state: `python3 src/RimMandrake/FlowWorks/human_review.py` writes the capability sheet `src/RimMandrake/FlowWorks/northstar/review/FlowWorks_review.html` (status per intended capability, derived from disk + the newest core result + the ledger); never a pass bar

## north star
state: DRAFT
validated-hash: 

The `state:` line above is authoritative;
`design/RimMandrake/north_star_validation_spec.md` defines what each state means, and a
checklist binds only while that line reads VALIDATED. The recorded hash covers this whole
section, so any edit reverts it to DRAFT until he re-validates. Every bar is one observable
claim a player can check by looking; where each came from is in the provenance table at the
end of this section, never in the bar text, because the bar text is the question the judge
is asked.

🔑 **A bar for a feature that is not built yet fails until it is built.** That is the bar
doing its job, not a reason to park it. Every bar below stays bound whatever the state of
the code or the art.

### the experience  (OWNER'S WORDS — verbatim)

The canal, bench session 2026-09-16:

> *"This mod allows the user to dig canals in the ground from an ambient source of liquid
> (fresh water, salt water, tar, propane, colored water, slime, etc from Many Waters if
> present or just water if not). at the liquid's viscosity (water is essentially zero)
> liquid then flows into the canal to fill it, extending the source. This brings the
> concept of a limited vs limitless source. Any source that touches the map edge is
> determined to be limitless. If it is fully encompassed by the map edge, then it is
> limited. Each source's square can supply up to five canal squares with liquid before it
> stops providing. This also brings with it a reduced graphic for the parent water source
> to show that it is strained. This same graphic can be reused should the player start to
> PUMP the water into tanks. One full tank can reduce a source of liquid (equivalent to 5
> filled canal squares). Incompletely filled canals spread the water throughout themselves
> using a graphic showing partial fill, and the parent body of water reduces itself in
> proportion as well. Pumping water out of a source or canal has the same effect. An
> unfilled pit slows movement as per other established dug barriers, while filled pits
> reduce as per that terrain cost. Some materials are flammable and thus the canals can be
> lit and burn for a very long time. They will also light their source at that time. Slime
> has the particular properly of being so slippery that it is nearly impossible to cross,
> and escape from the pit takes a great deal of time. The mod is intended to allow natural
> irrigation of crops (all plants nearby the canal react to the presence of the water as
> though watered)."*

His ranking the same session: **defense first, then irrigation, then industry, and finally
terraforming.** His scarcity ruling: **every source is stock**, refilling *"slowly, from rain
and season and ground liquids oozing in… it can take quite a while to fill up from a very
small natural source."*

2026-09-17, retiring the source object (ruling 34):

> *"Strained isn't a thing anymore. We replaced 'sources' with just placed deep liquid
> reservoirs just like a player would normally place on the map. Filled very deep tiles.
> Everything follows from that."*

The pit, 2026-09-13 and 2026-09-15, on seeing the shipped trap:

> *"Looks like it was working. But we need to think now about very deeply what it looks
> like. It can't just be a simple trap graphic you get stuck on. So we need a big dark
> pit."*

> *"A simple little trap that just Snares a pawn to stand there staring at the camera, stuck
> in a trap with "Pit" written on it. Not at all "falling in a pit" but I understand what
> happened."*

2026-09-17, collapsing the pit onto the canal (`PIT_SUPERDEEP_COLLAPSE_1`):

> *"I'm not really sure a pit is any different than a deep canal."* · *"If you're in a
> superdeep pit, you can't climb out. Period. Welcome to your pit."*

2026-09-17, the depth ruling, verbatim:

> *"All depths must be visually legible and differentiable graphically. The pawn should
> visibly rise up and lower down as they move over the depths. They should be low enough
> that it is visually clear how they could not possibly climb out (the walls are higher
> than their head by 20%)"*

2026-09-17, on spikes and the camera:

> *"The spikes will barely be able to be tall enough to be visible most likely, but there
> should still be something showing their presence. make sure the viewing angle of the pit
> is such that SOME amount of spike is possible"*

🔑 The through-line: **a canal is the reservoir, moved, and a pit is a canal dug all the way
down.** Every cell carries a depth and a fill; the reservoir, the channel and the pit are the
same thing at different depths, and the screen must show which depth and which fill a cell
holds.

### must show

**The channel itself**
- [ ] `canal_reads_as_dug_channel` — a dug channel has a visibly recessed bed and cut earthen
      walls, not the look of a path or a floor.
- [ ] `canal_dry_reads_as_obstacle` — an unfilled channel is legible as something that
      impedes crossing, without a tooltip.
- [ ] `filled_excavation_reads_as_obstacle` — a filled channel reads as harder to cross than
      the ordinary ground beside it.

**Fill**
- [ ] `canal_partial_fill_distinct` — a partly filled canal is distinguishable at a glance
      from a full one.
- [ ] `fill_tier_legible` — dry, trace, half and brimming fill in excavations of the same
      depth are distinguishable from each other by looking.
- [ ] `canal_fill_spreads_along_itself` — an incompletely filled channel shows one
      continuous wet reach extending away from its inlet, not an isolated puddle at the inlet.
- [ ] `canal_fill_front_watchable` (change) — the boundary between wet and dry is visibly
      farther along the same channel in the AFTER frame than in the BEFORE frame.
- [ ] `tar_fill_front_lags_water` (change) — from matching dry starts, water has visibly
      reached farther along its channel than tar has along an identical one after the same
      time.
- [ ] `canal_holds_only_the_channel` — the liquid surface ends at the channel's walls and does
      not spread onto the ground beside it.
- [ ] `canal_reads_as_same_liquid_as_reservoir` — a filled canal reads as the same substance
      as the body it came from.
- [ ] `fill_fluid_distinct` — excavations holding different fluids are distinguishable from
      each other by looking.
- [ ] `depth_and_fill_jointly_legible` — in one view, cells sharing a fill but differing in
      depth, and cells sharing a depth but differing in fill, are all distinguishable.

**The reservoir paying for it**
- [ ] `reservoir_fill_visibly_drops` (change) — after supplying a canal, an enclosed
      reservoir's visible liquid level is lower in the AFTER frame than in the BEFORE frame.
- [ ] `reservoir_shoreline_recedes` (change) — after supplying a canal, the far shoreline of
      a small enclosed pond has visibly receded.
- [ ] `empty_reservoir_stops_flow` (change) — once its enclosed reservoir is visibly empty, a
      canal's wet front stays where it was between two frames taken apart in time.
- [ ] `reservoir_recharge_progress_visible` (change) — a drawn-down reservoir left alone has
      visibly regained some liquid in the AFTER frame while still short of full.

**Defense**
- [ ] `canal_burning_reads_as_burning_liquid` — a lit flammable canal reads as the liquid
      surface itself alight, not as ordinary fire standing on ground.
- [ ] `canal_fire_reaches_reservoir` (change) — a connected flammable reservoir is unlit in
      the BEFORE frame and visibly alight in the AFTER frame, while the channel fire is still
      visible.
- [ ] `canal_fire_persists` (change) — the same liquid is still visibly alight in two frames
      labelled at least one in-game day apart.
- [ ] `canal_spent_after_burn` — a burned-out channel is visibly distinguishable from an
      unburned dry channel by scorching, reading as burned and empty rather than merely dry.
- [ ] `slime_reads_as_viscous_not_water` — slime shows a thick, opaque surface, never the look
      of recoloured water.
- [ ] `slime_occupant_below_surface` — a pawn caught in a slime canal is drawn sunk into the
      slime, not standing on its surface.

**Depth**
- [ ] `pit_depth_ladder_legible` — undug ground and excavations of depth one, two, three and
      four side by side are each distinguishable from the others by looking, without a
      tooltip.
- [ ] `pawn_height_ladder_legible` — pawns standing on undug ground and on each of the four
      depths sit progressively lower at every deeper step.
- [ ] `pawn_lowers_on_deeper_cell` (change) — the same pawn is drawn visibly lower relative to
      the rim in the AFTER frame, after moving onto a deeper cell.
- [ ] `pawn_rises_on_shallower_cell` (change) — the same pawn is drawn visibly higher in the
      AFTER frame, after moving onto a shallower cell.

**The pit — a superdeep excavation, empty**
- [ ] `pit_reads_as_hole` — a superdeep cell reads as a big dark hole at play zoom with labels
      hidden.
- [ ] `pit_walls_have_visible_depth` — an empty superdeep excavation shows wall faces
      descending from rim to floor, not a flat dark tile.
- [ ] `pit_not_vanilla_trap` — a superdeep excavation is visually distinct from vanilla's
      spike trap.
- [ ] `pit_reads_at_size` — a multi-cell superdeep area reads as one excavated place, not as
      a grid of identical tiles.

**The pit, occupied**
- [ ] `pit_occupant_below_floor` — an occupant of a superdeep cell reads as being down in
      the hole, not standing on top of it.
- [ ] `pit_occupied_distinguishable` — occupied and empty superdeep cells are
      distinguishable at a glance, with no tooltip and no click.
- [ ] `pit_trapped_reads_as_trapped` — the walls around a superdeep occupant rise visibly
      above the top of their head, by about a fifth of their height, so climbing out reads
      as impossible.

**The cover**
- [ ] `pit_covered_invisible` (change) — the same patch of ground looks the same at play zoom
      in the BEFORE frame (undug) and the AFTER frame (a covered superdeep excavation).
- [ ] `pit_covered_seam_at_max_zoom` — a covered superdeep excavation shows a slight seam or
      discoloration at maximum zoom, so the player who placed it can find it.

**The built half — ladders, sluice gates, spikes**
- [ ] `ladder_state_legible` — a raised ladder beside the rim is visibly distinguishable from
      the same ladder lowered into the excavation.
- [ ] `sluice_gate_state_legible` — a sluice gate open versus shut is visible without
      selecting it.
- [ ] `spikes_read_distinct` — at play zoom some part of the spikes is visibly projecting in a
      spiked cell, distinguishing it from a bare one before anything falls in.

⛔ **Irrigation has NO visual line, by ruling 36 (2026-09-17).** He was told the consequence is
a player who may irrigate for hours without perceiving that it works, and ruled the yield is
enough. **A future pass must not re-add an irrigation line as an oversight.**

### cannot show

- [ ] `never_liquid_on_open_ground` — liquid standing on undug ground outside both the
      reservoir and the channel.
- [ ] `never_gravel_path` — a channel that reads as a gravel road.
- [ ] `never_full_reservoir_after_heavy_draw` (change) — an enclosed reservoir whose fill looks
      untouched after filling a long canal.
- [ ] `never_snared_standing` — a pawn snared upright on a labelled tile, staring at the
      camera.
- [ ] `never_reads_as_building` — the bare excavation itself, apart from any ladder, gate or
      spikes in it, reads as a placed building sitting on the floor.

### candidate lines

**Empty by decision.** Resolved with him and not to be re-added:

- `limited_vs_limitless_legible` — **cut** by ruling 35. The classification is real in the
  simulation and shown nowhere.
- `source_exhausted_distinct_from_strained` — **cut.** Incoherent after ruling 34, which
  removed the source object and the strained state.
- `irrigated_ground_visibly_differs` — **cut** by ruling 36, above.
- `digsite_stage_legible` — **cut** with the staged dig-site chain the pit collapse retires.

### provenance

| bar | his words it distils |
|---|---|
| `canal_reads_as_dug_channel` | *"dig canals in the ground"* |
| `canal_dry_reads_as_obstacle` | *"an unfilled pit slows movement as per other established dug barriers"* |
| `filled_excavation_reads_as_obstacle` | *"filled pits reduce as per that terrain cost"*; *"all other flooded canal depths just slow you down more"* |
| `canal_partial_fill_distinct` | *"a graphic showing partial fill"* |
| `fill_tier_legible` | pit card round 3, 2026-09-17 — approved; strengthens `canal_partial_fill_distinct` (four states vs two), sits beside it because ids are frozen |
| `canal_fill_spreads_along_itself` | *"spread the water throughout themselves"* |
| `canal_fill_front_watchable` | *"at the liquid's viscosity (water is essentially zero)"*; promoted from candidate 2026-09-17 |
| `tar_fill_front_lags_water` | *"water is essentially zero"* viscosity against tar; split from `canal_fill_front_watchable` on GPT review |
| `canal_holds_only_the_channel` | *"flows into the canal to fill it"* |
| `canal_reads_as_same_liquid_as_reservoir` | *"extending the source"* |
| `fill_fluid_distinct` | pit card round 3 — approved; generalises `slime_reads_as_viscous_not_water`; half of the old Pits `fitting_reads_distinct` |
| `depth_and_fill_jointly_legible` | the depth ruling (*"All depths must be visually legible"*) held together with the four fill tiers |
| `reservoir_fill_visibly_drops` | *"the parent body of water reduces itself in proportion as well"*; ruling 34 makes it partial fill on a deeper cell |
| `reservoir_shoreline_recedes` | *"a small pond visibly shrinks at its far edge"*, split out of `reservoir_fill_visibly_drops` |
| `empty_reservoir_stops_flow` | *"Each source's square can supply up to five canal squares with liquid before it stops providing"* |
| `reservoir_recharge_progress_visible` | *"refilling slowly, from rain and season and ground liquids oozing in"* |
| `canal_burning_reads_as_burning_liquid` | *"the canals can be lit and burn for a very long time"* |
| `canal_fire_reaches_reservoir` | *"They will also light their source at that time"* |
| `canal_fire_persists` | *"burn for a very long time"* |
| `canal_spent_after_burn` | promoted from candidate 2026-09-17 so the defense use leaves a visible mark |
| `slime_reads_as_viscous_not_water` | *"so slippery that it is nearly impossible to cross"* |
| `slime_occupant_below_surface` | *"escape from the pit takes a great deal of time"*; his rejection of a pawn *"staring at the camera"* |
| `pit_depth_ladder_legible` | the depth ruling: *"All depths must be visually legible and differentiable graphically."* |
| `pawn_height_ladder_legible` | the depth ruling: *"They should be low enough that it is visually clear how they could not possibly climb out"* |
| `pawn_lowers_on_deeper_cell` | the depth ruling: *"The pawn should visibly rise up and lower down as they move over the depths."* |
| `pawn_rises_on_shallower_cell` | the same sentence, the other direction |
| `pit_reads_as_hole` | *"we need a big dark pit"*; ruling 33 *"walls with depth, not a flat tile"* |
| `pit_walls_have_visible_depth` | ruling 33 *"walls with depth, not a flat tile"*, split out of `pit_reads_as_hole` |
| `pit_not_vanilla_trap` | *"stuck in a trap with "Pit" written on it"* — reworded from the Pits walk to drop the building's texture path |
| `pit_reads_at_size` | Pits walk bar, strengthened from "fills its own footprint" to "one excavated place" |
| `pit_occupant_below_floor` | Pits walk bar; absorbs the Pits walk's `pitcell_occupant_visible` (same claim) |
| `pit_occupied_distinguishable` | Pits walk bar, "sprung pits" re-subjected to superdeep cells |
| `pit_trapped_reads_as_trapped` | pit card round 3, worded against the walls by his choice; the depth ruling's *"the walls are higher than their head by 20%"* |
| `pit_covered_invisible` | `design/Jawa/covered_pit_traps_spec.md` §3, 2026-08-30 |
| `pit_covered_seam_at_max_zoom` | *"a slight seam/discoloration at high zoom for the player's own eye"* |
| `ladder_state_legible` | *"A ladder nearby can be pulled up or lowered"*; half of the Pits walk's `pitcell_gate_state_legible` |
| `sluice_gate_state_legible` | *"A sluice gate also acts just like a door"*; the other half of `pitcell_gate_state_legible` |
| `spikes_read_distinct` | *"there should still be something showing their presence"*; half of the Pits walk's `fitting_reads_distinct` |
| `never_liquid_on_open_ground` | *"flows into the canal to fill it"* |
| `never_gravel_path` | the dug channel must not read as a road |
| `never_full_reservoir_after_heavy_draw` | conservation of mass made visible; his stock ruling |
| `never_snared_standing` | the defect that prompted the north-star system, kept verbatim from the Pits walk |
| `never_reads_as_building` | pit card round 3 — approved; the general form of `pit_not_vanilla_trap` |

## anti-guessing notes
- ✅ **The DRAFT banner that used to open `## north star` was false and is deleted** (2026-09-17).
  It said the checklist "has never bound" while `state: VALIDATED` sat three lines above it, and
  a note here instructed the reader ⛔ *not* to tidy it, because correcting it would revert his
  validation by hash mismatch. **Owner ruled that trade away the same day** — verbatim: *"Change
  no code — you just re-validate when prose is corrected."* So the banner was replaced with
  state-independent prose and he re-validated in the same sitting; `NORTHSTAR_HASH_SCOPE_1` is
  dropped, declined not deferred. 🔑 The general rule this leaves: **never leave false text
  standing inside a hashed section to protect a hash** — correct it and re-validate. And write
  only state-independent prose in there, so a state change cannot make the prose wrong.
- The live dig/fill/read surface is `jawa/flowworks_excavation_drive` (Deepen/TrySetDriverFill), `jawa/flowworks_excavation_report` (D/F, source/sink, map counters) and `jawa/flowworks_spawn_flood` in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksTools.cs`, plus the `jawa/static_call` read surfaces in the mod (`RM_PromotionProofs`, `RM_NorthstarProofs`, `RM_LiquidFireProof`, `RM_DigDiscoveryProof`, `RM_FluidIdentityProof`). `jawa/canal_dig` is a STUB since ruling 24 that always fails — never call it.
- 🔴 This walk USED TO CLAIM "No [S] line: nothing here is a visual-only concern". That claim was false and is deleted. MEASURED 2026-09-16: the mod ships **zero bespoke textures** — the dug channel borrows `Terrain/Surfaces/Gravel`, the test source borrows the drop-beacon sprite — so every state assertion above can pass while the player looks at gravel. That is exactly the defect class the north star system exists to catch (`design/RimMandrake/north_star_validation_spec.md`), and this walk was one of the 7 that dismissed the visual pass in writing.
- ✅ **The rename is complete and this walk carries the new name.** MEASURED 2026-09-17: file is `FlowWorks.md`, `subject:` reads `src/RimMandrake/FlowWorks`, `About.xml` declares `mandrake.rm.flowworks`, C# namespaces are `RimMandrake.FlowWorks.*`, def files are `FlowWorks_*.xml`. The six remaining "fluidcanal" strings in `src/` are the live defName `RM_FluidCanalFlood` (its ThingDef and DefOf agree, so it functions), three history comments, and a compiled DLL — none is owed work. A prior note here claimed this file was still `FluidCanals.md`; that was false and is deleted.
