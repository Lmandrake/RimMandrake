A scratch clone made with scratch_clone.py --sparse (default tooling dirs) has no src/RimMandrake/contracts, so selftest_maturation_dispatch.py CRASHES (ModuleNotFoundError: contracts, via delegated_digest.build) and run_selftests reads RED for a reason unrelated to the change. Fix: git sparse-checkout add src/RimMandrake/contracts, then re-run; read a CRASH's traceback before blaming your diff.
item: RIMMANDRAKE_MEASURE_MATURATION_CONVERGENCE_PER_ROUND
home: skills/clone-landing-commits
