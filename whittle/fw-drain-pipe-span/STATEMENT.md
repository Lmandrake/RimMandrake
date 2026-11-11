# Make the pipe-span callback regression guard useful

- The pipe-span selftest rejects the retired counter-only OnSpansChanged callback even after source whitespace is collapsed, and accepts the current callback that invalidates the liquid net when the span set changes.
- Meaningful negative controls demonstrate the repaired guard can fail; the existing production net-bump, listener registration and join-order checks remain effective, and the relevant FlowWorks selftest passes on the final sources.
- Evidence identifies the exact tested source and reconciles the later triage note with the actual callback contract. Shipping behavior and the approved GSS cord appearance are preserved.
