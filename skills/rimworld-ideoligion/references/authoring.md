# BUILD — the authoring layer, field by field

Companion to `SKILL.md` §3. Everything below is read out of a real def, the live
def dump (585 active mods, captured 2026-08-14T08:20:26Z, game 1.6.4871 rev591) or
`Assembly-CSharp.dll` metadata. Anything I could not verify is marked
**UNVERIFIED** and says why.

🔴 **Nothing here creates a religion.** `SKILL.md` §1 stands: there is no
`IdeoDef`. Every field below either *replaces* the generator's output for one
faction or *narrows* what it may roll. The `Ideo` object still comes into
existence at worldgen and lives in the save.

---

## 1. The `FactionDef` ideo block — complete field reference

All 87 installed `FactionDef`s carry the four booleans in the dump (the serializer
emits defaults), so their defaults are directly measurable: `fixedIdeo` true on 2,
`classicIdeo` on 2, `hiddenIdeo` on 2, `requiredPreceptsOnly` on 1. Everything
else is absent unless authored.

**Family A = author a fixed ideo. Family B = constrain a generated one.**
Mixing families is legal but mostly pointless: `fixedIdeo true` makes the
Family-B narrowing fields dead weight.

| field | type | default | family | what it does |
|---|---|---|---|---|
| `fixedIdeo` | `bool` | `false` | **A** | Do not generate. Build the ideo from `forcedMemes` + `ideoName` + `deityPresets` + `styles`. |
| `ideoName` | `string` | `null` | **A** | The religion's displayed name. Free text, not a def. Horax: `Nightmare Deep`. |
| `ideoDescription` | `string` | `null` | **A** | The paragraph shown in the ideo tab. Free text. |
| `forcedMemes` | `List<MemeDef>` | empty | **A** | **The complete meme set, structure meme included.** Not additive to a random roll. |
| `deityPresets` | `List<DeityPreset>` | empty | **A** | Named gods. Shape in §5. |
| `styles` | `List<StyleCategoryDef>` | empty | **A** | Art/apparel/tattoo style categories. Ceiling 3 — §6. |
| `hiddenIdeo` | `bool` | `false` | both | Keep the ideo off the player's ideo list UI. Horax and Odyssey `Salvagers` set it. |
| `classicIdeo` | `bool` | `false` | both | Give this faction the Ideology-off fallback belief set. `OutlanderCivil` and `AG_OutlanderCivilUnion` only. Mutually exclusive with authoring anything else. |
| `requiredPreceptsOnly` | `bool` | `false` | **A** | Take **only** the precepts the memes' `requireOne` groups demand — suppress every random extra. Meaningless without `fixedIdeo`. |
| `requiredMemes` | `List<MemeDef>` | empty | **B** | The roll must include these; the remainder is random. |
| `allowedMemes` | `List<MemeDef>` | empty | **B** | The random remainder may draw only from this list. Must be a superset of `requiredMemes`. |
| `disallowedMemes` | `List<MemeDef>` | empty | **B** | Never roll these. 🔴 **Mutually exclusive with `allowedMemes`** — both is a `ConfigError`. |
| `structureMemeWeights` | `List<MemeWeight>` | empty | **B** | Weighted pick of the one structure meme. **XML shape is `<MemeDefName>weight</MemeDefName>` children, not `<li>`** — see §3b. |
| `disallowedPrecepts` | `List<PreceptDef>` | empty | both | Blacklist. **The only precept field that exists on a FactionDef.** |
| `allowedCultures` | `List<CultureDef>` | empty | neither | Naming/style *culture*, not doctrine. 15 installed (`Astropolitan`, `Rustican`, `Corunan`, `Kriminul`, `Sophian`, …). Present on 66 of 87 FactionDefs — the commonest of the lot and the one most often mistaken for a religion field. |

**Fields I looked for and confirmed do NOT exist on `FactionDef`:** `requiredPrecepts`,
`forcedPrecepts`, `preceptsOnly`, `ideoIconPath`, `ideoColor`, `allowedIdeoPresets`,
`ideoNameMaker`. The complete key list is 125 fields; none of those is in it.
(Query: every key present across all 87 dumped `FactionDef`s.)

### Wild usage counts — every ideo field, all 585 mods

`fixedIdeo` 2 · `ideoName` 2 · `ideoDescription` 2 · `deityPresets` 2 ·
`forcedMemes` 3 · `styles` 4 · `hiddenIdeo` 2 · `classicIdeo` 2 ·
`requiredPreceptsOnly` 1 · `structureMemeWeights` 39 · `requiredMemes` 38 ·
`disallowedMemes` 31 · `disallowedPrecepts` 28 · `allowedMemes` 21 ·
`allowedCultures` 66.

**Every fully-authored religion in the installed universe, in full:**

| faction | source | pattern |
|---|---|---|
| `HoraxCult` | `ludeon.rimworld.anomaly` | `fixedIdeo` + `hiddenIdeo` + `requiredPreceptsOnly`, 3 memes, 3 styles, 1 deity |
| `DV_PirateKeshig` | `det.keshig` | `fixedIdeo`, 3 memes (`Structure_TheistAbstract`/`Raider`/`PainIsVirtue`), 2 styles, **2 deities**, no `requiredPreceptsOnly` |
| `Salvagers` | `ludeon.rimworld.odyssey` | `forcedMemes` **without** `fixedIdeo` — one meme (`Shipborn`) + `hiddenIdeo` + `styles` |

⚠️ **`MemeDef.factionWhitelist` exists and is not what you would guess.**
`Inhuman` is whitelisted to `HoraxCult`, `Shipborn` to `TradersGuild` — yet Odyssey's
`Salvagers` forces `Shipborn` anyway. So the whitelist gates the *random picker*,
not `forcedMemes`. **Inferred from those two defs; the enforcement site in the
assembly is UNVERIFIED.** Treat a whitelisted meme in `allowedMemes` as a no-op and
in `forcedMemes` as probably fine.

---

## 2. §meme budget — the measured cap

🔴 **There is no total-impact budget. The enforced ceiling is a meme COUNT.**

Read from the CLI metadata of
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
(Field + Constant tables, and the `RimWorld.IdeoFoundation..cctor` IL decoded by
hand — `ldc.i4.1 ldc.i4.4 newobj IntRange stsfld MemeCountRangeAbsolute`):

| symbol | value | what it governs |
|---|---|---|
| `IdeoFoundation.MemeCountRangeAbsolute` | `IntRange(1, 4)` | 🔴 **hard cap: 1–4 NORMAL memes.** The structure meme is outside it. |
| `IdeoFoundation.MemeCountRangeNPCInitial` | `IntRange(1, 3)` | how many normal memes a *generated* NPC ideo gets |
| `IdeoFoundation.MemeCountRangeFluidAbsolute` | `IntRange(1, 1)` | a fluid ideo starts at one meme |
| `IdeoFoundation.MaxStyleCategories` | `3` | see §6 |
| `IdeoFoundation.MaxRituals` | `6` | rituals per ideo |
| `IdeoImpactUtility.MaxMemeImpact` | `3` | **label scale only** |
| `IdeoImpactUtility.MaxCombinedImpact` | `9` | **label scale only** |

`MaxMemeImpact` and `MaxCombinedImpact` are used *only* to clamp a translation-key
index — `Mathf.Clamp(x,1,3)` → `IdeoMemeImpactLabel_1..3` (low/medium/high) and
`Mathf.Clamp(x,1,9)` → `IdeoImpactLabel_1..9` (low → extreme), both keyed in
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Ideology\Languages\English\Keyed\MainTabs.xml`
lines 86–95. Nothing compares an impact sum to them.

**Proof they are not budgets:** two shipped `IdeoPresetDef`s exceed 9 —
`VME_Inhuman_Ravagers` and `VME_Insectoid_Psykers` both total **impact 10** and
simply display as "extreme". Measured across all 46 installed presets: totals span
1–10, and the maximum meme list length is **5 = 1 structure + 4 normal**, never 6.

Enforcement site: `Dialog_ChooseMemes.TryAccept` compares
`GetMemeCount(MemeCategory.Normal)` against `MemeCountRangeAbsolute` and emits
`MessageNotEnoughMemes` / `MessageTooManyMemes`
(`…\Data\Ideology\Languages\English\Keyed\Messages.xml` lines 14–15).
It is a hardcoded C# constant — not in any def, not difficulty- or
settings-dependent, not scaling.

**Impact distribution, 136 installed memes:** 35 at impact 0 (all 35 structure
memes), 27 at 1, 50 at 2, 24 at 3.

⇒ **Author to 3 normal memes, 4 at the absolute outside.** The project's
`faction_religions_spec.md` gives most factions **4** normal memes — legal against
the absolute cap, one above what the NPC generator would ever produce, and worth a
deliberate decision rather than a default.

⇒ `validate_ideoligion.py` correctly leaves `DEFAULT_IMPACT_BUDGET = None`
(`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\validate_ideoligion.py` line 58).
**Do not pass `--impact-budget`.** There is nothing to enforce.

**UNVERIFIED:** whether `forcedMemes` listing 5+ normal memes is clamped, ignored
or accepted. No def in the installed universe exceeds 3, so there is no natural
experiment. `Dialog_ChooseMemes` is the *editor* path, not the worldgen path.

---

## 3. Skeletons

All three validate clean. Every defName below was read out of the live dump today.

### 3a. Family A — a fully authored NPC religion (Horax pattern)

Project faction 11, the Junkers. 3 normal memes, total impact 8, no exclusion-tag
collision, structure `deityCount 0` so no `deityPresets`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <FactionDef ParentName="FactionBase">
    <defName>Jawa_Junkers</defName>
    <label>junkers</label>
    <pawnsPlural>junkers</pawnsPlural>
    <categoryTag>Pirate</categoryTag>
    <permanentEnemy>true</permanentEnemy>
    <techLevel>Industrial</techLevel>

    <!-- ===== the ideo block ===== -->
    <fixedIdeo>true</fixedIdeo>
    <ideoName>the Ladder</ideoName>
    <ideoDescription>There is no doctrine. There is the ladder, and there is what you can carry up it. Everything that stops climbing is scrap.</ideoDescription>

    <forcedMemes>
      <!-- exactly one Structure_*; the rest are Normal; 1-4 of those -->
      <li MayRequire="sarg.alphamemes">AM_Structure_Scavenger</li>
      <li MayRequire="Ludeon.RimWorld.Ideology">Raider</li>
      <li MayRequire="Ludeon.RimWorld.Ideology">Cannibal</li>
      <li MayRequire="vanillaexpanded.vmemese">VME_Scrapper</li>
    </forcedMemes>

    <requiredPreceptsOnly>true</requiredPreceptsOnly>

    <styles>
      <li MayRequire="sarg.alphamemes">AM_Scavenger</li>
      <li MayRequire="Ludeon.RimWorld.Ideology">Spikecore</li>
    </styles>

    <disallowedPrecepts>
      <li MayRequire="Ludeon.RimWorld.Ideology">Slavery_Disapproved</li>
    </disallowedPrecepts>
    <!-- no deityPresets: AM_Structure_Scavenger has deityCount 0..0 -->
  </FactionDef>

</Defs>
```

### 3b. Family B — constrain a generated religion (Empire pattern)

Note the two different container shapes: `<li>` for meme lists,
`<MemeDefName>weight</MemeDefName>` for `structureMemeWeights`. Copied from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Royalty\Defs\FactionDefs\Faction_Empire.xml`
lines 27–48.

```xml
<FactionDef ParentName="FactionBase">
  <defName>Jawa_Homesteaders</defName>
  <label>homestead defense league</label>
  <allowedCultures><li>Rustican</li></allowedCultures>

  <requiredMemes>
    <li MayRequire="Ludeon.RimWorld.Ideology">Individualist</li>
  </requiredMemes>

  <allowedMemes>
    <li MayRequire="Ludeon.RimWorld.Ideology">Individualist</li>
    <li MayRequire="Ludeon.RimWorld.Ideology">Guilty</li>
    <li MayRequire="Ludeon.RimWorld.Ideology">Rancher</li>
    <li MayRequire="sarg.alphamemes">AM_WaterPrimacy</li>
  </allowedMemes>

  <!-- NO disallowedMemes here: it is mutually exclusive with allowedMemes.
       An allowedMemes whitelist already excludes Cannibal and Raider. -->

  <structureMemeWeights>
    <Structure_TheistAbstract MayRequire="Ludeon.RimWorld.Ideology">1</Structure_TheistAbstract>
  </structureMemeWeights>

  <disallowedPrecepts>
    <li MayRequire="Ludeon.RimWorld.Ideology">Slavery_Acceptable</li>
    <li MayRequire="Ludeon.RimWorld.Ideology">IdeoDiversity_Abhorrent</li>
  </disallowedPrecepts>

  <styles>
    <li MayRequire="Ludeon.RimWorld.Ideology">Rustic</li>
  </styles>
</FactionDef>
```

🔴 **`allowedMemes` and `disallowedMemes` are mutually exclusive** — defining both
is a `ConfigError` the game rejects. Corroborated: **zero of the 87 installed
FactionDefs carry both** (13 use `disallowedMemes` alone, 21 `allowedMemes` alone).
And **every `requiredMemes` entry must also appear in `allowedMemes`** when a
whitelist is present — the Empire lists `Collectivist` and `Loyalist` in both
(`Faction_Empire.xml` lines 27–37). Both rules are errors in the validator
(`faction/both-meme-lists`, `faction/required-not-allowed`).

⚠️ **Multiple `structureMemeWeights` entries are legal** — the Empire ships one,
`OutlanderCivil` ships **30** — but `validate_ideoligion.py` flattens them into the
meme set and reports `structure/multiple`. **That is a known false positive on
Family B**, the only one. One entry keeps the gate green; more than one means
reading the error rather than trusting it.

⚠️ **`requiredMemes` + `allowedMemes` do not control the count.** The generator
still rolls `MemeCountRangeNPCInitial` = 1–3 normal memes. Listing four "allowed"
memes does not mean the faction gets four.

### 3c. `IdeoPresetDef` — the player start screen

Complete field set, verified across all 46 installed presets:
`categoryDef · memes · classicPlus · iconPath` (plus `label`/`description`).
**There is no precept field and no deity field.**

```xml
<?xml version="1.0" encoding="utf-8"?>
<Defs>

  <IdeoPresetDef>
    <defName>Jawa_ScrapCreed</defName>
    <label>scrap creed</label>
    <description>The gravship is the only ground. What it cannot carry is not real, and what it can be rebuilt from is holy.</description>
    <categoryDef>Strong</categoryDef>   <!-- Classic | Fluid | Mild | Strong | Intense | Custom -->
    <classicPlus>false</classicPlus>
    <memes>
      <li MayRequire="sarg.alphamemes">AM_Structure_Scavenger</li>
      <li MayRequire="vanillaexpanded.vmemese">VME_Scrapper</li>
      <li MayRequire="Ludeon.RimWorld.Ideology">Individualist</li>
      <li MayRequire="Ludeon.RimWorld.Ideology">Tunneler</li>
    </memes>
  </IdeoPresetDef>

</Defs>
```

- `categoryDef` takes an `IdeoPresetCategoryDef`. The six installed are `Classic`,
  `Fluid`, `Mild`, `Strong`, `Intense`, `Custom`
  (`…\Data\Ideology\Defs\PreconfiguredIdeos\IdeoPresetDefs.xml` lines 6–43).
- The structure meme goes in `<memes>` like any other and must come **first** —
  that is what all 17 structure-carrying presets do. 29 of the 46 omit it and let
  the player pick.
- `classicPlus: true` means "classic RimWorld plus this" — only `ClassicLike` uses it.
- `iconPath` is optional; exactly one preset sets it (`ClassicLike` →
  `UI/HeroArt/RimWorldLogo`).
- Ceiling: 1 structure + 4 normal, same `MemeCountRangeAbsolute` as everything else.

---

## 4. `MayRequire` — the packageId table

🔴 **On the `<li>`, never on the parent.** `<forcedMemes MayRequire="…">` is wrong
and does nothing useful; the attribute belongs on each element that names a def
from another mod. Same for `structureMemeWeights` — it goes on the
`<Structure_Foo MayRequire="…">` element.

- `MayRequire="a.b"` — drop this node unless `a.b` is active.
- `MayRequireAnyOf="a.b,c.d"` — keep if **any** listed packageId is active.
  Comma-separated, no spaces.
- **Case-insensitive at load, but `ModsConfig.xml` casing is what you should
  match.** Steam mods appear there without the `_steam` suffix in this install.

Every mod supplying an ideoligion def in this campaign (585 active mods,
counted from the live dump, activity confirmed against
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`).
**All of these are active today.**

| packageId | mod | memes | precepts | styles | rituals | presets |
|---|---|---|---|---|---|---|
| `Ludeon.RimWorld.Ideology` | Ideology | 32 | 179 | 10 | 23 | 23 |
| `vanillaexpanded.vmemese` | VIE — Memes and Structures | 48 | 160 | 13 | 13 | 21 |
| `sarg.alphamemes` | Alpha Memes | 35 | 109 | 13 | 25 | – |
| `llunak.moreprecepts` | Ideology: More Precepts | 2 | 52 | – | 5 | – |
| `oskarpotocki.vanillavehiclesexpanded` | Vanilla Vehicles Expanded | 4 | 27 | – | – | – |
| `erdelf.humanoidalienraces` | Humanoid Alien Races | 2 | 20 | – | – | – |
| `telardo.romanceontherim` | Romance On The Rim | – | 16 | – | 1 | – |
| `divinederivative.romance` | Way Better Romance | – | 14 | – | – | – |
| `Ludeon.RimWorld.Anomaly` | Anomaly | 2 | 8 | 1 | – | 1 |
| `Ludeon.RimWorld.Biotech` | Biotech | 1 | 9 | – | 1 | 1 |
| `mlie.preceptsandmemes` | Precepts and Memes (Continued) | 3 | 9 | – | – | – |
| `Ludeon.RimWorld` | Core | – | 11 | – | – | – |
| `vanillaexpanded.vgeneticse` | Vanilla Genetics Expanded | 2 | 9 | – | – | – |
| `garryflowers.moreslaverystuff` | More Slavery Stuff | – | 9 | – | – | – |
| `oskarpotocki.vfe.tribals` | VFE — Tribals | – | 6 | – | 6 | – |
| `Ludeon.RimWorld.Odyssey` | Odyssey | 1 | 6 | – | 1 | – |
| `vanillaexpanded.gravship` | Vanilla Gravship Expanded Ch.1 | – | 5 | – | 2 | – |
| `oskarpotocki.vfe.pirates` | VFE — Pirates | 1 | 4 | – | 1 | – |
| `ap.huntingmeme` | [AP] Hunting Meme | 1 | 4 | – | – | – |
| `mlie.preceptsandmemesritualsmodule` | P&M — Rituals module | – | 4 | – | 4 | – |
| `vanillaquestsexpanded.generator` | VQE — The Generator | 1 | 3 | – | – | – |
| `Ludeon.RimWorld.Royalty` | Royalty | – | 2 | – | 2 | – |
| `biomesteam.biomescaverns` | Biomes! Caverns | 1 | 1 | – | – | – |

**Style-only suppliers (1 `StyleCategoryDef` each):** `asp.halituisamaricanous`
(`ASP_Astronomy_StylePack`) · `det.keshig` (`DV_Tengrism`) ·
`kxp.ideosymbolsasideograms` (`KxPDefaultStyleBase`) · `tleno.wireheadstyle`
(`Tleno_Wirehead`).
**Long tail, 1–3 precepts each, no memes or styles:** `redmattis.bigsmall.core` ·
`gulmadred.breedingritual` · `thesepeople.ritualattachableoutcomes` ·
`dimonsever000.ideologyvirtues` · `lovelydovey.recreation.witheuterpe` ·
`lovelydovey.sex.witheuterpe` · `avius.prisonlabor` · `lee.theforce.lightsaber` ·
`amegakull.scvrole`.

Ludeon's own four verified verbatim from `ModsConfig.xml` lines 9–13 (they appear
there lowercased; the canonical mixed-case form above is what vanilla defs write):
`ludeon.rimworld.royalty`, `ludeon.rimworld.ideology`, `ludeon.rimworld.biotech`,
`ludeon.rimworld.anomaly`, plus `ludeon.rimworld.odyssey` and `ludeon.rimworld`.

⚠️ **`Ludeon.RimWorld.Ideology` still needs `MayRequire` on Ideology defs**, even
though this campaign always runs it — vanilla does it on every one of its own,
and a def that skips it breaks any Ideology-off sanity check.

---

## 5. `deityPresets`

Verified verbatim from `HoraxCult`,
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Anomaly\Defs\FactionDefs\Factions_Misc.xml`
lines 48–56.

```xml
<deityPresets>
  <li>
    <nameType>
      <name>Horax</name><type>God of the Void</type>
    </nameType>
    <gender>Male</gender>
    <iconPath>UI/Deities/DeityGeneric</iconPath>
  </li>
</deityPresets>
```

| element | type | notes |
|---|---|---|
| `nameType` | `DeityNameType` | required; two children |
| `nameType/name` | `string` | the proper name |
| `nameType/type` | `string` | the epithet — "God of the Void", "Bringer of War" |
| `gender` | `Gender` | `Male` / `Female` / `None`. **UNVERIFIED** whether `None` is accepted here; both shipped examples use Male/Female. |
| `iconPath` | `string` | texture path. Vanilla ships `UI/Deities/DeityGeneric`, `UI/Deities/DeityEvil`, `UI/Deities/DeityGood` (the latter two read out of `DV_PirateKeshig`). |

**The `deityCount` rule.** Every `MemeDef` of `category: Structure` carries
`deityCount`, an `IntRange`, and that governs **how many deities the generator
invents**. Structure memes are the only source of a deity count; normal memes have
none. Installed values:

- `deityCount 0..0` — 22 of 35 structures, including all of `Structure_Archist`,
  `Structure_Ideological`, `Structure_Animist`, `AM_Structure_Scavenger`.
- `deityCount 1..1` — `Structure_OriginChristian`, `Structure_OriginIslamic`,
  `VME_Structure_Corporate`, `AM_Structure_Horaxian`, …
- `deityCount 1..4` — `Structure_TheistAbstract`.
- `deityCount 2..4` — `Structure_TheistEmbodied`.
- `deityCount 4..4` — `Structure_OriginHindu`, `AM_Structure_Kemetism`,
  `AM_Structure_Neolithic`, `VME_Structure_ChthonianCult`.

🔴 **A `deityPresets` block on a `deityCount 0..0` structure is legal but strange
— and Ludeon ships exactly that.** `HoraxCult` names one deity on
`Structure_Archist` (0..0). The structure invents no gods, so the religion has only
what you named. Whether the named preset then *displays* is **UNVERIFIED** and sits
on the live-load checklist in `references/validation.md`.
`validate_ideoligion.py` reports this as a WARN (`deity/structure-generates-none`),
not an error — match that.

⇒ **If the design calls for named gods, pick a structure whose `deityCount` covers
the number you are naming.** `Structure_TheistAbstract` (1..4) is the flexible one.

---

## 6. Styles

`FactionDef.styles` is a `List<StyleCategoryDef>`. A `StyleCategoryDef` supplies:

| field | supplies |
|---|---|
| `thingDefStyles` | `ThingDef` → `ThingStyleDef` pairs — the alternate art for beds, sculptures, apparel, walls |
| `addDesignators` | extra build menu entries the style unlocks (e.g. `Morbid` adds `MorbidSlab_Medium`, `MorbidSlab_Broad`) |
| `addDesignatorGroups` | grouped build menu entries |
| `iconPath` | the style's UI icon |
| `ritualVisualEffectDef`, `soundOngoingRitual` | ritual dressing |
| `fixedIdeoOnly` | 🔴 gate — see below |

🔴 **`IdeoFoundation.MaxStyleCategories = 3`** (assembly const). `HoraxCult` uses
exactly three. Do not list a fourth.

🔴 **`fixedIdeoOnly: true` means the style cannot be rolled by the generator.**
Exactly one installed style carries it: `Horaxian` (`ludeon.rimworld.anomaly`).
Such a style is reachable only through a `fixedIdeo` faction's `styles` list.

**The live list is the palette, not this file:**
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\data\ideology_palette.md`
§"Style categories (41)", line 1204. 41 installed, from 8 mods — 10 Ideology,
13 Alpha Memes, 13 VIE-Memes, 1 each from Anomaly, `det.keshig`,
`asp.halituisamaricanous`, `kxp.ideosymbolsasideograms`, `tleno.wireheadstyle`.

⚠️ **A vanilla `styles` list is not what the game ends up with.** Anomaly's XML
writes `<li>Horaxian</li>`, but the resolved dump shows `HoraxCult.styles =
[AM_Horaxian, Morbid, Techist]` — Alpha Memes replaces the whole list at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2661356814\1.6\Mods\Anomaly\Patches\CultFactionPatch.xml`
(a `PatchOperationReplace` on `/Defs/FactionDef[defName="HoraxCult"]/styles`).
Read the **dump**, not the vanilla XML, when you want to know what a faction
actually has.

Memes also drag styles in via `MemeDef.thingStyleCategories` / `styleItemTags`,
independently of the faction's `styles` list. **UNVERIFIED** whether those count
against `MaxStyleCategories`.

---

## 7. Authoring order, and the silent-failure checklist

**Write it in this order. Each step makes the next one cheap.**

1. **Pick the structure meme first.** It fixes `deityCount`, which fixes whether
   §5 applies at all. Read the count out of the palette, line 11.
2. **Pick 1–3 normal memes** (4 is the absolute ceiling, §2). Check every pair's
   `exclusionTags` against each other *before* writing XML — the palette lists them.
3. **Decide the family.** `fixedIdeo` if the doctrine is load-bearing for the
   campaign; `structureMemeWeights` + `requiredMemes` if you only want flavour.
   Do not write both.
4. **`requiredPreceptsOnly` only with `fixedIdeo`**, and only when you want the
   religion *empty* of random doctrine. It is what makes the Junkers austere.
5. **Deities, then styles** — ≤3 styles, and only styles from the palette.
6. **`disallowedPrecepts` last**, and only for precepts that would actively
   contradict the design. It is a blacklist; it cannot add anything.
7. **Wrap every non-Ludeon def in `MayRequire`** using §4. On the `<li>`.

**Then run the gate before you believe any of it:**

```bash
python3 src/RimMandrake/Utils/validate_ideoligion.py --xml <path to your FactionDefs.xml>
python3 src/RimMandrake/Utils/validate_ideoligion.py --md design/Jawa/worldbuilding/faction_religions_spec.md
```

Exit 0 = no errors. **Do not pass `--impact-budget`** (§2).

🔴 **Every one of these fails silently — no red error, no log line, the faction
just generates something else:**

| failure | what you see in game | caught offline by |
|---|---|---|
| defName not installed | faction has a different religion | `def/unknown-meme` |
| meme from a disabled mod | same | `def/inactive-mod` |
| missing `MayRequire` | works today, breaks on any load-order change | `def/needs-mayrequire` (INFO) |
| two memes share an `exclusionTag` | one is dropped | `meme/exclusion` |
| zero or two structure memes | random structure | `structure/none` / `structure/multiple` |
| `deityPresets` on a `deityCount 0` structure | possibly no gods shown | `deity/structure-generates-none` (WARN) |
| precept with `visible: false` | never appears | `precept/invisible` |
| precept with `enabledForNPCFactions: false` | never appears on a faction | `precept/npc-disabled` |
| precept whose `conflictingMemes` hits your set | dropped | `precept/conflicting-meme` |
| >4 normal memes | **UNVERIFIED** — clamp, ignore or accept | nothing yet |
| `allowedMemes` + `disallowedMemes` together | ⚠️ **not silent** — a red `ConfigError` | `faction/both-meme-lists` |
| a `requiredMemes` entry outside `allowedMemes` | ⚠️ **not silent** — a red `ConfigError` | `faction/required-not-allowed` |
| a 4th style | **UNVERIFIED** — probably truncated | nothing yet |

**Offline green is not built.** Only a game load proves the ideo was *constructed*
as specified — `references/validation.md` §live.
