# FOUNDRY_REBOOT_HANDOFF_202609180218 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609140417`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A backgrounded subagent can go completely silent and leave real, finished, well-formed
work sitting **uncommitted** on disk with no trace in the task registry (`TaskOutput`
returns "No task found") and no ledger note — this happened to the Mlie porting Pass 9
agent this wave. Before writing off a dispatched agent as "stuck" or "lost", check
`git status --porcelain` for its natural output area before assuming the work itself
is gone — the agent died, the WORK often didn't. Recovered and committed it this pass
(`48b72ac41`). Also: `TaskOutput`'s "Running background agents" list is
environment-wide (every seat's live agents, not just this window's) — an unfamiliar
description/ID in that list is not necessarily yours, and messaging a task ID you
half-remember can resume a completely different, already-finished agent instance that
just recaps old work rather than telling you anything new.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- He gave two art-direction notes this wave for the universal cargo tank and the
  bottle/bucket/barrel line (both recorded on `LIQUID_BOTTLE_LOOP_1` via `--owner-said`,
  commits `3d6479f41`/`386d51170`) — no art has been generated against either brief yet,
  that's still owed whenever art work picks it up.
- `WRECKED_DISTILLATION_MODULE_1` is genuinely blocked on a mechanism ruling only he
  can make: no existing WreckedMachines module (only `AutomatedSmelter`, which consumes
  ThingDef ingredients via PipeSystem) has ever consumed/produced a terrain/canal
  liquid. Building Distillation needs either new bottled-water ThingDefs + invented
  ProcessDef rates, or a brand-new liquid-consuming comp — re-tagged `needs owner`
  (commit `39e885c78`), was previously mislabeled `needs deploy`.
- Live modlist is 632 active vs. the stored FULL snapshot's 633 (1-mod difference) —
  most likely explained by BENCH's donor-shim retirement work today
  (`FIREECOLOGY_SHIM_RETIREMENT_1`), not touched or reconciled by me. Worth a glance
  before he plays, per the standing "restore before he plays" doctrine.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
Touched this window (real progress, all verified/committed/pushed, left `doing` on purpose):
- `LIQUID_REGISTRY_CORE_1` — v1 LiquidDef registry: 10 rows + generator shipped
  (`0cc6bdfa3`). Next action: build slime/blood/astrofuel rows (deferred, each with a
  real reason recorded on the item) or move on — registry itself is usable now.
- `LIQUID_BOTTLE_LOOP_1` (not auto-listed above but real and open) — full bottle chain
  built across 3 slices: bottle-ThingDef generator+base defs (`b296de839`), fill/use/
  dirty/wash jobs+settings (`5dfaf7c79`), buckets+barrels generalized onto the same
  chain (`08e11f160`). Next action: the "fill/empty bills at a tank" half is deferred —
  no tank-building exists in this codebase at all (confirmed by search, not assumed).
  Owner gave the tank's and the bottle/bucket/barrel line's art direction this wave
  (see "What the owner should see") — build the tank, generate art against both briefs.
  Live quicktest (fill/drink/dirty/wash/settings-off) still owed, no bridge access all
  session.
- `WRECKED_DISTILLATION_MODULE_1` — `distillable` flag + 6 water rows shipped
  (`4a5625629`). Genuinely blocked on an owner mechanism ruling, re-tagged `needs
  owner` (`39e885c78`). Do not build a tank-consuming comp without that ruling.
- `ROT_SPORECLOUD_PORT_1` — ported off the donor class onto our own
  `GameCondition_EnvironmentalWeather` (`44b4f3549`), build clean. Next action: live
  quicktest (dev-trigger, unroofed-vs-roofed pawn) — `BMT_FAUNA_ABSORPTION_1` gate 3
  stays open until that proof actually runs, do not mark it clear on the source work
  alone.
- `ROT_DECAY_HARVEST_1` — both map components built (`b5b947fe9`): accelerated rot
  (250-tick, swappable exposure predicate per BENCH's own note) and living-produce
  heat (calibrated against real vanilla Campfire heat, not guessed). Next action: live
  quicktest (outdoor meat decay, indoor control, freezer heat climb).
- `ROT_HEALTH_SHARING_1` — wound-link mirroring + kin-mending aura built (`dd1c978f1`),
  hook points verified via reflection against the live assembly (RimSage unreachable
  here). Next action: live quicktest (spawn several tagged pawns, shoot one, verify
  mirrored injury). One invented constant (`extraSeverityHealedPerDay`) flagged in code
  comments for calibration once a decompile is reachable.
- `MLIE_FAUNA_ABSORPTION_1` — Pass 9 (4 more species) recovered from a died subagent
  and committed (`48b72ac41`) — see "The one thing to carry forward". 64 species +
  Fambaa remain in the Wave C worklist. Fambaa specifically needs its own careful pass
  (ArtOverride-gated, flagged since Pass 7).
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — standing loop, several waves this session
  (39-43 plus a `wave 5` from a different seat working the same item): ArtOverride
  family (61 mods) and MenuShell fully clean, several small mods clean, ~8 real bugs
  found and fixed (dead comp fields, wrong `MayRequire` gates silently dropping animals
  from biome rosters, a false-positive bridge-holder substring bug in `handoff.py`).
  Never closes — next seat just picks the next dirty mod (candidates recorded on the
  item: `RimStarWars/Armoury` 261/1867, `Droidworks`, `RaidRedesigner`, `Aftermath`,
  `RimProperty`, `RotSporeKit`).

Pre-existing `doing` items, NOT touched this window (inherited open, confirmed state
below, no action taken — flagging per the handoff gate, not claiming credit or blame):
- `ARTPIPE_FAILED_REQUEUE_1` — still `doing`, last real note references commit
  `4117ae00`. Not opened this session.
- `BAZAAR_WINDOW_GRID_1` — still `doing`, model:opus per its own tag (Dialog_Trade
  replacement). Not opened this session.
- `BIOME_KITS_PUSH_TO_TEST_1` — still `doing`, umbrella tracker for the biome kits.
  Not opened this session.
- `BOOMALOPE_CUT_EVERYWHERE_1` — still `doing`. Not opened this session.
- `DROIDWORKS_FORMAT_TIERS_1` — still `doing`, needs bridge. Not opened this session.
- `FISH_BESTIARY_COMMISSION_1` — `ready`, not `doing` (kind:design, needs:owner) — this
  was FOUNDRY's own `next` pick at the top of this session but correctly left alone
  since design work backgrounds to Fable per policy, not built in-window. Untouched.
- `FORGE_MECHANICS_1` — still `doing`, spec exists (`the_forge.md`). Not opened this
  session.
- `GRAFFITI_VARIANT_COUNTS_1` — still `doing`. Not opened this session.
- `GREENTIDE_MECHANICS_2` — still `doing`, spec exists. Not opened this session.
- `MODCHECK_STATUS_ORPHANED_BY_RENAME_1` — still `doing`, needs a rename/forget verb
  on modcheck status before the stale `FluidCanals` key can be cleared. Not opened
  this session.
- `SCARLANDS_MECHANICS_2` — still `doing`, spec exists. Not opened this session.
- `TWILEK_TROPE_GENES_MOVE_1` — still `doing`. Not opened this session.
- `XENOTYPE_NONCOSMETIC_FIXES_1` — still `doing`, cosmetic genes explicitly off-limits
  per its own scope note. Not opened this session.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- A backgrounded subagent dying silently leaves finished work on disk with ZERO trace
  in the task registry and no ledger note — `TaskOutput` on its original ID returns
  "No task found", so the only way to discover the loss is `git status --porcelain`.
  Check disk before assuming lost work is actually lost. (See "The one thing to carry
  forward" for the full story — Mlie Pass 9, recovered and committed `48b72ac41`.)
- `TaskOutput`'s "Running background agents" list in its error message is
  ENVIRONMENT-WIDE, not scoped to the calling window/seat — it will list another
  seat's live agents too (saw MACBENCH's own `DIRTY_CODE_REVIEW_STANDING_LOOP_1`
  work under an ID I never dispatched). Don't assume every ID in that list is yours.
- `handoff.py`'s bridge-holder gate used a bare substring match
  (`if seat() in who`), which false-positives whenever one seat's name is a substring
  of another's (e.g. `BENCH` inside `MACBENCH`) — could have told a seat it held the
  bridge when a *different* seat actually did, blocking a legitimate handoff. Fixed
  this session (`2d48e8c5d`) to parse the exact holder and compare for equality —
  worth knowing if you see this class of bug elsewhere (any "is my name a substring
  of the live holder string" check is suspect).
- `code_review_status.py`'s filesystem-walk dirty-file counts include
  untracked/gitignored files (e.g. `_artsrc/raw/*`, `__pycache__/*.pyc`), inflating
  the "N/M dirty" figures older wave notes cite. Re-derive with `git ls-files -- <path>
  | wc -l` before trusting a stale count to size a review wave.
- `generate_liquid_suite.py`'s tag-union helper (`union_tags_affordances`) carries
  EVERY vanilla water terrain tag onto every generated liquid uniformly, including
  `dbh_water` onto tar/propane/acid — a known, deliberately-deferred simplification
  from an earlier spike, not a new bug; don't "fix" it without an owner call on which
  tags apply per liquid.

## Closed since the last handoff (14)

- `BOOMFAMILY_PAWNKIND_CUTS_1` — cc582d6329f833a4a49baf0a908cf9e33cae22f6
- `BOOMSNAKE_CUT_CONFLICT_1` — e63fae1e3
- `DROID_REPAIR_FOR_PROFIT_EVENTS_1` — 7160e8a5020dec09afe91fccb0c66f8615b7385c
- `PITCELL_PRISONER_BED_BRIDGE_GAP_1` — 93a9d49973317223554c49f1ec36cba94cf7d08b
- `TIBANNA_EMBARGO_PLOT_1` — f2926bfebaed173ca76d61a033cb17bce753fe2f
- `DOING_SEDIMENT_RECLAIM_1` — 4117ae00bb6a465661a6d15b240e67b353b29230
- `PYRELANDS_MAPGEN_SCRUB_1` — 10165d659809726cc13d87420cf06fd225ff3a9e
- `FLAMEFANG_SNAKE_REBIRTH_1` — 9490e2aa8f7e25cefbb05fee0aaec64d0a76a7a9
- `AFTERMATH_DEAD_LETTERS_1` — ed8398f9d6fc44cff992ff325ea4dfa16b74ef8c
- `AFTERMATH_TELEGRAPH_REFERENT_1` — ed8398f9d6fc44cff992ff325ea4dfa16b74ef8c
- `FLOWWORKS_MECHANICS_TABLE_STALE_1` — 5c11150e36442347f1dfd50af2940d56557231de
- `WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1` — 6cdf52b39875701a7867549a7e67cdfb77fda5c2
- `GRAFFITI_WARNGLYPH_INUNIVERSE_1` — d2256aea5aa35a51cbe9756a67ee1ddceb6b6510
- `ORACLE_FALLBACK_UNVALIDATED_1` — 81325f011dfc45b9d2a940cd0d2a6651a7b7e67a

## Filed and still open (52) — the next seat's queue

- `GREENTIDE_MECHANICS_2` — The Greentide C# kit build: wet-bulb condition+gear, dry-air blower, steam devils (Scald damage already shipped by FORGE), Roil/Breaklight weather, th
- `PYRELANDS_ANIMALS_GENSTEP_1` — GenStep_Animals NREs on Pyrelands mapgen (BiomeDef.CommonalityOfAnimal ArgumentNullException via Alpha Animals commonality postfix) — wild fauna genst
- `BIOME_KITS_PUSH_TO_TEST_1` — Push every biome mechanics kit (Forge/Scald/Miasma/Sump/FeverWood/RustCathedral/Greentide/Scarlands) through spike+build passes toward live-test readi
- `SCARLANDS_MECHANICS_2` — The Scarlands C# kit build: Scarlands mark hediff+severity floor, plated-grazer scaria onset, Forgotten Sentinel defend-only AI, pre-sprung danger dre
- `PYRELANDS_GRASS_SATURATION_1` — Pyrelands ground cover: grass everywhere, ash where burned, no bare dirt
- `QUICKGRASS_GROWTH_STAGES_1` — Quickgrass green-gold art plus three growth-stage graphics
- `PYRELANDS_FIRE_CADENCE_1` — Pyrelands fires arrive every few days as the biome clock
- `FURNACEBEAST_THERMAL_CYCLE_1` — Furnace-beast thermal capacitor cycle: migration AI, true heat immunity, thornvine diet
- `RAZORJACK_IDENTITY_RESTYLE_1` — Razorjack restyle: grass-camo art, our-modspace description, new SW name
- `BOOMALOPE_CUT_EVERYWHERE_1` — Boomalope cut everywhere: roster, patch, Cherry Picker, in-joke lane dead
- `PYRELANDS_FACING_REGRESSION_1` — Creature facing inverted on both axes despite FACING_COMPLETE closed
- `NUNA_ART_REGEN_1` — Nuna art regeneration
- `ANOOBA_DRAWSIZE_FIX_1` — Anooba renders far oversized on Pyrelands map
- `IRIAZ_ART_REGEN_1` — Iriaz art regeneration
- `FIREHAWK_FLIGHT_BEHAVIOR_1` — FireHawk and all flying fauna get donor-style flight animation
- `SCORCHFRUIT_ART_REGEN_1` — ScorchFruit art: half-buried in ash, cracking open, no stalk
- `MANTISTANIS_CAMO_REGEN_1` — Mantistanis eco-camouflage regen all facings
- `BARBSLINGER_REDESIGN_1` — Barbslinger redesigned: domed scorpion form with bifurcated double tail
- `XENOTYPE_NONCOSMETIC_FIXES_1` — Fix the non-cosmetic xenotype canon defects in gen_races_mod.py: water-breathing for four aquatic species, five wrong-species nameMakers, two missing 
- `TWILEK_TROPE_GENES_MOVE_1` — Move the Twi'lek submissive-aggression, high-libido and beautiful genes off the xenotype and onto individual pawns as a background or trait, so a ster
- `VALIDATION_SCRIPT_BACKFILL_1` — Write validation.py for the 59 mods that have a walk and no script - state assertions now, shows= added per mod as each checklist is validated, so thi
- `MANY_WATERS_DRILL_BUILDINGS_1` — Many Waters gains drill/tap buildings that raise a liquid from underground on maps whose subsurface yields it - his fourth acquisition route, and the 
- `FLUID_SOURCE_STOCK_MODEL_1` — Give CompFluidReservoir a real volume stock per the owner's 2026-09-16 reversal - debit on fill and on pump, limited-vs-limitless by map-edge contact,
- `CANAL_FILL_IN_DISPLACEMENT_1` — Fill-in designator that displaces a canal cell's liquid back into connected channel and source, crediting whatever has room and destroying only the ov
- `TAR_VISCOUS_SURFACE_ART_1` — Give tar a viscous surface instead of tinted water - adopt Alpha Biomes AB_Tar/AB_TarPits by the same MayRequire pattern ManyWaters already uses for A
- `EMBERGRASS_LEAFLESS_ALTS_1` — EmberGrass leafless: additional variant sprites
- `OFFBIOME_SHEET_RERENDERS_1` — Sheet rerenders outside Pyrelands: bolotaur, gualaar, fulgurite
- `CANYON_FLOOD_ERASES_CANALS_1` — A canyon flood permanently erases a dug canal - RM_MapComponent_CanyonFlood.StartFlood writes SetTerrain over every flood cell and RecedeFlood convert
- `LIQUID_SINK_DRAINAGE_1` — Map-edge sinks that drain a canal on purpose - the inverse of a limitless source, so liquid leaving is transferred off-map rather than destroyed and o
- `FLOWWORKS_BUILD_PROGRAM_1` — FlowWorks - the phased build program for one liquid mod built on excavation depth as the primitive, carrying 27 owner rulings of 2026-09-16, two Deskt
- `STALE_RENAME_GATE_SWEEP_1` — Sweep the dead NAMING_SCHEME_EXECUTION_1 rename gate out of ~10 design drafts (item closed 2026-08-31 at 54a8e28d); also fix liquids_framework_design.
- `SALVAGECLAIM_WALK_STALE_1` — design/validation_walks/RimMandrake/SalvageClaim.md names a subject that no longer exists (src/RimMandrake/SalvageClaim is gone, consolidated into Rim
- `GRAFFITI_VANDAL_ART_REGEN_1` — Regenerate all 6 RM_Graffiti_Vandal variants as punk/urban marks with ZERO real-world lettering (vandal_0.png ships the donor author's legible tag 'TA
- `GRAFFITI_VARIANT_COUNTS_1` — Graffiti variant counts are lopsided 6:2:2:2 - Scratches, TallyMarks and WarningGlyph have only 2 variants each so Graphic_Random repeats visibly on a
- `WRECKEDMACHINES_MOD_SETTINGS_1` — WreckedMachines ships NO Mod Settings at all (no ModSettings/DoSettingsWindowContents anywhere in the mod, MEASURED 2026-09-16) - violates MOD_OPTIONS
- `DEEP_TRIBES_FIRE_RITE_1` — Deep Tribes fire rite: arrive, ignite the burn, harvest scorch fruit, leave
- `PYRELANDS_TERRAIN_BURNDEF_1` — RM_FE terrain burnedDef flammable config errors on load
- `FLOWWORKS_BUILD_PROGRAM_1` — FlowWorks program 1: depth/fill primitive, pulse engine, stock model, tier rendering
- `ATMOSPHERIC_BASE_BUILD_PROGRAM_1` — AtmosphericBase (mandrake.rm.atmosphericbase): the ambient framework the gods speak through — light AND sound, designed in full with the owner 2026-09
- `NINEFOLD_LOUDNESS_FRONT_1` — Ninefold owes LOUDNESS and THE FRONT, which canon rules exist and no code computes — MEASURED 2026-09-16: GameComponent_Ninefold's entire public read 
- `MODCHECK_STATUS_ORPHANED_BY_RENAME_1` — modcheck_status.json records the canal mod's GREEN under the dead key FluidCanals while the mod ships as FlowWorks, and there is no CLI verb to move o
- `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` — Regenerate three top-down south facings caught by the new viewpoint gate: GR_Mantistanis (v5 south, drained unattended, never eyeballed), FurnaceBeast
- `BARBSLINGER_SCORPION_REDESIGN_1` — Barbslinger redesigned: yellowish large scorpion-like creature, bulbous domed body, TWO independent tails each carrying an unusually large javelin-lik
- `MAYREQUIRE_OPERATION_INERT_SWEEP_1` — MayRequire on a patch Operation is inert — sweep all uses; Class= injections are whole-file killers
- `ROT_SPORECLOUD_PORT_1` — Port RUT_SporeCloud off the donor's compiled GameCondition to RC4's GameCondition_EnvironmentalWeather (unblocks BMT_FAUNA_ABSORPTION_1 gate 3)
- `ROT_SHEEN_WEATHER_1` — The Sheen: RUT_ weather reskin defs + permanent exposure condition + SporeFlesh ladder (fixes the live ban-3 'Rain' violation)
- `ROT_DECAY_HARVEST_1` — The gut digests: RM_MapComponent_AcceleratedRot (exposed rottables/corpses/filth) + RM_MapComponent_LivingProduce freezer-heat
- `ROT_WARM_MAT_1` — Metabolic warmth: RM_MapComponent_WarmGround mat-floored room heating + RUT_GrownFurnace plant/building loop + RUT_Gene_Furnaceblood (fallback strengt
- `ROT_LIVE_PREPARATIONS_1` — Live preparations: brewing vessel + three teas + three symbiont pairs, all dying-if-stored (CompTemperatureRuinable + CompLifespan on every item)
- `ROT_GUARDIAN_GROVES_1` — Guardian groves: three tea-source mushrooms that defend themselves (RC1 spore gas, mycelial alarm, grasping-mat lure)
- `ROT_HEALTH_SHARING_1` — Health-sharing comps: RM_CompWoundLink wound-splitting + RM_HediffComp_KinMending tend-aura, content-blind, tamed included
- `ROT_PALE_TREE_1` — The pale tree: Plant_TreeAnima reskin, psylink capped by a one-entry requiredSubplantCountPerPsylinkLevel list, RUT_PaleMoss subplants

## Commits

```
948c21d3b MSEDroidFix: add validation.py (VALIDATION_SCRIPT_BACKFILL_1); rimflow ledger sync
48b72ac41 MLIE_FAUNA_ABSORPTION_1 Pass 9: port Gelagrub, Gorg, Gornt, GraniteSlug (68 -> 64 remaining)
23d41cb44 BENCH reboot handoff 202609180208: crash forensics + world switch + Rot ticketing
60862f6e0 rimflow: ledger sync (bridge release, FlowWorks hold note, game states) + archived load logs
517ea471e Retire PyrelandsFireEcology (FIREECOLOGY_SHIM_RETIREMENT_1)
a82ccc79c rimflow: DESERT_TRIBES_FIRE_HARVEST_1 filed (owner ruling moves the idea to the scenario); shim retirement claimed by BENCH
31c6e44b5 rimflow: file FIREECOLOGY_SHIM_RETIREMENT_1 (donor shim orphaned by the world switch)
dd1c978f1 ROT_HEALTH_SHARING_1: RM_CompWoundLink wound-mirroring + RM_HediffComp_KinMending heal aura
b3457a829 Pyrelands walk: draft the fire-ecology must-show bars (scorchfruit, ash weathers, regrow, ground ladder)
386d51170 rimflow: owner art direction for barrels/buckets (LIQUID_BOTTLE_LOOP_1)
d2fd296c3 rimflow: sync ledger (ROT_DECAY_HARVEST_1 claim/start/note)
b5b947fe9 ROT_DECAY_HARVEST_1: RM_MapComponent_AcceleratedRot + RM_MapComponent_LivingProduce
3d6479f41 rimflow: owner art direction for the universal cargo tank (LIQUID_BOTTLE_LOOP_1)
f5ce015e7 Pyrelands walk: bleed attribution corrected to the biometransitions module; R&D deactivation noted
1cbb4e7dc Pyrelands walk: interior-tile rule on the census steps (Odyssey neighbour-bleed); lesson
7690c96fb Pyrelands walk: VALIDATED north star — correct plant + animal distributions (owner bars)
08e11f160 LIQUID_BOTTLE_LOOP_1: buckets and barrels, same generalized chain
34cc5dab1 rimflow: sync ledger (ROT_SPORECLOUD_PORT_1 claim/start/note)
44b4f3549 ROT_SPORECLOUD_PORT_1: port RUT_SporeCloud off the BiomesCaverns donor class
5dfaf7c79 LIQUID_BOTTLE_LOOP_1: fill/use/dirty/wash JobDriver/WorkGiver pair
d29708a79 rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 43 note)
1c1b77bb3 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 4 mods (wave 43)
bc57d6eaf mapsynth: document render_designs.py in README pipeline table
f0e697a0a rimflow: PYRELANDS_WORLD_SWITCH_1 closed; 8 ROT_* kit tickets filed for FOUNDRY
eb1f92993 Transient: Pyrelands world-switch evidence (222 tiles pre/post CSVs) + review shots
21970f0cd rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 42 note)
d0c97fd51 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean RimUtinni/MenuShell (wave 42)
0b7206abc rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 41 note)
37d213eae DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 28 remaining ArtOverride mods (wave 41)
5f63bb262 rimflow: sync ledger (MLIE_FAUNA_ABSORPTION_1 Pass 8 note)
7d6efe921 MLIE_FAUNA_ABSORPTION_1: item note for Pass 8 (FeralNerf/Nerf/FrilledGorg)
9aaf55cec DIRTY_CODE_REVIEW_STANDING_LOOP_1 (wave 41): add missing LICENSE to NunaArtOverride
32e8d6ca9 MLIE_FAUNA_ABSORPTION_1: worklist update after Pass 8 (71 -> 68)
7e302ad7a MLIE_FAUNA_ABSORPTION_1 Pass 8: port FeralNerf, Nerf, FrilledGorg (71 -> 68 remaining)
71167b724 rimflow: sync ledger (LIQUID_BOTTLE_LOOP_1 full-modlist validate_patch confirmation)
b296de839 LIQUID_BOTTLE_LOOP_1: bottle-ThingDef generator + empty/dirty item chain
fefa06ffa DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 32 ArtOverride mods (wave 40)
38ce6b1fa DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 7 small RimMandrake dev-tool mods
57d78d214 rimflow: sync ledger (MLIE_FAUNA_ABSORPTION_1 Pass 7 note)
c797f5d79 MLIE_FAUNA_ABSORPTION_1: item note for Falumpaset/Fanback/FeralGrazer pass
de99b5f8a MLIE_FAUNA_ABSORPTION_1: port Falumpaset, Fanback, FeralGrazer (74 -> 71 remaining)
7192a008b DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 10 UtinniPatches biome files
ac17db00a DIRTY_CODE_REVIEW_STANDING_LOOP_1: fix 3 wrong wildAnimals MayRequire gates
4bb61f11a Rot kit spec: 9 mechanics mapped to engine + 8 FOUNDRY tickets + 6 owner cards
6bb047413 rimflow: sync ledger (LIQUID_THIRST_CHAIN_1 blocked on LIQUID_BOTTLE_LOOP_1)
f2f0e962e Pyrelands fauna: gate GR_Mantistanis on Spino.Megafauna (keyed-element MayRequire)
39e885c78 rimflow: WRECKED_DISTILLATION_MODULE_1 needs owner (mechanism ruling, not deploy)
f7a91e44f rimflow: sync ledger (WRECKED_DISTILLATION_MODULE_1 note + claim/start)
4a5625629 FlowWorks: LiquidDef.distillable flag, six water-family rows opt in (WRECKED_DISTILLATION_MODULE_1)
0f7d6cb3d rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note)
619c5508d DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 3 UtinniPatches wiring files
59173f610 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark-clean 12 files (hooks + PyrelandsMechanics)
d966fa898 PyrelandsMechanics: drop two dead XML-configured comp fields
ce2f24872 queue_lint.py: fix root-.md all-caps exemption, unreachable via isupper()
8fb20eed9 rimflow: sync ledger (LIQUID_REGISTRY_CORE_1 second-slice note)
0cc6bdfa3 FlowWorks: v1 LiquidDef registry rows, generator-emitted (LIQUID_REGISTRY_CORE_1)
fe0c15a0a lessons + sweep-item census note (missing-type pre-flight, DLL drift, review finding)
8fc55cc94 rimflow: MAYREQUIRE_OPERATION_INERT_SWEEP_1 filed + world-switch note/watch-out; lesson
01eca070e UtinniPatches: real FindMod gates on the two EnvironmentalHazards comp injections
2de4bd27d BENCH reboot handoff 202609172331: Pyrelands wave + live-review skill
fc9d9c62c rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
4d1f89181 FireHawk: wire wing-flap animation via PawnRenderNodeProperties_Spastic (FIREHAWK_FLIGHT_BEHAVIOR_1)
ccf5d0285 StructureInjectionsSW: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
087b556fa rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
c57b3b03a StructureInjectionsRUT: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
a250251ef StarWarsPatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
535840f2b rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 wave note)
aef515fdd SacredGraffiti: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
e1f053fb4 Cuisine: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
36e27e912 RaidRedesigner: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
89b8439e3 UtinniPatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f1dfdf882 SWBestiary: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
b7cacb9e9 LongHunger: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
3c416d58b DesertVehicleReskin: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
7bbf3391c PlantGrowth: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8690a8bcd rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
df99a89e3 BirthHatchDemo: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
aa8ee4e3a WeatherSuite: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
40ce13844 Rites: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
b8ea593a5 LoadTracer: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
c4fa7f413 AshkarrWeatherSuite: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
be2852a6f Doctrine: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8a88fc66d RimDefDump: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1c06dcf5c Visibility: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
4696bd32c AshkarrLandmarkArt: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
c19799667 PlanetPresetPrime: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8738e2eb9 rimflow: sync ledger/queue for MODCHECK_STATUS_ORPHANED_BY_RENAME_1, VALIDATION_SCRIPT_BACKFILL_1, GRAFFITI_VARIANT_COUNTS_1
817cdb37d LanternDeeps: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f05a72988 Graffiti: add one new Scratches/TallyMarks variant, two new WarningGlyph variants
d0b02d0be Oracle: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
74130acaf EmpirePursuit: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
9f23d9845 AshkarrInhabited: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1c3fcf7d3 RestrainingBolts: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
df0d9d1b4 StrandedQuest: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1d49ca2fa JawaRules: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
33d5d1ece KotORBandolierNorthFix: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f145b6587 AshkarrFlora: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
bfadfd5b9 MenuShell: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
14a8a0080 AftermathRites: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
61141c531 JawaVoice: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
868452fa4 MandrakePatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
e6ae928f5 IshkoDarkLandmarks: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1e30d7d1d New skill: rimworld-live-review + stage_review.py helper
e4481b066 modcheck: add validation.py for RustChrome (first slice of the 63-mod backfill)
b110a7a2d modcheck: add rename-key/forget-key verbs; retire dead FluidCanals key
363098d4d rimflow: sync queue views
b003ac6ef rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note)
058e113c2 review: mark 9 unreviewed validation.py suites CLEAN (wave)
d28bf3edf rimflow: sync ledger/queue views
8dac88fec Merge remote-tracking branch 'origin/main'
08cf0cc10 chore(sync): FOUNDRY 2026-09-17 — codebase_health.html, codebase_health.json, codebase_health_artifact.html and 2 more
ce29736c5 artpipe: terminate all Pyrelands jobs from failed/
b765afbfb chore(sync): laptop 2026-09-17T15:21:32-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
fc16d5507 Twi'lek: remove the 3 trope genes from the species (first slice)
dc71e87aa MACBENCH reboot handoff — two checkers shipped, and a pit that was never a building
7ef5345b8 Ledger: FOUNDRY note on XENOTYPE_NONCOSMETIC_FIXES_1
24c711562 Xenotypes: fix 9 placeholder descriptions, drop 5 wrong-species name-makers, correct Sith caste labels
4518b563b Pyrelands: plantDensity 1.15 -> 1.55 (owner walk: still too bare)
fbea87682 rimflow: sync ledger/queue views
4b622e11b Ledger: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
81325f011 Oracle: validate the fallback letter too, not just the live reply
848a54cc1 Code review wave: mark 6 files clean, zero findings
616570761 All ten of the spec's open questions ruled — and the depth answer raises the bar
4037168ab Ledger: 3 FOUNDRY items closed/dropped this wave
3b446a8e2 set_current_map: hide the world layer too
d2256aea5 RM_Graffiti_WarningGlyph: replace both ISO hazard sprites with in-universe glyphs
285fd7552 Ledger: note FlowWorks code-review wave on DIRTY_CODE_REVIEW_STANDING_LOOP_1
173022c4c Mark 28 FlowWorks C# files CLEAN after full-file review
b32878458 Add a sanctioned emergency repair path for a torn ledger line
10bf37afc FlowWorks: fix ReportCell debug action's missing off-map bounds check
1a5f5b3ed Pyrelands: choked with grass (owner ruling, live walk 2026-09-17)
bb0872341 Sweep the closed NAMING_SCHEME_EXECUTION_1 rename gate out of 10 design drafts
f84421661 Ledger: repair unresolved git-stash conflict markers from d2414508e
d269fbf1b jawa/set_current_map: the Game.CurrentMap setter the bridge never exposed
d2414508e Four more pit rulings, and a door family commissioned out of one of them
d5ad5e05d rimflow: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
ab8f9df9a Mark 7 files CLEAN after full-file review (Armoury absorption generators, Oracle client, StarWarsRaces head types)
0afdb147c gen_kotorweapons_absorption.py: fix bare-defName collision false-positives
d5f35b021 rimflow: block BAZAAR_BROKER_TAB_1 on the same open Bazaar dependency chain
ac50a6526 rimflow: block BAZAAR_BANTER_LINES_1 on the same open Bazaar dependency chain
bbb4a697c rimflow: block BAZAAR_HAGGLE_DUEL_1 on open price-engine dependency
50f5d56f0 Greentide: rebuild assembly for the BaseWorkAmount cache fix
f2ec05625 rimflow: note wave progress on DIRTY_CODE_REVIEW_STANDING_LOOP_1
3bbfd88fd Mark 5 files CLEAN after full-file review (Greentide dig-out-buried, ProximityHatch props, RustCathedralHum attitude system)
a136c3b7e Greentide: freeze BaseWorkAmount at job start instead of recomputing live
e48443a16 Seven RUT biomes: generatesNaturally=false — they were breaking ALL worldgen
34f395caf FOUNDRY afk wave: block LANDMARK_NAMING_PASS_1, NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1, TILEGEN_SILENT_REUSE_1
6e52b2b3b rimflow: close WRECKEDMACHINES_VFE_SMELTER_REMOVAL_1
6cdf52b39 WreckedMachines: remove the donor Automated Smelter from the build menu
080e6f87f rimflow: close FLOWWORKS_MECHANICS_TABLE_STALE_1
5c11150e3 flowworks_mod_definition.md: correct section 4's mechanics table against real source
863ae4aa0 rimflow: close AFTERMATH_DEAD_LETTERS_1 and AFTERMATH_TELEGRAPH_REFERENT_1
ed8398f9d Aftermath: wire the baseline letterLabel/letterText, fix the AlliesArrive telegraph referent
eefafc7c1 rimflow: note DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
1cdc095a3 DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave: mark 14 files clean, zero findings
0aa131589 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave (13 files)
bc08f013b mark-clean: 13 files reviewed in DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
c1ae25eaa DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave: fix misleading ConfigError in EnvironmentalHazards
735ecd850 rimflow: close FLAMEFANG_SNAKE_REBIRTH_1; block two more stuck items
0306dc1c8 rimflow: reassign the three held Pyrelands items to BENCH
239a59567 rimflow: PYRELANDS_GRASS_SATURATION_1 -- Bush/PincushionCactus ruling recorded
47aabd98c Pyrelands: evict Plant_Bush and Plant_PincushionCactus from wildPlants
ebde5ad1c BAZAAR_WINDOW_GRID_1: The Bazaar mod skeleton, slice 1 (plugin defs only)
5fad77171 rimflow: note on DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave
7d87d8d3c Mark 4 files CLEAN (dirty-code-review wave): handoff.py, EnvironmentalHazards mod C#+csproj, mapgen_paint.py
2d48e8c5d handoff.py: bridge-holder gate used substring match, false-positive on a seat whose name is contained in another's
7dc279764 DEBUG_ACTION_ENUM_CRASH_1: add jawa/debug_action_yielders, per-yielder try/catch
0238b1f69 Four rulings on the pit spec: fluid per body, LAW 2 gets an exception
8ae4fa67b rimflow: LiquidDef registry first slice; block two dependent liquids items
bf3d6744a Mark art_checks.py, art_legibility.py, build_pyrelands_art_sheet.py, gm_blackboard_shadow.py CLEAN
69e7933af Code review: fix double-counted Cathedral Regard delta and a rung-skip in the conduct-posture stage machine; art_checks stops misdiagnosing a blank sprite as clipped
30880dca5 FlowWorks: LiquidDef registry skeleton (LIQUID_REGISTRY_CORE_1, first slice)
63f2e5623 rimflow: Pyrelands XML sweep — genstep NRE correlated, grass item noted
decc20622 rimflow: close PYRELANDS_MAPGEN_SCRUB_1, DOING_SEDIMENT_RECLAIM_1; block MODCHECK_DONOR_ENVIRONMENTS_1
baa2a0fb6 Merge remote-tracking branch 'origin/main'
e038d3f4e Pyrelands: correct the stale wildPlants comment (PYRELANDS_GRASS_SATURATION_1)
9c714b69f Spec the pit-superdeep collapse — and three things the ruling could not see
4117ae00b ARTPIPE_FAILED_REQUEUE_1: drop 27 gemini-banned failed jobs (lockjaw_improve_*, mantrap_improve_*)
0dd3ab9c3 Ledger sync: FOUNDRY dirty-code-review wave note (EnvironmentalHazards batch)
b8cd4cecc Mark 8 EnvironmentalHazards Fever-Wood-spike files CLEAN (dirty-code-review wave)
d3aa7fb5d Three eye-level souths wired (owner "Yes", 2026-09-17)
ff88071af Mark 22 files CLEAN (dirty-code-review wave)
cf2657ae8 Ledger sync: three eye-level souths delivered, awaiting owner verdicts
d79860270 DEPLOY_HOLD: hold Absorbed_OPTurret.xml, donor rpgwanderer.opturret still active
f5e25eeaa AA_FireWasp south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
9613cfe3b Merge remote-tracking branch 'origin/main'
9b8ccfdac rimflow: block 3 more Rust Cathedral arc items on their shared foundation gate
a4debf028 Lesson: a backgrounded agent dies at 600s of silence, losing the whole run
81246e666 FurnaceBeast south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
bc1fe302b rimflow: advance 3 more stuck items (belt-mode sweep)
9b63a43cc rimflow: FISH_BESTIARY_COMMISSION_1 correctly needs owner, not offline
7b9012ac9 rimflow: re-block MOVING_DUNES_BUILD_1 on the load-round shader gate
d6954229f rimflow ledger: recover + replay events lost to a git-stash mishap
92c5243f9 Mark-clean wave: 6 Utils files (migrate_names, selftest_art_checks, selftest_pit_logic, run_selftests, statusline, modset_builder)
66fbc9bbc modset_builder: stop hardcoding "down from 568" for the full mod count
dfbfa3a5c GR_Mantistanis south: eye-level front portrait candidate (PYRELANDS_SOUTH_TOPDOWN_REGEN_1)
f2926bfeb Merge remote-tracking branch 'origin/main'
aabb71efe the_forge.md §8's TIBANNA_EMBARGO_PLOT_1 pointer now lands on the real spec
5bff71c14 The pit's art was already ruled, and Quarry proves the collapse can look right
7f169188b FireHawk south: symmetric portrait wired (owner "Yes! Go", 2026-09-17)
23a3e4832 chore(sync): laptop 2026-09-17T12:14:54-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
756196f2a A pit is a superdeep cell, not a building — his ruling, in full
91ea31041 chore(sync): laptop 2026-09-17T11:03:08-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
8396e0c64 Ledger sync: symmetric south validated, awaiting owner verdict
d6e591819 FireHawk south: symmetric-wings portrait, split into body+wingL+wingR layers
fa27e1cab modcheck doctor: the five registries must agree, and the summary stops lying
d004443e4 Barbslinger scorpion v1 wired (owner approved 2026-09-17)
d029ade7d FlowWorks and WreckedMachines: false text out, re-validated on his word
67b6214ad Ledger: file DETERMINISTIC_CHECKER_WAVE_1, drop NORTHSTAR_HASH_SCOPE_1
5a0935a14 Bar-scoped hashing is declined, not deferred — and §6a survives it
2b8dbd314 walklint: 25 walk steps assert the absence of an id that cannot exist
917c1722c Ledger sync: wingsplit validation verdict + review sheets
1ff8b8f7f FireHawk wing-split art for FIREHAWK_FLIGHT_BEHAVIOR_1
4447ba4f6 validate refuses a zero-bar section — his re-validation path is now the gate
3a1b7072f Barbslinger scorpion redesign: fresh 3-facing candidate set
ddfeecc4f Ledger sync: Pyrelands art rulings + top-down-south regen item
c046853da BENCH reboot handoff — and four checkers that lied
bb51a1aac 29 faces can take skin colour again
86ed9a960 facing_set_audit: south viewpoint gate (the top-down-south class)
daf766e30 Ledger sync: FlowWorks Phase 5 live-restart pass closed out
fac8d2672 Full mod list: add 3 missing Pyrelands mods
bd9a1b8ee Gizka: dino_v5 is the locked set (owner, 2026-09-17)
9e7e773a0 Wire approved Pyrelands creature render wave into art-override mods
1f8d8b20b FlowWorks: fix viscosityClass casing, was silently discarding vanilla terrain
de46f98c1 Gizka biped + Iriaz v2 wired (owner rulings 2026-09-17)
b2a800d5c Ugnaught skin is dull pink, on the films
9e6ad6ce8 chore(sync): laptop 2026-09-17T08:47:44-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
a97ce794e The canon dossier he will check by hand
f60d197b0 Six species get the skin canon actually sources
ccf21240a Four species rulings, and the reverse audit he asked for
d11280cda chore(sync): laptop 2026-09-17T08:29:17-07:00 — infrastructure/DETERMINISM_ASSESSMENT.md
657d2a8fd chore(sync): laptop 2026-09-17T08:13:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
071a4e667 Every checklist now names a folder that exists
f873119d9 Repair the documents before writing to them
db60eff8d Ledger sync: FlowWorks Phase 5 recovery note
52e312a15 FlowWorks Phase 5: superdeep capture, ladders, ruling-23 shooting rule
8afddf9a9 Ledger sync: union of the rebase-window events
c63807a9d Pyrelands: rescue 5 flora textures that lived only in the game copy
ce96c5b7d Strike the reservoir era from the canal walk
875bada07 Step 1 was a check that could not fail
4071837b1 chore(sync): laptop 2026-09-17T07:01:25-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5dd16639f Only mods you can look at owe visual bars
538796cd9 The canal's 16 bars are his now
77ca3c8b5 chore(sync): laptop 2026-09-17T06:41:19-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
d753e6a11 Declare the canal's three change bars, and delete the claim that there was one
353f59404 Two lessons from the ship-lighting walk
5a2798ef7 Stop the ship-lighting north star at intent, on his word
4c8075f65 Three rulings on the ship-lighting list: one cut, one moved, one split in four
77f8f7a33 Ruling: the alarm may be learned, not read on sight
2cb408c31 chore(sync): laptop 2026-09-17T06:12:52-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
76c910258 Ruling: a north-star bar about change is evidenced by a frame sequence
d122894ff File the canal walk under the name the mod actually ships as
25aa8864a chore(sync): laptop 2026-09-17T05:27:57-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
1eefeae9a File the stale mechanics table, with the rows I verified myself
c2c0e1a6f Rulings 34-36: walking the canal checklist deleted art instead of adding it
7a41307da chore(sync): laptop 2026-09-17T05:06:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
f20473605 Four rulings onto the ledger; the law-conflicts item closes with all three resolved
872b3814e The gods are holograms, so a dark ship is witnessed after all
2a00b10ac chore(sync): laptop 2026-09-17T04:27:07-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 5 more
15414ff32 PITCELL_PRISONER_BED_BRIDGE_GAP_1: live proof closes it
f54338cfe DROID_REPAIR_FOR_PROFIT_EVENTS_1: live verify closes it
69664cff7 chore(sync): laptop 2026-09-16T22:21:51-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 4 more
2e4029791 Drop the Transient duplicates a rebase reinstated
b09f87f67 Phase 0 is eight questions, not seven — the doc claimed an edit I had not made
cae747843 Six lessons from the AtmosphericBase sitting
407855a27 The repo answers back: AtmosphericBase has no canvas, and no rank supplier
7160e8a50 FlowWorks rulings 28-33 recorded; Quarry perspective reference saved
c4ca4fe3c AtmosphericBase hook ecosystem: the rank source is owed, and the ship has no canvas
0e5d58211 The AtmosphericBase build programme: eleven phases, and Phase 0 is only questions
a6bb05724 Fix the walk's line format — the parser read zero lines from the first draft
8bb7c29d2 FlowWorks Phases 2-4 complete; Odyssey decoupled; canyon flood is a client
c1e67088b AtmosphericBase's north star, and an axis the system does not have
6999f2c85 AtmosphericBase: the mod he designed tonight, with every ruling verbatim
4c3ed4151 FlowWorks: LiquidCorrosion/LiquidIgnition gated OFF by default
6a073f249 artpipe state sync: six claimed pending files, throughput log
cade628c1 FlowWorks Phase 1: rename, ruling-24 deletions, three-mod merge (FLOWWORKS_BUILD_PROGRAM_1)
e3b6b577d FlowWorks Phase 0 blockers MEASURED via RimSage; gizka dino v5 rendered
0d1fed5d7 chore(sync): laptop 2026-09-16T21:00:36-07:00 — Transient/dynamiclighting_scheme_catalog_DRAFT_2026-09-16.md
57fdb69cb Gizka is a dinosaur, not a frog — owner's KOTOR references land in canon
942ccc764 codex_image.py: stdin=DEVNULL cures the daemon-wide stdin hang; gizka v4 r2 rendered
45f6884ab Gizka review rulings: two eyes, east/west are side profiles (owner 2026-09-16)
a7c1d5792 Pyrelands census sheets 2026-09-16 + 3 EmberGrass leafless alternates
e9e7e76ac chore(sync): laptop 2026-09-16T19:04:00-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 4 more
89232b332 facing_set_audit.py: the full wiring-time metric gate for creature facing sets
53c4dbb8b Lesson: pathspec commits are the only safe commit in the shared worktree
47efcc641 rimflow ledger sync: FLOWWORKS_BUILD_PROGRAM_1 start + core-engine note
4db4b3852 FLOWWORKS core engine: depth/fill grid, the pulse, dig-to-depth
39b977eeb FLOWWORKS art candidates: four dry-excavation depths, ladder, designators, sluice gate
6fd764fac FlowWorks program 1: grouped validation checklist, name-collision check, Liquid Logistics correction
679d1d209 Three rulings on the read axis, and a capability nobody owns
e14c9cfed FloodedCanyon: dug canals survive a canyon flood cycle
fb9345c06 File the Aftermath telegraph's wrong referent — verified, not taken on report
af1f8e69f Aftermath read-axis draft, and rule 2's telegraph names the wrong faction
6f4e7e3f5 Reboot lessons: the stale gate, the hash trap, and the pathspec rule
097bce16c WreckedMachines VALIDATED, and the owner overruled the judge asymmetry
b24c35d78 chore(sync): laptop 2026-09-16T17:40:51-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
11bdbeaf3 The must read axis, and it costs zero re-validation
dca82d184 WreckedMachines' north star, and the owner chose to bind a vision he has not built yet
abb619826 Graffiti is VALIDATED and now refuses itself — the system's second proof
1320d91ef chore(sync): laptop 2026-09-16T16:52:46-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
477e2c79a Keep the north-star state: field a bare token — modcheck parses it
bddc55dc3 Graffiti's north star, ruled in an owner sitting — and it refuses two of four marks
16726a1b7 chore(sync): laptop 2026-09-16T16:10:12-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
745ddc2f0 North-star batch 1 drafted, and the dismissals were hiding a real bug
54b0acfd3 chore(sync): laptop 2026-09-16T15:54:00-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5fbbc162d Four of seven visual-pass dismissals judged: two sound, one time-bounded, one challenged
660827578 The canon library gets an index that cannot go stale, and a skill that fires
1b1620a1b chore(sync): laptop 2026-09-16T15:22:41-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
252f8ff2e Canon library census: one dangling image, and the droid item's premise is already met
7343e307f A rename gate that closed on 2026-08-31 was still stopping work 16 days later
01de1faaa The pit's art spec joins FlowWorks instead of floating beside it
df9b1c656 chore(sync): laptop 2026-09-16T13:59:31-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
69491c8a5 Regenerating the pit into FlowWorks does not discharge its visual requirement
581840a2d chore(sync): laptop 2026-09-16T13:46:56-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
f7a940c7e MACBENCH reboot handoff — and handoff.py no longer guesses the seat
c2f6977c7 A v2 dream was mostly delivered by v1, and the walk says it is scheduled for replacement
e09bd85c4 Resolve the docs and queue items today's rulings falsified
01d3bcef1 Pits' north star is VALIDATED — and the falsification test passes offline
2b9f8fbe9 Three lessons from the FlowWorks design session
5a188da03 chore(sync): laptop 2026-09-16T11:39:40-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
0ced17e8a FLOWWORKS_BUILD_PROGRAM_1 — the ticket for the Fable process on the Desktop
7fa541ef3 Rulings 24-27: sources become terrain, rain needs no roof, SUPERDEEP captures regardless of fill, merge before the pit art
76ca92619 Gizka bipedal facing set validated — artpipe state for the quota-delayed drain
43af1ae4a Rulings 20-23: the mod is FlowWorks; terrace farming general and gated; one shooting exception
1e73ce51b DEEP_TRIBES_FIRE_RITE_1: the Deep Tribes come and light it themselves
ea4b748d3 Ruling 19: four depths - plus the two laws and one algorithm that give terraces without a Z-system
f27beebc4 ScorchFruit density: one 1-in-20 roll per burned cell, not per fire-tick
5e7ab077d Ruling 18: Pits IS Canals - depth is the primitive, and it collapses three ladders into one
4d6605cef Canals and Pits compose rather than merge - and it deletes planned work
930d82498 The Fluidity boundary as a principle, plus detonation, sticky-limitless, dry-channel cost, and fill-in advice
b2866cab0 chore(sync): laptop 2026-09-16T09:45:27-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e45229d67 Gizka canon corrected: bipedal hopper — owner ruling recorded in the entry
9490e2aa8 FLAMEFANG_SNAKE_REBIRTH_1: recommit after a concurrent rebase dropped e63fae1e3
ad449c467 Propagate the Fluidity consolidation into the framework's client map
988599e40 Ruling: one mod called Fluidity, absorbing Many Waters and Liquid Logistics; sluice gates yes; ignition is per-liquid
dd5c2336c Ledger sync: PYRELANDS_SCORCHED_RUINS_1 closed, FIREHAWK_FLIGHT_BEHAVIOR_1 noted blocked-on-art
58a08013f Pyrelands: the biome's fire clock, and the furnace-beast's thermal capacitor
cad170e94 PYRELANDS_SCORCHED_RUINS_1: ruins scorch and burn via BiomeDef.extraGenSteps
f67c8d4b4 Pyrelands SW-canon fidelity check: 6 of 7 pass, iriaz fails the one-horn line
6d452b001 chore(sync): laptop 2026-09-16T09:04:38-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5af00922c File the Desktop's first task (temp-terrain DLC gate) and the sink item
ee9b32883 Ruling: this mod IS the liquid engine - plus sinks, and it needs a new name
2102e0988 File the canyon-flood-erases-canals collision
80161da41 Three more rulings: three fill tiers, self-drain returns, and burn as a rate on the tier ladder
1688d9a2a Quickgrass reads its growth: sprout, half-grown, tall lush
06b3062de chore(sync): laptop 2026-09-16T08:44:52-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
3b123dac9 statusline: the digits were overstating context headroom by ~440k
097183478 ScorchFruit ships as 4 random ash-buried variants, tint dropped, stalk art dead
0c45174ba Ledger sync: Pyrelands full-review art wave notes (4 items)
c51c341ba Pyrelands full-review art wave: 30 painterly renders, 8 canon creatures + Sytheclaw restyle + Mantistanis S/E + quickgrass burn state
44f7c9531 Two rulings: filling a canal in displaces liquid back, and tar gets viscosity first
8a7f18ad1 chore(sync): laptop 2026-09-16T07:35:41-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e824de757 The art survey: partial fill is nearly free, and tar currently looks like water
64b2c66e8 Record the FluidCanals north star draft against the 77-walk authoring item
9456d910a Draft the FluidCanals north star from his own words — DRAFT, binding nothing
219ef6bcf Fire: name what is unknown, and why the decision does not wait on it
de9c1292e The two hardest parts of the canal design are already built — in FloodedCanyon
ce2926e93 chore(sync): laptop 2026-09-16T07:14:36-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
97b613102 Fold the Pits vocabulary into the canal definition — and one line of his prose is false today
c6c8d854f Fluid Canals mod definition (DRAFT) — and RimSage cannot be reached from this machine
148db88f4 File the three items his rulings created; fix a walk asserting a field that isn't there
0f8cdabdb Scarcity is stock: propagate the owner's reversal, and delete two stale claims
80cb83777 chore(sync): laptop 2026-09-16T04:55:07-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
de7859ff4 Close NORTH_STAR_RUNNER_WIRING_1; one lesson to the inbox
758c6d7f6 The north star now binds: a run's verdict reads the screen, not just the state
a3b849fe7 chore(sync): laptop 2026-09-15T22:57:48-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
6d8d450d8 BENCH handoff: the north star system, and why a GREEN modcheck meant nothing
49b520734 facing_symmetry: record the measured false negative next to its threshold
d4462ee89 Four north-star items, and the pit as the falsification test
0e03d1bed North stars: bind a mod's intended experience to its validation run
2227c41ad chore(sync): laptop 2026-09-15T22:24:36-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
63d03b9c6 No trace of cartoon-generating art — TOYFIG terminated by owner
1433a9dd6 BENCH reboot handoff: art facts wired unarmed, and he is mid-review
1e5afdd9a Facts gate wired into the artpipe, and deliberately not armed
0b14b00b8 Keep the hash, drop the rotation test — it fires on nothing here
2ed732a4d BENCH reboot handoff, and the canon library into CLAUDE.md
e13c6148c All 137 checklists in place, and the continuity fork restored on evidence
4af7a7567 Checklists for the n-s entries
f64c4430b Sprite skill never said what north and south MEAN — that omission has a price
d52031fe8 Symmetry is a free facing check, and the donor art beats ours on it
3b406be89 h-m checklists, and a third class of limit: the pawn rig
ebdbdfe8e Checklists for the a-c entries, including a Bothan that checks negatives
226aa15ef Must-show checklists and engine limits for the d-g entries
d6873f167 Height measured on haze, not silhouette — two rows I cleared are the worst two
8e93eb153 Canon is the validation target, and every entry gains two checkable sections
4f6ee61d2 chore(sync): laptop 2026-09-15T21:39:10-07:00 — Transient/pyrelands_art_review/pyrelands_art_decisions.json
dfa55ba9a All twelve checks refuse, inside the artpipe — so the retry loop needs a cap
ab7883b91 Art review as facts, not scores — the twelve rules and why two tiers
0e742dbe3 Cuisine ingredients go wide: his quantifiers are the spec, not a shortlist
bc53af332 Five lessons from the Pyrelands art sheet, chiefly: don't restart a sidecar
5e3a2a586 Droid index continuity was wrong on 72% of rows
ccc60ff61 Pyrelands art sheet: three facings a row, and the facing law is still broken
68ab65f61 Ladder settled: Wrecked, Kludged, Refurbished, and the original at 1.0
0c91c6629 chore(sync): laptop 2026-09-15T21:02:18-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 6 more
432e4410f Reconcile the ancient machines spec with rulings made after it was written
12ddc9ae0 Bank eight operational lessons from the canon-library sweep
e3341827c All 23 droid chassis done, plus orphan gonk art nothing references
cec1a65a3 Specialist droid chassis, and four errors in our own index
c6e96b4ad Utility droid chassis, and two index pairs proven to be one chassis each
8e12e7bf6 Three more droid chassis: B1A, DSD1 dwarf spider, KX-series
7f6f43ca8 chore(sync): laptop 2026-09-15T20:20:49-07:00
fe5fe7c59 Extend the brief to droids: one entry per chassis, not per canon variant
6e733c9cd Record that the droid era column is finished at 2.7%, not unfinished
6261d3538 Era fill returns a negative result: canon does not record it for 97% of droids
a1cbe6490 chore(sync): laptop 2026-09-15T19:29:12-07:00
32ec82c2e Cosmetic genes are off limits: gate most of the findings, release the rest
2e813982e chore(sync): laptop 2026-09-15T19:11:56-07:00
f84143b34 Close the species canon library: 69 of 69
47de84d5f Species library complete: all 69 entries, and montrals that are decoration
422ce08ab Batch E: a fourth aquatic species that cannot breathe water
eeddc3484 Batch H, and a Duros head nothing can colour
0150b31d1 File the xenotype canon findings as nine patterns, not sixty mistakes
6b822500f Batch J, and skin colour that never reaches the face
be792759a Zabrak and the roster: a Mimbanese wearing a Tusken's head
75f8339ca Four more entries: the canon pages omit the traits these species are known for
279bfd4f0 Six more entries, and a Kaminoan with no neck
6a13b9079 Oversized images kill a run, so check dimensions before viewing one
3bae44878 Fourteen more entries, including a species canon refuses to draw
a88a65a72 Note Fetcher's 50,000-character cap, since it silently ate two Biology sections
d211f3acc Ten more species entries, and two aquatic races that cannot breathe water
9bb1c5eef Seven more species entries: anzati, aqualish, chagrian, herglic, nautolan, pantoran, snivvian
6cf288bd6 curl reaches the wiki API directly, so stop routing every fetch through Fetcher
01a6ea4a4 11 more species entries, and they found real art bugs in the shipped defs
cc431b9d8 Droid index QA: 1766 -> 1757 rows, and the build was already clean
cf5d56d00 Write the species-entry brief down once instead of re-briefing every batch
bd34ff636 Droid index at 1,768 rows, the race roster, and 14 image-only entries
7ce3aee14 1.0 is the ordinary modern machine, so 'exceeds modern' is withdrawn
6e149cd77 chore(sync): laptop 2026-09-15T17:22:10-07:00
b5899b14d 11 race canon entries, plus the revised grade ratios
0ac41611a WreckedMachines is not a texture reskin, so remove its false settings exemption
f9478c297 Ancient machines: one spec for the three layers and the grade ladder
da5cee683 File the two canon-library research items
cec752071 Rakatan: three layers, and no Rakatan word below the middle one
808c06960 Rakatan: three grades with real ratios, and the mod splits in two
80ddfdd1f Rakatan design session: nine rulings banked, chief among them that nothing equals the original
fc1373743 chore(sync): laptop 2026-09-15T12:06:45-07:00
86308d312 narrative dictionary: implementation plan for batch 1
6bc96eaf7 Archotech is Rakatan: land the ruling and propagate it
8ff4bd8a5 Narrative dictionary: design approved, pilot filed, Rakatan archotech captured
6e9c884b2 chore(sync): laptop 2026-09-15T05:52:19-07:00
e5bd51e9b chore(sync): laptop 2026-09-14T20:40:50-07:00
107ac16c0 Gizka 0.3 -> 1.0: pyramid law puts the grain on top (owner: 'Yes on Gizka')
8ac82bd03 BOOMFAMILY_PAWNKIND_CUTS_1: close (ledger sync)
cc582d632 BOOMFAMILY_PAWNKIND_CUTS_1 + BOOMSNAKE_CUT_CONFLICT_1: close the pawnkind gap, resolve the timeline conflict
0390c772b Barbslinger south facing wired (r3) — facing regen wave complete
5087c0f19 BOOMALOPE_CUT_EVERYWHERE_1: propagate the owner's "Absolutely no boomalopes"
dd83d8a36 PYRELANDS_FACING_REGRESSION_1: wire 5 of 6 facing-fixed regens, refuse 1
54e2fa209 PYRELANDS_FACING_REGRESSION_1: file painterly regen jobs for the wrong-facing sprites
c6e21d2d2 artpipe facing prompts spell out the camera convention; canon regen item repointed
4afc6923e PIT_TRAP_VISUAL_REDESIGN_1: pit trap visual interface spec, 3 directions for Thursday
139c4342e ART_PAINTERLY_RESTORATION_1: propagate the restored painterly law into artpipe code+docs
1f1b8ab19 PYRELANDS_FACING_REGRESSION_1 + ANOOBA_DRAWSIZE_FIX_1: Boomsnake east mirror fix, Anooba oversized-drawSize patch
fc10912f3 Scorch-fruit pod: four half-buried candidates for owner review
20387631a Pyrelands flora: drago tree, agave, dandelion evicted from wildPlants
776b07f96 Quickgrass approved art installed: tall green-gold variants live, tint removed
c6c82063a Quickgrass green-gold stage sprite candidates for owner review
08b53e328 Furnace-beast fireproof stats + capacitor lore; razorjack -> sytheclaw identity patch
9fc17ad90 Quickgrass growDays 1 — owner revised the 3-day call same day
10165d659 Pyrelands: mapgen scrub (preventGenSteps), quickgrass growDays 3, clear_chunks.py
c1bbb05cd Pyrelands: preventGenSteps blocks RockChunks+ScatterShrines; clear_chunks.py library script
cb06457c2 PYRELANDS_GRASS_SATURATION_1 filed; palette ruling noted on PYRELANDS_FLORA_ART_IDENTITY_1
40dd4d168 DROIDWORKS_FORMAT_TIERS_1: live re-test, box 1 confirmed, root cause found
83d23ae4f BIOME_KITS_PUSH_TO_TEST_1: record final status after the offline push
63d29b530 Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M3/M7
035c903af mark-clean GREENTIDE_MECHANICS_2 M3/M7 build pass files
3bcf80ccf GREENTIDE_MECHANICS_2: M3/M7 build pass, steam devil vortex + Lunger ambush
d5d55c63a Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M4/M5
1c0eedc96 mark-clean GREENTIDE_MECHANICS_2 M4/M5 build pass files
6f7f5ff61 GREENTIDE_MECHANICS_2: M4/M5 build pass, the Roil + Breaklight
00ee47b00 rimflow: bridge released after Pyrelands walk staging
88cdc3b2f PYRELANDS_CREATURE_RERENDER_1: wave-2 tally, deploy holds, Codex weekly wall Sep 19
751ac722d ART_PAINTERLY_RESTORATION_1: Zeer + Dalgo full painterly sets, rear-view norths, canon-library-cited
91f69301c ART_PAINTERLY_RESTORATION_1: Mantistanis E+N (rear-view north) + Boomsnake E painterly; sets incomplete, deploy held
3a255e2bb ART_PAINTERLY_RESTORATION_1: Razorjack full set + Nuna (m N/S interim-copied from f) + Gizka easts, painterly via Codex before weekly quota wall
06e04cc0b ART_PAINTERLY_RESTORATION_1: EmberGrass A/B/C repainted painterly (Codex) before weekly quota wall
d10a23cae Rebuild RimMandrake.EnvironmentalHazards.dll after Fever Wood F6/F7 + Greentide M6
b6799ab8a mark-clean GREENTIDE_MECHANICS_2 M6 build pass files
0dedc6cfa GREENTIDE_MECHANICS_2: M6 build pass, three-feller tree fall
1c47392bb mark-clean FEVER_WOOD_MECHANICS_1 F6/F7 build pass files
1741b389a FEVER_WOOD_MECHANICS_1: F6/F7 build pass, boughway network + fever trunks
ff348403a Rebuild RimMandrake.EnvironmentalHazards.dll after Greentide M1/M2 + M9/M12
647b306fe mark-clean GREENTIDE_MECHANICS_2 M9/M12 build pass files
07118c4e6 GREENTIDE_MECHANICS_2: M9/M12 build pass, root causeways + the Greatbole
9a4890127 mark-clean GREENTIDE_MECHANICS_2 M1/M2 build pass files
946fc0b04 GREENTIDE_MECHANICS_2: M1/M2 build pass, wet-bulb overwhelm + dry-air blower
58cd1139a Rebuild RimMandrake.EnvironmentalHazards.dll after Scarlands build pass
2c3737cba mark-clean SCARLANDS_MECHANICS_2 build pass files
52c8c982c SCARLANDS_MECHANICS_2: build pass, §2/§3/§4/§5 wired to real content
9cc0cd8e1 Rebuild RimMandrake.EnvironmentalHazards.dll after Miasma M3, Scald S5, Sump S4
735d5bef7 mark-clean SUMP_MECHANICS_1 S4 files (dread field, wander JobGiver, filth trail, placeholder mouse, filth-acceptance patch)
b3a646c3f SUMP_MECHANICS_1 S4 build pass: mouse-line telegraphy
ea9d3aedd mark-clean SCALD_MECHANICS_1 S5 files (sail scatterer validator, GenStepDef, register patch, IncidentDef, translation)
a90656d07 SCALD_MECHANICS_1 S5 build pass: bubble-sailor scatterer + walker-surfacing incident
92a5c740c mark-clean MIASMA_MECHANICS_1 M3 files (stranding pools, JobGiver, ThinkTree)
c76fc40a0 MIASMA_MECHANICS_1 M3 build pass: stranding pools and the stranded
50e7917cc rimflow: close BACTA_PAWNINTANK_RECON_1
fdca467f3 BACTA_PAWNINTANK_RECON_1: close with findings (growth-vat renderer re-entry; MIT BioReactor Continued fork)
cc382ee92 Rebuild RimMandrake.EnvironmentalHazards.dll after Forge F3/F4, Scarlands, Miasma M2
34e253cf7 mark-clean MIASMA_MECHANICS_1 M2 files (gradient axis, repaint, surge extension, surge condition)
3901f320b MIASMA_MECHANICS_1 M2 build pass: breath-tide surge
6b6231bb4 PYRELANDS_CREATURE_RERENDER_1: walk relocated to daylight tile 59952 (104504 is polar-dark); staging route + open owner questions; two lessons
28961d188 mark-clean FORGE_MECHANICS_1 F4 files (channels, biome validator, entrance/floor/scatter defs)
378f67436 FORGE_MECHANICS_1 F4 build pass: foundry tower dungeon shell (single-floor)
bc306ddc1 mark-clean SCARLANDS_MECHANICS_2 files (RC5 filter, severity floor, Sentinel lord)
8801d8429 SCARLANDS_MECHANICS_2 spike pass: RC5 scaria-arm filter, mark severity floor, Sentinel defend-only lord
83cb8f92b mark-clean FORGE_MECHANICS_1 F3 files (vapor columns, drifter, wander JobGiver, wiring patch)
0cdbc22b8 FORGE_MECHANICS_1 F3 build pass: vapor-column pasture-binding for sky fauna
6b987d33c File BIOME_KITS_PUSH_TO_TEST_1: umbrella tracker for the biome-kits push
7c9f2c7b7 Revert "ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nuna/Gizka cite starwars_iconic_creatures.md)"
02a4d5ec1 mark-clean SUMP_MECHANICS_1 S3 files (bulge, wake relay, station eater, gen step, register, job)
212775b67 SUMP_MECHANICS_1 S3 build pass: tar beast set-pieces (placement + wake + eater scaffold)
f209d892c ART_PAINTERLY_RESTORATION_1: Iriaz/Nuna/Gizka regenerated painterly, rear-view norths (Iriaz UNGATED - no canon library entry; Nuna/Gizka cite starwars_iconic_creatures.md)
3ade11b7a mark-clean 15 files: FORGE_MECHANICS_1 F2/F5/F6 build pass
b62604fad mark-clean M6 files (creche scatterer, marker, despoil memory)
ce17e0865 lesson: pathspec commits are mandatory in the shared worktree
935cbe93e rimflow sync: file PYRELANDS_ANIMALS_GENSTEP_1; two lessons (player-map regen route, staged-index sweep)
645b93f2e ART_PAINTERLY_RESTORATION_1: revert Anooba/Orray/FireHawk/FurnaceBeast to painterly v1 (owner ordered Pyrelands-wide painterly regen 2026-09-14)
197746425 mark-clean RM_WeatherOverlay_GreentideRoil.cs (GREENTIDE_MECHANICS_2)
dd56bb453 GREENTIDE_MECHANICS_2: file+spike the Greentide kit build, reconcile against already-shipped M3/M5/M8/M11
05af75f44 BENCH reboot handoff 2026-09-13 23:30: mid-walk state, load+regen sequence, today's rulings; unignore fix for registry lock
e9d7ab2c0 artpipe state sync at BENCH handoff: today's render waves through the queue
edaa118f0 ART_PAINTERLY_RESTORATION_1: MAJOR RULING - painterly style restored, cartoonish pipeline stood down
6b96cb625 Rebuild RimMandrake.EnvironmentalHazards.dll after Sump S1 build pass
a11100c51 SUMP_MECHANICS_1: record S1 build pass, mark-clean 6 files
670da445d SUMP_MECHANICS_1 S1 build pass: poured tar moat + command ignition
b2152acb6 mark-clean: MIASMA_MECHANICS_1 M5 build pass files
346490000 MIASMA_MECHANICS_1 M5: fever-forged boon tables, full strange tier
88e49f189 First-walk verdicts: Bolotaur+Gualaar done, GreenGoo wiggle study note
cbeb9e2a8 ARTPIPE_FACING_COHERENCE_1: owner ruling recorded - N faces away, S faces toward, hook mandatory, not done until true everywhere
76e940561 mark-clean: SCALD_MECHANICS_1 S6 build pass files (5 entries)
e7810e12f SCALD_MECHANICS_1 S6 build pass: burning-shallows wreck salvage
61ee1dd08 Iriaz + Nuna lawset override mods (retried norths landed); bank for next load
8dd244bd8 Pyrelands leafless grass art in; flora deploy hold lifted
a5e872617 Rebuild RimMandrake.EnvironmentalHazards.dll: fold in Forge/Scald/Miasma build passes
130d37af1 mark-clean: Miasma M4/M1 build pass files (10 entries, MIASMA_MECHANICS_1)
b1a2aa399 MIASMA_MECHANICS_1: M4/M1 build pass — weather lock+exposure, gradient axis
dde341c12 Canon-5 lawset renders installed (Anooba/Orray/Zeer/Gizka/Dalgo), Pyrelands flora art in; FULL.LATEST +42 override mods (631)
6e301d3b2 mark-clean: SCALD_MECHANICS_1 S1/S4/S2 build pass files
f4d5c1714 SCALD_MECHANICS_1 S1/S4/S2 build pass: steam sky, vent field, steam-catch
fd1b8c462 mark-clean: SUMP_MECHANICS_1 S6/S5 build pass files (dusk lock, glow, wick crop)
779a079ab SUMP_MECHANICS_1: S6 dusk lock + glow calibration, S5 wick-garden crop build pass
682f6907d mark-clean: FORGE_MECHANICS_1 F1 files (weather pulse, scald, flash growth)
0e38767e7 FORGE_MECHANICS_1 F1 build pass: weather pulse condition, scald damage, flash-interval growth
cea007c3a Art-review platform: install every gate-passed render awaiting verdict (95 stems)
f2ed05b4d LESSONS_INBOX: small-modlist in-game load is a standing art-review tier (owner 2026-09-14)
0f3cda1fc rimflow: sync ledger for FORGE_MECHANICS_1 spike-pass note
33b62fcee mark-clean: RM_CompGatherableGas, RM_CompScriptedDieOff (FORGE_MECHANICS_1 spike)
1ae30640a FORGE_MECHANICS_1 spike pass: resolve 5 engine unknowns, build RM_CompGatherableGas + RM_CompScriptedDieOff
983d41cac DEPLOY_HOLD: Pyrelands flora defs held until their sprites land
ae889ad7d Pyrelands flora own art identity: 5 defs off vanilla texPaths, leafless states rebound
3b19faa56 Canon Pyrelands prep: zeer+gizka library entries, drawsize backfill (Zeer 4.0, Gizka 0.87 MEASURED from SWAC adult lifeStages)
f28250027 modlists: capture-full adopts the post-MW2-cut 589 list as FULL.LATEST
8d1099849 Pyrelands invented-7 sprite install: RUT natives 3-facing v3, five donor ArtOverride mods (v2 renders)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: FREE    since 2026-09-18T02:07:41Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? infrastructure/artpipe/active/rotscythe_v1_south.json
?? infrastructure/artpipe/active/twistingthornweed_v1.json
?? infrastructure/artpipe/active/wastewing_v1_north.json
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
```

