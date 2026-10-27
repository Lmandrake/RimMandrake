#!/usr/bin/env python3
"""selftest_contracts -- the contracts package (CONTRACTS_BUILD_COMMON_READER_FIVE_RECORDS).

  C1  jsonl.decode never raises and every line lands as exactly one Row or Fault (fixtures + hostile lines)
  C2  the fixture corpus: old / new / strict decisions per line equal expected.json; every old/new difference is a
      row the manifest marks DISAGREEMENT (intended)          [needs git history: the old readers come from BASE]
  C3  AuditRecord == audits.schema.json, keyword by keyword (required, enums, pattern, types)
  C4  audits.problems() (now the model) decides like the old interpreter at BASE on 3000 mutated records
  C5  the exported Arbiter schema files are current (export.py --check)
  C6  the stdlib layers import no pydantic; the hot readers (close_evidence, dispatcher, arbiter_pending) neither
  C7  close_evidence_kind on a v4 line never mutates the dict (the mac is over the raw dict)

Without pydantic every check prints the UNMEASURED phrase instead of passing or failing.
"""
import copy
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
if RM not in sys.path:
    sys.path.insert(0, RM)
UNMEASURED_PHRASE = "UNMEASURED, not a pass or a fail"
fails = []
n_ok = 0


def check(name, cond, detail=""):
    global n_ok
    if cond:
        n_ok += 1
    else:
        fails.append(name)
        print("FAIL %s %s" % (name, detail))


def no_pydantic_after(code):
    r = subprocess.run([sys.executable, "-c", code + "\nimport sys; print('pydantic' in sys.modules)"],
                       capture_output=True, text=True, timeout=60, cwd=RM)
    return r.returncode == 0 and r.stdout.strip().endswith("False"), (r.stdout + r.stderr)[-300:]


def main():
    try:
        import pydantic  # noqa: F401
    except ImportError:
        print("pydantic missing (pip install --user -r src/RimMandrake/contracts/requirements.lock): " +
              UNMEASURED_PHRASE)
        return 0
    from contracts import jsonl as CJ, models as CM, replay as RP, export as EX
    from contracts.fixtures import make_fixtures as FX

    # C1
    hostile = ["", "  ", "{", "[1]", "null", "1e999", '{"a": NaN}', '{"a":1,"a":2}', "\ufffd", "\x00", FX.DEEP_LINE,
               b"\xff\xfe{}", '{"x": "' + "y" * 100000 + '"}']
    lines = hostile + [ln for fam in RP.FAMILIES for ln, _ in FX.load(fam)]
    raised = 0
    for strict in (False, True):
        for i, ln in enumerate(lines):
            try:
                r = CJ.decode(ln, i, strict=strict)
                check("C1 one outcome", (r.ok and hasattr(r, "value")) or (not r.ok and r.code), repr(ln)[:60])
            except BaseException:  # noqa: BLE001
                raised += 1
    check("C1 decode never raises", raised == 0, "%d raised" % raised)
    rows, faults = CJ.scan(hostile)
    check("C1 scan accounts every line", len(rows) + len(faults) == len(hostile))
    check("C1 deep is too_deep", CJ.decode(FX.DEEP_LINE).code == CJ.TOO_DEEP)
    check("C1 dup_key strict only", CJ.decode('{"a":1,"a":2}').ok and CJ.decode('{"a":1,"a":2}', strict=True).code
          == CJ.DUP_KEY)

    # C2
    import tempfile
    have_git = subprocess.run(["git", "-C", RP.REPO, "cat-file", "-e", RP.BASE + "^{commit}"],
                              capture_output=True).returncode == 0
    if not have_git:
        print("C2 base commit %s absent from this clone: %s" % (RP.BASE, UNMEASURED_PHRASE))
    else:
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(1000)
        try:
            with tempfile.TemporaryDirectory(prefix="selftest_contracts_") as tmp:
                rep = RP.run_fixtures(RP.Readers(RP.BASE, tmp))
        finally:
            sys.setrecursionlimit(old_limit)
        check("C2 fixture lines", rep["lines"] >= 70, rep["lines"])
        check("C2 expectations", not rep["expectation_misses"], rep["expectation_misses"][:3])
        check("C2 every old/new diff intended", not rep["unexplained"],
              [(d["family"], d["class"]) for d in rep["unexplained"]])
        check("C2 some diffs exist (instrument sees)", len(rep["old_new_diffs"]) >= 5, len(rep["old_new_diffs"]))

    # C3
    import audits
    sch = audits.schema()
    fields = CM.AuditRecord.model_fields
    req = sorted(k for k, f in fields.items() if f.is_required())
    check("C3 required", req == sorted(sch["required"]), (req, sch["required"]))
    check("C3 properties", sorted(fields) == sorted(sch["properties"]), sorted(set(fields) ^ set(sch["properties"])))
    for k in ("why_picked", "verdict"):
        lit = fields[k].annotation.__args__
        check("C3 enum " + k, list(lit) == sch["properties"][k]["enum"], (lit, sch["properties"][k]["enum"]))
    check("C3 sha pattern", sch["properties"]["sha"]["pattern"] == CM.HEX7_40)

    # C4
    old = RP.load_module("old_audits_st", RP.REL["audits"], RP.BASE) if have_git else None
    if old is None:
        print("C4 needs the base commit: " + UNMEASURED_PHRASE)
    else:
        rng = random.Random(4)
        base = {"ts": "2026-10-27T00:00:00Z", "item": "X_Y_Z", "sha": "abcdef1", "run": "r1", "why_picked": "rank",
                "flags": [], "verdict": "SOUND", "defect_class": None, "evidence": ["D:\\a"]}
        vals = [None, "", "x", "DEFECT", "UNRESOLVED", "SOUND", "abcdef1\n", "ABCDEF1", 0, 1.5, True, [], ["a"], [1],
                {}, "random", "mandatory"]
        differ, refused = 0, 0
        for _ in range(3000):
            d = copy.deepcopy(base)
            for _k in range(rng.randrange(1, 4)):
                key = rng.choice(sorted(base) + ["waiting_for", "extra"])
                if rng.random() < 0.15:
                    d.pop(key, None)
                else:
                    d[key] = rng.choice(vals)
            refused += bool(audits.problems(d))
            if bool(old.problems(d)) != bool(audits.problems(d)):
                differ += 1
                if differ <= 3:
                    print("  C4 differ:", json.dumps(d), old.problems(d), audits.problems(d))
        check("C4 audits decision unchanged", differ == 0, "%d of 3000 differ" % differ)
        check("C4 the mutations both pass and fail (instrument sees)", 100 < refused < 2900, refused)

    # C5
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        rc = EX.main(["--check"])
    check("C5 exported schemas current", rc == 0)

    # C6
    for code in ("from contracts import jsonl, compat",
                 "import sys; sys.path.insert(0, 'Utils'); import close_evidence",
                 "import sys; sys.path.insert(0, 'rimflow'); import arbiter_pending",
                 "import sys; sys.path.insert(0, 'rimflow'); import dispatcher"):
        ok, out = no_pydantic_after(code)
        check("C6 no pydantic: " + code.split(";")[-1].strip(), ok, out)

    # C7
    ev = [json.loads(ln) for ln, e in FX.load("close_evidence") if e["class"] in ("valid_v4", "valid_v4_fail")]
    check("C7 has a v4 fixture", bool(ev))
    for d in ev:
        before = json.dumps(d, sort_keys=True)
        kind, _ = CM.close_evidence_kind(d)
        check("C7 kind v4", kind == "v4", kind)
        check("C7 dict unchanged", json.dumps(d, sort_keys=True) == before)

    print("selftest_contracts: %d ok, %d fail%s" % (n_ok, len(fails), "" if fails else " -- ALL PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
