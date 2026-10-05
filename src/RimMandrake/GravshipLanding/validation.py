"""validation.py -- modcheck suite for RimMandrake: Gravship Landing Reveal (mandrake.rm.gravshiplanding).

First north-star script (GRAVSHIP_LANDING_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/GravshipLanding.md.
One Harmony postfix (Patch_GenStep_GravshipMarker_Generate.Postfix on GenStep_GravshipMarker.Generate) that unfogs every
unroofed fogged cell of a gravship-ARRIVAL map before the landing picker shows, behind one Mod Setting
(GravshipLandingSettings.revealOutdoorsBeforeLanding). The mod ships NO defs.

CHAINS
  defs_resolve          the mod ships no defs (static) and the probe can say absent on a control name.
  settings_roundtrip    every `public static` field of GravshipLandingSettings (parsed from the C#): get, set, read back, restore.
  reveal_gate_armed     the postfix is attached to GenStep_GravshipMarker.Generate by this mod's Harmony id (a failed patch would
                        leave the mod loaded and doing nothing); a nonexistent method reads no owner.
  arrival_map_reveal    GravshipLandingProof.ProofReveal runs the shipped RevealIfArrival on a fogged rect with a staged
                        walled+roofed room: outdoors all unfogged, interior 9/9 fogged, setting off and non-arrival
                        unfog nothing (GRAVSHIPLANDING_COVERAGE_GAPS_1). A real arrival-generated map stays unreached.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.GravshipLanding.GravshipLandingSettings"
HARMONY_ID = "mandrake.rm.gravshiplanding"
CONTROL_ABSENT = "ThingDef/RM_GravshipLandingNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
PATCH_TYPE, PATCH_METHOD, PATCH_NAME = "GenStep_GravshipMarker", "Generate", "Postfix"
PROOF_TYPE = "RimMandrake.GravshipLanding.GravshipLandingProof"


def parse_proof(text):
    """\"outdoor=A/B interiorFogged=C/9 off_unfogged=D ...\" -> {key: (num, den or None)}."""
    return dict((k, (int(a), int(b) if b else None)) for k, a, b in re.findall(r"(\w+)=(-?\d+)(?:/(\d+))?", text))


def _read(name):
    return open(os.path.join(HERE, "Source", name), encoding="utf-8").read()


def settings_fields():
    """{name: type} for every scalar `public static` field of GravshipLandingSettings, read from the C#."""
    body = _read("GravshipLandingMod.cs").split("class GravshipLandingSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    fields = settings_fields()
    if "revealOutdoorsBeforeLanding" not in fields:
        return ["settings probe did not find revealOutdoorsBeforeLanding (sanity probe failed)"]
    mod = _read("GravshipLandingMod.cs")
    scribed = mod.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    if 'HarmonyId = "%s"' % HARMONY_ID not in mod:
        bad.append("HarmonyId constant is not %s" % HARMONY_ID)
    if "PatchAll" not in mod:
        bad.append("the mod no longer calls PatchAll (the postfix would never attach)")
    patch = _read("Patch_GenStep_GravshipMarker.cs")
    if "typeof(%s), nameof(%s.%s)" % (PATCH_TYPE, PATCH_TYPE, PATCH_METHOD) not in patch:
        bad.append("postfix no longer targets %s.%s" % (PATCH_TYPE, PATCH_METHOD))
    if not re.search(r"static void %s\(" % PATCH_NAME, patch):
        bad.append("postfix method %s not found" % PATCH_NAME)
    if "revealOutdoorsBeforeLanding" not in patch:
        bad.append("the postfix no longer reads the toggle")
    if os.path.isdir(os.path.join(HERE, "Defs")):
        bad.append("a Defs/ folder appeared: add a defs_resolve component that reads it")
    proj = _read("RM_GravshipLanding.csproj")
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "GravshipLanding.md")):
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
    suite = Suite("GravshipLanding")
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
            if "revealOutdoorsBeforeLanding" not in settings_fields():
                raise ExpectationFailed("settings probe found no revealOutdoorsBeforeLanding (blind regex)")
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

    @suite.chain("reveal_gate_armed")
    def reveal_gate_armed(t):
        with t.component("control_nonexistent_method_has_no_owner", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName=PATCH_TYPE, methodName="NoSuchMethodZZ")
            if _live(t) and isinstance(r, dict) and r.get("success") is True and not r.get("harmonyError"):
                for m in (r.get("methods") or []):
                    if any(p.get("owner") == HARMONY_ID for p in (m.get("postfixes") or [])):
                        raise ExpectationFailed("a nonexistent method reads as patched by %s" % HARMONY_ID)
        with t.component("postfix_attached_to_gravship_marker_generate", toggle="revealOutdoorsBeforeLanding"):
            r = t.bridge_call("jawa/harmony_patches", typeName=PATCH_TYPE, methodName=PATCH_METHOD)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked: %s" % str(r)[:160])
                    return
                mine = [p for m in (r.get("methods") or []) for p in (m.get("postfixes") or [])
                        if (p.get("patchMethod") or "").endswith(PATCH_NAME) and p.get("owner") == HARMONY_ID]
                if not mine:
                    owners = sorted(set(p.get("owner") for m in (r.get("methods") or [])
                                        for p in (m.get("postfixes") or []) if p.get("owner")))
                    raise ExpectationFailed("%s.%s carries no postfix %s from %s (owners: %s)"
                                            % (PATCH_TYPE, PATCH_METHOD, PATCH_NAME, HARMONY_ID, owners[:8]))

    @suite.chain("arrival_map_reveal")
    def arrival_map_reveal(t):
        """GravshipLandingProof.ProofReveal runs the SHIPPED RevealIfArrival (the postfix's whole body, gates
        included) on a fogged 21x21 rect holding a staged 5x5 walled, roofed room. The gen-step hook itself is
        reveal_gate_armed's bar; a map generated by a real arrival stays out of reach of the bridge."""
        kv = {}
        with t.component("outdoor_cells_unfogged_on_arrival_map", toggle="revealOutdoorsBeforeLanding"):
            r = t.bridge_call("jawa/static_call", type=PROOF_TYPE, method="ProofReveal", args="go")  # empty args binds a 0-param call; the C# signature takes one string
            if _live(t):
                text = str((r or {}).get("result") or "(no result: %s)" % str(r)[:160])
                kv = parse_proof(text)
                if text.startswith("REFUSED"):
                    _unmeasured(t, "ProofReveal: " + text)
                elif text.startswith("ERROR") or "outdoor" not in kv:
                    raise ExpectationFailed("ProofReveal: %s" % text)
                elif kv["outdoor"][1] < 300 or kv["outdoor"][0] != kv["outdoor"][1]:
                    got, of = kv["outdoor"]
                    raise ExpectationFailed("outdoor cells unfogged %d of %d (want all)" % (got, of))
        with t.component("roofed_interiors_stay_fogged", toggle="revealOutdoorsBeforeLanding"):
            if _live(t):
                got, of = kv["interiorFogged"]
                if of != 9 or got != of:
                    raise ExpectationFailed("walled roofed interior fogged %d of %d (want 9 of 9)" % (got, of))
        with t.component("toggle_off_leaves_vanilla_fog", toggle="revealOutdoorsBeforeLanding"):
            if _live(t) and kv["off_unfogged"][0] != 0:
                raise ExpectationFailed("setting off still unfogged %d cells" % kv["off_unfogged"][0])
        with t.component("non_arrival_map_is_a_no_op", beyond_toggle=True):
            if _live(t) and kv["nonarrival_unfogged"][0] != 0:
                raise ExpectationFailed("a non-arrival map unfogged %d cells" % kv["nonarrival_unfogged"][0])

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
