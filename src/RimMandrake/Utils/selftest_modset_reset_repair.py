#!/usr/bin/env python3
"""A crash that resets ModsConfig to Core+DLC must not strand the swap (STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST).

RimWorld answers a crashed load by rewriting the list to Core+DLC (resetModsConfigOnCrash). take_before_copy then saw a
list that was neither the tier nor the before-copy and refused every swap until a hand restore (SteveDesktop 2026-11-06,
after canary 618fb0). Temp dirs only. RESET_LIST is that incident's file as it stood on SteveDesktop, BOM included.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modset_builder as mb  # noqa: E402

RESET_LIST = ("﻿" + '<?xml version="1.0" encoding="utf-8"?>\n<ModsConfigData>\n  <version>1.6.4871 rev591</version>\n'
              "  <activeMods>\n    <li>ludeon.rimworld</li>\n    <li>ludeon.rimworld.royalty</li>\n"
              "    <li>ludeon.rimworld.ideology</li>\n    <li>ludeon.rimworld.biotech</li>\n"
              "    <li>ludeon.rimworld.anomaly</li>\n    <li>ludeon.rimworld.odyssey</li>\n  </activeMods>\n"
              "  <knownExpansions>\n    <li>ludeon.rimworld.royalty</li>\n  </knownExpansions>\n</ModsConfigData>\n")
OWNER = "<ModsConfigData><activeMods><li>brrainz.harmony</li><li>ludeon.rimworld</li><li>a.b</li></activeMods></ModsConfigData>"
TIER = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>mandrake.rm.flowworks</li></activeMods></ModsConfigData>"
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def put(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def get(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def refused(fn):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            fn()
    except mb.RestoreRefused:
        return True
    return False


def swapped(d):
    """A live swap: the owner's list is aside, the tier is live and stamped. -> (config, backups, marker, before-copy)"""
    cfg, bk = os.path.join(d, "ModsConfig.xml"), os.path.join(d, "bk")
    put(cfg, OWNER)
    before = mb.take_before_copy(cfg, bk, "t1")
    put(cfg, TIER)
    mb.record_tier_written(cfg, bk)
    return cfg, bk, os.path.join(bk, mb.SWAP_MARKER), before


def t_detect(d):
    p = os.path.join(d, "list.xml")
    put(p, RESET_LIST)
    check(mb.is_game_reset_list(p), "the incident's own list reads as a game reset")
    put(p, RESET_LIST.replace("ludeon.rimworld</li>", "Ludeon.RimWorld</li>", 1))
    check(mb.is_game_reset_list(p), "ids are read case-blind")
    for name, text in (("one mod more", RESET_LIST.replace("</activeMods>", "<li>a.b</li></activeMods>")),
                       ("Harmony more", RESET_LIST.replace("</activeMods>", "<li>brrainz.harmony</li></activeMods>")),
                       ("a lookalike id", RESET_LIST.replace("</activeMods>", "<li>ludeon.rimworldx</li></activeMods>")),
                       ("expansions without Core", RESET_LIST.replace("<li>ludeon.rimworld</li>", "")),
                       ("an empty list", "<ModsConfigData><activeMods/></ModsConfigData>"),
                       ("no activeMods", "<ModsConfigData/>"), ("not XML", "OWNER"), ("a tier", TIER)):
        put(p, text)
        check(not mb.is_game_reset_list(p), "%s is no game reset" % name)
    check(not mb.is_game_reset_list(os.path.join(d, "absent.xml")), "a missing file is no game reset")
    tiers = [k for k, t in mb.TIERS.items() if t["want"] and all(mb.GAME_RESET_ID.fullmatch(w.lower()) for w in t["want"])]
    check(not tiers, "no modset_builder tier is this bare: %s" % tiers)


def t_swap_survives_the_reset(d):
    cfg, bk, marker, before = swapped(d)
    put(cfg, RESET_LIST)                            # the crash
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        stamp = mb.take_before_copy(cfg, bk, "t2")  # refused before this fix: "neither its tier list nor its before-copy"
    check(get(cfg) == OWNER, "the next swap puts the before-copy back")
    check(get(stamp) == OWNER, "and snapshots the owner's list, never the Core+DLC one")
    check("REPAIRED" in out.getvalue(), "and says so: %r" % out.getvalue())
    put(cfg, TIER)
    mb.record_tier_written(cfg, bk)
    with contextlib.redirect_stdout(io.StringIO()):
        mb.restore_before(cfg, bk)
    check(get(cfg) == OWNER, "a restore after that swap still gives the owner's list")


def t_repair(d):
    cfg, bk, marker, before = swapped(d)
    check(mb.repair_game_reset(cfg, bk) is None and get(cfg) == TIER and os.path.exists(marker),
          "the live tier list is left alone")
    put(cfg, RESET_LIST)
    msg = mb.repair_game_reset(cfg, bk)
    check(get(cfg) == OWNER and not os.path.exists(marker) and "REPAIRED" in (msg or ""), "repaired, md5-checked: %s" % msg)
    check(mb.repair_game_reset(cfg, bk) is None, "a second call finds nothing to do")
    put(cfg, RESET_LIST)
    check(mb.repair_game_reset(cfg, bk) is None and get(cfg) == RESET_LIST, "no swap on record: nothing to restore from")


def t_foreign_list_still_refused(d):
    cfg, bk, marker, before = swapped(d)
    put(cfg, OWNER.replace("a.b", "c.d"))
    check(mb.repair_game_reset(cfg, bk) is None, "a list with other mods is no reset")
    check(refused(lambda: mb.take_before_copy(cfg, bk, "t2")) and "c.d" in get(cfg), "and the swap still refuses it")


def t_bare_tier_is_not_a_reset(d):
    cfg, bk, marker, before = swapped(d)
    put(cfg, RESET_LIST)
    mb.record_tier_written(cfg, bk)                 # a swap that really wrote this list
    check(mb.repair_game_reset(cfg, bk) is None and get(cfg) == RESET_LIST, "the swap's own tier list is left alone")
    put(before, RESET_LIST)
    m = json.load(open(marker))
    m.update(md5=mb._md5(before), tier_md5="other")
    json.dump(m, open(marker, "w"))
    check(mb.repair_game_reset(cfg, bk) is None, "live == before-copy: nothing to do")


def t_untrusted_before_copy(d):
    cfg, bk, marker, before = swapped(d)
    good = get(marker)
    put(cfg, RESET_LIST)
    put(before, "TAMPERED")
    check(refused(lambda: mb.repair_game_reset(cfg, bk)) and get(cfg) == RESET_LIST, "a changed before-copy: refused, live untouched")
    check(refused(lambda: mb.take_before_copy(cfg, bk, "t2")) and get(marker) == good, "the swap refuses too, marker kept")
    os.remove(before)
    check(refused(lambda: mb.repair_game_reset(cfg, bk)) and get(cfg) == RESET_LIST, "a missing before-copy: refused, live untouched")
    put(marker, "{not json")
    check(refused(lambda: mb.repair_game_reset(cfg, bk)) and get(cfg) == RESET_LIST, "a garbled marker: refused, live untouched")


def t_restores_repair(d):
    cfg, bk, marker, before = swapped(d)
    put(cfg, RESET_LIST)
    msg = mb.restore_before(cfg, bk)                # refused before this fix
    check(get(cfg) == OWNER and "REPAIRED" in msg, "--restore repairs a reset: %s" % msg)
    cfg, bk, marker, before = swapped(d)
    put(cfg, RESET_LIST)
    msg = mb.restore_own(cfg, bk)                   # used to clear the marker and leave Core+DLC live
    check(get(cfg) == OWNER and "REPAIRED" in msg and not os.path.exists(marker), "--restore-own repairs a reset: %s" % msg)


DRIVER = """
import os, sys
sys.path.insert(0, sys.argv[1])
import modset_builder as mb
mb.CONFIG, mb.BACKUPS = sys.argv[2], sys.argv[3]
mb.scan = lambda: sys.exit("--repair-reset must need no mod scan")
sys.argv = ["modset_builder.py", "--repair-reset", "--not-my-bridge", "selftest"]
sys.exit(mb.main())
"""


def t_cli(d):
    cfg, bk, marker, before = swapped(d)
    env = dict(os.environ, RM_MODSET_LOCK=os.path.join(d, "lock"))
    env.pop("RIMFLOW_SEAT", None)

    def cli():
        return subprocess.run([sys.executable, "-c", DRIVER, HERE, cfg, bk], env=env, capture_output=True, text=True, timeout=120)
    r = cli()
    check(r.returncode == 0 and "nothing written" in r.stdout and get(cfg) == TIER, "CLI on a tier list: %s" % (r.stdout + r.stderr)[-200:])
    put(cfg, RESET_LIST)
    r = cli()
    check(r.returncode == 0 and "REPAIRED" in r.stdout and get(cfg) == OWNER, "CLI on a reset list: %s" % (r.stdout + r.stderr)[-200:])
    cfg, bk, marker, before = swapped(d)
    put(cfg, RESET_LIST)
    os.remove(before)
    r = cli()
    check(r.returncode == 1 and "REFUSING --repair-reset" in r.stdout and get(cfg) == RESET_LIST, "CLI refusal exits 1: %s" % (r.stdout + r.stderr)[-200:])


def main():
    for t in (t_detect, t_swap_survives_the_reset, t_repair, t_foreign_list_still_refused, t_bare_tier_is_not_a_reset,
              t_untrusted_before_copy, t_restores_repair, t_cli):
        with tempfile.TemporaryDirectory() as d:
            t(d)
    print("selftest_modset_reset_repair: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
