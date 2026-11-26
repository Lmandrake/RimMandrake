# SteveDesktop's uptime SIMD fault: what is measured, what is not

Item `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`. Machine: i9-10900K, ROG STRIX Z490-G, 4×32 GB F4-2666C18.

- Live instrument: `python3 src/RimMandrake/Utils/testq/fault_monitor.py report` (timer `rm-steve-fault.timer`,
  state `D:\ClaudeWork\rimmandrake\testq\fault_state.json`).
- Raw evidence: `D:\ClaudeWork\rimmandrake\steve_diag\`.
- 🔑 **Reading the raw log from any machine, no Archmagi needed** (measured 2026-11-17). The Desktop's host `ssh` cannot
  reach Steve. The tailnet container can reach Steve:
  `docker exec tailscale-gmail sh -c 'ssh -o BatchMode=yes mandrake@100.115.10.14 "<cmd>"'`. The probe log is
  `/mnt/c/SteveDesktop/diag/logs/watch.log` (4262 CYCLE lines as of 2026-11-18T01:00Z).

Terms in this file:

- "Steve" is the machine SteveDesktop.
- The register probe is `regprobe.exe` (the section "The register probe").
- `RPCONTROL ok=1` in `regprobe.log` means that the probe's control passed on a CPU. The control plants faults at each
  probe start. The control passes when the probe classes each planted fault, and a clean hold, correctly.
- An `RPFAULT` line in `regprobe.log` is one wrong register.
- The watch is the old fault watch (`watch2.ps1`, log `watch.log`). The watch is retired since 2026-11-23.
- The audio driver is the Windows kernel driver `AVoluteSS3Vad`.
- The lane is the SteveDesktop test lane.

## 🔴 `AVoluteSS3Vad` is OFF for good (2026-11-21): the cure is in place

- **What was turned off:** the ASUS Sonic Studio kernel audio driver `AVoluteSS3Vad` (PnP "Sonic Studio Virtual Mixer").
  The driver's registry `Start` is 4 (Disabled). The original value was 3. Nothing was uninstalled. No audio default was
  changed.
- **Why:** the fault needs this driver (the sections below). The owner said on 2026-11-21 that SteveDesktop is otherwise
  unused. So its sound is unused.
- **The test boot was CLEAN** (19:52:06Z). The driver was off. The other nine vendor drivers were loaded. The lane's own
  `rw_game.sh up` started the game.
  - The probe ran 10 cycles with the game up, 3.8 to 48.7 min after the start. All cycles were clean, 18/18 CPUs. The
    fault watch was clean 10 of 10.
  - With the split's boot 1 and the unload test's B, the driver off was clean in 3 of 3 boots.
  - After one more reboot (20:48:58Z) the driver was still `Start=4` and absent from `driverquery /v`. Nothing had
    re-enabled the driver.
  - Record: `D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_driver_off_for_good.md`.
- **A silent return is seen:**
  - The lane's preflight (`infrastructure/stevedesktop/preflight.py`, check `audio_driver`) refuses every job while the
    driver is loaded or re-enabled.
  - `fault_monitor.py` writes `steve_audio_driver.json` every tick. Its `check` fails on LOADED or ENABLED.
- **To turn it back on:** run one command in an admin PowerShell on Steve, then reboot. The command is
  `reg add HKLM\SYSTEM\CurrentControlSet\Services\AVoluteSS3Vad /v Start /t REG_DWORD /d 3 /f`.
  - The fault then returns.
  - Also set `TESTQ_PREFLIGHT_AUDIO_DRIVER=0` in `testcentre_env.sh`. Otherwise the lane refuses every job.
  - Detail: `infrastructure/stevedesktop/RUNBOOK.md`.

## The register probe (running since 2026-11-20)

- Task `SteveDiag Register Probe` (SYSTEM, at startup) runs `C:\SteveDesktop\diag\regprobe\regprobe.exe` every 300 s.
  - The probe visits each logical CPU, in a random order. On each CPU the probe holds fixed patterns in three register
    sets:
    - all 16 YMM registers (steady, and cut by context switches);
    - all 16 XMM registers (legacy SSE);
    - 14 general registers.
  - The probe compares all bits with compiled-in answers. Classes: `upper_half_loss`, `lower_half_error`, `sse_error`,
    `scalar_error`.
  - The log is `C:\SteveDesktop\diag\logs\regprobe.log`. The `rm-steve-fault` tick mirrors the log.
  - To read the log, run `python3 src/RimMandrake/Utils/testq/fault_monitor.py regprobe` (exit 0 CLEAN, 1 FAULT,
    2 UNMEASURED).
  - Source: `src/RimMandrake/Utils/steve_cpu_retest/regprobe.c`. RED/GREEN readings:
    `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/regprobe_red_green/README.md`.
- **The register probe is the one tracker** (owner, 2026-11-23: *"We should only have whatever the most modern tracker
  installed to monitor the situation, that's IT."*).
  - The monitor (`rm-steve-fault.timer`) makes the fault windows from the probe's cycles.
  - The watch (`watch2.ps1`), its heat sampler, the CPU soak and the CPU retest are retired: their tasks are gone from
    Steve, their code is gone from the repo, their logs stay as evidence.
  - While both probes ran (2026-11-20 20:05Z to 2026-11-21 20:48Z), 19 boots faulted. The register probe saw 17 of them
    and the watch saw 16 [measured]. Each missed boot had one or two bad cycles. A lasting fault (the 14 boots to
    2026-11-21 03:29Z) the probe saw 14 of 14 times. A single short fault may pass unseen in one boot.
  - A new fault window, or the audio driver loaded again, wakes the sleeping ticket `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`
    (`ingest.wake_fault_ticket`).
  - The 12 h periodic reboot runs only while a fault or the loaded audio driver was seen in the last 48 h (`fault_monitor.fault_shown`).

## Live catch, boot 2026-11-20 20:05:07Z (read 2026-11-20 20:21-20:26Z over ssh, read-only)

In this section, "this boot" and "today" mean the boot of 2026-11-20 20:05:07Z and that day.

- **Turbo is OFF in this boot, as in the 66 h soak boot** [measured].
  - Balanced plan, PROCTHROTTLEMAX AC = 99. At 20:22Z with RimWorld up, `% Processor Performance` was 97 and
    `Processor Frequency` was 3596 MHz on every CPU.
  - No script under `C:\SteveDesktop` writes a processor power setting, the soak included. The only `powercfg` writes are
    sleep, hibernate and monitor in `bootstrap.ps1` lines 311-318.
  - So the soak did not change turbo. The soak's clean 66 h ran at the same turbo-off setting as today.
- **A 1.30 V reading is not a turbo sign** [measured, `watch.log` per boot].
  - Turbo-off boots 11-13 20:45Z, 11-14 09:34Z, 11-15 05:11Z and 11-15 08:57Z have 50, 47, 1 and 18 cycles at 1.2 V or
    more (max 1.315-1.325 V).
  - Today's 1.302 V is the 20:13Z cycle (cold load, 66 C). The next cycles read 1.012 and 1.017 V.
  - In the soak boot only 19 cycles carried vcore (max 1.032 V). So vcore under Prime95 load is UNMEASURED.
- **The fault** [measured, `regprobe.log`]: 4 probe cycles this boot.
  - 20:08:44Z was clean (before RimWorld started, 20:10:14Z).
  - 20:13:42Z, 20:18:44Z and 20:23:44Z were all `upper_half_loss` on logical CPU 0 only. In these cycles, 16 of 16 AVX
    holds were wrong, SSE and scalar were right, and the other 17 CPUs were clean.
  - The watch agrees (`bad_cpus=[0]` at 20:13, 20:18, 20:23Z).
  - The 20:23:44Z cycle faulted after both lane jobs ended (20:22:18Z), with RimWorld still up. So the fault does not
    follow job start and end.
  - Whether the fault follows the game process is UNMEASURED: the game has been up since before the onset.
- **CPU 0 under load** [measured, one 3 s sample at 20:22Z].
  - `Interrupts/sec` was 4221 on CPU 0, the highest of 18 (even CPUs 1926-3178, odd CPUs 484-1465).
  - `% Interrupt Time` 0.5 and `% DPC Time` 0.5 were no higher than on the others (max 1.0).
  - Third-party ring-0 drivers running: AsIO2, GLCKIO2, ene (EneTechIo), MsIo64, CorsairLLAccess, cpuz154 (CPUID),
    PawnIO (the sensor sampler's MSR driver), AVoluteSS3Vad (audio enhancer), CyberLink CLFCL, Dropbox dbx, Google
    Drive, Hasleo disk/Dokan, wintun, NVIDIA, Intel, Realtek.
  - None is anti-cheat. None is known to us to use AVX in kernel or hook context switches.
  - The one component that saves and restores every CPU's full register state is the hypervisor itself.
- **Hypervisor ON** [measured]: `HypervisorPresent` True, VBS status 2 (running, no security services), WSL2 `vmmem` up.
  `bcdedit {current}` has no `hypervisorlaunchtype` line. `numproc 18`.
- **Remote access is Windows-native** [measured]. `sshd` is `C:\Windows\System32\OpenSSH\sshd.exe` (Automatic) behind the
  Windows Tailscale service `tailscaled.exe` (Automatic), address 100.118.241.96. The shell is PowerShell. Remote access
  does not depend on WSL2.
- Two jobs overlapped the fault: `J20261118T093145Z-70df7c` (FlowWorks, 20:07:00-20:18:16Z) and
  `J20261118T093156Z-5dcd3d` (FlowWorks, 20:19:38-20:22:18Z). Both were REFUSED, cause HARNESS `stale_load`. The restart
  onto the composed list failed: `rimflow bridge idle` gave no verdict.
- The vendor-software section below was written before the cause was known. Today's one-CPU shape fits a per-CPU state loss (CPU defect, driver or
  hypervisor). The shape does not tell those apart.

## 🔴 The +0.100 V raise is stored in the BIOS, is not visible in the sensors, and did not cure the fault (MEASURED 2026-11-20)

Bad-cycle counts of five boots: three before the raise, and the two after it. These five boots hold 2326 cycles. Every
boot: `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/package/digest/watch_per_boot.tsv`.

| boot (UTC) | cycles | bad cycles | bad share | uptime at last read |
|---|---|---|---|---|
| 2026-11-07 17:52 | 1416 | 774 | **55%** | 118.1 h |
| 2026-11-14 09:37 | 145 | 129 | **89%** | 12.1 h |
| 2026-11-15 09:00 | 652 | 231 | **35%** | 54.3 h |
| **2026-11-17 15:35** (first post-raise) | 51 | **2** | **3.9%** | 4.2 h |
| **2026-11-17 19:54** (second post-raise) | 62 | **0** | **0%** | 5.1 h |

- **The raise is stored in the BIOS.** The UEFI variables, read 2026-11-20, show CPU Core/Cache Voltage = Offset Mode,
  sign +, offset field raw value 20. That value is +0.100 V if the unit is ASUS's 0.005 V step.
- **The raise is not visible in the sampler's vcore or in temperature:**
  - Turbo-off boots before the raise read vcore about 1.026-1.029 V and hottest core about 41-42 C at idle. The
    post-raise boots read 1.030-1.031 V and 41 C.
  - The sampler reads LibreHardwareMonitor's CPU "CPU Core" voltage. That voltage is probably the CPU's VID request, not the
    delivered voltage [guess ~75%].
  - An earlier version of this bullet said the raise was visible because vcore's spread and the mean temperature fell.
    That version compared post-raise cycles with a pre-raise set that included the turbo-on boots (1.31 V, 58 C). So it
    measured the turbo change, not the raise.
  - Report and data: `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/REPORT.md`.
- **The fault still fired after the raise.** Window `F20261117T153258Z` opened 4.13 h into the first post-raise boot. CPUs
  8 then 7 had one bad cycle each. The positive control (`inject_exit=1 clean_exit=0`) passed on both boots, so the
  instrument could see.
- **Severity dropped by about an order of magnitude** (2 bad cycles vs 231 in the previous window;
  3.9% vs 35–89% of cycles). That is the shape of a **marginal** fault whose margin improved. It is not the shape of a
  cured fault. `[measured]`
- 🔴 **Do not read the current 0-bad boot as a cure.** 62 clean cycles over 5.1 h is well inside what the pre-raise boots
  did between windows (one pre-raise boot ran 44 cycles / 3.6 h with 1 bad). The counting window set by the item runs
  to **2026-11-20T15:33Z**. Only then is zero meaningful.

## The 72 h Prime95 soak (2026-11-18 to 2026-11-20, retired)

- The soak and its reader are retired (2026-11-23). Its log stays at `C:\SteveDesktop\diag\soak\soak.log`; the code is in
  git history (`src/RimMandrake/Utils/steve_cpu_retest/`, before 2026-11-23).
- The 2026-11-17 six-hour soak was **not** cut by a fault. A Conductor helper wrote the soak's STOP file at 19:16:56Z.

## The RAM test: done, clean (MEASURED 2026-10-31)

- Windows Memory Diagnostic, Basic, 1 pass: no errors (events 1101/1201, 18:57Z).
- In-OS RAM walks: 85 GB (faulty CPU 2 excluded) 0 bad; 108 GB on a fresh 20-CPU boot 0 bad.
- No WHEA events. RAM is clean within that coverage. RAM is not the fault's cause on present evidence.

## The fault's shape (MEASURED)

- 🔑 **The wrong results are a loss of the upper 128 bits of the 256-bit AVX registers** (measured 2026-11-20).
  - Every wrong floating-point result in `watch-chk.log` equals the right answer with the two upper lanes turned to the
    x86 default NaN, on every CPU and day, including both post-raise bad cycles.
  - The fault is register-state loss, not random arithmetic noise. A CPU defect, a kernel driver or Hyper-V can each cause
    such a loss. The 2026-11-21 pair of tests named the kernel driver `AVoluteSS3Vad`.
  - The 2026-10-31 `stevecheck hold` test cannot see the loss: it compares two registers that would both be zeroed. So
    its clean result is void.
  - Detail: `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/REPORT.md`.
- The fault is wrong SIMD results (Prime95 rounding, `stevecheck`, sha256 distinct digests) on a logical CPU. The fault is
  acquired during uptime and held until a reboot. Every reboot so far cleared the fault.
- 10-26 it was CPU 18; 10-31 CPU 2 under `numproc 18`. So a masked core cures nothing.
- 🔴 **Not established (2026-11-17): the post-flash onsets are too few to say the flash changed anything.**
  Three-or-four short onsets against ONE pre-flash observation is not a changed distribution. Nothing controlled for
  workload, detection cadence or settings. Read the next bullet as timings, not as a finding.
- After the BIOS 3401 flash (new microcode) onsets came SOONER: 3.30, 0.88, 2.88 h into a boot (fault_monitor
  windows F20261101T035219Z, F20261101T164245Z, F20261103T195921Z), against ~5 days once before the flash.
  Inside a window the bad CPU wanders from cycle to cycle, with clean cycles between, until the reboot.
- So old microcode is ruled out as the sole cause, and "one dead core" does not fit.

## What the fault does to jobs (MEASURED, one stack)

- A modcheck run that dies "exit 5, no sheet" is a python.exe process that an access violation in pure CPython code
  (`ast.parse`) killed, inside a fault window. The measured case is `J20261103T233438Z-aa0482` in `F20261103T195921Z`.
  Since the 10-31 reboot, 1 of 42 in-window jobs crashed and 0 of 57 outside. Census:
  `infrastructure/state/evidence/MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET.md`.
- A cold load can die in the mono JIT (`0xE0000001`, RaiseException under `mono_unity_jit_cleanup`) before the monitor
  reads bad. This happened 11-03 and 11-06, each 6-7 min before first_bad and outside the window as recorded. So ingest
  files a repair item. Table and odds: `infrastructure/state/evidence/HARNESS_REPAIR_CAUSE_4F477502.md`.
- A cold-load death is not always the CPU fault. One job died INVALID/LOAD on a native `RaiseException` in the mono JIT
  under HugsLib's Harmony `PatchAll`, before any JawaBench code ran. The same job loaded fine when resubmitted. So read
  `Player.log`'s stack before you blame the last thing deployed.
- For a mono JIT abort (`0xE0000001`) that precedes the monitor's first_bad by 6-7 min, `mono_profiler_init_etw` in the
  note is only the thread-start tail. Read `crash.dmp` and first_bad before you touch the harness.

## Tested and falsified (2026-11-04): vendor software callers holding CPU state

The cause is a kernel driver, not its callers (§`AVoluteSS3Vad` is OFF for good, and "Result" below).

A fault that persists until reboot and spans many cores fits a machine-wide setting that a reboot resets (MSRs,
voltage/ratio offsets, SMBus/IO writes) better than a marginal core. Steve runs several ring-0 MSR/IO drivers and
their callers: ASUS AI Suite (`asComSvc`, `AsIO2`), Corsair iCUE (`CorsairService`, `CpuIdRemote64` via the
CPUID `cpuz154` driver, `CorsairLLAccess`), Aura `LightingService` (`GLCKIO2`, `ene`), `MsIo64`.

**A/B started 2026-11-04T03:40:20Z** (boot 02:45:13Z, clean at that time). The callers above were set Disabled and
stopped. `cpuz154` and `CorsairLLAccess` were unloaded. Kernel drivers with System start stay loaded but have no caller.
The only Corsair device is a keyboard (no AIO), so cooling falls back to BIOS fan curves. Original start modes:
`C:\SteveDesktop\diag\driver_ab_original.json`; revert: `C:\SteveDesktop\diag\driver_ab_revert.ps1`.

How to read the A/B:

- Baseline onsets on BIOS 3401 are all ≤ 3.3 h.
- A fault window that opens after 03:40:20Z falsifies the vendor-software hypothesis. Then hardware stays the lead: CPU
  or VRM/board.
- 12 h or more of clean uptime with the callers off is evidence for the hypothesis.

## Result

**FALSIFIED (MEASURED 2026-11-04).** Three fault windows opened with the callers off
(`python3 src/RimMandrake/Utils/testq/fault_monitor.py report`):

| window | boot | onset | first bad | CPUs | hottest core at onset |
|---|---|---|---|---|---|
| F20261104T024513Z | 02:45:13Z (A/B began mid-boot) | 0.96 h | 03:43:02Z | 2 | UNMEASURED |
| F20261104T035722Z | 03:57:22Z, callers off from boot | 4.46 h | 08:25:14Z | 16 | 61 °C, vcore max 1.302 V |
| F20261104T083546Z | 08:35:46Z, callers off from boot | 0.88 h | 09:28:37Z | 16 | 56 °C, vcore max 1.315 V |

- The first window opened on the boot where the A/B started. So state set before 03:40Z could explain that window. The
  other two windows opened on clean boots with the callers off.
- A read at 2026-11-04T10:00Z (boot 09:38:00Z) showed every caller still Disabled and stopped. `cpuz154` and
  `CorsairLLAccess` were not loaded. No SCM start event for them existed since the disable
  (`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\verify_g3.out`).
- 🔴 **Corrected 2026-11-17:** this line read "Onsets with the callers off (4.46 h, 0.88 h) fall inside the baseline
  range". That statement is FALSE. The stated baseline is ≤ 3.3 h (line 46 of the text before this correction; "How to read the A/B" in this text), so 4.46 h is
  OUTSIDE the baseline. An independent reviewer caught the contradiction.
- The falsification does not depend on that statement. The A/B tested whether any window opens with the callers off.
  Three windows did. Two of them opened on clean boots that began with the callers already off.
- **Software that calls these vendor drivers is not the cause.**
- What 4.46 h does mean: onset timing is NOT tightly bounded. So "all ≤ 3.3 h" was never a safe baseline either.
- There are 4 post-flash onsets (3.30, 0.88, 2.88, 4.46 h) against ONE ~5-day pre-flash observation. So the claim that
  the flash made onsets sooner is UNMEASURED, not measured. The samples are too few, and workload, detection cadence and
  settings were uncontrolled.

Not excluded:

- The System-start drivers `AsIO2`, `GLCKIO2`, `ene` and `MsIo64` stayed loaded, with no known caller running.
- `iCUE.exe`, the user-mode app, kept running. But `iCUE.exe` reaches hardware only through the disabled services.

Heat at onset is ordinary (56–61 °C), so thermal runaway is not the trigger. The drivers left loaded here are the ones
that the 2026-11-21 boot below unloaded. With them unloaded, the fault did not come.

Reverted 2026-11-04T10:00:58Z: original start modes restored, services running again
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\revert_g3b.out`). 🔴 `C:\SteveDesktop\diag\driver_ab_revert.ps1`
does nothing on Windows PowerShell 5 (the JSON array arrives as one object). Use `driver_ab\revert2.ps1` instead.

## 🔴 With the vendor kernel drivers unloaded, the fault did not come (MEASURED 2026-11-21, one boot, A-B-A)

Item `RIMMANDRAKE_BOOT_STEVE_NO_LIGHTING_DRIVERS_LAST_SUSPECT_BUT_CPU`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_driver_unload.md` and its `drvtest\` folder.

- **The set (16), each set to registry `Start=4` and the machine rebooted:**
  - Kernel drivers: `Asusgio2` (AsIO2.sys), `EneTechIo` (ene.sys), `GLCKIO2`, `MSIO` (MsIo64.sys), `CorsairLLAccess64`,
    `cpuz154` (CPUID), `PawnIO` (our own stevetemp sensor driver), `CorsairVBusDriver`, `CorsairVHidDriver`,
    `AVoluteSS3Vad` (ASUS Sonic Studio Virtual Mixer: the default speaker endpoint, so the game's audio passes through
    the mixer).
  - The drivers' six caller services.
  - Measured after the boot: none of the 10 drivers loaded, and no other driver was added (no WinRing0 fallback). NVIDIA,
    Intel, Realtek and the file-system drivers stayed.
- **A, drivers loaded:** 6 of 6 boots on 2026-11-21 between 00:40Z and 03:30Z faulted, with a first fault 10–15 min after
  boot (regprobe.log; whether a game ran in each boot was not checked).
- **B, drivers unloaded (boot 11:44:18Z):** RPCONTROL ok=1. RimWorld ran the same 315-mod list, started natively at
  11:45:29Z. The probe ran 10 cycles with the game up, 4 to 49 min after the start, **all clean**, 18/18 CPUs each,
  0 RPFAULT lines. Before tonight, 7 of 7 boots (2026-11-20 from 20:05Z, `night_20261120\steve_hypervisor_test.md`) faulted 3–14 min after a game start, with the hypervisor on or off.
- **A again, drivers restored (boot 12:41:17Z):** the same native launcher ran at 12:43:42Z. **Fault** at 12:46:35Z,
  CPU 2, `upper_half_loss`, 2.9 min after the start.
- **What this means:** a driver in the set is needed for the fault [guess ~90%].
  - This is one clean boot. One clean boot is evidence, not proof.
  - The CPU is not excluded as a contributor (the fault could need both). But a CPU defect alone does not explain a clean
    49 min.
  - The set mixes two kinds: the lighting/monitoring drivers (port and MSR access) and one kernel audio driver. Each kind
    can explain a game-start trigger (the game opens an audio stream, and iCUE and Aura react to a game). The split below
    names the audio driver.
- 🔑 **Disabling a vendor service does not unload a System-start driver.** The 2026-11-04 A/B above stopped the callers
  only. Set the driver's own `Start` to 4 and reboot. Then check `driverquery`.

## 🔴 The ASUS Sonic Studio kernel audio driver `AVoluteSS3Vad` is needed for the fault (MEASURED 2026-11-21, both-ways pair)

Item `RIMMANDRAKE_SPLIT_STEVE_DRIVER_SET_AUDIO_DRIVER_ALONE_FIRST`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_driver_split.md` and its `drvsplit\` folder. The method is the
same as in the unload test: the same 315-mod native game launch, the register probe with RPCONTROL ok=1 in every boot,
and `driverquery /v` checked after each boot.

| boot (UTC) | Start=4 | game start | probe after game start | reading |
|---|---|---|---|---|
| 13:10:20Z | `AVoluteSS3Vad` only (the other nine drivers loaded) | 13:11:53Z | 10 cycles, 3.8 to 48.8 min, all clean | CLEAN |
| 14:09:10Z | the other nine drivers and the six callers (`AVoluteSS3Vad` loaded) | 14:10:28Z | fault at 14:14:28Z, 4.0 min, CPU 0 `upper_half_loss` | FAULT |

- With the unload test: `AVoluteSS3Vad` off gave a clean boot 2 of 2 times. `AVoluteSS3Vad` loaded gave a fault in 2 of 2
  test boots. The nine lighting and monitoring drivers are neither needed (boot 2) nor sufficient (boot 1).
- The driver: `AVoluteSS3Vad.sys`, "A-Volute Sonic Suite VAD" 10.0.10011.16384, file date 2021-10-14; PnP "Sonic Studio
  Virtual Mixer" 1.0.2.0. The driver is the default speaker endpoint over Realtek HD Audio 6.0.8960.1. With the driver
  off, the only working audio endpoint was "Realtek Digital Output".
- The shape (upper YMM halves lost on a user thread) fits a kernel driver that uses AVX without saving the extended
  state [guess ~70%].
- UNMEASURED: a newer Sonic Studio build. (Driver loaded, no stream through it: measured below.)
- That test left nothing disabled (end state measured 14:22Z). The driver was turned off for good later the same day (the
  section at the top).

## 🔴 With `AVoluteSS3Vad` loaded but the game's audio on Realtek, the fault did not come (MEASURED 2026-11-21, one boot)

Item `RIMMANDRAKE_TEST_STEVE_AUDIO_DEFAULT_ON_REALTEK_DRIVER_STILL_LOADED`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_audio_default_test.md` and its `audiodef\` folder. The method is
the same as in the split: the same 315-mod native game launch, the register probe with RPCONTROL ok=1, and
`driverquery /v` after the boot. No driver was changed.

- **The boot (14:40:04Z):** all 10 drivers were loaded. `AVoluteSS3Vad` was Running and its endpoints were active.
  - All 6 default devices (playback and recording, each for Console, Multimedia and Communications) were moved off Sonic
    Studio and read back. Playback went to "Realtek Digital Output". Recording went to Realtek "Stereo Mix" (enabled for
    the test; no Realtek microphone input was active).
  - The defaults survived the reboot.
- **Where the game's audio went** [measured 2.1 and 22.3 min after start, from the desktop session]: `RimWorldWin64` held
  an ACTIVE session on Realtek Digital Output. The Sonic Studio speaker endpoint held only the idle system session.
  - Over ssh the session list shows only the system sessions. So read the list from the desktop session (a scheduled task
    with an Interactive principal).
- **Reading: CLEAN.** The probe ran 10 cycles with the game up, 2.9 to 47.9 min after the start, all clean, 18/18 CPUs,
  0 RPFAULT lines. With the defaults on Sonic Studio and the same driver set, the same method faulted at 2.9 and 4.0 min
  (and the fault came on each of the 13 boots before this one).
- **What this means:** the fault needs the game's audio to pass through the Sonic Studio virtual mixer; the driver loaded
  with no game stream through the mixer is not enough [guess ~80%: one boot, evidence, not confirmed]. Playback and
  recording defaults moved together, so this boot does not split them.
- The only active Realtek playback endpoint is the S/PDIF "Realtek Digital Output". The analog Realtek "Speakers" endpoint
  reads unplugged. So this workaround may leave analog speakers silent [guess ~60%].
- Nothing was left changed: defaults restored and read back, Stereo Mix disabled again, the full endpoint list identical
  to before.
- 🔑 **The Windows default audio device can be read and set with no install:** use inline C# over the Core Audio COM
  interfaces (`IMMDeviceEnumerator`, `IPolicyConfig.SetDefaultEndpoint`). The script is
  `C:\SteveDesktop\diag\audiodef\audiodef.ps1`. A default set to an unplugged endpoint returns success but does not take
  effect. So read the default back.

## 🔴 Windows per-app audio routing does not move a fresh RimWorld start off Sonic Studio; with the game on Sonic Studio the fault came (MEASURED 2026-11-21, one boot)

Item `RIMMANDRAKE_ROUTE_STEVE_RIMWORLD_AUDIO_TO_REALTEK_ONLY_THE_GAME`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_audio_per_app_test.md` and its `perapp\` folder. The method is
the same as in the default test: the same native launch, the register probe with RPCONTROL ok=1, and `driverquery /v`
after the boot. No driver and no system default was changed.

- **The route:** RimWorldWin64.exe (D:\SteamLibrary path) Render -> "Realtek Digital Output". A script set the route with
  the per-app mechanism of Settings > App volume and device preferences.
  - The mechanism is the WinRT factory `Windows.Media.Internal.AudioPolicyConfig`, downlevel IID `{2a59116d-...}` on
    19045. The script is `C:\SteveDesktop\diag\perapp\perapp.ps1`, run as sjlewis in the desktop session.
  - Windows keeps the route in `HKCU\Software\Microsoft\Multimedia\Audio\DefaultEndpoint\<hash>`.
  - Set on a running game, the route moved the live stream to Realtek. The 6 system defaults stayed on Sonic Studio. A second
    app's stream stayed on Sonic Studio.
- **After a reboot (boot 15:52:46Z):** the route was still in the registry and read back for the new game process. But a
  fresh start opened its audio on Sonic Studio anyway, both with the native task and with the lane's `rw_game.sh up` (2 of
  2 launches). **Per-app reading: UNMEASURED; the route was removed.**
- **The same boot as a control:** all drivers were loaded, the defaults were on Sonic Studio, and the game's session was
  measured ACTIVE on Sonic Studio. **Fault at 4.1 min** (15:58:13Z, CPU 5, `upper_half_loss`). With the default test above
  (game on Realtek: clean 48 min), the fault follows the game's audio through the Sonic Studio mixer [guess ~88%: one boot
  each side].
- 🔑 sjlewis's `PolicyConfig\PropertyStore` holds about 700 per-app VOLUME records (not routes). The API's
  `ClearAllPersistedApplicationDefaultEndpoints` would also clear every other app's route. So reset one app with
  `SetPersistedDefaultAudioEndpoint(pid, flow, role, NULL)` instead.

## 🔴 Moving the game's sound off Sonic Studio about 9 s after the start still gave one fault reading (MEASURED 2026-11-21, one boot)

Item `RIMMANDRAKE_KEEP_STEVE_LANE_GAME_SOUND_OFF_SONIC_STUDIO_AT_LAUNCH`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_lane_launch_audio.md` and its `laneaudio\` folder. The method is
the same as in the tests above.

- **No launch switch gives "no audio".** Unity 2022.3.35f1 (RimWorld 1.6's engine) documents no player argument for audio, and
  "Disable Unity Audio" is a build setting. RimWorld reads only `quicktest`, `legacy-xml-deserializer` and
  `savedatafolder`. `volumeMaster` 0 in Prefs (already set on Steve) still gives an ACTIVE session on Sonic Studio.
- **The step:** `rw_game.sh up` starts `infrastructure/stevedesktop/game_audio_route.ps1` before the game.
  - The watcher (`game_audio_route.ps1`) waits for the game's own render session. Then it sets the per-app route for that
    pid to "Realtek Digital Output" (reset, then set), and checks that the stream moved.
  - `up` prints `audio route: ROUTED ...` (the log is `audio_route.log` in the game's log folder). No system default
    changes.
- **The lane-style launch after a reboot (boot 16:47:59Z, all drivers loaded, defaults on Sonic Studio):** the game was
  ACTIVE on Sonic Studio from 2.3 s to 9.1 s after start, and ACTIVE on Realtek from 9.4 s. A separate reader saw the game
  on Realtek at 19.6 s and 51 s.
  - The first two route sets (2.2 s, 5.3 s) did not move the stream, and the third one (8.4 s) did. The dev run behaved
    the same way (moved at 8.5 s). So about 7 s on the mixer is the floor with this method [guess ~70%].
- **Boot reading: FAULT, by the 20-min rule** (a fault inside 20 min of the game start is a FAULT reading).
  - The fault watch read `bad_cpus=[14] exits=[1]` in its 16:50:51Z cycle. CPU 14's check ran about 10-14 s after the
    start, just after the 6.8 s on the mixer. That watch read 0 bad cycles in the earlier CLEAN boots (about 100 polls).
  - Then everything read clean: the register probe 10 of 10 cycles, 3.1 to 48.1 min, and the watch 17 cycles.
- **What this means:** the stream on the mixer for a few seconds is enough for at least one wrong result.
  - In the boots where the game stayed on the mixer, the fault came again and again until the reboot; here the fault came
    once, before the move, and not after [guess ~70%: one boot].
  - This reading fits the earlier tests (the fault needs the game's stream to pass the mixer). The reading says that a move after the start
    is not enough. Only a stream that never opens on the mixer can be clean: the system default off Sonic Studio (the
    default test), or the driver off.
- **The step is OFF by default** (`AUDIO_TO=${RW_GAME_AUDIO_TO-}` in `rw_game.sh`; the brief said: on FAULT, remove it).
  The code and its selftest stay. To turn the step on, set `RW_GAME_AUDIO_TO='Realtek Digital Output'`. The per-app route
  was removed and Steve was restored.
