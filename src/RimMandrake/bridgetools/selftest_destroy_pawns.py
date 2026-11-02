#!/usr/bin/env python3
"""selftest_destroy_pawns.py - jawa/destroy_batch never removes pawns, and the callers that need pawns gone say so.

JAWABENCH_DESTROY_PAWNS_1 (fix landed as DESTROY_BATCH_NEVER_KILLS_PAWNS_1). LIVE 2026-10-07: destroy_batch answered
"1 pawn(s) left alone" on every categories=Pawn call, so Greentide _clear_hostiles and Cauldron kill_pawns removed
nothing and a hostile Megascarab wounded Greentide's rescue helper. Offline clauses:

A1  the companion source refuses a categories list holding 'Pawn' (before the destroy loop) and still skips pawns
    inside the loop for categories=All;
A2  Greentide _clear_hostiles and Cauldron _kill_pawns_in remove each pawn BY ID through
    jawa/pawn_force_incapacitate action=vanish, never destroy_batch -- driven against a fake bridge;
A4  no Python caller under src/ (selftests and the A3 live proof excepted: they ask to
    see the refusal) asks destroy_batch for Pawn
    (AST scan of LITERAL tool names and category strings -- a category held in a variable is not seen;
    calibrated on planted bad calls).
A3 (the running DLL refuses, a spawned hostile is really gone) is prove_destroy_pawns_live.py.
"""
import ast
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))          # src/
RM = os.path.join(SRC, "RimMandrake")
fails, ran = [], [0]


def check(name, ok, detail=""):
    ran[0] += 1
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)[:400]))
    if not ok:
        fails.append(name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- A1: the C# refusal
cs = open(os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchTerrainTools.cs"), encoding="utf-8").read()
m = re.search(r"public static async Task<object> DestroyBatch\((.*?)\n        \}\n", cs, re.S)
check("A1 DestroyBatch method found", m is not None)
body = m.group(1) if m else ""
refuse = re.search(r'if \(wanted\.Contains\("Pawn"\)\)\s*return Fail\(', body)
loop = body.find("foreach")
check("A1 categories containing Pawn is refused with Fail", refuse is not None)
check("A1 the refusal comes before the destroy loop", refuse is not None and loop > 0 and refuse.start() < loop,
      (refuse and refuse.start(), loop))
check("A1 wanted is case-insensitive (pawn/PAWN refused too)",
      re.search(r"var wanted = new HashSet<string>\([\s\S]{0,300}StringComparer\.OrdinalIgnoreCase", body) is not None)
check("A1 categories=All still skips pawns in the loop",
      re.search(r"if \(thing is Pawn[^)]*\) \{ skippedPawns\+\+; continue; \}", body) is not None)


# ---------------------------------------------------------------- A2: the two callers, on a fake bridge
PAWNS = [
    {"id": "Megascarab1", "hostile": True, "spawned": True, "x": 10, "z": 12, "dead": False},
    {"id": "Helper2", "hostile": False, "spawned": True, "x": 11, "z": 12, "dead": False},
    {"id": "Gone3", "hostile": True, "spawned": False, "x": -1, "z": -1, "dead": False},
    {"id": "Corpse4", "hostile": True, "spawned": True, "x": 9, "z": 9, "dead": True},
    {"id": "Bystander5", "hostile": False, "spawned": True, "x": 8, "z": 8, "dead": False},
]


class FakeT:
    def __init__(self, vanish_ok=True):
        self.calls = []
        self.vanish_ok = vanish_ok
        self.anchor = (10, 10)
        self._bystanders = {"Bystander5"}
        self.session = self

    def call(self, tool, **kw):          # t.session.call (raw)
        return self.bridge_call(tool, **kw)

    def bridge_call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"pawns": [dict(p) for p in PAWNS]}
        if tool == "jawa/pawn_force_incapacitate":
            return {"success": True, "destroyedAfter": self.vanish_ok}
        return {"success": True}

    def tools(self, name):
        return [kw for t, kw in self.calls if t == name]


gt = load("gt_validation", os.path.join(RM, "Greentide", "validation.py"))
check("A2 Greentide _clear_hostiles importable", hasattr(gt, "_clear_hostiles"),
      "modcheck Suite not importable? the suite body did not run")
if hasattr(gt, "_clear_hostiles"):
    t = FakeT()
    gt._clear_hostiles(t)
    v = t.tools("jawa/pawn_force_incapacitate")
    check("A2 Greentide vanishes exactly the spawned living hostile, by id",
          [(k.get("pawn"), k.get("action")) for k in v] == [("Megascarab1", "vanish")], v)
    check("A2 Greentide never calls destroy_batch", not t.tools("jawa/destroy_batch"), t.calls)

ca = load("ca_validation", os.path.join(RM, "Cauldron", "validation.py"))
check("A2 Cauldron _kill_pawns_in importable", hasattr(ca, "_kill_pawns_in"))
if hasattr(ca, "_kill_pawns_in"):
    for raw in (False, True):
        t = FakeT()
        n = ca._kill_pawns_in(t, (0, 0, 20, 20), raw=raw)
        v = t.tools("jawa/pawn_force_incapacitate")
        got = sorted((k.get("pawn"), k.get("action")) for k in v)
        want = sorted((p, "vanish") for p in ("Megascarab1", "Helper2", "Gone3"))
        check("A2 Cauldron (raw=%s) vanishes every living non-bystander by id" % raw, got == want and n == 3, (n, got))
        check("A2 Cauldron (raw=%s) never calls destroy_batch" % raw, not t.tools("jawa/destroy_batch"), t.calls)
        check("A2 Cauldron (raw=%s) no bullet fallback when the vanish reads back" % raw,
              not t.tools("jawa/damage"), t.tools("jawa/damage"))
    t = FakeT(vanish_ok=False)
    ca._kill_pawns_in(t, (0, 0, 20, 20))
    check("A2 Cauldron falls back to a bullet when the vanish does not read back",
          len(t.tools("jawa/damage")) == 3, t.tools("jawa/damage"))


# ---------------------------------------------------------------- A4: no caller asks destroy_batch for Pawn
def pawn_asks(tree):
    """Calls whose args name 'jawa/destroy_batch' and carry a category(ies) string holding the token Pawn."""
    hits = []
    tok = re.compile(r"(?i)(^|[,\s])pawn($|[,\s])")
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not any(isinstance(a, ast.Constant) and a.value == "jawa/destroy_batch" for a in node.args):
            continue
        vals = [k.value for k in node.keywords if k.arg in ("category", "categories")]
        for a in node.args:
            if isinstance(a, ast.Dict):
                vals += [v for k, v in zip(a.keys, a.values)
                         if isinstance(k, ast.Constant) and k.value in ("category", "categories")]
        for v in vals:
            if isinstance(v, ast.Constant) and isinstance(v.value, str) and tok.search(v.value):
                hits.append(node.lineno)
    return hits


planted = ast.parse('c.call("jawa/destroy_batch", rects="0,0,1,1", categories="Item,Pawn")\n'
                    'rb.call("jawa/destroy_batch", {"rects": "0,0,1,1", "category": "pawn"})\n'
                    'c.call("jawa/destroy_batch", rects="0,0,1,1", categories="All")\n')
check("A4 calibration: the scan sees both planted Pawn asks and not the All one", pawn_asks(planted) == [1, 2],
      pawn_asks(planted))
bad, scanned = [], 0
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in (".git", "artifacts", "bin", "obj", "__pycache__")]
    for f in files:
        # selftests and the A3 live proof ask on purpose, to see the refusal
        if not f.endswith(".py") or f.startswith("selftest") or f == "prove_destroy_pawns_live.py":
            continue
        p = os.path.join(root, f)
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "jawa/destroy_batch" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        scanned += 1
        bad += ["%s:%d" % (os.path.relpath(p, SRC), ln) for ln in pawn_asks(tree)]
check("A4 the scan read destroy_batch callers (sanity: more than a handful)", scanned >= 10, scanned)
check("A4 no src caller asks destroy_batch for Pawn", not bad, bad)

print("%d checks, %d failed" % (ran[0], len(fails)))
sys.exit(1 if fails else 0)
