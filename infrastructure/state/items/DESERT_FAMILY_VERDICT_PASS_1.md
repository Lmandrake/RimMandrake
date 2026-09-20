# DESERT_FAMILY_VERDICT_PASS_1 — the desert family's flora/fauna pass

## why this biome, and why these three together

Owner picked it 2026-09-20, from a card, after the Rot / Lantern Deeps /
Pyrelands passes: *"Then let's push on then next biome."*

Tile counts MEASURED from `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows):

| biome | tiles |
|---|---:|
| `RUT_ExtremeDesert` | 3,969 |
| `RUT_Desert` | 2,390 |
| `RUT_BlueDesert` | 1,029 |
| **family total** | **7,388** |

That is a third of the planet, and it is where the player starts. One sheet
covers all three because they share a roster problem; every row still records
which of the three it belongs to.

⛔ `RUT_Wasteland` (1,853) and `RUT_AridShrubland` (628) are ADJACENT and out of
scope for this item. They share the family's roster and are the obvious next
pass — do not let them creep in here.

## spec

The shape the Rot and the Lantern Deeps both used, in order:

1. **Sheet** — flora + fauna of all three defs, one HTML review sheet with real
   sprite thumbnails, current label, size, commonality, and an ORIGIN column
   (ours vs which donor mod). The origin column is the point: donor retirement
   is the owner's stated driver.
2. **Owner verdicts** — he rules keep / cut / rename / regen / resize, into the
   sheet's frozen `.decisions.json` sidecar.
3. **Apply** — labels, descriptions, `visualSizeRange` for flora, adult-stage
   `bodyGraphicData.drawSize` for fauna, and cuts from `<wildPlants>` /
   `<wildAnimals>`. Donor defs get ONE patch file, gated the way
   `RotSpecies_NamesAndSizes.xml` is.
4. **Art** — regen jobs filed through `fill_queue.py` only, never hand-written.
5. **Land** — review each render by eye, wire texPaths, validate, deploy.
6. **Live look** — the owner walks it.

## known blocker, inherited

`BIOME_ENRICHMENT_DESERT_WASTELAND_1` (FOUNDRY's, BLOCKED) already measured that
**`desert.md` names zero RimWorld defNames** and `wasteland.md`'s injection
palette is thematic categories, not defNames — so the enrichment half of the
desert cannot be executed without someone inventing the kit. That is an owner
ruling, and it is a different question from this item's flora/fauna verdicts.
🔑 This item is NOT blocked on it: the roster pass can run on the defs that
already exist. Keep the two apart.

## Watch out

- 🔴 **Do not parse def XML as text.** The first Rot sheet understated 11 rows by
  up to 6× because Alpha Biomes nests `<descriptionHyperlinks><ThingDef>` early
  in a def and a string-matched close tag fired inside it. The owner had to
  re-judge. Use `xml.etree.ElementTree`.
- 🔴 **Fauna size is the ADULT life stage, `lifeStages/li[3]`** — reading `[0]`
  gives the baby and has already produced one wrong ruling here.
- The def dump carries **no `statBases`**; sizes calibrate from mod XML.
- A def whose texPath resolves to no loose PNG is usually **vanilla art**, not
  missing art — `resources.assets`, per `reading-rimworld-graphics`.
- The desert sheets' own rule is that the roster should look *sparse to the
  point of discomfort* ("if the roster looks healthy, it is wrong",
  `biomes/_assignment_prep.md` §1). Do not read a thin result as a parser bug —
  but do not read a parser bug as a thin result either. Check which it is.

## verify

The sheet renders every flora and fauna row of all three defs with a real
thumbnail or an explicit reason it has none; the owner's verdicts are applied and
confirmed from a post-load def dump, not from the patch file (a
`PatchOperationConditional` returns true on no match, so a clean log proves
nothing).

## criteria

All three desert defs carry owner-ruled names, sizes and rosters; every verdict
that called for new art has landed; the owner has walked the result in game.
