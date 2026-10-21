# Unwanted and lingering factions: how a faction hangs around, and how we stop it (2026-10-20)

FOUNDRY, offline, while the owner was away. Every engine claim below was read from the RimWorld 1.6 source
(RimSage, `Source/RimWorld/...`) on 2026-10-20; every def value from the def dump capture `2026-10-20T08-31-20Z`
(the 374-mod list, before Wave 4); every save value from the four `ASHKARR_DEV_*_2026-10-20.rws` saves, read only.

> Owner, 2026-10-20: *"I notice in factions there are Tallmere Combs and Sacrileg Hunters however. We don't want
> those... same with the Space Exchange."*
>
> Owner, 2026-10-20 (AFK brief): *"give Opus a chance to think deeply about the factions. I seem to remember having a
> faction hang around was problematic for raiding and such (might still appear in lists or even in game). Make sure
> we can stop that."*

## 1. The answer in short

- **Why a faction "hangs around".** The game removes only *temporary* factions (`FactionManager.Remove` logs an error
  for any other). A permanent faction leaves the game only by being *defeated*, and `defeated` is set in one place:
  `SettlementDefeatUtility.CheckDefeated`, when the player destroys its **last settlement**. **A faction with no
  settlement can therefore never be defeated.** It stays in the Factions tab for ever, and nothing about having no
  settlements stops it acting: `IncidentWorker_PawnsArrive.MustHaveSettlementOnLayer` is `false` for every vanilla
  worker, so raids, trader caravans, visitors and travelers all still pick it. If it ever turns hostile, it raids
  for ever and the player has nothing to attack.
- **That is exactly Tallmere Combs today.** `RM_Faction_CombHolds` is in all four dev saves with **0 settlements and
  no leader**, neutral, with 7 caravan trader kinds and a Combat group. Its kinds carry no `factionLeader` and the
  def no `fixedLeaderKinds`, so it can never get a leader, and vanilla `Faction.FactionTick` raises
  `Log.ErrorOnce("Faction leader for Tallmere Combs is null.")` on every tick (the 2026-10-14 "six empty thrones"
  cost was 360 suppressed repeats per second from six such factions).
- **The Space Exchange cannot be removed at all.** `BackCompatibility.FactionManagerPostLoadInit` creates a
  `TradersGuild` (and a `Salvagers`) faction on **every load** with Odyssey active when none exists, ignoring every
  def field. The Wave 4 register blamed `requiredCountAtGameStart`, which a page-made world never reads; that line is
  corrected. The three dev saves that lack it will gain it on their next load (source; UNMEASURED live). Odyssey also
  makes it the owner of Core's four orbital traders, so every bulk-goods ship announces itself "from the Space
  Exchange".
- **The recommendation is to banish, not delete.** A banished faction stays loadable, so saves never break, but it is
  hidden, its raids are forbidden, it is off the Configure Factions page and never generated, and, on a save, it is
  flagged defeated with its world objects removed. The def side is implemented. The save side waits for the bridge.
  Deleting our own def waits until the world is re-made.
- **The general guard** is a registry of banned factions, kept as data, plus a checker with three modes: the repo,
  a save, and the running game's def dump. A selftest proves the checker can fail.

## 2. What the history holds

No incident in the repo matches "a defeated or unwanted faction kept raiding". Searched: lessons, items and
`items/closed/`, skills, `design/`, `infrastructure/state/facts/`, auto-memory and the conversation logs. The owner's
memory most likely joins three recorded things with the mechanism in §1:

1. **Deleting a faction from a save is a measured failure** (2026-08-16,
   `skills/rimworld-world-editing/references/savegame-editing.md`).
   - **What was done:** 36 factions were removed offline, down to one residual reference.
   - **What broke:** the save loaded with `Could not do PostLoadInit on RimWorld.FactionManager: NullReferenceException`,
     plus dangling references in mods' own faction-keyed dictionaries (VTE `banksByFaction`, a raid-cooldown mod).
     `load_game_ready` reported success all the same.
   - **The rule it left:** "A faction is removed at the Configure Factions page during worldgen, or not at all."
2. **Unwanted factions leaking onto the faction list.**
   - **`maxConfigurableAtWorldCreation` vs the count.** The zeroed `maxConfigurableAtWorldCreation` changed nothing,
     and `startingCountAtWorldCreation` is the field that decides
     (`src/RimUtinni/UtinniPatches/Patches/FactionSlate/OnlyOurFactions.xml` header, 2026-08-21).
   - **Load order (`JAWA_FACTION_SLATE_LOAD_ORDER_1`):** half the slate's targets loaded after it.
   - **Name leaks:** the `Pirate`/`Empire` name leaks (`items/closed/BLACKSTAR_NAME_MUST_NOT_LEAK_1.md`,
     `items/closed/GALACTIC_EMPIRE_NAME_COLLIDES_1.md`).
3. **Raid-faction picking surprises.**
   - **`SIX_FACTIONS_NEVER_RAID_1`:** `Leo.RaidProtectionFee` swallowed raids per `loadID`.
   - **`FIRE_RAID_ECHOES_REQUESTED_FACTION_1`:** a neutral target faction was silently swapped for Blackstar.
   - **`EMPIRE_RAID_NEVER_GENERATES_1`.**

Two more live routes by which a faction comes back. Both are measured here:

- **VEF faction discovery.** On every load, VEF (`VEF.Factions`, `GameComponentUtility_LoadedGame`, source read
  from GitHub `Vanilla-Expanded/VanillaExpandedFramework`) offers to add every non-player FactionDef that is absent
  from the world. It skips a def only when (a) the def is hidden and its `requiredCountAtGameStart` is 0, or (b) the
  def is in the world's `NewFactionSpawningState.ignoredFactions`.
  - **Clicking "add"** puts the faction in for good, with settlements.
  - **The dev saves:** each ignores 60 defs. On the live 324-mod list VEF would still offer 3:
    `GR_RoamingMonstrosities`, `VFEP_Junkers` and `VFEP_Mercenaries`. The conversation log of 2026-10-20 records 7
    pop-ups on the 374 list.
  - **No dead ignore entries:** none of the 60 ignored entries names a def missing from the 324 list.
- **`jawa/faction_create`.** Our own bridge tool, which is the route that added `RUT_GreentideAntFaction` on
  2026-10-20.

## 3. The levers, verified against 1.6 source

| lever | where it lives | what it stops | what it does NOT stop |
|---|---|---|---|
| `Faction.defeated` | per faction, in the save (`Scribe "defeated"`) | `IncidentWorker_PawnsArrive.FactionCanBeGroupSource` (every raid, caravan, visitor and traveler); `FactionManager.GetFactions` (QuestNode_GetFaction and the Random*Faction pickers); goodwill change (`CanChangeGoodwillFor`) | still listed in the Factions tab (sorted last, marked defeated); quest roots that walk `AllFactionsVisible` with no defeated test (e.g. `QuestNode_Root_Gravcore_AbandonedSettlement`, `_Mission_AncientComplex`, `_ShuttleCrash_Rescue`); orbital traders |
| `Faction.Hidden` = `hidden ?? def.hidden` | nullable per faction in the save, else the def | Factions tab and comms console (`AllFactionsVisible`); neutral arrivals (`IncidentWorker_NeutralGroup`: traders, visitors, travelers); `QuestNode_GetFaction` unless allow-listed; worldgen and new-faction settlements (`FactionGenerator`); `ShouldHaveLeader` (the null-leader ErrorOnce); `HasGoodwill`, so goodwill can never turn it hostile | **enemy raids**: `IncidentWorker_RaidEnemy.TryResolveRaidFaction` passes `allowHidden: true` (that is how Mechanoid and Insect raid); orbital traders |
| `FactionDef.raidsForbidden` | def | `PawnGroupMakerUtility.UsableFactions`, the enemy-raid pool | nothing else |
| `FactionDef.canGenerateQuestSites` | def | the only gate in `QuestNode_Root_DistressCall` and `_WorkSite`, which walk `AllFactionsListForReading` | — |
| `startingCountAtWorldCreation` 0 | def | not on the default Configure Factions list | the row is still on the page |
| `maxConfigurableAtWorldCreation` 0 | def | the row is deleted from the page (`FactionGenerator.ConfigurableFactions`) | right for a banned def; wrong for a wanted one (the OnlyOurFactions incident) |
| `requiredCountAtGameStart` 0 | def | the no-page worldgen path only; VEF skips a hidden def with 0 | a page-made world, and Odyssey's PostLoadInit |
| `TraderKindDef.faction` | def | `IncidentWorker_OrbitalTraderArrival.GetFaction` takes ANY instance of that def, hidden or defeated, and the arrival letter names it | — |
| `Faction.temporary` + engine removal | per faction | `FactionManager.Remove`: relations, pawns, letters, play log, quests, ideos, tales all cleaned | runs only when `FactionCanBeRemoved` (no live pawn or world object of it); mods' own faction dictionaries are not notified; `TradersGuild` is re-created on the next load |
| delete the FactionDef | mod | everything, in a fresh world | an existing save: `FactionManager.ExposeData` drops the def-less faction with "Some factions were null after loading" and every other faction keeps a relation pointing at it |

**So "banished" means:** at the def, `hidden` + `raidsForbidden` + `canGenerateQuestSites false` + off the page + never
generated. In a save, also `defeated` (belt and braces for the `AllFactionsVisible` quest roots and for a stored
`hidden=false`) and no world objects. Hidden plus raidsForbidden already closes the Factions tab, comms, every arrival
and every raid on the next load with no save edit, because the dev saves store no `hidden` value (the def decides).

## 4. Inventory

**Legend.**
- `flags`: H = hidden, PE = permanentEnemy, NE = naturalEnemy.
- `start/maxCfg/required`: startingCountAtWorldCreation / maxConfigurableAtWorldCreation / requiredCountAtGameStart.
- `can (by def)`:
  - raid = a Combat group and not raidsForbidden;
  - caravan = caravanTraderKinds;
  - visit = a Peaceful or Trader group;
  - questsites = canGenerateQuestSites.
- Save columns are from `ASHKARR_DEV_START`. SHIP, LANDED and FOUNDERS are identical except that they lack
  `TradersGuild` and `Salvagers` (23 factions).
- Relation "Neutral" is the Scribe default (`FactionRelation.kind` is omitted when Neutral).
- Def values are BEFORE this change (the dump predates it). Rebuild with:
  `python3 src/RimMandrake/Utils/banned_factions.py inventory <capture> <save>`.

| FactionDef | mod | flags | start/maxCfg/required | can (by def) | DEV_START loadID+name | settlements | leader | to player |
|---|---|---|---|---|---|---|---|---|
| `RUT_Jawa_IndigenousTribes` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 0 'Jawa Trade Moot' | 2 | Y | Neutral |
| `RUT_Jawa_Junkers` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 1 'the Junkers' | 4 | Y | Neutral |
| `RUT_Jawa_HuttCartel` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 2 'Hutt Cartel' | 12 | Y | Neutral |
| `RUT_Jawa_DeepwaterCompact` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | caravan,visit,questsites | 3 'Deepwater Compact' | 6 | Y | Neutral |
| `RUT_Jawa_WildsteamClan` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 4 'Wildsteam Clan' | 9 | Y | Neutral |
| `RUT_Jawa_GeonosianFoundryHive` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,questsites | 5 'Geonosian Foundry Hive' | 5 | Y | Neutral |
| `RUT_Jawa_FreeDroidEnclaves` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 6 'Free Droid Enclaves' | 7 | Y | Neutral |
| `RUT_Jawa_AscendantHelix` | RimUtinni Patches (Jawa campaign) |  | 1/9999/1 | raid,caravan,visit,questsites | 7 'Ascendant Helix' | 7 | Y | Neutral |
| `OutlanderCivil` | Core |  | 1/9999/1 | caravan,visit,questsites | 8 'Homestead Defense League' | 27 | Y | Neutral |
| `RM_Faction_CombHolds` | RimMandrake: Baroque Biomes |  | 1/9999/1 | raid,caravan,visit,questsites | 9 'Tallmere Combs' | 0 | no | Neutral |
| `TribeCivil` | Core |  | 1/9999/1 | raid,caravan,visit,questsites | 10 'Deep Desert Tribes' | 9 | Y | Neutral |
| `Pirate` | Core |  PE | 1/9999/1 | raid,questsites | 11 'Blackstar Company' | 4 | Y | Hostile |
| `Empire` | Royalty |  | 1/1/1 | raid,caravan,visit,questsites | 12 'Galactic Empire' | 3 | Y | Neutral |
| `Mechanoid` | Core | H PE | 1/1/1 | raid,questsites | 13 'Slinox Mechhive' | 0 | no | Hostile |
| `Insect` | Core | H | 1/1/1 | raid,questsites | 14 'Sorne Geneline' | 0 | no | Hostile |
| `Entities` | Anomaly | H | 1/1/1 | questsites | 15 'Dark entities' | 0 | no | Hostile |
| `RM_Thozziks` | RimMandrake: Baroque Biomes | H PE | 1/1/1 | questsites | 16 'Thozziks' | 0 | no | Hostile |
| `RSW_PustuleHornets` | RimMandrake: SW — Bestiary | H PE | 1/1/1 | questsites | 17 'Pustule Hornets' | 0 | no | Hostile |
| `Ancients` | Core | H | 1/1/1 | - | 18 'Ancients' | 0 | no | Neutral |
| `AncientsHostile` | Core | H PE | 1/1/1 | - | 19 'Ancients' | 0 | no | Hostile |
| `HoraxCult` | Anomaly | H PE | 1/1/1 | questsites | 20 'The Servants of Horax' | 0 | no | Hostile |
| `PlayerColony` | Core |  | 1/-1/0 | questsites | 21 'None' | 1 | no | - |
| `RUT_GreentideAntFaction` | RimUtinni: Greentide Raid Ant | H PE | 0/-1/1 | raid,questsites | 22 'They!' | 0 | no | Hostile |
| `TradersGuild` | Odyssey |  | 0/1/1 | raid,visit | 23 'Space Exchange' | 1 | Y | Neutral |
| `Salvagers` | Odyssey | H PE | 0/1/1 | raid,visit | 24 'The Celestial Rogues' | 0 | Y | Hostile |
| `RM_FactionDef_KurrethSwarm` | RimMandrake: Baroque Biomes | H PE | 0/0/0 | raid | absent | | | |
| `RM_FactionDef_SkrethBrood` | RimMandrake: Baroque Biomes | H PE | 0/0/0 | raid | absent | | | |
| `RSW_Shokk_FeraliskBrood` | RimMandrake: SW — Shokk | H PE | 0/0/0 | raid | absent | | | |
| `CASacrilegHunters` | Caravan Adventures |  | 0/-1/1 | raid,caravan,visit,questsites | absent | | | |

total FactionDefs in dump: 70  ours: 15

**What keeps each kind alive.**
- **Ours and the reskinned vanilla, with settlements** (8 `RUT_Jawa_*`, OutlanderCivil, TribeCivil, Pirate, Empire):
  wanted; they can be defeated by taking their last settlement.
- **The hidden system set** (Mechanoid, Insect, Entities, Ancients, AncientsHostile, HoraxCult, RM_Thozziks,
  RSW_PustuleHornets, RUT_GreentideAntFaction, Salvagers):
  - **Why they persist:** they have no settlements by design and so can never be defeated. That is intended, because
    they are the threat sources.
  - **Re-created on load whatever the def says:** HoraxCult and Entities (Anomaly), TradersGuild and Salvagers
    (Odyssey), and Empire (Royalty, only if `world.info.factions` is null).
  - **Salvagers ("The Celestial Rogues")** is Odyssey's hidden permanent enemy. `arrivalLayerWhitelist` is `Orbit`
    only, so it never reaches a surface map. **Banned by the owner's card, 2026-10-20** ("Celestial Rogues is another
    faction you may not want. Ban it too?" -> "Ban Celestial Rogues"); see §5 Celestial Rogues.
- **The two lingering problems**:
  - **Tallmere Combs:** no settlements, no leader, and visible.
  - **The Space Exchange:** visible, with an orbital `SpaceSettlement`, owning the orbital traders.
- **Our own hidden raid factions not in the world** (`RM_FactionDef_KurrethSwarm`, `RM_FactionDef_SkrethBrood`,
  `RSW_Shokk_FeraliskBrood`): `0/0/0`. They are created on demand by their own mods' code, so they are absent from
  every save.
- **Wave 4 ghosts: none.** Every faction def in every dev save is supplied by a mod on the live 324 list (checked
  against `ModsConfig.xml`), and VEF's 60 ignored defs all resolve.

## 5. Per faction: options and the recommendation

### Tallmere Combs — `RM_Faction_CombHolds` (ours, Leaning Scrub inside Baroque Biomes)

| option | cost | what breaks |
|---|---|---|
| A. **Banish at the def now, keep it as a tombstone, delete after the re-make** (RECOMMENDED, done) | none to the saves | nothing: the four saves still load. The faction disappears from the tab, the comms console, arrivals and raids on the next load. Its ideo stays in the save, and the ideo screen lists only visible factions |
| B. Delete the def now | every dev save loses loadID 9 on load with a red "Some factions were null after loading", plus 24 dangling relations | the measured savegame-editing failure class, for saves that are about to be re-made anyway |
| C. `temporary=true` through the bridge, so the engine removes it | the engine cleans vanilla references properly, and it has no pawns or world objects, so it qualifies | removal fires only on a later Notify event (a quest cleanup and the like), so the timing is not ours. Mods' own faction dictionaries keep a dead reference: `Could not resolve reference` on the next load. Not worth it on saves that will be re-made |

**Banish values.** Done in its own file (`src/RimMandrake/LeaningScrub/Defs/FactionDefs/RM_CombHolds.xml`):
`hidden`, `raidsForbidden`, `canGenerateQuestSites false`, start/max/required `0/0/0`,
`displayInFactionSelection false`. The header says why it is still there.

**The Scrub camps.** The camps of `RM_ScrubInjections` named it as `farmerFaction`. They now name Core's
`OutlanderCivil`.
- **Why OutlanderCivil:** the settled outlanders (the Homestead Defense League in the Utinni layer) are the nearest
  existing people to "vaporator farmers".
- **This is an agent default, and the owner may pick another.** The alternative is no farmer camps at all
  (`farmerFaction` empty, scavenger camps only).
- **The faction pick is his call.** The camps already skip a faction that is missing, defeated or hostile
  (`LivingFaction`).

**Delete the def, its 3 kinds and 2 namers** once no kept save holds it: `COMB_HOLDS_DEF_RETIRE_AFTER_THE_REMAKE`.

### Sacrileg Hunters — `CASacrilegHunters` (Caravan Adventures)

| option | cost | what breaks |
|---|---|---|
| A. **Keep the mod cut (Wave 4), keep a guarded banish block in case it returns** (RECOMMENDED, done) | none | Caravan Adventures' quests, sites and boss content are gone with the mod (already ruled in Wave 4) |
| B. Bring the mod back with the def banished | small | the def patch hides the faction and forbids its raids. But Caravan Adventures' own C# drives its Sacrileg Hunters story and may create or use the faction whatever the def says (UNMEASURED; the DLL was not read). It needs a fresh look first |

It is in no dev save and in no VEF ignore list, so the cut leaves no orphan. Under the 324 list the def does not load,
so `check-dump` reports it ABSENT.

### Space Exchange — `TradersGuild` (Odyssey DLC)

The owner asked whether its start requirement can be set to 0, or whether it can be made non-spawning, hidden,
removed from the world, or have its raid and incident weight zeroed. Each, verified:

| option | does it work? | cost / what breaks |
|---|---|---|
| `requiredCountAtGameStart` 0 | **No, on its own.** A page-made world never reads it, and `BackCompatibility.FactionManagerPostLoadInit` re-creates the faction on every load when absent | nothing; done anyway, so VEF skips it and the no-page path never makes it |
| make it non-spawning (start 0, max 0) | **Only for the Configure Factions page.** Start was already 0; max 0 removes the row | the load-time re-creation is untouched |
| remove it from the world (save edit or `temporary` removal) | **No.** It comes back on the next load, with a fresh `SpaceSettlement` platform if the def is visible | worse than leaving it, because each load rolls a new one |
| zero its raid weight | partly. It has no `raidCommonalityFromPointsCurve` (weight 1); `raidsForbidden` is the clean switch | raids only |
| Harmony-skip the Odyssey block of `FactionManagerPostLoadInit` | it would work | C# that patches a vanilla back-compat path, for no gain over banishing |
| **hidden + raidsForbidden at the def, orbital traders unfactioned, and on the save defeated + platform removed** (RECOMMENDED; def side done) | **Yes.** The instance that keeps existing satisfies Odyssey's check, so nothing is re-created; hidden keeps it off every list and arrival, and a re-created one gets no platform (`NewGeneratedFaction` skips settlements for hidden factions) | nothing measured: no QuestScriptDef or C# outside BackCompatibility names `TradersGuild` (RimSage, 2026-10-20). The Empire still lists it in `permanentEnemyToEveryoneExcept` (our `GalacticEmpire.xml`), which is harmless |

**The orbital traders.** `Orbital_BulkGoods`, `Orbital_CombatSupplier`, `Orbital_Exotic` and
`Orbital_PirateMerchant` have their `<faction>` removed, so the ships arrive factionless, which is the pre-Odyssey
behaviour.
- **Trade ships are not lost.** `CanSpawn` returns true when `trader.faction` is null.
- **The removal is required, not optional.** If the instance were absent, those four would never come
  (`GetFaction` would return null). Hidden alone leaves them announced "from the Space Exchange".
- **Techprints are not lost either.** With a null faction, `StockGenerator_Techprints` offers any techprint. Every
  research project our mods hold through the `TradersGuild` category tag also lists Empire (measured in the dump,
  32 projects), so none loses its last holder.

### Celestial Rogues — `Salvagers` (Odyssey DLC)

Banned by the owner's card, 2026-10-20: *"Celestial Rogues is another faction you may not want. Ban it too?"* ->
**"Ban Celestial Rogues"**. Same recipe as the Space Exchange, because the same engine path keeps it alive:
`BackCompatibility.FactionManagerPostLoadInit` re-creates a `Salvagers` faction on the Orbit layer on every load
when none exists (`FactionDefOf.Salvagers`, RimSage 2026-10-20). Removing it is impossible; it is banished in place.

- **The def** (Odyssey `Factions_Misc.xml`) already had `hidden`, `canGenerateQuestSites false`,
  `displayInFactionSelection false`, `permanentEnemy`, Orbit-only arrival. The banish block in `BannedFactions.xml`
  adds `raidsForbidden` (out of the enemy-raid pool, which `hidden` does not close), start/max/required `0/0/0`.
- **In the saves** (capture `2026-10-21T01-39-11Z`, read only): loadID 24 'The Celestial Rogues', hostile, leader
  present (`fixedLeaderKinds` Salvager_Elite), **0 settlements and 0 world objects** in `ASHKARR_DEV_START`,
  `_FACTIONS` and **`_PARITY_QUIET`**; absent from SHIP and FOUNDERS (gained on their next load, per source).
  `check-save` reports it LIVE (not defeated) in all three START saves. The save step is
  `CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT`.
- **What the banish does NOT stop: Odyssey content that spawns its pawns directly.** `QuestNode_Root_OrbitalFugitive`
  (quest `OrbitalFugitive`, weight 1) generates a `Salvager_Elite` and a Combat group with `Faction.OfSalvagers`;
  GenStepDefs `OrbitalFugitivePlatform` (`GenStep_OrbitalPlatform`) and `Opportunity_OrbitalWreck_Salvagers`
  (`GenStep_SitePawns`, "Hostile salvagers") name `factionDef Salvagers`; an ancient-crate ThingSetMaker uses the
  `Salvager_Pirate` kind. Defeated and hidden do not gate pawn generation, so orbital sites can still hold
  "salvager" pawns. Whether those go too is §8 decision 4. Nothing outside these names it (RimSage, 2026-10-20).

## 6. The general guard

1. **The registry is data:** `src/RimMandrake/Utils/factions/banned_factions.json`.
   - **Per faction:** the defName, the name it was seen under, its supplier, its disposition
     (`banish` | `supplier_cut`), why it is kept loadable, and the owner's words.
   - **Also held:** the `banish` field values with their reasons, the orbital trader list, and a reasoned
     allowlist of files that may name a banned def.
2. **The checker:** `src/RimMandrake/Utils/banned_factions.py`.
   - **`check-repo`:**
     - our banned def carries the banish values in its own file;
     - a donor or DLC def carries them in `src/RimUtinni/UtinniPatches/Patches/FactionSlate/BannedFactions.xml`,
       where the Replace and nomatch-Add branches must agree;
     - the orbital traders are unfactioned;
     - **no XML element, attribute or C# string literal under `src/` names a banned def** outside the allowlist
       (comments are not references). This is what catches the next `farmerFaction`.
   - **`check-save <rws>... [--dump <capture>]`:** every banned faction must be ABSENT or BANISHED (effectively
     hidden, defeated, owning no world object). LIVE fails.
   - **`check-dump <capture>`:** the running game's defs, which is the proof after deploy.
   - **Exit codes:** 0 PASS, 1 FAIL, 2 UNMEASURED (no factions parsed, an empty registry, a missing capture).
3. **The selftest:** `src/RimMandrake/Utils/selftest_banned_factions.py`, found by `run_selftests.py`'s glob.
   - **Against the repo:** check-repo must pass.
   - **The guard must be able to fail.** Each check is run on a fixture built to fail it: a wrong patch field, an
     orbital trader that keeps its faction, a GenStep reference, a C# literal against a comment, an empty registry,
     LIVE / half-banished / BANISHED / empty saves, and dumps before and after.
   - **Result:** 17/17.
4. **To ban another faction:** add the entry, give the def the banish values (an edit if it is ours, a guarded block
   in the patch if not), run the selftest, deploy, then `check-dump` and `check-save` after the next load.

Measured today:
- **check-repo:** PASS (4 registry entries after Salvagers, 2026-10-20; selftest 17/17).
- **check-dump on the pre-change capture:** FAIL on all 3 defs and the 4 traders, as expected. This is the baseline
  the post-deploy run must turn green.
- **check-save:** LIVE for `RM_Faction_CombHolds` in all four saves, and for `TradersGuild` in START, which owns a
  `SpaceSettlement`.

## 7. What can happen now, and what waits

| step | when | state |
|---|---|---|
| def banish (Comb Holds own file; TradersGuild + CASacrilegHunters patch; orbital traders) + Scrub camps retarget | now, offline | **done, not deployed** |
| deploy Baroque Biomes + UtinniPatches, one load, `check-dump` PASS | next load round (another agent is restarting the game now; not ours to take) | `UNWANTED_FACTIONS_SILENCE_NOT_DELETED` |
| dev saves: `jawa/faction_flags_set` hidden=true defeated=true for both; `jawa/world_objects_remove` the Space Exchange `SpaceSettlement`; save through the bridge; `check-save` PASS | with the bridge free, after the deploy | same item, needs=bridge |
| SHIP / LANDED / FOUNDERS gain `TradersGuild` + `Salvagers` on first load (source); banish it there too | the same sitting, per save | same item |
| shipped world: the Configure Factions page no longer offers either (max 0), so a re-made world never holds Comb Holds; Odyssey still adds the Space Exchange on its first load, so the remake runbook S7 now requires `check-save` PASS (banish it there) | at the re-make | `06_remake_runbook.md` S7/G15 edited |
| VEF: the shipped save's `ignoredFactions` should hold every absent, offerable def (3 today), or players get pop-ups | at the re-make | noted in the runbook item, not filed separately |
| Celestial Rogues (`Salvagers`): deploy UtinniPatches, `check-dump` PASS; dev saves `jawa/faction_flags_set faction=Salvagers hidden=true defeated=true`, save, `check-save` PASS | same load round / bridge sitting | `CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT` |
| delete `RM_Faction_CombHolds` + its kinds and namers | after no kept save holds it | `COMB_HOLDS_DEF_RETIRE_AFTER_THE_REMAKE` |

## 8. Decisions left to the owner (agent defaults taken, all reversible)

1. **Who farms the Scrub's vaporators now?** The default is `OutlanderCivil` (the Homestead Defense League). The
   alternative is no farmer camps at all.
2. **Salvagers ("The Celestial Rogues"):** ruled 2026-10-20 by card, banned (§5).
3. **The three VEF offers** (`GR_RoamingMonstrosities`, `VFEP_Junkers`, `VFEP_Mercenaries`): add them, ban them, or
   ignore them in the shipped world.
4. **Celestial Rogues' pawns at Odyssey orbital sites** (the `OrbitalFugitive` quest, the orbital-wreck salvager
   guards): keep them as anonymous orbital pirates, or cut that content (zero the quest's `rootSelectionWeight`,
   remove the salvager GenStep). Default taken: kept, because the card banned the faction, not the content.
