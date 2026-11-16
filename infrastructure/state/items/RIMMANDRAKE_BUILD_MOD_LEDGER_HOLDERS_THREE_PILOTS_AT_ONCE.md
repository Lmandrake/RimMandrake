# RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE

Build what the owner chose on 2026-11-15 (~9:45 PM PST) from `design/specs/2026-11-15-holder-pipeline-fusion.md`.

## What the card said (his answers, verbatim; the whole card is stamped on RIMMANDRAKE_DESIGN_HOLDER_PIPELINE_FUSION_CHECKLIST_NOT_HANDOFF)

1. Which do we build? → **"Resumed session per mod (Recommended)"**: "Why: keeps context as the mod progresses, unattended, which is what you asked for. The dispatcher resumes one long session per mod at every stage; built as the packet version first, falls back to it. Cost: a warm session can cling to a refuted theory; may cost more per stage; resume is untested in our detached launcher."
2. Who fixes what a blind judge finds? → his words: **"Anyone finding anything documents precisely how they would fix it but it goes back to the holder fully informed."** (replaces the 11-13 "FIX THEM RIGHT THERE" rule)
3. Which mod is the pilot? → his words: **"Do all three side by side as a deeper test. When one reveals a needed fix to the system all three benefit."** (Gimme Some Slack, FlowWorks, Explosive Knockback; overrides the spec's two-mods cap)
4. Context ceiling? → his words: **"Try 400k first."**

His additions the same evening (~9:40 PM PST): "I think the key to closing many tickets for the same mod might be keeping that context and working them all together. I think a mod holder should be handing off to its next version with context of what has happened before. Even into judging phases. I think this might be very important. Almost like a conductor custom following along. I think we're on to something."

## spec

`design/specs/2026-11-15-holder-pipeline-fusion.md` (Option B, built as A first), amended by the answers above:
- a finder (judge, checker, anyone) writes the finding AND the precise fix it would make; the holder applies it;
- the holder works all of its mod's open tickets together in one context;
- the holder carries across Design Versions with its context (a handoff, not a new stranger);
- the holder stays alive and following through the judging phases, like a per-mod Conductor; judges stay blind;
- holder context ceiling 400k (rotate at the next natural boundary after it), one setting, tunable;
- three pilot mods side by side; a system fix found on one benefits all three.

Order of work: (1) amend the spec with these decisions and write the build plan to `design/plans/`; (2) `modledger` (append, lint, show, packet, views) on rimflow's shard code, tests first; (3) backfill + shadow views for the three mods; (4) cutover; (5) packet-started runs; (6) resumed holder sessions with the kill-and-resume test. Steps 3 onward are filed as their own items by the builder when step 2 lands.

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only modledger` — written first, watched failing on the base commit (no modledger exists there), then passing. It must show the lint refusing: a hand-edited view, a shard that is not a strict extension of its published form, a HOLDER event with a stale lease token, a holder writing into a JUDGE or OWNER shard; and cover empty ledger, single shard, many shards, duplicate (idempotent) append, superseded event, packet over budget.

## criteria

- the selftest above passes and is in the pipeline tests run at `./publish`;
- the packet for one real mod prints from a backfilled ledger under 15k tokens and names what it left out;
- the spec carries the four card answers and his additions; no line of it still says two mods, 600k, or "judge fixes";
- live/unrun parts are named UNRUN with their command.
