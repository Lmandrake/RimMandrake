# RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE

## spec
Owner, 2026-11-17, on the proposed Pyrelands polish entry `RIMMANDRAKE_RESTORE_PYRE_WIND_SCENE_GROUND` (deleted, never
filed): *"This is dumb. It's not even an item at all. Just save the test in a file and reload... We shouldn't be judging
Test Reset as a mod deliverable."* Standing ruling: `design/RimMandrake/standing_rulings.md` § "Resetting a test scene is
harness housekeeping, never a mod deliverable".

Build the harness half: any mod's live scene runner saves the game to a unique file before the scene changes anything,
and reloads that file after the scene, on a normal exit and when the scene raises. No mod's scene code cleans up by hand.

- The pattern already exists for one mod: `src/RimMandrake/HugeThings/northstar/showcase_common.py::LiveSite`
  (begin: save a unique scene-begin snapshot and reload it; restore: reload the snapshot), built on
  `src/RimMandrake/Utils/modcheck/test_site_saves.py::save_site` / `load_site`. Lift it into one shared helper,
  `src/RimMandrake/Utils/modcheck/scene_snapshot.py` (a context manager `scene_snapshot(call, prefix)`), and make
  `LiveSite` use it rather than keep a second copy.
- First user: `src/RimMandrake/Pyrelands/wind_burn_live.py` (today it neither saves nor reloads: grep finds no
  `save_site`, `load_site` or `save_game` in it, measured 2026-11-17).
- Then `designer_stage.py scene-begin` may default `--recovery` to "reload the pre-scene save <name>" when the runner
  used the helper; the `restore` line in `scenes.json` stays (runner recovery record, never judged).
- Not in scope: no judge, gate or criterion change (the ruling already removed reset from judging, coverage_judge
  recalibrated 9/9 on 2026-11-17); no live test of a flyer's flight; no worldgen.

## criteria
- A selftest (`src/RimMandrake/Utils/modcheck/selftest_scene_snapshot.py`) with a fake `call` that records every
  bridge call proves: the save happens before the body's first call; the reload happens after the body, also when the
  body raises; two scenes get different save names; a failed reload is reported as an error, never swallowed. It is
  watched failing once against a helper that skips the reload on raise.
- `wind_burn_live.py` and `showcase_common.LiveSite` both run through `scene_snapshot`.
- Acceptance command (exit 0 passes): `python3 -c "import os,sys; p='src/RimMandrake/Utils/modcheck/scene_snapshot.py'; w=open('src/RimMandrake/Pyrelands/wind_burn_live.py').read(); sys.exit(0 if os.path.isfile(p) and 'scene_snapshot' in w else 1)"`
  **watched it fail** (exit 1) on 8dba1b6a25, 2026-11-17. Coarse (presence, not behaviour): the selftest above is the
  behaviour check.

## verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_scene_snapshot` passes, printing its case count.
- Live (needs game-up, owner's list or minimal): one `wind_burn_live.py` run whose evidence shows the snapshot name,
  the reload's `verified: true`, and the burn scar absent on the reloaded map.

Evidence of the judge change: `D:\ClaudeWork\rimmandrake\evidence\test_reset_ruling\` (the old brief refused
`good_lanterns_no_reset` on "has no restoration": `old_noreset2.txt`; the new brief 9/9: `cal_new.txt`).

## refs
- file: design/RimMandrake/standing_rulings.md
- file: src/RimMandrake/rimflow/roles/designer_scene_contract.md
- file: src/RimMandrake/HugeThings/northstar/showcase_common.py
- file: src/RimMandrake/Utils/modcheck/test_site_saves.py
- file: src/RimMandrake/Pyrelands/wind_burn_live.py
- new: src/RimMandrake/Utils/modcheck/scene_snapshot.py
- new: src/RimMandrake/Utils/modcheck/selftest_scene_snapshot.py
