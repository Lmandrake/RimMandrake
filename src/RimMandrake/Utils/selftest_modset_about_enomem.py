#!/usr/bin/env python3
"""selftest_modset_about_enomem.py -- a mod whose About.xml cannot be read for want of memory is never "not installed"
(RIMMANDRAKE_RETRY_ABOUT_READ_ON_ENOMEM_BIOTECH_READ_MISSING).

Offline, on a fake Data folder, with the read patched to raise OSError(ENOMEM):
  - a read that fails and then works gives the same map as one that never failed;
  - a read that keeps failing raises AboutUnreadable, so no tier reads a DLC missing; build_match passes it on, as a read
    that could not look, and never as "gives no list";
  - the same for a listing of the folder; a malformed About.xml still reads "not installed" and raises nothing.
"""
import errno
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
import modset_builder as MB     # noqa: E402
import build_match as BM        # noqa: E402

FAILS = []
REAL = (MB.ET.parse, MB.os.listdir)


def ok(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def blind(real, left, match):
    """real, raising ENOMEM the first left[0] times it is asked for a path holding match."""
    def f(p, *a):
        if match in str(p) and left[0] > 0:
            left[0] -= 1
            raise OSError(errno.ENOMEM, "Cannot allocate memory")
        return real(p, *a)
    return f


def scan():
    """-> the map, or the name of what scan raised."""
    try:
        return sorted(MB.scan())
    except Exception as e:      # noqa: BLE001  the reading under test
        return type(e).__name__


def main():
    tmp = tempfile.mkdtemp(prefix="about_enomem_")
    MB.DATA, MB.WORKSHOP, MB.LOCAL_MODS = (os.path.join(tmp, x) for x in ("Data", "ws", "Mods"))
    MB.ABOUT_WAITS = (0, 0)
    for d, pid in (("Core", "ludeon.rimworld"), ("Biotech", "ludeon.rimworld.biotech")):
        os.makedirs(os.path.join(MB.DATA, d, "About"))
        with open(os.path.join(MB.DATA, d, "About", "About.xml"), "w") as f:
            f.write("<ModMetaData><packageId>%s</packageId></ModMetaData>" % pid)
    os.makedirs(os.path.join(MB.DATA, "Bad", "About"))
    with open(os.path.join(MB.DATA, "Bad", "About", "About.xml"), "w") as f:
        f.write("<ModMetaData><packageId>")
    both = ["ludeon.rimworld", "ludeon.rimworld.biotech"]
    try:
        ok(scan() == both, "a clean scan reads both, and a malformed About.xml reads as not installed")
        MB.ET.parse = blind(REAL[0], [2], "Biotech")
        ok(scan() == both, "about-read-waits-out-enomem: a read that fails twice for want of memory is read again: %s" % scan())
        MB.ET.parse = blind(REAL[0], [10 ** 6], "Biotech")
        got = scan()
        ok(got == "AboutUnreadable", "a read that keeps failing is could-not-look, never a missing DLC: %s" % got)
        real_def, MB.tier_def = MB.tier_def, lambda *a, **k: {"want": [], "dlc": True}
        try:
            why = BM._resolve_tier("t", [])
            raised = None
        except Exception as e:      # noqa: BLE001
            why, raised = None, e
        MB.tier_def = real_def
        ok(raised is not None and BM.could_not_look(raised),
           "build_match passes it on as could-not-look: returned %s, raised %r" % (why, raised))
        ok(not BM.could_not_look(ValueError("x")) if hasattr(BM, "could_not_look") else False,
           "another error is not could-not-look")
        MB.ET.parse = REAL[0]
        MB.os.listdir = blind(REAL[1], [2], "Data")
        ok(scan() == both, "a folder listing that fails twice is listed again")
        MB.os.listdir = blind(REAL[1], [10 ** 6], "Data")
        got = scan()
        ok(got == "AboutUnreadable", "a listing that keeps failing is could-not-look: %s" % got)
    finally:
        MB.ET.parse, MB.os.listdir = REAL
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
