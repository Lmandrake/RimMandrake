# The 48-kind armed sweep — run live, and it moved the question

**CHECK, 2026-08-21 ~17:05 PDT. 578 mods, dev-quicktest map, game paused at tick 1.**
240 spawns: all 48 authored role kinds (12 factions × Grunt/Heavy/Leader/Specialist),
**5 rolls each, 5/5 spawned for every kind**, each in its own faction. Equipment read
back with `jawa/pawn_get` — ⛔ never `jawa/pawn_gear`, which is a WRITER and reports
every pawn bare.

## The bar, and the result

`criteria`: 5/5 armed for all 48. **NOT MET.**

| | |
|---|---|
| kinds 5/5 armed | **25 / 48** |
| kinds with at least one bare roll | **23** |
| bare rolls | **27 / 240 = 11.2%** |
| every pawn's `developmentalStage` | `Adult` — no child excuse, and all were clothed |

## 🔴 But the cause is NOT weaponMoney, and that is the finding

`jawa/pawnkind_audit` (the engine's own weapon-pair table and eligibility test):
**"69 tool-using kind(s) audited; every kind that intends to arm can."** 54 healthy,
15 carry no `weaponTags` by design, **0 `cannotAfford`.**

The roll model was then tested arithmetically and **refuted**. If `weaponMoney` is a roll
between `min` and `max`, a bare pawn needs the roll to land under the cheapest eligible
weapon. Measured across all 48 kinds:

    kinds whose weaponMoney.min is BELOW their cheapest eligible weapon:  0 of 48
    expected bare rolls under the roll model:  0.0        observed:  27

It is not close. `Jawa_Blackstar_Leader` rolls **1800–2160** against a cheapest eligible
weapon of **570** and still came up bare twice. ⇒ ⛔ **Do not raise `weaponMoney` on
anything. It is not the lever, and `WEAPON_MONEY_ROLL_NOT_CEILING_1`'s money framing does
not survive this measurement.**

## What does explain it: pawns who cannot do violence

| | bare (27) | armed (213) |
|---|---|---|
| backstory disables `Violent` | **19** | **0** |

A clean separator with no false positives. RimWorld will not hand a weapon to a pawn whose
backstory disables Violent, and `PawnKindDef` generation happily rolls such backstories for
combat kinds. That is **engine behaviour, not a defect in our defs.**

⚠️ **8 of the 27 remain unexplained** and are listed in `rolls.json`
(`pacifistBackstory: false`). A trait check was attempted and came back **UNMEASURED**:
the dump reports 0 `TraitDef`s with `Violent` in `degreeDatas`, which is a dump blind spot
rather than a proven zero.

## 🔴 The control that changes what this item is about

The same 5-roll test, same map, same session, on **vanilla** combat kinds:

    VANILLA:  13 bare of 40 rolls  = 32.5%   (0 of 13 explained by backstory)
    OURS:     27 bare of 240 rolls = 11.2%   (19 of 27 explained by backstory)

    Mercenary_Sniper   bare 5/5      Scavenger    bare 5/5      Town_Guard  bare 3/5
    Mercenary_Gunner   bare 0/5      Mercenary_Heavy 0/5        Tribal_Warrior 0/5

**The authored roster is in better shape than vanilla's own kinds in this mod list**, and
two vanilla kinds cannot arm at all. The bare-handed problem is real but it is **not ours**.

## 🔴 And the cause of THAT is measured too: the vanilla gun pool is empty

`jawa/get_defs`, read off the running game:

| def | runtime `weaponTags` |
|---|---|
| `Gun_Revolver` · `Gun_Autopistol` · `Gun_BoltActionRifle` · `Gun_PumpShotgun` · `Gun_MachinePistol` · `Gun_HeavySMG` · `Gun_AssaultRifle` · `Gun_SniperRifle` · `Gun_Needle` · `Gun_Scattergun` | **`[]`** |
| `Gun_IncendiaryLauncher` | `['Gun','GunHeavy','IndustrialGunAdvanced']` |
| `Gun_ChargeRifle` | `['Gun','SpacerGun','VFEP_Sergeant','VFEP_Captain']` |

Vanilla SHIPS the revolver with `<weaponTags><li>SimpleGun</li><li>Revolver</li></weaponTags>`
(`Core/Defs/ThingDefs_Misc/Weapons/RangedIndustrial.xml:40`). **Something strips them at
load.** The def dump agrees with the runtime, so ⇒ **the dump did not lie** — the branch
`CHEAPEST_WEAPON_IS_ABSURD_1` calls "the dump lied" is closed, and its other branch holds:
**the pool is emptied, and the fix is restoring the tag, not raising money.**

That is exactly why `Mercenary_Sniper` is 5/5 bare — its `SniperRifle` pool has nothing in
it — and it is the best candidate for the 8 unexplained rolls above.

## Files
`rolls.json` (240 rows: kind, name, armed, weapon, both backstories, pacifist flag) ·
`equipment_by_kind.json` · `spawned_ids_by_kind.json` · `pawnkind_audit.json` ·
`runtime_weapon_tags.json`

---

# Addendum — the strip is 26 vanilla weapons wide, and it takes the mechs and the archer with it

## `MECH_AND_ARCHER_ARMED_1`, run in the same window: **0/5, 0/5, 0/5**

    Mech_Pikeman        armed 0/5
    Drone_Sentry        armed 0/5
    Tribal_Archer_Fire  armed 0/5

Five spawns each. Not one of the fifteen held anything. The item expected the pikeman on a
long-range mech gun, the drone on a scattergun and the archer on a plain bow.
`Gun_Needle`, `Gun_Scattergun`, `Bow_Great` and `Flamebow` all read **`weaponTags: []`** at
runtime ⇒ **same cause, not a second bug.** `MECH_WEAPONS_UNCUT_1`'s repair has not taken
on this load.

## The exact stripped set

Every `ThingDef` in `Data/*/Defs/**` that SHIPS a non-empty `<weaponTags>` block, compared
against the live def dump:

| | |
|---|---|
| vanilla/DLC defs shipping non-empty `weaponTags` | 57 |
| still tagged in the live game | 31 |
| **stripped to `[]`** | **26** |

    Artillery_AutoMortar  Artillery_Mortar  Bow_Great  Bow_Recurve  Bow_Short  Flamebow
    Gun_AssaultRifle  Gun_Autopistol  Gun_ChainShotgun  Gun_HeavySMG  Gun_HellcatRifle
    Gun_Incinerator  Gun_LMG  Gun_MachinePistol  Gun_Minigun  Gun_Needle  Gun_PumpShotgun
    Gun_Revolver  Gun_Scattergun  Gun_SniperRifle  MeleeWeapon_Axe  MeleeWeapon_Gladius
    MeleeWeapon_Ikwa  MeleeWeapon_LongSword  MeleeWeapon_Mace  Pila

⚠️ **26 is a FLOOR, not the total.** This compares only defs with an explicit
`<weaponTags>` block in their own XML; a def inheriting tags from an abstract parent is not
counted, and `Gun_BoltActionRifle` — measured `[]` at runtime — is one such absentee. The
true count is 26 or more.

🔑 Read the pattern: **every basic gun, all three bows, and the entire medieval melee set.**
That is the starting kit of every low-tech and mid-tech faction in the campaign.
