## spec
testq J20261113T071830Z-7b0808 (SteveDesktop, FlowWorks tier, sha fd568d495b), chain toggle_superdeep_shooting, row
shooting_rule_off FAIL: "OFF: picked 11098, want the nearer pit enemy Human11094"; shooting_rule_on_pit_only then read
UNMEASURED (upstream failed). Not yet known whether this is MOD (the switch off does not restore vanilla targeting) or
HARNESS (vanilla target choice is not strictly the nearest, so the row's expectation is wrong). Decide by reading vanilla
AttackTargetFinder for the scene's verb and range before changing either side.
## acceptance
Live: live-proof A1 of RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE reads shooting_rule_off and shooting_rule_on_pit_only PASS,
or the row is rewritten to vanilla's real rule and a mutant (rule forced on) fails it. Acceptance test (offline): none, live
targeting.
