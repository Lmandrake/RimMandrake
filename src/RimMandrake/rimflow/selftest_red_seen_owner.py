#!/usr/bin/env python3
"""selftest_red_seen_owner: the promises of design/specs/2026-11-20-red-seen-owner/boundary.md, one test per promise,
each named as the promise is. A certificate that refuses on red_seen alone used to launch nothing (Gimme Some Slack sat
from 2:14 AM to about 4:50 AM PST on 2026-11-20); now it launches one run that records the proof, resuming the run that
edited the decider when that run is warm (item RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION). No game,
no network, no real launch."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="red_seen_owner_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation_dispatch as MD  # noqa: E402
import probe_result as PR  # noqa: E402

MOD = "WMod"
NOW = 1795170000.0
CFG = {"cap_usd": 10.0, "max_live": 2, "launch_tries": 3, "settle_s": 180, "seat": "BENCH", "model": "opus"}


def cert(*rows):
    return {"ok": False, "rows": [dict(status="REFUSED", bar=b, test=t, clause=c) for t, b, c in rows]}


def decide(f, s=None):
    row, put = {"mod": MOD}, []
    f = dict({"stage": "offline_build", "spend": []}, **f)
    got = MD.cert_red_decide(CFG, s if s is not None else {}, f, row, lambda *a: put.append(a), NOW,
                             (True, "account ok"), 0, CFG["cap_usd"])
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
             t_brief_names_the_proof, t_a_new_set_gets_its_own_try]
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
