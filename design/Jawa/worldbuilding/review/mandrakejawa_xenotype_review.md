# `MandrakeJawa` — design + engineering review

_VISION seat, 2026-08-14. Measured against the live def dump refreshed 2026-08-14 01:19–01:20
(`GeneDef.json`, 4833 genes · `XenotypeDef.json`, 250 · `XenotypeIconDef.json`, 227) and against
the file itself. **No skill covers xenotypes in this project** — `skills/` has no such entry, so
the instruments used were the def dump, `src/RimMandrake/Utils/genome_matrix_build.py`'s parsing
convention (`load_dump()` → `["defs"]`), and `strings` on `Assembly-CSharp.dll`._

---

## VERDICT BOX

1. **Nothing in the world spawns it.** `MandrakeJawa` is a `<savedXenotype>` editor file, referenced
   by **zero** defs, mods, scenarios or saves. It appears only where you pick it by hand.
2. **Metabolism total: exactly 0.** Complexity 31, archite 0. The "permanently hungry, nutrient
   paste forever" failure mode **does not apply** — this genome is perfectly budget-balanced.
3. **5 real defects**, one of them load-bearing: **the reproduction chain does not close.**
4. **Verdict: SHIP WITH CHANGES.** The changes cost **+1 complexity and 0 metabolism** in total.
5. The live copy is `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\MandrakeJawa.xtp`
   — **not** the `deployed\config\xenotypes\` path you are backing up to.

---

## B. Does this thing ever spawn? — No. And that changes what the rest of this review is for.

| question | answer | evidence |
|---|---|---|
| Is there a `XenotypeDef` named `MandrakeJawa`? | **NO** | `XenotypeDef.json`, 250 defs — the only Jawa entries are `OuterRim_Jawa`, `BTD_Jawa`, `Jawa_Xeno_Gamorrean` |
| Does any `PawnKindDef` reference it? | **NO** | `grep MandrakeJawa` over the whole `DefDump/defs/` tree → **zero files** |
| Any `FactionDef` / `ScenarioDef`? | **NO** | same grep |
| Any mod, in repo or deployed? | **NO** | `/mnt/d/Luke/dev/Rimworld/` (excl. `.git`) → 1 hit, the file itself. All 21 local mods under `Mods\` → 0 hits |
| Any save? | **NO** | `Saves\` is empty (0 files); `Saves_old\` 40+ `.rws`, all 2022, 0 hits |

**What it actually is.** The root element is `<savedXenotype>`; the engine reads these through
`get_XenotypesFolderPath` / `get_CustomXenotypesForReading` / `XenotypesAvailableFor` (confirmed as
literals in `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`).
That means it surfaces in exactly three places: **starting-pawn xenotype selection, the xenotype
editor, and the gene assembler / xenogerm UI.** It is invisible to worldgen, to raids, to trader
caravans, to wanderer-joins. Nothing generates it.

### Where the file has to live

| | path | state |
|---|---|---|
| **live — the game reads this** | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes\MandrakeJawa.xtp` | present, 54 327 bytes, saved 2026-08-14 11:50 |
| **backup — the game never reads this** | `D:\Luke\dev\Rimworld\deployed\config\xenotypes\MandrakeJawa.xtp` | byte-identical (`md5 380dd10a67787b56884886f1763ecdc6`), copied 12:22 |

⚠️ The folder is `Xenotypes\`, a **sibling** of `Config\` and `Saves\` — it is *not* inside `Config\`.
The repo backup path `deployed\config\xenotypes\` implies otherwise, so a restore driven by that path
name would put the file where nothing reads it. Rename the backup folder or leave a note in it.

### So what is `BTD_Jawa` for, and why does this matter

`BTD_Jawa` is the thing that **actually generates**, and it is what every tuning patch targets:

| | `MandrakeJawa` (this file) | `BTD_Jawa` (the campaign's real Jawa) |
|---|---|---|
| kind | `<savedXenotype>` file | `XenotypeDef`, mod `[BTD] Xenotype REMIX: Star Wars` |
| genes | 35 | 24 |
| metabolism / complexity | **0 / 31** | **+1 / 17** |
| icon | `iconDef BS_Lilim` | `iconPath OuterRim/XenotypeIcons/Xenotype_Jawa` |
| spawned by | nothing | `OuterRim_Jawa` + `OuterRim_JawaTribal` pawnkinds, `chance 1`, re-pointed by `D:\Luke\dev\Rimworld\src\Jawa\Jawa_Patches\Patches\JawaXenotype_Repoint.xml` |
| in a faction | — | **no `FactionDef` references either pawnkind** (0 hits in `FactionDef.json`) |

They share **21 genes**. `MandrakeJawa` adds 14 and drops 3.

- **adds:** `AG_FrailSkin`, `AG_Stinky`, `AG_SurvivalInstinct_High`, `AG_TableResistance`,
  `AG_UnderdevelopedTeeth`, `BS_EarlyMaturity`, `MinTemp_SmallIncrease`, `Mood_Pessimist`,
  `Outland_Evasive`, `Outland_FamiliarScent`, `SEX_Ovipositor`, `StrongStomach`,
  `VRE_Curiosity_Social`, `VRE_ShortPregnancy`
- **drops:** `Hair_DarkBlack`, `Hair_Grayless`, `Outland_Chest_Fur`

**The action this implies.** Either (a) accept it as a start-of-game-only choice for your own founding
pawns — fine, and then the fiction lives only in your head; or (b) **promote it to a real
`XenotypeDef` in `Jawa_Patches` and point the two `OuterRim_Jawa*` pawnkinds at it instead of
`BTD_Jawa`.** Route (b) is the only one where the 14 extra genes ever touch a pawn you did not
personally create, and it is also the only route that can carry a description and a proper icon.
Right now you are maintaining two Jawa genomes and only one of them is in the game.

---

## Defects, worst first

### D1 🔴 The reproduction chain does not close, and three genes are riding on it

Your own lore (`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\jawa_xenotype_and_religion.md` §4.3)
specifies all-male, male-male conception, egg-laying, fast growth. The file attempts exactly that.
It does not land.

| gene | what the def actually says | status |
|---|---|---|
| `Outland_AllMale` | `GeneExtension.forceMale: true` — "always male at birth" | **works** |
| `SEX_Ovipositor` | *"**Gestor or aphrodor** carriers of this gene will be born with an ovipositor instead of a uterus."* `GenderWorksModExtension.femaleReproductiveReplacement: SEX_Ovipositor` | **conditional — see below** |
| `VRE_ShortPregnancy` | `pregnancySpeedFactor 1.5`, met −1, cpx 1 | inert unless a pregnancy exists |
| `BS_EarlyMaturity` | `PawnExtension.babyStartAge: 3`, met −1, cpx 2 | inert unless a birth exists |

**The gap is measurable.** Gender Works (`lovelydovey.sex.*`, three modules active in `ModsConfig.xml`)
models reproductive sex on its **own axis** — gestor / aphrodor / phallor / neuter — separate from
vanilla `Gender`. It ships four genes that pin it, all in exclusion group `SEX_Reproductive`:
`SEX_AlwaysGestor`, `SEX_AlwaysAphrodor`, `SEX_AlwaysPhallor`, `SEX_AlwaysNeuter` (each met 0, cpx 1).

**None of the four is in your gene list.** So reproductive sex is left to whatever Gender Works rolls,
and `SEX_Ovipositor` fires on only the fraction of pawns that roll gestor or aphrodor. It is a coin
flip you are paying 1 complexity for.

**Second gap.** No same-sex-pregnancy mod is installed. `ModsConfig.xml` (590 entries) contains no
Simple Trans, no Simple Trans Expanded, no Samesex IVF — the two routes your own §4.3 identified as
required. The romance stack is there (`divinederivative.romance`, `telardo.romanceontherim`,
`mianreplicate.romanceandintimacyontherim`, `lovelydovey.*`); the *conception* half is not.

**Third gap.** How `Outland_AllMale`'s `forceMale` interacts with Gender Works' independent sex axis
is a C#-to-C# question between two mods. **UNVERIFIED — I did not decompile either.** It is exactly
the kind of thing that reads as working in the editor and produces nothing at the keyboard.

**The fix that removes the whole dependency** is in Outland Genetics — the *same mod* that supplies
`Outland_AllMale`, so no cross-mod sex-axis ambiguity at all:

| gene | met | cpx | description, verbatim from `GeneDef.json` |
|---|---|---|---|
| `Outland_EggLayer` | 0 | 1 | "Carriers of this gene reproduce by laying an egg rather than typical pregnancy." |
| `Outland_AsexualReproduction` | 0 | 1 | "Carriers of this gene can reproduce asexually, allowing them to **begin a pregnancy or lay eggs at will without a partner**." |
| `Outland_AcceleratedPregnancy` | −1 | 1 | "…half as long for a pregnancy to complete, this even applies to eggs… Affects all Outland reproduction options!" |

All three are present in the live dump. `Outland_AsexualReproduction` is the load-bearing one: it makes
an all-male clan reproduce **without needing a same-sex-pregnancy mod at all**, which is the single
biggest de-risking available here.

### D2 🔴 Three eye genes, one exclusion slot — two of them are dead

This is the **only** exclusion collision in the entire 35-gene set. I checked every `exclusionTags`
entry across all 35 genes; every other tag is held by exactly one gene.

| gene | mod | `exclusionTags` | `texPath` | met/cpx |
|---|---|---|---|---|
| `guy762_Eyes_HugeYellow` | Star Wars Xenotypes | `["EyeColor"]` | `JawaEyes/jawaeyes_glow` | 0 / 0 |
| `Jawa_Eyes_HugeOrange` | Jawa Patches (local) | `["EyeColor"]` | `JawaEyes/jawaeyes_glow` | 0 / 0 |
| `Jawa_Eyes_HugeAmber` | Jawa Patches (local) | `["EyeColor"]` | `JawaEyes/jawaeyes_glow` | 0 / 0 |

**What happens.** RimWorld does not delete the losers — `Assembly-CSharp.dll` carries
`CheckForOverrides`, `OverrideBy`, `overriddenByGene` and `get_Overridden`. All three genes stay on the
pawn; two are marked **overridden** and render greyed-out in the Genes tab, contributing nothing.

**What the eyes will look like.** All three render the *same* texture, `JawaEyes/jawaeyes_glow`, with
`shaderTypeDef: MoteGlow` and `colorType: Custom`. They differ only in tint and in
`displayOrderInCategory` (1774 / 1775 / 1776). So you get **huge glowing eyes either way** — the
silhouette is never in doubt. What is undefined is the *tint*: yellow, orange or amber.

**Which one wins is UNVERIFIED.** The tie-break lives inside `CheckForOverrides` in the compiled
assembly and I did not decompile it. The exact RGB of each is also unreadable — the dump emits
`"color": "<skipped:Color>"` and does not serialise `Color`. **This is a case where the instrument
cannot see the field, so I am reporting it missing rather than guessing a winner.**

**Cost of the defect: 0 metabolism, 0 complexity.** It is free to fix and free to leave. Fix it anyway,
because "which tint do my Jawa have" is currently a question with no answer.

⚠️ **`BTD_Jawa` has the identical defect** — it also carries all three, and it is the one that spawns.
Fixing it there is the higher-value change. Filing that for whoever owns `Jawa_Patches`.

### D3 🔴 On a desert world, this xenotype is worse at night than a baseliner

The two temperature genes read straight off `statOffsets`:

| gene | stat | offset |
|---|---|---|
| `MinTemp_SmallIncrease` (label: **"cold weakness"**) | `ComfyTemperatureMin` | **+4.5 °C** |
| `MaxTemp_LargeIncrease` (label: "heat super-tolerant") | `ComfyTemperatureMax` | **+20 °C** |

Human baseline comfy band is 16 °C – 26 °C, so:

> **`MandrakeJawa` comfortable band = 20.5 °C to 46.0 °C.**

| claim | verdict |
|---|---|
| genuinely heat-adapted? | **YES, strongly.** 46 °C ceiling is 20 above baseliner; a desert noon is a non-event. |
| can survive the night side? | **NO better than a baseliner — 4.5 °C worse.** They start taking cold discomfort at 20.5 °C, where a baseliner is fine to 16 °C. RimWorld desert nights routinely fall well below both. |

Note the label trap that caught the sibling xenotype: `MinTemp_SmallIncrease` sounds like cold
tolerance. It is the opposite — *increasing* your minimum comfortable temperature makes you **worse**
in cold. Its own label says "cold weakness" and its `labelShortAdj` is `warm`.

**This is not automatically wrong.** It is +1 free metabolism, and "Jawa are never seen unrobed" is
solved by heavy clothing anyway — so it is arguably *on-theme*. But it must be a decision, not a
side effect. If the campaign involves caravans or outposts (§4.4 says it does), swapping to
`MinTemp_SmallDecrease` (`ComfyTemperatureMin −10`, met −1, cpx 1) moves the floor from 20.5 °C to
6 °C for a 2-point metabolism swing.

### D4 🟠 `Jawa_Gene_Skittish` — your flagship custom gene is probably mechanically inert

Source: `Jawa Patches (local)`. Its description is the best writing in the whole genome. Its entire
mechanical payload is one line:

```
"statFactors": [{"stat": "Terror", "value": 1.5}]
```

`Terror` (`StatDef.json`, mod **Ideology**, `category BasicsPawn`, `defaultBaseValue 0`, `maxValue 100`,
description *"The intensity of terror this person is experiencing"*) is the stat vanilla reads for
**slave suppression**. A free colonist sits at 0, and multiplying 0 by 1.5 is 0.

**UNVERIFIED — I did not decompile `Terror`'s consumers**, so I cannot state categorically that
nothing else reads it. But from the defs alone I can find no path by which this gene changes anything
a free Jawa colonist does. The fiction says "does not stand and trade fire; finds cover, finds
numbers"; the def delivers a number nobody reads.

Second, smaller: its `displayCategory` is **`Turn_GeneCategory_Slavery`** — so in the gene picker it
files under a Slavery heading, next to slave-suppression genes. That is a paste-artifact, not intent.

**Fix is ours to make**, in `Jawa_Patches`. Something that fires on a colonist: a `ShootingAccuracy`
or `MentalBreakThreshold` modifier, or a forced trait. Cost of the current gene is +1 met / +1 cpx,
so replacing its payload is metabolism-neutral if you keep the biostats.

### D5 🟡 `iconDef BS_Lilim` is Big and Small's demon icon — and the right Jawa icon exists

| | |
|---|---|
| what `BS_Lilim` is | a `XenotypeIconDef` (not a XenotypeDef) from **Big and Small — Genes & More**, `texPath: Xenotypes/BS_Lilim` |
| where the art is | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2920751126\Textures\Xenotypes\BS_Lilim.png` |
| what it looks like | I opened it: a black-lineart round head, curled hair or horns on both sides, two round pupils. **Lilim is that mod's succubus xenotype.** |
| does it read as a Jawa? | **Half.** The hooded round silhouette with two prominent eyes is closer than you would expect — but the side curls read as horns, it is lineart rather than a dark hood, and it is another species' identity. |

**The correct asset is already on disk and already in use.** `BTD_Jawa` renders
`OuterRim/XenotypeIcons/Xenotype_Jawa` — I opened it too: a solid dark hood with two glowing orange
discs. It is the fiction, exactly.

`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2980427615\Common_Old\Textures\OuterRim\XenotypeIcons\Xenotype_Jawa.png`

**Why you could not pick it.** A `<savedXenotype>` can only name an `iconDef`, and **none of the 227
`XenotypeIconDef`s in the live dump points at a Jawa texture** — I grepped every `iconPath` and every
`defName` for "jawa" and got zero. `BTD_Jawa` reaches the art through the `XenotypeDef.iconPath`
*string* field, which a saved xenotype cannot use. So the fix is a three-line def in `Jawa_Patches`:

```xml
<XenotypeIconDef>
  <defName>Jawa_Icon_Hood</defName>
  <texPath>OuterRim/XenotypeIcons/Xenotype_Jawa</texPath>
</XenotypeIconDef>
```

⚠️ The texture sits under `Common_Old\` in that mod, which implies a `LoadFolders.xml` version gate.
It resolves today (BTD_Jawa renders it), but **confirm the path is the one the 1.6 fold serves before
shipping the def** — see `skills/rimworld-modding/references/patch-operations.md` §9.

### Not defects, but know them

**The missing `<description>` is the file format, not an omission.** `CustomXenotype`'s serialised
members are name / inheritable / genes / iconDef — `description` is not among them, and none of the six
`.xtp` files on this machine has one. RimWorld builds the tooltip from the gene list instead. **So it
does not surface as a blank in the UI.** But it does mean the fiction has nowhere to live. If you want
a description a player reads, the xenotype must become a real `XenotypeDef` — another argument for
route (b) in section B.

**`guy762_BodySizeGene_smaller` is cosmetic-only, and that is a bargain.** Its one `statOffset` is
`SM_Cosmetic_BodySizeOffset −0.5` — a Big-and-Small Framework stat, `category SM_Stats`, literally
named *cosmetic*. There is no food reduction, no carry-capacity change, no hitbox change. Yet the
author priced it at **+2 metabolism**, i.e. as a drawback. You are being paid 2 points of budget for a
purely visual change. Just do not expect "small" to mean anything mechanically.

**`AG_Stinky` and `Outland_FamiliarScent` push against each other.** Stinky bothers everyone;
Familiar Scent gives an opinion bonus among the same xenotype. In an all-Jawa colony they partly
cancel; the net penalty lands on visitors and slaves. That is arguably the right shape for the
fiction — Jawa smell terrible to *outsiders*.

---

## A. The mechanical audit

### A1 — Biostat totals

> **metabolism 0 · complexity 31 · archite 0** — summed across all 35 genes from `GeneDef.json`.

**What the metabolism number means at the keyboard.** A baseliner has no genes and therefore a
metabolism of 0, so **your Jawa eat exactly what a baseliner eats.** No nutrient-paste dependency, no
permanent hunger spiral, no need for a dedicated farm-to-feed-the-genes. This is the single most
playable fact about the genome, and it is not luck — the two halves balance to the point:

| direction | sum |
|---|---|
| genes **giving** budget (drawbacks, positive `biostatMet`) | **+15** |
| genes **spending** budget (benefits, negative `biostatMet`) | **−15** |
| **total** | **0** |

*(The off-zero mapping lives in `GeneTuning.MetabolismToFoodConsumptionFactorCurve` — I confirmed the
curve exists by name in `Assembly-CSharp.dll` but **could not read its points from disk. UNVERIFIED.**
The direction is certain — negative total eats more, positive eats less — and 0 is the defined neutral
point, which is all this genome needs.)*

**Biggest contributors, both ways:**

| gene | met | cpx | what it does |
|---|---|---|---|
| `Mood_Pessimist` | **+3** | 1 | permanent mood penalty |
| `guy762_BodySizeGene_smaller` | **+2** | 1 | cosmetic size only (see above) |
| `WoundHealing_Slow` | **+2** | 1 | `InjuryHealingFactor ×0.5` |
| `Pain_Extra` | **+2** | 1 | **forces the `Wimp` trait** |
| `AG_UnderdevelopedTeeth` | +1 | 1 | `EatingSpeed ×0.7` |
| `AG_Stinky` | +1 | 1 | opinion penalty |
| `AG_FrailSkin` | +1 | 0 | `IncomingDamageFactor ×1.1` |
| `MinTemp_SmallIncrease` | +1 | 1 | `ComfyTemperatureMin +4.5` |
| `MeleeDamage_Weak` | +1 | 1 | `MeleeDamageFactor ×0.5` |
| `Jawa_Gene_Skittish` | +1 | 1 | `Terror ×1.5` — probably inert (D4) |
| — | | | |
| `MaxTemp_LargeIncrease` | **−2** | 1 | `ComfyTemperatureMax +20` |
| `VRE_Curiosity_Social` | **−2** | 2 | no Social skill loss + recreation from social |
| `AptitudeStrong_Construction` | −1 | 2 | **Construction +4** |
| `AptitudeStrong_Crafting` | −1 | 2 | **Crafting +4** |
| `AptitudeStrong_Social` | −1 | 2 | **Social +4** |
| `AG_SurvivalInstinct_High` | −1 | 1 | `ForagedNutritionPerDay ×1.75` |
| `Outland_Evasive` | −1 | 1 | `MeleeDodgeChance +10` |
| `DarkVision` | −1 | 1 | no darkness mood penalty, sees in the dark |
| `StrongStomach` | −1 | 1 | never food-poisoned, eats rot |
| `Superclotting` | −1 | 1 | bleeding stops fast |
| `AG_TableResistance` | −1 | 1 | no "ate without a table" |
| `BS_EarlyMaturity` | −1 | 2 | `babyStartAge 3` — inert (D1) |
| `VRE_ShortPregnancy` | −1 | 1 | 1.5× gestation speed — inert (D1) |

*(The 12 genes not listed are all met 0: the cosmetics, the three eye genes, `Jawa_Head_Plain`,
`Outland_Blood_Gray`, `Outland_FamiliarScent`, `Outland_AllMale`, `SEX_Ovipositor`.)*

**What complexity 31 means.** For your use case — a start-of-game inheritable xenotype — **nothing.
Complexity is not checked on that path.** It only gates the gene assembler: base capacity is
`BaseMaxComplexity` (hardcoded, **value not readable from disk — UNVERIFIED**) and each gene processor
adds `GeneticComplexityIncrease 2`
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Biotech\Defs\ThingDefs_Buildings\Buildings_Misc.xml:832`).
At 31 you would need roughly a dozen processors to ever build this as a xenogerm. **So: you cannot
realistically convert an existing colonist into a MandrakeJawa. It is a birth-or-start genome only.**

### A2 — Conflicts and silent overrides

I checked `exclusionTags`, `prerequisite` and the override machinery across all 35 genes. The dump's
field names are `exclusionTags` (list of strings) and `prerequisite`; there is no `overrides` or
`disablesGenes` field on `GeneDef` in this build.

| finding | result |
|---|---|
| `prerequisite` set on any of the 35 | **none** — every one is `null` |
| exclusion tags held by more than one gene | **exactly one: `EyeColor`** (see D2) |
| all other tags | held by exactly one gene each — `MinTemperature`, `MaxTemperature`, `Mood`, `Pain`, `WoundHealingRate`, `MeleeDamage`, `BodySize`, `SkinColorOverride`, `HairStyle`, `BeardStyle`, `BodyType`, `BloodType`/`Blood`, `Gender`/`AG_Gender`, `Aptitude_*` ×3, `AG_*` ×5, `BS_*` ×2, `VRE_Curiosity`/`Curiosity`, `Turn_Exclusion_NightVision` |

**The three suspicions, resolved:**

1. **Three eye genes** — confirmed collision, all on `EyeColor`. Two go overridden, the surviving tint
   is undefined, the rendered texture is the same in all three cases. Zero biostat cost. → **D2**
2. **`Outland_AllMale` + the reproduction pair** — `forceMale: true` is real. `VRE_ShortPregnancy`
   (met −1, cpx 1) and `BS_EarlyMaturity` (met −1, cpx 2) are inert with no births, i.e. **3
   complexity and 2 points of spent metabolism budget doing nothing**. `SEX_Ovipositor` does imply a
   reproduction route of its own — Gender Works' gestor/aphrodor axis — but that axis is left
   unpinned, so it is a coin flip. → **D1**
3. **Temperature pair** — resolved to a comfortable band of **20.5 °C – 46.0 °C**. Heat-adapted yes;
   night side no, and 4.5 °C worse than a baseliner. → **D3**

### A3 — Missing-def check

> **All 35 genes resolve. Zero will be dropped on load.**

Checked every defName against `GeneDef.json` (4833 defs, dumped 2026-08-14 01:19). No dangling
references. `iconDef BS_Lilim` also resolves — against `XenotypeIconDef.json`, not `XenotypeDef.json`
(it is **absent** from the latter, which is correct and not a fault). The mod list that produced this
file matches the mod list that is loaded.

Source mods represented: Biotech (16 genes), Alpha Genes (5), Outland - Genetics (4), Jawa Patches
local (4), Star Wars Xenotypes (2), Big and Small (1), VRE-Archon (1), VRE-Genie (1),
Intimacy - Gender Works (1).

---

## C. The design read

### Does it play like a Jawa?

**Delivered at the keyboard — the fiction is genuinely legible:**

| fiction | gene | what you see |
|---|---|---|
| desert-adapted | `MaxTemp_LargeIncrease` | comfortable to 46 °C; noon is a non-event |
| glowing eyes, never unhooded | `Jawa_Eyes_*` + `Jawa_Head_Plain` + `Hair_BaldOnly` + `Beard_NoBeardOnly` + `Skin_InkBlack` | huge `MoteGlow` eyes on a black face under forced head types. **This is the best-executed part of the genome.** |
| tinker | `AptitudeStrong_Construction` + `_Crafting` | **+4 Construction, +4 Crafting** — a fresh Jawa builds and crafts like a veteran |
| trader | `AptitudeStrong_Social` + `VRE_Curiosity_Social` | +4 Social, *and* Social never decays, *and* socialising is recreation |
| scavenger | `AG_SurvivalInstinct_High` + `StrongStomach` + `AG_TableResistance` | 1.75× caravan foraging, eats rot without consequence, no table needed. **Perfect.** |
| burrower / hull-dweller | `DarkVision` | no darkness mood penalty — they work unlit corridors happily |
| dangerous in numbers, not alone | `Outland_Evasive` | +10 melee dodge — hard to pin, weak to trade blows with |
| clannish | `Outland_FamiliarScent` | same-xenotype opinion bonus |

**Invisible in play:**

- `Jawa_Gene_Skittish` — the flagship, and probably a no-op (D4). The most on-theme *writing* in the
  file attached to the least on-theme *mechanics*.
- `guy762_BodySizeGene_smaller` — renders smaller, changes nothing.
- `SEX_Ovipositor` / `VRE_ShortPregnancy` / `BS_EarlyMaturity` — the entire reproduction story (D1).
- `Outland_Blood_Gray` — cosmetic.

**The gap the genes cannot close:** "robed, never seen unhooded" is an *apparel* fact. No gene can
force clothing. That belongs in the pawnkind's `apparelTags` / `apparelRequired` or an Ideology
apparel precept — out of scope for this file, but do not expect the xenotype to deliver it.

### Is the negative load fun or just punishing?

Honest answer: **it is characterful in the mid-game and genuinely miserable in the first season**, and
one gene is doing most of the damage.

| gene | early-colony feel |
|---|---|
| `Mood_Pessimist` | **the problem.** A flat mood penalty on every pawn, all the time, from day one — before you have a dining room, art, or a decent bed. It compounds with every other early-game mood hit rather than being survivable on its own. |
| `Pain_Extra` | **worse than it looks.** It carries `forcedTraits: Wimp`. That is not "feels more pain" — it is *goes down from injuries other pawns walk off*. |
| `AG_FrailSkin` | mild. `IncomingDamageFactor ×1.1` is 10%; you will not feel it. |
| `WoundHealing_Slow` | real but slow-acting. Half-speed healing means a wounded Jawa is out of the roster for twice as long — painful with a 5–7 pawn cap. |
| `MeleeDamage_Weak` | **on-theme and cheap.** Jawa should lose melee fights. Pair it with `Outland_Evasive` and you get "hard to hit, useless when it hits back", which is precisely the fiction. |
| `Jawa_Gene_Skittish` | costs nothing because it does nothing (D4). |
| `AG_UnderdevelopedTeeth` | `EatingSpeed ×0.7` — a real time tax, and thematically excellent for a species with a hooded, ill-suited mouth. |

**The two I would cut first, in order:**

1. **`Mood_Pessimist` (met +3, cpx 1).** It is the single largest drain on early-colony fun and it is
   the least visible in the fiction — Jawa are *nervous* and *greedy*, not *depressed*. Cutting it
   costs you **3 points of metabolism budget** (total goes 0 → −3, so they eat more), which is the
   real price and it is not trivial. Pay it by dropping the two inert reproduction genes (below).
2. **`Pain_Extra` (met +2, cpx 1).** The `Wimp` trait on a colony of five is brutal — one raid and
   you have three pawns on the floor from flesh wounds. Cutting it costs 2 more metabolism. If you
   want to keep the flavour without the trait, keep `AG_FrailSkin` and `WoundHealing_Slow`; between
   them you still have "fragile, slow to recover" without the collapse mechanic.

**Cutting both costs 5 metabolism** (total → −5) — that is the point where you *would* start feeling
food pressure. So do not cut both without freeing budget elsewhere; see the numbered list.

### What is missing that the fiction promises

Every gene named below was checked against the live dump before recommending it.

| missing | candidate | met / cpx | note |
|---|---|---|---|
| **working reproduction** | `Outland_AsexualReproduction` + `Outland_EggLayer` | 0/1 + 0/1 | **the priority.** Same mod as `Outland_AllMale`. |
| **"dangerous in numbers"** — nothing makes them good with guns | `AptitudeStrong_Shooting` | −1 / 2 | +4 Shooting. Turns "cowardly individually" into a *tactic* (many bad-melee, good-shooting pawns behind cover) rather than just a weakness. |
| **cold survival for caravans/outposts** | `MinTemp_SmallDecrease` | −1 / 1 | replaces `MinTemp_SmallIncrease`; band becomes 6 °C – 46 °C |
| **faster gestation, to match §4.3 "fast-growing"** | `Outland_AcceleratedPregnancy` | −1 / 1 | works on eggs too; would replace `VRE_ShortPregnancy` |
| **explicit orientation** — §4.3 calls for the "Gay gene" | **not available.** Biotech's `Gay`/`Bisexual` are **ABSENT** from this dump; the only orientation genes present are `BS_Bisexual` (Big and Small, **met 0 / cpx 0 — free**) and asexual-reproduction genes. | 0 / 0 | `BS_Bisexual` is free and closest to intent. |
| **robes / never unhooded** | *no gene route exists* | — | pawnkind `apparelRequired` or an Ideology apparel precept |

---

## Verdict — **SHIP WITH CHANGES**

The genome is better engineered than most hand-built xenotypes: metabolism balances to exactly zero,
all 35 genes resolve, and there is precisely one exclusion collision in the whole set. The visual
identity is excellent. What is broken is the reproduction story and one dead flagship gene.

### The changes, in priority order

| # | change | Δ met | Δ cpx | running total |
|---|---|---|---|---|
| **1** | **Close the reproduction chain.** Remove `SEX_Ovipositor`; add `Outland_EggLayer` **and** `Outland_AsexualReproduction`. Removes the dependency on Gender Works' unpinned sex axis *and* on a same-sex-pregnancy mod you do not have installed. | **0** | **+1** | 0 / 32 |
| **1b** | *(alternative to 1, if you would rather stay on Gender Works)* keep `SEX_Ovipositor`, add `SEX_AlwaysGestor`. Cheaper in mods, but leaves the `forceMale` × gestor interaction UNVERIFIED. | 0 | +1 | 0 / 32 |
| **2** | **Drop two of the three eye genes.** Keep `Jawa_Eyes_HugeAmber` (ours, and the highest display order); remove `guy762_Eyes_HugeYellow` and `Jawa_Eyes_HugeOrange`. Fixes the undefined tint. **Do the same to `BTD_Jawa` — that one actually spawns.** | **0** | **0** | 0 / 32 |
| **3** | **Give `Jawa_Gene_Skittish` a real payload** in `Jawa_Patches` — swap `Terror ×1.5` for something a free colonist feels, and move `displayCategory` off `Turn_GeneCategory_Slavery`. Keep the biostats as they are. | **0** | **0** | 0 / 32 |
| **4** | **Add a `XenotypeIconDef` for the Jawa hood** and point `<iconDef>` at it instead of `BS_Lilim`. Confirm the `Common_Old` texture path first. | **0** | **0** | 0 / 32 |
| **5** | **Cut `Mood_Pessimist`.** The single biggest early-game misery for the least fiction. | **−3** | −1 | **−3** / 31 |
| **6** | **Drop the now-inert `BS_EarlyMaturity`** if you take route 1 and its `babyStartAge 3` is redundant with the Outland accelerated line; **or keep it** — it is the one reproduction gene that still fires once births work. Listed as optional. | +1 | −2 | −2 / 29 |
| **7** | **Swap `VRE_ShortPregnancy` → `Outland_AcceleratedPregnancy`.** Same cost, but works on eggs, which is what you will now have. | 0 | 0 | −2 / 29 |
| **8** | **Swap `MinTemp_SmallIncrease` → `MinTemp_SmallDecrease`** *only if* the campaign runs caravans and outposts. Band 20.5–46 °C becomes 6–46 °C. | **−2** | 0 | −4 / 29 |
| **9** | **Add `AptitudeStrong_Shooting`** to make "dangerous in numbers" a real tactic. | −1 | +2 | −5 / 31 |
| **10** | **Add `BS_Bisexual`** — free, and it is the §4.3 orientation the fiction calls for. | **0** | **0** | −5 / 31 |

**Changes 1–4 are the review's actual recommendation: they fix all five defects for +1 complexity and
zero metabolism.** Everything from 5 down is taste, and 5 + 8 + 9 together would put you at −5
metabolism, which is where food starts to matter — spend that budget deliberately.

### And the decision underneath all of it

None of this touches a pawn unless you either pick the xenotype by hand at game start, or promote it
to a `XenotypeDef` in `Jawa_Patches` and re-point the two `OuterRim_Jawa*` pawnkinds at it. **Decide
that first.** If the answer is "hand-picked founders only", changes 2 and 4 are cosmetic polish on a
thing five pawns will ever have, and the higher-value work is applying change 2 to `BTD_Jawa` — which
is what every Jawa in the world actually is.

---

## What I could not verify

| item | why |
|---|---|
| Which of the three eye genes wins the `EyeColor` slot | the tie-break is inside `CheckForOverrides` in `Assembly-CSharp.dll`; not decompiled |
| The RGB of each eye gene's tint | the dump emits `"color": "<skipped:Color>"` — it does not serialise `Color` at all |
| Whether `Outland_AllMale`'s `forceMale` overrides Gender Works' gestor/aphrodor assignment | a C#-to-C# interaction between two mods; unreadable from defs |
| Whether anything besides slave suppression reads the `Terror` stat | consumers not decompiled; reported as *probable* no-op, not certain |
| The points of `GeneTuning.MetabolismToFoodConsumptionFactorCurve` | confirmed to exist by name in the assembly; values are compiled, not on disk. Irrelevant here — the total is 0, the defined neutral point. |
| `BaseMaxComplexity`'s numeric value | hardcoded in the assembly; only the name is a readable literal |
| Whether the `Common_Old\` Jawa icon path is the one the 1.6 fold serves | needs that mod's `LoadFolders.xml` read before shipping change 4 |
