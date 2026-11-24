#!/usr/bin/env python3
"""items.py - ledger items about SteveDesktop or testq: state now, filed in the window, by family. Reads the event shards."""
import collections, glob, json, re, subprocess
from common import START, END
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
ev = collections.defaultdict(list)
for f in glob.glob(ROOT + "/infrastructure/state/ledger/events/*.jsonl"):
    for l in open(f, errors="replace"):
        try: d = json.loads(l)
        except ValueError: continue
        i = d.get("item") or d.get("id")
        if isinstance(i, str) and re.search(r"STEVE(?!N)|TESTQ|^HARNESS_REPAIR", i): ev[i].append(d)
fam = lambda i: re.sub(r"_[0-9A-F]{4}$|_[A-Z]{4}$|_[0-9A-F]{8}(_\d)?$", "", i) if re.match(r"STEVE_LANE|HARNESS_REPAIR|OPS_", i) else "named item"
K = collections.Counter(); F = collections.Counter(); st = {}
import sys
sys.path.insert(0, ROOT + "/src/RimMandrake/rimflow")
import model
w = model.replay()
for i, e in ev.items():
    e.sort(key=lambda d: d.get("ts") or d.get("at") or "")
    t = e[0].get("ts") or e[0].get("at")
    it = w.items.get(i)
    s = getattr(it, "state", None) or getattr(it, "status", None) or (it or {}).get("state") if it is not None else "no item"
    st[i] = s
    if START.isoformat()[:19] <= t[:19] <= END.isoformat()[:19]: F[(fam(i), s)] += 1
print("filed in window by family and state now:")
for k, v in sorted(F.items(), key=lambda z: (z[0][0], -z[1])): print("  ", v, k)
print("open now:", sorted(i for i, s in st.items() if s not in ("done", "dropped", "superseded", "no item", "resolved")))
