#!/usr/bin/env python3
"""selftest_install_wt_seat_profiles.py — the WT seat profiles start the wake ritual unattended.

Owner, 2026-10-28 14:13 PDT: "Why did we not start up bench or foundry upon wake? The agents reappered but static.
... Then let's fix the wake ritual to start the agent." Every launch of the AGENT BENCH / AGENT FOUNDRY tiles (cold
boot via the fleet shortcut, `claude-account use` relaunch, seat_loop.sh's first launch) must carry a first prompt, so
the seat begins work without anyone typing. Covered, on build() only (nothing is read or written outside memory):
  plain path     seat_restart off: the commandline is LAUNCH + one single-quoted first prompt, then `exec $SHELL -l`
  wrapped path   seat_restart on: seat_loop.sh's FIRST launch carries a first prompt that runs `seat_restart.py wake`
  wording        BENCH's prompt runs handoff.py --wake + seat ready and reports; FOUNDRY's also runs `rimflow next`
  quoting        the prompt sits inside `bash -lc "..."` in a JSON string: no quote, $, backtick, backslash or !
  untouched      HESTIA, EMERGENCY, SERVER and ARTIST get no first prompt; LAUNCH itself is unchanged (seat_restart
                 and the dispatcher's recover argv compare against it)
"""
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install_wt_seat_profiles as W  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def inner_of(commandline):
    m = re.fullmatch(r'wsl\.exe -d \S+ -- bash -lc "(.*)"', commandline)
    return m.group(1) if m else None


def launch_argv(inner, wrapped):
    """The claude_bounded.sh argv bash will see, from the `cd … && export … && <launch>` inner string."""
    if inner.endswith(W.SHELL_TAIL):
        inner = inner[:-len(W.SHELL_TAIL)]
    tail = inner.split(" && ")[-1]
    argv = shlex.split(tail)
    if wrapped:
        argv = argv[2:]            # seat_loop.sh SEAT
    return argv


def build_with(seats_on, seat):
    real = W.restart_seats
    try:
        W.restart_seats = lambda path=None: set(seats_on)
        return W.build(seat)[0]["commandline"]
    finally:
        W.restart_seats = real


SAFE = re.compile(r"[A-Za-z0-9 .,:/_\-]+")


def test_plain_path_has_first_prompt():
    for seat in ("BENCH", "FOUNDRY"):
        cl = build_with((), seat)
        inner = inner_of(cl)
        check(inner is not None and inner.endswith(W.SHELL_TAIL), f"{seat} plain: still drops to a login shell")
        argv = launch_argv(inner, wrapped=False)
        rc = argv.index("--remote-control")
        want = "CONDUCTOR" if seat == "BENCH" else f"AGENT {seat}"   # CONDUCTOR_RCNAME_RENAME_DISPATCHER_ALIAS
        check(argv[rc + 1] == want == W.session_name_for(seat), f"{seat} plain: --remote-control keeps its explicit label")
        check(argv[argv.index("--name") + 1] == want, f"{seat} plain: --name is {want}")
        check(len(argv) == rc + 3, f"{seat} plain: exactly one positional first prompt after the label ({argv[rc:]})")
        prompt = argv[-1]
        check(prompt.lower().startswith("wake"), f"{seat} plain: the prompt opens with the word wake ({prompt[:40]})")
        check("handoff.py --wake" in prompt and "seat ready" in prompt,
              f"{seat} plain: the prompt runs handoff.py --wake and rimflow seat ready")
        ident = "CONDUCTOR" if seat == "BENCH" else seat      # v3: the BENCH tile wakes as the Conductor
        check(f"infrastructure/agents/{ident}.md" in prompt, f"{seat} plain: the prompt points at its Start of turn")
        check(SAFE.fullmatch(prompt) is not None, f"{seat} plain: the prompt is shell/JSON-safe ({prompt!r})")
        check(argv[:-1] == shlex.split(W.LAUNCH.format(script=W.BOUNDED.format(home=W.SEAT_CLONES[seat][0]),
                                                        label=want, model=W.SEATS[seat][1])),
              f"{seat} plain: the argv is LAUNCH unchanged + the prompt")
    check("rimflow/cli.py next --seat FOUNDRY" in launch_argv(inner_of(build_with((), "FOUNDRY")), False)[-1],
          "FOUNDRY plain: the prompt pulls the queue (rimflow next --seat FOUNDRY)")
    b = launch_argv(inner_of(build_with((), "BENCH")), False)[-1]
    check("next --seat" not in b and "report" in b.lower(), "BENCH plain: wakes and reports, does not pull the queue")


def test_wrapped_path_has_first_prompt():
    cl = build_with({"FOUNDRY"}, "FOUNDRY")
    inner = inner_of(cl)
    check(inner is not None and "seat_loop.sh FOUNDRY " in inner, "FOUNDRY wrapped: seat_loop.sh still wraps it")
    argv = launch_argv(inner, wrapped=True)
    rc = argv.index("--remote-control")
    check(argv[rc + 1] == "AGENT FOUNDRY" and len(argv) == rc + 3,
          f"FOUNDRY wrapped: label then exactly one first prompt ({argv[rc:]})")
    prompt = argv[-1]
    check(prompt.lower().startswith("wake") and "seat_restart.py wake --seat FOUNDRY" in prompt,
          f"FOUNDRY wrapped: the first launch runs seat_restart.py wake ({prompt[:80]})")
    check("seat ready" in prompt, "FOUNDRY wrapped: the first launch also marks the seat ready")
    check(SAFE.fullmatch(prompt) is not None, f"FOUNDRY wrapped: the prompt is shell/JSON-safe ({prompt!r})")


def test_others_untouched():
    for seat in ("HESTIA", "EMERGENCY", "SERVER", "ARTIST"):
        cl = build_with((), seat)
        check("wake" not in cl.lower(), f"{seat}: no first prompt added")
    check(W.LAUNCH.endswith("--remote-control '{label}'"), "LAUNCH itself is unchanged")


def test_only_touches_only_named_tiles():
    import json, subprocess, tempfile
    d = {"profiles": {"list": [{"guid": W.seat_guid("BUILD"), "name": "old"}, {"guid": "{x}", "name": "Artist"}]},
         "schemes": [{"name": "Seat BUILD"}]}
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "settings.json")
        json.dump(d, open(f, "w"))
        r = subprocess.run([sys.executable, os.path.join(HERE, "install_wt_seat_profiles.py"), "--settings", f,
                            "--only", "bench", "--apply"], capture_output=True, text=True)
        out = json.load(open(f))
    check(r.returncode == 0, f"--only bench --apply runs ({r.stderr[-200:]})")
    names = [p["name"] for p in out["profiles"]["list"]]
    check("CONDUCTOR" in names and "AGENT FOUNDRY" not in names, "--only adds just the named tile (BENCH is shown as CONDUCTOR)")
    check("old" in names, "--only leaves retired profiles alone")
    check("defaults" not in out["profiles"], "--only leaves the font defaults alone")


def test_tab_closes_only_when_fleet_stopped():
    """Run the real tile tail under bash with a stub launcher: 143 (fleet SIGTERM) closes the tab, any other status
    leaves a login shell (stubbed to print MARK so we can see it was reached)."""
    import subprocess, tempfile
    d = tempfile.mkdtemp()
    sh = os.path.join(d, "fakeshell"); open(sh, "w").write("#!/bin/sh\necho SHELL-REACHED\nexit 0\n"); os.chmod(sh, 0o755)
    for status, closes in ((143, True), (0, False), (1, False), (137, False), (130, False)):
        r = subprocess.run(["bash", "-c", f"(exit {status}){W.SHELL_TAIL}"], env=dict(os.environ, SHELL=sh),
                           capture_output=True, text=True, timeout=20)
        check(("SHELL-REACHED" not in r.stdout) == closes, f"status {status}: tab {'closes' if closes else 'keeps a shell'}")
        if closes:
            check(r.returncode == 0, "fleet-stop close exits 0 so WT closeOnExit=graceful really closes the tab")


if __name__ == "__main__":
    test_only_touches_only_named_tiles()
    test_plain_path_has_first_prompt()
    test_tab_closes_only_when_fleet_stopped()
    test_wrapped_path_has_first_prompt()
    test_others_untouched()
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    sys.exit(1 if FAILS else 0)
