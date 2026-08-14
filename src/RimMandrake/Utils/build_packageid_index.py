#!/usr/bin/env python3
"""
build_packageid_index.py — map every installed mod's NAME to its own packageId.

WHY THIS EXISTS, AND WHY THE OBVIOUS VERSION IS WRONG
=====================================================
An earlier index built for the C7 art triage read "the first <packageId> in
About.xml" and was thrown away as unreliable. That heuristic returns the first
entry of <modDependencies> whenever dependencies are declared before the mod's
own id — it reported `brrainz.harmony` for Alpha Animals, Phytokin and Vanilla
Gravship Expanded, and `OskarPotocki.VanillaFactionsExpanded.Core` for Dark Ages
Beasts. Four wrong answers in the handful of mods anyone happened to check.

So this strips every <modDependencies>, <modDependenciesByVersion> and
<incompatibleWith> block BEFORE looking for <packageId>, which leaves only ids
that are direct children of <ModMetaData>.

WHAT IT IS FOR
==============
Writing honest <loadAfter> blocks. A PatchOperation that runs before the mod it
targets matches nothing and is skipped with one log line among thousands; a
texture override that loads before a loose-art donor is simply overwritten. Both
are silent. The constraint belongs in our own About.xml so it travels with the
mod, and that means resolving a mod NAME (which is what a generated patch groups
by, and what a human writes in a doc) to the packageId RimWorld actually keys on.

    python3 build_packageid_index.py                 # write the index
    python3 build_packageid_index.py "Alpha Animals" "Megafauna"   # look names up

Output: research/RimMandrake/installed_packageids.json — {name: {packageId, source, folder}}.
Committed as a manifest: it is small, it is provenance for every loadAfter we
write, and regenerating it needs the mods installed.
"""

import html
import json
import os
import re
import sys

WORKSHOP = ("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")
LOCAL = ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")
DATA = ("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "research", "RimMandrake", "installed_packageids.json")

# Blocks that legally contain OTHER mods' packageIds. Strip before matching.
FOREIGN = re.compile(
    r"<(modDependencies|modDependenciesByVersion|incompatibleWith|"
    r"loadAfter|loadBefore|loadAfterByVersion|forceLoadAfter|forceLoadBefore)"
    r"\b.*?</\1>",
    re.S | re.I,
)


def read_about(path):
    """Return (name, packageId) for one About.xml, or (None, None)."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            raw = fh.read()
    except OSError:
        return None, None
    own = FOREIGN.sub("", raw)
    pid = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", own, re.I)
    name = re.search(r"<name>\s*([^<]+?)\s*</name>", own, re.I)
    # Unescape entities: at least one installed mod is literally called
    # "Big and Small - Genes & More", which lives in About.xml as "&amp;". The
    # live def dump reports modName with the ampersand already decoded, so an
    # index that keeps the entity silently fails to match every generated patch.
    return (html.unescape(name.group(1)) if name else None), (pid.group(1) if pid else None)


def scan(root, source, index, collisions):
    if not os.path.isdir(root):
        return
    for entry in sorted(os.listdir(root)):
        about = os.path.join(root, entry, "About", "About.xml")
        if not os.path.isfile(about):
            continue
        name, pid = read_about(about)
        if not name or not pid:
            continue
        if name in index and index[name]["packageId"].lower() != pid.lower():
            collisions.append((name, index[name]["packageId"], pid))
            continue          # first writer wins; workshop is scanned first
        index.setdefault(name, {"packageId": pid, "source": source, "folder": entry})


def main():
    index, collisions = {}, []
    scan(WORKSHOP, "workshop", index, collisions)
    scan(LOCAL, "local", index, collisions)
    scan(DATA, "data", index, collisions)

    if len(sys.argv) > 1:                       # lookup mode, no write
        miss = 0
        for want in sys.argv[1:]:
            hit = index.get(want)
            if hit:
                print(f"{hit['packageId']}\t{want}")
            else:
                miss += 1
                print(f"?? NOT FOUND\t{want}", file=sys.stderr)
        return 1 if miss else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(f"{len(index)} mods indexed -> {OUT}")
    for name, a, b in collisions:
        print(f"  COLLISION  {name!r}: kept {a}, also saw {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
