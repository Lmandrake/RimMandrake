#!/usr/bin/env python3
"""Replay transcript JSONL through the detached finish path in a temporary state directory."""
import datetime
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import detached_helper as DH


FIXTURE = Path(__file__).with_name("testdata") / "run_seconds_transcript.jsonl"
RECORDED_SIDECHAIN = Path(__file__).resolve().parents[1] / "Utils/testdata/small_real_transcript.jsonl"
START = datetime.datetime(2026, 11, 27, tzinfo=datetime.timezone.utc).timestamp()
END = START + 21
UNIT = "rm-detached-bench-run-seconds-test"
SESSION = "aaaaaaaa-0000-0000-0000-000000000001"
SUCCESS = {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"}


class RunSecondsTest(unittest.TestCase):
    def setUp(self):
        contexts = ExitStack()
        self.addCleanup(contexts.close)
        folder = Path(contexts.enter_context(tempfile.TemporaryDirectory(prefix="selftest_run_seconds_")))
        config = folder / "claude"
        contexts.enter_context(patch.dict(os.environ, {"RM_DISPATCHER_STATE": str(folder / "state"),
                                                        "CLAUDE_CONFIG_DIR": str(config)}))
        contexts.enter_context(patch.object(DH, "stop_scope", return_value="scope stopped"))
        contexts.enter_context(patch.object(DH, "filing_refusal_lines", return_value=[]))
        contexts.enter_context(patch("run_alive.run_line", return_value=""))
        self.log = folder / "conductor.md"
        clone = folder / "gone-clone"
        projects = Path(DH.project_dir(clone, config / "projects"))
        projects.mkdir(parents=True)
        self.transcript = projects / (SESSION + ".jsonl")
        shutil.copyfile(FIXTURE, self.transcript)
        self.out = folder / "result.json"
        self.out.write_text(json.dumps({"session_id": SESSION, "result": "Finished"}), encoding="utf-8")
        self.record = {"unit": UNIT, "status": "running", "at": START, "seat": "BENCH", "item": "RUN_SECONDS",
                       "clone": str(clone), "model": "sonnet", "out": str(self.out), "err": str(folder / "err"),
                       "next_act_owner": "quiet_scan"}

    def finish(self, now=END, env=SUCCESS):
        def unexpected_command(*args, **kwargs):
            self.fail("finish tried to run a command: %r" % (args,))

        code, message = DH.finish(UNIT, now=now, env=env, runner=unexpected_command, log_path=str(self.log))
        self.assertEqual(code, 0, message)
        record = DH.read_record(UNIT)
        self.assertEqual(record["status"], "finished")
        return record

    def t_tool_and_model_seconds_sum_to_the_wall_within_the_gaps(self):
        DH.write_record(dict(self.record, resume_session=SESSION))
        record = self.finish()
        tool = record.get("tool_seconds")
        model = record.get("model_seconds")
        self.assertEqual(tool, 9.5)  # 4 to 12 (overlapping calls), then 14 to 15.5
        self.assertEqual(model, 6.5)
        self.assertEqual(tool + model + 2 + 3, record["ended"] - record["at"])

    def t_an_unreadable_transcript_reads_unmeasured_never_zero(self):
        original = self.transcript.read_bytes()
        result_timestamp = b"2026-11-27T00:00:09.000Z"
        cases = {
            "empty": b"",
            "invalid JSON": original + b"{",
            "invalid UTF-8": original + b"\xff",
            "invalid timestamp": original.replace(result_timestamp, b"bad time"),
            "tool result outside the run": original.replace(result_timestamp, b"2026-11-27T00:00:29.000Z"),
        }
        for name, content in cases.items():
            with self.subTest(transcript=name):
                self.transcript.write_bytes(content)
                DH.write_record(self.record)
                record = self.finish()
                self.assertEqual(record.get("model_seconds"), "UNMEASURED")
                self.assertEqual(record.get("tool_seconds"), "UNMEASURED")
        self.transcript.unlink()
        DH.write_record(self.record)
        with patch.object(DH, "_transcript_path", return_value=str(self.transcript)):
            record = self.finish()
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), ("UNMEASURED", "UNMEASURED"))

    def t_a_malformed_transcript_with_a_late_result_still_finishes(self):
        self.out.write_text(json.dumps({"session_id": SESSION, "result_index": 1, "result": "Finished"}),
                            encoding="utf-8")
        self.transcript.write_bytes(self.transcript.read_bytes() + b"[]\n")
        DH.write_record(self.record)
        record = self.finish()
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), ("UNMEASURED", "UNMEASURED"))

    def t_a_sidechain_only_recording_has_no_main_thread_time(self):
        shutil.copyfile(RECORDED_SIDECHAIN, self.transcript)
        started = datetime.datetime(2026, 11, 6, 14, 16, tzinfo=datetime.timezone.utc).timestamp()
        DH.write_record(dict(self.record, at=started))
        record = self.finish(now=started + 180)
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), ("UNMEASURED", "UNMEASURED"))

    def t_a_run_without_tool_calls_has_zero_tool_seconds(self):
        messages = [row for row in self.transcript.read_text(encoding="utf-8").splitlines(keepends=True)
                    if '"tool_use"' not in row and '"tool_result"' not in row]
        self.transcript.write_text("".join(messages), encoding="utf-8")
        DH.write_record(self.record)
        record = self.finish()
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), (16, 0))

    def t_the_run_record_carries_both(self):
        DH.write_record(self.record)
        record = self.finish()
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), (6.5, 9.5))
        self.transcript.unlink()
        self.assertEqual(self.finish(now=END + 60), record)

    def t_a_killed_run_uses_its_recorded_end(self):
        self.out.unlink()
        DH.write_record(dict(self.record, session=SESSION))
        DH.mark_killed(UNIT, "selftest", now=END)
        record = DH.read_record(UNIT)
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), (6.5, 9.5))
        record = self.finish(now=END + 60, env={"SERVICE_RESULT": "signal"})
        self.assertEqual(record["ended"], END)
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), (6.5, 9.5))

    def t_the_remote_record_keeps_the_hosts_measurement(self):
        DH.write_record(self.record)
        finished = self.finish()
        with patch("run_host.remote_status", return_value=("finished", finished)):
            DH.remote_live_status(dict(self.record, host="stevedesktop"))
        record = DH.read_record(UNIT)
        self.assertEqual((record.get("model_seconds"), record.get("tool_seconds")), (6.5, 9.5))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.testMethodPrefix = "t_"
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(loader.loadTestsFromTestCase(RunSecondsTest))
    if not result.wasSuccessful():
        raise SystemExit(1)
    print("PASS detached run seconds")
