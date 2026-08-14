#!/usr/bin/env python3
"""One-pass census of every building's graphic data from the LIVE def dump.

WHY THE DUMP AND NOT THE XML. The question "can I recolour this for free?" is
answered by the def the *running game* holds after every mod's patches have
applied, not by the XML Ludeon shipped. A mod can add a shaderType or a colour
to someone else's def and the raw XML will never show it. DefDump/defs/ThingDef.json
is the merged state, so it is the right source for structure.
(Values from the dump are still worth a second look — see CLAUDE.md; the dump has
disagreed with the running game before.)

ThingDef.json is ~850 MB, so this streams the `defs` array by brace depth rather
than json.load()-ing the lot into memory.

Writes a compact TSV of one row per building-ish ThingDef:
    defName, modName, texPath, graphicClass, shaderType, color, colorTwo,
    colorThree, stuffCategories, drawSize, designationCategory, size

Run: /home/mandrake/.venvs/art/bin/python design/Jawa/art/scan_graphics.py
     (plain python3 is fine too; no Pillow needed here)
"""

import json
import os
import sys

DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump/defs/ThingDef.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "census_building_graphics.tsv")

COLS = ["defName", "modName", "texPath", "graphicClass", "shaderType",
        "color", "colorTwo", "colorThree", "stuff", "drawSize",
        "designationCategory", "size", "label"]


def stream_objects(path):
    """Yield each top-level object inside the "defs":[ ... ] array."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        # skip to the start of the array
        buf = fh.read(1 << 16)
        i = buf.index('"defs":[') + len('"defs":[')
        depth = 0
        cur = []
        in_str = False
        esc = False
        while True:
            if i >= len(buf):
                chunk = fh.read(1 << 20)
                if not chunk:
                    break
                buf = chunk
                i = 0
            c = buf[i]
            i += 1
            if depth:
                cur.append(c)
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c == "{":
                if depth == 0:
                    cur = ["{"]
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    yield "".join(cur)
                    cur = []


def fmt_color(v):
    if v is None:
        return ""
    if isinstance(v, dict):
        # Unity Color is 0..1 floats; report as 0-255 ints for comparison with XML
        try:
            return "(%d,%d,%d)" % tuple(round(v.get(k, 0) * 255)
                                        for k in ("r", "g", "b"))
        except Exception:
            return json.dumps(v)
    return str(v)


def shader_of(gd):
    s = gd.get("shaderType")
    if s is None:
        return ""
    if isinstance(s, dict):
        return s.get("defName") or s.get("shaderPath") or json.dumps(s)[:60]
    return str(s)


def main():
    n = kept = 0
    with open(OUT, "w", encoding="utf-8") as out:
        out.write("\t".join(COLS) + "\n")
        for raw in stream_objects(DUMP):
            n += 1
            if '"graphicData"' not in raw:
                continue
            try:
                d = json.loads(raw)
            except Exception:
                continue
            f = d.get("fields") or {}
            gd = f.get("graphicData")
            if not isinstance(gd, dict):
                continue
            cat = f.get("category")
            if cat not in ("Building", "Item", "Ethereal", None):
                continue
            stuff = f.get("stuffCategories") or []
            if isinstance(stuff, list):
                stuff = ",".join(str(s) for s in stuff)
            ds = gd.get("drawSize")
            if isinstance(ds, dict):
                ds = "%sx%s" % (ds.get("x"), ds.get("y", ds.get("z")))
            sz = f.get("size")
            if isinstance(sz, dict):
                sz = "%sx%s" % (sz.get("x"), sz.get("z"))
            row = [
                d.get("defName", ""),
                d.get("modName", ""),
                gd.get("texPath", "") or "",
                gd.get("graphicClass", "") or "",
                shader_of(gd),
                fmt_color(gd.get("color")),
                fmt_color(gd.get("colorTwo")),
                fmt_color(gd.get("colorThree")),
                stuff,
                str(ds or ""),
                str(f.get("designationCategory") or ""),
                str(sz or ""),
                d.get("label", ""),
            ]
            out.write("\t".join(str(c).replace("\t", " ").replace("\n", " ")
                                for c in row) + "\n")
            kept += 1
    print("scanned %d defs, wrote %d rows -> %s" % (n, kept, OUT),
          file=sys.stderr)


if __name__ == "__main__":
    main()
