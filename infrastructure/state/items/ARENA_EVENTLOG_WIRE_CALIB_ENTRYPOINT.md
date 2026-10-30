# ARENA_EVENTLOG_WIRE_CALIB_ENTRYPOINT

## spec
ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST's criterion said critic calibration counts and intervals go to the arena
event log, but arena_eventlog's ENTRYPOINTS allowlist had no calibration entry, so they went to score.json plus a
rimflow note (evidence D:\ClaudeWork\rimmandrake\arena\calibration\critic\l4-main\score.json).

Built:
- arena_eventlog: `arena_critic_calib.py` joins ENTRYPOINTS; new event `calib`, valid only on arm
  CALIB_ARM = `critic_calib` (that arm holds nothing else). It must carry verdict in RELIABLE/UNRELIABLE/UNMEASURED/
  INCONCLUSIVE, detail.critic, set_sha256, integer invalid <= candidates, and false_reject/miss as
  {k, n, wilson95 [lo, hi], threshold} with 0 <= k <= n and 0 <= lo <= hi <= 1.
- NON_ARENA_ARMS = (critic_calib,): report() still verifies, anchors and rosters it (a deleted calibration log is
  refused), but arena_analysis.load_verified / load_raw never count it as a competing arm. Without this, a calib
  log in the arena store would enter the spend binding, window and per-arm problems.
- arena_critic_calib `score` writes score.json, then signs a `calib` event (run_id = run; detail = the six rate
  blocks' k/n/wilson95/threshold, critic + fingerprint, set sha, invalid/candidates, why, adjudicated sensitivity
  text). When the harness cannot sign (no token, RM_ARM, arm cwd) it prints `eventlog: NOT SIGNED` and exits 3;
  `--no-eventlog` skips it.

## criteria
- A1 L0: selftest_arena_eventlog t_calib_entry CAL-1..CAL-4: `arena_critic_calib.py score` run as a real process signs one calib event whose counts/intervals/verdict equal score.json; under RM_ARM it exits 3 and signs nothing; --no-eventlog exits 0. Forced: with `arena_critic_calib.py` removed from ENTRYPOINTS, CAL-1/2/3/7 FAIL
- A2 L0: CAL-5/CAL-6: a complete calib event validates; 14 malformed forms (wrong arm, other event on the calib arm, no/unknown verdict, no critic/set/miss, k > n, bool/float counts, lo > hi, interval > 1, no threshold, invalid > candidates) are each rejected
- A3 L0: CAL-7/CAL-8: report() verifies the calib arm; arena_analysis.load_verified and load_raw skip it while keeping a real arm
- A4 L1: the l4-main score is re-signed on the real harness token (`python3 src/RimMandrake/Utils/arena/arena_critic_calib.py score --run l4-main` from a harness shell) and `arena_eventlog.py report` lists arm critic_calib with 1 accepted record
