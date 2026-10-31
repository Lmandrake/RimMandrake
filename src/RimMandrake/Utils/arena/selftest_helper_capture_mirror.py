#!/usr/bin/env python3
"""selftest_helper_capture_mirror: a pass that deletes or shrinks its own spend logs mid-run hides nothing
(ARENA_TESTER_SPEND_ENFORCE_SELF_ERASED_LOGS). helper_capture.Mirror copies the logs, append-only, into a sibling the
sandbox never binds; capture_tester files that copy; arena_spend.sandbox_homes reads a builder's mirror home.
Sanity: the same run captured WITHOUT the mirror loses the deleted calls (the check can see a loss)."""
from __future__ import annotations

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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
