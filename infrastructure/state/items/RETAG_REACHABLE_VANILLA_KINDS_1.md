## spec
🔴 **The ruling is already made — this item only executes it.** `ORPHANED_KINDS_AFTER_GUN_CUT_1`,
DECIDE 2026-08-23: **a vanilla kind that intends to arm and cannot is RETAGGED onto a sensible
cheap Star Wars sidearm. Not cut, not given more money.**

⛔ **Do not re-litigate the three options.** Money funds the incendiary-launcher absurdity
(`CHEAPEST_WEAPON_IS_ABSURD_1`) rather than fixing it; cutting a kind reaches faction
`pawnGroupMakers`, quest scripts and trader generation, and a `QuestScriptDef` naming a dead kind
fails at offer time in silence.

## ⛔ BLOCKED ON A MEASUREMENT, and it is not optional
`weapon_tag_audit.py` **refuses** right now: the newest capture is `modCount 578` and
`ModsConfig.xml` has **580** active. `--anyway` returns numbers explicitly marked as describing a
game we are not running. 🔑 **This item cannot start until a capture matches the mod list** — that
means a cold load, then `measure build`.

⚠️ **The last time this was measured against a stale database it invented 12 broken kinds that did
not exist.** The corrected figure for empty tag pools is **2**, both `*NoEquipTag` sentinels that
are unarmed on purpose. Do not act on any count that a matching capture has not produced.

## the job, in order
1. Re-run `python3 src/RimMandrake/Utils/weapon_tag_audit.py` against a MATCHING capture. If it
   refuses, stop — the refusal is the instrument working.
2. 🔑 **Cut the list down to REACHABLE kinds first.** A kind fielded by no faction Ash'karr ships
   never spawns, and arming it is work nobody will ever see. The reachable set is the job; the
   audit's total is not.
3. For each reachable kind, add a weapon tag carried by a surviving cheap Star Wars sidearm.
   Keep the kind's existing tags — this is an addition, never a replacement.
4. ⛔ **The two sentinels stay unarmed.** `DP_ArtilleryPirate` and `DP_RocketPirate` carry
   `weaponMoney 99999` and a `*NoEquipTag`; they are correct and must still read as unarmed after.

## verify
A capture whose `modCount` matches `ModsConfig.xml`, then `weapon_tag_audit.py` reporting **zero**
reachable kinds that intend to arm and cannot, excluding the two sentinels.

## criteria
- [ ] Measured against a matching capture, not a provisional one.
- [ ] Every reachable kind that intends to arm can afford something sensible.
- [ ] No kind was cut and no `weaponMoney` was raised to reach an incendiary launcher.
