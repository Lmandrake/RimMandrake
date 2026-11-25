#!/usr/bin/env python3
"""selftest_walk_owes_checks.py: the promises of design/specs/2026-11-24-walk-owes-its-checks/boundary.md, one test of each
name (item RIMMANDRAKE_FIX_CHANGE_RELATION_BLIND_TO_CSHARP_NINE_ROWS_MISSED). Each test builds a throwaway git repository
with one mod at a walk stage and READS what the code answers or writes. The build match is a stub (it reads Windows
paths); every other part is the real code. Offline: no game, claude, unit or landing is touched."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="walk_owes_")
for _k, _v in (("RM_MATURATION_DISPATCH_DIR", "_dispatch"), ("RM_DISPATCHER_STATE", "_dispatcher"),
               ("RM_REFUSAL_DIR", "_refusals"), ("RM_OPS_WATCH_DIR", "_ops")):
    os.environ[_k] = os.path.join(TMP, _v)      # never a live store
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN", "RM_ROLE_UNIT"):
    os.environ.pop(_k, None)
import maturation as M              # noqa: E402
import maturation_autonomy as A     # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import raid_pause as RP             # noqa: E402

MOD, VER = "WalkOwes", "0.1.0"
CHECKS = ("sc_a", "sc_b", "sc_c")


class Tree(object):
    def __init__(self, stage="his_walk", extra=None, cs=False):     # cs: the change is C# that every check reads
        self.root = tempfile.mkdtemp(prefix="r_", dir=TMP)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "selftest@example.invalid")
        self.git("config", "user.name", "selftest")
        self.d = os.path.join(self.root, "design", "concepts", MOD)
        self.tests = {t: {"id": t, "kind": "live_minimal", "stage": "6", "tier": "t",
                          "file": "src/RimMandrake/%s/validation.py" % MOD, "entry": t,
                          "reads": ["src/RimMandrake/%s/Source/A.cs" % MOD]} for t in CHECKS}
        self.tests.update(extra or {})
        self.put("src/RimMandrake/%s/validation.py" % MOD, "".join("def %s():\n    return 1\n" % t for t in CHECKS))
        self.put("src/RimMandrake/%s/Source/A.cs" % MOD, "class A { int v = 0; }\n")
        self.put(self.c("version/test_table.json"), json.dumps({"version": VER, "tests": self.tests}))
        self.put(self.c("version/VERSION.json"), json.dumps({"version": VER}))
        self.put(self.c("journal.md"), "# j\n\n- **Stage now:** x.\n- **Waiting on:** x.\n")
        self.stage(stage)
        self.put("infrastructure/state/ledger/events/OWNER.jsonl", "")
        self.c0 = self.commit("base")
        self.put("src/RimMandrake/%s/Docs.txt" % MOD, "x\n")
        if cs:
            self.put("src/RimMandrake/%s/Source/A.cs" % MOD, "class A { int v = 1; }\n")
        self.c1 = self.commit("the change")
        self.put("src/RimMandrake/%s/Docs.txt" % MOD, "y\n")
        self.c2 = self.commit("later")

    def c(self, p):
        return "design/concepts/%s/%s" % (MOD, p)

    def git(self, *a):
        return subprocess.run(["git", "-C", self.root] + list(a), capture_output=True, text=True, timeout=60,
                              check=True).stdout.strip()

    def put(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def commit(self, msg):
        self.git("add", "-A", ".")
        self.git("commit", "-q", "--allow-empty", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def stage(self, stage):
        self.put(self.c("version/stage_record.json"), json.dumps({
            "mod": MOD, "version": VER, "stage": stage, "pre_human_arrivals": 1, "cycles": {"visit": 0, "total": 1},
            "moves": [{"from": "blind_challenge", "to": "in_game", "at": "2026-11-23T10:00:00-08:00", "by": "BENCH"},
                      {"from": "in_game", "to": "pre_human", "at": "2026-11-24T04:00:00-08:00", "by": "BENCH"}]}))
        body = "".join("## %s\nselftest text\n\n" % h for h in M.WALK_BRIEF_HEADINGS)
        self.put(self.c("version/walk_brief/arrival_1.md"), "written_by: fresh-reader-1\n\n%s" % body)

    def rows(self, shas, visit=1, **kw):
        self.put(self.c("version/in_game/visit_%d/rows.jsonl" % visit), "".join(json.dumps(dict(
            {"test": t, "verdict": "PASS", "site_checked": True, "mod_sha": s}, **kw)) + "\n" for t, s in shas.items()))

    def unrun(self, check, sha, at="2026-11-24T04:47:00-08:00"):
        p = self.c("version/in_game/unrun.jsonl")
        full = os.path.join(self.root, p)
        was = open(full).read() if os.path.exists(full) else ""
        self.put(p, was + json.dumps({"item": "I", "check": check, "command": "run %s" % check, "offline": "o", "sha": sha,
                                      "result": "UNRUN", "by": "BENCH", "at": at}) + "\n")


def bm(rerun=(), state="touched", walk_why=()):
    return {"read": 3, "rerun": list(rerun), "walk_why": list(walk_why), "deploy": None, "undeclared": [], "worst": None,
            "rows": {t: {"counts": t not in rerun, "why": "the change since X touches it" if t in rerun else "ok",
                         "relation": state if t in rerun else "untouched"} for t in CHECKS},
            "count": 3 - len(rerun)}


class Exit(object):
    """Stubs the build match of the last visit (it reads the walk machine's folders)."""

    def __init__(self, match, state="met"):
        self.v = {"state": state, "why": [], "build_match": match, "visit": 1}

    def __enter__(self):
        self.real = M.read_ingame_exit
        M.read_ingame_exit = lambda *a, **k: self.v

    def __exit__(self, *a):
        M.read_ingame_exit = self.real


def owed(tr, **kw):
    return sorted(u["check"] for u in M.unrun_owed(tr.root, MOD, **kw))


def clauses(res):
    return {r["clause"]: r for r in res["verdict"]["refusals"]}


def t_an_unrun_row_is_owed_until_a_row_on_its_commit_or_later():
    tr = Tree()
    tr.rows({"sc_a": tr.c0, "sc_b": tr.c1, "sc_c": tr.c2})
    for t in CHECKS:
        tr.unrun(t, tr.c1[:12])
    tr.unrun("P_norow", tr.c1)
    got = owed(tr)
    tr2 = Tree()                                    # a spoiled run meets nothing
    tr2.rows({"sc_a": tr2.c2}, void_system=True)
    tr2.unrun("sc_a", tr2.c1)
    tr3 = Tree()                                    # a commit git does not know: the visit's opening decides
    tr3.rows({"sc_a": tr3.c2, "sc_b": "0123456789ab"})
    tr3.unrun("sc_a", "ffffffffffff")
    tr3.unrun("sc_b", tr3.c1, at="2026-11-22T10:00:00-08:00")
    ok = got == ["P_norow", "sc_a"] and owed(tr2) == ["sc_a"] and owed(tr3) == ["sc_a"]
    return ok, (got, owed(tr2), owed(tr3))


def t_a_check_that_left_the_table_is_not_owed():
    tr = Tree(extra={"sc_new": {"id": "sc_new", "kind": "live_minimal", "stage": "6", "replaces": ["sc_a"]}})
    tr.put(tr.c("version/VERSION.json"), json.dumps({"version": VER, "scenes_moved_to_next_version": ["sc_b"]}))
    for t in CHECKS:
        tr.unrun(t, tr.c1)
    tr.rows({})
    got = owed(tr)
    real = RP.paused, RP.stages
    RP.paused, RP.stages = (lambda: True), (lambda spec: (spec or {}).get("id") == "sc_c")
    try:
        raid = owed(tr)
    finally:
        RP.paused, RP.stages = real
    return got == ["sc_c"] and raid == [], (got, raid)


def t_the_visit_brief_lists_only_owed_unrun_rows():
    tr = Tree()
    tr.rows({"sc_a": tr.c0, "sc_b": tr.c2})
    tr.unrun("sc_a", tr.c1)
    tr.unrun("sc_b", tr.c1)
    L = "\n".join(M.unrun_lines(tr.root, MOD))
    tr.rows({"sc_a": tr.c2, "sc_b": tr.c2})
    none = M.unrun_lines(tr.root, MOD)
    return "sc_a" in L and "sc_b" not in L and none == ["- none recorded"], (L, none)


def t_an_owed_unrun_check_runs_in_the_next_visit():
    tr = Tree()
    tt = {"tests": tr.tests}
    tr.rows({t: tr.c0 for t in CHECKS})             # the changes touch no check: each PASS is carried
    tr.unrun("sc_b", tr.c1)
    run, counted = M.ingame_to_run(tr.root, MOD, 2, tt)
    return run == ["sc_b"] and counted == ["sc_a", "sc_c"], (run, counted)


def t_stage_six_exit_waits_for_the_unrun_rows():
    tr = Tree(stage="in_game")
    tr.rows({t: tr.c0 for t in CHECKS})
    tr.unrun("sc_b", tr.c1)
    with Exit(bm()):
        bad = clauses(M.evaluate(tr.root, MOD, "pre_human", steward="read"))
        tr.rows({"sc_a": tr.c0, "sc_b": tr.c2, "sc_c": tr.c0})
        good = clauses(M.evaluate(tr.root, MOD, "pre_human", steward="read"))
    return "unrun_run" in bad and "sc_b" in bad["unrun_run"]["observed"] and "sc_a" not in bad["unrun_run"]["observed"] \
        and "unrun_run" not in good, (bad.get("unrun_run"), sorted(good))


def t_a_check_outside_the_table_holds_no_move():
    tr = Tree(stage="pre_human")
    tr.rows({t: tr.c0 for t in CHECKS})
    tr.unrun("map_agreement (proposed Stage 6 row)", tr.c1)
    with Exit(bm()):
        walk = "walk_checks_stand" not in clauses(M.evaluate(tr.root, MOD, "his_walk"))
        tr.stage("in_game")
        six = "unrun_run" not in clauses(M.evaluate(tr.root, MOD, "pre_human", steward="read"))
    brief = "map_agreement" in "\n".join(M.unrun_lines(tr.root, MOD))
    return walk and six and brief, (walk, six, brief)


def t_untouched_checks_read_no_walk_folder():
    tr = Tree()
    tr.rows({t: tr.c0 for t in CHECKS})
    real = M.read_ingame_exit
    M.read_ingame_exit = lambda *a, **k: 1 / 0
    try:
        a = M.walk_owed(tr.root, MOD)
    finally:
        M.read_ingame_exit = real
    tr2 = Tree(cs=True)
    tr2.rows({t: tr2.c0 for t in CHECKS})
    with Exit(bm(rerun=["sc_b"])):
        b = M.walk_owed(tr2.root, MOD)
    return a == {"owed": {}, "why": []} and list(b["owed"]) == ["sc_b"] and not b["why"], (a, b)


def t_no_walk_while_a_check_is_owed():
    tr = Tree(stage="pre_human", cs=True)
    tr.rows({t: tr.c0 for t in CHECKS})
    out = []
    with Exit(bm()):
        out.append("walk_checks_stand" not in clauses(M.evaluate(tr.root, MOD, "his_walk")))
    for st in ("touched", "unreadable"):
        with Exit(bm(rerun=["sc_c"], state=st)):
            r = clauses(M.evaluate(tr.root, MOD, "his_walk")).get("walk_checks_stand")
            out.append(bool(r) and "sc_c" in r["observed"] and "sc_a" not in r["observed"])
    with Exit(bm(rerun=["sc_c"], state="untouched")):       # a list or a game build that differs: not this page's
        out.append("walk_checks_stand" not in clauses(M.evaluate(tr.root, MOD, "his_walk")))
    tr.unrun("sc_a", tr.c1)
    with Exit(bm()):
        r = clauses(M.evaluate(tr.root, MOD, "his_walk")).get("walk_checks_stand")
        out.append(bool(r) and "sc_a" in r["observed"] and "UNRUN" in r["observed"])
        adv = M.advance(tr.root, MOD, "his_walk", "BENCH", "walk brief arrival_1 written")
    out.append(not adv["ok"] and M.load(tr.root, MOD)["stage"] == "pre_human")
    # the build match carries the relation's state of each row, which walk_owed reads
    rel = M.BM.RR.relate(tr.root, MOD, tr.tests, {"sc_a": {"mod_sha": tr.c0}})
    cmp_ = M.BM.compare([("sc_a", tr.tests["sc_a"])], {"sc_a": {"mod_sha": tr.c0, "mod_hash": "h", "game_build": "1",
                        "active_mods": ["x"], "tier": "t"}}, {"mod_hash": "g", "game_build": "1", "active_mods": ["x"]},
                        lambda t: (["x"], None), relation=rel)
    out.append(cmp_["rows"]["sc_a"].get("relation") == "touched" and cmp_["rerun"] == ["sc_a"])
    return all(out), out


def row(stage):
    return {"mod": MOD, "stage": stage, "decision": "not_offline"}


def tick(tr, stage, game=None, st=None):
    """The real resolve over one mod's row -> (its row, launches)."""
    rows = [row(stage)]
    fx = {"designer_state": lambda m: {}, "version_locked": lambda m: True, "version_evidence": lambda m: [],
          "exam_gate": lambda m: ([], None), "open_items": lambda ids, **k: [], "designer_unit": lambda m: None,
          "designer_chain": lambda m: None, "walk_game": lambda: game}
    got, launches = A.resolve(tr.root, MD.load_config() if hasattr(MD, "load_config") else {}, st if st is not None else {},
                              {MOD: {"stage": stage, "version": VER, "mod": MOD}}, rows, [], 1000, fx=fx)
    return got[0], launches


def t_could_not_look_is_not_clean():
    tr = Tree(stage="pre_human", cs=True)
    tr.rows({t: tr.c0 for t in CHECKS})
    out = []
    for x in (Exit(None, state="no_exit_block"), Exit(bm(rerun=CHECKS, state="touched", walk_why=["no savegame"]))):
        with x:
            r = clauses(M.evaluate(tr.root, MOD, "his_walk")).get("walk_checks_stand")
            out.append(bool(r) and "could not look" in r["observed"])
            out.append("order" in clauses(M.evaluate(tr.root, MOD, "in_game")))
            got, launches = tick(tr, "his_walk")
            out.append(got["decision"] == "owner" and not launches and "could not be read" in got["why"])
    return all(out), out


def t_stage_seven_goes_back_only_for_an_owed_check():
    tr = Tree(stage="pre_human")
    tr.rows({t: tr.c0 for t in CHECKS})
    with Exit(bm()):
        shut = "order" in clauses(M.evaluate(tr.root, MOD, "in_game"))
        tr.unrun("sc_a", tr.c1)
        opened = "order" not in clauses(M.evaluate(tr.root, MOD, "in_game"))
        other = "order" in clauses(M.evaluate(tr.root, MOD, "offline_build"))
    return shut and opened and other and "pre_human" not in M.ROADS_BACK, (shut, opened, other)


def t_a_fix_that_landed_at_the_walk_owes_a_reader():
    tr = Tree(stage="his_walk")
    src = "src/RimMandrake/%s/" % MOD

    def at(path, when, text="class A { int v = 9; }\n"):
        tr.put(src + path, text)
        tr.git("add", "-A", ".")
        env = dict(os.environ, GIT_COMMITTER_DATE=when, GIT_AUTHOR_DATE=when)
        subprocess.run(["git", "-C", tr.root, "commit", "-q", "-m", path], env=env, check=True, capture_output=True)
        return tr.git("rev-parse", "HEAD")
    tr.put(src + "Source/P.csproj", "<Project/>\n")
    tr.put(src + "Source/SelfTest/T.csproj", "<Project/>\n")
    tr.put(src + "Assemblies/P.dll.srchash", "# project: RimMandrake/%s/Source/P.csproj\n00 A.cs\n" % MOD)
    at("Source/A.cs", "2026-11-24T03:00:00-08:00", "class A { int v = 5; }\n")        # before the Stage 6 exit
    cs = at("Source/A.cs", "2026-11-24T04:10:00-08:00")
    xml = at("Defs/B.xml", "2026-11-24T04:11:00-08:00", "<Defs/>\n")
    at("Source/SelfTest/T.cs", "2026-11-24T04:12:00-08:00")                              # never ships
    at("validation2.py", "2026-11-24T04:13:00-08:00", "x = 1\n")
    at("Assemblies/P.dll", "2026-11-24T04:14:00-08:00", "dll")
    at("Source/A.cs", "2026-11-24T05:30:00-08:00", "class A { int v = 7; }\n")        # after the visit opened
    rec = M.load(tr.root, MOD)
    rec["stage"] = "in_game"
    rec["moves"] += [{"from": "pre_human", "to": "his_walk", "at": "2026-11-24T04:50:00-08:00", "by": "BENCH"},
                     {"from": "his_walk", "to": "in_game", "at": "2026-11-24T05:00:00-08:00", "by": "DISPATCH"}]

    def save():
        tr.put(tr.c("version/stage_record.json"), json.dumps(rec))
    save()
    out = [M.landed_at_walk(tr.root, MOD, rec, 2) == [cs, xml], M.landed_at_walk(tr.root, MOD, rec, 1) == []]
    tr.rows({t: tr.c2 for t in CHECKS}, visit=2)
    tr.put(tr.c("version/in_game/visit_2/SUMMARY.md"), "# v\n\n## Exit\n```\ningame_rows: {sc_a: pass, sc_b: pass, "
           "sc_c: pass}\nstrange_open: 0\nsavegame: /x.rws\nexit_met: true\n```\n")

    def reads():
        ex = M.read_ingame_exit(tr.root, MOD, 2)
        return sorted(o["fix"] for o in ex["fix_readers_owed"]), [w for w in ex["why"] if "walk" in w and "reader" in w]
    got, why = reads()
    out.append(got == sorted([cs, xml]) and cs[:10] in " ".join(why))
    tr.put(tr.c("version/in_game/visit_2/fix_reviews.jsonl"), "".join(json.dumps({
        "fix": c, "reader": "rm-reader", "verdict": v, "why": "w"}) + "\n" for c, v in ((cs, "sound"), (xml, "wrong"))))
    out.append(reads()[0] == [xml])
    tr.put(tr.c("version/in_game/visit_1/fix_reviews.jsonl"), json.dumps({
        "fix": xml[:10], "reader": "rm-reader", "verdict": "sound", "why": "w"}) + "\n")
    tr.put(tr.c("version/in_game/visit_2/fix_reviews.jsonl"), json.dumps({
        "fix": cs, "reader": "rm-reader", "verdict": "sound", "why": "w"}) + "\n")
    out.append(reads()[0] == [])                                    # read before the visit opened, by a short hash
    # the driver wrote exit_met false only for that owed reader (FlowWorks visit 13, 2026-11-25): with every review
    # sound, the false reads as that reader, now done (RIMMANDRAKE_READ_VISIT_DRIVER_FALSE_AS_OWED_FIX_READER)
    driver_false = "the driver's block says exit_met false"
    tr.put(tr.c("version/in_game/visit_2/SUMMARY.md"), "# v\n\n## Exit\n```\ningame_rows: {sc_a: pass, sc_b: pass, "
           "sc_c: pass}\nstrange_open: 0\nsavegame: /x.rws\nexit_met: false\n```\n")
    ex = M.read_ingame_exit(tr.root, MOD, 2)
    out.append(driver_false not in ex["why"] and sorted(ex.get("fix_readers_sound") or []) == sorted([cs, xml]))
    tr.put(tr.c("version/in_game/visit_2/fix_reviews.jsonl"), json.dumps({
        "fix": cs, "reader": "rm-reader", "verdict": "unsound", "why": "w"}) + "\n")
    out.append(driver_false in M.read_ingame_exit(tr.root, MOD, 2)["why"])     # a reader still owed: the false stands
    tr.put(tr.c("version/in_game/visit_2/fix_reviews.jsonl"), json.dumps({
        "fix": cs, "reader": "rm-reader", "verdict": "sound", "why": "w"}) + "\n")
    mv = rec["moves"][-1]
    mv["confirmed"] = {"walk_result": "x"}                          # his walk's own road back: its fixes come after it
    save()
    out.append(M.landed_at_walk(tr.root, MOD, rec, 2) == [] and reads()[0] == [])
    out.append(driver_false in M.read_ingame_exit(tr.root, MOD, 2)["why"])     # no fix to read: the false stands
    mv.pop("confirmed")
    mv["from"] = "in_game"
    out.append(M.landed_at_walk(tr.root, MOD, rec, 2) == [])
    mv["from"] = "his_walk"
    save()
    real = M._git_log
    M._git_log = lambda *a: real(os.path.join(tr.root, "no_such_clone"), *a[1:])
    try:
        g, w = reads()
        blind = any("could not" in x for x in M.read_ingame_exit(tr.root, MOD, 2)["why"])
        out.append(blind)
    finally:
        M._git_log = real
    return all(out), out


def t_the_tick_opens_the_visit():
    out = []
    for stage in ("pre_human", "his_walk"):
        tr = Tree(stage=stage, cs=True)
        tr.rows({t: tr.c0 for t in CHECKS})
        tr.unrun("sc_a", tr.c1)
        with Exit(bm(rerun=["sc_c"])):
            st = {"mods": {MOD: {}}}
            got, launches = tick(tr, stage, st=st)
            out.append(got["decision"] == "autovisit" and got.get("visit_checks") == ["sc_a", "sc_c"]
                       and launches == [MOD] and "autovisit" in A.ACTS and "autovisit" in MD.NO_SLOT_AUT)
            landed = []
            A.execute(tr.root, {"seat": "BENCH"}, st, [got], launches, 1000, fx={
                "known": lambda: set(), "autovisit": lambda root, mod, checks, now=None: A.visit_and_land(
                    root, mod, checks, now=now, land=lambda s, p: landed.append((s, p)) or "PUBLISHED abc")})
        rec = M.load(tr.root, MOD)
        out.append(rec["stage"] == "in_game" and rec["moves"][-1]["by"] == "DISPATCH"
                   and len(M.ingame_openings(rec)) == 2 and len(landed) == 1
                   and any(p.endswith(M.RECORD) for p in landed[0][1]) and got["decision"] == "launched")
        run, counted = M.ingame_to_run(tr.root, MOD, 2, {"tests": tr.tests})
        out.append("sc_a" in run and "sc_c" in run)
        out.append(got.get("why"))
    return all(x is True or isinstance(x, str) for x in out), out


def t_his_hold_keeps_the_walk():
    tr = Tree(stage="his_walk")
    tr.rows({t: tr.c0 for t in CHECKS})
    tr.unrun("sc_a", tr.c1)
    with Exit(bm()):
        got, launches = tick(tr, "his_walk", game="ArchBig: HIS HOLD since 05:00")
    real, out = None, []
    import game_lock as GL
    real = GL.query
    try:
        for code, want in ((GL.EX_HIS, True), (GL.EX_BLIND, True), (GL.EX_HELD, False), (GL.EX_FREE, False)):
            GL.query = lambda g, code=code, **k: {"code": code, "line": "L %s" % code}
            out.append(bool(A.walk_game()) is want)

        def boom(*a, **k):
            raise OSError("no record")
        GL.query = boom
        out.append("could not be read" in str(A.walk_game()))
    finally:
        GL.query = real
    tr7 = Tree(stage="pre_human")                   # his hold guards a look: nothing is staged for him at Stage 7
    tr7.rows({t: tr7.c0 for t in CHECKS})
    tr7.unrun("sc_a", tr7.c1)
    with Exit(bm()):
        g7, _ = tick(tr7, "pre_human", game="ArchBig: HIS HOLD")
    return (got["decision"] == "owner" and not launches and "sc_a" in got["why"] and "HIS HOLD" in got["why"]
            and all(out) and g7["decision"] == "autovisit"), (got, launches, out, g7["decision"])


def t_nothing_owed_changes_nothing():
    out = []
    for stage, want in (("his_walk", "owner"), ("pre_human", "steward")):
        tr = Tree(stage=stage)
        tr.rows({t: tr.c0 for t in CHECKS})
        with Exit(bm()):
            got, _ = tick(tr, stage)
        out.append((got.get("decision") == want or got.get("aut") == want or want in str(got.get("steward_kind"))
                    or got.get("steward_kind") == "stage", got.get("decision"), got.get("walk_note")))
    return all(x[0] and x[1] != "autovisit" and not x[2] for x in out), out


def t_an_unlanded_visit_move_puts_files_back():
    tr = Tree(stage="his_walk")
    tr.rows({t: tr.c0 for t in CHECKS})
    tr.unrun("sc_a", tr.c1)

    def snap():
        out = {}
        for d, _, fs in os.walk(tr.d):
            for n in fs:
                with open(os.path.join(d, n), "rb") as f:
                    out[os.path.join(d, n)] = f.read()
        return out
    was = snap()

    def boom(subject, paths):
        raise RuntimeError("land.sh exited 1")
    with Exit(bm()):
        try:
            A.visit_and_land(tr.root, MOD, ["sc_a"], land=boom)
            raised = False
        except RuntimeError as e:
            raised = "land.sh" in str(e)
    now = snap()
    return raised and now == was and M.load(tr.root, MOD)["stage"] == "his_walk", (raised, sorted(set(now) ^ set(was)))


def main():
    tests = (t_an_unrun_row_is_owed_until_a_row_on_its_commit_or_later, t_a_check_that_left_the_table_is_not_owed,
             t_the_visit_brief_lists_only_owed_unrun_rows, t_an_owed_unrun_check_runs_in_the_next_visit,
             t_a_check_outside_the_table_holds_no_move, t_untouched_checks_read_no_walk_folder,
             t_stage_six_exit_waits_for_the_unrun_rows, t_no_walk_while_a_check_is_owed, t_could_not_look_is_not_clean,
             t_stage_seven_goes_back_only_for_an_owed_check, t_a_fix_that_landed_at_the_walk_owes_a_reader, t_the_tick_opens_the_visit, t_his_hold_keeps_the_walk,
             t_nothing_owed_changes_nothing, t_an_unlanded_visit_move_puts_files_back)
    bad = 0
    for t in tests:
        try:
            good, got = t()
        except Exception:       # noqa: BLE001
            good, got = False, traceback.format_exc()[-700:]
        print("%s  %s%s" % ("ok   " if good else "FAIL ", t.__name__, "" if good else ": %s" % (got,)))
        bad += not good
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d of %d tests failed" % (bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
