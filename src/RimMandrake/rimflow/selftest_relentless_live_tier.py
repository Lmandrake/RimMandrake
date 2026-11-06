#!/usr/bin/env python3
"""selftest_relentless_live_tier.py -- a `live-tier:` proof line is loaded as the WHOLE list (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD).

VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL A1 measures on the ratchet_pilot tier; the staging could only ENABLE mods onto the
live list, so its load ran 39 mods and A1 read WRONG_TIER on every run. What must hold, on selftest_relentless_game's
fake world (no game, no ModsConfig):
  live_tier parses one tier, refuses two or a line of several words;
  a tier item's staging resolves the tier first (modset_builder --tier, a plan), enables nothing, carries no rider, and
  its staging prompt names the one modset_builder --tier ... --apply --by relentless command as the whole list;
  a tier that does not resolve holds the item before the bridge is taken; a malformed line holds it too;
  a tier item never "tries the running game": another item's load is not its tier;
  a plain item's staging never carries a tier item as a rider (and a full-list staging still does);
  restoring after: Relentless's own swap is undone before every staging writes a list (before any enable), and again
  when a tier item passes; a refused restore puts the staging down before the bridge.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                 # noqa: E402
import relentless_game as G            # noqa: E402
import relentless_live_round as LR     # noqa: E402
import selftest_relentless_game as T   # noqa: E402

FAILS = T.FAILS
ok = T.ok
TIER_PROOF = "live-tier: ratchet_pilot\n" + T.PROOF


def staged_launch(x):
    got = [l for l in x.w.launches if "STAGING" in l[2]]
    return got[-1][2] if got else ""


def both_stage(x, tier_item="I0"):
    T.two_in_prove(x)
    x.w.proofs[(tier_item, ".txt")] = TIER_PROOF
    for i in ("I0", "I1"):
        with x.s.lock():
            st = x.s.load(i)
            st["game"].update(phase="stage")
            x.s.save(st)
    x.w.running = False


def t_parse():
    ok(LR.live_tier(TIER_PROOF) == "ratchet_pilot", "one live-tier line names its tier")
    ok(LR.live_tier("`live-tier: gizkastowaway` # the A2 set\n") == "gizkastowaway", "backticks and a comment tail")
    ok(LR.live_tier(T.PROOF) is None, "no line, no tier")
    for bad in ("live-tier: a b\n", "live-tier: a\nlive-tier: b\n", "live-tier:\n"):
        try:
            LR.live_tier(bad)
            ok(False, "refused: %r" % bad)
        except ValueError:
            ok(True, "refused: %r" % bad)
    ok(LR.live_tier("live-tier: a\nlive-tier: a\n") == "a", "the same tier twice is one tier")


def t_tier_stages_whole_list_alone():
    x = T.rig(2, share=1.0, max_workers=2)
    both_stage(x)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging", "the tier item stages: %s %s" % (st["game"].get("phase"), acts))
    ev = x.w.events
    ok("tier_plan:ratchet_pilot" in ev and "take" in ev and ev.index("tier_plan:ratchet_pilot") < ev.index("take"),
       "the tier is resolved before the bridge is taken: %s" % x.w.events)
    ok(not x.w.enabled, "nothing is enabled on top of the tier: %s" % x.w.enabled)
    ok(st["game"].get("batch") == [] and st["game"].get("tier") == "ratchet_pilot",
       "it carries no rider, and remembers its tier: %s" % st["game"])
    p = staged_launch(x)
    ok(G.tier_cmd("I0", "ratchet_pilot") in p and "modset_builder.py --tier ratchet_pilot --apply --by relentless" in p,
       "the staging prompt names the one tier command")
    ok("EXACT TIER" in p and "WHOLE mod list" in p and "MOD LIST: the next load must hold" not in p
       and "the `ratchet_pilot` tier above IS the list" in p, "as the whole list, with no enable line")
    ok("smallest mod list" not in p, "and not the smallest-list instruction")
    x.done()


def t_plain_item_never_rides_a_tier_item():
    x = T.rig(2, share=1.0, max_workers=2)
    both_stage(x)
    acts = []
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)
    st = x.st("I1")
    ok(st["game"]["phase"] == "staging" and "I0" not in (st["game"].get("batch") or []),
       "a plain staging leaves the tier item to its own load: %s" % st["game"].get("batch"))
    ev = x.w.events
    ok("restore_own" in ev and "enable" in ev and ev.index("restore_own") < ev.index("enable"),
       "restoring after: Relentless's own swap is undone before the enable: %s" % x.w.events)
    ok("EXACT TIER" not in staged_launch(x) and "tier_plan:ratchet_pilot" not in x.w.events,
       "and the plain staging loads no tier")
    x.done()


def t_tier_plan_refused_holds():
    x = T.rig(2, share=1.0, max_workers=2)
    both_stage(x)
    x.w.tier_why = {"ratchet_pilot": "NOT INSTALLED (tier is incomplete): ['mandrake.rm.flowworks']"}
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(st["status"] == "held" and "ratchet_pilot" in st["hold"]["why"] and "take" not in x.w.events,
       "an unresolvable tier holds the item before the bridge: %s" % st.get("hold"))
    x.done()


def t_malformed_tier_holds():
    x = T.rig(2, share=1.0, max_workers=2)
    both_stage(x)
    x.w.proofs[("I0", ".txt")] = "live-tier: ratchet_pilot pyrelands\n" + T.PROOF
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(st["status"] == "held" and "live-tier" in st["hold"]["why"] and "take" not in x.w.events,
       "a two-word live-tier holds: %s" % st.get("hold"))
    x.done()


def t_restore_refused_waits():
    x = T.rig(2, share=1.0, max_workers=2)
    both_stage(x)
    x.w.restore_why = "REFUSING --restore-own: tier 'ratchet_pilot' is live but its before-copy is missing"
    acts = []
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)
    st = x.st("I1")
    ok(st["game"]["phase"] == "stage" and "take" not in x.w.events and not x.w.enabled
       and "restore-own" in (st.get("put_down") or {}).get("on", ""),
       "a refused restore stages nothing and enables nothing: %s %s" % (st.get("put_down"), x.w.events))
    x.done()


def t_tier_never_tries_the_running_game():
    x = T.rig(2, share=1.0, max_workers=2)
    T.two_in_prove(x)
    x.w.proofs[("I1", ".txt")] = TIER_PROOF
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="stage")
        x.s.save(st)
    acts = []
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)       # the game is UP since x.w.started and I1 has no row from it
    ok(not any(a["do"] == "game_try_running" for a in acts) and x.st("I1")["game"]["phase"] == "staging",
       "a tier item stages its own load instead of trying another's: %s" % acts)
    x.done()


def t_passed_restores():
    x = T.rig(1)
    T.to_game(x, "I0")
    x.w.proofs[("I0", ".txt")] = TIER_PROOF
    with x.s.lock():
        st = x.s.load("I0")
        st["game"].update(phase="prove", tier="ratchet_pilot")
        x.s.save(st)
    x.w.led["I0"] = {"state": "done", "built_sha": T.SHA, "title": x.w.title, "owed": {}}
    n = x.w.events.count("restore_own")
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    ok(x.w.events.count("restore_own") == n + 1 and any(a["do"] == "game_tier_restored" for a in acts),
       "a tier item that passes restores Relentless's swap: %s" % acts)
    x.done()


def main(args):
    picked, ran = set(a for a in args if not a.startswith("--")), 0
    for t in (t_parse, t_tier_stages_whole_list_alone, t_plain_item_never_rides_a_tier_item, t_tier_plan_refused_holds,
              t_malformed_tier_holds, t_restore_refused_waits, t_tier_never_tries_the_running_game, t_passed_restores):
        if picked and t.__name__ not in picked:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if picked and ran != len(picked):
        print("selftest_relentless_live_tier: FAIL ran %d of the %d named" % (ran, len(picked)))
        return 1
    print("selftest_relentless_live_tier: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
