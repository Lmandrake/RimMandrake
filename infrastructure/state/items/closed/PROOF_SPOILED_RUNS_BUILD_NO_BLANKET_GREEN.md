# PROOF_SPOILED_RUNS_BUILD_NO_BLANKET_GREEN

Source: Transient/foundry_bridge_system_review_gpt_20261010.md (row 14 line 791; N42 line 165; line 748; line 881 debug Q4; line 869). GPT opinion. The owner's operational rule (visitor CLEAN-with-note) stands; GPT flags that stronger visitor-sensitive acceptance "needs a policy decision" and that belongs in GPT_CONFLICTS_FOR_OWNER_DIGEST, not here.

## spec
GPT quotes:
- Row 14 "Spoiled-run and acceptance regression suite: Unknown blocking window, visitor-sensitive gap, empty rows, DRAFT status, capped list, log blindness: cannot produce blanket GREEN."
- N42 "Visitor removal itself perturbs the test ... Record intervention and affected dependencies; criterion-specific eligibility."
- Q4: "may need/mood/job criteria become INDETERMINATE when relevant interference was not observed well enough, even if the visitor is removed and the run continues?"
- "Slow is not hung. Low TPS alone should not fail a tick-semantic check."

Build: fixtures for each spoil class fed to the acceptance gate (validation_core / proof harness); gate returns INDETERMINATE or UNMEASURED per criterion, never overall GREEN. Where the criterion class need/mood/job and the visitor gap is unobserved, the gate emits INDETERMINATE plus a note (policy choice about FAIL vs note is the owner's; implement the INDETERMINATE state only and flag).

## verify
- One selftest case per listed class asserts non-GREEN overall.
- A clean fully observed run still reaches GREEN (control).
- Run: python3 src/RimMandrake/Utils/run_selftests.py --only <the new test>.
