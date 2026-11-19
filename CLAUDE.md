# RimMandrake: a RimWorld 1.6 mod project (a Jawa scavenger clan on a desert world)

This file holds rules and pointers only. Each rule's full text, the owner's words and the evidence live in the
file that the rule points at. Git holds the history. Write each entry in Simplified Technical English, with no
provenance (`design/RimMandrake/standing_rulings.md` §The root CLAUDE.md holds rule lines and pointers only).

## Read these first

- `PURPOSE.md` says what this repo is. It is an experimental agent software factory, and its product is a game.
  The owner uses it to test ideas about agents, factories and orchestration. The game domain has low risk and is easy
  for a person to read. So agent behaviour here is easy to understand and to trust.
- `infrastructure/agents/CHARTER.md` is the full process rulebook.
- Read your own window file. The Conductor (the window that the owner talks to) reads
  `infrastructure/agents/CONDUCTOR.md`.
- The Conductor launches builds directly, as helpers. The earlier pipelines are retired.
  `design/RimMandrake/retired_eras_index_2026-11-18.md` lists what they left and where git keeps it.
- The game cycle is in `infrastructure/GAME_STATE_WORKFLOW.md`.
- The model ladder is in `infrastructure/agents/Agent_Policy.md` and nowhere else. Do not restate it.

## Where the full text lives

| topic | full text |
|---|---|
| biome, roster, sea and naming-tier rulings | `design/RimMandrake/biome_rulings.md` |
| north star, LLM transport, pits, DLC, git, code review, art, bridge, savegame options, delegation, pipeline, judges, spend | `design/RimMandrake/standing_rulings.md` |
| measurements and owner words moved out of this file | `design/RimMandrake/CLAUDE.history.md` |
| instruments that return a confident wrong number | `infrastructure/state/facts/instrument_traps.md` |
| tools with surprising side effects | `infrastructure/state/facts/tool_traps.md` |
| creature flight (stat, race flags, flip-book) | `skills/rimworld-modding/references/flight.md` |
| ticking, `MayRequire`, csproj, patch behaviour | `skills/rimworld-modding/references/project-engine-facts.md` |

## How we debug

- Every mod has a functional script. Debug the mod through that script.
- Each live debug session ends with an update to that script. Write what the session learned, false theories included.
- Agents write and approve these scripts. Every new mod ships with its first script.
- Agents may add regression checks and new north-star bars (`design/RimMandrake/delegation_policy.md` §1).
- Only the Conductor may loosen a bar, as a mindful act (see "Only five acts stay his" below).
- Process: `design/RimMandrake/debug_process.md`. The build pause and its end: `infrastructure/agents/CHARTER.md`.

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
- If you are about to report one of our biomes on zero tiles, stop. It is the expected state.
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

- Search `src/` and the roster before you file or design a new thing.
- Name the greatbole that you mean:
  - `RM_Greatbole` is the tree that you can fell.
  - `RUT_GreatboleHeartwood` is the blob that you can mine.
  - `RUT_GreatboleCore` is a 1×1 marker for bookkeeping.
- An animal belongs to one biome, unless an in-game reason says otherwise. Fill a hole in a roster with a new creature.
- Evictions from a roster are stopped. No pass edits a roster to enforce the one-biome rule. A species with more than one home is a
  row on that biome's own review sheet, at that biome's sitting.
- If each new question to the owner adds a clause to a procedure, stop. That work is human review work: put the cases
  on a review sheet.
- A sea biome describes its floor and its catch: the animals you meet there and what you can fish there. Only
  fish-sized creatures owe a catch.
- In every sea, all fishable creatures are alive and move in the depths.
- The ship is the only way down to the seabed and back. The ship flies to its own planet layer, `RM_SeabedLayer`.
  `RM_SeaDiveHatch` is a leftover (`SEA_DIVE_HATCH_REMOVE_1`).
- Every BiomeDef with a roster sets `animalDensity`. An unset value is 0, and then no animals ever spawn.
- Parse `<wildAnimals>` and `<wildPlants>` as XML elements. Do not count `<li>` tags.
- A review sheet's `cut` applies to that sheet's biome only, never to the planet.
- An `RM_` twin biome gets its real cast from patches (`UtinniPatches/Patches/WildAnimals_<Biome>.xml`). If you read
  only the BiomeDefs, you see the wrong half.
- Full text: `design/RimMandrake/biome_rulings.md`.

## Star Wars style naming is not Star Wars IP

- An invented exotic name lives in the franchise-free `RM_` tier. Only a real canon name is IP, and it goes through the
  Utinni patch layer.
- An `RM_` roster can stand alone. It is never a thin fallback.
- When a tier or provenance question makes more sub-questions, first ask if the category is necessary at all.
- A donor mod's defName is not a canon source. Check canon with the Wookieepedia search API.
- Authority: `design/RimMandrake/biome_mod_architecture.md` §7 Q11a (a name that only sounds like Star Wars is not
  IP). Full text: `design/RimMandrake/biome_rulings.md`.

## Facts you cannot guess

- The game reads `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, never this repo. A file that you write
  here is not deployed.
- A cold load on the full mod list takes many minutes. A quicktest map takes about 90 s. So never restart the game
  only to look at the result. The figures: `design/RimMandrake/CLAUDE.history.md` and the `rimworld-load-round` skill.
- `ModsConfig.xml` is the live mod list. It describes the next load. Its path is
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`.
- To count active mods, parse ModsConfig (`ET.parse(p).find("activeMods")`). Do not `grep` it. Do not use a mod count
  from a doc.
- Do not restore the owner's mod list. Leave ModsConfig on the tier that serves your work. There is no "restore before
  release" step.
- Only the canonical world saves are precious (`infrastructure/state/CANONICAL_SAVE.md`). All other saves are
  disposable.
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
- Some tools have surprising side effects (subagent watchdog, mid-session hooks, card gates, `handoff.py`, two
  Conductor windows). Read `infrastructure/state/facts/tool_traps.md`.
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

- Every in-game LLM call runs `claude -p "<prompt>"` as a subprocess. It uses the claude.ai login and needs no API key.
- The spec has two laws. The LLM has authority over text and menus only. The game is complete when the LLM is absent.
- Detail: `design/RimMandrake/standing_rulings.md` §In-game LLM access. Spec:
  `design/RimMandrake/llm_ingame_wiring_spec.md`.

## A pit is a superdeep cell, not a building

- The authority is the item `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.
- Do not act on the 1127-line spec `design/RimMandrake/pit_superdeep_collapse_spec.md` before you read the item. Ten
  of the spec's answers changed after the spec was written.
- Summary: `design/RimMandrake/standing_rulings.md` §A pit is a SUPERDEEP cell.

## One Direct Sun, a pure function of geometry

- Direct Sun is one model. It feeds vanilla heat: felt temperature, then Heatstroke.
- Its value is 55 °C at the zenith × sin(sun angle). The sun angle comes from the tile's position on the planet.
- No biome has its own heat kind, number or exception. Low sun is less intense and casts longer shade. High sun is
  more intense and leaves only covered shade.
- Ambient heat follows normal RimWorld rules. Volcanic, steam and fog heat is plain air temperature.
- Shade gear is parasols and roofs. A tent is any quick roof.
- No animal or pawn ever vanishes without a sign that the player can read.
- Direct Sun runs the same on every day-side map only with a good tree shade model. Without that model, Direct Sun is
  off on maps with many trees, which the owner calls inferior. The model:
  `design/RimMandrake/tree_shade_model_2026-10-19.md`.
- Full text: `design/RimMandrake/standing_rulings.md` §Direct Sun. Design and migration:
  `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`.

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

## Every mod ships superb Mod Settings

- Every mod has Mod Settings, with no exceptions:
  - an on/off switch for each major feature;
  - tuning where a number is the experience;
  - defaults that equal the shipped behaviour;
  - a game that still works when every switch is off;
  - a label on each toggle that affects worldgen.
- We promise biome mechanics only inside our own biomes. Do not build a new cross-biome switch. The existing ones stay,
  switched off, with an "unsupported" label.
- Full text: `design/RimMandrake/standing_rulings.md` §Every mod ships superb Mod Settings.

## If it flies in the fiction, it flies in the game

- When a creature flies in its fiction, make it a real flyer where we can. Do this when you touch its def, not in a
  sweep.
- Flight is the `MaxFlightTime` STAT (Core, not a donor). The animation is a whole-body directional flip-book
  (`flyingAnimationFramePathPrefix`). Never use a Spastic wing render-tree.
- Mechanics: `skills/rimworld-modding/references/flight.md`.
- Never live-test a flyer's flight without the owner present. Never try to capture images of flight. Both attempts
  fail.
- Verify flight with a deterministic state read of `Pawn_FlightTracker`. A visual check happens in a joint session, or
  it waits.
- Full text: `design/RimMandrake/standing_rulings.md` §If it flies in the fiction, it flies in the game.

## Queue items are NAMED, not numbered

- Use the grammar in `~/.claude/CLAUDE.md`: `PROJECT_VERB_INTENTION_TWIST`. In this project, slot 1 for new names is
  `RIMMANDRAKE`. The registry Id stays `rimmaster`.
- Every older name stays valid forever and is never renamed: `RIMMASTER_*`, `SUBJECT_INTENT_TWIST`, `…_1`, and the
  `B*`/`C*`/`D*`/`W*` names.
- `rimflow namecheck <NAME>` shows how a name parses. `file` and `spawn` refuse a name that does not parse.
- `rimflow` reads the registry from `$LODESTAR_ROOT/sync/registry.md` (default `~/dev/Lodestar`). If it cannot read
  the registry, the refusal names that path.
- History: `design/RimMandrake/ticket_naming_2026-10-10.md`.

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
  helper. That includes Dispatcher, Operations, RUNNER, helpers and subagents.
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

## The Evidence-for-Ask rule

- This rule applies to every agent that would pause for the owner, for every question and choice.
- Take the obvious answer instead of the pause. Log it with `--per-ruling
  RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME --why "delegated: evidence-for-ask: <the call and why>"`.
  It reaches his daily digest.
- Pause only with concrete evidence against the obvious answer. Put that evidence in the question.
- His five acts (above) still wait for him. Each question about one of them also carries its evidence.
- The pipeline locks a new mod at Design Version 0.1.0. Do not ask him for that version.
- Full text: `design/RimMandrake/standing_rulings.md` §Evidence-for-Ask.

## A limit from before the Maturation Pipeline is suspect

- Do not refuse an act because of a limit from before the Maturation Pipeline. Act, or ask the owner first.
- If you ask, quote the old decision's date and text.
- Full text: `design/RimMandrake/standing_rulings.md` §A limit from before the Maturation Pipeline is suspect.

## The pipeline fixes its own defects

- This rule applies to any agent or program in the Maturation Pipeline. It covers defects in the pipeline's own
  machinery: code, tools, records, tests and the status page.
- When the fix is known, file the ticket with its acceptance test. Do the fix in the same run, tests first. Then
  publish, and say so.
- Hand off only when the fix is unknown, is outside your tools, or would change a north-star bar. Put the evidence on
  the ticket.
- A hand workaround without the permanent fix is not allowed.
- A mod's gaps still go through the stages.
- Full text: `design/RimMandrake/standing_rulings.md` §The pipeline fixes its own defects.

## No trial is spent by a system failure

- A run spends no trial, turn, look or cycle if it was killed, timed out or never started. The same applies when the
  owner or the Conductor stopped it.
- The pipeline tick (`maturation_dispatch.py tick`, a timed run) classes such a run `void_system`. To void any run by
  hand, use `maturation_dispatch.py void <unit> --why "..."`. `unvoid` reverses a void.
- Do not refuse to void a run because the record is frozen or append-only.
- Full text: `design/RimMandrake/standing_rulings.md` §No trial is spent by a system failure.

## No limit without the danger it guards

- This rule covers every cap, pause, timeout, wall time, retry bound, rate and text cut. It applies in our code,
  configs, role files and briefs.
- Each limit names the danger that it guards and the evidence that the danger happens. Put this beside the number, on
  the boundary page under LIMITS, or in the brief.
- If a limit cannot name both, remove it. Do not tune it.
- If you find such a limit in pipeline machinery, fix it in the same run.
- When the danger is real, guard against it cheaply.
- These limits stay:
  - his holds and stops;
  - the per-run spend stop that he ordered;
  - the account order and leave lines;
  - the machine-safety brakes.
- Full text and the planned measurement: `design/RimMandrake/standing_rulings.md` §No limit without the danger it
  guards.

## A passing bar is an experience, never a tuning number

- A bar is a plain sentence about what the player sees or can do. A check is the code that decides a bar.
- No bar pins a yield rate, a stat value, any tuning number or a count of asset variants.
- The test: would we have to pass this bar again after we renormalize numbers or add an art variant? If yes, it is not
  a bar.
- Gate: `src/RimMandrake/rimflow/bar_rule.py`. Full text: `design/RimMandrake/standing_rulings.md` §A passing bar is
  an experience.

## The judge refuses flaws, not polish

- A judge turns away incomplete work. A judge does not turn away work only because it is not tuned to perfection.
- Four rules:
  1. Refuse only for one of three flaws. Quote the promise. Everything else is advice. The three flaws:
     - a promise not kept;
     - a broken promise that nobody would notice;
     - a test or file that is itself wrong.
  2. Do one full inspection, then one check of the repairs, by reading the fix. Then the owner gets the short list.
  3. A refusal binds only "close this hole". Its numbers and methods are suggestions. A number binds only if the owner
     said it. Never change the mod to hit a test's number.
  4. A Designer "must not read as" line is a tip, not a thing to test. The exception is a line that is his words or
     the plain opposite of the promise.
- Two settings (the dials) can change: who confirms a refusal, and the number of looks. The number of looks starts
  at 2.
- These rules bind only after the judge prompt is edited and recalibrated.
- Full text: `design/RimMandrake/standing_rulings.md` §The judge refuses flaws, not polish.

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
- Sheet tools refuse to run without `<stem>.prereview.json` (`src/RimMandrake/Utils/art/prereview.py`).
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
- Commit explicit paths only. The pathspec goes on the commit. Never use `git add -A`, `git add .` or `git commit -a`
  (`block_blanket_git_stage.py` refuses them).
- `git worktree` is off (`block_worktrees.py`).
- More than 4 writers at one time may use a pool of up to 16 reused clones and 80 GB. `scratch_clone.py` refuses a new clone past
  those limits. Monitor the pool carefully, because clones multiply fast.
- The pool has one alarm, `disk.pool_breach`. It also fires on a helper clone that holds unlanded work after an idle
  hour.
- Revert the pool if a clone strands work or the pool passes 80 GB.
- A committed mod DLL travels with its `.srchash`.
- Pool reuse, the alarm details, the landing wrappers and per-writer state:
  `design/RimMandrake/standing_rulings.md` §Git.

## Each mod has its own Design Version

- The Design Version rule (Semantic Versioning, Convergent and Divergent changes) is a user-level rule. Here the unit
  is the mod. Each mod has its own current version and status.
- Detail: `design/RimMandrake/standing_rulings.md` §Mod Design Versions. Draft build plan:
  `design/specs/2026-11-13-mod-design-versions.md`.

## The test is built with the item, offline and live

- The run that builds an item also writes its offline selftest and its live bridge test. Later these join the formal
  tests.
- If the live test did not run, record it as UNRUN, with its command.
- Full text: `design/RimMandrake/standing_rulings.md` §The test is built with the item.

## A refusal carries its path to pass

- Every judge or gate refusal is a refusal record. It holds the evidence, `would_pass`, `smallest_fix`, and a verdict
  on the criterion.
- A refusal is as detailed as the evidence that it rejects. It gives fixes and paths to a pass that are reasonable to
  attain.
- A flawed criterion goes to the neutral fixer, never to the builder.
- Only a refusal from a CALIBRATED brief sends work back.
- If nothing could ever pass, that is the `REFUSAL_NOTHING_COULD_EVER_PASS` alarm.
- Full text: `design/RimMandrake/standing_rulings.md` §A refusal carries its path to pass.

## Code isn't clean until a review says so

- Every file is DIRTY until `python3 src/RimMandrake/Utils/code_review_status.py check <path>` says CLEAN. The check
  uses a content hash.
- Use `mark-clean` only after a full-file review finds nothing.
- Before you spend a review on a file, check that the file is still reachable.
- Procedure: `design/RimMandrake/standing_rulings.md` §Code isn't clean until a review says so.

### Pipeline machinery is under a different rule

- Pipeline machinery is any file that `pipeline_files` matches in `src/RimMandrake/Utils/pipeline_tests.json`.
- Before you write new pipeline code, write its one-page list: `design/specs/<component>/boundary.md`. The page says
  what the code accepts, which failures it does not survive, and what it promises. Each promise gets a test of the
  same name.
- Pipeline code is clean when every promise on its page has a test and the code has had two looks. The two looks are
  one full inspection against the page and one check that reads only the repairs. A later edit stays clean while those
  tests pass. A full-file review that finds nothing is not the bar for pipeline code.
- Fix a review claim only if it breaks a promise on the page. Write each other claim as one line on `polish.md` or
  `next_version.md` beside the page.
- Codex and GPT reviews of pipeline code stay stopped until a calibrated review brief exists. The owner stopped them.
- Full text: `design/RimMandrake/standing_rulings.md` §A boundary page before pipeline code.

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

- If a person reads it once, put it in `Transient/`. If a program reads it, put it in `/tmp`, never the repo. If
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
python3 src/RimMandrake/Utils/gpt_consult.py "q" -f <file>...  ask GPT via Codex (Archmagi/WSL: Linux default; --codex win); files inlined
./pipe show|why|log|off|on|stop|void|grant ...     command the pipeline in one line (control.py; conductor.md §Commanding the pipeline)
python3 src/RimMandrake/Utils/refresh.py            rebuild the offline def dump
measure count <DefType>                             one line; never a bare number
python3 skills/rimworld-modding/scripts/validate_patch.py <path> --defs ...
./src/RimMandrake/Utils/show.sh <path>              open it in Explorer
./game --said "<his words>" up|down|loading         the moment he says it; bare ./game measures
./game --why "<your reason>" down|loading|up        a reboot is yours to call; do not ask. Free the bridge first.
./bridge [conductor|free]                           his override; bare ./bridge says who has it
rimflow …                                           the ledger: file/claim/close/drop/verify
rimflow pilot [<ID>]                                Test Pilot: 3 non-pass runs in a row or live-only defect → spawn rm-testpilot
python3 src/RimMandrake/Utils/run_selftests.py --only <tests>   before a commit: only the tests for what you changed;
                                                     the nightly checks FINISHED mods only, and is held until one
                                                     passes (`nightly_scope.py show`);
                                                     pipeline tests run at ./publish (pipeline_tests.json)
python3 src/RimMandrake/Utils/system_screenshot.py <out.bmp>   OS desktop capture; always allowed, do not ask
python3 src/RimMandrake/Utils/system_click.py <x> <y>          OS-level click for dialogs a
                                                     bridge call can't reach
```

## Never send him to a computer you can reach yourself

- This is a user-level rule. Here, reach the other machine over Tailscale.

## The bridge is passed through one file

- One window drives the live game at a time. `infrastructure/state/BRIDGE` records who holds the bridge.
- Write that file only with `rimflow bridge who | take --for "<what for>" | release`. Release the bridge the moment
  you stop.
- The lock errs toward allowing. A hold with no event for 45 minutes is stale: take it. `take --force` works on any
  seat's hold.
- The owner overrides with `./bridge conductor|free`.
- His OWNER hold: nobody may take it until 45 min after his last deliberate interaction, `--force` included. If the
  signal is unmeasured, the take is refused (`rimflow/owner_interaction.py`).
- Only the Conductor window may cut his OWNER hold sooner, as its mindful act:
  `--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why "…; lost: …; undo: …"`. Never cut it for a
  flyer's flight.
- A ledger event in seat OWNER carries his authority. It is not proof that his own hands acted. So an agent's
  `--owner-said` or `--by-card` event does not restart his 45-minute clock (`is_his_act` in
  `src/RimMandrake/rimflow/owner_interaction.py`).
- `host_guard` applies the same rule across clones: a live OWNER lock takes no `--force` without the verdict of the
  `rimflow` cli.
- His presence at the machine is not an event. Nothing reads his input clock. When he touches, leaves or returns to
  the machine, nothing is gated, delayed, yielded, requeued or aborted.
- A seat may take the bridge when the bridge is free, ours, or stale by the 45-minute rule. Then it may also deploy
  and restart the game. Use `rimflow bridge take --idle-ok --for "<what>"` and `./game --idle-ok --why "<what>" ...`. Each act goes
  in his daily digest, class `bridge idle`.
- These still bind: his OWNER hold, the `./bridge` override, no flyer flight, and never fullscreen or focus the game.
- When you hold the bridge, you may start Steam, launch the game, or do anything else that you need. Do not ask.
- A game-state relay is stamp-only: when a seat runs `./game`, the command writes the ledger event and messages no
  window. Other windows read the game state with `rimflow next`. A message to each window uses tokens and rarely
  informs.
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
4. The bridge holds (who holds `infrastructure/state/BRIDGE`, and for what) and the game state.
5. Running subagents: name or ID, task, and what each writes where.
6. Uncommitted or unpushed paths.
7. If nobody said **HANDOFF READY** since the last commit, write the line **HANDOFF OWED**. Then the resumed session
   writes the handoff first, from the transcript on disk if necessary.
