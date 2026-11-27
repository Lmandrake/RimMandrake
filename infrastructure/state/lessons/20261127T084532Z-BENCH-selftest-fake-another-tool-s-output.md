A selftest fake of another tool's output must print what the real tool prints. fresh_reader's test faked check --record printing FLAGGED, but the real tool prints DIRTY for a flagged file, so every reader ticket that ended in a flag stayed red. Drive the real tool once on a moved root (CODE_REVIEW_STATUS_ROOT) beside the fake.
item: RIMMANDRAKE_READ_FIX_3318E30BE0_WITH_FRESH_EYES
home: skills/clone-landing-commits
