# Fast testing: the OUTSIDE view (divergent, phase 1 of 3)

Owner ask 2026-11-05 (verbatim in the brief): get MUCH faster at in-game testing and playtesting; test at
the speed of the bridge/game/Python, not of LLM generations; literature search; as many NEW ideas as
possible; small fast judgment models "playing the game" via the Bridge (the Doom precedent).

This file: external precedents (section 1, with links in section 3) and 42 generated concepts (section 2).
Divergent pass: nothing here is scored or selected. The inside measurements are in the sibling
`ideas_inside.md`.

Method note: WebSearch/WebFetch were not loadable in this session (ToolSearch found no such tools), and the
DuckDuckGo/Bing HTML endpoints served bot walls. Research went through the GitHub search API, the arXiv
API and direct fetches; every URL in section 3 was fetched and returned HTTP 200 on 2026-11-05 (titles of
the arXiv and blog links checked). Claims about a source marked (recalled) come from background knowledge
and were not re-read today.

## 1. Precedents by area

### 1.1 Game test automation practice

- **Factorio (Wube).** Deterministic lockstep simulation, which gives you replays and desync detection for
  free. Thousands of scripted integration tests run headless on every commit on a build/test server
  (FFF-62 "The automation of Factorio"); GUI tests too (FFF-366 "The only way to go fast, is to go
  well!"). Key ideas: the test is a tiny map plus a scripted sequence plus an assertion, run with no
  rendering, at many times real speed, many in parallel. Determinism means a failing test reruns exactly.
- **Minecraft GameTest framework.** A test is a saved *structure* (a small block arrangement) plus a
  script. The framework lays many structures out in a grid in ONE world, runs them all at once on the
  same tick loop, and each one asserts within a tick timeout (`succeedWhen`, `assertBlockPresent`,
  `runAtTickTime`). This is the closest precedent to "batch many proofs per load".
- **Unreal Automation / Functional Tests / Gauntlet.** Functional tests are actors placed in a test map
  that run in-world and report. Gauntlet is the session orchestrator: it launches builds (client, server,
  headless), deploys, drives a test controller inside the game, collects logs and artefacts, and gives a
  verdict. Split of roles: orchestrator outside, controller inside.
- **Unity Test Framework (EditMode vs PlayMode) and Automated QA.** PlayMode tests are coroutines that
  `yield` frames inside the running player; Automated QA records UI input and replays it. `-batchmode
  -nographics` for CI. ML-Agents (Unity) trains agents through a Python gym-like API with time scaling
  (`time_scale` 20-100x) and many parallel env instances.
- **Godot GUT.** In-engine unit test runner with `simulate()` to step frames and `wait_frames`, doubles
  and spies on engine objects, CLI headless runs.
- **Roblox TestEZ / jest-lua.** BDD-style specs run inside the engine's Lua VM.
- **Riot (League of Legends).** ~100,000 test cases a day; a large share are scripted functional
  tests that drive the real game client/server with bots, plus a dedicated test-tools team.
- **EA SEED.** Imitation learning from a few minutes of human play to produce test bots (concurrent
  actions); curiosity-driven RL to maximise map coverage (arXiv 2103.13798); "Augmenting automated game
  testing with deep RL" (2103.15819); and a production report on adding RL to an existing scripted-bot
  testing system on Battlefield 2042 and Dead Space (2307.11105) — the lesson: scripted bots carry the
  load, RL adds coverage at the edges, and most of the time sink is environment plumbing.
- **Ubisoft / Massive (The Division).** GDC talk: AI-controlled players run gameplay feature tests
  overnight on many machines (GDC Vault 1026382).
- **King (Candy Crush).** Agents trained on player data predict level difficulty so designers get a pass
  rate without human playtests (recalled, Gudmundsson et al., "Human-like playtesting with deep learning",
  CIG 2018).
- **Pixel-only testers.** Inspector (2207.08379): explore, detect key objects, investigate them in a
  human-like way, no engine integration. CA2 (2605.13918): an agent that receives the *call stack* and
  learns to reach target functions — code coverage as the reward.
- **DFHack.** Ships an in-game test runner (`test/` in the repo, run with a script inside Dwarf Fortress
  in CI): Lua tests with a `mock` library run against a live, loaded fortress.
- **Stardew / SMAPI.** SMAPI gives mods a console-command and event hook layer; testing is mostly
  in-game console commands (recalled) — the same "debug action as test primitive" pattern RimWorld has.
- **Paradox.** Observer mode plus scripted AI-only hands-off runs ("run the game 400 years with AI
  only, check for crashes and economic invariants") is the standard approach in grand strategy (recalled;
  the dev diaries forum is the source).

### 1.2 RimWorld specifically

- **Vanilla Dev mode.** Debug actions menu has an *Autotests* section: "Make Colony (full)" spawns 26
  colonists, every buildable, every item including DLC and mods; "Make colony (animals)" one of every
  animal. The Debug Logging menu has performance and RNG tests. Vanilla `-quicktest` starts a throwaway
  map straight from launch. (rimworldwiki Development_mode.) These are already in-process test
  generators nobody wraps with assertions.
- **Rimworld-Pickle (RimWorks).** RimWorld 1.6 mod: Gherkin scenarios run against a live session
  ("Given the save X is loaded / When I draft / And I wait 30 ticks / Then has job Wait_Combat").
  Steps are C# methods; feature files need no build. Explicitly sits a level above unit tests: def
  loads, patch conflicts, a job driver stalling at tick 400.
- **RimTest Redux (ilyvion, fork of LaTrissTitude's RimTest).** Attribute-based in-game unit tests
  (`[TestSuite]`, `[Test]`, `[BeforeEach]`, `[ShouldThrow]`), fluent asserts, a runner window; re-runs
  on every save load. CI badge on GitHub.
- **RimWorldTestHarness (Jeffrharr).** Dev-only 1.6 mod plus driver: a JSON scenario (save, forced
  clock/latitude/season, steps) produces a JSON report. Three verification kinds in one format: numeric
  probes with tolerance (real exit code), screenshots/timelapses, and "vision asserts" — a rubric for an
  LLM judge with the shots and recent log errors attached. Mid-suite save reload designed.
- **RimDevTools (1264600905).** Windows toolchain for 1.6/1.7: transactional deploy, transactional
  ModsConfig edit-and-restore, an in-game AutoTestRunner (UI, combat, recipe, skill tests) with quick /
  manual / auto tiers, exact-defName targeting, batch caps, one JSON result plus evidence files plus a
  *main-thread heartbeat* diagnostic.
- **HeadlessRim (IlyaChichkov) + RIMAPI.** Harmony patches that neutralise rendering, audio and input so
  RimWorld runs in Docker / headless Linux, driven over a REST API. RimWorks/steam-game-image-action
  builds a private OCI image of RimWorld for CI.
- **RimBridgeServer (pardeike)** — our bridge — plus a crowd of siblings: rimUIMCP (real UI clicking for
  agents, 28 helpers), rimworld-agent-bridge (JSON commands, 1.7), autorim-mcp, RimAPI_MCP_Server,
  RimSage / RiMCP_hybrid (source-search MCPs for agents writing mods).
- **RLE — RimWorld Learning Environment (AppSprout-dev).** A harness x model benchmark on a live colony,
  modelled on FLE (Factorio Learning Environment): swappable agent harnesses, an unmanaged-colony
  baseline, harness-agnostic scoring that reads only the writes that reached the game, deterministic
  terrain analysis given to every agent. Proof that a RimWorld gym over a bridge is buildable.
- **Rimworld-Antfarm (Sorcerio).** LLM colony administrator over a localhost REST mod with typed Pydantic
  client; state serialised every tick.
- **SimplifiedRimWorldRL (EmmanuelMess).** A toy re-implementation of RimWorld mechanics as a gym env to
  train RL — the "surrogate model" route.
- **RimWorld Multiplayer (rwmt, Zetrith).** Makes RimWorld deterministic enough for lockstep: seeded
  Rand per tick, sync of commands, and desync traces (stack traces of every Rand call, diffed between
  clients). This is the existing proof that RimWorld *can* be run deterministically and diffed.
- **Prepatcher (Zetrith), Harmony, Dubs Performance Analyzer.** In-process tooling: field injection
  before load, runtime patching, per-method tick profiling — all three are mechanisms a test harness can
  borrow (profile a single mod's tick cost; patch a method to count calls; add fields to Things).

### 1.3 General interactive-system testing

- **Deterministic simulation testing.** FoundationDB runs the whole cluster in one thread on a simulated
  clock and network with injected faults, seeds every run, and replays any failure exactly (Will Wilson,
  Strange Loop talk; FDB testing docs). TigerBeetle's VOPR does the same and even ships it as a browser
  game. Antithesis sells this as a deterministic hypervisor: any program, fully reproducible, with
  guided exploration toward rare states and "sometimes assertions" (assert that a state is *reached* at
  least once, not only that bad states never happen).
- **Property-based and stateful PBT.** Hypothesis `RuleBasedStateMachine` (rules, preconditions,
  invariants, automatic shrinking of failing sequences); QuickCheck state machines (a pure model runs
  beside the real system; postconditions compare them; parallel linearisability checks).
- **Model-based testing.** A small abstract model generates test sequences and is the oracle.
- **Metamorphic testing.** When there is no oracle, assert relations between runs: "rotate the build 90
  degrees and the output is the same", "double the input, output doubles", "adding a wall cannot make the
  room hotter in winter".
- **Record/replay and time travel.** rr records a process and replays it deterministically, backwards
  too. Game demo files (Valve demos, Age of Empires command logs — "1500 Archers") record only inputs and
  replay the deterministic sim.
- **Snapshot / approval tests.** Verify (.NET), ApprovalTests, insta: serialise a big state, store it,
  diff on later runs; humans approve deltas once.
- **Fault injection / concurrency exploration.** Jepsen and Maelstrom; Microsoft Coyote systematically
  explores interleavings of async .NET code.
- **Fuzzing.** AFL++ coverage-guided input mutation.
- **Mutation testing.** Stryker.NET mutates the code and checks the tests notice; measures test strength.

### 1.4 Agents playing games

- **ViZDoom.** Doom as an RL platform: headless, frame-skip, thousands of frames per second per core,
  many instances in parallel, game variables (health, ammo) given to the agent directly — no pixels needed
  when you have state.
- **"Playing DOOM with 1.3M parameters" (arXiv 2604.07385).** A 1.3M-param ModernBERT-style classifier
  over ASCII frames + depth, trained on 31k human demonstrations, picks actions at 31 ms and beats LLMs up
  to 92,000x larger (Nemotron-120B, Qwen3.5-27B, GPT-4o-mini) on defend_the_center: 178 frags in 10
  episodes vs 13 for all LLMs combined. Directly answers the owner's "could a small fast model learn to
  play via the bridge": yes, if you give it a compact text observation and a small discrete action set and
  train it on demonstrations. "Will GPT-4 run DOOM?" (2403.05468) is the slow-LLM counterpoint.
- **GameNGen (2408.14837).** A diffusion model *is* the Doom engine at 20 fps — a learned world model.
  The testing use: a learned surrogate predicts what the game will do, so disagreement between surrogate
  and real game flags novel behaviour.
- **DreamerV3 (2301.04104).** Learns a world model and plans in imagination; one config for many domains.
- **Voyager / MineDojo / MineRL / VPT.** Voyager: an LLM writes *code skills* into a growing skill
  library and calls them; the LLM is in the loop only to write a new skill or pick the next goal, the skill
  runs at game speed. VPT: learn actions from unlabeled video via a small inverse-dynamics model.
- **Cradle (2403.03186), SIMA (2404.10179).** General computer-control / many-worlds agents; slow, but
  show the "skills + reflection" split.
- **Claude Plays Pokemon (starter harness).** Tool-using LLM with a knowledge base, navigator tool and
  memory summarisation; the lesson is that the harness (tools, memory) dominates, and the LLM is slow, so
  every scripted helper (pathing) buys speed.
- **FLE — Factorio Learning Environment (2503.09617) and BALROG (2411.13543).** LLMs act by writing
  programs against an API, not by pressing keys — one model call yields many game actions.
- **Throughput engines.** ALE (frame-skip, sticky actions protocol), EnvPool (C++ batched envs, ~1M
  Atari frames/s), stable-retro, NetHack Learning Environment (very fast text roguelike), Crafter, Griddly,
  OpenSpiel. OpenAI Five: 180 years of Dota per day through massive parallel self-play.
- **Speed recipe common to all of them:** headless/no render; frame-skip (decide every k ticks, not every
  tick); state vectors instead of pixels; many env instances in parallel; scripted skills/macros with the
  model choosing only among them; small model for the hot loop, big model offline (training, skill
  writing, triage).

## 2. Concepts for RimMandrake

Each: the idea, where it comes from, the speed-up mechanism. Numbered for reference only, not ranked.

### A. Many proofs per load (the GameTest family)

**1. Test plots on one map.** Lay a grid of fenced 15x15 "plots" on one quicktest map; each plot is one
proof (a machine, a creature, a plant). All plots tick together; each has a tick deadline and an assert.
One load runs fifty proofs in the time of the slowest one. Source: Minecraft GameTest structure grid,
Unreal functional test actors. Speed: amortises the load and the tick budget over N proofs.

**2. Proof structures as saved blueprints.** Every proof's setup is a small saved fragment (terrain,
things, pawns) pasted by one bridge call instead of twenty spawn calls. Fragments live in the repo,
versioned like test fixtures. Source: GameTest `.mcstructure`, Unreal test maps. Speed: setup in one
call; no LLM writing setup code per item.

**3. A Python "spec" DSL, compiled not authored.** Proof = YAML/Gherkin lines ("given plot with
RM_Thing powered; tick 2500; expect output RM_X >= 3"); a deterministic compiler turns it into bridge
calls. LLMs write specs once; nothing LLM runs during the test. Source: Rimworld-Pickle, Cucumber,
RimWorldTestHarness JSON scenarios. Speed: removes LLM generations from retries; a failing spec reruns
in seconds.

**4. The always-on test colony.** A persistent minimal-list game stays loaded on the test host; a daemon
accepts specs from a queue and runs them back to back, resetting plots between them, never quitting.
Source: Gauntlet's controller, Factorio's test server, RimTest Redux "re-run on every load". Speed: the
22 s / 15 min cold load becomes a one-time cost per DLL change.

**5. Hot-reload instead of reload.** For XML-only changes, re-resolve defs or re-apply a patch in place
(or route a def change through a companion tool that edits the live DefDatabase field) so a cycle does
not need a restart; restart only when the assembly changes. Source: Unity domain-reload-off, game
"live tuning". Speed: edit-test loop in seconds for def tweaks.

**6. Mod-list tiers as test sizes.** "Small / medium / large" tests à la Google: small = one mod +
deps, 22 s load, run everything there first; large = full list, only for interaction tests that need
other mods. A test declares its smallest legal tier. Source: Google test sizes, RimDevTools quick/auto
tiers, our own lane-tier work. Speed: most proofs never pay the 15-minute load.

### B. Determinism, snapshots, replays

**7. Seeded deterministic runs.** Fix `Rand` seed, storyteller off, weather fixed, at test start
(the rwmt Multiplayer mod already does per-tick seeding). Same spec, same seed, same result — a flaky
fail becomes a reproducible fail. Source: FoundationDB, Factorio lockstep, rwmt. Speed: no "run it again
to see" generations; one failure is enough to debug.

**8. Snapshot and fork.** Save a mid-test state to memory (or a small .rws) at the interesting tick,
then fork: replay from there with variations without re-doing setup. Source: Antithesis branching,
rr, savestates in emulator RL (stable-retro). Speed: exploration costs ticks from the fork point only.

**9. Desync-style trace diff.** Record a compact per-tick trace (hashes of the subject's state, Rand call
count) for a passing run; on a later run diff traces and report the first divergent tick and its stack.
Source: rwmt desync traces, Factorio desync reports. Speed: localises a regression to one tick without
an agent reading logs.

**10. Golden state snapshots (approval tests).** After a proof, serialise the subject (thing fields,
comps, hediffs, stats) to sorted JSON and diff against the approved golden file. Any diff is shown once;
approval is a file write. Source: Verify, insta, ApprovalTests. Speed: one assertion covers hundreds of
fields; regressions caught without someone thinking of the assert.

**11. Input-log replay of owner playtests.** Log every command the owner issues in a live session (bridge
or UI) with the tick; replay the log on the next build against the same save. Source: AoE command logs,
Valve demos, Unity Automated QA recording. Speed: one human playtest becomes a permanent regression test.

**12. Time-skip with checkpoints.** For long processes (plant growth, breeding), jump the clock in
chunks with invariant checks at each chunk, rather than ticking through. Where the engine allows it,
call the subject's own `TickLong` N times directly. Source: ViZDoom/ALE frame-skip, "fast forward"
simulation testing. Speed: days of game time in seconds — paired with a metamorphic check (13) to prove
the skip did not change the outcome.

### C. Oracles without LLMs

**13. Metamorphic relations for mods.** Catalogue relations per system: rotating a machine does not
change its throughput; two identical machines produce double; adding a heater never cools the room;
skip-ticking N vs ticking N gives the same result; same seed twice gives the same result. Each is a pure
Python check over two runs. Source: metamorphic testing literature. Speed: oracle without an expected
value, so no LLM needed to decide "is this right".

**14. Always-on invariant monitor.** A companion component checks, every 250 ticks, global invariants:
no Thing with negative HP; no pawn in rock; no NaN stat; no item stack above limit; no red error lines
since last check; tick time per mod under budget. Fails fast with the tick. Source: TigerBeetle
assertions, Antithesis "always" properties, Dubs Performance Analyzer. Speed: every test and every
playtest is also an invariant test for free.

**15. "Sometimes" assertions as coverage.** Declare what must happen at least once in a session (the
machine outputs; the creature eats; the plant reaches harvestable). A dashboard shows which never fired.
Source: Antithesis sometimes-assertions, CA2 code-coverage reward. Speed: a single long playtest answers
dozens of "does it ever work" questions at once.

**16. Python shadow model.** For each mod system with rules (power, recipes, growth rates, spawn
weights), a 50-line Python model predicts the outcome from the defs; the live run is compared to the
prediction. Source: QuickCheck state-machine model, model-based testing. Speed: oracle is computed, not
judged; a mismatch is a precise number.

**17. Def-derived expectations.** Read the def dump and compute expected values (stat totals, recipe
outputs, plant grow days at given fertility) mechanically, then assert them live. Source: oracle
generation from specs. Speed: zero authoring per item; covers every def at once.

**18. Log as oracle, budgeted.** Every test asserts "zero new red errors and no new warning classes
attributable to our packageIds" over its window, with the Player.log/Verse.Log cap handled. Source:
Pickle's "def that will not load, conflicting patch", RimDevTools LogSync. Speed: free assertion on
every run.

### D. Generators and explorers (no LLM in the loop)

**19. Stateful PBT over the bridge.** A Hypothesis `RuleBasedStateMachine` whose rules are bridge
calls (spawn, damage, haul, toggle power, change temperature, save-load) and whose invariants are 14.
Hypothesis picks sequences, finds a failure, and *shrinks* it to the minimal sequence. Source: Hypothesis
stateful, QuickCheck. Speed: hundreds of random scenarios per minute; output is a minimal repro, not a
log to read.

**20. Def fuzzing.** Generate every legal combination of our defs with stuff/quality/biomes/temperature
and spawn them in batches on plots; catch exceptions and invariant breaks. Source: AFL-style fuzzing,
vanilla "Make Colony (full)". Speed: exhaustive smoke in one load.

**21. Wrap the vanilla Autotests.** "Make Colony (full)" and "Make colony (animals)" already spawn every
buildable, item and animal including mods. Run them on a quicktest with invariant monitor on, tick 10k,
and diff errors. Source: RimWorld Dev mode Autotests. Speed: near-zero new code, whole-mod coverage.

**22. Chaos storyteller.** A test storyteller fires every incident and game condition in a seeded random
order against a colony built with our content; records which ones crash or break invariants. Source:
Netflix chaos engineering, Jepsen fault injection, Paradox AI-only runs. Speed: interaction coverage
humans never reach.

**23. Save/load round-trip on everything.** For each of our Things/comps: spawn, run, save, load, compare
golden snapshot (10). The single most common class of mod bug (unsaved fields) caught mechanically.
Source: serialisation round-trip property tests. Speed: batch of all defs per load.

**24. Curiosity explorer.** A scripted agent that prefers actions which reach states never seen (new
jobs, new hediffs, new stat ranges, new code paths counted by a Harmony call counter). Source: EA SEED
curiosity RL (2103.13798), Go-Explore, CA2 call-stack reward. Speed: finds edge states without anyone
specifying them.

**25. Coverage via Harmony call counters.** Patch every method in our assemblies with a counter prefix
(test builds only); a test run reports which methods never ran. Directs the generators of 19-24 to
uncovered code. Source: CA2, coverage-guided fuzzing, Dubs Performance Analyzer's method patching.
Speed: tells you which tests to stop writing.

**26. Mutation testing for our proofs.** Run Stryker.NET-style mutants (or flip def values) and check
the proofs fail. Proofs that never fail on mutants are ceremony. Source: Stryker.NET. Speed: prunes
useless proofs; trust in a green run without an LLM re-reading it.

### E. Small fast models that play

**27. RimWorld gym over the bridge.** Wrap the bridge as a Gymnasium env: observation = compact text/
vector (pawn needs, jobs, nearby things, our subject's state), action = a small discrete set of scripted
skills (build X here, draft, haul, feed, tame). Many short episodes per load. Source: RLE, ViZDoom, FLE,
ML-Agents. Speed: the loop runs at bridge speed; models are optional consumers.

**28. Tiny policy trained on our own runs.** Like the 1.3M-param Doom model: train a small classifier to
pick the next skill from the compact observation, on demonstrations harvested from scripted runs and
owner playtests (11). It plays a colony for 30 in-game days in minutes. Source: arXiv 2604.07385, VPT,
EA imitation learning. Speed: 30 ms decisions vs multi-second LLM calls.

**29. Skill library, LLM only at the edges.** Voyager-style: the LLM writes and debugs *skills* (Python
functions over bridge calls) once; a deterministic planner or tiny policy sequences them at game speed.
The LLM is called only when no skill applies or a skill fails. Source: Voyager, FLE, Claude Plays Pokemon
harness lessons. Speed: LLM calls drop from per-step to per-new-capability.

**30. Small judge models for "does it look right".** A small local vision or text classifier (or Jev)
trained on accepted/rejected screenshots and states answers the routine visual checks (subject visible,
not in rock, lit, correct facing) in milliseconds; the big model only sees disagreements. Source:
RimWorldTestHarness vision asserts, Inspector key-object detector. Speed: removes the slowest judging
step from most runs.

**31. Persona bots for playtesting.** Scripted personas (the hoarder, the rusher, the pacifist, the
min-maxer) that play our content with different priorities; compare outcome distributions. Source: King
persona/difficulty bots, EA SEED, MMO generative-agent simulation (2512.02358). Speed: "is this mod fun /
balanced" answered by distributions over hundreds of bot-runs.

**32. World-model surrogate for triage.** Train a small model to predict next-state summaries from
state+action on harvested traces. Where its prediction and the real game diverge most, something new or
broken happened — point the human there. Source: GameNGen, DreamerV3. Speed: humans and LLMs only look
at surprising moments.

### F. Infrastructure and parallelism

**33. Headless RimWorld instances, many at once.** HeadlessRim-style Harmony patches (no render, no audio,
no input) let several minimal-list instances run side by side on one host, each on its own bridge port,
each taking specs from the same queue. Source: HeadlessRim, EnvPool, ALE, OpenAI Five scale-out.
Speed: N x throughput; GPU not needed.

**34. Containerised test image.** A private OCI image of RimWorld plus our mods, booted in CI on every
push, running the small-tier suite. Source: RimWorks steam-game-image-action, Factorio build server.
Speed: tests run without anyone asking, so failures arrive before an agent starts work.

**35. Uncapped tick speed for tests.** Remove the speed-4 cap and frame pacing in test builds (tick as
fast as the CPU allows, skip rendering between ticks). Source: ML-Agents time_scale, ViZDoom frame-skip.
Speed: the in-game clock stops being the bottleneck.

**36. In-process test runner, Python only orchestrates.** Move assertion loops into C# (RimTest-style
attributes or a companion `RunSpec` tool) so one bridge call runs a whole spec in-process and returns a
result table; Python dispatches and aggregates. Source: RimTest Redux, Unreal functional tests,
DFHack tests, Gauntlet controller. Speed: removes per-tick round trips.

**37. Main-thread heartbeat and hang watchdog.** A companion heartbeat lets the orchestrator detect a hung
or menu-dropped game in a second and restart automatically, instead of an agent noticing minutes later.
Source: RimDevTools heartbeat diagnostic. Speed: dead time after failures goes to near zero.

**38. Transactional environment edits.** Every ModsConfig/list swap, deploy and setting change is a
transaction with guaranteed restore, so a crashed test never leaves the next test a broken game. Source:
RimDevTools transactional deploy/ModsConfig. Speed: fewer "fix the harness" generations.

### G. Wild ones

**39. Test-the-tests mode: the game plays itself overnight.** A nightly AI-only colony on our full
content (personas 31, chaos 22, invariants 14, sometimes-assertions 15), recorded (11) and traced (9);
the morning report is a list of first-divergence ticks and never-fired assertions. Source: Paradox
observer runs, Ubisoft overnight bot tests, Riot's 100k tests a day. Speed: 8 hours of unattended
playtesting per night at zero LLM cost.

**40. Benchmark our harness on RLE.** Point RLE's harness-agnostic scoring at our mod list: "does a
colony with RimMandrake content survive as well as vanilla under the same harness and seed?" — a balance
oracle borrowed from someone else's benchmark. Source: RLE, FLE. Speed: an existing scoring pipeline.

**41. Specs from the def files themselves.** A generator reads each new def and emits the obvious spec
(it spawns, it saves/loads, its recipe outputs what the def says, its stats match the def) without any
LLM, so a new item has 5 live tests the moment it is written. Source: property-based "derive tests from
types", Pickle feature files. Speed: no authoring step at all for the common case.

**42. Diffusion "what should it look like" oracle.** Render the subject from the bridge, compare against
a small learned model of what our sprites look like in-game (scale, alpha, facing) and flag outliers.
Source: GameNGen (learned rendering), Inspector (pixel-only). Speed: art regressions found without a
human or large-model look.

## 3. Sources

All fetched 2026-11-05 with HTTP 200.

Game test practice
- Factorio FFF-62 The automation of Factorio: https://factorio.com/blog/post/fff-62
- Factorio FFF-366 The only way to go fast, is to go well: https://factorio.com/blog/post/fff-366
- Factorio FFF-288: https://factorio.com/blog/post/fff-288
- Factorio FFF-302 multiplayer megapacket: https://factorio.com/blog/post/fff-302
- Minecraft GameTest getting started: https://learn.microsoft.com/en-us/minecraft/creator/documents/gametestgettingstarted
- Minecraft wiki GameTest: https://minecraft.wiki/w/GameTest
- Unreal Gauntlet: https://dev.epicgames.com/documentation/en-us/unreal-engine/gauntlet-automation-framework-in-unreal-engine
- Unreal Functional Testing: https://dev.epicgames.com/documentation/en-us/unreal-engine/functional-testing-in-unreal-engine
- Unity Test Framework: https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/index.html
- Unity Automated QA: https://docs.unity3d.com/Packages/com.unity.automated-testing@0.8/manual/index.html
- Unity ML-Agents: https://github.com/Unity-Technologies/ml-agents ; paper https://arxiv.org/abs/1809.02627
- Godot GUT: https://github.com/bitwes/Gut ; Godot engine tests https://github.com/godotengine/godot/tree/master/tests
- Roblox TestEZ: https://github.com/Roblox/testez ; jest-lua https://github.com/jsdotlua/jest-lua
- Riot, Automated Testing for League of Legends: https://technology.riotgames.com/news/automated-testing-league-legends
- EA SEED imitation learning with concurrent actions: https://www.ea.com/seed/news/seed-imitation-learning-concurrent-actions
- Curiosity-driven playtesting coverage: https://arxiv.org/abs/2103.13798
- Augmenting automated game testing with deep RL: https://arxiv.org/abs/2103.15819
- RL for game testing in AAA games (Battlefield 2042, Dead Space): https://arxiv.org/abs/2307.11105
- Automated video game testing with synthetic and human-like agents: https://arxiv.org/abs/1906.00317
- Robust imitation learning for automated game testing (EVOLUTE): https://arxiv.org/abs/2401.04572
- Inspector, pixel-based game testing: https://arxiv.org/abs/2207.08379
- CA2, code-aware agent for game testing: https://arxiv.org/abs/2605.13918
- GDC: AI controlled players to test The Division: https://www.gdcvault.com/play/1026382/Automated-Testing-of-Gameplay-Features
- Generative multi-agent simulation for MMO playtesting: https://arxiv.org/abs/2512.02358
- DFHack tests: https://github.com/DFHack/dfhack/tree/develop/test
- SMAPI: https://github.com/Pathoschild/SMAPI
- Paradox dev diaries: https://forum.paradoxplaza.com/forum/developer-diary/
- Griddly: https://arxiv.org/abs/2011.06363

RimWorld
- Dev mode (Autotests, debug logging): https://rimworldwiki.com/wiki/Development_mode
- Rimworld-Pickle: https://github.com/RimWorks/Rimworld-Pickle
- RimTest Redux: https://github.com/ilyvion/rimtest-redux
- RimWorldTestHarness: https://github.com/Jeffrharr/RimWorldTestHarness
- RimDevTools: https://github.com/1264600905/RimDevTools
- HeadlessRim: https://github.com/IlyaChichkov/HeadlessRim ; RIMAPI https://github.com/IlyaChichkov/RIMAPI
- steam-game-image-action: https://github.com/RimWorks/steam-game-image-action
- RimBridgeServer: https://github.com/pardeike/RimBridgeServer
- rimUIMCP: https://github.com/Hcrab/rimUIMCP
- RLE RimWorld Learning Environment: https://github.com/AppSprout-dev/RLE
- Rimworld-Antfarm: https://github.com/Sorcerio/Rimworld-Antfarm
- SimplifiedRimWorldRL: https://github.com/EmmanuelMess/SimplifiedRimWorldRL
- RimWorld Multiplayer: https://github.com/rwmt/Multiplayer
- Prepatcher: https://github.com/Zetrith/Prepatcher
- Harmony: https://github.com/pardeike/Harmony
- Dubs Performance Analyzer: https://github.com/Dubwise56/Dubs-Performance-Analyzer
- Zombieland (pardeike, large tested mod): https://github.com/pardeike/Zombieland

Interactive-system testing
- FoundationDB testing: https://apple.github.io/foundationdb/testing.html
- Will Wilson, Testing Distributed Systems w/ Deterministic Simulation: https://www.youtube.com/watch?v=4fFDFbi3toc
- TigerBeetle safety: https://docs.tigerbeetle.com/concepts/safety/ ; VOPR in the browser: https://tigerbeetle.com/blog/2023-07-11-we-put-a-distributed-database-in-the-browser/
- Antithesis, how it works: https://antithesis.com/docs/introduction/how_antithesis_works/ ; blog https://antithesis.com/blog/is_something_bugging_you/
- Hypothesis stateful testing: https://hypothesis.readthedocs.io/en/latest/stateful.html ; repo https://github.com/HypothesisWorks/hypothesis
- quickcheck-state-machine: https://hackage.haskell.org/package/quickcheck-state-machine
- Model-based testing: https://en.wikipedia.org/wiki/Model-based_testing
- Metamorphic testing: https://en.wikipedia.org/wiki/Metamorphic_testing
- rr record and replay: https://rr-project.org/
- Valve demo recording: https://developer.valvesoftware.com/wiki/Demo_Recording_Tools
- 1500 Archers on a 28.8 (AoE lockstep): https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond
- Deterministic lockstep (Gaffer on Games): https://gafferongames.com/post/deterministic_lockstep/
- Jepsen: https://jepsen.io/ ; Maelstrom https://github.com/jepsen-io/maelstrom
- Coyote: https://github.com/microsoft/coyote
- Verify (.NET snapshot): https://github.com/VerifyTests/Verify ; ApprovalTests https://approvaltests.com/ ; insta https://insta.rs/
- AFL++: https://github.com/AFLplusplus/AFLplusplus
- Stryker.NET: https://github.com/stryker-mutator/stryker-net

Agents playing games
- ViZDoom: https://github.com/Farama-Foundation/ViZDoom ; paper https://arxiv.org/abs/1605.02097
- Playing DOOM with 1.3M parameters: https://arxiv.org/abs/2604.07385
- Will GPT-4 Run DOOM?: https://arxiv.org/abs/2403.05468
- GameNGen: https://arxiv.org/abs/2408.14837 ; https://gamengen.github.io/
- DreamerV3: https://arxiv.org/abs/2301.04104
- Voyager: https://arxiv.org/abs/2305.16291 ; https://github.com/MineDojo/Voyager
- MineDojo: https://minedojo.org/ ; https://github.com/MineDojo/MineDojo ; MineRL https://github.com/minerllabs/minerl
- VPT: https://arxiv.org/abs/2206.11795
- Malmo: https://github.com/microsoft/malmo
- Cradle: https://arxiv.org/abs/2403.03186 ; https://github.com/BAAI-Agents/Cradle
- SIMA: https://deepmind.google/discover/blog/sima-generalist-ai-agent-for-3d-virtual-environments/ ; https://arxiv.org/abs/2404.10179
- Claude Plays Pokemon: https://www.twitch.tv/claudeplayspokemon ; starter https://github.com/davidhershey/ClaudePlaysPokemonStarter
- Factorio Learning Environment: https://arxiv.org/abs/2503.09617 ; https://github.com/JackHopkins/factorio-learning-environment ; https://jackhopkins.github.io/factorio-learning-environment/
- BALROG: https://arxiv.org/abs/2411.13543
- ALE: https://github.com/Farama-Foundation/Arcade-Learning-Environment ; protocol paper https://arxiv.org/abs/1709.06009
- EnvPool: https://github.com/sail-sg/envpool ; https://arxiv.org/abs/2206.10558
- stable-retro: https://github.com/Farama-Foundation/stable-retro
- NetHack Learning Environment: https://github.com/facebookresearch/nle ; https://arxiv.org/abs/2006.13760
- Crafter: https://github.com/danijar/crafter
- OpenSpiel: https://github.com/google-deepmind/open_spiel
- OpenAI Five (Dota 2): https://arxiv.org/abs/1912.06680
