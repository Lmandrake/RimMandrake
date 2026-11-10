#!/usr/bin/env python3
"""Codex worker transport: opt-in, meter refusal, usage and unchanged stage acceptance."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import agent_runner as AR
import role_launch as RL
import designer_stage as DS
import relentless as R
import relentless_usage as RU


def meter(used=50):
    return {"codex.week_used_pct": {"m": "MEASURED", "v": used},
            "codex.hours_to_reset": {"m": "MEASURED", "v": 24}}


class CodexRunnerTests(unittest.TestCase):
    def test_quota_unreadable(self):
        for p in ({}, {**meter(), "codex.hours_to_reset": {"m": "UNMEASURED", "v": None}},
                  {**meter(), "codex.week_used_pct": {"m": "ESTIMATE", "v": 50}}):
            with self.assertRaises(AR.Refused):
                AR.quota_gate(p)

    def test_quota_over_90(self):
        with self.assertRaises(AR.Refused):
            AR.quota_gate(meter(90.1))

    def test_quota_normal(self):
        self.assertEqual(AR.quota_gate(meter(90)), meter(90))

    def test_codex_argv(self):
        with patch.object(AR.CX, "wsl_to_win", side_effect=lambda p: "WIN:" + str(p)), patch.dict(os.environ, {}, clear=True):
            a = AR.launch_argv(Path("/work"), Path("/out"), exe="codex.exe")
            self.assertEqual(a, ["codex.exe", "exec", "--sandbox", "workspace-write", "--skip-git-repo-check",
                                 "-C", "WIN:/work", "-o", "WIN:/out", "--json", "-c",
                                 'model_reasoning_effort="high"', "-"])
            a = AR.launch_argv(Path("/work"), Path("/out"), "configured-model", "medium", "read-only", "codex.exe")
            self.assertEqual(a[-3:], ["-m", "configured-model", "-"])
            self.assertIn('model_reasoning_effort="medium"', a)

    def test_usage(self):
        ev = lambda i, o: json.dumps({"type": "turn.completed", "usage": {"input_tokens": i, "output_tokens": o}})
        self.assertEqual(AR.event_usage(ev(10, 2) + "\nnoise\n" + ev(20, 3)), {"input_tokens": 30, "output_tokens": 5})
        self.assertEqual(AR.event_usage(""), "UNMEASURED")
        self.assertEqual(AR.event_usage(ev(1, True)), "UNMEASURED")

    def test_no_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            calls = []
            def fail(argv, **kw):
                calls.append((argv, kw))
                return subprocess.CompletedProcess(argv, 1, '{"type":"turn.failed","error":{"message":"quota/auth"}}', '401')
            with patch.object(AR.CX, "on_windows_drive", return_value=True), patch.object(AR, "launch_argv", return_value=["codex.exe", "exec", "-"]):
                res = AR.run(d, "injected", Path(d)/"last", Path(d)/"events", Path(d)/"spend", invoke=fail, meter=meter())
            self.assertTrue(res["is_error"])
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0][1]["input"].endswith("injected"))
            self.assertEqual(calls[0][0][0], "codex.exe")
            self.assertEqual(json.loads((Path(d)/"spend").read_text())["usage"], "UNMEASURED")
            self.assertEqual(res["runner"], "codex")
            cfg = {"chain_stages":True, "ledger_item":"fixture"}
            rows = lambda: [("concept", {"status":"ready", "stage":1, "runner":"codex"}, 0)]
            requested = RL.chain_sweep("Designer", {}, cfg, 10000, lambda **kw: None, rows)
            self.assertEqual(requested[0]["runner"], "codex")

    def test_unreadable_does_not_launch(self):
        with tempfile.TemporaryDirectory() as d:
            def unexpected(*a, **kw):
                self.fail("quota refusal still launched a process")
            res = AR.run(d, "prompt", Path(d)/"last", Path(d)/"events", Path(d)/"spend", invoke=unexpected, meter={})
            self.assertTrue(res["is_error"])
            self.assertIn("unreadable", res["result"])

    def test_designer_argv(self):
        role = {"name":"designer", "seat":"BENCH", "clone":"/clone", "model":"opus", "run_max_s":600}
        default = RL.launch_argv(role, "unit", "injected", "/out", "/err", "/bin/claude")
        self.assertIn("/clone/src/RimMandrake/Utils/claude_bounded.sh", default)
        role.update(runner="codex", codex_model="from-config", codex_effort="high")
        a = RL.launch_argv(role, "unit", "injected", "/out", "/err", "/bin/claude")
        cmd = a[a.index("--")+1:]
        self.assertEqual(cmd[:2], ["python3", "/clone/src/RimMandrake/Utils/agent_runner.py"])
        self.assertEqual(cmd[cmd.index("--prompt")+1], "injected")
        self.assertNotIn("--output-format", cmd)
        self.assertIn("from-config", cmd)
        self.assertEqual(RL.launch_role(role, {"run_now":{"runner":"codex"}})["runner"], "codex")

    def test_relentless_argv(self):
        with tempfile.TemporaryDirectory() as d:
            fx = R.Effects.__new__(R.Effects)
            fx.r = {"seat":"BENCH", "model":"sonnet", "runner":"codex"}
            fx.RL = RL
            run = {"unit":"test-codex", "out":d+"/out", "err":d+"/err"}
            with patch.object(AR, "quota_gate", return_value=meter()), patch.object(R.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as call:
                self.assertIsNone(fx.launch({}, run, "worker task", "rm-builder", d, 600, {"TMPDIR":d}))
            a = call.call_args.args[0]
            cmd = a[a.index("--")+1:]
            self.assertIn(d+"/src/RimMandrake/Utils/agent_runner.py", cmd)
            self.assertEqual(cmd[cmd.index("--agent")+1], "rm-builder")
            self.assertNotIn("--output-format", cmd)
            self.assertEqual(run["runner"], "codex")

    def test_result_validation(self):
        with tempfile.TemporaryDirectory() as d:
            concept = str(Path(d)/"concept")
            DS.init(concept, "RunnerSmoke")
            DS.open_run(concept, "invalid", repo=d)
            RL.stage_runner(concept, "invalid", "codex")
            DS.open_run(concept, "invalid", repo=d)  # simulate an interrupted run before testing its result
            self.assertEqual(DS.load_state(concept)["budget"]["spent"], 0)
            self.assertEqual(DS.load_state(concept)["runner_spend"][-1]["usage"], "UNMEASURED")
            (Path(concept)/"result.json").write_text(json.dumps({"run":"invalid", "stage":0, "outcome":"done"}))
            ok, errs = DS.close_run(concept, "invalid", repo=d, runner="codex", usage="UNMEASURED")
            self.assertFalse(ok)
            self.assertTrue(any("inventory" in e for e in errs))
            self.assertEqual(DS.load_state(concept)["budget"]["spent"], 0)
            DS.open_run(concept, "valid", repo=d)
            (Path(concept)/"result.json").write_text(json.dumps({"run":"valid", "stage":0, "outcome":"blocked", "on":"smoke fixture has no source"}))
            self.assertTrue(DS.close_run(concept, "valid", repo=d, runner="codex", usage={"input_tokens":1,"output_tokens":2})[0])
            st = DS.load_state(concept)
            self.assertEqual(st["runner_spend"][-1]["runner"], "codex")
            self.assertEqual(st["budget"]["spent"], 0)

    def test_spend_separation(self):
        self.assertEqual(RL.spent_today({"runs":[{"day":RL.day_of(1),"runner":"codex","tokens":100}]}, 1), 0)
        with patch.object(RL, "read_result", return_value={"runner":"codex","codex_usage":"UNMEASURED"}):
            self.assertEqual(RU.measure(RL, {"out":"missing"}), (0,"codex"))
        self.assertEqual(R.charge(None, {"spent":0}, 100, 0, {}, "codex-unit", basis="codex"), 0)


if __name__ == "__main__":
    unittest.main()
