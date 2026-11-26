#!/usr/bin/env python3
"""Is every donor class in Armoury's XML guarded by a MayRequire for its donor?

    python3 src/RimMandrake/Utils/armoury_donor_class_guard.py [--mod-dir D] [--fix] [--quiet]

Item RIMMANDRAKE_LOAD_ARMOURY_ABSORBED_DEFS_WITHOUT_LIGHTSABER_TYPES. The rule and the table of donors live in
src/RimStarWars/Armoury/Source/donor_class_guard.py. This tool reads every .xml under Defs/ and Patches/ of the mod.

  exit 0  every donor-class node is guarded (prints files read, nodes that name a donor class, 0 unguarded)
  exit 1  one or more unguarded nodes: each line names the file, line, class and the guard it needs
  exit 2  UNMEASURED: no XML file found, or a file did not parse (a blind read must not print a clean zero)

--fix adds the missing MayRequire as a text edit on the start tag of the element that RimWorld reads it from (the
file's comments and layout stay). A top-level patch Operation that names a donor class is not fixed: it must move into
a PatchOperationSequence <li MayRequire>, and it stays in the report.
"""
import argparse
import glob
import os
import re
import sys

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_MOD = os.path.join(REPO, "src", "RimStarWars", "Armoury")
sys.path.insert(0, os.path.join(DEFAULT_MOD, "Source"))
import donor_class_guard as G  # noqa: E402


def files(mod):
    out = []
    for sub in ("Defs", "Patches"):
        out += [(p, sub == "Patches") for p in sorted(glob.glob(os.path.join(mod, sub, "**", "*.xml"), recursive=True))]
    return out


def parse(p):
    return etree.parse(p, etree.XMLParser(remove_comments=False)).getroot()


def strip_comments(root):
    for c in root.iter(etree.Comment):
        c.getparent().remove(c)
    return root


def scan(mod):
    """-> (files read, donor-class nodes seen, [(path, line, name, ns, holder_line, holder_tag, has_holder)], [parse errors]).
    holder_line is None when the holder sits inside another unguarded holder (that one is fixed instead) or when
    the node is a top-level patch Operation (has_holder False)."""
    nfiles, seen, bad, errs = 0, 0, [], []
    for p, in_patch in files(mod):
        try:
            root = strip_comments(parse(p))
        except etree.XMLSyntaxError as e:
            errs.append("%s: %s" % (p, e))
            continue
        nfiles += 1
        for el in root.iter():
            if isinstance(el.tag, str) and any(G.donor_of(n) for n in G.named_classes(el)):
                seen += 1
        rows = [(chain, name, ns, G.holder(chain, in_patch)) for chain, name, ns in G.unguarded(root, in_patch)]
        holders = {id(h) for _c, _n, _s, h in rows if h is not None}
        for chain, name, ns, h in rows:
            # --fix guards only the outermost holder: a guard on a def also covers every node inside it
            outer = h is not None and not any(id(a) in holders for a in h.iterancestors())
            bad.append((p, chain[-1].sourceline, name, ns, h.sourceline if outer else None,
                        h.tag if outer else None, h is not None))
    return nfiles, seen, bad, errs


def fix_file(p, rows):
    """Insert MayRequire="<donor>" into each holder's start tag. rows: [(holder_line, holder_tag, ns)]."""
    lines = open(p, encoding="utf-8-sig").read().split("\n")
    done = set()
    for hl, htag, ns in sorted(set(rows), key=lambda r: -r[0]):
        if (hl, htag) in done:
            continue
        done.add((hl, htag))
        i = hl - 1
        m = re.search(r"<%s(?=[\s>/])" % re.escape(htag), lines[i])
        if not m:
            raise SystemExit("could not find <%s on %s:%d" % (htag, p, hl))
        tagtext = lines[i][m.start():]
        cur = re.match(r"<%s\b[^>]*?\sMayRequire=\"([^\"]*)\"" % re.escape(htag), tagtext)
        want = G.DONORS[ns][0][0]
        if cur:
            s = m.start() + cur.start(1)
            lines[i] = lines[i][:s] + cur.group(1) + "," + want + lines[i][s + len(cur.group(1)):]
        else:
            lines[i] = lines[i][:m.end()] + ' MayRequire="%s"' % want + lines[i][m.end():]
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mod-dir", default=DEFAULT_MOD)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    nfiles, seen, bad, errs = scan(a.mod_dir)
    if errs or nfiles == 0:
        for e in errs:
            print("PARSE ERROR " + e)
        print("UNMEASURED: %d files read, %d did not parse" % (nfiles, len(errs)))
        return 2
    if a.fix and bad:
        by = {}
        for p, _l, _n, ns, hl, ht, _h in bad:
            if hl is not None:
                by.setdefault(p, []).append((hl, ht, ns))
        for p, rows in by.items():
            fix_file(p, rows)
        nfiles, seen, bad, errs = scan(a.mod_dir)
    for p, line, name, ns, hl, ht, has_holder in bad:
        if hl:
            need = "MayRequire=\"%s\" on <%s> line %d" % (G.DONORS[ns][0][0], ht, hl)
        elif has_holder:
            need = "MayRequire=\"%s\" on an enclosing element that is also unguarded" % G.DONORS[ns][0][0]
        else:
            need = ("this Operation moved into a PatchOperationSequence as <li MayRequire=\"%s\"> (a FindMod does not "
                    "guard a class: the patch is parsed before FindMod runs)" % G.DONORS[ns][0][0])
        print("UNGUARDED %s:%d %s (donor %s): needs %s" % (os.path.relpath(p, REPO), line, name, ns, need))
    print("%s: %d files read, %d nodes name a donor class, %d unguarded" % ("FAIL" if bad else "PASS", nfiles, seen, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
