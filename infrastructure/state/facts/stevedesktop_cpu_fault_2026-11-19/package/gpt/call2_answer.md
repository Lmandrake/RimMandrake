**The package establishes a real computation fault. It does not establish that the CPU package is failing, or that buying a CPU is the best next experiment.** The strongest competing explanation is loss of AVX register state across a driver, OS, hypervisor, or firmware boundary.

I reviewed the inlined text only. Below, quoted lines are identified by file plus section, timestamp, or table row, since the supplied files have no line numbers.

**1. The verdict turns failed remedies into a component diagnosis.**

The decisive reasoning appears in `findings/vcore_visit/BIOS_VISIT_STEPS.md`, final paragraph:

> “One visit at +0.100 V gives a clean answer: if it does nothing, low voltage is not the cause and we replace the CPU.”

And in `findings/item_RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING.txt`, event **2026-11-17T15:33:56Z**:

> “Any window = voltage did not cure it; no second voltage visit, next route is the replacement CPU.”

“Any genuine recurrence means this intervention did not completely cure it” is valid. Neither “low voltage is excluded” nor “therefore replace the CPU” follows. An offset cannot exclude board delivery problems, transients, another voltage domain, or software corruption. Nor does its failure distinguish CPU from motherboard.

Several facts deserve substantially more weight:

- **The register signature is unusually specific.** `digest/chk_mismatch_analysis.md`, item 2:

  > “The same alternative appears on every logical CPU that faulted … Errors in `fp` are therefore not random bit noise.”

  A common architectural state-loss mechanism explains this more directly than independent marginal arithmetic units across many cores.

- **The vendor A/B left privileged code loaded.** `findings/steve_fault_diagnosis.md`, final section:

  > “Not excluded: the System-start drivers `AsIO2`, `GLCKIO2`, `ene` and `MsIo64` stayed loaded, with no known caller running.”

  That supports a narrower conclusion: the disabled callers and unloaded drivers were unnecessary for recurrence under those conditions. It does not exclude autonomous callbacks in remaining drivers, other drivers, or Hyper-V.

- **The hypervisor remained present.** `findings/vcore_visit/BEFORE_STATE.md`:

  > “Hypervisor PRESENT: WSL2 … VBS status 2 but no security service (HVCI) running.”

  No HVCI service does not mean no hypervisor. There is no supplied comparison against Windows running without it.

- **Windows versus WSL was suggestive and never properly resolved.** `findings/item_STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH.txt`, opening description:

  > “md5 and scalar HACL sha256 are stable; WSL python3 is stable”

  But `gpt/call1_facts_neutral.md`, timeline, qualifies that:

  > “WSL not pinned”

  This is a lead, not an acquittal of hardware: different instruction paths, placement, and exposure could explain it. The later ledger explicitly preserves the guest canary as **UNRUN**.

- **The later improvement is much stronger than the verdict’s wording acknowledges.** `digest/watch_per_boot.tsv`, boot **2026-11-18 01:39:36**, records **651 cycles, zero bad, through 54.18 hours**. `digest/soak_digest.md` records:

  > “Steps in the 72 h run: 3978; FAIL steps: 3”

  Every failure was `prime95_died_early`, with `fatal=0 whea=0`. These are unexplained exits, not three demonstrated arithmetic failures. The clean watch interval and absence of Prime95 error lines are substantial contrary evidence, although changed workload prevents attributing the improvement solely to voltage.

- **“The raise took effect” is overclaimed from the sensors.** `findings/steve_fault_diagnosis.md` says:

  > “The raise IS visible, in temperature, not in the vcore reading.”

  And:

  > “Cooler and electrically calmer under the same workload … the BIOS change took.”

  Cooler operation and reduced variation do not prove increased delivered core voltage. The later package admits the sensor’s interpretation is uncertain. Current LibreHardwareMonitor source derives its “CPU Core” value from `IA32_PERF_STATUS`, using a variable named `vidBits`; it is not a direct motherboard voltage measurement. The installed version still needs matching to its source. [LibreHardwareMonitor implementation](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/blob/master/LibreHardwareMonitorLib/Hardware/Cpu/IntelCpu.cs)

  The owner’s report and decoded NVRAM support that an offset was **configured**. Its electrical effect at the relevant instant remains unmeasured.

- **“Persistent until reboot” partly describes your bookkeeping.** `gpt/call1_facts_neutral.md`, Instruments:

  > “Fault window … from the first bad cycle of a boot to the end of that boot.”

  That definition cannot establish continuous persistence. `raw/fault_monitor_report.txt` includes window `F20261115T051134Z` with **one bad and 42 clean cycles**. Other windows clearly contain recurrent trouble, but “a bad result occurred sometime since boot” and “the machine remains continuously faulty” are different claims.

- **RAM was reasonably downgraded, then rhetorically excluded.** `findings/steve_fault_diagnosis.md`:

  > “RAM is clean within that coverage; it is not the fault's cause on present evidence.”

  The first clause is sound; the second is too categorical. The stronger standard-memory test is documented elsewhere: `item_STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO.txt`, **2026-11-07T13:13:32Z**:

  > “That pass does not clear RAM under load”

  Also, the old assertion in `item_STEVE_HASHER_DIAGNOSE_WRONG_DIGESTS.txt`, **2026-11-01T22:17:10Z**, that the FP check “uses no main RAM” is not literally true of the supplied implementation: `Fp` uses a stack array, while the integer and hash stages use large buffers.

The old “2.5 windows/day” luck calculation also assumes a sufficiently stable event process. Reboot policy, workload, detection, and settings changed; a pre-raise boot already reached **29.12 hours before first detection**. Those probabilities should not be treated as calibrated confidence in either a cure or a component diagnosis.

**2. The YMM signature fits state corruption better than an ordinary failing execution core.**

First, a qualification to the premise: the digest does **not directly observe every wrong result’s registers being zeroed**. It observes one alternative FP result per seed, then reproduces that alternative by a proposed zeroing mechanism for **three of eight seeds**. That is strong mechanistic evidence, but it is not a register capture or a unique proof of cause. Integer/hash corruption sharing the mechanism remains explicitly inferential.

Nevertheless, this is the most diagnostic evidence in the package.

Two documented architectural mechanisms produce precisely this kind of separation:

- `VZEROUPPER` clears the upper halves while preserving the lower 128 bits. [Intel instruction reference](https://cdrdv2-public.intel.com/671110/325383-sdm-vol-2abcd.pdf)
- XSAVE manages those upper halves as **AVX state component 2**, separately from the XMM state. A restore that incorrectly treats that component as initial can clear it while preserving lower halves. [Intel architecture manual, §§13.5.3 and 13.8](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)

Microsoft explicitly requires kernel drivers to save and restore AVX state before using it, including in DPC routines, to preserve the interrupted application’s context. This is a documented route to application corruption on otherwise healthy processors. **It does not prove any named driver here violates that rule.** [Microsoft driver requirements](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kesaveextendedprocessorstate)

That mechanism explains several observations together:

- AVX/FMA paths fail while tested scalar paths survive.
- Native Prime95 and OpenSSL can fail alongside managed applications.
- Multiple cores exhibit the same FP alternative.
- Failures can follow uptime-dependent driver or virtualization activity.
- Reboot resets the triggering state.
- Logical processors can differ because interrupt and deferred-work placement differs.

The even/odd imbalance strengthens this interpretation. `digest/watch_per_cpu_by_era.tsv`, turbo-off/pre-raise row, gives CPU **2:591 versus 3:34**, and every tested pair favors the even-numbered processor.

A failing shared vector execution resource could affect siblings unequally: architectural thread state is separate, resource allocation differs, and exposure is not identical. Therefore **unequal siblings do not exclude CPU hardware**. But a consistent numbering-related bias across all cores needs an explanation beyond “bad core.” Processor-specific interrupt/DPC placement supplies one; Windows maintains per-processor DPC queues and permits explicit targeting. [Microsoft DPC documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/organization-of-dpc-queues)

There is also an experimental confound: the watcher checks processors sequentially. Processor number is therefore coupled to test order. Randomizing that order and measuring mismatch rates against completed work would help distinguish topology from scheduling effects.

A defective CPU remains possible—particularly its state tracking or save/restore behavior. That is a more specific hypothesis than failing arithmetic hardware. A design or firmware interaction could also survive replacement with another CPU of the same model.

**3. Your register-hold test has a consequential blind spot.**

`findings/steve_diag/Program.cs`, `HoldLoop`:

```csharp
var a=Avx.LoadVector256(want);var c=Avx.LoadVector256(want+4);
```

The initialization in `Hold` makes those two vectors identical:

```csharp
for(int q=0;q<4;q++)w[q+4]=w[q];
```

The loop then compares **the two registers against each other**:

```csharp
var e=Avx2.CompareEqual(a,c);
```

If an interruption clears both upper halves, **they remain equal**. The test can pass after exactly the corruption now suspected.

Thus the ledger’s **2026-10-31T19:01:00Z** statement—

> “A YMM register held in a spin stayed intact … against a simple clobber”

—is stronger than this test supports. It demonstrates no detected divergence between the compared values, subject also to actual generated code.

The replacement test should compare register contents against unchanged memory or scalar-held truth, inspect the assembly, and deliberately inject `VZEROUPPER` to prove detection.

Other instrument limitations matter:

- `Core` computes its own references on the suspect machine. A repeatable wrong reference and repeatable wrong results can agree. The digest confirms references were sometimes corrupted.
- The stopwatch starts **before** reference generation. If reference generation consumes the allotted time, the code can return success with zero comparison rounds. Require a minimum amount of verified work.
- The injected control flips an integer result. It validates that mismatch path, not sensitivity to simultaneous register clearing.
- Affinity-setting success is unchecked; the later processor sample is useful but incomplete.
- The supplied `Core` returns 1 when `bad>0`. **Simple starvation does not, by itself, explain exit 1 in this source.** It more naturally creates inadequate coverage. Match the two post-raise exits to their actual mismatch records.

A JIT or calling-convention defect is another instrument hypothesis. Windows treats YMM upper portions as volatile across ordinary calls, so generated code must preserve live values appropriately. [Microsoft x64 conventions](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions)

However, a checker-only bug fits the independent native failures poorly. It could distort your monitoring without explaining the entire incident.

**4. The alternatives have different predictions.**

| Candidate | Fit to this package | Discriminating prediction |
|---|---|---|
| **Driver / Windows / Hyper-V AVX-state corruption** | Best match to the architectural signature and logical-processor bias | Fault changes with the privileged software environment or correlates with particular interrupt/DPC activity; independent native probes capture upper-half loss |
| **Board firmware / SMM state handling** | Can affect application state across cores and survive service disabling | Fault can persist across OS changes but depend on firmware configuration; CPU replacement on the same board may leave it intact |
| **Board / VRM / socket electrical fault** | Still credible; delivered voltage, transients and VRM temperature were not established | Original CPU works in a known-good board, or replacement CPU fails in this board; behavior may depend on power transitions or socket contact |
| **PSU / supply connection** | Possible, but the selective AVX signature is a weaker fit | Changes under a known-good supply or combined CPU/GPU load; needs an account of the precise register-state effect |
| **DIMM / memory controller / memory path** | Downgraded by clean tests and the signature, not excluded | Errors follow DIMM/channel/loading changes, or independent memory testing fails; corruption of saved state is possible but currently speculative |
| **CPU silicon** | Supported by real, affinity-associated native computation errors | Failure follows this particular CPU into a known-good platform and remains under an independent software environment |
| **Checker / soak orchestration** | Demonstrated weaknesses; insufficient as the sole historical explanation | Corrected independent probes disagree with existing classifications; process exits correlate with lifecycle handling rather than wrong arithmetic |

A board voltage fault does not inherently explain upper-half clearing better than CPU hardware. Its main claim is **continued plausibility without a discriminating test**. The software/state-management alternative has the stronger positive signature.

PawnIO and the temperature sampler cannot explain the original October failures: they were installed later. They can still change the later environment, so monitoring should be included in subsequent isolation tests.

**5. There is a cheaper discriminating sequence before purchasing a CPU.**

My next step would be a **validated native register-state probe in the existing Windows environment**, paired with scalar/SSE controls and fixed expected results.

It should:

1. Detect deliberately injected upper-half clearing.
2. Capture full register values at failure.
3. Record affinity success, completed work, PID and precise timestamps.
4. Run with randomized processor order and with both steady computation and frequent scheduling transitions.
5. Run while reproducing the workload associated with historical failures.

This requires no purchased part and directly tests the newly identified mechanism. It also repairs the most relevant negative test in the record.

Next, compare software environments while retaining the validated probe:

- **Run the pending WSL2 comparison during a Windows failure.** A guest-only clean result would support an environment distinction, but guest affinity does not by itself establish matching physical placement, and WSL2 still shares the hypervisor.
- **Use a separate Windows boot configuration with the hypervisor disabled**, verifying its absence after reboot. Merely stopping WSL does not perform that experiment. Microsoft documents the `hypervisorlaunchtype` setting. [BCDEdit reference](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/bcdedit--set)
- **Test with the relevant third-party kernel drivers actually absent**, rather than only their known callers stopped.
- If ambiguity remains, use a **bare-metal live Linux environment** with native AVX/FMA and register-preservation probes.

The package says WSL hosts remote-control processes, so the hypervisor-off experiment needs a working Windows-side access and recovery path.

One clean boot is insufficient: the record contains long clean intervals before intervention. A convincing result is reproducible failure in one condition, sustained comparable exposure in the other, and recurrence after restoring the original condition.

If hardware substitution becomes necessary, a **borrowed known-good CPU and reciprocal board test** offers more diagnostic value than an unpaired purchase. “Failure follows the CPU” is much stronger evidence than “the machine improved after a CPU installation.”

**6. A failed CPU purchase buys limited information.**

There is no current replacement quote, labor rate, return policy, or resale value in the package. A dollar estimate would be invented.

The exposure is the CPU’s unrecovered purchase cost, shipping or return costs, installation materials and labor, downtime, and any subsequent diagnosis. Whether that is economically preferable depends partly on the owner’s stated cost of visits. A convenient substitution can be a rational operational choice without being a proven diagnosis.

If a known-good replacement CPU shows **the same captured fault under comparable conditions**, the old CPU becomes substantially less likely to be the necessary cause. Board, firmware, power and software remain unresolved.

If replacement appears to cure it, you have changed more than silicon: socket contact, cooler mounting, thermal interface, firmware initialization and sometimes settings also change. Without comparable exposure—and ideally an old/new/old comparison—you have evidence for the intervention, not conclusive proof of CPU degradation.

**7. Where your verdict is right.**

The computation fault is real. Independent SHA failures and Prime95 rounding errors prevent dismissing this as a dashboard misunderstanding or a RimWorld bug.

You are also right that:

- Masking one core did not solve it.
- Open-case operation and turbo limiting did not guarantee correctness.
- Ordinary measured core temperatures weaken a simple overheating explanation.
- Clean memory tests lower RAM’s priority.
- The vendor A/B usefully narrowed the suspects.
- CPU replacement is a legitimate substitution test and may be the fastest practical repair.

What the evidence does not justify is elevating that option to an established failing-part diagnosis.

**My verdict: recurrent AVX-state corruption is established much more strongly than CPU-package failure. A driver/OS/hypervisor or firmware preservation defect is my leading explanation; CPU and board hardware remain serious alternatives. I would validate the register probe and perform a software-environment comparison before buying a CPU.**

**My probability that a known-good CPU swap alone ends the recurring SIMD fault is roughly 40%.** That is a subjective engineering judgment, not a measured probability or a statistical result from these logs.