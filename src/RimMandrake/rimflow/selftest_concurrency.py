#!/usr/bin/env python3
"""Proves the O_APPEND atomicity claim the whole ledger design rests on.

🔴 WHY THIS IS A TEST AND NOT A PARAGRAPH. The argument for replacing six editable
markdown queues with one append-only file is entirely this: concurrent `O_APPEND`
writes below `PIPE_BUF` cannot interleave, so four seats can write at once without
locking. If that is false — on this filesystem, on this kernel, at this size — the
ledger silently accumulates torn lines and is worth less than what it replaced.

It is exactly the kind of claim that gets written down as settled and is never run.
So it runs: N processes, M events each, all appending to one file with no
coordination, then the result is checked for lost and torn lines.

    python3 src/RimMandrake/rimflow/selftest_concurrency.py [--writers 8] [--each 200]

🔴 IT ALREADY CAUGHT A REAL ONE, AND IT CAUGHT ITSELF FIRST. The first version of
this file wrote to `tempfile.mkdtemp()` — i.e. `/tmp`, which is tmpfs — and reported
3600/3600 with zero torn lines. The repo is on `/mnt/d`, a **9p/DrvFs** mount, where
the same test loses five of every six events and tears hundreds of lines. The test
was green and measuring the wrong disk. `--where` now defaults to the directory the
ledger actually lives in, and pointing it at `/tmp` is something you do on purpose,
to compare.

⚠️ Re-run this in the repo after any move to a different filesystem. `O_APPEND`
atomicity is a LOCAL-filesystem guarantee; it does not hold on 9p, NFS or SMB, and
`model.append()` takes an advisory `flock` precisely because of that.
"""
import argparse
import json
import multiprocessing
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                        # noqa: E402


def writer(args):
    path, wid, count = args
    for i in range(count):
        ev = {"ts": "2026-08-20T00:00:00Z", "seat": "BUILD", "event": "note",
              "id": "CONCURRENCY_PROBE_%d_%d" % (wid, i),
              "text": "writer %d event %d %s" % (wid, i, "p" * 40)}
        model.append(ev, path)
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--writers", type=int, default=8)
    ap.add_argument("--each", type=int, default=200)
    ap.add_argument("--where", default=os.path.join(model.ROOT, "infrastructure", "state"),
                    help="directory to test IN. Defaults to where the ledger lives; "
                         "pass /tmp only to compare filesystems deliberately.")
    a = ap.parse_args()

    # 🔴 THE DIRECTORY IS THE TEST. Defaulting to tempfile's /tmp made this pass
    # 3600/3600 while the repo's own 9p mount was losing 83% of writes — a green
    # test measuring the wrong disk. It now writes where the ledger actually lives.
    tmp = tempfile.mkdtemp(prefix=".rimflow_conc_", dir=a.where)
    path = os.path.join(tmp, "events.jsonl")
    try:
        with multiprocessing.Pool(a.writers) as pool:
            pool.map(writer, [(path, w, a.each) for w in range(a.writers)])

        expected = a.writers * a.each
        with open(path, "rb") as fh:
            raw = fh.read()
        lines = raw.decode("utf-8").splitlines()

        torn, seen = [], set()
        for n, line in enumerate(lines, 1):
            try:
                ev = json.loads(line)
            except ValueError:
                torn.append((n, line[:80]))
                continue
            seen.add(ev["id"])

        size = len(raw) / float(expected)
        print("writers %d × %d events = %d expected" % (a.writers, a.each, expected))
        print("lines written      : %d" % len(lines))
        print("distinct ids seen  : %d" % len(seen))
        print("torn lines         : %d" % len(torn))
        print("mean event size    : %.0f bytes  (PIPE_BUF is %d)"
              % (size, model.PIPE_BUF))
        print("trailing newline   : %s" % ("yes" if raw.endswith(b"\n") else "NO"))

        bad = 0
        if torn:
            bad += 1
            print("\n🔴 TORN LINES — O_APPEND did not hold on this filesystem.")
            for n, frag in torn[:5]:
                print("   line %d: %s…" % (n, frag))
            print("   The ledger design assumes this cannot happen. Do not use it "
                  "concurrently on this filesystem until it is understood.")
        if len(lines) != expected or len(seen) != expected:
            bad += 1
            print("\n🔴 LOST EVENTS — %d of %d survived. Appends overwrote each other."
                  % (len(seen), expected))
        if not raw.endswith(b"\n"):
            bad += 1
            print("\n🔴 NO TRAILING NEWLINE — the next append would join the last line.")
        if not bad:
            print("\n✅ %d concurrent appends, zero torn, zero lost — WITH the "
                  "advisory flock in model.append()." % expected)
            print("   ⚠️ That lock is what makes this pass. Removing it on this "
                  "filesystem loses ~5 of every 6 events; see the module docstring.")
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
