# BRIDGE_HOOKS_HARDEN_REENTRANT_AND_FAULTY

Source: Transient/foundry_bridge_system_review_gpt_20261010.md (line 58, N23 line 146, row 11 line 788, line 689). GPT opinion; ruling: never live-test a flyer's flight (irrelevant here); no new always-on hook without proof.

## spec
GPT quotes:
- "Copy a bounded immutable snapshot on the main thread; serialize and write that snapshot elsewhere. Returning a game object from InvokeAsync and serializing it later defeats the boundary."
- N23 "Cross-thread snapshot/lock deadlock ... No game API on writers; no main-thread waits for writer; immutable snapshots and bounded handoff."
- Row 11 "Production Harmony safety hardening: Reentrancy, skipped prefix, exception, off-thread, late install, writer fault: game result/exception preserved, coverage failure visible, stacks clean."
- "For the first full-list launch, keep unproven generation hooks disabled."

Build: audit the recorder hooks in the JawaBench/recorder C# for those six faults; fix each; keep unproven always-on hooks disabled until their test passes.

## verify
- A test (offline harness or minimal-list quicktest) per fault: the original game return value or exception is unchanged, and a coverage-failure marker is visible in the recorder output.
- Writer fault does not block the main thread.
- List of hooks with enabled/disabled and proof reference.
