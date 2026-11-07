#!/usr/bin/env python3
"""heap_bisect.py - which mods make a reload of one save retain memory, and what do they retain?
Item HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE; finding: infrastructure/state/facts/heap_reload_ratchet_2026-11-06.md

    python.exe src/RimMandrake/Utils/heap_bisect.py live --tier TIER [--save NAME] [--loads 6]     the running game
    python3 src/RimMandrake/Utils/heap_bisect.py read FILE...      the HEAP_ROW lines in saved output, as a table and a verdict
    python3 src/RimMandrake/Utils/heap_bisect.py scan [--root src] [--json]    static collections of game objects in our C#

`live` reloads one save and reads, per load, a forced-GC floor and the jawa/heap_census census (the companion must be at this
item's commit). It prints one `HEAP_ROW {json}` line, then the reading. With no --save it saves the running quicktest map as
rm_heapbisect_<tier>, so each list reloads a map it made; --save reloads a save already on disk and never saves.
Exit: 0 read, 1 a reload made no new Game (the series is not reloads), 2 `UNMEASURED: reason`.
The tier is the proof line's label for the list testq loaded; this tool swaps nothing.

Three readings of "retained" sit side by side, because they fail differently:
  floor     GC.GetTotalMemory after a forced full collection, one per load
  ratchet   heap_ratchet.py over the same session's TPS record (a floor between natural GCs: the alarm's own series)
  oldGames  how many earlier Game and Map objects a WeakReference still finds alive (a whole world kept, or none)

Verdict over a ladder of lists, on MB per load and percent of the first floor per load:
  jump      one step of the ladder holds JUMP_SHARE or more of the rise and JUMP_RATIO times its share of the mods added
  smooth    the rise is spread over the steps: it scales with the list, not with a few mods
  flat      the ladder moved under FLAT_MB per load in all
  UNMEASURED  fewer than MIN_LADDER lists read
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import heap_ratchet  # noqa: E402

MIN_LOADS = 6           # the item's floor: 6 or more reloads per list
MIN_LADDER = 3          # two points cannot tell a jump from a line
JUMP_SHARE = 0.5
JUMP_RATIO = 2.0
FLAT_MB = 5.0           # the 14-mod control's own scatter is several MB per load (8.0 falling back from 17)
HELD_MIN_MB = 48        # the sanity canary holds 64 MB
UNHELD_MAX = 500        # Boehm may keep a few of 1000 unheld objects through false pointers; most must die
GROWER_MIN_STEADY = 0.8     # a retainer rises on most loads, never one step's cache fill
TOP_GROWERS = 12
LOAD_BUDGET_S = 900
TPS_TRIES = 6
ROW = "HEAP_ROW "

# ---------------------------------------------------------------- pure readings


def per_load(values):
    """(MB per load, percent of the first value per load) over a series, or (None, None) under two values."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None, None
    mb = (vals[-1] - vals[0]) / float(len(vals) - 1)
    return round(mb, 2), round(100.0 * mb / vals[0], 3) if vals[0] else None


def growers(censuses, top=TOP_GROWERS):
    """Fields whose count climbs across loads, biggest rise first. censuses: one census reply per load. A field absent from
    an early census (under the row cap then) counts from its first appearance."""
    seen = {}
    for i, c in enumerate(censuses):
        for r in c.get("rows") or []:
            seen.setdefault(r["field"], []).append((i, r["n"], r.get("gameObj", 0), r.get("asm")))
    out = []
    for field, pts in seen.items():
        if len(pts) < 3:
            continue
        rises = sum(1 for a, b in zip(pts, pts[1:]) if b[1] > a[1])
        steps = len(pts) - 1
        rate = (pts[-1][1] - pts[0][1]) / float(pts[-1][0] - pts[0][0])
        if rate > 0 and rises / float(steps) >= GROWER_MIN_STEADY:
            out.append({"field": field, "asm": pts[-1][3], "first": pts[0][1], "last": pts[-1][1],
                        "perLoad": round(rate, 1), "gameObj": pts[-1][2]})
    out.sort(key=lambda g: -g["perLoad"])
    return out[:top]


def sanity_problem(s, census):
    """-> why the instruments cannot be trusted, or None."""
    if (s.get("heldMB") or 0) < HELD_MIN_MB or (s.get("releasedMB") or 0) < HELD_MIN_MB:
        return "the floor did not follow the 64 MB canary (held %s, released %s)" % (s.get("heldMB"), s.get("releasedMB"))
    if s.get("unheldAliveOf1000") is None or s["unheldAliveOf1000"] > UNHELD_MAX:
        return "WeakReferences stayed alive on unheld objects (%s of 1000)" % s.get("unheldAliveOf1000")
    if census.get("canarySeen") != 64:
        return "the census did not read its own canary field (%s)" % census.get("canarySeen")
    return None


def ladder_verdict(rows, key="mbPerLoad"):
    """rows: [{mods, mbPerLoad, ...}] -> (verdict, the jump step or None). Sorted by list size."""
    use = sorted((r for r in rows if r.get(key) is not None and r.get("mods")), key=lambda r: r["mods"])
    if len(use) < MIN_LADDER:
        return "UNMEASURED", None
    rise = use[-1][key] - use[0][key]
    if abs(rise) < FLAT_MB and key == "mbPerLoad":
        return "flat", None
    if rise <= 0:
        return "flat", None
    added = float(use[-1]["mods"] - use[0]["mods"])
    best = None
    for a, b in zip(use, use[1:]):
        share = (b[key] - a[key]) / rise
        mods = (b["mods"] - a["mods"]) / added if added else 0.0
        if share >= JUMP_SHARE and (not mods or share >= JUMP_RATIO * mods) and (best is None or share > best["share"]):
            best = {"from": a.get("tier"), "to": b.get("tier"), "share": round(share, 2), "modsShare": round(mods, 2)}
    return ("jump", best) if best else ("smooth", None)


def rows_in(text):
    """The HEAP_ROW json objects in a blob of output; a line torn by a tail cap is skipped."""
    out = []
    for line in (text or "").splitlines():
        at = line.find(ROW)
        if at < 0:
            continue
        try:
            out.append(json.loads(line[at + len(ROW):]))
        except ValueError:
            pass
    return out


def show_rows(rows):
    print("%-26s %5s %5s %8s %7s %8s %7s %6s %6s  %s" % (
        "tier", "mods", "loads", "floor0", "MB/load", "%/load", "ratchet", "oldG", "oldM", "top grower"))
    for r in sorted(rows, key=lambda x: x.get("mods") or 0):
        g = (r.get("growers") or [{}])[0]
        print("%-26s %5s %5s %8s %7s %8s %7s %6s %6s  %s" % (
            r.get("tier"), r.get("mods"), r.get("loads"), (r.get("floors") or [None])[0], r.get("mbPerLoad"), r.get("pctPerLoad"),
            r.get("ratchetMbPerLoad"), (r.get("oldGamesAlive") or [None])[-1], (r.get("oldMapsAlive") or [None])[-1],
            "%s +%s" % (g.get("field"), g.get("perLoad")) if g else "-"))


# ---------------------------------------------------------------- the static scan
STATIC = re.compile(r"^[ \t]*(?:\[[^\]]*\][ \t]*)?(?:(?:private|internal|public|protected|readonly|volatile)[ \t]+)*static[ \t]+"
                    r"(?:readonly[ \t]+)?(?P<type>(?:\w+\.)*(?:Dictionary|List|HashSet|Queue|Stack|SortedList|SortedDictionary|"
                    r"LinkedList|ConcurrentDictionary|ConcurrentBag|ConcurrentQueue)<[^;=(){}]*>)[ \t]+(?P<name>\w+)[ \t]*(?:=|;)",
                    re.M)
GAME_TYPE = re.compile(r"\b(?:Map|Thing|ThingWithComps|Pawn|Building|Plant|Corpse|Game|World|Hediff|Faction|Lord|Apparel|Mote|Job|"
                       r"Settlement|WorldObject|Caravan|Filth|Fire|Projectile)\b")


def scan_text(text):
    """-> [{field, type, line, cleared}] for one C# file's static collections that hold game objects. cleared names how the file
    empties the field; a field nothing in its own file empties is the suspect (another file may still do it)."""
    out = []
    for m in STATIC.finditer(text):
        if not GAME_TYPE.search(m.group("type")):
            continue
        name = re.escape(m.group("name"))
        rest = text[:m.start()] + text[m.end():]
        cleared = []
        if re.search(r"\b%s\s*\.\s*Clear\s*\(" % name, rest):
            cleared.append("Clear")
        if re.search(r"\b%s\s*=[^=]" % name, rest):
            cleared.append("assigned")
        if re.search(r"\b%s\s*\.\s*(?:Remove|RemoveAll|RemoveWhere)\s*\(" % name, rest):
            cleared.append("Remove")
        out.append({"field": m.group("name"), "type": re.sub(r"\s+", " ", m.group("type")),
                    "line": text.count("\n", 0, m.start()) + 1, "cleared": cleared})
    return out


def scan_tree(root):
    rows = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("obj", "bin", "artifacts", ".git")]
        for f in files:
            if f.endswith(".cs"):
                path = os.path.join(d, f)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for r in scan_text(fh.read()):
                        r["file"] = os.path.relpath(path, REPO).replace(os.sep, "/")
                        rows.append(r)
    rows.sort(key=lambda r: (bool(r["cleared"]), r["file"], r["line"]))
    return rows


def cmd_scan(a):
    root = a.root if os.path.isabs(a.root) else os.path.join(REPO, a.root)
    rows = scan_tree(root)
    if a.json:
        print(json.dumps(rows, indent=1))
        return 0
    bare = [r for r in rows if not r["cleared"]]
    print("%d static collections of game objects in C# under %s; %d never emptied in their own file" % (len(rows), a.root, len(bare)))
    for r in bare:
        print("  %s:%d  %s %s" % (r["file"], r["line"], r["type"], r["field"]))
    return 0


def cmd_read(a):
    rows = []
    for p in a.files:
        with open(p, encoding="utf-8", errors="replace") as fh:
            rows += rows_in(fh.read())
    if not rows:
        print("UNMEASURED: no %srow in %s" % (ROW, ", ".join(a.files)))
        return 2
    show_rows(rows)
    print("by MB per load: %s %s" % ladder_verdict(rows, "mbPerLoad"))
    print("by percent per load: %s %s" % ladder_verdict(rows, "pctPerLoad"))
    return 0


# ---------------------------------------------------------------- the live series
class Unmeasured(Exception):
    pass


def tps_reading(session, save):
    """heap_ratchet over this session's record -> (floors of the same-save run, MB per load, verdict) with Nones if unread."""
    rep = heap_ratchet.report(heap_ratchet.default_dir(), session, save)
    if not rep or not rep["sameSave"]:
        return None, None, rep and rep["verdict"]
    r = rep["sameSave"][-1]
    return r["floors"], r["mbPerLoad"], rep["verdict"]


def ensure_fixture(B, a):
    """-> the save name to reload. --save stays as it is; otherwise the running test map is saved under this tier's name."""
    import validation_core as V
    if a.save:
        return a.save
    site = subprocess.run([sys.executable, os.path.join(HERE, "live_site.py"), "--game"], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=LOAD_BUDGET_S)
    if site.returncode:
        raise Unmeasured("no test map to save: %s" % ((site.stdout or "") + (site.stderr or ""))[-200:].strip())
    name = "rm_heapbisect_%s" % a.tier
    B.call("rimworld/save_game", saveName=name)
    if not V._wait_saved(name):
        raise Unmeasured("the fixture save was not written")
    return name


def run_series(B, a):
    import validation_core as V
    running = B.call("jawa/running_mods", details=False, assembly="") or {}
    ids = running.get("packageIds") or running.get("mods") or []
    sanity = B.call("jawa/heap_census", action="sanity") or {}
    save = ensure_fixture(B, a)
    # the first census fills reflection's caches: taken before load 1, so every floor below already holds them
    warm = B.call("jawa/heap_census", action="census") or {}
    why = sanity_problem(sanity, warm)
    if why:
        raise Unmeasured(why)
    floors, reserved, oldg, oldm, games, censuses, session = [], [], [], [], [], [], None
    for i in range(a.loads):
        B.call("rimworld/load_game", saveName=save)
        ok, info = V._wait_playing(B, budget_s=LOAD_BUDGET_S)
        if not ok:
            raise Unmeasured("reload %d of %s did not reach a map: %s" % (i + 1, save, info))
        B.ticks(a.ticks)            # samples into the TPS record, so its gc counter has a before
        c = B.call("jawa/heap_census", action="census") or {}
        f = c.get("floor") or {}
        session = f.get("session") or session
        floors.append(f.get("usedMB"))
        reserved.append(f.get("reservedMB"))
        oldg.append(f.get("oldGamesAlive"))
        oldm.append(f.get("oldMapsAlive"))
        games.append(f.get("gamesSeen"))
        censuses.append(c)
        for _ in range(TPS_TRIES):  # and a sample after the forced GC: that is the record's floor for this game
            B.ticks(a.ticks)
            time.sleep(2.0)
        print("load %d: floor %s MB, reserved %s, old games %s, old maps %s, statics %s" % (
            i + 1, f.get("usedMB"), f.get("reservedMB"), f.get("oldGamesAlive"), f.get("oldMapsAlive"), c.get("collections")), flush=True)
    return {"ids": ids, "save": save, "session": session, "floors": floors, "reserved": reserved, "oldGames": oldg, "oldMaps": oldm,
            "games": games, "censuses": censuses, "sanity": sanity}


def reading_row(a, s):
    """The series -> the HEAP_ROW dict. Pure once the TPS reading is in s (`tps`), so a selftest can feed it."""
    mb, pct = per_load(s["floors"])
    last = s["censuses"][-1] if s["censuses"] else {}
    holders = {h.get("field") for c in s["censuses"] for h in c.get("staleHolders") or []}
    tps_floors, tps_mb, tps_verdict = s.get("tps") or (None, None, None)
    return {"tier": a.tier, "mods": len(s["ids"]) or None, "save": s["save"], "session": s["session"], "loads": len(s["floors"]),
            "floors": s["floors"], "mbPerLoad": mb, "pctPerLoad": pct, "reservedFirst": s["reserved"][0], "reservedLast": s["reserved"][-1],
            "ratchetFloors": tps_floors, "ratchetMbPerLoad": tps_mb, "ratchetVerdict": tps_verdict,
            "oldGamesAlive": s["oldGames"], "oldMapsAlive": s["oldMaps"], "gamesSeen": s["games"],
            "growers": growers(s["censuses"]), "staleHolders": sorted(h for h in holders if h)[:TOP_GROWERS],
            "censusTruncated": last.get("truncated"), "censusFields": last.get("collections"), "readErrors": last.get("readErrors"),
            "sanity": {k: s["sanity"].get(k) for k in ("heldMB", "releasedMB", "unheldAliveOf1000")}}


def judge(row):
    """-> (exit code, closing line). A measurement holds when the series really was reloads and every load read a floor."""
    games = row["gamesSeen"]
    if len(games) >= 2 and games[-1] - games[0] < len(games) - 1:
        return 1, "FAIL: %d reloads made %d new Game objects, so the series is not reloads" % (len(games) - 1, games[-1] - games[0])
    if any(v is None for v in row["floors"]) or row["loads"] < MIN_LOADS:
        return 2, "UNMEASURED: under %d reloads read a floor" % MIN_LOADS
    if not row["mods"]:
        return 2, "UNMEASURED: jawa/running_mods named no list size"
    if not row["ratchetFloors"]:
        return 2, "UNMEASURED: the TPS record holds no same-save floors for this series"
    return 0, "MEASURED %s: %s MB/load, %s %%/load over %d reloads; TPS floor %s MB/load; old games alive %s" % (
        row["tier"], row["mbPerLoad"], row["pctPerLoad"], row["loads"], row["ratchetMbPerLoad"], row["oldGamesAlive"][-1])


def write_json(row):
    d = os.path.join(os.path.dirname(heap_ratchet.default_dir()), "heap_bisect")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s_%s.json" % (row["tier"], (row["session"] or "nosession")[:8]))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(row, fh, indent=1)
    return path


def cmd_live(a):
    if a.loads < MIN_LOADS:
        print("UNMEASURED: --loads under %d is not the item's measurement" % MIN_LOADS)
        return 2
    import validation_core as V
    try:
        B = V.Bridge()
        s = run_series(B, a)
        s["tps"] = tps_reading(s["session"], s["save"]) if s["session"] else (None, None, None)
    except Unmeasured as e:
        print("UNMEASURED: %s" % e)
        return 2
    except Exception as e:      # noqa: BLE001 - the bridge dropped or the tool is absent: nothing was read, so nothing is judged
        print("UNMEASURED: the live series broke: %s: %s" % (type(e).__name__, str(e)[:200]))
        return 2
    row = reading_row(a, s)
    print("wrote %s" % write_json(row))
    print(ROW + json.dumps(row, separators=(",", ":")))
    code, line = judge(row)
    print(line)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("live")
    p.add_argument("--tier", required=True, help="the name of the list this game was loaded on")
    p.add_argument("--save", help="reload this save instead of saving the running test map")
    p.add_argument("--loads", type=int, default=MIN_LOADS)
    p.add_argument("--ticks", type=int, default=120, help="ticks advanced around each census")
    p.set_defaults(fn=cmd_live)
    p = sub.add_parser("read")
    p.add_argument("files", nargs="+")
    p.set_defaults(fn=cmd_read)
    p = sub.add_parser("scan")
    p.add_argument("--root", default="src")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_scan)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
