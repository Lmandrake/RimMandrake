# How we debug — debug through the script, leave the harness behind

status: **OFFICIAL**, owner rulings 2026-10-01 · binds the Conductor and every helper and subagent

## 0. The rule

1. **Every mod has a functional script.** Debug a bug in a mod with this script. Rerun the
   script, and watch it get further each run. The script grows with the code.
2. **Source first, still.** Read the source before you go live. A live run must be proven needed.
3. A live **behaviour** bug starts with **the mod's script**.
4. If the script cannot see the bug, poke the live game as long as it takes. **The session ends by writing what it
   learned into the script**:
   - a check that goes red for the reported reason before the final fix;
   - guards for the theories that proved false but are worth knowing.

   Nothing that found a bug lives only in `Transient/` or in a conversation.
5. Stuck → GPT, **early**, for hypotheses to test, never for a verdict. Still stuck → the owner.

The owner, 2026-10-01, typed: *"Initial debugging will always be debugging new code as
well as new validation scripts. And that's good. They evolve together."* And on poking:
*"It's more a sense of writing the final acceptance from a poking session. Capture what
you learned in terms of tests to detect this from now on. Including other theories that
proved false but would be informative to know."*

## 1. The build pause — 2026-10-01, LIFTED 2026-10-02

**Lifted by the owner 2026-10-02, typed: *"Build pause is lifted."*** The rest of this section records what the pause
was. The first-script contract (§2) still applies to every mod.

Owner, typed: *"It's worth slowing or stopping all current build to get this in place
everywhere and really exercise northstar. I really do mean stop and start working a new
way. This would be as big a need as rerunning clean dirty code is now."*

**Stopped** (decision taken by question card, 2026-10-01): **all new content**. All new content means new mods, new defs,
new mechanics and biome work. It also means roster sittings, and art jobs for content that is not built yet. Bring work
in flight to a committable state, and commit it. File its remainder as an item. Then the work stops.

**Allowed during the pause:**
- **Bug fixes** to existing mods, done by this process.
- **First scripts** (§2) and the harness that they need: `modcheck`, `northstar_driver`, site recipes, companion
  `[Tool]`s, and these four items in order:
  - (1) the static schema lint over bridge calls;
  - (2) the prior-pass-now-fail diff;
  - (3) the GPT-consult wrapper (§5);
  - (4) `northstar_driver run` that writes its result through `modcheck.status.record_run` (built; `--no-record` skips
    the record in `modcheck_status.json`).
- Load rounds that run first scripts. Batch them per `rimworld-load-round`. They remain on the Charter's expensive
  list (`infrastructure/agents/CHARTER.md` §The expensive list).
- **Exceptions:** only by the owner's own word, quoted on the item. A BENCH request is not an exception until he says
  it.

**DONE: what lifts the pause.** The pause lifts when **both** of these hold:

- **(a) Every mod has a committed first script.** "Every mod" means every folder that matches
  `src/*/*/About/About.xml`. The glob is the set, not a number in a doc. The glob held 164 on 2026-10-01, 48 of them
  `*ArtOverride`. "Has a script" means that the mod meets §2. The mod has its own `validation.py`, or it is a member of a
  family script. A family script is one script that covers a group of related mods. The mod also has a walk whose `## must be true`
  declares coverage. A walk is the file `design/validation_walks/<tier>/<Mod>.md` (§2.1).
- **(b) Every mod has a recorded live run.** In
  `infrastructure/state/modcheck_status.json`, every mod (or its family key) holds a run entry at its current hash.
  That entry is not `NEVER RUN` and not `REFUSED`. Every `RED` component is either fixed or filed as a named item.
  The item says which kind of defect it is: a MOD, SITE or HARNESS defect.

A filed RED does not hold the pause. A filed RED is bug work, and bug work continues anyway. When `modcheck status`
plus the glob census show (a) and (b), the seat that saw it tells the owner in one line, with the census output. Then
the pause is over. Umbrella item: `NORTHSTAR_EVERYWHERE_PROGRAM_1`.

**Keep the bridge busy** (owner, 2026-10-01, typed: *"Multitasking to keep the bridge active is a good
idea. That's what we want to maximize. Live bridge usage. In fact that's a great metric to track."*).
Live-run throughput bounds the pause, not authoring. So the bridge holder always has a next script to run:

- Authors work offline in parallel behind the current live run. Each author delivers a READY-TO-RUN script with a
  live-run sheet.
- The holder never sits on the bridge between runs. Release the bridge when it is truly idle.
- Nobody blocks on "writing everything first".

The tracked metric is bridge utilization (active driving and ticking time over held time):
`NORTHSTAR_BRIDGE_UTILIZATION_1`.

## 2. What a first script must contain

**Use the existing machinery and build no parallel system.** A first script is a modcheck `Suite` in
`src/<tier>/<Mod>/validation.py`. Its chains run on a live site. `northstar_driver` runs the same suite fast
(`USE_SUITE = True` in a `northstar_plan.py`). A `@bar` in a plan is for the owner's validated bars only. Functional
checks belong in the suite.

1. **Intended-function bars.** Write one line for each thing that the mod is for. Put the lines in the mod's walk
   `design/validation_walks/<tier>/<Mod>.md`, under **`## must be true`**. That section is agent-owned and not hashed.
   Take the lines from the mod's design doc, its `About.xml` description, and its defs and C#. Never invent them: a
   line with no source is a guess. If a mod has no walk, give it one. The walk is part of the first script.
2. **One cheap state check per line.** Each line gets a chain component that reads game state back. Examples: a def
   present with the right field, a thing spawned, a hediff applied, a job run. Another example is a setting toggled
   off, with the effect gone. Use the `t.*` verbs, and read the `success`/`foundCount`/`notFound` fields. Never substring a payload. A
   component that cannot ask records `UNMEASURED`, never PASS. Prefer short, local, cheap chains. Depth comes
   later, as bugs teach it.
3. **Coverage declaration.** Every `## must be true` line ends with `→ <chain>.<component>` or
   `→ UNCOVERED: <why>`. The why is a §4 boundary, or a missing tool named as an item. The arrows are the coverage. A
   line with neither arrow counts as uncovered and missing. Every Mod Settings toggle goes in `suite.toggles`
   (CLAUDE.md "superb Mod Settings").
4. **Ruled-out theories** go in the walk's `## anti-guessing notes`, one line each:
   `RULED OUT: <theory> — <the check or source line that killed it>`. A machine can watch some ruled-out causes. Such
   a cause also gets a guard component. The guard goes red if the ruled-out cause ever becomes true.
5. **Selftest offline first.** Run the script under `--mock`. The script must exit clean before it costs a bridge
   minute. A run recorded through `modcheck` is the record (§1 DONE (b)).
6. **Site prep.** Every scene starts from a cleared, dry, known site (`prepare_site` / `ProofResetRect`, a dryness
   check). So water, plants and clutter cannot decide the result. Check the footprint plus a 2-cell margin for
   source and water cells (`jawa/flowworks_excavation_rect`, `includeTerrain`). A failed check returns UNMEASURED with
   a named reason, never PASS or FAIL.
7. **Control.** Every scene has a case that must fail. That case is the same act without the thing (held without
   ladder, off-switch, wrong material). A scene with no control is not a test.
8. **Runnable with no LLM (Lightspeed).** Lightspeed is the testq lane that runs a proof with no model. A proof for
   that lane obeys these rules:
   - Exit 0/1/2 means PASS/FAIL/UNMEASURED.
   - Print one deterministic row per criterion, with the verdict last.
   - In a `live-proof` line, use no `$`-built commands and no game-mutating calls. A `live-proof` line is a line of
     `infrastructure/state/live_proofs/<ID>.txt`.
   - Keep each criterion ≤160 chars, or put the full text in the prose.
   - Advance with `B.ticks` (safe_advance), never with an advance-read-repeat loop.
   - Read flyers as state only.
   - Declare the smallest tier (the smallest mod-list tier that holds the mod).

   The reason: 93% of test units need no model. But only a proof written this way can run in that lane. The rules,
   their sources, and today's fallback for each PLANNED tool:
   `skills/live-debugging-proof-harness/references/lightspeed-authoring.md`.

**The `*ArtOverride` family is gone.** ART_OVERRIDE_FOLD_ALL_1 (2026-10-09) folded all 60 standalone art-override
mods into the mods that own their creatures. The art sits at a path inside the mod that owns the creature. A
`Patches/ArtFold/` patch points the donor def at that path. The offline proof is
`src/RimMandrake/Utils/art_fold_check.py` over `art_fold_manifest.json`. The live half is
`src/RimMandrake/Utils/art_fold_live.py --live` over the same manifest. The live half spawns each bound kind wild in
one expectations_l2 batch (`src/RimMandrake/Utils/expectations_l2.py`: spawn, tick and read the log once for all of the
kinds) and reads its texPath back. It attributes missing-texture lines per creature
(ART_OVERRIDE_FAMILY_SCRIPT_1). No owner mod's script covers these rows. (Here an owner mod is the mod that owns the
creature.)

**Folded mods.** A composed mod holds the member mods folded into it. An example is a biome folded into
`RimMandrake.Biomes`. The script of the composed mod covers a member only if that script's `## must be true` names the
member's lines.

**How passing is recorded.** `modcheck.status.record_run` is the only record. `record_run` writes `modcheck_status.json` under a
lock. The record is hash-bound: any edit to the mod makes the record STALE (the `code_review_status.py` discipline).
**The functional script passed** = `GREEN` (no hashed north star), or `DRAFT-CHECKLIST` / `PENDING-OWNER-REVIEW`
(passed; only the owner's layer is incomplete). **Not passing** = `RED`, `REFUSED`, `NEVER RUN`.

## 3. The debugging ladder

Walk the ladder in order. Stop at the first rung that settles the bug.

- **Rung 0: classify.** Write one line, only enough to choose the instrument:
  - **LOAD** (startup NRE, ConfigError, ModsConfig reset) → `Player.log`'s **first** exception.
  - **STATIC** (field, xpath, patch matching nothing, duplicate comp) → source, def dump, `validate_patch.py`, RimSage.
  - **BEHAVIOUR** → the mod's script.
  - **VISUAL** → screenshot plus judge, or the owner.
  - **HARNESS** (bridge tool, driver, site, result shape) → the driver's selftest and the schema lint.
- **Rung 1: source first.** Write down what source cannot tell you. If source settles the bug, fix it there.
- **Rung 2: run the script**, the relevant chains. Act on the outcome:
  - red on the symptom → a reproduction; go to rung 4.
  - **a check that passed before now fails → STOP**. That regression is the finding.
  - a new unrelated red → record it, and carry on, unless the red invalidates the reproduction or threatens state.
  - green while the symptom is real → the script is blind; go to rung 3.
- **Rung 3: poke, then write it down.** No clock. Probe live freely, through `python.exe`, while you hold the bridge.
  The poking ends **when it has taught you the cause**. The poking ends by writing a check that goes **red for the
  reported reason** before the final fix. "Red for the reported reason" means this: the check reads the same quantity
  as the symptom, not a correlate. A check never seen red proves nothing. Write the informative dead
  theories as §2.4 notes and guards. Throw the scratch probes away; only the checks stay. On 2026-10-01 the
  `ns_probe_*` scratch files vanished, and what they learned survived only in commit messages.
- **Rung 4: fix** the mod, the site or the harness, as the class says. Independent fixes may share a rerun. Isolate
  only fixes that could interact. A new assembly always goes alone.
- **Rung 5: rerun until green and read the whole result.** A changed predicate carries its reason in the commit.
  Never weaken a check to pass. A looser check is a script defect, unless the commit shows that the old predicate
  was wrong.
- **Rung 6: commit the check.** The commit names the class (MOD / SITE / HARNESS) and the check id.
- **Rung 7: stuck → GPT** (§5).
- **Rung 8:** two GPT rounds, no new evidence → the owner.

**At the bench** (decision taken by question card): interactive work with the owner is the point there, and the
script does not lead. **Every bench session leaves a test behind whenever a machine can check the lesson.** Write the
test in that sitting, or file it as a named item before the session ends.

**Ablation is later and explicit.** Owner: *"We can ablate unnecessary testing later if it
becomes slow or onerous."* Ablation is the removal of tests. Until he or a review says so, coverage grows. Nobody cuts a
test for speed.

## 4. Boundaries — where the script does not lead

| case | instrument instead | what still comes back to the script |
|---|---|---|
| engine load errors | `Player.log`, **first** exception (not the loudest); `rimworld-load-round` | a preflight log gate if it can recur |
| def / patch bugs | offline: source, def dump, `validate_patch.py`, RimSage | a state check only if it was visible only live |
| visual quality, tuning by feel | screenshot + judge / owner; `rimworld-live-review` | a framing check on captured frames |
| flyers in flight | `Pawn_FlightTracker` state read **only**; never unattended live flight (ruled 3×) | the state read, as a check |
| cold load, mod list, save migration | `rimworld-start-prep`, `rimworld-load-round`, `rimworld-savegame` | a tier fingerprint in preflight |
| world, map, art authoring | iterate by LOOKING | nothing |
| performance, intermittent, statistical | none yet; no Boolean check, which would mislead | the seed or sampling method, once one exists |

**Short ambient visuals are not verified live with the owner watching** (owner, 2026-09-25, verbatim):
*"stop this live testing. It's wasting time. These tests should be first handled my northstar-type validations and screenshots and such."*
A ripple, a puff or a flight animation first gets a north-star-style validation or an offline/screenshot check. A live
session that a human watches is the escalation, only when those checks genuinely cannot answer the question. A
frame-diff hunt does not work either: the terrain shader animates every frame and swamps a small transient fleck
(SCALD_WATER_AGITATION_FLECKS_1).

## 5. GPT consults — asked early

General consult lessons (inlining, size, timeouts, grading) live in the global `chatgpt-consult` skill,
`references/windows-wsl-codex.md`.

**Trigger** (decision taken by question card). Consult GPT when any **one** of these is true:

- 20 minutes without new evidence that tells hypotheses apart;
- **two** genuinely different causal theories refuted;
- a result that makes no sense against the current model of the system.

**Mechanism.** Run `python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file prompt.md -f <file>...`. The tool is a
shim over Dispatch's GPT door (`~/dev/Dispatch/providers/chatgpt/bin/gpt_door.py`). Do not start `codex` or
`codex.exe` by hand. The door picks the binary and the sign-in. The door keeps the outcomes apart: each consult ends
with one named verdict, and no answer is never a success. The door refuses a Windows launch that would raise the
sandbox-setup dialog.

**The brief contains:**

- the symptom and its class;
- expected vs actual;
- last-known-good state and what changed since;
- mod, tier and companion versions;
- the failing result rows;
- `Player.log`'s first exception;
- each ruled-out theory, and the check that ruled it out;
- the relevant source excerpts (GPT reads nothing it is not given);
- and one question: **"rank the hypotheses and give the cheapest test that tells each apart."**

🔑 **GPT's answer is a hypothesis, never a verdict.** Test each material claim with the strongest instrument that
fits: a script check, source, the log, or a mod-set bisection. Nothing that GPT says closes an item or reaches the
owner as a finding until someone has tested it.

**Retention** (decision taken by question card). The prompt and the answer stay in `Transient/` for the 14-day shelf.
Commit only the survivors, into the script, the walk and the commit: confirmed tests, and false theories worth knowing.

## 6. Who approves scripts, and the owner's bars

Owner, typed: *"Agents absolutely can build and approve validation scripts and declare
passing. I will periodically release adversarial agents and even gpt reviews to criticize
them or grow them."*

- **Functional scripts are agents' work, approved by agents.** A script runs green → the mod passes. No owner step.
- **The owner's validated north-star bars are a separate layer and are untouched.** These bars are the hash-bound
  `## north star` sections in walks with `state: VALIDATED`. `modcheck floor --all` re-derives which sections those
  are. CLAUDE.md's hash rule stands: a functional script never edits a hashed section. An agent may still draft
  north-star lines (DRAFT). Three routes bind them: his `modcheck validate --owner-said`; `--delegated --judge-verdict`, for new bars only
  (`delegation_policy.md` §1); and `--per-ruling`, as the Conductor's act (`delegation_policy.md` §2).
- **Periodic adversarial review.** The owner releases adversarial agents and GPT reviews against the scripts, on his
  clock (`NORTHSTAR_ADVERSARIAL_REVIEW_1`). A weakened, proxy or never-red check that they find is a script defect.
  Fix it and record it like any bug. Record each round in `design/RimMandrake/northstar_adversarial_rounds/`
  (findings, false leads, what changed). `src/RimMandrake/Utils/modcheck/selftest_northstar_adversarial_round.py`
  refuses a row without class, evidence or change.

### 6a. The north-star ladder (`NORTHSTAR_PHASE_LADDER_1`)

A mod with owner bars climbs these rungs in order. Each rung of each mod is one ledger item, named
`<MOD>_NORTHSTAR_<RUNG>_1`. The trial plans in `design/RimMandrake/northstar_trials/` list their items.

| rung | reached when | evidence that closes it |
|---|---|---|
| DRAFT | the walk has a `## north star` section, `state: DRAFT` | the commit |
| VALIDATED | the owner's word, `modcheck/cli.py validate <Mod> --owner-said "…"` (hash-bound; if you correct the prose, re-validate in the same sitting) | the ledger event |
| WIRED | every must-show / cannot-show line is claimed by a component's `shows=` in `validation.py`; `modcheck floor <Mod>` reports no uncovered or orphan id | the `floor` output |
| GREEN minimal | `northstar_driver` on the minimal list + the mod: preflight OK, every expected bar PASS (UNMEASURED is not green) | results JSON under `Transient/northstar/` |
| GREEN full | the same on the full canonical list, all five DLCs | results JSON |
| SHIPPED | deployed copy == repo with `.srchash` matching, Mod Settings complete, art complete, `code_review_status.py check` CLEAN for every file | the deploy plan + `check` output |

A rung closes only against that evidence, never against prose. A rung that regresses reopens as a finding, not as a
silent edit. MEASURED 2026-10-03: 3 of 110 tracked `validation.py` files carry `shows=` (FlowWorks, Graffiti,
Pyrelands). Re-measure: the number moves.

### 6b. Basic checkout vs extended concerns (owner, 2026-10-04)

Owner, typed: *"there are the 'basic checkout' requirements for a mod to be functional, and then there are the
'extended' aspects such as mod-mod compatibility, ensuring non compatible mods have been declared, game removal
consequences, and other such 'extended concerns' that are not part of typical Utinni play. These are NOT checked in a
typical checkout process but can be requested."*

- **Basic checkout** is what every run checks. The basic checkout covers the walk's `## must be true` lines and
  their chains. It also covers the hash-bound `## north star` bars and the floor (`modcheck floor`). The basic checkout is the evidence for "the mod works in
  Utinni play". `modcheck record` and the §6a ladder stand on it.
- **Extended concerns** are listed in a separate **`## extended`** section of the mod's walk. That section covers
  these concerns:
  - mod-mod compatibility;
  - declared incompatibilities (`incompatibleWith` / `loadAfter` in `About.xml`);
  - what happens when a player removes the mod from a save;
  - any other concern that ordinary Utinni play never meets.

  **They never run
  by default and never block a basic checkout.** An extended item that is not covered is not a gap in the basic
  checkout.
- **They run only on request.** A script runs them only behind an explicit flag (for example
  `validation.py --removal-check NAME`). The walk names that flag on the item. The walk's flags are the whole
  interface. There is no modcheck verb for extended concerns (owner, 2026-11-12: delete that design).
- Write each item in `## extended` as `- E<n>. <what> -> <flag or UNBUILT>; <state>`.

### 6c. The human review map

The human review map is a third layer, next to the script and the bars. The map shows a staged scene, with labels. The
owner can look at it and play with it. The map records no verdict. Draft principles from the first map (MessyConduit), pending his
approval: `design/RimMandrake/northstar_human_review.md`.

## 7. Briefing a bridge-driving subagent

The standing form of this brief is the Test Pilot (owner 2026-10-31). `rimflow pilot <ID>` prints the brief for an
`rm-testpilot` agent. An item reaches a Test Pilot in two cases: 3 non-pass runs in a
row, or a need for live observation. The route is in `src/RimMandrake/rimflow/testpilot_route.py`. The brief of the Test Pilot names deploys and list changes.
The Test Pilot may do them on its host, and it backs the list up and restores it. Everything below still binds the
Test Pilot.

- **One driver at a time.** The holder takes the bridge lock. The subagent drives through the driver or `modcheck`,
  never around them.
- **The brief contains:**
  - the mod, its `validation.py` / plan path, the tier; the symptom and its class; the check that must go red;
  - stop conditions: prior-pass-now-fail; two refuted theories (report back, with the GPT trigger); `success: true`
    with no visible effect;
  - forbidden: `ModsConfig.xml`, deploys and `modcheck run` (it swaps the mod list) unless the brief names them.
    Also forbidden: `stash` / `reset --hard` / `checkout --`, and unattended flyer flight.
- **"End the poking by committing the check and the ruled-out notes; throw the probe away"**. Tell the subagent also
  to create the output file as a skeleton first.
- **Model:** a live bridge write follows `Agent_Policy.md`, which is never restated here.
- **Who closes:** whoever proves it. The evidence is a red→green pair and the commit.

## 8. Why — the evidence of 2026-10-01

One day of script-driven work on Graffiti and Pyrelands turned findings into commits:

- `draft=` vs `drafted=`, and a ~10 s `step_game_ticks` give-up (`f4428e8f1`);
- a no-op `waitTicks` on a paused site (`afcd048bd`);
- a 10/10 state PASS hiding 76 of 79 unjudgeable frames (`757ee7521`);
- 22 call sites with undeclared params or missing tools (`cceea3071`);
- one-tick waits stretching a run to ~4 h (`e2879e83a`);
- one mod defect, `RUT_Barbslinger`'s two turret comps (`710208b9d`).

Lessons: **rerunnable checks work and are fast**; **most early findings are HARNESS, not MOD** (why the commit names
the class); **what lived outside a script vanished**.

This file adopts GPT's adversarial review of the draft on these points (prompt and answer:
`Transient/debug_process_gpt/`, kept in history):

- a red check before the *final* fix, not before all investigation;
- "red for the reported reason" defined;
- non-machine, intermittent and performance defects out of scope (§4);
- prior-pass-now-fail kept separate from a new unrelated red;
- independent fixes batch;
- the bench owes a test;
- GPT asked early, tested by the strongest instrument, conclusions only committed.

Superseded by the owner:

- the 20-minute exploration window (now no clock);
- never-owner-approved non-bar checks (now agent-approved functional scripts);
- the pilot (a trial of 10 incidents or 14 days on Graffiti and two Pyrelands chains; now a full stop and a new way of
  working).

## Every debug set carries the camera-zoom mod — owner, 2026-10-04

*"We need the extra camera zoom mod to be in ALL DEBUG SETS for testing … make that policy change right now for Rimworld Debugging and Northstar."*

- `src/RimMandrake/Utils/zoom_guard.py` is the guard. Every door that writes the live list calls the guard. The doors
  are `modlist_swap` swap/--enable, `modset_builder.write_config`, and `modcheck` `compose_test_list`.
- `resolve_tier` adds the zoom mod per tier. `ModsConfig.MINIMAL.xml` carries it.
- Either `ray1203.simplecamerasetting` or Camera+ satisfies the guard. The two conflict, so never load both.
- A door does not write a list that has neither: the guard refuses that list.
- `./game deploying` adds the zoom mod. `./game loading|up` shouts and exits 3 if the load lacks it.
- Item ZOOM_MOD_ENFORCE_NOT_JUST_ONE_DOOR.

## Test disturbances: verdict, restart, and a ticket every time — owner, 2026-10-13 (by card)

> *"if telemetry detected an anomaly that was corrected and there is no evidence of damage to the test, it can PASS still. If there's any sign of damage to the test itself (active fires in the testing area, colonists dying or getting hurt that were supposed to do something) test is restarted. ALSO, every time a threat to a test appears, it must be logged and a testing environment ticket made to improve/control the testing environment to prevent this interference next time. Let's get better at testing!"*

- **Corrected anomaly, no damage to the test → the row may still PASS.** Damage to the test itself (fire in the test
  area, a needed colonist hurt or dead, the sample gone) → restart the row. Never score the row FAIL.
- **Every threat that appears during a test is logged AND gets a test-environment item.** The job of the item is to
  stop that interference next time.
- **Long runs of game time:** start none (§Long-duration properties below: his words of 2.5 h later the same day).
- **Staging is put back by a script step, never by an agent remembering** (owner, 2026-11-03; item
  `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED`). A teardown step in the script restores whatever a scene forces (event
  chances, spawns, cleared plants, drafted pawns). A run that ends early still runs the teardown step.
- **Support colonists** may be protected (can't die, can't starve) **only in tests labelled as not about health,
  needs, damage or death** (by card).
- **Two suites:** isolated mechanism tests on quiet maps, plus a separate integration suite. Load all five DLCs in
  both (by card).

Basis: pass 7 (Pyrelands live pass 7, 2026-10-13: a test colony starved during long tick advances) and GPT's review
`design/RimMandrake/test_control/test_control_review_gpt_20261013.md`. Build: `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO`.

## Owner-look scenes come from the proof scripts

The mod's own proof script stages each scene that the owner will watch (its site prep, its control case). Do not stage
the scene by hand. If the script lacks the scene, add the scene to the script first. Label a hand-staged look as
hand-staged, and name each cheat. (Evidence, Conductor 2026-11-03: the scripts `climb_proof.py` and `extensions.py`
encode the dry plot and the held-without-ladder control. Hand staging gave a flooded pit and a ladder in a climbable
pit.)

## Long-duration properties: compress, decompose, infer — owner, 2026-10-13

> *"we are going to need a different method of testing for "long game duration" type exploration. Perhaps we could change the timing constants to one that is within easy testing so it can be observed, then reset back to the longer duration once confirmed. Things like that. Some things will not be directly verified in that way as well, due to the complex or long duration nature of their needs. Instead, they will have individual components verified and the integrated whole inferred instead. Please make a note of this: we should not waste dozens of hours frantically testing for a single very-hard-to-demonstrate property of an otherwise checked out mod."*

- **Compress first.** A property can need days of game time. Shorten its timing constants (a Mod Setting or a
  test-profile override), so that you can watch it in minutes. Then restore the shipped constant, and read its value
  back to check it.
- **Otherwise decompose.** When compression cannot reach the property, verify each component separately. Record the
  integrated whole as **INFERRED**, and name the components that it rests on. INFERRED is an accepted verdict, not a
  gap to chase.
- **No long runs (owner, 2026-10-13, typed: *"Go back to building and testing things you can directly measure. No more long runs, ok?"*).**
  Do not start long multi-suite live passes or long game-time waits. Build and test the work in pieces that you can
  measure directly.
- **Never chase one hard property for hours.** One very-hard-to-demonstrate property does not hold a mod hostage when
  its other rows check out. Most mods will have some of these items by necessity. A row of this kind says so in its
  contract, instead of reading UNMEASURED forever.

## Every owner-found defect is stored for the ladder — owner, 2026-11-12

*"Make it a rule to store these items until our validation ladder is fully defined and regenerated. Then we will ingest
them properly where and how they belong."* (2026-11-12 ~9:35 PM PST.) This rule replaces two older texts:

- the 2026-10-24 rule that a defect gets its own wired selftest;
- the 2026-11-12 ~9:20 PM "closes only with a named check" text.

Append each defect that he reports in a look to `design/RimMandrake/validation_holding/`. Wire nothing from there into
a ladder stage, gate, nightly list or close check until its mod reaches preflight (Stage 2). There each held statement
goes into the mod's test table (owner by card 2026-11-14: "Per mod, as it advances."). Rule:
`design/RimMandrake/validation_map_and_rules.md` Rule 12. A live session that debugs such a defect also ends with its
check in the mod's own functional script (§0.4). The script is not a ladder stage, gate, nightly list or close check.
