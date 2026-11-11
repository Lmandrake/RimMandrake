# Completed claim

- true: Switching a suspension bridge’s railings off and back on before deconstruction cancels the existing railings’ Deconstruct designations, leaving those railings available while the switch is on. | evidence: `whittle/fw-drain-railing-toggle/evidence/parent_acceptance_refreshed.json`
- true: Production-linked regression checks reproduce the defect and protect the repair while preserving unrelated designations and existing blueprint, frame, material and god-mode behavior. The relevant FlowWorks selftest and shipping build pass. | evidence: `whittle/fw-drain-railing-toggle/evidence/parent_acceptance_refreshed.json`
- true: A disposable live-game check exercises the repaired off/on toggle on the deployed DLL and records identities, results, restoration and remaining limits. | evidence: `whittle/fw-drain-railing-toggle/evidence/parent_acceptance_refreshed.json`

The evidence file is a fresh readback of the preserved raw executions, current source/test/build/stage/deployed identities, restoration and shutdown. Its primary raw paths remain available. The C# suite ran once; the later Python-only schema correction and supporting off capture are separately published, tested offline and exercised live. No pawn-job completion, full-list acceptance, stale-ON automatic healing or new GSS visual approval is claimed.

The parent readability follow-up preserves C# syntax tokens, project XML structure and Python AST. The full suite ran before formatting. Current formatted harness and live-driver controls pass. Shipping compile inputs and artifacts remain byte-identical. The live execution used the AST-equivalent published driver.
