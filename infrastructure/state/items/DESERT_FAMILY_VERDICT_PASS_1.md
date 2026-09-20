# DESERT_FAMILY_VERDICT_PASS_1 — the desert family's flora/fauna pass

## why this biome, and why these three together

Owner picked it 2026-09-20, from a card, after the Rot / Lantern Deeps /
Pyrelands passes: *"Then let's push on then next biome."*

Tile counts MEASURED from `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows):

| biome | tiles | ours | 3rd-party | unguarded |
|---|---:|---:|---:|---:|
| `RUT_ExtremeDesert` | 3,969 | 0 | 22 | 3 |
| `RUT_Desert` | 2,390 | 1 | 54 | 7 |
| `RUT_AridShrubland` | 628 | 2 | 51 | 11 |
| **family total** | **6,987** | **3** | **127** | **21** |

Roster ownership MEASURED 2026-09-20 off each entry's `MayRequire` packageId —
full method and the planet-wide table in `infrastructure/state/facts/biome_rosters.md`.
One sheet covers all three because they share a roster; every row records which
of the three it belongs to.

🔴 **`RUT_BlueDesert` (1,029 tiles) is OUT of this item — but it is a GAP, not a
finished biome.** Its tables are empty because the life it was commissioned to
have was **never authored**: the owner ratified a whole hydrocarbon biology for
it (Swallowers, Burners, Pickers, transparent fractal flora), and the def's own
comment says the densities are zeroed only "until Swallowers/Burners/Pickers and
the transparent fractal flora exist". It is out of THIS item because a verdict
pass rules on roster entries that already exist and it has none — it needs
**authoring**, tracked separately at `BLUE_DESERT_LIFE_AUTHORING_1`.

⚠️ This window first recorded it as "deliberately sterile by design" and told
both the owner and a running subagent so. The owner corrected it. Do not restate
the sterile reading.

`RUT_AridShrubland` took its slot here: it shares the family's roster and is the
second-heaviest third-party donor load on the planet.

⛔ `RUT_Wasteland` (1,853) is ADJACENT and out of scope — the obvious next pass,
not this one.

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
- 🔴 **These wild tables are ELEMENT-KEYED, not `<li>`-keyed.** An entry is
  `<Bantha MayRequire="mlie.starwarsanimalcollection">0.8</Bantha>`. A parser
  looking for `<li>` returns zero rows for every biome — hit exactly that way
  2026-09-20.
- 🔴 **Never infer a donor from the defName prefix.** `mlie.starwarsanimalcollection`
  ships BARE defNames (`Bantha`, `Kreetle`, `Scavrat`, `Shyrack`, `Gorg`,
  `Gutkurr`, `Jamel`, `Rat`), so a prefix rule buckets the planet's single
  largest donor as vanilla Core. Read the `MayRequire` attribute.
- The family's **unguarded** entries (no `MayRequire`, not ours) include real
  donor defs — `AB_HardyGrass`, `AB_Aaklac`, `AB_DessertTree`, `AB_GiantStikehr`,
  and four `RG_Plant_*`. Those are what break when a donor is retired. Listed in
  the facts file; not yet ruled a defect.

## verify

The sheet renders every flora and fauna row of all three defs with a real
thumbnail or an explicit reason it has none; the owner's verdicts are applied and
confirmed from a post-load def dump, not from the patch file (a
`PatchOperationConditional` returns true on no match, so a clean log proves
nothing).

## criteria

All three desert defs carry owner-ruled names, sizes and rosters; every verdict
that called for new art has landed; the owner has walked the result in game.
