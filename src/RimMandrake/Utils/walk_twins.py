#!/usr/bin/env python3
"""walk_twins.py: every station of a walk save that shows an aftermath has a START twin beside it.

Page: design/specs/2026-11-24-walk-save-start-twin/boundary.md. Why: on 2026-11-23 the owner could not judge stations 10 and
14 of the Explosive Knockback walk ("these are hard tests to evaluate given I can't see their initial states").

    python3 src/RimMandrake/Utils/walk_twins.py check <save name or path, .rws>     one save
    python3 src/RimMandrake/Utils/walk_twins.py check --mod <Mod>                    the save the newest visit's Exit block names

Exit 0 every aftermath station has its twin (or the save has stations and none is an aftermath); 1 one has not, each named;
2 could not look (no such save, no station sign in it, no visit).

A sign's title is "SIGN <key> <name>[ - DO: ...]" (reviewmap.sign_book). The name's last word is the tag:
    AFTER   the station stands as the event left it
    START   its twin: the same scene as it stood before the event, nothing armed, on its own cell, same key and name
A sign with no tag that quotes a scene's "proof verdict" shows that finished scene, so it is an aftermath too.
"""
import functools
import html
import mmap
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

PREFIX = "SIGN "
VERDICT = re.compile(r"\bproof verdict\b", re.I)
REPAIR = ("Stage each scene again beside its AFTER site, remove what would set it off before any tick, and give it a sign with the "
          "same key and name and the tag START (design/concepts/ExplosiveKnockback/version/in_game/visit_6/scripts/walk_save.py "
          "does it), then save under a new name")


class CouldNotLook(Exception):
    pass


def station(title, body, x, z):
    """-> {key, name, tag, x, z} of one sign; tag: AFTER, START or None (the station shows no finished event)."""
    t = " ".join(title[len(PREFIX):].split()).split(" - DO:")[0]
    key, _, name = t.partition(" ")
    words = name.split()
    tag = words[-1] if words and words[-1] in ("AFTER", "START") else None
    if tag:
        words = words[:-1]
    elif VERDICT.search("%s %s" % (title, body)):
        tag = "AFTER"
    return {"key": key, "name": " ".join(words), "tag": tag, "x": x, "z": z}


def of_ops(ops):
    """The stations of jawa/review_sign place ops ('x|z|title|body' lines); a line that is no sign book is skipped."""
    out = []
    for ln in (ops.split("\n") if isinstance(ops, str) else ops or []):
        f = ln.strip().split("|", 3)
        if len(f) == 4 and f[2].startswith(PREFIX):
            out.append(station(f[2], f[3], f[0].strip(), f[1].strip()))
    return out


def of_save(path):
    """The stations whose sign books lie in the .rws file. Raises CouldNotLook when the file cannot be read. One process reads
    one file once (the exit is read several times in a call, and 36 MB over /mnt is about 4 s)."""
    try:
        st = os.stat(path)
    except OSError as e:
        raise CouldNotLook("%s could not be read (%s: %s)" % (path, type(e).__name__, e))
    return list(_of_save(path, st.st_size, st.st_mtime_ns))


@functools.lru_cache(maxsize=None)
def _of_save(path, _size, _mtime):
    out = []
    try:
        with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
            at = 0
            while True:             # from each title back to its <thing>: a regex from every <thing> reads 30 MB many times
                i = m.find(b"<title>" + PREFIX.encode(), at)
                if i < 0:
                    break
                a, b = m.rfind(b"<thing Class=", 0, i), m.find(b"</thing>", i)
                txt = m[max(a, 0):b if b > 0 else i + 4000].decode("utf-8", "replace")
                title = re.search(r"<title>(.*?)</title>", txt, re.S)
                pos = re.search(r"<pos>\((-?\d+), *-?\d+, *(-?\d+)\)</pos>", txt)
                if title:
                    out.append(station(html.unescape(title.group(1)), html.unescape(txt[title.end():]),
                                       pos.group(1) if pos else "?", pos.group(2) if pos else "?"))
                at = b if b > 0 else i + 1
    except (OSError, ValueError) as e:      # ValueError: an empty file cannot be mapped
        raise CouldNotLook("%s could not be read (%s: %s)" % (path, type(e).__name__, e))
    return out


def lacking(stations):
    """The aftermath stations that have no START twin (same key and name, on another cell)."""
    return [s for s in stations if s["tag"] == "AFTER" and not any(
        t["tag"] == "START" and (t["key"], t["name"]) == (s["key"], s["name"]) and (t["x"], t["z"]) != (s["x"], s["z"])
        for t in stations)]


def why(stations):
    """-> None, or the refusal in one sentence with its repair."""
    bad = lacking(stations)
    if not bad:
        return None
    return "%d aftermath station(s) of the walk save have no start-state twin, so he cannot compare before and after: %s. %s" % (
        len(bad), ", ".join("%s %s" % (s["key"], s["name"]) for s in bad), REPAIR)


def save_why(path):
    """The Stage 6 exit's reading of a walk save: None, the refusal, or that it could not be read."""
    try:
        return why(of_save(path))
    except CouldNotLook as e:
        return "%s, so its start-state twins are not checked" % e


def find(name):
    import game_instance
    import game_paths
    p = re.sub(r"^([A-Za-z]):[\\/]", lambda m: "/mnt/%s/" % m.group(1).lower(), name).replace("\\", "/")
    if os.path.sep in p:
        return p if p.startswith("/") else os.path.abspath(p)
    folders = [game_paths.SAVES]
    try:
        root = game_instance.root()
        root = re.sub(r"^([A-Za-z]):[\\/]", lambda m: "/mnt/%s/" % m.group(1).lower(), root).replace("\\", "/")
        folders += [os.path.join(root, d, "Saves") for d in sorted(os.listdir(root))]
    except Exception as e:      # noqa: BLE001  (no instance root: ArchBig's folder is still read)
        print("note: the other games' folders could not be read (%s)" % e, file=sys.stderr)
    hits = [q for q in (os.path.join(d, name if name.endswith(".rws") else name + ".rws") for d in folders) if os.path.isfile(q)]
    if not hits:
        raise CouldNotLook("no save %s in %s" % (name, "; ".join(folders)))
    return hits[0]


def of_mod(mod):
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import maturation as M
    for k in reversed(M.visit_numbers(REPO, mod)):
        blk = M.ingame_exit_block(M.read_text(REPO, mod, "%s/visit_%d/SUMMARY.md" % (M.INGAME_DIR, k)))
        if blk and blk.get("savegame"):
            return M.native_to_here(blk["savegame"])
    raise CouldNotLook("no in-game visit of %s names a savegame in its Exit block" % mod)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2 or a[0] != "check" or (a[1] == "--mod" and len(a) < 3):
        print(__doc__)
        return 2
    try:
        p = of_mod(a[2]) if a[1] == "--mod" else find(a[1])
        st = of_save(p)
        if not st:
            raise CouldNotLook("%s holds no station sign" % p)
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    w = why(st)
    print("%s  %s: %s" % ("FAIL" if w else "ok  ", os.path.basename(p), w or "%d station sign(s), %d aftermath, each with its START twin" % (
        len(st), sum(s["tag"] == "AFTER" for s in st))))
    return 1 if w else 0


if __name__ == "__main__":
    sys.exit(main())
