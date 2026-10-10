# Beskar armorer quest: the decided design (2026-10-09)

Item: `BESKAR_ARMORER_QUEST_1`. Parent: `CANON_MATERIALS_BUILD_1` (its L7). All design questions are ruled; this
is the build spec for FOUNDRY.

## 0. Rulings

- Owner, typed 2026-10-09: *"(1) and a quest with Blackstar allows you to access that rare individual,
  otherwise you just use the pieces you find. Never can reforge yourself, smelting destroys it (converts into
  other lesser ores), only the rare location can properly reforge."*
- Owner, typed 2026-10-09: *"Capturing then freeing a mandalorian bounty hunter is the preferred way.
  Alternative path later is to receive a quest to help them break out a mandalorian from a small prison run by
  the empire. Cool quest destination and very direct. I like this quest. Raises your heat a lot."*
- Decisions taken by question card 2026-10-09:
  - The Armorer works at a **base in orbit**, reached **by gravship**.
  - A reforge returns **the same beskar mass as gear of your choice**; she **keeps 1 in 5** as tribute.
  - **Smelting beskar yourself yields steel + slag.**
  - **You can return any time.**
  - **Harming her or her base loses the base for good AND Blackstar hunts you at max heat.**

What follows from them:

- Beskar pieces are salvage. The colony wears and wields them as found.
- No colony recipe makes beskar, and no colony bill may consume beskar.
- The only place beskar becomes other beskar gear is the Armorer's forge in her orbital covert.
- Two ways to learn where the covert is: route 1 (§3), route 2 (§4). Both end in the same reveal (§3.3).

## 1. Fiction

**Blackstar Company** is the vanilla `Pirate` faction reskinned (`src/RimUtinni/UtinniPatches/Patches/BlackstarCompany.xml`,
`design/Jawa/worldbuilding/FACTION_SPEC.md` entry 10), `permanentEnemy true` on purpose. Its Mandalorians are
pawn kinds `RUT_Jawa_Blackstar_Heavy` (label "Mandalorian") and `RUT_Jawa_Blackstar_Leader` (Captain Jaxen Marr)
in `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml`. Its ideoligion, the Contract, honours a
fair release; freeing a hunter is the one lever the lore gives on a permanent enemy
(`reconciled_lore/04_factions.md` §10).

**Canon** (Wookieepedia `The_Armorer`, `Beskar`, `Mandalorian_covert`, pulled 2026-10-09): the Armorer forges in
a hidden covert; after Nevarro hers sat on Glavis Ringworld in space, a cryo-furnace beside a corridor open to
vacuum. She reforges salvage to the wearer's wish and keeps the excess "for future foundlings". That is the
orbital covert and the 1-in-5 tribute.

**The beat:** a freed Mandalorian owes the clan that let him go. He pays the only way his Creed allows: he tells
the Armorer that this clan keeps beskar honourably, and she sends coordinates.

## 2. The orbital covert (the one place beskar is reforged)

### 2.1 World object

- **`RM_ArmorerCovert`**: a `WorldObjectDef` on the **`Orbit`** planet layer (Odyssey `PlanetLayerDef Orbit`),
  `worldObjectClass` = **`RimMandrake.Utinni.BeskarArmorer.RM_ArmorerCovert : MapParent`** (new, small).
  - Permanent: it is **not** a `Site`. A quest-spawned world object survives quest end once spawned
    (`QuestPart_SpawnWorldObject.Cleanup` destroys it only if it never spawned; decompiled 1.6).
  - `ShouldRemoveMapNow` = no player pawns or player gravship on the map. The **map is discarded on departure
    and regenerated from the fixed layout on each visit**; the object itself stays. Cheap, and "return any
    time" needs nothing else.
  - Holds, scribed: the Armorer and her two sworn guards as **world pawns** (the same three pawns every visit,
    respawned into the regenerated map), a `lost` flag, and the revealed tick.
  - Hidden until revealed: the object is spawned by the reveal (§3.3), never at world start, so nothing shows
    on the planet before.
  - 🔴 UNVERIFIED, read before building: which check lets a gravship **land on a non-`Site` `MapParent`** in
    orbit. Vanilla Odyssey lands on `ClaimableSpaceSite` (`WorldObjectDefOf.ClaimableSpaceSite`, used by
    `QuestNode_Root_Gravcore_OrbitalAncientPlatform`). If the landing gate is that def or `SpaceMapParent`,
    derive `RM_ArmorerCovert` from `SpaceMapParent` instead of `MapParent`.
- **Map**: `MapGeneratorDef` `RM_ArmorerCovertMap` = Odyssey's orbital-platform base generation (the
  `OrbitalAncientPlatform` site part's generator is the reference) plus one `GenStep` that stamps
  `StructureLayoutDef` `RM_ArmorerCovertLayout`: a small derelict platform, a cryo-furnace bay beside a
  vacuum-open service corridor (canon), quarters, a landing pad. Layout pattern:
  `src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/StructureLayoutDefs_Vaults.xml`.
- **Faction**: `RM_TribeOfTheArmorer`, a **hidden** `FactionDef` (no settlements, not in the faction tab, starts
  neutral-friendly, `permanentEnemy false`). Hidden so it never raids or trades; it exists so her pawns are
  non-hostile and so harm to them is attributable.
- **Cast**: the Armorer (`RM_TheArmorer` `PawnKindDef`: Human, Mandalorian armour of beskar stuff, the fixed
  name *the Armorer*, unrecruitable, non-capturable by any vanilla route the C# can close) and two
  `RM_CovertSworn` guards. Inhabited's PLACE / CAST shape (`src/RimMandrake/Inhabited`) is the reference for a
  named persistent cast of a place.

### 2.2 The forge and the reforge

- **`RM_ArmorerForge`**: a `Building_WorkTable`, **not buildable and not minifiable** (no
  `designationCategory`, no `minifiedDef`), spawned only by `RM_ArmorerCovertLayout`. Indestructible to
  pawns is not needed: harming it is the harm rule (§2.3).
- **Two kinds of bill on it, and only on it:**
  1. **`RM_Recipe_ArmorerMeltBeskar`**: any thing carrying beskar (§5.1 list) → `KOTOR_IngotBeskar` equal to
     its **beskar mass × 0.8**. The 1-in-5 tribute is taken **here, once**. Beskar mass of a thing = its
     `costList` count of a beskar material, or its `CostStuffCount` if it is made of beskar stuff; full mass
     regardless of hit points. Custom `RecipeWorker` (`RM_RecipeWorker_ArmorerMelt`) computes the count.
  2. **`RM_Reforge_<ThingDef>`**: one generated recipe per beskar product: every apparel/weapon whose
     `costList` names a beskar material (the six Mando pieces in
     `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Apparel/Absorbed_KotorWeapons_Apparel_KotORFactions_Mando.xml`
     and any Outer Rim beskar gear), at that def's own beskar cost, plus every stuffable `Metallic` apparel or
     weapon made **of beskar** at its normal stuff count. Generated at startup (a `DefGenerator`-style
     `[StaticConstructorOnStartup]` pass, `recipeUsers = RM_ArmorerForge`). That list **is** "gear of your
     choice"; the vanilla bill UI is the reforge menu.
  - Net effect: carry beskar pieces up, melt them (she keeps a fifth), queue the gear you want from the
    ingots; same mass in, same mass out, less tribute. Leftover ingots can go home: they are still
    unusable there (§5.2).
- **Only she works these bills.** Bill postfix (§5.2) allows a pawn to start a bill at `RM_ArmorerForge` only
  if it carries the `RM_ArmorerOfTheTribe` hediff (given to her `PawnKindDef`). Colonists cannot.
- **Time**: her crafting skill (fixed 20) on the recipe's work amount; about a day per armour piece. The
  gravship waits docked; fuel is the travel cost.
- **Any time**: no visit limit, no cooldown.

### 2.3 Harm rule: the base is lost for good

Harm = any of, by the player faction:
- damage to the Armorer or a sworn guard (`dinfo.Instigator?.Faction == Faction.OfPlayer`), anywhere;
- arresting or capturing any of the three (`Pawn_GuestTracker.CapturedBy` with `Faction.OfPlayer`);
- damage to any building on the covert map, `RM_ArmorerForge` included;
- any of the three killed while a player pawn is on the covert map.

Consequence, at once and permanently:
1. `RM_ArmorerCovert.lost = true`; the object is destroyed when the player leaves the map (the current visit is
   not yanked away mid-fight). It is never re-spawned: both reveals (§3, §4) check `lost` and refuse.
2. Her faction turns hostile for that visit (the guards fight).
3. **Blackstar hunts at max heat** (§6): heat for `Pirate` set to max, and one Blackstar raid is fired at once
   on the player's home map, `RaidEnemy` with faction `Pirate`, points × 2, Mandalorians preferred.
4. A letter says so plainly: the Creed's verdict, the covert gone, Blackstar coming.

## 3. Route 1 (preferred): capture, then free, a Blackstar Mandalorian

### 3.1 Trigger (reuse RaidRedesigner's freed-hunter detection)

`src/RimMandrake/RaidRedesigner/Source/Patch_PrisonerReleasedOrNamedHunter.cs` already postfixes
`GenGuest.PrisonerRelease(Pawn)` and tags any `Pirate` release `RoleTag.NamedHunter`. Add, in the BeskarArmorer
assembly (its own Harmony postfix on the same method, so RaidRedesigner stays untouched and either mod can be
off):

- **Condition**: released pawn's `kindDef` is `RUT_Jawa_Blackstar_Heavy` or `RUT_Jawa_Blackstar_Leader`, it is
  alive, and it was a **prisoner of the player** at release; the covert is not yet revealed and not lost; no
  route-1 or route-2 quest is already running.
- **Action**: `QuestUtility.GenerateQuestAndMakeAvailable(RM_Quest_ArmorerDebt, slate{ hunter })` and
  `QuestUtility.SendLetterQuestAvailable`.
- The choice it leaves the player is real: keep him (recruit him, strip his beskar plate, which counts as found
  beskar) or free him and get the covert. His plate stays on him if freed.

### 3.2 `RM_Quest_ArmorerDebt` (QuestScriptDef shape)

Firing route: **from C#** (§3.1): `isRootSpecial true`, `rootSelectionWeight 0`, no `IncidentDef`.
`autoAccept true` (it is news, not a job). `everAcceptableInSpace true`.

```
root QuestNode_Sequence
  QuestNode_GetMap                         canBeSpace true            -> map
  QuestNode_Letter  (no inSignal: fires on accept)
      "[hunter_nameDef] walks out of your gate. A Blackstar Mandalorian does not thank anyone. He says the Creed
       keeps its debts, and that someone will hear of the clan that let him go."
  QuestNode_Set  revealTicks = $(randInt(2,5)*60000)
  QuestNode_Delay  delayTicks $revealTicks  outSignalComplete RevealDue
  RM_QuestNode_RevealArmorerCovert        inSignal RevealDue  outSignal CovertRevealed
  QuestNode_Letter  inSignal CovertRevealed  (positive letter, lookTargets = the covert)
  QuestNode_End  inSignal CovertRevealed  outcome Success
  QuestNode_End  inSignal RevealRefused   outcome Unknown   (covert already revealed or lost meanwhile)
```

Text: `questName->The Creed Keeps Its Debts`; description names `[hunter_nameDef]` and says the coordinates will
come. Every conditional symbol gets an empty fallback (rimworld-quests §5).

### 3.3 The reveal (shared by both routes)

**`RM_QuestNode_RevealArmorerCovert`** (C#, small): finds a tile on the `Orbit` layer adjacent to the player's
home layer, 20–60 tiles out, reachable (copy `QuestNode_Root_Gravcore.TryFindSiteTile`'s query; vanilla
`QuestNode_GetSiteTile` cannot target a different layer), generates and spawns `RM_ArmorerCovert` with its three
world pawns, and emits `CovertRevealed`. If the covert already exists or is `lost`, it emits `RevealRefused`
instead. `TestRunInt` returns false without Odyssey (all DLCs are assumed, but the guard costs nothing).
Gate acceptance with `QuestNode_RequirementsToAcceptPlanetLayer` only if a reveal ever needs the player in orbit;
it does not today.

## 4. Route 2 (later): break a Mandalorian out of an Imperial prison

### 4.1 The ask

Blackstar sends word: one of their Mandalorians is held at a small Imperial detention post on the surface.
Get him out. Very direct: one site, one prisoner, one fight. **Raises your heat a lot** with the Empire, and the
freed Mandalorian pays the same debt as route 1.

### 4.2 `RM_Quest_ImperialPrisonBreak` (QuestScriptDef shape)

Firing route: **a dedicated incident** `RM_BlackstarPrisonBreakOffer` (`category GiveQuest`,
`workerClass IncidentWorker_GiveQuest`, `questScriptDef RM_Quest_ImperialPrisonBreak`); the quest has
`isRootSpecial true`, `rootSelectionWeight 0` (an incident-plus-weight pair is a hard vanilla ConfigError,
rimworld-quests §7). "Later": `rootEarliestDay` 30, `minRefireDays` 60 (tuning, Mod Settings). The incident's
worker refuses while the covert is revealed or lost, or a route-1 quest is running. Shape copied from vanilla
`OpportunitySite_PrisonerWillingToJoin` (`Defs/Core/QuestScriptDefs/Script_PrisonerWillingToJoin.xml`), which is
a prisoner breakout at a site already:

```
root QuestNode_Sequence
  QuestNode_SubScript Util_RandomizePointsChallengeRating
  QuestNode_SubScript Util_AdjustPointsForDistantFight
  QuestNode_GetMap                          canBeSpace true
  QuestNode_GetSiteTile  storeAs siteTile   preferCloserTiles true
  QuestNode_GetFaction (Empire)             -> siteFaction       (vanilla Empire, reskinned: Patches/GalacticEmpire.xml)
  QuestNode_Set  sitePartDefs = [RM_ImperialDetentionPost]
  QuestNode_GetDefaultSitePartsParams  tile $siteTile  faction $siteFaction  -> sitePartsParams
  QuestNode_SubScript Util_GenerateSite
  QuestNode_SpawnWorldObjects  $site
  QuestNode_WorldObjectTimeout  $site  isQuestTimeout true  delayTicks $(randInt(10,20)*60000)
        inSignalDisable site.MapGenerated   node: QuestNode_End outcome Fail
  -- on arrival: he fights beside you until he is out --
  QuestNode_ExtraFaction  inSignal site.MapGenerated  pawns [$detainee]  (lodger shape, as Quest_DroidRepairJob.xml)
  -- success: he leaves the site map alive with you (caravan, gravship or map edge) --
  RM_QuestNode_AddHeat  inSignal detainee.LeftMap  faction Empire  amount Large    (§6)
  QuestNode_Delay  inSignal detainee.LeftMap  delayTicks $(randInt(2,4)*60000)  outSignalComplete PursuitDue
  QuestNode_SubScript Util_Raid  inSignal PursuitDue  (Empire, points × 1.5: the heat arriving)
  QuestNode_Leave  inSignal PursuitDue  pawns [$detainee]   (he goes home; no release needed)
  RM_QuestNode_RevealArmorerCovert  inSignal PursuitDue  outSignal CovertRevealed
  QuestNode_End  inSignal CovertRevealed  outcome Success
  QuestNode_End  inSignal RevealRefused   outcome Success   (heat still paid; reveal already had)
  QuestNode_End  inSignal detainee.Destroyed  outcome Fail
  QuestNode_NoWorldObject $site  node: QuestNode_End (Unknown)
```

🔴 UNVERIFIED, read before building: whether `detainee.LeftMap` fires when he leaves **inside a caravan or a
departing gravship** as well as by the map edge (vanilla Hospitality lodgers use `.LeftMap`; check
`QuestPart_ExtraFaction` / `Pawn.ExitMap` signal emission). If not, success is the site map's `MapRemoved` with
`$detainee` alive and not on it, via a small check node.

### 4.3 The site: `RM_ImperialDetentionPost`

- `SitePartDef` with its own worker `RM_SitePartWorker_ImperialDetainee` (subclass the vanilla
  `SitePartWorker_PrisonerWillingToJoin`, which already places a prisoner in a cell and writes the slate var):
  generates `$detainee` as a `RUT_Jawa_Blackstar_Heavy`, **faction `Pirate`**, held prisoner by the Empire,
  stripped of weapon, plate in an evidence locker on the map (a beskar find in its own right).
- Map: `StructureLayoutDef` `RM_ImperialDetentionPostLayout`: a small prefab post, four to six cells, a guard
  room, a comms mast, a landing pad; Empire guards scaled by `$points`. Same StructureInjections pattern as the
  Vault dungeons (`SitePartDefs_Vaults.xml`, `StructureLayoutDefs_Vaults.xml`).
- Stakes: the quest can be failed (timeout, or he dies) and failing is survivable. The choice: walk away from
  the offer, or buy the covert with Imperial heat.

## 5. The minimal C# seam: no reforging anywhere else, smelting yields steel + slag

New assembly `RimMandrake.Utinni.BeskarArmorer` (its own mod folder under `src/RimUtinni/BeskarArmorer`,
packageId `mandrake.rut.beskararmorer`, Harmony). Everything here is in it.

### 5.1 What counts as beskar

`DefModExtension` **`RM_BeskarMaterial`** on: `KOTOR_IngotBeskar`, `KOTOR_RawBeskar`, `OuterRim_Beskar`,
`OuterRim_PureBeskar`, `LKBeskar_Ore`, `guy762_crystalitem_beskar` (patched in, each `MayRequire`-guarded per its
mod; never a top-level `<Operation MayRequire>`). A thing **carries beskar** if its def has the extension, its
stuff has it, or its `costList` names a def that has it.

### 5.2 Three patches, nothing else

1. **No colony bill consumes beskar.** Postfix `Bill.IsFixedOrAllowedIngredient(Thing)` and
   `Bill.IsFixedOrAllowedIngredient(ThingDef)`: if the ingredient carries beskar and the bill's
   `billStack.billGiver` is not an `RM_ArmorerForge`, return false. This blocks the Mando gear recipes, any
   stuffable Metallic recipe picking beskar as stuff, and any mod recipe we have not seen, with no def edits.
   The six Mando `recipeMaker` blocks are patched out as well so the colony bench does not list bills it can
   never fill.
2. **Only the Armorer works her forge.** Postfix `Bill.PawnAllowedToStartAnew(Pawn)`: at `RM_ArmorerForge`,
   false unless the pawn has hediff `RM_ArmorerOfTheTribe`.
3. **Smelting beskar yields steel + slag.** Postfix `Thing.SmeltProducts(float)` (virtual, `Verse/Thing.cs`):
   replace every beskar output with **`Steel` = ⌈beskar count / 3⌉** plus **one `ChunkSlagSteel`**. Covers vanilla
   smelting of apparel and weapons at the electric smelter. (Overrides that do not call base are not covered;
   list any found.) The 1/3 is a Mod Settings number; the owner ruled "steel + slag", not the ratio.

Plus the covert's own pieces: `RM_ArmorerCovert` (world object), `RM_QuestNode_RevealArmorerCovert`,
`RM_SitePartWorker_ImperialDetainee`, `RM_RecipeWorker_ArmorerMelt`, the startup recipe generator, the
release postfix (§3.1), and the harm watcher (§2.3: postfix `Thing.TakeDamage`, postfix
`Pawn_GuestTracker.CapturedBy`, and a death check on her pawns).

### 5.3 What goes, and where it is tracked

- **The Armoury's `kotor_IngotBeskar_recipe`** (3 raw beskar → ingot at a colony smelter,
  `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Resources/Absorbed_KotorCore_KotORResource_Metals2.xml`)
  is **removed**, and beskar mining routes yield nothing. Both are **`CANON_MATERIALS_BUILD_1` L7**, not this
  item (`MATERIAL_MERGES_CLEANUP_1` does not list them). Patch 1 above would block that recipe anyway; L7
  deletes it so nothing dead is listed.

## 6. Heat

Heat today is **`src/RimMandrake/Utils/gm_blackboard_shadow.py`** (`GM_BLACKBOARD_SHADOW_M4_1`): a Python,
shadow-mode Imperial Heat number fed by polled bridge reads, firing nothing. Blackstar's Heat-scaled raid
weight (`design/Jawa/worldbuilding/faction_roster_v2.md` §Blackstar) is designed, not built. So this item does
**not** build a heat system. It does two things:

- **Records** heat in game: `RM_QuestNode_AddHeat` (and the harm rule) append `{tick, faction, amount, source}`
  to a scribed `GameComponent` `RM_HeatEvents`, and a JawaBench read tool `jawa/heat_events` exposes it, so the
  blackboard takes it as one more input. Amounts: route 2 success = **Large** (+30 on the blackboard's scale,
  where `HEAT_HIGH_BAND` is 40); harm = **Max** for `Pirate`.
- **Delivers the teeth now, in vanilla**: route 2's Empire pursuit raid (§4.2), and the harm rule's immediate
  Blackstar raid (§2.3). When the Heat-scaled raid weights are built, they read `RM_HeatEvents` and these
  one-off raids stay as the first blow.

## 7. Mod Settings

On/off: route 1, route 2, the harm rule's raid. Numbers: tribute (default 1 in 5), smelt steel ratio (1/3),
route-2 earliest day (30) and refire (60), reveal delay (2–5 days). Defaults are the shipped behaviour. With the
whole mod off, beskar is salvage and smelts normally.

## 8. Checks for FOUNDRY

- `python3 skills/rimworld-quests/scripts/validate_quest.py --dir src/RimUtinni/BeskarArmorer/Defs/QuestScriptDefs`
  clean.
- Deterministic triggers, never the storyteller: a debug action that releases a spawned
  `RUT_Jawa_Blackstar_Heavy` prisoner (route 1), dev *Generate quest* for `RM_Quest_ImperialPrisonBreak`
  (route 2).
- Selftests (offline) for: beskar mass of a thing, melt count × 0.8, smelt replacement, the bill ingredient gate.
