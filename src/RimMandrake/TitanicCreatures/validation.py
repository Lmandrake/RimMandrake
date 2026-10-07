"""validation.py -- modcheck suite for RimMandrake: Titanic Creatures (mandrake.rm.titaniccreatures).

First north-star script (TITANIC_CREATURES_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TitanicCreatures.md.

THE MOD is an ENGINE (About.xml: "No creature in this mod list is wired to it here"): a size tier by bodySize
(T1 >= 4, T2 >= 8, T3 >= 20, from RM_TitanicTierDef) that auto-attaches CompTitanicWake to every qualifying race,
a destruction wake (a curated RM_CrushRuleDef table crushes plants at T1, walls/buildings at T2+, never chunks;
thin roofs holed at T2+; a rubble trail from T1), thick-roof path avoidance, a butcher-yield curve for T1-T2, and a
T3 corpse that becomes a harvestable landmark (RM_TitanicCorpseSite + RM_HarvestTitanicCorpse). Footprint rides
Large Pawns when present (soft reflection bridge).

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML) resolves; a control name reads notFound.
  settings_roundtrip every `public static` bool/int/float of RM_TitanicCreaturesSettings (12), numerically compared.
  tier_ladder        the live RM_TitanicTierDef thresholds equal the XML's and are strictly ascending.
  crush_rules        each RM_CrushRuleDef's `crushable` and `minTier` read back as the XML says (chunks protected).
  harmony            the four Harmony patches (Thing.set_Position wake, Pawn_PathFollower.CostToMoveIntoCell roof
                     avoidance, Corpse.SpawnSetup site conversion, Pawn.ButcherProducts yield curve) carry a postfix
                     owned by mandrake.rm.titaniccreatures.
  wake               an Elephant (a T1 race) walking a lane leaves a rubble trail and tramples fragile plants; a Rat
                     on a parallel lane does neither (control); `wakeEnabled` off = neither.
  not_driven         T2 roof holing and wall crushing, T3 corpse site + harvest, butcher-yield curve, roof-avoidance
                     pathing, the Large Pawns footprint: UNMEASURED, each with its reason.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.TitanicCreatures.RM_TitanicCreaturesSettings"
HARMONY_ID = "mandrake.rm.titaniccreatures"
CONTROL_ABSENT = "ThingDef/RM_TitanicNoSuchDef_ZZ"
BEAST = "Elephant"          # vanilla race with baseBodySize 4 (the T1 floor); gated by a live BodySize read
CONTROL = "Rat"
PLANT = "Plant_Grass"
FILTH = "Filth_RubbleRock"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
DEFAULTS = {"wakeEnabled": True, "wakeCrushDamageMultiplier": 1.0, "wakeFilthTrailChance": 0.35,
            "roofAvoidanceEnabled": True, "yieldCurveEnabled": True, "yieldCurveMinFactor": 0.15,
            "corpseSiteEnabled": True, "corpseSiteHarvestMeatPerSession": 25, "corpseSiteHarvestLeatherPerSession": 10,
            "corpseSiteMeatSpoilagePerDay": 0.15, "corpseSiteLeatherSpoilagePerDay": 0.08,
            "corpseSiteWorkHoursPerSession": 1.0}
PATCHES = [("Thing", "set_Position", "Patch_Thing_Position_Wake.cs"),
           ("Pawn_PathFollower", "CostToMoveIntoCell", "Patch_ThickRoofAvoidance.cs"),
           ("Corpse", "SpawnSetup", "Patch_CorpseSiteConversion.cs"),
           ("Pawn", "ButcherProducts", "Patch_ButcherYieldCurve.cs")]


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML (never a hand list)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RM_TitanicCreaturesSettings.cs"), encoding="utf-8").read()
    body = src.split("class RM_TitanicCreaturesSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def tier_xml():
    r = ET.parse(os.path.join(HERE, "Defs", "TitanicTierDefs", "RM_TitanicTierDef.xml")).getroot()[0]
    return dict((k, float(r.findtext(k))) for k in ("t1MinBodySize", "t2MinBodySize", "t3MinBodySize"))


def crush_xml():
    """{defName: {'crushable': 'true', 'minTier': 'T2'}} from the XML."""
    r = ET.parse(os.path.join(HERE, "Defs", "CrushRuleDefs", "RM_CrushRules.xml")).getroot()
    return dict((e.findtext("defName"), {"crushable": e.findtext("crushable"), "minTier": e.findtext("minTier")}) for e in r)


def static_checks():
    bad = []
    if len(SHIPPED) < 6:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    if sorted(fields) != sorted(DEFAULTS):
        bad.append("settings fields changed: %s (update DEFAULTS and the walk)" % sorted(set(fields) ^ set(DEFAULTS)))
    src = open(os.path.join(HERE, "Source", "RM_TitanicCreaturesSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    for ty, name, f in PATCHES:
        p = None
        for dp, _d, files in os.walk(os.path.join(HERE, "Source")):
            if f in files:
                p = os.path.join(dp, f)
        if p is None:
            bad.append("patch file %s gone" % f)
        elif ty not in open(p, encoding="utf-8").read():
            bad.append("%s no longer patches %s" % (f, ty))
    t = tier_xml()
    if not (0 < t["t1MinBodySize"] < t["t2MinBodySize"] < t["t3MinBodySize"]):
        bad.append("tier thresholds not ascending: %r" % t)
    cr = crush_xml()
    if len(cr) < 4 or cr.get("RM_Crush_Chunks", {}).get("crushable") != "false":
        bad.append("crush table probe read %r (expected 4 rows, chunks protected)" % sorted(cr))
    if len([1 for ty, _n in SHIPPED if ty.endswith("RM_CrushRuleDef")]) != len(cr):
        bad.append("crush rule count differs between the defs probe and the table probe")
    mod = open(os.path.join(HERE, "Source", "RM_TitanicCreaturesMod.cs"), encoding="utf-8").read()
    if 'HarmonyId = "%s"' % HARMONY_ID not in mod:
        bad.append("Harmony id is no longer %s (the harmony chain asserts it)" % HARMONY_ID)
    wake = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "Wake", "TitanicWakeProcessor.cs"), encoding="utf-8").read())
    for needle in ("wakeEnabled", "wakeCrushDamageMultiplier", "wakeFilthTrailChance", "Filth_RubbleRock", "isThickRoof"):
        if needle not in wake:
            bad.append("TitanicWakeProcessor.cs lacks %s" % needle)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "TitanicCreatures.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


class _patient(object):
    """Raise the bridge client's per-reply socket timeout (30 s) for a slow job order, then restore it
    (the Contagion/validation.py pattern). A mock session without a real socket is left alone."""
    def __init__(self, t, secs=240.0):
        self.rb = getattr(getattr(t, "session", None), "_rb", None)
        self.secs, self.old = secs, None

    def __enter__(self):
        if self.rb is not None and hasattr(self.rb, "timeout"):
            self.old = self.rb.timeout
            self.rb.timeout = self.secs
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.secs)
        return self

    def __exit__(self, *a):
        if self.old is not None:
            self.rb.timeout = self.old
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.old)
        return False


def _build_suite():
    suite = Suite("TitanicCreatures")
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

    def _put(t, field, value):
        if t.session is None:
            return
        if not _raw(t, "set", field, value).get("success"):
            raise ExpectationFailed("could not set %s=%s" % (field, value))

    def _restore(t, field):
        if t.session is not None:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                               value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[titanic] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=40)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%s of %d defs resolved; notFound=%r" % (r.get("foundCount"), len(names), r.get("notFound")))

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
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
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

    @suite.chain("tier_ladder")
    def tier_ladder(t):
        with t.component("thresholds_match_xml_and_ascend", beyond_toggle=True):
            exp = tier_xml()
            r = t.bridge_call("jawa/get_defs", defs="RimMandrake.TitanicCreatures.RM_TitanicTierDef/RM_TitanicTiers_Default",
                              fields="t1MinBodySize,t2MinBodySize,t3MinBodySize", limit=2)
            if not _live(t):
                return
            rows = (r or {}).get("defs") or []
            if not isinstance(r, dict) or r.get("success") is False or not rows:
                raise ExpectationFailed("could not read the tier def: %r" % r)
            f = rows[0].get("fields") or {}
            try:
                got = dict((k, float(f.get(k))) for k in exp)
            except (TypeError, ValueError):
                _unmeasured(t, "tier fields did not come back numeric: %r" % (f,))
                return
            for k in exp:
                if abs(got[k] - exp[k]) > 1e-4:
                    raise ExpectationFailed("%s is %s live but %s in the XML (stale deploy?)" % (k, got[k], exp[k]))
            if not got["t1MinBodySize"] < got["t2MinBodySize"] < got["t3MinBodySize"]:
                raise ExpectationFailed("tier thresholds not ascending live: %r" % got)

    @suite.chain("crush_rules")
    def crush_rules(t):
        exp = crush_xml()
        with t.component("rules_read_back_as_the_xml_says", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=";".join("RimMandrake.TitanicCreatures.RM_CrushRuleDef/%s" % n for n in sorted(exp)),
                              fields="crushable,minTier", limit=10)
            if not _live(t):
                return
            rows = dict((d.get("defName"), d.get("fields") or {}) for d in ((r or {}).get("defs") or []))
            if not isinstance(r, dict) or r.get("success") is False or not rows:
                raise ExpectationFailed("could not read the crush rules: %r" % r)
            for name, want in sorted(exp.items()):
                got = rows.get(name)
                if got is None:
                    raise ExpectationFailed("rule %s did not come back" % name)
                if str(got.get("crushable")).lower() != want["crushable"].lower():
                    raise ExpectationFailed("%s crushable is %r live, %r in the XML" % (name, got.get("crushable"), want["crushable"]))
                if str(got.get("minTier")) != want["minTier"]:
                    raise ExpectationFailed("%s minTier is %r live, %r in the XML" % (name, got.get("minTier"), want["minTier"]))
            if str(rows.get("RM_Crush_Chunks", {}).get("crushable")).lower() != "false":
                raise ExpectationFailed("chunks must stay protected (crushable false)")

    @suite.chain("harmony")
    def harmony(t):
        for ty, name, _f in PATCHES:
            with t.component("%s_%s_postfix_attached" % (ty, name), beyond_toggle=True):
                r = t.bridge_call("jawa/harmony_patches", typeName=ty, methodName=name)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked about %s.%s: %s" % (ty, name, str(r)[:160]))
                    continue
                methods = r.get("methods") or []
                if not methods:
                    _unmeasured(t, "harmony_patches returned no method for %s.%s (a property setter or overload the tool "
                                   "does not resolve): %s" % (ty, name, str(r)[:160]))
                    continue
                owners = []
                for m in methods:
                    for kind in ("postfixes", "prefixes"):
                        owners.extend(p.get("owner") for p in (m.get(kind) or []))
                if HARMONY_ID not in owners:
                    raise ExpectationFailed("%s.%s carries no patch owned by %s (owners: %s)"
                                            % (ty, name, HARMONY_ID, sorted(set(o for o in owners if o))[:8]))

    def _rect(t, x0, z0, w, h):
        return "%d,%d,%d,%d" % (x0, z0, w, h)

    def _count(t, defName, rect):
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=200)
        if not _live(t):
            return 0
        if not isinstance(r, dict) or r.get("success") is False or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) unreadable: %r" % (defName, r))
        return int(r.get("countMatched"))

    def _lane(t, kind, dz):
        """Spawn `kind` at the lane start, with fragile plants down the lane; order it east. Returns
        (pawn_id, lane_rect, confirmed_running)."""
        x, z = t.anchor
        lz = z + dz
        r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=lz, faction="none", count=1)
        pid = (((r or {}).get("pawns") or [{}])[0]).get("id") if _live(t) else None
        if _live(t) and not pid:
            raise ExpectationFailed("%s did not spawn: %r" % (kind, r))
        for dx in range(3, 15, 2):
            t.bridge_call("jawa/spawn_batch", ops="%s:%d,%d" % (PLANT, x + dx, lz))
        rect = _rect(t, x, lz, 16, 1)
        if _live(t):
            rows = (t.bridge_call("jawa/list_things", defName=PLANT, rect=rect, limit=50) or {}).get("things") or []
            for row in rows:     # one blow of 20 must be enough to kill a trampled plant
                t.bridge_call("jawa/set_thing_props", thing=row["id"], hitPoints=5)
        return pid, rect, x, lz

    def _walk(t, pid, x, lz):
        with _patient(t):
            job = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="Goto", targetAX=x + 15, targetAZ=lz,
                                waitTicks=0, timeoutSeconds=60)
        return bool(isinstance(job, dict) and job.get("nowRunningRequested"))

    def _tier_ok(t, pid):
        """UNMEASURED-gate: the beast must really be tier T1 (BodySize >= 4); an unreadable stat proceeds."""
        r = t.bridge_call("jawa/pawn_stats", pawn=pid, stats="BodySize", limit=4)
        if not _live(t) or not isinstance(r, dict):
            return True
        rows = r.get("stats") or []
        for row in rows if isinstance(rows, list) else []:
            if isinstance(row, dict) and "BodySize" in str(row.get("stat") or row.get("defName") or row.get("name")):
                try:
                    return float(row.get("value")) >= tier_xml()["t1MinBodySize"]
                except (TypeError, ValueError):
                    return True
        return True

    SITE = 60            # cleared square (half 30): the control lane sits CTL_DZ cells away, well inside it
    CTL_DZ = 22          # control lane offset; the Elephant wanders after its Goto, so 6 cells polluted the Rat lane

    def _sweep_filth(t):
        """Wipe every Filth thing in the cleared site (clear_area's own pass did not remove Filth_RubbleRock)."""
        x, z = t.anchor
        h = SITE // 2
        t.bridge_call("jawa/destroy_batch", rects=_rect(t, x - h, z - h, SITE, SITE), categories="Filth")

    def _run(t, with_control=True):
        """One lane run. with_control=False leaves the Elephant the only creature we placed (the off/multiplier
        components judge the beast alone, so no second walker can drop rubble into its rect)."""
        t.clear_area(size=SITE)
        _sweep_filth(t)
        beast, brect, bx, bz = _lane(t, BEAST, 0)
        ctl = crect = cx = cz = None
        if with_control:
            ctl, crect, cx, cz = _lane(t, CONTROL, CTL_DZ)
        if not _live(t):
            return None
        _sweep_filth(t)      # ambient tiered wanderers scatter rubble map-wide; start from zero right before the walk
        if _count(t, FILTH, _rect(t, bx - 1, bz - 2, 18, 5)) != 0 or \
                (with_control and _count(t, FILTH, _rect(t, cx - 1, cz - 2, 18, 5)) != 0):
            _unmeasured(t, "rubble filth still on a test lane after clear_area + Filth sweep: no clean baseline")
            return None
        if not _tier_ok(t, beast):
            _unmeasured(t, "a spawned %s reads BodySize < the T1 floor: this race is not tiered, so a wake is not expected" % BEAST)
            return None
        ok1 = _walk(t, beast, bx, bz)
        ok2 = _walk(t, ctl, cx, cz) if with_control else True
        if not (ok1 and ok2):
            _unmeasured(t, "ordered Goto not confirmed running (beast %s, control %s): no walker, so no wake can be judged"
                           % (ok1, ok2))
            return None
        t.wait_ticks(500)
        m = {"beast_filth": _count(t, FILTH, _rect(t, bx, bz - 1, 16, 3)), "beast_plants": _count(t, PLANT, brect)}
        if with_control:
            m["ctl_filth"] = _count(t, FILTH, _rect(t, cx, cz - 1, 16, 3))
            m["ctl_plants"] = _count(t, PLANT, crect)
        return m

    @suite.chain("wake")
    def wake(t):
        with t.component("t1_beast_trails_rubble_and_tramples_plants", toggle="wakeEnabled"):
            m = _run(t) if _live(t) else None
            if m is not None:
                if m["ctl_filth"] != 0 or m["ctl_plants"] != 6:
                    _unmeasured(t, "the un-tiered control (%s) left filth or lost plants (%r): the lane is not clean, so the "
                                   "differential is invalid" % (CONTROL, m))
                elif m["beast_filth"] < 1:
                    raise ExpectationFailed("a %s walked a 15-cell lane and left no rubble (0.35 chance per cell step makes "
                                            "this ~1 in 10^3): %r" % (BEAST, m))
                elif m["beast_plants"] >= 6:
                    raise ExpectationFailed("a %s walked over six 5-HP plants and crushed none: %r" % (BEAST, m))
        with t.component("wake_off_leaves_no_trail", toggle="wakeEnabled"):
            if _live(t):
                _put(t, "wakeEnabled", False)
                try:
                    m = _run(t, with_control=False)
                    if m is not None and (m["beast_filth"] != 0 or m["beast_plants"] != 6):
                        raise ExpectationFailed("wakeEnabled=false but the %s still left a wake (toggle dead): %r" % (BEAST, m))
                finally:
                    _restore(t, "wakeEnabled")
        with t.component("crush_damage_multiplier_scales_the_blow", toggle="wakeCrushDamageMultiplier"):
            if _live(t):
                _put(t, "wakeCrushDamageMultiplier", 0.1)
                try:
                    m = _run(t, with_control=False)
                    # 20 x 0.1 = 2 damage against 5-HP plants: they must survive (control for the 1x kill above)
                    if m is not None and m["beast_plants"] < 6:
                        raise ExpectationFailed("multiplier 0.1 (2 damage) still destroyed 5-HP plants: %r" % (m,))
                finally:
                    _restore(t, "wakeCrushDamageMultiplier")

    @suite.chain("not_driven")
    def not_driven(t):
        for name, toggle, why in (
            ("t2_holes_thin_roofs_and_crushes_walls", "wakeEnabled",
             "needs a race of bodySize >= 8; no vanilla race qualifies and this mod wires none (campaign content). A "
             "bridge tool to force a pawn's size, or a wired T2 creature, is owed"),
            ("t3_corpse_becomes_a_harvest_site", "corpseSiteEnabled",
             "needs a bodySize >= 20 corpse and several harvest work sessions; no race qualifies in a mod-only list"),
            ("butcher_yield_curve_reduces_t1_t2_yield", "yieldCurveEnabled",
             "needs a butcher job on a tiered corpse compared with an untiered same-mass control"),
            ("thick_roof_cost_penalty_steers_paths", "roofAvoidanceEnabled",
             "needs an overhead-mountain roof and a path-cost read; the harmony chain proves the patch is attached only"),
            ("large_pawns_footprint_bridge", None,
             "soft reflection into neku.largepawns; needs that mod loaded and a multi-cell OccupiedRect read"),
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
