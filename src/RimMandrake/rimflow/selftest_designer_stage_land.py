#!/usr/bin/env python3
"""selftest_designer_stage_land.py - DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE.

The Designer's harvest (role_launch._supervise_one -> stage_close -> designer_stage.close_run) advances
design/concepts/<Mod>/stage.json and renames result.json in the Designer's clone. Before the fix nothing committed
them: origin/main kept reading the old stage until a person landed them (3906e2b306 landed three by hand). Now the
launcher lands exactly those paths (designer_stage.land_state, land.sh -m). This builds a throwaway bare origin and a
clone of it, runs the real launcher path on a fixture concept, and reads origin/main.

    python3 src/RimMandrake/rimflow/selftest_designer_stage_land.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import designer_stage as DS  # noqa: E402
import role_launch as RL  # noqa: E402

FAILS = []
MOD = "LandFixture"
REL = "design/concepts/" + MOD


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (str(got)[:600],)))
    if not ok:
        FAILS.append(name)


def git(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def fixture(tmp):
    """-> (bare origin, clone, concept dir): stage.json and a result.json committed and pushed, as a run leaves them."""
    origin, clone = os.path.join(tmp, "origin.git"), os.path.join(tmp, "clone")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
    subprocess.run(["git", "clone", "-q", origin, clone], check=True, capture_output=True)
    for k, v in (("user.name", "selftest"), ("user.email", "selftest@example.invalid"), ("commit.gpgsign", "false")):
        git(clone, "config", k, v)
    d = os.path.join(clone, REL)
    DS.init(d, MOD, "LAND_FIXTURE_ITEM", cap=1000000, reserve=10000)
    with open(os.path.join(clone, "README"), "w") as f:
        f.write("fixture\n")
    git(clone, "add", "README", REL + "/stage.json")
    git(clone, "commit", "-q", "-m", "fixture")
    git(clone, "push", "-q", "origin", "HEAD:main")
    return origin, clone, d


def run_once(d, unit, result, pushed=False):
    """Open a run, leave `result` as its result.json, and close it through the launcher's supervisor. pushed: the run
    committed its result.json to origin itself, so the close's rename must land as a deletion there."""
    DS.open_run(d, unit, 90000, repo=DS.REPO)
    with open(os.path.join(d, "result.json"), "w") as f:
        json.dump(result, f)
    if pushed:
        clone = os.path.dirname(os.path.dirname(os.path.dirname(d)))
        git(clone, "add", REL + "/result.json")
        git(clone, "commit", "-q", "-m", "the run's own result")
        git(clone, "push", "-q", "origin", "HEAD:main")
        check("fixture: result.json is on origin/main before the close", on_origin(clone, REL + "/result.json"), "")
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    now = time.time()
    rs = {"runs": [{"state": "running", "unit": unit, "at": now - 60, "day": RL.day_of(now), "budget": 90000,
                    "mode": "run", "item": "LAND_FIXTURE_ITEM", "concept": d, "scope": "S.scope", "marker": "M"}]}
    res = {"subtype": "success", "usage": {k: 0 for k in RL.USAGE_KEYS}}
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
           "stage_close": lambda c, u, t: RL.stage_close(c, u, t, sync=False),
           "stage_turn": lambda c: None}           # stage_land is NOT injected: the real landing runs
    RL._supervise_one(row["name"], rs, dict(RL.ROLE_DEFAULTS, **row), obs, now, lambda **kw: acts.append(kw), set())
    return acts


def on_origin(clone, path):
    git(clone, "fetch", "-q", "origin", "main")
    return git(clone, "show", "origin/main:" + path)


def main():
    DS.owner_away = lambda: (False, "selftest: attended")   # the real presence must not move this test
    tmp = tempfile.mkdtemp(prefix="designer_stage_land_")
    os.environ.setdefault("RM_DISPATCHER_STATE", os.path.join(tmp, "dstate"))
    saved = (DS.result_errors, DS.owner_uncited)
    try:
        origin, clone, d = fixture(tmp)
        DS.owner_uncited = lambda *a, **k: []     # the fixture has no ledger; the real one must not move this test
        # 1. an accepted (done) result: stage 0 -> 1 on origin/main, result.json renamed there too
        DS.result_errors = lambda *a, **k: []
        acts = run_once(d, "rm-role-designer-11", {"run": "rm-role-designer-11", "stage": 0, "outcome": "done"},
                        pushed=True)
        alarms = [a for a in acts if str(a.get("kind", "")).endswith(":stage_land")]
        check("accepted: no stage_land alarm", not alarms, alarms)
        st = json.loads(on_origin(clone, REL + "/stage.json") or "{}")
        check("accepted: origin/main's stage.json reads the advanced stage (1, ready)",
              st.get("stage") == 1 and st.get("status") == "ready", (st.get("stage"), st.get("status")))
        check("accepted: origin/main holds result.rm-role-designer-11.json",
              on_origin(clone, REL + "/result.rm-role-designer-11.json") is not None, "")
        check("accepted: the pushed result.json is deleted on origin/main", on_origin(clone, REL + "/result.json") is None, "")
        subj = git(clone, "log", "-1", "--format=%s", "origin/main") or ""
        check("accepted: the landing commit names the concept and stage", MOD in subj and "stage 0 done" in subj, subj)
        stat = (git(clone, "show", "--name-only", "--format=", "origin/main") or "").split()
        check("accepted: the landing touches only the concept's stage and result files",
              stat and all(p.startswith(REL + "/stage.json") or p.startswith(REL + "/result") for p in stat), stat)
        # 2. a rejected result: renamed .rejected.json, the retry recorded, both landed
        DS.result_errors = saved[0]
        acts = run_once(d, "rm-role-designer-12", {"garbage": True})
        st = json.loads(on_origin(clone, REL + "/stage.json") or "{}")
        check("rejected: origin/main's stage.json records the rejection",
              (st.get("results") or [{}])[-1].get("outcome") == "rejected", (st.get("results") or [{}])[-1])
        check("rejected: origin/main holds result.rm-role-designer-12.rejected.json",
              on_origin(clone, REL + "/result.rm-role-designer-12.rejected.json") is not None, "")
        check("rejected: origin/main still has no result.json", on_origin(clone, REL + "/result.json") is None, "")
        # 3. nothing new: a second land is a quiet no-op, never an alarm
        check("re-land with nothing changed says nothing to land", DS.land_state(d, "again") == "nothing to land",
              DS.land_state(d, "again"))
        # 4. a peer's unrelated edit in the clone is never swept in
        with open(os.path.join(clone, "README"), "w") as f:
            f.write("a peer's unstaged edit\n")
        with open(os.path.join(d, "record.json"), "w") as f:
            f.write("{}\n")
        DS.charge(d, 5, "helper", "selftest")
        got = DS.land_state(d, "rm-role-designer-13")
        check("a later land publishes", got.startswith("PUBLISHED"), got)
        # RIMMANDRAKE_LAND_DESIGNER_WORK_HARVEST_STRANDED_TWICE: the run's own work in its concept folder lands too
        # (stage 3's tree/sheet/scenes and stage 4's exam.json sat in the bench clone while origin/main read them absent)
        check("a peer's README edit outside the concept folder stays off origin/main",
              on_origin(clone, "README") == "fixture", on_origin(clone, "README"))
        check("the Designer's record.json, written in its concept folder, lands", on_origin(clone, REL + "/record.json")
              == "{}", on_origin(clone, REL + "/record.json"))
        # 4b. nested exam evidence and a modified tracked file land; a file the clone did not change is never reverted
        os.makedirs(os.path.join(d, "exam_evidence"), exist_ok=True)
        with open(os.path.join(d, "exam.json"), "w") as f:
            f.write('{"exam": 1}\n')
        with open(os.path.join(d, "exam_evidence", "reader_one.verdicts.json"), "w") as f:
            f.write("[]\n")
        with open(os.path.join(d, "plan.md"), "w") as f:
            f.write("old plan\n")
        git(clone, "add", REL + "/plan.md")
        git(clone, "commit", "-q", "-m", "plan as this clone has it")
        git(clone, "push", "-q", "origin", "HEAD:main")
        peer = os.path.join(tmp, "peer")
        subprocess.run(["git", "clone", "-q", origin, peer], check=True, capture_output=True)
        for k, v in (("user.name", "selftest"), ("user.email", "selftest@example.invalid")):
            git(peer, "config", k, v)
        with open(os.path.join(peer, REL, "plan.md"), "w") as f:
            f.write("newer plan from a peer\n")
        git(peer, "commit", "-q", "-am", "a peer's newer plan")
        git(peer, "push", "-q", "origin", "HEAD:main")
        got = DS.land_state(d, "rm-role-designer-14")
        check("work products land", got.startswith("PUBLISHED"), got)
        check("exam.json and nested exam_evidence/ land",
              on_origin(clone, REL + "/exam.json") == '{"exam": 1}' and
              on_origin(clone, REL + "/exam_evidence/reader_one.verdicts.json") == "[]",
              (on_origin(clone, REL + "/exam.json"), on_origin(clone, REL + "/exam_evidence/reader_one.verdicts.json")))
        check("a concept file this clone left unchanged is not reverted over a peer's newer copy",
              on_origin(clone, REL + "/plan.md") == "newer plan from a peer", on_origin(clone, REL + "/plan.md"))
        # 5. a folder that is not design/concepts/<Mod> of a clone never pushes (selftest fixtures elsewhere)
        loose = os.path.join(tmp, "design/concepts/Loose")
        DS.init(loose, "Loose", "X", cap=1000, reserve=10)
        check("a non-git concept folder is skipped", DS.land_state(loose, "r").startswith("skipped"), "")
        odd = os.path.join(clone, "elsewhere", MOD)
        DS.init(odd, MOD, "X", cap=1000, reserve=10)
        check("a folder in a clone but outside design/concepts is skipped", DS.land_state(odd, "r").startswith("skipped"),
              DS.land_state(odd, "r"))
        os.environ["RM_STAGE_LAND"] = "0"
        check("RM_STAGE_LAND=0 skips", DS.land_state(d, "r").startswith("skipped"), "")
        os.environ.pop("RM_STAGE_LAND")
        # 6. a refused landing is an alarm, not a lost close (origin gone)
        shutil.rmtree(origin)
        DS.charge(d, 5, "helper", "selftest")
        acts = []
        st = DS.load_state(d)
        try:
            DS.land_state(d, "r")
            raised = False
        except RuntimeError:
            raised = True
        check("a refused landing raises (role_launch turns it into a stage_land alarm)", raised, "")
        src = open(os.path.join(HERE, "role_launch.py"), encoding="utf-8").read()
        check("role_launch alarms role:<name>:stage_land", 'kind="role:%s:stage_land"' in src, "")
    finally:
        DS.result_errors, DS.owner_uncited = saved
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
