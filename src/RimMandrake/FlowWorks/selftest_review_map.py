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
check(tiers == [0, 2, 3, 4], "look_canal plots are not dry/0.5/1/1.5 m of water: tiers %s" % tiers)
check(R.fill_tier(1, 3) == 2 and R.fill_tier(1, 2) == 2 and R.fill_tier(1, 4) == 2 and R.fill_tier(2, 3) == 3
      and R.fill_tier(3, 3) == 4 and R.fill_tier(4, 4) == 5 and R.fill_tier(9, 9) == 5,
      "fill_tier no longer mirrors RM_ExcavationDepth.FillTier (by metres of water, any hole)")
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

# every built station has a how-to-poke and a what-to-look-for line, and layout_check sees a missing one (sanity)
check(all(s["placeholder"] or (s["try_"] and s["look"]) for s in S), "a station without poke/look lines")
bad = [dict(s) for s in S]
k0 = next(i for i, s in enumerate(bad) if not s["placeholder"])
bad[k0]["look"] = ""
check(any("what-to-look-for" in p for p in R.layout_check(bad, doc)), "layout_check missed a planted missing look line")
# extras sit beside the station they extend (neighbours differ in one thing)
order = [s["id"] for s in S]
for k, v in R.extras().items():
    a = v.get("after")
    if a and a in order and k in order:
        check(order.index(k) == order.index(a) + 1 or R.SETUPS.get(order[order.index(k) - 1], {}).get("after") is not None,
              "extra %s is not beside %s" % (k, a))
# an extra's status is derived from its probes: a planted missing def makes it NOT BUILT (sanity both ways)
pb = dict(R.SETUPS["tank_sizes"])
check(R.extra_status(m, pb, capd, rows)[0] != "not", "tank_sizes probes should find the tall tanks on disk")
pb["probes"] = ["xml:defName>RM_NoSuchTank_Selftest<"]
check(R.extra_status(m, pb, capd, rows)[0] == "not", "a missing probe did not make the extra NOT BUILT")
# staged mid-states: half-full tanks are half of 16/32/32/64 kL (litres, LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS); the raised ladder is raised
caps_ = {"RM_LiquidTank": 16000, "RM_LiquidTankTall": 32000, "RM_UniversalCargoTank": 32000, "RM_UniversalCargoTankXTall": 64000}
ts = R.SETUPS["tank_sizes"]
at = {(b[1], b[2]): b[0] for b in ts["build"]}
check(all(u * 2 == caps_[at[(x, z)]] for x, z, _, _, u in ts["tank"]), "tank_sizes not staged half full")
check(R.SETUPS["hold_ladder_raised"]["ladder"] == [(7, 8, "raise")], "the raised-ladder station is not raised")
# PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: each ladder station stages one slid up and one slid down on DIFFERENT walls
_hl = R.SETUPS["hold_ladder"]
check([(d, x, z) for d, x, z, _ in _hl["spawn"]] == [("RM_Ladder", 5, 6), ("RM_Ladder", 7, 4)]
      and _hl["ladder"] == [(7, 4, "raise")], "hold_ladder: west slid down + south slid up")
check(("RM_Ladder", 12, 6, 1, None) in R.SETUPS["hold_ladder_raised"]["build"], "hold_ladder_raised: an east-wall ladder built turned east")

# map R: anchors on a synthetic river (vertical band x 100..110 of moving water on a 250 map)
import review_map_rivers as RV  # noqa: E402
terr = {(x, z): ("WaterMovingChestDeep" if 100 <= x <= 110 else "Soil") for x in range(250) for z in range(250)}
placed, unplaced = RV.plan(terr, (250, 250))
check(len(placed) == len(RV.STATIONS) and not unplaced, "river plan placed %d of %d" % (len(placed), len(RV.STATIONS)))
bs = [c[0] for _, c, _ in placed]
check(all(max(abs(a[0] - b[0]), abs(a[1] - b[1])) >= RV.SPACING for i, a in enumerate(bs) for b in bs[i + 1:]),
      "river anchors closer than SPACING")
check(all(c[2] == 11 and terr[c[3]] == "Soil" and terr[c[0]] == "Soil" for _, c, _ in placed), "a crossing is not 11 wide")
for st_, c, o in placed:
    for d_, (x, z), rot, _ in o["build"]:
        if d_ in ("RM_BankWeir", "RM_SluiceBox"):
            check(RV.ROT[c[1]] == rot and terr[(x + c[1][0], z + c[1][1])].startswith("WaterMoving"),
                  "%s wet end not in the water" % d_)
    if st_["id"] == "r_ferry":
        check([b[1] for b in o["build"]] == [c[0], c[3]], "ferry posts not on both banks")
    if st_["id"] == "r_ford":
        check(len(o["terrain"]) == c[2], "ford stones do not span the river")
wide = {(x, z): ("WaterMovingChestDeep" if 60 <= x <= 160 else "Soil") for x in range(250) for z in range(250)}
check(RV.plan(wide, (250, 250))[0] == [], "a 101-wide river (over the rope span) still got anchors")
check(RV.plan({(x, z): "Soil" for x in range(50) for z in range(50)}, (50, 50))[1] == [s["id"] for s in RV.STATIONS],
      "a riverless map should leave every river station unplaced")
with tempfile.TemporaryDirectory() as d:
    pth = os.path.join(d, "p.json")
    RV.save_placed(pth, placed)
    back = RV.load_placed(pth)
    check([(s["id"], c) for s, c, _ in back] == [(s["id"], c) for s, c, _ in placed], "placed anchors do not round-trip")

# coverage: the whole inventory is covered, every rule names a station, and an unknown item is caught (sanity)
import review_map_coverage as COV  # noqa: E402
items = COV.inventory()
check(len(items) > 500 and {k for k, _, _ in items} == {"def", "set", "gizmo", "tex"}, "inventory blind: %d" % len(items))
got, unc = COV.classify(items)
check(not unc, "uncovered: %s" % unc[:5])
check(not COV.check_targets(S, [s["id"] for s in RV.STATIONS]), "rule names no station: %s" % COV.check_targets(
    S, [s["id"] for s in RV.STATIONS])[:3])
check(COV.classify(items + [("def", "ThingDef/RM_SelftestThing", "x")])[1], "a planted unknown def was covered")
check(COV.check_targets([s for s in S if s["id"] != "pit_ramp"], [s["id"] for s in RV.STATIONS]),
      "a removed station left its rule unflagged")
with tempfile.TemporaryDirectory() as d:
    cv = COV.write(S, path=os.path.join(d, "C.md"), items=items)
    txt = open(cv["path"], encoding="utf-8").read()
check(cv["uncovered"] == 0 and "python.exe src/RimMandrake/FlowWorks/review_map.py --build" in txt, "coverage file")

# in-save sign books: one per built station, own cell outside every station footprint
books = R.sign_ops(S)
bc = [tuple(int(v) for v in b.split("|")[:2]) for b in books]
built = [t for t in S if not t["placeholder"]]
inside = [c for c in bc if any(t["origin"][0] <= c[0] < t["origin"][0] + R.SW and t["origin"][1] <= c[1] < t["origin"][1] + R.SH
                               for t in S)]
check(len(books) == len(built) and not inside and len(set(bc)) == len(bc) and all(b.split("|")[2].startswith("SIGN ") for b in books),
      "sign books: %d for %d built stations; inside a footprint: %s" % (len(books), len(built), inside[:5]))
vdoc = {"stations": R.VIS.stations()}
vb = R.vis_sign_ops(vdoc)
vc = [tuple(int(v) for v in b.split("|")[:2]) for b in vb]
vin = [c for c in vc for v in vdoc["stations"] for o in [R.VIS.origin_of(v, *R.VIS_BASE)]
       if o[0] <= c[0] < o[0] + R.VIS.PLOT_W and o[1] <= c[1] < o[1] + R.VIS.PLOT_H]
check(len(vb) == len(vdoc["stations"]) and not vin and len(set(vc + bc)) == len(vc) + len(bc)
      and all(len(b.split("|")[2]) > 0 for b in vb), "visuals sign books: %d for %d plots; inside a plot: %s"
      % (len(vb), len(vdoc["stations"]), vin[:5]))
pl = [(st_, None, dict(label=(20 + 30 * i, 40))) for i, st_ in enumerate(RV.STATIONS)]
check(len(RV.sign_ops(pl)) == len(RV.STATIONS), "map R: one sign book a river station")

print("FAIL\n  " + "\n  ".join(fails) if fails else "ok  review_map: %d stations, layout, derived statuses, labels, signs, plain key sheet" % len(S))
sys.exit(1 if fails else 0)
