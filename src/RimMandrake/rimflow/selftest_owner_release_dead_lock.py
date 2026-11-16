#!/usr/bin/env python3
"""RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE: his deliberate release frees his driver lock once its
holder process is gone ("45 minutes after my last interaction, or I deliberately release it", owner by card
2026-10-30). Measured 2026-11-16: the Conductor took the bridge in his name (OWNER driver lock, its process exited),
he said "ok, I'm done", the hold was released with his words - and every take still refused "the OWNER holds the
driver lock" while he kept chatting, and `bridge release` could not clear it ("only the holder releases it").

Staged on throwaway state only (temp ledger, lock, shared file, transcripts, stamp).
  take     (a) a dead OWNER lock + his release (ownerSaid/byCard) after it was acquired: cli and host_guard take it
  release  (b) `bridge release` with his words clears an OWNER lock whose holder is dead
  control  his rule unchanged: no release, a release older than the lock, a release without his words (perRuling,
           why), or a LIVE holder -> refused while he chatted 1 min ago, --force included
"""
import contextlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import types

T = tempfile.mkdtemp(prefix="rf_ownerrel_")
for k in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY", "RIMFLOW_BRIDGE_SEAT",
          "RM_ROLE_UNIT", "RM_HOST", "RM_GAME_INSTANCE", "RM_HOST_GUARD_GEN"):
    os.environ.pop(k, None)
os.makedirs(os.path.join(T, "items"))
os.makedirs(os.path.join(T, "chat"))
LEDGER = os.path.join(T, "events.jsonl")
open(LEDGER, "w").close()
os.environ.update(RIMFLOW_LEDGER=LEDGER, RIMFLOW_ITEMS=os.path.join(T, "items"),
                  RIMFLOW_SHARED_BRIDGE=os.path.join(T, "shared.json"), RIMFLOW_SEAT="BENCH",
                  RIMFLOW_OWNER_CHAT_DIRS=os.path.join(T, "chat"), RIMFLOW_OWNER_TERMINAL="0",
                  RIMFLOW_OWNER_ACT_STAMP=os.path.join(T, "OWNER_LAST_ACT.json"),
                  RIMFLOW_DISPATCH_LOCK=os.path.join(T, "dispatch.lock"),
                  RIMFLOW_BRIDGE_LOCK=os.path.join(T, "bridge.lock"),
                  RIMFLOW_DRIVER_LOCK=os.path.join(T, "DRIVER_LOCK.json"), RM_HOST="archmagi")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import cli, driver_lock as D, host_guard as H, model  # noqa: E402

cli._bind_paths()        # else model.read() is the REAL ledger until the first cli.load() (its real releases pass (a))
FAILS = []
LOCK = os.environ["RIMFLOW_DRIVER_LOCK"]
CHAT = os.path.join(T, "chat")
STAMP = os.environ["RIMFLOW_OWNER_ACT_STAMP"]


def check(ok, msg, detail=""):
    print(("ok    " if ok else "FAIL  ") + msg + ("  [%s]" % str(detail)[:260] if detail and not ok else ""))
    if not ok:
        FAILS.append(msg)


def iso(age_s):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_s))


def clean():
    for p in (LOCK, LOCK + ".op", LOCK + ".gen", os.environ["RIMFLOW_SHARED_BRIDGE"], STAMP):
        if os.path.exists(p):
            os.remove(p)
    for f in os.listdir(CHAT):
        os.remove(os.path.join(CHAT, f))
    open(LEDGER, "w").close()
    for attr in ("OWNER_SAID", "BY_CARD", "PER_RULING", "AGENT_WHY"):
        setattr(model, attr, "")


def gone_identity():
    p = subprocess.Popen(["true"])
    p.wait()
    return {"pid": p.pid, "start": 1.0, "boot_id": D.current_boot_id(), "platform": "wsl", "host": socket.gethostname()}


def live_identity(proc):
    return {"pid": proc.pid, "start": D._proc_start(proc.pid), "boot_id": D.current_boot_id(), "platform": "wsl",
            "host": socket.gethostname()}


def write_lock(ident, acquired_age):
    with open(LOCK, "w") as f:
        json.dump({"seat": "OWNER", "purpose": "owner is walking the review map", "identity": ident,
                   "acquired": iso(acquired_age), "heartbeat": iso(acquired_age), "generation": 1479}, f)


def chat_at(age_s):
    rec = {"type": "user", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - age_s)),
           "origin": {"kind": "human"}, "promptSource": "typed", "turnOrigin": "human",
           "message": {"role": "user", "content": "two hours I'll be gone"}}
    with open(os.path.join(CHAT, "s.jsonl"), "w") as f:
        f.write(json.dumps(rec) + "\n")


_N = [0]


def event(age_s, **fields):
    _N[0] += 1
    t = time.time() - age_s
    ev = dict(fields, ts=iso(age_s), tsn=int(t * 1e9) + _N[0])
    with open(LEDGER, "a") as f:
        f.write(json.dumps(ev) + "\n")


def stage(ident, release=None, acquired_age=1200, release_age=600):
    """His hold as measured 2026-11-16: an OWNER take relayed by a seat, then (release=) a relayed release."""
    clean()
    write_lock(ident, acquired_age)
    event(acquired_age, seat="OWNER", event="bridge", state="taken", purpose="owner walk",
          ownerSaid="stop the visit and show me the human walk map", ranBy="BENCH")
    if release is not None:
        event(release_age, seat="OWNER", event="bridge", state="released", ranBy="BENCH", **release)
    chat_at(60)                                           # he is still chatting: his 45-min clock keeps moving


def gate():
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        return cli._driver_owner_gate("BENCH", model.read())


def script_take(force=None):
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        return H.acquire("RUNNER", "job", path=LOCK, identity=dict(gone_identity(), pid=7, host="elsewhere"),
                         force=force)


def run(fn):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = fn()
    except SystemExit as e:
        rc = e.code
    return rc, out.getvalue()


def lock_seat():
    cur = D._read(LOCK)[0]
    return (cur or {}).get("seat")


SAID = {"ownerSaid": "ok, I'm done"}


def test_take():
    stage(gone_identity(), release=SAID)
    n = len(model.read())
    check(n == 2, "sanity: the ledger read is this test's own (2 events staged)", n)
    if n != 2:
        return
    refusal, cleared = gate()
    check(refusal is None and cleared and "released" in cleared.get("text", ""),
          "take: cli gate clears a dead OWNER lock he released (ownerSaid) after it was acquired", (refusal, cleared))
    real_mirror = cli._mirror_from_ledger
    cli._mirror_from_ledger = lambda *a, **k: "BENCH"
    try:
        args = types.SimpleNamespace(purpose="save the review map", force=None, idle_ok=True, flyer=False)
        rc, out = run(lambda: cli._bridge_take_locked(args, "BENCH", *cli.load()))
    finally:
        cli._mirror_from_ledger = real_mirror
    check(rc in (0, None) and lock_seat() == "BENCH", "take: a delegated `bridge take --idle-ok` then gets the lock",
          (rc, out, lock_seat()))
    stage(gone_identity(), release={"byCard": "Release your hold? -> yes, I'm done"})
    refusal, cleared = gate()
    check(refusal is None and cleared, "take: his release by card counts as deliberate", refusal)
    stage(gone_identity(), release=SAID)
    r = script_take()
    check(r["ok"] and lock_seat() == "RUNNER", "take: a host_guard script take gets a dead OWNER lock he released", r)


def test_controls(sleeper):
    stage(gone_identity())
    refusal, _ = gate()
    check(refusal and "chat prompt" in refusal, "control: a dead OWNER lock he never released still refuses", refusal)
    r = script_take(force="cut")
    check(not r["ok"] and lock_seat() == "OWNER", "control: ...and host_guard refuses it, --force included", r)
    stage(gone_identity(), release=SAID, acquired_age=300, release_age=600)
    refusal, _ = gate()
    check(refusal is not None, "control: a release OLDER than his lock (he took it again) does not clear it", refusal)
    r = script_take()
    check(not r["ok"] and lock_seat() == "OWNER", "control: ...nor for a host_guard take", r)
    for rel in ({"perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"}, {"why": "the walk looks finished"}):
        stage(gone_identity(), release=rel)
        refusal, _ = gate()
        check(refusal is not None, "control: a release without his words (%s) does not clear it" % list(rel)[0],
              refusal)
    stage(gone_identity(), release=SAID)
    event(300, seat="OWNER", event="bridge", state="taken", purpose="one more look", ownerSaid="wait, one more look",
          ranBy="BENCH")
    refusal, _ = gate()
    check(refusal is not None, "control: his take AFTER the release (same lock) keeps it his", refusal)
    stage(live_identity(sleeper), release=SAID)
    refusal, _ = gate()
    check(refusal is not None, "control: a LIVE holder process keeps his lock past a release", refusal)
    r = script_take(force="cut")
    check(not r["ok"] and lock_seat() == "OWNER", "control: ...host_guard included, --force included", r)


def test_release(sleeper):
    real_mirror = cli._mirror_from_ledger
    cli._mirror_from_ledger = lambda *a, **k: None
    try:
        stage(gone_identity(), release=SAID)
        model.OWNER_SAID = "ok, I'm done"
        rc, out = run(lambda: cli._bridge_release_locked("OWNER", cli.load()[1]))
        check(rc in (0, None) and lock_seat() is None,
              "release: `bridge release --owner-said` clears an OWNER lock whose holder is dead", (rc, out, lock_seat()))
        stage(gone_identity(), release=SAID)
        model.PER_RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
        rc, out = run(lambda: cli._bridge_release_locked("OWNER", cli.load()[1]))
        check(lock_seat() == "OWNER", "control: a --per-ruling release (no words of his) leaves his lock", (rc, out))
        stage(live_identity(sleeper), release=SAID)
        model.OWNER_SAID = "ok, I'm done"
        rc, out = run(lambda: cli._bridge_release_locked("OWNER", cli.load()[1]))
        check(lock_seat() == "OWNER", "control: his words do not cut a lock whose holder process LIVES", (rc, out))
    finally:
        cli._mirror_from_ledger = real_mirror
        clean()


def main():
    sleeper = subprocess.Popen(["sleep", "120"])
    try:
        for t in (test_take, test_controls, test_release):
            try:
                t() if t is test_take else t(sleeper)
            except Exception as e:                       # a crash is a failure of that group, never a pass
                check(False, "%s crashed: %r" % (t.__name__, e))
    finally:
        sleeper.kill()
        shutil.rmtree(T, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
