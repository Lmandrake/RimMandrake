A selftest that runs a committed scene script with the fake world must set scene_verdicts.REPO to its temp folder: the script's own scene.judge call appends run lines to design/concepts/<Mod>/version/scene_runs.jsonl of the real clone. selftest_scene_conversion.py left 2 fake SUCCESS lines (build aaaa...) in FlowWorks' file on every run until 2026-11-25; a later real run appends to that untracked file and a commit carries the fakes.
item: RIMMANDRAKE_BUILD_MUTANTS_BY_OVERLAY_AUTHOR_DOES_NOT_CHOOSE
home: design/specs/2026-11-23-scene-library/boundary.md
