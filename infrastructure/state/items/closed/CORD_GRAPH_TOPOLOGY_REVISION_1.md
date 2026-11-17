---
state: built
needs: bridge
---

# CORD_GRAPH_TOPOLOGY_REVISION_1

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

GimmeSomeSlack: Cord graph rebuilds the whole map for every section reprint; motion rescans all pieces per material

Built at `2c5974430623` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-11: Built the DrawMotion half only (2c5974430). The topology-revision half is deliberately NOT built, per FOUNDRY's 2026-10-09 note: a PollLive flip changes geometry, so the revision would bump on nearly every regenerate.
- 2026-10-23: Topology-revision half deliberately not built (FOUNDRY 2026-10-09); only A2 L2 live check of the DrawMotion half remains.
- 2026-10-29: Done when: A2 L2 live check of the DrawMotion bucket half passes (SwayHash/RippleHash and draw counters match before/after, MotionBucketBuilds rises only on rebuilds). Topology-revision half is deliberately not built (2026-10-09 note).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify CORD_GRAPH_TOPOLOGY_REVISION_1 --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=CORD_GRAPH_TOPOLOGY_REVISION_1` first: another commit may already do it.
