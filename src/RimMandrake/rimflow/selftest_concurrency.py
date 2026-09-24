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

TWO ARMS, AND BOTH MUST HOLD
============================
1. **one file, no routing** — `model.append(ev, path)` with an explicit path, the
   original single-file contract. Unchanged by the sharding, which is the point: an
   explicit path still writes exactly one literal file.
2. **sharded** (`sharded()`) — `model.append(ev)` with NO path, which routes by
   `ev["seat"]`. It proves the claim the sharding rests on: two seats appending at the
   same instant never touch the same git-tracked file, several processes on ONE seat's
   shard still lose nothing, and `events.jsonl` is never written at all.
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


SHARD_SEATS = ("BENCH", "FOUNDRY")


def shard_writer(args):
    """One process appending with NO path, i.e. through the seat-sharding router.

    ⚠️ `model.EVENTS` is reassigned IN THE CHILD. `shard_dir()` derives the shard
    location from the ledger in use, so this is what keeps a concurrency test's 1600
    appends out of the real repo's ledger — the same property
    `t_ledger_path_is_redirectable` pins in `selftest_model.py`.
    """
    where, wid, count, seat = args
    model.EVENTS = os.path.join(where, "events.jsonl")
    for i in range(count):
        model.append({"ts": "2026-08-20T00:00:00Z", "seat": seat, "event": "note",
                      "id": "SHARD_PROBE_%s_%d_%d" % (seat, wid, i),
                      "text": "writer %d event %d %s" % (wid, i, "p" * 40)})
    return count


def sharded(where, writers, each):
    """🔴 THE CLAIM THE SHARDING RESTS ON: two seats appending at once never touch the
    same file, so git can never conflict between them — and several processes on ONE
    seat's shard still lose nothing, which is the BENCH-plus-subagents case.

    -> 0 if that holds, 1 if it does not, with the numbers printed either way.
    """
    tmp = tempfile.mkdtemp(prefix=".rimflow_shard_", dir=where)
    try:
        jobs = [(tmp, w, each, SHARD_SEATS[w % len(SHARD_SEATS)])
                for w in range(writers)]
        with multiprocessing.Pool(writers) as pool:
            pool.map(shard_writer, jobs)

        expected = writers * each
        head = os.path.join(tmp, "events.jsonl")
        sdir = os.path.join(tmp, "events")
        names = sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []
        per, torn, seen = {}, [], set()
        for n in names:
            with open(os.path.join(sdir, n), encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            seats = set()
            for ln, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    torn.append((n, ln, line[:80]))
                    continue
                seats.add(ev.get("seat"))
                seen.add(ev["id"])
            per[n] = (len(lines), seats)

        print("")
        print("SHARDED ARM — %d writers × %d events across seats %s"
              % (writers, each, "/".join(SHARD_SEATS)))
        for n in names:
            print("  %-16s %5d lines   seats: %s"
                  % (n, per[n][0], ", ".join(sorted(x or "?" for x in per[n][1]))))
        print("  events.jsonl     %s" % ("PRESENT" if os.path.exists(head) else "absent"))

        bad = 0
        if torn:
            bad += 1
            print("\n🔴 TORN LINES in a shard — flock did not hold: %r" % (torn[:3],))
        if len(seen) != expected:
            bad += 1
            print("\n🔴 LOST EVENTS — %d of %d survived across the shards."
                  % (len(seen), expected))
        mixed = {n: s for n, (_, s) in per.items() if len(s) > 1}
        if mixed:
            bad += 1
            print("\n🔴 A SHARD HOLDS MORE THAN ONE SEAT'S EVENTS: %r. The whole point "
                  "is that two seats never write the same git-tracked file." % mixed)
        for n, (_, s) in per.items():
            if s and n[: -len(".jsonl")] not in s:
                bad += 1
                print("\n🔴 %s does not hold %s's events (%r) — the routing is not a "
                      "pure function of ev['seat']." % (n, n[:-6], s))
        if sorted(names) != sorted("%s.jsonl" % s for s in SHARD_SEATS):
            bad += 1
            print("\n🔴 shard files are %r, expected one per seat." % (names,))
        if os.path.exists(head):
            bad += 1
            print("\n🔴 something appended to events.jsonl — it is FROZEN HISTORY and "
                  "every new event belongs in a per-seat shard.")
        model.EVENTS = head
        merged = model.read()
        if len(merged) != expected:
            bad += 1
            print("\n🔴 model.read() merged %d of %d events across the shards."
                  % (len(merged), expected))
        if not bad:
            print("\n✅ %d appends, %d seats, %d files, zero torn, zero lost — and "
                  "no two seats shared a file." % (expected, len(SHARD_SEATS), len(names)))
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--writers", type=int, default=8)
    ap.add_argument("--each", type=int, default=200)
    ap.add_argument("--where", default=os.path.join(model.ROOT, "infrastructure", "state"),
                    help="directory to test IN. Defaults to where the ledger lives; "
                         "pass /tmp only to compare filesystems deliberately.")
    a = ap.parse_args()
    real_events = model.EVENTS

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
        return (1 if bad else 0) | sharded(a.where, a.writers, a.each)
    finally:
        model.EVENTS = real_events
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
