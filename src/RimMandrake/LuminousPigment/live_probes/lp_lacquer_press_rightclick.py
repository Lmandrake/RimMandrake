"""LACQUER_PRESS_REWIRE_BILL_PLUS_RIGHT_CLICK, the two owed live rows, through the real right-click path
(rimworld/open_context_menu dispatches a live map click, so FloatMenuOptionProvider_LacquerAtPress runs as for a player):
  R1 POWERED: a selected colonist right-clicking RM_DeepfirePress gets one enabled "Lacquer <item> (N deepfire)" per
     worn/held item; taking one starts RM_LacquerWornItem, which consumes N deepfire and adds a coat (read as the
     item's Beauty rising: RM_StatPart_Deepfire reads CompDeepfire.coats; jawa/comp_read cannot see worn items).
  R2 UNPOWERED: the same options, every one disabled and reading ": The deepfire press has no power."
python.exe, bridge held, any scratch/quicktest map, game paused. argv: "X,Z" site origin (default 10,10),
optional evidence dir (default D:\\ClaudeWork\\rimmandrake\\lacquer_press\\live_rc). Exit 0 = both PASS."""
import sys, os, json, re, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
X, Z = (int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else "10,10").split(","))
EV = sys.argv[2] if len(sys.argv) > 2 else r"D:\ClaudeWork\rimmandrake\lacquer_press\live_rc"
os.makedirs(EV, exist_ok=True)
stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
R = lambda x, z, w, h: "%d,%d,%d,%d" % (x, z, w, h)
SITE = R(X - 2, Z - 2, 14, 11)
PX, PZ = X + 4, Z + 5                      # press centre (3x1, interaction cell at PZ-1)
ev = {"site": SITE, "press": [PX, PZ]}
rows = {}                                  # row -> (verdict, detail)
LAB = re.compile(r"^Lacquer (.+) \((\d+) deepfire\)(?:: (.*))?$")

def deepfire():
    th = call("jawa/list_things", defName="RM_Deepfire", rect=SITE).get("things") or []
    return sum(int(x.get("stackCount") or x.get("count") or 1) for x in th)
def gear(pid):
    r = call("jawa/thing_stats", pawn=pid, slot="equipment,apparel", stats="Beauty")
    out = []
    for th in r.get("things") or r.get("rows") or []:
        st = th.get("stats") or []
        b = next((s.get("value") for s in st if isinstance(s, dict) and s.get("defName", s.get("stat")) == "Beauty"), None)
        out.append({"id": th.get("id"), "def": th.get("defName"), "label": th.get("label"), "beauty": b})
    return out, r
def menu():
    m = call("rimworld/open_context_menu", x=PX, z=PZ, button="right")
    o = call("rimworld/get_context_menu_options")
    opts = o.get("options") or m.get("options") or []
    lac = [x for x in opts if str(x.get("label", "")).startswith("Lacquer ")]
    return m, o, opts, lac
def shot(name):
    s = call("rimworld/take_screenshot", fileName="lacquer_rc_%s_%s" % (name, stamp))
    return s.get("path") or s.get("screenshotPath") or s

# ---- preflight
gi = call("rimworld/get_game_info")
ev["preflight"] = {"paused": (gi.get("state") or {}).get("paused"), "tick": gi.get("ticksGame")}
if ev["preflight"]["paused"] is not True:
    call("rimworld/set_time_speed", speed="Paused")
# ---- stage: room, press, 10 deepfire, fresh colonist with known gear
call("jawa/clear_area", rect=SITE, dryRun=False)
call("jawa/set_fog", action="unfog", rect=SITE)
call("jawa/make_empty_room", rect=R(X - 1, Z - 1, 12, 9), wallDef="Wall", stuffDef="WoodLog", floorDef="WoodPlankFloor")
call("jawa/spawn_batch", ops="RM_DeepfirePress:%d,%d;RM_Deepfire:%d,%d,10" % (PX, PZ, X + 1, Z + 1))
press = (call("jawa/list_things", defName="RM_DeepfirePress", rect=SITE).get("things") or [None])[0]
before = {q.get("id") for q in call("jawa/list_pawns", rect=SITE).get("pawns") or []}
call("jawa/spawn_pawn", kindDef="Colonist", x=X + 8, z=Z + 1, faction="player", count=1)
pid = next((q.get("id") for q in call("jawa/list_pawns", rect=SITE).get("pawns") or [] if q.get("id") not in before), None)
ev["press"] = press; ev["pawn"] = pid
if not press or not pid:
    print("UNMEASURED: staging failed press=%s pawn=%s" % (bool(press), pid)); json.dump(ev, open(os.path.join(EV, "rc_%s.json" % stamp), "w"), indent=1); sys.exit(2)
ev["gear_ops"] = [call("jawa/pawn_gear", pawn=pid, action="clear", clearWhat="all").get("success"),
                  call("jawa/pawn_gear", **{"pawn": pid, "action": "wear", "def": "Apparel_CollarShirt", "stuff": "Cloth"}).get("success"),
                  call("jawa/pawn_gear", **{"pawn": pid, "action": "wear", "def": "Apparel_Pants", "stuff": "Cloth"}).get("success"),
                  call("jawa/pawn_gear", **{"pawn": pid, "action": "equip", "def": "Gun_Autopistol"}).get("success")]
items, raw = gear(pid)
ev["items0"] = items
if not items:
    ev["gear_raw"] = raw
call("rimworld/jump_camera_to_cell", x=PX, z=PZ)
ev["deepfire0"] = deepfire()

# ---- R1 powered
ev["power_on"] = {k: v for k, v in call("jawa/power_net", thing=press["id"], forcePowerOn=True).items() if k in ("success", "powerOnBefore", "powerOnAfter", "connected", "error")}
call("rimworld/select_pawn", pawnId="Thing_" + str(pid))
m, o, opts, lac = menu()
ev["r1_menu"] = {"open": m, "options": opts}
ev["r1_shot"] = shot("powered")
p1 = []
if ev["power_on"].get("powerOnAfter") is not True:
    rows["R1"] = ("UNMEASURED", "press would not power on: %s" % ev["power_on"])
elif not items:
    rows["R1"] = ("UNMEASURED", "could not read the colonist's gear")
else:
    if len(lac) != len(items):
        p1.append("%d lacquer options for %d worn/held items" % (len(lac), len(items)))
    for x in lac:
        mm = LAB.match(str(x.get("label")))
        if not mm or mm.group(3) or x.get("disabled"):
            p1.append("option not enabled/well-formed: %r disabled=%s" % (x.get("label"), x.get("disabled")))
    target = next((x for x in lac if not x.get("disabled") and LAB.match(str(x.get("label"))) and not LAB.match(str(x.get("label"))).group(3)), None)
    if target is None:
        rows["R1"] = ("FAIL", "; ".join(p1) or "no enabled lacquer option")
    else:
        cost = int(LAB.match(target["label"]).group(2))
        ex = call("rimworld/execute_context_menu_option", label=target["label"])
        ev["r1_exec"] = ex
        jobs, seen, tick = [], False, 0
        for _ in range(30):
            sel = call("jawa/select_things", action="get")
            cj = next((r.get("currentJob") for r in sel.get("selected") or sel.get("pawns") or sel.get("rows") or [] if isinstance(r, dict) and str(r.get("id")) == str(pid)), None)
            jobs.append((tick, cj))
            if cj == "RM_LacquerWornItem":
                seen = True
            elif seen:
                break
            call("rimworld/step_game_ticks", ticks=150, pauseFirst=True, timeoutMs=120000); tick += 150
        ev["r1_jobs"] = jobs
        ev["deepfire1"] = deepfire()
        items1, _ = gear(pid); ev["items1"] = items1
        name = LAB.match(target["label"]).group(1)
        b0 = next((i["beauty"] for i in items if name.lower() in str(i["label"]).lower()), None)
        b1 = next((i["beauty"] for i in items1 if name.lower() in str(i["label"]).lower()), None)
        ev["beauty_target"] = [name, b0, b1]
        if not seen:
            p1.append("taking %r never started RM_LacquerWornItem (jobs %s)" % (target["label"], jobs[:6]))
        elif ev["deepfire0"] - ev["deepfire1"] != cost:
            p1.append("deepfire %s -> %s, wanted -%d" % (ev["deepfire0"], ev["deepfire1"], cost))
        coat = "beauty %s -> %s" % (b0, b1)
        if seen and b0 is not None and b1 is not None and not float(b1) > float(b0):
            p1.append("no coat added (%s)" % coat)
        rows["R1"] = ("FAIL" if p1 else "PASS", "; ".join(p1) if p1 else "%d/%d options enabled; took %r: job RM_LacquerWornItem ran, deepfire %s->%s, %s"
                      % (len(lac), len(items), target["label"], ev["deepfire0"], ev["deepfire1"], coat if b1 is not None else "coat UNMEASURED (no Beauty row)"))
call("rimworld/close_context_menu")

# ---- R2 unpowered
ev["power_off"] = {k: v for k, v in call("jawa/power_net", thing=press["id"], forcePowerOn=False).items() if k in ("success", "powerOnBefore", "powerOnAfter", "connected", "error")}
call("rimworld/select_pawn", pawnId="Thing_" + str(pid))
m, o, opts, lac = menu()
ev["r2_menu"] = {"open": m, "options": opts}
ev["r2_shot"] = shot("unpowered")
p2 = []
if ev["power_off"].get("powerOnAfter") is not False:
    rows["R2"] = ("UNMEASURED", "press would not power off: %s" % ev["power_off"])
else:
    if len(lac) != len(items):
        p2.append("%d lacquer options for %d worn/held items" % (len(lac), len(items)))
    for x in lac:
        mm = LAB.match(str(x.get("label")))
        if not mm or mm.group(3) != "The deepfire press has no power." or x.get("disabled") is not True:
            p2.append("not greyed with the no-power reason: %r disabled=%s" % (x.get("label"), x.get("disabled")))
    rows["R2"] = ("FAIL" if p2 or not lac else "PASS", "; ".join(p2) if p2 else ("%d/%d options greyed 'The deepfire press has no power.'" % (len(lac), len(items)) if lac else "no lacquer options at all"))
call("rimworld/close_context_menu")
call("rimworld/set_time_speed", speed="Paused")

out = os.path.join(EV, "rc_%s.json" % stamp)
json.dump(ev, open(out, "w"), indent=1, default=str)
print("%-4s %-11s %s" % ("row", "verdict", "detail"))
for k in ("R1", "R2"):
    v, d = rows.get(k, ("UNMEASURED", "not reached"))
    print("%-4s %-11s %s" % (k, v, d))
print("evidence", out, "shots", ev.get("r1_shot"), ev.get("r2_shot"))
sys.exit(0 if all(rows.get(k, ("",))[0] == "PASS" for k in ("R1", "R2")) else 1)
