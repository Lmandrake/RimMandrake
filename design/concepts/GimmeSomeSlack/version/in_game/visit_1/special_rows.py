"""special_rows.py -- the rows that carry a class, a repair or a read: sc_restyle_whole_line, sc_look_menu_icons, sc_wall_lamp_looks, sc_pole_south_of_tree, sc_stub_joins."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = "design/concepts/GimmeSomeSlack/version/in_game/visit_1/"
ident = json.load(open(HERE + "/evidence/identity_tier_gimmesomeslack.json"))
E = lambda n: json.load(open(HERE + "/evidence/" + n))
rows = lambda n: {r["id"]: r["status"] for r in E(n)["rows"]}
base = dict(ident, game="archmagi", site_checked=True, held=[], site_conditions="own cleared plot on the calm site save; every part of the mod on")
out = []
def add(test, verdict, ev, **k): out.append(dict(base, test=test, verdict=verdict, evidence=P + "evidence/" + ev, **k))
cmd = lambda s: "python.exe src\\RimMandrake\\GimmeSomeSlack\\validation.py --scene scene_%s" % s
pre = dict(mod_sha="cf5a867a53", mod_hash="sha256:a9e908d1ed3e6d0ee987901f1e02fdb0ff5a81c09b0e4769b082538f3a394ac4")
r1 = dict(base, **pre); r1.update(test="sc_restyle_whole_line", verdict="FAIL", evidence=P + "evidence/scene_restyle_whole_line_FIRST.json", command=cmd("restyle_whole_line"), run="first pass (build a9e908d1ed3e)", detail=rows("scene_restyle_whole_line_FIRST.json"),
  **{"class": "SITE", "why": "the first pole auto-linked to the bracket as well as the far pole, so cutting the poles' span left the two legs one line and the restyle rightly took both"})
out.append(r1)
add("sc_restyle_whole_line", "PASS", "scene_restyle_whole_line.json", command=cmd("restyle_whole_line"), run="fixed_scene_restyle_whole_line", detail=rows("scene_restyle_whole_line.json"),
  repair={"class": "SITE", "commit": "01c8191ac9c430a39d1f71c32d96fda024e5ff01", "planted": {"plant": "the known-bad state: a second wire joins the legs across the cut (live); and the planted fault crosses_cut on the fake game (selftest_gss_look_scenes.py)", "command": cmd("restyle_whole_line") + " ; python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_look_scenes.py", "verdict": "FAIL", "evidence": P + "evidence/scene_restyle_whole_line_FIRST.json"}})
r2 = dict(base, **pre); r2.update(test="sc_look_menu_icons", verdict="UNMEASURED", evidence=P + "screenshots/sc_look_menu_icons.jpg", command=cmd("look_menu_icons"), run="first pass", detail={"SC_look_icons_shot": "no menu in the capture"},
  **{"class": "HARNESS", "why": "the capture was a cell-rect render, which leaves the interface out: it showed no menu at all"})
out.append(r2)
add("sc_look_menu_icons", "PASS", "scene_look_menu_icons.json", command=cmd("look_menu_icons") + "; then the captures read", run="fixed_scene_look_menu_icons", detail=dict(rows("scene_look_menu_icons.json"), SC_look_icons_shot="PASS (read)"), **{"class": "LOOK"},
  look_read={"reader": "this visit run", "shot": P + "screenshots/sc_look_menu_icons_buttons.jpg", "real": "PASS: the Restyle button wears a rusted scrap plate (Scrapper), a riveted black plate with hazard stripe (Industrial), a white wall socket (Modern), a pale panel with a cyan line (Futuristic); all four tell apart at 27 px without a label",
             "limit": "the look menu itself cannot be held open from the bridge while the game window is not under the mouse; which picture each of its 150 entries carries is read by the program (three rows PASS)"},
  repair={"class": "HARNESS", "commit": "b4a2b18dafa38b693e7a4cadfe5fc9f32cf4443c", "planted": {"plant": "strand_icon: a look entry that carries the strand texture, on the fake game", "command": "python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_look_scenes.py", "verdict": "FAIL", "evidence": "src/RimMandrake/GimmeSomeSlack/selftest_gss_look_scenes.py (planted strand_icon: FAIL rows SC_look_icons_restyle_menus, SC_look_icons_same_picture); the first capture, with no interface in it, reads no icon at all"}})
add("sc_wall_lamp_looks", "PASS", "scene_wall_lamp_looks.json", command=cmd("wall_lamp_looks") + "; then the capture read", run="fixed_scene_wall_lamp_looks", detail=dict(rows("scene_wall_lamp_looks.json"), SC_wall_lamp_shot="PASS (read)"), **{"class": "LOOK"},
  look_read={"reader": "this visit run", "shot": P + "screenshots/sc_wall_lamp_looks.jpg, modern_wall_plug_AFTER_fix.jpg, wall_lamps_close_first_pass.jpg", "real": "PASS: caged bulb (Scrapper), caged bulb on a riveted plate (Industrial), flat box light (Modern), pale cone with a cyan bar (Futuristic), each flush on its wall in four facings, beside a standing lamp"},
  mod_fix={"commit": "01c8191ac9c430a39d1f71c32d96fda024e5ff01", "unit": ident.get("unit"),
           "red": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --joins-only", "rc": 1, "on": "90543074a05426fdaffac67bbd9fc82340360f7a with the new StubJoinChecks.FarWallLamps (evidence/fix_wall_lamp_joins_RED_on_parent.log)"},
           "green": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --joins-only", "rc": 0, "on": "01c8191ac9c430a39d1f71c32d96fda024e5ff01"}})
add("sc_pole_south_of_tree", "PASS", "scene_pole_south_of_tree.json", command=cmd("pole_south_of_tree") + "; then the capture read", run="fixed_scene_pole_south_of_tree", detail=dict(rows("scene_pole_south_of_tree.json"), SC_pole_south_of_tree_shot="PASS (read)"), **{"class": "LOOK"},
  look_read={"reader": "this visit run; the read's planted control is visit 1 of 0.1.1's (the check is unchanged)", "shot": P + "screenshots/sc_pole_south_of_tree.jpg", "real": "PASS: the pole south of the green tree is drawn over it; the pole north of the orange tree is behind its canopy"})
j = E("stub_joins.json")
add("sc_stub_joins", j["result"], "stub_joins.json", command="python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_stub_joins.py --load (ArchBig, tier gimmesomeslack)", run="fixed_stub_joins", detail={k: j["probe"].get(k) for k in ("taken", "offLine", "offSlope", "empty", "liveOffSlope", "livePinched", "liveUnlaid", "wallTerminalsLoose")})
with open(HERE + "/rows.jsonl", "a") as f:
    for r in out: f.write(json.dumps(r, sort_keys=True) + "\n")
print(len(out))
