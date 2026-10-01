# Worker notes — FLOWWORKS_NORTHSTAR_SITE_PREP_1

Status: started 2026-10-01

## Plan
- tier flowworks
- preflight_flowworks.py
- prep_site.py
- selftests

## Progress
- read plan §3/§3.9/§6, driver (site/preflight/transport/session), Graffiti template, modset_builder
- layout: src/RimMandrake/FlowWorks/northstar/ (.py excluded from deploy, so P-O3 in-sync unaffected)
- MEASURED tool facts (JawaBench [Tool] source): get_terrain_batch/get_roof_batch return RLE `ops`, not `cells`;
  get_terrain_layers gives base+temp per cell; weather_get gives conditions[]; no read-only incident-queue tool
  (incident_queue_clear reports clearedCount); no autosave setter (plan §3.4's `jawa/set_player_settings` is a
  per-pawn tool -- plan line corrected); JawaBench is a RimBridge companion, not a ModsConfig entry.
- NEW tools the site needs (absent today => prep stops before save, preflight UNMEASURED):
  jawa/flowworks_body_report (body classify/read), jawa/flowworks_engine_state (nextPulseTick, activeFluid,
  rain accumulator), type_probe extension (assembly location/MVID/sha).
- Plot E (tar) and F (slime) ponds are NOT painted in the golden site: ActiveFluid must be set before first
  classification (plan §2.3), so the bar paints them on its own working copy. Every golden body is water.
- DONE: modset_builder tier `pits` -> `flowworks` + `tier_guard` (forbid pits/alphabiomes/manywaters in the
  CLOSURE, all 5 DLC). Plan run: 9 mods, Harmony..FlowWorks.
- DONE: northstar/site_spec.py -- defaults (27 toggles), layout packer (11 plots, fits 200..275), manifest
  model, RLE parser, exact-bytes config backup/restore.
- DONE (untested yet): fakegame.py (dirty start + item's dirt faults), preflight_flowworks.py (23 rows).
- DONE: prep_site.py. `--fake` rehearsal: builds 11 plots, classifies 4 bodies, saves read-only golden +
  sidecar. `--fake-without-new-tools` (today's live tool set): REFUSED at step 6, exit 3, nothing saved.
- DONE: selftest_flowworks_northstar.py -- 88/88 ok (tier guards, settings==C#, layout, byte-exact
  backup/restore, prep incl. refusals, clean preflight all-PASS, 9 dirt cases each refused by its row,
  combined dirt (rain+prefilled+stray pawn+cold) refused on P-E1/P-S1/P-E4/P-E2, offline rows on fixtures).
- P-S1 reads D/F at every FOOTPRINT cell (batched); buffer D/F covered by P-S3 map-wide count.
- Real offline preflight (read-only) 2026-10-01: P-O1 PASS (38+5 VALIDATED), P-O3 PASS (in sync, stamp MATCH),
  P-O2 FAIL (38/38 must-show unclaimed, 25/27 toggles uncovered -- validation.py is still the Pits suite),
  P-O4 FAIL (live list lacks 5 FULL.LATEST mods: prepatcher, loadtracer, betterstacktraces, rule56,
  nwnrealfogofwar -- restore_full() would change his list), P-O5 FAIL (pre-commit + no golden yet),
  P-O6 FAIL (no backup yet). NB that run READ the live ModsConfig.xml (P-O4) -- read only, nothing written.
- run_selftests: 81/83, new selftest PASS; the one FAIL is selftest_sound_paths.py (TheForge/Wasteland
  clipPaths), unrelated.
- Plan §3.4 corrected: autosave has no bridge setter (`jawa/set_player_settings` is per-pawn).
- Needs the bridge holder: build jawa/flowworks_body_report + jawa/flowworks_engine_state + type_probe identity,
  then `preflight_flowworks.py backup`, swap tier, `prep_site.py`, `preflight_flowworks.py all`, and the live
  dirtied-working-copy proof the item asks for.
