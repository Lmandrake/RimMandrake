"""validation.py -- modcheck suite for RimMandrake: Huge Things (mandrake.rm.hugethings).

One mod since 2026-10-07: Titanic Creatures (mandrake.rm.titaniccreatures, retired) merged into it, owner's words
"Merge into one mod called Huge Things". First scripts: HUGE_THINGS_FOOTPRINT_1 and TITANIC_CREATURES_FIRST_SCRIPT_1.
Walk: design/validation_walks/RimMandrake/HugeThings.md. Designs: design/RimMandrake/giant_footprint_design_2026-10-07.md,
Transient merge design 2026-10-07 (commit 2ba286b2f).

THE MOD is an ENGINE with two halves under two master toggles (Mod Settings `giantPlantsEnabled`, `giantAnimalsEnabled`):
  giant plants   a plant carrying RM_HugePlantExtension is solid where its art touches the ground (invisible impassable
                 RM_HugeTrunkBlocker edifices on the contact cells measured by measure_huge_plant_masks.py), selected anywhere on
                 its drawn picture, gives partial cover and forwards hits to the plant; items under a growing trunk are pushed.
  giant animals  a race carrying RM_HugePawnExtension gets a click area the size of its drawn body; a race of bodySize >= T1
                 (RM_TitanicTierDef 4 / 8 / 20, or the Mod Settings custom ladder) is a titan: CompTitanicWake auto-attached, a
                 destruction wake (curated RM_CrushRuleDef table; plants at T1, walls/buildings at T2+, chunks and giant trunks
                 never; thin roofs holed at T2+; rubble from T1), a thick-roof slow-down, a butcher-yield curve for T1-T2, a T3
                 corpse site (RM_TitanicCorpseSite + RM_HarvestTitanicCorpse). Footprint rides Large Pawns by reflection.
  the seam       titans at or above `giantPlantSmashMinTier` (T3 by default) smash giant plants they brush (one heavy crush per
                 step per giant, through Building_TrunkBlocker.ForwardToPlant); smaller titans go around trunks as walls.

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML) resolves; a control name reads notFound.
  settings_roundtrip every `public static` bool/int/float of RM_HugeThingsSettings, numerically compared.
  harmony            Thing.get_CustomRectForSelector carries a postfix owned by mandrake.rm.hugethings.
  harmony_titans     the four titan patches carry a patch owned by mandrake.rm.titaniccreatures (the Harmony id string the
                     titan half kept on purpose: it is a patch owner name, not a packageId).
  trunk              a full-grown brommok timber (RM_Nogtyl) gets one of its variants' measured contact counts and none south of
                     it; a young one none; `plantTrunkEnabled` off clears them; cutting the plant removes them.
  tier_ladder        the live RM_TitanicTierDef thresholds equal the XML's and ascend.
  crush_rules        each RM_CrushRuleDef reads back as the XML says (chunks and the giant trunk protected).
  wake               an Elephant (T1) walking a lane leaves rubble and tramples fragile plants; a Rat does neither; `wakeEnabled`
                     off = neither; the crush multiplier scales the blow.
  not_driven         click selection, pawn hitbox, save/load re-link, T2 roofs/walls, T3 corpse site, yield curve, roof
                     slow-down, Large Pawns footprint, the titan-vs-giant smash: UNMEASURED, each with its reason.

LIST: needs mandrake.rm.biomes (TheRot folded in) beside this mod for RM_Nogtyl. STATIC: `python3 validation.py`
-> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.HugeThings.RM_HugeThingsSettings"
HARMONY_ID = "mandrake.rm.hugethings"
TITAN_HARMONY_ID = "mandrake.rm.titaniccreatures"   # the titan half's Harmony owner id, kept through the merge on purpose
CONTROL_ABSENT = "ThingDef/RM_HugeNoSuchDef_ZZ"
BLOCKER = "RM_HugeTrunkBlocker"
GIANT = "RM_Nogtyl"          # brommok timber: TheRot's own def (no donor mod needed), 12 cells drawn at full size
REFRESH_TICKS = 300          # settings change marks every plant dirty; RefreshesPerTick per tick + PendingRetryInterval 250
BEAST = "Elephant"          # vanilla race with baseBodySize 4 (the T1 floor); gated by a live BodySize read
CONTROL = "Rat"
PLANT = "Plant_Grass"
FILTH = "Filth_RubbleRock"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=(?!>)\s*([^;]+);")   # not `=>` properties
DEFAULTS = {"giantPlantsEnabled": True, "plantTrunkEnabled": True, "plantSelectionEnabled": True, "plantTrunkScale": 1.0,
            "plantTrunkDamageEnabled": True, "plantItemPushEnabled": True,
            "giantAnimalsEnabled": True, "pawnHitboxEnabled": True, "pawnHitboxScale": 1.0, "largePawnsFootprintEnabled": True,
            "largePawnsClearingOff": True,
            "tierThresholdsCustom": False, "tierT1MinBodySize": 4.0, "tierT2MinBodySize": 8.0, "tierT3MinBodySize": 20.0,
            "wakeEnabled": True, "wakeCrushDamageMultiplier": 1.0, "wakeFilthTrailChance": 0.35, "wakeRoofHolingEnabled": True,
            "giantPlantSmashEnabled": True, "giantPlantSmashMinTier": 3, "roofAvoidanceEnabled": True,
            "yieldCurveEnabled": True, "yieldCurveMinFactor": 0.15,
            "corpseSiteEnabled": True, "corpseSiteHarvestMeatPerSession": 25, "corpseSiteHarvestLeatherPerSession": 10,
            "corpseSiteMeatSpoilagePerDay": 0.15, "corpseSiteLeatherSpoilagePerDay": 0.08,
            "corpseSiteWorkHoursPerSession": 1.0}
PATCHES = [("Thing", "set_Position", "Patch_Thing_Position_Wake.cs"),
           ("Pawn_PathFollower", "CostToMoveIntoCell", "Patch_ThickRoofAvoidance.cs"),
           ("Corpse", "SpawnSetup", "Patch_CorpseSiteConversion.cs"),
           ("Pawn", "ButcherProducts", "Patch_ButcherYieldCurve.cs")]


def read(*parts):
    return open(os.path.join(HERE, *parts), encoding="utf-8").read()


def settings_fields():
    body = read("Source", "RM_HugeThingsSettings.cs").split("class RM_HugeThingsSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


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


def giant_blockers():
    """{variant texture: contact cell count} the Rot patch gives GIANT, read from the patch (never a hand number)."""
    p = os.path.join(HERE, "..", "TheRot", "Patches", "RotGiants_HugeFootprint.xml")
    for op in ET.parse(p).getroot():
        if 'defName="%s"' % GIANT in (op.findtext("xpath") or ""):
            li = op.find("match/value/li")
            return dict((v.findtext("texture"), len(v.findall("contact/li"))) for v in li.findall("variants/li"))
    return None


def tier_xml():
    r = ET.parse(os.path.join(HERE, "Defs", "TitanicTierDefs", "RM_TitanicTierDef.xml")).getroot()[0]
    return dict((k, float(r.findtext(k))) for k in ("t1MinBodySize", "t2MinBodySize", "t3MinBodySize"))


def crush_xml():
    """{defName: {'crushable': 'true', 'minTier': 'T2'}} from the XML."""
    r = ET.parse(os.path.join(HERE, "Defs", "CrushRuleDefs", "RM_CrushRules.xml")).getroot()
    return dict((e.findtext("defName"), {"crushable": e.findtext("crushable"), "minTier": e.findtext("minTier")}) for e in r)


def _src(name):
    for dp, _d, files in os.walk(os.path.join(HERE, "Source")):
        if name in files and os.sep + "SelfTest" not in dp:
            return os.path.join(dp, name)
    return None


def static_checks():
    bad = []
    defs = SHIPPED
    if len(defs) < 7:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(defs)]
    for need in (("ThingDef", BLOCKER), ("ThingDef", "RM_TitanicCorpseSite"), ("JobDef", "RM_HarvestTitanicCorpse")):
        if need not in defs:
            bad.append("%s %s not shipped" % need)
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    if sorted(fields) != sorted(DEFAULTS):
        bad.append("settings fields changed: %s (update DEFAULTS and the walk)" % sorted(set(fields) ^ set(DEFAULTS)))
    src = read("Source", "RM_HugeThingsSettings.cs")
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n, ty in fields.items():
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
        m = re.search(r"public\s+static\s+\w+\s+%s\s*=\s*([^;]+);" % n, src)
        v = m.group(1).strip().rstrip("f") if m else None
        want = DEFAULTS.get(n)
        if v is not None and want is not None and (str(want).lower() != v.lower() if ty == "bool" else abs(float(v) - float(want)) > 1e-6):
            bad.append("settings field %s defaults to %s, DEFAULTS says %s (defaults = shipped behaviour)" % (n, v, want))
    # every *Active gate names its master: giant plants or giant animals
    for prop, master in re.findall(r"public static bool (\w+Active) => HugeGates\.\w+\((\w+),", src):
        if master not in ("giantPlantsEnabled", "giantAnimalsEnabled"):
            bad.append("%s is not gated by a master toggle (%s)" % (prop, master))
    core = read("Source", "HugeThingsCore.cs")
    if 'HarmonyId = "%s"' % HARMONY_ID not in core:
        bad.append("Harmony id is no longer %s" % HARMONY_ID)
    if "PatchAll(" in core or "PatchAll(" in read("Source", "Titanic", "RM_TitanicCreaturesMod.cs"):
        bad.append("an assembly-wide PatchAll is back: both halves would patch every method twice (use PatchNamespace)")
    if "nameof(Thing.CustomRectForSelector), MethodType.Getter" not in core:
        bad.append("the selection postfix no longer targets Thing.CustomRectForSelector's getter")
    mc = read("Source", "MapComponent_HugeFootprints.cs")
    if "PendingRetryInterval = 250" not in mc or "RefreshesPerTick" not in mc:
        bad.append("refresh cadence moved; update REFRESH_TICKS (the toggle-off wait depends on it)")
    for patch, why in (('typeof(ZoneManager), "Notify_NoZoneOverlapThingSpawned"', "blockers would carve zones (GPT #3)"),
                       ('typeof(DamageWorker), "ExplosionDamageThing"', "a blast over N trunk cells would hit nothing / N times"),
                       ("nameof(GravshipPlacementUtility.ClearArea)", "gravship landing policy (GPT #15)"),
                       ("nameof(GenUI.ThingsUnderMouse)", "duplicate mouse candidates (GPT #12)"),
                       ("nameof(Plant.PlantCollected)", "footprint lags harvest (GPT #14)")):
        if patch not in core:
            bad.append("HugeThingsCore lost its patch on %s: %s" % (patch, why))
    blk = read("Source", "Building_TrunkBlocker.cs")
    if "p.TakeDamage(dinfo)" not in blk or "absorbed = true" not in blk or "ForwardToPlant(owner, dinfo, false)" not in blk:
        bad.append("Building_TrunkBlocker no longer forwards hits to its plant (owner ruling 2026-10-07 20:38)")
    gb = giant_blockers()
    if not gb or min(gb.values()) < 2:
        bad.append("the Rot patch no longer gives %s measured contact cells: %r" % (GIANT, gb))
    for ty, name, f in PATCHES:
        p = _src(f)
        if p is None:
            bad.append("patch file %s gone" % f)
        elif ty not in open(p, encoding="utf-8").read():
            bad.append("%s no longer patches %s" % (f, ty))
    t = tier_xml()
    if not (0 < t["t1MinBodySize"] < t["t2MinBodySize"] < t["t3MinBodySize"]):
        bad.append("tier thresholds not ascending: %r" % t)
    cr = crush_xml()
    if len(cr) < 5 or cr.get("RM_Crush_Chunks", {}).get("crushable") != "false" or cr.get("RM_Crush_HugeTrunk", {}).get("crushable") != "false":
        bad.append("crush table probe read %r (expected 5 rows, chunks and the giant trunk protected)" % sorted(cr))
    if len([1 for ty, _n in SHIPPED if ty.endswith("RM_CrushRuleDef")]) != len(cr):
        bad.append("crush rule count differs between the defs probe and the table probe")
    mod = read("Source", "Titanic", "RM_TitanicCreaturesMod.cs")
    if 'HarmonyId = "%s"' % TITAN_HARMONY_ID not in mod:
        bad.append("titan Harmony id is no longer %s (the harmony_titans chain asserts it)" % TITAN_HARMONY_ID)
    wake = re.sub(r"//[^\n]*", "", read("Source", "Titanic", "Wake", "TitanicWakeProcessor.cs"))
    for needle in ("WakeActive", "wakeCrushDamageMultiplier", "wakeFilthTrailChance", "Filth_RubbleRock", "isThickRoof",
                   "RoofHolingActive", "SmashGiantPlants", "GiantSmash.Owners", "ForwardToPlant", "GiantSmash.WakeMayCrush"):
        if needle not in wake:
            bad.append("TitanicWakeProcessor.cs lacks %s" % needle)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "HugeThings.md")):
        bad.append("walk missing")
    if os.path.isdir(os.path.join(HERE, "..", "TitanicCreatures", "About")):
        bad.append("the retired TitanicCreatures mod folder is back beside its replacement")
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
    suite = Suite("HugeThings")
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        kw = dict(typeName=SETTINGS, action=action, field=field)
        if value is not None:
            kw["value"] = str(value)
        r = t.session.call("jawa/mod_settings_field", **kw)
        if action == "set" and isinstance(r, dict) and r.get("success"):
            # jawa/mod_settings_field only writes the static; the mod's own refresh is Mod.WriteSettings -> RefreshAllMaps,
            # which the settings window calls and the bridge does not (MEASURED 2026-10-08: toggle off left 10 blockers).
            t.session.call("jawa/static_call", type="RimMandrake.HugeThings.MapComponent_HugeFootprints", method="RefreshAllMaps")
        return r if isinstance(r, dict) else {}

    # HUGETHINGS_TEST_HONESTY_1 (C3.7): a run must hand the player's settings back as it found them, never as DEFAULTS. Each
    # field is snapshotted (raw get) before its first write and that value is restored in the caller's finally.
    _saved = {}

    def _put(t, field, value):
        if t.session is None:
            return
        if (id(t), field) not in _saved:
            old = _raw(t, "get", field).get("value")
            if old is None:
                raise ExpectationFailed("could not read %s before changing it; refusing to overwrite the player's setting" % field)
            _saved[(id(t), field)] = old
        if not _raw(t, "set", field, value).get("success"):
            raise ExpectationFailed("could not set %s=%s" % (field, value))

    def _restore(t, field):
        if t.session is None:
            return
        old = _saved.pop((id(t), field), None)
        if old is None:
            print("[titanic] RESTORE SKIPPED %s: no snapshot (never changed)" % field, file=sys.stderr, flush=True)
            return
        try:
            if not _raw(t, "set", field, old).get("success"):
                print("[titanic] RESTORE FAILED %s -> %s" % (field, old), file=sys.stderr, flush=True)
        except Exception as ex:
            print("[titanic] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    def _count(t, defName, rect):
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=200)
        if not _live(t):
            return 0
        if not isinstance(r, dict) or r.get("success") is False or "countMatched" not in r:
            raise ExpectationFailed("list_things(%s) unreadable: %r" % (defName, r))
        return int(r.get("countMatched"))

    def _stage(t, x, z, growth):
        r = t.bridge_call("jawa/artboard_stage", phase="subjects", pause=False, killHostiles=True,
                          ops="id=g|kind=plant|x=%d|z=%d|def=%s|growth=%s" % (x, z, GIANT, growth))
        if not _live(t):
            return True
        ops = (r or {}).get("ops") or [] if isinstance(r, dict) else []
        if not ops or not ops[0].get("ok"):
            _unmeasured(t, "could not stage %s at %d,%d (growth %s): %s" % (GIANT, x, z, growth, str(r)[:200]))
            return False
        return True

    def _rects(x, z):
        around = "%d,%d,17,17" % (x - 8, z - 2)   # the 12-cell quad plus margin, incl. two rows south
        south = "%d,%d,17,2" % (x - 8, z - 2)
        return around, south

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t) and (not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 0):
                raise ExpectationFailed("control def reads as present or the call failed: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=60)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%s of %d defs resolved; notFound=%r" % (r.get("foundCount"), len(names), r.get("notFound")))
        with t.component("blocker_def_resolves", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s;ThingDef/%s" % (BLOCKER, GIANT), fields="defName", limit=4)
            if _live(t) and (not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 2):
                raise ExpectationFailed("blocker or %s did not resolve (is mandrake.rm.biomes loaded?): %r" % (GIANT, r))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
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
                    new = str(int(float(old)) - 1 if int(float(old)) > 1 else int(float(old)) + 1)
                else:
                    new = str(round(float(old) - 0.25, 2))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)

    @suite.chain("harmony")
    def harmony(t):
        with t.component("Thing_get_CustomRectForSelector_postfix_attached", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName="Thing", methodName="get_CustomRectForSelector")
            if not _live(t):
                return
            methods = (r or {}).get("methods") or [] if isinstance(r, dict) else []
            if not isinstance(r, dict) or r.get("success") is not True or not methods:
                _unmeasured(t, "harmony_patches could not resolve the property getter: %s" % str(r)[:160])
                return
            owners = [p.get("owner") for m in methods for p in (m.get("postfixes") or [])]
            if HARMONY_ID not in owners:
                raise ExpectationFailed("no postfix owned by %s (owners %r)" % (HARMONY_ID, owners[:8]))

    @suite.chain("trunk")
    def trunk(t):
        if _live(t):
            t.clear_area(size=30)
        x, z = t.anchor if t.anchor else (0, 0)
        around_r, south_r = _rects(x, z)
        allowed = sorted(set((giant_blockers() or {}).values()))
        baseline = {}
        with t.component("full_grown_giant_gets_its_measured_footprint", toggle="plantTrunkEnabled"):
            if _live(t) and _stage(t, x, z, 1):
                t.wait_ticks(120)
                out, south = _count(t, BLOCKER, around_r), _count(t, BLOCKER, south_r)
                baseline["n"] = out
                if out not in allowed:
                    raise ExpectationFailed("%s at growth 1 has %d blockers nearby; its measured variants allow %r"
                                            % (GIANT, out, allowed))
                if south:
                    raise ExpectationFailed("%d blockers south of the plant: its own cell would be unreachable" % south)
        with t.component("toggle_off_clears_the_trunk", toggle="plantTrunkEnabled"):
            if _live(t):
                _put(t, "plantTrunkEnabled", False)
                try:
                    t.wait_ticks(REFRESH_TICKS + 60)
                    n = _count(t, BLOCKER, around_r)
                    if n:
                        raise ExpectationFailed("plantTrunkEnabled off, yet %d blockers remain after a refresh" % n)
                finally:
                    _restore(t, "plantTrunkEnabled")
                t.wait_ticks(REFRESH_TICKS + 60)
        with t.component("cutting_the_plant_removes_the_trunk", toggle="plantTrunkEnabled"):
            if _live(t):
                if not baseline.get("n") or _count(t, BLOCKER, around_r) != baseline["n"]:
                    _unmeasured(t, "the trunk did not come back after re-enabling: no baseline to cut")
                else:
                    t.bridge_call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Plant")
                    n = _count(t, BLOCKER, around_r)
                    if n:
                        raise ExpectationFailed("plant destroyed, %d blockers left behind" % n)
        with t.component("young_giant_blocks_nothing", toggle="plantTrunkEnabled"):
            if _live(t) and _stage(t, x, z, 0.1):
                t.wait_ticks(120)
                n = _count(t, BLOCKER, around_r)
                if n:
                    raise ExpectationFailed("%s at growth 0.1 already has %d blockers" % (GIANT, n))

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

    @suite.chain("harmony_titans")
    def harmony_titans(t):
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
                if TITAN_HARMONY_ID not in owners:
                    raise ExpectationFailed("%s.%s carries no patch owned by %s (owners: %s)"
                                            % (ty, name, TITAN_HARMONY_ID, sorted(set(o for o in owners if o))[:8]))

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
                    raise ExpectationFailed("%r: a %s walked a 15-cell lane and left no rubble (0.35 chance per cell step makes this ~1 in 10^3)" % (m, BEAST))
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
                ("click_anywhere_on_picture_selects_plant", "plantSelectionEnabled", "no bridge tool reads Thing.CustomRectForSelector or simulates a map click"),
                ("huge_pawn_hitbox_covers_drawn_body", "pawnHitboxEnabled", "no selection-rect read tool"),
                ("trunk_relinks_after_save_load", None, "needs a save/load round on a map with a giant"),
                ("shot_into_trunk_damages_the_plant_once", "plantTrunkDamageEnabled", "no bridge tool fires a projectile or explosion at a cell; offline: kernel fuzz `damage`, static patch checks"),
                ("growth_pushes_items_never_wipes_them", "plantItemPushEnabled", "needs items staged under a growing footprint; offline: kernel fuzz `items`"),
                ("growth_never_traps_a_pawn", None, "needs a pawn staged inside a growing footprint; offline: kernel fuzz `planner`"),
                ("zone_cells_survive_blockers", None, "needs a stockpile staged under a footprint; offline: static patch check"),
                ("mapgen_giants_get_trunks", None, "needs a fresh Rot map generation"),
                ("t2_holes_thin_roofs_and_crushes_walls", "wakeRoofHolingEnabled",
                 "needs a race of bodySize >= 8 (ours: RM_Hwelgrue, RM_Totchak, RM_Gorrask; see the walk plan) in the list"),
                ("t3_titan_smashes_a_giant_plant", "giantPlantSmashEnabled",
                 "needs a T3 race (RM_Gloomcast, RM_Oommok) ordered past a Rot giant; offline: kernel fuzz `smash`, `smashstep`, `gates`"),
                ("smaller_titan_goes_around_a_giant", "giantPlantSmashMinTier",
                 "needs a T1/T2 race beside a Rot giant; the trunk is an impassable edifice, so this is vanilla pathing"),
                ("t3_corpse_becomes_a_harvest_site", "corpseSiteEnabled",
                 "needs a bodySize >= 20 corpse and several harvest work sessions"),
                ("butcher_yield_curve_reduces_t1_t2_yield", "yieldCurveEnabled",
                 "needs a butcher job on a tiered corpse compared with an untiered same-mass control"),
                ("thick_roof_slows_a_titan", "roofAvoidanceEnabled",
                 "needs an overhead-mountain roof and a step-cost read; the harmony_titans chain proves the patch is attached only"),
                ("custom_tiers_move_the_ladder", "tierThresholdsCustom", "a startup-read setting: needs a restart between two loads"),
                ("large_pawns_footprint_bridge", "largePawnsFootprintEnabled",
                 "soft reflection into neku.largepawns at startup; needs that mod loaded and a multi-cell OccupiedRect read"),
                ("giant_plants_master_off_is_vanilla", "giantPlantsEnabled", "offline: kernel fuzz `gates`; live: the trunk chain's toggle-off case covers trunks only"),
                ("giant_animals_master_off_is_vanilla", "giantAnimalsEnabled", "offline: kernel fuzz `gates`; live: needs the wake lane rerun with the master off")):
            with t.component(name, toggle=toggle, beyond_toggle=toggle is None):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None


if __name__ == "__main__":
    findings = static_checks()
    for f in findings:
        print("FINDING:", f)
    print("STATIC: %s (%d findings)" % ("PASS" if not findings else "FAIL", len(findings)))
    sys.exit(1 if findings else 0)
