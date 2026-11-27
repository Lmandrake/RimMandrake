# WreckedMachines 0.1.0 test table (read view of test_table.json)

Made by `pilot_throwaway/make_test_table.py`, 2026-11-27T06:22:45-0800. A bar passes when every deciding test passes; a support adds evidence and decides nothing.

## How a pair is made

- R1 decides: each scene that the coverage judge names for the bar with ok true, in either round: the full round (rm-coverage-judge-1795778084, coverage_verdict.json at git 89b10e6f1a) and the signed delta round that closed its seven gaps (coverage_verdict.json at the lock). The delta round's checklist holds only what it read again
- R2 decides: each acceptance scene whose `requirement` in scenes.json names the bar
- R3 decides: each name in a coverage_rest `by` list for the bar: a scene decides; a leaf brings that leaf's deciders
- R4 an exploration scene accepts no bar (scenes.json: its `question` only): where R1 or R3 names one, the offline test that its question names by check id (C_...) decides in its place, and the exploration scene is a support
- R5 decides: T_ONBOARDED_SET and T_ONBOARDING_COMPLETE for each bar that a scene decides whose kind_note counts a machine only 'once its onboarding has landed' or 'once its machine's art is in' (the coverage judge's reason for its repair g3: those two checks fix the full list of machines, so the note cannot let a missing machine pass)
- R6 decides: the offline test of a check that a coverage_rest `why` names for the bar
- R7 decides: T_LATER_STAYS_OUT for an inventory bar whose scope is `later` and that no scene decides (delegated call, after Pyrelands' T_CUT_STAYS_CUT: the version's reading of such a bar is that 0.1.0 does not ship it half-built)
- R8 supports: the offline test of a check that the bar's leaf text, or a meeting whose members hold the bar, names; a showcase scene that exercises the bar; an interaction scene whose `features` name the bar; a built offline test whose file names the bar id or one of its deciding scenes
- R9 supports: LOOK_STAGE8 for a bar with a deciding scene that holds for his review (`hold: owner_review`)
- R10 supports, written by the steward with its ground (STEWARD_SUPPORTS): a check of the tree that no other rule pairs supports the bar whose locked text reads the same thing. A support decides nothing, so no bar moves

## Counts

- bars: 30 (locked: 30)
- tests: 48 (10 built offline, 26 live scenes with their entry written, 7 specified for Stage 3, 4 explorations, 1 look)
- built offline tests green today: 10, red: 0 (none)
- live scenes whose tier is not defined: none
- bars with every decider runnable today: 23 of 30
- bars with no deciding test: 0

## Bars

| bar | kind | proves at | decides | supports | runnable today | waits on |
|---|---|---|---|---|---|---|
| inv_grade_ladder | inventory, approved | 6 | sc_repair_on_machine, sc_levels_under_settings, sc_component_gate | sc_ruin_holds_wrecks, sc_carry_wreck_home, sc_study_opens_first_project, sc_whole_journey, T_KERNEL_FUZZ | yes | - |
| inv_smelter_line | inventory, approved | 6 | sc_levels_do_their_work, sc_menu_and_research, sc_three_looks_rows, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | sc_ruin_holds_wrecks, sc_carry_wreck_home, sc_study_opens_first_project, sc_repair_on_machine, sc_component_gate, sc_whole_journey, LOOK_STAGE8 | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| inv_power_cell_line | inventory, approved | 6 | sc_cell_and_emanator, sc_levels_under_settings, sc_carry_wreck_home, sc_switch_machine_off | - | yes | - |
| inv_emanator_line | inventory, approved | 6 | sc_cell_and_emanator, sc_marks_agree, sc_carry_wreck_home, sc_no_handouts | sc_levels_under_settings, sc_switch_machine_off | yes | - |
| inv_study_the_wreck | inventory, approved | 6 | sc_study_opens_first_project, sc_second_study, sc_study_without_research_reinvented | sc_ruin_holds_wrecks, sc_carry_wreck_home, sc_repair_on_machine, sc_component_gate, sc_whole_journey | yes | - |
| inv_ancient_component | inventory, approved | 6 | sc_component_gate | sc_ruin_holds_wrecks, sc_carry_wreck_home, sc_study_opens_first_project, sc_repair_on_machine, sc_whole_journey | yes | - |
| inv_donor_smelter_hidden | inventory, approved | 6 | sc_menu_and_research, sc_switch_machine_off, sc_every_machine_onboarded, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | sc_three_looks_rows, sc_forge_plasteel | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| inv_mod_settings | inventory, approved | 6 | sc_switch_machine_off, sc_all_switches_off, sc_levels_under_settings, sc_ruin_holds_wrecks, sc_cannery_tier | sc_cell_and_emanator | yes | - |
| inv_wrecks_draw_links | inventory, approved | 4-5 | sc_wreck_link_tags | - | yes | - |
| inv_alloy_forge_gates | inventory, opened_by_owner | 6 | sc_forge_plasteel | sc_menu_and_research, sc_three_looks_rows, T_FORGE_GATES_GONE | yes | - |
| inv_one_salvage_rule | inventory, not_opened | 4-5 | T_SALVAGE_RULE | sc_rider_salvage_rule | yes | - |
| inv_distillation_module | inventory, opened_by_owner | 4-5 | T_DISTILLATION_LOADS, sc_text_names_no_setting | sc_rider_distillation | yes | - |
| inv_wreck_found_in_world | inventory, approved | 6 | sc_ruin_holds_wrecks, sc_rare_wreck_ordinary_map, sc_caravan_wreck_home | sc_carry_wreck_home, sc_study_opens_first_project, sc_repair_on_machine, sc_component_gate, sc_whole_journey | yes | - |
| inv_ancient_component_source | inventory, approved | 6 | sc_ruin_holds_wrecks, sc_no_handouts, sc_rare_wreck_ordinary_map | sc_carry_wreck_home, sc_study_opens_first_project, sc_repair_on_machine, sc_component_gate, sc_whole_journey | yes | - |
| inv_wealth_exclusion | inventory, later | 4-5 | T_LATER_STAYS_OUT | - | yes | - |
| inv_grade_changed_signal | inventory, approved | 6 | sc_repair_on_machine, T_REPAIR_STATE_WALK | - | yes | - |
| inv_turret_line | inventory, later | 4-5 | T_LATER_STAYS_OUT | - | yes | - |
| inv_more_factory_machines | inventory, approved | 6 | sc_menu_and_research, sc_three_looks_rows, sc_cannery_tier, sc_every_machine_onboarded, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | sc_forge_plasteel, LOOK_STAGE8 | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| only_by_repair | live | 6 | sc_menu_and_research, sc_no_handouts, sc_cannery_tier, sc_component_gate | sc_old_save | yes | - |
| wreck_is_found | live | 6 | sc_ruin_holds_wrecks, sc_rare_wreck_ordinary_map | T_REPAIR_STATE_WALK | yes | - |
| wreck_comes_home | live | 6 | sc_carry_wreck_home, sc_caravan_wreck_home | T_REPAIR_STATE_WALK, sc_uninstall_during_repair, sc_repair_needs_ground | yes | - |
| study_opens_research | live | 6 | sc_study_opens_first_project, sc_second_study, sc_whole_second_order, sc_study_without_research_reinvented, sc_every_machine_onboarded, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | T_REPAIR_STATE_WALK | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| repair_on_the_machine | live | 6 | sc_repair_on_machine, sc_repair_cancelled, sc_repair_needs_ground, sc_component_gate, sc_every_machine_onboarded, sc_cannery_tier, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | T_REPAIR_STATE_WALK, sc_uninstall_during_repair | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| levels_of_function | live | 6 | sc_levels_do_their_work, sc_forge_plasteel, sc_cell_and_emanator, sc_levels_under_settings, sc_every_machine_onboarded, sc_cannery_tier, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | T_LEVEL_NUMBERS, T_REPAIR_STATE_WALK, T_ONBOARDING_TABLE_OFFLINE, T_KERNEL_FUZZ | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| last_repair_needs_component | live | 6 | sc_component_gate, sc_ruin_holds_wrecks, sc_no_handouts | - | yes | - |
| levels_told_apart | live | 6 | sc_three_looks_rows, sc_marks_agree, sc_text_names_no_setting, T_ONBOARDED_SET, T_ONBOARDING_COMPLETE | T_REPAIR_STATE_WALK, LOOK_STAGE8 | no | T_ONBOARDED_SET, T_ONBOARDING_COMPLETE |
| switch_gives_machine_back | live | 6 | sc_switch_machine_off, sc_all_switches_off, sc_forge_plasteel | T_LEVEL_NUMBERS | yes | - |
| no_setting_named | offline | 4-5 | sc_text_names_no_setting | T_NEIGHBOUR_NAMES | yes | - |
| wrecks_join_lines | offline | 4-5 | sc_wreck_link_tags | - | yes | - |
| whole_journey | live | 6 | sc_whole_journey, sc_whole_second_order | T_REPAIR_STATE_WALK, LOOK_STAGE8 | yes | - |

## Tests

| test | kind | stage | file::entry | today |
|---|---|---|---|---|
| T_KERNEL_FUZZ | offline | 4-5 | src/RimMandrake/Utils/selftest_wreckedmachines_fuzz.py | PASS |
| T_SALVAGE_RULE | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_salvage_rule.py | PASS |
| T_ONBOARDED_SET | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_onboarded_set.py | specified, Stage 3 builds it |
| T_ONBOARDING_COMPLETE | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_onboarding_complete.py | specified, Stage 3 builds it |
| T_ONBOARDING_TABLE_OFFLINE | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_onboarding_table.py | specified, Stage 3 builds it |
| T_LEVEL_NUMBERS | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_level_numbers.py | specified, Stage 3 builds it |
| T_REPAIR_STATE_WALK | offline | 4-5 | src/RimMandrake/Utils/selftest_wreckedmachines_repair_walk.py | PASS |
| T_NEIGHBOUR_NAMES | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_neighbour_names.py | specified, Stage 3 builds it |
| T_FORGE_GATES_GONE | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_forge_gates_gone.py | specified, Stage 3 builds it |
| T_DISTILLATION_LOADS | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_distillation_loads.py | PASS |
| sc_old_save | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_old_save | specified, Stage 3 builds it |
| T_LINT_DEFS | offline | 4-5 | src/RimMandrake/Utils/lint_wreckedmachines_defs.py | PASS |
| T_LINT_PLANTS | offline | 4-5 | src/RimMandrake/Utils/selftest_wreckedmachines_lint.py | PASS |
| T_STATIC | offline | 4-5 | src/RimMandrake/WreckedMachines/validation.py | PASS |
| sc_menu_and_research | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_menu_and_research | entry written |
| sc_no_handouts | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_no_handouts | entry written |
| sc_ruin_holds_wrecks | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_ruin_holds_wrecks | entry written |
| sc_rare_wreck_ordinary_map | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_rare_wreck_ordinary_map | entry written |
| sc_carry_wreck_home | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_carry_wreck_home | entry written |
| sc_study_opens_first_project | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_study_opens_first_project | entry written |
| sc_second_study | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_second_study | entry written |
| sc_repair_on_machine | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_repair_on_machine | entry written |
| sc_repair_cancelled | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_repair_cancelled | entry written |
| sc_levels_do_their_work | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_levels_do_their_work | entry written |
| sc_levels_under_settings | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_levels_under_settings | entry written |
| sc_forge_plasteel | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_forge_plasteel | entry written |
| sc_cell_and_emanator | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_cell_and_emanator | entry written |
| sc_component_gate | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_component_gate | entry written |
| sc_three_looks_rows | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_three_looks_rows | entry written |
| sc_marks_agree | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_marks_agree | entry written |
| sc_switch_machine_off | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_switch_machine_off | entry written |
| sc_all_switches_off | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_all_switches_off | entry written |
| sc_text_names_no_setting | offline | 4-5 | src/RimMandrake/WreckedMachines/validation.py::scene_text_names_no_setting | PASS |
| sc_wreck_link_tags | offline | 4-5 | src/RimMandrake/FlowWorks/selftest_wrecked_links_draw_in.py::main | PASS |
| sc_whole_journey | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_whole_journey | entry written |
| sc_whole_second_order | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_whole_second_order | entry written |
| sc_uninstall_during_repair | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_uninstall_during_repair | entry written |
| sc_repair_needs_ground | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_repair_needs_ground | entry written |
| sc_study_without_research_reinvented | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_study_without_research_reinvented | entry written |
| sc_cannery_tier | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_cannery_tier | entry written |
| sc_every_machine_onboarded | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_every_machine_onboarded | entry written |
| sc_caravan_wreck_home | live_minimal | 6 | src/RimMandrake/WreckedMachines/validation.py::scene_caravan_wreck_home | entry written |
| sc_study_spike | exploration | 6 | - | an exploration accepts no bar (scenes.json); its question is read by a look in the running game |
| sc_first_look_built_mod | exploration | 6 | - | an exploration accepts no bar (scenes.json); its question is read by a look in the running game |
| sc_rider_salvage_rule | exploration | 4-5 | - | an exploration accepts no bar (scenes.json); its question is read by T_SALVAGE_RULE |
| sc_rider_distillation | exploration | 4-5 | - | an exploration accepts no bar (scenes.json); its question is read by T_DISTILLATION_LOADS |
| T_LATER_STAYS_OUT | offline | 4-5 | src/RimMandrake/WreckedMachines/selftest_wm_later_stays_out.py | PASS |
| LOOK_STAGE8 | look | 8 | - | Stage 8: the owner's own walk |

## The tree's checks

| check | test |
|---|---|
| C_kernel_fuzz | T_KERNEL_FUZZ |
| C_salvage_rule_offline | T_SALVAGE_RULE |
| C_onboarded_set | T_ONBOARDED_SET |
| C_onboarding_complete | T_ONBOARDING_COMPLETE |
| C_onboarding_table_offline | T_ONBOARDING_TABLE_OFFLINE |
| C_level_numbers | T_LEVEL_NUMBERS |
| C_repair_state_walk | T_REPAIR_STATE_WALK |
| C_neighbour_names | T_NEIGHBOUR_NAMES |
| C_forge_gates_gone | T_FORGE_GATES_GONE |
| C_distillation_loads | T_DISTILLATION_LOADS |
| C_old_save | sc_old_save |
| C_power_mark | sc_marks_agree (the scene's kind_note: 'this scene re-reads the fault of the first look (record contradiction c_bolt_on_powered_machine) and classes it') |

## Suites that decide and support no bar

- `src/RimMandrake/WreckedMachines/selftest_wm_scenes.py`: proof-harness completeness: each scene of validation.py has its asserted start, its control and no forbidden act after the start, on a fake game; not a mod behaviour
- `src/RimMandrake/bridgetools/selftest_wreck_reads.py`: the generic bridge reads that the scenes use (thing_set_sample, install_blueprint, study record, processor_fill, reach_edge, caravan reads), with planted faults; a test of the bridge, not of the mod
- `src/RimMandrake/WreckedMachines/prove_alloy_forge_offline.py`: the offline proof of the alloy forge's gates (--vfef <VFE Factory mod dir>): the gates leave the mod when the forge is onboarded (plan.md); its patch interpreter is what T_ONBOARDING_TABLE_OFFLINE is to reuse (tree check C_onboarding_table_offline)

## Held look statements

0 held look statements name this mod: a grep of design/RimMandrake/validation_holding/*.md for 'wreck|kludg|refurbish|smelter|vanometric|emanator|ancient component|alloy forge' finds 2 line(s) (design/RimMandrake/validation_holding/flowworks_walk_20261120.md:77, design/RimMandrake/validation_holding/flowworks_walk_20261120.md:164), and each is FlowWorks' ruined bridge (RM_SuspensionWreck), not a machine of this mod
