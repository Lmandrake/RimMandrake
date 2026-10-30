#!/usr/bin/env python3
"""selftest_arena_critic_calib.py - arena_critic_calib.py, each criterion proven by FORCED FAILURE. No model is
called: stand-in critics run in process, and a fake executable stands in for `claude` inside the REAL sandbox.

  maths         Wilson bounds and the Beta(1,1) tail against hand values
  rule          accept-all (miss 1.0) and reject-all (false reject 1.0) are each UNRELIABLE on a full-size set; a
                perfect oracle on the same set is RELIABLE (so the rule CAN pass); too few valid verdicts, or too many
                invalid, is UNMEASURED; a borderline critic is INCONCLUSIVE; an invalid verdict is never an accept
  set           an Escaped item nobody vetted refuses the build; a vetted planted item missing from the census
                refuses; the tier-B draw is the same twice and ignores items whose label window had not ended at the
                fixed cutoff, or that have a rework candidate; an edited set fails its hash
  blind         the critic's input carries no role, task id, label or rework; the diff is the neutralised one; the
                L4 prompt never says calibration, planted or defect set; a binary (DLL) change is listed by name and
                does not refuse the candidate
  resume        a valid verdict is not re-asked; an invalid one is retried up to `attempts`; a run started with
                one critic refuses another
  sandbox       the fake `claude` cannot read a canary under $HOME or /tmp, cannot write outside its work dir, and
                its JSON verdict is parsed; garbage output and a timeout are invalid, never a verdict
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_critic_calib as C  # noqa: E402
import arena_judge as J  # noqa: E402
import arena_tasks as A  # noqa: E402

FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + detail))
    if not ok:
        FAILS.append(name)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}).stdout.strip()


def make_repo(root: Path) -> tuple:
    repo = root / "repo"
    (repo / "pkg").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "pkg" / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    git(repo, "add", "pkg")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "pkg" / "calc.py").write_text("def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n")
    (repo / "pkg" / "Lib.dll").write_bytes(bytes(range(256)) * 4)
    git(repo, "add", "pkg")
    git(repo, "commit", "-q", "-m", "head")
    return repo, base, git(repo, "rev-parse", "HEAD")


def synth_set(base: str, head: str, n_good: int = 30, n_bad: int = 9) -> dict:
    cands = []
    for i in range(n_good + n_bad):
        role = "good" if i < n_good else "planted"
        tid = "RP_SYNTH_%s_%02d" % (role.upper(), i)
        c = {"cid": C._cid("t", tid), "role": role, "task": tid, "source_item": tid[3:], "kind": "python-util",
             "size": "S", "base": base, "head": head, "area": ["pkg/**"], "prompt": "Add sub() to pkg/calc.py.",
             "criteria": "sub(a, b) returns a - b."}
        if role == "good":
            c["tier"] = "A" if i % 2 else "B"
        else:
            c.update(grade="strong" if i % 2 else "medium", defect="x", rework_items=["REWORK_%d" % i],
                     rework_fix_shas=[None])
        cands.append(c)
    doc = {"candidates": cands}
    doc["set_sha256"] = __import__("hashlib").sha256(json.dumps(cands, sort_keys=True).encode()).hexdigest()
    return doc


class Oracle:
    """Knows the truth (reads the set behind the critic's back): the rule must be able to say RELIABLE."""
    name, needs_tree = "oracle", False

    def __init__(self, doc):
        self.role = {c["cid"]: c["role"] for c in doc["candidates"]}

    def review(self, ci):
        return C.CriticVerdict("accept" if self.role[ci.cid] == "good" else "reject", ["oracle"], {})


class Garbage:
    name, needs_tree = "garbage", False

    def review(self, ci):
        return C.CriticVerdict("maybe", ["?"], {})


class Recorder:
    name, needs_tree = "recorder", True

    def __init__(self):
        self.seen = []

    def review(self, ci):
        self.seen.append(ci)
        assert ci.tree is not None and (ci.tree / "pkg" / "calc.py").exists()
        return C.CriticVerdict("accept", [], {})


class Flaky:
    name, needs_tree = "flaky", False

    def __init__(self):
        self.calls = {}

    def review(self, ci):
        self.calls[ci.cid] = self.calls.get(ci.cid, 0) + 1
        return C.CriticVerdict("invalid" if self.calls[ci.cid] == 1 else "accept", [], {})


def t_maths():
    lo, hi = C.wilson(0, 10)
    check("wilson 0/10 upper 0.2775", abs(hi - 0.2775) < 1e-3 and lo == 0.0, str((lo, hi)))
    lo, hi = C.wilson(5, 10)
    check("wilson 5/10 [0.2366, 0.7634]", abs(lo - 0.2366) < 1e-3 and abs(hi - 0.7634) < 1e-3, str((lo, hi)))
    check("wilson n=0 is [0, 1]", C.wilson(0, 0) == (0.0, 1.0))
    t = C.beta_tail(0, 10, 0.25)
    check("beta tail 0/10 >= .25 is 0.75^11", abs(t - 0.75 ** 11) < 1e-4, str(t))
    t = C.beta_tail(0, 0, 0.25)
    check("beta tail prior >= .25 is 0.75", abs(t - 0.75) < 1e-4, str(t))
    t = C.beta_tail(10, 10, 0.5)
    check("beta tail 10/10 >= .5 is 1 - 0.5^11", abs(t - (1 - 0.5 ** 11)) < 1e-4, str(t))


def t_rule(repo, base, head, root):
    doc = synth_set(base, head)
    os.environ["ARENA_CRITIC_WORK"] = str(root / "work")
    v = {}
    for crit in (C.AcceptAll(), C.RejectAll(), Oracle(doc), Garbage()):
        C.run(doc, crit, "r-" + crit.name, concurrency=4, root=root / "runs", repo=repo)
        v[crit.name] = C.score(doc, C.read_results(root / "runs" / ("r-" + crit.name) / "results.jsonl"))
    a, r, o, g = v["accept-all"], v["reject-all"], v["oracle"], v["garbage"]
    check("forced: accept-all is UNRELIABLE (miss)", a["reliability"]["verdict"] == "UNRELIABLE"
          and a["miss"]["rate"] == 1.0 and a["false_reject"]["rate"] == 0.0, json.dumps(a["reliability"]))
    check("forced: reject-all is UNRELIABLE (false reject)", r["reliability"]["verdict"] == "UNRELIABLE"
          and r["false_reject"]["rate"] == 1.0 and r["miss"]["rate"] == 0.0, json.dumps(r["reliability"]))
    check("oracle on the same set is RELIABLE (the rule can pass)", o["reliability"]["verdict"] == "RELIABLE",
          json.dumps(o["reliability"]))
    check("all-invalid critic is UNMEASURED and counts no accept", g["reliability"]["verdict"] == "UNMEASURED"
          and g["invalid"] == 39 and g["miss"]["n"] == 0, json.dumps(g["reliability"]))
    small = synth_set(base, head, n_good=6, n_bad=9)
    s = C.score(small, [{"cid": c["cid"], "verdict": "accept" if c["role"] == "good" else "reject"}
                        for c in small["candidates"]])
    check("6 valid good verdicts is UNMEASURED", s["reliability"]["verdict"] == "UNMEASURED", json.dumps(s["reliability"]))
    res = [{"cid": c["cid"], "verdict": "accept" if c["role"] == "good" else "reject"} for c in doc["candidates"]]
    for x in res[:9]:
        x["verdict"] = "invalid"
    s = C.score(doc, res)
    check("9 invalid of 39 (>20%) is UNMEASURED", s["reliability"]["verdict"] == "UNMEASURED", json.dumps(s["reliability"]))
    tier = {c["cid"]: c.get("tier") for c in doc["candidates"]}
    res = [{"cid": c["cid"], "verdict": "accept" if c["role"] == "good" else "reject"} for c in doc["candidates"]]
    a_cids = [x for x in res if tier[x["cid"]] == "A"]
    b_cids = [x for x in res if tier[x["cid"]] == "B"]
    for x in a_cids[:2] + b_cids:         # tier A 2/15 = .133 < .25 but Wilson upper .38 >= .25; tier B all rejected
        x["verdict"] = "reject"
    s = C.score(doc, res)
    check("FR is tier A only: 2/15 is INCONCLUSIVE even with tier B 15/15 rejected",
          s["reliability"]["verdict"] == "INCONCLUSIVE" and (s["false_reject"]["k"], s["false_reject"]["n"]) == (2, 15)
          and s["reject_rate_tierB_unlabelled"]["k"] == 15, json.dumps(s["reliability"]))
    res.append({"cid": a_cids[0]["cid"], "verdict": "invalid"})          # a later invalid never overrides a verdict
    check("a later invalid record does not erase a valid verdict", C.score(doc, res)["false_reject"]["k"] == 2)
    check("false rejects are listed with task and reasons", len(s["false_rejects"]) == 17
          and all("task" in x for x in s["false_rejects"]))
    few = synth_set(base, head, n_good=30, n_bad=4)       # 4/4 missed: below MIN_BAD, but Wilson lower .51 >= .5
    s = C.score(few, [{"cid": c["cid"], "verdict": "accept"} for c in few["candidates"]])
    check("a lower bound past the threshold FAILS below the minimum count", s["reliability"]["verdict"] == "UNRELIABLE"
          and s["reliability"]["parts"]["miss"] == "FAIL", json.dumps(s["reliability"]))


def synth_pool(extra_escaped=(), drop=None):
    pool = []

    def add(i, label, kind="python-util", **h):
        t = {"id": i, "source_item": i[3:], "kind": kind, "size": "S", "base_sha": "b" * 40, "area": ["pkg/**"],
             "prompt": "p", "criteria": "c"}
        hid = {"label": label, "fix_sha": "f" * 40, "reworks": [{"item": "RW_" + i, "fix_sha": None}],
               "rework_candidates": [], "label_pending": [], "label_window_ends": "2026-10-20T00:00:00Z"}
        hid.update(h)
        pool.append((t, hid))
    for i in list(C.PLANTED) + list(C.EXCLUDED) + list(extra_escaped):
        if i != drop:
            add(i, "Escaped")
    for k in range(9):
        add("RP_CLEAN_%d" % k, "Clean")
    for kind, n in C.TIER_B.items():
        for k in range(n + 3):
            add("RP_U_%s_%d" % (kind, k), None, kind=kind)
        add("RP_LATE_%s" % kind, None, kind=kind, label_window_ends="2026-10-31T00:00:00Z")
        add("RP_RC_%s" % kind, None, kind=kind, rework_candidates=["X"])
    return pool


def t_set(root):
    d1, d2 = C.build_set(synth_pool()), C.build_set(synth_pool())
    check("set counts 9 planted / 9 A / 21 B", d1["counts"] == {"planted": 9, "planted_strong": 5, "good_A": 9,
                                                                 "good_B": 21}, json.dumps(d1["counts"]))
    check("tier-B draw is reproducible", d1["set_sha256"] == d2["set_sha256"])
    tasks = {c["task"] for c in d1["candidates"]}
    check("late label window and rework candidates are never tier B",
          not any(t.startswith(("RP_LATE_", "RP_RC_")) for t in tasks))
    check("each planted candidate records its rework item", all(c["rework_items"] for c in d1["candidates"]
                                                                 if c["role"] == "planted"))
    for name, pool in (("an unvetted Escaped item refuses the build", synth_pool(extra_escaped=["RP_NEW_ESCAPE"])),
                       ("a vetted planted item missing from the census refuses",
                        synth_pool(drop=sorted(C.PLANTED)[0]))):
        try:
            C.build_set(pool)
            check(name, False, "built")
        except A.ArenaError:
            check(name, True)
    p = root / "set.json"
    d1["candidates"][0]["role"] = "good" if d1["candidates"][0]["role"] == "planted" else "planted"
    p.write_text(json.dumps(d1))
    try:
        C.load_set(p)
        check("an edited set fails its hash", False, "loaded")
    except A.ArenaError:
        check("an edited set fails its hash", True)


def t_blind(repo, base, head, root):
    doc = synth_set(base, head, n_good=2, n_bad=1)
    rec = Recorder()
    C.run(doc, rec, "r-blind", concurrency=1, root=root / "runs", repo=repo)
    ok = len(rec.seen) == 3
    for ci in rec.seen:
        blob = json.dumps({k: str(v) for k, v in vars(ci).items()})
        for c in doc["candidates"]:
            ok &= c["task"] not in blob and "REWORK_" not in blob
        ok &= not any(w in blob for w in ("planted", "\"good\"", "tier", "Escaped", "Clean"))
        ok &= "def sub(a, b)" in ci.diff and head not in ci.diff and base not in ci.diff
        ok &= "Lib.dll" in ci.diff and "BINARY FILES CHANGED" in ci.diff
    check("critic input carries no role/task/rework; diff neutralised; DLL listed not refused", ok)
    low = C.L4_PROMPT.lower()
    check("L4 prompt never mentions calibration", not any(w in low for w in ("calibrat", "planted", "defect set",
                                                                             "known-good", "escaped")))
    check("work dirs are removed after each call", not any((root / "work").glob("*")) if (root / "work").exists()
          else True)


def t_resume(repo, base, head, root):
    doc = synth_set(base, head, n_good=3, n_bad=1)
    fl = Flaky()
    C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo, attempts=2)
    first = dict(fl.calls)
    C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo, attempts=2)
    C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo, attempts=2)
    check("invalid retried once, valid never re-asked", all(v == 1 for v in first.values())
          and all(v == 2 for v in fl.calls.values()), json.dumps(fl.calls))
    try:
        C.run(doc, C.AcceptAll(), "r-flaky", root=root / "runs", repo=repo)
        check("a run refuses a second critic", False, "mixed")
    except SystemExit:
        check("a run refuses a second critic", True)
    meta = root / "runs" / "r-flaky" / "run.json"
    m = json.loads(meta.read_text())
    meta.write_text(json.dumps(dict(m, critic_fingerprint="0" * 64)))
    try:
        C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo)
        check("a resume with the same name but another fingerprint is refused", False, "mixed")
    except SystemExit:
        check("a resume with the same name but another fingerprint is refused", True)
    m.pop("critic_fingerprint")
    meta.write_text(json.dumps(m))
    try:
        C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo)
        check("a legacy run.json without a fingerprint cannot be resumed", False, "mixed")
    except SystemExit:
        check("a legacy run.json without a fingerprint cannot be resumed", True)
    import fcntl
    with open(root / "runs" / "r-flaky" / ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            C.run(doc, fl, "r-flaky", concurrency=1, root=root / "runs", repo=repo)
            check("a run held by another process is refused", False, "interleaved")
        except SystemExit as e:
            check("a run held by another process is refused", "another process" in str(e), str(e))
    l4a, l4b, l4c = C.L4OpusCritic(exe=["claude"]), C.L4OpusCritic(exe=["python3"]), C.L4OpusCritic(timeout=7)
    fps = {C.critic_fingerprint(x) for x in (l4a, l4b, l4c)}
    check("the fingerprint changes with the executable and the instance configuration", len(fps) == 3)
    check("the fingerprint is stable for an identical critic",
          C.critic_fingerprint(l4a) == C.critic_fingerprint(C.L4OpusCritic(exe=["claude"])))
    sys.modules["calib_plugin_probe"] = type(sys)("calib_plugin_probe")
    sys.modules["calib_plugin_probe"].K = C.AcceptAll
    sys.modules["calib_plugin_probe"].I = C.RejectAll()
    sys.modules["calib_plugin_probe"].F = lambda: C.AcceptAll()
    got = [type(C.load_critic("calib_plugin_probe:" + a)).__name__ for a in "KIF"]
    check("a plug-in may be a class, an instance or a factory", got == ["AcceptAll", "RejectAll", "AcceptAll"], str(got))
    leaky = json.loads(json.dumps(doc))
    leaky["candidates"][0]["prompt"] += " This was reworked later."
    leaky["candidates"][1]["rework_items"] = ["RP_SECRET_RW"]
    leaky["candidates"][1]["criteria"] += " see RP_SECRET_RW"
    leaky["candidates"][2]["prompt"] += " (" + leaky["candidates"][2]["task"] + ")"
    leaky["candidates"][3]["criteria"] += " at " + leaky["candidates"][3]["head"][:12]
    for i, name in ((0, "a role word in the item text is refused"), (1, "a rework id in the item text is refused"),
                    (2, "the candidate's own task id in the item text is refused"),
                    (3, "the candidate's head sha in the item text is refused")):
        try:
            C.prepare(leaky["candidates"][i], C.AcceptAll(), repo=repo)
            check(name, False, "prepared")
        except J.JudgeError:
            check(name, True)
    ok = dict(doc["candidates"][0], prompt=doc["candidates"][0]["prompt"] + " " + doc["candidates"][0]["source_item"])
    try:
        C.prepare(ok, C.AcceptAll(), repo=repo)
        check("the item's own name (a builder sees it) is not refused", True)
    except J.JudgeError as e:
        check("the item's own name (a builder sees it) is not refused", False, str(e))


FAKE = r"""
import json, os, sys, time
mode = %r
prompt = sys.stdin.read()
seen = [p for p in %r if os.path.exists(p)]
wrote = []
for p in %r:
    try:
        open(p, "w").write("x"); wrote.append(p)
    except OSError:
        pass
if mode == "sleep":
    time.sleep(30)
if mode == "garbage":
    print("not json"); sys.exit(0)
ok = "def sub(a, b)" in prompt and os.path.exists("pkg/calc.py")
v = "accept" if ok and not seen else "reject"   # writes land on tmpfs at best: the HOST check decides
print(json.dumps({"result": "looks fine\n" + json.dumps({"verdict": v, "reasons": [str(seen), str(wrote)]}),
                  "is_error": False, "total_cost_usd": 0.0, "num_turns": 1, "modelUsage": {}}))
"""


def t_sandbox(repo, base, head, root):
    if not shutil.which("bwrap"):
        check("sandbox (bwrap absent: UNMEASURED)", False, "bwrap not installed")
        return
    home_dir = Path(tempfile.mkdtemp(dir=Path.home(), prefix=".critcalib_canary_"))
    tmp_dir = Path(tempfile.mkdtemp(prefix="critcalib_canary_", dir="/tmp"))
    try:
        canaries = [str(home_dir / "secret"), str(tmp_dir / "secret")]
        for p in canaries:
            Path(p).write_text("rework")
        outside = [str(home_dir / "w"), "/var/tmp/critcalib_outside_%d" % os.getpid(), str(repo / "pkg" / "w"),
                   str(Path(C.__file__).parent / ("critcalib_outside_%d" % os.getpid()))]
        doc = synth_set(base, head, n_good=1, n_bad=0)
        c = doc["candidates"][0]
        os.environ["ARENA_CRITIC_WORK"] = "/var/tmp/rm_critic_calib_selftest_%d" % os.getpid()
        os.environ[C.RELAY.ALLOW_ENV] = "127.0.0.1:1"
        sib = Path(os.environ["ARENA_CRITIC_WORK"]) / "other_candidate"
        sib.mkdir(parents=True, exist_ok=True)
        (sib / "secret").write_text("rework")
        canaries.append(str(sib / "secret"))         # another candidate's work dir must be invisible too

        def go(mode, timeout=60):
            crit = C.L4OpusCritic(exe=[sys.executable, "-c", FAKE % (mode, canaries, outside)], timeout=timeout)
            return C.run_one(c, crit, repo=repo)
        # red: the same probe WITHOUT the sandbox sees the canaries (so the probe can see)
        probe = subprocess.run([sys.executable, "-c", FAKE % ("ok", canaries, [])], input="def sub(a, b)",
                               capture_output=True, text=True, cwd=str(repo))
        check("red: unsandboxed probe sees the canary", "secret" in probe.stdout, probe.stdout[-200:])
        r = go("ok")
        check("sandboxed critic sees no canary, writes nothing outside, verdict parsed", r["verdict"] == "accept",
              json.dumps(r)[:400])
        check("nothing was written outside the work dir", not any(os.path.exists(p) for p in outside))
        r = go("garbage")
        check("garbage output is invalid", r["verdict"] == "invalid", json.dumps(r)[:300])
        r = go("sleep", timeout=3)
        check("a timed-out call is invalid", r["verdict"] == "invalid" and r["meta"].get("rc") == 124,
              json.dumps(r)[:300])
    finally:
        shutil.rmtree(home_dir, ignore_errors=True)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        shutil.rmtree(os.environ.get("ARENA_CRITIC_WORK", "/nonexistent"), ignore_errors=True)


NET_PROBE = r"""
import json, os, socket, sys
good, bad = int(sys.argv[1]), int(sys.argv[2])
out = {}
def direct(port):
    s = socket.socket(); s.settimeout(3)
    try:
        s.connect(("127.0.0.1", port)); return "open"
    except OSError as e:
        return type(e).__name__
out["direct_good"] = direct(good)
try:
    socket.socket(40, socket.SOCK_STREAM); out["vsock"] = "open"
except OSError as e:
    out["vsock"] = e.errno
url = os.environ.get("HTTPS_PROXY", "")
out["proxy"] = bool(url)
if url:
    def via(port):
        s = socket.create_connection(("127.0.0.1", int(url.rsplit(":", 1)[1])), 5)
        s.sendall(b"CONNECT 127.0.0.1:%d HTTP/1.1\r\n\r\n" % port)
        h = b""
        while b"\r\n\r\n" not in h:
            d = s.recv(4096)
            if not d: break
            h += d
        line = h.split(b"\r\n")[0].decode()
        if " 200 " in line:
            s.sendall(b"ping"); return s.recv(16).decode()
        return line
    out["via_good"], out["via_bad"] = via(good), via(bad)
print(json.dumps(out))
"""


def t_network():
    if not shutil.which("bwrap"):
        check("network (bwrap absent: UNMEASURED)", False, "bwrap not installed")
        return
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    other = socket.socket()
    other.bind(("127.0.0.1", 0))
    other.listen(8)
    good, bad = srv.getsockname()[1], other.getsockname()[1]

    def echo():
        while True:
            try:
                c, _ = srv.accept()
            except OSError:
                return
            d = c.recv(16)
            c.sendall(d)
            c.close()
    threading.Thread(target=echo, daemon=True).start()
    os.environ["ARENA_CRITIC_WORK"] = "/var/tmp/rm_critic_net_selftest_%d" % os.getpid()
    os.environ[C.RELAY.ALLOW_ENV] = "127.0.0.1:%d" % good
    work = Path(os.environ["ARENA_CRITIC_WORK"]) / "w"
    work.mkdir(parents=True)
    argv = [sys.executable, "-I", "-c", NET_PROBE, str(good), str(bad)]

    def run(**kw):
        r = subprocess.run(C.sandbox_argv(argv, work, work, **kw), capture_output=True, text=True, timeout=30, cwd="/")
        try:
            return json.loads(r.stdout)
        except ValueError:
            return {"rc": r.returncode, "out": r.stdout[-300:], "err": r.stderr[-300:]}
    try:
        red = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        check("red: outside the sandbox the probe reaches the loopback service", '"direct_good": "open"' in red.stdout,
              red.stdout + red.stderr[-200:])
        check("red: outside the sandbox AF_VSOCK opens", '"vsock": "open"' in red.stdout, red.stdout)
        o = run()
        check("sandbox: host loopback service refused", o.get("direct_good") == "ConnectionRefusedError", str(o))
        check("sandbox: AF_VSOCK refused by seccomp (EAFNOSUPPORT, the filter's answer)", o.get("vsock") == 97, str(o))
        check("sandbox: allowed target reached through the relay, bytes cross", o.get("via_good") == "ping", str(o))
        check("sandbox: other target refused by the relay and recorded", " 403 " in str(o.get("via_bad"))
              and "127.0.0.1:%d" % bad in C.RELAY._relay.denied, str(o))
        o = run(model_route=False)
        check("no model route: no proxy, no way out", o.get("proxy") is False
              and o.get("direct_good") == "ConnectionRefusedError", str(o))
        for raw, name in (("", "empty"), ("hostonly", "no port")):
            os.environ[C.RELAY.ALLOW_ENV] = raw
            try:
                C.sandbox_argv(argv, work, work)
                check("allow-list %s refuses" % name, False)
            except C.J.JudgeUnavailable:
                check("allow-list %s refuses" % name, True)
    finally:
        os.environ[C.RELAY.ALLOW_ENV] = "127.0.0.1:1"
        srv.close()
        other.close()
        shutil.rmtree(os.environ["ARENA_CRITIC_WORK"], ignore_errors=True)


def t_persist(repo, base, head):
    """ARENA_TESTER_SPEND_ENFORCE_METERED_HOME: calibration keeps --no-session-persistence; trio's critic
    (persist_sessions=True) keeps its transcript so helper_capture can meter it."""
    seen, real = [], C.sandbox_argv
    C.sandbox_argv = lambda argv, work, cwd: (seen.append(list(argv)), ["true"])[1]
    os.environ["ARENA_CRITIC_WORK"] = "/var/tmp/rm_critic_calib_persist_%d" % os.getpid()
    try:
        c = synth_set(base, head, n_good=1, n_bad=0)["candidates"][0]
        C.run_one(c, C.L4OpusCritic(exe=["claude"]), repo=repo)
        C.run_one(c, C.L4OpusCritic(exe=["claude"], persist_sessions=True), repo=repo)
    finally:
        C.sandbox_argv = real
        shutil.rmtree(os.environ["ARENA_CRITIC_WORK"], ignore_errors=True)
    check("calibration critic runs --no-session-persistence; persist_sessions=True drops it",
          len(seen) == 2 and "--no-session-persistence" in seen[0] and "--no-session-persistence" not in seen[1],
          str(seen)[:300])


def t_adjudicate(repo, base, head):
    doc = synth_set(base, head)
    good = [c["cid"] for c in doc["candidates"] if c["role"] == "good"]
    res = [{"cid": c["cid"], "verdict": "reject" if c["role"] == "planted" or c["cid"] in good[:6] else "accept"}
           for c in doc["candidates"]]
    adj = {"set_sha256": doc["set_sha256"], "cids": {
        good[0]: {"finding": "true_defect", "evidence": "sha1"}, good[1]: {"finding": "true_defect", "evidence": "s"},
        good[2]: {"finding": "bad_candidate", "evidence": "wrong commit"},
        good[3]: {"finding": "false_reject", "evidence": "kept"}}}
    s = C.score_adjudicated(doc, res, adj)
    check("adjudication: true defects become caught planted, bad candidates leave, false rejects stay",
          (s["false_reject"]["k"], s["false_reject"]["n"], s["miss"]["k"], s["miss"]["n"]) == (2, 14, 0, 11)
          and (s["reject_rate_all_good_nominal"]["k"], s["reject_rate_all_good_nominal"]["n"]) == (3, 27),
          json.dumps({k: s[k] for k in ("false_reject", "miss")}))
    check("an adjudicated score carries no verdict", s["reliability"]["verdict"] == "SENSITIVITY-ONLY",
          json.dumps(s["reliability"]))
    raw = C.score(doc, res)
    check("adjudication leaves the raw score alone", (raw["false_reject"]["k"], raw["false_reject"]["n"]) == (3, 15))
    for name, bad in (("an accepted candidate cannot be adjudicated (reject side only)",
                       {good[10]: {"finding": "false_reject", "evidence": "x"}}),
                      ("a planted candidate cannot be adjudicated",
                       {[c["cid"] for c in doc["candidates"] if c["role"] == "planted"][0]:
                        {"finding": "true_defect", "evidence": "x"}}),
                      ("an unknown finding is refused", {good[0]: {"finding": "maybe", "evidence": "x"}}),
                      ("a finding without evidence is refused", {good[0]: {"finding": "true_defect", "evidence": ""}})):
        try:
            C.adjudicate(doc, {"set_sha256": doc["set_sha256"], "cids": bad}, res)
            check(name, False, "accepted")
        except A.ArenaError:
            check(name, True)
    try:
        C.adjudicate(doc, dict(adj, set_sha256="0" * 64), res)
        check("an adjudication for another set is refused", False, "accepted")
    except A.ArenaError:
        check("an adjudication for another set is refused", True)
    real = json.loads(C.ADJ_PATH.read_text())
    check("the shipped adjudication names the shipped set and only legal findings",
          real["set_sha256"] == C.load_set()["set_sha256"]
          and all(a["finding"] in C.ADJ_FINDINGS and a["evidence"] for a in real["cids"].values()))


def t_tree_and_hidden(root):
    repo = root / "repo2"
    (repo / "pkg").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "pkg" / "a.py").write_text("x = 1\n")
    git(repo, "add", "pkg")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "pkg" / "a.py").write_text("x = 2\n")
    (repo / "pkg" / "big.bin").write_bytes(b"\0" * (C.TREE_BLOB_MAX + 1))
    (repo / "pkg" / "small.txt").write_text("hi\n")
    (repo / "Transient").mkdir()
    (repo / "Transient" / "a.py").write_text("junk\n")
    (repo / ".claude" / "hooks").mkdir(parents=True)
    (repo / ".claude" / "hooks" / "guard.py").write_text("print(1)\n")
    (repo / ".claude" / "notes.md").write_text("n\n")
    git(repo, "add", "pkg", "Transient", ".claude")
    git(repo, "commit", "-q", "-m", "head")
    head = git(repo, "rev-parse", "HEAD")
    files = C.critic_tree_files(repo, head, ["pkg/a.py", "Transient/a.py"])
    check("critic tree keeps the changed file and its small neighbours, drops big blobs and Transient/ extras",
          "pkg/a.py" in files and "pkg/small.txt" in files and "pkg/big.bin" not in files
          and not any(f.startswith("Transient/") and f != "Transient/a.py" for f in files), str(files))
    # sandbox gap: a changed selftest that names a sibling mod must find that mod's defs in the critic tree
    sd = repo / "src" / "RimMandrake"
    (sd / "Mine").mkdir(parents=True)
    (sd / "TheSump" / "Defs").mkdir(parents=True)
    (sd / "Other").mkdir()
    (sd / "Mine" / "selftest_mine.py").write_text('import os\np = os.path.join(mods, "TheSump", "Defs", "a.xml")\n')
    (sd / "TheSump" / "Defs" / "a.xml").write_text("<Defs/>\n")
    (sd / "TheSump" / "icon.png").write_bytes(b"\x89PNG")
    (sd / "Other" / "x.xml").write_text("<Defs/>\n")
    git(repo, "add", "src")
    git(repo, "commit", "-q", "-m", "sib")
    head2 = git(repo, "rev-parse", "HEAD")
    f2 = C.critic_tree_files(repo, head2, ["src/RimMandrake/Mine/selftest_mine.py"])
    check("critic tree holds the sibling mod a changed selftest names (text only), not unnamed mods",
          "src/RimMandrake/TheSump/Defs/a.xml" in f2 and "src/RimMandrake/TheSump/icon.png" not in f2
          and "src/RimMandrake/Other/x.xml" not in f2, str(f2))
    # CRITIC_TREE_WIDEN_UNCHANGED_ASSETS: the changed mod's unchanged textures are named, never carried
    (sd / "Art" / "Defs").mkdir(parents=True)
    (sd / "Art" / "Textures").mkdir()
    (sd / "Art" / "Defs" / "a.xml").write_text("<Defs/>\n")
    (sd / "Art" / "Textures" / "RM_Art_east.png").write_bytes(b"\x89PNG")
    git(repo, "add", "src")
    git(repo, "commit", "-q", "-m", "art")
    head3 = git(repo, "rev-parse", "HEAD")
    (sd / "Art" / "Defs" / "a.xml").write_text("<Defs><!-- x --></Defs>\n")
    git(repo, "add", "src")
    git(repo, "commit", "-q", "-m", "art2")
    head4 = git(repo, "rev-parse", "HEAD")
    chg = ["src/RimMandrake/Art/Defs/a.xml"]
    check("asset_roots: a mod is src/<tier>/<mod>; elsewhere the file's directory",
          C.asset_roots(chg + ["pkg/a.py", "src/x.py", "top.py"]) == ["pkg", "src", "src/RimMandrake/Art"],
          str(C.asset_roots(chg + ["pkg/a.py", "src/x.py", "top.py"])))
    png = "src/RimMandrake/Art/Textures/RM_Art_east.png"
    f4 = C.critic_tree_files(repo, head4, chg)
    left = C.unchanged_assets(repo, head4, chg, f4)
    check("unchanged_assets names the texture the tree left out, not what it holds, not another mod's",
          png not in f4 and left == [png], str(left))
    work = Path(tempfile.mkdtemp(prefix="critic_assets_"))
    real = os.environ.get("ARENA_CRITIC_WORK")
    os.environ["ARENA_CRITIC_WORK"] = str(work)

    class TreeCritic:
        needs_tree = True
    cand = {"cid": "x", "prompt": "p", "criteria": "c", "base": head3, "head": head4, "area": ["src/**"]}
    try:
        ci = C.prepare(cand, TreeCritic(), repo)
        check("prepare writes the listing beside the tree, carries no blob, and tells the critic where it is",
              (ci.work / C.ASSET_LIST).read_text().split() == [png] and not (ci.tree / png).exists()
              and ci.diff.startswith("=== FILES NOT IN YOUR TREE") and "../" + C.ASSET_LIST in ci.diff, ci.diff[:300])
        fp = C.critic_fingerprint(C.AcceptAll())
        src = C.unchanged_assets

        def other(repo, head, changed, tree_paths):
            return []
        try:
            C.unchanged_assets = other
            check("a changed listing changes the critic fingerprint", C.critic_fingerprint(C.AcceptAll()) != fp)
        finally:
            C.unchanged_assets = src
    finally:
        os.environ.pop("ARENA_CRITIC_WORK") if real is None else os.environ.update(ARENA_CRITIC_WORK=real)
        shutil.rmtree(work, ignore_errors=True)
    hid = C.hidden_code(repo, base, head, ["pkg/**", ".claude/**"])
    check("hidden_code finds stripped bookkeeping CODE, not bookkeeping prose",
          hid == [".claude/hooks/guard.py"], str(hid))
    check("hidden_code is empty when the area holds no bookkeeping", C.hidden_code(repo, base, head, ["pkg/**"]) == [])


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="selftest_critic_calib_"))
    os.environ["ARENA_METER_HELPERS"] = str(root / "meter_helpers")      # tester captures: not the live arena root
    try:
        repo, base, head = make_repo(root)
        t_maths()
        t_rule(repo, base, head, root)
        t_set(root)
        t_blind(repo, base, head, root)
        t_resume(repo, base, head, root)
        t_sandbox(repo, base, head, root)
        t_network()
        t_persist(repo, base, head)
        t_adjudicate(repo, base, head)
        t_tree_and_hidden(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
