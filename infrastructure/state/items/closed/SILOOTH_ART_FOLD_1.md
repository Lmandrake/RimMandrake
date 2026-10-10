## spec
Owner, 2026-10-09 (typed): the Silooth art override `mandrake.rsw.siloothartoverride` is a single creature's
art swap and "should just be added to our mods, not as its own mod". The Silooth's live home is SWBestiary
(`Patches/Silooth/Silooth_Warbeast.xml` already resizes it and swaps its acid spit), so the three adult
facings now live at `src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Silooth/Silooth_{south,east,north}.png`
and the same patch points the donor PawnKindDef's lifeStages li[2] (juvenile stage) and li[3] (adult)
`bodyGraphicData/texPath` at `RimStarWars/SWBestiary/Silooth/Silooth`. Those are the two stages the old
same-path override already reached (both draw the donor's `swanimals/Silooth/Silooth`); the larva and the
dessicated corpses stay on donor art, as before. The standalone `src/RimStarWars/SiloothArtOverride` is deleted.

## deploy note (next game-down; not applied)
1. `deploy_custom_mods.py --mod SWBestiary` plan, then `--apply` (adds the three textures + the patch edit).
2. Delete the game-folder copy `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SiloothArtOverride`.
3. If `mandrake.rsw.siloothartoverride` is in the live `ModsConfig.xml` activeMods, remove it (RimWorld warns
   on a missing active mod; harmless, but clean it). No modlist snapshot in the repo names it.

## criteria
- S1 L0: no file in the repo defines or names `mandrake.rsw.siloothartoverride` outside ledgers/Transient
- S2 L0: SWBestiary carries the three facings and the patch redirects li[2] and li[3] texPath to them
- S3 L1: after deploy, an adult and a juvenile-stage silooth draw the v6 redraw (game-folder copy removed)
