#!/usr/bin/env python3
"""Turn one generated faction into a different faction, in the save.

The use case: a faction that CANNOT be added at worldgen — `Pirate` is
`permanentEnemy`, so the planet editor never offers it — while a faction you have
too many of sits right there. Swap one into the other after the fact.

⭐ This is far safer than deleting a faction (which does not work at all — see
`skills/rimworld-world-editing/references/savegame-editing.md`). Only the `<def>`
string changes. Every loadID, every settlement's `<faction>` pointer, every
relation entry and every world pawn keeps pointing at the same `Faction_N`, so the
reference graph is untouched.

    python3 src/RimMandrake/Utils/swap_faction_def.py --from Jawa_Junkers --to Pirate
    python3 src/RimMandrake/Utils/swap_faction_def.py --from Jawa_Junkers --to Pirate \
        --nth 2 --name "Blackstar Company" --hostile --apply

⚠️ The NEW def's traits apply from the next load: pawn kinds, xenotypes,
`permanentEnemy`. Stored goodwill does NOT re-derive itself, so pass --hostile when
swapping into a permanent enemy or you get a permanently-hostile faction sitting at
neutral.
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SAVE = os.path.join(REPO, "world", "WORLDMAP_gen.rws")
GAME = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/Saves/WORLDMAP_gen.rws")


def top_level_lis(seg):
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", default=SAVE)
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--to", dest="dst", required=True)
    ap.add_argument("--nth", type=int, default=1,
                    help="which instance of --from to convert (1-based, default the LAST)")
    ap.add_argument("--name", default=None)
    ap.add_argument("--hostile", action="store_true",
                    help="set goodwill -100 and kind Hostile toward the player faction")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    text = open(a.save, encoding="utf-8").read()
    i = text.find("<allFactions>") + len("<allFactions>")
    j = text.find("</allFactions>", i)
    seg = text[i:j]
    spans = top_level_lis(seg)

    hits, player_idx = [], None
    for k, (s0, s1) in enumerate(spans):
        dn = re.search(r"<def>([\w.]+)</def>", seg[s0:s1])
        dn = dn.group(1) if dn else "?"
        if dn == a.src:
            hits.append((k, s0, s1))
        if dn == "PlayerColony":
            player_idx = k
    if not hits:
        sys.exit("no faction with def %r in this save" % a.src)
    print("found %d instance(s) of %s at Faction_%s"
          % (len(hits), a.src, ", Faction_".join(str(h[0]) for h in hits)))
    if len(hits) < a.nth:
        sys.exit("--nth %d but only %d instance(s)" % (a.nth, len(hits)))
    k, s0, s1 = hits[a.nth - 1]
    blk = seg[s0:s1]
    old_name = re.search(r"<name>([^<]*)</name>", blk)
    old_name = old_name.group(1) if old_name else "(unnamed)"
    print("converting Faction_%d  %s %r -> %s %r"
          % (k, a.src, old_name, a.dst, a.name or old_name))

    new = re.sub(r"<def>%s</def>" % re.escape(a.src), "<def>%s</def>" % a.dst, blk, count=1)
    if a.name:
        new = re.sub(r"<name>[^<]*</name>", "<name>%s</name>" % a.name, new, count=1)
    if a.hostile and player_idx is not None:
        pf = "Faction_%d" % player_idx
        if re.search(r"<other>%s</other>" % pf, new):
            new = re.sub(r"(<li>\s*<other>%s</other>)(.*?)(</li>)" % pf,
                         lambda m: "%s<kind>Hostile</kind><goodwill>-100</goodwill>%s"
                                   % (m.group(1), m.group(3)), new, count=1, flags=re.S)
        else:
            new = new.replace("<relations>",
                              "<relations><li><other>%s</other><kind>Hostile</kind>"
                              "<goodwill>-100</goodwill></li>" % pf, 1)
        print("  set hostile toward the player (%s)" % pf)

    seg = seg[:s0] + new + seg[s1:]
    text = text[:i] + seg + text[j:]

    if not a.apply:
        print("\nplan only - pass --apply to write")
        return
    shutil.copy(a.save, a.save + ".bak")
    open(a.save, "w", encoding="utf-8").write(text)
    if os.path.isdir(os.path.dirname(GAME)):
        shutil.copy(a.save, GAME)
    print("\nwrote (backup at %s.bak) and deployed" % os.path.basename(a.save))
    print("⚠️ verify by LOADING it and reading Player.log - a def swap is cheap but the")
    print("   new def's pawn kinds and xenotypes only take effect on the next load.")


if __name__ == "__main__":
    main()
