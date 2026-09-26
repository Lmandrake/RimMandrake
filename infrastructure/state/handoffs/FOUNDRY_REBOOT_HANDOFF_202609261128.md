# FOUNDRY_REBOOT_HANDOFF_202609261128 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609260052`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
This was a single sustained "full belt" wave, holding 3-4 concurrent Sonnet agents for
~10 hours straight (owner said "wake foundry and full belt", one message, no further
input needed): 67 items closed, ~14 of them RM_MOD_BUILD Phase-A biome splits (roughly
half of THOSE turned out already fully built — the "check first, half these items are
already done" pattern from prior sessions held again, hard). The floor holds at this
scale IF concurrent agents are spread across DIFFERENT mods — every real collision this
wave (all recovered cleanly) happened when 2+ agents landed content in the SAME biome's
shared csproj/DLL at once (FeverWood/Webwork/Greentide). Next wave: bias dispatch toward
distinct mods when 3+ agents are in flight, not just distinct items.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Two LOOKING decisions are staged and ready, canonical save confirmed byte-unchanged
  (SHA-256) both times, nothing written to it: `WORLD_LABEL_SIZE_HIERARCHY_1` (a sizing
  curve applied to a new slot, one whole-planet review picture,
  `Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.png`)
  and `FEATURE_DRAWCENTER_UNVERIFIED_1` (52 of 63 single-piece features had a genuinely
  wrong drawCenter, fixed to a slot built ON TOP of the sizing one so both show together;
  8 multi-piece regions' three candidate placements each rendered for him to pick by
  looking, `Transient/world_drawcenter_audit/`). Both items sit `doing`/`needs=owner`.
- `WYYYSCHOKK_IDENTITY_COLLISION_1` (new, filed this wave): two mechanically unrelated
  creatures now both carry the "Wyyyschokk" canon label — `RSW_Wyyyschokk` (a full
  standalone port from `MLIE_FAUNA_ABSORPTION_1`, 2026-09-18) and `RM_Ollathrix` wearing
  a Wyyyschokk skin patch (`SHOKK_SKIN_SHRINK_1`, this wave). Neither was touched pending
  his call on which identity wins.
- `STONEBACK_BOKKA_ART_STANDARD_1`: the bokka's regen jobs failed the artpipe validator
  TWICE on 2026-09-23 (quota-abort both times, no output ever produced) and are still
  sitting `pending`, well back in a 400+ job queue. The verdict (wrong animal depicted,
  regen needed) stands; there is simply nothing new to look at yet.
- Several `_TUNING_1`/`_TUNING` items were deliberately left with flagged placeholder
  numbers rather than guessed real ones, per this wave's own established discipline —
  see "Filed and still open" below for the full list (Tentacle set-piece, Dianoga tank,
  Sap-sucker mishandling trigger, Two-front lure numbers). None were closed on a guess.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FEATURE_DRAWCENTER_UNVERIFIED_1` — doing, needs=owner; NEXT: owner looks at `Transient/world_drawcenter_audit/drawcenter_overview.png` + the 8 multi-piece panels and rules on (a) approve the 52 single-piece fixes and (b) pick a placement style per multi-piece region, then FOUNDRY writes the approved slot to canonical.
- `GREENTIDE_HUMMING_GROVE_1` — blocked, needs=deploy; NEXT: next shutdown-window deploy, redeploy `RimMandrake.CreatureBehaviors.dll` (carries `RM_ProximitySoundscapeExtension`), then a joint listening session with the owner in the Thalquith grove before claiming it works — his own `## verify` section requires hearing it, not just a def dump passing.
- `STONEBACK_BOKKA_ART_STANDARD_1` — doing; NEXT: check `infrastructure/artpipe/pending/RSW_Stoneback_{south,east,north}.json` again (queue position, or whether the daemon has finally cleared its quota backlog past them) — do not requeue, do not re-verdict, just check if they've rendered yet and if so build the old-vs-new comparison this item's own checklist still owes.
- `WORLD_LABEL_SIZE_HIERARCHY_1` — doing, needs=owner; NEXT: owner looks at `Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.png`, rules whether the curve reads right, then FOUNDRY writes `ASHKARR_LABELSIZES_2026-09-26.rws`'s sizing to canonical on his word.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `BiomeDef.movementDifficulty` is world-tile-only, not in-map pathfinder cost — two design docs had assumed it stacked with in-map `pathCost` (filed: LESSONS_INBOX).
- A `Plant` ThingDef cannot block line of sight at any `fillPercent` — only Buildings reach the edifice grid `GenSight` checks (filed: LESSONS_INBOX).
- Vanilla `GasType` is a fixed 4-value enum and `TraderKindDef.PriceTypeFor` has no player-sell price-premium lever — both kill a pure-XML design without a Harmony hook (filed: LESSONS_INBOX).
- A content "move" (copy new + delete old) that only commits the new half leaves the old path deleted-on-disk-but-tracked, silently, for hours — caught and fixed twice at handoff time this wave (BlueDesert's UtinniPatches originals, Sump's mouse placeholder); `git status` the old path after every claimed move (filed: LESSONS_INBOX).
- `DLL_SOURCE_STAMP_GUARD_1` refusing YOUR push is often actually a DIFFERENT concurrent agent's half-finished commit on the shared tree — rebuild and re-stage before assuming your own change is broken (filed: LESSONS_INBOX).
- Concurrent agents building different content into the SAME biome mod's shared csproj/DLL collide repeatedly and need git-plumbing recovery every time — spread concurrent dispatch across mods, not just across items (filed: LESSONS_INBOX).

## Closed since the last handoff (67)

- `NIGHTSIDEICE_RM_MOD_BUILD_1` — ada959c90941d977c308b0b9f649d123921d2203
- `WATERTRUCE_CTOR_BIOME_READ_1` — aaa808b16bcb334343ea67fa2ad658343e492405
- `BLUEDESERT_RM_MOD_BUILD_1` — 979d69dc1
- `POISONFOREST_RM_MOD_BUILD_1` — dcc620586
- `FLOWWORKS_DONOR_AFFORDANCE_GAP_1` — c3bbfff0bab894c42d41ff5acba6e310a778fbb0
- `MIASMA_FEVERWOOD_GREENTIDE_BMT_1` — 264e468cfc8ecfc8994a4aea3fdf309b70b07a19
- `PYRELANDS_RM_MOD_BUILD_1` — d8dbcd276
- `THEFORGE_RM_MOD_BUILD_1` — 86ddebac777b3bfec334afe1cb3bfece69f99cee
- `CONTAGION_RM_MOD_BUILD_1` — 33db46fed32bcca65f446f4da4294b4b06b73127
- `MIASMA_RM_MOD_BUILD_1` — 2438d54586a6191a74a6d71270b3fef02694f67d
- `GELATINOUSSLIME_RM_MOD_BUILD_1` — 64042a910546212a6c623ce7e9598c74a3db1d2c
- `LANTERNDEEPS_RM_MOD_BUILD_1` — 7d0642655a48729087ef8d8388ee00802d823820
- `FEVERWOOD_RM_MOD_BUILD_1` — 1986e8e69
- `RUSTCATHEDRAL_RM_MOD_BUILD_1` — d4951cbe0
- `TERMINALBIOMES_RM_MOD_BUILD_1` — aa9ef0947
- `THESUMP_RM_MOD_BUILD_1` — 533ade837
- `SCARLANDS_STANDALONE_MOD_1` — f8a6096dd
- `WEBWORK_RM_MOD_BUILD_1` — c1362979d
- `SW_FAUNA_NEVER_IN_RM_TIER_1` — 921715e03
- `SUMP_FLORA_ROSTER_1` — d5c593255
- `FEVERWOOD_FLORA_ROSTER_1` — d37e5bb44
- `MIASMA_FLORA_ROSTER_1` — de937a7e7492054b26f6ecaec1a57601859ea2e8
- `WEBWORK_FLORA_ROSTER_1` — 3b4f86a17bcf4000295e03f55e360c1980223992
- `SUMP_FAUNA_ROSTER_1` — 656ab93f012f3b34aa1092dc9f4e7d8590ca4b97
- `MIASMA_FAUNA_FLOOR_ROSTER_1` — db372f55a07fdbbb25481e30055dca6ce0676aa5
- `MLIE_ABSORPTION_BIOME_WIRING_1` — 3abed6f36
- `WEBWORK_FAUNA_ROSTER_1` — 065360d74b41a36f248c1a2364e4e9b257c34e97
- `UTINNIPATCHES_LOAD_ORDER_CYCLE_1` — 3130ef31229e2cdfe0783fa53bbf4daf8efd352e
- `FEVERWOOD_TENTACLE_BESTIARY_1` — 8ffcbfb88
- `SEA_DIVE_MAPS_BUILD_1` — 44a44438c1ee09eb24491e1e9509216b0146d044
- `FEVERWOOD_DIANOGA_PRISON_1` — 6318074f5
- `SEA_BEASTS_TIER_RULING_1` — 099966fd1b921fd183e6b613ee21f7725ae2ffb0
- `GREATBOLE_HARVEST_LADDER_1` — 018801d35ef98a79282fb4c18c9fb7782d8e931c
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — 2a423c59cb66fdb6953b5039809bfb5774160523
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — ba560a36c9bf559fb4c944570bd3530d93fcace6
- `CONTAGION_GENOME_ORGAN_GROWING_1` — 992215f6b
- `WARDEN_MOTHER_BEFRIENDING_1` — b835cf956
- `FEVERWOOD_TWO_FRONT_LURE_1` — f9477b98b
- `FURNACEBEAST_WORLD_MIGRATION_1` — 8a8e05414ec3137902b675be49ef8c0bd8c96da3
- `DEEPFIRE_PIGMENT_MOD_1` — 8052842e763eda33b6cfc0f54d29814205cb1363
- `OLLATHRIX_OWNER_SPECIES_1` — 709c58754
- `WEBWORK_SOUNDSCAPE_1` — 16f7b8d1f28ea3c4248cbaac2faaa31618c9772b
- `WEBWORK_WEB_STRUCTURES_1` — 624f11ade4e7953cc40a10869d79d8433e992b30
- `SUMP_TAR_BELCH_EVENT_1` — d602fdf21a6db48705e50519ee4f9d860001a1e4
- `BIOME_ARRIVAL_NARRATION_1` — b6feb2490e6eafbf12761833429ed9264eee463f
- `SHOKK_SKIN_SHRINK_1` — 6d79b7b63
- `SUMP_TAR_VAULT_1` — b662ca89e8b4f9e4284897146f6a5cbced9295a9
- `CONTAGION_UNFINISHED_SPAWNER_1` — 5b0a16d491a774a02648e208ffca7f7d4b841845
- `WEBWORK_EGG_BLACKMARKET_BUILD_1` — 0dbff530f
- `WEBWORK_NEST_EGG_ECONOMY_1` — 579d32bc46a3d55def9d9aaa6fc75f206e4a6a2a
- `SUMP_UTINNI_LAYER_1` — 2dc431e5760cb3be3f49466172b71b94999cdc9a
- `SUMP_TAR_HYDROLOGY_1` — f51298908
- `DEEPFIRE_PAINT_STATUS_CUISINE_1` — 9876847c4
- `WEBWORK_EGG_RECKONING_QUEST_1` — 720fc2e5a
- `GREENTIDE_EXOTIC_JUNGLE_FISH_1` — fd2244219
- `GREENTIDE_RM_MOD_BUILD_1` — 4f9e42387d10f93fabe7db8b9f8d87f6c05581e1
- `GREENTIDE_JUNGLE_TREE_ROSTER_1` — f521c0c7939e1b21cbd1a83ce72d457f1fcdc3c2
- `GREENTIDE_BIOME_DENSITY_1` — 7427b8aedc0775da7e80e62acf2a3f24a1055e0e
- `GREENTIDE_RISK_REWARD_EXCHANGE_1` — 3e35adc86
- `GREENTIDE_YEARNING_FRUIT_1` — fddbdee0a
- `GREENTIDE_FRENZY_DISEASE_1` — 35ac3ab3f871cd21d0dd15f611a64535ede637ca
- `GREENTIDE_GRENADE_WEAPONS_1` — 709e1b57e687da9595861fbed0b45d24352ca703
- `CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1` — f7436c156690264d89e71f97c65bcaa47114124a
- `GREENTIDE_UNDERSTORY_PLANT_ROSTER_1` — 6ba656f0f
- `GREENTIDE_WASP_SWARM_1` — a29cc8bef69114647f85f09619b62220980063f6
- `GREENTIDE_DENSITY_SETTINGS_1` — 6e6a209ba04e7e836f17c392d7c88eb828358714
- `WARDEN_MOTHER_SUCCESSION_1` — 300df605f541bce41768a2297edcd4eb13ef5dbb

## Filed and still open (16) — the next seat's queue

- `MIASMA_SCUTTLER_PREDATION_1` — Wire the five carnivorous plants to actually eat the arthropod-floor scuttlers
- `FEVERWOOD_TENTACLE_SETPIECE_TUNING_1` — The eye set-piece's frequency and the poison/radioactive suppression route
- `FEVERWOOD_DIANOGA_TANK_TUNING_1` — Sekkulaath prison tank — real numbers, not placeholders
- `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1` — The greatbole's song, thermal sanctuary, pilgrims, and the two opt-in crossovers
- `FEVERWOOD_SAP_SUCKER_TUNING_1` — Real numbers and the mishandling trigger for the sap-sucker guild
- `WARDEN_MOTHER_PATHFINDER_VERIFY_1` — Live-verify the warden mother's water-only movement and load cleanly
- `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` — Two-front lure numbers, prey-quality gate, and a free-tier second raider
- `WYYYSCHOKK_IDENTITY_COLLISION_1` — Decide fate of RSW_Wyyyschokk (MLIE_FAUNA_ABSORPTION_1's full port) now that RM_Ollathrix wears the Wyyyschokk skin (SHOKK_SKIN_SHRINK_1)
- `WEBWORK_EGG_BROKER_CHANNEL_1` — Add the egg black-market broker channel as a Bazaar tab, once Bazaar has tabs
- `DEEPFIRE_PAINT_LIVE_VERIFY_1` — Deepfire painting + worn-glow darkness tradeoff (needs live bridge)
- `SUMP_TAR_FIRE_NETWORK_1` — Network fire with gate firebreaks; wire belch to glass-cooling
- `SUMP_TAR_LIVING_SYSTEMS_1` — Living-map responders; tar rain mod-vs-scenario split
- `GREENTIDE_FEVER_SPECIALISTS_1` — Survivors become specialists: Greentide fevers as a qualification, not just attrition
- `GREENTIDE_CANOPY_SWARM_1` — The Greentide's insect axis: a new canopy-hazard swarm, driving the Gnawer/Shatterer tree-fall mechanics
- `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1` — Make a Plant actually block line of sight (Harmony/comp), the owner's sight-blocking ruling has no def-only answer
- `WARDEN_MOTHER_TRAINABLE_GATE_1` — Hard-exclude Rescue/general Haul from a self-tamed warden young's training tab

## Commits

```
25f0d0244 LESSONS_INBOX: 8 durable findings from the 2026-09-26 FOUNDRY full-belt wave
6b256b264 Finish SUMP_FAUNA_ROSTER_1's cleanup: commit deletion of retired SumpMouse placeholder
b9da6ff93 Finish BLUEDESERT_RM_MOD_BUILD_1's move: commit deletion of superseded UtinniPatches files
6ea7ff569 Ledger: close WARDEN_MOTHER_SUCCESSION_1 at 300df605f
300df605f WARDEN_MOTHER_SUCCESSION_1: self-taming, water-scoped training backstop, succession
985c1a56f Ledger: close GREENTIDE_DENSITY_SETTINGS_1 at 6e6a209ba
6e6a209ba Greentide: Mod Settings sliders for plantDensity/movementDifficulty
6f54801e7 Ledger: FOUNDRY shard sync, GREENTIDE_UNDERSTORY_PLANT_ROSTER_1 close event
9a9c78c09 Ledger: close GREENTIDE_WASP_SWARM_1 at a29cc8bef
035e73df5 Ledger: close GREENTIDE_UNDERSTORY_PLANT_ROSTER_1 at 6ba656f0f
6ba656f0f Greentide: seven invented understory plants, brakkel replaces foraged berries
c274aaf68 Ledger: close CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1 at f7436c156
f7436c156 Contagion: grown limbs and an install-match bonus for the amoeba organ mechanic
451ccfdbe Ledger: close GREENTIDE_GRENADE_WEAPONS_1 at 709e1b57e
709e1b57e Greentide: stench smoke grenade, the jungle's first grenade weapon
24d422f0f Ledger: close GREENTIDE_FRENZY_DISEASE_1 at 35ac3ab3f
35ac3ab3f GREENTIDE_FRENZY_DISEASE_1: author "the Frenzy", the biome's first disease
4a75306b1 Ledger: close GREENTIDE_YEARNING_FRUIT_1 at fddbdee0a
fddbdee0a GREENTIDE_YEARNING_FRUIT_1: wire RUT_YearningFruit into RM_Greentide's wildPlants
532f36261 selftest_sound_paths: allow-list the three Obelisk clips GREENTIDE_HUMMING_GROVE_1 reuses
... 195 more: git log --oneline 141e9e40c..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-26T05:57:19Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient dashboard auto-regen; not this window's
 M Transient/codebase_health.json   ambient dashboard auto-regen; not this window's
 M Transient/codebase_health_artifact.html   ambient dashboard auto-regen; not this window's
 M Transient/project_maturity_dashboard.html   ambient dashboard auto-regen; not this window's
 M Transient/project_maturity_dashboard.json   ambient dashboard auto-regen; not this window's
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/art_status.html   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/art_status.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brindeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dorvel_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Korveth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Mirrelin_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Pallick_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skelver_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Soffeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Tolleth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Velloch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_crowncarpet_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_crowncarpet_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_pigmentjar_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_pigmentjar_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ollamane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/registry.jsonl   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/throughput.jsonl   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/dashboards/hub/data/artsheets.json   ambient dashboard auto-regen; not this window's
 M infrastructure/dashboards/hub/data/health.json   ambient dashboard auto-regen; not this window's
 M infrastructure/dashboards/hub/data/maturity.json   ambient dashboard auto-regen; not this window's
 M infrastructure/dashboards/hub/data/publish_ready.json   ambient dashboard auto-regen; not this window's
 M infrastructure/state/codebase_health_last.json   ambient dashboard auto-regen; not this window's
 M skills/rimworld-debug-testing/SKILL.md   unclear provenance -- not touched by this wave's agents; flag for the skill-curation pass
 M skills/rimworld-sprite-facings/SKILL.md   unclear provenance -- not touched by this wave's agents; flag for the skill-curation pass
?? deployed/config/ModsConfig.before-tier-firehawk.xml   pre-existing backup/snapshot file, predates this window; not this window's
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   pre-existing backup/snapshot file, predates this window; not this window's
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   pre-existing backup/snapshot file, predates this window; not this window's
?? infrastructure/artpipe/active/desertportb_uvak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brindeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brindeth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dorvel_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dorvel_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Korveth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Korveth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Mirrelin_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Mirrelin_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Pallick_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Pallick_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skelver_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skelver_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Soffeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Soffeth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Tolleth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Tolleth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Velloch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Velloch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ollamane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ollamane.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Brommet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Gulveth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Quarrok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_kessik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_thrizzik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_thrizzik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_pikobis_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_pikobis_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/scald2_shullacatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/scald2_shullacatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_essarn_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_fessk_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_otheska_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/greysea_sorruth_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_mahllik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/nightside_zhissa_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_heemin_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_hoolen_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_oovanam_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/propanelake_vaunoom_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_bezzul_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_greateroomb_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_hennul_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_mubbaro_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_oomb_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_thummorak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_vohhm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuppik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_wuum_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/slime_yollum_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_loohn_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/dashboards/hub/tabs/maturity.html   ambient dashboard auto-regen; not this window's
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   ambient dashboard auto-regen; not this window's
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing backup/snapshot file, predates this window -- not this window's
?? src/RimMandrake/Utils/firehawk_flight_probe.py   another live FOUNDRY window's in-progress work (FIREHAWK_FLIGHT_BEHAVIOR_1 state-read tool); not this window's
```

