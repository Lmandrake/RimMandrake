"""Offline instrument tests of the production M15f path. No live acceptance."""
import ast
import contextlib
import os
import copy
import json
import pathlib
import subprocess
import tempfile
import time
from unittest import mock
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validation_aerial as A


class Bridge:
    def __init__(self, fault=None):
        self.fault = fault
        self.sent = []
        self.cut = False
        self.complete = False
        self.ordered = False
        self.job = False
        self.steps = 0
        self.complete_after = 1
        self.counter_base = 0
        self.overrides = {}
        self.looks = ["Scrapper", "Scrapper"]
        self.pawns = [{"id": 7, "pos": [80, 180], "drafted": True, "downed": False, "job": None}]

    def ap(self, cmd):
        self.sent.append(cmd)
        if cmd in self.overrides:
            return copy.deepcopy(self.overrides[cmd])
        ok = {"success": True, "cmd": cmd}
        if cmd.startswith("cut:"):
            self.cut = self.fault != "no_cut"
            return dict(ok, done=self.cut)
        if cmd.startswith("crestyle:"):
            cell, look = cmd[9:].split(":")
            idx = 0 if cell == "%d,%d" % A.M2 else 1
            self.looks[idx] = look.split("_")[0]
            if self.fault == "same_before" and not self.complete:
                self.looks = ["Industrial", "Industrial"]
            return ok
        if cmd == "cprocess":
            return ok
        if cmd == "cstyles":
            looks = list(self.looks)
            if self.complete:
                looks = ["Modern", "Industrial"] if self.fault == "unequal_after" else ["Industrial", "Industrial"]
            if self.fault == "none_after" and self.complete:
                looks[1] = None
            if self.fault in ("missing_style", "none_style", "empty_style"):
                looks[1] = {"none_style": None, "empty_style": ""}.get(self.fault)
            result = dict(ok, defaultKey="Scrapper", members=[
                {"id": i, "x": p[0], "z": p[1], "look": looks[n],
                 "rawStyle": "Style_" + str(looks[n]), "colour": None,
                 "run": 2 if self.complete else i}
                for n, (i, p) in enumerate(((2, A.M2), (3, A.M3)))])
            if self.complete and self.fault == "colour_after":
                result["members"][1]["colour"] = "Orange"
            if self.complete and self.fault == "runs_after":
                result["members"][1]["run"] = 3
            if self.fault == "runs_before" and not self.complete:
                result["members"][1]["run"] = 2
            if self.fault == "raw_style_missing":
                result["members"][1]["rawStyle"] = None
            return result
        if cmd == "census":
            joined = self.complete or not self.cut
            nets = [11, 11] if joined else [11, 22]
            if self.fault == "no_disconnect":
                nets = [11, 11]
            if self.complete and self.fault == "unjoined_after":
                nets = [11, 22]
            return dict(ok, anchors=[
                {"id": i, "x": p[0], "z": p[1], "net": nets[n],
                 "links": [{"other": other, "state": "Up" if joined else "Cut"}]}
                for n, (i, other, p) in enumerate(((2, 3, A.M2), (3, 2, A.M3)))])
        if cmd.startswith("restringorder:"):
            self.ordered = True
        if cmd.startswith("restringjob:"):
            if self.fault == "job_failure":
                return {"success": False, "error": "no free colonist"}
            if self.fault == "direct_bypass":
                self.complete = True
            self.job = True
            self.pawns[0]["job"] = None if self.fault == "not_running" else "RM_RestringSpan"
            return dict(self.state(cmd), by="Human999" if self.fault == "wrong_worker" else "Human7")
        if cmd.startswith("restringstate:") or cmd.startswith("restringorder:"):
            return self.state(cmd)
        if cmd.startswith("restring:"):
            self.complete = True
            return dict(ok, done=True)
        raise AssertionError(cmd)

    def state(self, cmd):
        completed = self.complete and self.fault != "no_completion"
        return {"success": True, "cmd": cmd, "cut": 0 if self.complete else 1,
                "designated": self.ordered and not self.complete,
                "jobsDone": self.counter_base + int(completed), "spansRestrung": self.counter_base + int(completed)}

    def probe(self, cmd):
        self.sent.append(cmd)
        if cmd == "colonists":
            return {"success": True, "cmd": cmd, "pawns": copy.deepcopy(self.pawns)}
        _, rest = cmd.split(":", 1)
        _, action = rest.split("=")
        if action.startswith("tp"):
            self.pawns[0]["pos"] = [80, 180]
            self.pawns[0]["job"] = None
        else:
            self.pawns[0]["drafted"] = action == "draft"
        return {"success": True, "cmd": cmd, "pawn": dict(self.pawns[0])}

    def ticks(self, n):
        self.sent.append(("ticks", n))
        if self.job and n == 250:
            self.steps += 1
            if self.fault != "timeout" and self.steps >= self.complete_after:
                self.complete = True
                self.pawns[0]["job"] = None
                self.pawns[0]["pos"] = [110, 185]


    def call(self, tool, **kwargs):
        self.sent.append((tool, kwargs))
        if tool != "jawa/pawn_get":
            raise AssertionError(tool)
        return {"success": True, "pawns": [{"thingId": kwargs["pawn"], "thingIdNumber":
                                           999 if self.fault == "wrong_worker" else 7}]}


def run_row(bridge):
    rows = []
    A.restring_style_job(bridge, rows, 2, 3)
    if len(rows) != 1:
        raise AssertionError(rows)
    print(json.dumps({"fault": bridge.fault, "row": rows[0], "calls": bridge.sent}, default=str))
    return rows[0]


class RestringProof(unittest.TestCase):
    def test_live_flow_calls_helper(self):
        tree = ast.parse(pathlib.Path(A.__file__).read_text())
        live, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_run_live"]
        calls = [n for n in ast.walk(live) if isinstance(n, ast.Call) and
                 isinstance(n.func, ast.Name) and n.func.id == "restring_style_job"]
        self.assertEqual(len(calls), 1)
        self.assertEqual([n.id for n in calls[0].args], ["B", "rows", "i2", "i3"])

    def test_actual_job_path(self):
        b = Bridge()
        row = run_row(b)
        self.assertEqual(row["status"], "PASS", row)
        self.assertFalse(any(isinstance(c, str) and c.startswith("restring:") for c in b.sent), b.sent)
        self.assertIn("restringjob:2", b.sent)


    def test_rejects_false_pass_scenarios(self):
        for fault in ("job_failure", "direct_bypass", "no_cut", "no_disconnect", "same_before",
                      "missing_style", "none_style", "empty_style", "no_completion",
                      "not_running", "wrong_worker", "colour_after", "runs_after", "runs_before", "raw_style_missing", "unequal_after", "unjoined_after", "none_after", "timeout"):
            with self.subTest(fault=fault):
                b = Bridge(fault)
                row = run_row(b)
                self.assertNotEqual(row["status"], "PASS", row)
                self.assertLessEqual(b.steps, 12)
                self.assertEqual(b.pawns[0]["pos"], [80, 180])
                self.assertIs(b.pawns[0]["drafted"], True)
                self.assertFalse(any(isinstance(c, str) and c.startswith("restring:") for c in b.sent))

    def test_counter_deltas_with_existing_jobs(self):
        b = Bridge()
        b.counter_base = 5
        self.assertEqual(run_row(b)["status"], "PASS")
        b = Bridge("no_completion")
        b.counter_base = 5
        self.assertNotEqual(run_row(b)["status"], "PASS")

    def test_mismatched_reply_echo(self):
        b = Bridge()
        b.overrides["cut:2,3"] = {"success": True, "done": True, "cmd": "restring:2,3"}
        self.assertNotEqual(run_row(b)["status"], "PASS")

    def test_bounded_completion(self):
        for complete_after, passes in ((12, True), (13, False)):
            with self.subTest(complete_after=complete_after):
                b = Bridge()
                b.complete_after = complete_after
                self.assertEqual(run_row(b)["status"] == "PASS", passes)
                self.assertEqual(b.steps, 12)

    def test_bad_readings(self):
        invalid = [
            ("cut:2,3", None),
            ("restringorder:2", {"success": False, "error": "order failed"}),
            ("restringorder:2", {"success": True, "cut": 1, "jobsDone": 0,
                                 "spansRestrung": 0, "designated": False}), ("cut:2,3", {"success": True, "done": 1}),
            ("census", {"success": True, "anchors": [None]}),
            ("census", {"success": True, "anchors": []}),
            ("cstyles", {"success": True, "members": None}),
            ("cstyles", {"success": True, "defaultKey": "Scrapper", "members": [None]}),
            ("restringorder:2", {"success": True, "cut": True, "jobsDone": 0,
                                 "spansRestrung": 0, "designated": True}),
            ("restringjob:2", {"success": True, "cut": 1, "jobsDone": "0",
                               "spansRestrung": 0, "designated": True, "by": "Human7"}),
            ("restringstate:2", {"success": True, "cut": 0, "jobsDone": None,
                                 "spansRestrung": 1, "designated": False}),
        ]
        for cmd, value in invalid:
            with self.subTest(cmd=cmd, value=value):
                b = Bridge()
                b.overrides[cmd] = dict(value, cmd=cmd) if isinstance(value, dict) else value
                self.assertNotEqual(run_row(b)["status"], "PASS")

    def test_no_colonist_and_missing_anchor(self):
        b = Bridge()
        b.pawns = []
        self.assertNotEqual(run_row(b)["status"], "PASS")
        rows = []
        A.restring_style_job(Bridge(), rows, None, 3)
        self.assertNotEqual(rows[0]["status"], "PASS")

    def test_park_attempts_all_pawns_after_transport_exception(self):
        b = Bridge()
        home = copy.deepcopy(b.pawns) + [{"id": 8, "pos": [81, 180]}]
        sent = []
        def probe(cmd):
            sent.append(cmd)
            raise RuntimeError("transport down")
        with mock.patch.object(b, "probe", side_effect=probe):
            with self.assertRaises(RuntimeError):
                A.park_restring_colonists(b, home)
        self.assertIn("pawn:8=tp:81,180", sent)

    def test_exact_pair_evidence(self):
        for key, bad in (("net", -1), ("net", None), ("net", True), ("links", []),
                         ("links", [{"other": 2, "state": "Up"}])):
            b = Bridge()
            original = b.ap("census")
            original["anchors"][1][key] = bad
            b.overrides["census"] = original
            with self.subTest(key=key, bad=bad):
                self.assertNotEqual(run_row(b)["status"], "PASS")
        b = Bridge()
        original = b.ap("cstyles")
        original["members"].append(original["members"][0])
        b.overrides["cstyles"] = original
        self.assertNotEqual(run_row(b)["status"], "PASS")

    def test_style_restore_and_pawn_return_precede_next_cut(self):
        b = Bridge()
        row = run_row(b)
        self.assertEqual(row["class"], "MOD")
        self.assertEqual(b.pawns[0]["pos"], [80, 180])
        self.assertIs(b.pawns[0]["drafted"], True)
        self.assertEqual(b.looks, ["Scrapper", "Scrapper"])
        self.assertIn("crestyle:104,185:Scrapper", b.sent)
        self.assertIn("crestyle:116,185:Scrapper", b.sent)

    def test_cleanup_failure_stops_flow(self):
        b = Bridge()
        def failed_park(*args):
            raise RuntimeError("return transport failed")
        rows = []
        with mock.patch.object(A, "park_restring_colonists", side_effect=failed_park):
            with self.assertRaisesRegex(RuntimeError, "cleanup failed"):
                A.restring_style_job(b, rows, 2, 3)
        self.assertEqual(rows[0]["status"], "FAIL")
        self.assertIn("return transport failed", str(rows[0]))


class FreshCommand(unittest.TestCase):
    def result(self, **changes):
        import restring_style_proof as P
        return {"script": "validation_aerial.py", "mode": "live",
                "rows": [{"id": P.ROW, "status": "PASS", "class": "MOD",
                          "detail": {"schema": 1, "jobDef": "RM_RestringSpan"}}], **changes}

    def test_exact_fresh_result(self):
        import restring_style_proof as P
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "aerial.json"
            path.write_text(json.dumps(self.result()))
            stamp = path.stat().st_mtime
            self.assertEqual(P.check_result(path, stamp - 1, stamp + 1)["status"], "PASS")
            for start, end in ((stamp + 1, stamp + 2), (stamp - 2, stamp - 1)):
                with self.assertRaises(ValueError):
                    P.check_result(path, start, end)

    def test_absent_wrong_stale_malformed_rows(self):
        import restring_style_proof as P
        variants = [None, [], {}, self.result(rows=[{"id": P.ROW, "status": "PASS", "class": "MOD"}]), self.result(rows=[]), self.result(mode="save-load"),
                    self.result(script="validation.py"), self.result(aborted="probe dead"),
                    self.result(rows=[None]), self.result(rows="PASS"),
                    self.result(rows=[{"id": P.ROW + "_extra", "status": "PASS", "class": "MOD"}]),
                    self.result(rows=self.result()["rows"] * 2)]
        for field, values in (("status", ("FAIL", "UNMEASURED", None, True)),
                              ("class", ("HARNESS", "SITE", None))):
            for value in values:
                r = self.result()
                r["rows"][0][field] = value
                variants.append(r)
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "aerial.json"
            with self.assertRaises(ValueError):
                P.check_result(path, 0, time.time())
            for value in variants:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value))
                    stamp = path.stat().st_mtime
                    with self.assertRaises(ValueError):
                        P.check_result(path, stamp - 1, stamp + 1)
            path.write_text("{bad JSON")
            with self.assertRaises(ValueError):
                P.check_result(path, 0, time.time())

    def test_command_launch_and_raw_retention(self):
        import restring_style_proof as P
        for fault in (None, "driver_fail", "no_file", "row_fail", "timeout", "malformed"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                def driver(command, **kwargs):
                    self.assertEqual(command[1], str(HERE / "validation_aerial.py"))
                    self.assertEqual(command[2:4], ["--live", "--out"])
                    self.assertEqual(kwargs["timeout"], 900)
                    kwargs["stdout"].write(b"full driver raw stdout\n")
                    kwargs["stderr"].write(b"full driver raw stderr\n")
                    if fault == "timeout":
                        raise subprocess.TimeoutExpired(command, 900)
                    result = self.result()
                    if fault == "row_fail":
                        result["rows"][0]["status"] = "FAIL"
                    if fault != "no_file":
                        pathlib.Path(command[4]).write_text("[]" if fault == "malformed" else json.dumps(result))
                    return subprocess.CompletedProcess(command, 2 if fault == "driver_fail" else 0)
                with mock.patch.object(P.subprocess, "run", side_effect=driver):
                    code = P.main(["--out-dir", directory])
                self.assertEqual(code == 0, fault is None)
                attempt = next(pathlib.Path(directory).iterdir())
                self.assertEqual((attempt / "stdout.txt").read_bytes(), b"full driver raw stdout\n")
                self.assertEqual((attempt / "stderr.txt").read_bytes(), b"full driver raw stderr\n")
                self.assertEqual(json.loads((attempt / "receipt.json").read_text())["returncode"], code)

    def test_registered_A1_runs_wrapper(self):
        proof = HERE.parents[2] / "infrastructure/state/live_proofs/GSS_RESTRING_FIX_STYLES_UNRECONCILED.txt"
        line, = [l for l in proof.read_text().splitlines() if l.startswith("live-proof A1:")]
        self.assertIn("python.exe src/RimMandrake/GimmeSomeSlack/restring_style_proof.py", line)
        self.assertIn("--max-seconds 900", line)


if __name__ == "__main__":
    log_path = os.environ.get("GSS_RESTRING_TEST_RAW")
    if log_path:
        with open(log_path, "w", encoding="utf-8") as raw:
            with contextlib.redirect_stdout(raw), contextlib.redirect_stderr(raw):
                suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
                result = unittest.TextTestRunner(stream=raw, verbosity=2).run(suite)
        print(pathlib.Path(log_path).read_text())
        sys.exit(0 if result.wasSuccessful() else 1)
    unittest.main(verbosity=2)

