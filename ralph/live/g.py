"""Ralph's live driver for Graffiti on game B. Run on Steve through ralph/steve.sh run 'python.exe ralph/live/g.py ...'.
    g.py st <Method> [arg]          RM_GraffitiStage.<Method>
    g.py so <Method> [arg]          RM_GraffitiSocialProof.<Method>
    g.py run <ticks> [chunk]        advance the clock, print the social ledger after each chunk
    g.py shot <name> x,z,w,h [ppc]  measured-zoom shot into Transient/gshots
    g.py raw <tool> [json]          any bridge tool
    g.py tools [filter]             list bridge tools
Several commands can be chained with " @ " between them."""
import json, os, shutil, sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
sys.path.insert(0, r"src\RimMandrake\Utils\modcheck")
import rimbridge_client as rb
import play_zoom

STAGE = "RimMandrake.Graffiti.RM_GraffitiStage"
SOCIAL = "RimMandrake.Graffiti.RM_GraffitiSocialProof"
SHOTS = r"Transient\gshots"


class Sess(object):
    def __init__(self):
        h, p, t = rb.resolve_endpoint()
        self.s = rb.RimBridge(host=h, port=p, token=t, timeout=300.0)
        self.s.connect()
        self.cal = play_zoom.Calibration()

    def call(self, tool, **kw):
        r = self.s.call(tool, kw) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r


def static(s, typ, method, arg="x"):
    r = s.call("jawa/static_call", type=typ, method=method, args=arg)
    return (r.get("result") if isinstance(r, dict) else None) or r


def shot(s, name, rect, ppc=64):
    s.call("rimworld/frame_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0)
    s.call("rimworld/step_game_ticks", ticks=4)
    static(s, STAGE, "Settle")
    for _ in range(6):
        if not s.call("rimworld/close_window", windowType="Dialog_NamePlayerFactionAndSettlement").get("changed"):
            break
    unique = "%s__%d" % (name, int(time.time()))
    path = play_zoom.shoot(s, s.cal, rect, 0, ppc, unique, RuntimeError)
    local = play_zoom.local_path(path)
    for _ in range(40):
        if os.path.exists(local) and os.path.getsize(local) > 0:
            break
        time.sleep(0.5)
    os.makedirs(SHOTS, exist_ok=True)
    dest = os.path.join(SHOTS, name + ".png")
    shutil.copy(local, dest)
    print("SHOT", dest, "ticks", s.call("rimworld/get_game_info").get("ticksGame"))


def run(s, ticks, chunk=2500):
    done = 0
    while done < ticks:
        n = min(chunk, ticks - done)
        r = s.call("jawa/safe_advance", ticks=n)
        done += n
        print("== +%d (%s)" % (done, str(r.get("triggers") if isinstance(r, dict) else r)[:160]), flush=True)
        print(static(s, SOCIAL, "Ledger"), flush=True)


CAST = ["Abrasive/12", "Nerves:-2/0", "Psychopath/13"]     # the quicktest's three colonists become: the mocker, her target, the cold one
RECRUITS = ["Brick/Brawler,Bloodlust/0", "Mo/Neurotic:2/2", "Vex/Kind/3", "Lark/TorturedArtist/15", "Pell/Nerves:1/1"]


def setup(s):
    """The lived-in colony and its eight people. Prints the three originals' names in role order."""
    print(static(s, STAGE, "Colony"))
    names = [l.split(" [")[0] for l in str(static(s, SOCIAL, "Ledger")).splitlines() if " [" in l][:3]
    for n, c in zip(names, CAST):
        print(static(s, SOCIAL, "Cast", n + "/" + c))
    for r in RECRUITS:
        print(static(s, SOCIAL, "Recruit", r))
    print("ROLES mocker=%s target=%s cold=%s" % tuple(names))


def one(s, a):
    if a[0] == "setup":
        setup(s)
        return
    if a[0] == "st":
        print(static(s, STAGE, a[1], a[2] if len(a) > 2 else "x"))
    elif a[0] == "so":
        print(static(s, SOCIAL, a[1], a[2] if len(a) > 2 else "x"))
    elif a[0] == "run":
        run(s, int(a[1]), int(a[2]) if len(a) > 2 else 2500)
    elif a[0] == "shot":
        shot(s, a[1], tuple(int(v) for v in a[2].split(",")), int(a[3]) if len(a) > 3 else 64)
    elif a[0] == "raw":
        print(json.dumps(s.call(a[1], **json.loads(a[2] if len(a) > 2 else "{}")))[:4000])
    elif a[0] == "tools":
        r = s.s.list_tools() if hasattr(s.s, "list_tools") else s.call("tools/list")
        names = [t.get("name") for t in (r.get("tools") if isinstance(r, dict) else r) or []]
        print("\n".join(n for n in names if len(a) < 2 or a[1] in n))


def main():
    s = Sess()
    cmd, cur = [], []
    for w in sys.argv[1:]:
        if w == "@":
            cmd.append(cur)
            cur = []
        else:
            cur.append(w)
    if cur:
        cmd.append(cur)
    for a in cmd:
        one(s, a)


main()
