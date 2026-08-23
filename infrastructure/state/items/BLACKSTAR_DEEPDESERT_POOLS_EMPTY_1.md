## spec
🔴 **Eight bare-handed spawns are OUR defect, and they are concentrated in two families.**
DECIDE ruled 2026-08-22 that pool integrity is an **absolute** bar — a pawn that spawns
bare while its backstory permits violence is a defect, and the acceptable count is **zero**.
Ruling: `design/Jawa/worldbuilding/pawnkind_roster.md`, *"Who may arrive unable to fight"*.

Measured 2026-08-21, 240 spawns
(`observed/2026-08-21/armed_sweep_48/rolls.json`):

| family | rolls | bare | pacifist | unexplained |
|---|---|---|---|---|
| **Blackstar** | 20 | 5 | 0 | **5** |
| **DeepDesert** | 20 | 4 | 1 | **3** |
| the other ten families | 200 | 18 | 18 | **0** |

Six kinds carry all eight:
`Jawa_Blackstar_Heavy · _Leader · _Specialist`, `Jawa_DeepDesert_Grunt · _Leader · _Specialist`.

⭐ **Ten of twelve families are clean. Do not work this as a roster-wide tag problem.**

⚠️ **The same two families are the ones `ORPHANED_ROLE_KINDS_UNFIELDED_1` found fielded by
no FactionDef.** Suggestive, but they are different defects — unfielded is wiring, an empty
pool is tags. Fixing one leaves the other.

⚠️ `ORPHANED_ROLE_KINDS_UNFIELDED_1` reports the DeepDesert kinds spawning gaderffii sticks
and Tusken cyclers on hand-spawn. Both measurements are live. Reconcile them before
concluding the pool is empty rather than intermittently empty.

## verify
For each of the six kinds, resolve its `weaponTags` against the surviving item set
post-cut and post-patch, then spawn 20 and count bare rolls with a non-pacifist backstory.

## criteria
Zero unexplained bare rolls across the six kinds in 20 spawns each, with the other ten
families' bare counts unchanged.

## watch out
⚠️ Likely a casualty of `RESTORE_VANILLA_GUN_TAGS_1` / the vanilla firearm cut. Check the
tag→surviving-item index rather than the raw mod XML.

---

## 🔴 MEASURED OFFLINE 2026-08-23 by BUILD — **the hypothesis in "watch out" is WRONG**

> *"Likely a casualty of `RESTORE_VANILLA_GUN_TAGS_1` / the vanilla firearm cut."*

**It is not.** Tag → surviving-item index rebuilt from the def dump (post-inheritance,
post-PatchOperation, post-dedup) and filtered against the live Cherry Picker kill list:

    535 ThingDefs carry a non-empty weaponTags
    390 distinct tags — and ALL 390 have at least one SURVIVING carrier
    not one of the six kinds' tags was emptied by a cut

⇒ **Nothing is cut and no tag is empty. The defect is AFFORDABILITY.** These kinds ask for
weapons they cannot pay for.

| kind | budget ≤ | tag | surviving carriers | cheapest |
|---|---|---|---|---|
| `Jawa_Blackstar_Leader` | **2160** | `KotORRanged_legendary` | 11 | 🔴 **12000** — 5.5× the budget |
| `Jawa_Blackstar_Specialist` | **1320** | `KotORRanged_rare` | 13 | 🔴 **12799** — ~10× the budget |
| `Jawa_Blackstar_Heavy` | 840 | `KotORRanged_strong` | 13 | 900 — just over, **but** its other tag `SWKotORWeaponCategoryTag_heavyranged` has one at **550**, so this kind is FINE |
| `Jawa_DeepDesert_Grunt` | 180 | `NeolithicMeleeAdvanced` | 23 | 120 ✅ |
| `Jawa_DeepDesert_Leader` | 600 | `NeolithicMeleeAdvanced` | 23 | 120 ✅ |
| `Jawa_DeepDesert_Specialist` | 2400 | `SaV_tusken` | 2 | 1977 ✅ |

**The KotOR "rare" and "legendary" tiers are 10× a mid-tier budget.** A kind whose only
affordable tag is one it cannot reach rolls bare — which is exactly the observed Blackstar 5.

## ⚠️ UNMEASURED, and it decides the other half
`ORPistol` (8 carriers) and `ORSniper` (8 carriers) — the second tag on both broken kinds —
**all report `MarketValue: null` in the dump.** They are Outer Rim weapons priced by
`costList`, and RimWorld derives MarketValue from it at load; the dump does not serialise the
derived value. ⇒ **Whether those two tags are affordable cannot be answered offline.** If they
are, these kinds have a fallback and the bare rolls come from the roll landing low
(`WEAPON_MONEY_ROLL_NOT_CEILING_1`); if they are not, the pools are genuinely dead.
🔑 **Read `MarketValue` off a SPAWNED instance, or off `Player.log`, before ruling.**

## What the fix is NOT
⛔ **Do not restore a cut weapon for this.** Nothing was cut. `RESTORE_VANILLA_GUN_TAGS_1`
is a different item and will not touch this.
⛔ **Do not lower the KotOR weapons' prices.** They are a third-party mod's balance and the
prices are consistent within their own tier.

## The two candidate fixes, both DECIDE's under the renormalization ruling
1. **Raise the budgets** to reach the tier the tag names — Leader to ≥12000, Specialist to
   ≥12799. That makes a Blackstar leader carry a legendary KotOR weapon, which is a wealth
   and difficulty decision, not a bug fix.
2. **Point the tags at a tier the budget can afford** — the same move that fixed the
   stormtrooper (`ORImperialStandard` at 906 against a 950 budget). Cheaper, and keeps
   Blackstar mid-tier.

🔑 **This is weapon renormalization across factions and pawnkinds, which the owner's
2026-08-23 ruling put with DECIDE.** BUILD measured it and stopped.

## Instrument note, for the next person
`MarketValue` lives in `fields.statBases` as a **list of `StatModifier` objects**
(`{"stat": "MarketValue", "value": N}`), not a dict — reading it as a dict returns None for
everything and makes every tag look empty. And a **cut** weapon reads `weaponTags: []`, so
"no tags" and "cut" are the same shape from here; the kill list is what separates them.
