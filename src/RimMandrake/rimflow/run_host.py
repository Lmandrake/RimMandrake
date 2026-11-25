#!/usr/bin/env python3
"""run_host.py - where a detached list run starts: this machine, or SteveDesktop over ssh.

Boundary page: design/specs/2026-11-24-run-on-steve/boundary.md. Pure: plan() and stop_argv() read only their arguments;
read_facts() is the one function that touches the network.
plan(host, item, brief_path, facts) -> {"verdict": LOCAL|REMOTE|REFUSED|COULD NOT LOOK, "why": str, "argv": [...]}
"""
import json
import re
import subprocess
import sys
from pathlib import Path

LOCAL_NAMES = ("archmagi", "local", "")
HOSTS = {"stevedesktop": "stevedesktop"}          # lower-case name -> ssh alias
LANE_CLONES = ("rm/runner", "rm/runner_b")         # the test lane's own clones: a session writing there pauses the lane
FACTS = ("reachable", "claude", "account", "picked_account", "push", "clone", "free_gb")


def _norm(host):
    return (host or "").strip().lower()


def _lane_clone(path):
    p = str(path).replace("\\", "/").rstrip("/")
    return any(p.endswith("/" + c) or p.endswith(c) and p.startswith("~") for c in LANE_CLONES)


def plan(host, item, brief_path, facts):
    h = _norm(host)
    if h in LOCAL_NAMES:
        return {"verdict": "LOCAL", "why": "this machine", "argv": []}
    if h not in HOSTS:
        return {"verdict": "REFUSED", "why": "unknown host %r (known: archmagi, %s)" % (host, ", ".join(HOSTS)), "argv": []}
    facts = facts or {}
    unread = [k for k in FACTS if facts.get(k) is None]
    if unread:
        return {"verdict": "COULD NOT LOOK", "why": "could not read: " + ", ".join(unread), "argv": []}
    if facts["reachable"] is False:
        return {"verdict": "COULD NOT LOOK", "why": "%s is not reachable" % host, "argv": []}
    if facts["account"] != facts["picked_account"]:
        return {"verdict": "REFUSED", "why": "login %s is not the Dispatcher's pick %s" % (facts["account"],
                                                                                          facts["picked_account"]), "argv": []}
    if not facts["push"]:
        return {"verdict": "REFUSED", "why": "no push route (github-rimmandrake-write) on %s" % host, "argv": []}
    if _lane_clone(facts["clone"]):
        return {"verdict": "REFUSED", "why": "clone %s is the test lane's own" % facts["clone"], "argv": []}
    unit = "rm-list-%s" % re.sub(r"[^A-Za-z0-9_-]", "-", item)[:60]
    inner = ("cd %s && claude -p --dangerously-skip-permissions --model sonnet < %s"
             % (facts["clone"], brief_path))
    argv = ["ssh", HOSTS[h], "systemd-run --user --unit=%s --collect bash -lc %s" % (unit, json.dumps(inner))]
    return {"verdict": "REMOTE", "why": "unit %s on %s in %s" % (unit, host, facts["clone"]), "argv": argv, "unit": unit}


def stop_argv(rec):
    h = _norm(rec.get("host"))
    if h not in HOSTS:
        raise ValueError("record names no known host: %r" % rec.get("host"))
    return ["ssh", HOSTS[h], "systemctl --user stop %s" % rec["unit"]]


def read_facts(host, clone, picked_account, runner=subprocess.run):
    """Facts over ssh; a fact that could not be read stays None."""
    h = HOSTS.get(_norm(host))
    f = {k: None for k in FACTS}
    f["picked_account"], f["clone"] = picked_account, clone
    if not h:
        return f
    connect = "ConnectTimeout=10"

    def sh(cmd):
        try:
            r = runner(["ssh", "-o", connect, h, cmd], capture_output=True, text=True, timeout=60)
        except Exception:  # noqa: BLE001
            return None
        return r.stdout.strip() if r.returncode == 0 else None

    up = sh("echo up")
    f["reachable"] = up == "up"
    if up != "up":
        return f
    f["claude"] = sh("claude --version") or None
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Utils"))
    import account_live as AL

    def run_status(argv, timeout):
        argv = [connect if arg.startswith("ConnectTimeout=") else arg for arg in argv]
        r = runner(argv, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout

    f["account"] = AL.name_of(AL.read(target=h, run=run_status))
    f["push"] = (sh("ssh -T -o BatchMode=yes git@github-rimmandrake-write 2>&1; true") or "").lower().count("successfully") > 0 or None
    free = sh("df -BG --output=avail / | tail -1 | tr -dc 0-9")
    f["free_gb"] = int(free) if free else None
    return f
