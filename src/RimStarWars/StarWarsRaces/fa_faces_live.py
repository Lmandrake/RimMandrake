#!/usr/bin/env python3
"""fa_faces_live.py -- RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM: does Facial Animation draw its face on our RSW_ pawns?

The question is runtime state of FA's own comp, so it is answered by a STATE READ, not a picture hunt: FA's
`DrawFaceGraphicsComp.EnableDrawing` is false exactly when FA builds no face nodes for the pawn
(design/RimMandrake/mod_deepdive_faces.md section 2.1). The portraits are for the owner to look at; the verdict
never comes from them.

What it does (live, python.exe: the bridge binds Windows loopback):
  1. refuses (exit 2, UNMEASURED) unless FA, StarWarsRaces, StarWarsPatches and UtinniPatches are all running;
  2. spawns one Baseliner Colonist -- the SANITY PROBE: FA must read EnableDrawing=True on it, or the instrument is
     blind and nothing is judged (exit 2);
  3. spawns 2 Jawa from their own kind (RUT_Jawa_Colonist, xenotype NOT forced) and checks the xenotype they
     actually rolled is RSW_MandrakeJawa ("verify actual kind");
  4. spawns one Colonist forced to each RSW_ xenotype the opt-out def lists, plus RSW_Jawa_Xeno_Gamorrean, and
     checks each landed as asked;
  5. renders a south portrait of every subject (PortraitsCache, forceDirty) into Transient/fa_faces_<ts>/, then
     reads EnableDrawing and the shim's own verdict (RSW_FacialAnimationOptOut.Skips) per pawn;
  6. writes Transient/fa_faces_<ts>/results.json and clears the subjects' rect (jawa/clear_area).

Exit 0: every opt-out-listed xenotype reads EnableDrawing=False, every subject landed as the kind/xenotype asked,
every portrait was written. Exit 1: any of those fails. Exit 2: UNMEASURED.
The two unlisted vanilla-head xenotypes (RSW_MandrakeJawa, RSW_Jawa_Xeno_Gamorrean) are REPORTED, never judged:
whether FA should draw on them is a cosmetic question for the owner (the opt-out def's header says so).

Usage:  python.exe src/RimStarWars/StarWarsRaces/fa_faces_live.py --live
        python3   src/RimStarWars/StarWarsRaces/fa_faces_live.py --selftest
"""
import argparse
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
DEF_XML = os.path.join(HERE, "Defs", "Misc", "RSW_FacialAnimationOptOut.xml")
DEF_CLASS = "RimMandrake.StarWars.Races.RSW_FacialAnimationOptOutDef"
SHIM_TYPE = "RimMandrake.StarWars.Races.RSW_FacialAnimationOptOut"
NEEDED_MODS = ("nals.facialanimation", "mandrake.rsw.starwarsraces", "mandrake.rsw.patches", "mandrake.rut.patches")
JAWA_KIND, JAWA_XENO, JAWA_COUNT = "RUT_Jawa_Colonist", "RSW_MandrakeJawa", 2
UNLISTED = ("RSW_MandrakeJawa", "RSW_Jawa_Xeno_Gamorrean")  # vanilla heads: reported, the owner's call
BASE_KIND = "Colonist"


def listed_xenotypes(path=DEF_XML):
    root = ET.parse(path).getroot()
    out = []
    for d in root:
        if d.tag == DEF_CLASS:
            out += [li.text.strip() for li in d.iter("li") if li.text and li.text.strip()]
    return out


def plan(listed):
    """Subjects in spawn order: (role, kind, forced xenotype or None, expected xenotype)."""
    subs = [("sanity", BASE_KIND, "Baseliner", "Baseliner")]
    subs += [("jawa", JAWA_KIND, None, JAWA_XENO)] * JAWA_COUNT
    subs += [("listed", BASE_KIND, x, x) for x in listed]
    subs += [("unlisted", BASE_KIND, x, x) for x in UNLISTED if x not in listed and x != JAWA_XENO]
    return subs


def _truth(text):
    t = str(text if text is not None else "").strip().lower()
    return True if t == "true" else False if t == "false" else None


def judge(rows):
    """rows: dicts with role, expected, xenotype, kindOk, enable (text), portrait_ok. -> (exit, verdict lines)."""
    lines, bad = [], 0
    sanity = [r for r in rows if r["role"] == "sanity"]
    if not sanity or _truth(sanity[0].get("enable")) is not True:
        return 2, ["UNMEASURED sanity: a Baseliner must read EnableDrawing=True, read %r -- the instrument is blind"
                   % (sanity[0].get("enable") if sanity else None)]
    for r in rows:
        tag = "%s %s" % (r["role"], r["expected"])
        landed = r.get("xenotype") == r["expected"] and r.get("kindOk", False)
        if not landed:
            bad += 1
            lines.append("FAIL %s: landed as xenotype=%s kindOk=%s" % (tag, r.get("xenotype"), r.get("kindOk")))
            continue
        if not r.get("portrait_ok"):
            bad += 1
            lines.append("FAIL %s: no portrait written (%s)" % (tag, r.get("portrait_err")))
        e = _truth(r.get("enable"))
        if r["role"] == "listed":
            if e is not False:
                bad += 1
                lines.append("FAIL %s: FA EnableDrawing=%s (shim Skips=%s) -- FA draws a face" % (tag, r.get("enable"), r.get("skips")))
            else:
                lines.append("PASS %s: no FA face" % tag)
        elif r["role"] in ("jawa", "unlisted"):
            lines.append("REPORT %s: FA EnableDrawing=%s (unlisted: owner's cosmetic call)" % (tag, r.get("enable")))
        else:
            lines.append("PASS %s: FA draws on a Baseliner (instrument sees)" % tag)
    return (1 if bad else 0), lines


def win_path(p):
    if os.name == "nt":
        return p
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, check=True).stdout.strip()


def run_live(out_dir, log=print):
    sys.path.insert(0, UTILS)
    import validation_core as vc
    import live_def_check
    B = vc.Bridge()
    running = live_def_check.running_ids(B.call("jawa/running_mods", details=False, assembly=""))
    gap = [m for m in NEEDED_MODS if m not in {str(x).lower() for x in (running or ())}]
    if gap:
        return 2, ["UNMEASURED: not running: %s" % ", ".join(gap)], []
    if B.call("rimworld/get_ui_state").get("programState") != "Playing":
        log("no game in progress: starting a quicktest map")
        try:
            B.call("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
        except Exception as e:  # noqa: BLE001
            log("quicktest call ended: %s" % str(e)[:200])
            B = vc.Bridge()
    B.call("rimworld/set_time_speed", speed=0)
    info = B.call("jawa/map_info")
    cx, cz = int(info.get("sizeX", 250)) // 2, int(info.get("sizeZ", 250)) // 2
    os.makedirs(out_dir, exist_ok=True)
    wdir = win_path(out_dir)
    rows = []
    for i, (role, kind, forced, expected) in enumerate(plan(listed_xenotypes())):
        kw = dict(kindDef=kind, x=cx + (i % 10) * 2 - 10, z=cz + (i // 10) * 2 - 8, faction="player", count=1)
        if forced:
            kw["xenotype"] = forced
        res = B.call("jawa/spawn_pawn", **kw)
        p = (res.get("pawns") or [{}])[0]
        row = {"role": role, "kind": kind, "expected": expected, "id": p.get("id"),
               "xenotype": p.get("xenotype") or ("Baseliner" if p.get("id") else None),
               "kindOk": bool(p.get("id")) and not p.get("kindSubstituted", True) and bool(p.get("spawned")),
               "spawn_msg": str(res.get("message"))[:200]}
        rows.append(row)
    B.call("rimworld/step_game_ticks", ticks=30)
    for r in rows:
        if not r["id"]:
            r["portrait_ok"], r["portrait_err"] = False, "no pawn"
            continue
        name = "%02d_%s_%s.png" % (rows.index(r), r["role"], r["expected"])
        pr = B.call("jawa/pawn_portrait", pawn=r["id"], path=wdir + "\\" + name, width=256, height=256,
                    rotation="south", renderHeadgear=False, forceDirty=True)
        r["portrait"] = os.path.join(out_dir, name)
        r["portrait_ok"] = bool(pr.get("success")) and int(pr.get("fileSizeBytes") or 0) > 0
        r["portrait_err"] = None if r["portrait_ok"] else str(pr.get("error") or pr.get("message"))[:200]
        cr = B.call("jawa/comp_read", thing=r["id"], comp="DrawFaceGraphicsComp", members="EnableDrawing")
        r["enable"] = (cr.get("values") or {}).get("EnableDrawing") if cr.get("success") else None
        r["comp_read"] = None if cr.get("success") else str(cr.get("error") or cr.get("message"))[:200]
        sk = B.call("jawa/static_call", type=SHIM_TYPE, method="Skips", args=r["id"])
        r["skips"] = sk.get("result") if sk.get("success") else "ERR " + str(sk.get("error") or sk.get("message"))[:120]
    code, lines = judge(rows)
    # GenDebug.ClearArea removes pawns (destroy_batch never does); the subjects stand in this rect, scattered a cell or two
    cl = B.call("jawa/clear_area", rect="%d,%d,%d,%d" % (cx - 14, cz - 12, 30, 28), dryRun=False)
    log("cleanup: %s things removed" % cl.get("destroyedCount"))
    return code, lines, rows


def selftest():
    listed = listed_xenotypes()
    assert len(listed) == len(set(listed)) and len(listed) >= 60, "opt-out list unreadable: %d" % len(listed)
    assert not set(UNLISTED) & set(listed), "an unlisted xenotype is in the opt-out def"
    p = plan(listed)
    assert p[0][0] == "sanity" and sum(1 for s in p if s[0] == "jawa") == 2 and p[1][2] is None
    assert [s[2] for s in p if s[0] == "unlisted"] == ["RSW_Jawa_Xeno_Gamorrean"]

    def row(role, x, enable, xeno=None, kind_ok=True, portrait=True):
        return {"role": role, "expected": x, "xenotype": xeno or x, "kindOk": kind_ok, "enable": enable,
                "portrait_ok": portrait}
    good = [row("sanity", "Baseliner", "True"), row("jawa", JAWA_XENO, "True"), row("listed", "RSW_A", "False"),
            row("unlisted", "RSW_Jawa_Xeno_Gamorrean", "True")]
    assert judge(good)[0] == 0, judge(good)
    assert judge([row("sanity", "Baseliner", None)] + good[1:])[0] == 2          # blind instrument
    assert judge([row("sanity", "Baseliner", "False")] + good[1:])[0] == 2
    assert judge(good + [row("listed", "RSW_B", "True")])[0] == 1                 # FA draws on a listed one
    assert judge(good + [row("listed", "RSW_B", None)])[0] == 1                   # unread is not a pass
    assert judge(good + [row("jawa", JAWA_XENO, "True", xeno="Baseliner")])[0] == 1  # wrong actual kind
    assert judge(good + [row("listed", "RSW_C", "False", kind_ok=False)])[0] == 1
    assert judge(good + [row("listed", "RSW_D", "False", portrait=False)])[0] == 1
    assert judge(good + [row("jawa", JAWA_XENO, "False")])[0] == 0                # unlisted: reported only
    print("selftest PASS: %d listed xenotypes, %d subjects planned" % (len(listed), len(p)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.live:
        return selftest()
    out = os.path.join(REPO, "Transient", "fa_faces_%s" % time.strftime("%Y%m%d_%H%M%S"))
    try:
        code, lines, rows = run_live(out)
    except Exception as e:  # noqa: BLE001
        code, lines, rows = 2, ["UNMEASURED: %s: %s" % (type(e).__name__, str(e)[:300])], []
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "results.json"), "w", encoding="utf-8") as fh:
        json.dump({"exit": code, "verdict": lines, "rows": rows}, fh, indent=1)
    for ln in lines:
        if not ln.startswith("PASS"):
            print(ln)
    print("%s: %d rows; results %s" % (["PASS", "FAIL", "UNMEASURED"][code], len(rows), os.path.join(out, "results.json")))
    return code


if __name__ == "__main__":
    sys.exit(main())
