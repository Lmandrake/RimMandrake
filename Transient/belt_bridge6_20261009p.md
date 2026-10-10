# belt bridge6 — redeploy + full-list cold load + fail investigations, 2026-10-09 (helper #5)

## Status
- 21:32 started; reading predecessor log + deploy plan.

## (1) Kill, deploy, relaunch
- 21:36 Dry runs (game up): src/ has NO uncommitted edits except mine, so all drift is committed work. Drift: compose biomes (3 new, ~20 updated incl. Webwork DLL; 5 game-only files deleted in repo by c211092ce/adf9fc7be/23a59a864 -> prune), SWBestiary (3 Silooth PNG + patch + 2 port defs; 1 stale Ossik png), UtinniPatches (DLL, DyingCreep, 12 catch defs etc; 2 stale defs RUT_Hardwood/RUT_ScarlandsItems from material merges), Armoury (DLL + Zersium/AlloyForge), WreckedMachines (DLL + AlloyForge gates), AshkarrFlora, RustCathedralRoaches, ResearchRetag. FlowWorks only has game-only leftovers (old textures, northstar jsons): left alone. No ArtOverride mod shows drift.
- Plan: --apply --prune on Biomes(compose), SWBestiary, UtinniPatches, Armoury, WreckedMachines, AshkarrFlora, RustCathedralRoaches; --apply ResearchRetag. Delete game folder SiloothArtOverride + its ModsConfig entry (SILOOTH_ART_FOLD_1 deploy note).
- Added ProofEnrage hook to RM_CompParentalEnrage (records each calf's last CompTickRare tick + decision; static rareTicksSeen; fresh side-effect-free intruder/guardian eval). Built clean, rides the compose deploy.

### Decide strings (written before launch)
- Load up: `Bridge token:` present. Dead load: `Recovered from incompatible or corrupted mods` or `Caught exception while loading play data` present.
- DyingCreep fix (b4400b20a): 0 lines containing `RUT_DyingCreep` with Error/Config error/Graphic. Baseline last load: >=1 (Graphic_Single on folder art).
- Catch items fix: 0 lines containing `Meat_Small` in an error/texture line. Baseline: 12 defs read as Graphic_Single.
- Silooth fold: 0 `Could not load` lines naming `SWBestiary/Silooth`; an expected-present check is the live texPath read (S3).
- Pruned defs: no new `Could not resolve cross-reference` naming RUT_Hardwood / RUT_ScarlandsItems / RM_ScaldFloraProducts / RUT_SweetlineTree / RUT_CathedralRoachShell defs (would mean a live reference to a merged-away def).
- Enrage hook: `RM_CompParentalEnrage.ProofEnrage` answers via jawa/static_call (expected-present).
- 21:38 killed game (pid 9104), prev Player.log copied to scratch. Live list was the BAZAAR candidate (FULL.LATEST minus hobtook.tradeui + vanillatradingexpanded, same as bridge4/5) plus siloothartoverride: removed that one entry (612 active) and deleted Mods/SiloothArtOverride. Applied all deploys above, rc 0 each, no WinError.
- 21:39:48 launched via Steam on 612 (bazaar candidate list). Committed hook 7b3ba4fb7.
- 21:43 coordinator: more fixes landed (droid tiers 6f98539db, lasso ddb3795da, EK staging 425d0d520). Load was ~4 min in, so KILLED it rather than pay a second 15-min load later. Deployed Droidworks (DLL + BlankStandby think tree), UtinniPatches (MeleeAnimation_LassoRemoval.xml), ExplosiveKnockback (DLL), JawaRules (DLL with extended ProofHood: worker type, applies/kept, restoredCan, headgearVisibleRestored, baseGate, skip/rot fields). All VERIFIED in sync. Alloy forge / zersium already rode the first apply.
- 21:44:47 relaunched via Steam (612).
- Hood reading (offline, ilspycmd): Fortified prefix only fires for IHumanlikeMech (and returns true); LovinExpansion postfix only clears during JobDriver_Sex lovin; VEF transpiler only rewrites the Prefs.HatsOnlyOnMap portrait branch. None of the three can refuse a swimming Jawa, so patch order is NOT the mechanism. Remaining suspects: a base-gate refusal under the proof's hand-built PawnDrawParms, or the postfix not taking the re-ask branch. The extended proof discriminates.
- git note: local main carries two helper commits (bb89b03c7, 8040541c5) whose content landed on origin under other shas, so HEAD's ledger shard lacks origin lines and the push hook refuses HEAD. Landing via temp index on origin/main (scratch land6.sh), same as bridge5.

## (2) SHOKKWEAVE A1 rerun + DyingCreep / catch-item texture check
- pending

## (3) Fail investigations
### Parental enrage on the full list
- pending
### Jawa hood while swimming
- pending
### EK shield_counter
- pending

## Commits
- none yet
