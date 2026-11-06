#!/usr/bin/env python3
"""selftest_relentless_admission.py -- LIVELANE_BUILD_PREFLIGHT_REFUSES_UNRUNNABLE (redesign_final 2026-11-06 G1, WP-01).

One check per acceptance clause, each red under its mutant:
  A every pre-bridge return of relentless_live.run is NOT_ADMITTED with a cause, an action, a key and slot False, and
    the replay of old rows leaves no pre-bridge UNMEASURED row unclassified (the CLI exits 0);
  B a forced deploy-gap row fires the lane's deploy fix (relentless_game._env -> the staging remedy);
  C a forced stale-build row fires its recarry (carried to the new sha) or decides the build (game_stale_build);
  D a NOT_ADMITTED key reruns only after one part (sha, load, site, harness) moves; a transient cause is the timer's;
  E the supervisor's live_check reader (relentless.Effects.live_check through relentless_reach.live_reading) reads;
  F the four SLIs and the old row share are printed.
No game, no bridge, no ledger.
"""
import calendar
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R                      # noqa: E402
import relentless_envcause as E             # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_live as L                 # noqa: E402
import relentless_live_round as LR          # noqa: E402
import relentless_reach as RR               # noqa: E402
import selftest_relentless_game as SG       # noqa: E402
import selftest_relentless_live as SL       # noqa: E402

FAILS = SG.FAILS
ok = SG.ok
GAME = "2026-11-06T11:50:33Z"
GAP = "not deployed: the deploy plan does not cover Graffiti: name it in --deploy"


def t_every_pre_bridge_return_is_not_admitted():
    """A: each way run() stops before the proof is NOT_ADMITTED, its cause read from its why, never UNMEASURED."""
    drift = SL.PLAN + "TheRot  mandrake.rm.therot  1 file(s)\n    ~  TheRot/Defs/Fauna/RM_Chittik.xml\n"
    cases = {"stale": dict(later=[(SL.TOUCHED[0], "ef081426f0")]),
             "deleted": dict(deleted=["src/RimMandrake/TheRot/Defs/Fauna/Old.xml"]),
             "no game": dict(started=None), "old game": dict(mtime=3000.0), "bridge busy": dict(take_rc=1),
             "plan failed": dict(plan=(1, "Traceback")), "drift": dict(plan=(0, drift)),
             "running gap": dict(gap="not in the running load: RM_Biomes (mandrake.rm.biomes)")}
    want = {"stale": "stale", "deleted": "stale", "no game": "no_game", "old game": "old_build",
            "bridge busy": "bridge_busy", "plan failed": "deploy_plan", "drift": "deploy_gap", "running gap": "running_load"}
    rows = []
    for name, kw in cases.items():
        fx = SL.FakeFx(**kw)
        row = SL.go(fx)
        rows.append(row)
        ok(row["outcome"] == L.NOT_ADMITTED and row.get("admit") == want[name] == L.admit_cause(row["why"]),
           "A %s: NOT_ADMITTED %s: %s" % (name, want[name], {k: row.get(k) for k in ("outcome", "admit", "why")}))
        ok(row.get("action") == L.ADMIT[want[name]][0] and row.get("slot") is False
           and set(row.get("key") or {}) == {"sha", "load", "site", "harness"} and row["key"]["sha"] == SL.SHA,
           "A %s: an action, slot False and a 4-part key: %s" % (name, row))
        ok("proof" not in fx.verbs(), "A %s: no proof ran" % name)
    final = SL.item(criteria=[{"id": "F1", "level": L.FINAL, "text": "the running list equals FULL.LATEST"}],
                    outstanding=["F1"])
    fx = SL.FakeFx(it=final, touched=[], full_gap="%s: the running game has 23 mods" % L.FINAL_WAIT)
    row = L.run(fx, tempfile.mkdtemp(prefix="rl_adm_"), "ROT_X", "F1", "python3 x.py", "", {}, now=1_800_000_000)
    ok(row["outcome"] == L.NOT_ADMITTED and row["admit"] == "full_list" and row["action"] == "full_list",
       "A full list: NOT_ADMITTED full_list: %s" % row)
    ok(not SL.FAILS, "A: the live rig's own checks: %s" % SL.FAILS)
    # every prefix reader still routes the words: the gap is a RESTAGE, the stale row is STALE, FINAL_WAIT is the tier's
    ok(rows[-1]["why"].startswith(G.RESTAGE) and rows[0]["why"].startswith(L.STALE), "A: the old words are kept")


def t_replay_leaves_no_pre_bridge_unmeasured():
    """A: old rows -> every pre-bridge UNMEASURED row has a cause; a row that ran keeps UNMEASURED; the CLI exits 0."""
    old = [{"outcome": "UNMEASURED", "why": w, "log": None, "item": "I", "at": GAME}
           for w in ("not in the running load: Graffiti (mandrake.rm.graffiti)", GAP, "no running game to test",
                     "bridge not taken: busy", "%s: small game" % L.FINAL_WAIT,
                     "changed since the built commit, so the game cannot run abc: x (y)")]
    old.append({"outcome": "UNMEASURED", "why": "the proof exited 2", "log": "/l/x.log", "released": True})
    rep = L.admission_replay(old)
    ok(rep["pre_bridge"] == 6 and not rep["unclassified"] and sum(rep["by_cause"].values()) == 6,
       "A replay: 6 pre-bridge rows, all classified, the ran row not counted: %s" % rep)
    ok(L.admission_replay(old + [{"outcome": "UNMEASURED", "why": "something new", "slot": False}])["unclassified"],
       "A replay: an unknown pre-bridge why is reported, never folded into a cause")
    p = os.path.join(tempfile.mkdtemp(prefix="rl_adm_"), "runs.jsonl")
    with open(p, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in old))
    cp = subprocess.run([sys.executable, os.path.join(HERE, "relentless_live.py"), "admission-replay", p],
                        capture_output=True, text=True, timeout=60)
    ok(cp.returncode == 0, "A replay CLI exits 0: %s %s" % (cp.returncode, (cp.stdout + cp.stderr)[-300:]))


def in_prove():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    ok(x.w.proves == ["I0"], "proving")
    return x


def t_deploy_gap_fires_deploy():
    """B: a forced deploy-gap NOT_ADMITTED row is the envcause deploy kind and the lane fixes it in its staging."""
    row = {"at": L.iso(10**9 * 4), "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": L.NOT_ADMITTED,
           "why": GAP, "admit": "deploy_gap", "action": "deploy", "slot": False}
    e = E.classify(row, "I0", [])
    ok(e and e.kind == "deploy" and e.fix and e.mods == ["Graffiti"], "B: the deploy gap is a deploy fix: %s" % (e,))
    x = in_prove()
    acts = []
    G._env(x.s, x.w, x.r, "I0", {"A2": dict(row, at=L.iso(x.now))}, 0, x.now, acts)
    st = x.st("I0")
    ok([a["do"] for a in acts] == ["game_env_fix"] and "Graffiti" in (st["game"].get("remedy") or {}).get("why", ""),
       "B: the deploy action fired, the staging carries it: %s %s" % (acts, st["game"].get("remedy")))
    ok(not st.get("last_fail") and st["status"] == "game", "B: no builder, no generation: %s" % st.get("last_fail"))
    x.done()


def t_stale_build_fires_recarry():
    """C: a forced stale NOT_ADMITTED row carries the build when only rebuilt files moved, else decides it."""
    stale = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SG.SHA, "outcome": L.NOT_ADMITTED,
             "proof": "python3 p.py", "admit": "stale", "action": "recarry", "slot": False,
             "why": "changed since the built commit, so the game cannot run sha1: a (b)"}
    for carry in (("sha2full", "only rebuilt assemblies changed"), None):
        x = in_prove()
        x.w.rows = [dict(stale)]
        x.w.carry = carry
        x.tick()
        st = x.st("I0")
        if carry:
            ok(not st.get("last_fail") and st["game"]["sha"] == "sha2full", "C: recarried: %s" % st.get("last_fail"))
        else:
            ok(st.get("last_fail") and st["last_fail"]["class"] == "game_stale_build",
               "C: no carry: the build is decided stale: %s" % st.get("last_fail"))
        ok(x.w.proves == ["I0"], "C: no second prove round on a stale row")
        x.done()


def t_key_reruns_only_on_a_moved_part():
    """D: (sha, load, site, harness): same key holds; any part moved runs now; a transient cause waits the timer only."""
    site = "python.exe live_site.py --biome RM_Stillsand"
    now = 1_800_000_000
    at = L.iso(now - 60)
    row = {"sha": "s1", "at": at, "outcome": L.NOT_ADMITTED, "admit": "old_build", "action": "wait_load",
           "why": "the game started %s, before the build's files were deployed" % GAME, "game": GAME, "slot": False,
           "key": L.admit_key("s1", GAME, site)}
    held = LR.due(row, "s1", now, 900, game=GAME, site=site)
    ok(held and held.startswith("not admitted (old_build)"), "D: same key holds: %s" % held)
    gap = dict(row, admit="running_load", why="not in the running load: Graffiti (mandrake.rm.graffiti)")
    held = LR.due(gap, "s1", now, 900, game=GAME, site=site, per_game=False)
    ok(held and held.startswith("not admitted (running_load)"), "D: a game phase's round holds on the key too: %s" % held)
    ok(LR.due(gap, "s1", now, 900, game=GAME, site=site + " --size 40", per_game=False) is None,
       "D: and runs when its site moves")
    ok(LR.due(row, "s1", now, 900, game="2026-11-06T13:00:00Z", site=site) is None, "D: a new load runs at once")
    ok(LR.due(row, "s1", now, 900, game=GAME, site=site + " --size 40") is None, "D: a new site runs at once")
    ok(LR.due(row, "s2", now, 900, game=GAME, site=site) is None, "D: a new build runs at once")
    moved = dict(row, key=dict(row["key"], harness="0" * 12))
    ok(LR.due(moved, "s1", now, 900, game=GAME, site=site) is None, "D: a repaired harness runs at once")
    ok(LR.due(row, "s1", now + 10**6, 900, game=GAME, site=site), "D: same key never ages into a rerun")
    busy = dict(row, admit="bridge_busy", action="retry", why="bridge not taken: busy")
    ok(LR.due(busy, "s1", now, 900, game=GAME, site=site) == "unmeasured lately"
       and LR.due(busy, "s1", now + 900, 900, game=GAME, site=site) is None,
       "D: a transient cause is the retry timer's, never the key's")
    ok(L.admit_key("s1", GAME, site)["harness"] == L.harness_rev() and len(L.harness_rev()) == 12,
       "D: the harness part is the harness source's hash")


def t_live_check_reader_reads():
    """E: relentless_reach.live_reading calls check(line, now=now); the supervisor's Effects.live_check takes it."""
    got = RR.live_reading("once: the build adds a def", lambda line, now=None: R.Effects.live_check(None, line, now=now),
                          now=1_800_000_000)
    ok(got["state"] == RR.HOLDS and got["holds"], "E: the live_check reader reads: %s" % got)
    got = RR.live_reading("not a live line", lambda line, now=None: R.Effects.live_check(None, line, now=now))
    ok(got["state"] == RR.DOES_NOT_HOLD, "E: a bad line is DOES NOT HOLD, never COULD NOT READ: %s" % got)


def t_slis_printed():
    """F: the four SLIs per distinct key on the newest load, and the old row share labelled as such."""
    def r(item, outcome, at, **kw):
        return dict({"item": item, "criterion": "A2", "sha": "s" + item, "outcome": outcome, "at": at, "game": GAME,
                     "log": "/l/%s.log" % item, "released": True}, **kw)
    later = "2026-11-06T12:30:00Z"
    rows = [r("1", "PASS", later), r("2", "UNMEASURED", later), r("2", "UNMEASURED", later),
            r("3", L.NOT_ADMITTED, later, admit="deploy_gap", action="deploy", slot=False, log=None, released=None),
            r("4", "FAIL", later), {"item": "5", "outcome": "UNMEASURED", "at": 1.5}]
    t = calendar.timegm(time.strptime(later, "%Y-%m-%dT%H:%M:%SZ"))
    now = t + 3600
    s = L.live_slis(rows, now, built_at=lambda sha: t - 7200 if sha == "s1" else None)
    ok(s["load"] == GAME and s["keys"] == 4, "F: distinct keys on the newest load: %s" % s)
    ok(s["not_admitted_by_cause"] == {"deploy_gap": {"keys": 1, "action": "deploy", "fired": 1}},
       "F1: NOT_ADMITTED keys by cause and whether the action fired: %s" % s["not_admitted_by_cause"])
    ok(s["slot_keys"] == 3 and s["slot_unmeasured_share"] == round(1 / 3.0, 3),
       "F2: slot-spending UNMEASURED share per key, not per row: %s" % s)
    ok(s["measured_keys_per_day"] == 2.0 and s["built_to_verdict_s"] == {"p50": 7200, "p95": 7200, "n": 1}, "F3/F4: completions and lag: %s" % s)
    lines = L.sli_lines(s)
    for n, word in (("1", "NOT_ADMITTED keys by cause"), ("2", "slot-spending UNMEASURED share"),
                    ("3", "measured completions (PASS+FAIL keys) per day"), ("4", "built -> first measured verdict")):
        ok(any(x.startswith("  %s %s" % (n, word)) for x in lines), "F%s printed: %s" % (n, lines))
    ok(any("rows incl. repeats and admission" in x for x in lines), "F: the old share is printed and labelled")
    ok(L.sli_lines({"unread": "boom"})[0].startswith("live SLIs: COULD NOT READ"), "F: an unread SLI says so")


def main():
    for t in (t_every_pre_bridge_return_is_not_admitted, t_replay_leaves_no_pre_bridge_unmeasured,
              t_deploy_gap_fires_deploy, t_stale_build_fires_recarry, t_key_reruns_only_on_a_moved_part,
              t_live_check_reader_reads, t_slis_printed):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a crashing case is a failed case, never a skipped one
            import traceback
            ok(False, "%s raised %s: %s" % (t.__name__, e, traceback.format_exc()[-600:]))
    if FAILS:
        print("FAIL selftest_relentless_admission: %d" % len(FAILS))
        for f in FAILS:
            print("  -", f)
        return 1
    print("PASS selftest_relentless_admission")
    return 0


if __name__ == "__main__":
    sys.exit(main())
