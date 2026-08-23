## spec
🔴 **Two of the Empire's three combat kinds do not look Imperial.** 12 live spawns,
2026-08-22:

| kind | `apparelRequired` | what it actually wore |
|---|---|---|
| `Jawa_Empire_Grunt` | ✅ `OuterRim_StormtrooperCuirass`, `OuterRim_StormtrooperHelmet` | **stormtrooper plate, 4 of 4** |
| `Jawa_Empire_Heavy` | 🔴 none | psyfocus shirt, bone pauldrons, armbands, a parka, a Siegebreaker warcasket, **`guy762_Clothing_RebelCamoII`**, a rebel cap |
| `Jawa_Empire_Specialist` | 🔴 none | warcasket pieces, **`GS_SandP_Hood`** (Sandpeople), **`guy762_SithMask_marauder`**, a poncho, suspenders, two backpacks, an `Apparel_Blindfold` |

Weapons are fine on all three — Imperial blasters throughout. **It is only the silhouette.**

⇒ The faction the guidance doc describes as *"uniform. Mass-produced, identical, no
personality — you are fighting a supply chain"* currently fields Imperial troops in **rebel
camouflage and a Tusken hood.**

## the cause
`Jawa_Empire_Heavy` and `_Specialist` carry neither `apparelRequired` nor any
faction-specific `apparelTags`, so `PawnApparelGenerator` dresses them from the whole
723-def usable pool. On a 578-mod list that pool contains everything.

## the fix, and the palette is already measured
Two live tag families, neither cut:

    ImperialApparel        20 usable defs
    ImperialStormtrooper / ImperialDeathTrooper / ImperialScout / ImperialArmy /
    ImperialSpecialist / ImperialOfficer / ImperialArmyFatigues / ImperialJumpsuit

Either give each kind an `apparelRequired` pair the way the Grunt has, or set
`apparelTags: ["ImperialApparel"]` (plus the specific tier tag) on all four kinds. ⚠️ The
roster is EMITTED by `src/RimMandrake/Utils/gen_pawnkind_roster.py` — the Empire rows are
in the same table as the Trade Moot rows at ~226-229 — so **edit the generator, not the
XML**, or the next run reverts it. Same constraint as `IONBLASTER_INTO_THE_GENERATOR_1`.

⭐ Suggested split, from the measured palette:
- Grunt — `OuterRim_StormtrooperCuirass` + `Helmet` (already correct)
- Heavy — `OuterRim_ImperialArmyCuirass` or `OuterRim_SnowtrooperCuirass` + a helmet
- Specialist — `OuterRim_DeathTrooperCuirass` + `OuterRim_DeathTrooperHelmet`
- Leader — `OuterRim_ImperialOfficerUniform` + `OuterRim_ImperialOfficerCap`
  ⚠️ but `Jawa_Empire_Leader` is fielded by nothing — see `ORPHANED_ROLE_KINDS_UNFIELDED_1`

## while you are in there
`pawnGroupMakers[3]` (`kindDef: Settlement`, commonality 100) was never reskinned and still
fields `Empire_Fighter_Janissary`, `Empire_Fighter_Cataphract`, `Empire_Fighter_Champion`,
five vanilla mech kinds and `RBM_MinotaurGuardianHigh`. **B40 removed the cataphracts from
raids; they are still what defends an Imperial settlement.**

## criteria
Four spawns of each Empire kind come back in Imperial-family apparel, and no rebel,
Sandpeople or Sith piece appears on any of them.

Evidence: `observed/2026-08-22/b40_empire/`.
