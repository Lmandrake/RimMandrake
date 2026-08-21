## spec
Three things landed offline on 2026-08-21 and none is visible without a load, because
Cherry Picker's list and RimWorld's weapon-tag pool both re-form only at startup.
Evidence for all of it: `observed/verify/2026-08-21_mech_uncut_and_fire_archers.md`.

| what changed | where | closed at |
|---|---|---|
| `Gun_Needle` + `Gun_Scattergun` removed from the cherrypick (1349 → 1347 `<li>`) | live Cherry Picker config + `deployed/config/v1_freeze/` | `143ee4e` |
| `NeolithicRangedBasic` appended to `Tribal_Archer_Fire` | `src/Jawa/Jawa_Patches/Patches/WeaponTags_Renormalise.xml`, deployed | `d82c5cb` |

⛔ `Flamebow` is still cut and must stay cut.
⚠️ `Tribal_Hunter_Fire` was deliberately NOT patched — it is not disarmed. Do not report
its absence from the patch as an omission.

## verify
On the next load, re-take the def dump and run
`python3 src/RimMandrake/Utils/weapon_tag_audit.py`.
- `Gun_Needle` and `Gun_Scattergun` carry non-empty `weaponTags` and non-zero MarketValue
  (both currently `[]` / 0 — that is the neutering signature, and its disappearance is
  the proof).
- The tagless list no longer contains `Mech_Pikeman`, `Drone_Sentry` or
  `Tribal_Archer_Fire`. It should drop from 12 kinds to 9.
- `Flamebow` still reads `weaponTags: []`.

## criteria
Spawn a `Mech_Pikeman`, a `Drone_Sentry` and a `Tribal_Archer_Fire`, and confirm each
holds a weapon — the pikeman a long-range mech gun, the drone a scattergun, the archer a
plain bow (not on fire).
