#!/usr/bin/env python3
"""fake_systemctl.py - a stand-in for `systemctl --user` used ONLY by the arena selftests. It never talks to systemd,
dbus or a cgroup. It reads unit files from a directory and keeps its "active" set in a JSON state file.

    fake_systemctl.py --state S.json --unit-dir D <verb> [args]
verbs: start U...  stop U...  is-active U  list-units PATTERN  daemon-reload  show-conflicts

Semantics emulated (systemd's, for Conflicts=/PartOf=/Wants=):
  - `start A B` is ONE transaction: if any two requested units conflict (either side lists the other) it fails with
    "Transaction contains conflicting jobs" and changes nothing.
  - `start B` alone starts B and STOPS every active unit that B Conflicts= (or that lists B in Conflicts=); stopping a
    target also stops the units that are PartOf= it; starting a target starts its Wants=.
  - `stop T` stops T and its PartOf= members.
"""
import fnmatch
import json
import re
import sys
from pathlib import Path


def parse(text):
    d, sec = {}, None
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or ln[0] in "#;":
            continue
        m = re.match(r"^\[(\w+)\]$", ln)
        if m:
            sec = m.group(1); continue
        if "=" in ln and sec:
            k, v = ln.split("=", 1)
            d.setdefault(k.strip(), []).extend(v.split())
    return d


def load_units(ud):
    out = {}
    for f in Path(ud).glob("*.target"):
        out[f.name] = parse(f.read_text())
    for dd in Path(ud).glob("*.d"):
        unit = dd.name[:-2]
        if unit.startswith("rm-arm-"):
            continue
        merged = {}
        for c in sorted(dd.glob("*.conf")):
            for k, v in parse(c.read_text()).items():
                merged.setdefault(k, []).extend(v)
        out.setdefault(unit, {}).update(merged)
    return out


def conflicts(units, a, b):
    return b in units.get(a, {}).get("Conflicts", []) or a in units.get(b, {}).get("Conflicts", [])


def members(units, t):
    return [u for u, d in units.items() if t in d.get("PartOf", [])]


def stop(units, active, u):
    active.discard(u)
    for m in members(units, u):
        active.discard(m)


def main(argv):
    state = Path(argv[argv.index("--state") + 1]); ud = argv[argv.index("--unit-dir") + 1]
    rest = [a for i, a in enumerate(argv) if i not in (argv.index("--state"), argv.index("--state") + 1,
                                                        argv.index("--unit-dir"), argv.index("--unit-dir") + 1)]
    verb, args = rest[0], rest[1:]
    units = load_units(ud)
    active = set(json.loads(state.read_text())["active"]) if state.exists() else set()

    def save():
        state.write_text(json.dumps({"active": sorted(active)}))
    if verb == "start":
        for i, a in enumerate(args):
            for b in args[i + 1:]:
                if conflicts(units, a, b):
                    print("Failed to start %s: Transaction contains conflicting jobs 'start' and 'stop' for %s. "
                          "Probably contradicting requirement dependencies configured." % (a, b), file=sys.stderr)
                    return 1
        for u in args:
            if u not in units:
                print("Failed to start %s: Unit not found." % u, file=sys.stderr); return 5
        for u in args:
            for other in sorted(active):
                if conflicts(units, u, other):
                    stop(units, active, other)
            active.add(u)
            for w in units[u].get("Wants", []):
                active.add(w)
        save(); return 0
    if verb == "stop":
        for u in args:
            stop(units, active, u)
        save(); return 0
    if verb == "is-active":
        on = args[0] in active
        print("active" if on else "inactive"); return 0 if on else 3
    if verb == "list-units":
        pat = [a for a in args if not a.startswith("-")][0]
        for u in sorted(units):
            if fnmatch.fnmatch(u, pat):
                print("%s loaded %s running %s" % (u, "active" if u in active else "inactive", u))
        return 0
    if verb == "daemon-reload":
        return 0
    print("fake_systemctl: unsupported verb %s" % verb, file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
