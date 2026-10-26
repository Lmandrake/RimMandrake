#!/usr/bin/env python3
"""Offline selftest for LEANINGSCRUBFAUNA_BUILD_STUBBED_BEHAVIOURS: the fauna behaviours that are built by data and
small hooks, plus the stub comments that must point at owning items.

Rows (each one is checked on the real tree, then broken in memory to prove the row can fail):
  thornhold  the thornhold's "quill lash" tool resolves capacity -> ManeuverDef -> DamageDef -> RM_VenomvineVenom,
             and that hediff exists in EnvironmentalHazards (a hard dependency).
  surrik     the surrik carries CreatureBehaviors' RM_SandSwimExtension; its swim terrains are exactly the biome's
             terrainsByFertility; its submerged hediff is ours and hides it from the player (Invisibility,
             visibleToPlayer false); its marker, take filth and the runway bloom's Surface response resolve.
  hooks      RM_CompSandSwim.ForceSurface is public and gated on sandSwimEnabled; the runway bloom's Surface branch
             calls it; the ripple skips crust-swimmers only while the kit is on.
  ribbonwhip "moving when the wind moves" = the ripple: body size within rippleMaxBodySize's default, a wild animal,
             bloom response Sway. (The kernel's wind/Stall behaviour is pinned by SelfTest/LeaningScrubTonightCheck.cs.)
  thornholdden  THORNHOLD_DECIDE_DEN_AND_STAND (owner card "Stand its ground"): HomeTether then RM_CompVineDen on the
             thornhold, every den plant a real venomvine ThingDef, standState a ScopedAggression MentalStateDef,
             ContactVenomImmunity; the comp's damage hook starts the stand only for a wild, in-den, not-already-mental
             pawn hit by external violence from a living pawn, naming the attacker and anchoring on the den; both
             settings default on.
  rollbug    ROLLBUG_DECIDE_CARRION_BALL (owner card "Any corpse in reach"): HomeTether and RM_CompCarrionLarder on the
             rollbug; JobDef/ThinkTree splice resolve to the C# classes; colony corpses are taken by default
             (rollbugTakesColonyCorpses = true, his choice); the one Destroy of a ball is preceded by Strip (gear is
             never eaten); the drop toil strips; an interrupted job drops the carried corpse.
  stubs      no STUB comment in RM_LeaningScrubFauna.xml names a closed item, and every one names an item id.

Live behaviour (surfacing in game, the ripple ignoring a submerged surrik) is NEXT for BENCH in the validation walk.

    python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub_fauna_behaviours.py
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
THIS_ITEM = "LEANINGSCRUBFAUNA_BUILD_STUBBED_BEHAVIOURS"
# Items closed by building them; a STUB naming one is stale.
CLOSED = (THIS_ITEM, "SHIRREL_DECIDE_GALE_GLIDE", "THORNHOLD_DECIDE_DEN_AND_STAND", "ROLLBUG_DECIDE_CARRION_BALL")

FILES = {
    "fauna": "LeaningScrub/Defs/ThingDefs_Races/RM_LeaningScrubFauna.xml",
    "damage": "LeaningScrub/Defs/DamageDefs/RM_LeaningScrub_FaunaDamage.xml",
    "surrikhediff": "LeaningScrub/Defs/HediffDefs/RM_LeaningScrub_Surrik.xml",
    "exithole": "LeaningScrub/Defs/ThingDefs_Misc/RM_SurrikExitHole.xml",
    "venom": "EnvironmentalHazards/Defs/HediffDefs/RM_Hediffs_ContactVenom.xml",
    "swimhediffs": "CreatureBehaviors/Defs/HediffDefs/RM_SandSwim_Hediffs.xml",
    "biome": None,  # found below
    "comp": "CreatureBehaviors/Source/RM_CompSandSwim.cs",
    "bloom": "LeaningScrub/Source/RM_RunwayBloom.cs",
    "ripple": "LeaningScrub/Source/RM_Ripple.cs",
    "settings": "LeaningScrub/Source/RM_LeaningScrubMod.cs",
    "dens": "LeaningScrub/Source/RM_ScrubDens.cs",
    "densdefs": "LeaningScrub/Defs/JobDefs/RM_ScrubDens.xml",
}

# Every ThingDef defName in these plant folders is a candidate den plant.
PLANT_DIRS = ("EnvironmentalHazards/Defs/ThingDefs_Plants", "LeaningScrub/Defs/ThingDefs_Plants")

FAILED = []


def expect(label, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", label, detail))
    if not ok:
        FAILED.append(label)


def find_biome():
    d = os.path.join(SRC, "LeaningScrub/Defs/BiomeDefs")
    for f in sorted(os.listdir(d)):
        if f.endswith(".xml"):
            t = open(os.path.join(d, f), encoding="utf-8").read()
            if "<terrainsByFertility>" in t:
                return os.path.relpath(os.path.join(d, f), SRC)
    return None


def load():
    FILES["biome"] = find_biome()
    tree = {}
    for k, rel in FILES.items():
        if rel is None:
            raise SystemExit("FAIL no LeaningScrub biome with terrainsByFertility found")
        tree[k] = open(os.path.join(SRC, rel), encoding="utf-8").read()
    names = []
    for d in PLANT_DIRS:
        for f in sorted(os.listdir(os.path.join(SRC, d))):
            if f.endswith(".xml"):
                names += list(defs(open(os.path.join(SRC, d, f), encoding="utf-8").read(), "ThingDef"))
    tree["plants"] = "\n".join(names) + "\n"
    return tree


def defs(text, tag):
    """defName -> element for every <tag> in the file (abstract parents with Name only are skipped)."""
    out = {}
    for el in ET.fromstring(text).iter(tag):
        n = el.findtext("defName")
        if n:
            out[n] = el
    return out


def check_thornhold(t):
    errs = []
    races = defs(t["fauna"], "ThingDef")
    th = races.get("RM_Thornhold")
    if th is None:
        return ["no RM_Thornhold ThingDef"]
    caps = []
    for tool in th.iter("li"):
        if (tool.findtext("label") or "").strip() == "quill lash":
            caps = [c.text.strip() for c in tool.findall("capacities/li")]
    if caps != ["RM_ThornholdQuillLash"]:
        errs.append("quill lash capacities %r, want ['RM_ThornholdQuillLash']" % caps)
    caps_defs = defs(t["damage"], "ToolCapacityDef")
    if "RM_ThornholdQuillLash" not in caps_defs:
        errs.append("ToolCapacityDef RM_ThornholdQuillLash missing")
    man = [m for m in defs(t["damage"], "ManeuverDef").values() if m.findtext("requiredCapacity") == "RM_ThornholdQuillLash"]
    if len(man) != 1:
        errs.append("want one ManeuverDef requiring RM_ThornholdQuillLash, found %d" % len(man))
        return errs
    dmg_name = man[0].findtext("verb/meleeDamageDef")
    dmg = defs(t["damage"], "DamageDef").get(dmg_name)
    if dmg is None:
        errs.append("maneuver damage %r is not a DamageDef in the file" % dmg_name)
        return errs
    hed = [li.findtext("hediff") for li in dmg.findall("additionalHediffs/li")]
    if hed != ["RM_VenomvineVenom"]:
        errs.append("quill additionalHediffs %r, want ['RM_VenomvineVenom']" % hed)
    try:
        sev = float(dmg.findtext("additionalHediffs/li/severityPerDamageDealt") or "0")
    except ValueError:
        sev = 0.0
    if not 0 < sev <= 0.04:
        errs.append("quill venom per damage %r outside (0, 0.04] (the thorn's own rate is the ceiling)" % sev)
    if "RM_VenomvineVenom" not in defs(t["venom"], "HediffDef"):
        errs.append("RM_VenomvineVenom not defined in EnvironmentalHazards")
    return errs


def biome_terrains(t):
    root = ET.fromstring(t["biome"])
    for b in root.iter("BiomeDef"):
        tf = b.find("terrainsByFertility")
        if tf is not None:
            return sorted(li.findtext("terrain") for li in tf.findall("li"))
    return []


def check_surrik(t):
    errs = []
    sr = defs(t["fauna"], "ThingDef").get("RM_Surrik")
    if sr is None:
        return ["no RM_Surrik ThingDef"]
    ext = None
    bloom = None
    for li in sr.findall("modExtensions/li"):
        cls = li.get("Class", "")
        if cls.endswith(".RM_SandSwimExtension"):
            ext = li
        if cls.endswith(".RM_RunwayBloomExtension"):
            bloom = li
    if ext is None:
        return ["RM_Surrik has no RM_SandSwimExtension"]
    if ext.get("Class") != "RimMandrake.CreatureBehaviors.RM_SandSwimExtension":
        errs.append("extension class %r is not the CreatureBehaviors one" % ext.get("Class"))
    terr = sorted(li.text.strip() for li in ext.findall("swimTerrains/li"))
    want = biome_terrains(t)
    if not want or terr != want:
        errs.append("swimTerrains %r, want the biome's terrainsByFertility %r" % (terr, want))
    sub = ext.findtext("submergedHediff")
    h = defs(t["surrikhediff"], "HediffDef").get(sub)
    if h is None:
        errs.append("submergedHediff %r is not defined in RM_LeaningScrub_Surrik.xml" % sub)
    else:
        inv = [c for c in h.findall("comps/li") if c.get("Class") == "HediffCompProperties_Invisibility"]
        if len(inv) != 1 or (inv[0].findtext("visibleToPlayer") or "").strip() != "false":
            errs.append("%s must carry one HediffCompProperties_Invisibility with visibleToPlayer false" % sub)
    if ext.findtext("swimmerMarkerHediff") not in defs(t["swimhediffs"], "HediffDef"):
        errs.append("swimmerMarkerHediff %r not a CreatureBehaviors sand-swim hediff" % ext.findtext("swimmerMarkerHediff"))
    if ext.findtext("takeFilth") not in defs(t["exithole"], "ThingDef"):
        errs.append("takeFilth %r not defined" % ext.findtext("takeFilth"))
    if bloom is None or bloom.findtext("response") != "Surface":
        errs.append("RM_Surrik's runway bloom response must be Surface (the bloom drives it up)")
    return errs


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


def check_hooks(t):
    errs = []
    comp = strip_comments(t["comp"])
    body = method_body(comp, r"public\s+void\s+ForceSurface\s*\(\s*\)")
    if body is None:
        errs.append("RM_CompSandSwim has no public void ForceSurface()")
    else:
        if "sandSwimEnabled" not in body:
            errs.append("ForceSurface is not gated on sandSwimEnabled")
        if "Surface(pawn, breach: true)" not in body:
            errs.append("ForceSurface does not breach a submerged swimmer")
        if "surfacedUntilTick" not in body:
            errs.append("ForceSurface does not hold an already-surfaced swimmer up")
    bloom = strip_comments(t["bloom"])
    m = re.search(r"if\s*\(\s*ext\.response\s*==\s*RM_RunwayBloomResponse\.Surface\s*\)", bloom)
    seg = method_body(bloom[m.start():], r"if\s*\(") if m else None
    if seg is None or "ForceSurface()" not in seg:
        errs.append("runway bloom Surface branch does not call RM_CompSandSwim.ForceSurface()")
    rip = strip_comments(t["ripple"])
    should = method_body(rip, r"private\s+bool\s+ShouldHide\s*\(\s*Pawn\s+p\s*,\s*bool\s+on\s*,\s*bool\s+gale")
    if should is None or "IsCrustSwimmer(p.def)" not in should:
        errs.append("ripple ShouldHide does not skip crust-swimmers")
    crust = method_body(rip, r"public\s+static\s+bool\s+IsCrustSwimmer\s*\(")
    if crust is None or "sandSwimEnabled" not in crust or "RM_SandSwimExtension" not in crust:
        errs.append("IsCrustSwimmer must test RM_SandSwimExtension and be gated on sandSwimEnabled")
    return errs


def ripple_default(t):
    m = re.search(r"public\s+static\s+float\s+rippleMaxBodySize\s*=\s*([0-9.]+)f", t["settings"])
    return float(m.group(1)) if m else None


def check_ribbonwhip(t):
    errs = []
    rw = defs(t["fauna"], "ThingDef").get("RM_Ribbonwhip")
    if rw is None:
        return ["no RM_Ribbonwhip ThingDef"]
    limit = ripple_default(t)
    try:
        size = float(rw.findtext("race/baseBodySize") or "nan")
    except ValueError:
        size = float("nan")
    if limit is None or not size <= limit:
        errs.append("ribbonwhip body size %r not within rippleMaxBodySize default %r: the ripple would not hide it" % (size, limit))
    if (rw.findtext("race/intelligence") or "Animal").strip() != "Animal":
        errs.append("ribbonwhip is not an Animal (the ripple hides wild animals only)")
    resp = [li.findtext("response") for li in rw.findall("modExtensions/li")
            if li.get("Class", "").endswith(".RM_RunwayBloomExtension")]
    if resp != ["Sway"]:
        errs.append("ribbonwhip runway bloom response %r, want ['Sway']" % resp)
    return errs


TETHER = "RimMandrake.CreatureBehaviors.RM_CompProperties_HomeTether"


def comp_classes(el):
    return [li.get("Class", "") for li in el.findall("comps/li")]


def check_settings(t, names):
    errs = []
    st = t["settings"]
    for n in names:
        m = re.search(r"public\s+static\s+bool\s+%s\s*=\s*(true|false)\s*;" % n, st)
        if not m or m.group(1) != "true":
            errs.append("setting %s does not default to true (the owner's choice)" % n)
        if not re.search(r'Scribe_Values\.Look\(ref\s+%s\s*,\s*"%s"\s*,\s*true' % (n, n), st):
            errs.append("setting %s is not saved with default true" % n)
        if not re.search(r'\.Declare\([^)]*"%s"' % n, st):
            errs.append("setting %s is not declared to the settings kit" % n)
    return errs


def check_thornholdden(t):
    errs = []
    th = defs(t["fauna"], "ThingDef").get("RM_Thornhold")
    if th is None:
        return ["no RM_Thornhold ThingDef"]
    cls = comp_classes(th)
    den = "RimMandrake.LeaningScrub.RM_CompProperties_VineDen"
    if TETHER not in cls or den not in cls or cls.index(TETHER) > cls.index(den):
        errs.append("thornhold comps %r: want HomeTether before RM_CompProperties_VineDen (the den sets the tether's home)" % cls)
    li = [c for c in th.findall("comps/li") if c.get("Class") == den]
    plants = set(t["plants"].split())
    if len(plants) < 5:
        errs.append("probe: only %d plant ThingDefs seen in %s" % (len(plants), PLANT_DIRS))
    if li:
        dp = [x.text.strip() for x in li[0].findall("denPlants/li")]
        if not dp:
            errs.append("RM_CompProperties_VineDen has no denPlants")
        bad = [x for x in dp if x not in plants or "Venomvine" not in x]
        if bad:
            errs.append("den plants %r are not venomvine plant ThingDefs" % bad)
        st = li[0].findtext("standState")
        ms = defs(t["densdefs"], "MentalStateDef").get(st)
        if ms is None or ms.findtext("stateClass") != "RimMandrake.CreatureBehaviors.RM_MentalState_ScopedAggression":
            errs.append("standState %r is not a ScopedAggression MentalStateDef in RM_ScrubDens.xml" % st)
    if "RimMandrake.EnvironmentalHazards.ContactVenomImmunity" not in [x.get("Class") for x in th.findall("modExtensions/li")]:
        errs.append("thornhold lacks ContactVenomImmunity (its own den would poison it)")
    cs = strip_comments(t["dens"])
    hook = method_body(cs, r"public\s+override\s+void\s+PostPostApplyDamage\s*\(")
    if hook is None or "WhyNotStand(dinfo.Instigator, dinfo.Def)" not in hook or "StartStand(" not in hook:
        errs.append("PostPostApplyDamage does not gate on WhyNotStand(instigator, def) then StartStand")
    why = method_body(cs, r"public\s+string\s+WhyNotStand\s*\(")
    for need in ("StandOn", "Faction != null", "InMentalState", "standRadius", "ExternalViolenceFor(pawn)", "attacker.Dead"):
        if why is None or need not in why:
            errs.append("WhyNotStand lacks %r" % need)
    start = method_body(cs, r"public\s+bool\s+StartStand\s*\(")
    for need in ("otherPawn: attacker", "stand.anchorCell = den", "stand.disengageRadius"):
        if start is None or need not in start:
            errs.append("StartStand lacks %r" % need)
    errs += check_settings(t, ("thornholdDenEnabled", "thornholdStandEnabled"))
    return errs


def check_rollbug(t):
    errs = []
    rb = defs(t["fauna"], "ThingDef").get("RM_Rollbug")
    if rb is None:
        return ["no RM_Rollbug ThingDef"]
    cls = comp_classes(rb)
    if TETHER not in cls or "RimMandrake.LeaningScrub.RM_CompProperties_CarrionLarder" not in cls:
        errs.append("rollbug comps %r: want HomeTether and RM_CompProperties_CarrionLarder (the larder is the tether home)" % cls)
    cs = strip_comments(t["dens"])
    jd = defs(t["densdefs"], "JobDef").get("RM_RollCarrion")
    drv = (jd.findtext("driverClass") or "") if jd is not None else ""
    if not drv.startswith("RimMandrake.LeaningScrub.") or not re.search(r"class\s+%s\s*:\s*JobDriver\b" % re.escape(drv.split(".")[-1]), cs):
        errs.append("JobDef RM_RollCarrion driver %r is not a JobDriver in RM_ScrubDens.cs" % drv)
    if "public static JobDef RM_RollCarrion;" not in cs:
        errs.append("RM_RollCarrion missing from the [DefOf] class")
    tt = defs(t["densdefs"], "ThinkTreeDef").get("RM_RollCarrion_Splice")
    giver = [li.get("Class") for li in tt.iter("li")] if tt is not None else []
    if tt is None or tt.findtext("insertTag") != "Animal_PreWander" or "RimMandrake.LeaningScrub.RM_JobGiver_RollCarrion" not in giver:
        errs.append("ThinkTree splice must insert RM_JobGiver_RollCarrion at Animal_PreWander")
    if not re.search(r"class\s+RM_JobGiver_RollCarrion\s*:\s*ThinkNode_JobGiver\b", cs):
        errs.append("RM_JobGiver_RollCarrion is not a ThinkNode_JobGiver")
    bite = method_body(cs, r"public\s+static\s+string\s+Bite\s*\(")
    if bite is None or "ball.Destroy()" not in bite or "ball.Strip(" not in bite or bite.index("ball.Strip(") > bite.index("ball.Destroy()"):
        errs.append("Bite must Strip the ball before any Destroy (Corpse.Destroy eats gear)")
    elif "HediffDefOf.MissingBodyPart" not in bite or "GetBestBodyPartToEat" not in bite or "corePart" not in bite:
        errs.append("Bite is not the vanilla part-by-part shape (GetBestBodyPartToEat, MissingBodyPart, core part ends it)")
    if cs.count(".Destroy(") != 1:
        errs.append("RM_ScrubDens.cs has %d Destroy calls; only Bite's may destroy a ball" % cs.count(".Destroy("))
    i = cs.find("class RM_JobDriver_RollCarrion")
    toils = method_body(cs[i:], r"MakeNewToils\s*\(\s*\)") if i >= 0 else None
    if toils is None or "AddFinishAction" not in toils or "TryDropCarriedThing(pawn.Position," not in toils:
        errs.append("RollCarrion driver has no finish action dropping the carried corpse (ExitMap would destroy it)")
    elif "ball.Strip(false)" not in toils:
        errs.append("RollCarrion drop toil does not strip the ball at the larder")
    why = method_body(cs, r"public\s+string\s+WhyNotRoll\s*\(")
    if why is None or "rollbugTakesColonyCorpses" not in why or "Faction != null" not in why:
        errs.append("WhyNotRoll must be wild-only and honour rollbugTakesColonyCorpses")
    errs += check_settings(t, ("rollbugCarrionEnabled", "rollbugTakesColonyCorpses"))
    return errs


STUB = re.compile(r"STUB:([^>]*?)-->", re.S)
ITEM = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")


def check_stubs(t):
    errs = []
    stubs = STUB.findall(t["fauna"])
    # five at birth; SHIRREL_DECIDE_GALE_GLIDE, THORNHOLD_DECIDE_DEN_AND_STAND and
    # ROLLBUG_DECIDE_CARRION_BALL closed three (2026-10-26); SCRUBAMBUSHERS owns the rest.
    if len(stubs) < 3:
        errs.append("probe: only %d STUB comments seen (expected the three SCRUBAMBUSHERS ones still owed)" % len(stubs))
    for s in stubs:
        ids = ITEM.findall(s)
        closed = [i for i in ids if i in CLOSED]
        if closed:
            errs.append("a STUB still names closed %s: %s" % (closed[0], " ".join(s.split())[:90]))
        elif not ids:
            errs.append("a STUB names no owning item: %s" % " ".join(s.split())[:90])
    return errs


ROWS = [("thornhold", check_thornhold), ("surrik", check_surrik), ("hooks", check_hooks),
        ("ribbonwhip", check_ribbonwhip), ("thornholdden", check_thornholdden), ("rollbug", check_rollbug),
        ("stubs", check_stubs)]

# One planted break per row: (row, file key, old, new). Each must turn its row red.
BREAKS = [
    ("thornhold", "damage", "<hediff>RM_VenomvineVenom</hediff>", "<hediff>ToxicBuildup</hediff>"),
    ("thornhold", "fauna", "<li>RM_ThornholdQuillLash</li>", "<li>Scratch</li>"),
    ("surrik", "fauna", "<submergedHediff>RM_SurrikInCrust</submergedHediff>", "<submergedHediff>RM_SandSubmerged</submergedHediff>"),
    ("surrik", "surrikhediff", "<visibleToPlayer>false</visibleToPlayer>", "<visibleToPlayer>true</visibleToPlayer>"),
    ("surrik", "fauna", "<li>SoilRich</li>\n", ""),
    ("hooks", "bloom", "ForceSurface();", "GetHashCode();"),
    ("hooks", "ripple", "&& !IsCrustSwimmer(p.def)", ""),
    ("hooks", "comp", "public void ForceSurface()", "internal void ForceSurface()"),
    ("ribbonwhip", "settings", "rippleMaxBodySize = 0.6f", "rippleMaxBodySize = 0.2f"),
    ("thornholdden", "fauna", "<standState>RM_ThornholdStand</standState>", "<standState>Manhunter</standState>"),
    ("thornholdden", "fauna", "<li>RM_Venomvine</li>", "<li>RM_Venomvin</li>"),
    ("thornholdden", "fauna", '<li Class="RimMandrake.EnvironmentalHazards.ContactVenomImmunity" />', ""),
    ("thornholdden", "dens", "damage.ExternalViolenceFor(pawn)", "damage.Equals(pawn)"),
    ("thornholdden", "dens", "otherPawn: attacker", "otherPawn: null"),
    ("thornholdden", "settings", "thornholdStandEnabled = true", "thornholdStandEnabled = false"),
    ("rollbug", "dens", "ball.Strip(false);\n            }\n            Pawn inner", "}\n            Pawn inner"),
    ("rollbug", "dens", "ball.Strip(false);\n                }\n            };", "}\n            };"),
    ("rollbug", "dens", "pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _);",
     "pawn.carryTracker.GetHashCode();"),
    ("rollbug", "settings", "rollbugTakesColonyCorpses = true", "rollbugTakesColonyCorpses = false"),
    ("rollbug", "densdefs", "<insertTag>Animal_PreWander</insertTag>", "<insertTag>Humanlike_PreMain</insertTag>"),
    ("rollbug", "fauna", "RimMandrake.LeaningScrub.RM_CompProperties_CarrionLarder", "RimMandrake.LeaningScrub.RM_CompProperties_Larder"),
    ("stubs", "fauna", "SCRUBAMBUSHERS_BUILD_EDGE_RUN_CANOPY; plain predator here.", "ROLLBUG_DECIDE_CARRION_BALL; plain predator here."),
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
        fn = dict(ROWS)[row]
        try:
            errs = fn(broken)
        except ET.ParseError as e:
            errs = ["parse error %s" % e]
        expect("planted break caught: %s (%s -> %s)" % (row, old.strip()[:40], new.strip()[:30]), bool(errs))
    if FAILED:
        print("FAILED %d: %s" % (len(FAILED), ", ".join(FAILED)))
        return 1
    print("PASS selftest_leaningscrub_fauna_behaviours (%d rows, %d planted breaks)" % (len(ROWS), len(BREAKS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
