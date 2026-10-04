"""validation.py -- modcheck suite for RimMandrake: Hostile Flora (mandrake.rm.hostileflora).

First north-star script (HOSTILE_FLORA_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/HostileFlora.md.
The mod ships ONE species (RM_Gallowroot: ThingDef + PawnKindDef, an animal def, never a Plant) whose whole
behaviour is the shared CreatureBehaviors reaction mechanism (RM_CompReactionSource + SameKindWithinRadius
propagation + ActivateSelf response). The mod owns no settings class: its only knobs are CreatureBehaviors'
`reactionSourceSpawnEnabled` and `reactionSourceBudgetMultiplier`, so the round-trip chain exercises those.

CHAINS
  defs_resolve        every def in Defs/ resolves live (names parsed from the XML) + the comp's rule classes' target
                      mental state def; a control name proves the probe can say "absent".
  settings_roundtrip  the shared reaction-source settings: default / write / restore, numerics compared numerically.
  reaction_cluster    damage one of three adjacent gallowroots; the others should enter RM_SwarmAggression
                      (propagation); with `reactionSourceSpawnEnabled` off none should (control). Needs a live map and
                      a mental-state reader: UNMEASURED (with the reason) whenever either is missing, never PASS.
NOT PROVEN HERE (the About lists them as unbuilt): proximity trigger, rooted-idle read, art, biome placement.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import contextlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.join(HERE, "..", "CreatureBehaviors")
SETTINGS = "RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings"
SETTING_FIELDS = ("reactionSourceSpawnEnabled", "reactionSourceBudgetMultiplier")
MENTAL = "RM_SwarmAggression"
CONTROL_ABSENT = "ThingDef/RM_GallowrootNoSuchDef_ZZ"
_SCALAR = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    """[(DefType, defName)] for every non-abstract def under Defs/, read from the XML (never a hand list)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    """{name: type} of the shared scalar settings this mod rides on, read from CreatureBehaviors' C#."""
    src = open(os.path.join(CB, "Source", "RM_CreatureBehaviorsMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_CreatureBehaviorsSettings", 1)[1]
    body = re.sub(r"//[^\n]*", "", body)
    return dict((m.group(2), m.group(1)) for m in _SCALAR.finditer(body))


def static_checks():
    bad = []
    if not SHIPPED:
        return ["no defs parsed from Defs/ (sanity probe failed)"]
    names = dict((n, ty) for ty, n in SHIPPED)
    if names.get("RM_Gallowroot") != "ThingDef" or ("PawnKindDef", "RM_Gallowroot") not in SHIPPED:
        bad.append("RM_Gallowroot ThingDef + PawnKindDef not both present")
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Gallowroot.xml")).getroot()
    thing = next(e for e in root.iter("ThingDef"))
    kind = next(e for e in root.iter("PawnKindDef"))
    if kind.findtext("race") != "RM_Gallowroot":
        bad.append("PawnKind race != RM_Gallowroot")
    if thing.findtext("race/manhunterOnDamageChance") != "0":
        bad.append("manhunterOnDamageChance must be 0 (all aggression is routed through the reaction comp)")
    if root.find(".//Plant") is not None or thing.get("ParentName") != "AnimalThingBase":
        bad.append("gallowroot must be an animal def (ParentName AnimalThingBase), never a Plant")
    comp = thing.find("comps/li[@Class='RimMandrake.CreatureBehaviors.RM_CompProperties_ReactionSource']")
    if comp is None:
        bad.append("reaction source comp missing")
    else:
        if comp.find("propagation").get("Class") != "RimMandrake.CreatureBehaviors.RM_ReactionPropagationRule_SameKindWithinRadius":
            bad.append("propagation rule is not SameKindWithinRadius")
        if comp.find("response").get("Class") != "RimMandrake.CreatureBehaviors.RM_ReactionResponseRule_ActivateSelf":
            bad.append("response rule is not ActivateSelf")
        if comp.findtext("response/mentalState") != MENTAL:
            bad.append("response mental state is not %s" % MENTAL)
        if not int(comp.findtext("eventBudget") or 0) > 0:
            bad.append("eventBudget must be > 0")
    # every referenced class and mental state exists in CreatureBehaviors (a missing one discards the def silently)
    cbsrc = ""
    for fn in os.listdir(os.path.join(CB, "Source")):
        if fn.endswith(".cs"):
            cbsrc += open(os.path.join(CB, "Source", fn), encoding="utf-8").read()
    for cls in ("RM_CompProperties_ReactionSource", "RM_ReactionPropagationRule_SameKindWithinRadius",
                "RM_ReactionResponseRule_ActivateSelf"):
        if "class %s" % cls not in cbsrc:
            bad.append("CreatureBehaviors source has no class %s" % cls)
    if "<defName>%s</defName>" % MENTAL not in open(os.path.join(CB, "Defs", "MentalStateDefs", "RM_SwarmAggression_MentalStates.xml"), encoding="utf-8").read():
        bad.append("mental state %s missing from CreatureBehaviors" % MENTAL)
    # settings: the shared fields this mod claims exist and are Scribed
    f = settings_fields()
    if not f:
        bad.append("settings probe found no scalar field (sanity probe failed)")
    for n in SETTING_FIELDS:
        if n not in f:
            bad.append("shared setting %s not declared in CreatureBehaviors" % n)
    if "mandrake.rm.biomes" not in open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read():
        bad.append("About.xml lacks its modDependencies entry")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "HostileFlora.md")):
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
    suite = Suite("HostileFlora")
    suite.toggles = list(SETTING_FIELDS)

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        """UNMEASURED, never FAIL: the harness's route is upstream_failed + upstream_reason."""
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    @contextlib.contextmanager
    def _set(t, field, value):
        old = _raw(t, "get", field).get("value") if t.session is not None else None
        try:
            if _live(t):
                r = _raw(t, "set", field, value)
                if not r.get("success"):
                    raise ExpectationFailed("set %s=%s failed: %r" % (field, value, r))
            yield
        finally:
            if t.session is not None and old is not None:
                try:
                    _raw(t, "set", field, old)
                except Exception as ex:
                    print("[hostileflora] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _near(a, b):
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        """Every shipped def resolves live (a def with an unresolvable comp/class is discarded silently)."""
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present or not-found is empty: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            want = ["%s/%s" % p for p in SHIPPED] + ["MentalStateDef/" + MENTAL]
            r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName", limit=50)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(want):
                    raise ExpectationFailed("expected %d defs, foundCount=%r notFound=%r" % (len(want), r.get("foundCount"), r.get("notFound")))
        with t.component("reaction_comp_loaded_on_def", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Gallowroot", fields="comps", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                comps = ((rows[0].get("fields") or {}).get("comps") if rows else None)
                if not isinstance(comps, list) or (comps and not all(isinstance(c, dict) for c in comps)):
                    _unmeasured(t, "get_defs returned comps as bare type names, no class names (modExtension/comp reads carry no class)")
                    return
                if "ReactionSource" not in json.dumps(comps):
                    raise ExpectationFailed("no ReactionSource comp on RM_Gallowroot: %r" % (comps,))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        """The shared settings this mod rides on: default / write / restore (this mod declares no settings class)."""
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if not settings_fields():
                raise ExpectationFailed("settings probe found no scalar field (blind regex)")
        for field in SETTING_FIELDS:
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                ty = settings_fields()[field]
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    ok = str(back).lower() == new.lower() if ty == "bool" else _near(back, new)
                    if not ok:
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not (str(back).lower() == str(old).lower() if ty == "bool" else _near(back, old)):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    def _mental(row):
        """(found_key, value) for the first key naming a mental state anywhere in a pawn_get payload."""
        stack = [row]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    if "mental" in str(k).lower():
                        return True, v
                    stack.append(v)
            elif isinstance(o, list):
                stack.extend(o)
        return False, None

    @suite.chain("reaction_cluster")
    def reaction_cluster(t):
        """Damage one of three adjacent gallowroots; neighbours should swarm; control with the mechanism off."""
        with t.component("neighbours_swarm_when_one_is_hurt", toggle="reactionSourceSpawnEnabled"):
            if not _live(t):
                return
            t.clear_area(size=24)
            ids = []
            for i in range(3):
                r = t.bridge_call("jawa/spawn_pawn", kindDef="RM_Gallowroot", x=t.anchor[0] + 2 * i,
                                  z=t.anchor[1], faction="none", count=1)
                rows = (r or {}).get("pawns") or []
                if rows and rows[0].get("id"):
                    ids.append(rows[0]["id"])
                    t.session.track("pawn", rows[0]["id"], x=t.anchor[0] + 2 * i, z=t.anchor[1])
            if len(ids) < 3:
                _unmeasured(t, "could not spawn three gallowroots (spawn_pawn returned %r)" % (ids,))
                return
            probe = t.bridge_call("jawa/pawn_get", pawn=ids[1])
            if not _mental(probe)[0]:
                _unmeasured(t, "jawa/pawn_get exposes no mental-state field for an animal pawn; the swarm cannot be read "
                               "(a mental-state reader tool is owed)")
                return
            r = t.bridge_call("jawa/damage", thingId=ids[0], amount=1, damageDef="Scratch")
            if isinstance(r, dict) and r.get("success") is False:
                _unmeasured(t, "jawa/damage refused: %r" % r)
                return
            t.wait_ticks(120)
            swarming = [i for i in ids[1:] if MENTAL in json.dumps(_mental(t.bridge_call("jawa/pawn_get", pawn=i))[1])]
            if not swarming:
                raise ExpectationFailed("no neighbour entered %s after one gallowroot was hurt" % MENTAL)
        with t.component("mechanism_off_control_no_swarm", toggle="reactionSourceSpawnEnabled"):
            if not _live(t):
                return
            _unmeasured(t, "the off-control needs the previous component's cluster to have been readable; "
                           "owed to the first live run (state after recovery of RM_SwarmAggression is timed)")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
