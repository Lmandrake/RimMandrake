#!/usr/bin/env python3
"""Offline selftest for SHIRREL_DECIDE_GALE_GLIDE: the shirrel's Gale glide as a real 1.6 flyer (owner by card 2026-10-26,
"Shirrel ... How should the Gale glide work? -> Real glide as a flyer").

Rows (each one is checked on the real tree, then broken in memory to prove the row can fail):
  def       RM_Shirrel can fly (MaxFlightTime > 0) but only briefly (<= 4 s), has a FlightCooldown, never starts flying on
            a job by chance (flightStartChanceOnJobStart 0), cannot fly into or out of the map; its comps list the
            CreatureBehaviors home tether BEFORE the glide comp; every glide field the def sets exists on the props class;
            homeTrees name LeaningScrub tree defs; no STUB comment names this item; a flip-book prefix, if ever set, has
            its frames on disk (none today: it flies drawn with its body graphic).
  gate      the CanFlyNow getter is postfixed and the postfix goes through RM_GlideKernel.CanFlyNow; the comp's launch
            raises `launching` only around RM_Flight.TryLaunch, after StartJob, and lowers it in a finally; TryGlide is
            gated on RM_WindCalendar.IsGale and on FeatureOn = RM_WindCalendar.On(shirrelGlideEnabled); off unbinds the
            tether; the proof hook launches nothing (no Launch / StartFlying / TryLaunch / StartJob in it).
  setting   shirrelGlideEnabled defaults true, is saved with default true, sits under the modEnabled master, in the Gale
            group's names and Dependent list, and has a checkbox.
  build     both new .cs files are compiled by the mod csproj; the SelfTest csproj compiles the kernel and its check;
            Program.cs ANDs the check into the exit code.
  walk      the validation walk carries the BENCH state-read row (ProofGlide) and the joint-session-only flight row.

Flight itself is never run here or live without the owner (standing ruling); the live look is a joint session.

    python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub_shirrel_glide.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
THIS_ITEM = "SHIRREL_DECIDE_GALE_GLIDE"

FILES = {
    "fauna": "LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml",
    "glide": "LeaningScrub/Source/RM_ShirrelGlide.cs",
    "kernel": "LeaningScrub/Source/Kernel/RM_GlideKernel.cs",
    "settings": "LeaningScrub/Source/RM_LeaningScrubMod.cs",
    "csproj": "LeaningScrub/Source/RM_LeaningScrub.csproj",
    "stcsproj": "LeaningScrub/Source/SelfTest/RimMandrakeLeaningScrub.SelfTest.csproj",
    "program": "LeaningScrub/Source/SelfTest/Program.cs",
    "walk": "../../design/validation_walks/RimMandrake/LeaningScrub.md",
}

FAILED = []


def expect(label, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", label, detail))
    if not ok:
        FAILED.append(label)


def load():
    return {k: open(os.path.normpath(os.path.join(SRC, rel)), encoding="utf-8").read() for k, rel in FILES.items()}


def defs(text, tag):
    out = {}
    for el in ET.fromstring(text).iter(tag):
        n = el.findtext("defName")
        if n:
            out[n] = el
    return out


def strip_comments(cs):
    cs = re.sub(r"/\*.*?\*/", "", cs, flags=re.S)
    return re.sub(r"//[^\n]*", "", cs)


def method_body(cs, sig_regex):
    m = re.search(sig_regex, cs)
    if not m:
        return None
    i = cs.index("{", m.end() - 1)
    depth = 0
    for j in range(i, len(cs)):
        if cs[j] == "{":
            depth += 1
        elif cs[j] == "}":
            depth -= 1
            if depth == 0:
                return cs[i:j + 1]
    return None


def leaning_tree_defs():
    out = set()
    root = os.path.join(SRC, "LeaningScrub", "Defs")
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".xml"):
                try:
                    for el in ET.parse(os.path.join(dp, fn)).getroot().iter("ThingDef"):
                        if el.findtext("plant/treeCategory") or el.findtext("plant/treeLoversCareIfChopped") is not None \
                                or (el.get("ParentName") or "").startswith("Tree"):
                            if el.findtext("defName"):
                                out.add(el.findtext("defName"))
                except ET.ParseError:
                    pass
    return out


def num(el, path):
    t = el.findtext(path)
    try:
        return float(t) if t is not None else None
    except ValueError:
        return None


def check_def(t):
    errs = []
    things = defs(t["fauna"], "ThingDef")
    s = things.get("RM_Shirrel")
    if s is None:
        return ["no ThingDef RM_Shirrel"]
    mft = num(s, "statBases/MaxFlightTime")
    if mft is None or not (0 < mft <= 4):
        errs.append("MaxFlightTime %r not in (0, 4]: the glide must fly, and briefly" % mft)
    cd = num(s, "statBases/FlightCooldown")
    if cd is None or cd <= 0:
        errs.append("FlightCooldown %r must be > 0" % cd)
    if num(s, "race/flightStartChanceOnJobStart") != 0:
        errs.append("race/flightStartChanceOnJobStart must be 0 (no chance take-offs)")
    for flag in ("canFlyIntoMap", "canLeaveMapFlying"):
        if (s.findtext("race/" + flag) or "false").strip().lower() == "true":
            errs.append("race/%s must not be true (a short hop, never map travel)" % flag)
    comps = [li.get("Class") or "" for li in s.findall("comps/li")]
    ti = [i for i, c in enumerate(comps) if c == "RimMandrake.CreatureBehaviors.RM_CompProperties_HomeTether"]
    gi = [i for i, c in enumerate(comps) if c == "RimMandrake.LeaningScrub.RM_CompProperties_ShirrelGlide"]
    if not ti or not gi:
        errs.append("comps must carry both the home tether and the shirrel glide: %s" % comps)
    elif gi[0] < ti[0]:
        errs.append("the glide comp must be listed after the home tether")
    props = re.search(r"class RM_CompProperties_ShirrelGlide\b.*?\{(.*?)public RM_CompProperties_ShirrelGlide\(\)",
                      t["glide"], re.S)
    fields = set(re.findall(r"public\s+[\w<>]+\s+(\w+)\s*=", props.group(1))) if props else set()
    if not fields:
        errs.append("RM_CompProperties_ShirrelGlide fields not found in source")
    trees = leaning_tree_defs()
    for li in s.findall("comps/li"):
        if (li.get("Class") or "").endswith("RM_CompProperties_ShirrelGlide"):
            for child in li:
                if child.tag not in fields:
                    errs.append("def sets <%s>, not a field of RM_CompProperties_ShirrelGlide" % child.tag)
            homes = [x.text for x in li.findall("homeTrees/li")]
            if not homes:
                errs.append("homeTrees empty")
            for h in homes:
                if h not in trees:
                    errs.append("home tree %r is not a LeaningScrub tree def" % h)
    for m in re.finditer(r"<!--(.*?)-->", t["fauna"], re.S):
        if "STUB" in m.group(1) and THIS_ITEM in m.group(1):
            errs.append("a STUB comment still names %s" % THIS_ITEM)
    kind = defs(t["fauna"], "PawnKindDef").get("RM_Shirrel")
    if kind is None:
        errs.append("no PawnKindDef RM_Shirrel")
    else:
        for p in kind.iter("flyingAnimationFramePathPrefix"):
            d = os.path.join(SRC, "LeaningScrub", "Textures", os.path.dirname(p.text or ""))
            base = os.path.basename(p.text or "")
            if not (os.path.isdir(d) and any(f.startswith(base) for f in os.listdir(d))):
                errs.append("flip-book prefix %r has no frames on disk" % p.text)
    return errs


def check_gate(t):
    errs = []
    cs = strip_comments(t["glide"])
    if not re.search(r"PropertyGetter\(\s*typeof\(Pawn_FlightTracker\)\s*,\s*nameof\(Pawn_FlightTracker\.CanFlyNow\)\s*\)", cs):
        errs.append("CanFlyNow getter is not the patch target")
    post = method_body(cs, r"static void CanFlyNow_Postfix\([^)]*\)")
    if not post or "RM_GlideKernel.CanFlyNow(" not in post or "ref bool __result" not in cs:
        errs.append("CanFlyNow postfix does not route through RM_GlideKernel.CanFlyNow")
    if "postfix: new HarmonyMethod(typeof(RM_ShirrelGlidePatches), nameof(CanFlyNow_Postfix))" not in cs:
        errs.append("postfix not registered")
    k = strip_comments(t["kernel"])
    body = method_body(k, r"static bool CanFlyNow\([^)]*\)")
    if not body or "isGlider ? vanilla && launching : vanilla" not in body:
        errs.append("kernel gate is not `isGlider ? vanilla && launching : vanilla`")
    launch = method_body(cs, r"public bool Launch\(Pawn pawn, Vector2 downwind\)")
    if not launch:
        errs.append("Launch not found")
    else:
        a, b = launch.find("StartJob("), launch.find("RM_Flight.TryLaunch(")
        if a < 0 or b < 0 or a > b:
            errs.append("RM_Flight.TryLaunch must come after StartJob")
        if not re.search(r"launching = true;\s*try \{ RM_Flight\.TryLaunch\(pawn\); \}\s*finally \{ launching = false; \}", launch):
            errs.append("launching is not raised only around TryLaunch with a finally reset")
    tg = method_body(cs, r"private void TryGlide\(int interval\)")
    if not tg or "RM_WindCalendar.IsGale(map)" not in tg or "if (!FeatureOn || !gale || lean == null) return;" not in tg:
        errs.append("TryGlide is not gated on FeatureOn, the Gale and a known wind")
    if "FeatureOn => RM_WindCalendar.On(RM_LeaningScrubSettings.shirrelGlideEnabled)" not in cs:
        errs.append("FeatureOn does not read RM_WindCalendar.On(shirrelGlideEnabled)")
    bind = method_body(cs, r"private void Bind\(\)")
    if not bind or "tether?.SetHome(IntVec3.Invalid)" not in bind:
        errs.append("feature off does not clear the tether home")
    proof = method_body(cs, r"public static string ProofGlide\(string unused\)")
    if not proof:
        errs.append("ProofGlide not found")
    else:
        for bad in ("Launch(", "StartFlying(", "TryLaunch(", "StartJob(", "ForceLand("):
            if bad in proof:
                errs.append("ProofGlide calls %s: the proof must be a state read" % bad)
    return errs


def check_setting(t):
    errs = []
    s = strip_comments(t["settings"])
    if "public static bool shirrelGlideEnabled = true;" not in s:
        errs.append("field shirrelGlideEnabled = true missing")
    if 'Scribe_Values.Look(ref shirrelGlideEnabled, "shirrelGlideEnabled", true, true);' not in s:
        errs.append("shirrelGlideEnabled not saved with default true")
    m = re.search(r'\.Declare\("modEnabled",([^)]*)\)', s)
    if not m or '"shirrelGlideEnabled"' not in m.group(1):
        errs.append("shirrelGlideEnabled not under the modEnabled master")
    g = re.search(r'Group\(list, "The Stall and the Gale",[^\n]*', s)
    if not g or '"shirrelGlideEnabled"' not in g.group(0):
        errs.append("shirrelGlideEnabled not in the Gale group names")
    d = re.search(r'Dependent\(list, "stallFreezeEnabled",[^\n]*', s)
    if not d or '"shirrelGlideEnabled"' not in d.group(0):
        errs.append("shirrelGlideEnabled not in the Gale group's Dependent list")
    if "ref shirrelGlideEnabled," not in s or 'CheckboxLabeled("Shirrel: glides on the Gale"' not in s:
        errs.append("no checkbox for shirrelGlideEnabled")
    return errs


def check_build(t):
    errs = []
    for inc in ('<Compile Include="Kernel\\RM_GlideKernel.cs" />', '<Compile Include="RM_ShirrelGlide.cs" />'):
        if inc not in t["csproj"]:
            errs.append("mod csproj misses %s" % inc)
    for inc in ('<Compile Include="..\\Kernel\\RM_GlideKernel.cs" />', '<Compile Include="LeaningScrubGlideCheck.cs" />'):
        if inc not in t["stcsproj"]:
            errs.append("SelfTest csproj misses %s" % inc)
    p = strip_comments(t["program"])
    if "bool glide = LeaningScrubGlideCheck.Run();" not in p or not re.search(r"&& glide \? 0 : 1", p):
        errs.append("Program.cs does not AND the glide check into the exit code")
    return errs


def check_walk(t):
    errs = []
    w = t["walk"]
    if "RM_ShirrelGlideProof" not in w or "`ProofGlide`" not in w or "STATE READ ONLY" not in w:
        errs.append("walk has no BENCH ProofGlide state-read row")
    if "JOINT SESSION ONLY" not in w or "never live-tested without the owner" not in w:
        errs.append("walk has no joint-session-only flight row")
    return errs


ROWS = [("def", check_def), ("gate", check_gate), ("setting", check_setting), ("build", check_build), ("walk", check_walk)]

BREAKS = [
    ("def", "fauna", "<MaxFlightTime>3</MaxFlightTime>", "<MaxFlightTime>0</MaxFlightTime>"),
    ("def", "fauna", "<MaxFlightTime>3</MaxFlightTime>", "<MaxFlightTime>20</MaxFlightTime>"),
    ("def", "fauna", "<FlightCooldown>30</FlightCooldown>", ""),
    ("def", "fauna", "<flightStartChanceOnJobStart>0</flightStartChanceOnJobStart>", "<flightStartChanceOnJobStart>0.1</flightStartChanceOnJobStart>"),
    ("def", "fauna", "<flightSpeedFactor>1.5</flightSpeedFactor>", "<flightSpeedFactor>1.5</flightSpeedFactor><canFlyIntoMap>true</canFlyIntoMap>"),
    ("def", "fauna", '<li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_HomeTether">\n        <tetherRadius>10</tetherRadius>',
     '<li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_Nothing">\n        <tetherRadius>10</tetherRadius>'),
    ("def", "fauna", "<homeTrees><li>RM_SweetlineTree</li></homeTrees>", "<homeTrees><li>RM_SweetlineTrea</li></homeTrees>"),
    ("def", "fauna", "<hopMin>10</hopMin>", "<hopMinimum>10</hopMinimum>"),
    ("def", "fauna", "<!-- SHIRREL_DECIDE_GALE_GLIDE (owner", "<!-- STUB SHIRREL_DECIDE_GALE_GLIDE (owner"),
    ("gate", "glide", "nameof(Pawn_FlightTracker.CanFlyNow)", "nameof(Pawn_FlightTracker.CanEverFly)"),
    ("gate", "kernel", "isGlider ? vanilla && launching : vanilla", "vanilla"),
    ("gate", "glide", "launching = true;\n            try { RM_Flight.TryLaunch(pawn); }", "launching = true;\n            RM_Flight.TryLaunch(pawn); try { }"),
    ("gate", "glide", "if (!FeatureOn || !gale || lean == null) return;", "if (!FeatureOn || lean == null) return;"),
    ("gate", "glide", "tether?.SetHome(IntVec3.Invalid);", "tether?.SetHome(parent.Position);"),
    ("gate", "glide", 'if (map == null) return "UNMEASURED no map";', 'if (map == null) return "UNMEASURED no map"; RM_Flight.TryLaunch(null);'),
    ("setting", "settings", "public static bool shirrelGlideEnabled = true;", "public static bool shirrelGlideEnabled = false;"),
    ("setting", "settings", '"galeDustOverlayEnabled", "shirrelGlideEnabled", "drippingRegrowEnabled"', '"galeDustOverlayEnabled", "drippingRegrowEnabled"'),
    ("setting", "settings", 'list.CheckboxLabeled("Shirrel: glides on the Gale"', 'list.Label("Shirrel: glides on the Gale"'),
    ("build", "csproj", '<Compile Include="RM_ShirrelGlide.cs" />', ""),
    ("build", "stcsproj", '<Compile Include="LeaningScrubGlideCheck.cs" />', ""),
    ("build", "program", "&& glide ? 0 : 1", "? 0 : 1"),
    ("walk", "walk", "JOINT SESSION ONLY", "LIVE"),
]


def main():
    tree = load()
    for name, fn in ROWS:
        errs = fn(tree)
        expect("real tree: " + name, not errs, "; ".join(errs))
    for row, key, old, new in BREAKS:
        if old not in tree[key]:
            expect("planted break %s/%s applies" % (row, key), False, "anchor %r not in %s" % (old, FILES[key]))
            continue
        broken = dict(tree)
        broken[key] = tree[key].replace(old, new, 1)
        try:
            errs = dict(ROWS)[row](broken)
        except ET.ParseError as e:
            errs = ["parse error %s" % e]
        expect("planted break caught: %s (%s -> %s)" % (row, old.strip()[:40], new.strip()[:30]), bool(errs))
    if FAILED:
        print("FAILED %d: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("PASS selftest_leaningscrub_shirrel_glide (%d rows, %d planted breaks)" % (len(ROWS), len(BREAKS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
