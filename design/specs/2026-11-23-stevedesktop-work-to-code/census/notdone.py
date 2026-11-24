#!/usr/bin/env python3
"""notdone.py - not-DONE jobs by cause and normalised note head, with one example id each. Splits fault-window and filler."""
import collections, re
from common import records
R, bad = records()
G = collections.defaultdict(list)
for d in R:
    r = d.get("result") or {}
    if r.get("outcome") == "DONE": continue
    n = re.sub(r"J?\d{8}T\d{6}Z(-\w+)?(\.a\d)?", "<id>", str(r.get("note")))
    n = re.sub(r"0x[0-9a-f]+|\b[0-9a-f]{8,}\b|\d+(\.\d+)?", "#", n)
    G[(r.get("outcome"), r.get("cause"), n[:170])].append(d)
for k, v in sorted(G.items(), key=lambda kv: -len(kv[1])):
    q = sum(d["_state"] == "quarantined" for d in v); fl = sum("filler" in str(d["job"].get("requested_by")) for d in v)
    print(len(v), "quar", q, "filler", fl, v[0]["_fin"].date(), v[-1]["_fin"].date(), k, v[-1]["job"]["id"], sorted({d["job"]["mod"] for d in v})[:5])
