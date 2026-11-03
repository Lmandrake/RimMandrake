"""Selftest for LongShade/prove_stampede.py (LONGSHADE_STAMPEDE_LIVECHECK_1): the offline half of the proof stays green, so a
drifted mechanism string, tuning number or probe method breaks the nightly sweep instead of the next live sitting."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prove_stampede", os.path.join(HERE, "prove_stampede.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

rc = m.offline()
# sanity probe: the judge can see a failure at all (a judge that passes everything would leave offline() green too)
rec = m._good()
rec["hot"] = rec["hot"].replace("sub=True", "sub=False", 1)
seen = m.judge(rec)["A2"][0] == 1
print("%-5s sanity probe: judge fails A2 when canFireNow is false on a hot herd" % ("ok" if seen else "FAIL"))
sys.exit(0 if rc == 0 and seen else 1)
