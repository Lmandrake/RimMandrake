#!/usr/bin/env python3
"""Class guard: the sparse deploy checkout (pulse.SPARSE_DIRS) holds every repo module the deploy's units reach
(PULSEDEPLOY_FIX_SPARSE_LIST_FORGOT_CONTRACTS).

The instance: close_evidence.py (a Utils/ file, free in the cone) loads src/RimMandrake/contracts/jsonl.py BY PATH at
import time; SPARSE_DIRS omitted contracts, so in a sparse checkout the evidence family was UNMEASURED every pass with
FileNotFoundError. The class: a dir the deploy's code reaches that the cone does not hold.

Entry points: every `pulse-deploy/src/...py` an ExecStart in systemd/*.service names, plus ops_watch.py (the collector
the item caught blind). Walked statically (ast): `import X`, `from X import Y` (absolute), and a path load written as
`... / "<pkg dir>" / "<file>.py"`. Reads the repo only; touches no live state. In git's cone mode a file sitting
directly in an ancestor dir of a cone entry comes free (Utils/close_evidence.py, Utils/rmpaths.py).
"""
import ast
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
R = Path("src/RimMandrake")
sys.path.insert(0, str(HERE))
import pulse  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


# A package reached ONLY by an import inside a function that drives the live game; the deploy's units never call it.
# Every allowlisted hit is re-proved function-local below, so a module-level import of one still fails.
LAZY_OK = {"src/RimMandrake/Utils/rimdrive": "live-game driver: modcheck runner/scene_report import it inside live calls"}

CONE = tuple(pulse.SPARSE_DIRS)
SEARCH = [R / "Utils" / "pulse", R / "rimflow", R / "Utils", R] + [Path(c) for c in CONE]


def in_cone(rel: Path) -> bool:
    s, par = str(rel), str(rel.parent)
    return any(s.startswith(c + "/") for c in CONE) or any(c == par or c.startswith(par + "/") for c in CONE)


def resolve(mod: str, here: Path):
    parts = mod.split(".")
    for d in [here] + SEARCH:
        f = REPO / d.joinpath(*parts)
        for cand in (f.with_suffix(".py"), f / "__init__.py"):
            if cand.is_file():
                return cand.relative_to(REPO)
    return None


def pkg_dirs():
    """name -> rel dir, for every python package-ish dir under src/RimMandrake and src/RimMandrake/Utils."""
    out = {}
    for base in (R, R / "Utils"):
        for d in sorted((REPO / base).iterdir()):
            if d.is_dir() and any(d.glob("*.py")):
                out.setdefault(d.name, base / d.name)
    return out


def refs(tree):
    """-> [(module or rel path string, is_path_load, function_local)] for every reference in the module."""
    out = []
    local = set()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            for n in ast.walk(fn):
                local.add(id(n))
    for n in ast.walk(tree):
        loc = id(n) in local
        if isinstance(n, ast.Import):
            out += [(a.name, False, loc) for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out += [(n.module, False, loc)] + [(n.module + "." + a.name, False, loc) for a in n.names]
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            # `<expr> / "contracts" / "jsonl.py"` parses as ((expr / "contracts") / "jsonl.py")
            l, r = n.left, n.right
            if (isinstance(l, ast.BinOp) and isinstance(l.op, ast.Div) and isinstance(l.right, ast.Constant)
                    and isinstance(l.right.value, str) and isinstance(r, ast.Constant) and isinstance(r.value, str)
                    and r.value.endswith(".py")):
                out.append((l.right.value + "/" + r.value, True, loc))
    return out


def walk(entries):
    pk = pkg_dirs()
    seen, todo, outside = set(), list(entries), {}
    while todo:
        f = todo.pop()
        if f in seen or not (REPO / f).is_file():
            continue
        seen.add(f)
        for ref, is_path, loc in refs(ast.parse((REPO / f).read_text(encoding="utf-8"))):
            if is_path:
                d, name = ref.split("/", 1)
                t = (pk[d] / name) if d in pk and (REPO / pk[d] / name).is_file() else None
            else:
                t = resolve(ref, f.parent)
            if t is None:
                continue
            if not in_cone(t):
                outside.setdefault(t, []).append((f, loc))
            todo.append(t)
    return seen, outside


def entries():
    out = set()
    for u in sorted((REPO / R / "Utils" / "systemd").glob("*.service")):
        out.update(Path(m) for m in re.findall(r"pulse-deploy/(src/[^\s\"']+\.py)", u.read_text(encoding="utf-8")))
    return out


ENTRIES = entries()
check("the units name pulse-deploy entry points (instrument can see)", len(ENTRIES) >= 2, sorted(map(str, ENTRIES)))
ENTRIES.add(R / "Utils" / "ops_watch.py")
SEEN, OUTSIDE = walk(ENTRIES)
check("the walk reaches close_evidence.py from ops_watch.py (instrument can see)",
      R / "Utils" / "close_evidence.py" in SEEN, len(SEEN))
check("the walk sees close_evidence's path load of contracts/jsonl.py (instrument can see)",
      R / "contracts" / "jsonl.py" in SEEN or R / "contracts" / "jsonl.py" in OUTSIDE)
check("SPARSE_DIRS holds src/RimMandrake/contracts (the instance)", "src/RimMandrake/contracts" in CONE, CONE)

bad = {}
for t, by in OUTSIDE.items():
    lazy = next((k for k in LAZY_OK if str(t).startswith(k + "/")), None)
    if lazy and all(loc for _, loc in by):
        continue
    bad[str(t)] = sorted({str(f) + (" (in a function)" if loc else " (module level)") for f, loc in by})[:3]
check("every module the deploy's code reaches is inside the sparse cone", not bad,
      "; ".join(f"{k} <- {v}" for k, v in sorted(bad.items())))

# the guard must fail on the instance: drop contracts from the cone and re-walk
CONE = tuple(c for c in pulse.SPARSE_DIRS if c != "src/RimMandrake/contracts")
_, OUT2 = walk(ENTRIES)
check("without contracts in the cone the walk flags contracts/jsonl.py (guard bites)",
      any(str(t).startswith("src/RimMandrake/contracts/") for t in OUT2), sorted(map(str, OUT2)))

print("RESULT: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
