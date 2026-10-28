#!/usr/bin/env python3
"""selftest_close_evidence_blast.py -- a TAMPER poisons only what it can cast doubt on (EVIDENCE_CUTOVER_CLONES_SYNC_CHECK).

After 6e771b895c one bad line anywhere in the 30-day window turned EVERY sha lookup UNMEASURED: a single append by a
clone still on the old code after CHAIN_CUTOVER would have blinded every gate. Threat model: careless edits by our own
agents. Pins:
  * a FOREIGN line (an unchained or unsealed line the chain still runs over: an old-code append, a hand-added line)
    hides nothing -- it poisons only lookups for ITS sha, and names its day, line and kind;
  * an old-code first line on a post-cutover day is not a "head missing" tamper of the whole day;
  * a BREAK (a line deleted or edited: the next line's prev does not match) poisons (a) the lookups whose records sit
    on that day from the break on, and (b) the lookups for a sha that already existed when the gap closed
    (commit_time(sha) <= the ts of the line after the break, + slack): a deleted line could have been its FAIL. A sha
    committed after the gap, with records only elsewhere, stays MEASURED; a sha whose commit time cannot be read is
    poisoned (unknown is not "after");
  * an UNLOCATED problem (head missing, unsealed, sticky, bytes gone at the tail) covers its whole UTC day, whose
    gap closes at the day's end;
  * every tamper is alarmed: close_evidence.tamper_findings() names file, line and kind, ops_watch's `evidence`
    family counts it and an alarm target files it with the first finding in the title;
  * GPT review (gpt_review_blast.md) pins: an old-code line cannot hide a deleted chained FAIL (the byte count up to
    the last sealed line, net of proven insertions); a record of the sha written before the gap proves it existed
    whatever its commit clock says; a chained day with no head fails closed; unreadable and seal-broken chained lines
    are alarmed (`unreadable`), not only marked.
Offline: temp store, temp key, injected commit times.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import close_evidence as CE  # noqa: E402

FAILS: list = []
UTC = datetime.timezone.utc
S = {k: (str(k) * 40)[:40] for k in range(1, 10)}
POST = "2000-01-01"


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def end(sha):
    return {"sha": sha, "dirty": False, "dirty_n": 0, "dirty_paths": []}


def put_at(store, when, sha, result="PASS", tool="selftest"):
    rec = CE.build_record(tool, result, [], now=when, end=end(sha))
    return CE._append_chained(store / ("%s.jsonl" % when.date().isoformat()), rec, CE._key(create=True))


def marker(sha, store):
    hs = CE.lookup(sha=sha, include_dirty=True, folder=store)
    mk = [h for h in hs if h["tool"] == "close_evidence"]
    return hs, (mk[0] if mk else None)


def why(sha, store):
    _hs, mk = marker(sha, store)
    return " | ".join(((mk or {}).get("detail") or {}).get("tamper") or [])


def measured(sha, store):
    hs, mk = marker(sha, store)
    return mk is None and any(h["sha"] == sha for h in hs)


def lines_of(f):
    return f.read_bytes().split(b"\n")[:-1]


def write_lines(f, ls):
    f.write_bytes(b"".join(x + b"\n" for x in ls))


def old_code_line(sha, when):
    """What a clone on the pre-chain code appends: a sealed v4 line with no `prev`."""
    rec = CE.build_record("selftest", "PASS", [], now=when, end=end(sha))
    rec.pop("prev", None)
    return json.dumps(CE.seal(rec), sort_keys=True).encode()


def main():
    os.environ.pop("RM_SELFTEST_NESTED", None)
    os.environ.pop("RIMFLOW_ITEM", None)
    real_ct = CE.commit_time
    today = datetime.datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)
    dm1, d0, dp1 = (today - datetime.timedelta(days=k) for k in (3, 2, 1))
    with tempfile.TemporaryDirectory() as td:
        os.environ[CE.KEY_ENV] = str(Path(td) / "close_evidence.key")
        CE.CHAIN_CUTOVER = POST
        early = (dm1 - datetime.timedelta(days=5)).timestamp()

        # 1. one bad write on day D (a line deleted mid-file): scoped, not global
        store = Path(td) / "break"
        store.mkdir()
        put_at(store, dm1, S[1])                                     # D-1: S1, committed long ago
        put_at(store, d0, S[2])                                      # D line 1: S2, committed long ago
        put_at(store, d0 + datetime.timedelta(minutes=1), S[4], "FAIL")      # D line 2: S4's FAIL (to be deleted)
        put_at(store, d0 + datetime.timedelta(minutes=2), S[3])      # D line 3: S3 (after the break)
        put_at(store, d0 + datetime.timedelta(minutes=30), S[5])     # D line 4: S5, committed after the gap
        put_at(store, dp1, S[6])                                     # D+1: S6, committed after the gap
        gap_close = (d0 + datetime.timedelta(minutes=2)).timestamp()
        times = {S[1]: early, S[2]: early, S[3]: early, S[4]: early,
                 S[5]: gap_close + 2 * CE.COMMIT_SLACK_S, S[6]: dp1.timestamp() - 60}
        CE.commit_time = lambda sha: times.get(sha)
        f = store / ("%s.jsonl" % d0.date().isoformat())
        ls = lines_of(f)
        write_lines(f, [ls[0]] + ls[2:])
        check(measured(S[6], store), "break on D: a sha committed after the gap, records on D+1 -> MEASURED: %s"
              % why(S[6], store))
        check("line 2" in why(S[5], store), "break on D: a record AFTER the break on D -> UNMEASURED TAMPER naming the "
              "line, though committed after the gap: %r" % why(S[5], store))
        check("line 2" in why(S[3], store), "break on D: the record right after the break -> TAMPER")
        check("line 2" in why(S[2], store), "break on D: a sha with a record BEFORE the break, existing at the gap -> "
              "TAMPER (the deleted line could be its FAIL)")
        check("line 2" in why(S[1], store), "break on D: a sha on D-1 that existed when the gap closed -> TAMPER")
        times.pop(S[6])
        check(why(S[6], store) != "", "break on D: a sha whose commit time cannot be read -> TAMPER (unknown is not "
              "after)")

        # 2. the alarm: file, line and kind, counted by ops_watch and filed by an alarm target
        fs = CE.tamper_findings(folder=store)
        check(len(fs) == 1 and fs[0]["file"] == str(f) and fs[0]["line"] == 2 and fs[0]["kind"] == "break",
              "tamper_findings names the file, line and kind: %r" % fs)
        os.environ[CE.ENV_DIR] = str(store)
        os.environ.setdefault("RM_OPS_WATCH_DIR", str(Path(td) / "ops"))
        import ops_watch as OW
        pts = OW.c_evidence(0, OW.load_rules(), {})
        pt = pts.get("evidence.tamper") or {}
        check(pt.get("m") == "MEASURED" and pt.get("v") == 1 and f.name in json.dumps((pt.get("x") or {}).get("first")),
              "ops_watch evidence family: evidence.tamper = 1, first finding names the file: %r" % pt)
        filed = []
        st = OW.run_alarms(pts, OW.load_rules(), 1.0e9, set(), lambda todo, conf: filed.extend(todo) or
                           {a["name"]: None for a in todo})
        title = " ".join(a["title"] for a in filed)
        check(filed and f.name in title and "line 2" in title and "break" in title,
              "an alarm target files the tamper with file, line and kind in the title: %r %r" % (filed, st))
        os.environ.pop(CE.ENV_DIR, None)

        # 3. an old-code append (no prev) after the cutover: that line only
        store = Path(td) / "oldcode"
        store.mkdir()
        CE.commit_time = lambda sha: early
        put_at(store, d0, S[1])
        f = store / ("%s.jsonl" % d0.date().isoformat())
        with f.open("ab") as fh:
            fh.write(old_code_line(S[9], d0 + datetime.timedelta(minutes=1)) + b"\n")
        put_at(store, d0 + datetime.timedelta(minutes=2), S[2])
        check(measured(S[1], store) and measured(S[2], store), "old-code append: other shas on the same day stay "
              "MEASURED: %r / %r" % (why(S[1], store), why(S[2], store)))
        check("line 2" in why(S[9], store) and "unchained" in why(S[9], store),
              "old-code append: ITS sha reads TAMPER naming line 2, unchained: %r" % why(S[9], store))
        fs = CE.tamper_findings(folder=store)
        check([(x["line"], x["kind"]) for x in fs] == [(2, "foreign")], "old-code append: exactly one finding, "
              "foreign at line 2: %r" % fs)

        # 4. an old-code line FIRST on a post-cutover day, then chained appends: no whole-day "head missing"
        store = Path(td) / "oldfirst"
        store.mkdir()
        f = store / ("%s.jsonl" % d0.date().isoformat())
        write_lines(f, [old_code_line(S[9], d0)])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[1])
        put_at(store, d0 + datetime.timedelta(minutes=2), S[2])
        check(measured(S[1], store) and measured(S[2], store), "old-code first line: later chained shas MEASURED: %r"
              % why(S[1], store))
        check("line 1" in why(S[9], store), "old-code first line: its own sha flagged at line 1: %r" % why(S[9], store))
        fs = CE.tamper_findings(folder=store)
        check([x["kind"] for x in fs] == ["foreign"], "old-code first line: one foreign finding, no head tamper: %r"
              % fs)

        # 5. a hand-written line INSERTED between two chained lines: the chain still runs over it -> that line only
        store = Path(td) / "insert"
        store.mkdir()
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[2])
        f = store / ("%s.jsonl" % d0.date().isoformat())
        ls = lines_of(f)
        hand = json.dumps({"v": 4, "tool": "selftest", "sha": S[8], "result": "PASS"}).encode()
        write_lines(f, [ls[0], hand, ls[1]])
        check(measured(S[1], store) and measured(S[2], store), "inserted line: the chained shas stay MEASURED: %r / %r"
              % (why(S[1], store), why(S[2], store)))
        check("line 2" in why(S[8], store), "inserted line: its own (plain) sha is flagged at line 2: %r"
              % why(S[8], store))

        # 6. an unlocated problem (head deleted on a chained day): the whole day; the gap closes at the day's end
        store = Path(td) / "nohead"
        store.mkdir()
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[2])
        put_at(store, dp1, S[6])
        os.unlink(str(store / ("%s.jsonl" % d0.date().isoformat())) + ".head")
        eod = datetime.datetime.combine(d0.date() + datetime.timedelta(days=1), datetime.time(), UTC).timestamp()
        times = {S[1]: eod + 2 * CE.COMMIT_SLACK_S, S[2]: eod + 2 * CE.COMMIT_SLACK_S,
                 S[6]: eod + 2 * CE.COMMIT_SLACK_S, S[7]: eod - 60}
        CE.commit_time = lambda sha: times.get(sha)
        check("head missing" in why(S[1], store) and "head missing" in why(S[2], store),
              "head deleted: every record on that day -> TAMPER")
        check(measured(S[6], store), "head deleted: a later-committed sha on the next day -> MEASURED: %r"
              % why(S[6], store))
        check("head missing" in why(S[7], store), "head deleted: a sha that existed during that day -> TAMPER")

        # 8. (GPT review HIGH 1) an old-code line between a chained FAIL and the next chained line: deleting the FAIL
        # leaves every prev matching and the last sealed line in place -- only the byte count before it shows the loss
        store = Path(td) / "oldhides"
        store.mkdir()
        CE.commit_time = lambda sha: early
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[4], "FAIL")
        f = store / ("%s.jsonl" % d0.date().isoformat())
        with f.open("ab") as fh:
            fh.write(old_code_line(S[9], d0 + datetime.timedelta(minutes=2)) + b"\n")
        put_at(store, d0 + datetime.timedelta(minutes=3), S[2])
        ls = lines_of(f)
        write_lines(f, [ls[0]] + ls[2:])
        check("deleted" in why(S[4], store), "old-code line hides a deleted chained FAIL: the FAIL's sha -> TAMPER "
              "(bytes before the last sealed line went missing): %r" % why(S[4], store))
        check("day" in [x["kind"] for x in CE.tamper_findings(folder=store)], "old-code line hides a deletion: a "
              "whole-day finding is alarmed: %r" % CE.tamper_findings(folder=store))
        # ... and a hand line inserted before the last sealed line is not a deletion (its bytes are accounted for)
        store = Path(td) / "insert_ok"
        store.mkdir()
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[2])
        f = store / ("%s.jsonl" % d0.date().isoformat())
        ls = lines_of(f)
        write_lines(f, [ls[0], json.dumps({"v": 4, "sha": S[8]}).encode(), ls[1]])
        check([x["kind"] for x in CE.tamper_findings(folder=store)] == ["foreign"], "inserted hand line: one "
              "foreign finding, no byte-count day finding: %r" % CE.tamper_findings(folder=store))

        # 9. (GPT review HIGH 2) a sha whose commit clock runs ahead but which has a record BEFORE the gap existed then
        store = Path(td) / "skew"
        store.mkdir()
        put_at(store, dm1, S[5])                                     # D-1: S5's PASS, written before the gap
        put_at(store, d0, S[2])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[4], "FAIL")
        put_at(store, d0 + datetime.timedelta(minutes=2), S[3])
        f = store / ("%s.jsonl" % d0.date().isoformat())
        ls = lines_of(f)
        write_lines(f, [ls[0]] + ls[2:])
        gap_close = (d0 + datetime.timedelta(minutes=2)).timestamp()
        CE.commit_time = lambda sha: gap_close + 2 * CE.COMMIT_SLACK_S if sha == S[5] else early
        check("line 2" in why(S[5], store), "commit clock ahead, but a record of the sha precedes the gap -> TAMPER: "
              "%r" % why(S[5], store))
        CE.commit_time = lambda sha: early

        # 10. (GPT review HIGH 3) truncate a chained day to its first line and delete the head: fail closed
        store = Path(td) / "trunc"
        store.mkdir()
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[4], "FAIL")
        f = store / ("%s.jsonl" % d0.date().isoformat())
        write_lines(f, lines_of(f)[:1])
        os.unlink(str(f) + ".head")
        check("head missing" in why(S[4], store), "truncated to the first chained line, head deleted -> TAMPER: %r"
              % why(S[4], store))

        # 11. (GPT review MED 4) an unreadable line and a chained line whose mac fails are alarmed, not only marked
        store = Path(td) / "unread"
        store.mkdir()
        put_at(store, d0, S[1])
        put_at(store, d0 + datetime.timedelta(minutes=1), S[2])
        f = store / ("%s.jsonl" % d0.date().isoformat())
        with f.open("ab") as fh:
            fh.write(b'{"sha": "' + S[3].encode() + b'", torn\n')
        put_at(store, d0 + datetime.timedelta(minutes=2), S[3])
        fs = CE.tamper_findings(folder=store)
        check([(x["line"], x["kind"]) for x in fs] == [(3, "unreadable")], "an unreadable line: one unreadable "
              "finding at line 3: %r" % fs)
        ls = lines_of(f)
        write_lines(f, [ls[0].replace(b'"PASS"', b'"FAIL"')] + ls[1:])
        kinds = sorted((x["line"], x["kind"]) for x in CE.tamper_findings(folder=store))
        check((1, "unreadable") in kinds and (2, "break") in kinds, "a chained line edited (mac fails): unreadable at "
              "line 1 and a break at line 2: %r" % kinds)

        # 7. the default commit_time reads git (this clone's HEAD has one; a made-up sha has none)
        CE.commit_time = real_ct
        head = CE._git(str(HERE), "rev-parse", "HEAD")[1].strip()
        t = CE.commit_time(head)
        check(isinstance(t, (int, float)) and 1.6e9 < t < 4e9, "commit_time(HEAD) reads git: %r" % t)
        check(CE.commit_time("f" * 40) is None, "commit_time of an unknown sha is None")

    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
