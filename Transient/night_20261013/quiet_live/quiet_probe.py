"""Quiet isolated test-site profile: ONE short live probe batch (BENCH night helper, 2026-10-13).
Fresh quicktest -> read the noise -> apply the isolated profile -> advance 3000 ticks (safe_advance, drained) ->
read vitals/threat channels; then three narrow checks (governor note, support guard + hurt attribution, faction
dialog broker on NS_FlowWorks_TrialSite_v1). Code under test comes from the mirror (D:\\Luke\\dev\\RimMandrake)."""
import json, os, sys, time, traceback
M = r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils"
sys.path.insert(0, M)
sys.path.insert(0, os.path.join(M, "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import quiet_site as Q  # noqa: E402
import helpers as H  # noqa: E402
import clockgate as CG  # noqa: E402

OUT = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
OUTP = r"D:\Luke\dev\_rmscratch\quiet_probe_out.json"
GLOG = r"D:\Luke\dev\_rmscratch\governor_stops.jsonl"


def J(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            return json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


class S(object):
    def __init__(self, rb):
        self.rb = rb

    def call(self, tool, **kw):
        return J(self.rb.call(tool, kw, check=False))


def save():
    with open(OUTP, "w", encoding="utf-8") as f:
        json.dump(OUT, f, indent=1, default=str)


def wait_playing(s, budget=300):
    t0 = time.time()
    while time.time() - t0 < budget:
        try:
            if s.call("rimworld/get_ui_state").get("programState") == "Playing":
                return round(time.time() - t0)
        except Exception:
            pass
        time.sleep(3)
    raise SystemExit("not Playing after %ds" % budget)


def noise(s):
    st = s.call("jawa/quiet_site", action="status")
    pawns = H.read_pawns(s, health=False)
    ws = s.call("jawa/window_list_close", action="list").get("windows") or []
    return {"threats": [(t.get("def"), t.get("faction"), t.get("dormant")) for t in st.get("threats") or []],
            "letters": [(l.get("def"), l.get("sentAfter")) for l in st.get("letters") or []],
            "hostilePawns": [(r["id"], r.get("faction")) for r in pawns if H.is_hostile(r)],
            "forcePause": [Q._wtype(w) for w in ws if w.get("forcePause")],
            "queue": [q.get("defName") for q in s.call("jawa/incident_queue_peek").get("queue") or []]}


def step(name, fn):
    try:
        OUT[name] = fn()
    except SystemExit:
        raise
    except Exception as e:
        OUT[name] = {"EXC": repr(e), "tb": traceback.format_exc()[-1500:]}
    save()
    print(name, json.dumps(OUT[name], default=str)[:600])


with RimBridge(*resolve_endpoint(), timeout=600.0) as rb:
    s = S(rb)
    tools = [t.get("name") for t in (J(rb.call("rimbridge/list_tools", {}, check=False)) or {}).get("tools") or []] \
        if False else None
    OUT["fresh"] = J(rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True,
                                                                 "timeoutMs": 280000}, check=False))
    OUT["playingAfterS"] = wait_playing(s)
    time.sleep(2)
    H.pause(s)
    step("before", lambda: noise(s))

    # the 'hostile' alias fixture (TESTENV_VITALS_HARDEN_FIXTURES_ARE_NOT_HIVES): a hostile Battery must be humanlike-owned
    def alias():
        x, z, d = H.safe_anchor(s)
        b = s.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z), faction="hostile")
        lt = s.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % (x, z), limit=3)
        fac = s.call("jawa/list_factions", limit=60)
        return {"build": b.get("success"), "cell": (x, z), "things": [(t.get("id"), t.get("faction")) for t in lt.get("things") or []],
                "hostileFactions": [(f.get("defName"), f.get("name"), f.get("humanlike")) for f in fac.get("factions") or []
                                    if f.get("hostile") or f.get("hostileToPlayer")][:8]}
    step("alias", alias)

    qs = Q.QuietSite(s, suite="isolated", row="quiet_profile_probe")
    step("apply", lambda: qs.apply())
    step("afterApply", lambda: noise(s))
    step("arm", lambda: s.call("jawa/vitals", action="arm", ttlMin=20, row="quiet_profile_probe",
                                why="quiet profile probe (BENCH night)"))
    step("strangerQueued", lambda: s.call("jawa/incident_schedule", incidentDef="StrangerInBlackJoin", delayTicks=900))
    step("queueBeforeAdvance", lambda: s.call("jawa/incident_queue_peek").get("queue"))
    step("advanced", lambda: qs.advance(3000, chunk=600))
    step("drainEvents", lambda: list(qs.events))
    step("vitalsStatus", lambda: s.call("jawa/vitals", action="status"))
    step("vitalsEvents", lambda: s.call("jawa/vitals", action="events", limit=60))
    step("verify", lambda: qs.verify())
    step("afterAdvance", lambda: noise(s))
    step("letters", lambda: s.call("jawa/letter_list"))

    # GovernorStop leaves a note (TESTENV_GOVERNOR_STOP_DIAGNOSE_NO_NOTE_LEFT): a row budget of 500 refuses a 600 chunk
    def gov():
        n0 = sum(1 for _ in open(GLOG, encoding="utf-8")) if os.path.exists(GLOG) else 0
        s.call("jawa/vitals", action="arm", ttlMin=10, row="quiet_probe_governor", budgetTicks=500, why="governor note probe")
        t0 = s.call("jawa/time_clock").get("ticksGame")
        try:
            CG.advance_chunk(s, 600)
            raised = None
        except CG.GovernorStop as g:
            raised = str(g)
        t1 = s.call("jawa/time_clock").get("ticksGame")
        rows = open(GLOG, encoding="utf-8").read().splitlines() if os.path.exists(GLOG) else []
        return {"raised": raised, "ticksMoved": (t1 - t0) if isinstance(t0, int) and isinstance(t1, int) else None,
                "newRows": [json.loads(x) for x in rows[n0:]]}
    step("governor", gov)

    # support guard + hurt attribution (TESTENV_BURROW_HEAT_..., TESTENV_INJURY_...): a probe colonist is cut,
    # the vitals hurt row must name the newest hediff, the guard records then repairs
    def guard():
        s.call("jawa/vitals", action="arm", ttlMin=10, row="quiet_probe_guard", why="guard probe")
        cols = [r["id"] for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"]]
        col = cols[0]
        g = Q.QuietSite(s, suite="isolated", controls=[], protect_support=True, topic="quiet_probe", support_ids=[col])
        g.apply()
        seq0 = s.call("jawa/vitals", action="status").get("latched", {}).get("seq") or 0
        d = s.call("jawa/damage", thingId=col, damageDef="Cut", amount=12, bodyPart="Torso", allowColonists=True)
        s.call("jawa/vitals", action="sample")
        ev = s.call("jawa/vitals", action="events", sinceSeq=seq0, limit=20).get("triggers") or []
        acts = g.drain(tick=None)
        after = [h.get("def") for h in (dict((r["id"], r) for r in H.read_pawns(s))[col]["health"]["hediffs"])]
        g.restore()
        return {"col": col, "damage": d.get("success"), "hurtRows": [t for t in ev if t.get("kind") == "hurt"],
                "guardActs": acts, "hediffsAfter": after}
    step("guard", guard)
    step("disarm", lambda: s.call("jawa/vitals", action="disarm", why="quiet profile probe done"))
    qs.restore()

    # faction dialog broker (TESTENV_FACTION_DIALOG_HARDEN_FIVE_KNOCKS): the golden save on this tier knocks five times
    def dialogs():
        s.call("rimworld/load_game", saveName="NS_FlowWorks_TrialSite_v1")
        t0 = time.time()
        seen = []
        while time.time() - t0 < 240:
            ws = s.call("jawa/window_list_close", action="list").get("windows") or []
            seen = [Q._wtype(w) for w in ws]
            if any("NewFactionSpawning" in w for w in seen):
                break
            try:
                if s.call("rimworld/get_ui_state").get("programState") == "Playing" and time.time() - t0 > 60:
                    break
            except Exception:
                pass
            time.sleep(3)
        b = Q.QuietSite(s, suite="isolated", controls=["modal_broker"], row="quiet_probe_dialogs")
        try:
            b.apply()
            err = None
        except Q.QuietSiteUnclean as e:
            err = str(e)
        ws2 = [Q._wtype(w) for w in s.call("jawa/window_list_close", action="list").get("windows") or []]
        return {"windowsSeen": seen, "handled": b.applied.get("modal_broker"), "error": err, "windowsAfter": ws2,
                "secs": round(time.time() - t0)}
    step("dialogs", dialogs)
print("DONE", OUTP)
