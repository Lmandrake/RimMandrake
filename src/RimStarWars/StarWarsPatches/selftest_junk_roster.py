"""selftest_junk_roster.py -- FASCINATING_WORLD_JUNK_1: the junk roster is data, and the game is made to obey it. L0.

Checks, offline, against the base game's own def files (all five DLC):
  * design/Jawa/worldbuilding/junk/junk_roster.json is well formed: every kept or cut def exists in the base game or
    our src/ defs, no def sits in two kinds, no def is both kept and cut, every kind says was / yields / risks;
  * Patches/AncientJunk_RosterCut.xml is exactly what gen_junk_roster_cut.py makes from the roster, inside the
    junkRosterCut Mod Settings gate, and that setting exists in the C# switch and the settings class (default on);
  * every cut xpath matches at least one node in the GenStep it names (a patch that matches nothing logs nothing),
    and no scatter group is left empty after the cut;
  * no player-facing label of a KEPT def says car / truck / tank / jeep / APC (reskin patch labels for the reskinned
    defs, the base game's labels for the rest), and no reskin description does either;
  * junk_spawn_census.py with the reskin and cut patches applied: every def the scatter and the Zeddo's Yard
    template can place is in a kept kind, none is on the cut list;
  * the Fall Line: FallLineArrivals ships noOldJunk = true, sets RUT_FallLine's junkDensityFactor from it, and its
    DLL matches its .srchash; StarWarsPatches' DLL matches its .srchash.
Sanity probes prove the instruments can see: a planted unknown def must be refused, a planted car label caught, a
cut xpath with a typo must match nothing, and the census must see AncientTank before the patches.
"""
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROSTER = os.path.join(REPO, "design", "Jawa", "worldbuilding", "junk", "junk_roster.json")
CUT = os.path.join(HERE, "Patches", "AncientJunk_RosterCut.xml")
RESKIN = os.path.join(HERE, "Patches", "AncientJunk_StarWarsReskin.xml")
CENSUS = os.path.join(HERE, "junk_spawn_census.py")
SW_SRC = os.path.join(HERE, "Source", "StarWarsPatches")
SW_DLL = os.path.join(HERE, "Assemblies", "RimMandrakeStarWarsPatches.dll")
FL = os.path.join(REPO, "src", "RimUtinni", "FallLineArrivals")
FL_SRC = os.path.join(FL, "Source")
FL_DLL = os.path.join(FL, "Assemblies", "RimMandrake.Utinni.FallLineArrivals.dll")
DATA_ROOTS = [os.environ.get("RIMWORLD_DATA") or "",
              "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data",
              "/mnt/d/SteamLibrary/steamapps/common/RimWorld/Data"]
DLC = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]
EARTH = re.compile(r"\b(cars?|trucks?|tanks?|jeeps?|APCs?|chemtrucks?)\b", re.I)
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def data_root():
    for r in DATA_ROOTS:
        if r and os.path.isdir(os.path.join(r, "Core", "Defs")):
            return r
    return None


def load_defs(root):
    """defName -> element, and GenStepDef defName -> element, over every base-game def file."""
    things, steps = {}, {}
    for d in DLC:
        for dp, _, fs in os.walk(os.path.join(root, d, "Defs")):
            for f in fs:
                if not f.endswith(".xml"):
                    continue
                try:
                    r = ET.parse(os.path.join(dp, f)).getroot()
                except ET.ParseError:
                    continue
                for e in r:
                    n = e.findtext("defName")
                    if not n:
                        continue
                    if e.tag == "GenStepDef":
                        steps[n] = e
                    elif e.tag == "ThingDef":
                        things.setdefault(n, e)
    return things, steps


def our_thingdefs():
    names = set()
    for dp, _, fs in os.walk(os.path.join(REPO, "src")):
        if os.sep + "Defs" not in dp and os.sep + "Patches" not in dp:
            continue
        for f in fs:
            if f.endswith(".xml"):
                try:
                    for e in ET.parse(os.path.join(dp, f)).getroot().iter("ThingDef"):
                        n = e.findtext("defName")
                        if n:
                            names.add(n)
                except ET.ParseError:
                    pass
    return names


def validate_roster(r, known):
    errs = []
    seen = {}
    for k in r.get("kinds", []):
        for f in ("id", "was", "yields", "risks", "defs", "regions"):
            if not k.get(f):
                errs.append("kind %s lacks %s" % (k.get("id"), f))
        for d in k.get("defs", []):
            if d in seen:
                errs.append("%s in two kinds (%s, %s)" % (d, seen[d], k["id"]))
            seen[d] = k["id"]
            if d not in known:
                errs.append("kept def %s exists nowhere" % d)
    for c in r.get("cut", []):
        if c["def"] in seen:
            errs.append("%s is both kept (%s) and cut" % (c["def"], seen[c["def"]]))
        if c["def"] not in known:
            errs.append("cut def %s exists nowhere" % c["def"])
        if not c.get("why") or not c.get("from"):
            errs.append("cut %s lacks why/from" % c["def"])
    return errs


def remove_from_step(step, path):
    """Apply one cut xpath shape to a GenStepDef element copy. Returns the number of nodes removed."""
    groups = step.find("genStep/groups")
    if groups is None:
        return 0
    m = re.fullmatch(r"groups/li/things/(\w+)", path)
    if m:
        n = 0
        for li in groups.findall("li"):
            th = li.find("things")
            if th is None:
                continue
            for c in th.findall(m.group(1)):
                th.remove(c)
                n += 1
        return n
    if path == "groups/li[not(things/*)]":
        n = 0
        for li in groups.findall("li"):
            th = li.find("things")
            if th is None or len(th) == 0:
                groups.remove(li)
                n += 1
        return n
    m = re.fullmatch(r"groups/(\w+)", path)
    if m:
        n = 0
        for c in groups.findall(m.group(1)):
            groups.remove(c)
            n += 1
        return n
    raise ValueError("unknown xpath shape " + path)


def cut_ops(patch_root):
    """(step, path, conditional) for every op in the cut patch."""
    out = []
    for li in patch_root.iter("li"):
        cls = li.get("Class")
        if cls not in ("PatchOperationRemove", "PatchOperationConditional"):
            continue
        xp = li.findtext("xpath") or ""
        m = re.fullmatch(r'/Defs/GenStepDef\[defName="(\w+)"\]/genStep/(.+)', xp)
        out.append((m.group(1) if m else None, m.group(2) if m else xp, cls == "PatchOperationConditional"))
    return out


def label_of(reskin_root, things, d):
    for li in reskin_root.iter("li"):
        if li.findtext("xpath") == '/Defs/ThingDef[defName="%s"]/label' % d:
            return li.findtext("value/label")
    e = things.get(d)
    return e.findtext("label") if e is not None else None


def srchash_stale(dll, src):
    stamp = open(dll + ".srchash").read().splitlines()
    dl = [l for l in stamp if l.startswith("# dll:")]
    stale = [] if dl and dl[0].split(":", 1)[1].strip() == sha(dll) else ["dll bytes"]
    for l in stamp:
        if l and not l.startswith("#"):
            h, rel = l.split(" ", 1)
            p = os.path.normpath(os.path.join(src, rel))
            if not os.path.isfile(p) or sha(p) != h:
                stale.append(rel)
    return stale


def main():
    root = data_root()
    check("base game Data is readable", root is not None, DATA_ROOTS)
    if root is None:
        return 1
    things, steps = load_defs(root)
    known = set(things) | our_thingdefs()
    roster = json.load(open(ROSTER, encoding="utf-8"))

    errs = validate_roster(roster, known)
    check("roster well formed (%d kinds, %d kept defs, %d cut defs, %d cut prefabs)" % (
        len(roster["kinds"]), sum(len(k["defs"]) for k in roster["kinds"]), len(roster["cut"]),
        len(roster.get("cut_prefabs", []))), not errs, errs)
    bad = copy.deepcopy(roster)
    bad["kinds"][0]["defs"].append("AncientHoverTruckThatIsNotReal")
    check("probe: a planted unknown def is refused", bool(validate_roster(bad, known)))

    # the patch is the roster's
    spec = importlib.util.spec_from_file_location("gen", os.path.join(HERE, "gen_junk_roster_cut.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    check("AncientJunk_RosterCut.xml == gen_junk_roster_cut.py output",
          open(CUT, encoding="utf-8").read() == gen.build(roster))
    proot = ET.parse(CUT).getroot()
    top = list(proot)
    check("one Operation, the junkRosterCut setting gate",
          len(top) == 1 and top[0].get("Class") == gen.GATE and top[0].findtext("setting") == "junkRosterCut")
    sw = open(os.path.join(SW_SRC, "RSW_PatchOperationStarWarsPatchesSetting.cs")).read()
    st = open(os.path.join(SW_SRC, "RSW_StarWarsPatchesSettings.cs")).read()
    check("junkRosterCut is in the C# switch and the settings (default true)",
          'case "junkRosterCut":' in sw and "DefaultJunkRosterCut = true" in st
          and 'Scribe_Values.Look(ref junkRosterCut, "junkRosterCut"' in st)

    # every cut op hits; no group empties
    patched = {n: copy.deepcopy(e) for n, e in steps.items()}
    misses = []
    for step, path, cond in cut_ops(proot):
        if step not in patched:
            misses.append("no GenStep %s" % step)
            continue
        n = remove_from_step(patched[step], path)
        if n == 0 and not cond:
            misses.append("%s %s matches nothing" % (step, path))
    check("every cut xpath matches in its GenStep", not misses, misses)
    probe = copy.deepcopy(steps["AncientJunkClusters"])
    check("probe: a typo'd cut matches nothing", remove_from_step(probe, "groups/li/things/AncientShopingCart") == 0)
    empties = [n for n, e in patched.items() for li in e.findall("genStep/groups/li")
               if li.find("things") is not None and len(li.find("things")) == 0]
    check("no scatter group left empty", not empties, empties)
    still = []
    for c in roster["cut"]:
        for step in c["from"]:
            if patched[step].find("genStep/groups/li/things/" + c["def"]) is not None:
                still.append((step, c["def"]))
    check("no cut def left in its GenStep after the patch", not still, still)

    # labels: no earth vehicle nouns on any kept def
    rroot = ET.parse(RESKIN).getroot()
    loud = []
    for k in roster["kinds"]:
        for d in k["defs"]:
            lab = label_of(rroot, things, d) or ""
            if EARTH.search(lab):
                loud.append("%s: %s" % (d, lab))
    for li in rroot.iter("li"):
        desc = li.findtext("value/description")
        if desc and EARTH.search(desc):
            loud.append("%s description: %s" % (li.findtext("xpath"), EARTH.findall(desc)))
    check("no car/truck/tank on a kept def's label or a reskin description", not loud, loud)
    check("probe: the noun check sees 'ancient car'", bool(EARTH.search("ancient car")))

    # census: what the scatter and the yard can place, against the roster
    if os.path.isfile(CENSUS):
        env = dict(os.environ, RIMWORLD_DATA=root)
        base = subprocess.run([sys.executable, CENSUS, "--json"], capture_output=True, text=True, env=env,
                              timeout=300)
        try:
            unpatched = json.loads(base.stdout)
        except ValueError:
            unpatched = {}
        check("probe: the census sees AncientTank before any patch", "AncientTank" in unpatched.get("all", []),
              base.stderr[-400:])
        res = subprocess.run([sys.executable, CENSUS, "--apply-patch", CUT,
                              "--roster", ROSTER], capture_output=True, text=True, env=env, timeout=300)
        tail = "\n".join(res.stdout.splitlines()[-12:])
        print(tail)
        check("census with the patches: every spawnable def is kept, none cut (exit 0)", res.returncode == 0, tail)
        # per region: the yard template's defs sit in kinds ruled for the yard; vanilla scatter defs in kinds ruled for
        # the scatter; and the Fall Line prevents every vanilla source the census knows
        kinds_of = {}
        for k in roster["kinds"]:
            for d in k["defs"]:
                kinds_of[d] = k
        yard = unpatched.get("ours:zeddos_yard", [])
        wrong = [d for d in yard if "zeddos_yard" not in kinds_of.get(d, {}).get("regions", [])]
        check("every Zeddo's Yard template def (%d) is in a kind ruled for zeddos_yard" % len(yard), yard and not wrong, wrong)
        vsrc = sorted(k.split(":", 1)[1] for k in unpatched if k.startswith("vanilla:"))
        prevent = ET.parse(os.path.join(FL, "Defs", "GenStepDefs", "RUT_FallLine_NoOldJunk.xml")).getroot()
        listed = sorted(li.text for li in prevent.iter("li"))
        check("RUT_FallLine_NoOldJunk prevents every vanilla junk source the census reads (%d)" % len(vsrc),
              vsrc and set(vsrc) <= set(listed), sorted(set(vsrc) - set(listed)))
        unknown = [n for n in listed if n not in steps]
        check("every prevented step exists in the base game", not unknown, unknown)
    else:
        check("junk_spawn_census.py exists", False, CENSUS)

    # the Fall Line carries no old junk
    fl = open(os.path.join(FL_SRC, "FallLineArrivalsMod.cs")).read()
    check("FallLineArrivals: noOldJunk ships true and sets RUT_FallLine.junkDensityFactor",
          "public static bool noOldJunk = true;" in fl and 'GetNamedSilentFail("RUT_FallLine")' in fl
          and "junkDensityFactor = FallLineArrivalsSettings.noOldJunk ? 0f : 1f" in fl
          and "[StaticConstructorOnStartup]\n    public static class FallLineOldJunk" in fl
          and "FallLineOldJunk.Apply();" in fl and "m.extraGenSteps.Add(prevent)" in fl
          and "m.extraGenSteps.Remove(prevent)" in fl)
    check("noOldJunk is declared before the shippedDefaults snapshot",
          fl.find("public static bool noOldJunk") < fl.find("shippedDefaults = SnapshotDefaults()"))
    for dll, src in ((FL_DLL, FL_SRC), (SW_DLL, SW_SRC)):
        stale = srchash_stale(dll, src)
        check("%s matches its .srchash" % os.path.basename(dll), not stale, stale)

    print("%d junk-roster selftest(s) FAILED" % len(FAILS) if FAILS else "all junk-roster checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
