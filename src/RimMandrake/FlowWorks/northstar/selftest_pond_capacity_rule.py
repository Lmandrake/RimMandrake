"""selftest_pond_capacity_rule -- offline proof of GOLDEN_PONDS_RECONCILE_TWO_FIFTHS.

The v1 golden site's sidecar recorded D 125 / K 20 / S 80 (5 a square: model 2's LegacyUnitsPerLevel); the live DLL
reported D 50 / K 8 / S 32. This proves the shrink is the SHIPPED rule (sum of RM_Volume.BedLevels x volumePerTile, read
from RM_Volume.cs, never restated), not a body-capacity regression, and that P-S2 / prep_site now say which one a
disagreement is. No game, no bridge."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import site_spec as S  # noqa: E402
import preflight_flowworks as PF  # noqa: E402
import prep_site as PS  # noqa: E402
from northstar_driver import PASS, FAIL  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % str(detail)[:300]))
    if not ok:
        FAILS.append(name)


LIVE_20261024 = {"D_pond": 50, "K_pond": 8, "S_pond": 32}       # preflight P-S2 on v1, 2026-10-24
SIDECAR_V1 = {"D_pond": 125, "K_pond": 20, "S_pond": 80}         # the v1 sidecar (5 a square)


class Stub(object):
    tools = ("jawa/flowworks_body_report",)

    def __init__(self, caps):
        self.caps = caps

    def call(self, tool, **kw):
        name = self.by_probe[(kw["x"], kw["z"])]
        b = self.layout[name]
        n = len(S.cells(b["rect"]))
        return {"success": True, "classified": True, "activeFluid": "RM_Fluid_Water",
                "body": {"id": 1, "limitless": b["limitless"], "cellCount": n, "capacity": self.caps.get(name),
                         "stock": self.caps.get(name), "recededCount": 0}}


def sidecar(caps):
    bodies = {}
    for p in S.PLOTS:
        for b in p["bodies"]:
            if b["limitless"]:
                continue
            n = len(S.cells(b["rect"]))
            bodies[b["name"]] = {"probe": [len(bodies), 0],   # unique: layout rects are plot-relative
                                 "activeFluid": "RM_Fluid_Water",
                                 "record": {"id": 1, "limitless": False, "cellCount": n, "capacity": caps[b["name"]],
                                            "stock": caps[b["name"]], "recededCount": 0}}
    return {"bodies": bodies}


def run_ps2(live, recorded):
    sc = sidecar(recorded)
    st = Stub(live)
    st.layout = {b["name"]: b for p in S.PLOTS for b in p["bodies"]}
    st.by_probe = {tuple(v["probe"]): k for k, v in sc["bodies"].items()}
    return PF.p_s2(st, None, sc)


def main():
    # 1. the shipped rule predicts exactly what the live DLL reported: the 0.4x shrink is intended
    pred = {b["name"]: S.expected_capacity(b) for p in S.PLOTS for b in p["bodies"]}
    check("rule predicts the 2026-10-24 live capacities (D 50, K 8, S 32)",
          all(pred[k] == v for k, v in LIVE_20261024.items()), pred)
    check("limitless C_sea has no predicted budget", pred.get("C_sea") is None, pred)
    legacy = S._rm_volume_const("LegacyUnitsPerLevel")
    body = {b["name"]: b for p in S.PLOTS for b in p["bodies"]}
    check("v1 sidecar is the dead LegacyUnitsPerLevel rule (5 a square), not the shipped one",
          legacy == 5 and all(SIDECAR_V1[k] == legacy * len(S.cells(body[k]["rect"])) != pred[k] for k in SIDECAR_V1),
          (legacy, SIDECAR_V1))

    # 2. P-S2 against the v1 sidecar: FAIL, every pond named STALE SIDECAR, none named MOD
    r = run_ps2(LIVE_20261024, SIDECAR_V1)
    ev = str(r.evidence)
    check("P-S2 v1 sidecar -> FAIL", r.status == FAIL, r)
    check("P-S2 names all three ponds STALE SIDECAR", all("%s STALE SIDECAR" % k in ev for k in SIDECAR_V1), ev)
    check("P-S2 names no MOD regression on the v1 numbers", " MOD:" not in ev, ev)

    # 3. a live capacity off the rule is a MOD regression, whatever the sidecar says
    bad_live = dict(LIVE_20261024, D_pond=20)
    r = run_ps2(bad_live, dict(LIVE_20261024, D_pond=20))
    ev = str(r.evidence)
    check("P-S2 live off the rule -> FAIL naming D_pond MOD", r.status == FAIL and "D_pond MOD" in ev, (r.status, ev))

    # 4. a sidecar re-captured under the shipped rule passes
    r = run_ps2(LIVE_20261024, LIVE_20261024)
    check("P-S2 re-captured sidecar -> PASS", r.status == PASS, r)

    # 5. prep_site never records a capacity off the rule
    st = Stub(bad_live)
    st.layout = {b["name"]: b for p in S.PLOTS for b in p["bodies"]}
    plots = [p for p in S.PLOTS if any(b["name"] == "D_pond" for b in p["bodies"])]
    d = plots[0]["bodies"][0]
    st.by_probe = {(d["rect"][0] + d["rect"][2] // 2, d["rect"][1] + d["rect"][3] // 2): "D_pond"}
    try:
        PS.classify_bodies(st, plots, lambda m: None)
        check("prep refuses a body capacity off the rule", False, "no refusal")
    except PS.Refused as ex:
        check("prep refuses a body capacity off the rule (step 6, names MOD)",
              ex.step == "6" and "MOD" in str(ex), ex)
    st.caps = LIVE_20261024
    try:
        out = PS.classify_bodies(st, plots, lambda m: None)
        check("prep records the on-rule capacity", out["D_pond"]["record"]["capacity"] == 50, out)
    except PS.Refused as ex:
        check("prep records the on-rule capacity", False, ex)

    print("%s  selftest_pond_capacity_rule: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
