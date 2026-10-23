"""loadsave.py NAME -- load a save, wait for Playing, pause, print ticks."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import validation_core as V
B = V.Bridge()
print(json.dumps(B.call("rimworld/load_game", saveName=sys.argv[1]), default=str)[:200])
ok, w = V._wait_playing(B, budget_s=420)
B.call("rimworld/pause_game", paused=True)
print("playing", ok, w, json.dumps(B.call("jawa/map_info"), default=str)[:200])
