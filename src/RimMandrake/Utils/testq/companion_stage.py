#!/usr/bin/env python3
"""companion_stage.py - keep a FRESH JawaBench companion staged on SteveDesktop for origin/main. No LLM.

COMPANION_STAGE_FIX_JOBS_ARRIVE_STALE (and STEVE_COMPANION_WIRE_STAGE_HAND_CRANKED). The worker refuses a job whose
companion is not built from the job's sources (STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES), and the only thing that
staged one was a person. So each commit to the companion's sources failed every later job at deploy, and two filler
jobs tripped the brake (J20261101T215632Z-85a7de, J20261103T093058Z-dcd4da, J20261103T215041Z-3b04b3).

    companion_stage.py run      one pass; testq-tick.service runs it after its pull, before `tick` and `fill`
    companion_stage.py status   the live answer over ssh: wanted hash, inbox, game copy (exit 0 when ready)
    companion_stage.py proof    read-only: this fix held on the real lane (exit 0, else 1)

A pass hashes the companion sources at origin/main (companion_identity). Unchanged since the last staging: no ssh, no
build. Changed: if SteveDesktop's inbox or game copy already embeds that hash nothing is sent; otherwise build.py --gm
here (~14 s measured) and sync_test_mods.companion into the inbox, then read it back. A failed build is retried after
RETRY_S, not every tick. Reading: QHOME/companion_stage.json, rewritten every pass, state:
  staged       the wanted hash is on SteveDesktop (`how`: unchanged, present, built)
  unread       ssh could not read SteveDesktop: said, tried again next pass
  behind       this clone's sources are not origin/main's (a failed pull): nothing built
  failed       the build or the push failed (`reason`, `log`)
  unmeasured   the sources at origin/main could not be hashed

The filler reads that file (testq.companion_hold) and holds rather than spend a job, and `fill_plan` says so as verdict
`companion`, which the steward turns into a fault after a grace. No file at all means this tool never ran: no hold, and
the worker's own refusal still stands. Live, at admission, a filler job at a sha whose companion left SteveDesktop in
the meantime is cancelled (testq.admit), which the brake does not count.
"""
import argparse
import contextlib
import io
import json
import os
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "infrastructure", "stevedesktop"))
import schema as S  # noqa: E402
import sync_test_mods as M  # noqa: E402  (imports companion_identity)
import testq as T  # noqa: E402

CI = M.CI
STATE = "companion_stage.json"
LOG = "companion_stage.log"
RETRY_S = 1800              # a build that failed is not retried every tick
BUILD_TIMEOUT_S = 420       # the tick's TimeoutStartSec is 900; winbuild queues on a shared stage lock
FIXED_AT = "2026-11-03T22:40:00Z"   # `proof` counts only jobs finished after this fix began
PROOF_MAX_AGE_S = 7200
_READER = ("import re,sys\n"
           "for p in sys.argv[1:]:\n"
           "    try:\n"
           "        b=open(p,'rb').read()\n"
           "    except OSError:\n"
           "        print('absent'); continue\n"
           "    m=re.search(rb'%s\\x40([0-9a-f]{64})',b)\n"
           "    print(m.group(1).decode() if m else 'none')\n" % CI.META_KEY)


def state():
    return T.read_json(T.q(STATE))


def wanted(rev="origin/main"):
    return CI.srchash_at(M.REPO, rev)


def remote_paths():
    return {"inbox": M.INBOX + "/" + CI.DLL_NAME, "game": M.GAME + "/BridgeTools/JawaBench/" + CI.DLL_NAME}


def probe():
    """-> {"inbox": hash|"none"|"absent", "game": ...} as embedded on SteveDesktop, or None when it could not be read.
    A remote python, because a size or a sha256 cannot say which sources built a DLL."""
    paths = remote_paths()
    cmd = "python3 -c %s %s %s" % (shlex.quote(_READER), shlex.quote(paths["inbox"]), shlex.quote(paths["game"]))
    try:
        r = subprocess.run(M.SSH + [cmd], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    lines = r.stdout.split()
    if r.returncode or len(lines) != 2 or not all(x in ("none", "absent") or (len(x) == 64 and set(x) <= set("0123456789abcdef"))
                                                  for x in lines):
        return None
    return {"inbox": lines[0], "game": lines[1]}


def build():
    """Build the companion in this clone -> None, or why not. TESTQ_COMPANION_BUILD replaces the command (selftests)."""
    cmd = os.environ.get("TESTQ_COMPANION_BUILD")
    argv = shlex.split(cmd) if cmd else [sys.executable, os.path.join(M.REPO, "src", "RimMandrake", "bridgetools", "build.py"), "--gm"]
    try:
        with open(T.q(LOG), "w") as f:
            r = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT, cwd=M.REPO, timeout=BUILD_TIMEOUT_S)
    except (subprocess.TimeoutExpired, OSError) as e:
        return "build did not finish: %s" % str(e)[:200]
    return None if r.returncode == 0 else "build.py exit %d (%s)" % (r.returncode, T.q(LOG))


def stage(want):
    """Build and push -> None, or why not."""
    why = build()
    if why:
        return why
    v = CI.verdict(os.path.join(M.ARTIFACT, CI.DLL_NAME), M.REPO, "HEAD", want=want)
    if v["state"] != "FRESH":
        return "the build is not fresh: " + CI.describe(v)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc = M.companion(True)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
        return "push failed: %s" % str(e)[:200]
    if rc:
        return "sync_test_mods.companion refused: " + out.getvalue().strip()[-300:]
    got = probe()
    if not got or want not in got.values():
        return "pushed, but SteveDesktop does not read back %s: %s" % (want[:12], got)
    return None


def decide(now):
    """-> the record of this pass (run's body; the record carries `at`, the epoch this state and want began)."""
    prev = state() or {}
    sha = subprocess.run(["git", "-C", M.REPO, "rev-parse", "--short", "origin/main"], capture_output=True, text=True,
                         timeout=60).stdout.strip()
    want = wanted()
    rec = {"want": want, "sha": sha}
    if want is None:
        return dict(rec, state="unmeasured", reason="cannot hash %s at origin/main in %s" % (CI.SRC_REL, M.REPO))
    if prev.get("state") == "staged" and prev.get("want") == want:
        return dict(rec, state="staged", how="unchanged", staged_at=prev.get("staged_at"))
    got = probe()
    if got is None:
        return dict(rec, state="unread", reason="could not read SteveDesktop over ssh")
    rec.update(got)
    if want in got.values():
        return dict(rec, state="staged", how="present", staged_at=S.utcnow())
    if prev.get("state") == "failed" and prev.get("want") == want and now - (prev.get("tried") or 0) < RETRY_S:
        return dict(rec, state="failed", reason=prev.get("reason"), tried=prev.get("tried"), log=T.q(LOG))
    if CI.srchash_worktree(M.REPO) != want:
        return dict(rec, state="behind", reason="%s is not at origin/main's companion sources" % M.REPO)
    why = stage(want)
    if why:
        T.log("companion_stage: %s FAILED: %s" % (want[:12], why))
        return dict(rec, state="failed", reason=why, tried=now, log=T.q(LOG))
    T.log("companion_stage: staged %s (origin/main %s)" % (want[:12], sha))
    got = probe() or got
    rec.update(got)
    return dict(rec, state="staged", how="built", staged_at=S.utcnow())


def run_pass(now=None):
    now = time.time() if now is None else now
    prev = state() or {}
    rec = decide(now)
    same = (prev.get("state"), prev.get("want")) == (rec["state"], rec["want"])
    rec.update(ts=S.utcnow(), epoch=now, since=prev.get("since", now) if same else now)
    S.dump(rec, T.q(STATE))
    return rec


def hold_reason(st, rev="origin/main"):
    """Why the filler may not submit at `rev` given the record `st`, or None. Reads no ssh: fill_plan runs every tick."""
    want = wanted(rev)
    if want is None:
        return "companion hold: cannot hash its sources at %s" % rev
    if st.get("want") != want:
        return "companion hold: sources at %s hash %s, the stager last saw %s" % (rev, want[:12], (st.get("want") or "none")[:12])
    if st.get("state") != "staged":
        return "companion hold: %s for %s: %s" % (st.get("state"), want[:12], str(st.get("reason"))[:200])
    return None


def unready_at(sha):
    """Live: why a job at `sha` cannot pass deploy, or None (also when that cannot be read: the worker still judges)."""
    want = wanted(sha)
    got = probe() if want else None
    if not got or want in got.values():
        return None
    return "companion for %s not on SteveDesktop: its sources hash %s, inbox %s, game %s" % (
        sha, want[:12], got["inbox"][:12], got["game"][:12])


def proof(now=None):
    """-> (ok, [lines]). The item's own bar: a filler job passed deploy FRESH (a canary proves the lane, not that the
    filler reaches it), the lane left BRAKED, and the stager is alive. A later, unrelated brake (its tail newer than the
    proving job) does not un-prove this fix."""
    now = time.time() if now is None else now
    lines, ok = [], True
    st = state() or {}
    age = now - (st.get("epoch") or 0)
    good = st.get("state") == "staged" and age < PROOF_MAX_AGE_S
    ok &= good
    lines.append("%s stager: %s want %s, %.0f s old" % ("ok  " if good else "FAIL", st.get("state"), str(st.get("want"))[:12], age))
    since = S.parse_ts(FIXED_AT)
    best = None
    for rec in T.records("done"):
        job, res = T.job_of(rec), rec.get("result") or {}
        comp = (res.get("deployed") or {}).get("companion") or {}
        if job.get("requested_by") != T.FILLER or comp.get("state") != "FRESH":
            continue
        try:
            fin = S.parse_ts(rec.get("finished") or res["finished"])
        except (KeyError, TypeError, ValueError):
            continue
        if fin > since and (best is None or fin > best[0]):
            best = (fin, job["id"], job["requested_by"], res.get("outcome"))
    ok &= bool(best)
    lines.append(("ok   job %s (%s) passed deploy with companion FRESH, outcome %s" % best[1:]) if best else
                 "FAIL no filler job has passed deploy with companion FRESH since %s" % FIXED_AT)
    sj = T.read_json(T.q("steward.json")) or {}
    held = sj.get("state") == "BRAKED"
    if held and best:
        fins = []
        for j in sj.get("jobs") or []:
            r = T.read_json(T.q("done", str(j) + ".json")) or {}
            try:
                fins.append(S.parse_ts(r.get("finished") or r["result"]["finished"]))
            except (KeyError, TypeError, ValueError):
                fins.append(0)
        held = not fins or min(fins) <= best[0]     # a tail newer than the proof is a new brake, not this one
    ok &= not held
    lines.append("%s steve.state %s: %s" % ("FAIL" if held else "ok  ", sj.get("state"), str(sj.get("reason"))[:160]))
    return ok, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", nargs="?", default="run", choices=("run", "status", "proof"))
    a = ap.parse_args(argv)
    if a.verb == "run":
        rec = run_pass()
        print("companion_stage: %s %s %s" % (rec["state"], str(rec["want"])[:12], rec.get("how") or rec.get("reason") or ""))
        return 0
    if a.verb == "status":
        want, got = wanted(), probe()
        print(json.dumps({"want": want, "steve": got, "record": state()}, sort_keys=True))
        return 0 if got and want in got.values() else 1
    ok, lines = proof()
    print("\n".join(lines))
    print("PROOF " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
