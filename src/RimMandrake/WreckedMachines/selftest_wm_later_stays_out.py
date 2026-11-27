#!/usr/bin/env python3
"""T_LATER_STAYS_OUT (bars inv_turret_line and inv_wealth_exclusion, both of scope `later`): Design Version 0.1.0 does not
ship either of them half-built. An absence check, read from the mod's shipped files.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_later_stays_out.py

  no_turret_line       no def or patch of the mod names a turret: no <turretGunDef>, no thingClass or Class with Turret in it,
                       no defName, label or line key with "turret" in it (record.json, inv_turret_line, search_scope)
  no_wealth_exclusion  no C# of the mod (comments taken out, tests and tools left out) names WealthWatcher, wealth or the
                       MarketValue stat, and no def of the mod gives a building a MarketValue of zero or less
                       (record.json, inv_wealth_exclusion, search_scope)

The version that builds either one deletes its row here with the bar's move out of `later`.
Exit 0 both PASS; 1 a FAIL; 2 COULD NOT LOOK (the mod's Defs or Source could not be read), never a verdict on the mod. Each row
is shown able to fail on a planted def and a planted patch; a plant that is not found fails the run.
"""
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = ("obj", "bin", "SelfTest", "tests", "art_source")


def _files(root, sub, ext):
    out = []
    for dp, dn, fs in os.walk(os.path.join(root, sub)):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        out += [os.path.join(dp, f) for f in fs if f.endswith(ext)]
    return sorted(out)


def turret_hits(root):
    """-> ([hits], count of xml files read). A file that does not parse raises."""
    hits, n = [], 0
    for sub in ("Defs", "Patches"):
        for p in _files(root, sub, ".xml"):
            n += 1
            rel = os.path.relpath(p, root)
            for el in ET.parse(p).getroot().iter():
                text = (el.text or "").strip()
                cls = el.get("Class") or ""
                if el.tag == "turretGunDef":
                    hits.append("%s: <turretGunDef>%s" % (rel, text))
                if "turret" in cls.lower():
                    hits.append("%s: Class=%s" % (rel, cls))
                if el.tag in ("thingClass", "compClass", "defName", "label", "key", "line") and "turret" in text.lower():
                    hits.append("%s: <%s>%s" % (rel, el.tag, text))
    return hits, n


WEALTH = re.compile(r"WealthWatcher|\bwealth\w*|StatDefOf\s*\.\s*MarketValue\w*|StatWorker_MarketValue\w*|\"MarketValue\w*\"", re.I)


def wealth_hits(root):
    """-> ([hits], count of C# files read, count of defs read)."""
    hits, n, ndefs = [], 0, 0
    for p in _files(root, "Source", ".cs"):
        n += 1
        txt = open(p, encoding="utf-8", errors="replace").read()
        txt = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), txt, flags=re.S)
        for i, line in enumerate(txt.splitlines(), 1):
            m = WEALTH.search(re.sub(r"//.*", "", line))
            if m:
                hits.append("%s:%d: %s" % (os.path.relpath(p, root), i, m.group(0)))
    for sub in ("Defs", "Patches"):
        for p in _files(root, sub, ".xml"):
            for d in ET.parse(p).getroot().iter("ThingDef"):
                ndefs += 1
                mv = d.findtext("statBases/MarketValue")
                try:
                    zero = mv is not None and float(mv) <= 0
                except ValueError:
                    zero = True
                if zero and (d.find("building") is not None or d.find("size") is not None):
                    hits.append("%s: %s MarketValue %s" % (os.path.relpath(p, root), d.findtext("defName"), mv))
    return hits, n, ndefs


def _planted(kind):
    """A small copy of a mod with one planted half-build; -> its folder."""
    d = tempfile.mkdtemp(prefix="wm_later_")
    for sub in ("Defs", "Patches", "Source"):
        os.makedirs(os.path.join(d, sub))
    open(os.path.join(d, "Defs", "Clean.xml"), "w").write(
        "<Defs><ThingDef><defName>RM_WM_Clean</defName><label>clean machine</label><size>(1,1)</size>"
        "<statBases><MarketValue>100</MarketValue></statBases></ThingDef></Defs>")
    open(os.path.join(d, "Source", "Clean.cs"), "w").write("// wealth is only named in this comment\nclass Clean { int value; }\n")
    if kind == "turret_def":
        open(os.path.join(d, "Defs", "T.xml"), "w").write(
            "<Defs><ThingDef><defName>RM_WM_Sentry_Wrecked</defName><label>wrecked sentry</label>"
            "<building><turretGunDef>Gun_MiniTurret</turretGunDef></building></ThingDef></Defs>")
    elif kind == "turret_patch":
        open(os.path.join(d, "Patches", "T.xml"), "w").write(
            '<Patch><Operation Class="PatchOperationAdd"><xpath>Defs</xpath><value><ThingDef><defName>RM_WM_X_Kludged</defName>'
            "<thingClass>Building_TurretGun</thingClass></ThingDef></value></Operation></Patch>")
    elif kind == "wealth_patch":
        open(os.path.join(d, "Source", "W.cs"), "w").write(
            "[HarmonyPatch(typeof(WealthWatcher), \"ForceRecount\")]\nclass W { static void Postfix() { } }\n")
    elif kind == "wealth_stat":
        open(os.path.join(d, "Source", "W.cs"), "w").write("class W { float V(Thing t) { return t.GetStatValue(StatDefOf.MarketValue); } }\n")
    elif kind == "zero_value":
        open(os.path.join(d, "Defs", "Z.xml"), "w").write(
            "<Defs><ThingDef><defName>RM_WM_Relic_Kludged</defName><size>(2,2)</size>"
            "<statBases><MarketValue>0</MarketValue></statBases></ThingDef></Defs>")
    return d


PLANTS = (("turret_def", "turret"), ("turret_patch", "turret"), ("wealth_patch", "wealth"), ("wealth_stat", "wealth"),
          ("zero_value", "wealth"), ("clean", None))


def main():
    try:
        th, nx = turret_hits(HERE)
        wh, ncs, ndefs = wealth_hits(HERE)
    except (OSError, ET.ParseError) as e:
        print("T_LATER_STAYS_OUT: COULD NOT LOOK: %s" % e)
        return 2
    if nx < 3 or ncs < 3 or ndefs < 3:
        print("T_LATER_STAYS_OUT: COULD NOT LOOK: read %d xml files, %d C# files, %d ThingDefs (sanity probe: at least 3 each)"
              % (nx, ncs, ndefs))
        return 2
    print("no_turret_line      %s worst %d hits, limit 0, %d xml files read%s" % ("PASS" if not th else "FAIL", len(th), nx,
                                                                              "".join("\n    " + h for h in th[:8])))
    print("no_wealth_exclusion %s worst %d hits, limit 0, %d C# files and %d ThingDefs read%s"
          % ("PASS" if not wh else "FAIL", len(wh), ncs, ndefs, "".join("\n    " + h for h in wh[:8])))
    blind = []
    for kind, want in PLANTS:
        d = _planted(kind)
        try:
            t, _ = turret_hits(d)
            w, _, _ = wealth_hits(d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        got = "turret" if t else "wealth" if w else None
        if got != want or (t and w):
            blind.append("%s read as %s (turret %d, wealth %d), want %s" % (kind, got, len(t), len(w), want))
    print("planted half-builds: %d of %d read right%s" % (len(PLANTS) - len(blind), len(PLANTS), "; " + "; ".join(blind) if blind else ""))
    fail = bool(th or wh or blind)
    print("T_LATER_STAYS_OUT: %s" % ("FAIL" if fail else "PASS"))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
