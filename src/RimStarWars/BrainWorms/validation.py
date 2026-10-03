"""validation.py -- modcheck suite for RimStarWars: Geonosian Brain Worms (mandrake.rsw.brainworms).

First north-star script (BRAIN_WORMS_FIRST_SCRIPT_1). Walk: design/validation_walks/RimStarWars/BrainWorms.md.
A Geonosian hive parasite: a worm burrows into a LIVING humanlike host and rides a three-stage hediff
(latent 0 / influenced 0.35 / puppeted 0.8) into RSW_BrainWormPuppet. Cold (below freezing) reverses the
severity and clears it; surgery (RSW_RemoveBrainWorm) is the risky fast path. Three vectors: ruin-loot egg
clusters (a patch), the cargo-pod incident (gated by cargoIncidentEnabled), the mortar egg shell (gated by
eggProjectileEnabled). PERMANENT owner ruling: never a corpse-walker -- every path needs a living host.

CHAINS
  defs_resolve        every def under Defs/ (parsed from the XML) resolves live; a control name reads notFound.
  settings_roundtrip  every `public static` field of RSW_BrainWormsSettings (found by regex): get / set / get /
                      restore; numerics compared numerically.
  ladder_wiring       the hediff's three stages carry the ruled minSeverity ladder, the puppeteer threshold equals
                      the third stage, cold is a negative severity rate; the surgery recipe removes the infection.
  infection_state     a spawned colonist given the infection carries it (a clean control pawn does not); severity
                      advances while the host is warm (UNMEASURED if the site is cold: the cure direction is seen).
  puppet_state        a host pushed to severity 0.9 is held in RSW_BrainWormPuppet (state read, never a screenshot).
  cargo_incident      A/B on cargoIncidentEnabled via fire_incident dryRun (off arm must refuse).
  mechanics_unmeasured  worm burrow bite, cold cure by place, surgery outcome, egg shell burst, ruin loot, the
                      dead-host refusal: each says what it needs (never a fake pass).

STATIC (offline): `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.StarWars.BrainWorms.RSW_BrainWormsSettings"
HEDIFF = "RSW_BrainWormInfection"
PUPPET_STATE = "RSW_BrainWormPuppet"
CONTROL_ABSENT = "ThingDef/RSW_BrainWormNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+(?:static\s+)?(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


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
    """{name: type} for every scalar field of RSW_BrainWormsSettings, read from the C# (comments stripped)."""
    src = open(os.path.join(HERE, "Source", "RSW_BrainWormsSettings.cs"), encoding="utf-8").read()
    body = src.split("class RSW_BrainWormsSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def _read(rel):
    return open(os.path.join(HERE, *rel.split("/")), encoding="utf-8").read()


def _hediff_el():
    root = ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "HediffDefs_BrainWorm.xml")).getroot()
    return [e for e in root if e.findtext("defName") == HEDIFF][0]


def static_checks():
    bad = []
    if len(SHIPPED) < 8:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no field (sanity probe failed)"]
    cs = re.sub(r"//[^\n]*", "", _read("Source/RSW_BrainWormsSettings.cs"))
    scribed = cs.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    # the cold-kill slider must never reach zero (owner design: cold is the intended escape)
    if not re.search(r"coldKillRateMultiplier\s*=\s*list\.Slider\([^,]+,\s*0\.[1-9]", cs):
        bad.append("coldKillRateMultiplier slider can reach zero (the cold cure would be switchable off)")
    proj = _read("Source/RimMandrake.StarWars.BrainWorms.csproj")
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    if "0Harmony" in proj:
        bad.append("csproj references Harmony: About.xml promises no Harmony")
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("HediffDef", "ThingDef", "PawnKindDef", "MentalStateDef", "IncidentDef", "RecipeDef", "ThinkTreeDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    # DefOf names all ship
    defof = re.findall(r"public static (\w+) (\w+);", _read("Source/BrainWormsDefOf.cs"))
    names = set(n for _t, n in SHIPPED)
    for ty, n in defof:
        if (ty, n) not in SHIPPED:
            bad.append("DefOf %s %s names no shipped def" % (ty, n))
    # the stage ladder
    h = _hediff_el()
    mins = [float(s.findtext("minSeverity")) for s in h.findall("stages/li")]
    if mins != [0.0, 0.35, 0.8]:
        bad.append("hediff stage ladder is %r, ruled 0 / 0.35 / 0.8" % mins)
    if h.findtext("stages/li[1]/becomeVisible") != "false":
        bad.append("latent stage is not invisible (Discoverable's design)")
    prog = [c for c in h.findall("comps/li") if c.get("Class", "").endswith("HediffCompProperties_BrainWormProgress")][0]
    pup = [c for c in h.findall("comps/li") if c.get("Class", "").endswith("HediffCompProperties_BrainWormPuppeteer")][0]
    if not float(prog.findtext("severityPerDayWhenCold")) < 0:
        bad.append("cold severity rate is not negative: no cold cure")
    if not float(prog.findtext("severityPerDay")) > 0:
        bad.append("warm severity rate is not positive: no progression")
    if float(pup.findtext("puppetSeverity")) != mins[2]:
        bad.append("puppetSeverity differs from the puppeted stage minSeverity")
    if pup.findtext("mentalState") != PUPPET_STATE:
        bad.append("puppeteer does not name %s" % PUPPET_STATE)
    if h.findtext("tendable") != "false" or h.findtext("everCurableByItem") != "false":
        bad.append("infection became tendable / item-curable (only cold and surgery are cures)")
    rec = open(os.path.join(HERE, "Defs", "RecipeDefs", "Recipes_BrainWormSurgery.xml"), encoding="utf-8").read()
    if "<removesHediff>%s</removesHediff>" % HEDIFF not in rec:
        bad.append("surgery recipe does not remove the infection")
    # NEVER A CORPSE-WALKER (owner, permanent): every puppeting path refuses the dead
    for fn in ("CompRSWWormBurrow.cs", "HediffComp_BrainWormPuppeteer.cs"):
        if not re.search(r"\.Dead\b", re.sub(r"//[^\n]*", "", _read("Source/" + fn))):
            bad.append("%s has no dead-host refusal (owner ruling: never a corpse-walker)" % fn)
    if "<canBecomeShambler>false</canBecomeShambler>" not in _read("Defs/ThingDefs_Races/Races_BrainWorm.xml"):
        bad.append("worm race can become a shambler (corpse path)")
    for fn in ("Patches/BrainWormEggs_RuinLoot.xml", "Patches/BrainWormSurgery_RecipeUsers.xml"):
        ET.parse(os.path.join(HERE, *fn.split("/")))
    if re.search(r'<Operation[^>]*MayRequire', _read("Patches/BrainWormEggs_RuinLoot.xml")):
        bad.append("ruin-loot patch uses MayRequire on an Operation (inert in 1.6)")
    inc = _read("Source/IncidentWorker_BrainWormCargo.cs")
    if "cargoIncidentEnabled" not in inc:
        bad.append("incident worker no longer reads cargoIncidentEnabled")
    if "eggProjectileEnabled" not in _read("Source/Projectile_BrainWormEgg.cs"):
        bad.append("egg projectile no longer reads eggProjectileEnabled")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimStarWars", "BrainWorms.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


class _Unmeasured(Exception):
    pass


def _live(t):
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    """Stop this component and record UNMEASURED with `why` (never a pass)."""
    t._why = why
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() whose UNMEASURED does not poison the independent components after it."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw):
        yield
    if getattr(t, "_why", None) and not before:
        t.upstream_failed = False
        t.upstream_reason = None
    t._why = None


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _same(ty, a, b):
    if ty == "bool":
        return str(a).lower() == str(b).lower()
    try:
        return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


def _raw(t, action, field, value=None):
    kw = dict(typeName=SETTINGS, action=action, field=field)
    if value is not None:
        kw["value"] = str(value)
    r = t.session.call("jawa/mod_settings_field", **kw)
    return r if isinstance(r, dict) else {}


def _map_centre(t):
    r = t.bridge_call("jawa/map_info")
    if _live(t) and isinstance(r, dict) and r.get("sizeX") and r.get("sizeZ"):
        return int(r["sizeX"]) // 2, int(r["sizeZ"]) // 2
    return t.anchor


def _spawn(t, kind, x, z, faction="player"):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    pid = (((r or {}).get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn: %r" % (kind, r))
    t.session.track("pawn", pid, x=x, z=z)
    return pid


def _snap(t, pid):
    r = t.bridge_call("jawa/pawn_get", pawn=pid)
    if not _live(t):
        return {}
    snap = (r or {}).get("pawn") or r or {}
    return snap if isinstance(snap, dict) else {}


def _hediff_row(snap, name):
    """The hediff entry named `name` on a pawn_get snapshot: ('present', row) / ('absent', None) / ('unreadable', None)."""
    if "hediffs" not in snap:
        return "unreadable", None
    for h in snap["hediffs"] or []:
        if isinstance(h, dict):
            if name in (h.get("def"), h.get("defName"), h.get("hediff")):
                return "present", h
        elif str(h) == name:
            return "present", {}
    return "absent", None


def _build_suite():
    suite = Suite("BrainWorms")
    suite.toggles = sorted(settings_fields())

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with _comp(t, "control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                _ok(r, "get_defs control")
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    _fail("control def reads as present: %r" % r)
        with _comp(t, "every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):
                r = t.bridge_call("jawa/get_defs", defs=";".join(names[i:i + 40]), fields="defName", limit=60)
                if not _live(t):
                    continue
                _ok(r, "get_defs")
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                _fail("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))
        with _comp(t, "custom_comp_types_loaded", beyond_toggle=True):
            # a def naming a comp class that did not load is discarded silently: read the hediff's comps back
            r = t.bridge_call("jawa/get_defs", defs="HediffDef/" + HEDIFF, fields="comps", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs hediff comps")
                if int(r.get("foundCount", 0)) != 1:
                    _fail("hediff %s not found: %r" % (HEDIFF, r))
                blob = str((((r.get("defs") or [{}])[0]).get("fields") or {}).get("comps"))
                for need in ("BrainWormProgress", "BrainWormPuppeteer", "BrainWormWhispers"):
                    if need not in blob:
                        _unmeasured(t, "get_defs comps did not name %s (shape %s); cannot tell load failure from "
                                       "a bare-type-name reply" % (need, blob[:120]))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with _comp(t, "settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                _fail("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with _comp(t, "%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    _fail("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        _fail("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        _fail("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    _fail("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("ladder_wiring")
    def ladder_wiring(t):
        with _comp(t, "stage_ladder_live", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="HediffDef/" + HEDIFF, fields="stages", deep=True, limit=2)
            if _live(t):
                _ok(r, "get_defs stages")
                st = (((r.get("defs") or [{}])[0]).get("fields") or {}).get("stages")
                if not isinstance(st, list) or not all(isinstance(x, dict) for x in st):
                    _unmeasured(t, "get_defs returned stages as bare type names despite deep=true: %r" % (st,))
                got = [(str(x.get("label")), float(x.get("minSeverity", -1))) for x in st]
                if got != [("latent", 0.0), ("influenced", 0.35), ("puppeted", 0.8)]:
                    _fail("live stage ladder %r (stale deploy?)" % (got,))
        with _comp(t, "surgery_recipe_removes_infection", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="RecipeDef/RSW_RemoveBrainWorm", fields="removesHediff", limit=2)
            if _live(t):
                _ok(r, "get_defs recipe")
                if int(r.get("foundCount", 0)) != 1 or r.get("notFound"):
                    _fail("recipe did not resolve: %r" % r)
                f = (((r.get("defs") or [{}])[0]).get("fields") or {}).get("removesHediff")
                if HEDIFF not in str(f):
                    _fail("recipe removesHediff reads %r, not %s" % (f, HEDIFF))

    @suite.chain("infection_state")
    def infection_state(t):
        box = {}
        with _comp(t, "infected_pawn_carries_hediff_clean_control_does_not", beyond_toggle=True):
            cx, cz = _map_centre(t)
            t.clear_area(size=12)
            if _live(t):
                box["sick"] = _spawn(t, "Colonist", cx, cz)
                box["clean"] = _spawn(t, "Colonist", cx + 4, cz)
                r = t.bridge_call("jawa/pawn_health", pawn=box["sick"], action="add", hediff=HEDIFF, severity=0.5)
                _ok(r, "pawn_health add")
                state, _row = _hediff_row(_snap(t, box["sick"]), HEDIFF)
                if state == "unreadable":
                    _unmeasured(t, "jawa/pawn_get has no hediffs list")
                cstate, _c = _hediff_row(_snap(t, box["clean"]), HEDIFF)
                if cstate == "present":
                    _fail("the clean control pawn carries the infection")
                if state == "absent":
                    # a latent/undiscovered hediff may be hidden from the listing: the add itself succeeded, so
                    # this is not a mod verdict
                    _unmeasured(t, "pawn_health add succeeded but pawn_get lists no %s (an undiscovered hediff may "
                                   "be hidden from the snapshot)" % HEDIFF)
        with _comp(t, "severity_advances_while_warm", toggle="progressionSpeedMultiplier"):
            if _live(t):
                s0 = _hediff_row(_snap(t, box["sick"]), HEDIFF)[1] or {}
                if "severity" not in s0:
                    _unmeasured(t, "pawn_get hediff rows carry no severity field")
                t.wait_ticks(1500)
                s1 = _hediff_row(_snap(t, box["sick"]), HEDIFF)[1] or {}
                if "severity" not in s1:
                    _unmeasured(t, "second pawn_get read carries no severity field")
                a, b = float(s0["severity"]), float(s1["severity"])
                if b > a:
                    pass
                elif b < a:
                    _unmeasured(t, "severity FELL %.4f -> %.4f: the site was below freezing (the cold cure direction "
                                   "was seen, the warm direction needs a warm site)" % (a, b))
                else:
                    _fail("severity did not move in 1500 ticks on a living pawn (%.4f)" % a)

    @suite.chain("puppet_state")
    def puppet_state(t):
        with _comp(t, "host_at_puppet_severity_is_held_in_puppet_state", beyond_toggle=True):
            cx, cz = _map_centre(t)
            t.clear_area(size=12)
            if _live(t):
                pid = _spawn(t, "Colonist", cx, cz)
                _ok(t.bridge_call("jawa/pawn_health", pawn=pid, action="add", hediff=HEDIFF, severity=0.9),
                    "pawn_health add")
                t.wait_ticks(250)
                snap = _snap(t, pid)
                keys = [k for k in snap if "mental" in k.lower()]
                if not keys:
                    _unmeasured(t, "pawn_get carries no mental-state field (keys: %s)" % sorted(snap)[:20])
                if PUPPET_STATE not in str(dict((k, snap[k]) for k in keys)):
                    _fail("a host at severity 0.9 is not in %s: %r" % (PUPPET_STATE, dict((k, snap[k]) for k in keys)))

    @suite.chain("cargo_incident")
    def cargo_incident(t):
        with _comp(t, "cargo_incident_off_refuses_to_fire", toggle="cargoIncidentEnabled"):
            if not _live(t):
                return
            on = t.bridge_call("jawa/fire_incident", incidentDef="RSW_BrainWormCargoPod", dryRun=True)
            if not isinstance(on, dict) or "canFireNow" not in on:
                _fail("fire_incident dryRun gave no canFireNow: %r" % (on,))
            _raw(t, "set", "cargoIncidentEnabled", "False")
            try:
                off = t.bridge_call("jawa/fire_incident", incidentDef="RSW_BrainWormCargoPod", dryRun=True)
            finally:
                _raw(t, "set", "cargoIncidentEnabled", "True")
            if not isinstance(off, dict) or "canFireNow" not in off:
                _fail("fire_incident dryRun (off arm) gave no canFireNow: %r" % (off,))
            if off.get("canFireNow"):
                _fail("cargoIncidentEnabled=false but the incident can still fire")
            if not on.get("canFireNow"):
                _unmeasured(t, "the ON arm also reads canFireNow=False, so the toggle's effect cannot be told from the "
                               "site refusing (colony-age / map gates): %r" % (on.get("note") or on.get("reason")))

    @suite.chain("mechanics_unmeasured")
    def mechanics_unmeasured(t):
        for name, toggle, why in (
            ("worm_burrows_living_humanlike_host", None,
             "a loose worm biting and burrowing into a live humanlike needs a hostile worm, a host and a bite; no bridge verb "
             "forces CompRSWWormBurrow's attack path"),
            ("cold_below_freezing_clears_the_infection", "coldKillRateMultiplier",
             "clearing a puppeted host needs ~8 hours of below-freezing ambient; no verb sets a map's temperature"),
            ("surgery_removes_worm", None,
             "an operation bill needs a visible hediff, Medicine 9, a bed and 4000 work ticks of a surgeon"),
            ("egg_shell_bursts_into_worms", "eggProjectileEnabled",
             "a fired mortar shell is needed; a spawned projectile does not impact on its own"),
            ("ruin_loot_can_hold_egg_cluster", None,
             "needs a generated ancient complex (map generation); the patch target is vanilla's ThingSetMakerDef"),
            ("dead_host_is_never_puppeted", None,
             "needs a killed infected pawn and ticks past death (static check covers the Dead refusals in source)"),
        ):
            with _comp(t, name, toggle=toggle, beyond_toggle=(toggle is None)):
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
