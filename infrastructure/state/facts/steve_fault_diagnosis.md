# SteveDesktop's uptime SIMD fault: what is measured, what is not

Item `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO`. Machine: i9-10900K, ROG STRIX Z490-G, 4×32 GB F4-2666C18.
Live instrument: `python3 src/RimMandrake/Utils/testq/fault_monitor.py report` (timer `rm-steve-fault.timer`,
state `D:\ClaudeWork\rimmandrake\testq\fault_state.json`). Raw evidence: `D:\ClaudeWork\rimmandrake\steve_diag\`.
🔑 **Reading the raw log from any machine, no Archmagi needed** (measured 2026-11-17): the Desktop's host
`ssh` cannot reach Steve, but the tailnet container can —
`docker exec tailscale-gmail sh -c 'ssh -o BatchMode=yes mandrake@100.115.10.14 "<cmd>"'`, with the probe
log at `/mnt/c/SteveDesktop/diag/logs/watch.log` (4262 CYCLE lines as of 2026-11-18T01:00Z).

## The register probe (running since 2026-11-20)

- Task `SteveDiag Register Probe` (SYSTEM, at startup) runs `C:\SteveDesktop\diag\regprobe\regprobe.exe` every 300 s: on
  each logical CPU, in a random order, it holds fixed patterns in all 16 YMM registers (steady, and cut by context switches),
  all 16 XMM registers (legacy SSE) and 14 general registers, and compares all bits with compiled-in answers. Classes:
  `upper_half_loss`, `lower_half_error`, `sse_error`, `scalar_error`. Log `C:\SteveDesktop\diag\logs\regprobe.log`; the
  `rm-steve-fault` tick mirrors it; read it with `python3 src/RimMandrake/Utils/testq/fault_monitor.py regprobe` (exit 0
  CLEAN, 1 FAULT, 2 UNMEASURED). Source and RED/GREEN readings:
  `src/RimMandrake/Utils/steve_cpu_retest/regprobe.c`, `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/regprobe_red_green/README.md`.
- The watch's `heat=UNMEASURED(no_output)` during the 72 h soak had one cause: the soak's step cleanup killed every
  `stevetemp` started since the step began, the watch's own sampler included. Fixed in the repo's `steve_cpu_soak.ps1`
  (it kills only its own sampler); Steve's copy is older and was not replaced, so the next soak deploy carries the fix.

## Live catch, boot 2026-11-20 20:05:07Z (read 2026-11-20 20:21-20:26Z over ssh, read-only)

- **Turbo is OFF in this boot, as in the 66 h soak boot** [measured]: Balanced plan, PROCTHROTTLEMAX AC = 99; at 20:22Z with
  RimWorld up, `% Processor Performance` 97 and `Processor Frequency` 3596 MHz on every CPU. No script under `C:\SteveDesktop`
  writes a processor power setting (the only `powercfg` writes are sleep, hibernate and monitor in `bootstrap.ps1` lines 311-318),
  the soak included. So the soak did not change turbo, and the soak's clean 66 h ran at the same turbo-off setting as today.
- **A 1.30 V reading is not a turbo sign** [measured, `watch.log` per boot]: turbo-off boots 11-13 20:45Z, 11-14 09:34Z, 11-15
  05:11Z and 11-15 08:57Z have 50, 47, 1 and 18 cycles at 1.2 V or more (max 1.315-1.325 V); today's 1.302 V is the 20:13Z cycle
  (cold load, 66 C); the next cycles read 1.012 and 1.017 V. In the soak boot only 19 cycles carried vcore (max 1.032 V), so
  vcore under Prime95 load is UNMEASURED.
- **The fault** [measured, `regprobe.log`]: 4 probe cycles this boot; 20:08:44Z clean (before RimWorld started, 20:10:14Z); 20:13:42Z,
  20:18:44Z and 20:23:44Z all `upper_half_loss` on logical CPU 0 only (16 of 16 AVX holds, SSE and scalar right; the other 17
  CPUs clean). The watch agrees (`bad_cpus=[0]` at 20:13, 20:18, 20:23Z). The 20:23:44Z cycle faulted after both lane jobs ended
  (20:22:18Z), with RimWorld still up, so the fault does not follow job start and end; whether it follows the game process is
  UNMEASURED (the game has been up since before the onset).
- **CPU 0 under load** [measured, one 3 s sample at 20:22Z]: `Interrupts/sec` 4221 on CPU 0, the highest of 18 (even CPUs
  1926-3178, odd CPUs 484-1465); `% Interrupt Time` 0.5 and `% DPC Time` 0.5, no higher than the others (max 1.0). Third-party
  ring-0 drivers running: AsIO2, GLCKIO2, ene (EneTechIo), MsIo64, CorsairLLAccess, cpuz154 (CPUID), PawnIO (the sensor
  sampler's MSR driver), AVoluteSS3Vad (audio enhancer), CyberLink CLFCL, Dropbox dbx, Google Drive, Hasleo disk/Dokan, wintun,
  NVIDIA, Intel, Realtek. None is anti-cheat; none is known to us to use AVX in kernel or hook context switches. The one
  component that saves and restores every CPU's full register state is the hypervisor itself.
- **Hypervisor ON** [measured]: `HypervisorPresent` True, VBS status 2 (running, no security services), WSL2 `vmmem` up;
  `bcdedit {current}` has no `hypervisorlaunchtype` line; `numproc 18`.
- **Remote access is Windows-native** [measured]: `sshd` is `C:\Windows\System32\OpenSSH\sshd.exe` (Automatic) behind the Windows
  Tailscale service `tailscaled.exe` (Automatic), address 100.118.241.96; the shell is PowerShell. It does not depend on WSL2.
- Jobs that overlapped the fault: `J20261118T093145Z-70df7c` (FlowWorks, 20:07:00-20:18:16Z) and `J20261118T093156Z-5dcd3d`
  (FlowWorks, 20:19:38-20:22:18Z), both REFUSED, cause HARNESS `stale_load` (the restart onto the composed list failed: `rimflow bridge idle` gave no verdict).
- The vendor-software section below still stands: today's one-CPU shape fits a per-CPU state loss (CPU defect, driver or
  hypervisor) and does not tell those apart.

## 🔴 The +0.100 V raise is stored in the BIOS, is not visible in the sensors, and did not cure the fault (MEASURED 2026-11-20)

Per-boot bad-cycle counts from the whole probe log, and the pre/post split over all 3898 cycles:

| boot (UTC) | cycles | bad cycles | bad share | uptime at last read |
|---|---|---|---|---|
| 2026-11-07 17:52 | 1416 | 774 | **55%** | 118.1 h |
| 2026-11-14 09:37 | 145 | 129 | **89%** | 12.1 h |
| 2026-11-15 09:00 | 652 | 231 | **35%** | 54.3 h |
| **2026-11-17 15:35** (first post-raise) | 51 | **2** | **3.9%** | 4.2 h |
| **2026-11-17 19:54** (second post-raise) | 62 | **0** | **0%** | 5.1 h |

- **The raise is stored in the BIOS** (UEFI variables read 2026-11-20: CPU Core/Cache Voltage = Offset Mode, sign +, offset
  field raw value 20, which is +0.100 V if the unit is ASUS's 0.005 V step). **It is not visible in the sampler's vcore or in
  temperature:** turbo-off boots before the raise read vcore about 1.026-1.029 V and hottest core about 41-42 C at idle; the
  post-raise boots read 1.030-1.031 V and 41 C. The sampler reads LibreHardwareMonitor's CPU "CPU Core" voltage, probably the
  CPU's VID request, not the delivered voltage [guess ~75%]. An earlier version of this bullet said the raise was visible
  because vcore's spread and the mean temperature fell; that compared post-raise cycles with a pre-raise set that included the
  turbo-on boots (1.31 V, 58 C), so it measured the turbo change, not the raise. Report and data:
  `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/REPORT.md`.
- **And the fault still fired**: window `F20261117T153258Z` opened 4.13 h into the first post-raise
  boot, CPUs 8 then 7, one bad cycle each, with the positive control (`inject_exit=1 clean_exit=0`)
  passing on both boots, so the instrument could see.
- **Severity dropped by about an order of magnitude** (2 bad cycles vs 231 in the previous window;
  3.9% vs 35–89% of cycles). That is the shape of a **marginal** fault whose margin improved, not a
  cured one. `[measured]`
- 🔴 **Do not read the current 0-bad boot as a cure.** 62 clean cycles over 5.1 h is well inside what
  the pre-raise boots did between windows (one pre-raise boot ran 44 cycles / 3.6 h with 1 bad). The
  counting window set by the item runs to **2026-11-20T15:33Z**; only then is zero meaningful.

## The 72 h Prime95 soak (started 2026-11-18T01:29Z, planned end 2026-11-21T01:29Z)

Read it: `python3 src/RimMandrake/Utils/steve_cpu_retest/soak_read.py` (exit 0 proven / 1 instrument unproven /
2 stalled or unplanned / 3 unreachable). Task `SteveDiag CPU Soak` (SYSTEM, boot trigger), log
`C:\SteveDesktop\diag\soak\soak.log`. The testq lane is paused to 2026-11-21T03:29Z so no game job or reboot of ours
lands in it. A reboot resumes the same run and logs `SOAK REBOOT` (proven by a deliberate reboot at 01:34Z).
- The 2026-11-17 six-hour soak was **not** cut by a fault: a Conductor helper wrote its STOP file at 19:16:56Z to
  free Steve for testq jobs (32 steps, all PASS); the fault window at 19:35Z came after, during the Pyrelands job.
  Its log is kept at `C:\SteveDesktop\diag\soak\soak_20261117T185136Z_interrupted.log`.
- The soak's "worker busy" yield is blind under SYSTEM (`worker_probe=blind`, measured): only a running RimWorld makes
  it wait (`RIMMANDRAKE_UNBLIND_SOAK_WORKER_PROBE_SYSTEM_SEES_NO_DISTRO`).
- The fault watch (watch2.ps1) keeps running during the soak, and its 4 s checks share CPUs with Prime95 every 5 min.

## The RAM test: done, clean (MEASURED 2026-10-31)

- Windows Memory Diagnostic, Basic, 1 pass: no errors (events 1101/1201, 18:57Z).
- In-OS RAM walks: 85 GB (faulty CPU 2 excluded) 0 bad; 108 GB on a fresh 20-CPU boot 0 bad.
- No WHEA events. RAM is clean within that coverage; it is not the fault's cause on present evidence.

## The fault's shape (MEASURED)

- 🔑 **The wrong results are a loss of the upper 128 bits of the 256-bit AVX registers** (measured 2026-11-20): every wrong
  floating-point result in `watch-chk.log` equals the right answer with the two upper lanes turned to the x86 default NaN, on every
  CPU and day, including both post-raise bad cycles. This is register-state loss, not random arithmetic noise; a CPU defect, a
  kernel driver or Hyper-V can each cause it. The 2026-10-31 `stevecheck hold` test cannot see it (it compares two registers
  that would both be zeroed), so its clean result is void. Detail: `infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/REPORT.md`.
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
Heat at onset is ordinary (56–61 °C), so thermal runaway is not the trigger. The drivers left loaded here are the
ones the 2026-11-21 boot below unloaded; with them unloaded, the fault did not come.

Reverted 2026-11-04T10:00:58Z: original start modes restored, services running again
(`D:\ClaudeWork\rimmandrake\steve_diag\driver_ab\revert_g3b.out`). 🔴 `C:\SteveDesktop\diag\driver_ab_revert.ps1`
does nothing on Windows PowerShell 5 (the JSON array arrives as one object). Use `driver_ab\revert2.ps1` instead.

## 🔴 With the vendor kernel drivers unloaded, the fault did not come (MEASURED 2026-11-21, one boot, A-B-A)

Item `RIMMANDRAKE_BOOT_STEVE_NO_LIGHTING_DRIVERS_LAST_SUSPECT_BUT_CPU`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_driver_unload.md` and its `drvtest\` folder.

- **The set (16), each set to registry `Start=4` and the machine rebooted:** kernel drivers `Asusgio2` (AsIO2.sys),
  `EneTechIo` (ene.sys), `GLCKIO2`, `MSIO` (MsIo64.sys), `CorsairLLAccess64`, `cpuz154` (CPUID), `PawnIO` (our own
  stevetemp sensor driver), `CorsairVBusDriver`, `CorsairVHidDriver`, `AVoluteSS3Vad` (ASUS Sonic Studio Virtual Mixer:
  the default speaker endpoint, so the game's audio passes through it); and their six caller services. Measured after the
  boot: none of the 10 drivers loaded, and no other driver was added (no WinRing0 fallback). NVIDIA, Intel, Realtek and
  the file-system drivers stayed.
- **A, drivers loaded:** 6 of 6 boots on 2026-11-21 between 00:40Z and 03:30Z faulted, with a first fault 10–15 min after
  boot (regprobe.log; whether a game ran in each boot was not checked).
- **B, drivers unloaded (boot 11:44:18Z):** RPCONTROL ok=1; RimWorld (the same 315-mod list, started natively at 11:45:29Z);
  10 probe cycles with the game up, 4 to 49 min after the start, **all clean**, 18/18 CPUs each, 0 RPFAULT lines.
  Before tonight, 7 of 7 boots faulted 3–14 min after a game start, with the hypervisor on or off.
- **A again, drivers restored (boot 12:41:17Z):** the same native launcher at 12:43:42Z; **fault** at 12:46:35Z, CPU 2,
  `upper_half_loss`, 2.9 min after the start.
- **What this means:** a driver in the set is needed for the fault [guess ~90%]. This is one clean boot; it is evidence,
  not proof. The CPU is not excluded as a contributor (the fault could need both), but a CPU defect alone does not explain a
  clean 49 min. The set mixes two kinds: the lighting/monitoring drivers (port and MSR access) and one kernel audio
  driver. Each kind can explain a game-start trigger (the game opens an audio stream, and iCUE and Aura react to a game).
  The split below names the audio driver.
- 🔑 **Disabling a vendor service does not unload a System-start driver.** The 2026-11-04 A/B above stopped the callers
  only. Set the driver's own `Start` to 4 and reboot, then check `driverquery`.

## 🔴 The ASUS Sonic Studio kernel audio driver `AVoluteSS3Vad` is needed for the fault (MEASURED 2026-11-21, both-ways pair)

Item `RIMMANDRAKE_SPLIT_STEVE_DRIVER_SET_AUDIO_DRIVER_ALONE_FIRST`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_driver_split.md` and its `drvsplit\` folder. Same method as the unload test
(same 315-mod native game launch, register probe with RPCONTROL ok=1 in every boot, `driverquery /v` checked after each boot).

| boot (UTC) | Start=4 | game start | probe after game start | reading |
|---|---|---|---|---|
| 13:10:20Z | `AVoluteSS3Vad` only (the other nine drivers loaded) | 13:11:53Z | 10 cycles, 3.8 to 48.8 min, all clean | CLEAN |
| 14:09:10Z | the other nine drivers and the six callers (`AVoluteSS3Vad` loaded) | 14:10:28Z | fault at 14:14:28Z, 4.0 min, CPU 0 `upper_half_loss` | FAULT |

- With the unload test: `AVoluteSS3Vad` off gave a clean boot 2 of 2 times; loaded gave a fault in 2 of 2 test boots. The nine lighting and
  monitoring drivers are neither needed (boot 2) nor sufficient (boot 1).
- The driver: `AVoluteSS3Vad.sys`, "A-Volute Sonic Suite VAD" 10.0.10011.16384, file date 2021-10-14; PnP "Sonic Studio Virtual Mixer" 1.0.2.0.
  It is the default speaker endpoint over Realtek HD Audio 6.0.8960.1. With it off, the only working audio endpoint was "Realtek Digital Output".
- The shape (upper YMM halves lost on a user thread) fits a kernel driver that uses AVX without saving the extended state [guess ~70%].
- UNMEASURED: a newer Sonic Studio build. (Driver loaded, no stream through it: measured below.)
- Nothing was left disabled (end state measured 14:22Z: 16/16 at original Start, 10/10 drivers loaded, HV on, WSL answering, lane resumed).
  What to do about the driver is the owner's and Steve's choice; the options and their costs are in the record.

## 🔴 With `AVoluteSS3Vad` loaded but the game's audio on Realtek, the fault did not come (MEASURED 2026-11-21, one boot)

Item `RIMMANDRAKE_TEST_STEVE_AUDIO_DEFAULT_ON_REALTEK_DRIVER_STILL_LOADED`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_audio_default_test.md` and its `audiodef\` folder. Same method as the split
(same 315-mod native game launch, register probe with RPCONTROL ok=1, `driverquery /v` after the boot). No driver was changed.

- **The boot (14:40:04Z):** all 10 drivers loaded, `AVoluteSS3Vad` Running and its endpoints active. All 6 default devices (playback and
  recording, each for Console, Multimedia and Communications) moved off Sonic Studio and read back: playback to "Realtek Digital Output", recording
  to Realtek "Stereo Mix" (enabled for the test; no Realtek microphone input was active). The defaults survived the reboot.
- **Where the game's audio went** [measured 2.1 and 22.3 min after start, from the desktop session]: `RimWorldWin64` held an ACTIVE session on
  Realtek Digital Output; the Sonic Studio speaker endpoint held only the idle system session. Over ssh the session list shows only the
  system sessions, so read it from the desktop session (a scheduled task with an Interactive principal).
- **Reading: CLEAN.** 10 probe cycles with the game up, 2.9 to 47.9 min after the start, all clean, 18/18 CPUs, 0 RPFAULT lines.
  With the defaults on Sonic Studio and the same driver set, the same method faulted at 2.9 and 4.0 min (and 13 of 13 boots before).
- **What this means:** the fault needs the game's audio to pass through the Sonic Studio virtual mixer; the driver loaded with no game stream
  through it is not enough [guess ~80%: one boot, evidence, not confirmed]. Playback and recording defaults moved together, so this boot does not
  split them.
- The only active Realtek playback endpoint is the S/PDIF "Realtek Digital Output"; the analog Realtek "Speakers" endpoint reads unplugged. So
  this workaround may leave analog speakers silent [guess ~60%]. Nothing was left changed: defaults restored and read back, Stereo Mix disabled
  again, the full endpoint list identical to before.
- 🔑 **The Windows default audio device can be read and set with no install:** inline C# over the Core Audio COM interfaces
  (`IMMDeviceEnumerator`, `IPolicyConfig.SetDefaultEndpoint`); script `C:\SteveDesktop\diag\audiodef\audiodef.ps1`. A default set to an
  unplugged endpoint returns success but does not take effect; read it back.

## 🔴 Windows per-app audio routing does not move a fresh RimWorld start off Sonic Studio; with the game on Sonic Studio the fault came (MEASURED 2026-11-21, one boot)

Item `RIMMANDRAKE_ROUTE_STEVE_RIMWORLD_AUDIO_TO_REALTEK_ONLY_THE_GAME`. Record and raw evidence:
`D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_audio_per_app_test.md` and its `perapp\` folder. Same method as the default test (same native
launch, register probe with RPCONTROL ok=1, `driverquery /v` after the boot). No driver and no system default was changed.

- **The route:** RimWorldWin64.exe (D:\SteamLibrary path) Render -> "Realtek Digital Output", set by script with the per-app mechanism of Settings > App volume
  and device preferences (WinRT factory `Windows.Media.Internal.AudioPolicyConfig`, downlevel IID `{2a59116d-...}` on 19045; script
  `C:\SteveDesktop\diag\perapp\perapp.ps1`, run as sjlewis in the desktop session). Windows keeps it in
  `HKCU\Software\Microsoft\Multimedia\Audio\DefaultEndpoint\<hash>`. Set on a running game, it moved the live stream to Realtek; the 6 system defaults stayed
  on Sonic Studio, and a second app's stream stayed on Sonic Studio.
- **After a reboot (boot 15:52:46Z):** the route was still in the registry and read back for the new game process, but a fresh start opened its audio on
  Sonic Studio anyway, both with the native task and with the lane's `rw_game.sh up` (2 of 2 launches). **Per-app reading: UNMEASURED; the route was removed.**
- **The same boot as a control:** all drivers loaded, defaults on Sonic Studio, the game's session measured ACTIVE on Sonic Studio: **fault at 4.1 min**
  (15:58:13Z, CPU 5, `upper_half_loss`). With the default test above (game on Realtek: clean 48 min), the fault follows the game's audio through the Sonic
  Studio mixer [guess ~88%: one boot each side].
- 🔑 sjlewis's `PolicyConfig\PropertyStore` holds about 700 per-app VOLUME records (not routes). The API's `ClearAllPersistedApplicationDefaultEndpoints`
  would also clear every other app's route: reset one app with `SetPersistedDefaultAudioEndpoint(pid, flow, role, NULL)` instead.
