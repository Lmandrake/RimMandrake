# Which xenotypes could feasibly be made big — BIG_WEAPON_XENOTYPE_AUDIT_1

_Measured 2026-08-22 by BUILD against the live def dump
(`defs.sqlite`, mods=578/`9a204707f6dc183d`, game 1.6.4871 rev591, captured
2026-08-21T22:44:59Z) and the mods' own XML on disk. Reproduce the numbers with
`python3 src/RimMandrake/Utils/xenotype_size_audit.py genes / xenotypes / shortlist / report`._

---

## 🔴 THE ANSWER, IN ONE LINE

**The gate is real, and there is exactly one size threshold in it: body size over 1.99
lets a pawn hold a GIANT weapon. Warcasket weapons have no size threshold at all. And
both gates open to a named trait as well — so `BS_GiantWeaponWielder`, a one-line gene
that changes no size whatsoever, unlocks everything the size route unlocks.**

Two consequences the owner should have before ruling:

1. **1.99 is ogre scale, not "big and tall".** A human is 1.0. The smallest gene that
   clears the bar is `OgreFrame` at +1.0 → exactly 2.0. `BS_LargeFrame` (+0.4 → 1.4) —
   the gene that actually reads as "big and tall" — is **not enough**, and never will be.
2. ⇒ **For every Star Wars species, the size route is the wrong route.** A Wookiee at
   2.1 m is not twice a human's mass, and giving it `OgreFrame` to unlock a hammer would
   misrepresent the species to win a permission check. `BS_GiantWeaponWielder` is the
   correct instrument and it costs 1 complexity and 0 metabolism.

Making a species physically larger and making it able to hold big weapons are two
separate edits. Either can be done without the other.

---

## 1. THE MECHANISM, MEASURED

### ⚠️ There are TWO gates and they are not the same gate

The item that filed this work assumed one. There are two, they come from different mods,
and only one of them is declared in XML at all.

#### Gate A — warcasket and other "heavy" weapons: an explicit allow-list

Every one of the **15 warcasket weapons** (all from Vanilla Factions Expanded — Pirates;
no other mod in the stack ships one) carries a `VEF.Weapons.HeavyWeapon` modExtension.
Read from the dump, post-patch, identical on all 15:

```
supportedTraits : VFEP_WarcasketTrait, BS_Giant, RBM_Herculean_Trait
supportedGenes  : VQEA_Enormous, AG_ToughSinews
isHeavy         : true
refusal         : VFEP.RequiresWarcasket -> "Requires warcasket"
```

The extension's entire field vocabulary is `isHeavy`, `supportedTraits`, `supportedGenes`,
`disableOptionLabelKey`, `weaponHitPointsDeductionOnShot`. 🔑 **There is no body-size,
stature, mass or strength field in it.** A pawn is admitted if and only if its trait or
gene defName appears in one of those two lists.

`VFEP_WarcasketTrait` has `commonality 0` — it is never rolled. It is granted by
**wearing the warcasket apparel** (`VEF.Apparels.ApparelExtension` → `traitsOnEquip`), and
taken away on unequip. That is the vanilla intent: the armour carries the gun, not the
pawn.

The other four entries were added by other mods patching the same list:

| entry | added by | how a pawn gets it |
|---|---|---|
| `BS_Giant` | Big and Small — Framework, `compatibilityPatches.xml` | forced by the giant frame genes, or by `BS_GiantWeaponWielder` |
| `RBM_Herculean_Trait` | Roo's Minotaur Xenotype | the `RBM_Herculean` gene |
| `AG_ToughSinews` | Alpha Genes | the gene itself — *"Carriers of this gene can naturally use Heavy weapons or Warcasket weapons without the need of assisting armor."* |
| `VQEA_Enormous` | Vanilla Quests Expanded — Ancients | the gene itself |

⚠️ Big and Small's patch is **unconditional and global** — it appends `BS_Giant` to *every*
`HeavyWeapon` extension in the game, creating the node if absent. That is why `BS_Giant`
appears twice in the serialised list.

#### Gate B — the "giant" weapons: a real size check, and it is C#

⛔ **The `*Giant` weaponTags are naming convention only. No code reads them.** They exist
solely so vanilla's spawn-time weapon picker can pair a `PawnKindDef.weaponTags` entry with
a `ThingDef.weaponTags` entry. The item that filed this work suspected as much and it was
right — but it was looking at the wrong field, which is why the gate looked absent.

**The marker is `ThingDef.weaponClasses`, not `weaponTags` and not a modExtension.**
Measured in the dump: **23 ThingDefs** carry `weaponClasses: BS_GiantWeapon` — the same 23
that carry a `*Giant` weaponTag, all from Big and Small — Genes & More and
Big and Small — Weapons. `BS_GiantWeapon` is a `WeaponClassDef` from Big and Small —
Framework, and the whole 578-mod stack contains exactly **one** `ItemRestrictionDef`:

```
BS_ItemRestrictionDefaults   (Big and Small - Framework)
  restrictedTags: [ BS_GiantWeapon ]
```

**Enforcement**, read as decoded IL out of
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2925432336\1.6\Base\Assemblies\BigAndSmall.dll`:

- `BigAndSmall.CanEquipPatches.CanEquip_Postfix` — a Harmony **postfix on the vanilla
  `RimWorld.EquipmentUtility.CanEquip`** — funnels into `CanEquipPatches.CanEquipThing`.
- Sibling postfixes `PawnCanWear_Postfix`, `AllowedForPawn_Postfix`, `RequiredForPawn_Postfix`
  and `GeneratePawns_Patch.RemoveInvalidThings` funnel into the same method, so **the gate
  also runs at pawn generation** — a too-small raider's giant weapon is stripped at spawn,
  not merely un-equippable later.
- `ItemRestrictionHelper.HasRequiredWeaponClassTags` reads `ThingDef.weaponClasses` and
  tests it against `ItemRestrictionDef.restrictedTags`. No name-sniffing, no hardcoded list.
- The pawn side is built in `BSCache.RegenerateCache`, and it is an **OR**:

```
    pawn has the BS_Giant trait      (or a trait whose defName contains "warcasket")
 OR BSCache.totalSize > 1.99
```

  `totalSize` is Big and Small's own accumulated body size, fed by `SM_BodySizeOffset` and
  `SM_BodySizeMultiplier`. That closes the loop with the XML: `GeneDef
  BS_GiantWeaponWielder` → `forcedTraits: BS_Giant` → permission regardless of size,
  exactly as its description claims. The frame genes grant `BS_Giant` the same way *and*
  clear the threshold on size.
- The live refusal string is `BS_LacksRequiredClassTag` ("Race cannot equip this class of
  items"). ⚠️ `BS_PawnIsNotAGiant` ("Pawn is not giant") is a **dead language key** — it
  appears in no assembly's user-string heap. Do not go looking for it in a log.

### ⚠️ A third weapon class is declared and NOT restricted

`RBM_HerculeanClass` (Roo's Minotaur Xenotype) is a `WeaponClassDef` on **8 weapons**, but
no `ItemRestrictionDef` lists it. **Those 8 weapons are therefore open to every pawn in the
game.** That is upstream's defect, not ours, and it costs us nothing — but do not assume a
`weaponClasses` entry implies a restriction.

### 🔑 What this means for the question as asked

| | giant weapons (23) | warcasket / heavy weapons (15) |
|---|---|---|
| marker on the weapon | `weaponClasses: BS_GiantWeapon` | `VEF.Weapons.HeavyWeapon` modExtension |
| size threshold | **yes — `totalSize > 1.99`** | **none. There is no size field in the extension at all** |
| trait/gene route | `BS_Giant` trait | `VFEP_WarcasketTrait`, `BS_Giant`, `RBM_Herculean_Trait`; or the genes `VQEA_Enormous`, `AG_ToughSinews` |
| enforced at | `EquipmentUtility.CanEquip` **and pawn generation** | `EquipmentUtility.CanEquip` |
| who patched it | Big and Small — Framework | VFE-Pirates, then patched by 3 other mods |

---

## 2. THE SIZE GENES, AND THE TRAP IN THEIR NAMES

Big and Small and Vanilla Expanded Framework each ship **two** body-size stats whose names
differ by one word:

```
MECHANICAL   SM_BodySizeOffset   SM_BodySizeMultiplier      "affects a variety of mechanics"
             VEF_BodySize_Offset VEF_BodySize_Multiplier
COSMETIC     SM_Cosmetic_BodySizeOffset   SM_Cosmetic_BodySizeMultiplier    sprite scale only
             VEF_CosmeticBodySize_Offset  VEF_CosmeticBodySize_Multiplier
             SM_HeadSize_Cosmetic         VEF_HeadSize_Cosmetic
```

Measured over all 3845 GeneDefs:

- **23 genes** move a mechanical size stat (or `bodySizeFactor` / `sizeByAge` in a
  modExtension).
- **22 more** move only a Cosmetic twin, and change nothing else about the pawn.
- ⛔ Matching the substring `BodySize` anywhere in a gene returns **562** and is almost
  entirely `renderNodeProperties` scaling. That filter is useless; the audit matches the
  exact stat defName instead.

The mechanical set, largest first (net adult bodySize starting from a human's 1.0):

| gene | mod | net size |
|---|---|---|
| `TitanFrame` | Big and Small — Genes & More | 4.0 |
| `GreatOgreFrame` | Big and Small — Genes & More | 3.0 |
| `JotunFrame` | Big and Small — Genes & More | 2.5 |
| `OgreFrame` (+`_Astrogene`) | Big and Small — Genes & More | 2.0 |
| `VQEA_Enormous` | Vanilla Quests Expanded — Ancients | 2.0 |
| `HalfJotunFrame` (+`_Astrogene`) | Big and Small — Genes & More | 1.75 |
| `HalfColossusFrame` (+`_Astrogene`) | Big and Small — Genes & More | 1.7 |
| `XylGiant` (+`_Astrogene`) | Posthuman Drift Titan Xenotype | 1.5 |
| `AG_Shambler_Armoured` | Alpha Genes | 1.5 |
| **`BS_LargeFrame`** (+`_Astrogene`) | Big and Small — Genes & More | **1.4** |
| `RBM_Herculean` (+`_Astrogene`) | Roo's Minotaur Xenotype | 1.3 |
| `BS_SmallFrame` · `DwarfFrame` | Big and Small — Genes & More | 0.65 |
| `GnomeFrame` · `BS_RabbitFrame` | Big and Small — Genes & More | 0.4 |
| `BS_AriettyFrame` | Big and Small — Genes & More | 0.15 |
| `BS_EndlessGrowth` | Big and Small — Genes & More | grows with age (curve; the dump strips the points) |

**`BS_LargeFrame` (+0.4) is the "big & tall" gene the owner's question is reaching for.**
It is the smallest step that reads as genuinely large without turning a species into an
ogre. Everything above it is a monster-scale frame.

### 🔴 Every one of our 70 Star Wars races is mechanically bodySize 1.0

`RimMandrake_BodySizeGene_big` / `_bigger` / `_biggest` / `_small` / `_smaller` all write
`SM_Cosmetic_BodySizeOffset` (+0.2 / +0.5 / +0.7 and the negatives). They scale the sprite
and nothing else. Herglic's `Outland_BodyScale_Large` is the same kind of gene from Outland
Genetics.

⇒ **To every mechanic in the game — health scale, carrying capacity, food, melee, the lot —
a Wookiee, a Hutt, a Gamorrean, an Ewok and a Jawa are currently the same size.** That is a
separate defect from the weapon question, and it is the owner's call whether it is one at
all: identical mechanical size is defensible as a balance decision, but it is currently
undocumented and looks like an oversight.

Across the whole stack, **21 of 139** xenotypes carry a real size gene, and all but three
are Big and Small's own Jotun / Ogre / Troll / Titan / Dwarf / Gnome races. The other three
are `RBM_Minotaur`, `XylTitan` and `BS_FrostJotunInBlue`.

---

## 3. THE FOUR LEVERS, AND WHAT EACH ACTUALLY BUYS

⛔ **Recommend, do not apply — every one of these is the owner's call.**

| lever | what it does | what it costs |
|---|---|---|
| **1. `BS_GiantWeaponWielder`** on a xenotype | grants the `BS_Giant` trait → **both** gates open: all 23 giant weapons and all 15 warcasket weapons. **No size change at all.** | `biostatCpx 1`, `biostatMet 0`. The cheapest thing in this table, and the species stays exactly the size it is. |
| **2. `BS_LargeFrame`** on a xenotype | +0.4 real body size (1.0 → 1.4): health scale, carry, melee, food | ⛔ **unlocks nothing.** 1.4 is under the 1.99 bar, and the gene grants no trait. Take this one only because the species *should be bigger*, never to unlock a weapon. |
| **3. `OgreFrame` or heavier** | +1.0 → 2.0, which clears the bar on size alone, and the frame genes also force `BS_Giant` | 🔴 **ogre scale.** Twice a human's mass, with the food bill and the apparel problems to match. Right for a Jotun; wrong for anything in Star Wars. |
| **4. Add our own gene to the allow-lists** | patch `supportedGenes` on the 15 `HeavyWeapon` extensions to admit a gene of ours | most control, most maintenance — and it does nothing for the 23 giant weapons, which read `weaponClasses` instead |

🔑 **Lever 1 is the answer to the question as the owner asked it.** If the goal is "let this
species wield big weapons", nothing needs to become bigger, and nothing needs patching.
✅ **Lever 2 is a separate and legitimate question** — whether our species should have real
sizes at all — and it should be ruled on separately, not smuggled in to pass a weapon check.

---

## 4. THE SHORTLIST — all 139 xenotypes, judged once each

⛔ **Recommend, do not apply.** Every row is the owner's call.

Judged on the FICTION, not on the numbers, as the item required. Regenerate with
`python3 src/RimMandrake/Utils/xenotype_size_audit.py shortlist --markdown` — the verdicts
live in that file as data, so a change of mind is a one-line edit and not a rewrite.

| verdict | means |
|---|---|
| **STRONG** | canonically large AND built to fight. Give it `BS_GiantWeaponWielder`. |
| **PLAUSIBLE** | arguably large; the owner could go either way |
| **SPECIAL** | big, but a giant weapon still reads wrong |
| **TALL NOT BIG** | tall and slight. Tall is not big, and a giant frame would misrepresent it |
| **ALREADY BIG** / **ALREADY SMALL** | carries a mechanical size gene already |
| **HUMAN SCALE** | ours, near-human in the fiction, no reason to be larger |
| **NEVER** | canonically small. Not a candidate whatever the numbers say |
| **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |

### 🔑 The nine to rule on first

`RimMandrakeWookiee` · `RimMandrakeGamorrean` · `Jawa_Xeno_Gamorrean` · `RimMandrakeHerglic` ·
`RimMandrakeTrandoshan` · `RimMandrakeTogorian` · `RimMandrakeLasat` · `RimMandrakeFeeorin` ·
`RimMandrakeSithMassassi`

One line each on the xenotype's `genes` list adds `BS_GiantWeaponWielder`. Nothing else changes.

| xenotype | mod | size now | verdict | why |
|---|---|---:|---|---|
| `Jawa_Xeno_Gamorrean` | Jawa Patches (local) | 1.0 | **STRONG** | our own Gamorrean variant -- same call as RimMandrakeGamorrean, and it already carries the cosmetic big gene |
| `RimMandrakeFeeorin` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | tall, heavily muscled and long-lived; grows stronger with age |
| `RimMandrakeGamorrean` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | the def's own text says 'tall, strong bipeds'; porcine brutes hired as muscle |
| `RimMandrakeHerglic` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | the def calls them 'hulking' and says they 'hit like a wrecking ball' |
| `RimMandrakeLasat` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | over 2 m and famously powerful in melee |
| `RimMandrakeSithMassassi` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | the Sith war caste -- bred tall and heavily muscled for exactly this |
| `RimMandrakeTogorian` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | the def's own text: 'large, feline beings' |
| `RimMandrakeTrandoshan` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | 2 m reptilian trophy hunters; large and built for violence |
| `RimMandrakeWookiee` | RimMandrake - Star Wars Races | 1.0 | **STRONG** | 2.1 m and the galaxy's byword for strength; the single most obvious candidate |
| `RimMandrakeAqualish` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | burly and thickset; frequently cast as heavies |
| `RimMandrakeCathar` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | large athletic felinoids, though closer to human height than to a giant |
| `RimMandrakeChagrian` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | tall and solidly built, though not warriors by disposition |
| `RimMandrakeGungan` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | tall amphibians, but rangy rather than heavy |
| `RimMandrakeKaleesh` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | formidable warriors, but canonically near human height -- the fighting is the argument, not the size |
| `RimMandrakeKlatoonian` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | the def's own text: 'possessed a strong build, which made them useful laborers' |
| `RimMandrakeNelvaanian` | RimMandrake - Star Wars Races | 1.0 | **PLAUSIBLE** | lupine and powerfully built; a defensible large frame |
| `RimMandrakeHutt` | RimMandrake - Star Wars Races | 1.0 | **SPECIAL** | canonically the largest species we field by a wide margin, so a size gene is RIGHT -- but a Hutt is a sessile slug with vestigial arms and could not swing a giant hammer. Size yes, giant weapons no. |
| `RimMandrakeCerean` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | the height is in the cranium; the body is ordinary |
| `RimMandrakeIthorian` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | tall, but gentle herbivore pacifists; arming one with an ogre club is against the species |
| `RimMandrakeKaminoan` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | 2.3 m and famously frail -- tall is not big, and a giant weapon on one would read as a joke |
| `RimMandrakeKelDor` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | slight build under the mask |
| `RimMandrakeMuun` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | the def says it: 'tall thin humanoids'. Bankers. |
| `RimMandrakeNagai` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | the def says 'tall and agile' -- agility is the point, mass is not |
| `RimMandrakePyke` | RimMandrake - Star Wars Races | 1.0 | **TALL NOT BIG** | tall and spindly criminal caste |
| `BS_BrokenTitan` | Big and Small - Races | 4.0 | **ALREADY BIG** | already bodySize 4.0 via TitanFrame |
| `BS_Corrupterd_Titan` | Big and Small - Races | 4.0 | **ALREADY BIG** | already bodySize 4.0 via TitanFrame |
| `BS_FireJotun` | Big and Small - Races | 3.25 | **ALREADY BIG** | already bodySize 3.25 via JotunFrame, HalfJotunFrame |
| `BS_FrostJotun` | Big and Small - Races | 3.25 | **ALREADY BIG** | already bodySize 3.25 via JotunFrame, HalfJotunFrame |
| `BS_FrostJotunInBlue` | Big and Small - Genes & More | 3.25 | **ALREADY BIG** | already bodySize 3.25 via JotunFrame, HalfJotunFrame |
| `BS_Jotun` | Big and Small - Races | 3.25 | **ALREADY BIG** | already bodySize 3.25 via JotunFrame, HalfJotunFrame |
| `BS_GreatOgre` | Big and Small - Races | 3.0 | **ALREADY BIG** | already bodySize 3.0 via GreatOgreFrame |
| `BS_Surtr` | Big and Small - Races | 2.5 | **ALREADY BIG** | already bodySize 2.5 via JotunFrame |
| `BS_Ymir` | Big and Small - Races | 2.5 | **ALREADY BIG** | already bodySize 2.5 via JotunFrame |
| `BS_Ogre` | Big and Small - Races | 2.0 | **ALREADY BIG** | already bodySize 2.0 via OgreFrame |
| `BS_Half_Jotun` | Big and Small - Races | 1.75 | **ALREADY BIG** | already bodySize 1.75 via HalfJotunFrame |
| `BS_Hearthguard` | Big and Small - Races | 1.7 | **ALREADY BIG** | already bodySize 1.7 via HalfColossusFrame |
| `XylTitan` | Posthuman Drift Titan Xenotype | 1.5 | **ALREADY BIG** | already bodySize 1.5 via XylGiant |
| `BS_Troll` | Big and Small - Races | 1.4 | **ALREADY BIG** | already bodySize 1.4 via BS_LargeFrame |
| `RimMandrakeAbednedo` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeAnzati` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeArkanian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeBith` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeChiss` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeDathomirian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeDevaronian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeDuros` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeEchani` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeFalleen` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeIktotchi` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeIridonian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeKubaz` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeMimbanese` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeMirialan` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeMonCalamari` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeNautolan` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeNeimoidian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeNikto` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakePantoran` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeQuarren` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeRakata` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeRodian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeSithKissaiPureblood` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeSithZ` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeTaung` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeTogruta` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeTusken` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeTwilek` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeUmbaran` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeWeequay` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeZeltron` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `RimMandrakeZygerrian` | RimMandrake - Star Wars Races | 1.0 | **HUMAN SCALE** | near-human build in the fiction; no reason to be larger |
| `MandrakeJawa` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | the player xenotype, and canonically ~1 m. Never a candidate. |
| `RimMandrakeBothan` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | short and slight |
| `RimMandrakeChadraFan` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | the def's own text: 'meter-tall, rodent-like humanoids' |
| `RimMandrakeDefel` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | small shadow-dwellers |
| `RimMandrakeEwok` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | the def's own text: 'small primitive species', 'diminutive size' |
| `RimMandrakeGand` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | small insectoids |
| `RimMandrakeGeonosianVariants` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | slight winged insectoids |
| `RimMandrakeJawa` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | canonically ~1 m |
| `RimMandrakeOrtolan` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | the def's own text: 'squat, blue-skinned bipeds' |
| `RimMandrakeSelkath` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | modest build |
| `RimMandrakeSnivvian` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | short |
| `RimMandrakeSullustan` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | short |
| `RimMandrakeUgnaught` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | canonically short and stocky labourers |
| `RimMandrakeYoderForceGremlin` | RimMandrake - Star Wars Races | 1.0 | **NEVER** | the Yoda species; tiny by definition |
| `BS_Dwarf` | Big and Small - Races | 0.65 | **ALREADY SMALL** | already bodySize 0.65 via DwarfFrame |
| `BS_Svartalf` | Big and Small - Races | 0.65 | **ALREADY SMALL** | already bodySize 0.65 via DwarfFrame |
| `BS_Gnome` | Big and Small - Races | 0.4 | **ALREADY SMALL** | already bodySize 0.4 via GnomeFrame |
| `BS_Redcap` | Big and Small - Races | 0.4 | **ALREADY SMALL** | already bodySize 0.4 via GnomeFrame |
| `RBM_Minotaur` | Roo's Minotaur Xenotype | 1.3 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Animusen` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Drakonori` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Efreet` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Fleetkind` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Forsaken` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Helixien` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Hiveling` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Lapis` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_MindDevourer` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Mycormorph` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Nereid` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_RandomCustom` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Taukai` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `AG_Wretch` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BS_FleshGolemServant` | Big and Small - Races | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BS_Hearthdoll` | Big and Small - Races | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BS_PilotableFleshGolem` | Big and Small - Races | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BS_TrollAdult` | Big and Small - Races | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BS_TrollOld` | Big and Small - Races | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `BX_Beliar` | Beliar Xenotype | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Baseliner` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Avaloi` | Det's Xenotypes - Avaloi | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Bogleg` | Det's Xenotypes - Boglegs | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Brawnum` | Det's Xenotypes - Brawnum | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Buzzer` | Det's Xenotypes - Buzzers | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Keshig` | Det's Xenotypes - Keshig | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `DV_Venator` | Det's Xenotypes - Venators | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Dirtmole` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Genie` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `HBX_Highborn` | Highborn Xenotype | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Highmate` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Hussar` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Impid` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `KAR_Orc` | Orc Clan + Xenotype | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Neanderthal` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Pigskin` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `PureBlood` | Rimwars:Pureblood Xenotype | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Sanguophage` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Starjack` | Odyssey | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRESaurids_Saurid` | Vanilla Races Expanded - Saurid | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Animakin` | Vanilla Races Expanded - Phytokin | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Archon` | Vanilla Races Expanded - Archon | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Fungoid` | Vanilla Races Expanded - Fungoid | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Gauranlenkin` | Vanilla Races Expanded - Phytokin | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Ocularkin` | Alpha Genes | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `VRE_Poluxkin` | Vanilla Races Expanded - Phytokin | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Waster` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `Yttakin` | Biotech | 1.0 | **NOT OURS** | a third-party xenotype we do not field; out of scope unless the owner says otherwise |
| `guy762_debugxenotype_droid` | Star Wars KotOR Resources and Materials | 1.0 | **NOT OURS** | a debug def from a resource mod; not a species we field |

139 xenotypes, each judged once: 9 STRONG, 7 PLAUSIBLE, 1 SPECIAL, 7 TALL NOT BIG, 14 ALREADY BIG, 33 HUMAN SCALE, 14 NEVER, 4 ALREADY SMALL, 50 NOT OURS


## 5. WHAT THIS AUDIT DOES NOT SETTLE

- **Runtime is not measured.** That `SM_BodySizeOffset` reaches `Pawn.BodySize` is asserted
  by the StatDef's own description and by Big and Small's design, not read off a live pawn.
  A bridge read of a spawned pawn would settle it in one call.
- **A C#-only gene is invisible to the dump.** A gene whose `geneClass` resizes a pawn in
  code, writing no stat and carrying no modExtension, appears in none of these counts.
- **Whether Big and Small's and VEF's size stats stack** when both frameworks are installed
  is UNMEASURED.
- **`HeavyWeaponsSettings` exists in VEF** — a mod setting may disable the heavy-weapon
  restriction globally. Unread.
- **`> 1.99` vs `>= 1.99`** — the constant and the branch were read; the `cgt`/`clt` opcode
  itself was not. `OgreFrame` lands on exactly 2.0, so the distinction is the difference
  between "clears the bar" and "clears it by 0.01". If that edge ever matters, read the
  opcode or spawn one and look.
- ⚠️ **An upstream bug, noted not chased.** `BSCache.RegenerateCache` tests
  `t.def.defName.ToLower().Contains("AG_ToughSinews")` against an already-lowercased
  string, so that branch can never match. It costs us nothing — `AG_ToughSinews` is a
  GENE and reaches the warcasket weapons through `supportedGenes`, which works — but do
  not expect the trait branch to admit it.
- **Only the 1.6 assemblies were read.** The 1.4 / 1.5 copies were not.
- **Whether some other mod grants `BS_GiantWeapon` by a different route** (a `PawnExtension`,
  say) is UNMEASURED. What IS measured is that only one `ItemRestrictionDef` exists in the
  whole stack.

---

## 6. HOW THIS WAS READ, SO IT CAN BE CHECKED

The def numbers all come from the sqlite def dump, queried read-only; every one is
reproducible from `src/RimMandrake/Utils/xenotype_size_audit.py` or from a three-line
query named in the section that uses it.

🔑 **The C# was decoded, not scanned.** No `ilspycmd`, `monodis`, `ikdasm`, `dotnet` or
`mono` exists on this machine, so a PE/CLI metadata reader and an ECMA-335 IL decoder were
written for the job: `#~` tables (TypeDef / MethodDef / Field / MemberRef / TypeRef /
MethodSpec with coded-index widths), the `#Strings` and `#US` heaps, and enough of the IL
to resolve `call` / `callvirt` / `ldfld` / `ldstr` tokens and decode `ldc.r4`. Every quoted
method name, field and constant above came out of that, and the `BS_PawnIsNotAGiant`
absence is a real absence in the user-string heap — ⛔ not a `strings` byte scan, which
CLAUDE.md is right that it could never have proven.
