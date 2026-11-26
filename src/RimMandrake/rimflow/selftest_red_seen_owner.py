#!/usr/bin/env python3
"""selftest_red_seen_owner: the promises of design/specs/2026-11-20-red-seen-owner/boundary.md, one test per promise,
each named as the promise is. A certificate that refuses on red_seen alone used to launch nothing (Gimme Some Slack sat
from 2:14 AM to about 4:50 AM PST on 2026-11-20); now it launches one run that records the proof, resuming the run that
edited the decider when that run is warm (item RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION). No game,
no network, no real launch."""
import datetime
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="red_seen_owner_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import judge_certificate as JC  # noqa: E402
import maturation_dispatch as MD  # noqa: E402
import probe_result as PR  # noqa: E402

MOD = "WMod"
NOW = 1795170000.0
CFG = {"cap_tokens": 2_500_000, "max_live": 2, "launch_tries": 3, "settle_s": 180, "seat": "BENCH", "model": "opus"}


def cert(*rows):
    return {"ok": False, "rows": [dict(status="REFUSED", bar=b, test=t, clause=c) for t, b, c in rows]}


def decide(f, s=None):
    row, put = {"mod": MOD}, []
    f = dict({"stage": "offline_build", "spend": []}, **f)
    got = MD.cert_red_decide(CFG, s if s is not None else {}, f, row, lambda *a: put.append(a), NOW,
                             (True, "account ok"), 0, CFG["cap_tokens"])
    return got, row, put


RS = cert(("T_CORE", "b1", "red_seen"), ("T_STUB_JOINS", "b2", "red_seen"))


def t_red_seen_only_launches():
    got, row, _ = decide({"certificate": RS})
    return (got == "launch" and row.get("cert_kind") == "red_seen"
            and row.get("cert_reds") == ["T_CORE", "T_STUB_JOINS"]), (got, row)


def t_mixed_refusal_keeps_its_route():
    red, rrow, _ = decide({"certificate": cert(("T_CORE", "b1", "red_seen"), ("T_A", "b3", "green"))})
    other, orow, _ = decide({"certificate": cert(("T_CORE", "b1", "red_seen"), ("T_B", "b4", "registered"))})
    stale, _, _ = decide({"certificate": cert(("T_CORE", "b1", "red_seen"), ("T_C", "b5", "ran_on_this_build"))})
    return (red == "launch" and rrow.get("cert_kind") == "red" and rrow.get("cert_reds") == ["T_A"]
            and other is None and stale is None), (red, rrow.get("cert_kind"), other, stale)


def t_one_try_per_set():
    s = {"cert_red_seen": {"tests": ["T_CORE", "T_STUB_JOINS"], "unit": "u1", "at": NOW - 3600, "failed": None}}
    again, _, put = decide({"certificate": RS}, s)
    s2 = {"cert_red": {"tests": ["T_CORE", "T_STUB_JOINS"], "unit": "u0", "at": NOW - 3600, "failed": None}}
    other, row2, _ = decide({"certificate": RS}, s2)
    return (again == "decided" and any(p[0] == "stopped" for p in put)
            and other == "launch" and row2.get("cert_kind") == "red_seen"), (again, put, other)


def t_a_new_set_gets_its_own_try():
    """Pyrelands, 2026-11-23 4:17 AM PST: a red_seen run on T_FUZZ and T_SETTINGS_SCREENS (2026-11-22) cleared both;
    an edit at f7773e31d1 then owed T_SITE alone, and the tick read the disjoint set as "the same reds" and stopped the
    mod (RIMMANDRAKE_UNPAUSE_PYRELANDS_SITE_DECIDER_RED_AFTER_VISIT_SIX_PASSED). A set that shares no test with the last
    try's launches; a set that still holds a test the last try was on stays stopped."""
    old = {"tests": ["T_FUZZ", "T_SETTINGS_SCREENS"], "unit": "u-old", "at": NOW - 40000, "failed": None}
    new, nrow, _ = decide({"certificate": cert(("T_SITE", "b1", "red_seen"))}, {"cert_red_seen": dict(old)})
    redn, rrow, _ = decide({"certificate": cert(("T_SITE", "b1", "green"))}, {"cert_red": dict(old)})
    kept, _, kput = decide({"certificate": cert(("T_FUZZ", "b1", "red_seen"), ("T_SITE", "b2", "red_seen"))},
                           {"cert_red_seen": dict(old)})
    return (new == "launch" and nrow.get("cert_reds") == ["T_SITE"] and redn == "launch"
            and rrow.get("cert_reds") == ["T_SITE"] and kept == "decided" and any(p[0] == "stopped" for p in kput)), \
        (new, redn, kept, kput)


def cert_proved(*rows):
    return {"ok": False, "rows": [dict(status="REFUSED", bar=b, test=t, clause="red_seen", proof_at=at)
                                  for t, b, at in rows]}


def t_a_proof_recorded_since_the_try_is_a_new_debt():
    """Gimme Some Slack, 2026-11-23 7:20 PM PST: a try of 2026-11-21 on T_CORE, T_STUB_JOINS and T_SWITCH_LIGHT_OFFLINE
    was paid (each red proof recorded on 11-23, after the try), the wall-plug fix then edited the test files again, and
    the tick read the new debt as "the same reds" and stopped the mod."""
    old = {"tests": ["T_CORE", "T_STUB_JOINS", "T_LIGHT"], "unit": "u-old", "at": NOW - 200000, "failed": None,
           "stage": "offline_build"}
    since, before = PR_ISO(NOW - 3600), PR_ISO(NOW - 300000)

    def one(*rows):
        got, _, put = decide({"certificate": cert_proved(*rows)}, {"cert_red_seen": dict(old)})
        return got, put
    paid = one(("T_CORE", "b1", since), ("T_STUB_JOINS", "b2", since), ("T_NEW", "b3", None))
    unpaid = one(("T_CORE", "b1", before), ("T_NEW", "b3", None))         # the proof is older than the try
    none = one(("T_CORE", "b1", None), ("T_NEW", "b3", None))             # the try recorded nothing
    part = one(("T_CORE", "b1", since), ("T_STUB_JOINS", "b2", None), ("T_NEW", "b3", None))
    bad = one(("T_CORE", "b1", "not a time"), ("T_NEW", "b3", None))      # an unreadable time pays nothing
    return (paid[0] == "launch" and all(x[0] == "decided" and any(p[0] == "stopped" for p in x[1])
                                        for x in (unpaid, none, part, bad))), (paid, unpaid, none, part, bad)


def PR_ISO(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def t_the_certificate_row_carries_the_proof_time():
    """The row cert_red_decide reads is the one judge_certificate.certify writes: a decider whose red proof is of another
    version of its file carries proof_at; one never proved carries None."""
    root = os.path.join(TMP, "repo")
    d = os.path.join(root, "design", "concepts", MOD, "version")
    os.makedirs(os.path.join(d, "evidence"), exist_ok=True)
    for n in ("t_a.py", "t_b.py"):
        with open(os.path.join(root, n), "w") as fh:
            fh.write("print('x')\n")
    run = {"ran": True, "rc": 0, "result": "PASS", "last": "PASS", "build": "x", "command": "c"}
    table = {"tests": {"T_A": {"id": "T_A", "kind": "offline", "file": "t_a.py", "command": "c", "reads": [],
                               "runs_today": run},
                       "T_B": {"id": "T_B", "kind": "offline", "file": "t_b.py", "command": "c", "reads": [],
                               "runs_today": run}},
             "bars": [{"id": "b1", "proves_at": "4-5", "offline_decides": ["T_A", "T_B"], "decides": ["T_A", "T_B"]}]}
    with open(os.path.join(d, "test_table.json"), "w") as fh:
        json.dump(table, fh)
    with open(os.path.join(d, "evidence", "red_seen.json"), "w") as fh:
        json.dump({"T_A": {"rc": 1, "at": "2026-11-23T15:03:10Z", "test_blob": "old", "command": "c"}}, fh)
    with open(os.path.join(d, "evidence", "red_seen_grandfather.json"), "w") as fh:
        json.dump({}, fh)
    rows = {r["test"]: r for r in JC.certify(root, MOD)["rows"] if r["clause"] == "red_seen"}
    return (rows["T_A"]["status"] == "REFUSED" and rows["T_A"].get("proof_at") == "2026-11-23T15:03:10Z"
            and rows["T_B"]["status"] == "REFUSED" and rows["T_B"].get("proof_at") is None), rows


def t_the_stop_says_what_is_owed():
    """The stop of a red_seen set never says the deciders are red: the four of 2026-11-23 were green, and the Conductor
    filed an item to repair four red deciders."""
    s = {"cert_red_seen": {"tests": ["T_CORE", "T_STUB_JOINS"], "unit": "u1", "at": NOW - 3600, "failed": None}}
    _, _, put = decide({"certificate": RS}, s)
    why = " ".join(str(x) for p in put if p[0] == "stopped" for x in p)
    _, _, rput = decide({"certificate": cert(("T_A", "b", "green"))},
                        {"cert_red": {"tests": ["T_A"], "unit": "u1", "at": NOW - 3600, "failed": None}})
    rwhy = " ".join(str(x) for p in rput if p[0] == "stopped" for x in p)
    return ("still red" not in why and "red proof" in why and "still red" in rwhy), (why, rwhy)


def t_clear_lifts_the_red_seen_stop():
    """The stop's own line names `maturation_dispatch.py clear <Mod>`; clear popped cert_red alone, so a red_seen stop
    came back on the next tick."""
    d = MD.sdir()
    os.makedirs(d, exist_ok=True)
    book = {"tests": ["T_CORE", "T_STUB_JOINS"], "unit": "u1", "at": NOW - 3600, "failed": None}
    p = os.path.join(d, "state.json")
    with open(p, "w") as fh:
        json.dump({"mods": {MOD: {"cert_red_seen": book, "cert_red": dict(book)}}}, fh)
    rc = MD._clear(types.SimpleNamespace(mod=MOD, why="test"))
    with open(p) as fh:
        s = json.load(fh)["mods"][MOD]
    return rc == 0 and "cert_red_seen" not in s and "cert_red" not in s, (rc, s)


def t_a_voided_run_gives_its_try_back():
    """A run that died of a system cause or was voided spends no try: the red_seen book goes out with its launch, as
    cert_red does."""
    import run_void as RV
    return ("cert_red_seen" in RV.ONE_BOOKS and "cert_red_seen" in RV.FOLLOW_LAUNCH), (RV.ONE_BOOKS, RV.FOLLOW_LAUNCH)


REC_U = {"unit": "rm-detached-bench-mend-slack-1", "session": "11111111-2222-3333-4444-555555555555",
         "at": NOW - 3000, "ended": NOW - 1500}
REC_V = {"unit": "rm-detached-bench-other-run-2", "session": "66666666-7777-8888-9999-000000000000",
         "at": NOW - 2900, "ended": NOW - 1400}


def launch(records, commit_t, now=NOW):
    seen = []

    def brief(item, text, model, cap, seat, env=None, session=None):
        seen.append({"item": item, "text": text, "session": session})
        return 0, "DETACHED u", "u-red-seen"
    row = {"mod": MOD, "cert_reds": ["T_CORE"], "cert_kind": "red_seen", "cap": 10.0,
           "cert_gate": {"stage": "offline_build"},
           "certificate": {"rows": [{"test": "T_CORE", "bar": "b1", "clause": "red_seen", "status": "REFUSED"}]}}
    st = {"mods": {MOD: {}}}
    fx = {"launch_brief": brief, "pilot": lambda root, mod: False, "ended": lambda ids: set(),
          "records": lambda: list(records),
          "commit_time": lambda root, path: PR.value(commit_t) if commit_t else PR.could_not_look("planted: git"),
          "decider_files": lambda root, mod, tests: {"T_CORE": "src/WMod/selftest_wmod.py"}}
    ok = MD.cert_launch(TMP, CFG, st, row, now, fx, set(), lambda *a, **k: (True, "filed"))
    return ok, seen, st["mods"][MOD]


def t_warm_editor_is_resumed():
    warm = launch([REC_U], NOW - 2000)
    cold = launch([REC_U], NOW - 2000, now=NOW + 7200)
    two = launch([REC_U, REC_V], NOW - 2000)
    nogit = launch([REC_U], None)
    return (warm[0] and warm[1][0]["session"] == REC_U["session"]
            and all(x[0] and x[1][0]["session"] is None for x in (cold, two, nogit))
            and warm[2]["cert_red_seen"]["resumed"] == REC_U["unit"]), [
        (x[1][0]["session"] if x[1] else None, x[2].get("cert_red_seen", {}).get("resume_why")) for x in (warm, cold, two, nogit)]


def t_brief_names_the_proof():
    ok, seen, s = launch([], None)
    text = seen[0]["text"] if seen else ""
    return (ok and "maturation.py red-seen %s T_CORE --patch" % MOD in " ".join(text.split())
            and seen[0]["item"].endswith("_RED_SEEN_OWED") and "cert_red" not in s), (seen[:1], sorted(s))


def main():
    tests = [t_red_seen_only_launches, t_mixed_refusal_keeps_its_route, t_one_try_per_set, t_warm_editor_is_resumed,
             t_brief_names_the_proof, t_a_new_set_gets_its_own_try, t_a_proof_recorded_since_the_try_is_a_new_debt,
             t_the_certificate_row_carries_the_proof_time, t_the_stop_says_what_is_owed,
             t_clear_lifts_the_red_seen_stop, t_a_voided_run_gives_its_try_back]
    fails = []
    for fn in tests:
        try:
            good, got = fn()
        except Exception as e:  # noqa: BLE001 - a test that raises is a failure by name, never a pass
            good, got = False, "%s: %s" % (type(e).__name__, e)
        print("%s  %s%s" % ("PASS" if good else "FAIL", fn.__name__[2:].replace("_", "-"),
                            "" if good else "  got: %r" % (got,)))
        if not good:
            fails.append(fn.__name__)
    if fails:
        print("FAIL selftest_red_seen_owner: %d of %d red" % (len(fails), len(tests)))
        return 1
    print("PASS selftest_red_seen_owner: %d tests" % len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
