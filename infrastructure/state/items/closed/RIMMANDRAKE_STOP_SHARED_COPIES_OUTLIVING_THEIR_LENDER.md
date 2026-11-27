# RIMMANDRAKE_STOP_SHARED_COPIES_OUTLIVING_THEIR_LENDER

## spec
caused-by: RIMMANDRAKE_REAP_CLONES_WHOSE_LENDER_IS_GONE (that item makes the cleaner archive and reap such copies; this
one stops them being made).

Measured 2026-11-19 (run 13:01Z, `~/.local/state/rm-scratch-reap/last_run.json`): ~15 directories of ~4.5 GB each were
git clones borrowing objects (`objects/info/alternates`, i.e. `git clone --shared` or `--reference`) from a lender clone
that was deleted while they lived on. Two makers:

1. Review copies under `/tmp/rm-judge-review.*`, `/tmp/rim-review-*`, `/tmp/*-review*`: their alternates name
   `/home/mandrake/rm/scratch/BENCH/codex-rimmandrake-*` lane clones (`~/.local/state/rm-objstore/uses.jsonl` purpose
   "codex lane builder on <ITEM>"), and one a relentless pool clone `rm/relentless/clones/<ITEM>.det`. The copy is
   made inside the Codex lane run; the lane clone is removed afterwards (no row for it in the reaper's runs.jsonl, so
   not by the reaper) while the /tmp copy stays. The copy's commits then exist nowhere else.
2. `src/RimMandrake/Utils/tunable_sweep.py` `scratch_copy` (`git clone --shared` into `.seat-tmp/<SEAT>/tunable_sweep_*`)
   removes its copy only in a `finally:`; a killed sweep leaves it, detached at a commit only the lender had.

Fix direction: a copy that must outlive its maker's process clones with `--dissociate` (or from the store, not from a
lane clone); a lane clone is not removed while a live clone names it in its alternates (the reaper's borrow check,
`borrowers`, already does this for the reaper's own deletes).

## verify
A selftest per maker: make the copy as the maker does, delete the lender as the maker's cleanup does, and the copy can
still read HEAD (`git rev-parse HEAD^{commit}`), or no copy is left.

## criteria
- no new `/tmp/*review*` or `tunable_sweep_*` clone in a scratch_reap run reads "lender gone" for 7 days after landing.
