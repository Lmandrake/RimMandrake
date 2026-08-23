# AUTHORED_FACTIONS_WEAR_ANYTHING_1 — implementation, BUILD, 2026-08-23

Implements PART 3 item 3 of `design/Jawa/worldbuilding/faction_equipment_clusters.md`:
"Give each faction its apparel cluster. One tag family each, replacing the shared
IndustrialBasic."

## what changed
`src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` — **35 PawnKindDefs**
gained `<apparelTags>`, across 9 faction families. All 35 previously had NEITHER
`apparelTags` nor `apparelRequired`. Deployed, VERIFIED in sync.
validate_patch.py against the full 578-mod load set: **0 errors, 0 warnings**.

## 🔴 THREE TAGS IN THE DESIGN TABLE DO NOT EXIST, and writing them would have
## spawned pawns NAKED. Measured against capture 2026-08-23T07-12-04Z before writing:

    BMT_Apparel_Chitin        0 carriers   (no BMT_Apparel* tag exists at all)
    BMT_Apparel_ChitinHelmet  0 carriers
    BMT_Apparel_ChitinArmor   0 carriers
    GS_SandP_*                0 carriers   (no such family)

The design's own Finding 7 warned about exactly this class: "25 apparel tags are
requested by kinds and carried by nothing."

**Substituted, staying inside the stated idiom:**
- Geonosian "chitin (natural) + lab apparel" -> `ORChitinArmour` (3 carriers, the only
  real chitin family) + `KotORClothing_civilian_prole` (4, cheapest 20) for the lab half.
- Deep Desert "desert robes / veiled faces" -> `ORTusken` (3) + `SaV_apparel_tusken`
  (2, cheapest 20). `GS_SandP_*` dropped.

## 🔴 THE AFFORDABILITY RULE, which is the trap this project keeps hitting
Every kind's tag set must contain at least one tag with a PRICED carrier at or below its
`apparelMoney` max — otherwise the cluster is unreachable and the pawn spawns with less or
nothing. This is the apparel form of `WEAPON_BUDGET_BELOW_POOL_FLOOR_1`, filed hours earlier
against the weapon layer, and my first draft of this assignment hit it three times.

Verified after the edit: **0 kinds have priced options but none affordable.**

**Two numbers changed to satisfy it, and only two:**

    Jawa_Droid_Grunt    apparelMoney 120~144 -> 180~216
        KotORDroidArmorT1's cheapest carrier is guy762_DroidArmorLte at 175.
        At 144 the entire cluster was unreachable.
    Jawa_Droid_Leader   apparelMoney 400~480 -> 600~720, and T1 added as a floor
        T3 starts at 1250 and T2 at 500; at 480 neither was reachable. 600~720 buys
        T2 (guy762_DroidArmorMid, 500), which also restores the tier ladder over the
        Grunt's T1.

**Tier split introduced for Helix**, because `KotORArmor_heavy` starts at 2500:
Grunt/Heavy get `PrestigeCombatGear` + `KotORArmor_mid`; Specialist and Leader get
`KotORArmor_heavy` as well. The "merc composite, top tier only" idiom is kept for the
ranks that can pay for it rather than written onto ranks that cannot.

## ⚠️ WHAT IS UNMEASURED, and must not be read as broken
12 kinds (all 4 Empire, all 4 Wildsteam, all 4 Junkers) have pools whose carriers are
ENTIRELY unpriced: Outer Rim, warcaskets and vanilla stuffables compute MarketValue at
runtime from costList + WorkToMake. Their affordability is **UNMEASURED, not zero**.
Empire and Junkers were already constrained and working before this change, so nothing
regressed; Wildsteam's bone/chitin/Neolithic kit is new and unproven on price.

## verify — what a load must show
- No authored combat kind spawns in `Apparel_Pants` / `Apparel_BasicShirt` (the
  `IndustrialBasic` signature).
- A raid from each of the six previously-unconstrained factions is visually distinct.
- ⛔ No log string proves any of this. It is a LOOK defect and it is settled on screen.


---

## 🔴 SECOND PASS — the owner asked two questions and both found defects

**Owner, 2026-08-23 01:36:** *"Shouldn't the prices be in our ThingDef dump then... weren't
they computed, then written? Anything else we should audit?"*

### 1. Why "unpriced" — and it is NOT a dump defect

A def dump captures **`statBases`, the AUTHORED list**. `MarketValue` appears there only when
a modder wrote it. Measured:

    guy762_DroidArmorLte   statBases HAS MarketValue 175          -> authored
    OuterRim_BoneCuirass   no MarketValue; costList 60 Durasteel  -> DERIVED at runtime
                           + 2 ComponentHypertech, WorkToMake 8000
    Apparel_Parka          no MarketValue; costStuffCount 80,     -> DERIVED from the STUFF
                           stuffCategories Fabric/Leathery           chosen at generation

⇒ **It cannot be in the dump, at any capture time.** `StatWorker_MarketValue` computes it per
THING, and for a stuffable the answer depends on which material that particular instance is
made of. There is no single value for the def to carry.

✅ **But it is COMPUTABLE offline, and "UNMEASURED" was too weak an answer.** Summing the
costList components' own MarketValue and adding `WorkToMake * 0.0055` reproduces RimWorld's
own method:

    OuterRim_BoneCuirass      636      OuterRim_ChitinCuirass    918
    OuterRim_ImperialArmyCuirass 918   Apparel_Parka (cheap stuff) 196

**This converted 12 UNMEASURED kinds into measured ones.** Wildsteam, which I had flagged as
unproven, is fine — `Neolithic` stuffables come in around 36 and give full coverage.

### 2. The audit I had NOT run, and it found five real failures: BODY LAYERS

A cluster can be affordable and still leave a pawn in underwear, because a tag family may be
all helmets and cuirasses and no trousers. Checking `apparel.bodyPartGroups` over each kind's
AFFORDABLE set:

    Jawa_Hutt_Grunt         torso -  legs -   (SaV_apparel_huttgoon is hats and helmets;
    Jawa_Hutt_Heavy         torso -  legs -    KotORArmor_mid's torso pieces cost > budget)
    Jawa_Hutt_Specialist    torso Y  legs -
    Jawa_Blackstar_Grunt    torso -  legs -   (MNCFactionArmor starts at 3750)
    Jawa_Blackstar_Specialist torso Y legs -

**Fixed in idiom, not with a generic fallback:**
- Hutt goons get `SaV_apparel_thug` (scum clothing, cheapest 10) — they are thugs.
- Blackstar get `KotORClothing_undersuit` (bodysuits, 20) — an undersuit under merc plate.
- ⛔ Added to the FIVE failing kinds only. The Hutt Leader keeps `Royal` regalia without cheap
  scum clothing in its pool, and the Blackstar Leader keeps `MNCFactionArmor`.

✅ **Re-verified: 0 kinds lack an affordable torso AND legs.** Deployed, VERIFIED in sync,
validate_patch.py 0 errors 0 warnings.

### Still not audited, and named so nobody assumes otherwise
- **Head coverage** is reported but not enforced — Geonosians read `head -`, which may be
  correct (insectoid heads) or may be the beetle helm the design asks for. DECIDE's call.
- **`apparelDisallowTags`** for the design's taboos is PART 3 item 4 and is not built.
- **Quality**: `minApparelQuality Excellent` on Helix and `Good` on Wildsteam/Deepwater raises
  effective cost above these estimates. The estimates are BASE values; a quality multiplier
  applies on top, so the thin tiers may be thinner in play than they read here.
