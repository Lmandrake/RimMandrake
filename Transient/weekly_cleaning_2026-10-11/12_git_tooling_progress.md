# 12 — git tooling root-cause fixes + `clone-landing-commits` skill (progress)

Writer: BENCH subagent, 2026-10-11.

| step | state | PUBLISHED |
|---|---|---|
| 1 served sheet outputs untracked | done | f1ebcd0ea |
| 2 land.sh realign + LAND_REPO default + push-race retry | done | a4f01d816 |
| 3 seat sync (`./sync`, seat_sync.py; reconcile_clone.py deleted) | done (landed before 2: land.sh calls it) | 6b0855059 |
| 4 publish.py: plumbing replay + reset --keep, no --autostash | done | 467255961 |
| 5 ledger_sync.py temp clone cleanup | done | f12fe2a7c |
| 6 hook false positives | blanket-stage fixed; owner-said written up | 6ac4d20d0 |
| 7 loose objects (document only) | documented, nothing run | — |
| GIT_WORKFLOW Traps + skill `clone-landing-commits` (+ standing_rulings landing line) | done | ffb721531 |
| run_selftests N/N | GREEN: PASS 406/408, FAIL 0, CRASH 0, SKIPPED 2 | — |

## Notes per step

### 1 — why this fix (served sheet outputs)
- Measured: the sidecar (`serve_sheet.py`, exec'd by `serve_gated.py`) writes ONLY `<sheet>.decisions.json`; it never
  rewrites the HTML. The 24 dirty `*_sheet_*.html` are REAL rebuilds by `refresh_sheets.py` (gate stamp + new template,
  ~650-700 lines each, 08:23 today) that nobody published. So "write only on content change" already holds.
- Untracked (gitignore + removed from the index, files stay on disk): `Transient/**/*.serve.log` (27) and
  `Transient/biome_ffar/sheets_state.json` (program-read fingerprint cache). RimPulse (`pulse_core.read_sheets`) and
  `refresh_sheets.served_url` read them from the clone's disk, so they keep working. Side effect: a clone that PULLS the
  removal loses its own copies (foundry's are stale; no server runs there); `sheets_state.json` missing = refresh rebuilds all once.
- HTML and `*.decisions.json` stay TRACKED (owner 2026-09-01 Transient ruling). Instead `refresh_sheets.py` now ends with an
  `UNPUBLISHED:` line naming every rebuilt sheet and the exact `land.sh -m` command. With `./sync` (reset --keep) a dirty
  sheet no longer blocks syncing unless upstream changed the same sheet.
- NOT done, for the owner: the 24 rebuilt sheet HTMLs in bench are still unpublished (~7 MB) — publish or leave;
  `Transient/biome_ffar/img/` has 1,934 untracked renders beside 7,600 tracked ones (noise only; not blocking).

### 2/3 — landing and sync
- `land.sh`: LAND_REPO defaults to `git rev-parse --show-toplevel`; refuses outside a clone. After the push: update
  `refs/remotes/origin/main`, run `seat_sync.py --no-fetch` (stderr), stdout stays `PUBLISHED <sha>`. Retries a lost push
  race up to 5 times (hit live while landing step 2). `~/.seat-tmp/land.sh` is now a one-line exec wrapper (old file
  backed up to `~/.claude/backups/weekly_cleaning_2026-10-11/seat-tmp-land.sh.tgz`). Selftest `selftest_land.py` 15/15.
- `./sync` = `seat_sync.py`: fetch → refuse unless every local commit is upstream (git cherry `-`, or same bytes per path)
  → stage dirty paths already holding upstream bytes (needed: `reset --keep` refuses a dirty file even when it equals the
  target — measured) → move aside byte-identical untracked blockers → backup branch → `git reset --keep origin/main`.
  Selftest `selftest_seat_sync.py` 18/18. Live: refused correctly on a peer's unlanded commit, then SYNCED bench (8 dup commits).

### 4 — publish.py
- `rebase()` no longer runs `git pull --rebase --autostash`. Each local commit not already upstream (git cherry `+`) is
  re-created on origin/main by `git merge-tree --write-tree` + `commit-tree` (no index, no worktree), then
  `git reset --keep <new tip>`. A real conflict, or an uncommitted edit to a file origin changed, is refused by name with
  the commit intact on HEAD; nothing is ever stashed. `PUBLISHED <sha>` contract unchanged. Selftest 11/11 (new case:
  dirty overlap refused, no stash). Steps 4-6 were published with the new `./publish` from the dirty bench clone.

### 5 — ledger_sync.py
- Without `--clone` it made `tempfile.mkdtemp()` (in /tmp tmpfs) + `git clone --reference <seat> --dissociate` (full
  object copy) and never deleted it. Now: temp dir under `/home/mandrake/rm/scratch/<SEAT>/`, objects BORROWED (no
  `--dissociate`; safe because the clone is deleted at the end), `shutil.rmtree` in `finally`. A user-given `--clone` is
  still kept for reuse and still dissociated. Selftest: new "temp clone removed after the run".

### 6 — hooks
- `block_blanket_git_stage.py`: FIXED. Quote-aware segment split (a `;`/`|` inside quotes no longer splits), heredoc
  bodies dropped unless fed to a shell (`bash <<EOF` is still scanned), `bash -c '<script>'` scanned recursively. Stale
  "Four threads share this working tree" text replaced with one-writer-per-clone + helpers wording. Selftest 40/40
  (8 new cases: 4 hidden-in-shell DENY, 4 text-not-command ALLOW).
- `block_forged_owner_said.py`: NOT changed — not clearly safe. It was hardened TODAY (ab1dab8b6, 4badee467) against 37
  adversarial routes, one of which is a python argv list (the flag and a value as list items) — a script body that DOES
  set the field. Exempting heredoc/script bodies would reopen that route. Hit by THIS writer too: a python heredoc that
  only wrote this progress file was refused because its text contained the flag followed by a one-letter quoted value.
  Workarounds that work today: write such text with the Write/Edit tools, or put the script in a file and run
  `python3 /path/script.py` (the command-text hook does not read files; `owner_said_provenance.py` re-proves a quote
  where it is USED — rimflow, broadcast.py, apply_blanket_ruling.py). A real fix needs a "does this command reach one of
  those three tools at all" gate before matching; that is a judgement for whoever owns OWNER_SAID_GUARD_REVIEW.

### 7 — repo weight (measured 2026-10-11, NOTHING run)
- bench `.git`: 101,797 loose objects (4.40 GiB) + 155 packs (5.60 GiB); 3,393 prune-packable; garbage 0.
- foundry `.git`: 1,183 loose (32 MiB) + 5 packs (6.37 GiB).
- Owner decides: `git -C /home/mandrake/rm/bench gc` once (or `git maintenance register` for a scheduled repack). Expect
  several GiB back from packing the loose objects (UNMEASURED until run); run it when no window is mid-git in bench.

### Docs + skill
- `GIT_WORKFLOW.md`: "The loop" rewritten around `./publish` / `land.sh` / `./sync`; the "Landing when pull --rebase is
  refused" section and its manual `git cherry` + `checkout -B` realign ritual DELETED (replaced by the tools); new
  "Scratch clones" and "Traps" sections (16 rows from lessons + memory: silenced add, deleted-path add, pathspec takes
  worktree, remove-but-keep, untracked pathspec, `-F -` after `--`, bare commit, index.lock, compound refusals,
  owner-said on text, zsh `:r` refspec, land.sh duplicates, autostash, pre-push lint on stale HEAD, served sheets,
  fetch OOM, merge commit). `standing_rulings.md` §Git still prescribed `git pull --rebase` — corrected.
- `skills/clone-landing-commits/SKILL.md` (lean; traps point to GIT_WORKFLOW), symlink `.claude/skills/clone-landing-commits`,
  roster row via `doc_roster.py --write` (design/INDEX.md regeneration discarded — not in scope).
- skill-creator's description-trigger eval (`run_loop`, 20 queries x 3 runs x up to 5 iterations of `claude -p`) was NOT
  run: not cheap. Description is 831 chars, trigger-form, names the failure symptoms agents actually hit.
- Lessons now folded into GIT_WORKFLOW (candidates for deletion by the lessons-curation writer, not deleted here):
  20260924T021505Z-UNSEATED-git-commit-path-f-fails-with, 20260924T033451Z-BENCH-git-add-deleted-path-after-git,
  20260924T182022Z-BENCH-bench-2026-09-24-git-commit, 20260928T191601Z-FOUNDRY-git-commit-path-refuses-brand-new,
  20260929T062905Z-UNSEATED-git-commit-paths-refuses-untracked-file, 20261002T193524Z-BENCH-background-subagents-running-read-only-git,
  20260928T153719Z-FOUNDRY-back-back-git-commit-rimflow-close, 20261008T022031Z-BENCH-git-fetch-from-10g-capped-seat,
  20261010T164936Z-BENCH-publish-runs-git-pull-rebase-autostash, 20261010T235838Z-BENCH-landing-commits-through-scratch-clone-because,
  20261011T070420Z-BENCH-land-sh-defaults-land-repo-home, 20261009T100707Z-FOUNDRY-land-sh-old-replayed-shared-head,
  20261011T125554Z-FOUNDRY-before-deleting-scratch-clone-check-untracked, 20260911T054544Z-UNSEATED-block-blanket-git-stage-py-has.
