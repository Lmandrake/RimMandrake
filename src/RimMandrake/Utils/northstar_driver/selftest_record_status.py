#!/usr/bin/env python3
"""Selftest for NORTHSTAR_DRIVER_RECORD_STATUS_1: the driver records a run through
modcheck.status.record_run. Offline; no bridge; the real modcheck_status.json is never touched
(status.LOG_PATH/LOCK_PATH are pointed at a temp dir, and the mod is a temp folder).

Criteria under test: a recorded run shows at the mod's current hash; a later edit reads STALE;
a run with an UNMEASURED or FAIL row is not GREEN; refusals, empty runs and mid-run edits are
not recorded; a mock run (cmd_run) never records; functional suite rows reach the verdict.
"""
import json
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_UTILS, os.path.join(_UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import status                                                             # noqa: E402
from northstar_driver import PASS, FAIL, UNMEASURED, cli                  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def doc(*statuses, **kw):
    rows = [{"id": "c.k%d" % i, "status": s, "functional": True} for i, s in enumerate(statuses)]
    d = {"mod": "NsRecFake", "mode": "live", "started_utc": "2026-10-02T00:00:00Z", "bars": rows,
         "expected_source": "no walk", "all_green": cli.run_all_green(rows, [])}
    d.update(kw)
    return d


def main():
    tmp = tempfile.mkdtemp(prefix="ns_rec_")
    real = (status.LOG_PATH, status.LOCK_PATH)
    status.LOG_PATH = os.path.join(tmp, "modcheck_status.json")
    status.LOCK_PATH = status.LOG_PATH + ".lock"
    try:
        mod_dir = os.path.join(tmp, "NsRecFake")
        os.makedirs(os.path.join(mod_dir, "Defs"))
        defs = os.path.join(mod_dir, "Defs", "a.xml")
        with open(defs, "w") as f:
            f.write("<Defs/>")
        h = status.mod_hash(mod_dir)
        out = os.path.join(tmp, "NsRecFake_x.json")

        e, msg = cli.record_result(doc(PASS, PASS), "NsRecFake", out, h, mod_dir)
        check("all-PASS run records GREEN", e and e["status"] == "GREEN", msg)
        on_disk = json.load(open(status.LOG_PATH)).get("NsRecFake") or {}
        check("entry is in the registry at the current hash", on_disk.get("hash") == h, str(on_disk)[:200])
        check("per-bar verdicts ride along", on_disk.get("bars") == {"c.k0": PASS, "c.k1": PASS})
        check("source names the driver", (on_disk.get("source") or {}).get("verb") == "northstar_driver run")
        check("check() reads GREEN now", status.check("NsRecFake", mod_dir) == "GREEN",
              status.check("NsRecFake", mod_dir))

        with open(defs, "w") as f:
            f.write("<Defs><!-- edit --></Defs>")
        check("an edit after the run reads STALE", status.check("NsRecFake", mod_dir) == "STALE",
              status.check("NsRecFake", mod_dir))

        h2 = status.mod_hash(mod_dir)
        e, msg = cli.record_result(doc(PASS, UNMEASURED), "NsRecFake", out, h2, mod_dir)
        check("UNMEASURED row -> not GREEN (RED)", e and e["status"] == "RED", msg)
        e, msg = cli.record_result(doc(PASS, FAIL), "NsRecFake", out, h2, mod_dir)
        check("FAIL row -> RED", e and e["status"] == "RED", msg)

        before = open(status.LOG_PATH).read()
        e, msg = cli.record_result(doc(PASS, refused="site:map_size FAIL"), "NsRecFake", out, h2, mod_dir)
        check("preflight refusal not recorded", e is None and "refused" in msg, msg)
        e, msg = cli.record_result(doc(), "NsRecFake", out, h2, mod_dir)
        check("empty run not recorded", e is None, msg)
        e, msg = cli.record_result(doc(PASS), "NsRecFake", out, "0" * 64, mod_dir)
        check("mod edited mid-run not recorded", e is None and "changed during the run" in msg, msg)
        e, msg = cli.record_result(doc(PASS), "adhoc", out, None, None)
        check("ad-hoc mod not recorded", e is None, msg)
        check("no refused case wrote the registry", open(status.LOG_PATH).read() == before)

        # functional rows reach the verdict, with or without north-star bars expected
        ns = [{"id": "ns1", "status": PASS}]
        check("expected bar PASS + functional FAIL is not green",
              not cli.run_all_green(ns + [{"id": "c.k", "status": FAIL, "functional": True}], ["ns1"]))
        check("expected bar PASS + functional PASS is green",
              cli.run_all_green(ns + [{"id": "c.k", "status": PASS, "functional": True}], ["ns1"]))
        chains = [{"name": "c", "components": [{"name": "a", "verdict": "PASS"},
                                               {"name": "b", "verdict": "FAIL", "detail": "x"},
                                               {"name": "v", "verdict": "PASS", "shows": ["ns1"]},
                                               {"name": "u", "verdict": "UNMEASURED"}]}]
        fr = {r["id"]: r["status"] for r in cli.functional_rows(chains)}
        check("functional_rows: one per non-visual component", fr == {"c.a": PASS, "c.b": FAIL, "c.u": UNMEASURED},
              str(fr))

        # failure text longer than the 300-char console excerpt survives whole in `evidenceFull`
        long_why = "map_fire started no fire " + "R" * 700 + " TAIL-MARKER"
        lc = [{"name": "c", "components": [{"name": "k", "verdict": "FAIL", "detail": long_why,
                                            "shows": ["ns1"]},
                                           {"name": "f", "verdict": "FAIL", "detail": long_why}]}]
        from northstar_driver import bars as _bars
        row = _bars.rollup_components(lc, ["ns1"])[0]
        check("rollup: console evidence stays short", len(row["evidence"]) < 400, str(len(row["evidence"])))
        check("rollup: evidenceFull keeps the whole reason", "TAIL-MARKER" in row.get("evidenceFull", ""))
        frow = cli.functional_rows(lc)[0]
        check("functional row: console short, evidenceFull whole",
              len(frow["evidence"]) == 300 and frow["evidenceFull"].endswith("TAIL-MARKER"))
        crec = cli.component_records(lc)[0]
        check("component record: a shows= component keeps evidenceFull whole",
              crec.get("evidenceFull", "").endswith("TAIL-MARKER"))

        # a mock run through cmd_run never records (the real registry must not move either)
        status.LOG_PATH = os.path.join(tmp, "must_not_exist.json")
        root = os.path.dirname(os.path.dirname(os.path.dirname(_UTILS)))
        # Salvation Rites: its suite carries Ishko's landmarks since 2026-10-22 (was IshkoDarkLandmarks)
        plan = os.path.join(root, "src", "RimUtinni", "Rites", "northstar_plan.py")
        rc = cli.main(["run", "--mock", "--mod", "Rites", "--plan", plan,
                       "--out", os.path.join(tmp, "rites_mock.json")])
        check("Rites mock run is GREEN", rc == 0, "rc=%s" % rc)
        check("mock run wrote no registry", not os.path.exists(status.LOG_PATH))
        res = json.load(open(os.path.join(tmp, "rites_mock.json")))
        check("mock result carries mod_hash", bool(res.get("mod_hash")))
        check("mock result has the 12 functional rows (2 research, 2 shipped-defs, 8 Ishko)",
              sum(1 for r in res["bars"] if r.get("functional")) == 12, str(len(res["bars"])))
    finally:
        status.LOG_PATH, status.LOCK_PATH = real
        shutil.rmtree(tmp, ignore_errors=True)

    print("FAILED: %s" % FAILS if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
