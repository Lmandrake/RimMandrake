"""BROADEN experiments for PIT_TEMPERATURE_SOFTENING_1 (GPT scenarios 1 and 4).
E1 stacking: six prisoners in one open 4 m pit; the Charity colonist's RM_ExposedPrisoner count and mood total after
   1 h; then the prisoners leave (vanish) and the memory count after 12 h and after 26 h.
E4 coupling: one 5x5 pit with ONE roof hole (4 % open: below vanilla's 25 % outdoor rule, so the FlowWorks postfix is
   the only extra coupling). The clock jumps from night to a hot noon; the pit's approach rate to outdoors
   k = dT/dt / (Tout - T) is measured over 250-tick steps with pitTemperatureCoupling 1, then 3, then 1."""
import sys, os, json, time
sys.path.insert(0, sys.argv[1])
import proof_hose as PH
import pit_exposure_live as L
B = PH.PB(); V = PH.V
NSP = L.NSP
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
out = sys.argv[2]
res = {}
def save():
    json.dump(res, open(out, "w"), indent=1, default=str)
def step(n):
    B.call("rimworld/step_game_ticks", ticks=int(n), pauseFirst=True, timeoutMs=240000)
def sset(f, v):
    return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v)) or {}
V._wait_playing(B, leave_s=0)
V.site_calm(B)
B.call("jawa/weather_set", weather="Clear", lockWeather=True)
mi = B.call("jawa/map_info") or {}
tile, lon = mi.get("tile"), L.fnum(mi.get("longitude"), 0.0)
B.call("jawa/world_tile_set", tiles=str(tile), biome="Desert", temperature=28.0)
B.call("jawa/world_tile_cache_reset", tiles=str(tile))
clk = B.call("jawa/time_clock") or {}
sa = int(clk["ticksAbs"]) - int(clk["ticksGame"])
B.call("jawa/time_set_ticks", ticks=L.tick_for(22, 4.0, lon) - sa, timeException=True, why="broaden experiments")
step(1)
for wt in ("Dialog_NamePlayerFactionAndSettlement",):
    B.call("rimworld/close_window", windowType=wt)
cols = (B.call("rimworld/list_colonists") or {}).get("colonists") or []
cids = []
for c in cols:
    cid = c["pawnId"].replace("Thing_", "")
    pg = ((B.call("jawa/pawn_get", pawn=cid) or {}).get("pawns") or [{}])[0]
    if pg.get("developmentalStage") == "Adult" and pg.get("ideo"):
        cids.append((cid, pg))
kind, pg = cids[0]
pos = pg["position"]
ox, oz = pos["x"] - 14, pos["z"] + 6
rect = (ox - 1, oz - 1, 18, 9)
B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
V.prepare_site(B, rect, [], "broaden")
B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % rect)
pitE1 = [(ox + x, oz + z) for x in range(1, 6) for z in range(1, 6)]
pitE4 = [(ox + x, oz + z) for x in range(9, 14) for z in range(1, 6)]
for c in pitE1 + pitE4:
    B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=8, setFill=-1)
# E4 roof: all but the centre cell
B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,5,5" % (ox + 9, oz + 1))
B.call("jawa/set_roof_batch", ops="None:%d,%d,1,1" % (ox + 11, oz + 3))
# the kind colonist's ideo must mind beggars
ideo = pg["ideo"]
io = (B.call("jawa/ideo_of", ideo=ideo, precepts=True) or {}).get("ideos") or []
ch = [p["defName"] for i in io if i.get("name") == ideo for p in i.get("precepts") or [] if p["defName"].startswith("Charity_")]
if not ch:
    for i in (B.call("jawa/ideo_of", precepts=True) or {}).get("ideos") or []:
        if any(p["defName"].startswith("Charity_") for p in i.get("precepts") or []):
            B.call("jawa/set_pawn_ideo", pawn=kind, action="set", ideo=i["name"]); ideo = i["name"]; break
res["kind"] = {"pawn": kind, "ideo": ideo}
B.call("jawa/pawn_refresh_needs", pawn=kind)
# E1: six prisoners
pris = []
for k in range(6):
    c = pitE1[k * 4 % 25]
    r = B.call("jawa/spawn_pawn", kindDef="Villager", x=c[0], z=c[1], faction="hostile", count=1) or {}
    pid = r["pawns"][0]["id"]
    B.call("jawa/pawn_set_guest_status", pawn=pid, guestStatus="Prisoner", hostFaction="PlayerColony")
    pris.append(pid)
res["prisoners"] = pris
def mem():
    th = (B.call("jawa/pawn_thoughts", pawn=kind) or {})
    rows = [t for t in th.get("thoughts") or [] if t["def"] == "RM_ExposedPrisoner"]
    return {"count": len(rows), "offsets": [t["moodOffset"] for t in rows], "total": th.get("totalMoodOffset")}
step(2500)
res["E1_after_1h"] = mem(); print("E1 1h", res["E1_after_1h"], flush=True); save()
# E4 coupling while E1 runs on: settle the pit, then measure k at 1, 3, 1
cell = (ox + 10, oz + 2)
def tk():
    r = B.call("jawa/cell_temperature", cell="%d,%d" % cell) or {}
    return L.fnum(r.get("temperature")), L.fnum(r.get("outdoorTemp"))
res["E4_room"] = str((B.call("jawa/static_call", type=NSP, method="ProofRoom", args="%d,%d;%d,%d" % (cell + (ox + 10, oz + 7)), _answer=True) or {}).get("result"))
ks = {}
for coup in (1.0, 3.0, 1.0, 3.0):
    sset("pitTemperatureCoupling", coup)
    seg = []
    for i in range(6):
        t0, o0 = tk(); step(250); t1, o1 = tk()
        if t0 is not None and o0 is not None and abs(o0 - t0) > 0.5:
            seg.append(round((t1 - t0) / (o0 - t0), 4))
    ks.setdefault(str(coup), []).append(seg)
    print("E4 coupling", coup, seg, tk(), flush=True)
sset("pitTemperatureCoupling", 3.0)
res["E4_k"] = ks; save()
# E1 expiry: prisoners leave
for pid in pris:
    B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
step(12 * 2500)
res["E1_after_leave_12h"] = mem(); print("E1 +12h", res["E1_after_leave_12h"], flush=True); save()
step(14 * 2500)
res["E1_after_leave_26h"] = mem(); print("E1 +26h", res["E1_after_leave_26h"], flush=True); save()
