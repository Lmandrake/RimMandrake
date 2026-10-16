# Liquid containers in the four styles

status: **DESIGN + PILOT ART, nothing installed or wired.** Item `LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS` (BENCH, 2026-10-16).

Owner, 2026-10-16: *"The art for buckets, barrels, etc. is really boring. They too should have the four styles of art. And
the bottles look like mana potions in fantasy games. This is a scifi future world. Junker bottles should be oddly shapes.
Industrial should look like generic water bottles. Modern should look like soda bottles (multicolored). Futuristic should
look like hexagonal canteens."*

## What was measured

- **The four styles** are GSS/FlowWorks' **Scrapper** (his "Junker"), **Industrial**, **Modern**, **Futuristic**
  (`messyconduit_style_per_build_design.md`). Buildings carry one as a vanilla `ThingStyleDef` per building × style
  (e.g. `FlowWorks/Defs/LiquidTypes/ThingDefs/RM_LiquidTankStyles.xml`), listed by no `StyleCategoryDef`, picked on the
  build button by FlowWorks' shared picker (`Source/Machinery/PipeLook.cs`). The engine draws `StyleDef.graphicData`
  by itself and saves the style per thing.
- **Containers are items, so there is no build button.** They are crafted by bill (`RM_ContainerRecipes.xml`, one recipe
  per material per bench, `FLOWWORKS_CONTAINER_MATERIALS_1`).
- **Today's art:** one greyscale 256 px `Graphic_Single` per size (`Textures/Things/Item/Resource/FlowWorks/RM_{Bottle,
  Bucket,Barrel}.png`), shared by every liquid. The WHOLE sprite is multiplied by one colour: the stuff colour when
  empty, the `LiquidDef` colour when filled (`RM_CompContainerMaterial.ForceColor`, colours from the generator's
  `LIQUID_CONTAINER_COLORS`). A round corked flask washed entirely in one liquid colour is the mana potion.
- `RM_ColoredWaterBottles_Patch.xml` (DBH present only) makes `RM_WaterBottle_*` on DBH's own bottle texture, tinted
  whole by `graphicData.color`: the same wash, a second source of potions.
- Filled defs are generated (`Tools/generate_liquid_suite.py` → `RM_LiquidBottles.xml`); empty/dirty and the three
  `RM_*ItemBase`s are hand-authored (`RM_LiquidBottles_Base.xml`). Chemfuel's bottle adopts vanilla `Chemfuel`.
- No earlier container art in the four styles: `artpipe_state.py find` holds only the greyscale stuffable regens, and
  no sheet's `.decisions.json` rules on containers beyond them.

## Engine facts the design rests on (RimSage, RimWorld 1.6)

- `Toils_Recipe.FinishRecipeAndStartStoringProduct`: with Ideology active (every DLC is assumed) and a one-product
  recipe, the product gets `bill.style` whenever `bill.globalStyle` is false, through `GenRecipe.MakeRecipeProducts`.
  `Bill` saves `style` / `globalStyle`. **So a bill already carries a style to its product; only the picker is missing.**
- `Dialog_BillConfig` shows its style button **only in classic ideoligion mode and only for ideoligion style
  categories**: the same catch the building picker hit. Ours never appears there.
- `Thing.DrawColorTwo` is virtual; `CutoutComplex` tints the mask's red region with the draw colour and green with colour
  two, and leaves black regions as painted.

## The design

| piece | what | size of the change |
|---|---|---|
| Style carrier | 12 `ThingStyleDef`s, `RM_{Bottle,Bucket,Barrel}_{Scrapper,Industrial,Modern,Futuristic}`, each `Graphic_Single` + `CutoutComplex`, same drawSize as today. `CompProperties_Styleable` on the three `RM_*ItemBase`s | XML only; ItemBases are hand-authored, the generator is untouched |
| Picker | one Harmony postfix on `Dialog_BillConfig.DoWindowContents`: for a recipe whose product has `RM_BottledLiquidExtension`, draw a "Style" button (the four, with icons, same labels as the building picker) that sets `bill.style` and `globalStyle = false` | small C#; vanilla then does the rest |
| Default | a bill with no pick, and anything not crafted (traders, loot, starting items) gets a style from the maker's tech: neolithic/medieval = Scrapper, industrial = Industrial, spacer = Modern, ultra = Futuristic | one helper, called where the item spawns unstyled |
| Chain | `RM_LiquidBottleUtility.MakeContainer` already carries `Stuff` across every def swap (fill, drink, wash, pour, revert); it also copies `StyleDef` | one line in the one helper |
| Liquid colour | mask red = the liquid (bottle body, bucket surface, barrel sight-glass). `ForceColor` stays as built: filled = liquid colour on that region only; the rest of the sprite keeps its painted colours. Empty: a pale clear-glass grey; dirty: a grime brown | `ForceColor` returns two new constants; art does the rest |
| Material | **open question for the owner.** Ruling 4 (2026-10-06) has the empty container show its material. With painted styles the body is no longer a blank to tint. Proposal: the material tints a mask-green TRIM region only (cap, handle, hoops) via `DrawColorTwo` (needs a small `ThingWithComps` subclass on the ItemBases). The pilot masks carry no green yet | decide before the full set |
| DBH coloured waters | repoint `RM_WaterBottle_*` at the Industrial bottle sprite + mask, `CutoutComplex`, keeping their colours | XML in that patch |

**Stacking:** confirm in game that two bottles of different style do not merge into one stack (vanilla `CanStackWith`
on style); if they merge, a comp `AllowStackWith` comparing `StyleDef` closes it.

## Asset count

Liquids never multiply art: **3 sizes × 4 styles = 12 sprites + 12 masks = 24 PNGs** for the whole set, covering every
bottled liquid (ten today, each in three sizes) plus empty and dirty. Per-liquid painted art would be 144 sprites for
today's liquids alone and grow with every new one.

## Pilot

All 12 sprites are drawn (`src/RimMandrake/FlowWorks/art_source/LiquidContainers/v1/`): three generations, one row of
four styles per call, the liquid painted pure magenta so `make_pilot.py` can turn it into the mask by hue and repaint it
neutral grey. 256 px, real alpha, 0.00% fringe, clean corners (validator `--describe`). Tint previews: `tint_preview.py`.
Review sheet: `Transient/biome_ffar/liquid_containers_four_styles_sheet_2026-10-16.html`. Each row is one sprite: the
installable base, then fresh water, toxic water and tar, then the current art for comparison.

Measured generation time: 76 s + 58 s + 62 s = **196 s for all 12** (one codex call per container size). Cutting,
masking and tinting take about a second.

Camera note for review: the bottles are drawn nearly face-on (the open top barely shows). That suits a small item, but
buckets and barrels show their tops at the building camera, so the set is slightly mixed.
