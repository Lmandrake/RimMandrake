# GREENTIDE_FREE_ROSTER_OWNED_1 — the free Greentide owns its whole animal list; the campaign only adds canon

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.greentide` (folds into
`RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`), plus the campaign patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml`. Design:
`design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §1 findings 3 and 4, §3, §4 row
0b, §8. Ruling: **build first: base fixes plus the giant** (decision taken by question card 2026-10-02 07:43
PDT); the base includes *"give the free mod its own jungle animals in place of the vanilla seven"*.
Precedent: `CRACKEDLANDS_PLANT_LIST_OWNED_1` (a campaign op that wholesale-REPLACEs a free list is deleted;
the free tier owns its list; the campaign adds only genuine canon/donor rows with Add). Already ruled: Q11a
and Q12 (`design/RimMandrake/biome_mod_architecture.md` §7: invented names live in `RM_`, moved per biome at
its sitting), Q10 (the sytheclaw moves to RimMandrake), the sheet's six fauna sorts
(`design/Jawa/worldbuilding/biomes/the_greentide.md` §4), the dianoga's removal and its two replacements.

Siblings, same ruling: `GREENTIDE_BASE_PORT_BUILD_1`, `GREENTIDE_THURROCK_HERD_BUILD_1` (the giant's row
lands in this list).

## spec

1. **Three new free-tier creatures** (`RM_`, in `mandrake.rm.greentide`, inline in `RM_Greentide`'s
   `<wildAnimals>`; names collision-checked in the review §3 and re-checked 2026-10-02: no hit in `src/`,
   `design/`, `infrastructure/` outside the review, none on Wookieepedia, artpipe `find` 0 hits each, probe
   `korrum` 12 hits). Descriptions are the review §3's, written into the defs in the biome's voice:
   - **`RM_Sulleth`** (the Brake): big fast-metabolism grazer in loose herds, body size about 2, dusky
     violet hide with lime-green flank bars, always eating, leaves filth and sprouts. Tameable as livestock.
     Carries `RM_SeekShadeExtension` (moved off vanilla Muffalo). Encroachment suppression waits on
     `EXPLOSIVE_PLANT_GROWTH_1`; not built here.
   - **`RM_Dhollock`** (the Lunger): long flat river ambusher, body size about 2.5, mottled slate-blue back
     with ochre eye-ridges, carries `RM_CompAquaticAmbusher` (built, settings toggle #11) and
     `RM_SilenceAuraExtension` (moved off vanilla Warg; the aura fires on a carrier's hunt job, so it goes
     on a predator). Replaces the alligator placeholder: delete `RUT_Placeholder_GreentideLunger` and its
     race def. `RUT_LungerFry` (`RUT_GreentideFish_Items.xml`) is a catch item; leave it, but check its
     description does not name the placeholder.
   - **`RM_Yammeth`** (the Flier): screaming canopy flier in flocks, body size about 0.3, hot magenta and
     acid-yellow membranes. Real 1.6 flight, the `Locust` shape (`MaxFlightTime`, `FlightCooldown`,
     `flightStartChanceOnJobStart`, `flightSpeedFactor`, `canFlyIntoMap`, `canLeaveMapFlying`); no flight
     frames (flying without frames is correct, plainer). Its calls are an ambient soundscape layer that the
     silence cue hushes: when a predator hunts, the flock goes quiet. 🔴 Never live-test its flight without
     the owner present; verify flight by the stat read in criteria.
2. **The canopy swinger moves to the free tier with its own art.** `RSW_CanopySwinger`
   (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_CanopySwinger.xml`) is an invented creature that
   borrows the canon Kowakian monkey-lizard's texPath; the creature is not IP. Re-author it as
   `RM_CanopySwinger` in the free mod with new art (art list row), delete the `RSW_` def, fix the two comment
   references in `RSW_Excretor.xml`. Working defName only: its shipping name is the owner's
   (`GREENTIDE_SHIPPING_NAMES_1`), so build under the working name and let that item rename it.
3. **The yearning fruit moves to the free tier.** `RUT_YearningFruit`, `RUT_YearningFruitHarvested` and
   `RUT_YearningFruit_Hediffs.xml` become `RM_` in the free mod, the plant inline in `RM_Greentide`'s
   `<wildPlants>` at 1.2; delete campaign op 5. Same working-name caveat (`GREENTIDE_SHIPPING_NAMES_1`).
   Fix the comment in `src/RimMandrake/Stillsand/Defs/ThingDefs_Races/RM_Oommok.xml` l.52.
4. **The sytheclaw's Greentide row repoints to the free def.** `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` moves
   `RUT_Sytheclaw` to `RM_Sytheclaw` in `mandrake.rm.pyrelands` and leaves the Greentide row to this
   sitting. Put the row inline in the free list at 0.2 as `<RM_Sytheclaw MayRequire="mandrake.rm.pyrelands">`
   (the guard the Contagion uses for the same creature, `RM_Contagion.xml` l.19; drop it once both biomes
   live in `RimMandrake.Biomes`). It is **multi-homed** (Greentide and Pyrelands): annotate the row in place,
   do not evict (evictions are stopped; the owner did not rule on its home this sitting).
5. **The free list, after this item** (first values, invented; the sheet's bands): krannock (built, wired
   now) 0.3, sulleth 0.8, dhollock 0.15, yammeth 1.0, canopy swinger 0.3, sytheclaw 0.2 (guarded), thurrock
   (`GREENTIDE_THURROCK_HERD_BUILD_1`) when it lands. **The vanilla seven come out** (Warg, Muffalo,
   Elephant, Cobra, Megaspider, Rat, Hare), and so do the two Warg/Muffalo operations in
   `src/RimMandrake/Greentide/Patches/RM_Greentide_FaunaHooks.xml` (they patch every Warg and Muffalo in
   the game; the extensions now live on our own defs). The ruled **Illisk** and **Vurrak** enter this same
   list when `GREENTIDE_TERROR_REPLACEMENT_1` builds them, in the `RM_` tier (Q11a: both names are
   invented); this item reserves nothing else for them. The skerrel stays plant-spawned (the gall is its
   home by design). Check whether felling `RM_Greatbole` drops a `RM_GreatboleGrub`; if it does not, the
   fruitfall (now free, `GREENTIDE_BASE_PORT_BUILD_1`) is its route and nothing is owed here.
6. **The campaign patch shrinks to canon Adds** (`WildAnimals_Greentide.xml`):
   - **delete op 1** (the `PatchOperationReplace` of `RM_Greentide/wildAnimals` that seats the sytheclaw and
     throws away the free list);
   - remove `RSW_CanopySwinger` from op 2's rows;
   - **re-gate ops 2 to 4** with `PatchOperationFindMod` (`mandrake.rsw.swbestiary`, `sarg.alphaanimals`,
     `oskarpotocki.vfe.insectoid2`) and drop the top-level `<Operation MayRequire=…>`, which the 1.6 engine
     ignores (`PATCH_MAYREQUIRE_GUARD_INERT_1`, closed; these three survived it);
   - delete op 5 (yearning fruit, now free); keep ops 6 and 7 (canon catches);
   - **rewrite the header's dianoga paragraph** (finding 4): the swinger does not fill the dianoga's slot;
     the owner filled it with two new terrors, the Illisk and the Vurrak (`GREENTIDE_TERROR_REPLACEMENT_1`,
     card 2026-09-23); the dianoga stays out. Remove the "27 rows / 9.468" parity sums the header quotes
     (they describe a list this item replaces) rather than recomputing them in prose.
7. **Mod Settings:** a commonality multiplier for the new cast is not owed (vanilla density settings
   cover it); the existing ambush toggle (#11) now governs the dhollock.

Depends on: `PYRELANDS_FAUNA_TIER_PORT_BUILD_1` (only for step 4; build steps 1 to 3 and 5 to 6 first and
leave the sytheclaw row on `RUT_Sytheclaw` with a `mandrake.rut.patches` guard if that item has not landed).
Related, not duplicated: `GREENTIDE_TERROR_REPLACEMENT_1` (Illisk, Vurrak), `GREENTIDE_SHIPPING_NAMES_1`
(the swinger's and fruit's names), `BIOME_SPECIFIC_FAUNA_LAW_1` (the sytheclaw's two homes, per-biome
review only). Art: `infrastructure/artpipe/art_lists/greentide_turn1_2026-10-02.csv` (`RM_Sulleth`,
`RM_Dhollock`, `RM_Yammeth`, `RM_CanopySwinger` rows).

## criteria

Deterministic state reads (XML parse of `<wildAnimals>` as elements, never a `<li>` count; def dump;
`jawa/get_defs` reading `success`/`foundCount`/`notFound`), recorded in the Greentide functional script:
- Free tier alone: `BiomeDef/RM_Greentide`'s `<wildAnimals>` element names are exactly
  {`RM_Krannock`, `RM_Sulleth`, `RM_Dhollock`, `RM_Yammeth`, `RM_CanopySwinger`, the sytheclaw row,
  `RM_Thurrock` once built}; zero vanilla rows (no `Warg`, `Muffalo`, `Elephant`, `Cobra`, `Megaspider`,
  `Rat`, `Hare`). Sanity probe: the same parser reads `RM_Pyrelands`'s list as non-empty.
- `ThingDef/RM_Sulleth`, `RM_Dhollock`, `RM_Yammeth`, `RM_CanopySwinger` and `ThingDef/RM_YearningFruit`
  resolve on the free tier; `RSW_CanopySwinger`, `RUT_YearningFruit`, `RUT_Placeholder_GreentideLunger`
  resolve in neither tier; a python search of `src/` for those three old names returns 0, probe
  `RM_Krannock` > 0.
- `RM_Dhollock` carries `RM_CompAquaticAmbusher` and `RM_SilenceAuraExtension`; `RM_Sulleth` carries
  `RM_SeekShadeExtension`; `ThingDef/Warg` and `ThingDef/Muffalo` carry neither extension.
- Flight by stat, not by sight: a spawned `RM_Yammeth`'s `MaxFlightTime` stat > 0 and
  `Pawn_FlightTracker.CanEverFly` reads true (debug `[Tool]`).
- Campaign loaded: no PatchOperation anywhere in `src/` targets `RM_Greentide/wildAnimals` with Replace
  (parse every patch's `Class` and resolved `xpath`); the merged list contains every free row above plus
  the canon `RSW_` rows; `RSW_CanopySwinger` is absent; ops 2 to 4 have no top-level `MayRequire`
  attribute and are `PatchOperationFindMod`.
- With `mandrake.rsw.swbestiary` absent, the merged list holds no unresolved `RSW_` name (read
  `notFound`/the load log's cross-reference errors for zero Greentide rows).
- `<wildPlants>` of `RM_Greentide` contains `RM_YearningFruit` 1.2 on the free tier alone.
