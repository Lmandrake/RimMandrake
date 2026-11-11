#!/usr/bin/env python3
"""Offline tests of the actual M22 production rows, probe transport and executable launcher. No live proof."""
import ast
import copy
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validation_aerial as A
import kinetic_sway_proof as P
import restring_style_proof as L


class Bridge:
    def __init__(self, change=None):
        self.change = change or (lambda phase, reply: None)
        self.serial = 0
        self.sways, self.cuts = 7, 4  # cumulative counts deliberately nonzero in both arms
        self.enabled = True
        self.arm = 0
        self.exploded = False
        self.calls = []

    def scene(self, *_):
        self.arm += 1
        self.exploded = False
        return self.arm * 2, self.arm * 2 + 1, True

    def ticks(self, count):
        self.calls.append(("ticks", count))

    def call(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return {"success": True}

    def ap(self, cmd):
        self.calls.append(cmd)
        self.serial += 1
        reply = {"success": True, "cmd": cmd, "_probeSerial": self.serial}
        if cmd.startswith("set:"):
            self.enabled = cmd.endswith("True")
            reply["value"] = str(self.enabled)
            phase = "set"
        elif cmd.startswith("explode:"):
            self.exploded = True
            delta = int(self.enabled)
            self.sways += delta
            reply.update(cuts=0, sways=delta, damageDef=A.KINETIC_DAMAGE, synthetic=False,
                         kinetic=True, harmsHealth=True, spansReached=1)
            phase = "explode"
        elif cmd == "census":
            left, right = self.arm * 2, self.arm * 2 + 1
            reply.update(kineticSways=self.sways, explosionCuts=self.cuts,
                         settings={k: str(self.enabled) if k == "kineticSway" else "True" for k in
                                   ("kineticSway", "dripLoops", "cutWiresOnOwnerChange", "keepWiresOnGravship")},
                         anchors=[{"id": pid, "x": pos[0], "z": pos[1], "net": 11,
                                   "links": [{"other": other, "state": "Up", "hp": 30.0}]}
                                  for pid, pos, other in ((left, A.F1, right), (right, A.F2, left))])
            phase = "after" if self.exploded else "before"
        else:
            raise AssertionError(cmd)
        self.change(phase, reply)
        return reply


def run_rows(bridge):
    rows = []
    with mock.patch.object(A, "_scene_pair", side_effect=bridge.scene):
        A.kinetic_sway_rows(bridge, rows)
    return rows


class Rows(unittest.TestCase):
    def test_real_path_and_cumulative_isolation(self):
        b = Bridge()
        rows = run_rows(b)
        self.assertEqual([r["id"] for r in rows], list(A.KINETIC_ROWS))
        self.assertEqual([r["status"] for r in rows], ["PASS", "PASS"], rows)
        self.assertEqual([r["detail"]["censusSwayDelta"] for r in rows], [1, 0])
        self.assertEqual(b.arm, 2)
        self.assertNotEqual(rows[0]["detail"]["anchors"], rows[1]["detail"]["anchors"])
        self.assertEqual(b.calls.count("explode:98,135,2.5,50," + A.KINETIC_DAMAGE), 2)
        self.assertFalse(any(isinstance(c, str) and c.endswith(",kinetic") for c in b.calls))
        self.assertGreater(rows[1]["detail"]["readings"][-1]["reply"]["kineticSways"], 0)
        for row in rows:
            self.assertEqual(row["class"], "MOD")
            self.assertEqual(row["detail"]["setting"], "kineticSway")

    def reject(self, phase, change):
        def edit(current, reply):
            if current == phase:
                change(reply)
        rows = run_rows(Bridge(edit))
        self.assertTrue(all(r["status"] != "PASS" for r in rows), rows)

    def test_all_calls_require_success_echo_and_fresh_serial(self):
        for phase in ("set", "before", "explode", "after"):
            for key, bad in (("success", False), ("success", 1), ("cmd", "old request"),
                             ("_probeSerial", None), ("_probeSerial", True), ("_probeSerial", "3"), ("_probeSerial", 0)):
                with self.subTest(phase=phase, key=key, bad=bad):
                    self.reject(phase, lambda r: r.update({key: bad}))

    def test_counters_and_setting_reads(self):
        for phase in ("before", "after"):
            for key in ("kineticSways", "explosionCuts"):
                for bad in (None, True, "0", 0.0, -1):
                    with self.subTest(phase=phase, key=key, bad=bad):
                        self.reject(phase, lambda r: r.update({key: bad}))
                self.reject(phase, lambda r: r.pop(key))
            for bad in (None, {}, {"kineticSway": True}, {"kineticSway": "not read"}):
                self.reject(phase, lambda r: r.update(settings=bad))
        self.reject("set", lambda r: r.update(value=False))
        self.reject("set", lambda r: r.update(value="not read"))
        for key in ("cuts", "sways"):
            for bad in (None, True, "0", 0.0, -1):
                self.reject("explode", lambda r: r.update({key: bad}))
            self.reject("explode", lambda r: r.pop(key))

    def test_wrong_def_synthetic_fallback_and_cut(self):
        for key, bad in (("damageDef", "Bomb"), ("damageDef", None), ("synthetic", True),
                         ("synthetic", 0), ("synthetic", None), ("cuts", 1), ("kinetic", False),
                         ("kinetic", 1), ("harmsHealth", False), ("spansReached", 0),
                         ("spansReached", True), ("spansReached", "1")):
            self.reject("explode", lambda r: r.update({key: bad}))
        self.reject("after", lambda r: r.update(explosionCuts=r["explosionCuts"] + 1))

    def test_connected_span_is_required_both_directions_before_and_after(self):
        mutations = [lambda r: r.update(anchors=None), lambda r: r.update(anchors=[]),
                     lambda r: r["anchors"].append(copy.deepcopy(r["anchors"][0])),
                     lambda r: r["anchors"][1].update(net=22), lambda r: r["anchors"][1].update(net=True),
                     lambda r: r["anchors"][1].update(links=[]), lambda r: r["anchors"][1].update(x=999),
                     lambda r: r["anchors"][1]["links"][0].update(hp=None),
                     lambda r: r["anchors"][1]["links"][0].update(hp=True),
                     lambda r: r["anchors"][1]["links"][0].update(hp=float("nan")),
                     lambda r: r["anchors"][1]["links"][0].update(state="Cut"),
                     lambda r: r["anchors"][1]["links"].append(copy.deepcopy(r["anchors"][1]["links"][0]))]
        for phase in ("before", "after"):
            for mutation in mutations:
                self.reject(phase, mutation)
        def wound(phase, reply):
            if phase == "after":
                for a in reply["anchors"]: a["links"][0]["hp"] -= 1
        self.assertTrue(all(r["status"] == "FAIL" for r in run_rows(Bridge(wound))))

    def test_same_input_stale_census_and_inverted_setting(self):
        saved = {}
        def stale(phase, reply):
            if phase == "before":
                saved.update(copy.deepcopy(reply))
            if phase == "after":
                reply.clear()
                reply.update(saved)
        self.assertTrue(all(r["status"] == "FAIL" for r in run_rows(Bridge(stale))))
        rows = run_rows(Bridge(lambda phase, r: r["settings"].update(kineticSway="False" if r["settings"]["kineticSway"] == "True" else "True")
                               if phase in ("before", "after") else None))
        self.assertTrue(all(r["status"] == "FAIL" for r in rows))

    def test_zero_on_and_positive_off_deltas_fail(self):
        def zero_on(phase, reply):
            if phase == "after":
                reply["kineticSways"] = 7
        self.assertEqual(run_rows(Bridge(zero_on))[0]["status"], "FAIL")
        def sway_off(phase, reply):
            if phase == "after":
                reply["kineticSways"] += 1
        self.assertEqual(run_rows(Bridge(sway_off))[1]["status"], "FAIL")

    def test_production_wiring_and_existing_cleanup(self):
        tree = ast.parse(Path(A.__file__).read_text())
        four, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_four_switches"]
        self.assertEqual(sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "kinetic_sway_rows"
                             for n in ast.walk(four)), 1)
        b = Bridge()
        b.enabled = False
        with mock.patch.object(A, "_four_switches", side_effect=RuntimeError("arm failed")):
            with self.assertRaisesRegex(RuntimeError, "arm failed"):
                A.four_switches_block(b, [], {})
        self.assertIn("set:kineticSway=False", b.calls)

    def test_xml_definition_and_inherited_marker(self):
        import xml.etree.ElementTree as ET
        defs = ET.parse(HERE.parent / "KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml").getroot()
        real, = [d for d in defs if d.findtext("defName") == A.KINETIC_DAMAGE]
        parent, = [d for d in defs if d.get("Name") == real.get("ParentName")]
        self.assertIsNotNone(parent.find("modExtensions/li[@Class='RimMandrake.KineticArms.RM_KineticBlastExtension']"))


class Transport(unittest.TestCase):
    def read(self, replies):
        bridge = object.__new__(A.A)
        bridge.call = mock.Mock(side_effect=replies)
        return bridge.ap("census", wait_s=0.01)

    def test_real_transport_reports_serial_and_requires_stable_successful_matching_read(self):
        def sequence():
            return [{"success": True, "value": "9"}, {"success": True}, {"success": True, "value": "10"},
                    {"success": True, "value": json.dumps({"success": True, "cmd": "census"})},
                    {"success": True, "value": "10"}]
        self.assertEqual(self.read(sequence())["_probeSerial"], 10)
        for index, replacement in ((0, {"success": False, "value": 9}), (0, {"success": True, "value": True}),
                                   (2, {"success": True, "value": None}), (3, {"success": False, "value": "{}"}),
                                   (3, {"success": True, "value": json.dumps({"success": True, "cmd": "other"})}),
                                   (4, {"success": True, "value": "11"})):
            replies = sequence()
            replies[index] = replacement
            try:
                result = self.read(replies)
            except ValueError:
                continue
            self.assertIsNot(result.get("success"), True)


class Command(unittest.TestCase):
    def result(self):
        return {"script": "validation_aerial.py", "mode": "flips", "rows": run_rows(Bridge())}

    def test_both_exact_fresh_mod_rows(self):
        valid = self.result()
        bad = [[], {}, dict(valid, mode="live"), dict(valid, aborted="dead"), dict(valid, rows=[]),
               dict(valid, rows=valid["rows"][:1]), dict(valid, rows=valid["rows"] * 2)]
        for index in (0, 1):
            for field, value in (("id", A.KINETIC_ROWS[index] + "_old"), ("status", "FAIL"),
                                 ("status", "UNMEASURED"), ("class", "HARNESS"), ("detail", {})):
                changed = copy.deepcopy(valid)
                changed["rows"][index][field] = value
                bad.append(changed)
            for field, value in (("synthetic", True), ("damageDef", "Bomb"), ("kinetic", False), ("harmsHealth", False),
                                 ("spansReached", 0), ("censusSwayDelta", True), ("settingAfter", "unknown"),
                                 ("censusCutDelta", 1), ("spanStillUp", False)):
                changed = copy.deepcopy(valid)
                changed["rows"][index]["detail"][field] = value
                bad.append(changed)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aerial.json"
            with self.assertRaises(ValueError):
                P.check_result(path, 0, time.time())
            for result in [valid, *bad]:
                path.write_text(json.dumps(result))
                stamp = path.stat().st_mtime
                if result is valid:
                    self.assertEqual(len(P.check_result(path, stamp - 1, stamp + 1)), 2)
                else:
                    with self.assertRaises(ValueError):
                        P.check_result(path, stamp - 1, stamp + 1)
            path.write_text(json.dumps(valid))
            stamp = path.stat().st_mtime
            for start, end in ((stamp + 1, stamp + 2), (stamp - 2, stamp - 1)):
                with self.assertRaises(ValueError):
                    P.check_result(path, start, end)

    def test_actual_launcher_retains_all_attempts_and_requires_driver_success(self):
        for fault in (None, "driver_fail", "missing", "malformed", "timeout", "row_fail", "one_row", "duplicate"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                def driver(command, **kwargs):
                    self.assertEqual(command[2:4], ["--flips", "--out"])
                    self.assertEqual(kwargs["timeout"], 900)
                    kwargs["stdout"].write(b"raw stdout\n")
                    kwargs["stderr"].write(b"raw stderr\n")
                    if fault == "timeout":
                        raise subprocess.TimeoutExpired(command, 900)
                    result = self.result()
                    if fault == "row_fail": result["rows"][1]["status"] = "FAIL"
                    if fault == "one_row": result["rows"] = result["rows"][:1]
                    if fault == "duplicate": result["rows"] *= 2
                    if fault != "missing":
                        Path(command[4]).write_text("[]" if fault == "malformed" else json.dumps(result))
                    return subprocess.CompletedProcess(command, 2 if fault == "driver_fail" else 0)
                with mock.patch.object(L.subprocess, "run", side_effect=driver):
                    code = P.main(["--out-dir", directory])
                self.assertEqual(code == 0, fault is None)
                attempt, = Path(directory).iterdir()
                self.assertEqual((attempt / "stdout.txt").read_bytes(), b"raw stdout\n")
                self.assertEqual((attempt / "stderr.txt").read_bytes(), b"raw stderr\n")
                self.assertEqual(json.loads((attempt / "receipt.json").read_text())["returncode"], code)

    def test_registered_line_runs_executable_with_both_mods(self):
        root = HERE.parents[2]
        sys.path.insert(0, str(HERE.parent / "rimflow"))
        import relentless_live_round as RR
        import relentless_live as RL
        text = (root / "infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt").read_text()
        command = RR.proof_lines(text)["A2"]
        mods = [m.group("mods") for m in map(RR.LIVE_MODS.match, text.splitlines()) if m]
        self.assertEqual(mods, ["GimmeSomeSlack, KineticArms"])
        rules = json.loads((HERE.parent / "rimflow/relentless_rules.json").read_text())
        self.assertIsNone(RL.refused_proof(RL.live_rules(rules), "GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC", "", command))
        # Execute the registered shell line locally. Only its live child is replaced by an offline driver.
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            result = work / "fixture.json"
            result.write_text(json.dumps(self.result()))
            stub = work / "validation_aerial.py"
            stub.write_text('KINETIC_DAMAGE = ' + repr(A.KINETIC_DAMAGE) + '\nKINETIC_ROWS = ' + repr(A.KINETIC_ROWS) + '\n'
                            'if __name__ == "__main__":\n'
                            ' import os,sys,pathlib\n p=pathlib.Path(sys.argv[sys.argv.index("--out")+1])\n'
                            ' p.write_text(pathlib.Path(os.environ["KINETIC_FIXTURE"]).read_text())\n'
                            ' sys.exit(int(os.environ["KINETIC_EXIT"]))\n')
            for filename in ("kinetic_sway_proof.py", "restring_style_proof.py"):
                (work / filename).write_bytes((HERE / filename).read_bytes())
            line = command.replace("python.exe", shlex.quote(sys.executable)).replace(
                "src/RimMandrake/GimmeSomeSlack/kinetic_sway_proof.py", shlex.quote(str(work / "kinetic_sway_proof.py"))).replace(
                "D:/ClaudeWork/rimmandrake/scratch/gss_kinetic_sway", shlex.quote(str(work / "attempts")))
            for exitcode in (0, 2):
                child = subprocess.run(["bash", "-c", line], cwd=work, capture_output=True, text=True, timeout=30,
                                       env=dict(os.environ, KINETIC_FIXTURE=str(result), KINETIC_EXIT=str(exitcode)))
                self.assertEqual(child.returncode == 0, exitcode == 0, child.stdout + child.stderr)


if __name__ == "__main__":
    log = os.environ.get("GSS_KINETIC_TEST_LOG")
    if log:
        import contextlib
        with open(log, "x") as raw, contextlib.redirect_stdout(raw), contextlib.redirect_stderr(raw):
            suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
            result = unittest.TextTestRunner(stream=raw, verbosity=2).run(suite)
        print(Path(log).read_text())
        sys.exit(0 if result.wasSuccessful() else 1)
    unittest.main(verbosity=2)
