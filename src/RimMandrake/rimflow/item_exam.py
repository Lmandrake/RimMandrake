"""item_exam.py -- an item's exam as the Setter seam reads and resits it (status, set_status, kick, unit_name) and the Setter's run in a checker box (run_setter, box_runner, apply_patch).

Moved verbatim from rimflow/relentless_exam.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import effort as EF  # the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CONFIG = os.path.join(HERE, "item_exam.json")
EXAM_DIR = ".exam"                  # the Setter's own files, copied into the box tree under this name for each run
# a planted break of equal size inside the same second leaves a .pyc the import trusts: the break would read green
RUN_ENV = {"PYTHONDONTWRITEBYTECODE": "1"}


def config(path=None):
    try:
        with open(path or os.environ.get("RELENTLESS_EXAM_CONFIG") or CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"mode": "off"}


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------------------------------------------------------- store
def exam_root(store):
    return store.p("exams")


def item_dir(store, item):
    return os.path.join(exam_root(store), item)


def _read(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def _append(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def status(store, item):
    return _read(os.path.join(item_dir(store, item), "owed.json"))


def set_status(store, item, **kw):
    p = os.path.join(item_dir(store, item), "owed.json")
    rec = _read(p, {}) or {}
    rec.update(kw)
    _write(p, rec)
    return rec


def unit_name(item):
    return "rm-relentless-exam-" + hashlib.sha1(item.encode("utf-8")).hexdigest()[:10]


def kick(store, item, cfg=None, runner=subprocess.run):
    """Start the item's exam unit, detached (systemd-run --user): the builder's contract call never waits on a Setter.
    The unit runs the supervisor's released code, not the worker's clone (that may be reaped first). -> None or why not."""
    cfg = config() if cfg is None else cfg
    tool = os.path.abspath(__file__)     # this release's own code, as the tick that starts it
    d = item_dir(store, item)
    os.makedirs(d, exist_ok=True)
    max_s = int(cfg.get("unit_max_s", 3600))
    argv = ["--user", "--quiet", "--collect",
            "-p", "StandardOutput=file:" + os.path.join(d, "unit.out"), "-p", "StandardError=file:" + os.path.join(d, "unit.err"),
            "-p", "RuntimeMaxSec=%d" % max_s, "--working-directory", os.path.dirname(tool),
            "--setenv", "RM_RUNS_ROOT=" + store.root, "--setenv", "PATH=" + os.environ.get("PATH", "/usr/bin:/bin"),
            "--", sys.executable, tool, "run", item]
    import control as C     # Relentless is retired: its family is OFF in the control store
    try:
        r = C.launch_unit(argv, {"family": "relentless", "item": item, "unit": unit_name(item)}, runner=runner,
                          capture_output=True, text=True,
                          timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return "%s: %s" % (type(e).__name__, e)
    return ("systemd-run exit %d: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")))) if r.returncode else None


_PATCH_NAME_LINES = re.compile(r"^(?:diff --git (\S+) (\S+)|(?:rename|copy) (?:from|to) (.+)|(?:---|\+\+\+) (\S+))", re.M)


def unsafe_patch_paths(patch):
    """-> the paths of a diff that would land outside the tree: absolute, `..`, `~`, a backslash or a NUL. Every header that
    names a path is read (diff --git, ---/+++, rename/copy from/to), not only the ones _patch_paths uses."""
    bad = []
    for m in _PATCH_NAME_LINES.finditer(patch or ""):
        for p in m.groups():
            if not p or p == "/dev/null":
                continue
            q = p.strip()
            if q.startswith('"') and q.endswith('"') and len(q) > 1:      # git's C-quoted name: \ooo bytes, \t, \", \\
                q = re.sub(r"\\([0-7]{3}|.)", lambda m: chr(int(m.group(1), 8)) if len(m.group(1)) == 3 else
                           {"t": "\t", "n": "\n", '"': '"', "\\": "/\\"}.get(m.group(1), "\\" + m.group(1)), q[1:-1])
            q = q[2:] if re.match(r"^[ab]/", q) else q
            if q.startswith(("/", "~")) or "\\" in q or "\0" in q or ".." in q.split("/") or re.match(r"^[A-Za-z]:", q):
                bad.append(p)
    return list(dict.fromkeys(bad))


# --------------------------------------------------------------------------------------------------------- the box
OUT_CAP = 4 << 20       # a check's whole output reaches red_kind (a signature mid-dump still disqualifies); 4 MiB a side


def _cap(out):
    return out if len(out) <= 2 * OUT_CAP else out[:OUT_CAP] + "\n[... %d chars cut ...]\n" % (len(out) - 2 * OUT_CAP) + out[-OUT_CAP:]


def apply_patch(patch, tree, runner=subprocess.run):
    """Apply a Setter's planted break inside `tree` only. -> None or why not. A path outside the tree is refused before git
    sees it, git runs WITHOUT --unsafe-paths (it then refuses ../ and absolute paths itself, and writes through no
    symlink), and GIT_CEILING_DIRECTORIES stops it adopting a repository above the tree."""
    unsafe = unsafe_patch_paths(patch)
    if unsafe:
        return "unsafe path(s) outside the tree: %s" % ", ".join(unsafe[:5])
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CEILING_DIRECTORIES"] = os.path.dirname(os.path.abspath(tree))
    p = runner(["git", "apply", "-"], cwd=tree, input=patch, capture_output=True, text=True, timeout=60, env=env)
    return (p.stderr or p.stdout or "git apply exit %d" % p.returncode) if p.returncode else None


def box_runner(rules, source, sha, files_dir, item=None, nonce=None, runner=subprocess.run):
    """-> (run, read_file, close): checks run in a Marker box at `sha` (checker_box.make_box with the WP-02
    toolchain: git history, cv2 venv) under the Marker's own systemd properties; the Setter's files at tree/.exam/.
    Every run() gets a FRESH box: a check that leaves state behind (a sentinel, a cache, a half-reverted break) cannot
    colour the next run, and a break is never reverted, only thrown away with its tree. read_file and the Setter's cwd
    (read_file.tree) use the first box."""
    import checker_box
    prof = checker_box.profile(rules, "marker")
    if not prof:
        raise RuntimeError("no marker wall profile in the rules")
    nonce = nonce or "exam-%s" % uuid.uuid4().hex[:12]

    def fresh(n):
        bx = checker_box.make_box(prof, source, sha, n, base=None, item=item)
        tr = os.path.join(bx, "tree")
        try:
            if files_dir and os.path.isdir(files_dir):
                shutil.copytree(files_dir, os.path.join(tr, EXAM_DIR), dirs_exist_ok=True)
        except BaseException:
            checker_box.remove_box(bx)
            raise
        return bx, tr

    box, tree = fresh(nonce)
    runs = [0]

    def run(argv, patch, timeout):
        runs[0] += 1
        rbox = None
        try:
            rbox, rtree = fresh("%s-r%d" % (nonce, runs[0]))
            if patch:
                why = apply_patch(patch, rtree, runner)
                if why:
                    return None, "PATCH_FAILED: " + why, False
            unit = ["--user", "--wait", "--pipe", "--collect", "--quiet", "-p", "WorkingDirectory=" + rtree,
                    "-p", "RuntimeMaxSec=%d" % (timeout + 30)] + checker_box.props(prof, rbox) \
                + sum((["--setenv", "%s=%s" % kv] for kv in dict(checker_box.unit_env(prof, rbox), **RUN_ENV).items()), []) \
                + ["--"] + list(argv)
            try:
                import control as C     # Relentless is retired: its family is OFF in the control store
                q = C.launch_unit(unit, {"family": "relentless", "unit": "rm-relentless-check-%s-r%d" % (nonce, runs[0])}, runner=runner, capture_output=True, text=True,
                                  timeout=timeout + 60, stdin=subprocess.DEVNULL)
                return q.returncode, _cap((q.stdout or "") + (q.stderr or "")), False
            except subprocess.TimeoutExpired as e:
                return None, str(e), True
        finally:
            if rbox:
                checker_box.remove_box(rbox)

    def read_file(path):
        try:
            with open(os.path.join(tree, path), "rb") as f:
                return f.read()
        except OSError:
            return None

    def close():
        checker_box.remove_box(box)

    read_file.tree = tree               # the Setter's cwd when this box is the Setter's

    return run, read_file, close


def run_setter(cwd, prompt, cfg, out, session=None, resume=None, runner=subprocess.run):
    """Run the Setter (claude -p, Judge-mode agent, fresh or resumed) in the foreground of the exam unit. -> session id."""
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    sid = resume or session or str(uuid.uuid4())
    argv = [claude, "-p", prompt, "--agent", cfg.get("setter_agent", "rm-judge"), "--model", cfg.get("setter_model", "opus"),
            "--output-format", "json", "--dangerously-skip-permissions"] + EF.effort_args(cfg.get("setter_model", "opus")) \
        + (["--resume", resume] if resume else ["--session-id", sid])
    with open(out, "a", encoding="utf-8") as f:
        try:
            r = runner(argv, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, timeout=int(cfg.get("setter_max_s", 1200)),
                       stdin=subprocess.DEVNULL)
            f.write("\n[setter exit %s]\n" % getattr(r, "returncode", "?"))
        except (OSError, subprocess.SubprocessError) as e:
            f.write("\n[setter failed %s: %s]\n" % (type(e).__name__, e))
    return sid


def _item_text(item):
    cli = os.path.join(HERE, "cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "show", item], capture_output=True, text=True, timeout=120)
        return r.stdout or ""          # whole: an examiner reads it (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    except (OSError, subprocess.SubprocessError):
        return ""


def _lines(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out
