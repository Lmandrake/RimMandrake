# FOUNDRY_REBOOT_HANDOFF_202609122103 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609121737`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

A single "sorts after the one file I know about" ordering fix for a same-mod
Patches/ load-order bug is not enough — it has now broken TWICE on the exact
same item (GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1). RimWorld applies one mod's
`Patches/*.xml` in plain filesystem/alphabetical order, and ANY file in that
folder can add a duplicate wildAnimals entry, not just the one you had in
mind when you renamed the fix file. The only actually-safe fix is a name that
sorts after EVERY current filename in the folder (we used a `ZZZ_` prefix),
confirmed against a fresh live capture, not just "after BiomeCast_Ashkarr.xml"
or "after the file I know touches this." Re-check the real folder listing,
every time, before trusting an ordering-based fix in this codebase.

## What the owner should see

- The new Utinni world-map ship icon (`UTINNI_WORLDMAP_FLIGHT_ICON_1`) is
  shipped and deployed but has NOT been looked at in flight by anyone —
  `Gravship.ExpandingIconColor` multiplies the sprite by the player faction
  color in C# (the XML color field is inert for this def), so the art was
  authored mid-value/near-neutral to survive that multiply rather than the
  literally-dark hull the owner's own description implied. Worth a look next
  real flight, and worth saying explicitly whether the tint reads right or
  needs darkening at source.
- Two real, silent regressions caught and fixed tonight before they shipped
  further: reverted-to-donor Dewback art (live, actually showing wrong art
  until fixed) and a would-have-been-reintroduced Anooba regression (caught
  before commit/deploy). Both from the same mechanism: a `mandrake.rsw.
  <name>artoverride` mod's custom art silently loses to a later SWBestiary
  port shipping donor art at the identical texPath. `MLIE_ARTOVERRIDE_
  COLLISION_CHECK_1` left a full collision map for the 6 species still queued
  to port (Mynock, Kreetle, Horax, Fambaa, Zakkeg, Ronto) — whoever ports them
  next must read it first.
- `OCULAR_OVERDRIVE_SITE_1`'s landmark half shipped clean (The Spire, tile
  16955 — NOT the original donor tiles, which turned out to be Impassable
  hilliness and literally unreachable by caravan; a real siting error in the
  original filing, corrected). The dungeon/KCSG half explicitly needs a bench
  sitting per the design doc's own words — re-routed to `needs=owner`, not
  left as a silent FOUNDRY stall.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and the exact next action,
     or close/block it. --check refuses while any is unaccounted
     for, so deleting a line here is not a way past it. -->
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — cross-registration class (RSW_Iriaz/
  RSW_Mudhorn) and the ZBiome_Grasslands in-list class (Gizka/Nuna/Orray/Zeer)
  are LIVE-CONFIRMED fixed this session. The AA_Eyeling in-list class (Wasteland/
  ExtremeDesert/ZBiome_DesertOasis) was fixed AFTER this session's restart and
  deployed but NOT yet live-confirmed — next action: restart, `harvest_log.py
  --show configerror`, confirm no more "Duplicate animal record: AA_Eyeling"
  lines, then `rimflow close`. Also: a SEPARATE Giddy-Up crash
  (`ArgumentNullException: Value cannot be null. Parameter name: key`, same
  call site) showed up in this session's log — filed as `GIDDYUP_NULLKEY_
  CRASH_1`, untouched, needs its own investigation (which biome/PawnKindDef
  has a null reference).
- `OCULAR_OVERDRIVE_SITE_1` — landmark half done and closed via its own item
  (`ASHFALL_SPIRE_LANDMARK_1`). Re-routed to `needs=owner`: the dungeon/KCSG
  authoring and canon.yml propagation is explicitly a bench sitting per
  `design/Jawa/worldbuilding/ashfall_research_base.md`'s own words, not solo
  FOUNDRY work. Next action is the owner's, not FOUNDRY's — do not pick this
  back up without a bench sitting first.
- `UTINNI_WORLDMAP_FLIGHT_ICON_1` — art, patch and Mod Settings toggle all
  shipped and deployed (including the DLL, redeployed during this session's
  shutdown window). The one remaining step is a live look: the parked
  `FLIGHT_hop1_seas_cleaned_2026-09-12.rws` save has the ship GROUNDED, not in
  flight (`world_objects_get{def:Gravship}` returned 0) — deliberately did NOT
  force a launch on the owner's own in-progress save just to screenshot it.
  Next action: whoever is at the bench when the owner (or a session) actually
  flies the ship should screenshot both zoom levels and flag whether the tint
  reads right.

## Traps learned

- **A same-mod Patches/ load-order fix must sort after the WHOLE folder, not
  the one file you think is the offender.** See "The one thing to carry
  forward" above — this cost a second restart tonight. `ZZZ_` prefix is now
  the house convention for "must load last within this mod."
- **`validate_patch.py` without `--defs` cannot see a DIFFERENT mod's texPath
  coverage.** It only checks the mod being edited's own `Textures/`. A "missing
  texture, 6 errors" result from a bare run can be a false positive if another
  mod (an ArtOverride mod, in this campaign) supplies that exact texPath and
  loads after. Cost a near-regression on `RSW_Anooba` tonight (caught before
  commit). Always run with `--defs <installed mod dirs>` when checking texPath
  coverage, never bare, when an ArtOverride-style mod might be in play.
  `MLIE_ARTOVERRIDE_COLLISION_CHECK_1`'s writeup names which species have this
  risk right now.
- **A background subagent can get stuck in a self-inflicted "waiting for a
  monitor" loop after actually finishing its work**, sending several
  duplicate/garbled task-notifications before eventually recovering with a
  real report (or never recovering — reviewed the diff directly rather than
  trusting the notification, both times). Filed as product feedback
  (`SendFeedback`) this session; if it recurs, don't wait on the notification
  text — check `git status`/`git diff` on the paths the agent was told to
  touch directly.
- `AA_Eyeling` is the renamed-in-repo `ikee` (`Ikee_Rename.xml`) — searching
  for the OLD donor name still finds every place it matters; the NEW label
  ("ikee") is cosmetic only and does not change the defName anywhere.

## Closed since the last handoff (5)

- `CATHEDRAL_ROACH_THINKTREE_GAP_1` — 95eb3bfe8c1f54ebd9ea860cee8e3a520b05bc33
- `ASHFALL_SPIRE_LANDMARK_1` — 95eb3bfe8c1f54ebd9ea860cee8e3a520b05bc33
- `MLIE_ARTOVERRIDE_COLLISION_CHECK_1` — f614eb5ba1e603d3e1adf99234ae9077f30dc659
- `SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1` — 36e0255c1d8273608bc3749aea911255b9cf5269
- `MEGAFAUNAYIELD_DEAD_GR_TARGETS_1` — 8f627e057d068df7a17c2aa14084452bfbd96102

## Filed and still open (4) — the next seat's queue

- `MOD_VALIDATION_RUNNER_1` — Build modcheck: the scripted mod-functionality validation runner (steps file + shared runner, minimal-list quicktest sessions, read-back+screenshot ev
- `MOD_VALIDATION_PIT_PILOT_1` — modcheck pilot: write the pit mod's validation.steps.yaml (settings toggles as floor + beyond-toggle components: falls-in, climb-out vs not, full func
- `MOD_VALIDATION_RETROFIT_1` — modcheck full retrofit wave: every shipped mod gets a validation.steps.yaml and a green run (owner ruling 2026-09-12: full wave, not campaign-critical
- `GIDDYUP_NULLKEY_CRASH_1` — Giddy-Up BuildAnimalBiomeCache also throws ArgumentNullException (key) at BiomeDef.CommonalityOfAnimal -- a NULL PawnKindDef reference, not a duplicat

## Commits

```
07de1dcb9 rimdrive: bridge-library design deep-dive (owner-commissioned, 2026-09-12)
8f627e057 GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: rename the dedup fix again, one file still beat it
745e14e42 modcheck: debug mode with declared chain checkpoints; smoke mode stays checkpoint-free (owner addendum, 2026-09-12)
dd2048e52 modcheck re-ruled (owner, 2026-09-12): per-mod Python on shared library, steps-YAML dropped; build-up/tear-down absolute (spec 1b)
0769a4d67 MEGAFAUNAYIELD_DEAD_GR_TARGETS_1: record the full investigation writeup
4ad33cdf8 Lesson: bridge driving cost is LLM turns, not the bridge (measured 2026-09-12)
34a6dc87d bridge_latency_bench.py: re-runnable A/B/C driving-cost benchmark (spawn / setup / per-call), read-only
36e0255c1 SCARROACH_CATHEDRALROACH_TEXTURES_MISSING_1: original sprite art for both roaches
935b29048 MEGAFAUNAYIELD_DEAD_GR_TARGETS_1: gate stat/resize/tolerance patches on target-def existence
cba1a4944 modcheck: scripts own their entire setup; chained components share state, downstream of a chain failure reads UNMEASURED (owner, 2026-09-12)
7f3fc2247 modcheck: minor-declare bounded to trivial no-gameplay-effect changes, diff recorded with the claim (owner, 2026-09-12)
f614eb5ba MLIE_ARTOVERRIDE_COLLISION_CHECK_1: fix live Dewback art-override regression
1a2cae364 modcheck: owner-designed pre-playtest validation system — spec + 3 items filed (owner sitting 2026-09-12)
770a328ed UTINNI_WORLDMAP_FLIGHT_ICON_1: replace vanilla gravship world-map sprite with the Utinni's own silhouette
95eb3bfe8 CATHEDRAL_ROACH_THINKTREE_GAP_1 + GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1 (in-list class)
18d8b11c7 Owner sitting 2026-09-12: biome repaint GO, fog reveal confirmed, sheets sitting marked done, FULL modlist captured at 593
539990920 GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1: strip duplicate wildBiomes entries across 14 RSW_ animals
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-09-12T21:02:35Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 D infrastructure/artpipe/pending/dactillion_v1_east.json
 D infrastructure/artpipe/pending/dactillion_v1_north.json
 D infrastructure/artpipe/pending/dactillion_v1_south.json
 D infrastructure/artpipe/pending/fanback_v1_east.json
 D infrastructure/artpipe/pending/fanback_v1_north.json
 D infrastructure/artpipe/pending/fanback_v1_south.json
 D infrastructure/artpipe/pending/grank_v1_east.json
 D infrastructure/artpipe/pending/grank_v1_north.json
 D infrastructure/artpipe/pending/grank_v1_south.json
 M infrastructure/artpipe/registry.jsonl
 M infrastructure/artpipe/throughput.jsonl
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? design/Jawa/worldbuilding/review/serve_fauna.log
?? design/Jawa/worldbuilding/review/serve_flora.log
?? design/Jawa/worldbuilding/review/serve_homeless.log
?? infrastructure/artpipe/daemon_run_20260911_105041.log
?? infrastructure/artpipe/done/aa_frostmite_v1_east.json
?? infrastructure/artpipe/done/aa_frostmite_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.json
?? infrastructure/artpipe/done/aa_frostmite_v1_north.manifest.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.json
?? infrastructure/artpipe/done/aa_frostmite_v1_south.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.json
?? infrastructure/artpipe/done/aa_terramorph_v1_east.manifest.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.json
?? infrastructure/artpipe/done/aa_terramorph_v1_south.manifest.json
?? infrastructure/artpipe/done/boma_v1_east.json
?? infrastructure/artpipe/done/boma_v1_east.manifest.json
?? infrastructure/artpipe/done/boma_v1_north.json
?? infrastructure/artpipe/done/boma_v1_north.manifest.json
?? infrastructure/artpipe/done/boma_v1_south.json
?? infrastructure/artpipe/done/boma_v1_south.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_east.json
?? infrastructure/artpipe/done/borcatu_v1_east.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_north.json
?? infrastructure/artpipe/done/borcatu_v1_north.manifest.json
?? infrastructure/artpipe/done/borcatu_v1_south.json
?? infrastructure/artpipe/done/borcatu_v1_south.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_east.json
?? infrastructure/artpipe/done/cinderwing_v1_east.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_north.json
?? infrastructure/artpipe/done/cinderwing_v1_north.manifest.json
?? infrastructure/artpipe/done/cinderwing_v1_south.json
?? infrastructure/artpipe/done/cinderwing_v1_south.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_east.json
?? infrastructure/artpipe/done/dactillion_v1_east.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_north.json
?? infrastructure/artpipe/done/dactillion_v1_north.manifest.json
?? infrastructure/artpipe/done/dactillion_v1_south.json
?? infrastructure/artpipe/done/dactillion_v1_south.manifest.json
?? infrastructure/artpipe/done/duskram_v1_east.json
?? infrastructure/artpipe/done/duskram_v1_east.manifest.json
?? infrastructure/artpipe/done/duskram_v1_north.json
?? infrastructure/artpipe/done/duskram_v1_north.manifest.json
?? infrastructure/artpipe/done/duskram_v1_south.json
?? infrastructure/artpipe/done/duskram_v1_south.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_east.json
?? infrastructure/artpipe/done/emberscythe_v1_east.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_north.json
?? infrastructure/artpipe/done/emberscythe_v1_north.manifest.json
?? infrastructure/artpipe/done/emberscythe_v1_south.json
?? infrastructure/artpipe/done/emberscythe_v1_south.manifest.json
?? infrastructure/artpipe/done/fanback_v1_east.json
?? infrastructure/artpipe/done/fanback_v1_east.manifest.json
?? infrastructure/artpipe/done/fanback_v1_north.json
?? infrastructure/artpipe/done/fanback_v1_north.manifest.json
?? infrastructure/artpipe/done/fanback_v1_south.json
?? infrastructure/artpipe/done/fanback_v1_south.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_east.json
?? infrastructure/artpipe/done/featherfeel_v1_east.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_north.json
?? infrastructure/artpipe/done/featherfeel_v1_north.manifest.json
?? infrastructure/artpipe/done/featherfeel_v1_south.json
?? infrastructure/artpipe/done/featherfeel_v1_south.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_east.json
?? infrastructure/artpipe/done/fenshear_v1_east.manifest.json
?? infrastructure/artpipe/done/fenshear_v1_south.json
?? infrastructure/artpipe/done/fenshear_v1_south.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.json
?? infrastructure/artpipe/done/gr_spidercat_v1_east.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.json
?? infrastructure/artpipe/done/gr_spidercat_v1_north.manifest.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.json
?? infrastructure/artpipe/done/gr_spidercat_v1_south.manifest.json
?? infrastructure/artpipe/done/grank_v1_east.json
?? infrastructure/artpipe/done/grank_v1_east.manifest.json
?? infrastructure/artpipe/done/grank_v1_north.json
?? infrastructure/artpipe/done/grank_v1_north.manifest.json
?? infrastructure/artpipe/done/grank_v1_south.json
?? infrastructure/artpipe/done/grank_v1_south.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_east.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_north.manifest.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.json
?? infrastructure/artpipe/done/greaterkraytdragon_v1_south.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_east.json
?? infrastructure/artpipe/done/grubhorn_v1_east.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_north.json
?? infrastructure/artpipe/done/grubhorn_v1_north.manifest.json
?? infrastructure/artpipe/done/grubhorn_v1_south.json
?? infrastructure/artpipe/done/grubhorn_v1_south.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_east.json
?? infrastructure/artpipe/done/hawkbat_v1_east.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_north.json
?? infrastructure/artpipe/done/hawkbat_v1_north.manifest.json
?? infrastructure/artpipe/done/hawkbat_v1_south.json
?? infrastructure/artpipe/done/hawkbat_v1_south.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_east.json
?? infrastructure/artpipe/done/insectomorph_v1_east.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_north.json
?? infrastructure/artpipe/done/insectomorph_v1_north.manifest.json
?? infrastructure/artpipe/done/insectomorph_v1_south.json
?? infrastructure/artpipe/done/insectomorph_v1_south.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_east.json
?? infrastructure/artpipe/done/kinrath_v1_east.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_north.json
?? infrastructure/artpipe/done/kinrath_v1_north.manifest.json
?? infrastructure/artpipe/done/kinrath_v1_south.json
?? infrastructure/artpipe/done/kinrath_v1_south.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_east.json
?? infrastructure/artpipe/done/mycolith_v1_east.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_north.json
?? infrastructure/artpipe/done/mycolith_v1_north.manifest.json
?? infrastructure/artpipe/done/mycolith_v1_south.json
?? infrastructure/artpipe/done/mycolith_v1_south.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_east.json
?? infrastructure/artpipe/done/ollopom_v1_east.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_north.json
?? infrastructure/artpipe/done/ollopom_v1_north.manifest.json
?? infrastructure/artpipe/done/ollopom_v1_south.json
?? infrastructure/artpipe/done/ollopom_v1_south.manifest.json
?? infrastructure/artpipe/done/orray_v1_east.json
?? infrastructure/artpipe/done/orray_v1_east.manifest.json
?? infrastructure/artpipe/done/orray_v1_north.json
?? infrastructure/artpipe/done/orray_v1_north.manifest.json
?? infrastructure/artpipe/done/orray_v1_south.json
?? infrastructure/artpipe/done/orray_v1_south.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_east.json
?? infrastructure/artpipe/done/pekopeko_v1_east.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_north.json
?? infrastructure/artpipe/done/pekopeko_v1_north.manifest.json
?? infrastructure/artpipe/done/pekopeko_v1_south.json
?? infrastructure/artpipe/done/pekopeko_v1_south.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_east.json
?? infrastructure/artpipe/done/scarrend_v1_east.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_north.json
?? infrastructure/artpipe/done/scarrend_v1_north.manifest.json
?? infrastructure/artpipe/done/scarrend_v1_south.json
?? infrastructure/artpipe/done/scarrend_v1_south.manifest.json
?? infrastructure/artpipe/done/shiro_v1_east.json
?? infrastructure/artpipe/done/shiro_v1_east.manifest.json
?? infrastructure/artpipe/done/shiro_v1_north.json
?? infrastructure/artpipe/done/shiro_v1_north.manifest.json
?? infrastructure/artpipe/done/shiro_v1_south.json
?? infrastructure/artpipe/done/shiro_v1_south.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_east.json
?? infrastructure/artpipe/done/slagmaw_v1_east.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_north.json
?? infrastructure/artpipe/done/slagmaw_v1_north.manifest.json
?? infrastructure/artpipe/done/slagmaw_v1_south.json
?? infrastructure/artpipe/done/slagmaw_v1_south.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_east.json
?? infrastructure/artpipe/done/sludrin_v1_east.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_north.json
?? infrastructure/artpipe/done/sludrin_v1_north.manifest.json
?? infrastructure/artpipe/done/sludrin_v1_south.json
?? infrastructure/artpipe/done/sludrin_v1_south.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_east.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_north.manifest.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.json
?? infrastructure/artpipe/done/vaewaste_megatardi_v1_south.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_east.json
?? infrastructure/artpipe/done/verdaunt_v1_east.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_north.json
?? infrastructure/artpipe/done/verdaunt_v1_north.manifest.json
?? infrastructure/artpipe/done/verdaunt_v1_south.json
?? infrastructure/artpipe/done/verdaunt_v1_south.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_east.json
?? infrastructure/artpipe/done/vornskyr_v1_east.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_north.json
?? infrastructure/artpipe/done/vornskyr_v1_north.manifest.json
?? infrastructure/artpipe/done/vornskyr_v1_south.json
?? infrastructure/artpipe/done/vornskyr_v1_south.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_east.json
?? infrastructure/artpipe/done/whisperbird_v1_east.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_north.json
?? infrastructure/artpipe/done/whisperbird_v1_north.manifest.json
?? infrastructure/artpipe/done/whisperbird_v1_south.json
?? infrastructure/artpipe/done/whisperbird_v1_south.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.json
?? infrastructure/artpipe/done/wyyyschokk_v1_east.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.json
?? infrastructure/artpipe/done/wyyyschokk_v1_north.manifest.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.json
?? infrastructure/artpipe/done/wyyyschokk_v1_south.manifest.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.json
?? infrastructure/artpipe/failed/aa_terramorph_v1_north.manifest.json
?? infrastructure/artpipe/failed/fenshear_v1_north.json
?? infrastructure/artpipe/failed/fenshear_v1_north.manifest.json
?? infrastructure/artpipe/registry.jsonl.lock
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? infrastructure/state/items/MLIE_ARTOVERRIDE_COLLISION_CHECK_1.md
```

