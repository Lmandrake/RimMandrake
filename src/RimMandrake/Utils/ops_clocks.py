#!/usr/bin/env python3
"""ops_clocks.py - every Operations clock runs its code from ONE deploy (OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY).

Strategy §8 step 0 (design/RimMandrake/operations_metronome_strategy_2026-11-02.md): the Operations timers ran code from
six clones, so two clocks could read the same file with different code. The list of clocks and the deploy is data,
src/RimMandrake/Utils/systemd/ops_clocks.json; `RM_OPS_DEPLOY` overrides the deploy (tests only).

    ops_clocks.py check      exit 0 when every clock, as systemd has it loaded, runs only from the deploy, its trigger
                             exists, the deploy holds no local edits under src/, and every loaded rm-*/testq-*/
                             timer-guard/account-plan unit is a clock or named in "outside"; else exit 1, one line each
    ops_clocks.py deploy     print the deploy path (installers default their --deploy to it)
"""
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONF = HERE / "systemd" / "ops_clocks.json"
UNIT_GLOBS = ("rm-*", "testq-*", "timer-guard*", "account-plan*")
EXEC_KEYS = ("ExecStart", "ExecStartPre", "ExecStartPost", "ExecStop", "ExecStopPost", "ExecReload")
CODE_PATH = re.compile(r"(/[^\s'\";]*?)/src/RimMandrake/")   # the checkout a script path lives in


def load_conf(path=CONF):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def deploy(conf=None):
    return os.environ.get("RM_OPS_DEPLOY") or (conf or load_conf())["deploy"]


def effective(unit_text):
    """systemctl cat text (unit + drop-ins, in order) -> {key: [values]} as systemd applies them: a later list entry
    appends, an empty assignment (`ExecStart=`) clears what came before. Comments and section headers are dropped."""
    out = {}
    for raw in unit_text.splitlines():
        line = raw.strip()
        if not line or line[0] in "#;[" or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if v == "":
            out[k] = []
        else:
            out.setdefault(k, []).append(v)
    return out


def judge(unit_text, dep):
    """Pure: problems with one loaded service's text against deploy `dep`; [] = it runs only from the deploy."""
    dep = dep.rstrip("/")
    eff = effective(unit_text)
    probs = []
    execs = [v for k in EXEC_KEYS for v in eff.get(k, [])]
    if not execs:
        return ["no ExecStart"]
    for wd in eff.get("WorkingDirectory", [])[-1:]:
        if wd.lstrip("-").rstrip("/") != dep:
            probs.append("WorkingDirectory %s is not the deploy" % wd)
    for v in execs:
        roots = {m.group(1) for m in CODE_PATH.finditer(v)}
        for r in sorted(roots - {dep}):
            probs.append("runs code from %s" % r)
        if re.search(r"(^|[\s'\"])src/RimMandrake/", v) and not eff.get("WorkingDirectory"):
            probs.append("relative script path with no WorkingDirectory")
    return probs


def classify(units, conf):
    """Loaded unit names (no suffix) that are neither a clock nor matched by an "outside" pattern."""
    return sorted(u for u in units if u not in conf["clocks"]
                  and not any(fnmatch.fnmatchcase(u, pat) for pat in conf["outside"]))


def _sc(*a):
    return subprocess.run(["systemctl", "--user", *a], capture_output=True, text=True, timeout=30)


def loaded_units():
    r = _sc("list-units", "--all", "--plain", "--no-legend", *UNIT_GLOBS)
    names = set()
    for line in r.stdout.splitlines():
        name = line.split()[0] if line.split() else ""
        base, dot, kind = name.rpartition(".")
        if dot and kind in ("service", "timer", "path"):
            names.add(base)
    return names


def deploy_dirty(dep):
    r = subprocess.run(["git", "-C", dep, "status", "--porcelain", "--", "src"], capture_output=True, text=True,
                       timeout=60)
    if r.returncode:
        return ["git status in the deploy failed: %s" % (r.stderr.strip()[:200])]
    return ["local edit in the deploy: %s" % ln for ln in r.stdout.splitlines()]


def check(conf):
    dep = deploy(conf)
    probs = []
    if not (Path(dep) / "src/RimMandrake").is_dir():
        return ["deploy %s holds no src/RimMandrake" % dep]
    probs += deploy_dirty(dep)
    for name, trigger in sorted(conf["clocks"].items()):
        r = _sc("cat", name + ".service")
        if r.returncode:
            probs.append("%s: not installed (%s)" % (name, r.stderr.strip()[:120]))
            continue
        probs += ["%s: %s" % (name, p) for p in judge(r.stdout, dep)]
        en = _sc("is-enabled", trigger).stdout.strip()   # enabled or not is timers_guard's business, not ours
        if en in ("", "not-found"):
            probs.append("%s: trigger %s is not installed" % (name, trigger))
    probs += ["%s: loaded but not classified in %s (a clock, or outside with a reason)" % (u, CONF.name)
              for u in classify(loaded_units(), conf)]
    return probs


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "check"
    conf = load_conf()
    if cmd == "deploy":
        print(deploy(conf))
        return 0
    if cmd != "check":
        print(__doc__)
        return 2
    probs = check(conf)
    head = subprocess.run(["git", "-C", deploy(conf), "log", "-1", "--format=%h"], capture_output=True, text=True,
                          timeout=30).stdout.strip()
    for p in probs:
        print("FAIL " + p)
    print("%s: %d Operations clocks, deploy %s at %s, %d problem(s)"
          % ("OK" if not probs else "FAIL", len(conf["clocks"]), deploy(conf), head or "?", len(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
