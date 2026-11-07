"""Look at Graffiti the way a player does. Run from the repo root under Windows python.exe, game up on graffiti_solo, bridge held:
    python.exe src/RimMandrake/Graffiti/stage_colony.py new              fresh quicktest world
    python.exe src/RimMandrake/Graffiti/stage_colony.py colony           build the lived-in base (RM_GraffitiStage.Colony)
    python.exe src/RimMandrake/Graffiti/stage_colony.py call <Method> [arg]
    python.exe src/RimMandrake/Graffiti/stage_colony.py run <ticks>      advance the clock in steps (reads marks back)
    python.exe src/RimMandrake/Graffiti/stage_colony.py shot <name> x,z,w,h [ppc=64]    measured-zoom shot, saved to the shots folder
Every shot is taken paused at measured px per cell (modcheck/play_zoom)."""
import json, os, shutil, sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
sys.path.insert(0, r"src\RimMandrake\Utils\modcheck")
import rimbridge_client as rb
import play_zoom

PROBE = "RimMandrake.Graffiti.RM_GraffitiStage"
SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_graffiti\shots"
CALFILE = r"D:\ClaudeWork\rimmandrake\ralph_graffiti\k.json"


class Sess(object):
    def __init__(self):
        h, p, t = rb.resolve_endpoint()
        self.s = rb.RimBridge(host=h, port=p, token=t, timeout=300.0)
        self.s.connect()

    def call(self, tool, **kw):
        r = self.s.call(tool, kw) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r


def static(s, method, arg="x"):
    r = s.call("jawa/static_call", type=PROBE, method=method, args=arg)
    return (r.get("result") if isinstance(r, dict) else None) or r


def shot(s, name, rect, ppc=64):
    s.call("jawa/set_fog", action="unfog", rect=",".join(str(v) for v in rect)) if False else None
    cal = play_zoom.Calibration()
    path = play_zoom.shoot(s, cal, rect, 0, ppc, name, RuntimeError)
    local = play_zoom.local_path(path) if not os.path.exists(path) else path
    dest = os.path.join(SHOTS, name + ".png")
    shutil.copy(local, dest)
    print("SHOT", dest)


def run(s, ticks):
    done = 0
    while done < ticks:
        n = min(2000, ticks - done)
        s.call("rimworld/step_game_ticks", ticks=n)
        done += n
        print(done, static(s, "Count"), flush=True)


def main():
    a = sys.argv[1:]
    if a[0] == "new":
        import subprocess
        sys.exit(subprocess.call([sys.executable, r"src\RimMandrake\bridgetools\prove_quicktest_world.py"]))
    s = Sess()
    if a[0] == "colony":
        print(static(s, "Colony"))
    elif a[0] == "call":
        print(static(s, a[1], a[2] if len(a) > 2 else "x"))
    elif a[0] == "run":
        run(s, int(a[1]))
    elif a[0] == "shot":
        rect = tuple(int(v) for v in a[2].split(","))
        shot(s, a[1], rect, int(a[3]) if len(a) > 3 else 64)
    elif a[0] == "raw":
        print(json.dumps(s.call(a[1], **json.loads(a[2] if len(a) > 2 else "{}")))[:3000])


main()
