---
name: rimworld-custom-incidents
description: Build our own RimWorld 1.6 incidents and storyteller pacing — an IncidentDef plus IncidentWorker, a follow-up through the IncidentQueue, a pay-or-fight or take-or-refuse choice held save-safely in a ChoiceLetter, a per-faction memory that changes what arrives, or a comp patched into vanilla Randy. Covers every CanFireNow gate, forced versus bypassStorytellerSettings, what actually stamps a cooldown and the ThreatBig clock, shared cooldowns by tag, population intent, threat points and making danger qualitative instead of bigger, letters, save-safe pending choices and test hooks. Use for any new event, raid variant, extortion, visitor, disaster, infestation-like threat or pacing rule, or "a mod that makes X happen sometimes"; when an incident never fires, fires twice, or "fired" with nothing arriving; when a follow-up silently never came; and before patching any vanilla IncidentWorker. For QuestScriptDef authoring use rimworld-quests; for who joins, leaves or comes back use rimworld-crew-and-nemesis-events.
---

# Our own incidents and storyteller behaviour

With this skill, our own version of an event mod is a half-day job, not a research project. This file holds the recipe
and the traps.

The lessons come from eight event mods:

- active on the owner's full mod list of 2026-11-20: Tribute Demand and Space Worms;
- not on that list: Raid Protection Fee, Faction Raid Cooldown, Storyteller Enhanced, More Faction Interaction, Better
  Infestations and Large Faction Bases.

Where the evidence is:

- The full study, the engine evidence and the idea catalogue: `design/RimMandrake/event_quest_wisdom.md`.
- The evidence for each mod: §2 of that study. Corrected lines and their evidence: `references/history.md`.

A **gate** is a condition that stops an incident. A **generic gate** is a check in `IncidentWorker.CanFireNow` that
`parms.forced` skips. To **stamp** the cooldown is to record the fire time of the incident in the `StoryState` of the target.
The **ThreatBig clock** is the tick of the last unforced fire in category ThreatBig. Each target has its own clock.
After enough days with no such fire, Randy tries ThreatBig first. So a false stamp delays the next big threat.

## 1. Pick the vehicle first (cheapest that works)

| you want | vehicle | C#? |
|---|---|---|
| a vanilla event with new words or new gates | an XML patch on the vanilla `IncidentDef` (category, baseChance, minRefireDays, allowedBiomes) | no |
| a new event with its own spawn logic | an `IncidentDef` and a subclass of `IncidentWorker` | yes, small |
| a choice that the player may leave open for a time (pay or refuse, let in or turn away) | a `ChoiceLetter` subclass with Scribed fields and a timeout | yes, small |
| "it comes back in 3-5 days" | `Find.Storyteller.incidentQueue.Add(def, fireTick, parms, retryTicks)`. Vanilla saves the queue. | one call |
| a scripted beat that ignores difficulty bans, scenario bans and `earliestDay`, but keeps biome rules and spacing | `parms.bypassStorytellerSettings = true` (not `forced`) | one field, where our code makes the `parms` |
| a multi-step situation with a timer, a person and priced endings | a `QuestScriptDef` (see the skill `rimworld-quests`) | usually no |
| new pacing (a rhythm, a mood, a guaranteed beat) | append a comp to `StorytellerDef[defName="Randy"]/comps`. The vanilla comp classes take numbers. | no |
| the world remembers something, and that memory changes what arrives | one Scribed `GameComponent` and a Harmony postfix on a **boolean gate** (a method that returns yes or no) | yes |

Prefer the higher row. Every studied mod that broke something had taken a lower row than it needed. An example is a
Harmony patch on a vanilla worker where a worker of the mod itself was enough.

## 2. The recipe (each step answers one question)

1. **Trigger — who decides it happens?** There are three triggers:
   - a storyteller comp picks the incident by category weight (`category`, `targetTags`, `baseChance`);
   - our code schedules the incident;
   - a quest emits the incident.

   Our code schedules through `Storyteller.TryFire` or through the queue. Never call `Worker.TryExecute` directly. A
   direct call skips the gates *and* the cooldown stamp. Let only one of the three triggers start an
   incident.
2. **Gate — when must it not happen?** Use the XML gates first:
   - `earliestDay`, `minRefireDays` and `minPopulation`;
   - `minThreatPoints`/`maxThreatPoints`;
   - `allowedBiomes`/`disallowedBiomes`;
   - `layerWhitelist`/`layerBlacklist`;
   - a cooldown group, through `tags` + `refireCheckTags`. Give every member of the group the same `minRefireDays`.

   Put only what XML cannot say in `CanFireNowSub`. The game caches the result of `CanFireNowSub` per tick **per def,
   not per target**. So keep `CanFireNowSub` target-independent where you can.
3. **Scale — how dangerous?** `parms.points` already reflects wealth, crew and adaptation. Our knob is **what**
   arrives: `raidStrategy`, `raidArrivalMode`, `attackTargets`, `canKidnap`, `canSteal`, `canTimeoutOrFlee`,
   `raidForceOneDowned`, `pawnKind`, a named enemy, or a demand.
4. **Letter — what does the player read?** Send one letter for each real outcome. Write the letter for this world. Name
   the faction and the count. Put a choice in a `ChoiceLetter` or in a quest. Never put a choice in a plain letter that
   pretends to be a choice.
5. **Outcome — what is true afterwards?** The outcome is one or more of these:
   - something spawns;
   - goodwill changes, with a `HistoryEventDef` reason;
   - a follow-up goes in the queue, with a retry window;
   - a component holds a record.
6. **Cleanup — what is left behind?**
   - If a pawn was generated and not spawned, give it back with
     `Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard)`. Never do this to a spawned pawn.
   - State that belongs to a map dies with the map. So keep it in a `MapComponent`, or delete it when the map goes.
   - Every list that we keep has a cap.
7. **Test hook — can a bridge or dev action fire it deterministically?** Add a settings toggle that skips the
   choice. With that toggle on, the game applies the result of a timeout. Write one log line for each outcome.

## 3. Traps (each one cost a mod we studied, or the engine does it silently)

- 🔴 **Returning `true` before anything happened.** `Storyteller.TryFire` stamps the cooldown and the ThreatBig clock
  whenever `TryExecute` returns true (`StoryState.Notify_IncidentFired`). Only a `forced` fire is not stamped.
  - A worker that opens a dialog and returns true counts as fired, with zero pawns. A Harmony prefix that sets
    `__result = true` does the same. Raid Protection Fee had this defect.
  - Return true only when "the player was asked" *is* the outcome. Then hold the pending choice in a `ChoiceLetter`
    (`references/recipes.md` §2). Never hold the choice in a closure.
- 🔴 **`requireColonistsPresent` with the crew away returns true having done nothing.** The incident is consumed and
  its cooldown is stamped. Our crew is often off-ship. So refuse in `CanFireNowSub`; then the storyteller can pick
  something else.
- 🔴 **Pending state in statics or closures.** A modal `Dialog_NodeTree` pauses play but does not prevent saving. State
  in a static or a lambda is lost or stale after a save and load.
- 🔴 **`forced = true` skips every generic gate and stamps no cooldown and no ThreatBig clock.** `CanFireNowSub` still
  runs.
  - A forced fire ignores a ban that is a patch on a generic gate.
  - A ban that sets one def to zero in XML does not reach the *other* defs of that mod.
  - So a ban names every def that produces the effect.
- **A queued incident with no retry window is dropped without a log** if the incident fails at its tick.
- **Joiners without `populationEffect`** escape population intent. So set `populationEffect` on each joiner def:
  `IncreaseHard`, `IncreaseMedium` or `IncreaseEasy`. Population intent is a storyteller factor. The
  factor is high for a small crew and low for a large crew. This throttle keeps a six-person crew at about six. Under
  Randy, the throttled chance never goes to zero. The throttle acts only when the storyteller picks at random. A queued
  or direct fire ignores the throttle.
- **Global multipliers on hot methods** (`Thing.TakeDamage`, `Thought.MoodOffset`) are stat inflation. Such multipliers also cost
  time on every call.
- **Worker instance fields.** Do not set a field of the worker in `CanFireNowSub` and read the field in
  `TryExecuteWorker`. One worker object serves every fire of the def.
- **Per-faction data registered only at load.** A faction that appears later then has no data.
- **Counting the wrong event.** `Faction.Notify_MemberDied` fires for any death of a member of that faction, anywhere.
- **Unbounded save lists.** Cap each list.
- **Two mods answering one beat.** An example is two extortion letters for one raid.
- 🔴 **A `ChoiceLetter` option with `resolveTree=true` only closes the dialog.** The letter stays on the stack, and the
  player can click the option again until the timeout. A Sell option of ours paid 1500 silver per click.
  - Every one-shot choice must remove the letter itself, with `Find.LetterStack.RemoveLetter(this)`.
  - The ready-made vanilla options differ. `Option_Close`, `Option_Reject` and `Option_JumpToLocation` remove the
    letter. `Option_ViewInQuestsTab` removes the letter unless you pass `postpone`. `Option_Postpone` and
    `Option_JumpToLocationAndPostpone` keep the letter.
  - A removed letter stays in the archive, and the player can open it there. So when `ArchivedOnly` is true, let
    `Choices` return only `Option_Close`. The vanilla `ChoiceLetter_RansomDemand` does this.
  - A player must not escape a demand by removing its letter. So set `CanDismissWithRightClick` to false, as the vanilla
    `ChoiceLetter_AcceptVisitors` does. On a live demand, offer no vanilla option that removes the letter. Write your own
    Refuse option. Use `Option_JumpToLocationAndPostpone` and `Option_Postpone`.
  - `RemoveLetter` calls `Removed()` each time, also for a letter in the archive. So Scribe a `resolved` flag. Set the
    flag in each one-shot action, before `RemoveLetter`, and when the default branch runs. Apply the default branch in
    `Removed()` only if `TimeoutPassed && !resolved`.
- **`GenAdj.CellsAdjacent8Way(thing)` is not bounds-checked.** Test each cell with `InBounds(map)`.
- **`ThingDef.terrainAffordanceNeeded` is null for most items.** Only some stuff items hold a value, for example metals
  and wood. `TryFindSkyfallerCell(...null...)` rejects every cell. So pass an affordance of your own, for example
  `TerrainAffordanceDefOf.Light` or `Walkable`.
- **"Any faction of def X" is unsafe for Sanguophages (and any def quests spawn ad hoc).**
  - Vanilla `QuestNode_Root_SanguophageMeetingHost` makes a temporary Sanguophages faction. That faction is
    player-NEUTRAL, and the quest reserves it.
  - Vanilla `QuestNode_Root_SanguophageShip` makes a temporary Sanguophages faction that is hostile to all.
  - Before you put your own pawns in a faction, filter on `!temporary`, `!defeated` and the relation that you need.
    For raiders, that relation is `HostileTo(Faction.OfPlayer)`.

## 4. Where the depth lives

- `design/RimMandrake/event_quest_wisdom.md` §1 is the engine primer. Someone checked §1 against decompiled 1.6
  (VERIFIED). §1 marks the few claims that nobody checked (UNVERIFIED). The primer holds:
  - the vanilla pipeline, every gate in order, and what stamps what;
  - selection weights, population intent, threat points and Randy's comps;
  - the IncidentQueue, `ChoiceLetter` and world-pawn facts, and the `IncidentParms` levers.
- `references/recipes.md` holds sketches:
  - the XML-only incident, the ChoiceLetter choice and queue follow-ups;
  - a calendar or heartbeat component, the boolean-gate postfix and a comp appended to Randy;
  - test hooks, and a "what stamps what" table.
- `references/mod_lessons.md` has one paragraph for each studied mod: copy this, not that.
- `design/RimMandrake/event_quest_wisdom.md` §6 has 33 ideas for this campaign, with mechanism sketches and costs.
