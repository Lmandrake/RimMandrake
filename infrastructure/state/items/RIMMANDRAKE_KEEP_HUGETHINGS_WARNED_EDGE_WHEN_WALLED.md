# RIMMANDRAKE_KEEP_HUGETHINGS_WARNED_EDGE_WHEN_WALLED

## spec
At arrival keep the warned side and resolve barriers with ordinary titan wall/rock mechanics. Remove silent opposite-edge rerouting and generic one-cell reachability cancellation when the creature can break the obstacle. A barrier of sufficiently thick rock may hold. Do not weaken thick-roof/rock or curated protection rules.

Authority: design/RimMandrake/hugethings_codex_2026-11-09/ANSWERS_OWNER.md (2026-11-11).

## verify
L2: Build a barrier after the warning; real titan enters on the warned side, approaches/strikes traversable walls and departs; thick-rock control holds; save/load and disabled control preserve behavior.

## criteria
- A1 L0: implementation and current specifications agree with the cited owner answer; focused offline checks pass.
- A2 L2: Build a barrier after the warning; real titan enters on the warned side, approaches/strikes traversable walls and departs; thick-rock control holds; save/load and disabled control preserve behavior.



New mechanism not yet observed: At arrival keep the warned side and resolve barriers with ordinary titan wall/rock mechanics. Remove silent opposite-edge rerouting and generic one-cell reachability cancellation when the creature can break the obstacle. A barrier of sufficiently thick rock may hold. Do not weaken thick-roof/rock or curated protection rules.

## Sweep 2026-11-22 (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`)

**Version: current**, by the obvious reading: his answer 6 (2026-11-11) is about the titan's crossing, the first
version's bar `titan_crossing_destroys`; a walled-off titan that silently reroutes to the far edge is an experience he
rejected. The Conductor may move it to the next version. The old NEXT line here named Whittle, a retired era; it is
removed.

Still true in code on 2026-11-22: `Titanic/Events/TitanPassage.cs` `Arrive()` keeps the warned edge only while it "reaches
the far edge; otherwise a fresh route is found" (`if (!routeOk) routeOk = TitanPassageUtility.TryFindStartAndEnd(...)`),
and fades the event when no route is found.

Merged in: GPT deep review 2026-11-10 P2 #10 (`design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md`; was in
`RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND`), same file and same route logic: the passage accepts a one-cell route
that a T2/T3 footprint cannot traverse (`TitanPassage.cs:130`, `:204`, `:213`); tests assert its lord, not its traversal
and departure. With this fix, the route is judged for the titan's footprint and its own wall/rock rules, not for a
one-cell walker.

His words (2026-11-11, by card): "Blocked way -> Same side, it breaks through".

NEXT: remove the opposite-edge fallback in `Arrive()`, judge the route by the titan's footprint and clearing rules, then
prove A2 live on a free game (not ArchBig).

## Acceptance test

Offline (watched RED on 2026-11-22, exit 1):
`! grep -q "if (!routeOk) routeOk = TitanPassageUtility.TryFindStartAndEnd" src/RimMandrake/HugeThings/Source/Titanic/Events/TitanPassage.cs`.
It is a shape check only. The deciding row is A2 live: a barrier built after the warning; the titan enters on the warned
side and breaks traversable walls; the thick-rock control holds. Expected pass count: 1 offline command plus A2.
