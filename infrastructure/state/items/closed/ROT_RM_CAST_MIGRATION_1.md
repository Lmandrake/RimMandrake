# ROT_RM_CAST_MIGRATION_1 — move the ten ratified creatures into the free Rot mod as `RM_` defs, with hybrid descriptions and real flight for the illoth

Caused by `ROT_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.therot` (`src/RimMandrake/TheRot/`; folds
into `RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`), plus the campaign patch it empties
(`src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml`). Design:
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §1 (a), §3, §4 row 0, §8; the ruled
migration table `design/Jawa/worldbuilding/biomes/rot_rm_cast_proposal_2026-09-24.md` (rulings, decision
taken by question card 2026-09-24). Ruling: **build first: land the decided work plus the giant** (decision
taken by question card 2026-10-02 10:20 PDT). Nothing here is new design: it executes the 2026-09-24 card,
which `THEROT_RM_MOD_BUILD_1` closed without doing. Sheet bans bind: **ban 2, every resident a fungus/animal
hybrid**; **ban 7, no engineered organisms**.

## spec

1. **Ten `RM_` defs** (ThingDef race + PawnKindDef each), bodies copied from
   `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`, names from the
   ratified table:

   | campaign row today | becomes | label |
   |---|---|---|
   | `RSW_PustuleHornet` | `RM_Thozzik` | thozzik |
   | `RSW_ColonyPustuleHornet` | `RM_ThozzikColony` | thozzik |
   | `RSW_PustuleHornetSpawned` | `RM_ThozzikSpawned` | thozzik |
   | `RSW_PustuleHornetQueen` | `RM_ThozzikQueen` | thozzik queen |
   | `RSW_ColonyPustuleHornetQueen` | `RM_ThozzikColonyQueen` | thozzik queen |
   | `RSW_SmogMoth` | `RM_Illoth` | illoth |
   | `RSW_Thrumbungus` | `RM_Brullith` | brullith |
   | `RSW_Yooka` | `RM_Brogg` | brogg |
   | `RSW_FungalWeevil` | `RM_Grellik` | grellik |
   | `RSW_FungalMantis` | `RM_Skerrith` | skerrith |

   Any `ThingDef` the bodies reference that lives only in the bestiary (butcher products, hive buildings, the
   queens' spawn links, the gas the hornets release; read `RSW_BiomesTeamPort_Items.xml`) is copied into the
   free mod under an `RM_` name, so the free mod has **no** `mandrake.rsw.*` dependency (Q11a: the free mod
   stands alone). C# types the bodies name are listed first; a type from an assembly the free mod does not
   load is a discarded def (CLAUDE.md, debug-game trap 3), so measure each `<thingClass>`/comp class and port
   or replace it.
2. **Art: seven sets are done, three are redrawn.** MEASURED 2026-10-02 with `artpipe_state.py find` (probe
   `korrum` hits): finished three-facing renders in the artpipe `done/` and `_artsrc/` for
   `rot_thozzikqueen_*`, `rot_brullith_*`, `rot_skerrith_*` and `rot_fungalweevil_v2_*` (the grellik): deploy
   those PNGs into the mod's `Textures/` and point each `texPath` at them (texture binds by texPath).
   **The thozzik, illoth and brogg get NEW art** (owner, typed 2026-10-02 11:12 PDT: *"I like that they were
   hybridized, but NOT terrain animals hybridized. Our own custom creatures from other biomes."*): each is a
   fungus hybrid of one of our own invented creatures from another biome, never a wasp, moth or camel-llama.
   Jobs filed from `infrastructure/artpipe/art_lists/rot_hybrid_redraw_2026-10-02.csv` (ids `rot_thozzik_b`,
   `rot_illoth_b`, `rot_brogg_b`, three facings each): deploy those, not the old `rot_thozzik_*`, `rot_illoth_*`,
   `rot_brogg_*`. All five thozzik forms use the new thozzik set; the queens (`rot_thozzikqueen_*`, still a
   wasp-shaped render) take the new thozzik look scaled up: **a queen redraw from the same source creature is
   owed** (add `kurreth`-queen rows to the csv when the thozzik render is accepted).
   The pairings, read from creature descriptions in `src/`:
   - **thozzik = a fungus hybrid of the `RM_Kurreth`** (Fever Wood: a glossy red-black segmented dog-sized hive
     ant with forward-held mandibles; its queen `RM_KurrethQueen` is the thozzik queen's source). Fits a hive
     creature that farms a fungus inside itself.
   - **illoth = a fungus hybrid of the `RM_Vrisk`** (Blue Desert: a kite-thin, near-flat flier that rides haze
     with never-still wingtips). Fits a flying lantern-lure creature; no moth.
   - **brogg = a fungus hybrid of the `RM_Dorrak`** (Blue Desert: a six-legged slab plated like a boiler that
     grazes by closing its whole face over a plant). Fits a heavy hunched grazer carrying a mycelial store.
3. **Descriptions rewritten (ban 2, ban 7), franchise-free:**
   - **thozzik:** a hive creature built on the kurreth's armoured segmented ant body, whose toxin sacs are
     fruiting bodies of a fungus it farms inside itself; the gas it vents when hurt is that fungus's spore
     cloud. Keep the hive and queen loyalty. No wasp.
   - **illoth:** a flat kite-bodied skimmer built on the vrisk, its wing membranes fungal gills dusted with
     spore powder, a living fungal lantern hanging from its underside as the lure. No moth.
   - **brogg:** a heavy plated six-legged grazer built on the dorrak, its back a mycelial-store mound under
     layered bracket fungus, its edges shaggy with hanging hyphae. **Delete** *"closely related to camels and
     llamas"*.
   - **brullith:** **delete the lab origin** (*"created from a mix of a failed genetics experiment"*); it is a
     natural amalgam of beast and fungus. Keep its gentle-but-dangerous body.
   - **grellik, skerrith:** keep the descriptions (already hybrid).
4. **The illoth flies** (the flyers rule, 2026-09-19): `statBases MaxFlightTime` and `FlightCooldown`, race
   `flightStartChanceOnJobStart`, `flightSpeedFactor`, `canFlyIntoMap`, `canLeaveMapFlying` on the vanilla
   Locust shape. No flip-book frames are owed for this item (flight without frames is correct, plainer).
   ⛔ No live flight test without the owner present; the criteria read state.
5. **Rows inline on `RM_TheRot/wildAnimals`** (as XML elements, `<RM_Thozzik>0.5</RM_Thozzik>`), at today's
   commonalities (thozzik 0.5, thozzik colony 0.5, illoth 0.5, brullith 0.5, brogg 0.5, grellik 0.4, thozzik
   queen 0.3, colony queen 0.2, spawned 0.2, skerrith 0.15).
6. **Retire the ten `RSW_` rows** from `WildAnimals_TheRot.xml` in the same change. `RSW_ShiroTrap` and
   `Snoruuk` stay (genuine Star Wars). While there, replace the patch's top-level
   `<Operation … MayRequire=…>` guards (inert in 1.6) with `PatchOperationFindMod`
   (`PATCH_MAYREQUIRE_OPERATION_SWEEP_1`'s family).
7. **`RUT_TheRot`, the frozen twin**, keeps its `RSW_` rows untouched (frozen; repainted once at the end).
8. **References elsewhere:** `AnimalTolerances_Ashkarr.xml` names `RSW_Thrumbungus`/`RSW_Yooka`/`RSW_SmogMoth`
   (and the hornets, if listed): add the `RM_` names beside them. The `RSW_` bestiary defs are not deleted
   (other mods or saves may name them).

Depends on: nothing (land first). Blocks: `ROT_WOUND_SHARING_WIRING_1` (soft),
`ROT_HWELGRUE_GIANT_BUILD_1` (soft). `THE_ROT_FIRST_SCRIPT_1` is written against this item's state.

## criteria

Deterministic state reads through `jawa/get_defs` (reading `success`/`foundCount`/`notFound`, never a
substring) and an offline XML parse, recorded as cases in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`:
- `ThingDef/` and `PawnKindDef/` for all ten `RM_` names resolve: `foundCount` = 20.
- With only Core, the five DLCs and the free Rot's own declared dependencies loaded (no
  `mandrake.rsw.swbestiary`, no `sarg.alphaanimals`), the same 20 resolve and `Player.log` has no
  `Could not resolve` naming any of them.
- `RM_TheRot`'s merged `wildAnimals`, parsed as XML elements, contains all ten `RM_` names; the campaign
  patch file, parsed per operation, adds none of the ten `RSW_` names to `RM_TheRot` and still adds
  `RSW_ShiroTrap` and `Snoruuk`; no `<Operation>` node in it carries a `MayRequire` attribute.
- Every `RM_` description in the ten (read from the loaded def) contains no `wasp`, `hornet`, `moth`, `camel`, `llama`,
  `genetics`, `experiment` or `Force`; each of thozzik, illoth, brogg contains `fung` or `mycel` or `spore`.
- `RM_Illoth`: `MaxFlightTime` > 0 (stat read on a spawned pawn) and `Pawn_FlightTracker.CanEverFly` = true
  through a debug `[Tool]` state read.
- Each of the ten `texPath`s resolves to a texture (no magenta: a spawned pawn's graphic is not the error
  material).
</content>
</invoke>
