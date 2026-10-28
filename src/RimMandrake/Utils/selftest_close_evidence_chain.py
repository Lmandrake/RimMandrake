#!/usr/bin/env python3
"""selftest_close_evidence_chain.py -- seal-stripping and line deletion are TAMPER, never "absent"
(EVIDENCE_SEALS_HARDEN_STRIPPED_LOOKS_DELETED).

Threat model: accidental or careless edits by our own agents (an agent "fixing" a record by hand: stripping its seals,
editing it, deleting it), not a determined attacker holding the key. Before the fix a line with both seals stripped
read as a pre-seal legacy line, so re-pointing its sha (or deleting the line) made a FAIL vanish without a trace.

Pins: every line written from now on carries `prev` (sha256 of the previous raw line) under its mac, and the day file
has a sealed `<day>.jsonl.head` (byte size + hash of the last line) rewritten under the append lock, so
  * a stripped line, anywhere, is a tamper (the next line's prev, or the head, no longer matches; on/after the
    cutover an unsealed line is a tamper by itself);
  * a deleted line, middle or last, is a tamper (gap in the chain / head beyond the file);
  * a tamper stays visible after later appends (the head carries it forward);
  * normal concurrent appends from many processes are clean;
  * day files before CHAIN_CUTOVER are grandfathered: legacy and unchained lines there are accepted.
A tamper turns every sha lookup into an UNMEASURED close_evidence marker carrying detail.tamper.
Offline: temp store and temp key.
"""
from __future__ import annotations

import json
import multiprocessing
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import close_evidence as CE  # noqa: E402

FAILS: list = []
S1, S2, S3 = "1" * 40, "2" * 40, "3" * 40
POST, PRE = "2000-01-01", "9999-12-31"      # CHAIN_CUTOVER values: today is after / before the cutover


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def put(sha, result="PASS", tool="selftest"):
    return CE.record(tool, result, [], end={"sha": sha, "dirty": False, "dirty_n": 0, "dirty_paths": []})


def day_file(store):
    fs = sorted(store.glob("*.jsonl"))
    return fs[-1] if fs else None


def lines_of(f):
    return f.read_bytes().split(b"\n")[:-1]


def write_lines(f, ls):
    f.write_bytes(b"".join(x + b"\n" for x in ls))


def marker(sha):
    hs = CE.lookup(sha=sha, include_dirty=True)
    mk = [h for h in hs if h["tool"] == "close_evidence"]
    return hs, (mk[0] if mk else None)


def tampered(sha):
    _hs, mk = marker(sha)
    return bool(mk and mk["result"] == "UNMEASURED" and (mk.get("detail") or {}).get("tamper"))


def why(sha):
    _hs, mk = marker(sha)
    return " | ".join((mk or {}).get("detail", {}).get("tamper") or [])


def fresh(td, name):
    store = Path(td) / name
    os.environ[CE.ENV_DIR] = str(store)
    return store


def strip(raw, **edit):
    rec = json.loads(raw)
    rec.pop("mac", None)
    rec.pop("route", None)
    rec.update(edit)
    return json.dumps(rec, sort_keys=True).encode()


def _writer(args):
    store, key, n, tag = args
    os.environ[CE.ENV_DIR] = store
    os.environ[CE.KEY_ENV] = key
    os.environ.pop("RM_SELFTEST_NESTED", None)
    ok = 0
    for i in range(n):
        ok += put(S1 if i % 2 else S2, "PASS", tool="w%s" % tag) is not None
    return ok


def main():
    os.environ.pop("RM_SELFTEST_NESTED", None)
    os.environ.pop("RIMFLOW_ITEM", None)
    with tempfile.TemporaryDirectory() as td:
        os.environ[CE.KEY_ENV] = str(Path(td) / "close_evidence.key")
        CE.CHAIN_CUTOVER = POST

        # 1. a normal day: no marker; every new line is chained and the head is sealed
        store = fresh(td, "normal")
        for s, r in ((S1, "FAIL"), (S2, "PASS"), (S1, "PASS"), (S3, "PASS")):
            put(s, r)
        f = day_file(store)
        recs = [json.loads(x) for x in lines_of(f)]
        check(all("prev" in r for r in recs) and recs[0]["prev"] == "", "every new line carries prev; the first ''")
        check(Path(str(f) + ".head").is_file(), "the day file has a sealed head")
        hs, mk = marker(S1)
        check(mk is None and [h["result"] for h in hs] == ["FAIL", "PASS"], "untouched day: no marker, both runs: %r"
              % [(h["tool"], h["result"]) for h in hs])

        # 2. the reported hole: strip both seals off the FAIL and re-point it at another commit
        ls = lines_of(f)
        write_lines(f, [strip(ls[0], sha=S3)] + ls[1:])
        check(tampered(S1), "stripped + re-pointed FAIL (middle line) -> TAMPER marker for S1, not absent")
        check(tampered(S2), "a tamper is not attributable: every sha lookup sees it")
        check(CE.chain_problems(f.name[:10], lines_of_raw(f), head_of(f), CE._key()) != [],
              "chain_problems names the stripped line")

        # 3. strip the LAST line (no successor whose prev could see it)
        store = fresh(td, "strip_last")
        put(S2), put(S1, "FAIL")
        f = day_file(store)
        ls = lines_of(f)
        write_lines(f, ls[:-1] + [strip(ls[-1], sha=S3)])
        check(tampered(S1), "stripped last line -> TAMPER (head)")

        # 4. delete a middle line / the last line
        store = fresh(td, "del_mid")
        put(S2), put(S1, "FAIL"), put(S2)
        f = day_file(store)
        ls = lines_of(f)
        write_lines(f, [ls[0], ls[2]])
        check("the line before it was deleted" in why(S1), "deleted middle line -> TAMPER (gap in the chain)")
        store = fresh(td, "del_last")
        put(S2), put(S1, "FAIL")
        f = day_file(store)
        write_lines(f, lines_of(f)[:-1])
        check(tampered(S1), "deleted last line -> TAMPER (head beyond the file)")

        # 5. sticky: a later append does not heal a truncation
        put(S2)
        check("sealed bytes" in why(S1), "a truncation stays a TAMPER after the next append: %s" % why(S1))
        os.unlink(str(day_file(store)) + ".head")
        check("head missing" in why(S1), "a deleted head on a chained day -> TAMPER")
        Path(str(day_file(store)) + ".head").write_text('{"size": 1, "last": "x", "broken": [], "mac": "0"}')
        check("head unsealed" in why(S1), "a hand-written head -> TAMPER")

        # 6. edit FAIL -> PASS in place (mac broken) in the middle: tamper too
        store = fresh(td, "edit")
        put(S1, "FAIL"), put(S2)
        f = day_file(store)
        ls = lines_of(f)
        write_lines(f, [ls[0].replace(b'"FAIL"', b'"PASS"')] + ls[1:])
        check("line 2: the line before it" in why(S1), "FAIL edited to PASS (middle) -> TAMPER: %s" % why(S1))
        ls = lines_of(f)
        write_lines(f, [ls[0].replace(b'"PASS"', b'"FAIL"'), ls[1].replace(b'"PASS"', b'"FAIL"')])
        check("last sealed line was edited" in why(S1), "last line edited, same length -> TAMPER (head hash): %s"
              % why(S1))

        # 7. an unsealed hand-written line in a post-cutover file is a TAMPER by itself
        store = fresh(td, "hand")
        put(S2)
        f = day_file(store)
        with f.open("ab") as fh:
            fh.write(json.dumps({"v": 4, "tool": "selftest", "sha": S3, "result": "PASS"}).encode() + b"\n")
        check(tampered(S1), "hand-appended unsealed line after the cutover -> TAMPER")

        # 8. head lost after the very first append (a crash between line and head): not a tamper
        store = fresh(td, "crash_first")
        put(S2)
        f = day_file(store)
        os.unlink(str(f) + ".head")
        check(not tampered(S1), "first line with no head (crash before the head was written) is clean")
        put(S1)
        check(not tampered(S1), "...and the next append re-creates a clean head")
        # head lagging one append behind (crash after a later line): lines beyond the head chain -> clean
        hd = Path(str(f) + ".head").read_bytes()
        put(S2)
        Path(str(f) + ".head").write_bytes(hd)
        check(not tampered(S1), "a head lagging behind chained lines is clean")

        # 9. old records accepted: a pre-cutover file of legacy and unchained sealed lines, no head
        CE.CHAIN_CUTOVER = PRE
        store = fresh(td, "old")
        store.mkdir(parents=True)
        today = CE._days(1)[0]
        old_sealed = CE.seal(CE.build_record("selftest", "PASS", [], end={"sha": S1, "dirty": False, "dirty_n": 0,
                                                                          "dirty_paths": []}))
        old_sealed.pop("prev", None)
        old_sealed = CE.seal(old_sealed)
        legacy = {"v": 2, "ts": today + "T00:00:00+00:00", "tool": "x", "sha": S2, "result": "PASS"}
        f = store / ("%s.jsonl" % today)
        write_lines(f, [json.dumps(legacy, sort_keys=True).encode(), json.dumps(old_sealed, sort_keys=True).encode()])
        hs, mk = marker(S1)
        check(mk is None and len(hs) == 1, "pre-cutover file of old lines, no head: accepted, no marker")
        put(S3)                                           # the first chained line lands in a grandfathered file
        with f.open("ab") as fh:                          # an old-code writer (a clone not yet synced) appends after it
            fh.write(json.dumps(old_sealed, sort_keys=True).encode() + b"\n")
        check(not tampered(S1), "pre-cutover: an unchained line after a chained one (old clone) is accepted")
        put(S3)
        ls = lines_of(f)
        write_lines(f, ls[:2] + [strip(ls[2], sha=S2)] + ls[3:])
        check("seals stripped after the chain began" in why(S1),
              "pre-cutover: stripping a CHAINED line is still a TAMPER: %s" % why(S1))
        CE.CHAIN_CUTOVER = POST

        # 11. (review) the day file deleted but its head left behind: TAMPER, not an empty day
        store = fresh(td, "del_file")
        put(S1, "FAIL")
        f = day_file(store)
        os.unlink(f)
        check("deleted" in why(S1), "day file deleted, head left -> TAMPER: %s" % why(S1))

        # 12. (review) crash before the FIRST head in a pre-cutover file of old lines: clean, and not sticky
        CE.CHAIN_CUTOVER = PRE
        store = fresh(td, "crash_mixed")
        store.mkdir(parents=True)
        f = store / ("%s.jsonl" % today)
        write_lines(f, [json.dumps(old_sealed, sort_keys=True).encode()])
        put(S3)
        os.unlink(str(f) + ".head")
        check(not tampered(S1), "pre-cutover: first chained line after old lines, head lost in a crash -> clean: %s"
              % why(S1))
        put(S3)
        check(not tampered(S1), "...and the next append does not make it a sticky TAMPER: %s" % why(S1))
        CE.CHAIN_CUTOVER = POST

        # 13. (review) the first append of a post-cutover day torn mid-line by a crash: not a sticky TAMPER
        store = fresh(td, "torn_first")
        store.mkdir(parents=True)
        f = store / ("%s.jsonl" % today)
        f.write_bytes(b'{"v": 4, "tool": "selftest", "sha": "' + S2.encode()[:10])
        put(S1)
        check(not tampered(S1), "post-cutover: a torn first line (crash) then a good append -> no TAMPER: %s"
              % why(S1))

        # 10. concurrent appends from several processes: clean
        store = fresh(td, "conc")
        store.mkdir(parents=True)
        n, procs = 12, 8
        with multiprocessing.get_context("spawn").Pool(procs) as pool:
            got = sum(pool.map(_writer, [(str(store), os.environ[CE.KEY_ENV], n, i) for i in range(procs)]))
        f = day_file(store)
        check(got == n * procs and len(lines_of(f)) == n * procs, "concurrent: %d/%d lines written" % (got, n * procs))
        hs, mk = marker(S1)
        check(mk is None and len(hs) == n * procs // 2, "concurrent appends: clean chain, no marker (%d hits, %r)"
              % (len(hs), mk and mk.get("detail")))

    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


def lines_of_raw(f):
    return CE._split_lines(f.read_bytes())


def head_of(f):
    p = Path(str(f) + ".head")
    return p.read_bytes() if p.is_file() else None


if __name__ == "__main__":
    sys.exit(main())
