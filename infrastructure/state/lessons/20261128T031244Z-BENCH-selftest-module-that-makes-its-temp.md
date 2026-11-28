A selftest module that makes its temp root at import (TMP = mkdtemp(...)) and removes it only in its own main() leaks one tree on every run of each selftest that imports it for its fixtures: selftest_wrong_check_fixed_in_sitting.py left 181 trees, 521 k entries, in ~/.seat-tmp/BENCH (2026-11-27). Make such a root with selftest_own_dirs.own_dir_for_run(tag, redirect_tmp=False), so it goes at exit, on SIGTERM/SIGHUP, or at the next import after a SIGKILL.
item: RIMMANDRAKE_SPEED_SCRATCH_REAP_SEAT_TMP_PUBLISH_CHECK_RESIDUE_2M
home: skills/rimworld-modding/references/project-engine-facts.md
