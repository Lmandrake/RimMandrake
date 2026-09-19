# BENCH_REBOOT_HANDOFF_202609111830 — fan-out night: hub built, canon closed, ten specs drafted

## Finished this session (closed, pushed)
- **TERRAMANUFACTURE_CANON_1** — ruling propagated into every founding doc; the
  ship/race refinement ruled by card ("the SHIP was terraforming, the RACE was
  evolving the planet towards terramanufacturing") and recorded at the
  god-engine's MASTER KEY, the item, and the freeze review.
- **MECHANOID_ORIGIN_CANON_1** — verified complete (all cards ruled at the day's
  sitting); B3 item inherits the wipe/spike-immunity charge.
- **DASHBOARD_HUB_ARTIFACT_1 (built, pinned, v5)** —
  https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c
  Source `infrastructure/dashboards/hub/`. Codex spend = window %, NEVER
  dollars (ruled); Gemini channel OFF at the daemon's budget gate (ruled).
  Remaining verify rides HUB_TAB_PUBLISHER_MIGRATION_1 (FOUNDRY).
- **POST_FREEZE_WORLDMAP_AUDIT_1** — frozen world VERIFIED CLEAN, 0/21872 tiles
  differ vs `Saves/CANONICAL_ASHKARR_2026-09-09.rws` on every engine field;
  verification spliced into the Field Audit page; hub worldmap lamp GREEN.
  🔴 V24 is ARCHIVED and stale (2834 biome tiles) — CANONICAL is the world.
- **RIMWORLD_MEMORY_FOOTPRINT_AUDIT_1** — 18.82 GB steady-state MEASURED; crash
  is NOT OOM (native ntdll 0xc0000005); compression already ON (2026-09-08
  synthesis row struck); real lever = 1,578 non-%4 textures (~2 GB) →
  NONDIV4_TEXTURE_FIX_1 (FOUNDRY; 190 MB is our own mods).
- **LOCAL_IMAGEGEN_TRACK_PARKED_1** — parking record complete; rembg EXEMPT,
  capped one-run (REMBG_CONCURRENCY_CAP_1 filed).
- **POISON_FOREST_REPASS_1** — MEASURED block, weather table, R13 venting
  written through; struck phrasing deleted.
- Ruled by card mid-session and propagated: shokkweave commonality **0.05**;
  kyber K1 (deep-time mines) + K2 (heat unchanged); rembg scope.

## Drafted, awaiting the owner — MECHANICS_CARDS_SITTING_1 (~25 cards)
Kit specs: miasma · fever wood · sump · forge · scald · rust cathedral (0 cards,
build-ready, already FOUNDRY's). Plot specs: kyber trade (ruled) · tibanna
embargo (⚠️ T1 is a LIVE contradiction: outerrim.core ships non-beldon tibanna
routes vs the Forge sheet's hard ban) · cathedral concealment arc (A1–A5) ·
ashfall research base (4 held). Liquid types mod brief. Poison-forest weather
names. Fauna injection-layer domains.

## What the owner should look at FIRST
1. `MECHANICS_CARDS_SITTING_1` — one sitting unblocks seven build items.
2. The tibanna T1 contradiction (live stack vs hard ban — a curation cut is
   assumed but not executed).
3. `PLAYER_START_SITE_1` — his pick (Zeddo's Yard vs Gorga's shadow).
4. Hub: https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c
5. Fauna: 196/297 rostered animals violate ruled Law 5 pre-patch
   (`design/Jawa/worldbuilding/fauna_tolerance_violations_2026-09-11.md`).

## Routed to FOUNDRY
SHOKKWEAVE_SOLE_SOURCE_1 (build-ready) · RUST_CATHEDRAL_MECHANICS_1 (build) ·
KYBER_TRADE_PLOT_1 (build) · NINEFOLD_MISSING_EVENT_HOOKS_1 (live verify — four
event triggers, batched, one bridge driver) · COMPANION_SILENT_FAILURE_HARDENING_1 ·
HUB_TAB_PUBLISHER_MIGRATION_1 · NONDIV4_TEXTURE_FIX_1 · REMBG_CONCURRENCY_CAP_1 ·
WORLDMAP_AUDIT_LIVE_CHECKS_1 (game-up batch).

## Traps for whoever resumes
- The queue previews were stale twice tonight; `render.py --overwrite-queues`
  before trusting one.
- Two ledger closes carry an off-by-one sha (POISON, MEMORY — index.lock races
  with FOUNDRY's rapid commits); the item files name the real commits.
- A zero-byte 4-minute-old `.git/index.lock` with no live git process is stale;
  remove it — but check `pgrep -a git` first, FOUNDRY commits in bursts.
- canon.yml's planet census is STILL the deprecated painted lineage —
  CANON_PLANET_CENSUS_1 has ready-to-land values; CSV_REGION_SYNC_1 needs the
  owner's word (freeze re-stamp).
