# FOUNDRY_REBOOT_HANDOFF_202609181353 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609180351`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

FlowWorks' generated compat patch wrote lowercase `viscosityClass` values (`water` vs the
enum's `Water`) onto 9 core vanilla/Odyssey water TerrainDefs — `Enum.Parse` is
case-sensitive, so `DirectXmlToObject` silently discarded ALL NINE, every load, since the
patch first shipped. Every land-biome river/lake/coast has been generating with **zero
water terrain** all session (river/lake mutator workers still ran and painted a null
terrain, which is also what tripped the log's message-cap and made an unrelated crash
look uninvestigable). **FlowWorks has very likely never had working liquids in-game since
it shipped.** Fix is committed (`cd8ab494e`) — 37 lowercase values corrected across 14
files, the generator (`generate_liquid_suite.py`) now raises on an unknown enum member so
this can't recur silently — but it needs a COLD RELOAD to take effect, which this session
deliberately did not force (see "What the owner should see"). This is the fact that would
have cost the next seat the most time to rediscover: any water-mechanism test failure
until the next restart is THIS, not a new bug.

## What the owner should see

- **The FlowWorks water-terrain fix above needs your restart to actually take effect.**
  Nothing else is blocking it — it's committed, validated, just unverified live. First
  thing to check after any restart: spawn on a river/lake tile, confirm real water
  terrain generates (`QUICKTEST_RIVER_WATER_MISSING_1` has the exact repro/verify steps).
- **A second, independent finding this session**: `run_expectations.py --live` had been
  silently reading zero rows on every prior live run (wrong JSON key, `"rows"` vs the
  real `"defs"`) — fixed, but means any PRIOR session's "L1 live-verified" claim made
  through this specific tool should be treated as unverified until re-run.
- **Droidworks droids render a default human face** despite a blank head-type def — root
  cause found and a fix committed (`8d4f6fe39`, `useFactionXenotypes=false`), but the
  live re-verification restart was cut short by your shutdown — genuinely unverified,
  not just unattempted. Low risk (additive-only XML), but flagging since it touches
  every Droidworks race, not just G2.
- **Fish bestiary**: all 8 of your §6 rulings executed (per-biome mod homes, retire
  swfish_, keep BMT permanent, ship both hediffs, keep nicknames, add LungerFry now,
  build our own scalefish catches, fold in the Greentide fix + bladderboil). Genuinely
  new decision surfaced mid-build and already answered by you: Wasteland brine delivery
  is mining the pool floor (built). Twilight's roster is built but its wiring is HELD on
  a real structural gap — filed as its own item, `TWILIGHT_DEEP_WATER_LAYER_1`, needs
  your ruling (does Twilight get a real surface/deep BiomeDef split, or does the fish
  line wait).
- **The Kiln** is ruled: it's the sacred-sites dead crater (Zizzik/Mob'Unloo), not a live
  geothermal furnace — the roster doc's old text was wrong and is corrected.
- **Mynock**: the donor's version stays permanently unported — your ship-vermin
  `RSW_Mynock` is the only Mynock. Recorded so a future MLIE pass doesn't re-hit the
  same collision.
- **A genuinely new, unfiled defect surfaced and is now filed, unfixed**:
  `DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1` (see above — root cause found, fix committed,
  live re-verify owed).
- MLIE_FAUNA_ABSORPTION_1 Pass 20 was interrupted mid-flight by your shutdown — see "What
  is half-done" below, real generated art exists uncommitted, needs a decision (finish
  wiring vs. discard) before the next pass.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ANOOBA_DRAWSIZE_FIX_1` — fix already correct and deployed (found stale, re-verified with fresh math this pass); only live visual confirm (spawn + screenshot vs Warg/Iriaz at same zoom) never run; NEXT: live-spawn Anooba on a restart and screenshot-compare, then close.
- `CANON_CREATURE_REGEN_1` — waves 1+2 landed (10 creatures painterly-regenerated, fidelity sheets built and served, deliberately ungraded); wave 3 (Hawkbat/Kinrath/Kreetle — replacing already-wired ArtOverride art) was mid-daemon-job when this window ended, uncommitted/unfinished; NEXT: check `infrastructure/artpipe/done/canon_{hawkbat,kinrath,kreetle}_v1_*` for finished renders, verify+wire+commit wave 3, then walk waves 1-2's sheets (`Transient/canon_regen_wave{1,2}_2026-09-18/sheet.html`) for your fidelity grades.
- `CATHEDRAL_EXPOSURE_COMPLETION_1` — fall-stage sequencing, warzone posture flip, priced Hutt extraction, mourning register all built in `gm_blackboard_shadow.py`, offline-tested; deferred: live shadow-mode bridge run, re-check against item 3's linter once it ships, `CAMPAIGN_STORY_SITTING_1` ending ratification; NEXT: run the offline sequencing harness again to confirm nothing regressed, then a live shadow-mode bridge pass.
- `DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1` — root cause found and fix committed (`8d4f6fe39`, `useFactionXenotypes=false` across 4 PawnKind files + the generator); live re-verify was IN PROGRESS (a minimal-list restart) when your shutdown cut it short; NEXT: restart, spawn any Droidworks pawn, confirm no human face, close if clean.
- `DROIDWORKS_FORMAT_TIERS_1` — mechanics built; 2026-09-08 live test found need-gating doesn't respond to a stage change; root-caused this pass (the bridge's raw hediff-severity poke never triggers vanilla's `AddOrRemoveNeedsAsAppropriate()`, unlike a real `SetTier` call) and a new bridge tool (`jawa/droid_format_tier`) built+compiled to test the real code path, NOT deployed (DLL locked by running game); NEXT: deploy at next game-down window, re-run the original 7-box live-verify checklist using the new tool instead of the raw hediff poke.
- `DROIDWORKS_WIPE_SEVERITY_1` — fully built offline; live-verified the bed-requirement Harmony fix works (PASS, previously impossible); the actual wipe `ApplyOnPawn` completion is INCONCLUSIVE (log message-cap + AI-scheduling confounds, not a confirmed defect); NEXT: retest on a quiet quicktest map/log window to separate a real defect from noise — force the bill to completion directly rather than fighting colonist AI.
- `FISH_BESTIARY_BUILD_1` — huge session: all 8 §6 rulings executed, all 32 species + 4 owed defs built across 5 waves, a real bug found+fixed (3 waters' fish-wiring patches targeted dead donor BiomeDefs post-`BIOME_OWNERSHIP_WAVE_1`), a live verification pass run but blocked entirely by the water-terrain bug (see `QUICKTEST_RIVER_WATER_MISSING_1`) — genuinely NOTHING live-confirmed yet, not because the content is wrong but because no water generates on any test map right now; NEXT: after the water fix (`cd8ab494e`) is deployed+verified, re-run the live fishing pass across all 5 built waters (Scald/Wasteland/Cracked Lands/Weeping Stones/Greentide) — Twilight stays HELD on `TWILIGHT_DEEP_WATER_LAYER_1`.
- `FLORA_LEGIBILITY_BAR_1` — canvas-scaling law built and fixed (alientree/ambrosia's real root cause was wrong donor defNames in the backfill data, now corrected + regenerated live through the daemon); grading sheet built (`Transient/flora_legibility_sheet_2026-09-17/sheet.html`) covering 127 flora files, deliberately ungraded; NEXT: walk the sheet and grade — the flora legibility MODEL can't be fit until you do.
- `MASS_VALIDATION_LADDER_1` — manifest/runner machinery materially improved this pass (found+fixed `run_expectations.py --live` silently reading zero rows on every prior run — wrong JSON key; added `[key=value]` bracket lookups to the manifest DSL; fixed a missing `System.Type` case in the deep-serializer, rebuilt not deployed); one real L1 batch proof landed live (13 checks, 3 calls, zero restarts); the L2 behavior-gauntlet criterion and the "first review environment, owner-reviewed" criterion remain untouched; NEXT: deploy the Type-deserialize fix at next game-down, then attempt a real L2 batch run on 2-3 closed items.
- `PYRELANDS_FACING_REGRESSION_1` — turned out mostly already fixed by earlier sessions (Barbslinger superseded by an owner-approved scorpion redesign, Boomsnake/Mantistanis north+south regenerated and owner-approved) — this pass only re-verified by eye, made no changes; the one thing never actually confirmed is a LIVE spawn/rotate/screenshot check (all verification so far has been static PNG reads); NEXT: live-spawn each flagged creature after a restart and rotate-screenshot to confirm in-engine, then close.
- `QUICKTEST_RIVER_WATER_MISSING_1` — root cause found and FIXED in source (`cd8ab494e`): FlowWorks' generated compat patch used lowercase `viscosityClass` values, silently discarding 9 core water TerrainDefs every load via case-sensitive `Enum.Parse`. Generator hardened against recurrence. Confirmed this is a REAL regression affecting normal play, not a bridge-tool artifact. Deploy + cold load deliberately NOT done — that's the restart your shutdown cut short; NEXT: the very next restart should be this fix. After it, run `src/RimMandrake/bridgetools/prove_river_water.py --generate` to confirm water terrain generates on a fresh river/lake tile before trusting any other water-mechanism test this session flagged as blocked.
- `SETTLEMENT_VERBS_WAVE_1` — all 4 v1 verb families now have at least one real, compiled-in piece (salvage-law, walkable commerce, crime-suite/pickpocket, social-fabric/hire-the-placeless) for the first time — but a real defect was found+fixed along the way: pickpocket had silently never actually shipped (missing csproj `<Compile>` entry) despite an earlier pass reporting "0 warnings/0 errors." None deployed (RimProperty already loaded live, DLL locked). Substantial open scope remains in every family (night burglary/fencing/smuggling, haggling, rumors/sabacc/bribes) and the item's own `## criteria` was never revised to say whether "all four have a first piece" counts as done; NEXT: you rule on whether this item closes now or needs more sub-verbs per family, then deploy at next game-down.
- `SHIELD_MODS_LEVERAGE_1` — deeply built offline across many sessions (bubble mode, particulate screen, predictive failure alert, landing advisory, and this pass's escalating-damage half — built honestly to the ruling's actual "full strength from tick one" wording rather than inventing a ramp, and found vanilla already free-damages pawns so only ship-structure damage needed building). **ShipShields has never been enabled in ModsConfig at all — zero live/bridge verification of ANYTHING in this mod, ever.** NEXT: decide whether to enable it in ModsConfig (expensive-list ceremony) for a first-ever live pass, or keep building offline.
- `SHOKKWEAVE_SOLE_SOURCE_1` — deeply built and partly live-verified (web-cutting confirmed live, nest-raid dormancy bug found+fixed); this pass shipped the creep-web yield half and proved all 11 trader kinds source-side; item stays `needs: owner` on real open questions (trader-stock companion-tool decision, a new harvest-job build decision) — genuinely his call, not stale; NEXT: none for FOUNDRY until you rule on the open questions in the item file.
- `TILE_STRUCTURE_DESIGNS_1` — whisper side effectively done (8/22 built, remaining 14 all explicitly rejected/duplicated with evidence — coverage-lint satisfied); promise side went 16→19/22 this pass, 3 gaps re-confirmed genuinely blocked (an engine limitation, a needed mapsynth pipeline, and a doc contradiction on "The Kiln" — now RULED, see above, so that one promise gap should be re-attempted); NEXT: rebuild The Kiln's promise-row content now that its identity is settled (crater, not furnace), then the item's own remaining criterion is `GenStep_RimplacePlan` proven via a live quicktest — needs the bridge.
- `VALIDATION_SCRIPT_BACKFILL_1` — genuine finding: no standalone mod with a walk-doc and no script remains in the original 59 (absorbed mods' checklists belong in their parent's file; absorption doesn't imply coverage) — real coverage gaps found+fixed in 2 mods this pass (MandrakePatches, StarWarsPatches); backlog remains: SWBestiary×6, StructureInjectionsSW×1, StructureInjectionsRUT×2, UtinniPatches×1, MenuShell×1, FlowWorks×1, Pyrelands×1; NEXT: continue the same coverage-gap-audit pattern on that named backlog.
- `VAULT_THAW_QUEST_FAMILY_1` — everything already built+deployed by an earlier session, this pass just found the item's own "not deployed" claim was stale (byte-verified everything already matches disk); genuinely blocked on something new: `mandrake.rut.injections` (this mod's packageId) has apparently NEVER been added to the owner's real mod list at all — filed as an open question in the item file, not acted on; NEXT: you rule on whether that's a deliberate hold or an oversight; if oversight, add it to `ModsConfig.FULL.LATEST.xml` and the next restart can fire `RUT_GiveQuest_VaultThaw_V6_Umbra`/`_V1_RustCathedral` for the first time ever.
- `WYYYSCHOKK_FANG_PENDANT_1` — new mod built in full (`RimStarWars: Trophy Craft`), a real `<li>`-discard trap caught before shipping (butcherProducts is dict-keyed, not list-keyed), all 3 campaign factions' real defNames verified; zero live verification (bridge was held all session for other work); NEXT: live quicktest — butcher a wyyyschokk, craft the pendant, spawn a listed-faction and unlisted-faction observer, confirm the opinion delta and the trade-anywhere behavior, then close.
- `VAULT_DUNGEON_BUILD_1` — the 3 KCSG templates were already built+quicktest-proven by earlier sessions; this pass found and fixed a real regression instead (the MINIMAL modlist snapshot still named a dead packageId, `mandrake.rut.vaultdungeons`, absorbed into `mandrake.rut.injections` on 2026-09-09 — every MINIMAL-list restart since had silently tested zero vault content). Re-proved types ① and ③ live clean; type ② reproduces a known 2026-09-06 gap (its third-party symbol-source mods aren't on the MINIMAL list — a test-scope gap, not a template defect). Item stays `doing` per its own instruction (hand-finishing the 6 real sites + world_commit writes are explicitly "with the owner", never solo); NEXT: none for FOUNDRY until a joint bench session on the 6 real sites.
- `MLIE_FAUNA_ABSORPTION_1` — Pass 19 landed clean (29/90 remaining, front of worklist Pufferpig/Qormot/Ronto). **Pass 20 was mid-flight when your shutdown hit**: real generated art + def files exist UNCOMMITTED for Pufferpig/Qormot/Ronto (`git status` shows them untracked) — validated and clean for Pufferpig/Qormot, but `RSW_Ronto` FAILS `validate_patch.py` (texPath doesn't resolve without `--defs`, likely needs the same `loadAfter mandrake.rsw.rontoartoverride` fix Nuna/Iriaz needed but never got it — Ronto already has an art override mod covering east/north/south; the new file only added the uncovered Dessicated variant, correctly, so this may just be a validator limitation needing `--defs` to confirm, not a real defect). Cast wiring and the worklist json were NEVER updated for this pass — nothing is half-wired, it's cleanly all-or-nothing. NEXT: run `validate_patch.py --defs` on `RSW_Ronto.xml` to check whether the FAIL is real; if clean, finish wiring all 3 into BiomeCast_Ashkarr.xml + cast_assignment.csv + the worklist json and commit; if genuinely broken, just discard the 3 untracked def files (the PNGs are real generated art, worth keeping — check for a `loadAfter` fix before regenerating any of them).

## Traps learned

- A mis-cased enum value in a `modExtensions <li>` silently discards the WHOLE target
  def, same class as a missing modExtension type — cost this session most of its live
  water-mechanism testing before the cause was found (filed: LESSONS_INBOX).
- `Reached max messages limit. Stopping logging to avoid spam.` makes Player.log go
  dead mid-session and LOOKS like a hang; it is itself a finding (something is
  spamming), read the spam before assuming a crash (filed: LESSONS_INBOX).
- A bridge tool can read the RAW mutator field while the engine iterates a
  Harmony-postfixed PROPERTY that filters it — check the raw-vs-filtered pair before
  blaming either side of a mismatch (filed: LESSONS_INBOX).
- `run_expectations.py --live` was silently reading zero rows on every prior run (wrong
  JSON response key) — an instrument that reports clean because it never actually
  looked (filed: LESSONS_INBOX, this session).
- `deploy_custom_mods.py --apply` reporting success/in-sync does not mean a mod is
  ENABLED — hit three items independently this session (VAULT_THAW_QUEST_FAMILY_1,
  SHIELD_MODS_LEVERAGE_1, STICK_FOOD_INGEST_1 all had fully-deployed, zero-live-tested
  mods absent from ModsConfig.xml entirely) (see: LESSONS_INBOX, "deploy ≠ enabled").
- A companion/mod DLL cannot be written while the game is running (OS file-lock, not
  corruption) — hit again this session on Droidworks, RimProperty, ShipShields; the fix
  is never to force it, note it as owed to the next game-down window (filed:
  LESSONS_INBOX).
- A debug-dialog click (`rimworld/click_ui_target` on a `Dialog_DebugOptionListLister`
  row) reports success and the dialog closes, but the underlying delegate never fires —
  reproduced independently on two unrelated actions this session
  (`COLONY_VISIBILITY_BUILD_1`, and the same failure class `CAST_ROSTER_269_LOAD_1`
  already documented) — this whole debug-action-click mechanism is unreliable for
  triggering anything, not just one widget (see: `COLONY_VISIBILITY_BUILD_1`'s own note;
  worth filing to LESSONS_INBOX if not already there).
- A `git pull --rebase --autostash` from a peer window can silently revert your
  in-progress edits mid-pass, not just between commits — three MLIE passes this session
  hit it; the recovery is to wait for `.git/rebase-merge` to clear, then `git diff --stat`
  every file you believe you changed and redo any showing zero diff (filed: LESSONS_INBOX,
  "peer autostash" entries).
- A `.csproj` with `EnableDefaultCompileItems=false` silently drops any `.cs` file not
  explicitly listed — `RM_Property`'s Pickpocket verb compiled "0 warnings/0 errors" and
  never actually shipped for a full pass because two files were missing from the
  `<Compile>` list; "clean build" is not evidence a new file is even IN the build
  (filed: LESSONS_INBOX).

## Closed since the last handoff (10)

- `DIRTY_CODE_REVIEW_LOOP_RESTART_11` — 6d0c2bc2a49548e66b219d80cc2f42e7ec0b38d3
- `DIRTY_CODE_REVIEW_LOOP_RESTART_12` — 02498a0a23726486d4171489f35d0a1e2c8ed426
- `DIRTY_CODE_REVIEW_LOOP_RESTART_13` — 8a0a88e18710bcb1b37484f77665ceba3854f470
- `DIRTY_CODE_REVIEW_LOOP_RESTART_14` — f42da4dd6
- `DIRTY_CODE_REVIEW_LOOP_RESTART_15` — 7aea51f56236dfb33be4580b81c9fe3caf60cceb
- `RAZORJACK_IDENTITY_RESTYLE_1` — 0b8d46beb6042a7df39ae2e0261051bb2fad453a
- `MANTISTANIS_CAMO_REGEN_1` — d2808c9b056c09502b087aa8611a2da2ad233da0
- `SCORCHFRUIT_ART_REGEN_1` — 5909420825e9e27baf46bd29befd791293cbefa7
- `BARBSLINGER_REDESIGN_1` — 3d58116c2027bfa544f124b1e841cf6f12878649
- `IRIAZ_ART_REGEN_1` — 039622eff305ffbadcb4640339e5dafb9b133afa

## Filed and still open (9) — the next seat's queue

- `ROT_ART_WAVE_1` — Land the 22 rot artpipe jobs: review daemon output, deploy textures, verify texPaths render
- `FISH_BESTIARY_BUILD_1` — Build the fish bestiary: 32 RUT_ species across 8 registers on 7 waters, per-biome mod homes, all 8 §6 questions ruled 2026-09-18
- `FLOWWORKS_BOTTLED_LIQUID_TYPE_MISSING_1` — RM_BottledLiquidExtension type not found: RM_LiquidBottles_Base.xml discards + drives ~82 defs / 420 crossrefs on the full load
- `ENVHAZARDS_DLL_REBUILD_OWED_1` — EnvironmentalHazards repo DLL is stale vs source (RM_RootCausewayBiomeExtension.cs 21:29 > DLL build 20:12) — rebuild + redeploy
- `GIZKA_NEWGAME_NRE_FIX_1` — Fix gizkastowaway's new Game() reading-policy NRE so it can be re-activated
- `VALIDATE_PATCH_FULL_TREE_SWEEP_1` — First-ever full validate_patch.py sweep of UtinniPatches+SWBestiary surfaces 37 errors/2193 warnings across 408 files, never triaged
- `TWILIGHT_DEEP_WATER_LAYER_1` — Twilight Deep needs its own under-roof water layer before fishTypes can wire
- `QUICKTEST_RIVER_WATER_MISSING_1` — Quicktest maps generate zero river/lake water on any biome tried this session, blocking water-mechanism verification
- `DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1` — Droidworks races (G2 included) show a default human face despite RSW_DW_HeadType_Blank — AlienRace head-render gap, not a def error

## Commits

```
8d4f6fe39 DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1: root cause found, useFactionXenotypes=false
1d719c443 File DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1: droids show a human face
d24a4fdd9 DROIDWORKS_PRIMITIVE_TIER_1: correct stale briefing, no new G2 art needed
693ea051e SHIELD_MODS_LEVERAGE_1: build the escalating landing-hazard damage half
6ded2767f DROIDWORKS_WIPE_SEVERITY_1: live-verify pass, bed-gate fix confirmed, ApplyOnPawn completion inconclusive
646069cb8 NINEFOLD_ENGINE_M0_1: ground and wire Ishko/Oomo's first-contact hooks; correct a stale code-review claim
3636fae79 COLONY_VISIBILITY_BUILD_1: correct stale briefing, note reproducible dialog-click bridge trap
00a13d98f STICK_FOOD_INGEST_1: re-verify offline state, decline forced restart
b60c7e4ff DROIDWORKS_FORMAT_TIERS_1: jawa/droid_format_tier, the real fix for the need-gating test gap
5cd08fc86 MASS_VALIDATION_LADDER_1: live-wire the runner, fix what it found
5c09ebe31 SETTLEMENT_VERBS_WAVE_1: fourth verb family (social fabric: hire the placeless); fixes a real Pickpocket build gap
d95d7ec55 SETTLEMENT_VERBS_WAVE_1: crime-suite pass builds pickpocket
855112fee VAULT_THAW_QUEST_FAMILY_1: deploy already done, live quicktests still owed
e03de65fa LESSONS: mis-cased enum eats a def; log spam cap blinds diagnosis; raw-vs-filtered mutator reads
e647cdfe5 ledger sync: QUICKTEST_RIVER_WATER_MISSING_1 needs owner (deploy gate)
cd8ab494e QUICKTEST_RIVER_WATER_MISSING_1: lowercase viscosityClass deleted every water terrain
402f7a2ab FISH_BESTIARY_BUILD_1: live fishing verification, first real bridge pass
6d8ec7c70 FISH_BESTIARY_BUILD_1 wave 5: Twilight's remaining 7 species + rare table, built but HELD; hold confirmed real
0da141b42 FISH_BESTIARY_BUILD_1 wave 4: Greentide's remaining 7 species + fry + rare table
748f6c36b BENCH reboot handoff 202609180533: rot wave (6 closed) + campaign-load rescue (gizka NRE)
... 83 more: git log --oneline c830d86bb..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-09-18T13:50:03Z

Uncommitted (replace each not identified, low-risk (not a def/code file) -- next seat should check before assuming it's safe to ignore with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   the codebase-health generator (periodic, not any one seat's edit)
 M Transient/codebase_health.json   the codebase-health generator (periodic, not any one seat's edit)
 M Transient/codebase_health_artifact.html   the codebase-health generator (periodic, not any one seat's edit)
 M infrastructure/dashboards/hub/data/health.json   the codebase-health generator (periodic, not any one seat's edit)
 M infrastructure/state/codebase_health_last.json   the codebase-health generator (periodic, not any one seat's edit)
 M infrastructure/state/ledger/events.jsonl   shared ledger/queue churn from concurrent windows tonight, not mine
 M infrastructure/state/queue/BENCH.md   shared ledger/queue churn from concurrent windows tonight, not mine
 M infrastructure/state/queue/FOUNDRY.md   shared ledger/queue churn from concurrent windows tonight, not mine
?? defs.sqlite   a def-dump capture from a concurrent window's harvest, not mine
?? deployed/config/ModsConfig.before-tier-oracle.xml   a pre-swap ModsConfig backup from another window's mod-tier work, not mine
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   a pre-swap ModsConfig backup from another window's mod-tier work, not mine
?? deployed/config/ModsConfig.before-tier-warlab.xml   a pre-swap ModsConfig backup from another window's mod-tier work, not mine
?? infrastructure/artpipe/active/rut_agelesscap_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_brewingvessel_v1_south.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_euphoriccrown_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_falsefruit_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_furnacecap_plant_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_gene_furnaceblood_icon_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_grownfurnace_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_liveingredient_agelesscap_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_liveingredient_euphoriccrown_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_liveingredient_regenerantveil_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_liveprep_toxicinjection_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_livingfurnacecap_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_palemoss_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_paletree_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_regenerantveil_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_symbiont_mycoid_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_symbiont_nightwake_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_symbiont_quickflesh_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_symbiont_sheenblood_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_tea_agereversal_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_tea_bioregeneration_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/active/rut_tea_pleasure_v1.json   another window's pending art jobs (Pyrelands rot-wave family, ROT_ART_WAVE_1), not mine
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log   an old daemon log from a prior BENCH restart, not mine
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_east.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_north.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_south.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_east.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_north.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_south.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   MINE -- CANON_CREATURE_REGEN_1 wave 3 daemon jobs, finished after the wave-3 agent was stopped for the reboot; unverified/unwired, see half-done entry
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   another window's FlowWorks art job, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   another window's FlowWorks art job, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   another window's FlowWorks art job, not mine
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   another window's FlowWorks art job, not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   an earlier session's Pyrelands art-regen job (already landed/documented on PYRELANDS_FACING_REGRESSION_1/NUNA_ART_REGEN_1), not mine
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   the dead pre-library toy-figurine pilot's own rejects, not mine, harmless
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   the dead pre-library toy-figurine pilot's own rejects, not mine, harmless
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   the dead pre-library toy-figurine pilot's own rejects, not mine, harmless
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   the dead pre-library toy-figurine pilot's own rejects, not mine, harmless
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   the dead pre-library toy-figurine pilot's own rejects, not mine, harmless
?? infrastructure/state/.rimflow_conc_97j8px_9/   a rimflow concurrency lock artifact, not mine, safe to ignore
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   another window's CherryPicker pre-swap backup, not mine
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Pufferpig.xml   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Qormot.xml   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Ronto.xml   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Textures/swanimals/Pufferpig/   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Textures/swanimals/Qormot/   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Textures/swanimals/Ronto/   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
?? src/RimStarWars/SWBestiary/Textures/swresource/Meat_Ronto/   MINE -- MLIE_FAUNA_ABSORPTION_1 Pass 20, interrupted mid-flight by the reboot; see half-done entry (validated for Pufferpig/Qormot, Ronto FAILs validate_patch.py without --defs)
```

