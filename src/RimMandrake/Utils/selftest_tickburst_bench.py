"""TICKBURST_PROVE_MANY_TICKS_ONE_FRAME acceptance 1/2/6/7/8/10 offline: tickburst_bench.py --mock (sanity, throughput JSON
fields and provenance, equivalence comparator with bounds, resumable trials, N sweep, perFrameTickCap readback, each
against an in-memory game with faults that must be caught)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = subprocess.run([sys.executable, os.path.join(HERE, "tickburst_bench.py"), "--mock"], capture_output=True, text=True, timeout=300)
fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
oks = [l for l in p.stdout.splitlines() if l.startswith("ok")]
for l in fails:
    print(l)
ok = p.returncode == 0 and not fails and len(oks) >= 30
print("ok   tickburst_bench --mock: %d checks, %d failed" % (len(oks), len(fails)) if ok else
      "FAIL tickburst_bench --mock exit %s, %d ok, %d failed\n%s" % (p.returncode, len(oks), len(fails), p.stderr[-2000:]))
print("RESULT: %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
