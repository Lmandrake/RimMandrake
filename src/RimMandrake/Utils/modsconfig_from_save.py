#!/usr/bin/env python3
"""
modsconfig_from_save.py — rebuild a ModsConfig.xml from the mod list a SAVEGAME
records inside itself.

WHY. 2026-09-07: a peer window swapped ModsConfig.xml to a 6-mod vanilla list for a
quicktest without first backing up the live 599-mod list. The newest config backup on
disk was two days old and 596 mods, so restoring from it would silently have dropped
three of the owner's mods — and a mod list that is quietly three short is the kind of
thing nobody notices until a def is missing.

🔑 THE SAVE IS THE BETTER SOURCE. Every .rws records `<modIds>` (with `<modNames>` and
`<modSteamIds>` beside it) in its header — the exact list, IN LOAD ORDER, that the save
was made with. That is strictly better than a config backup: it cannot be stale
relative to the save, because it IS the save's own list, and a save can only be loaded
with the mods it was made with anyway.

So when a mod list is lost, do not hunt for the freshest backup. Take it from the
newest savegame you care about.

    python3 modsconfig_from_save.py <save.rws>                 # report only
    python3 modsconfig_from_save.py <save.rws> --out FILE.xml  # write a ModsConfig

⚠️ This writes a FILE. It deliberately does NOT install over the live
Config/ModsConfig.xml — RimWorld rewrites that from memory on exit, so installing it
while the game is running is discarded, and swapping a mod list under a running game
is its own hazard. Install it with the game closed.
"""
import argparse
import os
import re
import sys

HEAD_BYTES = 600_000          # the meta block lives at the very top of the file


def mod_list(path):
    head = open(path, encoding="utf-8", errors="replace").read(HEAD_BYTES)
    out = {}
    for tag in ("modIds", "modNames", "modSteamIds"):
        m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), head, re.S)
        out[tag] = re.findall(r"<li>([^<]*)</li>", m.group(1)) if m else []
    m = re.search(r"<gameVersion>([^<]*)</gameVersion>", head)
    out["gameVersion"] = m.group(1) if m else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("save")
    ap.add_argument("--out")
    ap.add_argument("--known-expansions", default="ludeon.rimworld.royalty,"
                    "ludeon.rimworld.ideology,ludeon.rimworld.biotech,"
                    "ludeon.rimworld.anomaly,ludeon.rimworld.odyssey")
    a = ap.parse_args()

    if not os.path.exists(a.save):
        sys.exit("no such save: %s" % a.save)
    d = mod_list(a.save)
    ids = d["modIds"]
    if not ids:
        sys.exit("no <modIds> block found in the first %d bytes — wrong file?" % HEAD_BYTES)

    print("%s" % os.path.basename(a.save))
    print("  gameVersion : %s" % d["gameVersion"])
    print("  mods        : %d (in load order)" % len(ids))
    print("  first 6     : %s" % ids[:6])
    names = d["modNames"]
    if names and len(names) == len(ids):
        print("  last 3      : %s" % ["%s (%s)" % (i, n) for i, n in zip(ids[-3:], names[-3:])])

    if not a.out:
        print("\nreport only. --out FILE.xml to write a ModsConfig.")
        return 0

    ke = "\n".join("    <li>%s</li>" % e for e in a.known_expansions.split(",") if e)
    body = "\n".join("    <li>%s</li>" % i for i in ids)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
           "<ModsConfigData>\n"
           "  <version>%s</version>\n"
           "  <activeMods>\n%s\n  </activeMods>\n"
           "  <knownExpansions>\n%s\n  </knownExpansions>\n"
           "</ModsConfigData>\n" % (d["gameVersion"] or "1.6", body, ke))
    open(a.out, "w", encoding="utf-8", newline="\n").write(xml)
    print("\nwrote %s  (%d mods)" % (a.out, len(ids)))
    print("⚠️ install it with RimWorld CLOSED — the game rewrites ModsConfig.xml from")
    print("   memory on exit, so a write made while it runs is discarded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
