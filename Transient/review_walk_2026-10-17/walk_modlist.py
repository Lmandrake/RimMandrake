#!/usr/bin/env python3
"""Build the review-walk active mod list: ROOTS + their hard-dependency closure, in the owner's FULL.LATEST load order.

  python3 walk_modlist.py            # plan: prints the list, writes nothing
  python3 walk_modlist.py --apply    # backs up the live ModsConfig.xml, then writes the walk list (GAME MUST BE DOWN)
  python3 walk_modlist.py --restore --apply   # put the backed-up pre-walk list back (or use modlist_swap.py --restore)

Order and the knownExpansions block come from infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml (identical, as a
set, to deployed/config/ModsConfig.full-post-dead-removal-20261016.xml); live-only bridge helpers come from the live file.
Hard dependencies are read from each mod's About.xml (modDependencies + modDependenciesByVersion[v1.6]) in the game Mods
folder, the Steam workshop folder, and src/ for ours. Reads only; --apply writes ONE file, atomically, after the backup.
"""
import os, re, sys, shutil, datetime
import xml.etree.ElementTree as ET
REPO = "/home/mandrake/rm/bench"
sys.path.insert(0, os.path.join(REPO, "src/RimMandrake/Utils"))
from game_paths import MODS_CONFIG, WORKSHOP, LOCAL_MODS  # noqa: E402
FULL = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")
BACKUP_DIR = os.path.join(REPO, "Transient/review_walk_2026-10-17")
ROOTS = ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
         "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey",
         "brrainz.rimbridgeserver", "ray1203.simplecamerasetting",          # the bridge + camera helpers the live list carries
         "mandrake.rm.gimmesomeslack", "mandrake.rm.flowworks", "mandrake.rm.biomes",
         "mandrake.rut.patches", "mandrake.rsw.swbestiary", "mandrake.rsw.patches"]
LIVE_ONLY_OK = {"ray1203.simplecamerasetting"}   # on the live list, absent from FULL


def own_id(root):
    for ch in root:
        if ch.tag == "packageId":
            return (ch.text or "").strip().lower()


def deps(root):
    out = []
    for tag in ("modDependencies", "modDependenciesByVersion"):
        for n in root.iter(tag):
            for pid in n.iter("packageId"):
                if (pid.text or "").strip():
                    out.append(pid.text.strip().lower())
    return out


def index():
    ix = {}
    roots = [LOCAL_MODS, WORKSHOP, os.path.join(REPO, "src/RimMandrake"), os.path.join(REPO, "src/RimStarWars"), os.path.join(REPO, "src/RimUtinni")]
    for base in roots:
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d, "About", "About.xml")
            if os.path.exists(p):
                try:
                    r = ET.parse(p).getroot()
                except ET.ParseError:
                    continue
                pid = own_id(r)
                if pid:
                    ix.setdefault(pid, []).append((base, d, deps(r)))
    return ix


def ids(path):
    return [e.text.strip() for e in ET.parse(path).getroot().find("activeMods")]


def main():
    apply_ = "--apply" in sys.argv
    full = ids(FULL)
    fl = [x.lower() for x in full]
    # biomes' About is composed at deploy time, not in src: its 10 hard deps are in deploy_plan_biomes.txt
    extra = {"mandrake.rm.biomes": ["brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.anomaly", "ludeon.rimworld.biotech", "ludeon.rimworld.ideology",
             "ludeon.rimworld.odyssey", "ludeon.rimworld.royalty", "mandrake.rm.flowworks", "mandrake.rm.luminouspigment", "sarg.alphabiomes"]}
    ix = index()
    want, todo, problems = set(), list(ROOTS), []
    while todo:
        p = todo.pop()
        if p in want:
            continue
        want.add(p)
        ds = list(extra.get(p, []))
        for _, _, d in ix.get(p, [])[:1]:
            ds += d
        if p not in ix and p not in extra and not p.startswith("ludeon."):
            problems.append("no About.xml found for %s" % p)
        for d in ds:
            if d not in fl and d not in LIVE_ONLY_OK and not d.startswith("ludeon."):
                problems.append("%s needs %s which is NOT on the owner's full list" % (p, d))
            todo.append(d)
    out = [x for x, l in zip(full, fl) if l in want]
    for p in sorted(want - set(fl)):
        out.append(p) if p in LIVE_ONLY_OK else None
    missing = [r for r in ROOTS if r not in [o.lower() for o in out]]
    print("walk list: %d mods (full list has %d)" % (len(out), len(full)))
    for o in out:
        print("  ", o)
    for pr in problems + ["ROOT missing from list: %s" % m for m in missing]:
        print("PROBLEM:", pr)
    if problems or missing:
        sys.exit(2)
    if not apply_:
        return
    live = MODS_CONFIG
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    bak = os.path.join(BACKUP_DIR, "ModsConfig.PRE_WALK_%s.xml" % stamp)
    shutil.copy2(live, bak)
    print("backup ->", bak)
    tree = ET.parse(FULL)
    am = tree.getroot().find("activeMods")
    for ch in list(am):
        am.remove(ch)
    for o in out:
        ET.SubElement(am, "li").text = o
    tmp = live + ".walk.tmp"
    tree.write(tmp, encoding="utf-8", xml_declaration=True)
    os.replace(tmp, live)
    print("WROTE live ModsConfig.xml with", len(out), "active; restore: cp", bak, "live  (or modlist_swap.py --restore --apply)")


if __name__ == "__main__":
    main()
