#!/usr/bin/env python3
"""selftest_stage6_checks.py - a Stage 6 check goes to a Steve game by its own script, one test per promise of
design/specs/2026-11-24-stage-six-checks-to-steve/boundary.md.

  python3 selftest_stage6_checks.py              every test; exit 1 on any failure
  python3 selftest_stage6_checks.py --mutants    each planted fault must turn the run red; exit 0 only if each does

Temp folders and fakes; no game, ssh, live queue or ledger is touched. The four-mods test reads the committed tables."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TMP = tempfile.mkdtemp(prefix="stage6_checks_")
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils")]
import selftest_steve_idle_takeable as F  # noqa: E402  (sets TESTQ_QUEUE and the other fixture env first)
sys.path.insert(0, HERE)
import proof_build as PB  # noqa: E402
import schema as S  # noqa: E402
import stage6_checks as SC  # noqa: E402
import stage6_site as SS  # noqa: E402
import testq as T  # noqa: E402
import testq_blocks as B  # noqa: E402
import visit_feed as VF  # noqa: E402
import visit_rows as VR  # noqa: E402

FAILS = []
NOW = F.NOW
MODS = ("FlowWorks", "Pyrelands", "ExplosiveKnockback", "GimmeSomeSlack")
FWC = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
EKP = "src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs"
ID = {"mod_sha": "abcdef1", "mod_hash": "sha256:a", "game_build": "1.6", "active_mods": ["x"], "tier": "flowworks"}


def check(ok, msg):
    print("%s  %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def concept(entry="scene_fill_front", **kw):
    return dict({"stage": "6", "kind": "live_minimal", "file": FWC, "entry": entry,
                 "command": "python.exe " + FWC.replace("/", "\\") + " --scene %s --out <json>  (bridge held)" % entry}, **kw)


def ek(scenes, tail=" --ticks 300", entry=None, **kw):
    return dict({"stage": "6", "kind": "live_minimal", "file": EKP, "entry": entry or scenes.split(",")[0],
                 "command": "python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py --scenes %s%s   (proof build)" % (
                     scenes, tail)}, **kw)


# ---- placement ----

def tables():
    out = {}
    for m in MODS:
        out[m] = B.plan(m, ROOT)
    return out


TABLES = {}


def t_each_check_is_placed_once():
    for m in MODS:
        placed = TABLES[m]["placed"]
        ids = [k for k, t in TABLES[m]["tt"]["tests"].items() if isinstance(t, dict) and str(t.get("stage")) == "6"]
        n = {s: sum(1 for v in placed.values() if v[0] == s) for s in (SC.TAKEABLE, SC.NOT_LANE, SC.NO_LOOK)}
        check(set(placed) == set(ids) and sum(n.values()) == len(ids),
              "each-check-is-placed-once: %s: %s of %d checks" % (m, n, len(ids)))
        check(all(isinstance(x, str) and len(x.split()) >= 3 for st, x in placed.values() if st != SC.TAKEABLE),
              "each-check-is-placed-once: %s: each check left out names its cause" % m)


def t_the_four_mods_are_takeable():
    for m in MODS:
        n = sum(1 for v in TABLES[m]["placed"].values() if v[0] == SC.TAKEABLE)
        have = B.blocks_of(TABLES[m]["tt"])
        check(n > 0 and n == len(have), "the-four-mods-are-takeable: %s: %d takeable, %d blocks committed" % (m, n, len(have)))
        fits = [k for k, t in TABLES[m]["tt"]["tests"].items() if isinstance(t, dict) and str(t.get("stage")) == "6"
                and not SC.not_the_lanes(t) and TABLES[m]["placed"][k][0] != SC.NO_LOOK]
        check(sorted(have) == sorted(fits), "the-four-mods-are-takeable: %s: exactly the checks whose tier fits" % m)
        bad = [k for k, b in have.items() if "check" in b and SC._rimflow("build_match") and T.tier_problem(b["check"]["tier"])]
        check(not bad, "the-four-mods-are-takeable: %s: each block's tier is a modset_builder tier %s" % (m, bad[:3]))


def t_a_full_list_check_is_never_sent():
    p = SC.place("FlowWorks", {"a": concept("scene_source_pays"), "b": concept(tier="gimmesomeslack_flowworks")}, root=ROOT)
    check(p["a"][1]["check"]["tier"] == "fw_gss_sitting" and p["b"][1]["check"]["tier"] == "gimmesomeslack_flowworks",
          "the-four-mods-are-takeable: a scene on a site built on another tier, or with a tier of its own, names it")
    p = SC.place("FlowWorks", {"a": concept(kind="live_full"), "b": concept(why_full_list="the walk"),
                               "c": concept(kind="look"), "d": concept()}, root=ROOT)
    check([p[k][0] for k in "abcd"] == [SC.NOT_LANE] * 3 + [SC.TAKEABLE], "a-full-list-check-is-never-sent: %s" % {
        k: v[0] for k, v in p.items()})
    p = SC.place("FlowWorks", {"a": concept(kind="live_full")}, {"a": ["some_chain"]}, root=ROOT)
    check(p["a"][0] == SC.NOT_LANE, "a-full-list-check-is-never-sent: not by a chain either")
    p = SC.place("ExplosiveKnockback", {"a": ek("barrage", "   (a game on Archmagi; any list)")}, root=ROOT)
    check(p["a"][0] == SC.NOT_LANE, "a-full-list-check-is-never-sent: a check bound to an Archmagi game stays there")


def t_no_entry_point_is_could_not_look():
    p = SC.place("FlowWorks", {"gone": concept(file="src/RimMandrake/FlowWorks/nope.py"), "flag": concept(entry_exists=False),
                               "none": concept(file=None), "noread": concept(file="src/RimMandrake/FlowWorks/validation.py",
                                                                              command="python.exe x.py")}, root=ROOT)
    check(all(v[0] == SC.NO_LOOK for v in p.values()), "no-entry-point-is-could-not-look: %s" % {k: v[0] for k, v in p.items()})
    check("not on disk" in p["gone"][1] and "does not exist" in p["flag"][1] and "no program" in p["noread"][1],
          "no-entry-point-is-could-not-look: each names its cause")
    got, why = B.derive("FlowWorks", {"gone": concept(file="src/RimMandrake/FlowWorks/nope.py")}, [], {}, ROOT)
    check(got["gone"] is None and why["gone"].startswith("could not look: "), "no-entry-point-is-could-not-look: derive says it")


def t_a_paused_raid_is_never_sent():
    raid = concept(stages_raid="a raid")
    check(SC.place("FlowWorks", {"a": raid}, root=ROOT, paused=True)["a"][0] == SC.NOT_LANE,
          "a-paused-raid-is-never-sent: paused")
    check(SC.place("FlowWorks", {"a": raid}, root=ROOT, paused=False)["a"][0] == SC.TAKEABLE,
          "a-paused-raid-is-never-sent: sent again when the pause is lifted")


# ---- the runner and its readers ----

def fake_run(mod, tier, specs, script):
    """SC.run with a fake shell: SCRIPT(line, out path) -> (rc, text) and may write the result file."""
    lines = []
    real = SC.wpath
    SC.wpath = lambda p: p

    def sh(line, log, timeout):
        lines.append(line)
        open(log, "a").write(line + "\n")
        base = log[:-4] + ".json"
        return script(line, base)
    try:
        d = tempfile.mkdtemp(dir=TMP)
        return SC.run(mod, tier, list(specs), d, 7200, ROOT, sh_=sh, tests=specs), lines
    finally:
        SC.wpath = real


def concept_json(status, rows, verified=True, error=None):
    def script(line, out):
        d = {"status": status, "site": {"verified": verified}, "rows": [{"id": i, "status": s, "detail": "d"} for i, s in rows]}
        if error:
            d["error"] = error
        json.dump(d, open(out, "w"))
        return (0 if status == "PASS" else 1), "x"
    return script


def one(script):
    rows, _ = fake_run("FlowWorks", "flowworks", {"c": concept()}, script)
    return rows["c"]["verdict"]


def t_the_verdict_is_the_checks_own_row():
    n = "the-verdict-is-the-checks-own-row: "
    check(one(concept_json("PASS", [("a", "PASS")])) == "PASS", n + "a scene whose rows pass is PASS")
    check(one(concept_json("FAIL", [("a", "PASS"), ("b", "FAIL")])) == "FAIL", n + "a failed row is FAIL")
    check(one(concept_json("FAIL", [("a", "PASS"), ("b", "UNMEASURED")])) == "UNMEASURED", n + "an unstaged scene is UNMEASURED")
    check(one(concept_json("FAIL", [], error="boom")) == "UNMEASURED", n + "no rows and an error is UNMEASURED")
    check(one(concept_json("PASS", [("a", "PASS")], verified=False)) == "UNMEASURED", n + "an unverified site is UNMEASURED")
    check(one(concept_json("FAIL", [("a", "FAIL")], verified=False)) == "UNMEASURED", n + "also for a FAIL")
    check(one(lambda line, out: (1, "Traceback")) == "UNMEASURED", n + "a crash with no result file is UNMEASURED")
    check(one(lambda line, out: (None, "")) == "UNMEASURED", n + "a timeout is UNMEASURED")

    def ekrun(lines, rc=0):
        def script(line, out):
            if "live_site" in line:
                return 0, "READY"
            if "stage6_site" in line:
                return 0, 'SITE_JSON {"biome": "AridShrubland"}\n'
            return rc, "\n".join(lines)
        rows, _ = fake_run("ExplosiveKnockback", "explosiveknockback_visit", {"e": ek("a_scene,a_control")}, script)
        return rows["e"]["verdict"]
    check(ekrun(["a_scene  PASS x", "a_control  PASS y"]) == "PASS", n + "each scene and its control pass: PASS")
    check(ekrun(["a_scene  PASS x"]) == "UNMEASURED", n + "a control with no line is UNMEASURED")
    check(ekrun(["a_scene  PASS x", "a_control  FAIL y"], 1) == "FAIL", n + "a failed control is FAIL")
    check(ekrun(["a_scene  INVALID x", "a_control  PASS y"], 1) == "UNMEASURED", n + "INVALID (the runner exits 1) is UNMEASURED")
    check(ekrun(["a_scene  ERROR x", "a_control  PASS y"], 1) == "UNMEASURED", n + "ERROR is UNMEASURED")
    check(ekrun(["PROOF BUILD REQUIRED: the release build"], 3) == "UNMEASURED", n + "the release DLL is UNMEASURED")
    rows, _ = fake_run("ExplosiveKnockback", "explosiveknockback_visit", {"e": ek("a_scene")},
                       lambda line, out: (2, "NOT READY: no map"))
    check(rows["e"]["verdict"] == "UNMEASURED" and "site not made" in rows["e"]["detail"], n + "no site, no verdict")
    rows, lines = fake_run("FlowWorks", "gimmesomeslack", {"c": concept()}, concept_json("PASS", [("a", "PASS")]))
    check(rows["c"]["verdict"] == "UNMEASURED" and not lines, n + "a check of another tier never runs on this load")

    def interleaved(line, out):
        if "live_site" in line:
            return 0, "READY"
        if "stage6_site" in line:
            return 0, 'SITE_JSON {"biome": "AridShrubland"}[bridge split] 0.3 s wall'
        return 0, "a_scene  PASS x"
    check(fake_run("ExplosiveKnockback", "explosiveknockback_visit", {"e": ek("a_scene")}, interleaved)[0]["e"]["verdict"] == "PASS",
          n + "a site line with another line glued to it still reads (Steve2, 2026-11-24)")
    log = os.path.join(TMP, "x.log")
    rc, text = SC.sh("echo one; echo noise >&2; echo two; echo Traceback >&2; exit 3", log, 60)
    check(rc == 3 and text.startswith("one\ntwo\n") and "noise" in text[text.index("--- stderr"):],
          n + "stderr never breaks a row's line: it comes after stdout (%r)" % text)
    check(SC.sh("sleep 5", log, 1)[0] is None, n + "a command past its time is ended and said")

    def walk(text, rc):
        def script(line, out):
            if "live_site" in line:
                return 0, "READY"
            if "stage6_site" in line:
                return 0, 'SITE_JSON {"biome": "AridShrubland"}\n'
            return (0, "STAGED S\n") if "stage_walk" in line else (rc, text)
        spec = {"stage": "6", "kind": "live_minimal", "file": "src/RimMandrake/ExplosiveKnockback/validation.py",
                "entry": "walk_storeroom_raid", "command": "python.exe src\\RimMandrake\\ExplosiveKnockback\\proof\\stage_walk_colony"
                ".py --save S   then   python.exe src\\RimMandrake\\ExplosiveKnockback\\validation.py --live walk_storeroom_raid "
                "--storeroom 1,2,3,4 --cover 1,2 --gas 3,4 --save S --frame-pairs 21"}
        return fake_run("ExplosiveKnockback", "explosiveknockback_visit", {"w": spec}, script)[0]["w"]["verdict"]
    check([walk("ROW STATUS DETAIL\nFRAME_BUDGET PASS x\n", 0), walk("FRAME_BUDGET FAIL x\n", 1),
           walk("FRAME_BUDGET UNMEASURED x\n", 1), walk("REFUSED walk", 2)] == ["PASS", "FAIL", "UNMEASURED", "UNMEASURED"],
          n + "the walk leaf's rows are read")
    spec = {"P_GS1_on": {"entry": "GS1_x_gravship_on_y"}}
    gj = os.path.join(TMP, "g.json")

    def grav(rows, rc, text=""):
        if rows is None:
            os.path.exists(gj) and os.remove(gj)
        else:
            json.dump({"rows": [{"id": i, "status": s, "detail": {}} for i, s in rows]}, open(gj, "w"))
        return SC.read_rowfile(["P_GS1_on"], spec, text, [rc], gj)["P_GS1_on"][0]
    check([grav([("GS1_x_gravship_on_y", "PASS")], 0), grav([("GS1_x_gravship_on_y", "FAIL")], 1), grav(None, 1, "GovernorStop"),
           grav([("GS2", "PASS")], 1), grav([("GS1_x_gravship_on_y", "UNMEASURED")], 2)] == [
               "PASS", "FAIL", "UNMEASURED", "UNMEASURED", "UNMEASURED"],
          n + "a flight's verdict is its own row, never its exit code (a stop exits 1 too)")
    r = SC.read_exit012(["p"], {"p": {}}, "Traceback (most recent call last):\nX", [1], None)
    check(r["p"][0] == "UNMEASURED" and SC.read_exit012(["p"], {"p": {}}, "no", [0, 1], None)["p"][0] == "FAIL"
          and SC.read_exit012(["p"], {"p": {}}, "no", [0, 2], None)["p"][0] == "UNMEASURED", n + "exit 1 from a crash is no FAIL")
    check(SS.judge({"biome": "X", "hostile": []}, "X") is None and SS.judge({"biome": "X", "hostile": ["Pirate"]}, "X")
          and SS.judge({}, None) and SS.judge({"biome": "Y"}, "X"), n + "a site with a hostile, no map or another biome is refused")


def gss(tid, entry, **kw):
    f = "src/RimMandrake/GimmeSomeSlack/"
    cmd = "python3 %snorthstar/proof_all.py --live" % f if tid.startswith("P_") else f + "validation.py"
    return dict({"stage": "6", "kind": "live_minimal", "file": f + "validation.py", "entry": entry, "command": cmd}, **kw)


def t_one_run_serves_all_its_checks():
    specs = {"P_A": gss("P_A", "A"), "P_B": gss("P_B", "B"), "P_GONE": gss("P_GONE", "GONE"),
             "sc_walls": gss("sc_walls", "scene_walls", tier="gimmesomeslack")}

    def script(line, out):
        if "proof_all" in line:
            json.dump({"rows": [{"id": i, "status": s} for i, s in (("P1_map", "PASS"), ("P3_pin", "PASS"), ("A", "PASS"),
                                                                   ("B", "FAIL"))]}, open(out, "w"))
            return 1, "done"
        open(out + ".scenes", "w").write("sc_walls                 PASS       A=PASS\n")
        return 1, ""
    rows, lines = fake_run("GimmeSomeSlack", "gimmesomeslack", specs, script)
    check(all("--skip-offline" in x for x in lines if "proof_all" in x),
          "one-run-serves-all-its-checks: the lane's proof skips the offline gate (its C# selftest passed 15 min there)")
    p = SC.place("GimmeSomeSlack", {"sc_spans": gss("sc_spans", "scene_spans", tier="gimmesomeslack")}, root=ROOT)
    check(p["sc_spans"][0] == SC.NO_LOOK and "offline gate" in p["sc_spans"][1],
          "no-entry-point-is-could-not-look: a scene that reads offline-gate rows is not sent (%s)" % p["sc_spans"][1])
    p = SC.place("GimmeSomeSlack", {"sc_gravship": gss("sc_gravship", "scene_gravship", tier="gimmesomeslack"),
                                    "P_SC_under_liquid_pit": gss("P_SC_under_liquid_pit", "SC_under_liquid_pit")}, root=ROOT)
    check(p["sc_gravship"][0] == SC.NO_LOOK and p["P_SC_under_liquid_pit"][1]["check"]["tier"] == "gimmesomeslack_flowworks",
          "no-entry-point-is-could-not-look: a scene of rows from two runs is not sent; a pit row goes to the FlowWorks tier (%s)" % p)
    check(sum("proof_all" in x for x in lines) == 1, "one-run-serves-all-its-checks: the proof ran once")
    check({k: v["verdict"] for k, v in rows.items()} == {"P_A": "PASS", "P_B": "FAIL", "P_GONE": "UNMEASURED", "sc_walls": "PASS"},
          "one-run-serves-all-its-checks: each check its own row %s" % {k: v["verdict"] for k, v in rows.items()})
    check(all(rows[k]["site"] for k in specs), "one-run-serves-all-its-checks: the proof's verified site is on the row")


# ---- the job and the worker ----

def t_the_job_form_is_checked():
    ok = dict(profile="tier:flowworks", lane="stevedesktop")
    j = S.make_job("FlowWorks", {"checks": ["sc_a"]}, "commission", "BENCH", "abcdef1", visit=9, proof_build=["FlowWorks"], **ok)
    check(S.is_checks(j) and not S.is_proofs(j) and S.tier_of(j) == "flowworks", "the-job-form-is-checked: a sound job is made")

    def bad(sel, **kw):
        try:
            S.make_job("FlowWorks", sel, "commission", "BENCH", "abcdef1", **kw)
            return False
        except S.SchemaError:
            return True
    check(bad({"checks": ["sc_a"]}) and bad({"checks": ["sc_a"]}, profile="tier:x", lane="any")
          and bad({"checks": ["a"], "chains": ["b"]}, **ok) and bad({"checks": ["a"]}, visit=0, **ok),
          "the-job-form-is-checked: no tier, another lane, a second key and a bad visit are refused")

    class A:
        mod, profile, deploy, proof_build = "ExplosiveKnockback", None, ["FlowWorks"], None
    a = A()
    check(T.fill_checks(a, ["sc_mortar_throw"]) is None and a.profile == "tier:explosiveknockback_visit"
          and a.proof_build == ["ExplosiveKnockback"], "the-job-form-is-checked: the tier and the proof build are filled in")
    check("not the lane's" in (T.fill_checks(A(), ["sc_barrage_perf"]) or ""), "the-job-form-is-checked: a check that is not the lane's is refused")


def worker():
    d = os.path.join(ROOT, "infrastructure", "stevedesktop")
    if d not in sys.path:
        sys.path.insert(0, d)
    import worker as W
    return W


def attempt(W, job, sh):
    a = W.Attempt.__new__(W.Attempt)
    a.d = tempfile.mkdtemp(dir=TMP)
    a.job, a.res, a.game_pid, a.aid = job, {"artifacts": [], "tier": {"exact": True, "running": ["x"]}, "rows": []}, None, "x.a1"
    a.sh, a.game_gone, a.say, a.mods_dir, a.cmd_down = sh, (lambda: None), (lambda m: None), (lambda: "/mods"), (lambda: "down")
    return a


def t_the_worker_publishes_each_check():
    W = worker()
    n = "the-worker-publishes-each-check: "
    j = S.make_job("FlowWorks", {"checks": ["sc_a", "sc_b", "sc_c"]}, "commission", "BENCH", "abcdef1",
                   profile="tier:flowworks", lane="stevedesktop")
    seen = []

    def sh(cmd, log_name=None, timeout=None):
        seen.append(cmd)
        out = cmd.split("--out ")[1].split()[0]
        os.makedirs(out)
        json.dump({"identity": ID, "rows": {"sc_a": {"verdict": "PASS", "detail": "ok", "site": {"x": 1}, "command": "c"},
                                            "sc_b": {"verdict": "WEIRD", "detail": "?"}}}, open(os.path.join(out, "checks.json"), "w"))
        return 0, ""
    a = attempt(W, j, sh)
    ok = a.run_checks()
    check(ok and a.res["outcome"] == "DONE" and [(r["row"], r["verdict"]) for r in a.res["rows"]] == [
        ("sc_a", "PASS"), ("sc_b", "UNMEASURED"), ("sc_c", "UNMEASURED")], n + "one row each, only PASS and FAIL are verdicts")
    check(a.res["checks"]["identity"] == ID and a.res["checks"]["rows"]["sc_a"]["site"] == {"x": 1}, n + "identity and site travel")
    check("--mod FlowWorks" in seen[0] and "--tier flowworks" in seen[0], n + "the runner gets the mod and the tier")
    a = attempt(W, j, lambda *x, **k: check(False, n + "nothing runs off the tier"))
    a.res["tier"] = {"exact": False, "why": "WRONG_TIER"}
    check(a.run_checks() is False and (a.res["outcome"], a.res["cause"]) == ("INVALID", "LOAD")
          and {r["verdict"] for r in a.res["rows"]} == {"UNMEASURED"} and len(a.res["rows"]) == 3, n + "off the tier: INVALID/LOAD")
    a = attempt(W, j, lambda *x, **k: (1, "boom"))
    check(a.run_checks() is False and (a.res["outcome"], a.res["cause"]) == ("INVALID", "HARNESS"), n + "no record: INVALID/HARNESS")
    src = open(os.path.join(ROOT, "infrastructure", "stevedesktop", "worker.py")).read()
    check("self.run_checks if S.is_checks(self.job)" in src, n + "run() routes a checks job to it")
    b = dict(W.base_result(j["id"], j["id"] + ".a1", "abcdef1"), outcome="DONE", checks=a.res.get("checks") or {"identity": ID})
    check(W.contract_errors(b) == [], n + "the result contract accepts it")


def t_the_proof_build_never_touches_the_clone():
    n = "the-proof-build-never-touches-the-clone: "
    root, mods = tempfile.mkdtemp(dir=TMP), tempfile.mkdtemp(dir=TMP)
    src = os.path.join(root, "src", "RimMandrake", "Ek")
    os.makedirs(os.path.join(src, "Assemblies"))
    os.makedirs(os.path.join(mods, "Ek", "Assemblies"))
    open(os.path.join(src, "x.csproj"), "w").write("<RmProofs/>")
    for p in (os.path.join(src, "Assemblies", "Ek.dll"), os.path.join(mods, "Ek", "Assemblies", "Ek.dll")):
        open(p, "w").write("release")

    class WB:
        args, rc = None, 0

        @staticmethod
        def find_csproj(mod):
            return os.path.join(src, "x.csproj")

        @classmethod
        def stage_build(cls, csproj, config, extra, stage_name=None):
            cls.args = (extra, stage_name)
            stage = tempfile.mkdtemp(dir=TMP)
            d = os.path.join(stage, "src", "RimMandrake", "Ek", "Assemblies")
            os.makedirs(d)
            open(os.path.join(d, "Ek.dll"), "w").write("proof")
            rec = {"stage": stage, "outputs": []}
            cls._copy_back([os.path.join(d, "Ek.dll")], stage, rec)
            return cls.rc, rec

        @staticmethod
        def _copy_back(outs, stage, record, staged_in=None):
            shutil.copy(outs[0], os.path.join(src, "Assemblies", "Ek.dll"))      # what winbuild does by default
            record["outputs"].append(os.path.relpath(outs[0], stage))
    with redirect_stdout(io.StringIO()):
        rc = PB.main(["--mod", "Ek", "--mods-dir", mods], WB=WB, root=root)
    check(rc == 0 and WB.args == (["-p:RmProofs=true"], "Ek_proof"), n + "built with RmProofs in its own stage (%s)" % (WB.args,))
    check(open(os.path.join(mods, "Ek", "Assemblies", "Ek.dll")).read() == "proof", n + "the game gets the proof DLL")
    check(open(os.path.join(src, "Assemblies", "Ek.dll")).read() == "release", n + "the clone's Assemblies are byte-identical")
    WB.rc = 1
    with redirect_stdout(io.StringIO()):
        check(PB.main(["--mod", "Ek", "--mods-dir", mods], WB=WB, root=root) == 2, n + "a failed build exits 2")
    WB.rc = 0
    with redirect_stdout(io.StringIO()):
        check(PB.main(["--mod", "Ek", "--mods-dir", tempfile.mkdtemp(dir=TMP)], WB=WB, root=root) == 3, n + "no release there exits 3")
    W = worker()
    j = S.make_job("ExplosiveKnockback", {"checks": ["sc_a"]}, "commission", "BENCH", "abcdef1",
                   profile="tier:explosiveknockback_visit", lane="stevedesktop", proof_build=["ExplosiveKnockback"])
    cmds = []
    a = attempt(W, j, lambda c, **k: (cmds.append(c), (0, ""))[1])
    check(a.deploy_proof() is True and cmds[0] == "down" and "proof_build.py --mod ExplosiveKnockback --mods-dir /mods" in cmds[1],
          n + "the worker stops the game, then builds (%s)" % cmds)
    a = attempt(W, j, lambda c, **k: (0, "") if c == "down" else (2, "NOT BUILT"))
    check(a.deploy_proof() is False and (a.res["outcome"], a.res["cause"]) == ("INVALID", "DEPLOY"), n + "a failed build is INVALID/DEPLOY")
    forgot = []

    class M:
        game_sig = staticmethod(lambda *x: {"s": 1})
        forget = staticmethod(lambda p: forgot.append(p))
        save = staticmethod(lambda *x: forgot.append("SAVED"))
    a = attempt(W, j, None)
    a._memo = (M, "memo.json", {"mods": []}, None)
    a.memo_save({"ExplosiveKnockback": {}})
    check(forgot == ["memo.json"], n + "a proof DLL is never the deploy memo, so the next job deploys the release (%s)" % forgot)


# ---- the feed ----

def feed(scripts, recs=()):
    blk = {"FlowWorks": dict(F.entry(9, NOW - 3600, {}), scripts=scripts)}
    return VF.waiting_scripts(NOW, blk, list(recs))


def rec(checks, verdicts, outcome="DONE", cause=None, fin=NOW - 100, mod="FlowWorks"):
    return {"job": {"id": "J1", "mod": mod, "selector": {"checks": checks}, "requested_by": "BENCH.visit"},
            "result": {"outcome": outcome, "cause": cause, "finished": F.iso(fin),
                       "rows": [{"chain": "checks", "row": k, "verdict": v} for k, v in verdicts.items()]}}


def t_the_feed_sends_one_tier_at_a_time():
    n = "the-feed-sends-one-tier-at-a-time: "
    fw = {"tier": "flowworks", "build": "release"}
    w, _, _ = feed({"a": fw, "b": fw, "c": {"tier": "gss", "build": "release"}})
    check(sorted(w["FlowWorks"]["groups"]) == [("flowworks", "release"), ("gss", "release")], n + "checks group by tier and build")
    w, _, _ = feed({"a": fw, "b": fw}, [rec(["a", "b"], {"a": "PASS", "b": "FAIL"}, fin=NOW - 3000)])
    check(w == {}, n + "a check that read PASS or FAIL since the opening is not sent again")
    w, _, _ = feed({"a": fw}, [rec(["a"], {"a": "PASS"}, fin=NOW - 7200)])
    check("FlowWorks" in w, n + "a run before the opening drains nothing")
    w, _, bo = feed({"a": fw}, [rec(["a"], {"a": "UNMEASURED"})])
    check(w == {} and bo["FlowWorks"]["a"] > 0, n + "a check that could not look waits (%s)" % bo)
    _, _, b2 = feed({"a": fw}, [rec(["a"], {"a": "UNMEASURED"}), rec(["a"], {"a": "UNMEASURED"}, fin=NOW - 900)])
    check(b2["FlowWorks"]["a"] > bo["FlowWorks"]["a"], n + "and doubles its wait")
    w, _, _ = feed({"a": fw}, [rec(["a"], {"a": "UNMEASURED"}, fin=NOW - 3000)])
    check("FlowWorks" in w, n + "and is sent again after it")
    w, sp, _ = feed({"a": fw}, [rec(["a"], {}, "REFUSED", "PREFLIGHT"), rec(["a"], {}, "REFUSED", "PREFLIGHT")])
    check(w == {} and sp["FlowWorks"]["a"] == 2, n + "two refusals of the job's own form spend it (%s)" % sp)
    for k, v in (("held", True), ("blocked", ["x"]), ("owed", "exit met")):
        e = dict(F.entry(9, NOW - 3600, {}), scripts={"a": fw}, **{k: v})
        check(VF.waiting_scripts(NOW, {"FlowWorks": e}, [])[0] == {}, n + "%s sends nothing" % k)
    tests = TABLES["FlowWorks"]["tt"]["tests"]
    ids = [k for k, b in B.blocks_of(TABLES["FlowWorks"]["tt"]).items() if "check" in b]
    got = VF.pick_checks("FlowWorks", {("flowworks", "release"): sorted(ids)}, ROOT, 2)
    check(len(got) == 2 and set(got) <= set(tests), n + "a job holds at most its runs (%s)" % got)
    g = sorted(k for k, b in B.blocks_of(TABLES["GimmeSomeSlack"]["tt"]).items() if (b.get("check") or {}).get("tier") == "gimmesomeslack"
               and (k.startswith("P_MX")))
    got = VF.pick_checks("GimmeSomeSlack", {("gimmesomeslack", "release"): g}, ROOT, 1)
    check(got == g and len(g) > 5, n + "checks of one run go together (%d)" % len(got))
    sent = []

    class FT:
        REPO = ROOT

        @staticmethod
        def cmd_submit(a):
            sent.append(a)
            print(json.dumps({"job": "J9"}))
            return 0

        @staticmethod
        def log(m):
            pass
    out = VF._send_scripts(FT, "FlowWorks", {"visit": 9, "opened": NOW, "groups": {("flowworks", "release"): sorted(ids)[:1]}},
                           "abcdef1", False, {})
    check(out["state"] == "queued" and sent[0].visit == 9 and sent[0].checks == sorted(ids)[0] and sent[0].chains is None
          and sent[0].by == "BENCH.visit", n + "the job carries its visit and its checks")


def t_the_filler_does_not_repeat_a_chain_in_flight():
    import gaps
    seen = {}
    keep = (gaps.rank, T.repeat_holds, T.chain_history, T.records)

    def rank(mod, n, now, recs, dry, exclude=()):
        seen["x"] = set(exclude)
        return dict({k: None for k in ("rank", "purpose", "row_items", "held", "ident", "flaky", "why")}, dry=[], blind=[],
                    counts={"never_run": 1}, all_dry=False, text="t")
    run = {"job": {"id": "J1", "mod": "Pyrelands", "selector": {"chains": ["burrowers"]}}}
    other = {"job": {"id": "J2", "mod": "FlowWorks", "selector": {"chains": ["swept"]}}}
    pend = {"schema": S.JOB_SCHEMA, "id": "J3", "mod": "Pyrelands", "selector": {"chains": ["firehawk"]}}
    try:
        gaps.rank, T.repeat_holds, T.chain_history = rank, (lambda *a: {}), (lambda *a: {})
        T.records = lambda st: {"running": [run, other], "pending": [pend]}.get(st, [])
        T.fill_rank("Pyrelands", 4, NOW)
    finally:
        gaps.rank, T.repeat_holds, T.chain_history, T.records = keep
    check(seen.get("x") == {"burrowers", "firehawk"},
          "the-filler-does-not-repeat-a-chain-in-flight: chains that run or wait for the mod are left out (%s)" % seen.get("x"))


# ---- the rows ----

def vrec(verdicts, outcome="DONE", identity=ID, visit=9, host="stevedesktop.b"):
    r = rec(list(verdicts), verdicts, outcome, None if outcome == "DONE" else "LOAD", mod="FlowWorks")
    r["job"].update(id="J20261124T000000Z-aaaaaa", visit=visit)
    r["result"].update(host=host, attempt="J20261124T000000Z-aaaaaa.a1",
                       checks={"identity": identity, "rows": {k: {"site": {"s": 1}, "held": ["x"], "command": "c"} for k in verdicts}})
    return r


TAB = {"sc_a": {"stage": "6"}, "sc_b": {"stage": "6"}, "sc_c": {"stage": "6"}, "ch": {"stage": "6", "testq": {"chains": ["z"]}}}


def t_a_visit_row_is_written_once():
    n = "a-visit-row-is-written-once: "
    root = tempfile.mkdtemp(dir=TMP)
    d = os.path.join(root, "design", "concepts", "FlowWorks", "version")
    os.makedirs(d)
    json.dump({"tests": TAB}, open(os.path.join(d, "test_table.json"), "w"))
    real, realt = VR._rf, VR.tier_lists
    VR.tier_lists = lambda: (lambda t: (ID["active_mods"], None))

    class M:
        stage, opens = "in_game", 9

        @classmethod
        def load(cls, root, mod):
            return {"stage": cls.stage}

        @classmethod
        def ingame_openings(cls, rec):
            return {i: "t" for i in range(cls.opens)}
    VR._rf = lambda name: M if name == "maturation" else real(name)
    try:
        a = VR.ingest(vrec({"sc_a": "PASS", "sc_b": "FAIL"}), root)
        b = VR.ingest(vrec({"sc_a": "PASS", "sc_b": "FAIL"}), root)
        p = os.path.join(d, "in_game", "visit_9", "rows.jsonl")
        rows = [json.loads(x) for x in open(p)]
        check((a["visit_rows"], b["visit_rows"], len(rows)) == (2, 0, 2), n + "two rows, once (%s %s)" % (a, b))
        r = {x["test"]: x for x in rows}
        check(r["sc_a"]["verdict"] == "PASS" and r["sc_a"]["outcome"] == "SUCCESS" and r["sc_a"]["game"] == "Steve2"
              and r["sc_a"]["site_checked"] and r["sc_a"]["site"] and r["sc_a"]["held"] == ["x"]
              and all(r["sc_a"][k] == v for k, v in ID.items()), n + "game, site, held and build identity are on the row")
        open(p, "a").write('{"test": "by_hand"}')                # a torn last line is not glued to ours
        VR.write(os.path.dirname(p), [{"job": "J2", "test": "sc_a"}])
        check(len(open(p).read().splitlines()) == 4, n + "a row never joins a torn line")
        x = VR.ingest(vrec({"sc_c": "UNMEASURED"}, "INVALID"), root)
        check(x["visit_rows"] == 0 and "INVALID" in x["no_look"] and len(open(p).read().splitlines()) == 4,
              n + "a job that ended before it ran is no run of its checks: no row (%s)" % x)
        M.opens = 10
        check(VR.ingest(vrec({"sc_c": "PASS"}), root)["visit_rows"] == 0, n + "a visit that moved on gets no row")
        M.opens, M.stage = 9, "passed"
        check(VR.ingest(vrec({"sc_c": "PASS"}), root)["visit_rows"] == 0, n + "a closed visit gets no row")
        check(VR.ingest(vrec({"sc_c": "PASS"}, visit=None), root) is None, n + "a job of no visit writes nothing")
    finally:
        VR._rf, VR.tier_lists = real, realt
    src = open(os.path.join(HERE, "ingest.py")).read()
    check("VR.ingest(rec, REPO)" in src and "visit_row_paths(git) if shard_rel" in src, n + "ingest writes and lands them")
    check("visit_*/rows.jsonl merge=union" in open(os.path.join(ROOT, ".gitattributes")).read(), n + "the lane and a driver append to one file")


def t_a_lane_row_never_opens_a_visit():
    n = "a-lane-row-never-opens-a-visit: "
    M = VR._rf("maturation")
    root = tempfile.mkdtemp(dir=TMP)
    d = os.path.join(root, "design", "concepts", "FlowWorks", "version", "in_game", "visit_9")
    state = lambda: M.read_ingame_exit(root, "FlowWorks", 9, {"tests": TAB})["state"]
    VR.write(d, VR.rows_of(vrec({"sc_a": "PASS", "sc_b": "FAIL"}), TAB, ID))
    check(len(open(os.path.join(d, "rows.jsonl")).read().splitlines()) == 2 and state() == "absent",
          n + "the rows that the lane writes open no visit: the driver is still owed (%s)" % state())
    with open(os.path.join(d, "rows.jsonl"), "a") as f:
        f.write('{"test": "sc_a", "verdict": "PASS"}\n')
    check(state() == "no_exit_block", n + "a driver's row beside them is a record (%s)" % state())


def t_could_not_look_never_replaces_a_row():
    n = "could-not-look-never-replaces-a-row: "
    LK = SC._rimflow("live_kinds")

    def rows(r):
        return {x["test"]: x for x in VR.rows_of(r, TAB, VR.identity_of(r["result"]))}
    for label, r in (("UNMEASURED", vrec({"sc_a": "UNMEASURED"})), ("INVALID job", vrec({"sc_a": "PASS"}, "INVALID")),
                     ("no identity", vrec({"sc_a": "PASS"}, identity=None)),
                     ("an identity with a fault", vrec({"sc_a": "PASS"}, identity=dict(ID, why=["x"]))),
                     ("an identity without a hash", vrec({"sc_a": "PASS"}, identity=dict(ID, mod_hash=None)))):
        x = rows(r)["sc_a"]
        check(x["verdict"] == "COULD NOT LOOK" and LK.spoiled(x) and LK.later({"test": "sc_a", "verdict": "PASS"}, x)["verdict"] == "PASS",
              n + "%s" % label)
    tiers = lambda t: (["x", "cherry"], None) if t == "flowworks" else (None, "no tier")
    tiers.others = lambda t: []
    bad, why = VR.matched(ID, tiers)
    check(bad is None and "list" in why and VR.matched(dict(ID, active_mods=["X", "cherry"]), tiers)[0]
          and VR.matched(dict(ID, tier="gone"), tiers)[0] is None and VR.matched(None, tiers)[0] is None,
          n + "a list that is not its tier's on Archmagi counts nothing (%s)" % why)
    tiers.others = lambda t: [("ArchSmall", ["x"], None)]
    check(VR.matched(ID, tiers)[0] == ID, n + "the list as another Archmagi install gives it counts")
    r = rec(["a"], {"a": "PASS"}, fin=NOW - 100)
    r["ingested"] = {"visit": {"no_look": "its list is not its tier's"}}
    w, _, bo = feed({"a": {"tier": "flowworks", "build": "release"}}, [r])
    check(w == {} and bo["FlowWorks"]["a"] > 0, n + "and it does not drain the check: the feed sends it again after its wait")
    f = rows(vrec({"sc_a": "FAIL"}))["sc_a"]
    check(f["verdict"] == "FAIL" and LK.outcome(f)[0] == LK.UNRESOLVED, n + "a FAIL is UNRESOLVED until someone classes it")
    c = {"job": {"id": "J3", "mod": "FlowWorks", "selector": {"chains": ["z"]}, "visit": 9},
         "result": {"outcome": "DONE", "rows": [{"chain": "z", "row": "z1", "verdict": "PASS"}]}}
    check(rows(c)["ch"]["verdict"] == "COULD NOT LOOK", n + "a chain job's row (no tier's list) counts nothing")
    d = rows(c)["ch"]["detail"]     # 2026-11-24: five FlowWorks rows said "could not be read", and a readiness run hunted a fault
    check("chain job" in d and "could not be read" not in d, n + "and says it is a chain job's, never an unreadable build identity")


MUTANTS = {
    "full_sent": ("stage6_checks.py", "    if BM.is_full(spec):", "    if False:"),
    "raid_sent": ("stage6_checks.py", "if RP.stages(spec) and", "if False and"),
    "archmagi_sent": ("stage6_checks.py", 'if re.search(r"\\ba game on Archmagi\\b", _cmd(spec)):', "if False:"),
    "missing_file_sent": ("stage6_checks.py", "if not f or not os.path.isfile(os.path.join(root, f)):", "if False:"),
    "unverified_site_counts": ("stage6_checks.py", '    if not site.get("verified"):\n        v = "UNMEASURED"\n    elif', "    if"),
    "unmeasured_is_fail": ("stage6_checks.py", 'else "PASS" if st and all(s == "PASS" for s in st) else "UNMEASURED"',
                           'else "PASS" if st and all(s == "PASS" for s in st) else "FAIL"'),
    "crash_is_fail": ("stage6_checks.py", 'v = "FAIL" if 1 in rcs and not crash', 'v = "FAIL" if 1 in rcs'),
    "wrong_tier_runs": ("stage6_checks.py", 'if why or r["tier"] != tier:', "if why:"),
    "form_unchecked": ("schema.py", 'need(bool(tier_of(job)) and set(sel) == {"checks"},', "need(True,"),
    "memo_kept": ("../../../../infrastructure/stevedesktop/worker.py", ' or self.job.get("proof_build"):', ":"),
    "off_tier_runs": ("../../../../infrastructure/stevedesktop/worker.py", '''            return none_ran(r.get("why") or "the tier''',
                      '''            none_ran(r.get("why") or "the tier'''),
    "clone_written": ("proof_build.py", "    WB._copy_back = lambda", "    _unused = lambda"),
    "resent_after_verdict": ("visit_feed.py", "if any(ok for _, ok, _ in runs):", "if False:"),
    "row_twice": ("visit_rows.py", 'if (r.get("job"), r.get("test")) not in have]', "]"),
    "moved_visit_written": ("visit_rows.py", "    if n != visit:", "    if False:"),
    "no_identity_counts": ("visit_rows.py", "    if lacks and v != NO_LOOK:", "    if False:"),
    "invalid_counts": ("visit_rows.py", '        if res.get("outcome") != "DONE":', "        if False:"),
}


def mutants():
    bad = []
    for name, (f, a, b) in MUTANTS.items():
        p = os.path.normpath(os.path.join(HERE, f))
        src = open(p).read()
        if src.count(a) < 1:
            bad.append("%s: its text is not in %s" % (name, f))
            continue
        try:
            open(p, "w").write(src.replace(a, b, 1))
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True, timeout=600)
        finally:
            open(p, "w").write(src)
        red = r.returncode != 0 and "FAIL  " in r.stdout or "Error" in r.stderr
        print("%s  mutant %s" % ("ok  " if red else "FAIL", name))
        if not red:
            bad.append(name)
    print("mutants: %d of %d caught%s" % (len(MUTANTS) - len(bad), len(MUTANTS), "; NOT: %s" % bad if bad else ""))
    return 1 if bad else 0


def t_a_passed_guard_stands_on_the_one_relation():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest_guard_relation.py")],
                       capture_output=True, text=True, timeout=300)
    check(r.returncode == 0, "a-passed-guard-stands-on-the-one-relation (selftest_guard_relation.py): %s" % r.stdout[-200:])


def main():
    if "--mutants" in sys.argv:
        return mutants()
    TABLES.update(tables())
    for t in (t_each_check_is_placed_once, t_the_four_mods_are_takeable, t_a_full_list_check_is_never_sent,
              t_no_entry_point_is_could_not_look, t_a_paused_raid_is_never_sent, t_the_verdict_is_the_checks_own_row,
              t_one_run_serves_all_its_checks, t_the_job_form_is_checked, t_the_worker_publishes_each_check,
              t_the_proof_build_never_touches_the_clone, t_the_feed_sends_one_tier_at_a_time, t_a_visit_row_is_written_once,
              t_a_lane_row_never_opens_a_visit,
              t_could_not_look_never_replaces_a_row, t_the_filler_does_not_repeat_a_chain_in_flight,
              t_a_passed_guard_stands_on_the_one_relation):
        t()
    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_stage6_checks: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
