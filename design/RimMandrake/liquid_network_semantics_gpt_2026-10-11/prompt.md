You are reviewing a design for liquid-network semantics in a RimWorld 1.6 mod (FlowWorks: rigid pipes, portable flexible hoses on reels, tanks, pumps, converters, adapters to VE PipeSystem nets). The owner wants to avoid circuit/pressure flow simulation and suggested hoses be the only place direction is set ("sources or sinks"), everything else just "connected".

Attached: the design doc (sections 7-9 pending), the owner's binding rulings, and the key current code (net kernel, net adapter, pump, tank, pipe adapter).

Please:
1. Find defects: conservation leaks (liquid created or destroyed), any way to fill storage from the world without a pump (violates ruling #3), deadlocks/starvation, order-dependence, loops, save-compat traps, perf traps. Cite file:line in the attached code or section numbers in the design.
2. Judge the recommended model A (direction on hoses) against model B (per-tank inlet/outlet/drain toggles like Rimefeller) and any better model you can construct. Be decisive.
3. List anything a builder would have to guess (unspecified rules), with the rule you would pick.
4. Check that the delta list (section 6) is complete against the code: what else must change or be deleted.
Answer as a numbered list of findings, each with severity BLOCKER/MAJOR/MINOR, evidence, and a fix. Then a one-paragraph verdict. Max ~1500 words.
