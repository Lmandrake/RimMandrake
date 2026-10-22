# FlowWorks composite review scenarios — DESIGN ONLY (2026-10-21)

> DESIGN ONLY. No source edited, no game run. Proposes replacing the one-mechanic-per-station
> review map with composite working systems the owner can walk and poke.

## 0. Why (owner, 2026-10-21)

Owner, ~21:10 PDT, after walking tonight's FlowWorks review map: *"This walk sheet didn't include any of the
sophistication that the hoses used to enjoy when they were part of Gimme Some Slack. There were cool maze-solving
examples to play with. I need more diversity of items to review. Ask a design Opus 5.5 to design a bunch of
interesting, complex examples that thoroughly demonstrate and exercise Flowworks for human review. Each one should test
many things simply by its existence, rather than each little iterative trial as now."* Earlier the same night: the
staged map carried no in-world text, station numbers or instructions.

So this doc proposes **12 composite scenarios** (C1-C12) that replace the 88-station one-mechanic gallery of
`src/RimMandrake/FlowWorks/review_map.py` (86 `SETUPS` entries plus the look-only `river_ford` and
`river_works_looks`) and the 8 river stations of
`review_map_rivers.py`. Each scenario is a small **working system**: it runs when he unpauses, every part of it is
something a player would build, and a broken mechanic shows up as the system not working, not as one pad looking odd.
The V block (39 pit-look plots, `review_map_visuals.py`) is kept as the art wall; it is not a mechanics walk.

## 1. What made the GSS review maps engaging

Read from `src/RimMandrake/GimmeSomeSlack/human_review.py` (stations 21/22/29 before 2026-10-15) and the copies that
moved into `review_map.py` (`hose_maze`, `hose_maze_walled`, `hose_relay`, `hose_into_pond`):

1. **A problem, not a specimen.** The maze (outer 13x11 ring, two gaps east, inner chamber with a west door, reel
   inside) asks *"which way will it go?"* The answer is visible, and there are two right-looking answers (short way,
   long way), so a wrong pick is obvious.
2. **He can change the problem.** `hose_maze_walled` walls the short gap after laying; the hose must re-route (~25 of 40
   cells) or reel in with a message and an alert. Deconstructing the wall should bring it back. That is a poke with a
   predicted answer.
3. **Limits are reachable.** 40 cells of hose, so "lengthen the way round" pushes it past the limit by his own hand;
   relays extend it and refuse a loop.
4. **Chains of cause.** Relay reels: reel in the first, the second drains. One action, a visible consequence two
   objects away.

What tonight's map lost: every station is a pad with one mechanic frozen mid-state; nothing depends on anything else, so
nothing can be *solved* or *broken* by him. The composites below put those four properties back and add a fifth:
**every scenario has a goal a colonist would care about** (water the crop, keep the raiders out, get Hobb out of the
hole), so he judges FlowWorks by whether the goal is reachable and how it looks while it happens.

## 2. Design rules for every scenario

- **Labels in the world, always.** Every scenario carries `jawa/review_label` labels (the `label_ops` route) and a sign
  book (`sign_ops`, a vanilla Novel) at its entrance: **number, name, what to try, what to look for**. Inside a
  scenario, each part a poke touches gets a tiny label (`marks=` route): "sluice A", "reel 2", "Hobb (trapped)". Labels
  are re-pinned by `--labels` after a load. A scenario with no labels is a build failure, checked by `verify`.
- **Running, not frozen, where time is the point.** Time-varying state is staged through the surfaces the player's own
  buttons write (round 2 of `review_map.py`: `ProofTank` for stock only, `gizmo_cycle` for every mode, ladder
  up/down, pump Draw/Pour, `HoseProbe lay/order/settrail`). The save holds what a player's clicks leave; when he
  unpauses, the system runs. Nothing is staged by writing a state a player could not reach.
- **Each scenario is a plot of about 40x40 cells** (some 48x40) on one 250x250 quicktest map **C**; river-bound ones
  (C1, C11) on the river map **R** (`northstar/river_site.py`; painted river has no current). Lake floors stay on
  `lake_floor_stage.py`'s natural-lake tile. No worldgen anywhere: map R and the lake map are colonies founded on
  existing tiles of the fixed planet.
- **Colonists dig to 2 m; deeper holes are machine-dug** (owner card 2026-10-21: *"COLONISTS go back to a 2 m dig
  limit; droids / ridable machines dig deeper"*). Any staged hole deeper than 2 m is labelled "machine-dug" and its
  dig order is never left for a colonist. Machine digging itself is `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL` (re-scope
  owed): **DEFERRED** where a scenario wants him to order one.
- **Pipes half as thick, hoses much thinner** are being redrawn (`PIPE_GIRTH_TUNE_HALF_AS_THICK`,
  `HOSE_GIRTH_TUNE_MUCH_THINNER`); every scenario shows lines at play zoom beside colonists so the girth is judged in
  context, not on a pad. Line spec: `design/RimMandrake/flowworks_line_widths_2026-10-20.md`.
- **The four looks are spread, not galleried.** Each scenario is built in one look (C3 Scrapper, C4/C5 Industrial, C7
  Modern, C8 Futuristic...) and C1's sprinkler net shows all four side by side, so every look is seen *working*.
- **Laws held:** one Direct Sun (no per-biome heat: the sun-pan still and the pit's exposure only read the vanilla
  temperature the geometry gives); every DLC assumed (the review tier loads all five); no worldgen; no seabed (the ship
  is the only way down: no scenario goes there); Mod Settings at shipped defaults except where a scenario's sign says
  a switch is part of the poke; **no flyer is live-tested without the owner present** (C12's kennel uses walkers and a
  jumper only).
- **A defect line per scenario** says what broken looks like, so a defect is visible as a broken goal.
- **Overflow (canal → open ground, `canal_overflow_flooding_2026-10-21.md` §5 D1-D7) is Stage 1+ and unbuilt.**
  Scenarios that would show it (C1, C5, C10) are laid out so it *will* show once it lands, and say **DEFERRED** today.

## 3. The scenarios

Format per scenario: **Purpose** · **Exercises** (current stations it replaces → north-star bars → items) · **Layout**
(ASCII, 1 char = 1 cell unless noted; N up) · **Running when he arrives** · **Try** · **Broken looks like** ·
**DEFERRED** · **Staging cost** (reuse first). Legend used in sketches: `#` wall, `~` water, `=` pipe, `-`/`|` hose,
`o` reel, `P` pump, `T` tank, `S` sluice, `G` security grate, `L` ladder, `^` spikes, `C` pit cover, `D` dug canal
(depth digit when it matters), `X` sheer pit, `s` sprinkler, `+` pipe pole, `@` colonist, `r` raider, `b` animal.

### C1 — The Thirsty Terraces (map R, 48x40, look: all four in the sprinkler rows)

**Purpose.** Grow a crop on dry ground three steps above a river. Water has to be caught, lifted, carried over a ditch,
stored, let down terrace by terrace, and sprayed. Every link is a FlowWorks piece; the field greens only if all work.

**Exercises.** Stations `flow_spreads`, `look_canal`, `land_swale`, `land_deepsand`, `pipe_styles`, `hose_grid`,
`r_weir` (+ new: sprinkler heads, pipe poles, flow meter). Bars: `canal_fill_spreads_along_itself`,
`canal_fill_front_watchable`, `canal_reads_as_dug_channel`, `depth_and_fill_jointly_legible`,
`pipe_and_hose_one_net`, `pipe_meets_building_centre`, `never_tank_bridges_pipe_runs`,
`hose_far_end_pump_reaches_reel_tank`, `hose_drawn_under_overhead_span`, `sluice_gate_state_legible`,
`hose_and_pipe_girth_sensible` (proposed bar, not hash-bound). Items: `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED`, `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE`,
`PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`, `RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS`, `PIPE_GIRTH_TUNE_HALF_AS_THICK`,
`HOSE_GIRTH_TUNE_MUCH_THINNER`, `FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES` (meter), `SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR`.

**Layout.**
```
 river (real current) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ~~~~~~~~~~~ WWW weir pool ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 bank   P=====+=====+=====T(tall, Fill)        meter M on terrace 1
              |  D1 ditch crossed by the pole span (pipe overhead)
 T1  DDDDDDDDDDSDDDDDDDDDD   <- terrace 1 canal, D1, sluice S1 at its tail
     . . crop . . . . . .
 T2  DDDDDDDDDDSDDDDDDDDDD   <- terrace 2, fed through S1, sluice S2
     s=s=s=s (Scrapper)  s=s=s=s (Industrial)
     s=s=s=s (Modern)    s=s=s=s (Futuristic)  <- four sprinkler rows, one per look, on the tank's pipe net
 T3  sand + swale strip beside a D1 canal fed through S2 (sand -> soil over days)
       o-------- hose (Industrial reel) 30 cells to the REMOTE FIELD, crossing a second hose at right angles
```

**Running when he arrives.** Clock 10:00 (not noon: shadows read), paused. Weir placed and pooling (its pool is the
river's, read live). Pump on the bank set **Drawing into the tank** (`gizmo_cycle`), tank about 40% (`ProofTank`).
Terrace 1 canal full; S1 **open**, so terrace 2 is mid-fill with its front half way (staged by one pulse run of the
driver, not written). S2 **shut**: terrace 3 dry. Sprinklers' network has the pump on it, so they spray on the hour.
Remote field hose laid and **Plump**; a second hose from the tank crosses it (`hose_grid` crossing in situ).

**Try.**
1. Unpause one in-game hour: every sprinkler in all four rows sprays (the spray mote, centred on its pipe); the
   sprayed cells stay wet till the next spray, read in the inspect pane and the crop's yield, **not** by a ground
   tint (irrigation has no visual line: ruling 36, 2026-09-17, *"must not re-add an irrigation line"*). Compare the
   four looks working side by side.
2. Open S2: watch the front run along terrace 3; after days (dev: advance) the sand by the swale turns to soil.
3. Switch the pump to **Pour** or cut its power: the sprinklers stop on the next hour (*a working pump must be on the
   network*); the remote hose goes flat.
4. Select the meter on terrace 1: squares, levels held, net in/out per day; shut S1 and watch the numbers turn.
5. Deconstruct one pipe pole: the overhead span is gone and the pipe line can no longer cross the ditch.

**Broken looks like.** A sprinkler not centred on its pipe (tonight's defect); sprinklers spraying with no pump on the
net; a pipe drawn passing *through* the tank instead of into its centre; the overhead pipe drawn on the ditch floor or
without sag; terrace 3 wet with S2 shut; a hose crossing that is not clean over/under.

**DEFERRED.** Overflow onto the field (D2: a gravity feed from a higher source overflows; D3: overflow irrigates, kills
crops after a week). Lay out terrace 1 so its brim is one notch from spilling: when Stage 1 lands, leaving S1 shut and
the pump on spills a sheet onto the crop — the same scenario then tests D2/D3 with no rebuild.

**Staging cost.** Medium-high (~250 lines). Reuse: `review_map_rivers.river_anchors` to find a straight bank;
`extensions_rivers` weir placement (`ProofWeirPlace`/`ProofWeirPool`); `owner_review_stage.row_sprinklers` and
`hose_pump`/`hose_lay_all`; `review_map.Review.stage` (`tank`, `pump`, `hose`, `style` keys) unchanged; `ProofLinkPoles`
for the span; one `water_scenes_walk.pulse_loop` call to put the terrace-2 front half way.

### C2 — The Drowned Keep (map C, 44x44, look: Industrial)

**Purpose.** A small walled keep on an island of ground inside a water moat: the classic defence, built only from
FlowWorks parts. It holds against a raid party staged outside, and has a nasty gatehouse.

**Exercises.** Stations `pit_cover`, `pit_cover_drop`, `pit_spikes`, `look_parts`, `hold_gates`, `look_sink`,
`fire_chemfuel` (a chemfuel moat segment) + new: drawbridge gate, steel winch on a power cord, suspension bridge with a
grated deck, jetty, guardrail, raid plank. Bars: `canal_dry_reads_as_obstacle` (dry outer ditch), `deep_water_pawn_swims`,
`pawn_lowers_on_deeper_cell`, `spikes_read_distinct`, `pit_covered_invisible`, `pit_covered_seam_at_max_zoom`,
`pit_cover_unlike_bridge`, `suspension_bridge_reads_hung`, `pawn_walks_under_deck`, `sluice_gate_state_legible`,
`pit_trapped_reads_as_trapped`, `canal_burning_reads_as_burning_liquid`. Items:
`SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`, `SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD`,
`SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP`, `SUSPENSION_JETTY_BUILD_WALK_THE_PLANK`, `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP`,
`PIT_SPIKES_SHRINK_HALF_A_MAN`, `PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO`, `GUARDRAIL_ART_RESKIN_BORROWED_FENCE` (look only;
cosmetic change needs his permission), `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS`.

**Layout.**
```
 r r r  raiders (4) behind a shut security grate pen, one carrying a RaidPlank      dry ditch D2 (outer)
 ..........DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD..........
 ..~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~..   moat: D2 water ring, 3 wide (swimmable at 2 m)
 ..~~  #########[DB]#########################  ~~..   [DB] drawbridge leaf + gate; winch W inside, cord to battery
 ..~~  #  gatehouse: C C C over ^ ^ ^ (3x3 sheer   #  ~~..   pit, machine-dug, spikes, Plank-lattice cover)
 ..~~  #  S <- sluice from the moat into the pit   #  ~~..
 ..~~  #  keep yard: 2 colonists, guardrail on the  #  ~~..
 ..~~  #  inner pit's lip, a rail ladder raised     #  ~~..
 ..~~  ########## G drain grate -> edge-sink canal ##  ~~..
 ..~~~~~~~~~~~~~~~~~~~~~ ==bridge (hung, grated)== ~~..   suspension bridge to a jetty over the moat's east arm
 ..~~ chemfuel moat segment (north arm), unlit, behind a sluice ~~..
```

**Running when he arrives.** Paused, noon. Moat brim-full (level holder marker keeps it). Drawbridge leaf **raised**
(winch powered). Gate pit covered, spikes in it, sluice to it **shut**. Raiders spawned hostile *inside* a pen whose
security grate is **shut** (so nothing happens until he opens it); Peaceful storyteller otherwise.

**Try.**
1. Open the raiders' grate and unpause: watch them reach the moat, lay the plank across or swim (at 2 m they swim,
   heads and shoulders up), hit the dry ditch (slow, climb), and try the gate (it stays shut while hostiles are free).
2. Lower the drawbridge (winch) mid-raid: the leaf drops; the gate still refuses unless held open. Then let one raider
   through the gate onto the cover: he drops onto the spikes.
3. Open the gatehouse sluice: the trapped raider's pit floods from the moat (a non-swimmer animal would drown; a
   raider at ≥2 m water swims — read which, from the inspect pane).
4. Walk a colonist under the suspension bridge along the moat's dry bank (walk-under, head clearance) and over its
   grated deck.
5. Light the chemfuel arm with a torch (dev: `ProofTorch`): it goes up like gasoline; the grated deck lets the fire's
   heat up where a plain deck would not.
6. Cut the winch's power cord: the leaf holds where it is.

**Broken looks like.** The cover visible as a seam at max zoom; the cover reading like a bridge; raiders walking on the
moat floor; the gate opening for raiders while the leaf is up; a raider standing on the spikes unhurt; the bridge drawn
as a pier-on-pylons; the sluice open but the pit dry.

**DEFERRED.** Doors leaking slowly under water (D4) — the keep's postern door sits one cell from the moat so it shows
once Stage 1 lands. Machine-dug pit: dig-by-machine order (re-scope).

**Staging cost.** High (~300 lines): the most new staging. Reuse `drawbridge_proof.py` (`ProofMakeDrawbridge`,
`ProofWinchPower`, `ProofLeaf`), `suspension_bridge_proof.py` (span/jetty placement), `raid_trench_proof.py` (raider
spawn and the plank, `ProofGivePlank`), `review_map._pit` + `static("ProofCover")`, `hostile=` key from `hose_their_tank`.
New: a hostile pen behind a shut grate (two calls).

### C3 — The Labyrinth Rescue (map C, 40x40, look: Scrapper; the GSS maze grown up)

**Purpose.** Hobb has fallen into a machine-dug sheer pit at the heart of a walled maze. No ladder reaches (deeper
than the portable ladder's 3 m). The only rescue is to **float him out**: get water from a pond outside, through the
maze, into his pit until it is 2 m deep or more, and he swims up. Next door, a boar in a second pit shows what flooding
does to a non-swimmer. This is the maze-solving the owner missed, with a stake.

**Exercises.** Stations `hose_maze`, `hose_maze_walled`, `hose_relay`, `hose_states`, `hose_reel`, `hose_styles`,
`hose_reels_laid`, `hose_deploy_by_hand`, `hose_dropped`, `hose_into_pond`, `pit_flood`, `pump_pour`, `flow_shrinks`.
Bars: `hose_plump_when_flowing_flat_when_not`, `hose_plumps_only_from_powered_pump`, `hose_carries_real_units`,
`hose_dropped_carries_nothing`, `hose_follows_port_changes`, `hose_joiner_reads_brass_screwed_together`,
`reel_hose_leaves_brass_outlet_nozzle`, `reel_laid_and_wound_look_differ`, `reel_offers_choose_style`,
`four_reel_looks_distinguishable`, `relay_chain_carries_liquid`, `relay_chain_reads_connected`,
`never_hose_across_impassable`, `hose_drawn_under_overhead_span`, `pump_hose_joins_at_side_port`,
`hose_thicker_stiffer_than_cord`, `deep_water_pawn_swims`, `pit_trapped_reads_as_trapped`, `reservoir_fill_visibly_drops`.
Items: `HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE`, `HOSE_LAY_POLISH_CENTRE_VS_MOUTH`, `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD`,
`FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE`, `HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY`, `DEEP_WATER_BUILD_SWIM_OR_SINK` (R12).

**Layout.**
```
 pond ~~~~~      ########################################
 ~~~~~ P o1 -->  #   .   #      .        #    .   +---+ #   +---+ = GSS overhead wire span on poles
 ~~~~~ (power    #  ###  #  ########  #  #  ###   |   | #           (hose must pass UNDER it)
 ~~~~~  cord)    #  # .  .  .   #  .  #  .  # .   .   . #
 ~~~~~           # ## ###### ## # ##### ##### #####  #  #   door d1 (short way; he can wall it)
 o2 (relay reel  #  .  #   XX  #  .  #    .   #  chasm  #   XX = Hobb's pit (2x2, machine-dug, sheer)
     in the maze #  ## # @ XX  #  ## ##### #  # (impass)#   YY = boar's pit (2x2), separate
     corridor)   #  .  #   YY b   .     d1    .         #
                 ########################################
 reel park (south): four reels, one per look, laid / wound, flat / filling / plump, a dropped carry, a deploy order
```
Route lengths are set so the **short way** (through door d1, under the wire span) is ~34 cells from reel o1 (one hose
does it) and the **long way** (round the chasm) is ~52 (needs relay reel o2).

**Running when he arrives.** Paused. Pump on the pond's edge, powered, **Drawing**; its hose (o1) laid **into the maze
along the short way**, ending at the pit's lip, flow **Plump** (the pump feeds a small tank beside it); the free end is **Capped**
(the reel's *Free end:* button: Capped / Intake / Outflow), so the pit is still dry: the last step is his. Relay o2 wound. Reel park staged as today's `hose_states`/`hose_reels_laid`.

**Try.**
1. Press the reel's *Free end* button to **Outflow** (an Outflow or Intake end is a port of the network; Intake
   needs a working pump on it); unpause: the pond shrinks, the pit fills; at ≥2 m Hobb swims and climbs out. Read `HoseProbe`/the reel's inspect: litres moved are real.
2. Before that, wall door d1 (the short way): the hose must re-route the long way (>40: it reels in with a message and
   an alert naming the cells needed); fix it by laying o1 onto relay o2.
3. Try a portable ladder into Hobb's pit: refused (too deep) — that is why the maze exists.
4. Move the hose end to the boar's pit instead: the boar starts drowning (the non-swimmer case). Draft and cancel.
5. Cut the pump's cord: the hose goes flat (plumps only from a powered pump); rotate the pump: the hose follows the port.
6. In the reel park: choose a style on a reel, deploy one by hand (unpause, a colonist walks it out), retract one.

**Broken looks like.** The hose through a wall, over the chasm, or on top of the wire span; the long way chosen when
the short is open; a hose that never plumps; litres in the pit that do not match litres out of the pond; Hobb standing
on the pit floor under 2 m of water; the boar swimming; a loop of relays accepted.

**DEFERRED.** Nothing core. Swimming up *out of* a flooded sheer pit is R12's claim ("deep water stops being a barrier
for pits") but no driver row measures that exact climb-out yet: the scenario is the first look; label it so.

**Staging cost.** Medium (~180 lines). Reuse `MAZE`/`_perimeter` (grown to 40x40 by a second ring), `Review.stage`
`hose`/`hose_order`/`hose_trail`/`hose_flow` keys, `hose_probe`, `late_hoses`, `owner_review_stage.hose_pump`,
`water_scenes_walk._pump_rig`; GSS overhead wire span from `GimmeSomeSlack/human_review.py` staging (`jawa/gss_stage`).
Pit sizing (litres to 2 m) read from `ProofReadout` at build time, never typed.

### C4 — The Wet Quarry (map C, 40x40, look: Industrial)

**Purpose.** A stone quarry dug below the water table: the deeper it goes, the more it floods, and a dewatering rig
keeps it workable. Shows the dig ladder, rock vs soil, finds, ways in and out, and pumping water *up and away*.

**Exercises.** Stations `dig_canal`, `dig_finds`, `pit_ramp`, `pit_pocket`, `look_walls`, `look_pit`, `flow_drains`,
`carry_industry` (a wrecked pumping station on the rim), `industry_stages_more`. Bars: `canal_reads_as_dug_channel`,
`never_gravel_path`, `pit_depth_ladder_legible`, `pit_walls_have_visible_depth`, `pawn_lowers_on_deeper_cell`, `pawn_rises_on_shallower_cell`, `pawn_height_ladder_legible`, `half_metre_water_reads_as_silt`,
`geared_pawn_climbs_out`, `climbing_gear_reads_as_kit`, `wall_ladder_rides_on_rails`, `empty_reservoir_stops_flow`. Items: `FLOWWORKS_QUARRY_DIGGING_1`, `DIG_ROCK_TUNE_STONE_FIGHTS_BACK`,
`PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS` (unbuilt), `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS`,
`FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE`, `DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`.

**Layout.**
```
 soil rim (dirt walls)              | stone rim (rock walls)
 D1 D1 D1 D1 D1 D1 D1 D1 D1 D1 D1 D1 D1 ramp R -> D1 bench
 D2 D2 D2 D2 D2 D2 D2 D2 D2 D2 D2 D2 D2      staircase pocket (D1>D2>D3)
 D3 D3 D3 [ machine-dug sump  D4 x 4x4 ] D3  rail ladder L on the sump's west wall
 D3 D3 D3 [ 1.5 m standing water, tap  ] D3  RM_LiquidTap "groundwater" bleeding in
          pump P on the D3 bench -> hose up the ramp -> edge-sink drain canal (D1) to the map edge
 dig order on the rim: 14 cells, colonist with a pick; second order to D3 (refused past 2 m: "machine")
 wrecked pumping station on the rim (stage 1 of 3)
```

**Running when he arrives.** Paused. Tap bleeding into the sump (live). Pump **Drawing** from the sump, hose laid up
the ramp to the drain canal, Pouring there; the sump is holding level (inflow ≈ outflow, staged by choosing rates, not
written). One miner in climbing gear on the D3 bench; one colonist at the rim with a 14-cell dig order.

**Try.**
1. Unpause: the colonist digs; about 1 in 70 dug tiles leaves a lump with a letter the first time; soil goes faster than
   rock and rock drops chunks.
2. Order a dig to 3 m: refused for a colonist (2 m cap) — machines dig deeper (DEFERRED: no machine yet).
3. Stop the pump: the sump rises half-metre by half-metre (silt-coloured at 0.5 m, then deeper), the miner wades, then
   swims; restart it and the level falls.
4. Raise the rail ladder from below, lower it from above (only from above); the geared miner climbs a sheer wall anyway.
5. Walk a colonist down the ramp and the pocket staircase: lower with each step, never trapped.

**Broken looks like.** Any dug tile reading as gravel path; dirt and stone walls drawn alike; the sump a flat blue
square with no depth; the miner standing on
water at 2 m; the ladder lowered from below.

**DEFERRED.** Machine digging past 2 m (re-scope card owed). Deepstone stratum finds (`PIT_DEEPSTONE_...`, unbuilt).

**Staging cost.** Medium (~150 lines). Reuse `review_map` `dig`/`designate`/`pump`/`ladder`/`items` keys,
`owner_review_stage.row_ladders` (rail ladder rotation), `static("PlaceSink")`/`PlaceLevelHolder` for the sump balance,
`ProofLiquid` for the tap, `carry_industry` setup verbatim.

### C5 — The Fuel Depot (map C, 40x36, look: Industrial; cargo tanks Futuristic)

**Purpose.** A caravan fuel stop: cargo tanks of chemfuel and propane, a filling bay where colonists fill barrels and
bottles, a neighbour's tank someone has tapped, a bunded containment canal, and a fire plan. It is the **one place that
must not burn**, so it shows every fire rule by being dangerous.

**Exercises.** Stations `carry_tanks`, `tank_styles_cargo`, `tank_modes`, `pipe_adapter`, `hose_their_tank`,
`carry_bottles`, `carry_containers`, `containers_styles`, `fire_chemfuel`, `fire_astrofuel`, `fire_out`, `fire_lights`,
`liquid_spill`, `canal_fluids_more`, `flow_no_mix`. Bars: `fill_fluid_distinct`, `hose_tint_is_carried_liquid`,
`never_external_pipe_carries`, `never_tank_bridges_pipe_runs`, `canal_burning_reads_as_burning_liquid`,
`canal_fire_persists`, `canal_spent_after_burn`, `canal_fire_reaches_reservoir`, `pipe_meets_building_centre`.
Items: `FLOWWORKS_CONTAINER_MATERIALS_1`, `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS`, `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH`,
`LIQUID_LEDGER_BUILD_NO_UNIT_LOST`, `MISSION_TANK_GOAL_REWIRE_TO_DEST`, `CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` (D5).

**Layout.**
```
 [cargo T chemfuel] [cargo T propane] [XTall T chemfuel]  -- adapters A (Send/Take/Shut) on the pipe run
        =========== pipe run (Industrial) ===========  P (pump, Pour) -> containment canal (D1, bunded, chemfuel 1/4)
 filling bay: tanks set Store | Fill | Empty | Dump; empty barrels/bottles in wood/metal/plasteel/leather/glass beside
 spill pad: one spilled chemfuel filth, tracked tar footprints
 THEIR tank (trader faction) ---- our hose coupled to it, laid back to our Fill tank
 astrofuel bund: a separate 2x2 D1 pit with a trace of astrofuel, 12 cells away, walled; firefoam popper beside the canal
 a water canal and an acid canal run parallel to the chemfuel canal, one wall apart (no mixing)
```

**Running when he arrives.** Paused. Tanks staged by `ProofTank` (stock) + `gizmo_cycle` (mode). Our hose on THEIR
tank laid, Plump with chemfuel tint. Containment canal a quarter full of chemfuel; nothing lit.

**Try.**
1. Unpause: colonists fill barrels from the **Empty** tank and pour into the **Fill** tank only; the **Dump** tank
   empties into the containment canal through the pump.
2. Cycle an adapter Send → Take → Shut and watch the pipe run's stock move (needs Vanilla Chemfuel Expanded, on the
   review tier).
3. Select the hose on their tank: tinted chemfuel; its inspect names nobody's faction (state read only).
4. Light the containment canal (`ProofTorch`): it burns like gasoline, keeps burning, reaches the tank end (does
   the canal fire reach the reservoir?), and leaves the canal spent. Pop the firefoam: foamed cells stay out while
   foam lies.
5. Light the astrofuel bund: it detonates, not burns.

**Broken looks like.** Chemfuel, propane and water hoses all the same colour; a tank drawn bridging two pipe runs; the
Fill tank emptied by colonists; water and chemfuel mixing at a shared wall; a burnt canal that looks fresh; foamed
cells relighting under foam; litres appearing from nowhere (the ledger says no unit is lost).

**DEFERRED.** **Fuel overflow spreads and burns (D5)**: the containment canal is filled to one notch below its brim;
when Stage 1 lands, setting the Dump tank on with the canal shut spills a sheet that a torch then lights. Today it
stops at the brim.

**Staging cost.** Low-medium (~120 lines). Almost all reuse: `carry_tanks`, `tank_modes`, `pipe_adapter`,
`hose_their_tank`, `fire_*`, `containers_styles` setups re-laid on one plot; `Review.stage` `tank`/`pump`/`hostile`/`hose`.

### C6 — The Tar Seep (map C, 40x36, look: Scrapper)

**Purpose.** A tar seep on the edge of the colony: tar bleeds up, crawls down a ditch, gets tracked into the base on
boots, is refined, and catches fire. A slime pit and an acid vat share the yard. It is the **viscous liquids** scenario:
tar and slime must look and behave unlike water, and water runs beside them for comparison.

**Exercises.** Stations `flow_identity`, `flow_slime`, `look_liquids`, `look_fire`, `fire_lights`, `fire_lasts`,
`fire_corrosion`, `liquid_spill`, `carry_drills`, `industry_stages`, `carry_industry`. Bars: `tar_fill_front_lags_water`,
`slime_reads_as_viscous_not_water`, `slime_occupant_below_surface`, `canal_reads_as_same_liquid_as_reservoir`,
`fill_fluid_distinct`, `canal_burning_reads_as_burning_liquid`, `canal_fire_persists`, `canal_spent_after_burn`.
Items: `TAR_LOOK_TUNE_THICK_AND_SLOW`, `SLIME_CROSSING_BUILD_SLIPPERY_SLOPE`, `LIQUID_LOOK_MATERIAL_OWNERSHIP_1`
(ReactionVat tar+acid: `RM_Reaction_TarAcid`).

**Layout.**
```
 tar drill (on a survey hit) -> tar ditch D1 ------------------------->  (40 cells, running downhill to a sump)
 tap (water) -> water ditch D1 --------------------------------------->  (same length, side by side: a race)
 tar refinery: Wrecked | Kludged | Repaired, the Repaired one fed by the tar ditch's sump
 slime pit 4x4 D2 (green slime), a muffalo standing in it; a 1-cell plank of ground across
 reaction vat between a tar tank and an acid tank; an acid canal with steel and wood lying in it
 tracked-tar footpath from the refinery door to a stockpile (filth on floor)
```

**Running when he arrives.** Paused at the race's start: both ditches staged empty, both sources live. The vat's two
feeds connected, idle.

**Try.**
1. Unpause: the water front runs, the tar front crawls behind it (watch both fronts together).
2. Walk a colonist across the slime pit's edge: slow, nearly uncrossable; the muffalo sits below the surface.
3. Light the tar ditch: it burns for days; the refinery stops if its feed burns; extinguish with rain (dev weather).
4. Start the vat: tar + acid meter in; product caught where there is a catcher, vented where there is none.
5. Watch the acid canal: what lies in it loses health over time, not in seconds.
6. Colonists clean the tar filth.

**Broken looks like.** Tar front level with water; slime that looks like coloured water; a muffalo standing on top of
slime; tar filth with no art; a burning tar ditch that goes out in an hour; the refinery's three stages hard to tell
apart; corrosion while the switch is off.

**DEFERRED.** None core. `TAR_LOOK_TUNE_THICK_AND_SLOW` is a tune he does at this scenario, with the game up.

**Staging cost.** Low-medium (~110 lines). `flow_identity`/`flow_slime`/`fire_*`/`carry_drills`/`industry_stages`
setups; one fluid race driver call (`water_scenes_walk` S1 geometry helpers `s1_geom`, `pulse_loop` left un-run).

### C7 — The Bathhouse and Water Tower (map C, 40x40, look: Modern)

**Purpose.** A desert colony's water: a tall tower tank fed by a well pump, gravity down to taps, a bathhouse, a
drinking fountain line, stills for bad water, a drip filter for poisoned water, and colonists who are thirsty.
Communicating vessels in plain sight: water finds its level.

**Exercises.** Stations `carry_tanks`, `tank_sizes`, `tank_styles`, `tank_modes`, `carry_drills` (both stills),
`industry_stages_more` (desalination and detox works), `containers_all`, `carry_kits`, `carry_bottles`. Bars:
`tank_feeds_hose_without_pump`, `pipe_meets_building_centre`, `never_tank_bridges_pipe_runs`,
`still_water_one_surface_height`, `reservoir_fill_visibly_drops`, `pipe_and_hose_one_net`. Items:
`THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY`, `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING`, `THIRST_RULES_BUILD_SALT_OFF_THE_MENU`,
`PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL`, `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`, `TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH`.

**Layout.**
```
 well: pump P on a small pond -> XTall cargo tank (tower) ----+
                                                             = pipe down
   short | tall | cargo tanks, one per size, all on one net  (levels equal when connected: communicating vessels)
 bathhouse (roofed): 2x3 bath pit D1 filled from a tap off the net; a liquid thermostat marker keeps it warm
 fountain line: three taps, Empty-mode tank, bottles on a shelf (every liquid in every container: the water seller's stall)
 bad-water corner: brine tank -> fueled still -> clean tank; salt tank -> sun-pan still (works by day only, noon sun)
 poisoned barrel -> drip filter -> pan (slow, wasteful)
 a hose from the tower tank (no pump) to the garden: gravity
 4 colonists with Thirst low; one prisoner in the bathhouse cell (administer water)
```

**Running when he arrives.** Paused, 11:00. Tower half full; the three ground tanks at different levels and **not yet joined** (a two-cell gap
in their pipe, with a blueprint for the missing cells); thirst staged low on colonists (vanilla need write, the same surface a day without water leaves).

**Try.**
1. Unpause: thirsty colonists drink from taps/bottles; the warden carries water to the prisoner.
2. Let the colonists build the two missing pipe cells: their levels move to one height (decilitre steps, not notches).
3. Hose from the tower to the garden with no pump: it flows (gravity), and stops when the tower's level drops below.
4. Run the stills: fuelled works day and night; the sun-pan stops at dusk and under a roof.
5. Pour poisoned water into the drip filter: a slow, small clean drip.
6. Look at the stall: every liquid in every container, all four looks, at true scale beside a colonist.

**Broken looks like.** Tanks on one net holding different levels at rest; a gravity hose flowing uphill; brine drunk
as water (salt off the menu); the sun-pan working at night; pipes ending at a tank's edge, not its centre; the bath pit
reading as a hole, not a bath.

**DEFERRED.** Overflowing bath (D2/D4: leaking under the bathhouse door) once Stage 1 lands.

**Staging cost.** Medium (~170 lines). Reuse `tank_sizes`/`tank_styles`/`tank_modes`/`containers_all` setups,
`level_water.py` (levelling read), `PlaceThermostat`, `pond_pump.py`, `thirst_live.py` staging for need values.

### C8 — The Canal Lock (map C, 44x24, look: Futuristic)

**Purpose.** Two canals at different water levels joined by a lock chamber with a sluice at each end, on a timer. A
swimmer rides the lock up. It is the **level-solving** scenario: one still surface per body, levels equalising only
through open gates, and the timer and meter markers working together.

**Exercises.** Stations `hold_gates` (sluices), `look_sink`, `look_canal`, `flow_spreads` + new: timer switch, flow
meter, level holder, swimming. Bars: `still_water_one_surface_height`, `sluice_gate_state_legible`,
`depth_and_fill_jointly_legible`, `fill_tier_legible`, `canal_partial_fill_distinct`, `deep_water_pawn_swims`,
`pawn_rises_on_shallower_cell`, `half_metre_water_reads_as_silt`. Items: `SLUICE_GATE_REWIRE_TURNS_LIKE_A_DOOR`,
`FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES`, `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS`, `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`.

**Layout.**
```
 upper canal: D2, level holder H keeps it brim-full     | lock chamber 6x3, D2 | lower canal: D2 dug, 0.5 m water,
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ S1 [   swimmer @      ] S2 ~~~~~~~ (edge-sink at far end)
 timer switch T beside the lock: S1 open 06-09h, S2 open 12-15h          meters M1 (upper) M2 (chamber) M3 (lower)
```
(Both canals are dug to the same floor; "upper" and "lower" are water levels, which is what FlowWorks models.)

**Running when he arrives.** Paused 05:50; both sluices shut; chamber at the lower canal's level; a colonist swimming in
the chamber (water staged at 2 m: swims).

**Try.**
1. Unpause through the morning: at 06:00 S1 opens, the chamber rises to the upper level, the swimmer rises with it; at
   09:00 S1 shuts; at 12:00 S2 opens and the chamber falls to the lower level.
2. Read the three meters as it happens: net in/out per day, levels held.
3. Open both sluices at once by hand: the whole run becomes one surface, the upper canal held up by the holder.
4. Watch the lower canal: 0.5 m reads as silt-coloured shallows, not as blue water.

**Broken looks like.** Two levels on one side of an open gate; a gate drawn open while shut (or turning unlike a door);
the swimmer standing on the floor; the timer firing at the wrong hours; meters disagreeing with what is drawn.

**DEFERRED.** A boat: FlowWorks has none. The swimmer is the boat.

**Staging cost.** Low (~90 lines). `PlaceTimer`, `PlaceMeter`, `PlaceLevelHolder`, `PlaceSink` (all exist);
`review_map` `dig`/`fluid`/`pawns` keys; sluices via `gizmo_cycle`.

### C9 — The Trench Line (map C, 44x32, look: n/a, earthworks)

**Purpose.** A dry trench line facing an open field, the way a desert colony would fight: zig-zag trenches at waist and
chest depth, a firing step, a tar-filled anti-raider ditch, and a raid party that has to get across. It is the
**dug-ground-as-terrain** scenario: cover, movement cost, shooting from holes, and what raiders do about trenches.

**Exercises.** Stations `dig_slows`, `pit_shooting`, `look_sink`, `flow_identity` (tar ditch) + new: trench cover,
raider ladder, raider fill-in, titan-wide trench. Bars: `trench_wall_cover_shown`, `raiders_never_shelter_in_a_cage`,
`canal_dry_reads_as_obstacle`, `filled_excavation_reads_as_obstacle`, `pawn_lowers_on_deeper_cell`,
`never_snared_standing`, `geared_pawn_scales_built_wall`. Items: `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT`,
`RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP`, `TITAN_TRENCHES_WIRE_MIND_THE_GAP`, `TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP`,
`PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`, `WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS`, `WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM`.

**Layout.**
```
 raiders (6, one in climbing gear) behind a shut grate pen, 30 cells east
 . . . . . . open field . . . . . . . . . . . . . . . . . . . . . .
 TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT  tar ditch D1, 2 wide (unlit)
 . . . . . . . . . . . . . . .
 D1 D1 D2 D2 D1 D1 D2 D2 D1 D1   zig-zag trench, waist (D1) and chest (D2) bays, 3 colonists with rifles in D2 bays
 D1 . . . D2 . . . . D1 . . .    one D2 bay flooded to 0.5 m (wet foxhole)
 a 4-wide D2 trench section ("titan gap") at the south end; a stone wall rampart behind the north end
```

**Running when he arrives.** Paused. Colonists drafted in the bays. Raiders penned; grate shut.

**Try.**
1. Hover a raider's shot at a colonist: the hit chance lists a "trench wall" cover line, bigger for the chest-deep man.
2. Open the pen and unpause: raiders cross the tar ditch (slow), hit the trench line, set a ladder or fill a cell to
   cross, and never shelter in a sheer pocket they could not leave; the geared raider goes over the north rampart.
3. Light the tar ditch as they cross.
4. Hover the lanes: walk cost climbs with depth; the wet bay is slower than the dry D2.

**Broken looks like.** No cover line, or the same for waist and chest; a raider stuck in a pocket; raiders walking over
a trench as if flat; a titan (if one comes) stepping across the 4-wide gap; the wet bay no slower.

**DEFERRED.** `WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM` (unbuilt): the wet bay is placed so it shows once built.

**Staging cost.** Medium (~130 lines). `raid_trench_proof.py` (raider spawn, `ProofTrenchCover`), `trench_cover_proof.py`,
`review_map` `dig`/`pawns`/`hostile` keys, `climb_proof.py` for the geared raider.

### C10 — The Rain Basin (map C, 44x40, look: n/a, land and water bodies)

**Purpose.** A dry wash that floods: a limited pond, a limitless spring, a canyon-flood channel, open and roofed
trenches for rain, a fill-in job, and a drain off the map edge. It is the **water bodies and weather** scenario:
where water comes from, where it goes, and that every litre is accounted.

**Exercises.** Stations `flow_ponds`, `flow_shrinks`, `pond_bed`, `pond_occupied`, `pond_return`, `flow_rain`,
`flow_canyon`, `flow_drains`, `dig_fill_in`, `pump_pour`, `hose_into_pond` + new: map edge setter, limitless body marker.
Bars: `reservoir_fill_visibly_drops`, `never_full_reservoir_after_heavy_draw`, `empty_reservoir_stops_flow`,
`reservoir_shoreline_recedes`, `reservoir_recharge_progress_visible`, `limitless_body_marked`, `canal_holds_only_the_channel`,
`never_liquid_on_open_ground`, `half_metre_water_reads_as_silt`. Items: `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD`,
`LIQUID_LEDGER_BUILD_NO_UNIT_LOST`, `FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS`, `FLOOD_STATION_REWIRE_DRY_CANAL_STAYS_DRY`,
`CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED` (D1, D2, D6), `FISH_ROLL_MEND_PONDS_BORN_BARREN`.

**Layout.**
```
 limited pond (12x8) --- canal A (D1) ----+---- canal B (D1) ----> edge sink (map edge, drain)
 limitless spring (marked) --- canal C (D1)          fill-in order on canal A's far 4 cells
 canyon flood trigger at the wash head -> dry canal D (D2) winding 30 cells
 rain trenches: E open, F roofed, side by side
 a second pond already drawn down to its hollow, a muffalo standing in the bed
 pump on the limited pond with a hose Intake end in it (pump on the net), tank beside, pump set Draw
```

**Running when he arrives.** Paused, clear. Canal A drawing from the limited pond (front mid-way); the spring's canal
C full; D dry; E/F dry. A colonist assigned to the fill-in.

**Try.**
1. Unpause: the limited pond's shoreline recedes as A and the pump draw; the spring never drops (marked limitless).
2. Let the fill-in run: filled cells' water goes back to the pond, the pond's edge rises.
3. Dev: weather Rain: E fills, F stays dry; the drawn-down pond refills around the muffalo, never over it.
4. Press *Flood now* on the canyon trigger: the flood runs in canal D, not over the land.
5. Switch the pump to Pour: the tank empties back into the pond.
6. Select the edge-setter: set the east edge *sealed*: B stops draining and fills.

**Broken looks like.** The pond full after heavy draw; the spring not marked limitless in its readout; water on open ground beside a full
canal (today; not after Stage 1); water poured onto the muffalo; the flood wiping the canal flat; a sealed edge still
draining; any litre unaccounted in the ledger.

**DEFERRED.** **Overflow, Stage 1+ (D1, D2, D6):** canal B is sized so that sealing the edge with the pump pouring
overfills it; after Stage 1 the sheet spreads, soaks in and evaporates on the pulse, and fill-in's homeless water
spills as a sheet (D1). Today the scenario shows the pre-overflow rule. Re-label then.

**Staging cost.** Medium (~150 lines). Nearly all reuse: the eight pond/flow/rain/canyon setups re-laid as one basin;
`PlaceEdgeSetter`, `PlaceFloodTrigger` (`BIOME_MC`), `ProofSetBodyFraction` for the drawn-down pond.

### C11 — Prospector's Creek (map R, 48x40, look: Scrapper)

**Purpose.** A working creek: ford stones for the road, a stake levee and silt trap protecting a bank camp, a weir
that a flood wears through, a ferry rope across the deep run, panners and a sluice box washing for gold, and river
drift fetching up on the bars. It is the **moving water** scenario, on a real river with real current.

**Exercises.** Stations `r_current`, `r_ford`, `r_weir`, `r_breach`, `r_stakes`, `r_silt`, `r_ferry`, `r_placer`,
`land_panning`, `river_ford`, `river_works_looks`. Bars: `deep_water_pawn_swims`, `pawn_lowers_on_deeper_cell`.
Items: `SUSPENSION_WATERS_BUILD_MAY_BACKTRACK` (a rope bridge over the deep run), `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED`,
`RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS`, `RIVER_SCENES_BUILD_WALKTHROUGH_WITH_CAPTIONS`.

**Layout.** Anchored on the river's real crossings (`river_anchors`); upstream to downstream: weir (worn, near breach)
→ ford stones → ferry post pair across the deep run, and a rope suspension bridge beside it → stake levee + silt trap
along the camp bank → panning spot and sluice box on the shallows → a gravel bar where drift lands.

**Running when he arrives.** Paused. A throwaway colonist standing in moving water beside the ford (control), one on
the ford stones; a ferry rope rigged; panners assigned.

**Try.**
1. Unpause: the control colonist is carried; the one on the stones is not.
2. Ferry a colonist across the deep run; then walk the rope bridge.
3. Watch the weir: it pools; dev-advance and it breaches (worn), the stakes hold the bank, the silt trap fills.
4. Panners and the sluice box draw from the shared stock; setting off washes nothing.
5. Stand a throwaway colonist in moving water at the map edge: swept off the map; he walks home.

**Broken looks like.** Nobody carried; the stones carrying; the ferry ignored; a weir that never pools or never breaks;
wash drawing from nothing.

**DEFERRED.** None core (river mechanics shipped; live rows owed).

**Staging cost.** Low (~60 lines new): `river_scenes_walk.py` scenes R1-R5 already stage these; re-lay them into one
plot and add labels/sign books (`review_map_rivers.label_ops` exists).

### C12 — The Oubliette and the Kennel (map C, 40x36, look: Modern)

**Purpose.** A prison yard dug into the ground, and next to it a kennel of pits that each hold a different beast. It is
the **pits hold, or do not** scenario: what fits, what climbs, what is trapped, how the wardens work from the lip, and
every way into and out of a pit.

**Exercises.** Stations `pit_holds`, `pit_width`, `pit_climb`, `pit_fall`, `pit_ways_in`, `hold_ladder`,
`hold_ladder_raised`, `hold_prison`, `hold_exposure`, `hold_gates`, `look_pit`, `pit_cover` + new: guardrail, portable
ladder, climbing gear, rail ladder, a jumper, administer water to a prisoner. Bars: `pit_reads_as_hole`,
`pit_not_vanilla_trap`, `never_reads_as_building`, `pit_reads_at_size`, `pit_occupied_distinguishable`,
`pit_trapped_reads_as_trapped`, `pit_occupant_below_floor`, `ladder_state_legible`, `wall_ladder_rides_on_rails`,
`portable_ladder_leans_on_its_wall`, `climbing_gear_reads_as_kit`, `geared_pawn_climbs_out`,
`jump_into_pit_lands_unhurt`, `pit_walls_have_visible_depth`. Items: `PIT_ALERT_BUILD_RED_MEANS_HELP`,
`PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER`, `PIT_TEMPERATURE_SOFTENING_1`, `PIT_LADDER_REDRAW_HUNG_ON_THE_WALL`,
`PIT_LIP_FIX_BOAR_HANGS_OUT`, `FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT` (walkers and a jumper only).

**Layout.**
```
 OUBLIETTE (machine-dug sheer, 3x4): prisoner bed, prisoner; rail ladder on the N wall RAISED; guardrail round the lip
   a sluice (wood) and a security grate (steel) in its east wall to a dry drain canal
 second cell 3x3: covered (reinforced frame cover); a colonist will walk onto it
 KENNEL: 2-deep pens: chicken | husky | muffalo   ;  sheer 1x1 pit with a thrumbo-size beast beside it (does not fit)
 a pit with a portable ladder leaning on its W wall (3 m: fits), a colonist with climbing gear inside a deeper one,
 a jump-capable colonist (`climb_proof.py`'s jumper kit) at the lip of a third
```

**Running when he arrives.** Paused, noon. Prisoner hungry-ish and thirsty (wardens have work).

**Try.**
1. Unpause: wardens feed and water the prisoner from the lip; nobody climbs down.
2. Lower the rail ladder from above (only from above); raise it from below with the prisoner on it: stranded.
3. Kennel: the chicken stays, the husky climbs out slowly, the muffalo steps out; the big beast walks round the 1x1.
4. Walk a colonist onto the cover: falls through, hurt; jump the jumper in: lands unhurt; the geared colonist
   climbs out of the deep one; a colonist climbs the portable ladder.
5. Inspect a pit cell at noon and midnight (dev advance): its temperature differs from the ground's (vanilla
   temperature only: no extra sun kind).

**Broken looks like.** A warden climbing down; the room not a prison; all three kennel beasts held, or all out; the
big beast in the 1x1; the cover visible; a ladder lowered from below; the guardrail letting someone walk off.

**DEFERRED.** Flyers and floaters (pit travel) — **never live-tested without the owner**; add one only when he is at
the keyboard.

**Staging cost.** Low-medium (~110 lines). `hold_*` and `pit_*` setups re-laid; `owner_review_stage.row_ladders`;
`ProofLadder`, `ProofCover`; `climb_proof.py` pawn kit (gear, jump pack).

## 4. Coverage matrix

Derived by script from the **Exercises** lines above (backticked ids only), against `review_map.py`'s `SETUPS` keys,
its two river-look stations, `review_map_rivers.py`'s eight R stations, and the 81 bars of the `## north star` section
of `design/validation_walks/RimMandrake/FlowWorks.md`. Re-derive it, never hand-edit it, when a scenario changes.

### 4.1 Every current station → the scenario(s) that show it

| station | scenarios |
|---|---|
| `dig_canal` | C4 |
| `dig_fill_in` | C10 |
| `dig_slows` | C9 |
| `dig_finds` | C4 |
| `flow_drains` | C4, C10 |
| `flow_spreads` | C1, C8 |
| `flow_identity` | C6, C9 |
| `flow_no_mix` | C5 |
| `flow_ponds` | C10 |
| `flow_shrinks` | C3, C10 |
| `pond_bed` | C10 |
| `pond_occupied` | C10 |
| `pond_return` | C10 |
| `flow_rain` | C10 |
| `flow_canyon` | C10 |
| `flow_slime` | C6 |
| `fire_lights` | C5, C6 |
| `fire_lasts` | C6 |
| `fire_out` | C5 |
| `fire_chemfuel` | C2, C5 |
| `fire_astrofuel` | C5 |
| `fire_corrosion` | C6 |
| `pit_holds` | C12 |
| `pit_width` | C12 |
| `pit_climb` | C12 |
| `pit_fall` | C12 |
| `pit_shooting` | C9 |
| `pit_ways_in` | C12 |
| `pit_ramp` | C4 |
| `pit_pocket` | C4 |
| `pit_cover` | C2, C12 |
| `pit_cover_drop` | C2 |
| `pit_spikes` | C2 |
| `pit_flood` | C3 |
| `hold_ladder` | C12 |
| `hold_ladder_raised` | C12 |
| `hold_prison` | C12 |
| `hold_exposure` | C12 |
| `hold_gates` | C2, C8, C12 |
| `look_sink` | C2, C8, C9 |
| `look_canal` | C1, C8 |
| `canal_fluids_more` | C5 |
| `look_pit` | C4, C12 |
| `look_walls` | C4 |
| `look_parts` | C2 |
| `look_liquids` | C6 |
| `look_fire` | C6 |
| `carry_bottles` | C5, C7 |
| `containers_all` | C7 |
| `carry_containers` | C5 |
| `containers_styles` | C5 |
| `carry_tanks` | C5, C7 |
| `pump_pour` | C3, C10 |
| `tank_sizes` | C7 |
| `tank_styles` | C7 |
| `tank_styles_cargo` | C5 |
| `tank_modes` | C5, C7 |
| `hose_reel` | C3 |
| `hose_styles` | C3 |
| `hose_reels_laid` | C3 |
| `hose_states` | C3 |
| `hose_grid` | C1 |
| `hose_maze` | C3 |
| `hose_maze_walled` | C3 |
| `hose_relay` | C3 |
| `hose_deploy_by_hand` | C3 |
| `hose_dropped` | C3 |
| `hose_into_pond` | C3, C10 |
| `hose_their_tank` | C5 |
| `pipe_styles` | C1 |
| `pipe_adapter` | C5 |
| `liquid_spill` | C5, C6 |
| `carry_drills` | C6, C7 |
| `carry_industry` | C4, C6 |
| `industry_stages` | C6 |
| `industry_stages_more` | C4, C7 |
| `carry_kits` | C7 |
| `land_liquids` | V+ (art wall: look-only liquid grounds, no mechanic) |
| `land_liquids_2` | V+ (art wall) |
| `land_liquids_3` | V+ (art wall) |
| `many_waters` | V+ (art wall) |
| `land_deepsand` | C1 |
| `land_shores` | L (lake map, `lake_floor_stage.py`: shores need a generated map, not a staged one) |
| `land_swale` | C1 |
| `land_panning` | C11 |
| `land_settings` | every scenario's sign book names its switches; S0 status board |
| `river_ford` | C11 |
| `river_works_looks` | C11 |
| `r_current` | C11 |
| `r_ford` | C11 |
| `r_weir` | C1, C11 |
| `r_breach` | C11 |
| `r_stakes` | C11 |
| `r_silt` | C11 |
| `r_ferry` | C11 |
| `r_placer` | C11 |

Result: **96 of 96** current stations (88 main + 8 R) land in a scenario or a stated home; 90 in a composite,
4 look-only liquid-ground strips on the art wall (V block grows by four rows), 1 on the lake map, 1 spread across every sign.

### 4.2 North-star bars × scenarios

| bar | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 | C12 | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `canal_burning_reads_as_burning_liquid` |  | ● |  |  | ● | ● |  |  |  |  |  |  | 3 |
| `canal_dry_reads_as_obstacle` |  | ● |  |  |  |  |  |  | ● |  |  |  | 2 |
| `canal_fill_front_watchable` | ● |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `canal_fill_spreads_along_itself` | ● |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `canal_fire_persists` |  |  |  |  | ● | ● |  |  |  |  |  |  | 2 |
| `canal_fire_reaches_reservoir` |  |  |  |  | ● |  |  |  |  |  |  |  | 1 |
| `canal_holds_only_the_channel` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `canal_partial_fill_distinct` |  |  |  |  |  |  |  | ● |  |  |  |  | 1 |
| `canal_reads_as_dug_channel` | ● |  |  | ● |  |  |  |  |  |  |  |  | 2 |
| `canal_reads_as_same_liquid_as_reservoir` |  |  |  |  |  | ● |  |  |  |  |  |  | 1 |
| `canal_spent_after_burn` |  |  |  |  | ● | ● |  |  |  |  |  |  | 2 |
| `climbing_gear_reads_as_kit` |  |  |  | ● |  |  |  |  |  |  |  | ● | 2 |
| `deep_water_pawn_swims` |  | ● | ● |  |  |  |  | ● |  |  | ● |  | 4 |
| `depth_and_fill_jointly_legible` | ● |  |  |  |  |  |  | ● |  |  |  |  | 2 |
| `empty_reservoir_stops_flow` |  |  |  | ● |  |  |  |  |  | ● |  |  | 2 |
| `fill_fluid_distinct` |  |  |  |  | ● | ● |  |  |  |  |  |  | 2 |
| `fill_tier_legible` |  |  |  |  |  |  |  | ● |  |  |  |  | 1 |
| `filled_excavation_reads_as_obstacle` |  |  |  |  |  |  |  |  | ● |  |  |  | 1 |
| `four_reel_looks_distinguishable` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `geared_pawn_climbs_out` |  |  |  | ● |  |  |  |  |  |  |  | ● | 2 |
| `geared_pawn_scales_built_wall` |  |  |  |  |  |  |  |  | ● |  |  |  | 1 |
| `half_metre_water_reads_as_silt` |  |  |  | ● |  |  |  | ● |  | ● |  |  | 3 |
| `hose_carries_real_units` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_drawn_under_overhead_span` | ● |  | ● |  |  |  |  |  |  |  |  |  | 2 |
| `hose_dropped_carries_nothing` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_far_end_pump_reaches_reel_tank` | ● |  |  |  |  |  |  |  |  |  |  |  | 1 |
| `hose_follows_port_changes` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_joiner_reads_brass_screwed_together` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_plump_when_flowing_flat_when_not` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_plumps_only_from_powered_pump` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_thicker_stiffer_than_cord` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `hose_tint_is_carried_liquid` |  |  |  |  | ● |  |  |  |  |  |  |  | 1 |
| `jump_into_pit_lands_unhurt` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `ladder_state_legible` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `limitless_body_marked` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `never_external_pipe_carries` |  |  |  |  | ● |  |  |  |  |  |  |  | 1 |
| `never_full_reservoir_after_heavy_draw` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `never_gravel_path` |  |  |  | ● |  |  |  |  |  |  |  |  | 1 |
| `never_hose_across_impassable` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `never_liquid_on_open_ground` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `never_reads_as_building` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `never_snared_standing` |  |  |  |  |  |  |  |  | ● |  |  |  | 1 |
| `never_tank_bridges_pipe_runs` | ● |  |  |  | ● |  | ● |  |  |  |  |  | 3 |
| `pawn_height_ladder_legible` |  |  |  | ● |  |  |  |  |  |  |  |  | 1 |
| `pawn_lowers_on_deeper_cell` |  | ● |  | ● |  |  |  |  | ● |  | ● |  | 4 |
| `pawn_rises_on_shallower_cell` |  |  |  | ● |  |  |  | ● |  |  |  |  | 2 |
| `pawn_walks_under_deck` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `pipe_and_hose_one_net` | ● |  |  |  |  |  | ● |  |  |  |  |  | 2 |
| `pipe_meets_building_centre` | ● |  |  |  | ● |  | ● |  |  |  |  |  | 3 |
| `pit_cover_unlike_bridge` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `pit_covered_invisible` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `pit_covered_seam_at_max_zoom` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `pit_depth_ladder_legible` |  |  |  | ● |  |  |  |  |  |  |  |  | 1 |
| `pit_not_vanilla_trap` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pit_occupant_below_floor` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pit_occupied_distinguishable` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pit_reads_as_hole` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pit_reads_at_size` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pit_trapped_reads_as_trapped` |  | ● | ● |  |  |  |  |  |  |  |  | ● | 3 |
| `pit_walls_have_visible_depth` |  |  |  | ● |  |  |  |  |  |  |  | ● | 2 |
| `portable_ladder_leans_on_its_wall` |  |  |  |  |  |  |  |  |  |  |  | ● | 1 |
| `pump_hose_joins_at_side_port` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `raiders_never_shelter_in_a_cage` |  |  |  |  |  |  |  |  | ● |  |  |  | 1 |
| `reel_hose_leaves_brass_outlet_nozzle` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `reel_laid_and_wound_look_differ` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `reel_offers_choose_style` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `relay_chain_carries_liquid` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `relay_chain_reads_connected` |  |  | ● |  |  |  |  |  |  |  |  |  | 1 |
| `reservoir_fill_visibly_drops` |  |  | ● |  |  |  | ● |  |  | ● |  |  | 3 |
| `reservoir_recharge_progress_visible` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `reservoir_shoreline_recedes` |  |  |  |  |  |  |  |  |  | ● |  |  | 1 |
| `slime_occupant_below_surface` |  |  |  |  |  | ● |  |  |  |  |  |  | 1 |
| `slime_reads_as_viscous_not_water` |  |  |  |  |  | ● |  |  |  |  |  |  | 1 |
| `sluice_gate_state_legible` | ● | ● |  |  |  |  |  | ● |  |  |  |  | 3 |
| `spikes_read_distinct` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `still_water_one_surface_height` |  |  |  |  |  |  | ● | ● |  |  |  |  | 2 |
| `suspension_bridge_reads_hung` |  | ● |  |  |  |  |  |  |  |  |  |  | 1 |
| `tank_feeds_hose_without_pump` |  |  |  |  |  |  | ● |  |  |  |  |  | 1 |
| `tar_fill_front_lags_water` |  |  |  |  |  | ● |  |  |  |  |  |  | 1 |
| `trench_wall_cover_shown` |  |  |  |  |  |  |  |  | ● |  |  |  | 1 |
| `wall_ladder_rides_on_rails` |  |  |  | ● |  |  |  |  |  |  |  | ● | 2 |
| **bars per scenario** | 10 | 12 | 19 | 12 | 9 | 8 | 6 | 8 | 7 | 9 | 2 | 14 | 116 |

Result: **81 of 81 bars** appear in at least one scenario; 116 bar-appearances in all (mean 9.7 per scenario), against
one station = one or two bars today. Bars seen in only one scenario are the thin spots (listed in 4.3).

### 4.3 What the set adds, and its thin spots

**New to the review map** (no station today; checked by grep of `review_map.py`): sprinkler heads, pipe poles and the
overhead span, the GSS power cord to a winch, drawbridge gate + winch + leaf, suspension bridge, grated deck and jetty
(walk-under), guardrail, portable ladder, climbing gear, rail ladder lowered-only-from-above, raiders' plank / ladder /
fill-in, trench cover in the hit-chance, titan-wide trench, swimming (R12), drip filter, reaction vat, thirst and
administering water, flow meter, timer switch, level holder, liquid thermostat, map edge setter, limitless marker,
gravity-fed hose (tank without pump), communicating tanks, hose free-end roles, a hose through a GSS wire span.

**Interactions no station can show:** pump power → sprinkler net → crop; maze route → hose length limit → relay;
flood a pit → swimmer rises vs non-swimmer drowns; timer → sluice → level solve → swimmer rises; raid → trench cover
+ ladders + plank + gate refusal; fill-in → water returns to its pond; tar vs water race in one frame.

**Bars in one scenario only** (57): `canal_fill_front_watchable`, `canal_fill_spreads_along_itself`, `canal_fire_reaches_reservoir`, `canal_holds_only_the_channel`, `canal_partial_fill_distinct`, `canal_reads_as_same_liquid_as_reservoir`, `fill_tier_legible`, `filled_excavation_reads_as_obstacle`, `four_reel_looks_distinguishable`, `geared_pawn_scales_built_wall`, `hose_carries_real_units`, `hose_dropped_carries_nothing`, `hose_far_end_pump_reaches_reel_tank`, `hose_follows_port_changes`, `hose_joiner_reads_brass_screwed_together`, `hose_plump_when_flowing_flat_when_not`, `hose_plumps_only_from_powered_pump`, `hose_thicker_stiffer_than_cord`, `hose_tint_is_carried_liquid`, `jump_into_pit_lands_unhurt`, `ladder_state_legible`, `limitless_body_marked`, `never_external_pipe_carries`, `never_full_reservoir_after_heavy_draw`, `never_gravel_path`, `never_hose_across_impassable`, `never_liquid_on_open_ground`, `never_reads_as_building`, `never_snared_standing`, `pawn_height_ladder_legible`, `pawn_walks_under_deck`, `pit_cover_unlike_bridge`, `pit_covered_invisible`, `pit_covered_seam_at_max_zoom`, `pit_depth_ladder_legible`, `pit_not_vanilla_trap`, `pit_occupant_below_floor`, `pit_occupied_distinguishable`, `pit_reads_as_hole`, `pit_reads_at_size`, `portable_ladder_leans_on_its_wall`, `pump_hose_joins_at_side_port`, `raiders_never_shelter_in_a_cage`, `reel_hose_leaves_brass_outlet_nozzle`, `reel_laid_and_wound_look_differ`, `reel_offers_choose_style`, `relay_chain_carries_liquid`, `relay_chain_reads_connected`, `reservoir_recharge_progress_visible`, `reservoir_shoreline_recedes`, `slime_occupant_below_surface`, `slime_reads_as_viscous_not_water`, `spikes_read_distinct`, `suspension_bridge_reads_hung`, `tank_feeds_hose_without_pump`, `tar_fill_front_lags_water`, `trench_wall_cover_shown`. These are fine where the
scenario is the natural home; a second sighting is cheap where marked in the build order.


## 5. Build order

### 5.1 How it is built (one builder, existing machinery)

- **One new file, `src/RimMandrake/FlowWorks/review_map_composite.py`**, importing `review_map.Review` (fresh map, calm,
  clear, stage, gizmo_cycle, hose_probe, late_hoses, labels, goto, verify_gallery, save) instead of copying it. A
  `SCENARIOS` dict replaces `SETUPS` with the same keys (`dig`, `fluid`, `terrain`, `build`, `tank`, `pump`, `hose`,
  `hose_flow`, `ladder`, `pawns`, `hostile`, `style`, `marks`, `try_`, `look`) plus three new ones: `parts` (labelled
  sub-points for the in-world marks), `markers` (the `Place*` map-maker calls: meter, timer, level holder, edge setter,
  thermostat, painter), `pens` (hostiles behind a shut grate). Plot = 40-48 cells, pitch 50: a 4x4 grid of plots fits
  inside the 230-cell buildable square of a 250 map with room for the free area, S0 board and V block.
- **Coverage stays data**: `review_map_coverage.py` gains a scenario route so `COVERAGE.md` maps every inventory item to
  a scenario (or the V block / lake map), and `--plan` still fails on any uncovered item. §4 above is the design-time
  version of that check.
- **Verify per scenario** = today's `verify_gallery` (dug cells, things present, pawns) + labels present + one
  *goal read* per scenario (e.g. C3: the hose route length and the pit's litres-to-2 m; C8: the timer's hours read
  back), so a scenario that cannot reach its goal is caught before he walks it.
- Map R scenarios (C1, C11) extend `review_map_rivers.py`; it already anchors on real crossings.

### 5.2 Order (most coverage per hour first)

| # | scenario | stations / bars | new staging | why here |
|---|---|---|---|---|
| 1 | **C3 Labyrinth Rescue** | 13 / 19 | ~180 lines | the owner's named loss (the maze); the richest bar set; all hose machinery already staged |
| 2 | **C12 Oubliette and Kennel** | 12 / 14 | ~110 | pure re-lay of `pit_*`/`hold_*` + `row_ladders`; covers the pit-access bars accepted 2026-10-20 |
| 3 | **C5 Fuel Depot** | 15 / 9 | ~120 | most stations per line of code; fire rules; overflow D5 hook ready |
| 4 | **C10 Rain Basin** | 11 / 9 | ~150 | all reservoir bars; the overflow scenario-in-waiting |
| 5 | **C6 Tar Seep** | 11 / 8 | ~110 | viscous-liquid bars; tar look tune happens here with him |
| 6 | **C4 Wet Quarry** | 9 / 12 | ~150 | dig ladder and climbing; 2 m colonist cap visible |
| 7 | **C2 Drowned Keep** | 7 / 12 | ~300 | most new pieces (drawbridge, bridges, raiders); expensive, but the showpiece |
| 8 | **C8 Canal Lock** | 4 / 8 | ~90 | cheap; level-solving and the map-maker markers |
| 9 | **C7 Bathhouse and Water Tower** | 9 / 6 | ~170 | thirst and stills; gravity hose |
| 10 | **C9 Trench Line** | 4 / 7 | ~130 | needs the raid-trench rows to pass first or it shows known failures |
| 11 | **C11 Prospector's Creek** (map R) | 11 / 2 | ~60 | cheap but needs the river map; build with C1 in one river session |
| 12 | **C1 Thirsty Terraces** (map R) | 7 / 10 | ~250 | the sprinkler/pipe-pole showpiece; waits for the pipe and hose girth redraws so he judges the new art |

Steps 1-6 (~820 lines, roughly two FOUNDRY sessions plus one ~12-minute live build) cover **63 of the 96 stations**
and most bars; he can walk those six while 7-12 are built. The old 88-station gallery stays buildable until the
composite map's `COVERAGE.md` shows 0 uncovered; then it is retired (its setups are the composites' raw material).

### 5.3 What each scenario waits on (not blocking the build)

- C1: `PIPE_GIRTH_TUNE_HALF_AS_THICK`, `HOSE_GIRTH_TUNE_MUCH_THINNER` (judge new art, not old). C1/C5/C7/C10: overflow
  Stage 1 (§5 D1-D7 of `canal_overflow_flooding_2026-10-21.md`) to show their DEFERRED pokes.
- C2/C9: raider rows of `raid_trench_proof.py` (A2-A7 L2) and suspension live rows, else he sees known failures.
- C4: the machine-dig re-scope (`DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL`).
- C12: flyers only with him present.

## 6. GPT critique — taken / rejected
(pending)
