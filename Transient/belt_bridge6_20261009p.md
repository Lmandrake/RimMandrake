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

- 21:50 load in progress; scripts staged: belt_bridge6_load.py (rehearsal COPY), _enrage.py, _hood.py, _misc.py (shokk/lasso/droid). Landed 6976275d9.
- Additional decide strings (coordinator's fixes): lasso -> get_defs RecipeDef/Make_AM_Lasso{Cloth,Hyperweave,Devilstrand} all notFound (control Make_Apparel_Duster found); droids -> Mindless/Blank needs == power only, Blank ProofJob=Wait and position unchanged over 600 ticks; EK -> shield_counter + body_override PASS in rewritten form.

## (2) SHOKKWEAVE A1 rerun + DyingCreep / catch-item texture check
- 22:03:08 bridge up (612). Log decide strings (Transient/belt_bridge6_logcheck_20261009p.txt): 0 lines RUT_DyingCreep error, 0 Meat_Small error, 0 Silooth/siloothartoverride, 0 refs to pruned defs, 0 Lasso/Droidworks/EK/CreatureBehaviors/Zersium/AlloyForge errors, 0 crossref; 29 Config errors (research-coords noise, RM_FE_Ash burnedDef flammable, menushell defName). All PASS.
- Loaded Saves/BAZAAR_VTE_UNWIND_REHEARSAL_20261009 (copy; never saved), closed 2 VEF Dialog_NewFactionSpawning.
- SHOKKWEAVE_SOLE_SOURCE_1 A1 PASS x2: `HARVEST designatable True (after 0 ticks) | workgiver True | yield 3 | weaveNear 0->3 | spawned 1` (static_call args must use `;` - the bridge splits `|` into params). Item -> done.
- LASSO_CHERRYPICKER_REMOVAL_1 A3 PASS: Make_AM_LassoCloth/Hyperweave/Devilstrand notFound, control Make_Apparel_Duster found. -> validated (A2 setting still owed).

## (3) Fail investigations
### Parental enrage on the full list — NOT a defect; bridge5 FAIL was a polling artifact
- ProofEnrage: CompTickRare runs on every calf (rareTicksSeen climbs, lastRare advances), the triggering calf records lastTrigger at its first rare tick, then cooldown -> no_intruder.
- The rage is SHORT: with exact `rimworld/step_game_ticks 8` polling, the wild adult held RM_ParentalEnrage ~56 ticks (135798-135846), mauled the colonist (2 Cut + BloodLoss), then disengaged (intruder downed / out of the 10-cell radius - by design, RM_MentalState_ParentalEnrage.ShouldDisengage). bridge5 polled with scenelib.run(125), which overshoots ~100+ ticks per call on the full list, so it never sampled the state.
- A1 PASS: S1 wild calves -> exactly the wild adult enrages, tame adult never; S2 tame calves + own colonist -> no adult enrages, colonist untouched. Item -> done.
- Lesson: never poll a short-lived mental state with scenelib.run on the full list; use step_game_ticks.
### Jawa hood while swimming — ROOT CAUSE FOUND: ReGrowthCore, not patch order on CanDrawNow
- Extended ProofHood on a live swimmer: worker=PawnRenderNodeWorker_Apparel_Head, applies=True, kept=True, baseGate=True, but restoredCan=False and headgearVisibleRestored=False even with Clothes|Headgear restored.
- harmony_patches on HeadgearVisible: 5 postfixes (VFEPirates, StandaloneHotSpring, ReGrowthCore, RomanceOnTheRim, VanillaMemesExpanded) + VEF transpiler. Decompiled: ReGrowthCore's postfix sets false when `pawn.IsBathingNow()`, and its IsBathingNow returns `pawn.jobs.curJob.swimming` for any non-bathe job -> every swimming pawn's headgear hidden. (HotSpring's twin only fires in its own bath toil; VFEPirates only forces true for warcaskets; VME only for its Naked hediff.)
- FIX built + landed 04916d360: Patch_HeadgearVisible_KeptHoodReask, Priority.Last postfix on HeadgearVisible; only while our kept-hood re-ask runs (reentry flag) it replaces the answer with vanilla's own rule. NOT DEPLOYED: JawaRules DLL is locked by the running game -> needs next game-down deploy + ProofHood reread (expect canDraw=True on a swimmer).
### EK shield_counter / body_override — PASS in rewritten form (425d0d520 staging fix)
- Scratch AridShrubland tile 9000 (mapId 4). knockback_runner 6 scenes VERDICT PASS: body_override big thrown 6 cells, control 0 launches (controlTooBig); shield_counter 0 cells, counter skip energy 1.067->0.737 (belt now charged); immunity_window, lookup_projectile, lookup_zero_wins, impact_factor PASS. EK.config + EK.guards verified pass (Transient/explosive_knockback/run_20261009T220936.jsonl).

## Coordinator's other fixes
- DROIDWORKS_FORMAT_TIERS_1 A1 PASS (Mindless+Blank needs == [RSW_DW_Power]; Sapient control full set), A3 PASS (Blank: ProofJob Wait, "Standing.", position unchanged 600 ticks; Programmable control GotoWander). -> done. Side note: the GNK droids inspect as "Aphrodor female/male" race label - cosmetic, not filed.
- SILOOTH_ART_FOLD_1 S3 PASS: li[2]/li[3] texPath RimStarWars/SWBestiary/Silooth/Silooth live; not in texture_audit dead list. -> done.

## texture_audit (whole game, 27808 paths): 28 dead
- FIXED offline + XML deployed (takes effect next load): RM_ToxinSealant, RM_RoyalRind, RM_GreatboleGrubSpines, RSW_TelluroxShell used texPath Things/Item/Resource/Leather/Leather_Plain; vanilla Leather_Plain is Things/Item/Resource/Leather (Graphic_StackCount folder). Same class as the Meat_Small fix.
- NOT ours to fix here (missing art): RM_Braskeen, RM_Ismerrow (plants, no texture in src), RUT_Fuzz, RSW_Zakkro dessicated, 14 KOTOR_SmallCrystal (+GravTide roofed twins) Buildings/Crystal_Formations/small_dyeable, donor Yobshrimp/AA_Swarmling. List: Transient/belt_bridge6_texaudit_20261009p.txt.
- NOTE: SWBestiary + compose-biomes re-apply also carried ART_OVERRIDE_FOLD_ALL_1's committed ArtFold patches into the game. The 59 *ArtOverride mods are still in Mods/ and ModsConfig (untouched as instructed), so next load runs both until that item's game-down cleanup.

## Commits
- none yet
