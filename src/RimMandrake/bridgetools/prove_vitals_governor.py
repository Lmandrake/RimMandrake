r"""Run: python.exe D:\Luke\dev\RimMandrake\src\RimMandrake\bridgetools\prove_vitals_governor.py [case ...]
(game up at the main menu or in a game; minimal list PLUS mandrake.rm.gimmesomeslack, see COMPANION_STATIC_LAMBDAS_UNBLOCK_WITHOUT_GSS)

Live acceptance proofs for the test-state monitor + row governor (TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO).
GPT §5 table cases that inject cheaply on a quicktest map. Each case writes {case: {result, evidence}}."""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import sys, json, time, os
# VITALSPROOF_FIX_EXIT0_AND_MIRROR_IMPORT: governor came from the hardcoded mirror path, so a clone's run judged
# with the mirror's (possibly older) governor; the path is now derived from this file, like rmpaths above.
_UTILS = _rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"
sys.path.insert(0, str(_UTILS / "modcheck"))
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
    rec3(case, "PASS" if ok else "FAIL", **ev)

def rec3(case, result, **ev):
    """result: PASS | FAIL | UNMEASURED (the row could not look; its cause is in ev)."""
    OUT[case] = {"result": result, **ev}
    print(result + " " + case + "  " + json.dumps(ev, default=str)[:600], flush=True)

def finish():
    """Write every row measured so far and exit by the contract: 1 = a row FAILED; 3 = no row failed but a row could
    not look (UNMEASURED) or no row ran; 0 = every row PASS."""
    name = os.path.join(rm_win("scratch", "vitals"), "proof_" + "_".join(which)) + "_" + time.strftime("%Y%m%dT%H%M%S") + ".json"
    os.makedirs(os.path.dirname(name), exist_ok=True)
    with open(name, "w") as f: json.dump(OUT, f, indent=1, default=str)
    print("wrote", name)
    # VITALSPROOF_FIX_EXIT0_AND_MIRROR_IMPORT: the old script exited 0 whatever rec() recorded.
    failed = [k for k, v in OUT.items() if v["result"] == "FAIL"]
    blind_rows = [k for k, v in OUT.items() if v["result"] not in ("PASS", "FAIL")]
    print("%d/%d passed%s%s" % (len(OUT) - len(failed) - len(blind_rows), len(OUT),
                                ("; FAILED: " + ", ".join(failed)) if failed else "",
                                ("; UNMEASURED: " + ", ".join(blind_rows)) if blind_rows else ""))
    sys.exit(1 if failed else 3 if blind_rows or not OUT else 0)

def blind(cause):
    """A case that cannot look stops the run: record it UNMEASURED with its cause, keep the rows already measured, and
    exit 3 (a bare SystemExit("...") exited 1, which reads as FAILED, and wrote no rows)."""
    print("UNMEASURED: " + cause, flush=True)
    rec3("run_stopped_could_not_look", "UNMEASURED", cause=cause)
    finish()

# RimPulse reads alarms from the store's FIRST game only (telemetry/analysis.py: a lane game's live view alarms nothing),
# so a red-alarm row is measured on ArchBig (RM_GAME_INSTANCE a or unset) and is UNMEASURED on any other game.
PULSE_WAIT_S = 120   # hang guard: telemetryd down or blind. Need: alerts.json is rewritten every few s (6 s old, measured
                     # 2026-11-27) and the armed TPS row is 1 s, so a real alarm shows in about 10 s; 120 s is over 10x that.

def pulse_alarm(aid, since):
    """-> (PASS|FAIL|UNMEASURED, evidence): a red `aid` alert in RimPulse's alerts.json written after `since`."""
    inst = os.environ.get("RM_GAME_INSTANCE") or "a"
    if inst != "a":
        return "UNMEASURED", "RimPulse alarms read ArchBig only (analysis.py); this run drives game instance %r" % inst
    sys.path.insert(0, str(_UTILS / "telemetry"))
    from tcommon import cfg
    path = os.path.join(cfg()["state"], "alerts.json")
    end, last = time.time() + PULSE_WAIT_S, "alerts.json never read: " + path
    while time.time() < end:
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except Exception as ex:   # noqa: BLE001 (a half-written file is retried; its cause is kept)
            last = "alerts.json unreadable: %r" % ex
            time.sleep(2); continue
        if (d.get("at") or 0) >= since:
            hit = [a for a in d.get("alerts") or [] if a.get("id") == aid and a.get("level") == "red"]
            if hit:
                return "PASS", hit[0]
            last = "fresh alerts.json (at %s) holds no red %s: %s" % (d.get("at"), aid, [a.get("id") for a in d.get("alerts") or []])
        else:
            last = "alerts.json not rewritten since the trigger (at %s < %s): telemetryd blind or down" % (d.get("at"), since)
        time.sleep(2)
    return ("FAIL" if last.startswith("fresh") else "UNMEASURED"), last

def ticks():
    # BRIDGE_PROOFS_W50_BLIND_LOG_AND_WRONG_MAP: a failed read was None == None, so "no tick ran" passed blind
    t = call("jawa/time_clock").get("ticksGame")
    if not isinstance(t, int):
        blind("jawa/time_clock gave no ticksGame, so a refusal cannot be shown to have run no tick")
    return t

def fresh_map():
    call("rimworld/go_to_main_menu")
    import os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'Utils'))
    from await_lifecycle import await_lifecycle  # noqa: E402
    if not await_lifecycle(call, "menu", 60): print("UNMEASURED: main menu not reached")
    call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    lc = await_lifecycle(call, "map_ready", 120)
    if not lc.ok: blind("no map after start: %s" % lc.reason)
    time.sleep(3)
    # A quicktest map can roll a dormant insect hive (live 2026-11-27, ArchSmall: "Hive (Sorne Geneline, spawner,
    # dormant)"), which the monitor rightly latches as an open threat, so every row read UNMEASURED. Each case wants a
    # bland map: vanish the hostile threat structures first (jawa/quiet_site uses the monitor's own classifier) and
    # read back that none is left.
    q = call("jawa/quiet_site", action="apply", clearThreats=True)
    if not q.get("success") or q.get("threatsAfter") != 0:
        blind("the map's hostile threat structures were not cleared before arm: %s"
                         % json.dumps(q, default=str)[:300])
    ps = call("jawa/list_pawns", faction="player").get("pawns") or []
    return [p["id"] for p in ps if p.get("def") == "Human" and not p.get("dead")]

def far_cell(from_id):
    """A standable cell far from pawn `from_id`: the cell of the non-player pawn farthest from it (pawns stand only on
    standable cells). -> (x, z), or the run stops UNMEASURED (blind)."""
    me = [p for p in call("jawa/list_pawns", faction="player").get("pawns") or [] if p.get("id") == from_id]
    others = [p for p in call("jawa/list_pawns", faction="nonplayer").get("pawns") or []
              if not p.get("dead") and isinstance(p.get("x"), int) and isinstance(p.get("z"), int)]
    if not me or not others:
        blind("no far standable cell (colonist seen %s, other pawns %d)" % (bool(me), len(others)))
    mx, mz = me[0]["x"], me[0]["z"]
    far = max(others, key=lambda p: (p["x"] - mx) ** 2 + (p["z"] - mz) ** 2)
    return far["x"], far["z"]

def events():
    # the latch holds 512 (JawaBenchVitalsCore.LatchCapacity) and events returns only the NEWEST `limit`: a dropped
    # trigger would let G.judge read PASS on a list missing what disqualifies it
    r = call("jawa/vitals", action="events", limit=512)
    if not isinstance(r.get("triggers"), list) or r.get("truncated") or r.get("overflow"):
        blind("jawa/vitals events incomplete (truncated=%r overflow=%r): %s"
                         % (r.get("truncated"), r.get("overflow"), json.dumps(r, default=str)[:300]))
    return r

def arm(row, critical=None, **kw):
    p = {"action": "arm", "row": row, "ttlMin": 30, "why": "live proof"}
    if critical: p["critical"] = critical
    p.update(kw)
    r = call("jawa/vitals", **p)
    if not r.get("armed"):
        blind("jawa/vitals would not arm row %s: %s" % (row, json.dumps(r, default=str)[:300]))
    return r

which = sys.argv[1:] or ["clock", "modal", "cluster", "raid", "downed", "death", "specimen", "hostile", "colonyloss"]

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
    # any failure (bad param, no game) is not THE refusal: it names the populated map
    rec("clock_set_refused_on_populated_map", r.get("success") is False and str(r.get("message") or "").startswith("REFUSED")
        and (r.get("details") or {}).get("populated") is True and ticks() == t0, message=r.get("message"))
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
    # an empty trigger list also judges PASS/CLEAN: only a seen-then-corrected modal shows the correction path
    rec("modal_closed_corrected_may_pass", bool(ms) and v["outcome"] == G.PASS and v["validity"] == "CLEAN", governor=v["outcome"], notes=v["notes"])

# cheaper_why: raid tests are paused (raid_pause.py, owner 2026-11-23), and neither bar needs a raid. The cluster bar is
# "a hostile structure with no hostile pawn is a threat", decided by one harmless building that a non-humanlike faction
# owns (the monitor's classifier counts every such building). The raid bar is "a hostile arrival stops a long step",
# decided by one hostile pawn put down far from the colony while the step runs; nothing attacks, because the step
# stops at once and the game stays paused.
if "cluster" in which:
    cols = fresh_map()
    arm("proof_cluster", critical=cols[0])
    x, z = far_cell(cols[0])
    b = call("jawa/build_batch", ops="Wall:%d,%d" % (x, z), stuff="Steel", faction="Mechanoid")
    call("jawa/vitals", action="sample")
    ev = events()
    # the trigger must name OUR wall (a new structure after arm, threats cleared before it), so the structure alone
    # raised it; hostile pawns the map holds are recorded, not required absent (live 2026-11-27: 4 on ArchBig's map)
    ts = [t for t in ev.get("triggers", []) if t["kind"] == "threat_structure" and t.get("subject") == "Wall"
          and "new hostile structure" in (t.get("detail") or "")]
    ha = [t for t in ev.get("triggers", []) if t["kind"] == "hostile_arrival"]
    st = call("jawa/vitals")
    rec("hostile_structure_threat_detected_without_hostile_pawn_count", bool(b.get("survived")) and len(ts) > 0,
        built=b.get("survived"), cell=(x, z), structures=st.get("threats"), structure_triggers=len(ts),
        first_structure=ts[:1], hostile_pawn_triggers=len(ha), hostile_pawns=[t.get("detail") for t in ha[:3]])

if "raid" in which:
    cols = fresh_map()
    arm("proof_raid", critical=cols[0])
    x, z = far_cell(cols[0])
    t0 = ticks()
    r0 = call("jawa/safe_advance", ticks=25000, timeoutMs=500)
    sp = call("jawa/spawn_pawn", kindDef="Drifter", faction="hostile", x=x, z=z, count=1)
    for _ in range(240):
        s = call("jawa/safe_advance", action="status").get("advance") or {}
        if s.get("state") != "running": break
        time.sleep(0.5)
    call("rimworld/pause_game", pause=True)
    sb = s.get("stopBy") or {}
    rec("hostile_arrival_during_long_step_interrupts_locally", r0.get("state") == "running" and bool(sp.get("success"))
        and s.get("state") == "stopped" and s.get("executed", 0) < 25000 and sb.get("kind") == "hostile_arrival",
        first_state=r0.get("state"), spawned=sp.get("success"), spawn_msg=str(sp.get("message") or sp.get("error"))[:200],
        cell=(x, z), state=s.get("state"), executed=s.get("executed"), stopBy=sb, tick_from=t0, tick_to=ticks())
    v = G.judge(G.RowContract("proof_raid", actors=(cols[0],)), events()["triggers"], "PASS")
    rec("hostile_arrival_is_a_threat_with_env_item", any("TESTENV_HOSTILES" in e for e in v["env_items"]) and v["outcome"] != G.PASS,
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
    r2 = call("jawa/list_pawns", includeCorpses=True, faction="player"); corpses2 = r2.get("pawns")
    ev = events()
    tomb = [t for t in ev.get("tombs", []) if ('"label"' in t)]
    vnum = int("".join(ch for ch in victim if ch.isdigit()) or -1)   # triggers carry thingIDNumber
    death = [t for t in ev.get("triggers", []) if t["kind"] == "death" and t.get("subjectId") == vnum]
    # "after corpse removal" needs a corpse that was SEEN and destroyed, and a second read that worked: a failed
    # list_pawns read (no rows) used to count as "corpse gone" with nothing ever removed
    removed = bool(c) and bool((gone or {}).get("success")) and isinstance(corpses2, list) \
        and not [p for p in corpses2 if p.get("id") == victim]
    rec("death_retained_after_corpse_removal", bool(death) and bool(tomb) and removed,
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

if "hostile" in which:
    # a colonist who turns on the colony (berserk: pawn.HostileTo(player) is true) latches colonist_hostile and raises
    # RimPulse's red vitals:colonist_hostile alarm
    cols = fresh_map()
    arm("proof_hostile", critical=cols[0])
    since = time.time()
    m = call("jawa/pawn_mental", action="start", pawn=cols[1], state="Berserk")
    call("jawa/vitals", action="sample")
    ch = [t for t in events().get("triggers", []) if t["kind"] == "colonist_hostile"]
    rec("colonist_turned_hostile_latched", bool(m.get("started")) and bool(ch),
        started=m.get("started"), state=m.get("currentState"), pawn=cols[1], trigger=ch[:1])
    pr, pev = pulse_alarm("vitals:colonist_hostile", since)
    rec3("colonist_hostile_raises_red_rimpulse_alarm", pr, alert=pev)
    call("jawa/pawn_mental", action="end", pawn=cols[1])

if "colonyloss" in which:
    cols = fresh_map()
    arm("proof_colonyloss")
    since = time.time()
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
    pr, pev = pulse_alarm("vitals:colony_dead", since)
    rec3("colony_loss_raises_red_rimpulse_alarm", pr, alert=pev)
    sl = call("jawa/send_letter", label="GameOver (injected by proof)", text="injected", letterDef="GameEnded")
    time.sleep(1.0)
    cl2 = [t for t in events().get("triggers", []) if t["kind"] == "colony_loss" and "GameEnded letter" in (t.get("detail") or "")]
    rec("colony_loss_letter_detected_while_paused", bool(cl2), sent=sl.get("success"), trigger=cl2[:1])

finish()
