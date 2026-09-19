# BENCH_REBOOT_HANDOFF_202609070000 — READ FIRST on wake

First handoff for this seat. Everything below is committed and pushed.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Read the donor def before writing a word of design.** Two "biomes" on the frozen world —
`BMT_CrystalCaverns` (578 tiles) and `BMT_FungalForest` (425) — are Biomes! Caverns
UNDERGROUND layers (`isCavern true`, roofed, single Calm weather); the map wore them as
surface biomes and a sheet nearly got written for one. The def's own fields (`isCavern`,
`workerClass`, its weather table, its description) say what a thing IS; lore and web pages
say what it was meant to be. Check the def first, every time — the same reflex caught the
haiku census mislabeling a 25-mod quicktest autosave as "the campaign" (its `<modIds>`
header said so in ten seconds).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Nine biome sheets ruled today** (`design/Jawa/worldbuilding/biomes/`): forsaken_crags,
  the_rot, the_slime (+ the accepted gene lists), the_contagion, the_blue_desert,
  the_propane_lakes, nightside_ice (second pass), the_lantern_deeps (injection),
  the_cracked_lands; plus `assailant_weapon_remnants.md`. HorrorWastes, the crystal
  caverns and the fungal forest are dissolved. **Nothing is painted yet** — every map
  change is an item with a render-before-painting step: `HORRORWASTES_BIOME_DISSOLVE_1`
  (the anti-bullseye lobe mosaic), `CONTAGION_BIOME_PLACEMENT_1` (widened today to every
  rain-fed dayside high), `NIGHTSIDE_ICE_DEF_1`, `FUNGALFOREST_RAID_MERGE_1`,
  `LIQUID_BIOMES_MAP_1`. He sees each render before a tile moves.
- **The droid program is Foundry-ready on his 15 rulings** (`design/Jawa/droids/`), 31
  packets filed. Five of today's rulings SUPERSEDE his own older ones (no rogue droid
  faction; programmable gets mood; brains never craftable; repair-for-profit events in
  v1; primitive fabrication only) — supersession lines are written into the older docs;
  he may want to eyeball `design/Jawa/droid_ruling.md`'s top.
- **Saves edited on his word**: 82 + 133 inert `Asimov.Need_Energy` entries removed from
  `Saves\WORLDMAP_V1_original_c.rws` and `Saves\gravship_scratch_d.rws`; backups sit
  beside them (`*.bak-asimov-20260906`). 75/71 other `Asimov` strings remain by design.
- **Codex pipeline**: native transparency works (the chroma-key stage is retirable) and
  the wrapper has been throwing away finished images on timeout — the ~14
  `TREE_GRAPHICS_OWNERSHIP_1` "blocked" attempts may be on disk. `CODEX_WRAPPER_HARVEST_FIX_1`.
- **Sequence he ruled**: `BIOME_FREEZE_FABLE_REVIEW_1` → `SETTLEMENT_REJIGGER_ROUND2_1` →
  the animal/plant assignment. The freeze review is blocked on the undefined small defs
  (oasis, the green squares, Scarlands, tar pits, mangrove, swamp, the Cathedral's biome,
  grasslands) and the four liquid biomes.
- **The Sarlacc discussion pack** (`design/Jawa/worldbuilding/sarlacc_discussion_pack.md`)
  has waited since morning for its sitting.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `CREATURE_ART_REVIEW_SHEET_1` — BENCH, `doing` since 2026-09-05, needs owner; NOT
  touched this session. State: the owner has been ruling through the art review sheet
  (rejected the reskin-terrestrial-with-glowing-plates approach). Next action: resume the
  sheet with him — and note the Codex fix (`CODEX_WRAPPER_HARVEST_FIX_1`) may have
  unblocked the art generation it feeds. Leave in `doing`.
- `TILEGEN_SILENT_REUSE_1` — **FOUNDRY's item** (owner FOUNDRY, started by FOUNDRY
  2026-09-05), listed here only because it is in `doing`; hardened by 2e3336f4 and
  33e2e681 per FOUNDRY's own note, needs deploy. Not BENCH's to close — no action.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- A haiku census called `Autosave-1.rws` "the campaign save" and concluded the KotOR
  donors were retired; its `<modIds>` header lists 25 mods with Droidworks — a quicktest.
  **Read a save's mod list before comparing it to anything.**
- `codex_image.py` raises on its 180 s ceiling BEFORE harvesting — finished PNGs are
  reported as "no image produced." A wrapper timeout is never evidence of a failed image.
- `xargs` on workshop paths breaks on "Program Files (x86)" — a grep chain silently found
  nothing; use python `glob` for any path with spaces.
- The offline def dump does not hold Alpha Biomes or inactive donors (`rimsage` said
  "not found" for defs that exist) — read the workshop XML directly for donor content.
- The blind-scan hook refuses a COMPOUND command whole — nothing in it runs; split the
  literal-string count out and run it alone with `MEASURE_ALLOW_SCAN=1`, saying so.
- `git` index.lock contention with FOUNDRY is constant during its waves — every commit
  here loops on the lock; bare retries lost two commits before the loop existed.
- BENCH cannot `close` a FOUNDRY item; `--owner-said "<his verbatim words>"` is the
  override and records itself as one.

## Closed since the last handoff (68)

- `TRIM_VALIDATION_LAYERS_1` — 5c3e1a9e
- `CAST_NAMES_UNSPAWNABLE_ANIMALS_1` — b1bbd51f
- `GRAVSHIP_LAUNCH_TRAVEL_1` — 138ee26a
- `GALACTIC_EMPIRE_NAME_COLLIDES_1` — 6123a1ec
- `QUEUE_GITHUB_MIRROR_1` — b1c8f39a
- `DROID_SYSTEM_EMBRACE_1` — bbea1609
- `EMPIRE_PURSUIT_SCRATCH_PROOF_1` — b0e12305
- `EMPIRE_PURSUIT_SCENPART_INSTALL_1` — e5f9f61b
- `GRAVSHIP_LANDING_DIRECT_PLACE_1` — 0f04c84e
- `TURRET_ROSTER_CURATION_1` — 3015d6a3
- `LORE_SWITCHOVER_ADOPTION_1` — cf1fe4e1
- `ASSAILANT_FLESH_DUNGEON_1` — 53bd66ab
- `VAULT_DUNGEON_CONCEPT_1` — bfc83dff
- `PAWN_FLAVOR_STARWARS_1` — ee13939f
- `DIVINE_FRONT_MATRIX_1` — 7cc6cb20
- `CURSE_COLUMN_RESPEC_1` — 40195a68
- `DEVOTIONAL_SACRIFICE_CATALOG_1` — 40195a68
- `GOD_INTERCESSION_SPEC_1` — 40195a68
- `DIVINE_DILEMMA_EVENTS_1` — 40195a68
- `FIRST_CONTACT_CHAINS_1` — 40195a68
- `JAWA_TRAP_RENAISSANCE_1` — 94a05164
- `COVERED_PIT_TRAPS_1` — 3ee5e2ec
- `FABLE_HANDOFF_SPRINT_1` — 127aadc5
- `CAI_FOG_DEEP_DIVE_1` — 1dc6d9bd
- `SARLACC_SPEC_SESSION_1` — 180bfe8b
- `NINE_VOICES_CAST_BIBLE_1` — e3533fa0
- `RESEARCH_TAXONOMY_DRAFT_1` — d85403b5
- `LLM_INGAME_WIRING_1` — 1309d59f
- `DUST_STORMS_DESTRUCTIVE_1` — f311db65
- `BOILING_WATER_BURNS_1` — f311db65
- `PLANTS_VISIBLE_GROWTH_1` — f311db65
- `DESERT_PLANTS_SCRAGGLY_1` — f311db65
- `CANTINA_KITCHEN_SPEC_1` — 5b6ad4fb
- `TUSKEN_WATER_RAID_1` — fd9d7071
- `RACE_REGEN_ARCHITECTURE_1` — 31428560
- `SKYHOOK_BESPIN_REDESIGN_1` — 03534618
- `PROPOSAL_SUITE_REVIEW_1` — 46edfb7e
- `PAWNFLAVOR_BREAK_LABEL_FIX_1` — 23f4043c
- `SAVE_HOLDS_DEAD_TITAN_CORPSE_1` — bd498088
- `SAVEGAME_PURGE_KEEP_B_1` — 7f96ba47
- `RIMPLACE_GENSTEP_LIVE_PROOF_1` — 7865b643
- `BRIDGE_OVERRIDE_ATTRIBUTION_GAP_1` — eaed5422
- `TEMPLATE_CANVAS_UNDECLARED_1` — 64477ab7
- `BRIDGE_INVENTORY_TRANSFER_REFUSES_ALL_1` — ac598d1e
- `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1` — ac598d1e
- `TRADERGEN_CONFIGERRORS_NRE_1` — f66246a7
- `CORRECT_COLD_LOAD_1` — 47903872
- `CHERRYPICKER_TWO_PROFILES_1` — ac444adb
- `CONFIG_SWAP_ATOMIC_WRITES_1` — d1c193ae
- `LIVE_BIRTH_AND_HATCH_DEMO_1` — c6615420
- `BRIDGE_TAKE_TOCTOU_AND_EPOCH_SENTINEL_1` — a2d8a0aa
- `FOG_REVIEW_SITTING_WITH_OWNER_1` — 75204205
- `COLD_LOAD_RUN_SHEET_2` — e9b009bf
- `SALVATION_RITUAL_PRUNE_1` — 5ee8fbcd
- `ANOMALY_CREATURE_RESTORE_1` — 560162dd
- `RESEARCH_RECOST_PREREQ_JOIN_1` — b2c50c1f
- `FLUID_CANAL_FLOOD_LIVE_CHECK_1` — c4edccb5
- `CORRECT_FLUID_CANAL_1` — c4edccb5
- `RESEARCH_TREE_NORMALIZATION_1` — f1ebc8c1
- `RESEARCH_TREE_TABS_1` — d27125d2
- `ARMOURY_LIGHTSABER_FINDMOD_1` — 33e2833d
- `INHABITED_TILEMUTATOR_NO_ENTRY_1` — d92f5459
- `OHM_RESCOPE_PROPAGATION_1` — f3293888
- `OHM_PROVENANCE_PURGE_1` — ebdca39a
- `BENCH_REBOOT_HANDOFF_20260905` — fc27cbf5
- `ORACLE_OHM_PROMPT_STILL_SHIP_1` — fc27cbf5
- `GENEPACK_MODS_PLUNDER_1` — 1549dec6d143a8a1c6f3e3a0c5734902443cce43
- `NIGHTSIDE_BLUE_DESERT_1` — 4d8f4d7999a3a1c98bebb3f17f85720c57ba6d92

## Filed and still open (80) — the next seat's queue

- `DROID_SYSTEM_BUILD_1` — Build the unifying droid mod per droid_system_spec.md (parked until the owner reopens)
- `JAWA_PATCHES_SPLIT_1` — Phase 3: triage src/SPLIT_Phase3/Jawa_Patches per-file (125 TBD defs) - Ashkarr/Rakata/DeepDesert/Pyrelands to RUT, animal/texture/generic to RSW or R
- `FLUID_CANAL_DEBUG_SURFACE_1` — FluidCanals [DebugAction]s never register in a live game
- `TILEGEN_SILENT_REUSE_1` — jawa/world_tile_map_generate fabricates success on the second distinct-tile call per session
- `INHABITED_AUGMENTATION_BUILD_1` — Build the tile-augmentation content: rimplace templates + Inhabited wiring for the biome/faction/latitude augmentation dream
- `PLOT_MECHANISM_MODS_WAVE_1` — Build wave: LLM raid-redesigner + post-battle/event hostility creation + plot-gap mods (from plot_mechanisms_wave.md)
- `NINEFOLD_MISSING_EVENT_HOOKS_1` — Ninefold has NO event hook for battle, trade, launch/rooted or droid-online - four gods (Sh'kaar, Mob'Unloo, Ta'Baa, Ohm) never move; the theology is 
- `VAULT_THAW_QUEST_FAMILY_1` — Six Forsaken vault layouts exist but nothing makes them play - no QuestScriptDef family for thaw/reversal/sleepers/ship-claim/Reclamation
- `NINEFOLD_FIRE_HOOK_RATELIMITED_1` — Fire as a Zizzik/Sh'kaar input needs an incident-level or rate-limited hook - per-fire (FireUtility.TryStartFireIn) would flood satiation in one fores
- `NINEFOLD_HOOK_DOWNS_NOT_JUST_DEATHS_1` — Ninefold battle hook should fire on a pawn being DOWNED, not only killed - Sh'kaar feeds on violence, and most fights end in downs
- `CREATURE_ART_REVIEW_SHEET_1` — Full creature-art review sheet: every nonhuman at true in-game scale, biome-clustered, verdict+priority+notes - start of the art regeneration pipeline
- `UI_SHELL_SLICE_BUILD_1` — Build the RimUtinni Shell vertical slice per ui_shell_spec.md: mandrake.rut.shell theme mod (3 button atlases + palette meta.xml), 1 loader + 1 menu-b
- `NINEFOLD_RUNTIME_PROOF_BLOCKED_1` — Ninefold compile-fix VERIFIED (ready:14, was 6); runtime firing UNPROVEN - GameComponent.Instance null on ignoreModCompatibility loads, all hooks incl
- `GRAPHICS_GEMINI_BILLING_DECISION_1` — Wrecked-Machines facing pipeline gated on owner enabling Gemini billing (free tier=0 for images); channel+key ready, rembg+Remotion free wins already 
- `MULTIVIEW_FACING_PIPELINE_1` — Productionize the multi-view-mesh facing pipeline: InstantMesh (4 sprites -> volumetric mesh) + meshfuse projection; local/free on the 5080; proven 2/
- `LOCAL_IMAGEGEN_TRACK_PARKED_1` — PARKED by owner 2026-09-05: local ComfyUI/Flux image-generation track halted - it caused the seat OOM window kills; do NOT relaunch local generation u
- `BIOME_SPAWN_FLORA_AUDIT_1` — Spawn each biome in game and photograph what actually grows - normalize before adjusting; also identify the rainbow prolific unclickable bushes the ow
- `SARLACC_NATIVE_HABITAT_1` — Sarlacc: native deep-desert habitat, three life-cycle stages, dungeon module
- `WORLDMAP_DESERT_BAND_REPAIR_1` — Repair the Desert def's climate outliers on the frozen world map, re-freeze the savegame
- `BIOME_FAUNA_ASSIGNMENT_SITTING_1` — Joint sitting: review all biome sheets, finish remaining biome descriptions (candidates: AB_RockyCrags, AB_MycoticJungle), then assign fauna/flora per
- `LIGHTFALL_CHASM_AUTHORING_1` — Author the Lightfall chasm landmark on the Damp chain (terminator suture, deepest at tile 9023) — site+name owner-ratified 2026-09-06, spec in forsake
- `EDIBLE_GENEPACK_NATIVE_1` — Scan Genepacks Injection DLL (TommasoBelluzzo.GenepacksInjection, ws 3784789591), understand its consumption flow, reimplement the edible-genepack loo
- `GIZKA_TRIBBLE_ADAPTATION_1` — Examine the subscribed (not installed) Tribble module; design the Gizka ship-pest event — cute first, real problem after; check Absorbed_KotorCore for
- `GEONOSIAN_BRAINWORM_MORPH_1` — Research Space Worms mod + Geonosian brain worm canon (Brain Invaders arc), author our own RSW_ brain worms — cold-vulnerable, host-puppeting
- `HORRORWASTES_BIOME_DISSOLVE_1` — Dissolve the HorrorWastes biome: re-biome its 1,711 tiles into neighbors (Deadstone receiving def ruled at the PropaneLakes sitting), re-freeze, re-ho
- `HORRORS_RAIDING_FACTION_1` — Horrors become a RAIDING faction (no settlements, nightside-gated encounters) + nests/sinkholes/crysalises injected as nightside dungeon content — the
- `OCULAR_OVERDRIVE_SITE_1` — Ocular Forest stays as a named site (the Overdrive, 3 Ashfall Range tiles) + custom dungeon, woven into the plot — Rust Cathedral enmity (45.5° apart,
- `CONTAGION_BIOME_PLACEMENT_1` — Move the Contagion (AB_OcularForest) to the peaks above the green: Scald Spine's 38 non-green highs + optional Ashfall/Dew Horn tops — NO green square
- `WATER_KINDS_TAXONOMY_1` — Owner: many kinds of water by content + the transmutations between them — inventory every sheet's water, write the taxonomy as data, map onto the live
- `MUTATION_MODIFIERS_SURVEY_1` — Survey every mutation-type system in the stack (Biotech genes, mutagen part-hediffs, SlurryHigh, transformation hediffs) to build Contagion-touched — 
- `CODEX_WRAPPER_HARVEST_FIX_1` — codex_image.py discards finished images on timeout (harvest never runs) — fix, recover ~14 orphaned TREE_GRAPHICS images, retire chroma-key: native tr
- `CODEX_PARALLEL_WORKERS_1` — N-worker codex exec queue with receiving-agent AGENTS.md prose + grumpiness detector reading rollout rate_limits; own CODEX_HOME per worker
- `BIOME_FREEZE_FABLE_REVIEW_1` — Full-scale Fable review of ALL biomes together before the freeze — temps, physics, weather, precipitation, dust/sand/ash, fuel/wood/animal/meat/growth
- `MECHANOID_BIOME_PRESENCE_REVIEW_1` — Review which biomes contain mechanoids and ancient dangers — not all should; the two magnetic poles (Rust Cathedral, the antistellar war lab) by rulin
- `LIQUID_BIOMES_MAP_1` — Four liquid biomes on the frozen world: boiling ocean, two brine seas, and the propane lake as worldmap tiles under Umbra (render before painting)
- `ANCIENT_WAR_LAB_1` — The war lab beneath the propane lake over the Impact Site — submerged dungeon, lab fauna + mechanoid guardians, and the crater ending as a permanent m
- `TERRAMANUFACTURE_CANON_1` — Propagate the terramanufacture ancient history (dynamo at the substellar pole, Cathedral as remnant, unplanned war lab, mutual learning) into the worl
- `LANTERN_DEEPS_INJECTION_1` — The crystal caverns as an injected underground layer beneath ≤ −40 °C nightside maps — quicktest the cave-map generation, two entrance features (emerg
- `CRYSTAL_MODS_INGEST_1` — Find the orange glowing crystal's source mod; inventory every crystal harvest in the stack; assess ingesting it so all crystals live in the Lantern De
- `MECHANOID_ORIGIN_CANON_1` — The mindstone droid-mind race; mechanoids + Rust Cathedral as a non-artificial AI and the Deeps' crystal minds as their wild cousins; the production f
- `KYBER_TRADE_PLOT_1` — Selling kyber: Empire heat rises per sale, Hutt interest rises, alleged Jedi from the Moisture Farmers, the donate-and-smuggle plot (no helping the Re
- `DROID_FACTIONS_IN_FROZEN_SAVE_1` — Census: which droid FactionDefs/kinds/need classes are scribed in the frozen world and campaign saves
- `DROID_DONOR_REFGREP_1` — Per-donor reference grep: every KotOR/ABF/Asimov/Depot defName and class in src/ and every active mod
- `DROID_ORACLE_VOICE_DESIGN_1` — Design (dormant): four droid Oracle consumers with prescribed fallbacks, claude -p transport
- `DROIDWORKS_LIVE_LOOP_PROOF_1` — Minimal-list quicktest proof of the five-state loop on GNK + a KotOR kind; close the 8 open live checkboxes
- `DROIDWORKS_FULL_LIST_COEXIST_1` — Enable Droidworks in the full mod list beside the donors; cold load, texPath census, Harmony idempotency
- `DROIDWORKS_FORMAT_TIERS_1` — Format tiers blank/mindless/programmable/sapient with needs by tier (ruling 4), work gating, format recipes
- `DROIDWORKS_MODULE_ABSORB_1` — Absorb KotOR's six-slot droid module apparel as RSW_DW_Module_* (loot-only, no recipes)
- `DROIDWORKS_HEADS_BRAINS_SPIKES_1` — Brain trio (import-only), per-family heads with CompHeadIdentity, the mindstone head, per-faction data spikes
- `DROIDWORKS_FINE_PARTS_1` — Fine parts per family (limbs, sensors, motivators, cells) with quality, drop tables and stat/personality effects
- `DROIDWORKS_SHOP_BENCHES_1` — Repair bench, reassembly harness (head-gated), rebuild-from-corpse, overclock as a bench job
- `DROIDWORKS_BOLT_PAYOFF_1` — Restraining bolt consequences: mood aura, rebellion on removal past resentment threshold, shear on damage, un-bolt-each-other
- `DROIDWORKS_ION_SHIELD_BODYSIZE_1` — Ion breaks shields (EMP side-damage) and scales by body size — merge with ION_STUN_IGNORES_BODY_SIZE_1
- `DROIDWORKS_DETONATION_REVIEW_1` — Detonation grid (energyDensity x charge) built and SAVED for the owner to walk; deny-module on JDS battle kinds
- `DROIDWORKS_PRIMITIVE_TIER_1` — Primitive family: Jawa-fabricable frames/parts/modules at grossly inferior stats, the G2 repair droid (new art), the Junker suicide droid
- `DROIDWORKS_WIPE_SEVERITY_1` — Memory wipe: 7-day severe relearning debuff, service-record reset, permanent accreting hardware quirks
- `DROIDWORKS_RESEARCH_ROWS_1` — Seven Droidworks research rows in The Unbolting; cut the Depot droid-brain rows; brains never researchable
- `DROID_FACTION_LOADOUTS_1` — Droids in every faction's hands: Empire attack droids, Homestead utility droids, Hutt heavies, Junker suicide droids, traders' protocol droids, Trade 
- `DROID_FDE_KINDS_REPOINT_1` — Repoint the 4 Jawa_Droid_* FDE kinds and FDE droid backstories onto Droidworks races (fix the generator)
- `DROID_FDE_GOODWILL_CAP_1` — Free Droid Enclaves goodwill cap via GoodwillSituationDef (spec: restraining_bolt_technical.md)
- `DROID_PROTOCOL_TRADE_ADVANTAGE_1` — Protocol droid in the trade party shifts prices both ways; none on your side is a penalty
- `DROID_REPAIR_FOR_PROFIT_EVENTS_1` — Recurring event: friendlies bring droids for paid repair/upgrade; inferior/superior parts choices; offload problem droids
- `DROID_HUTT_CAPTIVES_1` — Droids held in Hutt torture chambers as a rescue-or-purchase source at Hutt sites
- `DROID_DISTRESS_CALL_REPOINT_1` — Re-point the BTD Droid Distress Call quest's 5 KotOR kinds to Droidworks kinds; reframe as the crashed-droid rescue
- `DROID_RETIRE_KOTORDROIDS_1` — Retire guy762.kotordroids (wave R1) after modules, heads, loadouts, FDE repoint and Distress Call are closed; cold load
- `DROID_RETIRE_ABF_SYNCORE_1` — Retire ABF + SynCore (wave R2); DroidDonor_ABFGate fires; remove DroidsAreMachines ABF half; cold load
- `DROID_RETIRE_DEPOT_ASIMOV_1` — Retire Droid Depot + Asimov + MSEDroidFix (wave R3); repoint the Empire KX kind; retire NoDroidManufacture; cold load
- `DROIDWORKS_CHASSIS_PERSONALITY_1` — Per-family starting-trait weights and the protocol-droid pedantry social modifier
- `DROIDWORKS_SERVICE_RECORD_DRIFT_1` — CompServiceRecord: time-since-wipe accretes chassis-weighted idiosyncrasies; wipe resets
- `DROIDWORKS_MODULE_PERSONALITY_1` — Installed modules carry attitudes: CompModulePersonality trait-hediffs while worn
- `DROIDWORKS_WILD_DROIDS_1` — Wild crashed droids: factionless erratic hostiles, capture -> Wild spike -> reprogram-as-recruit with resistance
- `NIGHTSIDE_ICE_DEF_1` — Author RUT_NightsideIce (own def inheriting vanilla IceSheet, every list overridden, no arctic zoo, aurora-clear) and paint its 802 highland tiles und
- `ALPHA_FAMILY_SOURCE_REVIEW_1` — Study the whole Alpha family from its public source (github.com/juanosarg/AlphaBiomes + AlphaAnimals): catalog the C# mechanics, replicate the ones wo
- `FUNGALFOREST_RAID_MERGE_1` — Dissolve BMT_FungalForest (an underground def on 425 surface tiles) into its neighbors per the measured cluster table (the Rot; Wasteland at South Cra
- `FUNGAL_SOIL_TRADE_1` — Jawas dig fungal soil from the Rot and haul it to the moisture farms by ship — early money; digging sends distress through the fungal whole and brings
- `MOISTURE_FARM_TEMPLATES_1` — Content injection: several highly plausible moisture-farm templates (homestead, vaporator field, cistern head, compound, ruin) — needed many times ove
- `WORLD_RIVER_COLORS_1` — Color the worldmap's rivers by segment (red headwaters → brackish green/brown jungle → toxic brown/blue termini) and the propane lake slate cyan — Riv
- `SETTLEMENT_REJIGGER_ROUND2_1` — Round-2 rejigger: re-shift every settlement to fit the pre-frozen biomes — right AFTER BIOME_FREEZE_FABLE_REVIEW_1, BEFORE the animal/plant assignment
- `FISH_BY_BIOME_1` — Fish in every biome where relevant — inventory the stack's fish defs and each biome's fishTypes; rule per water kind (milk, propane, red water, brine)
- `SAND_SWIMMERS_MOD_1` — Sand fishing: impassable Deep Sand pools you fish like water, with sand-swimmer analogs (never fish-shaped) — the sand swimmers mod

## Commits

```
06b8880a the_cracked_lands.md: biome sheet ratified — the flood, soil in the shade, cisterns, fliers feed here and nest in the desert, Moisture Farmers only, the roads; FISH_BY_BIOME_1 and SAND_SWIMMERS_MOD_1 filed
f74d7e27 sequence riders: freeze review → settlement rejigger → assignment sitting
f11ca284 file SETTLEMENT_REJIGGER_ROUND2_1 — settlements re-shifted to the frozen biomes, sequenced after the freeze review and before the assignment sitting
c215533f WORLD_RIVER_COLORS_1: per-vertex gradient along the river preferred over hard segments
8e06a11e file WORLD_RIVER_COLORS_1 — per-segment river colors and the slate-cyan propane lake on the world view
d6807c4b MODE: belt — owner stepping away, FOUNDRY runs the queue
ac911c58 GLOBAL_CLAUDE.md: handoff-at-end-of-queue doctrine, generalized to every session
34b021c2 Badlands sitting: Contagion widened to every rain-fed dayside high (sterilized on descent); half-plant tree art note; FUNGAL_SOIL_TRADE_1 and MOISTURE_FARM_TEMPLATES_1 filed; tree-ownership ticket gets its riders
8c980100 handoff.py: write mode pre-fills instead of refusing, and filenames are not a clock
d1055e88 lessons: five from the offline wave (UTF-16 strings, self-reading generators, silent duplicate defs)
019884a8 handoff D: record the new handoff command and the final selftest count
ded2fd4a handoff.py: preparing a reboot is a command, and HANDOFF READY is said once
585fe05c the_rot.md: blastpod chemfuel ingested wild-only (owner), fungal power generator cut
89e16e40 Fungal Forest dissolved: raided into the Rot (spore-warfare kit, SporeFlesh, mushroom bridges, marsh fungi, Skultop), tiles merge into the Rot per measured clusters; FUNGALFOREST_RAID_MERGE_1 filed
22824143 the_rot.md: the Agarilux Prime celebrated as the guardian exemplar (GasProducer comp, radius 8, corpse-feeding hyphae); ALPHA_FAMILY_SOURCE_REVIEW_1 filed — study juanosarg's public source, replicate mechanics as generic comps
355736bd run sheet 4: three more readings from the offline wave
78981b01 ledger: SW_MODS gap closed; substring-rung and -1-anchor traps filed
62fbc541 gen_armoury_patch: absorbed weapons stopped classifying as Star Wars, so 31 melee ops vanished
372ef8da ledger: Doctrine loadAfter closed; the same gap filed for Armoury and the patch mods
bf99382b Doctrine loadAfter: two mods it patches were undeclared, and one entry named the wrong mod
58eeb012 nightside_ice.md second pass: bound to RUT_NightsideIce (own def), dirty ice + thaw pulse + tunnelers, six reconciliations with the newer sheets, event equivalence table; first-pass ecology unchanged; NIGHTSIDE_ICE_DEF_1 filed
40a4a1cd ledger: retirement-order check closed
0f430178 Retirement order is now a check, not a sentence in one state doc
634234c5 ledger: Absorbed_KotorCore duplicate-def hazard closed
a24cda4d Absorbed_KotorCore was overwriting its own live donor with a stale copy of it
ab4294d2 ledger: Armoury generator + config-error sweep closed; KotorCore duplicate-def hazard filed
7f781d1e config errors: 31 -> 17, and the baseline is now a command
f95eacfc Armoury: two hand-edits taught to the generator, and a defName that made two ops dead
c5f88b65 ledger: close DROID_ASIMOV_SAVE_SCRUB_1 on the owner's word
af539d5a DROID_ASIMOV_SAVE_SCRUB_1: done — 82 + 133 inert Asimov need entries removed from the latest worldmap and gravship saves, backups kept, residue noted for D4
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: for     RIMMANDRAKE_PITS_BUILD_1: live-prove PitCell/Oiled gizmos on pits tier

Uncommitted (say for each whether it is yours or another seat's):

```
M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
 M src/RimMandrake/Pits/Defs/ThingDefs/Pit_OpenPits.xml
 M src/RimStarWars/BeastLairs/About/About.xml
 M src/RimStarWars/BeastLairs/Defs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml
?? "D:\\Luke\\dev\\Rimworld\\Transient\\bench_tools_dump.json"
?? deployed/config/ModsConfig.before-tier-pits.xml
?? design/Jawa/art/gods/busts/.gitignore
?? "design/Jawa/worldbuilding/lua suggestions/"
?? design/Jawa/worldbuilding/review/creature_art/
?? design/Jawa/worldbuilding/review/creature_register.fiftyone_export.json
?? design/Jawa/worldbuilding/review/deck/creature_deck.pptx
?? design/Jawa/worldbuilding/review/deck/creature_deck_manifest.json
?? design/Jawa/worldbuilding/review/furniture_art/
?? infrastructure/state/CODE_REVIEW_STATUS.json.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260902_181509.xml
?? infrastructure/state/codebase_health_last.json.lock
?? infrastructure/state/facts/mlie_creature_defname_map_wave_a.json
?? research/RimMandrake/inspiration/map_injection_2026-09-06/p2_createprefab_export.xml
?? src/RimMandrake/LoadTracer/Assemblies/
```

