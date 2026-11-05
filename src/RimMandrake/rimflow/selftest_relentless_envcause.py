#!/usr/bin/env python3
"""selftest_relentless_envcause.py -- UNMEASURED_LANE_REWIRE_STOP_REBUILDING_SITES: a live proof that measured nothing for
an ENVIRONMENT reason never goes back to a builder and never starts a generation (relentless_envcause, relentless_game._env).

No game, no bridge, no ledger: selftest_relentless_game's rig. What must hold, each red under its mutant:
  classify names every cause the census found (deploy, load, produce, proof_call, harness, proof_or_site) and none for a
  stale build or a plain transient; a cause the lane can fix is fixed by the lane ONCE (a producer: staged now on voided
  rows, the staging's prompt carries it, the remedy is spent by that staging; a reload cause rides the lane's own
  restage); the same cause after a staging that carried the fix is routed ONCE to one fixer (a game hold), never a worker;
  a route cause a rerun cannot change is routed at once; the same cause after an unhold says so; no branch changes gen.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_envcause as E          # noqa: E402
import relentless_game as G              # noqa: E402
import relentless_live                   # noqa: E402
import selftest_relentless_game as SG    # noqa: E402

FAILS = SG.FAILS
ok = SG.ok
SHA = SG.SHA

# each why is a runs.jsonl row's own words (census 2026-11-05, the 21 held items)
WHYS = {
    "deploy": "not in the running load: CreatureBehaviors has no readable packageId in its deployed About.xml",
    "deploy2": "not deployed: the plan says Stillsand: not enabled in ModsConfig",
    "deploy3": "the deploy plan does not cover Graffiti, UtinniPatches: name it in --deploy",
    "load": "the running load lacks mandrake.rsw.armoury",
    "load2": "reload needed: restart on a list that holds 7f.alienworlds, mandrake.rm.generators; lacks x",
    "load3": "not in the running load: RM_X (mandrake.rut.menushell), RM_Y (arandomkiwi.rimthemes)",
    "load4": "Dubs Bad Hygiene not loaded on this tier",
    "produce": "the proof exited 1: UNMEASURED Armoury: entry hash 56fca373 is not the mod's current 18cbd40f",
    "proof_call": "proof or site defect: the proof's own call is broken, so a rerun or a reload cannot help: Type not found",
    "proof_call2": "the proof crashed: UnicodeDecodeError: 'utf-8' codec can't decode byte 0x90",
    "harness": "harness fault: save.missing_mods",
    "harness2": "the proof exited 2: the proof timed out after 540s",
    "proof_or_site": "proof or site defect: the same cause on the game of G1 and on this one (G2)",
}


def row(why, at=0.0, **kw):
    return dict({"at": relentless_live.iso(at), "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                 "proof": "python.exe p.py", "log": "/l/I0-A2.log", "why": why}, **kw)


def t_classify():
    for k, why in WHYS.items():
        e = E.classify(row(why), "I0")
        ok(e and e.kind == k.rstrip("0123456789"), "%s: %s -> %s" % (k, why[:60], e and e.kind))
    ok(E.classify(row(WHYS["deploy"]))["mods"] == ["CreatureBehaviors"], "a deploy names its mod")
    ok(E.classify(row(WHYS["load2"]))["mods"] == ["7f.alienworlds", "mandrake.rm.generators"], "a reload names its list")
    ok(E.classify(row(WHYS["load3"]))["mods"] == ["arandomkiwi.rimthemes", "mandrake.rut.menushell"],
       "not in the running load names the packageIds")
    p = E.classify(row(WHYS["produce"]), "I0")
    ok(p.cmd and "cli.py run Armoury" in p.cmd and "--item I0" in p.cmd, "a stale verdict names its producer: %s" % p.cmd)
    ok(E.classify(row("changed since the built commit, so the game cannot run sha1: a (b)")) is None,
       "a stale build is no environment cause: its own road stands")
    ok(E.classify(row("bridge not taken: busy")) is None, "a transient is no environment cause")
    ok(E.classify(dict(row(WHYS["harness"]), outcome="PASS")) is None, "a PASS is never a cause")
    ok(E.dud(row("the proof exited 2: it did not measure: x")).kind == "proof_or_site", "a dud with no cause is the proof's")
    a, b = E.classify(row(WHYS["harness"] + " at 12:00")), E.classify(row(WHYS["harness"] + " at 13:07"))
    ok(a.fp == b.fp, "the same cause at another time is the same cause")
    ok(a.fp != E.classify(row(WHYS["proof_call"])).fp, "another cause is another key")


def in_prove():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    ok(x.w.proves == ["I0"], "proving")
    return x


def t_producer_fixed_once_then_routed():
    x = in_prove()
    gen = x.st("I0")["gen"]
    x.w.rows = [row(WHYS["produce"], x.now)]
    x.tick()
    st = x.st("I0")
    g = st["game"]
    ok(st["status"] == "game" and g["phase"] in ("stage", "staging") and st["gen"] == gen and not st.get("last_fail"),
       "a producer cause is the lane's own fix, no worker, no gen: %s %s" % (g["phase"], st.get("last_fail")))
    ok(len(st.get("env_tried") or {}) == 1, "the fix is remembered: %s" % st.get("env_tried"))
    rem = g.get("remedy") or (x.w.prompts[-1] if getattr(x.w, "prompts", None) else None)
    ok(g["phase"] == "staging" or "cli.py run Armoury" in " ".join(rem["cmds"]), "the remedy carries the producer: %s" % rem)
    p = G.stage_prompt(st, x.r, SHA, remedy={"mods": ["Armoury"], "cmds": ["python.exe m.py run Armoury"], "why": "w"})
    ok("LANE FIX" in p and "python.exe m.py run Armoury" in p and "Armoury" in p, "the staging prompt carries the fix")
    ok("LANE FIX: none." in G.stage_prompt(st, x.r, SHA), "and no fix when none is owed")
    # the staging carried it; its re-read says the same: routed once, never a worker
    with x.s.lock():
        s = x.s.load("I0")
        s["game"].update(phase="prove", staged_at=x.now + 10)
        s["game"].pop("remedy", None)
        x.s.save(s)
    acts = []
    acted = G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["produce"], x.now + 20)}, 0, x.now + 30, acts)
    st = x.st("I0")
    ok(acted and st["status"] == "held" and st["hold"]["kind"] == "game" and st["gen"] == gen
       and "the lane fixed it once" in st["hold"]["why"] and not st.get("last_fail"),
       "the same cause after its fix is routed once to one fixer: %s" % st.get("hold"))
    ok([a["do"] for a in acts] == ["game_env_route"], "one route, nothing else: %s" % acts)
    x.done()


def t_reload_rides_the_lanes_restage():
    x = in_prove()
    acts = []
    acted = G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["load2"], x.now)}, 0, x.now, acts)
    st = x.st("I0")
    ok(not acted and st["status"] == "game" and st["game"]["phase"] == "proving",
       "a reload cause rides the lane's own restage and batch wait: %s" % acts)
    ok(st["game"]["remedy"]["mods"] == ["7f.alienworlds", "mandrake.rm.generators"],
       "and its staging enables the list it named: %s" % st["game"].get("remedy"))
    acts = []
    ok(not G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["load2"], x.now + 5)}, 0, x.now + 5, acts) and not acts,
       "read again before any staging carried it: not routed, not tried twice")
    x.done()


def t_route_kinds_routed_at_once():
    for why, extra in ((WHYS["proof_call"], {"defect": True}), (WHYS["harness"], {}), (WHYS["proof_or_site"], {"defect": True})):
        x = in_prove()
        gen = x.st("I0")["gen"]
        x.w.rows = [row(why, x.now, **extra)]
        x.tick()
        st = x.st("I0")
        ok(st["status"] == "held" and st["hold"]["kind"] == "game" and st["gen"] == gen and not st.get("last_fail")
           and "/l/I0-A2.log" in st["hold"]["why"] and len(st.get("env_routed") or {}) == 1,
           "%s: routed at once to one fixer with its log, no worker: %s" % (why[:40], st.get("hold")))
        ok(x.w.proves == ["I0"], "no second prove round on it")
        x.done()
    x = in_prove()
    ok(not G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["harness2"], x.now)}, 0, x.now, []),
       "a timeout a rerun can change is the lane's own retry, not a route")
    x.done()


def t_same_cause_after_unhold():
    x = in_prove()
    acts = []
    G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["proof_call"], x.now, defect=True)}, 0, x.now, acts)
    with x.s.lock():        # the fixer lifts the hold: the prove phase on the same sha
        s = x.s.load("I0")
        s["status"], s["hold"] = "game", None
        x.s.save(s)
    G._env(x.s, x.w, x.r, "I0", {"A2": row(WHYS["proof_call"], x.now + 60, defect=True)}, 0, x.now + 60, acts)
    st = x.st("I0")
    ok(st["status"] == "held" and "the same cause again after its route" in st["hold"]["why"] and not st.get("last_fail"),
       "the same cause after an unhold holds it again and says so, no worker: %s" % st.get("hold"))
    x.done()


def t_unclassified_keeps_its_road():
    x = in_prove()
    ok(not G._env(x.s, x.w, x.r, "I0", {"A2": row("changed since the built commit, so the game cannot run sha1: a (b)",
                                                   x.now)}, 0, x.now, []),
       "a stale build is not routed here")
    ok(not G._env(x.s, x.w, x.r, "I0", {"A2": dict(row("ran", x.now), outcome="PASS")}, 0, x.now, []), "a PASS is not")
    x.done()


def main():
    picked = set(sys.argv[1:])
    ran = 0
    for t in (t_classify, t_producer_fixed_once_then_routed, t_reload_rides_the_lanes_restage, t_route_kinds_routed_at_once,
              t_same_cause_after_unhold, t_unclassified_keeps_its_road):
        if picked and t.__name__ not in picked:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if picked and ran != len(picked):
        print("selftest_relentless_envcause: FAIL ran %d of the %d named" % (ran, len(picked)))
        return 1
    print("selftest_relentless_envcause: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
