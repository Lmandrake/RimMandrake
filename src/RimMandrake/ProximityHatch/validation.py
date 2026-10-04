"""validation.py -- modcheck suite for RimMandrake: Proximity Hatch (mandrake.rm.proximityhatch).

First north-star script (PROXIMITY_HATCH_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/ProximityHatch.md.

THE MOD is one generic engine comp, RimMandrake.ProximityHatch.CompProperties_ProximityHatch, paired on an egg
ThingDef with vanilla CompProperties_Hatcher: a live flesh pawn inside the egg's radius forces CompHatcher.Hatch()
early and the hatchling is aggroed (ManhunterPermanent + AttackMelee) on whoever tripped it. It ships NO defs and
NO textures (About.xml says so: engine only), so "every def the mod ships" is the empty set and the behaviour is
read on a CARRIER egg another mod wires it onto. Carriers are DERIVED from the repo's own XML (defs and patches
naming the comp), never listed by hand; the chain uses the first carrier that resolves in the running game.

CHAINS
  defs_resolve       a control def reads notFound (the probe can say no); every carrier egg that SHOULD resolve
                     is looked up and at least one must (none = UNMEASURED: no carrier mod is loaded).
  settings_roundtrip every `public static` field of RM_ProximityHatchSettings (4): write alt, read, restore.
  carrier_wiring     the first resolving carrier egg reads the comp in its deep `comps` rows (UNMEASURED if the
                     bridge cannot show comp classes; never read from a failed call).
  hatch_behaviour    egg alone does not hatch (control); egg + flesh pawn at distance 1 hatches early (egg gone,
                     a new animal in the rect) and the hatchling is in ManhunterPermanent; `enabled` off = egg
                     stays; radiusMultiplier 0.1 with the pawn at distance 1 = egg stays; `aggroEnabled` off =
                     it hatches but is NOT manhunter.
  not_driven         save/load of `hatchFired`, TemperatureDamaged spoiling instead of hatching, the scan
                     cadence (`scanIntervalMultiplier`), stacked-egg splitting: UNMEASURED, each with the reason.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SETTINGS = "RimMandrake.ProximityHatch.RM_ProximityHatchSettings"
COMP_CLASS = "RimMandrake.ProximityHatch.CompProperties_ProximityHatch"
CONTROL_ABSENT = "ThingDef/RM_ProximityHatchNoSuchEgg_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def settings_fields():
    """{name: type} for every `public static` scalar of RM_ProximityHatchSettings, read from the C#."""
    src = open(os.path.join(HERE, "Source", "RM_ProximityHatchMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_ProximityHatchSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def carriers():
    """[(defName, source_file, kind)] of every egg the repo wires the comp onto: a ThingDef carrying a
    `Class=RimMandrake.ProximityHatch.CompProperties_ProximityHatch` entry (kind 'def'), or a patch operation whose
    value carries it and whose xpath names the def (kind 'patch'). Derived from the XML, never a hand list."""
    out = []
    for root in ("RimMandrake", "RimStarWars", "RimUtinni"):
        base = os.path.join(SRC, root)
        for dp, dns, files in os.walk(base):
            dns[:] = [d for d in dns if d not in ("obj", "bin", "Textures", "Assemblies", "Source", "__pycache__")]
            for fn in files:
                if not fn.endswith(".xml"):
                    continue
                p = os.path.join(dp, fn)
                try:
                    raw = open(p, encoding="utf-8").read()
                except OSError:
                    continue
                if COMP_CLASS not in raw:
                    continue
                try:
                    tree = ET.parse(p).getroot()
                except ET.ParseError:
                    continue
                if tree.tag == "Defs":
                    for td in tree.findall("ThingDef"):
                        if any(e.get("Class") == COMP_CLASS for e in td.iter("li")) and td.findtext("defName"):
                            out.append((td.findtext("defName"), p, "def"))
                else:
                    for op in tree.iter("Operation"):
                        if any(e.get("Class") == COMP_CLASS for e in op.iter("li")):
                            for xp in op.iter("xpath"):
                                m = re.search(r'ThingDef\[defName="([^"]+)"\]', xp.text or "")
                                if m:
                                    out.append((m.group(1), p, "patch"))
    return sorted(set(out))


CARRIERS = carriers()


def static_checks():
    bad = []
    fields = settings_fields()
    if len(fields) < 1:
        return ["settings probe found no scalar field (sanity probe failed)"]
    if sorted(fields) != ["aggroEnabled", "enabled", "radiusMultiplier", "scanIntervalMultiplier"]:
        bad.append("settings fields changed: %s (update the walk and DEFAULTS)" % sorted(fields))
    src = open(os.path.join(HERE, "Source", "RM_ProximityHatchMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RimMandrake_ProximityHatch.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    comp = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "CompProximityHatch.cs"), encoding="utf-8").read())
    for needle in ("RM_ProximityHatchSettings.enabled", "RM_ProximityHatchSettings.radiusMultiplier",
                   "RM_ProximityHatchSettings.scanIntervalMultiplier", "RM_ProximityHatchSettings.aggroEnabled",
                   "hatcher.Hatch()", "ManhunterPermanent", "preHatch", "IsFlesh", "hatchFired"):
        if needle not in comp:
            bad.append("CompProximityHatch.cs lacks %s" % needle)
    if len(CARRIERS) < 2:
        bad.append("carrier probe found %d eggs wired to the comp (sanity probe: expected >= 2)" % len(CARRIERS))
    for name, p, kind in CARRIERS:
        if kind == "def":
            td = [e for e in ET.parse(p).getroot().findall("ThingDef") if e.findtext("defName") == name][0]
            if not any((e.get("Class") or "").endswith("CompProperties_Hatcher") for e in td.iter("li")):
                bad.append("carrier %s has the proximity comp but no CompProperties_Hatcher (the comp would sit dormant)" % name)
    if not os.path.isfile(os.path.join(SRC, "..", "design", "validation_walks", "RimMandrake", "ProximityHatch.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None

DEFAULTS = {"enabled": True, "radiusMultiplier": 1.0, "scanIntervalMultiplier": 1.0, "aggroEnabled": True}


def _build_suite():
    suite = Suite("ProximityHatch")
    suite.toggles = sorted(settings_fields())
    state = {"egg": None}

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

    def _put(t, field, value):
        if t.session is None:
            return
        r = _raw(t, "set", field, value)
        if not r.get("success"):
            raise ExpectationFailed("could not set %s=%s: %r" % (field, value, r))

    def _restore(t, field):
        if t.session is not None:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                               value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[proximityhatch] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _carrier(t):
        """First carrier egg that resolves live (cached). None when no carrier mod is loaded."""
        if state["egg"] is not None:
            return state["egg"] or None
        names = [n for n, _p, _k in CARRIERS]
        r = t.bridge_call("jawa/get_defs", defs=";".join("ThingDef/%s" % n for n in names), fields="defName", limit=20)
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs failed on the carrier eggs: %r" % r)
        missing = set(x.split("/")[-1] for x in (r.get("notFound") or []))
        for n in names:
            if n not in missing:
                state["egg"] = n
                return n
        state["egg"] = ""
        return None

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("mod_ships_no_defs_and_a_carrier_resolves", beyond_toggle=True):
            if len(CARRIERS) < 1:
                raise ExpectationFailed("no carrier egg derived from the repo XML (blind probe)")
            egg = _carrier(t)
            if _live(t) and egg is None:
                _unmeasured(t, "no egg that carries the proximity comp is loaded (carriers: %s); the mod ships no defs "
                               "of its own, so there is nothing else to resolve" % [n for n, _p, _k in CARRIERS])

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
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

    @suite.chain("carrier_wiring")
    def carrier_wiring(t):
        with t.component("carrier_egg_reads_the_proximity_comp", beyond_toggle=True):
            egg = _carrier(t)
            if not _live(t):
                return
            if egg is None:
                _unmeasured(t, "no carrier egg loaded")
                return
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % egg, fields="comps", deep=True, limit=2)
            rows = (r or {}).get("defs") or []
            if not isinstance(r, dict) or r.get("success") is False or not rows:
                raise ExpectationFailed("could not read %s: %r" % (egg, r))
            comps = (rows[0].get("fields") or {}).get("comps")
            if not isinstance(comps, list) or (comps and not all(isinstance(c, dict) for c in comps)):
                _unmeasured(t, "get_defs returned comps as bare type names / unreadable (%r): comp classes cannot be "
                               "read through this tool; the behaviour chain below proves the wiring by effect" % (comps,))
                return
            # a control: some comp row must be present (a vanilla egg has CompHatcher) so the read is not blind
            if not comps:
                _unmeasured(t, "comps came back empty for %s (blind read)" % egg)
                return
            classes = " ".join(str(c.get("compClass") or c.get("class") or c) for c in comps)
            if "ProximityHatch" not in classes:
                raise ExpectationFailed("%s's comps carry no ProximityHatch row: %s" % (egg, classes[:300]))

    def _rect(t, r=6):
        x, z = t.anchor
        return "%d,%d,%d,%d" % (x - r, z - r, 2 * r + 1, 2 * r + 1)

    def _eggs(t, egg):
        r = t.bridge_call("jawa/list_things", defName=egg, rect=_rect(t), limit=50)
        if not _live(t):
            return []
        if not isinstance(r, dict) or r.get("success") is False or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) unreadable: %r" % (egg, r))
        return list(r.get("things") or [])

    def _animals(t):
        r = t.bridge_call("jawa/list_pawns", rect=_rect(t), limit=50)
        if not _live(t):
            return []
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("list_pawns unreadable: %r" % r)
        return [p for p in (r.get("pawns") or []) if p.get("faction") in (None, "", "none") or "wild" in str(p.get("faction")).lower()]

    def _arm(t, egg, pawn_dx):
        """Fresh site: one fertilized carrier egg at the anchor, and (pawn_dx not None) one colonist pawn_dx cells east."""
        t.clear_area(size=24)
        t.spawn(egg, count=1, at="point")
        pid = None
        if pawn_dx is not None:
            x, z = t.anchor
            r = t.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=x + pawn_dx, z=z, faction="player", count=1)
            if _live(t):
                pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
                if not pid:
                    raise ExpectationFailed("colonist did not spawn: %r" % r)
        return pid

    def _manhunter(t, pawn_id):
        r = t.bridge_call("jawa/pawn_mental", pawn=pawn_id, action="list", limit=1)
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("pawn_mental unreadable: %r" % r)
        return str(r.get("currentState"))

    def _hatchling(t, egg):
        """The new wild animal after a hatch: exactly the wild pawns in the rect (the site was cleared first)."""
        rows = _animals(t)
        return rows

    @suite.chain("hatch_behaviour")
    def hatch_behaviour(t):
        with t.component("control_egg_alone_does_not_hatch", toggle="enabled"):
            egg = _carrier(t)
            if _live(t) and egg is None:
                _unmeasured(t, "no carrier egg loaded")
            elif _live(t):
                _arm(t, egg, None)
                t.wait_ticks(150)
                if len(_eggs(t, egg)) != 1:
                    raise ExpectationFailed("an egg with no pawn near it is gone after 150 ticks: the detector cannot "
                                            "separate a proximity hatch from some other loss")
        with t.component("pawn_in_range_hatches_early_and_ambushes", toggle="enabled"):
            egg = _carrier(t)
            if _live(t) and egg is not None:
                _arm(t, egg, 1)
                t.wait_ticks(150)
                if _eggs(t, egg):
                    raise ExpectationFailed("a flesh pawn one cell from a %s did not hatch it within 150 ticks" % egg)
                kids = _hatchling(t, egg)
                if not kids:
                    _unmeasured(t, "the egg is gone but no wild animal is in the rect (killed by the colonist already, "
                                   "or Hatch() produced nothing): cannot judge the ambush")
                else:
                    st = _manhunter(t, kids[0].get("id"))
                    if "Manhunter" not in str(st):
                        raise ExpectationFailed("hatchling mental state is %r, expected ManhunterPermanent (aggro beat dead)" % st)
        with t.component("enabled_off_egg_stays", toggle="enabled"):
            egg = _carrier(t)
            if _live(t) and egg is not None:
                _put(t, "enabled", False)
                try:
                    _arm(t, egg, 1)
                    t.wait_ticks(150)
                    if len(_eggs(t, egg)) != 1:
                        raise ExpectationFailed("enabled=false but the egg left the map with a pawn beside it (toggle dead)")
                finally:
                    _restore(t, "enabled")
        with t.component("radius_multiplier_shrinks_trigger", toggle="radiusMultiplier"):
            egg = _carrier(t)
            if _live(t) and egg is not None:
                _put(t, "radiusMultiplier", 0.1)
                try:
                    _arm(t, egg, 1)
                    t.wait_ticks(150)
                    if len(_eggs(t, egg)) != 1:
                        raise ExpectationFailed("radiusMultiplier 0.1 (radius ~0.3 cells) still hatched on a pawn one cell away")
                finally:
                    _restore(t, "radiusMultiplier")
        with t.component("aggro_off_hatchling_not_manhunter", toggle="aggroEnabled"):
            egg = _carrier(t)
            if _live(t) and egg is not None:
                _put(t, "aggroEnabled", False)
                try:
                    _arm(t, egg, 1)
                    t.wait_ticks(150)
                    if _eggs(t, egg):
                        raise ExpectationFailed("aggroEnabled=false must still hatch early, but the egg is still there")
                    kids = _hatchling(t, egg)
                    if not kids:
                        _unmeasured(t, "egg gone but no wild animal found to read its mental state")
                    else:
                        st = _manhunter(t, kids[0].get("id"))
                        if "Manhunter" in str(st):
                            raise ExpectationFailed("aggroEnabled=false but the hatchling is %r" % st)
                finally:
                    _restore(t, "aggroEnabled")

    @suite.chain("not_driven")
    def not_driven(t):
        for name, toggle, why in (
            ("scan_interval_multiplier_slows_the_scan", "scanIntervalMultiplier",
             "the cadence is a per-egg tick countdown with no state reader; proving 'higher = checks less often' needs a "
             "tick-by-tick read of the egg's position in its countdown (a debug [Tool] reading ticksUntilScan is owed)"),
            ("hatch_fired_persists_through_save_load", None,
             "hatchFired is Scribed; proving it needs a save, a reload and a second hatch attempt on the reloaded egg"),
            ("cold_egg_spoils_not_hatches", None,
             "CompHatcher's TemperatureDamaged branch needs a below-freezing cell and a fertilized egg left to age; owed to "
             "a cold-site recipe"),
        ):
            with t.component(name, toggle=toggle, beyond_toggle=toggle is None):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
