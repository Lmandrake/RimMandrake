# 18 — WSL move to E: — preparation (weekly cleaning 2026-10-11)

PREPARE ONLY. Nothing in this pass stopped WSL, exported, moved or unregistered the distro, or touched `.wslconfig`.
The only writes outside this file: the scripts below, and a trigger-less scheduled task `\WSL Move Once` registered by the
dry runs (inert; the real launch re-registers it with `-Force`).

Owner (decision taken by question card): move the whole distro to E:, make it sparse, full backup on F:; downtime right
after the grooming task finishes (Sunday morning).

## Status
- [x] probes (read-only)
- [x] script written — `D:\Luke\dev\_rmscratch\wslmove\move_wsl_to_e.ps1` + launcher `D:\Luke\dev\_rmscratch\wslmove\launch_move.ps1`
- [x] parser: **0 errors** on both (`[System.Management.Automation.Language.Parser]::ParseFile`)
- [x] `-WhatIf` dry run through the real launcher (one-shot scheduled task): 15 WOULD steps, `DONE`, task result 0
- [x] estimate + space check

Repo copies: `/home/mandrake/rm/bench/src/RimMandrake/Utils/wslmove/move_wsl_to_e.ps1`, `.../wslmove/launch_move.ps1`
(the D: copies are what runs; keep them identical).

## Probes (measured 2026-10-11 09:40–09:53, read-only)

| fact | value |
|---|---|
| WSL | 2.7.11.0, kernel 6.18.33.2-2, Windows 10.0.26200.9457; one distro `Ubuntu`, WSL 2, Running |
| `--manage` | `--move <Location>`, `--set-sparse <true\|false>`, `--set-default-user` all present |
| `--export --format` | `tar, tar.gz, tar.xz, vhd` |
| image | `C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx`, 908.1 GB, NOT sparse; Lxss DefaultUid 1000 |
| ext4 used | **362 GB** at 09:52 (was 502 G at 09:32; the clone reap is still shrinking it) |
| free | E: 3,726 GB (NTFS, `E:\WSL` absent); F: 13,038 GB (NTFS, `F:\WSLBackup` absent); C: 2,103 GB |
| elevation | this shell is not elevated; user SID has FullAccess on both tasks below and Write on the task root → no admin needed to disable/enable them or to register the launcher task |
| `/etc/wsl.conf` | `[boot] systemd=true`, `[user] default=mandrake` |
| linger | `Linger=no` — user units run only while a session exists; the keepalive's `sleep infinity` session is what keeps them up |

**Windows things that start WSL** (all non-Microsoft tasks, HKCU Run and the Startup folder enumerated):
1. `\WSL Keepalive` — logon task, `wscript.exe D:\Luke\dev\claude-remote-control\scripts\wsl_keepalive.vbs` → `wsl.exe -d Ubuntu sleep infinity`.
2. `\RimFlow Pulse` — **also starts WSL**: its lantern widget (`lantern.pyw`, process `pythonw3.13.exe`) runs
   `wsl.exe -d Ubuntu -- systemctl --user start rm-pulse.service` whenever the spine is down >60 s (every 5 min). Left
   running it would boot the distro mid-export. The script disables the task and kills the widget, then restores both.
3. Startup folder `Start Agent Fleet.lnk` → `launch_fleet.ps1` — logon only, harmless during the window; `-RelaunchFleet` runs it at the end.
- `\Git for Windows Updater` matched "bash" but is git-bash, not WSL. Nothing in HKCU Run touches WSL.

**Units to come back** — user (enabled): `rm-artpiped.service`, `rm-pulse.service`, `hestia.service`, timers
`rm-memwatch`, `rm-mirror`, `rm-objstore`, `rm-codebase-health`, `rm-pulse-digest`, `rm-pulse-health`. System:
`tailscaled.service`, `lodestar-sync.timer` (the Lodestar sweep). All 11 read `active` now through the exact
`systemctl is-active` calls the script makes.

## Runbook (what the script does, in order; any failed check STOPS, deletes nothing, and — if the registered image still exists — re-enables the tasks so WSL comes back)

0. Pre-flight: capabilities, registration, image path/size, **ext4 used measured live by `df` before shutdown** (the
   yardstick for the tar), free space (F: ≥ 1.3×used+50 GB, E: ≥ image+50 GB), `E:\WSL\Ubuntu` absent or empty.
1. Disable `\WSL Keepalive` and `\RimFlow Pulse` (ending running instances); kill the lantern by PID.
2. `wsl --shutdown`; `wsl -l -v` must say Stopped and no `wsl`/`wslhost`/`wslrelay` process may survive 25 s.
3. **Backup first:** `wsl --export Ubuntu F:\WSLBackup\Ubuntu_<stamp>.tar`; verify exit 0, size 0.80–1.30 × ext4-used,
   and the archive's final 1024 bytes are tar's zero end-of-archive blocks; re-check Stopped.
4. **Keep the old image:** hard-link the C: vhdx to `C:\Users\Mandrake\AppData\Local\wsl\pre_move_keep_<stamp>\ext4.vhdx`
   (instant, same volume, no extra space). `--move` removes its own source name after copying; the hard link means the
   old image still exists afterwards, as a rollback, until the owner deletes it.
5. `wsl --manage Ubuntu --move E:\WSL\Ubuntu`; verify exit 0, Lxss `BasePath` = `E:\WSL\Ubuntu`, image present.
6. `wsl --manage Ubuntu --set-sparse true`; a refusal or an "unsafe/corrupt" warning is logged and **never forced**.
7. Boot: `wsl -d Ubuntu -u mandrake -- echo ok`; `whoami` must be `mandrake` (else `--set-default-user mandrake` and re-check); `/etc/wsl.conf` `[user]` checked; `df -h /`.
8. `fstrim -v /` as root — the now-sparse image hands the ~540 GB Linux already freed back to E: (free space logged before/after).
9. Re-enable + start both tasks; after 20 s check the 9 user + 2 system units; optional `-RelaunchFleet`.
10. Report lines: tar path (keep), new location, **old-image paths for the owner to delete later**, total minutes, per-step `TIME` lines.

**Why `--move` and not export/unregister/import.** `--move` exists on 2.7.11, keeps the image byte-for-byte (UID, systemd
state, everything), and never unregisters anything. The tar is taken first and verified, so it is a real backup rather than
the transport. The import path is coded only as a fallback for a build without `--move`, and even there it **renames** the
old registration to `Ubuntu-old-C` in HKCU Lxss (keeping its image) instead of `--unregister`, so no step in either path
deletes the old disk. A test-import of the tar was rejected: it costs another ~360 GB write and ~40 min and protects
nothing the hard link and the untouched source do not. **`--format vhd` export was rejected** for the backup: it would copy
all 908 GB (the image is not sparse, so the 540 GB of freed blocks travel too) to a spinning disk, versus ~362 GB of tar.

## Launcher and elevation

From any WSL shell (registers the one-shot task and returns at once; the task is owned by Task Scheduler, so it survives
`wsl --shutdown` — a process spawned via WSL interop may not, and the script must not be a child of the VM it stops):

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\Luke\dev\_rmscratch\wslmove\launch_move.ps1' -DelaySec 90
```

Dry run: same line with `-WhatIf` (done, see below). Add `-RelaunchFleet` to reopen the seats at the end.
Progress: `D:\Luke\dev\_rmscratch\wslmove\move.log` (+ `move.transcript.log`).

**Elevation: none expected.** Task disable/enable and task registration are measured to be allowed for this user (ACLs
above); `--export`, `--import`, HKCU and hard links need no admin. **UNMEASURED:** whether `--manage --move` or
`--set-sparse` demand admin on 2.7.11. If `--move` refuses for lack of rights the script STOPS after the verified backup,
re-enables the tasks and WSL comes back on C: unharmed. Then the owner opens **Start → type "PowerShell" → right-click
"Windows PowerShell" → Run as administrator → Yes** and runs
`powershell -ExecutionPolicy Bypass -File D:\Luke\dev\_rmscratch\wslmove\move_wsl_to_e.ps1 -SkipBackup`
(an elevated console is a Windows process, so it also survives the shutdown; `-SkipBackup` reuses the tar already verified).

## Dry run (`-WhatIf`, via the launcher task, 09:53)

Pre-flight passed with live values (ext4 used 361.7 GB, F: 13,038 free / 520 needed, E: 3,726 / 958, both tasks found,
lantern found as pid 13664), then 15 `WOULD:` lines in the order above, `==== DONE`, task result 0. Nothing changed:
`\WSL Keepalive` Ready, `\RimFlow Pulse` Running after the run.
⚠️ The **first** task-launched dry run (09:51, an earlier revision) exited 1 right after the first `WOULD:` without logging
a `STOP` line; the cause was not captured (there was no transcript yet). Three later runs through the same task were clean
after the transcript was added and the lantern lookup rewritten. A recurrence is non-destructive at that point (only task
disables would have happened), but read `move.transcript.log` if the log ends without `DONE` or `STOP`.

## Duration and space

| step | volume | rate (estimate; UNMEASURED here) | time |
|---|---|---|---|
| shutdown + checks | — | — | ~1 min |
| export tar → F: (HDD) | ~362 GB (ext4 used now; shrinking) | 120–250 MB/s (tar stream, HDD write, many small files) | **25–50 min** |
| `--move` C: → E: (NVMe→NVMe) | **908 GB** (non-sparse: every block is copied) | 1–2 GB/s sustained | 8–15 min |
| set-sparse, boot, verify, fstrim | ~540 GB released | — | 3–5 min |
| **total downtime** | | | **~40–75 min**, plus seat relaunch |

Space: F: needs ~0.36–0.47 TB of 13 TB free. E: needs 0.91 TB transiently and settles to ~0.37 TB after fstrim. C:
gains nothing until the owner deletes the hard link `C:\Users\Mandrake\AppData\Local\wsl\pre_move_keep_<stamp>\ext4.vhdx`
(908 GB) once he is satisfied — that deletion is his, the script never does it.

Notes for the owner: Backblaze (HKCU Run) backs up internal drives; whether it will start uploading the 0.4 TB tar on F:
or the vhdx on E: is UNMEASURED — check its exclusions. `.wslconfig` is untouched (`sparseVhd=true` already there).
