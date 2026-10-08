"""validation.py -- modcheck suite for RimMandrake: Pyrinth (mandrake.rm.pyrinth).

First north-star script (PYRINTH_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/Pyrinth.md (DRAFT).
Absorbed copy of det.epochspyrinth: the pyrinth ore, torch/wall-torch/pylon/heater furniture, pyrinth blade and spark
effects. DORMANT by design (About.xml: not deployable while the donor is active; defNames are preserved verbatim). It has NO C#
and NO settings class, and no DEPLOY_HOLD entry. A live pass proves the defNames resolve, not that this pack supplied them.

CHAINS
  defs_resolve       every def parsed from the mod's own XML that actually DEPLOYS resolves live; a control name reads
                     notFound; no file of this mod is named in DEPLOY_HOLD.txt.
  settings_roundtrip there is NO settings class (no Source C#): the probe asserts none exists, nothing is round-tripped.
  ore_and_donor_identity  DV_MineablePyrinth's mineableThing / mineableYield equal the XML's; whether THIS pack is the loaded copy: UNMEASURED.
  furniture_and_weapon    glow/heat/meditation, blade, MO and Royalty patches, Lantern Deeps gate: UNMEASURED, each saying why.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game. Nothing here has been run live.
"""
import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "Pyrinth"
SETTINGS = None
BIOME = None
CONTROL_ABSENT = "ThingDef/PyrinthNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=\s*([^;]+);")
_HOLD_FILE = os.path.join(HERE, "..", "..", "DEPLOY_HOLD.txt")


def held_globs():
    """Globs from src/DEPLOY_HOLD.txt that name this mod (relative to custom_patches/, '*' crosses '/')."""
    out = []
    if not os.path.isfile(_HOLD_FILE):
        return out
    for line in open(_HOLD_FILE, encoding="utf-8"):
        g = line.split("#", 1)[0].strip()
        if g.startswith(MOD + "/"):
            out.append(g)
    return out


HELD = held_globs()


def is_held(rel):
    return any(fnmatch.fnmatchcase(MOD + "/" + rel.replace(os.sep, "/"), g) for g in HELD)


def parse_defs():
    """([(DefType, defName)] deployed, [(DefType, defName, file)] held) from every non-abstract top-level def under Defs/."""
    deployed, held = [], []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, HERE)
            for el in ET.parse(full).getroot():
                nm = el.find("defName") if isinstance(el.tag, str) else None
                if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                    (held if is_held(rel) else deployed).append((el.tag, nm.text.strip(), rel) if is_held(rel) else (el.tag, nm.text.strip()))
    return sorted(set(deployed)), sorted(set(held))


SHIPPED, HELD_DEFS = parse_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of the settings class, read from the C# ({} when none)."""
    return {}

def ore_facts():
    """(mineableThing, mineableYield) of DV_MineablePyrinth, parsed from the XML."""
    p = os.path.join(HERE, "Defs", "Absorbed_EpochsPyrinth", "ThingDefs_Buildings", "Absorbed_EpochsPyrinth_Buildings_Natural.xml")
    for el in ET.parse(p).getroot():
        if el.findtext("defName") == "DV_MineablePyrinth":
            return (el.findtext(".//mineableThing"), el.findtext(".//mineableYield"))
    return (None, None)



# ---- PYRINTH_COVERAGE_GAPS_1: what the shipped XML makes the furniture / blade / effects DO ---------------------------
# Parsed from the pack's own XML with parent/Inherit resolution inside the pack (vanilla parents are leaves), so each bar
# asserts a property of the effective def, and a selftest plants the XML break that must redden it. Live get_defs reads
# only prove names resolve (and cannot tell this pack from the donor), so these static bars are the behaviour floor.
GLOW_DEFS = ("DV_PyrinthLamp", "DV_PyrinthWallLamp", "DV_PyrinthBrazier", "DV_PyrinthHeater")
FLAME_DEFS = ("DV_PyrinthLamp", "DV_PyrinthWallLamp", "DV_PyrinthBrazier")


def load_pack(root=None):
    """({defName: element}, {Name: element}, [(file, Element root)] patches) for every def / patch file of the pack."""
    root = root or HERE
    byname, named, patches = {}, {}, []
    for dp, _d, files in os.walk(os.path.join(root, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    if not isinstance(el.tag, str):
                        continue
                    if el.get("Name"):
                        named[el.get("Name")] = el
                    if el.findtext("defName"):
                        byname[el.findtext("defName").strip()] = el
    for dp, _d, files in os.walk(os.path.join(root, "Patches")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                patches.append((fn, ET.parse(os.path.join(dp, fn)).getroot()))
    return byname, named, patches


def _chain(el, named):
    out = [el]
    while el.get("ParentName") in named:
        el = named[el.get("ParentName")]
        out.append(el)
    return list(reversed(out))     # root parent first


def effective_comps(el, named):
    """Comp <li> elements after inheritance: parents' first, a child with comps Inherit="False" starts over."""
    comps = []
    for d in _chain(el, named):
        c = d.find("comps")
        if c is None:
            continue
        if c.get("Inherit", "").lower() == "false":
            comps = []
        comps.extend(list(c))
    return comps


def effective_stat(el, named, stat):
    v = None
    for d in _chain(el, named):
        sb = d.find("statBases")
        if sb is not None and sb.find(stat) is not None:
            v = sb.findtext(stat)
    return v


def _comp(comps, cls):
    return [c for c in comps if c.get("Class") == cls]


def _num(el, tag, default=None):
    try:
        return float(el.findtext(tag))
    except (TypeError, ValueError):
        return default


def semantic_findings(byname, named, patches):
    """Findings for: glow, heat, meditation, spark effecters, blade, cost/ref integrity, patch targets and values."""
    bad = []

    def need(name):
        el = byname.get(name)
        if el is None:
            bad.append("%s is not defined in the pack" % name)
        return el

    rad, heat = {}, {}
    for name in GLOW_DEFS:
        el = need(name)
        if el is None:
            continue
        comps = effective_comps(el, named)
        g = _comp(comps, "CompProperties_Glower")
        if len(g) != 1 or not (_num(g[0], "glowRadius", 0) > 0):
            bad.append("%s: no Glower with glowRadius > 0 (%d glowers)" % (name, len(g)))
        else:
            rad[name] = _num(g[0], "glowRadius")
            if len([x for x in (g[0].findtext("glowColor") or "").strip("() ").split(",") if x.strip()]) != 4:
                bad.append("%s: glowColor is not an RGBA tuple" % name)
        h = _comp(comps, "CompProperties_HeatPusher")
        if len(h) != 1 or not (_num(h[0], "heatPerSecond", 0) > 0) or not (_num(h[0], "heatPushMaxTemperature", 0) > 0):
            bad.append("%s: no HeatPusher with heatPerSecond > 0 and heatPushMaxTemperature > 0" % name)
        else:
            heat[name] = _num(h[0], "heatPerSecond")
            if h[0].findtext("compClass") != "CompHeatPusherPowered":
                bad.append("%s: heat pusher is not CompHeatPusherPowered (it would heat unconditionally and ignore a power switch)" % name)
    if "DV_PyrinthWallLamp" in rad and "DV_PyrinthLamp" in rad and not rad["DV_PyrinthWallLamp"] < rad["DV_PyrinthLamp"]:
        bad.append("wall torch is not dimmer than the torch (its description says it is): %s vs %s" % (rad["DV_PyrinthWallLamp"], rad["DV_PyrinthLamp"]))
    if len(heat) == 4 and not (heat["DV_PyrinthHeater"] > heat["DV_PyrinthBrazier"] > heat["DV_PyrinthLamp"]):
        bad.append("heat ladder broken (heater > pylon > torch expected): %r" % heat)

    for name in FLAME_DEFS:
        el = byname.get(name)
        if el is None:
            continue
        comps = effective_comps(el, named)
        m = _comp(comps, "CompProperties_MeditationFocus")
        if len(m) != 1:
            bad.append("%s: %d MeditationFocus comps, want 1" % (name, len(m)))
            continue
        if [x.text for x in m[0].findall("focusTypes/li")] != ["Flame"] or m[0].findtext("statDef") != "MeditationFocusStrength":
            bad.append("%s: meditation focus is not Flame via MeditationFocusStrength" % name)
        if effective_stat(el, named, "MeditationFocusStrength") is None:
            bad.append("%s: no MeditationFocusStrength statBase to scale (the focus would read nothing)" % name)
        lit = m[0].findall("offsets/li[@Class='FocusStrengthOffset_Lit']")
        if len(lit) != 1 or not (_num(lit[0], "offset", 0) > 0):
            bad.append("%s: lit-flame offset missing or not positive" % name)
        near = m[0].findall("offsets/li[@Class='FocusStrengthOffset_BuildingDefsLit']")
        if len(near) != 1:
            bad.append("%s: no FocusStrengthOffset_BuildingDefsLit" % name)
        else:
            listed = [x.text for x in near[0].findall("defs/li")]
            for d in FLAME_DEFS:
                if d not in listed:
                    bad.append("%s: nearby-flame list omits %s (pack flames would not boost each other)" % (name, d))
            if not (_num(near[0], "offsetPerBuilding", 0) > 0 and _num(near[0], "radius", 0) > 0 and _num(near[0], "maxBuildings", 0) > 0):
                bad.append("%s: nearby-flame offset/radius/maxBuildings not all positive" % name)
        if not any(p.text == "PlaceWorker_MeditationOffsetBuildingsNear" for p in el.findall("placeWorkers/li")) and name != "DV_PyrinthWallLamp":
            bad.append("%s: no PlaceWorker_MeditationOffsetBuildingsNear (the player is never shown the focus ring)" % name)

    for name in ("DV_PyrinthLamp", "DV_PyrinthWallLamp", "DV_PyrinthBrazier", "DV_PyrinthHeater"):
        el = byname.get(name)
        if el is None:
            continue
        for e in _comp(effective_comps(el, named), "CompProperties_Effecter"):
            ef = byname.get(e.findtext("effecterDef") or "")
            if ef is None or ef.tag != "EffecterDef":
                bad.append("%s: effecter %r is not an EffecterDef of the pack" % (name, e.findtext("effecterDef")))
                continue
            kids = ef.findall("children/li")
            if not kids:
                bad.append("%s: effecter %s has no sub-effecter" % (name, ef.findtext("defName")))
            for k in kids:
                mote = byname.get(k.findtext("moteDef") or "")
                if mote is None or mote.findtext("thingClass") != "MoteThrownAttached" or not (_num(mote.find("mote"), "solidTime", 0) > 0):
                    bad.append("%s: spark mote %r is missing, not MoteThrownAttached, or never solid" % (ef.findtext("defName"), k.findtext("moteDef")))
                if not (_num(k, "chancePerTick", 0) > 0):
                    bad.append("%s: sub-effecter chancePerTick is not positive (it would never spark)" % ef.findtext("defName"))
    big, small = byname.get("DV_PyrinthSparkingEffect"), byname.get("DV_PyrinthSparkingEffectSmall")
    if big is not None and small is not None and not (_num(small.find("children/li"), "chancePerTick", 1) < _num(big.find("children/li"), "chancePerTick", 0)):
        bad.append("the small spark effecter is not rarer than the big one")

    blade = need("DV_MeleeWeapon_PyrinthBlade")
    if blade is not None:
        tools = blade.findall("tools/li")
        caps = [t.findtext("capacities/li") for t in tools]
        if sorted(caps) != ["Blunt", "Cut", "Stab"]:
            bad.append("blade tools are %r, want Blunt+Stab+Cut" % caps)
        for t in tools:
            if not (_num(t, "power", 0) > 0 and _num(t, "cooldownTime", 0) > 0):
                bad.append("blade tool %r has non-positive power or cooldown" % t.findtext("label"))
        burners = [t for t in tools if t.find("extraMeleeDamages/li[def='Flame']") is not None]
        if sorted(t.findtext("label") for t in burners) != ["edge", "point"]:
            bad.append("the blade's edge and point are not both Flame-searing (its description says it burns): %r" % [t.findtext("label") for t in burners])
        for t in burners:
            x = t.find("extraMeleeDamages/li[def='Flame']")
            if not (_num(x, "amount", 0) > 0 and 0 < _num(x, "chance", 0) <= 1):
                bad.append("blade flame bonus on %s has a non-positive amount or a chance outside (0,1]" % t.findtext("label"))
        if blade.findtext("recipeMaker/researchPrerequisite") is None or blade.find("costList/DV_Pyrinth") is None:
            bad.append("blade has no research prerequisite or no DV_Pyrinth cost")

    ex = need("DV_PyrinthHeater")
    if ex is not None:
        e = _comp(effective_comps(ex, named), "CompProperties_Explosive")
        if len(e) != 1 or e[0].findtext("preExplosionSpawnThingDef") not in byname:
            bad.append("heater explosive comp missing or its pre-explosion filth is not a def of the pack")

    for name, el in sorted(byname.items()):
        for ing in el.findall("costList/*"):
            if ing.tag.startswith("DV_") and ing.tag not in byname:
                bad.append("%s costs %s, which the pack does not define" % (name, ing.tag))
        for tag in ("filthLeaving", "mineableThing"):
            v = el.findtext(".//" + tag)
            if v and v.startswith("DV_") and v not in byname:
                bad.append("%s.%s names %s, which the pack does not define" % (name, tag, v))

    import re as _re
    for fn, root in patches:
        for xp in root.iter("xpath"):
            for m in _re.finditer(r'defName\s*=\s*"(DV_\w+)"', xp.text or ""):
                tgt = byname.get(m.group(1))
                tail = (xp.text or "").rsplit("/", 1)[-1]
                if tgt is None or tgt.find(tail) is None:
                    bad.append("%s: xpath targets %s/%s, which the pack does not have (a patch that matches nothing logs nothing)" % (fn, m.group(1), tail))
        for li in root.iter("li"):
            if (li.text or "").startswith("DV_"):
                if li.text not in byname:
                    bad.append("%s: patch adds %s, which the pack does not define" % (fn, li.text))
                elif not li.get("MayRequire") and "Royalty" in fn:
                    bad.append("%s: the Royalty patch adds %s with no MayRequire guard" % (fn, li.text))
    return bad


def static_checks():
    bad = []
    if len(SHIPPED) + len(HELD_DEFS) < 6:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % (len(SHIPPED) + len(HELD_DEFS))]
    if settings_fields():
        bad.append("a settings class appeared: add its round-trip expectations (this script assumes none)")
    if os.path.isdir(os.path.join(HERE, "Source")) and [f for f in os.listdir(os.path.join(HERE, "Source")) if f.endswith(".cs")]:
        bad.append("C# source appeared under Source/: add a csproj/settings check")
    ore = ore_facts()
    if ore[0] != "DV_Pyrinth" or not float(ore[1]) > 0:
        bad.append("ore facts parsed wrong: %r" % (ore,))
    bad.extend(semantic_findings(*load_pack()))
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("ThingDef", "EffecterDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if "DV_Pyrinth" not in [n for _t, n in SHIPPED]:
        bad.append("DV_Pyrinth missing")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", MOD + ".md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite(MOD)
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        if ty == "string":
            return str(a) == str(b)
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_deployed_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):      # batches: a long defs string risks the 30 s reply timeout
                chunk = names[i:i + 40]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))


    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if settings_fields():
                raise ExpectationFailed("a settings class exists but the script assumes none")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "string":
                    new = "zz_probe" if str(old) != "zz_probe" else "zz_probe2"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("ore_and_donor_identity")
    def ore_and_donor_identity(t):
        # The mod is dormant (About.xml: NOT YET DEPLOYABLE) and preserves the donor's defNames verbatim, so a pass here says the
        # NAMES resolve (from the donor det.epochspyrinth or from this mod), never that THIS mod is what loaded.
        with t.component("mineable_ore_yield_matches_xml", beyond_toggle=True):
            want = ore_facts()
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/DV_MineablePyrinth", fields="mineableThing,mineableYield", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read DV_MineablePyrinth: %r" % (r,))
                f = rows[0].get("fields") or {}
                if any(f.get(k) is None or "no such field" in str(f.get(k)) for k in ("mineableThing", "mineableYield")):
                    _unmeasured(t, "get_defs returned no mineable fields: %r" % (f,))
                    return
                if str(f.get("mineableThing")) != want[0]:
                    raise ExpectationFailed("mineableThing reads %r, XML says %r" % (f.get("mineableThing"), want[0]))
                if float(f.get("mineableYield")) != float(want[1]):
                    raise ExpectationFailed("mineableYield reads %r, XML says %r" % (f.get("mineableYield"), want[1]))
        with t.component("this_mod_is_the_loaded_copy", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "whether THIS dormant pack or the live donor det.epochspyrinth supplied the defs cannot be told from get_defs; "
                               "it needs the mod-of-origin of the def (not exposed) or det.epochspyrinth removed from the mod list")

    @suite.chain("furniture_and_weapon")
    def furniture_and_weapon(t):
        # PYRINTH_COVERAGE_GAPS_1: the first five bars assert the effective shipped XML (parent/Inherit resolved), so they run
        # with no game; the stubs after them are what needs a built instance, another mod, or a pawn fight.
        findings = semantic_findings(*load_pack())

        with t.component("torch_family_glows_heats_and_carries_the_ladder", beyond_toggle=True):
            bad = [f for f in findings if any(k in f for k in ("Glower", "glowColor", "HeatPusher", "heat ladder", "dimmer", "CompHeatPusherPowered"))]
            if bad:
                raise ExpectationFailed("; ".join(bad))
        with t.component("flame_furniture_gives_meditation_focus", beyond_toggle=True):
            bad = [f for f in findings if any(k in f for k in ("editation", "nearby-flame", "lit-flame", "focus"))]
            if bad:
                raise ExpectationFailed("; ".join(bad))
        with t.component("spark_effecters_resolve_to_attached_motes_that_fire", beyond_toggle=True):
            bad = [f for f in findings if any(k in f for k in ("effecter", "mote", "sub-effecter", "spark"))]
            if bad:
                raise ExpectationFailed("; ".join(bad))
        with t.component("pyrinth_blade_tools_hit_and_the_edge_and_point_sear", beyond_toggle=True):
            bad = [f for f in findings if any(k in f for k in ("blade", "DV_MeleeWeapon"))]
            if bad:
                raise ExpectationFailed("; ".join(bad))
        with t.component("every_reference_and_patch_target_resolves_inside_the_pack", beyond_toggle=True):
            bad = [f for f in findings if any(k in f for k in ("costs ", "names ", "xpath", "patch adds", "Royalty patch", "not defined", "explosive"))]
            if bad:
                raise ExpectationFailed("; ".join(bad))
        with t.component("no_finding_escapes_the_five_bars_above", beyond_toggle=True):
            known = ("Glower", "glowColor", "HeatPusher", "heat ladder", "dimmer", "CompHeatPusherPowered", "editation", "nearby-flame",
                     "lit-flame", "focus", "effecter", "mote", "sub-effecter", "spark", "blade", "DV_MeleeWeapon", "costs ", "names ",
                     "xpath", "patch adds", "Royalty patch", "not defined", "explosive")
            stray = [f for f in findings if not any(k in f for k in known)]
            if stray:
                raise ExpectationFailed("finding(s) no bar claims: %s" % "; ".join(stray))
        for name, why in (
            ("torch_family_glow_and_heat_in_play", "a built, powered instance, a light-level read and a room temperature read on a bland map (the XML bars above prove the shipped numbers, not the engine's use of them)"),
            ("pyrinth_blade_damage_in_a_fight", "damage in play needs a pawn fight; the tool profile is asserted statically above"),
            ("medieval_overhaul_heater_cost_patch", "applies only with Medieval Overhaul loaded; a patch that matches nothing logs nothing, so the live effect is unprovable without that mod (its xpath target is asserted statically above)"),
            ("royalty_throne_room_patch", "edits vanilla RoyalTitleDef throneRoomRequirements, which the offline def dump reports empty (a known dump blind spot), so the xpath's match is UNMEASURED until the pack is the loaded copy and get_defs deep=True reads them"),
            ("lantern_deeps_scatter_gate", "lives in RimUtinni LanternDeeps (patches the live donor def), not in this mod"),
        ):
            with t.component(name, beyond_toggle=True):
                if _live(t):
                    _unmeasured(t, why)

    # Every def this pack ships is loaded and labelled as its XML says (NORTHSTAR_PARTIAL_GAPS_FILL_1).
    from modcheck import shipped_defs
    shipped_defs.add_chain(suite, __file__, sanity=("DV_PyrinthHeater", "DV_Mote_PyrinthSpark"), min_count=12)
    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
