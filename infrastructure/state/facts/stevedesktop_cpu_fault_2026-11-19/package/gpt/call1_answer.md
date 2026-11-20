**1. What is failing?**

The machine has demonstrated a real computation-integrity failure. My leading explanation is **intermittent loss or incorrect restoration of live AVX register state**, with privileged software somewhat more likely than defective CPU silicon. The evidence does **not** yet identify a component to replace confidently.

These are subjective diagnostic probabilities, conditional on the supplied evidence—not statistically estimated failure rates. References below use the supplied filenames, numbered items, timestamped log rows, and source-code expressions.

| Candidate | Probability | Evidence for | Evidence against / limitations |
|---|---:|---|---|
| **(a) CPU silicon itself** | **30%** | Strong logical-CPU localization across independent programs: CPU 2 produced 669 bad rounds out of 849 while CPU 3 produced 0/858 (`raw/steve_logs/chk.log`, 17:21:00 and 17:22:39). Earlier CPU 18 failed several vector-heavy hashes while scalar SHA-256 remained stable (`call1_facts_neutral.md`, timeline 2026-10-26). Defective vector-state tracking could produce structured zeroing rather than random arithmetic errors. | Exact upper-half loss is also a direct consequence of software state-preservation mistakes. Broad even/odd asymmetry and changing affected CPUs are less persuasive for a single defective arithmetic unit. Reboots repeatedly restore observed correctness, and there is no independent operating-system test. |
| **(b) Board / VRM / socket / power delivery** | **10%** | An electrical margin problem can affect CPU correctness; the apparent improvement follows a voltage-setting change (`watch_per_boot.tsv`, three post-raise rows). Delivered voltage, VRM temperature and transients are unmeasured (`call1_facts_neutral.md`, machine and instruments). | No direct electrical evidence. Coherent loss of precisely one architectural state component is less natural than general instability. Failures occur at low measured temperatures; a long CPU soak subsequently produces no recorded arithmetic errors. Neither observation excludes transition-related power faults. |
| **(c) Memory** | **3%** | Non-ECC memory can corrupt data, instructions or an XSAVE image. In particular, corruption of an XSAVE header could cause vector-state initialization. Four DIMMs remain an unisolated configuration. | Large memory walks and Windows Memory Diagnostic found no errors (`call1_facts_neutral.md`, 2026-10-31 and 2026-11-07 entries). CPU-specific behavior and the repeatable floating-point alternative are poor matches for ordinary random DRAM errors (`chk_mismatch_analysis.md`, items 2–5). Those memory tests have coverage limitations discussed below. |
| **(d) PSU** | **2%** | Unknown PSU; one Kernel-Power 41 event and two unexpected-shutdown records (`winevents_digest.md`, “Unclean shutdowns”). Stopping games also changes GPU and combined-system power demand. | Those events do not diagnose a PSU. There is no rail measurement, substitution test or demonstrated relationship to GPU load. Precise YMM-state loss and selective logical-CPU failures fit it poorly. |
| **(e) Software below the application: kernel, Hyper-V/VBS, driver, firmware/SMM/microcode state** | **53%** | Exact upper-half loss has straightforward software mechanisms. Hyper-V/VBS and several privileged vendor drivers are present (`call1_facts_neutral.md`, machine). Logical-CPU asymmetry, reboot sensitivity and workload sensitivity fit interrupt/DPC affinity, per-CPU state, or faulty context preservation. The vendor A/B left several drivers loaded and did not test Hyper-V off. | No offending instruction, driver or context transition has been captured. The partial vendor A/B did not eliminate failures, and BIOS/microcode replacement did not eliminate them (`call1_facts_neutral.md`, 2026-11-04 and BIOS-change entries). Apparent voltage responsiveness remains evidence for hardware margin, although heavily confounded. |
| **(f) Something else: application/runtime/compiler/checker defect; storage or device-DMA corruption** | **2%** | The checker relies on JIT-generated code and self-generated references. The removed SSD had substantial errors (`call1_facts_neutral.md`, BIOS/SSD entry). Device DMA could corrupt memory. | Prime95 and multiple hash implementations provide independent corroboration; many unrelated processes crashed. Errors continued after SSD removal. A checker-only defect cannot readily explain that collection of observations. |

**Total: 100%.** Within category (e), the evidence does not support defensible separate percentages for Hyper-V, a driver, the Windows kernel and SMM.

Two qualifications materially affect these odds:

- **“CPU 2 alone failed” overstates the supplied Prime95 sweep.** `sweep.log` also records small-FFT failures on CPUs 6, 7, 8, 9 and 11. CPU 2 is nevertheless exceptional: it fails both FFT ranges and the checker. The other Prime95 rows need their launch/log handling checked before deciding whether they are genuine additional failures.
- **“Held until reboot” is not established literally.** The monitor defines a window to last until reboot. `watch_per_hour.tsv` shows ten consecutive clean hours on November 9, 13:00–22:59, after that boot had already failed. The November 15 05:11 boot has one bad cycle followed by 42 clean cycles (`fault_monitor_report.txt`, corresponding window). What is established is recurrent failure within boots and repeated observed improvement following reboot.

**2. What can produce exactly the upper-half signature?**

Item 5 is highly informative, but its strongest justified conclusion is:

> The observed floating-point alternatives are consistent with upper-lane NaN poisoning caused by loss of upper-half vector state.

It is **not yet a direct observation that every YMM register was zeroed**. The evidence is a 64-bit reduction of four final accumulator lanes; the simulation matched three of eight seeds, and the simulation source is not supplied here. Different corruptions can converge to the same absorbing NaN state. Moreover, the 12,550 lines are the first five mismatches per failing invocation, not every incorrect computation. (`chk_mismatch_analysis.md`, introduction and items 4–5.)

The distinction matters: **the final upper lanes are NaNs, not zeros**. Zeroing live constants is a proposed cause of those NaNs.

| Mechanism | How it produces this signature | Fit to this machine |
|---|---|---|
| **Unpreserved `VZEROUPPER`** | Clears the upper halves of YMM0–YMM15 while retaining their low halves. Interrupted code subsequently encounters zeroed constants and can generate the observed NaNs. | Excellent signature match. A driver, hypervisor or firmware path executing it without preserving interrupted state could affect unrelated applications. |
| **128-bit VEX instructions plus incomplete preservation** | A VEX-encoded 128-bit instruction clears the upper half of its destination. Saving/restoring only XMM state cannot repair that loss. | Fits selected-register loss. Losing the relevant constants is sufficient; all YMM registers need not be affected. |
| **Incorrect XRSTOR/XRSTORS state initialization** | AVX upper halves are state component 2. Restoring that component with its `XSTATE_BV` bit clear initializes it to zero while SSE state can be restored normally. | Particularly good match to preservation of lower halves and loss of upper halves. Could originate in software, corrupted save-image metadata, or defective hardware tracking. |
| **Defective CPU state tracking, restore logic or power-state retention** | Incorrect “initial/zero” metadata or restoration can make a whole register region read as zero without 128 independent bit failures. | Plausible hardware explanation. It is more specific than “bad FMA arithmetic,” but is not demonstrated. |
| **JIT/compiler/register-allocation error** | A misplaced `VZEROUPPER`, incorrect-width reload or bad spill restoration could destroy live upper halves. | Plausible for this checker alone; much weaker as a common explanation for Prime95, OpenSSL and unrelated applications. |
| **Ordinary DRAM or execution-data bit errors** | Can indirectly create NaNs or corrupt saved state. | Generic random corruption poorly explains the repeated lane boundary; save-header corruption is the more credible memory variant. |

Intel documents the `VZEROUPPER` and VEX.128 behavior in its [optimization manual](https://www.intel.com/content/dam/doc/manual/64-ia-32-architectures-optimization-manual.pdf), and the component initialization rules in [SDM Volume 1, §§13.5–13.8](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf).

There is a **documented driver programming failure mode matching the mechanism**: Microsoft requires kernel AVX users to explicitly save and restore AVX state. Saving only legacy floating-point/SSE state is insufficient. Its documentation specifically discusses preserving the interrupted program’s state in DPCs. That establishes plausibility, not culpability of any installed driver. [Microsoft driver guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/floating-point-support-for-64-bit-drivers), [KeSaveExtendedProcessorState](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kesaveextendedprocessorstate).

A separate user process legitimately executing `VZEROUPPER` should **not** corrupt another process. A preservation failure or hardware defect is needed to cross that boundary.

The timing and topology evidence fit as follows:

- **Acquisition during uptime and reboot recovery:** a driver entering a new operating mode, damaged per-CPU bookkeeping, recurring firmware activity, or a CPU state-tracking fault could fit. A static broken arithmetic circuit fits less naturally. Because persistent failure is not proven, the data do not require a permanently latched state.
- **Even/odd imbalance:** before the raise with turbo off, even CPUs account for **1,594** failing CPU-invocations versus **305** on odd CPUs: **5.23:1**, or **83.9% even**. CPU 2 versus 3 is **591:34 = 17.4:1** (`watch_per_cpu_by_era.tsv`, era 2). Interrupt affinity and per-logical-CPU software state are credible explanations. Hardware remains possible because architectural state is separate between siblings despite shared execution resources.
- **Testing-order confound:** every sweep tests the even sibling first, then the odd sibling. Cold-to-active transitions, warming, or periodic activity synchronized to the fixed order could generate an apparent topology effect. Reverse/randomized order is needed.
- **After November 17:** increased voltage could improve hardware margin. Removing games and introducing the soak could change driver activity, interrupts, scheduling and power-state transitions. Both classes fit; the intervention does not distinguish them.

**Published matches:** I did not find a verified public Windows 10 19045/Hyper-V bug or a named ASUS/Corsair/NVIDIA driver defect matching this complete signature and timeline.

Intel’s public [Comet Lake specification update, revision 013](https://cdrdv2-public.intel.com/615213/615213_013.pdf) provides no exact documented match. Its broadly worded CML119 involves AVX/divide-related unpredictable behavior, but the summary marks it **N/A for this Q0 stepping**. CML122 concerns guest page faults and is likewise N/A for Q0. Neither supports identifying this failure as that erratum. Older-family “ZMM/YMM incorrect values” errata cannot be transferred to a 10900K merely by architectural resemblance.

Windows tooling has had register-corruption bugs—for example, Microsoft fixed AVX register corruption during debugging in [Visual Studio 2017 15.9.7](https://learn.microsoft.com/en-us/visualstudio/releases/2017/vs2017-relnotes). No supplied evidence places these failures under that debugger, so it is not a case match. The 10900K/Z490 reports I found did not provide a sufficiently controlled matching diagnosis to change the odds.

**3. The cheapest high-information test, then the next two**

**First: a remotely administered Hyper-V/VBS-off crossover under the original game workload, keeping the current voltage setting fixed.**

Use an on/off/on comparison, verify that the hypervisor actually stopped, and run the Windows checker independently of WSL. Stop the soak during each comparable game-workload arm. Count completed rounds and compare against fixed canonical references.

The crucial prerequisite is **reproducing failures in the current Hyper-V-on configuration**. If it remains clean at the raised voltage, a clean Hyper-V-off arm says little. Because a pre-raise onset took 29.12 hours, I would budget **48–72 hours per arm**, ending an arm early if reproducible corruption appears. That duration is a proposed test budget, not a calculated guarantee.

Cost: **no component purchase or planned travel**, remote administration and reboots, plus the stated machine exposure. Actual operator time is unknown. An independent Windows access path is necessary because disabling Hyper-V removes the WSL2 agent path.

| Leading hypothesis | Expected result |
|---|---|
| Hyper-V/VBS preservation defect | Failures reproduce with it on, disappear off, return on. That would move substantial probability into (e). |
| Windows driver defect independent of Hyper-V | Failures continue off, although their rate or CPU distribution may change. |
| SMM/firmware defect | Usually persists; a dependence on virtualization configuration remains possible. |
| CPU silicon defect | Usually persists under sufficiently comparable conditions. A clean off arm alone is not decisive because scheduling and power behavior change. |
| Board/PSU electrical fault | Usually persists with comparable workload, but altered transitions can change its incidence. |
| Memory fault | Usually persists if the relevant memory conditions recur. |

**Second: an independent native checker under bare-metal Linux**, with fixed expected outputs, scalar/SSE/AVX2 variants, and a corrected register sentinel. Include deliberate context switching and alternating load/idle periods. WSL2 is not an independent operating-system control. Reproduction there would sharply reduce the Windows-driver/kernel/Hyper-V hypotheses; SMM and hardware remain. A clean result is weaker if the triggering workload cannot be reproduced. Whether remote booting is available—and therefore whether travel is required—is unknown.

**Third: a controlled CPU cross-swap with a known-good compatible system.** Ideally test the suspect CPU in the good board and the good CPU in the suspect board. A fault following the CPU strongly favors (a); remaining with the original platform favors board, PSU, memory or software. A one-direction replacement alone is less conclusive because reseating also changes socket contact and cooling pressure. Prices, spare availability and travel cost are unknown.

**4. Could the instruments be fooling us?**

Yes—especially about negative results, persistence and sensor interpretation. They do not plausibly explain away all the independent positive evidence.

**Checker (`Program.cs`)**

- **References can be wrong.** `refd[i]=Round(...)` learns truth on the suspect machine. Stable corruption shared by reference and later rounds passes. Item 1 already shows corrupted references. Compare every result and reference with an independently established canonical value.
- **A successful invocation can perform no comparisons.** `Stopwatch.StartNew()` precedes eight reference calculations. If those consume the four-second budget, the loop executes zero times and returns 0. Contention during the soak increases this concern. The watch does not enforce minimum `rounds`.
- **There is no matched scalar control.** Thus the watch demonstrates corruption in a vector-heavy program, not exclusive failure of AVX arithmetic.
- **“sha-only” does not localize the hash implementation.** `Buffer.BlockCopy` can corrupt the copied buffer; the integer result is only an XOR reduction; the Windows SHA implementation is not identified here. A correct integer reduction does not prove every buffer byte correct.
- **Affinity is incompletely verified.** The return from `SetThreadAffinityMask` is ignored; `moved` samples only after a round, and migration does not itself make the invocation fail. The logged `moved=0` rows are useful but not a continuous residency trace.
- **The `hold` test has a decisive blind spot.** `HoldLoop` compares two registers loaded with identical values. Common upper-half zeroing leaves them equal. Its comparison is also loop invariant in normal program semantics, so generated assembly must be inspected for hoisting. The clean HOLD rows in `s4.log` therefore do not exclude common register-state loss.
- **The source comment mentioning `exec` describes no implemented command.** `Main` dispatches only `hold`, `core`, or `mem`.
- **JIT output and deployed binary identity are missing.** Source alone does not establish register allocation, instruction widths, spills, tiering, or which binary version produced each historical log.

**Watch (`watch2.ps1`)**

- **Nonzero exit is broader than arithmetic mismatch.** It counts crashes, runtime startup failures and other failures as “bad CPU.” The exit codes preserve some distinction; aggregate bad-cycle totals do not.
- **Controls are logged, not enforced.** A failed CONTROL does not stop or invalidate subsequent cycles. The injected error flips a scalar result bit after computation; it does not validate every vector mechanism.
- **Sampling is sparse.** Each logical CPU receives nominally four seconds every 300 seconds—**1.33% of wall time**, with some budget consumed by references. A clean cycle is a sampled negative.
- **Fixed order confounds CPU identity with time and transitions.** Randomize order and measure completed work.
- **It has no checker timeout or atomic singleton lock.** A hung child can stop coverage; simultaneous watcher starts can race. Startup failure can also leave ambiguous `$LASTEXITCODE` handling without explicit process/result validation.
- **Cycle timestamps describe completion of sequential testing.** They are not exact fault-onset times, and cycle-wide heat cannot identify temperature at the particular failed instruction.

**Soak (`steve_cpu_soak.ps1`)**

- **PASS does not prove a worker computed correctly for the full step.** It checks that some `prime95` process exists at the end and that no matching error line was read. It does not retain the launched PID, exit code, per-step CPU time or completed-test count. A stopped worker can leave the process alive.
- **The three “died early” events are unresolved failures.** They could be genuine process deaths, failed launches or external termination. Absence of Event 1000 does not settle this. Their low midpoint load supports lack of sustained computation (`soak_digest.md`, all three FAIL rows).
- **Short restarts limit FFT coverage.** Repeated 45-second processes do not establish that the configured 8–128K range was traversed or that substantial self-checking completed.
- **Most of the soak is single-CPU work.** Nominally, a pass contains 810 seconds of single-CPU steps and 90 seconds all-core: **10% all-core wall time**, before overhead. It is not 54 hours of continuous all-core stress.
- **Load is checked once per step and is not a PASS requirement.** The successful CPU-0 startup control does not validate every later affinity/worker configuration.
- **The heat control has a string-prefix bug.** It rejects `UNMEASURED*`, but the sampler prints `heat=UNMEASURED(...)`. A sampler failure can therefore satisfy `heat_seen=1`. Neither failed controls nor missing heat automatically invalidate a step.
- **The soak can kill the watch’s sampler.** Its `finally` kills every `stevetemp` process started since the step began, including a concurrently launched watch sampler. This plausibly explains substantial `no_output` coverage loss.
- **Some errors become apparent negatives.** File deletion and WHEA-query errors are suppressed; stale result files can create false positives, while failed queries can look like zero events. The logged blind worker probe also cannot establish workload exclusivity.

**Sampler and firmware interpretation**

- **`vcore_v` is not established delivered Vcore.** Upstream LibreHardwareMonitor obtains this “CPU Core” value from `IA32_PERF_STATUS`, scaling its voltage field by 1/8192. The installed library revision and this platform’s reporting semantics still need verification. It is not an independent VRM measurement. [LibreHardwareMonitor source](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/blob/master/LibreHardwareMonitorLib/Hardware/Cpu/IntelCpu.cs).
- **It reports the maximum sampled voltage, not droop.** A 500 ms sampler cannot characterize fast supply transients. The “higher readings have more bad cycles” comparison is observational, workload-confounded, and uses maxima.
- **Temperature coverage is incomplete.** It cannot exclude peaks between samples, activity outside checks, VRM heating, or temperatures on the disabled physical core. Non-null sensor values are not independently checked for freshness.
- **Post-raise sensor statistics are strongly selected.** Only **129/770 = 16.8%** of post-raise watch cycles have readings; only **18/651 = 2.8%** on the long boot. Its watch temperature mean is not a representative continuous record (`watch_era_sensors.txt`; `watch_per_boot.tsv`).
- **The offset is a stored setting, not a measured voltage increase.** NVRAM confirms positive offset mode and raw field 20. Its unit conversion and actual electrical effect remain unverified (`uefi_cpu_settings_20261120.txt`).

**Memory tests and digests**

- **The memory walk is not full physical-memory coverage.** `VirtualAlloc` commits pageable virtual memory; it does not lock or identify every physical page. OS-reserved memory is excluded. The phase-3 “shifted thread pairing” rotates accesses within each chunk; it does not deliberately transfer chunks between pinned CPUs.
- **Fault windows encode persistence by policy.** They establish neither continuous failure nor recovery only at reboot.
- **Some summaries disagree.** The November 12 16:06 boot has 75 cycles/58 bad in `watch_per_boot.tsv`, versus 76 cycles/59 bad in the monitor material. Other rows have similar one-cycle differences. Reconcile snapshots/filtering before precise rate modeling.
- **Mismatch dates reconstructed from time-only logs can drift across missing days or clock changes.** This primarily weakens timing attribution, not the observed result strings.
- **Crash counts are not hardware-failure counts.** Software aborts, fail-fast events and related WER records need classification; provider totals should not be added as independent crashes.
- **Job outcomes establish association.** INVALID is **38.8% inside windows versus 9.3% outside**, a **4.16× risk ratio** (`testq_outcome_vs_window.txt`). Window construction, workload mix and correlated jobs prevent a causal reading.
- **Zero WHEA is a limited negative.** The System log begins October 31, and silent incorrect computation need not generate a machine-check event (`winevents_digest.md`).

**5. What the post-November-17 data support**

They support a **large observed improvement under the combined new conditions**, with continuing uncertainty about why.

| Observation | Supported interpretation | Not established |
|---|---|---|
| 2/770 bad cycles | Observed bad-cycle share fell from **53.66% to 0.260%**, approximately **207-fold**. | A 207-fold causal voltage benefit; cycles are correlated and workloads changed. |
| 651 clean cycles over 54.18 hours | Strong evidence against the earlier frequent-error regime continuing unchanged under this soak. | An error-free CPU or equivalent validation of the original workload. |
| 3,978 soak steps; zero arithmetic-error lines | Useful independent negative evidence for the tested execution pattern. | Full FFT coverage, verified work in every step, or a completely passing soak—the three process disappearances remain unresolved. |
| No application-error events after the raise | The observed crash regime stopped during this interval. | Production stability: the major game workload was subsequently absent. |

For scale, if 651 cycles were independent and equally sensitive, zero failures would give a one-sided 95% upper bound of about **0.46% failures per cycle**. Those assumptions are unsuitable for this boot-dependent process; the calculation is **not** a reliability guarantee.

**What the voltage raise could explain:** improved timing margin in CPU execution, register-state handling or core/cache circuitry. It could also compensate for deficient delivered voltage. Even a demonstrated voltage benefit would not distinguish degraded silicon from power delivery.

**What stopping games could explain:** removal of a graphics/audio/storage-driver trigger, different interrupt/DPC activity, reduced combined GPU/CPU demand, or fewer problematic power and scheduling transitions. The soak itself also changes those conditions.

The supplied history limits both stories:

- The raise **did not eliminate errors immediately**: CPUs 8 and 7 failed at 19:40 and 19:45 while a game job was loading (`watch_bad_rows.log`, November 17 rows).
- Games **were not necessary for every onset**: the November 15 boot first failed at 29.12 hours after an extended lane-idle period (`fault_monitor_report.txt`, `F20261115T085753Z`).
- The digest does not identify the mismatch components in those two post-raise failures, so it does not establish that they had the same floating-point signature.
- Reboot, voltage setting, game cessation and soak exposure changed together closely enough that their separate effects are **unknown**.

I would retain the raised-voltage result as evidence of improvement, but would test the privileged-software explanation before paying for a replacement CPU or a site visit.