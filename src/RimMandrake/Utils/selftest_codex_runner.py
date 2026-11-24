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

    # stale-meter refresh: a stale ESTIMATE weekly % is cured by ONE probe + re-read, never looped
    @staticmethod
    def stale():
        return {"codex.week_used_pct": {"m": "ESTIMATE", "v": 29.0}, "codex.hours_to_reset": {"m": "MEASURED", "v": 24}}

    @staticmethod
    def seq(*readings):
        it = iter(readings)
        calls = []
        def reader():
            calls.append(1)
            return next(it)
        return reader, calls

    def test_stale_probe_gives_measured_passes(self):
        reader, reads = self.seq(self.stale(), meter(29))
        probes = []
        self.assertEqual(AR.quota_gate(probe=lambda: probes.append(1), reader=reader), meter(29))
        self.assertEqual((len(probes), len(reads)), (1, 2))

    def test_stale_failing_probe_refuses_naming_probe(self):
        reader, _ = self.seq(self.stale())
        def boom():
            raise RuntimeError("codex exited 1")
        with self.assertRaises(AR.Refused) as c:
            AR.quota_gate(probe=boom, reader=reader)
        self.assertIn("probe failed", str(c.exception))
        self.assertIn("codex exited 1", str(c.exception))

    def test_stale_probe_timeout_refuses_naming_probe(self):
        reader, _ = self.seq(self.stale())
        def slow():
            raise subprocess.TimeoutExpired("gpt_consult", 150)
        with self.assertRaises(AR.Refused) as c:
            AR.quota_gate(probe=slow, reader=reader)
        self.assertIn("probe failed", str(c.exception))

    def test_stale_probe_leaves_estimate_refuses_once(self):
        reader, reads = self.seq(self.stale(), self.stale(), self.stale())
        probes = []
        with self.assertRaises(AR.Refused) as c:
            AR.quota_gate(probe=lambda: probes.append(1), reader=reader)
        self.assertIn("still not MEASURED", str(c.exception))
        self.assertEqual((len(probes), len(reads)), (1, 2))

    def test_fresh_never_probes(self):
        reader, _ = self.seq(meter(40))
        self.assertEqual(AR.quota_gate(probe=lambda: self.fail("probed a fresh reading"), reader=reader), meter(40))

    def test_over_90_after_probe_still_refuses(self):
        reader, _ = self.seq(self.stale(), meter(95))
        with self.assertRaises(AR.Refused) as c:
            AR.quota_gate(probe=lambda: None, reader=reader)
        self.assertIn("exceeds 90%", str(c.exception))

    def test_unreadable_not_stale_never_probes(self):
        bad = ({}, {**meter(), "codex.week_used_pct": {"m": "MEASURED", "v": None}},
               {**meter(), "codex.week_used_pct": {"m": "MEASURED", "v": -1}},
               {**meter(), "codex.week_used_pct": {"m": "MEASURED", "v": float("nan")}},
               {**meter(), "codex.week_used_pct": {"m": "ESTIMATE", "v": float("nan")}},
               {**meter(), "codex.week_used_pct": {"m": "ESTIMATE", "v": -3}},
               {"codex.week_used_pct": {"m": "UNMEASURED", "v": None}, "codex.hours_to_reset": {"m": "UNMEASURED", "v": None}})
        for p in bad:
            reader, _ = self.seq(p)
            with self.assertRaises(AR.Refused) as c:
                AR.quota_gate(probe=lambda: self.fail("probed an unfixable reading"), reader=reader)
            self.assertIn("unreadable", str(c.exception))

    def test_explicit_snapshot_without_probe_not_probed(self):
        with patch.object(AR, "codex_probe", side_effect=AssertionError("probed")):
            with self.assertRaises(AR.Refused):
                AR.quota_gate(self.stale())

    @staticmethod
    def result(outcome="ANSWERED", **kw):
        """A door result (Dispatch's door_agent.AgentResult), planted."""
        door = AR.dispatch_door.load("door_agent")
        return door.AgentResult(outcome, door.D.EXIT[outcome], **kw)

    def test_arguments_reach_the_door(self):
        with tempfile.TemporaryDirectory() as d:
            seen = {}
            def call(prompt, cwd, **kw):
                seen.update(kw, prompt=prompt, cwd=cwd)
                return self.result(text="done")
            with patch.dict(os.environ, {"CODEX_MODEL": "", "CODEX_EFFORT": ""}):
                res = AR.run(d, "native prompt", Path(d)/"last", Path(d)/"events", Path(d)/"spend", call=call, meter=meter())
            self.assertFalse(res["is_error"], res)
            self.assertEqual((seen["prompt"], seen["cwd"], seen["model"], seen["effort"], seen["home"], seen["timeout"]),
                             ("native prompt", Path(d).resolve(), "inherit", "high", None, 7200))
            AR.run(d, "p", Path(d)/"last", Path(d)/"events", Path(d)/"spend", call=call, meter=meter(),
                   model="configured-model", effort="medium", sandbox="read-only")
            self.assertEqual((seen["model"], seen["effort"], seen["sandbox"]), ("configured-model", "medium", "read-only"))

    def test_an_old_result_is_never_this_runs_answer(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "last").write_text("yesterday's answer")
            AR.run(d, "p", Path(d)/"last", Path(d)/"events", Path(d)/"spend", meter=meter(),
                   call=lambda *a, **k: self.result("DEADLINE"))
            self.assertFalse(Path(d, "last").exists())

    def test_door_failure_kinds_are_errors_by_name(self):
        for outcome, kw, kind in (("AUTH", {}, "failed"), ("DEADLINE", {}, "no_answer_in_time"),
                                  ("BAD_INPUT", {"started": False}, "could_not_start"), ("MODEL_REFUSED", {}, "failed")):
            with tempfile.TemporaryDirectory() as d:
                res = AR.run(d, "p", Path(d)/"last", Path(d)/"events", Path(d)/"spend", meter=meter(),
                             call=lambda *a, **k: self.result(outcome, detail="why", **kw))
                self.assertTrue(res["is_error"])
                self.assertIn(outcome, res["result"])
                sp = json.loads((Path(d)/"spend").read_text())
                self.assertEqual((sp["outcome"], sp["kind"], sp["state"]), (outcome, kind, "failed"))

    def test_usage(self):
        ev = lambda i, o: json.dumps({"type": "turn.completed", "usage": {"input_tokens": i, "output_tokens": o}})
        self.assertEqual(AR.event_usage(ev(10, 2) + "\nnoise\n" + ev(20, 3)), {"input_tokens": 30, "output_tokens": 5})
        self.assertEqual(AR.event_usage(""), "UNMEASURED")
        self.assertEqual(AR.event_usage(ev(1, True)), "UNMEASURED")

    def test_no_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            calls = []
            def fail(prompt, cwd, **kw):
                calls.append(prompt)
                return self.result("ALLOWANCE", detail="usage limit", rc=1)
            res = AR.run(d, "injected", Path(d)/"last", Path(d)/"events", Path(d)/"spend", call=fail, meter=meter())
            self.assertTrue(res["is_error"])
            self.assertEqual(calls, ["injected"])
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
            res = AR.run(d, "prompt", Path(d)/"last", Path(d)/"events", Path(d)/"spend", call=unexpected, meter={})
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
        import form_fault as FF     # every launched brief carries the repair line (1e91cc0953)
        self.assertEqual(cmd[cmd.index("--prompt")+1], "injected\n\n" + FF.BRIEF_LINE)
        self.assertNotIn("--output-format", cmd)
        self.assertIn("from-config", cmd)
        self.assertEqual(RL.launch_role(role, {"run_now":{"runner":"codex"}})["runner"], "codex")

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


    def test_killed_run_usage_is_read(self):
        """RIMMANDRAKE_READ_CODEX_SPEND_OF_A_KILLED_DESIGNER_RUN: a run that times out, or a unit stopped before it
        printed its result line, still reads the usage of every turn it completed."""
        ev = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 70, "output_tokens": 9}}) + "\n"
        with tempfile.TemporaryDirectory() as d:
            def slow(prompt, cwd, **kw):
                Path(kw["events"]).write_text(ev)
                return self.result("DEADLINE", rc=124)
            res = AR.run(d, "p", Path(d)/"last", Path(d)/"events", Path(d)/"spend", call=slow, meter=meter())
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
        # an opened concept (its `open` row): a never-opened one is not swept at all (never_opened, ad38a70a3d)
        rows = lambda: [("/c/M", {"status": "ready", "stage": 0, "runner": "codex", "history": [{"what": "open"}]}, 0),
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


    def test_rollout_usage_of_an_unfinished_turn(self):
        """codex exec is one turn: a run killed mid-turn has no turn.completed, so its usage is read from Codex's own
        session rollout (the last token_count's running total) for the thread its events started."""
        tid = "01a1e1e6-2713-7983-8668-aac2e813aa91"
        started = json.dumps({"type": "thread.started", "thread_id": tid}) + "\n" + json.dumps({"type": "turn.started"})
        tc = lambda i, o: json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {"input_tokens": i, "cached_input_tokens": i - 1, "output_tokens": o}}}})
        with tempfile.TemporaryDirectory() as home:
            self.assertEqual(AR.rollout_usage(started, home), "UNMEASURED")       # no rollout file
            day = Path(home, "sessions", "2026", "11", "15")
            day.mkdir(parents=True)
            Path(day, "rollout-2026-11-15T17-08-39-%s.jsonl" % tid).write_text("\n".join([tc(10, 1), "junk", tc(50, 4)]))
            u = AR.rollout_usage(started, home)
            self.assertEqual((u["input_tokens"], u["output_tokens"], u["cached_input_tokens"]), (50, 4, 49))
            self.assertEqual(AR.rollout_usage(json.dumps({"type": "thread.started", "thread_id": "../../x"}), home),
                             "UNMEASURED")
            ev = Path(home, "ev.jsonl")
            ev.write_text(started)
            self.assertEqual(AR.usage_of_files(Path(home, "no-spend"), ev, home)["input_tokens"], 50)
            self.assertEqual(AR.usage_of_files(Path(home, "no-spend"), Path(home, "no-events"), home), "UNMEASURED")


    def test_codex_stop_line(self):
        """DesignerCodex holds a launch under its codex_stop_week_left_pct line (25% of the week left); a Claude role,
        an unset line, or an unmeasured or degraded reading is not held by it (the quota gate handles those)."""
        cfg = {"runner": "codex", "codex_stop_week_left_pct": 25}
        m = lambda left, **kw: dict({"state": "MEASURED", "week_left": left}, **kw)
        self.assertIn("under the 25% stop line", RL.codex_stop(cfg, m(24.9)))
        self.assertIsNone(RL.codex_stop(cfg, m(25)))
        self.assertIsNone(RL.codex_stop(dict(cfg, runner="claude"), m(1)))
        self.assertIsNone(RL.codex_stop({"runner": "codex"}, m(1)))
        self.assertIsNone(RL.codex_stop(cfg, {"state": "UNMEASURED"}))
        self.assertIsNone(RL.codex_stop(cfg, m(0.0, degraded="x")))
        sch = json.load(open(HERE.parent / "rimflow" / "dispatcher_schedule.json"))
        dc = [r for r in sch["roles"] if r.get("name") == "DesignerCodex"][0]
        self.assertEqual((dc["runner"], dc["sweeps_runner"], dc["codex_stop_week_left_pct"]), ("codex", "codex", 25))

    def test_quota_uses_newest_account_reading_from_either_home(self):
        """The account meter is the newest reading in any known session folder; readings are never added."""
        import time
        import ops_watch as ow
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {
                "RM_CODEX_SESSIONS": td + "/one:" + td + "/two", "RM_OPS_WATCH_DIR": td}):
            now = int(time.time())
            for name, age, used in (("one", 2, 66), ("two", 1, 67)):
                folder = Path(td) / name
                folder.mkdir()
                payload = {"primary": {"used_percent": 1, "window_minutes": 300, "resets_at": now + 3600},
                           "secondary": {"used_percent": used, "window_minutes": 10080, "resets_at": now + 86400}}
                (folder / "rollout-test.jsonl").write_text(json.dumps({"timestamp": now - age,
                                                                       "payload": {"rate_limits": payload}}) + "\n")
            self.assertEqual(ow.c_codex(now, ow.load_rules(), {})["codex.week_used_pct"]["v"], 67)
            # the gate's own reader, with nothing injected (a missing import here refused every real run)
            self.assertEqual(AR.quota_gate()["codex.week_used_pct"]["v"], 67)
            p = Path(td) / "one/rollout-test.jsonl"
            row = json.loads(p.read_text())
            row["timestamp"] = now
            row["payload"]["rate_limits"]["secondary"]["used_percent"] = 68
            p.write_text(json.dumps(row) + "\n")
            self.assertEqual(ow.c_codex(now, ow.load_rules(), {})["codex.week_used_pct"]["v"], 68)

    def test_the_retired_windows_route_is_refused_and_logged(self):
        import gpt_consult as gc
        for argv, env in ((["q", "--codex", "win"], ""), (["q"], "win")):
            with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"GPT_DOOR_LOG_DIR": td, "RM_CODEX_SIDE": env,
                                                                              "GPT_DOOR_CALLER": "hidden"}), \
                    patch.object(gc.codex_advice, "gate", return_value=0), patch.object(gc.door, "ask", side_effect=AssertionError("asked")):
                self.assertNotEqual(gc.cli(argv), 0)
                self.assertEqual([(r["outcome"], r["caller"]) for r in gc.door.read_log(Path(td))], [("WINDOWS_RETIRED", "hidden")])

    def test_consult_lockdown_through_the_door(self):
        """gpt_consult --lockdown asks the door with no tools, in the job folder, on the named sign-in."""
        import gpt_consult as gc
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "auth.json").write_text('{}')
            def invoke(argv, **kw):
                self.assertEqual(kw["env"]["CODEX_HOME"], str(root))
                for flag in ("--ephemeral", "--strict-config", "image_generation"):
                    self.assertIn(flag, argv)
                self.assertEqual(argv[argv.index("-C") + 1], kw["cwd"])
                Path(argv[argv.index("-o") + 1]).write_text("ok")
                return subprocess.CompletedProcess(argv, 0)
            with patch.dict(os.environ, {"CODEX_SCRATCH": td + "/scratch", "GPT_DOOR_LOG_DIR": td + "/log",
                                         "GPT_DOOR_SIDE": "linux"}), \
                    patch.object(gc.door, "find_codex", return_value="codex"), patch.object(gc.codex_advice, "gate", return_value=0), \
                    patch.object(gc, "_receipt"), patch.object(gc, "_log_call"), patch.object(gc.door, "RUNNER", invoke):
                self.assertEqual(gc.main(["q", "--codex-home", td, "--lockdown", "--effort", "low"]), 0)


if __name__ == "__main__":
    unittest.main()
