"""special_rows.py -- visit 2's rows that carry a class, a read or a mod fix: sc_wall_lamp_looks, sc_look_menu_icons, sc_pole_south_of_tree, sc_stub_joins, sc_walk."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); P = "design/concepts/GimmeSomeSlack/version/in_game/visit_2/"
E = lambda n: json.load(open(HERE + "/evidence/" + n))
ident, pre = E("identity_tier_gimmesomeslack_fixed.json"), E("identity_tier_gimmesomeslack.json")
rows = lambda n: {r["id"]: r["status"] for r in E(n)["rows"]}
cmd = lambda s: "python.exe src\\RimMandrake\\GimmeSomeSlack\\validation.py --scene scene_%s" % s
out = []
def add(test, verdict, ev, idn=ident, **k):
    r = dict(idn, test=test, verdict=verdict, evidence=P + "evidence/" + ev, game="archmagi", game_instance="ArchSmall", site_checked=True, held=[],
             site_conditions="own cleared plot (scene _site); every part of the mod on", forbidden=[], **k)
    out.append(r)
FIX = "37c34e81fc644e7bc6c84c0eadfc5e2248d84aac"
add("sc_wall_lamp_looks", "FAIL", "scene_wall_lamp_looks.json", pre, command=cmd("wall_lamp_looks") + "; then the capture read", run="first pass (build c8a4aace8b18)", outcome="MOD FAILURE",
    detail=dict(rows("scene_wall_lamp_looks.json"), SC_wall_lamp_shot="FAIL (read)"),
    **{"class": "MOD", "why": "read close up (screenshots/near_lamp_plug_on_strip_BEFORE_fix.jpg): the device plug of a wall lamp on the cord's own side of the wall is drawn on the power strip, stacked on the strip's plug, not at the lamp. EndDecor measured each cord end to the lamp's footprint, but the lamp's cord ends in the wall cell, half a cell outside it"})
add("sc_wall_lamp_looks", "PASS", "fixed_scene_wall_lamp_looks.json", command=cmd("wall_lamp_looks") + "; then the capture read", run="fixed_scene_wall_lamp_looks", outcome="SUCCESS",
    detail=dict(rows("fixed_scene_wall_lamp_looks.json"), SC_wall_lamp_shot="PASS (read)"), **{"class": "LOOK"},
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_wall_lamp_looks.jpg, near_lamp_plug_on_strip_AFTER_fix.jpg, wall_lamps_and_pole_fixed_build.jpg",
               "real": "PASS: caged bulb (Scrapper), flat box light (Modern, also the two Industrial lamps after the run's restyle), pale cone with a cyan bar (Futuristic), each flush on its wall in four facings, beside a standing lamp; no plug on a strip but the strip's own"},
    planted="GC_LAMP_MASTER_OFF_KEEPS_LOOK: visit 1 planted it in a deployed DLL and this check read FAIL (evidence/scene_wall_lamp_looks_PLANTED_GC_LAMP_MASTER_OFF.json there); the row that read it, SC_wall_lamp_master_off_vanilla, is unchanged and reads PASS here",
    mod_fix={"commit": FIX, "unit": ident["unit"],
             "red": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --joins-only", "rc": 1, "on": "db7ead9f11 with the new StubJoinChecks.NearWallLamps (evidence/fix_near_lamp_plug_RED_on_parent.log: 246 of 480)"},
             "green": {"cmd": "python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py --no-export --joins-only", "rc": 0, "on": FIX}})
add("sc_look_menu_icons", "PASS", "fixed_scene_look_menu_icons.json", command=cmd("look_menu_icons") + "; then the captures read", run="fixed_scene_look_menu_icons", outcome="SUCCESS",
    detail=dict(rows("fixed_scene_look_menu_icons.json"), SC_look_icons_shot="PASS (read)"), **{"class": "LOOK"},
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_look_menu_icons_buttons.jpg",
               "real": "PASS: the Restyle button wears a rusted scrap plate (Scrapper), a black riveted plate with a hazard stripe (Industrial), a white wall socket (Modern), a pale panel with a cyan line (Futuristic)",
               "limit": "the 150 menu entries are read by the program; the menu itself cannot be held open from the bridge"})
add("sc_pole_south_of_tree", "PASS", "fixed_scene_pole_south_of_tree.json", command=cmd("pole_south_of_tree") + "; then the capture read", run="fixed_scene_pole_south_of_tree", outcome="SUCCESS",
    detail=dict(rows("fixed_scene_pole_south_of_tree.json"), SC_pole_south_of_tree_shot="PASS (read)"), **{"class": "LOOK"},
    look_read={"reader": "this visit run", "shot": P + "screenshots/sc_pole_south_of_tree.jpg", "real": "PASS: the south pole is drawn over its tree; the pole north of the other tree is behind its canopy"})
j = E("stub_joins.json")
add("sc_stub_joins", j["result"], "stub_joins.json", command="python.exe src\\RimMandrake\\GimmeSomeSlack\\northstar\\live_stub_joins.py --load (ArchSmall, tier gimmesomeslack)", run="fixed_stub_joins", outcome="SUCCESS",
    detail={k: j["probe"].get(k) for k in ("taken", "offLine", "offSlope", "empty", "liveOffSlope", "livePinched", "liveUnlaid", "wallTerminalsLoose")},
    wall_plug_look={"command": "python.exe src\\RimMandrake\\GimmeSomeSlack\\review\\wall_plug_look.py --new D:\\ClaudeWork\\rimmandrake\\scratch\\gss_020_v2\\plug_look_fixed", "rc": 0,
                    "real": "joins 60 taken, 0 off; 12 captures read: every cord leaves its wall plug straight out of the stub", "shot": P + "screenshots/wall_plug_look_fixed_build.jpg"},
    repair={"class": "HARNESS", "commit": FIX, "what": "wall_plug_look.py staged no cord (a Modern key that does not exist) and exited 0; V.shot's crop of a reused name showed the old picture",
            "planted": {"plant": "known-bad state: the bad look key put back on the repaired script", "command": "wall_plug_look.py with cline:...:Modern: (temporary copy)", "verdict": "FAIL", "evidence": "D:\\ClaudeWork\\rimmandrake\\scratch\\gss_020_v2\\wall_plug_look_bad.txt (staged all false, rc 2)"}})
ident_walk = {k: v for k, v in ident.items() if k not in ("tier", "full_list")}
add("sc_walk", "UNMEASURED", "identity_tier_gimmesomeslack_fixed.json", command="src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py (not run)", run="none", outcome="COULD NOT LOOK",
    detail="ArchSmall: tier list only beside ArchBig", **{"class": "SITE", "unrepaired": "ArchSmall cannot hold his full list beside ArchBig in memory, so this check did not run here",
    "owner": "ArchBig: its full-list run of this check"})
with open(HERE + "/rows.jsonl", "a") as f:
    for r in out: f.write(json.dumps(r, sort_keys=True) + "\n")
print(len(out))
