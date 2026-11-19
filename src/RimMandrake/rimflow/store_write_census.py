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

A CANDIDATE is a .py under src/RimMandrake that names a store (selftests, guard_*_accept.py and acceptance tests,
modledger*.py and the census itself excepted; a .py whose source cannot be decoded is a candidate too, never measured).
Each module gets one verdict:
  WRITER         the hook saw it open a store for writing, or rename a file onto one. The stack is read from the write
                 outwards up to the first test or modledger frame: a write whose innermost frame is a test (a fixture,
                 a stub the module called back) or modledger blames nobody; otherwise the innermost module there that
                 names a store is blamed, so a generic helper it calls is not, and a module naming none only when no
                 candidate is there. A frame from a copy whose content differs from the module on disk is skipped.
                 Nothing under a .git folder is a store;
  NO_WRITE_SEEN  looked and saw no write: every scope of it (function, class or module body, lambda, generator) that
                 names a store or holds a write call (open with a writing or non-literal mode, os.open, .write(,
                 .writelines(, .write_text(, .write_bytes(, .dump(, os.replace/os.rename, a one-argument .replace( or
                 any .rename(, shutil copy/move) started at least once in the module as it is on disk, and none wrote;
  NOT_MEASURED   some such scope never started under any census test (named in never_ran), or two such scopes share a
                 line and a name (two lambdas on one line), so no start can tell them apart: never "does not write".
Writes that blame nobody are counted in fixture_writes. A Python child a test starts without the hook (-I/-S/-E, or
an env that drops it) is listed in unhooked_children: whatever it did is unseen. The record's status is "ok", or
"could_not_look" with its cause: the probe was not caught, the tree or the test list could not be read, or no
configured test exists.

Known limits: a scope that ran only down a branch that does not write reads NO_WRITE_SEEN (the census measures
scopes, not every path); a write through a file handle a test opened and passed in is the test's open, so blames
nobody; a store opened through a dir_fd by os.open is not resolved (its name alone decides).
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
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HOOK_DIR = os.path.join(HERE, "store_census_hook")
SELF = ("src/RimMandrake/rimflow/store_write_census.py",)
SELF_DIR = "src/RimMandrake/rimflow/store_census_hook/"
NAMES = re.compile(r"stage_record\.json|journal\.md|['\"/]stage\.json")
LEDGER_IDENTITY = ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN")    # as publish.py: a test is not the publisher
PROBE = "src/RimMandrake/rimflow/census_probe_writer.py"
PROBE_SRC = ("import os, sys\n\ndef plant(root):\n    c = os.path.join(root, 'design', 'concepts', 'Probe')\n"
             "    os.makedirs(c, exist_ok=True)\n    with open(os.path.join(c, 'stage.json'), 'w') as f:\n"
             "        f.write('{}')\n\nplant(sys.argv[1])\n")


def excluded(rel):
    """A test, modledger or the census itself: never a candidate, and the boundary where blame stops."""
    b = os.path.basename(rel)
    return (b.startswith("selftest_") or (b.startswith("guard_") and b.endswith("_accept.py"))
            or b.startswith("modledger") or "/acceptance/" in rel or rel in SELF or rel == PROBE
            or rel.startswith(SELF_DIR))


WRITE_ATTRS = {"write", "writelines", "write_text", "write_bytes", "dump", "rename"}
SHUTIL = {"copy", "copy2", "copyfile", "copytree", "move", "copyfileobj"}
MODE = re.compile(r"^[rwaxbtU+]+$")
AMBIGUOUS = "ambiguous:"                               # a required scope no start can vouch for


def _opens_for_write(call):
    """An open(...) / x.open(...) call: does it write, or can its mode not be told from the source?"""
    named = isinstance(call.func, ast.Name)
    lits = [a.value for a in call.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    modes = [m for m in lits if MODE.match(m)]
    kw = {k.arg: k.value for k in call.keywords}
    for k in ("mode", "flags"):
        if k in kw:
            v = kw[k]
            if not (isinstance(v, ast.Constant) and isinstance(v.value, str)):
                return True
            modes.append(v.value)
    if named and len(call.args) >= 2 and not (isinstance(call.args[1], ast.Constant)
                                             and isinstance(call.args[1].value, str)):
        return True                                    # open(p, mode_var): cannot be told, counted as a write
    if isinstance(call.func, ast.Attribute):
        if isinstance(call.func.value, ast.Name) and call.func.value.id == "os":
            return True                                # os.open(p, flags): flags decide, counted as a write
        if any(not (isinstance(a, ast.Constant) and isinstance(a.value, str)) for a in call.args[:2]):
            return True                                # p.open(mode_var), io.open(p, mode_var): counted as a write
    return any(c in m for m in modes for c in "wax+")


def _is_write_call(n):
    if not isinstance(n, ast.Call):
        return False
    f = n.func
    if (isinstance(f, ast.Name) and f.id == "open") or (isinstance(f, ast.Attribute) and f.attr == "open"):
        return _opens_for_write(n)
    if not isinstance(f, ast.Attribute):
        return False
    recv = f.value.id if isinstance(f.value, ast.Name) else None
    return (f.attr in WRITE_ATTRS or (f.attr == "replace" and (recv == "os" or len(n.args) == 1))
            or (recv == "shutil" and f.attr in SHUTIL))


def store_functions(src):
    """-> {"first line:name" of a code object: label}: the scopes (function, class or module body, lambda, generator)
    holding a line that names a store or a write call. A decorated def starts at its first decorator, as its code
    object does; module code starts at line 1."""
    tree = ast.parse(src)
    scopes = []                                        # (start, end, key, label)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            first = min([d.lineno for d in n.decorator_list] + [n.lineno])
            scopes.append((first, n.end_lineno, "%d:%s" % (first, n.name), "%s (line %d)" % (n.name, n.lineno)))
        elif isinstance(n, (ast.Lambda, ast.GeneratorExp)):
            name = "<lambda>" if isinstance(n, ast.Lambda) else "<genexpr>"
            scopes.append((n.lineno, n.end_lineno, "%d:%s" % (n.lineno, name), "%s (line %d)" % (name, n.lineno)))
    lines = {i for i, line in enumerate(src.split("\n"), 1) if NAMES.search(line)}
    lines |= {n.lineno for n in ast.walk(tree) if _is_write_call(n)}
    shared = {k for k in (s[2] for s in scopes) if sum(1 for t in scopes if t[2] == k) > 1}
    out = {}
    for i in sorted(lines):
        inner = [s for s in scopes if s[0] <= i <= s[1]]
        if inner:
            s = max(inner, key=lambda s: (s[0], -s[1]))
            # two scopes with one identity (two lambdas on a line): one starting cannot vouch for the other
            out[AMBIGUOUS + s[2] if s[2] in shared else s[2]] = s[3] + (", shares its line and name" if s[2] in shared
                                                                         else "")
        else:
            out["1:<module>"] = "<module>"
    return out


def _walk(root):
    """-> sorted repo-relative paths of every .py under src/RimMandrake; raises OSError on a folder it cannot read."""
    def boom(e):
        raise e
    out = []
    for d, dirs, files in os.walk(os.path.join(root, "src", "RimMandrake"), onerror=boom):
        dirs.sort()
        out += [os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/") for f in files if f.endswith(".py")]
    if not out:
        raise OSError("no .py under %s" % os.path.join(root, "src", "RimMandrake"))
    return sorted(out)


def _source(path):
    """-> (source, None) or (None, why) for a .py read by its own coding cookie."""
    try:
        with tokenize.open(path) as f:
            return f.read(), None
    except (SyntaxError, UnicodeDecodeError, LookupError) as e:
        return None, "%s: %s" % (type(e).__name__, e)


def candidates(root):
    """-> {repo-relative path: source or None (undecodable)}; raises OSError when the tree cannot be read."""
    out = {}
    for rel in _walk(root):
        if excluded(rel):
            continue
        s, why = _source(os.path.join(root, rel))
        if s is None or NAMES.search(s):
            out[rel] = s
    return out


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def fingerprint(root):
    """sha256 over every .py under src/RimMandrake and the pipeline test list: a record read later is trusted only on
    the same code and the same tests."""
    h = hashlib.sha256()
    cfg = os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json")
    if os.path.isfile(cfg):
        with open(cfg, "rb") as f:
            h.update(b"pipeline_tests.json" + hashlib.sha256(f.read()).digest())
    for rel in _walk(root):
        h.update(rel.encode())
        with open(os.path.join(root, rel), "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def select_tests(root, cands):
    """-> ([{"test", "args"}], [missing configured tests], why_none): the pipeline tests (live_excluded out) and each
    candidate's own selftests. Raises ValueError/OSError when pipeline_tests.json cannot be read."""
    tests, live, missing = {}, {}, []
    cfg_path = os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json")
    if os.path.isfile(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        live = cfg.get("live_excluded") or {}
        for c in cfg.get("tests", ()):
            if c["test"] in live:
                continue
            if not os.path.isfile(os.path.join(root, c["test"])):
                missing.append(c["test"])
                continue
            tests[c["test"]] = {"test": c["test"], "args": c.get("args") or []}
    for rel in cands:
        d, stem = os.path.dirname(rel), os.path.basename(rel)[:-3]
        for t in sorted(glob.glob(os.path.join(root, d, "selftest_%s.py" % glob.escape(stem)))
                        + glob.glob(os.path.join(root, d, "selftest_%s_*.py" % glob.escape(stem)))):
            t = os.path.relpath(t, root).replace(os.sep, "/")
            if t not in live:
                tests.setdefault(t, {"test": t, "args": []})
    why = None if tests else "no runnable census test under %s%s" % (
        root, " (%d configured tests missing)" % len(missing) if missing else "")
    return sorted(tests.values(), key=lambda c: c["test"]), missing, why


def _run(root, c, outdir, hook_dir, timeout):
    """One test under the hook -> {"test", "rc" (None = timed out), "seconds", "dir"}."""
    tdir = tempfile.mkdtemp(prefix="census_tmp_")
    rec = tempfile.mkdtemp(prefix="rec_", dir=outdir)
    env = {k: v for k, v in os.environ.items() if k not in LEDGER_IDENTITY}
    env.update(PYTHONPATH=os.pathsep.join([hook_dir] + [p for p in [env.get("PYTHONPATH")] if p]),
               RM_STORE_CENSUS_DIR=rec, RM_STORE_CENSUS_TEST=c["test"], TMPDIR=tdir)
    t0 = time.monotonic()
    try:
        rc = subprocess.run([sys.executable, os.path.join(root, c["test"])] + [str(a) for a in c["args"]], cwd=root,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout,
                            stdin=subprocess.DEVNULL, env=env).returncode
    except subprocess.TimeoutExpired:
        rc = None
    finally:
        shutil.rmtree(tdir, ignore_errors=True)
    return {"test": c["test"], "rc": rc, "seconds": round(time.monotonic() - t0, 1), "dir": rec}


def _read(rec):
    """-> (events, ran {hook key: set of "first:name"}, processes reporting)."""
    writes, ran, procs = [], {}, 0
    for p in glob.glob(os.path.join(rec, "*.writes.jsonl")):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    writes.append(json.loads(line))
                except ValueError:
                    continue
    for p in glob.glob(os.path.join(rec, "*.cov.json")):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
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
    key = PROBE + "#" + file_sha(p)
    r = _run(root, {"test": PROBE, "args": [root]}, outdir, hook_dir, 60)
    writes, ran, procs = _read(r["dir"])
    caught = any(w.get("event") == "open" and (w.get("chain") or [None])[0] == key for w in writes) \
        and "1:<module>" in ran.get(key, set())
    return {"caught": caught, "detail": "probe exit %s, %d write(s) seen, %d process record(s)"
            % (r["rc"], len(writes), procs)}


def census(root=REPO, workers=6, hook_dir=None, timeout=None):
    """-> the record (a dict; see the module doc). Never raises for a test that fails or hangs: those are counted; a
    tree or test list that cannot be read is could_not_look with its cause."""
    root = os.path.abspath(root)
    hook_dir = hook_dir or os.environ.get("RM_STORE_CENSUS_HOOK_DIR") or HOOK_DIR
    rec = {"schema": 2, "root": root, "status": "could_not_look", "cause": None, "modules": {}, "fixture_writes": 0,
           "tests": [], "missing_tests": [], "unhooked_children": [], "probe": {}}
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
            real = {rel: file_sha(os.path.join(root, rel)) for rel in _walk(root)}
            tests, rec["missing_tests"], why = select_tests(root, cands)
            cfg_path = os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json")
            if timeout is None and os.path.isfile(cfg_path):
                with open(cfg_path, encoding="utf-8") as f:
                    timeout = json.load(f).get("timeout_s", 180)
            rec["fingerprint"] = fingerprint(root)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            rec["cause"] = "could not read the tree or its test list: %s: %s" % (type(e).__name__, e)
            return rec
        if why:
            rec["cause"] = why
            return rec
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            runs = list(ex.map(lambda c: _run(root, c, outdir, hook_dir, timeout or 180), tests))
        events, ran = [], {}
        for r in runs:
            w, rn, procs = _read(r.pop("dir"))
            r["processes"] = procs
            events += w
            for k, v in rn.items():
                rel, _, h = k.partition("#")
                if real.get(rel) == h:                 # only the module as it is on disk, never a differing copy
                    ran.setdefault(rel, set()).update(v)
            rec["tests"].append(r)
        blamed = {}
        for w in events:
            if w.get("event") == "unhooked_child":
                rec["unhooked_children"].append({"test": w.get("test"), "why": w.get("path"),
                                                 "chain": [k.partition("#")[0] for k in w.get("chain", [])][:6]})
                continue
            chain = []                  # the src modules above the write, up to the first test or modledger frame
            for k in w.get("chain", []):
                rel, _, h = k.partition("#")
                if excluded(rel):
                    break
                if real.get(rel) == h:
                    chain.append(rel)
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
                                  "chain": [k.partition("#")[0] for k in ws[0]["chain"]][:6]})
            else:
                src = cands[rel]
                if src is None:
                    m["never_ran"] = ["its source cannot be decoded: %s" % _source(os.path.join(root, rel))[1]]
                else:
                    try:
                        need = store_functions(src)
                        m["never_ran"] = [lab for key, lab in sorted(need.items(), key=lambda kv: kv[1])
                                          if key not in ran.get(rel, set())]
                    except SyntaxError as e:
                        m["never_ran"] = ["its source cannot be parsed: %s" % e]
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
    print("%d tests, %d red, %d timed out, %d configured tests missing; %d fixture writes; %d unhooked Python children"
          % (len(rec["tests"]), sum(1 for t in rec["tests"] if t["rc"] not in (0, None)),
             sum(1 for t in rec["tests"] if t["rc"] is None), len(rec["missing_tests"]), rec["fixture_writes"],
             len(rec["unhooked_children"])))
    return 1 if by.get("WRITER") else (2 if by.get("NOT_MEASURED") or rec["unhooked_children"] else 0)


if __name__ == "__main__":
    sys.exit(main())
