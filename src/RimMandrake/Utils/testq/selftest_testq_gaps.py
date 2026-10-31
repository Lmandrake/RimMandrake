#!/usr/bin/env python3
"""selftest_testq_gaps.py - the filler's evidence-gap order (gaps.py, TESTQ_FILL_RANK_BY_EVIDENCE_GAPS;
design/RimMandrake/work_allocation_framework_2026-10-26.md section 6.3).

Offline over hand-made done records; git, the modcheck probe and the ledger are fakes passed in, except one real
gapprobe.py call on FlowWorks (the instrument can see: a known chain, an offline chain, a backticked item link).
Proves: the rank order (fix landed > item owed > unmeasured > never run), that a chain which PASSED at the current
identity or FAILED there with no fix is never filler (nor one with a GAP there: testq/retest.py), the two halves of "fix landed" (a commit names it; files that
map to it changed), DRY and offline chains skipped, identity unknown once the source moved, a run without a deployed
block blocking nothing, flaky chains reported and never repeated, a blind probe reported, and fill_plan's
pick / exhausted / dry verdicts through a temp queue.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gaps as G      # noqa: E402
import schema as S    # noqa: E402

FAILS = []
NOW = S.parse_ts("2026-10-26T12:00:00Z")
MOD = "FlowWorks"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def rec(i, day, rows, ident="A", sha="s0", item=None, by="someone", purpose="guard", outcome="DONE", mod=MOD):
    fin = "2026-10-%02dT10:00:00Z" % day
    res = {"outcome": outcome, "started": fin, "finished": fin, "runner_sha": sha,
           "rows": [dict(chain=c, row=r, verdict=v) for c, r, v in rows]}
    if ident:
        res["deployed"] = {"mods": {mod: {"dll_sha256": ident, "defs_sha256": "d"}}, "modsconfig_sha256_prerun": "m"}
    job = {"id": "J%02d" % i, "mod": mod, "submitted": fin, "requested_by": by, "purpose": purpose}
    if item:
        job["item"] = item
    return {"finished": fin, "job": job, "result": res}


def fake_git(moved=False, logs=None):
    def g(*args):
        if args[0] == "diff":
            return "src/x.cs\n" if moved else ""
        if args[0] == "log":
            sha = args[2].split("..")[0]
            return "".join("%s\x1f%s\x1e" % (h, m) for h, m in (logs or {}).get(sha, []))
        return None
    return g


def fake_probe(chains, offline=(), item_chains=None, changed=None, blind=None):
    def p(mod, items, since):
        if blind:
            return {"blind": blind}
        return {"chains": list(chains), "offline": list(offline), "item_chains": item_chains or {},
                "changed": changed or {}}
    return p


class Item:
    def __init__(self, state, owed, title="", history=()):
        self.state, self._owed, self.title, self.history = state, owed, title, list(history)

    def owed_levels(self):
        return list(self._owed)


class World:
    def __init__(self, items):
        self.items = items


class Model:
    ITEMS = "/nonexistent"


NO_ITEMS = (Model, [], World({}))


def rank(recs, chains, n=2, dry=(), world=NO_ITEMS, g=None, prober=None, **kw):
    return G.rank(MOD, n, NOW, recs, lambda c: c in dry, world=world, g=g or fake_git(),
                  prober=prober or fake_probe(chains), **kw)


def t_identity_and_verdicts():
    a, b = rec(1, 1, [], ident="A")["result"], rec(2, 1, [], ident="B")["result"]
    check(G.identity_of(a) == G.identity_of(rec(3, 2, [], ident="A")["result"]) and G.identity_of(a) != G.identity_of(b),
          "identity: the same deployed dll/defs/ModsConfig is one identity, a new dll another")
    check(G.identity_of(rec(4, 1, [], ident=None)["result"]) is None, "no deployed block: no identity")
    cv = G.chain_verdict
    check(cv([{"row": "a", "verdict": "PASS"}, {"row": "b", "verdict": "FAIL"}]) == ("FAIL", ["b"]), "a FAIL row: FAIL")
    check(cv([{"row": "a", "verdict": "PASS"}, {"row": "b", "verdict": "UNMEASURED"}])[0] == "GAP", "UNMEASURED: GAP")
    check(cv([{"row": "a", "verdict": "NOT_RUN"}])[0] == "GAP", "NOT_RUN only: GAP")
    check(cv([{"row": "a", "verdict": "PASS"}, {"row": "b", "verdict": "SKIP"}])[0] == "PASS", "PASS + SKIP: PASS")
    check(cv([{"row": "<site hold, before any component>", "verdict": "UNMEASURED"}])[0] is None,
          "only the site hold: no verdict on the chain")


def t_pass_and_unfixed_fail_never_filler():
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("beta_b", "b1", "FAIL")])]
    r = rank(recs, ["alpha", "beta_b"])
    check(r["rank"] is None and r["pick"] == [] and r["text"].startswith("exhausted"),
          "PASS at the current identity and a FAIL with no fix since: nothing is filler: %s" % r["text"])
    check("2 chain(s) hold a verdict" in r["text"], "exhausted says why: %s" % r["text"])


def t_fix_landed():
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("beta_b", "b1", "FAIL"), ("gamma", "g1", "FAIL")], sha="s1"),
            rec(2, 21, [("delta", "d1", "PASS")], ident="A")]
    g = fake_git(logs={"s1": [("c0ffee1", "FlowWorks: fix the beta_b pump\n\nbody")]})
    r = rank(recs + [], ["alpha", "beta_b", "gamma", "delta", "eps"], g=g)
    check(r["rank"] == "fix_landed" and r["pick"] == ["beta_b"] and r["purpose"] == "fix",
          "a commit naming the FAILED chain: fix_landed, purpose fix, ahead of a never-run chain: %s" % r["text"])
    check("c0ffee1" in r["text"], "the plan cites the commit: %s" % r["text"])
    g = fake_git(logs={"s1": [("c0ffee2", "repair `g1` row drain")]})
    r = rank(recs, ["alpha", "beta_b", "gamma", "delta"], g=g)
    check(r["pick"] == ["gamma"], "a commit naming a FAIL row (backticked one-word row): fix_landed: %s" % r["pick"])
    r = rank(recs, ["alpha", "beta_b", "gamma", "delta"], g=fake_git(logs={"s1": [("c0ffee3", "unrelated")]}),
             prober=fake_probe(["alpha", "beta_b", "gamma", "delta"], changed={"s1": ["gamma"]}))
    check(r["rank"] == "fix_landed" and r["pick"] == ["gamma"] and "modcheck --changed" in r["why"]["gamma"],
          "files changed since the FAIL that modcheck maps to the chain: fix_landed: %s" % r["text"])
    recs2 = [rec(1, 20, [("beta_b", "b1", "FAIL")], sha="s1", item="X_BETA_ITEM")]
    r = rank(recs2, ["beta_b"], g=fake_git(logs={"s1": [("c0ffee4", "close X_BETA_ITEM: pump fixed")]}))
    check(r["pick"] == ["beta_b"] and r["row_items"] == {"beta_b": "X_BETA_ITEM"},
          "a commit naming the run's item: fix_landed, recorded against that item: %s %s" % (r["pick"], r["row_items"]))


def t_item_owed():
    world = (Model, [{"text": "drive `alpha` live"}],
             World({"X_OWES_L1": Item("built", ["L1", "L3"], "pump", [0]),
                    "X_OPEN": Item("open", ["L1"]), "X_ONLY_L3": Item("built", ["L3"]),
                    "X_VALID_GREEN": Item("validated", ["GREEN-MIN"])}))
    owed = G.owed_items(world)
    check(set(owed) == {"X_OWES_L1", "X_VALID_GREEN"},
          "owed items: built/validated owing a live level only (not open, not L3-only): %s" % sorted(owed))
    check("`alpha`" in owed["X_OWES_L1"], "an item's ledger text includes its notes (history -> events)")
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("beta_b", "b1", "UNMEASURED")])]
    pr = fake_probe(["alpha", "beta_b", "gamma", "delta"], item_chains={"X_OWES_L1": ["gamma", "alpha"]})
    r = rank(recs, None, world=world, prober=pr)
    check(r["rank"] == "item_owed" and r["pick"] == ["gamma"] and r["row_items"] == {"gamma": "X_OWES_L1"}
          and r["purpose"] == "guard",
          "an owed item's chain: item_owed, ahead of UNMEASURED and never-run, recorded against the item; the "
          "linked chain that already PASSED at this identity is not re-run: %s %s" % (r["text"], r["row_items"]))


def t_unmeasured_and_dry():
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("beta_b", "b1", "UNMEASURED"), ("gamma", "g1", "NOT_RUN")])]
    r = rank(recs, ["alpha", "beta_b", "gamma", "delta"])
    check(r["rank"] == "never_run" and r["pick"] == ["delta"],
          "UNMEASURED / NOT_RUN at the current identity is a verdict: only never-run delta: %s" % r["text"])
    r = rank(recs, ["alpha", "beta_b", "gamma", "delta"], dry={"beta_b", "gamma"})
    check(r["rank"] == "never_run" and r["pick"] == ["delta"] and r["dry"] == ["beta_b", "gamma"],
          "DRY chains are not re-queued for their gaps: %s" % r["text"])
    r = rank(recs, ["alpha", "beta_b", "gamma"], dry={"beta_b", "gamma"})
    check(r["rank"] is None and "2 DRY" in r["text"] and not r["all_dry"], "PASS + DRY: exhausted: %s" % r["text"])
    r = rank([rec(1, 20, [("beta_b", "b1", "UNMEASURED")])], ["beta_b"], dry={"beta_b"})
    check(r["rank"] is None and r["all_dry"], "every chain DRY: all_dry (the steward's fault, not exhaustion)")


def t_never_run_and_identity():
    recs = [rec(1, 10, [("old_c", "o", "PASS")], ident="OLD"), rec(2, 15, [("mid_c", "m", "PASS")], ident="OLD"),
            rec(3, 20, [("alpha", "a1", "PASS")], ident="A")]
    r = rank(recs, ["alpha", "old_c", "mid_c", "new_c"], n=2)
    check(r["rank"] == "never_run" and r["pick"] == ["new_c", "old_c"],
          "never run at the current identity, stalest first (never-ever first), n caps: %s" % r["pick"])
    check("alpha" not in r["pick"], "the chain that PASSED at the current identity is held")
    r = rank(recs, ["alpha"], n=5, g=fake_git(moved=True))
    check(r["moved"] is True and r["ident"] is None and "alpha" in r["pick"],
          "source moved since the run: identity unknown, a PASS no longer holds the chain: %s" % r["text"])
    r = rank([rec(1, 20, [("alpha", "a1", "PASS")], ident=None)], ["alpha"])
    check(r["rank"] == "never_run" and r["pick"] == ["alpha"], "a run with no deployed block blocks nothing")
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("core_offline", "c", "PASS")], ident=None)]
    r = rank(recs, ["alpha", "core_offline"], prober=fake_probe(["alpha", "core_offline"], offline=["core_offline"]))
    check(r["pick"] == ["alpha"], "an offline chain is never filler: %s" % r["pick"])
    r = rank(recs, ["alpha", "beta_b"], exclude={"beta_b"})
    check("beta_b" not in r["pick"], "an excluded chain (modcheck refused it) is never picked")
    r = rank([rec(1, 20, [("alpha", "a1", "PASS"), ("zz", "z", "PASS")], ident=None, outcome="FAILED")], ["alpha"])
    check(r["pick"] == ["alpha"], "a run that did not come back DONE is not a valid run")


def t_flaky_is_reported_never_repeated():
    recs = [rec(1, 1, [("beta_b", "b1", "PASS")]), rec(2, 2, [("beta_b", "b1", "FAIL")]),
            rec(3, 3, [("alpha", "a1", "PASS")])]
    r = rank(recs, ["alpha", "beta_b"])
    check(r["rank"] is None and r["pick"] == [] and "beta_b" in r["flaky"],
          "a flipped chain is reported and not run again at the same code (owner ruling 2026-10-31): %s" % r["text"])


def t_blind():
    recs = [rec(1, 20, [("alpha", "a1", "PASS"), ("beta_b", "b1", "UNMEASURED")])]
    r = rank(recs, None, prober=fake_probe([], blind="no modcheck in this checkout"))
    check(r["rank"] is None and r["blind"] == ["no modcheck in this checkout"],
          "a blind probe: chains from history, and the plan says it is blind: %s" % r["blind"])
    r = rank([rec(1, 20, [("alpha", "a1", "PASS")])], None, prober=fake_probe([], blind="no modcheck"))
    check(r["rank"] is None and "blind: no modcheck" in r["text"], "exhausted while blind says so: %s" % r["text"])


def t_real_probe():
    """The instrument can see: one real gapprobe.py run against this checkout's FlowWorks validation."""
    out = G.probe(MOD, {"X_T_PROBE": "walk the `drawbridges` chain"}, [])
    if out.get("blind"):
        check(False, "gapprobe on FlowWorks is blind in a full checkout: %s" % out["blind"])
        return
    check(len(out["chains"]) > 10 and "drawbridges" in out["chains"] and "core_offline" in out["offline"],
          "gapprobe lists FlowWorks' chains (%d) and its offline ones" % len(out["chains"]))
    check("drawbridges" in out["item_chains"].get("X_T_PROBE", []), "an item text naming `drawbridges` links to it")


def t_fill_plan():
    import testq as T
    tmp = tempfile.mkdtemp(prefix="rf_testq_gaps_")
    saved = (T.QHOME, G.probe, G.owed_items, G.git)
    try:
        T.QHOME = tmp
        T.ensure_dirs()
        fin = "2026-10-25T10:00:00Z"

        def put(r):
            with open(os.path.join(tmp, "done", r["job"]["id"] + ".json"), "w") as fh:
                json.dump(r, fh)
        put(rec(1, 25, [("alpha", "a1", "PASS")]))
        G.probe = fake_probe(["alpha", "beta_b"])
        G.owed_items = lambda world=None: {}
        G.git = fake_git()
        now = S.parse_ts(fin) + 3600
        p = T.fill_plan(MOD, 2, T.FILL_CAP_DEFAULT, T.FILL_DAY_S, now)
        check(p["verdict"] == "pick" and p["pick"] == ["beta_b"] and p["rank"] == "never_run"
              and p["purpose"] == "guard", "fill_plan: the gap order, not the stalest chain: %s" % p["text"])
        put(rec(2, 25, [("beta_b", "b1", "PASS")]))
        p = T.fill_plan(MOD, 2, T.FILL_CAP_DEFAULT, T.FILL_DAY_S, now)
        check(p["verdict"] == "exhausted" and p["pick"] == [], "fill_plan: all PASSED at the identity: exhausted: %s"
              % p["text"])
        put(rec(3, 25, [("beta_b", "b1", "FAIL")]))
        put(rec(4, 25, [("beta_b", "b1", "PASS")], by=T.FILLER, purpose="flake"))
        p = T.fill_plan(MOD, 2, T.FILL_CAP_DEFAULT, T.FILL_DAY_S, now)
        check(p["verdict"] == "exhausted" and p["flaky"] == ["beta_b"], "fill_plan: a flipped chain is only reported: %s"
              % p["text"])
    finally:
        T.QHOME, G.probe, G.owed_items, G.git = saved
        shutil.rmtree(tmp, ignore_errors=True)


def t_pilot_routed_skipped():
    """The Test Pilot rule (owner 2026-10-31): no filler, sweep or submit for a chain tied to a routed item."""
    rf = os.path.abspath(os.path.join(HERE, "..", "..", "rimflow"))
    sys.path.insert(0, os.path.dirname(rf))
    from rimflow import testpilot_route as TP
    import testq as T
    world = (Model, [], World({"X_OWES_L1": Item("built", ["L1"], "pump", [0])}))
    pr = fake_probe(["alpha", "gamma"], item_chains={"X_OWES_L1": ["gamma"]})
    recs = [rec(1, 20, [("alpha", "a1", "PASS")])]
    real = TP.routed
    try:
        TP.routed = lambda w, evs: []
        r = rank(recs, None, world=world, prober=pr)
        check(r["pick"] == ["gamma"], "unrouted item: its chain is picked: %s" % r["pick"])
        TP.routed = lambda w, evs: [{"id": "X_OWES_L1", "kind": "streak", "why": "3 non-pass runs in a row"}]
        r = rank(recs, None, world=world, prober=pr)
        check("gamma" not in r["pick"] and "gamma" in r["held"], "routed item: filler skips its chain: %s %s"
              % (r["pick"], r["held"]))
        s0 = G.settled(MOD, recs, world, fake_git(), pr)
        check(s0["pilot"] == {"gamma": "X_OWES_L1"}, "settled names the pilot chain: %s" % s0["pilot"])
        recs2 = [rec(2, 21, [("gamma", "g1", "FAIL")], item="X_OWES_L1")]
        pr2 = fake_probe(["gamma"])
        check(G.settled(MOD, recs2, world, fake_git(), pr2)["pilot"] == {"gamma": "X_OWES_L1"},
              "a chain whose latest run was for the routed item is taken too")
        check(G.routed_ids(world) == {"X_OWES_L1"}, "routed_ids reads the rule")
        T.pilot_stop = lambda mod: {"gamma": "X_OWES_L1"}
        pv = {"chains": ["gamma"]}
        a = argparse.Namespace(mod=MOD, by="someone", sha=None, retest_why=None)
        why = T.already_tested(a, {"chains": ["gamma"]}, pv)
        check(why and "Test Pilot" in why, "submit refuses a routed chain: %s" % why)
        check(T.already_tested(a, {"rows": ["g1"]}, pv), "a --rows job on a routed chain is refused too")
        a.by = T.FILLER
        check(T.already_tested(a, {"chains": ["gamma"]}, pv), "even the filler is refused a routed chain")
        a.retest_why = "owner asked"
        check(T.already_tested(a, {"chains": ["gamma"]}, pv) is None, "--retest-why overrides")
    finally:
        TP.routed = real


def main():
    for t in (t_pilot_routed_skipped, t_identity_and_verdicts, t_pass_and_unfixed_fail_never_filler, t_fix_landed, t_item_owed,
              t_unmeasured_and_dry, t_never_run_and_identity, t_flaky_is_reported_never_repeated, t_blind, t_real_probe, t_fill_plan):
        try:
            t()
        except Exception as e:      # noqa: BLE001 - one broken case must not hide the rest
            import traceback
            traceback.print_exc()
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
