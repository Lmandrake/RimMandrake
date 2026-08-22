<!-- status: draft -->
# Faction equipment clusters — the palette, and who draws from it

_CHECK, 2026-08-22. Owner's instruction, 01:17: cluster the weapon technologies, apparel
types and special items, associate factions with the clusters, and make different factions
want strongly different things._

> 🔑 **This is the layer BELOW `faction_equipment_guidance.md`, not a replacement for it.**
> That document settled the model — equipment lives on `PawnKindDef`, per faction by role,
> tech and money as independent axes — and gave each faction a sentence saying what its gear
> should SAY. **It never named a single def or tag.** This file is the bridge from that
> prose to defs that exist in the loaded game.

---

## PART 0 — the diagnostic, before any design

Measured 2026-08-22 against the 2026-08-21 def dump and the live Cherry Picker kill list.
**"Usable" excludes cut defs**, because Cherry Picker empties `weaponTags` at load and a cut
weapon can never be equipped by generation.

    weapon ThingDefs      771     cut 186     usable 585
    distinct weaponTags with a usable weapon behind them        389
    distinct apparel tags with usable apparel behind them       823

### 🔴 Finding 1 — the WEAPON axis is already differentiated, and it is good

The 68 authored `Jawa_*` kinds request **37 distinct `weaponTags`**, and the split by
faction reads as deliberate design rather than defaults:

| faction group | tags it asks for | what that says |
|---|---|---|
| DeepDesert | `ORTuskenMelee` · `ORMeleeBlunt` · `NeolithicMeleeAdvanced` · `SaV_tusken` | gaderffii sticks and the Tusken Cycler |
| TradeMoot | `Jawa_IonWeapon` · `Jawa_IonWeaponLight` · `KotORRanged_ion` · `SaV_jawaheavy` | the ion signature, exactly as canon has it |
| Empire | `ORImperialStandard` · `ORImperialLight` · `ORImperialHeavy` · `ORImperialSniper` · `ORHeavyWeapon` | one supply chain, four grades |
| Geonosian | `KotORRanged_sonic` + rare/legendary | sonic, as specified |
| Wildsteam | `KotORBowcaster` · `ORVibroweapon` · `ORMeleeSharp` | bowcasters and good blades |
| Junkers | `NeolithicMeleeBasic` · `ORMeleeBlunt` · `KotORRanged_weak` · `SimpleGun` | scrap |
| Blackstar | `KotORRanged_rare/strong/legendary` · `ORPistol` · `ORSniper` | bought, personal, expensive |
| Hutt | `KotORRanged_weak` **through** `legendary` | ostentation, unevenly spent |
| Droid | `ORDroidWeapon` | integral |

**No empty pools among them.** ⇒ Nobody needs to redo the weapon layer. It works.

### 🔴 Finding 2 — the APPAREL axis is essentially unbuilt

**823 apparel tags have usable gear behind them. The 68 authored kinds ask for FIVE.**

    IndustrialBasic          supply  20   asked by 14 kinds
    WarcasketAll             supply  51   asked by  4 kinds
    Neolithic                supply  12   asked by  3 kinds
    SaV_outfit_gamorrean     supply   3   asked by  2 kinds
    SaV_apparel_huttgoon     supply   5   asked by  1 kind

⇒ **Fourteen kinds across many factions all wear generic vanilla `IndustrialBasic`.** The
Empire, the Compact, the Helix and the Homestead are, on screen, the same people.
Meanwhile the pools that would separate them are sitting unused: `ImperialApparel` (21),
`KotORArmor_light` (16) / `_mid` (20) / `_heavy` (16), `EVA` (25), `Royal` (20),
`Warcasket` (15), `PrestigeCombatGear` (22).

🔑 **This is where the owner's wish lives.** Weapons already differ; silhouettes do not.

### 🔴 Finding 3 — every "flavour" lever the guidance doc specifies is at zero

`faction_equipment_guidance.md` assigns a quality clamp to each of the twelve factions —
`forceNormalGearQuality` for the Empire, *min Excellent* for the Helix, *max Poor→Normal*
for the Jawa, *armour unclamped* for the Junkers. Measured across the 68 authored kinds:

| lever | kinds using it |
|---|---|
| `apparelMoney` | **68 / 68** ✅ |
| `techHediffsMoney` | **68 / 68** ✅ |
| `apparelRequired` | 12 / 68 |
| `specificApparelRequirements` | 5 / 68 |
| `techHediffsTags` | 15 / 68 |
| **`forceWeaponQuality`** | **0 / 68** 🔴 |
| **`apparelColor`** | **0 / 68** 🔴 |
| **`apparelDisallowTags`** | **0 / 68** 🔴 |
| **`inventoryOptions`** | **0 / 68** 🔴 |

⇒ The money numbers landed. **The quality clamps, the faction colours, the taboos and the
carried items were specified and never built** — and those are exactly the four fields that
turn "different budget" into "visibly different culture".

### ⚠️ Finding 4 — one faction's stated identity has no defs behind it

`faction_equipment_guidance.md` gives the **Deepwater Compact** *"defensive and aquatic —
harpoons, pressure weapons, nothing built to march"*. Searched the whole usable set for
harpoon / speargun / trident / net / pressure / dive / aquatic: **zero**. The only
spear-shaped ranged weapons in the game, `AM_Spear68A` and `AM_Spear68C` (6.8 spear rifle),
are **on the Cherry Picker kill list**.

⇒ Three routes, and the cheapest is the first: **un-cut the two spear rifles** and give them
a Compact-only tag; or re-found the Compact's identity on something that exists (they
currently draw `ORVibroweapon` + KotOR mid-tier, which reads as generic); or author new
weapons, which is a mod-build, not a patch.

### ⚠️ Finding 5 — nine authored kinds are fielded by nothing
All four `Jawa_DeepDesert_*`, all four `Jawa_Blackstar_*`, and `Jawa_Empire_Leader` appear
in no `FactionDef`'s `pawnGroupMakers`. Filed as `ORPHANED_ROLE_KINDS_UNFIELDED_1`.
**A cluster assignment for those factions changes nothing until they are wired in.**

---

_Parts 1–3 (the weapon clusters, the apparel clusters, and the faction↔cluster matrix with
taboos) follow once the palette survey and the independent critique return._
