r"""Run: python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\bridgetools\prove_vitals_governor.py [case ...]
(game up at the main menu or in a game; minimal list PLUS mandrake.rm.gimmesomeslack, see COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS)

Live acceptance proofs for the test-state monitor + row governor (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO).
GPT §5 table cases that inject cheaply on a quicktest map. Each case writes {case: {result, evidence}}."""
import sys, json, time, os
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\modcheck")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=900.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
class Sess:
    def call(self, t, **p): return call(t, **p)
def j(x): print(json.dumps(x, default=str)[:3000])

import governor as G

OUT = {}
def rec(case, ok, **ev):
    OUT[case] = {"result": "PASS" if ok else "FAIL", **ev}
    print(("PASS " if ok else "FAIL ") + case + "  " + json.dumps(ev, default=str)[:600], flush=True)

def ticks(): return call("jawa/time_clock").get("ticksGame")

def fresh_map():
    call("rimworld/go_to_main_menu")
    for _ in range(60):
        if call("rimworld/get_ui_state").get("programState") == "Entry": break
        time.sleep(1)
    call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    for _ in range(120):
        if call("rimworld/get_ui_state").get("programState") == "Playing": break
        time.sleep(1)
    time.sleep(3)
    ps = call("jawa/list_pawns", faction="player").get("pawns") or []
    return [p["id"] for p in ps if p.get("def") == "Human" and not p.get("dead")]

def events(): return call("jawa/vitals", action="events", limit=500)

def arm(row, critical=None, **kw):
    p = {"action": "arm", "row": row, "ttlMin": 30, "why": "live proof"}
    if critical: p["critical"] = critical
    p.update(kw)
    r = call("jawa/vitals", **p)
    assert r.get("armed"), r
    return r

which = sys.argv[1:] or ["clock", "modal", "cluster", "raid", "downed", "death", "specimen", "colonyloss"]

if "clock" in which:
    cols = fresh_map()
    arm("proof_clock", critical=cols[0])
    st = call("jawa/vitals")
    rec("arm_baseline", st.get("hooks") == "complete" and st.get("samples", 0) >= 1 and '"colonistsAlive":' in (st.get("rollup") or ""),
        hooks=st.get("hooks"), driver=st.get("driver"), rollup=st.get("rollup"), populated=st.get("populated"))
    t0 = ticks()
    r = call("jawa/safe_advance", ticks=600000)
    rec("advance_600k_refused_before_any_tick", r.get("state") == "refused" and ticks() == t0,
        state=r.get("state"), refused=r.get("refused"), tick_before=t0, tick_after=ticks())
    r = call("jawa/time_set_ticks", ticks=t0 + 2500)
    rec("clock_set_refused_on_populated_map", r.get("success") is False and ticks() == t0, message=r.get("message"))
    r = call("jawa/time_set_ticks", ticks=t0 + 2500, timeException=True, why="live proof: declared reassignment")
    time.sleep(1.0)
    ev = events()
    cd = [t for t in ev.get("triggers", []) if t["kind"] == "clock_discontinuity"]
    c_plain = G.RowContract("proof_clock", about=("terrain",))
    c_exc = G.RowContract("proof_clock_exc", about=("growth",), time_exception=True)
    v1, v2 = G.judge(c_plain, ev["triggers"], "PASS"), G.judge(c_exc, ev["triggers"], "PASS")
    rec("declared_reassignment_detected_and_not_clean_without_exception",
        bool(cd) and cd[0]["declared"] and v1["outcome"] == G.RESTART and v2["outcome"] == G.PASS,
        trigger=cd[:1], verdict_plain=v1["outcome"], verdict_with_exception=v2["outcome"])
    call("jawa/debug_settings", action="set", field="fastEcology", value="true")
    t1 = ticks()
    r = call("jawa/safe_advance", ticks=10, chunk=1)
    call("jawa/debug_settings", action="set", field="fastEcology", value="false")
    sb = r.get("stopBy") or {}
    rec("undeclared_clock_jump_stops_advance", r.get("state") == "stopped" and sb.get("kind") == "clock_discontinuity" and not sb.get("declared"),
        state=r.get("state"), executed=r.get("executed"), stopBy=sb, tick_from=t1, tick_to=ticks())

if "modal" in which:
    arm("proof_modal")
    call("rimworld/pause_game", pause=True)
    w = call("rimworld/open_window_by_type", windowType="RimWorld.Dialog_Options")
    time.sleep(33)
    ev = events()
    ms = [t for t in ev.get("triggers", []) if t["kind"] == "modal_stuck"]
    st = call("jawa/vitals")
    v = G.judge(G.RowContract("proof_modal"), ev["triggers"], "PASS")
    rec("modal_while_paused_detected_by_wall_time", bool(ms) and st.get("paused") and st.get("modalMaxAgeS", 0) >= 30,
        opened=w.get("success"), trigger=ms[:1], modalMaxAgeS=st.get("modalMaxAgeS"), paused=st.get("paused"),
        governor_uncorrected=v["outcome"], env_items=v["env_items"][:1])
    call("rimworld/close_window", windowType="RimWorld.Dialog_Options")
    v = G.judge(G.RowContract("proof_modal"), ev["triggers"], "PASS", corrected={t["seq"] for t in ms})
    rec("modal_closed_corrected_may_pass", v["outcome"] == G.PASS and v["validity"] == "CLEAN", governor=v["outcome"], notes=v["notes"])

if "cluster" in which:
    cols = fresh_map()
    arm("proof_cluster", critical=cols[0])
    r = call("jawa/fire_incident", incidentDef="MechCluster", forced=True, dryRun=False, points=800)
    adv = call("jawa/safe_advance", ticks=2500, stopOn="threat_structure")
    call("jawa/vitals", action="sample")
    ev = events()
    ts = [t for t in ev.get("triggers", []) if t["kind"] == "threat_structure"]
    ha = [t for t in ev.get("triggers", []) if t["kind"] == "hostile_arrival"]
    st = call("jawa/vitals")
    rec("dormant_cluster_threat_detected_without_hostile_pawn_count", len(ts) > 0,
        fired=r.get("success"), advance=adv.get("state"), executed=adv.get("executed"), stopBy=adv.get("stopBy"), structures=st.get("threats"), structure_triggers=len(ts),
        first_structure=ts[:1], hostile_pawn_triggers=len(ha))

if "raid" in which:
    cols = fresh_map()
    arm("proof_raid", critical=cols[0])
    t0 = ticks()
    r0 = call("jawa/safe_advance", ticks=25000, timeoutMs=500)
    raid = call("jawa/fire_raid", dryRun=False, points=300)
    for _ in range(240):
        s = call("jawa/safe_advance", action="status").get("advance") or {}
        if s.get("state") != "running": break
        time.sleep(0.5)
    sb = s.get("stopBy") or {}
    rec("raid_during_long_step_interrupts_locally", r0.get("state") == "running" and s.get("state") == "stopped"
        and s.get("executed", 0) < 25000 and sb.get("kind") == "hostile_arrival",
        first_state=r0.get("state"), raid=raid.get("success"), raid_msg=str(raid.get("message"))[:200], state=s.get("state"),
        executed=s.get("executed"), stopBy=sb, tick_from=t0, tick_to=ticks())
    v = G.judge(G.RowContract("proof_raid", actors=(cols[0],)), events()["triggers"], "PASS")
    rec("raid_is_a_threat_with_env_item", any("TESTENV_HOSTILES" in e for e in v["env_items"]) and v["outcome"] != G.PASS,
        outcome=v["outcome"], validity=v["validity"], env_items=[e.split(" --for")[0] for e in v["env_items"]])

if "downed" in which:
    cols = fresh_map()
    arm("proof_downed", critical=cols[0])
    r = call("jawa/safe_advance", ticks=12000, timeoutMs=400)
    d = call("jawa/pawn_force_incapacitate", action="downed", pawn=cols[0], allowBleedingWounds=False)
    for _ in range(120):
        s = call("jawa/safe_advance", action="status").get("advance") or {}
        if s.get("state") != "running": break
        time.sleep(0.5)
    sb = s.get("stopBy") or {}
    v = G.judge(G.RowContract("proof_downed", actors=(cols[0],)), events()["triggers"], "FAIL")
    rec("worker_downed_during_wait_is_disrupted_restart_not_fail",
        s.get("state") == "stopped" and sb.get("kind") in ("downed", "hurt") and v["outcome"] == G.RESTART and v["validity"] == "DISRUPTED",
        first_state=r.get("state"), downed=d.get("success"), state=s.get("state"), executed=s.get("executed"), stopBy=sb,
        outcome=v["outcome"], validity=v["validity"], notes=v["notes"])

if "death" in which:
    cols = fresh_map()
    arm("proof_death", critical=cols[0])
    victim = cols[1]
    k = call("jawa/pawn_force_incapacitate", action="kill", pawn=victim)
    corpses = call("jawa/list_pawns", includeCorpses=True, faction="player").get("pawns") or []
    c = [p for p in corpses if p.get("id") == victim]
    gone = None
    if c:
        x, z = c[0]["x"], c[0]["z"]
        gone = call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Item")
    corpses2 = call("jawa/list_pawns", includeCorpses=True, faction="player").get("pawns") or []
    ev = events()
    tomb = [t for t in ev.get("tombs", []) if ('"label"' in t)]
    death = [t for t in ev.get("triggers", []) if t["kind"] == "death"]
    rec("death_retained_after_corpse_removal", bool(death) and bool(tomb) and not [p for p in corpses2 if p.get("id") == victim],
        killed=k.get("success"), corpse_destroyed=(gone or {}).get("success"), death=death[:1], tombs=len(tomb))

if "specimen" in which:
    cols = fresh_map()
    x, z = 100, 100
    for p in call("jawa/list_pawns", faction="player").get("pawns") or []:
        if p.get("id") == cols[0]: x, z = p["x"] + 3, p["z"] + 3
    call("rimworld/spawn_thing", defName="Steel", stackCount=10, x=x, z=z)
    th = [t for t in (call("jawa/list_things", defName="Steel", rect="%d,%d,1,1" % (x, z)).get("things") or [])]
    sid = th[0]["id"] if th else None
    arm("proof_specimen", critical=cols[0], specimens=sid)
    call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Item")
    call("jawa/vitals", action="sample")
    ev = events()
    sl = [t for t in ev.get("triggers", []) if t["kind"] == "specimen_lost"]
    v = G.judge(G.RowContract("proof_specimen", specimens=(sid,)), ev["triggers"], "FAIL")
    rec("specimen_lost_blocks_false_fail", bool(sl) and v["outcome"] == G.RESTART, specimen=sid, trigger=sl[:1], outcome=v["outcome"])

if "colonyloss" in which:
    cols = fresh_map()
    arm("proof_colonyloss")
    call("jawa/safe_advance", ticks=400)          # GameEnder ignores deaths before TicksGame 300
    call("jawa/debug_settings", action="set", field="enableStoryteller", value="false")   # no Man in Black rescue
    for c in cols:
        call("jawa/pawn_force_incapacitate", action="kill", pawn=c)
    r = call("jawa/safe_advance", ticks=600, stopOn="cancel")
    time.sleep(1)
    ev = events()
    cl = [t for t in ev.get("triggers", []) if t["kind"] == "colony_loss"]
    call("jawa/debug_settings", action="set", field="enableStoryteller", value="true")
    rec("colony_loss_detected_gameender_and_alive0", any("GameEnder" in (t.get("detail") or "") for t in cl) and any("alive colonists 0" in (t.get("detail") or "") for t in cl),
        advance=r.get("state"), executed=r.get("executed"), triggers=cl[:3],
        note="vanilla's Man in Black rescue (StrangerInBlackJoin at tick 581) cancels the countdown before the GameEnded letter")
    sl = call("jawa/send_letter", label="GameOver (injected by proof)", text="injected", letterDef="GameEnded")
    time.sleep(1.0)
    cl2 = [t for t in events().get("triggers", []) if t["kind"] == "colony_loss" and "GameEnded letter" in (t.get("detail") or "")]
    rec("colony_loss_letter_detected_while_paused", bool(cl2), sent=sl.get("success"), trigger=cl2[:1])

name = os.path.join(r"D:\Luke\dev\_rmscratch\vitals", "proof_" + "_".join(which)) + "_" + time.strftime("%Y%m%dT%H%M%S") + ".json"
with open(name, "w") as f: json.dump(OUT, f, indent=1, default=str)
print("wrote", name)
