#!/usr/bin/env python3
"""Selftest for review_map.py (offline): layout, statuses derived from the feature sheet (never typed), placeholders,
labels and the key sheet's plain-language rule."""
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_map as R  # noqa: E402

fails = []


def check(c, msg):
    if not c:
        fails.append(msg)


m, st, capd = R.derive()
S = R.station_list(m, st, capd)
doc = R.visuals_doc()
check(not R.layout_check(S, doc), "layout: %s" % R.layout_check(S, doc)[:5])
ids = [s["id"] for s in S]
feats = [f["id"] for f in m.FEATURES if f["id"] != "land_rivers"]
check(set(feats) <= set(ids), "a feature has no station: %s" % sorted(set(feats) - set(ids)))
check(len(ids) == len(set(ids)), "a feature twice")
check(all(s["status"] == st[s["id"]] for s in S if s["id"] in st), "a station status differs from the sheet's")
check(all(s["placeholder"] == (s["status"] == "not") for s in S), "placeholder iff NOT BUILT")

# status is DERIVED: flip one capability's live row and the station follows (sanity: the flip is visible)
f = next(f for f in m.FEATURES if f["id"] == "flow_spreads")
_, rows = m.latest_result()
rows2 = {k: v for k, v in rows.items()}
for c in f["caps"]:
    for r in capd[c].get("rows", []):
        rows2[r] = ("FAIL", "selftest")
_, st2, capd2 = R.derive(m, rows2)
S2 = R.station_list(m, st2, capd2)
check(next(s for s in S2 if s["id"] == "flow_spreads")["status"] != "works", "status did not follow the evidence")

# layout_check catches an overlap (sanity probe)
bad = [dict(s) for s in S]
bad[1]["origin"] = bad[0]["origin"]
check(any("closer than" in p for p in R.layout_check(bad, doc)), "layout_check missed a planted overlap")

# labels: every station number, every status word in use
ops = R.label_ops(S, st, doc, m)
for s in S:
    check(("|%d  %s|" % (s["n"], s["short"])) in ops, "station %d has no label" % s["n"])
check(all(R.STATUS_WORD[s["status"]] in ops or s["placeholder"] for s in S), "a status word missing from labels")
if doc:
    check(ops.count("|tiny|") >= len(doc["stations"]), "visuals plots unlabelled")

# key sheet: no ticket ids / class names / defNames in the main view (outside the closed agent block); sanity probe
with tempfile.TemporaryDirectory() as d:
    old = R.OUT
    R.OUT = d
    try:
        R.keysheet(S, st, doc, m, live={"probe": "RM_Channel_Deep FLOWWORKS_BUILD_PROGRAM_1"})
        md = open(os.path.join(d, "KEYSHEET.md"), encoding="utf-8").read()
        page = open(os.path.join(d, "keysheet.html"), encoding="utf-8").read()
    finally:
        R.OUT = old
main = md.split("<details>")[0]
rx = re.compile(r"\b[A-Z]{3,}_[A-Z_]{3,}_\d\b|\bRM_[A-Z]\w+|\b[A-Z][a-z]+[A-Z]\w*\.cs\b")
check(not rx.findall(main), "jargon in the key sheet main view: %s" % rx.findall(main)[:5])
check(rx.findall(md.split("<details>")[1]) if "<details>" in md else False, "jargon sweep cannot see the planted probe")
check(not rx.findall(page), "jargon in keysheet.html: %s" % rx.findall(page)[:5])
check("font:18px" in page and "max-width" not in page, "keysheet text size")

print("FAIL\n  " + "\n  ".join(fails) if fails else "ok  review_map: %d stations, layout, derived statuses, labels, plain key sheet" % len(S))
sys.exit(1 if fails else 0)
