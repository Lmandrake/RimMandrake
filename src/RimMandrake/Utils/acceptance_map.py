#!/usr/bin/env python3
"""acceptance_map -- the per-mod table saying which modcheck chain/component proves which
acceptance criterion, so recording a pass is mechanical (MODCHECK_ACCEPTANCE_MAPPING_TABLE_1).

Tables:  infrastructure/state/acceptance_map/<Mod>.json   (schema: that dir's README.md)

    python3 acceptance_map.py check [--mod M]
        Validate every table: items and criteria exist in the ledger, the level matches the
        ledger's, every component id is declared by the mod's validation.py (live no-op probe,
        falling back to modcheck/required_checks.json), rows are unique, notes are present.
    python3 acceptance_map.py list
        Every row, UNMAPPED rows called out.
    python3 acceptance_map.py apply <result.json> --config <tier> [--mod M]
                                    [--classified file.json] [--record]
        Evaluate each mapped criterion against a modcheck (Transient/modcheck/*.json) or
        l2sweep (Transient/l2sweep_<Mod>.json) result and print a table. With --record, call
        `rimflow verify ... --result pass` for CLEAN PASSes on outstanding criteria ONLY.

What this tool will never do: record a fail/partial, record anything for a FAIL or UNMEASURED
verdict, record an UNMAPPED row, record a criterion the ledger does not list as outstanding,
or record on a level that disagrees with the ledger. It never writes anything without --record.

Verdict algebra (components of one row): any FAIL -> FAIL; else any component missing from the
run or UNMEASURED -> UNMEASURED; else PASS. A row may list `accept: ["PASS","UNMEASURED"]`
only when the criterion's own wording accepts "recorded as unmeasured".
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAP_DIR = os.path.join(ROOT, "infrastructure", "state", "acceptance_map")
RIMFLOW_CLI = os.path.join(ROOT, "src", "RimMandrake", "rimflow", "cli.py")

LEVELS = ("L0", "L1", "L2", "GREEN-MIN", "GREEN-FULL", "L3", "L4")
MODES = ("all", "any", "classified", "unmapped")
VERDICTS = ("PASS", "FAIL", "UNMEASURED")
CLASSES = ("harness", "site", "mod", "unmeasured")
RUN = "@run"          # pseudo-component: the result file parsed and holds >= 1 component
ALL = "*"             # classified mode only: every component of the run
ROW_KEYS = {"item", "criterion", "level", "components", "mode", "notes", "accept"}


# --------------------------------------------------------------------------- tables
def table_path(mod, map_dir=None):
    return os.path.join(map_dir or MAP_DIR, mod + ".json")


def table_mods(map_dir=None):
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(map_dir or MAP_DIR, "*.json")))


def load_table(mod, map_dir=None):
    with open(table_path(mod, map_dir), encoding="utf-8") as fh:
        rows = json.load(fh)
    if not isinstance(rows, list):
        raise ValueError("%s: a table is a JSON list of rows" % mod)
    return rows


def row_schema_problems(row):
    """Static problems with one row, independent of the ledger and the validation script."""
    p = []
    if not isinstance(row, dict):
        return ["row is not an object"]
    for k in sorted(set(row) - ROW_KEYS):
        p.append("unknown key %r" % k)
    for k in ("item", "criterion", "level", "components", "mode", "notes"):
        if k not in row:
            p.append("missing key %r" % k)
    if p:
        return p
    if row["level"] not in LEVELS:
        p.append("level %r not one of %s" % (row["level"], "/".join(LEVELS)))
    if row["mode"] not in MODES:
        p.append("mode %r not one of %s" % (row["mode"], "/".join(MODES)))
    if not isinstance(row["notes"], str) or not row["notes"].strip():
        p.append("notes must justify the row (non-empty string)")
    comps = row["components"]
    if not isinstance(comps, list) or not all(isinstance(c, str) and c for c in comps):
        p.append("components must be a list of strings")
        return p
    if row["mode"] == "unmapped":
        if comps:
            p.append("an unmapped row carries no components")
        if "accept" in row:
            p.append("an unmapped row carries no accept")
    else:
        if not comps and row["mode"] != "classified":
            p.append("a mapped row needs at least one component")
        for c in comps:
            if c == ALL and row["mode"] != "classified":
                p.append("%r is only for mode classified" % ALL)
            elif c not in (RUN, ALL) and "/" not in c:
                p.append("component %r is not chain/component" % c)
        if row["mode"] == "classified" and not (ALL in comps or RUN in comps):
            p.append("classified mode lists %r or %r" % (ALL, RUN))
    if "accept" in row:
        a = row["accept"]
        if (not isinstance(a, list) or "PASS" not in a or "FAIL" in a
                or any(x not in ("PASS", "UNMEASURED") for x in a)):
            p.append("accept must be a list of PASS and optionally UNMEASURED (FAIL is never accepted)")
    return p


# --------------------------------------------------------------------------- results
def worst(a, b):
    order = {"PASS": 0, "UNMEASURED": 1, "FAIL": 2}
    return a if order[a] >= order[b] else b


def load_result(path):
    """-> (mod_or_None, {component_id: verdict}). Accepts a modcheck sheet ({mod, stamp,
    summary:{chains}}) or an l2sweep result ({chains,...}). Any verdict other than PASS/FAIL
    is read as UNMEASURED -- an instrument that cannot say is not a pass."""
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    mod = d.get("mod") if isinstance(d, dict) else None
    if isinstance(d, dict) and "summary" in d and "chains" not in d:
        d = d["summary"]
    if not isinstance(d, dict) or not isinstance(d.get("chains"), list):
        raise ValueError("%s: no `chains` list -- not a modcheck / l2sweep result" % path)
    out = {}
    for ch in d["chains"]:
        for c in ch.get("components") or []:
            v = c.get("verdict")
            v = v if v in ("PASS", "FAIL") else "UNMEASURED"
            cid = "%s/%s" % (ch.get("name"), c.get("name"))
            out[cid] = worst(out[cid], v) if cid in out else v
    if mod is None:
        b = os.path.basename(path)
        if b.startswith("l2sweep_") and b.endswith(".json"):
            mod = b[len("l2sweep_"):-5].split(".")[0]
        elif "_" in b:
            mod = b.split("_")[0]
    return mod, out


def evaluate(row, verdicts, classified=None):
    """-> (verdict, reason) for one row against {component_id: verdict}.
    verdict is PASS | FAIL | UNMEASURED | UNMAPPED."""
    mode = row["mode"]
    if mode == "unmapped":
        return "UNMAPPED", "no mechanical mapping: %s" % row["notes"]
    accept = set(row.get("accept") or ["PASS"])
    if mode == "classified":
        if not verdicts:
            return "UNMEASURED", "run holds no components"
        bad = sorted(c for c, v in verdicts.items() if v != "PASS")
        if not bad:
            return "PASS", "%d components, none non-pass" % len(verdicts)
        if classified is None:
            return "UNMEASURED", "%d non-pass components need a --classified file" % len(bad)
        missing = [c for c in bad if not _classified_ok(classified.get(c))]
        if missing:
            return "UNMEASURED", "unclassified non-pass: %s" % ", ".join(missing[:5])
        return "PASS", "%d non-pass all classified" % len(bad)
    got = []
    for c in row["components"]:
        if c == RUN:
            got.append((c, "PASS" if verdicts else "UNMEASURED"))
        else:
            got.append((c, verdicts.get(c, "ABSENT")))
    fails = [c for c, v in got if v == "FAIL"]
    ok = [c for c, v in got if v == "PASS" or (v == "UNMEASURED" and "UNMEASURED" in accept)]
    other = [(c, v) for c, v in got if c not in ok and v != "FAIL"]
    if mode == "all":
        if fails:
            return "FAIL", "FAIL: %s" % ", ".join(fails)
        if other:
            return "UNMEASURED", "; ".join("%s %s" % (c, v) for c, v in other)
        return "PASS", "%d/%d components" % (len(ok), len(got))
    # any
    if ok:
        return "PASS", "via %s" % ok[0]
    if other:
        return "UNMEASURED", "; ".join("%s %s" % (c, v) for c, v in other)
    return "FAIL", "FAIL: %s" % ", ".join(fails)


def _classified_ok(entry):
    return isinstance(entry, str) and entry.split(":", 1)[0].strip() in CLASSES


# --------------------------------------------------------------------------- ledger view
def load_world():
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake"))
    from rimflow import model
    return model.replay(model.read())


def ledger_status(world, item_id, criterion, level):
    """-> (status, detail). OUTSTANDING is the only status that may be recorded."""
    it = world.items.get(item_id)
    if it is None:
        return "NO-ITEM", "item not in the ledger"
    crit = {c["id"]: c for c in it.criteria}
    if criterion not in crit:
        return "NO-CRITERION", "item has no criterion %s (manifest: %s)" % (
            criterion, ",".join(sorted(crit)) or "none")
    if crit[criterion]["level"] != level:
        return "LEVEL-MISMATCH", "ledger says %s, table says %s" % (crit[criterion]["level"], level)
    if criterion in set(it.outstanding):
        return "OUTSTANDING", "state %s" % it.state
    return "NOT-OUTSTANDING", "already passed or item %s" % it.state


# --------------------------------------------------------------------------- check
def enumerate_components(mod):
    """Set of chain/component ids the mod's validation.py declares, or None if unknowable.
    Live no-op probe first (the committed manifest goes stale: EmpirePursuit's ladder chain
    was absent from it), manifest as fallback."""
    mc = os.path.join(HERE, "modcheck")
    if mc not in sys.path:
        sys.path.insert(0, mc)
    try:
        import required_checks as R
        dirs = R._mod_dirs().get(mod)
        if dirs and len(dirs) == 1:
            return {"%s/%s" % (c[0], c[1]) for c in R.script_checks(dirs[0])}
    except Exception:
        pass
    try:
        with open(os.path.join(mc, "required_checks.json"), encoding="utf-8") as fh:
            man = json.load(fh)["mods"].get(mod)
        if man:
            return {c["id"] for c in man["checks"]}
    except Exception:
        pass
    return None


def check_tables(world, map_dir=None, mods=None, enumerate_fn=enumerate_components):
    """-> list of problem strings (empty = every table is sound)."""
    problems = []
    for mod in (mods or table_mods(map_dir)):
        try:
            rows = load_table(mod, map_dir)
        except Exception as e:
            problems.append("%s: unreadable table: %s" % (mod, e))
            continue
        comps = None
        seen = set()
        for i, row in enumerate(rows):
            tag = "%s[%d]" % (mod, i)
            sp = row_schema_problems(row)
            if sp:
                problems.extend("%s: %s" % (tag, s) for s in sp)
                continue
            key = (row["item"], row["criterion"])
            if key in seen:
                problems.append("%s: duplicate row for %s %s" % (tag, *key))
            seen.add(key)
            st, detail = ledger_status(world, row["item"], row["criterion"], row["level"])
            if st in ("NO-ITEM", "NO-CRITERION", "LEVEL-MISMATCH"):
                problems.append("%s: %s %s: %s" % (tag, row["item"], row["criterion"], detail))
            real = [c for c in row["components"] if c not in (RUN, ALL)]
            if real:
                if comps is None:
                    comps = enumerate_fn(mod) or False
                if comps is False:
                    problems.append("%s: cannot enumerate %s's validation components" % (tag, mod))
                else:
                    for c in real:
                        if c not in comps:
                            problems.append("%s: component %r is not declared by %s validation.py" % (tag, c, mod))
    return problems


# --------------------------------------------------------------------------- apply
def real_verify(item, criterion, level, config, evidence):
    """-> (ok, message). The ONLY place a ledger write can start."""
    cmd = [sys.executable, RIMFLOW_CLI, "verify", item, "--criterion", criterion, "--result", "pass",
           "--config", config, "--level", level, "--evidence", evidence]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    msg = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()
    return p.returncode == 0, (msg[-1] if msg else "")


def run_apply(result_path, config, world, mod=None, classified=None, record=False,
              map_dir=None, verify_fn=real_verify, evidence=None):
    """-> list of result rows [{mod,item,criterion,level,verdict,ledger,action,reason}].
    `record` False never calls verify_fn. Records only PASS + OUTSTANDING."""
    rmod, verdicts = load_result(result_path)
    mod = mod or rmod
    if not mod:
        raise ValueError("cannot tell the mod from %s; pass --mod" % result_path)
    if not os.path.exists(table_path(mod, map_dir)):
        raise ValueError("no acceptance table for %s (%s)" % (mod, table_path(mod, map_dir)))
    rows = load_table(mod, map_dir)
    out = []
    for i, row in enumerate(rows):
        sp = row_schema_problems(row)
        if sp:
            raise ValueError("%s[%d]: %s -- run `check` first" % (mod, i, "; ".join(sp)))
        verdict, reason = evaluate(row, verdicts, classified)
        st, detail = ledger_status(world, row["item"], row["criterion"], row["level"])
        action = "-"
        if verdict == "PASS":
            if st != "OUTSTANDING":
                action = "skip (%s)" % st.lower()
            elif not record:
                action = "would record"
            else:
                ok, msg = verify_fn(row["item"], row["criterion"], row["level"], config,
                                    evidence or result_path)
                action = "RECORDED" if ok else "verify refused: %s" % msg
        out.append(dict(mod=mod, item=row["item"], criterion=row["criterion"], level=row["level"],
                        verdict=verdict, ledger=st, action=action, reason=reason))
    # criteria the ledger still owes on these items that no row covers: never silent
    mapped = {(r["item"], r["criterion"]) for r in out}
    for item in sorted({r["item"] for r in out}):
        it = world.items.get(item)
        for cid in sorted(it.outstanding) if it else ():
            if (item, cid) not in mapped:
                lvl = next((c["level"] for c in it.criteria if c["id"] == cid), "?")
                out.append(dict(mod=mod, item=item, criterion=cid, level=lvl, verdict="NOT-IN-TABLE",
                                ledger="OUTSTANDING", action="-", reason="outstanding criterion with no row"))
    return out


def render(results):
    cols = ("item", "criterion", "level", "verdict", "ledger", "action", "reason")
    w = {c: max(len(c), *(len(str(r[c])) for r in results)) if results else len(c) for c in cols}
    w["reason"] = 0
    lines = ["  ".join(c.ljust(w[c]) for c in cols).rstrip()]
    for r in results:
        lines.append("  ".join(str(r[c]).ljust(w[c]) for c in cols).rstrip())
    return "\n".join(lines)


# --------------------------------------------------------------------------- cli
def main(argv=None):
    ap = argparse.ArgumentParser(prog="acceptance_map", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--mod", action="append")
    sub.add_parser("list")
    a = sub.add_parser("apply")
    a.add_argument("result")
    a.add_argument("--config", required=True, help="tier/config name recorded on the verify, e.g. acc_green_min2")
    a.add_argument("--mod")
    a.add_argument("--classified", help='JSON {"chain/component": "harness|site|mod|unmeasured: why"}')
    a.add_argument("--record", action="store_true", help="call rimflow verify for clean PASSes only")
    args = ap.parse_args(argv)

    if args.cmd == "list":
        for mod in table_mods():
            for r in load_table(mod):
                print("%-18s %-44s %-4s %-10s %-10s %s" % (
                    mod, r["item"], r["criterion"], r["level"], r["mode"].upper() if r["mode"] == "unmapped" else r["mode"],
                    ",".join(r["components"])))
        return 0
    world = load_world()
    if args.cmd == "check":
        probs = check_tables(world, mods=args.mod)
        for p in probs:
            print("PROBLEM", p)
        print("acceptance_map check: %d tables, %d problems" % (len(args.mod or table_mods()), len(probs)))
        return 1 if probs else 0
    classified = None
    if args.classified:
        with open(args.classified, encoding="utf-8") as fh:
            classified = json.load(fh)
    res = run_apply(args.result, args.config, world, mod=args.mod, classified=classified,
                    record=args.record)
    print(render(res))
    for r in res:
        print("  %s %s: %s" % (r["item"], r["criterion"], r["reason"]))
    rec = sum(r["action"] == "RECORDED" for r in res)
    would = sum(r["action"] == "would record" for r in res)
    print("-- %d rows: %d PASS, %d FAIL, %d UNMEASURED, %d UNMAPPED, %d NOT-IN-TABLE; %s" % (
        len(res), *(sum(r["verdict"] == v for r in res) for v in ("PASS", "FAIL", "UNMEASURED", "UNMAPPED", "NOT-IN-TABLE")),
        "%d recorded (ledger writes are local, uncommitted)" % rec if args.record else "%d would record (re-run with --record)" % would))
    return 0


if __name__ == "__main__":
    sys.exit(main())
