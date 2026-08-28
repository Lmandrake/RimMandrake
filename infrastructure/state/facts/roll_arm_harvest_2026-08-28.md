# 2026-08-28 live re-harvest — 245 pawns rolled, full-582, post EMPIRE_GRUNT_SPAWNS_BARE_1

**Method:** `src/RimMandrake/Utils/rimbench/roll_arm_harvest.py --rolls 5`, all 49 roster kinds,
live map, full 582-mod set (confirmed against the live `ModsConfig.xml` at run time).
Data: `roll_arm_harvest_2026-08-28.json`.

Run for `ROLE_KINDS_ARMED_5_OF_5_1`'s own `verify` step, hours after
`EMPIRE_BLACKSTAR_ALWAYS_WILLING_1` (2026-08-27) and `EMPIRE_GRUNT_SPAWNS_BARE_1`
(2026-08-28T01:59Z) both closed `pass` on the same mod set.

## 1. The literal verify claim holds. The stronger one it stands in for does not.

**No kind is 0/5** — the item's literal wording ("all 48 spawn holding something") is TRUE.
But **25 of 245 pawns (10.2%) spawned bare**, across **23 of 49 kinds (47%)** — including
`Jawa_Empire_Grunt` (4/5) and every other Empire kind (4/5 each), the exact kind
`EMPIRE_GRUNT_SPAWNS_BARE_1` closed `pass` on hours earlier.

⚠️ **This is not proof that item regressed.** N=5 is small and the item's own note already
measured 2/10 (20%) for Empire_Grunt pre-fix and called that "the single surviving case." A
fresh 4/5 is consistent with a real but incompletely-fixed rate, or with noise around a rate
the two closed items' own (larger, N=10 and N=?) samples underestimated. Either way the
`criteria` — "no Jawa faction fields an unarmed raid" — is not demonstrated met by this roll.

## 2. It is NOT the pacifist-backstory cause `EMPIRE_BLACKSTAR_ALWAYS_WILLING_1` closed

That fix (`requiredWorkTags`, live 2026-08-27) targets a violence-disabled backstory/trait
combination and was verified to affect only Empire and Blackstar kinds. The 25 bare pawns here
carry **no common backstory or trait** — 25 distinct childhood/adulthood pairs, no repeated
violence-disabling tag, spread across mods (`VBE_`, `RT_`, `VTE_`, `Isekai_*`, vanilla). Full
list in `roll_arm_harvest_2026-08-28.json`. **Different cause, same symptom.**

## 3. It is NOT the weaponMoney-floor cause either — re-checked against the CURRENT dump

`WEAPON_MONEY_ROLL_NOT_CEILING_1` (closed REFUTED 2026-08-24) already showed floor > cheapest
for its 7 named kinds. Re-checked here, against the current def dump, for 7 of today's 23
bare-producing kinds:

| kind | weaponMoney (min–max) | cheapest eligible | floor − cheapest |
|---|---|---|---|
| Jawa_Empire_Grunt | 950–1150 | OuterRim_DLT20ABlaster @865 | +85 |
| Jawa_Hutt_Grunt | 200–240 | guy762_holdout @60 | +140 |
| Jawa_Wildsteam_Specialist | 620–744 | OuterRim_VibroDagger @485 | +135 |
| Jawa_Deepwater_Leader | 1400–1680 | OuterRim_VibroDagger @485 | +915 |
| Jawa_Geonosian_Grunt | 400–480 | guy762_sonpistol @220 | +180 |
| Jawa_Junkers_Grunt | 60–72 | BMT_ResourceBlueCrystal @1 | +59 |
| Jawa_Blackstar_Grunt (control, 5/5 today) | 400–480 | guy762_sonrifle_carbine @295 | +105 |

**Every floor comfortably clears its cheapest eligible weapon.** The FloatRange-below-cheapest
mechanism cannot explain any of these. 🔴 `jawa/pawnkind_audit` only ever reports
`weaponMoneyMax`, never `min` — it structurally cannot see this check either way; the min came
from the def dump directly (`fields.weaponMoney.min`), not the audit tool.

## 4. What is left, and it is UNMEASURED

Both prior theories (pacifist backstory, weaponMoney floor) are now ruled out for this batch.
The mechanism producing ~10% bare pawns with an affordable budget and no disabling trait is
**not diagnosed** — candidates not yet checked: `PawnWeaponGenerator.TryGenerateWeaponFor`'s own
tag-pool resolution (a tag whose live candidate set is empty after quality/stuff/techLevel
filters even though `pawnkind_audit`'s static `cheapestEligible` says otherwise), or a
generation-order interaction with apparel/ideology. Needs a source read of
`PawnWeaponGenerator`, not another roll.
