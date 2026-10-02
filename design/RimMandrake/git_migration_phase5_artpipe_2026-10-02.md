# Git migration Phase 5 — artpipe state out of the repo (2026-10-02)

Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.3 (artpipe daemon), §2.4 (artpipe row).

## 1. How jobs flow today

Read from `src/RimMandrake/Utils/artpipe/{artpiped,fill_queue,common,artreg}.py`.

- `fill_queue.py` writes `pending/<id>.json` (O_EXCL-style `os.link`, refuses an id already in
  pending/active/done/failed) and, only against the real queue, emits `registered`+`queued` events
  through `artreg` into `registry.jsonl`.
- `artpiped.py` claims by `os.rename` pending→`active/`, runs one worker subprocess per job
  (`codex_image.py` or `gemini_image.py`) with cwd = the per-job scratch dir `_artsrc/<id>/`, the
  worker writes `_artsrc/<id>/<id>.png`; the daemon re-validates, then moves the job JSON to `done/` or
  `failed/` beside `<id>.manifest.json`, appends a line to `throughput.jsonl`, and records the outcome
  through `artreg` (`registry.jsonl`, re-rendered `art_status.{json,html}`). Crash recovery:
  `active/` orphans → `pending/`. Logs → `logs/`, live status → `status/artpiped_<pid>.json`.
- **The daemon never writes into `src/`.** The finished PNG stays in `_artsrc/<id>/<id>.png`. Wiring it
  into a mod's `Textures/` is a separate, human-ruled step (review sheet → keep), done today by
  per-biome scripts (`src/RimMandrake/LanternDeeps/wire_art.py`) or by hand.
- Job `reference` paths are absolute and point at `/mnt/c` game textures (6) or `/mnt/d` (2) — 2,463 of
  2,471 done jobs have none — so a daemon running from an ext4 clone still hands codex.exe only
  Windows-drive paths (reference) and a Windows-drive cwd (`_artsrc/` in the state dir).

## 2. State vs outputs

| path under `infrastructure/artpipe/` | kind | where now |
|---|---|---|
| `pending/ active/ done/ failed/` | queue state, daemon-written | state dir, untracked |
| `_artsrc/` | worker outputs + per-job scratch (545 MB; was already gitignored except 35 force-added PNGs) | state dir |
| `_withdrawn/` | jobs pulled by hand from the queue | state dir |
| `registry.jsonl` (+ `.lock`), `art_status.{json,html}` | `artreg` record + its render; written by the daemon every job | state dir |
| `throughput.jsonl` (+ `.reservation.lock`) | daemon append-only cost/meter log | state dir |
| `logs/ status/ daemon_run_*.log` | daemon logs/live status | state dir |
| `README.md BACKGROUND_TEMPLATE*.md art_lists/ _art_lists/ legibility_*.json drawsize_backfill.json .gitignore` | authored inputs/config | stay tracked in the repo |

The plan's §2.4 row named only the four queue dirs. `registry.jsonl`/`throughput.jsonl`/`art_status.*`
move too because the daemon writes them on every job: left tracked, the daemon's own clone (FOUNDRY's)
would be permanently dirty and every FOUNDRY publish would race it. **Cost: `registry.jsonl` holds owner
verdicts (via `apply_verdicts.py`) and is no longer in git.** Its last tracked copy stays in history;
follow-up: a periodic snapshot of `registry.jsonl` somewhere durable (not filed by this pass).

## 3. Other readers/writers (all repointed to the resolver)

- artpipe package: `artpiped.py`, `fill_queue.py`, `artreg.py`, `console.py`, `make_verdict_sheet.py`,
  `build_flora_legibility_sheet.py`, `apply_verdicts.py` (via artreg) — all read `common.*`.
- `src/RimMandrake/LanternDeeps/{wire_art,build_art_sheet,build_species_sheet}.py` — hardcoded
  `REPO_ROOT/infrastructure/artpipe/{_artsrc,done,failed}`.
- `infrastructure/dashboards/hub/{regen_hub,hub_check,build_standalone}.py` — `art_status.json`.
- Docs: `CLAUDE.md` ("Check for existing regenerated art", and the empty-dir trap line),
  `skills/generating-rimworld-sprites/SKILL.md` ("Search before queuing"), `infrastructure/artpipe/README.md`.
- Left alone: `Transient/` one-off scripts (≈14-day shelf life), handoffs, closed items, docstring examples
  in `art_legibility.py`/`art_zoom_sim.py`, placeholder generators' prose provenance.

## 4. The state-dir resolver

`src/RimMandrake/Utils/artpipe/state_dir.py` (stdlib only, import-cheap): `$ARTPIPE_STATE_DIR` →
`/mnt/d/Luke/dev/_artpipe` when `/mnt/d/Luke/dev` exists → `<clone's parent>/_artpipe` (a Mac:
`~/dev/_artpipe`, normally absent — readers call `state_dir.require()`, which refuses rather than answer
"nothing found"). `common.QUEUE_ROOT` = that dir; `common.CONFIG_ROOT` = the tracked
`infrastructure/artpipe/`. Repo paths (skills scripts, validator, legibility config) still derive from
`__file__`, so the daemon runs unchanged from `/home/mandrake/rm/foundry`.

The state dir stays on the Windows drive on purpose: the codex worker's cwd is `_artsrc/<id>/` and
codex.exe fails from an ext4 cwd (plan §2.3).

Initial copy, 2026-10-02 (`artpipe_state.py migrate`, 9 min, source untouched), counts equal in a
separate python walk: pending 1 · active 1 (both `.gitkeep`) · done 4,943 · failed 130 · `_artsrc`
2,415 · `_withdrawn` 40 · logs 19 · `registry.jsonl` 10,862 lines · `throughput.jsonl` 3,536 lines, plus
`art_status.*` and 11 `daemon_run_*.log`. Probe: `find brindeth` → done json + manifest + `_artsrc/RM_Brindeth_a/`
+ 4 registry lines.

## 5. Outputs reaching src/ — collect

The daemon writes nothing into `src/` today or after this change, so there is no "direct write from the
FOUNDRY clone" question to settle: running it from FOUNDRY's clone would not dirty FOUNDRY's tree at all
once the state is out. Its output contract already is "PNG in `_artsrc/<id>/` + `done/<id>.manifest.json`".

`artpipe_state.py collect` is the seam a seat uses in its own clone:

    python3 src/RimMandrake/Utils/artpipe/artpipe_state.py collect <job_id> --to src/<Mod>/Textures/…/X_east.png
    python3 src/RimMandrake/Utils/artpipe/artpipe_state.py collect --from-jobs   # jobs carrying "install_to"

It refuses a destination outside the clone's `src/` and a job with no `done/` manifest (unless
`--allow-failed`), copies, appends `{job_id, dest, sha256, ts, clone, host}` to `<state>/collected.jsonl`,
and prints the paths to commit (explicit-path commit as always). `install_to` is an optional job field; no
filer sets it yet. Per-mod wiring scripts (`LanternDeeps/wire_art.py`) keep working: they read the state dir
through the resolver. `find <term>…` replaces "search `infrastructure/artpipe/done/`" in the docs.

## 6. Launcher

`src/RimMandrake/Utils/install_wt_seat_profiles.py`: `ARTIST_HOME = SEAT_CLONES["FOUNDRY"]`, command
`export ARTPIPE_STATE_DIR=/mnt/d/Luke/dev/_artpipe && python3 src/RimMandrake/Utils/artpipe/artpiped.py`.
**Code only — NOT applied to the live Windows Terminal `settings.json`.** The running daemon (pid 1144945,
started 2026-09-30 22:41 from the D:\ tree) was not touched, and the live `Artist` profile still says
`cd /mnt/d/Luke/dev/RimMandrake`, so a fleet reopen before cutover restarts the OLD arrangement — which
stays consistent (old code, old queue). Applying is cutover step 4.

Until cutover, jobs filed from an ext4 clone with this code land in `_artpipe/pending/` and wait; before
this change such filings landed in the clone's own `infrastructure/artpipe/pending/`, where no daemon
ever looked — so nothing regresses.

## 7. Cutover steps (drain)

1. **FOUNDRY's clone has this code**: `git -C /home/mandrake/rm/foundry merge-base --is-ancestor <sha> HEAD`
   (FOUNDRY pulls it itself if not). Old code there would ignore `ARTPIPE_STATE_DIR` and use the clone's
   own `infrastructure/artpipe/`.
2. **Drain the old daemon**: wait until the D:\ tree's `infrastructure/artpipe/active/` holds no `*.json`
   (`cd /mnt/d/Luke/dev/RimMandrake && python3 src/RimMandrake/Utils/artpipe/artpiped.py --status`), then stop
   it with Ctrl+C in the Artist tile or `kill -INT <pid>` (by PID, never `pkill -f`). A job still active is not
   lost either way: step 3 copies it into `_artpipe/active/` and the new daemon's reconcile requeues it.
3. **Final delta**: `python3 /home/mandrake/rm/foundry/src/RimMandrake/Utils/artpipe/artpipe_state.py migrate
   --from /mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe` — idempotent (~9 min stat walk on drvfs): copies
   what finished since the first copy, advances jobs pending/active→done/failed without regressing any,
   unions `registry.jsonl`/`throughput.jsonl` by line, never deletes from the source.
4. **Repoint and start**: `python3 /home/mandrake/rm/foundry/src/RimMandrake/Utils/install_wt_seat_profiles.py
   --apply` (writes `settings.json.bak`), then open the `Artist` profile (or reopen the fleet).
5. **Verify a job flows**: `artpiped.py --status` shows the new pid; file one real job with `fill_queue.py`
   from any clone and watch it reach `_artpipe/done/`; `artpipe_state.py where` counts move; and
   `git -C /home/mandrake/rm/foundry status --short infrastructure/artpipe` stays empty.
6. **Collect** any art already ruled keep: `artpipe_state.py collect <job> --to src/…` in the seat's clone,
   commit the printed paths.
7. Before the Phase 6 mirror freeze: the D:\ tree's old queue dirs are now untracked leftovers — keep as a
   backup for a week, then delete. Follow-up not done here: a durable snapshot of `registry.jsonl` (owner
   verdicts), which is no longer in git.
