## spec
found-by: GPT review (BENCH, 2026-10-23, FlowWorks + GSS high-depth review). NOT YET VERIFIED.
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (section "Unverified findings"). Raw GPT replies: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\F_validation_suite_<n>.md`; finding table `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\findings.tsv`.

70 findings GPT raised against the validation suite (parts F3-F9) were not checked in the review session (coordinator ruled to stop verifying for cost). Each must be checked against the cited lines exactly as the confirmed ones were: CONFIRM and file its own item (`rimflow namecheck`, then `rimflow file ... --why "found by GPT review, verified"`), or REJECT with a one-line reason in GPT_REVIEW.md. Severity below is GPT's, not ours.

## verify
Every id below carries a CONFIRMED/REJECTED verdict and confirmed ones have items; then close this.

## findings

| id | GPT sev | where | title |
|---|---|---|---|
| FF_validation_suite_3.1 | MAJOR | `src/RimMandrake/FlowWorks/northstar/live_session.py:428-430`, `1373-1393`, `1920-1935` (`Session.advance`, `g_dehydration_ride`, `feed_colonists`) | Session feeding invalidates the dehydration measurement |
| FF_validation_suite_3.2 | MAJOR | `src/RimMandrake/FlowWorks/northstar/live_session.py:1660-1661`, `1683-1688` (`b6_flood`); also `1572-1603` (`b5_cold_snap`) | Failed terrain reads can prove that flooding or ice disappeared |
| FF_validation_suite_3.3 | MAJOR | `src/RimMandrake/FlowWorks/northstar/player_missions.py:787-788`, `824-837` (`goal_check`, chain branch) | A truncated pawn census can pass the “unhurt” mission |
| FF_validation_suite_3.4 | MAJOR | `src/RimMandrake/FlowWorks/northstar/player_missions.py:583-626`, `923-931` (`cmd_observe`, `cmd_report`) | Mission reports enforce the tick deadline but omit wall and action limits |
| FF_validation_suite_3.5 | MAJOR | `src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py:692-711` (`p_e6`) | Trial preflight can accept an old loaded image after replacing its DLL |
| FF_validation_suite_3.6 | MAJOR | `src/RimMandrake/FlowWorks/northstar/pipe_levelling_perf_proof.py:261-266`, `321-330` (`main.go`, `_rigs_and_time`) | Perf certification ignores refused basin fills and actual movement |
| FF_validation_suite_3.7 | MAJOR | `src/RimMandrake/FlowWorks/northstar/owner_review_stage.py:130-136`, `731` (`layout`, `main`) | Default owner-review stations extend beyond a 250-cell map |
| FF_validation_suite_3.8 | MAJOR | `src/RimMandrake/FlowWorks/northstar/live_session.py:1126-1134`, `1796-1805` (`g_pit_access`, `rescue_verdict`) | Session rescue failure is attributed to the mod without checking for a bed |
| FF_validation_suite_3.9 | MINOR | `src/RimMandrake/FlowWorks/northstar/live_session.py:2125-2147` (`run_sub`, `verdicts`); `src/RimMandrake/FlowWorks/northstar/raid_trench_proof.py:460` | The raid’s descriptive row prevents an all-green raid verdict |
| FF_validation_suite_3.10 | MAJOR | `src/RimMandrake/FlowWorks/northstar/raid_trench_proof.py:467-478`, `527-533` (`_run`) | Legal crossings on colony ladders fail the mask-swap assertion |
| FF_validation_suite_3.11 | MINOR | `src/RimMandrake/FlowWorks/northstar/live_session.py:806-819` (`b2_settings_dialog`) | Settings round-trip fails when guardrails were already disabled |
| FF_validation_suite_3.12 | MINOR | `src/RimMandrake/FlowWorks/northstar/reach_map_proof.py:399-402` (`main`) | Reach proof exits successfully with requested checks unmeasured |
| FF_validation_suite_3.13 | MINOR | `src/RimMandrake/FlowWorks/northstar/prep_site.py:314-322` (`prep`); `src/RimMandrake/FlowWorks/northstar/preflight_flowworks.py:478-482`, `495-498` | Golden-site preparation accepts settings that its own preflight rejects |
| FF_validation_suite_4.1 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios_map.py:1385–1388` (`main`) | Rebuilding map C can modify the currently selected river map |
| FF_validation_suite_4.2 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios_map.py:1090–1095` (`river_main`); `:955–958` (`use_map`) | Rebuilding the river map discards the saved map-C identity |
| FF_validation_suite_4.3 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios/stage0_swim_pit.py:81–103` (`run`) | A failed dry control can still produce a successful swim-escape verdict |
| FF_validation_suite_4.4 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios_map.py:575–581`, `:1391–1428` (`after_soak`, `main`) | CLI success and saving do not consistently reflect validation failures |
| FF_validation_suite_4.5 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios_map.py:674–726` (`snapshot`, `verify_plots`, `soak`) | Plot verification discards liquid identity and exact water volume |
| FF_validation_suite_4.6 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios/c10_rain_basin.py:42–46`, `:64–65` (`SETUP`, `SCENARIO.try_`) | C10’s closed-ledger Start cannot initiate tank transfer |
| FF_validation_suite_4.7 | MAJOR | `src/RimMandrake/FlowWorks/northstar/scenarios/c05_fuel_depot.py:15–16`, `:68`, `:79` | C5’s single-cell no-mix poke does not connect the canals |
| FF_validation_suite_4.8 | MINOR | `src/RimMandrake/FlowWorks/northstar/selftest_conservation_roundtrip.py:214–220`, `:402–408` (`Body`, trip 8) | The conservation model still asserts the retired whole-notch pumping restriction |
| FF_validation_suite_5.1 | MAJOR | src/RimMandrake/FlowWorks/northstar/settings_registry.py:34–36 (`build`), :65–67 (`all_off`); src/RimMandrake/FlowWorks/northstar/site_spec.py (`SETTINGS`) | The “every setting” registry omits shipped settings sections |
| FF_validation_suite_5.2 | MAJOR | src/RimMandrake/FlowWorks/northstar/thirst_live.py:405 (`wet_cells`) | Thirst isolation silently excludes part of larger maps |
| FF_validation_suite_5.3 | MAJOR | src/RimMandrake/FlowWorks/northstar/thirst_live.py:418–420 (`dry_cells`) | A refused drying readback is accepted as successful isolation |
| FF_validation_suite_5.4 | MAJOR | src/RimMandrake/FlowWorks/northstar/station_reach_live.py:105–108 (`moved`) | The negative station-reach row can PASS without a usable test rig |
| FF_validation_suite_5.5 | MAJOR | src/RimMandrake/FlowWorks/northstar/suspension_settings_live.py:159–164 (`main`, weight arm) | Suspension settings-off can PASS when no ticks ran |
| FF_validation_suite_5.6 | MAJOR | src/RimMandrake/FlowWorks/northstar/sitting_gaps_proof.py:982 (`scene_s3`) | Missing hose drawing data becomes a clean S3 path |
| FF_validation_suite_5.7 | MAJOR | src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py:586 (`waters`, `WAT_river`) | River bridge crossing can PASS when the walker goes around it |
| FF_validation_suite_5.8 | MAJOR | src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py:364–368 (`main`, switch preflight) | Failed overflow-switch preflight bypasses settings restoration |
| FF_validation_suite_5.9 | MAJOR | src/RimMandrake/FlowWorks/northstar/sweep_identity_proof.py:127 (`main`) | Sweep identity failures still produce a successful process exit |
| FF_validation_suite_5.10 | MINOR | src/RimMandrake/FlowWorks/northstar/thirst_live.py:1212–1215 (`main`, T20 pour arm) | A refused bucket-pour order is scored as a mod defect |
| FF_validation_suite_5.11 | MINOR | src/RimMandrake/FlowWorks/northstar/sprinkler_live.py:417–419 (`main`, effects arm) | The chemfuel sprinkler arm restores effects OFF before testing them |
| FF_validation_suite_6.1 | MAJOR | src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:233 (`main`) | Wet-cost failures still return a successful process exit |
| FF_validation_suite_6.2 | MAJOR | src/RimMandrake/FlowWorks/northstar/validation_v2.py:2077–2080 (`Live.pulses`) | The exact-water differential comparison discards fractional water |
| FF_validation_suite_6.3 | MAJOR | src/RimMandrake/FlowWorks/northstar/trench_crossing_live.py:140–148 (`main`, one-ladder control) | A missing end position passes the one-ladder crossing control |
| FF_validation_suite_6.4 | MAJOR | src/RimMandrake/FlowWorks/northstar/underpass_raid_live.py:118–121 (`main`, sampling loop) | The underpass proof cannot distinguish walking beneath the bridge from walking on it |
| FF_validation_suite_6.5 | MAJOR | src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py:202–207 (`thrown_verdict`) | Ordinary pit exposure satisfies the thrown-person fall control |
| FF_validation_suite_6.6 | MAJOR | src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py:1393–1401, 1470, 1488 (`_s6_snap`, `run_S6`) | Save/load equality can pass when compared cells are unread |
| FF_validation_suite_6.7 | MAJOR | src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py:909–917 (`run_S3`, `S3.c`) | The pump conservation audit can pass using only its baseline sample |
| FF_validation_suite_6.8 | MAJOR | src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:215–221 (`main`, drowning-warning loop) | Another pawn’s drowning warning can pass the downed-pawn proof |
| FF_validation_suite_6.9 | MINOR | src/RimMandrake/FlowWorks/northstar/wet_costs_live.py:229 (`main`, `finally`) | Wet-cost cleanup enables the storyteller instead of restoring its previous state |
| FF_validation_suite_7.1 | MAJOR | `src/RimMandrake/FlowWorks/validation.py:289–299` (`latest_hose_result`) | Hose results can certify an undeployed DLL |
| FF_validation_suite_7.2 | MAJOR | `src/RimMandrake/FlowWorks/validation.py:352–353` (`_selftest_cases`) | Windows validation launches a WSL-only selftest runner |
| FF_validation_suite_7.3 | MAJOR | `src/RimMandrake/FlowWorks/review_map.py:1743–1745` (`Review.verify_gallery`) | One surviving building satisfies every requested copy |
| FF_validation_suite_7.4 | MAJOR | `src/RimMandrake/FlowWorks/review_map_rivers.py:267–274` (`build`); `src/RimMandrake/FlowWorks/review_map.py:1974–1980` (`rivers_main`) | River builds succeed when the current and ford stations were never verified |
| FF_validation_suite_7.5 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:1642–1651,1677–1678` (`gizmo_cycle`, `stage`) | Raised-ladder staging still assumes the button changes state immediately |
| FF_validation_suite_7.6 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:1612–1632` (`Review.late_hoses`) | The supposedly half-filled hose finishes filling before the map freezes |
| FF_validation_suite_7.7 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:1364,1410,2055–2065` (`calm`, `clear`, `main`) | Partial rebuilds delete animals and prisoners from the untouched gallery |
| FF_validation_suite_7.8 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:869–877` (`SETUPS["carry_kits"]`) | The reaction-vat demonstration has no liquid connection |
| FF_validation_suite_7.9 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:335–336,345–347,561–563` (`fire_lights`, `fire_out`, `look_fire`) | Three fire demonstrations mark ignition cells outside ignition reach |
| FF_validation_suite_7.10 | MINOR | `src/RimMandrake/FlowWorks/validation.py:967,1013` (`_driver_live_report`, `THIRST_LIVE`) | The thirst baseline falsely claims heat-scaling toggle coverage |
| FF_validation_suite_7.11 | MINOR | `src/RimMandrake/FlowWorks/selftest_hose_port.py:126–128` (`p9_credit_sites`) | Credit-site guard checking accepts an unconditional credit |
| FF_validation_suite_7.12 | MINOR | `src/RimMandrake/FlowWorks/review_map.py:1299–1301` (`visual_verdict`); `verify_visuals` | Visual verification cannot distinguish tar from water |
| FF_validation_suite_8.1 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar_matrix/design_spec.py: `hose_spec`, +35–40; src/RimMandrake/GimmeSomeSlack/northstar_matrix/fakegame.py: hose constants | Hose matrix expectations reject the current production widths |
| FF_validation_suite_8.2 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py: `Proof.save_load`, +16, +58, +73–88 | SL3 omits the main floor-cord save/load comparison |
| FF_validation_suite_8.3 | MAJOR | src/RimMandrake/FlowWorks/validation_hose.py: `run_carry`, +81–87 and CR5 verdict | Forced fallback can falsely certify unforced hose resumption |
| FF_validation_suite_8.4 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py: `Proof.determinism`, +8–10; src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py: `run`, D2 verdic | A failed fresh-builder probe can PASS D2 |
| FF_validation_suite_8.5 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py: `Run.scene`, +76–83 | Recorded scene construction failures do not prevent PASS |
| FF_validation_suite_8.6 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py: `main`, final return | Standalone matrix exits successfully after failed checks |
| FF_validation_suite_8.7 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py: `load_catalog`, +21–24 | The complement matrix silently drops its aerial and hose factors |
| FF_validation_suite_8.8 | MAJOR | src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py: `Run._shot`, +38; `post`, +11 | Later runs overwrite screenshots referenced by earlier results |
| FF_validation_suite_8.9 | MINOR | src/RimMandrake/GimmeSomeSlack/pole_shots.py: `main`, +5–9; src/RimMandrake/GimmeSomeSlack/human_review.py: `stations_style` | Pole capture loop does not change explicitly stored looks |
| FF_validation_suite_9.1 | MAJOR | `src/RimMandrake/GimmeSomeSlack/validation_style.py`:315–327, 686–697 (`run_live`, `s9_after_load`) | Style save/load compares against a snapshot taken before later fixtures were added |
| FF_validation_suite_9.2 | MAJOR | `src/RimMandrake/GimmeSomeSlack/validation.py`:1646–1655 (`run_removal_check`) | Removal check ignores the Player.log evidence it collects |
| FF_validation_suite_9.3 | MAJOR | `src/RimMandrake/GimmeSomeSlack/validation.py`:880–890 (`live_battery`, `M5_local_invalidation`) | Local invalidation can pass without updating the edited run |
| FF_validation_suite_9.4 | MAJOR | `src/RimMandrake/GimmeSomeSlack/validation_aerial.py`:945–952, 966–978, 986–1003, 1177 (`theft_day`, `theft_stop`, `run_theft`, `main`) | An unfinished theft phase can exit successfully without its verdict |
| FF_validation_suite_9.5 | MINOR | `src/RimMandrake/GimmeSomeSlack/validation_aerial.py`:466–470 (`M19m_tap_mixed_net_connects_own_conduit`) | Mixed-faction tap proof does not require a mixed-faction net |
| FF_validation_suite_9.6 | MINOR | `src/RimMandrake/Utils/mockups/messy_conduit/make_hose_binding.py`:26, 56–63 (`H`, `bare`) | Hose-art generator still targets the retired GSS asset location |
| FF_validation_suite_9.7 | MINOR | `src/RimMandrake/Utils/selftest_gimmesomeslack.py`:47 (`main`) | Core selftest requires an unrelated hard-coded checkout directory |
| FF_validation_suite_9.8 | MINOR | `src/RimMandrake/GimmeSomeSlack/validation.py`:1074–1117, 1810–1816 (`lane_a_live`, `live_battery_chain`) | Remote spark fixture escapes suite cleanup after an abort |
