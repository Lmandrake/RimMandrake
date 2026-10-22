"""Offline checks for water_looks_proof.py: the ProofWaterLook line parses, every pure verdict can go red, and every
FakeBridge fault (a planted defect) lands on its expected row. No bridge."""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import water_looks_proof as W  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


# ---- the C# line formats parse (RM_WaterLookProofs.ProofWaterLook's own docstring shape)
LINE = ("WATERLOOK cell=46,41 terrain=WaterDeep still=True dug=True hollow=22 waterM=11 dlPerMetre=2000 tint=2 tn=0 tw=0 key=2 "
        "watchKey=2 tintOn=True bandOn=True facesOn=True tintVisible=True bandVisible=True lookDirty=False")
kv = W.parse(LINE)
check("parse: every field of the read line", all(k in kv for k in (
    "cell", "terrain", "still", "dug", "hollow", "waterM", "dlPerMetre", "tint", "tn", "tw", "key", "watchKey", "tintOn", "bandOn",
    "facesOn", "tintVisible", "bandVisible", "lookDirty")))
check("parse: numbers read as numbers", W.fnum(kv, "tint") == 2 and W.fnum(kv, "waterM") == 11 and W.fnum(kv, "dlPerMetre") == 2000)
check("parse: an unread / NaN field is None", W.fnum({"watchKey": "unread"}, "watchKey") is None and W.fnum({"tn": "NaN"}, "tn") is None)
check("parse: the set and take lines", W.parse("WATERLOOKSET tintOn=False bandOn=True")["tintOn"] == "False"
      and W.parse("WATERTAKE cells=9 took=63000")["took"] == "63000")


def R(**over):
    d = dict(kv)
    d.update({k: str(v) for k, v in over.items()})
    return d


t5, t10, ctrl = R(waterM=6, tint=1), R(waterM=11, tint=2), R(waterM=3, tint=0)
check("A1 five: 6 m navy, 3 m clear: PASS", W.five_verdict(t5, ctrl) == ("PASS", "MOD"))
check("can-fail A1 five: 6 m untinted: FAIL", W.five_verdict(R(waterM=6, tint=0), ctrl)[0] == "FAIL")
check("can-fail A1 five: the 3 m control tints: FAIL", W.five_verdict(t5, R(waterM=3, tint=1))[0] == "FAIL")
check("A1 five: an unfilled pit: UNMEASURED/SITE", W.five_verdict(R(waterM=1, tint=0), ctrl) == ("UNMEASURED", "SITE"))
check("A1 five: unread: UNMEASURED/HARNESS", W.five_verdict({}, ctrl) == ("UNMEASURED", "HARNESS"))
check("A1 ten: 11 m darker than 6 m: PASS", W.ten_verdict(t10, t5) == ("PASS", "MOD"))
check("can-fail A1 ten: 11 m on the 5 m step: FAIL", W.ten_verdict(R(waterM=11, tint=1), t5)[0] == "FAIL")
check("A1 terrain: WaterDeep and still: PASS", W.terrain_verdict({"T5": t5, "T10": t10}) == ("PASS", "MOD"))
check("can-fail A1 terrain: a new terrain: FAIL", W.terrain_verdict({"T5": t5, "T10": R(waterM=11, terrain="RM_Navy")})[0] == "FAIL")
check("A1 terrain: unread: UNMEASURED/HARNESS", W.terrain_verdict({"T5": {}, "T10": t10})[0] == "UNMEASURED")
on, off = R(tintVisible="True"), R(tintVisible="False", tintOn="False")
check("A1 off: hidden, strength kept: PASS", W.off_verdict(on, off, "tintVisible", "tint") == ("PASS", "MOD"))
check("can-fail A1 off: still visible: FAIL", W.off_verdict(on, R(tintVisible="True"), "tintVisible", "tint")[0] == "FAIL")
check("can-fail A1 off: the strength moved (a state write, not a picture): FAIL",
      W.off_verdict(on, R(tintVisible="False", tint=0), "tintVisible", "tint")[0] == "FAIL")
check("A1 off: never visible ON (control): UNMEASURED/HARNESS", W.off_verdict(R(tintVisible="False"), off, "tintVisible", "tint")
      == ("UNMEASURED", "HARNESS"))
check("A1 off: visibility unread: UNMEASURED/HARNESS", W.off_verdict(R(tintVisible="unread"), off, "tintVisible", "tint")
      == ("UNMEASURED", "HARNESS"))
b1, b2 = R(hollow=10, waterM=4, tn=0.17, tw=0.17), R(hollow=10, waterM=3, tn=0.34, tw=0.34)
check("A2 widen: 2 m gap wider than 1 m: PASS", W.widen_verdict(b1, b2) == ("PASS", "MOD"))
check("can-fail A2 widen: same width: FAIL", W.widen_verdict(b1, R(hollow=10, waterM=3, tn=0.17, tw=0.17))[0] == "FAIL")
check("can-fail A2 widen: no band at all: FAIL", W.widen_verdict(R(hollow=10, waterM=4, tn=0, tw=0), b2)[0] == "FAIL")
check("A2 widen: a shallow dig: UNMEASURED/SITE", W.widen_verdict(R(hollow=6, waterM=4, tn=0.1, tw=0.1), b2) == ("UNMEASURED", "SITE"))
brim = R(hollow=10, waterM=5, tn=0, tw=0)
check("A2 brim: none: PASS", W.brim_verdict(brim, b1) == ("PASS", "MOD"))
check("can-fail A2 brim: a band: FAIL", W.brim_verdict(R(hollow=10, waterM=5, tn=0.1, tw=0), b1)[0] == "FAIL")
check("A2 brim: the control never read a band: UNMEASURED/HARNESS", W.brim_verdict(brim, R(tn=0)) == ("UNMEASURED", "HARNESS"))
check("A2 off: needs wall faces on: UNMEASURED/SITE",
      W.off_verdict(R(bandVisible="False", facesOn="False", tn=0.34), R(bandVisible="False", tn=0.34), "bandVisible", "tn",
                    needs=("facesOn", "True")) == ("UNMEASURED", "SITE"))
dd = [R(waterM=11, tint=2), R(waterM=7.5, tint=1), R(waterM=4, tint=0)]
check("A3 drawdown: terrain kept, tint follows: PASS", W.drawdown_verdict(dd) == ("PASS", "MOD"))
check("can-fail A3 drawdown: terrain written: FAIL",
      W.drawdown_verdict([dd[0], R(waterM=7.5, tint=1, terrain="RM_WaterChestDeepStill"), dd[2]])[0] == "FAIL")
check("can-fail A3 drawdown: tint frozen at 2: FAIL", W.drawdown_verdict([dd[0], R(waterM=7.5, tint=2), R(waterM=4, tint=2)])[0] == "FAIL")
check("A3 drawdown: the take missed its target: UNMEASURED/SITE", W.drawdown_verdict([dd[0], R(waterM=10.5, tint=2), dd[2]])
      == ("UNMEASURED", "SITE"))
check("A3 drawdown: a step unread: UNMEASURED/HARNESS", W.drawdown_verdict(dd[:2])[0] == "UNMEASURED")
base, a1, a2 = R(key=2, watchKey=2), R(key=1, watchKey=1), R(key=0, watchKey=0)
check("A3 fresh: the watcher re-keyed both times: PASS, stale=False", W.fresh_verdict(base, [a1, a2]) == ("PASS", "MOD", False))
check("can-fail A3 fresh: stale after the 10 m crossing: FAIL, stale=True",
      W.fresh_verdict(base, [R(key=1, watchKey=2), a2]) == ("FAIL", "MOD", True))
check("A3 fresh: baseline key != watch key (blind or unready): UNMEASURED/HARNESS",
      W.fresh_verdict(R(key=2, watchKey=0), [a1, a2])[:2] == ("UNMEASURED", "HARNESS"))
check("A3 fresh: watch key unread: UNMEASURED/HARNESS", W.fresh_verdict(base, [R(key=1, watchKey="unread"), a2])[:2]
      == ("UNMEASURED", "HARNESS"))
check("A3 fresh: no crossing happened: UNMEASURED/SITE", W.fresh_verdict(base, [R(key=2, watchKey=2), a2])[:2] == ("UNMEASURED", "SITE"))
check("every row is A1/A2/A3 of the item", all(r.split("_")[0] in ("A1", "A2", "A3") for r in W.ROW_IDS))
check("pits are disjoint with dry squares between", all(W.PITS[b][0] - W.PITS[a][0] >= 6 for a, b in zip(list(W.PITS), list(W.PITS)[1:])))

# ---- every planted defect lands on its row (mock end to end)
A = {r: ("UNMEASURED", "HARNESS") for r in W.ROW_IDS}
S = {r: ("UNMEASURED", "SITE") for r in W.ROW_IDS}
EXPECT = {"": {}, "old_deploy": A, "no_dig": S,
          "tint_shallow": {"A1_FIVE_METRES_NAVY": ("FAIL", "MOD"), "A3_DRAWDOWN_NO_TERRAIN_WRITE": ("FAIL", "MOD"),
                           "A3_TINT_FRESH_AFTER_DRAWDOWN": ("UNMEASURED", "SITE")},
          "tint_flat": {"A1_TEN_METRES_DARKER": ("FAIL", "MOD"), "A3_DRAWDOWN_NO_TERRAIN_WRITE": ("FAIL", "MOD"),
                        "A3_TINT_FRESH_AFTER_DRAWDOWN": ("UNMEASURED", "SITE")},
          "terrain_write": {"A1_TERRAIN_STILL_WATERDEEP": ("FAIL", "MOD"), "A3_DRAWDOWN_NO_TERRAIN_WRITE": ("FAIL", "MOD")},
          "off_shows": {"A1_OFF_HIDES_TINT": ("FAIL", "MOD")},
          "no_draw": {"A1_OFF_HIDES_TINT": ("UNMEASURED", "HARNESS"), "A2_OFF_HIDES_BAND": ("UNMEASURED", "HARNESS")},
          "faces_off": {"A2_OFF_HIDES_BAND": ("UNMEASURED", "SITE")},
          "band_flat": {"A2_BAND_WIDENS_WITH_GAP": ("FAIL", "MOD")},
          "band_brim": {"A2_BRIM_FULL_NO_BAND": ("FAIL", "MOD")},
          "band_off_shows": {"A2_OFF_HIDES_BAND": ("FAIL", "MOD")},
          "take_terrain": {"A3_DRAWDOWN_NO_TERRAIN_WRITE": ("FAIL", "MOD")},
          "stale": {"A3_TINT_FRESH_AFTER_DRAWDOWN": ("FAIL", "MOD")},
          "blind_watch": {"A3_TINT_FRESH_AFTER_DRAWDOWN": ("UNMEASURED", "HARNESS")}}
check("every fault has an expectation", sorted(k for k in EXPECT if k) == sorted(W.FakeBridge.FAULTS))
tmp = tempfile.mkdtemp()
for fault, want in EXPECT.items():
    out = os.path.join(tmp, "wl_%s.json" % (fault or "clean"))
    with contextlib.redirect_stdout(io.StringIO()):
        W.main(["--mock", out] + (["--mock-faults", fault] if fault else []))
    res = json.load(open(out))
    got = {r["id"]: (r["detail"].get("mock"), r["class"]) for r in res["rows"]}
    bad = {k: v for k, v in got.items() if v[0] != "PASS"}
    check("mock %-14s -> %s" % (fault or "clean", "all PASS" if not want else (sorted(want) if len(want) < 4 else "%d rows" % len(want))),
          bad == want and len(res["rows"]) == len(W.ROW_IDS) and all(r["status"] == "SKIP" for r in res["rows"]))
    if fault == "stale":
        check("stale: the row records stale=True", [r for r in res["rows"] if r["id"] == "A3_TINT_FRESH_AFTER_DRAWDOWN"][0]
              ["detail"].get("stale") is True)
    if fault == "":
        check("clean: settings restored to ON at the end", "tintOn=True bandOn=True" in res.get("settingsAfter", ""))
        check("clean: stale=False recorded", [r for r in res["rows"] if r["id"] == "A3_TINT_FRESH_AFTER_DRAWDOWN"][0]
              ["detail"].get("stale") is False)
out = os.path.join(tmp, "wl_only.json")
with contextlib.redirect_stdout(io.StringIO()):
    W.main(["--mock", out, "--only", "A2_BRIM_FULL_NO_BAND"])
check("--only writes just that row", [r["id"] for r in json.load(open(out))["rows"]] == ["A2_BRIM_FULL_NO_BAND"])
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
