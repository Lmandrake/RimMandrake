# SteveDesktop C: (Kingston NV3, 999 GB): what fills it, 2026-11-03

Item `STEVE_DISK_MEASURE_ONLY_FORTY_GIGS_LEFT`. Measured over ssh 2026-11-03 20:00-20:15 Steve local
(2026-11-04 04:00-04:15Z). C: free: **39.4 GB before, 68.4 GB after** (decimal GB, as the 999 GB size; PowerShell's `1GB` is GiB: 36.7 → 63.7 GiB). Raw scans and scripts:
`D:\ClaudeWork\rimmandrake\steve_diag\disk_fill\` on Archmagi (copied from Steve's `C:\SteveDesktop\diag\disk_fill\`) (`scan.tsv` whole C: to depth 4, `scan2.tsv` AppData and
Downloads deeper; sizes are file bytes in decimal GB, reparse points not followed).

Free-space reading after the work (`c_free_reading.ps1` over ssh, raw in `c_free_reading.txt` beside the scans):
`2026-11-04T04:30:06Z free_bytes=68354924544 size_bytes=999559708672`

## What fills C:

960 GB used. The non-OneDrive tree walks to 365 GB; the rest is `C:\Users\sjlewis\OneDrive` (607 GB = 565 GiB, a
reparse-point tree the walk skips; measured earlier with Get-ChildItem).

| GB | path | whose |
|---:|---|---|
| 603 | `C:\Users\sjlewis\OneDrive\Desktop\old_computer` | Steve's. Owner order: stays on C: until the Conductor says (`nvme_replacement.md`) |
| 69.6 → 58.4 | `C:\Users\sjlewis\AppData\Local\wsl\{353db0b6-…}\ext4.vhdx` | ours: the WSL seat (43 GB used inside) |
| 17.9 → 0 | `C:\Users\sjlewis\AppData\Local\Temp\<GUID>\swap.vhdx` × 19 stale | ours: WSL swap files of dead sessions |
| 27.6 | `AppData\LocalLow\Ludeon Studios` | Steve's RimWorld config and saves (the live game's, Config written today) |
| 27.0 | `AppData\LocalLow\Ludeon Studios old` | Steve's own 2020-2024 RimWorld data (created 2020-08-20), not ours |
| 45 / 37 | `Program Files` / `Program Files (x86)` | installed programs (Steam on C: 13.8, StarCraft 6.1) |
| 37 | `Windows` | system |
| 24 | `ProgramData` | Backblaze bzdata 7.1, Minecraft Education 6.9 |
| 15 | `AppData\Local\Packages` | Claude desktop app cache 9.7, Spotify 4.2 |
| 12.9 | `AppData\Local\Google\Chrome` | Steve's browser |
| 9.9 | `Downloads` | Steve's |
| 8 | `pagefile.sys` | system |

Inside the WSL distro (40 GiB used, `df -h`; these are `du -h` GiB): `/home/mandrake/mutation` 15 GB (`RimMandrake` 6.2, `shards` 8.1) and
`/home/mandrake/rm/runner` 14 GB. Both are working trees, and mutation/RimMandrake holds unpushed commits
(`nvme_replacement.md`): not cleared. Shadow copies use 0 bytes; no hiberfil.

## Cleared (ours)

1. 19 stale WSL `swap.vhdx` folders under `C:\Users\sjlewis\AppData\Local\Temp` (one of 17.2 GB from
   2026-10-28, eighteen of 36 MB). The live swap (`D24F4874-…`, written at the 19:57 WSL start) was kept.
   Freed 17.9 GB.
2. WSL vhdx compacted: `fstrim -v /` as root, `wsl --shutdown`, diskpart `attach vdisk readonly` /
   `compact vdisk` / `detach` as a SYSTEM task, with `Steve Seats Watch` disabled during it and then
   re-enabled; `WSL Keepalive` restarted it. 69.6 → 58.4 GB (64.85 → 54.4 GiB), 37 s. seat-server and seat-runner tmux came back
   at 20:13.

Nothing of Steve's was touched. A vhdx regrows as WSL writes; compact it the same way when C: gets tight again
(steps in `D:\ClaudeWork\rimmandrake\steve_diag\disk_fill\compact_task.ps1` and `phaseA.ps1`).
