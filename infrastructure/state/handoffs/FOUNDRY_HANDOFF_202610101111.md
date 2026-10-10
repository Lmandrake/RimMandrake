# FOUNDRY_HANDOFF_202610101111 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610100040`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Helpers landing by plumbing (land.sh) leave the shared clone's HEAD lagging origin with ~560 phantom 'modified' files, and a scratchpad checkout makes every dotnet.exe-wrapper selftest fail with MSB3030 — two false 'red' signals that cost a round of fixers each. Verify against origin/main (git fetch; compare bytes) and run selftests from /home/mandrake/rm/foundry, never from a scratch clone.

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Art to LOOK at (complete paths, rulings needed) is indexed in `D:\Luke\dev\RimMandrake\Transient\OWNER_MORNING_LOOK_20261010.md`: icon renders batches 1-3 and gap art (install yes/no); Rot v3 and ossrith v3 are installed already.
- Owner decisions queued: (1) FlowWorks walk step 4: each feature basic Utinni play / core proof / extended? (2) phrikite desert: Stillsand+ExtremeDesert (built) or BlueDesert? (3) solar oven crest keeps melting glass? (4) doonium/phrik smelts on donor + all 3 WreckedMachines tiers or Repaired only? (5) RM_Ismerrow: install miasma_ismerrow_a? (6) RUT_FungalSoil icon: copy TheRot MycelialSoil.png? (7) RM_TollukCap outline-free v4 render ready for look; harvest numbers PROVISIONAL. (8) FLOW_ORDER_EXTERNAL_INPUT_1 part 2 design fork; LONGSHADE_SHADE_EXTRAS_1 ruling. (9) FlowWorks north star still DRAFT — needs his re-validate. (10) Braskeen v2 renders await his pick.
- Shipped on his word by card: zersium minLumps guarantee, durasteel/transparisteel/doonium/phrik builds, bronzium cut by patch (no Cherry Picker), sandlock stops sarlacc, Pits capability retired, ~100 mods moved onto SettingsKit screens (live look at all owed).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ICON_OUTLINE_REPAINT_1` — batches 1-3 (75 jobs) rendered, none installed, ~119 outlined files unqueued (mostly stack variants / RUT_ duplicates); NEXT: after the owner rules on the contact sheets, install approved renders through `art.py install` and queue the rest.
- `gap_RM_Dakkra_rest_v1_north/south` — requeued against the finished east; NEXT: when rendered, install all three facings to LongShade RM_Dakkra_rest via the art ledger.
- `CANON_MATERIALS_BUILD_1` — durasteel/plasteel/transparisteel/doonium/phrik built offline; NEXT: owe L3-L10 live loads (bridge); not marked implemented.
- `ZERSIUM_FORGE_BIOME_1` / `BRONZIUM_DROP_1` / `LONGSHADE_BEDAZZLE_MECHANICS_1` — built offline; NEXT: live verify on fresh Forge maps, a minimal-list load, and haze/ash-pulse/sand-lock in a quicktest.
- `MOD_OPTIONS_RETROFIT_1` follow-through — SettingsKit screens landed for ~100 mods, none seen live; NEXT: bridge-screenshot a sample of settings windows (FlowWorks A5 first).
- `SELFTEST_RED_EIGHT_1` — all eight reds fixed or explained; NEXT: re-run run_selftests.py from /home/mandrake/rm/foundry and close the item if green.
- Bridge — BENCH's hold was idle 148+ min with the game down at my last look; NEXT: `rimflow bridge who`, and take it only if the owner allows (he said earlier I do not have it).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- Clone HEAD lags origin after plumbing lands; `git status` shows hundreds of phantom diffs; use `git diff --quiet origin/main -- <path>` (see: Transient/clone_reconcile2_20261010.md)
- Selftests that shell to dotnet.exe fail with MSB3030 from a scratchpad/ext4 clone path but pass from the real clone (see: Transient/selftest_fix4b_20261010.md)
- `selftest_settings_screens.py` is shared: land.sh ships the working-tree copy, so start each land from `git show origin/main:<file>` (see: Transient/builder_a5_20261010.md)
- A `git archive` export has no .git, so selftests using `git log` (utinnipatches dump skip) misreport (see: Transient/selftest_fix3_20261010.md)

## Commits

```
ff6d366ee FOUNDRY ledger shard: 3 trailing local events
1a44ec30e Gap art: requeue RM_Dakkra_rest north/south against finished east
7ad9b5226 Icon batch 3 + gap art contact sheets, owner morning index; ICON_OUTLINE_REPAINT_1 note
015d262e3 selftest fix4b report: 8 selftests pass in real clone; scratchpad-clone UNC builds were the failure
d6e7ab723 Six C# selftest wrappers stage on D: via winbuild before dotnet run (UNC build from ext4 clone fails MSB3030)
ea7252acc Stillsand lint: slider default looked up across all settings classes (thumperRadius moved class in a935fa379)
567f8c10e Transient: batch Y settings retrofit report
98bc0c4cc builder_s10x report: SettingsKit retrofit of 12 mods
d35fb9df7 MOD_OPTIONS_RETROFIT_1: SWBestiary's three settings screens (Livestock, Ikee, BeastMechanics) on SettingsKit; kiln cooldown, moornak release and innate abilities next pulse, rest now
f6b08d378 MOD_OPTIONS_RETROFIT_1: WeepingStones settings screen on SettingsKit (7 groups; oasis flora NewMapsOnly+worldgen, dewsilk next game start)
5798df955 MOD_OPTIONS_RETROFIT_1: BrainWorms settings screen on SettingsKit (cargo incident next pulse, rest now)
21fdda515 MOD_OPTIONS_RETROFIT_1: JawaRules settings screen on SettingsKit (generation fixes NextPulse; sow ban, hood, map labels Now)
94ecf9b07 MOD_OPTIONS_RETROFIT_1: UtinniStatues settings screen on SettingsKit (carving and idol fuel next game start, idol burn next pulse)
84c515281 MOD_OPTIONS_RETROFIT_1: JawaIonWeapons settings screen on SettingsKit (5 groups, all read per hit: Now; SelfTest csproj links the kit)
94bed27ce MOD_OPTIONS_RETROFIT_1: WildsteamEggBounty settings screen on SettingsKit (quest switch next pulse)
88271c2f6 MOD_OPTIONS_RETROFIT_1: TrophyCraft settings screen on SettingsKit (2 groups, both now)
d3dd4d3e9 MOD_OPTIONS_RETROFIT_1: ShokkweaveEconomy settings screen on SettingsKit (silk scatter NewMapsOnly + worldgen label)
2eeeccc90 MOD_OPTIONS_RETROFIT_1: ShipMemory settings screen on SettingsKit (2 groups, both now)
a6c8bcf79 MOD_OPTIONS_RETROFIT_1: DesertVehicleReskin settings screen on SettingsKit (single fuel toggle, Now)
e6bb5d6ff MOD_OPTIONS_RETROFIT_1: WildsteamEggBounty settings screen on SettingsKit (quest switch next pulse)
... 299 more: git log --oneline e2622ff17..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/.b4_day.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_lasso.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_rost.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_state.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_vte.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_wealth.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_web.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_web2.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_win.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.b4_win2.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.fw_v2_g.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.fw_v2_g2.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_aerial_g.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_aerial_g2.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_aerial_g3.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_h07_g.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_h07_g.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hm_g1.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hm_g2.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hm_g3.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hm_g4.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hm_g5.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g1.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g2.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g3.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g4.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_hose_matrix_g5.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_live_g.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_live_g2.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_live_g3.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_live_g4.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.gss_scenes_g.json   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/.probe/   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/acc_d_checks.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/acc_d_checks2.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/acc_d_gloom.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/bd_a5.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_acc3_q_20261009.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_acc4_diff_out.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge5_burst2.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge5_burst3.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge5_reads2.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge5_reads3.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge7_hood2_out_20261009r.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge7_hood3_out_20261009r.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge7_hood_out_20261009r.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_bridge7_zersium_out_20261009r.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/belt_g_shots/belt_g_settings_mandrake_rm_flowworks.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/clone_reconcile2_20261010.md   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/fc_a5.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/gen_gss_kit_a5.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/gen_huge_a5.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/kitify_a5.py   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_art_sheet_20261009.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_art_sheet_20261009_1.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_art_sheet_20261009_2.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_art_sheet_20261009_3.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_art_sheet_20261009_4.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_v3_contact_20261010.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/rot_variants_20261009.png   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_Atlas.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_Bacta.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_EmpirePursuit.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_LongShade.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_LuminousPigment.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_NightsideIce.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_RimProperty.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_ShipShields.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_WasteRun.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_entry_Watchers.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_Atlas.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_Bacta.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_EmpirePursuit.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_LongShade.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_LuminousPigment.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_NightsideIce.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_RimProperty.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_ShipShields.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_WasteRun.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/s7_notes_Watchers.txt   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/selftest_fix2_20261010.md   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/selftest_triage_20261010.md   FOUNDRY — scratch/probe leftovers, not committed work
?? Transient/selftests_20261010.log   FOUNDRY — scratch/probe leftovers, not committed work
?? conversations/   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-bridge4-fulllist_20261009.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-bridge6_20261009.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-bridge7_20261009.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_20261009.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_20261009b.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_20261009d.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_biomes.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_green_min.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_green_min2.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_harness.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-acc_l1x.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-builds_biomes.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-flowworks.kept-20261002.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-flowworks.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-ishko.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-live_20261008.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-live_20261008b.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-messyconduit.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.before-tier-watchers_live.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.pre-ns-flowworks.20261002T070221.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T142015.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.pre-ns-flowworks.20261005T161529.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ModsConfig.pre-session.20261007T135600.xml   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ns_flowworks_backup.20261002T070221.json   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ns_flowworks_backup.20261005T142015.json   FOUNDRY — scratch/probe leftovers, not committed work
?? deployed/config/ns_flowworks_backup.20261005T161529.json   FOUNDRY — scratch/probe leftovers, not committed work
?? infrastructure/state/handoffs/FOUNDRY_HANDOFF_202610101109.md   FOUNDRY — scratch/probe leftovers, not committed work
?? infrastructure/state/items/ASHKARR_PAINTER_NAMES_DIVERGED_1.md   FOUNDRY — scratch/probe leftovers, not committed work
?? infrastructure/state/items/FALL_LINE_MAJOR_REGION_LABEL_1.md   FOUNDRY — scratch/probe leftovers, not committed work
?? infrastructure/state/items/TWILIGHT_ART_REUSE_ELSEWHERE_1.md   FOUNDRY — scratch/probe leftovers, not committed work
?? src/RimMandrake/FlowWorks/northstar/extension_result_20261008T212615.json   FOUNDRY — scratch/probe leftovers, not committed work
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261009T180159.json   FOUNDRY — scratch/probe leftovers, not committed work
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_aerial_live_20261009T180402.json   FOUNDRY — scratch/probe leftovers, not committed work
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261009T181630.json   FOUNDRY — scratch/probe leftovers, not committed work
?? src/RimMandrake/GimmeSomeSlack/northstar/validation_result_20261009T182325.json   FOUNDRY — scratch/probe leftovers, not committed work
```

