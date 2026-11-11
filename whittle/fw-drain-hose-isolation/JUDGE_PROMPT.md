You are a fresh independent read-only Opus judge. Do not edit files, execute code, launch tools beyond Read/Glob/Grep, or mark anything CLEAN. Judge only the frozen statement below against actual source and raw executable proof. Do not use builder conclusions from DONE.md, BROADEN.md or FINDINGS.md as evidence. No prior session, fork or maker history applies.

Repository root: /home/mandrake/rm/scratch/BENCH/fw-drain
Whittle directory: whittle/fw-drain-hose-isolation

Frozen STATEMENT.md (read actual file and NOTES.md too):
- The TankEndpoints two-run fixture uses recognized, disconnected pipe runs and proves the pump reaches the near tank while excluding the far tank.
- Meaningful controls prove the repaired assertion detects unintended tank conduction and fails on the old unrecognized fixture; the relevant production-linked FlowWorks selftest passes on final sources.
- Evidence identifies the exact tested source and limitations. Shipping behavior and the approved GSS cord appearance are preserved.

Read the entire actual src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs, particularly G, Walk and TankEndpoints. Read relevant production RM_NetComponents, Seeds, Build, Conducts, StoreOf, RouteIn inside src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs (there is no separate RM_LiquidNetComponents.cs). Consult src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs for graph adapter geometry if needed. Read design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §3.1 and current kernel header for the endpoint rule. Read the actual SelfTest csproj and src/RimMandrake/Utils/selftest_flowworks_stock.py for production linkage.

Raw proof paths under whittle/fw-drain-hose-isolation/evidence:
- original_HoseNetChecks.cs (pre-change file)
- fast_probe.py (isolated staging, complete-kernel compilation, Program.Check stub, mutant construction)
- fast_reproduce/{Program.cs,Kernel.cs,HoseNetChecks.cs,Probe.csproj,stdout.txt,stderr.txt,receipt.json}
- fast_final/{Program.cs,Kernel.cs,HoseNetChecks.cs,Probe.csproj,stdout.txt,stderr.txt,receipt.json}
- fast_old_fixture/{Kernel.cs,HoseNetChecks.cs,hose.diff,kernel.diff,stdout.txt,stderr.txt,receipt.json}
- fast_tank_conduction/{Kernel.cs,HoseNetChecks.cs,hose.diff,kernel.diff,stdout.txt,stderr.txt,receipt.json}
- integrity_original.json, integrity_before.json, integrity_after_test.json, integrity_before_review.json
- selftest_receipt.json, selftest_stdout.txt, selftest_stderr.txt, csharp_stdout.txt, csharp_stderr.txt
- record_proof.py, extract_output.py, integrity.py, output_extraction.json, selftest_output_writes.strace (exact wrapper and runner stdout writes)
- process_samples.jsonl and selftest_writes.strace (full external observer; large, read only portions if necessary)
- cache_record_refusal.json (actual reasons behind the wrapper cache-recording refusal; distinguish cacheability from executed test results)
- reference_remeasurement.json and referenced prior reference_provenance.json (read its path)
- proof_checks.json and source_diff.patch (mechanically derived receipts/diff, check against actual source/raw outputs)

Questions:
1. Do the recognized pipe names and graph contacts implement the frozen requirement without an alternate touch/hose shortcut? Does the assertion require real near reachability as well as far exclusion? Is both-run component existence positively tested?
2. Do the two executable negative controls isolate the old unrecognized fixture and genuine pipe–tank–pipe conduction in the real production kernel? Read the complete mutant diff and raw failures, not merely return codes. Could unrelated suites or an instrument error explain their failures?
3. Are final and mutant source identities traceable to actual source, with production unchanged outside the isolated staged mutant? Do wrapper source inputs and staged identities match before/after? Does raw C# stdout show this case and the full wrapper pass on final sources?
4. What limitations remain (fake graph geometry, isolated mutant scope, offline versus live game, appearance preservation rather than re-approval)? Are any material claims unsupported?

Return a per-bullet true/false verdict with concrete source/raw-proof references, any defects or limitations, and a final line exactly `would show: yes` or `would show: no`. Say yes only if actual evidence satisfies all three frozen bullets. Your report will be extracted unchanged.
