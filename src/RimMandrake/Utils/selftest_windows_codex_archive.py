#!/usr/bin/env python3
"""windows_codex_archive.py on made-up folders: what moves, what stays, the way back, and when it may be deleted."""
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import windows_codex_archive as W


class T(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.t = Path(t.name)
        self.p, self.a, self.log = self.t / "profile", self.t / "archive", self.t / "log"
        for d in (".codex", ".codex_workers/artpipe/w0", ".codex_bacta_fluid", ".codex_sandbox_seed.bak-0.153.4",
                  ".codex_sandbox_backup_20261123T172153Z", ".codexfoo", "Documents", "AppData/Local/OpenAI/Codex"):
            (self.p / d).mkdir(parents=True)
            (self.p / d / "f").write_text(d)
        self.log.mkdir()
        e = mock.patch.dict(os.environ, {"WINDOWS_CODEX_PROFILE": str(self.p), "WINDOWS_CODEX_ARCHIVE": str(self.a),
                                         "GPT_DOOR_LOG_DIR": str(self.log)})
        e.start()
        self.addCleanup(e.stop)

    def run_(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()) as o:
            rc = W.main(list(argv))
        return rc, o.getvalue()

    def rec(self, outcome, t=None):
        t = time.time() + 1 if t is None else t
        d = self.log / "2026-11-30"
        d.mkdir(exist_ok=True)
        (d / ("%s%d.json" % (outcome, len(list(d.iterdir()))))).write_text(json.dumps(
            {"t": t, "outcome": outcome, "caller": "somebody"}))

    def tree(self):
        return {str(f.relative_to(self.p)): f.read_text() for f in self.p.rglob("*") if f.is_file()}

    def test_plan_changes_nothing_and_names_what_stays(self):
        before = self.tree()
        rc, o = self.run_("plan")
        self.assertEqual((rc, o.count("MOVE ")), (0, 4))
        self.assertIn("STAY %s" % (self.p / ".codex"), o)
        self.assertEqual((self.tree(), self.a.exists()), (before, False))

    def test_move_then_restore_is_byte_identical(self):
        before = self.tree()
        self.assertEqual(self.run_("move")[0], 0)
        self.assertEqual(sorted(x.name for x in self.p.iterdir()), [".codex", ".codexfoo", "AppData", "Documents"])
        self.assertEqual({r["state"] for r in W.manifest(self.a)["rows"].values()}, {"MOVED"})
        self.assertEqual(self.run_("move")[0], 0)                       # again: nothing to do
        self.assertEqual(self.run_("restore")[0], 0)
        self.assertEqual(self.tree(), before)

    def test_a_move_that_stops_is_named_and_carries_on(self):
        def half(src, dst):
            dst.mkdir(parents=True, exist_ok=True)
            raise OSError("the disk went away")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(W.move(self.p, self.a, [".codex_workers"], half), 1)
        row = W.manifest(self.a)["rows"][".codex_workers"]
        self.assertEqual((row["state"], row["why"]), ("PARTIAL", "the disk went away"))
        self.assertTrue((self.p / ".codex_workers/artpipe/w0/f").is_file())
        (self.a / ".codex_workers").rmdir()
        self.assertEqual(self.run_("move")[0], 0)
        self.assertEqual(W.manifest(self.a)["rows"][".codex_workers"]["state"], "MOVED")

    def test_files_left_behind_are_never_called_moved(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(W.move(self.p, self.a, [".codex_workers"], lambda s, d: d.mkdir(parents=True)), 1)
        self.assertEqual(W.manifest(self.a)["rows"][".codex_workers"]["state"], "PARTIAL")

    def test_restore_never_overwrites_a_folder_that_came_back(self):
        self.run_("move")
        (self.p / ".codex_bacta_fluid").mkdir()
        (self.p / ".codex_bacta_fluid/new").write_text("mine")
        rc, o = self.run_("restore")
        self.assertEqual(rc, 1)
        self.assertIn("REFUSED .codex_bacta_fluid", o)
        self.assertEqual((self.p / ".codex_bacta_fluid/new").read_text(), "mine")

    def test_delete_waits_a_week_and_for_no_calls(self):
        self.run_("move")
        self.rec("ANSWERED")
        self.assertIn("left", W.delete_refusal(self.a))
        later = time.time() + 8 * 86400
        self.assertEqual(W.delete_refusal(self.a, later), "")
        self.rec("WINDOWS_RETIRED")
        self.assertIn("somebody", W.delete_refusal(self.a, later))
        self.assertEqual(self.run_("delete")[0], 1)
        self.assertTrue(self.a.exists())

    def test_a_blind_reader_is_unmeasured_never_zero(self):
        self.run_("move")
        self.rec("ANSWERED", t=time.time() - 30 * 86400)               # only calls from before the move
        later = time.time() + 8 * 86400
        self.assertIn("UNMEASURED", W.delete_refusal(self.a, later))
        self.assertEqual(self.run_("status")[0], 2)
        self.assertIn("UNMEASURED", W.delete_refusal(self.a, later, self.t / "absent"))

    def test_an_old_call_does_not_count(self):
        self.run_("move")
        self.rec("ANSWERED")
        self.rec("WINDOWS_RETIRED", t=time.time() - 86400)
        self.assertEqual(W.calls(self.a)[0], 0)

    def test_a_declared_probe_is_named_and_not_counted_and_only_that_one(self):
        self.run_("move")
        self.rec("ANSWERED")
        self.rec("WINDOWS_RETIRED")
        f = next(self.log.rglob("WINDOWS_RETIRED*"))
        f.write_text(json.dumps(dict(json.loads(f.read_text()), id="probe-1")))
        self.assertEqual(self.run_("probe", "--id", "probe-1")[0], 1)              # no reason: refused
        self.assertEqual(self.run_("probe", "--id", "nothing", "--why", "x")[0], 1)     # no such call
        self.assertEqual(W.calls(self.a)[0], 1)
        self.assertEqual(self.run_("probe", "--id", "probe-1", "--why", "my own proof call")[0], 0)
        self.assertEqual(W.calls(self.a)[0], 0)
        self.assertIn("probe-1: my own proof call", self.run_("status")[1])
        self.rec("WINDOWS_RETIRED")
        self.assertEqual(W.calls(self.a)[0], 1)

    def test_the_live_app_folder_can_never_match(self):
        for n in (".codex", ".codex_", ".codexfoo", "codex_workers", ".codex_workers2", ".codex_sandbox", "AppData"):
            self.assertFalse(W.TAKES.match(n), n)


if __name__ == "__main__":
    unittest.main()
