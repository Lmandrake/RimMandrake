# Review request: FlowWorks north-star checklist (you stand in for the owner's read)

You are reviewing a **north-star checklist** for a RimWorld mod, FlowWorks (canals dug from
liquid bodies, a depth 0-4 / fill primitive per cell, and pits that are simply superdeep
cells). The owner asked for "the comprehensive one" and for you to review it in place of his
own read. Act as his proxy: a demanding player-designer who wants every bar to be something a
person can check by LOOKING at a screenshot.

How the bars are used: each `must show` bar is put, verbatim, as a YES/NO question to a vision
judge looking at ONE screenshot (bars marked `(change)` get a labelled before|after diptych).
A `cannot show` bar passes when the judge answers NO. Bars for unbuilt features are kept on
purpose: they fail until the feature is built, and that is correct, not a defect.

Rules already decided — do NOT relitigate:
- No irrigation visual bar (owner ruling 36). No limited/limitless indicator (ruling 35).
- Bar ids already validated are frozen and may not be renamed or reused.
- Unbuilt-feature bars stay bound (owner: comprehensive).
- The depth ruling and spike/camera ruling are his verbatim words and must be honoured.

Review for, bar by bar where relevant:
1. Observable — can a judge decide it from a screenshot (or the diptych) alone, with no tooltip,
   no code, no state read?
2. Falsifiable — is there a concrete screenshot that would answer NO?
3. Non-overlapping — do two bars test the same thing? Is any bar compound (two claims in one)?
4. No implementation detail in bar text.
5. Missing player expectations — anything his quoted words promise that no bar covers?
6. Unmeetable bars — anything no art or code could ever satisfy, or that contradicts another bar.

Answer as a numbered list of findings. Each: bar id(s), problem, concrete replacement wording or
"add bar: `<id>` — <text>". Be terse. Finish with a one-line overall verdict.

---

## The checklist under review
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
- [ ] `canal_reads_as_dug_channel` — a dug channel reads as excavated ground with walls, not
      as a path or a floor.
- [ ] `canal_dry_reads_as_obstacle` — an unfilled channel is legible as something that
      impedes crossing, without a tooltip.

**Fill**
- [ ] `canal_partial_fill_distinct` — a partly filled canal is distinguishable at a glance
      from a full one.
- [ ] `fill_tier_legible` — dry, trace, half and brimming fill in excavations of the same
      depth are distinguishable from each other by looking.
- [ ] `canal_fill_spreads_along_itself` — the liquid in an incompletely filled canal is
      spread through the channel rather than pooled in the cell it entered.
- [ ] `canal_fill_front_watchable` (change) — the arriving liquid has a visible fill front
      that advances along the channel, and tar's front is visibly behind water's after the
      same time.
- [ ] `canal_holds_only_the_channel` — the liquid is inside the dug channel and not standing
      on open ground beside it.
- [ ] `canal_reads_as_same_liquid_as_reservoir` — a filled canal reads as the same substance
      as the body it came from.
- [ ] `fill_fluid_distinct` — excavations holding different fluids are distinguishable from
      each other by looking.

**The reservoir paying for it**
- [ ] `reservoir_fill_visibly_drops` (change) — after supplying a canal, the reservoir is
      visibly less full, and a small pond visibly shrinks at its far edge.

**Defense**
- [ ] `canal_burning_reads_as_burning_liquid` — a lit flammable canal reads as the liquid
      surface itself alight, not as ordinary fire standing on ground.
- [ ] `canal_fire_reaches_reservoir` — fire is visibly present at the reservoir, not only in
      the channel.
- [ ] `canal_spent_after_burn` — a burned-out channel reads as scorched and empty, not
      merely dry.
- [ ] `slime_reads_as_viscous_not_water` — slime reads as opaque and viscous, never as
      tinted water.
- [ ] `slime_occupant_below_surface` — a pawn caught in a slime canal is drawn sunk into the
      slime, not standing on its surface.

**Depth**
- [ ] `pit_depth_ladder_legible` — surface, shallow, mid, deep and superdeep excavations
      side by side are each distinguishable from the others by looking, without a tooltip.
- [ ] `pawn_rises_and_lowers_with_depth` (change) — a pawn walking across excavations of
      different depths is drawn visibly lower on each deeper cell and higher again as it
      climbs back out.

**The pit — a superdeep excavation, empty**
- [ ] `pit_reads_as_hole` — a superdeep cell reads as a dark hole you would fall into, with
      walls that have depth, at play zoom with labels hidden.
- [ ] `pit_not_vanilla_trap` — nothing in the excavation family reads as vanilla's spike
      trap.
- [ ] `pit_reads_at_size` — a multi-cell superdeep area reads as one excavated place, not as
      a grid of identical tiles.

**The pit, occupied**
- [ ] `pit_occupant_below_floor` — an occupant of a superdeep cell reads as being down in
      the hole, not standing on top of it.
- [ ] `pit_occupied_distinguishable` — occupied and empty superdeep cells are
      distinguishable at a glance, with no tooltip and no click.
- [ ] `pit_trapped_reads_as_trapped` — a superdeep occupant reads as unable to get out
      because the walls around them stand visibly higher than their head, by about a fifth
      of their height.

**The cover**
- [ ] `pit_covered_invisible` — a covered superdeep excavation is invisible at play zoom,
      matching the surrounding terrain.
- [ ] `pit_covered_seam_at_max_zoom` — a covered superdeep excavation shows a slight seam or
      discoloration at maximum zoom, so the player who placed it can find it.

**The built half — ladders, sluice gates, spikes**
- [ ] `ladder_state_legible` — an excavation with a ladder lowered into it is
      distinguishable from one without, by looking at the excavation.
- [ ] `sluice_gate_state_legible` — a sluice gate open versus shut is visible without
      selecting it.
- [ ] `spikes_read_distinct` — a spiked cell is distinguishable from a bare one at play
      zoom before anything falls in.

⛔ **Irrigation has NO visual line, by ruling 36 (2026-09-17).** He was told the consequence is
a player who may irrigate for hours without perceiving that it works, and ruled the yield is
enough. **A future pass must not re-add an irrigation line as an oversight.**

### cannot show

- [ ] `never_liquid_on_open_ground` — liquid standing on open ground the player never dug.
- [ ] `never_gravel_path` — a channel that reads as a gravel road.
- [ ] `never_full_reservoir_after_heavy_draw` (change) — a reservoir whose fill looks
      untouched after filling a long canal.
- [ ] `never_snared_standing` — a pawn snared upright on a labelled tile, staring at the
      camera.
- [ ] `never_reads_as_building` — an excavation that reads as a placed building sitting on
      the floor.

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
| `canal_partial_fill_distinct` | *"a graphic showing partial fill"* |
| `fill_tier_legible` | pit card round 3, 2026-09-17 — approved; strengthens `canal_partial_fill_distinct` (four states vs two), sits beside it because ids are frozen |
| `canal_fill_spreads_along_itself` | *"spread the water throughout themselves"* |
| `canal_fill_front_watchable` | *"at the liquid's viscosity (water is essentially zero)"*; promoted from candidate 2026-09-17 |
| `canal_holds_only_the_channel` | *"flows into the canal to fill it"* |
| `canal_reads_as_same_liquid_as_reservoir` | *"extending the source"* |
| `fill_fluid_distinct` | pit card round 3 — approved; generalises `slime_reads_as_viscous_not_water`; half of the old Pits `fitting_reads_distinct` |
| `reservoir_fill_visibly_drops` | *"the parent body of water reduces itself in proportion as well"*; ruling 34 makes it partial fill on a deeper cell |
| `canal_burning_reads_as_burning_liquid` | *"the canals can be lit and burn for a very long time"* |
| `canal_fire_reaches_reservoir` | *"They will also light their source at that time"* |
| `canal_spent_after_burn` | promoted from candidate 2026-09-17 so the defense use leaves a visible mark |
| `slime_reads_as_viscous_not_water` | *"so slippery that it is nearly impossible to cross"* |
| `slime_occupant_below_surface` | *"escape from the pit takes a great deal of time"*; his rejection of a pawn *"staring at the camera"* |
| `pit_depth_ladder_legible` | the depth ruling: *"All depths must be visually legible and differentiable graphically."* |
| `pawn_rises_and_lowers_with_depth` | the depth ruling: *"The pawn should visibly rise up and lower down as they move over the depths."* |
| `pit_reads_as_hole` | *"we need a big dark pit"*; ruling 33 *"walls with depth, not a flat tile"* |
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


---

## Context: the trial plan's bar tables (how each bar is staged and expected today)

### 2.3 The canal bars (13 must + 3 cannot, VALIDATED, ids frozen)

| bar | asserts | setup → state predicates (state half) | shot | live/offline | expected today |
|---|---|---|---|---|---|
| `canal_reads_as_dug_channel` | dug channel reads as excavated ground with walls | Plot A: dig a 1×8 run at D=1 on Soil. Expect report `D=1`, `isExcavated=true`, terrain `RM_Channel_Empty`, F=0. | play zoom, run + 3-cell margin | live | **NO** (Gravel texture) |
| `canal_dry_reads_as_obstacle` | unfilled channel legible as impeding crossing | Same plot as above (shared component allowed: one shot, two `shows`). State: the effective `pathCost` of a D=1 dry cell **equals the ruled 30** (build program Phase 5) — not merely "more than soil" (GPT #34) — plus a timed traversal: a colonist ordered across 8 dug cells takes measurably longer than across 8 soil cells. Expected FAIL today (shipped 6). | same shot | live + `[D]` def read | NO |
| `canal_partial_fill_distinct` | partly filled vs full distinguishable | Plot B: two parallel 1×6 runs at D=3; fill run 1 to F=1, run 2 to F=3 via `setFill`; set `depthEngineEnabled=false` **for this component only** so the pulse cannot equalise them, read back F per cell, restore setting after. | play zoom, both runs in frame | live | NO/UNCERTAIN (tinted ramps may differ) |
| `canal_fill_spreads_along_itself` | liquid spreads through the channel, not pooled at entry | Plot C: limitless reservoir strip on the map edge; dig a 1×10 D=1 channel from it. Step pulses until settled (budget 20 pulses = 5,000 ticks). Predicate: mouth cell F≥1, every channel cell F≥1, no dry gap between wet cells, and settled inside budget — the old "monotone" fallback is struck because an all-dry channel satisfies it (GPT #35). The source is limitless, so no budget can legitimately run out. | play zoom, after settle | live | state PASS; visual UNCERTAIN |
| `canal_fill_front_watchable` (change) | visible fill front; water near-instant, tar creeping | Plot C, frames at pulse 1 and pulse 3 → diptych. For the tar half: a four-panel composite water/tar × pulse 1/pulse 3 from two working copies of the golden save with identical geometry, `ActiveFluid` set and verified **before first classification**, plus a machine-checked state delta: tar's wet front at pulse 3 is strictly shorter than water's (GPT #31). | diptych | live | **BLOCKED** — depth engine has no viscosity (MEASURED), so tar fills at water's rate; expected NO |
| `canal_holds_only_the_channel` | liquid inside the channel, not on open ground beside it | Plot C after settle. Predicate: every cell in the 1-cell ring around the channel has `D=0`, `tempTerrain=none`, terrain unchanged from the pre-dig snapshot. Toggle `channelConfinementEnabled` (default true). | play zoom | live | state PASS expected (MEASURED built) |
| `canal_reads_as_same_liquid_as_reservoir` | filled canal reads as the same substance as its body | Plot C after settle, reservoir + mouth + channel in one frame. | play zoom | live | UNCERTAIN |
| `reservoir_fill_visibly_drops` (change) | reservoir visibly less full after supplying; small pond shrinks at far edge | Plot D: **limited** pond, 5×5 natural `WaterShallow`, ≥10 cells from every edge and every other plot. Snapshot body stock + pond cells. Dig a 1×12 D=3 channel from it; step until settled (budget 40 pulses). Predicates: stock decreased by Σ F × volumePerTile (conservation ±1); `recessionEnabled` → ≥1 pond cell now dry (`underneath` = original, `isSourceCell=false`). Frames before/after → diptych. | diptych | live | state PASS likely; visual NO (no reduced-pond art) |
| `canal_burning_reads_as_burning_liquid` | lit flammable canal reads as liquid surface alight | Plot E on a **fresh working copy** with `ActiveFluid=RM_Fluid_Tar` set before first classification, `liquidIgnitionEnabled=true` (non-default). Fill 1×8 D=1 channel from a limited tar pond; ignite the mouth cell (driver: `ignite_cell`). Poll every 60 ticks up to 1,200. Predicate: the recorded ignited-cell set grows to ≥3 channel cells, N=3 repetitions with distinct ignition cells, pass on 3/3 (GPT #39). Which cells are *eligible* to hold Fire (channel fill terrain vs natural pond terrain) is read from `LiquidIgnition.cs` before wiring, not assumed. Fire-safety isolation: 8-cell non-flammable (bare Soil, plants wiped) moat round the plot; `jawa/clear_area` of plants first. | play zoom | live | UNCERTAIN (ignition premise UNMEASURED — build program Phase 6 flags `About.xml`'s "vanilla ignition already works" as unverified prose) |
| `canal_fire_reaches_reservoir` | fire present at the reservoir, not only the channel | Plot E continued, poll until a reservoir cell has Fire (budget 6,000 ticks), 3/3. | play zoom incl. pond | live | UNCERTAIN |
| `canal_spent_after_burn` | burned-out channel reads scorched and empty, not merely dry | Plot E, poll until no Fire in plot (budget 60,000 ticks — burn is "one canal tier per day"). "Burned cell" = a cell in the recorded ignited set. Predicate: every burned cell F=0 and still excavated (D unchanged). | play zoom | live | NO (no third channel state art) |
| `slime_reads_as_viscous_not_water` | slime opaque and viscous, never tinted water | Plot F, fresh working copy, `ActiveFluid=RM_Fluid_SlimeGreen` set and read back before any fill, fill terrain asserted to be the slime fill def (not the water ramp) after a forced redraw (GPT #38), then fill a 1×6 D=1 channel by `setFill`. Water control channel would need a second fluid on the same map — impossible today; the control is a stored reference PNG of the water fill from Plot C. | play zoom | live | UNCERTAIN |
| `slime_occupant_below_surface` | pawn in a slime canal not drawn standing on the surface | Plot F, D=3 slime run; spawn a colonist ADJACENT and order it into the middle cell so it makes a real cell transition (no teleport — GPT #24); step ≤300 ticks; predicate pawn position is in the run. | play zoom, pawn centred | live | **NO** (no depth draw offset) |
| `never_liquid_on_open_ground` (cannot) | no liquid standing on undug ground | Claimed by the Plot C component (photographing exactly where the defect would appear). | same as Plot C | live | PASS expected |
| `never_gravel_path` (cannot) | channel never reads as a gravel road | Claimed by Plot A. | Plot A shot | live | **FAIL expected** (it IS Gravel) |
| `never_full_reservoir_after_heavy_draw` (change, cannot) | reservoir fill never looks untouched after a long canal | Plot D diptych. | diptych | live | FAIL likely (no reduced art) |

### 2.4 The pit bars — the Pits-walk fold

🔴 **Do not move the 11+1 Pits bars as they stand** (`PIT_SUPERDEEP_COLLAPSE_1`, the item is
authority over the spec): several are claims about a Building, and the pit is now a SUPERDEEP cell.
The item records his third-card-round rulings, which change the roster. What goes to him for
re-validation, as **proposed text** (§7) inside FlowWorks.md's `## north star` under a new
`**The pit — a superdeep excavation**` group:

| proposed id | source | binding | expected today |
|---|---|---|---|
| `pit_reads_as_hole` | kept, re-subjected ("approved in substance") | Plot G: dig a 3×3 D=4 area; shot at play zoom, labels hidden | NO (Gravel) |
| `pit_not_vanilla_trap` | rewritten — drop "own texture path", keep the claim | Plot G shot; plus `[D]` offline: no FlowWorks def `texPath` = `Things/Building/Security/TrapSpikeArmed` (today 3 → FAIL) | FAIL |
| `pit_reads_at_size` | kept, strengthened (flag to him) | Plot G | NO |
| `pit_depth_ladder_legible` | 🆕 approved + strengthened by his depth ruling | Plot H: five adjacent 2×3 pads at D=0..4 in one row; then a colonist walked across all five with `superdeepCaptureEnabled=false` for this component only, so it is not captured on D=4 before the frame (GPT #25); frames at D=1 and D=4 → diptych for "rises and lowers". Capture is tested separately in Plot G at defaults. | **NO** (one Gravel texture for every depth; no draw offset) |
| `pit_occupant_below_floor` | kept; absorbs `pitcell_occupant_visible` (merge, flag) | Plot G: hostile-faction pawn spawned 3 cells off the lip and force-moved across it (a real cell transition — placing a pawn ON the cell may bypass the entry detector, GPT #24); predicate superdeep capture (`superdeepCaptureEnabled`) — pawn despawned into the hidden `RM_SuperdeepPit` holder. Ruling: superdeep traps *absolutely*, so the threshold is **3/3** over three spawns, never "most" | NO |
| `pit_occupied_distinguishable` | kept | Plot G occupied vs Plot G′ empty in one frame | NO |
| `pit_trapped_reads_as_trapped` | 🆕 approved, worded against the walls | Plot G occupied | NO |
| `pit_covered_invisible` / `pit_covered_seam_at_max_zoom` | kept | **BLOCKED** — no superdeep cover exists | UNJUDGEABLE until built |
| `ladder_state_legible` | rehoused from `pitcell_gate_state_legible` (split, flag) | Plot G with/without `RM_Ladder` | UNCERTAIN |
| `sluice_gate_state_legible` | rehoused (split, flag) | **BLOCKED** — `FLOWWORKS_DOOR_FAMILY_1` unbuilt | — |
| `fill_tier_legible` | 🆕 approved — strengthens `canal_partial_fill_distinct` (4 states vs 2) | Plot B extended to four runs F=0..3 at D=3 | NO/UNCERTAIN |
| `fill_fluid_distinct` | 🆕 approved — generalises `slime_reads_as_viscous_not_water` | **BLOCKED** — fluid is per-MAP today; the bar compares two fluids side by side, which cannot be staged on one map | — |
| `spikes_read_distinct` | 🆕 approved, with his camera constraint | **BLOCKED** — per-cell spikes unbuilt | — |
| `never_snared_standing` (cannot) | kept verbatim | Plot G occupied shot | FAIL likely |
| `never_reads_as_building` (cannot) | 🆕 approved | Plot G | FAIL likely while 3 defs use TrapSpikeArmed |

**Deleted, not carried:** `digsite_stage_legible` (its referent, the `RM_PitDigSite_*` chain, retires).
`fitting_reads_distinct` splits into `fill_fluid_distinct` + `spikes_read_distinct`.

⚠️ A bar that cannot be evaluated must not be filed as a binding bar (the spec's own rule). The
BLOCKED rows above go to him **marked as blocked**, with the choice: validate now and accept REFUSED
until built, or park them as `### candidate lines` until their feature lands. That is his call, so it
is a question in the re-validation item, not a decision here.

