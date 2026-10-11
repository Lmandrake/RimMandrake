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
# every visuals check below is inside `if doc:`; a missing JSON must be red here, not a silent skip
check(doc and len(doc["stations"]) == 39, "visuals JSON missing or not 39 stations: %s" % (
    len(doc["stations"]) if doc else doc))
check(not R.layout_check(S, doc), "layout: %s" % R.layout_check(S, doc)[:5])
ids = [s["id"] for s in S]
feats = [f["id"] for f in m.FEATURES if f["id"] != "land_rivers"]
check(set(feats) <= set(ids), "a feature has no station: %s" % sorted(set(feats) - set(ids)))
check(len(ids) == len(set(ids)), "a feature twice")
# (no "status == st[id]" check: station_list copies st[id], so it could never fail; the flip below tests derivation)
check(all(s["placeholder"] == (s["status"] == "not") for s in S), "placeholder iff NOT BUILT")

# status is DERIVED: flip one capability's live row and the station follows (sanity: the flip is visible)
f = next(f for f in m.FEATURES if f["id"] == "flow_spreads")
check(st["flow_spreads"] == "works", "probe precondition: flow_spreads must start 'works' or the flip proves nothing "
      "(now %r; refresh the evidence or pick another works feature)" % st["flow_spreads"])
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
    # each visuals plot carries ITS OWN label text ("|tiny|" counts were met by the gallery's notice lines alone)
    unl = [v["id"] for v in doc["stations"] if ("|%s|" % R.vis_label(v)) not in ops]
    check(not unl, "visuals plots unlabelled: %s" % unl[:5])
    ops_novis = R.label_ops(S, st, None, m)
    check(any(("|%s|" % R.vis_label(v)) not in ops_novis for v in doc["stations"]),
          "sanity: the visuals-label check cannot see a missing visuals block")

# look_canal: each marked plot shows a DIFFERENT fill tier (D2 F1 and D2 F2... once gave two "half" plots)
lc = R.SETUPS["look_canal"]
depth_at = {(x, z): d for x, z, w, h, d in lc["dig"]}
fill_at = {(x, z): f for x, z, w, h, f, _ in lc["fluid"]}
tiers = [R.fill_tier(fill_at.get(k, 0), depth_at[k]) for k in sorted(depth_at)][:4]
check(tiers == [0, 1, 2, 3], "look_canal plots are not empty/trace/half/brim: tiers %s" % tiers)
check(R.fill_tier(1, 3) == 1 and R.fill_tier(1, 2) == 2 and R.fill_tier(2, 3) == 2 and R.fill_tier(3, 3) == 3,
      "fill_tier no longer mirrors RM_ExcavationDepth.FillTier")
check(R.Review.verify_visuals.__doc__, "verify_visuals lost its docstring (a statement above it)")
# --build exit code: a short verify is non-zero; only a full read is 0
check(R.build_exit(39, 39, 30, 30)[0] == 0 and R.build_exit(38, 39, 30, 30)[0] == 1
      and R.build_exit(39, 39, 0, 30)[0] == 1 and R.build_exit(None, 0, 30, 30)[0] == 0,
      "build_exit: %s" % [R.build_exit(38, 39, 30, 30), R.build_exit(39, 39, 0, 30)])
check("39/39" in R.build_exit(39, 39, None, 0)[1], "build_exit text has no denominator")
# --build --save keeps the agent block: the save path passes live to keysheet
check("keysheet(S, st, doc, m, live, save=name)" in open(R.__file__, encoding="utf-8").read(),
      "--save rewrites the key sheet without the --build agent block")

# review_map_visuals: only --write rewrites the committed JSON (--help and typos once rewrote it)
_wrote = []
_w = R.VIS.write
R.VIS.write = lambda: _wrote.append(1) or ("x", 0)
try:
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        for argv in ([], ["--help"], ["--wirte"]):
            try:
                R.VIS.main(argv)
            except SystemExit:
                pass
        check(not _wrote, "review_map_visuals rewrote the JSON without --write")
        R.VIS.main(["--write"])
    check(_wrote, "sanity: --write did not reach write()")
finally:
    R.VIS.write = _w

# verify_visuals: a blind scorch read (None) is UNMEASURED, never "not scorched"
P = {"w": 4, "h": 3, "depth": 2}
rows_ok = [{"d": 2, "f": 1}] * 12
check(R.visual_verdict(P, 1, False, rows_ok, None, 1) is None, "blind scorch read passed a non-scorched station")
check(R.visual_verdict(P, 1, False, rows_ok, 0.0, 1) is True, "a read 0.0 on a non-scorched station must pass")
check(R.visual_verdict(P, 1, True, rows_ok, 0.0, 1) is False, "an unscorched read on a scorched station must fail")
check(R.visual_verdict(P, 1, False, rows_ok[:5], None, 1) is False, "a mis-built station must fail even when blind")
# verify_gallery: a placeholder is not "verified as built"; pawns match by kind, not head count
check(R.gallery_verdict(True, True, [], [], []) is None, "a placeholder counted as verified")
check(R.gallery_verdict(False, True, [], ["Muffalo"], ["Colonist"]) is False, "wrong pawn kind passed on head count")
check(R.gallery_verdict(False, True, [], ["Muffalo", "Colonist"], ["Colonist", "Muffalo", "Hare"]) is True,
      "right kinds (plus a stray) must pass")

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
# every V-block state is described (the extras were dropped by a hard-coded six-state list), and no stale save is named
for state in ("dry", "water", "tar", "scorched") + R.VIS.EXTRAS:
    v = next((v for v in (doc or {}).get("stations", []) if v["id"].split("_")[1] == state), None)
    if v:
        check(v["what_to_notice"] in md and R.html.escape(v["what_to_notice"]) in page,
              "key sheet does not describe the %s station" % state)
check("RM_fw_review_20261005" not in md + page, "key sheet names a hard-coded old save")
rx = re.compile(r"\b[A-Z]{3,}_[A-Z_]{3,}_\d\b|\bRM_[A-Z]\w+|\b[A-Z][a-z]+[A-Z]\w*\.cs\b")
check(not rx.findall(main), "jargon in the key sheet main view: %s" % rx.findall(main)[:5])
check(rx.findall(md.split("<details>")[1]) if "<details>" in md else False, "jargon sweep cannot see the planted probe")
check(not rx.findall(page), "jargon in keysheet.html: %s" % rx.findall(page)[:5])
check("font:18px" in page and "max-width" not in page, "keysheet text size")

print("FAIL\n  " + "\n  ".join(fails) if fails else "ok  review_map: %d stations, layout, derived statuses, labels, plain key sheet" % len(S))
sys.exit(1 if fails else 0)
