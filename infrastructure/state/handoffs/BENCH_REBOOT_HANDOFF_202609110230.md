# BENCH_REBOOT_HANDOFF_202609110230 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609110019`. Everything below is committed and pushed
unless a line says otherwise. **Game and bridge state is the last section.**

## The one thing to carry forward

**Every fauna ruling lands in THREE files together or the deck lies:**
`round2/decisions_propagated.json` + `round2/move_mapping_v2.md` +
`round2/biome_findings.md`. And a creature's row key is `fauna:<biome>:<name>` OR
`homeless:<name>` — **verify the key exists before any batch edit**: two commits this
session died on a KeyError mid-script while their commit messages overclaimed
(Wampa, Blarth — both re-applied in follow-up commits). The deck builder excludes
rows whose note carries `FACTION-/INJECTABLE-/DUNGEON-/MERGE-RESERVED`; use those
tags, not decision surgery, to keep something off the slides.

## What the owner should see

- **The review deck, Version 6** (calibrated: def-truth drawSizes, square-footprint
  render, per-biome dedup, family collapse):
  https://claude.ai/code/artifact/55e3c8e7-202a-4c5c-b47b-d2bce0747b55
- **The pptx is STALE** — never rebuilt since his drag edits (he had it open all
  night). Rebuild via `round2/build_review_pptx.py` when he closes PowerPoint.
- **Four design docs await/passed his eye** (all owner-ruled at cards already):
  `design/Jawa/worldbuilding/creatures/RUT_hydrocarbon_ecology_commission.md` (16
  species + §14 item economy), `RUT_ruled_commissions_wave2.md` (7 briefs +
  RUT_FurnaceHide), `design/RimMandrake/RM_gelatinous_slime_mod.md` (the universal
  slime mod + RM_GeneSeeker), `design/Jawa/worldbuilding/palettes/palette_color_board.html`.
- **CherryPicker restore at next game-down** — full spec on
  `CHERRYPICKER_SHIP_BASELINE_STALE_1` (restore 139 genuine reversals, keep +617
  Alpha Mechs cuts, then `--capture-ship`). Mechanoid audit for his dungeons:
  zero vanilla `Mech_*` cuts (MEASURED); only 2 Mechanitor enemy pawn-kinds cut.
- **Art regeneration remains HELD** on `CODEX_WORKER_SANDBOX_WRITE_1`; the redo
  queue (Kreetle/Fambaa/Dragonsnake/Horax TOTAL + 162 improves + Beelzebufo
  rename+redefine) and `ART_BACKGROUND_TEMPLATE_1` all ride the fix.

## What is half-done, and where it stops

- **PYRELANDS_MECHANICS_1 is NOT FILED** — the wave-2 brief logs its spikes
  (fire-spread comp cribbing `JobGiver_FireStartingSpree`, spread-only ratified;
  open-field heat-aura hediff for the furnace-beast). First downstream action.
- **FOUNDRY owes 5 changes to their (now committed?) Pyrelands build** — listed in
  wave-2 §8a: remove VEF `CompProperties_Untameable` (BOTH igniters ruled TAMEABLE,
  sheet ban 5 reversed in `the_pyrelands.md`), raise trainability, description line,
  keep 0.9 tame-fail, swap `Leather_Heavy` → `RUT_FurnaceHide`.
- **FLORA_COMMISSION_TEMPLATE_1 + PALETTE_ANCHOR_DRAFT_1**: deliverables landed and
  owner-ruled; items not formally closed in the ledger — close on next ledger pass.
- **GELATINOUS_SLIME_MOD_1**: design complete + owner-ruled twice; build not filed.
- **Three review sidecars still RUNNING deliberately** (fauna 43775, flora 45389,
  homeless 42841 — homeless is FROZEN and refuses writes, proven). Do not kill;
  the serve logs are untracked on purpose.
- FOUNDRY mid-edit in the tree: `src/RimUtinni/UtinniPatches/*AmbientShrineGuardians*`
  + Armoury Crystal textures — theirs, untouched.

## Traps learned (all in LESSONS_INBOX.md)

- **A live sidecar clobbers hand-added top-level keys** (the freeze race): freeze,
  wait, re-read, then PROBE the endpoint (frozen refusal + no leak) before trusting it.
- **Bare `git commit` sweeps whatever other agents staged** in the shared index —
  commit with explicit pathspecs (`git commit -m … -- <paths>`), and `-m` must come
  BEFORE `--`.
- **`cherrypicker.py --is-cut` prints "present" meaning NOT CUT** — present in the
  game. Misread once; cost a wrong claim to the owner.
- **drawSize truth lives in the def XML (adult lifeStage), never the harvested
  census** (census said 4.1-vs-3.2 wrong once, 1.0-default twice); and rendering
  needs explicit square footprint or wide sprites stretch to native aspect.
- **drvfs served a stale git status** that hid a modified file mid-commit; re-read
  before concluding a write vanished.
- serve_sheet's `explorer.exe` fallback pops File Explorer at Documents every
  launch (install wslu / reorder launcher — skill-curation fix).

## Closed / filed this session

- CLOSED: `HOMELESS_DISPOSITION_SITTING_1` (125 rows: 6 place / 9 trader / 18
  ninth-roster / 67 reserve / 25 cut; verdict file frozen; bug-faction law +
  chimera purge recorded).
- FILED: `MIASMA_NURSERY_KINDS_1` (9-species roster + spec), `ART_BACKGROUND_TEMPLATE_1`,
  `WYYYSCHOKK_FERALISK_MERGE_1`, `PYRELANDS_FIRE_WEB_COMMISSION_1`,
  `FLORA_COMMISSION_TEMPLATE_1`, `PALETTE_ANCHOR_DRAFT_1`, `TWINKLE_FLORA_SPIKE_1`,
  `GELATINOUS_SLIME_MOD_1`. UNBLOCKED: `GOO_BOOM_COMMISSION_1` (all 9 calls ruled).
- The sitting record of ~15 numbered owner-ruling batches lives in
  `BIOME_FAUNA_ASSIGNMENT_SITTING_1.md` §§1–15 — the single richest file for
  understanding what was decided tonight.

## Commits

This session runs `d4a4c10d` → `0daf1a65` (~45 BENCH commits interleaved with
FOUNDRY's) — `git log --oneline d4a4c10d^..0daf1a65` for the full list. Majors:
insect/horror/bat/'lisk culls, visitor law, Grey Deep cap release (sheet amended),
Terramorph dayside, flora verdicts + propagation, homeless drain + freeze, deck
calibration (c3d0dcc8/20ffc804), palette board + poison-forest recalibration,
3 commission docs, slime mod design ×3 passes, CherryPicker investigation + ruling.

## Game / bridge / tree state at wrap

- running : RUNNING (RimWorldWin64 up, bridge answers)
- recorded: UP
- Bridge: FREE since 2026-09-11T02:31:45Z
- Uncommitted: ledger/queue render churn (synced in this handoff commit),
  `Transient/` churn (mixed seats), `defs.sqlite` (never commit), three serve
  logs (running sidecars), FOUNDRY's shrine-guardian and crystal files (theirs).
