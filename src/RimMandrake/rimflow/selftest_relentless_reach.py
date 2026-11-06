#!/usr/bin/env python3
"""selftest_relentless_reach.py - CHECKER_REACH_PROBE_BEFORE_PAYING_TWICE: no Marker is paid to discover a box it cannot see.

(1) `contract` refuses a proof naming what the walled box hides, unless --offbox routes it or --reach-ok says why.
(2) a candidate whose contract still names such a thing is held before any clone or Marker.
(3) the supervisor reads the contract's live line outside the wall and the box gets the result.
(4) after an UNMEASURED, the recheck on the same sha and an unchanged box is held, not paid; a changed box is rechecked.
The census lines are the CANNOT REACH proofs the store held on 2026-11-04 (60 unmeasured attempts).
"""
from __future__ import annotations

import os
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_reach as RR           # noqa: E402
import relentless_wall as W             # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []
OWN = ("python3 src/RimMandrake/Utils/run_selftests.py --only selftest_relentless_reach.py,selftest_relentless_blind.py  "
       "# (1) contract refuses a proof naming what the Marker's box cannot reach (masked/tmpfs paths from the walls profile "
       "incl. /mnt/d/ClaudeWork and other clones and ~/dev, git history verbs, ssh/tailscale, Windows .exe/powershell)")
ADAPTER = "steve_c_free"
REAL = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
PROF = W.profile(REAL)


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# proofs of the kinds the store's 60 CANNOT REACH named, and proofs a box runs fine
BLIND = {
    "a worker folder": "cat /mnt/d/ClaudeWork/rimmandrake/relentless_agent/PROGRESS.md",
    "a worker's progress file": r"type D:\ClaudeWork\rimmandrake\relentless\X_progress.md",
    "the scratch root itself": "ls /mnt/d/ClaudeWork/rimmandrake",
    "another clone": "git -C /home/mandrake/rm/foundry status --short | wc -l",
    "the store": "ls /home/mandrake/rm/relentless/store/items",
    "a ~/dev repo": "python3 ~/dev/Lodestar/bin/conversations.py",
    "git history": "git log --oneline -3 && run_selftests.py --only selftest_x.py",
    "ssh": "ssh stevedesktop 'df -h'",
    "winbuild": "python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/Stillsand/Source/RM_Stillsand.csproj",
    "an exe": "powershell.exe -Command Get-Date",
    "the box's RM_DATA_ROOT": 'test -s "$RM_DATA_ROOT/arena/health.json" && cat ${RM_DATA_ROOT}/arena/x',
    "a subshell": "(cd /home/mandrake/rm/bench && git log -1)",
    "git with options": "git --no-pager log -1 && env X=1 git -c core.x=1 show HEAD",
    "bash -c": "bash -c 'ssh stevedesktop df'",
}
SEEN = {
    "seat tmp, named (MARKER_WALL_FIX_HIDES_ONLY_THE_DIARY: read through)": "ls /home/mandrake/.seat-tmp/runs",
    "relative selftest": "python3 src/RimMandrake/Utils/run_selftests.py --only selftest_relentless_reach.py",
    "relative path with slashes": "grep -q free_bytes infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md",
    "a word git": "python3 src/RimMandrake/rimflow/selftest_git_efficiency.py",
    "tmp": "python3 x.py --out /tmp/x.json && test -s /tmp/x.json",
    "a skill": "test -s /home/mandrake/.claude/skills/rimflow-operations/SKILL.md",
    "an RM_DATA_ROOT the proof sets": "RM_DATA_ROOT=/tmp/rmdr python3 x.py && test -s $RM_DATA_ROOT/out.json",
    "a comment": "python3 x.py --only a.py  # (1) refuses /mnt/d/ClaudeWork paths, git history verbs, ssh",
    # CHECKER_REACH_FIX_NAMED_SCRATCH_READ_ONLY: a named reading under read_through is bound read only into the box
    "ClaudeWork reading": "test -s /mnt/d/ClaudeWork/rimmandrake/ops_watch/health.json",
    "Windows ClaudeWork": r"python3 x.py --out D:\ClaudeWork\rimmandrake\artpipe\done",
    "a reading under the box's RM_DATA_ROOT": 'test -s "$RM_DATA_ROOT/ops_watch/health.json" && cat ${RM_DATA_ROOT}/x',
}


def t_needs():
    for k, proof in BLIND.items():
        ok(RR.needs(proof, PROF), "the live walls profile hides %s: %s" % (k, RR.needs(proof, PROF)[:1]))
    for k, proof in SEEN.items():
        ok(not RR.needs(proof, PROF), "a box runs %s: %s" % (k, RR.needs(proof, PROF)))
    ok(RR.needs("grep -c x#y /mnt/d/ClaudeWork/rimmandrake/arena/z", PROF), "a # inside a word is no comment")
    ok(not RR.needs(OWN, PROF), "this item's own contract proof (a comment names /mnt/d/ClaudeWork) is not held by its gate")
    ok(RR.hidden("/home/mandrake/rm/a-clone-made-tomorrow/x", PROF), "deny_children walls a clone made tomorrow")
    ok(not RR.hidden("/home/mandrake/rm", PROF), "the deny_children root itself is no child")
    ok(not RR.hidden("/home/mandrake/rm/bench/skills/x/SKILL.md", PROF, carved=["/home/mandrake/rm/bench/skills/x"]),
       "a skill target the wall carves out stays readable")
    ok(RR.needs("cat /home/mandrake/rm/dispatch/x /home/mandrake/rm/dispatch/x", PROF) ==
       ["hidden path: /home/mandrake/rm/dispatch/x"], "each need once")
    off = dict(REAL, walls={"marker": dict(PROF, enforce=False)})
    ok(RR.uncovered({"proof": BLIND["ssh"]}, off) == [], "an unwalled Marker reaches everything: no refusal")
    ok(RR.uncovered({"proof": BLIND["ssh"], "offbox": [ADAPTER]}, REAL) == [], "an offbox adapter routes it")
    ok(RR.uncovered({"proof": BLIND["ssh"], "reach_ok": "why"}, REAL) == [], "a reach_ok why lets it through")
    ok(RR.uncovered({"proof": BLIND["ssh"]}, REAL), "nothing routing it: uncovered")


def t_contract_refuses():
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    for k in ("a worker folder", "git history", "winbuild"):
        try:
            R.contract(x.s, "I0", g, BLIND[k], r=REAL)
            ok(False, "(1) contract refuses a proof needing %s" % k)
        except ValueError as e:
            ok("CANNOT REACH" in str(e) and "--offbox" in str(e) and "--reach-ok" in str(e),
               "(1) contract refuses a proof needing %s, naming both ways out: %s" % (k, str(e)[:90]))
    ok(x.st("I0")["contract"] is None, "(1) and nothing was stored")
    R.contract(x.s, "I0", g, SEEN["relative selftest"], r=REAL)
    ok(x.st("I0")["contract"]["proof"] == SEEN["relative selftest"], "(1) a proof the box can run is set")
    x.done()
    for kw, name in (({"offbox": [ADAPTER]}, "an adapter"), ({"reach_ok": "the selftest fakes the store"}, "a reach-ok why")):
        x = T.Rig(n=1, share=1.0)
        x.run_one("I0")
        g = x.st("I0")["gen"]
        R.contract(x.s, "I0", g, BLIND["ssh"], r=REAL, **kw)
        c = x.st("I0")["contract"]
        ok(c["proof"] == BLIND["ssh"] and (c.get("offbox") or c.get("reach_ok")), "(1) routed by %s, it is set" % name)
        x.done()
    x = T.Rig(n=1, share=1.0)       # a widening keeps the why already given
    x.run_one("I0")
    g = x.st("I0")["gen"]
    R.contract(x.s, "I0", g, BLIND["ssh"], r=REAL, reach_ok="why")
    R.contract(x.s, "I0", g, BLIND["ssh"], live="once: t", why="add the live line", r=REAL)
    ok(x.st("I0")["contract"].get("reach_ok") == "why" and x.st("I0")["contract"]["live"] == "once: t",
       "(1) a widening keeps the reach-ok why")
    with x.s.lock():
        st = x.s.load("I0")
        st["approach"] = "redesign"
        x.s.save(st)
    try:
        R.contract(x.s, "I0", g, BLIND["git history"], why="a new proof", r=REAL)
        ok(False, "(1) a redesign's new proof does not inherit the old reach-ok why")
    except ValueError:
        ok(True, "(1) a redesign's new proof does not inherit the old reach-ok why")
    x.done()


def to_candidate(x, i, proof, sha="sha1", live="once: test"):
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], proof, live=live, r=dict(REAL, walls=None))     # set before the probe existed
    R.finish(x.s, i, st["gen"], sha, "evidence")
    x.w.up[st["run"]["unit"]] = False


def t_prelaunch_hold():
    x = T.Rig(n=1, share=1.0, walls=REAL["walls"])
    to_candidate(x, "I0", BLIND["a worker folder"])
    launches = len(x.w.launches)
    for _ in range(6):
        x.tick()
        if x.st("I0")["status"] == "held":
            break
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["kind"] == "unmeasured" and st["hold"].get("reach"),
       "(2) an old contract naming a hidden path is held before launch: %s" % st["status"])
    ok(len(x.w.launches) == launches and not st.get("check"), "(2) no Marker launched, no check made")
    ok(x.s.attempts("I0")[-1]["end"] == "reach_held" and "/mnt/d/ClaudeWork" in x.s.attempts("I0")[-1]["detail"],
       "(2) the attempt names what it could not reach")
    ok(not R.hold_is_his(st["hold"]), "(2) the hold is the seat's to repair, not his")
    R.unhold(x.s, "I0", "Conductor: the selftest fakes that path", now=x.now)
    st = x.st("I0")
    ok(st["status"] == "candidate" and st["contract"].get("reach_ok", "").startswith("unhold: Conductor"),
       "(2) a plain unhold carries its why on as reach_ok")
    ok(R.reach_hold(x.s, x.r, "I0", x.now) is None, "(2) so the gate lets it through next tick")
    x.done()
    x = T.Rig(n=1, share=1.0, walls=REAL["walls"])
    to_candidate(x, "I0", BLIND["ssh"])
    for _ in range(6):
        x.tick()
        if x.st("I0")["status"] == "held":
            break
    R.unhold(x.s, "I0", "route it", now=x.now, offbox=[ADAPTER])
    st = x.st("I0")
    ok(st["contract"]["offbox"] == [ADAPTER] and not st["contract"].get("reach_ok")
       and R.reach_hold(x.s, x.r, "I0", x.now) is None, "(2) unhold --offbox routes it instead")
    x.done()


def t_live_into_box():
    calls = []

    def fake_check(line, now=None):
        calls.append(line)
        return None if "good" in line else "reading /mnt/d/ClaudeWork/rimmandrake/x.json is absent"
    got = RR.live_reading("unit=rm-good.timer reading=D:\\x max_age=1h", fake_check, now=0)
    ok(got["holds"] and calls, "(3) the supervisor runs the live check itself")
    got = RR.live_reading("unit=rm-bad.timer reading=D:\\x max_age=1h", fake_check, now=0)
    ok(not got["holds"] and "absent" in got["why"], "(3) a line that does not hold says why")
    got = RR.live_reading("x", lambda line, now=None: 1 / 0, now=0)
    ok(not got["holds"] and "ZeroDivisionError" in got["why"], "(3) a broken check is a failed reading, never a dead tick")
    # through the tick: an enforced wall with nothing denied, make_box faked to an empty folder
    root = tempfile.mkdtemp(prefix="rl-reach-")
    prof = {"enforce": True, "box_root": root, "deny": [], "deny_children": [], "tmpfs": [], "tree_exclude": []}
    real_make = W.make_box

    def make_box(p, source, sha, nonce, grants=(), **kw):
        b = os.path.join(root, nonce)
        os.makedirs(os.path.join(b, "tree"))
        return b
    W.make_box = make_box
    try:
        x = T.Rig(n=1, share=1.0, walls={"marker": prof})
        x.w.live_check = fake_check
        plain = x.w.launch      # the fake world predates the walled launch's systemd properties
        x.w.launch = lambda st, run, prompt, agent, clone, max_s, env, props=None: plain(st, run, prompt, agent, clone,
                                                                                        max_s, env)
        to_candidate(x, "I0", SEEN["relative selftest"], live="unit=rm-good.timer reading=D:\\x\\y.json max_age=1h")
        for _ in range(6):
            x.tick()
            if x.st("I0")["status"] == "checking":
                break
        st = x.st("I0")
        ok(st["status"] == "checking", "(3) the walled check launched: %s" % st["status"])
        box = (st.get("check") or {}).get("box") or ""
        f = os.path.join(box, "live.txt")
        body = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
        ok("HOLDS" in body and "rm-good.timer" in body and "outside the box" in body,
           "(3) the box holds the supervisor's live reading: %r" % body[:80])
        ok(os.path.exists(f) and not os.stat(f).st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), "(3) read only")
        prompt = next((l[2] for l in x.w.launches if l[1] == st["check"]["unit"]), "")
        ok("%s/live.txt" % box in prompt and "do not try to reach it" in prompt, "(3) the Marker is told where it is")
        x.done()
    finally:
        W.make_box = real_make
        shutil.rmtree(root, ignore_errors=True)
    ok(RR.live_lines({"proof": "p"}, "/b") == [], "(3) no live line, no words about it")


def t_through_into_box():
    """CHECKER_REACH_FIX_NAMED_SCRATCH_READ_ONLY through the tick: the proof's named reading under read_through is bound
    read only into the walled launch, kept on the check for its resume, and named to the Marker."""
    root = tempfile.mkdtemp(prefix="rl-through-")
    cw = os.path.join(root, "cw")
    os.makedirs(os.path.join(cw, "ops"))
    with open(os.path.join(cw, "ops", "health.json"), "w") as f:
        f.write("{}")
    prof = {"enforce": True, "box_root": root, "deny": [], "deny_children": [], "tmpfs": [cw], "tree_exclude": [],
            "read_through": [cw], "never_through": []}
    real_make, props = W.make_box, []

    def make_box(p, source, sha, nonce, grants=(), **kw):
        b = os.path.join(root, nonce)
        os.makedirs(os.path.join(b, "tree"))
        return b
    W.make_box = make_box
    try:
        x = T.Rig(n=1, share=1.0, walls={"marker": prof})
        plain = x.w.launch
        x.w.launch = lambda st, run, prompt, agent, clone, max_s, env, p=None: props.append(p) or plain(
            st, run, prompt, agent, clone, max_s, env)
        to_candidate(x, "I0", "test -s %s/ops/health.json" % cw)
        for _ in range(6):
            x.tick()
            if x.st("I0")["status"] == "checking":
                break
        st = x.st("I0")
        want = "BindReadOnlyPaths=-%s/ops/health.json" % os.path.realpath(cw)
        ok(st["status"] == "checking" and props and want in (props[-1] or []),
           "(5) the walled check binds the named reading read only: %s" % [q for q in (props[-1] if props else []) or []
                                                                           if "Bind" in q])
        ok(st["check"].get("through") == [os.path.realpath(cw) + "/ops/health.json"], "(5) kept on the check for its resume")
        prompt = next((l[2] for l in x.w.launches if l[1] == st["check"]["unit"]), "")
        ok("Bound read only" in prompt and "ops/health.json" in prompt, "(5) the Marker is told what was bound")
        x.done()
    finally:
        W.make_box = real_make
        shutil.rmtree(root, ignore_errors=True)


def blind_once(x, i):
    st = x.st(i)
    R.verdict(x.s, i, st["check"]["nonce"], "UNMEASURED", "CANNOT REACH: git history",
              unreached=["git cat-file -t 7684d1bcbe: not a git repository"])
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    return x.st(i)


def checked(x, i):
    for _ in range(8):
        if x.st(i)["status"] == "checking":
            return True
        x.tick()
    return False


def t_no_repaid_recheck():
    x = T.Rig(n=1, reach_repair=False, share=1.0, unmeasured_limit=2, unmeasured_recheck_s=1800)
    to_candidate(x, "I0", SEEN["relative selftest"])
    ok(checked(x, "I0"), "(4) the first check runs")
    st = blind_once(x, "I0")
    ok(st["status"] == "candidate" and st["blind"]["box"] == RR.fingerprint(x.r, st["contract"]),
       "(4) the UNMEASURED records the box it was blind in")
    n = len(x.w.launches)
    for _ in range(25):
        x.tick(120)
    st = x.st("I0")
    ok(len(x.w.launches) == n, "(4) an unchanged box buys no second Marker: %d launches after" % (len(x.w.launches) - n))
    ok(st["status"] == "held" and st["hold"]["kind"] == "unmeasured" and not st["hold"].get("reach")
       and "unchanged" in st["hold"]["why"], "(4) held for repair at the recheck instead: %s" % st["status"])
    x.done()
    x = T.Rig(n=1, reach_repair=False, share=1.0, unmeasured_limit=2, unmeasured_recheck_s=1800)
    to_candidate(x, "I0", SEEN["relative selftest"])
    checked(x, "I0")
    blind_once(x, "I0")
    x.r = dict(x.r, walls={"marker": {"enforce": False, "box_root": "/b", "deny": ["/repaired"]}})
    n = len(x.w.launches)
    for _ in range(25):
        if x.st("I0")["status"] == "checking":
            break
        x.tick(120)
    ok(x.st("I0")["status"] == "checking" and len(x.w.launches) == n + 1, "(4) a repaired box is checked again")
    x.done()
    x = T.Rig(n=1, reach_repair=False, share=1.0, unmeasured_limit=2, unmeasured_recheck_s=1800)
    to_candidate(x, "I0", SEEN["relative selftest"])
    checked(x, "I0")
    st = x.st("I0")
    with x.s.lock():
        s2 = x.s.load("I0")
        s2["contract"]["offbox"] = [ADAPTER]
        x.s.save(s2)
    blind_once(x, "I0")
    for _ in range(25):
        if x.st("I0")["status"] == "checking":
            break
        x.tick(120)
    ok(x.st("I0")["status"] == "checking", "(4) an offbox reading can differ later: its recheck still runs")
    x.done()
    ok(RR.fingerprint(REAL, {"proof": "a"}) != RR.fingerprint(REAL, {"proof": "b"}), "(4) the contract is in the print")
    ok(RR.fingerprint(REAL, {"proof": "a"}) != RR.fingerprint(dict(REAL, walls=None), {"proof": "a"}),
       "(4) the walls are in the print")


def t_host_only():
    """NIGHTLY_COP_REACH_FIX_ARENA_STAYS_DARK: a proof ran host-layout selftests in the box and the Judge went blind. A proof naming a reach_host_only test is a need at contract time."""
    HOST = dict(REAL, reach_host_only=[{"path": "src/RimMandrake/Utils/selftest_host_alpha.py", "why": "fixture"},
                                       {"path": "src/RimMandrake/Utils/selftest_host_beta.py", "why": "fixture"}])
    rows = RR.host_only_rows(HOST)
    names = [os.path.basename(p) for p, _ in rows]
    ok("selftest_host_alpha.py" in names and "selftest_host_beta.py" in names, "H1 the rules list the fixture pair")
    ok("selftest_art_eval.py" not in names, "H1 art_eval is not host-only (it passes with no bundle_textures)")
    inst = ("python3 src/RimMandrake/Utils/run_selftests.py --no-cache --only src/RimMandrake/Utils/art_eval/selftest_art_eval.py "
            "src/RimMandrake/Utils/selftest_host_beta.py src/RimMandrake/Utils/selftest_host_alpha.py")
    got = RR.uncovered({"proof": inst}, HOST)
    ok(sum(1 for g in got if g.startswith("a host-only test:")) == 2, "H2 the instance proof needs both host-only tests: %s" % got)
    ok(RR.uncovered({"proof": "run_selftests.py --only selftest_x.py,selftest_host_alpha.py"}, HOST),
       "H2 a comma list naming the bare file is caught")
    ok(not RR.uncovered({"proof": "run_selftests.py --only selftest_host_alpha.py.bak selftest_xselftest_host_alpha.py"},
                        HOST), "H3 a longer name is not the test")
    ok(not RR.uncovered({"proof": "run_selftests.py --only selftest_art_eval.py  # selftest_host_alpha.py is host-only"},
                        HOST), "H3 a comment naming it is prose")
    ok(RR.uncovered({"proof": inst, "reach_ok": "the host rerun is in the evidence"}, HOST) == [], "H4 --reach-ok routes it")
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    try:
        R.contract(x.s, "I0", g, inst, r=HOST)
        ok(False, "H4 contract refuses the instance proof")
    except ValueError as e:
        ok("host-only test" in str(e) and "--reach-ok" in str(e), "H4 contract refuses the instance proof: %s" % str(e)[-120:])
    x.done()


def t_git_tool():
    """OPS_CHURN_DIAGNOSE_RELENTLESS_HFDA_UHRX: RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM's proof ran code_review_since.py,
    which runs git itself; no git verb in the text, so the gate passed it and five checks could never run it."""
    rows = RR.git_tool_rows(REAL)
    ok(any(os.path.basename(p) == "code_review_since.py" for p, _ in rows), "G1 the rules list code_review_since.py")
    inst = ("python3 src/RimMandrake/Utils/code_review_since.py --after c5a80db3 --after 7c16acb1 "
            "src/RimMandrake/Utils/ops_watch.py   # exit 0, 9 PASS")
    got = RR.uncovered({"proof": inst}, REAL)
    ok(any(g.startswith("git history:") and "code_review_since.py" in g for g in got), "G2 the instance is a git need: %s" % got)
    ok(not RR.uncovered({"proof": "python3 src/RimMandrake/Utils/code_review_status.py check x.py  # not code_review_since.py"},
                        REAL), "G3 a comment naming it is prose; code_review_status is no git tool")
    ok(not RR.uncovered({"proof": "python3 code_review_since.py.bak x"}, REAL), "G3 a longer name is not the tool")
    ok(RR.uncovered({"proof": inst, "offbox": ["git_log_candidate"]}, REAL) == [], "G4 --offbox routes it")
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    g = x.st("I0")["gen"]
    try:
        R.contract(x.s, "I0", g, inst, r=REAL)
        ok(False, "G4 contract refuses the instance proof")
    except ValueError as e:
        ok("git history" in str(e) and "--offbox" in str(e), "G4 contract refuses the instance proof: %s" % str(e)[-120:])
    x.done()



def t_git_grant():
    """OPS_CHURN_DIAGNOSE_GRAFFITI_LOVJ_IMIL: GRAFFITI_V1_LIVE_PROOF_1's proof names selftest_graffiti_v1_live.py, which runs
    dll_source_stamp.py check; red in every git-less box, five checkers git-inited a copy by hand. The proof earns the grant."""
    ok(any(os.path.basename(p) == "dll_source_stamp.py" for p, _ in RR.git_granted_rows(REAL)), "B1 the rules grant for dll_source_stamp.py")
    repo = os.path.dirname(os.path.dirname(os.path.dirname(R.HERE)))
    inst = ("python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Graffiti/selftest_graffiti_v1_live.py "
            "src/RimMandrake/Utils/selftest_graffiti_lint.py src/RimMandrake/Utils/selftest_graffiti_fuzz.py")
    ok(os.path.isfile(os.path.join(repo, "src/RimMandrake/Graffiti/selftest_graffiti_v1_live.py")), "B2 the instance test exists")
    ok(RR.box_grants({"proof": inst}, REAL, repo) == [W.GIT_GRANT], "B2 the instance proof earns git_history: %s"
       % RR.box_grants({"proof": inst}, REAL, repo))
    ok(RR.box_grants({"proof": "python3 src/RimMandrake/Utils/dll_source_stamp.py check"}, REAL, repo) == [W.GIT_GRANT],
       "B3 naming the tool itself earns it")
    ok(RR.box_grants({"proof": "python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_graffiti_lint.py"},
                     REAL, repo) == [], "B4 a proof whose tests run no git tool earns nothing")
    ok(RR.box_grants({"proof": "python3 x.py  # dll_source_stamp.py"}, REAL, repo) == [], "B5 a comment is prose")
    ok(RR.box_grants({"proof": "python3 ../../etc/x.py /abs/dll.py"}, REAL, repo) == [], "B6 no path outside the clone is read")
    ok(RR.box_grants({"proof": inst}, {}, repo) == [], "B7 no rule rows, no grant")
    src = open(os.path.join(R.HERE, "relentless.py"), encoding="utf-8").read()
    ok("relentless_reach.box_grants(st.get(\"contract\"), r, clean)" in src, "B8 the check launch hands the grants to make_box")
    ok(not RR.uncovered({"proof": inst}, REAL), "B9 the grant is not a contract-time refusal")

def main():
    for t in (t_needs, t_contract_refuses, t_prelaunch_hold, t_live_into_box, t_through_into_box, t_no_repaid_recheck, t_host_only, t_git_tool, t_git_grant):
        t()
    print("RESULT %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
