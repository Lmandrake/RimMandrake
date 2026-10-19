"""validation.py -- modcheck suite for RimStarWars: Sith Line (mandrake.rsw.sithline).

SANGUOPHAGE_KEPT_UNREACHABLE_1, first functional script (design/RimMandrake/sith_line_design.md §7).
Walk: design/validation_walks/RimStarWars/SithLine.md.

CHAINS
  defs_resolve        every def under Defs/ resolves live; a control reads notFound.
  settings_roundtrip  every `public static` field of RSW_SithLineSettings: default / write / restore.
  defs                must-be-true bars 1-5 and 13 read from the live defs (label, no implanter, unbuildable, quests off,
                      scenario hidden, Anzati copies).
  live                bars 6-12, 14, 15 and the lair (9-10, waking) (recruit guard, absorb, inquisitors, Anzati alias, extraction): UNMEASURED until
                      a JawaBench tool spawns a pawn of a kind and reads guest/genes/group fields (each says why).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
SETTINGS = "RimMandrake.StarWars.SithLine.RSW_SithLineSettings"
CONTROL_ABSENT = "ThingDef/RSW_SithLineNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")
SITH_BUILDINGS = ("DeathrestCasket", "Hemopump", "HemogenAmplifier", "GlucosoidPump", "PsychofluidPump", "DeathrestAccelerator")
ANZATI_SWAP = {"Hemogenic": "RSW_AnzatiHemogenic", "HemogenDrain": "RSW_AnzatiHemogenDrain",
               "Bloodfeeder": "RSW_AnzatiBloodfeeder", "Coagulate": "RSW_AnzatiCoagulate", "Deathrest": "RSW_AnzatiDeathrest"}


def shipped_defs():
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text:
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    src = open(os.path.join(HERE, "Source", "RSW_SithLineSettings.cs"), encoding="utf-8").read()
    body = src.split("class RSW_SithLineSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def _code(path):
    return re.sub(r"<!--.*?-->", "", open(path, encoding="utf-8").read(), flags=re.S)


def static_checks():
    bad = []
    if len(SHIPPED) < 8:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 8:
        return ["settings probe found %d fields (sanity probe failed)" % len(fields)]
    src = open(os.path.join(HERE, "Source", "RSW_SithLineSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RSW_SithLine.csproj"), encoding="utf-8").read()
    allsrc = ""
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs"):
            allsrc += open(os.path.join(HERE, "Source", fn), encoding="utf-8").read()
            if 'Compile Include="%s"' % fn not in proj:
                bad.append("%s is not in the csproj (compiles into nothing, no error)" % fn)
    kern = open(os.path.join(HERE, "Source", "RSW_SithLineKernel.cs"), encoding="utf-8").read()
    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine)", kern, re.M):
        bad.append("the kernel imports Verse/RimWorld/Unity (the selftest compiles it standalone)")
    # every gate name used in XML exists in the C# switch
    gates = set(re.findall(r'case "(\w+)":', open(os.path.join(HERE, "Source", "RSW_PatchOperationSithSetting.cs"), encoding="utf-8").read()))
    for fn in os.listdir(os.path.join(HERE, "Patches")):
        code = _code(os.path.join(HERE, "Patches", fn))
        if "MayRequire" in code:
            bad.append("%s carries MayRequire (inert on a top-level Operation)" % fn)
        for g in re.findall(r"<setting>(\w+)</setting>", code):
            if g not in gates:
                bad.append("%s gates on %s, which RSW_PatchOperationSithSetting does not know" % (fn, g))
            if g not in fields:
                bad.append("%s gates on %s, which is not a setting field" % (fn, g))
    closed = _code(os.path.join(HERE, "Patches", "RSW_SithClosedRoutes.xml"))
    for need in ('QuestScriptDef[defName="SanguophageMeetingHost"]', 'QuestScriptDef[defName="SanguophageShip"]',
                 'ScenarioDef[defName="Sanguophage"]', 'li[text()="XenogermReimplanter"]', 'FactionDef[defName="Sanguophages"]',
                 'ThingDef[defName="DeathrestCasket"]', 'ThingDef[@Name="DeathrestBuildingBase"]', "canGenerateDefaultDesignator",
                 "claimable"):
        if need not in closed:
            bad.append("RSW_SithClosedRoutes.xml lost %s" % need)
    rep = _code(os.path.join(HERE, "Patches", "RSW_AnzatiRepoint.xml"))
    for v, c in ANZATI_SWAP.items():
        if 'li[text()="%s"]' % v not in rep or "<li>%s</li>" % c not in rep:
            bad.append("Anzati repoint lost %s -> %s" % (v, c))
        if ("GeneDef", c) not in SHIPPED:
            bad.append("Anzati copy %s is not defined" % c)
    for b in SITH_BUILDINGS:
        if '"%s"' % b not in allsrc:
            bad.append("C# SithBuildings list lost %s (casket minifiedDef is nulled there)" % b)
    # the relabel file is what the generator writes
    gen = os.path.join(HERE, "gen_relabels.py")
    out = os.path.join(HERE, "Patches", "RSW_SithRelabel.xml")
    before = open(out, encoding="utf-8").read()
    try:
        subprocess.run([sys.executable, gen], check=True, capture_output=True, timeout=30)
        if open(out, encoding="utf-8").read() != before:
            bad.append("Patches/RSW_SithRelabel.xml was stale against gen_relabels.py (now regenerated; commit it)")
    except (subprocess.SubprocessError, OSError) as e:
        bad.append("gen_relabels.py failed: %s" % e)
    q = _code(os.path.join(HERE, "Defs", "QuestScriptDefs", "RSW_SithLairRumour.xml"))
    for need in ("RSW_QuestNode_GetAbyssSiteTile", "<tag>RSW_SithLair</tag>", "QuestNode_WorldObjectTimeout", "<autoAccept>true</autoAccept>"):
        if need not in q:
            bad.append("the lair rumour lost %s" % need)
    sp = _code(os.path.join(HERE, "Defs", "SitePartDefs", "RSW_SithLair.xml"))
    if "<linkWithSite>RSW_SithLair</linkWithSite>" not in sp or "RSW_GenStep_SithLair" not in sp:
        bad.append("the lair genstep is no longer linked to the RSW_SithLair site part")
    lair = open(os.path.join(HERE, "Source", "RSW_SithLair.cs"), encoding="utf-8").read()
    if '"RM_Abyss"' not in lair or "MayRequire" in lair:
        bad.append("the lair tile node must find RM_Abyss by def lookup, never MayRequire")
    pf = os.path.join(SRC, "RimUtinni", "PawnFlavor", "Patches", "PawnFlavorPhase2_Xenotype.xml")
    if os.path.isfile(pf) and "<label>Sanguophage</label>" in open(pf, encoding="utf-8").read():
        bad.append("PawnFlavor still relabels Sanguophage to 'Sanguophage' (it loads after this mod and overwrites the Sith name)")
    if not os.path.isfile(os.path.join(SRC, "..", "design", "validation_walks", "RimStarWars", "SithLine.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "..", "RimMandrake", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _flat(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            for s in _flat(v):
                yield s
    elif isinstance(x, (list, tuple)):
        for v in x:
            for s in _flat(v):
                yield s


def _build_suite():
    suite = Suite("SithLine")
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

    def _row(t, defspec, fields, deep=False):
        r = t.bridge_call("jawa/get_defs", defs=defspec, fields=fields, deep=deep, limit=2)
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is False or r.get("notFound") or int(r.get("foundCount", 0)) != 1:
            raise ExpectationFailed("get_defs %s unreadable or absent: %r" % (defspec, r))
        rows = r.get("defs") or []
        return (rows[0].get("fields") or {}) if rows else {}

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t) and (not isinstance(r, dict) or int(r.get("foundCount", 0)) != 0 or not r.get("notFound")):
                raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=20)
            if _live(t) and (not isinstance(r, dict) or r.get("notFound") or int(r.get("foundCount", 0)) != len(names)):
                raise ExpectationFailed("%d shipped defs, foundCount=%r notFound=%r" % (len(names), (r or {}).get("foundCount"), (r or {}).get("notFound")))

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) * 0.5)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    if not _same(ty, _raw(t, "get", field).get("value"), new):
                        raise ExpectationFailed("%s: wrote %s, read back different" % (field, new))
                finally:
                    _raw(t, "set", field, old)
                if not _same(ty, _raw(t, "get", field).get("value"), old):
                    raise ExpectationFailed("%s did not restore to %r" % (field, old))

    @suite.chain("defs")
    def defs(t):
        with t.component("xenotype_label", toggle="reskinText"):
            f = _row(t, "XenotypeDef/Sanguophage", "label")
            if _live(t) and str(f.get("label")).lower() != "sith adept":
                raise ExpectationFailed("XenotypeDef Sanguophage label is %r (PawnFlavor overwrote it, or the relabel did not land)" % f.get("label"))
        with t.component("no_reimplanter", toggle="vanillaQuestsOff"):
            if _live(t):
                f = _row(t, "XenotypeDef/Sanguophage", "genes", deep=True)
                blob = " ".join(_flat(f))
                if "XenogermReimplanter" in blob:
                    raise ExpectationFailed("the Sith xenotype still carries XenogermReimplanter")
                if "Hemogenic" not in blob:
                    _unmeasured(t, "get_defs did not list the xenotype's genes by name, so absence proves nothing: %s" % blob[:120])
        with t.component("unbuildable", toggle="sithBuildingsUnbuildable"):
            if _live(t):
                for b in SITH_BUILDINGS:
                    f = _row(t, "ThingDef/" + b, "canGenerateDefaultDesignator,minifiedDef")
                    if str(f.get("canGenerateDefaultDesignator")).lower() != "false":
                        raise ExpectationFailed("%s canGenerateDefaultDesignator=%r" % (b, f.get("canGenerateDefaultDesignator")))
                    if f.get("minifiedDef") not in (None, "", "null", "None"):
                        raise ExpectationFailed("%s minifiedDef=%r (reinstallable)" % (b, f.get("minifiedDef")))
                f = _row(t, "ThingDef/RSW_AnzatiDeathrestCasket", "canGenerateDefaultDesignator")
                if str(f.get("canGenerateDefaultDesignator")).lower() != "true":
                    raise ExpectationFailed("the Anzati casket lost its build command")
        with t.component("vanilla_quests_off", toggle="vanillaQuestsOff"):
            if _live(t):
                for q in ("SanguophageMeetingHost", "SanguophageShip"):
                    f = _row(t, "QuestScriptDef/" + q, "rootSelectionWeight")
                    if float(f.get("rootSelectionWeight", -1)) != 0.0:
                        raise ExpectationFailed("%s rootSelectionWeight=%r" % (q, f.get("rootSelectionWeight")))
        with t.component("scenario_hidden", toggle="vanillaQuestsOff"):
            if _live(t):
                f = _row(t, "ScenarioDef/Sanguophage", "scenario", deep=True)
                blob = " ".join(_flat(f))
                if "showInUI" not in blob:
                    _unmeasured(t, "get_defs does not expand ScenarioDef.scenario.showInUI: %s" % blob[:120])
        with t.component("anzati_copies", beyond_toggle=True):
            if _live(t):
                f = _row(t, "XenotypeDef/RSW_RimMandrakeAnzati", "genes", deep=True)
                blob = " ".join(_flat(f))
                if "RSW_AnzatiHemogenic" in blob:
                    if any(">%s<" % v in blob or v == x for v in ANZATI_SWAP for x in blob.split()):
                        raise ExpectationFailed("the Anzati still carry a vanilla blood/trance gene: %s" % blob[:160])
                elif "Hair_" in blob or "Body_" in blob:
                    raise ExpectationFailed("the Anzati genes read by name but lack RSW_AnzatiHemogenic: %s" % blob[:160])
                else:
                    _unmeasured(t, "get_defs did not list the Anzati genes by name: %s" % blob[:120])

    @suite.chain("live")
    def live(t):
        for name, toggle, why in (
            ("recruit_guard", "neverRecruitable", "needs a JawaBench tool that spawns a Sith prisoner and reads guest.Recruitable before and after a dev toggle"),
            ("join_routes_refused", "neverRecruitable", "needs a JawaBench [Tool] that calls EnslavePrisoner, Recruit and SetFaction(player) on a Sith prisoner and reports the faction after"),
            ("absorb_blocked", "blockXenogermAbsorb", "needs a tool that reads GeneUtility.CanAbsorbXenogerm for a downed Sith"),
            ("empire_inquisitor", "inquisitorRaids", "needs a tool that generates an Empire Combat group at 2000 points with the chance forced to 1 and lists its kinds"),
            ("no_trader_inquisitor", "inquisitorRaids", "needs the same group read on an Empire Trader group"),
            ("anzati_defof_alias", None, "needs a tool that spawns an Anzati and reads HasActiveGene(Hemogenic) and IsBloodfeeder"),
            ("extraction_allowed", None, "needs a gene-extraction run on a captured Sith adept"),
            ("lair_gen", "lairRumours", "needs the rumour forced on a map with an RM_Abyss tile in range (the frozen planet has none until the paint-once pass), then a census of the site map: 1 sarcophagus, 1 Sith with the Deathrest hediff, >=2 bound devices, the shelf"),
            ("lair_no_abyss", "lairRumours", "needs a tool that reads the rumour's TestRun on a map with no Abyss tile in range"),
            ("lair_wake", "lairRumours", "needs a lair map: strike the sleeper (broken trance), enter the sanctum, or wait 6-10 h"),
        ):
            kw = {"toggle": toggle} if toggle else {"beyond_toggle": True}
            with t.component(name, **kw):
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
