#!/usr/bin/env python3
"""Selftest for agent_improve.py steps 1-3 and the ramp: Curator replies validated against the packet (rule 3 cites,
rule 4 fix layer, the line cap, unique edits inside the region), the Judge blind to the Curator's reasoning, apply in a
temp git repo (commit, tag, change record, verdict with its sha), a failing check reversing the diff, the ramp's step
rules, the level's interval and holds, and materialize from a tag. Models and publishing are fakes; the real repo,
store and ledger are never touched."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402

fails = []


def check(name, cond, detail=""):
    if not cond:
        fails.append(name)
        print("FAIL: %s %s" % (name, str(detail)[:400]))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sh(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=True).stdout


SKILL = "---\nname: foo\n---\n# Foo\n\n- Always read the def before naming it.\n- Land with ./publish.\n"


def entry(n=3, target="foo"):
    return {"target": target, "window_count": n + 1, "today": n, "kinds": {"lesson": n}, "task_kinds": [],
            "prior": None,
            "pieces": [{"target": target, "kind": "lesson", "ts": 1, "path": "/l/%d.md" % i,
                        "text": "WIDGET_REPAIR_SHAPE: guessed a defName, load failed (%d)" % i} for i in range(n)]}


# parse_json_reply: prose and fences around the object are tolerated; no object raises
check("json in fence", A.parse_json_reply('Here:\n```json\n{"decision": "none"}\n```')["decision"] == "none")
try:
    A.parse_json_reply("no object here {not json")
    check("json missing raises", False)
except ValueError:
    pass

with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    write(os.path.join(repo, "skills", "foo", "SKILL.md"), SKILL)
    write(os.path.join(repo, "skills", "validate_skills.py"),
          "import os,sys\nsys.exit(1 if 'BAD' in open('skills/foo/SKILL.md').read() else 0)\n")
    write(os.path.join(repo, "src", "RimMandrake", "rimflow", "roles", "operations.md"), "# Operations\n")
    write(os.path.join(repo, "src", "RimMandrake", "rimflow", "roles", "conductor.md"), "# Conductor\n")
    sh(repo, "git", "init", "-q")
    sh(repo, "git", "config", "user.email", "t@t")   # local identity: later fixture commits need no global one
    sh(repo, "git", "config", "user.name", "t")
    sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    sh(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    A.REPO, A.ROLES, A.SKILLS = repo, os.path.join(repo, "src/RimMandrake/rimflow/roles"), os.path.join(repo, "skills")
    changes, delegated, out = (os.path.join(repo, "infrastructure/state/agent_improve/changes"),
                               os.path.join(repo, "infrastructure/state/delegated"), os.path.join(tmp, "out"))

    # targets: repo skill and role editable; the Conductor and anything unknown are proposal-only
    check("skill target", (A.resolve_target("foo") or {}).get("path") == "skills/foo/SKILL.md")
    check("role target", (A.resolve_target("operations") or {}).get("path") == "src/RimMandrake/rimflow/roles/operations.md")
    check("conductor proposal-only", A.resolve_target("conductor") is None)
    check("unknown proposal-only", A.resolve_target("git-efficiency") is None)

    res = A.resolve_target("foo")
    good = {"decision": "change", "cites": [0, 2], "fix_layer": "prompt", "why_text": "SECRET-REASONING",
            "recheck": "no guessed defName lessons in 3 days",
            "edits": [{"old": "- Always read the def before naming it.\n",
                       "new": "- Always read the def before naming it (`measure`, see instrument_traps.md).\n"}]}
    nf, diff, probs = A.build_change(entry(), res, SKILL, good)
    check("good change no problems", not probs, probs)
    check("good change diff", diff.count("\n+") >= 1 and "instrument_traps" in nf, diff)
    for name, mut in [("uncited", {"cites": []}), ("bad cite", {"cites": [9]}), ("code layer", {"fix_layer": "code"}),
                      ("no recheck", {"recheck": ""}), ("not unique", {"edits": [{"old": "- ", "new": "* "}]}),
                      ("absent old", {"edits": [{"old": "nope", "new": "x"}]}),
                      ("too long", {"edits": [{"old": "# Foo\n", "new": "# Foo\n" + "line\n" * 16}]}),
                      ("too long, ++ lines", {"edits": [{"old": "# Foo\n", "new": "# Foo\n" + "++x\n" * 16}]})]:
        _nf, _d, p = A.build_change(entry(), res, SKILL, dict(good, **mut))
        check("refused: " + name, p, mut)

    # region: an edit outside the worker brief's function is refused even if unique in the file
    py = "X = 1\ndef worker_prompt(st):\n    return 'brief line'\n\ndef other():\n    return 'outside'\n"
    rres = {"path": "src/x.py", "region": "def worker_prompt(", "what": "brief"}
    _nf, _d, p = A.build_change(entry(), rres, py, dict(good, edits=[{"old": "'outside'", "new": "'o2'"}]))
    check("region refuses outside edit", p)
    nf, _d, p = A.build_change(entry(), rres, py, dict(good, edits=[{"old": "'brief line'", "new": "'brief 2'"}]))
    check("region allows inside edit", not p and "'brief 2'" in nf, p)
    apy = py.replace("def other():", "async def other():").replace("X = 1\n", "X = 1\nclass K:\n    v = 'k'\n")
    _nf, _d, p = A.build_change(entry(), rres, apy, dict(good, edits=[{"old": "'outside'", "new": "'o2'"}]))
    check("region ends at async def", p)
    gpy = py.replace("\ndef other():", "\nGLOBAL = 'g'\n\ndef other():")
    _nf, _d, p = A.build_change(entry(), rres, gpy, dict(good, edits=[{"old": "'g'", "new": "'g2'"}]))
    check("region excludes top-level code after the function", p)
    _nf, _d, p = A.build_change(entry(), rres, py, dict(good, edits=[{"old": "    return 'brief line'\n",
                                                                      "new": "    return 'b'\nLEAK = 1\n"}]))
    check("new text may not dedent out of the function", p)

    # curate_and_judge: the Judge never sees the Curator's reasoning
    seen = {}
    os.makedirs(out, exist_ok=True)

    def judge_keep(prompt):
        seen["judge"] = prompt
        return '{"verdict": "KEEP", "reasons": "cited pieces show the guess recurring"}'
    row = A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: json.dumps(good), judge=judge_keep, repo=repo)
    check("row KEEP", row.get("verdict") == "KEEP", row)
    check("judge blind to why_text", "SECRET-REASONING" not in seen.get("judge", "x"))
    check("judge sees diff", "instrument_traps" in seen.get("judge", ""))
    row_none = A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: '{"decision": "none", "reason": "checked, no recurring failure"}',
                                  judge=lambda p: 1 / 0, repo=repo)
    check("none costs no judge", row_none["decision"] == "none" and "verdict" not in row_none, row_none)
    check("none carries its reason", row_none.get("reason") == "checked, no recurring failure", row_none)
    row_bare = A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: '{"decision": "none"}',
                                  judge=lambda p: 1 / 0, repo=repo)
    check("reasonless none is an error", row_bare["decision"] == "error" and "no reason" in row_bare.get("error", ""), row_bare)
    row_prop = A.curate_and_judge(entry(target="conductor"), "2026-11-01", out,
                                  curator=lambda p: '{"decision": "proposal", "fix_layer": "code", "proposal": "gate"}',
                                  judge=lambda p: 1 / 0, repo=repo)
    check("proposal recorded", row_prop["decision"] == "proposal" and row_prop["proposal"] == "gate", row_prop)
    row_err = A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: "I refuse", judge=judge_keep, repo=repo)
    check("unparseable curator is an error row", row_err["decision"] == "error", row_err)
    row_redo = A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: json.dumps(good),
                                  judge=lambda p: '{"verdict": "REDO", "reasons": "paste", "violated": "pointer"}',
                                  repo=repo)
    check("REDO kept", row_redo["verdict"] == "REDO", row_redo)

    # apply, end to end in the temp repo, through run_pass with fakes
    def fake_publish(msg, paths, r):
        sh(r, "git", "add", "--", *paths)
        sh(r, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", msg, "--", *paths)
        return True, sh(r, "git", "rev-parse", "HEAD").strip()

    lessons_dir = os.path.join(tmp, "lessons")
    for i, hh in enumerate(("08", "09", "10")):
        write(os.path.join(lessons_dir, "20261101T%s0000Z-BENCH-x%d.md" % (hh, i)),
              "# WIDGET_REPAIR_SHAPE guessed a defName %d\n\nhome: foo\n" % i)
    src = {"lessons": lessons_dir, "store": os.path.join(tmp, "nostore"), "ops_alarms": os.path.join(tmp, "none.json"),
           "owner": os.path.join(tmp, "none.jsonl")}
    sp = os.path.join(out, "state.json")
    kw = dict(out=out, curator=lambda p: json.dumps(good), judge=judge_keep, repo=repo, src=src, state_path=sp,
              changes_dir=changes, delegated_dir=delegated, publish=fake_publish, cadence=lambda **k: [])
    s = A.run_pass("2026-11-01", apply=True, **kw)
    r0 = [r for r in s["rows"] if r["target"] == "foo"]
    check("pass applied", r0 and r0[0].get("applied"), s)
    check("skill edited in repo", "instrument_traps" in open(os.path.join(repo, "skills/foo/SKILL.md")).read())
    check("tag made", "agent/foo/v1" in sh(repo, "git", "tag", "-l"))
    log = sh(repo, "git", "log", "-3", "--format=%B")
    check("commit carries Delegated", "Delegated: technical — agent improvement foo" in log, log)
    rec = json.load(open(os.path.join(changes, "foo_v1.json")))
    check("change record", rec["version"] == 1 and rec["recheck"] and rec["source_kinds"] == ["REPAIR"], rec)
    vr = json.load(open(os.path.join(delegated, "2026-11-01", "agent_improve_foo.json")))
    tag_sha = sh(repo, "git", "rev-parse", "agent/foo/v1^{commit}").strip()
    check("verdict has sha and tag", vr["applied_sha"] == tag_sha and vr["tag"] == "agent/foo/v1"
          and "skills/foo/SKILL.md" in sh(repo, "git", "show", "--name-only", "--format=", tag_sha), (vr, tag_sha))
    check("books published", not sh(repo, "git", "status", "--porcelain", "--", "infrastructure").strip(),
          sh(repo, "git", "status", "--porcelain"))
    st = json.load(open(sp))
    check("state last pass", st["last_pass_day"] == "2026-11-01", st)
    check("not due again same day", A.run_pass("2026-11-01", **kw).get("skipped"))
    check("packet.md lists results", "Pass results" in open(os.path.join(out, "2026-11-01", "packet.md")).read())

    # a failing check reverses the diff and leaves the file as it was
    bad = dict(good, edits=[{"old": "- Land with ./publish.\n", "new": "- Land with ./publish. BAD\n"}], cites=[0])
    before = open(os.path.join(repo, "skills/foo/SKILL.md")).read()
    s2 = A.run_pass("2026-11-01", apply=True, force=True, **dict(kw, curator=lambda p: json.dumps(bad)))
    r2 = [r for r in s2["rows"] if r["target"] == "foo"][0]
    check("failing check not applied", r2.get("applied") is False and "validate_skills" in r2["apply_detail"], r2)
    check("failing check reverted", open(os.path.join(repo, "skills/foo/SKILL.md")).read() == before)
    check("no v2 tag", "agent/foo/v2" not in sh(repo, "git", "tag", "-l"))
    vday = os.path.join(delegated, "2026-11-01")
    n_v = {n: open(os.path.join(vday, n), "rb").read() for n in os.listdir(vday)}
    real_state = open(sp).read()
    write(sp, json.dumps(dict(json.loads(real_state), last_pass_day="2026-10-31")))   # a write by the dry run would show
    state_before = open(sp).read()
    s_dry = A.run_pass("2026-11-01", force=True, **dict(kw, curator=lambda p: json.dumps(bad)))
    check("dry run judged", any(r.get("verdict") == "KEEP" for r in s_dry["rows"]), s_dry)
    check("dry run writes no repo verdict", {n: open(os.path.join(vday, n), "rb").read() for n in os.listdir(vday)} == n_v)
    check("dry run leaves the state alone", open(sp).read() == state_before)
    write(sp, real_state)
    vr1 = json.load(open(os.path.join(delegated, "2026-11-01", "agent_improve_foo.json")))
    check("rerun keeps the applied verdict", vr1["applied_sha"] and vr1["tag"] == "agent/foo/v1", vr1)
    check("rerun verdict in its own file", os.path.exists(os.path.join(delegated, "2026-11-01",
                                                                       "agent_improve_foo.run2.json")))

    # a crashing check reverses the diff too
    real_rc = A.run_checks
    A.run_checks = lambda res, repo: (_ for _ in ()).throw(subprocess.TimeoutExpired("x", 1))
    try:
        ok_c, why_c = A.apply_change(dict(r2, verdict="KEEP", diff=r2.get("diff") or row["diff"]), entry(), out,
                                     repo=repo, publish=fake_publish, changes_dir=changes, delegated_dir=delegated)
    finally:
        A.run_checks = real_rc
    check("crashing check not applied", not ok_c and "crashed" in why_c, why_c)
    check("crashing check reverted", open(os.path.join(repo, "skills/foo/SKILL.md")).read() == before)
    real_nv = A.next_version
    A.next_version = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("git timeout"))
    _nf, okdiff, _p = A.build_change(entry(), A.resolve_target("foo"), before,
                                     dict(good, edits=[{"old": "- Land with ./publish.\n", "new": "- Land, ./publish.\n"}]))
    check("crash fixture diff builds and would validate", okdiff and not _p, _p)
    try:
        ok_c, why_c = A.apply_change(dict(r2, verdict="KEEP", diff=okdiff), entry(), out,
                                     repo=repo, publish=fake_publish, changes_dir=changes, delegated_dir=delegated)
    finally:
        A.next_version = real_nv
    stray = os.path.join(changes, "foo_v2.json")
    write(stray, '{"someone": "else"}')
    ok_s, why_s = A.apply_change(dict(r2, verdict="KEEP", diff=okdiff), entry(), out, repo=repo, publish=fake_publish,
                                 changes_dir=changes, delegated_dir=delegated)
    check("an existing record is never overwritten", not ok_s and open(stray).read() == '{"someone": "else"}'
          and open(os.path.join(repo, "skills/foo/SKILL.md")).read() == before, why_s)
    os.remove(stray)
    vd = os.path.join(tmp, "vreserve")
    p1, p2 = A.free_verdict_path(vd, "2026-11-01", "foo"), A.free_verdict_path(vd, "2026-11-01", "foo")
    p3 = A.free_verdict_path(vd, "2026-11-01", "foo")
    check("three passes reserve three verdict names", len({p1, p2, p3}) == 3 and all(map(os.path.exists, (p1, p2, p3)))
          and p2.endswith(".run2.json") and p3.endswith(".run3.json"), (p1, p2, p3))
    check("crash before publish reverted", not ok_c and "preparing" in why_c and open(os.path.join(repo, "skills/foo/SKILL.md")).read()
          == before, why_c)

    # a refused books publish puts the recheck back (an unpublished "pass" must not lift an L1 hold)
    v1p = os.path.join(changes, "foo_v1.json")
    v1_before = open(v1p).read()
    s_nb = A.run_pass("2026-11-01", apply=True, force=True, **dict(
        kw, curator=lambda p: '{"decision": "none", "reason": "r", "prior_recheck": "pass"}', publish=lambda m, ps, r: (False, "no")))
    check("books refused", any(r.get("decision") == "NOT published" for r in s_nb["rows"]), s_nb)
    check("books refused: recheck record restored", open(v1p).read() == v1_before)
    check("books refused: nothing left staged", not sh(repo, "git", "diff", "--cached", "--name-only").strip())

    # the ramp reads committed verdicts from HEAD: deleting the working copy changes nothing
    rd0 = A.ramp_reading(delegated)
    vf = os.path.join(delegated, "2026-11-01", "agent_improve_foo.json")
    vf_text = open(vf).read()
    os.remove(vf)
    rd1 = A.ramp_reading(delegated)
    write(vf, vf_text)
    check("ramp reads HEAD", rd0["applied"] == 1 and rd0 == rd1, (rd0, rd1))
    import shutil
    shutil.move(delegated, delegated + ".aside")
    rd2 = A.ramp_reading(delegated)
    shutil.move(delegated + ".aside", delegated)
    check("ramp reads HEAD with the folder gone", rd2 == rd0, (rd0, rd2))

    # the Curator sees commits to its target since the evidence day (the fix already landed is not proposed again)
    cap = {}
    A.curate_and_judge(entry(), "2026-11-01", out, curator=lambda p: cap.setdefault("p", p) and '{"decision": "none", "reason": "r"}',
                       judge=judge_keep, repo=repo)
    check("curator sees commits since", "COMMITS TO skills/foo/SKILL.md" in cap.get("p", "")
          and "AGENT_IMPROVE" in cap.get("p", ""), cap.get("p", "")[:300])
    check("no commits, no block", not A.commits_since("skills/foo/SKILL.md", "2099-01-01", repo))

    # materialize v1 into a scratch dir
    p = A.materialize("foo", "v1", os.path.join(tmp, "mat"), repo=repo)
    check("materialize", "instrument_traps" in open(os.path.join(p, "SKILL.md")).read(), p)

    # L1: the prior change's recheck must have passed; L1 also needs 2 task kinds
    lv1 = A.LEVELS[1]
    for i, hh in enumerate(("11", "12")):
        write(os.path.join(lessons_dir, "20261101T%s0000Z-BENCH-y%d.md" % (hh, i)),
              "# GADGET_AUDIT_FORM another %d\n\nhome: foo\n" % i)
    pk = A.gather("2026-11-01", src, lv1, changes)
    check("L1 holds on unread recheck", "foo" in pk["held"] and [t["recheck_only"] for t in pk["targets"]] == [True],
          pk["held"])
    ro = dict(pk["targets"][0])
    r_ro = A.curate_and_judge(ro, "2026-11-01", out, curator=lambda p: json.dumps(dict(good, prior_recheck="fail")),
                              judge=judge_keep, repo=repo)
    check("held target: change refused unless recheck pass", r_ro["decision"] == "refused" and not r_ro.get("verdict"),
          r_ro)
    r_ok = A.curate_and_judge(ro, "2026-11-01", out, curator=lambda p: json.dumps(dict(bad, prior_recheck="pass")),
                              judge=judge_keep, repo=repo)
    check("held target: change judged when recheck reads pass", r_ok.get("verdict") == "KEEP", r_ok)
    rec["recheck_result"] = "pass"
    write(os.path.join(changes, "foo_v1.json"), json.dumps(rec))
    pk = A.gather("2026-11-01", src, lv1, changes)
    check("L1 signals after pass", [t["target"] for t in pk["targets"]] == ["foo"], pk["held"])
    v2p = os.path.join(changes, "foo_v2.json")
    write(v2p, json.dumps(dict(rec, version=2, tag="agent/foo/v2", recheck_result=None, rechecks=[])))
    sh(repo, "git", "add", "--", os.path.join(changes, "foo_v1.json"), v2p)
    sh(repo, "git", "commit", "-q", "-m", "fixture records")
    A.record_rechecks([{"target": "foo", "day": "2026-11-03", "prior_recheck": "fail", "prior_version": 1}], changes)
    check("recheck lands on the version shown, not a newer one",
          json.load(open(os.path.join(changes, "foo_v1.json")))["recheck_result"] == "fail"
          and json.load(open(v2p))["recheck_result"] is None)
    write(os.path.join(changes, "foo_v1.json"), json.dumps(dict(rec, note="dirty")))
    A.record_rechecks([{"target": "foo", "day": "2026-11-04", "prior_recheck": "pass", "prior_version": 1}], changes)
    check("a dirty change record is never folded in", json.load(open(os.path.join(changes, "foo_v1.json")))
          .get("note") == "dirty" and json.load(open(os.path.join(changes, "foo_v1.json")))["recheck_result"] == "pass"
          and not any(x.get("day") == "2026-11-04" for x in json.load(open(os.path.join(changes, "foo_v1.json")))
                      .get("rechecks", [])))
    sh(repo, "git", "rm", "-q", "--", v2p)
    write(os.path.join(changes, "foo_v1.json"), json.dumps(rec))
    sh(repo, "git", "add", "--", os.path.join(changes, "foo_v1.json"))
    sh(repo, "git", "commit", "-q", "-m", "fixture records back")
    pk = A.gather("2026-11-01", src, A.LEVELS[2], changes)
    check("L2 bar 5 and 3 kinds holds", not pk["targets"], pk)
    row_l2 = dict(row, day="2026-11-02")
    ok, why = A.apply_change(row_l2, entry(), out, repo=repo, publish=fake_publish, changes_dir=changes,
                             delegated_dir=delegated, pk_level=2)
    check("L2 apply refused without generalization", not ok and "generalization" in why, why)

# the ramp: one step per 10 passes, up below 0.3, down above 0.6
with tempfile.TemporaryDirectory() as tmp:
    def fill(days, applied_every):
        for i, d in enumerate(days):
            write(os.path.join(tmp, d, "agent_improve_t.json"),
                  json.dumps({"applied_sha": "abc" if applied_every and i % applied_every == 0 else None}))
    fill(["2026-10-%02d" % d for d in range(1, 10)], 0)
    st = A.load_state("/nonexistent")
    st1, step = A.ramp_step(st, A.ramp_reading(tmp))
    check("no step before 10 passes", step is None and st1["level"] == 0)
    fill(["2026-10-10"], 0)
    st1, step = A.ramp_step(st, A.ramp_reading(tmp))
    check("step up at rate 0", step and st1["level"] == 1, step)
    fill(["2026-10-%02d" % d for d in range(11, 16)], 1)
    st2, step = A.ramp_step(st1, A.ramp_reading(tmp))
    check("no second step within 10 passes", step is None and st2["level"] == 1)
    fill(["2026-10-%02d" % d for d in range(16, 21)], 1)
    st2, step = A.ramp_step(st1, A.ramp_reading(tmp))
    check("step down at rate 1", step and st2["level"] == 0, (step, A.ramp_reading(tmp)))
    check("due daily at L0", A.due({"level": 0, "last_pass_day": "2026-11-01"}, "2026-11-02"))
    check("L1 not due after 2 days", not A.due({"level": 1, "last_pass_day": "2026-11-01"}, "2026-11-03"))
    check("L1 due after 3 days", A.due({"level": 1, "last_pass_day": "2026-11-01"}, "2026-11-04"))

print("selftest_agent_improve_steps: %s" % ("FAIL %d" % len(fails) if fails else "PASS"))
sys.exit(1 if fails else 0)
