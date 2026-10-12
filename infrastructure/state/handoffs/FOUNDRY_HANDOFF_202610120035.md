# FOUNDRY_HANDOFF_202610120035 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610111255`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
A `needs: owner` flag must mean he owes something OTHER than an already-given ruling; 15 stale flags were cleared this session (list: `Transient/foundry_owner_cards_2026-10-11.md`). Check ruling history before leaving or setting `needs: owner`.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing pending: all three cards were answered (relics: we propose five Star Wars items and he approves the list; health recorder: build the other 8 then judge all 20; donor fauna: convert the cheap SW pack first). Ten remaining `needs: owner` items are only looks/listens or numbers reviews.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS` — owner chose "we propose, you approve"; NEXT: write five Star Wars replacement relics (one per VWE relic precept) to a file for his approval
- `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP` — owner chose build all 8 then judge 20; NEXT: build the 8 designed metrics per `design/RimMandrake/game_health_record.md`
- `DONOR_DEFS_PORT_TO_OURS_1` — owner chose cheap pack first; NEXT: port the 160-row Star Wars animal pack defs to RM_ wholesale, then the 102-row pack

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
None new this session.

## Commits

```
7a3d9ffbf Owner cards 2026-10-11: relics, health recorder, donor fauna order ruled; needs:owner cleared on 15 already-ruled/agent-work items
e2ed966e8 Rulings: pit exposure ±8 C, prisoner resistance only while hurting
1157638ac Transient and conversation record sync: art-review matrices, biome_ffar images, modcheck surprises
e0e2e813d Design: pit exposure to the elements via vanilla comfort-range narrowing (replaces night-capable Heatstroke giver)
91923ffdd FOUNDRY handoff 2026-10-12: Pyrelands sheet enacted, three offline biome builds, FW/GSS sitting partial
f0bfc9174 Rulings: rigid pipe confirmed; pit exposure to the elements via vanilla; wet-cell doors; per-liquid wakes
eac269241 Code review: mark 135 FlowWorks files clean after full-file review
a867d9bb6 selftest_hose_port P9: widen the credit-site check from 11 to the 19 sites TransferChecks covers
a98680078 FlowWorks code review: fixes from the full-file review of the 169 dirty files
3402e9ebc FlowWorks step 4 live on the golden site: 100 PASS / 11 FAIL / 36 UNMEASURED; PIT_FALL_ONLY_FORCED done, CHECKOUT_SCOPE A2 partial, 5 findings filed
58a81b3ca Move owner walk scene script out of validation_walks (not a mod walk; walklint red)
2fe28671e Ledger: liquid network L1-L11 and the hose-ruling item implemented (live bars owed)
a341da28f FlowWorks L11: rev-2 perf fixture (ports, jobs, pouring pump) within 0.05 ms mean / 1 ms worst; probe counters
5ce7f4aae FlowWorks L10: pipe adapter modes Send/Take/Shut; new builds start Shut, failures shut the adapter
e329b7203 FlowWorks L9: liquid theft priced like power theft (2 goodwill/day once seen within 12 cells)
8ec0dbef2 FlowWorks L8: hoses hold a little of what they carry and spill it out of the open end when they stop
5b9a70435 FlowWorks L7: Outflow ends pour into channels or spill as cleanable filth; Dump tanks drain slowly with no pump
fe13508b7 FlowWorks L6: the pump as world mover; Intake ends as sources, Outflow ends before tanks (tankless lake->canal), pour drains Dump tanks only
9163cd3d7 FlowWorks L5: hose free-end roles Capped/Intake/Outflow on the reel (rmFreeEndRole), ports of the hose's network
25d272ff9 FlowWorks L4: tank jobs Store/Fill/Empty/Dump with a per-cycle settle; the equalising tank feed is deleted
... 142 more: git log --oneline ed774a8ec..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? conversations/2026-10-12-0024-db9d8bc8.md   this session's conversation record
```

