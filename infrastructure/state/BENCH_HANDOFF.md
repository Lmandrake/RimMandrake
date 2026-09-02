# BENCH handoff → Opus (2026-09-02, session 014vwgD9)

Owner is at the bench, actively driving. This is the one terminal today.

## Live state NOT in git (verify, don't trust)
- **Game is UP at `programState=Playing`** on a **disposable dev quicktest colony**
  (I loaded it to disprove the stall). Owner can quit to menu → load his campaign in
  seconds; no cold load needed. Bridge is up; endpoint via
  `rimbridge_client.resolve_endpoint()` (token changes per launch).
- **Bridge is held by BENCH.** `./game` state is `loading`/up per owner's broadcast.
- **`LoadTracer` mod is ENABLED in ModsConfig** (`Config/ModsConfig.xml`, backup
  `.pre_loadtracer`, 598 li). It is a DIAGNOSTIC — pull it before real play. Offered
  to remove it; owner hasn't answered yet.

## Just closed
- **COLD_LOAD_STALL_INTERMITTENT_1 — NOT A BUG** (commit 4f14c0de). The "stall" was a
  healthy idle main menu misread as a hang. Full evidence in
  `infrastructure/state/items/COLD_LOAD_STALL_INTERMITTENT_1.md` and memory
  `idle-menu-looks-like-load-stall.md`. PerformanceOptimizer cleared. Instruments
  built and committed: `jawa/load_stall_probe` (companion tool) + `LoadTracer` mod.
- **SAVE_HOLDS_DEAD_TITAN_CORPSE_1 — closed** (commit bd498088). Was a startup Scribe
  ref in DeepStorage's `Mod_3532608331_*.xml` filter list, scrubbed offline; save-side
  hits were foodRestriction filters that self-heal on re-save.

## Open threads for Opus
1. **Remove LoadTracer from ModsConfig?** Offered; awaiting owner. One-liner: reverse
   the `.pre_loadtracer` backup or delete the `<li>mandrake.rm.loadtracer</li>` line
   + `deploy_custom_mods.py` won't remove it (it's a repo mod, just disable in config).
2. **Load-error census.** Load-time red errors opened the in-game debug-log window
   (that's *why* the menu looked wrong). Offered to census the fresh Player.log and
   file as a NEW item. Not filed yet.
3. **SAVEGAME_PURGE_KEEP_B_1** (filed, owner-ordered, `needs: game-up`): delete all
   saves except the two newest `*_b` (WORLDMAP_V1_original_b, gravship_scratch_b).
   Owner said "must be done with the game up." NOT started.

## Instruments (reusable, committed)
- `jawa/load_stall_probe` — off-thread LongEventHandler read; the only tool safe
  during a REAL load hang. Driver: `src/RimMandrake/bridgetools/probe_now.py`.
- `LoadTracer` — `src/RimMandrake/LoadTracer/`, logs each static ctor before running.
- Staged A/B (unused now): `deployed/config/Mod_2664723367_PerformanceOptimizerMod.FasterGetComp-OFF.xml`.
