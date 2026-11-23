---
name: rimworld-scenario-building
description: Authoring a RimWorld scenario and the game-creation settings around it — ScenarioDefs, .rsc scenario files, ScenParts, Custom difficulty fields, storyteller, Anomaly playstyle, and planet/world settings — including which choices are permanent at world creation and which can be changed later. Use whenever a campaign start, scenario, custom difficulty, storyteller choice, world-generation setting or "how do we make the game start like X" comes up; before authoring any ScenarioDef or scenario file; and before anyone generates a world they intend to keep.
---

# RimWorld scenario building

A RimWorld scenario is smaller than people expect. The settings around the scenario are larger. Most of what makes a
campaign feel authored is in **game-creation settings that are not part of the scenario**. Nobody can change some of
those settings after the game starts.

Corrected lines and their evidence: `references/history.md`.

## What RimMandrake ships: one saved game

- RimMandrake players generate no world. Each player gets a saved game with one fixed, hand-made world.
- Bucket B holds the settings that the game fixes at world creation. So bucket B binds the person who makes that saved
  game. The choices of that person go to every player.
- Do not build worldgen, and do not offer worldgen to players. Rule: `design/RimMandrake/standing_rulings.md` §There is
  no worldgen feature, in any version.
- The settings that our campaign start needs are in `design/Jawa/worldbuilding/SCENARIO_SETTINGS_SPEC.md`.

## 🔴 The question that governs everything: WHEN is this fixed?

Before you touch a setting, put the setting in one of three buckets. **A wrong bucket is the expensive error**, because
bucket B has no undo.

| bucket | when it is decided | cost of being wrong |
|---|---|---|
| **A · Authored in files** | any time; reload to apply | cheap. Edit and retry |
| **B · 🔴 Clicked at WORLD CREATION** | once, permanently | **a new campaign.** There is no patch |
| **C · Changeable in an existing save** | any time | near zero |

**Write the bucket next to every setting in your spec.** A reader who cannot tell A from B will plan to "fix it later".
In bucket B, nobody can fix the setting later.

**How to tell B from C when you are unsure:**

- Find the UI that writes the field. Check in which game state that UI shows the control.
- If the code draws the control inside a `ProgramState.Entry` guard, the control does not exist in an existing save.
- That guard is the reason that the Anomaly playstyle is permanent.

## The three homes for a scenario

| home | what it is | when to use it |
|---|---|---|
| **`ScenarioDef`** in a mod | XML that ships with a mod; it appears in the scenario list | a scenario that you want to *distribute*, or that must load before a save exists |
| **`.rsc` file**: a saved scenario | `<savedscenario>` with `<meta>` (it holds `gameVersion` and `modIds`), then the scenario body; it is in the game's user folder under `Scenarios/` | to write a scenario by hand, or to export one from the in-game editor. Same content as a `ScenarioDef`, not attached to a mod |
| **🔴 A saved GAME** | the start, already played to the point that you want | **when the start needs anything that a ScenPart cannot express** |

⚠️ **The `.rsc` `<meta><modIds>` block records the entire mod list at authoring time.**

- The block is a compatibility stamp, not a dependency. Because of that stamp, a scenario from one mod list looks
  alarming on another.
- A part whose def is missing is a real loss. The game removes that part and marks the scenario invalid.

### 🔴 The hard limit that pushes campaigns to a saved game

**No ScenPart can force specific NAMED pawns with chosen backstories, traits, skills and relationships.**

- `ConfigPage_ConfigureStartingPawns` opens the *chooser*.
- `HAR_StartingHumanlikes` (a part from the Humanoid Alien Races mod) sets a count.
- `ConfigurePawnsXenotypes` and `ConfigurePawnsKindDefs` constrain *what kind* of pawn.
- None of those parts says "this person, called this, who knows that one."

**If your campaign has authored founders, the start ships as a SAVE.** Accept that early. The late way to learn it is
after you wrote a `ScenarioDef`. You can still write a scenario beside the save, for the parts that a scenario can
carry. The save is the product.

## What ScenParts can actually do

Read the live list before you design. Mods add their own parts, so the vanilla set is smaller than the modded set. List
`ScenPartDef` from a def dump, and group the defs by their `category` field. A heavily modded 1.6 list holds many
more parts than this table.

| category | what is there | notes |
|---|---|---|
| **Fixed** | `PlayerFaction`, `PlayerPawnsArriveMethod`, `ConfigPage_ConfigureStartingPawns`, `ConfigurePawnsXenotypes`, `ConfigurePawnsKindDefs`, `ForcedMap`, `PlanetLayerFixed` | the skeleton. Most scenarios differ only here |
| **StartingImportant** | `StartingAnimal`, `StartingMech`, `StartingResearch`; from mods: `HAR_StartingHumanlikes`, `StartingVehicle` | counts and kinds, never identities |
| **StartingItem** | `StartingThing_Defined`, `ScatterThingsNearPlayerStart` | ⭐ starting gear. These two parts do nearly all of it |
| **Rule** | `DisableIncident`, `DisableQuest`, `CreateIncident`, `CreateQuest`, `StatFactor`, `Rule_DisallowBuilding`, the `Rule_DisallowDesignator_*` family | ⭐ the parts that shape a campaign. To remove an option is often stronger design than to add one |
| **PlayerPawnModifier** | `ForcedTrait`, `ForcedHediff`, `SetNeedLevel`, `Naked` | a part cannot single a pawn out |
| **GameCondition** | `PermanentGameCondition`, `GameCondition_Planetkiller` | ⭐ a permanent condition is the cheapest way to make a world feel wrong |
| **Misc** | `GameStartDialog`, and parts for faction goodwill and starting structures | `GameStartDialog` gives you the whole opening narration for free |
| **WorldThing / PlayerPawnFilter** | `ScatterThingsAnywhere`, `PawnFilter_Age` | rare, useful when you need them |

**Reasons to use these parts, and reasons not to use them:**

- ⭐ **`StatFactor` is the most abusable part in the list.** The part puts one multiplier on a stat for every thing that
  has the stat. Use the part for a *planetary* fact. Do not use the part to balance a single item, because nobody will
  find the change again.
- ⭐ **`PermanentGameCondition` sells a setting in one line.** Before you ship a condition, check what it does to *light,
  temperature and plant growth*. The interesting conditions are interesting because they punish the player.
- **`DisableIncident` / `DisableQuest` beat cutting content.** Each part stops the natural draw, and the def stays
  loaded. Prefer them to deletion when you want "present but dormant". Each part has its own way back in:
  - An incident that `DisableIncident` names still fires if the caller sets `forced` or `bypassStorytellerSettings` on
    the `IncidentParms`. `QuestNode_Incident` sets `forced`.
  - A quest that `DisableQuest` names fails each `QuestScriptDef.CanRun` check. So a give-quest incident for that quest
    does not pass `CanFireNow`, also when the incident is forced. A caller that makes the quest without `CanRun` still
    starts the quest, for example `QuestPart_AddQuest` and `ScenPart_CreateQuest`.
- ⚠️ **`ForcedTrait` and `SetNeedLevel` hit every starting pawn** when `chance` is 1 and `context` is `All` or
  `PlayerStarter`.
  - `chance` makes a random choice for each pawn. `context` limits the part to starters or to other pawns. Neither
    field names a pawn.
  - For a cast with distinct personalities, these parts are too blunt. Their bluntness is one more reason for a saved game.

## Difficulty: use Custom, and know which fields matter

`DifficultyDef` ships the defNames `Peaceful · Easy · Medium · Rough · Hard · Extreme · Custom`.

- **Custom (`isCustom: true`) is not "cheating".** Custom is the only preset whose individual fields the player can
  set. Some important sliders are adjustable *only* on Custom.
- ⚠️ **If any campaign ruling depends on a numeric threat or yield setting, the campaign requires Custom difficulty.**
  Write that in the spec. A player who picks `Rough` loses the ruling with no message.
- When the player picks another preset, the game overwrites the Custom values with the values of that preset. When the
  player picks Custom again, Custom starts from the values of `Rough`. Neither act changes the Anomaly playstyle or
  `overrideAnomalyThreatsFraction`.

Fields that you need to know. Each one is on `DifficultyDef`, except where the row says otherwise:

| field | what it is for |
|---|---|
| `threatScale` · `allowBigThreats` · `allowIntroThreats` | the main raid dial and its coarse switches |
| `overrideAnomalyThreatsFraction` | ⭐ the one Anomaly threat slider of the `AmbientHorror` playstyle. **This is where "0% anomaly threats" actually is.** The field is on the runtime `Difficulty` object only, never on a def |
| `anomalyThreatsActiveFraction` · `anomalyThreatsInactiveFraction` | the pair of Anomaly threat sliders of the `Standard` playstyle. Under `AmbientHorror`, the override decides while it has a value |
| `adaptationEffectFactor` · `adaptationGrowthRateFactorOverZero` | how much the storyteller adapts to a colony that does well, and how fast that adaptation grows |
| `cropYieldFactor` · `mineYieldFactor` · `butcherYieldFactor` · `fishingYieldFactor` | economy controls. Prefer these fields to def edits |
| `fixedWealthMode` | ⭐ threat follows the age of the home map, not its wealth. Strong for a nomadic campaign that must not be punished for a full hold. The age counts from the generation of that map, so each new landing map starts low |
| `childAgingRate` · `adultAgingRate` · `noBabiesOrChildren` · `babiesAreHealthy` | ⚠️ set these deliberately if the campaign has a reproduction fiction |
| `manhunterChanceOnDamageFactor` | animal hostility: the chance that a hurt animal attacks |
| `scariaRotChance` | the chance that a corpse with scaria rots at once, so the player gets no meat from it |
| `allowTurrets` · `allowMortars` · `allowTraps` | to remove a defensive option is a strong design statement that the player can read |
| `unwaveringPrisoners` · `lowPopConversionBoost` | prisoner and conversion economy |

## Storyteller

Choose a `StorytellerDef` for the *shape* of its events, not for difficulty:

- **Cassandra** escalates on a curve. Good for a base that must grow.
- **Phoebe** gives long calm times. Good for play that is mostly building.
- **Randy** has no curve. ⭐ The right pick for a campaign about *reacting* (nomadic, escape, expedition). There, a
  difficulty curve that the player can read would fight the fiction.

The storyteller is in bucket **C**: the player can change the storyteller later. The difficulty *preset* is also in
bucket C. **The settings that nobody can change later are the world settings below.**

## 🔴 Anomaly playstyle: three defs, and the choice is permanent

`AnomalyPlaystyleDef` has exactly three defs:

| defName | `generateMonolith` | `enableAnomalyContent` | what it means |
|---|---|---|---|
| `Standard` | true | true | the monolith spawns; anomaly content runs normally |
| ⭐ **`AmbientHorror`** | **false** | **true** | **no monolith. ALL content stays live**: study, anomaly research, entity codex, tome trading. Anomaly threats still fire by chance, 0.15 by default, until the slider is at 0 |
| `Disabled` | false | **false** | ⚠️ kills study, research and codex too. **Art only** |

⭐ **`AmbientHorror` with `overrideAnomalyThreatsFraction` at 0 is "present but dormant"** for threats.

- People mean this setting when they want Anomaly's *content* without its *interruptions*.
- The slider controls only the categories `ThreatSmall` and `ThreatBig`. At 0, the storyteller draws no Anomaly incident
  of those two categories.
- ⚠️ The slider does not control the categories `Misc` and `GiveQuest`. So the storyteller still draws Anomaly incidents
  such as `CreepJoinerJoin`, `MetalhorrorImplantation`, `MysteriousCargoCube` and `GiveQuest_DistressCall`. To stop such
  an incident, add one `DisableIncident` part for each. Worked example:
  `src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`.
- The weather `GrayPall` ignores the slider. Under `AmbientHorror`, `GrayPall` can occur in each biome that lists
  `GrayPall` in its weather odds.
- `generateMonolith` is false, so the game does not apply the `minAnomalyThreatLevel` gate. So a quest or dev mode can
  still fire individual anomaly incidents deliberately.

🔴 **Bucket B.**

- The game draws the "Anomaly settings…" button only at the entry screen. So the player cannot change the playstyle
  in an existing save.
- The "Anomaly settings…" window shows the threat slider with each difficulty preset. To change a threat slider
  *later*, the game must be on Custom difficulty.
- Under `Standard`, the in-game slider for `anomalyThreatsActiveFraction` stops at 0.1.

⚠️ **`Scenario.standardAnomalyPlaystyleOnly` greys out everything but `Standard`.** If your scenario sets this field,
the player cannot choose `AmbientHorror`. Let only the DLC's own scenario set it.

⚠️ **Do not confuse the playstyle defNames with the slider's translation keys.** The `AnomalyFrequency_*` strings are
the labels that the slider shows for its value. Those strings are not playstyles. A check against those strings fails on a
correct setup.

## World creation: the bucket B list

The person who starts the game chooses these settings once, before world generation. The game keeps them forever:

- **Planet coverage, rainfall, temperature and population**: the global dials.
- **The planet type**, if a mod adds one. The mod Alien Worlds Framework adds `PlanetTypeDef`.
  - Without the Worldbuilder mod, the control is in Mod settings → Alien Worlds Framework, not on the world page.
  - Its fields include `avgTempByLatitudeCurve`, `rainfallCurves`, `elevationRange` (the share of ocean and mountain),
    `biomes` / `biomeBlacklist`, per-biome `biomeConfigs` with `scoreOffset`, and `sunlightFactor`.
  - A planet type sets where each climate and biome zone generates. Set the planet type that
    `SCENARIO_SETTINGS_SPEC.md` names (its row "Planet type"). The planet type does not replace the hand work on our one map.
- 🔴 **Which factions exist, and how many of each.** **A faction absent at world creation can NEVER be added later.**
  A def edit afterwards does not put back a faction that you unticked.
  - Four factions are an exception: `HoraxCult`, `Entities`, `TradersGuild` and `Salvagers`. If one is absent and its DLC
    is active, the game adds the faction at load. So do not plan a world without those four.
- **Permadeath**, and the Anomaly playstyle.

⚠️ **Screenshot each world-creation page before you leave it, the faction page most of all.** Include the Mod settings
page of the planet type. The save does not record
population or landmark density. The save can hold the faction list, but one observed save held none. To rebuild the
choices from a save later is far harder than to press the key.

## Traps

- 🔴 **"We can fix that later" is false for bucket B**, and bucket B is bigger than it looks: factions, planet type,
  Anomaly playstyle, permadeath.
- 🔴 **A ScenPart cannot name a pawn.** Every campaign with authored characters learns this in the end. Learn it before
  you write the `ScenarioDef`.
- **Mods add ScenParts.** The vanilla list is not the list. List the parts from the live def dump, not from memory or
  the wiki.
- ⚠️ **A def dump is post-load, not the authored XML.** The dump shows what the game resolved after every patch ran. The
  dump is what you want for "what will actually happen" and not what you want for "what does our mod say".
- **Prefer `DisableIncident` to the removal of content.** The choice is reversible, and authored events can still reach
  the content.
- **Custom difficulty is a REQUIREMENT, not a preference**, as soon as any ruling names a slider value. Write that in
  the spec.
