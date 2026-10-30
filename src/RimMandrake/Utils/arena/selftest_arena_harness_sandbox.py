#!/usr/bin/env python3
"""selftest_arena_harness_sandbox: every hook where a loop HARNESS runs clone-controlled code is blind to the answer
holders (item ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE).

A builder can rewrite any file of its clone. A payload is planted in each hook that runs one and tries to read a
retired tree (list /home/mandrake/rm/retired-trees, `git for-each-ref refs/arena/old/` in each tree), the notes root
(D:\\ClaudeWork) and the bench/foundry clones; it reports what it saw. Hooks:
  H1 precheck   ralph_a default_precheck, trio precheck_t, ralph_c precheck_c   (the clone's run_selftests.py)
  H2 release    ralph_a default_release                                         (the clone's rimflow cli.py)
  H3 publish    Loop._publish default = harness_publish (never the clone's ./publish; a clone publish_cmd refused)
  H4 gate       arena_gate strict steps: tests/proof (data ro), xml/deploy_plan (game ro), and its deny probe
CONTROL: the same payload run by the harness unsandboxed must see the retired tree (else the instrument is blind and
the run is UNMEASURED, never a pass)."""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arm_sandbox as AS  # noqa: E402

FAILS: list[str] = []
RETIRED = "/home/mandrake/rm/retired-trees"

PAYLOAD = r'''
import glob, json, os, subprocess, sys
R = %(retired)r
seen = {}
try:
    seen["retired"] = sorted(os.listdir(R))[:3]
except OSError:
    seen["retired"] = []
n = 0
for d in glob.glob(os.path.join(R, "*-git-*")):
    n += len(subprocess.run(["git", "-C", d, "for-each-ref", "refs/arena/old/"], capture_output=True,
                            text=True).stdout.splitlines())
seen["refs"] = n
for k, p in (("claudework", %(cw)r), ("foundry", "/home/mandrake/rm/foundry"), ("bench", "/home/mandrake/rm/bench")):
    try:
        seen[k] = bool(os.listdir(p))
    except OSError:
        seen[k] = False
line = "HSPROBE " + json.dumps(seen, sort_keys=True)
print(line)
out = os.environ.get("HS_OUT") or %(out)r
if out:
    try:
        with open(out, "w") as f:
            f.write(line + "\n")
    except OSError:
        pass
'''


def payload(out=""):
    return PAYLOAD % {"retired": RETIRED, "cw": AS.CLAUDEWORK, "out": out}


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def probe_of(text):
    m = re.findall(r"^HSPROBE (\{.*\})$", text or "", re.M)
    return json.loads(m[-1]) if m else None


def blind(got):
    return got is not None and not got["retired"] and not got["refs"] and not any(
        got[k] for k in ("claudework", "foundry", "bench"))


def mk_clone(tmp, name):
    """A tiny git clone whose run_selftests.py / rimflow cli.py / ./publish / proof are payloads."""
    c = tmp / name
    (c / "src/RimMandrake/Utils").mkdir(parents=True)
    (c / "src/RimMandrake/rimflow").mkdir(parents=True)
    (c / "src/RimMandrake/Utils/run_selftests.py").write_text(payload() + 'print("RESULT: GREEN (payload)")\n')
    (c / "src/RimMandrake/rimflow/cli.py").write_text(payload(str(c / "release_saw.txt")))
    (c / "src/RimMandrake/Utils/selftest_hs_payload.py").write_text(payload())
    pub = c / "publish"
    pub.write_text("#!/bin/sh\ntouch '%s'\n" % (c / "PUBLISH_PAYLOAD_RAN"))
    pub.chmod(0o755)
    git("init", "-q", "-b", "main", str(c))
    git("-C", str(c), "add", "-A")
    git("-C", str(c), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "payload")
    return c


def control(tmp):
    """The instrument can see: the payload run by the harness itself, unsandboxed, sees the retired refs."""
    r = subprocess.run([sys.executable, "-c", payload()], capture_output=True, text=True, timeout=120)
    got = probe_of(r.stdout)
    ok = bool(got and got["retired"] and got["refs"])
    if ok:
        check(True, "CONTROL unsandboxed payload sees the retired tree (%s refs)" % got["refs"])
    return ok


def h1_precheck(tmp, RA):
    import ralph_c_loop as RC
    import trio_loop as TL
    c = mk_clone(tmp, "h1")
    for name, fn in (("ralph_a default_precheck", RA.default_precheck), ("trio precheck_t", TL.precheck_t),
                     ("ralph_c precheck_c", RC.precheck_c)):
        log = tmp / ("pre_%s.log" % name.split()[0])
        v = fn(c, log)
        got = probe_of(log.read_text())
        check(blind(got), "H1 %s: the clone's run_selftests.py payload ran and saw nothing (%s)" % (name, got))
        check((v[0] if isinstance(v, tuple) else v) is True, "H1 %s: its green RESULT still reads green (%s)" % (name, v))
    # a refused sandbox is a red pre-check, never an unsandboxed run
    real = RA.CmdModel.wrap
    RA.CmdModel.wrap = staticmethod(lambda *a, **k: (_ for _ in ()).throw(RA.Refused("planted refusal")))
    try:
        log = tmp / "pre_refused.log"
        v = RA.default_precheck(c, log)
        check(v[0] is False and probe_of(log.read_text()) is None,
              "H1 refused sandbox: pre-check red and the payload never ran (%s)" % (v,))
    finally:
        RA.CmdModel.wrap = real


def h2_release(tmp, RA):
    c = mk_clone(tmp, "h2")
    RA.default_release(c)
    f = c / "release_saw.txt"
    got = probe_of(f.read_text()) if f.exists() else None
    check(got is not None, "H2 release: the clone's rimflow cli.py payload ran (it wrote %s)" % f.name)
    check(blind(got), "H2 release: the payload saw nothing (%s)" % (got,))


def h3_publish(tmp, RA):
    c = mk_clone(tmp, "h3")
    bare = tmp / "h3_origin.git"
    git("init", "-q", "--bare", "-b", "main", str(bare))
    ctl = tmp / "h3_ctl"
    ctl.mkdir()
    (ctl / "origin.url").write_text(str(bare) + "\n")
    for bad in ("./publish", "%s publish" % sys.executable, "%s/publish" % c, "sh ./publish --x"):
        try:
            RA.Loop(c, tmp / "h3_ctl_bad", [], model=RA.CmdModel("true"), publish_cmd=bad, sync=None)
            check(False, "H3 publish_cmd %r (clone code) refused at construction" % bad)
        except RA.Refused:
            check(True, "H3 publish_cmd %r (clone code) refused at construction" % bad)
    lp = RA.Loop(c, ctl, [], model=RA.CmdModel("true"), sync=None)
    ok, why = lp._publish()
    head = git("-C", str(c), "rev-parse", "main").stdout.strip()
    check(ok and git("-C", str(bare), "rev-parse", "main").stdout.strip() == head,
          "H3 default publish pushed the tested main to the pinned origin (%s)" % why)
    check(not (c / "PUBLISH_PAYLOAD_RAN").exists(), "H3 the clone's ./publish payload never ran")
    (ctl / "origin.url").unlink()
    git("-C", str(c), "config", "url.%s.insteadOf" % bare, "evil:")
    git("-C", str(c), "remote", "add", "origin", "evil:x")
    ok, why = RA.harness_publish(c, None)
    check(not ok and "refused" in why, "H3 a clone that redirects URLs is refused, not pushed (%s)" % why)


def h4_gate(tmp):
    import arena_eventlog as L
    import arena_gate as G
    import arena_tasks as A
    root = tmp / "h4"
    os.environ["ARENA_ROOT"] = str(root / "arena")
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(root / "secret" / "event_token")
    p = A.paths()
    L.init_token(p)
    repo = mk_clone(root, "repo")
    base = git("-C", str(repo), "rev-parse", "HEAD").stdout.strip()
    (repo / "src/RimMandrake/Utils/selftest_hs_payload.py").write_text(payload() + "# head\n")
    git("-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "head")
    head = git("-C", str(repo), "rev-parse", "HEAD").stdout.strip()
    task = {"id": "T1", "area": ["src/RimMandrake/Utils/**"], "live": "none",
            "proof": "python3 src/RimMandrake/Utils/selftest_hs_payload.py"}
    g = G.Gate(task, base, head, "armx", repo, p, workdir=root / "gw", defs_roots=[])
    g.checkout()
    g.sandbox_probe()
    check(g.sandbox_why == "", "H4 gate sandbox probe (incl. the arm_sandbox deny paths) passes: %r" % g.sandbox_why)
    check(g.deny_probe() == [], "H4 gate deny probe: no arm_sandbox deny path visible in a strict step")
    py = g.python
    pl = str(g.clone / "src/RimMandrake/Utils/selftest_hs_payload.py")
    for name, kw in (("tests (data ro)", {"data_rw": False}), ("xml/deploy_plan (game ro)", {"ro_extra": g.game_ro()}),
                     ("default", {})):
        rc, text = g.srun([py, pl], g.logdir / ("hs_%d.log" % len(name)), **kw)
        got = probe_of(text)
        check(rc == 0 and blind(got), "H4 gate strict step %s: payload ran (rc %s) and saw nothing (%s)" % (name, rc, got))
    st = g.s_proof()
    log = st.get("log") or str(g.logdir / "proof_0.log")
    got = probe_of(Path(log).read_text()) if Path(log).exists() else None
    check(got is not None and blind(got), "H4 gate s_proof: the clone's proof payload ran and saw nothing (%s, %s)"
          % (st.get("verdict") or st.get("status"), got))
    real = G.AS.CONTAINERS                     # a missed mask (/mnt left open: D:\ClaudeWork shows) must refuse the gate
    G.AS.CONTAINERS = tuple(x for x in real if x != "/mnt")
    try:
        g.sandbox_why = ""
        g.sandbox_probe()
    finally:
        G.AS.CONTAINERS = real
    check("masked path" in g.sandbox_why and AS.CLAUDEWORK in g.sandbox_why,
          "H4 a strict step that can see D:\\ClaudeWork is refused by the gate's probe (%r)" % g.sandbox_why[:160])
    g.sandbox_why = ""
    env = g.env()
    check(env.get("RM_DATA_ROOT") == os.path.realpath(g.work / "data"),
          "H4 a strict step's RM_DATA_ROOT is the gate's private data dir, not D:\\ClaudeWork (%s)" % env.get("RM_DATA_ROOT"))


def static_sites():
    """No loop harness runs a clone path directly any more (all through run_clone_code / harness_publish)."""
    bad = []
    for f in ("ralph_a_loop.py", "trio_loop.py", "ralph_c_loop.py"):
        for i, ln in enumerate((HERE / f).read_text().splitlines(), 1):
            if re.search(r"subprocess\.(run|Popen)\(\[sys\.executable, \"src/", ln) or \
                    re.search(r"subprocess\.run\(shlex\.split\(self\.publish_cmd\)", ln) and f != "ralph_a_loop.py":
                bad.append("%s:%d" % (f, i))
    check(not bad, "S no unsandboxed clone-code launch left in the loops (%s)" % bad)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_harness_sandbox_"))
    os.environ["RM_ARM_SANDBOX_SCRATCH"] = str(tmp / "armscratch")
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE")}
    try:
        static_sites()
        if not control(tmp):
            print("UNMEASURED: the unsandboxed control cannot see %s; a blind payload proves nothing" % RETIRED)
            return 1 if FAILS else 0
        import ralph_a_loop as RA
        for fn, a in ((h1_precheck, (tmp, RA)), (h2_release, (tmp, RA)), (h3_publish, (tmp, RA)), (h4_gate, (tmp,))):
            try:
                fn(*a)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
