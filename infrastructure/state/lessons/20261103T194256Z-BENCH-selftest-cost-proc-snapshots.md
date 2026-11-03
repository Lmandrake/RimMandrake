Each scratch_reap.Ctx/Live costs a whole-/proc walk (~7 s at 52k paths on load ~15, far more under run_selftests' 6 workers): selftest_scratch_reap_tmp passed in 122 s alone and CRASHed [timeout] at the 240 s default in a 26-file --only batch. Reuse one Ctx (copy.copy and set .now) where the test does not need a new look, and tag '# selftest-timeout: N' for what remains (2026-11-03).
home: NONE
