"""validation.py -- modcheck suite for RimMandrake: Lore Stages (mandrake.rm.lorestages).

First north-star script (LORE_STAGES_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/LoreStages.md.
The ENGINE half of staged lore descriptions: GameComponent_LoreStage scribes a stage per ladder and rewrites a def's
description / settleWarning / label to the rung reached (LoreStageApplier, def-field writes, no Harmony); content mods ship the
ladders as RM_LoreStageTableDef. This mod ships NO defs and no ladder; the only consumer today is RUT_ScarlandsLadder in
RimUtinni (so ladder reads are UNMEASURED on a tier without it). One Mod Setting, RM_LoreStagesSettings.stagedTextEnabled.

CHAINS
  defs_resolve       the mod ships no defs (static) and the probe can say absent on a control name.
  settings_roundtrip every `public static` field of RM_LoreStagesSettings (parsed from the C#): get, set, read back, restore.
                     A successful get also proves the assembly loaded (the type resolved).
  consumer_ladder    when a consumer ladder (RUT_ScarlandsLadder) is loaded: it reads ladderId + maxStage > 0 and the def its
                     targets rewrite resolves with a non-empty description. A tier without the ladder reads UNMEASURED.
  stage_walk         set rung N -> text changes; down again -> shipped text restored; both private caches cleared; the master
                     toggle off -> stage-0 text: UNMEASURED (no bridge tool reaches SetStage / Reapply; the only entry points
                     are the dev DebugActions menu). Offline proof of the mechanism: Source/SelfTest (net472 exe).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.LoreStages.RM_LoreStagesSettings"
CONTROL_ABSENT = "ThingDef/RM_LoreStagesNoSuchDef_ZZ"
LADDER = "RM_LoreStageTableDef/RUT_ScarlandsLadder"
LADDER_TARGET = "BiomeDef/RUT_Scarlands"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def _read(name):
    return open(os.path.join(HERE, "Source", name), encoding="utf-8").read()


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_LoreStagesSettings, read from the C#."""
    body = _read("RM_LoreStagesMod.cs").split("class RM_LoreStagesSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    fields = settings_fields()
    if "stagedTextEnabled" not in fields:
        return ["settings probe did not find stagedTextEnabled (sanity probe failed)"]
    mod = _read("RM_LoreStagesMod.cs")
    scribed = mod.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    if "stagedTextEnabled" not in _read("GameComponent_LoreStage.cs"):
        bad.append("GameComponent_LoreStage no longer reads stagedTextEnabled (the master toggle gates nothing)")
    applier = _read("LoreStageApplier.cs")
    for cache in ("descriptionDetailedCached", "descriptionCached"):
        if cache not in applier:
            bad.append("applier no longer clears the private cache %s" % cache)
    if os.path.isdir(os.path.join(HERE, "Defs")):
        bad.append("a Defs/ folder appeared: add a defs_resolve component that reads it")
    proj = _read("RM_LoreStages.csproj")
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "LoreStages.md")):
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
    suite = Suite("LoreStages")
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
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("mod_ships_no_defs", beyond_toggle=True):
            if os.path.isdir(os.path.join(HERE, "Defs")):
                raise ExpectationFailed("a Defs/ folder exists but this script reads none of it")
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if "stagedTextEnabled" not in settings_fields():
                raise ExpectationFailed("settings probe found no stagedTextEnabled (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value (assembly not loaded, or type name moved)" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
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

    @suite.chain("consumer_ladder")
    def consumer_ladder(t):
        with t.component("ladder_table_loaded_with_id_and_cap", toggle="stagedTextEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=LADDER, fields="defName,ladderId,maxStage", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    _unmeasured(t, "get_defs could not be asked for %s: %r" % (LADDER, r))
                    return
                if int(r.get("foundCount", 0)) == 0:
                    _unmeasured(t, "no consumer ladder in this tier (%s lives in RimUtinni; LoreStages loads and does nothing "
                                   "without one)" % LADDER)
                    return
                rows = r.get("defs") or []
                f = (rows[0].get("fields") or {}) if rows else {}
                try:
                    cap = int(float(f.get("maxStage")))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return a numeric maxStage: %r" % (f,))
                    return
                if not str(f.get("ladderId") or "").strip():
                    raise ExpectationFailed("ladder has an empty ladderId (the save would key it by defName)")
                if cap <= 0:
                    raise ExpectationFailed("ladder maxStage is %d: unbounded, or a misread" % cap)
        with t.component("ladder_target_def_resolves_with_text", toggle="stagedTextEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=LADDER_TARGET, fields="defName,description,settleWarning", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    _unmeasured(t, "get_defs could not be asked for %s: %r" % (LADDER_TARGET, r))
                    return
                if int(r.get("foundCount", 0)) == 0:
                    _unmeasured(t, "target def %s is not loaded in this tier (the applier would warn once and skip it)" % LADDER_TARGET)
                    return
                rows = r.get("defs") or []
                f = (rows[0].get("fields") or {}) if rows else {}
                if not str(f.get("description") or "").strip():
                    raise ExpectationFailed("staged target has an empty description: the reset-to-baseline snapshot would be blank")

    @suite.chain("stage_walk")
    def stage_walk(t):
        for name, why in (
            ("rung_up_changes_text_and_down_restores_shipped",
             "needs a bridge tool that calls GameComponent_LoreStage.SetStage; today only the dev DebugActions menu ('Lore stages' "
             "> 'Set ladder stage...') does, which the bridge cannot click"),
            ("thing_and_hediff_caches_cleared_on_apply",
             "same: ThingDef.DescriptionDetailed / HediffDef.Description must read the new rung after a stage change; the "
             "'Log staged fields' debug action is the only reader. Offline proof is Source/SelfTest"),
            ("master_toggle_off_reads_stage_zero_text",
             "settings set through jawa/mod_settings_field does not call Reapply(); the effect is only visible after the settings "
             "window flips the checkbox or a new apply, neither reachable from the bridge"),
        ):
            with t.component(name, toggle="stagedTextEnabled"):
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
