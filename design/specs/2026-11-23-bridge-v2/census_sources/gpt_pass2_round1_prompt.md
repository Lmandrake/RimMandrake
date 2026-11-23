You are a sceptical senior reviewer of test infrastructure for a RimWorld 1.6 mod project. Be adversarial. Do not praise.

Context. "The bridge" drives a running RimWorld from outside: RimBridgeServer (a third-party Workshop mod, a GABP server
in the game) plus our companion DLL "JawaBench" (C#, about 81,000 lines, 427 tools, Harmony taps), plus Python callers.
A first designer wrote WHAT live testing needs without reading the bridge's code. A second designer (the author of the
three attached files) read the code and the RimWorld 1.6 source, and decided HOW to build: 05_build_design.md,
06_build_order.md, 07_for_the_owner.md. The policy they serve: every live run ends in one of seven outcomes (SUCCESS,
MOD FAILURE, RANDOM MISS, ENVIRONMENT FAULT, APPARATUS FAULT, UNRESOLVED, COULD NOT LOOK); kinds A (deterministic),
B (stochastic, budgeted), C (hunt). The owner's aim: "Force the situation ALWAYS if possible, there are too many
variables to control otherwise" and to stop burning effort on repeating large expensive live suites with low yields.

You have NO web access in this run and about 7 minutes: answer from the attached text and from what you know; mark each engine fact you rely on as RECALLED. Be complete on all ten questions; keep each answer under 200 words.

Tear the design down. Answer each numbered question with a verdict (SOUND / WRONG / RISKY / UNPROVEN), the concrete
failure case (this input, this wrong result), and the smallest repair.



1. "Improve by joining, do not rebuild" (Way A against Ways B and C). Is the comparison fair? What cost or risk of Way A
   is missing or understated? Is there a fourth way that beats all three?
2. "Record inside the game, judge outside from the trace." Name every way a judge that reads only a trace can give a
   wrong verdict that an in-game judge would not (missing state, end-of-tick sampling, alias rebinding, values that
   change twice in one tick, dropped rows, clock of taps against tracks). Is "the arm phase adds a track for every
   probe that a condition names" enough? Is re-judging a kept trace with a REPAIRED checker sound evidence, or does it
   hide a class of faults?
3. Engine facts table: any claim that is wrong or over-read for RimWorld 1.6? In particular: (a) pausing inside a
   DoSingleTick postfix stops TickManagerUpdate's loop on that tick; (b) PathRequest results arrive only in
   PathFinderTick or FindPathNow; (c) a pocket map's temperature is fixed by pocketMapProperties.temperature; (d) the
   flying animation frame is a pure function of game ticks through AnimationWorker_Keyframes; (e) GenSpawn.Spawn is the
   only caller of SpawnSetup; (f) QuestManager.Add is the choke point for quest offers; (g) thing ids survive a load.
4. The stage map with no bystanders, as a pocket map, with the colony on a "green room" map. What breaks? (Incidents
   that need a player home map or free colonists; raids and their arrival points on a pocket map; mods' MapComponents on
   pocket maps; map-wide mechanics of the mods under test such as sun, weather and temperature; wealth and threat
   points; whether results on such a stage transfer to a real colony map.) Is "weaker, shared-map holds" for the
   full-list walks acceptable?
5. PLAY (the game's own loop, unpaused) as the default, STEP (paused DoSingleTick slices) not counted until compared.
   Is PLAY at high speed itself deterministic enough for kind A? What differs between PLAY at speed 1, speed 3 and
   Ultrafast that could change a verdict? Is the camera handling right?
6. Tracks-on-change first, Harmony taps only for sub-tick facts, and the "canary rite" at arm (real engine acts on a
   canary thing and pawn). What does the canary fail to prove? Does it add risk (side effects, random draws, thing ids
   consumed, a job given to a pawn) that could itself spoil kind A scenes or replays? What is a better arm-time proof?
7. The "deviation store" that unifies calm controls, force levels, the live-tuning overlay, pinned rates, and planted
   faults ("mutants by overlay"). Is unifying them a mistake? Is "shown both ways in one process: green first, then the
   mutant overlay, then revert" valid evidence that a scene can fail? What mutants can it not express, and does that
   bias which scenes get trusted?
8. The build order (06). Is the claim "the first three pay first" true? What ticket is missing, wrongly ordered, too big
   for one run, or has an acceptance test that could pass on wrong code (name the wrong code)? Which acceptance tests
   only restate the ticket?
9. The owner's page (07): is anything on it NOT truly his choice, or is a choice that IS his missing (money, his own
   game ArchBig, his camera, live flight tests)? Is any sentence on it an overclaim?
10. The three highest-value changes you would make to this design, in order.
