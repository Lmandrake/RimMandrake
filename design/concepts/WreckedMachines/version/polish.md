# Wrecked Machines polish list

Wording notes from the Cold Reader exam of 2026-11-27 (run rm-role-designer-1795777120). No Reader gave a wrong verdict
on any of them. Each line names `design/concepts/WreckedMachines/tree.json`, which that run did not change. The next run
that changes the tree takes the lines, and then takes the exam again by `exam_retake.py plan`.

- `design/concepts/WreckedMachines/tree.json` (bar `only_by_repair`, `range.varies`): the words "(17 when Vanilla Cooking Expanded is not loaded; the fish farm's def loads with Odyssey)" do not say which machine Vanilla Cooking Expanded brings. Both Readers and the control Reader stopped at them. Name the cannery there.
- `design/concepts/WreckedMachines/tree.json` (rule `R_kludged_move`): "As built:" can be read as the mod on disk today and not as the design. Three Readers stopped at it. Say that the smelter's onboarding table of 0.1.0 holds these values.
- `design/concepts/WreckedMachines/tree.json` (bar `only_by_repair`, `meant.figurative` "nothing in the world"): the list names map loot, a quest reward and a trader's stock. It does not speak of a scenario's starting items, or of a trader that sells a Wrecked machine. The Examiner and the Challenger each named one of the two. One sentence settles both.
- `design/concepts/WreckedMachines/tree.json` (bar `switch_gives_machine_back`): with a machine's line off, wrecks and repaired levels of that machine "stay as they are". The bar does not say whether such a wreck can still be studied and repaired. The Challenger named it.
- `design/concepts/WreckedMachines/tree.json` (bar `no_setting_named`, `range`, and rule `R_riders`): the bar reads the text of the distillation machine's patch, and the rule says that no bar judges what the distillation machine does. Say in the rule that its text is still read by `no_setting_named`. The Examiner named it.

A note of the stage-5 coverage judge rm-coverage-judge-1795778084 (2026-11-27), which it rated polish and did not repair.
Run rm-role-designer-1795780944 did not change `scenes.json`. The next run that changes `scenes.json` takes the line.

- `design/concepts/WreckedMachines/scenes.json` (scene `sc_levels_under_settings`): the range of bar `switch_gives_machine_back` names "the costs" at their lowest and highest values, and no scene moves a cost setting. Add an arm that sets each cost setting (repair cost, study length) to its lowest and its highest value, reads the applied repair cost or study length, and puts it back. risk: a cost slider that changes nothing passes every scene.

Notes of the art judges of 2026-11-27 on the last five machines (run on
RIMMANDRAKE_AUTOBUILD_WRECKEDMACHINES_SEVEN_BARS_LEFT_RUN_TWO). Each judge kept every picture and wrote these as proposals
that refuse nothing. Each needs a new drawing and a new judgement, so each stays here with its risk.

- `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Mobile/PsychicEmanator/Wrecked/PsychicEmanator.png`: its colour is close to tan ground. risk: at his walk on sand the wrecked emanator reads slowly when zoomed out; slightly darker plates would fix it.
- `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Factories/Autofarmer/Wrecked/`: low contrast at 18 px per cell. risk: zoomed far out, the wrecked autofarmer's parts merge into one brown shape.
- `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Factories/Autofarmer/Kludged/Autofarmer_east.png`: four strapped-on boxes where the other facings have one. risk: a player who turns the machine sees the bodge change between facings.
- `src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Factories/AutomatedFishfarm/Kludged/`: the chute's arrow mark is white on east and yellow on west. risk: the same change between facings.
- `src/RimMandrake/WreckedMachines/Source/judge_packet.py`: the packet makes true-scale strips for the south and east facings only, so a machine with north and east files (the power cell) gets one strip, and the sibling sheet has no donor column. The run did not change this file.
