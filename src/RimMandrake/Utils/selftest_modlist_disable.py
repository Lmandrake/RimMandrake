#!/usr/bin/env python3
"""STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION: modlist_swap.py --disable takes mods off the live list.

The instance: GENERATOR_MODS_PROVE_INERT_AFTER_CREATION A2 needed a load WITHOUT oblitus.mylittleplanet, and the
lane's only list tool could add (--enable), never remove, so four runs read UNMEASURED on whatever list was up.
Every case runs on a temp ModsConfig; nothing touches the live game's list.
"""
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modlist_swap as S  # noqa: E402
import zoom_guard as Z  # noqa: E402

FAILS = []
X = "oblitus.mylittleplanet"


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def cfg(ids):
    return ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<ModsConfigData>\n  <version>1.6</version>\n  <activeMods>\n%s"
            "  </activeMods>\n  <knownExpansions><li>ludeon.rimworld.odyssey</li></knownExpansions>\n</ModsConfigData>\n"
            % "".join("    <li>%s</li>\n" % i for i in ids))


def live_ids(p):
    return [li.text for li in ET.parse(p).getroot().find("activeMods").findall("li")]


BASE = ["brrainz.harmony", Z.ZOOM, "ludeon.rimworld", "ludeon.rimworld.royalty", "ludeon.rimworld.odyssey",
        X, "some.planetaddon", "addon.of.addon", "mandrake.rm.flowworks"]
INSTALLED = {"some.planetaddon": {"deps": [X, "brrainz.harmony"]}, "addon.of.addon": {"deps": ["some.planetaddon"]},
             "mandrake.rm.flowworks": {"deps": ["brrainz.harmony"]}, X: {"deps": ["brrainz.harmony"]}}


def t_pure():
    kept, removed = S.without(BASE, {X}, lambda p: (INSTALLED.get(p) or {}).get("deps") or [])
    ok(X not in kept and "some.planetaddon" not in kept and "addon.of.addon" not in kept,
       "the named mod and every active mod hanging on it (transitively) leave: %s" % kept)
    ok(kept == [m for m in BASE if m not in (X, "some.planetaddon", "addon.of.addon")], "the rest keep their order")
    ok(dict(removed) == {X: None, "some.planetaddon": X, "addon.of.addon": "some.planetaddon"},
       "each removal says why: %s" % removed)
    kept, removed = S.without(["A.B", "c.d"], {"a.b"}, lambda p: [])
    ok(kept == ["c.d"] and removed == [("A.B", None)], "ids compare lower-case, live spelling kept in the report")


def run(names, ids, apply_it=True, installed=INSTALLED):
    with tempfile.TemporaryDirectory() as d:
        live = os.path.join(d, "ModsConfig.xml")
        with open(live, "w", encoding="utf-8") as f:
            f.write(cfg(ids))
        before = open(live, encoding="utf-8").read()
        S.LIVE, S.STORE = live, os.path.join(d, "store")
        os.makedirs(S.STORE)
        rc = S.disable(names, apply_it, installed=installed)
        after = open(live, encoding="utf-8").read()
        return rc, live_ids(live), after != before, after


def t_disable():
    orig = (S.LIVE, S.STORE, S.is_mod_folder, S.about, Z.zoom_installed)
    S.is_mod_folder = lambda n: "." not in n
    S.about = lambda n: ("mandrake.rm.flowworks", ["brrainz.harmony"]) if n == "FlowWorks" else None
    Z.zoom_installed = lambda: True
    try:
        rc, ids, wrote, text = run([X], BASE)
        ok(rc == 0 and wrote and X not in ids and "some.planetaddon" not in ids and "addon.of.addon" not in ids,
           "the instance: --disable %s --apply leaves a list that lacks it and its dependents: %s" % (X, ids))
        ok("ludeon.rimworld.odyssey" in ids and "ludeon.rimworld.royalty" in ids and Z.ZOOM in ids,
           "every DLC and the zoom mod stay on")
        ok("<knownExpansions>" in text and "<version>1.6</version>" in text, "only activeMods is rewritten")
        rc, ids, wrote, _ = run([X], BASE, apply_it=False)
        ok(rc == 0 and not wrote and X in ids, "without --apply nothing is written (a plan)")
        rc, ids, wrote, _ = run(["FlowWorks"], BASE)
        ok(rc == 0 and "mandrake.rm.flowworks" not in ids and X in ids, "a mod folder resolves to its packageId: %s" % ids)
        rc, ids, wrote, _ = run(["NoSuchMod"], BASE)
        ok(rc == 2 and not wrote, "a folder that resolves nowhere is refused, nothing written")
        rc, ids, wrote, _ = run(["ludeon.rimworld.odyssey"], BASE)
        ok(rc == 2 and not wrote, "a DLC never leaves (every DLC is assumed): refused, nothing written")
        rc, ids, wrote, _ = run(["not.active"], BASE, installed=None)
        ok(rc == 0 and not wrote, "a mod already off: nothing to do, exit 0, and no install scan (installed=None)")
        rc, ids, wrote, _ = run([Z.ZOOM], BASE)
        ok(rc == 2 and not wrote, "the only zoom mod cannot leave: the zoom guard would put it back, so it is refused")
        hung = dict(INSTALLED, **{"ludeon.rimworld.odyssey": {"deps": [X]}})
        rc, ids, wrote, _ = run([X], BASE, installed=hung)
        ok(rc == 2 and not wrote, "a removal that would drag a DLC off is refused")
    finally:
        S.LIVE, S.STORE, S.is_mod_folder, S.about, Z.zoom_installed = orig


def t_cli():
    r = subprocess.run([sys.executable, os.path.join(HERE, "modlist_swap.py"), "--help"], capture_output=True, text=True,
                       timeout=60)
    ok(r.returncode == 0 and "--disable" in r.stdout, "the CLI offers --disable")


def main():
    for t in (t_pure, t_disable, t_cli):
        print("-- " + t.__name__)
        t()
    print("selftest_modlist_disable: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
