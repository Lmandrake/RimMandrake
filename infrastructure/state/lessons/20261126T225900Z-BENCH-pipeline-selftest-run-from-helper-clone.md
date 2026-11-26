A pipeline selftest run from a helper clone that lags origin/main runs the old test code, and the old code can land fixture state on origin. On 2026-11-26, selftest_maturation_dispatch.py from a clone that predated its fix ca4c2668a2 pushed the fake lease run-1794718800 onto the real Gimme Some Slack ledger (2922615d3a), and every later publish read the cert red gates case red beside other checks. Rebase onto origin/main before you run a pipeline selftest by hand.
item: TECHPRINT_FACTION_GATING_1
home: skills/using-rimflow/references/traps.md
