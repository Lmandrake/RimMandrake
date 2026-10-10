# BELT zersium 2026-10-09l

Item: ZERSIUM_FORGE_BIOME_1

## Steps
- [ ] claim
- [ ] read Forge source/roster
- [ ] def + deposit
- [ ] art check
- [ ] settings toggle
- [ ] script
- [ ] publish + implemented
- [x] claim (token FOUNDRY.pid36534.f37392bb)
- [x] read: TheForge is RM tier (Q11: no SW names) -> zersium def+deposit go RSW tier, Forge placement via Utinni-style biome-gated GenStep (RM_ScattererValidator_Biome precedent, RUT_FoundryTowerScatter)
- [x] art: artpipe find zersium = 0 hits (probe mindstone found); no rulings
- [ ] writing defs (Armoury RSW_Zersium + RSW_MineableZersium), GenStep in UtinniPatches
- [x] defs: Armoury/Defs/ThingDefs/RSW_Zersium.xml; UtinniPatches GenStep C# + GenStepDef + Base_Player register + setting zersiumForgeEnabled
- [x] winbuild UtinniPatches 0W/0E
- [x] validation.py chain zersium_forge (static PASS offline, break case caught); toggle in suite.toggles
- [x] art job queued: _artpipe/pending/RSW_Zersium.json (install_to Armoury/Textures/Things/Item/Resource/RSW_Zersium.png); placeholder tinted Steel stack until install
- [x] registry CSV row zersium (RM_TheForge/RUT_TheForge 660 EPM provisional); walk line added
- [x] selftests: 8 fails, none mine (utinnipatches_dump clears on commit via changed-after-dump; items_glob = PLASTEEL_DURASTEEL_MERGE_1 drift, not mine)
- [ ] publish
- [x] PUBLISHED 8f69533888d2; rimflow implemented run
