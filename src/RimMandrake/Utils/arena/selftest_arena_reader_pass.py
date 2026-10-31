#!/usr/bin/env python3
"""selftest_arena_reader_pass.py — arena_reader_pass.py with a STUB reader (no GPT, no claude, no real pool).

A synthetic arena root (tasks/, judge/hidden/, judge/vet_cache.jsonl) over a two-commit temp git repo. Proves: the
packet holds the task text, every scored check body with its base tail and the fix diff, and no unscored check; the
prompt asks both questions; run writes one verdict per task, a rerun reads nothing, a changed packet is re-read, a
task with no base tail is never read; a bad reply writes nothing and is retried; apply turns verdicts into drop /
unscore (and refuses while a survivor is unread unless --partial); arena_trial reads the result; auto falls back to
claude when GPT fails; every default output path is judge-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_reader_pass as R  # noqa: E402
import arena_tasks as A  # noqa: E402
import arena_trial as T  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                   GIT_COMMITTER_EMAIL="t@t")).stdout.strip()


OLD_TEST = "from tool import f, base_helper\nOLD_HELPER_LINE = base_helper()\n"


def fixture(d, extra=False):
    repo = Path(d, "repo")
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src/tool.py").write_text("def f():\n    return 1\n\ndef base_helper():\n    return 0\n")
    (repo / "src/selftest_old.py").write_text(OLD_TEST)
    (repo / "docs.md").write_text("plan: someday add prose_only_name to tool\n")       # rules v4 C3: prose only
    (repo / "notes").mkdir()
    (repo / "notes/prose_stem_name.md").write_text("a note\n")
    (repo / "README.TXT").write_text("upper_prose_name\n")                                 # suffix case
    (repo / "notes/upper_stem_name.MD").write_text("a note\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "src/tool.py").write_text("def f():\n    return _private_two()\n\ndef _private_two():\n    return 2\n"
                                      "\ndef base_helper():\n    return 0\n\ndef named_new_api():\n    return 3\n"
                                      "\ndef prose_only_name():\n    return 4\n")
    (repo / "src/selftest_tool.py").write_text("from tool import f\nassert f() == 2\ncheck_only_marker = 1\n")
    (repo / "src/newmod.py").write_text("def capped():\n    return 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: f returns 2")
    fix = git(repo, "rev-parse", "HEAD")
    p = A.paths(Path(d, "arena"))
    for k in ("tasks", "judge"):
        Path(p[k]).mkdir(parents=True)
    vet = []

    def task(tid, checks, unscored=False, prompt="make f return 2", body=None):
        Path(p["tasks"], tid + ".json").write_text(json.dumps({
            "id": tid, "source_item": tid[3:], "kind": "python-util", "prompt": "PROMPT-%s: %s" % (tid, prompt),
            "criteria": "CRITERIA-%s" % tid, "base_sha": base}))
        cs = []
        for i, (path, tail) in enumerate(checks):
            key = "%s-%d" % (tid, i)
            cs.append({"type": "fix_test", "path": path,
                       "body": body if body is not None else "BODY-%s-%d\nassert f() == 2\n" % (tid, i),
                       "command": "python3 " + path, "vet": {"key": key, "discriminates": True}})
            if tail is not None:
                vet.append({"key": key, "base_tail": tail, "base_result": "fail"})
        if unscored:
            cs.append({"type": "fix_test_unscored", "path": "src/UNSCORED.py", "body": "UNSCORED-BODY",
                       "vet": {"key": "u"}})
        Path(p["judge"], tid + ".json").write_text(json.dumps({"task": tid, "fix_sha": fix, "checks": cs}))

    task("RP_KEEP", [("src/selftest_tool.py", "AssertionError KEEP-TAIL")], unscored=True)
    task("RP_HALF", [("src/selftest_a.py", "FAIL tail a"), ("src/selftest_b.py", "FAIL tail b")])
    task("RP_ALLUN", [("src/selftest_c.py", "FAIL tail c")])
    task("RP_DROP", [("src/selftest_d.py", "FAIL tail d")])
    task("RP_NOTAIL", [("src/selftest_e.py", None)])
    if extra:
        # an EXISTING test file gaining one new assertion that uses a base name, a fix name the task gives
        # (named_new_api) and a fix name it does not (_private_two)
        task("RP_OLD", [("src/selftest_old.py", "AssertionError: tail old")], prompt="add named_new_api and make f return 2",
             body=OLD_TEST + "from tool import _private_two, named_new_api\nassert f() == _private_two() + base_helper()"
                             "\nassert named_new_api() == 3\n")
        task("RP_LSCRUB", [("src/selftest_old.py", "tail ls")], prompt="fix the fake in selftest_old.py",
             body=OLD_TEST + "assert True\n")
        # rules v3: red at base only on a missing name the fix adds (unnamed / named), on a missing name plus a
        # behavioural failure, on a name only the base output cites, and with no visible reason at all
        tb = "Traceback (most recent call last):\n  File \"src/selftest_n.py\", line 1\n"
        imp = "import newmod\nassert newmod.capped() == 1\n"
        task("RP_IMPORT", [("src/selftest_n.py", tb + "ModuleNotFoundError: No module named 'newmod'\n")], body=imp)
        task("RP_IMPNAMED", [("src/selftest_n.py", tb + "ModuleNotFoundError: No module named 'newmod'\n")],
             prompt="add module newmod whose capped() returns 1", body=imp)
        task("RP_ATTRPLUS", [("src/selftest_n.py", "FAIL f() returned 1, expected 2\n" + tb +
                              "AttributeError: module 'newmod' has no attribute 'capped'\n")], body=imp)
        task("RP_CITED", [("src/selftest_n.py", tb + "AttributeError: module 'tool' has no attribute '_private_two'\n")],
             body="from tool import f\nassert f() == 2\n")
        task("RP_NOREASON", [("src/selftest_n.py", "ok 1\nok 2\nrc 1\n")], body="from tool import f\nassert f() == 2\n")
        # rules v4 C1: a name defined from scratch in the check vs one aliased from the repo; C3: prose-only name
        attr = tb + "AttributeError: module 'tool' has no attribute '_private_two'\n"
        task("RP_LOCALDEF", [("src/selftest_n.py", attr)],
             body="from tool import f\ndef _private_two():\n    return 2\nassert f() == _private_two()\n")
        task("RP_ALIAS", [("src/selftest_n.py", attr)],
             body="import tool\n_private_two = tool._private_two\nassert _private_two() == 2\n")
        task("RP_ALIASDEF", [("src/selftest_n.py", attr)],
             body="import tool\ndef _private_two():\n    return tool._private_two()\nassert _private_two() == 2\n")
        task("RP_ALIASIMP", [("src/selftest_n.py", attr)],
             body="from tool import f, _private_two\n_private_two = _private_two\nassert f() == 2\n")
        task("RP_PROSE", [("src/selftest_n.py", tb + "AttributeError: module 'tool' has no attribute "
                           "'prose_only_name'\n")], body="import tool\nassert tool.prose_only_name() == 4\n")
    Path(p["tasks"], "RP_NOHIDDEN.json").write_text(json.dumps({"id": "RP_NOHIDDEN", "source_item": "NOHIDDEN"}))
    A.vet_cache_path(p).write_text("".join(json.dumps(r) + "\n" for r in vet))
    return p, repo


PLAN = {"RP_KEEP": {"src/selftest_tool.py": "KEEP"},
        "RP_HALF": {"src/selftest_a.py": "KEEP", "src/selftest_b.py": "UNSCORE_CHECK"},
        "RP_ALLUN": {"src/selftest_c.py": "UNSCORE_CHECK"},
        "RP_DROP": {"src/selftest_d.py": "DROP_TASK"}}


def row(path, verdict, **kw):
    """A stub reader row: fair answers for KEEP, a coupled answer otherwise; kw overrides."""
    k = verdict == "KEEP"
    r = {"path": path, "tests_task": k, "solvable_from_text": k, "coupled": not k,
         "coupled_names": [] if k else ["_private_two"], "self_overwrite": False, "partial_legs": False,
         "brittle_format": False, "format_stated": False, "fails_for_defect": k, "verdict": verdict,
         "reason": "stub " + verdict}
    r.update(kw)
    return r


def refused(reply, pk):
    try:
        R.validate_reply(reply, pk)
        return False
    except R.ReaderError:
        return True


class Stub:
    def __init__(self, plan=PLAN, bad=()):
        self.plan, self.bad, self.calls = plan, set(bad), []

    def __call__(self, prompt):
        tid = next(t for t in self.plan if ("PROMPT-%s:" % t) in prompt)
        self.calls.append(tid)
        rows = [row(pa, v) for pa, v in self.plan[tid].items()]
        if tid in self.bad:
            rows[0]["verdict"] = "KEEP"
            rows[0]["coupled"] = True                 # KEEP contradicting (b): must be refused
        return "Here you go:\n```json\n" + json.dumps({"checks": rows}) + "\n```\n", "stub"


def rules_v2():
    """The five audit fixes (ARENA_READER_FIX_COUPLED_VETO_TOO_EAGER, ARENA_READER_FIX_KEEPS_THE_SELF_OVERWRITE)."""
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d, extra=True)
        pk = R.build_packet("RP_OLD", p, repo)
        c = pk["checks"][0]
        pr = R.render_prompt(pk)
        P = "src/selftest_old.py"
        # rule 2: base-vs-fix test diff + base-name lookup; old lines are not new assertions
        check(not c["new_file"] and "+assert named_new_api() == 3" in c["test_diff"]
              and "+OLD_HELPER_LINE" not in c["test_diff"] and " OLD_HELPER_LINE = base_helper()" in c["test_diff"],
              "rule 2: test diff marks only the fix's new lines '+' (old lines are context)")
        nm = c["names"]
        check("base_helper" in nm["at_base"] and "_private_two" in nm["fix_only"] and "named_new_api" in nm["fix_only"]
              and "OLD_HELPER_LINE" not in nm["at_base"] + nm["fix_only"],
              "rule 2: name lookup: base name at_base, fix names fix_only, old-line names not looked up (%s)" % nm)
        check(nm["fix_only_unnamed"] == ["_private_two"],
              "rule 2: a fix name the task text gives is not unnamed (%s)" % nm["fix_only_unnamed"])
        check("--- test diff" in pr and "at_base: " in pr and "_private_two" in pr.split("fix_only_unnamed: ")[1][:80],
              "rule 2: the prompt shows the test diff and the name lookup")
        check(R.build_packet("RP_KEEP", p, repo)["checks"][0]["new_file"] and "(new file:" in
              R.render_prompt(R.build_packet("RP_KEEP", p, repo)), "rule 2: a check file new at the fix is flagged new")
        pk_s = dict(pk, checks=[dict(c, body=c["body"] + "#x\n")])
        check(R.packet_sha(pk_s) != R.packet_sha(pk), "packet sha moves with the check (verdicts are re-read)")
        # rule 3: fairness test says "working in that repo"
        check("working in that repo" in pr and "may read" in pr, "rule 3: fairness test is 'working in that repo'")
        # rule 1: at-base names are not coupling; fix-introduced unnamed names keep the veto
        ok_keep = {"checks": [row(P, "KEEP", coupled_names=["base_helper"])]}
        check(not refused(ok_keep, pk), "rule 1: KEEP citing only an at-base name is accepted")
        check(refused({"checks": [row(P, "KEEP", coupled_names=["_private_two"])]}, pk),
              "rule 1: KEEP citing a fix-introduced name the task never gives is refused")
        check(refused({"checks": [row(P, "KEEP", coupled=True)]}, pk),
              "rule 1: veto kept: KEEP with coupled=true (TRANSIENT_PIN: solvable is not enough) is refused")
        check(not refused({"checks": [row(P, "UNSCORE_CHECK", coupled=True)]}, pk),
              "rule 1: UNSCORE with coupled=true is accepted")
        check("INTRODUCED BY THE FIX" in pr and "NOT coupling" in pr, "rule 1: prompt redefines coupling")
        # rule 4: self-overwrite (LSCRUB) and one-leg-of-many (ARTPIPE)
        pl = R.build_packet("RP_LSCRUB", p, repo)
        check(pl["checks"][0]["check_named_in_task"] and not c["check_named_in_task"],
              "rule 4: packet flags a check file the task text names")
        check(refused({"checks": [row(P, "KEEP", self_overwrite=True)]}, pl),
              "rule 4: KEEP of a check whose file holds the requested work is refused")
        check(refused({"checks": [row(P, "KEEP", partial_legs=True)]}, pk),
              "rule 4: KEEP of a check testing one leg of a multi-leg task is refused")
        check(not refused({"checks": [row(P, "DROP_TASK", self_overwrite=True)]}, pl),
              "rule 4: DROP_TASK for a self-overwrite is accepted")
        check("self_overwrite" in pr and "partial_legs" in pr and "REPLACES" in pr, "rule 4: prompt asks both")
        # rule 5: brittle output format
        check(refused({"checks": [row(P, "KEEP", brittle_format=True)]}, pk),
              "rule 5: KEEP of a brittle format neither stated nor the repo's convention is refused")
        check(not refused({"checks": [row(P, "KEEP", brittle_format=True, format_stated=True)]}, pk),
              "rule 5: KEEP of a format the task states (or the repo already uses) is accepted")
        check(not refused({"checks": [row(P, "UNSCORE_CHECK", brittle_format=True)]}, pk),
              "rule 5: UNSCORE of a brittle format is accepted")
        check("brittle_format" in pr and "convention" in pr, "rule 5: prompt asks about output format")
        bad = row(P, "KEEP")
        del bad["partial_legs"]
        check(refused({"checks": [bad]}, pk), "a row missing a v2 answer is refused")
        rows = R.validate_reply(ok_keep, pk)
        check(all(k in rows[0] for k in R.BOOL_FIELDS), "verdict rows carry every v2 answer")
        cache = R.results_dir(p).parent / R.NAME_CACHE
        n = len(cache.read_text().splitlines())
        R.build_packet("RP_OLD", p, repo)
        check(n >= 1 and len(cache.read_text().splitlines()) == n and R.build_packet("RP_OLD", p, repo) == pk,
              "name lookups are cached and stable (%d lines)" % n)


def rules_v3():
    """ARENA_VET_REPAIR_IMPORT_ONLY_FAILS: a check red at base only on a missing fix-introduced unnamed module/name,
    or with no visible failure reason, may not be KEPT; the schema bump reads older verdicts as pending."""
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d, extra=True)
        P = "src/selftest_n.py"
        keep = {"checks": [row(P, "KEEP")]}
        un = {"checks": [row(P, "UNSCORE_CHECK")]}
        pk = R.build_packet("RP_IMPORT", p, repo)
        bf = pk["checks"][0]["base_failure"]
        check(bf["veto"] == "missing_name_only" and bf["missing_fix_only_unnamed"] == ["newmod"],
              "v3: ModuleNotFoundError on a fix-added module the task never names -> veto (%s)" % bf)
        check(refused(keep, pk) and not refused(un, pk) and not refused({"checks": [row(P, "DROP_TASK")]}, pk),
              "v3: KEEP of an import-only failure is refused; UNSCORE_CHECK / DROP_TASK accepted")
        pr = R.render_prompt(pk)
        check("fails_for_defect" in pr and "BASE FAILURE" in pr and "missing_name_only" in pr
              and "KEEP forbidden" in pr, "v3: prompt asks (f) and shows the mechanical base-failure reading")
        pn = R.build_packet("RP_IMPNAMED", p, repo)
        check(pn["checks"][0]["base_failure"]["veto"] is None and not refused(keep, pn),
              "v3: the same failure on a module the task text names is no veto; KEEP accepted")
        check(refused({"checks": [row(P, "KEEP", fails_for_defect=False)]}, pn),
              "v3: KEEP with the reader's own fails_for_defect=false is refused")
        pa = R.build_packet("RP_ATTRPLUS", p, repo)
        check(pa["checks"][0]["base_failure"]["veto"] is None and pa["checks"][0]["base_failure"]["behaviour_lines"] == 1
              and not refused(keep, pa), "v3: missing name beside a behavioural FAIL line is not import-only")
        pc = R.build_packet("RP_CITED", p, repo)
        c = pc["checks"][0]
        check(c["base_failure"]["veto"] == "missing_name_only" and "_private_two" in c["cited_names"]["fix_only_unnamed"]
              and "_private_two" not in c["names"]["fix_only"],
              "v3: a missing name only the base output cites gets its own lookup and vetoes (%s)" % c.get("cited_names"))
        pz = R.build_packet("RP_NOREASON", p, repo)
        check(pz["checks"][0]["base_failure"]["veto"] == "no_reason_visible" and refused(keep, pz) and not refused(un, pz),
              "v3: no visible failure reason at base -> KEEP refused, UNSCORE accepted")
        legacy = dict(pn, checks=[{k: v for k, v in pn["checks"][0].items() if k != "base_failure"}])
        check(refused(keep, legacy), "v3: a packet with no base_failure reading cannot carry a KEEP")
        bad = row(P, "KEEP")
        del bad["fails_for_defect"]
        check(refused({"checks": [bad]}, pn), "v3: a row missing fails_for_defect is refused")
        check(R.missing_names_cited("error CS0103: The name 'Foo' does not exist in the current context\n"
                                    "ImportError: cannot import name 'bar' from 'x'\nNo module named 'a.b.c'") ==
              ["Foo", "bar", "c"], "v3: cited names: C# CS0103, ImportError, dotted module's last part")
        check(R.base_failure("Build: 0 Error(s), rc 1\nDeprecationWarning: x", {})["veto"] == "no_reason_visible",
              "v3: '0 Error(s)' and a DeprecationWarning are not a failure reason")
        check(R.VERDICT_SCHEMA == "arena_reader_verdict/4", "v4: verdict schema bumped to /4")
        res = R.results_dir(p)
        res.mkdir(parents=True, exist_ok=True)
        for old in ("arena_reader_verdict/2", "arena_reader_verdict/3"):
            (res / "RP_IMPNAMED.json").write_text(json.dumps({"schema": old, "task": "RP_IMPNAMED",
                                                              "packet_sha256": R.packet_sha(pn)}))
            check(R.state(p, repo=repo)["RP_IMPNAMED"][0] == "pending",
                  "v4: a %s verdict (even same packet sha) reads pending" % old)
        (res / "RP_IMPNAMED.json").write_text(json.dumps({"schema": R.VERDICT_SCHEMA, "task": "RP_IMPNAMED",
                                                          "packet_sha256": R.packet_sha(pn)}))
        check(R.state(p, repo=repo)["RP_IMPNAMED"][0] == "done", "v4: a current-schema verdict, same packet sha, is done")
        jf = Path(p["judge"]) / "RP_IMPNAMED.json"
        hid = json.loads(jf.read_text())
        shas, bodies = [], []
        for tailend in ("assert value == 1\n", "assert value == 2\n"):
            hid["checks"][0]["body"] = "# pad\n" * 5000 + tailend
            jf.write_text(json.dumps(hid))
            pk2 = R.build_packet("RP_IMPNAMED", p, repo)
            shas.append(R.packet_sha(pk2))
            bodies.append(pk2["checks"][0]["body"])
        check(bodies[0] == bodies[1] and shas[0] != shas[1],
              "v4: an edit past the body clip still changes the packet sha (the verdict goes stale)")


UN = {"fix_only_unnamed": ["_private_two", "newmod", "lanes"]}
TB = 'Traceback (most recent call last):\n  File "src/selftest_n.py", line 2, in <module>\n'
MISS = TB + "AttributeError: module 'tool' has no attribute '_private_two'\n"


def veto(tail):
    return R.base_failure(tail, UN)["veto"]


def keep_refusals():
    """ARENA_READER_HARDEN_SELFTEST_MUTANTS_LIVE: every KEEP refusal, ONE answer at a time, on a packet with no veto
    (so the veto cannot be what refuses it)."""
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d, extra=True)
        pk = R.build_packet("RP_OLD", p, repo)
        P = "src/selftest_old.py"
        check(pk["checks"][0]["base_failure"]["veto"] is None and not refused({"checks": [row(P, "KEEP")]}, pk),
              "control: RP_OLD has no veto and a fair KEEP is accepted")
        for k, v in (("tests_task", False), ("solvable_from_text", False), ("fails_for_defect", False),
                     ("coupled", True), ("self_overwrite", True), ("partial_legs", True), ("brittle_format", True)):
            check(refused({"checks": [row(P, "KEEP", **{k: v})]}, pk), "KEEP with only %s=%s is refused" % (k, v))
            check(not refused({"checks": [row(P, "UNSCORE_CHECK", **{k: v})]}, pk),
                  "UNSCORE_CHECK with %s=%s is accepted" % (k, v))
        # v4 review: a fix-only unnamed name found by the cited-name lookup is coupling too
        pc = json.loads(json.dumps(pk))
        pc["checks"][0]["cited_names"] = {"at_base": [], "fix_only": ["ghost_api"], "fix_only_unnamed": ["ghost_api"]}
        check(refused({"checks": [row(P, "KEEP", coupled_names=["ghost_api"])]}, pc),
              "KEEP citing a cited-lookup fix-only unnamed name as coupling is refused")


def rules_v4():
    """ARENA_READER_REPAIR_RULES_MISS_PLANTS C1-C8 (BENCH plants, verify_reader2/report.md), plus one row per regex
    alternative so removing any of them turns a row red."""
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d, extra=True)
        keep = {"checks": [row("src/selftest_n.py", "KEEP")]}

        def pkt(tid):
            return R.build_packet(tid, p, repo)["checks"][0]
        c = pkt("RP_LOCALDEF")
        check("_private_two" not in c["names"]["fix_only"] + c["names"]["at_base"] and c["base_failure"]["veto"] is None,
              "C1: a name the check defines from scratch is not looked up and does not veto (%s)" % c["names"])
        for tid, how in (("RP_ALIAS", "`_x = tool._x`"), ("RP_ALIASDEF", "`def _x(): return tool._x()`"),
                         ("RP_ALIASIMP", "imported then rebound")):
            c = pkt(tid)
            check("_private_two" in c["names"]["fix_only_unnamed"] and c["base_failure"]["veto"] == "missing_name_only",
                  "C1: a local name aliasing the repo's (%s) is looked up and vetoes (%s)" % (how, c["names"]))
        check(R.defined_in("x = 1\ndef helper():\n  pass\nclass Fake:\n  pass\n") == {"x", "helper", "Fake"},
              "C1: defined_in still finds def / class / assignment")
        pp = R.build_packet("RP_PROSE", p, repo)
        c = pp["checks"][0]
        check("prose_only_name" in c["names"]["fix_only_unnamed"] and c["base_failure"]["veto"] == "missing_name_only"
              and refused(keep, pp), "C3: a name only a .md mentions at base is fix_only, vetoes (%s)" % c["names"])
        base = git(repo, "rev-list", "--max-parents=0", "HEAD")
        fix = git(repo, "rev-parse", "HEAD")
        check(R._grep_names(repo, base, ["base_helper", "prose_only_name", "prose_stem_name"], "src/x.py")
              == {"base_helper"}, "C3: lookup sees code (control) but not prose words or prose file stems")
        check(R._grep_names(repo, base, ["upper_prose_name", "upper_stem_name", "tool"], "src/x.py") == {"tool"},
              "C3: prose suffixes match in any case (README.TXT words, a .MD stem); a code stem is still found")
        # the name cache key carries NAME_LOOKUP_VERSION: a record stored under the /1 key form is never reused
        cf = Path(d, "names.jsonl")
        k1 = hashlib.sha256(json.dumps([str(repo), base, fix, "src/x.py", ["base_helper"]]).encode()).hexdigest()
        cf.write_text(json.dumps({"k": k1, "v": {"at_base": [], "fix_only": ["base_helper"]}}) + "\n")
        v = R.name_lookup(repo, base, fix, "src/x.py", ["base_helper"], "", cf)
        check(v["at_base"] == ["base_helper"] and not v["fix_only"], "C3: a v1 name-cache record is not reused (%s)" % v)
        check(R._grep_names(repo, fix, ["check_only_marker", "selftest_tool"], "src/selftest_tool.py") == set(),
              "lookup excludes the check file: its words and its own stem")
        check(R._grep_names(repo, fix, ["check_only_marker", "selftest_tool"], "src/other.py")
              == {"check_only_marker", "selftest_tool"}, "control: the same names are found when that file is not excluded")
    # C2: a traceback's quoted source line / an ok line is not behaviour
    for name, tail in (("assert source line", TB + "    assert tool._private_two() == 2\n           ^^^^^^^^^^^^\n"
                        "AttributeError: module 'tool' has no attribute '_private_two'\n"),
                       ("check(..., 'expected') source line", TB + "    check(tool._private_two()==2,'expected 2')\n"
                        "AttributeError: module 'tool' has no attribute '_private_two'\n"),
                       ("ok line 'as expected'", "ok 1 result as expected\n" + TB +
                        "ModuleNotFoundError: No module named 'newmod'\n"),
                       ("pytest summary FAILED test - ModuleNotFoundError", "FAILED src/t.py::t - ModuleNotFoundError: "
                        "No module named 'newmod'\n"),
                       ("FAIL line naming the error class", "FAIL: ImportError: cannot import name '_private_two'\n"),
                       ("FAIL line, ModuleNotFoundError", "FAIL: ModuleNotFoundError: No module named 'newmod'\n"),
                       ("FAIL line, AttributeError", "FAIL: AttributeError: has no attribute '_private_two'\n"),
                       ("FAIL line, NameError", "FAIL: NameError: name '_private_two' is not defined\n"),
                       ("unittest FAILED (errors=1)", MISS + "FAILED (errors=1)\n"),
                       ("C4 unexpected keyword argument", TB + "TypeError: f() got an unexpected keyword argument "
                        "'lanes'\n")):
        check(veto(tail) == "missing_name_only", "C2/C4/C7: %s -> missing_name_only (%s)" % (name, R.base_failure(tail, UN)))
    check(veto(TB.replace("src/selftest_n.py", "tests/expected/assert.py") + "AttributeError: module 'tool' has no attribute "
               "'_private_two'\n") == "missing_name_only",
          "C2: a traceback File line is not an outcome line (its path says expected/assert)")
    check(veto("    def test_x():\n        assert a == 1\n\n>       assert tool._private_two() == 2\n"
               "E       AttributeError: module 'tool' has no attribute '_private_two'\n") == "missing_name_only",
          "C2: pytest's quoted source (the > line and the context above it) is not an outcome line")
    check(veto("PASS: handled No module named 'newmod'\n" + TB + "ImportError: cannot import name 'public_api'\n")
          is None, "C2: a missing name on a pass line is not cited (only the task-named import fails)")
    check(veto('  File "<string>", line 1\nAssertionError: 1 != 2\n' + MISS) is None,
          "C2: an unindented error after a source-less File line is an outcome line (behaviour kept)")
    # C5 / C6: pass lines and zero counts are no reason; a lowercase failure word is one
    for t in ("12 PASS 0 FAIL\n", "ok 3 as expected\nok 4\n", "PASS assert count 3\n", "note: no ValueError raised\nok\n",
              "3 passed, 0 failed\n", "PASSED assert count 3\n", "PASS assert count, 0 failed\n"):
        check(veto(t) == "no_reason_visible", "C5: %r is no visible reason" % t.strip())
    for t in ("check failed: got 1\n", "PASS 3 FAIL 1\n", "ok 3, 2 failures\n"):
        check(veto(t) is None, "C6: %r is a visible reason" % t.strip())
    # each _REASON alternative alone
    for t in ("Traceback (most recent call last):\n", "ValueError: bad\n", "FAIL_GATE widget\n", "  assert x == 1\n",
              "x.cs(1,1): error CS1002: semicolon\n", "not ok 3 - widget\n", "got 1, expected 2\n", "it failed\n",
              "Error: invalid dimensions\n", "Unhandled exception. System.Exception: bad\n"):
        check(R.base_failure(t, {})["reason_visible"], "reason alternative alone is visible: %r" % t.strip())
    # C7 / C8 and each _BEHAVIOUR alternative: beside a fix-only missing name, the check is NOT import-only
    for t in ("AssertionError: 1 != 2", "assert count == 3 did not hold", "FAIL widget", "got 1, expected 2",
              "not ok 1 - f", "KeyError: 'x'", "TypeError: f() takes 0 args", "FAILED test_f - got 1",
              "AssertionError: expected 2 got 1; note has no attribute '_private_two'",
              "FAIL gate reported: cannot import name '_private_two'",
              "E   AssertionError: has no attribute '_private_two'", "not ok 2 - has no attribute '_private_two'",
              "ValueError: invalid dimensions", "Exception: bad dims", "AssertionError - has no attribute '_private_two'",
              "FAILED tests/t.py::t - AssertionError: No module named 'newmod'"):
        check(veto(MISS + t + "\n") is None and R.base_failure(MISS + t + "\n", UN)["behaviour_lines"] >= 1,
              "C7/C8: %r beside a missing name is behaviour (no veto)" % t)
    check(veto(MISS) == "missing_name_only", "control: the missing name alone vetoes")
    for t in ("FAILED t.py::t - TypeError: run() got an unexpected keyword argument 'lanes'",
              "=== 1 failed in 0.12s ===", "AttributeError: module 'tool' has no attribute 'named_new_api'"):
        check(veto(MISS + t + "\n") == "missing_name_only", "%r beside a fix-only unnamed name keeps the veto" % t)
    check(veto('KeyError: "No module named \'newmod\'"\n') is None,
          "a line led by another error class is that error (behaviour), whatever its message quotes")
    check(veto(MISS + "ImportError: DLL load failed while importing _native\n") == "missing_name_only",
          "an import/attribute/name error class is never behaviour, even without a missing-name message")
    forms = ("No module named 'a.b.m1'\ncannot import name 'm2' from 'x'\nAttributeError: 'X' has no attribute 'm3'\n"
             "NameError: name 'm4' is not defined\nerror CS0103: The name 'm5' does not exist\n"
             "error CS0117: 'A.B' does not contain a definition for 'm6'\n"
             "error CS1061: 'List<int>' does not contain a definition for 'm7'\n"
             "error CS0246: The type or namespace name 'm8' could not be found\n"
             "error CS0234: The type or namespace name 'm9' does not exist in the namespace 'X'\n"
             "TypeError: f() got an unexpected keyword argument 'm10'\n")
    check(R.missing_names_cited(forms) == sorted("m%d" % i for i in range(1, 11)),
          "every missing-name form is cited (%s)" % R.missing_names_cited(forms))


def tail_invariants():
    """The base tails the reader reads come from arena_tasks.vet_tail; invariants only (that function's owner may
    change how it chooses lines): never longer than n, the start of a long FAIL line survives, and the last line
    survives when failure lines are abundant."""
    n = A.VET_TAIL_CHARS
    many_gaps = "head\n" + "".join("x%03d %s\nFAIL %d\n" % (i, "y" * 20, i) for i in range(200))
    out = A.vet_tail(many_gaps)
    check(len(out) <= n, "vet_tail: never longer than n, even with many gap markers (%d > %d?)" % (len(out), n))
    long_fail = "".join("ok %d fine\n" % i for i in range(60)) + "FAIL widget: " + "y" * 3000 + "\n" + \
        "".join("ok %d after\n" % i for i in range(150))
    out = A.vet_tail(long_fail)
    check("FAIL widget:" in out and len(out) <= n, "vet_tail: a FAIL line longer than the budget keeps its start")
    abundant = "".join("FAIL case %04d broke\n" % i for i in range(400)) + "LAST-LINE-MARKER " + "z" * 40 + "\n"
    out = A.vet_tail(abundant)
    check("LAST-LINE-MARKER" in out and "FAIL case 0000" in out and len(out) <= n,
          "vet_tail: abundant FAIL lines leave room for the end of the output")


def main():
    with tempfile.TemporaryDirectory() as d:
        p, repo = fixture(d)
        res = R.results_dir(p)
        check(R.survivors(p) == ["RP_ALLUN", "RP_DROP", "RP_HALF", "RP_KEEP", "RP_NOTAIL"],
              "survivors: tasks with a judge file holding a scored check (%s)" % R.survivors(p))
        pk = R.build_packet("RP_KEEP", p, repo)
        pr = R.render_prompt(pk)
        check("PROMPT-RP_KEEP" in pr and "CRITERIA-RP_KEEP" in pr, "packet/prompt holds the task text and criteria")
        check("BODY-RP_KEEP-0" in pr and "KEEP-TAIL" in pr, "packet holds the scored check body and its base tail")
        check("UNSCORED" not in pr and [c["path"] for c in pk["checks"]] == ["src/selftest_tool.py"],
              "an unscored check (fix_test_unscored) is not in the packet")
        check("fix: f returns 2" in pr and "_private_two" in pr and "src/tool.py" in pr,
              "packet holds the fix diff summary (stat + diff)")
        check("+assert f() == 2" not in pk["fix_diff"], "the fix diff leaves out the hidden check files themselves")
        check("(a)" in pr and "solvable_from_text" in pr and "(b)" in pr and "coupled" in pr,
              "prompt asks both questions per check")
        check(R.build_packet("RP_NOTAIL", p, repo)["missing_tails"] == ["src/selftest_e.py"],
              "a check with no vet-cache record is a missing tail")

        st = Stub(bad={"RP_HALF"})
        logs = []
        c = R.run(st, p, repo=repo, log=logs.append)
        check(c["read"] == 3 and c["errors"] == 1 and c["not_ready"] == 1,
              "run: 3 read, 1 bad reply refused, 1 not ready (%s)" % c)
        check(sorted(f.name for f in res.glob("*.json")) == ["RP_ALLUN.json", "RP_DROP.json", "RP_KEEP.json"],
              "one verdict file per task; none for the bad reply or the task without a tail")
        check("RP_NOTAIL" not in st.calls, "a not-ready task is never sent to the reader")
        v = json.loads((res / "RP_KEEP.json").read_text())
        check(v["schema"] == R.VERDICT_SCHEMA and v["task_verdict"] == "KEEP" and v["checks"][0]["reason"]
              and v["packet_sha256"] == R.packet_sha(pk), "verdict schema: per-check verdict + reason, packet hash")
        try:
            R.apply(p, repo=repo)
            check(False, "apply refuses while a survivor has no verdict")
        except R.ReaderError:
            check(True, "apply refuses while a survivor has no verdict")

        st2 = Stub()
        c = R.run(st2, p, repo=repo, log=logs.append)
        check(st2.calls == ["RP_HALF"] and c["skipped_done"] == 3, "rerun reads only the task not done (%s)" % st2.calls)
        st3 = Stub()
        R.run(st3, p, repo=repo, log=logs.append)
        check(st3.calls == [], "a third run reads nothing")
        hf = Path(p["judge"], "RP_KEEP.json")
        h = json.loads(hf.read_text())
        h["checks"][0]["body"] += "# changed\n"
        hf.write_text(json.dumps(h))
        check(R.state(p, repo=repo)["RP_KEEP"][0] == "stale", "a changed check body makes the verdict stale")
        st4 = Stub()
        R.run(st4, p, repo=repo, log=logs.append)
        check(st4.calls == ["RP_KEEP"], "a stale task is read again")
        st5 = Stub()
        R.run(st5, p, repo=repo, force=True, limit=2, log=logs.append)
        check(len(st5.calls) == 2, "--force re-reads; --limit caps the reads")

        try:
            R.apply(p, repo=repo)
            check(False, "apply still refuses while RP_NOTAIL is not ready")
        except R.ReaderError:
            check(True, "apply still refuses while RP_NOTAIL is not ready")
        doc = R.apply(p, repo=repo, partial=True)
        out = T.reader_exclusions_path(p)
        check(out.is_file() and doc["pending"] == ["RP_NOTAIL"], "apply --partial writes the default file, lists pending")
        check(set(doc["drop"]) == {"RP_ALLUN", "RP_DROP"} and "no scored check left" in doc["drop"]["RP_ALLUN"],
              "drop: a DROP_TASK check, or every scored check unscored (%s)" % doc["drop"])
        check(doc["unscore"] == {"RP_HALF": ["src/selftest_b.py"]} and doc["keep"] == ["RP_KEEP"],
              "unscore: the bad check of a task that keeps another; KEEP task in neither")
        rx = T.read_reader_exclusions(out)
        check(rx["drop"].keys() == doc["drop"].keys() and rx["unscore"] == doc["unscore"],
              "arena_trial.read_reader_exclusions reads the apply output")
        vf = res / "RP_KEEP.json"
        v = json.loads(vf.read_text())
        v["task_verdict"] = "KEEP"
        v["checks"][0]["verdict"] = "DROP_TASK"
        vf.write_text(json.dumps(v))
        check("RP_KEEP" in R.apply(p, repo=repo, partial=True)["drop"], "apply recomputes from per-check verdicts")

        for tgt in (res, out):
            check(A._inside(tgt, Path(p["freeze"]).parent) and not any(
                A._inside(tgt, r) for r in (p["tasks"], p["events"])),
                "default output %s is judge-only (not under tasks/ or events/)" % tgt.relative_to(p["root"]))

    rules_v2()
    rules_v3()
    keep_refusals()
    rules_v4()
    tail_invariants()

    def boom(pr):
        raise R.ReaderError("no login")
    name = R.make_reader("auto", gpt=boom, claude=lambda pr: "{}")("x")[1]
    check(name.startswith("claude-opus") and "no login" in name, "auto: GPT failure falls back to claude -p (%s)" % name)
    check(R.make_reader("auto", gpt=lambda pr: "{}", claude=boom)("x")[1] == "gpt", "auto prefers GPT")
    for bad in ("no json", '{"x": 1}'):
        try:
            R._extract_json(bad)
            check(False, "reply %r refused" % bad)
        except R.ReaderError:
            check(True, "reply %r refused" % bad)
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
