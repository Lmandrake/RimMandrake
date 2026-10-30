# TESTPILOT_SELFTEST_HARDEN_DEDUP_ORDERING

Found by BENCH's independent check of e73abe40ab: mutants that survive selftest_arena_testpilot.
Runner: `D:\ClaudeWork\rimmandrake\testpilot_fixes\check\mutants.py`. Results: `mutants_out.txt`, 16 of 22 killed.

Survivors that leave load-bearing code untested:
- M06 / M07: `_interrupted`'s evidence dedup and state dedup by the in_flight key. The F6 test never kills a pilot
  BETWEEN `_interrupted` and the recovering-clear, which is the only window where the dedup matters. The probe
  `check\probe_window.py` exercises that window and kills both mutants (M06 gives 2 crash records -> quarantined;
  M07 gives parked instead of queued). The unmutated code is correct (1 record, 1 requeue, queued). Add it as a test.
- M18: F8's "most overdue first" (`max` -> `min` survives). Add a test with two overdue sealed repairs.

Survivors that are cosmetic or near-equivalent (fix optionally): M11 (abort does not clear pending_reload; the next
wake reconciles a game that is already None), M12 (no epoch bump on reconcile; the generation already guards), M15
(the problem text of the first mid-proof red vs the latest).

Fake-driver fidelity (from the F7 check): the real `apply_minimal`/`apply_tier` rewrite activeMods wholesale. Move the
reset `self.active = ["ludeon.rimworld"]` into FakeDriver.apply_minimal/apply_tier and drop the in-test line in
t_reload_crash. A check run showed the full suite stays green that way (`check\faithful_fake.txt`). Separately, the
fake's deploy() appends to active, but the real deploy_custom_mods never edits ModsConfig. Live, a candidate mod that
is in neither MINIMAL nor the tier would show as "deployed mod(s) not active", so the canary goes red. This fails safe,
but the fake is more generous than the real game.

## verify
probe_window.py turned into a selftest. A test with two overdue sealed repairs. Re-run mutants.py: M06, M07 and M18 must be KILLED.
