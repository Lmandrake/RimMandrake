#!/usr/bin/env python3
"""banned_factions.py - the guard that no faction the owner banned can raid, trade, visit or show in a list.

Registry (data): src/RimMandrake/Utils/factions/banned_factions.json. Design and the 1.6 source behind every check:
design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md.

  check-repo              offline, the repo only: each banned def carries the registry's 'banish' values (our own def
                          in its file, a donor/DLC def in the patch file), the orbital traders are unfactioned, and
                          no other XML or C# string literal under src/ names a banned defName.
  check-save <rws>...     a savegame: each banned faction is ABSENT, or BANISHED (effectively hidden, defeated, owns
                          no world object). LIVE fails. --dump <capture> resolves def.hidden; without it the stored
                          <hidden> must be True.
  inventory <capture> <rws>
                          a markdown table of every faction in the save (and every FactionDef of ours) with its
                          flags, counts, what its def lets it do, settlements, leader and relation to the player.
  check-dump <capture>    a def-dump capture (DefDump/captures/<id>): each banned def present in the running game has
                          the banish values, and the orbital traders name no faction. The post-deploy proof.

Exit 0 pass, 1 fail, 2 UNMEASURED (an instrument that saw nothing: no factions parsed, no defs in the dump).
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REGISTRY = os.path.join(ROOT, "src", "RimMandrake", "Utils", "factions", "banned_factions.json")
PASS, FAIL, UNMEASURED = 0, 1, 2


def load_registry(path=REGISTRY):
    reg = json.load(open(path, encoding="utf-8"))
    reg["_banish_fields"] = {k: v for k, v in reg["banish"].items() if not k.startswith("_")}
    return reg


def _norm(v):
    return str(v).strip().lower()


# ---------------------------------------------------------------- check-repo

def patch_ops(patch_path):
    """{defName: {field: value}} for FactionDefs set by the replace-or-add idiom, and the set of TraderKindDefs whose
    <faction> is removed. Read from the XML structure, not by regex over text."""
    root = ET.parse(patch_path).getroot()
    sets, removed = {}, set()
    rx_field = re.compile(r'^/Defs/FactionDef\[defName="([^"]+)"\]/(\w+)$')
    rx_trader = re.compile(r'^/Defs/TraderKindDef\[defName="([^"]+)"\]/faction$')
    for el in root.iter():
        cls = el.get("Class") or ""
        xp = (el.findtext("xpath") or "").strip()
        if cls == "PatchOperationReplace":
            m = rx_field.match(xp)
            val = el.find("value")
            if m and val is not None and len(val):
                sets.setdefault(m.group(1), {})[m.group(2)] = (val[0].text or "").strip()
        elif cls == "PatchOperationRemove":
            m = rx_trader.match(xp)
            if m:
                removed.add(m.group(1))
    # the nomatch Add must carry the same value as the Replace, or one branch silently disagrees
    adds = {}
    for el in root.iter():
        if (el.get("Class") or "") == "PatchOperationAdd":
            m = re.match(r'^/Defs/FactionDef\[defName="([^"]+)"\]$', (el.findtext("xpath") or "").strip())
            val = el.find("value")
            if m and val is not None:
                for child in val:
                    adds.setdefault(m.group(1), {})[child.tag] = (child.text or "").strip()
    return sets, adds, removed


def own_def_fields(def_file, def_name):
    for fd in ET.parse(def_file).getroot().iter("FactionDef"):
        if (fd.findtext("defName") or "").strip() == def_name:
            return {c.tag: (c.text or "").strip() for c in fd}
    return None


_STRING_LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')


def references(root_dir, names, allow):
    """(relpath, name, where) for every XML element text / attribute or C# string literal naming a banned def,
    outside the allowlist. Comments are not references."""
    hits = []
    allow = {os.path.normpath(a["path"] if isinstance(a, dict) else a) for a in allow}
    src = os.path.join(root_dir, "src")
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in ("obj", "bin", "__pycache__", ".git")]
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.normpath(os.path.relpath(p, root_dir))
            if rel in allow:
                continue
            if fn.endswith(".xml"):
                try:
                    tree = ET.parse(p)
                except ET.ParseError:
                    continue
                for el in tree.getroot().iter():
                    vals = [(el.text or "").strip()] + [v.strip() for v in el.attrib.values()]
                    for v in vals:
                        if v in names:
                            hits.append((rel, v, "<%s>" % el.tag))
            elif fn.endswith(".cs"):
                text = open(p, encoding="utf-8", errors="replace").read()
                text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
                text = re.sub(r"//[^\n]*", "", text)
                for m in _STRING_LIT.finditer(text):
                    if m.group(1) in names:
                        hits.append((rel, m.group(1), "string literal"))
    return hits


def check_repo(reg, root_dir=ROOT, out=print):
    want = reg["_banish_fields"]
    bad = []
    patch_path = os.path.join(root_dir, reg["patch_file"])
    if not os.path.isfile(patch_path):
        out("FAIL patch file missing: %s" % reg["patch_file"])
        return FAIL
    sets, adds, removed = patch_ops(patch_path)
    n = 0
    for f in reg["factions"]:
        dn = f["defName"]
        n += 1
        if f.get("own_def_file"):
            have = own_def_fields(os.path.join(root_dir, f["own_def_file"]), dn)
            if have is None:
                bad.append("%s: not found in its own def file %s" % (dn, f["own_def_file"]))
                continue
            where = f["own_def_file"]
        else:
            have = sets.get(dn, {})
            add = adds.get(dn, {})
            for k, v in want.items():
                if k in have and _norm(add.get(k)) != _norm(v):
                    bad.append("%s: Replace sets %s=%s but the nomatch Add sets %r" % (dn, k, v, add.get(k)))
            where = reg["patch_file"]
        for k, v in want.items():
            if _norm(have.get(k)) != _norm(v):
                bad.append("%s: %s should be %s, %s has %r" % (dn, k, v, where, have.get(k)))
    for t in reg.get("orbital_traders_unfactioned", []):
        if t not in removed:
            bad.append("TraderKindDef %s: <faction> is not removed in %s" % (t, reg["patch_file"]))
    names = {f["defName"] for f in reg["factions"]}
    for rel, name, where in references(root_dir, names, reg.get("reference_allowlist", [])):
        bad.append("%s names banned faction %s (%s); point it at a wanted faction, or allowlist it in the registry "
                   "with a reason" % (rel, name, where))
    out("banned factions in registry: %d (a zero is an instrument failure, not a pass)" % n)
    for b in bad:
        out("  FAIL " + b)
    if n == 0:
        return UNMEASURED
    return FAIL if bad else PASS


# ---------------------------------------------------------------- check-save

def dump_defs(capture, def_type):
    path = os.path.join(capture, "defs", def_type + ".json")
    if not os.path.isfile(path):
        return None
    return {d["defName"]: d for d in json.load(open(path, encoding="utf-8"))["defs"]}


def save_factions(rws):
    root = ET.parse(rws).getroot()
    fm = root.find("game/world/factionManager/allFactions")
    if fm is None:
        return None, {}
    owned = {}
    wo = root.find("game/world/worldObjects/worldObjects")
    for o in (wo.findall("li") if wo is not None else []):
        fac = o.findtext("faction")
        if fac:
            owned.setdefault(fac, []).append(o.findtext("def"))
    rows = []
    for f in fm.findall("li"):
        rows.append({
            "loadID": f.findtext("loadID") or "0",   # Scribe omits the default 0
            "def": (f.findtext("def") or "").strip(),
            "name": f.findtext("name"),
            "hidden": f.findtext("hidden"),         # nullable: absent means the def decides
            "defeated": _norm(f.findtext("defeated") or "False") == "true",
        })
    return rows, owned


def check_save(reg, rws, dump=None, out=print):
    rows, owned = save_factions(rws)
    if not rows:
        out("UNMEASURED %s: no factions parsed" % rws)
        return UNMEASURED
    fdefs = dump_defs(dump, "FactionDef") if dump else None
    worst = PASS
    out("%s: %d factions" % (os.path.basename(rws), len(rows)))
    for f in reg["factions"]:
        dn = f["defName"]
        inst = [r for r in rows if r["def"] == dn]
        if not inst:
            out("  ABSENT   %s" % dn)
            continue
        for r in inst:
            if r["hidden"] is not None:
                hid, how = _norm(r["hidden"]) == "true", "stored"
            elif fdefs is not None and dn in fdefs:
                hid, how = bool(fdefs[dn]["fields"].get("hidden")), "def, per dump"
            else:
                hid, how = False, "def unknown without --dump; stored hidden absent"
            objs = owned.get("Faction_" + r["loadID"], [])
            problems = []
            if not hid:
                problems.append("not hidden (%s)" % how)
            if not r["defeated"]:
                problems.append("not defeated")
            if objs:
                problems.append("owns world objects %s" % objs)
            if problems:
                out("  LIVE     %s loadID %s %r: %s" % (dn, r["loadID"], r["name"], "; ".join(problems)))
                worst = FAIL
            else:
                out("  BANISHED %s loadID %s %r (hidden: %s)" % (dn, r["loadID"], r["name"], how))
    return worst


# ---------------------------------------------------------------- check-dump

def check_dump(reg, capture, out=print):
    fdefs = dump_defs(capture, "FactionDef")
    tdefs = dump_defs(capture, "TraderKindDef")
    if not fdefs or not tdefs:
        out("UNMEASURED %s: FactionDef/TraderKindDef missing or empty" % capture)
        return UNMEASURED
    want = reg["_banish_fields"]
    bad = []
    for f in reg["factions"]:
        dn = f["defName"]
        d = fdefs.get(dn)
        if d is None:
            out("  ABSENT   %s (its supplier is not loaded)" % dn)
            continue
        for k, v in want.items():
            if _norm(d["fields"].get(k)) != _norm(v):
                bad.append("%s: %s is %r, want %s" % (dn, k, d["fields"].get(k), v))
    for t in reg.get("orbital_traders_unfactioned", []):
        d = tdefs.get(t)
        if d is not None and d["fields"].get("faction"):
            bad.append("TraderKindDef %s still names faction %s" % (t, d["fields"]["faction"]))
    out("%s: %d FactionDefs, %d TraderKindDefs" % (capture, len(fdefs), len(tdefs)))
    for b in bad:
        out("  FAIL " + b)
    return FAIL if bad else PASS


# ---------------------------------------------------------------- inventory

def inventory(capture, rws, out=print):
    """Markdown table: every faction in the save, then every FactionDef of ours (packageId mandrake.*) not in it."""
    fdefs = dump_defs(capture, "FactionDef") or {}
    root = ET.parse(rws).getroot()
    facs = root.find("game/world/factionManager/allFactions").findall("li")
    lid = lambda f: f.findtext("loadID") or "0"
    pid = ["Faction_" + lid(f) for f in facs if "Player" in (f.findtext("def") or "")]
    pid = pid[0] if pid else None
    owned = {}
    for o in root.find("game/world/worldObjects/worldObjects").findall("li"):
        owned[o.findtext("faction")] = owned.get(o.findtext("faction"), 0) + 1
    insave = {}
    for f in facs:
        rel = "-" if f.findtext("def") == "PlayerColony" else "Neutral"
        rels = f.find("relations")
        for rr in (rels.findall("li") if rels is not None else []):
            if rr.findtext("other") == pid:
                rel = rr.findtext("kind") or "Neutral"
        insave[f.findtext("def")] = (lid(f), f.findtext("name"), owned.get("Faction_" + lid(f), 0),
                                     "Y" if f.findtext("leader") not in (None, "null") else "no", rel)

    def row(dn):
        x = fdefs.get(dn)
        fl = x["fields"] if x else {}
        groups = [g.get("kindDef") for g in fl.get("pawnGroupMakers") or []]
        can = []
        if "Combat" in groups and not fl.get("raidsForbidden"):
            can.append("raid")
        if fl.get("caravanTraderKinds"):
            can.append("caravan")
        if "Peaceful" in groups or "Trader" in groups:
            can.append("visit")
        if fl.get("canGenerateQuestSites"):
            can.append("questsites")
        flags = " ".join(t for t, k in (("H", "hidden"), ("PE", "permanentEnemy"), ("NE", "naturalEnemy")) if fl.get(k))
        s = insave.get(dn)
        tail = ("%s '%s' | %s | %s | %s |" % s) if s else "absent | | | |"
        return "| `%s` | %s | %s | %s/%s/%s | %s | %s" % (
            dn, x["modName"] if x else "NOT IN DUMP", flags, fl.get("startingCountAtWorldCreation"),
            fl.get("maxConfigurableAtWorldCreation"), fl.get("requiredCountAtGameStart"), ",".join(can) or "-", tail)

    out("| FactionDef | mod | flags | start/maxCfg/required | can (by def) | save loadID+name | settlements | leader | to player |")
    out("|---|---|---|---|---|---|---|---|---|")
    seen = []
    for f in facs:
        seen.append(f.findtext("def"))
        out(row(f.findtext("def")))
    for dn in sorted(d for d, x in fdefs.items() if x.get("packageId", "").startswith("mandrake.") and d not in seen):
        out(row(dn))
    return PASS if facs and fdefs else UNMEASURED


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", default=REGISTRY)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-repo")
    s = sub.add_parser("check-save")
    s.add_argument("saves", nargs="+")
    s.add_argument("--dump", help="def-dump capture dir, to resolve def.hidden")
    d = sub.add_parser("check-dump")
    d.add_argument("capture")
    i = sub.add_parser("inventory", help="markdown table of a save's factions against a def dump")
    i.add_argument("capture")
    i.add_argument("save")
    a = ap.parse_args(argv)
    reg = load_registry(a.registry)
    if a.cmd == "check-repo":
        rc = check_repo(reg)
    elif a.cmd == "check-save":
        rc = max(check_save(reg, p, a.dump) for p in a.saves)
    elif a.cmd == "inventory":
        return inventory(a.capture, a.save)
    else:
        rc = check_dump(reg, a.capture)
    print({PASS: "PASS", FAIL: "FAIL", UNMEASURED: "UNMEASURED"}[rc])
    return rc


if __name__ == "__main__":
    sys.exit(main())
