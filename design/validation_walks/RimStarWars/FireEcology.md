# Fire Ecology — validation walk
subject: src/RimMandrake/Pyrelands  (packageId mandrake.rm.pyrelands)
feature: fire-ecology-biome-origin
absorbed: FireEcology (dying id rsw.fireecology) was promoted whole to a RimMandrake-tier mod and renamed Pyrelands in Sprint wave A (commit 485380d4) — Pyrelands's own About.xml no longer mentions "FireEcology" by name; RimUtinni/PyrelandsFireEcology.md is the separate campaign-side wiring walk that still names it explicitly.
deps: brrainz.harmony (hard), Ludeon.RimWorld base (declared modDependency, always present)
list: minimal   # no third-party mod dependency; the ash ladder/terrain/weather all ride vanilla mechanisms
status-hint: generic desert-savanna fire-ecology engine — scorchable-ground → ash-ladder terrain chain, a Black Rain weather that follows and extinguishes a large fire, fire-triggered fulgurites/scorch-fruit, a firefoam sprayer + firebreak strip. Campaign wiring (which biome uses it) lives in RimUtinni, not here.

## must be true
- The four scorchable-ground TerrainDefs (RM_FE_Ground_Sand/Gravel/Soil/SoilRich) each burnedDef-chain into RM_FE_Ash_Trace, and Trace→Light→Heavy→Deep chain forward with pathCost climbing (1→2→9→16) and fertility falling (0.5→0.25→0.05→0.0) at each rung.
- RM_FE_BlackRain (WeatherDef) has rainRate 1.1 and isBad true — it rides vanilla's ChanceFactorRainOnFire/FireWatcher.LargeFireDangerPresent mechanism unmodified, so this mod defines no eventMakers.
- RM_FE_FirefoamSprayer exists with a working verb, and RM_FE_FirebreakLine is a buildable zero-fertility terrain.
- RM_FE_Plant_ScorchFruit never appears in any biome's wildPlants list (it only spawns via the C# fire-tick hook) and rots via CompProperties_Rottable (daysToRotStart 1.1) if unharvested.
- The one C# hook (FireEcologyHookMod, Harmony ID mandrake.rm.pyrelands) patches WeatherEvent_LightningStrike.DoStrike (fulgurite spawn on sand-family ground, 35% chance) and Fire.TickInterval (loose-ash dusting + rare scorch-fruit seeding on scorchable ground, capped at 40 live scorch-fruit per map) — both postfixes, both no-op safely if their def targets are missing.
- ⛔ KNOWN, INTENTIONAL Config errors — do NOT flag these as failures: RM_FE_Ash_Trace/Ash_Light/Ash_Heavy each log "Config error in RM_FE_Ash_<x>: burnedDef is flammable" (vanilla's ConfigErrors() assumes burnedDef is terminal; the ash ladder deliberately isn't), and each of the four RM_FE_Ground_<x> terrains logs the same about burnedDef pointing at RM_FE_Ash_Trace. That is 7 expected Config error lines total, named in the .xml files' own comments.

## the walk
1. [L] Player.log after load contains exactly the 7 known "Config error in RM_FE_..." lines named above (4x RM_FE_Ground_*, 3x RM_FE_Ash_Trace/Light/Heavy) and no OTHER "Config error in mandrake.rm.pyrelands" or "Config error in RM_FE_" line, and no XML error naming AshLadder.xml, Firebreak.xml, ScorchableGround.xml, BlackRain.xml, Fulgurite.xml, ScorchFruit.xml, or FirefoamSprayer.xml
2. [L] Player.log contains both Harmony arm lines verbatim: "[RimMandrake.StarWars.FireEcology] fulgurite-spawn: armed; strikes on sand-family ground may leave a fulgurite" and "[RimMandrake.StarWars.FireEcology] fire-tick-ash-scorchfruit: armed; burning cells on scorchable ground may dust loose ash and rarely seed a scorch-fruit pod" (their absence means AccessTools.Method returned null — a game-version rename, not a config error)
3. [D] def read-back: TerrainDef RM_FE_Ash_Trace.burnedDef = RM_FE_Ash_Light; RM_FE_Ash_Light.burnedDef = RM_FE_Ash_Heavy; RM_FE_Ash_Heavy.burnedDef = RM_FE_Ash_Deep; RM_FE_Ash_Deep.burnedDef is unset (chain terminates)
4. [D] def read-back: TerrainDef RM_FE_Ground_Sand/Gravel/Soil/SoilRich each have burnedDef = RM_FE_Ash_Trace
5. [D] def read-back: WeatherDef RM_FE_BlackRain has rainRate=1.1, isBad=true, no eventMakers field set
6. [D] def read-back: ThingDef RM_FE_Plant_ScorchFruit has plant.harvestedThingDef = RM_FE_ScorchFruitYield, comps includes CompProperties_Rottable with daysToRotStart=1.1
7. [D] def read-back: ThingDef RM_FE_FirefoamSprayer resolves with a verb entry; TerrainDef RM_FE_FirebreakLine has fertility=0
8. [B] jawa/set_terrain {terrain: RM_FE_Ground_Sand} on a test cell → jawa/get_terrain_batch on that cell → expect RM_FE_Ground_Sand read back
9. [B] jawa/spawn_thing {def: RM_FE_Fulgurite} → expect a live thing (proves the def itself instantiates cleanly outside the Harmony hook's own rare-chance path)
X. [S] (human pass) ash-ladder terrain visual ramp (Trace→Deep) and Black Rain's sky-color/overlay read — out of scope here

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

**The ash ladder**
- [ ] `fireeco_burn_leaves_ash_ladder` — ground that has burned reads as ash, and a
      heavily burned patch (`RM_FE_Ash_Deep`) looks visibly deeper and darker than
      lightly burned ground (`RM_FE_Ash_Trace`).
- [ ] `fireeco_ash_gradient_follows_fire` — after a grass fire the ash shades from
      trace at the edges to heavy where the fire burned longest. (guess)

**Black rain**
- [ ] `fireeco_black_rain_reads_black` — `RM_FE_BlackRain` reads as dark, dirty rain
      over a fire, visibly different from ordinary rain. (guess)

**Fire's leftovers**
- [ ] `fireeco_fulgurite_reads_as_glass` — an `RM_FE_Fulgurite` on sand after a
      lightning strike reads as fused glass. (guess)
- [ ] `fireeco_scorchfruit_after_fire` — `RM_FE_Plant_ScorchFruit` pods appear on
      freshly burned ground and nowhere else.

**Fire control**
- [ ] `fireeco_firebreak_reads_as_strip` — an `RM_FE_FirebreakLine` reads as a
      cleared strip that a fire visibly stops at.

### cannot show

- [ ] `fireeco_never_green_after_fire` — burned ground still reading as green
      grass.
