#!/usr/bin/env python3
"""
cherrypicker.py — what the running game does NOT have, for anything projecting
over the def dump.

VERSION 1.0  (2026-08-27)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHY THIS EXISTS
===============
🔴 THE DEF DUMP IS CAPTURED BEFORE CHERRY PICKER REMOVES ANYTHING. A cut that
worked is PRESENT in the dump. The dump cannot answer "is this cut" in either
direction — measured 2026-08-23, `infrastructure/state/facts/dump-is-pre-cherrypicker.md`.

The cost was not theoretical. The owner reviewed a creature art sheet built from
the dump and said *"I had really thought I had already removed all of these
terrestrial animals somewhere already."* He had. The sheet was wrong, not his
memory — 1,162 of his 1,289 ThingDef cuts were still in it. He spent a review
pass judging animals the game no longer has, and asked a question that read as a
memory failure and was actually an instrument failure. That is
`DUMP_DERIVED_SHEETS_SHOW_CUT_1`, and this module is its single source.

⛔ DO NOT ADD A TENTH PARSER. Eight scripts already open the settings file with
their own regex, which is the drift machine CLAUDE.md names: "Single-source only
what a GENERATOR can enforce." This module is the thing to import; when you touch
one of those scripts, move it onto this and delete its copy.

⛔ AND DO NOT "FIX" THE PROBLEM BY RE-CAPTURING THE DUMP LATER IN LOAD. The
dump's job is the AUTHORED def set; the kill list's job is WHAT SURVIVES. Two
questions, two instruments. Joining them is this module's whole purpose.

THE INTERFACE
=============
    import cherrypicker

    cuts = cherrypicker.load()
    cuts.cut("ThingDef", "Cat")            # -> True
    cuts.cut_name("Cat")                   # -> True, type-agnostic
    kept, dropped = cuts.filter(rows, key=lambda r: ("ThingDef", r["defName"]))
    print(cuts.provenance())               # the line an artifact must carry

⭐ EVERY ARTIFACT THAT FILTERS MUST SAY SO, AND SAY HOW MANY ROWS IT SUPPRESSED.
A sheet that silently shows fewer things is the same instrument failure wearing
the other hat — the owner cannot tell "this mod ships nothing" from "I cut it
all". `provenance()` exists so there is no excuse not to print it.

WHAT IT IS NOT
==============
⚠️ This reads the SETTINGS FILE — Cherry Picker's INTENT, i.e. what will be
removed at the next load. It is not proof any removal SUCCEEDED. Three of Cherry
Picker's four failure modes are silent (see `cherrypick_build.py`), so a key here
can resolve to nothing and never say so.

🔑 Runtime truth is `Player.log`'s removal block — the lines after
`[Cherry Picker] The database was processed in`. `from_log()` reads it when you
have a log from the load you care about. Prefer it for a claim about a game that
actually ran; prefer the settings file for a claim about what the next load will
do. `load()` says which one it used, in `provenance()`.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_paths as GP                       # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SETTINGS = os.path.join(GP.LOCALLOW, "Config", "Mod_3521312241_Mod_CherryPicker.xml")
# The owner's RATIFIED list, tracked in git. `cherrypick_build.py` treats it as the
# anchor it never drops a key from; here it is the fallback for a machine with no
# LocalLow — a checkout on another disk still gets a real answer.
RATIFIED = os.path.join(REPO, "deployed", "config", "v1_freeze",
                        "Mod_3521312241_Mod_CherryPicker.xml")

_KEY = re.compile(r"<li>\s*([^<>/\s]+)\s*/\s*([^<>\s]+?)\s*</li>")
# Cherry Picker's own report lines: "	 - ThingDef/Cat," one per removal.
_LOG = re.compile(r"^\s*-\s*([A-Za-z]+)/([^,\s]+),?\s*$")


class Cuts(object):
    """The set of defs the game will not have. Immutable once loaded."""

    __slots__ = ("keys", "names", "by_type", "path", "source", "mtime")

    def __init__(self, keys, path, source):
        self.keys = frozenset(keys)                      # {"ThingDef/Cat", ...}
        self.names = frozenset(k.split("/", 1)[1] for k in self.keys)
        by_type = {}
        for k in self.keys:
            t, n = k.split("/", 1)
            by_type.setdefault(t, set()).add(n)
        self.by_type = {t: frozenset(n) for t, n in by_type.items()}
        self.path, self.source = path, source
        try:
            self.mtime = os.path.getmtime(path) if path else 0.0
        except OSError:
            self.mtime = 0.0

    def __len__(self):
        return len(self.keys)

    def cut(self, deftype, defname):
        """-> True if this exact typed def is on the list."""
        return ("%s/%s" % (deftype, defname)) in self.keys

    def cut_name(self, defname):
        """-> True if ANY type of that name is cut.

        ⚠️ Type-agnostic on purpose, for the callers that have a defName and no
        type — the review sheets work in defNames. It can only over-report, never
        under-report, and over-reporting a cut hides a row rather than showing the
        owner a thing that no longer exists. That is the safer direction here.
        """
        return defname in self.names

    def filter(self, rows, key):
        """-> (kept, dropped). `key(row)` returns "Name" or ("Type", "Name")."""
        kept, dropped = [], []
        for r in rows:
            k = key(r)
            gone = self.cut(*k) if isinstance(k, tuple) else self.cut_name(k)
            (dropped if gone else kept).append(r)
        return kept, dropped

    def provenance(self, suppressed=None):
        """The line an artifact MUST carry. Never print a filtered sheet without it."""
        import time
        when = (time.strftime("%Y-%m-%d %H:%M", time.localtime(self.mtime))
                if self.mtime else "unknown")
        line = ("cut list: %d defs, %s, %s (%s)"
                % (len(self.keys), self.source, when, self.path or "-"))
        if suppressed is not None:
            line += "  |  %d row%s suppressed as cut" % (
                suppressed, "" if suppressed == 1 else "s")
        return line


def _parse_settings(path):
    with open(path, encoding="utf-8") as fh:
        return set("%s/%s" % m for m in _KEY.findall(fh.read()))


def load(source="auto"):
    """-> Cuts. `source` is "auto" | "live" | "ratified".

    "auto" prefers the live settings file and falls back to the ratified repo
    copy. ⚠️ It NEVER silently returns an empty set: a machine with neither file
    raises, because "nothing is cut" and "I could not look" must not read alike —
    that equivalence is exactly the bug this module exists to kill.
    """
    tries = {"auto": ((SETTINGS, "live settings"), (RATIFIED, "ratified repo copy")),
             "live": ((SETTINGS, "live settings"),),
             "ratified": ((RATIFIED, "ratified repo copy"),)}[source]
    problems = []
    for path, label in tries:
        try:
            return Cuts(_parse_settings(path), path, label)
        except OSError as exc:
            problems.append("%s: %s" % (path, exc))
    raise IOError(
        "no Cherry Picker list readable, so nothing can be said about what the game "
        "actually has.\n  " + "\n  ".join(problems) +
        "\n  Pass source='ratified' for the git copy, or run cherrypick_build.py.")


def from_log(path=None):
    """-> Cuts, from `Player.log`'s removal block. RUNTIME TRUTH, not intent.

    🔑 This is what a load ACTUALLY removed, and it is the only source that can
    prove a key resolved. It is also destroyed at the next launch — harvest the
    log before relaunching or this answer is gone.
    """
    path = path or os.path.join(GP.LOCALLOW, "Player.log")
    keys, inside = set(), False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "[Cherry Picker]" in line and "was processed in" in line:
                inside = True
                continue
            if inside:
                m = _LOG.match(line)
                if m:
                    keys.add("%s/%s" % m.groups())
                elif line.strip():
                    break
    if not keys:
        raise IOError("no Cherry Picker removal block in %s — the log is from a load "
                      "where it did not run, or has already been overwritten." % path)
    return Cuts(keys, path, "Player.log removal block")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("--source", choices=("auto", "live", "ratified", "log"),
                    default="auto")
    ap.add_argument("--type", default="", help="list the cut names of one def type")
    ap.add_argument("--is-cut", default="", metavar="Type/Name")
    a = ap.parse_args(argv)

    cuts = from_log() if a.source == "log" else load(a.source)
    print(cuts.provenance())
    if a.is_cut:
        t, _, n = a.is_cut.partition("/")
        print("%s: %s" % (a.is_cut, "CUT" if (cuts.cut(t, n) if n else
                                              cuts.cut_name(t)) else "present"))
        return 0
    if a.type:
        for n in sorted(cuts.by_type.get(a.type, ())):
            print(n)
        return 0
    for t in sorted(cuts.by_type, key=lambda k: -len(cuts.by_type[k])):
        print("%-16s %5d" % (t, len(cuts.by_type[t])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
