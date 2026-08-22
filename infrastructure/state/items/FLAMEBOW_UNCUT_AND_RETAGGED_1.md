## spec
Owner, 2026-08-22 01:05: *"We should put tags on the flame bows so that more people can use
them too, like the deep tribes especially."*

## 🔴 STEP ZERO, or the whole thing is a silent no-op
**`ThingDef/Flamebow` is on the Cherry Picker kill list** and reads `weaponTags: []` at
runtime. Cherry Picker **empties `weaponTags` at load** as part of neutering a cut def, so
**any tag added in XML is wiped before generation ever sees it.**

⇒ **Remove `ThingDef/Flamebow` from
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\Mod_3521312241_Mod_CherryPicker.xml`
FIRST.** Same edit BUILD already made for `Gun_Needle` and `Gun_Scattergun` at 16:22 on
2026-08-21. Then tag it. In either order the tagging alone achieves nothing, and it will
look like the patch failed.

## what the tag situation is now
| tag | carried by |
|---|---|
| `NeolithicRangedFlame` | **0 loaded weapons** — this is why `Tribal_Archer_Fire` spawns 0/5 |
| `NeolithicRangedBasic` | 5 — `AG_ForsakenBow`, `BS_GiantPrimitiveBow`, `NerveSpiker`, `BMT_BlastSpore`, `VWE_Throwing_Knives` |
| `NeolithicRangedDecent` | 6 — the above plus `BMT_ThrumbungusShroom`, `BS_OgreThrowinRock` |

`Bow_Short`, `Bow_Recurve` and `Bow_Great` are all cut too, which is why the Deep Desert
Tribes' archers draw nerve spikers and throwing knives — **18 live spawns, zero bows.**

## the tags to add, and why
Give `Flamebow` the tags the kinds that should carry it already ask for:

    NeolithicRangedBasic     -> Tribal_Archer, and every basic tribal archer kind
    NeolithicRangedDecent    -> Tribal_HeavyArcher, Tribal_Hunter, Tribal_Hunter_Fire
    NeolithicRangedFlame     -> keep; it is what Tribal_Archer_Fire asks for

⚠️ **Check the price against the budgets before assuming it lands.** `Tribal_Archer` and
`Tribal_Archer_Fire` both run `weaponMoney` 80–80; `Tribal_Hunter_Fire` 100–100. If the
flamebow costs more than 80 the basic archers still cannot buy it, and the audit will say
`cannotAfford` rather than `emptyTagPool`. `jawa/pawnkind_audit` prints `raiseMaxTo` per
kind — read it before touching any budget.

⚠️ And consider un-cutting one plain bow at the same time. A world where the only neolithic
ranged weapon is an incendiary one is a different balance decision than restoring archery.

## 🔴 The bigger thing this uncovered — read before doing the above
The owner's description of the Deep Desert Tribes — *"combat stick weapons and long blaster
rifles"* — **is already built, and nothing fields it.**

    Jawa_DeepDesert_Grunt        tags ORTuskenMelee, ORMeleeBlunt, NeolithicMeleeAdvanced
    Jawa_DeepDesert_Heavy        tags ORMeleeBlunt, NeolithicMeleeAdvanced
    Jawa_DeepDesert_Leader       tags ORTuskenMelee, NeolithicMeleeAdvanced
    Jawa_DeepDesert_Specialist   tags SaV_tusken

Spawned live, they work: the Specialist drew `guy762_slugrifle_tusken` and
`guy762_slugrifle_SovTusken` — **the Tusken Cycler, the long blaster rifle** — and the Heavy
drew `OuterRim_GaderffiiStick`, the combat stick.

⛔ **But no FactionDef fields any of them.** `Jawa_DeepDesert` appears in zero
`pawnGroupMakers`, and `DeepDesertTribes.xml` contains the string zero times. The patch adds
one "water raid" group whose options are, by its own comment, *"the three FAST, LIGHT tribal
kinds only"* — all vanilla Core. So `TribeCivil` fields vanilla tribals and the authored
Tusken roster never arrives.

**Nine of the 48 authored role kinds are orphaned this way:** all four `Jawa_DeepDesert_*`,
all four `Jawa_Blackstar_*`, and `Jawa_Empire_Leader`. The other 39 are wired.

🔑 ⇒ **Flamebow tagging arms the WRONG kinds.** It fixes vanilla `Tribal_Archer`, which is
what the Deep Desert Tribes field *today* but not what they are supposed to field. The
larger fix is wiring `Jawa_DeepDesert_*` into `TribeCivil`'s `pawnGroupMakers` — filed
separately as `ORPHANED_ROLE_KINDS_UNFIELDED_1`. Do that first and the archer question may
answer itself.

## criteria
After the next cold load: `Flamebow` reads non-empty `weaponTags`, and a 5-roll spawn of
`Tribal_Archer_Fire` comes back **5/5 armed**.

Evidence: `infrastructure/state/observed/2026-08-21/armed_sweep_48/`.
