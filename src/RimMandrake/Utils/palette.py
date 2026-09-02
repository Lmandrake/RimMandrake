#!/usr/bin/env python3
"""
palette.py - load a material palette from Palettes/<name>.md, and check it.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/

A palette is an ordinary markdown document whose DATA lives in one fenced
```palette block. Prose is for humans; the block is what generators import, so a
generator can no longer quietly contradict the palette it was built from.

🔑 A PALETTE HOLDS OPTIONS. A RAMP IS A CHOICE.
The palette is the full legitimate option set for a material + condition - rust
really can be saturated orange. A `ramp` is one ordered selection through it, and
`used` records which ramp a build actually took. Nothing is "forbidden": a colour
that a given ship did not use is simply in a ramp that ship did not take. Do not
delete options because one build passed them over.

GRAMMAR - one statement per line, `#` starts a comment.

    color NAME  R,G,B                  @mod=<Mod>  | human description
    role  ROLE  <TerrainDef|->         @mod=<Mod>  | human description
    thing ROLE  <ThingDef>             @mod=<Mod>  | human description
    ramp  NAME  A > B > C                          | human description
    stuff ROLE  key=<ThingDef> ...     @mod=<Mod>  | human description
    param NAME  VALUE                              | human description
    rule  <a hard constraint, in words>
    used  <which ramps a real build took, and where>

`role` names a floor, `thing` names an object - a palette may be either or both
(machinewreck is things, flooring_rusted is floors). `-` as a role's def means "no
floor here" (a hole). `@mod=` is the mod that
SUPPLIES the def; --check reads the def dump and reports a name that has moved
mods or vanished, which is how a palette fails silently when a mod leaves.

⚠️ --check ALSO CONSULTS cherrypicker.py (2026-09-02, DUMP_DERIVED_SHEETS_SHOW_CUT_1).
The def dump is captured before Cherry Picker removes anything, so a def a palette
names can be present and correctly-typed in the dump and STILL be cut from the
shipped game - the check would read clean while a build using this palette places a
floor or wreck piece nobody will ever see in-game. A cut def is reported as its own
CUT class, never folded into a clean pass.
"""

import argparse
import io
import os
import re
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PALETTE_DIR = os.path.join(REPO, "Palettes")

sys.path.insert(0, HERE)
import cherrypicker  # noqa: E402

DEFAULT_DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                "RimWorld by Ludeon Studios/DefDump/defs.sqlite")

BLOCK = re.compile(r"^```palette\s*$(.*?)^```\s*$", re.M | re.S)


class PaletteError(Exception):
    pass


def _split(line):
    """-> (verb, tokens, mod, description). Order of stripping matters."""
    line = line.split("#", 1)[0].rstrip()
    desc = None
    if "|" in line:
        line, desc = line.split("|", 1)
        desc = desc.strip()
    mod = None
    if "@mod=" in line:
        line, mod = line.split("@mod=", 1)
        mod = mod.strip()
    parts = line.split()
    if not parts:
        return None, [], None, None
    return parts[0], parts[1:], mod, desc


class Palette(object):
    """Everything one material + condition may be built from."""

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.colors = {}        # ColorDef -> (r, g, b);  None -> (255,255,255)
        self.roles = {}         # ROLE -> TerrainDef or None
        self.things = {}        # ROLE -> ThingDef (wreckage, junk, debris)
        self.ramps = {}         # ramp name -> [ColorDef or None, ...]
        self.stuff = {}         # ROLE -> {key: ThingDef}
        self.params = {}        # name -> string
        self.rules = []
        self.used = []
        self.mods = {}          # defName -> mod that should supply it
        self.desc = {}          # defName or ramp name -> human description

    # ---------------------------------------------------------------- loading

    @classmethod
    def load(cls, ref):
        """`ref` is a path, or a bare palette name resolved under Palettes/."""
        path = ref
        if not os.path.exists(path):
            path = os.path.join(PALETTE_DIR, ref if ref.endswith(".md") else ref + ".md")
        if not os.path.exists(path):
            raise PaletteError("no palette %r (looked in %s)" % (ref, PALETTE_DIR))
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        m = BLOCK.search(text)
        if not m:
            raise PaletteError("%s has no ```palette block" % path)
        p = cls(os.path.splitext(os.path.basename(path))[0], path)
        p._parse(m.group(1))
        p._validate_internal()
        return p

    def _parse(self, body):
        for n, raw in enumerate(body.splitlines(), 1):
            verb, tok, mod, desc = _split(raw)
            if verb is None:
                continue
            try:
                self._statement(verb, tok, mod, desc, raw)
            except PaletteError:
                raise
            except Exception as exc:
                raise PaletteError("%s line %d: %s (%r)" % (self.path, n, exc, raw.strip()))

    def _statement(self, verb, tok, mod, desc, raw):
        if verb == "color":
            name = tok[0]
            rgb = tuple(int(v) for v in tok[1].split(","))
            if len(rgb) != 3:
                raise PaletteError("colour %s needs R,G,B" % name)
            self.colors[name] = rgb
        elif verb == "role":
            name = tok[0]
            self.roles[name] = None if tok[1] == "-" else tok[1]
        elif verb == "thing":
            # A palette of OBJECTS rather than floors - wreckage, junk, debris.
            # Same shape as `role`, but --check expects a ThingDef.
            name = tok[0]
            self.things[name] = tok[1]
        elif verb == "ramp":
            name = tok[0]
            seq = [s.strip() for s in " ".join(tok[1:]).split(">")]
            self.ramps[name] = [None if s == "-" else s for s in seq if s]
            name = "ramp:" + name
        elif verb == "stuff":
            # MERGES, so one role's materials may come from different mods and
            # each line can carry its own @mod=.
            name = tok[0]
            self.stuff.setdefault(name, {}).update(
                dict(kv.split("=", 1) for kv in tok[1:]))
            # ⚠️ namespaced: a `stuff HULL` description must not overwrite the
            # description of `role HULL`. They share a name and mean different things.
            name = "stuff:" + name
        elif verb == "param":
            name = tok[0]
            self.params[name] = tok[1]
        elif verb == "rule":
            self.rules.append(" ".join(tok) + (" " + desc if desc else ""))
            return
        elif verb == "used":
            self.used.append(" ".join(tok) + (" " + desc if desc else ""))
            return
        else:
            raise PaletteError("unknown verb %r" % verb)
        if mod:
            for d in self._defs_of(verb, tok):
                self.mods[d] = mod
        if desc:
            self.desc[name] = desc

    @staticmethod
    def _defs_of(verb, tok):
        if verb in ("role", "thing"):
            return [tok[1]] if tok[1] != "-" else []
        if verb == "color":
            return [tok[0]]
        if verb == "stuff":
            return [kv.split("=", 1)[1] for kv in tok[1:]]
        return []

    def _validate_internal(self):
        """Every ramp must name colours the palette declares. Caught here, not live."""
        bad = []
        for rname, seq in self.ramps.items():
            for c in seq:
                if c is not None and c not in self.colors:
                    bad.append("ramp %s names undeclared colour %s" % (rname, c))
        if bad:
            raise PaletteError("%s: %s" % (self.path, "; ".join(bad)))

    # ------------------------------------------------------------- using it

    def rgb(self, color):
        """The RGB the game MULTIPLIES by. None (no colour) is white."""
        if color is None:
            return (255, 255, 255)
        return self.colors[color]

    def ramp(self, name):
        if name not in self.ramps:
            raise PaletteError("%s has no ramp %r (has %s)"
                               % (self.name, name, ", ".join(sorted(self.ramps))))
        return list(self.ramps[name])

    def role(self, name):
        if name not in self.roles:
            raise PaletteError("%s has no role %r (has %s)"
                               % (self.name, name, ", ".join(sorted(self.roles))))
        return self.roles[name]

    def color_table(self):
        """{name: rgb} plus the None -> white entry generators expect."""
        out = dict(self.colors)
        out[None] = (255, 255, 255)
        return out

    def __repr__(self):
        return "<Palette %s: %d colours, %d roles, %d things, %d ramps>" % (
            self.name, len(self.colors), len(self.roles), len(self.things),
            len(self.ramps))


# ------------------------------------------------------------------- checking

def check(p, dump=DEFAULT_DUMP):
    """Every def in the palette, against the def dump AND Cherry Picker's live cut
    list. Returns (problems, cut_provenance_line)."""
    if not os.path.exists(dump):
        return ["UNMEASURED: no def dump at %s - run refresh.py" % dump], None
    cuts = cherrypicker.load()
    want = {}
    for name in self_defs(p):
        want[name] = None
    con = sqlite3.connect(dump)
    # ⚠️ ONE defName can carry SEVERAL def types - GravshipHull and ChunkSlagSteel
    # are each a SymbolDef *and* a ThingDef. Keeping only the first row makes the
    # type check answer about whichever the dump happened to return first, so
    # collect every row and let any one of them satisfy the expectation.
    got = {}
    names = list(want)
    for i in range(0, len(names), 400):
        chunk = names[i:i + 400]
        q = ("select def_name, def_type, mod_name from defs where def_name in (%s)"
             % ",".join("?" * len(chunk)))
        for dn, dt, mn in con.execute(q, chunk):
            got.setdefault(dn, []).append((dt, mn))
    con.close()

    expect_type = {}
    for c in p.colors:
        expect_type[c] = "ColorDef"
    for r, d in p.roles.items():
        if d:
            expect_type[d] = "TerrainDef"
    for r, d in p.things.items():
        expect_type[d] = "ThingDef"
    for r, kv in p.stuff.items():
        for d in kv.values():
            expect_type[d] = "ThingDef"

    problems = []
    for name in sorted(want):
        if name not in got:
            problems.append("MISSING  %-45s no such def in the dump" % name)
            continue
        rows = got[name]
        exp = expect_type.get(name)
        if exp and not any(dt == exp for dt, _ in rows):
            problems.append("WRONGTYPE %-44s is %s, palette uses it as %s"
                            % (name, "/".join(sorted(set(dt for dt, _ in rows))), exp))
            continue
        declared = p.mods.get(name)
        mods = set(mn for dt, mn in rows if mn and (not exp or dt == exp))
        if declared and mods and declared not in mods:
            problems.append("MOVED    %-45s dump says %s, palette says %r"
                            % (name, "/".join(sorted(repr(m) for m in mods)), declared))
            continue
        # Present, correctly typed, correct mod - and STILL cut. The dump precedes
        # Cherry Picker, so this is the one class none of the checks above can see.
        if any(cuts.cut(dt, name) for dt, _ in rows):
            problems.append("CUT      %-45s present in the dump, cut from the shipped "
                            "game" % name)
    return problems, cuts.provenance()


def self_defs(p):
    out = set(p.colors)
    out |= set(d for d in p.roles.values() if d)
    out |= set(p.things.values())
    for kv in p.stuff.values():
        out |= set(kv.values())
    return out


def main():
    ap = argparse.ArgumentParser(description="load and check a material palette")
    ap.add_argument("palette", help="a name (flooring_rusted) or a path")
    ap.add_argument("--check", action="store_true",
                    help="validate every def against the def dump")
    ap.add_argument("--dump", default=DEFAULT_DUMP)
    a = ap.parse_args()

    try:
        p = Palette.load(a.palette)
    except PaletteError as exc:
        print("PALETTE ERROR: %s" % exc)
        return 1
    print("%s  %s" % (p.path, p))
    for r in sorted(p.roles):
        print("  role  %-10s %s" % (r, p.roles[r] or "- (hole)"))
    for r in sorted(p.things):
        print("  thing %-10s %s" % (r, p.things[r]))
    for r in sorted(p.ramps):
        print("  ramp  %-16s %s" % (r, " > ".join(str(c) for c in p.ramps[r])))
    for r in sorted(p.stuff):
        print("  stuff %-10s %s" % (r, p.stuff[r]))
    for k in sorted(p.params):
        print("  param %-16s %s" % (k, p.params[k]))
    for r in p.rules:
        print("  RULE  %s" % r)
    for u in p.used:
        print("  used  %s" % u)

    if a.check:
        problems, cut_provenance = check(p, a.dump)
        n = len(self_defs(p))
        if cut_provenance:
            print("\n%s" % cut_provenance)
        if problems:
            print("check: %d problem(s) over %d defs" % (len(problems), n))
            for x in problems:
                print("  " + x)
            return 1
        print("check: MEASURED %d of %d defs present, types and mods agree, none cut"
              % (n, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
