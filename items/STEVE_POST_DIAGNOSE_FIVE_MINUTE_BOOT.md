# STEVE_POST_DIAGNOSE_FIVE_MINUTE_BOOT - read-only diagnosis (BENCH, 2026-10-31 ~18:45)

STATUS: PARTIAL. Steve dropped off the network at ~18:38 (ssh and ping time out; Tailscale 100.118.241.96), presumably the owner rebooting/in BIOS. Nothing was changed on Steve. Owed items below are unread.

## MEASURED
- Harddisk1 = Samsung 970 EVO Plus 2 TB NVMe, GPT: Recovery 0.5 GB, EFI 0.1 GB, MSR 16 MB, **C: (1.9 TB, the rest of the disk)**. D: is the WD 14 TB (Harddisk0). So every bad block is on C: ("Windows 10"). No partition other than C: is on the drive.
- Reliability counters (Get-StorageReliabilityCounter, disk 1): Wear 0, Temperature 61 C, TemperatureMax 85 C, ReadLatencyMax 834 ms, WriteLatencyMax 762 ms, FlushLatencyMax 722 ms; error counters, PowerOnHours empty (the Windows driver does not expose NVMe SMART). Disk 0 (WD): PowerOnHours 39804, ReadErrors 0, 38191 load/unload.
- smartmontools is not installed (Get-Command empty); winget v1.29 exists. Not installed: ssh dropped first.
- Event 7 (disk, "The device, \Device\Harddisk1\DR1, has a bad block."): 45,654 events, first 2026-10-30 ~10:54-11:19 (10-30: 16,426; 10-31: 29,228). Level Error, source process ID 4 (System, i.e. NTFS/cache/paging, not a user process).
- Decoded the IO_ERROR_LOG_PACKET of the 15,950 newest events (08:05-18:37 on 10-31): all MajorFunction 3 (READ), FinalStatus 0xC000009C (STATUS_DEVICE_DATA_ERROR). Only 74 distinct physical byte offsets, all between 22.07 and 31.56 GB of the disk, i.e. inside the first ~30 GB of C:. They repeat: the top offsets 0x789E66000 (30.155 GB) 3,593x, 0x7E3C0A000 (31.559 GB) 2,492x, 0x78A0F0000 and 0x789FF0000 1,096x each, 0x789E6A000/0x789E6E000 1,086x each, 0x789EE6000 1,046x, 0x7E3CAE000/0x7E3D2E000 775x each. Two clusters (30.15-30.16 GB and 31.55-31.56 GB), a few 4 KB-aligned neighbours: one narrow set of bad LBAs re-read by retries, not a spread-out surface failure.
- Hourly counts: 08h 3243, 09h 3532, 10h 3549, 11h 2417, 12h 2003, then none logged 13h-16h, 17h 643, 18h 563. Events appear only while the machine is up and busy.
- Other 3-day System noise: Kernel-Processor-Power 55 x182, disk 157 x36 ("disk was surprise removed", probably the USB stick), Ntfs 98 x30, Kernel-Power 109 x10 and 172 x10, disk 51 x2. Not decoded further.
- Brief's figures taken as given (not re-measured): BIOS 3401, ME 14.1.79.2540, FwPOSTTime 292,889 ms, microcode 0x100, 18 of 20 logical CPUs.

## NOT MEASURED (Steve went dark) - owed
1. File(s) at the bad LBAs: need C: partition start offset (Get-Partition 4 Offset), cluster = (offset - start)/4096, then map to a file (fsutil / FSCTL_GET_RETRIEVAL_POINTERS scan or chkdsk /scan output). Likely one big file or a hot system file in the first 30 GB of C: (candidates to check: WSL ext4.vhdx, pagefile.sys/hiberfil.sys, Defender quarantine/ScanCache, a game/save file).
2. A process tie: the reads come from System; correlate with Defender (MpCmdRun/Microsoft-Windows-Windows Defender/Operational scans) and WSL VHDX timing.
3. Boot history: Diagnostics-Performance event 100 (BootTime etc.), FwPOSTTime in HKLM\...\Power, bcdedit numproc/onecpu, Kernel-Power 41/6008/12/13 around the CPU fault. The query was sent but the output was lost to the disconnect.
4. Full NVMe SMART (Critical Warning, Media and Data Integrity Errors, Available Spare, Percentage Used, Unsafe Shutdowns): `winget install smartmontools` or WSL smartctl (WSL cannot see the NVMe).
5. chkdsk C: /scan (online, read-only; non-disruptive in principle, but it reads the whole volume, so do it after the reboot and not while the owner works).
6. Precious / unpushed / only-on-Steve: not enumerated. Recommended read: `git status` and `git log @{u}..` in every repo on C: and D:, plus the lane's results dir. Until then treat Steve's C: results since 10-30 as suspect.

## HYPOTHESES for the 4.9-minute POST, ranked (all HYPOTHESIS)
1. Firmware memory re-training after the BIOS 3401 / ME 14.1.79.2540 / microcode change. The first ME-update reboot took ~19 min dark; a shrinking first-boot-after-flash time (19 min then 4.9 min) fits retraining that is cached over several cold boots. Cheapest test: cold boot twice more with nothing changed and compare FwPOSTTime; if it falls, it self-heals.
2. A USB device (the stick that gives I/O errors and has no volume; disk 157 surprise-removal events) stalling enumeration. Cheapest test: boot once with all USB storage unplugged.
3. The NVMe itself: the BIOS/option ROM waits on a drive that returns media errors on part of the namespace (the unreadable region is at 30 GB, in C:, which the BIOS does not read, so this is weaker for POST but strong for OS slowness). Cheapest test: boot with the drive's temperature/health checked in BIOS, or compare POST with the NVMe slot empty (not a reboot-free test; owner's call).
4. Degraded CPU / 2 cores masked (18 of 20 logical): the CPU fault (per-CPU SIMD) plus a BIOS core mask causing repeated CPU init retry. Cheapest test: read bcdedit numproc and BIOS "Active Cores"; if mask is in BIOS, restore all cores and see.
Event-7 bad blocks are OS reads of C: files and are not a proven cause of POST time; they explain a slow, error-laden OS, not necessarily firmware time.

## Lane pause
KEEP PAUSED. Reasons: C: has unreadable regions being retried thousands of times an hour, the CPU fault already made earlier results suspect, and the machine is mid-reboot with the owner in BIOS. Resume only after: the file at the bad LBAs is identified (and replaced if it is a lane file), NVMe SMART shows Media Errors flat, and one clean boot with FwPOSTTime known.

Raw decoded events (15,950, 08:05-18:37) were saved under the BENCH scratchpad ev7.txt; script is in this note's method (offset at bytes 32-39 of the Binary, little endian).
