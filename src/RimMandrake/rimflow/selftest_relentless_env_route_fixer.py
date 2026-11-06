#!/usr/bin/env python3
"""selftest_relentless_env_route_fixer.py -- ENV_HOLDS_FIX_ROUTE_TO_BUILDERS: a game-lane environment cause no lane step
can fix is routed to a FIXER THAT BUILDS, never to the Conductor's seat queue (where nobody builds:
ART_OVERRIDE_FAMILY_SCRIPT_1 sat held overnight on a harness parse bug).

No game, no bridge, no ledger: selftest_relentless_game's rig. What must hold, each red under its mutant:
  a route files ONE repair item per cause (relentless_game.repair_id: kind + fingerprint), through fx.env_repair, and the
  routed item is `blocked` on it with a dependency wait that resumes the game lane on the same sha, never `held`, never
  delivered to the seat queue, no gen and no worker; a second item stopped by the same cause joins the same repair; the
  sweep writes the ledger block on the repair; the repair still open keeps the item waiting; the repair closed (done)
  puts the item back in its game phase on the SAME sha, with no builder sent; a filing that fails changes nothing (the
  next tick routes again); every repair id passes rimflow's namecheck.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_envcause as E          # noqa: E402
import relentless_game as G              # noqa: E402
import selftest_relentless_envcause as SE  # noqa: E402
import selftest_relentless_game as SG    # noqa: E402

FAILS = SG.FAILS
ok = SG.ok
SHA = SG.SHA


def t_route_files_a_repair_and_blocks():
    x = SE.in_prove()
    gen = x.st("I0")["gen"]
    mine = lambda: sum(1 for l in x.w.launches if l[0] == "I0")     # noqa: E731
    launches = mine()
    x.w.rows = [SE.row(SE.WHYS["harness"], x.now)]
    x.tick()
    st = x.st("I0")
    reps = getattr(x.w, "repairs", [])
    rep = G.repair_id(E.classify(SE.row(SE.WHYS["harness"])))
    ok([r[0] for r in reps] == [rep], "one repair item filed for the cause: %s" % [r[0] for r in reps])
    ok(reps and "I0" in reps[0][2] and "/l/I0-A2.log" in reps[0][2] and SHA[:12] in reps[0][2],
       "the repair's note names the item, its sha and the log: %s" % (reps[0][2] if reps else None))
    w = st.get("wait") or {}
    ok(st["status"] == "blocked" and not st.get("hold") and w.get("on") == rep and w.get("resume") == "game"
       and w.get("sha") == SHA and (st.get("block_pending") or {}).get("on") == [rep],
       "the item waits blocked on the repair, resuming the game lane on its sha: %s %s" % (st["status"], w))
    ok(st["gen"] == gen and not st.get("last_fail") and mine() == launches,
       "no builder on the item, no generation: gen %s->%s launches %d->%d" % (gen, st["gen"], launches, mine()))
    ok(any(l[0] == rep for l in x.w.launches), "a builder takes the repair item itself: %s" % [l[0] for l in x.w.launches])
    x.tick()        # the sweep writes the ledger block; nothing is delivered to the seat queue
    ok(("I0", "item", [rep]) in getattr(x.w, "blocks", []), "the ledger block names the repair: %s"
       % getattr(x.w, "blocks", None))
    ok("I0" not in x.w.seat_holds, "never a seat-queue hold: %s" % x.w.seat_holds)
    st = x.st("I0")
    ok(st["status"] == "blocked" and (st.get("wait") or {}).get("on") == rep,
       "the repair still open keeps it waiting: %s" % st["status"])
    # the repair closes: the item is back in its game lane on the same sha, no builder
    x.w.items[rep] = "done"
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and st["game"]["sha"] == SHA and st["gen"] == gen and not st.get("wait")
       and mine() == launches,
       "the repair closed: back to the game lane on the same sha, no worker: %s %s" % (st["status"], st.get("game")))
    x.done()


def t_same_cause_joins_one_repair():
    x = SE.in_prove()
    acts = []
    G._env(x.s, x.w, x.r, "I0", {"A2": SE.row(SE.WHYS["proof_call"], x.now, defect=True)}, 0, x.now, acts)
    x.done()
    y = SE.in_prove()
    y.w.items.update({r[0]: "doing" for r in x.w.repairs})      # the first route's repair, open on this ledger too
    G._env(y.s, y.w, y.r, "I0", {"A2": dict(SE.row(SE.WHYS["proof_call"], y.now + 99, defect=True),
                                            log="/l/other.log")}, 0, y.now + 99, acts)
    reps = [r[0] for r in x.w.repairs + y.w.repairs]
    ok(len(reps) == 2 and len(set(reps)) == 1,
       "a second item stopped by the same cause (another log, another time) joins the SAME repair: %s" % reps)
    ok((y.st("I0").get("wait") or {}).get("on") == reps[0], "and waits on it")
    y.done()


def t_failed_filing_changes_nothing():
    x = SE.in_prove()
    x.w.env_repair = lambda item, title, text: "rimflow: refused"
    acts = []
    acted = G._env(x.s, x.w, x.r, "I0", {"A2": SE.row(SE.WHYS["harness"], x.now)}, 0, x.now, acts)
    st = x.st("I0")
    ok(acted and st["status"] == "game" and not st.get("env_routed") and not st.get("wait")
       and [a["do"] for a in acts] == ["game_env_route_failed"],
       "a failed filing leaves the item in the game lane to route again: %s %s" % (st["status"], acts))
    x.done()


def t_repair_ids_pass_namecheck():
    import model        # rimflow's own minting rules (cli.py namecheck / file refuse what this refuses)
    for kind in E.KINDS:
        rid = G.repair_id(E.Env(kind=kind, fp="0123456789abcdef"))
        probs = model.mint_problems(rid, set())
        ok(not probs, "%s: %s passes rimflow namecheck: %s" % (kind, rid, probs))


def main():
    for t in (t_route_files_a_repair_and_blocks, t_same_cause_joins_one_repair, t_failed_filing_changes_nothing,
              t_repair_ids_pass_namecheck):
        print("--", t.__name__)
        t()
    print("selftest_relentless_env_route_fixer: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
