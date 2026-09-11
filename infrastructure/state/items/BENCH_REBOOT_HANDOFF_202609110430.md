# BENCH_REBOOT_HANDOFF_202609110430 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609110230`. Everything below is committed and
pushed. **Game and bridge state is the last section.**

## The one thing to carry forward

**The worldmap review is DONE — all four phases — and the verdict is YES.**
`Transient/final_review/WORLDMAP_REVIEW_REPORT.md` (with Phase-2/3 addenda) is
what the owner reads; every claim traces to a findings file in the same dir.
Do not re-run any audit; the punch list files after HIS read, except
`BIOME_TEXT_PORT_1` (already filed — it alone closes all 4 plot leaks).

## What the owner should see (his morning stack, in order)

1. **The review report** — `D:\Luke\dev\Rimworld\Transient\final_review\WORLDMAP_REVIEW_REPORT.md`
   — final verdict: **YES, this is THE map**; 11 punch rows + 2 polish +
   BIOME_TEXT_PORT, all S/M. The Scald closeup
   (`stare_shots/stare_closeup_Scald.png`) is his key-art moment.
2. **FAUNA_GRAPHS_SITTING_1** — 4 PNGs at `D:\Luke\dev\Rimworld\Transient\fauna_graphs_2026-09-11\`
   (Law-3 K band, 23 narrow tolerances, outliers).
3. **KIT_SPECS_CARD_SITTING_1** — now ~31 cards: 18 kit-spec + terraform
   verbatim + 🔴 the biomesteam retire-vs-keep two-rulings conflict + scenario
   "ten thousand years" + 9 mechanoid-origin cards.

## What happened tonight (compressed)

- **Crash saga, resolved**: two mods-config resets diagnosed → the nursery
  juveniles (cross-mod ParentName = unsupported; null thingClass → Game..ctor
  NRE via AlphaGenes' RaceProps deref). Bisect-proven; juveniles PULLED and in
  `src/DEPLOY_HOLD.txt`; `NURSERY_JUVENILES_CRASH_1` (FOUNDRY) owns the re-ship.
  ModsConfig restore = `cp infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
  over the live file (game must be DOWN or it re-clobbers on exit).
- **Game UP, Playing the canonical save** (loaded with `ignoreModCompatibility`
  over the 9 ruled retirements). Bridge FREE. 570-mod list.
- **Deployed during down-windows**: FOUNDRY's absorbed-species port +
  FurnaceHide + Wave-3 counter-patches + BMT port (RSW_-renamed, no collisions)
  + my quickgrass (RM_FE_Plant_Quickgrass; generic grasses evicted).
- Wave 2/3/4 of the stat audit RULED and closed; Law 3 no-op found and filed;
  20/135 GOAL_SHEET boxes ticked on evidence; Mirrored Tickets family retired;
  terramanufacture propagated (5 docs); staged-lore GO (build filed); brain
  worms ruled+filed; 3 biome kit specs installed; mechanoid origin drafted.

## Half-done, and where it stops

- `WORLDMAP_FINAL_REVIEW_1`: open ONLY on the owner's read.
- `MECHANOID_ORIGIN_CANON_1`: draft delivered; open on the 9 cards; propagation
  AFTER rulings.
- `BMT_FAUNA_ABSORPTION_1`: port half proceeds (FOUNDRY); **retirement half
  HELD** on the two-rulings conflict (carded).
- `CANON_DRAIN_1`: gate MET, deliberately left for a FRESH session (its own rule).
- Fresh dump request (`echo all > DefDump/dump_request.txt`) is PLACED but the
  RimDefDump capture state after tonight's loads is UNVERIFIED — check
  `DefDump/captures/` before trusting; it unlocks the biome half of the
  save-vs-bundle check and the Armoury dead-patch regen.

## Traps learned tonight (all in LESSONS_INBOX or item files)

- Cross-mod ParentName silently orphans defs and bricks EVERY game start.
- An unfocused RimWorld with runInBackground off freezes the main loop —
  bridge answers, queued loads never run; `game_focus.focus_game()` first.
- "Caught exception while loading play data" RESETS ModsConfig to ~11 mods.
- `rimworld/load_game` refuses missing-mods saves unless
  `ignoreModCompatibility:true`; a "queued" load from an unfocused Entry is a
  no-op, three times measured.
- Monitor patterns: 'Crashed' substring-matched a texture path — use exact
  signatures.
- pkill -f matched my own shell AGAIN (twice tonight). Kill by exact PID only.
- The seat cgroup OOM-killed a long python.exe during the game's load spike —
  short foreground steps beat one long driver.

## Game / bridge / tree state at wrap

- running : RUNNING, **Playing** CANONICAL_ASHKARR_2026-09-09 (loaded 
  ignoring the 9 retired mods — do NOT save over the canonical slot from this
  session without the owner)
- recorded: UP · Bridge: FREE
- Uncommitted: other seats' churn (Transient health files, artpipe throughput)
  **plus three regenerated Armoury patches + codebase_health_last.json from
  tonight's `refresh.py --all` runs** — left deliberately uncommitted because
  that run's validate step FAILED (the dead ABF patch) and its own verdict says
  not to trust the artefacts against this load set. Next clean refresh (after
  the fresh dump lands) regenerates and commits them deliberately. Everything
  BENCH authored is pushed through `0dda17232`.
