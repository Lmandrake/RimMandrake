# BENCH_REBOOT_HANDOFF_202609261917 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609260650`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**A creature/def census on this project must read DESCRIPTIONS, never defNames — and a
sweep harness must be smoke-tested on ONE subject before you trust it with N.**

Both halves cost real credibility this session. The name-match half reported two of the
Grey Deep's three "unbuilt" anchor creatures as missing and that reached the owner before
the descriptions were read: the ossuary shrimp ships as `RM_Fessk`, the crusted giant as
`RM_Reefback`. Our naming convention is invented exotic words, so a name-matched census
reports a fully built roster as empty, every time.

The harness half: one smoke-test biome exposed FIVE bugs in the load-proof runner, four of
which produced confident wrong verdicts — the worst being a bridge check that
substring-matched the response payload and so read a FAILED call as `ABSENT`. Run blind
across 22 biomes it would have reported a total catastrophe that was entirely my bug.
🔑 The general form: **an instrument that cannot find something must first be proven able to
find something.** Every census this session that had a probe-and-control survived; every one
that did not was wrong.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **`PROPANELAKE_ANIMALDENSITY_ZERO_1` — six authored animals that can never spawn.**
   Both Propane Lake defs leave `animalDensity` unset, so it is `0f`, `AnimalEcosystemFull`
   is true from tick zero and nothing ever spawns. Proven from the decompiled
   `WildAnimalSpawner`. One field, but it silently blocks `SEA_FISHABLES_ALIVE_IN_DEPTHS_1`
   for that sea.
2. 🔴 **`LANTERNDEEPS_TIER_COLLISION_1` — a live mod exists ONLY in the game folder.**
   `mandrake.rut.lanterndeeps` is active in his 628-mod list with **no repo copy anywhere**,
   and its `RM_` successor deploys to the same folder name. An `--apply` would delete a mod
   the canonical save references. A disk failure loses it outright — true of nothing else
   we ship.
3. **The biome load-proof wave passed 22/22**, but the error counts vary wildly against a
   measured baseline of zero: Flooded Canyon **53 distinct errors**, Webwork 30, the Sump 14.
   Not load failures, so no verdict changed — filed as `BIOME_CONFIG_ERROR_TRIAGE_1`. He may
   want that prioritised.
4. **Two Grey Sea questions he has not answered**, both flagged rather than guessed: the
   Elder's "visible charge build-up" tell versus ban 4 (*"the only glow is the giant's
   mark"*), and whether the Brine Crown's retraction violates *"no plants that open and
   close"* — the thinnest of the five non-contradiction arguments.
5. **"Cripple nearby ships" is UNMEASURED.** Nobody has checked what an Elder discharge does
   to a gravship — and since the ship is now the only way in and out of a sea floor, a
   discharge that strands a party is a bigger deal than it reads.
6. FYI: **`AA_Aerofleet` was cut from the Grey Sea only.** The Twilight Sea and the Forge
   still cast it deliberately, and the def says so inline so nobody "fixes" them to match.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GREYSEA_FLOOR_PASS_1` — bedazzle sitting HELD and all 11 questions ruled; the drop is
  merged into the frozen sheet. Content is specced, nothing is built.
  NEXT: start `GREYSEA_FLOOR_FORMATIONS_1` (the pillars — every other Grey feature leans on them).
- `GREYSEA_ANCHOR_CREATURES_1` — scope shrank after correction: only the PILLAR-MASON is
  genuinely unbuilt, plus the `AA_Aerofleet` replacement.
  NEXT: scope the pillar-mason honestly as creature-vs-navigation-system before writing any def.
- `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` — filed, unstarted. Twilight Sea is 12 catches vs 6 floor animals.
  NEXT: author the Grey Sea's 7 catch-only species as floor animals from their existing item descriptions.
- `LANTERNDEEPS_TIER_COLLISION_1` — filed, unstarted, blocks the 23rd biome load-proof.
  NEXT: establish what the canonical save holds via PLACED THINGS, not a `.rws` grep for the biome defName.
- `BIOME_LOAD_PROOF_WAVE_1` — 22/22 PASS recorded and verified; NOT closed, because LanternDeeps is excluded.
  NEXT: close it once LanternDeeps migrates and its tier passes.
- `TECHPRINT_FACTION_GATING_1` — all 15 questions ruled, map written to `faction_tech_alignment.md`.
  NEXT: hand the manifest row assignment to FOUNDRY as the build step.
- `BIOME_DEFNAME_MIGRATION_WAVE_1` — labels renamed and committed; defNames still lag.
  NEXT: establish live tile counts for the 3 old defNames from the LIVE world, never the exported CSV.
- `SUUSH_CAULDRON_DRIFTER_1` — ticketed; art north/east rendered, south was still rendering.
  NEXT: look at the three facings and decide whether they are disturbing enough, or regen.
- `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` — filed from his ruling, no design done.
  NEXT: read both factions' roster dossiers before designing a single beat.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A ledger event's key is `id`, not `item` — a hand-rolled census reads 0 and looks like a finding (filed: CLAUDE.md, LESSONS_INBOX)
- A creature census on defNames reports built creatures as missing; read descriptions (filed: CLAUDE.md, LESSONS_INBOX)
- `jawa/get_defs` takes `defs` as a STRING `"DefType/DefName"`; a list returns `success:false`, and a payload-substring check reads that failure as ABSENT (filed: CLAUDE.md)
- `python.exe` emits CRLF, so a captured value is `"PRESENT\r"` and every shell compare fails (filed: CLAUDE.md)
- `grep -c` prints 0 AND exits 1, so `|| echo 0` emits two values (filed: CLAUDE.md)
- A `grep -F` check for a quoted phrase fails on LINE WRAPPING — it reported intact text as missing twice today (filed: CLAUDE.md)
- `rimbridge_client.py` cannot reach the bridge from WSL at all; bridge calls run under `python.exe` (filed: CLAUDE.md)
- `modset_builder.py --apply` refuses while `Player.log` is warm, so in a swap loop the kill must come first (filed: CLAUDE.md)
- `modset_builder`'s refusal message claimed the game rewrites ModsConfig on exit — false, corrected in place (see: commit 31a75423c)
- The repo's own `block_blind_scan` and `harvest_log.py` guards both fired correctly on my Player.log counts; one error can span 30 lines, so `grep -c` is an occurrence count (see: `measure count-errors`)

## Closed since the last handoff (1)

- `DROID_ORACLE_VOICE_DESIGN_1` — e9b3feec3

## Filed and still open (19) — the next seat's queue

- `GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1` — The greatbole's song, thermal sanctuary, pilgrims, and the two opt-in crossovers
- `WYYYSCHOKK_IDENTITY_COLLISION_1` — Decide fate of RSW_Wyyyschokk (MLIE_FAUNA_ABSORPTION_1's full port) now that RM_Ollathrix wears the Wyyyschokk skin (SHOKK_SKIN_SHRINK_1)
- `BIOME_LOAD_PROOF_WAVE_1` — Prove every biome mod loads clean standalone on a minimal list - the narrow donor-retirement sense of PROVEN, not full functionality
- `LANTERNDEEPS_TIER_COLLISION_1` — Live mandrake.rut.lanterndeeps exists ONLY in the game folder with no repo copy, and the RM successor deploys to the same folder name - deploying it w
- `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` — Nobody mass-produces droids on Ash'karr: the Hive holds latent factory tech it cannot use, the Enclaves need it badly - build the quest chain that con
- `BIOME_DEFNAME_MIGRATION_WAVE_1` — Three biomes renamed 2026-09-26 carry defNames that no longer match their labels: RM_NightsideIce/RM_PoisonForest/RM_Wasteland move to Sleeping Ice, C
- `PROPANELAKE_ANIMALDENSITY_ZERO_1` — RM_PropaneLake and RUT_PropaneLake leave animalDensity UNSET so it defaults to 0f - their 6-animal floor roster can never spawn, proven from the decom
- `GREYSEA_ANCHOR_CREATURES_1` — Grey Deep's two unbuilt anchors (pillar-mason, ossuary shrimp) plus the AA_Aerofleet replacement - the sheet's whole image rests on creatures that hav
- `SUUSH_CAULDRON_DRIFTER_1` — The Suush: a docile tamable floating sphere with gathering tentacles that feeds on the Cauldron's roiling chemistry and detonates when shot
- `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` — Every fishable in EVERY sea owes a living creature swimming the floor map, not just a catch item - owner ruling 2026-09-26
- `GREYSEA_SHORE_MUTATOR_SPECIFICS_1` — RM_SeaCoast is generic across all four seas - make the shore respect the Grey Sea's specifics, above all the crusted white salt shoreline the owner su
- `BIOME_CONFIG_ERROR_TRIAGE_1` — Triage the per-biome config errors the load-proof wave exposed against a zero baseline: floodedcanyon 53 distinct, webwork 30, thesump 14, contagion a
- `GREYSEA_FLOOR_FORMATIONS_1` — Grey Sea floor formations: salt chimneys venting super-brine, mushroom-like salt domes, and the pillar wonderland the sheet's navigation law depends o
- `GREYSEA_CRYSTAL_FLORA_1` — Grey Sea crystalline flora: seven owner-specced plants (Glass Veil Kelp, Brine Crown Anemoflora, Mosaic Fan Palms, Salt Chimney Vines, Crucible Pods, 
- `GREYSEA_SALT_SNOW_WEATHER_1` — Grey Sea floor weather: precipitating salt crystals like snow, plus the pre-existing defect that RM_GreySea carries vanilla Rain on a hypersaline dyin
- `GREYSEA_BRINE_POOL_DEFENCE_1` — Brine pools as the Grey's central mechanism: protein-shower crystallisation that freezes and may smother, triggered by touching a pool or by its creat
- `GREYSEA_BRINE_ELDERS_1` — The Brine Elders: colossal branching salt-crystal organisms with area discharges, geological memory, a novelty-only trade economy and one-of-each mill
- `GREYSEA_SALT_CUISINE_1` — Harvestable valuable sea-floor salt crystals in several colours as cooking ingredients - RimCuisine is NOT installed, so these ship RM_ with recipes M
- `GREYSEA_SESSILE_LAYER_1` — The Grey's sessile layer: abundant shrimp, clam and mussel equivalents picking through organic matter raining from the surface, among the formations

## Commits

```
38ced5c02 Merge the Grey Sea drop into the frozen sheet, additively, on the owner's word
5dbc67de7 CLAUDE.md: eight instruments from this session that returned confident wrong answers
79c37ccd4 Finish DROID_ORACLE_VOICE_DESIGN_1's close: commit the moved item's deletion
caa402fe2 Ledger: eleven Grey Sea bedazzle rulings
cafd07a83 Capture the Grey Sea content drop: 804 lines, 7 items filed
73760e4ab Diving is ship-only everywhere; biome load-proof wave passes 22/22
31a75423c Biome load-proof harness, plus a false claim fixed in modset_builder
31f3603bd Correct GREYSEA_ANCHOR_CREATURES_1: the ossuary shrimp is built as RM_Fessk
61e48fe17 File the Suush: a docile bomb that drifts through the Cauldron
bb1866d85 code review: mark-clean 4 files from the SUMP_MECHANICS_1 disarm-interaction pass
d91e092c4 rimflow: progress notes on SUMP_MECHANICS_1/SUMP_TAR_NASTINESS_1/SUMP_WALKWAYS_1
6714ad67c SUMP_MECHANICS_1: owner card 2 disarm interaction + bitumen/seepwax roster reconciliation
fc75fb00e Ledger sync: GREENTIDE_MECHANICS_2 verification + M10 hook note
195469bee GREENTIDE_MECHANICS_2: verification + M10 hook progress note
cd7014026 SCARLANDS_MECHANICS_2: document the grave-ward placement/faction continuation pass
94c815127 rimflow: SCARLANDS_MECHANICS_2 progress note (grave-ward placement/faction pass)
7ce57a71f MIASMA_MECHANICS_1: continuation pass notes — salinity Scribe fix, M2 setting, RC4 confirmed
fe5441820 Grey Sea sitting: cut the donor drifter, file the two unbuilt anchors
f12a1387e SCARLANDS_MECHANICS_2: place the Sentinel grave-ward and faction it
832ef0715 EnvironmentalHazards: rebuild the shared DLL to match committed source
... 131 more: git log --oneline 87fddb80a..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-26T19:11:22Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   auto-generated by the health publisher
 M Transient/codebase_health.json   auto-generated by the health publisher
 M Transient/codebase_health_artifact.html   auto-generated by the health publisher
 M Transient/project_maturity_dashboard.html   auto-generated by the maturity dashboard
 M Transient/project_maturity_dashboard.json   auto-generated by the maturity dashboard
 M deployed/config/ModsConfig.before-tier-bridge.xml   BENCH (this session) - modset_builder's own archive from the load-proof wave; harmless, the live list is restored to 628
 D infrastructure/artpipe/_artsrc/lockjaw_improve_a_r7/lockjaw_improve_a_r7.png   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/_artsrc/lockjaw_improve_b_r7/lockjaw_improve_b_r7.png   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/art_status.html   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/art_status.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brindeth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Brommet_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dorvel_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Dredgel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Gulveth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Korveth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Mirrelin_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Pallick_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skarrid_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skellarn_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Skelver_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Soffeth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_SumpMouse_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_ThrummelWarden_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Thrummel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Tolleth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/RM_Velloch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_crowncarpet_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/deepfire_pigmentjar_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_grank_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_horax_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_porg_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_strill_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_brathek_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_brathek_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_brathek_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_chellow_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_chellow_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_chellow_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_drommath_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_drommath_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_drommath_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_gorrameth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_gorrameth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_gorrameth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_grolth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_grolth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_grolth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_lommerel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_lommerel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_lommerel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_murrelith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_murrelith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_murrelith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_nemmel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_nemmel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_nemmel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_ollareth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_ollareth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_ollareth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_ammeth.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_cistrel.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_claithe.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_corvath.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_halquin.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_maulith.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_nubrith.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_plennith.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_seepril.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_skethral.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_skimmel.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_sodderel.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_thulvane.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_tullick.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_varnoth.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_verrow.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_plant_wanlith.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_silloch_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_silloch_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_silloch_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_skellick_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_skellick_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_skellick_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_thavrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_thavrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_thavrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_vaulm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_vaulm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/feverwood_vaulm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_animalpersonhood.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_blindsight.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_bloodfeeding.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_cannibal.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_collectivist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_darkness.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_femalesupremacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_fleshpurity.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_guilty.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_highlife.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_humanprimacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_individualist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_inhuman.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_loyalist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_malesupremacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_natureprimacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_nudism.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_painisvirtue.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_proselytizer.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_raider.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_rancher.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_ritualist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_shipborn.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_supremacist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_transhumanist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_treeconnection.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/glyph_tunneler.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_crossout.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_paste_flyer_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_paste_flyer_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_paste_wanted_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_paste_wanted_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_sigilframe_dripframe.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_sigilframe_halo.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_sigilframe_stencilbox.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_stencil_crown.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_stencil_fist.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_stencil_gear.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_a_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_a_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_b_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_b_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_c_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_tag_c_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_throwup_a_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_throwup_a_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_throwup_b_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/graffiti_throwup_b_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/miasma_ollamane.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_cundral_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_phorrik_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_quathis_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_sarnstilt_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_sarquin_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_thalquith_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_tumbel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_vurmeloth_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_wollick_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rm_zhorrel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmdusthusk_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmdusthusk_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmdusthusk_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmleachmoss_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmtitanoslime_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmtitanoslime_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmtitanoslime_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rmvenomvine_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brogg_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brogg_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brogg_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brullith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brullith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_brullith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_illoth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_illoth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_illoth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_skerrith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_skerrith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_skerrith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzikqueen_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzikqueen_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rot_thozzikqueen_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_graffiti_stencil_imperialcog.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_zakkro_dessicated_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_zakkro_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_zakkro_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_zakkro_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rsw_zakkroegg_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rswrawultracactus_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rswultracactus_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_grellbush.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_grellspine.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_vhessk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_vhessk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_vhessk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rut_wildhealroot.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutbloomcrop_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutbrinebattery_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutbrinebattery_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutbrinebattery_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutdarkcrust_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutdeltaloam_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutemperorvulture_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutfleetflier_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutfuzz_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutglower_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutglowercrust_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrathil_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutkarrobel_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutradiothermal_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutradiothermal_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutradiothermal_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutslimegrazer_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutslimegrazer_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutslimegrazer_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseed_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutstaggerseeddish_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutvwake_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutvwake_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutvwake_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutwelcomeblanket_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 D infrastructure/artpipe/pending/rutyearningfruit_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/registry.jsonl   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/artpipe/throughput.jsonl   artpipe daemon churn - runs continuously, never commit mid-flight
 M infrastructure/dashboards/hub/data/artsheets.json   auto-generated dashboard data
 M infrastructure/dashboards/hub/data/health.json   auto-generated dashboard data
 M infrastructure/dashboards/hub/data/maturity.json   auto-generated dashboard data
 M infrastructure/dashboards/hub/data/publish_ready.json   auto-generated dashboard data
 M infrastructure/state/codebase_health_last.json   auto-generated by the health publisher
 M infrastructure/state/ledger/events/OWNER.jsonl   the ./game tool - owner-stamped game-state events
 M infrastructure/state/queue/BENCH.md   a peer window or a tool
 M infrastructure/state/queue/FOUNDRY.md   a peer window or a tool
 M skills/rimworld-debug-testing/SKILL.md   a peer window - skills curation
 M skills/rimworld-sprite-facings/SKILL.md   a peer window - skills curation
 M src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll   FOUNDRY - build output from its live mechanics work
 M src/RimMandrake/Greentide/Assemblies/RimMandrake.Greentide.dll   FOUNDRY - build output from its live mechanics work
?? deployed/config/ModsConfig.before-tier-firehawk.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   unattributed - peer window or tool; BENCH did not touch it
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   unattributed - peer window or tool; BENCH did not touch it
?? infrastructure/artpipe/active/twilightsea_loohn_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/active/twilightsea_lunoowa_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/active/twilightsea_lunoowa_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Brindeth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Brindeth_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dorvel_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Dorvel_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Korveth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Korveth_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Mirrelin_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Mirrelin_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pallick_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Pallick_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skelver_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skelver_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Skennet_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soffeth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Soffeth_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tolleth_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Tolleth_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Velloch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Velloch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/RM_Vennick_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/cauldron_suush_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_kessik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_shekkur_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_thrizzik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_ulkhorr_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_vrakk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zekkra_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/crags_zhurrakor_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_brathek_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_chellow_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_chellow_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_drommath_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_drommath_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_drommath_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_drommath_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_gorrameth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_grolth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_lommerel_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_murrelith_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_nemmel_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_ollareth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ammeth.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ammeth.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_cistrel.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_cistrel.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_claithe.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_claithe.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_corvath.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_corvath.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_halquin.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_halquin.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_maulith.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_maulith.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_nubrith.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_nubrith.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_plennith.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_plennith.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_seepril.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_seepril.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_skethral.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_skethral.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_skimmel.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_skimmel.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_sodderel.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_sodderel.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_thulvane.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_thulvane.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_tullick.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_tullick.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_varnoth.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_varnoth.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_verrow.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_verrow.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_wanlith.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_plant_wanlith.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_silloch_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skellick_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thavrik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/feverwood_vaulm_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_animalpersonhood.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_animalpersonhood.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_blindsight.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_blindsight.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_cannibal.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_cannibal.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_collectivist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_collectivist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_darkness.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_darkness.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_fleshpurity.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_fleshpurity.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_guilty.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_guilty.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_highlife.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_highlife.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_humanprimacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_humanprimacy.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_inhuman.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_inhuman.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_loyalist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_loyalist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_malesupremacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_malesupremacy.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_natureprimacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_natureprimacy.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_nudism.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_nudism.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_painisvirtue.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_painisvirtue.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_proselytizer.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_proselytizer.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_raider.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_raider.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_rancher.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_rancher.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_ritualist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_ritualist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_shipborn.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_shipborn.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_supremacist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_supremacist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_transhumanist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_transhumanist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_treeconnection.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_treeconnection.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_tunneler.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/glyph_tunneler.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_crossout.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_crossout.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_flyer_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_flyer_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_flyer_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_flyer_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_wanted_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_wanted_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_wanted_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_paste_wanted_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_dripframe.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_dripframe.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_halo.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_halo.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_stencilbox.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_sigilframe_stencilbox.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_crown.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_crown.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_fist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_fist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_gear.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_stencil_gear.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_a_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_a_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_a_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_a_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_b_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_b_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_b_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_b_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_c_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_c_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_c_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_tag_c_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_a_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_a_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_a_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_a_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_b_p1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_b_p1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_b_p2.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/graffiti_throwup_b_p2.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_essarn_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_fessk_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_otheska_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_sorruth_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_sorruth_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_sorruth_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/greysea_sorruth_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/miasma_ollamane.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/miasma_ollamane.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_mahllik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/nightside_zhissa_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_heemin_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_hoolen_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_oovanam_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_phorrik_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_phorrik_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_quathis_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_quathis_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_sarnstilt_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_sarnstilt_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_sarquin_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_sarquin_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_thalquith_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_thalquith_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_tumbel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_tumbel_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_vurmeloth_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_vurmeloth_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_wollick_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_wollick_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_zhorrel_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rm_zhorrel_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmleachmoss_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmleachmoss_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmtitanoslime_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmvenomvine_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rmvenomvine_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brogg_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_brullith_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_illoth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_skerrith_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rot_thozzikqueen_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_graffiti_stencil_imperialcog.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_graffiti_stencil_imperialcog.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_dessicated_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_dessicated_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkro_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkroegg_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rsw_zakkroegg_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rswrawultracactus_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rswrawultracactus_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rswultracactus_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rswultracactus_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_grellbush.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_grellbush.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_grellspine.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_grellspine.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutyearningfruit_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/rutyearningfruit_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_dosscatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_eeshcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_karrashcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_muddalcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_saalcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_shullacatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_thuumcatch_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_ventbuilding_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckframe_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wreckhull_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_b.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_b.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_c.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald2_wrecktank_c.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_bezzul_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_greateroomb_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_greateroomb_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_greateroomb_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_greateroomb_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_hennul_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_mubbaro_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_oomb_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_thummorak_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_vohhm_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuppik_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_wuum_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/slime_yollum_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/twilightsea_loohn_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/done/twilightsea_loohn_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Brommet_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Cravvet_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Dredgel_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Gulveth_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Quarrok_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skarrid_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skellarn_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Skennet_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_SumpMouse_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/RM_Thrummel_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/crags_thrizzik_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/crags_thrizzik_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_pikobis_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/desertportb_pikobis_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_chellow_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_chellow_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_chellow_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_chellow_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_drommath_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/feverwood_drommath_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_bloodfeeding.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_bloodfeeding.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_femalesupremacy.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_femalesupremacy.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_individualist.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/glyph_individualist.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/greysea_sorruth_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/greysea_sorruth_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmdusthusk_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rmmirrorgiant_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rut_vhessk_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutbrinebattery_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutfleetflier_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutglowercrust_v1.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutglowercrust_v1.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrathil_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutkarrobel_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutmortuarycrawler_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutradiothermal_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutslimegrazer_v2_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/rutvwake_v1_south.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/scald2_shullacatch_a.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/scald2_shullacatch_a.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/slime_greateroomb_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/slime_greateroomb_north.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/twilightsea_loohn_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/failed/twilightsea_loohn_v1_east.manifest.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_body_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_atlas.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_carapacewall_menuicon.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/rut_greentideant_dessicated_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_lunoowa_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_noolim_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_east.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_north.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/artpipe/pending/twilightsea_weloon_v1_south.json   artpipe daemon churn - runs continuously, never commit mid-flight
?? infrastructure/dashboards/hub/tabs/maturity.html   auto-generated dashboard data
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   auto-generated dashboard data
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   a peer window or a tool
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   mod-list snapshots - several seats; the BIOME_LOAD_PROOF one is BENCH this session
?? src/RimMandrake/Utils/firehawk_flight_probe.py   FOUNDRY - its in-flight content work
```

