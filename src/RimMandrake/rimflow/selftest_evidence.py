#!/usr/bin/env python3
"""selftest_evidence.py - the evidence record's receipts are immutable, appended, and tamper-evident
(RIMFLOW_BUILD_EVIDENCE_RECEIPTS_FIRST, redesign_final.md WP-09a). Owner: "I like replacing the guards with the evidence
already gathered very much".

3. the Marker verdict is appended after the run, never rewritten; the same nonce twice is one entry; harvest appends
   what a store item holds;
4. tampering is detected and nothing is appended on top: an edited line, an edited line re-hashed, a cut tail, a removed
   middle line, a deleted record, a line written around append(), a rewritten index; the files are 0444;
5. the CLI: verify exits 0 on a clean store and 1 on a tampered one.

Temp stores only. (Cases 1 and 2, the retired box run's finish receipts, went with relentless_boxrun.py.)

    python3 src/RimMandrake/rimflow/selftest_evidence.py
"""
import contextlib
import io
import json
import os
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import evidence as E                        # noqa: E402
import run_store                            # noqa: E402

FAILS = []
SHA = "a" * 40
SHA2 = "b" * 40


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what, flush=True)
    if not cond:
        FAILS.append(what)


def t_marker_append():
    d = tempfile.mkdtemp(prefix="evidence_selftest_")
    run = E.append(d, "I1", SHA, "run", {"exit": 0, "argv": ["x"]})
    with open(E.record_path(d, "I1", SHA), "rb") as f:
        before = f.read()
    m = E.append_marker(d, "I1", SHA, "fail", ["b_test_unfair"], session="s1", nonce="n1", reasons="why")
    with open(E.record_path(d, "I1", SHA), "rb") as f:
        after = f.read()
    ok(after.startswith(before) and m["prev"] == run["hash"] and m["n"] == 1 and m["verdict"] == "FAIL",
       "3. the Marker verdict is appended after the run, the run's bytes untouched")
    ok(E.append_marker(d, "I1", SHA, "FAIL", nonce="n1") is None, "3. the same nonce twice is one entry")
    m2 = E.append_marker(d, "I1", SHA, "PASS", nonce="n2")
    es = E.read(d, "I1", SHA)
    ok([e["kind"] for e in es] == ["run", "marker", "marker"] and es[1]["verdict"] == "FAIL" and m2["verdict"] == "PASS",
       "3. a later verdict is another entry; the earlier FAIL is not rewritten")
    try:
        E.append_marker(d, "I1", SHA, "MAYBE")
        ok(False, "3. a non-word verdict is refused")
    except ValueError:
        ok(True, "3. a non-word verdict is refused")
    for bad in (("I1", "HEAD"), ("I1", SHA[:10]), ("../x", SHA), ("..", SHA), (".hidden", SHA)):
        try:
            E.record_path(d, *bad)
            ok(False, "3. record_path refuses %r" % (bad,))
        except ValueError:
            ok(True, "3. record_path refuses %r" % (bad,))

    store = run_store.Store(os.path.join(d, "store_root"))      # harvest: what a store item holds now
    st = {"item": "I0", "status": "checking", "gen": 1}
    st["candidate"] = {"sha": SHA2}
    st["check"] = {"verdict": "WEAK", "nonce": "hn", "reasons": "r", "defects": ["c1"]}
    with store.lock():
        store.save(st)
    got = E.harvest(store)
    got2 = E.harvest(store)
    es = E.read(store.dir, "I0", SHA2)
    ok(got == [("I0", SHA2, "WEAK")] and got2 == [] and len(es) == 1 and es[0]["defects"] == ["c1"],
       "3. harvest appends a held verdict once: %r %r" % (got, got2))
    # REVIEW 2026-11-06: a held verdict with no nonce is still appended once
    st = store.load("I0")
    st["candidate"] = {"sha": SHA2}
    st["check"] = {"verdict": "FAIL", "reasons": "r2", "defects": []}
    with store.lock():
        store.save(st)
    n0 = len(E.read(store.dir, "I0", SHA2))
    E.harvest(store)
    E.harvest(store)
    ok(len(E.read(store.dir, "I0", SHA2)) == n0 + 1, "3b. a nonce-less held verdict is appended once, not every harvest")
    shutil.rmtree(d, ignore_errors=True)


def _fresh():
    d = tempfile.mkdtemp(prefix="evidence_tamper_")
    for i in range(3):
        E.append(d, "I1", SHA, "run", {"exit": i, "argv": ["a"]})
    E.append(d, "I2", SHA, "run", {"exit": 0, "argv": ["a"]})
    return d


def _rewrite(path, fn):
    os.chmod(path, 0o644)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines(True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(fn(lines))


def _dump(e):
    return json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n"


def _rehash(line):
    e = json.loads(line)
    e["exit"] = 0
    e["hash"] = E.entry_hash(e)
    return _dump(e)


def _forged_next(ls):
    """A well-formed next entry: right n, prev and hash - only the index can tell it was not appended."""
    last = json.loads(ls[-1])
    e = dict(last, n=last["n"] + 1, prev=last["hash"], exit=0)
    e["hash"] = E.entry_hash(e)
    return ls + [_dump(e)]


def t_tamper():
    d0 = d = _fresh()
    p = E.record_path(d, "I1", SHA)
    ok(E.verify_all(d) == {"index": []}, "4. a clean store verifies: %r" % E.verify_all(d))
    mode = stat.S_IMODE(os.stat(p).st_mode)
    ok(mode & 0o222 == 0, "4. the record is read-only between appends (%o)" % mode)

    cases = {
        "an edited exit (hash left)": (p, lambda ls: [ls[0], ls[1].replace('"exit":1', '"exit":0'), ls[2]]),
        "an edited line re-hashed": (p, lambda ls: [ls[0], _rehash(ls[1]), ls[2]]),
        "a cut tail": (p, lambda ls: ls[:2]),
        "a removed middle line": (p, lambda ls: [ls[0], ls[2]]),
        "the last line edited and re-hashed": (p, lambda ls: ls[:2] + [_rehash(ls[2])]),
        "a well-formed line written around append()": (p, _forged_next),
        "a rewritten index (one row dropped)": (os.path.join(d, "evidence", E.INDEX), lambda ls: ls[:1] + ls[2:]),
    }
    for what, (path, fn) in cases.items():
        d = _fresh()
        path = path.replace(os.path.dirname(os.path.dirname(os.path.dirname(p))), d, 1)
        _rewrite(path, fn)
        bad = E.verify_all(d)
        flagged = {k: v for k, v in bad.items() if v}
        ok(bool(flagged), "4. %s is detected: %s" % (what, "; ".join(sum(flagged.values(), []))[:150]))
        try:
            E.append(d, "I1", SHA, "marker", {"verdict": "PASS"})
            refused = False
        except E.TamperError:
            refused = True
        ok(refused, "4. nothing is appended on top of %s" % what)
        shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(d0, ignore_errors=True)

    d = _fresh()
    p = E.record_path(d, "I2", SHA)
    os.chmod(p, 0o644)
    os.remove(p)
    bad = E.verify_all(d)
    ok(any("deleted" in x for x in bad.get("I2@%s" % SHA, [])), "4. a deleted record is detected: %r" % bad)
    shutil.rmtree(d, ignore_errors=True)


def t_cli():
    d = _fresh()
    with contextlib.redirect_stdout(io.StringIO()):
        rc0 = E.main(["--store-dir", d, "verify"])
    _rewrite(E.record_path(d, "I1", SHA), lambda ls: ls[:1])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc1 = E.main(["--store-dir", d, "verify"])
    ok(rc0 == 0 and rc1 == 1 and "TAMPERED" in buf.getvalue(), "5. verify exits 0 clean, 1 tampered (%s, %s)" % (rc0, rc1))
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    try:
        for t in (t_marker_append, t_tamper, t_cli):
            t()
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
