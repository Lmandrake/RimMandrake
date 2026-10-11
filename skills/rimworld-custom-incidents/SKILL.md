---
name: rimworld-custom-incidents
description: Design and build our OWN small RimWorld 1.6 incidents and storyteller behaviour — an IncidentDef plus IncidentWorker, a delayed follow-up through the IncidentQueue, a choice dialog (pay or fight, take or refuse), a per-faction memory that changes what arrives, or an extra comp patched into vanilla Randy — distilled from studying the event mods we are retiring (Raid Protection Fee, Tribute Demand, Faction Raid Cooldown, Storyteller Enhanced, More Faction Interaction, Better Infestations, Space Worms, Large Faction Bases). Covers the vanilla firing pipeline and every gate CanFireNow checks, why `forced` skips cooldowns and biome bans, why a worker that returns true before its dialog resolves counts as fired with zero pawns, shared cooldowns by tag, population intent, threat points and how to make danger qualitative instead of bigger, letters, save-safe state, and test hooks. Use whenever someone wants a new event, raid variant, extortion, visitor, disaster, infestation-like threat, storyteller pacing rule, or "a mod that makes X happen sometimes", when an incident never fires or fires twice, when a raid "fired" but nothing arrived, or before patching any vanilla IncidentWorker. For QuestScriptDef authoring use rimworld-quests; for who joins, leaves or comes back use rimworld-crew-and-nemesis-events.
---

# Our own incidents and storyteller behaviour

The retiring event mods were studied for one reason: so that writing *our* version is a
half-day job instead of a research project. Full study, evidence and the idea catalogue:
`design/RimMandrake/event_quest_wisdom.md`. This skill is the recipe and the traps.

## 1. Pick the vehicle first (cheapest that works)

| you want | vehicle | C#? |
|---|---|---|
| a reworded / re-gated vanilla event | XML patch on the vanilla `IncidentDef` (category, baseChance, minRefireDays, allowedBiomes) | no |
| a new event with its own spawn logic | `IncidentDef` + `IncidentWorker` subclass | yes, small |
| "it comes back in 3-5 days" | `Find.Storyteller.incidentQueue.Add(def, fireTick, parms, retryTicks)` — saved by vanilla | one call |
| a multi-step situation with a timer, a choice and priced endings | a `QuestScriptDef` (see `rimworld-quests`) | usually no |
| new pacing (a rhythm, a mood, a guaranteed beat) | patch a comp into `StorytellerDef[defName="Randy"]/comps` — vanilla comp classes take numbers | no |
| the world remembers something and it changes what arrives | one `GameComponent` (Scribed) + a postfix on a **boolean gate** | yes |

Prefer the row higher in the table. Every mod studied that broke something had taken a
lower row than it needed (Harmony on a vanilla worker where its own worker would do).

## 2. The recipe (each step answers one question)

1. **Trigger — who decides it happens?** A storyteller comp picks it by category weight
   (set `category`, `targetTags`, `baseChance`), or our code queues it, or a quest emits it.
   If both a comp and our code can fire it, give it one owner.
2. **Gate — when must it not happen?** Use the XML gates before code: `earliestDay`,
   `minRefireDays`, `minPopulation`, `minThreatPoints`/`maxThreatPoints`, `allowedBiomes`/
   `disallowedBiomes`, `layerWhitelist`/`layerBlacklist`, and shared cooldown groups via
   `tags` + `refireCheckTags`. Put only what XML cannot say in `CanFireNowSub`, and keep it
   cheap and side-effect free (it is cached per tick, and Rand there shifts the RNG).
3. **Scale — how dangerous?** `parms.points` already reflects wealth, crew and adaptation.
   For us the knob is **what** arrives (kind, arrival mode, target, a named enemy, a demand),
   not more of it. `IncidentParms` has the qualitative levers: `raidStrategy`,
   `raidArrivalMode`, `attackTargets`, `canKidnap`, `canSteal`, `canTimeoutOrFlee`,
   `raidForceOneDowned`, `pawnKind`, `pawnGroupMakerSeed`.
4. **Letter — what does the player read?** One letter per real outcome, written for this
   world; name the faction and the count. A choice belongs in a `DiaNode` dialog *or* a quest,
   never a letter that pretends to be a choice.
5. **Outcome — what is true afterwards?** Spawn, change goodwill (with a `HistoryEventDef`
   reason the faction tab can show), queue a follow-up, or record into a component.
6. **Cleanup — what is left behind?** Generated pawns you did not spawn go back with
   `Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard)`; per-map state dies with
   the map; any list we keep has a cap.
7. **Test hook — can a bridge or dev action fire it deterministically?** A settings toggle
   or a `forced` path that skips the dialog and the RNG, and a log line naming the outcome.

## 3. Traps (each one cost a mod we studied)

- 🔴 **Returning `true` before anything happened.** `IncidentWorker.TryExecute` returns the
  worker's bool and records the incident as fired either way; a worker (or a Harmony prefix
  setting `__result = true`) that opens a dialog and returns true reports success with zero
  pawns. That is exactly how Raid Protection Fee swallowed a RaidEnemy in our 2026-10-10 live
  pass. If the outcome waits on the player, say so in the log, and make tests able to bypass it.
- 🔴 **Deferred state in statics.** A pending choice held in a static field or a lambda closure
  is lost on save/quit. Keep what the resume needs on a Scribed component, or resolve before
  the player can save.
- 🔴 **`forced = true` skips every generic gate** (cooldown, biome, earliestDay, population,
  difficulty) but still runs `CanFireNowSub`. A ban written as a generic-gate patch is
  invisible to forced fires; a ban written as an XML zero is invisible to a mod's *other*
  IncidentDefs (Better Infestations' `BI_*` defs bypass our planet-wide Infestation ban).
  Bans must name every def that produces the effect.
- **Joiners without `populationEffect`** escape the population-intent throttle that keeps a
  6-person crew at six. Set it on any event that adds a person.
- **Patching a hot vanilla method for a global multiplier** (`Thing.TakeDamage`,
  `Thought.MoodOffset`) is stat inflation, runs on every call, and breaks the ruling anyway.
- **Registering per-faction data only at load**: factions made mid-game get nothing until
  reload. Register lazily on first lookup.
- **Counting the wrong event**: `Faction.Notify_MemberDied` fires for any death of that faction
  anywhere. Hook what you mean (killed on our map, by us).
- **Unbounded save lists** (every raider ever, every encounter): cap them, prune by
  notability, release world-pawn pins you placed.
- **Two mods answering one beat** (Raid Protection Fee and Tribute Demand both extort): pick one
  owner per player-facing beat.

## 4. Where the depth lives

- `design/RimMandrake/event_quest_wisdom.md` §1 — the vanilla pipeline, every gate in
  order, selection weights, population intent, threat points, Randy's comps and numbers,
  IncidentQueue, the `IncidentParms` levers (all VERIFIED against decompiled 1.6).
- `references/recipes.md` — sketches: the XML-only incident, the choice-before-threat worker
  done right, IncidentQueue follow-ups, a calendar/heartbeat component, the boolean-gate
  postfix, a comp patched into Randy, test hooks.
- `references/mod_lessons.md` — one paragraph per studied mod: the mechanism worth copying
  and the defect worth not copying.
- `design/RimMandrake/event_quest_wisdom.md` §6 — the idea catalogue with mechanism sketches
  and costs for this campaign.
