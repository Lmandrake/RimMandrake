#!/usr/bin/env python3
"""boundary_check.py — every promise on a boundary page has a test of the same name.

Owner by card 2026-11-18 (`design/RimMandrake/standing_rulings.md` §A boundary page before pipeline code; design
`design/specs/2026-11-18-review-growth-cycle/01-design.md` §5.2). A page's `## PROMISES` and `## SURVIVES` sections list
entries `- **some-name.** ...`; each is owed a module-level test `t_some_name` (a def, or a name bound to one) in the
page's tests file, which that file's `main()` runs (names it, or the def it is bound to). `## DOES NOT SURVIVE`,
`## ACCEPTS` and `## LIFE CYCLES` entries are not promises.

  boundary_check.py <boundary.md> --tests <selftest.py>    one page
  boundary_check.py                                        every design/specs/*/boundary.md (what ./publish runs on a
                                                           change to one, pipeline_tests.json); each must be in PAGES

Exit 0: `promises covered N of N`. 1: a promise has no test, or one `main()` never runs (each named; `promises covered
N of M`). 3: UNREADABLE, the page or tests file could not be read or parsed, its `main()` is absent or a promised
test runs only with a runtime CLI option (`runtime_optional_test_counted`), its test selection is dynamic, or a page
is not in PAGES (cause named, no count printed). 4: NO PROMISES, the page lists none.
"""
import argparse
import ast
import glob
import os
import re
import sys

TOP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# page -> its tests file, repo-relative. A new boundary page is added here.
PAGES = {
    "design/specs/2026-11-24-flight-frames/boundary.md": "src/RimMandrake/Utils/selftest_flight_frames.py",
    "design/specs/scanguard/boundary.md": ".claude/hooks/selftest_block_blind_scan.py",
    "design/specs/2026-11-24-filing-gate/boundary.md": "src/RimMandrake/rimflow/selftest_filing_gate.py",
    "design/specs/2026-11-24-dispatcher-soon-timers/boundary.md": "src/RimMandrake/rimflow/selftest_seat_restart.py",
    "design/specs/2026-11-24-game-watch-tick/boundary.md": "src/RimMandrake/Utils/selftest_game_watch_tick.py",
    "design/specs/2026-11-24-fleet-now-stevedesktop/boundary.md": "src/RimMandrake/Utils/selftest_steve_reading.py",
    "design/specs/2026-11-24-monitors-consolidated/boundary.md": "src/RimMandrake/Utils/selftest_pages_index.py",
    "design/specs/2026-11-24-art-auto-judge/boundary.md": "src/RimMandrake/Utils/art_eval/selftest_auto_judge.py",
    "design/specs/2026-11-24-close-files-its-remainder/boundary.md":
        "src/RimMandrake/rimflow/selftest_close_remainder.py",
    "design/specs/2026-11-24-declaration-check/boundary.md": "src/RimMandrake/rimflow/selftest_declaration_check.py",
    "design/specs/2026-11-24-run-on-steve/boundary.md": "src/RimMandrake/rimflow/selftest_run_host.py",
    "design/specs/2026-11-25-effort-ladder/boundary.md": "src/RimMandrake/rimflow/selftest_effort_ladder.py",
    "design/specs/2026-11-24-full-list-walk-not-per-mod/boundary.md":
        "src/RimMandrake/rimflow/selftest_walk_small_list.py",
    "design/specs/2026-11-24-walk-save-start-twin/boundary.md": "src/RimMandrake/rimflow/selftest_walk_twins.py",
    "design/specs/2026-11-24-walk-pens/boundary.md": "src/RimMandrake/Utils/modcheck/selftest_walk_pens.py",
    "design/specs/2026-11-24-walk-owes-its-checks/boundary.md": "src/RimMandrake/rimflow/selftest_walk_owes_checks.py",
    "design/specs/2026-11-24-live-checks-in-builder-run/boundary.md": "src/RimMandrake/rimflow/selftest_live_checks_in_builder_run.py",
    "design/specs/2026-11-24-designer-mends-in-its-session/boundary.md":
        "src/RimMandrake/rimflow/selftest_designer_mend.py",
    "design/specs/2026-11-24-first-pass-calibration/boundary.md":
        "src/RimMandrake/rimflow/selftest_art_first_pass_calibration.py",
    "design/specs/2026-11-26-code-review-calibration/boundary.md":
        "src/RimMandrake/rimflow/selftest_code_review_calibration.py",
    "design/specs/2026-11-24-time-budgets/boundary.md": "src/RimMandrake/Utils/selftest_time_budget_lint.py",
    "design/specs/2026-11-24-progress-guard/boundary.md": "src/RimMandrake/Utils/selftest_progress_guard.py",
    "design/specs/2026-11-24-treecheck-slots/boundary.md": "src/RimMandrake/Utils/selftest_treecheck_slots.py",
    "design/specs/2026-11-25-treecheck-kept-tree/boundary.md": "src/RimMandrake/Utils/selftest_treecheck_kept.py",
    "design/specs/2026-11-24-quiet-scan/boundary.md": "src/RimMandrake/rimflow/selftest_quiet_scan.py",
    "design/specs/art-x-delete/boundary.md": "src/RimMandrake/Utils/art/selftest_art_x_ban_hardening.py",
    "design/specs/art-install-authority/boundary.md": "src/RimMandrake/Utils/art/selftest_art_install_authority.py",
    "design/specs/static-call-thing-id/boundary.md": "src/RimMandrake/Utils/selftest_static_call_args_core.py",
    "design/specs/2026-11-24-wrapup-game-debts/boundary.md": "src/RimMandrake/rimflow/selftest_wrapup_void_relaunch.py",
    "design/specs/2026-11-24-wrapup-game-release/boundary.md": "src/RimMandrake/rimflow/selftest_wrapup_restore_at_release.py",
    "design/specs/2026-11-23-launch-permissions/boundary.md": "src/RimMandrake/Utils/selftest_launch_permissions.py",
    "design/specs/2026-11-23-scene-library/boundary.md": "src/RimMandrake/Utils/selftest_scene_library.py",
    "design/specs/2026-11-23-scene-judge/boundary.md": "src/RimMandrake/rimflow/selftest_scene_judge.py",
    "design/specs/2026-11-24-scene-size/boundary.md": "src/RimMandrake/rimflow/selftest_scene_size.py",
    "design/specs/2026-11-24-owed-view-named-waits/boundary.md": "src/RimMandrake/rimflow/selftest_owed_view.py",
    "design/specs/2026-11-23-owed-sources-retired/boundary.md": "src/RimMandrake/rimflow/selftest_owed_sources.py",
    "design/specs/2026-11-23-canonical-save-guard/boundary.md": "src/RimMandrake/Utils/selftest_canonical_save_guard.py",
    "design/specs/2026-11-23-bridge-v2-hands/boundary.md": "src/RimMandrake/bridgetools/selftest_run_until.py",
    "design/specs/2026-11-24-bridge-order-waits/boundary.md": "src/RimMandrake/bridgetools/selftest_order_wait.py",
    "design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md": "src/RimMandrake/bridgetools/selftest_run_life_cycle.py",
    "design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md": "src/RimMandrake/bridgetools/selftest_test_hooks.py",
    "design/specs/2026-11-23-bridge-v2/boundary.md": "src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py",
    "design/specs/2026-11-24-play-vs-step/boundary.md": "src/RimMandrake/Utils/selftest_scene_compare.py",
    "design/specs/2026-11-23-bridge-v2-watcher/boundary.md": "src/RimMandrake/Utils/selftest_game_watcher.py",
    "design/specs/2026-11-23-deviation-record/boundary.md": "src/RimMandrake/bridgetools/selftest_deviation_record.py",
    "design/specs/2026-11-23-loaded-receipt/boundary.md": "src/RimMandrake/rimflow/selftest_loaded_receipt.py",
    "design/specs/2026-11-23-calm-map/boundary.md": "src/RimMandrake/Utils/selftest_calm_core.py",
    "design/specs/2026-11-23-first-exception-tap/boundary.md": "src/RimMandrake/Utils/selftest_first_exception_core.py",
    "design/specs/2026-11-23-stage-review-midday/boundary.md": "src/RimMandrake/Utils/selftest_stage_review.py",
    "design/specs/2026-11-23-gravship-layout-library/boundary.md": "src/RimMandrake/Utils/selftest_gravship_layout.py",
    "design/specs/2026-11-23-streamline-review-state/boundary.md": "src/RimMandrake/rimflow/selftest_close_gate.py",
    "design/specs/2026-11-23-close-check/boundary.md": "src/RimMandrake/rimflow/selftest_close_check.py",
    "design/specs/2026-11-23-guiding-prose-check/boundary.md": "src/RimMandrake/Utils/selftest_guiding_prose.py",
    "design/specs/2026-11-24-tick-children-own-cgroup/boundary.md": "src/RimMandrake/rimflow/selftest_own_cgroup.py",
    "design/specs/2026-11-23-tick-page-own-unit/boundary.md": "src/RimMandrake/rimflow/selftest_tick_page_own_unit.py",
    "design/specs/2026-11-23-wake-his-words/boundary.md": "src/RimMandrake/rimflow/selftest_wake_words.py",
    "design/specs/2026-11-23-wake-carries-result/boundary.md":
        "src/RimMandrake/rimflow/selftest_run_end_wake_result.py",
    "design/specs/2026-11-23-run-alive/boundary.md": "src/RimMandrake/rimflow/selftest_run_alive.py",
    "design/specs/2026-11-25-run-peek/boundary.md": "src/RimMandrake/rimflow/selftest_run_peek.py",
    "design/specs/2026-11-23-steve-two-games-lane/boundary.md": "src/RimMandrake/Utils/testq/selftest_testq_steve2.py",
    "design/specs/2026-11-24-lane-job-follows-companion/boundary.md":
        "src/RimMandrake/Utils/testq/selftest_companion_stage.py",
    "design/specs/2026-11-24-wait-lane-job/boundary.md": "src/RimMandrake/Utils/testq/selftest_testq.py",
    "design/specs/2026-11-24-ask-lane-after-host-facts/boundary.md": "src/RimMandrake/Utils/testq/selftest_ask_lane.py",
    "design/specs/2026-11-23-lane-stops-name-their-end/boundary.md": "src/RimMandrake/Utils/testq/selftest_lane_stop.py",
    "design/specs/2026-11-25-steve-idle-game-stop/boundary.md": "src/RimMandrake/Utils/testq/selftest_idle_stop.py",
    "design/specs/2026-11-23-lane-cause-once/boundary.md": "src/RimMandrake/Utils/testq/selftest_testq_steward.py",
    "design/specs/2026-11-24-stage-six-checks-to-steve/boundary.md": "src/RimMandrake/Utils/testq/selftest_stage6_checks.py",
    "design/specs/2026-11-22-steve-idle-takeable/boundary.md": "src/RimMandrake/Utils/selftest_steve_idle_takeable.py",
    "design/specs/2026-11-24-ingame-visit-owed/boundary.md": "src/RimMandrake/Utils/selftest_ingame_visit_owed.py",
    "design/specs/2026-11-23-list-dispatch/boundary.md": "src/RimMandrake/rimflow/selftest_list_dispatch.py",
    "design/specs/2026-11-24-work-bundles/boundary.md": "src/RimMandrake/rimflow/selftest_work_bundle.py",
    "design/specs/2026-11-25-temporary-work-bundle-monitor/boundary.md":
        "src/RimMandrake/rimflow/selftest_work_bundle_monitor.py",
    "design/specs/2026-11-24-record-readers/boundary.md": "src/RimMandrake/rimflow/selftest_record_readers.py",
    "design/specs/2026-11-23-list-stage-view/boundary.md": "src/RimMandrake/rimflow/selftest_list_pipeline.py",
    "design/specs/2026-11-23-owner-one-view/boundary.md": "src/RimMandrake/Utils/selftest_owner_one_view.py",
    "design/specs/2026-11-23-ticket-trend-graph/boundary.md": "src/RimMandrake/Utils/selftest_maturation_trend.py",
    "design/specs/2026-11-23-old-tickets-by-home/boundary.md": "src/RimMandrake/rimflow/selftest_list_home.py",
    "design/specs/2026-11-23-list-shape/boundary.md": "src/RimMandrake/rimflow/selftest_list_shape.py",
    "design/specs/2026-11-23-brief-commands/boundary.md": "src/RimMandrake/rimflow/selftest_brief_commands.py",
    "design/specs/2026-11-23-long-waits/boundary.md": "src/RimMandrake/Utils/selftest_waitalive.py",
    "design/specs/2026-11-23-item-packet/boundary.md": "src/RimMandrake/rimflow/selftest_item_packet.py",
    "design/specs/2026-11-22-list-outcome-checks/boundary.md": "src/RimMandrake/rimflow/selftest_list_effect.py",
    "design/specs/2026-11-24-live-line-host/boundary.md": "src/RimMandrake/rimflow/selftest_live_line_host.py",
    "design/specs/2026-11-23-follow-through-audit/boundary.md": "src/RimMandrake/Utils/selftest_follow_through.py",
    "design/specs/2026-11-24-art-daemon-over-the-one-door/boundary.md": "src/RimMandrake/Utils/artpipe/selftest_artpipe_signin.py",
    "design/specs/2026-11-22-clone-pool-disk-floor/boundary.md": "src/RimMandrake/Utils/selftest_pool_floor.py",
    "design/specs/2026-11-22-disk-sense-reads-only/boundary.md": "src/RimMandrake/Utils/selftest_disk_sense.py",
    "design/specs/2026-11-22-sense-families-cheap/boundary.md": "src/RimMandrake/Utils/selftest_ops_sense_blind.py",
    "design/specs/2026-11-23-sense-apart-from-beat/boundary.md": "src/RimMandrake/Utils/selftest_metronome_apart.py",
    "design/specs/2026-11-23-telemetry-any-game/boundary.md":
        "src/RimMandrake/Utils/telemetry/selftest_telemetry_games.py",
    "design/specs/2026-11-22-units-one-folder/boundary.md": "src/RimMandrake/Utils/selftest_units_one_folder.py",
    "design/specs/2026-11-25-weekly-crystallize-run/boundary.md": "src/RimMandrake/Utils/selftest_crystallize_weekly.py",
    "design/specs/2026-11-22-live-account/boundary.md": "src/RimMandrake/Utils/selftest_account_live.py",
    "design/specs/2026-11-22-login-deadline-forewarning/boundary.md": "src/RimMandrake/rimflow/selftest_login_deadline.py",
    "design/specs/2026-11-22-item-identity/boundary.md": "src/RimMandrake/rimflow/selftest_item_identity.py",
    "design/specs/2026-11-22-needs-conductor-list/boundary.md": "src/RimMandrake/Utils/selftest_needs_conductor.py",
    "design/specs/2026-11-22-non-mod-pipeline-section/boundary.md": "src/RimMandrake/Utils/selftest_maturation_nonmod.py",
    "design/specs/2026-11-22-selftest-deadline/boundary.md": "src/RimMandrake/Utils/selftest_selftest_deadline.py",
    "design/specs/2026-11-21-one-game-lock/boundary.md": "src/RimMandrake/rimflow/selftest_game_lock.py",
    "design/specs/2026-11-23-one-failure-classifier/boundary.md": "src/RimMandrake/rimflow/selftest_failure_class.py",
    "design/specs/2026-11-22-game-names/boundary.md": "src/RimMandrake/rimflow/selftest_game_names.py",
    "design/specs/2026-11-23-tick-names-steve-games/boundary.md": "src/RimMandrake/rimflow/selftest_tick_names_steve_games.py",
    "design/specs/2026-11-23-raid-tests-paused/boundary.md": "src/RimMandrake/rimflow/selftest_raid_pause.py",
    "design/specs/2026-11-23-live-kinds-exit-reader/boundary.md": "src/RimMandrake/rimflow/selftest_live_kinds.py",
    "design/specs/2026-11-23-scene-verdicts/boundary.md": "src/RimMandrake/rimflow/selftest_scene_verdicts.py",
    "design/specs/2026-11-21-rerun-only-related/boundary.md": "src/RimMandrake/rimflow/selftest_rerun_relation.py",
    "design/specs/2026-11-19-codebase-now/boundary.md": "src/RimMandrake/Utils/selftest_codebase_now.py",
    "design/specs/2026-11-19-standing-status-tabs/boundary.md": "src/RimMandrake/Utils/selftest_standing_tabs.py",
    "design/specs/2026-11-19-logon-tabs-shortcut/boundary.md": "src/RimMandrake/Utils/selftest_logon_shortcut.py",
    "design/specs/2026-11-19-judge-gates-and-designer-close/boundary.md": "src/RimMandrake/rimflow/selftest_judge_gates_designer_close.py",
    "design/specs/2026-11-19-exam-expect-verdict/boundary.md": "src/RimMandrake/rimflow/selftest_designer_stage.py",
    "design/specs/2026-11-23-helper-receipts-empty-markers/boundary.md": "src/RimMandrake/rimflow/selftest_helper_receipts.py",
    "design/specs/2026-11-18-pipeline-control-surface/boundary.md": "src/RimMandrake/rimflow/selftest_control.py",
    "design/specs/2026-11-19-probe-result/boundary.md": "src/RimMandrake/rimflow/selftest_probe_result.py",
    "design/specs/2026-11-19-stage-ceiling/boundary.md": "src/RimMandrake/rimflow/selftest_stage_ceiling_arrival.py",
    "design/specs/2026-11-22-art-sheet-prefill/boundary.md": "src/RimMandrake/Utils/art/selftest_prefill_keep_ts.py",
    "design/specs/2026-11-19-asks-on-empty-game/boundary.md": "src/RimMandrake/rimflow/selftest_asks_on_empty_game.py",
    "design/specs/2026-11-19-control-acts-export/boundary.md": "src/RimMandrake/rimflow/selftest_control_acts_export.py",
    "design/specs/2026-11-19-void-counters/boundary.md": "src/RimMandrake/rimflow/selftest_void_counters.py",
    "design/specs/2026-11-19-consumable-readers/boundary.md": "src/RimMandrake/rimflow/selftest_pipeline_control.py",
    "design/specs/2026-11-19-tick-pauses/boundary.md": "src/RimMandrake/rimflow/selftest_tick_pauses.py",
    "design/specs/2026-11-19-conductor-acts/boundary.md": "src/RimMandrake/rimflow/selftest_conductor_acts.py",
    "design/specs/2026-11-21-never-refuse-the-conductor/boundary.md":
        "src/RimMandrake/rimflow/selftest_never_refuse_conductor.py",
    "design/specs/2026-11-26-preflight-stops-at-pickup/boundary.md":
        "src/RimMandrake/rimflow/selftest_preflight_enforce.py",
    "design/specs/2026-11-19-pushover-critical-alerts/boundary.md": "src/RimMandrake/Utils/selftest_pager.py",
    "design/specs/2026-11-19-pushover-critical-alerts/triggers_boundary.md":
        "src/RimMandrake/Utils/selftest_pager_triggers.py",
    "design/specs/2026-11-19-incident-news-and-program-routes/boundary.md": "src/RimMandrake/rimflow/selftest_incident_news.py",
    "design/specs/2026-11-19-incident-clerk/boundary.md": "src/RimMandrake/rimflow/selftest_incident_clerk.py",
    "design/specs/2026-11-19-positive-steps-one-source/boundary.md": "src/RimMandrake/Utils/selftest_positive_steps_one_source.py",
    "design/specs/2026-11-19-rule-homes-in-briefs/boundary.md": "src/RimMandrake/rimflow/selftest_rule_homes_in_briefs.py",
    "design/specs/2026-11-19-brief-skill-paths/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-22-publish-door-judges-landing-tree/boundary.md":
        "src/RimMandrake/Utils/selftest_publish_tree_checks.py",
    "design/specs/2026-11-20-per-game-hold-own-install/boundary.md": "src/RimMandrake/rimflow/selftest_game_hold_split_install.py",
    "design/specs/2026-11-19-launch-unpublished-item/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-22-ledger-write-lands-its-shard/boundary.md": "src/RimMandrake/rimflow/selftest_ledger_landing.py",
    "design/specs/2026-11-21-launch-returns-a-kept-clone/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-22-launch-missing-clone/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-25-clone-lock-file-returned/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-25-park-item-given-to-mod/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-23-half-made-pool-clone/boundary.md": "src/RimMandrake/rimflow/selftest_take_clone_half_made.py",
    "design/specs/2026-11-23-brief-out-of-argv/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-23-resume-voided-blind-judge/boundary.md":
        "src/RimMandrake/rimflow/selftest_resume_voided_blind_judge.py",
    "design/specs/2026-11-20-detached-game-env/boundary.md": "src/RimMandrake/rimflow/selftest_detached_game_env.py",
    "design/specs/2026-11-20-reviewmap-game-saves/boundary.md": "src/RimMandrake/Utils/modcheck/selftest_reviewmap_game_saves.py",
    "design/specs/2026-11-19-launch-spend-cap/boundary.md": "src/RimMandrake/rimflow/selftest_detached_helper.py",
    "design/specs/2026-11-19-seat-restart-reads/boundary.md": "src/RimMandrake/rimflow/selftest_seat_restart_reads.py",
    "design/specs/2026-11-19-designer-stage-reads/boundary.md": "src/RimMandrake/rimflow/selftest_designer_stage_reads.py",
    "design/specs/2026-11-21-guiding-principles/boundary.md": "src/RimMandrake/rimflow/selftest_conversion_owed.py",
    "design/specs/2026-11-19-maturation-reads/boundary.md": "src/RimMandrake/rimflow/selftest_maturation_reads.py",
    "design/specs/2026-11-21-next-step-stage-moved/boundary.md": "src/RimMandrake/rimflow/selftest_next_step_stage_moved.py",
    "design/specs/2026-11-22-mod-next/boundary.md": "src/RimMandrake/rimflow/selftest_mod_next.py",
    "design/specs/2026-11-21-visit-wait-cited-items/boundary.md": "src/RimMandrake/rimflow/selftest_visit_wait_cited_items.py",
    "design/specs/2026-11-22-walk-result/boundary.md": "src/RimMandrake/rimflow/selftest_walk_result.py",
    "design/specs/2026-11-19-maturation-record/boundary.md": "src/RimMandrake/rimflow/selftest_maturation_record.py",
    "design/specs/2026-11-19-maturation-launch-twin/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_launch_twin.py",
    "design/specs/2026-11-19-maturation-tripwires/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_tripwires.py",
    "design/specs/2026-11-19-maturation-game-only-blind-exit/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_game_only_exit.py",
    "design/specs/2026-11-25-road-back-holds-stage-exit/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_road_back_hold.py",
    "design/specs/2026-11-20-tick-game-only-exit/boundary.md":
        "src/RimMandrake/rimflow/selftest_tick_game_only_exit.py",
    "design/specs/2026-11-24-game-deploy-own-unit/boundary.md":
        "src/RimMandrake/rimflow/selftest_game_deploy_unit.py",
    "design/specs/2026-11-20-launch-refusal-wait-and-deploy/boundary.md":
        "src/RimMandrake/rimflow/selftest_launch_wait_and_deploy.py",
    "design/specs/2026-11-24-brief-text-hash/boundary.md": "src/RimMandrake/rimflow/selftest_brief_text.py",
    "design/specs/2026-11-21-repair-at-the-refusal/boundary.md": "src/RimMandrake/rimflow/selftest_repair_at_refusal.py",
    "design/specs/2026-11-20-tick-names-never-refused/boundary.md":
        "src/RimMandrake/rimflow/selftest_tick_names.py",
    "design/specs/2026-11-20-tick-live-steward-and-card-brief/boundary.md":
        "src/RimMandrake/rimflow/selftest_tick_live_steward_card_brief.py",
    "design/specs/2026-11-20-wrong-check-fixed-in-sitting/boundary.md":
        "src/RimMandrake/rimflow/selftest_wrong_check_fixed_in_sitting.py",
    "design/specs/2026-11-20-red-seen-owner/boundary.md":
        "src/RimMandrake/rimflow/selftest_red_seen_owner.py",
    "design/specs/2026-11-23-stale-red-rerun-first/boundary.md":
        "src/RimMandrake/rimflow/selftest_stale_red_rerun_first.py",
    "design/specs/2026-11-23-one-live-run-per-mod/boundary.md":
        "src/RimMandrake/rimflow/selftest_one_live_run_per_mod.py",
    "design/specs/2026-11-20-road-back-holder-first/boundary.md":
        "src/RimMandrake/rimflow/selftest_road_back_holder_first.py",
    "design/specs/2026-11-25-tick-launches-road-back-hold/boundary.md":
        "src/RimMandrake/rimflow/selftest_dispatch_road_back_hold.py",
    "design/specs/2026-11-25-ledger-follows-version-bars/boundary.md":
        "src/RimMandrake/rimflow/selftest_modledger_version_bars.py",
    "design/specs/2026-11-20-coverage-judge-reads-only/boundary.md":
        "src/RimMandrake/rimflow/selftest_coverage_judge_reads_only.py",
    "design/specs/2026-11-19-coverage-signoff-and-slots/boundary.md": "src/RimMandrake/rimflow/selftest_coverage_signoff.py",
    "design/specs/2026-11-19-maturation-dispatch-reads/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_dispatch_reads.py",
    "design/specs/2026-11-20-maturation-pass-tag/boundary.md":
        "src/RimMandrake/rimflow/selftest_maturation_pass_tag.py",
    "design/specs/2026-11-19-card-capture-reads/boundary.md": "src/RimMandrake/rimflow/selftest_card_capture_reads.py",
    "design/specs/2026-11-25-card-reask-gate/boundary.md": ".claude/hooks/selftest_block_reasked_card.py",
    "design/specs/2026-11-19-failed-before-reads/boundary.md": "src/RimMandrake/rimflow/selftest_failed_before_reads.py",
    "design/specs/2026-11-19-mod-model-pin/boundary.md": "src/RimMandrake/rimflow/selftest_mod_model_pin.py",
    "design/specs/2026-11-22-run-spend-and-model-alias/boundary.md":
        "src/RimMandrake/rimflow/selftest_run_spend_and_model_alias.py",
    "design/specs/2026-11-19-closeout-matcher/boundary.md": "src/RimMandrake/rimflow/selftest_conductor_closeout.py",
    "design/specs/2026-11-19-role-clone-level/boundary.md": "src/RimMandrake/rimflow/selftest_role_clone_level.py",
    "design/specs/2026-11-19-run-end-continue/boundary.md": "src/RimMandrake/rimflow/selftest_left_open_continue.py",
    "design/specs/2026-11-21-live-sitting-context-burn/boundary.md": "src/RimMandrake/rimflow/selftest_continuation_progress.py",
    "design/specs/2026-11-20-account-drain/boundary.md": "src/RimMandrake/Utils/selftest_switching_plan_drain.py",
    "design/specs/2026-11-24-account-end/boundary.md": "src/RimMandrake/Utils/selftest_account_end.py",
    "design/specs/2026-11-19-card-brief-spend/boundary.md": "src/RimMandrake/rimflow/selftest_card_brief_spend.py",
    "design/specs/2026-11-20-owner-words-not-refused/boundary.md": "src/RimMandrake/rimflow/selftest_owner_words_not_refused.py",
    "design/specs/2026-11-19-one-fault-one-ticket/boundary.md": "src/RimMandrake/Utils/selftest_deadman_check.py",
    "design/specs/2026-11-19-card-stamp-fit/boundary.md": "src/RimMandrake/rimflow/selftest_card_capture.py",
    "design/specs/2026-11-19-run-return-reap/boundary.md": "src/RimMandrake/rimflow/selftest_detached_reap.py",
    "design/specs/2026-11-25-family-clean/boundary.md": "src/RimMandrake/Utils/selftest_family_clean.py",
    "design/specs/2026-11-19-vv-negative-control/boundary.md": "src/RimMandrake/Utils/selftest_vv_negative_control.py",
    "design/specs/2026-11-19-clean-means-promises-tested/boundary.md":
        "src/RimMandrake/Utils/selftest_code_review_page_state.py",
    "design/specs/2026-11-23-his-quotes-checked/boundary.md":
        "design/specs/2026-11-23-his-quotes-checked/selftest_his_quotes_checked.py",
    "design/specs/2026-11-21-northstar-run-exit-codes/boundary.md":
        "src/RimMandrake/Utils/northstar_driver/selftest_run_exit_codes.py",
    "design/specs/2026-11-24-account-plan-one-file/boundary.md": "src/RimMandrake/Utils/selftest_account_plan.py",
    "design/specs/2026-11-25-account-plan-sweep/boundary.md": "src/RimMandrake/Utils/selftest_account_plan_sweep.py",
    "design/specs/2026-11-24-live-gate-on-pipeline-host/boundary.md": "src/RimMandrake/rimflow/selftest_live_where_run.py",
    "design/specs/2026-11-25-deploy-shard-guard/boundary.md":
        "src/RimMandrake/rimflow/selftest_ledger_sparse_deploy.py",
    "design/specs/2026-11-25-deploy-installs-units/boundary.md":
        "src/RimMandrake/Utils/ops_core/selftest_deploy_installs_units.py",
    "design/specs/2026-11-25-polish-door/boundary.md": "src/RimMandrake/Utils/selftest_polish_door.py",
    "design/specs/2026-11-25-stevedesktop-work-vetted/boundary.md": "src/RimMandrake/rimflow/selftest_host_work_switch.py",
    "design/specs/2026-11-25-stevedesktop-work-vetted/testq/boundary.md":
        "src/RimMandrake/Utils/testq/selftest_testq_host_switch.py",
    "design/specs/2026-11-25-fixer-rule/boundary.md": "src/RimMandrake/rimflow/selftest_fixer_rule.py",
    "design/specs/2026-11-25-blind-readers-fix/boundary.md": "src/RimMandrake/rimflow/selftest_blind_readers_fix.py",
}
SECTIONS = ("PROMISES", "SURVIVES")
HEAD_RX = re.compile(r"^##\s+(\S+)")
ENTRY_RX = re.compile(r"^- \*\*(.+?)[.:]?\*\*")


class Unreadable(Exception):
    pass


def promises(page):
    """-> the page's promise and SURVIVES entry names, in order. Raises Unreadable."""
    try:
        with open(page, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable("%s: %s" % (page, e))
    out, cur, seen = [], None, False
    for ln in lines:
        h = HEAD_RX.match(ln)
        if h:
            cur = h.group(1).upper()
            seen = seen or cur == "PROMISES"
            continue
        m = ENTRY_RX.match(ln) if cur in SECTIONS else None
        if m:
            out.append(m.group(1).strip())
    if not seen:
        raise Unreadable("%s: no `## PROMISES` section, so it is not a boundary page this tool can read" % page)
    return out


def test_name(promise):
    return "t_" + re.sub(r"[^a-z0-9]+", "_", promise.lower().replace("'", "")).strip("_")


def _offline_names(main):
    """Names referenced by main() with no explicit CLI option, for direct flag guards."""
    argv = {arg.arg for arg in main.args.posonlyargs + main.args.args + main.args.kwonlyargs}
    parsed = {t.id for n in ast.walk(main) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "parse_args"
              for t in n.targets if isinstance(t, ast.Name)}

    def default(test):
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            value = default(test.operand)
            return None if value is None else not value
        if isinstance(test, ast.Attribute) and isinstance(test.value, ast.Name) and test.value.id in parsed:
            return False
        if isinstance(test, ast.Compare) and len(test.ops) == 1:
            parts = list(ast.walk(test))
            if (any(isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("--") for n in parts)
                    and any((isinstance(n, ast.Name) and n.id in argv) or
                            (isinstance(n, ast.Attribute) and n.attr == "argv") for n in parts)):
                if isinstance(test.ops[0], (ast.In, ast.Eq)):
                    return False
                if isinstance(test.ops[0], (ast.NotIn, ast.NotEq)):
                    return True
        return None

    def names(node):
        if isinstance(node, ast.Name):
            yield node.id
        if isinstance(node, ast.If):
            value = default(node.test)
            if value is not None:
                yield from names(node.test)
                for child in node.body if value else node.orelse:
                    yield from names(child)
                return
        for child in ast.iter_child_nodes(node):
            yield from names(child)

    return set(names(main))


def tests_in(path, promised=()):
    """-> (module-level names bound to a function: `def t_x` or `t_x = t_y`, the subset `main()` runs). Raises
    Unreadable when there is no `main()`, it picks its tests at run time, or a name in `promised` is CLI-only."""
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as e:
        raise Unreadable("%s: %s" % (path, e))
    defs = {n.name: n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Name) and n.value.id in defs:
            defs.update((t.id, defs[n.value.id]) for t in n.targets if isinstance(t, ast.Name))
    main = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    if not main:
        raise Unreadable("%s: no main(), so which tests it runs cannot be read" % path)
    used = {x.id for x in ast.walk(main[-1]) if isinstance(x, ast.Name)}
    dynamic = used & {"globals", "locals", "vars", "getattr"}
    if dynamic:
        raise Unreadable("%s: main() picks its tests at run time (%s), so which run cannot be read"
                         % (path, ", ".join(sorted(dynamic))))
    ran = {defs[u] for u in _offline_names(main[-1]) if u in defs}
    optional = {defs[u] for u in used if u in defs} - ran
    guarded = sorted(n for n in promised if defs.get(n) in optional)
    if guarded:
        raise Unreadable("%s: main() selects %s at run time through a CLI option" % (path, ", ".join(guarded)))
    return set(defs), {n for n, d in defs.items() if d in ran}


def check(page, tests):
    """-> exit code, printing the verdict for one page."""
    try:
        names = promises(page)
        have, run = tests_in(tests, map(test_name, names))
    except Unreadable as e:
        print("UNREADABLE %s" % e)
        return 3
    if not names:
        print("NO PROMISES on %s: its PROMISES section lists no `- **name.**` entry" % page)
        return 4
    missing = [p for p in names if test_name(p) not in run]
    for p in missing:
        print("FAIL promise %s: %s %s in %s" % (p, "main() never runs test" if test_name(p) in have else "no test",
                                                test_name(p), tests))
    print("promises covered %d of %d  (%s)" % (len(names) - len(missing), len(names), page))
    return 1 if missing else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("page", nargs="?")
    ap.add_argument("--tests")
    a = ap.parse_args(argv)
    if a.page and a.tests:
        return check(a.page, a.tests)
    if a.page or a.tests:
        ap.error("give both a page and --tests, or neither")
    rcs = [check(os.path.join(TOP, p), os.path.join(TOP, t)) for p, t in PAGES.items()]
    for p in sorted(glob.glob(os.path.join(TOP, "design", "specs", "*", "boundary.md"))):
        if os.path.relpath(p, TOP).replace(os.sep, "/") not in PAGES:
            print("UNREADABLE %s: no tests file registered for it in boundary_check.py PAGES" % p)
            rcs.append(3)
    return max(rcs)


if __name__ == "__main__":
    sys.exit(main())
