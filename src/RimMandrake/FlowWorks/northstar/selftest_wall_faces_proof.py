"""Offline checks for wall_faces_proof.py (WATER_DEPTH_RESKIN_HE_LOOKS_FIRST L3): every pure verdict can go red, and every
FakeBridge fault (a planted defect, including the ca3c9d4a saturation at D4) lands on its expected row. No bridge."""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_wall_faces_proof_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wall_faces_proof as W  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


N, S = [0.12, 0.23, 0.35, 0.50, 0.62], [0.06, 0.11, 0.17, 0.23, 0.29]
good = {p: {"drop": i + 1, "north": N[i], "side": S[i]} for i, p in enumerate(W.LOOKS)}
good["WET"] = dict(good["D3"])


def M(**over):
    d = {k: dict(v) for k, v in good.items()}
    for k, v in over.items():
        d[k] = dict(d[k], **v)
    return d


check("looks: five distinct, wet = D3: PASS", W.looks_verdict(good)[:2] == ("PASS", "MOD"))
check("can-fail looks: 2 m and 2.5 m draw the same face (ca3c9d4a): FAIL", W.looks_verdict(M(D5={"north": 0.50, "side": 0.23}))[0] == "FAIL")
check("can-fail looks: only the side faces tie: FAIL", W.looks_verdict(M(D2={"side": 0.06}))[0] == "FAIL")
check("can-fail looks: a face shrinks with depth: FAIL", W.looks_verdict(M(D3={"north": 0.10}))[0] == "FAIL")
check("can-fail looks: the shallowest face is zero: FAIL", W.looks_verdict(M(D1={"north": 0.0}))[0] == "FAIL")
check("can-fail looks: water ignored, wet draws D5's face: FAIL", W.looks_verdict(M(WET={"drop": 5, "north": 0.62, "side": 0.29}))[0] == "FAIL")
check("can-fail looks: a wrong exposed drop: FAIL", W.looks_verdict(M(D4={"drop": 3}))[0] == "FAIL")
check("looks: a read missing: UNMEASURED/HARNESS", W.looks_verdict(M(D5={"north": None}))[:2] == ("UNMEASURED", "HARNESS"))
F = {"D1": 0.5, "D2": 0.65, "D3": 0.8, "D4": 0.8375, "FL4": 0.8969, "FL8": 0.9428}
check("floors: 0.5..8 m all darker: PASS", W.floors_verdict(F)[:2] == ("PASS", "MOD"))
check("can-fail floors: 4 m == 2 m (ca3c9d4a 0.95 saturation): FAIL", W.floors_verdict(dict(F, D4=0.95, FL4=0.95, FL8=0.95))[0] == "FAIL")
check("can-fail floors: only 8 m == 4 m: FAIL", W.floors_verdict(dict(F, FL8=0.8969))[0] == "FAIL")
check("floors: a read missing: UNMEASURED/HARNESS", W.floors_verdict(dict(F, FL8=None))[:2] == ("UNMEASURED", "HARNESS"))
check("pits are disjoint with dry squares between", all(W.PITS[b][0] - W.PITS[a][0] >= 6 for a, b in zip(list(W.PITS), list(W.PITS)[1:])))
check("drops 0.5, 1, 1.5, 2, 2.5 m and floors 2, 4, 8 m are staged",
      [W.PITS[p][1] for p in W.LOOKS] == [1, 2, 3, 4, 5] and (W.PITS["D4"][1], W.PITS["FL4"][1], W.PITS["FL8"][1]) == (4, 8, 16))
check("site rect holds every pit (x offset + 3 <= 48)", max(dx for dx, *_ in W.PITS.values()) + 3 <= 48)

# ---- the mock's numbers ARE the source's: a FakeBridge drifting from RM_WallFaceMath.cs would prove a world that is not ours
import re  # noqa: E402
SRC = os.path.join(HERE, "..", "Source", "RM_WallFaceMath.cs")
src = open(SRC, encoding="utf-8").read()


def arr(name):
    m = re.search(r"%s\s*=\s*\{([^}]*)\}" % name, src)
    return [float(v.strip().rstrip("fF")) for v in m.group(1).split(",")] if m else None


check("mock NORTH == RM_WallFaceMath.NorthByDrop", arr("NorthByDrop") == W.FakeBridge.NORTH)
check("mock SIDE == RM_WallFaceMath.SideByDrop", arr("SideByDrop") == W.FakeBridge.SIDE)
check("source NorthByDrop/SideByDrop hold five looks past 0 (index 1..5) and rise", all(
    a is not None and len(a) >= 6 and all(y > x for x, y in zip(a[1:6], a[2:6])) for a in (arr("NorthByDrop"), arr("SideByDrop"))))

A = {r: ("UNMEASURED", "HARNESS") for r in W.ROW_IDS}
Sx = {r: ("UNMEASURED", "SITE") for r in W.ROW_IDS}
EXPECT = {"": {}, "old_deploy": A, "blind_math": A, "no_dig": Sx,
          "faces_saturate": {"L3_FIVE_WALL_LOOKS_BY_DROP": ("FAIL", "MOD")},
          "sides_flat": {"L3_FIVE_WALL_LOOKS_BY_DROP": ("FAIL", "MOD")},
          "fill_ignored": {"L3_FIVE_WALL_LOOKS_BY_DROP": ("FAIL", "MOD")},
          "floor_saturate": {"L3_FLOOR_BANDS_PAST_2M": ("FAIL", "MOD")}}
check("every fault has an expectation", sorted(k for k in EXPECT if k) == sorted(W.FakeBridge.FAULTS))
tmp = tempfile.mkdtemp()
for fault, want in EXPECT.items():
    out = os.path.join(tmp, "wf_%s.json" % (fault or "clean"))
    with contextlib.redirect_stdout(io.StringIO()):
        rc = W.main(["--mock", out] + (["--mock-faults", fault] if fault else []))
    res = json.load(open(out))
    got = {r["id"]: (r["detail"].get("mock"), r["class"]) for r in res["rows"]}
    bad = {k: v for k, v in got.items() if v[0] != "PASS"}
    want_rc = 0 if not want else (1 if any(v[0] == "FAIL" for v in want.values()) else 2)
    check("mock %-14s -> %s (exit %d)" % (fault or "clean", sorted(want) or "all PASS", want_rc),
          bad == want and len(res["rows"]) == len(W.ROW_IDS) and all(r["status"] == "SKIP" for r in res["rows"]) and rc == want_rc)
out = os.path.join(tmp, "wf_only.json")
with contextlib.redirect_stdout(io.StringIO()):
    W.main(["--mock", out, "--only", "L3_FLOOR_BANDS_PAST_2M"])
check("--only writes just that row", [r["id"] for r in json.load(open(out))["rows"]] == ["L3_FLOOR_BANDS_PAST_2M"])
print("%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
