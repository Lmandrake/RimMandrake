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
import maturation_autonomy as MA


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
        with patch.object(AR.CX, "wsl_to_win", side_effect=lambda p: "WIN:" + str(p)), patch.dict(os.environ, {"RM_CODEX_SIDE": "win"}, clear=True):
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


    def test_killed_run_usage_is_read(self):
        """RIMMANDRAKE_READ_CODEX_SPEND_OF_A_KILLED_DESIGNER_RUN: a run that times out, or a unit stopped before it
        printed its result line, still reads the usage of every turn it completed."""
        ev = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 70, "output_tokens": 9}}) + "\n"
        with tempfile.TemporaryDirectory() as d:
            def slow(argv, **kw):
                kw["stdout"].write(ev)
                kw["stdout"].flush()
                raise subprocess.TimeoutExpired(argv, 5)
            with patch.object(AR.CX, "on_windows_drive", return_value=True), patch.object(AR, "launch_argv", return_value=["codex", "exec", "-"]):
                res = AR.run(d, "p", Path(d)/"last", Path(d)/"events", Path(d)/"spend", invoke=slow, meter=meter())
            self.assertTrue(res["is_error"])
            self.assertEqual(res["codex_usage"], {"input_tokens": 70, "output_tokens": 9})
            self.assertEqual(json.loads((Path(d)/"spend").read_text())["usage"], {"input_tokens": 70, "output_tokens": 9})
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "rm-role-designer-1.json")
            run = {"out": out, "runner": "codex"}
            self.assertEqual(RL.codex_usage(run, {}), "UNMEASURED")
            Path(out + ".events.jsonl").write_text(ev + ev)
            self.assertEqual(RL.codex_usage(run, {}), {"input_tokens": 140, "output_tokens": 18})
            Path(out + ".spend.json").write_text(json.dumps({"usage": {"input_tokens": 1, "output_tokens": 2}}))
            self.assertEqual(RL.codex_usage(run, {}), {"input_tokens": 1, "output_tokens": 2})
            self.assertEqual(RL.codex_usage(run, {"codex_usage": {"input_tokens": 5, "output_tokens": 6}}),
                             {"input_tokens": 5, "output_tokens": 6})
            self.assertEqual(RL.codex_usage({"runner": "codex"}, {"codex_usage": "UNMEASURED"}), "UNMEASURED")


    def test_concept_runner_and_lanes(self):
        """A concept init'ed --runner codex is launched on Codex by the tick's own sweep, on the Codex lane only;
        the Claude lane leaves it alone, and an unset runner stays the Claude lane's."""
        with tempfile.TemporaryDirectory() as d:
            st = DS.init(os.path.join(d, "M"), "M", runner="codex")
            self.assertEqual(DS.load_state(os.path.join(d, "M"))["runner"], "codex")
            with self.assertRaises(DS.Refused):
                DS.init(os.path.join(d, "N"), "N", runner="gpt")
        rows = lambda: [("/c/M", {"status": "ready", "stage": 0, "runner": "codex"}, 0),
                        ("/c/G", {"status": "ready", "stage": 1}, 0)]
        base = {"chain_stages": True, "ledger_item": "fixture"}
        codex = RL.chain_sweep("DesignerCodex", {}, dict(base, runner="codex", sweeps_runner="codex"), 10000,
                               lambda **kw: None, rows)
        self.assertEqual([(q["concept"], q["runner"]) for q in codex], [("/c/M", "codex")])
        claude = RL.chain_sweep("Designer", {}, dict(base, sweeps_runner="claude"), 10000, lambda **kw: None, rows)
        self.assertEqual([q["concept"] for q in claude], ["/c/G"])
        self.assertEqual(len(RL.chain_sweep("Designer", {}, base, 10000, lambda **kw: None, rows)), 2)


    def test_draft_is_input_to_verify(self):
        """RIMMANDRAKE_SEED_DESIGNER_WITH_A_DRAFT_TO_VERIFY: a concept seeded with another model's draft names it in the
        stage 0-3 packets as input to verify, sha-checked; a changed draft is said, stage 4 does not carry it."""
        with tempfile.TemporaryDirectory() as d:
            dr = os.path.join(d, "M.designer_draft.md")
            Path(dr).write_text("draft")
            c = os.path.join(d, "M")
            st = DS.init(c, "M", runner="codex", draft=dr, draft_by="Codex lane E")
            self.assertEqual(st["draft_input"]["path"], dr)
            line = DS.draft_line(st)
            self.assertIn("DRAFT TO VERIFY", line)
            self.assertIn(dr, line)
            self.assertIn("unchanged since init", line)
            self.assertIn("DRAFT TO VERIFY", DS.packet(c, dict(st, stage=3), {}, 1000))
            self.assertIsNone(DS.draft_line(dict(st, stage=4)))
            Path(dr).write_text("edited")
            self.assertIn("CHANGED since init", DS.draft_line(st))
            os.remove(dr)
            self.assertIn("UNREADABLE", DS.draft_line(st))
            self.assertIsNone(DS.draft_line(DS.init(os.path.join(d, "N"), "N")))
            with self.assertRaises(DS.Refused):
                DS.init(os.path.join(d, "P"), "P", draft=os.path.join(d, "missing.md"))


    def test_codex_exam_helpers_on_claude(self):
        """RIMMANDRAKE_START_CODEX_DESIGNER_EXAMINERS_ON_CLAUDE: a Codex concept's stage 4 packet starts its helpers on
        Claude; a Claude concept's, or a Codex concept at another stage, carries no such line."""
        with tempfile.TemporaryDirectory() as d:
            c = os.path.join(d, "M")
            st = DS.init(c, "M", runner="codex")
            text = DS.packet(c, dict(st, stage=4), {}, 1000)
            self.assertIn("claude_bounded.sh -p --model opus", text)
            self.assertIn("Never play a helper yourself", text)
            self.assertIsNone(DS.helper_line(dict(st, stage=3)))
            self.assertIsNone(DS.helper_line(dict(st, stage=4, runner="claude")))
            self.assertIsNone(DS.helper_line({"stage": 4}))


    def test_maturation_sees_the_codex_lane(self):
        """The pipeline's Designer reading sees a DesignerCodex run live on its concept (it read only the Claude lane
        and called LeaningScrub's live Codex run 'waiting on nothing running', 2026-11-15 17:14 PST)."""
        import doorbell
        with tempfile.TemporaryDirectory() as d:
            line = lambda role, unit, mod: json.dumps({"blind": {"outcome": "launched", "role": role, "unit": unit},
                                                       "concept": "/x/design/concepts/" + mod, "do": "role_launch"})
            Path(d, "journal.jsonl").write_text("\n".join([line("Designer", "u-claude", "Other"),
                                                           line("DesignerCodex", "u-codex", "M"),
                                                           line("Designerish", "u-bad", "Z")]) + "\n")
            active = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "active\ninactive\n", "")
            with patch.object(doorbell, "state_dir", return_value=d), patch.object(MA.subprocess, "run", side_effect=active):
                self.assertEqual(MA.designer_unit("M"), "u-codex")
                self.assertNotEqual(MA.designer_unit("Z"), "u-bad")      # not a Designer lane
                self.assertIn("the Designer slot", MA.designer_unit("Nobody"))


if __name__ == "__main__":
    unittest.main()
