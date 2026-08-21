# WEAPON_TAGS_MATCH_NOTHING_1 — fifteen kinds whose tags match no weapon in the stack

## spec

🔴 **OWNER, 2026-08-21: "Chase the 15 tag-mismatch ones only."** He was offered all 32 and
deliberately took the 15.

`first_light.py` 01:23: **32 of 710 tool-using kinds intend to arm and cannot.** They split
into two unrelated failures and only one is in scope:

| | |
|---|---|
| ✅ **IN SCOPE — 15 kinds** | `weaponTags` match **no loaded weapon at all**. These spawn bare-handed every single time, with no roll involved |
| ⛔ **OUT — 17 kinds** | can't afford the cheapest weapon their tags allow. A money ceiling, not a missing pool |

**The fifteen, with the tag that finds nothing:**
`Mech_Pikeman` MechanoidGunLongRange · `Tribal_Archer_Fire` NeolithicRangedFlame ·
`Drone_Sentry` SentryDroneGunShortRange · `VEE_TribalHunter` VEE_HunterNeolithicWeapon ·
`VEE_Hunter` VEE_HunterIndustrialWeapon · `AncientSoldierBoss` + `AncientSoldierBossN` AMHP ·
`AncientMallGuards` PKM · `DP_ArtilleryPirate` DP_CannonNoEquipTag ·
`DP_RocketPirate` DP_RocketNoEquipTag · `VFEP_Footsoldier` WarcasketBasic ·
`BS_Crossbowman` + `BS_CrossbowDvergr` + `BS_DvergrTraditionalist` BS_CrossbowTag/DankPyon_Arbalest/VFEM2_Arbalest ·
`OuterRim_ImperialTrader` ORImperialOfficer

🔑 **Diagnose the CAUSE per kind before fixing any of them — they are not one bug.** At
least three distinct shapes are visible in that list:
1. ⚠️ **Some are correct as-is.** `DP_CannonNoEquipTag` and `DP_RocketNoEquipTag` are named
   *NoEquip* — a tag deliberately matching nothing, on a pawn whose weapon is built in.
   **Fixing those would be the defect.**
2. **Some lost their weapon to a cherrypick cut.** `rimworld-content-moderation`'s trap
   exactly: cutting the last item carrying a tag disarms every kind whose tags all reach
   zero. Those are ours to repair and are the point of this item.
3. **Some name a tag from a mod that is not installed** — `WarcasketBasic`, the arbalest
   tags. Not our cut; a mod expecting a companion mod.

⇒ **Report the three buckets with counts before proposing a single edit.** ⛔ Do not add a
weapon to a kind in bucket 1 or 3 to make a number go to zero.

⚠️ `Mech_Pikeman` is vanilla-adjacent and worth checking first — if a VANILLA mech kind
cannot arm, something broad was cut, and that is a bigger finding than fifteen kinds.

## verify

- Each of the 15 is assigned to a bucket, with the evidence for that assignment.
- For bucket 2, the tag → surviving-item index is rebuilt from the CURRENT def dump
  (`DefDump/`, captured 2026-08-21T08:20:20Z, 578 mods) — post-inheritance, post-patch.
  ⛔ Not from `observed/2026-08-13/dumps/*`, which are a **585**-mod set and will confirm
  weapons this stack does not have.
- After the fix, `pawnkind_audit` shows zero bucket-2 kinds unable to arm.
- Counts for buckets 1 and 3 are reported to the owner rather than silently fixed.

## criteria

Every kind that is supposed to carry a weapon can find one, and every kind that is
supposed to be empty-handed still is.
