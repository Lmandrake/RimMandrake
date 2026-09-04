# Anomaly exception access — the Memory-Core revelation (buildable spec)

Item: `infrastructure/state/items/ANOMALY_EXCEPTION_ACCESS_1.md`. Ruled by the
owner 2026-09-03: *"Yes the memory core event."* Options (a) class-item grant and
(c) no access are dead. Gameplay being granted: `research_review/recovery_drafts.md`
§1 (The Pit — a captured beast yields beast-metal and 2,000 W; containment
strength is the tension). Taxonomy rule 5 binds: a cut removes a
`ResearchProjectDef` and nothing else.

Every claim below is **VERIFIED** (read in the decompiled 1.6 source or the merged
def via RimSage, 2026-09-03) unless marked **HYPOTHESIS**.

---

## 1. The mechanism — how a building becomes buildable with no research row

### What actually gates a building (VERIFIED, `Designator_Build.Visible`, `Source/RimWorld/Designator_Build.cs` L108–170)

The architect menu shows a `Designator_Build` only if ALL of these pass, in order:

1. faction tech level within `minTechLevelToBuild`/`maxTechLevelToBuild`
2. **`entDef.IsResearchFinished`** — every `researchPrerequisites[i].IsFinished`
   (`BuildableDef.cs` L172)
3. Anomaly monolith: `minMonolithLevel > HighestLevelReached` **only when
   `Find.Anomaly.GenerateMonolith`** — the campaign playstyle is `AmbientHorror`
   (`SCENARIO_SETTINGS_SPEC.md` R-S4 / B2), whose def has
   `generateMonolith false` (VERIFIED, `AnomalyPlaystyleDef AmbientHorror`), so
   this gate is **skipped** for us. Same guard on the Anomaly architect category
   (`DesignationCategoryDef.cs` L245) and on entity capture
   (`CompHoldingPlatformTarget.CanBeCaptured` L158).
4. `difficulty.AllowedToBuild`
5. every `PlaceWorker.IsBuildDesignatorVisible(def)`
6. `buildingPrerequisites` (colonists own building X)
7. **`discoveryPrerequisites`** — `List<ThingDef>` on `BuildableDef` (L56); the
   designator is hidden while `Find.HiddenItemsManager.Hidden(thingDef)` is true
   for any listed def.
8. Odyssey `requireInspectedGravEngine`

`HiddenItemsManager` (VERIFIED, whole class, 65 lines): a saved
`Dictionary<ThingDef,bool>` seeded from every `ThingDef` with
`hiddenWhileUndiscovered = true`; `SetDiscovered(def)` flips the entry to false and
`ExposeData` persists it across save/load. Nothing else in the engine reads
`discoveryPrerequisites` (searched: only `Designator_Build.cs`). This is a vanilla
1.6 "buildable once discovered" gate that is **independent of the research
tree**, saved, and flipped by one call.

### Recommendation — REVEAL GATE via `discoveryPrerequisites` + one GameComponent

**Size: XML + small C#** (one ThingDef, one patch file, one GameComponent of ~80
lines, one Keyed strings file; no Harmony, no ResearchProjectDef, no quest).

1. **Gate def** — a never-spawned item `RUT_ShipMemory_Containment` with
   `hiddenWhileUndiscovered = true`. It exists only to be a key in
   `HiddenItemsManager`. It is never traded, never spawned, never in a category.
2. **Patch** the seven Anomaly buildables (§2): remove `researchPrerequisites`
   entirely and add `<discoveryPrerequisites><li>RUT_ShipMemory_Containment</li></discoveryPrerequisites>`.
   Before the reveal: gate 7 hides them. After: nothing hides them.
3. **Reveal** — `Find.HiddenItemsManager.SetDiscovered(RUT_ShipMemory_Containment)`
   plus the letter. Called by a `GameComponent` when the trigger (§3) is met.
   The saved dictionary makes it one-shot for free; no extra ExposeData.

Why this and not the alternatives:

| route | verdict | why |
|---|---|---|
| **Hidden `ResearchProjectDef` that only code finishes** (`ResearchManager.FinishProject`) | rejected | `FinishProject` is public and works (VERIFIED, L403–507; sets `progress[proj]=baseCost`, fires `Notify_UnlockedByResearch` and the `ResearchCompleted` signal). But the project **cannot be hidden**: `MainTabWindow_Research.PostOpen` adds EVERY `ResearchTabDef` to the tab bar unconditionally (L738); `visibleByDefault`/`TabInfoVisible` only gate the tab's description panel (L788); a project is skipped from drawing only when `IsHidden`, which is `EntityCodex.Hidden(def)` — true only for projects listed in an `EntityCodexEntryDef.discoveredResearchProjects` of an undiscovered entity (VERIFIED, `EntityCodex.cs` L61–80). `hideWhen` is a `DifficultyConditionConfig` (five difficulty booleans) — not ours to set. So the node would sit visibly in a tab as a locked row: **that is a research row reintroduced** (criterion 2), and with Nice Research Tab + Research Reinvented active (live `ModsConfig.xml`) the tree UI is not even vanilla's. Also `IsFinished` is `ProgressReal >= Cost`, so `baseCost 0` would mean finished at tick zero (`Cost` falls back to `knowledgeCost`). Too many ways to be wrong. |
| **Fake `EntityCodexEntryDef` to hide that project** | rejected | pollutes the entity codex (which `AmbientHorror` always shows — `alwaysShowCodex true`) with a "???" entry, and after the reveal the project still needs to be un-startable (`requiredResearchBuilding` on a ghost bench). Two hacks to buy what `discoveryPrerequisites` gives for one field. |
| **Patch `researchPrerequisites` off, no gate** | rejected | the six buildings appear in the architect menu on day one. That is option (a) without even the class item — dead by ruling, and no revelation moment. |
| **Custom `PlaceWorker.IsBuildDesignatorVisible`** (pattern: `PlaceWorker_RequireNaturePsycaster`) | viable fallback | same visibility effect, but needs a `WorldComponent` to persist the flag and a C# class on seven defs. Strictly more code than the `discoveryPrerequisites` route for the same result. Use only if FOUNDRY finds Research Reinvented bypassing gate 7 (§6 risk 2). |
| **Quest/incident that hands over minified buildings** | rejected | a minified `HoldingPlatform` can be reinstalled without research (Designator_Install does not check it), but it is a one-off object, not access; the harvesters need bioferrite the player cannot obtain without access anyway. |
| **Do nothing after the cut** | rejected | Cherry Picker's treatment of a cut `ResearchProjectDef` is **UNKNOWN** (DLL only, no source in workshop folder 3521312241). Either it strips the prerequisite (buildings free on day one) or leaves the reference dangling (`IsFinished` false forever, buildings unreachable). Our patch removes `researchPrerequisites` ourselves so the outcome does not depend on CP. |

🔑 **Why the removal patch is mandatory even with the gate:** `IsResearchFinished`
is checked BEFORE `discoveryPrerequisites`. If the cut rows stay referenced, the
buildings never appear no matter what we reveal. Removing the reference is what
makes the reveal the only gate. This does not reintroduce a row and cuts no
content — it edits a field on seven defs that stay in the game.

⚠️ **Ordering vs the cut (item criterion 1):** this mod must be deployed and
verified BEFORE the 42 rows are Cherry-Picked. After our patch the seven defs no
longer reference `EntityContainment`/`BioferriteHarvesting`/`Electroharvester`/
`BioferriteGenerator`/`BioferriteShaping`, so the cut then removes rows that
nothing depends on.

---

## 2. What the event grants — one package, one reveal

All seven point at the same gate def; one call reveals all. No staging: the loop
is one economy (`recovery_drafts.md` §1), and staging it would only recreate the
tree we cut.

| defName | type | vanilla `researchPrerequisites` (removed by our patch) | role in The Pit |
|---|---|---|---|
| `HoldingPlatform` | ThingDef | `EntityContainment` | the chains (Steel 40) |
| `ElectricInhibitor` | ThingDef | `EntityContainment` | +10 containment |
| `ShardInhibitor` | ThingDef | `EntityContainment` | +20 containment |
| `BioferriteHarvester` | ThingDef | `BioferriteHarvesting` | sap-tap, −15 containment |
| `Electroharvester` | ThingDef | `Electroharvester` | nerve-tap, 2,000 W, −25 containment |
| `BioferriteGenerator` | ThingDef | `BioferriteGenerator` | burns beast-metal, 4,000 W |
| `BioferritePlate` | TerrainDef | `BioferriteShaping` | floor, +15 containment (Bioferrite 4) |

(All seven VERIFIED via merged defs; `BioferritePlate` is a `TerrainDef` and
`discoveryPrerequisites` lives on `BuildableDef`, so the same field applies.)

**Not gated, needs nothing:** `Bioferrite` (stuff; no `researchPrerequisites`,
`commonality 0`, `allowedInStuffGeneration false` — only harvest yields it) and
`HoldingSpot` (no `researchPrerequisites`; `minMonolithLevel 1` is skipped under
`AmbientHorror`). ⭐ **The holding spot being free from day one is what makes the
trigger in §3 reachable**: the clan can rope a downed beast to the ground before
the ship remembers how to chain it.

**Out of scope, on purpose:** `BioferriteShaper` and its recipes
(`BioferriteIgnition`, cluster 2), the utility structures (cluster 4), the serum
bench (cluster 5). Their rows are cut and their recipes' `researchPrerequisite`
now point at dead rows — those are separate recovery decisions, not this item's.
Also `Apparel_CultistMask`/`NerveSpiker` (`BioferriteExtraction`'s unlocks) —
LOOT-ONLY per the recovery draft, not granted.

Vanilla also gates manual bioferrite EXTRACTION from a held entity (the
`ContainmentMode` "extract" toggle) by nothing but the entity's own
`CompStudiable`; **HYPOTHESIS**: it needs no research row — FOUNDRY confirms on
the quicktest by checking the held entity's ITab_Entity after the reveal.

---

## 3. When and how it fires

**Trigger (primary): the first thing the crew ties down.** The moment any pawn
is held on a player-faction holding platform or holding spot on any player map
(`Building_HoldingPlatform.HeldPawn != null`, VERIFIED L72;
`building.Faction == Faction.OfPlayer`). That is the Utinni recognising the
creature: the short ones dragged something aboard that she has met before.

**Trigger (fallback): beast-metal in the hold.** ≥ 50 `Bioferrite` in player
possession on a player home map (stockpiled or carried). Covers a player who
loots bioferrite from the Assailant complex or a night-side carcass before
ever capturing anything — the material itself is what she remembers.

**Trigger (scripted): the Assailant core.** The GameComponent implements
`ISignalReceiver` (VERIFIED, `SignalManager.RegisterReceiver`, L17) and reveals
on any signal whose tag ends with `RUT_ShipMemory_Containment`. The Assailant
dungeon's QuestScriptDef (`ASSAILANT_DUNGEON_BUILD_1`, thaw-gate = QuestNode +
map-trigger signal, ruled 2026-09-01) sends it from its core band via
`QuestNode_SendSignals` (VERIFIED, class exists) when the ship memory-fragment
loot is taken — canon `assailant_reveal_arc`: *"loot recovered here triggers ship
memory-surfacings — the dungeon feeds the ship its own past."* This is the
hook that makes the two items fit: the dungeon does not invent a parallel
unlock, it fires the same reveal. ⚠️ Quest signals are prefixed with the quest's
id (`<questId>.RUT_ShipMemory_Containment`) — match by `EndsWith`, never equality.

**Check cadence:** `GameComponentTick` every 600 ticks (10 s at 1×) over
`Find.Maps.Where(m => m.IsPlayerHome)`; the primary check is
`map.listerBuildings.AllBuildingsColonistOfClass<Building_HoldingPlatform>()`,
the fallback is `map.resourceCounter.GetCount(ThingDefOf.Bioferrite) >= 50`.
Cheap, no Harmony, no reliance on the storyteller rolling an incident.

**One-shot:** after `SetDiscovered` the saved `HiddenItemsManager` entry is
false; the component checks `Find.HiddenItemsManager.Hidden(gate)` first and
returns when already revealed. Nothing else to persist. Not repeatable, by
design — a memory surfaces once.

**Never met:** if the player never ties down a beast, never holds 50
bioferrite and never reaches the Assailant core, the seven buildables stay
hidden forever. Nothing is lost: every one of them is useless without a held
entity or bioferrite. There is no timer fallback and there should not be one —
the idiom is revelation, not a calendar.

**Pre-thaw dungeon?** No conflict: the complex is inert until the power core is
delivered; the memory-fragment loot lives in the core band behind the thaw.

---

## 4. What the player sees

One `ChoiceLetter`, `LetterDefOf.PositiveEvent`, via
`LetterMaker.MakeLetter(label, text, def, lookTargets, hyperlinkThingDefs: …)`
(VERIFIED signature, `LetterMaker.cs` L32). `lookTargets` = the platform (or the
bioferrite stack) that fired it; `hyperlinkThingDefs` = the six ThingDefs so the
letter itself teaches the package. Narrator register (canon `narrator_voice`:
the ship-mind's remnant, within and beyond the world, humour, "the short ones";
"Kolyska" allowed in this register).

**Label:** `She remembers the chains`

**Text (primary/fallback triggers):**

> The surprisingly hairy creatures have tied something to the deck that will
> not stop moving. It is not the first time. When this hull was called Kolyska
> the old masters kept such things below, chained at four corners on plates of
> their own grown metal, and drew from them what they needed — the fibre and
> the current.
>
> The Utinni has remembered how. Holding platforms, inhibitors, the harvesters
> and the bioferrite generator can now be built. The beast-metal you take from
> it burns, and the plate you lay from it holds. Chain it well: the more you
> draw, the harder it pulls.

**Text (Assailant-core signal), swap the first paragraph:**

> Something the short ones carried out of the frozen place has woken a room
> the Utinni had sealed off from herself. When this hull was called Kolyska
> the old masters kept the flesh below, chained at four corners on plates of
> their own grown metal, and drew from it what they needed — the fibre and
> the current.

Keyed strings, `Languages/English/Keyed/RUT_ShipMemory.xml`:
`RUT_ShipMemory_Containment_Label`, `RUT_ShipMemory_Containment_Text`,
`RUT_ShipMemory_Containment_Text_Assailant`.

---

## 5. Naming and layout (`design/NAMING_SCHEME_PLAN.md`, RimUtinni tier)

| thing | name |
|---|---|
| mod folder | `src/RimUtinni/ShipMemory/` (no collision: `grep -ril shipmemory src design` is empty) |
| packageId | `mandrake.rut.shipmemory` |
| C# namespace | `RimMandrake.Utinni.ShipMemory` |
| assembly | `RimMandrake.Utinni.ShipMemory.dll` — csproj mirrors `src/RimUtinni/EmpirePursuit/Source/EmpirePursuit.csproj` (net472, `OutputPath ..\Assemblies\`) |
| gate ThingDef | `RUT_ShipMemory_Containment` |
| GameComponent | `GameComponent_ShipMemory` (one component; later Memory-Core reveals add cases to it, never a second component) |
| letter keys | `RUT_ShipMemory_Containment_*` |
| signal tag | `RUT_ShipMemory_Containment` |
| patch file | `Patches/RUT_ShipMemory_ContainmentGate.xml` |

`About.xml` must declare `Ludeon.RimWorld.Anomaly` in `loadAfter` and the patch
must be wrapped in `PatchOperationFindMod` / `MayRequire="Ludeon.RimWorld.Anomaly"`
— remember a `PatchOperationFindMod` that finds nothing succeeds silently.
Run `python3 src/RimMandrake/Utils/naming_lint.py` before commit.

**Gate ThingDef** (`Defs/ThingDefs_Items/RUT_ShipMemory.xml`), minimal on
purpose — it must never be a real object:

```xml
<ThingDef>
  <defName>RUT_ShipMemory_Containment</defName>
  <label>memory: the chains below</label>
  <description>What the Utinni remembers of holding living things. Not an object.</description>
  <thingClass>ThingWithComps</thingClass>
  <category>Item</category>
  <hiddenWhileUndiscovered>true</hiddenWhileUndiscovered>
  <tradeability>None</tradeability>
  <destroyOnDrop>true</destroyOnDrop>
  <selectable>false</selectable>
  <graphicData>
    <texPath>Things/Item/Special/AIPersonaCore</texPath>
    <graphicClass>Graphic_Single</graphicClass>
  </graphicData>
  <statBases><MarketValue>0</MarketValue><Mass>0.01</Mass></statBases>
</ThingDef>
```

No `thingCategories` (so it never enters a stockpile filter tree even after
discovery — `Listing_TreeThingFilter` lists by category), no `tradeTags`, no
`thingSetMakerTags`. HYPOTHESIS: an item ThingDef with no `thingCategories`
raises no `ConfigErrors` — FOUNDRY greps the minimal-list log for
`Config error in RUT_ShipMemory_Containment` (the validate_patch.py blind spot).

**Patch** — per defName, two ops. Example for one:

```xml
<Operation Class="PatchOperationRemove">
  <xpath>Defs/ThingDef[defName="HoldingPlatform"]/researchPrerequisites</xpath>
</Operation>
<Operation Class="PatchOperationAdd">
  <xpath>Defs/ThingDef[defName="HoldingPlatform"]</xpath>
  <value><discoveryPrerequisites><li>RUT_ShipMemory_Containment</li></discoveryPrerequisites></value>
</Operation>
```

Repeat for the five other ThingDefs and `Defs/TerrainDef[defName="BioferritePlate"]`.
Validate with `validate_patch.py --defs … --live …` — a wrong xpath matches
nothing and logs nothing.

**GameComponent** (sketch — FOUNDRY writes it):

```csharp
namespace RimMandrake.Utinni.ShipMemory {
  public class GameComponent_ShipMemory : GameComponent, ISignalReceiver {
    const int Interval = 600; const int BioferriteThreshold = 50;
    static ThingDef Gate => DefDatabase<ThingDef>.GetNamed("RUT_ShipMemory_Containment");
    public GameComponent_ShipMemory(Game game) {}
    public override void FinalizeInit() { Find.SignalManager.RegisterReceiver(this); }   // receivers are not saved; re-register every load
    public override void GameComponentTick() {
      if (Find.TickManager.TicksGame % Interval != 0 || !Find.HiddenItemsManager.Hidden(Gate)) return;
      foreach (var map in Find.Maps) { if (!map.IsPlayerHome) continue;
        var plat = map.listerBuildings.AllBuildingsColonistOfClass<Building_HoldingPlatform>().FirstOrDefault(b => b.HeldPawn != null);
        if (plat != null) { Reveal(plat, false); return; }
        if (map.resourceCounter.GetCount(ThingDefOf.Bioferrite) >= BioferriteThreshold) { Reveal(null, false); return; } }
    }
    public void Notify_SignalReceived(Signal s) { if (s.tag.EndsWith("RUT_ShipMemory_Containment") && Find.HiddenItemsManager.Hidden(Gate)) Reveal(null, true); }
    void Reveal(Thing target, bool assailant) {
      Find.HiddenItemsManager.SetDiscovered(Gate);
      var letter = LetterMaker.MakeLetter("RUT_ShipMemory_Containment_Label".Translate(),
        (assailant ? "RUT_ShipMemory_Containment_Text_Assailant" : "RUT_ShipMemory_Containment_Text").Translate(),
        LetterDefOf.PositiveEvent, target != null ? new LookTargets(target) : null, hyperlinkThingDefs: SixBuildings);
      Find.LetterStack.ReceiveLetter(letter);
    }
  }
}
```

`Find.SignalManager` is per-game; `RegisterReceiver` errors on a duplicate, so
register only in `FinalizeInit` (runs once per load) — not in the constructor
and not in `LoadedGame` as well. Deregister is unnecessary (the manager dies
with the game). `ThingDefOf.Bioferrite` exists under Anomaly (VERIFIED,
`ThingDefGenerator`/`ResearchManager` use it); guard the whole tick on
`ModsConfig.AnomalyActive`.

---

## 6. Verification — what FOUNDRY runs

Honour the item's criteria: zero Anomaly research, no row reintroduced, no
Anomaly content cut. Minimal-list restart proves XML (owner ruling 2026-09-03);
the full list is needed once for risk 2.

**A. Load proof (minimal list, 22 s).** Player.log has no `Config error in
RUT_ShipMemory_Containment`, no patch-failure line naming
`RUT_ShipMemory_ContainmentGate.xml`, and the DLL loads (`Loaded assembly
RimMandrake.Utinni.ShipMemory` or the equivalent Harmony-free load line).

**B. Hidden before (quicktest, `rimworld/start_debug_game_ready`).** With no
research done: `jawa/research_availability` shows no `RUT_` project (there is
none — that is the point); the Anomaly architect category lists `HoldingSpot`
but NOT the seven; `rimworld/execute_debug_action` cannot find `HoldingPlatform`
under the build menu without god mode. Dump a def read of `HoldingPlatform`
and confirm `researchPrerequisites` is empty and `discoveryPrerequisites` names
the gate (`jawa/export_things` or the refreshed def dump — the dump keeps
`researchPrerequisites`, so the patch is visible there).

**C. Fallback route (cheapest end-to-end).** `rimworld/spawn_thing`
`Bioferrite` ×60 inside the home area; advance ≤ 600 ticks. Expect: the letter
`She remembers the chains` in `jawa/letter_list`; the seven now visible in the
architect menu; `jawa/build_check` accepts a `HoldingPlatform` placement.

**D. Primary route.** Fresh quicktest (a reveal is one-shot per save).
`jawa/spawn_pawn` an entity kind with `CompHoldingPlatformTarget` (e.g.
`Fingerspike` or whatever night-side kind the campaign fields), faction
`hostile`; down it (`jawa/pawn_force_incapacitate`); place a `HoldingSpot` and
have a colonist capture it (float-menu "Capture" — via
`rimworld/execute_debug_action` if a debug capture exists, else by hand on the
quicktest). Within 600 ticks: the letter and the architect entries as in C.
🔴 The capture path is what a real player walks; C alone is not a pass.

**E. Persistence.** Save after C or D, reload: the seven remain visible, no
second letter arrives, `GameComponentTick` does not re-reveal (the
`HiddenItemsManager` entry survived the save — VERIFIED it is scribed, but
prove it).

**F. Signal route.** From the quicktest console:
`Find.SignalManager.SendSignal(new Signal("TEST.RUT_ShipMemory_Containment", true))`
(via any bridge eval path, or a throwaway JawaBench tool) → the Assailant
variant letter fires. This is the contract the dungeon quest will use.

**G. Criteria audit.** `cherrypicker.py`: none of the seven, nor `Bioferrite`,
nor any `PawnKindDef`, entered the cut list during this work (criterion 3).
`research_tree_taxonomy.md` §1 row `(Anomaly)` and rule 6 state this route
(criterion 4 — BENCH edits, FOUNDRY does not).

**H. Full-list load, once.** With Research Reinvented active, repeat B: the
seven must NOT appear pre-reveal (risk 2).

---

## 7. Risks — silent failures FOUNDRY should expect

1. **Patch silently matches nothing.** `PatchOperationFindMod`/`MayRequire`
   both succeed on no-match; a typo in `TerrainDef[defName="BioferritePlate"]`
   leaves the vanilla `researchPrerequisites` in place → after the cut that
   buildable is unreachable forever, and the log says nothing. Check B reads the
   patched def back.
2. **Research Reinvented "prototypes"** (HYPOTHESIS — DLL only, no source
   shipped). RR lets colonists build prototype versions of things whose research
   is not done; if it patches `Designator_Build.Visible` with a prefix that
   returns true for prototypable defs, gate 7 is bypassed and the seven show on
   day one. With `researchPrerequisites` removed they are not "unresearched",
   so RR should have no opinion — but verify (check H). If it bypasses, switch to
   the PlaceWorker fallback (§1 table), which RR cannot reason about.
3. **Cherry Picker's research cut leaves a dangling reference** (UNKNOWN
   behaviour). Irrelevant once our patch has removed the field — but only if our
   patch is DEPLOYED before the cut lands, and CP runs after XML patching. If
   FOUNDRY deploys after the cut, check B's def read is the tell.
4. **`ThingDefOf.Bioferrite` / `HeldPawn` on a modded platform.** A mod
   subclassing `Building_HoldingPlatform` still matches
   `AllBuildingsColonistOfClass<>`; a mod replacing the class does not. Only
   vanilla platforms are in the campaign today.
5. **Duplicate receiver error.** Registering in both constructor and
   `FinalizeInit` logs `Tried to register the same receiver twice` on every load.
6. **The letter fires on a non-home map** (a caravan camp with a spot). The
   check is restricted to `IsPlayerHome`; a player who captures on a temporary
   map gets the reveal when the beast comes home. Acceptable; note it in the
   item if a tester trips on it.
7. **God mode hides the gate.** `Designator_Build.Visible` returns true first
   thing under `DebugSettings.godMode` — every "it shows!" from a god-mode
   quicktest is void. Turn it off for B–D.
8. **Study is still monolith-gated.** `CompStudiable` L183 blocks study when
   `HighestLevelReached < minMonolithLevelForStudy` WITHOUT the
   `GenerateMonolith` guard. Not this item's problem (knowledge rows are cut
   anyway), but a tester who expects "study" on the held beast will report a
   bug that is not one.

---

## 8. Unknowns

- Cherry Picker's exact handling of a cut `ResearchProjectDef` (strip vs
  dangle). Designed around; not resolved.
- Whether Research Reinvented's prototype patch touches `discoveryPrerequisites`
  (risk 2) — settled by check H, not by reading.
- Whether manual bioferrite extraction on a held entity needs any cut row (§2,
  HYPOTHESIS) — settled by looking at the ITab after check D.
- The night-side entity `PawnKindDef` FOUNDRY should spawn for check D — take it
  from `assailant_flesh_sheet.decisions.json` / the sea-beast roster, not from
  this spec.
