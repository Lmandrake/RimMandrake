# Map awareness during debugging — design (FOUNDRY, offline, 2026-10-10)

Status: design only. Nothing was built, the bridge was not touched, and `src/` was not edited.

## 0. Answer in one paragraph

**This is not a discipline problem, because Player.log contains nothing to read.** I measured three logs
(32k, 15k and 63k lines): there is not one line recording an incident firing or a pawn arriving. Vanilla logs
only warnings and errors.

Detection already exists in modcheck: `hostile_pawns`, `raid_arrived`, `strangers_near_anchor` and
`letter_unexpected`. It fires in up to 24 of 82 run summaries. It reports *"1 non-player pawn(s) within 30
cells of the anchor"* and cannot say who that pawn is or why it is there.

The missing piece is **provenance**, and the engine stores none on the pawn. It has to be recorded at creation.

Recommendation, in order:
1. A one-paragraph first-look rule (O0).
2. An "incident fired during this run" record (O3-lite): one cold postfix on `IncidentWorker.TryExecute`. The
   saved `StoryState.lastFireTicks` turned out to be written on the storyteller path only, so it cannot be used.
3. One companion build: a read tool, `jawa/scene_report`, backed by a small always-on arrival recorder. It tags
   each pawn at `PawnGenerator.GeneratePawn` with the active context (incident / wild-spawner / mapgen / our own
   bridge tool / quest) and logs it at `MapPawns.RegisterPawn`.
4. Validation and north-star runs end `CONTAMINATED`, naming the arrival, when any pawn's origin is not ours.

The game-mutating "freeze everything" version is not worth its risk.

## 1. Evidence of the problem

Search sanity probe: the same grep over `design/` + `infrastructure/state/items` finds `korrum` in 70 files. That shows
it can see. Phrase searches (manhunter, wandered in, random humans, hostile insects, naming dialog, raid letter)
were run over Transient/, items/ and closed/, handoffs/, lessons/, memory/ and design/RimMandrake.

| # | case | cost | what explained it | source |
|---|---|---|---|---|
| E1 | Bland-world run #1: the setup gate FAILed because **hostile insects were on map 1** (Locust, Spelopede, Megaspider: hostile-faction insects that arrive with a fresh map, i.e. mapgen, not an event) | **25.5 min** of a 210-min pass (row 22), plus run #2 on map 2 at **59.2 min**, also gated out | Measured after the fact. `bland_world.setup` now does `destroy_bulk filter=nonColonists` with the comment "MEASURED 2026-10-01 (tile 254)" | `design/RimMandrake/northstar_time_ledger_2026-10-01.md` §1–2; `src/RimMandrake/Utils/modcheck/bland_world.py:268` |
| E2 | Owner, 2026-10-05: *"There were mechanoids running around."* on a review map | an owner review spoiled; a standing rule was created | Nobody attributed them. The fix was blanket removal (`kill_hostiles` + `incident_queue_clear` + Peaceful) | memory `kill-hostiles-on-review-maps.md` |
| E3 | PORTED_BEAST: a hostile-AI test ran against `Whistler`, *"who'd wandered in from an unrelated wanderer-join event during the drum-lure ticks"*. Over 1260 ticks the result was inconclusive | one criterion (AI use on a hostile) left **unproven** in a closing item | Found by reading the pawn by hand. The test subject itself was an uncontrolled event's product | `infrastructure/state/items/closed/PORTED_BEAST_MECHANICS_REBUILD_1.md:310-318` |
| E4 | Owner, 2026-08-30: *"sometimes random humans pop up at the beginning of a new colony"* | a standing rule to spawn 3–5 of each subject and cross-check `list_pawns` | Never attributed. Handled by statistics, not by knowing | memory `spawn-many-for-bridge-tests.md`; `skills/rimworld-debug-testing/SKILL.md:191` |
| E5 | 80 `spawn_pawn` calls: 4 delivered a vanilla `Colonist` while the tool reported "Spawned 5/5 Jawa_…". The census then blamed a `weaponMoney` defect "that does not exist" | **days**: *"kept the bare-hands defect open for days"* | Resolved by recording the kind READ BACK, not the kind requested. This is the "created by us" provenance problem in its purest form | memory `census-requested-vs-actual-kind.md` |
| E6 | Owner, 2026-10-01: *"We're being eaten alive by random events, naming dialogs, the lot."* A stopped agent had *"burned 3h+ mostly on harness failures"* | 3h+ | Became the bland-world programme | memory `static-boring-test-worlds-…md`; `Transient/world_reset_2026-10-01.md` |
| E7 | Aftermath's raid letter opened a forcePause `Dialog_NodeTree` that "taints runs" | runs tainted until the modal sweep covered it | Added to the `required_checks.py` taint rules | `infrastructure/state/handoffs/FOUNDRY_REBOOT_HANDOFF_202610040745.md:45` |
| E8 | Every faction on a quicktest world was Hostile, so Lord members came out as factionless `OuterRim_BattleDroid`s | a confusing read during a 10-tool verify | Read by hand from `faction_relations_get` | `infrastructure/state/items/closed/BRIDGE_LORDS_AND_GAPS_TOOLS_1.md:66-70` |

**Pattern.** In none of E1–E8 did an instrument say *where the pawn came from*. Each was resolved by elimination,
or by blanket destruction, or not at all (E3, E4). E1 and E2 were answered by destroying the evidence, which works
for a review map but leaves a validation run unable to say whether it was clean.

**What I could not find.** I found no single incident that cost "several tickets" purely on the question "what is
that creature". The large costs (E1, E5, E6) are run invalidation and misattribution, not identification. The
owner's anecdote is probably real but is UNMEASURED here: chat transcripts were not searched.

## 2. What already exists

**Player.log does not record events at all. It cannot be a discipline problem.** MEASURED on 2026-10-10 over
three logs: the live `Player.log` (32,518 lines), `Player_log_before_lanterndeeps_quicktest_2026-09-07.log`
(15,062 lines, a quicktest session) and `Player-crashed-animaltype.log` (63,325 lines). Each was searched for
`RaidEnemy`, `ManhunterPack`, `HerdMigration`, `WandererJoin`, `WildAnimalSpawner` and `IncidentWorker`.

- Every hit was a load-time Harmony ctor line, an XML config error or a stack-trace frame.
- No hit recorded an incident firing, a pawn arriving or a letter being received.
- Sanity probe: the same patterns DO hit (e.g. `CM_Less_Shitty_Ambush.IncidentWorker_Ambush_ManhunterPack_Patches`), so the search can see.

Vanilla RimWorld writes only warnings and errors to the log, and an incident is neither. So the answer to "is
Player.log sufficient?" is **no, structurally**. Better reading cannot recover a line that was never written.

**Bridge reads that already exist** (all names grepped from `src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`):

| tool | gives | provenance? |
|---|---|---|
| `jawa/list_pawns` (`JawaBenchTerrainTools.cs:1011`) | every pawn on the map: id, kind, faction, hostility, position, dead/downed | no |
| `jawa/pawn_census` (G1, `JawaBenchSituationalTools.cs:541`) | mental state, job, prey, enemy target, needs, **lord + duty** | indirect: the Lord's job type hints at the origin |
| `jawa/letter_list` | label, defName, arrivalTick, lookTargets | **yes, partly**: a raid/migration/wanderer letter names its pawns as lookTargets |
| `jawa/story_stats` | raid counters etc. | count only |
| `jawa/forecast_incidents` | `StorytellerUtility.DebugGetFutureIncidents` | future, not past |
| `jawa/incident_queue_peek` / `_clear` / `_remove` / `incident_schedule` | the queued incidents | pre-fire only |
| `jawa/tale_list` | TaleManager rows | some arrivals leave tales (UNVERIFIED which) |
| `jawa/kill_hostiles`, `jawa/destroy_bulk filter=nonColonists` | removal | none; it destroys the evidence |
| `jawa/thing_lineage` | a **Harmony-installed lineage journal** for items (absorb/split/ingest/destroy), installed on the first tool call of a session | **this is the precedent**: a bounded in-game journal that answers "where did it go" for items |
| `jawa/tps_*` (`JawaBenchTps*.cs`) | the always-on TPS recorder | precedent for a bounded writer and a lifecycle |

**Python harness that already exists** (`src/RimMandrake/Utils/modcheck/`):
- `helpers.storyteller_off`: `enableStoryteller=false`, `threatScale=0`, `allowBigThreats=false`, queue cleared, all
  through a restoring `SettingsTransaction`. Its own docstring says: *"NOT a general event freeze … quests, site logic
  and mod tickers can still raid."*
- `helpers.random_events_off`: random mental states and diseases off.
- `bland_world.setup` / `reset` / `assert_world`, which includes "incidents queued: N" as a problem.
- `detectors.py` and `watch.py`: the catalogue in `design/RimMandrake/northstar_helpers_plan.md` §3 already has
  `hostile_pawns`, `raid_arrived`, `manhunter`, `letter_unexpected`, `strangers_near_anchor` and
  `condition_unexpected`, each classed SURPRISE.
- `surprise.py`: evidence-before-action capture (sidecar JSON + one screenshot) when a detector fires.

⇒ **Detection exists, at a tripwire cadence, inside modcheck runs. Attribution does not.** `hostile_pawns` can
say "a hostile is here that is not in the expected set". It cannot say "it came from `RaidEnemy` at tick 61,203,
fired by the storyteller", or "our `spawn_pawn` made it". The expected set is supplied by the caller (the
harness's own spawned ids), and ad-hoc debugging outside modcheck has none of this.

### 2a. Event-leakage audit (MEASURED today from existing evidence, no bridge)

Method: parse every `Transient/modcheck/**/*summary.json`, excluding `J2_abort_proof` (that suite injects
hazards on purpose), and count `chains[].situational.hits_seen[].detector` in the event classes.
- **24 of 82** run summaries carry at least one event-class hit.
- Counts: `letter_unexpected` 289, `condition_unexpected` 38, `strangers_near_anchor` 18, `raid_arrived` 12, `hostile_pawns` 5.
- Sample hit texts, verbatim: *"1 non-player pawn(s) within 30 cells of the anchor"* (FlowWorks, BlueDesert ×6, Bacta),
  and *"colonist Human189794 took 1 damage event(s): Stab by Metalhorror"* (LeaningScrub, an Anomaly entity in a validation run).

⚠️ **24/82 is an upper bound, not a leakage rate.** The summaries do not record whether a hit was expected for
that chain, and some situational chains perturb the world deliberately. That missing field is the defect itself:
**the harness detects, but cannot say "uncontrolled".** The detector text names no pawn, no kind and no
origin. An agent reading "1 non-player pawn" must start the deep dive the owner describes.

Re-run this audit after O3 lands. The rate must then be computed from `origin` fields, not from detector names.

## 3. Provenance: what the engine can tell us

Facts read from decompiled 1.6 via RimSage on 2026-10-10 are marked **[RS]**.

**Already on every pawn, readable now:**
- `Faction` (null for wild/manhunter), `HostileTo(player)`, `kindDef`, `def`, `thingIDNumber` (UNVERIFIED that it
  is strictly monotonic; if it is, "id > watermark" is a free "arrived after mark" test).
- `GetLord()`, whose `LordJob` type distinguishes `LordJob_AssaultColony` (raid), `LordJob_VisitColony`
  (visitor), `LordJob_TradeWithColony` (trader) and so on. Class names are UNVERIFIED except as already used by
  `pawn_census`. It answers "what it is doing", not "who made it", and a wild animal has no Lord.
- `guest` status and `mindState.mentalState` (manhunter).
- **[RS]** `StoryState.lastFireTicks : Dictionary<IncidentDef,int>` is set in `StoryState.Notify_IncidentFired(FiringIncident fi)`
  (`StoryState.cs:88/100`) and is Scribed. That makes it a free, saved record of **the last tick each incident
  def fired on each target**. It is per-def-last only, so not a log. Still, a run can snapshot it at start and
  diff it at end, and any changed key is an incident that fired. **[RS] But it is written only from `Storyteller.cs:230` (`TryFire`) and `StorytellerUtility.cs:359`**, so an
  incident fired directly through `TryExecute` (quests, `jawa/fire_incident`, mod code) does NOT update it. It
  sees exactly the storyteller incidents that `storyteller_off` already stops, so it is a weak leak check.
- **[RS]** `Storyteller.RecordIncidentFired(IncidentDef)` keeps only a 4-entry anomaly ratio queue, so it is useless as a log.
- **[RS]** `IncidentWorker.TryExecute(IncidentParms)` calls `TryExecuteWorker(parms)`, records tales, then calls
  `Find.Storyteller.RecordIncidentFired(def)`. Its fields are `def` (the IncidentDef). **[RS]** `IncidentParms`
  carries `faction`, `forced`, `quest`, `questTag`, `raidStrategy`, `raidArrivalMode`, `sendLetter` and
  `storeGeneratedNeutralPawns`.
- **[RS]** A tale is recorded only when `def.tale` or `def.category.tale` is set, so `tale_list` is a partial record.

**Nothing on a pawn says why it exists.** I found no `spawnedBy` / origin field (UNVERIFIED as exhaustive; I
searched the entry points, not every field of `Pawn`). Provenance must be recorded at the moment of creation.

**Attribution design: tag at GENERATION, look up at SPAWN.** Hook points confirmed to exist **[RS]**:
- `PawnGenerator.GeneratePawn(PawnGenerationRequest)` (`Verse/PawnGenerator.cs:140`)
- `MapPawns.RegisterPawn(Pawn)` (`Verse/MapPawns.cs:832`)
- `Pawn.SpawnSetup(Map,bool respawningAfterLoad)` (`Verse/Pawn.cs:2616`)
- `IncidentWorker.TryExecute` (`RimWorld/IncidentWorker.cs:183`)
- `WildAnimalSpawner.SpawnRandomWildAnimalAt(IntVec3,bool,PawnKindDef)` (`WildAnimalSpawner.cs:109`)
- `MapGenerator.GenerateContentsIntoMap(...)` (`Verse/MapGenerator.cs:289`)
- class `QuestPart_PawnsArrive`

1. **A context stack** (a static `Stack<Origin>`, main thread only) is pushed by a prefix and popped by a
   finalizer on each of these, innermost first:
   - `IncidentWorker.TryExecute`: `incident:<def>` plus parms (faction, forced, quest, raidStrategy, arrivalMode)
   - `WildAnimalSpawner.SpawnRandomWildAnimalAt`: `wild-spawner`
   - `MapGenerator.GenerateContentsIntoMap`, refined per `GenStep` if cheap: `mapgen:<genstep>` (E1's insects)
   - **every JawaBench tool body**: `bridge:<tool>:<callSeq>`. This needs one wrapper at the dispatch point;
     whether JawaBench has a single dispatch is UNVERIFIED, and the fallback is a helper call in each spawn tool
   - quest arrival, via `QuestPart_PawnsArrive`'s signal handler (method name UNVERIFIED)
   - dev debug actions (hook point UNVERIFIED)
2. **Generation tag.** A postfix on `PawnGenerator.GeneratePawn` records `pawnId → top-of-stack origin` into a
   bounded dictionary. This handles **delayed arrival**: a drop-pod raid generates pawns inside `TryExecute` but
   spawns them later from a skyfaller or transporter. That generation happens inside the worker is UNVERIFIED
   per arrival mode and is exactly what acceptance test A3 checks.
3. **Spawn event.** A postfix on `MapPawns.RegisterPawn` (or `Pawn.SpawnSetup` with `!respawningAfterLoad`)
   appends to a `JawaEventRing<ArrivalEvent>`: tick, map, pawn id, kind, faction, hostile, cell, `origin`
   (generation tag, else the current stack top, else `UNATTRIBUTED`), plus `stackHint` = the first 3 non-Verse,
   non-Harmony frames of a `new StackTrace()`, but **only when origin is UNATTRIBUTED**. Spawns are rare, so the
   cost is negligible; the hint makes "something else" name the mod that did it.
4. **"Created by us" is exact** because it is pushed by our own tool and is not inferred. A pawn the harness made
   but whose origin reads `incident:…` is a bug in the tag.

**Lessons carried from TPS / lineage:**
- Every patch body is try/catch (the lineage recorders already do this). None of these points is a per-tick hot path.
- The ring is bounded (lineage uses 4096).
- State is game-scoped: clear on a new Game and record `gameId` on every row.
- Reads go through `ctx.MainThread.InvokeAsync`.
- Every read reports `installed` and `oldestRetained`, so "no arrivals" is never confused with "not recording".
- 🔴 **Install timing matters more here than for lineage.** Lineage installs on the first `jawa/` call, so the
  initial map's mapgen pawns (E1) would be missed. The arrival recorder must install at companion startup. The
  hooks are cold paths, so that is safe. UNVERIFIED that JawaBench has an early-enough static ctor hook; TPS's
  starter is the precedent.
- Pawns that were present before install are reported as `origin: PRE_INSTALL`, never blank.

## 4. Options O0–O4

| | what | cost | stability risk | answers | stays blind to |
|---|---|---|---|---|---|
| **O0 discipline** | a "first look" rule: before any theory, run `jawa/list_pawns` + `jawa/letter_list` (lookTargets) + `jawa/pawn_census` (lord) + `incident_queue_peek`; added to `skills/rimbridge` and `debug_process.md` | a skill edit, 1 h | none | what is there, whether it is hostile, and **sometimes** why: a letter's lookTargets name raid/wanderer/migration pawns | wild-spawner and mapgen arrivals (no letter), events with `sendLetter=false`, our own substituted spawns (E5), anything after the letter was dismissed; **Player.log contributes nothing** (§2) |
| **O1 `jawa/scene_report`** | one read-only tool: a compact table per pawn (id, kind, def, faction, hostile, cell, distance to anchor, lord job type, mental state) **joined to the letters whose lookTargets name it**, plus `lastFireTicks` diff since a `mark` | ~1 day C#, no Harmony | very low (read-only) | everything O0 does, in one call, with letter-based provenance; `mark`/`since` gives "new arrivals" via id watermark (if ids are monotonic) | same blind spots as O0 for origin: a wild/mapgen/silent arrival reads `origin: unknown` honestly |
| **O2 awareness mode** | O1 + the §3 arrival recorder; agent arms it with a TTL (default 30 min, auto-off, off by default); cadence rows (e.g. every 2,500 ticks) appended to a bounded JSONL beside the TPS record; `scene_report since=mark` prints "new arrivals: 2× Megaspider (mapgen:…), Whistler (incident:WandererJoin)" | ~3 days C#, plus 6 Harmony patches on cold paths and a writer | low to medium: new patches, a file writer (the TPS writer exists to copy) | **exact** origin for incident, wild-spawner, mapgen, bridge and quest arrivals; "created by us" exact | arrivals before install; mods that spawn pawns without `GeneratePawn` (cloning, deserialising) read UNATTRIBUTED + stackHint; things that are not pawns (fires, items) |
| **O3 quiet-world profile + assertion** | the existing `storyteller_off` + `random_events_off`, plus O3-lite: one postfix on `IncidentWorker.TryExecute` appending (tick, def, target, forced, quest, faction) to a ring (`lastFireTicks` diff alone misses non-storyteller fires, §3); with O2, assert **every arrival's origin ∈ {bridge:*, expected incidents}**, else the run is `CONTAMINATED` (not FAIL, not PASS) and names the arrival | O3-lite (one TryExecute postfix + read tool): ~0.5 day; O3-full needs O2 | low | "was this run clean?" as a recorded fact, per run; turns the 24/82 upper bound into a real rate | the cause of quest/site/mod-ticker raids (which `storyteller_off` cannot stop, per its own docstring) is reported, not prevented |
| **O4 all of it** | O1+O2+O3 plus auto-capture of `surprise.py` evidence on any UNATTRIBUTED arrival, plus a "freeze" that also suspends quests and mod tickers | +1–2 weeks | medium to high: a quest/ticker freeze touches many mods' internals | the most | that freeze is the dangerous part: it changes the game being tested |

**Not recommended:** a timed cadence reporter as the main interface. The cadence is only there so the JSONL has a
timeline when nobody asked. Agents get more value from `since=mark` diffs taken at their own step boundaries.
The cadence rows are a cheap extra once the writer exists, and should never be required.

## 5. Recommendation and acceptance tests

**Recommendation: build the attribution (O1 + the O2 recorder, always-on but tiny) and wire O3's assertion into
validation and north-star runs. Skip O4's freeze.** Why, in one line: Player.log records **no** incident or
arrival at all (§2), and today's detectors already see "1 non-player pawn" in 24 of 82 runs but cannot say
whose it is. The missing piece is provenance, which only an in-game hook at creation can supply. Discipline
cannot read a line that was never written.

Sequencing:
1. **O0 now.** A skill paragraph costs nothing and covers the letter-visible cases.
2. **O3-lite** (one cold `TryExecute` postfix) next. It immediately makes "an incident fired during this run" a recorded fact.
3. **O1 + recorder** as one companion build.
4. **O3-full** on top of the recorder.

Make the recorder always-on rather than "armed". It sits on cold paths with a bounded ring, the same reasoning
TPS used to become standing. Only the JSONL cadence writer is armed with a TTL, so normal play writes nothing
to disk.

Acceptance tests (each must FAIL while the defect exists):

| id | option | test |
|---|---|---|
| A0 | O0 | Give a fresh agent a recorded scene with one raid pawn and one wild Megaspider: it must name the raid pawn's origin from letter lookTargets **and** say "origin unknown" for the Megaspider. A guess fails |
| A1 | O1 | On a bland map, `mark`; `jawa/spawn_pawn` ×3 of a known kind; `fire_incident RaidEnemy`; step until arrival. `scene_report since=mark` must list exactly the 3 + the raiders, the raiders joined to the raid letter, and the incident ring since mark `== [RaidEnemy]`. With today's tools the join does not exist, so it fails |
| A2 | O2 | Same scene, plus a `HerdMigration` incident, a forced `SpawnRandomWildAnimalAt`, and one `spawn_pawn` whose kind is substituted (E5). Each arrival's origin must read `bridge:jawa/spawn_pawn` ×3 (**including the substituted one**, with `requestedKind ≠ kind`), `incident:RaidEnemy`, `incident:HerdMigration` and `wild-spawner` respectively; zero UNATTRIBUTED |
| A3 | O2 | Drop-pod raid (`raidArrivalMode` = a drop-pod mode, defName UNVERIFIED): pawns spawn ticks after `TryExecute` returned; origin must still be `incident:RaidEnemy`. This is the test that proves generation-tagging, and stack-at-spawn alone fails it |
| A4 | O2 | Generate a new map: the mapgen insects (E1) must read `mapgen:*`, not `PRE_INSTALL`/UNATTRIBUTED. Fails under lazy install |
| A5 | O3 | A north-star chain under `storyteller_off`; fire one `WandererJoin` via a quest-like path outside the storyteller. The run must end `CONTAMINATED` naming that pawn; the same chain without the injection must end clean. Run the 82-summary audit again: the rate must now come from origins |

## 6. Ten questions for an adversarial reviewer

1. Is `thingIDNumber` strictly monotonic within a game (and across save/load)? If not, `since=mark` needs the recorder, and O1 alone cannot diff.
2. Do all raid arrival modes (edge walk-in, drop pods, centre drop, shuttle) generate pawns inside `IncidentWorker.TryExecute`, or does any generate them later (making the generation tag miss)?
3. Do quest-generated pawns get generated at quest-offer time (long before arrival, under no context we push), and is `QuestPart_PawnsArrive` the single arrival funnel?
4. Is `MapPawns.RegisterPawn` called for every spawn including pawns emerging from containers, transporters, caravans entering and pocket-map exits, and does it also fire on load (which must be excluded)?
5. Does JawaBench have a single tool-dispatch point where the `bridge:<tool>` context can be pushed once, or must every spawn tool opt in? And what about `rimworld/*` RimBridgeServer tools and dev debug actions?
6. Can the recorder be installed early enough to catch the first map's mapgen, given companion load order and `StaticConstructorOnStartup` timing?
7. Do any incidents bypass `IncidentWorker.TryExecute` entirely (a mod calling `TryExecuteWorker`, or a quest part spawning pawns with no IncidentDef)? (Checked: `lastFireTicks` is storyteller-path only, `Storyteller.cs:230`, which is why O3-lite moved to a `TryExecute` postfix.)
8. Is the 24/82 figure dominated by deliberate situational perturbations? Someone must classify a sample by hand before it is quoted as leakage.
9. Is "always-on recorder" acceptable given the owner's "debug mode only" framing? Would a TTL-armed recorder lose the E1 case (arrivals before the agent armed it)?
10. Is the owner's anecdotal cost ("several tickets to work out what a creature is") supported by transcripts? This pass found run-invalidation costs (E1, E5, E6) but no ticket chain spent on identification alone; if that cost is rare, O0 + O3-lite may be the whole answer.
