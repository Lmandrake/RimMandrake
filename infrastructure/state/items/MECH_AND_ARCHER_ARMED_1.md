## spec
Three things landed offline on 2026-08-21 and none is visible without a load, because
Cherry Picker's list and RimWorld's weapon-tag pool both re-form only at startup.
Evidence for all of it: `observed/verify/2026-08-21_mech_uncut_and_fire_archers.md`.

| what changed | where | closed at |
|---|---|---|
| `Gun_Needle` + `Gun_Scattergun` removed from the cherrypick (1349 → 1347 `<li>`) | live Cherry Picker config + `deployed/config/v1_freeze/` | `143ee4e` |
| `NeolithicRangedBasic` appended to `Tribal_Archer_Fire` | `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`, deployed | `d82c5cb` |

🔴 ~~`Flamebow` is still cut and must stay cut.~~ **SUPERSEDED — do not act on this line.**
This item was filed **2026-08-21 23:30**. At **2026-08-22 01:05** the owner ruled the other
way: *"We should put tags on the flame bows so that more people can use them too, like the
deep tribes especially."* `FLAMEBOW_UNCUT_AND_RETAGGED_1` carried that out and closed at
`e38d6fb5` ("The flamebow gets real tags; it lands on hunters, not basic archers").

✅ **Measured in capture `2026-08-23T07-12-04Z`:** `Flamebow` is **off** the Cherry Picker
kill list and carries `Neolithic`, `NeolithicRangedFlame`, `NeolithicRangedBasic`,
`NeolithicRangedDecent`. It is the **sole carrier of `NeolithicRangedFlame`**, which is
exactly why `Tribal_Archer_Fire` is armed now. ⛔ **Re-cutting it re-disarms that kind.**
⚠️ `Tribal_Hunter_Fire` was deliberately NOT patched — it is not disarmed. Do not report
its absence from the patch as an omission.

## verify
On the next load, re-take the def dump and run
`python3 src/RimMandrake/Utils/weapon_tag_audit.py`.
- `Gun_Needle` and `Gun_Scattergun` carry non-empty `weaponTags` and non-zero MarketValue
  (both currently `[]` / 0 — that is the neutering signature, and its disappearance is
  the proof).
  ✅ **MET, measured 2026-08-23:** `Gun_Needle` = `['MechanoidGunLongRange']`, MarketValue
  1400; `Gun_Scattergun` = `['SentryDroneGunShortRange']`, MarketValue 1000.
- The tagless list no longer contains `Mech_Pikeman`, `Drone_Sentry` or
  `Tribal_Archer_Fire`. ~~It should drop from 12 kinds to 9.~~
  🔴 **THE 12 AND THE 9 WERE BOTH WRONG, and the instrument was why.** `weapon_tag_audit.py`
  carried two defects (fixed `7f005f7c`): it read tags from a `defs.sqlite` built two days
  earlier while printing the newest capture's timestamp, and it subtracted the Cherry Picker
  kill list from a capture that is already post-cut. ✅ **The measured figure is 2**, and both
  are `DP_*NoEquipTag` sentinels that are correct by design. `Mech_Pikeman`, `Drone_Sentry`
  and `Tribal_Archer_Fire` are all off the list.
- ⛔ ~~`Flamebow` still reads `weaponTags: []`.~~ **STRUCK with the line above** — an empty
  `weaponTags` on `Flamebow` is now a FAILURE, not a pass. It must read four tags.

## criteria
Spawn a `Mech_Pikeman`, a `Drone_Sentry` and a `Tribal_Archer_Fire`, and confirm each
holds a weapon — the pikeman a long-range mech gun, the drone a scattergun, the archer a
plain bow (not on fire).
