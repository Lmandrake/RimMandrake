# Who loads Archmagi besides the rm timers (one hour, 2026-11-27 11:23:38 to 12:23:38 PST)

Item: `RIMMANDRAKE_FIND_LOAD_USERS_RM_TIMERS_ONLY_TEN_PERCENT`, row 10 of `one_page.md` (same folder). One sample of one
hour. The hour was an ordinary working hour: 12 detached helper runs, the Conductor window and two RimWorld games were up.
A second hour can read differently. Each figure is `[measured]` unless it carries a guess tag.

Instruments (same folder): `load_sample.py` reads each cgroup (`cpu.stat`, `memory.current`, `memory.swap.current`) and
each process (`/proc/<pid>/stat`, `/proc/<pid>/io`) every 3 s. `load_sample_win.ps1` reads `Win32_Process` and the
performance counters every 30 s. `load_report.py` makes the tables. The data is on Archmagi in
`D:\ClaudeWork\scratch\load_census_20261127\hour` (`linux.json`, `win.jsonl`, `journal.txt`, `timers.txt`,
`report.md`, the full tables). The sample used 0.01 core-hours itself. To run it again, from any machine on the tailnet:

```
D=/mnt/d/ClaudeWork/scratch/load_census_<date>; ssh mandrake@archmagi-wsl "mkdir -p $D/bin $D/hour"
scp load_sample.py load_sample_win.ps1 load_report.py mandrake@archmagi-wsl:$D/bin/
ssh mandrake@archmagi-wsl "systemd-run --user --collect -p WorkingDirectory=$D --unit=load-census-hour /usr/bin/python3 $D/bin/load_sample.py --out $D/hour --seconds 3600 --every 3 --win-ps1 \"\$(wslpath -w $D/bin/load_sample_win.ps1)\""
# after the hour: timers.txt and journal.txt as load_report.py's docstring says, then python3 $D/bin/load_report.py $D/hour
```

## The answer in five lines

- **CPU (Linux side).** The detached helper runs used 61% of the busy CPU, and nearly all of that was their tool
   commands (selftests, publish checks, git), not the model process. All systemd user units, every rm timer included,
   used 23%. The rm timers alone used about 15%. Kernel threads used 9%.
- **CPU (Windows side).** Windows read 99.6% CPU busy for the whole hour. The WSL VM was 62% of Windows' process CPU.
   The other 38% was mostly the ArchSmall game (1.76 core-hours), the Plan 9 server that serves `/mnt/c` and
   `/mnt/d` to WSL (0.93), the ArchBig game (0.47), Defender, Backblaze and the kernel (0.36 to 0.39 each).
- **Disk.** Two readers made most of the disk reads. The WSL VM read 563 GB in the hour (156 MB/s), and 86% of that
   was refaults: file pages that were evicted and then read again. Backblaze (`bztransmit64.exe`) read 410 GB
   (114 MB/s), while hashing a large file. Together these are about the disk's own mean of 284 MB/s `[guess ~70%]`:
  part of Backblaze's reads can come from the Windows cache.
- **Memory.** Windows has 63.3 GB of RAM. The WSL VM holds 30 GB of it (`.wslconfig` `memory=28GB`), the two games
   hold 11 GB, Backblaze holds 5.9 GB, and Windows' available memory went as low as 3.5 GB. Inside WSL, swap held 1.9 to
   2.4 GB, and the page cache was too small for the files that the hour read again and again (the disk line).
- **So before you add a slot:** a new slot adds more helper tool commands. Those commands are already the largest CPU
   user, and their file reads are the largest cause of refaults. The cheapest wins are the readers that read the same
   bytes again (rows below), and Backblaze's 410 GB per hour.

## CPU on the Linux side (WSL, 14 CPUs)

The guest's `/proc/stat` read 11.62 core-hours busy of 14.02 (83%), iowait 0.31. The load average was 18 to 50.
The slice totals are exact, because the slices live the whole hour. The split inside `app.slice` comes from systemd's
own `Consumed` line for each run that ended in the hour (280 rm timer runs). A run that began before 11:23:38 counts
whole, so that split leans high.

| who | core-hours | share of busy |
|---|---|---|
| `claude-seats.slice`: every Claude window and helper run | 7.10 | 61% |
|   detached helper runs, tool commands (`claude-code-bash`) | 6.31 | 54% |
|   detached helper runs, model process (`seat`) | 0.48 | 4% |
|   the Conductor window (`claude-seat-BENCH-1400472`), both parts | 0.27 | 2% |
| `app.slice`: every systemd user unit | 2.73 | 23% |
|   rm timers (journal, 280 runs ended) | 1.79 | 15% |
|   `testq-tick` (the SteveDesktop test lane; a timer without the `rm-` prefix) | 0.59 | 5% |
|   all other user units (rm units without a timer, `systemd-run` scopes, long-lived services) | 0.35 | 3% |
| kernel threads (the root cgroup's own CPU) | 1.07 | 9% |
| WSL init 0.23, ssh sessions 0.19, system services 0.18 | 0.60 | 5% |

The rm timers that used the most: `rm-maturation-dispatch` 0.38 (49 runs), `rm-maturation-page` 0.28 (26),
`rm-list-dispatch` 0.26 (7), `rm-scratch-reap` 0.24 (1), `rm-codebase-now` 0.14 (4), `rm-list-effect` 0.13 (4).

The helper runs that used the most CPU in the hour (whole scope): `fix-return-step-says-failed` 1.69,
`fix-passed-mod-badge-helper` 1.58, `run-lane-checks-once-193-of` 1.10, `build-lane-bundle-sweep-five` 0.99,
`ready-all-scheduled-infrastr` 0.67. In each one, the tool commands used 80% to 98% of the CPU.

The process names inside that CPU (own CPU of each process seen; the processes seen cover 71% of busy, because a
process that lives under 3 s is not seen): `selftest_scene_library.py` 1.31 core-hours in 276 runs,
`gapprobe.py` 0.49 (47), `selftest_steve_lane_sweep.py` 0.37 (151), `rimflow cli.py` 0.35 (929),
`maturation_dispatch.py` 0.32 (54), `maturation_now.py` 0.32 (115), `selftest_maturation_dispatch.py` 0.25 (8),
`selftest_maturation_autonomy.py` 0.22 (7). A selftest that runs 276 times in one hour is the largest single name.

## CPU on the Windows side (14 logical processors)

`% Processor Time` read 99.6% mean (83.5% min). The sum of process CPU was 13.35 core-hours of 14.

| Windows process | core-hours | what it is |
|---|---|---|
| `vmmemWSL` | 8.26 | the WSL VM |
| `RimWorldWin64.exe` (ArchSmall, `instances\b`) | 1.76 | a game that was up for the whole hour |
| `dllhost.exe` pid 23580 | 0.93 | `Plan9FileSystem` (`vp9fs.dll`): the server for `/mnt/c` and `/mnt/d` (registry, measured). It read 19.6 GB in the hour, and 8.2 TB since it started |
| `RimWorldWin64.exe` (ArchBig, Steam's install) | 0.47 | |
| `MsMpEng.exe` | 0.39 | Defender |
| `bztransmit64.exe` | 0.37 | Backblaze |
| `System` | 0.36 | the kernel |
| all others | 0.73 | |

The guest says that WSL used 11.62 core-hours; Windows says `vmmemWSL` used 8.26. The WSL guest shows no steal time
(`steal` is 0), so when Windows ran other work on the cores, the guest probably still counted that time as busy
`[guess ~60%]`. Read the Windows figure as the share of the machine.

## Disk

| reader | reads in the hour | note |
|---|---|---|
| WSL VM, page-ins (`/proc/vmstat` `pgpgin`) | 563 GB, 156 MB/s | ext4 on the VM's disk |
| of it, refaults (60 s probe at 12:25) | 1,506 MB of 1,753 MB, 86% | file pages that were evicted and then read again |
| Backblaze `bztransmit64.exe` | 410 GB, 114 MB/s | its log at 11:26 PST: `ReadLargeFileIntoBuf_Slowly - called by GetFileNameToBzFileIdHash`. Which file: UNMEASURED. The WSL disk image is a large file that changes constantly `[guess ~50%]` |
| Plan 9 server (`/mnt/c`, `/mnt/d`) | 19.6 GB | |
| Windows `PhysicalDisk` reads | 284 MB/s mean, 1.45 GB/s max | Backblaze plus the VM is about this figure |

In the 60 s probe, no cgroup hit its own `memory.max` (`memory.events.local`). So the refaults come from pressure on
the whole VM, not from the per-seat limits in `claude-seats.slice` (`MemoryMax` 6 GB for tool commands, 10 GB per seat,
24 GB for the slice). RULED OUT for that minute: the per-seat limits cause the refaults.

Storage reads by process (`/proc/<pid>/io` `read_bytes`). This counts reads from the Windows drive over 9p in full
(measured: 8,189,472 bytes read from `C:\Windows\System32\shell32.dll` gave 8,189,472 bytes), so the column sums to more
than the page-ins (1,434 GB attributed).

| process | GB | runs | per run |
|---|---|---|---|
| `claude` session processes (`-p` helpers and windows) | 275 | 37 | one Sonnet helper read 82 GB, the Conductor window 39 GB. Cause UNMEASURED (no `strace` on Archmagi). A probe of 12 of them read 43.5 MB with 651 major faults in 30 s, which fits page-fault readahead on the 371 MB binary and other mapped files `[guess ~50%]`; it does not explain the larger bursts |
| `publish.py` | 243 | 108 | about 2.2 GB |
| `selftest_bench_word_prose.py` | 95 | 29 | about 3.3 GB, in the treecheck trees |
| `spend_watchdog.py` | 72 | 15 | one run read 58 GB in 31 min, about 0.9 GB per 30 s poll: `role_launch.transcript_usage` reads each transcript file of the session whole on each poll. Which files it opens per poll: UNMEASURED |
| `git` in `/home/mandrake/rm/dispatch` | 64 | 299 | `git log -p --unified=0` from `maturation_rescue.py`, each in its own `systemd-run` scope |
| `list_dispatch.py` | 58 | 7 | 8 to 12 GB per tick |
| `git` in the treecheck clones (`rm-treecheck-kept-0`, `-1`, `-text`) | 96 | 118 | the same git also had the largest resident sizes, 2.3 to 3.4 GB |
| `list_effect.py` 38, `scratch_reap.py` 25 (4 runs), `account_usage.py` 24, `cli.py` 19 (929) | | | |

By class: helper tool commands 586 GB, rm timers 385 GB, helper model processes 211 GB, the Conductor window 121 GB.

## Memory

| holder | size |
|---|---|
| Windows RAM | 63.3 GB; available 3.5 to 14.0 GB (mean 10.2); committed 78 to 90 GB |
| WSL VM (`vmmemWSL` private) | 30.0 GB (`.wslconfig` `memory=28GB`, `swap=16GB`) |
| ArchSmall game, private | 7.1 GB |
| Backblaze, private | 5.9 GB |
| ArchBig game, private | 3.9 GB |
| inside WSL: swap in use | 1.9 to 2.4 GB; MemAvailable 12.8 to 19.2 GB of 29.4 |
| inside WSL: helper scopes at 12:23 (with their page cache) | 14.3 GB; the rm timers 3.8 GB |

MemAvailable counts page cache as free, so 13 to 19 GB "available" and 86% refaults can both be true: the cache was
full of files that were read once, and the files that were read again were evicted.

## Fixes this page proves are worth a look (the ordering item picks)

| fix | proves |
|---|---|
| Backblaze: find the file that it hashes at 114 MB/s, and exclude it if it is the WSL disk image or a scratch tree. Its backup coverage is his, so name the file to him first. | `bztransmit64` read bytes per hour |
| `spend_watchdog.py`: measure only the new lines of the transcript on each poll (keep the offset), not the whole files. | its read bytes per run (58 GB today) |
| `selftest_scene_library.py` ran 276 times in one hour (1.31 core-hours): find who runs it, and run it only when what it reads changed (`CLAUDE.md` §After a change, only the checks that the change touches run again). | runs per hour |
| `publish.py` and the treecheck git read about 2.2 GB per publish, and `selftest_bench_word_prose.py` 3.3 GB per run: read the changed files only, or keep the trees in cache. | read bytes per publish |
| `list_dispatch.py` reads 8 to 12 GB per tick (row 2 of `one_page.md` is the same tick). | read bytes per tick |
| `maturation_rescue.py`: 299 `git log -p` runs per hour in the dispatch clone, 64 GB. Keep the result per mod until a new commit touches it. | git runs per hour |
| The `claude` processes' own reads (275 GB): measure the cause with `strace -e openat` or `perf trace`; neither is on Archmagi. | the cause |

## What this page cannot say

- One hour, one sample. The helper runs of that hour decide the helper rows.
- A process that lived under 3 s is in its cgroup's CPU but not in the process tables (they cover 71% of busy).
- Windows `ReadTransferCount` counts all I/O of a process (file, network, device), and a read that the Windows cache
  served counts too.
- Which file Backblaze hashes, and why the `claude` processes read: UNMEASURED (above).
