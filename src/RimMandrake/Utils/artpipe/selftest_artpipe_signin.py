#!/usr/bin/env python3
"""Tests for design/specs/2026-11-24-art-daemon-over-the-one-door/boundary.md: the dead-sign-in reading and the picture
call. The daemon's promises are tested end to end in selftest_artpipe.py under the same names. Fake sign-ins only; no
network, no real Codex folder is read or written.

    python3 src/RimMandrake/Utils/artpipe/selftest_artpipe_signin.py     exit 0 all pass, 1 a failure
"""
from __future__ import annotations

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

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
os.environ.setdefault("ARTPIPE_STATE_DIR", tempfile.mkdtemp(prefix="artpipe_signin_state_"))

import imagecall  # noqa: E402
import signin_health as SH  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.t = Path(t.name)
        self.home, self.log = self.t / "home", self.t / "log"
        self.home.mkdir()
        self.log.mkdir()
        self.sign_in("rt-secret-1")

    def sign_in(self, refresh, at=None):
        f = self.home / "auth.json"
        f.write_text(json.dumps({"tokens": {"access_token": "x", "refresh_token": refresh}}))
        at = time.time() - 3600 if at is None else at
        os.utime(f, (at, at))

    def record(self, outcome, ago=60, kind="failed", home=None):
        t = time.time() - ago
        d = self.log / time.strftime("%Y-%m-%d", time.gmtime(t))
        d.mkdir(exist_ok=True)
        (d / ("%s-%d.json" % (outcome, int(ago * 1000)))).write_text(json.dumps(
            {"t": t, "secs": 3, "home": str(home or self.home), "outcome": outcome, "kind": kind}))

    def point(self, home=None, log=None):
        import ops_watch
        return ops_watch.artpipe_signin_reading(home or self.home, log or self.log)["queues.artpipe.signins_bad"]


class Health(Base):
    def test_a_dead_signin_reads_red(self):
        self.record("ANSWERED", 600, "answered")
        self.record("AUTH", 60)
        self.assertEqual(SH.check(self.home, self.log)[0], "auth_failed")
        p = self.point()
        self.assertEqual((p["m"], p["v"]), ("MEASURED", 1))
        self.assertNotIn("rt-secret", json.dumps(p))
        (self.home / "auth.json").write_text("{torn")
        self.assertEqual((SH.check(self.home, self.log)[0], self.point()["v"]), ("unreadable", 1))
        (self.home / "auth.json").unlink()
        self.assertEqual((SH.check(self.home, self.log)[0], self.point()["v"]), ("no_signin", 1))

    def test_a_live_signin_reads_green(self):
        self.assertEqual((self.point()["m"], self.point()["v"]), ("MEASURED", 0))     # no call yet: the folder decides
        self.record("ANSWERED", 60, "answered")
        self.assertEqual(self.point()["v"], 0)
        self.record("AUTH", 10, home=self.t / "another")                               # another folder's login
        self.record("AUTH", 5, kind="could_not_start")                                 # never reached the server
        self.assertEqual(self.point()["v"], 0)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = SH.main(["--home", str(self.home), "--log", str(self.log)])
        self.assertEqual(rc, 0)
        self.assertNotIn("rt-secret", out.getvalue())

    def test_a_later_answer_clears_it(self):
        self.record("AUTH", 60)
        self.assertEqual(self.point()["v"], 1)
        self.record("ANSWERED", 5, "answered")
        self.assertEqual(self.point()["v"], 0)

    def test_a_renewed_login_clears_it(self):
        self.record("AUTH", 60)
        self.sign_in("rt-secret-2", time.time() - 5)
        self.assertEqual(self.point()["v"], 0)

    def test_a_call_that_says_nothing_about_the_login_does_not_clear_it(self):
        self.record("AUTH", 60)
        for o in ("DEADLINE", "QUEUE_FULL", "TRANSPORT"):
            self.record(o, 5)
        self.assertEqual(self.point()["v"], 1)

    def test_a_log_that_cannot_be_read_is_unmeasured(self):
        p = self.point(log=self.t / "absent")
        self.assertEqual(p["m"], "UNMEASURED")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(SH.main(["--home", str(self.home), "--log", str(self.t / "absent")]), 2)
        with mock.patch.object(SH.dispatch_door, "load", side_effect=SH.dispatch_door.DoorMissing("no door")):
            import ops_watch
            self.assertEqual(ops_watch.artpipe_signin_reading()["queues.artpipe.signins_bad"]["m"], "UNMEASURED")


class TheCall(Base):
    def worker(self, body):
        w = self.t / "worker.py"
        w.write_text("import sys,time\n" + body)
        return w

    def call(self, body, **kw):
        return imagecall.call(self.worker(body), "generate", "p", self.t / "o.png", kw.pop("timeout", 5), self.t / "s.json",
                              self.t / "m.json", kw.pop("reference", None), kw.pop("model", None), "low", False, **kw)

    def test_verdict_is_the_last_typed_line(self):
        c = self.call("print('[image] VERDICT=AUTH KIND=failed exit=1',file=sys.stderr);"
                      "print('[image] VERDICT=ANSWERED KIND=answered exit=0',file=sys.stderr)")
        self.assertEqual((c.outcome, c.kind, c.not_run, c.timed_out), ("ANSWERED", "answered", False, False))

    def test_each_kind(self):
        for outcome, kind, not_run, timed in (("QUEUE_FULL", "could_not_start", True, False), ("AUTH", "failed", True, False),
                                              ("TRANSPORT", "could_not_start", True, False),
                                              ("BAD_INPUT", "could_not_start", False, False),
                                              ("NO_IMAGE", "failed", False, False),
                                              ("DEADLINE", "no_answer_in_time", False, True)):
            c = self.call("print('[image] VERDICT=%s KIND=%s exit=1',file=sys.stderr);sys.exit(1)" % (outcome, kind))
            self.assertEqual((outcome, c.not_run, c.timed_out), (outcome, not_run, timed))

    def test_a_worker_with_no_verdict_is_left_to_the_text_rules(self):
        c = self.call("print('ERROR no image produced',file=sys.stderr);sys.exit(1)")
        self.assertEqual((c.outcome, c.kind, c.not_run, c.code), (None, None, False, 1))

    def test_a_hung_worker_is_killed(self):
        with mock.patch.object(imagecall, "SLOT_WAIT_S", 0), mock.patch.object(imagecall, "GRACE_S", 1):
            c = self.call("time.sleep(60)", timeout=1)
        self.assertEqual((c.code, c.timed_out), (124, True))

    def test_production_names_no_signin_folder(self):
        c = self.call("print(sys.argv)")
        self.assertNotIn("--codex-home", c.out)
        self.assertIn("--slot-wait", c.out)

    def test_a_home_without_a_signin_is_not_ready(self):
        with mock.patch.dict(os.environ, {"GPT_DOOR_CODEX": "/bin/true"}):
            self.assertTrue(imagecall.ready(self.home)[0])
            (self.home / "auth.json").unlink()
            ok, why = imagecall.ready(self.home)
            self.assertFalse(ok)
            self.assertIn("renew", why)
            with mock.patch.object(imagecall.dispatch_door, "load",
                                   side_effect=imagecall.dispatch_door.DoorMissing("no door at /x")):
                self.assertEqual(imagecall.ready(), (False, "DoorMissing: no door at /x"))


def _case(cls, name) -> None:
    r = unittest.TestResult()
    cls(name).run(r)
    bad = r.errors + r.failures
    if bad or r.testsRun != 1:
        raise AssertionError(bad[0][1] if bad else "did not run")


def _scene(*names) -> None:
    """The daemon scenes of selftest_artpipe.py: a real daemon process on the fake worker."""
    import selftest_artpipe as SA
    for n in names:
        before = len(SA.FAILED)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            getattr(SA, n)()
        if len(SA.FAILED) > before or "ok " not in out.getvalue():
            raise AssertionError("%s: %s" % (n, SA.FAILED[before:] or "checked nothing"))


def t_a_could_not_start_call_spends_no_attempt():
    _scene("test_could_not_start_spends_no_attempt", "test_bad_input_fails_the_job_not_the_channel")


def t_a_dead_login_fails_no_job():
    _scene("test_dead_login_is_tried_once_per_interval_and_recovers")


def t_a_channel_comes_back_without_a_restart():
    _scene("test_channel_comes_back_without_a_restart")


def t_a_home_without_a_signin_is_not_ready():
    _case(TheCall, "test_a_home_without_a_signin_is_not_ready")
    _scene("test_home_without_signin_is_not_ready")


def t_n_workers_share_one_home():
    _scene("test_n_workers_share_one_home")


def t_a_dead_signin_reads_red():
    _case(Health, "test_a_dead_signin_reads_red")
    _case(Health, "test_a_call_that_says_nothing_about_the_login_does_not_clear_it")


def t_a_live_signin_reads_green():
    _case(Health, "test_a_live_signin_reads_green")


def t_a_later_answer_clears_it():
    _case(Health, "test_a_later_answer_clears_it")
    _case(Health, "test_a_renewed_login_clears_it")


def t_a_log_that_cannot_be_read_is_unmeasured():
    _case(Health, "test_a_log_that_cannot_be_read_is_unmeasured")


def t_the_call_is_typed():
    for n in ("test_verdict_is_the_last_typed_line", "test_each_kind",
              "test_a_worker_with_no_verdict_is_left_to_the_text_rules", "test_a_hung_worker_is_killed",
              "test_production_names_no_signin_folder"):
        _case(TheCall, n)


def main() -> int:
    tests = [t_a_could_not_start_call_spends_no_attempt, t_a_dead_login_fails_no_job,
             t_a_channel_comes_back_without_a_restart, t_a_home_without_a_signin_is_not_ready, t_n_workers_share_one_home,
             t_a_dead_signin_reads_red, t_a_live_signin_reads_green, t_a_later_answer_clears_it,
             t_a_log_that_cannot_be_read_is_unmeasured, t_the_call_is_typed]
    bad = 0
    for t in tests:
        try:
            t()
            print("PASS  %s" % t.__name__)
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure with its cause, never a skip
            bad += 1
            print("FAIL  %s  -- %s: %s" % (t.__name__, type(e).__name__, str(e)[-600:]))
    print("%d of %d failed" % (bad, len(tests)) if bad else "ALL PASS (%d tests)" % len(tests))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
