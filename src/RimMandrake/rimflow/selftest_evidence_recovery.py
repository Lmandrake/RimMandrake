#!/usr/bin/env python3
"""selftest_evidence_recovery.py - evidence.py survives a crash mid-append and sees what the review found it blind to
(RELENTLESS_EVIDENCE_HARDEN_APPEND_RECOVERY; Codex review 2026-11-06). One group per finding; each failed before its fix.

  R1 a crash between the record line and the index line (or torn mid-line, or before HEAD) strands nothing: the next
     locked reader or writer rolls that one append forward; a PENDING that does not fit the files is still tampering
  R2 strict read() and targeted verify() check the index chain: a forged PASS whose index row's `entry` was edited
     without re-hashing the row is refused, and `verify --item --sha` exits 1
  R3 nonce dedupe runs under the append lock: a rival writing the same nonce between check and write is one entry;
     eight processes racing one nonce write one entry
  R4 every directory and file an append creates is made durable in its parent (directory fsync)
  R5 a tail cut from the record AND the index together (two valid prefixes) is caught by HEAD; HEAD deleted from a
     sealed store is caught; a store from before HEAD verifies, and is sealed by its next append
  R6 a short write is completed, a zero-byte write is an error - never a silently truncated line
  R7 harvest reports every failure, and `evidence.py harvest` exits 1 when any receipt failed

Temp stores only.

    python3 src/RimMandrake/rimflow/selftest_evidence_recovery.py
"""
import contextlib
import io
import json
import multiprocessing
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evidence as E    # noqa: E402

FAILS = []
SHA = "a" * 40
REAL = {k: getattr(E, k, None) for k in ("_append_bytes", "_replace", "_locked", "_fsync_dir")}
REAL_WRITE = os.write


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what, flush=True)
    if not cond:
        FAILS.append(what)


def restore():
    for k, v in REAL.items():
        setattr(E, k, v)
    os.write = REAL_WRITE


def fresh(n=2):
    d = tempfile.mkdtemp(prefix="evidence_recovery_")
    for i in range(n):
        E.append(d, "I1", SHA, "run", {"exit": i, "argv": ["a"]})
    return d


def refuses(d, item="I1"):
    try:
        E.append(d, item, SHA, "marker", {"verdict": "PASS"})
        return False
    except E.TamperError:
        return True


def rewrite(path, fn):
    os.chmod(path, 0o644)
    with open(path, encoding="utf-8") as f:
        ls = f.read().splitlines(True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(fn(ls))


class Crash(Exception):
    pass


def crash_at(target, torn=False):
    """The append dies writing `target` ("record" | "index" | "head"); torn: half its bytes are on disk first."""
    def bytes_(path, data):
        is_index = os.path.basename(path) == E.INDEX
        if (target == "index") == is_index and target != "head":
            if torn:
                REAL["_append_bytes"](path, data[:len(data) // 2])
            raise Crash(path)
        return REAL["_append_bytes"](path, data)

    def replace(path, text):
        if target == "head" and os.path.basename(path) == E.HEAD:
            raise Crash(path)
        return REAL["_replace"](path, text)
    E._append_bytes, E._replace = bytes_, replace


def t_crash_recovery():
    for target, torn in (("record", False), ("record", True), ("index", False), ("index", True), ("head", False)):
        d = fresh()
        crash_at(target, torn)
        try:
            E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
            crashed = False
        except Crash:
            crashed = True
        restore()
        what = "a crash writing the %s%s" % (target, " (torn mid-line)" if torn else "")
        ok(crashed and os.path.exists(os.path.join(d, "evidence", E.PENDING)), "R1. %s leaves PENDING" % what)
        ents = E.read(d, "I1", SHA)      # strict: raises if the stranded entry were tamper
        ok([e["kind"] for e in ents] == ["run", "run", "marker"] and ents[-1]["verdict"] == "FAIL",
           "R1. %s is rolled forward by the next reader: %r" % (what, [e["kind"] for e in ents]))
        ok(E.verify_all(d) == {"index": []} and not os.path.exists(os.path.join(d, "evidence", E.PENDING)),
           "R1. after %s the store verifies and PENDING is gone" % what)
        e = E.append(d, "I1", SHA, "marker", {"verdict": "PASS"})
        ok(e["n"] == 3, "R1. after %s the next append is n=3, not TamperError" % what)
        shutil.rmtree(d, ignore_errors=True)

    d = fresh()
    crash_at("index")
    with contextlib.suppress(Crash):
        E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
    restore()
    e = E.append(d, "I1", SHA, "run", {"exit": 9})
    ok(e["n"] == 3 and E.verify_all(d) == {"index": []}, "R1. a writer (not only a reader) rolls the crash forward")
    shutil.rmtree(d, ignore_errors=True)

    d = fresh()     # a power loss before the fsync: the record's new tail is NULs, not the line
    crash_at("record")
    with contextlib.suppress(Crash):
        E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
    restore()
    rec = E.record_path(d, "I1", SHA)
    os.chmod(rec, 0o644)
    with open(rec, "ab") as f:
        f.write(b"\0" * 40)
    ents = E.read(d, "I1", SHA)
    ok([e["kind"] for e in ents] == ["run", "run", "marker"] and E.verify_all(d) == {"index": []},
       "R1. a NUL-filled tail from a power loss is cut back and the append completed")
    shutil.rmtree(d, ignore_errors=True)

    d = fresh()     # a malformed PENDING is reported, never a traceback
    with open(os.path.join(d, "evidence", E.PENDING), "w") as f:
        json.dump({"item": "../x", "sha": SHA, "rec_len": "no", "line": 3, "idx_len": 0, "ix_line": "", "head": {}}, f)
    try:
        bad = E.verify_all(d)["index"]
        crashed = None
    except Exception as ex:     # noqa: BLE001
        bad, crashed = [], ex
    ok(crashed is None and bad and refuses(d), "R1. a malformed PENDING is a reported problem (%r, %r)" % (crashed, bad[:1]))
    shutil.rmtree(d, ignore_errors=True)

    d = fresh()     # a stray file under evidence/ is reported, never a traceback
    with open(os.path.join(d, "evidence", "I1", "notes.jsonl"), "w") as f:
        f.write("{}\n")
    try:
        bad = E.verify_all(d)
        crashed = None
    except Exception as ex:     # noqa: BLE001
        bad, crashed = {}, ex
    ok(crashed is None and bad.get("I1@notes"), "R1. a stray .jsonl under evidence/ is reported (%r)" % (crashed,))
    shutil.rmtree(d, ignore_errors=True)

    d = fresh()
    crash_at("index")
    with contextlib.suppress(Crash):
        E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
    restore()
    rewrite(E.record_path(d, "I1", SHA), lambda ls: ls[:-1] + [ls[-1].replace("FAIL", "PASS")])
    ok(refuses(d) and any(E.verify_all(d).values()), "R1. a PENDING that does not fit the record is still tampering")
    shutil.rmtree(d, ignore_errors=True)


def t_strict_read_index_chain():
    d = fresh(1)
    E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
    rec = E.record_path(d, "I1", SHA)

    def forge(ls):
        e = json.loads(ls[-1])
        e["verdict"] = "PASS"
        e["hash"] = E.entry_hash(e)
        forge.h = e["hash"]
        return ls[:-1] + [json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n"]
    rewrite(rec, forge)
    rewrite(os.path.join(d, "evidence", E.INDEX),
            lambda ls: ls[:-1] + [json.dumps(dict(json.loads(ls[-1]), entry=forge.h), sort_keys=True,
                                             separators=(",", ":")) + "\n"])
    try:
        E.read(d, "I1", SHA)
        raised = False
    except E.TamperError:
        raised = True
    ok(raised, "R2. strict read() refuses a forged PASS vouched for by an un-rehashed index row")
    with contextlib.redirect_stdout(io.StringIO()):
        rc = E.main(["--store-dir", d, "verify", "--item", "I1", "--sha", SHA])
    ok(rc == 1, "R2. targeted `verify --item --sha` exits 1 on it (%s)" % rc)
    shutil.rmtree(d, ignore_errors=True)


def _race(args):
    d, i = args
    return E.append_marker(d, "I1", SHA, "PASS", nonce="same-check") is not None


def t_nonce_under_lock():
    d = fresh(1)
    real_locked = REAL["_locked"]
    fired = []

    @contextlib.contextmanager
    def rival_first(store_dir):
        if not fired:       # another writer lands the same nonce after our check would have run, before our lock
            fired.append(1)
            E._locked = real_locked
            E.append_marker(store_dir, "I1", SHA, "PASS", nonce="n-1")
            E._locked = rival_first
        with real_locked(store_dir):
            yield
    E._locked = rival_first
    try:
        E.append_marker(d, "I1", SHA, "PASS", nonce="n-1")
    finally:
        restore()
    n = sum(1 for e in E.read(d, "I1", SHA) if e.get("nonce") == "n-1")
    ok(n == 1, "R3. a rival writing the same nonce between check and write leaves one entry (%d)" % n)
    shutil.rmtree(d, ignore_errors=True)

    d = fresh(1)
    with multiprocessing.get_context("fork").Pool(8) as pool:
        wrote = pool.map(_race, [(d, i) for i in range(8)])
    n = sum(1 for e in E.read(d, "I1", SHA) if e.get("nonce") == "same-check")
    ok(n == 1 and sum(wrote) == 1, "R3. eight processes racing one nonce write one entry (%d entries, %d wrote)" % (n, sum(wrote)))
    shutil.rmtree(d, ignore_errors=True)


def t_dir_fsync():
    d = tempfile.mkdtemp(prefix="evidence_recovery_")
    synced = []

    def spy(path):
        synced.append(os.path.abspath(path))
        return REAL["_fsync_dir"](path)
    E._fsync_dir = spy
    try:
        E.append(d, "I9", SHA, "run", {"exit": 0})
    finally:
        restore()
    need = {os.path.abspath(d), os.path.abspath(os.path.join(d, "evidence")),
            os.path.abspath(os.path.join(d, "evidence", "I9"))}
    ok(need <= set(synced), "R4. a first append fsyncs every directory it created into (%s missing)" % sorted(need - set(synced)))
    shutil.rmtree(d, ignore_errors=True)


def t_tail_cut():
    d = fresh(1)
    E.append(d, "I1", SHA, "marker", {"verdict": "FAIL"})
    rewrite(E.record_path(d, "I1", SHA), lambda ls: ls[:-1])
    rewrite(os.path.join(d, "evidence", E.INDEX), lambda ls: ls[:-1])
    bad = {k: v for k, v in E.verify_all(d).items() if v}
    ok(bool(bad), "R5. a FAIL cut from the record and the index together is detected: %s" % "; ".join(sum(bad.values(), []))[:140])
    ok(refuses(d), "R5. nothing is appended on top of the coordinated cut")
    shutil.rmtree(d, ignore_errors=True)

    d = fresh(1)
    os.remove(os.path.join(d, "evidence", E.HEAD))
    ok(bool(E.verify_all(d)["index"]) and refuses(d), "R5. HEAD deleted from a sealed store is detected")
    shutil.rmtree(d, ignore_errors=True)

    d = fresh(2)     # a store from before HEAD: no HEAD.json, no sealed rows
    os.remove(os.path.join(d, "evidence", E.HEAD))

    def unseal(ls):
        out = []
        for ln in ls:
            e = json.loads(ln)
            e.pop("sealed", None)
            out.append(e)
        prev = E.ZERO
        for e in out:
            e["prev"] = prev
            e["hash"] = E.entry_hash(e)
            prev = e["hash"]
        return [json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in out]
    rewrite(os.path.join(d, "evidence", E.INDEX), unseal)
    ok(E.verify_all(d) == {"index": []}, "R5. a pre-HEAD store still verifies: %r" % E.verify_all(d))
    E.append(d, "I1", SHA, "run", {"exit": 5})
    ok(os.path.exists(os.path.join(d, "evidence", E.HEAD)) and E.verify_all(d) == {"index": []},
       "R5. its next append seals it (HEAD written, still verifies)")
    shutil.rmtree(d, ignore_errors=True)


def t_short_write():
    d = fresh(1)

    def half(fd, data):
        data = bytes(data)
        return REAL_WRITE(fd, data[:max(1, len(data) // 2)])
    os.write = half
    try:
        E.append(d, "I1", SHA, "run", {"exit": 7, "pad": "x" * 200})
    finally:
        restore()
    ok(E.verify_all(d) == {"index": []} and len(E.read(d, "I1", SHA)) == 2, "R6. short writes are completed, not truncated")
    os.write = lambda fd, data: 0
    try:
        E.append(d, "I1", SHA, "run", {"exit": 8})
        raised = False
    except OSError:
        raised = True
    finally:
        restore()
    ok(raised, "R6. a write that writes nothing is an OSError, not a success")
    shutil.rmtree(d, ignore_errors=True)


def t_harvest_exit():
    d = fresh(1)
    rewrite(os.path.join(d, "evidence", E.INDEX), lambda ls: ["not json\n"] + ls)     # every receipt now refused
    states = [{"item": "I1", "check": {"verdict": "PASS", "nonce": "h1"}, "candidate": {"sha": SHA}}]
    store = types.SimpleNamespace(dir=d, states=lambda: states)
    failed = []
    with contextlib.redirect_stderr(io.StringIO()):
        got = E.harvest(store, failed)
    ok(got == [] and len(failed) == 1, "R7. harvest reports the failed receipt (%r)" % failed)
    fake = types.ModuleType("relentless")
    fake.Store = lambda root=None: store
    saved = sys.modules.get("relentless")
    sys.modules["relentless"] = fake
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = E.main(["--store-dir", d, "harvest"])
    finally:
        if saved is None:
            sys.modules.pop("relentless", None)
        else:
            sys.modules["relentless"] = saved
    ok(rc == 1, "R7. `evidence.py harvest` exits 1 when a receipt failed (%s)" % rc)
    shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    for t in (t_crash_recovery, t_strict_read_index_chain, t_nonce_under_lock, t_dir_fsync, t_tail_cut, t_short_write,
              t_harvest_exit):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
            import traceback
            traceback.print_exc()
            FAILS.append("%s crashed: %s" % (t.__name__, e))
        finally:
            restore()
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
