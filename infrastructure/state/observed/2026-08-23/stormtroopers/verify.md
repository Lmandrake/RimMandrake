# Stormtroopers: shiny new armour, nothing else, proper blasters — BUILD, 2026-08-23

Owner: *"make sure that the empire's stormtroopers absolutely show up in shiny new
stormtrooper armor and nothing else and have appropriate blasters. That is absolutely
crucial."*

## 🔴 DEFECT 1 — stormtroopers could NEVER afford a rifle, and were carrying PISTOLS

    Jawa_Empire_Grunt   weaponMoney 650~780
    ORImperialStandard  OuterRim_E11BlasterRifle    906   OVER BUDGET
                        OuterRim_DLT20ABlaster      906   OVER BUDGET
                        OuterRim_E22BlasterRifle    906   OVER BUDGET
    ORImperialLight     DE-10 / EC-17 / SE-14R      592   affordable — and ALL FOUR ARE
                        DG-29                       592   TAGGED ORPistol

Every rifle the stormtrooper tag reaches costs 906 against a 780 ceiling, so the roll could
never buy one and always fell through to the light tag — which is entirely sidearms. **The
iconic E-11 was unreachable by construction.**

✅ **Fixed:** `weaponMoney` 650~780 → **950~1150**, and `ORImperialLight` dropped from the
Grunt. The three rifles left — E-11, DLT-20A, E-22 — are all canon-correct and all now
affordable, 3 of 3.

⚠️ This is the third instance tonight of the same bug class (`WEAPON_BUDGET_BELOW_POOL_FLOOR_1`,
and the apparel form of it in `AUTHORED_FACTIONS_WEAR_ANYTHING_1`): a full pool the pawn
cannot shop in is an empty pool at generation time.

## 🔴 DEFECT 2 — "nothing else" was not enforced; 21 carriers were reachable

`apparelTags` read `ImperialApparel`, which carries **21** items including **Snowtrooper**,
**Scout Trooper**, **Range Trooper**, **Death Trooper**, **ISB Agent** and Imperial Gunner
pieces — plus `ImperialArmy` and `ImperialOfficer` on top.

The required cuirass and helmet occupy Torso and FullHead, so a wrong helmet could not
stack — but **Shoulders/Arms was free**, and a stormtrooper could take the field wearing
**Scout Trooper or Snowtrooper pauldrons**.

✅ **Fixed, two ways:**
- `apparelTags` narrowed to **`ImperialStormtrooper`** — exactly 3 carriers, all correct:
  `OuterRim_StormtrooperCuirass`, `..._Helmet`, `..._Pauldrons`.
- `apparelDisallowTags` added as a hard refusal: `ImperialArmy`, `ImperialOfficer`,
  `ImperialSpecialist`, `ImperialScout`, `ImperialDeathTrooper`, `ImperialArmyFatigues`,
  `ImperialJumpsuit`. The field is real — 52 kinds in the load set already use it.

## ✅ "SHINY NEW" was ALREADY correct, and I checked rather than assumed

    gearHealthRange          1~1     pristine; no tattered or damaged armour
    forceNormalGearQuality   true    no awful/poor rolls
    itemQuality              Normal

⚠️ One sloppy value found and raised: `minApparelQuality` read **`Awful`** on all four. It
was inert while `forceNormalGearQuality` is true, but it is a trap for anyone who later turns
that off. Set to **Normal** on Grunt/Heavy/Specialist and **Excellent** on the Leader.

## the other three Empire kinds, locked to their own wardrobes

| kind | required | may add | refused |
|---|---|---|---|
| Grunt (stormtrooper) | Stormtrooper cuirass + helmet | `ImperialStormtrooper` | 7 families |
| Heavy (army) | Army cuirass + helmet + pauldrons | `ImperialArmy` | 5 families |
| Specialist (officer) | Officer uniform + cap | `ImperialOfficer` | 4 families |
| Leader (senior officer) | Black uniform + black cap | `ImperialOfficer` | 4 families |

Weapons after the change: Grunt 3 of 3 affordable, Heavy 4 of 6, Specialist 8 of 8,
Leader 9 of 9. validate_patch.py 0 errors 0 warnings. Deployed, VERIFIED in sync.

## ⚠️ what this still does NOT guarantee, stated plainly
`apparelRequired` is forced and ignores budget, so the cuirass and helmet always appear —
that part is certain. What is NOT certain from defs alone is what the pawn looks like on
screen after layering. **Only a live spawn proves it**, and there is no log string for it.
