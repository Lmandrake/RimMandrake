#!/usr/bin/env python3
"""Read and WRITE RimWorld gravship layout files (ShipLayoutDefV2).

Gravship Exporter saves a built ship as XML. This module treats that format as
an authoring surface: a ship can be written directly, with no map, no build, no
bridge and no game running. That turns "build it live, then export" into
"write it, then import".

    python3 src/RimMandrake/Utils/gravship_layout.py --roundtrip <file.xml>
    python3 src/RimMandrake/Utils/gravship_layout.py --info <file.xml>
    python3 src/RimMandrake/Utils/gravship_layout.py --demo <out.xml>

FORMAT, read off a real export (2026-08-13, our v1 ship, 4,057 cells /
1,052 things) rather than from any documentation:

    <ShipLayoutDefV2>
      <rows>
        <li>                          one <li> per ROW
          <li IsNull="True" />        one <li> per COLUMN in that row; empty cell
          <li>                        a populated cell
            <foundationDef>Substructure</foundationDef>
            <foundationStuff IsNull="True" />
            <terrainDef>MetalTile</terrainDef>
            <terrainStuff IsNull="True" />
            <things>
              <li>
                <defName>GravshipHull</defName>
                <stuffDef>Steel</stuffDef>      omit/null for stuffless defs
                <rotInteger>0</rotInteger>      0=N 1=E 2=S 3=W
                <quality IsNull="True" />
                <plantToGrowDef IsNull="True" />
                <exportedStorageSettings IsNull="True" />
                <compSettings IsNull="True" />
              </li>
            </things>
          </li>
        </li>
      </rows>
      <width>88</width>  <height>135</height>
      <gravEngineX>45</gravEngineX>  <gravEngineZ>92</gravEngineZ>
      <defName>Gravship</defName>  <label>Gravship</label>
      <descriptionHyperlinks IsNull="True" />
      <ignoreIllegalLabelCharacterConfigError>False</...>
    </ShipLayoutDefV2>

⚠️ THINGS THAT WILL BITE YOU, all measured:
 * `width`/`height` are the GRID, which carries a 1-cell empty margin on every
   side. Our 86x133 hull exported as 88x135. Author the margin or the engine
   sits one cell off from where you think.
 * `gravEngineX/Z` are LAYOUT-LOCAL, not map coordinates, and they include that
   margin. Engine at map (126,149) in a footprint starting (82,58) exported as
   (45,92), not (44,91).
 * A multi-cell building appears ONCE, in the cell the game considers its
   position -- not in every cell it covers.
 * `IsNull="True"` is how this format writes "absent". An empty element is NOT
   the same thing and RimWorld's scribe will read it as a value.
 * The file is written with a UTF-8 BOM. Preserved here; harmless either way.
"""
import argparse
import os
import sys
import xml.etree.ElementTree as ET

NULL = {"IsNull": "True"}


class Thing(object):
    __slots__ = ("defName", "stuffDef", "rot", "quality", "plantToGrow")

    def __init__(self, defName, stuffDef=None, rot=0, quality=None,
                 plantToGrow=None):
        self.defName = defName
        self.stuffDef = stuffDef
        self.rot = rot
        self.quality = quality
        self.plantToGrow = plantToGrow

    def __repr__(self):
        return "Thing(%s%s%s)" % (
            self.defName,
            ", " + self.stuffDef if self.stuffDef else "",
            ", rot=%d" % self.rot if self.rot else "")


class Cell(object):
    __slots__ = ("foundationDef", "terrainDef", "things")

    def __init__(self, foundationDef=None, terrainDef=None, things=None):
        self.foundationDef = foundationDef
        self.terrainDef = terrainDef
        self.things = things or []

    def empty(self):
        return not (self.foundationDef or self.terrainDef or self.things)


class Layout(object):
    """A gravship layout. Indexed [z][x] -- row major, matching the file."""

    def __init__(self, width, height, defName="Gravship", label=None,
                 gravEngineX=None, gravEngineZ=None):
        self.width = width
        self.height = height
        self.defName = defName
        self.label = label or defName
        self.gravEngineX = gravEngineX
        self.gravEngineZ = gravEngineZ
        self.rows = [[Cell() for _ in range(width)] for _ in range(height)]

    # -- access -------------------------------------------------------------
    def cell(self, x, z):
        return self.rows[z][x]

    def put(self, x, z, defName, stuff=None, rot=0, terrain=None,
            foundation="Substructure"):
        c = self.rows[z][x]
        if foundation:
            c.foundationDef = foundation
        if terrain:
            c.terrainDef = terrain
        c.things.append(Thing(defName, stuff, rot))
        return c

    def floor(self, x, z, terrain, foundation="Substructure"):
        c = self.rows[z][x]
        c.terrainDef = terrain
        if foundation:
            c.foundationDef = foundation
        return c

    def counts(self):
        terr = things = found = 0
        per = {}
        for row in self.rows:
            for c in row:
                if c.terrainDef:
                    terr += 1
                if c.foundationDef:
                    found += 1
                for t in c.things:
                    things += 1
                    per[t.defName] = per.get(t.defName, 0) + 1
        return {"terrainCells": terr, "foundationCells": found,
                "things": things, "perDef": per}

    # -- io -----------------------------------------------------------------
    @classmethod
    def load(cls, path):
        root = ET.parse(path).getroot()
        if root.tag != "ShipLayoutDefV2":
            raise ValueError("not a ShipLayoutDefV2: root is <%s>" % root.tag)

        def txt(parent, tag, default=None):
            e = parent.find(tag)
            if e is None or e.get("IsNull") == "True":
                return default
            return e.text

        w = int(txt(root, "width", "0"))
        h = int(txt(root, "height", "0"))
        lay = cls(w, h, txt(root, "defName", "Gravship"), txt(root, "label"))
        gx, gz = txt(root, "gravEngineX"), txt(root, "gravEngineZ")
        lay.gravEngineX = int(gx) if gx is not None else None
        lay.gravEngineZ = int(gz) if gz is not None else None

        rows = root.find("rows")
        for z, rowEl in enumerate(rows.findall("li")):
            for x, cellEl in enumerate(rowEl.findall("li")):
                if cellEl.get("IsNull") == "True":
                    continue
                c = lay.rows[z][x]
                c.foundationDef = txt(cellEl, "foundationDef")
                c.terrainDef = txt(cellEl, "terrainDef")
                thingsEl = cellEl.find("things")
                if thingsEl is not None and thingsEl.get("IsNull") != "True":
                    for tEl in thingsEl.findall("li"):
                        c.things.append(Thing(
                            txt(tEl, "defName"),
                            txt(tEl, "stuffDef"),
                            int(txt(tEl, "rotInteger", "0") or 0),
                            txt(tEl, "quality"),
                            txt(tEl, "plantToGrowDef")))
        return lay

    def to_element(self):
        root = ET.Element("ShipLayoutDefV2")
        rows = ET.SubElement(root, "rows")
        for z in range(self.height):
            rowEl = ET.SubElement(rows, "li")
            for x in range(self.width):
                c = self.rows[z][x]
                if c.empty():
                    ET.SubElement(rowEl, "li", NULL)
                    continue
                cellEl = ET.SubElement(rowEl, "li")
                _opt(cellEl, "foundationDef", c.foundationDef)
                ET.SubElement(cellEl, "foundationStuff", NULL)
                _opt(cellEl, "terrainDef", c.terrainDef)
                ET.SubElement(cellEl, "terrainStuff", NULL)
                thingsEl = ET.SubElement(cellEl, "things")
                for t in c.things:
                    tEl = ET.SubElement(thingsEl, "li")
                    ET.SubElement(tEl, "defName").text = t.defName
                    _opt(tEl, "stuffDef", t.stuffDef)
                    ET.SubElement(tEl, "rotInteger").text = str(t.rot)
                    _opt(tEl, "quality", t.quality)
                    _opt(tEl, "plantToGrowDef", t.plantToGrow)
                    ET.SubElement(tEl, "exportedStorageSettings", NULL)
                    ET.SubElement(tEl, "compSettings", NULL)
        ET.SubElement(root, "width").text = str(self.width)
        ET.SubElement(root, "height").text = str(self.height)
        if self.gravEngineX is not None and self.gravEngineZ is not None:
            ET.SubElement(root, "gravEngineX").text = str(self.gravEngineX)
            ET.SubElement(root, "gravEngineZ").text = str(self.gravEngineZ)
        ET.SubElement(root, "defName").text = self.defName
        ET.SubElement(root, "label").text = self.label
        ET.SubElement(root, "descriptionHyperlinks", NULL)
        ET.SubElement(root, "ignoreIllegalLabelCharacterConfigError").text = "False"
        return root

    def save(self, path):
        el = self.to_element()
        _indent(el)
        xml = ET.tostring(el, encoding="unicode")
        with open(path, "w", encoding="utf-8-sig") as fh:
            fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
            fh.write(xml)
            fh.write("\n")
        return path

    def validate(self):
        """Problems that make a layout silently wrong rather than invalid."""
        bad = []
        if self.gravEngineX is None:
            bad.append("no gravEngineX/Z -- the game needs the engine's cell")
        else:
            if not (0 <= self.gravEngineX < self.width
                    and 0 <= self.gravEngineZ < self.height):
                bad.append("grav engine (%s,%s) outside the %dx%d grid"
                           % (self.gravEngineX, self.gravEngineZ,
                              self.width, self.height))
            else:
                c = self.rows[self.gravEngineZ][self.gravEngineX]
                if not any("GravEngine" in t.defName for t in c.things):
                    bad.append(
                        "gravEngineX/Z points at (%d,%d) but no GravEngine is "
                        "in that cell -- the coordinates are LAYOUT-LOCAL and "
                        "include the 1-cell margin; this is the usual slip"
                        % (self.gravEngineX, self.gravEngineZ))
        for z, row in enumerate(self.rows):
            for x, c in enumerate(row):
                if c.things and not c.foundationDef:
                    bad.append("thing at (%d,%d) with no foundation -- it will "
                               "not be part of the ship" % (x, z))
        return bad


def _opt(parent, tag, value):
    e = ET.SubElement(parent, tag)
    if value is None:
        e.set("IsNull", "True")
    else:
        e.text = str(value)
    return e


def _indent(el, level=0):
    pad = "\n" + "  " * level
    if len(el):
        if not (el.text or "").strip():
            el.text = pad + "  "
        for child in el:
            _indent(child, level + 1)
        if not (el.tail or "").strip():
            el.tail = pad
    elif level and not (el.tail or "").strip():
        el.tail = pad


def roundtrip(path):
    """Parse, re-emit, parse again, and compare cell by cell.

    This is the proof that the format is understood. A doc claiming to
    describe a format is not evidence; a file that survives a round trip is.
    """
    a = Layout.load(path)
    tmp = path + ".roundtrip.tmp"
    a.save(tmp)
    b = Layout.load(tmp)
    os.remove(tmp)

    diffs = []
    for attr in ("width", "height", "defName", "label",
                 "gravEngineX", "gravEngineZ"):
        if getattr(a, attr) != getattr(b, attr):
            diffs.append("%s: %r != %r" % (attr, getattr(a, attr),
                                           getattr(b, attr)))
    for z in range(min(a.height, b.height)):
        for x in range(min(a.width, b.width)):
            ca, cb = a.rows[z][x], b.rows[z][x]
            if ca.foundationDef != cb.foundationDef:
                diffs.append("(%d,%d) foundation %r != %r"
                             % (x, z, ca.foundationDef, cb.foundationDef))
            if ca.terrainDef != cb.terrainDef:
                diffs.append("(%d,%d) terrain %r != %r"
                             % (x, z, ca.terrainDef, cb.terrainDef))
            if len(ca.things) != len(cb.things):
                diffs.append("(%d,%d) %d things != %d"
                             % (x, z, len(ca.things), len(cb.things)))
            else:
                for ta, tb in zip(ca.things, cb.things):
                    # 🔴 was (defName, stuffDef, rot) only -- quality and
                    # plantToGrow are loaded and stored on every Thing but were
                    # never compared, so a bug that silently dropped one of
                    # them on export still printed "round trip clean". Proven
                    # 2026-09-03: monkeypatching quality to None during
                    # to_element() produced zero diffs.
                    if (ta.defName, ta.stuffDef, ta.rot, ta.quality, ta.plantToGrow) != \
                       (tb.defName, tb.stuffDef, tb.rot, tb.quality, tb.plantToGrow):
                        diffs.append("(%d,%d) thing %r != %r" % (x, z, ta, tb))
            if len(diffs) > 20:
                return a, diffs
    return a, diffs


def demo(path):
    """A minimal hand-authored ship, written from nothing."""
    lay = Layout(9, 9, defName="JawaTestSled", label="Jawa test sled")
    for z in range(1, 8):
        for x in range(1, 8):
            lay.floor(x, z, "MetalTile")
    for x in range(1, 8):
        lay.put(x, 1, "GravshipHull", "Steel", terrain="MetalTile")
        lay.put(x, 7, "GravshipHull", "Steel", terrain="MetalTile")
    for z in range(2, 7):
        lay.put(1, z, "GravshipHull", "Steel", terrain="MetalTile")
        lay.put(7, z, "GravshipHull", "Steel", terrain="MetalTile")
    lay.put(4, 4, "GravEngine", terrain="MetalTile")
    lay.gravEngineX, lay.gravEngineZ = 4, 4
    lay.save(path)
    return lay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roundtrip", metavar="FILE")
    ap.add_argument("--info", metavar="FILE")
    ap.add_argument("--demo", metavar="OUT")
    a = ap.parse_args()

    if a.info:
        lay = Layout.load(a.info)
        c = lay.counts()
        print("%s  %dx%d  engine (%s,%s)" % (lay.defName, lay.width, lay.height,
                                             lay.gravEngineX, lay.gravEngineZ))
        print("  foundation %d, terrain %d, things %d"
              % (c["foundationCells"], c["terrainCells"], c["things"]))
        for d, n in sorted(c["perDef"].items(), key=lambda kv: -kv[1])[:12]:
            print("    %-36s %d" % (d, n))
        bad = lay.validate()
        print("  validate: %s" % ("OK" if not bad else "%d problem(s)" % len(bad)))
        for b in bad:
            print("    ⚠️ %s" % b)
        return

    if a.roundtrip:
        lay, diffs = roundtrip(a.roundtrip)
        c = lay.counts()
        print("parsed %dx%d, %d foundation, %d terrain, %d things"
              % (lay.width, lay.height, c["foundationCells"],
                 c["terrainCells"], c["things"]))
        if diffs:
            print("🔴 ROUND TRIP FAILED, %d difference(s):" % len(diffs))
            for d in diffs[:20]:
                print("   " + d)
            sys.exit(1)
        print("✅ round trip clean -- every cell, thing, stuff and rotation "
              "survived write+reread. The format is understood.")
        return

    if a.demo:
        lay = demo(a.demo)
        c = lay.counts()
        print("wrote %s: %dx%d, %d things, engine (%d,%d)"
              % (a.demo, lay.width, lay.height, c["things"],
                 lay.gravEngineX, lay.gravEngineZ))
        bad = lay.validate()
        print("validate: %s" % ("OK" if not bad else bad))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
