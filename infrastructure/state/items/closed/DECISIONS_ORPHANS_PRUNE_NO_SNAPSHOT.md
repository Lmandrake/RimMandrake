# DECISIONS_ORPHANS_PRUNE_NO_SNAPSHOT

Found in the ENACT_KEYED_FIX_UNREVIEWED review (FOUNDRY, 2026-10-24). Data hygiene; one file had held an owner ruling
(the phase0 one, below).

Under Transient/biome_ffar/, three `*.decisions.json` files crash every enact code path (old and new identically):
- `tree_art_new_renders_sheet_2026-10-18.decisions.json`: its snapshot was deleted in 76e72b9156, and the BSOD repair
  8e0f4a5c6f re-landed the decisions file. Prefill, 0 owner rows.
- `art_eval_shadow_e2e_weepingstones_20261023_sheet_2026-10-23.decisions.json`: tracked by dfbb2bf540, but its snapshot
  was never in infrastructure/state/art/sheets. Prefill.
- `phase0_remaining_art_sheet_2026-10-16.decisions.json`: not a decisions doc (a map keyed by sheetId), so the
  `*.decisions.json` glob picks it up. The map is a `remap_decisions.py --json` report that 8a725c4aef (2026-10-22)
  committed OVER his ruled sheet: 20 sidecar picks, enacted in 6a0fa2c99a.

Action: verify each reviewStatus is still prefill, then delete the two orphans, fixing inbound references, as the
wrong-material ruling requires. Rename or move the phase0 map out of the decisions glob.

Evidence: /home/mandrake/.seat-tmp/FOUNDRY/enact_vet4/realdiff.txt

## Outcome (relentless gen 1, 2026-11-02)
- tree_art: snapshot still absent, prefill, deleted. The one inbound mention is a dated handoff's untracked-file list (a record).
- weepingstones: its snapshot was committed in 3bf01960db and matches snapshotId d0303f0897921093; it reads cleanly and stays.
- phase0: his 20-row ruling restored from 6a0fa2c99a (reviewStatus still says prefill, so enact refuses to re-apply it).
- Root cause guarded: `remap_decisions.py --json` refuses a `*.decisions.json` target.
- Proof: `run_selftests.py --only selftest_decisions_glob_hygiene` checks every file in the glob against build_plan's head checks.
