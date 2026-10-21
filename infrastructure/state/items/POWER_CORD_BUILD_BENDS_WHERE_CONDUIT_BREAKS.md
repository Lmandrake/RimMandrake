## spec
A new **flexible power cord** def: the only power line that may lie on a bridge deck (any deck, rope included) and on a
drawbridge leaf (disconnects while raised, rejoins when lowered). Owner, review answer 5 (card, 2026-10-20): the
GSS-restyled vanilla `PowerConduit` is rigid conduit and crosses only by poles; *a separate flexible power cord is what
lies on decks*. No such def exists today (GSS restyles `PowerConduit`; no cord/cable/wire ThingDef in GSS or FlowWorks
Defs, measured 2026-10-20).
- Carries power like a conduit; tagged `FlexCord` by the line tag of `PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE`.
- Never on an excavated square or a cover; digging under one breaks it; a deck collapse drops it as a fallen live wire
  (reuse `RM_FallenWireShock`).
- Lives in GSS (power) or FlowWorks (decks): decided at build. Art follows the GSS cable looks, after
  `LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED`.
Spec: `design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md` §Ruled design P1-P4. ESTIMATE 1.5 to 2
agent-days plus art. Open: does a submerged cord short (design doc Q1).

## verify
- L1: selftests — cord placeable on rope/timber/steel decks and a drawbridge leaf, refused on dug squares and covers;
  restyled conduit still refused on decks.
- L2 (live): a cord across a timber deck powers a lamp on the far bank; raise a drawbridge carrying a cord: the lamp
  goes dark and returns on lowering.
