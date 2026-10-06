"""validation.py -- first script for RimMandrake: Solar Mirrors (mandrake.rm.solarmirrors), a standalone
RimMandrake mod depending on mandrake.rm.biomes (CreatureBehaviors' shade grid is folded into it).

SOLAR_MIRRORS_MOD_DESIGN_1 (design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md): the core (light
layer, signal/static mirrors, heliostat, re-aim job, relays, glow, render) plus E1 (solar furnace),
E4 (blinding defence) and a sun-stone receiver. Design §6.2 lists the must-be-true lines; their chains
are below. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run SolarMirrors

Offline: `python3 src/RimMandrake/SolarMirrors/validation.py` runs static_checks() only.
Not proven anywhere yet: every live line (no bridge [Tool] reads the shade grid or the mirror layer at
a cell; `RM_ShadeProbe` is owed, design §6.2 line 2), and legibility (owner-watched, design §2.8).
"""
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "Utils")))
from modcheck import Suite, ExpectationFailed  # noqa: E402

SRC = os.path.join(HERE, "Source")
DEFS = os.path.join(HERE, "Defs")
SHADE_GRID_CS = os.path.join(HERE, "..", "CreatureBehaviors", "Source", "RM_MapComponent_ShadeGrid.cs")
CB_DLL = os.path.join(HERE, "..", "CreatureBehaviors", "Assemblies", "RimMandrake.CreatureBehaviors.dll")
GLARE_HEDIFF_XML = os.path.join(HERE, "..", "CreatureBehaviors", "Defs", "HediffDefs", "RM_GlareBlind_Hediffs.xml")
NS = "RimMandrake.SolarMirrors."
MIRRORS = ("RM_SignalMirror", "RM_StaticMirror", "RM_Heliostat")
RECEIVERS = ("RM_SunStone", "RM_SolarFurnace")
ALL_DEFS = ["ThingDef/%s" % d for d in MIRRORS + RECEIVERS] + ["JobDef/RM_ReAimMirror", "WorkGiverDef/RM_ReAimMirror"]
NEEDLES = ("mandrake.rm.solarmirrors", "RimMandrake.SolarMirrors", "RM_CompMirror", "RM_MirrorLight",
           "RM_SolarFurnace", "RM_Heliostat", "RM_StaticMirror", "RM_SignalMirror", "RM_SunStone",
           # The CreatureBehaviors light hook: a TypeLoad/MissingMethod naming it means the shipped
           # Biomes DLL predates the hook and mirror light reaches nothing.
           "IRM_LightLayer", "RegisterLightSource")
SHADE_THRESHOLD = 0.8  # RM_MapComponent_ShadeGrid.ShadeCastingFillPercentThreshold

suite = Suite("SolarMirrors")
suite.toggles = ["shadeEffect", "glowEffect", "beamRender", "staticSweep", "blindingDefence",
                 "blindSeverityPerDay", "solarFurnace", "reflectivityMultiplier", "reAimWorkMultiplier",
                 "passIntervalTicks", "maxChain"]


# ── live chains (design §6.2) ────────────────────────────────────────────

@suite.chain("load")
def load(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("UNMEASURED: drain_log did not answer")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("present", beyond_toggle=True):
        if t._guard():
            # A ThingDef whose comp Class cannot resolve is discarded whole, so presence is the check.
            r = t.bridge_call("jawa/get_defs", defs=";".join(ALL_DEFS), fields="defName")
            if not isinstance(r, dict) or not r.get("success"):
                raise ExpectationFailed("UNMEASURED: get_defs failed: %r" % (r,))
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


# Lines that need a probe this repo does not have yet. Each stays UNMEASURED, never PASS.
LIVE_OWED = [
    ("hook", "registered", "shadeEffect",
     "on a map with a lit mirror, RM_MapComponent_ShadeGrid.LightAt(cell) > 0 at the spot (the grid pulled the "
     "light through IRM_LightLayer.AddLight). Needs RM_ShadeProbe"),
    ("light", "unshade", "shadeEffect",
     "aim a static mirror at a shaded cell: ShadeAt falls and ExposureAt rises there; un-aim restores both. "
     "Needs RM_ShadeProbe (a [Tool] reading ShadeAt/ExposureAt/LightAt at a cell)"),
    ("light", "blocked", None, "build a wall on the beam line; the spot's light is 0 within one pass (250 ticks)"),
    ("light", "roof", None, "a roof over the target, and a roof on the path, each take the light (design §2.2 rule)"),
    ("light", "chain", "maxChain", "a mirror in shadow throws nothing; lit by a second mirror it fires (relay)"),
    ("glow", "postfix", "glowEffect", "GroundGlowAt at a lit cell on a Long Shade map reads 1.0 against 0.8 beside it"),
    ("herd", "patchgraph", "shadeEffect", "re-aiming bumps the shade grid's GridVersion and changes the patch count"),
    ("save", "roundtrip", None, "save and load keeps every mirror's target and normal; the rebuilt layer hashes equal"),
    ("heliostat", "power_freeze", None, "cut a heliostat's power under a moving sun: its spot starts to drift"),
    ("furnace", "gated", "solarFurnace", "a furnace takes no bill with one mirror on it and works with two"),
    ("blind", "hostile_gain", "blindingDefence", "a hostile humanlike in a beam gains RM_GlareBlind; goggles stop it"),
]


@suite.chain("live_owed")
def live_owed(t):
    for chain, comp, tog, why in LIVE_OWED:
        with t.component("%s.%s" % (chain, comp), toggle=tog, beyond_toggle=tog is None):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: " + why)


# ── offline ──────────────────────────────────────────────────────────────

def _sun(shadow_x, shadow_z, elev):
    """Mirror of RM_MirrorMath.SunVector."""
    e = math.radians(max(0.0, min(90.0, elev)))
    ax, az = -shadow_x, -shadow_z
    ln = math.hypot(ax, az)
    if ln < 1e-5:
        return (0.0, 1.0, 0.0)
    return (ax / ln * math.cos(e), math.sin(e), az / ln * math.cos(e))


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _eff(s, t):
    """Mirror of RM_MirrorMath.Efficiency, sqrt((1 + s.t) / 2)."""
    return math.sqrt(max(0.0, (1 + sum(a * b for a, b in zip(s, t))) / 2))


def _math_checks(bad):
    """Design §2.2's claims about the cosine law, on the same formula the C# uses."""
    face_h = 1.5
    # Low pinned sun to the east (shadows fall west), elevation 10.
    s = _sun(-1.0, 0.0, 10.0)
    toward = _unit((10.0, -face_h, 0.0))   # throw back toward the sun's side
    side = _unit((0.0, -face_h, 10.0))
    down = _unit((-10.0, -face_h, 0.0))    # straight downsun
    e_t, e_s, e_d = _eff(s, toward), _eff(s, side), _eff(s, down)
    if not e_t > 0.95:
        bad.append("toward-sun efficiency %.2f, design says ~100%%" % e_t)
    if not 0.6 < e_s < 0.8:
        bad.append("sideways efficiency %.2f, design says ~71%%" % e_s)
    if not e_d < 0.25:
        bad.append("downsun efficiency %.2f, design says it falls toward 0" % e_d)
    # Overhead sun: ~0.71 whichever way the target lies (the GPT correction, §4 taken 1).
    s = _sun(0.0, -1.0, 89.9)
    for tgt in ((10.0, -face_h, 0.0), (0.0, -face_h, -10.0), (-7.0, -face_h, 7.0)):
        e = _eff(s, _unit(tgt))
        if not 0.6 < e < 0.8:
            bad.append("overhead-sun efficiency %.2f toward %r, design says ~0.71 in every direction" % (e, tgt))


def _class_names():
    names = set()
    for f in os.listdir(SRC):
        if f.endswith(".cs"):
            names |= set(re.findall(r"\bclass (\w+)", open(os.path.join(SRC, f), encoding="utf-8").read()))
    return names


def _def_files():
    for dp, _, fns in os.walk(DEFS):
        for fn in fns:
            if fn.endswith(".xml"):
                yield os.path.join(dp, fn)


def _hook_checks(bad):
    """The light reaches the shade grid ONLY through CreatureBehaviors' public hook (design §2.3).
    If the hook is gone, or not folded into Recompute, mirrors light nothing for shade, heat or
    pathing -- and nothing would say so. So each piece is checked, loudly."""
    cb = open(SHADE_GRID_CS, encoding="utf-8").read()
    for pat, what in ((r"public interface IRM_LightLayer\s*\{[^}]*bool AddLight\(float\[\] into\);", "interface IRM_LightLayer.AddLight(float[])"),
                      (r"public void RegisterLightSource\(IRM_LightLayer source\)", "RegisterLightSource(IRM_LightLayer)"),
                      (r"public void UnregisterLightSource\(IRM_LightLayer source\)", "UnregisterLightSource(IRM_LightLayer)"),
                      (r"BuildLightLayer\(\);\s*RebuildHeatLayers\(\);", "Recompute building light BEFORE the heat layers"),
                      (r"RM_SunHeatMath\.WithLight\(ex, lightLayer\[i\]\)", "light folded into the cached exposure"),
                      (r"RM_SunHeatMath\.ShadeWithLight\(s, lightLayer\[i\]\)", "light folded into ShadeAt")):
        if not re.search(pat, cb):
            bad.append("HOOK MISSING: CreatureBehaviors' shade grid lacks %s -- mirror light reaches nothing" % what)
    # The shipped CreatureBehaviors DLL must carry the hook too (source alone is not what loads).
    # Metadata names are UTF-8 in the #Strings heap; sanity-probe a name that has always been there.
    if os.path.isfile(CB_DLL):
        blob = open(CB_DLL, "rb").read()
        if b"RebuildHeatLayers" not in blob:
            bad.append("sanity: RebuildHeatLayers not found in %s (the DLL scan is broken)" % CB_DLL)
        for name in (b"IRM_LightLayer", b"RegisterLightSource", b"AddLight"):
            if name not in blob:
                bad.append("HOOK MISSING from the built DLL %s: %s (rebuild CreatureBehaviors)" % (CB_DLL, name.decode()))
    else:
        bad.append("no CreatureBehaviors DLL at %s" % CB_DLL)
    src = {f: open(os.path.join(SRC, f), encoding="utf-8").read() for f in os.listdir(SRC) if f.endswith(".cs")}
    light = src.get("RM_MapComponent_MirrorLight.cs", "")
    if not re.search(r"class RM_MapComponent_MirrorLight\s*:\s*MapComponent,\s*IRM_LightLayer", light):
        bad.append("RM_MapComponent_MirrorLight does not implement IRM_LightLayer")
    if "RegisterLightSource(this)" not in light or "UnregisterLightSource(this)" not in light:
        bad.append("RM_MapComponent_MirrorLight never registers/unregisters with the shade grid")
    for f, text in src.items():
        if re.search(r"HarmonyPatch\(typeof\(RM_MapComponent_ShadeGrid\)", text) or "FieldRefAccess<RM_MapComponent_ShadeGrid" in text:
            bad.append("%s patches the shade grid's internals; use the public light hook" % f)


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    if about.findtext("packageId") != "mandrake.rm.solarmirrors":
        bad.append("packageId is %r" % about.findtext("packageId"))
    deps = [li.findtext("packageId") for li in about.findall("modDependencies/li")]
    after = [li.text for li in about.findall("loadAfter/li")]
    for need in ("brrainz.harmony", "mandrake.rm.biomes"):
        if need not in deps or need not in after:
            bad.append("About.xml must depend on AND loadAfter %s" % need)
    if "mandrake.rm.creaturebehaviors" in after + deps:
        bad.append("About.xml names the folded mandrake.rm.creaturebehaviors (a silent no-op since the wave-2 fold)")

    classes = _class_names()
    things = {}
    for path in _def_files():
        for e in ET.parse(path).getroot():
            dn = e.findtext("defName")
            if dn and not dn.startswith("RM_"):
                bad.append("%s: defName %s lacks the RM_ tier prefix" % (os.path.basename(path), dn))
            for tag in ("driverClass", "giverClass"):
                v = e.findtext(tag)
                if v and v.startswith(NS) and v[len(NS):] not in classes:
                    bad.append("%s names %s, which no Source class defines" % (dn, v))
            for li in e.iter("li"):
                c = li.get("Class") or ""
                if c.startswith(NS) and c[len(NS):] not in classes:
                    bad.append("%s names comp class %s, which no Source class defines" % (dn, c))
            if e.tag == "ThingDef" and dn:
                things[dn] = e
    for dn in MIRRORS + RECEIVERS:
        if dn not in things:
            bad.append("ThingDef %s missing" % dn)
    base = next((e for p in _def_files() for e in ET.parse(p).getroot() if e.get("Name") == "RM_MirrorBase"), None)
    if base is None or base.get("Abstract") != "True":
        bad.append("RM_MirrorBase missing or not abstract")
    else:
        # A mirror must never shade itself (design §2.2: its own footprint is excluded).
        if float(base.findtext("fillPercent") or "1") >= SHADE_THRESHOLD or base.findtext("staticSunShadowHeight") != "0":
            bad.append("RM_MirrorBase would cast shade (fillPercent >= %.1f or a sun shadow height)" % SHADE_THRESHOLD)
    single_max = 0.0
    for dn in MIRRORS:
        e = things.get(dn)
        if e is None:
            continue
        if e.get("ParentName") != "RM_MirrorBase":
            bad.append("%s is not on RM_MirrorBase" % dn)
        props = [li for li in e.findall("comps/li") if li.get("Class") == NS + "RM_CompProperties_Mirror"]
        if len(props) != 1:
            bad.append("%s carries %d mirror comps (want 1)" % (dn, len(props)))
            continue
        p = props[0]
        size = (e.findtext("size") or "(1,1)").strip("()").split(",")
        if p.findtext("spotSize") != size[0].strip():
            bad.append("%s spot %s != its size %s (design §2.2: a flat mirror throws its own size)" % (dn, p.findtext("spotSize"), size[0]))
        refl = [float(p.findtext("reflectivity") or "0.7")] + [float(li.findtext("value")) for li in p.findall("stuffReflectivity/li")]
        if any(not 0 < r <= 1 for r in refl):
            bad.append("%s reflectivity out of 0..1: %r" % (dn, refl))
        single_max = max(single_max, max(refl))
        tracks = p.findtext("tracks") == "true"
        has_power = any(li.get("Class") == "CompProperties_Power" and li.findtext("compClass") == "CompPowerTrader"
                        for li in e.findall("comps/li"))
        if tracks != has_power:
            bad.append("%s: tracks=%s but powered=%s (only a heliostat tracks, and it needs power)" % (dn, tracks, has_power))
    for dn in RECEIVERS:
        e = things.get(dn)
        if e is None:
            continue
        props = [li for li in e.findall("comps/li") if li.get("Class") == NS + "RM_CompProperties_LightReceiver"]
        if len(props) != 1:
            bad.append("%s carries %d receiver comps (want 1)" % (dn, len(props)))
            continue
        on, off = float(props[0].findtext("litAt")), float(props[0].findtext("unlitBelow"))
        if not off < on:
            bad.append("%s hysteresis inverted (unlitBelow %s >= litAt %s)" % (dn, off, on))
    furnace = things.get("RM_SolarFurnace")
    if furnace is not None:
        p = [li for li in furnace.findall("comps/li") if li.get("Class") == NS + "RM_CompProperties_LightReceiver"]
        if p and float(p[0].findtext("litAt")) <= single_max:
            bad.append("furnace lights at %s, which one mirror (max %.2f) can reach: design E1 wants concentration"
                       % (p[0].findtext("litAt"), single_max))
        if p and p[0].findtext("gatesBills") != "true":
            bad.append("furnace does not gate bills on light")
        if [li for li in furnace.findall("comps/li") if li.get("Class") == "CompProperties_ReportWorkSpeed"]:
            bad.append("furnace restates BenchBase's CompProperties_ReportWorkSpeed (it would be listed twice)")
        if any(li.get("Class") == "CompProperties_Power" for li in furnace.findall("comps/li")):
            bad.append("furnace has a power comp: it must run on light alone")

    _hook_checks(bad)
    if "<defName>RM_GlareBlind</defName>" not in open(GLARE_HEDIFF_XML, encoding="utf-8").read():
        bad.append("RM_GlareBlind hediff gone: the blinding defence would silently do nothing")

    _math_checks(bad)

    proj = open(os.path.join(SRC, "RM_SolarMirrors.csproj"), encoding="utf-8").read()
    for f in os.listdir(SRC):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(SRC, "RM_SolarMirrorsMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("toggle %s is not Scribed" % f)
    if "maxOneColumn = true" not in mod or "BeginScrollView" not in mod:
        bad.append("settings screen lacks the scroll view + maxOneColumn (Webwork fix cfdba9344)")
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RM_SolarMirrors.xml"), encoding="utf-8").read()
    used = set()
    for f in os.listdir(SRC):
        if f.endswith(".cs"):
            used |= set(re.findall(r'"(RM_SolarMirrors_[A-Za-z_]+)"', open(os.path.join(SRC, f), encoding="utf-8").read()))
    for k in sorted(used):
        if "<%s>" % k not in keyed:
            bad.append("keyed string %s missing" % k)
    if not used:
        bad.append("sanity: no keyed strings found in Source (the scan is broken)")
    asm = os.path.join(HERE, "Assemblies", "RimMandrake.SolarMirrors.dll")
    if not os.path.isfile(asm) or not os.path.isfile(asm + ".srchash"):
        bad.append("no DLL + .srchash at %s" % asm)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
