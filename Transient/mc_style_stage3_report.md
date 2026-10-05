# MessyConduit style stage 3 — hose reels and hoses per style

## Status
Built offline, committed and pushed (8cc77b906 source, bd6a04d3a DLL+.srchash from committed source). NOT deployed, NOT run live.
started Sun Oct  4 17:25:22 PDT 2026

## Notes

## What was built
- 4 ThingStyleDefs `RM_HoseReel_<Look>` (`Defs/Hose/RM_HoseReelStyles.xml`), graphicClass Graphic_HoseReel, texPath = each look's stored reel; CompProperties_Styleable on RM_HoseReel.
- Reel art: the existing stored/laid image SWAP, per look (Graphic_HoseReel finds `Reel_Deployed` beside each look's texPath). The design's two-layer coil overlay was NOT built (no coil art exists).
- StylePicker: one-line registration (`AerialStyles.StyledDefs` + `HoseStyles.StyledDefs`). That alone gives the reel the 4-item build-button menu, the designator getter (any game mode), Copy carry-over, the Frame guard and the legacy read (unstyled reel draws the default look, nothing written to the save). Blueprint -> frame -> building and pack-up/reinstall are the engine's own CompStyleable carry, as for poles.
- Hose materials per look (`HoseLookMats` in RM_MapComponent_Hoses.cs): strand flat/plump, binding, coupling, nozzle, end cap, open mouth from `Hose/Styles/<Look>/` (Scrapper = root files); shadow shared. Chosen per draw from the REEL's look (`HoseMaterials.For(reel)` -> `StylePicker.LookOfThing` -> `HoseStyles.HoseLook`), also for the pipe feed hose. A missing piece falls back to Scrapper's and is logged once + reported by the probe (`styleArtMissing`).
- Binding's aged-cloth brown tint now applies to Scrapper only (other looks' wraps are rubber/steel/alloy; still take the wet tint).
- HoseProbe census adds per reel: look, rawStyle, style, reelState, reelTex (path printing now), hoseTex (piece -> loaded path); plus defaultLook, styleArtMissing.

## Selftests
- winbuild MessyConduit: 0 errors. selftest_messyconduit.py 530/530 (10 new `style3` checks in `Source/SelfTest/StyleStage3Checks.cs`: naming, 28 distinct piece paths + one shared shadow, each look's own stored/laid pair, hose takes the reel look in 16/16 (reel, default) pairs with a can-fail that a global-setting rule is right in only 4/16, legacy -> default, unknown look -> Scrapper art, wrap tint Scrapper only).
- `validation_style_hose.py --offline` R0 PASS: 4 defs, texPaths, Graphic_HoseReel class, drawSize equal to the reel's, 36 art files on disk, comp present, no StyleCategoryDef lists them (1814 Defs xml swept).
- run_selftests.py 174/177: the same 3 pre-existing failures (northstar_matrix C2 live shots, StarWarsPatches semantics, UtinniPatches dump).

## Live check (written, NOT run)
After deploy (game closed) on the `messyconduit` tier, map WITH a free colonist:
    python.exe src\RimMandrake\MessyConduit\validation_style_hose.py --live --save MC_STYLE3_<date>
R1 pick -> designator style -> blueprint (Scrapper, Industrial build mode) / building (Modern, Futuristic god mode) + finishbuild;
R2 built reels: rawStyle per look, stored art path in the look's folder, hose set in that look;
R3 laid out: reelState deployed, reelTex = the look's Reel_Deployed, all 7 hose pieces from the look's folder, >= 3 reels not in the default look;
R4 save/load WHILE laid out: style names in the .rws, every reel's style/look/state/paths/geometryHash identical after reload;
R5 reeled in: stored art again, style kept; R6 Industrial reel packed up + reinstalled (same id, style kept) and laid again in Industrial;
R7 legacy reel by jawa/build_batch: no stored style, reads RM_HoseReel_<default>, draws + lays in the default look.

## Commits
- 8cc77b906 source, defs, selftest, validation_style_hose.py
- bd6a04d3a DLL + .srchash built from committed source

## Unproven
- Everything live (R1-R7), and the look on screen: each look's laid drum at drawSize 2.8 (art was generated as edits of each look's stored reel, never seen in game), the hose leaving the drum's mouth in each look (HoseReelRect.Mouth was measured on Scrapper's art only), the non-Scrapper bindings without the cloth tint, the menu showing reel icons.
- hoseTex is the material set the draw code selects, not a GPU read-back.
- Not done: review-map row 3 (four reels laid out + one reeled in) in human_review.py; fakegame/northstar_matrix know nothing of reel looks.
- Owed: `deploy_custom_mods.py --mod MessyConduit --apply` at the next shutdown.

### Reading notes (as I go)
- Reel today: RM_HoseReel 2x2, Graphic_HoseReel (stored texPath, swaps to sibling `Reel_Deployed` in the same folder when laid), drawSize 2.8. Hose start = HoseReelRect.Mouth (under drum).
- Art on disk: Hose/Styles/{Industrial,Modern,Futuristic}/{Reel_PumpHookup,Reel_Deployed,Strand_Flat,Strand_Plump,Binding,Coupling_Bare,Nozzle_Bare,EndCap_Bare,Mouth}.png; Scrapper = Hose/<Name>.png. Strand_Shadow shared.
- Plan: register RM_HoseReel in StylePicker (small additive edit: a second styled-def list), 4 ThingStyleDefs RM_HoseReel_<Look> with graphicClass Graphic_HoseReel (folder sibling swap gives laid art per look for free), CompProperties_Styleable on the reel, HoseMaterials per look keyed by the reel's look (StylePicker.LookOfThing -> legacy = default look).
- Done so far: Source/Hose/HoseStyles.cs (Verse-free path/look rules), Defs/Hose/RM_HoseReelStyles.xml (4 ThingStyleDefs, graphicClass Graphic_HoseReel), CompProperties_Styleable on RM_HoseReel, StylePicker registration (one foreach line: AerialStyles.StyledDefs + HoseStyles.StyledDefs). Menu, getter, copy, Frame guard and legacy read all key on that registration, so they cover the reel with no further edit.
- Reel art: the existing stored/laid SWAP per look (Graphic_HoseReel finds Reel_Deployed beside each look's texPath). Coil overlay NOT built (no coil art; the art report §4 ships stored/laid pairs).
- Code written: HoseMaterials per look (HoseLookMats, For(reel) via StylePicker.LookOfThing -> HoseStyles.HoseLook), DrawAll/DrawEnds/DrawFeed use the reel's set; aged-cloth wrap tint Scrapper only; HoseProbe census adds look/rawStyle/style/reelState/reelTex/hoseTex + defaultLook/styleArtMissing; StyleStage3Checks.cs. Building now.
- Built 0 errors; selftest_messyconduit 530/530 (10 new style3). validation_style_hose.py --offline R0 PASS (36 art files, 4 defs, 1814 Defs xml swept). Running run_selftests.py.
