#!/usr/bin/env python3
# VENDORED VERBATIM (below this header) from the blind tester's model, D:\ClaudeWork\rimmandrake\foundry_arena\
# switch_test\fsd.py (2026-10-29), so selftest_arena_switch.py t_fsd_parity can check fake_systemctl.py against it.
# Do not edit: if the tester's model changes, re-copy it and re-run the parity test.
"""Tester's own fake systemd user manager (state in $FSD_STATE json). NEVER calls real systemctl.
Models: start of several units in ONE transaction (conflicting start jobs -> fail), Conflicts= symmetric per
systemd.unit(5) ("vice versa"), sequential start stops conflicting active units, PartOf= stop/restart propagation,
Wants= pull-in, enabled WantedBy=default.target/timers.target at boot, reset-failed, failing units, already-active.
Units: dir $FSD_UNITS (*.target, *.service, *.timer files, <unit>.d/*.conf drop-ins)."""
import json, os, re, sys, fnmatch
from pathlib import Path

ST = Path(os.environ["FSD_STATE"])
UD = Path(os.environ["FSD_UNITS"])


def parse(text, d=None):
    d = d if d is not None else {}
    sec = None
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or ln[0] in "#;":
            continue
        m = re.match(r"^\[(\w+)\]$", ln)
        if m:
            sec = m.group(1); d.setdefault(sec, {}); continue
        if "=" in ln and sec:
            k, v = ln.split("=", 1)
            if not v.strip():
                d[sec][k.strip()] = []          # empty assignment resets
            else:
                d[sec].setdefault(k.strip(), []).extend(v.split())
    return d


def load_units():
    u = {}
    for f in UD.glob("*"):
        if f.is_file():
            u[f.name] = parse(f.read_text())
    for dd in UD.glob("*.d"):
        name = dd.name[:-2]
        d = u.setdefault(name, {})
        for c in sorted(dd.glob("*.conf")):
            parse(c.read_text(), d)
    return u


def g(u, n, k, sec="Unit"):
    return set(((u.get(n) or {}).get(sec) or {}).get(k, []))


def st():
    return json.loads(ST.read_text()) if ST.exists() else {"active": [], "failed": [], "enabled": [], "log": [],
                                                              "fail_start": []}


def save(s):
    ST.write_text(json.dumps(s, sort_keys=True))


def conflicts(u, a):
    c = g(u, a, "Conflicts")
    c |= {n for n in u if a in g(u, n, "Conflicts")}       # symmetric (systemd adds ConflictedBy=)
    return c


def partof_children(u, a):
    return {n for n in u if a in g(u, n, "PartOf")}


def do_stop(u, s, a, seen=None):
    seen = seen or set()
    if a in seen:
        return
    seen.add(a)
    for ch in partof_children(u, a):
        do_stop(u, s, ch, seen)
    if a in s["active"]:
        s["active"].remove(a); s["log"].append("stop " + a)


def do_start(u, s, names):
    jobs, order = set(), []

    def pull(n):
        if n in jobs:
            return
        jobs.add(n); order.append(n)
        for w in g(u, n, "Wants") | g(u, n, "Requires"):
            pull(w)
    explicit = set(names)
    for n in names:
        if n not in u:
            return 5, "Failed to start %s: Unit %s not found." % (n, n)
        pull(n)
    for a in explicit:
        for b in explicit:
            if a != b and b in conflicts(u, a):
                return 1, ("Failed to start %s: Transaction for %s/start is destructive (%s has 'stop' job queued, "
                           "but 'start' is included in transaction)." % (" ".join(names), a, b))
    # pulled-in (Wants) units conflicting with explicit ones are dropped, like systemd drops non-required jobs
    for n in list(order):
        if n not in explicit and any(n in conflicts(u, e) for e in explicit):
            order.remove(n)
    for n in order:
        for c in conflicts(u, n):
            if c in s["active"]:
                do_stop(u, s, c)
    rc = 0
    for n in order:
        if n in s["fail_start"]:
            if n not in s["failed"]:
                s["failed"].append(n)
            if n in explicit:
                rc = 1
            continue
        if n not in s["active"]:
            s["active"].append(n); s["log"].append("start " + n)
    return rc, "" if rc == 0 else "Job for unit failed."


def main(argv):
    while argv and argv[0].startswith("--user"):
        argv = argv[1:]
    cmd, args = argv[0], argv[1:]
    u, s = load_units(), st()
    s["log"].append("CMD " + " ".join(argv))
    out, rc = "", 0
    if cmd == "start":
        rc, out = do_start(u, s, args)
    elif cmd == "stop":
        for a in args:
            do_stop(u, s, a)
    elif cmd == "restart":
        for a in args:
            ch = partof_children(u, a)
            do_stop(u, s, a); do_start(u, s, [a] + sorted(c for c in ch if c in u))
    elif cmd == "is-active":
        a = args[0]
        if a in s["active"]:
            out = "active"
        elif a in s["failed"]:
            out, rc = "failed", 3
        else:
            out, rc = "inactive", 3
    elif cmd == "list-units":
        pats = [x for x in args if not x.startswith("--")]
        names = set(u) | set(s["active"])
        for n in sorted(names):
            if pats and not any(fnmatch.fnmatch(n, p) for p in pats):
                continue
            state = "active" if n in s["active"] else ("failed" if n in s["failed"] else "inactive")
            sub = {"active": "active", "failed": "failed", "inactive": "dead"}[state]
            bullet = "● " if state == "failed" else ""
            out += "%s%s loaded %s %s fake\n" % (bullet, n, state, sub)
    elif cmd == "reset-failed":
        s["failed"] = []
    elif cmd == "enable":
        s["enabled"] += args
    elif cmd == "boot":                           # tester verb: fresh boot, start default.target + timers.target wants
        s["active"], s["failed"] = [], []
        want = [n for n in u if g(u, n, "WantedBy", "Install") & {"default.target", "timers.target"}
                and n in s["enabled"]]
        for n in want:
            do_start(u, s, [n])
    elif cmd == "daemon-reload":
        pass
    else:
        out, rc = "fsd: unknown verb %s" % cmd, 2
    save(s)
    sys.stdout.write(out + ("\n" if out and not out.endswith("\n") else ""))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
