#!/usr/bin/env python3
# selftest-tier: deployed
"""T_ONBOARDING_TABLE_OFFLINE (tree check C_onboarding_table_offline; models.md, Onboarding table against the donor): each
onboarding row read against the factory mod's real XML: the Kludged process list is not empty and is a strict part of the donor's
list (or the one process, for a machine with one); the Refurbished list equals the donor's list.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_onboarding_table.py [--staged] [--vfef <the factory mod's folder>]

HOW IT READS. One document holds the factory mod's installed defs (its Defs, its Mods/Odyssey folder and its
Mods/VanillaCookingExpanded folder) and this mod's Defs. Every patch file of this repo that names a donor or a level def and the
word `processes` is applied to it in file order (FindMod taken as loaded, Sequence, Conditional by its test, Add, Replace, Remove;
another operation class is COULD NOT LOOK, never skipped). Then each line of the onboarding table (Defs/MachineLines) is read:

  kludged_is_a_part     the Kludged def's processes are not empty and are a strict part of the donor's, or equal them when the donor
                        has one process; they hold every process the row names that the donor has
  refurbished_is_whole  the Refurbished def's processes are the donor's, in the donor's order
  row_names_real        every process the row names is one the donor lists (a name that only another mod adds, and that is not
                        installed, cannot be checked here and is printed as not read)
  conditions_kept       a process that the donor lists only when another mod is loaded (MayRequire on its entry) carries the same
                        condition on the Kludged and the Refurbished def; a bare entry names a process that is not loaded on a
                        list without that mod, and the game reports a config error (seen live on the alloy forge, 2026-11-27)

  list_exists           a Kludged or a Refurbished def with a processor comp has a <processes> element, empty or not. With no
                        element the game makes no list: the factory framework's own config check throws on it at startup
                        and this mod's startup code finds no list to fill (seen live on the Kludged fish farm, 2026-11-27).
                        This row reads every line whose donor has a processor, also one whose list is made in code

With --staged the lines waiting in Source/onboarding_staged/<key>/ are read too and printed apart; they decide nothing until
they land. Left out, and read live instead (scene sc_levels_do_their_work): what the C# sets at startup: the processes that the
factory mod makes in code (autoloom, machining bay, fish farm), a Kludged part given by a count, and the autofarmer, which has no
process list. A line with no process list on its donor reads as "no process list" and is not a pass of these rows.

Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK. Planted faults on the smelter's line show each row able to fail.
"""
import argparse
import glob
import os
import sys

from lxml import etree as LX

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
LINE_TAG = "RimMandrake.WreckedMachines.RM_MachineLineDef"
PROC = 'comps/li[@Class="PipeSystem.CompProperties_AdvancedResourceProcessor"]'
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
VFEF_DEFAULT = os.environ.get("RM_VFEF_DIR") or STEAM + "/workshop/content/294100/3686924415"
ROWS = ("kludged_is_a_part", "refurbished_is_whole", "row_names_real", "conditions_kept", "list_exists")


class CouldNotLook(Exception):
    pass


def _root(path):
    try:
        return LX.parse(path, LX.XMLParser(remove_comments=True)).getroot()
    except (OSError, LX.XMLSyntaxError) as e:
        raise CouldNotLook("%s: %s" % (path, e))


def _xp(x):
    x = x.strip()
    return x if x.startswith("/") else "/" + x


def apply(op, doc, where):
    cls = op.get("Class") or ""
    if cls == "PatchOperationFindMod":
        return apply(op.find("match"), doc, where) if op.find("match") is not None else None
    if cls == "PatchOperationSequence":
        for li in op.findall("operations/li"):
            apply(li, doc, where)
        return None
    xpath = op.findtext("xpath")
    if xpath is None:
        raise CouldNotLook("%s: operation %s has no xpath" % (where, cls))
    nodes = doc.xpath(_xp(xpath))
    if cls == "PatchOperationConditional":
        branch = op.find("match") if nodes else op.find("nomatch")
        return apply(branch, doc, where) if branch is not None else None
    if cls == "PatchOperationAdd":
        prepend = (op.findtext("order") or "Append") == "Prepend"
        for n in nodes:
            for i, k in enumerate(op.find("value")):
                c = LX.fromstring(LX.tostring(k))
                n.insert(i, c) if prepend else n.append(c)
        return None
    if cls == "PatchOperationReplace":
        for n in nodes:
            par, idx = n.getparent(), n.getparent().index(n)
            par.remove(n)
            for i, k in enumerate(op.find("value")):
                par.insert(idx + i, LX.fromstring(LX.tostring(k)))
        return None
    if cls == "PatchOperationRemove":
        for n in nodes:
            n.getparent().remove(n)
        return None
    raise CouldNotLook("%s: operation class %s is not read by this check" % (where, cls))


def build(vfef, staged):
    """-> (document, {key: row}, [staged keys], patch files applied)."""
    base = os.path.join(vfef, "1.6")
    if not os.path.isdir(os.path.join(base, "Defs")):
        raise CouldNotLook("the factory mod is not at %s (no 1.6/Defs); pass --vfef or set RM_VFEF_DIR" % vfef)
    doc = LX.Element("Defs")
    files = []
    for sub in ("Defs", os.path.join("Mods", "Odyssey"), os.path.join("Mods", "VanillaCookingExpanded")):
        files += sorted(glob.glob(os.path.join(base, sub, "**", "*.xml"), recursive=True))
    files += sorted(glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True))
    staged_keys = []
    if staged:
        for d in sorted(glob.glob(os.path.join(HERE, "Source", "onboarding_staged", "*"))):
            got = [f for f in (os.path.join(d, n) for n in ("row.xml", "levels.xml")) if os.path.isfile(f)]
            if len(got) == 2:
                files += got
                staged_keys.append(os.path.basename(d))
    for f in files:
        r = _root(f)
        if r.tag == "Defs":
            doc.extend(list(r))
    tree = LX.ElementTree(doc)
    rows = {}
    for row in doc.iter(LINE_TAG):
        rows[(row.findtext("key") or "").strip()] = row
    names = set()
    for row in rows.values():
        names |= {(row.findtext(f) or "").strip() for f in ("original", "kludged", "refurbished")}
    names.discard("")
    patches = []
    for dp, dn, fs in os.walk(SRC):
        dn[:] = [d for d in dn if d not in ("obj", "bin", "Textures", "art_source", "onboarding_staged", "__pycache__")]
        if os.sep + "Patches" not in dp + os.sep:
            continue
        for f in sorted(fs):
            if not f.endswith(".xml"):
                continue
            p = os.path.join(dp, f)
            txt = open(p, encoding="utf-8", errors="replace").read()
            if "processes" in txt and any(n in txt for n in names):
                patches.append(p)
    for p in sorted(patches):
        r = _root(p)
        if r.tag != "Patch":
            continue
        for op in r.findall("Operation"):
            apply(op, tree, os.path.relpath(p, SRC))
    return tree, rows, staged_keys, patches


def _procs(tree, defname):
    """The process list of a def's processor: (list or None when the def has no processor comp, def found)."""
    d = tree.xpath('/Defs/ThingDef[defName="%s"]' % defname)
    if not d:
        return None, False
    comp = d[0].xpath(PROC)
    if not comp:
        return None, True
    return [li.text.strip() for li in comp[0].xpath("processes/li") if li.text], True


def _has_list(tree, defname):
    """True when the def's processor comp has a <processes> element; None when the def or its processor comp is absent."""
    d = tree.xpath('/Defs/ThingDef[defName="%s"]' % defname)
    comp = d[0].xpath(PROC) if d else []
    return bool(comp[0].xpath("processes")) if comp else None


def _conds(tree, defname):
    """{process: the MayRequire on its entry, or None} of a def's processor."""
    d = tree.xpath('/Defs/ThingDef[defName="%s"]' % defname)
    comp = d[0].xpath(PROC) if d else []
    return {li.text.strip(): (li.get("MayRequire") or None) for li in comp[0].xpath("processes/li") if li.text} if comp else {}


def read_line(tree, key, row):
    """-> ({row name: [faults]}, note) for one line; note says why a line was not read."""
    bad = {r: [] for r in ROWS}
    donor, kl, rf = [(row.findtext(f) or "").strip() for f in ("original", "kludged", "refurbished")]
    D, found = _procs(tree, donor)
    named = [li.text.strip() for li in row.findall("kludgedProcesses/li") if li.text]
    if not found and not donor.startswith("VFEFactory_"):
        if named:
            bad["row_names_real"].append("%s: the row names processes %s and its donor %s is not a factory machine" % (key, named, donor))
        return bad, "the donor %s is the base game's and has no process list: not read by these rows" % donor
    if not found:
        return bad, "the donor %s is not installed here: not read" % donor
    if D is None:
        if named:
            bad["row_names_real"].append("%s: the row names processes %s and the donor has no process list" % (key, named))
        return bad, "no process list on the donor: not read by these rows"
    for nm, dn in (("Kludged", kl), ("Refurbished", rf)):
        if _has_list(tree, dn) is False:
            bad["list_exists"].append("%s: the %s def %s has a processor comp and no <processes> element" % (key, nm, dn))
    if not D:
        return bad, "the donor's process list is made in code at startup: its processes are read live, not here"
    K, kf = _procs(tree, kl)
    R, rfound = _procs(tree, rf)
    if K is None or R is None:
        bad["kludged_is_a_part" if K is None else "refurbished_is_whole"].append(
            "%s: the %s def %s has no processor comp (def found %s)" % (key, "Kludged" if K is None else "Refurbished", kl if K is None else rf, kf if K is None else rfound))
        return bad, None
    if not K or not set(K) <= set(D) or (set(K) == set(D) and len(D) > 1):
        bad["kludged_is_a_part"].append("%s: Kludged %s against the donor's %d processes %s" % (key, K, len(D), D))
    if [p for p in named if p in D and p not in K]:
        bad["kludged_is_a_part"].append("%s: the row names %s and the Kludged def lacks it" % (key, [p for p in named if p in D and p not in K]))
    if R != D:
        bad["refurbished_is_whole"].append("%s: Refurbished %s is not the donor's list %s" % (key, R, D))
    dc = _conds(tree, donor)
    for nm, dn in (("Kludged", kl), ("Refurbished", rf)):
        for p, c in sorted(_conds(tree, dn).items()):
            if p in dc and dc[p] != c:
                bad["conditions_kept"].append("%s: the %s def names %s with MayRequire %r, the donor has %r" % (key, nm, p, c, dc[p]))
    known = {d.text.strip() for d in tree.xpath("/Defs/PipeSystem.ProcessDef/defName")}
    for p in named:
        if p not in D and p in known:
            bad["row_names_real"].append("%s: the row names %s, a process the donor does not list" % (key, p))
    unread = [p for p in named if p not in known]
    return bad, ("names not read (their mod is not installed): %s" % unread) if unread else None


def verdict(tree, rows, keys):
    total = {r: [] for r in ROWS}
    read, notes = 0, []
    for key in keys:
        bad, note = read_line(tree, key, rows[key])
        for r in ROWS:
            total[r] += bad[r]
        if note and "not read" in note and "names not read" not in note:
            notes.append("%s: %s" % (key, note))
        else:
            read += 1
            if note:
                notes.append("%s: %s" % (key, note))
    return total, read, notes


def _plant(tree, how):
    t = LX.ElementTree(LX.fromstring(LX.tostring(tree)))
    k = t.xpath('/Defs/ThingDef[defName="RM_WM_AutomatedSmelter_Kludged"]/' + PROC + "/processes")[0]
    r = t.xpath('/Defs/ThingDef[defName="RM_WM_AutomatedSmelter_Refurbished"]/' + PROC + "/processes")[0]
    d = t.xpath('/Defs/ThingDef[defName="VFEFactory_AutomatedSmelter"]/' + PROC + "/processes")[0]
    if how == "kludged_empty":
        for li in list(k):
            k.remove(li)
    elif how == "kludged_is_everything":
        for li in list(k):
            k.remove(li)
        for li in d:
            k.append(LX.fromstring(LX.tostring(li)))
    elif how == "kludged_makes_what_the_donor_cannot":
        LX.SubElement(k, "li").text = "VFEFactory_MakeKibble"
    elif how == "refurbished_lacks_one":
        r.remove(r[-1])
    elif how == "refurbished_out_of_order":
        r.insert(0, r[-1])
    elif how == "kludged_drops_a_condition":
        [li for li in d if li.text == k[0].text][0].set("MayRequire", "Some.OtherMod")
    elif how == "kludged_has_no_list":
        k.getparent().remove(k)
    elif how == "row_names_a_foreign_process":
        row = [x for x in t.getroot().iter(LINE_TAG) if x.findtext("key") == "smelter"][0]
        LX.SubElement(row.find("kludgedProcesses"), "li").text = "VFEFactory_MakeKibble"
    return t


PLANTS = (("kludged_empty", "kludged_is_a_part"), ("kludged_is_everything", "kludged_is_a_part"),
          ("kludged_makes_what_the_donor_cannot", "kludged_is_a_part"), ("refurbished_lacks_one", "refurbished_is_whole"),
          ("refurbished_out_of_order", "refurbished_is_whole"), ("row_names_a_foreign_process", "row_names_real"),
          ("kludged_drops_a_condition", "conditions_kept"), ("kludged_has_no_list", "list_exists"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vfef", default=VFEF_DEFAULT)
    ap.add_argument("--staged", action="store_true")
    a = ap.parse_args()
    try:
        tree, rows, staged_keys, patches = build(a.vfef, a.staged)
        landed = sorted(k for k in rows if k not in staged_keys)
        total, read, notes = verdict(tree, rows, landed)
        blind = []
        if "smelter" not in rows:
            blind.append("the table has no smelter line to plant faults on")
        else:
            for how, want in PLANTS:
                t2 = _plant(tree, how)
                rows2 = {(r.findtext("key") or "").strip(): r for r in t2.getroot().iter(LINE_TAG)}
                if not verdict(t2, rows2, ["smelter"])[0][want]:
                    blind.append("%s did not turn %s red" % (how, want))
        st_total, st_read, st_notes = verdict(tree, rows, sorted(staged_keys)) if staged_keys else ({r: [] for r in ROWS}, 0, [])
    except CouldNotLook as e:
        print("T_ONBOARDING_TABLE_OFFLINE: COULD NOT LOOK: %s" % e)
        return 2
    for r in ROWS:
        print("%-21s %-4s worst %d faults, limit 0, %d lines read of %d on the table%s" % (
            r, "PASS" if not total[r] and read else "FAIL", len(total[r]), read, len(landed), "".join("\n    " + b[:300] for b in total[r][:6])))
    for n in notes:
        print("  note  " + n)
    if staged_keys:
        print("staged, deciding nothing: %d lines, %d read; faults %s" % (len(staged_keys), st_read, {r: len(st_total[r]) for r in ROWS}))
        for r in ROWS:
            for b in st_total[r][:20]:
                print("    staged %s: %s" % (r, b[:300]))
        for n in st_notes:
            print("  staged note  " + n)
    print("planted faults: %d of %d caught%s" % (len(PLANTS) - len(blind), len(PLANTS), "; " + "; ".join(blind) if blind else ""))
    print("read: %d patch files applied (%s)" % (len(patches), ", ".join(os.path.relpath(p, SRC) for p in patches)))
    fail = bool(any(total[r] for r in ROWS) or blind or not read)
    print("T_ONBOARDING_TABLE_OFFLINE: %s (%d lines read)" % ("FAIL" if fail else "PASS", read))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
