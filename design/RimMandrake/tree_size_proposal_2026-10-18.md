# Tree size: how big our trees should be (2026-10-18)

Items: `TREE_SIZE_ASK_GIANTS_WANTED` (census, this proposal) and `TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS` (the tier
sitting). **Status: the shape and the tier edges are RULED (below); each tree's tier is placed at one review sitting.
No def was edited.** Every number not quoted from him is MEASURED (cited) or PROPOSED (marked).

## Ruling (owner, 2026-10-18)

Verbatim: *"The tiers should be Small Tree (3-5), Big Tree (5-8), Giant Tree (8-12), and Titanic Tree (12-30+).
Titanic trees should be seen only as the solid trunk ... Use option (1) like this."*

Option (1) is size tiers by role: each of our 44 trees is placed in one tier at one review sitting (a true-scale sheet
of the 44 beside a vanilla human). The ruled tiers, in cells of `visualSizeRange` at full growth:

| tier | cells |
|---|---|
| Small Tree | 3–5 |
| Big Tree | 5–8 |
| Giant Tree | 8–12 |
| Titanic Tree | 12–30+ |

## The ask

Owner, 2026-10-18, verbatim: *"they likely need a size ruling as well, most trees have not yet been made "very large"
as our setting prefers"*.

## What is already ruled about size (found in the repo, quoted)

- **Size bins.** `design/Jawa/worldbuilding/flora_commission_template.md:177-180`: *"size_bin: owner's bin (small <1 ·
  medium 1–2.2, person=1.5 · large 2.2–5 · TITAN 5+ — squares on screen at full growth"*; *"visual_size:
  visualSizeRange min~max in cells. THE BIN IS THE CONTRACT: max sits inside the bin; an owner note like "7 cells wide"
  IS this field."* The same file (:359) records that his sheet notes were *"dominated by "N cells wide" visual-size
  orders"*, and (:127) a *"vertical landmark | trees, towers, titans"* role at *"large–TITAN"*.
- **Footprint default.** Same file, :181-182: *"footprint: single-tile with oversized visual (TREE_GRAPHICS_OWNERSHIP
  precedent) unless the card argues otherwise"*.
- **Our own scale, our own art.** `infrastructure/state/items/TREE_GRAPHICS_OWNERSHIP_1.md`, owner verbatim: *"we should
  simply generate our own tree graphics at the scales we want and drop all the nonsense of multiple tree mods modifying
  our designs to who-knows-what scale."* The sweetline: *"Huge, ancient, powerful things (owner's ruling — never small
  trees)."* (quoting `design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4).
- **Huge plants get a body when chosen.** `design/RimMandrake/giant_footprint_design_2026-10-07.md` (HugeThings, owner
  Option 1, 2026-10-07): *"Solid trunk, open canopy — the stem blocks a small patch (~2×2 to 4×4 by species) so pawns
  path around it; clicking anywhere on the trunk selects it; you walk under the cap like a tree canopy."* Built for the
  Rot fungi only.
- **What a tree is.** `design/RimMandrake/tree_burst_design_2026-10-17.md` §2 (Q2 by card): `visualSizeRange` max ≥ 3.0,
  not a fungus, not `RM_Greatbole`.
- **Art resolution.** Owner ruling 2026-08-23 as recorded in the art memory: *128 px per cell of occupancy*; sprites
  default to 256².

## Where we stand (MEASURED 2026-10-18, bench clone)

44 tree defs of ours (rule above, ParentName resolved, patches applied). `visualSizeRange` max: min 3.0 · median 4.4 ·
max 10.0. **24 sit in the "large" bin (3.0–<5), 20 in TITAN (≥5).** All 44 are 1×1 plants; none has a HugeThings
footprint; only `RM_VaultRoot` sets `drawSize` (2). Greentide owns 20 of them. Vanilla for comparison (installed 1.6
defs): oak/maple/poplar/birch/palm/cecropia/drago/bamboo **2.0**, pine/gray pine/witchwood/rat palm/snagroot **3.0**,
`RM_Greatbole` (excluded) 12~16. Per tree, `visualSizeRange` max:

`RSW_Plant_HydenockTree_Wild` 10 · `RM_SweetlineTree` 10 · `RM_CorriskTree` 10 · `RM_Veluthar` 10 · `RM_Kaddrath` 9 ·
`RSW_Plant_JoganTree_Wild` 8 · `RM_LumbrelTree` 8 · `RM_Mourvel` 8 · `RM_Sarnstilt` 7 · `RM_Illurin` 7 · `RM_Brunnock` 6
· `RM_Ghemmel` 6 · `RM_Ollim` 5.5 · `RM_Dulloth` 5.2 · `RM_VaultRoot` 5.2 (drawn 10.4) · `RM_Nemmer` 5 · `RM_Vurmeloth` 5
· `RM_Zhorrel` 5 · `RM_Tumbel` 5 · `RM_GiantFibreStalk` 5 · `RM_Kollavane` 4.8 · `RM_Rockfinger` 4.8 · `RM_Mirrelbole` 4
· `RM_Quathis` 4 · `RM_Thalquith` 4 · `RM_Brakkel` 4 · `RM_Sarquin` 4 · `RM_Wollick` 4 · `RM_Ollamane` 3.6 ·
`RM_Wickwood` 3.6 · `RM_Thulvane` 3.5 · `RM_Thessamor` 3.4 · `RM_Eyebark` 3.4 · `RM_CrackedThornwood` 3 ·
`RM_Shadespire` 3 · `RM_HalfmadeTree` 3 · `RM_KneelOllim` 3 · `RM_TwistingThornwood` 3 · `RM_TreeMartyr` 3 ·
`RM_KeeningCordax` 3 · `RM_Gorbeleth` 3 · `RM_Phorrik` 3 · `RM_Maddrick` 3 · `RM_GlowGlobe` 3

Descriptions and sizes disagree in places: `RM_Thulvane` is written *"A colossal fused column of a tree ... rising past
sight"* (its cast proposal: *"the 16-cell fused tower"*) and draws 3.5; `RM_Ollamane` *"rising far above everything"*
draws 3.6. (The sheet sitting, 2026-10-18, ruled `RM_GlowGlobe`, `RM_Maddrick`, `RM_KeeningCordax`, `RM_Phorrik` and
seven others *"Not a tree, does not make wood"*: `tree_burst_design_2026-10-17.md` §2.)

## Engine facts that limit every tier (decompiled 1.6, RimSage `RimWorld/Plant.cs`)

1. **Drawn size = `drawSize.x × visualSizeRange.LerpThroughRange(growth)`**, one SQUARE quad (`Plant.Print`:
   `num3 = def.graphicData.drawSize.x * num2; ... new Vector2(num3, num3)`). `visualSizeRange` is the size knob;
   `drawSize.y` is ignored for plants; growth lerps min→max, so the min is what a young tree looks like.
2. **The ground-lift uses the visual size, not the drawn side** (`if (vector2.z - num2 / 2f < num7) vector2.z = num7 +
   num2 / 2f`). With `drawSize` 1 the picture's bottom sits on the root cell's south edge; with `drawSize` k > 1 the
   bottom sinks `(k−1)·visual/2` cells below the root. `RM_VaultRoot` (drawSize 2, visual 5.2) sinks 2.6 cells. Every
   tier keeps `drawSize` 1 and sizes with `visualSizeRange` only (PROPOSED), which also keeps the tree test
   (which reads `visualSizeRange` alone) honest.
3. **Size is visual only.** Footprint, selection, pathing and cover all come from the 1×1 cell: `TreeBase`
   (`Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml`) gives `PassThroughOnly`, `pathCost 42`, `fillPercent 0.25`,
   `blockWind`, `interferesWithRoof`. A 10-cell tree blocks exactly what an oak blocks. Giving size a body is what
   HugeThings does (invisible `RM_HugeTrunkBlocker` edifices on the cells the art touches, measured from the texture;
   the root cell is never blocked because an edifice there wipes the plant; `giant_footprint_design_2026-10-07.md`
   §Mechanism). A true multi-cell plant `size` is not used anywhere in vanilla or our code: UNMEASURED whether it works.
4. **Plants are printed into the static section mesh** (`Print(SectionLayer)`), not drawn per frame, so a bigger quad
   costs no CPU per tick; the cost is GPU overdraw where quads stack and texture memory. Overdraw cost on a dense
   10-cell Greentide: UNMEASURED.
5. **Art density falls as size rises.** Today 25 px per drawn cell (`RM_VaultRoot`, 256 px over 10.4) to 186
   (`RM_Ollim`); 11 of 44 under 64, 26 under 128. Doubling a tree's size halves its px per cell unless the art is
   regenerated larger, and regenerating at 512²+ costs about 4× atlas VRAM per texture (art memory, 2026-09-12).
6. **The 3.0 line is a class boundary.** Anything that moves sizes moves which plants are trees (wood, bursts, Q2);
   the Small Tree tier starts on that line.

## The sitting

The 44 rows are placed on the review sheet `Transient/biome_ffar/tree_tiers_sheet_2026-10-18.html` (decisions in its
`.decisions.json`, key `q.tier` per row). Its tier prefills (`qPrefill`) are agent guesses from each description, never
his rulings.

## Enacted (2026-10-18)

The sheet's tiers were enacted: each row's `visualSizeRange` max placed inside his tier (drawSize 1 everywhere;
`RM_VaultRoot`'s drawSize 2 removed, it is a Small Tree). GlowGlobe, Maddrick and KeeningCordax were ruled not trees;
Gorbeleth is a Small Tree. Item: `TREE_TIERS_JUDGE_FORTY_FOUR_TRUNKS`.
