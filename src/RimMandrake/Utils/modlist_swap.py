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
    if not os.path.exists(LIVE):
        return "NO LIVE FILE"
    lm = md5(LIVE)
    for path, name in ((FULL, "FULL"), (MINIMAL, "MINIMAL")):
        if os.path.exists(path) and md5(path) == lm:
            return name
    return "UNRECOGNISED (neither FULL nor MINIMAL - someone edited it)"


def snapshot():
    """Archive whatever is live right now before overwriting it."""
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(STORE, "ModsConfig.PRESWAP.%s.xml" % stamp)
    shutil.copy2(LIVE, dst)
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
