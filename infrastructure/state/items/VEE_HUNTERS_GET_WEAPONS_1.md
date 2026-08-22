## spec
Ruled under `VANILLA_GUNS_CUT_OR_RETAG_1`: the vanilla firearm cut **stands**, and the
surviving-weapon retag in `WeaponTags_Renormalise.xml` is the architecture. Of the twelve
kinds still holding nothing, **exactly two are both reachable and genuinely disarmed.**

| kind | tag it asks for, on ZERO ThingDefs | `weaponMoney` | apparel |
|---|---|---|---|
| `VEE_Hunter` | `VEE_HunterIndustrialWeapon` | 9999–9999 | — |
| `VEE_TribalHunter` | `VEE_HunterNeolithicWeapon` | 330–850 | `apparelTags [Neolithic]` |

🔑 **Why the faction slate cannot fix these and did fix the others.** `OnlyOurFactions.xml`
zeroes `startingCountAtWorldCreation` on 48 FactionDefs, which is what makes
`BS_CrossbowDvergr`, `OuterRim_ImperialTrader` and `VFEP_Footsoldier` unreachable and
therefore harmless. **These two are referenced by no FactionDef at all** — they are spawned
by `IncidentDef VEE_HuntingParty` (worker `VEE.HuntingParty`), and `vanillaexpanded.vee` is
active. A faction slate has no purchase on an incident.

## What to do
**Add two operations to `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`**, in the
same shape as the `Tribal_Archer_Fire` op already at line ~1958 — tag surviving weapons
INTO the two dead tags, at the weapon end, so the fix also covers any future kind asking
for them.

- `VEE_HunterIndustrialWeapon` → a surviving industrial/spacer ranged weapon. The budget is
  9999, so price is not a constraint; pick from what the renormalise file already classifies
  as `IndustrialGunAdvanced` or `SimpleGun`.
- `VEE_HunterNeolithicWeapon` → a surviving neolithic ranged weapon inside **330–850**.
  ⚠️ Check the price: `NeolithicRangedBasic`'s cheapest carrier must be ≤ 850 or the pool is
  eligible-but-unaffordable, which reads identical to disarmed.

⛔ **Do NOT touch `DP_ArtilleryPirate` or `DP_RocketPirate`.** They are false positives by
design: the mod ships `DP_CannonNoEquip` / `DP_RocketNoEquip` as Primary equipment with
`destroyOnDrop=true` and no `weaponTags`, at `weaponMoney` 99999. Tagging them would put a
mortar in a pirate's hands.

## Two things worth fixing while you are here
1. **`weapon_tag_audit.py` reports unreachable kinds as disarmed.** It flagged 12; only 2
   matter. Teach it to read `startingCountAtWorldCreation` and mark a kind whose every
   referencing faction is zeroed — otherwise every future audit re-raises the same nine.
2. ⚠️ **One dump reading is not understood and should be confirmed in game before it is
   trusted.** `Bow_Short` reads zero `weaponTags` in the 22:44:59Z dump, and it is **not on
   the Cherry Picker cut list**. Either something else strips it or the dumper misses a
   field. `Gun_Autopistol` reads zero too but *is* on the cut list, so that one is explained.
   🔑 Until `Bow_Short` is explained, treat "empty in the dump" as a lead, not a verdict.

## verify
- `weapon_tag_audit.py` reports `VEE_Hunter` and `VEE_TribalHunter` no longer in the
  every-tag-empty list, with the dump regenerated after the deploy.
- `DP_ArtilleryPirate` and `DP_RocketPirate` are untouched.
- No `<li>` is removed from the Cherry Picker config by this item.

## criteria
A hunting party arrives and its hunters are carrying something.
