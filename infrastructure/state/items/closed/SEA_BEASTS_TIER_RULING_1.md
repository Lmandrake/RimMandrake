# SEA_BEASTS_TIER_RULING_1 — 11 of the 18 sea beasts are invented originals filed as Star Wars IP

**the Grey Sea, and the Miasma's nursery**

✅ **RULED 2026-09-23 — decision taken by question card: move the 11 invented originals to the
`RM_` tier and leave the 7 genuine canon creatures in the campaign layer.** The retier is
therefore owed work, not a question. ⛔ Do not re-raise it, and ⛔ do not widen it: the 7 canon
creatures stay exactly where they are.

Three alternatives were offered and **declined**, so none of them is a fallback:
- leaving all 18 in the campaign tier and accepting a nursery-less free biome — declined;
- moving only the juveniles and splitting families across two tiers — declined;
- inventing fresh free-tier sea young instead — declined, and it would have duplicated
  creatures we already have.

## the finding

`design/Jawa/worldbuilding/sea_beasts_roster.md` is tagged **Tier RimStarWars (`RSW_`)** in its
entirety. MEASURED against the roster itself, 2026-09-23: **only 7 of its 18 creatures are
canon.** The roster says so in its own words — *"canon Star Wars where a name exists, honest
originals where it does not."*

| canon (7) | invented originals (11) |
|---|---|
| opee sea killer · colo claw fish · sando aqua monster · mee scalefish · faa scalefish · laa scalefish · pale yobshrimp | crimson opee · shale gorger · abyssal colo · thornback colo · elder sando · storm sando · silt lamprey · rust nipper · reefback · starmaw · lanternwhale |

🔑 Under the owner's own **Q11a** ruling (`design/RimMandrake/biome_mod_architecture.md` §7),
*"the fact that we will use 'star wars style' naming doesn't mean they have to live in the star
wars layer"* — an **invented** exotic name is not franchise IP. ⇒ Those 11 belong in the `RM_`
tier and arguably always did.

## why it matters right now

The Miasma's nursery — the sheet's §4 first ring, the crèche of everything the Grey Sea holds —
is staffed **entirely** by these creatures' juveniles: `RSW_MeeJuv`, `RSW_FaaJuv`, `RSW_LaaJuv`,
`RSW_YobshrimpJuv`, `RSW_SiltLampreyJuv`, `RSW_RustNipperJuv`, `RSW_OpeeSeaKillerJuv`. All
campaign-tier.

⇒ **A franchise-free `mandrake.rm.miasma` has no nursery**, and therefore — since the owner
ruled this sitting that the stranded are *the nursery's failures rather than their own species*
— **no stranded animals either.** Two of the biome's three rings of refuge are absent from the
free mod.

That contradicts his ruling of 2026-09-22: *"The top mod without star wars will look precisely
the same as the star wars enhanced one save for any star wars beasts we populate it with"*, and
the corollary already in the project's instructions: a `RM_` biome does not get a thin
dependency-free fallback roster.

⭐ **And the fix invents nothing.** Retiering the 11 originals gives the free mod a real Grey Sea
and a real nursery out of creatures that already exist, with art already approved.

## spec

1. Rename the 11 ThingDefs / PawnKindDefs and their juveniles from `RSW_` to `RM_`, with the C#
   namespace and folder moves the three-tier grammar requires
   (`design/NAMING_SCHEME_PLAN.md`).
2. Repoint every reference: biome `wildAnimals`, `fishTypes`, leather and meat defs, egg defs,
   sound defs, `race/wildBiomes`, art paths, and the design rosters.
3. Keep the 7 canon creatures on the campaign patch layer, `MayRequire` gated as now.
4. Update `sea_beasts_roster.md`'s own tier tag, which currently says the whole roster is `RSW_`.

## verify

- No `RM_` sea beast references a `RSW_`-only body, leather, meat, sound or texture path.
- Zero new Config errors in `Player.log` on a cold load; a post-load def dump confirms all 18
  still resolve.
- A quicktest map in the Miasma with the **free** mod only, and no Star Wars mods: juveniles
  must spawn in the shallows.

## criteria

The tier line falls on IP and not on flavour, as Q11a says it should; and the free Miasma has a
nursery, and therefore stranded animals, without a single new creature being invented.

## Watch out

- 🔴 **A retier moves creatures between tiers. It removes none of them.** The roster was
  approved 2026-08-31 with *"They're exceptional. Don't get rid of any of them"* — all 18 stay
  in the game, and that ruling is untouched by this one.
- ⚠️ **Art is final-concept and must not be re-rolled.** That same ruling fixed the mockups as
  the art source of truth; a retier moves files, it does not regenerate them.
- ⚠️ **`RM_Gelatid` and `RM_Titanoslime` are the only `RM_` aquatic creatures shipping today** —
  check for name and role collisions before adding eleven more.
- 🔑 This is the **same Q11a misfiling in the same direction** the project already records
  BENCH getting backwards once — routing invented content into the franchise layer because the
  names sound alien. Worth stating in whatever commit lands it.
