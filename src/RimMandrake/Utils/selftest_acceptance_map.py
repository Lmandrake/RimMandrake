#!/usr/bin/env python3
"""Selftest for acceptance_map: fabricated results prove the tool REFUSES to record FAIL,
UNMEASURED, UNMAPPED, already-passed and level-mismatched criteria, and records a clean PASS.
Each refusal is paired with a control (same fixture, taint removed) that DOES record, so a
rule that silently stops firing turns this red. Nothing here touches the real ledger: the
verify call is a stub; real result files are read only (and skipped if rotted away)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import acceptance_map as M  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class FakeItem:
    def __init__(self, state, crit, outstanding):
        self.state = state
        self.criteria = [{"id": i, "level": l, "text": "t"} for i, l in crit]
        self.outstanding = set(outstanding)


class FakeWorld:
    def __init__(self, items):
        self.items = items


def world():
    return FakeWorld({
        "FAKE_ITEM_1": FakeItem("built", [("A1", "L2"), ("A2", "L2"), ("A3", "L2"), ("A4", "GREEN-MIN"),
                                          ("A5", "L2"), ("A6", "L2"), ("A7", "L2")],
                                ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]),
        "DONE_ITEM_1": FakeItem("done", [("A1", "L2")], []),
    })


def result(comps, wrap=True):
    chains = {}
    for cid, v in comps.items():
        ch, c = cid.split("/")
        chains.setdefault(ch, []).append({"name": c, "verdict": v, "toggle": None, "evidence": []})
    d = {"chains": [{"name": k, "components": v} for k, v in chains.items()]}
    return {"mod": "Fake", "stamp": "x", "summary": d} if wrap else d


def row(criterion, comps, mode="all", level="L2", item="FAKE_ITEM_1", **kw):
    r = dict(item=item, criterion=criterion, level=level, components=comps, mode=mode,
             notes="fabricated for the selftest")
    r.update(kw)
    return r


with tempfile.TemporaryDirectory() as tmp:
    mdir = os.path.join(tmp, "map")
    os.makedirs(mdir)

    def write_table(rows, mod="Fake"):
        with open(os.path.join(mdir, mod + ".json"), "w") as fh:
            json.dump(rows, fh)

    def write_result(comps, name="r.json", wrap=True):
        p = os.path.join(tmp, name)
        with open(p, "w") as fh:
            json.dump(result(comps, wrap), fh)
        return p

    calls = []

    def stub(item, crit, level, config, evidence):
        calls.append((item, crit, level, config))
        return True, "ok"

    def apply(rows, comps, record=True, classified=None, w=None, wrap=True, mod=None):
        del calls[:]
        write_table(rows)
        return {(r["item"], r["criterion"]): r for r in M.run_apply(
            write_result(comps, wrap=wrap), "cfg", w or world(), mod=mod, classified=classified,
            record=record, map_dir=mdir, verify_fn=stub)}

    # ---- the core refusal: PASS records, FAIL and UNMEASURED never do
    rows = [row("A1", ["c/ok"]), row("A2", ["c/bad"]), row("A3", ["c/unk"]), row("A4", ["c/ok", "c/bad"], level="GREEN-MIN"),
            row("A5", ["c/ok", "c/unk"]), row("A6", ["c/absent"])]
    comps = {"c/ok": "PASS", "c/bad": "FAIL", "c/unk": "UNMEASURED"}
    r = apply(rows, comps)
    v = {k[1]: x["verdict"] for k, x in r.items()}
    check("pass-verdict", v["A1"] == "PASS", v)
    check("fail-verdict", v["A2"] == "FAIL" and v["A4"] == "FAIL", v)
    check("unmeasured-verdict", v["A3"] == "UNMEASURED" and v["A5"] == "UNMEASURED", v)
    check("absent-component-is-unmeasured", v["A6"] == "UNMEASURED", v)
    check("only the clean pass was recorded", calls == [("FAKE_ITEM_1", "A1", "L2", "cfg")], calls)
    check("fail-beats-unmeasured", M.evaluate(row("A1", ["c/bad", "c/unk"]), comps)[0] == "FAIL")
    check("dry run records nothing (control: same fixture records with --record)",
          (apply(rows, comps, record=False) and not calls), calls)
    check("nonstandard verdict is not a pass", M.load_result(write_result({"c/x": "SKIPPED"}))[1] == {"c/x": "UNMEASURED"})

    # ---- any mode
    check("any: one pass suffices", M.evaluate(row("A1", ["c/bad", "c/ok"], mode="any"), comps)[0] == "PASS")
    check("any: all fail is FAIL", M.evaluate(row("A1", ["c/bad"], mode="any"), comps)[0] == "FAIL")
    check("any: fail plus unknown is not FAIL", M.evaluate(row("A1", ["c/bad", "c/unk"], mode="any"), comps)[0] == "UNMEASURED")

    # ---- accept
    acc = row("A1", ["c/unk"], accept=["PASS", "UNMEASURED"])
    check("accept UNMEASURED passes when the wording allows it", M.evaluate(acc, comps)[0] == "PASS")
    check("accept never rescues a FAIL", M.evaluate(row("A1", ["c/bad", "c/unk"], accept=["PASS", "UNMEASURED"]), comps)[0] == "FAIL")
    check("schema refuses accept containing FAIL", bool(M.row_schema_problems(row("A1", ["c/ok"], accept=["PASS", "FAIL"]))))
    check("a pass is not defaulted from UNMEASURED (control for accept)", M.evaluate(row("A1", ["c/unk"]), comps)[0] == "UNMEASURED")

    # ---- @run
    check("@run passes on a non-empty run", M.evaluate(row("A1", ["@run"]), comps)[0] == "PASS")
    check("@run is UNMEASURED on an empty run", M.evaluate(row("A1", ["@run"]), {})[0] == "UNMEASURED")

    # ---- classified
    crow = row("A1", ["*"], mode="classified")
    check("classified: no non-pass -> PASS", M.evaluate(crow, {"c/ok": "PASS"})[0] == "PASS")
    check("classified: non-pass without a file -> UNMEASURED", M.evaluate(crow, comps)[0] == "UNMEASURED")
    check("classified: partial classification -> UNMEASURED",
          M.evaluate(crow, comps, {"c/bad": "mod: real bug"})[0] == "UNMEASURED")
    check("classified: bad class label does not count",
          M.evaluate(crow, comps, {"c/bad": "whatever", "c/unk": "harness: x"})[0] == "UNMEASURED")
    check("classified: full classification -> PASS (control)",
          M.evaluate(crow, comps, {"c/bad": "mod: real bug", "c/unk": "unmeasured: no tool"})[0] == "PASS")

    # ---- unmapped, ledger state, level
    um = row("A7", [], mode="unmapped")
    r = apply([um], comps)
    check("unmapped row is reported UNMAPPED and never recorded", r[("FAKE_ITEM_1", "A7")]["verdict"] == "UNMAPPED" and not calls)
    r = apply([row("A1", ["c/ok"], item="DONE_ITEM_1")], comps)
    check("already-passed criterion is not re-recorded", not calls and "skip" in r[("DONE_ITEM_1", "A1")]["action"], r)
    r = apply([row("A1", ["c/ok"], level="L1")], comps)
    check("level mismatch with the ledger is not recorded", not calls and r[("FAKE_ITEM_1", "A1")]["ledger"] == "LEVEL-MISMATCH", r)
    r = apply([row("A1", ["c/ok"], item="NOPE_ITEM_1")], comps)
    check("unknown item is not recorded", not calls and r[("NOPE_ITEM_1", "A1")]["ledger"] == "NO-ITEM")
    r = apply([row("A1", ["c/ok"])], comps)
    check("control: the same row with a clean ledger records", len(calls) == 1)
    r = apply([row("A1", ["c/ok"])], comps)
    check("NOT-IN-TABLE lists outstanding criteria without rows",
          {k[1] for k, x in r.items() if x["verdict"] == "NOT-IN-TABLE"} == {"A2", "A3", "A4", "A5", "A6", "A7"})
    check("l2sweep-shaped (unwrapped) result is read", ("FAKE_ITEM_1", "A1") in apply([row("A1", ["c/ok"])], comps, wrap=False, mod="Fake"))

    # ---- check()
    good = [row("A1", ["c/ok"]), row("A7", [], mode="unmapped")]
    enum = lambda mod: {"c/ok", "c/bad", "c/unk"}  # noqa: E731
    write_table(good)
    check("check: sound table has no problems", M.check_tables(world(), mdir, ["Fake"], enum) == [])
    bad_cases = {
        "unknown component": [row("A1", ["c/typo"])],
        "unknown item": [row("A1", ["c/ok"], item="NOPE_ITEM_1")],
        "unknown criterion": [row("Z9", ["c/ok"])],
        "wrong level": [row("A1", ["c/ok"], level="L1")],
        "duplicate row": [row("A1", ["c/ok"]), row("A1", ["c/bad"])],
        "bad mode": [row("A1", ["c/ok"], mode="maybe")],
        "empty notes": [dict(row("A1", ["c/ok"]), notes=" ")],
        "unmapped with components": [row("A7", ["c/ok"], mode="unmapped")],
        "mapped without components": [row("A1", [])],
        "star outside classified": [row("A1", ["*"])],
        "unknown key": [dict(row("A1", ["c/ok"]), extra=1)],
        "bare component id": [row("A1", ["ok"])],
    }
    for name, rows_ in bad_cases.items():
        write_table(rows_)
        check("check catches: " + name, bool(M.check_tables(world(), mdir, ["Fake"], enum)))
    write_table(good)
    check("check: cannot-enumerate is a problem, not a silent pass",
          bool(M.check_tables(world(), mdir, ["Fake"], lambda m: None)))

# ---- the committed tables against the real ledger and real validation scripts
probs = M.check_tables(M.load_world())
check("committed tables check clean against the real ledger and validation.py", probs == [], probs[:3])
mods = M.table_mods()
nrows = sum(len(M.load_table(m)) for m in mods)
check("sanity probe: the committed tables are non-empty", len(mods) >= 1 and nrows >= 1, "%d tables %d rows" % (len(mods), nrows))
check("sanity probe: at least one unmapped row is committed (the tool can see them)",
      any(r["mode"] == "unmapped" for m in mods for r in M.load_table(m)))

# ---- real run files, if still on disk (Transient rots after ~14 days)
repo = M.ROOT
gt = os.path.join(repo, "Transient", "modcheck", "Greentide_20261007T203123Z.json")
pm = os.path.join(repo, "Transient", "modcheck", "PyrelandsMechanics_20261007T204247Z.json")
if os.path.exists(gt) and os.path.exists(pm):
    w = M.load_world()
    g = {(r["item"], r["criterion"]): r for r in M.run_apply(gt, "x", w)}
    check("real Greentide run: A2 PASS", g[("GREENTIDE_FIRST_SCRIPT_1", "A2")]["verdict"] == "PASS")
    check("real Greentide run: A3 UNMEASURED without a classification file", g[("GREENTIDE_FIRST_SCRIPT_1", "A3")]["verdict"] == "UNMEASURED")
    p = {(r["item"], r["criterion"]): r for r in M.run_apply(pm, "x", w)}
    check("real PyrelandsMechanics run reproduces the hand-recorded A2 and A3 as PASS",
          p[("PYRELANDS_MECHANICS_FIRST_SCRIPT_1", "A2")]["verdict"] == "PASS"
          and p[("PYRELANDS_MECHANICS_FIRST_SCRIPT_1", "A3")]["verdict"] == "PASS")
    _, vs = M.load_result(gt)
    cl = {c: "unmeasured: reviewed by selftest fixture" for c, v in vs.items() if v != "PASS"}
    check("real Greentide run: A3 PASS once every non-pass is classified (control)",
          M.evaluate(M.load_table("Greentide")[1], vs, cl)[0] == "PASS")
else:
    print("SKIP  real run files rotted away from Transient/modcheck")

# ---- CLI: a dry apply exits 0 and prints the summary; nothing is recorded
import subprocess  # noqa: E402
if os.path.exists(gt):
    p = subprocess.run([sys.executable, os.path.join(HERE, "acceptance_map.py"), "apply", gt, "--config", "x"],
                       capture_output=True, text=True)
    check("cli: dry apply exits 0 and says it would record nothing new", p.returncode == 0 and "re-run with --record" in p.stdout, p.stderr[-200:])

print("\n%s: %d failed" % ("RED" if FAILS else "GREEN", len(FAILS)))
sys.exit(1 if FAILS else 0)
