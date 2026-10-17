"""fw_walk_common.py -- shared helpers of the two OFFLINE-AUTHORED live walks objects_sheet.py and river_scenes_walk.py.

Nothing here talks to a game on its own: the walks hand it a water_scenes_walk.Walk. It holds
  * thing reading with the ROTATION READ BACK from the game (never assumed),
  * PIL labelling of a screenshot (large text, header band + per-item caption strip),
  * the index.html writer (one section per group, the owner's 'looks right / looks wrong / note' line per group),
  * traceback capture to a file (a crash is printed, kept, recorded; the walk goes on),
  * river-bank cell finding on a terrain map (pure, testable),
  * FakeGame, the OFFLINE bridge for --mock (proves the scripts' own paths, never anything about the game).
"""
import html
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WIN_FB = r"C:\Windows\Fonts\arialbd.ttf"
WIN_FR = r"C:\Windows\Fonts\arial.ttf"
ROT_NAMES = ("North", "East", "South", "West")


# ---------------------------------------------------------------- things / rotation
def norm_rot(v):
    """A rotation as the game reports it -> 0..3 (N,E,S,W), or None when unreadable. Accepts 0..3, 'North', 'N', 'Rot4:North'."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v) % 4 if 0 <= int(v) <= 3 else None
    s = str(v).strip().lower().replace("rot4:", "")
    for i, n in enumerate(ROT_NAMES):
        if s in (n.lower(), n[0].lower(), str(i)):
            return i
    return None


def thing_rot(t):
    for k in ("rotation", "rot", "rotInt", "facing", "rotationInt"):
        if k in t:
            return norm_rot(t[k])
    return None


def thing_cell(t):
    if "x" in t and "z" in t:
        return int(t["x"]), int(t["z"])
    for k in ("pos", "position", "cell"):
        p = t.get(k)
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p:
            return int(p["x"]), int(p.get("z", p.get("y", 0)))
    return None


def list_things(w, defs, rect):
    """[{def, cell, rot, raw}] for defName(s) in rect=(x,z,w,h); [] plus the reply's countMatched/countReturned kept in
    w.last_list so a truncated read is never taken for absence."""
    r = w.call("jawa/list_things", defName=",".join(defs), rect="%d,%d,%d,%d" % tuple(rect), limit=500) or {}
    w.last_list = {k: r.get(k) for k in ("countMatched", "countReturned", "scanned")}
    out = []
    for t in r.get("things") or []:
        out.append(dict(def_=t.get("defName") or t.get("def"), cell=thing_cell(t), rot=thing_rot(t), raw=t))
    return out


def place(w, defname, cell, rot=None, stuff=None, wipe=False):
    """build_batch one thing and READ IT BACK (list_things at the cell). Returns dict(def, asked, cell, rot_asked, rot_read,
    survived, note). rot_read is what the game says now; asked is only what we sent."""
    op = "%s:%d,%d" % (defname, cell[0], cell[1]) + ("" if rot is None else ",%d" % rot)
    kw = dict(ops=op, faction="player", wipeExisting=bool(wipe))
    if stuff:
        kw["stuff"] = stuff
    r = w.call("jawa/build_batch", **kw) or {}
    got = [t for t in list_things(w, [defname], (cell[0] - 2, cell[1] - 2, 5, 5)) if t["cell"] is not None]
    mine = [t for t in got if abs(t["cell"][0] - cell[0]) <= 1 and abs(t["cell"][1] - cell[1]) <= 1]
    t = mine[0] if mine else None
    note = ""
    if not mine:
        note = "not on the map after build_batch (reply: %s)" % str(r.get("failed") or r)[:300]
    elif t["rot"] is None:
        note = "game gave no rotation field (keys: %s)" % sorted(t["raw"].keys())
    return dict(def_=defname, asked=cell, rot_asked=rot, rot_read=(t or {}).get("rot"), survived=bool(mine), note=note)


def rot_text(r):
    return ROT_NAMES[r] if isinstance(r, int) and 0 <= r <= 3 else "UNREADABLE"


# ---------------------------------------------------------------- tracebacks
def keep_traceback(w, out_dir, name):
    """Print the current exception IN FULL, keep it at out_dir/<name>_traceback_<stamp>.txt, return the relative path."""
    tb = traceback.format_exc()
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "%s_traceback_%s.txt" % (name, time.strftime("%Y%m%dT%H%M%S")))
    with open(p, "w", encoding="utf-8") as f:
        f.write(tb)
    w.say("  CRASHED (traceback kept at %s):" % os.path.relpath(p, REPO))
    for line in tb.rstrip().splitlines():
        w.say("    " + line)
    return os.path.relpath(p, REPO), tb.rstrip().splitlines()[-1]


# ---------------------------------------------------------------- PIL labels
def _font(size, bold=False):
    from PIL import ImageFont
    for p in ((FB, WIN_FB) if bold else (FR, WIN_FR)):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(d, text, font, width):
    lines = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if d.textlength(t, font=font) <= width:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def label_image(src, dst, title, subtitle="", captions=()):
    """Screenshot src -> dst with a LARGE title band on top and one caption line per item below (left to right order of the
    staging). The picture is scaled to 1600 px wide first. Returns dst."""
    from PIL import Image, ImageDraw
    im = Image.open(src).convert("RGB")
    W = 1600
    im = im.resize((W, max(1, round(im.height * W / im.width))), Image.LANCZOS)
    ft, fs, fc = _font(64, True), _font(36), _font(32)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    pad = 24
    tl = _wrap(tmp, title, ft, W - 2 * pad)
    sl = _wrap(tmp, subtitle, fs, W - 2 * pad) if subtitle else []
    cl = []
    for c in captions:
        cl += _wrap(tmp, "- " + c, fc, W - 2 * pad)
    head = pad + len(tl) * 76 + (len(sl) * 46 + 8 if sl else 0) + pad // 2
    foot = (len(cl) * 42 + pad * 2) if cl else 0
    cv = Image.new("RGB", (W, head + im.height + foot), (250, 247, 240))
    d = ImageDraw.Draw(cv)
    y = pad
    for l in tl:
        d.text((pad, y), l, font=ft, fill=(30, 30, 30))
        y += 76
    for l in sl:
        d.text((pad, y), l, font=fs, fill=(0, 70, 140))
        y += 46
    cv.paste(im, (0, head))
    y = head + im.height + pad
    for l in cl:
        d.text((pad, y), l, font=fc, fill=(25, 25, 25))
        y += 42
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    cv.save(dst)
    return dst


def synthetic_png(path, w=1280, h=720, tag=""):
    """The mock's stand-in for a screenshot."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (96, 120, 70))
    d = ImageDraw.Draw(im)
    for i in range(0, w, 64):
        d.line([(i, 0), (i, h)], fill=(80, 100, 60))
    d.text((20, 20), "MOCK SCREENSHOT %s" % tag, font=_font(40, True), fill=(255, 255, 255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    return path


def snap(w, name, rect):
    """Screenshot a rect through the Walk (live: the game; mock: a synthetic image in the same folder). Returns the absolute
    png path, or None with the reason printed (never a silent None)."""
    import water_scenes_walk as m
    if getattr(w.args, "no_shots", False) and not getattr(w.args, "mock", False):
        return None
    if getattr(w.args, "mock", False):
        return synthetic_png(os.path.join(m.OUT, name + ".png"), tag=name)
    r = w.shot(name, rect)
    if not r or not str(r).endswith(".png"):
        w.say("         SCREENSHOT FAILED %s: %s" % (name, r))
        return None
    return os.path.join(REPO, r)


# ---------------------------------------------------------------- index.html
CSS = ("body{font:20px sans-serif;background:#2b2118;color:#eee;margin:20px auto;max-width:1700px;padding:0 16px}"
       "section{background:#faf7f0;color:#222;padding:16px 24px;margin:26px 0;border-radius:6px}"
       "img{width:100%;border:1px solid #888}h2{margin:0 0 6px}.ver{margin-top:12px;font-size:22px}"
       "td,th{padding:3px 14px 3px 0;text-align:left;vertical-align:top}.MATCHES{color:#0a6b1f;font-weight:bold}"
       ".DIFFERS,.CRASHED{color:#a40000;font-weight:bold}.UNMEASURED{color:#8a5a00;font-weight:bold}"
       ".cap{color:#04508c;font-weight:bold;margin:10px 0 4px}pre{white-space:pre-wrap;background:#eee;padding:8px;font-size:15px}")


def merge_groups(old, new, stamp=None):
    """Accumulate scene groups across runs: a group whose id is already there is REPLACED in place (the newest run of that
    scene wins, its position kept); a new id is appended. Each new group is stamped with the run that made it. Pure."""
    out = [dict(g) for g in (old or [])]
    pos = {g.get("id"): i for i, g in enumerate(out)}
    for g in new or []:
        g = dict(g)
        if stamp:
            g["stamp"] = stamp
        if g.get("id") in pos:
            out[pos[g["id"]]] = g
        else:
            pos[g.get("id")] = len(out)
            out.append(g)
    return out


def write_index(path, title, intro, groups, accumulate=True):
    """groups: list of dict(id, title, looking_at, check[], passif, fails, images[(relative png, caption)], readings[(status,
    text)], notes[], pre). One 'looks right / looks wrong / note' line per group, kept in localStorage and copyable as JSON.
    ACCUMULATES (2026-10-17: the river index showed only the last scene run): the groups of earlier runs are kept in
    <index>.groups.json beside it and merged by group id (merge_groups), so `go R2` after `go R1` leaves both. accumulate=
    False starts the index afresh (the walks' --reset-index)."""
    e = html.escape
    side = os.path.splitext(path)[0] + ".groups.json"
    old = []
    if accumulate and os.path.exists(side):
        try:
            with open(side, encoding="utf-8") as f:
                old = json.load(f)
        except (OSError, ValueError):
            old = []        # an unreadable sidecar is a fresh index, never a crash of the walk
    groups = merge_groups(old, groups, stamp=time.strftime("%Y-%m-%d %H:%M"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(side, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=1)
    h = ["<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>%s</title>"
         "<style>%s</style><h1>%s</h1><p>%s</p>" % (e(title), CSS, e(title), e(intro))]
    for g in groups:
        h.append("<section id='%s'><h2>%s</h2>%s" % (e(g["id"]), e(g["title"]),
                                                    ("<p><small>run %s</small></p>" % e(g["stamp"])) if g.get("stamp") else ""))
        if g.get("looking_at"):
            h.append("<p><b>What you are looking at.</b> %s</p>" % e(g["looking_at"]))
        if g.get("check"):
            h.append("<p><b>What to check</b></p><ul>%s</ul>" % "".join("<li>%s</li>" % e(c) for c in g["check"]))
        if g.get("passif") or g.get("fails"):
            h.append("<p><b>Pass if:</b> %s<br><b>Fails if:</b> %s</p>" % (e(g.get("passif", "")), e(g.get("fails", ""))))
        if g.get("readings"):
            h.append("<p><b>What the game measured</b></p><table>%s</table>" % "".join(
                "<tr><td class='%s'>%s</td><td>%s</td></tr>" % (e(s.split()[0]), e(s), e(t)) for s, t in g["readings"]))
        for rel, cap in g.get("images") or []:
            h.append("<div class=cap>%s</div><img src='%s' loading=lazy>" % (e(cap), e(rel)))
        for n in g.get("notes") or []:
            h.append("<p><i>%s</i></p>" % e(n))
        if g.get("pre"):
            h.append("<pre>%s</pre>" % e(g["pre"]))
        gid = e(g["id"])
        h.append("<p class=ver data-g='%s'>%s: <label><input type=radio name='r_%s' value=right> looks right</label> &nbsp; "
                 "<label><input type=radio name='r_%s' value=wrong> looks wrong</label> &nbsp; note: "
                 "<input size=60 class=note></p></section>" % (gid, gid, gid, gid))
    h.append("<p><button onclick='copyAll()'>Copy my answers as JSON</button> <span id=out></span></p>")
    h.append("""<script>
var K='fwwalk_'+location.pathname;
function load(){try{var s=JSON.parse(localStorage.getItem(K)||'{}');document.querySelectorAll('.ver').forEach(function(p){
var g=p.dataset.g,v=s[g]||{};p.querySelectorAll('input[type=radio]').forEach(function(r){r.checked=(v.verdict==r.value)});
p.querySelector('.note').value=v.note||''})}catch(e){}}
function collect(){var o={};document.querySelectorAll('.ver').forEach(function(p){var c=p.querySelector('input[type=radio]:checked');
o[p.dataset.g]={verdict:c?c.value:null,note:p.querySelector('.note').value}});return o}
function save(){try{localStorage.setItem(K,JSON.stringify(collect()))}catch(e){}}
function copyAll(){var t=JSON.stringify(collect(),null,1);document.getElementById('out').textContent=t.length+' chars copied';
try{navigator.clipboard.writeText(t)}catch(e){document.getElementById('out').textContent=t}}
document.addEventListener('change',save);document.addEventListener('input',save);load();
</script>""")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    return path


# ---------------------------------------------------------------- walk construction
def make_walk(args, out_dir):
    """A water_scenes_walk.Walk whose output folder is out_dir. --mock: the Walk gets FakeGame in place of the bridge."""
    import water_scenes_walk as m
    m.OUT = out_dir
    os.makedirs(out_dir, exist_ok=True)
    mock = getattr(args, "mock", False)
    if mock:
        args.mock_fail = None
    w = m.Walk(args)
    w.last_list = {}
    if mock:
        w.B = FakeGame()
    return w


# ---------------------------------------------------------------- river bank finding (pure)
def is_moving(t):
    return "Moving" in str(t or "")


def is_water(t):
    return "Water" in str(t or "") or "Marsh" in str(t or "")


def bank_cells(terrain, size, margin=12):
    """[(cell, rot)] where a moving-water cell has dry land on one cardinal side: rot is the Rot4 pointing from the water
    cell toward the dry side (N=0,E=1,S=2,W=3), in a stable order (nearest the map centre first). margin keeps the cells
    out of the map-edge sink band. A bank weir stands on the water cell's bank edge; the real PlaceWorker is the mod's, so
    these are CANDIDATES, each read back after placing."""
    w, h = size
    d4 = ((0, 1), (1, 0), (0, -1), (-1, 0))
    out = []
    for (x, z), t in terrain.items():
        if not is_moving(t) or not (margin <= x < w - margin and margin <= z < h - margin):
            continue
        for r, (dx, dz) in enumerate(d4):
            n = terrain.get((x + dx, z + dz))
            if n is not None and not is_water(n):
                out.append(((x, z), r))
    cx, cz = w / 2.0, h / 2.0
    out.sort(key=lambda it: ((it[0][0] - cx) ** 2 + (it[0][1] - cz) ** 2, it[0], it[1]))
    return out


def spread(cands, n, gap=7):
    """Up to n candidates, no two within `gap` cells (Chebyshev) of each other, in the given order."""
    pick = []
    for c, r in cands:
        if all(max(abs(c[0] - p[0][0]), abs(c[1] - p[0][1])) >= gap for p in pick):
            pick.append((c, r))
            if len(pick) >= n:
                break
    return pick


def read_terrain(w, size, band=64):
    """{(x,z): top terrain defName} of the whole map in bands of `band` rows (one get_terrain_batch per band). None if refused."""
    import site_spec as S
    out = {}
    W, H = size
    for z in range(0, H, band):
        r = w.call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z, W, min(band, H - z))) or {}
        if not r.get("success"):
            w.say("         get_terrain_batch refused at z=%d: %s" % (z, str(r)[:160]))
            return None
        out.update(S.parse_ops(r.get("ops")))
    return out


def map_size(w):
    mi = w.call("jawa/map_info") or {}
    return int(mi.get("sizeX") or 250), int(mi.get("sizeZ") or mi.get("sizeY") or 250)


def centroid_rect(cells, w_, h_, size):
    """A (x,z,w,h) rect w_ x h_ centred on the cells' mean, clamped inside the map."""
    cx = sum(c[0] for c in cells) // max(1, len(cells))
    cz = sum(c[1] for c in cells) // max(1, len(cells))
    x = max(0, min(size[0] - w_, cx - w_ // 2))
    z = max(0, min(size[1] - h_, cz - h_ // 2))
    return (x, z, w_, h_)


# ---------------------------------------------------------------- the offline fake game
class FakeGame(object):
    """OFFLINE bridge for --mock. Remembers terrain, built things (with their rotation, a ladder turned to its wall like the
    real RM_Building_Ladder), staged colonists (a river cell carries them east one cell per 60 ticks unless on a ford), and
    answers the walks' proofs with plausible strings. It proves the scripts' own code paths and nothing about the game."""

    MAP = (250, 250)

    def __init__(self):
        self.tick = 0
        self.depth = {}
        self.fill = {}
        self.terrain = {}
        self.things = []       # dict(id, defName, x, z, rot)
        self.pawns = {}        # id -> [x, z]
        self.ladders_raised = {}
        self.next_id = 100
        self.pulse = 0
        self.swept = 0
        self.gone = []
        self.has_river = True
        # a river running east-west through the map centre: moving shallow water rows z=120..123, bank land beside
        for x in range(self.MAP[0]):
            for z in range(120, 124):
                self.terrain[(x, z)] = "WaterMovingShallow" if z in (121, 122) else "WaterMovingChestDeep"

    # -- helpers
    def _terr(self, c):
        return self.terrain.get(c, "Soil")

    def _wall_rot(self, x, z, rot):
        """Mirror of RM_LadderWallMath: keep rot if it faces a shallower neighbour, else the biggest drop."""
        d4 = ((0, 1), (1, 0), (0, -1), (-1, 0))
        here = self.depth.get((x, z), 0)

        def drop(r):
            dx, dz = d4[r]
            return here - self.depth.get((x + dx, z + dz), 0)
        if rot is not None and drop(rot) > 0:
            return rot
        best = max(range(4), key=drop)
        return best if drop(best) > 0 else (rot or 0)

    # -- transport
    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            return self._static(kw.get("type", ""), kw.get("method"), kw.get("args") or "")
        if tool == "jawa/flowworks_engine_state":
            return {"success": True, "ticksGame": self.tick}
        if tool == "jawa/mod_settings_field":
            return {"success": True, "value": "250" if kw.get("field") == "pulseIntervalTicks" else kw.get("value", "True")}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            self.depth[c] = self.depth.get(c, 0) + int(kw.get("deepenLevels") or 0)
            if int(kw.get("setFill", -1)) >= 0:
                self.fill[c] = int(kw["setFill"])
            return {"success": True}
        if tool == "jawa/set_terrain_batch":
            for op in str(kw.get("ops") or "").split(";"):
                if not op:
                    continue
                name, nums = op.split(":")
                p = [int(v) for v in nums.split(",")] + [1, 1]
                for i in range(p[2]):
                    for j in range(p[3]):
                        self.terrain[(p[0] + i, p[1] + j)] = name
            return {"success": True}
        if tool == "jawa/get_terrain_batch":
            ops = []
            for rect in str(kw.get("rects") or "").split(";"):
                x, z, w, h = [int(v) for v in rect.split(",")]
                for i in range(w):
                    for j in range(h):
                        ops.append("%s:%d,%d,1,1" % (self._terr((x + i, z + j)), x + i, z + j))
            return {"success": True, "ops": ";".join(ops)}
        if tool in ("jawa/build_batch", "jawa/spawn_batch"):
            n = 0
            for op in str(kw.get("ops") or "").split(";"):
                if not op:
                    continue
                name, nums = op.split(":")
                p = [int(v) for v in nums.split(",")]
                rot = p[2] if len(p) > 2 else 0
                if name == "RM_Ladder":
                    rot = self._wall_rot(p[0], p[1], rot)
                self.next_id += 1
                self.things.append(dict(id=self.next_id, defName=name, x=p[0], z=p[1], rotation=ROT_NAMES[rot]))
                n += 1
            return {"success": True, "placed": n, "survived": n}
        if tool == "jawa/list_things":
            defs = set(str(kw.get("defName") or "").split(","))
            x, z, w, h = [int(v) for v in str(kw.get("rect") or "0,0,999,999").split(",")]
            hit = [t for t in self.things if t["defName"] in defs and x <= t["x"] < x + w and z <= t["z"] < z + h]
            return {"success": True, "things": hit, "countMatched": len(hit), "countReturned": len(hit), "scanned": 1000}
        if tool == "jawa/destroy_batch":
            self.things = []
            return {"success": True}
        if tool == "jawa/spawn_pawn":
            self.next_id += 1
            self.pawns[self.next_id] = [kw["x"], kw["z"]]
            return {"success": True, "pawns": [{"id": self.next_id}]}
        if tool == "jawa/pawn_force_incapacitate":
            self.pawns.pop(kw.get("pawn"), None)
            return {"success": True}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": i, "isPlayer": True, "dead": False} for i in self.pawns]}
        if tool == "jawa/map_info":
            return {"success": True, "sizeX": self.MAP[0], "sizeZ": self.MAP[1], "tile": 1234}
        if tool == "rimworld/get_ui_state":
            return {"success": True, "programState": "Playing"}
        return {"success": True}

    def probe_of(self, probe_type, cmd, wait_s=20.0, poll_s=0.3):
        if cmd == "colonists":
            return {"success": True, "pawns": [{"id": i, "pos": list(p)} for i, p in self.pawns.items()]}
        return {"success": True}

    def ticks(self, n):
        before = self.tick // 60
        self.tick += int(n)
        for _ in range(self.tick // 60 - before):
            for i, p in self.pawns.items():
                c = tuple(p)
                if is_moving(self._terr(c)) and self._terr(c) != "RM_FordStones":
                    p[0] = min(self.MAP[0] - 1, p[0] + 1)
                    if p[0] >= self.MAP[0] - 1:
                        self.gone.append(i)
                        self.swept += 1
            for i in self.gone:
                self.pawns.pop(i, None)
        return {"success": True, "advanced": n}

    # -- proofs
    def _static(self, typ, method, arg):
        if method == "ProofFluidRow":
            x, z, w, h = map(int, arg.split(","))
            cells = "".join("%d,%d:%d/%d/x/%s;" % (x + i, z + j, self.depth.get((x + i, z + j), 0),
                                                   self.fill.get((x + i, z + j), 0), self._terr((x + i, z + j)))
                            for j in range(h) for i in range(w))
            return {"success": True, "result": "ROW pulse=%d viscosity=True %s" % (self.pulse, cells)}
        if method == "ProofLadder":
            p = arg.split(",")
            c, op = (int(p[0]), int(p[1])), (p[2] if len(p) > 2 else "read")
            if not any(t["defName"] == "RM_Ladder" and (t["x"], t["z"]) == c for t in self.things):
                return {"success": True, "result": "LADDER cell=%d,%d present=False raised=None inspect=none" % c}
            if op == "raise":
                self.ladders_raised[c] = True
            elif op == "lower":
                self.ladders_raised[c] = False
            return {"success": True, "result": "LADDER cell=%d,%d present=True raised=%s inspect=Hangs_on_wall" % (
                c[0], c[1], bool(self.ladders_raised.get(c)))}
        if method in ("ProofResetRect",):
            return {"success": True, "result": "ok"}
        if method == "ProofGrid":
            return {"success": True, "result": "GRID current=480 fast=96 edge=120"}
        if method == "ProofShove":
            return {"success": True, "result": "MOVED 0" if arg.startswith("ford") else "MOVED 4"}
        if method == "ProofSwept":
            if arg == "return":
                for i in self.gone:
                    self.pawns[i] = [self.MAP[0] - 12, 121]
                self.gone, self.swept = [], 0
                return {"success": True, "result": "SWEPT pending=0 returned=1"}
            return {"success": True, "result": "SWEPT pending=%d" % self.swept}
        if method == "ProofWeirPlace":
            return {"success": True, "result": "PLACE edge=True dry=False wet=False"}
        if method == "ProofWeirPool":
            return {"success": True, "result": "POOL arrestedWet=True dropped=5 upstream=9"}
        if method == "ProofWeirJoin":
            return {"success": True, "result": "JOIN placeOk=True run=2 headIsBank=True joint=True poolSingle=6 poolJoined=9 poolGap=0"}
        if method == "ProofReport":
            return {"success": True, "result": "PLACER poolCount=3 got=2 drawMatches=True inPool=True off=sluice=off stock=11.2 panned=0"}
        return {"success": True, "result": "ok"}
