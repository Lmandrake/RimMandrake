"""Offline selftest for rollout_gate.py (NORTHSTAR_SITUATIONAL_ROLLOUT_1). Every pass case has a failing twin."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rollout_gate as G   # noqa: E402

FAILS = []


def check(name, ok):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def rec(verdict="PASS", status="MEASURED", mods=("A", "B"), sha="new", job="situational_rerun", dry=False):
    return {"job": job, "status": status, "verdict": verdict, "dry_run": dry, "failed": [], "finished": "t",
            "evidence": {"run_identity": {"git": {"sha": sha}}, "digests": [{"mod": m} for m in mods]}}


def anc(old, new):
    return {("env", "new"): True, ("env", "old"): False}.get((old, new))


def ev(r, suites=("A", "B"), keys=("A", "B"), dead=()):
    return G.evaluate(r, set(suites), set(keys), list(dead), "env", anc)


def main():
    check("a clean full pass on the current envelope licenses the flip", ev(rec()) == [])
    check("no record is a problem", ev(None) == ["no live situational_rerun record"])
    check("a FAIL record does not license it", any("FAIL" in p for p in ev(rec(verdict="FAIL", status="MEASURED"))))
    check("an UNMEASURED record does not license it", any("UNMEASURED" in p for p in ev(rec(verdict=None, status="UNMEASURED"))))
    check("a pass on an envelope older than the newest change does not", any("predates" in p for p in ev(rec(sha="old"))))
    check("an unrelatable sha is a problem, not a pass", any("cannot relate" in p for p in ev(rec(sha="zzz"))))
    check("a record without a sha is a problem", any("no git sha" in p for p in ev(rec(sha=None))))
    p = ev(rec(mods=("A",)), suites=("A", "B", "C"), keys=("A", "B"))
    check("suites that never ran are named", any("B, C" in x for x in p))
    check("an unregistered missing suite is called out", any("1 of them never recorded" in x for x in p))
    check("a dead registry key is a problem", any("dead registry key" in x for x in ev(rec(), dead=("Gone",))))
    check("extra digests beyond the disk set do not fail", ev(rec(mods=("A", "B", "X"))) == [])
    # latest_rerun: last live rerun wins; dry runs and other jobs are ignored
    rs = [rec(verdict="FAIL"), rec(), rec(verdict="FAIL", dry=True), rec(job="abort_proof", verdict="FAIL")]
    check("latest_rerun takes the last LIVE situational_rerun", G.latest_rerun(rs)["verdict"] == "PASS")
    check("latest_rerun maps the old J1 id", G.latest_rerun([rec(job="J1_situational_rerun")]) is not None)
    check("latest_rerun of nothing is None", G.latest_rerun([rec(dry=True)]) is None)
    # disk_suites / dead_keys over a fake tree
    with tempfile.TemporaryDirectory() as t:
        for tier, mod, body in (("RimMandrake", "Alpha", "suite = Suite('a')\n"), ("RimUtinni", "Beta", "x=1\nsuite=S()\n"),
                                ("RimMandrake", "Script", "def main(): pass\n"), ("RimStarWars", "Gamma", "  suite = 1\n")):
            os.makedirs(os.path.join(t, "src", tier, mod))
            with open(os.path.join(t, "src", tier, mod, "validation.py"), "w") as f:
                f.write(body)
        os.makedirs(os.path.join(t, "infrastructure", "state", "modlists"))
        with open(os.path.join(t, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml"), "w") as f:
            f.write("<ModsConfigData><activeMods><li>ludeon.rimworld</li></activeMods></ModsConfigData>")
        check("disk_suites finds module-level suites in every tier and nothing else",
              G.disk_suites(t) == {"Alpha", "Beta"})
        check("dead_keys names keys with no folder in any tier", G.dead_keys({"Alpha", "Script", "Gone"}, t) == ["Gone"])
    # main(): exit codes from a results file
    with tempfile.TemporaryDirectory() as t:
        empty = os.path.join(t, "r.jsonl")
        open(empty, "w").close()
        check("main exits 2 with no record", G.main(["--results", empty]) == 2)
        bad = os.path.join(t, "b.jsonl")
        with open(bad, "w") as f:
            f.write(json.dumps(rec(verdict="FAIL", mods=())) + "\n")
        check("main exits 1 on a failing record", G.main(["--results", bad]) == 1)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
