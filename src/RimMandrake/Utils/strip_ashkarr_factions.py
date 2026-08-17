#!/usr/bin/env python3
"""Delete factions from a save. ⛔ MEASURED NOT TO WORK - 2026-08-16.

🔴 ITS OUTPUT DOES NOT LOAD CLEANLY. Kept because the graph surgery in it is correct
and reusable; the CONCLUSION is that faction deletion is not a viable save edit.

What happened: 36 factions removed, every reference chased down to 1 residual, and
the save still loaded with

    Could not do PostLoadInit on RimWorld.FactionManager: NullReferenceException
    Could not resolve reference to Faction_16 ... VanillaTradingExpanded.TradingManager
                                                  /banksByFaction/keys
    Error while generating pawn. Rethrowing. NullReferenceException

⇒ FactionManager itself fails to initialise. Mods keep their own faction-keyed
dictionaries in places no general sweep finds, and pawn/relation state reaches
further than the faction list. **Remove factions at the Configure Factions page
during worldgen instead.**

The bridge cannot remove a faction (the engine's own `All Factions To Remove`
returns zero, and no debug action does it), so this does it in the save.

⚠️ THIS TOUCHES THE FRAGILE PART OF THE SAVE - the ID reference graph. It works on
a COPY and is verified by loading the result and reading Player.log for Scribe
errors. If the log is not clean the copy is thrown away, not promoted.

Four edits, in order:
  1. drop each doomed faction's top-level <li> from <allFactions>
  2. drop every <li><other>Faction_N</other>…</li> relation naming a doomed faction,
     from every surviving faction
  3. repoint any world pawn owned by a doomed faction at a surviving one - pawns are
     reassigned, never deleted, because deleting them orphans every ID that names them
  4. leave faction loadIDs ALONE. Faction_7 stays Faction_7 even with gaps; renumbering
     would invalidate every reference in the file.

    python3 src/RimMandrake/Utils/strip_ashkarr_factions.py [--apply]
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SAVE = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
TEST = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_nofac.rws")

# ours, ratified
OURS = {
    "Empire", "OuterRim_GalacticEmpire", "Jawa_DeepwaterCompact", "Jawa_HuttCartel",
    "Jawa_WildsteamClan", "Jawa_IndigenousTribes", "Jawa_FreeDroidEnclaves",
    "Jawa_Junkers", "Jawa_AscendantHelix", "Jawa_GeonosianFoundryHive",
    "OuterRim_MoistureFarmers", "OuterRim_BinaryStarRaiders", "JDSCIS_CIS_Faction",
    "guy762_KotORFaction_RogueDroids",
}
# 🔴 System factions the ENGINE needs. Removing any of these breaks raids,
# infestations, ancient dangers, anomaly content or the colony itself.
SYSTEM = {
    "PlayerColony", "Mechanoid", "Insect", "Entities", "Ancients", "AncientsHostile",
    "HoraxCult", "TribalHostile", "DP_GenericHostile", "AM_EnemyPirate",
}


def top_level_lis(seg):
    """Split a container's immediate <li> children, ignoring nested ones."""
    out, depth, start = [], 0, None
    for m in re.finditer(r"<(/?)li\b[^>]*?(/?)>", seg):
        closing, selfclose = m.group(1), m.group(2)
        if selfclose:
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((start, m.end()))
    return out


def main():
    apply = "--apply" in sys.argv
    text = open(SAVE, encoding="utf-8").read()
    i = text.find("<allFactions>") + len("<allFactions>")
    j = text.find("</allFactions>", i)
    seg = text[i:j]
    spans = top_level_lis(seg)
    print("faction blocks: %d" % len(spans))

    doomed, kept = [], []
    for idx, (a, b) in enumerate(spans):
        blk = seg[a:b]
        dn = re.search(r"<def>([\w.]+)</def>", blk)
        nm = re.search(r"<name>([^<]*)</name>", blk)
        dn = dn.group(1) if dn else "?"
        nm = nm.group(1) if nm else "(unnamed)"
        (kept if dn in OURS or dn in SYSTEM else doomed).append((idx, dn, nm, a, b))

    print("keeping %d, removing %d" % (len(kept), len(doomed)))
    for idx, dn, nm, _, _ in doomed:
        print("   - Faction_%-3d %-32s %s" % (idx, dn, nm))

    doomed_ids = {"Faction_%d" % idx for idx, *_ in doomed}
    survivor = None
    for idx, dn, nm, _, _ in kept:
        if dn == "OuterRim_BinaryStarRaiders":
            survivor = "Faction_%d" % idx
    if survivor is None:
        survivor = "Faction_%d" % kept[0][0]
    print("orphan pawns will be repointed at %s" % survivor)

    # 1. drop the doomed blocks, high offset -> low so earlier offsets stay valid
    for idx, dn, nm, a, b in sorted(doomed, key=lambda x: -x[3]):
        seg = seg[:a] + seg[b:]
    text = text[:i] + seg + text[j:]

    # 2. drop relation entries naming them, anywhere in the file
    before = len(text)
    text = re.sub(
        r"<li>\s*<other>(%s)</other>.*?</li>\s*" % "|".join(sorted(doomed_ids)),
        "", text, flags=re.S)
    print("relation entries removed: %d bytes" % (before - len(text)))

    # 3. repoint anything still owned by a doomed faction
    n_rep = 0
    def repoint(mo):
        nonlocal n_rep
        n_rep += 1
        return "<faction>%s</faction>" % survivor
    text = re.sub(r"<faction>(?:%s)</faction>" % "|".join(sorted(doomed_ids)),
                  repoint, text)
    print("owner references repointed: %d" % n_rep)

    # 4. faction-keyed DICTIONARIES: <keys> and <values> are parallel lists, so a key
    # must be removed together with the value at the SAME INDEX. Dropping only the key
    # silently shifts every later value onto the wrong faction.
    D = "(?:%s)" % "|".join(sorted(doomed_ids))
    dicts = 0
    def fix_dict(mo):
        nonlocal dicts
        keys = re.findall(r"<li>([^<]*)</li>", mo.group(1))
        vals = top_level_lis(mo.group(2))
        if len(keys) != len(vals):
            return mo.group(0)
        keep = [k for k, key in enumerate(keys) if not re.fullmatch(D, key)]
        if len(keep) == len(keys):
            return mo.group(0)
        dicts += 1
        nk = "".join("<li>%s</li>" % keys[k] for k in keep)
        nv = "".join(mo.group(2)[a:b] for k in keep for a, b in [vals[k]])
        return "<keys>%s</keys><values>%s</values>" % (nk, nv)

    text = re.sub(r"<keys>(.*?)</keys>\s*<values>(.*?)</values>", fix_dict, text, flags=re.S)
    print("faction-keyed dictionaries pruned: %d" % dicts)

    # 5. the last singletons
    for tag in ("parentFaction", "bountyFaction"):
        text, k = re.subn(r"<%s>%s</%s>" % (tag, D, tag),
                          "<%s>%s</%s>" % (tag, survivor, tag), text)
        if k:
            print("  %s repointed: %d" % (tag, k))

    left = len(re.findall(r"<(\w+)>%s</\1>" % D, text))
    print("RESIDUAL references to doomed ids: %d" % left)

    if not apply:
        print("\nplan only - pass --apply to write the TEST copy")
        return
    open(TEST, "w", encoding="utf-8").write(text)
    print("\nwrote TEST copy: %s" % TEST)
    print("load it and read Player.log before promoting it over the real save")


if __name__ == "__main__":
    main()
