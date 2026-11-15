import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); sys.path.insert(0, 'src/RimMandrake')
import maturation_dispatch as D
row = lambda m, k, dec, idle, owed='ready to advance': {'mod': m, 'stage': 'offline_build', 'owed': owed, 'live': [], 'decision': dec, 'klass': k, 'idle_min': idle}
cases = [
  ([row('P', 'paused', 'coverage_stop', 250), row('Q', 'launch', 'x', 90)], ['Q'], 90),   # paused excluded, real idle kept
  ([row('P', 'paused', 'coverage_stop', 250)], [], 0),                                     # only paused -> 0
  ([], [], 0),                                                                             # empty
  ([row('Q', 'launch', 'x', 30)], [], 30),                                                 # under line
  ([row('R', None, 'x', 70)], ['R'], 70),                                                  # klass absent still counts
]
bad = 0
for rows, mods, mx in cases:
    r = D.reading({'idle_alarm_min': 60}, rows, 0)
    ok = r['idle_owed_mods'] == mods and r['idle_owed_max_min'] == mx
    bad += not ok
    print('PASS' if ok else 'FAIL', mods, mx, '->', r['idle_owed_mods'], r['idle_owed_max_min'])
sys.exit(1 if bad else 0)
