#!/usr/bin/env python3
"""Offline selftest for CrackedLands's validation.static_checks (no game, no bridge).

static_checks() was reachable only from validation.py's __main__, so no suite run asserted it. This runs it
green on the shipped tree, then proves the tarruq-call component (CRACKEDLANDS_FIVE_BEATS_AUDIO_1) can go red:
call removed, call naming a SoundDef Core does not ship.
Run: python3 src/RimMandrake/CrackedLands/selftest_crackedlands_static.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


bad = V.static_checks()
check("shipped tree: static_checks green", not bad, "; ".join(bad))
xml = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_IrqitTarruq.xml"), encoding="utf-8").read()
check("shipped tarruq call green", V._tarruq_call_findings(xml) == [])
check("sanity: shipped XML carries the call", "<soundCall>Pawn_Muffalo_Call</soundCall>" in xml)
gone = xml.replace("<soundCall>Pawn_Muffalo_Call</soundCall>", "")
check("break: call removed -> red", any("no soundCall" in f for f in V._tarruq_call_findings(gone)))
if os.path.isdir(V.VANILLA_SOUNDDEF_DIR):
    typo = xml.replace("<soundCall>Pawn_Muffalo_Call</soundCall>", "<soundCall>Pawn_Tarruq_Call</soundCall>")
    check("break: non-Core SoundDef -> red", any("not a Core SoundDef" in f for f in V._tarruq_call_findings(typo)))
else:
    print("UNMEASURED  non-Core SoundDef break (no RimWorld install visible)")


# CRACKEDLANDS_SALVAGE_CLAIM_CREW_1: the crew data check can go red.
check("shipped claim crew data green", V._claim_crew_findings() == [])
prof = open(os.path.join(HERE, "Defs", "RM_ClaimCrewProfileDefs", "RM_ClaimCrew_Scavengers.xml"), encoding="utf-8").read()
check("break: Salvagers (a permanent enemy) in the crew -> red",
      any("Salvagers" in f for f in V._claim_crew_findings(profile_xml=prof.replace("OutlanderRoughPig", "Salvagers"))))
check("break: text without its faction slot -> red",
      any("arrivalText" in f for f in V._claim_crew_findings(profile_xml=prof.replace("from {0} has walked", "has walked"))))
utinni = os.path.normpath(os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "ClaimCrew_CrackedLands.xml"))
patch = open(utinni, encoding="utf-8").read()
check("break: Utinni patch naming a dead faction -> red",
      any("no real faction" in f for f in V._claim_crew_findings(patch_xml=patch.replace("RUT_Jawa_IndigenousTribes", "RUT_Jawa_Gone"))))
check("break: a Replace carrying a sibling field -> red",
      any("also carries" in f for f in V._claim_crew_findings(patch_xml=patch.replace(
          "</factionDefs>", "</factionDefs><arrivalLabel>x</arrivalLabel>"))))


# FLOOD_DRIVER_OWNERSHIP_CONTRACT_1 A2: the flood driver writes FlowWorks fill only through the outcome contract,
# never the bool TrySetDriverFill (whose false conflates NotOwned with Refused).
import re  # noqa: E402

OLD_BOOL = re.compile(r"\bTrySetDriverFill\s*\(")


def bool_driver_calls(text):
    return [ln.strip() for ln in text.splitlines() if OLD_BOOL.search(ln) and not ln.strip().startswith("//")]


src_dir = os.path.join(HERE, "Source")
calls, outcome_calls = [], 0
for dp, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".cs") and "/obj/" not in dp.replace("\\", "/") + "/":
            t = open(os.path.join(dp, f), encoding="utf-8").read()
            calls += ["%s: %s" % (f, c) for c in bool_driver_calls(t)]
            outcome_calls += len(re.findall(r"\bTrySetDriverFillOutcome\s*\(", t))
check("contract: no bool TrySetDriverFill call in CrackedLands source", calls == [], "; ".join(calls))
check("sanity: the recede restores through TrySetDriverFillOutcome", outcome_calls >= 1, outcome_calls)
check("break: the old bool call -> red",
      bool_driver_calls("(k, prior) => excavation?.TrySetDriverFill(Cell(k), prior));") != [])

# FLOOD_SOAK_MARKERS_BUILD_AIMED_AT_CANALS: the map-control wiring reader is green on the tree and goes red on each break.
check("map controls: wiring green", V._map_control_findings() == [], "; ".join(V._map_control_findings()))
_flood = open(os.path.join(HERE, "Source", "RM_MapComponent_CanyonFlood.cs"), encoding="utf-8").read()
_xml = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_BiomeMapControls.xml"), encoding="utf-8").read()
_soak = open(os.path.join(HERE, "Source", "MapControls", "Building_RM_SoakZone.cs"), encoding="utf-8").read()
check("break: biome gate not lifted -> red", any("Active does not lift" in f for f in V._map_control_findings(
    flood=_flood.replace("(aimedAt.IsValid || RM_BiomeMapControls.AnyClockTrigger(map))", "false"))))
check("break: aim not scribed -> red", any("not scribed" in f for f in V._map_control_findings(
    flood=_flood.replace('"aimedAt"', '"aimedAtX"'))))
check("break: buildable trigger -> red", any("buildable" in f for f in V._map_control_findings(
    defs_xml=_xml.replace("<label>flood trigger</label>", "<label>flood trigger</label><designationCategory>Misc</designationCategory>"))))
check("break: soak zone never ticks -> red", any("tick Rare" in f for f in V._map_control_findings(
    defs_xml=_xml.replace("<tickerType>Rare</tickerType>", ""))))
check("break: soak zone ungated -> red", any("soakZonesEnabled" in f for f in V._map_control_findings(
    soak=_soak.replace('if (!RM_CrackedLandsSettings.soakZonesEnabled) return', 'if (false) return'))))

# CRACKEDLANDS_THREE_HEIGHT_FLORA_1: "Art is reviewed on a sheet before the defs ship." Every flora def's texPath
# resolves to a shipped PNG, the sheet holds a row for that def whose reviewed picture IS that PNG (sha256), and
# prereview.py check passes on the sheet. Goes red if the PNG is deleted or swapped, the row or the record is missing.
import hashlib  # noqa: E402
import subprocess  # noqa: E402
import xml.etree.ElementTree as ET  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FLORA_XML = os.path.join(HERE, "Defs", "ThingDefs_Plants", "RM_ThreeHeightFlora.xml")
FLORA_SHEET = os.path.join(REPO, "Transient", "biome_ffar", "crackedlands_three_height_flora_sheet_2026-11-03.html")
PREREVIEW = os.path.join(REPO, "src", "RimMandrake", "Utils", "art", "prereview.py")
FLORA_DEFS = ("RM_QirraMat", "RM_TalusClasp")
sys.path.insert(0, os.path.dirname(PREREVIEW))
import prereview as PR  # noqa: E402


def _flora_art_findings(tex_root=os.path.join(HERE, "Textures"), sheet=FLORA_SHEET, flora_xml=FLORA_XML):
    out = []
    root = ET.parse(flora_xml).getroot()
    texs = {d.findtext("defName"): d.findtext("graphicData/texPath") for d in root.iter("ThingDef")}
    for dn in FLORA_DEFS:
        if dn not in texs:
            out.append("%s: no ThingDef" % dn)
            continue
        if not texs[dn]:
            out.append("%s: no graphicData/texPath" % dn)
            continue
        png = os.path.join(tex_root, *texs[dn].split("/")) + ".png"
        if not os.path.isfile(png):
            out.append("%s: texPath %s resolves to no PNG" % (dn, texs[dn]))
            continue
        if not os.path.isfile(sheet):
            out.append("review sheet missing: %s" % sheet)
            continue
        items = {str(it.get("id")): it for it in (PR.items_of(open(sheet, encoding="utf-8").read()) or [])}
        if dn not in items:
            out.append("%s: no row on the review sheet" % dn)
            continue
        sha = hashlib.sha256(open(png, "rb").read()).hexdigest()
        if sha not in (items[dn].get("fulls") or {}):
            out.append("%s: shipped PNG %s is not the picture reviewed on the sheet" % (dn, sha[:12]))
    if os.path.isfile(sheet):
        r = subprocess.run([sys.executable, PREREVIEW, "check", sheet], capture_output=True, text=True)
        if r.returncode != 0:
            out.append("prereview check refused the sheet: %s" % (r.stdout + r.stderr).strip()[:200])
        else:
            rec = os.path.splitext(sheet)[0] + ".prereview.json"
            import json
            rows = json.load(open(rec, encoding="utf-8")).get("rows", {})
            for dn in FLORA_DEFS:
                if (rows.get(dn) or {}).get("verdict") not in ("OK", "FIXED"):
                    out.append("%s: prereview verdict %r, not OK/FIXED" % (dn, (rows.get(dn) or {}).get("verdict")))
    return out


_fa = _flora_art_findings()
check("flora art: shipped PNGs are the sheet-reviewed pictures, prereview OK", _fa == [], "; ".join(_fa))
import shutil  # noqa: E402
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as _td:
    _tex = os.path.join(_td, "Textures")
    shutil.copytree(os.path.join(HERE, "Textures", "Things", "Plant"), os.path.join(_tex, "Things", "Plant"))
    _q = os.path.join(_tex, "Things", "Plant", "RM_QirraMat.png")
    os.remove(_q)
    check("break: qirra PNG deleted -> red", any("RM_QirraMat: texPath" in f for f in _flora_art_findings(tex_root=_tex)))
    with open(_q, "wb") as fh:
        fh.write(open(os.path.join(_tex, "Things", "Plant", "RM_TalusClasp.png"), "rb").read())
    check("break: qirra PNG swapped for unreviewed art -> red",
          any("RM_QirraMat: shipped PNG" in f for f in _flora_art_findings(tex_root=_tex)))
    _sh = os.path.join(_td, os.path.basename(FLORA_SHEET))
    shutil.copy(FLORA_SHEET, _sh)
    check("break: sheet without its prereview record -> red",
          any("prereview check refused" in f for f in _flora_art_findings(sheet=_sh)))
    check("break: no review sheet -> red",
          any("review sheet missing" in f for f in _flora_art_findings(sheet=os.path.join(_td, "none.html"))))
    _x = os.path.join(_td, "flora.xml")
    open(_x, "w", encoding="utf-8").write(open(FLORA_XML, encoding="utf-8").read().replace(
        "<texPath>Things/Plant/RM_TalusClasp</texPath>", "<texPath>Things/Plant/RM_TalusClaspX</texPath>"))
    check("break: talus texPath to nothing -> red",
          any("RM_TalusClasp: texPath" in f for f in _flora_art_findings(flora_xml=_x)))
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
