#!/usr/bin/env python3
"""selftest_delegated_digest_mut.py — kills for the mutation survivors of delegated_digest.py
(DELEGATED_DIGEST_HARDEN_MUTATION_SURVIVORS). The module was rewritten after the SteveDesktop run (c8d1d1285): the
old readers ledger_calls/verdict_calls/commit_calls/art_install_calls/leftover_calls/_group_lines/render are gone;
their successors (ledger_read, verdict_read, commit_read, art_reads, leftovers_read, build's window) are pinned here
on the RAW records they return, so a dropped, misfiled or re-windowed delegated call fails a check.
Writes only under a temp dir. Ends with a reached-the-end check."""
import datetime as dt
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import delegated_digest as D  # noqa: E402

FAILS = []
REACHED = []
UTC = dt.timezone.utc


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def T(h, m=0):
    return dt.datetime(2026, 10, 27, h, m, 0, tzinfo=UTC)


def test_utc_iso():
    check(D.utc("2026-10-27T01:02:03Z") == T(1, 2).replace(second=3), "utc: Z suffix read as UTC")
    check(D.utc("2026-10-27T01:02:03+02:00") == dt.datetime(2026, 10, 26, 23, 2, 3, tzinfo=UTC), "utc: offset converted")
    check(D.utc("2026-10-27T01:02:03Z").tzinfo is not None and D.utc("2026-10-27T01:02:03Z").utcoffset().total_seconds() == 0,
          "utc: aware UTC result")
    n = D.utc("2026-10-27T01:02:03")
    want = dt.datetime(2026, 10, 27, 1, 2, 3).astimezone().astimezone(UTC)
    check(n == want and n.tzinfo is not None, "utc: a naive time is LOCAL, returned aware UTC")
    for bad in (None, "", "garbage", 12345, ["x"], "2026-13-45T00:00:00Z"):
        check(D.utc(bad) is None, "utc: %r -> None" % (bad,))
    check(D.iso(T(5, 6).replace(second=7)) == "2026-10-27T05:06:07Z", "iso format")


def test_decided():
    f = D._decided
    for k in ("decision", "verdict", "overall", "final", "recommended_pick"):
        check(f({k: "X-" + k}) == "X-" + k, "_decided reads key %s" % k)
    check(f({"verdict": "v", "decision": "d"}) == "d", "_decided: decision outranks verdict")
    check(f({"final": "f", "overall": "o"}) == "o", "_decided: overall outranks final")
    check(f({"recommended_pick": "p", "final": "f"}) == "f", "_decided: final outranks recommended_pick")
    check(f({"decision": "  ", "verdict": "v"}) == "v", "_decided: blank string skipped")
    check(f({"decision": 5, "verdict": "v"}) == "v", "_decided: non-string skipped")
    for kk in ("decision", "verdict", "pick"):
        check(f({"overall": {kk: "n-" + kk}}) == "n-" + kk, "_decided nested %s" % kk)
    check(f({"overall": {"decision": "a", "verdict": "b", "pick": "c"}}) == "a", "_decided nested order")
    check(f({"overall": {"decision": 3, "verdict": "b"}}) == "b", "_decided nested non-string skipped")
    check(f({"overall": {"decision": ""}}) == "", "_decided nested empty string still a str")
    check(f({"overall": {"other": "x"}, "final": "later"}) == "later", "_decided: dict without keys falls through")
    check(f({}) is None and f({"decision": None}) is None, "_decided: nothing -> None")


def test_ledger_read():
    check(D.ledger_read(None)["state"] == "unmeasured" and D.ledger_read(None)["fault"] == "unreadable", "ledger None unmeasured")
    base = {"seat": "BENCH", "event": "close", "id": "A_ONE", "sha": "abc", "ranBy": "BENCH", "why": "delegated: scope",
            "ts": "2026-10-27T03:00:00Z", "tsn": 5}
    evs = [dict(base),
           dict(base, event="lease"), dict(base, event="renew"), dict(base, event="release"),
           dict(base, why="not delegated"), dict(base, why=None), dict(base, why=7), dict(base, why="Delegated: scope"),
           dict(base, ts="nope"), dict(base, ts=None), "str", 5, None,
           dict(base, event="note", ts="2026-10-27T04:00:00Z")]
    r = D.ledger_read(evs)
    check(r["state"] == "measured" and r["fault"] == "none", "ledger measured")
    check(len(r["items"]) == 2, "ledger: 2 records kept (lease/renew/release/non-delegated/bad dropped): %d" % len(r["items"]))
    check(r["malformed"] == 5, "ledger: malformed = 2 bad ts + 3 non-dicts: %d" % r["malformed"])
    ident, t, raw = r["items"][0]
    check(t == T(3) and raw["t"] == t, "ledger: t parsed")
    check(raw == {"source": "ledger", "t": T(3), "why": "delegated: scope", "id": "A_ONE", "event": "close",
                  "seat": "BENCH", "ranBy": "BENCH", "sha": "abc"}, "ledger: raw fields exact: %r" % (raw,))
    check(ident.startswith("L") and len(ident) == 41, "ledger: ident L+sha1")
    var = [dict(base), dict(base, seat="X"), dict(base, ts="2026-10-27T03:00:01Z"), dict(base, tsn=6),
           dict(base, event="note"), dict(base, id="B")]
    ids = set(i for i, _t, _r in D.ledger_read(var)["items"])
    check(len(ids) == 6, "ledger: identity separates seat, ts, tsn, event and id (%d of 6)" % len(ids))
    same = D.ledger_read([dict(base), dict(base, sha="zzz", why="delegated: other")])["items"]
    check(same[0][0] == same[1][0], "ledger: identity ignores sha and why")


def git(root, *a, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    e.update(env or {})
    return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, env=e, check=True).stdout


def commit(root, msg, when):
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", msg, env={"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})


def test_git_and_commits():
    with tempfile.TemporaryDirectory() as tmp:
        git(tmp, "init", "-q")
        d = os.path.join(tmp, "dd", "2026-10-27")
        os.makedirs(d)
        open(os.path.join(d, "a.json"), "w").write("{}")
        commit(tmp, "first\n\nDelegated: art accept\nbody line\nDelegated: scope\n not Delegated: indented", "2026-10-27T01:00:00+00:00")
        open(os.path.join(d, "b.json"), "w").write("{}")
        commit(tmp, "second", "2026-10-27T02:00:00+00:00")
        git(tmp, "rm", "-q", "dd/2026-10-27/a.json")
        commit(tmp, "drop a\n\nDelegated: leftover", "2026-10-27T03:00:00+00:00")
        open(os.path.join(d, "a.json"), "w").write("{}")
        commit(tmp, "re-add a", "2026-10-27T04:00:00+00:00")
        added, ok = D.git_added_times(tmp, "dd")
        check(ok is True, "git_added_times ok in a repo")
        check(added == {"dd/2026-10-27/a.json": T(4), "dd/2026-10-27/b.json": T(2)},
              "git_added_times: paths keyed repo-relative, an add after a delete keeps the newest add: %r" % (added,))
        added2, ok2 = D.git_added_times(tmp, "nosuchdir")
        check(ok2 is True and added2 == {}, "git_added_times: no match is measured empty")
        with tempfile.TemporaryDirectory() as plain:
            check(D.git_added_times(plain, "dd") == ({}, False), "git_added_times: not a repo -> ({}, False)")
            check(D.git_added_times(os.path.join(plain, "absent"), "dd") == ({}, False), "git_added_times: missing root")
        r = D.commit_read(tmp)
        check(r["state"] == "measured", "commit_read via git measured")
        got = sorted((raw["class"], raw["t"]) for _i, _t, raw in r["items"])
        check(got == sorted([("art accept", T(1)), ("scope", T(1)), ("leftover", T(3))]),
              "commit_read via git: one record per Delegated: line, class stripped, commit time: %r" % (got,))
        idents = sorted(i.split(":")[-1] for i, _t, _r in r["items"])
        check(idents == ["0", "0", "1"], "commit_read: identity is sha:line index")
        check(all(len(i.split(":")[0]) == 41 for i, _t, _r in r["items"]), "commit_read: identity carries the full sha")
        check(all(it[2]["sha"] and it[2]["source"] == "commit" and it[1] == it[2]["t"] for it in r["items"]), "commit raw fields")
        check(r["malformed"] == 0, "commit_read via git: no malformed")
        with tempfile.TemporaryDirectory() as plain:
            r2 = D.commit_read(plain)
            check(r2["state"] == "unmeasured" and r2["fault"] == "git_failed" and r2["items"] == [], "commit_read: git failure UNMEASURED")
    cm = [("s1", "2026-10-27T01:00:00Z", "subj\n\nDelegated: a\nDelegated:  b  \nnot Delegated: c\nxDelegated: d"),
          ("", "2026-10-27T01:00:00Z", "Delegated: nosha"), ("s3", "bad", "Delegated: nots"), ("s4", None, "Delegated: x"),
          ("s5", "2026-10-27T02:00:00Z", "no marker")]
    r = D.commit_read("/nonexistent", cm)
    check(r["malformed"] == 3, "commit_read: empty sha, bad ts and None ts are malformed: %d" % r["malformed"])
    check([(i, raw["class"]) for i, _t, raw in r["items"]] == [("Cs1:0", "a"), ("Cs1:1", "b")],
          "commit_read: only lines STARTING Delegated:, in order: %r" % ([(i, raw["class"]) for i, _t, raw in r["items"]],))


def test_verdicts():
    with tempfile.TemporaryDirectory() as tmp:
        dd = os.path.join(tmp, "dd")
        os.makedirs(os.path.join(dd, "2026-10-27"))
        os.makedirs(os.path.join(dd, "2026-10-28"))
        import json

        def w(sub, name, body):
            with open(os.path.join(dd, sub, name), "w") as fh:
                fh.write(body if isinstance(body, str) else json.dumps(body))
        w("2026-10-27", "a.json", {"item": "I_ONE", "subject": "SUBJ_A", "class": "art", "decision": "ACCEPT",
                                    "judge_model": {"opus": "x", "gpt": "y"}, "image_sha256": "ab"})
        w("2026-10-27", "plain_name.json", {"class": 5, "subject": 5, "judge_model": "notdict"})
        w("2026-10-28", "bad.json", "{not json")
        w("2026-10-28", "list.json", "[1]")
        w("2026-10-28", "readme.txt", "ignored")
        w("2026-10-28", "dated.json", {"verdict": {"pick": "P"}})
        os.makedirs(os.path.join(dd, "2026-10-28", "deep"))
        w("2026-10-28/deep", "x.json", {"a": 1})
        open(os.path.join(dd, "top.json"), "w").write("{}")
        added = {"dd/2026-10-27/a.json": T(7)}
        os.utime(os.path.join(dd, "2026-10-28", "dated.json"), (1793000000, 1793000000))
        r = D.verdict_read(tmp, dd, added)
        check(r["state"] == "measured" and r["fault"] == "none", "verdict_read measured, fault none when added given")
        check(r["malformed"] == 2, "verdict_read: bad json and non-object counted malformed: %d" % r["malformed"])
        by = {i: (t, raw) for i, t, raw in r["items"]}
        check(sorted(by) == ["Vdd/2026-10-27/a.json", "Vdd/2026-10-27/plain_name.json", "Vdd/2026-10-28/dated.json"],
              "verdict_read: identities are V+repo path; txt, deep and top-level ignored: %r" % sorted(by))
        t, raw = by["Vdd/2026-10-27/a.json"]
        check(t == T(7) and raw["t"] == T(7), "verdict_read: time is the git add time")
        check(raw == {"source": "verdict", "t": T(7), "rel": "dd/2026-10-27/a.json", "item": "I_ONE", "subject": "SUBJ_A",
                      "class": "art", "decision": "ACCEPT", "judge_keys": ["opus", "gpt"], "art": True}, "verdict raw exact: %r" % (raw,))
        t2, raw2 = by["Vdd/2026-10-27/plain_name.json"]
        check(raw2["subject"] == "plain_name" and raw2["class"] is None and raw2["judge_keys"] == [] and raw2["art"] is False
              and raw2["decision"] is None and raw2["item"] is None, "verdict fallbacks: basename subject, class None, no judges, not art")
        check(abs(t2.timestamp() - os.path.getmtime(os.path.join(dd, "2026-10-27", "plain_name.json"))) < 1 and t2.tzinfo is not None,
              "verdict: untracked file's time is its mtime (aware)")
        t3, raw3 = by["Vdd/2026-10-28/dated.json"]
        check(t3 == dt.datetime.fromtimestamp(1793000000, UTC) and raw3["decision"] == "P", "verdict mtime exact, nested pick")
        check(D.verdict_read(tmp, os.path.join(tmp, "absent"), {})["fault"] == "absent", "verdict_read: absent dir unmeasured")
        check(D.verdict_read(tmp, os.path.join(tmp, "absent"), {})["state"] == "unmeasured", "verdict absent state")
        git(tmp, "init", "-q")
        commit(tmp, "empty", "2026-10-27T00:00:00+00:00")
        r2 = D.verdict_read(tmp, dd)          # added=None: git runs; nothing committed
        check(r2["fault"] == "none" and len(r2["items"]) == 3, "verdict_read: git consulted when added is None, fault none")
        with tempfile.TemporaryDirectory() as plain:
            os.makedirs(os.path.join(plain, "dd", "s"))
            open(os.path.join(plain, "dd", "s", "z.json"), "w").write("{}")
            r3 = D.verdict_read(plain, os.path.join(plain, "dd"))
            check(r3["fault"] == "git_failed" and r3["state"] == "measured" and len(r3["items"]) == 1,
                  "verdict_read: git failure still measured by mtime, fault git_failed")
        l = D._list_json(dd)
        check(l == sorted(l) and len(l) == 5 and all(p.endswith(".json") for p in l), "_list_json: depth-1 json only, sorted")
        check(D._list_json(os.path.join(tmp, "absent")) is None, "_list_json: unlistable -> None")


def test_art_and_leftovers():
    ev = [{"type": "ban", "ts": "2026-10-27T01:00:00Z", "id": "E1", "sha": "s", "rel": "r", "reason": "why", "prev": "p"},
          {"type": "unban", "ts": "2026-10-27T01:01:00Z"}, {"type": "ban_hit", "ts": "2026-10-27T01:02:00Z", "id": "E3"},
          {"type": "live", "ts": "2026-10-27T01:03:00Z", "why": "delegated: art marks x", "id": "E4"},
          {"type": "live", "ts": "2026-10-27T01:04:00Z", "why": "other", "reason": "x-delete", "id": "E5"},
          {"type": "live", "ts": "2026-10-27T01:05:00Z", "why": "delegated: art install", "id": "E6", "seat": "BENCH",
           "sha": "sh", "rel": "rr"},
          {"type": "live", "ts": "2026-10-27T01:06:00Z", "why": "not delegated"},
          {"type": "live", "ts": "2026-10-27T01:07:00Z", "why": None},
          {"type": "other", "ts": "2026-10-27T01:08:00Z", "why": "delegated: x"},
          {"type": "ban", "ts": "bad"}, {"type": "live", "ts": "bad", "why": "delegated: z"}, "junk", 3]
    marks, inst = D.art_reads(ev, "delegated: art marks")
    check([i for i, _t, _r in marks["items"]][:1] == ["AE1"] and len(marks["items"]) == 5, "art marks: ban/unban/ban_hit/marks_why/x-delete = 5: %d" % len(marks["items"]))
    check(len(inst["items"]) == 1 and inst["items"][0][0] == "AE6", "art install: only the delegated live install, id-keyed")
    check(marks["malformed"] == 3 and inst["malformed"] == 1, "art malformed: marks=%d inst=%d (want 3,1)" % (marks["malformed"], inst["malformed"]))
    check(marks["items"][0][2] == {"source": "marks", "t": T(1), "type": "ban", "reason": "why", "id": "E1", "sha": "s",
                                   "prev": "p", "rel": "r"}, "marks raw exact")
    check(inst["items"][0][2] == {"source": "art_install", "t": T(1, 5), "why": "delegated: art install", "seat": "BENCH",
                                  "sha": "sh", "rel": "rr"}, "install raw exact")
    check(marks["items"][1][0].startswith("A") and len(marks["items"][1][0]) == 41, "art: no id -> A+hash")
    a, b = D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: q", "sha": "1", "rel": "r"}], "m")[1]["items"], \
        D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: q", "sha": "2", "rel": "r"}], "m")[1]["items"]
    check(a[0][0] != b[0][0], "art: hash identity separates sha")
    c = D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: q", "sha": "1", "rel": "r2"}], "m")[1]["items"]
    check(a[0][0] != c[0][0], "art: hash identity separates rel")
    d = D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:01Z", "why": "delegated: q", "sha": "1", "rel": "r"}], "m")[1]["items"]
    check(a[0][0] != d[0][0], "art: hash identity separates ts")
    m1, i1 = D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "mk", "id": ""}], "mk")
    check(len(m1["items"]) == 1 and m1["items"][0][0].startswith("A") and len(m1["items"][0][0]) == 41, "art: empty id -> hash")
    m2, i2 = D.art_reads([{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: mk"}], "delegated: mk")
    check(len(m2["items"]) == 1 and not i2["items"], "art: marks_why match is a mark, not an install")
    # leftovers
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "acts.jsonl")
        check(D.leftovers_read(p)["fault"] == "absent" and D.leftovers_read(p)["state"] == "unmeasured", "leftovers absent")
        open(p, "w").write('{"ts":"2026-10-27T01:00:00Z","kind":"k1","archive":"a1"}\n\n   \nnot json\n[1]\n'
                           '{"ts":"bad"}\n{"kind":"nots"}\n{"ts":"2026-10-27T02:00:00","kind":"naive"}\n'
                           '{"ts":"2026-10-27T01:00:00Z","kind":"k1","archive":"a1"}\n')
        r = D.leftovers_read(p)
        check(r["state"] == "measured" and r["malformed"] == 4, "leftovers: malformed counts bad json/non-dict/bad ts/no ts: %d" % r["malformed"])
        check(len(r["items"]) == 3, "leftovers: 3 records (blank lines skipped, duplicate line kept): %d" % len(r["items"]))
        i0, t0, raw0 = r["items"][0]
        check(raw0 == {"source": "leftovers", "t": T(1), "kind": "k1", "archive": "a1"} and t0 == T(1), "leftovers raw exact")
        check(i0.startswith("F") and len(i0) == 41 and r["items"][2][0] == i0, "leftovers: identity is the line's sha1")
        check(r["items"][1][2]["t"] == dt.datetime(2026, 10, 27, 2).astimezone().astimezone(UTC), "leftovers: naive time is local")
        check(D.leftovers_read(tmp)["fault"] == "unreadable" and D.leftovers_read(tmp)["state"] == "unmeasured" and D.leftovers_read(tmp)["items"] == [], "leftovers: a directory is unreadable, not absent")


def test_build_window_and_state():
    from contracts import blind as BL
    ids = BL.Identity(frozenset({"A_ONE", "B_TWO"}), frozenset())

    def led(h, i="A_ONE", seat="BENCH"):
        return {"seat": seat, "event": "close", "id": i, "why": "delegated: scope", "ts": "2026-10-27T%02d:00:00Z" % h}
    reads = {s: D._read() for s in D.SOURCES}
    reads["ledger"] = D.ledger_read([led(1), led(2, seat="X"), led(3, seat="Y"), led(4, seat="Z"), led(5, seat="W")])
    idents = [i for i, _t, _r in reads["ledger"]["items"]]
    text, seen = D.build("2026-10-27", T(1), T(4), reads, frozenset({idents[2]}), ids, None)
    check(seen["ledger"] == [idents[1], idents[3]], "build: floor exclusive, cut inclusive, other-digest ident excluded: %r" % (seen["ledger"],))
    check(all(seen[s] == [] for s in D.SOURCES if s != "ledger"), "build: other sources empty")
    text, seen = D.build("2026-10-27", None, T(5), reads, frozenset(), ids, None)
    check(len(seen["ledger"]) == 5, "build: no floor keeps all up to cut")
    text, seen = D.build("2026-10-27", None, T(3), reads, frozenset(), ids, None)
    check(len(seen["ledger"]) == 3, "build: cut inclusive (t == cut kept), later dropped")
    part = {"ledger": reads["ledger"]}
    text, seen = D.build("2026-10-27", None, T(5), part, frozenset(), ids, None)
    check(len(seen["ledger"]) == 5 and seen["verdict"] == [], "build: a missing source reads unmeasured, not a crash")
    # state
    import json
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "s", "st.json")
        check(D.load_state(p) == {"schema": D.STATE_SCHEMA, "floor": None, "digests": {}}, "load_state: absent -> empty v2")
        os.makedirs(os.path.dirname(p))
        open(p, "w").write('{"last_cut": "2026-10-27T01:00:00Z"}')
        check(D.load_state(p) == {"schema": D.STATE_SCHEMA, "floor": "2026-10-27T01:00:00Z", "digests": {}}, "load_state: legacy")
        for body, why in (('{"last_cut": "bad"}', "legacy bad"), ('{"last_cut": 5}', "legacy non-str"), ("[1]", "non-object"),
                          ('{"schema": "x", "floor": null, "digests": {}}', "schema"),
                          ('{"schema": "%s", "floor": "bad", "digests": {}}' % D.STATE_SCHEMA, "floor"),
                          ('{"schema": "%s", "floor": null, "digests": []}' % D.STATE_SCHEMA, "digests type"),
                          ("{oops", "json")):
            open(p, "w").write(body)
            try:
                D.load_state(p)
                check(False, "load_state raises: %s" % why)
            except (ValueError, json.JSONDecodeError):
                check(True, "load_state raises: %s" % why)
        sha = "a" * 64
        good = {"floor": None, "cut": "2026-10-27T01:00:00Z", "complete": True, "page_sha256": sha,
                "seen": {"ledger": ["Lx"]}, "sources": {s: "measured" for s in D.SOURCES}}

        def bad(mod, why, date="2026-10-27"):
            e = dict(good)
            e.update(mod)
            try:
                D._check_entry(date, e)
                check(False, "_check_entry rejects %s" % why)
            except ValueError:
                check(True, "_check_entry rejects %s" % why)
        D._check_entry("2026-10-27", good)
        D._check_entry("2026-10-27", dict(good, out="/x/y.md"))
        check(True, "_check_entry accepts a good entry and an absolute .md out")
        bad({"complete": 1}, "non-bool complete")
        bad({"cut": None}, "null cut")
        bad({"cut": "bad"}, "bad cut")
        bad({"floor": "bad"}, "bad floor")
        bad({"page_sha256": "A" * 64}, "uppercase sha")
        bad({"page_sha256": "a" * 63}, "short sha")
        bad({"out": "rel/y.md"}, "relative out")
        bad({"out": "/x/y.txt"}, "non-md out")
        bad({"out": 5}, "non-str out")
        bad({"extra": 1}, "unknown key")
        bad({"sources": {s: "measured" for s in D.SOURCES[:-1]}}, "missing source")
        bad({"sources": dict({s: "measured" for s in D.SOURCES}, ledger="bogus")}, "bad source state")
        bad({"sources": dict({s: "measured" for s in D.SOURCES}, zzz="measured")}, "extra source")
        bad({"seen": {"nosuch": []}}, "unknown seen source")
        bad({"seen": {"ledger": [""]}}, "empty identity")
        bad({"seen": {"ledger": [[1]]}}, "unhashable identity")
        bad({"seen": {"ledger": "Lx"}}, "seen list type")
        bad({"seen": []}, "seen type")
        bad({}, "bad date", date="2026-13-99")
        try:
            D._check_entry("2026-10-27", [])
            check(False, "_check_entry rejects non-object")
        except ValueError:
            check(True, "_check_entry rejects non-object")
        missing = dict(good)
        del missing["cut"]
        try:
            D._check_entry("2026-10-27", missing)
            check(False, "_check_entry rejects missing field")
        except ValueError:
            check(True, "_check_entry rejects missing field")
        # save/seen/reconcile
        D.save_state(p, {"b": 1, "a": 2})
        check(open(p).read() == '{"a": 2, "b": 1}' and not os.path.exists(p + ".tmp"), "save_state: sorted json, tmp replaced")
        st = {"digests": {"2026-10-26": dict(good, seen={"ledger": ["L1"], "verdict": ["V1"]}),
                          "2026-10-27": dict(good, seen={"ledger": ["L2"]}),
                          "2026-10-25": dict(good, complete=False, seen={"ledger": ["L3"]})}}
        check(D.seen_elsewhere(st, "2026-10-27") == {"L1", "V1"}, "seen_elsewhere: other COMPLETE digests only")
        check(D.seen_elsewhere({}, "x") == set(), "seen_elsewhere: empty")
        page = os.path.join(tmp, "page.md")
        open(page, "w").write("hello")
        h = D._sha256(page)
        check(D._page_ok(page, h) and not D._page_ok(page, "0" * 64) and not D._page_ok(page, "") and not D._page_ok(page, None)
              and not D._page_ok(os.path.join(tmp, "nope"), h), "_page_ok: match only")
        st = {"digests": {"2026-10-27": dict(good, complete=False, page_sha256=h, out=page),
                          "2026-10-26": dict(good, complete=False, page_sha256=h),
                          "2026-10-25": dict(good, complete=False, page_sha256="0" * 64, out=page),
                          "2026-10-24": dict(good, complete=True, page_sha256="0" * 64, out=page)}}
        check(D.reconcile(st, "2026-10-27", "/other") is True, "reconcile: changed")
        d = st["digests"]
        check(d["2026-10-27"]["complete"] is True, "reconcile: pending with matching page -> complete")
        check(d["2026-10-26"]["complete"] is False, "reconcile: entry without out is checked only for today's date")
        st2 = {"digests": {"2026-10-26": dict(good, complete=False, page_sha256=h)}}
        check(D.reconcile(st2, "2026-10-26", page) is True and st2["digests"]["2026-10-26"]["complete"], "reconcile: no out -> today's path")
        check(d["2026-10-25"]["complete"] is False and d["2026-10-24"]["complete"] is True, "reconcile: mismatched stays pending")
        check(D.reconcile({"digests": {"2026-10-24": dict(good)}}, "2026-10-24", page) is False, "reconcile: nothing to do -> False")


def test_second_round():
    import json
    # identity hash: the separator is part of it
    check(D._h("ab", "c") != D._h("a", "bc") and D._h("a", None) != D._h("a", "None ") and len(D._h(1)) == 40, "_h separates its parts")
    # subprocess failures
    real = D.subprocess.run

    class Boom(Exception):
        pass
    for exc in (OSError("no git"), D.subprocess.TimeoutExpired("git", 1)):
        def raiser(*a, **k):
            raise exc
        D.subprocess.run = raiser
        try:
            check(D.git_added_times("/x", "d") == ({}, False), "git_added_times: %s -> ({}, False)" % type(exc).__name__)
            r = D.commit_read("/x")
            check(r["state"] == "unmeasured" and r["fault"] == "git_failed", "commit_read: %s UNMEASURED git_failed" % type(exc).__name__)
        finally:
            D.subprocess.run = real

    class P:
        def __init__(self, out, rc=0):
            self.stdout, self.returncode = out, rc
    D.subprocess.run = lambda *a, **k: P("orphan/path\n@2026-10-27T05:00:00Z\np/new\n\n  p/spaced  \n@2026-10-27T01:00:00Z\np/new\np/old\n")
    try:
        got, ok = D.git_added_times("/x", "d")
        check(ok and got == {"p/new": T(5), "p/spaced": T(5), "p/old": T(1)},
              "git_added_times: a path line before any @ time is skipped, blanks skipped, newest add wins, names stripped: %r" % (got,))
    finally:
        D.subprocess.run = real
    D.subprocess.run = lambda *a, **k: P("x\x1f2026-10-27T01:00:00Z\x1fDelegated: a\x1e\ngarbage-no-separators\x1e\n"
                                          "s2\x1f2026-10-27T02:00:00Z\x1fDelegated: b\n\x1e")
    try:
        r = D.commit_read("/x")
        check(r["malformed"] == 1 and sorted(raw["class"] for _i, _t, raw in r["items"]) == ["a", "b"],
              "commit_read: a chunk that is not sha/time/body is malformed, the rest read: %d %r" % (r["malformed"], r["items"]))
    finally:
        D.subprocess.run = real
    D.subprocess.run = lambda *a, **k: P("", 1)
    try:
        check(D.git_added_times("/x", "d") == ({}, False) and D.commit_read("/x")["fault"] == "git_failed", "non-zero git exit is a failure")
    finally:
        D.subprocess.run = real
    # verdict listing: symlinks are not followed; an unlistable directory is UNMEASURED; 2+ and ordered malformed
    with tempfile.TemporaryDirectory() as tmp:
        dd = os.path.join(tmp, "dd")
        os.makedirs(os.path.join(dd, "2026-10-27"))
        elsewhere = os.path.join(tmp, "elsewhere")
        os.makedirs(elsewhere)
        open(os.path.join(elsewhere, "inside.json"), "w").write("{}")
        open(os.path.join(tmp, "target.json"), "w").write("{}")
        os.symlink(elsewhere, os.path.join(dd, "linkdir"))
        os.symlink(os.path.join(tmp, "target.json"), os.path.join(dd, "2026-10-27", "link.json"))
        open(os.path.join(dd, "2026-10-27", "a_bad.json"), "w").write("{")
        open(os.path.join(dd, "2026-10-27", "b_list.json"), "w").write("[]")
        open(os.path.join(dd, "2026-10-27", "c_num.json"), "w").write("3")
        open(os.path.join(dd, "2026-10-27", "c_trunc.json"), "w").write('{"a": ')
        open(os.path.join(dd, "2026-10-27", "d_ok.json"), "w").write('{"subject": "S"}')
        r = D.verdict_read(tmp, dd, {})
        check([i for i, _t, _r in r["items"]] == ["Vdd/2026-10-27/d_ok.json"],
              "verdict_read: symlinked dir and symlinked file ignored; malformed files do not stop later ones: %r" % ([i for i, _t, _r in r["items"]],))
        check(r["malformed"] == 4, "verdict_read: four malformed counted individually: %d" % r["malformed"])
        realscan = os.scandir

        def deny(path):
            raise PermissionError("denied")
        D.os.scandir = deny
        try:
            r = D.verdict_read(tmp, dd, {})
            check(r["state"] == "unmeasured" and r["fault"] == "unreadable" and r["items"] == [], "verdict_read: unlistable -> UNMEASURED unreadable")
        finally:
            D.os.scandir = realscan
    # art: counts of malformed per target, unmeasured pairs
    ev = [{"type": "ban", "ts": "x"}, {"type": "ban", "ts": "y"}, {"type": "live", "why": "delegated: a", "ts": "x"},
          {"type": "live", "why": "delegated: a", "ts": "y"}, 1, 2]
    m, i = D.art_reads(ev, "m")
    check((m["malformed"], i["malformed"]) == (4, 2), "art_reads: malformed per target accumulates: %r" % ((m["malformed"], i["malformed"]),))
    realart = D._artledger

    def no_import():
        raise ImportError("x")

    class Broken:
        MARKS_WHY = "delegated: art marks"

        @staticmethod
        def cached_index():
            raise RuntimeError("cache")

    class Fine:
        MARKS_WHY = "delegated: MW"

        class _Ix:
            events = [{"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: MW foo", "id": "M1"},
                      {"type": "live", "ts": "2026-10-27T01:00:00Z", "why": "delegated: other", "id": "I1"}]

        @staticmethod
        def cached_index():
            return Fine._Ix
    try:
        D._artledger = no_import
        a, b = D.art_reads(None)
        check((a["state"], a["fault"], b["state"], b["fault"]) == ("unmeasured", "import_failed") * 2, "art_reads: import failure UNMEASURED both")
        D._artledger = lambda: Broken
        a, b = D.art_reads(None)
        check((a["state"], a["fault"], b["state"], b["fault"]) == ("unmeasured", "unreadable") * 2, "art_reads: cache failure UNMEASURED both")
        D._artledger = lambda: Fine
        a, b = D.art_reads(None)
        check([x[0] for x in a["items"]] == ["AM1"] and [x[0] for x in b["items"]] == ["AI1"] and a["state"] == "measured",
              "art_reads: events and MARKS_WHY come from the ledger module")
        a, b = D.art_reads(None, "unused")
        check([x[0] for x in a["items"]] == ["AM1"], "art_reads: ledger's MARKS_WHY overrides the argument")
    finally:
        D._artledger = realart
    saved = list(sys.path)
    try:
        ap = os.path.join(D.SRC, "Utils", "art")
        drop = {os.path.realpath(ap), os.path.realpath(os.path.dirname(ap))}
        sys.path[:] = [x for x in sys.path if os.path.realpath(x) not in drop]
        first = "/sentinel/not/a/dir"
        sys.path.insert(0, first)
        mod = realart()
        check(ap in sys.path and sys.path.index(ap) < sys.path.index(first) and hasattr(mod, "cached_index"),
              "_artledger: Utils/art put ahead of the former first entry, module returned")
        realart()
        check(sys.path.count(ap) == 1, "_artledger: path added once")
    finally:
        sys.path[:] = saved
    # leftovers: undecodable bytes are replaced, not fatal
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "a.jsonl")
        open(p, "wb").write(b'{"ts":"2026-10-27T01:00:00Z","kind":"caf\xe9"}\n{"ts":"2026-10-27T01:00:00Z","kind":"k"}\n')
        r = D.leftovers_read(p)
        check(r["state"] == "measured" and len(r["items"]) == 2 and r["items"][0][2]["kind"] == "caf\ufffd",
              "leftovers: invalid UTF-8 is replaced, the line still counts")
    # gather: every source key present, wired to its reader
    with tempfile.TemporaryDirectory() as tmp:
        g = D.gather([], tmp, os.path.join(tmp, "none"), os.path.join(tmp, "none.jsonl"), added={}, commits=[], art_events=[])
        check(set(g) == set(D.SOURCES) and g["verdict"]["fault"] == "absent" and g["leftovers"]["fault"] == "absent"
              and g["ledger"]["state"] == "measured" and g["commit"]["state"] == "measured" and g["marks"]["state"] == "measured"
              and g["art_install"]["state"] == "measured", "gather: six sources wired")
        g = D.gather([{"seat": "S", "event": "close", "id": "A", "why": "delegated: x", "ts": "2026-10-27T01:00:00Z"}], tmp,
                     os.path.join(tmp, "none"), os.path.join(tmp, "none.jsonl"), added={}, commits=[("c", "2026-10-27T01:00:00Z", "Delegated: k")],
                     art_events=[{"type": "ban", "ts": "2026-10-27T01:00:00Z"}, {"type": "live", "why": "delegated: i", "ts": "2026-10-27T01:00:00Z"}])
        check([len(g[s]["items"]) for s in ("ledger", "commit", "marks", "art_install")] == [1, 1, 1, 1], "gather routes each input to its own source")
    # state
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "st.json")
        good = {"floor": None, "cut": "2026-10-27T01:00:00Z", "complete": False, "page_sha256": "0" * 64, "seen": {},
                "sources": {s: "unmeasured" for s in D.SOURCES}}
        open(p, "w").write(json.dumps({"schema": D.STATE_SCHEMA, "floor": None, "digests": {"2026-10-27": good}}))
        check(D.load_state(p)["digests"]["2026-10-27"] == good, "load_state: null floor, all-zero sha, unmeasured sources accepted")
        open(p, "w").write(json.dumps({"schema": D.STATE_SCHEMA, "floor": None, "digests": {"2026-10-27": dict(good, cut=None)}}))
        try:
            D.load_state(p)
            check(False, "load_state validates every digest entry")
        except ValueError:
            check(True, "load_state validates every digest entry")
        old = os.getcwd()
        os.chdir(tmp)
        try:
            D.save_state("bare.json", {"a": 1})
            check(sorted(os.listdir(tmp)) == ["bare.json", "st.json"], "save_state: a bare filename saves in the cwd, makes no directory: %r" % sorted(os.listdir(tmp)))
        finally:
            os.chdir(old)
        pg = os.path.join(tmp, "pg.md")
        open(pg, "w").write("x")
        realsha = D._sha256

        def oserr(path):
            raise OSError("gone")
        D._sha256 = oserr
        try:
            check(D._page_ok(pg, "a" * 64) is False, "_page_ok: an unreadable page is not ok")
        finally:
            D._sha256 = realsha
        h = D._sha256(pg)
        st = {"digests": {"2026-10-20": dict(good, complete=True), "2026-10-21": dict(good, complete=False, page_sha256=h, out=pg)}}
        stc = {"digests": {"2026-10-22": dict(good, complete=True, page_sha256=h, out=pg)}}
        check(D.reconcile(stc, "2026-10-22", pg) is False, "reconcile: an already-complete entry is not a change")
        check(D.reconcile(st, "2026-10-27", pg) and st["digests"]["2026-10-21"]["complete"],
              "reconcile: a complete entry first does not stop the scan")
    # build's status table is MEASURED from the reads
    from contracts import blind as BL
    ids = BL.Identity(frozenset({"A_ONE"}), frozenset())
    rd = {s: D._read() for s in D.SOURCES}
    rd["ledger"] = D.ledger_read([{"seat": "B", "event": "close", "id": "A_ONE", "why": "delegated: scope", "ts": "2026-10-27T01:00:00Z"},
                                  {"seat": "B", "event": "close", "id": "A_ONE", "why": "delegated: scope", "ts": "2026-10-29T01:00:00Z"}])
    rd["verdict"] = D._read("unmeasured", "absent")
    rd["commit"]["malformed"] = 2
    text, seen = D.build("2026-10-27", None, T(23), rd, frozenset(), ids, None)
    rows = {ln.split("|")[1].strip(): [c.strip() for c in ln.split("|")[2:-1]] for ln in str(text).splitlines() if ln.startswith("| ") and "---" not in ln}
    check((lambda r: r and [r[0], r[1], r[2], r[5]])(rows.get("ledger events")) == ["measured", "1", "0", "2"], "build table: ledger row records 1 / all time 2: %r" % rows.get("ledger events"))
    check(rows.get("judge verdict files", [""])[0] == "UNMEASURED absent", "build table: verdict row UNMEASURED absent: %r" % rows.get("judge verdict files"))
    check(rows.get("Delegated commits", [0, 0, 0])[2] == "2", "build table: commit malformed 2")
    check(rows.get("leftover deletions", [""])[0] == "measured", "build table: untouched source measured")


def test_run_main():
    import argparse
    import contextlib
    import io
    import json
    from contracts import blind as BL
    ids = BL.Identity(frozenset({"A_ONE", "B_TWO"}), frozenset())

    def led(h, i="A_ONE", seat="BENCH"):
        return {"seat": seat, "event": "close", "id": i, "why": "delegated: scope", "ts": "2026-10-27T%02d:00:00Z" % h}

    def reads(*evs, verdict_ok=True):
        r = {s: D._read() for s in D.SOURCES}
        r["ledger"] = D.ledger_read(list(evs))
        if not verdict_ok:
            r["verdict"] = D._read("unmeasured", "absent")
        return r

    def run_main(argv, rd, sources_kind=2):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = D.main(argv, sources=(rd, ids) if sources_kind == 2 else (rd, ids, None))
        return rc, out.getvalue()

    def A(tmp, *extra, date="2026-10-27", out="out"):
        return ["--date", date, "--state", os.path.join(tmp, "state.json"), "--out-dir", os.path.join(tmp, out),
                "--errors", os.path.join(tmp, "errors.log"), "--cut", "2026-10-27T23:00:00Z"] + list(extra)

    def state(tmp):
        return json.load(open(os.path.join(tmp, "state.json")))
    # _dest / handles_dir
    ns = argparse.Namespace
    check(D._dest(ns()) == (D.OUT_DIR, False), "_dest: default production dir")
    check(D._dest(ns(dry_run=True)) == (D.DRY_DIR, False), "_dest: dry run defaults to the dry dir")
    check(D._dest(ns(dry_run=True, out_dir=D.OUT_DIR)) == (D.DRY_DIR, True), "_dest: a dry run aimed at production is redirected and flagged")
    check(D._dest(ns(dry_run=True, out_dir="/x/y")) == ("/x/y", False), "_dest: a dry run keeps its own dir")
    check(D._dest(ns(dry_run=False, out_dir=D.OUT_DIR)) == (D.OUT_DIR, False), "_dest: a real run may write production")
    check(D._dest(ns(dry_run=False, out_dir="/x/y")) == ("/x/y", False), "_dest: out dir honoured")
    check(D.handles_dir(ns(dry_run=True), "/o") == "/o/handles", "handles_dir: dry run under its out dir")
    check(D.handles_dir(ns(dry_run=False, state="/s/t/state.json"), "/o") == "/s/t/handles", "handles_dir: beside the state")
    check(D.handles_dir(ns(state="/s/t/state.json"), "/o") == "/s/t/handles", "handles_dir: no dry_run attribute = a real run")
    # a first run writes page and state
    with tempfile.TemporaryDirectory() as tmp:
        rd = reads(led(1), led(2, "B_TWO"))
        rc, so = run_main(A(tmp), rd)
        page = os.path.join(tmp, "out", "delegated_digest_2026-10-27.md")
        e = state(tmp)["digests"]["2026-10-27"]
        check(rc == 0 and os.path.isfile(page) and "(2 record(s))" in so and "DRY RUN" not in so, "run: writes the page, reports 2 records: %r" % so[-80:])
        check(e["complete"] is True and e["floor"] is None and e["cut"] == "2026-10-27T23:00:00Z" and e["out"] == os.path.abspath(page)
              and e["page_sha256"] == D._sha256(page) and len(e["seen"]["ledger"]) == 2
              and e["sources"] == {s: "measured" for s in D.SOURCES}, "run: state entry complete with floor/cut/out/sha/seen/sources: %r" % (e,))
        # second run: nothing done, stale FAILED marker removed
        failed = os.path.join(tmp, "out", "delegated_digest_2026-10-27.FAILED.md")
        open(failed, "w").write("stale")
        before = open(page).read()
        rc, so = run_main(A(tmp), reads(led(1), led(2, "B_TWO"), led(3)))
        check(rc == 0 and "nothing done" in so and open(page).read() == before and not os.path.exists(failed),
              "run: a complete page => one digest per day, FAILED marker removed: %r" % so[-70:])
        # the page lives where the entry says (entry out wins over this run's out dir)
        rc, so = run_main(A(tmp, out="elsewhere"), reads(led(1)))
        check(rc == 0 and "nothing done" in so and not os.path.exists(os.path.join(tmp, "elsewhere", "delegated_digest_2026-10-27.md")),
              "run: the entry's recorded page path decides completeness, not this run's out dir")
        # page changed => rebuilt, with the entry's own floor, messaging
        st = state(tmp)
        st["floor"] = "2026-10-27T01:30:00Z"
        st["digests"]["2026-10-27"]["floor"] = "2026-10-27T00:30:00Z"
        json.dump(st, open(os.path.join(tmp, "state.json"), "w"))
        open(page, "w").write("tampered")
        rc, so = run_main(A(tmp), reads(led(1), led(2, "B_TWO")))
        e2 = state(tmp)["digests"]["2026-10-27"]
        check("recorded complete but its page is missing or changed; rebuilding it" in so and rc == 0,
              "run: a tampered page is rebuilt with a message: %r" % so[:120])
        check(e2["floor"] == "2026-10-27T00:30:00Z" and len(e2["seen"]["ledger"]) == 2 and e2["complete"],
              "run: a rebuild takes the entry's own floor, not the global one: %r" % (e2["floor"],))
        # lost source: refuse
        open(page, "w").write("tampered again")
        try:
            run_main(A(tmp), reads(led(1), verdict_ok=False))
            check(False, "run: rebuild refused when a source read before is UNMEASURED now")
        except RuntimeError as ex:
            check("refusing to rebuild" in str(ex) and "verdict" in str(ex) and "read before and is UNMEASURED now" in str(ex)
                  and "records would leave the page and its identities the state" in str(ex),
                  "run: rebuild refused, names the lost source: %s" % ex)
        check(state(tmp)["digests"]["2026-10-27"]["complete"] is True, "run: the refusal leaves the state untouched")
        # --force with a lost source is refused too; a dry run is not
        try:
            run_main(A(tmp, "--force"), reads(led(1), verdict_ok=False))
            check(False, "run: --force is refused with a lost source")
        except RuntimeError:
            check(True, "run: --force is refused with a lost source")
        sv = open(os.path.join(tmp, "state.json")).read()
        rc, so = run_main(A(tmp, "--dry-run", out="dry"), reads(led(1), verdict_ok=False))
        check(rc == 0 and "DRY RUN, state untouched" in so and open(os.path.join(tmp, "state.json")).read() == sv
              and os.path.isfile(os.path.join(tmp, "dry", "delegated_digest_2026-10-27.md")), "run: a dry run needs no rebuild guard and never moves the state")
    # floors: global floor applies to a new date; --since in a dry run; bad --since / --cut
    with tempfile.TemporaryDirectory() as tmp:
        json.dump({"schema": D.STATE_SCHEMA, "floor": "2026-10-27T01:30:00Z", "digests": {}}, open(os.path.join(tmp, "state.json"), "w"))
        rc, so = run_main(A(tmp), reads(led(1), led(2), led(3)))
        e = state(tmp)["digests"]["2026-10-27"]
        check(e["floor"] == "2026-10-27T01:30:00Z" and len(e["seen"]["ledger"]) == 2, "run: a new date takes the state's global floor: %r" % ((e["floor"], len(e["seen"]["ledger"])),))
        rc, so = run_main(A(tmp, "--dry-run", "--since", "2026-10-27T02:30:00Z", "--state", os.path.join(tmp, "f1.json"), out="dry"), reads(led(1), led(2), led(3)))
        check("(1 record(s))" in so, "run: a dry run's --since replaces the floor: %r" % so[-60:])
        for bad, why in (("--since", "bad since"), ("--cut", "bad cut")):
            try:
                av = A(tmp, "--dry-run", out="dry2")
                if bad == "--since":
                    av += ["--since", "garbage"]
                else:
                    av[av.index("--cut") + 1] = "garbage"
                run_main(av, reads(led(1)))
                check(False, "run: %s refused" % why)
            except ValueError as ex:
                check(True, "run: %s refused (%s)" % (why, ex))
        try:
            run_main(A(tmp, "--since", "2026-10-27T00:00:00Z"), reads(led(1)))
            check(False, "run: --since without --dry-run refused")
        except ValueError as ex:
            check("only a --dry-run may take it" in str(ex), "run: --since without --dry-run refused")
        try:
            run_main(["--date", "2026-10-27", "--dry-run", "--out-dir", D.OUT_DIR, "--state", os.path.join(tmp, "s2.json")], reads(led(1)))
            check(False, "run: dry run into production refused")
        except ValueError as ex:
            check("never writes the production" in str(ex), "run: dry run into production refused")
        # default cut is now: a future record is excluded, a past one kept
        av = A(tmp, "--state", os.path.join(tmp, "f2.json"), out="nowcut", date="2026-10-29")
        i = av.index("--cut")
        del av[i:i + 2]
        future = led(1)
        future["ts"] = (dt.datetime.now(UTC) + dt.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rc, so = run_main(av, reads(future, led(2)))
        e = json.load(open(os.path.join(tmp, "f2.json")))["digests"]["2026-10-29"]
        check(len(e["seen"]["ledger"]) == 1, "run: no --cut means now; the future record waits")
        check(abs((D.utc(e["cut"]) - dt.datetime.now(UTC)).total_seconds()) < 120, "run: default cut is the present")
        # sources tuple of 3 also accepted; a source missing from reads reads UNMEASURED
        rc, so = run_main(A(tmp, "--dry-run", "--state", os.path.join(tmp, "f3.json"), out="dry3"), {"ledger": D.ledger_read([led(1)])}, 3)
        check(rc == 0 and "(1 record(s))" in so, "run: 3-tuple sources accepted, missing sources tolerated")
        rc, so = run_main(A(tmp, "--state", os.path.join(tmp, "f4.json"), out="miss"), {"ledger": D.ledger_read([led(1)])})
        check(json.load(open(os.path.join(tmp, "f4.json")))["digests"]["2026-10-27"]["sources"] == dict({s: "unmeasured" for s in D.SOURCES}, ledger="measured"),
              "run: a source absent from reads is recorded unmeasured")
    # _load_ledger: any failure -> (None, None)
    import rimflow.model as M
    realread = M.read
    try:
        def boom():
            raise OSError("ledger")
        M.read = boom
        check(D._load_ledger() == (None, None), "_load_ledger: unreadable ledger -> (None, None)")
    finally:
        M.read = realread
    # main: argv handling and pre-launch
    with tempfile.TemporaryDirectory() as tmp:
        saved = sys.argv
        sys.argv = ["prog"] + A(tmp, "--dry-run", out="dry")
        try:
            rc, so = run_main(None, reads(led(1)))
        finally:
            sys.argv = saved
        check(rc == 0 and "(1 record(s))" in so, "main: argv None reads sys.argv[1:]")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                D.main(["--help", "--pre-launch"], sources=None)
            check(False, "main: --help under --pre-launch still exits")
        except SystemExit as ex:
            check(ex.code == 0, "main: --help under --pre-launch exits 0 (not a failure page)")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                D.main(["--no-such-flag"], sources=None)
            check(False, "main: a bad flag without --pre-launch raises SystemExit")
        except SystemExit as ex:
            check(ex.code == 2, "main: a bad flag without --pre-launch exits 2")
        with contextlib.redirect_stderr(io.StringIO()):
            rc = D.main(["--no-such-flag", "--pre-launch", "--date", "2026-10-27", "--out-dir", os.path.join(tmp, "pl"),
                         "--errors", os.path.join(tmp, "pl_errors.log")], sources=None)
        f = os.path.join(tmp, "pl", "delegated_digest_2026-10-27.FAILED.md")
        check(rc == 0 and os.path.exists(f), "main: --pre-launch bad flag -> exit 0 and a FAILED page where --date/--out-dir point")
        p = D._partial(["--date", "2026-10-27", "--bogus", "--out-dir", "/o"])
        check(p is not None and p.date == "2026-10-27" and p.out_dir == "/o", "_partial: the known arguments of a bad command line")
        check(D._partial(5) is None, "_partial: unparseable -> None")
        # _fail
        errs = os.path.join(tmp, "e", "x.log")
        try:
            raise RuntimeError("boom-marker")
        except RuntimeError:
            with contextlib.redirect_stderr(io.StringIO()) as err:
                rc = D._fail(ns(date="nope", out_dir=os.path.join(tmp, "fo"), errors=errs, dry_run=False))
        today = dt.date.today().isoformat()
        ff = os.path.join(tmp, "fo", "delegated_digest_%s.FAILED.md" % today)
        txt = open(errs).read()
        check(rc == 0 and os.path.exists(ff), "_fail: invalid date falls back to today's FAILED page")
        check("boom-marker" in txt and today in txt.splitlines()[0] and txt.splitlines()[0].endswith("Z " + today), "_fail: error log line = iso time, date, traceback: %r" % txt[:60])
        check(open(ff).read() in ("", D.FAILED_TEXT % today) and "FAILED; the Conductor starts anyway" in err.getvalue(), "_fail: fixed text (or blank), stderr notice")
        check(D._failed_text("2026-10-27") in ("", D.FAILED_TEXT % "2026-10-27"), "_failed_text: fixed text or blank")
        rc = D._fail(None)
        check(rc == 0, "_fail never raises, even with no arguments")
        # _errors_path
        od = os.path.join(tmp, "o")
        os.makedirs(od)
        for name, want_err in (("a.log", False), ("a.md", True), ("a.MARKDOWN", True), ("a.html", True), ("a.txt", True), ("a.json", False)):
            got = D._errors_path(ns(errors=os.path.join(tmp, name)), od)
            check((got == D.ERRORS) == want_err, "_errors_path: %s -> %s" % (name, "Operations log" if want_err else "kept"))
        check(D._errors_path(ns(errors=None), od) == D.ERRORS and D._errors_path(ns(), od) == D.ERRORS and D._errors_path(ns(errors=""), od) == D.ERRORS,
              "_errors_path: none -> Operations log")
        check(D._errors_path(ns(errors=od), od) == D.ERRORS, "_errors_path: the page directory itself")
        check(D._errors_path(ns(errors=os.path.join(od, "sub", "e.log")), od) == D.ERRORS, "_errors_path: beneath the page directory")
        check(D._errors_path(ns(errors=os.path.join(tmp, "o2", "e.log")), od) == os.path.join(tmp, "o2", "e.log"), "_errors_path: a sibling with the same prefix is kept")
        check(D._errors_path(ns(errors=os.path.join(D.OUT_DIR, "e.log")), od) == D.ERRORS and D._errors_path(ns(errors=os.path.join(D.DRY_DIR, "e.log")), od) == D.ERRORS,
              "_errors_path: production and dry directories")


def main():
    for t in (test_utc_iso, test_decided, test_ledger_read, test_git_and_commits, test_verdicts, test_art_and_leftovers,
              test_build_window_and_state, test_second_round, test_run_main):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    REACHED.append(1)
    return 1 if FAILS else 0


rc = main()          # no __main__ guard: a mutated guard cannot fake a pass by skipping main
print("REACHED-THE-END")
sys.exit(1 if (rc or not REACHED) else 0)
