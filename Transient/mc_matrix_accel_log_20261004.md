# MC matrix accel log 2026-10-04

- start
- read run_live.py; design: phases accountant, --no-shots, --sweep-shots rebuilds boards (all boards share origin so scenes are destroyed per board), async PNG copy
- step1: imports, poll 0.05, phase accountant added
- step2: board() phases + sweep branch hooks (scene_shots TODO)
- step3: shot()/_shot async copy, frame(), scene_shots, merge_sweep, hose sweep
- step4: run()/main() flags + timing print; now docstring + post + tests
- step5: docstring + post note; running selftest
- step6: selftest 54/54, mock clean; committing
- coordinator: no-shots wrong live; investigating C# for camera/draw-time dependence
- evidence: graph only updates via Rebuild() (on-screen section regen OR StaleOffscreen flag w/ same-frame skip); probe poll interval cannot change what a read returns; fix = no-shots keeps all camera/state, skip render only; add --profile, --probe-poll
- fix done: no-shots keeps camera/state, --profile, --probe-poll; selftest ok; publishing
