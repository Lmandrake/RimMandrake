# Sith line — redesign of the Sanguophage xenotype

item: `SANGUOPHAGE_KEPT_UNREACHABLE_1` · status: DESIGN, nothing built · author: BENCH design helper, 2026-10-09
Numbers marked PROVISIONAL are starting values for FOUNDRY to tune. Every vanilla defName below was read
from RimSage (decompiled 1.6 + Biotech/Royalty defs) on 2026-10-09, not guessed.

## 0. Rulings this spec builds (do not re-litigate)

- Owner, typed 2026-10-09: *"Redesign into a sith line among the empire as well as lurking in the Crags biome
  rarely. But none of the buildings are buildable by the player nor can they convert others to their line."*
- Decided by question card 2026-10-09 (ledger note on the item):
  - "Crags" = **`RM_Abyss`** (`src/RimMandrake/Abyss`, folded at runtime into `mandrake.rm.biomes`).
  - **This is a reskin of the vampire.** Hemogen, bloodfeed and deathrest machinery stays and is retold as
    dark-side life-drain and meditation trance. Only text, art and gene names change. **No new mechanics.**
  - **Never recruitable.** A Sith is always an enemy, and a Sith prisoner never joins.
  - **Abyss:** a RARE hidden lair site holding one lone Sith and their structures, which the player cannot
    build. The player raids it for loot.
  - **Empire:** a rare elite (inquisitor type) in Empire raids and visiting parties.
- **Constraint:** the `Sanguophage` XenotypeDef can't be deleted. `XenotypeDefOf.Sanguophage` is a
  `[MayRequireBiotech]` DefOf binding, and Biotech is always active
  (`infrastructure/state/items/closed/VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1.md` §2). **So the Sith line IS
  the `Sanguophage` def, relabelled.** No new XenotypeDef.
- All DLCs are assumed present. The Galactic Empire is vanilla `Empire` reskinned by
  `src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml`.

### Already in the repo (read before building)

- `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` already **relabels `Sanguophage`**: it sets
  the label to "Sanguophage" and adds a Jawa-voice description. It is the campaign layer, so it loads after
  this mod and **would overwrite the Sith relabel**. That block must be rewritten to Sith wording in the same
  change (§1.4).
- `src/RimUtinni/UtinniPatches/Patches/XenotypeCut_SpawnSets.xml` already strips `Sanguophage` from the
  `Empire_*` noble xenotype sets. **Keep it.** Sith reach the Empire only through the inquisitor kind (§4),
  never as random nobles.
- `src/RimUtinni/UtinniPatches/Patches/Abyss_CryptidSithWhisper.xml` already has Abyss whispers naming the
  Sith. The lair rumour (§3) reuses that voice.
- `src/RimMandrake/Abyss/Defs/BroodLair/RM_BroodLair.xml` is the existing rare-Abyss-feature pattern: a
  `TileMutatorDef` plus a global self-gating `GenStepDef`. §3 compares against it.
- `src/RimMandrake/Inhabited/Defs/CastRosters/CastRoster_EMPIRE.xml` already has
  `Inhabited_Empire_InquisitorVaunt` (race "Sith", weapon `Force_Lightsaber_Inquisitor`). It is a separate
  system and nothing here changes it. It is the natural named face of §4.
- Absorbed assets this design can reuse: the namers `guy762_NamerPawnKind_MaleInquisitor` /
  `_FemaleInquisitor` ("… Brother" / "… Sister", the canon Inquisitorius pattern), the apparel
  `guy762_SithHood_masked`, and the crystal `guy762_SWForceLightsabers_CrystalPart_red`
  (`src/RimStarWars/Armoury`). The weapon `Force_Lightsaber_Inquisitor` is only *patched* in `src/`.
  **Which mod defines it is UNMEASURED**, so FOUNDRY resolves that with `measure` before referencing it, and
  every reference carries `MayRequire` on its `<li>`.
- ⚠️ **The Anzati share this machinery.** `RSW_RimMandrakeAnzati`
  (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`) carries `Hemogenic`,
  `HemogenDrain`, `Bloodfeeder`, `Coagulate` and `Deathrest`. Any global relabel or buildability change
  reaches them too. See Open Question 1.

## 1. Def list

The mechanism column uses these patch types. 🔴 `MayRequire` on a top-level `<Operation>` is ignored by the
engine. Every guard is a `PatchOperationConditional` on the target node's existence. Biotech and Royalty are
hard dependencies in `About.xml`, so no DLC guards are needed.

### 1.1 Reused as-is (mechanics unchanged, text unchanged): 25

The generic archite and stat genes on the xenotype keep their vanilla labels. Other xenotypes and the gene
library use them, so renaming them would mislabel everyone else:
`Ageless`, `Deathless`, `TotalHealing`, `PerfectImmunity`, `DiseaseFree`, `ToxResist_Total`,
`WoundHealing_SuperFast`, `ArchiteMetabolism`, `PsychicAbility_Enhanced`, `LowSleep`, `Beauty_Pretty`,
`MoveSpeed_Quick`, `MeleeDamage_Strong`, `DarkVision`, `AptitudeStrong_Melee`, `AptitudeStrong_Social`,
`AptitudeStrong_Intellectual`, `UVSensitivity_Mild`, `FireWeakness`, `FireTerror`, `Aggression_Aggressive`,
`Robust`, `LongjumpLegs` + AbilityDef `Longjump` (24 genes + 1 ability). Also reused, with the count not
claimed: the gene classes (`Gene_Hemogen`, `Gene_Deathrest`, …), `PrisonerInteractionModeDef`
`Bloodfeed`/`HemogenFarm`, `RecipeDef` `ExtractHemogenPack`, and every sound, effecter, fleck and mote.

### 1.2 Relabelled (label + description, plus `labelShortAdj`/`resourceLabel`/`reportString` where present): 37

The defNames stay. Each row gives the new name and its one-line flavour text, which becomes the
description's first sentence. The wording is PROVISIONAL and the owner reads it at review. Canon terms were
checked against Wookieepedia's search API on 2026-10-09: Inquisitorius ✓, Force drain ✓, Sith alchemy ✓,
Sith holocron ✓, Sith Inquisitor ✓. Everything else is invented in a Star Wars style.

| # | Def | New name | Flavour |
|---|---|---|---|
| 1 | XenotypeDef `Sanguophage` | **Sith** (see OQ4) | A lineage that bound itself to the dark side and now lives on what it takes from others. Ageless, near-deathless, never one of yours. |
| 2 | FactionDef `Sanguophages` | **the Sith** | A hidden, scattered line of dark-side adepts who answer to no one. |
| 3 | PawnKindDef `Sanguophage` | **Sith** | A lone dark-side adept. |
| 4 | GeneDef `Hemogenic` | **dark-side reservoir** | The carrier holds a reserve of stolen life that fuels their other gifts. (`resourceLabel` → "essence") |
| 5 | GeneDef `HemogenDrain` | **dark-side hunger** | The reserve bleeds away faster. The dark side is never satisfied. |
| 6 | GeneDef `Bloodfeeder` | **life-drain** | The carrier can draw a living being's strength into themselves. |
| 7 | GeneDef `Coagulate` | **dark mending** | The carrier can close wounds by forcing stolen life into them. |
| 8 | GeneDef `Deathrest` | **dark trance** | The carrier must periodically sink into days of meditation in which the dark side remakes them. |
| 9 | GeneDef `PiercingSpine` | **telekinetic shard** | The carrier hurls a shard of bone or stone with the Force. |
| 10 | AbilityDef `Bloodfeed` | **Force drain** (canon) | Pull the life from a held victim. |
| 11 | AbilityDef `Coagulate` | **dark mending** | Seal a wound with stolen life. |
| 12 | AbilityDef `PiercingSpine` | **telekinetic shard** | Hurl a shard with the Force. |
| 13 | AbilityCategoryDef `Sanguophage` | **Sith arts** | |
| 14 | NeedDef `Deathrest` | **trance** | |
| 15 | HediffDef `Deathrest` | **in dark trance** | |
| 16 | HediffDef `InterruptedDeathrest` | **broken trance** | Torn out of meditation before the dark side finished its work. |
| 17 | HediffDef `DeathrestExhaustion` | **trance-starved** | |
| 18 | HediffDef `HemogenCraving` | **essence hunger** | |
| 19 | ThoughtDef `HemogenCraving` | essence hunger | |
| 20 | ThoughtDef `DeathrestExhaustion` | trance-starved | |
| 21 | ThoughtDef `DeathrestChamber` | meditated in a sanctum | |
| 22 | RoomRoleDef `DeathrestChamber` | **Sith sanctum** | |
| 23 | ResearchProjectDef `Deathrest` | **Sith lore** | Studying what the Sith leave behind. It unlocks nothing you can build. (The buildings' prerequisites and the Bloodfeeding meme reference it, so it stays.) |
| 24 | ThingDef `DeathrestCasket` | **Sith sarcophagus** | A black stone coffin where a Sith lies in trance. |
| 25 | ThingDef `Hemopump` | **essence alembic** | Sith alchemy (canon) that steeps the sleeper in drawn life. |
| 26 | ThingDef `HemogenAmplifier` | **dark focus** | An idol that sharpens what the sleeper takes. |
| 27 | ThingDef `GlucosoidPump` | **rage font** | Feeds the sleeper's body on hatred. |
| 28 | ThingDef `PsychofluidPump` | **holocron cradle** | A pyramid of whispering crystal that feeds the sleeper's mind (styled on the canon Sith holocron). |
| 29 | ThingDef `DeathrestAccelerator` | **trance obelisk** | Deepens the trance so it ends sooner. |
| 30 | ThingDef `HemogenPack` | **essence vial** | |
| 31 | ThingDef `DeathrestCapacitySerum` | **trance serum** | |
| 32 | GeneCategoryDef `Hemogen` | **dark side** | |
| 33 | InteractionDef `SanguophageChat` | **Sith discourse** | |
| 34 | JobDef `Deathrest` | `reportString` "in dark trance" | |
| 35 | HediffDef `HemogenAmplified` | dark-focused | |
| 36 | HediffDef `GlucosoidRush` | rage-fed | |
| 37 | HediffDef `PsychofluidRush` | holocron-fed | |

**Mechanism:** `PatchOperationReplace` on `label`/`description` (and the extra fields), each inside a
`PatchOperationConditional` on the node. One file per def family under `Patches/Relabel_*.xml`. UI text
that is hard-coded in Keyed strings (the gene gizmo's "hemogen", the deathrest gizmo) is overridden from
`Languages/English/Keyed/RSW_SithLine.xml`. FOUNDRY lists the keys from RimSage's `Languages` tree; they are
not guessed here.

**Art (owed, through the art ledger, after checking `artpipe_state.py find` for existing work):**
xenotype icon, 6 gene icons, 3 ability icons, 6 building textures (sarcophagus, alembic, dark focus, rage
font, holocron cradle, obelisk), essence vial, trance serum. Until each lands, the vanilla texture stays.
That is a deliberate placeholder, not a defect.

### 1.3 Suppressed: 9 routes

| # | Route | Mechanism |
|---|---|---|
| S1 | QuestScriptDef `SanguophageMeetingHost` (host a meeting; its own text says downed sanguophages can be "forced to turn one of your own colonists") | `PatchOperationReplace` `rootSelectionWeight` 0.5 → **0** (the node exists in vanilla). |
| S2 | QuestScriptDef `SanguophageShip` (capture the master and "force [them] to turn one of your colonists") | Same: `rootSelectionWeight` → 0. |
| S3 | ScenarioDef `Sanguophage` (start as one) | `PatchOperationAdd` `<showInUI>false</showInUI>` into `ScenarioDef[defName="Sanguophage"]/scenario` (field `Scenario.showInUI`, default true). The def stays because it is referenced. |
| S4 | PawnKindDef `Sanguophage_Player` | Reachable only from S3. Unreachable once S3 is hidden. No patch. |
| S5 | PawnKindDef `SanguophageThrall` | Reachable only from S2's quest code. Unreachable once S2 is off. No patch. |
| S6 | **Conversion by xenogerm**: GeneDef `XenogermReimplanter` → AbilityDef `ReimplantXenogerm`, and the "absorb xenogerm" float menu (`FloatMenuOptionProvider_Xenogerm` → `GeneUtility.CanAbsorbXenogerm`, which requires the target to have `XenogermReimplanter` active) | (a) `PatchOperationRemove` `XenotypeDef[defName="Sanguophage"]/genes/li[text()="XenogermReimplanter"]`. No Sith ever carries it, so the ability and the absorb option never appear. (b) Backstop: Harmony postfix on `GeneUtility.CanAbsorbXenogerm` returns false for any pawn whose `genes.Xenotype == XenotypeDefOf.Sanguophage`, which covers a dev-spawned or older-save Sith that still has the gene. |
| S7 | **Building them**: the 6 buildings in §1.2 #24–29 | `PatchOperationRemove` `designationCategory` on `ThingDef[defName="DeathrestCasket"]` and on the abstract `ThingDef[@Name="DeathrestBuildingBase"]` (the 5 bound buildings inherit from it). With no designation category, the architect menu can't place them. |
| S8 | **Reinstalling a looted one** (minify → reinstall is building it) | `PatchOperationRemove` `minifiedDef` on the same two defs, and `building/claimable` → false (Add) so a lair building never becomes the player's. Deconstruction still pays out resources. |
| S9 | **Joining the colony** | Not a def. It is the never-recruitable guard in §2. |

**Not suppressed, on purpose:** the FactionDef `Sanguophages` is repurposed as the lair Sith's faction (§3).
Add `<permanentEnemy>true</permanentEnemy>` (absent in vanilla → Add). It stays `hidden` with
`requiredCountAtGameStart` 0, so it exists only when a lair generates it. The reward set in
`ThingSetMakers_Reward.xml` (`weightIfPlayerHasXenotypeXenotype` Sanguophage, `makingFaction` Sanguophages)
is left alone because it fires only when the player has a Sith colonist, which S6 and S9 make impossible.

### 1.4 New defs (all `RSW_`)

`RSW_SithInquisitor` (PawnKindDef, §4) · `RSW_SithLair` (SitePartDef) · `RSW_GenStep_SithLair` (GenStepDef) ·
`RSW_SithLairRumour` (QuestScriptDef, §3) · `RSW_SithHolocron` (loot item: art, market value, no comps) ·
the C# (§2 guards, §3 tile picker and genstep, §4 group injector, settings).
**Owed edit to an existing file:** the `Sanguophage` block in
`src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` is rewritten to Sith wording in the Jawa
voice. If it is left as "Sanguophage", the campaign shows the old name over this mod.

## 2. Never recruitable

Vanilla's "unwaveringly loyal" is `Pawn_GuestTracker.Recruitable` (the backing field `recruitable`). When it
is false, the character card shows the loyal icon (`CharacterCardUtility`), and the prisoner modes marked
`hideIfNotRecruitable` (recruit, reduce resistance) are hidden in `ITab_Pawn_Visitor`. **On its own it isn't
permanent.** These routes measurably set it back or bypass it:
`PsychicRitualToil_Brainwipe` sets `Recruitable = true` (Anomaly);
`PawnGroupKindWorker_Normal` and `QuestPart_PawnJoinOffer` set it true; the getter returns true early for
`EverBeenColonistOrTameAnimal`; and Ideology's **enslave** (`GenGuest.EnslavePrisoner`) moves a prisoner
into the player faction without consulting `Recruitable` at all.

**The mechanism has four layers, all keyed on `pawn.genes?.Xenotype == XenotypeDefOf.Sanguophage`:**

1. **Set at birth:** a Harmony postfix on pawn generation sets `guest.Recruitable = false`, so the loyal icon
   shows from the first look.
2. **Make it permanent:** a postfix on the `Pawn_GuestTracker.Recruitable` getter forces `false`, which
   defeats brainwipe and every setter above.
3. **Close enslavement:** a prefix on `GenGuest.EnslavePrisoner` refuses with a message, and the enslave mode
   is hidden in the prisoner tab for these pawns.
4. **Last backstop:** a prefix on `RecruitUtility.Recruit` and on `Pawn.SetFaction` refuses any move of such
   a pawn into `Faction.OfPlayer`. Every join route ends in `SetFaction`, including quest joins and mods we
   haven't read.

Capture, imprisonment, execution, hemogen farming and gene extraction are not joining, so they stay allowed
(gene extraction: see OQ2). Ideoligion conversion changes a prisoner's ideo, not their faction, so it is
harmless.

## 3. Abyss lair site

**How it is found (recommended):** a rare rumour quest, `RSW_SithLairRumour`, built on the shape of vanilla
`OpportunitySite_ItemStash`. It runs `autoAccept`, uses `QuestNode_GetMap`, generates the site with
`Util_GenerateSite`, places it with `QuestNode_SpawnWorldObjects`, and sets a `QuestNode_WorldObjectTimeout`.
The text is a whisper of the Dark ("the sleeper below …"), reusing the cryptid's voice. Until the quest fires
there is no marker anywhere, which is what "hidden" means here. Vanilla `QuestNode_GetSiteTile` has **no
biome filter** (its fields are storeAs, preferCloserTiles, allowCaravans, canSelectSpace,
clampRangeBySiteParts, selectLandmarkChance, canSelectComboLandmarks), so it needs one small C# node:
`RSW_QuestNode_GetAbyssSiteTile`. That node picks a tile whose biome is `RM_Abyss` within PROVISIONAL 12
tiles of a player map. If none exists, `TestRun` fails and the quest never offers, which is also how it
degrades when the biomes mod is absent: a def lookup, never `MayRequire`. This route works on the frozen
world with no repaint dependency. The alternative is OQ5.

**Rarity (PROVISIONAL):** `rootSelectionWeight` 0.15 · `minRefireDays` 120 · `rootMinPoints` 400 · site
timeout 25–40 days · at most one open lair at a time.

**Layout:** `RSW_GenStep_SithLair` runs on the site map over the Abyss's own map generation. It carves one
sanctum of about 13×13, PROVISIONAL, into the nearest rock mass, with a single ancient door and dark floor
(`RM_EtchHollow` if present, otherwise vanilla dark stone).

- In the centre is a **Sith sarcophagus** with the lone Sith **in dark trance** inside it. The genstep starts
  the vanilla `Deathrest` job on the casket, with no new mechanic.
- Two to four bound buildings from §1.2 #25–29 stand around it, linked as vanilla deathrest buildings are,
  so the Sith gets their real bonuses when they rise.
- A loot shelf stands against the back wall.
- **Waking:** the trance breaks when the Sith takes damage, a colonist enters the sanctum, or a PROVISIONAL
  6–10 h passes after arrival. Breaking it early applies vanilla `InterruptedDeathrest` ("broken trance"),
  so sneaking in to strike first has a built-in payoff.
- The Sith's faction is a fresh hidden `Sanguophages` faction, generated the way vanilla
  `QuestNode_Root_SanguophageShip` does it (`FactionGenerator.NewGeneratedFactionWithRelations`). Their lord
  defends the sanctum.

**Loot (PROVISIONAL, scaled by points through a ThingSetMaker):**

- 1 `RSW_SithHolocron`, market value about 1500.
- A lightsaber with a red crystal (`guy762_SWForceLightsabers_CrystalPart_red`, MayRequire).
- `guy762_SithHood_masked`.
- 2–5 essence vials and 0–1 trance serum. They are worthless to the player except to sell, or to an Anzati
  (OQ1).
- Gold, silver and psychic apparel to the points value.

Deconstructing the buildings yields resources. They can't be minified (S8).

**Not built:** the lair has no thralls (the owner said "a lone Sith"), so it adds no new creatures.

## 4. Empire inclusion

**PawnKindDef `RSW_SithInquisitor`**, all values PROVISIONAL:

| Field | Value |
|---|---|
| `defaultFactionDef` | `Empire` |
| race | Human |
| `xenotypeSet` | `Sanguophage` 1, with `useFactionXenotypes` false |
| `combatPower` | 150 (the xenotype's `combatPowerFactor` 2.5 also applies, so measure the effective figure live) |
| name makers | `guy762_NamerPawnKind_MaleInquisitor` / `_FemaleInquisitor`, which give names like "Fifth Brother" / "Seventh Sister" |
| apparel | `guy762_SithHood_masked` plus black armour tags |
| weapon | `Force_Lightsaber_Inquisitor` (MayRequire on its `<li>`; defining mod to be measured) |
| label | "inquisitor" |

**How they enter groups:** not through `pawnGroupMakers` options. The campaign's `GalacticEmpire.xml`
**replaces** both Empire `Combat` option lists wholesale (`[commonality="100"]` and `[commonality="10"]`), so
an option added by this RSW-tier mod would be erased whenever the campaign loads after it. Use a Harmony
postfix on pawn-group generation instead (FOUNDRY reads the exact `PawnGroupMakerUtility` method in RimSage).
When the group's faction def is `Empire`, the postfix may append **at most one** inquisitor, by group kind:

| Group kind | Chance (PROVISIONAL) | Condition |
|---|---|---|
| `Combat` (raids) | 4% | points ≥ 1500 |
| `Settlement` (defenders when the player assaults an Empire base) | 25% | none |
| `Trader` (the Empire's only "visiting party" kind: it has no `Peaceful` group, so `IncidentWorker_NeutralGroup` visitors never come from it) | 5% | none |

🔴 **In the campaign the Empire is permanently hostile to the player.** `GalacticEmpire.xml` drops
`PlayerColony`/`PlayerTribe` from `permanentEnemyToEveryoneExcept`, so Empire traders and visitors **never
reach a Utinni colony**. The trader row works only in a non-campaign Star Wars game. See OQ3.

## 5. Mod Settings

Defaults reproduce the shipped behaviour. Turning everything off degrades to "vanilla sanguophage with the
vanilla routes closed", never to a broken state.

| Setting | Default | Notes |
|---|---|---|
| Sith reskin text (relabels + Keyed) | on | Off restores vanilla names. Only a restart applies it, which the label says. |
| Lair rumours enabled | on | |
| Lair rumour weight | 0.15 | |
| Lair refire days | 120 | |
| Lair search radius (tiles) | 12 | |
| Inquisitors in Empire raids · chance | on · 4% | |
| Raid minimum points | 1500 | |
| Inquisitors defending Empire settlements · chance | on · 25% | |
| Inquisitors with Empire caravans · chance | on · 5% | |
| Never recruitable (the §2 guard, all four layers) | on | |
| Block xenogerm absorb (S6b backstop) | on | |
| Block gene extraction from Sith | per OQ2 | |
| Vanilla sanguophage quests (S1/S2) stay off | on | Turning it off re-enables the weights, and with them the conversion offers, so the tooltip warns about that. |

Label as worldgen-affecting: none. Every setting is per-game runtime.

## 6. Tier, mod and canon check

- **Tier: RimStarWars.** "Sith" and "Inquisitor" are canon IP, so they go in the Star Wars layer, not `RM_`
  (CLAUDE.md "Star Wars style naming is NOT Star Wars IP", Q11a: canon names do route through the SW tier).
- **New mod** `src/RimStarWars/SithLine`, packageId `mandrake.rsw.sithline`, namespace
  `RimMandrake.StarWars.SithLine`, prefix `RSW_`.
  - Hard dependencies: Biotech, Royalty, Harmony, `mandrake.rsw.armoury` (namers, hood, crystal).
  - Soft dependency: `mandrake.rm.biomes`, for `RM_Abyss`. It is detected by def lookup in C#. Never use
    `MayRequire="mandrake.rm.abyss"`: that member id doesn't exist at runtime.
  - Load order: after Armoury. Its relabels don't depend on Utinni. The campaign's PawnFlavor edit (§1.4) is
    the only campaign-layer change.
- **Why not fold it into `mandrake.rsw.starwarsraces`:** this needs C#, a quest, a site and settings, and that
  mod is a def pack.
- **Canon check (Wookieepedia `list=search`, 2026-10-09):**
  - Found: Inquisitorius, Sith Inquisitor, Force drain, Sith alchemy, Sith holocron, the Sith Meditation
    Sphere (a ship; deliberately not used as a building name), Sith tombs (several canon tombs, which grounds
    "sarcophagus").
  - Invented in Star Wars style, so not IP claims: dark trance, essence, telekinetic shard, dark mending, rage
    font, trance obelisk, essence alembic.
  - ⚠️ The **xenotype label "Sith" collides** with the existing species xenotypes `RSW_RimMandrakeSithKissai` /
    `…Massassi` / `…SithZ` ("Red Sith"). See OQ4.

## 7. First functional script

`src/RimStarWars/SithLine/validation.py` (modcheck `Suite`) and walk
`design/validation_walks/RimStarWars/SithLine.md`. **`## must be true`** is below. Each line reads game state
back through the `t.*` verbs and their `success`/`foundCount` fields, never by substring. Every setting goes
in `suite.toggles`.

1. `XenotypeDef/Sanguophage` label is the Sith label, and the campaign's PawnFlavor didn't overwrite it →
   `defs.xenotype_label`
2. `XenotypeDef/Sanguophage` genes don't contain `XenogermReimplanter` → `defs.no_reimplanter`
3. `DeathrestCasket` and all 5 `DeathrestBuildingBase` children have no `designationCategory` and no
   `minifiedDef` → `defs.unbuildable`
4. `SanguophageMeetingHost` and `SanguophageShip` have `rootSelectionWeight` 0 → `defs.vanilla_quests_off`
5. `ScenarioDef/Sanguophage` has `showInUI` false → `defs.scenario_hidden`
6. A spawned Sith prisoner reads `Recruitable == false`, and still reads false after a dev toggle sets it
   true → `live.recruit_guard`
7. Enslave, `Recruit` and `SetFaction(player)` on a Sith prisoner all leave their faction unchanged →
   `UNCOVERED: needs a JawaBench [Tool] that calls these three and reports the faction after` (file as an item)
8. `GeneUtility.CanAbsorbXenogerm` is false for a downed Sith → `live.absorb_blocked`
9. Forcing `RSW_SithLairRumour` on a map with Abyss in range produces a site whose generated map holds 1
   sarcophagus, 1 Sith with the Deathrest hediff, at least 2 bound buildings and the loot shelf →
   `live.lair_gen`
10. With no Abyss tile in range, the rumour's `CanRun` is false → `live.lair_no_abyss`
11. An Empire raid at 2000 points with the chance forced to 1.0 contains exactly one `RSW_SithInquisitor` →
    `live.empire_inquisitor`
12. Each toggle off → its effect is gone → `suite.toggles`

**`## anti-guessing notes` (seeded):**

- RULED OUT: a top-level `<Operation MayRequire>` gating anything, because the engine ignores it. Guard: no
  such attribute in this mod's Patches.
- RULED OUT: `MayRequire="mandrake.rm.abyss"`, because Abyss is folded into `mandrake.rm.biomes`.
- RULED OUT: adding the inquisitor to Empire `Combat` options, because the campaign replaces them. Guard:
  bar 11 runs with UtinniPatches active.
- RULED OUT: `Recruitable = false` alone as permanence, because brainwipe and enslave bypass it.

## 8. Open questions (only what the owner must decide)

1. **The Anzati share the blood-and-trance machinery.** Renaming hemogen and deathrest to dark-side terms,
   and making the trance buildings unbuildable, also reaches Anzati colonists.
   (a) Accept it. "Essence" and "trance" read fine for the Anzati, but they lose the trance buildings.
   (b) Keep the buildings buildable for non-Sith pawns. That means a research-gated exception, and it bends
   "none of the buildings are buildable".
   (c) Give the Anzati their own copies of the genes. That's more defs, and the Anzati drift from the shared
   code.
2. **Gene extraction.** A captured Sith can have its non-archite genes extracted (life-drain, dark trance,
   dark-side reservoir) and implanted in a colonist. That gives you a blood-drinking, trancing colonist
   without them ever being Sith.
   (a) Block extraction from Sith. This is the purest reading of "cannot convert others".
   (b) Allow it. It's the player's own gene tech, a hard-won prize, and the colonist still isn't Sith.
3. **"Visiting parties" can't happen in the campaign.** The Empire is permanently hostile to the player, so
   its caravans never visit.
   (a) Sith appear only in raids and in Empire base defenders. Simple, and it fits the hostility.
   (b) Also add an occasional Empire "inspection" arrival that walks through and leaves. That's a new
   incident, so it's more work, and it makes the Empire a little less pure enemy.
   (c) Keep the caravan escort for non-campaign games only.
4. **The name "Sith" is already used** by the Red Sith species xenotypes (Kissai, Massassi, Sith Z).
   (a) Label the line "Sith", the way your ruling says it, and rename nothing else. The two read as
   "species" vs "order" only from their descriptions.
   (b) Label it "Sith adept" or "dark acolyte". That's clearer in the UI but less punchy.
5. **How a lair is found.**
   (a) A rare rumour quest marks a site, as recommended above. It works on the frozen world today, the
   player chooses whether to go, and it is rare and timed.
   (b) The BroodLair pattern: a rare hidden tile feature you stumble on when you land on that Abyss tile. It
   is more of a genuine surprise, but it has to be placed by hand at the final world-painting pass, and no
   lair exists until then.
