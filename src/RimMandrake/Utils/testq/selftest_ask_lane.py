#!/usr/bin/env python3
"""selftest_ask_lane.py - the promises of design/specs/2026-11-24-ask-lane-after-host-facts/boundary.md, one check each."""
import os
import sys
import json
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["TESTQ_QUEUE"] = tempfile.mkdtemp(prefix="ask_lane_")     # before any import of testq: never the live queue
sys.path.insert(0, HERE)
import host_facts as HF  # noqa: E402
import ask as ASK  # noqa: E402

F = {"mods": ["a.b"], "saves": ["NS_x"], "python": {"numpy": True, "lxml": False}, "companions": ["h1"], "free_gb": 9, "logins": {"lukas": 100, "steven": 9 * 86400}}
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def pl(**kw):
    b = dict(item="I", facts=F, stale=False, live_proofs={"A1": "x"}, table={}, tiers={"mods__base": ["a.b"]})
    b.update(kw)
    return ASK.plan(**b)


def t_old_facts_are_stale():
    p = os.path.join(tempfile.mkdtemp(), "f.json")
    json.dump({"at": 0, "facts": F}, open(p, "w"))
    check(not HF.read(p, 10)["stale"] and HF.read(p, HF.MAX_AGE_S + 1) == {"age_s": HF.MAX_AGE_S + 1, "stale": True, "facts": None} and HF.read(p, 10)["facts"] == F and HF.read(p + "x", 1)["facts"] is None, "old facts are stale")


def t_absent_is_measured():
    check(HF.lacks({"mods": ["c"], "python": ["lxml", "numpy"]}, F, False) == [("mods", "c", "absent"), ("python", "lxml", "absent")], "absent is measured")


def t_stale_never_says_absent():
    check({w for _, _, w in HF.lacks({"mods": ["c"]}, F, True)} == {"could not look"}, "stale never says absent")


def t_no_driver_is_cannot():
    check(pl(live_proofs={})["verdict"] == "CANNOT" and pl(table={"P": {"live_check_owed": True}})["verdict"] == "CANNOT", "no driver is CANNOT")


def t_a_missing_tier_mod_is_cannot():
    p = pl(tiers={"t": ["zz.q"]})
    check(p["verdict"] == "CANNOT" and "zz.q" in str(p["why"]), "a missing tier mod is CANNOT")


def t_stale_facts_are_could_not_look():
    check(pl(stale=True)["verdict"] == "COULD NOT LOOK" and pl(facts=None)["verdict"] == "COULD NOT LOOK", "stale facts are COULD NOT LOOK")


def t_an_ask_is_the_whole_line():
    a = pl()["argv"]
    check(pl()["verdict"] == "ASK" and a[:2] == ["submit", "I"] and "--sha" in a and "A1" in a and "--purpose" not in a, "an ask is the whole line")


def t_a_login_low_on_time_is_named():
    check(HF.logins_low(F) == ["lukas"], "a login low on time is named")


GAME = {"mods": ["a.b"], "saves": ["S1"]}


def reading(**kw):
    d = {"games": {"Steve1": GAME, "Steve2": {"mods": ["a.b", "c.d"], "saves": []}}, "unread": [], "python": {"numpy": True}, "free_gb": 5}
    d.update(kw)
    return HF.collect(lambda code: "noise\n" + json.dumps(d) + "\n")


def t_an_unread_part_is_never_absent():
    whole, half, torn = reading(), reading(games={"Steve1": GAME, "Steve2": None}), reading(unread=["/x/About/About.xml (ParseError)"])
    none = reading(games={"Steve1": None, "Steve2": None})
    need = {"mods": ["z.z"]}
    words = [HF.lacks(need, f, False)[0][2] for f in (whole, half, torn, none)]
    check(words == ["absent", "could not look", "could not look", "could not look"] and whole["mods"] == ["a.b", "c.d"]
          and HF.lacks({"python": ["numpy"]}, reading(python=None), False)[0][2] == "could not look",
          "an unread part is never absent %s" % words)


def t_a_refresh_that_fails_writes_nothing():
    p = os.path.join(tempfile.mkdtemp(), "f.json")

    def down(code):
        raise OSError("ssh exit 255")
    try:
        HF.refresh(p, run=down)
        raised = False
    except OSError:
        raised = True
    ok = raised and not os.path.exists(p)
    f = HF.refresh(p, run=lambda c: json.dumps({"games": {"Steve1": GAME}, "unread": [], "python": {}, "free_gb": 1}), now=5,
                   companions=lambda: 1 / 0, logins=lambda: {"x": None, "y": 5})
    check(ok and f["companions"] is None and "companions" in str(f["unread"]) and HF.logins_low(f) == ["y"] and not HF.read(p, 6)["stale"],
          "a refresh that fails writes nothing")


def t_each_clause_goes_to_its_own_list():
    pid = {"FlowWorks": "mandrake.rm.flowworks"}.get
    t = "live-mods: FlowWorks  # why\nlive-tier A2: bridge\nlive-proof A1: x\nlive-proof A2: y\nlive-proof A3: z\n"
    got = [ASK.tiers_of(t, pid), ASK.tiers_of("live-tier: flowworks\nlive-proof A1: x\n", pid), ASK.tiers_of("live-proof A1: x\n", pid),
           ASK.tiers_of("nothing\n", pid)]
    bad = [ASK.tiers_of("live-mods: Nope\nlive-proof A1: x\n", pid)[1], ASK.tiers_of("live-menu: q\nlive-proof A1: x\n", pid)[1],
           ASK.tiers_of("live-tier: a b\nlive-proof A1: x\n", pid)[1]]
    check(got[0] == ({"mods__mandrake_rm_flowworks": ["A1", "A3"], "bridge": ["A2"]}, None) and got[1][0] == {"flowworks": ["A1"]}
          and got[2][0] == {"mods__base": ["A1"]} and got[3] == ({}, None) and all(bad), "each clause goes to its own list %s %s" % (got, bad))


def t_a_held_companion_is_queued_not_dropped():
    import contextlib
    import io
    import testq as T
    sent, home = [], os.environ["TESTQ_QUEUE"]
    json.dump({"at": __import__("time").time(), "facts": dict(F, mods=["brrainz.rimbridgeserver", "brrainz.harmony", "owlchemist.cherrypicker"])},
              open(os.path.join(home, "host_facts.json"), "w"))
    real, T.cmd_submit = T.cmd_submit, lambda a: sent.append(a) or 0
    try:
        said = io.StringIO()
        with contextlib.redirect_stdout(said):      # the facts hold companion h1 and HEAD wants another: cmd_ask must ask for HEAD's
            rc = T.main(["ask", "RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE", "--purpose", "fix", "--sha", "HEAD"])
        dry = T.main(["ask", "RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE", "--purpose", "fix", "--sha", "HEAD", "--dry"])
        no = T.main(["ask", "NO_SUCH_ITEM_HAS_A_PROOF", "--purpose", "fix", "--sha", "HEAD"])
        os.remove(os.path.join(home, "host_facts.json"))
        blind = T.main(["ask", "RIMMANDRAKE_FIX_BRIDGE_STEPPED_PAWNS_DRAWN_ON_OLD_SQUARE", "--purpose", "fix", "--sha", "HEAD"])
    finally:
        T.cmd_submit = real
    check((rc, dry, no, blind) == (0, 0, 3, 4) and len(sent) == 1 and sent[0].profile == "tier:flowworks" and "FlowWorks" in sent[0].deploy,
          "a held companion is queued, not dropped; exits %s, sent %d" % ((rc, dry, no, blind), len(sent)))
    check(said.getvalue().startswith("HOLD ") and "is not staged yet" in said.getvalue(),
          "a held companion is queued, not dropped: cmd_ask asked for the companion (%s)" % said.getvalue()[:90].strip())


def t_a_check_the_host_cannot_run_is_not_sent():
    import visit_feed as VF
    import testq as T
    w = {"FlowWorks": {"opened": 0, "visit": 1, "checks": {"k": ["c"]}}}
    json.dump({"at": 100, "facts": F}, open(os.path.join(os.environ["TESTQ_QUEUE"], "host_facts.json"), "w"))
    got = VF.facts_gate(w, {}, 110, T.REPO)
    check(not w and "absent" in str(got) and "could not look" not in str(got), "a check the host cannot run is not sent (the rest: selftest_steve_visit_feed.py) %s" % got)


def t_facts_written_during_a_pass_are_never_read_as_stale():
    """rm-host-facts.timer writes the file while a testq-tick pass runs; the pass took its time at its start
    (RIMMANDRAKE_READ_FRESH_HOST_FACTS_NEGATIVE_AGE_CRIED_STALE: the steward read -176 s as `-2 min old`)."""
    import testq as T
    now = 1_000_000.0
    p = os.path.join(os.environ["TESTQ_QUEUE"], "host_facts.json")
    got = {}
    for name, at in (("later", now + 120), ("edge", now + HF.MAX_FUTURE_S), ("over", now + HF.MAX_FUTURE_S + 1), ("broken", now + 86400)):
        json.dump({"at": at, "facts": F}, open(p, "w"))
        got[name] = (HF.read(p, now), T.facts_hold("FlowWorks", now), HF.unmet("FlowWorks", kept=HF.read(p, now)))
    check(not got["later"][0]["stale"] and got["later"][0]["facts"] == F and "the host facts are" not in str(got["later"][1:])
          and not got["edge"][0]["stale"], "facts stamped 120 s after the caller's time read fresh: %s" % (got["later"],))
    check(got["over"][0]["stale"] and got["broken"][0]["stale"] and got["broken"][0]["facts"] is None
          and "could not look: the host facts are" in got["broken"][1] and "could not look: the host facts are" in got["over"][2],
          "facts stamped far in the future read could not look: %s" % (got["broken"][1:],))
    os.remove(p)


def main():
    os.environ["TESTQ_QUEUE_SSH"] = ""          # a submit here never leaves this fixture
    for t in (t_an_unread_part_is_never_absent, t_a_refresh_that_fails_writes_nothing, t_each_clause_goes_to_its_own_list,
              t_a_held_companion_is_queued_not_dropped, t_a_check_the_host_cannot_run_is_not_sent,
              t_old_facts_are_stale, t_facts_written_during_a_pass_are_never_read_as_stale, t_absent_is_measured, t_stale_never_says_absent, t_no_driver_is_cannot, t_a_missing_tier_mod_is_cannot,
              t_stale_facts_are_could_not_look, t_an_ask_is_the_whole_line, t_a_login_low_on_time_is_named):
        t()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
