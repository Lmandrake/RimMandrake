"""Site / pawn / camera / read primitives (Graffiti trial plan section 6, items 3-6, 13, 15).

Everything here is built ONLY on bridge tools that exist today (checked against
src/RimMandrake/bridgetools/JawaBench.BridgeTools [Tool] names). Every write is followed by an
independent read; a read that cannot be completed raises `Unmeasured` -- never PASS, never "zero".
Response shapes are mirrored in transport.MockGame and are UNPROVEN live until the first live run.

NOT buildable from existing tools (needs a new JawaBench [Tool]; listed in NEEDED_TOOLS):
see the constant at the bottom. Plan 6.7/6.12/6.14.
"""
import contextlib
import os
import shutil
import time

from northstar_driver.bars import Unmeasured


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        raise Unmeasured("%s failed or unreadable: %s" % (what, str(r)[:160]))
    return r


def rect_str(r):
    return "%d,%d,%d,%d" % tuple(r)


# ------------------------------------------------------------------ site primitives (plan 6.3)

def clear_rect(s, rect, margin=0):
    x, z, w, h = rect
    big = (x - margin, z - margin, w + 2 * margin, h + 2 * margin)
    _ok(s.call("jawa/destroy_batch", rects=rect_str(big), categories="All"), "destroy_batch")
    left = _ok(s.call("jawa/list_things", rect=rect_str(big), limit=500), "list_things")
    if left.get("isCompleteList") is False:
        raise Unmeasured("list_things truncated after clear -- cannot prove the rect is empty")
    # terrain/blueprints stay; Things must be gone
    stray = [t.get("def") or t.get("defName") for t in left.get("things") or []]
    if stray:
        raise AssertionError("clear_rect left %d thing(s): %s" % (len(stray), sorted(set(stray))[:6]))
    return big


def set_terrain_rect(s, rect, terrain):
    _ok(s.call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, rect_str(rect))), "set_terrain_batch")
    got = _ok(s.call("jawa/get_terrain_batch", rects=rect_str(rect)), "get_terrain_batch")
    cells = got.get("cells")
    if cells is not None and any(c != terrain for c in cells):
        raise AssertionError("terrain read-back differs from %s over %s" % (terrain, rect))
    if cells is None and terrain not in str(got):
        raise Unmeasured("get_terrain_batch shape not understood: %s" % str(got)[:120])
    return got


def spawn_wall_run(s, x, z, length, stuff="Steel"):
    ops = ";".join("Wall:%d,%d" % (x + i, z) for i in range(length))
    _ok(s.call("jawa/spawn_batch", ops=ops, stuff=stuff), "spawn_batch")
    got = things_by_defs(s, ["Wall"], (x, z, length, 1))
    if len(got) != length:
        raise AssertionError("wall run %d,%d len %d: read back %d" % (x, z, length, len(got)))
    return got


def unfog(s, rect):
    _ok(s.call("jawa/set_fog", action="unfog", rect=rect_str(rect)), "set_fog")


def unroof(s, rect):
    _ok(s.call("jawa/set_roof_batch", ops=rect_str(rect), roofDef="None"), "set_roof_batch")
    r = _ok(s.call("jawa/get_roof_batch", rects=rect_str(rect)), "get_roof_batch")
    # the real answer carries `roofs` (distinct roof names, "None" = open sky), not a `roofedCells` count (LIVE 2026-10-03)
    if r.get("roofedCells") or any(x not in (None, "None") for x in (r.get("roofs") or [])):
        raise AssertionError("roofed cell(s) remain in %s: %s" % (rect, r.get("roofedCells") or r.get("roofs")))


def weather_lock(s, weather="Clear"):
    _ok(s.call("jawa/weather_set", weather=weather, lockWeather=True), "weather_set")
    got = _ok(s.call("jawa/weather_get"), "weather_get")
    cur = got.get("weather") or got.get("current")
    if isinstance(cur, dict):
        cur = cur.get("current") or cur.get("defName")
    if cur != weather:
        raise AssertionError("weather read-back %r != %r" % (cur, weather))


def pin_time(s, lo_hour=10, hi_hour=14, ticks_per_hour=2500):
    """Time only moves FORWARD (plan 3.14). Returns the hour read; sets only if outside the window."""
    clk = _ok(s.call("jawa/time_clock"), "time_clock")
    hour = clk.get("hour")
    if hour is None:
        raise Unmeasured("time_clock has no hour field: %s" % str(clk)[:120])
    if lo_hour <= hour < hi_hour:
        return hour
    delta_h = (12 - hour) % 24
    s.call("jawa/time_set_ticks", ticks=int(clk["ticksGame"]) + int(delta_h * ticks_per_hour))
    return _ok(s.call("jawa/time_clock"), "time_clock").get("hour")


# ------------------------------------------------------------------ pawn primitives (plan 6.4)

def spawn_colonists(s, n, x, z, kind="Colonist"):
    ids = []
    for _ in range(n):
        r = _ok(s.call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="player", count=1), "spawn_pawn")
        row = (r.get("pawns") or [{}])[0]
        if not row.get("id"):
            raise AssertionError("spawn_pawn returned no id")
        ids.append(row["id"])
    return ids


def prepare_painter(s, pid, artistic=8):
    s.call("jawa/pawn_health", pawn=pid, action="restore", confirmDestructive=True)
    for need in ("Food", "Rest", "Joy"):
        s.call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
    s.call("jawa/set_pawn_skill", pawn=pid, skill="Artistic", level=artistic)
    s.call("jawa/set_draft", pawnId=pid, draft=False)


def set_work_priority_all(s, work_type, priority=0):
    r = _ok(s.call("jawa/list_pawns", limit=500), "list_pawns")
    ids = [p["id"] for p in r.get("pawns") or [] if p.get("id")]
    for pid in ids:
        s.call("jawa/set_work_priority", pawnId=pid, workType=work_type, priority=priority)
    return ids


def remove_rect_from_home(s, rect):
    _ok(s.call("jawa/paint_area", area="Home", ops=rect_str(rect), value=False), "paint_area")


def despawn_pawns_in(s, rect):
    """Kill every living pawn in rect. jawa/destroy_batch never removes pawns
    (DESTROY_BATCH_NEVER_KILLS_PAWNS_1), so kill each by id with jawa/damage. Returns the count killed."""
    x, z, w, h = rect
    r = _ok(s.call("jawa/list_pawns", limit=500), "list_pawns")
    n = 0
    for p in r.get("pawns") or []:
        if p.get("dead") or not p.get("id") or p.get("x") is None or p.get("z") is None:
            continue
        if not (x <= p["x"] < x + w and z <= p["z"] < z + h):
            continue
        _ok(s.call("jawa/damage", damageDef="Bullet", amount=5000, thingId=p["id"], allowColonists=True), "damage(kill)")
        n += 1
    return n


# ------------------------------------------------------------------ reads (plan 6.6)

def things_by_defs(s, defs, rect, limit=500):
    """Things of ANY of `defs` in rect. Truncated/failed reads raise -- never 'zero'."""
    r = _ok(s.call("jawa/list_things", defName=",".join(defs), rect=rect_str(rect), limit=limit), "list_things")
    if r.get("isCompleteList") is False:
        raise Unmeasured("list_things truncated (%s of %s)" % (r.get("countReturned"), r.get("countMatched")))
    return r.get("things") or []


def get_defs_checked(s, spec):
    """`defs` is a STRING 'DefType/DefName' (a list raises InvalidCastException)."""
    if not isinstance(spec, str):
        raise TypeError("jawa/get_defs takes defs as a STRING 'DefType/DefName'")
    r = s.call("jawa/get_defs", defs=spec)
    if not isinstance(r, dict) or r.get("success") is not True:
        raise Unmeasured("get_defs(%s) failed: %s" % (spec, str(r)[:120]))
    if r.get("notFound"):
        raise AssertionError("get_defs(%s): notFound %s" % (spec, r["notFound"]))
    return r


def thing_stat(s, thing_id, stat):
    r = _ok(s.call("jawa/thing_stats", thing=thing_id, stats=stat), "thing_stats")
    for th in r.get("things") or []:
        for st in th.get("stats") or []:
            if st.get("defName") == stat:
                return float(st["value"])
    raise Unmeasured("thing_stats returned no %s for %s" % (stat, thing_id))


def dlc_status(s, want=("Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")):
    r = _ok(s.call("jawa/dlc_status"), "dlc_status")
    blob = str(r).lower()
    missing = [d for d in want if d.lower() not in blob]
    # the tool answers `<dlc>Active: bool`; naming a DLC is not proof it is active
    off = [d for d in want if r.get(d.lower() + "Active") is False]
    if off:
        raise AssertionError("DLC not active in the running game: %s" % off)
    if missing:
        raise Unmeasured("dlc_status does not name %s: %s" % (missing, blob[:160]))
    return r


@contextlib.contextmanager
def setting_restored(s, type_name, field, default):
    """Flip a Mod Settings field for a block and ALWAYS restore + re-read the shipped default."""
    def get():
        return _ok(s.call("jawa/mod_settings_field", typeName=type_name, action="get", field=field),
                   "mod_settings_field(get)").get("value")
    try:
        yield get
    finally:
        s.call("jawa/mod_settings_field", typeName=type_name, action="set", field=field, value=str(default))
        if str(get()) != str(default):
            raise AssertionError("setting %s did not restore to %r" % (field, default))


def read_settings(s, type_name, expect):
    """Pre-flight: every field equals its shipped default; returns the mismatches."""
    bad = {}
    for f, v in expect.items():
        got = _ok(s.call("jawa/mod_settings_field", typeName=type_name, action="get", field=f),
                  "mod_settings_field(get)").get("value")
        if str(got) != str(v):
            bad[f] = got
    return bad


def log_offset(player_log):
    """Byte offset BEFORE launch; `defs_load_clean` reads from here, not from the first bridge call."""
    return os.path.getsize(player_log)


def read_log_since(player_log, offset, needles):
    with open(player_log, "rb") as f:
        f.seek(offset)
        txt = f.read().decode("utf-8", "replace")
    return [ln for ln in txt.splitlines() if any(n in ln for n in needles)]


# ------------------------------------------------------------------ camera / image (plan 6.5, 6.15)

def frame_rect(s, rect, padding=1):
    r = _ok(s.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3],
                   paddingCells=padding), "screenshot_cell_rect")
    return r.get("path")


def camera_state(s):
    return _ok(s.call("rimworld/get_camera_state"), "get_camera_state")


def clear_ui_and_log(s):
    s.call("jawa/clear_ui", all=True)
    s.call("jawa/window_list_close", action="close", typeName="EditWindow_Log")


def copy_for_judge(path, run_id, component, root):
    dst_dir = os.path.join(root, "Transient", "modcheck", "graffiti", run_id)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, component + ".png")
    shutil.copyfile(path, dst)
    return dst


def luminance(png):
    from PIL import Image, ImageStat
    return ImageStat.Stat(Image.open(png).convert("L")).mean[0]


def black_frame_guard(png, floor=8.0):
    m = luminance(png)
    if m < floor:
        raise AssertionError("frame mean luminance %.1f < %.1f: black/blank frame" % (m, floor))
    return m


def crop_roi(png, out, box):
    from PIL import Image
    Image.open(png).crop(box).save(out)
    return out


def burn_caption(png, out, lines):
    from PIL import Image, ImageDraw
    im = Image.open(png).convert("RGB")
    band = 14 * len(lines) + 6
    canvas = Image.new("RGB", (im.width, im.height + band), (0, 0, 0))
    canvas.paste(im, (0, 0))
    d = ImageDraw.Draw(canvas)
    for i, ln in enumerate(lines):
        d.text((4, im.height + 3 + 14 * i), ln, fill=(255, 255, 255))
    canvas.save(out)
    return out


def px_per_cell(png, marker_rgb, cells_apart, tol=40):
    """Pixel distance between the centroids of two marker blobs, / cells_apart (>=2 distinct blobs
    split by column gap). Calibrates 'play zoom' on the PNG (plan 3.9), never on a camera setting."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    xs = [x for x in range(im.width) for y in range(0, im.height, 4)
          if all(abs(a - b) <= tol for a, b in zip(im.getpixel((x, y)), marker_rgb))]
    if len(set(xs)) < 2:
        raise Unmeasured("marker colour %s not found in %s" % (marker_rgb, png))
    xs = sorted(set(xs))
    split = max(range(1, len(xs)), key=lambda i: xs[i] - xs[i - 1])
    left, right = xs[:split], xs[split:]
    return ((sum(right) / len(right)) - (sum(left) / len(left))) / float(cells_apart)


def nonce_canary_image(out, nonce):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (480, 120), (255, 255, 255))
    ImageDraw.Draw(im).text((10, 50), nonce, fill=(0, 0, 0))
    im.save(out)
    return out


# ------------------------------------------------------------------ NOT buildable today

NEEDED_TOOLS = {
    "jawa/thing_graphic": "for a spawned thing: resolved Graphic path / mainTexture.name (BadTex detection) and its "
                          "Graphic_Random variant index/path. Plan 6.7, textures_resolve, exact variant coverage.",
    "jawa/spawn_variant": "spawn a Graphic_Random thing pinned to variant k (set subgraphic, or reroll thingID "
                          "until the resolved path matches, capped); returns the resolved path. Plan 6.12.",
    "jawa/running_mods": "LoadedModManager.RunningModsListForReading ids+order, plus assembly Location and MVID "
                         "of a named assembly (RimMandrakeGraffiti). Plan 3.14 / 6.14.",
    "jawa/glow_at": "GameGlowAt(cell) for the light-band check (deepfire/glow_at exists but is a mod tool).",
    "jawa/site_state": "one call: auto-home on/off, storyteller+incident disable, snow depth/season over a rect, "
                       "every pawn's current job target. Plan 3.5/3.14/6.14 (jawa/pawn_get covers jobs per pawn).",
}
