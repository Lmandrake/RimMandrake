#!/usr/bin/env python3
"""Offline selftest of health_forensics.py (LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED).

The load-tree fixture reproduces Verse.ThreadLocalDeepProfiler.Output / AppendStringRecursive (decompiled 1.6,
RimSage 2026-10-10): depth prefix " -" x depth, " <ms>ms", " (<pct>)" below the root, " (self: <ms> ms)" when a
node has children, then the label; same-label siblings MERGED as "<n>x <label>"; a blank pair; then
"Hotspot analysis". No archived Player.log on this machine holds a real tree (18 logs searched 2026-10-10), so this
parser is UNMEASURED against real output until a verbose launch is archived.
"""
import os
import sys
import tempfile
import tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % detail))
    if not ok:
        FAILS.append(name)


TREE = (
    "Some unrelated line\r\n"
    "--- Main thread ---\r\n"
    " 1000.000ms (self: 100.000 ms) Load all active mods.\r\n"
    " - 600.000ms (60%) (self: 50.000 ms) Load defs\r\n"
    " - - 300.000ms (50%) 3x Parse XML\r\n"
    " - - 250.000ms (42%) Resolve references\r\n"
    " - 300.000ms (30%) Static constructors\r\n"
    "\r\n"
    "\r\n"
    "Hotspot analysis\r\n"
    "----------------------------------------\r\n"
    "1x Static constructors -> 300.000 ms (total (w/children): 300.000 ms)\r\n"
    "3x Parse XML -> 300.000 ms (total (w/children): 300.000 ms)\r\n"
    "1x Resolve references -> 250.000 ms (total (w/children): 250.000 ms)\r\n"
    "1x Load all active mods. -> 100.000 ms (total (w/children): 1000.000 ms)\r\n"
    "1x Load defs -> 50.000 ms (total (w/children): 600.000 ms)\r\n"
    "(Filename: C:\\buildslave\\x.cpp Line: 42)\r\n"
    "\r\n"
    "--- Thread 7 ---\r\n"
    " 40.000ms (self: 10.000 ms) Worker job\r\n"
    " - 30.000ms (75%) Inner\r\n")            # log ends here: tree never closed


def main():
    try:
        import health_forensics as F
    except ImportError as e:
        check("health_forensics imports", False, e)
        return 1
    tmp = tempfile.mkdtemp(prefix="hfor_")
    p = os.path.join(tmp, "Player.log")
    with open(p, "w", newline="") as f:
        f.write(TREE)
    r = F.load_trees(p)
    trees = r["trees"]
    check("two trees found", len(trees) == 2, [t.get("thread") for t in trees])
    t0 = trees[0]
    check("first tree: main thread, root label and total", t0["thread"] == "Main thread"
          and t0["root"]["label"] == "Load all active mods." and t0["root"]["ms"] == 1000.0, t0["root"])
    check("first tree is complete (closed by the hotspot block)", t0["complete"] is True, t0)
    kids = [c["label"] for c in t0["root"]["children"]]
    check("children kept in order at the right depth", kids == ["Load defs", "Static constructors"], kids)
    ld = t0["root"]["children"][0]
    merged = ld["children"][0]
    check("merged siblings keep their count and bare label", merged["count"] == 3 and merged["label"] == "Parse XML",
          merged)
    check("self time of a leaf is its total", merged["self"] == 300.0, merged)
    check("self times partition the root total (no double count)", abs(t0["selfSum"] - 1000.0) < 1e-6, t0["selfSum"])
    check("hotspot table parsed", len(t0["hotspots"]) == 5 and t0["hotspots"][0]["label"] == "Static constructors"
          and t0["hotspots"][1]["count"] == 3, t0["hotspots"])
    t1 = trees[1]
    check("a tree cut off by the end of the log is marked incomplete", t1["complete"] is False
          and t1["thread"] == "Thread 7", t1)
    top = F.top_self(t0, 2)
    check("top self-time nodes, with their path", top[0]["label"] == "Parse XML" and "Load defs" in top[0]["path"],
          top)
    none = os.path.join(tmp, "plain.log")
    with open(none, "w") as f:
        f.write("Mono path[0] = x\nnothing verbose here\n")
    r2 = F.load_trees(none)
    check("a log with no tree says so (UNMEASURED), not an empty success", r2["trees"] == []
          and "no DeepProfiler tree" in F.render_trees(r2), F.render_trees(r2))
    comma = os.path.join(tmp, "comma.log")
    with open(comma, "w") as f:
        f.write("--- Main thread ---\n 12,500ms (self: 2,500 ms) Root\n - 10,000ms (80%) Kid\n\n\nHotspot analysis\n")
    r3 = F.load_trees(comma)
    check("a comma decimal separator parses", r3["trees"] and r3["trees"][0]["root"]["ms"] == 12.5, r3)

    # streaming save census
    s = os.path.join(tmp, "x.rws")
    with open(s, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<savegame><meta><gameVersion>1.6</gameVersion></meta><game>'
                "<world><worldPawns><pawnsAlive>")
        for i in range(30):
            f.write('<li><def>Human</def><id>W%d</id></li>' % i)
        f.write("</pawnsAlive></worldPawns></world><maps><li><things>")
        for i in range(2000):
            f.write('<thing Class="%s"><def>%s</def><id>T%d</id></thing>' % (
                "Pawn" if i % 10 == 0 else "Plant", "Muffalo" if i % 10 == 0 else "Plant_Grass", i))
        f.write("</things><compressedThingMapDeflate>" + "A" * 50000 + "</compressedThingMapDeflate></li></maps>"
                "</game></savegame>")
    tracemalloc.start()
    c = F.save_census(s)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    check("things counted by Class", c["thingsByClass"].get("Plant") == 1800 and c["thingsByClass"].get("Pawn") == 200,
          c["thingsByClass"])
    check("things counted by def", c["thingsByDef"].get("Muffalo") == 200, c["thingsByDef"])
    check("maps counted", c["maps"] == 1, c["maps"])
    check("text bytes by section path find the big grid", c["textBytesByPath"].get(
        "savegame/game/maps/li/compressedThingMapDeflate", 0) == 50000, sorted(c["textBytesByPath"].items())[:5])
    check("file size is the real size", c["fileBytes"] == os.path.getsize(s), c["fileBytes"])
    big = os.path.join(tmp, "big.rws")
    with open(big, "w") as f:
        f.write("<savegame><game><maps><li><things>")
        for i in range(150000):
            f.write('<thing Class="Plant"><def>Plant_Grass</def><id>T%d</id><pos>(1, 0, 2)</pos></thing>' % i)
        f.write("</things></li></maps></game></savegame>")
    tracemalloc.start()
    cb = F.save_census(big)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    size = os.path.getsize(big)
    check("memory stays bounded on a %d MB save (peak %.1f MB)" % (size >> 20, peak / 1048576.0),
          cb["thingsByClass"].get("Plant") == 150000 and peak < size / 2, peak)
    trunc = os.path.join(tmp, "trunc.rws")
    with open(trunc, "w") as f:
        f.write("<savegame><game><maps><li><things><thing Class=\"Plant\"><def>X</def>")
    ct = F.save_census(trunc)
    check("a truncated save is reported incomplete with the parse error", ct["complete"] is False and ct["error"], ct)
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
