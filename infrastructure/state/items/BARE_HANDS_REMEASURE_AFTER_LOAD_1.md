## spec
🔴 **`WEAPON_MONEY_ROLL_NOT_CEILING_1`'s DIAGNOSIS IS REFUTED. Do not raise any
`weaponMoney.min`.** The live observation behind it is real — 23 of 54 kinds fielded a bare
pawn across 270 spawns — but the proposed cause is not.

**Measured offline 2026-08-22 against `OFFICIAL-2026-08-21T22-44-59Z`.** The item says a low
roll lands below the cheapest eligible weapon. Under that theory, `P(bare) = (cheapest − min)
/ (max − min)`, which is zero whenever `min ≥ cheapest`. For all seven kinds the item names
worst:

| kind | min | max | cheapest eligible | headroom | P(bare) predicted | CHECK saw |
|---|---|---|---|---|---|---|
| `Jawa_Empire_Grunt` | 650 | 780 | 573.0 | +77 | **0.0%** | 2/3 bare |
| `Jawa_Blackstar_Grunt` | 400 | 480 | 295.0 | +105 | **0.0%** | 3/5 |
| `Jawa_Deepwater_Heavy` | 600 | 720 | 550.0 | +50 | **0.0%** | 3/5 |
| `Jawa_Droid_Specialist` | 1200 | 1440 | 982.5 | +217 | **0.0%** | 3/5 |
| `Jawa_Hutt_Leader` | 13000 | 15600 | 12000.0 | +1000 | **0.0%** | 3/5 |
| `Jawa_Junkers_Grunt` | 60 | 72 | **1.0** | **+59** | **0.0%** | 3/5 |
| `Jawa_TradeMoot_Grunt` | 250 | 300 | 60.0 | +190 | **0.0%** | 3/5 |

🔑 **`Jawa_Junkers_Grunt` settles it on its own.** Its floor is 60 against a cheapest of
**1** — sixty times the price. No roll in `60~72` can land below 1. Raising the floor cannot
change a thing.
✅ `weapon_affordability.py` agrees independently: **48 always arm, 0 sometimes, 0 never.**
So does `RESTORE_VANILLA_GUN_TAGS_1`, which measured the same thing from the other side:
*"0 have a `weaponMoney.min` below their cheapest eligible weapon, and `jawa/pawnkind_audit`
reports 0 `cannotAfford`."* Three routes, one answer: **money is not the lever.**

⛔ **And raising the floor is not free.** `gen_pawnkind_roster.py` derives `max` and
`combatPower` from the same number, so lifting the floor lifts the ceiling and re-tiers the
raids — the trap the item itself warns about.

### What must happen instead

**Re-measure live, on the NEXT load, before anything is changed.** Three things landed after
CHECK's 2026-08-21 run that plausibly move these numbers, and none was in the game he
measured:

1. `MECH_WEAPONS_UNCUT_1` (`143ee4e`) — `Gun_Needle` and `Gun_Scattergun` un-cut.
2. `DROID_RACES_APPLIED_TO_KINDS_1` (`9b01b10`) — the four `Jawa_Droid_*` kinds were
   `<race>Human</race>` when he measured and are now droid races. 🔑 **`Jawa_Droid_Specialist`
   is one of the seven, and its cheapest eligible is an `OuterRim_DroidWeapon_*`. A human
   holding a droid weapon is a different question from an affordability one** — that kind may
   already be fixed.
3. `FIRE_ARCHERS_GET_BOWS_1` (`d82c5cb`) — `Tribal_Archer_Fire` re-tagged.

## verify
Re-run the same protocol on the next load: spawn each of the 54 arming kinds 5 times and read
equipment via `jawa/pawn_get`. Report the kinds still fielding a bare pawn, and for each one
**the `cheapestPrice` the engine reports** — `jawa/pawnkind_audit`'s number includes
`ThingStuffPair` stuff cost, which the offline pass cannot see.

## criteria
- The surviving bare-handed list is named, with the engine's own `cheapestPrice` beside each.
- If any kind's engine `cheapestPrice` is **above** its `weaponMoney.min`, the roll theory is
  alive for that kind and only that kind, and a floor change is justified for it alone.
- If none is, the cause is elsewhere and a new item names it. ⛔ Do not raise a floor to paper
  over a cause nobody has found.

## notes
⚠️ **Secondary finding, filed here so it is not lost.** `weapon_affordability.py` named
`BMT_ResourceBlueCrystal` — a **`stackLimit` 75 resource** from Biomes! Caverns — as
`Jawa_Junkers_Grunt`'s cheapest eligible weapon, at price 1. It is not strictly wrong: the
def carries `equipmentType Primary`, `weaponTags`, `weaponClasses` and a Cut `tool` at power
11, so the engine may genuinely equip it. But *"this kind is safe because it can hold a
crystal shard"* is not the answer the tool implies, and a resource stack answering a weapon
question is worth an eye.
