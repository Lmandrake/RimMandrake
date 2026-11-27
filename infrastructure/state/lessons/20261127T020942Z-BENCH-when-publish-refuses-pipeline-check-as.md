When ./publish refuses a pipeline check as 'green on origin/main <base>: this change turned it red' and the clone is many commits behind, the base it names is the clone's own old base, not today's origin/main. Rebase onto origin/main and run the check there before you hunt your diff. On 2026-11-26 the red cert-red-gates case of selftest_maturation_dispatch.py came from live ledger state that origin had already stubbed out, not from the steward's change.
item: RIMMANDRAKE_STEWARD_PYRELANDS_PREFLIGHT_STAGE
home: skills/clone-landing-commits
