## spec
🔴 **OWNER, 2026-08-22, reversing his own cut after being shown the cost:** *"Please restore
WarcasketGun_Autorifle, _Minigin, and _HandheldCannon. After seeing the impact, I reverse my
previous decision."*

Those three were the **only** carriers of `WarcasketBasic`, and `VFEP_Footsoldier` — a
**combatPower 300** raider — names that tag and nothing else. Cutting them left it arriving
bare-handed.

⚠️ **Un-cutting was the right lever and re-tagging was not.** The surviving warcasket guns
carry `WarcasketAll`/`Veteran`/`Heavy`/`Flamer`, and every one has `MarketValue: None`, so
`weaponMoney` cannot constrain the roll. Handing the footsoldier `WarcasketAll` would have
armed it *and promoted it* from basic tier to veteran and heavy weapons — an arms-race
change dressed as a bug fix, against `concept.md` §19.5.

## verify
- the live Cherry Picker config reads **1343** `<li>`, down from 1346
- none of the three defNames appears in it
- the `deployed/config/v1_freeze/` mirror is byte-identical to the live file
- ⛔ `Gun_Needle` and `Gun_Scattergun` are still absent (the earlier un-cut is intact)
- ⛔ on the NEXT dump, `WarcasketBasic` has 3 carriers and `VFEP_Footsoldier` leaves the
  `weapon_tag_audit` disarmed list

## criteria
CHECK, next load: spawn `VFEP_Footsoldier` 5 times; all 5 hold a warcasket weapon, and it is
a **basic-tier** one — an autorifle, minigun or handheld cannon — not a veteran laser or a
heavy grenade launcher.
