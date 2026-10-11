# Recipes: incident shapes worth copying

Sketches, not compiled code. Every engine name below was read from decompiled 1.6 (RimSage,
2026-10-10) or from a shipping mod's source; nothing else is guaranteed. Before building,
re-read the vanilla method you lean on. Engine facts and their sources:
`design/RimMandrake/event_quest_wisdom.md` §1; per-mod evidence: §2.

## Contents
1. The XML-only incident (gates, shared cooldowns)
2. Choice-before-threat: a ChoiceLetter (the Tribute Demand shape, fixed)
3. "It comes back later": IncidentQueue
4. Calendar or heartbeat component
5. Boolean-gate postfix (faction memory)
6. Adding pacing to Randy without a new storyteller
7. Test hooks
8. What stamps what

## 1. The XML-only incident

```xml
<IncidentDef>
  <defName>RM_SomethingHappens</defName>
  <label>something happens</label>
  <category>ThreatSmall</category>            <!-- the storyteller's pool; Misc is not threat-budgeted -->
  <targetTags><li>Map_PlayerHome</li></targetTags>
  <workerClass>RimMandrake.Events.IncidentWorker_SomethingHappens</workerClass>
  <baseChance>0.8</baseChance>
  <earliestDay>20</earliestDay>
  <minRefireDays>15</minRefireDays>
  <tags><li>RM_Extortion</li></tags>             <!-- this def's group name -->
  <refireCheckTags><li>RM_Extortion</li></refireCheckTags>  <!-- respects every def tagged so -->
  <populationEffect>None</populationEffect>      <!-- set IncreaseHard/Medium/Easy if it adds a person -->
  <minThreatPoints>300</minThreatPoints>
  <pointsScaleable>true</pointsScaleable>
  <letterDef>ThreatSmall</letterDef>
</IncidentDef>
```

`refireCheckTags` makes `FiredTooRecently` look at every def whose `tags` contain a listed tag
(VERIFIED, IncidentDef.cs ~155-200), measured against **this** def's `minRefireDays` — give every
member of a group the same value; a member with 0 opts out. Cooldowns are per target (the map's
StoryState), and a `forced` fire neither respects nor sets them.

## 2. Choice-before-threat: a ChoiceLetter

Tribute Demand's shape — show the threat, let the player decide, deliver or discard — with its
flaw removed (it, like Raid Protection Fee, returned `true` while a dialog closure held the
pawns).

**Preferred: a `ChoiceLetter` subclass holds the pending choice** (all types VERIFIED,
2026-10-10 review): `ChoiceLetter : LetterWithTimeout : Letter`; `LetterStack` Scribes letters;
`ChoiceLetter.OpenLetter` rebuilds its `DiaNode` from the abstract `Choices` property every
time it opens; `StartTimeout(ticks)` sets `disappearAtTick`; on timeout the stack removes the
letter through `Letter.Removed()`.

1. `TryExecuteWorker` resolves faction, strategy, arrival mode and points — **no pawns yet** —
   creates `ChoiceLetter_RM_Demand` with those as fields, `StartTimeout(...)`,
   `Find.LetterStack.ReceiveLetter(letter)`, logs `RM_Demand ASKED <faction> <points>`, and
   returns true. The true now means "the demand was made", which is the real outcome.
2. The subclass Scribes its fields in `ExposeData` (faction reference, points, defs, the demand
   list) so it survives save/load with no component.
3. `Choices` builds Pay / Refuse from those fields; disable Pay with a reason when the colony
   cannot pay. Refuse rebuilds `IncidentParms` from the fields and delivers the raid then
   (through the queue at `now`, or a direct worker call with `bypassStorytellerSettings`).
4. Override `Removed()`: if `TimeoutPassed`, apply the default branch (usually Refuse). Do not
   rely on the last-tick auto-open — it is skipped while another force-pause window is open.
   Vanilla precedents: `ChoiceLetter_RansomDemand`, `ChoiceLetter_AcceptVisitors`.

Showing "these exact pawns" before they exist would need regenerating them from a Scribed
`pawnGroupMakerSeed`; whether the seed alone fixes gear and backstory is UNVERIFIED — test first,
or describe the force instead of the pawns.

**Fallback: a modal `Dialog_NodeTreeWithFactionInfo`** (Tribute Demand's own shape) only with
`preventSave = true` set on the window: `Dialog_NodeTree` force-pauses but does not block saving
(VERIFIED). Resolve inside the option's `action`, and log the outcome.

Raid plumbing as Tribute Demand runs it (from its shipped source): resolve faction
(`PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup`), strategy and arrival mode,
`raidStrategy.Worker.TryGenerateThreats`, `raidArrivalMode.Worker.TryResolveRaidSpawnCenter`,
`IncidentWorker_Raid.AdjustedRaidPoints`, `IncidentParmsUtility.GetDefaultPawnGroupMakerParms`,
`PawnGroupMakerUtility.GeneratePawns`; deliver with `raidArrivalMode.Worker.Arrive(pawns, parms)`
+ `raidStrategy.Worker.MakeLords(parms, pawns)` (make the lords in the same call as the spawn, or
the pawns stand idle); discard with `Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard)`.

Demand what is scarce here (water, fuel, a spare part — never one whose loss blocks launch; a
crew member only when the beat means it). If the threat belongs to a quest (`parms.questTag`,
`inSignalEnd`), every branch must still emit the signal the quest waits for, or it hangs.

## 3. "It comes back later"

`Find.Storyteller.incidentQueue.Add(def, Find.TickManager.TicksGame + delay, parms, retryDurationTicks)`.
The queue is Scribed; at fireTick it calls `Storyteller.TryFire(..., queued: true)` — i.e. the
full `CanFireNow` gates still apply unless `parms.forced` — and with a retry window it retries
about every 833 ticks. Removing a map drops its entries. **With retry 0, a failed fire is removed
silently** — always pass a retry window for a beat that must happen, and log when you enqueue.
Whether every `IncidentParms` field (e.g. `attackTargets`) survives the queue's Deep scribe is
UNVERIFIED; check `IncidentParms.ExposeData` before relying on it. MFI's reply caravans and heartbeat
interactions use exactly this, with a 2,500-tick retry.

## 4. Calendar or heartbeat component

```csharp
public class WorldComponent_RM_Calendar : WorldComponent
{
    private int nextTick = -1;                       // Scribed; -1 = not yet scheduled
    public WorldComponent_RM_Calendar(World world) : base(world) { }
    public override void WorldComponentTick()
    {
        int now = Find.TickManager.TicksGame;
        if (nextTick < 0) { nextTick = now + 60000 * 30; return; }
        if (now < nextTick) return;                  // cheap check every tick; or gate on IsHashIntervalTick
        // parms from StorytellerUtility.DefaultParmsNow(def.category, target), then fire THROUGH the
        // storyteller so gates and cooldowns apply:
        // Find.Storyteller.incidentQueue.Add(def, now, parms, 60000);   never def.Worker.TryExecute(parms)
        nextTick = now + 60000 * 60;                 // on failure: now + 60000 (retry tomorrow)
    }
    public override void ExposeData() { Scribe_Values.Look(ref nextTick, "nextTick", -1); }
}
```

Give the incident `baseChance` 0 (or a worker whose `BaseChanceThisGame` is 0, as MFI's expo
does) so the storyteller never rolls it on its own. MFI's goodwill-curved heartbeat is the same
with one Scribed next-tick per faction and the interval read from a curve on `PlayerGoodwill`.

## 5. Boolean-gate postfix

```csharp
[HarmonyPatch(typeof(IncidentWorker_RaidEnemy), nameof(IncidentWorker_RaidEnemy.FactionCanBeGroupSource))]
static class Patch_RM_FactionMemory
{
    static void Postfix(Faction f, ref bool __result)
    {
        if (__result && RM_FactionMemory.Instance?.Blocks(f) == true) __result = false;
    }
}
```

Least invasive way to let world memory remove a faction from raid selection. Remember: it only
affects `IncidentWorker_RaidEnemy`'s source selection (not sieges from quests, not other attack
workers), and nothing at all when the raid comes with a hostile `parms.faction` already set
(VERIFIED, `IncidentWorker_RaidEnemy.TryResolveRaidFaction` returns early). It is consulted in
both the normal and the `desperate` selection pass, so if it blocks every hostile faction the
raid simply fails to find a source (the worker returns false; no raid, nothing queued). Register
factions lazily inside `Blocks`, Scribe the dictionary on the component, feed it from the event
you mean (killed on our map, by us), cap it, and show it.

## 6. Pacing for Randy without a new storyteller

```xml
<Operation Class="PatchOperationAdd">
  <xpath>Defs/StorytellerDef[defName="Randy"]/comps</xpath>
  <value>
    <li Class="StorytellerCompProperties_OnOffCycle">
      <incident>RM_SomethingHappens</incident>
      <minDaysPassed>20</minDaysPassed>
      <onDays>10</onDays>
      <offDays>20</offDays>
      <numIncidentsRange>1</numIncidentsRange>
      <allowedTargetTags><li>Map_PlayerHome</li></allowedTargetTags>
    </li>
  </value>
</Operation>
```

Field names copied from Randy's own OnOffCycle comps (merged def, VERIFIED); write
`<numIncidentsRange>1~1</numIncidentsRange>` to be safe. **Append, never insert**: an OnOffCycle's
phase is seeded by its index in the comp list, and comps are rebuilt from the def on load, so the
patch reaches existing saves and an insert would shift every later cycle. A comp with a fixed
`incident` still calls that incident's `CanFireNow`, so its own gates apply; a comp we add floors
population intent at `minIncChancePopulationIntentFactor` 0.05 unless set. Storyteller
Enhanced's four storytellers show the other shapes: two `RandomMain` comps with different
weights as two moods, `acceptPercentFactorPerThreatPointsCurve` to fade small threats when the
colony is strong, `forceRaidEnemyBeforeDaysPassed` for early real raids. Changing Randy is an
owner decision (the campaign rules vanilla Randy); propose, don't ship.

## 7. Test hooks

- A Mod Settings toggle "skip choice dialogs (testing)" that takes the default branch.
- One `Log.Message` per outcome with the defName, faction and pawn count — the bridge's
  `fire_incident` result alone cannot tell "asked" from "arrived" (Raid Protection Fee, 2026-10-10).
- A dev action or `forced` path that bypasses RNG rolls inside `TryExecuteWorker`.

## 8. What stamps what (VERIFIED, decompiled 1.6)

| call | runs `CanFireNow`? | stamps cooldown + ThreatBig clock? | notes |
|---|---|---|---|
| storyteller comp → `Storyteller.TryFire(fi)` | yes | yes, if `TryExecute` returned true and not `forced` | `StoryState.Notify_IncidentFired` |
| `incidentQueue` entry at its tick | yes (`TryFire(queued: true)`) | same as above | retry 0 ⇒ dropped silently on failure |
| `def.Worker.TryExecute(parms)` called directly | **no** | **no** | bypasses the storyteller entirely |
| any path with `parms.forced` | generic gates skipped; `CanFireNowSub` runs | **no** | the storyteller will not space around it |
| `Storyteller.RecordIncidentFired(def)` | — | no | Anomaly's recent-incident ratio only |
| `TryExecute` with `requireColonistsPresent` and nobody home | — | **yes** (it returned true) | consumed with nothing done |

