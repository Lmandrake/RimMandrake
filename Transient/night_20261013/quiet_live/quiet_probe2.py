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


OUTP = r"D:\Luke\dev\_rmscratch\quiet_probe2_out.json"
with RimBridge(*resolve_endpoint(), timeout=600.0) as rb:
    s = S(rb)
    # dialogs first: the game sits on the trial site from probe 1; reload it so the five knocks come again
    def dialogs():
        s.call("rimworld/load_game", saveName="NS_FlowWorks_TrialSite_v1")
        t0 = time.time()
        seen = []
        while time.time() - t0 < 240:
            ws = s.call("jawa/window_list_close", action="list").get("windows") or []
            seen = [Q._wtype(w) for w in ws]
            if any("NewFactionSpawning" in w for w in seen):
                break
            time.sleep(3)
        time.sleep(3)
        n0 = len([w for w in (Q._wtype(x) for x in s.call("jawa/window_list_close", action="list").get("windows") or []) if "NewFactionSpawning" in w])
        b = Q.QuietSite(s, suite="isolated", controls=["modal_broker"], row="quiet_probe_dialogs")
        try:
            b.apply()
            err = None
        except Q.QuietSiteUnclean as e:
            err = str(e)
        time.sleep(1)
        ws2 = [Q._wtype(w) for w in s.call("jawa/window_list_close", action="list").get("windows") or []]
        st = s.call("rimworld/get_ui_state")
        return {"knocksAtStart": n0, "clicks": len((b.applied.get("modal_broker") or {}).get("handled") or []),
                "error": err, "windowsAfter": ws2, "programState": st.get("programState"), "secs": round(time.time() - t0)}
    step("dialogs", dialogs)
    H.pause(s)

    def gov():
        n0 = sum(1 for _ in open(GLOG, encoding="utf-8")) if os.path.exists(GLOG) else 0
        s.call("jawa/vitals", action="arm", ttlMin=10, row="quiet_probe_governor", why="governor note probe")
        t0 = s.call("jawa/time_clock").get("ticksGame")
        r = s.call("jawa/safe_advance", ticks=600, budgetTicks=500, timeoutMs=60000)
        raised = None
        if r.get("state") != "done":
            try:
                raise CG.GovernorStop(r)          # exactly what clockgate.advance_chunk raises on a not-done chunk
            except CG.GovernorStop as g:
                raised = str(g)
        t1 = s.call("jawa/time_clock").get("ticksGame")
        rows = open(GLOG, encoding="utf-8").read().splitlines() if os.path.exists(GLOG) else []
        return {"state": r.get("state"), "raised": raised, "ticksMoved": (t1 - t0) if isinstance(t0, int) and isinstance(t1, int) else None,
                "newRows": [json.loads(x) for x in rows[n0:]]}
    step("governor", gov)

    def guard():
        s.call("jawa/vitals", action="arm", ttlMin=10, row="quiet_probe_guard", why="guard probe")
        cols = [r["id"] for r in H.read_pawns(s, health=False) if H.is_colonist(r) and not r["dead"]]
        col = cols[0]
        g = Q.QuietSite(s, suite="isolated", controls=[], protect_support=True, topic="quiet_probe", support_ids=[col])
        g.apply()
        seq0 = (s.call("jawa/vitals", action="status").get("latched") or {}).get("seq") or 0
        a1 = s.call("jawa/pawn_health", pawn=col, action="add", hediff="Cut", bodyPart="Torso", severity=12)
        a2 = s.call("jawa/pawn_health", pawn=col, action="add", hediff="Heatstroke", severity=0.3)
        s.call("jawa/vitals", action="sample")
        ev = s.call("jawa/vitals", action="events", sinceSeq=seq0, limit=20).get("triggers") or []
        acts = g.drain(tick=None)
        after = [h.get("def") for h in (dict((r["id"], r) for r in H.read_pawns(s))[col]["health"]["hediffs"])]
        g.restore()
        return {"col": col, "add": [a1.get("success"), a2.get("success")], "hurtRows": [t for t in ev if t.get("kind") == "hurt"],
                "guardActs": acts, "hediffsAfter": after}
    step("guard", guard)
    step("disarm", lambda: s.call("jawa/vitals", action="disarm", why="quiet profile probe 2 done"))
print("DONE", OUTP)
