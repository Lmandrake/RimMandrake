#!/usr/bin/env python3
"""Proves model.write_bridge_file() survives concurrent writers.

🔴 WHY THIS EXISTS. Code review, 2026-09-02, on the bridge-handoff commit found
`write_bridge_file` opened a FIXED tmp path (`target + ".tmp"`) with O_TRUNC before
ever acquiring its flock — O_TRUNC fires at open(), and truncation is not fd-local,
so two windows calling this within the same instant (exactly the BENCH/FOUNDRY
scenario this file exists for) could interleave: the second writer's O_TRUNC wipes
the first writer's not-yet-renamed content, or the first writer's own os.replace()
chases a tmp name the second writer already renamed away and raises
FileNotFoundError. Fixed by giving every call a per-process-unique tmp name (see
model.py's own comment at the fix site) — this is the test that proves it, not just
asserts it, same discipline selftest_concurrency.py already applies to append().

Unlike append() (an append-only ledger, where the claim is "no line is lost or
torn"), write_bridge_file() is a LAST-WRITER-WINS MIRROR — concurrent writers are
expected to overwrite each other, that is correct. The claim under test here is
narrower and still real: no writer's call may ever RAISE (the FileNotFoundError
race), and whatever ends up on disk when everyone is done must be exactly one
writer's COMPLETE, well-formed body — never a torn hybrid of two.

    python3 src/RimMandrake/rimflow/selftest_bridge_file_concurrency.py [--writers 16] [--rounds 30]
"""
import argparse
import multiprocessing
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                        # noqa: E402


def writer(args):
    where, wid, rounds = args
    os.environ["RIMFLOW_LEDGER"] = os.path.join(where, "events.jsonl")
    errors = []
    for i in range(rounds):
        try:
            model.write_bridge_file(
                holder="WRITER_%d" % wid, actor=None,
                purpose="round %d" % i, since="2026-09-02T00:00:00Z")
        except Exception as e:                                    # noqa: BLE001
            errors.append("writer %d round %d: %s: %s" % (wid, i, type(e).__name__, e))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--writers", type=int, default=16)
    ap.add_argument("--rounds", type=int, default=30)
    # 🔴 SAME 9p LESSON selftest_concurrency.py's own header names: default under
    # the repo (on the real mount this bug was found on), not /tmp.
    ap.add_argument("--where", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(HERE))), ".rimflow_selftest_bridgefile"))
    args = ap.parse_args()

    if os.path.exists(args.where):
        shutil.rmtree(args.where)
    os.makedirs(args.where)
    try:
        target = os.path.join(args.where, "BRIDGE")

        with multiprocessing.Pool(args.writers) as pool:
            results = pool.map(writer, [(args.where, w, args.rounds) for w in range(args.writers)])

        all_errors = [e for errs in results for e in errs]
        if all_errors:
            print("FAIL — %d error(s) during concurrent writes:" % len(all_errors))
            for e in all_errors[:10]:
                print("  " + e)
            return 1

        if not os.path.isfile(target):
            print("FAIL — no BRIDGE file exists after %d concurrent writers" % args.writers)
            return 1
        with open(target, encoding="utf-8") as fh:
            body = fh.read()
        # A well-formed body is exactly one writer's complete write: the 5-line
        # header, then a HELD line naming exactly one WRITER_<n>, then a `for` line
        # — never a header from one write spliced to a body from another, and never
        # truncated mid-line.
        lines = body.splitlines()
        ok = (
            len(lines) == 7
            and lines[5].startswith("HELD    WRITER_")
            and lines[6].startswith("for     round ")
        )
        if not ok:
            print("FAIL — final BRIDGE file is not one complete writer's body (torn write):")
            print(body)
            return 1

        print("ok    %d writers x %d rounds, zero errors, final file is one complete body"
              % (args.writers, args.rounds))
        print("\n1/1 passed")
        return 0
    finally:
        shutil.rmtree(args.where, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
