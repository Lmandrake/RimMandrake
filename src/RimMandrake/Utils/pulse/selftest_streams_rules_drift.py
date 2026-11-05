#!/usr/bin/env python3
"""Class guard for SELFTEST_FIX_STREAMS_FQCB: selftest_streams.py must not read the live slot_rules.json.

Its pacing() row twice went nightly-red when the owner retuned the live rules (1b78a2ad, the v3 split; 0751363d,
advisory n_total 6 -> 10), because it asserted the allocator's output against whatever slot_rules.json said that
night. This reruns selftest_streams.py with RM_SLOT_RULES pointing at drifted copies of the live rules (an owner
retune of total_max, of advisory.n_total, and advisory switched off): a hermetic test passes under every one.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent / "slot_rules.json"
TEST = HERE / "selftest_streams.py"

fails = []


def drift(name, edit):
    rules = copy.deepcopy(json.loads(LIVE.read_text(encoding="utf-8")))
    edit(rules)
    with tempfile.TemporaryDirectory(prefix="ss_drift_") as d:
        p = Path(d) / "slot_rules.json"
        p.write_text(json.dumps(rules), encoding="utf-8")
        env = dict(os.environ, RM_SLOT_RULES=str(p))
        r = subprocess.run([sys.executable, str(TEST)], env=env, capture_output=True, text=True, timeout=300)
    bad = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
    ok = r.returncode == 0 and not bad
    print("%s drift %s: selftest_streams rc=%d%s" % ("PASS" if ok else "FAIL", name, r.returncode,
                                                    "" if ok else " -- " + ("; ".join(bad)[:400] or r.stderr[-400:])))
    if not ok:
        fails.append(name)


def _adv(**kw):
    def f(r):
        r.setdefault("advisory", {}).update(kw)
    return f


drift("total_max=4", lambda r: r.update(total_max=4))
drift("advisory.n_total=8", _adv(enabled=True, n_total=8))
drift("advisory off", _adv(enabled=False))

print("RESULT:", "FAIL" if fails else "PASS")
sys.exit(1 if fails else 0)
