---
name: rimworld-custom-incidents
description: Build our own RimWorld 1.6 incidents and storyteller pacing — an IncidentDef plus IncidentWorker, a follow-up through the IncidentQueue, a pay-or-fight or take-or-refuse choice held save-safely in a ChoiceLetter, a per-faction memory that changes what arrives, or a comp patched into vanilla Randy. Covers every CanFireNow gate, forced versus bypassStorytellerSettings, what actually stamps a cooldown and the ThreatBig clock, shared cooldowns by tag, population intent, threat points and making danger qualitative instead of bigger, letters, save-safe pending choices and test hooks. Use for any new event, raid variant, extortion, visitor, disaster, infestation-like threat or pacing rule, or "a mod that makes X happen sometimes"; when an incident never fires, fires twice, or "fired" with nothing arriving; when a follow-up silently never came; and before patching any vanilla IncidentWorker. For QuestScriptDef authoring use rimworld-quests; for who joins, leaves or comes back use rimworld-crew-and-nemesis-events.
---

# Our own incidents and storyteller behaviour

Distilled from the event mods we are retiring (Raid Protection Fee, Tribute Demand, Faction
Raid Cooldown, Storyteller Enhanced, More Faction Interaction, Better Infestations, Space
Worms, Large Faction Bases), so writing *our* version is a half-day job instead of a research
project. Full study, engine evidence and the idea catalogue:
`design/RimMandrake/event_quest_wisdom.md`. This skill is the recipe and the traps.

## 1. Pick the vehicle first (cheapest that works)

| you want | vehicle | C#? |
|---|---|---|
| a reworded / re-gated vanilla event | XML patch on the vanilla `IncidentDef` (category, baseChance, minRefireDays, allowedBiomes) | no |
| a new event with its own spawn logic | `IncidentDef` + `IncidentWorker` subclass | yes, small |
| a choice the player may sit on (pay/refuse, let in/turn away) | a `ChoiceLetter` subclass with Scribed fields and a timeout | yes, small |
| "it comes back in 3-5 days" | `Find.Storyteller.incidentQueue.Add(def, fireTick, parms, retryTicks)` — saved by vanilla | one call |
| a scripted beat that ignores difficulty/scenario bans but keeps biome rules and spacing | `parms.bypassStorytellerSettings = true` (not `forced`) | none |
| a multi-step situation with a timer, a person and priced endings | a `QuestScriptDef` (see `rimworld-quests`) | usually no |
| new pacing (a rhythm, a mood, a guaranteed beat) | append a comp to `StorytellerDef[defName="Randy"]/comps` — vanilla comp classes take numbers | no |
| the world remembers something and it changes what arrives | one Scribed `GameComponent` + a postfix on a **boolean gate** | yes |

Prefer the higher row. Every studied mod that broke something had taken a lower row than it
needed (Harmony on a vanilla worker where its own worker would do).

## 2. The recipe (each step answers one question)

1. **Trigger — who decides it happens?** A storyteller comp picks it by category weight
   (`category`, `targetTags`, `baseChance`), or our code schedules it, or a quest emits it.
   Our code schedules through `Storyteller.TryFire` or the queue, never `Worker.TryExecute`
   directly (that skips the gates *and* the cooldown stamp). One owner per incident.
2. **Gate — when must it not happen?** XML first: `earliestDay`, `minRefireDays`,
   `minPopulation`, `minThreatPoints`/`maxThreatPoints`, `allowedBiomes`/`disallowedBiomes`,
   `layerWhitelist`/`layerBlacklist`, cooldown groups via `tags` + `refireCheckTags` (same
   `minRefireDays` on every member). Put only what XML cannot say in `CanFireNowSub`; it is
   cached per tick **per def, not per target**, so keep it target-independent where you can.
3. **Scale — how dangerous?** `parms.points` already reflects wealth, crew and adaptation. Our
   knob is **what** arrives: `raidStrategy`, `raidArrivalMode`, `attackTargets`, `canKidnap`,
   `canSteal`, `canTimeoutOrFlee`, `raidForceOneDowned`, `pawnKind`, a named enemy, a demand.
4. **Letter — what does the player read?** One letter per real outcome, written for this world,
   naming the faction and the count. A choice lives in a `ChoiceLetter` (or a quest), never in a
   plain letter that pretends to be a choice.
5. **Outcome — what is true afterwards?** Spawn, goodwill with a `HistoryEventDef` reason, a
   queued follow-up (with a retry window), or a record in a component.
6. **Cleanup — what is left behind?** Pawns generated and not spawned go back with
   `Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard)` (never on a spawned pawn);
   per-map state dies with the map; every list we keep has a cap.
7. **Test hook — can a bridge or dev action fire it deterministically?** A settings toggle that
   takes the default branch, and one log line per outcome.

## 3. Traps (each one cost a mod we studied, or the engine does it silently)

- 🔴 **Returning `true` before anything happened.** `Storyteller.TryFire` stamps the cooldown
  and the ThreatBig clock (`StoryState.Notify_IncidentFired`) whenever `TryExecute` returns
  true. A worker — or a Harmony prefix setting `__result = true` — that opens a dialog and
  returns true is counted as fired with zero pawns: the Raid Protection Fee defect of our
  2026-10-10 live pass. Return true only when "the player was asked" *is* the outcome, and hold
  the pending choice in a `ChoiceLetter` (`references/recipes.md` §2), never a closure.
- 🔴 **`requireColonistsPresent` with the crew away returns true having done nothing** — the
  incident is consumed and its cooldown stamped. For a crew often off-ship, refuse in
  `CanFireNowSub` so the storyteller picks something else.
- 🔴 **Pending state in statics or closures.** A modal `Dialog_NodeTree` pauses play but does
  not prevent saving; static or lambda-held state is lost or stale across save/load.
- 🔴 **`forced = true` skips every generic gate and stamps nothing** (no cooldown, no ThreatBig
  clock), though `CanFireNowSub` still runs. A ban written as a generic-gate patch is invisible
  to forced fires; a ban written as an XML zero is invisible to a mod's *other* defs. Bans name
  every def that produces the effect.
- **A queued incident with no retry window that fails at its tick is dropped without a log.**
- **Joiners without `populationEffect`** escape the population-intent throttle that keeps a
  six-person crew at six.
- **Global multipliers on hot methods** (`Thing.TakeDamage`, `Thought.MoodOffset`) are stat
  inflation and a per-call cost.
- **Worker instance fields** set in `CanFireNowSub` and read in `TryExecuteWorker`: the worker
  is a shared singleton.
- **Per-faction data registered only at load**, or **counting the wrong event**
  (`Faction.Notify_MemberDied` fires for any death of that faction, anywhere).
- **Unbounded save lists**, and **two mods answering one beat** (two extortion letters).

## 4. Where the depth lives

- `design/RimMandrake/event_quest_wisdom.md` §1 — the vanilla pipeline, every gate in order,
  what stamps what, selection weights, population intent, threat points, Randy's comps, the
  IncidentQueue, `ChoiceLetter` and world-pawn facts, the `IncidentParms` levers (VERIFIED
  against decompiled 1.6).
- `references/recipes.md` — sketches: the XML-only incident, the ChoiceLetter choice, queue
  follow-ups, a calendar/heartbeat component, the boolean-gate postfix, a comp appended to
  Randy, test hooks, and a "what stamps what" table.
- `references/mod_lessons.md` — one paragraph per studied mod: copy this, not that.
- Study §6 — 33 ideas for this campaign with mechanism sketches and costs.
