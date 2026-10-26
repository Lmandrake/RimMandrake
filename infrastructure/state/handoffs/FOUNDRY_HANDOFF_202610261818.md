# FOUNDRY_HANDOFF_202610261818 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610260536`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-25/26): "wake foundry and full belt", then "You may have up to three subagents" — ended when he wrote "please wrap up and handoff now". The offline queue for FOUNDRY ran as ~100 waves of the standing code-review loop (now item `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE`; the old `…_STANDING_LOOP_1` was closed by mistake and cannot be reopened). 🔑 **The loop keeps finding real bugs in the PREVIOUS wave's fixes and in verdict tools (vacuous selftests, blind reads/ignored exit codes that then delete or pass).** Review by risk, not alphabetically; a fixer never marks its own file clean; mutate each guard on a scratch copy. Nothing in this order is deployed or live-tested — BENCH holds the bridge and every fix is offline-proven only. (filed: ledger + lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Cards he answered: biome labels = OUR names only (done, 6173d05d32); meteorites = metals/ores only (done); fish = only big fish drop fishskin (done, RM_Fishskin); Thornhold = stands its ground, Shirrel = REAL glide as a flyer (his pick over my recommendation; flight never live-tested), Rollbug = takes ANY corpse in reach incl. his colonists (his pick; Mod Setting turns it off).
- Delegated design calls logged `--why "delegated: ..."` for his daily digest: unpowered shield bubble blocks nothing; Cathedral Pass revoked on striking a machine (judge: UPHOLD, wording revised); leather picks (judge UPHOLD); seabed fire ban covers stoves/generators (per CHILL_FIRE_BAN_1); day mushrooms grow in the dark; tetchik glower gate 10 plants anywhere (provisional); Force forecast wording; Sith inquisitor not in friendly aid.
- Open owner-eyes items: `ARMOURTIER_DECIDE_COMMANDO_NOT_MANDO` (6 commando defs rated beskar before the rewire), `LEATHERFACTORS_FIX_KEEP_OWN_STATS`, `PLASTEEL_AUDIT_EXPLICIT_MINEABLE_LISTS`, `ACCEPT_LOOKS_DECIDE_REJECTS_STILL_STAND`.
- Seven donor patches (kotorcore/vaewaste gates) NEVER ran until 61dcf6562d rewired them: Armour/stun/PawnFlavor/Megafauna changes reach the game for the first time at the next deploy — review the diff before deploying.
- Nightly 03:00 selftest sweep skips unchanged tests (no --full); outside-repo probes now re-check (730e76a2bc).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE` — open; ~2200 never-reviewed code files + ~70 DIRTY remain (FlowWorks/GSS are BENCH's); NEXT: review RimStarWars ranks #19-#30 (`RSW_ZeroedOreGates.xml`, `RSW_BronziumDrop.xml`; risk_rank_rsw.md and risk_rank_rsw2.md #38-#56) then TerminalBiomes/Stillsand/Scarlands by risk.
- Fixer-edited files stay DIRTY (a fix never marks a file clean): NEXT: run an independent fresh-eyes pass over every file named in the wave notes (progress_w95..w101.md in the FOUNDRY scratchpad), starting with `RSW_SithLineHarmony.cs` Anzati postfixes (fd1eb80fc6) and the Force-forecast texts (d2436394d5) whose review wave 100 never reported.
- DEPLOY OWED (nothing below is in the game folder) — NEXT: when BENCH has the bridge/game is down, run `deploy_custom_mods.py --mod <name>` dry-run, read it, then --apply for Armoury, SWBestiary, SithLine, StarWarsPatches, UtinniPatches (plan also deletes ArtFold files: read first), LeaningScrub, CreatureBehaviors, DivingInteraction, EnvironmentalHazards, TerminalBiomes, LanternDeeps, EggReckoning.
- Live checks owed to BENCH — NEXT: run the walk lines in `design/validation_walks/RimMandrake/LeaningScrub.md` (dens, bloom_sway_and_exit_hole, rollbug_rolls_any_corpse, Shirrel flight-STATE read only; the visual flight check is a joint session with him), meteorite chain (`METEORITE_ADAPTER_PROVE_LIVE_CHAIN`), `ARMOURY_ORE_TOGGLES_PROVE_OFF_LIVE`, TileFeatures checks 1-9.
- `ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG` — 27 twins pruned, Destroyer requeue owed; NEXT: fix `REGENGATE_ALIENRACE_BODYPATH_FIX_DONOR_BLIND`, queue `desert_gap_Destroyer_v1_south` through it, then close.
- `ARTSRC_LEGACY_UNMIGRATED_AUDIT_PURGED` — 2257 legacy files never migrated, some purged art; NEXT: audit against the purge ledger before any migrate.
- `ARTFOLD_DELETE_PATCHES_RETIRED_SWAC_DONOR` leftovers `SWACFOLD_DECIDE_ANOOBAM_MYNOCK_UNDRAWN` — NEXT: `art install` onto our creatures or delete the two folds.
- `VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT` — early `return` in check rows: 155 sites in 23 validation.py (Webwork 32, Scarlands 22); NEXT: audit per mod and fix the chains that skip rows.
- `SCRUBAMBUSHERS_BUILD_EDGE_RUN_CANOPY` and `SHIRREL` follow-ups: NEXT: build Shokka edge hold / Fuzzviper run-wall hold / Ribbonwhip canopy (offline C#).
- `RACES_JUDGE` done; `PROPANE_PIPES_DECIDE_FLOWWORKS_LANE` filed for BENCH (RUT_PipeSegment tickerType Normal made by FOUNDRY); NEXT: BENCH rules lane.
- `CSPROJ_BUILD_COMMENT_NAMES_READONLY_MIRROR` (~91 csprojs) — NEXT: one scripted comment fix, then rebuild nothing (comment only).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- `./publish` refuses while ANY helper's DLL/.srchash or edited file is uncommitted, and it rebases: always read `git log origin/main` for the real sha before `rimflow close --sha` (a local sha closes against nothing). (filed: LESSONS publish-dll-peer-dirty, publish-rebases-close-after)
- A closed rimflow item cannot be restarted — never `close` the standing loop item; file a continuation. (this handoff) (filed: lessons)
- `rimflow file/note --by-card` writes the OWNER shard: commit `infrastructure/state/ledger/events/OWNER.jsonl` by explicit path or `./publish` refuses. (this handoff) (filed: lessons)
- `validate_patch.py` is silent on patches nested in custom PatchOperation classes and over-counts `/Defs` per file; `--defs` needs ALL THREE roots (Data, workshop 294100, Mods) or it refuses UNMEASURABLE. (filed: LESSONS)
- `winbuild` rsync skipped same-size edits within 2 s (fixed 9bc564eecd). Fixers' `mark-clean` of their own edits is wrong by policy: re-review. (filed: LESSONS)
- A Corpse.Destroy eats its inventory; vanilla CompHeatPusher double-pushes on pawns; scatter counts that round to 0 place nothing silently; refuel/Kill hooks differ — see LESSONS 20261026T*. (filed: lessons)

## Commits

```
4ae6a284d2 ASTEROIDQUEST_FIX_PLASTEEL_PICK_NO_COUNT: RSW_OdysseyAsteroidNoPlasteel.xml took the MineablePlasteel count out of GenStep Asteroid, but the Odyssey quest OpportunitySite_Asteroid still listed MineablePlasteel as a possible pick (Script_SpaceSites.xml:47). Its AsteroidMiningSite uses mapGenerator Asteroid, so GenStep_Asteroid.SpawnOres (decomp :157) logged 'No count found for resource' and left a 'plasteel asteroid' with no ore. A new Remove drops that pick, and the header now names it. New selftest_odyssey_asteroid_pick_counts.py replays the patch over every Odyssey Defs file. It requires zero plasteel or components references and a GenStep Asteroid count for every quest pick. A probe requires at least 8 references unpatched. It is green now and red on HEAD~ (1 reference left, plus the no-count pick). selftest_canon_materials_audit is still green.
85048a33fc gitignore: art_eval run kept/ copies are derived from the art store
2853debffa conversations: catch-up 3 record(s)
1be5b50529 BESKAR_FIX_DEEPDRILL_UNDER_LK_GATE: RSW_BeskarNeverReforged.xml zeroed OuterRim_Beskar deepCommonality only inside the "LK Mineable Resources Outer Rim" FindMod. Outer Rim - Core ships 0.001 itself (1.6 Stuff_Beskar.xml:22), and LK is not in the load, so the 2026-10-26 dump showed beskar as deep-drillable, against L7 "mining routes produce nothing". Both deepCommonality ops now sit in the Outer Rim - Core block, with an unchanged shape (Replace, or Add if absent), and still run after LK's .75 when LK loads. prove_canon_materials.beskar_check now also replays the patch with Outer Rim alone on a fixture of Outer Rim's own fields. New selftest_beskar_live_modset.py is red on the old file and green now, and an empty-patch probe shows the check can see. prove_canon_materials --selftest is green. validate_patch: the new placement matches 1 node in Stuff_Beskar.xml; the 8 errors are the pre-existing LK-absent ones inside the LK FindMod.
218efc69f8 ledger: ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG classified 31 (A20 S8 P2 B1 D0; C3 already in art store), twins pruned 27 ids via 2348af749110; files REGENGATE_ALIENRACE_BODYPATH_FIX_DONOR_BLIND (blocks Destroyer requeue) and ARTSRC_LEGACY_UNMIGRATED_AUDIT_PURGED
2348af7491 ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG: artpipe_state.py twins excuses a lost _artsrc PNG only by art-store evidence
83cdb73c83 ledger: w100 closes (SITHLINE/BACTA/SARLACC/GIZKA/BRAINWORMS/GRAFFITIIMPERIAL/TROPHYCRAFT fixes at origin shas), file TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS + VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT, note DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE; carries other FOUNDRY agents' appended events
bcf5dcb837 lesson: a return inside a modcheck with-row ends the whole chain (and hides later rows from required_checks); restore the prior upstream_reason, never None
96638e1959 TROPHYCRAFT_VALIDATION_FIX_SKIPPED_ROWS: TrophyCraft validation.py had two faults. (1) A `return` inside a `with t.component` row left the whole CHAIN: in crafting a PASS on the products row dropped the layer and pendant rows from the record, in fang_drop a PASS dropped the unpatched control, and in social_thought a declared UNMEASURED on row 1 meant rows 2-3 were never recorded. The offline probe could not see them either, so required_checks.json lacked 3 rows. Row bodies are now functions, and a reason-restoring _comp lifts a declared UNMEASURED so each row gives its own reason. (2) defs_resolve and fang_drop read the donor Wyyyschokk, whose patch block was deleted in 3265277e01, so every live run gave a false FAIL. The fang is now read from RM_Ollathrix, the patch's only target (UNMEASURED without mandrake.rm.webwork), and the donor row is dropped. A static check pins the patch target. Walk deps and rows updated; required_checks.json rebuilt (other mods' rows refreshed from committed scripts). New selftest_trophycraft_validation_chains.py (modcheck TestContext, fake bridge): red on 7 checks against the old file, green now; static PASS.
b056148973 BENCH handoff 2026-10-26 10:56 PDT
79b4fb98ae conversations: catch-up 2 record(s)
078e60209d ledger: OWNER shard
028a3eaae1 ledger: BENCH bridge release after live round 5
cb8f6b4dfe DIANOGA_FIX_YOUNGCASK_LABEL_LEFTOVER: RSW_Sekkulaath_DianogaGiant.xml now relabels RM_SekkulaathYoungCask "dianoga young-cask". The cask def (6c34f761ae) postdates the reskin (b1948944cd), so with the SW tier loaded it was the one player-facing "sekkulaath" left in the 2026-10-26 dump. Its description names nothing, so it stays as written. The brood-ransom young follows the tank swap through YoungKind/occupantKindDefName. New selftest_dianoga_reskin_coverage.py requires every top-level Fever Wood label/description containing "sekkulaath" to be the target of an op in a SW patch. It is red on the old file and green now. validate_patch (Data + workshop + Mods + live dump): 0 errors, new op 1 match.
1ee7574a69 GRAFFITIIMPERIAL_VALIDATION_FIX_LOST_REASON: GraffitiImperial validation.py _comp set upstream_reason = None after lifting a row's UNMEASURED. A later plain FAIL latches without setting a reason, so in framework_wiring (row 1 shape unreadable -> UNMEASURED, row 2 sibling unresolved -> FAIL) empire_faction_def_resolves read UNMEASURED with detail None. _comp now restores the prior reason. New selftest_graffitiimperial_unmeasured_reason.py drives the production chain through modcheck's TestContext on a fake bridge: red on the old file, green now; static PASS.
a71281e42a BRAINWORMS_VALIDATION_FIX_BORROWED_REASON: BrainWorms validation.py infection_state is stateful (row 2 reads the pawn row 1 infected), but _comp lifts row 1's UNMEASURED, so with the hediff hidden from pawn_get row 2 ran on and reported a symptom ("pawn_get hediff rows carry no severity field") instead of the cause. Row 2 now names the row above's reason when no readable infected pawn was established. _comp also restores the prior upstream_reason instead of None (a later plain FAIL latches without setting one, leaving later rows with no reason). New selftest_brainworms_unmeasured_reasons.py (modcheck TestContext, fake bridge): red 2 checks on the old file, green now; selftest_brainworms green; static PASS.
a096f60c91 GIZKA_VALIDATION_FIX_LOST_REASON_DONOR_PICK: three harness faults in GizkaStowaway validation.py. (1) _comp set upstream_reason = None after lifting a declared UNMEASURED; a later plain FAIL latches without setting a reason, so every row after it read UNMEASURED with detail None (harmony_wiring: 3 rows). It now restores the prior reason. (2) donor_patch took the first resolving kind, the donor's Gizka, but only RSW_Gizka is patched (the donor block was deleted in 3265277e01): a false FAIL on 100 whenever the donor loads. It now reads RSW_Gizka only, UNMEASURED without it. (3) static_checks still demanded the deleted donor block: STATIC FAIL on HEAD; now checks the port's single MarketValue 15 and its targets. New selftest_gizka_validation_chains.py (modcheck TestContext, fake bridge): red 3 checks on the old file, green now with an unpatched-port FAIL control; selftest_gizkastowaway green; static PASS.
2c71d47a08 ledger: close ART_SELFTESTS_FIX_LIVE_DATA_DRIFT at a69cfd0b3a; ARTPIPE_TWINS_PRUNE_FAILED_COPY blocked on new ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG (31/32 twins have no PNG; prune not applied)
e7c155da4e ledger: live round 5 hose T2 fail (5.9 s frames), levelling timed PASS links 100, cold storage load note
9a5b67555a ledger: close FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS at 861069cb4a; GSS rows note; file REVIEW_MAP_FILL_FIVE_UNSTATIONED_DEFS
... 823 more: git log --oneline f98801092d..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M conversations/2026-10-26-0215-7ee2108f.md   (BENCH/FlowWorks capture or derived file, not mine)
 M infrastructure/state/ledger/events/FOUNDRY.jsonl   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_20261017T084726.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_p00.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_p03.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_p10.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S1_p14.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_p00.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_p10.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_p30.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S2_p60.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S3A_p20.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S3B_p06.png   (BENCH/FlowWorks capture or derived file, not mine)
?? Transient/fw_scenes/live/S3B_p16.png   (BENCH/FlowWorks capture or derived file, not mine)
... 117 more uncommitted paths (by top-level dir: Transient 115, design 1, infrastructure 1): git status --short
```

