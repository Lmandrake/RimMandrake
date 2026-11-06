#!/usr/bin/env python3
"""ARTPIPED_CODEX_LATCH_RETRY_ONE_BLIP_SINKS: one unreadable net.exe 'Password last set' must not latch codex off.

2026-11-02 21:06 PST: a single `net.exe user` read failed inside a worker's pre-launch sandbox guard, the
daemon latched `codex_sandbox_ok=False` for the rest of its run, and 29 codex jobs sat 'nothing claimable' for
50 min until a restart. That daemon had started at 20:53, before the housekeeping re-preflight
(ARTPIPE_ORPHAN_UNSTICK_WEDGE, 20:55) existed. These scenarios pin the behaviour on a RUNNING daemon, with a fake
net.exe (`$CODEX_SANDBOX_NET_EXE`) instead of the fixed `$CODEX_SANDBOX_MACHINE_PWSET` pin, so one read can fail
and the next pass:
  - a blip in the worker's guard -> job back to pending, channel off, re-preflight passes, job renders;
  - a blip in the startup preflight -> channel off, re-preflight passes, job renders;
  - a read that keeps failing -> the re-preflight is retried but the channel stays off (the latch holds).
Never touches real codex or the real net.exe.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_artpipe as base  # noqa: E402

FAKE_NET = r'''#!/usr/bin/env python3
import fcntl, json, os, sys
state = os.environ["FAKE_NET_STATE"]
with open(state, "r+") as fh:
    fcntl.flock(fh, fcntl.LOCK_EX)
    st = json.load(fh)
    st["calls"] += 1
    n = st["calls"]
    fh.seek(0); fh.truncate(); json.dump(st, fh)
fail = n in st["fail"] or (st.get("fail_from") is not None and n >= st["fail_from"])
if fail:
    print("System error 5 has occurred.", file=sys.stderr)
    sys.exit(2)
print("User name                    " + sys.argv[2])
print("Password last set            " + st["stamp"])
'''


def _local_stamp(iso_utc: str) -> str:
    """The pinned UTC provisioning as net.exe prints it: local wall time at TODAY's offset (the parser's rule)."""
    utc = datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
    return utc.astimezone(datetime.now().astimezone().tzinfo).strftime("%m/%d/%Y %H:%M:%S")


def _scenario(td: Path, job_id: str, fail: list[int], fail_from: int | None, wait_done: bool):
    q = base.Queue(td)
    fake = td / "fake_net.py"
    fake.write_text(FAKE_NET)
    fake.chmod(0o755)
    state = td / "fake_net_state.json"
    state.write_text(json.dumps({"calls": 0, "fail": fail, "fail_from": fail_from,
                                 "stamp": _local_stamp(base.SANDBOX_PWSET_PINNED)}))
    base.make_job(q.pending, job_id, q.reference, channel="codex")
    (q.root / "control.json").write_text(json.dumps({job_id: "ok"}))
    env = dict(os.environ)
    env.pop("CODEX_SANDBOX_MACHINE_PWSET", None)  # the fake net.exe is the instrument here, not the pin
    env.update({"ARTPIPE_LEGIBILITY_THRESHOLDS": "", "ARTPIPE_MOCK_CONTROL": str(q.root / "control.json"),
                "CODEX_SANDBOX_SEED": str(q.codex_sandbox_template),
                "CODEX_SANDBOX_NET_EXE": str(fake), "FAKE_NET_STATE": str(state),
                "ARTPIPE_HOUSEKEEPING_S": "0.5", "ARTPIPE_PREFLIGHT_RECHECK_S": "0.5"})
    log = q.root / "daemon.out"
    with open(log, "w") as fh:
        proc = subprocess.Popen(q.daemon_args("--workers", "1"), stdout=fh, stderr=subprocess.STDOUT,
                                text=True, env=env)
    try:
        deadline = time.time() + (40 if wait_done else 6)
        while time.time() < deadline and not (q.done / f"{job_id}.json").is_file():
            time.sleep(0.2)
        time.sleep(0.5)
        alive = proc.poll() is None
        calls = json.loads(state.read_text())["calls"]
        return q, log.read_text(), alive, calls
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_worker_guard_blip_reenables_codex():
    """Startup preflight reads net.exe twice (calls 1-2, both users) and passes; the worker's guard makes
    call 3, which fails once. The same daemon must re-enable codex and render the job."""
    with tempfile.TemporaryDirectory() as td:
        q, out, alive, calls = _scenario(Path(td), "blipworker", fail=[3], fail_from=None, wait_done=True)
        base.ok("worker blip: startup preflight passed on the fake net.exe", "codex sandbox ok" in out, out)
        base.ok("worker blip: the one failed read disabled codex from the worker's guard",
                "sandbox not ready" in out and "cannot read 'Password last set'" in out, out)
        base.ok("worker blip: the same running daemon re-enabled codex",
                "codex channel re-enabled" in out and alive, out)
        base.ok("worker blip: the waiting codex job rendered to done/ without a restart",
                (q.done / "blipworker.json").is_file(), out)


def test_startup_preflight_blip_reenables_codex():
    """The startup preflight's first net.exe read fails once; the re-preflight passes and the job renders."""
    with tempfile.TemporaryDirectory() as td:
        q, out, alive, calls = _scenario(Path(td), "blipstart", fail=[1], fail_from=None, wait_done=True)
        base.ok("startup blip: the failed read disabled codex at startup",
                "codex channel disabled" in out and "cannot read 'Password last set'" in out
                and "codex sandbox ok" not in out, out)
        base.ok("startup blip: the same running daemon re-enabled codex",
                "codex channel re-enabled" in out and alive, out)
        base.ok("startup blip: the waiting codex job rendered to done/",
                (q.done / "blipstart.json").is_file(), out)


def test_persistent_read_failure_keeps_codex_off():
    """net.exe never answers: the re-preflight keeps being retried (more reads than the startup one) but the
    channel is never re-enabled and the job stays pending — the latch holds for a real, lasting failure."""
    with tempfile.TemporaryDirectory() as td:
        q, out, alive, calls = _scenario(Path(td), "neverread", fail=[], fail_from=1, wait_done=False)
        base.ok("persistent failure: codex disabled at startup", "codex channel disabled" in out, out)
        base.ok("persistent failure: re-preflight was retried on the backoff", calls >= 3, f"net.exe calls={calls}")
        base.ok("persistent failure: codex never re-enabled", "codex channel re-enabled" not in out, out)
        base.ok("persistent failure: the job is still pending, nothing rendered or failed",
                (q.pending / "neverread.json").is_file() and not (q.done / "neverread.json").exists()
                and not (q.failed / "neverread.json").exists(), out)


def main() -> int:
    for fn in (test_worker_guard_blip_reenables_codex, test_startup_preflight_blip_reenables_codex,
               test_persistent_read_failure_keeps_codex_off):
        print(f"--- {fn.__name__} ---")
        try:
            fn()
        except Exception as exc:
            base.FAILED.append(fn.__name__)
            print(f"FAIL  {fn.__name__} raised {type(exc).__name__}: {exc}")
    print()
    if base.FAILED:
        print(f"{len(base.FAILED)} FAILED: {', '.join(base.FAILED)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
