# Git migration freeze — Phase 6 part B (2026-10-02)

Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.3, §4 row 6. Part A:
`design/RimMandrake/git_migration_drain_2026-10-02.md`. Mirror tool: `git_migration_publish_build_2026-10-02.md` §3.
Artpipe: `git_migration_phase5_artpipe_2026-10-02.md` §7. Owner authorized full implementation 2026-10-02.

**Status: DONE.** `D:\Luke\dev\RimMandrake` has no `.git`; it is the mirror export of origin/main
(`7f4eaffc6b16` at first sync), kept current by `rm-mirror.timer`. The artpipe daemon runs as
`rm-artpiped.service` from `/home/mandrake/rm/foundry`.

## Log (UTC)

- 08:02 started.
- 08:03 FOUNDRY window terminated (§1).
- 08:03 old artpipe daemon 1144945 SIGINT (active/ and pending/ held only .gitkeep); exited at once. 08:04 migrate delta started.
- 08:04 migrate done (40 s); rm-artpiped.service enabled+started; Artist WT profile → journalctl; probe job filed 08:04:53Z.
- 08:05 late-leftover check: 0 files (§3). 08:05 `.claude/worktrees` moved. 08:06 `.git` renamed (WSL `mv` got EACCES twice; PowerShell `Move-Item` succeeded). Mirror first sync starting.
- 08:10 mirror adopt done (3 min 39 s), clean; rm-mirror.timer enabled. Report committed.

## 1. Quiesce

Processes with cwd/fd under `/mnt/d/Luke/dev/RimMandrake` at 08:02Z (`/proc/*/cwd`, `/proc/*/fd`):
`Server` remote-control tile 1144321/1144329/1144504 (left: owner's phone link), artpipe daemon 1144937/1144945
(§2), FOUNDRY window 2070505 (bash) / 2070520 (claude), BENCH window 2070792/2070808, ChatGPTConsult
`broker.py --serve` 2088642 (cwd only, reader; left), and this agent's own shells.

- 🔴 **The brief's "old BENCH window pid ~2070808" is the ORCHESTRATING BENCH session** — this agent's
  process ancestry is `zsh 2462411 → claude 2070808 → bash 2070792`. Not killed. There is no separate idle
  BENCH window on this machine.
- FOUNDRY evidence: its transcript `a30d149c-…jsonl` last written 2026-10-01 22:54:41 PDT (05:54Z), its
  subagent files ≤ 22:45 PDT; last ledger event in `events/FOUNDRY.jsonl` = `game DOWN` at 05:45:03Z, file
  mtime 05:45Z; no children. Tree writes after 07:54Z (excluding `.git`, `.claude/worktrees`): 2 files —
  `infrastructure/artpipe/status/…` (daemon) and `design/INDEX.md` (mtime 08:02:23Z, `git status` clean:
  regenerated identical bytes). ⇒ idle >2 h. **SIGTERM 2070520 + 2070505 at 08:02:54Z.**

## 2. Artpipe cutover

- D:\ tree `infrastructure/artpipe/active/` and `pending/` held only `.gitkeep` at 08:03Z ⇒ `kill -INT 1144945`
  08:03:10Z; daemon exited at once (its WT tab shell 1144937 fell back to `zsh -l`, cwd D:\, harmless).
- `/home/mandrake/rm/foundry` already had the phase-5 code (`artpipe_state.py`, `state_dir.py`, `mirror.py`);
  pulled to `6b87accbe`. `artpipe_state.py migrate --from /mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe`:
  **40 s**, delta = 1 log file (nothing had finished since the first copy). `where` after: done 2,471 jobs,
  failed 61, `_withdrawn` 22, registry 1.70 MB, throughput 3.35 MB.
- **New daemon = systemd user service `rm-artpiped.service`** (`~/.config/systemd/user/rm-artpiped.service`:
  cwd `/home/mandrake/rm/foundry`, `ARTPIPE_STATE_DIR=/mnt/d/Luke/dev/_artpipe`, `bash -lc 'exec python3
  src/RimMandrake/Utils/artpipe/artpiped.py'` for the login PATH, `KillSignal=SIGINT`, `Restart=on-failure`,
  `WantedBy=default.target`). Enabled + started 08:04:24Z, main pid 2465095.
- Windows Terminal `Artist` profile would have started a second daemon from the D:\ tree ⇒ backed up
  `settings.json` → `settings.json.bak-artpipe-2026-10-02`, its commandline now
  `wsl.exe -d Ubuntu -- bash -lc "journalctl --user -fu rm-artpiped; exec $SHELL -l"` (only that profile
  touched; file re-parsed as JSON after the write). `install_wt_seat_profiles.py`'s ARTIST override changed to
  the same, so a future `--apply` cannot reintroduce it.
- **Probe job** `RM_ArtpipeCutoverProbe_20261002` (one 256² pebble icon, item `ART_PIPELINE_DAEMON_1`) filed with
  `fill_queue.py` from the FOUNDRY clone 08:04:53Z → claimed 08:04:54Z → **PASS 79 s** (codex) →
  `D:\Luke\dev\_artpipe\done\RM_ArtpipeCutoverProbe_20261002{.json,.manifest.json}` + PNG in
  `_artsrc\RM_ArtpipeCutoverProbe_20261002\`. `git -C /home/mandrake/rm/foundry status --short` = 0 lines.
- On start the daemon pruned 34 `_artsrc` scratch dirs older than 14 days (its normal housekeeping), which is why
  `_artsrc` reads 2,176 entries here vs the phase-5 doc's first-copy count.
- The D:\ tree's old `infrastructure/artpipe/{pending,active,done,failed,_artsrc,…}` are now untracked
  leftovers in the mirror (phase-5 §7.7: keep a week as backup, then delete).

## 3. Late leftovers

`find -newermt '2026-10-02 07:54:19Z'` over the D:\ tree (excluding `.git`, `.claude/worktrees`) at 08:05Z: 2 files —
`design/INDEX.md` (clean: regenerated identical bytes) and `infrastructure/artpipe/logs/artpiped_20260930_224139_1144945.log`
(gitignored; also copied to `_artpipe/logs/` by the migrate). Intersected with `git status --porcelain -uall`
(3,497 entries — the same count part A tarred): **0 tracked-dirty or untracked non-ignored late files ⇒ no
`leftovers-late.tar` written.** `git status --porcelain | wc -l` = **3,497** just before the freeze.

## 4. Freeze + mirror

- 08:05:48Z `mv .claude/worktrees → D:\Luke\dev\_rm_old_worktrees_2026-10\` (93 entries, 0.3 s).
- 08:06Z `.git → D:\Luke\dev\_rm_old_git_2026-10\`. ⚠️ WSL `mv` returned **EACCES twice** (no WSL process had
  an fd or cwd in `.git`; a Windows-side handle, likely the search indexer, is the suspect); PowerShell
  `Move-Item -LiteralPath 'D:\Luke\dev\RimMandrake\.git' -Destination 'D:\Luke\dev\_rm_old_git_2026-10'`
  succeeded at once (same volume ⇒ rename; objects 3.8 GB intact at the new path).
- `./mirror sync --seed /home/mandrake/rm/foundry` from the FOUNDRY clone (at `6b87accbe`, already carrying
  mirror.py), foreground: **adopt run 3 min 39 s** (08:06:15 → 08:09:54Z) — created `/home/mandrake/rm/mirror.git`,
  hashed the existing tree, landed `7f4eaffc6b16` (= `git ls-remote origin refs/heads/main`). No `MIRROR_STALE`.
- Clean check: `GIT_INDEX_FILE=/home/mandrake/rm/mirror.git/index.aaf029794a31 git --git-dir=/home/mandrake/rm/mirror.git
  --work-tree=/mnt/d/Luke/dev/RimMandrake status --porcelain --untracked-files=no` = **0 lines** (6 s). 800 untracked
  files remain (old artpipe queue dirs, Transient outputs, etc.; the mirror leaves untracked files alone).
  🔴 **Trap:** the same command WITHOUT `GIT_INDEX_FILE` reports 25,752 staged deletions — mirror.py keeps one
  index per target (`index.<sha1(target)[:12]>`), not the default `index`, so a bare `git --git-dir=… status`
  reads an empty index. `./mirror status` is the right check.
- `systemctl --user enable --now rm-mirror.timer` at 08:10:16Z; its first run: `already at 7f4eaffc6b16`, 1 s.
- `git -C /mnt/d/Luke/dev/RimMandrake rev-parse` → `not a git repository`. `find -name .git` finds only nested
  untracked clones/caches (`Transient/triposr_prototype/*/.git`, `_artsrc/*/.uv-cache/sdists-v9/.git`), none at
  the root. `~/dev` → `/mnt/d/Luke/dev` and `/mnt/d/Luke/dev/Rimworld` → `RimMandrake` both still resolve
  (`Rimworld/src/RimMandrake/Utils/claude_bounded.sh`, which the EMERGENCY window was launched through, is present).
- Consequences: the linked worktrees outside the tree (`/home/mandrake/wt_p3`, `D:\Luke\dev\RimMandrake-wt-handoff`,
  `-wt-livedeploy`, `D:\Luke\dev\wt_live2`, the `/tmp` pushwt) now point at a gitdir that moved and no longer work as
  git checkouts; their state is in the `archive/dirty/*` tags (part A). Sessions still running with cwd in D:\
  (orchestrating BENCH 2070808, Server tile, EMERGENCY's parent tree, broker.py) keep working as readers; any git
  call there now fails, which is the intended "no writers".

## 5. How to undo

    systemctl --user disable --now rm-mirror.timer
    powershell.exe -NoProfile -Command "Move-Item -LiteralPath 'D:\Luke\dev\_rm_old_git_2026-10' -Destination 'D:\Luke\dev\RimMandrake\.git'"
    mv /mnt/d/Luke/dev/_rm_old_worktrees_2026-10 /mnt/d/Luke/dev/RimMandrake/.claude/worktrees
    # the tree now holds origin/main 7f4eaffc6b16 (+ later timer syncs), not the pre-freeze HEAD: the old .git's
    # index will show those as changes; pre-freeze dirty state is in leftovers.tar / archive/shared-tree-dirty-* tag.
    systemctl --user disable --now rm-artpiped.service      # artpipe back to the WT tile:
    cp settings.json.bak-artpipe-2026-10-02 settings.json  # (Windows Terminal LocalState)

Keep `_rm_old_git_2026-10`, `_rm_old_worktrees_2026-10` and `_rm_shared_tree_leftovers_2026-10` until the owner says delete.
