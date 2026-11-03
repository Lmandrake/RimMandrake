#!/usr/bin/env python3
"""selftest_driver_death_recurrence.py - driver_death_recurrence.py over hand-made done records (offline).

Proves: CLEAN / RECUR / OTHER DRIVERS classification (a detail naming the result stem without a result is not CLEAN);
a pass resting on an unreadable, misshapen or undated record is UNMEASURED; timestamps compare as times; a damaged or malformed
snapshot is UNMEASURED; a snapshot round-trips to the same verdict as its done dir and
carries each source file's sha256; a missing done dir falls back to the snapshot and says so; the seed sanity probe
refuses (exit 2) when the seed is present but does not read as a recurrence; an empty dir and a too-early --since on a
snapshot are UNMEASURED; and the committed snapshot itself still passes (the item's evidence, MEASURED 2026-11-02).
"""
import contextlib
import gzip
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver_death_recurrence as D  # noqa: E402

FAILS = []


def check(name, cond):
    print("%s %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = D.main(list(argv))
    return rc, buf.getvalue()


def job(d, jid, started, chains, rows, note=""):
    rec = {"job": {"selector": {"chains": chains}},
           "result": {"job": jid, "started": started, "note": note, "rows": rows}}
    with open(os.path.join(d, jid + ".json"), "w", encoding="utf-8") as fh:
        json.dump(rec, fh)


def main():
    tmp = tempfile.mkdtemp(prefix="st_ddr_")
    try:
        done = os.path.join(tmp, "done")
        os.makedirs(done)
        seed = "J20261026T182927Z-seed00"
        db = [{"chain": "drawbridges", "detail": "drawbridge_result_20261028T023918.json: {'toggles': 1}"}]
        job(done, seed, "2026-10-26T18:29:27Z", ["drawbridges"], [], note="jawa/set_fog: client interrupted")
        job(done, "J1", "2026-10-27T01:00:00Z", ["drawbridges"], db)
        job(done, "J2", "2026-10-28T01:00:00Z", ["drawbridges"], db)
        job(done, "J3", "2026-10-29T01:00:00Z", [], db)                       # chain only in rows: still counts
        job(done, "J4", "2026-10-30T01:00:00Z", ["pawn_need"], [{"chain": "pawn_need", "detail":
            "earlier mutating call(s) have an UNKNOWN outcome"}])
        job(done, "J5", "2026-10-31T01:00:00Z", ["drawbridges"], [{"chain": "drawbridges", "detail":
            "UNMEASURED: no drawbridge_result_*.json result at the current mod hash"}])   # names the stem, no result
        base = ["--done-dir", done, "--seed", seed, "--since", "2026-10-26T18:34:00Z"]

        rc, out = run(*base)
        check("3 clean, 0 recur -> exit 0", rc == 0 and "CLEAN 3" in out and "RECUR 0" in out)
        check("other driver listed, not counted", "OTHER DRIVERS 1" in out and "J4" in out)
        check("chain without a result row listed", "J5" in out.split("without a driver-result row")[1])
        check("seed sanity line", "seed %s reads as a recurrence" % seed in out)
        rc, out = run(*base, "--need", "4")
        check("--need 4 -> exit 1", rc == 1 and "FAIL" in out)
        rc, out = run("--done-dir", done, "--seed", seed, "--since", "2026-10-26T18:00:00Z")
        check("seed after --since is a RECUR -> exit 1", rc == 1 and "RECUR 1" in out)

        snap = os.path.join(tmp, "snap.jsonl.gz")
        head = D.write_snapshot(done, snap, since="2026-10-26T18:00:00Z", taken="2026-11-02T00:00:00Z")
        check("snapshot holds every record after its since", head["records"] == 6)
        with gzip.open(snap, "rt", encoding="utf-8") as fh:
            body = [json.loads(ln) for ln in fh][1:]
        with open(os.path.join(done, "J1.json"), "rb") as fh:
            want = hashlib.sha256(fh.read()).hexdigest()
        check("snapshot carries the source sha256", any(r["file"] == "J1.json" and r["sha256"] == want for r in body))
        b1 = open(snap, "rb").read()
        D.write_snapshot(done, snap, since="2026-10-26T18:00:00Z", taken="2026-11-02T00:00:00Z")
        check("snapshot bytes are stable", open(snap, "rb").read() == b1)
        rc, out = run(*base, "--fixture", snap)
        check("snapshot gives the dir's verdict", rc == 0 and "CLEAN 3" in out and "OTHER DRIVERS 1" in out)
        rc, out = run(*base, "--fixture", snap, "--since", "2026-10-26T17:00:00Z")
        check("--since before the snapshot's -> UNMEASURED", rc == 2 and "UNMEASURED" in out)

        D.SNAPSHOT = snap
        rc, out = run(*base[2:], "--done-dir", os.path.join(tmp, "absent"))
        check("absent done dir falls back to the snapshot, loudly",
              rc == 0 and "reading the committed snapshot" in out and "snapshot %s" % snap in out)

        bad = os.path.join(tmp, "bad")
        shutil.copytree(done, bad)
        with open(os.path.join(bad, "bad.json"), "w") as fh:
            fh.write("{not json")
        rc, out = run("--done-dir", bad, "--seed", seed)
        check("a pass resting on an unreadable record -> UNMEASURED", rc == 2 and "(1 unreadable)" in out
              and "bad.json" in out.splitlines()[-1])
        rc, out = run("--done-dir", bad, "--seed", seed, "--need", "4")
        check("a fail with an unreadable record stays FAIL", rc == 1)

        und = os.path.join(tmp, "undated")
        shutil.copytree(done, und)
        job(und, "J6", "", ["drawbridges"], [], note="client interrupted")
        rc, out = run("--done-dir", und, "--seed", seed)
        check("an undated recurrence blocks a pass (dir)", rc == 2 and "J6: no parseable started" in out)
        usnap = os.path.join(tmp, "usnap.jsonl.gz")
        D.write_snapshot(und, usnap, since="2026-10-26T18:00:00Z")
        rc, out = run("--fixture", usnap, "--seed", seed)
        check("an undated recurrence survives the snapshot and blocks a pass", rc == 2 and "J6" in out)

        nores = os.path.join(tmp, "nores")
        shutil.copytree(done, nores)
        with open(os.path.join(nores, "J8.json"), "w") as fh:
            json.dump({"result": None}, fh)
        rc, out = run("--done-dir", nores, "--seed", seed)
        check("a record with no result object blocks a pass (dir)", rc == 2 and "J8.json: no result object" in out)
        nsnap = os.path.join(tmp, "nsnap.jsonl.gz")
        D.write_snapshot(nores, nsnap, since="2026-10-26T18:00:00Z")
        rc, out = run("--fixture", nsnap, "--seed", seed)
        check("a record with no result object survives the snapshot and blocks a pass", rc == 2 and "J8.json" in out)

        for tag, rec in (("sel", {"job": {}, "result": {"job": "J9", "started": "2026-10-30T00:00:00Z",
                                                         "note": "client interrupted", "rows": []}}),
                         ("row", {"job": {"selector": {"chains": ["drawbridges"]}},
                                  "result": {"job": "J9", "started": "2026-10-30T00:00:00Z",
                                             "rows": ["client interrupted"]}}),
                         ("int", {"job": {"selector": {}}, "result": {"job": "J9", "started":
                                                                       "2026-10-30T00:00:00Z", "rows": 1}})):
            sd = os.path.join(tmp, "shape_" + tag)
            shutil.copytree(done, sd)
            with open(os.path.join(sd, "J9.json"), "w") as fh:
                json.dump(rec, fh)
            rc, out = run("--done-dir", sd, "--seed", seed)
            check("misshapen record (%s) blocks a pass, no crash" % tag, rc == 2 and "J9.json:" in out)
            ss = os.path.join(tmp, "shape_%s.jsonl.gz" % tag)
            D.write_snapshot(sd, ss, since="2026-10-26T18:00:00Z")
            rc, out = run("--fixture", ss, "--seed", seed)
            check("misshapen record (%s) survives the snapshot and blocks a pass" % tag, rc == 2 and "J9.json" in out)
        for tag, lines in (("nosince", [{"snapshot": "driver_death_recurrence", "records": 0}]),
                           ("listhead", [[1, 2]]),
                           ("listbody", [{"snapshot": "driver_death_recurrence", "since": "2026-10-26T18:00:00Z",
                                          "records": 1}, [1]])):
            bs = os.path.join(tmp, "bad_%s.jsonl.gz" % tag)
            with gzip.open(bs, "wt", encoding="utf-8") as fh:
                fh.write("".join(json.dumps(x) + "\n" for x in lines))
            rc, out = run("--fixture", bs)
            check("malformed snapshot (%s) is UNMEASURED, not a crash" % tag, rc == 2 and "unreadable" in out)

        frac = os.path.join(tmp, "frac")
        shutil.copytree(done, frac)
        job(frac, "J7", "2026-10-26T18:34:00.500Z", ["drawbridges"], [], note="client interrupted")
        rc, out = run("--done-dir", frac, "--seed", seed)
        check("a fractional-second job after the cutoff is compared as a time", rc == 1 and "RECUR 1" in out)

        broken = os.path.join(tmp, "broken.jsonl.gz")
        raw = bytearray(open(snap, "rb").read())
        for i in range(20, min(len(raw) - 8, 60)):
            raw[i] ^= 0xFF
        open(broken, "wb").write(bytes(raw))
        rc, out = run("--fixture", broken)
        check("a damaged snapshot is UNMEASURED, not a crash", rc == 2 and "unreadable" in out)

        blind = os.path.join(tmp, "blind")
        os.makedirs(blind)
        for n in os.listdir(done):
            shutil.copy(os.path.join(done, n), blind)
        job(blind, seed, "2026-10-26T18:29:27Z", ["drawbridges"], [], note="died quietly")
        rc, out = run("--done-dir", blind, "--seed", seed)
        check("seed present but not a recurrence -> UNMEASURED", rc == 2 and "instrument is blind" in out)

        empty = os.path.join(tmp, "empty")
        os.makedirs(empty)
        rc, out = run("--done-dir", empty)
        check("empty done dir -> UNMEASURED", rc == 2 and "UNMEASURED" in out)
        try:
            run("--done-dir", empty, "--snapshot", os.path.join(tmp, "x.gz"))
            refused = ""
        except SystemExit as ex:
            refused = str(ex)
        check("snapshot of an empty dir is refused", "refused" in refused and not os.path.exists(
            os.path.join(tmp, "x.gz")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    D.SNAPSHOT = os.path.join(HERE, "fixtures", "driver_death_recurrence_snapshot.jsonl.gz")
    rc, out = run("--fixture", D.SNAPSHOT)
    check("committed snapshot: the item's evidence passes", rc == 0 and "seed %s reads as a recurrence" % D.SEED in out)

    print("RESULT: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
