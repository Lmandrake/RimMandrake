# Rot flora/fauna + new-art review sheet — build report (2026-09-18)

**55 rows.** Group A (flora) 40, Group B (fauna) 10, Group C (new art, other waves) 5.
`check_sheet.py`: **0 FAIL, 1 WARN, 33 ok, exit 0** (WARN is "55 rows missing from the
decisions file" — expected, nobody has reviewed it yet).

## Cell size + to-scale panels (owner ask, latest pass)

**All 40 flora rows print `graphicData.drawSize`; all 10 fauna rows print the adult
life stage's `bodyGraphicData.drawSize` + bodySize.** MEASURED: drawSize is **1.0 ×
1.0 (vanilla default) on every single one of the 40 flora defs** — resolved every
ParentName chain (through RotSporeKit's own `PlantBases/` abstracts and AlphaBiomes'
`AB_CavePlantBase`) and confirmed by grepping the whole flora file set for the
literal string `drawSize`: it occurs exactly once, on `RUT_MedicineFungal` (an
ingredient item, not a plant). So the "ankle-high to building-sized" spread the
descriptions promise is NOT in drawSize at all — it's `<plant><visualSizeRange>`,
which scales the same 1×1 quad up at growth. Each row prints both: the literal
drawSize (as asked) and, where the def sets a visualSizeRange (28 of 40 — 12 of 13
AlphaBiomes donor rows set none), the resulting mature quad size
(drawSize × visualSizeRange.max) that the panel is actually drawn at.

**All 45 Group A/B rows that already had a thumbnail now show a TO-SCALE panel**
instead of a plain thumbnail: the sprite at its measured cell size beside a real
RimWorld colonist (`design/Jawa/worldbuilding/review/assets/human_anchor_south.png`,
1.5 cells tall — already on disk, no re-extraction needed), on a 1-cell grid,
capped at 240px wide per the owner's instruction here. Method copied (not imported)
from `src/RimMandrake/Utils/gen_plant_register.py`'s `_scale_panel`/`_human_figure`
(plants, including its mesh sub-grid for `maxMeshCount` > 1 — 13 of 40 flora rows
tile 4-25 copies) and `gen_creature_register.py`'s `_scale_panel` (fauna) — copied
rather than imported because both reference modules pull in `cherrypicker` /
`game_paths` / `rimworld_loadset` (live def-dump and Windows-path machinery) this
generator's own hand-curated ROWS tables don't need. `PX_PER_CELL` (64) and
`HUMAN_CELLS` (1.5) match those scripts exactly; only the panel cap differs (240px
here vs. 1200-1500px on those dedicated art-review pages).

**Nothing skipped**: all 45 rows with a source image got a scale panel — 35 plant
panels, 10 creature panels (the 5 Group C rows, which have no drawSize/cells
concept, kept a plain thumbnail). The 5 flora rows with no source image at all
(RUT_FalseFruit, RUT_AgelessCap, RUT_RegenerantVeil, RUT_EuphoricCrown,
RUT_FurnaceCap — see below) still print their cell-size text; there's just no panel
to build without a sprite.

**Thumbnails: 50 of 55 (up from 28).** Two coordinator corrections in sequence:
(1) Alpha Biomes and Alpha Animals ARE locally reachable, at the Workshop ids
supplied (`1841354677`, `1541721856`), plus three `*ArtOverride` mods in the game's
own Mods folder that take priority where they exist; (2) the 4 AlphaBiomes plant
rows that read as "absent" (AB_Bryolux, AB_Glowstool, AB_Agarilux,
AB_GlowingAgarilux) are not a content gap at all — their texPaths
(`Things/Plant/Bryolux`/`Agarilux`/`Glowstool`, confirmed against
`.../1841354677/1.6/Defs/ThingDefs_Plants/Plants_MycoticJungle.xml`) are vanilla
Core cave-plant textures the donor mod deliberately reuses rather than shipping its
own (Core has stocked this art since 1.4), so they live in `resources.assets`
exactly like the RUT_PaleTree/RUT_PaleMoss/RUT_Emberscythe rows already extracted.
Pulled `BryoluxA`, `AgariluxA` (also covers AB_GlowingAgarilux, same texPath) and
`GlowstoolA` via UnityPy under Windows `python.exe` — bare letter-suffix
Graphic_Random names, no prefix, first alphabetically. Their art-status chip is now
`vanilla`, not `donor`.

**Only 5 rows remain with no thumbnail**, all the same reason: RUT_FalseFruit,
RUT_AgelessCap, RUT_RegenerantVeil, RUT_EuphoricCrown, RUT_FurnaceCap are
shared-placeholder RUT_ rows whose new-art jobs FAILED tonight on quota; their
placeholder texPaths (CrimsonCap / GreyLadyGrown / VioletWimple / FruitingBodies)
already have a thumbnail on THEIR OWN row (RUT_CrimsonCap, RUT_GreyLady,
RUT_VioletWimple, RUT_FruitingBodies) — not duplicated onto every def that reuses
the same texPath, to avoid five identical thumbnails scattered across the sheet
with no visual distinction.

## Group A — Rot flora (40 rows)
32 wildPlants entries in `RUT_TheRot.xml` + 5 patch-added (RotPaleTree_WildSpawn.xml,
RotGuardianGroves_WildSpawn.xml x4) + 3 non-wild RotSporeKit-only plant ThingDefs
(RUT_DulcisPlant, RUT_FurnaceCap, RUT_PaleMoss). Art: 20 owned (real PNGs on disk,
confirmed by folder listing), 9 donor (AlphaBiomes) resolved from
`/mnt/c/.../workshop/content/294100/1841354677/Textures/Things/Plants/...` (first
variant alphabetically per folder), 4 vanilla-reuse rows resolved from the base
`resources.assets` (AB_Bryolux, AB_Glowstool, AB_Agarilux, AB_GlowingAgarilux —
vanilla Core cave-plant art the donor mod deliberately reuses), 2 more
vanilla-reuse rows (RUT_PaleTree, RUT_PaleMoss) extracted from the Royalty
AssetBundle / base resources.assets, and 5 shared-placeholder rows still without
their own thumbnail (art queued, failed on quota tonight). RUT_DulcisPlant is owned
art that also got a same-day regen pass (dulciscropitem_v1 etc, PASS, not yet
wired) — noted on its row.

## Group B — Rot fauna (10 rows)
**MEASURED 9 wildAnimals in the live `RUT_TheRot.xml`, not the 15 the build brief
named.** Checked every `Patches/*.xml` for a patch adding the other 6 (all BMT_
cavern kinds named in `rot_fauna_assignment_draft_20260918.md`'s table) — none
exists. That draft's 15-row table reads as a proposed roster, not a landed one;
reported as measured (9) with the discrepancy flagged on the page, not silently
matched to the briefed number. Plus RUT_Emberscythe (ships in RotSporeKit, Pyrelands
not Rot) = 10 rows. Mend column prints "mend ∝ bodySize" per tonight's ruling, not a
flat number.

**All 10 rows now have a thumbnail and a real bodySize.** The 6 AA_ (Alpha Animals)
rows resolved from `.../1541721856/Textures/Things/Pawn/Animal/<defName>/<defName>_south.png`
(bodySize from `1.6/Defs/ThingDefs_Races/Races_*.xml`: Agaripod 4.0, Agaripawn 1.4,
MycoidColossus 6.0, Swarmling 0.3, Wildpawn 1.4, Wildpod 4.0); 3 of the 6
(Agaripod, MycoidColossus, Wildpod) use the game Mods folder's `*ArtOverride`
instead of the base donor art, since that override takes priority in the live load
order. RUT_Emberscythe's art (a deliberate vanilla Megascarab recolor per its own
header comment) is now extracted from the base `resources.assets`
(`Megascarab_south`). The 3 RSW_ (SWBestiary) rows were already owned art.

## Group C — new art landed, other waves (5 rows)
93 artpipe manifests finished after 2026-09-18 00:00 PDT. Excluded 39 canon_*
creature-fidelity renders (already served by their own sheet,
`Transient/canon_regen_wave1_2026-09-18/`) and 45 Lantern Deeps texture-slot
manifests (already served by `Transient/deeps_art_review_2026-09-18.html`) — showing
either again would be a second, disagreeing review surface over the same renders.
4 dulcis* jobs excluded too: their target (RUT_DulcisPlant) is already a Group A row
in this same sheet. Remaining 5: twisting thornweed (unrelated biome, genuinely new)
+ 4 Lantern Deeps puffer stages that finished AFTER that sibling sheet was built (it
still shows them "pending"). All 5: facts PASS, validator skipped (no reference),
checked `wired` via literal md5 match against every PNG under `src/**/Textures/` —
**0 of 5 wired.**

## Rules invented
Listed in full in `CONFIG.invented` inside the sheet itself (required by the skill,
never omitted) — 11 items: the `<plant>`-block scoping rule for Group A, the
9-vs-15 fauna discrepancy, the AA_/AB_ donor-reachability correction, the 4
vanilla-reuse AlphaBiomes rows, the Group C exclusion scoping, the md5-based
`wired` definition, the uniform-1.0-drawSize finding, the visualSizeRange fallback
rule, the copied-not-imported scale-panel method + 240px cap, and the
adult-life-stage fauna drawSize source.

## Outputs
- `src/RimUtinni/RotSporeKit/build_review_sheet.py`
- `Transient/rot_flora_fauna_review_2026-09-18.html`
- `Transient/rot_flora_fauna_review_2026-09-18.decisions.json` (posture: blacklist, default keep — UNTOUCHED this pass, byte-identical before/after by md5)
- `Transient/rot_review_thumbs_2026-09-18/` (50 PNGs — 35 plant scale panels, 10 creature scale panels, 5 plain Group C thumbnails, all ≤240px)

## Correction: visualSizeRange, not drawSize, drives mature size (owner, latest pass)
Panels already used `visualSizeRange.max` where a def set one (first pass's
`mature_cells_flora`) — that part was right. The bug: the first pass only checked
each def's OWN tag + its RotSporeKit/AlphaBiomes custom abstract, and fell back to
raw drawSize=1.0 for 13 rows that set none there. FIXED: resolved through vanilla
RimWorld's own Plant bases too (MEASURED from `Data/Core/Defs/ThingDefs_Plants/
Plants_Bases.xml`: PlantBaseNonEdible 0.3~1.00, PlantBase inherits it, TreeBase
1.5~2.0) — every one of the 40 flora rows now resolves a real visualSizeRange, none
fall back to a guess. This changed one actual panel size (RUT_FlakespireFungus:
1.0→2.0 cells, confirmed 209×144px vs. its old smaller render) and re-labeled 12
more (AlphaBiomes donor rows + RUT_BleedingTooth) as "vanilla default, inherited"
rather than "not set". Headline row text now leads with mature size — "mature size
X cells (grows min→max)" — with drawSize demoted to a secondary, explicitly-labeled
constant. `check_sheet.py` exit 0 again; `decisions.json` still byte-identical.
