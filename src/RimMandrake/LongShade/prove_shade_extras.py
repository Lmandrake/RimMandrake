"""Proof of LONGSHADE_SCENE_LIVECHECK_1: tollok ticks, the lure awning and the harrok on one RM_LongShade scene.

    python3 src/RimMandrake/LongShade/prove_shade_extras.py --offline
    python.exe "$(wslpath -w src/RimMandrake/LongShade/prove_shade_extras.py)" --clause A1 < /dev/null    (A1..A11)

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game or bridge, probe not in the loaded DLL, no generated
RM_LongShade map with three wild deep-shade cells, or a staging call refused).

The live clauses share ONE scene (~10000 game ticks): the first clause asked generates an RM_LongShade map (tile 114480,
size 150; up to 2 maps are tried for three wild deep-shade cells), runs every stage and stores each reading in
<tempdir>/rm_shade_extras_scene.json; a later clause within 45 minutes reads that record. The four toggles (modEnabled,
tollokTicksEnabled, lureAwningEnabled, harrokEnabled) are set true for the run and put back as found.
Scene: Cells -> Arm (message hook) -> TollokStage on (drafted colonists: wild deep cell / under a built roof / under an
RM_LureAwning) -> run 3300 -> Tollok -> Awning spawn (a wild Hare under it) / lureAwningEnabled=false Awning ->
tollokTicksEnabled=false, TollokStage off (fresh colonist on the wild cell) -> run 3300 -> Tollok -> HarrokStage (wild
RM_Harrok held still on an open cell, two downed colonists in its strip, one up-sun) -> harrokEnabled=false run 1000 ->
Harrok -> enabled run 600 -> Harrok -> run 1000 -> Harrok -> Cleanup.
  A1  tollok: a colonist still for 3300 ticks on a wild deep cell (shade >= 0.7, no roof, no gear shade) has RM_TollokInfestation
  A2  the same under a built roof (roof shade read; the cell was deep before the roof) has none
  A3  the same under an RM_LureAwning (gear shade read) has none
  A4  with tollokTicksEnabled=false a colonist still 3300 ticks on the same wild deep cell has none
  A5  the awning's inspect line is "Game sheltering nearby: N" with N = the wild animals in its shade (>= 1), and
      Thing.GetInspectString carries it
  A6  with lureAwningEnabled=false it reads "Lure awning switched off in Mod Settings."
  A7  the cell under the awning reads gear shade (GearShadeAt > 0) and ShadeAt carries it
  A8  enabled, the wild unroofed harrok strikes once in the first window: a Stab of 12-20 on a downed colonist (body size
      <= 1.5) in its strip, and the message "A harrok's shadow fell across <name>, and the harrok struck." is posted
  A9  cooldown: one strike in the first window (< 900 ticks); the next comes >= 900 ticks after it, and never more strikes
      than 1 + (ticks since the first)/900
  A10 with harrokEnabled=false (the same harrok and prey, 1000 ticks) no strike, no Stab, no message
  A11 the up-sun colonist (outside the strip) takes no Stab through every window
Probe: RimMandrake.LongShade.RM_ShadeExtrasProof (Source/RM_ShadeExtrasProof.cs) through jawa/static_call.
--offline  the wiring and the verdict logic (no game): the probe is compiled, every method the driver calls exists, the
           message text and toggles still match the mechanism, and judge() passes a good record and fails each clause on
           a record broken for that clause.
"""
import json
import os
import re
import sys
import tempfile
import time
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROBE = "RimMandrake.LongShade.RM_ShadeExtrasProof"
TILE, SIZE, TRIES = 114480, 150, 2
RECORD = os.path.join(tempfile.gettempdir(), "rm_shade_extras_scene.json")
FRESH_S = 45 * 60
CLAUSES = tuple("A%d" % i for i in range(1, 12))
TOGGLES = ("modEnabled", "tollokTicksEnabled", "lureAwningEnabled", "harrokEnabled")
METHODS = ("Toggle", "Arm", "Cells", "TollokStage", "Tollok", "Awning", "HarrokStage", "Harrok", "Cleanup")
OFF_TEXT = "Lure awning switched off in Mod Settings."
MSG = "A harrok's shadow fell across "
NEVER = -999999
DMG = (12.0, 20.0)


def kv(line):
    """'HEAD a=1 b=x,y' -> {'a': '1', 'b': 'x,y', '_head': 'HEAD'}"""
    out = {"_head": (line or "").split(" ", 1)[0]}
    for m in re.finditer(r"(\w+)=(\S*)", line or ""):
        out[m.group(1)] = m.group(2)
    return out


def _f(d, k, default=float("nan")):
    try:
        return float(d.get(k))
    except (TypeError, ValueError):
        return default


def _i(d, k, default=None):
    try:
        return int(d.get(k))
    except (TypeError, ValueError):
        return default


def _wild_deep(t, r):
    return _f(t, r + "_shade") >= 0.7 and _f(t, r + "_roof") <= 0.01 and _f(t, r + "_gear") <= 0.01


def _still(t, r):
    return t.get(r + "_moved") == "False" and t.get(r + "_dead") == "False"


def judge(rec):
    """{clause: (ok, why)} from a scene record. Pure; the selftest feeds it fakes."""
    out = {}
    st = kv(rec.get("tollok_stage"))
    on, off = kv(rec.get("tollok_on")), kv(rec.get("tollok_off"))
    a1 = (on.get("_head") == "TOLLOK" and on.get("biome") == "RM_LongShade" and on.get("setting") == "True"
          and on.get("wild_hed") == "True" and _wild_deep(on, "wild") and _still(on, "wild"))
    out["A1"] = (a1, rec.get("tollok_on"))
    a2 = (a1 and on.get("roof_hed") == "False" and _f(on, "roof_roof") > 0.01 and _still(on, "roof")
          and _f(st, "roofCastBefore") >= 0.7)
    out["A2"] = (a2, "%s | stage: %s" % (rec.get("tollok_on"), rec.get("tollok_stage")))
    a3 = a1 and on.get("awning_hed") == "False" and _f(on, "awning_gear") > 0.01 and _still(on, "awning")
    out["A3"] = (a3, rec.get("tollok_on"))
    a4 = (a1 and off.get("_head") == "TOLLOK" and off.get("setting") == "False" and off.get("off_hed") == "False"
          and _wild_deep(off, "off") and _still(off, "off"))
    out["A4"] = (a4, rec.get("tollok_off"))

    aw, awo = kv(rec.get("awning_on")), kv(rec.get("awning_off"))
    extra, full = unquote(aw.get("extra", "")), unquote(aw.get("full", ""))
    m = re.fullmatch(r"Game sheltering nearby: (\d+)", extra)
    a5 = (aw.get("_head") == "AWNING" and aw.get("setting") == "True" and m is not None
          and int(m.group(1)) == _i(aw, "wild", -1) and int(m.group(1)) >= 1 and extra in full)
    out["A5"] = (a5, "inspect %r (wild in its shade %s) | full %r" % (extra, aw.get("wild"), full))
    a6 = awo.get("_head") == "AWNING" and awo.get("setting") == "False" and unquote(awo.get("extra", "")) == OFF_TEXT
    out["A6"] = (a6, "inspect %r" % unquote(awo.get("extra", "")))
    a7 = aw.get("_head") == "AWNING" and _f(aw, "gear") > 0.01 and _f(aw, "shade") >= _f(aw, "gear") - 1e-3
    out["A7"] = (a7, "gear %s shade %s" % (aw.get("gear"), aw.get("shade")))

    hs = kv(rec.get("harrok_stage"))
    ho, h1, h2 = kv(rec.get("harrok_off")), kv(rec.get("harrok_w1")), kv(rec.get("harrok_w2"))
    staged = (hs.get("_head") == "HSTAGED" and hs.get("downed") == "True")

    def placed(h):
        return (h.get("_head") == "HARROK" and h.get("moved") == "False" and h.get("roofed") == "False"
                and h.get("wild") == "True" and h.get("prey1_inStrip") == "True" and h.get("prey2_inStrip") == "True"
                and h.get("ctrl_inStrip") == "False" and _f(h, "prey1_size") <= 1.5 and _f(h, "prey2_size") <= 1.5)

    def stabs(h):
        return (_i(h, "prey1_stab", 0) or 0) + (_i(h, "prey2_stab", 0) or 0)

    def sev(h):
        return _f(h, "prey1_stabsev", 0.0) + _f(h, "prey2_stabsev", 0.0)

    def missing(h):
        return (_i(h, "prey1_missing", 0) or 0) + (_i(h, "prey2_missing", 0) or 0)

    off_now, last1, last2 = _i(ho, "now"), _i(h1, "last"), _i(h2, "last")
    a10 = (staged and placed(ho) and ho.get("enabled") == "False" and _i(ho, "last") == NEVER and _i(ho, "msgs") == 0
           and stabs(ho) == 0 and missing(ho) == 0)
    a8 = (staged and placed(h1) and h1.get("enabled") == "True" and _i(h1, "exact") == 1 and _i(h1, "msgs") == 1
          and stabs(h1) >= 1 and (DMG[0] - 0.01 <= sev(h1) <= DMG[1] + 0.01 or missing(h1) > 0)
          and off_now is not None and last1 is not None and last1 >= off_now)
    out["A8"] = (a8, "%s | stage: %s" % (rec.get("harrok_w1"), rec.get("harrok_stage")))
    a9 = (a8 and placed(h2) and last2 is not None and _i(h1, "now") is not None and _i(h1, "now") - off_now < 900
          and _i(h2, "exact", 0) >= 2 and last2 - last1 >= 900
          and _i(h2, "exact", 0) <= 1 + (_i(h2, "now", 0) - last1) // 900)
    out["A9"] = (a9, "w1: %s | w2: %s" % (rec.get("harrok_w1"), rec.get("harrok_w2")))
    out["A10"] = (a10 and a8, "off: %s | then on: exact=%s" % (rec.get("harrok_off"), h1.get("exact")))
    a11 = a8 and all(_i(h, "ctrl_stab") == 0 and h.get("ctrl_inStrip") == "False" for h in (ho, h1, h2))
    out["A11"] = (a11, "ctrl stab off/w1/w2 = %s/%s/%s" % (ho.get("ctrl_stab"), h1.get("ctrl_stab"), h2.get("ctrl_stab")))
    return out


# ---------------------------------------------------------------- offline
def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def _good():
    return {
        "tollok_stage": "TSTAGED wild=20,30 roof=40,30 awning=60,30 roofCastBefore=0.9 roofNow=1 awningGear=0.7",
        "tollok_on": ("TOLLOK biome=RM_LongShade tick=4000 setting=True "
                      "wild_hed=True wild_sev=0.04 wild_shade=0.9 wild_roof=0 wild_gear=0 wild_cast=0.9 wild_moved=False wild_dead=False "
                      "roof_hed=False roof_sev=0 roof_shade=1 roof_roof=1 roof_gear=0 roof_cast=0.9 roof_moved=False roof_dead=False "
                      "awning_hed=False awning_sev=0 awning_shade=0.9 awning_roof=0 awning_gear=0.7 awning_cast=0.8 awning_moved=False awning_dead=False"),
        "awning_on": "AWNING gear=0.7 shade=0.9 wild=1 setting=True extra=Game%20sheltering%20nearby%3A%201 full=Made%20of%20wood%0AGame%20sheltering%20nearby%3A%201",
        "awning_off": "AWNING gear=0.7 shade=0.9 wild=1 setting=False extra=Lure%20awning%20switched%20off%20in%20Mod%20Settings. full=x",
        "tollok_off": ("TOLLOK biome=RM_LongShade tick=7400 setting=False "
                       "off_hed=False off_sev=0 off_shade=0.9 off_roof=0 off_gear=0 off_cast=0.9 off_moved=False off_dead=False"),
        "harrok_stage": "HSTAGED harrok=75,75 dir=0.6,0.8 prey1=76,77 prey2=77,78 ctrl=73,73 downed=True length=6 halfWidth=0.9 cooldown=900 maxPrey=1.5 dmg=12-20",
        "harrok_off": ("HARROK pos=75,75 moved=False roofed=False wild=True enabled=False last=-999999 now=8500 msgs=0 exact=0 "
                       "prey1_stab=0 prey1_stabsev=0 prey1_missing=0 prey1_inStrip=True prey1_size=1 "
                       "prey2_stab=0 prey2_stabsev=0 prey2_missing=0 prey2_inStrip=True prey2_size=1 "
                       "ctrl_stab=0 ctrl_stabsev=0 ctrl_missing=0 ctrl_inStrip=False ctrl_size=1"),
        "harrok_w1": ("HARROK pos=75,75 moved=False roofed=False wild=True enabled=True last=8520 now=9180 msgs=1 exact=1 "
                      "prey1_stab=1 prey1_stabsev=15.2 prey1_missing=0 prey1_inStrip=True prey1_size=1 "
                      "prey2_stab=0 prey2_stabsev=0 prey2_missing=0 prey2_inStrip=True prey2_size=1 "
                      "ctrl_stab=0 ctrl_stabsev=0 ctrl_missing=0 ctrl_inStrip=False ctrl_size=1"),
        "harrok_w2": ("HARROK pos=75,75 moved=False roofed=False wild=True enabled=True last=9420 now=10250 msgs=2 exact=2 "
                      "prey1_stab=2 prey1_stabsev=30 prey1_missing=0 prey1_inStrip=True prey1_size=1 "
                      "prey2_stab=0 prey2_stabsev=0 prey2_missing=0 prey2_inStrip=True prey2_size=1 "
                      "ctrl_stab=0 ctrl_stabsev=0 ctrl_missing=0 ctrl_inStrip=False ctrl_size=1"),
    }


def _breaks():
    """{clause: [(key, old, new)]}: one edit per clause that must flip exactly that clause to FAIL."""
    return {
        "A1": [("tollok_on", "wild_hed=True", "wild_hed=False"), ("tollok_on", "wild_shade=0.9", "wild_shade=0.5"),
               ("tollok_on", "wild_moved=False", "wild_moved=True"), ("tollok_on", "biome=RM_LongShade", "biome=TemperateForest")],
        "A2": [("tollok_on", "roof_hed=False", "roof_hed=True"), ("tollok_on", "roof_roof=1", "roof_roof=0"),
               ("tollok_stage", "roofCastBefore=0.9", "roofCastBefore=0.2")],
        "A3": [("tollok_on", "awning_hed=False", "awning_hed=True"), ("tollok_on", "awning_gear=0.7", "awning_gear=0")],
        "A4": [("tollok_off", "off_hed=False", "off_hed=True"), ("tollok_off", "setting=False", "setting=True")],
        "A5": [("awning_on", "wild=1", "wild=2"), ("awning_on", "extra=Game%20sheltering%20nearby%3A%201", "extra=Game%20sheltering%20nearby%3A%200"),
               ("awning_on", "full=Made%20of%20wood%0AGame%20sheltering%20nearby%3A%201", "full=Made%20of%20wood")],
        "A6": [("awning_off", "extra=Lure%20awning%20switched%20off%20in%20Mod%20Settings.", "extra=Game%20sheltering%20nearby%3A%201")],
        "A7": [("awning_on", "gear=0.7", "gear=0")],
        "A8": [("harrok_w1", "exact=1", "exact=0"), ("harrok_w1", "prey1_stabsev=15.2", "prey1_stabsev=30"),
               ("harrok_w1", "roofed=False", "roofed=True"), ("harrok_w1", "prey1_size=1", "prey1_size=2")],
        "A9": [("harrok_w2", "last=9420", "last=9100"), ("harrok_w2", "exact=2", "exact=1"),
               ("harrok_w1", "now=9180", "now=9500")],
        "A10": [("harrok_off", "last=-999999", "last=8400"), ("harrok_off", "prey1_stab=0", "prey1_stab=1"),
                ("harrok_off", "enabled=False", "enabled=True")],
        "A11": [("harrok_w2", "ctrl_stab=0", "ctrl_stab=1"), ("harrok_w1", "ctrl_inStrip=False", "ctrl_inStrip=True")],
    }


def offline():
    bad = []
    proj = _read("src/RimMandrake/LongShade/Source/RM_LongShade.csproj")
    if '<Compile Include="RM_ShadeExtrasProof.cs" />' not in proj:
        bad.append("RM_ShadeExtrasProof.cs is not compiled by RM_LongShade.csproj")
    src = _read("src/RimMandrake/LongShade/Source/RM_ShadeExtrasProof.cs")
    for meth in METHODS:
        if not re.search(r"public static string %s\(string \w+\)" % meth, src):
            bad.append("RM_ShadeExtrasProof.%s(string) missing" % meth)
    mech = _read("src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs")
    if '"A harrok\'s shadow fell across " + prey.LabelShort + ", and the harrok struck."' not in mech:
        bad.append("the harrok message in RM_ShadeExtras.cs is no longer the one the item and the probe name")
    if '"Lure awning switched off in Mod Settings."' not in mech or '"Game sheltering nearby: "' not in mech:
        bad.append("the lure awning's inspect strings in RM_ShadeExtras.cs changed")
    if '"A harrok\'s shadow fell across " + p.LabelShort + ", and the harrok struck."' not in src:
        bad.append("the probe's expected harrok message drifted from the mechanism's")
    if "private int lastStrike" not in mech:
        bad.append("RM_CompHarrokAmbush.lastStrike (read by reflection) was renamed")
    sett = _read("src/RimMandrake/LongShade/Source/RM_LongShadeMod.cs")
    for t in TOGGLES:
        if not re.search(r"public static bool %s\s*=" % t, sett):
            bad.append("RM_LongShadeSettings.%s is not a public static bool" % t)
    calls = set(re.findall(r'static\("(\w+)"', _read("src/RimMandrake/LongShade/prove_shade_extras.py")))
    if not calls or not calls <= set(METHODS):
        bad.append("the driver calls probe methods outside METHODS: %s" % sorted(calls - set(METHODS)))
    g = judge(_good())
    bad += ["judge fails %s on a good record: %s" % (c, w) for c, (ok, w) in g.items() if not ok]
    if set(g) != set(CLAUSES):
        bad.append("judge covers %s, not %s" % (sorted(g), CLAUSES))
    for c, edits in _breaks().items():
        for k, old, new in edits:
            rec = _good()
            if old not in rec[k]:
                bad.append("planted break for %s does not apply (%s lacks %r)" % (c, k, old))
                continue
            rec[k] = rec[k].replace(old, new, 1)
            if judge(rec)[c][0]:
                bad.append("judge passes %s on a record broken for it (%s: %r -> %r)" % (c, k, old, new))
    for k in _good():
        rec = _good()
        del rec[k]
        if all(ok for ok, _ in judge(rec).values()):
            bad.append("judge passes every clause with %s missing" % k)
    for b in bad:
        print("FAIL " + b)
    print("%s offline: probe compiled, mechanism strings match, judge sees a pass and every clause's fail" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


# ---------------------------------------------------------------- live
def _scene():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from scenes import scenelib as S  # noqa: E402

    def static(method, arg=""):
        r = S.call("jawa/static_call", type=PROBE, method=method, args=arg)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else str(r)

    if S.call("rimworld/get_ui_state").get("programState") != "Playing":
        S.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if S.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    back = (S.call("jawa/map_info") or {}).get("mapIndex", 0)
    rec = {"started": time.time()}
    if not static("Toggle", "probe").startswith("REFUSED: want"):
        rec["unmeasured"] = "probe RM_ShadeExtrasProof absent (new LongShade DLL not loaded): " + static("Toggle", "probe")
        return rec
    found = {}
    for t in TOGGLES:
        r = kv(static("Toggle", t + "=true"))
        found[t] = r.get("was")
    rec["toggles_found"] = found
    mid = None
    try:
        for _ in range(TRIES):
            mid = S.biome_map(TILE, "RM_LongShade", size=SIZE)
            S.run(300)                                   # the shade grid's first recompute
            cells = static("Cells")
            rec.setdefault("maps", []).append(cells)
            if " n=3 " in cells and "biome=RM_LongShade" in cells:
                break
            S.drop_map(mid, TILE, back)
            mid = None
        if mid is None:
            rec["unmeasured"] = "no generated RM_LongShade map had three wild deep-shade cells in %d tries" % TRIES
            return rec
        rec["arm"] = static("Arm")
        if not rec["arm"].startswith("ARMED"):
            rec["unmeasured"] = "message hook refused: " + rec["arm"]
            return rec
        rec["tollok_stage"] = static("TollokStage", "on")
        if not rec["tollok_stage"].startswith("TSTAGED"):
            rec["unmeasured"] = "tollok staging refused: " + rec["tollok_stage"]
            return rec
        S.run(3300)
        rec["tollok_on"] = static("Tollok")
        rec["awning_on"] = static("Awning", "spawn")
        static("Toggle", "lureAwningEnabled=false")
        rec["awning_off"] = static("Awning")
        static("Toggle", "lureAwningEnabled=true")
        static("Toggle", "tollokTicksEnabled=false")
        rec["tollok_off_stage"] = static("TollokStage", "off")
        S.run(3300)
        rec["tollok_off"] = static("Tollok")
        static("Toggle", "tollokTicksEnabled=true")
        rec["harrok_stage"] = static("HarrokStage")
        if rec["harrok_stage"].startswith("HSTAGED"):
            static("Toggle", "harrokEnabled=false")
            S.run(1000)
            rec["harrok_off"] = static("Harrok")
            static("Toggle", "harrokEnabled=true")
            S.run(600)
            rec["harrok_w1"] = static("Harrok")
            S.run(1000)
            rec["harrok_w2"] = static("Harrok")
        rec["cleanup"] = static("Cleanup")
    finally:
        for t, was in found.items():
            if was in ("True", "False"):
                static("Toggle", "%s=%s" % (t, was.lower()))
        if mid is not None:
            S.drop_map(mid, TILE, back)
    return rec


def live(clause):
    rec = None
    if os.path.isfile(RECORD):
        with open(RECORD, encoding="utf-8") as fh:
            old = json.load(fh)
        if time.time() - old.get("started", 0) < FRESH_S and not old.get("unmeasured"):
            rec = old
            print("scene record reused: %s" % RECORD)
    if rec is None:
        try:
            rec = _scene()
        except Exception as ex:   # no bridge, no game
            print("UNMEASURED: %r" % (ex,))
            return 2
        with open(RECORD, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
    if rec.get("unmeasured"):
        print("UNMEASURED: " + rec["unmeasured"])
        return 2
    ok, why = judge(rec)[clause]
    print("%s %s: %s" % ("PASS" if ok else "FAIL", clause, why))
    return 0 if ok else 1


def main(argv):
    if "--offline" in argv:
        return offline()
    if "--clause" in argv and argv.index("--clause") + 1 < len(argv) and argv[argv.index("--clause") + 1] in CLAUSES:
        return live(argv[argv.index("--clause") + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
