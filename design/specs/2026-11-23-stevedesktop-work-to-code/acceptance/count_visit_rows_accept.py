#!/usr/bin/env python3
"""Contract: src/RimMandrake/Utils/testq/visit_rows.py turns a finished visit job into rows of the open visit's rows.jsonl.

  rows_of(rec, table, identity) -> [row]     rec: a testq done record. table: {check id: {"testq": {"chains": [..]}}}.
        identity: {"mod_hash", "game_build", "active_mods", "mod_sha"} of the game that ran it, or None when it could not be
        read. One row per check all of whose chains are in the job: verdict PASS (every row PASS), FAIL (any FAIL), else
        COULD NOT LOOK with the first reason. Fields: test, verdict, game ("Steve1"/"Steve2"), job, command, detail, and
        the identity's fields. identity None: every verdict is COULD NOT LOOK.
  write(visit_dir, rows) -> how many were new; a row of the same (job, test) is never written twice.
  ingest.ingest_one calls it for a job requested by BENCH.visit.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _kit

ID = {"mod_hash": "sha256:a", "game_build": "1.6", "active_mods": ["x"], "mod_sha": "abc"}
TABLE = {"P_a": {"testq": {"chains": ["a"]}}, "P_bc": {"testq": {"chains": ["b", "c"]}}, "P_z": {"testq": {"chains": ["z"]}}, "P_none": {}}


def rec(rows, host=None):
    r = {"job": {"id": "J20261123T000000Z-aaaaaa", "mod": "Pyrelands", "requested_by": "BENCH.visit", "selector": {"chains": ["a", "b", "c"]}},
         "result": {"outcome": "DONE", "attempt": "J20261123T000000Z-aaaaaa.a1", "runner_sha": "abc",
                    "rows": [{"chain": c, "row": c + "1", "verdict": v, "detail": d} for c, v, d in rows]}}
    if host:
        r["host"] = r["result"]["host"] = host
    return r


def V():
    import visit_rows
    return visit_rows


def got(rows, host=None, identity=ID):
    return {r["test"]: r for r in V().rows_of(rec(rows, host), TABLE, identity)}


def wired():
    src = open(os.path.join(_kit.TESTQ, "ingest.py")).read()
    return "visit_rows" in src and "BENCH.visit" in src


def twice():
    d = tempfile.mkdtemp()
    rows = V().rows_of(rec([("a", "PASS", "")]), TABLE, ID)
    n = V().write(d, rows), V().write(d, rows)
    lines = [json.loads(x) for x in open(os.path.join(d, "rows.jsonl"))]
    return n == (1, 0) and len(lines) == 1 and lines[0]["test"] == "P_a" or (n, lines)


sys.exit(_kit.run([
    ("a check whose one chain passed reads PASS", lambda: got([("a", "PASS", "")])["P_a"]["verdict"] == "PASS"),
    ("a check of two chains waits for both: one absent is no row", lambda: "P_bc" not in got([("a", "PASS", ""), ("b", "PASS", "")])),
    ("both chains passed reads PASS", lambda: got([("b", "PASS", ""), ("c", "PASS", "")])["P_bc"]["verdict"] == "PASS"),
    ("any FAIL row reads FAIL", lambda: got([("b", "PASS", ""), ("c", "FAIL", "x")])["P_bc"]["verdict"] == "FAIL"),
    ("an unmeasured row is COULD NOT LOOK with its reason, never PASS or FAIL",
     lambda: got([("a", "UNMEASURED", "dead colonists")])["P_a"]["verdict"] == "COULD NOT LOOK" and "dead colonists" in got([("a", "UNMEASURED", "dead colonists")])["P_a"]["detail"]),
    ("a check with no block, and a chain not in the job, give no row", lambda: set(got([("a", "PASS", "")])) == {"P_a"}),
    ("the game is named Steve1", lambda: got([("a", "PASS", "")])["P_a"]["game"] == "Steve1"),
    ("the game is named Steve2", lambda: got([("a", "PASS", "")], "stevedesktop.b")["P_a"]["game"] == "Steve2"),
    ("the build identity is on the row", lambda: all(got([("a", "PASS", "")])["P_a"][k] == v for k, v in ID.items())),
    ("an identity that could not be read counts nothing", lambda: got([("a", "PASS", "")], identity=None)["P_a"]["verdict"] == "COULD NOT LOOK"),
    ("a second write of the same job adds nothing", twice),
    ("ingest calls it for a visit job", wired),
]))
