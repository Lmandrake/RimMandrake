## spec
🔴 **22 combat kinds across 6 of the 8 authored Jawa factions carry NEITHER `apparelRequired`
NOR `apparelTags`**, so they draw from the UNCONSTRAINED GLOBAL apparel pool — and they have
real budgets to spend in it. Measured in capture `2026-08-23T07-12-04Z`:

    Jawa_Helix_Grunt       apparelRequired None  apparelTags None  apparelMoney  700-840
    Jawa_Helix_Leader      None                  None                           1800-2160
    Jawa_Deepwater_Grunt   None                  None                            400-480
    Jawa_Hutt_Grunt        None                  None                            250-300
    Jawa_Wildsteam_Grunt   None                  None                            150-180
    Jawa_Droid_Grunt       None                  None                            120-144
    Jawa_Geonosian_Grunt   None                  None                             60-72

| faction | constrained | unconstrained |
|---|---|---|
| `Empire` | 15 / 15 | 0 ✅ |
| `Jawa_Junkers` | 4 / 4 | 0 ✅ |
| `Jawa_IndigenousTribes` | 7 / 7 | 0 ✅ |
| `Jawa_HuttCartel` · `Jawa_AscendantHelix` · `Jawa_DeepwaterCompact` · `Jawa_WildsteamClan` | 2–4 | **4 each** 🔴 |
| `Jawa_GeonosianFoundryHive` | 0 / 4 | **4** 🔴 |
| `Jawa_FreeDroidEnclaves` | 0 / 6 | **6** 🔴 |

In every case it is exactly the Grunt/Heavy/Leader/Specialist combat quartet, present in
**both** the `Combat` and `Settlement` groupMakers.

## 🔑 THE DESIGN ALREADY EXISTS — DO NOT REDESIGN IT

**`design/Jawa/worldbuilding/faction_equipment_clusters.md`** (CHECK, 2026-08-22, on the
owner's 01:17 instruction to *"cluster the weapon technologies, apparel types and special
items, associate factions with the clusters, and make different factions want strongly
different things"*), under `faction_equipment_guidance.md` which settled the model.

Its **Finding 2** reached this item's conclusion a day earlier: *"823 apparel tags have usable
gear behind them. The 68 authored kinds ask for FIVE."*

⇒ **This item is the IMPLEMENTATION of that document's PART 3 item 3** — *"Give each faction
its apparel cluster. One tag family each, replacing the shared `IndustrialBasic`. This is the
single highest-visibility change on the list."* The per-faction table is already written:

| faction | cluster | tags |
|---|---|---|
| Empire | Imperial trooper plate / officer uniform | `ImperialStormtrooper` `ImperialArmy` `ImperialOfficer` |
| Hutt Cartel | merc composite + noble regalia on the boss | `SaV_apparel_huttgoon` `KotORArmor_mid` `Royal` |
| Free Droid Enclaves | droid chassis + modules | `KotORDroidArmorT1/T2/T3` `DroidArmor` |
| Wildsteam | tribal hides | `Neolithic` `ORBoneArmour` `ORChitinArmour` |
| Deepwater Compact | environmental suits & breathers | `EVA` `Vacsuit` `KotORHeadband_gasmask` |
| Geonosian | chitin + lab apparel, `apparelMoney` 60 | `BMT_Apparel_Chitin*` |
| Ascendant Helix | merc composite, top tier only | `PrestigeCombatGear` `KotORArmor_heavy` |
| Blackstar | merc & composite, deliberately mixed | `SaV_outfit_merc` `MNCFactionArmor` `KotORArmor_*` |
| Trade Moot | desert robes, `apparelRequired` robe + hood | `ORJawa` `SaV_apparel_jawa` `guy762_JawaHood` |
| Junkers | warcasket | `WarcasketAll` `WarcasketVeteran` |
| Deep Desert | desert robes / veiled faces | `ORTusken` `SaV_apparel_tusken` `GS_SandP_*` |
| Homestead | salvager junk + desert robes | `Outlander` `Western` `ORScrapper` |

✅ **All six unconstrained factions are in that table.** The work is to write those tags onto
the kinds, not to decide what they should be.

## Watch out
- ⛔ **There is NO apparel equivalent of `WeaponTags_Renormalise.xml`.** Apparel has **4**
  patch operations in total, all one-pawn fixes, so this cannot be done the way weapons were.
- ⛔ **The vocabulary will not carry a blind sweep:** 823 distinct tags of which **503 have
  exactly ONE carrier**, and **195 of 855** apparel ThingDefs carry no tags at all, so they
  are unreachable via `apparelTags` and need `apparelRequired`.
- 🔑 **Nothing spawns naked — it spawns GENERIC**, which is why this never surfaced as an
  error. 93 of the 112 tag-carrying authored kinds name the single vanilla tag
  `IndustrialBasic`. A clean log proves nothing here; it is a LOOK defect.
- ⚠️ The KotOR Jawa robes carry `SaV_apparel_jawa` and **no authored pawnkind names that
  tag**; `apparelRequired` is currently the only route to them.
- ⚠️ **One contradiction the design flags and hands to DECIDE, not BUILD:** measured
  `Insulation_Heat` makes the hazard warcasket (333) the best heat protection on the planet,
  so on a dayside world the Junkers become the best-protected faction — against the roster's
  intent that warcaskets carry a heat penalty. Do not resolve that while implementing.

## verify
Every one of the 22 kinds carries `apparelTags` or `apparelRequired` naming its faction's
cluster from the table above, measured in a fresh capture; and no authored combat kind is
left with `IndustrialBasic` as its only apparel tag.

## criteria
A raid from each of the six factions is visually distinguishable at a glance, and no Jawa
turns up in jeans.
