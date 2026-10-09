# TAP_CONSERVATION_SELFTEST_1 — GS-6: Multi-tick power-tap conservation selftest and read-only conduit probe

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row GS-6 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| GS-6 | Robustness: tests and probes that cannot hide a bug. (a) A multi-tick conservation test for the power tap: what the victim paid must equal what we were credited. The double-pay found in review #19 was exactly this, and the current test checks one tick's math only. (b) The conduit-style probe should read state without first processing the pending work it is meant to measure. | Selftest with a fake net-tick loop. A read-only probe verb (keep `cprocess` as an explicit action). | S | low | GimmeSomeSlack | AerialSelfTest.cs:370-377 tests `TapStolenPerTick` per tick only. ConduitStyleProbe.cs:140 calls `runs.ProcessPending()` inside a read. VERDICTS GSS #19 shows the bug a ledger test would have caught. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: Selftest runs a fake multi-tick loop asserting victim paid == credited; ConduitStyleProbe read does not call ProcessPending (explicit cprocess verb remains).
