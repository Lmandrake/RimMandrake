# Recipes: incident shapes worth copying

Sketches, not compiled code. Every engine name below was read from decompiled 1.6 (RimSage,
2026-10-10) or from a shipping mod's source; nothing else is guaranteed. Before building,
re-read the vanilla method you lean on. Engine facts and their sources:
`design/RimMandrake/event_quest_wisdom.md` §1; per-mod evidence: §2.

## Contents
1. The XML-only incident (gates, shared cooldowns)
2. Choice-before-threat worker (the Tribute Demand shape, fixed)
3. "It comes back later": IncidentQueue
4. Calendar or heartbeat component
5. Boolean-gate postfix (faction memory)
6. Adding pacing to Randy without a new storyteller
7. Test hooks

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
(VERIFIED, IncidentDef.cs ~155-200). Cooldowns are per target (the map's StoryState).

## 2. Choice-before-threat worker

Tribute Demand's shape: generate the pawns, show them, let the player decide, then deliver or
discard. Its flaw (shared with Raid Protection Fee) is returning `true` while the dialog is
still open. Two acceptable fixes:

- **Resolve before unpausing.** A modal `Dialog_NodeTreeWithFactionInfo` pauses play; the
  attackers are delivered or discarded inside the option's `action`. Log the outcome there so
  a harness can see it. The worker's `true` then means "the player was asked", and the test
  toggle (§7) skips the dialog. Remaining risk: whether a save can be taken with the dialog
  open is UNVERIFIED; if it can, the pre-generated pawns (held only by the closure) are lost.
- **Make the pending state durable.** Store faction, points, strategy, arrival mode and the
  demand in a Scribed component entry; the dialog's actions read and clear it; on load, an
  unanswered entry re-opens the dialog (MFI's re-opening ChoiceLetter is the model).

Raid plumbing as Tribute Demand runs it (from its shipped source): resolve faction
(`PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroup`), strategy and arrival mode,
`raidStrategy.Worker.TryGenerateThreats`, `raidArrivalMode.Worker.TryResolveRaidSpawnCenter`,
`IncidentWorker_Raid.AdjustedRaidPoints`, `IncidentParmsUtility.GetDefaultPawnGroupMakerParms`,
`PawnGroupMakerUtility.GeneratePawns`; deliver with `raidArrivalMode.Worker.Arrive(pawns, parms)`
+ `raidStrategy.Worker.MakeLords(parms, pawns)`; discard with
`Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard)`.

Demand what is scarce here (water, fuel, a named ship part, a crew member only when the beat
means it). Disable an option with a reason when the colony cannot pay.

## 3. "It comes back later"

`Find.Storyteller.incidentQueue.Add(def, Find.TickManager.TicksGame + delay, parms, retryDurationTicks)`.
The queue is Scribed; at fireTick it calls `Storyteller.TryFire(..., queued: true)` — i.e. the
full `CanFireNow` gates still apply unless `parms.forced` — and with a retry window it retries
about every 833 ticks. Removing a map drops its entries. MFI's reply caravans and heartbeat
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
        // build parms, then either TryExecute directly or enqueue with a retry window
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

Field names copied from Randy's own OnOffCycle comps (merged def, VERIFIED). Storyteller
Enhanced's four storytellers show the other shapes: two `RandomMain` comps with different
weights as two moods, `acceptPercentFactorPerThreatPointsCurve` to fade small threats when the
colony is strong, `forceRaidEnemyBeforeDaysPassed` for early real raids. Changing Randy is an
owner decision (the campaign rules vanilla Randy); propose, don't ship.

## 7. Test hooks

- A Mod Settings toggle "skip choice dialogs (testing)" that takes the default branch.
- One `Log.Message` per outcome with the defName, faction and pawn count — the bridge's
  `fire_incident` result alone cannot tell "asked" from "arrived" (Raid Protection Fee, 2026-10-10).
- A dev action or `forced` path that bypasses RNG rolls inside `TryExecuteWorker`.
