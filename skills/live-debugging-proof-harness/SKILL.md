---
name: live-debugging-proof-harness
description: Write, run and read a LIVE proof of a RimWorld mod through the bridge — proof_all.py, proof_hose.py, a northstar/ runner, validation_v2.py, a mod's validation.py, validation_core.py (LogTap, log_revive, prepare_site, clear_huge_plants) — and turn each run into found mod bugs instead of harness ceremony. Use whenever a proof or validation run is about to start, is failing, or has just finished; when a row reads PASS, FAIL or UNMEASURED and you must decide what it is worth; when a log-budget row, a perf row or a timing window is involved; when a long proof on the owner's full mod list keeps failing on its own harness or two proof runs disagree; when staging test sites, pre-port save fixtures or mid-job saves; when classifying a finding as MOD, SITE or HARNESS; and before recording any run with modcheck. Also use before a long tick advance or clock jump on a test map, and when a colony died, a threat landed or the game dropped to menu mid-run. Also use when an instrument might have gone blind (Verse.Log cap, bridge journal ring, stale Player.log, wrong tier) and a clean result looks too good.
---

# Live debugging proof harness

A live proof is a script. The script does four things:

- it drives the running game through the bridge;
- it stages sites (a site is the cleared plot of map where a check runs);
- it reads the state of the game back;
- it writes one result JSON of rows (a row is the recorded result of one check).

This skill tells you how to build a proof that cannot lie to you. This skill also tells you how to spend a run so that
the run finds **mod bugs**.

**The problem this skill exists to fix.**

- The overnight validation of GimmeSomeSlack and FlowWorks on 2026-10-11 produced 12 distinct live findings.
- **One** finding was a mod bug: the hose perf defect. The defect is fixed, and the code is 6x faster.
- The other eleven findings were faults of the harness, the site or the instrument.
- The owner called that validation "mostly ceremony".
- Two of those faults were worse than wasted time: the Verse.Log cap and the 1,000-entry journal ring (§Log budgets).
- Because of these two faults, **every earlier full-list log-budget PASS had been partly blind**.
- A harness that reads PASS when it could not see is worse than no harness.

"The full list" in this file is the owner's full mod list.

So the job has two halves, and you owe both:

1. **Make the instrument honest.** The instrument reports UNMEASURED whenever it could not ask.
2. **Point the instrument at the mod.** Spend the run on the places where the mod can actually be wrong. Write what
   each run taught you into the mod's functional script, `validation.py`.

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
| deciding whether a live proof is the right test at all, or how much to run | `design/RimMandrake/testing_policy_2026-10-28.md` §2.8 (live proofs: helps, hurts, when it was a mistake) and §4 (maturity × risk table); tunables in `src/RimMandrake/rimflow/testing_policy.json` |

`rimworld-debug-testing` and `rimworld-start-prep` are not registered. Read them by path:
`skills/rimworld-debug-testing/SKILL.md` and `skills/rimworld-start-prep/SKILL.md`.

## The anatomy of a proof

The worked examples are these two scripts (row counts as of 2026-10-11):

- `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` (105 rows);
- `src/RimMandrake/FlowWorks/northstar/proof_hose.py` (66 rows).

Their shared harness is `src/RimMandrake/Utils/validation_core.py`. Copy the shape of the two scripts. Reuse
`validation_core`. Do not write a third harness.

```
0. offline gate (WSL python3)  selftests, C# SelfTest, the scene catalog -> JSON; any red refuses to go live
1. preflight                   fresh map; TIER TRUTH (len(env.running)); assembly identity; log_revive; tap_start;
                               control-noise save/load; probes answer; site pinned (weather, noon, incidents cleared)
2. blocks                      each one: re-calm the map -> clear huge plants -> prepare_site -> READ BACK -> act ->
                               wait on the precondition -> read state -> row
3. save / load                 one save (stat-diff the Saves folder) + one load; census before == census after
                               two causes to tell apart? validation_core.saveload_triplet (live/load/reload arms)
4. Z log budget                tap.lost == 0 and the sentinel is alive, or the row is UNMEASURED
5. result JSON                 mode "live" + certifiable; "partial" (--only) is refused by modcheck record
```

Terms in this block:

- A block is one group of rows that uses one site.
- The tier is the mod list that a run declares.
- §Before you trust any run explains tier truth and assembly identity.
- §Log budgets explains `log_revive`, `tap_start`, the tap and the sentinel.
- The control-noise save/load records the errors that the list makes before any scene exists (`references/log-budgets.md`).
- Z is the short name of the log-budget row (row id `Z_log_budget`).

Run the bridge side under `python.exe` from the repo root. Pipe the output through `tr -d '\r'`. Run the offline gate
under WSL `python3`. WSL cannot reach the bridge.

🔴 **Run TARGETED first** (owner 2026-10-25).

- The command is `modcheck run <Mod> --item <ITEM_ID>`, or the same command with `--chains a,b` / `--rows r1,r2`.
- The site hold (modcheck's calming of the map before each chain) still runs in a targeted run.
- A chain is a named group of checks in the mod's `validation.py` (`@suite.chain`). The record of a targeted run says
  TARGETED and names its chains.
- `--full` is the scheduled sweep. Run it at most daily.
- Add `--preview` first. `--preview` prints the per-chain plan and exits.
- `--rows` runs each chain up to the chain's last named row. The other rows record NOT_RUN by design.
- On a `--rows` job, read NOT_RUN as 'not asked for'. NOT_RUN is not a failed run.

Read `references/run-checklists.md` before every full-list run. That file holds the run-start and run-end checklists
line by line.

More traps for this section: [references/traps.md](references/traps.md) § The anatomy of a proof.

## Row semantics: PASS, FAIL, UNMEASURED

Every row has a **status** and a **class**.

🔴 **`modcheck record` knows six statuses:** PASS, SKIP, UNCOVERED and UNBUILT are OK. FAIL and UNMEASURED are not OK.
Any other word (`RECORD`, `INFO`, `MEASURED`) reads RED. `modcheck record` prints each such word with its row ids
(`record.KNOWN_ROWS`).

| status | means | never means |
|---|---|---|
| **PASS** | the check asked the game, got an answer, and the answer met the bar | "nothing went wrong" |
| **FAIL** | the check asked, got an answer, and the answer missed the bar | "the call errored" |
| **UNMEASURED** | the check **could not ask**: the site never got clear, the precondition never held, the journal lost entries, the sentinel died, a tool refused | a soft pass |

🔴 **"Could not ask" is UNMEASURED, never PASS.** Each of these is "could not ask":

- a failed bridge call;
- a `success: false`;
- a tool that is missing;
- a site that read back blocked;
- a dead log;
- a `lost > 0` tap;
- fewer than the free colonists that the block needs.

Read the tool's own `success` / `foundCount` / `notFound` fields. Never search a payload for a substring. An
UNMEASURED row is not green. `debug_process.md` §6a says "UNMEASURED is not green".

| class | the defect is in… | what fixes it |
|---|---|---|
| **MOD** | the mod's code, defs or settings | the mod |
| **SITE** | the staged scene (terrain, giants, fog, pawns, geometry the mod rightly refuses) | the staging |
| **HARNESS** | the script, the bridge, the instrument, the window it waits | the script |

🔴 **A row that ran after the colony died or the game dropped to the main menu is HARNESS/SITE and not counted.**

- The rule holds whatever the row reads.
- A map with no free colonist voids every row that waits on a job.
- Example: Pass 7, the Pyrelands live pass 7 (2026-10-13). 17 "FAIL"s came after a menu drop. Those rows, and every row
  after a starvation, were run again, not scored.

A shared session is one session on one map (`validation_core.SHARED`). There, a harness or site row is written **only
when it is not PASS**. A green harness or site row becomes a site note.

⛔ **Never hand-edit a result JSON** to flip a row.

- Do not edit it even to test how modcheck reads a status.
- Fix the harness so that the harness emits the right status. Then run it again.
- Delete an edited result, and run the proof again before you record anything.

More traps for this section: [references/traps.md](references/traps.md) § Row semantics: PASS, FAIL, UNMEASURED.

## Sites, clearing, calm

The owner's full list will not leave a map alone. Each block starts by making its site independent of the map. Then the
block **reads the site back**:

- **Re-calm before every block**, not once per run.
  - Wild animals respawn after a one-off non-colonist sweep. A predator downed two colonists in the middle of a run.
  - Map-gen insect hives throw their own NREs (NullReferenceExceptions).
  - Draft every colonist that the block is not using, because idle colonists wander into sites fast.
- **`clear_huge_plants` before every block** on an `RM_TheRot` map.
  - The mod Huge Things plans a giant plant's trunk blockers again when they vanish while the plant stands.
  - So a giant *outside* the rect blocks again a site that you just cleared.
  - This happened on 2026-10-11, on a map with 5,000+ blocker cells. The block style_hose FAILed with "Space already occupied". Its
    rows R1–R6 are R1 (pick a hose look and place a reel) to R6 (pack up the reel and reinstall it).
- **`prepare_site` reads back.**
  - A roof, rock, plant or ruin left in the rect is `UNMEASURED/SITE`, never a mod FAIL.
  - A colonist's sight clears the fog (`reveal`). `set_fog` alone does not clear it.
- **Sites must be disjoint**, with a margin for the mod's real geometry.
  - For a hose, the margin is the ~4.4-cell straight lead-out.
  - Aim a hose at a real footprint cell of the target.
- **Water and sources: footprint plus 2 cells.**
  - First check the cells with `jawa/flowworks_excavation_rect` (`includeTerrain`) for `isSource` / water.
  - A pit beside river sources filled by gravity and spoiled its row.
  - A failed check exits UNMEASURED with a named reason.

Detail, map culling and the fixture recipes: `references/sites-and-timing.md`.

## Timing windows: wait on the precondition, then start the clock

A flat tick window measures whatever happened to be slowest. The slowest thing is usually not your mechanism.

- **Read the window from the design's own contract**, half by half.
  - Example: discovery ≤ 60 ticks, then transfer within one 250-tick pump cycle *after discovery*.
  - A flat 260 ticks from the lay was shorter than the contract itself.
  - Each half of the new window was stricter than the old window, not looser.
- **Wait for the precondition, record how long it took, then start the clock.**
  - On the full list, a freshly built powered consumer reads `PowerOn=false` for ~100–170 ticks.
  - Vanilla's power net switches the consumer on later, not at spawn.
  - A cycle timed from the build measures that gap. So the row records `pumpPoweredAfterTicks`.
- **Bridge time is ticks, and a step is not the step you asked for.**
  - For tick-keyed caches, overshoot and load races, see `skills/rimbridge/references/traps/lifecycle.md`.
- **Advance with `B.ticks(n)`, never with an advance-read-repeat loop.**
  - `B.ticks` goes through `clockgate.advance_chunk` to `jawa/safe_advance`, which runs many ticks per frame.
  - A raw `step_game_ticks` runs one tick per frame.
  - Every poll round trip costs ~53 ms.
  - Stop-on-condition (`B.until`) and sampling (`B.watch`) are PLANNED. Their Python half exists in `validation_core`.
    Their game half is not complete (measured 2026-11-23): `jawa/safe_advance` has no `until` parameter, and the watch tool
    does not exist. Do not use `B.until` or `B.watch` yet.
  - Today's rule and the item ids are in `references/lightspeed-authoring.md` §3.

## Time advances and disturbances

- **A long-duration property is compressed, or decomposed and INFERRED — never chased for hours** (owner, 2026-10-13).
  - Compress first: shorten the property's timing constants, and watch the property in minutes. Then restore the shipped
    value and read it back.
  - If compression cannot reach the property, verify the components. Record the whole as INFERRED.
  - *"we should not waste dozens of hours frantically testing for a single very-hard-to-demonstrate property of an
    otherwise checked out mod."*
  - Full text: `design/RimMandrake/debug_process.md` § "Long-duration properties".
- **Start no long runs of game time.**
  - Owner, 2026-10-13: *"Go back to building and testing things you can directly measure. No more long runs, ok?"*
  - Pass 7's 120k–280k-tick waits starved the whole unfed colony.
  - Never warp the clock on a populated map. Set the season before mapgen.
  - Mechanics: `skills/rimbridge/references/silent-failures.md`.
  - His earlier, weaker words of that day are in `design/RimMandrake/CLAUDE.history.md` § Long runs of game time.
- **Before and after every advance, read two things:** the free colonists (alive and fed), and the open letters (death,
  `GameEnded`). A dead colony ends the counted part of the run.
- **Verdicts when something disturbs a row** are the owner's rules in `debug_process.md` § "Test disturbances":
  - A corrected anomaly with no damage to the test may PASS.
  - After damage to the test, restart the row. Never score it FAIL.
  - Log **every** threat, and file a test-environment item for it.
  - Protect support colonists (they cannot die or starve) only in rows labelled as not about health, needs, damage or death.
- **Watch the run, not just its result.**
  - The owner expects an agent to monitor a live pass.
  - Example: a `Monitor` that tails `D:\ClaudeWork\rimmandrake\scratch\bridge_calls.jsonl` for `time_set_ticks`,
    `start_debug_game` and failures.
  - What telemetry cannot see yet: `skills/telemetry/references/traps.md`.
- **When the owner says that something happened in the game, relay it at once** to whoever drives the bridge.
  - Name no cause until the log names one.
  - Pass 7's deaths were first blamed on the clock jump. The death letters said Malnutrition.

## Log budgets: two ways to go blind, both reading as PASS

A log-budget row says that the session added no errors that name the mod. Two limits can blind the row:

1. **Verse.Log stops ALL logging after 10,000 messages** (`StopLoggingAtMessageCount`; only `Log.Clear` resets it).
   - A chatty mod reaches the cap within one session.
   - Player.log and the bridge journal then both go silent while the game runs on.
   - At run start, call `validation_core.log_revive(B)`.
   - At the budget row, call `log_alive(B)`. `log_alive` writes a sentinel (a marker warning) and reads the sentinel back.
2. **RimBridge's journal is a ring of the last 1,000 entries of every level.**
   - An intimacy mod writes ~0.3 info lines/tick. So an end-of-run `list_logs` sees only the last ~3,400 ticks.
   - At run start, call `validation_core.tap_start(B)`. That call starts the tap, a reader that keeps each warning and error.
   - The harness polls the tap after every tick step and load. The tap counts the entries lost between polls (`lost`).

**A budget with `lost > 0` or a dead sentinel is UNMEASURED.** Charge an error to the mod only against a same-list
control. The control is the errors that the same mod list makes before any scene exists. Detail, the control-noise method and the known
full-list noise: `references/log-budgets.md`.

## Perf readings: time the production function, live

A perf selftest that times a **modelled** cost cannot see the real cost.

- The hose port's offline perf row passed at 0.001 ms/tick. Live, the cost was 0.152 ms/tick, 3x the budget.
- The cause: each laid reel checked on its own staggered tick. So a per-tick cache was rebuilt once per laid reel.

Measure live with `jawa/map_comp_timing`, on a map at least as big as the budget's scenario. Pair the timing with a work
counter on the real inner call. Pair it also with a can-fail (a run of the old, slow shape that must go red). Detail:
`references/perf.md`.

## Pre-port save fixtures

A port can move a class, job or def between mods. Before such a port deploys, save the **old** build mid-job. Then prove
that the new build loads that save with the job still running.

- Example: `proof_hose.py --preport-save` loaded `RM_PREPORT_HOSE_MIDCARRY_20261011.rws` and `…MIDRETRACT…`. The job was
  still running 60 ticks after load.
- Back up the keepers (the saves that must not change) first.
- Stat-diff the Saves folder after: exactly the new files, 0 changed.
- If the job would finish before your read, slow the carrier. On the full list "Out of Combat ReBoost" walks a colonist
  at ~2 ticks/cell. The hediffs BadBack + Frail bring that to ~8.

Recipe: `references/sites-and-timing.md`.

More traps for this section: [references/traps.md](references/traps.md) § Pre-port save fixtures.

## After the run: classify, then go hunting for the mod bug

1. **Classify every non-PASS row** as MOD / SITE / HARNESS, with the evidence that decided it.
   - Use "presumed, unproven" for a row that you did not trace.
   - Do not quietly fold an untraced row into the nearest proven row.
2. **Fix harness and site faults as a CLASS, not one at a time.**
   - A full-list run surfaces 2–4 new harness assumptions per ~15-minute run.
   - Before the second run, do one fresh-context read-only audit of the whole fragility class. One such audit found 8 at once.
   - The class is camera, ticks, idle pawns, site margins, fog, save timing, log budget and tier.
3. **Then deliberately aim at the mod.** A green proof after harness fixes is not the end of the job. Ask where the mod
   could still be wrong that no row reads:
   - **leads** (a place in the code that can fail, with no check on it). An example, since fixed:
     `Building_LiquidPump.TryDraw` lost the level if `TryAddLiquid` refused, and nothing asserted that it could not happen;
   - **rows that have never been red**: a check never seen red proves nothing;
   - **conservation and accounting**: units in == units out;
   - **perf on the real hot path**;
   - **upgrade paths**: old saves, imported settings flags;
   - **the mod on the full list**: a mod that has only ever run on its 15-mod tier carries tier assumptions.

   Each answer becomes a row that **can go red**.
4. **Record what the run learned in the mod's functional script** (`debug_process.md` §0.4, §2.4):
   - a check that goes red for the reported reason;
   - a guard for each informative dead theory;
   - a line `RULED OUT: <theory> — <the check that killed it>` in the `## anti-guessing notes` of the mod's walk (its
     page under `design/validation_walks/`).

   Nothing that found a bug lives only in a Transient log.
5. **The commit names the class** (MOD / SITE / HARNESS) and the row id.
   - A prior-pass-now-fail is a STOP: that regression is the finding.
   - The exception: `git log --since=<last pass>` on the subsystem's source shows a RULED behaviour change. A RULED
     change is one that an owner ruling ordered.
   - Example: the liquid spill became `RM_Filth_WaterSpill`, so a row that counted only `RM_Filth_LiquidSpill` failed.
   - Search the map for every filth def that the liquid can make before you call the liquid lost.

How to tell the classes apart, the 2026-10-11 tally and the modcheck/walk traps:
`references/classifying-and-learning.md`.

## Before you trust any run

- **Tier truth.** A proof labelled with a tier can run on a different list.
  - On 2026-10-10 a "gimmesomeslack tier" run was really on 550 mods.
  - Read `len(env.running)`. Compare that number between runs, never the labels.
- **Assembly identity.** Run from a clone or a `git archive` export whose DLL is byte-identical to the deployed copy.
  - A bench clone with an older DLL aborted FlowWorks' `validation_v2.py` at L2 (its row `L2_tier_live`).
- **Staleness.** A recorded proof goes STALE when any mod-folder file changes.
  - The exceptions are `validation.py`, `human_review.py`, `northstar/` and whatever the mod lists in `.hashignore`.
  - Review tooling and art sources belong in `.hashignore`.
  - A loose `.py` in the mod root IS hashed.
  - Finish every mod-folder edit before the run that you will record.
- **Owner rulings.** An owner ruling that *refuses* a behaviour invalidates every live site built before it.
  - Check the scene geometry against the ruling again.
  - The offline model stays green through that change, because the model never modelled the refusal.

More traps for this section: [references/traps.md](references/traps.md) § Before you trust any run.

## Flyers

🔴 **Never live-test a flyer's flight without the owner present.**

- He has said it three times. The rule is in the repo `CLAUDE.md` §If it flies in the fiction, it flies in the game. His
  words are in `design/RimMandrake/standing_rulings.md`, same heading.
- A proof row about flight reads `Pawn_FlightTracker` state through a debug `[Tool]`.
- A visual flight bar waits for a joint session (item FLYERFRAMES_PROVE_JOINT_SESSION, needs=owner).
- Never file a live-flight bar that only an unattended screenshot hunt could close.
- The proof-line lint (`rimflow/proof_lint.py`) marks a proof line as refused when it finds flyer words. The lint reads the
  line, its criterion and the item's title.
- The one exception is an item about a vehicle. That title names the vehicle before any flight word. No text of the item
  names a creature.

## Write it so Lightspeed can run it

Lightspeed is the testq lane that runs proofs with no LLM (SteveDesktop). 93% of test units qualify, but only if the
proof is written for Lightspeed:

- Exit 0/1/2 means PASS/FAIL/UNMEASURED.
- Print one deterministic row per criterion, with the verdict last.
- Use no `$`-built commands.
- Keep a criterion ≤160 chars, or put the full text in the prose.
- Validate the site first, and give a named UNMEASURED reason.
- Read flyers as state only.
- Declare the smallest tier (the smallest mod-list tier that holds the mod).
- `hot_reload_defs` is not a speed path.

`rimflow file`/`close` print a warning for each proof line that the proof-line lint marks as refused
(`rimflow/proof_lint.py`). The warning does not stop the filing or the close. `rimflow lint --proofs <ID>` runs the same lint, and
exits 1 on a bad line. The full rules, their reasons, and the PLANNED tools with today's fallback are in
`references/lightspeed-authoring.md`.

More traps for this section: [references/traps.md](references/traps.md) § Write it so Lightspeed can run it.

## Writing the plan before the run

Every live row owes three lines written **before** it runs:

- PROVE (the call);
- EXPECT (a number or string);
- LIES (how this row could pass falsely).

Every live row also owes a closing bar (the one reading that ends the check). The validation plan and threshold
discipline: `references/validation-plan-and-thresholds.md`. For handing a check to someone else, see
`skills/rimworld-modding/references/validation-plan.md`.

## Reference files

| file | read when |
|---|---|
| `references/run-checklists.md` | before every full-list run (start checklist) and before reporting one (end checklist) |
| `references/log-budgets.md` | any log-budget row, a "0 errors" that looks too clean, charging an error to a mod |
| `references/sites-and-timing.md` | staging sites, giants, fog, calm, map culling, tick windows, pre-port / mid-job save fixtures |
| `references/perf.md` | any perf row or budget |
| `references/classifying-and-learning.md` | after a run: MOD/SITE/HARNESS, fragility audits, recording into the script, modcheck/walk traps |
| `references/validation-plan-and-thresholds.md` | writing the plan and the closing bar for a check |
| `references/lightspeed-authoring.md` | writing any `live-proof` line or proof script: exit codes, rows, refused commands, advancing time, site checks, PLANNED tools |

## Helper budget for live proofs — owner, 2026-10-23 (token burn)

A live proof helper is ONE bridge driver with a hard budget:

- Write `max_turns` in the brief (default 30).
- Start a fresh helper per run or site. Never use one helper across many runs, because each turn re-reads its whole context.
- Run one Opus helper at a time.
- Run the proof as a single script and read its result.
- Never spend a turn per row, per tick window or per watchdog check. `belt_watchdog.py --watch 300` goes into `Monitor`,
  not a polling loop of turns.
- Stop at budget, or on any 429/session limit. Then write the exact resume command, push, and report in ≤12 lines.
- A limit error is never a PASS/FAIL row.

Measure each helper afterwards with `skills/rimworld-art-evaluation/scripts/helper_cost.py`. Full rules and the measured
incident: `skills/rimworld-art-evaluation/references/subagent_budget.md`.
