# BRIDGE_TOOLS_EASY_BLOCK_1 — the 32 still to build

Derived from `design/Jawa/bridge/dll_capability_roster.html` and its `.decisions.json`.
42 of the 74 shipped at `4a8324e1`. These are the rest, already split into three
workloads that do not touch each other's files.

⛔ The companion is ONE `sealed partial class` across many files. Each group creates its
OWN new file, named below, and edits nothing else — that is what lets three run at once.

Build with `python.exe src/RimMandrake/bridgetools/build.py --gm` (Windows python, not
WSL python3). `--gm` is NOT optional: without it the plan drops 10 existing tools.

## Group E — 10 tools -> `JawaBenchPawnKitTools.cs`

- **grant-xp** — Skills, traits, relations & backstory
  - api: `Pawn_SkillTracker.Learn(SkillDef, float, direct, ignoreLearnRate)`
  - effect: Real learn-rate path, or bypass it
- **read-opinion** — Skills, traits, relations & backstory
  - api: `Pawn_RelationsTracker.OpinionOf / OpinionExplanation / CompatibilityWith`
  - effect: The number plus the human-readable breakdown
- **grant-ability** — Abilities, psycasts & inspiration
  - api: `Pawn_AbilityTracker.GainAbility(AbilityDef)`
  - effect: Give any AbilityDef
  - ⚠️ self-notifies
- **start-inspiration** — Abilities, psycasts & inspiration
  - api: `InspirationHandler.TryStartInspiration(InspirationDef, reason, sendLetter)`
  - effect: Force a named inspiration
- **read-psychic-sensitivity** — Abilities, psycasts & inspiration
  - api: `Pawn_PsychicEntropyTracker.PsychicSensitivity`
  - effect: The stat that scales everything above
- **clear-xenogenes** — Genes & xenotypes
  - api: `Pawn_GeneTracker.ClearXenogenes()`
  - effect: Wipe xenogenes, keep endogenes
- **gene-resource-poke** — Genes & xenotypes
  - api: `GeneUtility.OffsetHemogen / SatisfyChemicalGenes`
  - effect: Hemogen and chemical genes
- **lock-apparel** — Apparel, equipment & inventory
  - api: `Pawn_ApparelTracker.Lock(Apparel) / LockAll()`
  - effect: Pawn cannot remove it, the ideo/royalty way
- **inventory add/remove** — Apparel, equipment & inventory
  - api: `Pawn_InventoryTracker.TryAddAndUnforbid / RemoveCount(ThingDef, int, destroy)`
  - effect: Stuff the pack or take things out
  - ⚠️ ⚠️ TryAddOrTransfer returns a COUNT, not a bool
- **split-stack** — Apparel, equipment & inventory
  - api: `Thing.SplitOff(int) + GenPlace.TryPlaceThing`
  - effect: Peel N off a stack and place it

## Group F — 11 tools -> `JawaBenchGroupTools.cs`

- **attach / detach pawn** — Lords, raids & AI groups
  - api: `Lord.AddPawn(Pawn) / RemovePawn`
  - effect: Move a pawn in or out of a lord
  - ⚠️ gate on Lord.CanAddPawn(p)
- **poke-lord** — Lords, raids & AI groups
  - api: `Lord.ReceiveMemo(string) / Find.SignalManager.SendSignal(new Signal(tag))`
  - effect: Advance the state machine the way vanilla scripts do
- **raid-shape flags** — Lords, raids & AI groups
  - api: `IncidentParms.raidNeverFleeIndividual / .raidForceOneDowned / .pawnGroupMakerSeed`
  - effect: Never-flee, force-one-downed, biocoding, seed
- **pre-flight the refusal** — Factions & relations
  - api: `Faction.CanChangeGoodwillFor(Faction, int)`
  - effect: So a caller reports it instead of silently no-oping
- **hidden / defeated / temporary flags** — Factions & relations
  - api: `Faction.hidden / .defeated / .temporary`
  - effect: Take a faction off the board without deleting it
- **found-player-colony** — Settlements, caravans & gravship
  - api: `SettleUtility.AddNewHome(PlanetTile, Faction)`
  - effect: Put a player settlement on a tile
  - ⚠️ does not generate a map
- **make & move a caravan** — Settlements, caravans & gravship
  - api: `CaravanMaker.MakeCaravan(...) + Caravan_PathFollower.StartPath(...)`
  - effect: Create one and send it somewhere
  - ⚠️ the whole caravan domain is absent today
- **attack a settlement** — Settlements, caravans & gravship
  - api: `SettlementUtility.Attack(Caravan, Settlement)`
  - effect: Send a caravan in
  - ⚠️ applies the goodwill hit itself
- **set a faction's primary ideo** — Ideology, precepts & rituals
  - api: `faction.ideos.SetPrimary(Ideo)`
  - effect: What the faction believes
- **assign an ideo role** — Ideology, precepts & rituals
  - api: `Precept_Role.Assign(Pawn, addThoughts) / Unassign`
  - effect: Make someone the Moral Guide
- **development points** — Ideology, precepts & rituals
  - api: `IdeoDevelopmentTracker.TryAddDevelopmentPoints(int) / Notify_Reformed()`
  - effect: Drive an ideo toward reform

## Group G — 11 tools -> `JawaBenchSystemTools.cs`

- **minify** — Map things & buildings
  - api: `MinifyUtility.MakeMinified(Thing, DestroyMode) / Uninstall`
  - effect: Installed building becomes a carryable
- **collapse-roof** — Terrain, roof & grids
  - api: `RoofCollapserImmediate.DropRoofInCells(cells, map, out crushed)`
  - effect: Drop it and crush whatever is underneath
- **snow / sand depth** — Terrain, roof & grids
  - api: `SnowGrid.SetDepth(cell, float) / SandGrid.SetDepth`
  - effect: Per-cell depth
  - ⚠️ sand is Odyssey
- **read monolith state** — Anomaly & entities (DLC)
  - api: `GameComponent_Anomaly.LevelDef / .NextLevelDef / .HighestLevelReached / .AmbientHorrorMode`
  - effect: Where the run is in the Anomaly arc
- **discover a codex entry** — Anomaly & entities (DLC)
  - api: `EntityCodex.SetDiscovered(EntityCodexEntryDef, ThingDef, Thing)`
  - effect: Mark an entity known
- **ModsConfig.AnomalyActive guard** — Anomaly & entities (DLC)
  - api: `ModsConfig.AnomalyActive`
  - effect: Every row above needs it
  - ⚠️ ⚠️ without the guard these no-op or throw
- **autosave now** — Save/load & scribe
  - api: `Find.Autosaver.DoAutosave()`
  - effect: Trigger the autosaver
- **mod-list match check** — Save/load & scribe
  - api: `ScribeMetaHeaderUtility.LoadedModsMatchesActiveMods(out string, out string)`
  - effect: Does this save match the running mods
- **mod inventory** — Diagnostics, logging & defs
  - api: `LoadedModManager.RunningModsListForReading`
  - effect: Which mods are running, with packageIds and assemblies
- **stat cache bust** — Diagnostics, logging & defs
  - api: `StatWorker.ClearCacheForThing(Thing) / DeleteStatCache()`
  - effect: Required after quality or stuff edits
- **prefs** — Diagnostics, logging & defs
  - api: `Prefs.DevMode ... then Prefs.Save()`
  - effect: Dev mode, verbose logging, autosave interval, pause-on-load
  - ⚠️ ⚠️ Prefs.xml is rewritten from memory on exit
