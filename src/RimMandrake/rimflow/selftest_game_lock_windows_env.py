#!/usr/bin/env python3
"""selftest_game_lock_windows_env.py - a Windows python.exe that cannot find its data root is UNMEASURED, not a FAIL.

RIMMANDRAKE_QUIET_GAME_LOCK_ENV_RED_REFUSES_STEVEDESKTOP_PUBLISH: on SteveDesktop the Windows python.exe has no
RM_DATA_ROOT, so rmpaths raises RmDataRootUnset ("Windows python cannot run Lodestar's helper") inside the probe.
selftest_game_lock_windows_python.py then read the probe's traceback as a lock result and FAILed, with a text that moved
between runs, so ./publish there read it as a new red (2026-11-24, twice). The machine's environment is not the lock's
behaviour: the harness says UNMEASURED (exit 2) and names the cause. No python.exe runs here: the reply is stubbed.

    python3 src/RimMandrake/rimflow/selftest_game_lock_windows_env.py
"""
import contextlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_game_lock_windows_python as W  # noqa: E402

FAILS = []
TRACE = ('Traceback (most recent call last):\n  File "C:\\\\x\\\\probe.py", line 3, in <module>\n'
         'rmpaths.RmDataRootUnset: set RM_DATA_ROOT (e.g. D:\\\\ClaudeWork\\\\rimmandrake) or LODESTAR_ROOT in the user '
         "environment; Windows python cannot run Lodestar's helper\n")


def check(ok, what, got=""):
    print(("ok    " if ok else "FAIL  ") + what + ("" if ok else "  (%s)" % (got,)))
    if not ok:
        FAILS.append(what)


def probe_with(reply):
    real = W.subprocess.run
    W.subprocess.run = lambda *a, **k: reply
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            got = W.probe(os.path.join(W.TMP, "lock.json"))
        return "returned", got, out.getvalue()
    except SystemExit as e:
        return "exit %s" % e.code, None, out.getvalue()
    finally:
        W.subprocess.run = real


def t_an_unset_data_root_is_unmeasured():
    how, got, said = probe_with(subprocess.CompletedProcess(["python.exe"], 1, "", TRACE))
    check(how == "exit 2" and "UNMEASURED" in said and "RM_DATA_ROOT" in said,
          "an-unset-data-root-is-unmeasured: the probe exits 2 and names RM_DATA_ROOT", (how, got, said[-200:]))


def t_a_real_reply_is_still_read():
    line = '{"os": "nt", "lock": "x", "crossing": "held", "new_run": null, "client": null, "alive": null}'
    how, got, _ = probe_with(subprocess.CompletedProcess(["python.exe"], 0, line + "\n", ""))
    check(how == "returned" and got.get("crossing") == "held", "a-real-reply-is-still-read", (how, got))


def main():
    for t in (t_an_unset_data_root_is_unmeasured, t_a_real_reply_is_still_read):
        t()
    print("selftest_game_lock_windows_env: %s" % ("FAILED %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
