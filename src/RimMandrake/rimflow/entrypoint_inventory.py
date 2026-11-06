#!/usr/bin/env python3
"""entrypoint_inventory.py - every way a module of ours can be started, read from what starts things (RIMFLOW_RETIRE_DEAD_MODULES).

A grep for importers misses a CLI, a timer, a hook and a dynamic import (redesign_final.md G20), so a module is dead only
when this reads no entry point for it across the tracked tree, the installed units and the hook settings:

  import   a Python import, importlib.import_module("x"), __import__("x"), spec_from_file_location(.., ".../x.py")
  string   a Python string constant holding x.py or `-m x`; a docstring or a comment starts nothing
  bare     a Python string constant equal to x or rimflow.x: what a computed import (relentless._mod(name)) is handed
  run      x.py or `-m x` in a unit, shell script, githook, repo-root tool or JSON file (schedules, settings, rules)
  doc      x.py in instructions an agent follows: roles, skills, agent files, CLAUDE.md, lessons
  live     x.py in an installed user unit, the user's settings.json or crontab (outside the repo; said when unread)

History is not an entry point: the ledger, conversations, handoffs, closed items, the code-review record and dated design
prose are skipped on purpose.

    python3 src/RimMandrake/rimflow/entrypoint_inventory.py show NAME...      every entry point of these modules
    python3 src/RimMandrake/rimflow/entrypoint_inventory.py zero              rimflow modules no entry point reaches
    python3 src/RimMandrake/rimflow/entrypoint_inventory.py retired           exit 0 each RETIRED module is gone and unreached,
                                                                              1 not so, 2 the instrument cannot see
    python3 src/RimMandrake/rimflow/entrypoint_inventory.py revert --bundle P   exit 0 the bundle holds a commit undoing
                                                                              the retirement byte for byte, 1 not so
"""
import argparse
import ast
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RIMFLOW = "src/RimMandrake/rimflow"

# Retired by RIMFLOW_RETIRE_DEAD_MODULES. A name here must stay unreached; bring one back by reverting, not by editing this.
RETIRED = {
    "v3_cutover": "refusing stub of a one-shot run on 2026-10-29; the record stays in infrastructure/state/v3_cutover",
    "selftest_v3_cutover": "tested the stub's refusals",
    "v3_ready": "GO/NO-GO table for the 2026-10-28 trial night; it read the disabled Dispatcher",
    "selftest_v3_ready": "tested the table",
    "audit_prescreen_compare": "one-shot before/after of one fix against a pinned sha; its reading is from 2026-11-01",
}
# Named dead by redesign.md, and not: retiring these takes a decision, not a delete.
KEPT = {
    "close_audit": "redesign_final.md G20: an independent audit is kept while the gate it audits is replaced",
    "audit_prescreen": "role_launch imports it at module top (AP.STAMP); the Auditor's pre_launch runs it; only switched off",
    "relentless_head_age": "a lesson tells agents to run it before calling the pool order a defect; written 2026-11-05",
}
# (module, kind, a substring of the file): an instrument that cannot see these cannot be believed about a retired module.
PROBES = (
    ("audit_prescreen", "import", "role_launch.py"),
    ("audit_prescreen", "run", "dispatcher_schedule.json"),
    ("relentless", "run", ".service"),
    ("relentless_head_age", "doc", "infrastructure/state/lessons/"),
)

HISTORY = ("conversations/", "infrastructure/state/ledger/", "infrastructure/state/handoffs/",
           "infrastructure/state/items/", "infrastructure/state/code_review/", "infrastructure/state/queue/",
           "infrastructure/archive/", "Transient/", "vendor/", "research/", "design/", "tickets/", "sync/", "items/",
           "observed/", "deployed/", "Fable_Review/", "world/")
DOC_ROOTS = ("skills/", ".claude/", "infrastructure/agents/","infrastructure/state/lessons/", RIMFLOW + "/roles/", RIMFLOW + "/docs/")
RUN_EXT = (".service", ".timer", ".path", ".target", ".conf", ".sh", ".ps1", ".bat", ".cmd", ".json", ".yaml", ".yml", ".toml")
MAX_TEXT = 4_000_000


def tracked(root):
    """Paths under root, git's list when there is one (a read-only checkout may have none: then a walk, same exclusions)."""
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, timeout=120)
        if out.returncode == 0 and out.stdout:
            return [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]
    except (OSError, subprocess.SubprocessError):
        pass
    found = []
    for d, subs, files in os.walk(root):
        subs[:] = [s for s in subs if s not in (".git", "__pycache__", "Transient", "vendor")]
        found += [os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/") for f in files]
    return found


def classify(rel):
    """-> 'py' | 'run' | 'doc' | None (not a place that starts anything)."""
    if rel.startswith(HISTORY):
        return None
    base = os.path.basename(rel)
    if rel.endswith(".py"):
        return "py"
    if rel.startswith(DOC_ROOTS) and rel.endswith(".md") or rel == "CLAUDE.md":
        return "doc"
    if rel.endswith(RUN_EXT):
        return "run"
    if "/" not in rel and "." not in base or rel.startswith(("infrastructure/githooks/", ".claude/")) and "." not in base:
        return "run"     # ./publish, ./game, ./bridge; pre-commit, pre-push
    return None


def _word_rx(names):
    alt = "|".join(sorted(map(re.escape, names), key=len, reverse=True))
    return re.compile(r"(?<![\w-])(?:rimflow\.)?(%s)\.py\b|(?:^|\s)-m\s+(?:rimflow\.)?(%s)\b" % (alt, alt), re.M)


def _literal(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _docstrings(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body:
            first = n.body[0]
            if isinstance(first, ast.Expr) and _literal(first.value) is not None:
                out.add(id(first.value))
    return out


def scan_py(text, names, word):
    """-> [(name, kind, line)] from one Python source; a file that does not parse is scanned as plain text, never skipped."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return [(m.group(1) or m.group(2), "string", text.count("\n", 0, m.start()) + 1) for m in word.finditer(text)]
    hits, docs = [], _docstrings(tree)
    top = lambda s: s.rsplit(".", 1)[-1]
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            hits += [(top(a.name), "import", n.lineno) for a in n.names if top(a.name) in names]
        elif isinstance(n, ast.ImportFrom):
            if n.module and top(n.module) in names:
                hits.append((top(n.module), "import", n.lineno))
            hits += [(a.name, "import", n.lineno) for a in n.names if a.name in names]
        elif isinstance(n, ast.Call):
            fn = getattr(n.func, "attr", getattr(n.func, "id", ""))
            if fn in ("import_module", "__import__") and n.args and _literal(n.args[0]) is not None:
                if top(_literal(n.args[0])) in names:
                    hits.append((top(_literal(n.args[0])), "import", n.lineno))
        elif _literal(n) is not None and id(n) not in docs:
            s = n.value
            if top(s) in names and s.count(".") <= 1 and (s == top(s) or s.startswith("rimflow.")):
                hits.append((top(s), "bare", n.lineno))
            hits += [(m.group(1) or m.group(2), "string", n.lineno) for m in word.finditer(s)]
    return hits


def _read(path):
    try:
        if os.path.getsize(path) > MAX_TEXT:
            return None
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def installed_sources():
    """-> ({label: text}, [what could not be read]): what runs on this machine that the repo does not hold."""
    home = os.path.expanduser("~")
    got, unread = {}, []
    units = sorted(glob.glob(os.path.join(home, ".config/systemd/user/*")))
    for p in units:
        if os.path.isfile(p):
            got["installed:" + os.path.basename(p)] = _read(p) or ""
    if not units:
        unread.append("~/.config/systemd/user")
    settings = os.path.join(home, ".claude/settings.json")
    if os.path.isfile(settings):
        got["installed:settings.json"] = _read(settings) or ""
    else:
        unread.append("~/.claude/settings.json")
    try:
        cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=20)
        got["installed:crontab"] = cron.stdout if cron.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        unread.append("crontab")
    return got, unread


def inventory(root, names, installed=None):
    """-> ({name: [(kind, file, line)]}, [unread]): a module naming itself, and this tool and its selftest, are no entry."""
    names = set(names)
    word = _word_rx(names)
    quick = re.compile("|".join(map(re.escape, sorted(names))))
    out = {n: [] for n in names}
    skip = {RIMFLOW + "/entrypoint_inventory.py", RIMFLOW + "/selftest_entrypoint_inventory.py"}
    for rel in tracked(root):
        kind = classify(rel)
        if kind is None or rel in skip:
            continue
        text = _read(os.path.join(root, rel))
        if not text or not quick.search(text):
            continue
        own = os.path.basename(rel)[:-3] if rel.endswith(".py") else None
        if kind == "py":
            found = [(k, ln, n) for n, k, ln in scan_py(text, names, word)]
        else:
            found = [(kind, text.count("\n", 0, m.start()) + 1, m.group(1) or m.group(2)) for m in word.finditer(text)]
        for k, ln, n in found:
            if n != own:
                out[n].append((k, rel, ln))
    src, unread = installed_sources() if installed is None else installed
    for label, text in src.items():
        for m in word.finditer(text or ""):
            out[m.group(1) or m.group(2)].append(("live", label, text.count("\n", 0, m.start()) + 1))
    return out, unread


def blind(inv):
    """-> [probes the inventory cannot see]."""
    missing = []
    for name, kind, where in PROBES:
        if not any(k == kind and where in f for k, f, _ in inv.get(name, ())):
            missing.append("%s %s in %s" % (name, kind, where))
    return missing


def check_retired(root=ROOT, retired=None, kept=None, probes=True, installed=None):
    """-> (exit code, lines)."""
    retired = RETIRED if retired is None else retired
    kept = KEPT if kept is None else kept
    names = set(retired) | set(kept) | ({p[0] for p in PROBES} if probes else set())
    inv, unread = inventory(root, names, installed)
    lines = ["installed sources unread here (the tracked units are still read): " + ", ".join(unread)] if unread else []
    if probes:
        miss = blind(inv)
        if miss:
            return 2, lines + ["UNMEASURED: the instrument cannot see known entry points: " + "; ".join(miss)]
    bad = []
    for n in sorted(retired):
        path = "%s/%s.py" % (RIMFLOW, n)
        if os.path.exists(os.path.join(root, path)):
            bad.append("%s still exists" % path)
        bad += ["%s reached by %s %s:%d" % (n, k, f, ln) for k, f, ln in inv[n]]
    for n in sorted(kept):
        if not os.path.exists(os.path.join(root, RIMFLOW, n + ".py")):
            bad.append("%s is gone but is kept: %s" % (n, kept[n]))
    if bad:
        return 1, lines + bad
    return 0, lines + ["OK %d retired modules absent and unreached; %d kept present" % (len(retired), len(kept))]


def _git(root, *args, check=True):
    p = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=300)
    if check and p.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args[:3]), p.stderr.strip()[:300]))
    return p.stdout.strip()


def _bundle_header(path):
    """-> (prerequisite shas, [(sha, ref)])."""
    prereq, heads = [], []
    with open(path, "rb") as f:
        if not f.readline().startswith(b"# v"):
            raise RuntimeError("%s is not a git bundle" % path)
        for raw in f:
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if not line:
                break
            if line.startswith("-"):
                prereq.append(line[1:].split(" ")[0])
            elif not line.startswith("@"):
                sha, _, ref = line.partition(" ")
                heads.append((sha, ref))
    return prereq, heads


def check_revert(bundle, root=ROOT, retired=None):
    """-> (exit code, lines): the one head R is the child of a deletion commit D in our history, and R's tree is D^'s."""
    retired = RETIRED if retired is None else retired
    if not os.path.isfile(bundle):
        return 1, ["no bundle at %s" % bundle]
    tmp = tempfile.mkdtemp(prefix="entrypoint_revert_")
    try:
        prereq, heads = _bundle_header(bundle)
        if len(heads) != 1 or len(prereq) != 1:
            return 1, ["the bundle must hold one head on one prerequisite, not %d on %d" % (len(heads), len(prereq))]
        rev, deletion = heads[0][0], prereq[0]
        head = _git(root, "rev-parse", "HEAD")
        if subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", deletion, head]).returncode:
            return 1, ["deletion commit %s is not in the history of %s" % (deletion[:10], head[:10])]
        objects = os.path.abspath(os.path.join(root, _git(root, "rev-parse", "--git-path", "objects")))
        _git(tmp, "init", "--quiet", "--bare", ".")
        with open(os.path.join(tmp, "objects", "info", "alternates"), "w") as f:
            f.write(objects + "\n")
        _git(tmp, "update-ref", "refs/heads/base", deletion)    # the fetch's connectivity check stops here, not at the root
        _git(tmp, "fetch", "--quiet", os.path.abspath(bundle), "%s:refs/heads/revert" % heads[0][1])
        parents = _git(tmp, "rev-list", "--parents", "-n", "1", rev).split()[1:]
        if parents != [deletion]:
            return 1, ["revert %s has parents %s, not the deletion commit" % (rev[:10], parents)]
        gone = {l.split("\t", 1)[1] for l in _git(tmp, "diff-tree", "--no-commit-id", "--name-status", "-r", deletion).splitlines()
                if l.startswith("D\t")}
        want = {"%s/%s.py" % (RIMFLOW, n) for n in retired}
        if want - gone:
            return 1, ["commit %s does not delete %s" % (deletion[:10], sorted(want - gone))]
        drift = _git(tmp, "diff", "--name-only", deletion + "^", rev)
        if drift:
            return 1, ["revert %s differs from the tree before the deletion: %s" % (rev[:10], drift.splitlines()[:5])]
        return 0, ["OK revert commit %s undoes deletion commit %s byte for byte" % (rev, deletion)]
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        return 1, ["bundle check failed: %s" % e]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def zero(root=ROOT):
    """-> [(module, 'none'|'selftest only')]: the rimflow modules nothing but at most their selftests reaches."""
    mods = [os.path.basename(p)[:-3] for p in glob.glob(os.path.join(root, RIMFLOW, "*.py"))]
    mods = [m for m in mods if not m.startswith("selftest_") and m not in ("__init__", "entrypoint_inventory")]
    inv, _ = inventory(root, mods)
    out = []
    for m in sorted(mods):
        real = [e for e in inv[m] if not os.path.basename(e[1]).startswith("selftest")]
        if not real:
            out.append((m, "selftest only" if inv[m] else "none"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("show").add_argument("names", nargs="+")
    sub.add_parser("zero")
    sub.add_parser("retired")
    sub.add_parser("revert").add_argument("--bundle", required=True)
    a = ap.parse_args(argv)
    if a.verb == "show":
        inv, unread = inventory(ROOT, a.names)
        for n in a.names:
            print("%s: %d entry points" % (n, len(inv[n])))
            for k, f, ln in sorted(inv[n]):
                print("  %-6s %s:%d" % (k, f, ln))
        if unread:
            print("unread: " + ", ".join(unread))
        return 0
    if a.verb == "zero":
        for m, how in zero():
            print("%-34s %s" % (m, how))
        return 0
    code, lines = check_retired() if a.verb == "retired" else check_revert(a.bundle)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
