---
name: rimworld-scenario-building
description: Authoring a RimWorld scenario and the game-creation settings around it — ScenarioDefs, .rsc scenario files, ScenParts, Custom difficulty fields, storyteller, Anomaly playstyle, and planet/world settings — including which choices are permanent at world creation and which can be changed later. Use whenever a campaign start, scenario, custom difficulty, storyteller choice, world-generation setting or "how do we make the game start like X" comes up; before authoring any ScenarioDef or scenario file; and before anyone generates a world they intend to keep.
---

# RimWorld scenario building

A "scenario" in RimWorld is smaller than people expect and the settings around it
are larger. Most of what makes a campaign feel authored lives in **game-creation
settings that are not part of the scenario at all** — and several of them can
never be changed again.

## 🔴 The question that governs everything: WHEN is this fixed?

Before touching any setting, put it in one of three buckets. **Getting this wrong
is the expensive error**, because bucket B has no undo.

| bucket | when it is decided | cost of being wrong |
|---|---|---|
| **A · Authored in files** | any time; reload to apply | cheap. Edit and retry |
| **B · 🔴 Clicked at WORLD CREATION** | once, permanently | **a new campaign.** There is no patch |
| **C · Changeable in an existing save** | any time | near zero |

**Write the bucket next to every setting in your spec.** A reader who cannot tell
A from B will happily plan to "fix it later" on something that cannot be fixed.

**How to tell B from C when you are unsure:** find the UI that writes the field
and check what game state it renders in. If the button is drawn inside a
`ProgramState.Entry` guard, it is not available in an existing save — that is
exactly how the Anomaly playstyle turns out to be permanent.

## The three homes for a scenario

| home | what it is | when to use it |
|---|---|---|
| **`ScenarioDef`** in a mod | XML shipped with a mod; appears in the scenario list | a scenario you want to *distribute*, or that must load before a save exists |
| **`.rsc` file** — a saved scenario | `<savedscenario>` with `<meta>` (gameVersion, modIds) then the scenario body; lives in the game's user folder under `Scenarios/` | authoring by hand or exporting from the in-game editor. Same content as a ScenarioDef, not attached to a mod |
| **🔴 A saved GAME** | the start already played to the point you want | **when the start needs anything a ScenPart cannot express** |

⚠️ **The `.rsc` `<meta><modIds>` block records the entire mod list at authoring
time.** It is a compatibility stamp, not a dependency — but it is why a scenario
authored on one stack looks alarming on another.

### 🔴 The hard limit that pushes campaigns to a saved game

**No ScenPart can force specific NAMED pawns with chosen backstories, traits,
skills and relationships.** `ConfigPage_ConfigureStartingPawns` opens the
*chooser*; `StartingHumanlikes` sets a count; `ConfigurePawnsXenotypes` and
`ConfigurePawnsKindDefs` constrain *what kind*. None of them says "this person,
called this, who knows that one."

⇒ **If your campaign has authored founders, the start ships as a SAVE.** Accept it
early rather than discovering it after writing a ScenarioDef. A scenario can still
be authored alongside for the parts it *can* carry, but the save is the artifact.

## What ScenParts can actually do

Read the live list before designing — mods add their own, and the vanilla set is
smaller than the modded set. Enumerate `ScenPartDef` from a def dump and group by
its `category` field. On one heavily modded 1.6 stack: **72 ScenPartDefs** across
ten categories.

| category | what lives there | notes |
|---|---|---|
| **Fixed** | `PlayerFaction`, `PlayerPawnsArriveMethod`, `ConfigPage_ConfigureStartingPawns`, `ConfigurePawnsXenotypes`, `ForcedMap`, `PlanetLayerFixed` | the skeleton. Most scenarios differ only here |
| **StartingImportant** | `StartingHumanlikes`, `StartingAnimal`, `StartingMech`, `StartingResearch`, `StartingVehicle` | counts and kinds, never identities |
| **StartingItem** | `StartingThing_Defined`, `ScatterThingsNearPlayerStart` | ⭐ where starting gear is expressed. Two parts do nearly all of it |
| **Rule** | `DisableIncident`, `DisableQuest`, `CreateIncident`, `CreateQuest`, `StatFactor`, `Rule_DisallowBuilding`, the `Rule_DisallowDesignator_*` family | ⭐ the campaign-shaping ones. Removing an option is often stronger design than adding one |
| **PlayerPawnModifier** | `ForcedTrait`, `ForcedHediff`, `SetNeedLevel`, `Naked` | applies to everyone; cannot single a pawn out |
| **GameCondition** | `PermanentGameCondition`, `GameCondition_Planetkiller` | ⭐ a permanent condition is the cheapest way to make a world feel wrong |
| **Misc** | `GameStartDialog`, faction-goodwill and starting-structure parts | `GameStartDialog` is the whole opening narration, for free |
| **WorldThing / PlayerPawnFilter** | `ScatterThingsAnywhere`, `PawnFilter_Age` | rare, useful when you need them |

**Reasons to reach for these, and reasons not to:**

- ⭐ **`StatFactor` is the most abusable part in the list.** It is the right tool
  for a *planetary* fact — one multiplier applied to everything — and the wrong
  tool for balancing a single item, because nobody will ever find it again.
- ⭐ **`PermanentGameCondition` sells a setting in one line.** But check what the
  condition does to *light, temperature and plant growth* before shipping it; the
  interesting ones are interesting because they are punishing.
- **`DisableIncident` / `DisableQuest` beat cutting content.** They leave the defs
  loadable — so a quest can still fire one deliberately — while stopping the
  storyteller drawing them. Prefer them to deletion whenever "present but
  dormant" is what you actually want.
- ⚠️ **`ForcedTrait` and `SetNeedLevel` hit every starting pawn.** For a cast with
  distinct personalities they are a blunt instrument; that is another push toward
  a saved game.

## Difficulty — use Custom, and know which fields matter

`DifficultyDef` ships `Peaceful · Easy · Medium · Rough · Hard · Extreme ·
Custom`. **Custom (`isCustom: true`) is not "cheating"** — it is the only preset
whose individual fields the player can set, and several important sliders are
*only* adjustable on it.

⚠️ **If any campaign ruling depends on a numeric threat or yield setting, the
campaign requires Custom difficulty.** Say so explicitly in the spec, because a
player who picks Rough silently loses the ruling.

Fields worth knowing, all real on `DifficultyDef`:

| field | what it is for |
|---|---|
| `threatScale` · `allowBigThreats` · `allowIntroThreats` | the main raid dial and its coarse switches |
| `anomalyThreatsActiveFraction` · `anomalyThreatsInactiveFraction` | ⭐ the Anomaly threat sliders. **This is where "0% anomaly threats" actually lives** |
| `adaptationEffectFactor` · `adaptationGrowthRateFactorOverZero` | how hard the storyteller learns from your wins |
| `cropYieldFactor` · `mineYieldFactor` · `butcherYieldFactor` · `fishingYieldFactor` | economy taps. Prefer these to editing defs |
| `fixedWealthMode` | decouples threat from wealth. Powerful for a nomadic campaign that should not be punished for a full hold |
| `childAgingRate` · `adultAgingRate` · `noBabiesOrChildren` · `babiesAreHealthy` | ⚠️ set deliberately if the campaign has a reproduction fiction |
| `scariaRotChance` · `manhunterChanceOnDamageFactor` | animal hostility |
| `allowTurrets` · `allowMortars` · `allowTraps` | removing a defensive option is a strong, legible design statement |
| `unwaveringPrisoners` · `lowPopConversionBoost` | prisoner and conversion economy |

## Storyteller

`StorytellerDef` — the choice is about *shape*, not difficulty:

- **Cassandra** escalates on a curve. Good for a base that is meant to grow.
- **Phoebe** gives long calm stretches. Good for building-heavy play.
- **Randy** is uncurated. ⭐ The right pick for a campaign about *reacting* —
  nomadic, escape, expedition — where a legible difficulty curve would fight the
  fiction.

Storyteller is bucket **C** — changeable later. Difficulty *preset* is too. **The
things that are not changeable are the world settings below.**

## 🔴 Anomaly playstyle — three defs, and the choice is permanent

`AnomalyPlaystyleDef` has exactly three defs:

| defName | `generateMonolith` | `enableAnomalyContent` | what it means |
|---|---|---|---|
| `Standard` | true | true | the monolith spawns; anomaly content runs normally |
| ⭐ **`AmbientHorror`** | **false** | **true** | **no monolith, nothing auto-spawns — but ALL content stays live**: study, anomaly research, entity codex, tome trading |
| `Disabled` | false | **false** | ⚠️ kills study, research and codex too. **Art only** |

⇒ ⭐ **`AmbientHorror` with the threat fractions at 0 is "present but dormant".**
It is the setting people mean when they say they want Anomaly's *content* without
its *interruptions* — and because `generateMonolith` is false, the
`minAnomalyThreatLevel` gating is bypassed, so individual anomaly incidents can
still be fired deliberately by a quest or by dev mode.

🔴 **Bucket B.** The "Anomaly settings…" button renders only at the entry screen,
so the playstyle cannot be changed in an existing save. The threat *sliders* stay
adjustable — but only on Custom difficulty.

⚠️ **`Scenario.standardAnomalyPlaystyleOnly` greys out everything but `Standard`.**
If your scenario sets it, the player cannot choose `AmbientHorror`. Only the DLC's
own scenario should set it.

⚠️ **Do not confuse the playstyle defNames with the slider's translation keys.**
`AnomalyFrequency_*` strings are UI labels for the frequency dropdown, not
playstyles. A check written against them will fail on a correct setup — a real
bug, found in a real state file.

## World creation — the bucket B list

These are chosen once, on the world screen, and kept forever:

- **Planet coverage, rainfall, temperature and population** — the global dials.
- **The planet type**, if a mod adds one. Planet-type mods can expose
  `avgTempByLatitudeCurve`, `rainfallCurves`, `elevationRange` (the ocean/mountain
  share), `biomes` / `biomeBlacklist`, per-biome `biomeConfigs` with
  `scoreOffset`, and `sunlightFactor`. ⭐ **Most "we must hand-build this world"
  problems are really zonation problems, and a PlanetTypeDef does zonation
  better than a person can.**
- 🔴 **Which factions exist, and how many of each.** **A faction absent at world
  creation can NEVER be added later.** Unticking is not reversible by editing a
  def afterwards.
- **Permadeath**, and the Anomaly playstyle above.

⚠️ **Screenshot the faction configuration page before leaving it.** It is the only
record of what was chosen, and reconstructing it later from a save is far harder
than pressing the key.

## Traps

- 🔴 **"We can fix that later" is false for bucket B**, and bucket B is bigger than
  it looks. Factions, planet type, Anomaly playstyle, permadeath.
- 🔴 **A ScenPart cannot name a pawn.** Every campaign with authored characters
  eventually learns this; learn it before writing the ScenarioDef.
- **Mods add ScenParts.** The vanilla list is not the list. Enumerate from the
  live def dump, not from memory or the wiki.
- ⚠️ **A def dump is post-load, not the authored XML.** It shows what the game
  resolved after every patch ran, which is what you want for "what will actually
  happen" and not what you want for "what does our mod say".
- **Prefer `DisableIncident` to removing content.** Reversible, and it leaves the
  content reachable for authored use.
- **Custom difficulty is a REQUIREMENT, not a preference**, the moment any ruling
  names a slider value. Write it in the spec.
