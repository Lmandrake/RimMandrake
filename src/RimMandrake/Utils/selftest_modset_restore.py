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
    open(cfg, "w").write("TINY1")
    mb.take_before_copy(cfg, bk, "t2")           # second swap must keep the ORIGINAL before-copy
    check("second swap keeps first before", open(p).read() == "OWNER")
    open(cfg, "w").write("TINY2")
    msg = mb.restore_before(cfg, bk)
    check("restored owner list", open(cfg).read() == "OWNER" and "verified" in msg)
    check("marker consumed", refused(lambda: mb.restore_before(cfg, bk)))
    # tampered before-copy is refused loudly
    mb.take_before_copy(cfg, bk, "t3")
    open(os.path.join(bk, "ModsConfig.before-tier-t3.xml"), "w").write("TAMPERED")
    open(cfg, "w").write("TINY3")
    check("tampered refused", refused(lambda: mb.restore_before(cfg, bk)) and open(cfg).read() == "TINY3")

print("selftest_modset_restore: %s" % ("FAIL " + ", ".join(fails) if fails else "OK 6/6"))
sys.exit(1 if fails else 0)
