# FOUNDRY_REBOOT_HANDOFF_202609280425 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609272103`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A single wrong enum literal (`<purpose>None</purpose>` — `PlantPurpose` has no
`None` member, only `Food/Health/Beauty/Misc`) was silently discarding whole
`ThingDef`s during parse, which is why `FEVERWOOD_PLANT_DANGLING_REFS_1`'s 15
"present in source but missing at load" plants were a genuine mystery rather
than a deploy-drift/MayRequire/mod-inactive story — none of those fit because
none of them were it. Same root-cause shape as CLAUDE.md's `MayRequire`-on-
`<Operation>` trap: a field that silently no-ops or throws mid-parse can take
a whole def with it, and "present in source, deployed, mod active" is not
proof a def loaded. Also found (grep, comment-aware to avoid matching the
string inside XML comments) the same misplaced-field family: `<butcherProducts>`
nested inside `<race>` instead of as a ThingDef-level sibling in 3 files
(BlueDesert ×3, TheSump ×5) — `butcherProducts` is `Verse.ThingDef`'s field,
not `RaceProperties`'s, so it was silently ignored rather than erroring,
which is why it survived unnoticed. Worth a `grep -rn "<butcherProducts>"
src --include=*.xml` sweep for any race-nested occurrence outside what this
pass already fixed.

## What the owner should see

- **Three items are all gated on the same one decision: may the canonical
  save be resaved now?** `LANTERNDEEPS_TIER_COLLISION_1`, `CRYPTOFORGE_
  HARVEST_RETIRE_1` and `BIOME_DEFNAME_MIGRATION_WAVE_1` are all blocked
  on it (the last one needs a live `world_stats` read, which needs the
  canonical save loaded, which needs the resave). The mod-list side of the
  first two is already cold-load-verified clean this session — nothing
  left to prove there, just waiting on the word to actually resave
  `CANONICAL_ASHKARR_START_2026-09-12.rws`.
- **The Twilight Compact tenancy-paper removal is fully executed in code**
  per your 2026-09-27 ruling ("The Compact does NOT sell light... Remove"):
  the two lease/forecast papers and the claim-buoy building are deleted,
  the poaching-standing tracker is gone, the sun-sphere is research + wild
  seed only now. Builds clean. Not yet deployed or cold-load-verified — the
  game was up for this whole pass — that's the very next FOUNDRY move.
- A subagent I forked to do this same Twilight work first spent 336k tokens
  and returned having done literally nothing (0 tool calls) while claiming
  it had "forked off" the work elsewhere, which it hadn't. Filed as Claude
  Code product feedback (not a project item); redone directly by hand
  instead — see this handoff's commits for what actually landed.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `MIASMA_SHIPPING_NAMES_1` — stale `doing` from a prior window, not touched this session (filed 2026-09-25, `needs owner`); NEXT: put the three working names (karrobel, karrathil, stranded deformation) in front of the owner for a ruling, or close it if he already ruled on them elsewhere and nobody recorded it.
- `TWILIGHT_REVIEW_FIXES_1` — all 14 findings fixed at `3e6a74b87`, builds clean, NOT deployed/cold-load-verified (game was up all pass); NEXT: `deploy_custom_mods.py --mod TerminalBiomes --apply`, cold-load, re-review the touched files whole and mark-clean, close against `3e6a74b87`.
- `TWILIGHT_TENANCY_PAPER_REMOVAL_1` — done at `3e6a74b87` (same commit, same assembly), same not-yet-deployed state; NEXT: same deploy+cold-load as above, then confirm zero log lines for the deleted RM_SkylightRight/RM_WellChart/RM_ClaimBuoy classes/defs before closing.

## Traps learned

- 🔴 `<purpose>None</purpose>` is invalid (`PlantPurpose` has no `None`
  member) and silently discards the WHOLE `ThingDef` at parse time, not just
  that field — the same class as `<butcherProducts>` misplaced inside
  `<race>` (silently ignored, a `Verse.ThingDef` field applied where
  `RaceProperties` was expected) (filed: LESSONS_INBOX).
- A `fork` subagent given a large-but-fully-specified task can, instead of
  executing it, produce a text-only response CLAIMING it delegated the work
  further — with `tool_uses: 0`, i.e. it did nothing and the claim was false
  (see: this session's SendFeedback draft; verify a fork's claimed actions
  against `git status`/task list before trusting a "done" report).
- `Plant` never overrides `Tick()`, only `TickLong()` — re-confirmed live
  this pass (`RM_Comp_VaeuliskLure`'s reveal check never fired because it
  was on `CompTick`) (see: CLAUDE.md's plant-ticker law).

## Closed since the last handoff (8)

- `DEBUG_GAME_READY_WORLDUI_CRASH_1` — 91bcd0a6d
- `LOAD_GAME_READY_MAPGEN_CRASH_1` — de45ea47e
- `GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1` — 974afecd047a1200fa80e2a8aa0627a96e2266bc
- `MIASMA_SCUTTLER_PREDATION_1` — 974afecd047a1200fa80e2a8aa0627a96e2266bc
- `DESERT_GLITTER_BIRDS_COMMENSALS_1` — 04242cb8f
- `DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1` — eecf7d496
- `FEVERWOOD_PLANT_DANGLING_REFS_1` — d084d2abe
- `BLUEDESERT_JOIN_FULL_LIST_1` — d084d2abe

## Filed and still open (13) — the next seat's queue

- `CHILL_RIME_TERRACES_1` — Floor terrain: sparkling ice bedrock + Krellik rime-terrace districts
- `CHILL_THERMAL_FOOTPRINTS_1` — Thermal footprints: warmth writes refrozen glossy trails the defense can read
- `CHILL_AURORA_SURGE_1` — Aurora surge storms: harvestable floor weather with shock risk
- `DEEP_SAND_WALKABLE_TERRAIN_1` — Deep sand: walkable-very-slow, a whole terrain type (some Long Shade, much Stillsand) - owner ruling 2026-09-27 supersedes the impassable spec
- `LONGSHADE_RULED_CONTENT_1` — Build the Long Shade content ruled 2026-09-27: 14-row tier move + Gloomcast, RM_Ultracactus + pad forage, roster cuts, Dewback in slowed, dewfringe - 
- `STILLSAND_RULED_CONTENT_1` — Build the Stillsand content ruled 2026-09-27: nine-row tier move, oommok/siidda names, vekka kept, size fixes, dunes-engine wiring - fill-out/qorrax d
- `SANDBUSTER_CASTES_BUILD_1` — Sand busters: ruukka eruptor + oorrik swarm + mound + biome-gated eruption incident - the ruled 2026-09-24 amendment finally filed, Stillsand marquee 
- `DESERT_CAVERN_BEAST_EGGS_1` — Deep-desert cave-beast + prized eggs-as-water: the successor EXTREME_DESERT_CAVERN_BEAST_1's closure promised and never filed
- `PYRELANDS_DEDICATED_GRAZER_1` — Author a dedicated pure-grazer burrower for the Pyrelands' 'burrowers' family, distinct from Orray
- `TWILIGHT_REVIEW_FIXES_1` — Fix the 14 Twilight-wave code-review findings: 4 ship-blockers (plant CompTick lure, Never-ticker cargo float, undersurge on every biome, unstandable 
- `GREYSEA_RULED_CONTENT_1` — Build the Grey Sea content ruled 2026-09-27: ten understorey flora at 0.22, catch rebalanced rare, crust clock + weather/berth multipliers, determinis
- `BAROQUE_BIOMES_COMPOSE_1` — Wave 1 of the Baroque Biomes merge: build the compose verb in deploy_custom_mods.py (manifest of 29 IN mods per spec section 8 rulings, generated Abou
- `TERMINALBIOMES_LIQUID_RETARGET_1` — Retarget TerminalBiomes' generic liquid terrain rows (boiling water, brine pool, liquid propane) onto FlowWorks' defs per the Q7 ownership ruling 2026

## Commits

```
67d22cb00 rimflow: progress notes on TWILIGHT items; game-up stamp
3e6a74b87 TWILIGHT_TENANCY_PAPER_REMOVAL_1 + TWILIGHT_REVIEW_FIXES_1: retire the Compact tenancy layer, fix all 14 review findings, capture corrected 630-mod FULL list
f04561bbd Unification 8/8 ruled (Baroque Biomes); pool sentinel named orruhmu, unblocked
008fe34e7 rimflow: refresh BIOME_DEFNAME_MIGRATION_WAVE_1's blocked reason
07da46b07 rimflow: close FEVERWOOD_PLANT_DANGLING_REFS_1, BLUEDESERT_JOIN_FULL_LIST_1 (d084d2abe)
d084d2abe FEVERWOOD_PLANT_DANGLING_REFS_1: fix invalid PlantPurpose, join BlueDesert to full list
006f3181d Grey Deep pool sentinel design (GREYSEA_RULED_CONTENT_1 unblock)
81cb33992 Biome mod unification spec: roster, packaging, collisions, card agenda (BIOME_MOD_UNIFICATION_1)
cf056110d FOUNDRY handoff: Cryptoforge/LanternDeeps fixes staged, load in flight
45323ce13 Grey Sea sitting complete: all 17 agenda questions ruled, build item filed
5dfbd97b6 Lessons: LanternDeeps ModsConfig-vs-About.xml drift, stale-DLL-fresh-srchash trap
17007f2ad rimflow: bridge release before handoff
bd07940c9 ModsConfig backup before LanternDeeps/RotSporeKit fix
12f180372 Correct false "reverted" claim in LANTERNDEEPS_TIER_COLLISION_1
a5e38b38a Desert fill-out art: fix facing-contradicted prompts, requeue 39 jobs
29fe08b1b Grey Deep sitting agenda: merged proposal + card agenda (GREYSEA_FLOOR_PASS_1)
06ad23d6a File FEVERWOOD_PLANT_DANGLING_REFS_1: 15 plant dangling refs, cause UNMEASURED
a3ae11de2 Q17 ruled: biome mods merge NOW into one RimMandrake.Biomes mod (per-biome toggles)
8cab1d89a rimflow: close DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1 (corrected sha), note BLUEDESERT/wake-restart
201896a5e DUNESEA_SHADE_COMMENSAL_MICROFAUNA_1: RM_ShadeMite, third shade-follow consumer
... 44 more: git log --oneline a5a49c0d7..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-28T04:05:23Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient -- health-publisher daemon, continuously running, predates and outlives this session
 M Transient/codebase_health.json   ambient -- health-publisher daemon, continuously running, predates and outlives this session
 M Transient/codebase_health_artifact.html   ambient -- health-publisher daemon, continuously running, predates and outlives this session
 M design/Jawa/worldbuilding/biomes/desert.md   BENCH's concurrent activity this session, not mine
 M design/Jawa/worldbuilding/biomes/rosters/desert.json   BENCH's concurrent activity this session, not mine
 M infrastructure/artpipe/daemon_run_20260927_derivefacings.log   ambient -- artpipe daemon, continuously running, predates and outlives this session
 M infrastructure/artpipe/registry.jsonl   ambient -- artpipe daemon, continuously running, predates and outlives this session
 M infrastructure/artpipe/throughput.jsonl   ambient -- artpipe daemon, continuously running, predates and outlives this session
 M infrastructure/dashboards/hub/data/health.json   ambient -- health-publisher daemon, continuously running, predates and outlives this session
 M infrastructure/state/codebase_health_last.json   ambient -- health-publisher daemon, continuously running, predates and outlives this session
?? deployed/config/ModsConfig.before-tier-firehawk.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   pre-existing -- modset_builder tier-proof backups, predate this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Dakkra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Gennok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Pirrik_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Qorrax_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Sollak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/_withdrawn/RM_Tebbra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/active/RM_Veessa_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dakkra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dewfringe.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Dewfringe.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Duumma_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gaanok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Gennok_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Glasscrust.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Glasscrust.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Hourbloom.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Hourbloom.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_KneelOllim.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Liikka_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Loomma_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Orruhmu_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Pirrik_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Qorrax_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Sollak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Soorrak_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Tebbra_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_UltracactusPad.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_UltracactusPad.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/RM_Veessa_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_eldspar.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_eldspar.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_fuselight.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_fuselight.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_ghostpane.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_keelgrass.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_pitchpearl.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_skyharp.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_skyharp.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_slackwax.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_slackwax.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stillbloom.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stonewater.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_stonewater.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_tarspool.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/chill_plant_tarspool.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/done/rmshademite_v2_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_east.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_north.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/artpipe/failed/rmshademite_v1_south.manifest.json   ambient -- artpipe daemon output, continuously running, predates and outlives this session
?? infrastructure/dashboards/hub/tabs/maturity.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/logs/harvested/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260926_142047.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/modlists/ModsConfig_before_miasma_predation_proof_2026-09-27.xml   pre-existing -- prior sessions' cold-load backups, not mine
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
?? src/RimMandrake/Utils/firehawk_flight_probe.py   pre-existing -- confirmed by wake-triage fork at start of prior session as predating it
```

