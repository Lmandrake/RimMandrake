"""northstar_driver plan for Salvation Rites (the whole suite in validation.py: the research
gate, every shipped def, and Ishko's three landmarks). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Rites \\
      --plan src/RimUtinni/Rites/northstar_plan.py
Live (bridge held, game up on the `rites` tier with a quicktest world):
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Rites --tier rites \\
      --plan src/RimUtinni/Rites/northstar_plan.py \\
      --deploy-mod Rites --deploy-mod AshkarrLandmarkArt

The mock below is an in-memory model of exactly what the suite asserts (get_defs readback of every
def in Defs/, the research gate, the planet's tiles, AddLandmark's forced Required-anchor roll). It
proves the SCRIPT, never the game. ISHKO_MOCK_BREAK=<comma list> re-introduces one defect each, so
every Ishko check can be seen red:
  wrong_pkg      a defName collision: RUT_LightlessSink resolves from another package
  no_anchor      AddLandmark leaves the tile without its Required anchor mutator
  shallow        mutatorChances comes back as bare type names (get_defs without deep=true)
  no_restore     world_mutators_set does nothing, so the post-run restore cannot verify
The live tier MUST carry mandrake.rm.gimmesomeslack (JawaBench TypeLoad-fails without it and preflight REFUSES at game_loaded).
Ishko's landmarks were their own mod (mandrake.rut.ishkolandmarks) until 2026-10-22; its 2026-10-07 live GREEN
(8 PASS) is at that retired package and an old hash. This mod has no live run of the merged suite yet.
Dev tooling, never deployed."""
import os

from modcheck import shipped_defs
from northstar_driver import site

MOD = "Rites"
USE_SUITE = True
PACKAGE_ID = "mandrake.rut.rites"
EXPECT_MODS = (PACKAGE_ID, "mandrake.rut.antiquities", "mandrake.rut.ashkarrlandmarkart")
NEED_GOD = False
RECT = None                 # research and world-level only: the suite touches no map cells

def _xml_defs():
    """The mock reads the SAME XML the suite checks, so its chances can never drift from the
    defs (GPT review 2026-10-22, #8: the old hand-copied table gave every optional 0.2)."""
    import xml.etree.ElementTree as ET
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for el in ET.parse(os.path.join(here, "Defs", "RUT_IshkoLandmarks.xml")).getroot().findall("LandmarkDef"):
        chances = []
        for m in el.find("mutatorChances"):
            req = (m.get("Required") or "").lower() == "true"
            chances.append({"mutator": m.tag, "chance": 1.0 if req else float(m.text), "required": req})
        out[el.findtext("defName")] = (el.findtext("category"), float(el.findtext("commonality")), chances)
    return out


_DEFS = _xml_defs()
_ICON = {"RUT_LightlessSink": "Hollow", "RUT_ShadowedOverhang": "Chasm", "RUT_ColdLavaTube": "Cavern"}
# every def the mod ships: (type, name) -> {leafTag: text}, read from the same Defs/ the suite parses
_SHIPPED = dict(((ty, n), leaf) for ty, n, leaf in shipped_defs.parse(os.path.dirname(os.path.abspath(__file__))))
# the research gate: ordinary and hidden prerequisites of the one tier the suite exercises
_RESEARCH = {"RUT_Rites_ConduitChoir": (("RUT_Rites_ScrapShrine",), ("RUT_Antiq_Language",))}


def preflight(s):
    """Ishko's landmarks are Odyssey-only: without it every placement no-ops and those defs are absent."""
    bad = []
    try:
        site.dlc_status(s)
    except Exception as ex:                                    # noqa: BLE001
        bad.append("dlc_status: %s" % ex)
    return bad


def _breaks():
    return set(x for x in os.environ.get("ISHKO_MOCK_BREAK", "").split(",") if x)


class _World(object):
    def __init__(self):
        # tile -> {"water": bool, "landmark": str|None, "mutators": [str]}
        # tile 2 already carries an anchor (Hollow): the suite must skip it as a candidate.
        self.tiles = {i: {"water": i % 5 == 0, "landmark": "Cove" if i == 1 else None,
                          "mutators": ["Coast"] if i % 7 == 0 else (["Hollow"] if i == 2 else [])}
                      for i in range(2000)}


def _row(i, t):
    return {"tile": i, "waterCovered": t["water"], "landmark": t["landmark"],
            "mutators": [{"def": m} for m in t["mutators"]], "mutatorCount": len(t["mutators"])}


def _ids(p):
    ids = [int(x) for x in str(p.get("tiles") or "").split(",") if x.strip()]
    if p.get("range"):
        a, b = [int(x) for x in str(p["range"]).split("-")]
        ids += list(range(a, b + 1))
    return ids


def mock_extension(game, tool, p):
    brk = _breaks()
    w = getattr(game, "_ishko", None)
    if w is None:
        w = game._ishko = _World()
    if tool == "jawa/research_finish_project":
        done = game.__dict__.setdefault("_rites_done", set())
        was = p.get("project") in done
        done.add(p.get("project"))
        return {"success": True, "project": p.get("project"), "wasAlreadyFinished": was}
    if tool == "jawa/research_availability":
        done = game.__dict__.setdefault("_rites_done", set())
        pre, hidden = _RESEARCH.get(p.get("project"), ((), ()))
        pre_ok = all(x in done for x in pre)
        return {"success": True, "project": p.get("project"), "prerequisitesCompleted": pre_ok,
                "canStartNow": pre_ok and all(x in done for x in hidden),
                "unfinishedPrerequisites": [x for x in pre if x not in done]}   # ordinary ones only, like the tool
    if tool == "jawa/get_defs":
        want = [f for f in str(p.get("fields") or "").split(",") if f]
        rows, nf = [], []
        for spec in str(p["defs"]).split(";"):
            ty, dn = spec.split("/")
            if (ty, dn) not in _SHIPPED:
                rows.append({"requested": spec, "found": False, "defName": dn})
                nf.append(spec)
                continue
            pkg = "someone.else.landmarks" if ("wrong_pkg" in brk and dn == "RUT_LightlessSink") else PACKAGE_ID
            fields = dict((f, _SHIPPED[(ty, dn)].get(f)) for f in want)
            if ty == "LandmarkDef" and dn in _DEFS:
                cat, comm, chances = _DEFS[dn]
                chances = [dict(c) for c in chances]
                if "shallow" in brk or not p.get("deep"):
                    chances = ["MutatorChance"] * len(chances)
                fields.update({"category": cat, "commonality": comm, "mutatorChances": chances,
                               "iconTexturePath": "World/Landmarks/Ashkarr/" + _ICON[dn]})
                fields = dict((f, fields.get(f)) for f in want)
            rows.append({"requested": spec, "found": True, "defName": dn, "defType": ty,
                         "packageId": pkg, "fields": fields})
        return {"success": True, "foundCount": len(rows) - len(nf), "notFound": nf, "defs": rows}
    if tool == "jawa/world_mutators_get":
        ids = _ids(p)
        lim = int(p.get("limit") or 100)
        return {"success": True, "tiles": [_row(i, w.tiles[i]) for i in ids[:lim]], "limitHit": len(ids) > lim}
    if tool == "jawa/world_landmarks_set":
        ids = _ids(p)
        if p.get("action") == "add":
            dn = p.get("def")
            if dn not in _DEFS:
                return {"success": False, "message": "No LandmarkDef '%s'." % dn}
            for i in ids:
                w.tiles[i]["landmark"] = dn
                req = [c["mutator"] for c in _DEFS[dn][2] if c["required"]]
                opt = [c["mutator"] for c in _DEFS[dn][2] if not c["required"]]
                if p.get("forced") and "no_anchor" not in brk:
                    for a in req:
                        if a not in w.tiles[i]["mutators"]:
                            w.tiles[i]["mutators"].append(a)
                # deterministic stand-in for one Rand.Chance optional roll, so every mock run
                # exercises the restore of a mutator the suite did not ask for
                if opt and opt[0] not in w.tiles[i]["mutators"]:
                    w.tiles[i]["mutators"].append(opt[0])
            return {"success": True, "added": len(ids), "removed": 0,
                    "validity": [{"tile": i, "isValidTile": False, "settlementAtOrAdjacent": False} for i in ids],
                    "tiles": [_row(i, w.tiles[i]) for i in ids[:8]]}
        n = 0
        for i in ids:
            if w.tiles[i]["landmark"]:
                w.tiles[i]["landmark"] = None
                n += 1
        return {"success": True, "added": 0, "removed": n}
    if tool == "jawa/world_mutators_set":
        names = [m for m in str(p.get("mutators") or "").split(",") if m]
        if "no_restore" in brk:
            return {"success": True}
        for i in _ids(p):
            if p.get("action") == "add":
                w.tiles[i]["mutators"] += [m for m in names if m not in w.tiles[i]["mutators"]]
            else:
                w.tiles[i]["mutators"] = [m for m in w.tiles[i]["mutators"] if m not in names]
        return {"success": True}
    return None
