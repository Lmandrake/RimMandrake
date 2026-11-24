#!/usr/bin/env python3
"""alpha_biomes_retired_live.py - the live scene of ALPHA_BIOMES_RETIRE_THE_LAST_PLANT_DONOR (kind A, deterministic).

CLAIM         With Alpha Biomes (sarg.alphabiomes) out of the mod list, the game loads and our content stands alone.
ENTRY POINT   A game that loaded the list under test (the proof: the full list), at the menu or playing.
OPPORTUNITY   jawa/running_mods reads the list; it holds mandrake.rm.biomes, mandrake.rut.patches and all five DLC.
SUCCESS       rows, every one PASS:
  load        sarg.alphabiomes is not running; no retired donor is
  log         no Player.log line of this load names a def that only Alpha Biomes defined, nor one of our port defs
  donor_gone  a sample of donor defs resolves to nothing (the def reader is not simply answering yes)
  defs        every successor def (census + *_DonorPorts* files + the three diseases) resolves
  plants      every port plant grows on a patch and draws a resolved picture from a path our own mods hold
  terrains    every port terrain is laid, read back, and reads a graphic of ours, clean and polluted path
  maps        a map of each successor biome generates, reads that biome, and draws no bad texture of ours
  diseases    each of the three Miasma diseases fires and puts its own hediff on a colonist
FORBIDDEN     any def of the donor present on any map; any hostile left; nothing is saved.
END           rows on disk. Exit 0 all PASS, 1 a FAIL, 2 UNMEASURED.

    python3 src/RimMandrake/Utils/modcheck/alpha_biomes_retired_live.py --plan
    python3 src/RimMandrake/Utils/modcheck/alpha_biomes_retired_live.py --out DIR     # WSL; bridge held by the caller
The log row is read on the WSL side from the live instance's Player.log. Scratch quicktest worlds only.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CENSUS = os.path.join(REPO, "design", "RimMandrake", "alpha_biomes_census_2026-11-01.json")
INVENTORY = os.path.join(REPO, "infrastructure", "state", "facts", "retired_donor_defs", "sarg.alphabiomes.json")
PID = "sarg.alphabiomes"
NEED = ("mandrake.rm.biomes", "mandrake.rut.patches")
DISEASES = {"RM_Disease_BacterialGangrene": "RM_BacterialGangrene", "RM_Disease_ViralAbasia": "RM_ViralAbasia",
            "RM_Disease_RavagingIntestinalParasites": "RM_RavagingIntestinalParasites"}
GONE_SAMPLE = {"ThingDef": ["AB_GiantAgarilux", "AB_JungleTree", "AB_TinkleGrass"], "TerrainDef": ["AB_DenseMud"],
               "BiomeDef": ["AB_RockyCrags", "AB_MycoticJungle"]}
TOKEN = re.compile(r"[A-Za-z0-9_]+")
MAP = 120


def plan(repo=REPO):
    """What must be there, read from the census and from the port files as XML. Refuses a thin read."""
    c = json.load(open(CENSUS, encoding="utf-8"))
    defs, plants, terrains, biomes = set(), {}, {}, []
    for cat, rows in c["categories"].items():
        for v in rows.values():
            if v["decision"] == "PORTED":
                for s in v["to"]:
                    defs.add((cat, s))
                    if cat == "BiomeDef" and s not in biomes:
                        biomes.append(s)
    want_terrain = {n for k, n in defs if k == "TerrainDef"}
    ports = set(glob.glob(os.path.join(repo, "src", "**", "*DonorPorts*.xml"), recursive=True))
    abs_by_name = {}
    files = []
    for f in glob.glob(os.path.join(repo, "src", "RimMandrake", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            files.append((f, ET.parse(f).getroot()))
        except ET.ParseError:
            continue
    for f, root in files:
        for d in root:
            if d.get("Name"):
                abs_by_name[(d.tag, d.get("Name"))] = d
    for f, root in files:
        for d in root:
            n = d.findtext("defName")
            if not n or not isinstance(d.tag, str):
                continue
            if f in ports:
                defs.add((d.tag, n))
                if d.tag == "ThingDef" and d.find("plant") is not None:
                    plants[n] = d.findtext("graphicData/texPath")
                if d.tag == "TerrainDef":
                    want_terrain.add(n)
            if d.tag == "TerrainDef" and n in want_terrain:
                terrains[n] = {"texturePath": d.findtext("texturePath"),
                               "pollutedTexturePath": d.findtext("pollutedTexturePath")}
    for n in DISEASES:
        defs.add(("IncidentDef", n))
    if len(defs) < 60 or len(plants) < 30 or len(biomes) < 10:
        raise SystemExit("UNMEASURED: thin plan (%d defs, %d plants, %d biomes)" % (len(defs), len(plants), len(biomes)))
    return {"defs": sorted(defs), "plants": dict(sorted(plants.items())), "terrains": dict(sorted(terrains.items())),
            "biomes": biomes}


def donor_names():
    d = json.load(open(INVENTORY, encoding="utf-8"))
    names = set(d["defs"]) - set(d.get("alsoLive") or [])
    if len(names) < 600:
        raise SystemExit("UNMEASURED: donor inventory holds %d names" % len(names))
    return names


def log_hits(lines, donors, ours):
    """[(line number, 'donor'|'ours', name, line)] of a load's log. A donor name anywhere is a hit (a texture name of
    ours that keeps a donor file name appears in a log only when it failed to load). One of our port defs is a hit only
    on a line that is an error or a warning. The mod list echo and the bridge's own lines are not read."""
    bad = re.compile(r"error|exception|could not|couldn't|failed|missing|unresolved|no .*def|warning|not found", re.I)
    out = []
    for i, ln in enumerate(lines, 1):
        if "[RimBridge]" in ln or "[JawaBench]" in ln:
            continue
        toks = set(TOKEN.findall(ln))
        for n in sorted(toks & donors):
            out.append((i, "donor", n, ln.strip()[:240]))
        if PID in ln.lower():
            out.append((i, "donor", PID, ln.strip()[:240]))
        if bad.search(ln):
            for n in sorted(toks & ours):
                out.append((i, "ours", n, ln.strip()[:240]))
    return out


def our_textures(repo=REPO):
    out = set()
    for f in glob.glob(os.path.join(repo, "src", "**", "Textures", "**", "*.png"), recursive=True):
        rel = f.replace(os.sep, "/").split("/Textures/", 1)[1][:-4].lower()
        out.add(rel)
        out.add(rel.rsplit("/", 1)[0])
    return out


def row(rows, name, bad, unread=(), **ev):
    v = "UNMEASURED" if unread else ("FAIL" if bad else "PASS")
    if bad:
        v = "FAIL"
    rows.append({"row": name, "verdict": v, "bad": list(bad)[:40], "unread": list(unread)[:40], **ev})
    print("%-11s %-10s bad=%d unread=%d %s" % (name, v, len(bad), len(list(unread)), (list(bad) + list(unread))[:3]), flush=True)


def drawn(t):
    return str(t.get("variantPath") or t.get("resolvedPath") or t.get("graphicPath") or "")


def bad_drawn(things, undrawn_of):
    """Our defs among `things` that draw BadTex. thing_graphic reads badTex for every Pawn (pawn art is not a Thing
    graphic) and for a thing that draws nothing on purpose (drawerType None: RM_HugeTrunkBlocker), so both are left out."""
    pawns = {t.get("defName") for t in things if "pawn" in str(t.get("thingClass")).lower()}
    cand = {t.get("defName") for t in things if t.get("badTex")
            and str(t.get("defName")).startswith(("RM_", "RUT_", "RSW_"))} - pawns
    return sorted(cand - undrawn_of(sorted(cand))) if cand else []


def undrawn(call, names):
    d = call("jawa/get_defs", defs=";".join("ThingDef/" + n for n in names), fields="drawerType", limit=200)
    return {x.get("defName") for x in (d.get("defs") or d.get("results") or [])
            if str((x.get("fields") or {}).get("drawerType")) == "None"}


# ------------------------------------------------------------------------------------------------- the bridge half
def inner(pl, out, shots):
    for p in (HERE, UTILS):
        if p not in sys.path:
            sys.path.insert(0, p)
    from northstar_driver.session import FastSession
    import biome_site as B
    NS = B.pyre()
    rows, rec = [], {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": None}
    ours = set(pl["ours"])
    try:
        _drive(pl, out, shots, rows, rec, ours, FastSession, B, NS)
    except Exception as ex:             # what was read so far stays on disk; a missing row is UNMEASURED at the end
        rec["died"] = "%s: %s" % (type(ex).__name__, str(ex)[:600])
        print("DIED " + rec["died"], flush=True)
    rec["rows"] = rows
    json.dump(rec, open(out, "w", encoding="utf-8"), indent=1, default=str)


def _drive(pl, out, shots, rows, rec, ours, FastSession, B, NS):
    with FastSession(strict=False, focus=False) as s:
        def call(tool, **k):
            return s.call(tool, **k) or {}
        mods, retired = B.running_retired(s.call)
        rec["mods"] = mods
        lack = B.missing_dlc(mods)
        need = [n for n in NEED if n not in mods]
        row(rows, "load", [m for m in mods if m == PID] + ["retired " + r for r in retired],
            ["DLC " + d for d in lack] + ["absent " + n for n in need], count=len(mods))
        if lack or need:
            return
        # defs
        bad, unread = [], []
        for kind, name in pl["defs"]:
            r = call("jawa/get_def", defType=kind, defName=name)
            if r.get("success") is not True:
                (bad if "no " in str(r).lower() or "not found" in str(r).lower() else unread).append(
                    "%s/%s %s" % (kind, name, str(r.get("message") or r.get("error") or "")[:90]))
        row(rows, "defs", bad, unread, n=len(pl["defs"]))
        bad = []
        for kind, names in GONE_SAMPLE.items():
            for n in names:
                if call("jawa/get_def", defType=kind, defName=n).get("success") is True:
                    bad.append("%s/%s still resolves" % (kind, n))
        row(rows, "donor_gone", bad)
        rec["world"] = str(NS.fresh_quicktest_world(s))[:300]
        base = call("jawa/map_info")
        rec["base"] = {k: base.get(k) for k in ("mapId", "mapBiome", "tile", "sizeX", "sizeZ")}
        call("jawa/kill_hostiles", destroyCorpses=True)
        call("jawa/set_fog", action="unfogAll")
        call("jawa/weather_set", weather="Clear", lockWeather=True)
        # plants: a 5-wide grid of 4x3 patches on rich soil
        ox, oz = 20, 20
        names = list(pl["plants"])
        cols = 8
        W, H = cols * 6 + 2, (len(names) // cols + 1) * 6 + 2
        call("jawa/clear_area", rect="%d,%d,%d,%d" % (ox - 2, oz - 2, W, H), dryRun=False)
        call("jawa/set_terrain", terrainDef="SoilRich", x=ox - 2, z=oz - 2, width=W, height=H)
        bad, unread, ev = [], [], {}
        for i, n in enumerate(names):
            x, z = ox + (i % cols) * 6, oz + (i // cols) * 6
            t = call("jawa/set_plants", ops="%s:%d,%d,3,3" % (n, x, z), growth=1.0)
            g = call("jawa/thing_graphic", rect="%d,%d,3,3" % (x, z), defs=n, limit=50)
            th = g.get("things") or []
            if not th:
                # a water, mud or pollution plant: give it a floor it can stand on and try once more
                for terr, pol in (("MarshyTerrain", False), ("Mud", False), ("WaterShallow", False), ("Sand", False), ("SoilRich", True)):
                    call("jawa/set_terrain", terrainDef=terr, x=x, z=z, width=3, height=3)
                    if pol:
                        call("jawa/set_pollution", rect="%d,%d,3,3" % (x, z), polluted=True)
                    t = call("jawa/set_plants", ops="%s:%d,%d,3,3" % (n, x, z), growth=1.0)
                    th = call("jawa/thing_graphic", rect="%d,%d,3,3" % (x, z), defs=n, limit=50).get("things") or []
                    if th:
                        break
            if not th:
                r = call("rimworld/spawn_thing", defName=n, x=x + 1, z=z + 1)
                th = call("jawa/thing_graphic", rect="%d,%d,3,3" % (x, z), defs=n, limit=50).get("things") or []
            if not th:
                bad.append("%s: none stands (%s)" % (n, str(t.get("rejectedCells") or t.get("message") or t)[:160]))
                continue
            for q in th:
                p = drawn(q)
                allp = [p] + [str(v) for v in (q.get("variantPaths") or [])]
                if q.get("badTex"):
                    bad.append("%s draws BadTex (%s)" % (n, p))
                elif not p:
                    unread.append("%s: no path read" % n)
                elif any(v and v.lower() not in ours for v in allp):
                    bad.append("%s draws %s, held by no mod of ours" % (n, [v for v in allp if v.lower() not in ours][:2]))
                elif any(v.startswith("StandIn/") for v in allp):
                    bad.append("%s draws the stand-in %s" % (n, p))
            ev[n] = {"path": drawn(th[0]), "variants": len(th[0].get("variantPaths") or []), "stand": len(th)}
        row(rows, "plants", bad, unread, n=len(names), drawn=ev, control_paths=len(ours))
        call("jawa/kill_hostiles", destroyCorpses=True)
        for k in range(0, len(names), cols * 3):
            z = oz + (k // cols) * 6
            r = call("rimworld/screenshot_cell_rect", x=ox - 2, z=z - 2, width=W, height=20, fileName="%s_plants_%d" % (shots, k // (cols * 3)), suppressMessage=True)
            rec.setdefault("shots", []).append(r.get("path") or r.get("filePath") or str(r)[:300])
        # terrains, clean then polluted
        tn = list(pl["terrains"])
        tx, tz = ox, oz + H + 4
        bad, unread, ev = [], [], {}
        if tz + 30 > (base.get("sizeZ") or 250):
            tz = 4
        call("jawa/clear_area", rect="%d,%d,%d,%d" % (tx - 2, tz - 2, 58, 34), dryRun=False)
        d = call("jawa/get_defs", defs=";".join("TerrainDef/" + n for n in tn), fields="texturePath,pollutedTexturePath,graphic", limit=200)
        got = {x.get("defName"): (x.get("fields") or {}) for x in (d.get("defs") or d.get("results") or [])}
        for i, n in enumerate(tn):
            x, z = tx + (i % 9) * 6, tz + (i // 9) * 6
            call("jawa/set_terrain", terrainDef=n, x=x, z=z, width=5, height=5)
            b = call("jawa/get_terrain_batch", rects="%d,%d,5,5" % (x, z))
            if n not in json.dumps(b):
                bad.append("%s not laid: %s" % (n, str(b)[:120]))
            f = got.get(n)
            if f is None:
                unread.append("%s fields unread" % n)
                continue
            for k in ("texturePath", "pollutedTexturePath"):
                v = f.get(k)
                if v and not str(v).startswith("(") and str(v).lower() not in ours:
                    ev.setdefault("not_ours", []).append("%s %s" % (n, v))
            ev[n] = f
        row(rows, "terrains", bad, unread, n=len(tn), fields=ev)
        rect = dict(x=tx - 1, z=tz - 1, width=56, height=(len(tn) // 9 + 1) * 6)
        r = call("rimworld/screenshot_cell_rect", fileName="%s_terrain_clean" % shots, suppressMessage=True, **rect)
        rec.setdefault("shots", []).append(r.get("path") or r.get("filePath") or str(r)[:300])
        rec["pollute"] = str(call("jawa/set_pollution", rect="%d,%d,%d,%d" % (tx, tz, 55, rect["height"]), polluted=True))[:300]
        r = call("rimworld/screenshot_cell_rect", fileName="%s_terrain_polluted" % shots, suppressMessage=True, **rect)
        rec["shots"].append(r.get("path") or r.get("filePath") or str(r)[:300])
        call("jawa/kill_hostiles", destroyCorpses=True)
        # diseases, on the quicktest colonists
        bad, unread, ev = [], [], {}
        for inc, hed in DISEASES.items():
            r = call("jawa/fire_incident", incidentDef=inc, forced=True)
            pawns = [p for p in (call("jawa/list_pawns", limit=500).get("pawns") or [])]
            sick = []
            for p in pawns:
                pid = p.get("id") or p.get("thingId") or p.get("pawnId")
                if not pid or not (p.get("isColonist") or p.get("colonist") or "Player" in str(p.get("faction"))):
                    continue
                g = json.dumps(call("jawa/pawn_get", pawn=str(pid)))
                if '"%s"' % hed in g:
                    sick.append(pid)
            ev[inc] = {"fired": r.get("fired"), "sick": sick, "reply": str(r)[:200]}
            if not pawns:
                unread.append("%s: list_pawns read nothing" % inc)
            elif not sick:
                bad.append("%s: fired=%s, no colonist holds %s" % (inc, r.get("fired"), hed))
        row(rows, "diseases", bad, unread, n=len(DISEASES), ev=ev)
        # maps
        work = os.path.join(os.path.dirname(out), "site")
        os.makedirs(work, exist_ok=True)
        e = call("jawa/world_tile_export", path=os.path.join(work, "tiles.csv"), format="csv", extended=True)
        tiles = NS.read_tile_csv(e.get("path") or os.path.join(work, "tiles.csv"))
        colony = base.get("tile")
        # a clean land tile per biome, far apart in the id order
        pool = [k for k, v in sorted(tiles.items()) if k != colony and not v["waterCovered"] and not v["riverCount"]
                and not v["roadCount"] and v["hilliness"] in ("Flat", "SmallHills") and abs(v["lat"]) < 45]
        bad, unread, ev = [], [], {}
        if len(pool) < len(pl["biomes"]) * 3:
            raise B.SiteError("only %d land tiles" % len(pool))
        step = max(1, len(pool) // (len(pl["biomes"]) + 1))
        dn = set(pl["donors"])
        for i, b in enumerate(pl["biomes"]):
            tile = pool[(i + 1) * step - 1]
            try:
                w = call("jawa/world_tile_set", tiles=str(tile), biome=b, temperature=25.0, rainfall=900.0,
                         hilliness="Flat", readBack=1)
                NS.strip_mutators(s, tile)
                g = call("jawa/world_tile_map_generate", tile=tile, biome=b, sizeX=MAP, sizeZ=MAP)
                if g.get("success") is False or g.get("mapId") is None:
                    bad.append("%s: no map: %s" % (b, str(g)[:200]))
                    continue
                call("jawa/set_current_map", mapId=g["mapId"])
                call("jawa/kill_hostiles", destroyCorpses=True)
                call("jawa/set_fog", action="unfogAll")
                mi = call("jawa/map_info")
                tg = call("jawa/thing_graphic", rect="0,0,%d,%d" % (MAP, MAP), limit=100000)
                th = tg.get("things") or []
                if mi.get("mapBiome") != b:
                    bad.append("%s: map reads %s" % (b, mi.get("mapBiome")))
                if not tg.get("isCompleteList") or not th:
                    unread.append("%s: things unread (%d)" % (b, len(th)))
                cnt = {}
                for t in th:
                    cnt[t.get("defName")] = cnt.get(t.get("defName"), 0) + 1
                pl_bad = bad_drawn(th, lambda ns: undrawn(call, ns))
                if pl_bad:
                    bad.append("%s: BadTex %s" % (b, pl_bad[:6]))
                don = sorted(set(cnt) & dn)
                if don:
                    bad.append("%s: donor defs on the map %s" % (b, don))
                ev[b] = {"tile": tile, "things": len(th), "kinds": len(cnt), "failedSteps": (g.get("mapFinalize") or {}).get("failedSteps"),
                         "ports": {n: cnt[n] for n in pl["plants"] if n in cnt}, "top": sorted(cnt.items(), key=lambda kv: -kv[1])[:12]}
                if (g.get("mapFinalize") or {}).get("failedSteps"):
                    bad.append("%s: finalize %s" % (b, g["mapFinalize"]["failedSteps"]))
                call("jawa/weather_set", weather="Clear", lockWeather=True)
                r = call("rimworld/screenshot_cell_rect", x=40, z=40, width=44, height=30, fileName="%s_map_%s" % (shots, b), suppressMessage=True)
                rec["shots"].append(r.get("path") or r.get("filePath") or str(r)[:300])
                call("jawa/set_current_map", mapId=base.get("mapId"))
                idx = g.get("mapIndex")
                if idx is not None:
                    call("jawa/map_drop", mapIndex=int(idx), notifyPlayer=False)
            except Exception as ex:
                unread.append("%s: %s %s" % (b, type(ex).__name__, str(ex)[:160]))
        row(rows, "maps", bad, unread, n=len(pl["biomes"]), ev=ev)
        rec["hostilesLeft"] = str(call("jawa/kill_hostiles", dryRun=True))[:200]


def win(p):
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, timeout=20).stdout.strip()


def load_lines(log):
    with open(log, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def outer(outdir):
    sys.path.insert(0, UTILS)
    from game_paths import PLAYER_LOG
    os.makedirs(outdir, exist_ok=True)
    pl = plan()
    pl["donors"], pl["ours"] = sorted(donor_names()), sorted(our_textures())
    stamp = time.strftime("%Y%m%dT%H%M%S")
    pf, of = os.path.join(outdir, "plan_%s.json" % stamp), os.path.join(outdir, "rows_%s.json" % stamp)
    json.dump(pl, open(pf, "w", encoding="utf-8"))
    rc = subprocess.run(["python.exe", win(os.path.abspath(__file__)), "--inner", win(pf), win(of), "abr_" + stamp],
                        stdin=subprocess.DEVNULL, timeout=7200).returncode      # hang guard; a real run is about 6 min
    if not os.path.exists(of):
        print("UNMEASURED: the bridge half wrote nothing (exit %s)" % rc)
        return 2
    rec = json.load(open(of, encoding="utf-8"))
    lines = load_lines(str(PLAYER_LOG))
    hits = log_hits(lines, set(pl["donors"]), {n for _, n in pl["defs"]})
    loaded = any("Initializing" in x or "Bridge token" in x or "GABP server connected" in x for x in lines)
    capped = any("Reached max messages limit" in x for x in lines)
    row(rec["rows"], "log", ["%d %s %s: %s" % h for h in hits],
        ([] if loaded else ["no load line in %s" % PLAYER_LOG]) + (["the log hit its message cap"] if capped else []),
        lines=len(lines), hits=len(hits), log=str(PLAYER_LOG))
    json.dump(rec, open(of, "w", encoding="utf-8"), indent=1, default=str)
    v = [r["verdict"] for r in rec["rows"]]
    need = {"load", "log", "donor_gone", "defs", "plants", "terrains", "maps", "diseases"}
    missing = need - {r["row"] for r in rec["rows"]}
    print("evidence: %s  missing rows: %s" % (of, sorted(missing)))
    return 1 if "FAIL" in v else (2 if "UNMEASURED" in v or missing else 0)


def main(argv):
    if argv[:1] == ["--inner"]:
        inner(json.load(open(argv[1], encoding="utf-8")), argv[2], argv[3])
        return 0
    if "--plan" in argv:
        p = plan()
        print({k: len(v) for k, v in p.items()}, p["biomes"])
        print(__doc__)
        return 0
    return outer(argv[argv.index("--out") + 1])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
