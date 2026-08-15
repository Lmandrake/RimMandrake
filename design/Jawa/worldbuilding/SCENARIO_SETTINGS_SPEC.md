# SCENARIO_SETTINGS_SPEC.md — every setting the campaign start needs, and WHEN it is fixed

DECIDE owns this file. **BUILD owns bucket A. The OWNER owns bucket B.** Chain
step 12, beside `SCENARIO_SPEC.md`.

`SCENARIO_SPEC.md` R25 settled *what the start contains* and ruled that it ships
as a **SAVED GAME**, because no `ScenPart` can force named pawns. This file rules
**how the game is CREATED around it** — the screens before the save exists, which
had no document. Factions are `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`
and are ratified; nothing here repeats them.

Everything below was read off the live 576-mod def dump
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\`,
captured 2026-08-15T15:10Z), the game's own XML under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\`, or the running
game's `Player.log`. No defName or field name in this document was guessed.

---

## 🔴 R-S0 · The organising principle: three buckets, and one has no undo

**Every setting in this document carries a bucket letter. Carry the letter into
any plan, item or checklist that quotes it.**

| bucket | when it is decided | cost of getting it wrong |
|---|---|---|
| **A · authored as FILES** | any time; a reload applies it | cheap. Edit and reload |
| 🔴 **B · CLICKED AT WORLD CREATION** | once, permanently | **a new campaign**, plus the ~25–30 min cold load to reach the screen again |
| **C · changeable in an existing save** | any time | near zero. Note it and move on |

**How B is told from C, and it is evidence, not taste.** Find the UI that writes
the field and check the game state it renders in. A control drawn inside a
`Current.ProgramState == ProgramState.Entry` guard does not exist once a game
does. Everything placed in B below carries its evidence in the table.

⚠️ **B is bigger than it looks**, and four of its five members have been called
"tune it later" somewhere in this repo: factions, planet type, the world sliders,
the Anomaly playstyle, permadeath.

---

## 🔴 R-S1 · BLOCKER — the planet type is NOT SELECTED, and there is no button for it on the world page

**Measured 2026-08-15. This is the most expensive latent failure in the campaign,
because it fails silently and produces a world that looks fine.**

**The Alien Worlds Framework has two backends.** With `ferny.Worldbuilder`
active, the planet type appears as a world preset **on the world-generation
page**. Without it the framework falls back to `Standalone`, and the selector is a
radio list **in the mod's own settings window** — the framework's `About.xml`
says so, and its DLL carries the literal string `Planet type for new worlds:`.

🔴 **`ferny.Worldbuilder` is NOT in `<activeMods>`.** So the backend is
`Standalone` and **there is no planet-type control on the world-generation
page at all.**

🔴 **And the setting has never been touched.** `AlienWorldsSettings` scribes
`selectedPlanetType` with the default `"Default"`, and **no
`Mod_3626210061_*.xml` exists** anywhere in
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\`
(all 85 entries listed; zero matches for `3626210061`, `3631364335` or
`alienworld`).

⇒ **A world generated on this install today would be the ordinary vanilla
planet.** No tidal lock, no `avgTempByLatitudeCurve`, no `biomeBlacklist` — every
temperature and biome ruling in this repo silently absent, on a world that
generates without one error line.

**The fix, in the order of preference:**

1. **The owner opens Options → Mod settings → Alien Worlds Framework, selects
   *tidally locked world*, and screenshots it.** Then confirms it survived by
   reopening the page. This is the route that cannot be wrong about a filename.
2. BUILD may pre-write `Mod_3626210061_AlienWorldsSettings.xml` with
   `<selectedPlanetType>TidallyLocked</selectedPlanetType>` — ⚠️ **the filename is
   derived, not observed** (`Mod_<folderName>_<settingsClassName>.xml`), so it is
   only valid once the settings page reads it back as selected. **Never treat the
   written file as the proof.**
3. Activating `ferny.Worldbuilder` would move the selector onto the world page —
   a mod-list change, and therefore `rimworld-start-prep`'s problem, not a fix to
   make on the night.

⭐ **Once a world exists it carries its own planet type**, scribed as
`alienWorldsFrameworkPlanetType` on `World.ExposeData`. The mod setting is
labelled *"for new worlds"* and changing it later does not touch an existing save.

⚠️ **What is baked vs. what still responds to a def edit.** Biome assignment and
tile temperatures are computed once, in `WorldGenStep_Terrain.GenerateTileFor` —
so `biomeBlacklist`, `biomeConfigs` and `avgTempByLatitudeCurve` are **worldgen
only**. `sunlightFactor`, `steamGeyserFactor`, `permaIceScoreOffset`,
`rainfallCurves` and `elevationRange` are applied by live Harmony field-patching
while the type is active, so **those five still respond to a def edit and a
reload** after the world exists.

## 🔴 R-S1b · BLOCKER — the biome mix is DEAD IN THE LIVE GAME, and worldgen reads it once

**Measured 2026-08-15 in `Player.log` at the 11:03 load, lines 1052–1079.** Like
R-S1 this is bucket A work with a bucket B deadline, which is why both lead the
document.

`src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml` writes `biomeConfigs` in
the dictionary-keyed shorthand:

```xml
<biomeConfigs>
  <Desert><scoreOffset>12</scoreOffset></Desert>
</biomeConfigs>
```

**The engine rejects every one of the 24 entries**, once per entry:

```
XML format error: List item found with name Desert that is not <li>,
and which does not have a custom XML loader method, in <biomeConfigs>…
```

⇒ The live def reads `biomeConfigs: []` while `biomeBlacklist` holds all 29
entries. **The blacklist works. The abundance and rarity offsets do nothing.**

**Why the shorthand is wrong here, stated so it is not re-learned.** The field is
`public Dictionary<string, BiomeConfig> biomeConfigs`
(`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3626210061\Source\PlanetTypeDef.cs`).
A plain `Dictionary<K,V>` has **no** `LoadDataFromXmlCustom`, so RimWorld needs
the `<li><key>/<value>` shape. The element-name-as-key shorthand works only where
a custom loader exists — `xenotypeChances` is the famous one, and **B56 is the
exact mirror-image mistake**: there the `<li>` shape was wrong, here the keyed
shape is. *One trap, two directions. Read the field's declared type; do not
pattern-match off another def.*

**The correct shape**, verified against a shipped vanilla dictionary
(`AnimationDef.keyframeParts`, `…\Data\Anomaly\Defs\AnimationDefs\DeathRefusal.xml:11`):

```xml
<biomeConfigs>
  <li>
    <key>Desert</key>
    <value><scoreOffset>12</scoreOffset></value>
  </li>
</biomeConfigs>
```

⭐ **`scoreOffset` does NOT require the biome to be listed in `<biomes>`.** The
offset is applied in `PlanetTypeManager.GetBiomeScorePostfix` (`:122-124`), which
only tests `biomeConfigs.ContainsKey`. The `<biomes>` membership check at
`PlanetTypeDef.cs:189-191` guards `HandleActivationFor` only — `defFields`,
`texture` and `workerClass`. **So keeping `<biomes>` empty is still correct**
(the whitelist trap in `WORLDGEN_RUN.md` §5 stands); expect up to 24 harmless
`<biomeConfigs> contains key X, which isn't present in <biomes>. Skipping.`
warnings after the fix, and do **not** "fix" them by populating `<biomes>`.

🔴 **Biome scoring runs once, in `WorldGenStep_Terrain`. A patch that misses the
worldgen click never touches that world.** Chain step 8 is recorded as done and
ratified; on this evidence its scoring half has never run.

⚠️ **Also seen at `Player.log:1080`:** `[Def Error]: TidallyLocked … Parsed 0.3 as
int.` Unexplained, not obviously ours, low priority — but look at it in the same
pass, because it is on the def the whole temperature design rests on.

---

# Bucket A — what BUILD authors as FILES

## R-S2 · What a `ScenarioDef` still buys us — and it is very little

**The ruling: do NOT author a `ScenarioDef` for v1.** Author the parts we want
**into the save's own embedded scenario** instead.

**Why.** The scenario is serialised into the `.rws` in full — `<savegame><game><scenario>`,
with `<name>`, `<summary>`, `<description>`, `<playerFaction>`, `<surfaceLayer>`
and every `<li Class="ScenPart_X">` expanded. **The save does not reference the
originating `ScenarioDef` by defName at all.** Once the game exists, editing or
deleting the def changes nothing.

⇒ Since our start IS a save, a `ScenarioDef` would only be a template that gets
copied once and then discarded. Everything it could carry can be written straight
into the save's `<parts>` list.

**Of the 72 live `ScenPartDef`s, the half that matters to a save-delivered start
is the ONGOING half.** Everything one-shot — starting things, starting research,
arrival method, pawn config, pawn modifiers, scatter parts — is **dead weight**,
because its effect is already baked into the save's pawns and things.

| still worth having, and why it is ongoing | defName | class |
|---|---|---|
| a permanent world-wrong condition | `PermanentGameCondition` | `ScenPart_PermaGameCondition` |
| one multiplier applied to everything | `StatFactor` | `ScenPart_StatFactor` — surfaces in the stat panel as the row keyed `StatsReport_ScenarioFactor` |
| stop the storyteller drawing an incident, **without cutting the def** | `DisableIncident` | `ScenPart_DisableIncident` |
| stop a quest, same shape | `DisableQuest` | `ScenPart_DisableQuest` |
| forbid a building or a designator for the whole run | `Rule_DisallowBuilding` · `Rule_DisallowDesignator_{Mine,Hunt,Tame,ZoneAdd_Growing}` | `ScenPart_DisallowBuilding` · `ScenPart_Rule_DisallowDesignator` |
| inject an incident on a timer | `CreateIncident` | `ScenPart_CreateIncident` — proven ticking by the assembly's own literal `Trying to tick ScenPart_CreateIncident but the incident is null` |
| the opening narration, for free | `GameStartDialog` | `ScenPart_GameStartDialog` |

⭐ **`DisableIncident` is the right tool for "present but dormant"**, and it is the
same doctrine as the Anomaly playstyle below: leave the def loadable so an
authored quest can still fire it deliberately, and only stop the storyteller
drawing it.

🔴 **Two of these do NOT take effect from a plain save edit.** `Rule_DisallowBuilding`
and `Rule_DisallowDesignator_*` materialise into `<rules><disallowedBuildings>` /
`<disallowedDesignatorTypes>` at `PostGameStart`, and nothing re-runs that on
load. **Append the part AND write the matching `<rules>` entry**, or add the part
before the save is first created. The live-queried parts (`StatFactor`,
`DisableIncident`, the ticking ones) work from the edit alone.

⚠️ **`ScenPart_Error`** — "One or more parts in this scenario could not be loaded
due to missing modded content". A save whose embedded scenario names a part from
an absent mod degrades rather than failing the load. Do not read a clean load as
proof the parts survived.

⛔ **Do NOT set `standardAnomalyPlaystyleOnly`.** It is a real `Scenario` field and
exactly one shipped scenario sets it — `TheAnomaly`, at
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Anomaly\Defs\Scenarios\Scenarios.xml:13`.
It greys out everything but the `Standard` playstyle, which would destroy R-S4.

## R-S3 · The planet type: patch the shipped def, and fill the two fields it leaves empty

⛔ **Never author a second `PlanetTypeDef`.** Only one is active at a time
(`PlanetTypeManager.activePlanetType`); ours would *replace* `TidallyLocked` and
drop the temperature curve the whole design rests on. **Patch by defName**, and
match on the subclass element `AlienWorlds.TidallyLocked.PlanetTypeDef` — that is
already what `JawaWorld_BiomeMix.xml` does and it is correct.

**The complete authorable API**, read from the mod's own shipped source at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3626210061\Source\PlanetTypeDef.cs`
(the framework, `7f.alienworlds`) — every one of these is an XML field:

| field | type | live value on `TidallyLocked` | our use |
|---|---|---|---|
| `biomes` | `List<string>` | **empty** | 🔴 **KEEP EMPTY.** Empty means "all allowed"; a whitelist silently excludes `Space`, `Orbit`, `Underground`, the undercaves and every pocket map |
| `biomeBlacklist` | `List<string>` | **our 29** | working. Overrules `biomes` |
| `biomeConfigs` | `Dictionary<string, BiomeConfig>` | 🔴 **empty — R-S1b** | the abundance/rarity mix. `scoreOffset` · `workerClass` · `texture` · `defFields` |
| `globalBiomeConfig` | `BiomeConfig` | unset | `scoreOffset` is meaningless here by the author's own comment. Only `defFields`/`workerClass` |
| `avgTempByLatitudeCurve` | `SimpleCurve` | the mod's 6 points, +70 → −80 | the day/night gradient. **Do not touch** — the arc-distance maths in `WORLDGEN_RUN.md` §2.C is derived from it |
| `seasonalTempVariationCurve` | `SimpleCurve` | 3 points, 15/15/5 | leave |
| `rainfallCurves` | `Dictionary<OverallRainfall, SimpleCurve>` | **EMPTY** | ⭐ **the XML home of R-H1** ("it rains only on the peaks"). Unwritten today |
| `defaultRainfallCurve` | `SimpleCurve` | unset | the fallback for any `OverallRainfall` value `rainfallCurves` omits |
| `elevationRange` | `FloatRange?` | **null** | the mountain/ocean share. ⚠️ its own author: *"I have absolutely no clue how it actually works"* |
| `sunlightFactor` | `float` | **1** | ⚠️ solar panel output ONLY, no visual change. A tidally locked dayside arguably wants > 1; **it is not a darkness dial** |
| `permaIceScoreOffset` | `float` | 0 | the temperature at which ice generates |
| `steamGeyserFactor` | `float` | 1 | geyser density — a fuel-adjacent dial, see the fuel-redundancy ruling |
| `oceanBiome` · `lakeBiome` | `string` | null | ⚠️ **must also appear in `<biomes>`** (author's comment) — which we keep empty. So these are unusable while `<biomes>` is empty |
| `hideWorldRivers` | `bool` | false | cosmetic |
| `scenParts` | `List<ScenPart>` | empty | ⭐ ScenParts applied to **every** scenario while this planet type is active — a second route for the R-S2 parts |
| `worldOceanTexture` · `ungeneratedPlanetPartsTexture` · `sunsetGradientTexture` · `cloudMapTexture` · `flavorTexture` · `thumbnailTexture` | `string` | partly set | presentation |

🔴 **`rainfallCurves` and `biomeConfigs` are BOTH `Dictionary`.** Both need the
`<li><key>/<value>` shape. Writing `rainfallCurves` in the keyed shorthand
reproduces R-S1b exactly.

**What BUILD authors here:** the `biomeConfigs` fix (R-S1b) and, if DECIDE's
hydrology ruling is to be expressed in XML rather than by hand-placement,
`rainfallCurves` + `defaultRainfallCurve`. Everything else stays as shipped.

⚠️ **One conflict to report, not to resolve.** `SeaIce` is on our
`biomeBlacklist`, and the Tidally Locked mod's own C# specifically postfixes
`BiomeWorker_SeaIce.GetScore` to `tile.WaterCovered ? PermaIceScore(tile) - 23f :
-100f` so that sea ice generates out to the world edge. **The blacklist wins**
(it is a hard exclusion) — so the mod's nightside-ice behaviour is being
suppressed by us. Whether that is wanted is DECIDE's call, not BUILD's; report it,
do not change it.

## R-S4 · Anomaly — `AmbientHorror`, and the file half is a NEGATIVE requirement

The playstyle itself is bucket B (B2). **The only thing BUILD owes here is not
to break it**, and there are exactly two ways to break it from a file:

1. ⛔ **Never set `standardAnomalyPlaystyleOnly` on any scenario we ship** (R-S2).
2. ⛔ **Never author a `DifficultyDef` preset for this campaign** (R-S5) — a
   non-Custom preset hides the anomaly threat slider and the game applies
   `SetupNonCustomDifficultyAnomalySettings` instead, which is not 0.

**The three defs, from the live dump — there are exactly three and no mod adds one:**

| defName | `generateMonolith` | `enableAnomalyContent` | `overrideThreatFraction` | `alwaysShowCodex` |
|---|---|---|---|---|
| `Standard` | true | true | false | false |
| ⭐ **`AmbientHorror`** | **false** | **true** | **true** | **true** |
| `Disabled` | false | **false** | false | false |

⭐ **`AmbientHorror` + the threat slider at 0% is "present but dormant".** Nothing
auto-spawns, no monolith ever, and study, the anomaly research tab, the entity
codex and tome trading all stay live. Because `generateMonolith` is false the
`minAnomalyThreatLevel` gate is skipped entirely, so `PitGate` and
`FleshmassHeart` can still be fired deliberately by an authored quest — which is
what unblocks the v2 sarlacc and the flesh vaults.

🔴 **`Disabled` is the wrong def and it was the recorded plan.** It sets
`enableAnomalyContent false`, which kills study, research, codex and tome
trading. The art survives; nothing you could build a sarlacc out of does.
Full derivation in `design/V2_DREAMS.md`, "Anomaly playstyle — measured, 2026-08-15".

## R-S5 · Difficulty: `Custom` is MANDATORY, and it CANNOT be authored as a file

**This is the one place where the natural bucket-A instinct is wrong, so it is
stated as a ruling rather than a note.**

`DifficultyDef` is an ordinary XML def — Storyteller Enhanced ships three, and
they load. **But authoring one for this campaign is the wrong move and would
silently cost us R-S4.**

| the trap | the evidence |
|---|---|
| Patching `DifficultyDef[defName="Custom"]` does nothing | vanilla's own file carries the comment *"no specific values defined, they are aren't used when Custom is selected"* — `…\Data\Core\Defs\Misc\DifficultyDefs\Difficulties.xml` |
| Authoring a **new** preset works, but is not Custom | `isCustom` is what the UI keys on; a new preset has `isCustom false` |
| 🔴 The anomaly threat slider renders **only** on `isCustom` | and a non-Custom preset instead gets `SetupNonCustomDifficultyAnomalySettings` — not 0 |
| 🔴 The dial we need is not on `DifficultyDef` at all | **`overrideAnomalyThreatsFraction` is absent from all 10 live `DifficultyDef`s.** It exists only on the runtime `Difficulty` object, which is scribed into the save under `<customDifficulty>` |

⇒ **Custom difficulty is a REQUIREMENT of this campaign, not a preference.** Any
ruling that names a slider value is lost the moment someone picks `Rough`.

**Six UI dials that exist on `Difficulty` and NOT on `DifficultyDef`** — i.e. they
can never be shipped in a file and must be set at the screen:
`overrideAnomalyThreatsFraction` · `anomalyThreatFraction` · `fixedWealthTimeFactor` ·
`friendlyFireChanceFactor` · `allowInstantKillChance` · `childShamblersAllowed`.

### The Custom fields this campaign actually rules on

The Custom page renders **48** labelled controls (keys `Difficulty_*_Label` in
`…\Data\Core\Languages\English\Keyed\Menus_Main.xml` plus the Anomaly file), in
eight sections. These are the ones our design has already committed to, with the
exact field name so nobody sets the neighbouring slider:

| our doctrine | the field, exactly | note |
|---|---|---|
| 🔴 **Anomaly content at zero** | `overrideAnomalyThreatsFraction` = **0** | UI label **"Anomaly threats"**, single slider. Renders only under `AmbientHorror` + Custom. Its own 0 label is *"No major threats"* |
| raids **heavier** | `threatScale` | ⚠️ this is **magnitude**, not frequency. Tooltip: *"Adjust the size of threats like raids and infestations"* |
| raids **fewer** | 🔴 **no such Custom slider exists** | `threatsGeneratorThreatCountFactor` is on `DifficultyDef` but has **no UI label**, so it is unreachable at the screen. Frequency lives on `StorytellerDef` comps (`onDays`/`offDays`/`minSpacingDays`/`numIncidentsRange`) — a bucket-A patch, not a click |
| "disable enemy flee %" | 🔴 **DOES NOT EXIST.** Strike it | No `flee` field on `DifficultyDef`, no `Difficulty_*Flee*` key anywhere. Fleeing is decided in code (`LordJob_AssaultColony.canTimeoutOrFlee`, `FleeUtility`). The docs quoting it — `setup_checklist.md` §1, `Gravship_Campaign_Planning_Discussion_2026-08-02.md:1420`, `concept.md:66` — are citing a setting that is not there. The nearest real dial is `enemyDeathOnDownedChanceFactor`, a different mechanic |
| adaptation off | `adaptationEffectFactor` (how much it bites) and `adaptationGrowthRateFactorOverZero` (how fast it grows) | note the `OverZero` suffix. **There is no decay field**; decay is hard-coded |
| a nomad should not be punished for a full hold | ⭐ `fixedWealthMode` + `fixedWealthTimeFactor` | ⚠️ `fixedWealthTimeFactor` is `Difficulty`-only. **Worth a deliberate ruling for a gravship campaign** — threat scaling off wealth fights "carry everything you own" |
| defence options | `allowTurrets` · `allowMortars` · `allowTraps` | ⛔ leave all three true unless DECIDE rules otherwise; the six founders are already a hard start |

⚠️ **Anti-trap:** `anomalyThreatsActiveFraction` (0.3) and
`anomalyThreatsInactiveFraction` (0.08) **are the `Standard`-playstyle pair** and
are the sliders shown when `displayThreatFractionSliders` is true. Under
`AmbientHorror` they are not the dial that fires — `overrideAnomalyThreatsFraction`
is. Setting the pair to 0 and leaving the override at its 0.15 default gives you
anomaly threats.

## R-S6 · Storyteller: `Randy`

`StorytellerDef`, 12 live, 11 visible. The defName is **`Randy`** (label "Randy
Random", Core) — not `RandyRandom`. Ratified in `setup_checklist.md` §1 and
unchanged. Bucket **C**: changeable later, so it is the cheapest decision on this
page. ⛔ Do not spend the owner's attention on it at the screen.

## R-S7 · Mod configs — bucket A, but written by the game, not by us

⚠️ `Config\ModsConfig.xml` and per-mod settings files are **written by the game
and by RimSort**, so they are bucket A only in the sense that they exist before
worldgen. They are `rimworld-start-prep`'s territory, not this spec's. The one
thing this spec asserts: **every FactionDef, ideo and planet-type patch must be
DEPLOYED and LOADED before the worldgen click** — writing a file is not deploying
it, and all three are read once.

---

# 🔴 Bucket B — the owner's checklist at world creation

> ⛔ **`WORLDGEN_RUN.md` §2 carries the owner's ruling of 2026-08-14: planet
> coverage, seed and planet type are HIS, decided at the screen, and nobody is to
> ratify values in advance.** This section obeys that. It supplies the
> **constraints and the warnings**, and deliberately leaves the numbers blank.

**Order of the screens, and it starts before the New Colony button:**
🔴 **Mod settings → Alien Worlds Framework (B4)** → storyteller & difficulty →
*Anomaly settings…* → world params (coverage, seed, rainfall, temperature,
population, landmarks, pollution) → *Advanced settings* → Configure Factions →
generate → landing tile.

| # | the choice | bucket-B evidence | what must be true |
|---|---|---|---|
| B1 | **Difficulty = Custom** | the anomaly slider block draws only when `difficulty.isCustom`; the values live in the save's `<customDifficulty>`, not in any def | 🔴 **Pick Custom BEFORE opening Anomaly settings.** Without it the threat slider is not on the page at all. *Technically re-selectable mid-game, but see B2 — the playstyle beside it is not, so treat the pair as one permanent click* |
| B2 | 🔴 **Anomaly playstyle = `AmbientHorror`** | `Dialog_AnomalySettings` is the only vanilla UI that writes `difficulty.AnomalyPlaystyleDef`, and `StorytellerUI.DrawStorytellerSelectionInterface` draws the "Anomaly settings…" button only inside `if (Current.ProgramState == ProgramState.Entry)`. `Page_SelectStorytellerInGame` calls the same method, so the button is simply **absent** once a game exists | **`AmbientHorror`, then drag "Anomaly threats" to 0%** (its own label at 0 is *"No major threats"*). ⛔ NOT `Disabled` — that kills study, research, codex and tome trading. The default on picking the playstyle is 0.15, so **not touching the slider is the failure mode** |
| B3 | **Permadeath / commitment = OFF** | `permadeathMode` and `permadeathModeUniqueName` are scribed on `Game`; `MustChoosePermadeath` is a storyteller-page validation string and no keyed string exists for changing it later | Ruled OFF (`setup_checklist.md` §1, owner 2026-08-04). OFF is the default — the risk is only an accidental tick |
| B4 | 🔴 **Planet type = `TidallyLocked`** — ⚠️ **NOT on this page. It is in Mod settings → Alien Worlds Framework** | R-S1. `ferny.Worldbuilder` is inactive so the backend is `Standalone`; the value is scribed per save as `alienWorldsFrameworkPlanetType` and the setting is labelled *"for new worlds"* | 🔴 **Today it reads `Default` and there is no settings file at all.** Set it, screenshot it, reopen the page to confirm. **Do not go to the world page until the settings page says *tidally locked world*** |
| B5 | **Globe coverage** (`planetCoverage`) | the world is generated once; nothing regenerates it | ⚠️ **The planet type's own description: *"Generating at least 50% of the planet is recommended."*** ⚠️ Against that: `required_mods.md` records a user report that **Faction Territories & Vassalage breaks above ~30% coverage**. 🔴 **These two constraints CONFLICT and the owner must be shown both.** F&T is explicitly cut-on-sight and not load-bearing; the planet type is. ⚠️ Coverage also drives generation time on a 576-mod stack | 
| B6 | **World seed** (`WorldSeed`) | as above | the owner's. Map Preview (WS 2800857642) shortlists |
| B7 | **Overall rainfall** — `overallRainfall`, three steps **Low · Normal · High** | keys `PlanetRainfall_Low/_Normal/_High`, `…\Data\Core\…\Keyed\Menus_Main.xml:54-58` | ⚠️ **This slider selects WHICH of our curves applies.** The planet type overrides `OverallRainfallUtility.GetRainfallCurve` **per `OverallRainfall` value** — so a `rainfallCurves` entry written for `Low` does nothing if the owner picks `Normal`. With `rainfallCurves` empty (today) the slider behaves vanilla. **If R-H1 is expressed in XML, DECIDE must also name the step** |
| B8 | **Overall temperature** — `overallTemperature`, **Low · Normal · High** | `PlanetTemperature_*` | ⚠️ **It sits ON TOP of `avgTempByLatitudeCurve`**, whose live range is +70 → −80 °C. The habitable ring is already narrow (`WORLDGEN_RUN.md` §2.C: ~34–57° of arc); a step off Normal moves it |
| B9 | **Population** — `overallPopulation`, **Sparse · Normal · Crowded** | `PlanetPopulation_*` | ⚠️ **It sets settlement DENSITY, not which factions exist** — that is B12 and it is a different page. The design wants trader frequency high (`setup_checklist.md` §9), which argues away from Sparse |
| B10 | **Landmarks** (Odyssey) — `landmarkDensity`, **Sparse · Normal · Crowded** | `PlanetLandmarkDensity_*`, `…\Data\Odyssey\…\Keyed\Menus_Main.xml:5-8` | ⭐ **Not previously on any checklist.** `desert_world_design.md`'s two-tier set-piece model rides native Landmarks generating the tile *type* before anything of ours authors its content. Sparse thins the layer the design assumes |
| B11 | **Pollution** (Biotech) — `pollution` | key `PlanetPollution`, `…\Data\Biotech\…\Keyed\Menus_Main.xml:22` | ⭐ **It closes the one residual Anomaly auto-spawn.** Under `AmbientHorror`, `GameComponent_Anomaly.TrySpawnHarbingerTrees` bypasses the threat fraction — but `GenStep_HarbingerTrees` sets `pollutionNone 0` / `pollutionLight 0`, so on an unpolluted world the desired count is 0 and the incident refuses. **Low pollution is load-bearing for R-S4, not cosmetic** |
| B12 | **Factions** | `WORLDGEN_FACTION_CHECKLIST.md`, ratified | 🔴 **A faction absent at world creation can NEVER be added later.** 21 untick / 6 keep / 13 set ≥ 1. Screenshot the page |
| B13 | **The landing tile** | the map is generated from it | `WORLDGEN_RUN.md` §2.B and §2.C — read the tile's **mutators**, and target by **arc distance from the subsolar point**, never by latitude |

🔴 **Screenshot every one of these screens.** The world is not reproducible from
any file in this repo, and a cold load is ~25–30 minutes.

---

# Bucket C — changeable later; note and move on

| setting | how it changes later |
|---|---|
| **Storyteller** | `Page_SelectStorytellerInGame`. Free |
| **Difficulty preset** | same page. ⚠️ but moving *off* Custom loses every custom value, including the anomaly override |
| **The anomaly threat slider** | adjustable in an existing save — **only while difficulty is Custom**. This is the reason B1 and B2 must be taken together |
| **Individual Custom sliders** | same page, same Custom-only condition |
| **Mod settings, autosave interval, UI** | any time |
| **Everything in `SCENARIO_SPEC.md`'s starting stock** | it is a save; edit the save |

---

## What BUILD owes

1. 🔴 **Get the planet type actually selected (R-S1).** Confirm `selectedPlanetType`
   reads `TidallyLocked` at the settings page, by whichever of the three routes.
   **This is the item that decides whether the campaign world is the designed
   world at all**, and today it reads `Default`.
2. 🔴 **Fix `biomeConfigs` in `src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml`**
   to the `<li><key>/<value>` shape (R-S1b), keep `<biomes>` empty, and **deploy it**.
   This blocks the worldgen run.
3. **Decide with DECIDE whether `rainfallCurves` carries R-H1**, and if so author
   it — same dictionary shape, same trap. Note it needs an `OverallRainfall` key
   matching the step the owner picks at B7.
4. **Author nothing as a difficulty file.** No `DifficultyDef`, no patch to
   `Custom` (R-S5).
5. **Author no `ScenarioDef`.** If any ongoing ScenPart is wanted, it goes into
   the save's `<parts>` — and for `Rule_Disallow*`, into `<rules>` as well (R-S2).
6. **Correct two state files that carry wrong facts:**
   - `infrastructure/state/EXPECTED_FAILURES_next_load.md` **S5** records
     `AnomalyFrequency_None` and friends as playstyle **defNames**. 🔴 **They are
     translation keys** — `…\Data\Anomaly\Languages\English\Keyed\Misc_Gameplay.xml:499-504`,
     the labels for the frequency slider. The only three playstyle defNames are
     `Standard` · `AmbientHorror` · `Disabled`. **S5's pass condition is
     unsatisfiable as written**: `grep -o "anomalyPlaystyleDef>[^<]*"` will never
     return `AnomalyFrequency_None`. Correct the expected value to `AmbientHorror`
     and add a second grep for `overrideAnomalyThreatsFraction` = 0.
   - `infrastructure/state/WORLDGEN_RUN.md` **§2.E** says playstyle `Disabled`.
     🔴 **Superseded by R-S4.** Point it at `AmbientHorror` + slider 0. Its §2.A
     also assumes the planet type is a choice *at the page*; per R-S1 it is not.
7. **Strike "disable enemy flee%" wherever it appears** (`setup_checklist.md` §1,
   `concept.md:66`, `Gravship_Campaign_Planning_Discussion_2026-08-02.md:1420`).
   The setting does not exist.
8. **Report, do not fix:** the `SeaIce` conflict above, and
   `Player.log:1080` `[Def Error]: TidallyLocked … Parsed 0.3 as int.`

## Verify

**Offline, before the load:**

- `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml --defs` — 0 errors.
- `grep -c "not <li>.*biomeConfigs" "<Player.log>"` on the **next** load returns **0**, where today it returns 28.
- `python3 src/RimMandrake/Utils/refresh.py`, then the live `PlanetTypeDef.json`
  entry for `TidallyLocked` reads **24** `biomeConfigs` entries and 29
  `biomeBlacklist` entries. 🔴 **The blacklist alone is not a pass** — that is
  exactly the state that hid this bug.
- No `ScenarioDef` and no `DifficultyDef` exist anywhere under `src/`.

**At the screen — the four that are unrecoverable if missed:**

- 🔴 **Mod settings → Alien Worlds Framework reads *tidally locked world*.**
  Check this FIRST; it is not on the world page and today it is wrong.
- Difficulty reads **Custom** and the *Anomaly settings…* button is present.
- The playstyle reads **ambient horror** and the *Anomaly threats* slider reads
  **0% / "No major threats"**.
- Screenshot each. They are the only record.

**After the world exists, from the save — the only read-back there is:**

```
grep -o "anomalyPlaystyleDef>[^<]*"            <the .rws>  # want AmbientHorror
grep -o "overrideAnomalyThreatsFraction>[^<]*" <the .rws>  # want 0
grep -o "<difficulty>[^<]*"                    <the .rws>  # want Custom
grep -o "alienWorldsFrameworkPlanetType>[^<]*" <the .rws>  # want TidallyLocked
```

⚠️ **The four greps above are DERIVED from field names, not from a save that has
them.** The six saves on disk are all `Rough` on the vanilla planet, so the
`customDifficulty`, `overrideAnomalyThreatsFraction` and
`alienWorldsFrameworkPlanetType` blocks are simply absent from every one of them.
**A grep returning nothing may mean the setting is wrong OR that the element is
spelled differently in the serialised form — resolve that against the first real
save, not against a guess.**

⚠️ **This costs one save and there is no other route.** `rimworld/get_game_info`
returns only `ticksGame` and `mapCount`. If the save is not taken, the setup
screens are gone and the answer is unrecoverable short of another worldgen.
