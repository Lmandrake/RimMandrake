# Legacy variant ticks inside biome sheets — 2026-10-10

Owner (verbatim, 2026-10-10): "The confirm old variant ticks sheet is far too large and clumsy to request this info from the human. Let's handle it within the biome sheets themselves instead."

## Owner question

None needed. Reversible default implemented: **drop** shows the picture's chip as grey struck-through
`old tick dropped` (the set itself is not dimmed or hidden); clicking `drop` again un-answers it.

## Design

- An old (schema-1, possibly machine-default) variant tick is `legacyVariants: [L]` on the row's record. On the biome
  sheet the set it names now carries an in-place control under its letter: **`was ticked before — keep? [keep] [drop]`**
  (same purple chip as the old badge). Tooltip says what keep means on THAT slot: on a random pool, keep = ships as
  one of the pictures the game picks at random; elsewhere keep = only protects its pictures from deletion.
- Answered: `✓ old tick kept` (green) or `old tick dropped` (grey, struck) with the other button still there; clicking the
  lit button again clears the answer (reversible).
- A legacy letter not shown in any lane (purged / quarantined) gets the same keep/drop pair in the row head.
- Row head shows `old tick B, C: keep or drop?` only while some are unanswered. Rows with no legacy ticks: no change.
- Record: `legacyRuled: {L: {v: "confirm"|"drop", at: ISO}}` — written only by his click. No separate screen, no list.
- Readers: `decisions_v2.legacy_answers(v, conf)` (record wins, old-sheet answer as fallback); `confirmations()`
  reads the old confirm file AND every biome decisions file. enact/ingest use `legacy_answers`.

## Changes

- `src/RimMandrake/Utils/art/art_sheet.py` — SLX.legacyState/legacyRule/legacyOpen/legacyHtml; per-picture keep/drop
  replaces the "confirm on the old-ticks sheet" badge; row-head chip only while open; `legacy` act; CSS.
- `src/RimMandrake/Utils/art/decisions_v2.py` — `legacyRuled` documented; `row_answers`, `legacy_answers`,
  `confirmations()` now reads every biome decisions file + the retired sheet's file; `fold_old_sheet_answers`
  (`decisions_v2.py --fold-old-ticks [--apply]`).
- `enact.py`, `ingest.py` — use `legacy_answers(v, conf)` (row click wins); wording points at the row.
- `migration_proof.py` — wording.
- DELETED `src/RimMandrake/Utils/art/old_ticks_sheet.py` (no inbound references); old sheet's server PID 1836845
  stopped; its html/serve.log/img removed (untracked); its decisions file kept (still read by confirmations()).
- RimPulse hand-off `hand:67385f229e` ("Confirm old variant ticks") marked seen.

## Tests

- `selftest_sheet_slots.py` (+8 checks, all fail on the old code): keep/drop toggle and take-back; non-legacy letter
  refused; markup — keep/drop on the picture with pool wording, dropped state with non-pool wording, row-head chip
  and a keep/drop for a tick whose picture is not on the sheet; a row with no old ticks has no old-tick markup.
- `selftest_enact_v2.py` (+5): keep in the row ships; drop in the row beats an old-sheet confirm; confirmations()
  reads biome files + old sheet; fold dry run writes nothing; fold never overwrites an in-row answer, never folds a
  prefill.
- `refresh_sheets.py --selftest` (+2): served_url picks the LAST answering URL (see below).
- Art + pulse selftests 24/24 GREEN. Full sweep: 3 red, none in touched code (ledger_lint: clone vs origin FOUNDRY
  shard; one_path_seam: LocalLow literals in vanilla_beast_carriers.py / Armoury; seashores FileNotFoundError).
- Headless Edge (gate_browser.py) on cauldron: 5/5 legacy rows show the control and the open-ticks chip; 41/41 other
  rows carry no old-tick markup; 0 console errors.

## Migration of existing answers

The old sheet's decisions file held 627 records, **0 with decidedAt** (all agent prefills, never his). Server stopped
first, then `decisions_v2.py --fold-old-ticks --apply`: 0 answers to fold. confirmations() still reads that file, so
nothing could be lost either way.

## Status

DONE. 21 sheets carrying legacy ticks rebuilt via `refresh_sheets.py --no-backfill --force --only …` (627 legacy ticks:
abyss 18, blue_desert 25, cauldron 5, deep_desert 17, desert 85, feverwood 16, floodedcanyon 3, greentide 115,
greysea 42, lanterndeeps 6, leaningscrub 90, miasma 9, pyrelands 3, thechill 14, therot 80, thescald 10, thesump 3,
twilightsea 40, wasteland 5, webwork 23, weepingstones 18). The 6 sheets with none were not rebuilt (no visible change).
remap_decisions dry run: 27 sheets, 0 orphaned. Owner's 8 open servers all answer; each serve.log's last URL is live.

Incident found and fixed on the way: `refresh_sheets.served_url` read the FIRST URL in a serve.log; the owner's
own launches append a second block, so it judged his live cauldron server dead and started a duplicate on a new port.
The duplicate (mine) was stopped, cauldron's serve.log restored to his live server's block, and served_url now reads
the last answering URL (as RimPulse already did). Lesson filed.
