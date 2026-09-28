# WASTELAND_RULED_CONTENT_1 — build the survivor cast: full RM_ donor replacement

Ruled at `WASTELAND_BEDAZZLE_SITTING_1` (2026-09-27/28; owner-typed rulings on its
ledger, "Full accept. Bedazzled!"). **The authority is the cast bible:**
`design/Jawa/worldbuilding/biomes/wasteland_survivor_cast_2026-09-28.md` — per-def
hooks, stats sketches, diets, commonalities, wiring notes. The sheet amendment
(2026-09-28 block in `wasteland.md`) admits the new natives and revises the
register to survivors-not-sufferers. Art: 21 jobs queued
(`wasteland_survivor_cast.csv`); renders come back as a BENCH review sheet — wire
art as it is ruled kept.

## Scope

1. **Full RM_ port of the donor cast** — new ThingDef/PawnKindDef pairs (one file
   per species in `src/RimMandrake/Wasteland/Defs/ThingDefs_Races/`): Scumrat,
   Slagmole, Scabspinner, Boilhide, Middenbeetle, Gristleswarm + Soot
   Gristleswarm (own variant def `RM_SootGristleswarm`), Gravelgut. NOT patches:
   donor rows leave `RM_Wasteland_Biome.xml` in the same commit ours land, at the
   bible §7 commonalities. Boilhide replaces the vanilla Toxalope row (row
   dropped, vanilla def untouched).
2. **New species**: Sloghog, Sootgrazer, Smolderback (stats/diet per bible §3 —
   their comps are `WASTELAND_MECHANICS_BUILD_1`'s; defs land here with the comp
   hookup points stubbed to whatever that item ships).
3. **Flora ports** (`Defs/ThingDefs_Plants/RM_WastelandFlora.xml`): Scumgrass,
   Tall Scumgrass, Pusberry, Boilbulb, Wartshrub + the NEW Cinderfelt (def only;
   its storm-germination wiring is the mechanics item's — ship the 0.02
   wildPlants fallback row so it is never dead content).
4. **Item defs**: `RM_ContaminantBezoar`, `RM_VitrifiedBezoar`, `RM_SootBrick`.
5. **Brine trio label-only renames** — defNames FROZEN (canonical save):
   labels/descriptions only, drazz→brineleech, tekk→sparkcrab, deposit-bed labels
   follow (bible §5).
6. **TexPath rescue**: copy the finished `done/`/`_artsrc/` renders for
   DosimeterLawn and VaultRoot into this mod's `Textures/` at the defs' texPaths
   (both currently resolve to no PNG in the repo — bible §8).
7. Roster rewiring: shorthand element form throughout (`<RM_Scumrat>0.7</…>`,
   never `<li>`); the mod ends the build with zero donor references in its
   roster. The `RUT_` twin's patch-added campaign roster is NOT this item's
   scope (`MLIE_ABSORPTION_BIOME_WIRING_1` family).

## Watch out

- `<li>` in wildAnimals/wildPlants silently discards the def — shorthand form only.
- animalDensity/plantDensity must stay explicitly set on the biome def (an unset
  animalDensity defaults 0f and kills the whole roster — the PropaneLake lesson).
- The Middenshell is NOT a roster row and NOT this item — it ships with the
  titanic wiring in `WASTELAND_MECHANICS_BUILD_1`.
- Ban sweep before close (sheet §6): no anomaly flavor, no weapon-organism
  framing, wildlife never the headline threat, everything visibly marked, nothing
  rain- or spoilage-dependent.
- Register sweep: no pity language in any label or description — every entry
  reads as a creature that WON.

## verify

- Donor defNames absent from `RM_Wasteland_Biome.xml`'s roster; every ruled name
  present at the ruled commonality (measured, not assumed).
- A quicktest map spawns the cast; DosimeterLawn/VaultRoot render (texPath
  resolves); brine items show the new labels.
