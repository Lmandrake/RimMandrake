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

A note of the fresh reader of e3dc3bb854e3 (run for RIMMANDRAKE_READ_FIX_E3DC3BB854_WITH_FRESH_EYES, 2026-11-27).

- `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWreckTools.cs` (tool `jawa/install_blueprint`): the refusal "held on another map" reads `mini.Spawned == false && mini.MapHeld != map`, so a carried form that lies on another map than the current one (a caravan still loading on the away map) is not refused. Drop the `Spawned == false` part. risk: `scene_caravan_wreck_home` reads "arrived" on its first loop while the wreck is still on the away map, then fails 30000 ticks later on a caravan that is still travelling.
