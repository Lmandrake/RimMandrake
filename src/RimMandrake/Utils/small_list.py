#!/usr/bin/env python3
"""small_list.py - each mod's small mod list, in one named place, and the check that it holds every mod the mod needs. No AI.

Owner, 2026-11-24: "Development of the mods is 100% small mod list. Version after version, we build them up only on the mods
they really need". The rule: design/RimMandrake/standing_rulings.md §Mod development runs on small lists. Page:
design/specs/2026-11-24-full-list-walk-not-per-mod/boundary.md.

The one place: design/concepts/<Mod>/version/small_list.json
  {"mod", "tier": a modset_builder tier (its contents are the list), "why",
   "also": {packageId: why}: a mod the C# reaches and no XML names}
A mod's test may run on a smaller tier of its own; his walk, its walk save and every sitting run on this tier.

The check. A patch that matches nothing logs nothing, so a list that lacks the patched mod passes every test and proves nothing.
A mod NEEDS: the modDependencies of its About.xml, each PatchOperationFindMod <mods> name, each MayRequire / MayRequireAnyOf
packageId (one of an AnyOf is enough), each `also`. A needed mod that Baroque Biomes folds in is held by mandrake.rm.biomes.
  FAIL  a needed mod is absent from the list; a DLC, the zoom mod or Character Editor is absent; the tier is refused
  ok    ... unless the needed mod is NOT on the whole list he plays (ModsConfig.FULL.LATEST.xml): no game of ours loads it,
        so the line reads OFF LIST with its name and is no fault
  FAIL  a FindMod name that no mod, installed or ours, has: the patch can never match
  COULD NOT LOOK (exit 2)  an About.xml, patch or list that cannot be read: never read as "not installed"

  small_list.py check [--mod M ...]   one line per fault; exit 0 clean, 1 a fault, 2 could not look
  small_list.py show M                the list, in order, with what needs each mod
"""
import argparse
import contextlib
import glob
import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE) if HERE not in sys.path else None

BIOMES = "mandrake.rm.biomes"
DLC = ("ludeon.rimworld.royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech", "ludeon.rimworld.anomaly",
       "ludeon.rimworld.odyssey")
ZOOMS = ("ray1203.simplecamerasetting", "brrainz.cameraplus")
# owner 2026-11-25, his FlowWorks walk: "Please add Character Editor to all smallmod lists, beside the Zoom requirement."
# (packageId read from its About.xml, workshop 1874644848)
CHARACTER_EDITOR = "void.charactereditor"
REPAIR = ("add it to the `want` of the tier in src/RimMandrake/Utils/modset_builder.py that small_list.json names "
          "(design/RimMandrake/standing_rulings.md §Mod development runs on small lists)")


class CouldNotLook(Exception):
    pass


def norm(p):
    p = str(p or "").strip().lower()
    return p[:-len("_steam")] if p.endswith("_steam") else p


def spec_path(root, mod):
    return os.path.join(root, "design", "concepts", mod, "version", "small_list.json")


def load_spec(root, mod):
    p = spec_path(root, mod)
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise CouldNotLook("%s: %s" % (p, e))
    if not isinstance(d, dict) or not str(d.get("tier") or "").strip():
        raise CouldNotLook("%s names no tier" % p)
    return d


def mod_dir(root, mod):
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        d = os.path.join(root, "src", tier, mod)
        if os.path.isdir(d):
            return d
    raise CouldNotLook("no source folder of %s under src/" % mod)


def needs(moddir):
    """-> {("id"|"name"|"any", key): sorted relative paths}. An "any" key holds its packageIds joined by commas, a "name" key
    the names of one FindMod joined by newlines; one of them is enough."""
    out = {}

    def put(kind, key, rel):
        out.setdefault((kind, key), set()).add(rel)
    files = [os.path.join(moddir, "About", "About.xml")]
    for sub in ("Defs", "Patches"):
        files += sorted(glob.glob(os.path.join(moddir, "**", sub, "**", "*.xml"), recursive=True))
    for f in dict.fromkeys(files):
        rel = os.path.relpath(f, moddir).replace(os.sep, "/")
        if re.search(r"(^|/)(bin|obj|review|diag)/", rel):
            continue
        try:
            r = ET.parse(f).getroot()
        except (OSError, ET.ParseError) as e:
            raise CouldNotLook("%s: %s" % (f, e))
        if rel == "About/About.xml":
            for d in list(r.findall("modDependencies/li")) + list(r.findall("modDependenciesByVersion/v1.6/li")):
                if norm(d.findtext("packageId")):
                    put("id", norm(d.findtext("packageId")), rel)
            continue
        for e in r.iter():
            for a, kind in (("MayRequire", "id"), ("MayRequireAnyOf", "any")):
                if e.get(a):
                    ids = [norm(x) for x in e.get(a).split(",") if norm(x)]
                    if kind == "id":
                        for x in ids:
                            put("id", x, rel)
                    elif ids:
                        put("any", ",".join(ids), rel)
            if e.get("Class") == "PatchOperationFindMod":
                names = [li.text.strip() for li in e.findall("mods/li") if (li.text or "").strip()]
                if names:                           # FindMod matches when ANY of its mods is active
                    put("name", "\n".join(names), rel)
    return {k: sorted(v) for k, v in out.items()}


def full_list(root=REPO):
    p = os.path.join(root, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
    try:
        a = ET.parse(p).getroot().find("activeMods")
    except (OSError, ET.ParseError) as e:
        raise CouldNotLook("%s: %s" % (p, e))
    ids = {norm(li.text) for li in a.findall("li")} if a is not None else set()
    if not ids:
        raise CouldNotLook("%s lists no mod" % p)
    return ids


def scan():
    """modset_builder.scan(), or CouldNotLook when an About.xml could not be parsed (it would read as not installed)."""
    import modset_builder as MB
    for _try in (1, 2, 3):          # a drvfs read can fail once for want of memory (measured 2026-11-24, five files)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            got = MB.scan(keep=True)
        if "could not parse" not in err.getvalue():
            return got
    raise CouldNotLook("modset_builder.scan: %s" % err.getvalue().strip().splitlines()[0].strip())


def with_our_names(installed, root=REPO):
    """installed plus our own source mods: a mod folded into Baroque Biomes has no folder in the game, but has its name."""
    import modset_builder as MB
    out = dict(installed)
    for f in sorted(glob.glob(os.path.join(root, "src", "*", "*", "About", "About.xml"))):
        rec = MB.read_about(f)
        if rec:
            out.setdefault(rec["packageId"], rec)
    return out


def resolve(tier, installed):
    import modset_builder as MB
    if MB.tier_def(tier, installed) is None:
        return [], ["modset_builder has no tier %s" % tier]
    ordered, missing, refusals = MB.resolve_tier(tier, installed)
    return [norm(x) for x in ordered], (["missing %s" % ", ".join(missing)] if missing else []) + list(map(str, refusals or []))


def folded():
    import biomes_compose
    return {norm(x) for x in biomes_compose.folded_ids(os.path.join(REPO, "src"))}


def judge(need, also, tier_list, installed, full, fold):
    """-> (faults, off): one line each. Pure: every reading is an argument."""
    have = {norm(x) for x in tier_list}
    ids_of_name = {}
    for pid, rec in installed.items():
        ids_of_name.setdefault(str(rec.get("name") or "").strip().lower(), set()).add(norm(pid))
    faults, off = [], []

    def held(p):
        return p in have or (p in fold and BIOMES in have)

    def one(label, pids, where):
        if not pids:
            faults.append("no mod, installed or ours, is named %s (%s): the patch can never match" % (label, where[0]))
        elif any(held(p) for p in pids):
            return
        elif any(p in full or (p in fold and BIOMES in full) for p in pids):
            faults.append("%s is needed (%s) and the list lacks it: %s" % (label, ", ".join(where[:3]), REPAIR))
        else:
            off.append("OFF LIST %s: not on the whole list he plays (%s)" % (label, where[0]))
    for (kind, key), where in sorted(need.items()):
        if kind == "name":
            names = key.split("\n")
            if any(n.lower() in ("core", "royalty", "ideology", "biotech", "anomaly", "odyssey") for n in names):
                continue                            # the game's own folders, held by the DLC check below
            one("'%s'" % "' or '".join(names), sorted(set().union(*(ids_of_name.get(n.lower(), set()) for n in names))), where)
        else:
            one(key, key.split(",") if kind == "any" else [key], where)
    for pid, why in sorted((also or {}).items()):
        one(norm(pid), [norm(pid)], ["also: %s" % why])
    for d in DLC:
        if d not in have:
            faults.append("%s (an expansion) is absent: every list holds all five" % d)
    if not any(z in have for z in ZOOMS):
        faults.append("no advanced-zoom mod (%s): a sitting keeps it" % " or ".join(ZOOMS))
    if CHARACTER_EDITOR not in have:
        faults.append("no Character Editor (%s): a sitting keeps it beside the zoom mod; %s" % (CHARACTER_EDITOR, REPAIR))
    return faults, off


def check(root, mod, installed, full, fold):
    sp = load_spec(root, mod)
    if sp is None:
        return ["no %s: the mod has no small list" % os.path.relpath(spec_path(root, mod), root)], []
    tl, bad = resolve(sp["tier"], installed)
    if bad:
        return ["tier %s is refused: %s" % (sp["tier"], "; ".join(bad))], []
    return judge(needs(mod_dir(root, mod)), sp.get("also"), tl, with_our_names(installed, root), full, fold)


def walk_save_why(root, mod, save_mods, installed=None):
    """-> None when the walk save's mods are the mod's small list, else the reason in one sentence. The exit reads it."""
    sp = load_spec(root, mod)
    if sp is None:
        return None                                 # `check` names a mod with no list; a save is not judged without one
    want, bad = resolve(sp["tier"], installed if installed is not None else scan())
    if bad:
        return "the mod's small list (tier %s) cannot be built: %s" % (sp["tier"], "; ".join(bad))
    w, s = set(want), {norm(x) for x in save_mods or []}
    if w == s:
        return None
    lack, more = sorted(w - s), sorted(s - w)
    return ("the walk savegame is not on %s's small list, tier %s (%d mods): it has %d; %s%s. Stage the save on that tier "
            "(design/RimMandrake/standing_rulings.md §Mod development runs on small lists)" % (
                mod, sp["tier"], len(w), len(s), "lacks %s" % ", ".join(lack[:4]) if lack else "lacks none",
                "; has also %s%s" % (", ".join(more[:4]), " and %d more" % (len(more) - 4) if len(more) > 4 else "")
                if more else ""))


def list_faults(root, mod):
    """-> the mod's small-list faults as read on this machine now (a mod with no small_list.json: none). Raises CouldNotLook."""
    if load_spec(root, mod) is None:
        return []
    return check(root, mod, scan(), full_list(root), folded())[0]


def mods_with_lists(root=REPO):
    return sorted(os.path.basename(os.path.dirname(os.path.dirname(p))) for p in glob.glob(spec_path(root, "*")))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--mod", action="append", default=[])
    s = sub.add_parser("show")
    s.add_argument("mod")
    a = ap.parse_args(argv)
    mods = [a.mod] if a.cmd == "show" else (a.mod or mods_with_lists())
    if not mods:
        print("COULD NOT LOOK: no mod has a small_list.json")
        return 2
    try:
        installed, full, fold = scan(), full_list(), folded()
        bad = 0
        for m in mods:
            faults, off = check(REPO, m, installed, full, fold)
            for x in faults:
                print("FAIL  %s: %s" % (m, x))
            for x in off:
                print("note  %s: %s" % (m, x))
            bad += len(faults)
            sp = load_spec(REPO, m)
            tl = resolve(sp["tier"], installed)[0] if sp else []
            print("%s  %s: %s" % ("FAIL" if faults else "ok  ", m, "tier %s, %d mods" % (sp["tier"], len(tl)) if sp else "no list"))
            if a.cmd == "show":
                print("\n".join("  " + x for x in tl))
        print("small lists: %d mod(s), %d fault(s)" % (len(mods), bad))
        return 1 if bad else 0
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
