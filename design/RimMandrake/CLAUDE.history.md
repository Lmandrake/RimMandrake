# CLAUDE.md history — measurements and incident detail moved out of the root CLAUDE.md

The root `CLAUDE.md` holds rules and pointers. When a measurement that goes stale, or the story behind a rule, leaves
it and has no better home (a rulings file, a skill, a lesson), it lands here, under the rule it belongs to. The rule
itself stays in `CLAUDE.md`.

## Facts you cannot guess — how long a cold load takes

Moved 2026-11-19 (Crystallize W47, knowledge merge), because the figure grows with the mod list.

- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** *(MEASURED 2026-09-07, second launch
  of a session; a first launch after a reboot may run slower.)*
- An earlier figure: ~25 minutes on the owner's full list against 22 seconds on a 13-mod minimal list (measured
  2026-08-19; the `rimworld-load-round` skill carries it with its method).
- The rule that stays in `CLAUDE.md`: never "restart and see"; a quicktest map is the cheap instrument.

## Long runs of game time — the earlier of his two rulings of 2026-10-13

Moved 2026-11-23 from `design/RimMandrake/debug_process.md` §Test disturbances. His later words of the same day
(2026-10-13 04:34Z) replaced it: `debug_process.md` §Long-duration properties, "No long runs".

- Owner, 2026-10-13 02:02Z: *"long runs are possible but risky: they require more time, more monitoring, and fewer assumptions to succeed. Avoid them when possible unless it's a clear win for time efficiency compared to an alternative."*

## The owner's earlier two-way promotion test

Moved 2026-11-23 from `infrastructure/STRUCTURE.md`. The three naming tiers (`design/NAMING_SCHEME_PLAN.md`) replaced it.

- The owner: *"Am I likely to want this in a totally unrelated playthrough, or will I have to fundamentally remake it — not just reconfigure it?"* The old rule read: reconfigure → `RimMandrake/`; remake → `Jawa/`; when unsure, `Jawa/`.

## The owner's words the root CLAUDE.md quoted, by rule

Moved 2026-11-19, when the root `CLAUDE.md` was drained to rule lines and pointers (owner, 2026-11-19: *"No
provenance either, that's for git."*; `standing_rulings.md` §The root CLAUDE.md holds rule lines and pointers only).
Each heading is the rule's old `CLAUDE.md` heading, with its date. Each line is the excerpt of his words that
`CLAUDE.md` quoted. His full words are in the rule's home (`standing_rulings.md`, `biome_rulings.md`, or the file the
rule points at); an excerpt here is often part of a longer sentence there. Rules whose `CLAUDE.md` quotes already
appear word for word in their home are not repeated here.

### How we debug — owner, 2026-10-01
- "I really do mean stop and start working a new way."
- "Both autonomy questions are yes"

### 🔴 A BIOME WITH ZERO TILES IS NOT A DEFECT — owner, 2026-09-20, said repeatedly
- "It is a RECORD of the planet, not a rival to it."

### 🔴 Six biome mods are HELD BY OWNER; Pyrelands is the only biome mod advancing — owner, 2026-11-16
- "And stop the new biome mods work. Only Pyrelands as a biome mod right now."

### 🔴 No mod runs forward on a broken pipeline — owner, 2026-11-19
- "We're not running mods forward until the pipeline is fixed, ok? So now you don't have to ask me anymore for that."

### Biomes, rosters and seas — owner rulings (full text: `design/RimMandrake/biome_rulings.md`)
- "Animals sound be biome-specific unless there is an in-game reason"
- "I meant pick one arid home."
- "Let's stop evictions right now"
- "This is a human review process issue."
- "what you encounter as an animal there … as well as what you can FISH out"
- "It's ship or nothing."

### 🔑 "Star Wars style" naming is NOT Star Wars IP — owner, 2026-09-22 (Q11a)
- "The fact that we will use "star wars style" naming doesn't mean they have to live in the star wars layer."

### 🔴 One Direct Sun, a pure function of geometry — owner, 2026-09-29 and 2026-10-19
- "It can't be a new "kind" of heat."
- "no biome-specific heat, no biome-specific sun. It's a matter of geometry (low sun is less intense AND produces longer shade, high sun produces only covered shade and much more intense effect). Ambient heat is normal Rimworld rules."
- "If we have an excellent tree shade model working, then YES direct sun works the same everywhere on the day side."

### 🔑 Every DLC is assumed — owner, 2026-09-19/25/26
- "ALL TEST MOD LISTS should include ALL THE EXPANSIONS; we're not trying to ablate expansions out of our list at this time."

### Every mod ships superb Mod Settings — owner, 2026-09-12
- "We can't guarantee they will work in other biomes beyond our framework. They should… but we're not going to validate that at this time."

### 🔴 Agents decide nearly everything; only five acts stay his, and the Conductor may do the rest, mindfully — owner, 2026-10-22 and 2026-11-19
- "Nearly everything including art. An agent can absolutely ask another agent for an art ruling based on some prose constraints and requirements we can draft."
- "I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending money, public publishing. Everything else the Conductor should mindfully be able to do."

### 🔴 The Evidence-for-Ask rule — owner, 2026-11-15
- "For ALL questions and choices from now on, Conductor must have evidence why it does not select the obvious answer before it pauses for the human, alright? This is a RimMandrake-wide ruling for all pausing agents."
- "Don't keep telling me we can't do things when it's from pre-maturation pipeline decisions."

### 🔴 The pipeline fixes its own defects — owner, 2026-11-15
- "the Pipeline fixes its own issues once detected. When there's a clear problem and a known fix... do it. It's not a ticket for someone else, it's a ticket to file then do yourself."

### 🔴 No trial is spent by a system failure — owner, 2026-11-18
- "I will not accept ANY system that pointlessly expends such statistical measurements based on failed system calls or behavior."

### 🔴 No limit without the danger it guards — owner, 2026-10-31 to 2026-11-17
- "Each element must defend precisely what it's protecting against and have evidence that it actually happens... but when it has... protect cheaply!"
- "Please stop building arbitrary pauses into the system..."
- "No time limits please."
- "please get rid of these arbitrary cuts!"

### 🔴 A passing bar is an experience, never a tuning number — owner, 2026-11-16
- "The mod passing bars should not specify flora and fauna yield rates! That would mean every time we renormalize every mod must repass its bars... drop that!"

### 🔴 The test is built with the item, offline and live — owner, 2026-11-13
- "from now on, we build the test at the same time as the item, both offline and online versions. then they get consolidated into the formal tests."

### 🔴 A refusal carries its path to pass — owner, 2026-11-12
- "ANY refusals must be as detailed as the evidence they are rejecting and include the fixes and paths towards passing that are attainable and reasonable."

### From `design/RimMandrake/standing_rulings.md` §Resetting a test scene is harness housekeeping — what the 2026-11-17 ruling superseded

- **Superseded:** the polish entry `RIMMANDRAKE_RESTORE_PYRE_WIND_SCENE_GROUND` (deleted from
  `design/concepts/Pyrelands/version/polish.md`; it was never filed); "restoration" as a judged part of the proof-scene
  contract (`coverage_judge.py` prompt, `roles/designer_scene_contract.md`, `roles/designer_lock.md` step 5).

### From `design/RimMandrake/standing_rulings.md` §Todoist is for to-do lists only — the old alarm tasks, closed 2026-11-19

- The 173 alarm tasks our senders had left open in the Inbox he shares with Steve were completed 2026-11-19
  (`D:\ClaudeWork\rimmandrake\conductor\todoist_alarm_tasks_closed_20261119.md`).

### From `design/RimMandrake/standing_rulings.md` §The root CLAUDE.md holds rule lines and pointers only — the drain of 2026-11-19

- The drain itself: item `RIMMANDRAKE_DRAIN_CLAUDE_MD_RULE_LINES_OLD_RULING_OBSOLETE`; report
  `D:\ClaudeWork\rimmandrake\conductor\crystallize_2026W47\claude_md_drain.md`.

### From `design/RimMandrake/standing_rulings.md` §The bridge is passed through one file — the old RELENTLESS holder

**RELENTLESS** was the retired Relentless Pipeline's bridge holder (`model.bridge_identity`), not a seat: only old `bridge` events carry it.

### From `design/RimMandrake/standing_rulings.md` §Every DLC is assumed — the Core-only tiers before 2026-09-19

`modset_builder.py`'s `bridge`/`pits`/`graffiti`/`oracle` tiers built Core-only before the owner's ruling of 2026-09-19 that all test mod lists include all five expansions.

### From `design/RimMandrake/standing_rulings.md` §Shipping names are three-tier — the stale citations of 2026-09

Three live docs were still citing `NAMING_SCHEME_EXECUTION_1` as a reason to wait 16 days after it
closed, which is how `FlowWorks` (named by ruling 20, 2026-09-16) kept shipping
as `fluidcanals`.

### From `design/RimMandrake/standing_rulings.md` §North-star validation state — the stored-field fix of 2026-09-17

The "modcheck status reads a stored field" bug was
FIXED (`fa27e1cab`, `status.check_or_orphaned` + `doctor.py`, the same day as the walk claim of that section was
first written) — live-checked 2026-09-17: `modcheck status` now correctly prints `FlowWorks
STALE   [stored: GREEN]` and `Pits ORPHANED (no such mod folder)   [stored: GREEN]`, re-deriving
every row rather than trusting the stored field. The dead `FluidCanals` key is gone too
(`b110a7a2d`, `rename-key`/`forget-key`).

### From `infrastructure/agents/CHARTER.md` §CHARTER — binds the Conductor and its helpers — what the charter replaced, 2026-08-27
*Adopted 2026-08-27 (owner's ruling, this date). The charter replaced POLICY.md, the four seat files, and most of the
process prose. Git holds everything removed.*

### From `infrastructure/agents/CHARTER.md` §Decisions — a limit from before the Maturation Pipeline is suspect, owner 2026-11-17
**A limit from before the Maturation Pipeline is suspect** (owner, 2026-11-17: "Don't keep telling me we can't do
things when it's from pre-maturation pipeline decisions"). Never refuse an act because of such a limit. Act, or ask him
first. If you ask, quote the old decision's date and text (`standing_rulings.md` §A limit from before the Maturation
Pipeline).

### From `infrastructure/agents/CHARTER.md` §How we debug — owner, 2026-10-01 — the lines that root `CLAUDE.md` §How we debug now holds
`design/RimMandrake/debug_process.md` is the process. **Every mod has a functional script and is debugged through
it.**

- Run the script first. When the script is blind, poke the live game.
- End every poking session with the lesson written into the script. The lesson is a check that is red for the reported
  reason before the final fix. Add the informative theories that proved false.
- Agents write, approve and declare passing on these scripts.
- Agents may add regression checks and new `## north star` bars (owner 2026-10-26, `delegation_policy.md` §1).
- When you are stuck, go to GPT early, for hypotheses to test.

The owner lifted the 2026-10-01 build pause on 2026-10-02 (*"Build pause is lifted."*). Every new mod still ships with
its first script (`debug_process.md` §2).

### From `infrastructure/agents/CHARTER.md` §Instruments, in order — the owner's testing words, 2026-10-28

Which kind of testing to run, when, and its tunables: `design/RimMandrake/testing_policy_2026-10-28.md` and
`src/RimMandrake/rimflow/testing_policy.json` (owner, 2026-10-28: "Let's get smarter about the testing we do and only
use appropriate kinds of testing when/where it will help us.").

### From `design/RimMandrake/standing_rulings.md` §The pipeline fixes its own defects — the incident of 2026-11-15

The incident: on 2026-11-15 the Conductor and its helpers worked around one pipeline defect after another by hand (fix
tickets that never launched, a silent exam skip, run dollars, a sparse-clone publish, a stale dispatch clone, stale
owner labels), and each one came back.

### From `design/RimMandrake/standing_rulings.md` §Evidence-for-Ask — the incident of 2026-11-15

The incident: every new mod's Design Version reached him as an ask, and the answer was 0.1.0 every time.

### From `design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found — the eleven refusals of 2026-11-20

The incident: in one night (2026-11-20) eleven gates refused work for a fault of form, and the tick turned each set of
three refusals into a paused mod (`OPS_MATURATION_SYSTEM_FAULT_LOOP`) or a line that waited for a hand: a launch during
a planned account drain, a game folder with another mod's developer script, an item name without its visit number, a
commit of an ignored lock file, a 66-character item name, a by-card brief without the card text, a helper-slot count
that included the Conductor window's slots, a stale certificate left as a hand command, a capped visit left
unfinished, a close that wanted a level-L0 `verify` first, and a test table whose live commands could not start under
`red-seen`. Each one was repaired as one instance. This section repairs the class.
