# 10 — Disk layout design: using Archmagi's other drives (weekly cleaning 2026-10-11)

Design only. **Nothing was deleted, moved, resized or mounted by this pass.** Another agent is deleting stray clones
in parallel, so the WSL-side sizes are a 09:32 PDT snapshot and are already falling.

Owner (typed): *"We should do (1) [delete clean clones + compact the WSL disk], but we also need to look at how to handle
this better. This machine has MANY large SSD's beyond C to use. How can we leverage that?"*

Every number here was measured by a command on 2026-10-11 unless marked UNMEASURED. All commands were read-only
(`Get-PhysicalDisk`, `Get-Disk`, `Get-Partition`, `Get-Volume`, `Get-PSDrive`, `wsl.exe -l -v / --version / --help`,
`fsutil sparse queryflag`, the Lxss registry key, `df`, `du`, `findmnt`, and `Get-ChildItem | Measure-Object`).

## 1. Hardware (measured)

| disk # | model | media / bus | size | letter | label | used | free | health |
|---|---|---|---|---|---|---|---|---|
| 1 | Kingston FURY Renegade SFYRD4000G | SSD / **NVMe** | 3.7 TB | **C:** | Windows 11 | 1,622 GB | 2,103 GB | Healthy |
| 2 | Kingston FURY Renegade SFYRD4000G | SSD / **NVMe** | 3.7 TB | **D:** | Drive | 1,883 GB | 1,843 GB | Healthy |
| 3 | Kingston FURY Renegade SFYRD4000G | SSD / **NVMe** | 3.7 TB | **E:** | Drive | **0 GB** | **3,726 GB** | Healthy |
| 0 | WD Red Pro WD142KFGX | **HDD** / SATA | 13 TB | **F:** | Drive | ~1 GB | **13,038 GB** | Healthy |
| — | (virtual) | Google Drive for desktop | — | G: | Google Drive | — | — | — |

What this means:

- **The "many SSDs beyond C" are two**: D: (half full) and **E: (a whole 3.7 TB NVMe, completely empty)**. Plus **F:, a 13 TB
  spinning disk, also empty**. All three NVMe drives are the same model, so moving work from C: to E: buys **isolation and
  room, not speed** — E: is exactly as fast as C:.
- G: is the Google Drive client, not a disk. Never put a git repo or the WSL disk on it (Drive replicating `.git` corrupts it).

## 2. WSL: distros, the disk image, version, `.wslconfig` (measured)

| fact | value |
|---|---|
| distros | one: `Ubuntu`, WSL 2, default, running |
| WSL version | 2.7.11.0, kernel 6.18.33.2-2, Windows 10.0.26200 |
| disk image | `C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx` (Lxss `BasePath`) |
| image file size | **908.1 GB** on C: |
| ext4 inside | 1007 G capacity; **502 G used at 09:32** (541 G at 09:00 — the clone deletion is in progress) |
| **so C: holds ~400 GB of space Linux has already freed** | and the gap grows as the other agent deletes |
| sparse? | **`This file is NOT set as sparse`** (fsutil) |
| `.wslconfig` | `memory=36GB`, `swap=16GB`, `[experimental] autoMemoryReclaim=gradual`, **`sparseVhd=true`** |
| root mount | `/dev/sdd ext4 rw,relatime,discard` — Linux already issues discards on delete |
| `/etc/wsl.conf` | `systemd=true`, `default=mandrake` |
| Hyper-V tools | `Optimize-VHD` cmdlet **is installed**; this shell is **not elevated** (`Get-VHD` refused: permission) |
| `wsl --manage` options present | `--move <Location>`, `--set-sparse <true|false>`, `--resize <size>`, `--set-default-user` |
| keep-alive | Windows task `\WSL Keepalive` (Ready) — **it restarts WSL**, so it must be disabled for any downtime |
| other vhdx | Claude desktop's VM bundle under `C:\Users\Mandrake\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\` (8.6 + 0.6 GB) — not ours |

**The key finding:** `.wslconfig` already says `sparseVhd=true`, but that setting only applies to disk images **created
after** it was set. The existing image predates it and is measured **not sparse**. That is why it never shrinks: Linux
discards freed blocks (`discard` is on), and a non-sparse vhdx simply ignores them. One command fixes the future
(`wsl --manage Ubuntu --set-sparse true`, distro stopped); one compaction fixes the past.

## 3. Heavy consumers by location (measured)

**Inside WSL (ext4 on C:, 502 G used at 09:32)** — detail and per-clone safety in `05_git_and_disk.md` §5.

| path | size | kind |
|---|---|---|
| `/home/mandrake/.seat-tmp` (scratch clones, ledger_sync temp clones, session scratchpads) | **342 G** (382 G at 09:00, being cleaned) | churn — the thing that fills the disk |
| `/home/mandrake/rm/bench`, `foundry` | 18 G + 14 G | seat clones (hot git) |
| `/home/mandrake/rm/foundry_old_20261011` | 17 G | holds 1 unlanded commit (05 §7c) |
| `/home/mandrake/rm/stv`, `rm/scratch` | 7.2 G + 7.1 G | old clones |
| `/home/mandrake/rm/store.git`, `mirror.git` | 6.3 G + 6.0 G | shared object store, mirror (by design) |
| `/home/mandrake/ComfyUI` | 27 G | parked imagegen track |
| `/home/mandrake/.venvs`, `.cache` | 27 G + 13 G | regenerable |
| `/home/mandrake/.claude` (transcripts) | 7.8 G | 30-day cleanup already works |
| `/home/mandrake/wt_p3` | 4.1 G | worktree era |
| `/tmp` (tmpfs, RAM) | 18 G cap | the 10-06 ENOSPC |

**Windows side**

| path | size | files | kind |
|---|---|---|---|
| `D:\Luke\dev` (total; `Rimworld` is a symlink to `RimMandrake`, counted once here) | **~469 GB** | 3.26 M | |
| — `D:\Luke\dev\_rm_old_worktrees_2026-10` | **373.3 GB** | 2.68 M | **93 `agent-*` worktrees from before worktrees went OFF (10-02). Not in report 05.** Cold. |
| — `D:\Luke\dev\_rmscratch` | 29.1 GB | 114 k | scratch (edge_gate, codex staging, save backups) |
| — `D:\Luke\dev\MandrakeAudio` | 22.2 GB | 2,950 | another project |
| — `D:\Luke\dev\RimMandrake` | 11.1 GB | 118 k | read-only mirror of origin/main |
| — `D:\Luke\dev\Custos` | 9.3 GB | | another project |
| — `D:\Luke\dev\_rmbuild` | 6.7 GB | 256 k | C# build staging (Windows `dotnet` needs it Windows-side) |
| — `wt_live2`, `RimMandrake-wt-handoff`, `RimMandrake-wt-livedeploy`, `_rm_old_git_2026-10` | 4.2 + 4.0 + 4.0 + 4.1 GB | | worktree-era leftovers |
| — `D:\Luke\dev\_artpipe` | 0.97 GB | | artpipe state (05) |
| `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios` | 19.0 GB | 6,829 | Screenshots 9.3 G, DefDump 4.4 G, Saves 3.7 G (05) |
| `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100` | 10.5 GB | 248 k | Workshop mods |
| `C:\Program Files (x86)\Steam\steamapps\common\RimWorld` | 1.9 GB | 15.8 k | game + our deployed Mods |
| WSL `ext4.vhdx` | 908.1 GB | 1 | **the biggest single thing on C:** — ~56% of C:'s 1,622 GB used |

## 4. Design: what lives where

### 4a. Principles (why each thing goes where it goes)

1. **Git and Python tooling stay on ext4 inside WSL.** drvfs (`/mnt/c`, `/mnt/d`) is ~2 s per `git status` and is where
   stale-read bugs came from (memory `drvfs-stale-reads-mimic-revert`). Moving clones "to a Windows drive" as plain NTFS
   folders would be a big regression. Using another drive means **putting an ext4 disk image on it**, not a folder.
2. **Windows-side tools need Windows-side paths**: `_rmbuild` (Windows `dotnet`), `_rmscratch\codex` (codex.exe), the game's
   `Mods` folder, the mirror, `_artpipe`. These stay on NTFS. They are not the problem (D: has 1.8 TB free).
3. **Churn gets its own blast radius.** The two disk incidents (10-06 tmpfs, 10-11 276 GB clones) were both agent churn.
   Churn should never be able to fill the drive that Windows, the pagefile, Steam and RimWorld live on (C:).
4. **Cold bulk goes to the HDD (F:).** 13 TB, empty, slow but fine for archives that are read rarely.
5. **No disk image ever again without sparse.** Every vhdx we own is set sparse, so freed space returns on its own.
6. **SQLite (telemetry) lives on ext4, never on drvfs.** SQLite's file locking and WAL are unreliable over WSL's 9p/drvfs;
   the telemetry DB (design 08) belongs at `~/.local/share/rimpulse/` inside WSL. A Windows-side Grafana reads it through
   an exporter or `\\wsl$`, never by putting the DB on D:.

### 4b. Target layout

| drive | role | what goes there |
|---|---|---|
| **C:** NVMe | Windows, Steam, RimWorld, appdata | unchanged; **the WSL disk image leaves** (option A) or stops growing (option B) |
| **E:** NVMe (empty) | **WSL drive** | `E:\WSL\Ubuntu\ext4.vhdx` — the whole distro, sparse, resized to e.g. 2.5 TB so the ext4 cap stops being the near limit |
| **D:** NVMe | Windows-side working set | repos `D:\Luke\dev`, mirror, `_rmbuild`, `_rmscratch` (hot part), `_artpipe` |
| **F:** HDD | **cold archive** | `F:\Archive\rm_old_worktrees_2026-10` (373 GB), RimWorld screenshot archive, old save backups, parked ComfyUI, `wsl --export` backups |

**Why the whole distro on E:, rather than a second disk mounted beside it** — see owner question Q2. Short version: a second
mounted VHDX (`wsl --mount --vhd`) needs an **elevated** command after every WSL start, and if it is not mounted the
agents silently write into the empty mount-point directory on the root disk — the exact failure we are trying to stop.
Moving the whole distro is one command, survives restarts with no new moving parts, and takes churn off C: entirely.

### 4c. The scratch-clone volume, done without a second disk

The dedicated "scratch/clones volume" idea is achieved inside the one ext4 disk by **quota by tooling, not by partition**:
`scratch_clone.py` becomes the only way to make a clone, it records a manifest, and its `gc` reaps clean landed clones
(05 §7b). Paired with sparse, deleted clones return space to E: within minutes. If the owner wants a hard wall anyway
(option B in Q2), the second VHDX on D: or E: mounted at `/home/mandrake/.seat-tmp` with a mount guard is the design.

### 4d. Build staging and scratch

`_rmbuild` (6.7 GB, 256 k files) and `_rmscratch` stay on D:. They need Windows paths, D: has room, and moving them gains
nothing. Their problem is retention (05 §7b), not placement.

## 5. Procedures (owner-scheduled — every one of these stops ALL of WSL)

⚠️ **Every procedure below kills every Claude seat, every systemd timer (memwatch, pulse, objstore, mirror, Lodestar
sweep) and the artpipe daemon.** Remote Control sessions drop with them. RimWorld itself keeps running (it is Windows),
but nothing can drive the bridge until WSL is back. **The owner schedules it; no agent starts it.**

### 5.0 Shared pre-flight (all procedures)

1. All seats hand off (`HANDOFF READY`), every commit landed; bridge released (`rimflow bridge release`).
2. Clone cleanup finished (the other agent's pass), so the image holds as little as possible.
3. In WSL: `sudo fstrim -av` (belt-and-braces; `discard` is already on, but a trim makes compaction see every free block).
4. In an **elevated** PowerShell:
   `Disable-ScheduledTask -TaskName "WSL Keepalive"` — otherwise it restarts WSL mid-procedure.
5. `wsl --shutdown`, then `wsl -l -v` must show `Ubuntu  Stopped`.

### 5.1 Compaction in place (the owner's choice "(1)", keeps the image on C:)

Elevated PowerShell, after 5.0:

```
$v = "C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx"
(Get-Item $v).Length / 1GB                      # before
Optimize-VHD -Path $v -Mode Full
(Get-Item $v).Length / 1GB                      # after: expect roughly ext4-used, ~500 GB or less after cleanup
wsl --manage Ubuntu --set-sparse true           # stop it re-growing (see caveat)
Enable-ScheduledTask -TaskName "WSL Keepalive"
wsl -d Ubuntu -e true                           # boots it; systemd timers resume
```

If `Optimize-VHD` is unavailable or errors, the equivalent with built-in `diskpart` (elevated):

```
diskpart
  select vdisk file="C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx"
  attach vdisk readonly
  compact vdisk
  detach vdisk
  exit
```

- **Downtime: UNMEASURED.** A full pass reads the whole 908 GB file; on this NVMe expect roughly 10–40 minutes plus seat
  relaunch. Run it once, time it, write the number into this doc.
- **Expected gain:** ~400 GB+ back on C: (908 G image vs ~500 G used, more as cleanup completes).
- ⚠️ **`--set-sparse` caveat (UNMEASURED on 2.7.11):** some earlier WSL builds refused it with a "potential data
  corruption" warning and an `--allow-unsafe` escape. **If it refuses, do not pass `--allow-unsafe`**; fall back to
  compacting on a schedule (Q3 option c) and the disk watch below telling us when.

### 5.2 Move the distro to E: (recommended; includes compaction for free)

Two ways. Both after 5.0.

**(a) `--move` — simplest, one command, keeps the image byte-for-byte:**

```
New-Item -ItemType Directory E:\WSL\Ubuntu
wsl --manage Ubuntu --move E:\WSL\Ubuntu
wsl --manage Ubuntu --set-sparse true
wsl --manage Ubuntu --resize 2500GB             # optional: lift the 1007 G ext4 cap
```

Copies whatever the file size is, so **compact first (5.1)**, then move: ~500 GB NVMe-to-NVMe instead of 908 GB.
Downtime UNMEASURED; NVMe-to-NVMe at 1–3 GB/s suggests minutes for the copy itself.

**(b) export / import — rewrites the filesystem fresh, and doubles as a full backup on F::**

```
wsl --export Ubuntu F:\Archive\wsl\ubuntu_2026-10-xx.tar          # full backup on the HDD
# verify the tar exists and its size is ~ext4-used before the next line — it is the destructive one
wsl --unregister Ubuntu
wsl --import Ubuntu E:\WSL\Ubuntu F:\Archive\wsl\ubuntu_2026-10-xx.tar --version 2
```

The new image is created fresh, so it is compact and (with `sparseVhd=true` in `.wslconfig`) sparse from birth. The
default user survives because `/etc/wsl.conf` sets `default=mandrake`. **Slower** (tar to a spinning disk and back: ~500 GB
at ~200–250 MB/s each way, so likely 1–1.5 h; UNMEASURED) and it has one irreversible step (`--unregister`), protected
only by the verified tar. Its advantage is the backup, which today does not exist anywhere.

**After any move, check:** `wsl -l -v` (Running), `df -h /`, `systemctl --user list-timers` (six `rm-*` timers), a seat
launches, `git -C /home/mandrake/rm/bench status` is fast, and the Lxss `BasePath` now points at `E:\WSL\Ubuntu`.
Windows paths that refer **into** WSL (`\\wsl$\Ubuntu\...`) are unaffected by a move.

### 5.3 Cold archive to F: (no WSL downtime)

`robocopy` the owner-approved cold sets to `F:\Archive\…` with `/MOVE` only after a verified copy (`/L` dry run first,
then a file-count and byte-count compare). First candidate: `D:\Luke\dev\_rm_old_worktrees_2026-10` (373 GB, 93 old
agent worktrees). Then screenshots older than 30 days and the `saves_backup_*` copies (Q4). Moving is the owner's call;
deleting is a separate one.

## 6. Monitoring and retention

### 6a. Disk watch — extends `memwatch.py` and the hourly `scratch_clone.py sample` (no new timer)

`rm-memwatch.timer` runs every minute (`src/RimMandrake/Utils/memwatch.py --no-host`); `rm-objstore.timer` runs
`scratch_clone.py sample` hourly and already records `disk_free_bytes` for `/`. Add:

| metric | source | cadence | warn / critical |
|---|---|---|---|
| per-volume free: `/`, `/mnt/c`, `/mnt/d`, `/mnt/e`, `/mnt/f` | `os.statvfs` | 1 min | `/` < 150 G / < 60 G; C: < 200 G; others < 10% |
| vhdx file size and sparse flag | `powershell.exe Get-Item` + `fsutil sparse queryflag` (Lxss `BasePath`, so it follows a move) | **hourly** (powershell steals focus, memwatch's own `--no-host` note) | image − ext4-used > 150 G and not sparse → "compaction due" |
| clone count and bytes | walk `~/.seat-tmp`, `~/rm/scratch` for top-level clones (a `.git` with a sibling working tree; stop descending once found — a raw `find -name .git` at depth 5 returned **356** today, which counts nested/inner entries, not clones) | hourly | > 4 clones or > 60 G |
| growth rate and days-until-full | linear fit over the last 24 h of `/` used from the samples file | hourly | days-until-full < 7 / < 2 |
| top-5 growers | daily `du -s` of `~/.seat-tmp/*`, `D:\Luke\dev\_rmscratch\*` | daily | report only |
| loose objects per seat clone | `git count-objects -v` | hourly | > 20,000 |

Samples append to `~/.seat-tmp/disk_samples.jsonl` (rotate at 20 MB like memwatch) — or straight into the telemetry
SQLite once design 08 lands (on ext4, §4a.6). **RimPulse**: one status line (`/ 455 G free · image 908 G (not sparse) ·
clones 12 / 140 G · full in 19 d`), a red alert on any critical, and a line in the 06:00 / 17:30 `rm-pulse-digest`.

### 6b. Retention per source

| source | rule | enforcer |
|---|---|---|
| scratch clones | auto-reaped **only** when older than 24 h AND every local commit is on origin/main (patch-id) AND **0 modified, 0 untracked** (the 10-11 lost-prose lesson); anything else is listed, never deleted | `scratch_clone.py gc`, daily |
| `ledger_sync.py` temp clones | `try/finally: shutil.rmtree` (a code bug today, `ledger_sync.py:170`) | code fix |
| session scratchpads `~/.seat-tmp/<SEAT>/claude-1000/<session>` | deleted when the session's transcript is > 3 days idle AND it holds no clone that fails the clone rule above | same gc |
| tmpfs `/tmp` | watched at 70 / 90% (exists) | memwatch |
| RimWorld `Screenshots` | > 30 d moved to `F:\Archive\rimworld_screenshots\` (or deleted — Q4) | weekly job, Windows side |
| `D:\Luke\dev\_rmscratch` | `codex\<job>` removed after copy-back; everything else > 14 d listed weekly | code fix + weekly list |
| save backups (`saves_backup_*`, `Saves_backup_*`) | listed after 14 d; keeper saves never touched (owner rule) | weekly list |
| worktree-era leftovers on D: | one-time archive to F: (Q4) | owner |
| WSL image | sparse; compaction only if the watch says sparse failed | watch |
| WSL backup | monthly `wsl --export` to `F:\Archive\wsl\`, keep 2 — **only if Q3 picks it**, it needs the same downtime | owner-scheduled |

## 7. Owner questions

**Q1. Where does the WSL disk live from now on?**
- (a) **Move it to E: (the empty NVMe)** — churn can never again fill the drive Windows and RimWorld run on; E: is the same
  speed as C:; one owner-scheduled downtime. *Recommended.*
- (b) Keep it on C:, compact it and make it sparse — least change; C: still has 2.1 TB free; but the next runaway still
  lands on the Windows drive.
- (c) Move it to D: — works, but D: already holds the repos and Windows-side scratch, so two kinds of churn share one drive
  and E: stays idle.

**Q2. Whole distro on E:, or a second disk only for the scratch clones?**
- (a) **Move the whole distro** — one command, no new moving parts, survives restarts. *Recommended.*
- (b) Keep the distro on C: and add a second ext4 disk on E: mounted at `/home/mandrake/.seat-tmp` — a hard wall around
  clones, but it needs an **elevated** `wsl --mount --vhd` after every WSL start (a new scheduled task with admin rights),
  and if the mount is missing, agents write into the root disk silently (needs a guard in every tool).
- (c) Neither — rely on the reaper and sparse alone.

**Q3. When do we take WSL down (every seat, timer and the artpipe daemon stop; ~10–40 min for compaction, UNMEASURED; a
move with export/import is likely 1–1.5 h)?**
- (a) Tonight at the end-of-day handoff.
- (b) At the next reboot you were going to call anyway.
- (c) Never as a ritual — make it sparse once (one short downtime), then only when the disk watch says "compaction due".
- (d) A monthly window, combined with a full `wsl --export` backup to F: (there is no WSL backup anywhere today).

**Q4. Should cold bulk move to the 13 TB HDD (F:)?**
- (a) Yes: the 373 GB of old agent worktrees on D:, screenshots older than 30 days, old save-backup copies, and the parked
  ComfyUI — moved (verified copy), not deleted.
- (b) Move only the old worktrees; delete screenshots and save-backup copies outright.
- (c) Delete the old worktrees outright (they predate worktrees-OFF on 10-02; unlanded work in them is UNMEASURED and would
  need checking first) and use F: only for WSL backups.
