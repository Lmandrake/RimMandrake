#!/usr/bin/env python3
"""ops_clocks.py - every Operations clock runs its code from ONE deploy (OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY).

Strategy §8 step 0 (design/RimMandrake/operations_metronome_strategy_2026-11-02.md): the Operations timers ran code from
six clones, so two clocks could read the same file with different code. The list of clocks and the deploy is data,
src/RimMandrake/Utils/systemd/ops_clocks.json; `RM_OPS_DEPLOY` overrides the deploy (tests only).

    ops_clocks.py check      exit 0 when every clock, as systemd has it loaded, runs only from the deploy, its trigger
                             exists, the deploy holds no local edits under src/, and every loaded rm-*/testq-*/
                             timer-guard/account-plan unit is a clock or named in "outside", and every old timer the
                             metronome's phase table says a phase `owns` (cut over, OPS_METRONOME_MIGRATE_CLOCKS_FENCED)
                             is neither enabled nor active (two owners); else exit 1, one line each
    ops_clocks.py deploy     print the deploy path (installers default their --deploy to it)
    ops_clocks.py snapshot   record the deploy's HEAD and `git status --porcelain -- src` in SNAPSHOT (commit it), for
                             a checker that cannot read the deploy: there `check` judges the pinned clause from that
                             reading (younger than SNAPSHOT_MAX_H hours, HEAD on the deploy's origin/main as measured
                             when it was taken, no local edit) and says so on a NOTE line; everything systemd shows is
                             still read live. The checker's own git is a second witness only where it holds the
                             commit: a checkout without that history (a blind export) cannot disprove it, and says so.
"""
import ast
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONF = HERE / "systemd" / "ops_clocks.json"
UNIT_GLOBS = ("rm-*", "testq-*", "timer-guard*", "account-plan*")
EXEC_KEYS = ("ExecStart", "ExecStartPre", "ExecStartPost", "ExecStop", "ExecStopPost", "ExecReload")
REPO = HERE.parents[2]
SNAPSHOT = REPO / "infrastructure/state/live_proofs/OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY.deploy.json"
SNAPSHOT_MAX_H = 48
CODE_PATH = re.compile(r"(/[^\s'\";]*?)/src/RimMandrake/")   # the checkout a script path lives in


def load_conf(path=CONF):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def deploy(conf=None):
    return os.environ.get("RM_OPS_DEPLOY") or (conf or load_conf())["deploy"]


def _is_deploy_call(node):
    """`__import__("ops_clocks").deploy()` or `ops_clocks.deploy()`, called with no arguments."""
    if not (isinstance(node, ast.Call) and not node.args and not node.keywords and isinstance(node.func, ast.Attribute)
            and node.func.attr == "deploy"):
        return False
    owner = node.func.value
    if isinstance(owner, ast.Name):
        return owner.id == "ops_clocks"
    return (isinstance(owner, ast.Call) and isinstance(owner.func, ast.Name) and owner.func.id == "__import__"
            and len(owner.args) == 1 and isinstance(owner.args[0], ast.Constant) and owner.args[0].value == "ops_clocks")


def deploy_default_ok(src):
    """installer source -> True when it has an add_argument(..., "--deploy", ...) call, every one defaults to this
    module's deploy(), and no set_defaults(deploy=...) overrides it. Judged on the call, never the text: a file may READ
    RM_PULSE_DEPLOY elsewhere (ops_watch's DEPLOY_STALE), and wrapping the call over lines changes nothing
    (NIGHTLY_COP_FIX_RED_YZWCJJ_JDSB). Unparseable source is False."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    found = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        if n.func.attr == "add_argument" and any(isinstance(a, ast.Constant) and a.value == "--deploy" for a in n.args):
            dflt = [k.value for k in n.keywords if k.arg == "default"]
            found.append(len(dflt) == 1 and _is_deploy_call(dflt[0]))
        elif n.func.attr == "set_defaults" and any(k.arg in ("deploy", None) for k in n.keywords):
            found.append(False)   # overrides the add_argument default (or might, through **kwargs)
    return bool(found) and all(found)


def effective(unit_text):
    """systemctl cat text (unit + drop-ins, in order) -> {key: [values]} as systemd applies them: a later list entry
    appends, an empty assignment (`ExecStart=`) clears what came before. Comments and section headers are dropped."""
    out = {}
    for raw in re.sub(r"\\\n", " ", unit_text).splitlines():   # a trailing backslash continues the line
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


def snapshot_path():
    return Path(os.environ.get("RM_OPS_SNAPSHOT") or SNAPSHOT)


def _git(dep, *a):
    return subprocess.run(["git", "-C", str(dep), *a], capture_output=True, text=True, timeout=60)


def take_snapshot(dep, out=None):
    """Read the deploy (which must be readable here) and write the reading; returns it."""
    if not (Path(dep) / "src/RimMandrake").is_dir():
        raise SystemExit("deploy %s holds no src/RimMandrake" % dep)
    st = _git(dep, "status", "--porcelain", "--", "src")
    if st.returncode:
        raise SystemExit("git status in the deploy failed: %s" % st.stderr.strip()[:200])
    snap = {"deploy": str(dep).rstrip("/"), "head": _git(dep, "rev-parse", "HEAD").stdout.strip(),
            "src_tree": _git(dep, "rev-parse", "HEAD:src").stdout.strip(),
            # provenance measured HERE, where the history is: no commit of the deploy's own that origin/main lacks
            "head_on_origin": _git(dep, "merge-base", "--is-ancestor", "HEAD", "origin/main").returncode == 0,
            "porcelain_src": st.stdout.splitlines(), "uid": os.getuid(), "taken": int(time.time()),
            "taken_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    p = Path(out) if out else snapshot_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snap, indent=1) + "\n", encoding="utf-8")
    return snap


def has_commit(repo, sha):
    """True only when `repo` is a git checkout holding commit `sha`; a history-less export answers False."""
    return _git(repo, "cat-file", "-e", sha + "^{commit}").returncode == 0


def judge_snapshot(snap, dep, now=None, repo=REPO, notes=None):
    """Problems with a recorded reading of an unreadable deploy. Provenance is the recorded `head_on_origin`; the
    checker's git confirms it only where it holds the commit (held but not an ancestor = a problem), else a note."""
    now = time.time() if now is None else now
    probs = []
    if snap.get("deploy", "").rstrip("/") != str(dep).rstrip("/"):
        probs.append("snapshot is of %s, not the deploy %s" % (snap.get("deploy"), dep))
    taken = snap.get("taken", 0)
    age_h = (now - taken) / 3600.0 if isinstance(taken, (int, float)) else float("inf")
    if not 0 <= age_h <= SNAPSHOT_MAX_H:
        probs.append("snapshot is %.1f h old (limit %d h): rerun `ops_clocks.py snapshot` where the deploy is readable"
                     % (age_h, SNAPSHOT_MAX_H))
    head = snap.get("head", "")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        probs.append("snapshot HEAD %r is not a commit id" % head)
    else:
        if snap.get("head_on_origin") is not True:
            probs.append("snapshot HEAD %s was not on the deploy's origin/main when taken (local commits in the deploy)"
                         % head[:10])
        if has_commit(repo, head):
            if _git(repo, "merge-base", "--is-ancestor", head, "HEAD").returncode:
                probs.append("snapshot HEAD %s is not an ancestor of this checkout's HEAD" % head[:10])
        elif notes is not None:
            notes.append("this checkout holds no commit %s (no git history here): ancestry not re-measured, relying on"
                         " the snapshot's recorded head_on_origin" % head[:10])
    porc = snap.get("porcelain_src", ["?"])
    if not isinstance(porc, list):
        porc = ["porcelain_src unreadable: %r" % (porc,)]
    probs += ["local edit in the deploy (snapshot): %s" % ln for ln in porc]
    return probs


def readable(dep):
    return os.access(dep, os.R_OK | os.X_OK)


def owned_timers(table_path=None):
    """{old timer: metronome phase} from the phase table's `owns`."""
    t = json.loads(Path(table_path or HERE / "systemd" / "metronome_phases.json").read_text(encoding="utf-8"))
    return {tm: name for name, p in t["phases"].items() for tm in (p.get("owns") or [])}


def judge_owned(owned, state):
    """Pure. owned {timer: phase}, state(timer) -> (is-enabled, is-active) text. A cut-over timer still enabled or
    active is a second owner of its clock."""
    probs = []
    for tm, phase in sorted(owned.items()):
        en, act = state(tm)
        if en in ("enabled", "enabled-runtime") or act in ("active", "activating", "reloading"):
            probs.append("%s: the metronome's %s phase owns it, but it is %s and %s (two owners): "
                         "systemctl --user disable --now %s" % (tm, phase, en or "?", act or "?", tm))
    return probs


def check(conf, notes=None):
    dep = deploy(conf)
    probs = []
    if Path(dep).exists() and not readable(dep):
        sp = snapshot_path()
        try:
            snap = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            return ["deploy %s is unreadable here and its snapshot %s cannot be read (%s)" % (dep, sp, e)]
        probs += judge_snapshot(snap, dep, notes=notes)
        if notes is not None:
            notes.append("deploy unreadable here: pinned clause judged from snapshot %s taken %s by uid %s at %s"
                         % (sp.name, snap.get("taken_utc"), snap.get("uid"), str(snap.get("head", ""))[:10]))
    elif not (Path(dep) / "src/RimMandrake").is_dir():
        return ["deploy %s holds no src/RimMandrake" % dep]
    else:
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
    probs += judge_owned(owned_timers(), lambda tm: (_sc("is-enabled", tm).stdout.strip(),
                                                     _sc("is-active", tm).stdout.strip()))
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
    if cmd == "snapshot":
        snap = take_snapshot(deploy(conf))
        print("snapshot %s: deploy %s at %s, %d local edit(s) under src/"
              % (snapshot_path(), snap["deploy"], snap["head"][:10], len(snap["porcelain_src"])))
        return 0
    if cmd != "check":
        print(__doc__)
        return 2
    notes = []
    probs = check(conf, notes)
    head = _git(deploy(conf), "log", "-1", "--format=%h").stdout.strip() if readable(deploy(conf)) else ""
    for p in probs:
        print("FAIL " + p)
    for n in notes:
        print("NOTE " + n)
    print("%s: %d Operations clocks, deploy %s at %s, %d problem(s)"
          % ("OK" if not probs else "FAIL", len(conf["clocks"]), deploy(conf), head or "?", len(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
