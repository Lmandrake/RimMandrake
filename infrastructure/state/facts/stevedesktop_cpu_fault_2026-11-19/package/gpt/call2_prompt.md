You are an adversarial reviewer. Our team's verdict on this machine (i9-10900K, ASUS ROG STRIX Z490-G, 4x32 GB DDR4-2666) is:

    "The CPU is failing; replacing the CPU is the route."

That verdict was reached on 2026-11-17/18 after: a RAM test came back clean, a vendor-software A/B was falsified, turbo-off and
an open case did not stop the fault, and a +0.100 V core-voltage offset was followed by a fault window 4.13 h into the next boot
(see `findings/item_RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING.txt`, `findings/steve_fault_diagnosis.md`,
`findings/vcore_visit/BIOS_VISIT_STEPS.md`). The files below hold our findings documents, the ledger history, and the same
evidence digests an independent assessor saw. Use web search where it helps and cite links.

Make the strongest honest case AGAINST that verdict:
1. Which facts in the package does the verdict ignore, misread or over-weight? Quote them (file + the line).
2. What other cause (board/VRM/socket, power, memory, OS/hypervisor/driver/firmware state, our own instruments) fits the data
   as well or better, and what would each predict that the CPU verdict does not?
3. In particular: `digest/chk_mismatch_analysis.md` shows every wrong floating-point result is "upper 128 bits of YMM registers
   zeroed", and the even/odd hyper-thread counts are very unequal. Does a failing core fit that? What fits better?
4. Is "replacement is the route" the cheapest next step, or is there a cheaper discriminating test first? If we bought a CPU and
   the fault persisted, what would that cost and what would we have learned?
5. Where is our verdict right? Say so plainly where it is.
End with your own verdict and a probability that a CPU swap alone ends the fault. Do not invent numbers or prices.
