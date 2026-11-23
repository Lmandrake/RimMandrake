# Live-test needs per mod: hypotheses (pass one, m1)
Mods: FlowWorks (+Drawbridge), Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, ColdStorage, MachineLooks, Graffiti, WreckedMachines/droids.
Each line marked DESIGN (path) or GUESS. Repo-relative paths.

(sections follow)

## FlowWorks (pits, liquids, canals, bridges, raids) + Drawbridge
Sources: design/concepts/FlowWorks/scenes.json (27 scenes), design/concepts/FlowWorks_Drawbridge/sheet.md.
1. HOLD STILL
- Rain refills ponds and moats; sc_source_pays wants "5 days of rain" on purpose, every other scene wants none (lock weather per scene, both ways). DESIGN scenes.json sc_source_pays / sc_dig_and_read "no weather".
- Temperature: sc_ice needs it held below freezing, then raised on demand; elsewhere drift can freeze or thaw a canal. DESIGN sc_ice.
- Colonists' own jobs: haulers, diggers and wanderers walk into pads, pits and canals; idle pawns must be held (draft or no-work) except the one ordered. DESIGN sc_ways_out, sc_pawn_height (named colonist only); GUESS for the rest.
- Wild animals and visitors walking onto a covered pit or a bridge spoil "a hostile heavier than the tier" (sc_covered_pit) and the light-colonist control. GUESS.
- Storyteller raids/visitors during raid scenes (sc_moat_raid, sc_islands, sc_pit_trap_raid) other than the staged raid of 6. GUESS.
- Other liquid tickers (vanilla water, another mod's fluid, the FlowWorks river Endless source) moving litres in a conservation read. DESIGN sc_one_network "litres conserved", sc_sluice control "liquid deleted rather than moved".
- Fire spreading from sc_canal_fire / sc_toss_flame to the twin lanes; plant regrowth on pads (saplings in sc_fetch_fallen must stay). GUESS.
- Daylight: pictures need "daylight, play zoom". DESIGN sc_dig_and_read.
2. FORCE
- Open a sluice / canal on one named tick (two canals "on the same tick"). DESIGN sc_fill_front.
- A raid of N arriving at a chosen edge whose AI then chooses its own path (swim, walk the cover, ladder, attack a winch); force only arrival, never the path. DESIGN sc_moat_raid, sc_islands, sc_pit_trap_raid, sc_fetch_fallen.
- Player orders through the real UI/job path: dig, capture from rim, toss flame at a picked cell, raise/lower drawbridge ("a click ... answers at once", "a colonist comes, works it"). DESIGN Drawbridge sheet leaf:click_answers, leaf:order_gets_done.
- Set liquid litres/fill tier per cell and assert it (pads at D0..D16, F0..F4). DESIGN sc_fill_tiers, sc_dig_and_read.
- A real fire at one cell (not a spawned burn effect). DESIGN sc_canal_fire.
- Pawn state: downed raiders, trapped raider, geared vs ungeared colonist, thirst need. DESIGN sc_pit_reads, sc_ways_out, sc_garden.
- Save mid-swim / mid-swing, reload, toggle mod off/on. DESIGN sc_walk; Drawbridge leaf:walk.
- Freeze a pond / warm above freezing. DESIGN sc_ice.
3. OBSERVE
- Litres per cell and per network, per tick, summed (conservation). DESIGN sc_one_network, sc_sluice.
- Front position cell by cell over time (fill order, tar behind water). DESIGN sc_fill_front.
- Draw-time only: pawn draw offset by depth, "occupant below the lip", hose plump vs flat, wall faces, fill tiers, drawbridge leaf pose in 4 directions and 2 materials, ropes to winch side, no stretching, no line across gap. DESIGN sc_pawn_height, sc_hose_look, Drawbridge sheet leaf:up_or_down .. no_line_across_gap.
- Motion over frames at normal speed (drawbridge swing "one rigid leaf", no pop at 2x/3x). DESIGN Drawbridge sheet "delegated".
- One-tick events: fall onto spikes (damage on the tick), winch destroyed then bridge falls. DESIGN sc_covered_pit, sc_islands.
- UI: gizmo answer text and refusal reason; inspect readout agreeing with the picture; "Endless" readout; message on swept pawn. DESIGN Drawbridge leaf:click_answers, sc_river.
- Path choice of AI (did raiders swim or walk; path round open pit). DESIGN sc_moat_raid control, sc_pit_trap_raid control.
- Save-state digest before/after reload. DESIGN sc_walk.
- Long processes: dig "takes hours", one day in hole prison, 2 days river, 5 days garden growth. DESIGN sc_dig_finds, sc_hole_prison, sc_river, sc_garden.
4. REPEATS
- Mostly deterministic physics (fill, conservation, level) - one run plus a control twin side by side (the scenes already stage twins on one map). DESIGN control fields in scenes.json.
- Raid scenes are random by AI choice (who falls, who swims, who ladders); need several runs, one per map reload; copies side by side would interfere (raiders share one lord). GUESS.
- Durations: seconds to minutes of ticks for fills; 60k-300k ticks for 1-5 day scenes. DESIGN as above.

## Pyrelands (fire biome, ash, fire fauna; "titans" = Huge Things wake of the furnace-beast)
Sources: design/concepts/Pyrelands/scenes.json (30 scenes), design/concepts/Pyrelands/version/in_game/visit_7/SUMMARY.md.
1. HOLD STILL
- Weather: rain puts out fires and waters ash; scenes assert "weather locked Clear"; sc_no_rain needs the weather chooser left running, then forced Rain. DESIGN sc_roof_withers, sc_fire_sense, sc_no_rain.
- Wind direction and fire spread: must be set (sc_fire_walks_with_wind sets 90 then 270), else held; strips "ringed bare". DESIGN.
- Stray fire: the biome's own burn line and lone fires reach control pads (visit 7: control pad C "burned in the first run ... one candidate: a lone-fire lane"). DESIGN SUMMARY.md, sc_roof_withers "no fire within 20 cells".
- Wild fauna (fire-hawks carry embers, ullai herds graze, flamefang bites) wander into pads; pad animals must be counted and excluded or staged. DESIGN sc_firehawk "second fire-hawk ... more than 54 cells".
- Other mods' effects: Huge Things wake unroofs a furnace-beast's room (P_furnace_room FAIL). DESIGN SUMMARY.md.
- Colony vitals and pending incidents across multi-day waits (colonists starve on fire duty, raids). DESIGN sc_burn_compounds "colony vitals and pending incidents recorded".
- Time of day for pictures (skies captures at 10h-14h). DESIGN sc_three_skies.
- Temperature: two rooms "at the same temperature"; outdoor below 0 C for the hide bank on a tundra map. DESIGN sc_furnace, sc_furnace_hide_bank.
2. FORCE
- Light a real Fire at a cell; force the scheduled opening front (ProbeOpeningFront). DESIGN sc_burn_line_walks, sc_fire_sense.
- Force a weather or game condition for a fixed span (ash fall, cinderfall, black rain, forced Rain via GameCondition_ForceWeather). DESIGN sc_three_skies, sc_no_rain.
- Fire incidents through their own CanFireNow (herd migration, manhunter pack, foreign species). DESIGN sc_foreign_arrivals.
- A single damage hit of a chosen kind (Burn hit on an ashwallow); a hostile flamefang landing a bite, then removed. DESIGN sc_heat_dome, sc_flamefang_venom.
- Keep animals asleep / laid down on a pad. DESIGN sc_furnace_bed.
- Flip mod settings at load and live (PyrelandsMechanicsGate, windCarriesFireEnabled, furnaceBeastGiant). DESIGN.
- Generate a fresh map on a seed and tile with required features (a water body; ruins). DESIGN sc_ash_ground, sc_ruins (no new worldgen: a site from a known tile).
- Flyers: fire-hawk ember carry must happen by its own AI; "flight is not watched, only state read". DESIGN sc_firehawk.
3. OBSERVE
- Per-cell grids: ash depth (ProbeAsh on the sand grid), burn stamps, fire cells, terrain defs. DESIGN sc_ash_ground, sc_fire_dusts_ash.
- Per-plant values: GrowthRateFactor_Temperature, growth, hit points, inspect line RM_WithersUnderRoof. DESIGN sc_ash_watered, sc_roof_withers.
- Per-pawn job each 30 ticks for 600 ticks (RM_PyreStepAwayFromFire), hediff severity hourly, need levels (RM_Thirst) hourly. DESIGN sc_fire_sense, sc_flamefang_venom, sc_herd_thirst.
- 5-tick windows: domed within 5 ticks of hit, dome sprite at +60 (draw-time: bodyGraphic path). DESIGN sc_heat_dome.
- A thing carried by a flying animal and its drop cell (state only). DESIGN sc_firehawk.
- Letters stack (exactly one sighting letter); log tap from generation. DESIGN sc_firehawk_rewards, sc_populations.
- Pictures at play zoom, hourly for a day, each at an asserted hour; judge reads moving front vs ruler-straight lanes. DESIGN sc_burn_line_walks; SUMMARY.md.
- Long processes: 1 day, 3 days, 5 days, 7 days, a season, two weeks. DESIGN.
- Rare outcomes: crestfeather drop ("butcher 400 fire-hawks"). DESIGN sc_firehawk_rewards.
4. REPEATS
- Random by design: fire spread, furnace-bed ignition ("about two hours of sleep on average, never at once"), crestfeather chance, herd drift. DESIGN sc_furnace_bed, sc_firehawk_rewards.
- One run: minutes (dome, fire sense 600 ticks) to 420k ticks (7 days) to a season.
- Side-by-side copies: fire pads must be ringed bare and spaced (stray fire reached a control in visit 7); weather is map-wide, so weather twins need reloads of one save (sc_three_skies does that). DESIGN.

## PyrelandsMechanics (Deep Desert Tribes fire rite, visits, fruit defence)
Sources: design/concepts/PyrelandsMechanics/scenes.json (11), version/bars.md.
1. HOLD STILL
- Faction goodwill drift from unrelated events (gifts, quests, other raids) during the "goodwill unchanged" scenes. DESIGN sc_no_arson_tally.
- Storyteller incidents in the queue (a raid or letter that is not the Tribes'); recorded "pending incidents". DESIGN all scenes' start.
- Colonists wandering into the scar (sc_defence_reach wants only the ordered colonist); tame fire-hawk and furnace-beast behaviour that should NOT count as arson. DESIGN sc_no_animal_blame.
- Weather/fire as for Pyrelands (the burn line and fire clock must keep running). DESIGN start lines "burn line and fire clock running (asserted)".
2. FORCE
- Force the next scheduled front through rite_force_hook; fire RUT_FlameHarvest visit; in the walk, wait for the rite's own roll and record when the hook was used. DESIGN sc_rite_party, sc_visit_picks, sc_walk_tribes_season.
- Order a colonist to pick fruit / to shoot a harvester (player order, then NPC AI reacts). DESIGN sc_fruit_defence, sc_attack_raids.
- Advance days under a vitals and incident guard until a Tribes raid. DESIGN sc_attack_raids.
3. OBSERVE
- Each harvester's cell each game hour against the fire grid (never on a burning cell). DESIGN sc_rite_harvest_route.
- Lord/group membership and leaving; no lord left behind. DESIGN sc_walk_tribes_season.
- Messages and letters naming the faction; relation state; a later raid's faction. DESIGN sc_fruit_defence, sc_attack_raids.
4. REPEATS
- Random: party size within group min-max, who attacks, when rites roll. One run is game days to a season. Many copies on one map: no (one faction, one rite schedule per map). GUESS.

## ExplosiveKnockback (blasts throw pawns, corpses and goods)
Sources: design/concepts/ExplosiveKnockback/scenes.json (35).
1. HOLD STILL
- The thrown pawn's own job: it must not step off its cell before the blast (scenes stage "standing", "hauling a named stack"). DESIGN sc_pawn_arc, sc_mortar_throw.
- Other pawns walking into lanes (sc_pawn_hits_pawn needs one standing pawn, exactly where staged). GUESS.
- Fire from incendiary / gas bursts spreading to neighbouring lanes; smoke. DESIGN sc_cover_breaks, sc_gas_chain.
- Shield recharge, immunity window carry-over between lanes (the recovery window must be clean before each lane). DESIGN sc_recovery, sc_shield.
- Leftovers of earlier lanes (debris, corpses, broken doors) - each blast "on its own fresh staging". DESIGN sc_mass_and_power.
- Mod list: minimal list plus named extras (Deep Storage, Cauldron, FlowWorks) asserted; scene INVALID if the proof name is missing. DESIGN all scenes.
- Frame rate noise from other processes on the machine during the perf scene. DESIGN sc_barrage_perf ("owner's full list on Archmagi").
2. FORCE
- A real projectile of a chosen def landing on a chosen cell on a chosen tick (mortar shell, grenade, EMP, smoke, incendiary); a scripted explosion of given radius/damage. DESIGN sc_mortar_throw, sc_all_fly_no_cap, sc_killed_thrown.
- A melee blow and a rifle bullet at a pawn. DESIGN sc_only_explosions.
- Light a gas cloud at one edge cell. DESIGN sc_gas_chain.
- A scripted grenadier throwing on a cover cell during a mortar raid (keep the raid AI). DESIGN sc_walk_raid.
- Settings sweep without restart; save/reload inside the immunity window. DESIGN sc_settings_sweep, sc_recovery.
- A test hook that sleeps one frame 100 ms (probe self-check). DESIGN sc_frame_probe_check.
3. OBSERVE
- Every tick for 600 ticks: holder of the pawn (RM_PawnFlyer_Knockback), drawn position strictly between start and landing, height above zero, rotation; things in mid-air are unspawned. DESIGN sc_pawn_arc, sc_storeroom_mortar.
- One-tick events: wall hit, pawn hit, door hit, rebound at about 0.7 speed, descent into a pit, despawn-respawn. DESIGN sc_wall_stop, sc_goods_obstacles.
- Mod journal lines: launch, skip reason (too_heavy_creature, in_pit, immune, shield), stop reason, tuning source. DESIGN sc_spared, sc_lookup.
- Per-frame timing (99th percentile frame in a window at normal speed, unpaused). DESIGN sc_barrage_perf, sc_frame_probe_check.
- Container contents unchanged; hose end connected. DESIGN sc_closed_containers, sc_hose_drop.
4. REPEATS
- Mostly deterministic kernel (cells = baseCells x force x ratio x falloff); explosions have random damage/injury. One run 300-900 ticks. Lanes side by side work if far apart (the scenes already use lanes); blasts per lane on fresh staging. DESIGN sc_mass_and_power.

## GimmeSomeSlack (visible power cords, spans, shocks, taps)
Sources: design/concepts/GimmeSomeSlack/scenes.json (27).
1. HOLD STILL
- Colonists rebuilding or repairing conduit, re-stringing spans by their own work queue before the scene reads the cut. DESIGN sc_restring (the job is wanted only there).
- Power state drift: solar/wind generators changing with time and weather; batteries draining; short circuits (vanilla zzztt events) and solar flare. GUESS.
- Things set on cords moved by haulers (sc_cords_under_items battery/bed/steel stack). GUESS.
- Fire from sparking ends spreading (sc_fuel_ignition wants "nothing else burning or hot within 5 cells"). DESIGN.
- Faction goodwill drift (sc_tap_theft "every other faction's goodwill unchanged"). DESIGN.
- Visitors and pawns other than the named hauler crossing a sparking end. DESIGN sc_shock (roles named).
- Machine load for the 20 ms slice bar (sc_rewire_cost, sc_walk). DESIGN.
2. FORCE
- Destroy one named conduit cell or mast; explode a charge under a span. DESIGN sc_cut_ends, sc_fallen_span.
- A hauler hauling along a path that crosses the end; a visitor walking across; the re-stringer's path asserted to cross (orders that leave pathing to the game). DESIGN sc_shock, sc_floor_end_shock.
- A neighbour faction's powered line on our map and one of their pawns brought into sight. DESIGN sc_tap_theft.
- Hand a building to another faction. DESIGN sc_owner_change.
- Gravship launch and landing (never watch the flight). DESIGN sc_gravship; standing ruling.
- Settings flips live with no restart; load a save on a list minus GSS. DESIGN sc_settings, sc_removal_consequence.
3. OBSERVE
- Draw-time geometry: each cord's drawn curve vs chord, bend radius, sampled points vs walkability, altitude and render queue under items, span altitude above pawns. DESIGN sc_cords_slack, sc_walls, sc_cords_under_items, sc_spans.
- Static printed-section state (SectionLayer_RM_MessyCords.PrintedStatic). DESIGN sc_statics_new_game.
- PowerNet membership, live/dead per end per poll (250 ticks). DESIGN sc_cut_ends.
- One-tick shock on a pawn crossing a cell; fire on a puddle cell. DESIGN sc_shock, sc_fuel_ignition.
- Per-action slice ms and frame time. DESIGN sc_rewire_cost.
- Alert content and camera position after jump. DESIGN sc_restring.
- A judge agent reading captures (tangle, no repeated stamp, grayscale looks). DESIGN sc_dense_tangle, sc_no_repeat, sc_four_looks.
4. REPEATS
- Cord shapes are seeded per edge (deterministic); shocks are by crossing (deterministic). Goodwill fall daily over 2 days. Many runs side by side on one map work for geometry (separate nets one cell apart is itself a scene); shock scenes need isolated paths. DESIGN sc_true_to_grid; GUESS for the rest.

## Graffiti (painting sprees, marks, thoughts, raider tags and pressure)
Sources: design/concepts/Graffiti/scenes.json (30).
1. HOLD STILL
- Colonists' own mood breaks, joy choices and cleaning: an unforced spree, a recreation pick or a cleaning job can paint or scrub marks off-script; sc_scrub_protection wants "700 ticks unforced" then forced cleaning. DESIGN sc_scrub_protection, sc_own_fun.
- Social drift: opinions, fights and thoughts from causes other than marks (sc_fights "the mark as its reason"; sc_rereads "refreshes at most once per day"). DESIGN.
- Storyteller raids and traders outside the staged ones; storyteller points must be equal for A and B (sc_raider_pressure). DESIGN.
- Weather and roofs age marks (WeatherDays); unroofed marks despawn. DESIGN sc_weathered_raid_mark.
- Ideoligion state (glyph pool by meme; "ideoligions off"). DESIGN sc_sigil, sc_settings.
- Wall loss from other causes (fire, raids breaching). DESIGN sc_wall_loss (wanted only there).
2. FORCE
- Force a named colonist's painting spree and let its length run; force a paint job of a named mark on a cell. DESIGN sc_spree_corridor, sc_player_orders.
- Move a raid lord to its leaving toil (exit tagging); send a breaching raid and let its lord choose the target. DESIGN sc_raid_exit, sc_breach_bias_raid.
- Trigger a faction's next raid at given storyteller points; a trader caravan visit. DESIGN sc_raider_pressure, sc_visitors.
- Lower a colonist's mood to a break (clean freak cleaning break). DESIGN sc_temperament.
- Age a mark by setting its placed tick back (time travel for one object). DESIGN sc_weathered_raid_mark.
- Feud/rival relations and traits (psychopath, sensitive, clean freak) set on chosen pawns. DESIGN sc_mockery, sc_temperament.
3. OBSERVE
- Thoughts and their stages per pawn per hour/day (EnemyClaim stage vs mark count; maker, hostile, mood flags). DESIGN sc_raid_retaken, sc_hostile_thought.
- Room beauty before/after. DESIGN sc_art_skill.
- Draw-time: mark on the wall's front face climbing the crease, face bolder than top; 64 px captures read by a blind judge. DESIGN sc_wall_closeup, sc_spree_variety, sc_gallery.
- Lord's toil and breach target choice (FindBuildingToBreach). DESIGN sc_breach_bias_raid.
- Letters naming a faction and pointing at marks; goodwill change count per visit. DESIGN sc_raider_pressure, sc_visitors.
- Long processes: 2 days of rereads, 3 days of fights, 3 weeks of lived-in soak at top speed. DESIGN sc_rereads, sc_fights, sc_lived_in_soak.
4. REPEATS
- Random by design: spree length and marks, which kind, fights ("at least one confrontation" in 3 days), raid size modes. Several runs or long soaks. Six painter lanes side by side on one map work (sc_spree_wall); social scenes share colony-wide relations, so copies interfere. DESIGN sc_spree_wall; GUESS for the rest.

## ColdStorage (fridge-like chill units, stasis, seals) - design THIN
Sources: design/concepts/ColdStorage/admission_proposal.md (a PROPOSAL; no bars locked, no scenes.json), src/RimMandrake/ColdStorage/coldstorage_live_proof.py (A1-A6, never run live).
1. HOLD STILL
- Room temperature: the proof needs "a day in a 25 C room"; outdoor weather, doors opening, heaters/coolers of other mods drift it. DESIGN coldstorage_live_proof.py header.
- Power: "with no power the units warm back toward the room" - solar flare, a generator stopping, a short circuit. DESIGN admission_proposal.md vision.
- Haulers moving the meat in or out of the unit, colonists eating it. GUESS.
- Prisoner/colonist reach for the wall unit (A5: "prisoner inside may eat from it, one outside may not"). DESIGN.
2. FORCE
- Today the probe hand-ticks a day (jawa/static_call RM_ColdStorageProof.Run): no live game clock. DESIGN live_proof header. A real-clock day would need ~60000 ticks of held temperature. GUESS.
- A gravship lift and set-down on the same map (no flight). DESIGN A6.
- Seal aging past due by one tick (A4). DESIGN.
- "a crude unit can frost up and need a pawn". DESIGN proposal (no mechanism in a bar yet).
3. OBSERVE
- Rot ticks per stack and item temperature over a day; setpoint after landing. DESIGN A1, A6.
- Inspect text: "says on inspect what it holds and how cold it is". DESIGN proposal.
- Art read at play zoom (own art owed, none exists). DESIGN proposal.
4. REPEATS
- Deterministic rates; one day (60000 ticks) per clause; many units side by side work only in separate rooms (room temperature is shared). GUESS.

## MachineLooks (look picker for vanilla electrical objects) - design THIN, mod does not exist
Sources: design/concepts/MachineLooks/admission_proposal.md: "Mod folder: none ... Tests, Mod Settings, live proof: none".
1. HOLD STILL
- Ideoligion style overwriting a picked look, and back ("no silent overwrite either way"). DESIGN proposal.
- GSS loaded or not changes the default look. DESIGN proposal.
2. FORCE
- Build a battery, pick each of four looks through the shared picker, in three facings. DESIGN proposal.
3. OBSERVE
- Draw-time: which texture is drawn per look and facing; picture judged at true scale. DESIGN proposal, kept_art.md.
4. REPEATS
- Deterministic; all looks side by side on one map (GSS sc_four_looks does the same). GUESS.

## WreckedMachines and droids (Droidworks, DroidRepairJobs)
Sources: design/validation_walks/RimMandrake/WreckedMachines.md (north star VALIDATED), design/validation_walks/RimStarWars/Droidworks.md (north star DRAFT, "the experience (not yet dictated)"), design/validation_walks/RimUtinni/DroidRepairJobs.md. No design/concepts/ folder for any of them.
1. HOLD STILL
- WreckedMachines: Research Reinvented present or absent changes the walk (MayRequire study option). DESIGN WreckedMachines.md walk step 8.
- WreckedMachines: VEF breakdowns of the kludged tier (VEF_BuildingBreakdownFactor 6) during a run. DESIGN must be true. Power supply for the 360/300 W tiers. GUESS.
- Droids: power need draining (RSW_DW_Power), charger power; ion weapons present or absent. DESIGN Droidworks.md.
- DroidRepairJobs: the generator picks the settlement's faction, so tech/goodwill scaling cannot be held ("depends on the faction of whichever settlement the generator picks"). DESIGN DroidRepairJobs.md.
2. FORCE
- WreckedMachines: finish research, then the player builds the repaired tier over the wreck (replaceTags build-over by a colonist). DESIGN walk step 7.
- Droids: an ion hit that powers a droid down; a reboot recipe at a shop. DESIGN Droidworks.md status-hint.
- DroidRepairJobs: fire the quest (fire_quest bypasses the pool); the customer walks in, the player fits a part of a chosen quality; pickup; arrest or death of the droid. DESIGN DroidRepairJobs.md UNCOVERED lines.
3. OBSERVE
- Art reads: three tiers told apart at play zoom; droid five-state overlays; droid docked at a charger. DESIGN WreckedMachines.md must show, Droidworks.md must show.
- Quest signals (lodgers.Arrested / Destroyed), goodwill history event lines, silver at the landing spot. DESIGN DroidRepairJobs.md.
- Storyteller pool offering over days (weight 1.1, refire 15 days). DESIGN DroidRepairJobs.md.
4. REPEATS
- Quest outcome by part quality is deterministic; pool offering is random over many days; one quest run is days. Several wrecks side by side work. GUESS.

## Cross-mod table
Counted over 9 sections: FlowWorks, Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti, ColdStorage, MachineLooks, Wrecked/droids.
| need (plain words) | mods that need it | count of mods |
|---|---|---|
| keep idle colonists, haulers and wanderers out of the scene; only the named pawn acts | FlowWorks, Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti, ColdStorage | 7 |
| give a player order through the real job path and let the game choose the path and the doing | FlowWorks, PyrelandsMechanics, GimmeSomeSlack, Graffiti, ColdStorage, MachineLooks, Wrecked/droids | 7 |
| read what is DRAWN (pose, offset, texture, altitude, curve), not only the state | FlowWorks, Pyrelands, ExplosiveKnockback, GimmeSomeSlack, Graffiti, MachineLooks, Wrecked/droids | 7 |
| pictures at play zoom judged by someone who did not make them, at a set hour and light | FlowWorks, Pyrelands, GimmeSomeSlack, Graffiti, ColdStorage, MachineLooks, Wrecked/droids | 7 |
| hold storyteller raids, visitors, traders and other incidents; record the pending queue | FlowWorks, Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti | 6 |
| lock weather (or force one weather or condition for a set span) | FlowWorks, Pyrelands, PyrelandsMechanics, GimmeSomeSlack, Graffiti, ColdStorage | 6 |
| flip a mod setting live, read it back, restore defaults, no restart | Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti, Wrecked/droids | 6 |
| run long game time (days to weeks) safely: colony vitals guard, no starving, no death | FlowWorks, Pyrelands, PyrelandsMechanics, Graffiti, ColdStorage, Wrecked/droids | 6 |
| save mid-action, reload, compare a state digest | FlowWorks, Pyrelands, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti | 6 |
| stage a control twin beside the test case, far enough apart not to touch | FlowWorks, Pyrelands, ExplosiveKnockback, GimmeSomeSlack, Graffiti, ColdStorage | 6 |
| bring in hostiles (a raid of N, one hostile, a lord) and leave their choices to their AI | FlowWorks, PyrelandsMechanics, ExplosiveKnockback, GimmeSomeSlack, Graffiti | 5 |
| read per-tick or per-poll values in a window (job, position, holder, litres, power live/dead) | FlowWorks, Pyrelands, ExplosiveKnockback, GimmeSomeSlack, ColdStorage | 5 |
| catch one-tick events (hit, fall, shock, despawn, rebound, ignition) without missing them | FlowWorks, Pyrelands, ExplosiveKnockback, GimmeSomeSlack, Graffiti | 5 |
| hold or set temperature (room or map) | FlowWorks, Pyrelands, GimmeSomeSlack, ColdStorage | 4 |
| stop stray fire spreading into lanes or controls | FlowWorks, Pyrelands, ExplosiveKnockback, GimmeSomeSlack | 4 |
| read pawn thoughts, needs, hediff severity, relations, goodwill over time | Pyrelands, PyrelandsMechanics, Graffiti, Wrecked/droids | 4 |
| read letters, messages, alerts and inspect text | FlowWorks, Pyrelands, PyrelandsMechanics, Graffiti | 4 |
| assert the loaded mod list and the deployed DLL are current (stale mod spoils the run) | Pyrelands, ExplosiveKnockback, GimmeSomeSlack, Graffiti | 4 |
| hold faction goodwill against unrelated drift | PyrelandsMechanics, GimmeSomeSlack, Graffiti, Wrecked/droids | 4 |
| light a real fire at a chosen cell | FlowWorks, Pyrelands, ExplosiveKnockback | 3 |
| fire an incident or quest through its own CanFireNow, and wait for a natural roll | Pyrelands, PyrelandsMechanics, Wrecked/droids | 3 |
| land a real projectile or damage hit of a chosen kind on a chosen cell and tick | Pyrelands, ExplosiveKnockback, GimmeSomeSlack | 3 |
| hold other mods' tickers (other liquids, Huge Things wake, other heaters) | FlowWorks, Pyrelands, ColdStorage | 3 |
| frame-time and slice-time measurement at normal speed on a quiet machine | FlowWorks, ExplosiveKnockback, GimmeSomeSlack | 3 |
| many random runs (rates, chances) with a count of cases | Pyrelands, Graffiti, Wrecked/droids | 3 |
| a flyer or gravship moves and only state is read (never watch flight) | Pyrelands, GimmeSomeSlack, ColdStorage | 3 |
| motion over frames at normal speed (a swing, an arc) | FlowWorks, ExplosiveKnockback | 2 |
| set liquid litres or an object's age/placed tick directly | FlowWorks, Graffiti | 2 |
| fresh map from a known tile with required features (no worldgen) | Pyrelands | 1 |

Could not read / thin: ColdStorage and MachineLooks have no locked bars and no scenes (proposals only; MachineLooks has no mod). Droidworks' experience is "not yet dictated"; WreckedMachines/Droidworks have no design/concepts folder. Graffiti exam_control/, FlowWorks test_table.json (265 kB) and exercises.json were not read; scene 'hold' fields were read only for FlowWorks.
