#!/usr/bin/env python3
"""selftest_helper_capture_mirror: a pass that deletes or shrinks its own spend logs mid-run hides nothing
(ARENA_TESTER_SPEND_ENFORCE_SELF_ERASED_LOGS). helper_capture.Mirror copies the logs, append-only, into a sibling the
sandbox never binds; capture_tester files that copy; arena_spend.sandbox_homes reads a builder's mirror home.
Sanity: the same run captured WITHOUT the mirror loses the deleted calls (the check can see a loss).
F1-F4 (ARENA_MIRROR_FAILURE_ENFORCE_SILENT_LOSS): a mirror tick that fails, a state that cannot be written, a mirror
that never starts (tester and builder) each make the meter BLOCK; with no failure record possible the pass is VOID."""
from __future__ import annotations

import calendar
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sim"))
import helper_capture as HC  # noqa: E402
import arena_spend as SP  # noqa: E402
import ralph_a_loop as RA  # noqa: E402
import spend_census as S  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def msg(i):
    return json.dumps({"type": "assistant", "timestamp": "2026-10-30T10:00:%02dZ" % i,
                       "message": {"id": "msg_%d" % i, "model": "claude-opus-4", "usage": {
                           "input_tokens": 10, "output_tokens": 5}, "content": []}}) + "\n"


def gpt(i):
    return json.dumps({"ts": "2026-10-30T10:00:%02dZ" % i, "call": i}) + "\n"


def wait_for(mirror, path, n, t=5.0):
    end = time.time() + t
    while time.time() < end:
        if path.exists() and path.read_bytes().count(b"\n") >= n:
            return True
        time.sleep(0.02)
    return False


def calls_in(d):
    seen, n = set(), 0
    for p in sorted(Path(d).rglob("*.jsonl")):
        n += len(S.scan_file(str(p), 0, seen)[0])
    return n, seen


def blocked(rec, what):
    """The meter's tester rule on rec's capture -> its blocking lines."""
    t = calendar.timegm(time.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ"))
    _, _, bl = SP.tester_captures({rec["arm"]: {"recs": [rec]}}, None, t - 1, t + 100)
    return [b for b in bl if what in b]


def mirror_failure_cases(tmp, rec):
    """ARENA_MIRROR_FAILURE_ENFORCE_SILENT_LOSS: a mirror that fails flags (meter BLOCKS) or voids the run."""
    # ---- a tick's write fails mid-run, then the log is erased: the error is on disk, the capture blocks
    r = tmp / "rt-f1"
    pj = r / "home" / ".claude" / "projects" / "-x"
    pj.mkdir(parents=True)
    tr = pj / "s.jsonl"
    tr.write_text(msg(1))
    m = HC.Mirror(r, interval=0.02).start()
    md = m.dir / "home" / ".claude" / "projects" / "-x"
    check(wait_for(m, md / "s.jsonl", 1), "F1 mirror copied the first call")
    os.chmod(md / "s.jsonl", 0o400)
    with open(tr, "a") as f:
        f.write(msg(2))
    end = time.time() + 5
    while time.time() < end and not any("mirror error" in x for x in HC.mirror_skipped(m.dir)):
        time.sleep(0.02)
    on_disk = HC.mirror_skipped(m.dir)
    check(any("mirror error" in x for x in on_disk), "F1 a failed tick is written to the mirror state at once (%s)"
          % on_disk)
    tr.unlink()                                          # the undelivered call is gone with the log
    os.chmod(md / "s.jsonl", 0o600)
    m.stop()
    r1 = dict(rec, run_id="f1")
    RA.capture_tester(r1, r, 0)
    check(blocked(r1, "mirror error"), "F1 the meter BLOCKS the tester whose mirror failed (run flagged)")
    sane = dict(rec, run_id="f1s")
    r_ok = tmp / "rt-f1s"
    (r_ok / "home" / ".claude" / "projects" / "-x").mkdir(parents=True)
    (r_ok / "home" / ".claude" / "projects" / "-x" / "s.jsonl").write_text(msg(1))
    RA.spend_mirror(r_ok).stop()
    RA.capture_tester(sane, r_ok, 0)
    check(not blocked(sane, "arm"), "F1 sanity: the same tester with a healthy mirror is not blocked")

    # ---- the state cannot be written either: the failure goes to the <root>.mirror.failed marker
    r = tmp / "rt-f2"
    (r / "home" / ".claude" / "projects" / "-x").mkdir(parents=True)
    (r / "home" / ".claude" / "projects" / "-x" / "s.jsonl").write_text(msg(1))
    m = HC.Mirror(r, interval=3600)
    save = m._save
    m._save = lambda: (_ for _ in ()).throw(OSError("disk full"))
    m.sync = lambda: (_ for _ in ()).throw(OSError("copy failed"))
    m.stop()
    m._save = save
    check(m.persisted and any("copy failed" in x for x in HC.mirror_failures(m.dir)),
          "F2 state unwritable: the failure lands in the marker file")
    r2 = dict(rec, run_id="f2")
    RA.capture_tester(r2, r, 0)
    check(blocked(r2, "copy failed"), "F2 the meter BLOCKS on the marker")
    check(not HC.failed_marker(m.dir).exists(), "F2 capture_tester removes the marker after filing it")

    # ---- the mirror never starts: marker -> tester blocked, builder scratch blocked
    hm = HC.Mirror
    HC.Mirror = lambda *a, **k: (_ for _ in ()).throw(OSError("mirror unavailable"))
    try:
        r = tmp / "rt-f3"
        (r / "home" / ".claude" / "projects" / "-x").mkdir(parents=True)
        (r / "home" / ".claude" / "projects" / "-x" / "s.jsonl").write_text(msg(1))
        check(RA.spend_mirror(r) is None, "F3 spend_mirror -> None when the mirror cannot start")
        r3 = dict(rec, run_id="f3")
        RA.capture_tester(r3, r, 0)
        check(blocked(r3, "did not start"), "F3 a tester whose mirror never started is BLOCKED (was clean)")
        base = tmp / "sandbox-f"
        sc = base / "armB-12345678-b" / "build"
        (sc / "home" / ".claude" / "projects" / "-z").mkdir(parents=True)
        RA.spend_mirror(sc)
        _, bl = SP.sandbox_homes(base)
        check(len(bl) == 1 and "did not start" in bl[0], "F3 a builder scratch whose mirror never started BLOCKS (%s)"
              % bl)
        # ---- not even the marker can be written: the pass is VOID, never run
        ro = tmp / "ro"
        (ro / "role" / "home").mkdir(parents=True)
        os.chmod(ro, 0o500)
        plan = RA.sandbox_plan
        try:
            try:
                RA.spend_mirror(ro / "role")
                check(False, "F4 spend_mirror raises MirrorVoid when no failure record can be written")
            except RA.MirrorVoid:
                check(True, "F4 spend_mirror raises MirrorVoid when no failure record can be written")
            ran = tmp / "ran"
            cm = RA.CmdModel("true")
            RA.sandbox_plan = lambda role, cwd, sandbox: ([], ro / "role" / "home")
            cm.wrap = lambda argv, env, **k: (["touch", str(ran)], env)
            rc = cm.spawn("test", ["x"], {}, cwd=tmp, sandbox=None, agent_id="a", log=tmp / "void.log", prompt="",
                          timeout_s=10)
            check(rc == RA.VOID_RC and not ran.exists() and "VOID" in (tmp / "void.log").read_text(),
                  "F4 CmdModel.spawn does not run the pass (rc %s, ran %s)" % (rc, ran.exists()))
            # ---- F5: the mirror failed mid-pass and neither state nor marker could record it -> VOID, not rc 0
            class Lost:
                persisted = False

                def stop(self):
                    return []

                def reconcile(self, text):
                    return None
            sm = RA.spend_mirror
            RA.spend_mirror = lambda root: Lost()
            try:
                cm.wrap = lambda argv, env, **k: (["true"], env)
                rc = cm.spawn("test", ["x"], {}, cwd=tmp, sandbox=None, agent_id="a", log=tmp / "lost.log", prompt="",
                             timeout_s=10)
                check(rc == RA.VOID_RC, "F5 mid-pass persist lost -> rc VOID_RC (rc %s)" % rc)
                Lost.persisted = True
                rc = cm.spawn("test", ["x"], {}, cwd=tmp, sandbox=None, agent_id="a", log=tmp / "lost.log", prompt="",
                             timeout_s=10)
                check(rc == 0, "F5 sanity: a persisted mirror leaves rc 0 (rc %s)" % rc)
            finally:
                RA.spend_mirror = sm
        finally:
            RA.sandbox_plan = plan
            os.chmod(ro, 0o700)
    finally:
        HC.Mirror = hm


def smsg(i, sid="sess-1", cr=1000):
    return json.dumps({"type": "assistant", "sessionId": sid, "timestamp": "2026-10-30T10:00:%02dZ" % i,
                       "message": {"id": "msg_%d" % i, "model": "claude-opus-4", "usage": {
                           "input_tokens": 2, "cache_read_input_tokens": cr, "cache_creation_input_tokens": 8,
                           "output_tokens": 5}, "content": []}}) + "\n"


def envelope(n, sid="sess-1", cr=1000):
    return json.dumps({"type": "result", "session_id": sid, "num_turns": n, "modelUsage": {"claude-opus-4": {
        "inputTokens": 2 * n, "cacheReadInputTokens": cr * n, "cacheCreationInputTokens": 8 * n,
        "outputTokens": 5 * n}}})


def reconcile_cases(tmp, rec):
    """ARENA_SPEND_RECONCILE_ERASED_CALL_UNSEEN: the call a model erases before the 1 s copy is still in the CLI's own
    envelope; the shortfall BLOCKS a tester (manifest) and a builder (sandbox_homes), through the real spawn."""
    # ---- R1 tester: the mirror saw 3 calls (the 4th, the erasing one, never reached a copy); the CLI counted 4
    tr = tmp / "rt-r1"
    pj = tr / "home" / ".claude" / "projects" / "-x"
    pj.mkdir(parents=True)
    (pj / "sess-1.jsonl").write_text(smsg(1) + smsg(2) + smsg(3))
    m = HC.Mirror(tr, interval=3600).start()
    m.stop()
    r = m.reconcile(envelope(4))
    check(r and r["seen_calls"] == 3 and r["why"] and abs(r["short"] - 0.25) < 1e-3,
          "R1 reconcile sees 3 of 4 calls, 25%% of the input side unseen, and says why (%s)" % r)
    r1 = dict(rec, run_id="rr1")
    RA.capture_tester(r1, tr, 0)
    check(blocked(r1, "spend reconcile"), "R1 the meter BLOCKS the tester whose erased call the CLI still counted")
    # ---- R2 sanity: the same tester with an envelope that matches is clean; a text-output log is no check at all
    tr2 = tmp / "rt-r2"
    pj2 = tr2 / "home" / ".claude" / "projects" / "-x"
    pj2.mkdir(parents=True)
    (pj2 / "sess-1.jsonl").write_text(smsg(1) + smsg(1) + smsg(2) + smsg(3) + smsg(9, sid="other"))
    m2 = HC.Mirror(tr2, interval=3600).start()
    m2.stop()
    r = m2.reconcile(envelope(3))
    check(r and r["seen_calls"] == 3 and r["why"] is None and r["short"] == 0,
          "R2 sanity: a matching envelope reconciles clean (a repeated id counts once, another session not) (%s)" % r)
    check(m2.reconcile("plain text answer") is None, "R2 a non-JSON pass log is no reconcile (None)")
    r2 = dict(rec, run_id="rr2")
    RA.capture_tester(r2, tr2, 0)
    check(not blocked(r2, "arm"), "R2 sanity: the reconciled tester is not blocked")
    bad = m2.reconcile(json.dumps({"type": "result", "session_id": "s", "modelUsage": {"m": {"inputTokens": True}}}))
    check(bad and bad["why"] and "no usable" in bad["why"], "R2 an envelope with a bool count BLOCKS (%s)" % bad)
    # ---- R3 builder through CmdModel.spawn: the pass prints its envelope; the meter blocks the builder's scratch
    base = tmp / "sandbox-r"
    plan = RA.sandbox_plan
    try:
        for tag, n, want in (("over", 5, True), ("even", 2, False)):
            sc = base / ("armR-12345678-%s" % tag) / "build"
            bp = sc / "home" / ".claude" / "projects" / "-z"
            bp.mkdir(parents=True)
            (bp / "sess-1.jsonl").write_text(smsg(1) + smsg(2))
            RA.sandbox_plan = lambda role, cwd, sandbox, sc=sc: ([], sc / "home")
            cm = RA.CmdModel("true")
            cm.wrap = lambda argv, env, n=n, **k: (["printf", "%s", envelope(n)], env)
            log = tmp / ("r3-%s.log" % tag)
            rc = cm.spawn("build", ["x"], {}, cwd=tmp, sandbox=None, agent_id="a", log=log, prompt="", timeout_s=10)
            _, bl = SP.sandbox_homes(base)
            hit = [b for b in bl if "spend reconcile" in b and tag in b]
            check(rc == 0 and bool(hit) == want, "R3 builder %s: CLI %d calls, mirror 2 -> blocking %s (rc %s, %s)"
                  % (tag, n, want, rc, bl))
    finally:
        RA.sandbox_plan = plan


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_hc_mirror_"))
    os.environ["ARENA_METER_HELPERS"] = str(tmp / "helpers")
    try:
        # ---- a tester: rm of its transcript and its GPT log mid-run, an innocent re-create, a torn last line
        troot = tmp / "rt-1"
        pj = troot / "home" / ".claude" / "projects" / "-x"
        pj.mkdir(parents=True)
        (troot / "gpt").mkdir()
        tr, gl = pj / "s.jsonl", troot / "gpt" / "calls.jsonl"
        tr.write_text(msg(1))
        gl.write_text(gpt(1))
        m = HC.Mirror(troot, interval=0.02).start()
        mt = m.dir / "home" / ".claude" / "projects" / "-x" / "s.jsonl"
        check(not m.dir.resolve().is_relative_to(troot.resolve()), "the mirror is a sibling, outside the bound root")
        with open(tr, "a") as f:
            f.write(msg(2))
        check(wait_for(m, mt, 2), "mirror picked up the appended call")
        tr.unlink()                                       # the mid-session rm
        gl.unlink()
        time.sleep(0.1)
        tr.write_text(msg(3) + msg(4)[:20])              # a fresh transcript at the same name, last line torn
        gl.write_text(gpt(2))
        skipped = m.stop()
        check(not skipped, "nothing skipped on a clean run (%s)" % skipped)
        n, ids = calls_in(m.dir / "home")
        check(n == 3 and ids == {"msg_1", "msg_2", "msg_3"}, "mirror holds all 3 complete calls (%d, %s)"
              % (n, sorted(ids)))
        segs = sorted(p.name for p in (m.dir / "home").rglob("*.jsonl"))
        check(segs == ["s.jsonl", "s~m1.jsonl"], "the re-created file continues in a new segment (%s)" % segs)
        rec = {"event": "test_start", "arm": "armA", "run_id": "r1", "task": "t1", "ts": "2026-10-30T10:00:00Z",
               "detail": {"tester": "tester-1"}}
        sane = HC.capture(dict(rec, run_id="r0"), home=troot / "home", gpt_dir=troot / "gpt")
        n0, _ = calls_in(sane / "claude")
        check(n0 == 1, "sanity: captured WITHOUT the mirror, the rm hides calls (%d of 3 seen)" % n0)
        cap = RA.capture_tester(rec, troot, 0)
        man, d = HC.load(rec)
        check(man is not None and not man["skipped"], "capture_tester filed a clean manifest from the mirror")
        n1, _ = calls_in(Path(d) / "claude")
        check(n1 == 3, "the meter's capture holds all 3 calls (%d)" % n1)
        g = sorted((Path(d) / "gpt").glob("*.jsonl"))
        glines = sum(p.read_text().count("\n") for p in g)
        check(glines == 2, "both GPT records survive the GPT log's rm (%d)" % glines)
        check(not m.dir.exists(), "capture_tester removes the mirror after filing it")
        check(cap == d, "capture dir returned")

        # ---- a shrink (truncate and rewrite) is a new segment, never a shrink of the mirror
        r2 = tmp / "rt-2"
        (r2 / "gpt").mkdir(parents=True)
        g2 = r2 / "gpt" / "c.jsonl"
        g2.write_text(gpt(1) + gpt(2))
        m2 = HC.Mirror(r2, interval=3600).start()
        with open(g2, "w") as f:
            f.write(gpt(3))
        m2.stop()
        lines = sum(p.read_text().count("\n") for p in (m2.dir / "gpt").glob("*.jsonl"))
        check(lines == 3, "truncated log: mirror keeps the 2 old records and the new one (%d)" % lines)

        # ---- a planted symlink is never followed and blocks the capture
        r3 = tmp / "rt-3"
        p3 = r3 / "home" / ".claude" / "projects" / "-y"
        p3.mkdir(parents=True)
        foreign = tmp / "foreign.jsonl"
        foreign.write_text(msg(9))
        os.symlink(foreign, p3 / "f.jsonl")
        m3 = HC.Mirror(r3, interval=3600).start()
        sk = m3.stop()
        check(sk and not list(m3.dir.rglob("f.jsonl")), "symlinked log: not copied, recorded skipped (%s)" % sk)
        rec3 = dict(rec, run_id="r3")
        RA.capture_tester(rec3, r3, 0)
        man3, _ = HC.load(rec3)
        check(man3 is not None and man3["skipped"], "the mirror's skipped list reaches the manifest (meter blocks)")

        # ---- a builder: persistent scratch; the mirror resumes without re-copying; the meter reads it
        base = tmp / "sandbox"
        sc = base / "armA-12345678-b" / "build"
        bp = sc / "home" / ".claude" / "projects" / "-z"
        bp.mkdir(parents=True)
        bt = bp / "b.jsonl"
        bt.write_text(msg(1))
        RA.spend_mirror(sc).stop()
        with open(bt, "a") as f:
            f.write(msg(2))
        RA.spend_mirror(sc).stop()
        mb = HC.mirror_dir(sc) / "home" / ".claude" / "projects" / "-z" / "b.jsonl"
        check(mb.read_text() == msg(1) + msg(2), "second pass appends only the new bytes (no duplicate copy)")
        shutil.rmtree(sc / "home")                        # the builder wipes its whole home
        homes, blocking = SP.sandbox_homes(base)
        n2 = sum(calls_in(h)[0] for h, _, _ in homes)
        names = {s for _, _, s in homes}
        check(not blocking and n2 == 2 and names == {"armA-12345678-b"},
              "sandbox_homes reads the builder's mirror home under its scratch name (%d calls, %s, %s)"
              % (n2, names, blocking))

        mirror_failure_cases(tmp, rec)
        reconcile_cases(tmp, rec)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
