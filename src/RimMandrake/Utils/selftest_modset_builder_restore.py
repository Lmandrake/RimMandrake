#!/usr/bin/env python3
"""modset_builder's OWNED swap (--by / --restore-own, LANE_TIER_WIRE_A_WHOLE_LIST_LOAD), temp dirs only.

Relentless's staging worker writes a `live-tier:` list from the item's clone and the supervisor restores it from the books
clone, so the marker lives in agent storage under the owner's name and restore_own undoes only that owner's swap:
  the tier list still live -> the before-copy back, md5-verified, marker gone;
  the before-copy already live -> marker cleared, nothing written;
  the list moved on (owner or another tool wrote it) -> marker cleared, nothing written over it, before-copy kept;
  the tier live but its before-copy gone -> RestoreRefused, nothing written;
  no marker -> nothing written; a second owner's swap is invisible to the first; an owner name with a path is refused.
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modset_builder as mb  # noqa: E402

fails = []


def check(name, cond):
    print("%s  %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        fails.append(name)


def swap(cfg, bk, tier, write):
    """What `--tier <tier> --apply --by X` does to the files: before-copy + marker, the tier list, its md5."""
    mb.take_before_copy(cfg, bk, tier)
    open(cfg, "w").write(write)
    mb.record_tier_written(cfg, bk)


with tempfile.TemporaryDirectory() as d:
    cfg, bk, other = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "relentless"), os.path.join(d, "someone")
    open(cfg, "w").write("OWNER_LIST")
    check("no marker: nothing written", "nothing written" in mb.restore_own(cfg, bk) and open(cfg).read() == "OWNER_LIST")

    swap(cfg, bk, "ratchet_pilot", "TIER_RATCHET")
    check("another owner sees no swap of its own", "nothing written" in mb.restore_own(cfg, other)
          and open(cfg).read() == "TIER_RATCHET")
    msg = mb.restore_own(cfg, bk)
    check("tier live: the before-copy goes back, verified", open(cfg).read() == "OWNER_LIST" and "verified" in msg)
    check("and the marker is gone", not os.path.exists(os.path.join(bk, mb.SWAP_MARKER)))
    check("a second restore writes nothing", "nothing written" in mb.restore_own(cfg, bk))

    swap(cfg, bk, "ratchet_pilot", "TIER_RATCHET")
    swap(cfg, bk, "gizkastowaway", "TIER_GIZKA")       # a second tier on top keeps the ORIGINAL before-copy
    mb.restore_own(cfg, bk)
    check("two tiers in a row restore the list before the first", open(cfg).read() == "OWNER_LIST")

    swap(cfg, bk, "ratchet_pilot", "TIER_RATCHET")
    open(cfg, "w").write("OWNER_LIST")                  # someone restored it already
    msg = mb.restore_own(cfg, bk)
    check("already back: marker cleared, nothing written", "already equals" in msg and open(cfg).read() == "OWNER_LIST"
          and not os.path.exists(os.path.join(bk, mb.SWAP_MARKER)))

    swap(cfg, bk, "ratchet_pilot", "TIER_RATCHET")
    open(cfg, "w").write("OWNER_NEWER_LIST")            # the list moved on: never written over
    msg = mb.restore_own(cfg, bk)
    check("moved on: nothing written over it", open(cfg).read() == "OWNER_NEWER_LIST" and "moved on" in msg)
    check("and the swap is over (marker cleared, before-copy kept)",
          not os.path.exists(os.path.join(bk, mb.SWAP_MARKER))
          and open(os.path.join(bk, "ModsConfig.before-tier-ratchet_pilot.xml")).read() == "OWNER_LIST")

    open(cfg, "w").write("OWNER_LIST")
    swap(cfg, bk, "ratchet_pilot", "TIER_RATCHET")
    os.remove(os.path.join(bk, "ModsConfig.before-tier-ratchet_pilot.xml"))
    try:
        mb.restore_own(cfg, bk)
        refused = False
    except mb.RestoreRefused:
        refused = True
    check("tier live, before-copy gone: refused, nothing written", refused and open(cfg).read() == "TIER_RATCHET")

    os.environ["RM_DATA_ROOT"] = d
    mb_root = mb.owned_backups("relentless")
    check("the owned marker lives in agent storage, per owner",
          mb_root.replace("\\", "/").endswith("/modset_swaps/relentless") and mb_root.startswith(d))
    for bad in ("a/b", "..", "", "x y"):
        try:
            mb.owned_backups(bad)
            ok_ = False
        except ValueError:
            ok_ = True
        check("owner name %r refused" % bad, ok_)

print("selftest_modset_builder_restore: %s" % ("FAIL %d" % len(fails) if fails else "OK"))
sys.exit(1 if fails else 0)
