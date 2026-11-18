# SteveDesktop's uptime SIMD fault: what is measured, what is not

Item `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`. Machine: i9-10900K, ROG STRIX Z490-G, 4×32 GB F4-2666C18.
Live instrument: `python3 src/RimMandrake/Utils/testq/fault_monitor.py report` (timer `rm-steve-fault.timer`,
state `D:\ClaudeWork\rimmandrake\testq\fault_state.json`). Raw evidence: `D:\ClaudeWork\rimmandrake\steve_diag\`.
🔑 **Reading the raw log from any machine, no Archmagi needed** (measured 2026-11-17): the Desktop's host
`ssh` cannot reach Steve, but the tailnet container can —
`docker exec tailscale-gmail sh -c 'ssh -o BatchMode=yes mandrake@100.115.10.14 "<cmd>"'`, with the probe
log at `/mnt/c/SteveDesktop/diag/logs/watch.log` (4262 CYCLE lines as of 2026-11-18T01:00Z).

## 🔴 The +0.100 V raise DID take effect, and it did not cure the fault (MEASURED 2026-11-18T01:00Z)

Per-boot bad-cycle counts from the whole probe log, and the pre/post split over all 3898 cycles:

| boot (UTC) | cycles | bad cycles | bad share | uptime at last read |
|---|---|---|---|---|
| 2026-11-07 17:52 | 1416 | 774 | **55%** | 118.1 h |
| 2026-11-14 09:37 | 145 | 129 | **89%** | 12.1 h |
| 2026-11-15 09:00 | 652 | 231 | **35%** | 54.3 h |
| **2026-11-17 15:35** (first post-raise) | 51 | **2** | **3.9%** | 4.2 h |
| **2026-11-17 19:54** (second post-raise) | 62 | **0** | **0%** | 5.1 h |

- **The raise IS visible, in temperature, not in the vcore reading.** Package temp mean fell from
  **42.8 °C (n=3792, max 73)** before the raise to **36.1 °C (n=106, max 43)** after — and vcore's
  *spread* collapsed from 1.004–1.332 V (mean 1.125) to 1.016–1.037 V (mean 1.031). An earlier note
  read "vcore ~1.03 V both before and after, so the raise is not visible": that compared the MEAN
  against a single sample and is **wrong**. What changed is the variance, not the idle level — the
  board stopped excursioning to 1.33 V. Cooler and electrically calmer under the same workload is a
  machine whose boost behaviour changed, i.e. the BIOS change took.
- **And the fault still fired**: window `F20261117T153258Z` opened 4.13 h into the first post-raise
  boot, CPUs 8 then 7, one bad cycle each, with the positive control (`inject_exit=1 clean_exit=0`)
  passing on both boots, so the instrument could see.
- **Severity dropped by about an order of magnitude** (2 bad cycles vs 231 in the previous window;
  3.9% vs 35–89% of cycles). That is the shape of a **marginal** fault whose margin improved, not a
  cured one. `[measured]`
- 🔴 **Do not read the current 0-bad boot as a cure.** 62 clean cycles over 5.1 h is well inside what
  the pre-raise boots did between windows (one pre-raise boot ran 44 cycles / 3.6 h with 1 bad). The
  counting window set by the item runs to **2026-11-20T15:33Z**; only then is zero meaningful.

## The RAM test: done, clean (MEASURED 2026-10-31)

- Windows Memory Diagnostic, Basic, 1 pass: no errors (events 1101/1201, 18:57Z).
- In-OS RAM walks: 85 GB (faulty CPU 2 excluded) 0 bad; 108 GB on a fresh 20-CPU boot 0 bad.
- No WHEA events. RAM is clean within that coverage; it is not the fault's cause on present evidence.

## The fault's shape (MEASURED)

- Wrong SIMD results (Prime95 rounding, `stevecheck`, sha256 distinct digests) on a logical CPU, acquired
  during uptime, held until a reboot, cleared by every reboot so far.
- 10-26 it was CPU 18; 10-31 CPU 2 under `numproc 18`; so masking a core cures nothing.
- 🔴 **Not established (2026-11-17): the post-flash onsets are too few to say the flash changed anything.**
  Three-or-four short onsets against ONE pre-flash observation is not a changed distribution, and nothing
  controlled for workload, detection cadence or settings. Read the next bullet as timings, not as a finding.
- After the BIOS 3401 flash (new microcode) onsets came SOONER: 3.30, 0.88, 2.88 h into a boot (fault_monitor
  windows F20261101T035219Z, F20261101T164245Z, F20261103T195921Z), against ~5 days once before the flash. Inside a
  window the bad CPU wanders cycle to cycle, with clean cycles between, until the reboot.
- So old microcode is ruled out as the sole cause, and "one dead core" does not fit.

## What the fault does to jobs (MEASURED, one stack)

A modcheck run that dies "exit 5, no sheet" is python.exe killed by an access violation in pure CPython code
(`ast.parse`), inside a fault window: `J20261103T233438Z-aa0482` in `F20261103T195921Z`. Since the 10-31 reboot, 1 of
42 in-window jobs crashed and 0 of 57 outside. Census: `infrastructure/state/evidence/MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET.md`.

A cold load can die in the mono JIT (`0xE0000001`, RaiseException under `mono_unity_jit_cleanup`) before the monitor
reads bad: 11-03 and 11-06, each 6-7 min before first_bad and outside the window as recorded, so ingest files a repair
item. Table and odds: `infrastructure/state/evidence/HARNESS_REPAIR_CAUSE_4F477502.md`.
A cold-load death is not always the CPU fault. A job that died INVALID/LOAD on a native `RaiseException` in the mono JIT under HugsLib's Harmony `PatchAll`, before any JawaBench code ran, loaded fine when resubmitted: read `Player.log`'s stack before blaming the last thing deployed. For a mono JIT abort (`0xE0000001`) that precedes the monitor's first_bad by 6-7 min, `mono_profiler_init_etw` in the note is only the thread-start tail: read `crash.dmp` and first_bad before touching the harness.

## Hypothesis under test: vendor software holding CPU state

A fault that persists until reboot and spans many cores fits a machine-wide setting that a reboot resets (MSRs,
voltage/ratio offsets, SMBus/IO writes) better than a marginal core. Steve runs several ring-0 MSR/IO drivers and
their callers: ASUS AI Suite (`asComSvc`, `AsIO2`), Corsair iCUE (`CorsairService`, `CpuIdRemote64` via the
CPUID `cpuz154` driver, `CorsairLLAccess`), Aura `LightingService` (`GLCKIO2`, `ene`), `MsIo64`.

**A/B started 2026-11-04T03:40:20Z** (boot 02:45:13Z, clean at that time): the callers above were set Disabled and
stopped; `cpuz154` and `CorsairLLAccess` unloaded. Kernel drivers with System start stay loaded but have no caller.
The only Corsair device is a keyboard (no AIO), so cooling falls back to BIOS fan curves. Original start modes:
`C:\SteveDesktop\diag\driver_ab_original.json`; revert: `C:\SteveDesktop\diag\driver_ab_revert.ps1`.

Reading it: baseline onsets on BIOS 3401 are all ≤ 3.3 h. A fault window opening after 03:40:20Z falsifies the
vendor-software hypothesis (hardware stays the lead: CPU or VRM/board). 12 h or more of clean uptime with the
callers off is evidence for it.

## Result

**FALSIFIED (MEASURED 2026-11-04).** Three fault windows opened with the callers off
(`python3 src/RimMandrake/Utils/testq/fault_monitor.py report`):

| window | boot | onset | first bad | CPUs | hottest core at onset |
|---|---|---|---|---|---|
| F20261104T024513Z | 02:45:13Z (A/B began mid-boot) | 0.96 h | 03:43:02Z | 2 | UNMEASURED |
| F20261104T035722Z | 03:57:22Z, callers off from boot | 4.46 h | 08:25:14Z | 16 | 61 °C, vcore max 1.302 V |
| F20261104T083546Z | 08:35:46Z, callers off from boot | 0.88 h | 09:28:37Z | 16 | 56 °C, vcore max 1.315 V |

The first window opened on the boot where the A/B started, so state set before 03:40Z could explain it. The other two
opened on clean boots with the callers off. A read at 2026-11-04T10:00Z (boot 09:38:00Z) showed every caller still
Disabled and stopped, `cpuz154` and `CorsairLLAccess` not loaded, and no SCM start event for them since the disable
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\verify_g3.out`). 🔴 **Corrected 2026-11-17:** this line read
"Onsets with the callers off (4.46 h, 0.88 h) fall inside the baseline range", which is FALSE — the stated
baseline is ≤ 3.3 h (line 46), so 4.46 h is OUTSIDE it, and an independent reviewer caught the contradiction.
The falsification does not depend on it: the A/B's test was whether any window opens with the callers off, and
three did, two of them on clean boots that began with the callers already off. **Software that calls these
vendor drivers is not the cause.** What 4.46 h does mean is that onset timing is NOT tightly bounded, so
"all ≤ 3.3 h" was never a safe baseline either: with 4 post-flash onsets (3.30, 0.88, 2.88, 4.46 h) against
ONE ~5-day pre-flash observation, the claim that the flash made onsets sooner is UNMEASURED, not measured —
the samples are too few and workload, detection cadence and settings were uncontrolled.

Not excluded: the System-start drivers `AsIO2`, `GLCKIO2`, `ene` and `MsIo64` stayed loaded, with no known caller
running. `iCUE.exe`, the user-mode app, kept running, but it reaches hardware only through the disabled services.
Heat at onset is ordinary (56–61 °C), so thermal runaway is not the trigger. **Hardware is the lead: the CPU or the
board/VRM.** Next discriminators: run at stock settings with XMP/MCE (multicore enhancement) off and a small negative
ratio or a fixed vcore, or swap the CPU.

Reverted 2026-11-04T10:00:58Z: original start modes restored, services running again
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\revert_g3b.out`). 🔴 `C:\SteveDesktop\diag\driver_ab_revert.ps1`
does nothing on Windows PowerShell 5 (the JSON array arrives as one object). Use `driver_ab\revert2.ps1` instead.
