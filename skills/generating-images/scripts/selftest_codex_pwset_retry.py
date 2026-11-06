#!/usr/bin/env python3
"""CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE: a one-off `net.exe user` failure must not read as "unreadable".

On 2026-11-03 artpiped's codex channel flapped 37 times in 12 h on "cannot read 'Password last set' for the
codex sandbox users (net.exe user)"; the read is transient (200 parallel reads on 2026-11-06 all passed). Pins:
  - a net.exe that fails its first read and then answers gives a current reading in ONE call, so
    sandbox_state_current() says True and nothing flaps;
  - a net.exe that never answers is retried NET_READ_TRIES times per user, then the not-ready message names
    the cause (exit code and stderr), never a bare "cannot read";
  - a net.exe that cannot be launched at all names the exception.
Uses a fake net.exe ($CODEX_SANDBOX_NET_EXE) with zero backoff; never touches real net.exe or codex.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codex_image as ci  # noqa: E402

FAKE_NET = r'''#!/usr/bin/env python3
import json, os, sys
state = os.environ["FAKE_NET_STATE"]
st = json.load(open(state))
st["calls"] += 1
json.dump(st, open(state, "w"))
if st["calls"] in st["fail"] or st["fail_all"]:
    print("System error 1722 has occurred.", file=sys.stderr)
    sys.exit(2)
print("User name                    " + sys.argv[2])
print("Password last set            " + st["stamp"])
'''

PWSET = "2026-10-16T17:20:36Z"
FAILED: list[str] = []


def ok(label: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"\n      {detail[-600:]}"))
    if not cond:
        FAILED.append(label)


def _stage(td: Path, fail: list[int], fail_all: bool) -> tuple[Path, Path, Path]:
    fake = td / "fake_net.py"
    fake.write_text(FAKE_NET)
    fake.chmod(0o755)
    state = td / "state.json"
    local = datetime.fromisoformat(PWSET.replace("Z", "+00:00")).astimezone(datetime.now().astimezone().tzinfo)
    state.write_text(json.dumps({"calls": 0, "fail": fail, "fail_all": fail_all,
                                 "stamp": local.strftime("%m/%d/%Y %H:%M:%S")}))
    home = td / "home"
    (home / ".sandbox").mkdir(parents=True)
    (home / ".sandbox-secrets").mkdir()
    (home / ci.SANDBOX_STATE_FILES[0]).write_text(json.dumps({"created_at": PWSET.replace("Z", ".5Z")}))
    (home / ci.SANDBOX_STATE_FILES[1]).write_text("{}")
    return fake, state, home


def _env(fake: Path, state: Path, tries: str | None = None) -> None:
    os.environ.pop(ci.MACHINE_PWSET_ENV, None)
    os.environ.pop(ci.NET_READ_TRIES_ENV, None)
    os.environ[ci.NET_EXE_ENV] = str(fake)
    os.environ["FAKE_NET_STATE"] = str(state)
    if tries is not None:
        os.environ[ci.NET_READ_TRIES_ENV] = tries


def main() -> int:
    ci.NET_READ_BACKOFF_S = (0.0,)
    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        fake, state, home = _stage(td, fail=[1], fail_all=False)

        _env(fake, state, tries="1")
        cur, why = ci.sandbox_state_current(home)
        ok("instance (single-shot read, the pre-fix behaviour): one failed read -> not ready",
           cur is None and "cannot read 'Password last set'" in why, why)

        state.write_text(json.dumps({**json.loads(state.read_text()), "calls": 0}))
        _env(fake, state)
        cur, why = ci.sandbox_state_current(home)
        calls = json.loads(state.read_text())["calls"]
        ok("first read fails, retry answers: ONE call proves the state current", cur is True, why)
        ok("the retry re-read the failed user (2 users + 1 retry = 3 net.exe calls)", calls == 3, f"calls={calls}")
        ok("nothing left in LAST_PWSET_FAILURE after a good read", ci.LAST_PWSET_FAILURE == "", ci.LAST_PWSET_FAILURE)

    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        fake, state, home = _stage(td, fail=[], fail_all=True)
        _env(fake, state)
        cur, why = ci.sandbox_state_current(home)
        calls = json.loads(state.read_text())["calls"]
        ok("net.exe never answers: still not ready (never a pass)", cur is None, why)
        ok(f"net.exe never answers: retried {ci.NET_READ_TRIES} times, then gave up",
           calls == ci.NET_READ_TRIES, f"calls={calls}")
        ok("the not-ready message names the cause (exit code + stderr + attempts)",
           "exit 2" in why and "System error 1722" in why and f"{ci.NET_READ_TRIES} attempts" in why, why)
        guard_ok, guard_why = ci.ensure_home_sandbox(td / "w0", base=home)
        ok("the pre-launch guard refuses and carries the cause into its message",
           guard_ok is False and "System error 1722" in guard_why and "--sync-sandbox" in guard_why, guard_why)

    with tempfile.TemporaryDirectory() as t:
        td = Path(t)
        _fake, state, home = _stage(td, fail=[], fail_all=False)
        _env(td / "no_such_net.exe", state)
        cur, why = ci.sandbox_state_current(home)
        ok("net.exe cannot be launched: not ready, message names the exception",
           cur is None and ("FileNotFoundError" in why or "PermissionError" in why), why)

    for k in (ci.NET_EXE_ENV, ci.NET_READ_TRIES_ENV, "FAKE_NET_STATE"):
        os.environ.pop(k, None)
    print()
    if FAILED:
        print(f"FAILED {len(FAILED)}: " + "; ".join(FAILED))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
