#!/usr/bin/env python3
"""selftest_stale_red_rerun_first: the promises of design/specs/2026-11-23-stale-red-rerun-first/boundary.md, one test
per promise, each named as the promise is. A decider recorded red on an older build or command is rerun (zero tokens)
before an offline builder is spent on it (Explosive Knockback's T_SETTINGS_SCREEN, 2026-11-23; item
RIMMANDRAKE_RERUN_STALE_RED_DECIDER_BEFORE_ANY_BUILDER_RUNS). No game, no network, no real launch."""
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="stale_red_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "_dispatcher")
import maturation_dispatch as MD  # noqa: E402

MOD = "KMod"
NOW = 1795430000.0
CFG = {"cap_tokens": 2_500_000, "max_live": 3, "launch_tries": 3, "settle_s": 180, "seat": "BENCH", "model": "opus"}


def row(test, clause, bar="b1", would="a run of %s on this build"):
    return {"status": "REFUSED", "bar": bar, "test": test, "clause": clause,
            "would_pass": would % test if "%s" in would else would}


def cert(*rows):
    return {"ok": False, "rows": list(rows)}


STALE_RED = cert(row("T_SCREEN", "ran_on_this_build"), row("T_SCREEN", "green", would="rc 0 and PASS"),
                 row("T_FUZZ", "red_seen"))


def t_a_stale_red_decider_gets_the_free_rerun_not_a_builder():
    f = {"stage": "blind_challenge", "certificate": STALE_RED}
    reds = MD.red_deciders(f)
    key = MD.stale_key(STALE_RED)
    # the tick's own route at the blind cycle gate: the red route declines, the zero-token rerun launches
    r, put = {"mod": MOD}, []
    got_red = MD.cert_red_decide(CFG, {}, f, r, lambda *a: put.append(a), NOW, (True, "ok"), 0, CFG["cap_tokens"])
    r2, put2 = {"mod": MOD}, []
    got_rerun = MD.cert_rerun_decide(CFG, {}, dict(f, cert_rerun_result=None, cert_rerun_landed=None), r2,
                                     lambda *a: put2.append(a), NOW)
    ok = reds == [] and key is not None and got_red is None and got_rerun == "launch" and r2.get("cert_rerun_key") == key
    return ok, "reds %s key %s red-route %s rerun %s" % (reds, key, got_red, got_rerun)


def t_a_fresh_red_decider_still_gets_the_builder():
    cv = cert(row("T_SCREEN", "green", would="rc 0 and PASS"))
    f = {"stage": "blind_challenge", "certificate": cv}
    reds, key = MD.red_deciders(f), MD.stale_key(cv)
    return reds == ["T_SCREEN"] and key is None, "reds %s key %s" % (reds, key)


def t_a_fresh_red_beside_a_stale_red_sends_the_builder_on_the_fresh_one_only():
    cv = cert(row("T_SCREEN", "ran_on_this_build"), row("T_SCREEN", "green", would="rc 0 and PASS"),
              row("T_KERNEL", "green", bar="b2", would="rc 0 and PASS"))
    reds, key = MD.red_deciders({"certificate": cv}), MD.stale_key(cv)
    return reds == ["T_KERNEL"] and key is None, "reds %s key %s" % (reds, key)


def t_a_key_for_stale_stamps_alone_is_unchanged():
    rows = [row("T_A", "ran_on_this_build"), row("T_B", "ran_on_this_build", bar="b2"), row("T_C", "red_seen")]
    want = sorted({(r["test"], r["would_pass"]) for r in rows if r["clause"] == "ran_on_this_build"})
    old = hashlib.sha1(json.dumps(want).encode("utf-8")).hexdigest()[:12]
    got = MD.stale_key(cert(*rows))
    return got == old, "key %s, the old formula %s" % (got, old)


def main():
    tests = [t_a_stale_red_decider_gets_the_free_rerun_not_a_builder, t_a_fresh_red_decider_still_gets_the_builder,
             t_a_fresh_red_beside_a_stale_red_sends_the_builder_on_the_fresh_one_only,
             t_a_key_for_stale_stamps_alone_is_unchanged]
    bad = 0
    for t in tests:
        try:
            ok, why = t()
        except Exception as e:  # noqa: BLE001  a crash is a FAIL with its cause
            ok, why = False, "%s: %s" % (type(e).__name__, e)
        bad += not ok
        print("%s %s: %s" % ("PASS" if ok else "FAIL", t.__name__[2:].replace("_", "-"), why))
    print("ALL PASS" if not bad else "%d of %d FAIL" % (bad, len(tests)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
