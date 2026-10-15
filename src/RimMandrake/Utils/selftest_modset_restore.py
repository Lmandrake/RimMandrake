#!/usr/bin/env python3
"""modset_builder --restore must restore the swap's before-copy, md5-verified (temp dirs only)."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modset_builder as mb

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

def refused(fn):
    try:
        fn(); return False
    except mb.RestoreRefused:
        return True

with tempfile.TemporaryDirectory() as d:
    cfg, bk = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "bk")
    open(cfg, "w").write("OWNER")
    check("refuse without marker", refused(lambda: mb.restore_before(cfg, bk)))
    p = mb.take_before_copy(cfg, bk, "t1")
    open(cfg, "w").write("TINY1"); mb.record_tier_written(cfg, bk)
    mb.take_before_copy(cfg, bk, "t2")           # second swap must keep the ORIGINAL before-copy
    check("second swap keeps first before", open(p).read() == "OWNER")
    open(cfg, "w").write("TINY2"); mb.record_tier_written(cfg, bk)
    msg = mb.restore_before(cfg, bk)
    check("restored owner list", open(cfg).read() == "OWNER" and "verified" in msg)
    check("marker consumed", refused(lambda: mb.restore_before(cfg, bk)))
    # tampered before-copy is refused loudly
    mb.take_before_copy(cfg, bk, "t3")
    open(os.path.join(bk, "ModsConfig.before-tier-t3.xml"), "w").write("TAMPERED")
    open(cfg, "w").write("TINY3")
    check("tampered refused", refused(lambda: mb.restore_before(cfg, bk)) and open(cfg).read() == "TINY3")


# --- r5 case 1: a stale marker (owner restored by hand / --restore-full) must not pin an old before-copy
def fresh(d):
    cfg, bk = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "bk")
    return cfg, bk

with tempfile.TemporaryDirectory() as d:
    cfg, bk = fresh(d)
    open(cfg, "w").write("OWNER_V1")
    mb.take_before_copy(cfg, bk, "a"); open(cfg, "w").write("TIER_A"); mb.record_tier_written(cfg, bk)
    # manual restore (RimSort) of a NEWER owner list; marker left behind
    open(cfg, "w").write("OWNER_V1")
    open(cfg, "w").write("OWNER_V2_MORE_MODS")
    check("stale marker + changed live refused", refused(lambda: mb.take_before_copy(cfg, bk, "b")))
    # owner list identical to before-copy: stale marker, re-snapshot is safe
    open(cfg, "w").write("OWNER_V1")
    p = mb.take_before_copy(cfg, bk, "b")
    check("stale marker, owner list back -> fresh snapshot", os.path.basename(p).endswith("-b.xml"))
    open(cfg, "w").write("TIER_B"); mb.record_tier_written(cfg, bk)
    check("restore gives owner list", (mb.restore_before(cfg, bk), open(cfg).read())[1] == "OWNER_V1")
    # --restore-full path: marker cleared, next swap snapshots the then-current list
    mb.take_before_copy(cfg, bk, "c"); open(cfg, "w").write("TIER_C"); mb.record_tier_written(cfg, bk)
    check("clear marker", mb.clear_swap_marker(bk) and refused(lambda: mb.restore_before(cfg, bk)))
    open(cfg, "w").write("OWNER_V3")
    p = mb.take_before_copy(cfg, bk, "d"); open(cfg, "w").write("TIER_D"); mb.record_tier_written(cfg, bk)
    check("after restore-full a new swap restores V3", (mb.restore_before(cfg, bk), open(cfg).read())[1] == "OWNER_V3")

# --- r5 case 2: bad marker / missing or changed before-copy must refuse, never snapshot the tier list
with tempfile.TemporaryDirectory() as d:
    cfg, bk = fresh(d)
    open(cfg, "w").write("OWNER")
    p = mb.take_before_copy(cfg, bk, "a"); open(cfg, "w").write("TIER_A"); mb.record_tier_written(cfg, bk)
    marker = os.path.join(bk, mb.SWAP_MARKER)
    good = open(marker).read()
    open(marker, "w").write("{not json")
    check("garbled marker refused", refused(lambda: mb.take_before_copy(cfg, bk, "b")))
    check("garbled marker left alone", open(marker).read() == "{not json")
    open(marker, "w").write(good); os.remove(p)
    check("missing before-copy refused", refused(lambda: mb.take_before_copy(cfg, bk, "b")))
    open(p, "w").write("TAMPERED")
    check("changed before-copy refused", refused(lambda: mb.take_before_copy(cfg, bk, "b")))
    check("tier list never became a before-copy", open(cfg).read() == "TIER_A" and open(marker).read() == good)
    # old-format marker (no tier_md5) mid-swap: live is neither -> refused, not guessed
    open(p, "w").write("OWNER")
    import json
    json.dump({"tier": "a", "before": os.path.basename(p), "md5": mb._md5(p)}, open(marker, "w"))
    check("marker without tier_md5 refused", refused(lambda: mb.take_before_copy(cfg, bk, "b")))

print("selftest_modset_restore: %s" % ("FAIL " + ", ".join(fails) if fails else "OK"))
sys.exit(1 if fails else 0)
