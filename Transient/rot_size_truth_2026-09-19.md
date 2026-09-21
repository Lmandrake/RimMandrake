# Rot review sheet — true in-game rendered size (2026-09-19)

Measurement pass over the 50 rows of
`/mnt/d/Luke/dev/Rimworld/src/RimUtinni/RotSporeKit/build_review_sheet.py`
(`FLORA_VSR` / `FLORA_MESH` / `FAUNA_DRAWSIZE`, lines 60–155).

Method: every def re-resolved through its full `ParentName` chain by an XML
parser (not a text scan) over the 1.6 load folders only — Core/Royalty/…,
AlphaBiomes `1841354677/1.6`, AlphaAnimals `1541721856/1.6`, the repo mods and
the live `Mods` folder. Two baselines are reported because the owner's ruling
`ROT_FLORA_FAUNA_VERDICTS_1` landed at `df261b2bc` (2026-09-19) and moved many
of these numbers *after* the sheet was reviewed:

- **true@sheet** — the def as it stood at the sheet's commit (`34a579a6c`,
  2026-09-18, i.e. `df261b2bc^`). This is what the sheet *should* have shown.
- **true@live** — the def as it loads today, `RotSpecies_NamesAndSizes.xml`
  patch included. This is what the game renders now.

## Verdict

**The FLORA table is the wrong one; the FAUNA table was right.** All 10 fauna
rows displayed exactly the adult `drawSize` the def carried on the day the
sheet was built (10/10 MATCH). 11 of the 40 flora rows were wrong, every one of
them an `AB_` AlphaBiomes donor, understated by up to **6×** (`AB_GiantAgarilux`
shown at 1.0 cell, actually 6). The single mechanism: the sheet's donor-def
reader extracted each `<ThingDef>` block **as text**, and AlphaBiomes puts a
nested `<descriptionHyperlinks><ThingDef>…</ThingDef></descriptionHyperlinks>`
early in the def — so the extractor's closing `</ThingDef>` fired inside the
hyperlink list and truncated the def *before* `<plant>`. `visualSizeRange` then
read as absent, and the script recorded the vanilla `PlantBaseNonEdible`
fallback `0.3~1.00` as if it had been measured (the comment at lines 80–94 calls
this "fully resolved… none fall back to a guess"). The predicate is exact:
**13 of 13** AB donor rows — the 11 wrong ones have `descriptionHyperlinks`
before `<plant>`, the 2 correct ones (`AB_Bryolux`, `AB_AgariluxPrime`) do not.
Ignorance was written down as a measurement.

Separately, and not the sheet's fault: the owner's own ruling has since moved
**5 of 10 creature sizes and 24 of 40 plant sizes** away from the numbers he saw.
Both lists are in §5.

## The rule RimWorld actually applies

**Animals** (MEASURED via RimSage, RimWorld 1.6 source):

- `Verse/PawnRenderNode_AnimalPart.MeshSetFor` → `MeshPool.GetMeshSetForSize(graphic.drawSize.x, graphic.drawSize.y)`,
  where `GraphicFor` reads `pawn.ageTracker.CurKindLifeStage.bodyGraphicData.Graphic`.
  So the rendered quad is **the PawnKindDef's current life-stage `bodyGraphicData/drawSize`, verbatim, in cells**.
- `Verse/PawnRenderNodeWorker.ScaleFor` multiplies only by `node.Props.drawSize`
  (default `Vector2.one`) and animation/drawData scale — **no body-size term**.
- `RimWorld/LifeStageDef` has **no `bodyGraphicData` field at all** (only
  `silhouetteGraphicData`), so the race's `lifeStageAges` LifeStageDefs cannot
  contribute a body graphic.
- `LifeStageDef.bodySizeFactor` feeds `Pawn.BodySize`
  (`Verse/Pawn.cs:2499 — ageTracker.CurLifeStage.bodySizeFactor * RaceProps.baseBodySize`),
  a **stat**, not the render. It appears in render-adjacent code only for
  *attachments* (`Verse/MoteAttached.cs:51-52`) and the targeting reticle
  (`RimWorld/TargetHighlighter.cs:67`) — never for the body quad.
- All 10 races here declare 3 PawnKindDef life stages against 3 `lifeStageAges`,
  so **the adult is `lifeStages/li[3]`** and the sheet's "last life stage" rule is right.

**Plants** (`RimWorld/Plant.Print`, lines ~950-1067):

```
num2 = def.plant.visualSizeRange.LerpThroughRange(growthInt);
num3 = def.graphicData.drawSize.x * num2;      // side of the printed quad, in cells
```

At `growth == 1.0` that is exactly `drawSize.x * visualSizeRange.max` — the
sheet's `mature_cells_flora` formula is **correct**, and its claim that
`graphicData/drawSize` is unset (→ `1.0`) on all 40 flora defs is **confirmed**
(no def in any of the 40 chains declares it). Only the inputs were wrong.
`maxMeshCount` tiles that many copies on a `sqrt(n)` sub-grid *inside one cell*;
it does not widen the plant.

## Fauna table

`displayed` / `true@sheet` / `true@live` are adult `bodyGraphicData/drawSize` in cells.

| defName | displayed | true@sheet | agree? | true@live | why |
|---|---|---|---|---|---|
| RSW_FungalWeevil | 1.8 | 1.8 | MATCH | **4.0** | own def, `SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`; raised 1.8→4 in the ruling commit `df261b2bc` |
| AA_Swarmling | 1.75 | 1.75 | MATCH | **0.5** | AlphaAnimals `1.6/Defs/ThingDefs_Races/Races_Swarmling.xml`; patched down by `RotSpecies_NamesAndSizes.xml` (chittik) |
| AA_Agaripod | 3.8 | 3.8 | MATCH | 3.8 | AlphaAnimals `Races_Agaripod.xml`; "keep + rename" (gromma), no size op |
| AA_MycoidColossus | 6.0 | 6.0 | MATCH | **15** | AlphaAnimals `Races_MycoidColossus.xml`; patched up (vorrugath) |
| RSW_BovineBeetle | 3.0 | 3.0 | MATCH | 3.0 | own def; unchanged. (Note: **not in `RUT_TheRot`'s `<wildAnimals>`** — see §6) |
| AA_Agaripawn | 2.0 | 2.0 | MATCH | **7** | AlphaAnimals `Races_Agaripawn.xml`; patched up (rennok) |
| AA_Wildpawn | 2.0 | 2.0 | MATCH | **6** | AlphaAnimals `Races_Wildpawn.xml`; patched up (durrok) |
| AA_Wildpod | 3.8 | 3.8 | MATCH | **5** | AlphaAnimals `Races_Wildpod.xml`; patched up (mullgoth) |
| RSW_FungalMantis | 3.0 | 3.0 | MATCH | 3.0 | own def; rename only |
| RUT_Emberscythe | 2.2 | 2.2 | MATCH | 2.2 | own def, `RotSporeKit/Defs/ThingDefs_Races/RUT_Emberscythe.xml`; unchanged |

**0 of 10 wrong at display time.** The name-collision trap was checked: every one
of these strings is BOTH a `ThingDef` and a `PawnKindDef`, and the sheet read the
right one (the PawnKindDef). `race/baseBodySize` (the ThingDef number) is a
different quantity and was printed separately, correctly labelled.

## Flora table

`displayed` = `FLORA_VSR[max] × drawSize 1.0` = mature cells. `drawSize` is 1.0
on all 40 (confirmed; no chain declares `graphicData/drawSize`).

| defName | displayed | true@sheet | agree? | true@live | why |
|---|---|---|---|---|---|
| AB_Bryolux | 0.95 | 0.95 | MATCH | 0.95 | own `visualSizeRange 0.82~0.95` read correctly |
| AB_Glowstool | 1.0 | **0.7** | WRONG −0.3 | 0.7 | own `0.4~0.7`; missed → PlantBase fallback |
| AB_Agarilux | 1.0 | **1.5** | WRONG +0.5 | 1.5 | own `0.9~1.5`; missed |
| AB_GiantAgarilux | 1.0 | **6** | WRONG +5 (6×) | 6 | own `3.5~6`; missed |
| AB_GlowingAgarilux | 1.0 | **2** | WRONG +1 | 4 | own `1.3~2`; missed. Live patched to `2.6~4` |
| AB_LilacBeacon | 1.0 | **2** | WRONG +1 | 3 | own `1~2`; missed. Live `1.5~3` |
| AB_WitchesOyster | 1.0 | **2** | WRONG +1 | 6 | own `1~2`; missed. Live `3~6` |
| AB_RecurvedStropharia | 1.0 | **5** | WRONG +4 (5×) | 5 | own `3.5~5`; missed |
| AB_ArbuscularMycorrhiza | 1.0 | **3.5** | WRONG +2.5 | 9 | own `2~3.5`; missed. Live `5.14~9` |
| AB_SlimyPholiota | 1.0 | **5** | WRONG +4 (5×) | 5 | own `3.5~5`; missed |
| AB_AgaricusDomeCap | 1.0 | **2** | WRONG +1 | 7 | own `1.5~2`; missed. Live `5.25~7` |
| AB_DribblingCap | 1.0 | **5** | WRONG +4 (5×) | 12 | own `3.5~5`; missed. Live `8.4~12` |
| AB_AgariluxPrime | 8.0 | 8 | MATCH | 20 | own `7.95~8` read correctly. Live `19.88~20` |
| RUT_Dewshrooms | 0.5 | 0.5 | MATCH | 0.5 | own def |
| RUT_FruitingBodies | 0.5 | 0.5 | MATCH | 0.5 | own def |
| RUT_Nuitae | 0.6 | 0.6 | MATCH | 1.0 | own def; ruling raised to `0.67~1` |
| RUT_Wrinklecap | 0.85 | 0.85 | MATCH | 0.9 | ruling → `0.74~0.9` |
| RUT_Arpeau | 2.5 | 2.5 | MATCH | 10 | ruling → `6~10` |
| RUT_Nogtyl | 2.5 | 2.5 | MATCH | 12 | ruling → `7.2~12` |
| RUT_FlakespireFungus | 2.0 | 2.0 | MATCH | 3 | inherited `TreeBase 1.5~2.0` at sheet time — correctly resolved. Ruling → own `0.9~3` |
| RUT_Pusmelon | 0.7 | 0.7 | MATCH | 1.0 | ruling → `0.43~1` |
| RUT_RustPuff | 0.6 | 0.6 | MATCH | 0.6 | unchanged |
| RUT_Sagecrust | 0.5 | 0.5 | MATCH | 0.5 | unchanged |
| RUT_BleedingTooth | 1.0 | 1.0 | MATCH | 2 | inherited `PlantBaseNonEdible 0.3~1.00` at sheet time — correctly resolved. Ruling → own `0.6~2` |
| RUT_Brightbell | 0.7 | 0.7 | MATCH | 1.5 | ruling → `0.64~1.5` |
| RUT_CrimsonCap | 1.0 | 1.0 | MATCH | 2 | ruling → `1.6~2` |
| RUT_GreyLady | 1.0 | 1.0 | MATCH | 1.0 | unchanged |
| RUT_Shinecap | 2.5 | 2.5 | MATCH | 4 | ruling → `2.4~4` |
| RUT_VioletWimple | 0.7 | 0.7 | MATCH | 2 | ruling → `0.86~2` |
| RUT_MortalMorelPlant | 1.0 | 1.0 | MATCH | 0.8 | ruling → `0.48~0.8` |
| RUT_Skulltop | 0.7 | 0.7 | MATCH | 0.7 | unchanged |
| RUT_BlastpodShroom | 0.9 | 0.9 | MATCH | 0.9 | unchanged |
| RUT_PaleTree | 2.5 | 2.5 | MATCH | 6 | ruling → `4.32~6` |
| RUT_AgelessCap | 1.6 | 1.6 | MATCH | 1.6 | unchanged |
| RUT_RegenerantVeil | 1.3 | 1.3 | MATCH | 1.3 | unchanged |
| RUT_EuphoricCrown | 1.5 | 1.5 | MATCH | 1.5 | unchanged |
| RUT_FalseFruit | 0.6 | 0.6 | MATCH | 0.6 | unchanged |
| RUT_DulcisPlant | 1.3 | 1.3 | MATCH | 3 | ruling → `1.15~3` |
| RUT_FurnaceCap | 1.0 | 1.0 | MATCH | 2 | ruling → `1.0~2` |
| RUT_PaleMoss | 0.45 | 0.45 | MATCH | 0.45 | unchanged |

**11 of 40 wrong** — all `AB_`, all the same defect. All 27 `RUT_` rows and 2 of
13 `AB_` rows were exactly right.

`FLORA_MESH` spot-checked against the resolved `plant/maxMeshCount`: every entry
in the dict matches the def, and no row outside the dict declares one. Not a
source of error.

## The subset that must be re-judged

### A. Rows whose DISPLAYED number was wrong (the sheet lied to him) — 11 rows, all flora

He judged these against a picture drawn at `displayed`. The size he was actually
looking at in game on review day is `true@sheet`.

| defName | label on sheet | he saw | it really was | now (live) |
|---|---|---|---|---|
| AB_GiantAgarilux | giant agarilux | 1.0 | **6** | 6 |
| AB_RecurvedStropharia | recurved stropharia | 1.0 | **5** | 5 |
| AB_SlimyPholiota | slimy pholiota | 1.0 | **5** | 5 |
| AB_DribblingCap | dribbling cap | 1.0 | **5** | 12 |
| AB_ArbuscularMycorrhiza | arbuscular mycorrhiza | 1.0 | **3.5** | 9 |
| AB_AgaricusDomeCap | agaricus domecap | 1.0 | **2** | 7 |
| AB_GlowingAgarilux | glowing agarilux | 1.0 | **2** | 4 |
| AB_LilacBeacon | lilac beacon | 1.0 | **2** | 3 |
| AB_WitchesOyster | witches' oyster | 1.0 | **2** | 6 |
| AB_Agarilux | agarilux | 1.0 | **1.5** | 1.5 |
| AB_Glowstool | glowstool | 1.0 | **0.7** | 0.7 |

### B. Rows whose number has MOVED since he judged (ruling `ROT_FLORA_FAUNA_VERDICTS_1`, `df261b2bc`)

Not a sheet defect — but if he is re-judging sizes, these are no longer what the
sheet showed. **5 creatures**: `AA_Agaripawn` 2→**7**, `AA_Wildpawn` 2→**6**,
`AA_Wildpod` 3.8→**5**, `AA_MycoidColossus` 6→**15**, `AA_Swarmling` 1.75→**0.5**,
plus `RSW_FungalWeevil` 1.8→**4** (6 rows in total if the weevil is counted —
it moved in the same commit, by direct edit rather than by patch).
**Plants**: `RUT_Arpeau` 2.5→10, `RUT_Nogtyl` 2.5→12, `RUT_PaleTree` 2.5→6,
`RUT_Shinecap` 2.5→4, `RUT_FlakespireFungus` 2→3, `RUT_DulcisPlant` 1.3→3,
`RUT_CrimsonCap` 1→2, `RUT_FurnaceCap` 1→2, `RUT_BleedingTooth` 1→2,
`RUT_VioletWimple` 0.7→2, `RUT_Brightbell` 0.7→1.5, `RUT_Nuitae` 0.6→1,
`RUT_Pusmelon` 0.7→1, `RUT_Wrinklecap` 0.85→0.9, `RUT_MortalMorelPlant` 1→0.8,
`AB_AgariluxPrime` 8→20, and the AB rows already listed in A.

## What I could not measure

- **Why the sheet's author entered `1.8` etc. by hand.** The dicts are hardcoded;
  no generator survives that would show the exact extractor. The
  `descriptionHyperlinks` predicate matches 13/13, which is strong, but it is
  inferred from the data, not read from code. Marked as the mechanism with that
  caveat.
- **Nothing was verified against a running game.** Every number here is
  def-resolved and engine-source-justified; no live spawn/screenshot was taken.
- `RUT_TheRot`'s `<wildAnimals>` measured **8** entries (parsed, not grepped);
  the sheet's header says 9 and lists 10 rows. `RSW_BovineBeetle` and
  `RUT_Emberscythe` are not in the biome's wild list, and no patch adding
  `RSW_BovineBeetle` was found. Flagged, not chased — it is a roster question,
  not a size question.

### Confirmations for `true@live`

- `ModsConfig.xml` parsed (not grepped): **621 active mods**; `mandrake.rut.patches`
  (UtinniPatches), `sarg.alphabiomes`, `sarg.alphaanimals`, `mandrake.rut.rotsporekit`
  and `mandrake.rsw.swbestiary` are all active — so `RotSpecies_NamesAndSizes.xml`
  does load, and its `PatchOperationConditional` guards all match.
- `AgaripodArtOverride`, `MycoidColossusArtOverride` and `WildpodArtOverride` in the
  live `Mods` folder contain **only `About/About.xml` and textures** — no Defs, no
  Patches. They cannot affect size.
- AlphaBiomes/AlphaAnimals `loadFolders.xml` were read: under 1.6 only `/` and `1.6`
  load. The `1.5` trees were excluded; reading them would have given different
  numbers (e.g. AlphaBiomes 1.5 `Plants_MycoticJungle.xml` differs).
