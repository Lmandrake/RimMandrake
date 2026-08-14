#!/usr/bin/env python3
"""
preload_check.py — validate every hand-edited game config BEFORE a load.

A RimWorld load costs ~25-30 minutes. Almost everything we edit by hand outside
the repo fails SILENTLY: a mod listed but absent, a load-order constraint
inverted, a Cherry Picker key that resolves to nothing, a settings file whose XML
is malformed and is therefore replaced with an empty one at startup. None of
those produce a red error, and several produce a perfectly clean log.

This is the gate. Run it immediately before launching.

    python3 preload_check.py            # report, exit 1 on any FAIL
    python3 preload_check.py --quiet    # only failures

WHAT IT CHECKS, and why each one is here rather than invented

  1. ModsConfig.xml parses, and every active packageId exists on disk.
     "Listed but absent" is the classic — the game drops the mod and carries on.

  2. No duplicate entries in activeMods.

  3. 🔴 Load-order constraints, derived from OUR OWN About.xml files rather than
     hardcoded. Every <loadAfter> target that is itself active must appear
     EARLIER. A texture override that loads before its donor is invisible with no
     log line; a patch mod above its target patches nothing.

  4. 🔴 DEAD loadAfter targets — a packageId that matches no installed mod. The
     rule is then 100% inert and looks maintained. This has already bitten twice.

  5. Cherry Picker's settings: XML well-formed, and every key valid. A key with
     no "/" aborts EVERY removal at startup; an unresolvable or out-of-scope key
     is silently ignored. Delegated to cherrypick_build.check().

  6. Every Config/Mod_*.xml parses and has a <SettingsBlock> root. Malformed mod
     settings are caught by RimWorld, logged as a yellow warning, and REPLACED
     WITH EMPTY DEFAULTS — losing the whole file's content quietly.

  7. Explicit constraints that no About.xml can express, listed in HARD_RULES.
"""

import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_paths as GP                                   # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONFIG = os.path.join(GP.LOCALLOW, "Config")
MODSCONFIG = os.path.join(CONFIG, "ModsConfig.xml")
INDEX = os.path.join(REPO, "research", "RimMandrake", "installed_packageids.json")
SRC = os.path.join(REPO, "src")

# Constraints that live in no mod's metadata.
#   (earlier, later, why)
HARD_RULES = [
    ("owlchemist.cherrypicker", "oskarpotocki.vanillafactionsexpanded.core",
     "the mod author's own changelog: VEF must load AFTER Cherry Picker, "
     "because of how VEF handles recipe inheritance"),
]

# Cherry Picker must also precede anything that caches def lists in its own
# static constructor, which is most frameworks. Rather than enumerate them,
# assert it sits near the very top.
CHERRYPICKER_MAX_INDEX = 40

FAIL, WARN, OK = "FAIL", "WARN", "ok"
results = []


def add(level, check, detail):
    results.append((level, check, detail))


def active_mods():
    tree = ET.parse(MODSCONFIG)
    li = tree.getroot().find("activeMods")
    return [(e.text or "").strip() for e in li.findall("li")] if li is not None else []


def own_package_id(path):
    """packageId that is a DIRECT child of ModMetaData — never a dependency's."""
    try:
        raw = open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return None, []
    stripped = re.sub(
        r"<(modDependencies|modDependenciesByVersion|incompatibleWith|loadBefore)"
        r"\b.*?</\1>", "", raw, flags=re.S | re.I)
    pid = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", stripped, re.I)
    after = re.search(r"<loadAfter>(.*?)</loadAfter>", stripped, re.S | re.I)
    targets = re.findall(r"<li>\s*([^<\s]+)\s*</li>", after.group(1)) if after else []
    return (pid.group(1) if pid else None), targets


def main():
    quiet = "--quiet" in sys.argv

    # ---- 1/2. ModsConfig ------------------------------------------------
    try:
        active = active_mods()
    except Exception as e:
        add(FAIL, "ModsConfig.xml parses", str(e))
        report(quiet)
        return 1
    add(OK, "ModsConfig.xml parses", "%d active mods" % len(active))

    lower = [m.lower() for m in active]
    pos = {m: i for i, m in enumerate(lower)}
    dupes = {m for m in lower if lower.count(m) > 1}
    add(FAIL if dupes else OK, "no duplicate activeMods entries",
        ", ".join(sorted(dupes)) if dupes else "none")

    try:
        with open(INDEX, encoding="utf-8") as fh:
            installed = {v["packageId"].lower() for v in json.load(fh).values()}
    except OSError:
        installed = set()
        add(WARN, "installed packageId index", "missing — run build_packageid_index.py")

    # The base game and its DLC are not in the workshop/local index, and a
    # loadAfter naming them is legitimate. Without this, `Ludeon.RimWorld` reads
    # as a dead target.
    installed |= {"ludeon.rimworld", "ludeon.rimworld.royalty",
                  "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
                  "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"}

    # 🔴 The index is a SNAPSHOT and goes stale the moment a mod is subscribed or
    # a new local mod is deployed. Falling back to the disk keeps a stale index
    # from raising a false "listed but absent" — which is the one alarm that
    # must never cry wolf, because the real thing silently drops a mod.
    def on_disk(pid):
        for root in (os.path.join(GP.STEAM_WORKSHOP) if hasattr(GP, "STEAM_WORKSHOP")
                     else "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100",
                     "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"):
            if not os.path.isdir(root):
                continue
            for entry in os.listdir(root):
                about = os.path.join(root, entry, "About", "About.xml")
                if os.path.isfile(about):
                    got, _ = own_package_id(about)
                    if got and got.lower() == pid:
                        return True
        return False

    if installed:
        maybe = [m for m in lower if m not in installed]
        absent = [m for m in maybe if not on_disk(m)]
        stale = [m for m in maybe if m not in absent]
        add(FAIL if absent else OK, "every active mod is present on disk",
            ", ".join(absent) if absent else
            ("none listed-but-absent" + (" (%d found on disk but missing from the "
             "index — regenerate it)" % len(stale) if stale else "")))

    # ---- 3/4. load order, derived from our own About.xml ----------------
    inverted, dead = [], []
    for about in glob.glob(os.path.join(SRC, "*", "*", "About", "About.xml")):
        pid, targets = own_package_id(about)
        if not pid or pid.lower() not in pos:
            continue                      # not ours, or not active — nothing to assert
        mine = pos[pid.lower()]
        for t in targets:
            tl = t.lower()
            if installed and tl not in installed:
                dead.append("%s -> %s" % (pid, t))
            elif tl in pos and pos[tl] > mine:
                inverted.append("%s @%d must load AFTER %s @%d"
                                % (pid, mine, t, pos[tl]))
    add(FAIL if inverted else OK, "our mods load after their loadAfter targets",
        "; ".join(inverted) if inverted else "all %d ordered correctly" % len(pos))
    add(FAIL if dead else OK, "no loadAfter names a mod that is not installed",
        "; ".join(dead) if dead else "no dead targets")

    # ---- 7. hard rules --------------------------------------------------
    for earlier, later, why in HARD_RULES:
        if earlier in pos and later in pos:
            good = pos[earlier] < pos[later]
            add(OK if good else FAIL, "%s before %s" % (earlier, later),
                "%d < %d" % (pos[earlier], pos[later]) if good else "INVERTED — " + why)
    if "owlchemist.cherrypicker" in pos:
        i = pos["owlchemist.cherrypicker"]
        add(OK if i <= CHERRYPICKER_MAX_INDEX else FAIL,
            "cherrypicker is near the top of the load order",
            "@%d — removals must happen before other mods cache def lists in "
            "their own static constructors" % i)

    # ---- 5. Cherry Picker keys -----------------------------------------
    cp = os.path.join(CONFIG, "Mod_3521312241_Mod_CherryPicker.xml")
    if os.path.isfile(cp):
        try:
            root = ET.parse(cp).getroot()
            keys = [(e.text or "").strip() for e in root.iter("li")]
            import cherrypick_build
            problems = cherrypick_build.check(keys)
            add(FAIL if problems else OK, "every Cherry Picker key is valid",
                "; ".join("%s (%s)" % (k, w) for k, _, w in problems)
                if problems else "%d keys, all resolve and are in scope" % len(keys))
        except Exception as e:
            add(FAIL, "Cherry Picker settings parse", str(e))
    else:
        add(WARN, "Cherry Picker settings file", "absent — nothing is being removed")

    # ---- 6. every mod settings file ------------------------------------
    bad = []
    for f in glob.glob(os.path.join(CONFIG, "Mod_*.xml")):
        try:
            if ET.parse(f).getroot().tag != "SettingsBlock":
                bad.append("%s: root is not <SettingsBlock>" % os.path.basename(f))
        except Exception as e:
            bad.append("%s: %s" % (os.path.basename(f), e))
    add(FAIL if bad else OK, "every Config/Mod_*.xml is well-formed",
        "; ".join(bad) if bad else "%d settings files parse"
        % len(glob.glob(os.path.join(CONFIG, "Mod_*.xml"))))

    return report(quiet)


def report(quiet):
    fails = [r for r in results if r[0] == FAIL]
    for level, check, detail in results:
        if quiet and level == OK:
            continue
        mark = {FAIL: "FAIL", WARN: "warn", OK: " ok "}[level]
        print("  [%s] %-52s %s" % (mark, check, detail))
    print("\n%s — %d check(s), %d failure(s)"
          % ("NOT SAFE TO LOAD" if fails else "SAFE TO LOAD", len(results), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
