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

---

# Second addendum — the culprit is Cherry Picker, and I had one thing backwards

## The strip is the owner's own curation. 27 of 27.

`Config/Mod_3521312241_Mod_CherryPicker.xml` — the list the running game loaded — carries
**every one of the 27 weapons measured as stripped**, and **neither of the two measured as
intact**. No exceptions in either direction.

Cherry Picker is C#/Harmony, not XML: at load it **neuters** each named def rather than
deleting it (deleting breaks cross-references), and part of neutering a weapon is emptying
its `weaponTags`. An exhaustive sweep of 1437 XML files mentioning `weaponTags` across 1254
workshop mods found nothing targeting these defs — **because there is nothing to find.**

🔑 **A Cherry Picker cut is invisible to every XML-shaped search. Read the kill list first.**

⛔ **So "restore the vanilla gun tags" was the wrong conclusion** and the item carrying that
title now opens with the correction. Nobody is to undo the cut.

## 🔴 And "the pool is emptied, not the budget" was too broad

That reading was right for the mechs and wrong for the traders. The whole-game audit
(`jawa/pawnkind_audit`, no filter — **711 tool-using kinds**) splits them:

    29 of 711 INTEND to arm and CANNOT
       12  emptyTagPool   - tags match no loaded weapon at all
       17  cannotAfford   - the pool survives, but only expensive things are left in it
    (not counted: 291 with no weaponTags, 9 with weaponMoney.max 0 - civilians and children)

**The 12 with a genuinely empty pool** — and these are exactly the 0/5 results measured
above:

    Mech_Pikeman         tags [MechanoidGunLongRange]      Drone_Sentry  tags [SentryDroneGunShortRange]
    Tribal_Archer_Fire   tags [NeolithicRangedFlame]       VEE_Hunter, VEE_TribalHunter,
    VFEP_Footsoldier, BS_Crossbowman x3, DP_ArtilleryPirate, DP_RocketPirate, OuterRim_ImperialTrader

**The 17 that cannot afford** — and here the earlier reading was wrong:

| kind | tags | budget | cheapest left | raise max to |
|---|---|---|---|---|
| `Mercenary_Sniper` (+2 variants) | `SniperRifle` | 600–600 | `guy762_brifle_dmr` **760** | 760 |
| `Town_Trader`, `Town_Councilman` (+5 clones) | `Gun` | 200–200 | `Gun_IncendiaryLauncher` **340** | 340 |
| `Hunter` | `Gun` | 140–250 | `Gun_IncendiaryLauncher` **340** | 340 |
| `Scavenger` (+3 clones) | `Gun`, `MakeshiftGun` | 200–300 | `Gun_IncendiaryLauncher` **340** | 340 |
| `TradersGuild_Citizen` | `Gun` | 150–250 | `Gun_IncendiaryLauncher` **340** | 340 |

⇒ **`Mercenary_Sniper` is not bare because its pool is empty.** Its pool holds a 760-silver
DMR and it has 600 to spend. Every cheap `Gun`-tagged weapon was cut, so the cheapest thing
left wearing `Gun` is the **incendiary launcher at 340** — which is precisely the absurdity
`CHEAPEST_WEAPON_IS_ABSURD_1` was named after. The item's own framing was right all along.

🔑 **The correction, stated plainly: `weaponMoney` is refuted for the 48 AUTHORED kinds
(0 of 48 can roll below their cheapest weapon) and it is the correct lever for these 17.**
Do not carry the "money is never the answer" line across to them. The audit even prints
`raiseMaxTo` per kind.

Whole-game audit: `pawnkind_audit_wholegame.json`.

---

# Third addendum — the Deep Desert Tribes' archers have no bows

Prompted by the owner asking what `Tribal_Archer_Fire` is. Answering it turned up something
about **his own faction**.

## What the fire archer is, and whose it is
`Tribal_Archer_Fire` is **vanilla Biotech**, label "archer", `combatPower 75`. Its single
weapon tag `NeolithicRangedFlame` maps to Biotech's **`Flamebow`** — a neolithic bow firing
incendiary arrows. So yes: a tribal archer that shoots fire.

⚠️ **It is not the Deep Desert Tribes'.** The only FactionDef fielding it is
`TribeSavageImpid` — the savage impid tribe, which generated on this world as "League of
Necuvizz". Thematically right: impids are Biotech's fire-resistant xenotype.

**Why it is disarmed and its sibling is not:** `NeolithicRangedFlame` is now carried by
**0 loaded weapons**. `Tribal_Hunter_Fire` survives only because it carries a *second* tag,
`NeolithicRangedDecent`, still on 6 weapons. **One tag versus two — that is the entire
difference**, and it is the tag-pool trap in miniature.

## 🔴 What the Deep Desert Tribes (`TribeCivil`) actually field now

18 live spawns in faction `TribeCivil`, equipment read back:

| kind | what they drew |
|---|---|
| `Tribal_Archer` ×6 | `NerveSpiker` ×4 · `VWE_Throwing_Knives` ×1 · **bare** ×1 |
| `Tribal_HeavyArcher` ×6 | `BMT_ThrumbungusShroom` ×3 · `VFET_Throwspikes` ×1 · **bare** ×2 |
| `Tribal_Hunter` ×6 | `NerveSpiker` ×3 · **bare** ×3 |

**Not one bow among the eighteen.** `Bow_Short`, `Bow_Recurve` and `Bow_Great` are all on
the Cherry Picker kill list, so `NeolithicRangedBasic` and `NeolithicRangedDecent` now
resolve to a five-weapon pool of modded oddities — a nerve spiker, throwing knives, throw
spikes and a fungal spore. **6 of 18 (33%) arrived bare-handed.**

## 🔑 And this is the part the instrument cannot tell you
**None of these three kinds appears in `jawa/pawnkind_audit`'s 29.** They are counted
`healthy`, because healthy means *"a weapon exists in its pool that it can afford"* — not
*"it draws something sensible"*. ⇒ The audit is the right tool for **disarmed**, and it is
blind to **absurdly armed**. `CHEAPEST_WEAPON_IS_ABSURD_1` was about exactly that gap and
the gap is wider than the town traders: it reaches an authored faction's core troops.
