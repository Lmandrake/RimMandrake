#!/usr/bin/env python3
"""Guard: no live FOUNDRY seat literal in the code that used to route work to it (FOUNDRY_LITERALS_EXCISE_FROM_CODE).

FOUNDRY is retired (owner, by card 2026-11-02, "What should happen to FOUNDRY?" -> "Retire it"). A string literal
"FOUNDRY" in these files is a seat some program still names: a default, a view, a budget-less bucket, a foreign seat.
Comments and docstrings are history and stay. Deliberately NOT scanned: model.SEATS and cli.RETIRED_SEATS, which keep
FOUNDRY so the 2387 closed FOUNDRY items still replay from events/FOUNDRY.jsonl. The machine-total helper budget key
(slot_allocator, slot_rules.json, helper_budget, block_agent_over_slots) moved with its reader, relentless_rules
staffing.seat, to RELENTLESS: both ends are scanned here, so one cannot drift back alone.

    python3 src/RimMandrake/rimflow/selftest_foundry_literals.py
"""
import ast
import json
import os
import re
import sys

ROOT = os.environ.get("FOUNDRY_LITERALS_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))   # the override lets a reviewer point it at an older tree
PY = ["src/RimMandrake/Utils/ops_watch.py", "src/RimMandrake/Utils/l1_batch_manifest.py",
      "src/RimMandrake/Utils/install_wt_seat_profiles.py", "src/RimMandrake/Utils/ledger_sync.py",
      "src/RimMandrake/rimflow/detached_helper.py", "src/RimMandrake/rimflow/render.py",
      "src/RimMandrake/rimflow/relentless.py", "src/RimMandrake/Utils/slot_allocator.py",
      "src/RimMandrake/rimflow/helper_budget.py", ".claude/hooks/block_agent_over_slots.py"]
JSON = {"src/RimMandrake/Utils/ops_watch_rules.json": ("token_talk",),
        "src/RimMandrake/rimflow/relentless_rules.json": ("staffing",),
        "src/RimMandrake/Utils/slot_rules.json": ("seats", "enforce_seats", "fallback_n", "split")}
WORD = re.compile(r"\bFOUNDRY\b")

FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def docstring_ids(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            b = n.body[0]
            if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) and isinstance(b.value.value, str):
                out.add(id(b.value))
    return out


def live_literals(src):
    """-> [(line, text)] string literals (f-string parts included) naming FOUNDRY, docstrings excluded."""
    tree = ast.parse(src)
    docs = docstring_ids(tree)
    return [(n.lineno, n.value[:80]) for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs and WORD.search(n.value)]


def json_hits(node, path=""):
    """-> [path] of non-doc values (keys not starting '_') that name FOUNDRY."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if not str(k).startswith("_"):
                out += json_hits(v, path + "." + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += json_hits(v, "%s[%d]" % (path, i))
    elif isinstance(node, str) and WORD.search(node):
        out.append(path)
    return out


def main():
    # the instrument can see: a planted literal is caught, a docstring, comment and FOUNDRY_ item id are not
    probe = '"""FOUNDRY doc"""\nX = ("BENCH", "FOUNDRY")  # FOUNDRY comment\nY = f"to {1} FOUNDRY"\nZ = "FOUNDRY_OLD_ITEM"\n'
    got = live_literals(probe)
    check([ln for ln, _ in got] == [2, 3], "probe: planted literal and f-string part caught, doc/comment/item id not (%r)" % got)
    check(json_hits({"_doc": "FOUNDRY", "s": {"seat": "FOUNDRY", "l": ["A", "FOUNDRY"]}}, "") == [".s.seat", ".s.l[1]"],
          "probe: json value and list member caught, doc key not")
    for rel in PY:
        p = os.path.join(ROOT, rel)
        check(os.path.isfile(p), "%s exists (a vanished file proves nothing)" % rel)
        if os.path.isfile(p):
            hits = live_literals(open(p, encoding="utf-8").read())
            check(not hits, "%s: no live FOUNDRY literal %s" % (rel, hits[:5]))
    for rel, sections in JSON.items():
        d = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        for sec in sections:
            check(isinstance(d.get(sec), (dict, list)), "%s has section %s" % (rel, sec))
            hits = json_hits(d.get(sec), sec)
            check(not hits, "%s: no FOUNDRY value in %s %s" % (rel, sec, hits))
    # both ends of the budget key agree: Relentless reads its budget under the key the allocator places
    sys.path.insert(0, os.path.join(ROOT, "src/RimMandrake/Utils"))
    import slot_allocator as SA
    rr = json.load(open(os.path.join(ROOT, "src/RimMandrake/rimflow/relentless_rules.json"), encoding="utf-8"))
    sr = json.load(open(os.path.join(ROOT, "src/RimMandrake/Utils/slot_rules.json"), encoding="utf-8"))
    key = rr["staffing"]["seat"]
    check(key == SA.seat_label(SA.BUILDER) and SA.BUILDER in sr["seats"],
          "staffing.seat %r is the published name of the allocator's builder key %r, a placed seat" % (key, SA.BUILDER))
    per = SA.split_seats(7, sr["seats"], sr, "ELSEWHERE", "CRUISE")
    check(per.get(SA.BUILDER) == 7, "v3 split gives the builder key the whole machine total (%r)" % per)
    print("selftest_foundry_literals: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
