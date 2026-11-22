#!/usr/bin/env python3
"""account_live.py - the one reader of which Claude account a machine is logged in as.

Page: design/specs/2026-11-22-live-account/boundary.md (tests: selftest_account_live.py). The fact is the `live`
field of `claude-account --json status`, on this machine or, with target=, on another one over ssh. Every reader
of it calls read() here; nothing else runs the status or parses it.

read() returns one probe_result answer (rimflow/probe_result.py):
    value(status)          the switcher answered and names its live account: status is its whole JSON object
    empty()                the switcher answered (exit 0, not refused) and names no live account
    could_not_look(cause)  the switcher was not found, could not run, or passed the deadline
    failed(cause)          it ran and broke: a non-zero exit, a refusal ("ok": false), or no status object printed
name_of(answer) -> the account name or None; why_of(answer) -> None on a name, else the cause.

    account_live.py [--target HOST]     print the live account, or UNMEASURED and the cause (exit 0 / 1)
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rimflow"))
import probe_result as PR  # noqa: E402

# A hang guard, far above a real run: the status waits at most 2 s on the switcher's machine lock and took 0.10 to
# 0.14 s on 2026-11-22. A hung switcher or ssh must not stall a timer pass (boundary page, LIMITS).
DEADLINE_S = 60
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]


def exe():
    """The switcher: RM_CLAUDE_ACCOUNT (the one seam, read at call time), else PATH, else ~/.local/bin (systemd's PATH
    lacks ~/.local/bin)."""
    return (os.environ.get("RM_CLAUDE_ACCOUNT") or shutil.which("claude-account")
            or os.path.expanduser("~/.local/bin/claude-account"))


def _run(argv, timeout):
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def _status_object(out):
    """The first JSON object in out that has a `live` key, or None. Text before or after it is skipped."""
    dec, i = json.JSONDecoder(), (out or "").find("{")
    while i >= 0:
        try:
            obj, _ = dec.raw_decode(out[i:])
            if isinstance(obj, dict) and "live" in obj:
                return obj
        except ValueError:
            pass
        i = out.find("{", i + 1)
    return None


def parse(rc, out):
    """Pure: the exit code and stdout of a status run -> a probe_result answer."""
    if rc != 0:
        return PR.failed("claude-account status exited %s" % rc)
    st = _status_object(out)
    if st is None:
        return PR.failed("claude-account status printed no status object" if (out or "").strip()
                         else "claude-account status printed nothing")
    if st.get("ok") is False:
        return PR.failed("claude-account reports not ok: %s" % (st.get("refused") or "no reason given"))
    live = st.get("live")
    if not isinstance(live, str) or not live.strip():
        return PR.empty()
    return PR.value(st)


def read(target=None, exe_path=None, run=None, timeout=DEADLINE_S):
    """The live account of this machine (target None) or of `target` over ssh -> a probe_result answer.
    run(argv, timeout) -> (rc, stdout) is a caller's own world seam; exe_path overrides the switcher's path."""
    if target:
        argv = SSH + [target, "bash -lc " + shlex.quote("claude-account --json status")]
    else:
        argv = [exe_path or exe(), "--json", "status"]
    try:
        rc, out = (run or _run)(argv, timeout)
    except subprocess.TimeoutExpired:
        return PR.could_not_look("claude-account status timed out after %s s" % timeout)
    except FileNotFoundError:
        return PR.could_not_look("%s not found" % ("ssh" if target else "claude-account"))
    except OSError as e:
        return PR.could_not_look("claude-account could not run: %s" % e)
    return parse(rc, out)


def name_of(answer):
    """The live account name, or None (no account named, or the switcher could not be read)."""
    return answer.value["live"] if answer.kind == "value" else None


def why_of(answer):
    """None when a name was read; otherwise why not, in words."""
    if answer.kind == "value":
        return None
    return "claude-account names no live account" if answer.kind == "empty" else answer.cause


def status_of(answer):
    """The whole status object when a name was read, else {}."""
    return answer.value if answer.kind == "value" else {}


def fake_switcher(folder, live):
    """For selftests (point RM_CLAUDE_ACCOUNT at the result): a switcher whose status names `live`. live None -> a
    path that does not exist (the switcher cannot be read)."""
    path = os.path.join(str(folder), "claude-account-%s" % (live or "missing"))
    if live is None:
        return path
    with open(path, "w") as f:
        f.write("#!/bin/sh\necho '%s'\n" % json.dumps({"ok": True, "machine": "testhost", "live": live}))
    os.chmod(path, 0o755)
    return path


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--target", help="read another machine over ssh")
    a = p.parse_args(argv)
    ans = read(a.target)
    print(name_of(ans) or "UNMEASURED (%s)" % why_of(ans))
    return 0 if ans.kind == "value" else 1


if __name__ == "__main__":
    sys.exit(main())
