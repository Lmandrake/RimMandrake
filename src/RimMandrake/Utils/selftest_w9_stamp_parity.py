#!/usr/bin/env python3
"""Selftest: the three stamp-side parity fixes (design/Jawa/worldbuilding/parity_causes_2026-10-20.md).

Offline; no bridge, no game, no def dump.
 U4 rivers   1a probe: the RECORD links laid in file order reproduce the flattened dev riverDist
               (the U4 plan's `before`, max <= 5) - the instrument can see the defect
             1b the same rows through order_links_mouth_first + the bundle's riverdist table give the
               canonical riverDist on every river tile; edge set, defs and road rows unchanged
             1c w9_run.mouth_first_links: no riverdist file -> LINKS itself (old behaviour); with it ->
               a temp CSV that lays canonical; an impossible target -> refused
 U2 mutators 2a rolled_mutators removes only what the input lacks, keeps KEEP_DERIVED
             2b it agrees with parity_fix_plans.mutator_diff's `remove`, and KEEP_DERIVED is one set
             2c read_live_mutators refuses a truncated read
 U1 labels   3a the bundle's features CSV carries the canonical size and a centerTile on its own region
               for all 71 labels (Fall Line 26)
             3b probe: check_companions flags a centerTile moved off its region
             3c world_features_import (C#) takes featuresPath, reads size/centerTile by name, keeps
               the sqrt(tiles)*1.35 fallback, and never reads the mirrored-frame drawCenter column
             3d paint_inputs_build.add_label_centres refuses a plan/CSV name mismatch

    python3 src/RimMandrake/Utils/selftest_w9_stamp_parity.py
"""
import contextlib, csv, io, json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w9_run  # noqa: E402
import river_lay  # noqa: E402

REPO = w9_run.REPO
BUNDLE = os.path.join(REPO, "world", "paint_inputs_2026-10-20")
RECORD_LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")
U1 = os.path.join(REPO, "world", "ASHKARR_PARITY_U1_labels_2026-10-20_plan.json")
U4 = os.path.join(REPO, "world", "ASHKARR_PARITY_U4_riverdist_2026-10-20_plan.json")
CS = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchWorldTools.cs")
fails = []


def ok(cond, name):
    print(("ok  " if cond else "FAIL"), name)
    if not cond:
        fails.append(name)


def rows(path):
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def sim(link_rows):
    return river_lay.simulate_overlay([(int(r["a"]), int(r["b"])) for r in link_rows if r["kind"] == "river"])


def edges(link_rows):
    return sorted((min(int(r["a"]), int(r["b"])), max(int(r["a"]), int(r["b"])), r["def"])
                  for r in link_rows if r["kind"] == "river")


def rivers_and_roads():
    rec = rows(RECORD_LINKS)
    plan = json.load(io.open(U4, encoding="utf-8"))
    before = {int(k): v for k, v in plan["before"].items()}
    target = river_lay.read_river_dist(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_riverdist.csv"))
    flat = sim(rec)
    ok(all(flat[t] == v for t, v in before.items()) and max(flat[t] for t in before) <= 5,
       "1a probe: record file order reproduces the flattened dev riverDist (max %d)" % max(flat[t] for t in before))
    laid, mism = river_lay.order_links_mouth_first(rec, target)
    got = sim(laid)
    ok(not mism and all(got[t] == v for t, v in target.items()) and len(target) == 335
       and max(target.values()) == 50,
       "1b mouth-first lay gives canonical riverDist on %d/%d river tiles (max %d)"
       % (sum(got[t] == v for t, v in target.items()), len(target), max(got[t] for t in target)))
    ok(edges(laid) == edges(rec) and [r for r in laid if r["kind"] == "road"] == [r for r in rec if r["kind"] == "road"],
       "1b same river edges and defs; roads unchanged and in order")
    ok(target == {int(k): v for k, v in plan["after"].items()}, "1b bundle riverdist == U4 plan `after`")

    tmp = tempfile.mkdtemp(prefix="w9par_")
    try:
        shutil.copy(RECORD_LINKS, os.path.join(tmp, "ASHKARR_WORLDMAP_links.csv"))
        w9_run.set_inputs(tmp)
        out = []
        p, good = quiet(w9_run.mouth_first_links, out, tmp)
        ok(good and p == w9_run.LINKS, "1c no riverdist file -> LINKS in file order (old behaviour)")
        shutil.copy(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_riverdist.csv"), tmp)
        p, good = quiet(w9_run.mouth_first_links, out, tmp)
        got = sim(rows(p)) if good else {}
        ok(good and p != w9_run.LINKS and all(got.get(t) == v for t, v in target.items()),
           "1c with riverdist -> temp CSV that lays canonical")
        rd = os.path.join(tmp, "ASHKARR_WORLDMAP_riverdist.csv")
        base = io.open(rd, encoding="utf-8").read()
        with io.open(rd, "a", encoding="utf-8") as fh:
            fh.write("999999,7\n")   # a tile no link touches
        p, good = quiet(w9_run.mouth_first_links, out, tmp)
        ok(not good, "1c a river_dist row for a tile no river link touches is refused")
        head = max(target, key=lambda t: target[t])
        with io.open(rd, "w", encoding="utf-8") as fh:   # a real head pushed out of reach
            fh.write(base.replace("\n%d,%d\n" % (head, target[head]), "\n%d,%d\n" % (head, 500)))
        p, good = quiet(w9_run.mouth_first_links, out, tmp)
        ok(not good, "1c an unreachable river_dist on a real tile is refused")
    finally:
        w9_run.set_inputs(os.path.join(REPO, "world"))
        shutil.rmtree(tmp, ignore_errors=True)


def mutators():
    stamp = {(1, "River"), (2, "Coast"), (3, "Caves")}
    live = [(1, "River"), (1, "VEE_LargerRegion"), (2, "RM_SeaCoast"), (3, "Caves"), (3, "Mountain"),
            (4, "RM_MoldyEnvironment"), (4, "RM_MoldyEnvironment")]
    strip = w9_run.rolled_mutators(live, stamp)
    ok(strip == {"VEE_LargerRegion": [1], "Mountain": [3], "RM_MoldyEnvironment": [4]},
       "2a strip = rolled only; stamped and RM_SeaCoast kept (got %s)" % strip)
    ok(w9_run.stamp_mutator_entries([{"tile": "5", "mutators": "A; B;"}]) == {(5, "A"), (5, "B")},
       "2a input entries split on ';'")
    try:
        import parity_fix_plans as P
        rem, _, kept, _ = P.mutator_diff(live, stamp)
        flat = sorted((t, d) for d, ts in strip.items() for t in ts)
        ok(flat == sorted(set(rem)) and set(P.KEEP_DERIVED) == set(w9_run.KEEP_DERIVED),
           "2b agrees with parity_fix_plans.mutator_diff; KEEP_DERIVED is one set")
    except ImportError as e:   # numpy absent: say so, do not pass silently
        ok(False, "2b parity_fix_plans import failed: %s" % e)

    class FakeRB(object):
        def call(self, method, args):
            return {"success": True, "limitHit": args["range"].startswith("0-"), "errors": [], "tiles": []}
    try:
        w9_run.read_live_mutators(FakeRB(), 4000)
        ok(False, "2c truncated live read must raise")
    except RuntimeError:
        ok(True, "2c truncated live read is refused")


def labels():
    plan = {f["name"]: f["after"] for f in json.load(io.open(U1, encoding="utf-8"))["features"]}
    feats = rows(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_features.csv"))
    ok(len(feats) == 71 and all(float(r["size"]) == float(plan[r["name"]]["size"])
                                and int(r["centerTile"]) == plan[r["name"]]["centerOnTile"] for r in feats)
       and float(next(r for r in feats if r["name"] == "Fall Line")["size"]) == 26.0,
       "3a bundle features: canonical size + centerTile for all 71 (Fall Line 26)")
    w9_run.set_inputs(BUNDLE)
    try:
        ok(quiet(w9_run.check_companions, []) == [], "3a check_companions passes the bundle")
        tmp = tempfile.mkdtemp(prefix="w9feat_")
        try:
            for k in ("tiles", "links"):
                shutil.copy(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_%s.csv" % k), tmp)
            bad = [dict(r) for r in feats]
            bad[0]["centerTile"] = next(r for r in feats if r["name"] != bad[0]["name"])["centerTile"]
            with io.open(os.path.join(tmp, "ASHKARR_WORLDMAP_features.csv"), "w", encoding="utf-8", newline="") as fh:
                wr = csv.DictWriter(fh, fieldnames=list(feats[0].keys()), lineterminator="\n")
                wr.writeheader()
                wr.writerows(bad)
            w9_run.set_inputs(tmp)
            ok(any(p.startswith("features:") for p in quiet(w9_run.check_companions, [])),
               "3b probe: a centerTile off its region is flagged")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        w9_run.set_inputs(os.path.join(REPO, "world"))

    src = io.open(CS, encoding="utf-8").read()
    i = src.index('"jawa/world_features_import"')
    body = src[i:src.index("jawa/seabed_layer_probe", i)]
    ok("string featuresPath = null" in body and '"centerTile"' in body and '"size"' in body
       and "Math.Sqrt(kv.Value.Count) * 1.35f" in body and 'Cell(fcsv, row, "drawCenter")' not in body,
       "3c C# features import: featuresPath by name, 1.35 fallback kept, drawCenter column unread")

    import paint_inputs_build as B
    try:
        quiet(B.add_label_centres, ["name"], [{"name": "Nowhere"}], U1)
        ok(False, "3d name mismatch must refuse")
    except SystemExit:
        ok(True, "3d add_label_centres refuses a name mismatch")


def main():
    rivers_and_roads()
    mutators()
    labels()
    print("FAIL selftest_w9_stamp_parity: %d" % len(fails) if fails else "OK selftest_w9_stamp_parity")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
