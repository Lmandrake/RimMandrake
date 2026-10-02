# RimMandrake: Leaning Scrub — validation walk
subject: src/RimMandrake/LeaningScrub  (packageId `mandrake.rm.leaningscrub`)
deps: `mandrake.rm.environmentalhazards`, `brrainz.harmony`; ships composed inside the Baroque Biomes mod (Biomes.compose.json)
list: baroque_wave0
status-hint: a windswept fuzz-plain biome kit — the Stall and the Gale (wind calendar), the Lean (one wind heading per map), the twitcher lash, the smother-craft, dripping/crown venomvine, the runway bloom and named sweetline trees; script = `src/RimMandrake/LeaningScrub/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_leaningscrub.py`

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`. Sources: the mod's About.xml description, `RM_LeaningScrubMod.cs`, the mechanic `.cs` headers, `LEANINGSCRUB_MECHANICS_BUILD_1`, `LEANINGSCRUB_GPT_ENRICHMENT_1`, `LEANINGSCRUB_ENRICHMENT_QUICKTEST_1`.

Load and wiring
- Every def this mod ships (weathers, hediff, items, recipe, job, flora, 13 fauna kinds, the sweetline namer, the biome) resolves in the live game; none is silently discarded for a missing comp or extension type. → defs.defs_resolve
- `RM_LeaningScrub` runs its own windy twins `RM_ScrubWind` / `RM_ScrubWindFog` plus `RM_Stall` and `RM_Gale`, and carries no stock Clear, Fog, rain or snow commonality (ban 5: every ordinary day carries wind). → defs.biome_weather_table
- `RM_LeaningScrub` has `animalDensity` above 0 (below that its roster can never spawn) and names the fuzz, the four venomvine forms, the thicket and the whipfuzz/cruststar flora in `wildPlants`. → defs.biome_density_and_flora
- `RM_LeaningScrub` carries `RM_LeanExtension` (the marker that makes a map of this biome keep a wind heading). → defs.biome_lean_extension
- Each of the 13 wild kinds spawns a living wild pawn of that kind. → fauna.fauna_spawns
- `RM_Dustflutter` can fly (`MaxFlightTime` above 0): the runway bloom and the crown mob launch it. State read only; flight in the air is never live-tested unattended. → fauna.dustflutter_can_fly
- Every fuzz/shrub/venomvine plant def stands when placed. → flora.flora_spawns
- The five Harmony rules (Stall freeze on `JobGiver_Wander`, Gale turbine surge on the wind plant, Gale raid weighting on `IncidentWorker.ChanceFactorNow`, Lean scent on `JobGiver_AnimalFlee`, Lean fire on `Fire.TrySpread`) are armed, each owned by `mandrake.rm.leaningscrub`. → patches.rules_armed
- The shared `RM_VenomvineThicket` carries the smotherable comp (the patch matched; a patch that matches nothing logs nothing). → patches.thicket_smotherable
- Dead venomvine is accepted as fuel by a campfire (every refuelable whose filter names wood). → patches.dead_venomvine_fuels_fire
- All 25 Mod Settings fields exist and read their shipped defaults; a nonexistent field fails loudly. → settings.defaults
- The log carries no `LeaningScrub` error or warning and no cross-reference error naming one of this mod's defs. → log.log_clean

The Stall
- In the Stall, a wild animal no bigger than `stallFreezeMaxBodySize` holds still while a larger one keeps wandering. → stall.stall_freezes_small
- With `stallFreezeEnabled` off the small animal wanders in the Stall. → stall.stall_toggle_off_wanders
- With the master switch `modEnabled` off the Stall freeze does nothing. → stall.stall_master_off_wanders

The Gale
- An unroofed pawn in the Gale gains `RM_GaleDeafened`. → gale.gale_deafens_outdoors
- A roofed pawn in the Gale does not. → gale.gale_spares_roofed
- With `galeDeafenEnabled` off an unroofed pawn is not deafened. → gale.gale_deafen_toggle_off
- A running wind turbine produces `galeTurbineSurgeFactor` times its output in the Gale while `galeTurbineSurgeEnabled` is on. → gale.gale_turbine_surge
- A running wind turbine breaks down in the Gale at the mean interval `galeTurbineBreakdownMtbDays`. → gale.gale_turbine_breakdown
- Raids weigh `galeRaidWeightFactor` times heavier among threats while the Gale blows. → UNCOVERED: a statistical effect on the storyteller (debug_process §4); no bridge tool reads `ChanceFactorNow`; only the rule being ARMED is checked (patches.rules_armed)
- `galeRaidWeightingEnabled` exists, defaults on and is writable. → settings.galeRaidWeightingEnabled_roundtrip

The Lean
- Each map of this biome locks one wind heading for its whole life. → UNCOVERED: applies only to a map whose biome carries `RM_LeanExtension` and `RM_MapComponent_Lean` caches that answer on first use; the baroque_wave0 quicktest map is not a Scrub map; needs a Scrub site (LEANING_SCRUB_LEAN_SITE_1)
- A wild non-predator bolts from a person standing upwind of it within `leanScentRange`; downwind it never knows. → UNCOVERED: same Scrub-site gap (LEANING_SCRUB_LEAN_SITE_1)
- Fire spread picks downwind cells `leanFireBias` of the time. → UNCOVERED: same Scrub-site gap, and a statistical effect (LEANING_SCRUB_LEAN_SITE_1)
- `leanEnabled` exists, defaults on and is writable. → settings.leanEnabled_roundtrip
- `leanScentEnabled` exists, defaults on and is writable. → settings.leanScentEnabled_roundtrip
- `leanFireEnabled` exists, defaults on and is writable. → settings.leanFireEnabled_roundtrip

The twitcher lash
- With `twitcherLashEnabled` off a poised twitcher stand does not strike and reports no lash state. → lash.lash_toggle_off_quiet
- A poised twitcher stand strikes a pawn beside it once, then reads as spent and does not strike again within the hour. → lash.lash_strikes_once

The smother-craft
- The `RM_SmotherVenomvine` job banks a claim on a stand (the stand reads "smothered", a blanket is consumed). → smother.smother_claims_stands
- With `smotherCraftEnabled` off a due claim waits: the stand stands and reads as ready to fall. → smother.smother_off_holds_claims
- With it back on, a due claim dies back to `RM_DeadVenomvine` (about 40 per grown stand, scaled by `smotherYieldFactor`). → smother.smother_matures_to_dead_wood
- The `RM_Make_SmotherBlanket` recipe weaves a blanket from fuzz fibre and giant-wool at a tailoring bench. → UNCOVERED: the recipe is checked only to resolve (defs.defs_resolve); driving a bill needs a built bench and a crafter (no cheap fixture yet)

Venomvine rooms, the runway bloom, sweetline trees
- Harvesting a dripping venomvine stand leaves the stand standing (regrowing from growth 0.3) and yields `RM_RawVenom`. → dripping.dripping_survives_harvest
- With `drippingRegrowEnabled` off the harvest kills the stand. → UNCOVERED: the harvest-after-growth value is applied to the def at startup and on a settings write only; no tool triggers `WriteSettings`, so only the ON arm is driven
- While the Stall holds, wild dustflutters within range fly to a crown venomvine stand and settle around it. → crown.crown_mob_gathers
- With `crownMobEnabled` off they do not. → crown.crown_toggle_off_stays_away
- A person walking through the canopy sets off the bloom: crustweevils, fuzzrunners, dustflutters and visslers take Flee jobs; visslers drop `RM_VisslerArm`. → bloom.bloom_answers_a_walker
- With `runwayBloomEnabled` off nothing answers. → bloom.bloom_toggle_off_quiet
- A sweetline tree carries a generated name (its label) and a wool-timer line in its inspect text. → sweetline.station_named_and_timed
- With `sweetlineStationsEnabled` off the tree reads as a plain sweetline tree. → sweetline.station_toggle_off_plain
- A mature sweetline tree sheds 5 `RM_SweetlineWool` beside its trunk once its timer has passed. → sweetline.station_sheds_wool
- The tree's History panel lists dated entries (named, wool shed, struck). → UNCOVERED: the panel is a message-box dialog with no readable text through the bridge
- A sweetline tree keeps its name across save and load. → UNCOVERED: save migration is a boundary instrument (debug_process §4)
- Thickets block creatures above the huge body-size band on this biome only while `venomvinePassabilityEnabled` is on. → UNCOVERED: needs a huge pawn pathing through a thicket (the EnvironmentalHazards barrier's own script owns that); here only the toggle is checked
- `venomvinePassabilityEnabled` exists, defaults on and is writable. → settings.venomvinePassabilityEnabled_roundtrip
- The canopy reads as one even fuzz carpet all leaning the same way; the Stall reads as still. → UNCOVERED: visual; left to the judge pass (debug_process §4)

## the walk
1. [B] Tier: `python3 src/RimMandrake/Utils/modset_builder.py --tier baroque_wave0 --apply` (Windows-side seat only), launch via Steam, wait for `Bridge token:` in Player.log, start a quicktest map (150 cells or larger).
2. [B] `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod LeaningScrub --plan src/RimMandrake/LeaningScrub/northstar_plan.py` → results JSON in `Transient/northstar/`.
3. [L] Player.log after load has no `[RM LeaningScrub]` line saying "rule NOT armed" and no cross-reference error naming a LeaningScrub def   # load-time
Offline: `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py` runs the suite against a scripted fake game: healthy, then once per mod behaviour broken, each of which must turn exactly its own component red.

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The wind is always there**
- [ ] `scrub_lean_visible` — on a Leaning Scrub map the fuzz and scrub visibly lean
      one way, the map's wind heading, across the whole map. (guess: depends on
      what the Lean draws)
- [ ] `scrub_gale_reads_as_gale` — under `RM_Gale` the map reads as a gale: driven
      dust or fuzz, not a calm day. (guess)
- [ ] `scrub_stall_reads_still` — under `RM_Stall` small animals hold still across
      a short sequence of frames while big ones keep moving.

**Fuzz plain flora**
- [ ] `scrub_fuzz_plain_reads` — the ground cover reads as a soft fuzz plain,
      dotted with venomvine and thicket, not vanilla grass.
- [ ] `scrub_venomvine_forms_distinct` — the crown, dripping, twitcher and hollow
      venomvine forms are distinguishable from each other at play zoom.
- [ ] `scrub_sweetline_reads_as_landmark` — an `RM_SweetlineTree` stands out as a
      named landmark tree, bigger than the scrub around it.

**Fauna**
- [ ] `scrub_fauna_various` — the 13 wild kinds read as distinct animals in one
      line-up.
- [ ] `scrub_runway_bloom_launches_dustflutters` — a runway bloom sends
      `RM_Dustflutter` up in a visible burst. (guess; flight is never filmed
      unattended)

### cannot show

- [ ] `scrub_never_windless` — an ordinary Scrub day that reads as calm, still
      air (the biome bans calm).
- [ ] `scrub_never_lean_mixed` — plants leaning in different directions on one
      map. (guess)

## anti-guessing notes
- RULED OUT: "the smotherable patch on `RM_VenomvineThicket` matches nothing because the thicket has no `<comps>` node" — `EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml` carries one on the thicket; patches.thicket_smotherable is the guard if that ever changes.
- RULED OUT: "the lash can ride a plant comp tick" — plants only `TickLong`; the lash is driven by `RM_MapComponent_TwitcherLash` (source header). The check reads the effect, not the driver.
- RULED OUT: "a settings write via the bridge re-applies `RM_RegrowingHarvest`" — `Apply()` runs at startup and in `WriteSettings` only, so dripping's OFF arm is not drivable live (the walk line says UNCOVERED).
- RULED OUT: "`list_things countMatched` counts items" — it counts things; a stack of 5 wool is 1. The suite sums `stackCount` (`_stack_total`); the selftest's wool check goes red if that regresses.
- RULED OUT: "a lingering Gale after a chain only affects that chain" — a released weather lock keeps the last weather; every chain ends by setting vanilla Clear and starts by locking it, else a leftover Gale deafens the lash chain's colonist.
- ASSUMED (source comment in `RM_TheLean.cs`, not measured here): vanilla wild animals do not flee people. The bloom's OFF arm is the guard: a Flee job there would mean the assumption is false.
- UNPROVEN live shapes (first run settles them; each reads `UNMEASURED`, never PASS, when absent): the "Power output" inspect line of a wind turbine, `get_def` comps as a list of class names, `get_roof_batch.roofedCells`, `pawn_flight report` rows with `canEverFly`, `harmony_patches` naming the `get_DesiredPowerOutput` getter, `list_pawns includeHealth` hediff rows.
- Not driven because no cheap fixture: Lean (needs a Scrub-biome map), gravship/diving (not this mod), Utinni roster layer (UtinniPatches owns it).
