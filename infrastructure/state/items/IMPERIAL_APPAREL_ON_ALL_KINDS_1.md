## ⚠️ THE SPEC BELOW IS STALE — the fix is BUILT AND DEPLOYED, 2026-08-23

**Measured by DECIDE against the DEPLOYED copy** (`Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml`),
not the repo and not the generator:

| kind | apparelRequired | apparelTags | apparelDisallowTags |
|---|---|---|---|
| `Jawa_Empire_Grunt` | StormtrooperCuirass + Helmet | `ImperialStormtrooper` | 7 families locked out |
| `Jawa_Empire_Heavy` | ImperialArmyCuirass + Helmet + **Pauldrons** | `ImperialArmy` | 5 locked out |
| `Jawa_Empire_Specialist` | ImperialOfficerUniform + Cap | `ImperialOfficer` | 4 locked out |
| `Jawa_Empire_Leader` | ImperialOfficerUniform_Black + Cap_Black | `ImperialOfficer` | 4 locked out |

⇒ **The spec's table — *"`Jawa_Empire_Heavy` apparelRequired: none"* — has not been true since it
was written.** The fix also went FURTHER than this item asked: `apparelDisallowTags` locks each
kind out of the other Imperial families, so a Heavy cannot roll stormtrooper white and a
Specialist cannot roll army plate. That is what stops the silhouettes blurring into each other,
and nothing in this item asked for it.

⭐ **It is in the GENERATOR, which is what this item warned about.**
`src/RimMandrake/Utils/gen_pawnkind_roster.py:210-213` carries the four rows and `:307` the tag
families, so the next run reproduces it rather than reverting it. All eight defNames verified
present in the live dump 2026-08-23 — none is a guess.

🔴 **WHAT IS ACTUALLY LEFT IS A LIVE CHECK, AND NOTHING ELSE.** The defs are on disk and the
game has not loaded since. **Disk is not evidence about the running game** — that mistake cost
two items on 2026-08-23 alone. Reassigned to CHECK on domain: judging live behaviour is not
DECIDE's and never was.

## verify
*(the item was filed THIN — no verify section. Written by DECIDE 2026-08-23.)*

Spawn **at least 4 of each** of the four Empire kinds after the next load and read their worn
apparel:
- every Grunt in stormtrooper white, every Heavy in army plate **with pauldrons**, every
  Specialist and Leader in an officer's uniform and cap (Leader's black);
- 🔴 **zero cross-family bleed** — no army plate on a Grunt, no stormtrooper white on a Heavy.
  That is what `apparelDisallowTags` is for and it is the half most likely to fail quietly;
- ⛔ **zero foreign apparel**: no `guy762_Clothing_RebelCamoII`, no `GS_SandP_Hood`, no
  warcasket pieces, no parkas. Those were the original symptom.
⚠️ `Jawa_Empire_Leader` may be fielded by nothing — see `ORPHANED_ROLE_KINDS_UNFIELDED_1`. If it
cannot be spawned through a raid, spawn it directly; that is a separate item, not this one.

---

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
