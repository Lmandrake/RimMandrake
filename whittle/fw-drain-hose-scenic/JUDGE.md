```json
{
  "item": "HOSE_SCENIC_SELFTEST_FIX_NEVER_CROSSES",
  "judge": "independent read-only Opus 5.5 (claude-opus-5-5)",
  "root": "/home/mandrake/rm/scratch/BENCH/fw-drain",
  "bullets": [
    {
      "bullet": 1,
      "text": "The ScenicRoute forced-lay fixture requires traversing costed building cells and asserts a successful hose lay across them.",
      "verdict": "MET",
      "evidence": [
        "HoseReviewChecks.cs:448-460: a remote 2x2 costed footprint at x=12..13, z=8..9 (SetExtraCost BuildingCrossCost). Full-width walls at z=7 and z=10 (x < boxed.Width = 44). Lay goes from reel.Mouth with reel.Outward to (8,9).Centre. The assertion requires forced.Ok && Crosses(Flat) && Crosses(Plump).",
        "Crosses (456-458) needs, for EACH column x=12 and x=13, a pose sample with x in (x+0.1, x+0.9), z in (8.1, 9.9) and ExtraCost >= BuildingCrossCost. A boundary graze, a non-costed point or a single column cannot satisfy it.",
        "The mouth is (20.026, 8.773) (exact_stdout.txt:1) and Outward is west (HoseMath.cs:2794, 2729), so the nozzle and the source reel (x=20-21) sit 6+ cells from the remote columns. Nozzle contact cannot count.",
        "Out-of-bounds cells are unwalkable and BlockAt = Wall (CordWorld.cs:308-309). Hose Lay plans with dive=false (HoseMath.cs:393; CordPlanner.cs:308-309). Clear rejects wall depth beyond ClipTolerance and diagonal pinches (HoseMath.cs:1520-1526). DirectJoin returns null without endInward (HoseMath.cs:411). So there is no alternate corridor. The in-fixture control at 462-466 confirms this: blocking only the remote footprint yields 'no route'.",
        "LayOnce pins F[0]=a and F[last]=b (HoseMath.cs:925-926, 945-946), so a successful lay runs nozzle to target and is not a partial lay."
      ]
    },
    {
      "bullet": 2,
      "text": "Executable controls show the original fixture misses a building-as-block regression and the repaired fixture catches it. The relevant production-linked FlowWorks selftest passes on final sources.",
      "verdict": "MET",
      "evidence": [
        "exact_mutant.py extracts ScenicRoute verbatim from git HEAD (original) and from the working tree (final). Each production input is asserted against probe_manifest.json hashes before staging (lines 29-31).",
        "building_block_mutant.patch changes exactly one line, CordPlanner.Walk: it adds && ExtraCost < BuildingCrossCost and keeps the c==start || c==goal exemptions. Walk is used only by non-dive Search (CordPlanner.cs:162-163). CordWorld, Clear, nozzle and shaping are unchanged. mutant_receipt.json shows only CordPlanner.cs with a differing stage_sha256.",
        "exact_stdout.txt: every Original and Final line PASSes, including Final 'cost never blocks ... laid'. mutant_stdout.txt:7 is Original forced PASS. mutant_stdout.txt:14 is Final FAIL '... no route'. All other Final checks PASS. The mouth is the same in both runs. The program exits non-zero unless Original passes and Final flips, and it throws on any non-'no route' fault. Both receipts have returncode 0.",
        "Wrapper run: selftest_receipt.json returncode 0. selftest_stdout.txt reads 'PASS 1/1 FAIL 0/1 ... RESULT: GREEN'. csharp_stdout.txt:1470 '1240/1240 passed', :1485 'HoseGptFix: 27/27', :1509 'hose: 457/457'. There is no FAIL, error CS or UNMEASURED; Thirst_harmony_target_and_call_sites ran ok (:1290). The 27 count matches the 27 static Check sites now in HoseGptFix (26 before the new can-fail check), which ties the run to the final source.",
        "The same strings appear verbatim in the retained raw write line selftest_output_writes.strace:22 from wrapper PID 247912. process_samples.jsonl identifies that PID as selftest_flowworks_stock.py, child of runner 247739."
      ]
    },
    {
      "bullet": 3,
      "text": "Evidence identifies the exact tested source and its limits. The repair preserves shipping behavior and the approved GSS cord appearance.",
      "verdict": "MET",
      "evidence": [
        "integrity_before / during_proof / post_proof / pre_judge all record HEAD fea33f6, HoseReviewChecks.cs 80815870…, CordPlanner.cs 2b1a8ab0…, CordWorld.cs 71e15119…, HoseMath.cs dd6e26b9…, selftest_flowworks_stock.py 1c4bc152…, run_selftests.py 651f5e82…. Git status shows only HoseReviewChecks.cs modified.",
        "exact_receipt fixture_source_sha256 = 80815870…, the same hash. stage_after_proof.json shows the Windows stage HoseReviewChecks.cs and CordPlanner.cs matching, with 'mismatches': [].",
        "Reference: reference_remeasurement / reference_final_identity / reference_windows_readback match the prior provenance (assembly 5cf1b5be…, Pawn_NeedsTracker.cs fa588681…). RIMWORLD_DECOMPILED was passed through WSLENV in the run.",
        "The repair is test-only. SelfTest is a separate net8.0 project excluded from the mod build (RimMandrake_FlowWorks.csproj:20-22). No production, shared-geometry (GSS) or art file changed, so shipping hose and GSS cord behavior are unchanged by construction.",
        "The source_diff.patch hunk leaves the planned/old detour, carried/carriedOld, shortcut and live-world wiring checks (HoseReviewChecks.cs:434-443, 467-476) byte-identical."
      ]
    }
  ],
  "questions": {
    "q1_unavoidable": "Yes. No mere nozzle contact, boundary graze, alternate corridor, failed or incomplete lay, or non-costed point can satisfy the assertion (reasons in bullet 1).",
    "q2_linkage_and_mutant": "Yes. Both fixtures are extracted verbatim and run on hash-checked production kernels. The mutant is the single Walk rule, with start/goal exemptions, nozzle origin, collision geometry and the other planner rules preserved. The final failure is exactly the forced crossing ('no route'), and the old assertion still passes.",
    "q3_wrapper_proof": "Yes. The authorized wrapper returned GREEN, actual C# stdout was decoded from the observed wrapper PID, and stage and source identity are unchanged before, during and after the run. No hidden failure or reference mismatch was found.",
    "q4_preservation": "Yes. The detour, uncosted, carried, shortcut and wiring checks are preserved, and the repair is test-only."
  },
  "limitations": [
    "The mutant controls run in an isolated net8.0 probe. It compiles 11 hash-matched production files plus a RiverSwitchFlipChecks shim, not the full SelfTest project. Only the unmutated final fixture ran in the real wrapper.",
    "extract_output.py deleted the full strace after filtering. Only wrapper and runner lines are retained, and the original observer hash (3d907ef0…) can no longer be re-verified.",
    "The runner reported the result 'not recordable: changed during the run'. cache_record_refusal.json attributes this to /etc and /home/mandrake folder mtimes, a clock read and /mnt/c externals, not repo sources. The refusal rows are not timestamped, so the attribution to this run is circumstantial. The source integrity snapshots independently show no repo source change.",
    "Crosses depends on pose sample density. This can only cause a false FAIL, never a false PASS, and the poses passed on the current kernels.",
    "I did not recompute hashes; I am relying on recorded sha256 values. The current HoseReviewChecks.cs text matches source_diff.patch on read.",
    "There was no live in-game validation, and none is implied. Shipping and GSS preservation is by construction (no production diff), not by a visual check."
  ],
  "defects": [],
  "extraction_receipt": {
    "read_source": [
      "src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs:1-60,312-351,390-499 (+Check-site grep)",
      "src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs:370-414,914-988,1436-1539,2700-2799 (+greps)",
      "src/RimMandrake/_Shared/SlackGeometry/CordWorld.cs (InBounds/IsWalkable/BlockAt/ExtraCost greps)",
      "src/RimMandrake/_Shared/SlackGeometry/CordPlanner.cs:20-189 (+Plan/AStar greps)",
      "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj (Compile greps)",
      "src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj:15-29",
      "src/RimMandrake/Utils/selftest_flowworks_stock.py, run_selftests.py, known_results.py (greps)"
    ],
    "read_evidence": [
      "STATEMENT.md, NOTES.md, source_diff.patch, building_block_mutant.patch, exact_mutant.py",
      "exact_stdout.txt, mutant_stdout.txt, exact_receipt.json, mutant_receipt.json, probe_manifest.json, *_program.cs.txt (greps)",
      "pre_broaden/building_block_mutant.patch, pre_broaden/mutant_stdout.txt, instrument_failures.md",
      "selftest_running.json, selftest_receipt.json (head), selftest_stdout.txt, csharp_stdout.txt:1-30,1440-1510 (+greps)",
      "selftest_output_writes.strace (greps), output_extraction.json, extract_output.py, process_samples.jsonl (grep), cache_record_refusal.json",
      "integrity_before/during_proof/post_proof/pre_judge_integrity.json (greps), stage_after_proof.json (head/greps/mismatches)",
      "reference_remeasurement.json, reference_final_identity.json, reference_windows_readback.json, ../fw-drain-selftest-resume/evidence/reference_provenance.json (grep)"
    ],
    "not_relied_on": ["DONE.md", "BROADEN.md", "FINDINGS.md", "verification.json conclusions", "prior judge outputs"]
  },
  "would_show": "yes"
}
```

**Summary:** All three bullets are met, with no actionable defects.

1. **The crossing is forced.** Full-width walls at z=7 and z=10, map bounds that count as walls, a hose planner with diving off, and wall-clearance checks leave rows 8–9 as the only corridor. The remote 2×2 costed footprint spans both rows, so any lay from the west-facing nozzle (x≈20.03) to (8,9) must cross it. The assertion needs interior, costed samples in both columns, in both the flat and plump poses, on a lay that succeeded.
2. **The controls work and the real run passed.**
   - The single-line mutant (cost treated as a block in `CordPlanner.Walk`, start/goal exemptions kept) leaves the original fixture passing.
   - Under that mutant the final fixture fails with exactly "no route", and every other check still passes.
   - The real wrapper run is GREEN. Its C# output, decoded from the observed wrapper PID, shows `HoseGptFix: 27/27`, `1240/1240` and `457/457`.
3. **Source identity and shipping behavior hold.** Source and Windows-stage hashes match before, during and after the run, with HEAD fea33f6 throughout. The only modified file is the SelfTest-only `HoseReviewChecks.cs`. The other ScenicRoute checks are unchanged, and the engine reference identity matches.

**Limitations:**
- The mutant ran in an isolated probe built from hash-matched production files, not the full SelfTest project.
- The full strace was deleted after filtering, so its original hash can't be re-checked.
- The runner's "changed during the run" cache refusal is attributed to non-repo folders. The integrity snapshots independently show no repo source change.
- I did not recompute hashes, and there was no live in-game validation.

would show: yes