# Our setup and pain points (RimMandrake, as of 2026-10-22)

## What we run
- **Product:** a RimWorld 1.6 total-conversion family of mods (C#/Harmony + XML defs + art), loosely specified game
  design held by one owner (Lukas), who decides by question cards and phone art reviews. (`CLAUDE.md`, `infrastructure/agents/BENCH.md`)
- **Two Claude Code seats** in separate ext4 clones: **BENCH** (Opus, sits with the owner, orchestrates helpers) and
  **FOUNDRY** (Sonnet, autonomous queue: `rimflow next --seat FOUNDRY`, 45-min leases). Helpers are Claude Code
  subagents (cap 3-5 the owner sets per day). Worktrees are OFF by owner ruling (2026-10-02); helpers share one clone.
  (`infrastructure/agents/CHARTER.md`, `FOUNDRY.md`, `Agent_Policy.md`)
- **rimflow:** an in-repo Python CLI over an append-only, per-seat-sharded JSONL ledger; items are named
  `SUBJECT_INTENT_TWIST`, move proposed -> doing -> built -> validated -> done with level-tagged acceptance criteria
  (L0 offline ... L2 behaviour gauntlet ... L4 owner). 528 live item prose files today (MEASURED, `ls infrastructure/state/items | wc -l`).
  It already has leases, a bridge lock, reconcile, provenance flags for owner authority. (`skills/using-rimflow/SKILL.md`)
- **Live testing:** RimWorld runs on **Windows**; agents run in **WSL2**. They drive it through the **RimBridgeServer
  GABP bridge + our JawaBench companion DLL** (spawn, edit pawns, weather, raids, screenshots). **One live driver
  at a time** (`infrastructure/state/BRIDGE`). Cold load ~15 min full list / ~22 s on a 13-mod minimal list; a
  quicktest map ~90 s. Each mod has northstar proof scripts (`proof_all.py`, `*_proof.py`) emitting PASS/FAIL/UNMEASURED
  rows classified MOD/SITE/HARNESS. The bridge's signature hazard: 30+ engine calls that report success and change
  nothing (`skills/rimbridge/references/silent-failures.md`).

## What a real day looks like (2026-10-22, `Transient/pile_2026-10-22/day_plan.md`, `belt.md`)
- Order: advance FlowWorks "to the most ready state possible today without human interaction", owner reachable only for
  cards + phone art. Starting state: ~47 FlowWorks items `built` (never proven live), ~20 validated, ~18 doing, ~53 proposed.
- The live belt (one bridge driver) ran 08:48-14:44: ~20 proof scripts, ~548 proof rows passed (seat's count),
  4 MOD bugs filed by 10:11 and 8 by day's end (seat's count), many HARNESS fixes made mid-run (plant re-seeding,
  raid staging, mass-normalised ratios).
- **Pain points, with evidence:**
  1. **Serial live resource.** One game, one driver; every DLL redeploy = game down + Steam relaunch (09:37, 09:57 ...).
     Fixers wait on the belt and the belt waits on fixers ("Waiting on fixers for re-prove", belt.md NEXT).
  2. **Push conflicts in a shared clone.** `./publish REFUSED` twice (08:58, 09:16): a helper's uncommitted
     `RM_SheetMath.cs` vs origin; 11 local commits stranded; a plumbing replay was refused by the pre-push hook.
  3. **Orchestrator idle / latency.** Run-log gaps of 16-28 min (12:36->12:52, 13:13->13:41, MEASURED from belt.md
     timestamps); the seat reports helper slots idle for hours while the orchestrator waited (seat's report, not re-measured).
  4. **Harness churn vs mod bugs.** A large share of FAILs were HARNESS/SITE (raid staging, plant regrowth, wrong
     construction priority -> one wrongly filed bug DROPPED). Classification costs judgment the owner can't supply live.
  5. **Owner bandwidth is the binding constraint** ("I simply can't spend enough time with you"). Design is loose;
     decisions arrive by card/phone in batches; L4 (owner look) criteria pile up for the evening walk.
  6. **Context loss on long days.** Seats hand off at ~50% context; the belt itself is the memory.
