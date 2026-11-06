#!/usr/bin/env python3
"""selftest_evidence_wire_repair.py - RELENTLESS_WIRE_MARKER_VERDICT_AND_REPAIR (WP-09a's two gaps).

1. a real Relentless tick appends the Marker verdict a store item holds, with no manual `evidence.py harvest`
   (relentless.harvest_receipts in _tick); a second tick adds nothing (same nonce); and the detector goes red when the
   tick's call site is planted out;
2. one unparseable index line refuses every receipt; `evidence.repair_index` (and `evidence.py repair-index`) is a dry
   run by default (no byte changes), with --apply backs the whole index up and removes ONLY the unparseable lines, and
   receipts resume; a torn last line is repaired too; above the cap it refuses; a removal that would not make the
   index verify (an edited parseable row beside the junk) is refused and nothing is written; and the detector goes red
   under a planted repair that removes nothing.

Temp stores only; never the real one.

    python3 src/RimMandrake/rimflow/selftest_evidence_wire_repair.py
"""
import contextlib
import io
import os
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import selftest_relentless as T             # noqa: E402  (its Rig: a real tick on a temp store and a fake world)
import evidence as E                        # noqa: E402

FAILS = []
SHA = "c" * 40
SHA2 = "d" * 40


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what, flush=True)
    if not cond:
        FAILS.append(what)


def markers(d, item, sha):
    return [e for e in E.read(d, item, sha, strict=False) if e.get("kind") == "marker"]


# ---------------------------------------------------------------- 1. the tick call site

def plant_verdict(x, item, nonce):
    st = x.st(item)
    st["candidate"] = dict(st.get("candidate") or {}, sha=SHA, gen=st.get("gen") or 1, evidence="planted", at=x.now)
    st["check"] = dict(st.get("check") or {}, verdict="PASS", nonce=nonce, session="sess-1", reasons="planted verdict",
                       defects=[])
    x.s.save(st)


def tick_appends():
    """-> (marker entries after one tick, after a second tick, acts of the first): a verdict planted on a store item
    with no receipt, then the real tick."""
    x = T.Rig(n=1, share=1.0)
    try:
        x.tick()        # the item is enrolled; a clean tick on record
        item = x.s.items()[0]
        plant_verdict(x, item, "nonce-tick-1")
        before = len(markers(x.s.dir, item, SHA))
        acts = x.tick()
        one = len(markers(x.s.dir, item, SHA)) - before
        x.tick()
        two = len(markers(x.s.dir, item, SHA)) - before
        return one, two, acts
    finally:
        x.done()


def t_tick_harvests():
    one, two, acts = tick_appends()
    ok(one == 1, "a tick appends the Marker verdict with no manual harvest (got %d entries)" % one)
    ok(two == 1, "a second tick adds nothing: the same nonce is one entry (got %d)" % two)
    ok(any(a.get("do") == "evidence_harvest" for a in acts), "the tick says what it harvested in its acts")
    real = R.harvest_receipts
    R.harvest_receipts = lambda store, now, acts: []        # planted break: the call site does nothing
    try:
        one_b, _, _ = tick_appends()
    finally:
        R.harvest_receipts = real
    ok(one_b == 0, "RED under a planted break: with the call site out, no tick appends a verdict (got %d)" % one_b)


def t_tick_survives_a_torn_index():
    x = T.Rig(n=1, share=1.0)
    try:
        x.tick()
        item = x.s.items()[0]
        E.append_marker(x.s.dir, "OTHER", SHA2, "PASS", nonce="n0")
        junk(x.s.dir, 1)
        plant_verdict(x, item, "nonce-torn")
        acts = x.tick()
        ok(any(a.get("do") == "evidence_harvest_failed" for a in acts),
           "a torn index: the tick reports the failed receipt (and keeps ticking)")
        ok(not any(a.get("do") == "error" and "evidence" in str(a.get("why")) for a in acts),
           "a torn index never raises out of the tick")
        r = E.repair_index(x.s.dir, apply=True)
        ok(r["applied"], "the index repairs: %s" % (r["refused"],))
        acts = x.tick()
        ok(len(markers(x.s.dir, item, SHA)) == 1, "after the repair the next tick writes the held verdict")
    finally:
        x.done()


# ---------------------------------------------------------------- 2. the index repair

def store():
    d = tempfile.mkdtemp(prefix="ev-repair-")
    E.append_marker(d, "I1", SHA, "PASS", nonce="a")
    E.append_marker(d, "I1", SHA, "FAIL", nonce="b")
    E.append_marker(d, "I2", SHA2, "WEAK", nonce="c")
    return d


def ipath(d):
    return os.path.join(E.base(d), E.INDEX)


def raw(d):
    with open(ipath(d), "rb") as f:
        return f.read()


def put(d, data):
    os.chmod(ipath(d), 0o644)
    with open(ipath(d), "wb") as f:
        f.write(data)
    os.chmod(ipath(d), 0o444)


def junk(d, at, text=b"{\"half\": tr"):
    """An unparseable line inserted before line `at` (1-based) of the index; at past the end appends it."""
    lines = raw(d).split(b"\n")[:-1]
    lines.insert(at - 1, text)
    put(d, b"\n".join(lines) + b"\n")


def appends(d):
    try:
        return bool(E.append_marker(d, "I3", SHA, "PASS", nonce="after-%d" % len(raw(d))))
    except E.TamperError:
        return False


def receipts_resume(repair):
    """-> (refused before, resumed after): a planted corrupt line, `repair` applied, then a receipt."""
    d = store()
    try:
        junk(d, 2)
        refused = not appends(d)
        repair(d, apply=True)
        return refused, appends(d) and not E.verify_index(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_repair():
    refused, resumed = receipts_resume(E.repair_index)
    ok(refused, "one corrupt index line refuses the next receipt (the instance)")
    ok(resumed, "repair-index --apply: receipts resume and the index verifies")
    _, resumed_b = receipts_resume(lambda d, **k: {"applied": True})
    ok(not resumed_b, "RED under a planted break: a repair that removes nothing leaves receipts refused")

    d = store()
    try:
        junk(d, 3, b"\xff\xfe not text")
        before = raw(d)
        r = E.repair_index(d)
        ok(r["bad"] == [3] and r["would_verify"] and not r["applied"] and not r["refused"],
           "dry run names the bad line and that the rest would verify: %s" % r)
        ok(raw(d) == before, "dry run: not one byte of the index changes")
        ok(not os.path.exists(E.repair_backup_dir(d)), "dry run: no backup written")
        r = E.repair_index(d, apply=True)
        ok(r["applied"] and r["backup"] and open(r["backup"], "rb").read() == before,
           "apply: the whole index is backed up byte for byte first")
        ok(not os.path.commonpath([r["backup"], E.base(d)]) == E.base(d), "the backup lives outside evidence/")
        ok(raw(d) == b"".join(x + b"\n" for x in before.split(b"\n") if x and not x.startswith(b"\xff")),
           "apply removes only the unparseable line; every other byte stays")
        ok(not stat.S_IMODE(os.stat(ipath(d)).st_mode) & 0o222, "the repaired index is left read-only")
        ok(E.verify_all(d) == {"index": []}, "every record verifies against the repaired index")
        ok(E.repair_index(d)["refused"].startswith("nothing to repair"), "a clean index: nothing to repair")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = store()
    try:
        put(d, raw(d) + b"{\"torn\":")          # a torn last line, no newline
        ok(not appends(d), "a torn last index line refuses receipts")
        r = E.repair_index(d, apply=True)
        ok(r["applied"] and r["bad"] == [4], "a torn last line is removed: %s" % r)
        ok(appends(d), "receipts resume after a torn tail is repaired")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = store()
    try:
        for at in (1, 3, 5):
            junk(d, at)
        before = raw(d)
        r = E.repair_index(d, apply=True, cap=2)
        ok(r["refused"] and "cap" in r["refused"] and raw(d) == before, "above the cap: refused, nothing written")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = store()
    try:
        lines = raw(d).split(b"\n")
        lines[1] = lines[1].replace(b"\"FAIL\"", b"\"PASS\"")      # an edited row: parseable, its hash broken
        put(d, b"\n".join(lines))
        junk(d, 2)
        before = raw(d)
        r = E.repair_index(d, apply=True)
        ok(r["refused"] and not r["would_verify"] and raw(d) == before,
           "an edited parseable row beside the junk: refused (tampering, not a tear), nothing written: %s" % r["refused"])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_cli():
    d = store()
    try:
        junk(d, 2)
        before = raw(d)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = E.main(["--store-dir", d, "repair-index"])
        ok(rc == 0 and "dry run" in out.getvalue() and raw(d) == before, "CLI: dry run by default, exit 0, no write")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = E.main(["--store-dir", d, "repair-index", "--apply"])
        ok(rc == 0 and "APPLIED" in out.getvalue() and appends(d), "CLI --apply: repaired, receipts resume")
        junk(d, 1)
        junk(d, 2)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = E.main(["--store-dir", d, "repair-index", "--apply", "--cap", "1"])
        ok(rc == 1 and "REFUSED" in out.getvalue(), "CLI: a refusal exits 1")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    old = os.environ.pop("RM_EVIDENCE_REPAIR_BACKUP_DIR", None)
    try:
        for fn in (t_repair, t_cli, t_tick_harvests, t_tick_survives_a_torn_index):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                ok(False, "%s raised %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        if old is not None:
            os.environ["RM_EVIDENCE_REPAIR_BACKUP_DIR"] = old
    print("selftest_evidence_wire_repair: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "ALL PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
