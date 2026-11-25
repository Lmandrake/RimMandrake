#!/usr/bin/env python3
"""ops_clocks.py - every Operations clock runs its code from ONE deploy (OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY).

Strategy §8 step 0 (design/RimMandrake/operations_metronome_strategy_2026-11-02.md): the Operations timers ran code from
six clones, so two clocks could read the same file with different code. The list of clocks and the deploy is data,
src/RimMandrake/Utils/systemd/ops_clocks.json; `RM_OPS_DEPLOY` overrides the deploy (tests only).

    ops_clocks.py check      exit 0 when every clock, as systemd has it loaded, runs only from the deploy, its trigger
                             exists, the deploy holds no local edits under src/, and every loaded rm-*/testq-*/
                             timer-guard/account-plan unit is a clock, an old timer a metronome phase `owns`, or named
                             in "outside", every such owned timer (cut over, OPS_METRONOME_MIGRATE_CLOCKS_FENCED) is
                             neither enabled nor active (two owners), and `units` below holds; else exit 1, one line each
    ops_clocks.py units      exit 0 when every unit text of ours has its one home, src/RimMandrake/Utils/systemd/: each
                             installed rm-*/testq-*/timer-guard/account-plan/claude-seats unit and
                             drop-in equals the folder file of its name, every folder file is installed, and no non-test
                             Python source holds unit text (design/specs/2026-11-22-units-one-folder/boundary.md)
    ops_clocks.py install [UNIT ...] [--apply] [--enable]
                             the only unit installer: write the named units (a bare name takes its service, timer and
                             drop-ins; none = every folder file that differs) into ~/.config/systemd/user, then one
                             daemon-reload; --enable also enables and starts the named timers and paths. Plan unless
                             --apply. Refuses a masked (retired) name.
    ops_clocks.py deploy     print the deploy path
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


# ------------------------------------------------------------------ unit texts: one home
# Every unit text of ours is one file in UNIT_DIR with its installed name; `install` is the only installer
# (design/specs/2026-11-22-units-one-folder/boundary.md).
UNIT_DIR = HERE / "systemd"
UNIT_SUFFIXES = (".service", ".timer", ".path", ".slice", ".socket", ".target")
INSTALL_GLOBS = UNIT_GLOBS + ("claude-seats*",)
THROWAWAY = ("testq-selftestthrow-*", "rm-probe-*")   # selftests make and remove these in the real install dir
MASK = object()                                       # an installed name that is a symlink to /dev/null
SECTION = re.compile(r"^\[(Service|Timer|Path|Slice|Socket)\]\s*$", re.M)


def install_dir():
    return Path(os.environ.get("RM_UNIT_INSTALL_DIR") or Path.home() / ".config/systemd/user")


def _is_unit(name):
    return name.endswith(UNIT_SUFFIXES)


def _scoped(name, globs):
    base = name.split("/")[0]
    return (any(fnmatch.fnmatchcase(base, g) for g in globs)
            and not any(fnmatch.fnmatchcase(base, g) for g in THROWAWAY))


def _units_in(d, globs=None):
    """-> {name: Path} for unit files and `<unit>.d/*.conf` drop-ins directly under d (globs: names in scope only)."""
    out = {}
    for p in sorted(Path(d).iterdir()):
        if p.is_dir() and _is_unit(p.name[:-2]) and p.name.endswith(".d"):
            out.update(("%s/%s" % (p.name, c.name), c) for c in sorted(p.iterdir()) if c.name.endswith(".conf"))
        elif _is_unit(p.name):
            out[p.name] = p
    return {n: p for n, p in out.items() if globs is None or _scoped(n, globs)}


def folder_units(d=None):
    """-> {installed name: text} of the one home."""
    return {n: p.read_text(encoding="utf-8") for n, p in _units_in(d or UNIT_DIR).items()}


def installed_units(d=None, globs=INSTALL_GLOBS):
    """-> {name: text | MASK} of what is installed, in scope; None when the install dir cannot be read."""
    d = Path(d or install_dir())
    try:
        found = _units_in(d, globs)
    except OSError:
        return None
    out = {}
    for n, p in found.items():
        if p.is_symlink() and os.path.realpath(p) == "/dev/null":
            out[n] = MASK
            continue
        try:
            out[n] = p.read_text(encoding="utf-8")
        except OSError as e:
            out[n] = e
    return out


def judge_units(folder, installed, where="the install dir"):
    """Pure: folder {name: text}, installed {name: text | MASK | OSError} or None -> problems ([] = one home holds all)."""
    if installed is None:
        return ["units: could not read %s, so no installed unit was compared with the folder" % where]
    probs = []
    for n in sorted(set(folder) | set(installed)):
        f, i = folder.get(n), installed.get(n, None)
        if n not in installed:
            probs.append("%s: in the folder, not installed: ops_clocks.py install %s --apply" % (n, n))
        elif i is MASK:
            if f is not None:
                probs.append("%s: masked here (retired), but the folder still holds its text: delete the folder file" % n)
        elif isinstance(i, OSError):
            probs.append("%s: installed copy could not be read (%s)" % (n, i))
        elif f is None:
            probs.append("%s: installed only on this machine: its text belongs in %s" % (n, UNIT_DIR.relative_to(REPO)))
        elif f != i:
            probs.append("%s: installed text differs from the folder: ops_clocks.py install %s --apply" % (n, n))
    return probs


def embedded_units(src):
    """Python source -> line numbers of string constants that hold a unit section line ([] = none)."""
    if not any("[%s]" % k in src for k in ("Service", "Timer", "Path", "Slice", "Socket")):
        return []                                         # cheap: most sources name no section at all
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    return sorted({n.lineno for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, str) and SECTION.search(n.value)})


def _is_test(path):
    return path.name.startswith(("selftest_", "test_")) or "tests" in path.parts


def embedded_in_tree(root=None):
    """-> problems: every non-test .py under src/RimMandrake that holds unit text."""
    root = Path(root or HERE.parent)
    probs = []
    for p in sorted(root.rglob("*.py")):
        if _is_test(p.relative_to(root)):
            continue
        try:
            lines = embedded_units(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        probs += ["%s:%d: unit text in code: move it to %s and install with ops_clocks.py install"
                  % (p.relative_to(root.parent.parent), ln, UNIT_DIR.relative_to(REPO)) for ln in lines]
    return probs


def units_problems(folder_dir=None, inst_dir=None, src_root=None):
    d = Path(inst_dir or install_dir())
    return (judge_units(folder_units(folder_dir), installed_units(d), str(d)) + embedded_in_tree(src_root))


def _unit_of(name):
    """"rm-x.service.d/a.conf" -> "rm-x.service"; a unit file name is itself."""
    u = name.split("/")[0]
    return u[:-2] if u.endswith(".d") else u


def _expand(names, folder):
    """`rm-deadman` -> every folder file of that unit (service, timer, drop-ins); a full name stays itself."""
    out = []
    for n in names:
        hits = sorted(k for k in folder if n in (k, _unit_of(k), _unit_of(k).rsplit(".", 1)[0]))
        if not hits:
            raise SystemExit("install: %s is not in %s" % (n, UNIT_DIR))
        out += [h for h in hits if h not in out]
    return out


def install(names=(), apply=False, enable=False, folder_dir=None, dest=None, sc=None, out=print):
    """Write folder files into the install dir. names: units or files (none = every file that differs). -> exit code."""
    sc = sc or (lambda *a: _sc(*a))
    folder = folder_units(folder_dir)
    dest = Path(dest or install_dir())
    inst = installed_units(dest, globs=("*",)) or {}
    todo = _expand(names, folder) if names else sorted(n for n in folder if inst.get(n) != folder[n])
    wrote = []
    for n in todo:
        if inst.get(n) is MASK:
            out("refused %s: masked here (a retired unit); unmask by hand only on a ruling" % n)
            return 2
        same = inst.get(n) == folder[n]
        out("%s %s" % ("unchanged" if same else ("write" if apply else "would write"), dest / n))
        if apply and not same:
            (dest / n).parent.mkdir(parents=True, exist_ok=True)
            tmp = dest / (n + ".tmp")
            tmp.write_text(folder[n], encoding="utf-8")
            os.replace(tmp, dest / n)
            wrote.append(n)
    if not apply:
        out("plan only: pass --apply to write")
        return 0
    steps = ([["daemon-reload"]] if wrote else []) + [["enable", "--now", n] for n in todo
                                                      if enable and n.endswith((".timer", ".path"))]
    for argv in steps:
        r = sc(*argv)
        out("systemctl --user %s: exit %d %s" % (" ".join(argv), r.returncode, (r.stderr or "").strip()))
        if r.returncode:
            return 1
    return 0


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
    for env in eff.get("Environment", []):
        # The plan is one file, written by ./acct. A unit that names another plan folder, or another rule file for the
        # old engine's fallback, decides from a copy that goes stale (2026-11-20: a 2026-11-05 week file still routed
        # the switch to steven and lacked the drain floors). An empty Environment= clears it above.
        for m in re.finditer(r"(?:^|[\s\"'])(RM_SWITCH_PLAN|RM_ACCOUNT_PLAN_DIR)=([^\s\"']+)", env):
            probs.append("Environment %s=%s: the timed pass must read the one account plan file (./acct plan), and "
                         "its fallback the standard switching_plan.json" % (m.group(1), m.group(2)))
    return probs


def classify(units, conf, owned=()):
    """Loaded unit names (no suffix) that are neither a clock, nor an old timer a metronome phase owns, nor matched by
    an "outside" pattern."""
    owned = {t.rsplit(".", 1)[0] for t in owned}
    return sorted(u for u in units if u not in conf["clocks"] and u not in owned
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
        return ["git status in the deploy failed: %s" % (r.stderr.strip())]
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
        raise SystemExit("git status in the deploy failed: %s" % st.stderr.strip())
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
            probs.append("%s: not installed (%s)" % (name, r.stderr.strip()))
            continue
        probs += ["%s: %s" % (name, p) for p in judge(r.stdout, dep)]
        en = _sc("is-enabled", trigger).stdout.strip()   # enabled or not is timers_guard's business, not ours
        if en in ("", "not-found"):
            probs.append("%s: trigger %s is not installed" % (name, trigger))
    probs += judge_owned(owned_timers(), lambda tm: (_sc("is-enabled", tm).stdout.strip(),
                                                     _sc("is-active", tm).stdout.strip()))
    probs += ["%s: loaded but not classified in %s (a clock, or outside with a reason)" % (u, CONF.name)
              for u in classify(loaded_units(), conf, set(owned_timers()))]
    probs += units_problems()
    return probs


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "check"
    conf = load_conf()
    if cmd == "deploy":
        print(deploy(conf))
        return 0
    if cmd == "units":
        probs = units_problems()
        for p in probs:
            print("FAIL " + p)
        print("%s: %d unit files in %s, %d problem(s)" % ("OK" if not probs else "FAIL", len(folder_units()),
                                                         UNIT_DIR.relative_to(REPO), len(probs)))
        return 1 if probs else 0
    if cmd == "install":
        rest = argv[1:]
        flags = {"--apply", "--enable"}
        return install([a for a in rest if a not in flags], apply="--apply" in rest, enable="--enable" in rest)
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
