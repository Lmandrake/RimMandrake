# RimMandrake: The Rot — validation walk
subject: src/RimMandrake/TheRot  (packageId `mandrake.rm.therot`)
deps: `mandrake.rm.environmentalhazards`, `mandrake.rm.creaturebehaviors` (modDependencies)
list: biomes tier; when folded into mandrake.rm.biomes it is active under the composed name (reads here are by def name)
status-hint: THE_ROT_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimMandrake/TheRot/About/About.xml`, `Defs/**`, `Source/RM_TheRotMod.cs`, `Source/RM_BiomeWorker_TheRot.cs`.

## must be true
- Every def the mod ships loads and resolves; a bogus name reads notFound. → defs_resolve.every_deployed_def_resolves
- `RM_TheRot` has animalDensity > 0 and plantDensity > 0 and its worker class is `RM_BiomeWorker_TheRot`. → biome_wiring.animal_and_plant_density_positive, biome_wiring.biome_worker_class_loaded
- Every Mod Settings field of `RM_TheRotSettings` round-trips. → settings_roundtrip.*
- Sheen exposure, accelerated rot, warm ground, live preparations, guardian groves, health sharing, pale tree, spore cloud, cross-biome mode. → map_mechanics.* (UNMEASURED: need a generated map and ticks)
- At most one wild hwelgrue lives on a map (setting): three spawn attempts leave one. → hwelgrue.map_cap_holds
- A hwelgrue keeps metal whole and destroys the rest: a steel knife goes into its gut, a wood stack is gone. → hwelgrue.digest_keeps_metal_only
- Its gut passes one Sheen casting; cracking it drops the metal at full hit points and empties the gut. → hwelgrue.casting_polishes_contents
- Where it rests, rottables within 6 cells rot faster than ones 20 cells away. → hwelgrue.rest_accelerates_rot
- A downed pawn lying in the open is swallowed whole (not spawned, held by the comp, named with hours left in the inspect line); 150 damage to the hwelgrue cuts it out alive. → hwelgrue.swallow_then_cut_out
- Knocking from inside is louder and of the strong kind early, fainter and failing late. → hwelgrue.knocking_louder_early
- Left inside past the digestion time the pawn dies and its metal gear joins the gut; swallowing toggled off, a downed pawn beside it is never taken. → UNCOVERED: needs a day of ticks; first poke: ProofSwallow, then step_game_ticks past the inspect line's hours.
- Exactly one hwelgrue per world carries the swallowed drive core; once it drops, none ever carries it again. → hwelgrue.one_core_per_world
- The carrier drops the drive core at or above the ruin threshold, the ruined core below it. → hwelgrue.ruined_below_threshold
- An installed, linked core multiplies the grav engine's TOTAL range (thrusters included) by 1 + bonus x integrity. → hwelgrue.core_multiplies_total_range
- Only the ship's own guns lower the core's integrity. → hwelgrue.ship_guns_wreck_the_core
- An idle hwelgrue crawls to and eats the nearest corpse or item on open ground, never one in a stockpile zone or under a roof, and never starts a fight. → UNCOVERED: needs ticks; first poke: RM_HwelgrueProof.ProofGrazeTarget with a knife on open ground and one in a stockpile.
- Studying the gut-mother sac unlocks its research; a fed vat returns a dead pawn's bionic arm, rifle and parka and consumes the body; an unfed vat does not progress; the starter keeps, trades, and a split makes one. → gut_mother.research_needs_studied_sac, gut_mother.digest_returns_implants_and_gear, gut_mother.hungry_vat_is_dormant, gut_mother.starter_keeps_and_trades
- The swallowed navigator's log reads one entry per 4 pings and reveals a salvage site at the second; pings after the carrier dies move nothing; a gravship landing beside a carrier pings at once. → navigator_log.entry_every_n_pings, navigator_log.carrier_death_cuts_log, navigator_log.landing_pings_at_once (UNMEASURED: needs a gravship landing)
- The Unjoining Draught purges parasites and symbionts (one husk per symbiont, one scar, the purge), gives a clean patient only the purge, and forces a metalhorror implant out. → unjoining.purges_parasites_and_symbionts, unjoining.clean_patient_only_purges, unjoining.forces_metalhorror_out
- The five Rot network bodies share wounds (chittik, gromma, rennok) or mend among kin (mullgoth, durrok), one RotNetwork tag across species; Health sharing off strips the comps from exactly those five. → UNCOVERED: no live chain yet (static wiring is `validation.py` static_checks, red 2026-10-22 when the donor retirement had dropped chittik/durrok/mullgoth); first poke: spawn two RM_Agaripod, damage one, read the other's health.

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RM_TheRotSettings`   # settings_roundtrip
3. [D] `jawa/get_defs BiomeDef/RM_TheRot fields animalDensity,plantDensity,workerClass`   # biome_wiring
4. [B] map-generation, weather and ticks mechanics   # map_mechanics (UNMEASURED)

## north star
state: DRAFT
validated-hash:

### the experience  (OWNER'S WORDS)
"A cathedral of mushrooms in the dark, generous and hungry. The Rot shares everything, including you."
(chosen by the owner from drafted options, by question card, 2026-10-20)

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1).
RULED OUT: "the RM_ ports inherited the donor's wound sharing" — only RM_Agaripod/RM_Agaripawn were ported with it; the AA_ FindMod patch was deleted at b28a7414f and the static check now names the five RM_ bodies.
