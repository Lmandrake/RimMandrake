#!/usr/bin/env python3
"""selftest_greentide_spine.py -- GREENTIDE_BASE_PORT_BUILD_1: greatbole_ladder_static (moved here from
UtinniPatches with RM_CompGreatboleHarvestLadder) and spine_static are green on the shipped mod and go red on every
planted break (in-memory copies of the parsed inputs; the shipped files are never written)."""
import copy
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def main():
    spec = importlib.util.spec_from_file_location("gt_v", os.path.join(HERE, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)

    # ---- the greatbole ladder
    p = v.ladder_parse()
    check("shipped ladder: clean", v.ladder_findings(p) == [], v.ladder_findings(p))
    check("sanity probe: defaults parsed (0.40/0.60/0.70, hysteresis 0.03, catastrophe on)",
          (p["greatboleShakingThreshold"], p["greatboleHealingThreshold"], p["greatboleCatastropheThreshold"], p["hysteresis"], p["catastropheEnabled"]) == (0.4, 0.6, 0.7, 0.03, True))
    S = "RM_GreentideSettings."

    def cs_break(tag, old, new, must):
        q = dict(p)
        assert old in q["_cs"] or old in q["_st"], "planted break target missing: %r" % old
        q["_cs"] = q["_cs"].replace(old, new, 1)
        q["_st"] = q["_st"].replace(old, new, 1)
        got = v.ladder_findings(q)
        check("break ladder: %-44s -> %s" % (tag, must[:34]), any(must in g for g in got), got)

    cs_break("shaking no longer one-shot (armed check gone)", "if (!shakingArmed && fraction", "if (fraction", "ladder source lost")
    cs_break("shaking re-arms with no hysteresis", "fraction < %sgreatboleShakingThreshold - h" % S, "fraction < %sgreatboleShakingThreshold" % S, "ladder source lost")
    cs_break("healing re-announces (flag never set)", "healingAnnounced = true; AnnounceViolentHealing();", "AnnounceViolentHealing();", "ladder source lost")
    cs_break("catastrophe ignores its toggle", "%sgreatboleCatastropheEnabled && fraction" % S, "fraction", "ladder source lost")
    cs_break("catastrophe not marked done first", "catastropheDone = true; IntVec3", "IntVec3", "catastropheDone first")
    cs_break("poll stops honouring catastropheDone", "if (catastropheDone || !parent.Spawned)", "if (!parent.Spawned)", "ladder source lost")
    q = dict(p, greatboleShakingThreshold=0.5)
    check("break ladder: shaking default 0.5 is not the ruled 0.40", any("ruled 0.40" in g for g in v.ladder_findings(q)), v.ladder_findings(q))
    q = dict(p, greatboleHealingThreshold=0.8)
    check("break ladder: healing above catastrophe is not ordered", any("not ordered" in g for g in v.ladder_findings(q)), v.ladder_findings(q))
    cs_break("shaking slider excludes its default", "list.Slider(greatboleShakingThreshold, 0.1f, 0.9f)", "list.Slider(greatboleShakingThreshold, 0.5f, 0.9f)", "outside its slider")
    q = dict(p, hysteresis=0.0)
    check("break ladder: hysteresis 0 lets a one-step dip re-fire shaking", any("hysteresis" in g for g in v.ladder_findings(q)), v.ladder_findings(q))
    q = dict(p, greatboleCatastropheThreshold=0.3)
    check("break ladder: catastrophe threshold below shaking/healing is caught", v.ladder_findings(q) != [])
    check("sim: rising 0..0.9 -> shaking, healing, catastrophe once each, in order",
          [e[0] for e in v.ladder_sim(p, [i / 100.0 for i in range(91)])] == ["shaking", "healing", "catastrophe"])

    # ---- the spine
    defs = v.shipped_defs()
    check("sanity probe: >= 50 shipped defs parsed, RM_Krannock among them", len(defs) >= 50 and ("ThingDef", "RM_Krannock") in defs, len(defs))
    check("shipped spine: clean", v.spine_findings() == [], v.spine_findings())
    got = v.spine_findings(defs=[d for d in defs if d != ("ThingDef", "RM_DryAirBlower")])
    check("break spine: a missing spine def is named", any("RM_DryAirBlower" in g for g in got), got)
    root = v.ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Greentide_Biome.xml")).getroot()
    for tag, path, must in (("roil lock", "biomeMapConditions", "RM_RoilLock"),
                            ("living-bole extension", "modExtensions", "RM_LivingBoleBiomeExtension"),
                            ("roil weather row", "baseWeatherCommonalities", "RM_RoilWeather")):
        r2 = copy.deepcopy(root)
        gt = next(e for e in r2 if e.findtext("defName") == "RM_Greentide")
        parent = gt.find(path)
        for c in list(parent):
            if must in (c.text or "") or must in (c.get("Class") or "") or c.tag == must:
                parent.remove(c)
        got = v.spine_findings(biome_root=r2, defs=defs)
        check("break spine: dropping the %s is named" % tag, any(must in g for g in got), got)

    # ---- the chains through their own Suite
    try:
        import runner
        from northstar_driver.session import FastSession
        from northstar_driver.transport import MockGame, MockTransport
    except ImportError as e:
        print("UNMEASURED  chain runs: %s" % e)
        return 1 if FAILS else 0

    def run(chain_name, patch=None):
        saved = {}
        for k, fn in (patch or {}).items():
            saved[k] = getattr(v, k)
            setattr(v, k, fn)
        try:
            own = v.Suite("Greentide")
            own.toggles = list(v.suite.toggles)
            own.chains = [(n, f) for n, f in v.suite.chains if n == chain_name]
            with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
                res = runner.run_suite(own, s, anchor=None, mod=None)
        finally:
            for k, fn in saved.items():
                setattr(v, k, fn)
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])
    got = run("greatbole_ladder_static")
    check("chain greatbole_ladder_static PASSes on the shipped mod", list(got.values()) == ["PASS"], got)
    got = run("greatbole_ladder_static", {"ladder_parse": lambda: dict(p, hysteresis=0.0)})
    check("chain: a hysteresis break reddens the ladder", list(got.values()) == ["FAIL"], got)
    got = run("spine_static")
    check("chain spine_static PASSes on the shipped mod", list(got.values()) == ["PASS"], got)
    got = run("spine_static", {"spine_findings": lambda: ["planted"]})
    check("chain: a spine finding reddens spine_static", list(got.values()) == ["FAIL"], got)

    if FAILS:
        print("\n%d Greentide spine selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall Greentide spine selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
