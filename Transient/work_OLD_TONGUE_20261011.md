# WARSCAR_OLD_TONGUE_1 — 2026-10-11 FOUNDRY offline pass
Lease FOUNDRY.pid41271.51e4cb2d. Prior slice: e95f75751 (notes Transient/work_OLD_TONGUE_20261003.md).
## Already built (probe)
- e95f75751: 3 set panel defs (Hospice 2 / Projector 3 / Pool 3), RM_OldTongue_* research, Intellectual gate, chalk overlay, genstep, settings.
- Consumers now wired: RM_Hospice.cs (HospiceUnlocked: -0.04 failure, oddities), RM_ReactionPools.cs (PoolPhaseReaderUnlocked). ProjectorCalibrated has no reader yet (screen item's work, not this one).
## Remaining this pass
- Rest panels: research points + every Nth read reveals sealed crate (AncientSealedCrate, as loosened panels) or a buried kneeling chassis.
  Deviation from spec: one transcribe job for all panels (CompInscribedPanel restPanel flag), not CompStudiable+IThingStudied — keeps one gate, one job, one chalk path. Points via ResearchManager.AddProgress(GetProject()).
- Transcription item RM_OldTongueTranscription dropped per read; Utinni patch adds CompProperties_Antiquity + faction premium list (Helix, Deepwater).
- Premium: engine has no buy-side premium lever (RUT_HuttCartel_EggMarket.xml note) -> generic RM ext + Tradeable.GetPriceFor postfix (PlayerSells only).
- Research tooltip: postfix ResearchProjectDef.GetTip (Description is cached inside GetTip) listing unread panels + positions.
## Built this pass
- RM_InscribedPanel_Rest (restPanel flag on CompInscribedPanel, analysisID 740100004, never satisfied); genstep places oldTongueRestPanelsPerMap (2) after the set panels.
- Rest read: +oldTongueRestPoints (150, PROVISIONAL) to current project; refused with a reason when no project is chosen. RM_OldTongueGame counts reads game-wide; every oldTongueFindEvery (3) reveals AncientSealedCrate or a slagged/posed kneeling chassis within 8 cells (letter).
- RM_OldTongueTranscription item (MarketValue 40 PROVISIONAL) dropped per read (setting oldTongueTranscriptions).
- Utinni: src/RimUtinni/Antiquities/Patches/RUT_OldTongueTranscription.xml adds CompProperties_Antiquity + RM_FactionBuyPremium(Helix, Deepwater, x1.5 PROVISIONAL), guarded by def existence (warscar may ship composed).
- RM_OldTonguePatches_BuyPremium: Tradeable.GetPriceFor postfix, PlayerSells only (setting oldTongueTradePremium). Composes with Bazaar's postfix.
- RM_OldTonguePatches_ResearchTip: GetTip postfix lists unread panels (map + cell) for RM_OldTongue_* projects.
- Art queued (artpipe pending): RM_InscribedPanel_Rest, RM_OldTongueTranscription. Until they land those two textures are missing (loud magenta, not silent).
## Validation / selftests
- winbuild Scarlands: Build succeeded, 0 warnings. validation.py STATIC PASS. validate_patch static OK (1 intentional add-if-missing WARN).
## Owed live
- L2: set-read unlocks; Intellectual<8 refusal; chalk mark; rest points/find; transcription drop; tooltip line; Helix/Deepwater premium; Antiquity comp present on the transcription.
- Whether ResourceBase-derived item with patched-in <comps> merges cleanly (expected: yes).
