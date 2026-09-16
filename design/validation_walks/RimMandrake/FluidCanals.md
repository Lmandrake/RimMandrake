# RimMandrake Fluid Canals — validation walk
subject: src/RimMandrake/FluidCanals  (packageId `mandrake.rm.fluidcanals`)
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
state: DRAFT
validated-hash:

⚠️ **DRAFT — not a bar until the owner validates it** with
`modcheck validate FluidCanals --owner-said "…"`. Per
`design/RimMandrake/north_star_validation_spec.md` a DRAFT checklist cannot fail a mod
and cannot green one. Every `### must show` line below is distilled from his own words of
2026-09-16 and adds no claim of its own; each names the phrase it came from. Lines that
are an agent's inference sit in `### candidate lines` instead, where they cannot bind.

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

🔑 The through-line: **a canal is the source, moved.** What the player digs becomes part of
the body it came from — it holds the same liquid, it costs that body volume to fill, and the
body shows the cost.

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
- [ ] `canal_holds_only_the_channel` — the liquid is inside the dug channel and not standing
      on open ground beside it. From *"flows into the canal to fill it"*; today's flood is not
      channel-constrained, so this line is expected to FAIL until that is fixed.
- [ ] `canal_reads_as_same_liquid_as_source` — a filled canal reads as the same substance as
      the body it came from. From *"extending the source"*.

**The source paying for it**
- [ ] `source_strained_state_visible` — a drawn-down source is visibly strained, distinct
      from a full one, at a glance. From *"a reduced graphic for the parent water source to
      show that it is strained"*.
- [ ] `source_body_recedes_visibly` — the parent body is visibly smaller after supplying a
      canal. From *"the parent body of water reduces itself in proportion as well"*.

**Defense**
- [ ] `canal_burning_reads_as_burning_liquid` — a lit flammable canal reads as the liquid
      surface itself alight, not as ordinary fire standing on ground. From *"the canals can be
      lit and burn for a very long time"*.
- [ ] `canal_fire_reaches_source` — fire is visibly present at the source, not only in the
      channel. From *"They will also light their source at that time"*.
- [ ] `slime_reads_as_viscous_not_water` — slime reads as opaque and viscous, never as tinted
      water. From *"so slippery that it is nearly impossible to cross"*.
- [ ] `slime_occupant_below_surface` — a pawn caught in a slime canal is not drawn standing on
      the surface. Kin to Pits' `pit_occupant_below_floor`; his standing rejection of a pawn
      *"staring at the camera"* is the same defect.

**Irrigation**
- [ ] `irrigated_ground_visibly_differs` — ground and plants beside a filled canal are
      visibly different from the same ground away from it. From *"all plants nearby the canal
      react to the presence of the water as though watered"* — the whole irrigation motivation
      rests on this being visible.

### cannot show

- [ ] `never_liquid_on_open_ground` — liquid standing on open ground the player never dug. This
      is the current engine's actual behaviour and the most likely thing a screenshot catches.
- [ ] `never_gravel_path` — a channel that reads as a gravel road.
- [ ] `never_full_source_after_heavy_draw` — a source that looks untouched after filling a long
      canal, which would make conservation of mass invisible and the stock ruling pointless.

### candidate lines  (AGENT-INFERRED — not his words, and they bind nothing while they sit here)

Promote any of these into `### must show` before validating, or delete them.

- `limited_vs_limitless_legible` — the player can tell a limited source from a limitless one
  before committing labor. He ruled every source is stock, so this may not need to be visible
  at all.
- `canal_fill_front_watchable` — the arriving liquid has a visible fill front, so viscosity is
  something you watch rather than infer. Motion is hard to judge from one screenshot.
- `canal_spent_after_burn` — a burned-out channel reads as scorched and empty.
- `source_exhausted_distinct_from_strained` — a third source state for empty, distinct from
  strained.

## anti-guessing notes
- `jawa/canal_dig` and `jawa/canal_cell_report` are cited verbatim from `Transient/bench_tools_dump.json`; both note the mod's own gizmo/dev-menu equivalents "never register live" (FLUID_CANAL_DEBUG_SURFACE_1), so these two ARE the only live-reachable surface — no separate `rimworld/execute_debug_action` route exists for this mod's report/dig actions.
- 🔴 This walk USED TO CLAIM "No [S] line: nothing here is a visual-only concern". That claim was false and is deleted. MEASURED 2026-09-16: the mod ships **zero bespoke textures** — the dug channel borrows `Terrain/Surfaces/Gravel`, the test source borrows the drop-beacon sprite — so every state assertion above can pass while the player looks at gravel. That is exactly the defect class the north star system exists to catch (`design/RimMandrake/north_star_validation_spec.md`), and this walk was one of the 7 that dismissed the visual pass in writing.
- Step 4 used to assert `volume` = 60 on the comp. **There is no `volume` field.** MEASURED 2026-09-16 from `Defs/ThingDefs/FluidCanal_ThingDefs.xml:51-57`: the comp is configured with `fluidDef`, `dripVolume` 3, `dripIntervalTicks` 2500, `reFloodVolume` 60, `reFloodIntervalTicks` 180000. The 60 that line was reaching for is `reFloodVolume`.
