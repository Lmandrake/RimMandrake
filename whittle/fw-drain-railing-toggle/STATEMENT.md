# Railings stay on after cancelling their pending removal

- Switching a suspension bridge’s railings off and back on before deconstruction cancels the existing railings’ Deconstruct designations, leaving those railings available while the switch is on.
- Production-linked regression checks reproduce the defect and protect the repair while preserving unrelated designations and existing blueprint, frame, material and god-mode behavior. The relevant FlowWorks selftest and shipping build pass.
- A disposable live-game check exercises the repaired off/on toggle on the deployed DLL and records identities, results, restoration and remaining limits.
