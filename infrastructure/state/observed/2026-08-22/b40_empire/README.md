# B40 — the cataphracts are gone, and only one Empire kind looks Imperial

**CHECK, 2026-08-22 ~02:30 PDT. 578 mods, fresh dev-quicktest map.** Raid composition read
off the `Empire` FactionDef in the 2026-08-21 dump; appearance read from 12 live spawns.

## The named criteria — MET

| check | reading |
|---|---|
| `fixedName` | **`Galactic Empire`** ✅ |
| `leaderTitle` | **`Emperor`** ✅ |
| `techLevel` | `Ultra` (vanilla's own value, unchanged) |
| **common raid, commonality 100** | `Jawa_Empire_Grunt` · `_Heavy` · `_Specialist` — **no cataphracts** ✅ |
| **rare raid, commonality 10** | the same three **+** `OuterRim_ImpRangeTrooper` · `OuterRim_ImpDeathTrooper` · `OuterRim_ImpISBAgent` ✅ |

⭐ **Both raid tiers were checked, including the commonality-100 one the item warns
"nobody looks at".** Neither contains a cataphract. The item's core fear is unfounded.

## ⚠️ But the SETTLEMENT group was never reskinned
`pawnGroupMakers[3]`, `kindDef: Settlement`, commonality 100:

    Empire_Fighter_Trooper · Empire_Fighter_Janissary · Empire_Fighter_Cataphract
    Empire_Fighter_Champion · Mech_Scyther · Mech_Lancer · Mech_CentipedeBlaster
    Mech_CentipedeBurner · Mech_Centurion · Mechanitor · RBM_MinotaurGuardianHigh

⇒ **A player who attacks an Imperial settlement meets Royalty janissaries, cataphracts and
a Minotaur Guardian.** Out of scope for this item's wording — it says *raids* — but it is
the same reskin left half-done, and it is where the cataphracts actually still live.

⚠️ `Jawa_Empire_Leader` appears in **no** group, consistent with
`ORPHANED_ROLE_KINDS_UNFIELDED_1`.

## 🔴 "Raids with stormtroopers" is one kind in three

12 live spawns in faction `Empire`, apparel read back:

| kind | what it wore |
|---|---|
| **`Jawa_Empire_Grunt`** | ✅ **`OuterRim_StormtrooperCuirass` + `OuterRim_StormtrooperHelmet`, 4 of 4** — its `apparelRequired` works exactly |
| `Jawa_Empire_Heavy` | 🔴 no Imperial anything. Psyfocus shirt, bone pauldrons, armbands, a parka, a **Siegebreaker warcasket**, **`guy762_Clothing_RebelCamoII`**, a rebel cap |
| `Jawa_Empire_Specialist` | 🔴 warcasket pieces, **`GS_SandP_Hood`** (a Sandpeople hood), **`guy762_SithMask_marauder`**, a poncho, suspenders, two backpacks, and an `Apparel_Blindfold` |

Weapons are fine on all three — Imperial blasters throughout (`OuterRim_EC17Blaster`,
`DE10`, `DG29`, `E22BlasterRifle`, `T21RepeatingBlaster`), one bare roll each on Grunt and
Heavy.

🔑 **The cause is exactly Finding 2 of `faction_equipment_clusters.md`:** only the Grunt
carries `apparelRequired`. `Jawa_Empire_Heavy` and `_Specialist` have none and no
faction-specific `apparelTags`, so generation dresses them from the whole 723-def pool —
which on this mod list means rebel camo and Tusken hoods on Imperial troops.

⇒ **The Empire is the faction the guidance doc calls "uniform. Mass-produced, identical, no
personality… you are fighting a supply chain."** Two thirds of it currently reads as a
jumble sale. The fix is one `apparelRequired` block per kind, or the `ImperialApparel` /
`ImperialStormtrooper` tag family (21 usable defs) on `apparelTags`.

## Verdict
The item's stated criteria pass. Recorded **partial** rather than pass because "raids with
stormtroopers" is true of one kind in three, and because the settlement group still fields
the cataphracts the item was created to remove.
