# Donor retirement — ordering plan (2026-10-02)

The ordering plan `DONOR_DEFS_PORT_TO_OURS_1` is blocked on (its spec: *"needs a plan and an
owner sitting on the order first"*). Nothing here is a ruling. It applies rulings already made
(§7 Q9, Q11, Q11a, Q12, Q13, Q14 of `biome_mod_architecture.md`; the 2026-09-22 stop on
evictions; the 2026-10-01 build pause) and asks the owner only what they leave open.

## 1. What was measured (and how)

**Instrument.** A Python census written for this plan (session scratchpad, `donor_census.py`;
not committed). It parses every `BiomeDef` under `src/` as XML elements (`<DefName>weight</DefName>`
shorthand, `fishTypes` buckets read one level down) and every `PatchOperation` under `src/**/Patches/`
whose xpath names one of our BiomeDefs. It walks `FindMod`/`Sequence`/`Conditional` down to the
`Add`/`Replace` and reads the rows from `<value>`. Ownership comes from the row's `MayRequire`
packageId, never from the prefix. An unguarded row is looked up against our 6,967 defNames in `src/`,
then against 11,586 vanilla and DLC defNames from the installed `Data\`. A "port exists" match needs
a same-stem `RSW_`/`RM_`/`RUT_` def, or a `<donor> -> <ours>` comment in `src/` that names a def
we actually have.

**Sanity probe (all passed, the script refuses to report on a zero):** 58 BiomeDefs, 1,469 rows,
0 parse failures. `RSW_Gizka` was found on 8 rows, `AA_DuskRat` on 2, Core `Muffalo` on 2, and
`AA_Cactipine` resolved to `RSW_Chikka`.

**Two layers, kept apart.** The `RUT_` twins in `UtinniPatches/Defs/BiomeDefs/` are FROZEN. The world
still runs on them until the one-time paint (`BIOME_PAINT_ONCE_AT_THE_END_1`), and they are deleted
at that pass. ⛔ They are not edited and not ported. What ships is the **`RM_` defs plus the
Utinni patches onto them.** The plan targets only that layer.

| layer | rows | donor rows | unique donor names | already have a port of ours |
|---|---:|---:|---:|---:|
| **shipping (`RM_` + patches)** | 892 | **128** | 117 | **16 rows / 12 names** (instrument floor, see below) |
| frozen `RUT_` twins (die at the paint) | 577 | 306 | 240 | 118 / 88 |

Shipping layer by donor: **`sarg.alphaanimals` 72**, `sarg.alphabiomes` 14, unguarded and
owner-unresolved 11, `mlie.starwarsanimalcollection` 7, `regrowth.botr.core` 5, then
`ironscruff.primordialgeysers`, `sarg.alphamemes` and `who.vfee.isopodageneline` at 3 each,
`oskarpotocki.vfe.insectoid2` 3, `vanillaexpanded.vgeneticse` 2, `mlie.horrors` 2,
`sarg.alphagenes` 2 and `grimterra.biomesmod` 1.

🔑 **What moved since the item's 2026-09-20 table (160 / 102):**
- **The Star Wars animal mod is nearly gone from the shipping layer: 7 rows.** They are `Tibidee`
  (Forge), `Silooth` (Cauldron), `Snoruuk` (Rot), `Vapaad` (Blue Desert) and the three canon plants
  hydenock, jogan and tooke-trap (Fever Wood, Webwork). The "73 already-ported creatures still named
  as donors" are **done**. `MLIE_ABSORPTION_BIOME_WIRING_1` closed 2026-09-25 having retargeted 55
  rows, and this census finds **0** shipping rows that name a Star Wars donor creature we have ported.
- **Alpha Animals is now the job**: 72 of 128 rows.
- ⚠️ **"Already ported" is a floor.** The desert port renamed 7 plants (`RSW_SurraGrass`, `JekkaGrass`,
  `TanniVine`, `RuzzoCarpet`, `QuissaBloom`, `VellaraBloom`, `DommoTree`), and none of them carries a
  machine-readable donor comment. So the 4 ReGrowth grasses in the Leaning Scrub and `AB_HardyGrass` in
  the Flooded Canyon probably have ports too. **UNMEASURED.**

**Load-safety findings (shipping layer):**
- **11 donor rows carry no guard at all**: 6 Abyss flora, `AB_TinkleGrass` and `AB_FirevineTree`
  (Forge), `AB_HardyGrass` and `AB_GargantuanLithops` (Flooded Canyon), and `Plant_Nysyllin_Wild`
  (Leaning Scrub).
- **8 rows are guarded only by a top-level `<Operation MayRequire>`**, which 1.6 ignores. They are
  `Vapaad`, `Snoruuk`, `AA_Needlepost`, `AA_BloodShrimp` and `VFEI2_Swarmling` (Greentide), plus the
  3 canon plants.
- **2 rows are mis-guarded** (both unfiled since 2026-09-24): `VFEI2_BlackSwarmling` (Miasma) sits
  under Alpha Animals' guard, and `LavaSnail` (Forge) under Alpha Biomes', a mod that does not
  define it.

All 21 are harmless while every donor stays installed. They break the moment a donor leaves. That
is the shape that reset `ModsConfig.xml` to Core-only twice on 2026-09-27.

## 2. Sibling items — open or closed (`rimflow show`, 2026-10-02)

| item | ledger | what it means for this plan |
|---|---|---|
| `DONOR_DEFS_PORT_TO_OURS_1` | ready, BLOCKED, needs owner | this plan unblocks it |
| `DESERT_FAMILY_PORT_EXECUTION_1` | proposed (BENCH) | desert ruled "replace all" 2026-09-20. 96/109 defs ported; the art is what remains (24 renders recorded as awaiting his eye, 2026-09-20 sheet). One word owed: `Rat` |
| `MLIE_ABSORPTION_BIOME_WIRING_1` | **done** (`3abed6f36`) | the "73 ported, still named as donor" win is spent; re-measured 0 left |
| `STARWARS_DONOR_PORT_LABEL_COLLISIONS_1` | proposed, needs owner | its 62-collision list predates the 09-25 rewiring. Re-run `label_collision_check.py` before asking him anything |
| `ABYSS_DONOR_BEASTS_FREED_1` | proposed | 2 new invented beasts, fresh art. Its reading of "those two beasts" still needs his confirm |
| `ABYSS_FREE_TIER_BODY_1` | proposed | Abyss labels, 12 finished art sets to wire, 8 flora to guard or own |
| `COMMISSION_LEDGER_CLEANUP_1` | doing | new-creature commissions, not ports. 7 slugs left, all design-blocked. Not on this path |
| `DESERT_WRAPS_ART_COMMISSION_1` | doing | apparel, not a donor roster. 17 art cells owed. Not on this path |
| `STONEBACK_BOKKA_ART_STANDARD_1` | doing | bokka art FAILS (donor creature drawn). The regen failed validation twice. It shows the port-art trap: our path, the donor's pixels |
| `ROT_ROSTER_DEAD_DONOR_NAMES_1` / `NONCANON_BEAST_RENAME_1` / `PATCH_MAYREQUIRE_GUARD_INERT_1` | done | closed precedents |

## 3. Order of work

Cheapest first, then one biome at a time. The original spec said "order by donor, not by
biome". That was overtaken on 2026-09-22, when the owner stopped sweeping changes in favour of
biome-by-biome handling, and by Q12, which puts each biome's tier moves at its own sitting. Each
step below therefore touches one biome's files and leaves every other biome alone.

- **Step A: load-safety guards (bug fix).** Give the 11 unguarded rows a row-level `MayRequire`.
  Move the 8 rows that sit behind an inert `<Operation MayRequire>` to row-level guards. Correct the 2
  mis-guarded rows (`VFEI2_BlackSwarmling`, `LavaSnail`). No roster changes membership, and no weight
  changes. It is a precondition for every retirement test.
- **Step B: swaps where our version already exists.**
  - **B1, the Sump (4 rows).** He ruled the replacement on 2026-09-24. `RM_Gulveth`, `RM_Thrummel`,
    `RM_ThrummelWarden` and `RM_ThrummelBroodmother` are built in `TheSump`, with renders done (artpipe
    `RM_*` targets). The roster still names the four `AA_` rows because the swap was left to "this
    biome's own sitting".
  - **B2, the 12 already-remade creatures** (§4, column "port exists"). Their remakes live in the Star
    Wars add-on (`SWBestiary`). Q12 already rules how they ship: behind the Utinni
    `WildAnimals_<Biome>.xml` patch, with the move to the free tier at each biome's own sitting. Open:
    what happens to the borrowed original in the free mod meanwhile (Q1 in §5).
  - **B3, the last 7 Star Wars animal-mod rows.** Remake or drop them. After that the Star Wars animal
    mod has **zero** rows in anything we ship.
- **Step C: per-biome units** in the order of §4: biomes whose art is finished come first, then biomes
  already sat, then unsat biomes. Each unit follows the `CAVERNS_PARITY_BUILD_1` / `BMT_FAUNA_ABSORPTION_1`
  pattern: close every reference (body, sounds, meat, eggs), re-point the texPath, drop donor-assembly
  comps, and re-point the `MayRequire` at our mod (never drop it).
- **Step D: per-donor retirement tests, after the paint.** The world still runs on the frozen twins
  (306 donor rows, 66 of them unguarded). A donor-absent load before the paint tests the twins, not what
  ships. So each donor's "absent from `ModsConfig.xml`, biomes still generate" test waits for
  `BIOME_PAINT_ONCE_AT_THE_END_1`, except a quicktest on the `RM_` defs alone.

Two donor pairs must retire together, because each depends on the other mod: `who.vfee.isopodageneline`
needs `oskarpotocki.vfe.insectoid2` (Warscar's 3 rows), and `vanillaexpanded.vgeneticse`'s
`GR_Beetlefleet` needs `sarg.alphaanimals` (Cauldron).

## 4. Per-biome units (shipping layer, MEASURED 2026-10-02)

The art column comes from name search over `D:\Luke\dev\_artpipe\art_status.json` plus our
`*ArtOverride` mods (our art painted onto a donor body). A miss is **not** proof that no art exists.
Abyss art is keyed by invented label (`crags_vrakk`…), so its figure comes from `ABYSS_FREE_TIER_BODY_1`.
The pipeline's universal state, `awaiting_verdict`, covers 2,018 of 2,167 targets, so "rendered" here
means "pixels exist" and says nothing about whether he approved them.

| # | biome | donor rows | port exists | donor-code creatures (HIGH) | art | sitting / ruling state |
|---|---|---:|---:|---|---|---|
| 1 | Sump | 4 | **4 (ruled replace)** | 0 | replacements rendered | ruled 2026-09-24. Bedazzle sitting proposed |
| 2 | Weeping Stones | 1 | 1 (`RSW_Ikee`) | 0 | rendered | the swap makes the biome donor-free |
| 3 | Leaning Scrub | 10 | 6 (+4 likely) | 0 | 6 rendered, 1 override | desert family ruled "replace all" 2026-09-20 |
| 4 | Nightside Ice | 7 | 3 | 1 (`AA_RedGoo`) | 1 override, 1 rendered | bedazzle sitting done |
| 5 | Abyss | 22 | 1 | 1 (`AA_Darkbeast`) | **12 finished fauna sets + 8 flora redraws**, dusk rat redo owed | sitting done, 2 items proposed |
| 6 | The Rot | 22 | 2 | 3 (`Agaripawn`, `Agaripod`, `MycoidColossus`) | 16 rendered, 3 override. Sheet re-ruled 2026-10-02 (60 keep, 1 regen) | no donor-row keep/cut found |
| 7 | Cauldron | 18 | 1 | 6 (`InfectedAerofleet`, `OcularJelly`, `DecayDrake`, 3 dryads) | 1 override, 17 none found | bedazzle sitting done |
| 8 | The Forge | 11 | 0 | 0 graded | 5 flora rendered, fauna none found | bedazzle sitting done |
| 9 | Miasma | 9 | 0 | 4 (`Mantrap`, `DecayDrake`, `Thermadon`, `VFEI2_Swarmling`) | 3 override, 1 rendered, 1 queued | donor rows PROPOSED only (2026-09-23) |
| 10 | Warscar | 6 | 0 | 0 (but tied to two donors) | 1 override | none found |
| 11 | Flooded Canyon | 5 | 1 (+1 likely) | 0 | 4 rendered | none found |
| 12 | Greentide · Fever Wood | 3 · 3 | 1 · 0 | 1 · 0 | mixed | Fever Wood rows include 2 canon plants |
| 13 | Blue Desert · The Chill · Rust Cathedral · Twilight Sea · Webwork | 2·2·1·1·1 | 0 | `AA_Thunderbeast`, `GR_Mecharat` | none found, except Webwork (rendered) | singles |
| — | Contagion, Gelatinous Slime, Grey Sea, Lantern Deeps, Long Shade, Pyrelands, Stillsand, The Scald, Wasteland | **0** | — | — | — | already donor-free in the shipping layer |

`AA_LuciferBug`, `AA_Radyak`, `AA_RipperHound`, `AA_ColossalAerofleet`, `Tibidee`, `Silooth`, `Snoruuk`,
`Vapaad`, the IronScruff grasses, `AG_*` and `GRimMoss` arrived after the 2026-09-24/25 cost census.
They are **ungraded**, so grade each one inside its biome's unit.

## 5. What each step needs from the owner (as simple choices)

1. **Creatures we have already remade (12+).** Our versions currently live in the Star Wars add-on.
   Until each biome's review, should the free biome mod: **(a)** keep showing the borrowed original,
   so the campaign swaps in ours and nothing gets thinner; or **(b)** drop the original now, which
   makes the free mod thinner until that biome's review moves ours in?
2. **The Sump's four replacements are built and drawn.** **(a)** Swap them in now, as an exception to
   the pause; or **(b)** wait for the Sump review.
3. **Order of the biomes after that.** **(a)** Finished art first (Abyss, Rot, Leaning Scrub); **(b)**
   the biggest borrowed cast first (Abyss, Rot, Cauldron); or **(c)** simply follow the bedazzle
   sittings as they come.
4. **Creatures whose special trick lives in the other modder's code** (15 Alpha Animals creatures, the
   3 dryads, swarmlings, mecharat). These come up one at a time at each biome's review, never as a
   blanket rule. For each one: keep the look and lose the trick, rebuild the trick in our code, or
   replace the creature.
5. **Last Star Wars animal-mod rows (7).** Remake each of them as ours, or drop it from the biome?
6. **Two one-word answers already owed.** Is `Rat` in the desert still to be replaced, given it only
   arrives with wreckage? And do "those two beasts" in the Abyss mean the ghorrumak and the zhurrakor?

⛔ No question here asks him to rule on a category or a procedure. If an answer starts producing
sub-questions, stop and go back to the biome's review sheet (the `BIOME_SPECIFIC_FAUNA_LAW_1` lesson).

## 6. Build pause: allowed now vs needs his exception

| step | under the pause (`debug_process.md` §1) |
|---|---|
| A: guards, mis-guard fixes | **allowed.** It is a load-safety bug fix to existing mods, with no new content or membership. If he reads it as content, it waits |
| re-run `label_collision_check.py`, this census, art searches | **allowed.** These are measurements, not builds |
| putting already-rendered art in front of him (review sheets) | **allowed.** Nothing gets built. It does spend his time, so it happens when he chooses |
| B1 Sump swap, B2 swaps, B3 remakes | **needs his exception.** Roster and biome work are stopped |
| C per-biome ports, any new art job for a port | **needs his exception** (new defs, and art for unbuilt content) |
| D donor-absent load rounds | **needs his exception.** Only first-script load rounds are allowed, and the test is meaningless before the paint anyway |

The pause lifts when every mod has a first script and a recorded live run
(`NORTHSTAR_EVERYWHERE_PROGRAM_1`). With no exception granted, Step A runs now and B onward waits for
that.
