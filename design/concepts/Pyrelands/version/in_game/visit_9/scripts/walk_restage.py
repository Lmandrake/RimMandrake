"""Visit 9, restage of the walk save (item RIMMANDRAKE_FREE_PYRE_WALK_SAVE_SKY_TUTOR_PINS_CLEAR). python.exe, ArchSmall held, the
old walk save freshly loaded (live_site.py --save PYRELANDS_0.1.0_VISIT9_WALK) and still paused. Runs no tick: the stations stay
as saved. Storyteller Cassandra (Tutor pins the sky clear), Peaceful so no raid meets his walk, one sign per station in the save,
and one pen for each creature kind of the mod with six animals in each (modcheck/walk_pens.py; the walk brief's pens rule).
    python.exe ...\\walk_restage.py NAME      stage and save as NAME (refuses an existing name)
The Pyrelands review save (PYRELANDS_REVIEW) is this script's output on PYRELANDS_0.1.0_VISIT9_WALK: version/walk_brief/review_save.md."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
for p in ("Utils", "Utils/modcheck"):
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", *p.split("/")))
import reviewmap as RM  # noqa: E402
import stage_review as S  # noqa: E402
import walk_pens as WP  # noqa: E402
NAME, OLD_TICK = sys.argv[1], 677101
# x, z of the sign, key, name, look, do, decide, then the rect a capture of the station frames
STATIONS = [
    (30, 37, "1", "burn front", "a line of fire at the left edge of fresh ember grass", "unpause and watch for a day or two at speed 3",
     "does it spread like a natural grass fire?", (18, 18, 24, 21)),
    (84, 37, "2", "creatures", "a herd of 6 ullai, one furnace-beast, 2 ashwallows", "look while it is paused: once the clock runs they leave for shade",
     "do the outlined ullai read well?", (74, 20, 20, 19)),
    (138, 32, "3", "scorch-fruit", "16 pods standing in bare ash, set by hand; real ones come up in the burned ground of station 1", "", "", (130, 22, 14, 12)),
    (180, 44, "4", "roofed grass", "the left patch is under a roof, the right patch is open", "run one day: the roofed patch withers, the open one stays", "",
     (170, 33, 20, 13)),
    (159, 111, "5", "charred ruin", "blackened walls on deep ash, made with the map", "", "", (149, 97, 20, 17)),
]
B = RM.LiveBridge()
c = B.call
c("rimworld/set_time_speed", speed=0)
hour, tick = S.local_hour(B.S)
if not OLD_TICK <= tick <= OLD_TICK + 5 or not 10 <= hour <= 14:
    sys.exit("NOT STAGED: tick %s, hour %.1f; load the old walk save first" % (tick, hour))
st = c("jawa/storyteller_swap", storytellerDef="Cassandra", difficultyDef="Peaceful")
wx = c("jawa/weather_set", unlock=True)
q = c("jawa/incident_queue_clear")
c("jawa/review_label", action="clear", tag="pyre_visit9")
signs = [RM.sign_book(x, z, k, n, look=l, do=d, decide=e) for x, z, k, n, l, d, e, _ in STATIONS]
pr = RM.place_signs(B, signs)
got = {(s["x"], s["z"]): s["title"] for s in c("jawa/review_sign", action="list").get("signs") or []}
moved = [(x, z) for x, z, *_ in STATIONS if (x, z) not in got]
hostiles = [p for p in c("jawa/list_pawns", limit=500).get("pawns") or [] if p.get("hostile")]
for x, z, k, n, l, d, e, (rx, rz, rw, rh) in STATIONS:
    c("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (rx, rz, rw, rh))
c("jawa/clear_ui")
fx, fz, fw, fh = STATIONS[0][-1]
c("rimworld/jump_camera_to_cell", x=fx + fw // 2, z=fz + fh // 2)
c("rimworld/frame_cell_rect", x=fx, z=fz, width=fw, height=fh, paddingCells=3)
out = {"storyteller": st.get("after"), "weather_unlock": wx.get("success"), "queue": q.get("success"), "placed": len(pr.get("placed") or []),
       "refused": pr.get("refused"), "signs": sorted(got.values()), "not_on_its_cell": moved, "hostiles": len(hostiles), "hour": hour, "tick": tick}
if len(got) != len(STATIONS) or (st.get("after") or {}).get("storytellerDef") != "Cassandra" or hostiles:
    print(json.dumps(out, indent=1)); sys.exit("NOT SAVED: see above")
pens = WP.stage(B, "Pyrelands")
out["pens"] = {k: pens.get(k) for k in ("ok", "why", "site", "block", "rows", "not_loaded")}
if not pens.get("ok"):
    print(json.dumps(out, indent=1)); sys.exit("NOT SAVED: the pens did not stage (see out.pens)")
out["save"] = RM.save_keeper(B, NAME, saves=RM.SAVES, signs=signs + pens["signs"])
print(json.dumps(out, indent=1))
json.dump({"name": NAME, "stations": [(s[2], s[3], s[-1], s[:2]) for s in STATIONS], "out": out},
          open(os.path.join(ROOT, "design/concepts/Pyrelands/version/in_game/visit_9/evidence/walk_restage.json"), "w"), indent=1)
sys.exit(0 if out["save"]["ok"] else 1)
