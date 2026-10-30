#!/usr/bin/env python3
"""fake_systemctl.py - a stand-in for `systemctl --user` used ONLY by the arena selftests. It never talks to systemd,
dbus or a cgroup. It reads unit files from a directory and keeps its state in a JSON file.

    fake_systemctl.py --state S.json --unit-dir D <verb> [args]
verbs: start U...  stop U...  restart U...  is-active U  is-enabled U  enable U...  disable U...  list-units PATTERN
       reset-failed  daemon-reload  boot (test verb: a fresh boot - everything inactive, then every enabled unit starts)

State {"active": [...], "failed": [...], "enabled": [...], "fail_start": [...], "log": [...]}; a state file holding
only "active" is fine (the rest default to empty).

Semantics emulated (systemd's, after the tester's fsd.py, switch_test/fsd.py):
  - units = every file in D (*.target, *.service, *.timer) plus `<unit>.d/*.conf` drop-ins merged by name (a unit
    known only through a drop-in exists); an empty assignment `Key=` resets that list.
  - `start A B` is ONE transaction: Wants=/Requires= are pulled in recursively; if any two EXPLICIT units conflict
    (either side lists the other: Conflicts= is symmetric) it fails with "Transaction contains conflicting jobs" and
    changes nothing; a pulled-in unit that conflicts with an explicit one is dropped from the transaction.
  - starting a unit STOPS every active unit it conflicts with; stopping a unit stops (recursively) the units PartOf= it.
  - a unit in fail_start fails to start (lands in failed; rc 1 when it was explicit). is-active: active rc0,
    failed rc3, inactive rc3. is-enabled: enabled rc0, disabled rc1.
"""
import fnmatch
import json
import re
import sys
from pathlib import Path


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
                d[sec][k.strip()] = []
            else:
                d[sec].setdefault(k.strip(), []).extend(v.split())
    return d


def load_units(ud):
    u = {}
    for f in Path(ud).glob("*"):
        if f.is_file():
            u[f.name] = parse(f.read_text())
    for dd in Path(ud).glob("*.d"):
        if not dd.is_dir():
            continue
        d = u.setdefault(dd.name[:-2], {})
        for c in sorted(dd.glob("*.conf")):
            parse(c.read_text(), d)
    return u


def g(u, n, k, sec="Unit"):
    return set(((u.get(n) or {}).get(sec) or {}).get(k, []))


def conflicts(u, a):
    return g(u, a, "Conflicts") | {n for n in u if a in g(u, n, "Conflicts")}


def partof_children(u, a):
    return {n for n in u if a in g(u, n, "PartOf")}


def do_stop(u, s, a, seen=None):
    seen = seen if seen is not None else set()
    if a in seen:
        return
    seen.add(a)
    for ch in sorted(partof_children(u, a)):
        do_stop(u, s, ch, seen)
    if a in s["active"]:
        s["active"].remove(a); s["log"].append("stop " + a)


def do_start(u, s, names):
    jobs, order = set(), []

    def pull(n):
        if n in jobs:
            return
        jobs.add(n); order.append(n)
        for w in sorted(g(u, n, "Wants") | g(u, n, "Requires")):
            if w in u:
                pull(w)
    explicit = list(names)
    for n in explicit:
        if n not in u:
            return 5, "Failed to start %s: Unit %s not found." % (n, n)
    for i, a in enumerate(explicit):
        for b in explicit[i + 1:]:
            if b in conflicts(u, a):
                return 1, ("Failed to start %s: Transaction contains conflicting jobs 'start' and 'stop' for %s. "
                           "Probably contradicting requirement dependencies configured." % (a, b))
    for n in explicit:
        pull(n)
    order = [n for n in order if n in explicit or not any(n in conflicts(u, e) for e in explicit)]
    for n in order:
        for c in sorted(conflicts(u, n)):
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
        if n in s["failed"]:
            s["failed"].remove(n)
    return rc, "" if rc == 0 else "Job for unit failed."


def main(argv):
    i_s, i_u = argv.index("--state"), argv.index("--unit-dir")
    state, ud = Path(argv[i_s + 1]), argv[i_u + 1]
    rest = [a for i, a in enumerate(argv) if i not in (i_s, i_s + 1, i_u, i_u + 1)]
    while rest and rest[0].startswith("--user"):
        rest = rest[1:]
    verb, args = rest[0], rest[1:]
    u = load_units(ud)
    s = json.loads(state.read_text()) if state.exists() else {}
    for k in ("active", "failed", "enabled", "fail_start", "log"):
        s.setdefault(k, [])
    s["log"].append("CMD " + " ".join(rest))
    out, err, rc = "", "", 0
    if verb == "start":
        rc, err = do_start(u, s, args)
    elif verb == "stop":
        for a in args:
            do_stop(u, s, a)
    elif verb == "restart":
        for a in args:
            do_stop(u, s, a)
            r, e = do_start(u, s, [a])
            rc, err = rc or r, err or e
    elif verb == "is-active":
        a = args[0]
        if a in s["active"]:
            out = "active"
        elif a in s["failed"]:
            out, rc = "failed", 3
        else:
            out, rc = "inactive", 3
    elif verb == "is-enabled":
        if args[0] in s["enabled"]:
            out = "enabled"
        elif args[0] in u:
            out, rc = "disabled", 1
        else:
            out, rc = "not-found", 1
    elif verb == "enable":
        for a in args:
            if a not in s["enabled"]:
                s["enabled"].append(a)
    elif verb == "disable":
        s["enabled"] = [x for x in s["enabled"] if x not in args]
    elif verb == "list-units":
        pats = [x for x in args if not x.startswith("-")]
        for n in sorted(set(u) | set(s["active"])):
            if pats and not any(fnmatch.fnmatch(n, p) for p in pats):
                continue
            st = "active" if n in s["active"] else ("failed" if n in s["failed"] else "inactive")
            out += "%s loaded %s %s fake\n" % (n, st, {"active": "running", "failed": "failed",
                                                       "inactive": "dead"}[st])
    elif verb == "reset-failed":
        s["failed"] = []
    elif verb == "boot":
        s["active"], s["failed"] = [], []
        for n in list(s["enabled"]):
            if n in u:
                do_start(u, s, [n])
    elif verb == "daemon-reload":
        pass
    else:
        err, rc = "fake_systemctl: unsupported verb %s" % verb, 2
    state.write_text(json.dumps(s, sort_keys=True))
    if out:
        sys.stdout.write(out if out.endswith("\n") else out + "\n")
    if err:
        sys.stderr.write(err + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
