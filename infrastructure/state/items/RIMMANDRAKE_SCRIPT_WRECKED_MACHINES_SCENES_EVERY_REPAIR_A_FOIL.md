# RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL

Filed by the Designer at stage 3 of Wrecked Machines 0.1.0 (run `rm-role-designer-1795776308`, 2026-11-27). The name:
each scene of a repair has a control beside it (a foil) that must stay unrepaired, locked or refused.

## spec

Write the entry points that `design/concepts/WreckedMachines/scenes.json` names, in the mod's proof script
`src/RimMandrake/WreckedMachines/validation.py`. The design of each scene is its row in `scenes.json`: `start`, `action`,
`expect`, `control` and `restore`. The bar that each scene decides is in `design/concepts/WreckedMachines/tree.json`.

- 21 acceptance scenes and 2 interaction scenes have no entry point today. Every one of them names this item as
  `entry_point_item`. The scene `sc_wreck_link_tags` has its entry point already
  (`src/RimMandrake/FlowWorks/selftest_wrecked_links_draw_in.py`).
- Each entry point asserts its start state before it acts, and runs its control in the same pass.
- Four generic bridge functions are missing (census of 2026-11-27, `plan.md` under "order", step 2). Build each in the
  bridge's C#, test first, with no test and no scene of this mod in C#:
  - run a ThingSetMakerDef, or a TraderKindDef's stock, N times and list the defs that it produced;
  - place the install blueprint of a carried building;
  - read the game's study record for a kind of thing;
  - place the inputs of a factory process, only if `jawa/container_fill` does not reach the factory mod's processor.
- The scenes are built with the mod's build, in the order of `plan.md` ("order"): the spike `sc_study_spike` first, then
  the smelter's scenes, then placement, then the two carried machines, then the other factory machines, then the whole
  run.
- The existing ten settings rows of `validation.py` stay. Its three spawn-and-inspect scenes and its four UNMEASURED
  rows are replaced by the scenes of `scenes.json`. Its `alloy_forge_gated` scene ends when the forge is onboarded.
- A reset is the harness's job. A reset is not part of this item.

## acceptance test

A presence test, not a behaviour test. Seen red on `4f6c3feade` (2026-11-27, exit 1, `missing 23`); it passes with
`missing 0` and exit 0. The same command is the item's `--effect`.

    python3 -c "import json,sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import designer_stage as D; s=json.load(open('design/concepts/WreckedMachines/scenes.json')); m=[x['id'] for x in s['scenes'] if x.get('kind')!='exploration' and not D.entry_point_exists('.', x.get('entry_point'))]; print('missing', len(m), m); sys.exit(1 if m else 0)"

Input kinds that the test reads: an acceptance scene, an interaction scene, an exploration scene (not counted), an
entry point that is a function in a script, and an entry point that is a selftest file.

## verify

The behaviour of each scene has no offline oracle. At the mod's first in-game visit, the tester reads each scene
against its row in `scenes.json`: the start is asserted, the control ran, and the control can go red. Each run is
recorded with `maturation.py live-row`.

## criteria

- The acceptance test prints `missing 0`.
- Each of the four bridge functions has its own test, seen red first.
- No scene finishes research, finishes a study, sets a level or spawns a machine after its asserted start, except
  where its row in `scenes.json` says that the scene places the machine.
