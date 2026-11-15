#!/usr/bin/env python3
"""Selftest for record_check.py: a pinned ledger event passes, and every way of it not being there, or having changed,
fails by name. Offline, on a temp ledger; writes nothing in the repo."""
import hashlib, json, os, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record_check as R  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    d = tempfile.mkdtemp(prefix="record_check_")
    try:
        ev = {"seat": "OWNER", "event": "note", "id": "SHEET_X", "ownerSaid": "Ok, I'm approving this whole sheet.",
              "tsn": 1792122659817386516}
        line = json.dumps(ev)
        sha = hashlib.sha256(line.encode()).hexdigest()
        other = json.dumps({"seat": "OWNER", "event": "note", "id": "OTHER", "tsn": 17})
        p = os.path.join(d, "OWNER.jsonl")

        def write(*lines):
            with open(p, "w") as f:
                f.write("\n".join(lines) + "\n")

        def run(**kw):
            a = dict(events_dir=d, seat="OWNER", tsn=ev["tsn"], item="SHEET_X", said="approving this whole sheet", sha=sha)
            a.update(kw)
            return R.check(**a)

        write(other, line)
        good, out = run()
        ok(good and out.startswith("RECORD PASS OWNER.jsonl:2") and sha in out, "the pinned event passes (%s)" % out[:60])
        ok(R.main(["--seat", "OWNER", "--tsn", str(ev["tsn"]), "--id", "SHEET_X", "--sha256", sha,
                   "--events-dir", d]) == 0, "the command line exits 0 on the pinned event")
        write(other)
        good, out = run()
        ok(not good and "0 events" in out, "the event gone fails (%s)" % out)
        write(other, line, line)
        good, out = run()
        ok(not good and "2 events" in out, "two events with that tsn fail (%s)" % out)
        write(line.replace("whole sheet", "whole shelf"))
        good, out = run(said=None)
        ok(not good and "changed" in out, "an edited event fails its hash (%s)" % out)
        write(line)
        good, out = run(said="something he never said")
        ok(not good and "ownerSaid" in out, "words he did not say fail (%s)" % out)
        good, out = run(item="SHEET_Y")
        ok(not good and "id is" in out, "the wrong item id fails (%s)" % out)
        good, out = run(seat="CONDUCTOR")
        ok(not good and "unreadable" in out, "a missing seat shard fails (%s)" % out[:60])
        ok(R.main(["--seat", "OWNER", "--tsn", "1", "--id", "SHEET_X", "--events-dir", d]) == 1,
           "the command line exits 1 when the record is absent")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
