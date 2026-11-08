"""Ralph's live driver for Graffiti on game B. Run on Steve through ralph/steve.sh run 'python.exe ralph/live/g.py ...'.
    g.py st <Method> [arg]          RM_GraffitiStage.<Method>
    g.py so <Method> [arg]          RM_GraffitiSocialProof.<Method>
    g.py run <ticks> [chunk]        advance the clock, print the social ledger after each chunk
    g.py shot <name> x,z,w,h [ppc]  measured-zoom shot into Transient/gshots
    g.py raw <tool> [json]          any bridge tool
    g.py kv <tool> k=v k=v          any bridge tool, args as key=value (true/false/ints coerced)
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
STOP = "death,downed,hostile_arrival"   # a punch in a fist fight is no reason to stop the clock


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
        r = s.call("jawa/safe_advance", ticks=n, stopOn=STOP)
        done += n
        print("== +%d (%s)" % (done, str(r.get("triggers") if isinstance(r, dict) else r)[:160]), flush=True)
        print(static(s, SOCIAL, "Ledger", "trace"), flush=True)


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


def days(s, ticks, chunk=15000):
    """A run of days with nothing staged: one Tally line per chunk, and only the trace lines that are events (not every read)."""
    import re
    keep = re.compile(r"painted|wants to|over|confront|BLOWS|scrub|crossed|unfinished|refus|fit|goodwill|raid|left their|means to|weathered|eases")
    done = 0
    while done < ticks:
        n = min(chunk, ticks - done)
        r = s.call("jawa/safe_advance", ticks=n, stopOn=STOP)
        done += n
        trig = r.get("triggers") if isinstance(r, dict) else r
        if trig:
            print("TRIGGERS", str(trig)[:300])
        led = str(static(s, SOCIAL, "Ledger", "trace"))
        for l in led.splitlines():
            if l.startswith("  . ") and ((keep.search(l) and " reads " not in l) or " rereads " in l):
                print(l)
        print(static(s, SOCIAL, "Tally"), flush=True)


def until(s, pattern, maxticks, step=60):
    """Advance `step` ticks at a time until a trace line matches `pattern`; leaves the game paused right after it."""
    import re
    done = 0
    while done < maxticks:
        s.call("jawa/safe_advance", ticks=step, stopOn=STOP)
        done += step
        led = str(static(s, SOCIAL, "Ledger", "trace"))
        lines = [l for l in led.splitlines() if l.startswith("  . ")]
        if lines:
            print("\n".join(lines), flush=True)
        if any(re.search(pattern, l) for l in lines):
            print("UNTIL +%d" % done)
            return True
    print("UNTIL gave up after %d" % done)
    return False


def need(s, pawn, which):
    r = s.call("jawa/pawn_need", pawn=pawn)
    for n in (r.get("needs") or []) if isinstance(r, dict) else []:
        if n.get("need") == which:
            return n.get("level")
    return None


def memories(s, pawn, prefix="RM_Graffiti"):
    """A pawn's memories off the walls with their ages in ticks: a reread renews one, so an age under a day on a mark seen for days is the evidence."""
    r = s.call("jawa/pawn_need", pawn=pawn)
    mem = [m for m in (r.get("memories") or []) if str(m.get("def", "")).startswith(prefix)] if isinstance(r, dict) else []
    print("MEMORIES", pawn, " ".join("%s:%s%s" % (m.get("def", "").replace("RM_Graffiti_", ""), m.get("age"), ("/" + str(m.get("otherPawn"))) if m.get("otherPawn") else "") for m in mem))


def painting(s, name, maxticks, step=60):
    """Run until a colonist is painting on their own (a joy paint job), shoot their Needs tab mid-job (recreation rising), then run
    until they finish and shoot it again ("Left my mark")."""
    import re
    done = 0
    who = None
    while done < maxticks and not who:
        s.call("jawa/safe_advance", ticks=step, stopOn=STOP)
        done += step
        w = str(static(s, STAGE, "Who"))
        for part in w.replace("WHO ", "").split(" || "):
            m = re.match(r"(\S+) joy=([\d.]+).*?job=(\S+)", part)
            if m and "Paint" in m.group(3):
                who, joy = m.group(1), m.group(2)
                print("PAINTING", who, "joy", joy, "job", m.group(3), "after", done)
                break
    if not who:
        print("PAINTING none after", done)
        return
    # Recreation only rises once the brush is on the wall: wait for the joy to climb between two reads, then shoot.
    last, cell = None, None
    for _ in range(80):
        s.call("jawa/safe_advance", ticks=20, stopOn=STOP)
        joy = need(s, who, "Joy")
        w = str(static(s, STAGE, "Who"))
        m = re.search(re.escape(who) + r" joy=.*?pos=\((\d+), 0, (\d+)\)", w)
        if m:
            cell = "%s,%s" % (m.group(1), m.group(2))
        if last is not None and joy is not None and joy > last + 1e-5:
            print("RISING", who, last, "->", joy)
            break
        last = joy
    ui(s, name + "_mid", who, "Needs", cell)
    print("MID", who, "joy", need(s, who, "Joy"))
    for _ in range(60):
        s.call("jawa/safe_advance", ticks=120, stopOn=STOP)
        led = str(static(s, SOCIAL, "Ledger", "trace"))
        hit = [l for l in led.splitlines() if l.startswith("  . ") and (who + " painted") in l]
        if hit:
            print("\n".join(hit))
            break
    w = str(static(s, STAGE, "Who"))
    m = re.search(re.escape(who) + r" joy=([\d.]+).*?pos=\((\d+), 0, (\d+)\)", w)
    print("AFTER", who, "joy", need(s, who, "Joy"))
    ui(s, name + "_after", who, "Needs", "%s,%s" % (m.group(2), m.group(3)) if m else None)


def close_naming(s):
    for _ in range(6):
        if not s.call("rimworld/close_window", windowType="Dialog_NamePlayerFactionAndSettlement").get("changed"):
            break


def ui(s, name, pawn, tab, cell=None, root=7.4):
    """Select a pawn, open an inspect tab, frame at about play zoom, take a full-screen shot (UI included)."""
    close_naming(s)
    s.call("jawa/clear_ui")
    s.call("jawa/screenshot_mode", enabled=False)
    if pawn != "-":
        print(str(s.call("rimworld/select_pawn", pawnName=pawn))[:60])
        time.sleep(0.8)
        if tab != "-":
            for _ in range(5):
                r = s.call("rimworld/open_inspect_tab", inspectTabId=tab)
                print(str(r)[:120])
                if isinstance(r, dict) and r.get("success"):
                    break
                time.sleep(0.8)
    if cell:
        x, z = (int(v) for v in cell.split(","))
        s.call("rimworld/jump_camera_to_cell", x=x, z=z)
    elif pawn != "-":
        s.call("rimworld/jump_camera_to_pawn", pawnName=pawn)
    s.call("rimworld/set_camera_zoom", rootSize=root)
    # Steve's real mouse rests over the left of the screen and raises a tooltip on whatever tab is open there: park a virtual hover on the map, right of the wall.
    if cell:
        print(str(s.call("rimworld/set_hover_target", x=x + 7, z=z + 2))[:120])
    s.call("rimworld/step_game_ticks", ticks=1)
    static(s, STAGE, "Settle")
    time.sleep(1.0)
    r = s.call("rimworld/take_screenshot", fileName="%s__%d" % (name, int(time.time())), suppressMessage=True)
    path = r.get("path") if isinstance(r, dict) else None
    for _ in range(40):
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            break
        time.sleep(0.5)
    os.makedirs(SHOTS, exist_ok=True)
    dest = os.path.join(SHOTS, name + ".png")
    shutil.copy(path, dest)
    s.call("rimworld/clear_hover_target")
    s.call("jawa/screenshot_mode", enabled=True)
    print("UISHOT", dest)


def wallui(s, name, cell, root=7.4):
    """Click the wall a mark is drawn on, as a new player would, and shoot the inspect pane with the wall in view."""
    x, z = (int(v) for v in cell.split(","))
    r = s.call("jawa/list_things", rect="%d,%d,1,1" % (x, z), group="BuildingArtificial")
    things = r.get("things") if isinstance(r, dict) else None
    tid = None
    for t in things or []:
        tid = t.get("id") or t.get("thingId") or t.get("ThingID")
        if tid:
            break
    print("WALL", tid, str(r)[:200])
    if not tid:
        return
    close_naming(s)
    s.call("jawa/clear_ui")
    s.call("jawa/screenshot_mode", enabled=False)
    print(str(s.call("jawa/select_things", ids=tid))[:200])
    s.call("rimworld/jump_camera_to_cell", x=x, z=z - 2)
    s.call("rimworld/set_camera_zoom", rootSize=root)
    s.call("rimworld/step_game_ticks", ticks=1)
    static(s, STAGE, "Settle")
    time.sleep(1.0)
    r = s.call("rimworld/take_screenshot", fileName="%s__%d" % (name, int(time.time())), suppressMessage=True)
    path = r.get("path") if isinstance(r, dict) else None
    for _ in range(40):
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            break
        time.sleep(0.5)
    os.makedirs(SHOTS, exist_ok=True)
    shutil.copy(path, os.path.join(SHOTS, name + ".png"))
    s.call("jawa/screenshot_mode", enabled=True)
    print("UISHOT", os.path.join(SHOTS, name + ".png"))


def load(s, save):
    """Load a save from game B's Saves and wait until its map is playing."""
    print(str(s.call("rimworld/load_game", saveName=save))[:200], flush=True)
    for _ in range(240):
        time.sleep(1.0)
        try:
            gi = s.call("rimworld/get_game_info")
        except Exception:
            continue
        if isinstance(gi, dict) and gi.get("ticksGame") and (gi.get("programState") in (None, "Playing")) and gi.get("mapCount", gi.get("maps", 1)):
            print("LOADED", save, "tick", gi.get("ticksGame"), str(gi)[:200])
            # The load reports done before the map is finalised: the first read can see an empty map. Wait for two equal mark counts.
            last = None
            for _ in range(30):
                time.sleep(1.0)
                c = str(static(s, STAGE, "Count"))
                if c == last and not c.startswith("REFUSED"):
                    break
                last = c
            print("MAP", last)
            return
    print("LOAD timed out", save)


def one(s, a):
    if a[0] == "load":
        load(s, a[1])
        return
    if a[0] == "uil":
        # UI layout, one element per line: id, kind, label, rect; filtered by a substring of the line when given
        kw = {"surfaceId": a[1]} if len(a) > 1 and a[1] != "-" else {}
        off = 0
        while True:
            kw["offset"] = off
            r = s.call("rimworld/get_ui_layout", **kw)
            els = []
            if isinstance(r, dict):
                els = list(r.get("elements") or [])
                for sf in r.get("surfaces") or []:
                    print("SURFACE", sf.get("surfaceTargetId"), sf.get("surfaceKind"), sf.get("label"), str(sf.get("rect"))[:80])
                    for e in sf.get("elements") or []:
                        e = dict(e)
                        e["_surface"] = sf.get("surfaceTargetId")
                        els.append(e)
            if not els and off == 0:
                print(json.dumps(r)[:1500])
            for e in els:
                line = json.dumps(e)[:300]
                if len(a) < 3 or a[2].lower() in line.lower():
                    print(line)
            nxt = ((r.get("page") or {}).get("nextOffset")) if isinstance(r, dict) else None
            if not nxt:
                break
            off = nxt
        return
    if a[0] == "hoverlabel":
        # hover the first UI element whose label holds this text (spaces as _), as a player's mouse would
        want = a[1].replace("_", " ").lower()
        r = s.call("rimworld/get_ui_layout")
        for sf in (r.get("surfaces") or []) if isinstance(r, dict) else []:
            for e in sf.get("elements") or []:
                if want in str(e.get("label") or "").lower():
                    print("HOVER", e.get("targetId"), e.get("label"))
                    print(json.dumps(s.call("rimworld/set_hover_target", targetId=e.get("targetId"), anchor=a[2] if len(a) > 2 else "center"))[:300])
                    return
        print("HOVER no element labelled", want)
        return
    if a[0] == "screen":
        # the whole screen as it stands, UI and all
        s.call("rimworld/step_game_ticks", ticks=1)
        time.sleep(1.0)
        r = s.call("rimworld/take_screenshot", fileName="%s__%d" % (a[1], int(time.time())), suppressMessage=True)
        path = r.get("path") if isinstance(r, dict) else None
        for _ in range(40):
            if path and os.path.exists(path) and os.path.getsize(path) > 0:
                break
            time.sleep(0.5)
        os.makedirs(SHOTS, exist_ok=True)
        shutil.copy(path, os.path.join(SHOTS, a[1] + ".png"))
        print("SCREEN", os.path.join(SHOTS, a[1] + ".png"))
        return
    if a[0] == "hover":
        print(json.dumps(s.call("rimworld/set_hover_target", targetId=a[1], anchor=a[2] if len(a) > 2 else "center"))[:300])
        return
    if a[0] == "mem":
        for p in a[1:]:
            memories(s, p)
        return
    if a[0] == "setjoy":
        for p in a[2:]:
            print(str(s.call("jawa/pawn_need", pawn=p, action="need", need="Joy", level=float(a[1])))[:120])
        return
    if a[0] == "painting":
        painting(s, a[1], int(a[2]) if len(a) > 2 else 30000)
        return
    if a[0] == "save":
        print(json.dumps(s.call("rimworld/save_game", saveName=a[1]))[:300])
        return
    if a[0] == "days":
        days(s, int(a[1]), int(a[2]) if len(a) > 2 else 15000)
        return
    if a[0] == "wallui":
        wallui(s, a[1], a[2], float(a[3]) if len(a) > 3 else 7.4)
        return
    if a[0] == "brk":
        print(str(s.call("jawa/pawn_force_mental_break", pawn=a[1], breakDef=a[2], reason="the walls"))[:400])
        return
    if a[0] == "until":
        until(s, a[1], int(a[2]), int(a[3]) if len(a) > 3 else 60)
        return
    if a[0] == "ui":
        ui(s, a[1], a[2], a[3], a[4] if len(a) > 4 and a[4] != "-" else None, float(a[5]) if len(a) > 5 else 7.4)
        return
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
    elif a[0] == "gw":
        r = s.call("jawa/list_factions")
        print("GOODWILL t=%s " % s.call("rimworld/get_game_info").get("ticksGame") + " ".join("%s=%s" % (f.get("name"), f.get("goodwill")) for f in r.get("factions", []) if not a[1:] or f.get("name") in a[1:]))
    elif a[0] in ("kv", "kvall"):
        kw = {}
        for pair in a[2:]:
            k, v = pair.split("=", 1)
            kw[k] = True if v == "true" else False if v == "false" else int(v) if v.lstrip("-").isdigit() else v
        print(json.dumps(s.call(a[1], **kw))[:4000 if a[0] == "kv" else 2000000])
    elif a[0] == "raw":
        print(json.dumps(s.call(a[1], **json.loads(a[2] if len(a) > 2 else "{}")))[:4000])
    elif a[0] == "schema":
        r = s.s.list_tools() if hasattr(s.s, "list_tools") else s.call("tools/list")
        for t in (r.get("tools") if isinstance(r, dict) else r) or []:
            if t.get("name") in a[1:]:
                print(t.get("name"), json.dumps(t.get("inputSchema") or t.get("parameters") or t)[:900])
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
