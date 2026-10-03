# FOUNDRY_REBOOT_HANDOFF_202610030327 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202610020551`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Messy Conduit (`mandrake.rm.messyconduit`, `src/RimMandrake/MessyConduit`) is built through phase 1b + aerial lines + 4 style families + hoses, all committed (HEAD aec7c56f3) and proven live by state reads; the design is `design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md`. Its premier-mod Northstar matrix (`northstar_matrix/run_live.py`, 109 scenes) runs in about 71 ticks per pass and found and fixed two real determinism bugs; the owner's rulings for it are on `MESSY_CONDUIT_MOD_1` (notes with his words). The game is UP on the flowworks tier and the bridge is released.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Look at the Messy Conduit screenshots in `Transient/messy_conduit_live_20261002/` (real_art_06_*, p1b_*, aerial_*, style_*, hose_A/hose_B) and the matrix review sheet `Transient/mc_matrix_live_20261002/review.html` (open from the WSL path; raw shots are local only, 500 MB, not committed).
- Decide: does the tolluk cap regen (`Transient/belt_art_agarilux_v3_compare.png`) replace the interim art (`TOLLUK_CAP_ART_REGEN_1`)?
- Wildpawn/Wildpod/Cactipine/Needlepost/Terrorworm are Alpha Animals but their ports are RSW_-prefixed (`ALPHA_ANIMAL_PORTS_REHOME_1`); Nysyllin is canon SW and stays RSW_.
- Tier-law skip: `AA_BoulderMit` -> `RSW_Korrum` in Nightside Ice needs a placement decision.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `MESSY_CONDUIT_MOD_1` -- phases 1a/1b, aerial, styles, hoses built; unbuilt: shader sway, floor ripple, live-end art, lamp mast/tap art, hose pump/tank (FlowWorks has none); NEXT: have the owner review the hose, aerial and style screenshots, then queue the remaining art and wire it.
- `MESSY_CONDUIT_MOD_1` ownership -- item still belongs to OWNER (reassign refused without his words); NEXT: reassign to FOUNDRY when the owner says so.
- `ALPHA_ANIMAL_PORTS_REHOME_1` -- filed, no spec; NEXT: write ## spec/## verify then re-home the five RSW_ ports to RM_ at each biome's own sitting.
- `TOLLUK_CAP_ART_REGEN_1` -- v3 render exists, not copied; NEXT: ask the owner to rule on the side-by-side compare.
- `PIT_SUPERDEEP_COLLAPSE_1` children -- CANAL_BOTTOM_SPIKES_1, LADDER_PRISON_DOOR_1, PIT_COVER_FALL_REWIRE_1, SUPERDEEP_PRISON_ROOM_1, LIQUID_BODY_FLUID_IDENTITY_1, PIT_FILL_EFFECTS_1 are filed; NEXT: claim CANAL_BOTTOM_SPIKES_1 (spikes only at depth 4) and run FlowWorks validation_v2.py before and after.
- Northstar -- FlowWorks v2 run is REFUSED by modcheck for 12 unbuilt bars (not failures); NEXT: run `python3 -m modcheck.cli floor --all` from src/RimMandrake/Utils and decide which unbuilt bars to build.
- Code review debt -- MessyConduit Core/CordBuilder, CordGraph, RM_MapComponent_CordGraph, SectionLayer and Hose files changed after review; NEXT: diff-review them and mark-clean.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Several lanes sharing one game starved each other for 45 minutes; run at most one live-game lane at a time (see: Transient/belt_mc_lane_d_20261002.md).
- `modset_builder --apply` overwrites `deployed/config/ModsConfig.before-tier-*.xml` on every run; the kept copy is `ModsConfig.before-tier-flowworks.kept-20261002.xml` (filed: lessons).
- `take_screenshot`/`screenshot_cell_rect` do not capture per-frame DrawMesh work (hoses, whip, sway); use `system_screenshot.py` cropped to the game window (see: Transient/belt_mc_lane_f_20261002.md).
- A cache key that omits one input to the computation reuses stale cords (the ring bug); a quote guard refuses --owner-said for a mid-turn chat message, so record it without the flag (see: MESSY_CONDUIT_MOD_1 notes).
- `rimflow claim/reassign` refuse items owned by OWNER without his words (see: using-rimflow).

## Closed since the last handoff (5)

- `FLOWWORKS_CHANNEL_OSCILLATION_1` — ddb4734162cf
- `FLOWWORKS_SHARED_SOURCE_STALL_1` — a8e179a4007f
- `SUPERDEEP_SEAM_MEASURE_1` — e79f8de4f89e
- `SUPERDEEP_HOLDER_RETIRE_1` — e79f8de4f89e
- `PIT_LEGACY_CODE_RETIRE_1` — e79f8de4f89e

## Filed and still open (110) — the next seat's queue

- `TOLLUK_CAP_ART_REGEN_1` — Regenerate AB_Agarilux (tolluk cap) art: too cartoonish; keep current as interim, replace only this one
- `PROPERTY_CLAIM_ERASE_API_1` — RimProperty: ClearForeignClaims API, wipe other parties' stored claims on a Thing or in bulk (Sump Sinking rite)
- `SUMP_SINKING_RITE_BUILD_1` — Sump Rite A, the Sinking: one valuable into the tar; Heat down, fewer raids, claims wiped; beast-sleeps and trap-fizzle riders
- `SUMP_EFFIGY_RITE_BUILD_1` — Sump Rite B, Mob'Unloo's Price: good thing + hated effigy; Empire held off 5x on this map, faction's next group tarred
- `SUMP_SOLVENT_WAKE_BUILD_1` — Sump solvent wake: pour solvent on a tar bulge, the tar beast wakes instantly manhunter; feeds Sh'kaar and Zizzik
- `BLUEDESERT_FLORA_EXPANSION_BUILD_1` — Build 4 admitted Blue Desert flora: Qeshra, Kethevar, Vashpuk, Lisqueth (+ roe, char-lace items)
- `CRACKEDLANDS_FLORA_EXPANSION_BUILD_1` — Build 6 admitted Cracked Lands flora incl. Zennaq lightning-draw C# (RM_FloodedCanyon)
- `CAULDRON_FLORA_EXPANSION_BUILD_1` — Build 6 admitted Cauldron flora: Tsevrix, Ixalith, Fexxil, Sessarix, Kissaveth, Selvix
- `CANAL_BOTTOM_SPIKES_1` — Spikes as per-cell hardware on a superdeep canal bottom (RM_Spikes)
- `LADDER_PRISON_DOOR_1` — Ladder raise/lower works like a prison door; ladder art
- `PIT_COVER_FALL_REWIRE_1` — Pit cover rehoused: multi-cell terrain-mimic cover that drops pawns into a superdeep cell
- `SUPERDEEP_PRISON_ROOM_1` — An enclosed superdeep area is a room; a prisoner bed makes it a prison; capture down / convert down from the lip
- `PIT_TEMPERATURE_SOFTENING_1` — Pit temperature couples hard to ambient and wears down resistance; Exposed Prisoner thought
- `DEPTH_FILL_COST_MATRIX_1` — Path cost as a depth × fill-tier matrix so flooded is always slower than dry
- `LIQUID_BODY_FLUID_IDENTITY_1` — Fluid identity per liquid body (retire per-map ActiveFluid); the merge rule
- `PIT_FILL_EFFECTS_1` — What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burning oil with an occupant
- `PIT_DEPTH_DRAW_OFFSET_1` — Pawns visibly sink and rise with canal depth; superdeep walls 20% above the head
- `EXCAVATION_WALL_ART_1` — Wall-face art for all four depths, spikes and ladder (Quarry perspective)
- `CRACKEDLANDS_PLANT_LIST_OWNED_1` — Cracked Lands owns its plant list: delete the campaign wholesale replace, move twisting thorns to RM_, drop 3 donor plants
- `WEBWORK_BASE_PORT_BUILD_1` — Webwork free tier: port anchor/web/gutter RUT_->RM_, wire the creeping front, free-tier thrixweave
- `WEBWORK_HEAT_SHADE_BUILD_1` — Webwork: declare overhead heat kind; ollathrix sun-scald reads the shade grid (tree shade)
- `WEBWORK_DEAD_GIANT_BUILD_1` — Webwork giant: wrapped urraveth skeleton, read bone by bone, loaded bones creak and collapse
- `WEBWORK_TRACTION_LANCE_BUILD_1` — Traction lance: capstan sibling on one shared pull, learnable at Webwork or Sump, fabric tether
- `WEBWORK_FELLED_NOON_RITE_1` — Rite: The Felled Noon for Sh'kaar (found in Webwork; fell tallest tree at noon, owners gather at shade line)
- `MESSY_CONDUIT_MOD_1` — Messy Conduit (mandrake.rm.messyconduit): conduit sprawls over the floor like real wiring; concept talk with the owner comes before any mock-up
- `GREENTIDE_BASE_PORT_BUILD_1` — Greentide free tier gets Roil, Breaklight, wet-bulb, dry-air blower, root causeways and living greatbole (RUT_ to RM_)
- `GREENTIDE_FREE_ROSTER_OWNED_1` — Free Greentide owns its animal list: sulleth, dhollock, yammeth, RM_ swinger and fruit; campaign op 1 Replace deleted
- `GREENTIDE_THURROCK_HERD_BUILD_1` — The thurrock: tree-felling giant herd on the built Shatterer aura (no moult)
- `GREENTIDE_STELLOCK_LACE_BUILD_1` — Stellock lace: study a self-sealing branch, craft a cartridge that stops all bleeding on a pawn anywhere
- `GREENTIDE_CEDED_ROOM_RITE_1` — The Ceded Room, for Ozzik: cede a room built outside the ship to the jungle; scales with room quality
- `WARSCAR_OPEN_BOAST_RITE_1` — The Open Boast, for Ozzik, found in the Warscar: a public boast, a warned challenge raid, once per colony
- `RUSTCATHEDRAL_FREE_NAMES_TIDY_1` — Rust Cathedral free mod: rename 19 RUT_ defNames and two Utinni namespaces to RM_ (eel catch to RM_CoolantEelCatch)
- `RUSTCATHEDRAL_BASE_FINISH_BUILD_1` — Rust Cathedral: line-cycle, hum reading, living coolant eels, overhead-sun heat, cooked strays, mynocks
- `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1` — Rust Cathedral giant: the borehulk, a colossal peaceful mining droid with a worn-out drill (three drill states)
- `RUSTCATHEDRAL_WORN_BIT_ARC_1` — The Worn Bit: unbolt the borehulk's drill, Junkers refurbish it, restore the giant; keep it to mine or free it
- `RUSTCATHEDRAL_HULL_BOLTS_BUILD_1` — Hull bolts: living bolts ride the ship for good as hull pets and the Cathedral's ears; reveal and dilemma
- `RUSTCATHEDRAL_MENDING_WELD_RITE_1` — The Mending Weld, for Rekko: rebuild a broken stretch of old structure into a whole room (Rust Cathedral rite)
- `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` — The Stranger's Overhaul, for Ohm: repair a free droid, capture it mid-repair or release it (Rust Cathedral rite)
- `ROT_RM_CAST_MIGRATION_1` — Move the ten ratified Rot creatures into the free mod as RM_ defs: hybrid descriptions, illoth flight, RSW_ rows retired
- `ROT_WOUND_SHARING_WIRING_1` — Wire wound-link and kin-mending onto the five Rot creatures whose descriptions promise it
- `ROT_SPORE_ALLERGY_PORT_1` — Our own spore allergy (people and animals) replaces the Alpha Biomes pair in the free Rot
- `ROT_MOD_SETTINGS_WIRING_1` — Make every control on the Rot's Mod Settings screen actually change the game
- `ROT_TIER_LEAKS_FIX_1` — Regate FungalSoilTrade from AB_MycoticJungle to RM_TheRot; take the Force off the free pale tree
- `ROT_HWELGRUE_GIANT_BUILD_1` — The hwelgrue: a huge slow maggot giant that eats whatever lies down and passes polished salvage castings
- `ROT_STILL_ALIVE_SWALLOW_1` — Still Alive In There: the hwelgrue swallows the downed; muffled knocking tells who is inside and how long
- `ROT_SWALLOWED_NAVIGATOR_1` — Swallowed Navigator: core pings the ship, log reveals salvage sites; extracted it boosts range; ship guns ruin it
- `ROT_GUT_MOTHER_VAT_1` — The Gut-Mother: a vat grown anywhere from the hwelgrue's sac returns implants and gear from corpses; starters trade
- `ROT_UNJOINING_DRAUGHT_1` — The Unjoining Draught: a brutal purge driving out parasites, symbionts and metalhorrors, anywhere
- `ROT_UNJOINING_RITE_1` — The Unjoining, for Ta'Baa: a symbiont-joined colonist purged until it dies, just before the clan leaves
- `FEVERWOOD_RM_CAST_COMPLETION_1` — Fever Wood: build the seven ratified creatures; the skreth brood as the free second front of the lure
- `FEVERWOOD_ANT_THEFT_RAIDBACK_1` — Fever Wood: kurreth carry thornbugs off alive; letter, track, column camp and hive raid-back
- `FEVERWOOD_CROWN_SOUND_HEAT_1` — Fever Wood: crown ambient sound for the sentinel hush to cut; heat kind ambient
- `FEVERWOOD_DIANOGA_GIANT_MAP_1` — Fever Wood campaign: map the dianoga over all six sekkulaath limbs, not just the tank
- `FEVERWOOD_TIER_LEAKS_FIX_1` — Fever Wood: donor-only patches (ancient danger, label, fish) onto RM_FeverWood; three Biomes! ports out of roster
- `FEVERWOOD_BROOD_RANSOM_1` — Fever Wood giant story: ransom of its young (world tally, release gift, young cask trade, Sporefall tank)
- `FEVERWOOD_OIL_BOIL_WEATHER_1` — Fever Wood weather: the oil boil (hot still days, doubled seep oil, spark flash fire wakes the deep)
- `WEEPINGSTONES_MURRIN_CATCH_WIRING_1` — Weeping Stones: murrin catchable (floor resident + RM_MurrinCatch in fishTypes); dead FISH_BY_BIOME_1 citations out
- `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` — Water truce suppression half: predators never start a hunt within the truce radius
- `WEEPINGSTONES_DEWSILK_COCOON_1` — Weeping Stones: dewsilk from mirrik cocoons (cocoon item, tamed-swarm harvest, cloth)
- `WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1` — Weeping Stones: heat kind by sun angle from latitude; rewrite the 12 dead wind-hour sentences
- `WEEPINGSTONES_OASIS_MUTATOR_FLORA_1` — Weeping Stones: register RM_/RUT_ with the Oasis mutator; Earth palms (date palm) out of our oases
- `WEEPINGSTONES_SETTINGS_SLIDERS_1` — Weeping Stones Mod Settings sliders: truce radius, vhorrin odds, vizhik escape chance
- `WEEPINGSTONES_WALKING_CONDENSER_1` — Weeping Stones giant: the walking condenser (oldest gorrask carries a running machine; a pool and truce where it settles)
- `WEEPINGSTONES_CONDENSER_QUESTS_1` — Walking condenser quests: Hutt capture for the Arena, or Moisture Farmers keep it free vs Blackstar fame hunters
- `WEEPINGSTONES_REFUSED_TOLL_RITE_1` — The Refused Toll, for Mob'Unloo: draw at an Imperial metering station and walk away unpaid
- `GELATINOUSSLIME_GAPPO_FAMILY_1` — Slime: the gappo family (grazer moved to RM_ with its v2 art, plus lesser and greater gappo); RUT_SlimeGrazer out
- `GELATINOUSSLIME_DWOMMO_FLIER_1` — Slime: the dwommo, a gas-float flier (real flight), the flying aristocracy
- `GELATINOUSSLIME_GLURRO_SALVE_1` — Slime: the glurro, iron-crusted grazer milked and rendered for a slime-resistance salve
- `GELATINOUSSLIME_FUBBUM_HUNTER_1` — Slime: the fubbum, the one hunter of the gelatid herds
- `GELATINOUSSLIME_KIT_ART_1` — Slime: real art for the whole free kit, replacing the vanilla tortoise/grass/bush/dandelion stand-ins
- `GELATINOUSSLIME_RAIN_STRIP_1` — Slime: campaign strips vanilla Rain/FoggyRain from RM_GelatinousSlime and the twin (ban 2); shrine denial retargeted
- `GELATINOUSSLIME_GENE_TEXT_TIER_1` — Slime: move the Star Wars A/B gene lists (57 genes, 19 canon strings) from the free mod to Utinni
- `GELATINOUSSLIME_SETTINGS_SWITCHES_1` — Slime Mod Settings: on/off and a slider for slimification, farm conversion, the visitors
- `GELATINOUSSLIME_PIT_SOLVENT_1` — Slime pit as a solvent: renders toxic or indigestible food safe (Rot's finest in the campaign)
- `GELATINOUSSLIME_FARM_RUINS_1` — Slime: ruined farms sinking into slime-grass (map genstep)
- `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` — Slime giant: a chunk of the titanoslime is a terrible thrown bioweapon
- `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` — A titanoslime chunk opens a Forsaken vault blocked by an Assailant seal (seal does not exist yet; owner to confirm)
- `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` — Slime: resurrect someone as of the last time they touched the slime (Ascendant Ladder tech; are they the same?)
- `GELATINOUSSLIME_JOINING_WATER_RITE_1` — The Joining Water rite: join hands holding slime, one person's permanent hediffs spread weak over several (god: Pomp, unresolved)
- `ALPHA_ANIMAL_PORTS_REHOME_1` — Five Alpha Animals creatures have RSW_-prefixed ports (Wildpawn=RSW_Durrok, Wildpod=RSW_Mullgoth, Cactipine=RSW_Chikka, Needlepost=RSW_Skorra, Terrorw
- `MIASMA_FREE_SALT_CRUST_1` — Miasma free tier: its own salt crust so the salt line paints without the campaign
- `MIASMA_SWARM_COMPOSTER_PORT_1` — Miasma: port the fever swarm, karrobel and delta loam to RM_, and the pollination gate into the free mod
- `MIASMA_FREE_NURSERY_YOUNG_1` — Miasma free nursery: young of crimson opee, thornback colo, shale gorger, reefback
- `MIASMA_AMBUSH_FROG_REMAKE_1` — Miasma: the giant ambush frog remade as ours (new name, alienized art)
- `MIASMA_ROUND2_IMPORTS_1` — Miasma campaign cast: round-2 imports as races (bogwing flier, blarth, blixus, marsh haunt); sando adult held
- `MIASMA_WARDEN_MOTHER_ART_1` — Warden mother art, with an aged variant for her last season
- `MIASMA_YOUNG_CALL_1` — Miasma: the stranded young's cry, and the warden mother lumbering toward it
- `MIASMA_ATTAR_STILL_1` — Miasma: the attar (beauty oil) from delta silt and salt; glaze and balm, never medicine
- `MIASMA_FLOTSAM_YARD_1` — Miasma: the flotsam beach, river goods washed into the roots after each surge
- `MIASMA_SETTINGS_SWITCHES_1` — Miasma Mod Settings: plant predation, pollination gate, stranded deformation
- `MIASMA_MOTHERS_PRICE_1` — Miasma giant: the mother's price (sell a stranded young and she never forgives; succession void)
- `MIASMA_DECAY_CELLS_1` — Miasma tech: decay cells, a learned generator making power from rot; spent cells become rotting beds
- `MIASMA_ROTTING_BED_CUISINE_1` — Rotting bed (spent decay cell) grows a Star Wars Cuisine ingredient (mandrake.rsw.cuisine)
- `MIASMA_RECALL_WRITTEN_OFF_RITE_1` — The Recall of the Written-Off rite (Rekko): a struck-out disposal order calls a salvage operation on you
- `CHILL_FLOOR_CAST_TRIM_1` — Chill floor: move hoolen, vaunoom and the two Alpha Animals borrowings off the floor roster (Q1)
- `CHILL_FREE_TIER_CATCH_1` — Chill: move the 7 campaign-only catch species into the free mod; one rare-catch table; amend the_propane_lakes.json (Q2)
- `CHILL_ZHIIL_FLOOR_BODY_1` — Chill: the zhiil gets a living floor body (def + sprite), so every catch is alive on the floor (Q3)
- `CHILL_RETURN_COMB_LANDMARK_1` — Chill floor landmark: the Return Comb, dynamo junction as scenery and lore only, no puzzle (Q4)
- `CHILL_WAX_PROCESSION_GIANT_1` — Chill floor giant: the Wax Procession (design then build; GPT idea 1 in the agenda) (Q4b)
- `CHILL_NATIVE_COLD_TOLERANCE_1` — Chill natives comfortable to -150 C on the -110 C floor (they freeze today, read from source) (Q5)
- `CHILL_DIVE_DENSITY_SAMPLER_1` — Chill dive spawns obey density (not one-of-each); number set on a live walk with the owner, leaning 2-4 (Q6)
- `SEABED_PER_SEA_FLOORS_1` — Sea-floor planet layer Phases 3+4: guard the FinalizeInit plant crash, then a real floor biome per sea (replaces the empty RM_SeabedFloor placeholder)
- `SCALD_WALKING_PASTURE_1` — Scald bottom-walkers: a grazing herd creature first, then the Walking Pasture (crew follows the herd, harvests what grazing exposes)
- `SCALD_IMMERSION_BERTH_1` — Scald Immersion Berth: a parked ship's rooms slowly heat; compact ships cheap to cool; never seals doors or blocks launch
- `SCALD_FLOOR_VENT_FIELDS_1` — Scald floor map generates vent fields: anchors bubble-sailors (no more placeholder penguin), vent flora, Sail Forecast eruption warning
- `SCALD_RETURN_GALLERY_1` — Scald floor: the Return Gallery, a half-buried Rust Cathedral coolant ruin to trace (design then build; avoid arbitrary switch-matching)
- `SCALD_BATHING_RITE_1` — Scald rite: water pilgrims bathe at the cool margins (design; register entry; waits on the margin cove)
- `SCALD_SAAL_ONE_NAME_1` — Scald bubble-sailor: creature and catch both named saal; retire noohm everywhere
- `NABOO_FISH_TO_TWILIGHT_1` — Mee and faa off the Scald floor; into the Twilight Sea as floor residents with catch wired
- `SCALD_SIMMERLACE_EKKEL_LORE_1` — Scald flora: simmerlace knots are ekkel in fishermen's lore (description text); kettlewick and seepcandle yields still open

## Commits

```
aec7c56f3 Messy Conduit lane F: ring and aerial determinism fixed (edge cache key + off-screen section rebuild), hose lay bug fixed; live 40/40, hose 12/12, matrix 100 PASS / 9 UNBUILT, fresh==in-game on all 19 boards; hose flat vs plump screenshots
46cc59d40 Program: track (b) sittings done; per-sea floors gate
a81867298 Scald floor sitting ruled; nine items filed incl. SEABED_PER_SEA_FLOORS_1 (no open item covered per-sea floors)
ed36b768b Scald floor-pass sitting agenda draft + GPT five-ideas consult (BEDAZZLE track b)
b1fdc3ed8 Chill floor sitting ruled (7 cards); seven CHILL_* items filed for FOUNDRY
7180fd37f Chill floor sitting agenda: five GPT ideas (Return Comb landmark, Wax Procession giant) and ranked decisions
2e2729525 Messy Conduit lanes C/D/E: style selector (4 families), hoses (plump/flat state machine, offline-proven), Northstar live matrix 109 scenes: 100 PASS, 9 UNBUILT, determinism defect on ring boards found (screenshots stay local, 500 MB)
78079c554 Chill floor-pass sitting agenda draft (track b): built state, gaps, catch table, six questions; GPT ideas pending
e7490dd79 Rites register: owner accepted every pitched rite; program moves to track (b) sea floors
d9b75bb58 Messy Conduit lane C: 42 real art pieces wired for Cybertek/ExtCord/StarWars + aerial + staged hose set; style screenshots (source+DLL follow with lanes D/E)
5e2321b2c Messy Conduit phase 1b + aerial lines: rope physics, tangles, whipping/dripping live ends, net highlight, CPU sway; poles, sagging spans, power across distance, fallen cords, one-way power tap; live 32/32 + aerial 18/18
41222ed33 Hose art redone as brown sackcloth (owner): 6 v2 jobs done, v1 superseded
6ede54d93 Messy Conduit phase 2 art: 41 artpipe jobs done (Cybertek 7, ExtCord 11, StarWars 9, shared+aerial 7, hose 7); hose colour to be redone as brown sackcloth
4445cfac2 Long Shade proposed-fills art review sheet (LONGSHADE_BEDAZZLE_CONTENT_1 pt 8)
050d3b677 Messy Conduit design doc: aerial spans now in scope (owner); stale NOT ADVISABLE rows replaced
cfc6dd58e Messy Conduit polish: T/X junction alignment, node draw order, wall/rock stubs on face, lamp plug, limp dead end (137/137 selftest, 19/19 live); Northstar scene-matrix generator, oracle, placer, contact sheets (47/47)
904ea5513 ledger: BENCH shard sync on wake
5051553fb Messy Conduit phase 2 design: lanes L1-L8, 109-scene Northstar matrix, aerial lines, fire-hose behaviour
07582a226 BENCH handoff 2026-10-02: all 12 bedazzle scoring sittings closed; Northstar pilot to FOUNDRY for live run; 3 lessons
521eb7c46 ledger: NORTHSTAR_ISHKO_PILOT_1 to FOUNDRY for the live run
... 160 more: git log --oneline 7d4d26dc6..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-03T03:27:45Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/FOUNDRY.jsonl   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY (this window; ledger shard / mod-list backups from lane runs)
```

