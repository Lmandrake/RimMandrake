# Rot-wave art jobs — 2026-09-18

Scope: `src/RimUtinni/RotSporeKit/Defs/{ThingDefs_Plants,ThingDefs_Items,ThingDefs_Buildings,GeneDefs}/RUT_RotSporeKit_*` + `RUT_PaleTree.xml` + `RUT_RotSporeKit_Furnaceblood.xml`. Jobs written directly to `infrastructure/artpipe/active/` per instruction (not `pending/` — normally `fill_queue.py`'s lane; noted here since it deviates from the README's stated writer convention). No bridge/game commands run, no images generated, no commits made.

## Inventory

Files read and their graphicClass / texPath:

| Def | File | graphicClass | texPath |
|---|---|---|---|
| RUT_AgelessCap | ThingDefs_Plants/RUT_RotSporeKit_GuardianGroves.xml | Graphic_Random | RotSporeKit/Things/Plant/CrimsonCap |
| RUT_RegenerantVeil | same | Graphic_Random | RotSporeKit/Things/Plant/GreyLady/GreyLadyGrown |
| RUT_EuphoricCrown | same | Graphic_Random | RotSporeKit/Things/Plant/VioletWimple |
| RUT_FalseFruit | same | Graphic_Random | RotSporeKit/Things/Plant/FruitingBodies |
| RUT_LiveIngredient_AgelessCap | ThingDefs_Items/RUT_RotSporeKit_GuardianGroves_Ingredients.xml | Graphic_StackCount | .../MushroomLog/MushroomlLog_a |
| RUT_LiveIngredient_RegenerantVeil | same | Graphic_StackCount | .../GlowGoo/GlowGoo_A |
| RUT_LiveIngredient_EuphoricCrown | same | Graphic_StackCount | .../ThrumbungusShroom/ThrumbungusShroom |
| RUT_BrewingVessel | ThingDefs_Buildings/RUT_RotSporeKit_BrewingVessel.xml | Graphic_Multi (rotatable) | Things/Building/Production/FermentingBarrel (vanilla, tinted) |
| RUT_Tea_AgeReversal | ThingDefs_Items/RUT_RotSporeKit_LivePreparations.xml | Graphic_StackCount | .../GlowGoo/GlowGoo_A |
| RUT_Tea_Bioregeneration | same | Graphic_StackCount | .../GlowGoo/GlowGoo_B |
| RUT_Tea_Pleasure | same | Graphic_StackCount | .../Drug/Ambrosyx |
| RUT_Symbiont_Quickflesh | same | Graphic_StackCount | .../MushroomLog/MushroomLog_b |
| RUT_Symbiont_Nightwake | same | Graphic_StackCount | .../GlowGoo/GlowGoo_A |
| RUT_Symbiont_Sheenblood | same | Graphic_StackCount | .../GlowGoo/GlowGoo_B |
| RUT_Symbiont_Mycoid | same | Graphic_StackCount | .../MushroomLog/MushroomlLog_a |
| RUT_LivePrep_ToxicInjection | same | Graphic_StackCount | .../GlowGoo/GlowGoo_A |
| RUT_FurnaceCap | ThingDefs_Plants/RUT_RotSporeKit_FurnaceCap.xml | Graphic_Random | RotSporeKit/Things/Plant/CrimsonCap |
| RUT_LivingFurnaceCap | ThingDefs_Items/RUT_RotSporeKit_FurnaceCap.xml | Graphic_StackCount | .../Crops/MortalMorel (actually HealingMorel_*.png) |
| RUT_GrownFurnace | ThingDefs_Buildings/RUT_RotSporeKit_GrownFurnace.xml | Graphic_Random, rotatable=false | RotSporeKit/Things/Building/GlowGooTorch |
| RUT_PaleTree | ThingDefs_Plants/RUT_PaleTree.xml | Graphic_Random | vanilla Things/Plant/TreeAnima |
| RUT_PaleMoss | same | Graphic_Random | vanilla Things/Plant/Grass_Anima |
| RUT_Gene_Furnaceblood | GeneDefs/RUT_RotSporeKit_Furnaceblood.xml | (gene iconPath) | vanilla UI/Icons/Genes/Gene_Furskin |

## Proven missing / placeholder

Every one of the 22 defs above carries an explicit **"ART OWED" / "placeholder"** comment in its own source file header (quoted directly during review — not inferred). Independently cross-checked by grepping the whole `src/` tree for each literal texPath: every single one is **also used by at least one unrelated def elsewhere** (confirmed reuse, not bespoke art):

- `CrimsonCap` — shared by RUT_AgelessCap, RUT_FurnaceCap, AND an unrelated species in `RUT_RotSporeKit_Flora.xml`.
- `GreyLady/GreyLadyGrown`, `VioletWimple`, `FruitingBodies` — each also used by `RUT_RotSporeKit_Flora.xml`.
- `MushroomlLog_a` — shared by RUT_LiveIngredient_AgelessCap AND RUT_Symbiont_Mycoid (two unrelated items).
- `GlowGoo_A` — shared by 4 unrelated defs (RUT_LiveIngredient_RegenerantVeil, RUT_Tea_AgeReversal, RUT_Symbiont_Nightwake, RUT_LivePrep_ToxicInjection).
- `GlowGoo_B` — shared by RUT_Tea_Bioregeneration and RUT_Symbiont_Sheenblood.
- `ThrumbungusShroom` — shared with an unrelated weapon/creature family (`RUT_RotSporeKit_ThrumbungusShroom.xml`, `RSW_BiomesTeamPort`).
- `MushroomLog_b` — used only by RUT_Symbiont_Quickflesh here but is vanilla-adjacent donor stock art, per header.
- `Drug/Ambrosyx` — shared with `RUT_RotSporeKit_Drugs.xml` (a different drug def).
- `Crops/MortalMorel` folder — shared with `RUT_RotSporeKit_Flora.xml`; actual files are `HealingMorel_A/B/C.png` (folder/texPath naming doesn't match file names — pre-existing oddity, not something I fixed).
- `Building/GlowGooTorch` — shared with `RUT_RotSporeKit_Buildings.xml` (a torch/lamp, not a furnace).
- `Things/Plant/TreeAnima`, `Plant/Grass_Anima` — vanilla Royalty DLC textures, used verbatim (not even a RotSporeKit asset).
- `UI/Icons/Genes/Gene_Furskin` — shared with `RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml`'s own Furskin gene.

No ambiguous/borderline case needed an MD5 byte-check — every one had either an explicit header admission, a confirmed cross-def texPath collision, or both.

## Jobs filed (22, all in `infrastructure/artpipe/active/`, priority 60, channel codex, background transparent, no `reference` field — all new art)

1. `rut_agelesscap_v1` — ROT_GUARDIAN_GROVES_1 — plant, 256x256
2. `rut_regenerantveil_v1` — ROT_GUARDIAN_GROVES_1 — plant, 256x256
3. `rut_euphoriccrown_v1` — ROT_GUARDIAN_GROVES_1 — plant, 256x256
4. `rut_falsefruit_v1` — ROT_GUARDIAN_GROVES_1 — plant, 256x256 (drawsize 0.5, small mimic lure)
5. `rut_liveingredient_agelesscap_v1` — ROT_GUARDIAN_GROVES_1 — item, 256x256
6. `rut_liveingredient_regenerantveil_v1` — ROT_GUARDIAN_GROVES_1 — item, 256x256
7. `rut_liveingredient_euphoriccrown_v1` — ROT_GUARDIAN_GROVES_1 — item, 256x256
8. `rut_brewingvessel_v1_south` — ROT_LIVE_PREPARATIONS_1 — building, 256x256, south facing only (see Skipped)
9. `rut_tea_agereversal_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
10. `rut_tea_bioregeneration_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
11. `rut_tea_pleasure_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
12. `rut_symbiont_quickflesh_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
13. `rut_symbiont_nightwake_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
14. `rut_symbiont_sheenblood_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
15. `rut_symbiont_mycoid_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
16. `rut_liveprep_toxicinjection_v1` — ROT_LIVE_PREPARATIONS_1 — item, 256x256
17. `rut_furnacecap_plant_v1` — ROT_WARM_MAT_1 — plant, 256x256
18. `rut_livingfurnacecap_v1` — ROT_WARM_MAT_1 — item, 256x256 (drawsize 0.85)
19. `rut_grownfurnace_v1` — ROT_WARM_MAT_1 — building, 256x256, single view (Graphic_Random, rotatable=false — no facings needed)
20. `rut_gene_furnaceblood_icon_v1` — ROT_WARM_MAT_1 — gene UI icon, 128x128 (AMBIGUOUS, see Skipped)
21. `rut_paletree_v1` — ROT_PALE_TREE_1 — plant, 512x512 (drawsize 2.5, matches visualSizeRange ceiling + treeCategory Super, "err generous")
22. `rut_palemoss_v1` — ROT_PALE_TREE_1 — plant, 256x256 (drawsize 0.4, small subplant)

Each prompt is painterly-vanilla per ART_PAINTERLY_RESTORATION_1 (Ronto exemplar), heavy black outline required, no "reference" field (true new art, not a reskin). `style_notes` on every job names the specific donor texPath being replaced and its collision partner, for traceability.

## Skipped + why

- **Nothing skipped as "already has real bespoke art"** — all 22 target defs were confirmed placeholder/reused. No SKIP entries of that kind.
- **`rut_brewingvessel_v1_south`** — filed ONLY the south-facing view, not the full south/east/north Graphic_Multi set a rotatable building normally wants. The README's Ronto precedent and `fill_queue.py`'s facings mechanism support a 3-facing job, but there's no README guidance specifically for building multi-facing jobs, so I followed the task's own explicit fallback instruction ("if unclear, file the single/_south canonical view and note it"). **East and north views are still owed** — a follow-up filing should add `rut_brewingvessel_v1_east` / `_north` against the same reference once the south view exists to seed a matched set (or as three fresh new-art jobs if the daemon should treat all three independently — owner's call).
- **`rut_gene_furnaceblood_icon_v1`** — filed but flagged AMBIGUOUS: every other job here follows the painterly full-render creature/plant/building lawset, but a RimWorld gene is a small flat UI icon (a different visual grammar entirely), and this artpipe daemon has no prior gene-icon job in `done/` to anchor sizing/style conventions against. I filed it at 128px in a flat-icon style prompt (explicitly NOT painterly) rather than skip it outright, since the task named it in scope, but the owner should sanity-check whether this belongs in this pipeline at all versus a manual/different-tool icon pass.
- **`Crops/MortalMorel` texPath oddity** — noted, not fixed: the def's texPath folder is named `MortalMorel` but the actual files on disk are `HealingMorel_A/B/C.png`. Out of scope (pre-existing naming quirk, not an art-generation gap) — flagged for whoever next touches that file.

## Verification performed
- All 22 JSON files parse as valid JSON, ids unique, no id collisions against `pending/`, `done/`, or `failed/` (checked by script).
- No bridge/game commands run. No git commit/push. No images generated.
