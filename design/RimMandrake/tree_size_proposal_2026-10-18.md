# Tree size: how big our trees should be (proposal draft, 2026-10-18)

Item: `TREE_SIZE_ASK_GIANTS_WANTED`. **Status: DRAFT for the owner's sitting. Nothing is ruled here and no def was
edited.** Every number not quoted from him is MEASURED (cited) or PROPOSED (marked).

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

No ruling found that sets a tree **floor** ("very large" = N cells) or a per-biome scale. That is the gap.

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
draws 3.6. The other way: the five plants ruled trees today include `RM_GlowGlobe` (*"A low plant that grows a single
round glowing globe the size of a melon"*) and `RM_Maddrick` (*"standing shoulder-high"*), both at 3.0.

## Engine facts that limit every option (decompiled 1.6, RimSage `RimWorld/Plant.cs`)

1. **Drawn size = `drawSize.x × visualSizeRange.LerpThroughRange(growth)`**, one SQUARE quad (`Plant.Print`:
   `num3 = def.graphicData.drawSize.x * num2; ... new Vector2(num3, num3)`). `visualSizeRange` is the size knob;
   `drawSize.y` is ignored for plants; growth lerps min→max, so the min is what a young tree looks like.
2. **The ground-lift uses the visual size, not the drawn side** (`if (vector2.z - num2 / 2f < num7) vector2.z = num7 +
   num2 / 2f`). With `drawSize` 1 the picture's bottom sits on the root cell's south edge; with `drawSize` k > 1 the
   bottom sinks `(k−1)·visual/2` cells below the root. `RM_VaultRoot` (drawSize 2, visual 5.2) sinks 2.6 cells. Every
   option below keeps `drawSize` 1 and sizes with `visualSizeRange` only (PROPOSED), which also keeps the tree test
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
6. **The 3.0 line is a class boundary.** Anything that moves sizes moves which plants are trees (wood, bursts, Q2), so
   every option states what it does at 3.0.

## Options

### A. One multiplier for every tree

Every tree's `visualSizeRange` (min and max) × k, PROPOSED k = 2 (median 4.4 → 8.8; floor 3.0 → 6.0; top 10 → 20).
- **Buys:** one number, one ruling, relative order kept, trivial to apply and to undo; the 3.0 test is unaffected
  (only trees scale).
- **Costs:** keeps every existing mismatch (Thulvane stays among the smallest; GlowGlobe becomes a 6-cell "melon");
  the 26 trees already under 128 px/cell drop to 13–64 px/cell, so most need regenerated art; dense Greentide stands of
  16–20-cell quads overlap into a ceiling that hides pawns (vanilla has no canopy fade we know of: UNMEASURED); size
  stays visual only, so a 20-cell trunk is still walked through.

### B. Size tiers by role (PROPOSED recommendation)

Put each tree in a tier using the bins he already owns, with a TREE floor added, and assign rows at one sitting:
PROPOSED **canopy giant 8–12** (dominant/landmark trees: Veluthar, Thulvane, Sweetline, Corrisk, Hydenock, Kaddrath …),
**forest tree 5–8** (mid-storey and timber: Ghemmel, Vurmeloth, Nemmer, Mirrelbole …), **small tree 3–5** (understory,
arid and stunted forms: Shadespire, Thornwoods, Kneeling Ollim, Halfmade …). Plants ruled trees but described as low
(GlowGlobe, Maddrick, Gorbeleth) are a row he decides: stay 3.0, or the description changes.
- **Buys:** fixes the description mismatches; "very large" means the top two tiers, which is most of the forest trees;
  the bins become the contract the commission template already says they are; only the trees that move need art.
- **Costs:** a 44-row sitting (a review sheet at true scale beside a human); the tier assignment is judgment, not a
  formula; art regeneration for every tree that grows past its px budget.

### C. Per-biome scale

Each biome declares a tree scale (PROPOSED: Greentide and Fever Wood ×2, the dry and broken biomes ×1), applied by a
patch per biome mod.
- **Buys:** "the setting prefers" as a property of place: the jungles become giant forests while the arid trees stay
  lone and stunted, matching their prose (Shadespire *"three or four metres tall"*); small number of decisions (one per
  biome, ~14).
- **Costs:** a species in two biomes (Ollim, Vault Root, Thornwood, Fibre Stalk) needs one size; a def has one size,
  so the scale is really per species and only labelled per biome; still fixes no single mismatch inside a biome; same
  art and overlap costs as A where it applies.

### D. Tiers plus a body for the giants

Option B, and every tree in the top tier opts into HugeThings: trunk cells measured from the art block pathing and
building, give partial cover (0.4), select on click anywhere, and take hits (the ruled HugeThings behaviour).
- **Buys:** size you can feel: pawns route round a trunk, a giant is cover, a fall matters; fits his 2026-10-07 Option 1.
- **Costs:** a mask measurement per tree (`HugeThings/measure_huge_plant_masks.py`, one run each) and a new patch file
  per biome mod; dense Greentide stands of trunks can cut paths (HugeThings refuses a cell that would cut ground off, so
  some trunks stay partly open); per-plant footprint refresh on growth (`design/RimMandrake/huge_footprints_perf.md`
  measures the Rot's cost; the Greentide tree count is larger: UNMEASURED); interacts with the tree-burst and HugeThings
  footprint updates when a giant bursts or falls.

## Recommendation (PROPOSED)

**B now, D for the canopy-giant tier as a follow-up**, with `drawSize` 1 everywhere (engine fact 2), the 3.0 tree line
unchanged, and the sitting run as a true-scale review sheet of the 44 so he assigns tiers by looking. A is the fallback
if he wants one number today.

## Questions for the sitting

1. Which shape: A, B, C, or D? (card)
2. If B or D: the tier edges (PROPOSED 3–5 / 5–8 / 8–12), and whether the top may go past 12 toward the greatbole.
3. The low "trees" (GlowGlobe, Maddrick, Gorbeleth, KeeningCordax): grow them, or keep 3.0 and adjust the prose?
4. `RM_VaultRoot`'s `drawSize` 2: fold the 10.4 it draws today into `visualSizeRange` (drawSize 1, visual 10.4, base no longer sunk), or shrink it to
   the 5.2 the tree test already reads?
