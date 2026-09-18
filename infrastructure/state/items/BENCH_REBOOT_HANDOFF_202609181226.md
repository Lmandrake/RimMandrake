# BENCH_REBOOT_HANDOFF_202609181226 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609181608` (which was left uncommitted by its
writer and committed by this session at `cb54695c7`). Everything below is
committed and pushed. **Game and bridge state is the last section.**

## The one thing to carry forward

🔴 **LanternDeeps is built donor-free but HELD from deploy — it must ship WHOLE at
the next shutdown window.** The new XML references GenStep classes in the rebuilt
DLL; deploying the XML alone red-errors the load. `src/DEPLOY_HOLD.txt` carries the
`LanternDeeps/*` hold — remove it in the same change as the deploy. Second: **the
def dump on disk (10:31) is WATER-BROKEN** — captured while 49 water TerrainDefs
were discarded (the FlowWorks lowercase-viscosityClass deploy gap, fixed same day).
The dump marker is RE-ARMED; the next restart refreshes it. Terrain claims against
the current dump are UNMEASURED.

## What the owner should see

Nothing owed his eyes — he sat the whole session and ruled ~30 cards live:
worldmap docs pass (click-is-done, live-roster-canon, rain-excuse doctrine, warm
crags stand, sinks-are-fine, Wildsteam roads, Bitterleaf = island prison colony),
modlist sitting (romance keep-all, VGE census-port-cut, caverns keep+deepscan,
tree trio out post-regen), all six caverns-replacement questions, research-trio
route, Iriaz = antelope, Jawa-fine-in-RSW, shade hinge, droid enclaves one-faction,
WeatherSuite enabled, Maguana port + art accepted unreviewed, Deep incident
suppression.

## What is half-done, and where it stops

- `CAVERNS_PARITY_BUILD_1` (BENCH, doing) — build LANDED at `cd88cd08c`+`f0becf6f9`
  (donor-free defs, DLL clean, incident suppression, KotOR twin injector,
  regression guard). NEXT, in order: (1) queue the 26 art jobs
  (`src/RimUtinni/LanternDeeps/ART_JOBS.md`) through the artpipe — NOT yet queued;
  (2) shutdown-window deploy of the whole mod + drop the DEPLOY_HOLD lines;
  (3) dump refresh rides that restart (marker armed); (4) quicktest that ENTERS a
  Deep — verify strings on the item (cave shape without donor extension, flora
  gate, RSW_BloodropMoth ambush, no suppressed incident fires); (5) Salvation
  precept swap (ruled: replace with RUT equivalent) + re-ingest; (6) then the
  owner's actual CUT ruling retires Biomes! Caverns and the MapComponent_CaveFungus
  crash dies everywhere.
- `WORLDMAP_DOCS_PASS_1` (BENCH, doing) — 15+ rulings landed in docs and ledger.
  Remaining: (a) the landmark review sheet (owner picked sheet-based curation;
  BIOME_LANDMARK_REFINEMENT_1, use review-sheets skill, 8 dense biomes);
  (b) REGIONS_THAT_LIE re-audit against today's world, then card only still-true
  rows; (c) residual stale-directive rows in
  `Transient/worldmap_docs_pass_agenda_2026-09-18.md` (41 found, the decision-grade
  ones ruled; the mechanical strikes can be swept).
- `RESEARCH_TRIO_RETIRE_1` (FOUNDRY, unblocked) — route RULED (port the 4 ruled
  projects, retire the trio); full execution spec is on the item. Briefing:
  `Transient/research_trio_briefing_2026-09-18.md`.
- For FOUNDRY, filed this session: `WALK_FEATURE_KEY_1` (walk model ruled),
  `WORLDGEN_CLICK_RECONCILE_1` (verify the 09-12 save against gate docs),
  `FULL_LOAD_RESIDUE_TRIAGE_1` (RSW patchfails ×10, RSW_*Juv config errors ×42,
  TYR Scribe refs ×10 — evidence files in Transient), `VGE_CENSUS_PORT_CUT_1`,
  `TREE_TRIO_RETIRE_1` (gated on jungle/forest regen), `CAVERNS_PARITY_BUILD_1`
  spawned `BITTERLEAF`-lore already recorded in the world definition.

## Traps learned (all in LESSONS_INBOX)

- **Full-tree `deploy_custom_mods.py` plan reported FlowWorks "in sync" while 4
  files drifted** — the drift carried the water-terrain bug into a full load.
  Re-plan per-mod before trusting a full-tree "in sync".
- **`--mod X --apply` syncs the WHOLE mod** — the Maguana apply carried the peer
  window's undeployed Pufferpig/Qormot/Ronto bestiary WIP to the game folder
  (275 files where ~8 were mine). Read the plan and count files first.
- `jawa/world_neighbors` takes `path` = an OUTPUT FILE and dumps the whole
  adjacency CSV (a stray file named "17007" exists somewhere from a mis-call).
- index.lock storms: the peer window commits in bursts; a retry loop without a
  real sleep (plain `sleep` is blocked; use `python3 -c "import time..."`) burns
  itself out in ms. A 0-byte lock >90s old with `pgrep git` empty is stale.
- The proposals-suite memory said "none ruled" — it was written the day BEFORE the
  review; the suite is FULLY RULED 2026-09-02 (memory corrected).

## Closed since the last handoff (14)

MODLIST_DEFERRED_CARDS_1 · PYRELANDS_CREATURE_RERENDER_1 (walks were the
acceptance) · BIOMES_CAVERNS_DEEPSCAN_1 · CAVERNS_REPLACEMENT_SCOPING_1 ·
NINEFOLD_DEBUG_GAME_READY_CRASH_1 (root cause named, Ninefold cleared) ·
RAIN_BAN_SCOPE_DRIFTED_1 · ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1 ·
JAWA_PHRASING_RSW_TIER_CARD_1 · MOD_CONSOLIDATION_SPRINT_1 ·
IKEE_MYNOCK_ART_REGEN_1 · MENTALBREAK_DESCRIPTION_UNUSED_1 ·
HELIX_TELLUROX_SHELL_LOAD_CRASH_1 · ANTIQUITIES_TREE_BUILD_1 ·
UI_SHELL_SLICE_BUILD_1. Also unblocked: WEAPONS_DONOR_RETIREMENT_1 (kotorcore
dep caveat noted), LIVESTOCK_STARTER_TRIO_1 (richer moornak owed),
DESERT_WRAPS_ART_COMMISSION_1 (pick landed 09-10, matrix buildable).

## Game and bridge state — read before touching the game

- **Game UP** on the full 635 list, **his campaign save
  `CANONICAL_ASHKARR_START_2026-09-12.rws` is LOADED over the bridge** (loaded
  for measurements; ~ticks 126810). ⛔ **Do NOT save** — nothing was changed
  in-session that should persist; a reload or restart is always safe.
- **Bridge FREE** (released after the road authoring).
- **ModsConfig holds 636 and describes the NEXT load** (WeatherSuite enabled on
  the owner's card; the running game is 635). Injections is live this session.
- **Def dump marker ARMED** — next restart writes a fresh dump (the current one
  is water-broken, see the top).
- Roads authored live and committed to the world: Oilpalm + Warthorn DirtPath
  links (world_commit run, read back). Bitterleaf is deliberately roadless
  forever (island prison colony ruling).
