You are an independent hardware-failure analyst. A Windows 10 desktop (i9-10900K, ASUS ROG STRIX Z490-G, 4x32 GB DDR4-2666,
RTX 2080 Ti) produces wrong results from vector (AVX2/FMA) code and crashes in unrelated processes. The files below are the
facts sheet, the digests of every telemetry stream, the instruments' source code, and the analysis of the checker's wrong
results. No conclusion of ours is included on purpose: judge the evidence yourself. Use web search where it helps (Intel errata,
Windows/Hyper-V bugs, known 10900K or Z490 failure reports), and cite links for anything you take from the web.

Answer, in this order:
1. What is failing? Give a probability (summing to 100%) for each of: (a) the CPU silicon itself, (b) the board / VRM / socket /
   power delivery, (c) memory, (d) the PSU, (e) software below the application: OS kernel, hypervisor (Hyper-V/WSL2/VBS), a
   kernel driver, firmware/SMM/microcode state, (f) something else (name it). For each, the evidence for and the evidence
   against, citing the file and line or table row.
2. Pay particular attention to `digest/chk_mismatch_analysis.md` item 5: every wrong floating-point result equals the correct
   result with the two upper 64-bit lanes of a 256-bit register turned into the x86 default NaN, i.e. the upper 128 bits of YMM
   registers were zeroed. What mechanisms produce exactly that, in hardware and in software, and which of them fit "acquired
   during uptime, held until reboot, cleared by every reboot", the even/odd hyper-thread imbalance, and the change after
   2026-11-17? Is there any known Intel erratum, Windows/Hyper-V bug or driver behaviour that matches?
3. Which single cheapest test (cost in money, hands-on time and machine time; the owner is remote and a person must travel to
   touch the machine) would most change those odds? Give the expected result under each leading hypothesis. Also give the next
   two tests after it.
4. Could our instruments be fooling us? Check the checker source (Program.cs), the watch script, the soak script, the sampler
   and the digests for ways a count, a "clean" boot, a vcore reading or a temperature could be wrong or blind. Name each one and
   what it would change.
5. What does the post-2026-11-17 data (2 bad cycles in 770, a 54 h clean boot under a Prime95 soak, zero application crashes)
   support, given that the game workload stopped at the same time? Separate what the voltage raise could explain from what
   the workload change could explain.

Be concrete and quantitative. Say "unknown" where the evidence does not decide. Do not invent prices or numbers.
