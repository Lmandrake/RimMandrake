"""Selftest for the checkout-result join (NORTHSTAR_RESULTS_JOIN_1; rules: bridge_validation_observatory.md 2.4).

A checkout (walk header `checkout:`) writes one result JSON per run; required_checks_report must read it as a
trustworthy-or-not record. Every rule is paired with a CONTROL that differs in that one field, so a rule that
silently stops firing turns this red instead of passing vacuously:
  fresh, fingerprinted, detectors recorded   -> its PASS/FAIL rows are proven
  same, no deploy fingerprint                -> pending deploy proof, never proven
  stale mod_hash                             -> tainted stale-result, listed STALE, never proven
  running DLL != repo DLL (hash current)     -> tainted stale-deploy
  a preflight row not PASS                   -> precondition on every row
  a newer PARTIAL run                        -> ignored; the newest LIVE run is read
  a checkout with no result / no record      -> the mod is LISTED, never omitted
Plus required_checks._add_checkout (mirrored rows marked, others added) and a sanity probe on the committed
manifest and the real results: both real checkouts enumerate and the report can read a result for each.
"""
import json
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import required_checks as RC  # noqa: E402
import required_checks_report as R  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


CUR = "c" * 64
OLD = "0" * 64
DLL = "d" * 64
DLLS = [("RimMandrakeSynth.dll", DLL, DLL)]
IDS = ["P1_fresh_map", "A1_one", "A2_two", "A3_three"]


def fp(mod):
    f = {"mod": mod, "state": "in-sync", "src_hash": "s1", "deployed_hash": "s1", "src_dirty": False}
    return {"deploy_start": dict(f), "deploy_end": dict(f), "git": {"source": "git", "sha": "abcdef1234"}}


def result(mod, mode="live", mod_hash=CUR, dll=DLL, fingerprint=True, situational=True, started="2026-10-05T08:00:00",
           pre="PASS", rows=None):
    r = {"mod": mod, "script": "proof_all.py", "mode": mode, "started": started, "wall_s": 600, "mod_hash": mod_hash,
         "env": {"assembly_sha256": dll},
         "rows": rows if rows is not None else [
             {"id": "P1_fresh_map", "status": pre, "class": "SITE", "detail": "", "block": "preflight"},
             {"id": "A1_one", "status": "PASS", "class": "MOD", "detail": "", "block": "core"},
             {"id": "A2_two", "status": "FAIL", "class": "MOD", "detail": "", "block": "core"},
             {"id": "A3_three", "status": "UNMEASURED", "class": "HARNESS", "detail": "", "block": "core"},
             {"id": "ZZ_undeclared", "status": "PASS", "class": "MOD", "detail": "", "block": "core"}]}
    if fingerprint:
        r["run_identity"] = fp(mod)
    if situational:
        r["situational"] = {"bland": True, "companion": True, "surprises": []}
    return r


def mrow(tmp, mod, rows=IDS, extra_missing=True):
    checks = [{"id": "checkout/" + i, "source": "checkout_row", "owner": False, "required": True, "checkout_row": i}
              for i in rows]
    if extra_missing:
        checks.append({"id": "checkout/A9_declared_never_emitted", "source": "checkout_row", "owner": False,
                       "required": True, "checkout_row": "A9_declared_never_emitted"})
    return {"script": None, "checks": checks,
            "checkout": {"script": os.path.join(tmp, mod, "proof_all.py"), "rows": len(checks), "error": None}}


def write(tmp, mod, name, res):
    d = os.path.join(tmp, mod, "northstar")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump(res, f)


def run(tmp, mods, results):
    """mods: {mod: mrow}; results: {mod: [(file name, result)]} -> {mod: entry}, rendered text."""
    for mod, rs in results.items():
        for name, res in rs:
            write(tmp, mod, name, res)
    rec = os.path.join(tmp, "records")
    os.makedirs(rec, exist_ok=True)
    rep, runs = R.build_report({"mods": mods}, rec, os.path.join(tmp, "none.jsonl"),
                               checkout_ident=lambda mod, row: (CUR, DLLS))
    return {e["mod"]: e for e in rep}, R.render(rep, runs, None)


def main():
    tmp = tempfile.mkdtemp(prefix="results_join_")
    try:
        cases = {
            "Fresh": [("proof_all_20261005T080000.json", result("Fresh"))],
            "NoFingerprint": [("proof_all_20261005T080000.json", result("NoFingerprint", fingerprint=False))],
            "Stale": [("proof_all_20261005T080000.json", result("Stale", mod_hash=OLD))],
            "WrongDll": [("proof_all_20261005T080000.json", result("WrongDll", dll="e" * 64))],
            "NoDetectors": [("proof_all_20261005T080000.json", result("NoDetectors", situational=False))],
            "PreflightRed": [("proof_all_20261005T080000.json", result("PreflightRed", pre="FAIL"))],
            "NewerPartial": [("proof_all_20261005T080000.json", result("NewerPartial")),
                             ("proof_all_20261005T090000.json",
                              result("NewerPartial", mode="partial", mod_hash=OLD, started="2026-10-05T09:00:00"))],
            "PartialOnly": [("proof_all_20261005T080000.json", result("PartialOnly", mode="partial"))],
            "NoResult": [],
        }
        mods = {m: mrow(tmp, m) for m in cases}
        mods["NoRecordNoCheckout"] = {"script": None, "checks": [{"id": "c/x", "source": "script_check",
                                                                    "owner": False, "required": True}]}
        by, text = run(tmp, mods, cases)

        f = by["Fresh"]
        check("fresh: read, current", f.get("checkout", {}).get("ident", {}).get("state") == "current",
              str(f.get("checkout", {}).get("ident")))
        check("fresh: its PASS/FAIL rows proven (2 PASS + 1 FAIL), the UNMEASURED one not",
              f["head"]["proven"] == 3 and f["head"]["proven_pass"] == 2 and f["head"]["proven_fail"] == 1,
              str(f["head"]))
        check("fresh: declared row never emitted is not reached",
              any(r["id"] == "checkout/A9_declared_never_emitted" and r["ran"] == "not_reached" for r in f["rows"]))
        check("fresh: emitted row not declared is observed-not-in-manifest", "checkout/ZZ_undeclared" in f["extras"],
              str(f["extras"]))
        h = by["NoFingerprint"]["head"]
        check("control no fingerprint: 0 proven, pending deploy 3", h["proven"] == 0 and h["pending_deploy"] == 3, str(h))
        h = by["Stale"]["head"]
        check("stale: 0 proven, tainted stale-result", h["proven"] == 0 and h["tainted"].get("stale-result") == 3, str(h))
        check("stale: listed under STALE in the report", "STALE / UNIDENTIFIED" in text and
              any(ln.strip().startswith("Stale ") for ln in text.splitlines()[text.splitlines().index(
                  next(l for l in text.splitlines() if l.startswith("STALE / UNIDENTIFIED"))):]))
        h = by["WrongDll"]["head"]
        check("wrong DLL: 0 proven, stale-deploy", h["proven"] == 0 and h["tainted"].get("stale-deploy") == 3, str(h))
        h = by["NoDetectors"]["head"]
        check("no detector record: 0 proven, unknown", h["proven"] == 0 and
              h["unknown"].get(R.DETECTORS_UNRECORDED) == 3, str(h))
        h = by["PreflightRed"]["head"]
        check("preflight red: 0 proven, precondition on every row", h["proven"] == 0 and
              h["tainted"].get("precondition") == 3, str(h))
        e = by["NewerPartial"]
        check("newer partial ignored, newest live read", e.get("checkout", {}).get("path", "").endswith("T080000.json")
              and e["head"]["proven"] == 3, str(e.get("checkout", {}).get("path")))
        check("partial only: not read, listed", by["PartialOnly"].get("unread") is True and
              "PartialOnly" in text, "")
        check("no result: listed under CHECKOUT DECLARED", by["NoResult"].get("unread") is True and
              any(ln.strip().startswith("NoResult") for ln in text.splitlines()), "")
        check("no record, no checkout: listed in NOT IN THE TOTAL",
              by["NoRecordNoCheckout"].get("unread") is True and "NOT IN THE TOTAL: 3 mods" in text, "")
        tot = [ln for ln in text.splitlines() if ln.startswith("TOTAL proven")]
        check("total counts only the trustworthy rows", tot and tot[0].startswith("TOTAL proven 6 of "), str(tot))

        # required_checks._add_checkout: a mirroring script_check is marked, the rest added once each
        sd = os.path.join(tmp, "Synth")
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "proof_all.py"), "w") as fh:
            fh.write("def declared_rows():\n    return ['M1_a', 'M2_b', 'M2_b', 'M3_c']\n")
        row = {"checks": [{"id": "core/M1_a", "source": "script_check"}, {"id": "core/M3_c#2", "source": "script_check"}]}
        RC._add_checkout(row, os.path.join(sd, "proof_all.py"))
        ids = [c["id"] for c in row["checks"]]
        check("manifest: mirrored row marked, not re-added", row["checks"][0].get("checkout_row") == "M1_a"
              and "checkout/M1_a" not in ids, str(ids))
        check("manifest: unmirrored rows added once each (dup id once; a #n mirror does not count)",
              ids.count("checkout/M2_b") == 1 and "checkout/M3_c" in ids and row["checkout"]["rows"] == 4, str(ids))
        with open(os.path.join(sd, "nodecl.py"), "w") as fh:
            fh.write("X = 1\n")
        row = {"checks": []}
        RC._add_checkout(row, os.path.join(sd, "nodecl.py"))
        check("manifest: a checkout without declared_rows() is a recorded error", bool(row["checkout"]["error"])
              and not row["checks"], str(row["checkout"]))
        wk = os.path.join(tmp, "w.md")
        with open(wk, "w") as fh:
            fh.write("# x\nsubject: a\ncheckout: src/a/b.py  (note)\n## north star\ncheckout: src/WRONG.py\n")
        w2 = os.path.join(tmp, "w2.md")
        with open(w2, "w") as fh:
            fh.write("# x\n## north star\ncheckout: src/WRONG.py\n")
        check("walk header: read from the header", RC.walk_checkout(wk) == "src/a/b.py", str(RC.walk_checkout(wk)))
        check("walk header: never read from inside a section", RC.walk_checkout(w2) is None, str(RC.walk_checkout(w2)))

        # sanity probe on the real repo: the instrument can SEE both real checkouts
        man = RC.load()
        for mod, n in (("GimmeSomeSlack", 144), ("FlowWorks", 59)):
            co = (man["mods"].get(mod) or {}).get("checkout") or {}
            check("committed manifest enumerates %s's checkout (%d rows)" % (mod, n),
                  co.get("rows") == n and not co.get("error"), str(co))
            got = R.checkout_results(mod, man["mods"].get(mod))
            check("real %s result files are found and parse" % mod, len(got) > 0 and
                  all(isinstance(r.get("rows"), list) for _f, r in got), "%d files" % len(got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failed" % ("RED" if FAILS else "GREEN", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
