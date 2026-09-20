# BIOME_BINDINGS_TABLE_STALE_1 — the def→sheet table points 25 of 29 rows at dead defs

## what is wrong

`design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md` is the table an
agent consults to answer *"which BiomeDef owns this biome's fauna and flora?"*
Its own header calls its tile counts "the caller's MEASURED figures".

They are no longer true. MEASURED 2026-09-20 against
`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles, 27 distinct painted biomes):

- **25 of 29 rows name a defName that carries ZERO painted tiles.**
- 2 more rows name a live def with a wrong tile count (`RUT_TwilightSea` doc 479
  / live 607; `RUT_GreySea` doc 429 / live 472).
- **4 rows are correct**: `RUT_NightsideIce`, `RUT_TheScald`, `ZBiome_Grasslands`,
  `RUT_PropaneLake`.

The cause is not drift. **The world was repainted onto our own `RUT_*` biome
defs after the table was written**; every painted def but one is now `RUT_*`.
The table still names the donor and vanilla defs it was compiled from —
`Desert`, `ExtremeDesert`, `AB_PropaneLakes`, `AB_MycoticJungle`, `Wasteland`,
`BiomeGRimond`, `ZBiome_Badlands`, `AridShrubland`, `PoisonForest` and 16 more.

It is also wrong about ownership: it names
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` as the `wildAnimals`
owner for the deserts. That file contains no `Desert` reference at all — the
def files own those tables now.

## why it matters

🔴 **This is the `PYRELANDS_WRONG_BIOME_DEF_1` defect with a supply chain.** That
item records content built perfectly onto `RM_FE_Pyrelands`, a def carrying 0 of
21,872 tiles. This table is *how an agent would choose that def*. Anyone doing a
fauna/flora pass who trusts it wires their work onto a biome no player visits,
and every check they run passes, because the def is real — it just has no ground.

The one surviving non-`RUT_` painted def is `ZBiome_Grasslands` (222 tiles) —
precisely the biome `PYRELANDS_WRONG_BIOME_DEF_1` says the player actually
visits. The two findings corroborate each other.

## the fix

Regenerate the `def` and `tiles` columns from the painted CSV, **keeping the
sheet-binding column**, which is human knowledge and still good. The mapping from
each old row to its `RUT_*` successor must be **proved per row** — match the
sheet to the biome def's `<label>`, do not infer from name similarity. Several
are not obvious (`AB_MycoticJungle` → `RUT_TheRot`, `ZBiome_Badlands` →
`RUT_CrackedLands`, `BiomeGRimond` → `RUT_BlueDesert`).

Where a row's successor cannot be proved, **delete the row and say so** rather
than guessing — per the standing rule, inaccurate material is removed, not
annotated.

## Watch out

- ⚠️ **The CSV is one instrument, not two.** `GRASSLANDS_TILES_CSV_STALE_1` is an
  open item saying this very CSV disagrees with a live measurement on Grasslands
  vs Pyrelands. The 21,872 total and the all-`RUT_` shape corroborate
  `PYRELANDS_WRONG_BIOME_DEF_1`, which is why this item treats the CSV as good
  enough to act on — but a live world read is the confirming instrument and has
  not been run. Close `GRASSLANDS_TILES_CSV_STALE_1` first if you can.
- ⚠️ **Do not "fix" a row by repainting the world.** The world is frozen and
  hand-authored; the def follows the paint, never the reverse.
- 🔑 **Check what else cites this table** before trusting any doc downstream of
  it. A wrong owning-def answer propagates silently.
- ✅ The two desert rows were corrected in place on 2026-09-20 as part of the
  desert review, so `RUT_Desert` (2,390) and `RUT_ExtremeDesert` (3,969) are
  already right; the other 23 are not.

## verify

Every row's `def` appears in the painted CSV with a tile count equal to the
row's, or the row is gone. No row names a def with zero painted tiles.

## criteria

An agent picking an owning BiomeDef from this table wires content onto ground a
player stands on.
