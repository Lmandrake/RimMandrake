# Rimflow redesign — addendum: the validation levels

Extends `rimflow_gpt_review_2026-10-07.md` (the `built` state, structured criteria, leases). The
review split criteria into *implementation* and *acceptance* but treated "acceptance" as one
bucket. This project already has a graded set of checks, and the item lifecycle should speak that
language instead of the vague "needs live".

## The levels that exist today

| Level | What it proves | Where it runs | Cost | Who/what |
|---|---|---|---|---|
| L0 offline | XML lint, `validate_patch.py`, selftests, texture validators, `validation.py` static bars | any clone, no game | seconds | the builder |
| L1 resolved-live | defs resolve in the real engine; `jawa/get_defs` against an expectations manifest | minimal mod list restart | ~22 s per cycle | an agent holding the bridge |
| L2 behaviour gauntlet | spawn, tick, harvest log once; art presence by machine | one quicktest map, batched per sitting | minutes, many items per sitting | an agent holding the bridge |
| north-star GREEN minimal | every `## north star` bar PASS on the minimal list (UNMEASURED is not green) | `northstar_driver` | minutes per mod | an agent with the bridge |
| north-star GREEN full | the same on the full canonical list, all five DLCs | full list | ~15 min cold load | an agent with the bridge |
| L3 Opus evaluation | art/style/thematic judgment | bridge in the evaluator's hands | one evaluator pass | an Opus agent |
| L4 human | gameplay, fun, thematic coherence, UI | review environment / keeper save | owner time | the owner only |

(`infrastructure/VALIDATION_LADDER.md`, `design/RimMandrake/debug_process.md`, `modcheck status`
reports GREEN / STALE / ORPHANED per mod.)

## Why this matters for the stuck-state problem

Today every criterion is free text and the only axis is `needs: offline|deploy|game-up|bridge|owner`.
A built item whose remaining proof is "L1, one 22-second minimal-list read" looks identical to one
that needs a 15-minute full-list load or an owner's evening. So acceptance work cannot be batched,
priced or routed, and `next` cannot tell an agent holding the bridge which items to sweep
in one sitting.

## Recommendations (additions to the review)

1. **Tag every criterion with its level**: `L0`, `L1`, `L2`, `GREEN-MIN`, `GREEN-FULL`, `L3`, `L4`.
   The review's O1/O2/L1 manifest becomes e.g. `O1 L0`, `A1 L1`, `A2 L2`, `A3 GREEN-FULL`, `A4 L4`.
2. **Derive `needs` from the cheapest outstanding level, not the first**:
   L0 -> offline; L1/L2/GREEN-MIN -> bridge on the minimal list; GREEN-FULL -> bridge + full list;
   L3 -> bridge + an Opus evaluator; L4 -> owner. An item is `built` when every L0 criterion passes
   and a *published sha* exists; it is `done` only when every tagged level has a passing record.
3. **Acceptance sittings are batched by level**: one bridge sitting sweeps every `built` item whose
   next level is L1/L2 on the minimal list (the 22 s workhorse); GREEN-FULL items wait for one
   cold load that covers all of them; L4 items go to the owner as a review environment, never as
   one card per item. `rimflow next --seat BENCH --sitting` would list the batch.
4. **`verify` records carry the level, the list (minimal/full), the built sha and the DLL
   `.srchash`**, so a pass stays tied to the artifact it tested and `STALE` is computable
   (the north-star `STALE` rule already works this way for mods).
5. **Reuse existing gates instead of new ones**: GREEN means what `modcheck status` already says;
   the validity floors (`modcheck floor`) already refuse a run with an uncovered toggle or
   must-show line, so `implemented` should refuse the same uncovered-floor condition for L0.
6. **Waivers and honesty**: a level can be waived only by an OWNER event naming the criterion.
   `UNMEASURED` is never a pass at any level.

## Open for the owner

See the question cards that accompanied this addendum (start point, level tags, acceptance
ownership, how to treat the ~115 already-built items).

## Owner decisions, 2026-10-06 (question card; the typed text is his, the clicks are ours)

- **Build order:** *"In order, 1, 2, 3, 4"* — (1) git check before `next` offers work, (2) the `built` state, (3) expiring claims, (4) sort the existing board.
- **More states than `built`?** He asked: *"Are we not adding any other states besides built, like something about validated to some level?"* — open; see the answer given in the session (a `validated` state with the level reached recorded on the item).
- **Levels:** decision taken by question card — tag every criterion with its level.
- **Who owns acceptance:** *"Foundry is supposed to own automated processes. Bench is about human interaction, design work, and emergency response."* — FOUNDRY owns acceptance sittings (L0-GREEN-FULL, L3 evaluation); BENCH is only the L4 human-facing and design seat.
- **The ~115 look-built items:** decision taken by question card — import as `built` after checking source.
