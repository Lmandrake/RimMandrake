# SteveDesktop CPU fault: evidence, two GPT assessments, and what to buy or test (2026-11-20)

Item `RIMMANDRAKE_REPORT_STEVEDESKTOP_CPU_FAULT_DATA_TO_GPT_TWICE`. Written 2026-11-20 about 12:40 AM PST by a detached BENCH
helper. The owner's order (2026-11-19 ~11:55 PM PST): *"Package up all our findings including the raw data and telemetry
streams nd send it to gpt for assessment as well. Then forward your research to gpt and ask it to expand improve it once
you're done. File all this in a report on Steve desktop."*

Tags: `[measured]` = read or counted from a named package file this run; `[guess ~N%]` = an estimate with its confidence;
`[GPT]` = GPT's statement (its answer files are whole in the package); `UNMEASURED` = nobody has read it. All package paths below
are relative to `D:\ClaudeWork\rimmandrake\steve_cpu_report_20261119\package\` (a copy of every file under 5 MB is beside this
report in `package\`). Times are Pacific unless marked Z (UTC).

---

## 1. The answer

**What is broken.** SteveDesktop really computes wrong answers, and this run found their exact shape: **every wrong
floating-point result the watch logged is what you get when the upper 128 bits of the 256-bit AVX registers are lost (zeroed)**
while the lower 128 bits stay correct [measured: 3 of 3 seeds tested match bit for bit; `digest\chk_mismatch_analysis.md` item 5;
`scripts\fp5.py`]. The two bad cycles after the voltage raise have the same shape [measured: `raw\steve_logs\watch-chk.log`
lines 88531-88557, round 4 on CPUs 8 and 7 gives the NaN-lane value `7ddb450510ba1a62`]. So this is a **register-state loss**, not
random arithmetic noise.

**Which part causes that is not settled.** A CPU defect can do it, and so can software below the application (a kernel driver
that uses AVX without saving the interrupted program's state, Hyper-V/WSL2, firmware/SMM). The facts that point away from "a
failing core": the identical corruption on all 9 physical cores, and even-numbered logical CPUs failing far more than their
hyper-thread siblings on the same core (CPU 2: 591 bad, CPU 3: 34) [measured: `digest\watch_per_cpu_by_era.tsv`]. The facts that
point toward hardware: the fault followed logical CPUs in independent programs (Prime95, openssl, python), and it fell sharply
after the voltage raise [measured].

| who | CPU silicon | board / VRM / socket / power | memory | PSU | software below the app (driver, Hyper-V, firmware) | other |
|---|---|---|---|---|---|---|
| our verdict before this run (Conductor, 2026-11-17/18) | "the CPU; replacement is the route" | — | — | — | — | — |
| earlier independent review, 2026-11-17 (`findings\STEVE_CPU_SWAP_SECOND_OPINION_2026-11-17.md`) | 45% | 30% | 10% | 5% | (in "other") | 10% |
| GPT, blind (call 1) | 30% | 10% | 3% | 2% | **53%** | 2% |
| GPT, against our verdict (call 2) | "serious alternative" | "serious alternative" | downgraded | — | **leading** | — |
| this run, after the register finding | 35% | 12% | 4% | — | 45% | 4% |

The last row is `[guess ~55%]` that the order is right; none of the rows is a statistic. GPT (call 2) puts the chance that a
known-good CPU swap **alone** ends the fault at **about 40%** [GPT]; the 2026-11-17 review said 40-60%.

**How sure.** That the fault is real and is a loss of the upper register halves: high [measured]. That the CPU is the cause:
about a one-in-three chance [guess]. Our earlier verdict "the CPU; replacement is the route" did not follow from its evidence:
the voltage raise failing to cure the fault does not separate the CPU from the board or from software (both GPT calls say this;
I agree).

**Since the voltage raise (Tue 11-17 7:28 AM PST) the fault is much rarer**: 2 bad cycles in 770 against 1,533 in 2,857 before
(turbo off, same machine); a 54 h boot with zero bad cycles under the Prime95 soak; zero Windows application crashes against
3-42 a day before [measured: `digest\watch_per_boot.tsv`, `digest\winevents_digest.md`]. **But the game workload stopped at the
same time**, so the voltage cannot take the credit yet. Pre-raise idle boots also ran clean for long spells: one boot with no
jobs ran 29.1 h before its first fault [measured].

**What to do (recommended order, total cost $0 until step 3):**

1. **Let the soak finish (Fri 11-20 5:29 PM PST), then run the normal game lane for 48-72 h at the current settings** and count
   fault windows (`python3 src/RimMandrake/Utils/testq/fault_monitor.py report`). This decides whether the fault still exists at
   +0.100 V under the workload that used to trigger it. Cost $0, no visit. If it stays at zero, stop here and keep watching.
2. **If it returns: test the software explanation before buying.** Use the corrected register probe (built 2026-11-20; it must catch a deliberate
   `VZEROUPPER`, compare against fixed known answers, and check the scalar path too; the old `hold` test cannot see this fault,
   section 4) and run one boot with the hypervisor off (`bcdedit /set hypervisorlaunchtype off`), then back on. GPT call 1 names
   the hypervisor-off crossover as the single cheapest high-information test; GPT call 2 names the corrected probe first. Cost
   $0 and remote, **but** the lane's runner lives in WSL2, so a hypervisor-off arm needs a Windows-native workload (section 7).
   If the fault disappears with the hypervisor off and returns with it on, do not buy a CPU.
3. **If the fault persists with the hypervisor off: swap the CPU with a returnable part**, then put the old CPU back if
   practical. Best buys from GPT's linked, dated (2026-11-20) listings: used i7-10700K **$169.99** shipped (eBay, 30-day returns),
   used i9-10900K **$279.99** shipped (eBay, 30-day returns), open-box i9-10850K **$239.98** shipped (eBay, 30-day returns,
   1-year Allstate) [GPT, linked; not re-checked by us]. One person's visit to fit it. A 10-core part keeps the electrical load
   comparable, which makes the swap a better test (GPT call 3).
4. **Only if a new CPU in this board still fails:** replace the board too. Cheapest routes that keep the 128 GB of DDR4: Ryzen 7
   5700X + MSI B550M GAMING PLUS WIFI6E + cooler **$328.98**; i7-12700K + MSI PRO B760M-P DDR4 + cooler **$485.43**; add
   **$199.99** if a new Windows licence is needed [GPT, linked, 2026-11-20; not re-checked by us].

**Buy nothing yet.** Any purchase is the owner's act; this report only recommends.

---

## 2. The machine

[measured unless tagged; sources `gpt\call1_facts_neutral.md`, `digest\uefi_cpu_settings_20261120.txt`,
`findings\vcore_visit\BEFORE_STATE.md`]

- Intel Core i9-10900K (Comet Lake, CPUID A0655), microcode 0x100. Windows shows 9 cores / 18 threads because `bcdedit numproc 18`
  has been set since 2026-10-26 (it drops logical CPUs 18-19, one physical core); the core is not disabled in the BIOS
  ("Active Processor Cores = All").
- ASUS ROG STRIX Z490-G GAMING (WI-FI), BIOS 3401. ASUS lists 3401 as released 2026-08-19 (Intel IPU 2026.1 microcode, ME
  14.1.79.2540) [GPT call 3, linked]; Windows reports a BIOS date of 2026-05-26 (build date and release date can differ).
- 4 x 32 GB G.Skill F4-2666C18-32GTZN at 2666 MT/s 1.2 V. RTX 2080 Ti. Windows 10 Pro 19045. Hyper-V on (WSL2 Ubuntu guest hosts
  the remote seats and the test runner). Kingston NV3 1 TB system disk since 2026-11-02 (the Samsung 970 with bad blocks is out).
- BIOS settings read from NVRAM 2026-11-20: CPU Core/Cache Voltage = Offset Mode, sign +, offset field raw value 20 (+0.100 V
  if the unit is ASUS's 0.005 V step [guess ~80%]); MultiCore Enhancement "Disabled - Enforce All limits"; Ai Overclock Tuner
  Auto; LLC Auto; SVID Auto; Turbo enabled in firmware. Windows caps the CPU at ~3.6 GHz (PROCTHROTTLEMAX 99) since 2026-11-07.
  On BIOS 0607 (read 2026-10-31) Ai Overclock Tuner was "Manual" and MCE "Auto" [measured: `findings\steve_diag\PROGRESS_bios.md`].
- PSU model, VRM temperature, ambient: UNMEASURED.

## 3. Fault history (Pacific time)

| when (PST/PDT) | what | source |
|---|---|---|
| Mon 10-26 1:20 PM PDT | Logical CPU 18 hashes one buffer to 60 different sha256 digests of 60; AVX2-heavy hashes vary, md5 and scalar sha256 stable. `numproc 18` set. | `findings\item_STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH.txt` |
| 10-27 onward | Windows Application crashes in unrelated programs (dotnet, python, Defender, RimWorld), mostly 0xc0000005 | `digest\winevents_digest.md` |
| Sat 10-31 ~10 AM PDT | Logical CPU 2 fails Prime95 (rounding 0.5) and stevecheck after 5 days up; clean after reboot. RAM walks 85 GB and 108 GB, 0 bad; Windows Memory Diagnostic basic pass clean. | `raw\steve_logs\chk.log`, `sweep.log`, `s2..s4*.log` |
| ~10-31 / 11-01 | BIOS 0607 -> 3401 (microcode 0xC8 -> 0x100). Samsung NVMe bad blocks; cloned to Kingston, Samsung removed Sun 11-01 8 PM PST. | `findings\item_STEVE_POST_DIAGNOSE_FIVE_MINUTE_BOOT.txt` |
| Sat 10-31 7:28 PM PDT | 5-minute per-CPU watch starts | `raw\steve_logs\watch.log` |
| Tue 11-03 7:40 PM PST | Vendor-software A/B (AI Suite, iCUE, Aura callers stopped): three fault windows with them off. Falsified. | `findings\steve_fault_diagnosis.md` |
| Thu 11-05 6:55 PM PST | Case side removed. Onsets then fell to 0.21-0.30 h on five boots. | `findings\item_STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO.txt` |
| Fri 11-06 6:20 PM PST | Windows Memory Diagnostic standard, all memory: no errors | same |
| Sat 11-07 7:18 AM PST | Unexpected shutdown (Kernel-Power 41) | `digest\winevents_digest.md` |
| Sat 11-07 8:00 AM PST | Turbo off (PROCTHROTTLEMAX 99). Faults continue at ~1.03 V. | `digest\watch_per_boot.tsv` |
| Thu 11-12 7:46 AM PST | Owner: stop quarantining, reboot every 12 h, run anyway | item history above |
| Sun 11-15 12:58 AM PST boot | Lane idle from 6 AM; first fault at 29.1 h (Mon 11-16 6:05 AM) with no job running | `raw\fault_monitor_report.txt` |
| Tue 11-17 7:28 AM PST | Owner sets +0.100 V core offset in BIOS | `findings\vcore_visit\BIOS_VISIT_STEPS.md` |
| Tue 11-17 11:40 and 11:45 AM | 2 bad cycles (CPU 8, CPU 7) 4.13 h into the post-raise boot, during a game job's load phase; same register-loss shape | `digest\watch_bad_rows.log`, `raw\steve_logs\watch-chk.log` |
| Tue 11-17 5:29 PM PST | 72 h Prime95 soak starts; ends Fri 11-20 5:29 PM | `raw\steve_soak\soak.log` |
| Thu 11-19 11:53 PM PST | Soak at pass 210, 3,978 steps, 0 Prime95 errors, 0 WHEA, 3 "Prime95 died early"; watch clean for 54.2 h | `raw\soak_read_output.txt` |

Per-era totals [measured, `digest\watch_era_sensors.txt`]: turbo on 426 bad of 1,292 cycles; turbo off before the raise 1,533 of
2,857; after the raise 2 of 770. Test jobs: INVALID 199 of 513 jobs that overlapped a fault window vs 76 of 815 outside
(`digest\testq_outcome_vs_window.txt`).

## 4. The instruments, and whether each was proven able to see

| instrument | what it sees | proven able to see? | known blind spots (who found them) |
|---|---|---|---|
| 5-minute watch (`watch2.ps1` + `stevecheck core`, `findings\steve_diag\Program.cs`) | wrong results from AVX2 integer, FMA/AVX double and .NET SHA-256 work, 4 s per logical CPU every 300 s | **Yes**: a CONTROL at each start (injected fault exits 1, clean run 0), passed on all 43 boots where it ran; the 6 boots of 2026-11-01 to 11-03 ran an older watch with no CONTROL [measured: `digest\watch_per_boot.tsv`] | References are computed on the suspect machine (a wrong reference was seen); no scalar control; samples 1.3% of each CPU's time; fixed CPU order (even sibling always first); a non-zero exit from a crash counts as "bad" too; CONTROL failure would not stop it (GPT 1). Zero-round runs pass silently, but only 2 of 88,978 runs had under 8 rounds [measured]. |
| "Fault window" (`fault_monitor.py`) | first bad cycle of a boot to that boot's end | — | **By definition lasts to reboot, so it cannot show "held until reboot"**: one window had 1 bad and 42 clean cycles, and one boot had 10 clean hours inside its window (GPT 1, GPT 2). |
| `stevecheck hold` (2026-10-31 register-hold test) | was read as "a YMM register held in a spin stayed intact" | **No** | It compares two registers loaded with the same value; zeroing both upper halves leaves them equal, so it **cannot see this fault** (GPT 2, confirmed by reading `Program.cs` `HoldLoop`/`Hold`). The 10-31 reading is void. |
| Prime95 soak (`steve_cpu_soak.ps1`) | Prime95 error lines, WHEA, Prime95 alive at step end, one load sample | **Yes**: CONTROL at each start (injected error and injected kill both seen) [measured] | 90% of a pass is single-CPU work; PASS does not prove work completed; the 3 "died early" are unexplained exits, not arithmetic errors; the heat control's prefix test (`-like 'UNMEASURED*'` against `heat=UNMEASURED(...)`) can never fail; it kills the watch's temperature sampler, which is why 633 of 651 soak-boot watch cycles carry no heat (GPT 1; counts [measured]). |
| vcore reading (`stevetemp`, LibreHardwareMonitor CPU sensor) | "CPU Core" voltage, max per cycle | **No** | Comes from the CPU's own `IA32_PERF_STATUS` VID request, not the VRM output (GPT 1 and 2, citing LHM source). It does not show the +0.100 V offset. Max only; 500 ms samples cannot see droop. |
| temperature (same sampler) | package and per-core temps | partly (readings change with load) | Gaps: no VRM temperature; under the soak the watch's readings are mostly missing. |
| RAM tests (Windows Memory Diagnostic x2, in-OS walks 85/108 GB) | memory errors | Windows tool: not proven on this machine; in-OS walk: its own inject mode exists | Walks cover pageable virtual memory, not every physical page; none ran while the fault was active (GPT 1; 2026-11-17 review). |
| WHEA / event logs | machine-check events, crashes | — | System log only reaches back to 2026-10-31; silent wrong results raise no WHEA (GPT 1). |

## 5. What we concluded and what GPT concluded

| question | ours (before this run) | GPT | settled? |
|---|---|---|---|
| Is the fault real? | yes | yes (both calls) | **agreed** |
| What is it? | "wrong SIMD results on a logical CPU" | loss of upper-half AVX state (both calls, after this run's item 5) | **agreed** now; this run found it |
| Which part? | the CPU | software below the app most likely (53%); CPU 30% (call 1); CPU "not established" (call 2) | **disagree** |
| Next step | replace the CPU | test the software explanation first (hypervisor-off crossover, corrected probe) | **disagree** |
| Did the +0.100 V raise take effect? | yes, "visible in temperature and vcore spread" (`findings\steve_fault_diagnosis.md` as sent) | stored in NVRAM, not shown to be delivered; the sensor reads a VID request | **ours was wrong**; corrected in the repo's facts file this run |
| Did the raise help? | "did not cure it" | large improvement under combined new conditions; voltage and workload changes are confounded | agreed it did not cure; GPT weighs the improvement more |
| "Held until reboot" | yes | not established; windows are defined to last to reboot | **ours overstated** |
| "CPU 2 alone failed" on 10-31 | yes; rows on CPUs 6-9, 11 were the driver's unpinned first 200 ms | sweep.log shows small-FFT failures on CPUs 6, 7, 8, 9, 11 too; check before discounting | **open**: our artifact reading stands unless re-tested |
| RAM | "not the fault's cause" | lower priority, not excluded | ours too categorical |
| Soak's 3 faults | counted as faults | unexplained Prime95 exits, not arithmetic failures | agreed after review |
| 11th-gen CPU on this board | not supported (unverified) | not supported: no 11th gen on ASUS's exact-board list, 3401 notes add none | **agreed**, now verified with links |

Named disagreements, not smoothed over:
1. **The cause.** We said CPU. GPT blind gives software below the application 53% and the CPU 30%. I side with GPT on order
   after the register finding, but the voltage improvement and the CPU-pinned failures keep the CPU close behind [guess].
2. **The next step.** We said replace. Both GPT calls say test first, because a swap that "fixes" it also reseats the socket and
   changes the load, and a swap that does not fix it costs a part and a visit for little information.
3. **The evidence that the raise took effect.** Our facts file compared post-raise readings with a set that included turbo-on
   boots; the drop it showed was the turbo change. This run fixed the file (`infrastructure/state/facts/steve_fault_diagnosis.md`)
   and the Conductor handoff `CONDUCTOR_HANDOFF_202611180140.md` that repeated it (culled 2026-11-25; read it with `git show eeb532cee4:infrastructure/state/handoffs/CONDUCTOR_HANDOFF_202611180140.md`).
4. **The 10-31 "register held intact" result** was void (blind test). It was the only test that had looked for exactly this fault.

## 6. Buying options

### Ours (Sonnet web research 2026-11-19, unverified, `research\web_research_sonnet_20261119.md`)
Drop-in i9-10900K used ~$261 (aggregator estimate), new $399-$529 (undated); i7-10700K used ~$179-185; 11th gen treated as
unsupported; warranty for a 2020 chip almost surely expired; no forum evidence found.

### GPT's corrections and expansion (call 3, 2026-11-20, every price linked in `gpt\call3_answer.md`; not re-checked by us)

| option | total (USD, 2026-11-20, before tax) | what it proves |
|---|---|---|
| Tests in section 1 steps 1-2 | $0 | separates software from hardware |
| Borrowed LGA1200 CPU, ideally a cross-test of the old CPU | $0 if available | strongest cheap isolation |
| Used i7-10700 / i7-10700K, eBay, 30-day returns | $135.99 / $169.99 shipped | a pass favours the old CPU (or its contact/load); a fail leaves board, RAM, PSU, software |
| Open-box i9-10850K (Dell pull, 1-year Allstate) / used i9-10900K | $239.98 / $279.99 shipped | better like-for-like CPU test (same 10-core load) |
| New i9-10900K | ~$400.59 (eBay "new", stock unverified) | — (poor value) |
| Ryzen 7 5700X + MSI B550M GAMING PLUS WIFI6E + cooler | $328.98 (+$199.99 if a Windows licence is needed) | replaces CPU and board; cannot say which failed |
| i7-12700K + MSI PRO B760M-P DDR4 + cooler | $485.43 (+$199.99) | same; 12th gen is outside Intel's 13th/14th-gen Vmin issue |
| Ryzen 7 5800X3D + B550M + cooler | $509.93 (+$199.99) | same; RimWorld gain not measured |

Corrections GPT made to our research: BIOS 3401 is real (2026-08-19); 11th gen is not on the exact board's list; 10850K and
10900/F/KF are findable; the 10700K is a 125 W part like the 10900K (only the 10700 non-K is 65 W); B560/Z590 cannot take 12th-14th
gen; our $1,700/$800 extrapolations and the "$381 Micro Center bundle" were unsupported. All four platform boards named have
maker-stated 4-slot 128 GB support; the exact G.Skill kit is on none of their QVLs as checked (UNMEASURED). Intel warranty: 3
years for a boxed 10900K, none for used chips; check this unit's FPO/ATPO at Intel's warranty checker (GPT call 3, links).

## 7. Still unmeasured, and the command that would measure it

| unknown | how to measure it |
|---|---|
| Does the fault return at +0.100 V under the game workload? | After the soak ends: `python3 src/RimMandrake/Utils/testq/testq.py resume --reason "post-soak baseline at +0.100 V"`, then after 48-72 h `python3 src/RimMandrake/Utils/testq/fault_monitor.py report` |
| Hypervisor on vs off | `ssh stevedesktop "bcdedit /set hypervisorlaunchtype off"` + reboot, verify with `systeminfo`, run 48-72 h, then `bcdedit /set hypervisorlaunchtype auto`. Blocker: the test runner and remote seats live in WSL2, so this arm needs a Windows-native workload (Prime95 + the watch + a RimWorld run started from Windows). Not built. |
| A probe that can see upper-half loss | Built and running since 2026-11-20 20:08Z (task `SteveDiag Register Probe`, `src/RimMandrake/Utils/steve_cpu_retest/regprobe.c`): it caught an injected `VZEROUPPER` on 18 of 18 logical CPUs and read clean on a normal run (`regprobe_red_green/README.md`). Read it: `python3 src/RimMandrake/Utils/testq/fault_monitor.py regprobe`. |
| The WSL2-guest canary (same check inside Linux on the same CPU) | UNRUN since `RIMMANDRAKE_DIAGNOSE_STEVE_WORLD_START_SIX_MODS_ONE_FAILURE`; no command written |
| Bare-metal Linux | Live USB + `mprime` + a native AVX/scalar checker; needs a person at the machine |
| Why Prime95 "died early" 3 times | the soak does not keep the PID or exit code; UNMEASURED |
| Delivered Vcore and VRM temperature | a board (SuperIO) sensor read; `stevetemp` opens CPU sensors only; UNMEASURED |
| Unit of the BIOS offset field (raw 20) | look at the BIOS screen, or decode the IFR numeric step; UNMEASURED |
| RAM while the fault is active | MemTest86 4 passes per DIMM set; needs a person |
| Is the even/odd imbalance real or the fixed test order? | watch2.ps1 now checks the CPUs in a random order each cycle and logs it as `order=[...]` (on Steve's disk 2026-11-20; it takes effect at the first boot after 20:05Z); compare the per-CPU counts after that |
| PSU model | a look at the label |
| This CPU's warranty | FPO/ATPO from the box or IHS into Intel's checker |

## Appendices

### A. The evidence package
`D:\ClaudeWork\rimmandrake\steve_cpu_report_20261119\package\MANIFEST.md` lists every file with source, time range, row count,
sha256, and whether GPT saw it whole, as a digest, or not at all. A copy of every file under 5 MB is beside this report in
`package\` (same layout; the instrument source files under `raw\tools_steve_cpu_retest\` are left out of the repo copy because
they are already in the repo at `src/RimMandrake/Utils/steve_cpu_retest/`). Two repo copies carry one added HISTORY head line that the repo's retired-era check requires, so their sha256 differs from the
manifest: `package/findings/ledger_steve_fault_events.md` and `package/findings/steve_diag/driver_ab/PROGRESS.md`.

Files kept outside the repo (over 5 MB):
- `D:\ClaudeWork\rimmandrake\steve_cpu_report_20261119\package\raw\steve_logs\watch-chk.log` (7,603,469 bytes, 101,528 lines,
  sha256 `5804000937fb742d22595243e7ab937fbf09f6f3d04536ef1e2856de1b0c6800`): every checker run and its first five mismatches.
- `D:\ClaudeWork\rimmandrake\steve_cpu_report_20261119\package\gpt\call3_events.jsonl` (7,405,135 bytes, sha256
  `199c61e390550aa152745c5a117c6d7f42da3ecbc9bfb77f3d87924e1c3cdc11`): the buying-research call's full event stream.
- Not copied into the package at all: the BIOS images and decode tools `D:\ClaudeWork\rimmandrake\steve_diag\bios\` (75 MB) and
  the sampler software `D:\ClaudeWork\rimmandrake\steve_diag\heat\` (22 MB).

### B. The three GPT calls
Model gpt-6.1-sol via `src/RimMandrake/Utils/gpt_consult.py`, high effort, web search on, three separate sessions run in
parallel (so call 1 never saw our verdict). Prompts and answers whole in `package\gpt\`:
- call 1, blind assessment: `call1_prompt.md` + 23 files (481 KB), answer `call1_answer.md`, events `call1_events.jsonl`.
- call 2, strongest case against our verdict: `call2_prompt.md` + 19 files (146 KB), answer `call2_answer.md`.
- call 3, buying research: `call3_prompt.md` + the Sonnet research file, answer `call3_answer.md`.
Call 2 saw the facts file before this run corrected it; it flagged the same error independently.

### C. How the register finding was made
`digest\chk_mismatch_analysis.md`: the 12,550 MISMATCH lines were split into their three parts; the correct reference values were
identified (their hash reproduces the checker's clean `ref=E99EB79839CA4010`); the floating-point part, when wrong, took exactly one
alternative value per seed on every CPU and every day; a Python re-implementation (`scripts\fp.py`, `fp5.py`) reproduces the
correct value bit for bit, and setting the two upper lanes of the final accumulator to the x86 default NaN reproduces the
alternative for seeds 0, 3 and 7. Five other seeds were not run (about 1 minute each).

### D. Corrections made in other files this run
- `infrastructure/state/facts/steve_fault_diagnosis.md`: the "+0.100 V raise IS visible" bullet was false (it compared with
  turbo-on readings); replaced with the NVRAM reading and the turbo-off comparison.
- `infrastructure/state/handoffs/CONDUCTOR_HANDOFF_202611180140.md` (culled 2026-11-25; in git at `eeb532cee4`): the same false sentence, replaced.
