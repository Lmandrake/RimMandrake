"""health_forensics.py - offline, read-only game-health forensics (LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED).

    python3 src/RimMandrake/Utils/health_forensics.py load-tree <Player.log> [--top 25] [--json]
    python3 src/RimMandrake/Utils/health_forensics.py save-census <save.rws> [--top 30] [--json]

load-tree: RimWorld prints a DeepProfiler tree into Player.log only when Prefs.LogVerbose is on
(DeepProfiler.Start/End are no-ops otherwise; decompiled 1.6 Verse/DeepProfiler.cs and ThreadLocalDeepProfiler.cs,
RimSage 2026-10-10). Each outermost End() prints "--- Main thread ---" (or "--- Thread <managed id> ---"), then one
line per node: " -" x depth, " <ms>ms", " (<pct>)" below the root, " (self: <ms> ms)" when it has children, then the
label. Same-label siblings are MERGED by the engine into "<n>x <label>" with their children pooled, so a node is a
label group, not one call. Then two blank lines and a "Hotspot analysis" table. A tree with no hotspot table was cut
off (crash, log cap, end of file) and is marked incomplete. A verbose launch is a DIAGNOSTIC load: compare it only
with other verbose loads. Streaming, line by line; at most MAX_NODES nodes kept per tree.

save-census: streaming iterparse of a .rws with every finished element cleared and detached, so memory does not
grow with the save. Counts things by Class and by def, maps, world pawns, elements and text characters by section
path (depth <= 6). Text characters equal bytes for the base64 grids that dominate saves.
"""
import argparse
import gzip
import json
import os
import re
import sys

MAX_NODES = 200000
MAX_KEYS = 50000
PATH_DEPTH = 6
NUM = r"[0-9]+(?:[.,][0-9]+)?"
HEADER = re.compile(r"^--- (Main thread|Thread [0-9]+) ---$")
NODE = re.compile(r"^((?: -)*) (" + NUM + r")ms(?: \(([^()]*%)\))?(?: \(self: (" + NUM + r") ms\))? (.*)$")
HOT = re.compile(r"^([0-9]+)x (.*) -> (" + NUM + r") ms \(total \(w/children\): (" + NUM + r") ms\)$")
COUNTED = re.compile(r"^([0-9]+)x (.*)$")


def _f(s):
    return float(s.replace(",", "."))


def _new_tree(thread, line_no):
    return {"thread": thread, "line": line_no, "root": None, "complete": False, "nodes": 0, "droppedNodes": 0,
            "anomalies": 0, "hotspots": [], "selfSum": 0.0, "_stack": [], "_phase": "body"}


def _finish(t, out):
    t.pop("_stack", None)
    t.pop("_phase", None)
    t["selfSum"] = round(t["selfSum"], 3)
    if t["root"] is not None:
        t["residualMs"] = round(t["root"]["ms"] - t["selfSum"], 3)
    out.append(t)


def load_trees(path):
    trees, cur, lines = [], None, 0
    with open(path, "rb") as fh:
        for raw in fh:
            lines += 1
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            h = HEADER.match(line)
            if h:
                if cur is not None:
                    _finish(cur, trees)
                cur = _new_tree(h.group(1), lines)
                continue
            if cur is None:
                continue
            ph = cur["_phase"]
            if ph == "body":
                m = NODE.match(line)
                if m:
                    depth = len(m.group(1)) // 2
                    label = m.group(5)
                    cm = COUNTED.match(label)
                    count, bare = (int(cm.group(1)), cm.group(2)) if cm and depth > 0 else (1, label)
                    ms = _f(m.group(2))
                    self_ms = _f(m.group(4)) if m.group(4) else ms
                    node = {"label": bare, "count": count, "ms": ms, "self": self_ms, "depth": depth,
                            "pct": m.group(3), "children": []}
                    st = cur["_stack"]
                    if depth == 0:
                        if cur["root"] is not None:
                            cur["anomalies"] += 1
                            continue
                        cur["root"] = node
                        st[:] = [node]
                    elif depth > len(st) or not st:
                        cur["anomalies"] += 1
                        continue
                    else:
                        del st[depth:]
                        if cur["nodes"] < MAX_NODES:
                            st[-1]["children"].append(node)
                        else:
                            cur["droppedNodes"] += 1
                        st.append(node)
                    cur["nodes"] += 1
                    cur["selfSum"] += self_ms
                elif line.strip() == "":
                    cur["_phase"] = "gap"
                else:
                    _finish(cur, trees)          # interrupted by an unrelated line: incomplete
                    cur = None
            elif ph == "gap":
                if line.strip() == "":
                    continue
                if line.strip() == "Hotspot analysis":
                    cur["_phase"], cur["complete"] = "hot", True
                else:
                    _finish(cur, trees)
                    cur = None
            elif ph == "hot":
                if set(line.strip()) == {"-"}:
                    continue
                m = HOT.match(line)
                if m:
                    if len(cur["hotspots"]) < 1000:
                        cur["hotspots"].append({"count": int(m.group(1)), "label": m.group(2), "selfMs": _f(m.group(3)),
                                                "totalMs": _f(m.group(4))})
                else:
                    _finish(cur, trees)
                    cur = None
    if cur is not None:
        _finish(cur, trees)
    return {"path": path, "lines": lines, "trees": trees}


def top_self(tree, n=25):
    out = []

    def walk(node, path):
        p = path + [node["label"]]
        out.append({"label": node["label"], "count": node["count"], "selfMs": node["self"], "totalMs": node["ms"],
                    "depth": node["depth"], "path": " > ".join(p)})
        for c in node["children"]:
            walk(c, p)
    if tree.get("root"):
        sys.setrecursionlimit(max(1000, sys.getrecursionlimit()))
        walk(tree["root"], [])
    out.sort(key=lambda x: (-x["selfMs"], -x["depth"]))
    return out[:n]


def render_trees(r, top=25):
    if not r["trees"]:
        return ("%s: no DeepProfiler tree in %d lines. Trees print only on a verbose launch (Prefs.LogVerbose): "
                "load timing is UNMEASURED from this log." % (r["path"], r["lines"]))
    out = []
    for t in r["trees"]:
        root = t["root"] or {}
        out.append("%s tree at line %d: %s %sms, %d nodes, %s%s%s; self-time sum %s ms (residual %s ms)" % (
            t["thread"], t["line"], root.get("label"), root.get("ms"), t["nodes"],
            "complete" if t["complete"] else "INCOMPLETE (no hotspot table: cut off)",
            ", %d anomalies" % t["anomalies"] if t["anomalies"] else "",
            ", %d nodes over the cap dropped" % t["droppedNodes"] if t["droppedNodes"] else "",
            t["selfSum"], t.get("residualMs")))
        for x in top_self(t, top):
            out.append("   self %10.3f ms  total %10.3f ms  %s%s" % (
                x["selfMs"], x["totalMs"], "%dx " % x["count"] if x["count"] > 1 else "", x["path"][-150:]))
    out.append("(a node is a label group: the engine merges same-label siblings; a verbose load is a diagnostic "
               "load, comparable only with other verbose loads)")
    return "\n".join(out)


def _bump(d, k, n=1, over=None):
    if k in d or len(d) < MAX_KEYS:
        d[k] = d.get(k, 0) + n
    elif over is not None:
        over[0] += 1


def save_census(path):
    import xml.etree.ElementTree as ET
    res = {"path": path, "fileBytes": os.path.getsize(path), "complete": False, "error": None, "elements": 0,
           "textChars": 0, "maps": 0, "worldPawnEntries": 0, "thingsByClass": {}, "thingsByDef": {},
           "elementsByPath": {}, "textBytesByPath": {}, "keysOverCap": 0}
    over = [0]
    with open(path, "rb") as probe:
        gz = probe.read(2) == b"\x1f\x8b"
    fh = gzip.open(path, "rb") if gz else open(path, "rb")
    res["gzip"] = gz
    tags, elems = [], []
    try:
        for ev, el in ET.iterparse(fh, events=("start", "end")):
            if ev == "start":
                tags.append(el.tag)
                elems.append(el)
                key = "/".join(tags[:PATH_DEPTH])
                _bump(res["elementsByPath"], key, 1, over)
                res["elements"] += 1
                if el.tag == "thing":
                    _bump(res["thingsByClass"], el.get("Class", "(no Class)"), 1, over)
                if len(tags) == 4 and tags[1:] == ["game", "maps", "li"]:
                    res["maps"] += 1
                if len(tags) >= 2 and tags[-2] in ("pawnsAlive", "pawnsDead") and "worldPawns" in tags:
                    res["worldPawnEntries"] += 1
                continue
            txt = el.text
            if txt and not len(el):
                n = len(txt.strip())
                if n:
                    res["textChars"] += n
                    _bump(res["textBytesByPath"], "/".join(tags[:PATH_DEPTH]), n, over)
                if el.tag == "def" and len(tags) >= 2 and tags[-2] == "thing":
                    _bump(res["thingsByDef"], txt.strip(), 1, over)
            tags.pop()
            elems.pop()
            el.clear()
            if elems:
                del elems[-1][:]          # detach finished children: the tree never grows
        res["complete"] = True
    except ET.ParseError as e:
        res["error"] = "ParseError: %s" % e
    except (OSError, EOFError) as e:
        res["error"] = "%s: %s" % (type(e).__name__, e)
    finally:
        fh.close()
    res["keysOverCap"] = over[0]
    return res


def render_census(c, top=30):
    def tops(d, n):
        return ", ".join("%s %d" % kv for kv in sorted(d.items(), key=lambda kv: -kv[1])[:n])
    out = ["%s: %.1f MB on disk%s, %s; %d elements, %d text chars; %d maps, %d world-pawn entries" % (
        c["path"], c["fileBytes"] / 1048576.0, " (gzip)" if c.get("gzip") else "",
        "complete" if c["complete"] else "INCOMPLETE (%s): counts cover only what parsed" % c["error"],
        c["elements"], c["textChars"], c["maps"], c["worldPawnEntries"]),
        "things by Class: " + tops(c["thingsByClass"], top),
        "things by def: " + tops(c["thingsByDef"], top),
        "largest text sections (chars): " + tops(c["textBytesByPath"], 15),
        "most elements by section: " + tops(c["elementsByPath"], 15)]
    if c["keysOverCap"]:
        out.append("%d keys over the %d-key cap were not tallied" % (c["keysOverCap"], MAX_KEYS))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("load-tree")
    a1.add_argument("log")
    a1.add_argument("--top", type=int, default=25)
    a1.add_argument("--json", action="store_true")
    a2 = sub.add_parser("save-census")
    a2.add_argument("save")
    a2.add_argument("--top", type=int, default=30)
    a2.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "load-tree":
        r = load_trees(a.log)
        print(json.dumps(r, indent=1) if a.json else render_trees(r, a.top))
        return 0
    c = save_census(a.save)
    print(json.dumps(c, indent=1) if a.json else render_census(c, a.top))
    return 0 if c["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
