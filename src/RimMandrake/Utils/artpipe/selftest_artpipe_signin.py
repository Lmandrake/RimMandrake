#!/usr/bin/env python3
"""Tests for design/specs/2026-11-22-art-worker-own-signin/boundary.md: one sign-in per art worker home, never copied,
and the dead-sign-in alarm. Each test has the name of its promise. Fake sign-ins only (unsigned JWTs, made-up refresh
tokens); no network, no real Codex home is read or written.

    python3 src/RimMandrake/Utils/artpipe/selftest_artpipe_signin.py     exit 0 all pass, 1 a failure
"""
from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
os.environ.setdefault("ARTPIPE_STATE_DIR", tempfile.mkdtemp(prefix="artpipe_signin_state_"))

import artpiped  # noqa: E402
import codex_image  # noqa: E402  (artpiped put the image skills on sys.path)
import signin_health  # noqa: E402

FAILS: list[str] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    print("%s  %s%s" % ("PASS" if cond else "FAIL", name, "" if cond else "  -- %s" % detail))
    if not cond:
        FAILS.append(name)


def _jwt(exp: int) -> str:
    b64 = lambda o: base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()
    return "%s.%s.sig" % (b64({"alg": "none"}), b64({"exp": exp}))


def sign_in(home: Path, refresh_token: str, last_refresh: datetime | None = None) -> None:
    """A fake device sign-in: its own refresh-token lineage."""
    last_refresh = last_refresh or datetime.now(timezone.utc)
    home.mkdir(parents=True, exist_ok=True)
    (home / "auth.json").write_text(json.dumps({
        "auth_mode": "chatgpt", "last_refresh": last_refresh.isoformat(),
        "tokens": {"access_token": _jwt(int((last_refresh + timedelta(days=10)).timestamp())),
                   "refresh_token": refresh_token, "id_token": "x.y.z", "account_id": "acct"}}))


def five_own_signins(root: Path) -> dict:
    """Five homes as the owner left them on 2026-11-21: five lineages, a few minutes apart, all older than the
    daemon's 12 h stale line. -> {home name: auth.json bytes}."""
    t0 = datetime.now(timezone.utc) - timedelta(hours=40)
    for i in range(5):
        sign_in(root / ("w%d" % i), "rt-device-%d" % i, t0 + timedelta(minutes=i))
    return {"w%d" % i: (root / ("w%d" % i) / "auth.json").read_bytes() for i in range(5)}


class _Ctx:
    """The three fields of artpiped.RunCtx that _StaleRefreshGuard reads."""
    def __init__(self, root: Path):
        import threading
        self.codex_home_root = root
        self._stale_refresh_lock = threading.Lock()
        self._lineage_probe_ok = {}


# ---------------------------------------------------------------------------------------------------------- promises

def t_a_restart_leaves_every_worker_signin_untouched(startup=None):
    """The daemon's start-up sign-in step reads the five homes and writes none of them. `startup(root, base, warn)`
    is the step under test; the red run on the parent passed the parent's step (common.resync_stale_worker_homes)."""
    startup = startup or artpiped.worker_signin_startup
    with tempfile.TemporaryDirectory() as td:
        root, base = Path(td) / "workers", Path(td) / "base"
        before = five_own_signins(root)
        sign_in(base, "rt-consults")            # the GPT consults' home, a sixth lineage, fresher than all five
        warns: list[str] = []
        startup(root, base, warns.append)
        after = {n: (root / n / "auth.json").read_bytes() for n in before}
        changed = sorted(n for n in before if before[n] != after[n])
        ok("a-restart-leaves-every-worker-signin-untouched: no worker auth.json changed at start-up", not changed,
           "overwritten: %s" % changed)
        ok("a-restart-leaves-every-worker-signin-untouched: five live own sign-ins raise no warning", not warns,
           warns)


def t_a_mid_run_rotation_copies_no_signin():
    """A job whose own home rotates its token mid-run (codex refreshed it) changes no other home."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        before = five_own_signins(root)
        with mock.patch.object(artpiped, "_codex_home_is_refresh_due",
                               side_effect=lambda h, p=None: (True, codex_image.read_auth_freshness(h)["last_refresh"])):
            g = artpiped._StaleRefreshGuard(_Ctx(root), root / "w0")
            with g:
                ok("a-mid-run-rotation-copies-no-signin: the stale home took the guard", g.held)
                sign_in(root / "w0", "rt-device-0-rotated")      # codex rotates w0's own lineage
        changed = sorted(n for n in before if n != "w0" and (root / n / "auth.json").read_bytes() != before[n])
        ok("a-mid-run-rotation-copies-no-signin: no sibling home was overwritten", not changed,
           "overwritten: %s" % changed)


def t_a_new_worker_home_is_never_seeded_with_a_signin():
    """A worker home with no sign-in of its own is refused by name, and no auth.json is copied into it."""
    with tempfile.TemporaryDirectory() as td:
        base, new = Path(td) / "base", Path(td) / "w5"
        sign_in(base, "rt-consults")
        (base / "config.toml").write_text("model = 'x'\n")
        env = {"CODEX_HOME": str(base), "RM_CODEX_SIDE": "wsl"}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stderr(io.StringIO()):
            try:
                codex_image.codex_home(new)
                err = None
            except codex_image.EnvError as e:
                err = str(e)
            seeded = Path(td) / "w6"
            try:
                codex_image.seed_codex_home(base, seeded)
            except codex_image.EnvError:
                pass                              # refused by name, as codex_home() is; the copy is what is checked
        ok("a-new-worker-home-is-never-seeded-with-a-signin: codex_home() refuses a home with no sign-in",
           err is not None and "device-auth" in err, err or "no refusal")
        ok("a-new-worker-home-is-never-seeded-with-a-signin: no auth.json was copied in by codex_home()",
           not (new / "auth.json").exists())
        ok("a-new-worker-home-is-never-seeded-with-a-signin: seed_codex_home() copies config but no auth.json",
           (seeded / "config.toml").is_file() and not (seeded / "auth.json").exists())
        ok("a-new-worker-home-is-never-seeded-with-a-signin: auth.json is not a seed file",
           "auth.json" not in codex_image.HOME_SEED_FILES)


def t_a_dead_signin_reads_red():
    """Each planted dead or doomed sign-in reads as its own bad verdict, and the alarm point counts it."""
    with tempfile.TemporaryDirectory() as td:
        root, base = Path(td) / "workers", Path(td) / "base"
        five_own_signins(root)
        sign_in(base, "rt-consults")
        (root / "w1" / "auth.json").unlink()                                          # gone
        (root / "w2" / "auth.json").write_text("{not json")                           # torn
        sign_in(root / "w3", "rt-consults")                                           # a copy of the base's
        signin_health.record_outcome(root / "w4", auth_failed=True)                   # died on its last job
        (root / "w5").mkdir()                                                         # a leased slot never signed in
        v = signin_health.check(root, base)
        want = {"w0": "live", "w1": "no_signin", "w2": "unreadable", "w3": "shared", "w4": "auth_failed",
                "w5": "no_signin"}
        ok("a-dead-signin-reads-red: each planted fault has its verdict", v == want, v)
        p = artpiped_free_point(root, base)
        ok("a-dead-signin-reads-red: the alarm point is MEASURED 5", p.get("m") == "MEASURED" and p.get("v") == 5, p)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        five_own_signins(root)
        (root / "w1" / "auth.json").write_bytes((root / "w0" / "auth.json").read_bytes())   # the old resync's copy
        v = signin_health.check(root, None)
        ok("a-dead-signin-reads-red: two workers on one lineage both read shared",
           v["w0"] == v["w1"] == "shared" and v["w2"] == "live", v)


def t_a_live_signin_reads_green():
    """Five own lineages, a base on a sixth, last jobs clean: every home live, the point MEASURED 0."""
    with tempfile.TemporaryDirectory() as td:
        root, base = Path(td) / "workers", Path(td) / "base"
        five_own_signins(root)
        sign_in(base, "rt-consults")
        signin_health.record_outcome(root / "w0", auth_failed=False)
        v = signin_health.check(root, base)
        ok("a-live-signin-reads-green: all five live", set(v.values()) == {"live"} and len(v) == 5, v)
        p = artpiped_free_point(root, base)
        ok("a-live-signin-reads-green: the alarm point is MEASURED 0", p.get("m") == "MEASURED" and p.get("v") == 0, p)
        ok("a-live-signin-reads-green: the point names no token", "rt-" not in json.dumps(p), p)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = signin_health.main(["--root", str(root), "--base", str(base)])
        ok("a-live-signin-reads-green: the CLI exits 0 and prints no token", rc == 0 and "rt-" not in out.getvalue(),
           (rc, out.getvalue()))


def t_a_new_signin_clears_an_auth_failure():
    """The daemon's guard writes each job's sign-in outcome; a failed one reads red until a device sign-in gives the
    home a new lineage."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        five_own_signins(root)
        g = artpiped._StaleRefreshGuard(_Ctx(root), root / "w2")
        with g:
            g.auth_failed = True                  # what process_codex_job sets on Codex's refresh-token wording
        ok("a-new-signin-clears-an-auth-failure: the guard recorded the failed job",
           signin_health.check(root)["w2"] == "auth_failed", signin_health.check(root))
        sign_in(root / "w2", "rt-device-2-again")
        ok("a-new-signin-clears-an-auth-failure: a new device sign-in reads live",
           signin_health.check(root)["w2"] == "live", signin_health.check(root))
        with artpiped._StaleRefreshGuard(_Ctx(root), root / "w3"):
            pass
        rec = json.loads((root / "w3" / signin_health.OUTCOME_FILE).read_text())
        ok("a-new-signin-clears-an-auth-failure: a clean job is recorded clean, with no token in the record",
           rec.get("auth_failed") is False and "rt-" not in json.dumps(rec), rec)


def t_a_root_that_cannot_be_read_is_unmeasured():
    """No worker-home root is UNMEASURED with its cause, never 0; a root with no homes is MEASURED 0 with homes 0."""
    with tempfile.TemporaryDirectory() as td:
        p = artpiped_free_point(Path(td) / "absent", None)
        ok("a-root-that-cannot-be-read-is-unmeasured: an absent root reads UNMEASURED",
           p.get("m") == "UNMEASURED" and "absent" in json.dumps(p), p)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = signin_health.main(["--root", str(Path(td) / "absent")])
        ok("a-root-that-cannot-be-read-is-unmeasured: the CLI exits 2", rc == 2, rc)
        p = artpiped_free_point(Path(td), None)
        ok("a-root-that-cannot-be-read-is-unmeasured: an empty root reads MEASURED 0 with homes 0",
           p.get("m") == "MEASURED" and p.get("v") == 0 and (p.get("x") or {}).get("homes") == 0, p)


def artpiped_free_point(root: Path, base: Path | None) -> dict:
    """ops_watch's reading for the alarm key, on these homes."""
    import ops_watch
    return ops_watch.artpipe_signin_reading(root, base)["queues.artpipe.signins_bad"]


def main() -> int:
    tests = [t_a_restart_leaves_every_worker_signin_untouched, t_a_mid_run_rotation_copies_no_signin,
             t_a_new_worker_home_is_never_seeded_with_a_signin, t_a_dead_signin_reads_red, t_a_live_signin_reads_green,
             t_a_new_signin_clears_an_auth_failure, t_a_root_that_cannot_be_read_is_unmeasured]
    for t in tests:
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure with its cause, never a skip
            ok(t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%d checks failed of %d tests" % (len(FAILS), len(tests)) if FAILS else "ALL PASS (%d tests)" % len(tests))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
