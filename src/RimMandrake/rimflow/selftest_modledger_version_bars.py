#!/usr/bin/env python3
"""Selftest: a mod ledger follows its Design Version's bars and its set-aside evidence
(RIMMANDRAKE_REPAIR_KNOCKBACK_LEDGER_READINESS_STOPS_TICK_HOLDER; page
design/specs/2026-11-25-ledger-follows-version-bars/boundary.md, one test per promise).

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_version_bars

Live failure, 2026-11-25: Explosive Knockback's ledger read 59 bars against 0.2.0's 73 (lock-bars wrote the 14 new
ids to version/locked_bars.json and nothing wrote them to the ledger), and 105 BACKFILL events cited 0.1.0 files that
next-version had set aside in version/previous/0.1.0/ (modledger_backfill_accept.py FAIL 2 of 7). FlowWorks read 57
against 55: his card moved 3 bars to 0.2.0 and added 1, in locked_bars.json only. Gimme Some Slack's VERSION.json
counted 57 bars after his order locked 59.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402

FAIL = []
MOD = "VbTestMod"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def ev(i, kind, subject, body, version="0.1.0"):
    return {"id": "BACKFILL:%04d" % i, "writer": "BACKFILL", "kind": kind, "subject": subject, "body": body,
            "version": version, "ts": "2026-11-25T23:%02d:00Z" % i, "evidence": []}


def vdir(tmp):
    return os.path.join(tmp, "design", "concepts", MOD, "version")


def base():
    return "design/concepts/%s/version/" % MOD


def ledger(tmp, bars=("a", "b"), version="0.2.0"):
    """A temp mod ledger at `version` holding `bars`."""
    M.append(tmp, MOD, "BACKFILL", "version.open", "version", body={"version": version, "text": "Design Version"},
             version=version, evidence=["path:%sVERSION.json" % base()], env_writer=None, views=False)
    for b in bars:
        M.append(tmp, MOD, "BACKFILL", "bar.locked", "bar:" + b, body={"text": "bar " + b},
                 evidence=["path:%slocked_bars.json" % base()], env_writer=None, views=False)


def lockrec(tmp, ids, version="0.2.0", records=1):
    os.makedirs(vdir(tmp), exist_ok=True)
    json.dump({"version": version, "ids": list(ids),
               "history": [{"at": "2026-11-25T%02d:00:00Z" % i} for i in range(records)]},
              open(os.path.join(vdir(tmp), "locked_bars.json"), "w"))


def bars_of(tmp):
    return sorted(M.reduce(M.read(tmp, MOD))["bars"])


def t_a_deferred_bar_leaves_the_version():
    lines = [ev(1, "version.open", "version", {"version": "0.1.0", "text": "Design Version 0.1.0"}),
             ev(2, "bar.locked", "bar:a", {"text": "a"}), ev(3, "bar.locked", "bar:b", {"text": "b"}),
             ev(4, "bar.deferred", "bar:a", {"text": "moved to 0.2.0"}),
             ev(5, "live.run", "bar:a", {"result": "PASS", "bar": "a", "text": "a ran"})]
    st = M.reduce(lines)
    check("a deferred bar leaves the version's bars", sorted(st["bars"]) == ["bar:b"], sorted(st["bars"]))
    check("a deferred bar is kept in bars_deferred", "bar:a" in (st.get("bars_deferred") or {}),
          st.get("bars_deferred"))
    check("a live.run on a deferred bar does not bring it back", "bar:a" not in st["bars"]
          and (st.get("bars_deferred") or {}).get("bar:a", {}).get("verdict") == "PASS", st.get("bars_deferred"))
    st2 = M.reduce(lines + [ev(6, "bar.locked", "bar:a", {"text": "a again"})])
    check("a later bar.locked brings a deferred bar back", sorted(st2["bars"]) == ["bar:a", "bar:b"]
          and "bar:a" not in (st2.get("bars_deferred") or {}), (sorted(st2["bars"]), st2.get("bars_deferred")))
    st3 = M.reduce(lines + [ev(6, "bar.eased", "bar:a", {"text": "a eased"})])
    check("an eased deferred bar stays deferred (only a lock or an add brings it back)",
          "bar:a" not in st3["bars"] and "bar:a" in (st3.get("bars_deferred") or {}), sorted(st3["bars"]))
    check("a deferred bar keeps its status for the index", M._status_of(st, "bar:a") == "deferred",
          M._status_of(st, "bar:a"))
    check("control: with no bar.deferred both bars count", sorted(M.reduce(lines[:3])["bars"]) == ["bar:a", "bar:b"])
    check("a ledger with no deferred bar has no bars_deferred key (its views read as before the key existed)",
          "bars_deferred" not in M.reduce(lines[:3]))


def t_a_set_aside_citation_resolves():
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        os.makedirs(os.path.join(vdir(tmp), "previous", "0.1.0", "in_game", "visit_2"))
        open(os.path.join(vdir(tmp), "previous", "0.1.0", "in_game", "visit_2", "rows.jsonl"), "w").write("{}\n")
        os.makedirs(os.path.join(tmp, "previous", "0.1.0", "docs"))
        open(os.path.join(tmp, "previous", "0.1.0", "docs", "x.md"), "w").write("x\n")
        check("a set-aside version/ path resolves in version/previous/<v>/",
              M.cited_file_exists(tmp, "path:%sin_game/visit_2/rows.jsonl#68" % base()))
        check("a version/ path in neither place is still missing",
              not M.cited_file_exists(tmp, "path:%sin_game/visit_9/rows.jsonl#1" % base()))
        check("a path outside version/ is never looked up in previous/", not M.cited_file_exists(tmp, "path:docs/x.md"))
        check("control: a file at its own path exists",
              M.cited_file_exists(tmp, "path:%sprevious/0.1.0/in_game/visit_2/rows.jsonl" % base()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_sync_bars_levels_the_ledger_with_the_lock():
    import modledger_backfill as B
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        ledger(tmp)
        lockrec(tmp, ["b", "c"])
        r = B.sync_bars(tmp, MOD)
        st = M.reduce(M.read(tmp, MOD))
        check("sync_bars locks the id the ledger lacks and defers the bar not locked",
              r.get("ok") and sorted(st["bars"]) == ["bar:b", "bar:c"] and "bar:a" in (st.get("bars_deferred") or {}),
              (r, sorted(st["bars"])))
        check("sync_bars says what it wrote", r.get("locked") == ["c"] and r.get("deferred") == ["a"], r)
        n = len(M.read(tmp, MOD))
        r2 = B.sync_bars(tmp, MOD)
        check("a second sync_bars writes nothing", r2.get("ok") and not r2.get("locked") and not r2.get("deferred")
              and len(M.read(tmp, MOD)) == n, r2)
        bf = [e for e in M.read(tmp, MOD) if e.get("kind") in ("bar.locked", "bar.deferred")]
        check("every event sync_bars wrote cites locked_bars.json, a file that exists",
              all(M.cited_file_exists(tmp, e["evidence"][0]) for e in bf), [e["evidence"] for e in bf])
        lockrec(tmp, ["a", "b", "c"], records=2)
        r3 = B.sync_bars(tmp, MOD)
        check("a deferred bar locked again by a later record comes back",
              r3.get("locked") == ["a"] and bars_of(tmp) == ["bar:a", "bar:b", "bar:c"], r3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_sync_bars_writes_nothing_it_cannot_read():
    import modledger_backfill as B
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        check("a mod with no ledger: sync_bars returns None", B.sync_bars(tmp, MOD) is None)
        ledger(tmp)
        os.makedirs(vdir(tmp), exist_ok=True)
        r0 = B.sync_bars(tmp, MOD)
        check("an absent locked_bars.json writes nothing and says why",
              isinstance(r0, dict) and not r0.get("ok") and "locked_bars.json" in r0.get("why", "")
              and bars_of(tmp) == ["bar:a", "bar:b"], r0)
        open(os.path.join(vdir(tmp), "locked_bars.json"), "w").write("{not json")
        r1 = B.sync_bars(tmp, MOD)
        check("a malformed locked_bars.json writes nothing and says why",
              isinstance(r1, dict) and not r1.get("ok") and bars_of(tmp) == ["bar:a", "bar:b"], r1)
        lockrec(tmp, ["b", "c"], version="0.1.0")
        r2 = B.sync_bars(tmp, MOD)
        check("a locked_bars.json of another version writes nothing and says why",
              isinstance(r2, dict) and not r2.get("ok") and "0.1.0" in r2.get("why", "")
              and bars_of(tmp) == ["bar:a", "bar:b"], r2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _lock_setup(tmp, bars_total):
    ledger(tmp)
    os.makedirs(vdir(tmp), exist_ok=True)
    json.dump({"mod": MOD, "version": "0.2.0", "state": "locked", "locked_from_commit": "c0ffee",
               "bars_total": bars_total, "measured_from": {"bars_total": "the lock"}},
              open(os.path.join(vdir(tmp), "VERSION.json"), "w"))
    shown = {"design/concepts/%s/record.json" % MOD: {"inventory": [{"id": "b"}]},
             "design/concepts/%s/tree.json" % MOD: {"leaves": [{"id": "c"}, {"id": "d"}]}}
    return lambda c, p: shown.get(p) if c == "c0ffee" else None      # noqa: E731


def t_lock_bars_syncs_the_ledger():
    import maturation as MT
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        show = _lock_setup(tmp, 3)
        r = MT.lock_bars(tmp, MOD, "BENCH", "selftest", show=show, blob=lambda c, p: None)
        check("lock_bars brings the mod ledger level with the ids it records",
              r.get("ok") and bars_of(tmp) == ["bar:b", "bar:c", "bar:d"], (r, bars_of(tmp)))
        check("lock_bars says what the ledger sync did", isinstance(r.get("ledger"), dict)
              and r["ledger"].get("locked") == ["c", "d"] and r["ledger"].get("deferred") == ["a"], r.get("ledger"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        os.makedirs(vdir(tmp))
        json.dump({"mod": MOD, "version": "0.2.0", "state": "locked", "locked_from_commit": "c0ffee"},
                  open(os.path.join(vdir(tmp), "VERSION.json"), "w"))
        shown = {"design/concepts/%s/tree.json" % MOD: {"leaves": [{"id": "c"}]}}
        r = MT.lock_bars(tmp, MOD, "BENCH", "selftest", show=lambda c, p: shown.get(p), blob=lambda c, p: None)
        check("control: a mod with no ledger locks as before (ledger None)", r.get("ok") and r.get("ledger") is None, r)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_lock_bars_keeps_bars_total_level():
    import maturation as MT
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        show = _lock_setup(tmp, 2)
        r = MT.lock_bars(tmp, MOD, "BENCH", "selftest", show=show, blob=lambda c, p: None)
        v = json.load(open(os.path.join(vdir(tmp), "VERSION.json")))
        check("a record of 3 ids sets VERSION.json bars_total 2 -> 3 and says so",
              v.get("bars_total") == 3 and r.get("bars_total") == {"was": 2, "now": 3}
              and "locked_bars.json" in v["measured_from"]["bars_total"], (v.get("bars_total"), r.get("bars_total")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tmp = tempfile.mkdtemp(prefix="sel_mlvb_")
    try:
        show = _lock_setup(tmp, 3)
        p = os.path.join(vdir(tmp), "VERSION.json")
        before = open(p).read()
        r = MT.lock_bars(tmp, MOD, "BENCH", "selftest", show=show, blob=lambda c, p: None)
        check("control: a bars_total already level is not rewritten", open(p).read() == before
              and r.get("bars_total") is None, r.get("bars_total"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    for t in (t_a_deferred_bar_leaves_the_version, t_a_set_aside_citation_resolves,
              t_sync_bars_levels_the_ledger_with_the_lock, t_sync_bars_writes_nothing_it_cannot_read,
              t_lock_bars_syncs_the_ledger, t_lock_bars_keeps_bars_total_level):
        t()
    print("selftest_modledger_version_bars: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
