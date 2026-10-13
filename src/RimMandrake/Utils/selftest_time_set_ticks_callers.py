#!/usr/bin/env python3
"""Static guard (CLOCK_SET_CALLERS_MIGRATE_DECLARE_FIRST): the deployed companion refuses
jawa/time_set_ticks on a map with colonists unless timeException=true. Every live call site
under src/ must pass it (fakes/selftests that merely handle the tool are exempt)."""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
bad, n = [], 0
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if not f.endswith(".py") or f.startswith("selftest") or f in ("watch.py", "prove_vitals_governor.py") :  # the proof asserts the refusal without the flag
            continue
        p = os.path.join(d, f)
        try: s = open(p, encoding="utf-8").read()
        except Exception: continue
        for m in re.finditer(r'call\(\s*"jawa/time_set_ticks"', s):
            n += 1
            i = s.index("(", m.start()); dep = 0
            for j in range(i, len(s)):
                dep += (s[j] == "(") - (s[j] == ")")
                if dep == 0: break
            if "timeException" not in s[i:j]:
                bad.append("%s:%d" % (p, s.count("\n", 0, m.start()) + 1))
print("call sites: %d, missing timeException: %d" % (n, len(bad)))
for b in bad: print("FAIL", b)
if n < 10: print("FAIL: found only %d call sites; scanner is blind" % n); sys.exit(1)
sys.exit(1 if bad else 0)
