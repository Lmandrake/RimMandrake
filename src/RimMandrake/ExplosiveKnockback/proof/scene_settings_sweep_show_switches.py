"""scene_settings_sweep_show_switches.py - Explosive Knockback 0.2.0, sc_settings_sweep_show: the show's switches in the game.

CONTRACT. Bar blast_show_switches_off_clean (design/concepts/ExplosiveKnockback/record.json): "Each part of the blast show
has its own on/off switch in Mod Settings, all on by default. With every switch off, a blast looks as it does in the
unmodded game, and the throws are the same with the show on or off." The plan's answer for every switch setting is
decided offline (T_SETTINGS_SWEEP_SHOW, selftest_explosiveknockback_settings_sweep.py --half show). This scene reads what
only the game can show:
  1. a real blast with each built switch off in turn, then all off: the switched-off part is absent and the others are
     present; with all off, vanilla's own mark comes back and nothing of ours is drawn;
  2. one colonist thrown twice on a like pad, show on against show off: the same landing offset, the same cells and the
     same mass (the throw reads no show switch).
Smoke, soot on things and soot on pawns are not built and have no switch (RM_KnockbackShow.Switches() hands them
`false`); their rows join when they are built. Kind A, a fresh quicktest map on ArchSmall, one clean station; no raid,
no hostile pawn.

PLANTS that must go red:
  --plant switches_ignored   no switch is written: S_SCAR and S_SHAKE FAIL on every off pad and S_ALL_OFF FAILS
                             (our scar and kick stay, vanilla's mark stays away), which shows that the rows can see.
  --plant unlike_pad         the show-off blast is set off 3 cells from the colonist, not 2: T_LIKE_PAD FAILS, and
                             T_SAME_THROW FAILS (or T_THROWN off, if 3 cells is past the 2.9-cell radius), which
                             shows that the throw rows can tell two throws apart.

    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_settings_sweep_show_switches.py
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_settings_sweep_show_switches.py --plant switches_ignored
    python.exe src\\RimMandrake\\Utils\\scene.py accept src\\RimMandrake\\ExplosiveKnockback\\proof\\scene_settings_sweep_show_switches.py --plant unlike_pad

Pads (each Shell_HighExplosive, Bomb, radius 2.9, on Soil, 12 cells apart so no blast reaches the next shell; radius and
type read from Core's Items_Resource_Shell.xml, which also gives the shell its vanilla
<preExplosionSpawnSingleThingDef>Filth_BlastMark</preExplosionSpawnSingleThingDef>):
  all_on      every switch on (the default): the control
  off_fire    showFireAndFlash off     off_shake   showScreenShake off
  off_ripple  showAirRipple off        off_scar    showCraterScars off
  all_off     the four built switches off: the unmodded look
  throw lane  Soil, 80 x 13 cells; each throw is a 1-damage Bomb blast (jawa/explosion_at, radius 2.9) 2 cells west of
              the colonist, with blast power from damage off, so it throws at full force and harms nobody

Rows (each prints PASS or FAIL with what it read, the count of cases and the limit):
  S_SCAR <pad>    our RM_KnockbackBlastCrater_* filth present iff showCraterScars is on; Filth_BlastMark present iff off
  S_SHAKE <pad>   RM_KnockbackShow.lastShakeTick moved by the blast iff showScreenShake is on
  S_ALL_OFF       all_off: no scar of ours, at least one Filth_BlastMark, no kick of ours
  T_THROWN <on|off> exactly one journal launch line for the colonist after its blast
  T_LIKE_PAD      both throws start 2 cells east of their shell (the lane is staged Soil; no terrain path is reviewed)
  T_SAME_MASS     the journal's launch mass is the same for both throws (else the throws cannot be compared)
  T_SAME_THROW    launch offset (to - from), cells travelled and landing offset (land at - from) equal, show on and off
  SHOTS           <pad>_blast right after each blast, <pad>_settled after 300 ticks: fire, flash and ripple are flecks,
                  which no reader reaches; the art judge (design/RimMandrake/art_judge_brief.md) reads in each picture
                  the part that must be absent and the ones that must be present (the JUDGE line lists them)

UNRUN until Stage 6: written 2026-11-24 by RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_SIX_BARS_LEFT and never run live.
Open points for the first run: jawa/mod_settings_field set is a changing raw call, so the run is stamped EXPLORED and
counts for no bar until the switches have a typed hand (s.act.tune is NOT_BUILT for mod settings; scene_blast_show has
the same point); whether s.act.place takes station-relative cells like s.stage (T_LIKE_PAD reads the placed shell back
and FAILS with the cells it read if not); whether "static:...RM_KnockbackJournal" path "lines" returns the list of
strings (if not, the T_ rows FAIL with the state read, never pass); and whether the off-screen capture draws flecks (if
not, the _blast shots are taken on screen with rimworld/jump_camera_to_cell).
"""
import json

import scene
from scene import cond as c

GAME = "ArchSmall"
# a stage save (stage_map.py make ArchSmall --kind settlement --save RM_Stage_ExplosiveKnockback): every roof and
# destroyable thing cleared. A fixed station on a fresh quicktest map can lie under mountain roof: on 2026-11-24 the
# colonist was gone by tick 3 under collapsed rocks and the stack buried (APPARATUS FAULT of the first run).
STAGE = "RM_Stage_ExplosiveKnockback"
NS = "RimMandrake.ExplosiveKnockback."
SETTINGS = NS + "RimMandrakeExplosiveKnockbackSettings"
SHOW = NS + "RM_KnockbackShow"
JOURNAL = NS + "RM_KnockbackJournal"
SWITCHES = ("showFireAndFlash", "showScreenShake", "showAirRipple", "showCraterScars", "showSmoke", "showSootOnThings",
            "showSootOnPawns")   # RM_KnockbackMod.cs fields; the last three were built after this scene was written and have
                                 # no single-off pad yet: they are switched with "all off" and the show-off throw
SHELL = "Shell_HighExplosive"
STATION = (20, 20, 100, 40)
HALF = 4                 # a pad is its centre +-4 cells: the 2.9-cell blast and our widest HE scar (7 cells) fit inside
SETTLE = 300             # ticks after each show blast: every fleck of the show is gone in under 2 s (120 ticks)
THROW_SETTLE = 600       # ticks after each throw: flight and landing, plus the 120-tick recovery window
                         # (RimMandrakeExplosiveKnockbackSettings.recoveryWindowTicks = 120) with room to spare
GAP = 2                  # the colonist stands 2 cells east of its shell: inside the 2.9-cell radius
# pad -> (centre relative to the station's corner, the switches turned off for its blast)
PADS = {
    "all_on": ((66, 6), ()),
    "off_fire": ((6, 6), ("showFireAndFlash",)),
    "off_shake": ((18, 6), ("showScreenShake",)),
    "off_ripple": ((30, 6), ("showAirRipple",)),
    "off_scar": ((42, 6), ("showCraterScars",)),
    "all_off": ((54, 6), SWITCHES),
}
ORDER = ["all_on", "off_fire", "off_shake", "off_ripple", "off_scar", "all_off"]
LANE = (4, 20, 80, 13)   # the throw lane, relative to the station's corner
THROW_SHELL = (10, 26)
COLONIST = (THROW_SHELL[0] + GAP, THROW_SHELL[1])
PART_OF = {"showFireAndFlash": "fire, fireball, sparks, thrown bits and our flash",
           "showScreenShake": "our camera kick", "showAirRipple": "the air ripple ring",
           "showCraterScars": "our crater scar (vanilla's blast mark instead)"}

show = scene.contract(
    claim="each built show switch turns off its own part only; all off is the unmodded look; the throw is the same "
          "with the show on or off",
    kind="A",
    exposure=c.state("all_off_x", "positionInt") == "gone",
    success=[c.played(THROW_SETTLE)],             # c.played counts the judged run only: the last throw's settle
    forbidden=[],
    end=THROW_SETTLE, limit=len(ORDER) * SETTLE + 2 * THROW_SETTLE + 900)


def rect(centre, h=HALF):
    x, z = centre
    return (STATION[0] + x - h, STATION[1] + z - h, 2 * h + 1, 2 * h + 1)


def lane_rect():
    return (STATION[0] + LANE[0], STATION[1] + LANE[1], LANE[2], LANE[3])


def cell(v):
    """-> (x, z) in map cells from a positionInt Value ("x,y,z"), or None."""
    if v.state != "ok":
        return None
    try:
        p = [int(float(t)) for t in str(v.v).strip("() ").split(",")]
        return (p[0], p[1]) if len(p) == 2 else (p[0], p[2])    # the bridge reads positionInt back as "x,z"
    except (ValueError, IndexError):
        return None


def scars_on(s, centre):
    """-> (count of our crater filth, count of vanilla blast marks) on a pad."""
    names = [str(v.v) for v in s.read_many(rect=rect(centre), path="def.defName") if v.state == "ok"]
    return sum(n.startswith("RM_KnockbackBlastCrater_") for n in names), names.count("Filth_BlastMark")


def read_field(s, field, of=SETTINGS):
    """Read one static field; -> its value as text, or None when it could not be read."""
    r = s.raw("jawa/mod_settings_field", typeName=of, action="get", field=field)
    v = (r or {}).get("value") if isinstance(r, dict) else None
    return None if v is None else str(v)


def setting(s, field, value, of=SETTINGS):
    """Set one static field (only inside the session's try, whose finally puts every switch back)."""
    s.raw("jawa/mod_settings_field", typeName=of, action="set", field=field, value=value)
    return value


def shake_tick(s):
    v = read_field(s, "lastShakeTick", of=SHOW)
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None



# The journal is a static list: it outlives a load. Every run of a scene loads the same stage save, so its thing ids and
# ticks repeat, and a filter on tick or id cannot tell this run's records from the last run's. mark_journal keeps the
# last line already there when the session opens; since_mark keeps only the lines after it (the list trims its oldest
# 1000 lines at 4000, so the mark is a line's text, not a position; a mark trimmed away means every line is this run's).
_MARK = []


def mark_journal(s):
    v = s.read("static:" + JOURNAL, "lines")
    lines = list(v.v) if v.state == "ok" and isinstance(v.v, (list, tuple)) else []
    _MARK[:] = [lines[-1] if lines else None, len(lines)]
    print("INFO journal mark: %d line(s) before this run" % len(lines))


def since_mark(raw):
    raw = list(raw)
    if not _MARK or _MARK[0] is None:
        return raw
    last, n = _MARK
    # by position while the list has not trimmed (the line before the cut is still the mark); a run on the same save
    # writes lines identical to the last run's, so the mark's text alone can cut inside this run's own lines
    if 0 < n <= len(raw) and raw[n - 1] == last:
        return raw[n:]
    for i in range(min(n, len(raw)) - 1, -1, -1):   # trimmed: the mark moved toward the front, never past position n
        if raw[i] == last:
            return raw[i + 1:]
    return raw


def journal(s):
    """-> (list of journal records, None) or (None, the state that was read)."""
    v = s.read("static:" + JOURNAL, "lines")
    if v.state != "ok":
        return None, "journal %s" % v.state
    raw = since_mark(v.v if isinstance(v.v, (list, tuple)) else str(v.v).splitlines())
    recs = []
    for line in raw:
        line = str(line).strip()
        if line.startswith("{"):
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass
    return recs, None


def throw(s, after_tick, pawn_id):
    """-> dict(launch, land) of the colonist's throw after a tick, from the journal, or dict(cause=...)."""
    recs, cause = journal(s)
    if recs is None:
        return dict(cause=cause)
    try:
        pid = str(int(float(pawn_id)))   # an id reads back as a float (88274.0)
    except (TypeError, ValueError):
        return dict(cause="the colonist's id could not be read: %r" % (pawn_id,))
    mine = [r for r in recs if str(r.get("thing", "")).endswith(pid) and int(r.get("tick", -1)) >= after_tick]
    launch = [r for r in mine if r.get("type") == "launch"]
    land = [r for r in mine if r.get("type") == "land"]
    if len(launch) != 1:
        return dict(cause="%d launch line(s) for the colonist after tick %d (want 1)" % (len(launch), after_tick))
    return dict(launch=launch[0], land=land[0] if land else None)


planted = scene.plant()
def sweep(s, rows, throws, before):
    """The pads with each switch off in turn and all off, then the colonist thrown show-on and show-off. Every switch is
    put back on every exit path."""
    kick0 = read_field(s, "lastShakeTick", of=SHOW)
    try:
        r = s.raw("jawa/mod_settings_field", typeName=SHOW, action="set", field="lastShakeTick", value="-1")
        print("INFO kick tick reset to -1: %s" % ({k: (r or {}).get(k) for k in ("success", "valueBefore", "valueAfter", "error")},))
        for pad in ORDER:
            centre, off = PADS[pad]
            for f in SWITCHES:
                if planted != "switches_ignored":
                    setting(s, f, "False" if f in off else "True")
            # the show shakes the camera only for a blast in view: put the view on the pad first (the all_on pad, 86
            # cells east, lay out of view on the first run and read no kick)
            s.raw("rimworld/jump_camera_to_cell", x=STATION[0] + centre[0], z=STATION[1] + centre[1])
            t0 = shake_tick(s)
            hp = s.read(pad + "_x", "hitPointsInt")
            blast_tick = hp.tick
            s.act.damage(pad + "_x", (hp.v if hp.state == "ok" else 100) + 60, kind="Crush", name=pad)
            s.shot(rect(centre), name=pad + "_blast")
            s.run(until=SETTLE, limit=SETTLE + 120)
            s.shot(rect(centre), name=pad + "_settled")
            t1 = shake_tick(s)
            ours, vanilla = scars_on(s, centre)
            # the kick's tick is a static: it outlives the load of the stage save, whose ticks repeat from run to run,
            # so a kick counts only inside this blast's own window (its tick to the end of its settle), never as "it moved"
            rows[pad] = dict(off=off, ours=ours, vanilla=vanilla, t0=t0, t1=t1,
                             shook=None if t1 is None or blast_tick is None else blast_tick <= t1 <= blast_tick + SETTLE + 120)

        # the throws: show on (every switch on), then show off (the four off), the same colonist on a like pad
        pid = s.read("thrown", "thingIDNumber")
        setting(s, "blastPowerFromDamage", "False")
        for name, value in (("on", "True"), ("off", "False")):
            for f in SWITCHES:
                setting(s, f, value)
            pawn_at = cell(s.read("thrown", "positionInt"))
            alias = "throw_%s_x" % name
            gap = GAP + 1 if (planted == "unlike_pad" and name == "off") else GAP
            # a 1-damage blast with blast power off: the throw at full force, and a colonist 2 cells from it takes no
            # blast damage, so the second throw finds it as the first did (a real shell's 50 Bomb damage would not)
            if pawn_at is None:
                raise scene.Fault("STAGING_FAULT", detail="the colonist's cell could not be read before the %s throw: %s" % (
                    name, s.read("thrown", "Dead")))
            shell_at = (pawn_at[0] - gap, pawn_at[1])
            tick = s.read("thrown", "positionInt").tick or 0
            s.raw("jawa/explosion_at", at="%d,%d" % shell_at, radius=2.9, damType="Bomb", damAmount=1)
            s.shot(lane_rect(), name="throw_%s_blast" % name)
            s.run(until=THROW_SETTLE, limit=THROW_SETTLE + 120)
            s.shot(lane_rect(), name="throw_%s_landed" % name)
            t = throw(s, tick, pid.v if pid.state == "ok" else "?")
            t.update(pawn_at=pawn_at, shell_at=shell_at)
            throws[name] = t
    finally:
        for f in SWITCHES:
            setting(s, f, before.get(f) or "True")       # unread: the default, on
        setting(s, "blastPowerFromDamage", before.get("blastPowerFromDamage") or "True")
        setting(s, "lastShakeTick", kick0 if kick0 is not None else "-1", of=SHOW)


with scene.open(GAME, contract=show, needs={"mods": ["ExplosiveKnockback"], "map": STAGE, "calm": "standard"}) as s:
    mark_journal(s)
    terrain = {p: dict(rect=(x - HALF, z - HALF, 2 * HALF + 1, 2 * HALF + 1), terrain="Soil") for p, ((x, z), _off) in PADS.items()}
    terrain["lane"] = dict(rect=LANE, terrain="Soil")
    things = {p + "_x": dict(thing=SHELL, at=centre) for p, (centre, _off) in PADS.items()}
    s.stage(station=STATION, terrain=terrain, things=things,
            cast={"thrown": dict(kind="Colonist", at=COLONIST)})
    before = {f: read_field(s, f) for f in SWITCHES + ("blastPowerFromDamage",)}   # put back on every exit path
    rows = {}
    throws = {}
    sweep(s, rows, throws, before)
    folder = s.run_dir


fails = 0


def row(ok, ident, text):
    global fails
    fails += not ok
    print("%s %s: %s" % ("PASS" if ok else "FAIL", ident, text))


for pad in ORDER:
    r = rows[pad]
    scar_on = "showCraterScars" not in r["off"]
    row((r["ours"] > 0) == scar_on and (r["vanilla"] > 0) == (not scar_on), "S_SCAR " + pad,
        "%d crater filth of ours, %d Filth_BlastMark; scars %s (want %s); 1 blast read, limit 0 wrong"
        % (r["ours"], r["vanilla"], "on" if scar_on else "off", "ours only" if scar_on else "vanilla's mark only"))
    shake_on = "showScreenShake" not in r["off"]
    row(r["shook"] is not None and r["shook"] == shake_on, "S_SHAKE " + pad,
        "lastShakeTick %s -> %s (moved %s, want %s); 1 blast read, limit 0 wrong" % (r["t0"], r["t1"], r["shook"], shake_on))
a = rows["all_off"]
row(a["ours"] == 0 and a["vanilla"] > 0 and a["shook"] is False, "S_ALL_OFF",
    "ours %d (limit 0), Filth_BlastMark %d (want >= 1), our kick moved %s (want False)" % (a["ours"], a["vanilla"], a["shook"]))
print("JUDGE (pictures in %s, not counted above): in <pad>_blast, all_on shows every part; off_fire shows no fire, "
      "fireball, sparks, thrown bits or flash of ours; off_ripple shows no ripple ring; all_off shows vanilla's own flash "
      "and nothing of ours; each other part is present. Parts: %s" % (folder, "; ".join("%s = %s" % kv for kv in PART_OF.items())))

on, off = throws["on"], throws["off"]
for name, t in (("on", on), ("off", off)):
    if "cause" in t:
        row(False, "T_THROWN " + name, t["cause"])
ok_like, like_txt = True, []
for name, t in (("on", on), ("off", off)):
    p, sh = t.get("pawn_at"), t.get("shell_at")
    d = None if p is None or sh is None else (p[0] - sh[0], p[1] - sh[1])
    ok_like &= d == (GAP, 0)
    like_txt.append("%s: colonist %s, shell %s, offset %s" % (name, p, sh, d))
row(ok_like, "T_LIKE_PAD", "; ".join(like_txt) + " (want (%d, 0) for both, 2 cases)" % GAP)
if "launch" in on and "launch" in off:
    lo, lf = on["launch"], off["launch"]
    row(lo.get("mass") == lf.get("mass"), "T_SAME_MASS", "launch mass on %s, off %s (limit: equal)" % (lo.get("mass"), lf.get("mass")))

    def offs(rec, key):
        a_, b_ = rec.get(key), rec.get("from")
        return None if not a_ or not b_ else (a_[0] - b_[0], a_[1] - b_[1])
    land_on = offs(dict(on["land"], **{"from": lo.get("from")}), "at") if on.get("land") else None
    land_off = offs(dict(off["land"], **{"from": lf.get("from")}), "at") if off.get("land") else None
    same = (offs(lo, "to") == offs(lf, "to") and lo.get("cells") == lf.get("cells") and land_on == land_off
            and land_on is not None and lo.get("cells") is not None)
    row(same, "T_SAME_THROW", "on: to-from %s, cells %s, landed at-from %s | off: to-from %s, cells %s, landed at-from %s "
        "(2 throws read, limit 0 cells apart)" % (offs(lo, "to"), lo.get("cells"), land_on, offs(lf, "to"), lf.get("cells"), land_off))
print("%s sc_settings_sweep_show: %d failing row(s) over %d blasts and 2 throws; the pictures in %s go to the art judge"
      % ("PASS" if fails == 0 else "FAIL", fails, len(ORDER), folder))
print(scene.judge(folder))
