#!/usr/bin/env python3
"""jobs.py - every lane job of the window: state, host, who asked, outcome/cause, and the NOT-DONE ones by note head."""
import collections, re
from common import records, START, END
R, bad = records(("done", "quarantined", "cancelled", "pending", "running", "orphans"))
print("window", START, END, "records", len(R), "unreadable", len(bad), bad[:5])
C = collections.Counter
print("state", C(d["_state"] for d in R))
D = [d for d in R if d["_state"] in ("done", "quarantined")]
print("host", C((d.get("host"), d["_state"]) for d in D))
def by(d):
    j = d.get("job") or {}; return j.get("requested_by")
print("requested_by", C(by(d) for d in D).most_common(30))
print("mod", C((d.get("job") or {}).get("mod") for d in D).most_common(30))
print("purpose", C((d.get("job") or {}).get("purpose") for d in D))
print("outcome", C((d["_state"], (d.get("result") or {}).get("outcome"), (d.get("result") or {}).get("cause")) for d in D).most_common(40))
print("item named", C(bool((d.get("job") or {}).get("item") or (d.get("job") or {}).get("row_items")) for d in D))
print("filler?", C(("filler" if "filler" in str(by(d)) else "visit" if "visit" in str(by(d)) else "other", (d.get("result") or {}).get("outcome")) for d in D).most_common())
print("ingested", C((str((d.get("ingested") or {}).get("skipped"))[:70], sorted(k for k in (d.get("ingested") or {}) if k != 'at').__str__()[:90]) for d in D).most_common(30))
