"""special_rows.py -- visit 3's rows that carry a class, a read, a repair or a mod fix."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = "design/concepts/GimmeSomeSlack/version/in_game/visit_3/"
E = lambda n: json.load(open(HERE + "/evidence/" + n))
ident, pre = E("identity_tier_gimmesomeslack.json"), E("identity_tier_gimmesomeslack_prefix.json")
rows = lambda n: {r["id"]: r["status"] for r in E(n)["rows"]}
cmd = lambda s: "python.exe src\\RimMandrake\\GimmeSomeSlack\\validation.py --scene scene_%s" % s
FIX = "ad72a3cec3d9f9e52634ace20abc224df7ab1e67"; GS = "8d5d5c574055599e1b2fc02659962ce29cb6a8fb"
out = []
def add(test, verdict, ev, idn=ident, **k):
    r = dict(idn, test=test, verdict=verdict, evidence=P + "evidence/" + ev, game="archmagi", game_instance="ArchBig", site_checked=True, held=[], forbidden=[])
    r.setdefault("site_conditions", "own cleared plot; every part of the mod on"); r.update(k); out.append(r)
LOOK = {"class": "LOOK"}
add("sc_wall_lamp_looks", "PASS", "scene_wall_lamp_looks.json", command=cmd("wall_lamp_looks") + "; then the capture read", run="scene_wall_lamp_looks", outcome="SUCCESS",
    detail=dict(rows("scene_wall_lamp_looks.json"), SC_wall_lamp_shot="PASS (read)"), **LOOK,
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_wall_lamp_looks.jpg",
               "real": "PASS: caged bulb (Scrapper), flat box lights (Industrial, Modern), pale cone with a cyan bar (Futuristic), each flush on its wall in four facings, beside a standing lamp; each near lamp's plug is at its lamp and no plug stacks on a strip"},
    planted="GC_LAMP_MASTER_OFF_KEEPS_LOOK: visit 1 planted it in a deployed DLL and SC_wall_lamp_master_off_vanilla read FAIL (visit_1/evidence/scene_wall_lamp_looks_PLANTED_GC_LAMP_MASTER_OFF.json); that row is unchanged and reads PASS here")
add("sc_look_menu_icons", "PASS", "scene_look_menu_icons.json", command=cmd("look_menu_icons") + "; then the captures read", run="scene_look_menu_icons", outcome="SUCCESS",
    detail=dict(rows("scene_look_menu_icons.json"), SC_look_icons_shot="PASS (read)"), **LOOK,
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_look_menu_icons_buttons.jpg",
               "real": "PASS: the Restyle button wears a rusted scrap plate (Scrapper), a black riveted plate with a hazard stripe (Industrial), a white wall socket (Modern), a pale panel with a cyan line (Futuristic)",
               "limit": "the menu entries are read by the program; the menu itself cannot be held open from the bridge"})
add("sc_pole_south_of_tree", "PASS", "scene_pole_south_of_tree.json", command=cmd("pole_south_of_tree") + "; then the capture read", run="scene_pole_south_of_tree", outcome="SUCCESS",
    detail=dict(rows("scene_pole_south_of_tree.json"), SC_pole_south_of_tree_shot="PASS (read)"), **LOOK,
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_pole_south_of_tree.jpg", "real": "PASS: the pole south of its tree is drawn over the tree; the pole north of the other tree stands behind its canopy"})
j = E("stub_joins.json")
add("sc_stub_joins", j["result"], "stub_joins.json", command="python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_stub_joins.py --load (ArchBig, tier gimmesomeslack)", run="stub_joins", outcome="SUCCESS",
    detail={k: j["probe"].get(k) for k in ("taken", "offLine", "offSlope", "empty", "liveOffSlope", "livePinched", "liveUnlaid", "wallTerminalsLoose")},
    wall_plug_look={"command": "python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\wall_plug_look.py --new D:\\ClaudeWork\\rimmandrake\\scratch\\gss_020_v3\\plug_look", "rc": 0,
                    "real": "joins 60 taken, 0 off; 12 captures read: every cord leaves its wall plug straight out of the stub", "shot": P + "screenshots/wall_plug_look.jpg"})
pb = {r["id"]: r for r in E("prefix_build_runB.json")["rows"]}
add("sc_save_reload_wire_down", "FAIL", "prefix_build_runB.json", pre, command="python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots --skip-offline --only aerial,style,save_load,d4_save,statics,tap_goodwill", run="first pass (build f4d5517ca1)", outcome="MOD FAILURE",
    detail={k: pb[k]["status"] for k in ("WD_save_before_cut_refused", "WD_reload_true_to_grid", "WD_reload_live_dead_ends_equal")}, **{"class": "MOD",
    "why": "the cut floor run drew no dead end: its far side was one loop at the lamp (edge consumer:72,212|consumer:72,212). HookupPick.Pick hooked the lamp to both ends of its one run when vanilla's power parent was the run's other end. Beside it the scene read its lamps 8 ticks after the build, before vanilla switches them on (SITE)"})
wd = E("runB_gss_aerial_style_save_statics.slim.json"); wr = {r["id"]: r["status"] for r in wd["rows"]}
last = [json.loads(l) for l in open(HERE + "/rows.jsonl") if l.strip()]
def latest(t):
    r = [x for x in last if x["test"] == t and x.get("game") == "archmagi"][-1]
    return {k: v for k, v in r.items()}
def again(test, **k):
    r = latest(test); assert r["verdict"] == "PASS", (test, r["verdict"]); r.update(k); out.append(r)
again("sc_save_reload_wire_down",
    mod_fix={"commit": FIX, "unit": ident["unit"],
             "red": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export", "rc": 1, "on": "f4d5517ca1 with the new PhantomSparkChecks.CutRunKeepsItsDeadEnd (evidence/fix_cut_run_dead_end_RED_on_parent.log: 10 of 33 red); the same under the planted fault, version/evidence/red_seen.json T_CORE"},
             "green": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export", "rc": 0, "on": FIX}},
    repair={"class": "SITE", "commit": FIX, "what": "save_wire_down.stage waits until both lamps are lit (they read dark at 8 ticks, lit at 258)",
            "planted": {"plant": "a run cell lost between the two reads; and a floor battery removed", "command": "python.exe design/concepts/GimmeSomeSlack/version/in_game/visit_3/wd_plant.py", "verdict": "FAIL", "evidence": P + "evidence/wd_plant.txt"}})
GSREP = {"class": "HARNESS", "commit": GS, "what": "the landed true-to-grid read: a lamp wired straight to the battery stands on no transmitted net (its own net is read); the cord of a wall bracket ends in the bracket's own wall (counted apart)",
         "planted": {"plant": "the battery destroyed under the read cord set; a bracket's wall not counted as its own; the pre-launch cord set (every flight)", "command": "python.exe design/concepts/GimmeSomeSlack/version/in_game/visit_3/gs_plant.py", "verdict": "FAIL", "evidence": P + "evidence/gravship_plant.txt"}}
for m, t in (("on", "P_GS1_keep_wires_on_gravship_on_aboard_span_flies"), ("off", "P_GS1_keep_wires_on_gravship_off_aboard_span_taken_down"), ("off_autolink", "P_GS3_auto_link_on_keep_wires_off_span_stays_down")):
    f = E("first_gravship_%s.json" % m)["rows"][0]
    k = dict(command="python.exe src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py %s" % m, run="first pass", outcome="APPARATUS FAULT", **{"class": "HARNESS", "why": "check wrong: " + "; ".join(f["detail"]["whyNot"])[:300]})
    add(t, "UNMEASURED", "first_gravship_%s.json" % m, **k)
    if m == "on":
        add("sc_gravship", "UNMEASURED", "first_gravship_on.json", **k)
    again(t, repair=GSREP)
again("sc_gravship", repair=GSREP)
with open(HERE + "/rows.jsonl", "a") as f:
    for r in out: f.write(json.dumps(r, sort_keys=True) + "\n")
print(len(out))
