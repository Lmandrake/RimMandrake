"""SHOVELS live check (SHOVELS_BUILD_NO_DIGGING_BARE_HANDED; design design/RimMandrake/shovels_v1_2026-10-25.md section 7).
Owner 2026-10-25: "You can't dig without them. Hands don't work"; Q1 "Siege is mortar-based. Sappers however would bring
shovels & ladders"; Q2 sand/drift shovelling needs a shovel; Q3 every shipped scenario starts with one.

  python.exe src/RimMandrake/FlowWorks/northstar/shovels_live.py [out.json] [--origin X,Z] [--ring X,Z] [--only a,b]

One fresh colonist (Mining 10, Hauling off, every other colonist vanished), shovelRequired on, digLabourMultiplier 1.0
(restored after). "No shovel" = every player inventory cleared of RM_Shovel and every loose RM_Shovel destroyed, read back.
PROVE / EXPECT / LIES per row:
  SH_bare_hands_refused        soil dig order, no shovel: probe hasJobOnCell False + failReason "Needs a shovel"; 6000 ticks
                               -> depth 0, order still there. LIES: a colonist who never works anything -> the control is
                               SH_fetches_shovel_then_digs on the SAME order; no cut there -> UNMEASURED.
  SH_fetches_shovel_then_digs  one RM_Shovel dropped on the plot: probe jobDef TakeInventory; the cut lands (D1) and the
                               census reads has=True (the shovel went to the pack, not the hands).
  SH_shovel_stays_in_inventory 30000 ticks idle after; census has=True. LIES: census on the wrong pawn -> it names the id.
  SH_fill_needs_shovel         D1 pit + fill order + 1 gravel, no shovel: probe refused with the reason, 3000 ticks -> D1;
                               shovel dropped: probe TakeInventory, fill lands (D0).
  SH_setting_off_bare_hands_dig shovelRequired False, no shovel: probe RM_DigCanalJob, cut lands; census needs=False.
  SH_machine_digs_bare         a player Mech_Militor, no shovel: census needs=False, probe RM_DigCanalJob, ordered cut lands.
  SH_sand_shovel_needs_shovel  Pyrelands RM_FE_Ground_Sand + RM_ShovelTerrain order: 2500 ticks bare -> terrain unchanged;
                               shovel in pack -> terrain changes within 4000.
  SH_drift_clear_needs_shovel  Moving Dunes: 0.6 sand on a SnowOrSandClear cell, Cleaning 1: bare 2500 ticks -> depth kept (>= 80 pct: the dunes drift ~0.01 on their own);
                               shovel in pack -> cleared (< 0.05) within 4000.
  SH_pyrelands_underwall       RM_TerrainDigProof.ProofShovelUnderWall: hasJobBeforeWall True, hasJobUnderWall False.
  SH_raider_without_shovel_does_not_fill / SH_raider_with_shovel_fills
                               D8 moat ring round the colonist, 4 Mercenary_Slasher assault 30 east, no loose shovel:
                               ProofDecision never a fill job; each given a shovel: at least one decides a fill job.
                               LIES: a with-shovel side that never picks fill leaves the without-shovel side UNMEASURED.
  SH_raid_brings_shovels       fire_raid ImmediateAttack (moat >= 20 climb cells): census hostiles 1 <= holders < raiders.
  SH_sapper_brings_shovels_and_ladders  ImmediateAttackSappers: holders >= 1 and ladder carriers >= 1.
  SH_siege_brings_none         Siege: raiders >= 2, holders == 0 (the control is the raid row reading holders >= 1).
  SH_scenario_starts_with_shovel  RUT_Jawa_UtinniStart: on the minimal list UtinniPatches is not loaded, so the DEPLOYED
                               Scenario_Utinni.xml is parsed (one ScenPart_StartingThing_Defined RM_Shovel/Steel x1) and an
                               RM_Shovel/Steel is spawned (the def+stuff resolve); a loaded scenario reads the census instead.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import shovel_stage  # noqa: E402
import work_bar  # noqa: E402

NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_RT = "RimMandrake.FlowWorks.RM_RaiderTrenchSettings"
S_PY = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
SH = "RimMandrake.FlowWorks.RM_Shovels"
RT = "RimMandrake.FlowWorks.RM_RaiderTrench"
LP = "RimMandrake.FlowWorks.RM_LadderParity"
SHOVEL = "RM_Shovel"
ITEM = "SHOVELS_BUILD_NO_DIGGING_BARE_HANDED"
NEED_WORDS = "Needs a shovel"
FILL_JOBS = ("RM_RaiderFillTrench", "RM_RaiderFetchFill")
SCEN_DEF = "RUT_Jawa_UtinniStart"
SCEN_XML = r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\UtinniPatches\Defs\ScenarioDefs\Scenario_Utinni.xml"
ROWS = ("SH_bare_hands_refused", "SH_fetches_shovel_then_digs", "SH_shovel_stays_in_inventory", "SH_fill_needs_shovel",
        "SH_setting_off_bare_hands_dig", "SH_machine_digs_bare", "SH_sand_shovel_needs_shovel",
        "SH_drift_clear_needs_shovel", "SH_pyrelands_underwall", "SH_raider_without_shovel_does_not_fill",
        "SH_raider_with_shovel_fills", "SH_raid_brings_shovels", "SH_sapper_brings_shovels_and_ladders",
        "SH_siege_brings_none", "SH_scenario_starts_with_shovel")
RUN_SETTINGS = {"shovelRequired": True, "digLabourMultiplier": 1.0, "digFindsEnabled": False, "digDeepStoneEnabled": False,
                "digCostRisesWithDepth": False, "fillCostsSpoilEnabled": True}


def kv(text):
    """'a=1 b=True c=x' -> dict (the census/parity text)."""
    return dict(t.split("=", 1) for t in str(text or "").split() if "=" in t)


def truthy(v):
    return str(v).lower() == "true"


def scenario_xml_shovels(path):
    """[(stuff, count)] for each ScenPart_StartingThing_Defined making RM_Shovel in the deployed scenario file."""
    import xml.etree.ElementTree as ET
    out = []
    root = ET.parse(path).getroot()
    for sd in root.iter("ScenarioDef"):
        if (sd.findtext("defName") or "").strip() != SCEN_DEF:
            continue
        for li in sd.iter("li"):
            if li.get("Class") == "ScenPart_StartingThing_Defined" and (li.findtext("thingDef") or "").strip() == SHOVEL:
                out.append(((li.findtext("stuff") or "").strip(), int((li.findtext("count") or "1").strip())))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--ring", default="", help="moat centre x,z (default origin + 40,0)")
    ap.add_argument("--only", default="")
    ap.add_argument("--stay-ticks", type=int, default=30000)
    ap.add_argument("--points", type=float, default=1500)
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "shovels_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    t_start = time.time()
    res = {"script": "shovels_live.py", "item": ITEM, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows,
           "args": vars(a), "mode": "partial" if a.only else "live", "notes": {}}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        det = dict(det, wall_s=round(time.time() - t_start))
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-40s %-10s %-7s %s" % (rid, st, cls, json.dumps(det, default=str)[:500]), flush=True)
        save()

    only = {r.strip() for r in a.only.split(",") if r.strip()}
    if only - set(ROWS):
        print("unknown row ids: %s" % sorted(only - set(ROWS)), flush=True)
        return 2

    def want(*rids):
        return not only or bool(only & set(rids))

    def unmeasured_rest(cls, why):
        done = {r["id"] for r in rows}
        for rid in ROWS:
            if rid not in done and want(rid):
                row(rid, "UNMEASURED", cls, {"why": why})

    def step(n):
        left = n
        while left > 0:
            k = min(left, 2500)
            B.call("rimworld/step_game_ticks", ticks=k, pauseFirst=True, timeoutMs=max(60000, k * 40))
            left -= k

    def sget(t, f):
        return (B.call("jawa/mod_settings_field", typeName=t, action="get", field=f) or {}).get("value")

    def sset(t, f, v):
        return B.call("jawa/mod_settings_field", typeName=t, action="set", field=f, value=str(v)) or {}

    def scall(t, m, args=""):
        r = B.call("jawa/static_call", type=t, method=m, args=args, _answer=True) or {}
        return str(r.get("result") if r.get("success") is not False else "REFUSED " + str(r.get("message") or r)[:200])

    def census(pid):
        return kv(scall(SH, "ProofShovelCensus", "pawn:" + str(pid).replace("Thing_", "")))

    def depth(c):
        return (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("depth")

    def probe(c, kind, pid):
        return B.call("jawa/flowworks_job_probe", x=c[0], z=c[1], kind=kind, pawnId=pid) or {}

    def wg(p):
        return (p or {}).get("workGiver") or {}

    def wait_depth(c, d0, limit):
        t = 0
        while t < limit:
            step(250)
            t += 250
            d = depth(c)
            if d not in (None, d0):
                return t, d
        return None, depth(c)

    def loose_shovels():
        r = B.call("jawa/list_things", defName=SHOVEL, limit=200) or {}
        if r.get("success") is False or not isinstance(r.get("things"), list):
            return None
        return r["things"]

    def clear_shovels():
        """-> None when the map and every player pack read back shovel-free, else the reason (HARNESS)."""
        players = [p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []
                   if p.get("isPlayer") and not p.get("dead")]
        for p in players:
            B.call("jawa/pawn_gear", pawn=p.get("id"), action="clear", clearWhat="inventory")
        for t in loose_shovels() or []:
            B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t.get("x"), t.get("z")), categories="Item")
        left = loose_shovels()
        if left is None:
            return "list_things RM_Shovel failed"
        if left:
            return "loose shovels remain: %s" % [(t.get("x"), t.get("z")) for t in left][:5]
        held = [p.get("id") for p in players if truthy(census(p.get("id")).get("has"))]
        return ("still holding a shovel: %s" % held) if held else None

    def clear_orders():
        """Earlier rows' dig/fill orders outlive their D1 cut (a dig order deepens on), and outrank the next row's work."""
        for des in ("RM_DigCanal", "RM_FillInCanal", "RM_ShovelTerrain"):
            B.call("jawa/designate_batch", action="remove", designation=des, rect="%d,%d,%d,%d" % plot)

    def drop_shovel(c, stuff="WoodLog"):
        B.call("jawa/spawn_batch", ops="%s:%d,%d,1" % (SHOVEL, c[0], c[1]), stuff=stuff)
        return [t for t in loose_shovels() or [] if (t.get("x"), t.get("z")) == tuple(c)]

    def designate(des, c):
        return B.call("jawa/designate_batch", action="add", designation=des, rect="%d,%d,1,1" % tuple(c)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    ring_c = tuple(int(v) for v in a.ring.split(",")) if a.ring else (ox + 40, oz + 8)
    plot = (ox, oz, 20, 20)
    dig_a, fill_c, dig_off, dig_m = (ox + 4, oz + 12), (ox + 10, oz + 12), (ox + 4, oz + 6), (ox + 14, oz + 6)
    fill_mat, shovel_at, sand_c, drift_c = (ox + 12, oz + 12), (ox + 8, oz + 4), (ox + 4, oz + 16), (ox + 12, oz + 16)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        unmeasured_rest("HARNESS", "no game in Playing")
        return 2
    prof = (B.call("jawa/companion_handshake") or {}).get("effectiveProfile")
    if prof != "test":
        unmeasured_rest("HARNESS", "companion profile is %r, not 'test'" % prof)
        return 2
    res["site_calm"] = V.site_calm(B)
    before = {k: sget(S_FW, k) for k in RUN_SETTINGS}
    res["settings_before"] = before
    if any(v is None for v in before.values()):
        unmeasured_rest("HARNESS", "a FlowWorks setting is unreadable (deployed DLL without shovels?): %s" % before)
        return 2
    try:
        for k, v in RUN_SETTINGS.items():
            sset(S_FW, k, v)
        res["settings_run"] = {k: sget(S_FW, k) for k in RUN_SETTINGS}
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % plot)
        for des in ("RM_DigCanal", "RM_FillInCanal", "Mine", "RM_ShovelTerrain"):
            B.call("jawa/designate_batch", action="remove", designation=des, rect="%d,%d,%d,%d" % plot)
        site_rows = []
        V.prepare_site(B, plot, site_rows, "shovel_site")
        if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
            unmeasured_rest("SITE", "site not prepared: %s" % str(site_rows[:2])[:200])
            return 2
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if not p.get("dead") and p.get("isPlayer"):
                B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
        pid, rolls = None, []
        for _ in range(6):
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 8, z=oz + 9, faction="player", count=1) or {}
            got = [p.get("id") for p in r.get("pawns") or [] if p.get("id")]
            if not got:
                break
            step(5)
            st = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}.get(got[0]) or {}
            nomine = (probe(dig_a, "dig", got[0]).get("pawn") or {}).get("workTypeDisabled") is True
            # HARNESS (live 2026-10-25): SH_drift_clear_needs_shovel bars Cleaning 1 later; a roll incapable of Cleaning
            # refuses that write (the row read UNMEASURED after 464 s), so the roll proves Cleaning can be set (the bar
            # below puts it back to 0)
            noclean = not work_bar.set_priority(B.call, got[0], "Cleaning", 1)[0]
            rolls.append({"id": got[0], "downed": st.get("downed"), "miningDisabled": nomine, "cleaningDisabled": noclean})
            if st and not st.get("downed") and not st.get("dead") and not nomine and not noclean:
                pid = got[0]
                break
            B.call("jawa/pawn_force_incapacitate", pawn=got[0], action="vanish", _answer=True)
        res["colonist_rolls"] = rolls
        if not pid:
            unmeasured_rest("HARNESS", "no usable colonist spawned")
            return 2
        B.call("jawa/set_pawn_skill", pawn=pid, skill="Mining", level=10, _answer=True)
        bar_ok, bar_why = work_bar.set_all(B.call, pid, [("Mining", 1), ("Hauling", 0), ("Cleaning", 0)])
        if not bar_ok:
            unmeasured_rest("HARNESS", "work bar did not take: %s" % bar_why)
            return 2

        # 1+2. bare hands refused; the same order with a shovel on the ground is fetched then cut (the control)
        if want("SH_bare_hands_refused", "SH_fetches_shovel_then_digs"):
            why = clear_shovels()
            B.call("jawa/set_terrain", terrainDef="Soil", x=dig_a[0], z=dig_a[1])
            d0 = depth(dig_a)
            designate("RM_DigCanal", dig_a)
            step(2)
            p0 = probe(dig_a, "dig", pid)
            step(6000)
            d1, p1 = depth(dig_a), probe(dig_a, "dig", pid)
            det1 = {"pawn": pid, "depth0": d0, "depth6000": d1, "probe": wg(p0), "designationAfter": p1.get("designationPresent"),
                    "census": census(pid)}
            drop = drop_shovel(shovel_at)
            step(2)
            pf = probe(dig_a, "dig", pid)
            t2, d2 = wait_depth(dig_a, d1, 8000)
            cen = census(pid)
            det2 = {"pawn": pid, "dropped": bool(drop), "probe": wg(pf), "cutAfterTicks": t2, "depth": d2, "census": cen,
                    "looseLeft": len(loose_shovels() or [])}
            if why or d0 != 0 or not drop:
                for rid in ("SH_bare_hands_refused", "SH_fetches_shovel_then_digs"):
                    row(rid, "UNMEASURED", "HARNESS", dict(det1, why=why or "not D0 or shovel did not spawn"))
            else:
                fetch_ok = wg(pf).get("jobDef") == "TakeInventory" and d2 == 1 and truthy(cen.get("has"))
                row("SH_fetches_shovel_then_digs", "PASS" if fetch_ok else "FAIL", "MOD", det2)
                bare_ok = (wg(p0).get("hasJobOnCell") is False and NEED_WORDS in str(wg(p0).get("failReason"))
                           and d1 == 0 and p1.get("designationPresent") is True)
                if d2 != 1:
                    row("SH_bare_hands_refused", "UNMEASURED", "SITE", dict(det1, why="the shovel control never cut"))
                else:
                    row("SH_bare_hands_refused", "PASS" if bare_ok else "FAIL", "MOD", det1)

        # 3. the shovel stays in the pack
        if want("SH_shovel_stays_in_inventory"):
            pre = census(pid)
            if not truthy(pre.get("has")):
                clear_shovels()
                shovel_stage.give_shovel(B.call, pid)
                pre = census(pid)
            if not truthy(pre.get("has")):
                row("SH_shovel_stays_in_inventory", "UNMEASURED", "HARNESS", {"why": "no shovel to start with", "census": pre})
            else:
                t0 = time.time()
                step(a.stay_ticks)
                post = census(pid)
                row("SH_shovel_stays_in_inventory", "PASS" if truthy(post.get("has")) else "FAIL", "MOD",
                    {"pawn": pid, "ticks": a.stay_ticks, "stepWall_s": round(time.time() - t0), "before": pre, "after": post,
                     "loose": [(t.get("x"), t.get("z")) for t in loose_shovels() or []]})

        # 4. fill needs a shovel too
        if want("SH_fill_needs_shovel"):
            why = clear_shovels()
            B.call("jawa/set_terrain", terrainDef="Soil", x=fill_c[0], z=fill_c[1])
            B.call("jawa/flowworks_excavation_drive", x=fill_c[0], z=fill_c[1], deepenLevels=1, setFill=-1)
            d0 = depth(fill_c)
            designate("RM_FillInCanal", fill_c)
            B.call("jawa/spawn_batch", ops="RM_Gravel:%d,%d,1" % fill_mat)
            step(2)
            p0 = probe(fill_c, "fillin", pid)
            step(3000)
            d1 = depth(fill_c)
            drop = drop_shovel(shovel_at)
            step(2)
            pf = probe(fill_c, "fillin", pid)
            t2, d2 = wait_depth(fill_c, d1, 8000)
            det = {"depth0": d0, "depth3000": d1, "bareProbe": wg(p0), "shovelProbe": wg(pf), "fillAfterTicks": t2, "depth": d2,
                   "census": census(pid)}
            if why or d0 != 1 or not drop:
                row("SH_fill_needs_shovel", "UNMEASURED", "HARNESS", dict(det, why=why or "no D1 pit or no shovel spawned"))
            elif d2 != 0:
                row("SH_fill_needs_shovel", "UNMEASURED" if d1 == 1 and wg(p0).get("hasJobOnCell") is False else "FAIL",
                    "SITE" if d1 == 1 else "MOD", dict(det, why="the with-shovel fill never landed"))
            else:
                ok_ = (wg(p0).get("hasJobOnCell") is False and NEED_WORDS in str(wg(p0).get("failReason")) and d1 == 1
                       and wg(pf).get("jobDef") == "TakeInventory")
                row("SH_fill_needs_shovel", "PASS" if ok_ else "FAIL", "MOD", det)

        # 5. setting off: bare hands dig
        if want("SH_setting_off_bare_hands_dig"):
            why = clear_shovels()
            sset(S_FW, "shovelRequired", False)
            try:
                got = sget(S_FW, "shovelRequired")
                B.call("jawa/set_terrain", terrainDef="Soil", x=dig_off[0], z=dig_off[1])
                d0 = depth(dig_off)
                designate("RM_DigCanal", dig_off)
                step(2)
                p0 = probe(dig_off, "dig", pid)
                cen = census(pid)
                t, d1 = wait_depth(dig_off, d0, 6000)
            finally:
                sset(S_FW, "shovelRequired", True)
            det = {"setting": got, "depth0": d0, "probe": wg(p0), "census": cen, "cutAfterTicks": t, "depth": d1}
            if why or str(got).lower() != "false" or d0 != 0:
                row("SH_setting_off_bare_hands_dig", "UNMEASURED", "HARNESS", dict(det, why=why or "setting/site did not take"))
            else:
                ok_ = d1 == 1 and wg(p0).get("jobDef") == "RM_DigCanalJob" and cen.get("needs") == "False"
                row("SH_setting_off_bare_hands_dig", "PASS" if ok_ else "FAIL", "MOD", det)

        # 6. a machine digs bare-handed
        if want("SH_machine_digs_bare"):
            why = clear_shovels()
            r = B.call("jawa/spawn_pawn", kindDef="Mech_Militor", x=dig_m[0] + 2, z=dig_m[1], faction="player", count=1) or {}
            mid = ((r.get("pawns") or [{}])[0]).get("id")
            if not mid:
                row("SH_machine_digs_bare", "UNMEASURED", "SITE", {"why": "no mech spawned", "reply": str(r)[:200]})
            else:
                B.call("jawa/set_terrain", terrainDef="Soil", x=dig_m[0], z=dig_m[1])
                d0 = depth(dig_m)
                designate("RM_DigCanal", dig_m)
                step(2)
                p0 = probe(dig_m, "dig", mid)
                cen = census(mid)
                od = B.call("jawa/ordered_job", pawnId=mid, jobDef="RM_DigCanalJob", targetAX=dig_m[0], targetAZ=dig_m[1],
                            waitTicks=0) or {}
                t, d1 = wait_depth(dig_m, d0, 6000)
                det = {"mech": mid, "depth0": d0, "probe": wg(p0), "census": cen, "order": str(od)[:200], "cutAfterTicks": t,
                       "depth": d1}
                if why or d0 != 0:
                    row("SH_machine_digs_bare", "UNMEASURED", "HARNESS", dict(det, why=why or "not D0"))
                elif d1 != 1 and wg(p0).get("jobDef") == "RM_DigCanalJob" and cen.get("needs") == "False":
                    row("SH_machine_digs_bare", "UNMEASURED", "SITE", dict(det, why="offered the job bare, but no cut landed"))
                else:
                    ok_ = d1 == 1 and wg(p0).get("jobDef") == "RM_DigCanalJob" and cen.get("needs") == "False"
                    row("SH_machine_digs_bare", "PASS" if ok_ else "FAIL", "MOD", det)
                B.call("jawa/pawn_force_incapacitate", pawn=mid, action="vanish", _answer=True)

        # 7. Pyrelands sand shovelling
        if want("SH_sand_shovel_needs_shovel"):
            clear_orders()
            why = clear_shovels()
            en = sget(S_PY, "sandShovelEnabled")
            B.call("jawa/set_terrain", terrainDef="RM_FE_Ground_Sand", x=sand_c[0], z=sand_c[1])
            t0 = probe(sand_c, "dig", pid).get("terrain")
            ds = designate("RM_ShovelTerrain", sand_c)
            step(2500)
            t1 = probe(sand_c, "dig", pid).get("terrain")
            gv = shovel_stage.give_shovel(B.call, pid)
            t, t2 = None, t1
            for i in range(16):
                step(250)
                t2 = probe(sand_c, "dig", pid).get("terrain")
                if t2 != t1:
                    t = (i + 1) * 250
                    break
            det = {"enabled": en, "terrain0": t0, "terrainBare2500": t1, "designate": str(ds)[:160], "shovel": gv,
                   "changedAfterTicks": t, "terrainAfter": t2}
            if why or str(en).lower() != "true" or t0 != "RM_FE_Ground_Sand" or not gv[0]:
                row("SH_sand_shovel_needs_shovel", "UNMEASURED", "HARNESS", dict(det, why=why or "setting/terrain/shovel"))
            elif t is None:
                row("SH_sand_shovel_needs_shovel", "UNMEASURED" if t1 == t0 else "FAIL", "SITE" if t1 == t0 else "MOD",
                    dict(det, why="the with-shovel control never dug"))
            else:
                row("SH_sand_shovel_needs_shovel", "PASS" if t1 == t0 else "FAIL", "MOD", det)

        # 8. Moving Dunes drift clear
        if want("SH_drift_clear_needs_shovel"):
            clear_orders()
            why = clear_shovels()
            bar_ok, bar_why = work_bar.set_all(B.call, pid, [("Mining", 0), ("Cleaning", 1)])
            if not bar_ok:
                why = why or "work bar did not take: %s" % bar_why
            rect = "%d,%d,1,1" % drift_c

            def sand_at():
                c = ((B.call("jawa/set_weather_buildup", kind="sand", mode="add", rect=rect, depth=0.0, readBack=1) or {})
                     .get("cells") or [{}])[0]
                return c.get("sand")
            try:
                B.call("jawa/set_weather_buildup", kind="sand", mode="set", rect=rect, depth=0.6)
                B.call("jawa/paint_area", area="snow", ops=rect, value=True)
                s0 = sand_at()
                step(2500)
                s1 = sand_at()
                gv = shovel_stage.give_shovel(B.call, pid)
                t, s2 = None, s1
                for i in range(16):
                    step(250)
                    s2 = sand_at()
                    if s2 is not None and s2 < 0.05:
                        t = (i + 1) * 250
                        break
            finally:
                work_bar.set_all(B.call, pid, [("Cleaning", 0), ("Mining", 1)])
                B.call("jawa/paint_area", area="snow", ops=rect, value=False)
            det = {"sand0": s0, "sandBare2500": s1, "shovel": gv, "clearedAfterTicks": t, "sandAfter": s2}
            if why or s0 is None or s0 < 0.5 or not gv[0]:
                row("SH_drift_clear_needs_shovel", "UNMEASURED", "HARNESS", dict(det, why=why or "sand did not take / no shovel"))
            elif t is None:
                kept = s1 is not None and s1 >= s0 * 0.8
                row("SH_drift_clear_needs_shovel", "UNMEASURED" if kept else "FAIL", "SITE" if kept else "MOD",
                    dict(det, why="the with-shovel control never cleared"))
            else:
                row("SH_drift_clear_needs_shovel", "PASS" if s1 is not None and s1 >= s0 * 0.8 else "FAIL", "MOD", det)

        # 9. Pyrelands under-wall proof re-run (it lends its colonist a shovel when needed)
        if want("SH_pyrelands_underwall"):
            txt = scall("RimMandrake.Pyrelands.RM_TerrainDigProof", "ProofShovelUnderWall")
            m = re.search(r"hasJobBeforeWall (\w+) \| hasJobUnderWall (\w+)", txt)
            if not m:
                row("SH_pyrelands_underwall", "UNMEASURED", "HARNESS", {"result": txt})
            else:
                row("SH_pyrelands_underwall", "PASS" if (m.group(1), m.group(2)) == ("True", "False") else "FAIL", "MOD",
                    {"result": txt})

        # 10. raider fill, with and without a shovel, at a D8 moat round the colonist
        raid_rows = ("SH_raider_without_shovel_does_not_fill", "SH_raider_with_shovel_fills", "SH_raid_brings_shovels",
                     "SH_sapper_brings_shovels_and_ladders", "SH_siege_brings_none")
        if want(*raid_rows):
            cx, cz = ring_c
            rrect = (cx - 8, cz - 8, 17, 17)
            B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rrect)
            srows = []
            V.prepare_site(B, rrect, srows, "moat_site")
            bad = [r for r in srows if r.get("status") not in (None, "PASS")]
            ring = [(x, z) for x in range(cx - 6, cx + 7) for z in range(cz - 6, cz + 7) if max(abs(x - cx), abs(z - cz)) >= 5]
            short = 0
            for c in ring:
                d = (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=8, setFill=-1) or {}).get("depth")
                short += 0 if isinstance(d, int) and d >= 8 else 1
            # the island colonist is spawned on the centre (no teleport tool); the plot colonist is vanished so the raid
            # has one target, behind the moat
            isl = B.call("jawa/spawn_pawn", kindDef="Colonist", x=cx, z=cz, faction="player", count=1) or {}
            iid = ((isl.get("pawns") or [{}])[0]).get("id")
            if iid:
                B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
                pid = iid
            step(5)
            res["moat"] = {"centre": ring_c, "ringCells": len(ring), "short": short, "site": str(bad)[:200],
                           "colonistAt": [(p.get("x"), p.get("z")) for p in (B.call("jawa/list_pawns", limit=400) or {})
                                          .get("pawns") or [] if p.get("id") == pid]}
            probe_f = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=cx + 30, z=cz, faction="?", count=1) or {}
            avail = (probe_f.get("details") or {}).get("available") or []
            fac = next((f["def"] for f in avail if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
            res["moat"]["faction"] = fac
            if bad or short > 4 or not fac:
                for rid in raid_rows:
                    if want(rid):
                        row(rid, "UNMEASURED", "SITE", {"why": "moat site not ready or no Pirate faction", "moat": res["moat"]})
            else:
                if want("SH_raider_without_shovel_does_not_fill", "SH_raider_with_shovel_fills"):
                    clear_shovels()
                    ids = []
                    for k in range(4):
                        sp = B.call("jawa/spawn_pawn", kindDef="Mercenary_Slasher", x=cx + 30, z=cz - 2 + k, faction=fac,
                                    count=1) or {}
                        ids += [str(p.get("id")) for p in sp.get("pawns") or [] if p.get("id")]
                    for i in ids:
                        B.call("jawa/pawn_gear", pawn=i, action="clear", clearWhat="inventory")
                    B.call("jawa/lord_assault_spawn", pawns=",".join(ids))
                    step(2)
                    dec0 = {i: scall(RT, "ProofDecision", i) for i in ids}
                    cen0 = {i: census(i).get("has") for i in ids}
                    gave = [shovel_stage.give_shovel(B.call, i, stuff="Steel")[0] for i in ids]
                    step(1)
                    dec1 = {i: scall(RT, "ProofDecision", i) for i in ids}
                    B.call("jawa/kill_hostiles", factionDef=fac)
                    step(2)
                    fills0 = [i for i, d in dec0.items() if d.split(" ")[0] in FILL_JOBS]
                    fills1 = [i for i, d in dec1.items() if d.split(" ")[0] in FILL_JOBS]
                    det = {"raiders": ids, "holdersBefore": cen0, "decisionsBare": dec0, "gave": gave, "decisionsShovel": dec1}
                    if len(ids) < 2 or any(truthy(v) for v in cen0.values()):
                        for rid in ("SH_raider_without_shovel_does_not_fill", "SH_raider_with_shovel_fills"):
                            row(rid, "UNMEASURED", "HARNESS", dict(det, why="raiders missing or arrived with shovels"))
                    else:
                        row("SH_raider_with_shovel_fills", "PASS" if fills1 else "FAIL", "MOD", det)
                        if not fills1:
                            row("SH_raider_without_shovel_does_not_fill", "UNMEASURED", "SITE",
                                dict(det, why="no raider chose fill even with a shovel: the bare side proves nothing"))
                        else:
                            row("SH_raider_without_shovel_does_not_fill", "PASS" if not fills0 else "FAIL", "MOD", det)

                def raid(strategy):
                    B.call("jawa/kill_hostiles")
                    clear_shovels()
                    par0 = scall(LP, "ProofLadderParity", "carriers")
                    fr = B.call("jawa/fire_raid", dryRun=False, points=a.points, faction=fac, strategy=strategy,
                                arrivalMode="EdgeWalkIn") or {}
                    cen = kv(scall(SH, "ProofShovelCensus", "hostiles"))
                    par = kv(scall(LP, "ProofLadderParity", "carriers"))
                    B.call("jawa/kill_hostiles", factionDef=fac)
                    step(2)
                    return {"fire": {k: fr.get(k) for k in ("success", "blockedByDialog", "message", "strategy", "points")},
                            "arrived": len(fr.get("arrived") or []), "census": cen, "ladders": par, "laddersBefore": par0}

                share = {k: sget(S_RT, k) for k in ("raiderShovelShare", "sapperShovelShare")}
                if want("SH_raid_brings_shovels"):
                    d = dict(raid("ImmediateAttack"), shares=share)
                    n, h = int(d["census"].get("raiders") or 0), int(d["census"].get("holders") or 0)
                    if n < 4:
                        row("SH_raid_brings_shovels", "UNMEASURED", "SITE", dict(d, why="fewer than 4 raiders"))
                    else:
                        row("SH_raid_brings_shovels", "PASS" if 1 <= h < n else "FAIL", "MOD", d)
                if want("SH_sapper_brings_shovels_and_ladders"):
                    d = dict(raid("ImmediateAttackSappers"), shares=share)
                    n, h = int(d["census"].get("raiders") or 0), int(d["census"].get("holders") or 0)
                    c_ = int(d["ladders"].get("carriers") or 0)
                    if n < 2:
                        row("SH_sapper_brings_shovels_and_ladders", "UNMEASURED", "SITE", dict(d, why="fewer than 2 raiders"))
                    else:
                        row("SH_sapper_brings_shovels_and_ladders", "PASS" if h >= 1 and c_ >= 1 else "FAIL", "MOD", d)
                if want("SH_siege_brings_none"):
                    d = raid("Siege")
                    n, h = int(d["census"].get("raiders") or 0), int(d["census"].get("holders") or 0)
                    if n < 2:
                        row("SH_siege_brings_none", "UNMEASURED", "SITE", dict(d, why="fewer than 2 siege raiders"))
                    else:
                        row("SH_siege_brings_none", "PASS" if h == 0 else "FAIL", "MOD", d)

        # 11. the scenario's one shovel
        if want("SH_scenario_starts_with_shovel"):
            live = scall(SH, "ProofShovelCensus", "scenario:" + SCEN_DEF)
            det = {"census": live, "method": "census (scenario loaded)"}
            if live.startswith("shovels="):
                ok_ = live.startswith("shovels=1 ") and "RM_Shovel/Steel x1" in live
                row("SH_scenario_starts_with_shovel", "PASS" if ok_ else "FAIL", "MOD", det)
            else:
                det["method"] = "deployed def parsed + RM_Shovel/Steel spawned (UtinniPatches not on this list)"
                try:
                    parts = scenario_xml_shovels(SCEN_XML)
                except (OSError, ValueError) as ex:
                    parts = "unreadable: %s" % ex
                spot = (ox + 16, oz + 2)
                sp = drop_shovel(spot, stuff="Steel")
                det.update(xmlParts=parts, spawned=[(t.get("def"), t.get("stuff")) for t in sp])
                for t in sp:
                    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % spot, categories="Item")
                if not isinstance(parts, list):
                    row("SH_scenario_starts_with_shovel", "UNMEASURED", "HARNESS", det)
                else:
                    row("SH_scenario_starts_with_shovel", "PASS" if parts == [("Steel", 1)] and sp else "FAIL", "MOD", det)
        return 0 if all(r["status"] == "PASS" for r in rows) else 1
    finally:
        for k, v in before.items():
            if v is not None:
                try:
                    sset(S_FW, k, v)
                except Exception as ex:  # noqa: BLE001
                    print("RESTORE %s failed: %s" % (k, ex), flush=True)
        res["settings_restored"] = {k: sget(S_FW, k) for k in before}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result: %s" % out, flush=True)


if __name__ == "__main__":
    sys.exit(main())
