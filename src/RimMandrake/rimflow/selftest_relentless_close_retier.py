#!/usr/bin/env python3
"""CLOSE_RETIER_FIX_LEDGER_STILL_OWES_L1: a non-game item whose candidate re-tiers a criterion in
live_proofs/<ID>.criteria (A2 L1 -> L0) closes. Before the fix the closing step called `close` on the stale ledger
manifest, which refused for ever ('still owes A2 L1'; GENERATOR_MODS_PROVE_INERT_AFTER_CREATION at 856e59a2).

  R  a re-tiered criterion is recorded again from the candidate's file, then the close lands
  K  a ledger criterion the file does not name is carried into the new manifest, never dropped
  U  a file that agrees with the ledger (or names nothing) re-records nothing
  P  criteria_moved, pure: level change, wording change, the 160-char cut, one-sided lines
  M  mutant: close_rerecord made a no-op must turn R red (the instance: close_refused)

Rows run the real tick on selftest_relentless's rig."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model                            # noqa: E402
import relentless_game as G             # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


REFUSAL = ("close: GENERATOR has not earned its close: it still owes A2 L1 (the ledger manifest; "
           "verify it or record the manifest again)")


def rig(ledger, criteria_file):
    """T.Rig with a ledger manifest `ledger` ({cid: level}) and the candidate's .criteria text; close refuses while any
    criterion above L0 is owed, as `rimflow close` does."""
    x = T.Rig(n=1, share=1.0)
    w = x.w
    w.manifest = {cid: {"id": cid, "level": lv, "text": "clause %s" % cid} for cid, lv in ledger.items()}
    w.impl = []

    def game_ledger(item):
        return {"state": w.items[item], "built_sha": "sha1", "title": "", "owed": {},
                "criteria": {k: dict(v) for k, v in w.manifest.items()}, "passed": {}}

    def proofs_at(item, sha, ext=".txt"):
        return criteria_file if ext == ".criteria" else ""

    def game_implement(item, sha, text, live=None, why=None, no_code=None):
        w.impl.append((item, sha, text))
        crit, _ = model.parse_criteria(text)
        w.manifest = {c["id"]: dict(c) for c in crit}
        return None

    real_close = w.ledger_close

    def ledger_close(item, sha, reason, live=None):
        owed = sorted(c for c, v in w.manifest.items() if v["level"] != "L0")
        if owed:
            return REFUSAL.replace("A2 L1", ", ".join("%s %s" % (c, w.manifest[c]["level"]) for c in owed))
        return real_close(item, sha, reason, live)

    w.game_ledger, w.proofs_at, w.game_implement, w.ledger_close = game_ledger, proofs_at, game_implement, ledger_close
    return x


def drive(x):
    T.full_pass(x, "I0")
    for _ in range(4):
        x.tick()
    return x.st("I0")


def fam_retier():
    x = rig({"A1": "L0", "A2": "L1"}, "A1 L0: clause A1\nA2 L0: clause A2\n")
    st = drive(x)
    ok(x.w.closes == [("I0", "sha1")] and x.w.items["I0"] == "done",
       "R the re-tiered item closes (closes %s, status %s)" % (x.w.closes, st["status"]))
    ok(len(x.w.impl) == 1 and x.w.impl[0][1] == "sha1",
       "R the manifest is recorded once, at the candidate (%d)" % len(x.w.impl))
    ok(x.w.manifest["A2"]["level"] == "L0", "R the ledger now holds A2 at L0")
    x.done()


def fam_keep():
    x = rig({"A1": "L0", "A2": "L1", "B1": "L0"}, "A2 L0: clause A2\n")
    drive(x)
    ok(sorted(x.w.manifest) == ["A1", "A2", "B1"] and x.w.manifest["B1"]["text"] == "clause B1",
       "K ledger criteria the file does not name are carried over (%s)" % sorted(x.w.manifest))
    ok(x.w.closes == [("I0", "sha1")], "K and the item closes")
    x.done()


def fam_unchanged():
    for name, crit in (("agrees", "A1 L0: clause A1\nA2 L0: clause A2\n"), ("empty", "")):
        x = rig({"A1": "L0", "A2": "L0"}, crit)
        drive(x)
        ok(x.w.impl == [] and x.w.closes == [("I0", "sha1")],
           "U a file that %s re-records nothing and the close lands (impl %d)" % (name, len(x.w.impl)))
        x.done()
    # a stale manifest the file does NOT re-tier still refuses: the fix moves no obligation by itself
    x = rig({"A2": "L1"}, "A1 L0: clause A1\n")
    st = drive(x)
    ok(x.w.impl == [] and x.w.closes == [] and "close_refused" in json.dumps(st),
       "U an owed L1 the file does not re-tier is still refused (%s)" % st["status"])
    x.done()


def fam_pure():
    led = {"A1": {"level": "L1", "text": "seen"}, "A2": {"level": "L0", "text": "old words"},
           "A3": {"level": "L0", "text": "x" * model.CRITERION_TEXT_MAX}, "Z9": {"level": "L2", "text": "ledger only"}}
    text = "A1 L0: seen\nA2 L0: new words\n- A3 L0: %s and more past the cut\nB7 L1: file only\n" % ("x" * model.CRITERION_TEXT_MAX)
    ok(G.criteria_moved(text, led) == ["A1", "A2"], "P level and wording moves, cut text and one-sided lines do not (%s)"
       % G.criteria_moved(text, led))
    ok(G.criteria_moved("", led) == [] and G.criteria_moved(text, {}) == [], "P nothing to compare moves nothing")


def fam_mutant():
    real = G.close_rerecord
    G.close_rerecord = lambda store, fx, item, sha, acts: None
    try:
        x = rig({"A1": "L0", "A2": "L1"}, "A1 L0: clause A1\nA2 L0: clause A2\n")
        st = drive(x)
        red = x.w.closes == [] and "close_refused" in json.dumps(st) and "A2 L1" in json.dumps(st)
        ok(red, "M without the re-record the instance comes back: close refused, still owes A2 L1 (%s)" % st["status"])
        x.done()
    finally:
        G.close_rerecord = real


def main():
    for fam in (fam_retier, fam_keep, fam_unchanged, fam_pure, fam_mutant):
        fam()
    FAILS.extend(getattr(T, "FAILS", []))     # the rig's own rows (full_pass) report into selftest_relentless
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS)))
        return 1
    print("selftest_relentless_close_retier: all rows green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
