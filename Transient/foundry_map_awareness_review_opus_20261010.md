# Adversarial review — FOUNDRY map awareness design (2026-10-10)

Reviewer: independent Opus 5.5 instance. Subject: `Transient/foundry_map_awareness_design_20261010.md`.
Status: complete. Offline only: no bridge, no game, no `src/` edits. Engine claims checked against
decompiled 1.6 via RimSage; logs and the 82 summaries re-scanned with sanity probes.

## Verdict

**Right diagnosis of the log, wrong centre of gravity, and the recorder as specified would not work.**
Player.log genuinely cannot answer the question (CONFIRMED). But the design's own evidence argues mainly for
*controlling* injection, not *attributing* it: only 2 of its 8 cases (E1, E4) need provenance, and the 24/82
figure is mostly our own content tripping category-based detectors. The recorder's spec has three structural
defects (off-main-thread mapgen, `RegisterPawn` is not an arrival, top-of-stack loses "we caused it") that would
make the proposed `CONTAMINATED` verdict fire on our own runs. Re-order: quiet world + detector allowlist first;
a much smaller recorder second.

## Ranked findings

### MUST
1. **Record the whole context chain, not the top of stack.** `jawa/fire_incident RaidEnemy` pushes
   `bridge:fire_incident` then `incident:RaidEnemy`; top-of-stack says "incident", so A1/A5 and the
   CONTAMINATED rule would call our own injected raid foreign. Likewise mapgen wildlife reads `wild-spawner`
   (because `GenStep_Animals` calls `SpawnRandomWildAnimalAt`) and a bridge-created map reads `mapgen`. Store
   `root` (outermost) + `cause` (innermost); "ours" = root is `bridge:*`.
2. **The context stack must be thread-aware.** First-map generation and save loading run on a
   `LongEventHandler` worker thread. "Main thread only" either misses E1/E4 or races. `[ThreadStatic]` stack,
   locked tag store. And the bridge context cannot be pushed at RimBridgeServer dispatch (server thread, earlier
   time); it must be pushed inside each tool's `MainThread.InvokeAsync` lambda.
3. **`CONTAMINATED` as specified would fire on our own runs.** The 24/82 re-read shows most event hits are the
   mod under test (RM conditions, our letters, "Illoth hunting", "Half absorbed"). Under the proposed rule
   (origin ∈ {bridge:*, expected incidents}), every biome mechanic that spawns via its own MapComponent/GameCondition
   reads UNATTRIBUTED. Classify by **defining mod** (`IncidentDef.modContentPack`, first foreign assembly of the
   stackHint) against the mod under test before calling anything contamination. Without that the verdict
   trains agents to ignore it within a week.
4. **Use `Pawn.SpawnSetup(!respawningAfterLoad)`, not `MapPawns.RegisterPawn`,** and separate `arrival` (first spawn
   of an id) from `transit` (caravan return, gravship/sea-floor landing, transporter, release from a container).
   `RegisterPawn` also fires on every faction change and skips dormant pawns.

### SHOULD
5. **Put quiet-world control first; it is mostly free.** `storyteller_off` already exists. Add: an armed prefix
   that returns false on `WildAnimalSpawner.WildAnimalSpawnerTick` (one cold call site, `Map.cs:968`), end/clear
   active quests at run start, flip `DebugSettings.logRaidInfo`, and check scenario parts
   (`ScenPart_CreateIncident` ticks outside the storyteller). That is the "freeze" the design dismissed, minus the
   dangerous part (mod tickers), and it addresses E2/E3/E6 directly — the costliest cases.
6. **Fix the detectors before building a new instrument.** `letter_unexpected`/`condition_unexpected`/`raid_arrived`
   classify by letter def category; an allowlist by mod-under-test removes most of the 289+38+12 noise, and
   `strangers_near_anchor` should print `id/kind/faction/lord-job/letter-join` — that is O1, and it is Python
   over existing tools (`list_pawns`, `pawn_census`, `letter_list`), no C#.
7. **Drop E3, E5, E7, E8 from the provenance argument** (see Incident cases). E5's `requestedKind` cannot come
   from a generator hook at all; it must be emitted by `spawn_pawn` itself — a 10-line tool change.
8. **Tags do not survive save/load**, and must not be persisted by a GameComponent in the save (the frozen
   world ships). Report `PRE_LOAD` honestly; runs that need quest provenance must not load mid-quest.
9. **Don't base `since=mark` on id watermarks** — redressed world pawns, returning caravans and pre-generated
   quest pawns arrive with old ids. Use a spawn-event ring (or, without C#, diff `list_pawns` id *sets*).

### COULD
10. Key the tag store by int id or `ConditionalWeakTable`; skip tagging when the stack is empty; rate-limit
    stackHint per (kind, assembly) because breeders/hives/hatchers spawn in bursts.
11. Inventory omissions: `jawa/damage_log` + `JawaBenchEventRecorder` (damage/kill ring) is the real precedent;
    `rimworld-debug-testing` SKILL already has "look before you theorise" (line 294) — O0 is an edit, not new text.
12. `IncidentWorker.TryExecute` returns `true` without running when `requireColonistsPresent` and no free
    colonists; O3-lite should log `executed` separately from `called`.
13. Add explicit contexts for the non-incident spawners the project actually has: births/hatching, hives
    (`CompSpawnerPawn`), our own breeders — otherwise they dominate UNATTRIBUTED.

## Claims table (RimSage, decompiled 1.6, read 2026-10-10)

| claim | verdict | evidence |
|---|---|---|
| Player.log records no incident/arrival | **CONFIRMED** (own scan, 3 logs, probes) | §Player.log |
| "Vanilla writes only warnings and errors" | **REFUTED (overstated)** | `DebugSettings.logRaidInfo` → `Log.Message("Raid: …")`, `IncidentWorker_Raid.cs:184` |
| `IncidentWorker.TryExecute` calls `TryExecuteWorker`, tales, `RecordIncidentFired` | **CONFIRMED** | `IncidentWorker.cs:183-231`; also it returns `true` *without executing* when `requireColonistsPresent` and no colonists — an O3-lite ring must log the result, not just the call |
| `lastFireTicks` written only on the storyteller path | **CONFIRMED** | `Storyteller.TryFire` calls `StoryState.Notify_IncidentFired`; note `TryFire` also serves the **incident queue**, which ticks even with `enableStoryteller=false` (`Storyteller.cs:213-216`) |
| Raid pawns are generated inside `TryExecute` (drop pods included) | **CONFIRMED** | `TryGenerateRaidInfo` → `SpawnThreats` or `PawnGroupMakerUtility.GeneratePawns` → `raidArrivalMode.Worker.Arrive`, all inside `TryExecuteWorker` (`IncidentWorker_Raid.cs:70-127`). Drop-pod spawns are deferred, generation is not. A3 should pass by construction |
| Wild spawner funnel `SpawnRandomWildAnimalAt` | **CONFIRMED, with a twist** | `WildAnimalSpawner.cs:109`; it also generates pawns for **fly-in arrivals via `SkyfallerMaker.MakeSkyfaller(FlyerArrival, pawn)`** — deferred spawn, so generation-tagging is needed here too, not only for raids. **And `GenStep_Animals` calls the same method at mapgen** (`map != MapGenerator.mapBeingGenerated` check inside it), so with innermost-wins mapgen wildlife reads `wild-spawner`, not `mapgen:*` — A4 needs the chain, not the top |
| Quest pawns: `QuestPart_PawnsArrive` is the arrival funnel | **REFUTED** | also `QuestPart_DropPods`, `QuestPart_SpawnThing`, `QuestPart_SpawnPawnsInStructure`, others. Quest pawns are generated at offer time inside `IncidentWorker_GiveQuest.GiveQuest` → `QuestUtility.GenerateQuestAndMakeAvailable`, so a storyteller quest's pawns get tag `incident:GiveQuest_*` from the TryExecute context — **no `QuestPart` hook is needed** if tags survive until arrival (they do not survive a load) |
| Map generation runs on the main thread | **REFUTED** | `Root_Play` → `QueueLongEvent(..InitNewGame.., doAsynchronously: true)` → `new Thread` (`LongEventHandler.cs:368`) |
| `MapPawns.RegisterPawn` = spawn event | **REFUTED** | also faction change, registry refresh, load; early return for inactive pawns (`MapPawns.cs:832-906`, `Pawn.cs:2657, 4000`) |
| `Pawn.SpawnSetup(map, respawningAfterLoad)` usable with `!respawningAfterLoad` | **CONFIRMED** | `Pawn.cs:2616` |
| `thingIDNumber` strictly monotonic | **CONFIRMED for new things, but irrelevant for arrivals** | `ThingIDMaker` → `UniqueIDsManager.GetNextThingID` → `GetNextID(ref nextThingID)` (saved). Redressed world pawns, returning caravans, quest pawns generated before `mark` all arrive with ids **below** the watermark |
| Nothing on `Pawn` records origin | **UNVERIFIED (plausible)** | not exhaustively checked; agree with author |
| Storyteller off stops quests/mod tickers | **REFUTED as the author also says**, and **one more leak**: `ScenPart_CreateIncident` fires from `Scenario.TickScenario` (`TickManager.cs:386`), outside the storyteller gate |
| A cheaper "freeze" does not exist | **REFUTED** | `DebugSettings.enableStoryteller` (all comps incl. quest-giving) + queue clear + a one-line armed prefix returning false on `WildAnimalSpawner.WildAnimalSpawnerTick` (called from `Map.cs:968`) + ending active quests + `logRaidInfo` covers every *vanilla* source except scenario parts and mod tickers. `DebugSettings.noAnimals` exists but destroys every animal on tick (`Pawn.cs:2798`) — too blunt for creature tests |
| JawaBench has one dispatch point | **UNVERIFIED → irrelevant** | `BindArguments` is a central Harmony-patchable point (ArgGuard uses it), but it runs on the server thread before the main-thread lambda; see Hook safety |
| Lord job type hints origin | **CONFIRMED in principle** | raid `MakeLords` after `Arrive` (`IncidentWorker_Raid.cs` TryExecuteWorker); author's caveat (wild animals no Lord) holds |

## Player.log re-search

Re-run independently (python, not grep) over `Player.log` (32,522 lines, 2026-10-10 10:27), `Player-prev.log`
(487) and the 2026-09-07 quicktest log (15,062), 14 patterns, with two sanity probes per file
(`Harmony` 32/4/169 hits; `JawaBench` 0/8/4 — the current Player.log is a non-JawaBench session, which is
itself worth knowing before anyone greps it for bridge evidence).

- **CONFIRMED:** no line records an incident firing, a letter arriving, a quest pawn arriving or a pawn
  spawning. `incident`/`arriv`/`manhunter`/`wander` hits are load-time ctor lines, def-list dumps, mod config
  lines (`Added ManhunterAmbush to Wasteland with mtbDays 30`) and stack frames.
- **MISSED by the design:** vanilla is not purely warnings/errors. `DebugSettings.logRaidInfo`
  (`IncidentWorker_Raid.cs:184`) emits `Log.Message("Raid: <faction> <arrivalMode> <strategy> c=<cell> p=<points>")`
  for every raid that fires through `IncidentWorker_Raid.TryExecuteWorker`. It is off by default (0 hits),
  but it is one static bool a harness can set today with zero C#. It covers raids only.
- **MISSED:** `[JawaBench] event recorder: damage=True kill=True lineage=True` — a damage/kill ring
  (`jawa/damage_log`, `JawaBenchEventRecorder`, `JawaBenchSituationalTools.cs:138`) already exists beside
  lineage and is absent from §2's inventory. It already answers "what hit my subject" (E3's Metalhorror stab
  is exactly that kind of row) and its ring/installed/lazy-install machinery is the one the arrival recorder
  would extend, not a new precedent.
- The headline ("Player.log cannot be the answer") **stands**. But "vanilla logs only warnings and errors"
  is overstated and should be cut to "vanilla logs no arrivals; one dev flag logs raids".

## Incident cases (each cited source read)

| # | supports provenance? | supports event control? | note |
|---|---|---|---|
| E1 | **partly** | yes | Source (`bland_world.py:268`) says only "a fresh map also arrives with hostile-faction insects". "i.e. mapgen, not an event" is the **author's inference, UNVERIFIED** — hostile Insect-faction Spelopede/Megaspider on a fresh map is more like a hive/landmark/mutator/ancient-danger structure than wild animals (vanilla `GenStep_Animals` makes factionless wildlife). If they come from a hive, they keep spawning *during* the run under no context we push → UNATTRIBUTED, not `mapgen:*`. The best case for provenance, but its own attribution is a guess. |
| E2 | no | **yes** | The remedy (kill + Peaceful + queue clear) needed no attribution. Knowing "mechanoids came from incident X" would not have changed the action. |
| E3 | **no — refutes the framing** | **yes** | The item already says Whistler "wandered in from an unrelated wanderer-join event". Origin was **known**; the cost was that the event *happened*. And the test was inconclusive because the predators would not hunt an uninvolved colonist, not because of Whistler's origin. This is an argument for a quiet world, not for a recorder. |
| E4 | yes | yes | Genuine unknown origin; never attributed. Strongest pure-provenance case, but it is a quicktest-start artefact (scenario/start-map), which one targeted read (`ScenPart`s of the debug scenario) could settle once. |
| E5 | **no — miscategorised** | no | The substituted Colonist WAS ours. A generation-time origin tag reads `bridge:jawa/spawn_pawn` for it, correctly, and is no help. The fix was read-back of kind, which the tool owns. A2's `requestedKind ≠ kind` cannot come from a `GeneratePawn` postfix (it sees the request it was given, i.e. the substituted kind); it has to be emitted by the spawn tool. Remove E5 from the provenance case. |
| E6 | n/a | yes | Harness failures generally; became bland-world. Not provenance. |
| E7 | **no** | yes | A modal dialog, not a pawn. The recorder cannot see it; the existing modal sweep handles it. |
| E8 | **no** | weak | Faction-relation setup confusion, read correctly by hand from `faction_relations_get` in one call. |

**Net:** of eight cases, two (E1, E4) actually need "where did this pawn come from"; five (E1, E2, E3, E4, E6)
need "stop the world injecting things"; three (E5, E7, E8) support neither and should be dropped from §1.
The design's own §1 "What I could not find" paragraph says the same thing; its recommendation does not
follow from it.

## 24/82 audit (re-run)

Re-run reproduced the numbers exactly (82 summaries, 24 with an event-class hit; 289/38/18/12/5). Then I read
the hit texts. **The figure is dominated by the subjects under test, not by leakage:**
- `condition_unexpected` top rows: `RM_ForgePulse`, `RM_BlueDesertHazeCarrier` — our own biome conditions.
- `letter_unexpected` top rows: "Slicked", "The mountain walks in", "Touched by the slime", "Feral droid breaks
  cover" (our mods); Ideology funeral/eulogy opportunities and "in labor" (consequences of deaths/births in the
  test); "Area revealed" (fog).
- `raid_arrived` (12): "Illoth hunting", "Half absorbed" ×3, "The bank moved", "The oil haze flashed", "A line of
  glare", "Nothing they freed comes back", "Brain worm" ×2, "Metalhorror emerging". At least 8 of 12 are named
  mechanics of the mod/biome under test.
- Pawn-class hits plausibly uncontrolled: `strangers_near_anchor` in BlueDesert ×9, FlowWorks ×3, Bacta, Greentide,
  Slime, TheForge; `hostile_pawns` in TheForge/FeverWood. Whether those are the subject's own spawns is UNMEASURED.

⇒ The honest statement is "**up to ~8 of 82 runs** carry a pawn-class surprise that might be uncontrolled;
the other hits are our own content tripping detectors that classify by letter category". That is a
**detector false-positive defect** (cheap: allowlist by `def.modContentPack` of the letter/condition/incident
against the mod under test) and it is a bigger, cheaper win than the recorder. It is also exactly the false
positive the proposed `CONTAMINATED` rule would inherit (see MUST-3).

## Hook safety (TPS-era failure classes)

| class | finding |
|---|---|
| **Threads** | 🔴 **The "static `Stack<Origin>`, main thread only" premise is REFUTED for the case the design most wants (E1/E4).** `Root_Play` queues `Current.Game.InitNewGame()` with `doAsynchronously: true` (`Root_Play.cs:~45`), and `LongEventHandler.UpdateCurrentAsynchronousEvent` runs it on `new Thread(...)` (`LongEventHandler.cs:368`). Save loading is the same (`GameDataSaveLoader.cs:155`). So the first map's mapgen, scenario pawns and quicktest-start pawns are generated **off the main thread**. A main-thread guard drops them; an unguarded static stack is a cross-thread data race. Use `[ThreadStatic]` stacks plus a lock (or `ConcurrentQueue`) on the shared tag store. Bridge tool bodies run on main via `ctx.MainThread.InvokeAsync` (`JawaBenchTerrainTools.cs:111`), which is a *different thread and a later time* than the RimBridgeServer dispatch (`AnnotatedExtensionCapabilityProvider.BindArguments`, already Harmony-patched by `JawaBenchArgGuard`) — **a push at dispatch is not on the stack when the lambda runs**. The bridge context must be pushed inside the main-thread lambda, i.e. per tool or via a shared helper, not at one dispatch point. |
| **Skip-safety** | Prefix-push / finalizer-pop survives a skipping prefix from another mod (finalizers always run). But an exception thrown in *our* prefix before the push, then a finalizer pop, unbalances the stack for the rest of the session. Pop by saved depth (`__state = depth; finally truncate to depth`), never a blind `Pop()`. `IncidentWorker.TryExecute` is non-virtual and calls virtual `TryExecuteWorker` (`IncidentWorker.cs:183-231`), so patching `TryExecute` once covers every subclass — CONFIRMED good choice. |
| **Wrong-hook: RegisterPawn** | 🔴 `MapPawns.RegisterPawn` is **not an arrival event**. It is called from `Pawn.SpawnSetup` (incl. `respawningAfterLoad`, `Pawn.cs:2657`), from `Pawn.SetFaction` on every faction change while spawned — taming, recruiting, `jawa/set_pawn_faction` (`Pawn.cs:4000`) — and from `UpdateRegistryForPawn` (`MapPawns.cs:903-906`); and it **returns early for `!mindState.Active`** pawns (dormant ancient-danger insects/mechs). Using it would log recruits as arrivals and miss dormant hostiles. Use `Pawn.SpawnSetup` postfix with `!respawningAfterLoad`, and classify a pawn whose id has been seen spawned before (caravan return, gravship landing — this project's **sea-floor layer flight**, transporters, cryptosleep/casket release, holding-platform escape) as `transit`, not `arrival`. |
| **Hot path** | `PawnGenerator.GeneratePawn(PawnGenerationRequest)` (`PawnGenerator.cs:140`) runs at world gen and settlement/faction-leader generation (thousands of world pawns), recursively for relatives, and through `GenerateOrRedressPawnInternal`. A postfix that only does `dict[id]=origin` is cheap, but a **bounded** dict gets churned out by world-gen pawns before the map pawns that matter. Skip tagging when the stack is empty (no context ⇒ nothing worth storing; the spawn-time lookup falls back to stack-at-spawn anyway). |
| **Leak/retention** | Key by `thingIDNumber` (int), never `Pawn` — or use `ConditionalWeakTable<Pawn,Origin>`, which is unbounded but GC-safe and needs no eviction policy. A `new StackTrace()` per UNATTRIBUTED spawn is fine for rare spawns but our own content breeds (`RM_CompVerminBreeder`), hives spawn, eggs hatch: rate-limit per (kind, first-foreign-assembly). |
| **Game-scope** | Clear on new Game — but the generation tags are **not saved**. Quest pawns are generated at offer time and arrive days later; any save/load between offer and arrival (bland-world runs start by *loading* a save) loses the tag ⇒ UNATTRIBUTED ⇒ false `CONTAMINATED`. Do **not** fix this with a JawaBench `GameComponent` scribed into the save: the shipped frozen savegame must never carry a dev-companion class. Report `PRE_LOAD` (generated before the last load) as its own origin. |
| **Redress** | `GenerateOrRedressPawnInternal` returns **recycled world pawns** (`PawnGenerator.cs:205-224`) carrying old `thingIDNumber`s. A postfix still sees them (good), but the O1 "id > watermark" arrival test is wrong for them (see Q1). |

## Revised recommendation

To the owner's question: **Player.log plus discipline is not enough — but the first fix is a quiet world plus
fixed detectors, not a provenance recorder.** And yes, events should be controlled during validation and
north-star runs; the cheap controls cover every vanilla source except scenario parts and mod tickers.

1. **Quiet-world profile (≈½ day, mostly Python):** `storyteller_off` + queue clear (exists) + armed wild-spawner
   off (one tiny prefix) + end active quests + `logRaidInfo=true` + scenario-part check. Default ON for
   validation/north-star runs, opt-out per suite for situational chains that need the world alive.
2. **Detector repair (≈½ day, Python):** allowlist by mod-under-test; `strangers_near_anchor`/`hostile_pawns`
   print who (id, kind, faction, lord job, joined letter). This *is* O1, built over existing reads.
3. **O0 skill edit:** extend `rimworld-debug-testing` §"look before you theorise" with the 4-call first look.
4. **O3-lite:** the `TryExecute` ring (record root chain, `executed` flag). It also catches scenario-part and quest
   incidents the quiet profile misses.
5. **Only then, and only if 1–4 still leave unexplained pawns:** the arrival recorder, with MUST 1–4 fixed
   (chain, thread-aware, `SpawnSetup`, arrival vs transit) and `CONTAMINATED` scoped by defining mod.
   Re-run the 82-summary audit after step 2: if pawn-class surprises go to ~0, stop.

Trust requirements for a fresh agent reading any report: it must print `installed`/`installedAtTick`,
`gameId`, `loadedAtTick` (tags before it are PRE_LOAD), count of UNATTRIBUTED, and a sanity row (a known
`bridge:` spawn made at run start). A report that cannot show its own control row is not evidence.

## Answers to the author's open questions

1. **Monotonic `thingIDNumber`?** Yes for newly made things (`GetNextID(ref nextThingID)`, saved). But not an
   arrival test: redressed world pawns, returning caravans and pre-generated quest pawns carry older ids.
2. **Raid arrival modes generate inside `TryExecute`?** Yes for the default path and `SpawnThreats` overrides
   (`TryGenerateRaidInfo`); drop pods defer the *spawn* only. Wild fly-ins defer too (FlyerArrival skyfaller).
3. **Quest pawns at offer time; single funnel?** Generated at offer time (inside `GiveQuest`'s TryExecute when
   storyteller-given; inside `jawa/fire_quest` when ours). Not a single funnel: `QuestPart_PawnsArrive`,
   `_DropPods`, `_SpawnThing`, `_SpawnPawnsInStructure` … Generation tagging makes the funnel irrelevant — if
   no load intervenes.
4. **`RegisterPawn` for every spawn, also on load?** It fires on load, on faction change and on registry
   refresh, and skips inactive pawns. Use `Pawn.SpawnSetup(!respawningAfterLoad)` + an arrival/transit split.
5. **Single dispatch point?** `BindArguments` is central and already patched, but wrong thread/time. Push
   inside the main-thread lambda (shared helper used by spawn/fire/map tools). `rimworld/*` tools: wrap their
   few spawn-capable ones, otherwise they read UNATTRIBUTED. Dev debug actions call the same funnels
   (`DebugToolsSpawning.cs:713` uses `SpawnRandomWildAnimalAt`) and will read `wild-spawner` — acceptable.
6. **Install early enough for first-map mapgen?** It must install before `InitNewGame`, i.e. from a
   `StaticConstructorOnStartup` or companion registration (TPS's starter), not the lazy first-call init that
   `JawaBenchEventRecorder` uses. And it must work on the long-event worker thread.
7. **Incidents bypassing `TryExecute`?** Vanilla: incident firing routes through it (storyteller, queue,
   scenario parts). Pawn spawns that are not incidents (MapComponents, GameConditions, hives, breeders, births,
   quests' own parts) bypass it by nature — that is the UNATTRIBUTED bulk, not an edge case.
8. **24/82 dominated by deliberate perturbation?** Yes — re-read above. At most ~8 runs carry pawn-class hits
   that might be uncontrolled; most hits are our own mods' letters/conditions. Do not quote 24/82 as leakage.
9. **Always-on vs armed?** Always-on is acceptable for the *in-memory* hooks if they are skip-safe and cheap
   (they are cold except `GeneratePawn`, where an empty-stack early return makes it free); a TTL-armed recorder
   would indeed lose E1. Keep only the disk writer armed. The owner's "debug mode" framing is satisfied because
   JawaBench itself is a dev-only companion that never ships.
10. **Is identification cost real?** Not shown by the cited files; E3 shows origin was known and the cost was
    injection. Treat the owner's anecdote as plausible but UNMEASURED; with a quiet world + detector repair the
    recorder may be unnecessary. Decide after re-running the audit.
