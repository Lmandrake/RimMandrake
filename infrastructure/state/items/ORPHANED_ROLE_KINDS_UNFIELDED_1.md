## spec
🔴 **Nine of the 48 authored role pawn kinds are built, correct, and fielded by nothing.**

Measured off the 2026-08-21 dump — every `FactionDef`'s resolved `pawnGroupMakers` scanned
for `Jawa_*` kind names:

    authored role kinds that exist:                48
    fielded by at least one FactionDef:            39
    fielded by NOTHING:                             9

        Jawa_DeepDesert_Grunt  Heavy  Leader  Specialist      <- the Tuskens
        Jawa_Blackstar_Grunt   Heavy  Leader  Specialist      <- the mercenaries
        Jawa_Empire_Leader

## they are not broken — they work when spawned by hand
Live spawns, 5 rolls each, equipment read back:

    Jawa_DeepDesert_Specialist  ->  guy762_slugrifle_tusken x2, guy762_slugrifle_SovTusken x2
    Jawa_DeepDesert_Heavy       ->  OuterRim_GaderffiiStick, MeleeWeapon_Spear, MA_DuskSpear, MA_MegaboneClub
    Jawa_DeepDesert_Grunt       ->  MA_MegaboneClub x4
    Jawa_DeepDesert_Leader      ->  MA_GnautHornMace x2, MeleeWeapon_Spear, MA_DuskSpear

⇒ The **Tusken Cycler** (the long blaster rifle) and the **gaderffii stick** (the combat
stick) both land. The owner's description of this faction — 2026-08-22, *"they normally use
their combat stick weapons and have long blaster rifles"* — **is exactly what these kinds
produce.** The authoring is done. Only the wiring is missing.

## what arrives instead, today
`TribeCivil` (Deep Desert Tribes) fields vanilla `Tribal_*` kinds. 18 live spawns:

| kind | drew |
|---|---|
| `Tribal_Archer` ×6 | `NerveSpiker` ×4, `VWE_Throwing_Knives` ×1, bare ×1 |
| `Tribal_HeavyArcher` ×6 | `BMT_ThrumbungusShroom` ×3, `VFET_Throwspikes` ×1, bare ×2 |
| `Tribal_Hunter` ×6 | `NerveSpiker` ×3, bare ×3 |

**No bows, no gaffi sticks, no cyclers, and a third empty-handed.** That is the raid the
player will actually meet.

## why it slipped through
`DeepDesertTribes.xml` contains the string `Jawa_DeepDesert` **zero times**. Its one
sanctioned group addition — the "water raid" — is documented in its own header as using
*"the three FAST, LIGHT tribal kinds only… Every kind here is vanilla Core"*. So the patch
did precisely what it says; nobody ever wrote the step that puts the authored roster into
the faction. Same for `BlackstarCompany.xml`, which states outright that `pawnGroupMakers`
are not touched.

⚠️ `GalacticEmpire.xml` DOES wire its kinds — 13 references — which is why `Jawa_Empire_Grunt`,
`_Heavy` and `_Specialist` are fielded and only `_Leader` is missing. That one looks like an
omission rather than a policy.

## 🔴 why it is on the pre-worldgen path
A faction's `pawnGroupMakers` are read from the def at raid time, not baked at world
creation — **so this is fixable after the click.** But the *faction roster itself* is baked,
and `BLACKSTAR_IN_DEFAULT_LIST_1` already turns on whether Blackstar generates at all. Settle
the two together rather than discovering the second one later.

## the decision
1. ⭐ **Wire them in.** Add `pawnGroupMakers` entries to `TribeCivil` and `Pirate` naming the
   authored kinds, and add `Jawa_Empire_Leader` to `Empire`. ⚠️ Inheritance APPENDS, so a new
   `<li>` adds to the twelve inherited vanilla groups rather than replacing them — the
   authored kinds would arrive *alongside* vanilla tribals unless the vanilla groups are
   given `Inherit="False"` or their commonality is rewritten. Decide which.
2. **Leave them.** The kinds stay as a reserve for hand-placed encounters and the factions
   keep fielding vanilla pawns.

⛔ Do not treat this as the same problem as the cut weapons. Wiring the roster in is a
different fix from `FLAMEBOW_UNCUT_AND_RETAGGED_1`, and doing the roster first may make the
flamebow question moot for this faction.

Evidence: `infrastructure/state/observed/2026-08-21/armed_sweep_48/`.
