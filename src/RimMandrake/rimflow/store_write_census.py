#!/usr/bin/env python3
"""store_write_census.py: which modules WRITE the old mod stores, measured at run time (item
RIMMANDRAKE_NARROW_CUTOVER_WRITER_CHECK_EIGHT_OF_THIRTEEN_READ; the Conductor's decision 2026-11-18 7:35 PM PST: writers
are measured, not matched from source text and not kept on a hand allowlist, which goes stale the day a module changes).

    python3 src/RimMandrake/rimflow/store_write_census.py [--root R] [--workers N] [--out record.json]

The old stores are stage.json, journal.md and version/stage_record.json (the cutover moves them into modledger). The
census runs the pipeline selftests (Utils/pipeline_tests.json, its live_excluded left out) and every candidate's own
selftest_<stem>.py / selftest_<stem>_*.py, each with store_census_hook/ first on PYTHONPATH, whose sitecustomize records
each open-for-writing of a store (and each rename onto one) with the modules on the stack, and which functions started.
Before the record is trusted, a planted writer is run the same way and must be caught.

A CANDIDATE is a .py under src/RimMandrake that names a store (selftests, guard_* and acceptance tests, modledger*.py and
the census itself excepted). Each module gets one verdict:
  WRITER         the hook saw it open a store for writing, or rename a file onto one. The stack is read from the write
                 outwards up to the first test or modledger frame: a write whose innermost frame is a test (a fixture,
                 a stub the module called back) or modledger blames nobody; otherwise the innermost module there that
                 names a store is blamed, so a generic helper it calls is not, and a module naming none only when no
                 candidate is there. Nothing under a .git folder is a store;
  NO_WRITE_SEEN  looked and saw no write: every function of it that names a store or holds a write call
                 (open(...,"w"/"a"), .write_text(, json.dump(, os.replace() started at least once, and none wrote one;
  NOT_MEASURED   some such function never started under any census test (named in never_ran): never "does not write".
Writes that blame nobody are counted in fixture_writes. The record's status is "ok", or "could_not_look" with its
cause when the hook cannot be shown to see (the probe was not caught) or no test could be found.

Known limits, each reading the safe way or named: a process started with -I/-S/-E, or with an env that drops
PYTHONPATH, carries no hook, so its code reads as never run; a function that ran only down a branch that does not write
reads NO_WRITE_SEEN (the census measures functions, not every path); a write through a path handed to an unexercised
function of another module is seen only when that function runs.
"""
import argparse
import ast
import concurrent.futures
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HOOK_DIR = os.path.join(HERE, "store_census_hook")
SELF = ("src/RimMandrake/rimflow/store_write_census.py", "src/RimMandrake/rimflow/store_census_hook/sitecustomize.py")
NAMES = re.compile(r"stage_record\.json|journal\.md|['\"/]stage\.json")
WRITE = re.compile(r"open\([^)]*['\"][wa]b?['\"]|\.write_text\(|json\.dump\(|os\.replace\(")
LEDGER_IDENTITY = ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN")    # as publish.py: a test is not the publisher
PROBE = "src/RimMandrake/rimflow/census_probe_writer.py"
PROBE_SRC = ("import os, sys\n\ndef plant(root):\n    c = os.path.join(root, 'design', 'concepts', 'Probe')\n"
             "    os.makedirs(c, exist_ok=True)\n    with open(os.path.join(c, 'stage.json'), 'w') as f:\n"
             "        f.write('{}')\n\nplant(sys.argv[1])\n")


def excluded(rel):
    b = os.path.basename(rel)
    return (b.startswith("selftest_") or b.startswith("guard_") or b.startswith("modledger")
            or "/acceptance/" in rel or rel in SELF or rel == PROBE)


def store_functions(src):
    """-> {first line of a code object: label}: the functions (module and class bodies included) holding a line that
    names a store or makes a write call. A decorated def starts at its first decorator, as its code object does."""
    tree = ast.parse(src)
    scopes = []                                        # (start, end, first, label)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            first = min([d.lineno for d in getattr(n, "decorator_list", [])] + [n.lineno])
            label = getattr(n, "name", "<lambda>")
            scopes.append((first, n.end_lineno, first, "%s (line %d)" % (label, n.lineno)))
    out = {}
    for i, line in enumerate(src.split("\n"), 1):
        if not (NAMES.search(line) or WRITE.search(line)):
            continue
        inner = [s for s in scopes if s[0] <= i <= s[1]]
        if inner:
            s = max(inner, key=lambda s: s[0])
            out[s[2]] = s[3]
        else:
            out[1] = "<module>"
    return out


def candidates(root):
    """-> {repo-relative path: source} of every module that names a store, or raises OSError."""
    out = {}
    for py in sorted(glob.glob(os.path.join(root, "src", "RimMandrake", "**", "*.py"), recursive=True)):
        rel = os.path.relpath(py, root).replace(os.sep, "/")
        if excluded(rel):
            continue
        try:
            s = open(py, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        if NAMES.search(s):
            out[rel] = s
    return out


def fingerprint(root):
    """sha256 over every .py under src/RimMandrake: a record read later is trusted only on the same code."""
    h = hashlib.sha256()
    for py in sorted(glob.glob(os.path.join(root, "src", "RimMandrake", "**", "*.py"), recursive=True)):
        h.update(os.path.relpath(py, root).encode())
        with open(py, "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def select_tests(root, cands):
    """-> ([{"test", "args"}], why_none): the pipeline tests (live_excluded out) and each candidate's own selftests."""
    tests, live = {}, {}
    cfg_path = os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json")
    if os.path.isfile(cfg_path):
        cfg = json.load(open(cfg_path, encoding="utf-8"))
        live = cfg.get("live_excluded") or {}
        for c in cfg.get("tests", ()):
            if c["test"] not in live:
                tests[c["test"]] = {"test": c["test"], "args": c.get("args") or []}
    for rel in cands:
        d, stem = os.path.dirname(rel), os.path.basename(rel)[:-3]
        for t in sorted(glob.glob(os.path.join(root, d, "selftest_%s.py" % stem))
                        + glob.glob(os.path.join(root, d, "selftest_%s_*.py" % stem))):
            t = os.path.relpath(t, root).replace(os.sep, "/")
            if t not in live:
                tests.setdefault(t, {"test": t, "args": []})
    return sorted(tests.values(), key=lambda c: c["test"]), (None if tests else "no census test found under %s" % root)


def _run(root, c, outdir, hook_dir, timeout):
    """One test under the hook -> {"test", "rc" (None = timed out), "seconds", "dir"}."""
    tdir = tempfile.mkdtemp(prefix="census_tmp_")
    rec = tempfile.mkdtemp(prefix="rec_", dir=outdir)
    env = {k: v for k, v in os.environ.items() if k not in LEDGER_IDENTITY}
    env.update(PYTHONPATH=os.pathsep.join([hook_dir] + [p for p in [env.get("PYTHONPATH")] if p]),
               RM_STORE_CENSUS_DIR=rec, RM_STORE_CENSUS_TEST=c["test"], TMPDIR=tdir)
    t0 = time.monotonic()
    try:
        r = subprocess.run([sys.executable, os.path.join(root, c["test"])] + [str(a) for a in c["args"]], cwd=root,
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = None
    finally:
        shutil.rmtree(tdir, ignore_errors=True)
    return {"test": c["test"], "rc": rc, "seconds": round(time.monotonic() - t0, 1), "dir": rec}


def _read(rec):
    """-> (writes, ran {module: set of first lines}, processes reporting)."""
    writes, ran, procs = [], {}, 0
    for p in glob.glob(os.path.join(rec, "*.writes.jsonl")):
        for line in open(p, encoding="utf-8"):
            try:
                writes.append(json.loads(line))
            except ValueError:
                continue
    for p in glob.glob(os.path.join(rec, "*.cov.json")):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError:
            continue
        procs += 1
        for k, v in (d.get("ran") or {}).items():
            ran.setdefault(k, set()).update(v)
    return writes, ran, procs


def _probe(outdir, hook_dir):
    """Plant a writer and run it under the hook: -> {"caught": bool, "detail"}."""
    root = tempfile.mkdtemp(prefix="probe_", dir=outdir)
    p = os.path.join(root, PROBE)
    os.makedirs(os.path.dirname(p))
    with open(p, "w") as f:
        f.write(PROBE_SRC)
    r = _run(root, {"test": PROBE, "args": [root]}, outdir, hook_dir, 60)
    writes, ran, procs = _read(r["dir"])
    caught = any(w.get("chain", [None])[0] == PROBE for w in writes) and 1 in ran.get(PROBE, set())
    return {"caught": caught, "detail": "probe exit %s, %d write(s) seen, %d process record(s)"
            % (r["rc"], len(writes), procs)}


def census(root=REPO, workers=6, hook_dir=None, timeout=None):
    """-> the record (a dict; see the module doc). Never raises for a test that fails or hangs: those are counted."""
    root = os.path.abspath(root)
    hook_dir = hook_dir or os.environ.get("RM_STORE_CENSUS_HOOK_DIR") or HOOK_DIR
    rec = {"schema": 1, "root": root, "status": "could_not_look", "cause": None, "modules": {}, "fixture_writes": 0,
           "tests": [], "probe": {}}
    outdir = tempfile.mkdtemp(prefix="store_census_")
    try:
        if not os.path.isfile(os.path.join(hook_dir, "sitecustomize.py")):
            rec["probe"] = {"caught": False, "detail": "no sitecustomize.py in %s" % hook_dir}
        else:
            rec["probe"] = _probe(outdir, hook_dir)
        if not rec["probe"]["caught"]:
            rec["cause"] = "the planted probe write was not caught (%s): the hook cannot be shown to see" \
                % rec["probe"]["detail"]
            return rec
        try:
            cands = candidates(root)
        except OSError as e:
            rec["cause"] = "could not read the tree: %s" % e
            return rec
        tests, why = select_tests(root, cands)
        if why:
            rec["cause"] = why
            return rec
        if timeout is None:
            cfg_path = os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json")
            timeout = json.load(open(cfg_path)).get("timeout_s", 180) if os.path.isfile(cfg_path) else 180
        rec["fingerprint"] = fingerprint(root)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            runs = list(ex.map(lambda c: _run(root, c, outdir, hook_dir, timeout), tests))
        writes, ran = [], {}
        for r in runs:
            w, rn, procs = _read(r.pop("dir"))
            r["processes"] = procs
            writes += w
            for k, v in rn.items():
                ran.setdefault(k, set()).update(v)
            rec["tests"].append(r)
        blamed = {}
        for w in writes:
            chain = []                  # the src modules above the write, up to the first test or modledger frame
            for k in w.get("chain", []):
                if excluded(k):
                    break
                chain.append(k)
            if not chain:               # a test wrote it (a fixture, or a stub the module called back), or modledger did
                rec["fixture_writes"] += 1
                continue
            who = next((k for k in chain if k in cands), chain[0])
            blamed.setdefault(who, []).append(w)
        for rel in sorted(set(cands) | set(blamed)):
            m = {"candidate": rel in cands}
            if rel in blamed:
                ws = blamed[rel]
                m.update(verdict="WRITER", writes=len(ws),
                         example={"path": ws[0]["path"], "event": ws[0]["event"], "test": ws[0]["test"],
                                  "chain": ws[0]["chain"][:6]})
            else:
                try:
                    need = store_functions(cands[rel])
                except SyntaxError as e:
                    need = {}
                    m["never_ran"] = ["unparseable: %s" % e]
                never = [lab for first, lab in sorted(need.items()) if first not in ran.get(rel, set())]
                m["never_ran"] = m.get("never_ran", []) + never
                m["verdict"] = "NOT_MEASURED" if m["never_ran"] else "NO_WRITE_SEEN"
            rec["modules"][rel] = m
        rec["status"] = "ok"
        return rec
    finally:
        shutil.rmtree(outdir, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", help="write the record here as JSON")
    a = ap.parse_args(argv)
    rec = census(a.root, a.workers)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
    if rec["status"] != "ok":
        print("COULD NOT LOOK  %s" % rec["cause"])
        return 3
    by = {}
    for rel, m in rec["modules"].items():
        by.setdefault(m["verdict"], []).append(rel)
    for v in ("WRITER", "NOT_MEASURED", "NO_WRITE_SEEN"):
        print("%-13s %d  %s" % (v, len(by.get(v, [])), ", ".join(by.get(v, []))))
    print("%d tests, %d red, %d timed out; %d fixture writes" % (
        len(rec["tests"]), sum(1 for t in rec["tests"] if t["rc"] not in (0, None)),
        sum(1 for t in rec["tests"] if t["rc"] is None), rec["fixture_writes"]))
    return 1 if by.get("WRITER") else (2 if by.get("NOT_MEASURED") else 0)


if __name__ == "__main__":
    sys.exit(main())
