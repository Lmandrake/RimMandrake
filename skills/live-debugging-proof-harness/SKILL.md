---
name: live-debugging-proof-harness
description: Write, run and read a LIVE proof of a RimWorld mod through the bridge — proof_all.py, proof_hose.py, a northstar/ runner, validation_v2.py, a mod's validation.py, validation_core.py (LogTap, log_revive, prepare_site, clear_huge_plants) — and turn each run into found mod bugs instead of harness ceremony. Use whenever a proof or validation run is about to start, is failing, or has just finished; when a row reads PASS, FAIL or UNMEASURED and you must decide what it is worth; when a log-budget row, a perf row or a timing window is involved; when a long proof on the owner's full mod list keeps failing on its own harness or two proof runs disagree; when staging test sites, pre-port save fixtures or mid-job saves; when classifying a finding as MOD, SITE or HARNESS; and before recording any run with modcheck. Also use before a long tick advance or clock jump on a test map, and when a colony died, a threat landed or the game dropped to menu mid-run. Also use when an instrument might have gone blind (Verse.Log cap, bridge journal ring, stale Player.log, wrong tier) and a clean result looks too good.
---

# Live debugging proof harness

A live proof is a script that drives the running game through the bridge, stages
sites, reads state back, and writes one result JSON of rows. This skill is how to
build one that cannot lie to you, and how to spend a run so it finds **mod bugs**.

**The problem this skill exists to fix.** The 2026-10-11 overnight validation of
GimmeSomeSlack and FlowWorks produced 12 distinct live findings. **One** was a mod
bug (the hose perf defect, fixed, 6x faster). The other eleven were harness, site or
instrument faults. The owner called that validation "mostly ceremony". Two of those
faults were worse than wasted time: the Verse.Log cap and the 1,000-entry journal
ring meant **every earlier full-list log-budget PASS had been partly blind**. A
harness that reads PASS when it could not see is worse than no harness.

So the job has two halves, and you owe both:

1. **Make the instrument honest.** It reports UNMEASURED whenever it could not ask.
2. **Point it at the mod.** Spend the run on the places where the mod can actually be
   wrong, and write down what each run taught you in the mod's functional script.

## When this skill, when another

| you are… | use |
|---|---|
| writing, running or reading a proof / validation script, or classifying its rows | **this skill** |
| needing *a* map, a quicktest, or deciding bridge vs quicktest vs cold load | `rimworld-debug-testing` |
| staging a scene for a human to LOOK at, or taking review screenshots | `rimworld-live-review` |
| calling a bridge tool and it did nothing, or you need its exact params | `rimbridge` and `skills/rimbridge/references/traps.md` |
| adding a new `[Tool]` to JawaBench | `rimbridge-companion` |
| launching, swapping mod lists, reading the first exception at load | `rimworld-load-round`, `rimworld-start-prep` |
| the debugging *process* itself: the first-script contract, the ladder, GPT consults | `design/RimMandrake/debug_process.md` (binding; this skill is its live-run half) |

## The anatomy of a proof

The worked examples are `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py`
(105 rows) and `src/RimMandrake/FlowWorks/northstar/proof_hose.py` (66 rows). Their
shared harness is `src/RimMandrake/Utils/validation_core.py`. Copy their shape, and
reuse `validation_core` rather than writing a third harness.

```
0. offline gate (WSL python3)  selftests, C# SelfTest, the scene catalog -> JSON; any red refuses to go live
1. preflight                   fresh map; TIER TRUTH (len(env.running)); assembly identity; log_revive; tap_start;
                               control-noise save/load; probes answer; site pinned (weather, noon, incidents cleared)
2. blocks                      each one: re-calm the map -> clear huge plants -> prepare_site -> READ BACK -> act ->
                               wait on the precondition -> read state -> row
3. save / load                 one save (stat-diff the Saves folder) + one load; census before == census after
4. Z log budget                tap.lost == 0 and the sentinel is alive, or the row is UNMEASURED
5. result JSON                 mode "live" + certifiable; "partial" (--only) is refused by modcheck record
```

Run bridge-side under `python.exe` from the repo root, piping through `tr -d '\r'`.
The offline gate runs under WSL `python3`. WSL cannot reach the bridge.

Read `references/run-checklists.md` before every full-list run. It holds the
run-start and run-end checklists line by line.

## Row semantics: PASS, FAIL, UNMEASURED

Every row has a **status** and a **class**.

| status | means | never means |
|---|---|---|
| **PASS** | the check asked the game, got an answer, and the answer met the bar | "nothing went wrong" |
| **FAIL** | it asked, got an answer, and the answer missed the bar | "the call errored" |
| **UNMEASURED** | it **could not ask**: the site never got clear, the precondition never held, the journal lost entries, the sentinel died, a tool refused | a soft pass |

🔴 **"Could not ask" is UNMEASURED, never PASS.** This covers a failed bridge call, a
`success: false`, a tool that is missing, a site that read back blocked, a dead log, a
`lost > 0` tap, and fewer than the free colonists the block needs. Read the tool's own
`success` / `foundCount` / `notFound` fields. Never substring a payload. An
UNMEASURED row is not green. `debug_process.md` §6a: "UNMEASURED is not green".

| class | the defect is in… | what fixes it |
|---|---|---|
| **MOD** | the mod's code, defs or settings | the mod |
| **SITE** | the staged scene (terrain, giants, fog, pawns, geometry the mod rightly refuses) | the staging |
| **HARNESS** | the script, the bridge, the instrument, the window it waits | the script |

🔴 **A row that ran after the colony died or the game dropped to the main menu is
HARNESS/SITE and not counted**, whatever it reads; a map with no free colonist voids every
row that waits on a job. Pass 7 (2026-10-13): 17 "FAIL"s after a menu drop and every row
after a starvation were re-run, not scored.

A harness or site row in a shared session is written **only when it is not PASS**.
A green one becomes a site note (`validation_core.SHARED`).

⛔ **Never hand-edit a result JSON** to flip a row, not even to test how modcheck reads
a status. Fix the harness so it emits the right status and rerun. A result that has
been edited is deleted and rerun before anything is recorded.

## Sites, clearing, calm

The owner's full list will not leave a map alone. Each block starts by making its
site independent of the map, then **reads it back**:

- **Re-calm before every block**, not once per run: wild animals respawn after a
  one-off non-colonist sweep (a predator downed two colonists mid-run), and map-gen
  insect hives throw their own NREs. Draft every colonist the block is not using,
  because idle colonists wander into sites fast.
- **`clear_huge_plants` before every block** on an `RM_TheRot` map. Huge Things
  re-plans a giant's trunk blockers whenever they vanish while the plant stands, so a
  giant *outside* the rect re-blocks a site you just cleared. This happened on
  2026-10-11: a map with 5,000+ blocker cells, and style_hose R1–R6 FAILed with
  "Space already occupied".
- **`prepare_site` reads back.** A roof, rock, plant or ruin left in the rect is
  `UNMEASURED/SITE`, never a mod FAIL. Fog is cleared by a colonist's sight
  (`reveal`), not by `set_fog` alone.
- **Sites must be disjoint**, with margin for the mod's real geometry. For a hose
  this is the ~4.4-cell straight lead-out. Aim at the target's real footprint cell.

Detail, map culling and the fixture recipes: `references/sites-and-timing.md`.

## Timing windows: wait on the precondition, then start the clock

A flat tick window measures whatever happened to be slowest, and that is usually
not your mechanism.

- **Read the window from the design's own contract**, half by half. For example:
  discovery ≤ 60 ticks, then transfer within one 250-tick pump cycle *after
  discovery*. A flat 260 ticks from the lay was shorter than the contract itself.
  Each half was stricter than the old window, not looser.
- **Wait for the precondition, record how long it took, then start the clock.** On
  the full list a freshly built powered consumer reads `PowerOn=false` for ~100–170
  ticks. Vanilla's power net switches it on later, not at spawn. A cycle timed from
  the build measures that gap, so the row records `pumpPoweredAfterTicks`.
- **Bridge time is ticks, and a step is not the step you asked for.** See
  `skills/rimbridge/references/traps.md` for tick-keyed caches, overshoot and load races.

## Time advances and disturbances

- **A long-duration property is compressed, or decomposed and INFERRED — never chased for
  hours** (owner, 2026-10-13). Shorten its timing constants to watch it in minutes, then restore
  and read back the shipped value; if that cannot reach it, verify the components and record the
  whole as INFERRED. *"we should not waste dozens of hours frantically testing for a single
  very-hard-to-demonstrate property of an otherwise checked out mod."* Full text:
  `design/RimMandrake/debug_process.md` § "Long-duration properties".

- **Avoid long runs of game time.** Owner, 2026-10-13: *"long runs are possible but risky:
  they require more time, more monitoring, and fewer assumptions to succeed. Avoid them when
  possible unless it's a clear win for time efficiency compared to an alternative."* Pass 7's
  120k–280k-tick waits starved the whole unfed colony. Never warp the clock on a populated
  map; set the season before mapgen. Mechanics: `skills/rimbridge/references/silent-failures.md`.
- **Before and after every advance, read** free colonists alive and fed, and open letters
  (death, `GameEnded`). A dead colony ends the counted part of the run.
- **Verdicts when something disturbs a row** are the owner's rules in `debug_process.md`
  § "Test disturbances": corrected anomaly with no damage may PASS; damage to the test →
  restart the row, never FAIL; **every** threat → logged plus a test-environment item;
  protected colonists only in rows labelled not about health/needs/damage/death.
- **Watch the run, not just its result.** The owner expects a live pass to be monitored
  (e.g. a `Monitor` tailing `D:\Luke\dev\_rmscratch\bridge_calls.jsonl` for `time_set_ticks`,
  `start_debug_game`, failures). What telemetry cannot see yet: `skills/telemetry/references/traps.md`.
- **When the owner says something happened in the game, relay it to whoever drives the
  bridge at once, and name no cause until the log does.** Pass 7's deaths were first blamed
  on the clock jump; the death letters said Malnutrition.

## Log budgets: two ways to go blind, both reading as PASS

1. **Verse.Log stops ALL logging after 10,000 messages** (`StopLoggingAtMessageCount`;
   only `Log.Clear` resets it). A chatty mod reaches the cap within one session.
   Player.log and the bridge journal then both go silent while the game runs on.
   → `validation_core.log_revive(B)` at run start, and `log_alive(B)` (a sentinel
   warning read back) at the budget row.
2. **RimBridge's journal is a ring of the last 1,000 entries of every level.** An
   intimacy mod writes ~0.3 info lines/tick, so an end-of-run `list_logs` sees only
   the last ~3,400 ticks. → `validation_core.tap_start(B)`. The tap is polled after
   every tick step and load, and it counts the entries lost between polls.

**A budget with `lost > 0` or a dead sentinel is UNMEASURED.** Charge an error to the
mod only against a same-list control. Detail, the control-noise method and the known
full-list noise: `references/log-budgets.md`.

## Perf readings: time the production function, live

A perf selftest that times a **modelled** cost cannot see the real one. The hose
port's offline perf row passed at 0.001 ms/tick while live it was 0.152 ms/tick, 3x
the budget. A per-tick cache was being rebuilt once per laid reel, because each reel
checked on its own staggered tick. Measure live with `jawa/map_comp_timing` on a map
at least as big as the budget's scenario. Pair it with a work counter on the real
inner call and with a can-fail. Detail: `references/perf.md`.

## Pre-port save fixtures

When a port moves a class, job or def between mods, save the **old** build mid-job
before the port deploys, and prove the new build loads it with the job still
running. For example: `RM_PREPORT_HOSE_MIDCARRY_20261011.rws` and `…MIDRETRACT…`
were loaded by `proof_hose.py --preport-save` and the job was still running 60 ticks
after load. Back up the keepers first and stat-diff the Saves folder after: exactly
the new files, 0 changed. Slow the carrier if the job would finish before your read.
On the full list "Out of Combat ReBoost" walks a colonist at ~2 ticks/cell, and
BadBack + Frail brings that to ~8. Recipe: `references/sites-and-timing.md`.

## After the run: classify, then go hunting for the mod bug

1. **Classify every non-PASS row** as MOD / SITE / HARNESS, with the evidence that
   decided it. Use "presumed, unproven" when you did not trace it. Do not quietly
   fold an untraced row into the nearest proven one.
2. **Fix harness and site faults as a CLASS, not one at a time.** A full-list run
   surfaces 2–4 new harness assumptions per ~15-minute run. Before the second run,
   one fresh-context read-only audit of the whole fragility class found 8 at once.
   The class is camera, ticks, idle pawns, site margins, fog, save timing, log
   budget and tier.
3. **Then deliberately aim at the mod.** A green proof after harness fixes is not
   the end of the job. Ask where the mod could still be wrong that no row reads:
   - **leads**: for example, `Building_LiquidPump.TryDraw` loses the level if
     `TryAddLiquid` refuses, and nothing asserts it cannot happen;
   - **rows that have never been red**: a check never seen red proves nothing;
   - **conservation and accounting**: units in == units out;
   - **perf on the real hot path**;
   - **upgrade paths**: old saves, imported settings flags;
   - **the mod on the full list**: a mod that has only ever run on its 15-mod tier
     carries tier assumptions.
   Each answer becomes a row that **can go red**.
4. **Record what the run learned in the mod's functional script** (`debug_process.md`
   §0.4, §2.4). A check that goes red for the reported reason. A guard for each
   informative dead theory. `RULED OUT: <theory> — <the check that killed it>` in
   the walk's `## anti-guessing notes`. Nothing that found a bug lives only in a
   Transient log.
5. **The commit names the class** (MOD / SITE / HARNESS) and the row id. A
   prior-pass-now-fail is a STOP: that regression is the finding.

How to tell the classes apart, the 2026-10-11 tally and the modcheck/walk traps:
`references/classifying-and-learning.md`.

## Before you trust any run

- **Tier truth.** A proof labelled with a tier can run on a different list. On
  2026-10-10 a "gimmesomeslack tier" run was really on 550 mods. Read
  `len(env.running)` and compare that number between runs, never the labels.
- **Assembly identity.** Run from a clone or `git archive` export whose DLL is
  byte-identical to the deployed copy. A bench clone with an older DLL aborted v2 at
  L2.
- **Staleness.** A recorded proof goes STALE when any mod-folder file changes, except
  `validation.py`, `human_review.py` and `northstar/`. Finish every mod-folder edit
  before the run you will record.
- **Owner rulings.** An owner ruling that *refuses* a behaviour invalidates every
  live site built before it. Re-check scene geometry against the ruling. The offline
  model stays green through that change, because it never modelled the refusal.

## Flyers

🔴 **Never live-test a flyer's flight without the owner present.** He has said it three
times (repo `CLAUDE.md`, "NEVER live-test a flyer's flight"). A proof row about flight
reads `Pawn_FlightTracker` state through a debug `[Tool]`. A visual flight bar waits
for a joint session. Never file a live-flight bar that only an unattended screenshot
hunt could close.

## Writing the plan before the run

Every live row owes three lines written **before** it runs: PROVE (the call), EXPECT
(a number or string), and LIES (how this row could pass falsely). It also owes a
closing bar. The validation plan and threshold discipline:
`references/validation-plan-and-thresholds.md`. For handing a check to someone else,
see `skills/rimworld-modding/references/validation-plan.md`.

## Reference files

| file | read when |
|---|---|
| `references/run-checklists.md` | before every full-list run (start checklist) and before reporting one (end checklist) |
| `references/log-budgets.md` | any log-budget row, a "0 errors" that looks too clean, charging an error to a mod |
| `references/sites-and-timing.md` | staging sites, giants, fog, calm, map culling, tick windows, pre-port / mid-job save fixtures |
| `references/perf.md` | any perf row or budget |
| `references/classifying-and-learning.md` | after a run: MOD/SITE/HARNESS, fragility audits, recording into the script, modcheck/walk traps |
| `references/validation-plan-and-thresholds.md` | writing the plan and the closing bar for a check |
