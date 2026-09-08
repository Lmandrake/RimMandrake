# CHRONICLE_EVENT_SPINE_1

## Spec
Owner adopted (card, 2026-09-08, on BENCH's advice): RimChronicle
(ex-Aftermath) is the shared event spine of the RM engine suite. Before
the consolidation sprint, write a ONE-PAGE spec: what an event row
carries (kind, actors, thing, map, tick, outcome), how an engine
subscribes, and the soft-hook rule — every integration is a MayRequire
hook, never a hard dependency; each engine must ship standalone.
Producers/consumers to name in v1: RimProperty taking-events IN;
battle records IN (existing recorder); RimPursuit noticedness reads
FROM the record; Ninefold god-deltas and ChronicleRites rules interpret
FROM it. Battle-scoped v1 stands (R5): design the hook API for more
event kinds, build no universal recorder now.

This is DESIGN work — per Agent_Policy it drafts on a backgrounded
Fable agent; the sprint's merge rows for Chronicle/Property/Pursuit
land with these hook points named, so this item gates the sprint's
Chronicle rows.

## Verify
The page exists in design/, names every v1 producer/consumer, and each
hook is MayRequire-soft (grep: no hard modDependencies between the
engines).

## Criteria
One page; owner has seen it; sprint map's Chronicle rows cite it.
