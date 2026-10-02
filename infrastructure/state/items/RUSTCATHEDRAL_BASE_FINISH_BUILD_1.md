# RUSTCATHEDRAL_BASE_FINISH_BUILD_1 — finish what the Rust Cathedral was promised: the line-cycle, hum reading, living coolant eels, overhead-sun heat, cooked strays, mynocks

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.rustcathedral`
(`src/RimMandrake/RustCathedral/`; folds into `RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`), plus
one campaign patch (the mynocks, part 6). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §1, §3, §4 row 0, §8; sheet
`design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` §3 (the line-cycle), §4 (the residents), §7 (hum
literacy), §9 (shadows). Ruling: **build first: finish the decided work plus the giant** (decision taken by
question card 2026-10-02 09:41 PDT). Every part below executes an existing ruling; nothing here is new
design. The seven hard bans of sheet §6 bind every line, above all **ban 1: no player text explains the
mind, the hum, the bolts or the eels**.

Siblings, same ruling: `RUSTCATHEDRAL_FREE_NAMES_TIDY_1` (land it **first**; this item is written against
its `RM_` names), `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` (the giant freezes in the line-cycle built here),
`RUSTCATHEDRAL_HULL_BOLTS_BUILD_1` (its off-plateau clue is read by the hum readers built here).

## spec

Reuse first: `RM_MapComponent_BiomeAttitude` and its bands, `RM_ThinkNode_ConditionalAttitudeBand`, the
bolt freeze, `RM_IncidentWorker_CathedralResponse` (a biome-gated incident worker: the line-cycle's shape),
`RM_CathedralFishing`, `RM_CompWaterLocked` (`src/RimMandrake/EnvironmentalHazards/Source/`, the
water-only confinement already built for the warden mother), `RM_SunHeatExtension`
(`src/RimMandrake/CreatureBehaviors/Source/`). 🔴 If any part seems to need a new system, re-read those first.

1. **The line-cycle** (sheet §3: *"a mile of machinery turning over in its sleep, and every living thing on
   the plateau stops until it passes"*). `IncidentDef RM_LineCycle`, worker `RM_IncidentWorker_LineCycle`,
   biome-gated to `RM_RustCathedral` exactly as the cathedral-response worker gates (category Misc, never a
   threat; base MTB a Mod Settings value, default about once per 8 days).
   - A deep rolling sound (`SoundDef RM_LineCycleRoll`, sustained, positional) travels across the map along
     one axis over 60 to 120 seconds of game time; a dust-shiver mote line runs along the deck plate under it.
   - The hum drops one band for the duration (call into the attitude component, never a second meter); the
     bolts freeze, which they already do on low bands.
   - **Every non-colonist, non-mechanoid-hostile pawn on the map stops where it stands** until the roll
     passes its position: a forced short wait job `RM_Job_LineCycleStill` (animals, the living eels, the
     borehulk giant, wild bolts). Colonists are **not** stopped; each colonist on the map gets the memory
     `ThoughtDef RM_FeltTheGroundTurn` (small, neutral-to-uneasy).
   - A plain message names what was felt, never why: *"Something turned over under the plate."*
   - Mod Settings: on/off, MTB, duration.
2. **Hum reading** (sheet §7: *"learnable, tradeable knowledge: reading the tones and the bolts' dances tells
   you what no instrument can"*). No stat buff anywhere.
   - `TraitDef RM_HumReader` (no stat offsets, no mood), granted by exposure: a map-component tally of hours
     each colonist spends on `RM_RustCathedral` ground while the band is calm (band 0 or 1); at a threshold
     (Mod Settings, default 5 in-game days total) the trait is added with a letter.
   - Tradeable: `ThingDef RM_HumPrimer`, a vanilla 1.6 book (`CompBook`) written by a hum reader at a desk
     (a recipe gated on the trait) and sellable; reading it to completion grants `RM_HumReader`.
   - The payoff: while any colonist with `RM_HumReader` is on the map, the attitude component's inspect
     readout names the current band in plain words (*calm, uneasy, sharp, alarmed*) and the bolts' current
     figure; with none, it shows nothing new. On any other map a hum reader near living bolts (or the hull
     bolts of `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1`) sees the same plain-words line on the bolt's inspect.
   - Mod Settings: on/off, threshold.
3. **The living coolant eel** (sheet §4; roster `new_defs`: canal-locked movement). `ThingDef` +
   `PawnKindDef RM_CoolantEel`: a small blind pale eel race, swimming only, carrying `RM_CompWaterLocked`
   (confines it to water cells: whatever water terrain the biome's map lays as the canals; read
   `RM_CathedralFishing.cs`'s cell test for the exact set), never tameable, never hunts, flees nothing,
   circles. Wired into `RM_RustCathedral/wildAnimals` at a low commonality on water maps only (or spawned by a
   map GenStep into the canal cells, if the vanilla spawner cannot place a water-locked animal: measure
   first). The catch item `RM_CoolantEelCatch` stays in `fishTypes` (the pair convention: a floor resident
   plus a catch). Butchering a living eel yields `RM_CoolantEelCatch` and triggers the existing eel-fishing
   hum consequence (`RM_NegativeFishingOutcome_CoolantEel`'s machinery). Art: `RM_CoolantEel` in
   `infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv`.
4. **Heat: overhead sun.** Add `RimMandrake.CreatureBehaviors.RM_SunHeatExtension` with
   `heatKind overhead` to `BiomeDef RM_RustCathedral`'s `modExtensions` (the planet's highest steady sun,
   +79°, median 62.5 °C; the deck plate's never-moving wall shadows are the shade, sheet §9). Default offsets
   unless the review's numbers argue otherwise. 📌 **Note for `SOLAR_HEAT_EXPOSURE_1`:** that item's spec
   tells its builder to *"list them [each extreme-heat biome] in the close note"*; the Rust Cathedral belongs
   on that list as **overhead**. This item declares it; whoever closes `SOLAR_HEAT_EXPOSURE_1` lists it
   (no edit to that item's prose is needed for the declaration to work).
5. **The cooked strays** (sheet §4: *"the desiccated dead are map dressing, not spawns"*). `GenStepDef
   RM_CathedralStrays`, self-gated to `RM_RustCathedral` (the wall GenSteps' gate): scatters a handful of
   animal corpses at the map edges at generation, rot stage forced to **dessicated**, kinds drawn from the
   neighbouring Scarlands and Scorch rosters (ordinary animals only, no humanlikes), each carrying a visible
   scaria scar where the engine allows (a dead pawn's hediff set before kill). Never a live spawn (ban 7).
   Mod Settings: on/off, count.
6. **Mynocks, campaign tier** (sheet §4: *"the one grazer that belongs… the Cathedral tolerates them, or
   grooms them"*; canon, so campaign-only; wired nowhere today). New patch
   `src/RimUtinni/UtinniPatches/Patches/WildAnimals_RustCathedral.xml` adds `RSW_Mynock` (already a real
   flyer, `MaxFlightTime 30`) to `Defs/BiomeDef[defName="RM_RustCathedral"]/wildAnimals` at a low
   commonality, guarded by `PatchOperationFindMod` on `mandrake.rsw.swbestiary` (**never** `MayRequire` on
   the `<Operation>` node, which the engine ignores; `PATCH_MAYREQUIRE_GUARD_INERT_1`). The mynock already
   lives on the Warscar (`WildAnimals_Warscar.xml`); this is deliberate multi-homing under the flyer
   carve-out and the sheet's *"one home, two ranges"*: annotate it in place in both patch files (precedent:
   the screecher, `29ccede91`), never "fix" it.
7. **Mod Settings**, added to the existing settings screens (`MOD_OPTIONS_RETROFIT_1` law): each part above
   has its toggle; map-generation toggles labelled as such; defaults = shipped behaviour.

Depends on: `RUSTCATHEDRAL_FREE_NAMES_TIDY_1` (names). Soft: `SOLAR_HEAT_EXPOSURE_1` (the extension exists
and is read by its built code today; its sun-cost pathing and shade grid apply here when built).
`RUST_CATHEDRAL_FIRST_SCRIPT_1` must be written against this item's state, not today's.

## criteria

Deterministic state reads through `jawa/get_defs` (reading `success`/`foundCount`/`notFound`) and debug
`[Tool]`s, recorded as cases in `RUST_CATHEDRAL_FIRST_SCRIPT_1`'s `validation.py`:
- Free tier: `IncidentDef/RM_LineCycle`, `SoundDef/RM_LineCycleRoll`, `JobDef/RM_Job_LineCycleStill`,
  `ThoughtDef/RM_FeltTheGroundTurn`, `TraitDef/RM_HumReader`, `ThingDef/RM_HumPrimer`,
  `ThingDef/RM_CoolantEel`, `PawnKindDef/RM_CoolantEel`, `GenStepDef/RM_CathedralStrays` resolve
  (`foundCount` = list length).
- `BiomeDef/RM_RustCathedral` carries `RM_SunHeatExtension` with `heatKind` = `overhead`.
- Line-cycle, on a generated free-tier Rust Cathedral test map with spawned animals: firing `RM_LineCycle`
  lowers the attitude band by one (read the component's band before/after); while active, every spawned
  non-colonist animal's current job is `RM_Job_LineCycleStill`; no colonist's is; after it ends every
  colonist on the map holds `RM_FeltTheGroundTurn`. Firing it on a non-Cathedral map returns `false`.
- Hum reading: a colonist given `RM_HumReader` makes the attitude readout return a non-empty plain-words
  band string; removing the trait makes it return empty. Advancing the exposure tally past the threshold on a
  calm band adds the trait; the same hours on a band ≥ 2 do not. Reading `RM_HumPrimer` to completion adds it.
- Eels: on a test map with canal water, spawned `RM_CoolantEel` count > 0 and every one stands on a water
  cell after 5,000 simulated ticks (each position's terrain read); none is tameable (`RaceProps` read).
- Strays: after generation, the count of corpses whose rot stage is Dessicated and whose cell is within 8
  cells of the map edge is > 0 with the toggle on, and 0 with it off; live pawn count from the GenStep is 0.
- Mynocks (campaign tier loaded): `RM_RustCathedral`'s merged `wildAnimals` (read as XML elements, never
  `<li>`) contains `RSW_Mynock`; with `mandrake.rsw.swbestiary` absent the patch applies nothing and the
  log has no error.
- Each Mod Settings toggle off removes exactly its effect (one case per toggle).
