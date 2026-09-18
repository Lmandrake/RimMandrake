# BENCH_REBOOT_HANDOFF_202609180208 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609172331`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**MayRequire on a patch `<Operation>` is INERT** — measured against 1.6 source
(ModContentPack.LoadPatches never reads the attribute; PatchOperation has no
field). Two "gated" comp injections applied with their mod absent, the missing
types discarded WHOLE def files (Races_Aerofleet.xml, RSW_Beldon.xml), the
dangling PawnKindDef races NRE'd AlphaGenes' gene generator, and **RimWorld
itself reset the owner's live ModsConfig to Core+DLCs** before giving up. Real
per-operation gates: PatchOperationFindMod, or MayRequire on the injected
`<li>` (honored at def parse). Fixed at `01eca070e`; repo-wide sweep filed as
`MAYREQUIRE_OPERATION_INERT_SWEEP_1` (~18 more files carry the inert form).
Same-family corollary that cost an hour: the deployed-DLL drift check —
6 of 65 repo DLLs differed from deployed, and the missing-type census
(our-namespace tokens in active XML vs all deployed DLL bytes) finds this
class offline in seconds. Both belong in pre-flight before any cold load.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Ten Pyrelands north-star bars await his yes** — his 2 distribution bars were
  VALIDATED, then his ask to "bring everything over" added 8 fire-ecology
  drafts, reverting the section to DRAFT by hash (the ruled flow). One
  `modcheck/cli.py validate Pyrelands --owner-said` re-binds all ten:
  `design/validation_walks/RimMandrake/Pyrelands.md`.
- **Rot kit ruled ready to build**: spec at
  `design/Jawa/worldbuilding/biomes/kits/rot_kit_spec.md`, 8 ROT_* tickets
  filed for FOUNDRY — but **6 owner cards** in the spec await him (tea potency,
  rot-clock scope, psylink cap gates ROT_PALE_TREE_1, +3).
- **His mod list changed, deliberately**: live = 632 (R&D list —
  `m00nl1ght.geologicallandforms.biometransitions` OFF on his word,
  PyrelandsFireEcology deleted, dead `mandrake.rm.fluidcanals` →
  `mandrake.rm.flowworks`). `ModsConfig.FULL.LATEST.xml` = 633 (keeps
  transitions for play). RimWorld had also RESET his list to 6 during the
  failed load — restored same night; snapshot committed.
- **The campaign world switched**: all 222 Pyrelands tiles are RM_FE_Pyrelands
  (read back exact, saved, backups in Saves/). `PYRELANDS_WORLD_SWITCH_1`
  closed; zylle donor retirement unblocked.
- **FireHawk wing-flap motion still needs his 5-second in-game look** — spawns
  and renders clean on the new BodyDef (the rollback criterion), but sprite too
  small in captures to judge motion.
- **Spino.Megafauna is not in his list**, so the mantistanis roster entry (and
  its art override) are dead weight until he either activates that mod or cuts
  the kind from the roster — his call, flagged on `PYRELANDS_FAUNA_WIRING_1`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
- **A cold load is IN FLIGHT on the 632 list** (launched ~02:05Z via Steam).
  The marker watcher dies with this session — NEXT ACTION on wake: check
  Player.log for `Bridge token:` (success) vs `Exception loading def from
  file` / `Resetting mods config` / `Could not recover` (failure). On arrival:
  (1) generate a fresh RM_FE_Pyrelands map — expect NO
  BiomeDef.CommonalityOfAnimal NRE and real wildlife (`f2f0e962e` fix's first
  live test, closes the loop on `PYRELANDS_ANIMALS_GENSTEP_1`); (2) run the
  Pyrelands walk's clean-tile censuses.
- **PYRELANDS_REVIEW.rws keeper is polluted** — 172 Mech_Militor landed on it
  mid-staging. Re-stage a fresh keeper (interior tile; transitions now off) —
  do not hand him this one to walk.
- **FlowWorks committed drift deliberately NOT deployed** (new LiquidTypes
  defs + DLL) — it is FOUNDRY's live bottle program; noted on
  `LIQUID_BOTTLE_LOOP_1`. Do not "helpfully" deploy it in passing.
- **PYRELANDS_FAUNA_WIRING_1 state is stale**: the wiring IS deployed (it was
  the genstep crash vector); what remains is the live wildAnimals count
  read-back on the new load.
- **5 repo DLLs have never been deployed** (Bacta = its waiting item;
  DesertVehicleReskin, JawaIonVehicleTier, RimDefDump, TheBazaar = untriaged)
  — recorded on `MAYREQUIRE_OPERATION_INERT_SWEEP_1`'s census note.
- `DESERT_TRIBES_FIRE_HARVEST_1` — design item holding the owner's ruling that
  the tribes-fire-harvest idea moves into the scenario as an event; needs a
  design pass + owner cards.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
- The headers of BOTH killer patch files claimed their MayRequire gate was
  "load-bearing", and full-file reviews marked both CLEAN (09-13/09-14). An
  engine claim in prose is not evidence — verify against source/RimSage before
  a review accepts it.
- **The biometransitions module makes biome-purity censuses lie**: a lone
  re-tiled scratch tile read 78% foreign plants — neighbour-bleed, not
  injection. The quadrant-share spatial split discriminates in one pass.
  Module now OFF in the R&D list (owner's word).
- `rimworld/save_game` wrote 0 bytes silently once, then succeeded on retry —
  stat the named file every time (already doctrine; it fired again).
- `rimworld/frame_cell_rect` after a jump can re-park the camera; and
  `rimworld/screenshot_cell_rect` rendered the CAMERA view, not the requested
  rect (observed once, unconfirmed mechanism) — verify what a "framed" shot
  actually shows before reading it.
- `rimworld/step_game_ticks` completes ~250 ticks/call on the full list before
  frame-timeout, and vanilla raid-arrival letters re-pause speed-3 runs — long
  behavioural settles need the raid source dead first (or jawa/time_set_ticks
  for clock-only jumps, which simulate NOTHING).
- RimWorld drops unknown packageIds from the ACTIVE set silently at startup —
  a list entry naming a renamed mod (fluidcanals) means the mod simply isn't
  loaded, while ModsConfig.xml still shows it. The save-load missing-mods
  refusal is the only loud symptom.
All in LESSONS_INBOX.md.

## Closed since the last handoff (1)

- `PYRELANDS_WORLD_SWITCH_1` — eb1f92993aab21e55e0265f2a68447fe476b8eef

## Filed and still open (10) — the next seat's queue

- `MAYREQUIRE_OPERATION_INERT_SWEEP_1` — MayRequire on a patch Operation is inert — sweep all uses; Class= injections are whole-file killers
- `ROT_SPORECLOUD_PORT_1` — Port RUT_SporeCloud off the donor's compiled GameCondition to RC4's GameCondition_EnvironmentalWeather (unblocks BMT_FAUNA_ABSORPTION_1 gate 3)
- `ROT_SHEEN_WEATHER_1` — The Sheen: RUT_ weather reskin defs + permanent exposure condition + SporeFlesh ladder (fixes the live ban-3 'Rain' violation)
- `ROT_DECAY_HARVEST_1` — The gut digests: RM_MapComponent_AcceleratedRot (exposed rottables/corpses/filth) + RM_MapComponent_LivingProduce freezer-heat
- `ROT_WARM_MAT_1` — Metabolic warmth: RM_MapComponent_WarmGround mat-floored room heating + RUT_GrownFurnace plant/building loop + RUT_Gene_Furnaceblood (fallback strengt
- `ROT_LIVE_PREPARATIONS_1` — Live preparations: brewing vessel + three teas + three symbiont pairs, all dying-if-stored (CompTemperatureRuinable + CompLifespan on every item)
- `ROT_GUARDIAN_GROVES_1` — Guardian groves: three tea-source mushrooms that defend themselves (RC1 spore gas, mycelial alarm, grasping-mat lure)
- `ROT_HEALTH_SHARING_1` — Health-sharing comps: RM_CompWoundLink wound-splitting + RM_HediffComp_KinMending tend-aura, content-blind, tamed included
- `ROT_PALE_TREE_1` — The pale tree: Plant_TreeAnima reskin, psylink capped by a one-entry requiredSubplantCountPerPsylinkLevel list, RUT_PaleMoss subplants
- `DESERT_TRIBES_FIRE_HARVEST_1` — Scenario event: deep-desert tribes occasionally arrive in the Pyrelands to light the fires for harvesting (moved out of the dead FireEcology shim per 

## Commits

```
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
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: FREE    since 2026-09-18T02:07:41Z

Uncommitted (whose): everything below is ANOTHER SEAT'S mid-flight work
(codebase_health*/health.json = FOUNDRY health sync; fauna BiomeCast +
cast_assignment + SWBestiary Mlie-wave files = FOUNDRY's absorption passes;
artpipe json = the daemon's; defs.sqlite + deployed/config = untracked
tooling residue). BENCH's work is all committed and pushed.

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M design/Jawa/fauna/BiomeCast_Ashkarr.xml
 M design/Jawa/fauna/cast_assignment.csv
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml
 M src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_FrilledGorg.xml
 M src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml
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
?? src/RimStarWars/MSEDroidFix/validation.py
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Gelagrub.xml
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Gorg.xml
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Gornt.xml
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_GraniteSlug.xml
?? src/RimStarWars/SWBestiary/Textures/swanimals/Gelagrub/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Gorg/
?? src/RimStarWars/SWBestiary/Textures/swanimals/Gornt/
?? src/RimStarWars/SWBestiary/Textures/swanimals/GraniteSlug/
?? src/RimStarWars/SWBestiary/Textures/swresource/Leather_Reptomammal/
?? src/RimStarWars/SWBestiary/Textures/swresource/Meat_Gornt/
```

