#!/usr/bin/env python3
"""Relentless building Relentless, in stages (SELFBUILD_DESIGN_STAGE_ZERO_KEEPS_KEYS).

Design: design/RimMandrake/relentless_selfbuild_2026-11-06.md. A frozen stage 0 builds a stage 1 candidate; the
candidate replaces stage 0 only through the gates below, each a program, never a prompt word (survey rule 1,
design/RimMandrake/builder_agents_survey_2026-11-02.md):

    protected  a candidate diff touching a grader part (relentless_selfbuild.json: Judge, Marker, wall, seeds/E1,
               counting rules, their checks, and every local module a protected .py imports, transitively) is refused
    ready      the builder wall exists and denies the seed keys and the store; until it does, no self-build starts
    promote    stage 1 swaps in only if pass^k (passed on EVERY repeat) on each frozen set is >= stage 0's, on the
               same frozen case list, k >= min_repeats, and its diff passed `protected`
    draw       the replay sample for a cross-built Judge: stratified by (outcome, leaf class), seeded, token-sized
               (owner 2026-11-02: "We are not going to spend much on pulsing known work. It's just to show some
               skill."), fixed before the build; rows authored by the building instance are dropped
    cross      a Judge built by instance A for B: no label, held-out case or mutant authored by A; at least one
               known-good that must PASS and one mutant that must FAIL; the replays equal `draw` of the recorded seed

Exit: 0 pass, 1 refused, 2 UNMEASURED (could not ask). Every refusal prints one reason per line.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import posixpath
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SPEC = HERE / "relentless_selfbuild.json"


class Unmeasured(Exception):
    pass


def load(path=SPEC):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- protected

def _imports(src):
    """Dotted module names a Python source imports, at any depth (a function-local import counts). `from a import b`
    yields both `a` and `a.b`, since b may be a submodule; a name that resolves to no file is simply not followed."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            out.add(n.module)
            out.update(f"{n.module}.{a.name}" for a in n.names if a.name != "*")
        elif isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", "")) in ("import_module", "__import__"):
            if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                out.add(n.args[0].value)
    return out


def protected_set(spec, read):
    """{repo path: why} for the list plus the transitive local imports of every protected .py.
    read(path) -> text or None, so the closure is taken at a given sha, not the working tree."""
    roots = spec.get("import_roots", [])
    out = {}
    todo = []
    for e in spec.get("protected", []):
        out[e["path"]] = e["part"]
        todo.append(e["path"])
    for e in spec.get("protected_keys", []):
        todo.append(e["path"])  # its keys are compared; a .json imports nothing
    seen = set()
    while todo:
        p = todo.pop()
        if p in seen or not p.endswith(".py"):
            continue
        seen.add(p)
        text = read(p)
        if text is None:
            continue
        here = posixpath.dirname(p)
        mods = set()
        for m in _imports(text):
            parts = m.split(".")
            mods.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
        for mod in sorted(mods):
            rel = mod.replace(".", "/")
            for d in [here] + roots:
                for cand in (posixpath.join(d, rel + ".py"), posixpath.join(d, rel, "__init__.py")):
                    if read(cand) is not None:
                        if cand not in out:
                            out[cand] = f"imported by {p}"
                            todo.append(cand)
                        break
                else:
                    continue
                break
    return out


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        raise Unmeasured(f"git {' '.join(args)}: timed out after 120 s") from None
    if r.returncode:
        raise Unmeasured(f"git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r.stdout


def _reader(root, sha):
    cache = {}

    def read(p):
        if p not in cache:
            try:
                r = subprocess.run(["git", "-C", str(root), "show", f"{sha}:{p}"],
                                   capture_output=True, text=True, timeout=60)
            except subprocess.TimeoutExpired:
                raise Unmeasured(f"git show {sha}:{p}: timed out after 60 s") from None
            cache[p] = r.stdout if r.returncode == 0 else None
        return cache[p]
    return read


def violations(spec, changed, read_base, read_head):
    """Reasons a candidate (base -> head, `changed` paths) touches a grader part. The closure is taken at BOTH
    ends, so a new import that drags a protected module in, or one that drops it, is seen either way."""
    prot = protected_set(spec, read_base)
    prot.update({k: v for k, v in protected_set(spec, read_head).items() if k not in prot})
    pats = [e["path"] for e in spec.get("protected", []) if any(c in e["path"] for c in "*?[")]
    out = []
    keyed = {e["path"]: e for e in spec.get("protected_keys", [])}
    for p in sorted(set(changed)):
        if p in prot:
            out.append(f"{p}: protected ({prot[p]})")
        elif any(fnmatch.fnmatch(p, g) for g in pats):
            out.append(f"{p}: protected (pattern)")
        elif p in keyed:
            e = keyed[p]
            try:
                a = json.loads(read_base(p) or "{}")
                b = json.loads(read_head(p) or "{}")
            except ValueError:
                out.append(f"{p}: protected keys unreadable as JSON")
                continue
            for k in e["keys"]:
                if a.get(k) != b.get(k):
                    out.append(f"{p}: protected key {k!r} changed ({e['part']})")
    return out


SPEC_REL = "src/RimMandrake/rimflow/relentless_selfbuild.json"


def check_protected(root, base, head, spec=None):
    """The list is read AT THE BASE sha, never from the candidate: a candidate that edits the list it is checked
    against would otherwise check itself. (The supervisor also runs stage 0's copy of this program, not the
    candidate's.) A base with no list is UNMEASURED."""
    changed = [ln for ln in _git(root, "-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", base, head).splitlines() if ln]
    rb = _reader(root, base)
    if spec is None:
        text = rb(SPEC_REL)
        if text is None:
            raise Unmeasured(f"no {SPEC_REL} at base {base}")
        spec = json.loads(text)
    return violations(spec, changed, rb, _reader(root, head))


# ---------------------------------------------------------------- ready

def ready(spec, rules):
    """Reasons a self-build may not start yet: the builder wall must exist, be enforced and deny every outside part."""
    w = (rules.get("walls") or {}).get(spec.get("build_wall", "builder"))
    if not isinstance(w, dict):
        return [f"no walls.{spec.get('build_wall', 'builder')} profile in relentless_rules.json: the builder can read the keys"]
    out = []
    if not w.get("enforce"):
        out.append(f"walls.{spec.get('build_wall')} is not enforced")
    deny = list(w.get("deny") or []) + list(w.get("deny_children") or []) + list(w.get("never_through") or [])
    for e in spec.get("outside", []):
        p = os.environ.get(e["env"], e["path"]) if e.get("env") else e["path"]
        if not any(p == d or p.startswith(d.rstrip("/") + "/") for d in deny):
            out.append(f"{p}: {e['part']} not denied by the builder wall")
    return out


# ---------------------------------------------------------------- promote

def manifest_hash(case_ids):
    return hashlib.sha256("\n".join(sorted(case_ids)).encode()).hexdigest()[:16]


def pass_k(runs):
    """runs: list of repeats, each {case_id: True/False}. A case counts only if it passed on every repeat."""
    if not runs:
        return 0, 0
    cases = set(runs[0])
    return sum(all(r.get(c) is True for r in runs) for c in cases), len(cases)


def promote(spec, doc):
    """doc: {"frozen": {set: hash}, "protected_ok": bool, "stage0": {set: [repeat...]}, "stage1": {...}}.
    Returns (swap, reasons). Ties swap (>=, the item's words); any missing piece refuses."""
    pr = spec["promotion"]
    why = []
    if doc.get("protected_ok") is not True:
        why.append("candidate diff has not passed the protected check")
    for s in pr["sets"]:
        a, b = (doc.get("stage0") or {}).get(s), (doc.get("stage1") or {}).get(s)
        if not a or not b:
            why.append(f"{s}: missing runs for a stage")
            continue
        if len(a) < pr["min_repeats"] or len(b) < pr["min_repeats"]:
            why.append(f"{s}: fewer than {pr['min_repeats']} repeats")
            continue
        ids = {frozenset(r) for r in a + b}
        if len(ids) != 1:
            why.append(f"{s}: the stages ran different case lists")
            continue
        h = manifest_hash(next(iter(ids)))
        if (doc.get("frozen") or {}).get(s) != h:
            why.append(f"{s}: case list {h} is not the frozen one {(doc.get('frozen') or {}).get(s)}")
            continue
        (k0, n), (k1, _) = pass_k(a), pass_k(b)
        if k1 < k0:
            why.append(f"{s}: stage 1 pass^{min(len(a), len(b))} {k1}/{n} < stage 0 {k0}/{n}")
    return not why, why


# ---------------------------------------------------------------- draw and cross

def draw(spec, pool, seed, builder, n=None):
    """Stratified, seeded replay sample. pool rows: {id, outcome, leaf_class, author}. Round-robin over strata in a
    seeded order, so every (outcome, class) present is drawn once before any is drawn twice."""
    rp = spec["replay"]
    n = min(n or rp["token_max"], rp["token_max"])
    rng = random.Random(seed)
    strata = {}
    for r in sorted(pool, key=lambda r: r["id"]):
        if r.get("author") == builder:
            continue
        strata.setdefault((r["outcome"], r["leaf_class"]), []).append(r)
    keys = sorted(strata)
    rng.shuffle(keys)
    for k in keys:
        rng.shuffle(strata[k])
    out = []
    while len(out) < n and any(strata[k] for k in keys):
        for k in keys:
            if strata[k] and len(out) < n:
                out.append(strata[k].pop())
    return [r["id"] for r in out]


def cross(spec, doc):
    """doc: {builder, target, labels:[{case,label,author}], held_out:[{case,author}], mutants:[{case,author}],
    pool:[...], seed, replays:[ids]}. Returns reasons to refuse."""
    a = doc.get("builder")
    why = []
    if not a or a == doc.get("target"):
        why.append("builder and target instance must both be named and differ")
    for part in ("labels", "held_out", "mutants"):
        for r in doc.get(part) or []:
            if not r.get("author"):
                why.append(f"{part} {r.get('case')}: no author recorded")
            elif r["author"] == a:
                why.append(f"{part} {r.get('case')}: authored by the building instance {a}")
    labels = doc.get("labels") or []
    labelled = {r.get("case") for r in labels}
    if not any(r.get("label") == "PASS" for r in labels):
        why.append("no known-good case the Judge must PASS")
    if not any(r.get("label") == "FAIL" for r in labels) and not doc.get("mutants"):
        why.append("no mutant or known fault the Judge must FAIL")
    want = draw(spec, doc.get("pool") or [], doc.get("seed"), a) if doc.get("seed") else None
    if want is None:
        why.append("no draw seed recorded before the build")
    elif list(doc.get("replays") or []) != want:
        why.append(f"replays are not the seeded draw (picked {doc.get('replays')}, draw gives {want})")
    elif len(want) < spec["replay"]["token_min"]:
        why.append(f"draw gives {len(want)} replays, fewer than {spec['replay']['token_min']}")
    else:
        why.extend(f"replay {c}: no known outcome among the labels" for c in want if c not in labelled)
    return why


# ---------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("protected", help="refuse a base..head diff touching a grader part")
    p.add_argument("--base", required=True)
    p.add_argument("--head", default="HEAD")
    p.add_argument("--root", default=str(REPO))
    p.add_argument("--list", action="store_true", help="print the protected set at head and exit")
    sub.add_parser("ready", help="may a self-build start? (the builder wall)")
    for name in ("promote", "cross"):
        q = sub.add_parser(name)
        q.add_argument("file")
    q = sub.add_parser("draw")
    q.add_argument("pool")
    q.add_argument("--seed", required=True)
    q.add_argument("--builder", required=True)
    q.add_argument("--n", type=int)
    a = ap.parse_args(argv)
    spec = load()
    try:
        if a.cmd == "protected":
            if a.list:
                for k, v in sorted(protected_set(spec, _reader(a.root, a.head)).items()):
                    print(f"{k}\t{v}")
                return 0
            why = check_protected(a.root, a.base, a.head, spec)
        elif a.cmd == "ready":
            why = ready(spec, json.loads((HERE / "relentless_rules.json").read_text(encoding="utf-8")))
        elif a.cmd == "promote":
            ok, why = promote(spec, json.loads(Path(a.file).read_text(encoding="utf-8")))
        elif a.cmd == "cross":
            why = cross(spec, json.loads(Path(a.file).read_text(encoding="utf-8")))
        else:
            print(json.dumps(draw(spec, json.loads(Path(a.pool).read_text(encoding="utf-8")), a.seed, a.builder, a.n)))
            return 0
    except (Unmeasured, OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        print(f"UNMEASURED: {e}")
        return 2
    for w in why:
        print("REFUSED " + w)
    print("PASS" if not why else f"REFUSED {len(why)} reason(s)")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
