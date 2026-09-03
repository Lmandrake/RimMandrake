#!/usr/bin/env python3
"""Swap RimWorld's live mod list between the owner's full list and a minimal test set.

CHECK owns this. The point is that a cold load on the owner's list is ~25 minutes, and
the worldmap bridge work needs many reloads. A minimal list makes a reload cheap.
⚠️ The active count is not written here on purpose — `--status` measures it. Every doc
that hardcoded it (583, 578, 585) was wrong within days of being written.

🔴 The owner's real list is infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml.
   --restore puts it back. Never leave the machine on the minimal list.

    modlist_swap.py --status
    modlist_swap.py --minimal          # plan only
    modlist_swap.py --minimal --apply
    modlist_swap.py --restore --apply
"""
import argparse, hashlib, os, sys, datetime
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import MODS_CONFIG  # noqa: E402
from atomic_copy import atomic_copy  # noqa: E402  temp+os.replace; never a bare copy2

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LIVE = MODS_CONFIG
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
    """The active mod ids, in order, or None if the file is missing or unreadable.

    ⚠️ A HALF-WRITTEN OR EMPTY `<li/>` MUST NOT BE A TRACEBACK. RimWorld, RimSort and
    Steam all rewrite this file and none of them tells the others; a torn read used to
    come out of here as `ParseError` or `AttributeError: 'NoneType' has no 'strip'`,
    which reads as a broken tool rather than as "look at your config". None means
    unreadable, and every caller already has a path for that.
    """
    if not os.path.exists(p):
        return None
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError:
        return None
    am = root.find("activeMods")
    if am is None:
        return []
    return [li.text.strip() for li in am.findall("li") if li.text and li.text.strip()]


def describe(p, label):
    if not os.path.exists(p):
        return "%-9s MISSING  %s" % (label, p)
    m = mods(p)
    if m is None:
        # Present but unparseable is a different fact from absent, and the difference
        # decides whether you go looking for a deleted file or a truncated one.
        return "%-9s UNREADABLE (present, will not parse)  %s" % (label, p)
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
    os.makedirs(STORE, exist_ok=True)
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
    # Atomic even here: a half-written archive would be counted as a kept copy by the
    # md5 sweep above on the next swap, and the real backup would then be skipped.
    atomic_copy(LIVE, dst)
    print("  snapshot : %s" % os.path.basename(dst))
    return dst


def swap(src, apply_it):
    if not os.path.exists(src):
        sys.exit("REFUSING: %s does not exist. Build it first." % src)
    src_ids = mods(src)
    if src_ids is None:
        sys.exit("REFUSING: %s will not parse. Do not write it over the live list." % src)
    n_src, n_live = len(src_ids), len(mods(LIVE) or [])
    print("  live now : %d active (%s)" % (n_live, which_is_live()))
    print("  would be : %d active  <- %s" % (n_src, src))
    if not apply_it:
        print("\nplan only. re-run with --apply")
        return
    # ⚠️ `md5(LIVE)` used to be called with no existence check, so a missing config
    # turned --apply into a FileNotFoundError traceback instead of doing the one thing
    # that is obviously right: write the list, with nothing to snapshot.
    if not os.path.exists(LIVE):
        print("\n  no live file to archive — writing %s fresh." % os.path.basename(src))
        arch = "(nothing — there was no live file)"
    elif md5(src) == md5(LIVE):
        print("\nalready identical. nothing written.")
        return
    else:
        arch = snapshot()
    atomic_copy(src, LIVE)
    print("\n  archived live -> %s" % arch)
    print("  WROTE %s -> live  (%d active)" % (os.path.basename(src), n_src))
    print("  verify: md5 %s" % md5(LIVE))


def capture_full(apply_it):
    """Adopt the live list as FULL.LATEST — the restore point must track deliberate changes.

    🔴 WHY THIS EXISTS. FULL.LATEST is what `--restore` writes back, so every mod
    add/removal made directly against the live file silently rots it, and `--restore`
    then UNDOES that decision. Measured 2026-09-02: STARWARS_DONOR_SUNSET_1 retired
    `starwars.themedsounds`, `m3.continued.jangodsoul.starwars.tsda` and `lumi.swlights`
    from the live file with the owner's green light (ee675203) and left FULL.LATEST
    holding all three — a `--restore` would have resurrected three deliberately
    retired mods, and nothing anywhere would have said so.

    ⚠️ This is deliberately NOT automatic. FULL.LATEST is the owner's list, and a
    temporary debug mod pulled in for one investigation does not belong in it. Look at
    the diff this prints and decide; that is the whole point of the command existing
    separately from the swap.
    """
    live_ids, full_ids = mods(LIVE), mods(FULL) or []
    if live_ids is None:
        sys.exit("REFUSING: cannot read the live list at\n  %s" % LIVE)
    added = [m for m in live_ids if m not in set(full_ids)]
    dropped = [m for m in full_ids if m not in set(live_ids)]
    print("  FULL.LATEST : %d active" % len(full_ids))
    print("  live        : %d active" % len(live_ids))
    for m in dropped:
        print("    - %s   (in FULL.LATEST, NOT live — would be forgotten)" % m)
    for m in added:
        print("    + %s   (live only — would become part of the owner's list)" % m)
    if not added and not dropped:
        print("\n  identical mod sets. nothing to capture.")
        return
    # 🔴 REFUSE WHILE MINIMAL IS LIVE. Capturing then would replace the owner's real
    # restore point with the 13-mod test list, and `--restore` — the one command that
    # is supposed to undo that — would put the test list back. Recovery would be git
    # alone. Found in review 2026-09-02; `cherrypicker_swap.capture_ship` had the
    # analogous guard from the start and this did not.
    if which_is_live().startswith("MINIMAL"):
        sys.exit("REFUSING: the MINIMAL test list is live. Capturing it as FULL.LATEST "
                 "would destroy\nthe owner's real restore point and make --restore "
                 "restore the test list.\n\n  put his list back first:  "
                 "modlist_swap.py --restore --apply")
    if not apply_it:
        print("\nplan only. Read those lines — a debug mod does not belong in the "
              "owner's list.\nre-run with --apply")
        return
    # ⚠️ ARCHIVE **FULL**, NOT LIVE. This used to call snapshot(), which archives the
    # LIVE file — then overwrote FULL with that same live content and printed
    # "archived old FULL.LATEST". The old restore point was never copied anywhere and
    # the message said it had been. A backup that is a copy of the NEW content is
    # worse than no backup, because it stops you reaching for git.
    arch = None
    if os.path.exists(FULL):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        arch = os.path.join(STORE, "ModsConfig.FULL.PRECAPTURE.%s.xml" % stamp)
        if not any(md5(os.path.join(STORE, n)) == md5(FULL)
                   for n in os.listdir(STORE)
                   if n.lower().endswith(".xml") and n != os.path.basename(FULL)
                   and os.path.isfile(os.path.join(STORE, n))):
            atomic_copy(FULL, arch)
        else:
            arch = None
            print("  archive : skipped, the old FULL.LATEST is already kept elsewhere")
    atomic_copy(LIVE, FULL)
    if arch:
        print("\n  archived the OLD FULL.LATEST -> %s" % os.path.basename(arch))
    print("  WROTE live -> FULL.LATEST (%d active)" % len(live_ids))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--status", action="store_true")
    g.add_argument("--minimal", action="store_true", help="swap to the minimal test list")
    g.add_argument("--restore", action="store_true", help="put the owner's full list back")
    g.add_argument("--capture-full", action="store_true",
                   help="adopt the live list as FULL.LATEST, after a deliberate mod change")
    ap.add_argument("--apply", action="store_true", help="actually write; default is plan only")
    a = ap.parse_args()

    # `--apply` is a modifier, not a mode. On its own it used to print the status page
    # and exit 0 — a command that looks like it did something and did nothing.
    if a.apply and not (a.minimal or a.restore or a.capture_full):
        sys.exit("REFUSING: --apply on its own has nothing to apply. Say which:\n"
                 "  --minimal --apply       swap to the minimal test list\n"
                 "  --restore --apply       put the owner's full list back\n"
                 "  --capture-full --apply  adopt the live list as FULL.LATEST")

    if a.capture_full:
        print("CAPTURE THE LIVE LIST AS FULL.LATEST")
        capture_full(a.apply)
    elif a.minimal:
        print("SWAP TO MINIMAL")
        swap(MINIMAL, a.apply)
    elif a.restore:
        print("RESTORE THE OWNER'S LIST")
        swap(FULL, a.apply)
    else:
        print(describe(LIVE, "LIVE"))
        print(describe(FULL, "FULL"))
        print(describe(MINIMAL, "MINIMAL"))
        live = which_is_live()
        print("\nlive currently matches: %s" % live)
        # 🔴 startswith, NEVER ==. `which_is_live` returns "MINIMAL (same mods and
        # order; file reformatted, e.g. by RimSort)" for the case its own docstring
        # says is the COMMON one, and an `==` test silently withheld this alarm in
        # exactly that case — the test list live, and nothing on screen saying so
        # (review finding, 2026-09-02). `capture_full` already used startswith.
        if live.startswith("MINIMAL"):
            print("🔴 THE OWNER'S LIST IS NOT LOADED. --restore --apply before he plays.")
        elif live.startswith("UNRECOGNISED"):
            print("⚠️ The live list is neither stored list. If that change was deliberate:\n"
                  "   modlist_swap.py --capture-full --apply")


if __name__ == "__main__":
    main()
