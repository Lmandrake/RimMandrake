# GM_BLACKBOARD_SHADOW_M4_1 — the external blackboard, in shadow mode

Filed by FOUNDRY, 2026-09-13. Two queue items — `KYBER_TRADE_PLOT_1`
(BLOCKED: "Heat/Hutt-Interest GM blackboard (M4) unbuilt — cannot meet
verify's sale-raises-heat clause without inventing parallel infra") and
`CATHEDRAL_REGARD_BLACKBOARD_1` ("Depends on: GM blackboard M4... live in
shadow mode") — both name this milestone as a hard prerequisite, but no
queue item existed to build it. This item is that build.

## spec

`design/Jawa/build_plan.md` §4, milestone M4 (verbatim):

> The external blackboard: Imperial Heat + the orbital-detection timer + the
> dark-tile pause, as a Python state machine driven by polled reads. Runs in
> **shadow mode** for a whole playthrough of the thin slice — logs what it
> *would* fire, fires nothing. Then flip injection on a throwaway save, then
> for real. This is the instrument-autonomy staging ramp from
> `first_live_access.md`.
>
> **Exit:** a shadow log we can read and believe, before anything is live.

Read `design/Jawa/worldbuilding/enrichment_agents.md` §4 (the read → propose
→ human-approve → write-with-V&V → re-verify loop M0 already established —
this state machine is a consumer of that pattern, not a new one) and §7.1
("the headline unknown") for the reload-survival answer M0 already settled
— reuse it, don't re-answer it.

This item builds the STATE MACHINE and its SHADOW-MODE run only — polled
reads over the bridge, an Imperial Heat number, an orbital-detection timer,
a dark-tile-pause flag, logging what each WOULD fire without firing it. It
does NOT build: the live injection flip (a separate, later step per M4's own
"then flip... then for real" sequencing), `CATHEDRAL_REGARD_BLACKBOARD_1`'s
Regard counter/stage machine (a *consumer* of this blackboard, its own
item), or anything from `KYBER_TRADE_PLOT_1`'s own quest content (already
built, per that item's own note — only the blackboard was missing).

## verify

- The state machine runs against a live game session (polled bridge reads,
  per M0's primitive verbs) for a meaningful stretch of play and produces a
  shadow log of would-be Heat/timer/pause events.
- Nothing it does writes to the save, fires an incident, sends a letter, or
  otherwise mutates game state — shadow mode means read-only, by construction,
  not by discipline.
- The shadow log is legible enough that a human (or `CATHEDRAL_REGARD_BLACKBOARD_1`'s
  own later build) could believe and act on it.

## criteria

A shadow-mode run against a real live session produces a Heat number, an
orbital-detection timer state, and a dark-tile-pause flag that track sensible
inputs (kyber/mindstone sales, faction-13 goodwill, Cathedral-ground
presence — cross-check exact inputs against `design/Jawa/kyber_trade_plot_spec.md`
§2/§3 and `design/Jawa/cathedral_concealment_arc_spec.md`'s "The law" section,
which both this item and its two dependents must respect: knowledge gate,
bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen), logged
without firing anything. Live injection ("then flip... for real") is
explicitly NOT this item's exit bar — that is M4's own later half, owed to
a follow-up once the shadow log is trusted.
