# WEBWORK_TRACTION_LANCE_BUILD_1 progress 2026-10-06

## status
started

## findings (search before build)
- Capstan shipped (e263d1d13) with the pull INLINE in `RM_CapstanTurret : Building` (TheSump). Step 1 => lift into shared comp in CreatureBehaviors, repoint capstan.
- Shared code home: mandrake.rm.creaturebehaviors (Webwork already depends on it; TheSump will gain the dependency).
- Thrixweave = Core `Hyperweave` relabelled (RM_Thrixweave_Rename.xml). Tether stuffs: Cloth / DevilstrandCloth / Hyperweave.
- No `hidden` field on ResearchProjectDef in 1.6 (IsHidden is Anomaly codex only). Capstan precedent: visible-but-locked.
- CompAnalyzable.OnAnalyzed(Pawn) is virtual -> grant hook.
- SenseWeb "touch" = felt-mark hediff applied to a pawn on a registered cell.

## plan (decided)
- CreatureBehaviors: RM_CompTetherPull (+props, IRM_TetherPullHost), RM_Building_TractionLance (manned via vanilla CompMannable/JobDriver_ManTurret — works on a plain Building, RimSage-read), RM_CompAnalyzableGrantResearch (OnAnalyzed grant by defName, cross-mod safe), RM_CompLeaveSpecimenOnDeconstruct (gutter cut-out; trips SenseWeb via new RegisterTouch), lance settings.
- TheSump: capstan repointed to the comp (class name + save keys kept); draw-joint grants RM_Research_TractionLance by defName; About + csproj gain creaturebehaviors.
- Webwork: RM_TractionLance def (stuff Fabric, CompRefuelable = re-rig), RM_Research_TractionLance, RM_GutterJunction item, gutter alwaysDeconstructible + specimen comp.

## progress
- CB: settings, RM_CompTetherPull.cs, RM_Building_TractionLance.cs, RM_CompResearchSpecimens.cs, SenseWeb.RegisterTouch written; csproj updated. Next: capstan repoint.
- Capstan repointed (TheSump cs/xml/About/csproj/validation.py); draw-joint grants lance row.
- Webwork: RM_TractionLance.xml, RM_Research_TractionLance.xml, RM_GutterJunction.xml, gutter alwaysDeconstructible+specimen comp. Next: proof class, build.

## status: offline build DONE, not committed
- winbuild CreatureBehaviors + TheSump: 0 errors (DLL + .srchash refreshed).
- XML well-formed; validate_patch: 0 new errors (8 pre-existing vanilla-texture false positives in Webwork/TheSump).
- Webwork validation.py STATIC PASS (new _traction_lance_findings: one-pull search w/ sanity probe); TheSump STATIC PASS (needle updated for the lift).
- run_selftests: only bridgetools selftest_tool_metadata FAIL (pre-existing, unrelated) + 2 contention timeouts that passed on the prior run.
## left
- Live: RM_TractionLanceProof.ProofPull(stuff, raider|unmanned|wall|heavy|downed), ProofStuffTable(), both research doors, SenseWeb touch on cut, ollathrix-into-sun, per-toggle settings; then a live chain in Webwork/validation.py.
- Art: install RM_TractionLance_Base/_Top + RM_GutterJunction via art ledger (Base render dir is EMPTY); placeholders in use.
- Lance Mod Settings live in CreatureBehaviors settings (the class lives there), not Webwork's screen.
