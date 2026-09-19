# BENCH_REBOOT_HANDOFF_202609160549 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609160516`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**A state assertion and the screen can both be right and disagree, and our
validation system only ever read the state.** The pit mod's
`expect_pawn_despawned` PASSES — the pawn genuinely leaves the map — while
`Building_OpenPit` draws its first occupant over a vanilla 64px `TrapSpikeArmed`
placeholder. So the player sees someone standing in a box labelled Pit while
every assertion is green, and `modcheck_status.json` recorded **Pits as GREEN**.

Measured this session: `component()` had no visual-expectation parameter, the
model judge that `mod_validation_runner_spec.md` §2 rules for **does not exist**
anywhere in `modcheck/`, and `runner.py:205` computes `all_green` from state
verdicts alone — so screenshots were captured and never read, and the 2026-09-12
ruling "neither alone passes a component" was unenforced. The pit's own walk had
written down "nothing here is visual-only".

The fix is designed, built and tested:
`design/RimMandrake/north_star_validation_spec.md`.

## What the owner should see

**1. Five minutes of his time unblocks the whole thing.**
`design/validation_walks/RimMandrake/Pits.md` now carries a **DRAFT** `## north
star` — 12 must-show lines in five mechanic groups, drafted from his own recorded
words. He validates, edits or rejects it. It binds nothing until he does. Native
path: `D:\Luke\dev\Rimworld\design\validation_walks\RimMandrake\Pits.md`

**2. His four rulings of 2026-09-15 are recorded** (unit = one whole mod; lives in
the walk file; enforcement per-mod as he validates; model judges every run with
his eyes required before a mod's first GREEN). He chose per-mod over a finer unit
with the sprawl cost stated — the mitigation is in spec §1: the FILE is per-mod,
every LINE names one mechanic.

**3. A shipped sprite is wrong and a numeric gate passes it.**
`Gizka_north.png` scores 0.845 mirror-symmetry — passing `art_checks`'
`SYMMETRY_MIN_NS` of 0.80 — while being an unmistakable side profile facing
right. Confirmed by looking. This is `ARTPIPE_FACING_COHERENCE_1` on a live
asset, and no threshold fixes it.

**4. Shipped with a flag raised:** I committed
`src/RimMandrake/Utils/art_checks.py`, which was sitting uncommitted in the
shared tree and blocking `git pull --rebase`. I could not attribute the work, so
it is committed as written; only the false-negative comment is mine (`49b520734`).
He can veto.

**5. TOYFIG is gone** as he ordered — 201 files, `63d03b9c6`. That included
revoking `ART_PAINTERLY_RESTORATION_1`'s "preserve the cartoonish craft as a
selectable option" and deleting `STYLE_CARTOONISH.md`, which was an earlier
instruction of his that his 2026-09-15 order supersedes.

## What is half-done, and where it stops

**Half-done: the north-star modules exist and are tested, but nothing calls
them.** `runner.py` still computes `all_green` from state verdicts alone, so a
`modcheck run` today would still report the old GREEN. This is deliberate — the
modules landed with 22 passing offline checks before touching the runner's
verdict path.

**Exact next action:** claim `NORTH_STAR_RUNNER_WIRING_1` and work its `## spec`.
Its item file lists what is already built so nobody rebuilds it. Six numbered
pieces; the smallest is item 6 (`northstar.parse` returns must-show ids but the
judge needs `{id: prose}` — the regex already captures the line).

Ordering that matters:
1. `NORTH_STAR_RUNNER_WIRING_1` — no owner time, blocks the value of everything else.
2. `NORTH_STAR_PIT_PILOT_1` — needs his validation first, then bridge. **This is
   the falsification test: if the pit does not go red, the design failed.**
3. `NORTH_STAR_WALK_AUTHORING_1` (77 walks, his vision) and
   `VALIDATION_SCRIPT_BACKFILL_1` (59 missing scripts, no owner time) run in
   parallel — neither blocks the other, because enforcement is per-mod.

**Not started, and left alone deliberately:** the brainstorming I was in when he
went afk had reached its design stage; the spec IS that design written up, so the
architectural path's remaining step is his review of the spec, not more questions.

## Traps learned

- 🔴 **A green modcheck verdict currently proves nothing about appearance.** Two
  of 14 mods are GREEN and one of them (Pits) is a mod the owner rejected on
  sight. The Pits GREEN came from `MODCHECK_RUNNER_SWAP_LIVE_PROOF_1` on config
  `min+Pits` — a run proving the RUNNER worked, never a judgement of the pit.
  Read the `config` and item on a verify event before trusting a GREEN.
- **`handoff.py` defaults the seat to FOUNDRY** when `RIMFLOW_SEAT` is unset, and
  each Bash call is a fresh shell, so an `export` from an earlier call does not
  carry. It silently wrote `FOUNDRY_REBOOT_HANDOFF_…` for me; I deleted it and
  re-ran with `RIMFLOW_SEAT=BENCH` inline. Prefix the var on the same command.
- **BSD `xargs` has no `-a`.** `xargs -a file git rm` fails on macOS and the
  whole compound is refused, so an earlier "deleted 148 files" step had in fact
  deleted nothing. Use `tr '\n' '\0' < file | xargs -0`. Verify a bulk delete by
  re-measuring, never by the command's exit.
- **The commit hook requires the pathspec on `git commit` itself**, not just on
  `git add`, and it refuses the whole compound — so anything chained BEFORE the
  commit also does not run. Write the message to a file first.
- **`grep -rniel` does not list filenames.** The `-l` after `-e` was ignored and
  the command returned 41.7 MB of matching lines. For "which files mention X",
  use the Grep tool or `-rl`.
- **A geometric image check can pass what the eye rejects, and that is not a
  tuning problem.** `facing_symmetry` is now documented in place with its Gizka
  false negative. Treat it as evidence a facing is WRONG, never that it is RIGHT.
- **`Image.getdata()` is deprecated** in this Pillow (removal 2027-10-15) in
  favour of `get_flattened_data()` — which is why the uncommitted `art_checks.py`
  used the latter. Not a bug; do not "fix" it back.

All of these are in `LESSONS_INBOX.md` or the relevant file's own comments.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (4) — the next seat's queue

- `NORTH_STAR_RUNNER_WIRING_1` — Wire the north-star modules into modcheck's verdict: runner consults the visual floor and the judge, modcheck validate CLI, the new GREEN definition, 
- `NORTH_STAR_PIT_PILOT_1` — Pit north-star pilot: owner validates the DRAFT checklist already drafted into the Pits walk, then shows= is wired into Pits/validation.py and the run
- `NORTH_STAR_WALK_AUTHORING_1` — Author must-show sections across the 77 validation walks: agent drafts candidate lines from each walk's must-be-true plus sprites and settings, owner 
- `VALIDATION_SCRIPT_BACKFILL_1` — Write validation.py for the 59 mods that have a walk and no script - state assertions now, shows= added per mod as each checklist is validated, so thi

## Commits

```
49b520734 facing_symmetry: record the measured false negative next to its threshold
d4462ee89 Four north-star items, and the pit as the falsification test
0e03d1bed North stars: bind a mod's intended experience to its validation run
2227c41ad chore(sync): laptop 2026-09-15T22:24:36-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
63d03b9c6 No trace of cartoon-generating art — TOYFIG terminated by owner
```

## Game / bridge / tree state at wrap

- <could not run /Users/mandrake/dev/RimMaster/game: [Errno 13] Permission denied: '/Users/mandrake/dev/RimMaster/game'>
- Bridge: FREE    since 2026-09-14T18:25:31Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
```

