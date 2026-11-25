# RimMandrake: a RimWorld 1.6 mod project (a Jawa scavenger clan on a desert world)

This file holds rules and pointers only. Each rule's full text, the owner's words and the evidence live in the
file that the rule points at. Git holds the history. Write each entry in Simplified Technical English, with no
provenance (`design/RimMandrake/standing_rulings.md` §The root CLAUDE.md holds rule lines and pointers only).

## Read these first

- `PURPOSE.md` says what this repo is. It is an experimental agent software factory, and its product is a game.
- `infrastructure/agents/CHARTER.md` is the full process rulebook.
- The top of `infrastructure/agents/CHARTER.md` holds the Principle of Impactful Evidence. Spend testing where the
  evidence is likely to change what we do, weighed against the cost of the evidence. Read the Principle before you add,
  repeat or retire a test.
- Read your own window file. The Conductor (the window that the owner talks to) reads
  `infrastructure/agents/CONDUCTOR.md`.
- The game cycle is in `infrastructure/GAME_STATE_WORKFLOW.md`.
- This repo's application of the fleet ladder is in `infrastructure/agents/Agent_Policy.md` and nowhere else. Do not restate it.
- `GUIDING_PRINCIPLES.md` says what is always true of the game, above any one mod or biome. It binds. Read it before
  you design or judge.

## Where the full text lives

| topic | full text |
|---|---|
| biome, roster, sea and naming-tier rulings | `design/RimMandrake/biome_rulings.md` |
| north star, LLM transport, pits, DLC, git, code review, art, bridge, savegame options, delegation, pipeline, judges, spend, tests | `design/RimMandrake/standing_rulings.md` |
| measurements and owner words moved out of this file | `design/RimMandrake/CLAUDE.history.md` |
| instruments that return a confident wrong number | `infrastructure/state/facts/instrument_traps.md` |
| tools with surprising side effects | `infrastructure/state/facts/tool_traps.md` |
| creature flight (stat, race flags, flip-book) | `skills/rimworld-modding/references/flight.md` |
| ticking, `MayRequire`, csproj, patch behaviour | `skills/rimworld-modding/references/project-engine-facts.md` |

## How we debug

- Every mod has a functional script. Debug the mod through that script. Run the script first. When the script is
  blind, poke the live game.
- Each live debug session ends with an update to that script. Write what the session learned, false theories included.
  The lesson is a check that is red for the reported reason before the final fix.
- After the fix, a check that was made only for that fault stays in the live tests only while the fault is likely to
  return. Otherwise move the check to the offline tests, or retire the check (§A live test declares its kind).
- Agents write, approve and declare passing on these scripts. Every new mod ships with its first script.
- Agents may add regression checks and new north-star bars (`design/RimMandrake/delegation_policy.md` §1).
- Only the Conductor may loosen a bar, as a mindful act (see "Only five acts stay his" below).
- When Python cannot control or measure a thing through the bridge, add generic C# to the bridge that reaches the
  thing. Do not ask first: build or file the bridge function, test first. Tests, scene steps and verdicts stay in Python;
  never put a test, a scene or a check of one mod in C#. Full text: `design/RimMandrake/standing_rulings.md` §What Python
  cannot reach goes into the bridge's C#.
- When you are stuck, go to GPT early, for hypotheses to test.
- Process: `design/RimMandrake/debug_process.md`.

## There is no worldgen feature, in any version

- Do not build automated or programmatic worldgen. Do not offer worldgen to players. This is permanent: mark such
  work dead, never deferred to v2.
- Players do not generate anything. They receive a savegame that holds one fixed, hand-made world. A faction,
  ideoligion or setting that is absent when the world freezes is absent from every player's game.
- Do not build anything that makes alternative planets. That includes seed sweeps, variants and any setting that
  could roll a second world.
- Author the one map. Judge it by realism first, and improve it by looking at it (`worldview.py`). Target and
  references: `design/Jawa/worldbuilding/the_one_map.md`.
- Full text: `design/RimMandrake/standing_rulings.md` §There is no worldgen feature.

## A biome with zero tiles is not a defect

- We paint the planet once, at the end, after every biome's content is in mods. Until then, a BiomeDef of ours on
  0 tiles is the expected state. It is not a finding or a defect.
- Do not point our content at a donor def to make it show on today's map.
- Do not use a tile count as evidence that something is or is not built.
- The paint list is the item `BIOME_PAINT_ONCE_AT_THE_END_1`.
- `world/ASHKARR_WORLDMAP_tiles.csv` is a record of the planet on its export date. It is not the live planet. Only the
  live game tells you the state now.
- Full text: `design/RimMandrake/biome_rulings.md`.

## The pipelines before the Maturation Pipeline are retired

- Builds run in the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md`).
- The Conductor launches helpers with `src/RimMandrake/rimflow/detached_helper.py`.
- Design work goes to the Designer (`src/RimMandrake/rimflow/roles/designer.md`). Ops alarms go to Operations.
- No `relentless*` module is left. Do not bring back any part of a retired era: `selftest_retired_era_gone.py`
  refuses a remnant at `./publish`.
- Some live paths and names still say relentless, FOUNDRY or pulse, which are retired names. Each rename is a ticket.
  The list is in `design/RimMandrake/retired_eras_index_2026-11-18.md`.
- `rm-findings-judge.timer` runs the daily findings judgment and the Friday memory sweep.
- FOUNDRY is a retired name, not a seat. `rimflow` maps it to the Conductor's key (`RETIRED_SEATS` in `cli.py`), and
  so does the FlowWorks lane (`infrastructure/state/flowworks_lane.json`, field `seat`).
- Full text: `design/RimMandrake/standing_rulings.md` §The pipelines before the Maturation Pipeline are retired.

## Six biome mods are held by the owner; Pyrelands is the only biome mod that advances

- The held list is `src/RimMandrake/rimflow/mod_owner_hold.json`. The pipeline launches, chains and alarms nothing on
  a held mod.
- Only the owner or the Conductor window may lift a hold.
  - His lift: `mod_owner_hold.py lift <Mod> --said "…"`.
  - The Conductor's lift, from the Conductor window: `mod_owner_hold.py lift <Mod> --per-ruling
    RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE --why "…"`. The ledger records it as the Conductor's act,
    never as his words. It goes into his daily digest.
- No helper, other seat or tick lifts a hold. `pipe on` does not lift a hold.
- A lifted mod still does not run while its readiness list is not READY (next rule).
- A helper may write design text on a held mod. Builds, tests and live runs stay held. The held mods will return;
  they are not deprecated.
- Full text: `design/RimMandrake/standing_rulings.md` §Owner hold.

## No mod runs forward on a broken pipeline

- Do not run a mod forward while an open pipeline ticket classed BLOCKS lies on that mod's path.
- Each of these acts runs a mod forward:
  - to switch a mod stage on;
  - to release a stage ceiling (the spend limit of one stage) for the mod;
  - to launch a build, a fix or an in-game visit of the mod.
- The check is the mod's readiness list. The readiness list names every component the mod will touch. The readiness
  list marks each open ticket BLOCKS, RARE or NOT ON PATH. A component you could not look at is never clean.
- The pipeline is fixed for a mod when its readiness list reads READY.
- Do not ask the owner whether to run a mod before then. Pipeline repair, design text and investigations continue.
- Full text: `design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline.

## Biomes, rosters and seas

- Before you design, build, audit or edit a biome, roster, sea or creature, read
  `design/RimMandrake/biome_rulings.md`. The file holds the full rules. Topics: greatbole defs, one biome per animal,
  roster holes, sea catches, the ship to the seabed, review-sheet cuts.
- Every BiomeDef with a roster sets `animalDensity`. An unset value is 0, and then no animals ever spawn.
- Parse `<wildAnimals>` and `<wildPlants>` as XML elements. Do not count `<li>` tags.
- An `RM_` twin biome gets its real cast from patches (`UtinniPatches/Patches/WildAnimals_<Biome>.xml`). If you read
  only the BiomeDefs, you see the wrong half.
- Evictions from a roster are stopped. No pass edits a roster to enforce the one-biome rule.

## Star Wars style naming is not Star Wars IP

- Before you name a creature, plant or roster, read `design/RimMandrake/biome_rulings.md` §"Star Wars style" naming
  is NOT Star Wars IP. Read that section also before you pick a tier (`RM_` or the Utinni patch layer) or call a name
  canon.
- A question about a naming tier or about provenance can make more sub-questions. Then stop. First ask if the category
  itself is necessary.

## Facts you cannot guess

- ArchBig reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, and ArchSmall reads its own `Mods` folder
  (§There are several live games). No game reads this repo. A file that you write
  here is not deployed.
- A cold load on the full mod list takes many minutes. A quicktest map takes about 90 s. So never restart the game
  only to look at the result. The figures: `design/RimMandrake/CLAUDE.history.md` and the `rimworld-load-round` skill.
- `ModsConfig.xml` is the live mod list. It describes the next load. Its path is
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
- To count active mods, parse ModsConfig (`ET.parse(p).find("activeMods")`). Do not `grep` it. Do not use a mod count
  from a doc.
- Do not restore the owner's mod list. Leave ModsConfig on the tier that serves your work. There is no "restore before
  release" step.
- Nobody plays the game during development. No game and no save is the owner's. The full list of what is protected:
  - Only the canonical world saves are precious (`infrastructure/state/CANONICAL_SAVE.md`). All other saves are
    disposable. Keep a save that waits for his review until he rules (§Options he must LOOK at).
  - His OWNER hold and `./pipe off game:<name>` guard a look: he looks at staged work on ArchBig or ArchSmall.
  - Never put the game in fullscreen or in focus. He controls the clock in a sitting.
  - Do not write a rule, a guard or a question that protects his play, his game or his saves. If you find one, delete it.
  - Stop a broken game at once, on any game, and report the stop. A test may remove things on any save that is not
    canonical.
  - Full text: `design/RimMandrake/standing_rulings.md` §Nobody plays during development.
- Do not guess a defName, field or namespace. Read it from RimSage (`mcp__rimsage__*`, Windows Desktop only), the def,
  the About.xml or `measure`.
- Get a number about a large artifact from `measure`, never from a scan (`block_blind_scan.py` refuses a scan). `0`
  means measured zero. If you do not know, the answer is `UNMEASURED`.
- An instrument here can return a confident wrong number. Before you trust a count, read the measured traps in
  `infrastructure/state/facts/instrument_traps.md`.
- `Plant` ticks only `TickLong()`. A comp on a plant overrides `CompTickLong()`.
- `MayRequire` on a top-level `<Operation>` has no effect. Guard with `PatchOperationFindMod`/`Conditional`.
- A member mod that is composed into `mandrake.rm.biomes` has no packageId of its own at runtime. So a `MayRequire`
  that names a member id never loads.
- A patch that matches nothing logs nothing. Detail: `skills/rimworld-modding/references/project-engine-facts.md`.
- `modcheck run <Mod>` rewrites the live `ModsConfig.xml` (the expensive list).
- When a new game does not start, read the FIRST exception in `Player.log`, not the loudest one.
- Some tools have surprising side effects. Read `infrastructure/state/facts/tool_traps.md`. Subagent watchdog,
  mid-session hooks and card gates: `infrastructure/agents/Agent_Policy.md`. `handoff.py` and two Conductor windows:
  `skills/using-rimflow/references/traps.md`.
- Dumps and harvests go stale. Trust one only after its fingerprint matches the live mod set. The frozen `official`
  dump (`observed/inventory/DefDump_OFFICIAL/`) is the only design target.
- Full text: `design/RimMandrake/standing_rulings.md` §Facts you cannot guess.

## North-star validation

- The validated hash covers the whole `## north star` section, prose included.
- When north-star prose is false, correct the text and re-validate in the same sitting. Change no code. Re-validate on
  the owner's word or as the Conductor's act.
- Write only prose that stays true in every state. Never write validation state as prose: `modcheck floor --all`
  measures it.
- The traps of walk findings, and all other detail: `design/RimMandrake/standing_rulings.md` §North-star validation
  state.

## In-game LLM access is the Claude Code CLI, never a hosted API key

- Before you design or build an in-game LLM call, read `design/RimMandrake/standing_rulings.md` §In-game LLM access.
  Then read the two laws in the spec, `design/RimMandrake/llm_ingame_wiring_spec.md`.

## A pit is a superdeep cell, not a building

- Before you design or build a pit, read the item `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`. Then read
  `design/RimMandrake/standing_rulings.md` §A pit is a SUPERDEEP cell.
- Do not act on the 1127-line spec `design/RimMandrake/pit_superdeep_collapse_spec.md` before you read the item. Ten
  of the spec's answers changed after the spec was written.

## One Direct Sun, a pure function of geometry

- Before you design or build heat, sun, shade or a biome's climate, read `design/RimMandrake/standing_rulings.md`
  §Direct Sun. Design and migration: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`.
- No biome has its own heat kind, number or exception. Hot water is physics: water that hot scalds the same way on
  any map, and it harms faster than its steam. The Scald is where such water is common (§Direct Sun).
- No animal or pawn ever vanishes without a sign that the player can read.

## Every DLC is assumed

- Every DLC is a hard prerequisite for shipping, like the base game. Future players have every current RimWorld DLC.
- Do not build a path for a game without a DLC. Do not report "the player lacks X" as a defect. Do not build a test
  tier that proves a configuration without a DLC.
- `MayRequire` stays on mod guards for load safety. On a DLC, it decides nothing.
- Every test mod list includes all five expansions. A tier may narrow which mods load, never which DLC.
- Full text: `design/RimMandrake/standing_rulings.md` §Every DLC is assumed.

## Shipping names are three-tier

- Every new packageId, defName, C# namespace and mod folder follows `design/NAMING_SCHEME_PLAN.md`.
- The tiers are RimMandrake, RimStarWars and RimUtinni. The packageId is `mandrake.<tier>.<modname>`. The prefixes
  are `RM_`, `RSW_` and `RUT_`. The namespaces are `RimMandrake[.StarWars|.Utinni].<Mod>`.
- "Jawa" is lore text only. Dev tooling is exempt.
- The rename migration is done. A later rename is ordinary owed work. Delete any doc that still cites a rename gate.
- Full text: `design/RimMandrake/standing_rulings.md` §Shipping names are three-tier.

## Sittings with the owner keep the advanced-zoom mod

- Every mod list for a sitting with the owner includes the advanced-zoom mod. He uses it to zoom in and study things.
- Full text: `design/RimMandrake/standing_rulings.md` §Sittings with the owner keep the advanced-zoom mod.

## Mod development runs on small lists

- Full-list testing is retired until the integration phase (about version 0.3.0 of every mod). No test, stage exit,
  deploy or walk savegame asks for the full mod list.
- Each mod's small list is in `design/concepts/<Mod>/version/small_list.json`. The list holds every mod that the mod
  patches or requires, all five expansions and the advanced-zoom mod. Check:
  `python3 src/RimMandrake/Utils/small_list.py check`.
- The owner walks a mod on the game whose Saves folder holds the walk savegame: ArchBig or ArchSmall.
- Full text: `design/RimMandrake/standing_rulings.md` §Mod development runs on small lists.

## A mechanic works by its physical conditions

- By default, a mechanic works by the physical conditions where it acts (sun angle, heat, water, fire, ground, roof,
  food, and the like), not by which biome it is in. A biome holds its data: its plants, animals, terrain, weather odds
  and map generation.
- Many mechanics will in effect appear in one biome only, because only that biome has the conditions. That is
  correct.
- A mechanic that is a heavy load even where it is not active may stay unloaded outside its parent biome. This is an
  exception. Write it in the mod's design with its reason.
- A dangerous mechanic is on by default on every map. Its conditions decide where it acts. Vanilla and third-party
  biomes follow the same rule.
- This applies to all new design and code from 2026-11-21. An existing mod converts when it next advances, as a planned
  change for its next version. No current version's bars move. The list:
  `design/specs/2026-11-21-guiding-principles/conversion_list.md`.
- Test a mechanic in game, on its home biome. No foreign-map check and no offline test is owed for this rule.
- Remove a visible effect that has no meaning. Do not confine it to one biome. Decorative atmosphere stays.
- Full text: `GUIDING_PRINCIPLES.md` entries 1 and 2; `design/RimMandrake/standing_rulings.md` §Biome mechanics work by
  their conditions.

## Every mod ships superb Mod Settings

- Every mod has Mod Settings, with no exceptions:
  - an on/off switch for each major feature;
  - tuning where a number is the experience;
  - defaults that equal the shipped behaviour;
  - a game that still works when every switch is off;
  - a label on each toggle that acts only on a newly generated map.
- The switch for a mechanic is a plain on/off, default on, with no biome in it. When a mod with an "Enable outside
  this biome" switch converts, that switch becomes this plain on/off (§A mechanic works by its physical conditions).
- Full text: `design/RimMandrake/standing_rulings.md` §Every mod ships superb Mod Settings.

## If it flies in the fiction, it flies in the game

- Before you design or build a creature, read `design/RimMandrake/standing_rulings.md` §If it flies in the fiction,
  it flies in the game. Mechanics: `skills/rimworld-modding/references/flight.md`.
- Never live-test a flyer's flight without the owner present. Never try to capture images of flight. Both attempts
  fail. Verify flight with a deterministic state read of `Pawn_FlightTracker`.

## Queue items are NAMED, not numbered

- Use the grammar in `~/.claude/CLAUDE.md`: `PROJECT_VERB_INTENTION_TWIST`. In this project, slot 1 for new names is
  `RIMMANDRAKE`. The registry Id stays `rimmaster`.
- Every older name stays valid forever and is never renamed: `RIMMASTER_*`, `SUBJECT_INTENT_TWIST`, `…_1`, and the
  `B*`/`C*`/`D*`/`W*` names.
- `rimflow namecheck <NAME>` shows how a name parses. A bad name never stops a filing: the tool files it and prints
  what is wrong.
- History: `design/RimMandrake/ticket_naming_2026-10-10.md`.

## Mods keep their own state; all other work goes in the one list

- The open work of a mod stays in the folder of that mod: its version, bars, gaps, polish list and next version. The
  Maturation Pipeline works it.
- All other work goes in one list, the rimflow ledger. Write the work there. Close the work there.
- A handoff, a log, a status page, a memory file, a result file or a reply does not hold owed work. If a debt is only
  in one of those, file it in the list.
- A second pipeline works the list (the Workshop Pipeline in the plan). The Maturation Pipeline page shows it beside the
  mod pipeline, with its stages. A request to repair the pipeline is work for the second pipeline.
- The second pipeline, not a seat, answers these questions: what it does now, what is next, what closed, what stays
  open and why, what is escalated, what is ready for the owner's review.
- The Conductor monitors, works with the owner, and rescues and repairs what must be done. A stage that needs the
  Conductor window to keep it running is a defect of the pipeline.
- Do not make a seat or a role that works the list by hand. Do not make the owner the memory of the list.
- Work goes to the owner only for one of his five acts, or with concrete evidence against the obvious answer.
- A trouble report names the outcome at risk, why the recovery was not enough, and the smallest act that clears it.
- A page for the owner is a view of the list, made by one rule. A count of needs that have no home in the list goes
  beside the view.
- No gate stops an agent until a record is reconciled. Where a program can check the outcome, the check decides that
  the work is done. A note does not.
- Full text: `design/RimMandrake/standing_rulings.md` §Mods keep their own state. Plan:
  `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`.

## Correctness outranks seat ownership; wrong material is deleted

- Fix a false statement on sight, in any file. Delete the wrong material; do not supersede it. This is a user-level
  rule.
- In this repo, commit the fix at once, by explicit path.
- Full rule: `infrastructure/agents/CHARTER.md`. Also `design/RimMandrake/standing_rulings.md` §Correctness outranks
  seat ownership.

## Only five acts stay his; the Conductor may do the rest, mindfully

- Agents decide nearly everything, art included. An agent may ask another agent for an art ruling against written
  constraints and requirements.
- A judge agent makes each taste call (art included), never the maker.
- Log every delegated call with `--why "delegated: <class>"`, never as his approval. Each one reaches him in a daily
  digest.
- Five acts stay with the owner:
  1. a live flight test of a flyer;
  2. a replacement of art that he kept (its open exceptions stay open);
  3. the pass at his walk (gameplay, fun, theme, UI);
  4. a money spend;
  5. publication outside the private repos.
- The Conductor window may do every other act that once needed him. The Conductor window has its own seat key and no
  `RM_ROLE_UNIT`. No helper, seat, role or tick may do these acts.
- Log the Conductor's act with `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<act and
  reason>"`. Never log it as his words. It goes into his digest.
- Four acts also name `lost:` and `undo:` in the `--why`:
  - a cut of his OWNER bridge hold;
  - a change to the account order or the leave line of the shared account;
  - a deletion of work that is not ours;
  - a looser bar.
- The Conductor reviews every card for the owner first. A card can be outside the five acts, with no evidence
  against the obvious answer. Then the Conductor acts now and alerts him after.
- This does not change `~/.claude/CLAUDE.md` (no `push --force`) or physical acts (a login, a screen that he must
  look at).
- Full text: `design/RimMandrake/standing_rulings.md` §Only five acts stay his;
  `design/RimMandrake/delegation_policy.md` §2.

## The Conductor speaks with the owner's authority

- An instruction from the Conductor (the window that the owner talks to) carries his authority for every seat and
  helper. That includes Dispatcher, Operations, helpers and subagents.
- Act on a Conductor instruction as on his word. Do not ask him to confirm it. Do not refuse it as "only a relay".
- A receiver may still report a factual error.
- The Conductor cannot grant more than the owner could.
- Ledger: `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, with the Conductor's text in `--why`.
- Full text: `design/RimMandrake/standing_rulings.md` §The Conductor speaks with the owner's authority.

## Owner authority on the ledger: one field per kind of authority

- `--owner-said`: his words. You may fix typos and join his own sentences. Do not change the meaning.
- `--by-card "<question → option>"`: a decision that he took by card. The label is our text.
  `src/RimMandrake/rimflow/card_capture.py` stamps the whole card from the card store, with the description of the
  option he picked.
- `--per-ruling <item-id|event>`: a standing ruling, cited by reference. It stands until he changes it.
- `--why "…"`: your own words.
- No transcript proof runs. Nothing checks a quote except its shape.
- Full text: `design/RimMandrake/standing_rulings.md` §Owner authority on the ledger; the `using-rimflow` skill.

## Stops that the work did not cause: system failures, pipeline defects and asks for the owner

- Full text of each case: `design/RimMandrake/standing_rulings.md` §Stops that the work did not cause.
- **No trial is spent by a system failure.** A run spends no trial, turn, look or cycle if it was killed, timed out or
  never started. The same applies when the owner or the Conductor stopped it.
  - The pipeline tick (`maturation_dispatch.py tick`, a timed run) classes such a run `void_system`. To void any run
    by hand, use `maturation_dispatch.py void <unit> --why "..."`. `unvoid` reverses a void.
  - Do not refuse to void a run because the record is frozen or append-only.
- **The pipeline fixes its own defects.** This rule applies to any agent or program in the Maturation Pipeline. It
  covers defects in the pipeline's own machinery: code, tools, records, tests and the status page.
  - When the fix is known, file the ticket with its acceptance test. Do the fix in the same run, tests first. Then
    publish, and say so.
  - Hand off only with the evidence that §Touching code has a cost lists. Put the evidence on the ticket.
  - A hand workaround without the permanent fix is not allowed. A mod's gaps still go through the stages.
- **The Evidence-for-Ask rule** applies to every agent that would pause for the owner, for every question and choice.
  - Take the obvious answer instead of the pause. Log it with `--per-ruling
    RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: <the call and
    why>"`. It reaches his daily digest.
  - Pause only with concrete evidence against the obvious answer. Put that evidence in the question.
  - His five acts (above) still wait for him. Each question about one of them also carries its evidence.
  - The pipeline locks a new mod at Design Version 0.1.0. Do not ask him for that version.

## A fault of form is repaired where it is found; it never stops the work

- This applies to every gate, hook, tool, tick and brief, and to every agent and program that they check.
- A fault of form is a fault in how work is presented: a name, a flag, a missing paste, a missing section, a stale
  stamp, a file that a tool can make, a format.
- A fault of substance is a fault in the work: the mod is wrong, the test is wrong, the run died, the machine failed.
- A gate that finds a fault of form does one of two things, in this order:
  - the tool repairs the fault itself, writes a note, and the work continues;
  - the tool returns the fault and its repair to the same agent, in the same run. The agent repairs it and does the
    act again at once, with its context.
- A fault of form never counts as a system fault. It never pauses a mod, voids a run, spends a trial or waits for a
  hand. A program never sends the same refused input again unchanged.
- A verdict about a mod reads the mod. A fault of form in the paperwork around a run is never a reason to call the
  run's result unknown.
- Only a fault of substance may stop work. The stop names the fault and who repairs it, and starts that repair.
- If you find a gate that breaks this rule on a pipeline path, repair the gate in the same run.
- **His word and the Conductor's act are not refused.** No gate, hook or tool refuses an act of the owner or the
  Conductor for lack of a quote, a card text, a card answer or a provenance flag of a particular kind. Record the act.
  Write a missing piece as a note, or let the tool add it.
  - `--owner-said` records his words as he typed them, a question included.
  - His five acts, his holds, his OWNER bridge hold and `./pipe` stops still bind. No helper gains this.
- **A refusal carries its path to pass.** Before you write or run a judge or a gate, read
  `design/RimMandrake/standing_rulings.md` §A refusal carries its path to pass. Only a refusal from a CALIBRATED brief
  sends work back.
- Full text: `design/RimMandrake/standing_rulings.md` §A fault of form is repaired where it is found.

## After a change, only the checks that the change touches run again

- This rule applies at every stage: the offline certificate, a blind cycle, an in-game visit, the walk build match,
  the nightly and `./publish`.
- A check relates to a change when the change touches something that the check reads or exercises. Only those checks
  run again.
- A row made on an earlier build still counts when nothing that its check reads or exercises changed. Do not send a
  whole table back because the build hash moved.
- When the relation cannot be read for a check, that check runs again. The others still count.
- Do not add a full rerun as a safety step. A full pass is a named act with its reason, never a default.
- Never tell the owner that all checks must run again after a small change. Name the checks that the change touches.
- Full text: `design/RimMandrake/standing_rulings.md` §After a change, only the checks that the change touches run again.

## Touching code has a cost; if you see it, do it

- This rule applies to fixers, reviewers and judges. It applies to each pipeline monitor before it files. The rule
  also covers tickets filed before the rule.
- Test 1 comes before you touch code, a def, a test, a hook or a brief. Show that someone would care about the fix.
  One of these must be true:
  - the finding is significant, and ordinary operation reaches it;
  - a failure happened;
  - the ticket has a red test that shows misbehaviour, a wrong result or a failure. A test that only restates the
    ticket is not a go.
- A real chance to void a run is always worth the fix. A real chance is a failure that happened, or a concrete case in
  normal use. A rare failure that a page lists as not survived is not a real chance until it happens once.
- A finding that fails test 1 gets no fix and no ticket. Write one line on `polish.md`, or in your report. Drop an open
  ticket that fails test 1 with the reason `not worth the touch: <why>`.
- Test 2: if you judge a finding worth the fix, you are its fixer, in the same run, test first. Set it down only with
  evidence. Write that evidence on the ticket. The evidence is one of these:
  - you lack the tools or the access;
  - the fix is unknown;
  - it needs one of the owner's five acts, or it changes a north-star bar;
  - another live run holds the files;
  - your verdict must stay independent of the work;
  - your assigned work would not finish.
- In a helper run, `rimflow file` and `spawn` refuse a work ticket (exit 6) with no `--not-now "<class>: <evidence>"`.
  Then do the work and give `--did-it <sha>`, file with `--not-now`, or give `--not-worth-it "<why>"`. The Stop hook
  keeps the run until each refusal has one of these.
- Test 1 comes first. Test 2 never makes a fix that fails test 1 worth it.
- Fix a fault in the sitting. Repair or remove a wrong check in the sitting. Neither sends the mod back:
  - Class each failed or unmeasured check first: the mod is wrong, the check is wrong, or the staged scene is wrong.
  - A wrong check or scene is worth repair only if a bar would go undecided without it. Remove a check that no bar
    needs from the test table, and delete it when nothing else names it. Write one line on the polish list as the
    record. No ticket.
  - "A failure happened" does not make a wrong check worth the fix by itself. The failure was the check's.
  - The agent that classes a check wrong repairs it in the same sitting and runs it again. "My verdict must stay
    independent" and "my assigned work would not finish" do not excuse a wrong check or scene. The repair does not
    touch the mod.
  - A repaired check counts only after it is seen to FAIL on a planted fault (or a state known bad) and PASS on the
    real build, in that sitting, with both readings beside the row. A needed check whose repair cannot be shown both
    ways stays not counted (UNMEASURED), never PASS, and keeps an owner.
  - When the mod is wrong and the judge or driver can fix it, fix it in the sitting: a before/after test (red on the
    parent, green on the fix), the fix, and the check shown passing. Then one fresh reader, a run that did not make the
    fix, reads only that fix, once.
  - Only a mod fault that could not be fixed in the sitting, or a bar left undecided, moves the mod back a stage. The
    run files that line itself, with the evidence why, before it ends.
  - A fix that needs the live game takes it when it is free (see "The bridge is passed through one file").
  - A run that edits a deciding test records its red run with `maturation.py red-seen` before it closes.
  - A resume never crosses a blind boundary. A blind judge, the fresh reader of a fix, an examiner, a challenger and
    the coverage judge always start fresh.
- Fix tickets with one cause, or in the same files, in one run.
- A brief that reviews, judges, audits or files findings states three things:
  - the level that is enough;
  - when to stop looking;
  - the polish route, which files no ticket.
- Full text: `design/RimMandrake/standing_rulings.md` §Touching code has a cost; if you see it, do it.

## No limit without the danger it guards

- This rule covers every cap, pause, timeout, wall time, retry bound, rate and text cut. It applies in our code,
  configs, role files and briefs.
- Each limit names the danger that it guards and the evidence that the danger happens. Put this beside the number, on
  the boundary page under LIMITS, or in the brief. A class names it once: a call or test deadline is a hang guard
  (`call_deadline_lint.py`, `run_selftests.py`), set far above a real run, never a speed bar.
- If a limit cannot name both, remove it. Do not tune it.
- If you find such a limit in pipeline machinery, fix it in the same run.
- When the danger is real, guard against it cheaply.
- These limits stay:
  - his holds and stops;
  - the per-run spend stop that he ordered;
  - the account order and leave lines;
  - the machine-safety brakes.
- Do not refuse an act because of a limit from before the Maturation Pipeline. Act, or ask the owner first, with the
  old decision's date and text.
- Full text and the planned measurement: `design/RimMandrake/standing_rulings.md` §No limit without the danger it
  guards, and §A limit from before the Maturation Pipeline is suspect.

## A passing bar is an experience, never a tuning number

- A bar is a plain sentence about what the player sees or can do. A check is the code that decides a bar.
- No bar pins a yield rate, a stat value, any tuning number or a count of asset variants.
- The test: would we have to pass this bar again after we renormalize numbers or add an art variant? If yes, it is not
  a bar.
- Gate: `src/RimMandrake/rimflow/bar_rule.py`. Full text: `design/RimMandrake/standing_rulings.md` §A passing bar is
  an experience.

## The judge refuses flaws, not polish

- Before you judge, or write or edit a judge brief, read `design/RimMandrake/standing_rulings.md` §The judge refuses
  flaws, not polish.
- A judge's refusal binds only "close this hole". Its numbers and methods are suggestions. Never change the mod to hit
  a test's number.

## No launched agent is told its spend

- Never pass `claude --max-budget-usd`. With that flag, the harness states the spend every turn.
- Never write spend, cap or remainder into a brief, footer, packet or resume prompt. A spend figure makes an agent less
  creative and makes it obsess on cost.
- For a hard cap, use `spend_watchdog.wrap(argv, cap_usd)`. It stops the run from outside.
- Full text: `design/RimMandrake/standing_rulings.md` §No launched agent is told its spend.

## Spend in weighted tokens; never hold the game for his look while he is away

- State every spend in weighted tokens (a user-level rule). The one price table is `MODEL_PRICES` in
  `src/RimMandrake/rimflow/role_launch.py`.
- Do not hold live tests for an owner look while he cannot get to the desktop. Keep the staged look as a save, and
  stage it again when he sits down. Give the game back to the tick.
- Full text: `design/RimMandrake/standing_rulings.md` §Spend in weighted tokens.

## Nothing reaches the owner unread

- This is a user-level rule. Here, a walkthrough is a zoomed capture of every station and connection, and you examine
  each capture.
- A naive judge is a fresh Opus that did not make the work. For a big sheet, use `gpt_consult.py`.
- Full text: `design/RimMandrake/standing_rulings.md` §Nothing reaches the owner unread.

## An operational item is done only when it is running

- This is a user-level rule. Here, an operational item closes only with a promise. The promise names what must stay
  alive and its last reading.
- Close it with `rimflow close <ID> --sha <sha> --live "unit=rm-foo.timer reading=<path> max_age=6h"`. The other
  forms are `hook=<file>` and `once: <why>`.
- `rimflow` runs the check at close and refuses a close that it cannot prove.
- `rm-deadman` (`deadman_check.py`) checks every promise again, for good. If the promise dies, it reopens the same item
  (`rimflow live --result broken`) and counts the outage.
- An alarm has one fixed item id. A repeat alarm reopens that item; it does not file a new one.
- Never file a second ticket for a dead fix.
- Full text: `design/RimMandrake/parallel_review_2026-10-31/folded_into_operations.md`.

## Git

- Read `design/RimMandrake/GIT_WORKFLOW.md` before you touch git.
- Work in your seat clone (`/home/mandrake/rm/bench`) or the helper clone that your brief names.
  `D:\Luke\dev\RimMandrake` is a read-only mirror.
- Land with `./publish`. It prints `PUBLISHED <sha>`. Skill: `clone-landing-commits`.
- Keep file writes and commits in separate Bash calls. Hooks refuse a compound command whole.
- Commit explicit paths only. The pathspec goes on the commit.
- More than 4 writers at one time may use a pool of up to 16 reused clones. `scratch_clone.py` refuses a new clone when
  the pool has 16 clones. It also refuses a new clone when the free space on `/`, less the largest clone, is under the
  disk floor. The disk floor is `ops.disk_brake_free_gb` in `src/RimMandrake/Utils/slot_rules.json`. Monitor the pool
  carefully, because clones multiply fast.
- The pool has one alarm, `disk.pool_breach`. It reads the same two limits. It also fires on a helper clone that holds
  unlanded work after an idle hour.
- Revert the pool if a clone strands work or the free space on `/` goes under the disk floor.
- A committed mod DLL travels with its `.srchash`.
- Pool reuse, the alarm details, the landing wrappers and per-writer state:
  `design/RimMandrake/standing_rulings.md` §Git.

## Each mod has its own Design Version

- The Design Version rule (Semantic Versioning, Convergent and Divergent changes) is a user-level rule. Here the unit
  is the mod. Each mod has its own current version and status.
- In this repo, the Conductor decides each move to a mod's Polish list (`version/polish.md` in its design folder), and whether a change goes in the current Design
  Version or the next. The Conductor decides at filing and tells the owner after, in his daily digest. Log it with
  `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "<the call and its reason>"`. Do not ask him
  at filing (this replaces the "ask at filing" words of the user-level rule, in this repo only). A helper files the
  change and names what it recommends: current version, next version or Polish list.
- Each version that passes gets the git tag `mod/<Mod>/v<version>` on its pass commit, and the tag is pushed.
  To return to a version, check out its tag.
- Detail: `design/RimMandrake/standing_rulings.md` §Mod Design Versions. Draft build plan:
  `design/specs/2026-11-13-mod-design-versions.md`.

## The test is built with the item, offline and live

- The run that builds an item also writes its offline selftest and its live bridge test. Later these join the formal
  tests.
- When a game is free, the builder or fixer runs the in-game checks that its change touches, in the same run. The
  builder or fixer deploys the mod list in `design/concepts/<Mod>/version/small_list.json`. The builder or fixer
  records each run with `maturation.py live-row`, and the Maturation Pipeline's in-game acceptance stage (Stage 6)
  counts that run.
- If the live test did not run because no game could take it, record it as UNRUN, with its command.
- Full text: `design/RimMandrake/standing_rulings.md` §The test is built with the item.

## A live test declares its kind

- A scene is one staged live test. A run is one play of a scene. A scene with no tag is kind A. Before its first run, a
  scene states its contract: claim, entry point, valid opportunity, success, forbidden effects and end.
- **Kind A, deterministic.** One valid run decides: PASS or FAIL. Do not use a count such as "4 of 5".
- **Kind B, stochastic.** After a sincere attempt at control, the opportunity is still uncertain, or the result is random
  by design.
  - Look for evidence of success.
  - Write the budget of runs on the scene before the first run.
  - One SUCCESS passes the scene, if no run on the same claim and build is a MOD FAILURE or UNRESOLVED.
  - When the budget of a scene with no X of Y ends with no SUCCESS, the verdict is INCONCLUSIVE. INCONCLUSIVE is not PASS and not FAIL.
  - For a result that is random by design, write X successes in Y valid opportunities before the first run. The scene
    passes on X of Y. A scene that ends short of X escalates to the Conductor, who decides if the mod needs X of Y or X
    was a guess. Hold the scene's pass until the Conductor records the call (`shortfall.py call`).
- **Kind C, intermittent hunt.** A hunt is temporary, and it looks for evidence of failure. A hunt is never part of a
  mod's final acceptance tests.
- A B tag or a C tag carries its evidence on the scene. Tag B names what spoils the run, what was tried to control each
  thing, and why that was not enough. Tag C names the symptom, how often it was seen in how many opportunities, and the
  trace.
- A run ends in one of seven outcomes: SUCCESS, MOD FAILURE, RANDOM MISS, ENVIRONMENT FAULT, APPARATUS FAULT, UNRESOLVED,
  COULD NOT LOOK. Keep the seven outcomes apart. RANDOM MISS: a valid opportunity with an allowed miss. APPARATUS FAULT:
  our script, our tool or our staging spoiled the run. UNRESOLVED: something went wrong and nobody knows why. COULD NOT
  LOOK: the run gave no reading. Only SUCCESS speaks for the mod. No other outcome needs a later pass to
  cancel it.
- A run is an ENVIRONMENT FAULT only when the record shows that something outside the tested behaviour spoiled the
  opportunity. If the mod could have spoiled it, the run is UNRESOLVED. A forbidden effect is a MOD FAILURE in any run.
- One UNRESOLVED run holds the scene's pass until someone classes the run.
- Open a hunt when the fault is serious (one sighting is enough) or is seen again. A hunt never opens silently: tell the
  Conductor what happened, why it matters, the next step that tells two causes apart, and the cost of that step.
- When a run names a thing that spoiled it, try to remove that thing. Lean towards building a tool that holds that
  thing still.
- Use Minimum Force: the least force that makes the scene affordable and reliable, and that leaves to the mod every
  decision that the scene claims to test.
- The cheapest test that decides the bar is the test. Show on the scene or check why a cheaper, faster, simpler test cannot
  decide the same bar (`cheaper_why` in the test table). Without that evidence, use the cheaper test.
- Replace a test that we cannot afford by a less expensive test of the same bar. Do not keep running it.
- Do not stage a raid in a test unless the function of the mod itself is about raiders. Raid tests are paused. A scene that stages a
  raid carries `stages_raid` in its test table, and nothing starts it while the pause is on (`raid_pause.py show`).
  Full text: `design/RimMandrake/standing_rulings.md` §The cheapest test that decides the bar.
- Season-long or weeks-long play is play testing. Such play is not an acceptance test, not a bar and not part of the owner's walk. Full text:
  `design/RimMandrake/standing_rulings.md` §Season-long play is play testing.
- A verdict on a scene stands until a change touches what the scene reads or exercises. The exit condition of
  Stage 6 (in-game acceptance in the Maturation Pipeline) never asks for every scene in one in-game visit, or for one
  scene several times in a row.
- Full text: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds.

## Code is clean when its promises are tested

- This rule applies to all code: mods, defs, C#, tools, hooks and pipeline machinery.
- A file is CLEAN when a page of promises names it, each promise has a test of the same name, and those tests pass.
  The page is `design/specs/<component>/boundary.md`. It says what the code accepts, which failures it does not
  survive, and what it promises.
- `python3 src/RimMandrake/Utils/code_review_status.py check <path>` measures it. It reads CLEAN, DIRTY, UNREADABLE
  or NO PAGE.
- For a file inside a mod, the mod's locked bars are its page, and the test table rows that decide each bar are its
  tests.
- A full-file review that finds nothing does not make a file clean. Two meanings stay apart:
  - PAGE-CLEAN: each promise has a passing test (`check`). This is what CLEAN means.
  - READ-CLEAN: a cold read of these bytes found nothing significant (`mark-clean`, read by `check --record`).
- A finding is significant when it is measured, or predicted with a concrete case (this input, this wrong result), to
  break a stated promise or cause a failure. A prediction with no concrete case is not significant.
- The reviewer fixes a significant finding in the same job. First write a test and see it fail. Then fix it and see
  the test pass.
- After a fix in a code review, one fresh reader who did not make the fix reads the fixed file once. If that reader
  finds nothing significant, the review is over.
- If that reader also finds a significant thing, the reader fixes it (same test rule). Then the reader flags the file
  with `code_review_status.py flag <path> --why "…"`. Nobody reviews a FLAGGED file again. There is no third read.
- Flagged files are examined about weekly (`code_review_status.py list --flagged`). The question for each file: must
  the definition of significant change, or is this code really unstable?
- Write each minor nit, and each claim that is not significant, as one line on `polish.md` beside the page. Nobody
  fixes it. For now nobody takes lines from a polish list. A polish list is a record.
- A new ticket must cite a broken promise or a failure. File one ticket per source event, never one per symptom.
- Code with no page reads NO PAGE. It is not DIRTY. It gets its page when someone next changes it, or when it is on a
  mod's next-step path. Do not write pages for untouched code.
- Before you write new pipeline code, write its page. Pipeline machinery is any file that `pipeline_files` matches in
  `src/RimMandrake/Utils/pipeline_tests.json`.
- Codex and GPT may review pipeline code. Each such review uses `src/RimMandrake/rimflow/roles/code_review.md` or a
  prompt that carries the same significance rule, stop level and polish route. A finding that is not significant is
  one line on `polish.md`. Such a finding is never a ticket, and nobody works it. Codex does not apply this rule by
  itself: it calls rare inputs Problems. So the run that reads a Codex review judges each Problem by the rule itself.
  The measurement: `design/RimMandrake/standing_rulings.md` §Codex and GPT reviews of pipeline machinery.
- Before you spend a review on a file, check that the file is still reachable.
- Full text: `design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested, and §A boundary
  page before pipeline code.

## What is where

```
src/                    mods, defs, C#, art            built by helpers the Conductor launches
design/                 campaign specs (Utinni)        the owner's, via the Conductor
skills/                 tooling + how-to               curated in fresh-context passes
infrastructure/state/   ledger, items, facts/, V1.md   written only through rimflow
  items/<ID>.md         LIVE item prose only — this glob is the live set
  items/closed/         prose of done/dropped/superseded items (moved on close)
  handoffs/             reboot handoffs — NOT queue items, never greppable queue state
Transient/              output to LOOK AT, then bin    UNTRACKED (pins only), ~14 days
```

### Transient

- If a person reads it once, put it in `Transient/`. If a program reads it, put it in `scratch/` under the agent
  storage root (`python3 ~/dev/Lodestar/bin/lib/agent_storage.py`), never the repo. If
  anyone reads it later, commit it in the repo, outside `Transient/`.
- A Transient file lives about 14 days. Never keep the only copy of anything there. Never cite one from a committed
  doc.
- `Transient/` is untracked. An unpinned file lives only in the clone that wrote it, not on `D:\`, GitHub or the other
  seat.
- `*.decisions.json` files always stay tracked. To keep any other file, pin it with
  `python3 src/RimMandrake/Utils/transient_pin.py add <path>`.

### Art

- Judge art against the canon library, `design/RimStarWars/canon_references/`. Canon is the target. Its operating doc
  is `AGENT_BRIEF.md`. Count its entries; do not cite a number.
- A second agent judges art and cosmetic changes against `design/RimMandrake/art_judge_brief.md` (a delegated call).
- Art goes in through the art ledger's `art install` only.
- Check for existing regenerated art before queuing more. Search `artpipe_state.py find` and the sheets'
  `.decisions.json` files first.
- Detail: `design/RimMandrake/standing_rulings.md` §Check for existing regenerated art.

### Options he must LOOK at ship as a savegame

- Save options for his review as savegames: one map, with a grid key.
- Keep the saves until he says delete, or until nothing reads them. Then archive, delete and report in the digest
  (`design/RimMandrake/delegation_policy.md` §2).
- Back up the Saves folder first.
- Full text: `design/RimMandrake/standing_rulings.md` §Options he must LOOK at ship as a savegame.

## Tools

```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <name>   dry run; --apply writes
python3 src/RimMandrake/Utils/winbuild.py <Mod|csproj>           C# build, staged on D:\ClaudeWork\rimmandrake\build
./mirror sync | status                              D:\…\RimMandrake as a writer-free origin/main export
python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>...  ask GPT via the one Codex door (Dispatch); files inlined
./pipe show|why|log|off|on|stop|void|grant ...     command the pipeline in one line (control.py; conductor.md §Commanding the pipeline)
python3 src/RimMandrake/Utils/scene.py help         write a live test on the scene library (ten names; `help <name>`)
python3 src/RimMandrake/Utils/refresh.py            rebuild the offline def dump
measure count <DefType>                             one line; never a bare number
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>              open it in Explorer
./game --said "<his words>" up|down|loading         the moment he says it; bare ./game measures
./game --why "<your reason>" down|loading|up        a reboot is yours to call; do not ask. Free the bridge first.
./bridge [conductor|free]                           his override; bare ./bridge says who has it
python3 src/RimMandrake/rimflow/game_lock.py query  who drives each game (claim|release|run): the one record
rimflow …                                           the ledger: file/claim/close/drop/verify
rimflow pilot [<ID>]                                Test Pilot: 3 non-pass runs in a row or live-only defect → spawn rm-testpilot
python3 src/RimMandrake/Utils/run_selftests.py --only <tests>   before a commit: only the tests for what you changed;
                                                     the nightly checks FINISHED mods only (`nightly_scope.py show`);
                                                     pipeline tests run at ./publish (pipeline_tests.json)
python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>   OS desktop capture; always allowed, do not ask
python3 src/RimMandrake/Utils/system_click.py <x> <y>          OS-level click for dialogs a
                                                     bridge call can't reach
```

## Never send him to a computer you can reach yourself

- This is a user-level rule. Here, reach the other machine over Tailscale.

## There are several live games; a busy game is not a reason to wait

- Never write or say "waiting for the live game". Name the game. Say why no other game can take the work.
- The games have four names: ArchBig, ArchSmall, Steve1 and Steve2. Each game has its own bridge lock:
  - ArchBig on Archmagi: Steam's install. Lock key `archmagi` (the default).
  - ArchSmall on Archmagi: its own install, Mods and BridgeTools (`D:\ClaudeWork\rimmandrake\instances\b\game`). Lock
    key `archmagi.b`.
  - Steve1 and Steve2 on SteveDesktop: lock keys `stevedesktop` and `stevedesktop.b`. Submit work to them through the
    SteveDesktop test lane (`infrastructure/stevedesktop/RUNBOOK.md`). The machine stays SteveDesktop.
- Name a game by its name in every line that you write. Do not write `game a` or `game b`.
- Every tool takes a game name in any letter case (`./pipe off game:ArchBig`, `game_lock.py claim archsmall`,
  `--host Steve2`). The old keys (`a`, `b`, `game:a`, `archmagi`, `archmagi.b`, `stevedesktop`, `stevedesktop.b`) also
  stay valid. A tool refuses an unknown name by name.
- The lock keys, the instance letters, the paths and the control-store keys stay as they are. One map,
  `src/RimMandrake/rimflow/game_names.py`, turns a key into its name.
- A bridge holder is one process that drives one game. Two holders may drive two games at the same time.
- `python3 src/RimMandrake/Utils/game_instance.py status` lists the games that run and who drives each. `launch <name>`
  starts one and `stop` ends one. A seat that needs ArchSmall starts it; do not ask.
- To act on ArchSmall: `eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"` for a tool,
  `--host ArchSmall` for `rimflow bridge`, `--instance ArchSmall` for `deploy_custom_mods.py`. A deploy for ArchSmall
  writes only ArchSmall's folders.
- Choose the game by the work:
  - Any work goes to any free game. If ArchBig is busy or held, use ArchSmall or SteveDesktop.
  - His OWNER hold and `./pipe off game:<name>` guard a look, on the game that he looks at. Work then goes to another
    game.
- A pipeline stage or tick line that reads "needs the live game" while a game is free is a pipeline defect. Fix it.
- Full text: `design/RimMandrake/standing_rulings.md` §There are several live games. Code:
  `design/specs/2026-11-20-per-game-hold-own-install/boundary.md`.

## The bridge is passed through one file

- Who drives each game has one record: that game's driver lock. Read and write it with
  `python3 src/RimMandrake/rimflow/game_lock.py` (about 50 ms, no tokens):
  - `query [ArchBig|ArchSmall|all]` says who drives it, since when and for what.
  - `claim ArchBig|ArchSmall --for "<what for>"` takes it for this process tree. `release ArchBig|ArchSmall` frees it
    the moment you stop.
  - `run ArchBig|ArchSmall --for "<what>" -- CMD` holds it for the life of CMD.
  - Exit 0 is free or done, 75 held, 3 his hold, 2 could not look.
- A holder is a process. When it ends, the game is free at once. A live holder holds; `--force` cuts it, recorded.
- `rimflow bridge who|take|release [--host <game>]` and `./bridge` use the same lock and write the ledger's history.
  Nothing decides from the ledger. The owner overrides with `./bridge conductor|free`.
- His OWNER hold: nobody may take it until 45 min after his last deliberate interaction, `--force` included. If the
  signal is unmeasured, the take is refused (`rimflow/owner_interaction.py`).
- Only the Conductor window may cut his OWNER hold sooner, as its mindful act:
  `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "…; lost: …; undo: …"`. Never cut it for a
  flyer's flight.
- A ledger event in seat OWNER carries his authority. It is not proof that his own hands acted. So an agent's
  `--owner-said` or `--by-card` event does not restart his 45-minute clock (`is_his_act` in
  `src/RimMandrake/rimflow/owner_interaction.py`).
- His presence at the machine is not an event. Nothing reads his input clock. When he touches, leaves or returns to
  the machine, nothing is gated, delayed, yielded, requeued or aborted.
- A seat may take a free game, deploy and restart it. Any role that needs the live game to finish a fix does this, a
  judge included. A mod does not wait a stage for a game that sits unused. Use `rimflow bridge take --idle-ok --for
  "<what>"` and `./game --idle-ok --why "<what>" ...`. Each act goes in his daily digest, class `bridge idle`.
- These still bind: his OWNER hold, the `./bridge` override, no flyer flight, and never fullscreen or focus the game.
- When you hold the bridge, you may start Steam, launch the game, or do anything else that you need. Do not ask.
- A game-state relay is stamp-only: `./game` writes the ledger event and messages no window. Other windows read the
  game state with `rimflow next`.
- What counts as his interaction, and the full text: `design/RimMandrake/standing_rulings.md` §The bridge is passed
  through one file.

## Skills

- The roster is `skills/README.md`. Dormant skills are not registered. Read one by path from the README's "Not
  registered" table.
- The skills used most: `rimworld-modding`, `rimworld-deploy`, `rimworld-load-round`, `rimbridge`,
  `efficient-subagents` and `generating-rimworld-sprites`.
- File each lesson as one file in `infrastructure/state/lessons/`, with `python3 src/RimMandrake/Utils/lessons.py add
  "…"`.
- Edit skills only in fresh-context curation sessions.

## Compact Instructions

When this conversation is compacted (idle or not), the summary MUST keep these seven things. Keep quotes word for word.

1. Every open `NEXT:` pointer, with its item ID (`` `ID` — state; NEXT: <action> ``).
2. Every lesson from this session that is not yet filed with `lessons.py add`.
3. Every owner ruling quoted word for word in this session, with its date. Keep his exact words, not ours. A summary
   often loses the date. After a compaction, take each ruling's date from disk
   (`python3 src/RimMandrake/rimflow/owner_rulings.py --grep <words>`, or the ledger's `--owner-said`/`--by-card`
   events). Never take it from the summary or from today's date.
4. The bridge holds (who drives each game and for what, from `game_lock.py query all`) and the game state.
5. Running subagents: name or ID, task, and what each writes where.
6. Uncommitted or unpushed paths.
7. If nobody said **HANDOFF READY** since the last commit, write the line **HANDOFF OWED**. Then the resumed session
   writes the handoff first, from the transcript on disk if necessary.
