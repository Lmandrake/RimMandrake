
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §3 bullet 1: stage sets the *baseline* the kit's composite band recovers
toward — WARY reads flat/dull, TOLERATED+ breathes (richer band range, faster
recovery from low bands). Mechanism: a bridge lane feeding the kit's
data-driven `RM_BiomeAttitudeDef` thresholds (kit §1) — a small setter on
`RM_MapComponent_BiomeAttitude` exposed as a JawaBench bridge tool
(rimbridge-companion pattern), NOT a second attitude system. Dark flip (item
1) drives baseline back to WARY-flat regardless of history. No new defNames;
binds to the kit's two classes exactly as coined.

## verify
Bridge test on a quicktest Cathedral map: set stage WARY → band ceiling
flattens, dull drone only; set TOLERATED → band range widens and recovery
rate rises; irritation/goodwill machinery unchanged (kit §1's own tests still
pass); hysteresis bounds untouched (arc §8 seed 4); baseline survives save/
load without writing a new save stat beyond the map component's own state.

## criteria
One documented bridge tool; baseline parameters live in `RM_BiomeAttitudeDef`
data, not code; kit selftests green.

**Depends on:** RUST_CATHEDRAL_MECHANICS_1 §1 (the component + def exist);
item 1 (stage source). **Waited on by:** items 7, 8 (their hum registers).
**Seat/needs:** FOUNDRY; C# companion build + bridge + quicktest (game-up on
minimal list). Row-3 hard (C#, companion DLL) — model per
`infrastructure/agents/Agent_Policy.md` ladder.
