"""validation.py -- modcheck suite for RimMandrake AtmosphericBase (mandrake.rm.atmosphericbase).

ATMOSPHERIC_BASE_BUILD_PROGRAM_1, Phase 1 only: capability discovery, the hard exclusion list, the per-thing
take-over / take-back buttons, the scenario-decides switch, exact restore on release, and two Mod Settings.
Grounded in Source/, read whole: Kernel/RM_AtmosphericKernel.cs, RM_GlowAccess.cs, RM_EmitterDiscovery.cs,
RM_MapComponent_AtmosphericBase.cs, RM_AtmosphericDesignators.cs, RM_AtmosphericBaseAPI.cs, RM_AtmosphericBaseSettings.cs,
RM_AtmosphericBaseProof.cs. Nothing here speaks for Phases 2-10 (groups, moods, territory, gestures, sound): they are
not built, and a bar for them would be a guess.

Three layers, cheapest first:
  1. static_findings(srcs) -- pure over the source text: no Harmony anywhere, no def mutated, every .cs compiled,
     every setting read where it does its job and Scribed, the exclusion list ahead of capability, the selftest seam
     never set by production code. Selftested by planted breaks in selftest_atmosphericbase.py.
  2. selftest_atmosphericbase_kernel.py -- the C# kernel + snapshot/restore against the REAL CompGlower fields.
  3. take_over_proof -- RM_AtmosphericBaseProof.ProofTakeover through jawa/static_call on a live map. Leaves the map as
     it found it. A map with no eligible fixture, or no excluded glower, answers "-" and those bars are UNMEASURED.

🔴 NEVER RUN LIVE. Built offline 2026-10-11; the lit-fixture branch of SetGlowColorInternal (DeRegister/Register on
the glow grid) runs only in game, so `restored` and `drive` are first proven by the live proof, not by the selftest.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
_PROOF = "RimMandrake.AtmosphericBase.RM_AtmosphericBaseProof"

suite = Suite("AtmosphericBase")
suite.toggles = ["lightChannel", "playerTakeoverButton"]

SETTINGS = ("lightChannel", "playerTakeoverButton")
GATES = (   # (setting, file, class, member) -- the setting must be read inside that member
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "TakeOverRefusal"),
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Drive"),
    ("lightChannel", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapComponentUpdate"),
    ("lightChannel", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("playerTakeoverButton", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("scenarioDecides", "RM_AtmosphericDesignators.cs", "RM_AtmosphericDesignators", "PlayerMayChoose"),
    ("PlayerMayChoose", "RM_AtmosphericDesignators.cs", "RM_Designator_TakeOverGlow", "CanDesignateThing"),
    ("PlayerMayChoose", "RM_AtmosphericDesignators.cs", "RM_Designator_ReleaseGlow", "CanDesignateThing"),
    ("TakeOverRefusal", "RM_AtmosphericDesignators.cs", "RM_Designator_TakeOverGlow", "CanDesignateThing"),
    ("TakeOverRefusal", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "TakeOver"),
    ("IsTaken", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Drive"),
    ("RM_GlowAccess.Restore", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "Release"),
    ("WriteColor", "RM_GlowAccess.cs", "RM_GlowAccess", "Restore"),
    ("EnsureRegistered", "RM_MapComponent_AtmosphericBase.cs", "RM_MapComponent_AtmosphericBase", "MapComponentUpdate"),
)
WIRING = (  # (file, needle, why)
    ("RM_GlowAccess.cs", '"glowColorOverride"', "the colour override field is no longer what is snapshotted"),
    ("RM_GlowAccess.cs", '"SetGlowColorInternal"', "colour is no longer written through the game's own regrid path"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Collections.Look(ref taken, "taken", LookMode.Deep)', "held fixtures forget their prior glow on reload"),
    ("RM_MapComponent_AtmosphericBase.cs", 'Scribe_Values.Look(ref scenarioDecides', "a scenario's decision is lost on reload"),
    ("RM_AtmosphericDesignators.cs", "Find.ReverseDesignatorDatabase", "the buttons are never offered"),
    ("RM_AtmosphericDesignators.cs", "ReferenceEquals(list, registeredIn)", "a Reinit()'d designator list never gets the buttons back"),
)
EXCLUSIONS = ("isPawn", "isPlant", "isApparelOrEquipment", "hologramMarked")


def load_sources():
    out = {}
    for dirpath, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("bin", "obj")]
        for fn in files:
            if fn.endswith((".cs", ".csproj")):
                rel = os.path.relpath(os.path.join(dirpath, fn), SRC).replace(os.sep, "/")
                out[rel] = open(os.path.join(dirpath, fn), encoding="utf-8").read()
    p = os.path.join(HERE, "About", "About.xml")
    out["About.xml"] = open(p, encoding="utf-8").read()
    return out


def _balanced(src, start):
    i, depth = src.index("{", start) + 1, 1
    j = i
    while j < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        j += 1
    return src[i:j]


def member_body(src, cls, member):
    """Text of `member` (method or property) inside `class cls`, comments removed; None when absent."""
    src = re.sub(r"//[^\n]*", "", src)
    m = re.search(r"class\s+%s\b" % re.escape(cls), src)
    if not m:
        return None
    body = _balanced(src, m.end())
    mm = re.search(r"\b%s\s*(?:\([^)]*\))?\s*\{" % re.escape(member), body)
    return _balanced(body, mm.start()) if mm else None


def _code(s):
    return re.sub(r"//[^\n]*", "", s)


def static_findings(srcs):
    """Pure over {relpath: text}. Each finding names its class in brackets."""
    bad = []
    prod = dict((k, v) for k, v in srcs.items() if not k.startswith("SelfTest/"))
    for fn, text in prod.items():
        if fn.endswith(".cs") and re.search(r"\bHarmony(Lib)?\b", _code(text)):
            bad.append("[no-harmony] %s references Harmony (spec: no Harmony; the buttons ride the reverse-designator list)" % fn)
        if fn.endswith(".cs") and re.search(r"\.comps\.Add\(|DefDatabase<[^>]+>\.Add\(|\.modExtensions\.Add\(", _code(text)):
            bad.append("[no-def-edit] %s mutates a def (the take-over must be per thing and reversible)" % fn)
        if fn.endswith(".cs") and re.search(r"glowRadiusOverride|RadiusField|\bGlowRadius\s*=(?!=)|ForceRegister", _code(text)):
            bad.append("[light-ledger] %s writes a light's radius; radius belongs to _Shared/LightLedger (LIGHT_LEDGER_ONE_1)" % fn)
        if fn.endswith(".cs") and "ColorWriterForSelfTest =" in _code(text):
            bad.append("[seam] %s sets the selftest colour writer in production code" % fn)
    proj = srcs.get("RM_AtmosphericBase.csproj", "")
    if "Harmony" in re.sub(r"<!--.*?-->", "", proj, flags=re.S):
        bad.append("[no-harmony] RM_AtmosphericBase.csproj references Harmony")
    for fn in prod:
        if fn.endswith(".cs") and ('Compile Include="%s"' % fn.replace("/", "\\")) not in proj:
            bad.append("[wiring] %s is not in RM_AtmosphericBase.csproj and compiles into nothing" % fn)
    about = srcs.get("About.xml", "")
    after = re.findall(r"<li>([^<]+)</li>", (re.search(r"<loadAfter>(.*?)</loadAfter>", about, re.S) or [None, ""])[1])
    if after != ["Ludeon.RimWorld"]:
        bad.append("[about] loadAfter must be Ludeon.RimWorld only, got %r" % after)
    if "brrainz.harmony" in about:
        bad.append("[about] About.xml depends on Harmony")
    for setting, fn, cls, member in GATES:
        b = member_body(srcs.get(fn, ""), cls, member)
        if b is None:
            bad.append("[gate] %s: %s.%s not found" % (fn, cls, member))
        elif setting not in b:
            bad.append("[gate] %s.%s no longer reads %s" % (cls, member, setting))
    for fn, needle, why in WIRING:
        if needle not in srcs.get(fn, ""):
            bad.append("[wiring] %s lost `%s`: %s" % (fn, needle, why))
    cl = member_body(srcs.get("Kernel/RM_AtmosphericKernel.cs", ""), "RM_AtmosphericKernel", "Classify") or ""
    cap = cl.find("hasGlower")
    for ex in EXCLUSIONS:
        at = cl.find(ex)
        if at < 0:
            bad.append("[exclusion] Classify no longer tests %s" % ex)
        elif cap >= 0 and at > cap:
            bad.append("[exclusion] Classify tests %s AFTER capability, so a glowing %s could be driven" % (ex, ex))
    x = srcs.get("RM_AtmosphericBaseSettings.cs", "")
    for f in SETTINGS:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), x):
            bad.append("[settings] %s is not Scribed" % f)
        if not re.search(r"ref %s," % f, x.split("DoWindowContents", 1)[-1]):
            bad.append("[settings] %s has no control in DoWindowContents" % f)
    return bad


def _kv(t):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method="ProofTakeover", args="go")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RM_AtmosphericBaseProof.ProofTakeover answered nothing (DLL not deployed?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofTakeover: %s" % text)
    kv = dict(re.findall(r"(\w+)=(\S+)", text))
    if kv.get("map") == "-":
        t.upstream_reason, t.upstream_failed = "UNMEASURED: no current map", True
        return None, ""
    return kv, text


def _unmeasured(t, why, text):
    t.upstream_reason, t.upstream_failed = "UNMEASURED: %s: %s" % (why, text[:200]), True


def _want(kv, text, keys):
    bad = dict((k, kv.get(k)) for k in keys if kv.get(k) != "True")
    if bad:
        raise ExpectationFailed("want True, got %s: %s" % (bad, text[:500]))


@suite.chain("take_over_proof")
def take_over_proof(t):
    with t.component("static_no_harmony_no_def_edit_gates_and_settings", beyond_toggle=True):
        bad = static_findings(load_sources())
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("compglower_members_bound_and_buttons_registered", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            _want(kv, text, ("bound", "buttons_registered"))
    with t.component("excluded_glowers_never_accepted", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("excluded_glowers", "0") == "0":
                _unmeasured(t, "this map holds no glowing pawn, plant, worn gear or hologram to test the exclusion on", text)
            elif kv.get("excluded_accepted") != "0":
                raise ExpectationFailed("%s excluded glower(s) would be taken over: %s" % (kv.get("excluded_accepted"), text[:400]))
    with t.component("take_drive_release_restores_exactly", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no untaken player-owned lit fixture on this map", text)
            else:
                _want(kv, text, ("offered", "take", "release_offered", "drive", "released", "restored", "drive_after_release_refused"))
    with t.component("untaken_neighbour_untouched", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("neighbour", "-") == "-":
                _unmeasured(t, "fewer than two eligible fixtures on this map", text)
            else:
                _want(kv, text, ("neighbour",))
    with t.component("light_channel_off_refuses_and_releases", toggle="lightChannel"):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            elif kv.get("channel_off_releases", "-") == "-":
                _want(kv, text, ("channel_off",))
                _unmeasured(t, "the player already holds fixtures here, so the release-everything half is not exercised", text)
            else:
                _want(kv, text, ("channel_off", "channel_off_releases"))
    with t.component("button_switch_hides_the_button", toggle="playerTakeoverButton"):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            else:
                _want(kv, text, ("button_off_hides",))
    with t.component("scenario_decides_hides_the_button", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("eligible", "0") == "0":
                _unmeasured(t, "no eligible fixture on this map", text)
            else:
                _want(kv, text, ("scenario_hides",))
    with t.component("release_after_save_reload_restores", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: release after a save and reload needs a save/load round trip on a held fixture; "
                                 "instrument missing (a site recipe that takes over, saves, reloads, then calls the proof)")
            t.upstream_failed = True
