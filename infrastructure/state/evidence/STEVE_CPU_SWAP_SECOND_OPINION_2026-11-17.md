**1. The CPU is my leading suspect, with only moderate confidence.**

My rough allocation for the **computation fault**, assuming the reported failures are reproducible:

| Cause | Probability |
|---|---:|
| CPU package, including caches and memory controller | 45% |
| Motherboard, VRM, or socket contacts | 30% |
| RAM modules | 10% |
| PSU | 5% |
| Something else: firmware/settings, drivers, storage contamination, test defect | 10% |

These are judgment estimates, not statistically derived probabilities. CPU and motherboard are close enough that buying either outright is a gamble.

The evidence strongly suggests instability somewhere in the execution/memory/power path. It does **not** localize it to a degrading SIMD execution unit. Prime95 errors can originate from several components; its own documentation describes it as testing CPU, memory, and caches. [Prime95 documentation](https://www.mersenne.org/download/stress.txt)

Two important limitations:

- Your RAM results reduce suspicion but **do not exclude RAM**. One Basic pass and memory walks do not establish stability under every access pattern, load, or fault state. Were those walks performed while the arithmetic fault was actively reproducible? That matters. [MemTest86 troubleshooting](https://www.memtest86.com/troubleshooting.htm)
- Normal sampled temperatures and maximum Vcore do not exclude brief voltage droops, VRM trouble, or frequency/voltage transition problems. No WHEA events does not clear those possibilities.

**2. A replacement 10900K has roughly a 50% chance of fixing it; I would budget around 40–60%.**

That assumes a genuinely good replacement, conservative settings, and enough observation time. A different chip could also tolerate a marginal board better, or reseating could fix a contact problem, so successful replacement would not automatically prove degraded silicon.

**I would not spend a nonreturnable $400 yet.** You have not established stock-settings stability, fully excluded the Windows driver environment, or isolated the suspect SSD.

A borrowed or shop-supplied known-good 10900K is a sound diagnostic step. Reciprocal testing is stronger: your CPU fails in another good board, while its CPU passes in yours. A lower-power LGA1200 CPU passing in your board is weaker evidence because it changes the electrical load substantially.

**3. Yes. Start with a free experiment during an active fault, without rebooting.**

Record the existing boost setting from an elevated terminal:

```text
powercfg /qh SCHEME_CURRENT SUB_PROCESSOR PERFBOOSTMODE
```

Then disable boost:

```text
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PERFBOOSTMODE 0
powercfg /setactive SCHEME_CURRENT
```

Microsoft documents value `0` as disabled and applying this setting without rebooting. Verify that actual loaded core frequencies fall to approximately base frequency or below; an accepted command alone is insufficient. [Boost setting](https://learn.microsoft.com/en-us/windows-hardware/customize/power-settings/options-for-perf-state-engine-perfboostmode), [application instructions](https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/hardware/power/power-performance-tuning)

Run repeated batches of the same failing checker, restore the **recorded original value**, and repeat the off/on comparison.

- **Errors repeatedly disappear with boost off and return with it on, within one boot:** strong evidence of an operating-margin problem. CPU silicon, board voltage delivery, and firmware voltage policy remain candidates. It also disproves the stronger claim that rebooting is necessary for recovery.
- **Errors continue at verified lower frequency:** turbo instability becomes less likely; CPU, shared cache/memory path, board, and software remain.
- **One clean batch:** inconclusive, because your existing fault windows already contain clean cycles.

Before buying, also run the missing conservative BIOS baseline:

- Record current settings, then load optimized defaults.
- `ASUS MultiCore Enhancement = Disabled – Enforce All limits`.
- `Ai Overclock Tuner = Auto`, with XMP off.
- BCLK 100 MHz; CPU/core-cache voltage and load-line calibration Auto; no manual offsets.
- For a conservative memory baseline: DDR4-2133, 1.20 V, automatic timings.

These controls are documented in the [board’s BIOS manual](https://dlcdnets.asus.com/pub/ASUS/mb/LGA1200/ROG_STRIX_Z490-G_GAMING/E16801_ROG_STRIX_Z490-G_GAMING_Series_BIOS_manual_EM_WEB.pdf). If this passes repeatedly and the former settings reproducibly fail, configuration is implicated; permanent hardware damage remains unproved.

The next useful isolation test is a verified live Linux USB, **with the Samsung NVMe physically disconnected**, running mprime/Prime95 small in-place FFTs with AVX2/FMA enabled, plus alternating idle periods and your reproducible checker where portable. Reproduction there strongly weakens Windows-driver and SSD explanations. A pass is weaker because the workload and power management differ.

Use several boots and 12–24 hours per condition initially. Given the historical five-day onset, that is evidence, not certification. If memory remains suspect, repeat with one DIMM in A2 and substitute another DIMM. Failure following a particular module implicates it; failure only with four modules implicates memory loading, training, board, or CPU memory controller.

**No free software test cleanly separates marginal CPU silicon from marginal VRM delivery. Controlled substitution does.**

**4. Conclusion (a) is the weakest. Conclusion (b) is substantially correct. Conclusion (c) is plausible but untested.**

**(a): Your stated mechanism does not follow from the evidence.**

Errors moving between cores weaken the “one damaged core” explanation. They fit shared CPU circuitry, shared voltage delivery, memory corruption, and machine-wide state too. Reboot recovery distinguishes none of these reliably.

Also:

- Logical CPU numbers are not physical-core identities. Establish APIC/core/SMT mapping across the `numproc` change before interpreting CPU 18 versus CPU 2.
- Your record describes intermittent failures after onset, not continuously wrong arithmetic. “Persistent susceptibility until reboot” is the supported statement.
- Disabling callers while leaving kernel drivers loaded substantially weakens that particular caller hypothesis; it does **not** falsify software generally.
- The statement that **4.46 h falls inside a baseline whose maximum is 3.30 h is wrong**. That does not rescue the hypothesis, but the comparison must be corrected.

**The post-flash timing does not identify a component.** Three short onsets versus one five-day observation cannot establish a changed failure distribution. Workload, detection cadence, settings, training, and chance are uncontrolled.

Yes, changed firmware or microcode could alter behavior that exposes marginal silicon—or marginal voltage delivery. ASUS confirms that 3401 updates both microcode and ME; its release notes do not establish a particular voltage/frequency change. [ASUS BIOS release notes](https://rog.asus.com/us/supportonly/rog-strix-z490-g-gaming/helpdesk_bios/)

To attribute this to microcode, you would need matched firmware comparisons with settings, workload, actual loaded microcode revision, clocks, and voltage behavior recorded. **The timing does not increase my CPU-swap estimate.** If firmware policy is responsible, a replacement might merely have more margin.

**(b): Correct for a genuine like-for-like replacement.** ASUS lists the 10900K as supported since BIOS 0403. Your existing BIOS supports it; RAM and cooler compatibility do not change. Reuse the cooler if serviceable, with fresh thermal compound and correct mounting. [ASUS CPU support](https://www.asus.com/supportonly/rog%20strix%20z490-g%20gaming/helpdesk_cpu/)

**(c): Possibly separate, but you have not earned that conclusion.** An SSD fault is a poor direct explanation for a validated register/cache computation test using internally generated data. It can, however, corrupt files or contaminate tests that depend on disk reads. Shared board or power trouble could also affect both.

Back up important data, verify the disk identity by serial number, and obtain actual NVMe health/error logs using a tool that supports the drive. Empty counters and “Healthy” do not resolve 46,000 error events. Those events are also **not necessarily 46,000 distinct bad blocks**. Testing with the drive disconnected is the decisive separation experiment. Samsung provides model-dependent diagnostic facilities through [Magician](https://semiconductor.samsung.com/consumer-storage/magician/).

**5. No: this board/chip combination is an ordinary socketed LGA1200 installation. No soldering or special exception.**

The processor seats without insertion force; the retention lever applies substantial clamping force when closed. Intel explicitly includes LGA1200 in its installation procedure. [Intel installation guide](https://www.intel.com/content/www/us/en/support/articles/000005762/processors.html)

During the swap:

- Shut down, disconnect mains power, discharge residual power, and use antistatic precautions.
- Support the heavy air cooler while releasing its mounting. Keep the CPU retention plate closed while separating the cooler; do not wrench against hardened paste.
- Hold the CPU by its edges. Never touch or drag anything across the **socket’s fragile contacts**.
- Inspect for bent contacts or contamination. Align the notches and triangle, and lower the replacement straight down. Never use the lever to force a misaligned CPU into place.
- Clean old compound, let the cleaner evaporate, apply fresh paste, and tighten the cooler evenly according to its instructions. Reconnect CPU_FAN and check temperature immediately after boot. [Intel thermal-compound guidance](https://www.intel.com/content/www/us/en/support/articles/000005576/processors.html)
