#!/usr/bin/env python3
"""Swap RimWorld's live mod list between the owner's full 583 and a minimal test set.

CHECK owns this. The point is that a cold load with 583 mods is ~25 minutes, and the
worldmap bridge work needs many reloads. A minimal list makes a reload cheap.

🔴 The owner's real list is infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml.
   --restore puts it back. Never leave the machine on the minimal list.

    modlist_swap.py --status
    modlist_swap.py --minimal          # plan only
    modlist_swap.py --minimal --apply
    modlist_swap.py --restore --apply
"""
import argparse, hashlib, os, shutil, sys, datetime
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LIVE = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/ModsConfig.xml"
if os.name == "nt" or not os.path.exists(os.path.dirname(LIVE)):
    LIVE = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml"
STORE = os.path.join(REPO, "infrastructure", "state", "modlists")
FULL = os.path.join(STORE, "ModsConfig.FULL.LATEST.xml")
MINIMAL = os.path.join(STORE, "ModsConfig.MINIMAL.xml")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def mods(p):
    if not os.path.exists(p):
        return None
    root = ET.parse(p).getroot()
    am = root.find("activeMods")
    return [li.text.strip() for li in am.findall("li")] if am is not None else []


def describe(p, label):
    m = mods(p)
    if m is None:
        return "%-9s MISSING  %s" % (label, p)
    return "%-9s %4d active  md5 %s" % (label, len(m), md5(p))


def which_is_live():
    """
    Which stored list the live file IS -- by the MOD LIST, not by the bytes.

    🔴 It used to compare md5 of the whole file, and that cried wolf. RimSort
    rewrites ModsConfig.xml with its own formatting every time it saves, so on
    2026-08-20 the live file and FULL.LATEST held the SAME 578 mods in the SAME
    order and still reported "someone edited it" -- measured: same set True,
    order differences 0, different md5. A status line that says the owner's list
    has been tampered with when nothing has changed is worse than no status line,
    because the next real tampering reads as more of the same.

    So: compare activeMods, in order. Byte-identical is reported too, because
    "identical" and "same mods, reformatted" are different facts and the second
    one is the one somebody will want to know about.
    """
    if not os.path.exists(LIVE):
        return "NO LIVE FILE"
    live_ids = mods(LIVE)
    if live_ids is None:
        return "LIVE FILE UNREADABLE"
    for path, name in ((FULL, "FULL"), (MINIMAL, "MINIMAL")):
        if not os.path.exists(path):
            continue
        if mods(path) == live_ids:
            if md5(path) == md5(LIVE):
                return name
            return "%s (same mods and order; file reformatted, e.g. by RimSort)" % name
    return "UNRECOGNISED (neither FULL nor MINIMAL - the MOD LIST differs, not just the bytes)"


def snapshot():
    """
    Archive whatever is live right now before overwriting it -- but only if we
    are not already keeping an identical copy.

    A backup identical to a file we already hold is not a backup. Before this
    check, every single swap stamped a new PRESWAP file unconditionally; five had
    accumulated by 2026-08-20 and md5 proved all five were byte-identical to the
    FULL.LATEST / MINIMAL sitting beside them. They were pure noise, one per swap,
    forever.

    ⚠️ The check is against EVERY .xml already in the store, not just FULL and
    MINIMAL, so a genuinely distinct earlier snapshot still counts as kept. That
    matters: `ModsConfig.FULL.20260819_201527.xml` looked like a duplicate for a
    day and is in fact the only surviving copy of the 578-mod list.
    """
    live_hash = md5(LIVE)
    for name in sorted(os.listdir(STORE)):
        if not name.lower().endswith(".xml"):
            continue
        existing = os.path.join(STORE, name)
        if os.path.isfile(existing) and md5(existing) == live_hash:
            print("  snapshot : skipped, identical to %s" % name)
            return existing
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(STORE, "ModsConfig.PRESWAP.%s.xml" % stamp)
    shutil.copy2(LIVE, dst)
    print("  snapshot : %s" % os.path.basename(dst))
    return dst


def swap(src, apply_it):
    if not os.path.exists(src):
        sys.exit("REFUSING: %s does not exist. Build it first." % src)
    n_src, n_live = len(mods(src)), len(mods(LIVE) or [])
    print("  live now : %d active (%s)" % (n_live, which_is_live()))
    print("  would be : %d active  <- %s" % (n_src, src))
    if not apply_it:
        print("\nplan only. re-run with --apply")
        return
    if md5(src) == md5(LIVE):
        print("\nalready identical. nothing written.")
        return
    arch = snapshot()
    shutil.copy2(src, LIVE)
    print("\n  archived live -> %s" % arch)
    print("  WROTE %s -> live  (%d active)" % (os.path.basename(src), n_src))
    print("  verify: md5 %s" % md5(LIVE))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--status", action="store_true")
    g.add_argument("--minimal", action="store_true", help="swap to the minimal test list")
    g.add_argument("--restore", action="store_true", help="put the owner's full list back")
    ap.add_argument("--apply", action="store_true", help="actually write; default is plan only")
    a = ap.parse_args()

    if a.minimal:
        print("SWAP TO MINIMAL")
        swap(MINIMAL, a.apply)
    elif a.restore:
        print("RESTORE THE OWNER'S LIST")
        swap(FULL, a.apply)
    else:
        print(describe(LIVE, "LIVE"))
        print(describe(FULL, "FULL"))
        print(describe(MINIMAL, "MINIMAL"))
        print("\nlive currently matches: %s" % which_is_live())
        if which_is_live() == "MINIMAL":
            print("🔴 THE OWNER'S LIST IS NOT LOADED. --restore --apply before he plays.")


if __name__ == "__main__":
    main()
