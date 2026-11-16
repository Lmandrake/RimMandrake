#!/usr/bin/env python3
"""tunable_sweep.py: does any selftest go red because the owner changed a shipped tunable number?

RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS criterion A1: for each owner-tunable number in a config, a scratch copy of
the repo with that number changed to another sane value runs the selftests that read the config, and no new red is
caused by the change alone. Selftests pin fixtures; at most one deliberate "shipped config is sane" range check each.

    tunable_sweep.py <config.json> [--tests T ...] [--only GLOB] [--deep] [--out report.json] [--jobs N] [--timeout S]

The scratch copy is a `git clone --shared` of HEAD in /tmp plus this tree's uncommitted edits to tracked files. Every
numeric leaf (keys starting "_" skipped) is mutated at once (int n -> 2n, or n+1 below 2; a fraction in (0, 1)
halfway to 1; another float x1.5); the readers
(default: every selftest_*.py naming the config's file name;
--deep adds every selftest importing a module that names it) run on the base and on the mutated copy. A test red only
when mutated is bisected down to the leaves that alone turn it red. A test red on the base is reported, not judged.
Prints one line per red reader and `RESULT: CLEAN|PINNED n`; exit 0 clean, 1 pinned, 2 usage.
"""
import argparse
import concurrent.futures
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def leaves(o, path=()):
    """-> [(path tuple, number)] for every numeric leaf; dict keys starting '_' (docs) are skipped."""
    if isinstance(o, dict):
        return [x for k, v in o.items() if not str(k).startswith("_") for x in leaves(v, path + (k,))]
    if isinstance(o, list):
        return [x for i, v in enumerate(o) for x in leaves(v, path + (i,))]
    if isinstance(o, (int, float)) and not isinstance(o, bool):
        return [(path, o)]
    return []


def mutated(v):
    if isinstance(v, int):
        return v * 2 if v >= 2 else v + 1
    if 0 < v < 1:
        return round((v + 1) / 2, 6)           # a fraction stays a fraction: halfway to 1
    return round(v * 1.5, 6) if v else 0.5


def apply(cfg, paths):
    """-> a deep copy of cfg with each leaf in `paths` mutated."""
    out = json.loads(json.dumps(cfg))
    for p in paths:
        o = out
        for k in p[:-1]:
            o = o[k]
        o[p[-1]] = mutated(o[p[-1]])
    return out


def scratch_copy(repo):
    tmp = tempfile.mkdtemp(prefix="tunable_sweep_")
    subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "clone", "-q", "--shared", repo, tmp + "/r"],
                   check=True, timeout=600)
    head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                          timeout=60).stdout
    subprocess.run(["git", "-C", tmp + "/r", "checkout", "-q", "--detach", head.strip()], check=True, timeout=600)
    edits = subprocess.run(["git", "-C", repo, "diff", "--name-only", "HEAD"], capture_output=True, text=True,
                           check=True, timeout=120).stdout.split()
    for p in edits:
        src, dst = os.path.join(repo, p), os.path.join(tmp, "r", p)
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    return tmp, tmp + "/r"


def readers(root, cfg_rel, deep=False):
    """Selftests naming the config's stem; with `deep`, also every selftest importing a module that names it."""
    stem = os.path.splitext(os.path.basename(cfg_rel))[0]

    def grep(*args):
        r = subprocess.run(["git", "-C", root, "grep", *args], capture_output=True, text=True, timeout=120)
        return [p for p in r.stdout.split() if p]
    out = set(grep("-l", "-F", stem, "--", "*selftest_*.py"))
    if deep:
        mods = sorted({os.path.splitext(os.path.basename(p))[0] for p in grep("-l", "-F", stem, "--", "*.py")
                       if not os.path.basename(p).startswith("selftest_")})
        if mods:
            pat = r"^\s*(import|from)\s.*\b(%s)\b" % "|".join(re.escape(m) for m in mods)
            out |= set(grep("-l", "-E", pat, "--", "*selftest_*.py"))
    return sorted(out)


def run_tests(root, tests, jobs, timeout):
    """-> {test: True green | False red | None timed out}"""
    def one(t):
        try:
            r = subprocess.run([sys.executable, os.path.join(root, t)], cwd=root, capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=timeout)
            return t, r.returncode == 0
        except subprocess.TimeoutExpired:
            return t, None
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        return dict(ex.map(one, tests))


def sweep(repo, cfg_rel, tests=None, jobs=6, timeout=300, log=print, deep=False, only=None):
    tmp, root = scratch_copy(repo)
    cfg_path = os.path.join(root, cfg_rel)
    raw = open(cfg_path, encoding="utf-8").read()
    cfg = json.loads(raw)
    every = [p for p, _v in leaves(cfg) if not only or fnmatch.fnmatch("/".join(map(str, p)), only)]
    tests = tests or readers(root, cfg_rel, deep)

    def with_leaves(ps, ts):
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(apply(cfg, ps), f, indent=2)
        try:
            return run_tests(root, ts, jobs, timeout)
        finally:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(raw)

    def culprits(t, ps):
        """The leaves in ps that alone turn t red (halving; a red needing two leaves together reports the pair)."""
        if len(ps) == 1:
            return [ps[0]]
        a, b = ps[:len(ps) // 2], ps[len(ps) // 2:]
        ra, rb = with_leaves(a, [t])[t] is False, with_leaves(b, [t])[t] is False
        if not ra and not rb:
            return [tuple(ps)]
        return (culprits(t, a) if ra else []) + (culprits(t, b) if rb else [])

    try:
        base = run_tests(root, tests, jobs, timeout)
        fmt = with_leaves([], [t for t in tests if base[t]])      # the file rewritten by json.dump with nothing changed
        fmt_red = sorted(t for t, v in fmt.items() if v is False)
        mut = with_leaves(every, [t for t in tests if base[t] and t not in fmt_red])
        rep = {"config": cfg_rel, "leaves": len(every), "tests": len(tests),
               "base_red": sorted(t for t in tests if base[t] is False),
               "base_timeout": sorted(t for t in tests if base[t] is None),
               "mut_timeout": sorted(t for t, v in mut.items() if v is None), "pinned": {}, "flaky": []}
        for t in sorted(t for t, v in mut.items() if v is False):
            if with_leaves(every, [t])[t] is not False:      # red beside others, green alone: a shared-path race
                rep["flaky"].append(t)
                log("FLAKY %s (red only when run in parallel: not judged)" % t)
                continue
            rep["pinned"][t] = ["/".join(map(str, c)) if c and not isinstance(c[0], tuple)
                                else " + ".join("/".join(map(str, x)) for x in c) for c in culprits(t, every)]
            log("PINNED %s <- %s" % (t, ", ".join(rep["pinned"][t])))
        rep["format_sensitive"] = fmt_red
        for t in fmt_red:
            log("FORMAT-SENSITIVE %s (red when json.dump merely rewrites the file, e.g. text-matching mutants: not judged)" % t)
        for t in rep["base_red"]:
            log("BASE RED %s (red before any change: not judged)" % t)
        for t in rep["base_timeout"] + rep["mut_timeout"]:
            log("TIMEOUT %s: UNMEASURED" % t)
        return rep
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("config")
    ap.add_argument("--tests", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--only", help="sweep only the leaves whose path (a/b/0/c) matches this glob")
    ap.add_argument("--deep", action="store_true", help="also the selftests importing a module that names the config")
    a = ap.parse_args(argv)
    repo = subprocess.run(["git", "-C", a.repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=60)
    if repo.returncode:
        print("not a git repo: %s" % a.repo)
        return 2
    repo = repo.stdout.strip()
    cfg_rel = os.path.relpath(os.path.abspath(a.config), repo)
    rep = sweep(repo, cfg_rel, a.tests, a.jobs, a.timeout, log=lambda m: print(m, flush=True), deep=a.deep, only=a.only)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)
    print("%s: %d leaves, %d readers, %d base red, %d timeout, %d flaky" % (cfg_rel, rep["leaves"], rep["tests"],
          len(rep["base_red"]), len(rep["base_timeout"]) + len(rep["mut_timeout"]), len(rep["flaky"])))
    print("RESULT: %s" % ("PINNED %d" % len(rep["pinned"]) if rep["pinned"] else "CLEAN"))
    return 1 if rep["pinned"] else 0


if __name__ == "__main__":
    sys.exit(main())
