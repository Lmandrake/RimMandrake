#!/usr/bin/env python3
"""selftest_peaceful_landing.py -- GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 (offline half).

Owner, 2026-10-02: "We need a way for gravship to land properly in settlement and not be seen as attacking."

A buyer-pit site (the Hutt slave pit first) is a trading post. Vanilla 1.6 decides "attack or visit" from data on the
site's SitePartDefs, in four places (read from the decompiled 1.6 Assembly-CSharp; anchors below):

  GravshipUtility.ArriveNewMap            attack iff parent is Settlement, or a Site whose parts ALL say
                                          considerEnteringAsAttack, and the parent's faction is someone else's
  CaravanArrivalAction_VisitSite.DoEnter  AffectRelationsOnAttacked iff ANY part says considerEnteringAsAttack
  TransportersArrivalAction_VisitSite     attack iff faction is someone else's and the MAIN part says it
  Site.PostMapGenerate                    detection-raid countdown unless a part disallowsAutomaticDetectionTimerStart
                                          or the map was spawned by a gravship landing
  Site.GravShipCanLandOn                  MainSitePartDef.gravShipsCanLandOn and no map yet

This test ports those predicates, evaluates them on every SitePartDef that carries RM_BuyerPitSiteExtension, checks the
quest node only ever hands such a site to a faction that is not hostile, and plants breaks that must go red. When the
decompile is on disk its source lines are matched against the ported expressions, so a game update that changes them
fails here instead of passing on a stale port.

Not covered (prior art, GravTide Docs/vanilla-traps.md): a full faction SETTLEMENT has no peaceful path in vanilla --
ArriveNewMap always attacks one, and a loaded settlement map with no hostile on it is destroyed by
SettlementDefeatUtility.CheckDefeated. The Hutt test site is a Site, so neither applies.

    python3 src/RimMandrake/KeelHoist/selftest_peaceful_landing.py
    python3 src/RimMandrake/KeelHoist/selftest_peaceful_landing.py --live   # A1: the RUNNING game loaded the fields;
                                       one read-only jawa/get_defs; exit 0 holds, 1 the game says otherwise, 2 UNMEASURED
"""
import copy
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
PIT_CS = os.path.join(HERE, "Source", "RM_PitBuyer.cs")
EXT = "RimMandrake.KeelHoist.RM_BuyerPitSiteExtension"
DECOMP = os.environ.get("RM_DECOMP_1_6", "/mnt/d/ClaudeWork/rimmandrake/SOORRAK_LOOP/full")
ANCHORS = [   # (file under the decompile, text that must appear verbatim) -- the expressions ported below
    ("RimWorld/GravshipUtility.cs", "(orGenerateMap.Parent is Settlement || (orGenerateMap.Parent is Site site2 && "
     "site2.parts.All((SitePart part) => part.def.considerEnteringAsAttack))) && orGenerateMap.Parent.Faction != null "
     "&& orGenerateMap.Parent.Faction != Faction.OfPlayer"),
    ("RimWorld.Planet/CaravanArrivalAction_VisitSite.cs",
     "if (site.parts.Any((SitePart part) => part.def.considerEnteringAsAttack))"),
    ("RimWorld.Planet/TransportersArrivalAction_VisitSite.cs",
     "if (site.Faction != null && site.Faction != Faction.OfPlayer && site.MainSitePartDef.considerEnteringAsAttack)"),
    ("RimWorld.Planet/Site.cs", "if (!parts.Any((SitePart p) => p.def.disallowsAutomaticDetectionTimerStart) && "
     "!map.wasSpawnedViaGravShipLanding)"),
    ("RimWorld.Planet/Site.cs", "if (MainSitePartDef.gravShipsCanLandOn)"),
    ("RimWorld/SitePartDef.cs", "public bool considerEnteringAsAttack = true;"),
    ("RimWorld/SitePartDef.cs", "public bool disallowsAutomaticDetectionTimerStart;"),
    ("RimWorld/SitePartDef.cs", "public bool gravShipsCanLandOn;"),
]
DEFAULTS = {"considerEnteringAsAttack": True, "disallowsAutomaticDetectionTimerStart": False, "gravShipsCanLandOn": False}
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _bool(node, field):
    el = node.find(field)
    if el is None or el.text is None:
        return DEFAULTS[field]
    t = el.text.strip().lower()
    if t not in ("true", "false"):
        raise ValueError("%s/%s is not a bool: %r" % (node.findtext("defName"), field, el.text))
    return t == "true"


def part_fields(node):
    return {f: _bool(node, f) for f in DEFAULTS}


def buyer_pit_parts():
    """-> {defName: (path, SitePartDef element)} for every SitePartDef in src/ carrying the buyer-pit extension."""
    out = {}
    for path in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("SitePartDef"):
            if any(li.get("Class") == EXT for li in d.iter("li")):
                out[d.findtext("defName")] = (path, d)
    return out


# ---- vanilla 1.6 predicates, ported (parts = list of field dicts; parts[0] is the main part) ----
def gravship_entry_is_attack(parts, parent_is_settlement, faction, player="player"):
    hit = parent_is_settlement or all(p["considerEnteringAsAttack"] for p in parts)
    return hit and faction is not None and faction != player


def caravan_entry_is_attack(parts):
    return any(p["considerEnteringAsAttack"] for p in parts)


def transporters_entry_is_attack(parts, faction, player="player"):
    return faction is not None and faction != player and parts[0]["considerEnteringAsAttack"]


def detection_countdown_starts(parts, via_gravship_landing):
    return not any(p["disallowsAutomaticDetectionTimerStart"] for p in parts) and not via_gravship_landing


def gravship_can_land(parts, has_map=False):
    return parts[0]["gravShipsCanLandOn"] and not has_map


def peaceful_findings(parts):
    """Every way the site would be treated as hostile on entry; [] is a trading post."""
    f = []
    if not gravship_can_land(parts):
        f.append("gravship cannot land")
    if gravship_entry_is_attack(parts, False, "keepers"):
        f.append("gravship landing is an attack")
    if caravan_entry_is_attack(parts):
        f.append("caravan entry is an attack")
    if transporters_entry_is_attack(parts, "keepers"):
        f.append("transport pods are an attack")
    for via in (True, False):
        if detection_countdown_starts(parts, via):
            f.append("detection raid countdown starts (%s)" % ("gravship" if via else "caravan"))
    return f


def faction_findings(cs):
    """The quest node must hand the site only to a faction that is not hostile to the player."""
    m = re.search(r"private static Faction FactionFor\(SitePartDef def\)\s*\{(.*?)\n        \}", cs, re.S)
    if not m:
        return ["FactionFor not found"]
    body, f = m.group(1), []
    if "!f.HostileTo(Faction.OfPlayer)" not in body:
        f.append("FactionFor may pick a hostile faction")
    if "SiteMaker.MakeSite(def, tile, faction)" not in cs:
        f.append("site is not made with FactionFor's faction")
    return f


def live(timeout=60):
    """A1: the running game's RUT_HuttSlavePit carries the shipped values (a MayRequire-gated def can silently not load)."""
    sys.path.insert(0, os.path.join(SRC, "RimMandrake", "Utils"))
    import live_def_check as L
    want = {"considerEnteringAsAttack": False, "disallowsAutomaticDetectionTimerStart": True, "gravShipsCanLandOn": True}
    reply, why = L._bridge("jawa/get_defs", {"defs": "SitePartDef/RUT_HuttSlavePit", "fields": ",".join(want)}, timeout)
    if reply is None:
        print("UNMEASURED: " + why)
        return 2
    recs = [d for d in (reply.get("defs") or []) if isinstance(d, dict)] if isinstance(reply, dict) else []
    if len(recs) != 1 or not isinstance(recs[0].get("found"), bool):
        print("UNMEASURED: not one get_defs record: %r" % (reply,))
        return 2
    d = recs[0]
    if d["found"] is not True:
        running = L.call_running_mods(timeout)
        if running is None or "mandrake.rm.keelhoist" not in running:
            print("UNMEASURED: RUT_HuttSlavePit not loaded and mandrake.rm.keelhoist is not in the running load (%s)"
                  % ("unread" if running is None else "%d mods" % len(running)))
            return 2
        print("FAIL: mandrake.rm.keelhoist is running but SitePartDef/RUT_HuttSlavePit did not resolve")
        return 1
    if not isinstance(d.get("fields"), dict):
        print("UNMEASURED: record has no fields map: %r" % (d,))
        return 2
    got = {k: str(d["fields"].get(k)).strip().lower() for k in want}
    bad = {k: got[k] for k, v in want.items() if got[k] != str(v).lower()}
    print(("FAIL: " if bad else "PASS: ") + "RUT_HuttSlavePit live fields %r" % got)
    return 1 if bad else 0


def main():
    # anchors: the port is only as good as its match to the game's code
    if os.path.isdir(DECOMP):
        for rel, text in ANCHORS:
            p = os.path.join(DECOMP, rel)
            body = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else ""
            check("decompile anchor %s: %s" % (rel, text[:48]), text in body, "not found in " + p)
    else:
        print("note  decompile not on disk (%s): anchors UNMEASURED, ported predicates trusted as committed" % DECOMP)

    # the predicates themselves, on vanilla defaults (a SitePartDef that says nothing is a raid target)
    dflt = [dict(DEFAULTS)]
    check("sanity: a default site part is an attack every way and gets a raid countdown by caravan",
          gravship_entry_is_attack(dflt, False, "x") and caravan_entry_is_attack(dflt)
          and transporters_entry_is_attack(dflt, "x") and detection_countdown_starts(dflt, False))
    check("sanity: a Settlement is an attack even when every part says no",
          gravship_entry_is_attack([dict(DEFAULTS, considerEnteringAsAttack=False)], True, "x"))
    check("sanity: own or factionless site is never an attack by gravship",
          not gravship_entry_is_attack(dflt, False, "player") and not gravship_entry_is_attack(dflt, False, None))

    parts = buyer_pit_parts()
    check("sanity: RUT_HuttSlavePit is found among buyer-pit site parts", "RUT_HuttSlavePit" in parts, sorted(parts))
    for name, (path, node) in sorted(parts.items()):
        fl = peaceful_findings([part_fields(node)])
        check("%s (%s): landing, caravan and pods are visits, no detection raid" % (name, os.path.relpath(path, SRC)),
              fl == [], fl)
        # planted breaks, on a copy (never the shipped file)
        for field, bad, must in (("considerEnteringAsAttack", "true", "gravship landing is an attack"),
                                 ("disallowsAutomaticDetectionTimerStart", "false", "detection raid countdown starts (caravan)"),
                                 ("gravShipsCanLandOn", "false", "gravship cannot land")):
            n2 = copy.deepcopy(node)
            el = n2.find(field)
            if el is None:
                el = ET.SubElement(n2, field)
            el.text = bad
            got = peaceful_findings([part_fields(n2)])
            check("break %s: %s=%s -> %s" % (name, field, bad, must), must in got, got)
        n3 = copy.deepcopy(node)
        n3.remove(n3.find("considerEnteringAsAttack"))
        check("break %s: considerEnteringAsAttack removed (vanilla default true) -> attack" % name,
              "gravship landing is an attack" in peaceful_findings([part_fields(n3)]))
        # a second, default part on the same site: gravship needs ALL to say attack, caravan needs ANY
        two = [part_fields(node), dict(DEFAULTS)]
        check("%s + a default part: gravship stays a visit, caravan turns attack (vanilla All vs Any)" % name,
              not gravship_entry_is_attack(two, False, "keepers") and caravan_entry_is_attack(two))

    cs = open(PIT_CS, encoding="utf-8").read()
    check("quest node gives the site only a non-hostile faction", faction_findings(cs) == [], faction_findings(cs))
    check("break: FactionFor drops the hostility filter -> red",
          "FactionFor may pick a hostile faction" in faction_findings(cs.replace(" && !f.HostileTo(Faction.OfPlayer)", "")))

    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(live() if "--live" in sys.argv[1:] else main())
