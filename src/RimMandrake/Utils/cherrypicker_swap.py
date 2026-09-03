#!/usr/bin/env python3
"""Swap Cherry Picker's cut list between the SHIP profile and an empty REVIEW profile.

🔑 WHY THIS EXISTS (owner, 2026-09-02). Cherry Picker's config is ONE global file. It
serves both the game we ship and the game we test in, and those are different games:
the ship list must be fat so cut content cannot reach a player through any of its
several independent spawn paths (trade stock, raid loadouts, quest rewards, scenario
starts — commonality only ever suppressed WILD spawns), while a review pass needs to
see and spawn everything. One file cannot be both, and that conflict — not the number
of cuts — is what made varying the game for testing painful.

⭐ THE REVIEW PROFILE IS EMPTY, and that is a measured decision, not a shortcut. Of the
1509 keys live on 2026-09-02, not one was cut to fix a breakage: every batch anyone can
attribute is lore or roster curation. Cutting has only ever CAUSED failures here — the
Ikwa cut silently disarmed every kind inheriting TribalWarriorBase for four days — so a
review game with zero cuts is no less stable than the ship game, and is the only one
whose contents match the def dump.

⚠️ THE DUMP CANNOT SEE CUTS. The def dump is captured before Cherry Picker runs, so
every dump-derived census and review sheet describes the SHIP list's contents as though
they were present. That is how the owner came to review animals that no longer existed
in his game. Under REVIEW they genuinely are present, and the dump is honest again.

    cherrypicker_swap.py --status
    cherrypicker_swap.py --capture-ship --apply   # first run: adopt the live list as SHIP
    cherrypicker_swap.py --review --apply         # cut nothing; for review and testing
    cherrypicker_swap.py --ship   --apply         # put the campaign's cuts back

🔴 A SWAP IS INERT UNTIL THE NEXT GAME START. Cherry Picker applies its list once, at
load. Writing this file while the game runs changes nothing in the running game and is
not a way to un-cut something you are looking at.
"""
import argparse, datetime, hashlib, os, shutil, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import MODS_CONFIG  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Cherry Picker writes its settings beside ModsConfig.xml, named for its workshop id.
LIVE = os.path.join(os.path.dirname(MODS_CONFIG), "Mod_3521312241_Mod_CherryPicker.xml")
STORE = os.path.join(REPO, "infrastructure", "state", "cherrypicker")
SHIP = os.path.join(STORE, "CherryPicker.SHIP.xml")
REVIEW = os.path.join(STORE, "CherryPicker.REVIEW.xml")

EMPTY = ('<?xml version="1.0" encoding="utf-8"?>\n'
         '<SettingsBlock>\n'
         '\t<ModSettings Class="CherryPicker.ModSettings_CherryPicker">\n'
         '\t\t<keys />\n'
         '\t</ModSettings>\n'
         '</SettingsBlock>\n')


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def keys(p):
    """The cut keys, in order, or None if the file is missing/unreadable.

    ⚠️ Identity is the KEY LIST, never the bytes. RimWorld rewrites its own mod-settings
    files with its own formatting whenever the settings window is touched, so a
    byte-comparison cries wolf about tampering that never happened — the same lesson
    modlist_swap.py learned from RimSort reformatting ModsConfig.xml.
    """
    if not os.path.exists(p):
        return None
    try:
        node = ET.parse(p).getroot().find("./ModSettings/keys")
    except ET.ParseError:
        return None
    if node is None:
        return []
    return [li.text.strip() for li in node.findall("li") if li.text]


def by_type(ks):
    out = {}
    for k in ks:
        out[k.split("/", 1)[0] if "/" in k else "?"] = out.get(k.split("/", 1)[0] if "/" in k else "?", 0) + 1
    return out


def describe(p, label):
    ks = keys(p)
    if ks is None:
        return "%-7s MISSING  %s" % (label, p)
    top = ", ".join("%s %d" % (t, n) for t, n in sorted(by_type(ks).items(), key=lambda x: -x[1])[:4])
    return "%-7s %5d cuts  %s%s" % (label, len(ks), ("[" + top + "]  ") if ks else "", md5(p)[:8])


def which_is_live():
    live = keys(LIVE)
    if live is None:
        return "NO LIVE FILE"
    for path, name in ((SHIP, "SHIP"), (REVIEW, "REVIEW")):
        if os.path.exists(path) and keys(path) == live:
            return name if md5(path) == md5(LIVE) else "%s (same keys; file reformatted by the game)" % name
    return "UNRECOGNISED (%d cuts matching neither profile — someone edited the list in game)" % len(live)


def snapshot():
    """Archive the live file before overwriting — unless we already hold it byte for byte."""
    os.makedirs(STORE, exist_ok=True)
    live_hash = md5(LIVE)
    for name in sorted(os.listdir(STORE)):
        p = os.path.join(STORE, name)
        if name.lower().endswith(".xml") and os.path.isfile(p) and md5(p) == live_hash:
            print("  snapshot : skipped, identical to %s" % name)
            return name
    dst = "CherryPicker.PRESWAP.%s.xml" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(LIVE, os.path.join(STORE, dst))
    print("  snapshot : %s" % dst)
    return dst


def swap(src, label, apply_it):
    if not os.path.exists(src):
        sys.exit("REFUSING: %s does not exist.\n"
                 "  First run?  cherrypicker_swap.py --capture-ship --apply" % src)
    print("  live now : %d cuts (%s)" % (len(keys(LIVE) or []), which_is_live()))
    print("  would be : %d cuts  <- %s" % (len(keys(src)), os.path.basename(src)))
    if not apply_it:
        print("\nplan only. re-run with --apply")
        return
    if keys(src) == keys(LIVE):
        print("\nalready this profile. nothing written.")
        return
    arch = snapshot()
    shutil.copy2(src, LIVE)
    print("\n  archived live -> %s" % arch)
    print("  WROTE %s -> live (%d cuts)" % (label, len(keys(LIVE))))
    print("  🔴 INERT until the next game start — Cherry Picker applies its list at load.")


def capture_ship(apply_it):
    ks = keys(LIVE)
    if ks is None:
        sys.exit("REFUSING: cannot read the live Cherry Picker settings at\n  %s" % LIVE)
    if not ks:
        sys.exit("REFUSING: the live list is EMPTY, so capturing it as SHIP would\n"
                 "throw away the campaign's cuts. Load the ship profile first.")
    have = keys(SHIP) or []
    # ⚠️ AN EMPTY LIST WAS NEVER THE ONLY DANGEROUS SHAPE. A live list of 3 keys — a
    # partial write, or someone mid-edit in the mod's own settings window — passed the
    # guard above and replaced a 1509-key curated profile, which then existed only in
    # git. Refuse any capture that would lose most of what SHIP already holds; the
    # owner can still force it by deleting SHIP first, deliberately.
    if have and len(ks) < len(have) * 0.5:
        sys.exit("REFUSING: the live list has %d cuts and SHIP holds %d. Capturing "
                 "would discard\nmore than half of a curated profile.\n\n"
                 "  If the live list really is the new truth, delete\n    %s\n"
                 "  and run this again — that deletion is the deliberate act."
                 % (len(ks), len(have), SHIP))
    print("  live     : %d cuts" % len(ks))
    print("  SHIP now : %d cuts" % len(have) if have else "  SHIP now : (none yet)")
    print("  would be : %s" % SHIP)
    if not apply_it:
        print("\nplan only. re-run with --apply")
        return
    os.makedirs(STORE, exist_ok=True)
    # 🔴 ARCHIVE THE EXISTING SHIP FIRST. `swap()` snapshots before every write and this
    # did not, so the one command that overwrites the curated profile was the one with
    # no backup behind it (review finding, 2026-09-02).
    if have:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(STORE, "CherryPicker.SHIP.PRECAPTURE.%s.xml" % stamp)
        shutil.copy2(SHIP, dst)
        print("  archived : %s (%d cuts)" % (os.path.basename(dst), len(have)))
    shutil.copy2(LIVE, SHIP)
    if not os.path.exists(REVIEW):
        with open(REVIEW, "w", encoding="utf-8") as f:
            f.write(EMPTY)
        print("  wrote    : %s (empty — cuts nothing)" % os.path.basename(REVIEW))
    print("  wrote    : %s (%d cuts)" % (os.path.basename(SHIP), len(ks)))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--status", action="store_true")
    g.add_argument("--ship", action="store_true", help="the campaign's cut list")
    g.add_argument("--review", action="store_true", help="cut nothing — for review and testing")
    g.add_argument("--capture-ship", action="store_true",
                   help="adopt the current live list as the SHIP profile (first run)")
    ap.add_argument("--apply", action="store_true", help="actually write; default is plan only")
    a = ap.parse_args()

    if a.capture_ship:
        print("CAPTURE THE LIVE LIST AS THE SHIP PROFILE")
        capture_ship(a.apply)
    elif a.review:
        print("SWAP TO REVIEW (cuts nothing)")
        swap(REVIEW, "REVIEW", a.apply)
    elif a.ship:
        print("RESTORE THE SHIP CUT LIST")
        swap(SHIP, "SHIP", a.apply)
    else:
        print(describe(LIVE, "LIVE"))
        print(describe(SHIP, "SHIP"))
        print(describe(REVIEW, "REVIEW"))
        live = which_is_live()
        print("\nlive currently matches: %s" % live)
        if live.startswith("REVIEW"):
            print("🔴 NOTHING IS BEING CUT. This is the review/testing profile — content the\n"
                  "   campaign excludes is present and CAN spawn. --ship --apply before he plays.")
        elif live.startswith("UNRECOGNISED"):
            print("⚠️ The live list is neither profile. If that edit was deliberate, adopt it:\n"
                  "   cherrypicker_swap.py --capture-ship --apply")


if __name__ == "__main__":
    main()
