#!/usr/bin/env python3
# selftest-tier: deployed
"""T_ONBOARDED_SET (tree check C_onboarded_set): the list of ancient machines equals the production machines found in the
factory mod's own defs (18 with Vanilla Cooking Expanded, 17 without) plus the vanometric power cell and the psychic emanator.
A factory update that adds a machine turns this red.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_onboarded_set.py [--vfef <the factory mod's folder>] [--data <RimWorld Data>]

WHAT IT READS
  the list of ancient machines   the mod's onboarding table: one RimMandrake.WreckedMachines.RM_MachineLineDef for each machine,
                                 in src/RimMandrake/WreckedMachines/Defs/MachineLines/*.xml (its <original> is the donor def). A
                                 line def with MayRequire="VanillaExpanded.VCookE" loads only with that mod.
  the factory mod's machines     every concrete ThingDef in a file named Buildings_Factories*.xml of the installed factory mod
                                 (Steam workshop 3686924415, folder 1.6): its Defs, its Mods/Odyssey folder (every DLC is assumed)
                                 and, with Vanilla Cooking Expanded, its Mods/VanillaCookingExpanded folder. The conveyors, the
                                 hopper, the booster and the heatsink are in other files and are not production machines (rule
                                 R_parts_stay).
  the two base-game machines     VanometricPowerCell and PsychicEmanator, looked up in the installed game's Data/Core/Defs.

ROWS
  factory_has_17_and_18   the factory mod holds 17 production machines without Vanilla Cooking Expanded and 18 with it (the
                          numbers of the check itself; another count means the factory mod changed, and the table must follow)
  set_without_cooking     the lines that load without Vanilla Cooking Expanded name exactly the 17 machines and the two base ones
  set_with_cooking        all the lines name exactly the 18 machines and the two base ones
  one_line_each           no key, original or level def is named by two lines; each line names a key, an original and three levels

Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK (the factory mod or the game's Data is not installed where this looks, or a file
does not parse), which is never a verdict on the mod. The planted faults at the end show each row able to fail.
"""
import argparse
import copy
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
LINES_DIR = os.path.join(HERE, "Defs", "MachineLines")
LINE_TAG = "RimMandrake.WreckedMachines.RM_MachineLineDef"
COOKING = "VanillaExpanded.VCookE"
BASE_GAME = ("VanometricPowerCell", "PsychicEmanator")
STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
VFEF_DEFAULT = os.environ.get("RM_VFEF_DIR") or STEAM + "/workshop/content/294100/3686924415"
DATA_DEFAULT = os.environ.get("RM_RIMWORLD_DATA") or STEAM + "/common/RimWorld/Data"
LEVELS = ("wrecked", "kludged", "refurbished")


class CouldNotLook(Exception):
    pass


def _parse(path):
    try:
        return ET.parse(path).getroot()
    except (OSError, ET.ParseError) as e:
        raise CouldNotLook("%s: %s" % (path, e))


def factory_machines(vfef):
    """-> (machines without Vanilla Cooking Expanded, machines with it), each a sorted list of defNames."""
    base = os.path.join(vfef, "1.6")
    if not os.path.isdir(os.path.join(base, "Defs")):
        raise CouldNotLook("the factory mod is not at %s (no 1.6/Defs); pass --vfef or set RM_VFEF_DIR" % vfef)

    def read(sub):
        out = []
        for f in sorted(glob.glob(os.path.join(base, sub, "**", "Buildings_Factories*.xml"), recursive=True)):
            for d in _parse(f).findall("ThingDef"):
                if d.get("Abstract", "").lower() != "true" and d.findtext("defName"):
                    out.append(d.findtext("defName").strip())
        return out
    main, ody, cook = read("Defs"), read(os.path.join("Mods", "Odyssey")), read(os.path.join("Mods", "VanillaCookingExpanded"))
    if len(main) < 5:
        raise CouldNotLook("only %d machines read from %s/Defs/**/Buildings_Factories*.xml (sanity probe)" % (len(main), base))
    return sorted(main + ody), sorted(main + ody + cook)


def base_game_defs(data):
    found = set()
    core = os.path.join(data, "Core", "Defs")
    if not os.path.isdir(core):
        raise CouldNotLook("the game's Data is not at %s (no Core/Defs); pass --data or set RM_RIMWORLD_DATA" % data)
    for f in glob.glob(os.path.join(core, "**", "*.xml"), recursive=True):
        txt = open(f, encoding="utf-8", errors="replace").read()
        for name in BASE_GAME:
            if "<defName>%s</defName>" % name in txt:
                found.add(name)
    return found


def lines(lines_dir=LINES_DIR):
    """-> [{'key','original','wrecked','kludged','refurbished','requires','file'}], one per line def; [] when there is none."""
    out = []
    for f in sorted(glob.glob(os.path.join(lines_dir, "*.xml"))):
        for d in _parse(f).iter(LINE_TAG):
            row = {k: (d.findtext(k) or "").strip() for k in ("key", "original") + LEVELS}
            row["requires"] = (d.get("MayRequire") or "").strip()
            row["file"] = os.path.basename(f)
            out.append(row)
    return out


def rows_for(table, without, with_cooking):
    """One (row, ok, worst, cases, detail) per rule."""
    rows = []
    rows.append(("factory_has_17_and_18", len(without) == 17 and len(with_cooking) == 18, abs(len(without) - 17) + abs(len(with_cooking) - 18),
                 len(with_cooking), "the factory mod holds %d production machines without Vanilla Cooking Expanded and %d with it"
                 % (len(without), len(with_cooking))))
    for name, want, tab in (("set_without_cooking", without, [r for r in table if r["requires"].lower() != COOKING.lower()]),
                            ("set_with_cooking", with_cooking, table)):
        want = set(want) | set(BASE_GAME)
        got = set(r["original"] for r in tab)
        missing, extra = sorted(want - got), sorted(got - want)
        rows.append((name, not missing and not extra, len(missing) + len(extra), len(want),
                     "%d lines for %d machines%s%s" % (len(tab), len(want),
                                                       "; no line for %s" % ", ".join(missing) if missing else "",
                                                       "; a line for %s, which is not on the list" % ", ".join(extra) if extra else "")))
    bad = []
    for field in ("key", "original") + LEVELS:
        seen = {}
        for r in table:
            if not r[field]:
                bad.append("a line in %s names no %s" % (r["file"], field))
            elif r[field] in seen:
                bad.append("%s %s is named by two lines" % (field, r[field]))
            seen[r[field]] = 1
    rows.append(("one_line_each", bool(table) and not bad, len(bad) if table else 1, len(table),
                 "; ".join(bad[:6]) or ("%d lines" % len(table) if table else "the onboarding table holds no line")))
    return rows


def _planted(table, without, with_cooking, how):
    t, wo, wi = copy.deepcopy(table), list(without), list(with_cooking)
    if how == "line_dropped":
        t = t[1:]
    elif how == "line_for_a_conveyor":
        t.append(dict(t[0], key="conveyor", original="VFEFactory_Conveyor", wrecked="a", kludged="b", refurbished="c"))
    elif how == "key_twice":
        t[1] = dict(t[1], key=t[0]["key"])
    elif how == "cannery_loads_without_cooking":
        for r in t:
            r["requires"] = ""
    elif how == "factory_gains_a_machine":
        wo.append("VFEFactory_AutomatedNewMachine")
        wi.append("VFEFactory_AutomatedNewMachine")
    return t, wo, wi


PLANTS = (("line_dropped", "set_with_cooking"), ("line_for_a_conveyor", "set_with_cooking"), ("key_twice", "one_line_each"),
          ("cannery_loads_without_cooking", "set_without_cooking"), ("factory_gains_a_machine", "factory_has_17_and_18"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vfef", default=VFEF_DEFAULT)
    ap.add_argument("--data", default=DATA_DEFAULT)
    a = ap.parse_args()
    try:
        without, with_cooking = factory_machines(a.vfef)
        base = base_game_defs(a.data)
        if set(BASE_GAME) - base:
            raise CouldNotLook("the game's Data/Core/Defs does not hold %s" % sorted(set(BASE_GAME) - base))
        table = lines()
    except CouldNotLook as e:
        print("T_ONBOARDED_SET: COULD NOT LOOK: %s" % e)
        return 2
    rows = rows_for(table, without, with_cooking)
    for row, ok, worst, cases, detail in rows:
        print("%-22s %-4s worst %d off, limit 0, %d cases: %s" % (row, "PASS" if ok else "FAIL", worst, cases, detail))
    bad = [r[0] for r in rows if not r[1]]
    # planted faults, on a table that is whole (the shipped one when it passes, else a made one, so the rows are shown able to fail
    # before the build is complete)
    whole = table if not bad else [dict(key=m.lower(), original=m, wrecked=m + "_W", kludged=m + "_K", refurbished=m + "_R",
                                        requires=COOKING if m not in without and m not in BASE_GAME else "", file="made")
                                   for m in list(with_cooking) + list(BASE_GAME)]
    w17 = without if len(without) == 17 else with_cooking[:17]
    blind = []
    if [r[0] for r in rows_for(whole, w17, with_cooking) if not r[1]] and not bad:
        blind.append("the whole table does not pass before a fault is planted")
    for how, want in PLANTS:
        t, wo, wi = _planted(whole, w17, with_cooking, how)
        if dict((r[0], r[1]) for r in rows_for(t, wo, wi))[want]:
            blind.append("%s did not turn %s red" % (how, want))
    print("planted faults: %d of %d caught%s" % (len(PLANTS) - len([b for b in blind if "did not turn" in b]), len(PLANTS),
                                                "; " + "; ".join(blind) if blind else ""))
    print("read: %d line defs in %s; the factory mod at %s" % (len(table), os.path.relpath(LINES_DIR, os.path.dirname(HERE)), a.vfef))
    fail = bool(bad or blind)
    print("T_ONBOARDED_SET: %s (%d rows, %d not PASS)" % ("FAIL" if fail else "PASS", len(rows), len(bad)))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
