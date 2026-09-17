# RimMandrake FlowWorks — validation walk
subject: src/RimMandrake/FlowWorks  (packageId `mandrake.rm.flowworks`)
deps: Ludeon.RimWorld.Odyssey (Flood is Odyssey-gated in the base game); none third-party
list: minimal+Odyssey     # official DLC, not a workshop mod; check it is in the active list
status-hint: dig a canal cell, let a fluid reservoir prime and then drip + re-flood adjacent terrain on two cadences — species/biome-agnostic engine, water is the one shipped fluid

⚠️ **This walk describes the mod as it stands TODAY and is scheduled for replacement.** Every
assertion below was verified against the code on 2026-09-16 and is accurate now — but
`FLOWWORKS_BUILD_PROGRAM_1` deletes `CompFluidReservoir` and `RM_FluidSpring_Test` (a source becomes a
SUPERDEEP cell, not a building) and drops the `Flood_FluidCanal` subclass, so the reservoir and flood
assertions here die with them. Rewrite this walk and `validation.py` in that program's Phase 9, against
the depth/fill primitive. Do not "fix" it earlier — until the build lands, this is the true description.

## must be true
- `RM_DigCanal` designation exists and `RM_DigCanalJob`/`RM_DigCanalWorkGiver` drive a colonist to actually dig it (`JobDriver_DigCanal`, `WorkGiver_DigCanal`).
- Digging a cell adjacent to a spring (`RM_FluidSpring_Test`, holds a `CompFluidReservoir` seeded with `RM_Fluid_Water`) triggers `CompFluidReservoir.Notify_CanalCellOpened` and spawns a `RM_FluidCanalFlood` (`Flood_FluidCanal`) that spreads `ShallowFloodwater` (temporary terrain layer) into adjacent open ground.
- The reservoir is a RATE, not a stock: `Prime()` fires one re-flood immediately and thereafter the comp releases a small drip and a rare large re-flood on two independent cadences, via `CompTickRare`, indefinitely. Read back on its own cell: `primed=True`, `fluid=RM_Fluid_Water`.
- At the three shipped Mod Settings defaults (`canalFlowEnabled=true`, `floodVolumeMultiplier=1.0`, `flowRateMultiplier=1.0`) the first re-flood's `remainingVolume` reads back `60.0` and `nextDripTick - nowTick` is exactly `2500`.
- A flooded cell's *underlying* terrain is recoverable — `TerrainGrid.TopTerrainAt` (what remains once the flood drains) must differ from the temporary flood terrain and must not itself be destroyed. `SpreadFlood` writes `SetTempTerrain` + `QueueRemoveTerrain`, never `SetTerrain`, and the flood terrains deliberately carry no `tempTerrain.destroysFloors`.
- A flood that is walled in before its volume runs out destroys itself at `ExpiryTick` = `spawnedTick + 2 * FloodingTicks` rather than ticking into every save.
- `RM_Channel_Empty` (the dug-channel terrain, Diggable/Walkable/Light affordances, not itself water) is what `canal_dig` sets a cell to.
- ⚠️ Spread is NOT channel-constrained: `Flood_FluidCanal` inherits vanilla `Flood`'s gating and spreads across any open, non-water, non-edifice ground, not along the dug channel. Recorded here because it is the engine's actual behaviour, and because the owner's 2026-09-16 design session assumes the opposite — see `design/RimMandrake/fluid_canals_mod_definition.md`.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.fluidcanals" and no XML error naming `FluidCanal_ThingDefs.xml`/`FluidCanal_Terrain.xml`/`FluidCanal_Fluids.xml`   # load-time
2. [D] def read-back: `RimMandrake.FluidCanals.FluidDef` `RM_Fluid_Water` exists; `floodTerrain` = `ShallowFloodwater`; `volumePerTile` = 1; `ticksPerTile` = 60; `floodedTicks` = 300000
3. [D] def read-back: `TerrainDef` `RM_Channel_Empty` exists; `affordances` contains `Diggable`; `natural` = true
4. [D] def read-back: `ThingDef` `RM_FluidSpring_Test` exists; its `CompProperties_FluidReservoir` comp has `fluidDef` = `RM_Fluid_Water`, `dripVolume` = 3, `dripIntervalTicks` = 2500, `reFloodVolume` = 60, `reFloodIntervalTicks` = 180000
5. [B] jawa/spawn_batch (or jawa/list_things) `defName=RM_FluidSpring_Test` to place a spring on the current map at a known cell, then `jawa/canal_dig {x,z}` on the cell adjacent to it → expect result names `mapId`/`mapTile` and no error
6. [B] jawa/canal_cell_report `{x,z}` on the dug cell, immediately after step 5 → expect `terrain=RM_Channel_Empty`
7. [B] jawa/canal_cell_report on a cell one step further from the spring, polled again after some ticks (advance via `rimworld/execute_debug_action` if a "pass time" hook is needed) → expect `tempTerrain=ShallowFloodwater`, `underneath=` the original (pre-flood) terrain defName, and a `[flood ... remainingVolume=...]` block with `remainingVolume` decreasing toward 0
8. [B] jawa/canal_cell_report on the spring's own cell after step 5 → expect a `[reservoir ...]` block reading `primed=True`, `fluid=RM_Fluid_Water`, and `nextDripTick` ahead of `nowTick` by exactly 2500
9. [S] LOOK at the dug channel and the flooded cells at play zoom: the channel reads as a dug channel rather than a gravel path, flooded cells read as the liquid they hold, and a partly-filled canal is distinguishable from a full one

## north star
state: VALIDATED
validated-hash: 4899e58a892ef1f86374562d1b049a8ba1ebf4a15e922cd7c77707dc2b725fb0

⚠️ **DRAFT — not a bar until the owner validates it** with
`modcheck validate FlowWorks --owner-said "…"`. Per
`design/RimMandrake/north_star_validation_spec.md` a DRAFT checklist cannot fail a mod
and cannot green one. Every `### must show` line below is distilled from his own words and
adds no claim of its own; each names the phrase it came from.

✅ **WALKED WITH HIM 2026-09-17** — the whole checklist read back to him line by line, which
produced rulings 34-36 (`flowworks_mod_definition.md` §25) and **deleted three lines rather
than adding any**. What changed, so nobody restores a line he cut:

- **The two source lines are gone.** Ruling 34: *"Strained isn't a thing anymore."* A reservoir
  is deep filled terrain, so a drawn-down reservoir is partial fill on a deeper cell — the same
  art as a partly filled channel. One line survives in its place, reframed.
- **The irrigation line is gone.** Ruling 36: the yield is enough, and neither soil nor plants
  need a watered look. This reverses what this walk and the mod definition both used to call the
  visual the whole irrigation motivation rested on.
- **Two candidates were promoted to real bars** — the fill front and the spent channel — and the
  other two were dropped, so `### candidate lines` is now empty by resolution rather than by
  neglect.
- ⚠️ **Ids were renamed** where they said "source" (now "reservoir"). Permitted only because this
  checklist is DRAFT and has never bound; §1's never-reuse-an-id rule applies from validation
  onward.

### the experience  (OWNER'S WORDS — verbatim, bench session 2026-09-16)

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

His ranking the same session, which decides what gets tuned until it feels right:
**defense first, then irrigation, then industry, and finally terraforming.** And his
scarcity ruling: **every source is stock**, refilling *"slowly, from rain and season and
ground liquids oozing in… it can take quite a while to fill up from a very small natural
source."*

2026-09-17, asked why no line covered pumping when his own description said the strained graphic
would be reused for it — **the answer retired the concept instead**:

> *"Strained isn't a thing anymore. We replaced 'sources' with just placed deep liquid reservoirs
> just like a player would normally place on the map. Filled very deep tiles. Everything follows
> from that."*

🔑 The through-line: **a canal is the reservoir, moved.** What the player digs becomes part of the
body it came from — it holds the same liquid, it costs that body volume to fill, and the body
shows the cost.

🔑 And after ruling 34 the through-line has one mechanism instead of two: **a reservoir and a canal
are the same thing at different depths.** Both are excavated cells carrying a depth and a fill, so
"the body shows the cost" is not a separate graphic — it is the fill level dropping, which is the
line the channel already has. Every deleted line above was deleted because this collapsed two art
systems into one.

### must show

**The channel itself**
- [ ] `canal_reads_as_dug_channel` — a dug channel reads as excavated ground with walls, not
      as a path or a floor. From *"dig canals in the ground"*; it borrows
      `Terrain/Surfaces/Gravel` today.
- [ ] `canal_dry_reads_as_obstacle` — an unfilled channel is legible as something that
      impedes crossing, without a tooltip. From *"an unfilled pit slows movement as per other
      established dug barriers"*.

**Fill**
- [ ] `canal_partial_fill_distinct` — a partly filled canal is distinguishable at a glance
      from a full one. From *"a graphic showing partial fill"*.
- [ ] `canal_fill_spreads_along_itself` — the liquid in an incompletely filled canal is
      spread through the channel rather than pooled in the cell it entered. From *"spread the
      water throughout themselves"*.
- [ ] `canal_fill_front_watchable` (change) — the arriving liquid has a visible fill front, so
      viscosity is something you watch rather than infer: water almost at once, tar creeping.
      **Promoted from candidate to bar 2026-09-17.** Judging it needs two frames rather than
      one; that cost was stated and accepted. ⚠️ It was recorded here as the only such line on the
      list, which was wrong — `reservoir_fill_visibly_drops` and `never_full_reservoir_after_heavy_draw`
      are the same shape, and all three are declared `(change)` per spec §4b.
- [ ] `canal_holds_only_the_channel` — the liquid is inside the dug channel and not standing
      on open ground beside it. From *"flows into the canal to fill it"*.
      ✅ **MEASURED 2026-09-17: this is now BUILT and expected to PASS**, reversing this line's
      previous note that it must fail. `Flood_FlowWorks.CanFloodInto` gates on
      `RM_MapComponent_Excavation.CanLiquidEnter`, behind the `channelConfinementEnabled`
      setting, which defaults to **true** (`RimMandrakeFlowWorksMod.cs:43`). A player who turns
      that setting off is choosing the old behaviour and is not a failure of this line.
- [ ] `canal_reads_as_same_liquid_as_reservoir` — a filled canal reads as the same substance as
      the body it came from. From *"extending the source"*.

**The reservoir paying for it**
- [ ] `reservoir_fill_visibly_drops` (change) — after supplying a canal, the reservoir is visibly less
      full, and a small pond visibly shrinks at its far edge. From *"the parent body of water
      reduces itself in proportion as well"*. 🔑 Ruling 34 makes this the **same art as
      `canal_partial_fill_distinct`** on a deeper cell, so it demands nothing new to draw —
      which is why the two strained-source lines it replaces could be deleted outright.

**Defense**
- [ ] `canal_burning_reads_as_burning_liquid` — a lit flammable canal reads as the liquid
      surface itself alight, not as ordinary fire standing on ground. From *"the canals can be
      lit and burn for a very long time"*.
- [ ] `canal_fire_reaches_reservoir` — fire is visibly present at the reservoir, not only in
      the channel. From *"They will also light their source at that time"*.
- [ ] `canal_spent_after_burn` — a burned-out channel reads as scorched and empty, not merely
      dry. **Promoted from candidate to bar 2026-09-17**, so the defense use he ranked first
      leaves a visible mark afterwards. Costs a third channel state to art, on top of dry and
      filled; he took it while declining the matching exhausted-reservoir state, which is
      consistent with ruling 34 — there is no reservoir object to be exhausted.
- [ ] `slime_reads_as_viscous_not_water` — slime reads as opaque and viscous, never as tinted
      water. From *"so slippery that it is nearly impossible to cross"*.
- [ ] `slime_occupant_below_surface` — a pawn caught in a slime canal is not drawn standing on
      the surface. Kin to Pits' `pit_occupant_below_floor`; his standing rejection of a pawn
      *"staring at the camera"* is the same defect.

⛔ **Irrigation has NO visual line, by ruling 36 (2026-09-17).** There used to be one here —
`irrigated_ground_visibly_differs`, called "the whole irrigation motivation rests on this being
visible." He was told the consequence is a player who may irrigate for hours without perceiving
that it works, and ruled the yield is enough. Irrigation is still second in the motivation
ranking and still tuned; it is simply not drawn, and **a future pass must not re-add this line
as an oversight.**

### cannot show

- [ ] `never_liquid_on_open_ground` — liquid standing on open ground the player never dug.
      ⚠️ Was described here as "the current engine's actual behaviour"; that is **no longer
      true** as of the channel-confinement measurement above, so this absolute now guards a fixed
      behaviour against regression rather than describing a live defect.
- [ ] `never_gravel_path` — a channel that reads as a gravel road.
- [ ] `never_full_reservoir_after_heavy_draw` (change) — a reservoir whose fill looks untouched after
      filling a long canal, which would make conservation of mass invisible and the stock ruling
      pointless.

### candidate lines

**Empty — all four were resolved with him on 2026-09-17, none left parked.** Recorded so the
absence reads as a decision:

- `canal_fill_front_watchable` — **promoted** to a bar.
- `canal_spent_after_burn` — **promoted** to a bar.
- `limited_vs_limitless_legible` — **cut** by ruling 35. The classification stays real in the
  simulation and is shown nowhere; do not re-add an indicator as a usability fix.
- `source_exhausted_distinct_from_strained` — **cut.** Incoherent after ruling 34, which removed
  both the source object and the strained state it was to be distinguished from.

## anti-guessing notes
- 🔴 **The `## north star` section still opens with a DRAFT banner and still says the checklist
  "has never bound". Both are FALSE as of 2026-09-17** — he validated it (`state: VALIDATED`,
  hash `4899e58a…`, 13 must-show + 3 cannot-show binding). The false text is left standing
  **deliberately**: the recorded hash covers the whole section including its prose, so correcting
  those two sentences would revert his validation to DRAFT by mismatch and silently stop the mod
  being refused. This note lives out here because everything above `## anti-guessing notes` is
  inside the hashed region. It is the exact defect `NORTHSTAR_HASH_SCOPE_1` describes — hash the
  bars, not the commentary — and it can only be fixed by that item, or by him re-validating after
  the edit. ⛔ Do not "tidy" the banner; that is the trap, not the fix.
- `jawa/canal_dig` and `jawa/canal_cell_report` are cited verbatim from `Transient/bench_tools_dump.json`; both note the mod's own gizmo/dev-menu equivalents "never register live" (FLUID_CANAL_DEBUG_SURFACE_1), so these two ARE the only live-reachable surface — no separate `rimworld/execute_debug_action` route exists for this mod's report/dig actions.
- 🔴 This walk USED TO CLAIM "No [S] line: nothing here is a visual-only concern". That claim was false and is deleted. MEASURED 2026-09-16: the mod ships **zero bespoke textures** — the dug channel borrows `Terrain/Surfaces/Gravel`, the test source borrows the drop-beacon sprite — so every state assertion above can pass while the player looks at gravel. That is exactly the defect class the north star system exists to catch (`design/RimMandrake/north_star_validation_spec.md`), and this walk was one of the 7 that dismissed the visual pass in writing.
- Step 4 used to assert `volume` = 60 on the comp. **There is no `volume` field.** MEASURED 2026-09-16 from `Defs/ThingDefs/FluidCanal_ThingDefs.xml:51-57`: the comp is configured with `fluidDef`, `dripVolume` 3, `dripIntervalTicks` 2500, `reFloodVolume` 60, `reFloodIntervalTicks` 180000. The 60 that line was reaching for is `reFloodVolume`.
- 🔴 **That comp no longer exists, so every step written against it is owed a rebuild.** MEASURED 2026-09-17: `CompFluidReservoir` is gone from disk — the only four remaining mentions in `src/RimMandrake/FlowWorks/` are comments recording its deletion, so ruling 24 was executed cleanly and there is no build break. But ruling 24 warned that "the validator and the walk must be rebuilt against the new primitive, and until they are, this mod has no live proof at all", and **that rebuild has not happened in this walk's `[D]` steps.** The new primitive is `RM_ExcavationDepth`'s depth/fill pair on `RM_MapComponent_Excavation`, with stock in `RM_LiquidStock` and body classification in `RM_LiquidBody`.
- ⚠️ **This walk is filed under the mod's old name.** The mod is `FlowWorks` (`mandrake.rm.flowworks`) and was renamed on disk 2026-09-16; this file is still `FluidCanals.md` and its `subject:` line should be checked against `src/RimMandrake/FlowWorks/`. Not renamed in this pass because the owner chose the checklist walk-through over the naming sweep — `STALE_RENAME_GATE_SWEEP_1`.
