"""wet_costs_live.py -- the L2 rows of WET_FOXHOLE_BUILD_COLD_FEET_SHAKY_AIM (what standing in water costs; canal cover
design §5, owner Q4/Q6/Q8 2026-10-18), each row an evidence line written to the result JSON as it is measured.

    python.exe src/RimMandrake/FlowWorks/northstar/wet_costs_live.py [--fresh-map] [out.json]

Run from the repo root with python.exe; the bridge must be held; the flowworks tier running with a FlowWorks DLL that has
RM_WetCosts (ProofWet / ProofShot). Every touched setting is restored in `finally`. Each row compares ONE pawn with a setting
on and off, so skill, weapon and distance cancel.

Rows:
  WET_aim_chest_deep_x085         a rifle colonist in a 1.5 m wet pit (dig 3, fill 3): ShotReport aim with deepWaterAimPenalty
                                  ON / OFF = 0.85 (+-0.01); aimFactor reads 0.850.
  WET_aim_dry_unchanged           a second rifle colonist on dry ground: ON / OFF = 1.
  WET_cold_comfymin_plus6         a colonist standing in 1 m dug water: ComfyTemperatureMin with wetFeelsColder ON minus OFF = 6.
  WET_cold_dry_unchanged          a second colonist on dry ground: ON minus OFF = 0.
  WET_swimmer_no_guns             a rifle colonist in 3 m dug water (dig 6, fill 6), swimming: CanHitTargetFrom false with
                                  swimmersCannotShoot ON, true OFF (the OFF read is the control: false there = another rule
                                  refuses, UNMEASURED).
  WET_downed_drowning_warned      a colonist downed in 1 m dug water: "X is drowning." appears in the message log while it is
                                  still alive (Q8; built before this item, RM_Swim.DrownMessage).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

WET = "RimMandrake.FlowWorks.Swimming.RM_WetCosts"
S_SW = "RimMandrake.FlowWorks.Swimming.RM_SwimSettings"
SW_FIELDS = ("deepWaterAimPenalty", "wetFeelsColder", "swimmersCannotShoot")


def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def num(d, k):
    try:
        return float(d.get(k))
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "wet_costs_live_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "wet_costs_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    could_not = []

    def row(rid, st, det):
        if st == "FAIL" and could_not:     # "could not ask" is UNMEASURED, never a MOD FAIL
            det = dict(det, couldNotAsk=list(could_not))
            st = "UNMEASURED"
        del could_not[:]
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:420]), flush=True)
        save()

    def sc(method, arg=""):
        r = B.call("jawa/static_call", type=WET, method=method, args=arg) or {}
        if not r.get("success"):
            could_not.append("%s.%s refused" % (method, arg[:30]))
        return str(r.get("result") if r.get("success") else (r.get("message") or r.get("error") or r))

    def fget(f):
        return (B.call("jawa/mod_settings_field", typeName=S_SW, action="get", field=f) or {}).get("value")

    def fset(f, v):
        r = B.call("jawa/mod_settings_field", typeName=S_SW, action="set", field=f, value=str(v)) or {"success": False}
        if r.get("success") is False:
            could_not.append("set %s refused" % f)
        return r

    def dig(c, n, fill=-1):
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}
        if r.get("success") is False:
            could_not.append("dig %s refused" % (c,))
        return r

    def spawn(kind, c, faction):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if not pid:
            could_not.append("spawn %s failed" % kind)
        return pid

    def pit(o, w, h, n, fill):
        for i in range(w):
            for j in range(h):
                dig((o[0] + i, o[1] + j), n, fill)

    def on_off(field, read):
        fset(field, True)
        r_on = read()
        fset(field, False)
        r_off = read()
        fset(field, True)
        return r_on, r_off

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    before = {f: fget(f) for f in SW_FIELDS}
    res["settings_before"] = before
    save()
    try:
        if not ok:
            row("site", "UNMEASURED", {"why": "not playing"})
            return 2
        B.call("jawa/kill_hostiles")
        B.call("jawa/quiet_site", action="apply", clearThreats=True, proximityLetters=True)
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False)   # restored in finally
        ox, oz = 140, 100
        rect = (ox, oz, 30, 14)
        if not V.prepare_site(B, rect, rows, "WET_site_ready"):
            row("WET_site", "UNMEASURED", {"why": "site not ready"})
            return 2
        chest = (ox + 2, oz + 2)        # 3x3, 1.5 m deep, full
        waist = (ox + 8, oz + 2)        # 3x3, 1 m deep, full
        deep = (ox + 14, oz + 2)        # 3x3, 3 m deep, full
        pit(chest, 3, 3, 3, 3)
        pit(waist, 3, 3, 2, 2)
        pit(deep, 3, 3, 6, 6)
        B.ticks(70)
        tgt = (ox + 8, oz + 10)         # a hostile target on dry ground
        en = spawn("Villager", tgt, "hostile")
        dry = (ox + 2, oz + 10)
        # ---- aim
        sh = spawn("Colonist", (chest[0] + 1, chest[1] + 1), "player")
        if sh:
            B.call("jawa/pawn_gear", **{"pawn": sh, "action": "equip", "def": "Gun_BoltActionRifle"})
            B.call("jawa/order_pawn", pawnId=sh, x=chest[0] + 1, z=chest[1] + 1, waitTicks=10, draft=True)
        sq = (chest[0] + 1, chest[1] + 1)
        arg = "%d,%d,%d,%d" % (sq[0], sq[1], tgt[0], tgt[1])
        r_on, r_off = on_off("deepWaterAimPenalty", lambda: kv(sc("ProofShot", arg)))
        h_on, h_off = num(r_on, "hit"), num(r_off, "hit")
        ratio = h_on / h_off if h_on is not None and h_off else None
        row("WET_aim_chest_deep_x085", "UNMEASURED" if ratio is None else
            ("PASS" if abs(ratio - 0.85) <= 0.01 and r_on.get("aimFactor") == "0.850" else "FAIL"),
            {"on": r_on, "off": r_off, "ratio": ratio, "wet": sc("ProofWet", "%d,%d" % sq)})
        sd = spawn("Colonist", dry, "player")      # a second shooter on dry ground: its own on/off ratio
        if sd:
            B.call("jawa/pawn_gear", **{"pawn": sd, "action": "equip", "def": "Gun_BoltActionRifle"})
            B.call("jawa/order_pawn", pawnId=sd, x=dry[0], z=dry[1], waitTicks=10, draft=True)
        arg = "%d,%d,%d,%d" % (dry[0], dry[1], tgt[0], tgt[1])
        r_on, r_off = on_off("deepWaterAimPenalty", lambda: kv(sc("ProofShot", arg)))
        h_on, h_off = num(r_on, "hit"), num(r_off, "hit")
        row("WET_aim_dry_unchanged", "UNMEASURED" if h_on is None or not h_off else
            ("PASS" if abs(h_on / h_off - 1.0) <= 1e-3 else "FAIL"), {"on": r_on, "off": r_off})
        # ---- cold
        cp = (waist[0] + 1, waist[1] + 1)
        cc = spawn("Colonist", cp, "player")
        if cc:
            B.call("jawa/order_pawn", pawnId=cc, x=cp[0], z=cp[1], waitTicks=10, draft=True)
        w_on, w_off = on_off("wetFeelsColder", lambda: kv(sc("ProofWet", "%d,%d" % cp)))
        a_, b_ = num(w_on, "comfyMin"), num(w_off, "comfyMin")
        row("WET_cold_comfymin_plus6", "UNMEASURED" if a_ is None or b_ is None else
            ("PASS" if abs((a_ - b_) - 6.0) <= 0.05 and w_on.get("inWater") == "True" else "FAIL"),
            {"on": w_on, "off": w_off, "diff": None if a_ is None or b_ is None else a_ - b_})
        d2 = (dry[0] + 2, dry[1])
        cd = spawn("Colonist", d2, "player")       # a second colonist on dry ground
        if cd:
            B.call("jawa/order_pawn", pawnId=cd, x=d2[0], z=d2[1], waitTicks=10, draft=True)
        w_on, w_off = on_off("wetFeelsColder", lambda: kv(sc("ProofWet", "%d,%d" % d2)))
        a_, b_ = num(w_on, "comfyMin"), num(w_off, "comfyMin")
        row("WET_cold_dry_unchanged", "UNMEASURED" if a_ is None or b_ is None else
            ("PASS" if abs(a_ - b_) <= 0.05 else "FAIL"), {"on": w_on, "off": w_off})
        # ---- swimmers cannot shoot
        sp = (deep[0] + 1, deep[1] + 1)
        sw = spawn("Colonist", sp, "player")
        if sw:
            B.call("jawa/pawn_gear", **{"pawn": sw, "action": "equip", "def": "Gun_BoltActionRifle"})
            B.call("jawa/order_pawn", pawnId=sw, x=sp[0], z=sp[1], waitTicks=10, draft=True)
        arg = "%d,%d,%d,%d" % (sp[0], sp[1], tgt[0], tgt[1])
        s_on, s_off = on_off("swimmersCannotShoot", lambda: kv(sc("ProofShot", arg)))
        if s_off.get("canHit") != "True" or s_on.get("swimming") != "True":
            st = "UNMEASURED"     # control failed: another rule refuses the shot, or the pawn is not swimming
        else:
            st = "PASS" if s_on.get("canHit") == "False" else "FAIL"
        row("WET_swimmer_no_guns", st, {"on": s_on, "off": s_off})
        # ---- downed drowning warning (Q8)
        dp = (waist[0] + 1, waist[1] + 2)
        dn = spawn("Colonist", dp, "player")
        ms0 = B.call("rimworld/list_messages", limit=20) or {}
        seen0 = set(m.get("text") or m.get("label") or "" for m in (ms0.get("messages") or []))
        inc = (B.call("jawa/pawn_force_incapacitate", pawn=dn, action="downed", allowBleedingWounds=False) or {}) if dn else {}
        warned, alive_then, trace = None, None, []
        for k in range(8):
            B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True, timeoutMs=60000)
            ms = B.call("rimworld/list_messages", limit=20) or {}
            texts = [m.get("text") or m.get("label") or "" for m in (ms.get("messages") or [])]
            hit = [t for t in texts if t not in seen0 and "drowning" in t.lower()]
            pr = B.call("jawa/pawn_get", pawn=dn) or {}
            alive = bool(pr.get("pawns")) and not pr["pawns"][0].get("dead")
            trace.append({"t": (k + 1) * 250, "alive": alive, "msgs": hit[:2]})
            if hit and warned is None:
                warned, alive_then = (k + 1) * 250, alive
                break
        row("WET_downed_drowning_warned", "UNMEASURED" if not dn else ("PASS" if warned and alive_then else "FAIL"),
            {"incap": str(inc)[:200], "warnedAtTick": warned, "aliveWhenWarned": alive_then, "trace": trace,
             "wet": sc("ProofWet", "%d,%d" % dp)})
    finally:
        for f, v in before.items():
            if v is not None:
                fset(f, v)
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=True)
        res["settings_restored"] = {f: fget(f) for f in SW_FIELDS}
        save()
        print("result ->", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
