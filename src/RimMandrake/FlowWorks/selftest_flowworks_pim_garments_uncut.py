#!/usr/bin/env python3
"""selftest_flowworks_pim_garments_uncut.py - the pawn-in-liquid matrix dresses its colonists only in garments the ship
cut list keeps.

WHY (RIMMANDRAKE_FIND_WHY_PAWN_GEAR_WEAR_KEPT_NONE): on ArchBig, 2026-11-25 03:17 PST, all 28 wear rows of the matrix
(northstar/pawn_in_liquid_matrix.py) failed. Its colonists wore Apparel_PowerArmor, Apparel_PowerArmorHelmet,
Apparel_Robe and Apparel_PackJump. The ship cut list (infrastructure/state/cherrypicker/CherryPicker.SHIP.xml, applied
on ArchBig by Cherry Picker) cuts all four, so Wear() left the pawns bare. The cowboy hat and the parka, which the list
keeps, were worn. ArchSmall has no Cherry Picker settings, and there the same six garments were worn. This offline check
makes a cut garment red before a live run spends a game on it.

WHAT IT CHECKS: each apparel defName in the matrix's KINDS (read with ast, not by import: the matrix reads sys.argv when
it loads) is absent from the <keys> of the ship cut list as ThingDef/<defName>. It also checks that at least one
garment is listed, so an empty or renamed KINDS cannot pass.

Exit 0 PASS, 1 FAIL (a garment is cut, or no garment is listed), 2 COULD NOT LOOK (a file cannot be read or parsed).
  --matrix PATH   check this matrix file instead of the repo's (used to show the check goes red)
  --ship PATH     check against this cut list instead of the repo's
Seen RED (exit 1, the four garments named) on the parent's matrix, and GREEN on the fix, 2026-11-25.
"""
import argparse
import ast
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
MATRIX = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar", "pawn_in_liquid_matrix.py")
SHIP = os.path.join(ROOT, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")


def garments(path):
    """-> [defName] of every apparel list in the KINDS literal of the matrix file."""
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "KINDS" for t in node.targets):
            kinds = ast.literal_eval(node.value)
            return [ap for k in kinds for ap in k[4]]
    raise ValueError("no KINDS assignment in %s" % path)


def cut_keys(path):
    """-> set of the cut list's keys (Type/defName)."""
    keys = ET.parse(path).getroot().find(".//keys")
    if keys is None:
        raise ValueError("no <keys> in %s" % path)
    return {(li.text or "").strip() for li in keys.findall("li")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--matrix", default=MATRIX)
    ap.add_argument("--ship", default=SHIP)
    a = ap.parse_args(argv)
    try:
        worn = garments(a.matrix)
        cut = cut_keys(a.ship)
    except (OSError, SyntaxError, ValueError, ET.ParseError) as ex:
        print("COULD NOT LOOK: %s" % ex)
        return 2
    if not cut:
        print("COULD NOT LOOK: the cut list %s has no keys" % a.ship)
        return 2
    if not worn:
        print("FAIL: the matrix lists no garment, so this check could pass on a stage that wears nothing")
        return 1
    bad = [g for g in worn if "ThingDef/" + g in cut]
    for g in worn:
        print("%-4s %s" % ("CUT" if g in bad else "ok", g))
    if bad:
        print("FAIL: %d of %d matrix garments are cut by the ship list (%s): %s" % (len(bad), len(worn), a.ship, ", ".join(bad)))
        return 1
    print("PASS: %d matrix garments, none cut by the ship list" % len(worn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
