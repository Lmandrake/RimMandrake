#!/usr/bin/env python3
"""Selftest (SWB_BIOMES_DEPLOY_GUARD_DUPLICATE_DEFS): the planner refuses an
--apply whose resulting game copy defines a def twice, keeps a moved def's old
name live beside its alias target, or drops a moved def whose new home is not
in the deploy -- and passes when both sides of the move ship together.

Fixture (real main(), throwaway git repo + fake game dir): ModOld (the
SWBestiary role) shipped RM_Durrok (same-name move) and RSW_Ikee (renamed move
-> RM_Ikee, aliased); both moved to ModNew (the biome role) in a COMMITTED
move. The game holds both mods at their pre-move state.

    python3 src/RimMandrake/Utils/selftest_deploy_def_guard.py
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
from selftest_deploy_prune import write, git                     # noqa: E402

TIER = D.SRC_TIERS[0]


def about(pid):
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            "<ModMetaData><packageId>%s</packageId></ModMetaData>\n" % pid)


def defs(*items):
    return "<Defs>%s</Defs>\n" % "".join(items)


def thing(name, tag="ThingDef"):
    return "<%s><defName>%s</defName></%s>" % (tag, name, tag)


ALIAS = ("<RimMandrake.EnvironmentalHazards.RM_DefAliasDef><defName>A</defName><aliases>"
         "<li><from>RSW_Ikee</from><to>RM_Ikee</to><defType>ThingDef</defType></li>"
         "</aliases></RimMandrake.EnvironmentalHazards.RM_DefAliasDef>")

PRE = {   # game copy == repo state BEFORE the move
    "ModOld": {"About/About.xml": about("mandrake.rsw.old"),
               "Defs/Keep.xml": defs(thing("RSW_Keep")),
               "Defs/Durrok.xml": defs(thing("RM_Durrok", "AlienRace.ThingDef_AlienRace")),
               "Defs/Ikee.xml": defs(thing("RSW_Ikee"))},
    "ModNew": {"About/About.xml": about("mandrake.rm.new"),
               "Defs/Scrub.xml": defs(thing("RM_Scrub"))},
    "ModX":   {"About/About.xml": about("mandrake.rm.x"),
               "Defs/X.xml": defs(thing("RM_X"))},
    "ModY":   {"About/About.xml": about("mandrake.rm.y"),
               "Defs/Y.xml": defs(thing("RM_X"), thing("RM_Yonly"))},   # PRE-EXISTING dup, X and Y
    "ModV":   {"About/About.xml": about("mandrake.rm.v"),
               "Defs/V.xml": defs(thing("RM_V"))},
    "ModW":   {"About/About.xml": about("mandrake.rm.w"),
               "Defs/W.xml": defs(thing("RM_W"))},
}
# alias whose `from` the REPO still defines (ModOld's RSW_Keep): inert, never blocks
KEEP_ALIAS = ALIAS.replace("RSW_Ikee", "RSW_Keep").replace("RM_Ikee", "RM_X") \
    .replace("<defName>A</defName>", "<defName>KeepAlias</defName>")


def run(argv):
    sys.argv = ["x"] + argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = D.main()
    except SystemExit as e:
        rc = "exit %s" % e.code
    return rc, buf.getvalue()


def build(tmp):
    repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
    for mod, files in PRE.items():
        for f, t in files.items():
            write(os.path.join(repo, TIER, mod, f), t)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "."); git(repo, "commit", "-qm", "pre")
    for mod, files in PRE.items():
        for f, t in files.items():
            write(os.path.join(game, mod, f), t)
    # the move, committed
    old, new = os.path.join(repo, TIER, "ModOld"), os.path.join(repo, TIER, "ModNew")
    os.remove(os.path.join(old, "Defs", "Durrok.xml"))
    os.remove(os.path.join(old, "Defs", "Ikee.xml"))
    write(os.path.join(new, "Defs", "Durrok.xml"),
          defs(thing("RM_Durrok", "AlienRace.ThingDef_AlienRace")))
    write(os.path.join(new, "Defs", "Ikee.xml"), defs(thing("RM_Ikee")))
    write(os.path.join(new, "Defs", "Misc", "Aliases.xml"), defs(ALIAS))
    write(os.path.join(repo, TIER, "ModX", "Defs", "KeepAlias.xml"), defs(KEEP_ALIAS))
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "move")
    write(os.path.join(game, "ModX", "Defs", "KeepAlias.xml"), defs(KEEP_ALIAS))
    # orphan game folder (merged away, no repo source) duplicating ModY's RM_Yonly
    write(os.path.join(game, "ModGone", "About", "About.xml"), about("mandrake.rm.gone"))
    write(os.path.join(game, "ModGone", "Defs", "G.xml"), defs(thing("RM_Yonly")))
    # stale game-only file in ModW duplicating ModV's RM_V (a ManyWaters-style leftover)
    write(os.path.join(game, "ModW", "Defs", "Gone.xml"), defs(thing("RM_V")))
    cfg = os.path.join(tmp, "ModsConfig.xml")
    write(cfg, "<ModsConfigData><activeMods><li>mandrake.rsw.old</li></activeMods></ModsConfigData>\n")
    hold = os.path.join(tmp, "HOLD.txt"); write(hold, "")
    D.SRC_ROOT, D.HOLD_FILE = repo, hold
    D._MODS, D._CONFIG = [game], [cfg]
    D.FULL_LIST = os.path.join(tmp, "no-full-list.xml")      # absent: nothing scoped out
    full = os.path.join(tmp, "FULL.xml")
    write(full, "<ModsConfigData><activeMods>%s</activeMods></ModsConfigData>\n" % "".join(
        "<li>%s</li>" % about_pid for about_pid in (
            "mandrake.rsw.old", "mandrake.rm.new", "mandrake.rm.x", "mandrake.rm.y")))
    return game


def main():
    tmp = tempfile.mkdtemp(prefix="defguard-")
    try:
        game = build(tmp)
        g = lambda m, f: os.path.exists(os.path.join(game, m, "Defs", f))   # noqa: E731

        rc_plan, out_plan = run(["--mod", "ModNew"])
        rc_fwd, out_fwd = run(["--mod", "ModNew", "--apply"])
        fwd_untouched = not g("ModNew", "Durrok.xml") and g("ModOld", "Durrok.xml")
        rc_rev, out_rev = run(["--mod", "ModOld", "--apply"])
        rev_untouched = g("ModOld", "Durrok.xml") and g("ModOld", "Ikee.xml")
        rc_x, out_x = run(["--mod", "ModX"])
        rc_y, out_y = run(["--mod", "ModY"])
        rc_both, out_both = run(["--mod", "ModOld", "--mod", "ModNew", "--apply"])
        both_done = (g("ModNew", "Durrok.xml") and g("ModNew", "Ikee.xml")
                     and not g("ModOld", "Durrok.xml") and not g("ModOld", "Ikee.xml"))
        rc_after, out_after = run(["--mod", "ModNew"])
        D.FULL_LIST = os.path.join(tmp, "FULL.xml")         # ModGone not on the full list
        rc_y2, out_y2 = run(["--mod", "ModY"])
        rc_w, _ = run(["--mod", "ModNew", "--with", "ModOld"])

        fix = "--mod ModNew --mod ModOld --apply"
        cases = [
            ("plan: guard reports BLOCKING and says --apply would be refused",
             "BLOCKING" in out_plan and "would be REFUSED" in out_plan),
            ("forward (new without old): --apply refused, rc 1", rc_fwd == 1
             and "REFUSING --apply" in out_fwd),
            ("... DUP RM_Durrok across AlienRace/ThingDef tags (one ThingDef database)",
             "DUP ThingDef RM_Durrok" in out_fwd),
            ("... ALIAS-STALE RSW_Ikee -> RM_Ikee", "ALIAS-STALE ThingDef RSW_Ikee -> RM_Ikee" in out_fwd),
            ("... fix line names both mods", fix in out_fwd),
            ("... nothing written", fwd_untouched),
            ("reverse (old without new): --apply refused, rc 1", rc_rev == 1
             and "REFUSING --apply" in out_rev),
            ("... VANISHED RM_Durrok (same-name move)", "VANISHED ThingDef RM_Durrok" in out_rev),
            ("... VANISHED RSW_Ikee (renamed move, via the repo alias)",
             "VANISHED ThingDef RSW_Ikee" in out_rev),
            ("... fix line names both mods", fix in out_rev),
            ("... nothing written (moved files not pruned)", rev_untouched),
            ("pre-existing X/Y dup blocks the X deploy (X is a target)",
             "DUP ThingDef RM_X" in out_x and "BLOCKING" in out_x),
            ("pre-existing X/Y dup does NOT block an unrelated deploy",
             "PRE-EXISTING" in out_both and "! DUP ThingDef RM_X" not in out_both),
            ("repo-kept alias: ALIAS-REPO reported, not blocking",
             "ALIAS-REPO ThingDef RSW_Keep -> RM_X" in out_x and "! ALIAS-STALE ThingDef RSW_Keep" not in out_x),
            ("orphan game folder dup: blocks ModY, fix line says remove by hand, no --with",
             "DUP ThingDef RM_Yonly" in out_y and "orphan game folder(s) ModGone" in out_y
             and "--mod ModGone" not in out_y),
            ("orphan NOT on the owner's full list: out of scope, named, no RM_Yonly dup",
             "out of scope: 1 orphan game folder(s)" in out_y2 and "ModGone" in out_y2
             and "RM_Yonly" not in out_y2),
            ("... a repo mod off the full list (ModV/ModW) stays in scope",
             "DUP ThingDef RM_V" in out_y2),
            ("pre-existing stale copy: fix line names only that mod, not this plan's",
             "--mod ModW --apply --prune" in out_both and "--mod ModNew --mod ModOld --mod ModW"
             not in out_both),
            ("together: --apply passes and the move lands (old pruned, committed delete)",
             rc_both == 0 and both_done),
            ("after: guard clean for the moved mods", "! " not in out_after.split("def guard")[1]
             .split("\n\n")[0] if "def guard" in out_after else False),
            ("--with without --compose is an argparse error", str(rc_w).startswith("exit")),
        ]
        bad = 0
        for label, ok in cases:
            bad += not ok
            print("%s  %s" % ("ok  " if ok else "FAIL", label))
        if bad:
            for nm, o in (("plan", out_plan), ("x", out_x), ("y", out_y), ("fwd", out_fwd), ("rev", out_rev),
                          ("both", out_both), ("after", out_after)):
                print("----- %s\n%s" % (nm, o[:3000]))
        print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
