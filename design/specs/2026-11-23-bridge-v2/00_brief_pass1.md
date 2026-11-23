# BRIDGE v2.0, design pass 1: what live testing needs from the bridge

You are the first of two Fable designers. The owner asked for your full powers on this one, and authorized a large spend.
His words, whole, are on your item: `python3 src/RimMandrake/rimflow/cli.py show RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE`.
Read them first, twice. His frame: "BRIDGE is the limiting reagent to all live testing."

"The bridge" is how an agent drives a running RimWorld from outside: RimBridgeServer (a GABP server inside the game) and
our companion DLL JawaBench with its `[Tool]` methods, plus the Python that calls them. A live test today is a script
that calls bridge tools one at a time and reads results.

## Your question: WHAT do we need? (not how to build it)
Design the capabilities that live testing needs, as completely as we can understand them today. The second designer,
after you, reads the existing bridge code and your design, and decides how to build it (rebuild or improve). So do NOT
let the existing code shape your design. You may read the bridge's tool list and skills to learn what exists and what
it cannot do; do not design around its present structure, and do not judge its code.

## Read first
- `design/specs/2026-11-23-three-test-kinds/rule_draft3.md` (the testing policy this bridge must serve: the scene
  contract, the seven run outcomes, kinds A, B and C, Minimum Force, the calm test environment), then `draft.md` beside
  it for his words, then `gpt_review.md` section 5 ("ENVIRONMENT CONTROL IN RIMWORLD 1.6", with its six bridge priorities)
  and section 3 (how a program, not an agent, establishes success and classes an environment fault).
- `GUIDING_PRINCIPLES.md`, and CLAUDE.md sections "A mechanic works by its physical conditions", "If it flies in the
  fiction, it flies in the game", "There are several live games", "The bridge is passed through one file".
- Skills, by path: `skills/rimbridge/SKILL.md`, `skills/rimbridge-companion/SKILL.md`,
  `skills/live-debugging-proof-harness/SKILL.md`, `skills/rimworld-live-review/SKILL.md`,
  `skills/rimworld-load-round/SKILL.md`, `skills/rimworld-modding/references/flight.md`,
  `~/dev/MandrakeWorkflows/skills/test-pilot-sitting/SKILL.md`, `~/dev/MandrakeWorkflows/skills/efficient-subagents/SKILL.md`.
- Facts: `infrastructure/state/facts/instrument_traps.md`, `infrastructure/state/facts/tool_traps.md`,
  `infrastructure/state/lessons/` (search it; do not read it whole).
- RimWorld 1.6 itself: read game code through RimSage (`mcp__rimsage__*`) wherever a claim about the engine decides a
  design choice (the storyteller and incident queue, `Rand` and its state, the tick loop, the pathfinder's scheduled
  work, save and load, `Pawn_FlightTracker`). Do not guess a class, field or method name.

## Part 1: the census (measure before you design)
Find EVERY environment influence that spoiled a live test, a proof run, a visit or an owner look in this project, and
those that still do. Sources: each mod's `design/concepts/<Mod>/version/in_game/visit_*/SUMMARY.md`, `strange.jsonl`,
`polish.md` and journals; test-pilot PROGRESS files; the lessons and facts above; closed and open rimflow items
(`rimflow` search by words such as invalid, flaky, wandered, visitor, raid, starved, mental break, weather, unmeasured,
harness, SITE, staging fault); the SteveDesktop test lane's INVALID jobs; conductor log lines about voided or rerun
visits. Use helpers for this sweep (see Helpers). For each influence record: what it was, where it was seen (path),
how often (a count where one can be measured, else "seen at least N times"), what it cost, how it was handled then,
and whether that handling was a control, a workaround or nothing.
Then HYPOTHESIZE the influences that the mods we are building will bring. Read the mod list of the pipeline (`./pipe show`)
and each mod's design: FlowWorks (pits, liquids, canals, bridges, raids crossing them), Pyrelands (fire, heat, flyers,
titans), Explosive Knockback (blasts, thrown things), Gimme Some Slack (wires, power), Contagion, Cauldron, Stillsand,
Fever Wood, Gelatinous Slime, Leaning Scrub, Graffiti, Wrecked Machines and droids (Droidworks), Machine Looks, Cold
Storage, the Bazaar trade window, the in-game LLM wiring. For each, say what a live test of it will need to hold still,
to force, and to observe.
State the census's own blind spots: what you could not look at, kept apart from "looked and found none".

## Part 2: the design
Design the full set of capabilities. At least these areas; add any that the census shows:
1. **Environment control.** A named calm test environment that is switched on in one call, reports which controls
   armed and which could not, detects and reports breaches while a scene runs, takes per-scene exceptions (a scene that
   IS about a raid allows that raid and nothing else), and is restored afterwards. Cover: storyteller incidents and the
   incident queue, quests and scripted events, weather and game conditions, temperature, time of day and season, needs,
   mental states, inspirations, wild animals and their replenishment, visitors and traders, faction relations, fire,
   plant growth, other mods' spawners and tickers. For each, say what can be held, what can only be watched, and what
   is unknown until the engine is read.
2. **Scene preparation.** Build a known start state fast: a clean map or region, terrain, structures, things, pawns with
   exact health, gear, skills, traits, faction and position; isolation of one scene from the next on a shared map;
   a "start state twin" beside each aftermath station for the owner's walk (his request of 2026-11-23).
3. **Reassert the environment easily, cheaply and swiftly.** One call that checks every declared condition and repairs
   what drifted, before a run and between repeats. Its cost budget in milliseconds and in tool calls.
4. **Confounder sweep.** A scan that, before and during a scene, looks for anything that could spoil it: pawns, jobs,
   reservations, incidents queued, hediffs, other mods' objects in the scene's cells, errors in the log. It names what
   it found in the words of the scene contract.
5. **Guiding and forcing, by the Minimum Force ladder.** For colonists, enemies, animals, mechanoids and droids: place,
   hold in place, give a path, give a job through the normal job-giver, lure with bait, set a duty or lord, and say for
   each which production decisions of the game and of our mods it steps past. The bridge records the level of force
   that a scene used.
6. **Scripted in-game telemetry.** The agent sends a small program or declarative probe that runs INSIDE the game on
   the simulation thread and captures what cannot be seen from outside: per-tick state of named things, events (a
   damage, a job start and end, a reservation, a spawn and despawn, a region or room change, an exception), with stable
   entity ids and tick stamps, bounded in size, surviving the failure it watches for. Consider the telemetry that exists
   today. Design the hard cases explicitly: a flyer's flight and its flapping animation frame by frame (the owner:
   "dare I say it, even a flapping bird test? yes!"; today flight is verified only by a state read of
   `Pawn_FlightTracker` and never by image), a thing in mid-air during a throw, a one-tick event, a draw-time-only
   effect (what is drawn, not what the state says), a UI window's content, sound.
7. **Atomic scene execution.** One call that takes a whole scene (prepare, verify the valid opportunity, arm probes,
   act, advance until a predicate or a tick limit, evaluate the contract, return paused) and returns a compact receipt
   with one of the seven run outcomes of the policy. No tool round-trip inside the deciding window.
8. **Fast repeats for kind B and kind C.** Repeat one scene many times cheaply: snapshot and restore of game state
   (full save and load, a partial snapshot of a region, or a rollback), `Rand` state capture and replay for diagnosis,
   many copies of one scene side by side on one map (the owner already reviews matrices), running at high tick rate
   with no rendering. Say honestly what determinism can and cannot be promised with about 300 mods loaded, and how a
   replay is told apart from a new sample.
9. **Receipts and identity.** What the game actually loaded (assemblies and their hashes, mod list, settings, DLC),
   the scene and checker versions, the controls that were on.
10. **Errors and safety.** Capture of the first exception; a broken game is detected and reported, never left running;
    the owner's game is never focused or made fullscreen; nothing unpauses while he watches.
11. **Authoring cost.** How a mod builder writes a scene and its contract in minutes, how a program reads the result,
    and what the builder never has to learn. A scene language or schema, with two or three worked examples from real
    scenes of ours (the spared carrier in a blast; a raider rescued from a pit; a flyer taking off).
For every capability state: what it is for (which scenes, which outcomes of the policy it makes decidable), how you
would know it works (an acceptance check in one sentence), and its value against its build effort in three levels.
Then rank: the first ten capabilities to build, by stability gained per unit of effort, with your reasons.
Name what you chose NOT to design and why (the testing horizon).

## Method
- Solve the hard parts on paper against the real engine before you assert them. Mark each engine claim as read (with
  the symbol you read) or guessed (with a rough confidence).
- Give at least three genuinely different shapes for the two hardest areas (in-game telemetry, fast repeats) with what
  each buys and costs, then pick one.
- Use GPT as a skeptical reviewer when a section is drafted: `python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file <f> -f <file>`
  (web-enabled; ask it for RimWorld 1.6 engine facts and for what the Multiplayer mod had to do for determinism). Two
  or three rounds at the points where they help you most. Fold in what holds; say what you rejected and why.
- You touch NO code and NO game. This run writes design text only.

## Helpers
You may run up to six helpers of your own at a time, for the census sweep and for reading the engine: Sonnet for
searches and censuses, Opus for judgment. Each gets a narrow brief, the paths to read, and a report limit of 300 words
with file paths as evidence. Helpers start no helpers. No Fable helpers. Keep your own context for the design.

## Output
- `design/specs/2026-11-23-bridge-v2/01_census.md` (the influences, measured and hypothesized, with evidence paths)
- `design/specs/2026-11-23-bridge-v2/02_needs_design.md` (the design; plain words; a person who has never seen the
  bridge can follow it; every coined term says what the thing does)
- `design/specs/2026-11-23-bridge-v2/03_open_questions.md` (what the second designer and the owner must decide; for the
  owner, only real choices, each with what it buys and costs)
- Write the skeleton of each file first and publish it, then fill it: a run that is silent for long loses its work.
  Commit explicit paths only and land with `./publish` after each major part. End commit messages with
  `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`.
- Leave a `rimflow note` on your item with the sha when the design is complete. Do not close the item: the Conductor
  reads the design first.

## Report (under 300 words)
The three files and the sha; the ten most damaging influences from the census with their counts; the ten capabilities
you rank first; the two hardest design choices and what you picked; what GPT changed; what is guessed, not read; what
you could not look at.
