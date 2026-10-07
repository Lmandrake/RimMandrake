"""northstar_driver plan for IshkoDarkLandmarks (the suite in validation.py). Offline:
  python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod IshkoDarkLandmarks \\
      --plan src/RimUtinni/IshkoDarkLandmarks/northstar_plan.py
Live (bridge held, game up on the `ishko` tier with a quicktest world):
  python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod IshkoDarkLandmarks --tier ishko \\
      --plan src/RimUtinni/IshkoDarkLandmarks/northstar_plan.py \\
      --deploy-mod IshkoDarkLandmarks --deploy-mod AshkarrLandmarkArt

The mock below is an in-memory model of exactly what the suite asserts (get_defs readback, the
planet's tiles, AddLandmark's forced Required-anchor roll). It proves the SCRIPT, never the game.
ISHKO_MOCK_BREAK=<comma list> re-introduces one defect each, so every check can be seen red:
  wrong_pkg      a defName collision: RUT_LightlessSink resolves from another package
  no_anchor      AddLandmark leaves the tile without its Required anchor mutator
  shallow        mutatorChances comes back as bare type names (get_defs without deep=true)
The live tier MUST carry mandrake.rm.gimmesomeslack (JawaBench TypeLoad-fails without it and preflight REFUSES at game_loaded).
First live run 2026-10-07: 8 PASS in 3 s, recorded GREEN by the driver (see validation.py "LEARNED").
Dev tooling, never deployed."""
import os

from northstar_driver import site

MOD = "IshkoDarkLandmarks"
USE_SUITE = True
EXPECT_MODS = ("mandrake.rut.ishkolandmarks", "mandrake.rut.ashkarrlandmarkart")
NEED_GOD = False
RECT = None                 # world-level mod: the suite touches no map cells

_DEFS = {
    "RUT_LightlessSink": ("mountain", 0.08, "Hollow", ["IceCaves", "FoggyMutator", "AnimalLife_Decreased", "DryGround"]),
    "RUT_ShadowedOverhang": ("mountain", 0.08, "Chasm", ["IceCaves", "FoggyMutator", "AnimalLife_Decreased", "SunnyMutator"]),
    "RUT_ColdLavaTube": ("mountain", 0.06, "Cavern", ["LavaCaves", "IceCaves", "FoggyMutator", "AnimalLife_Decreased", "DryGround"]),
}
_ICON = {"RUT_LightlessSink": "Hollow", "RUT_ShadowedOverhang": "Chasm", "RUT_ColdLavaTube": "Cavern"}


def preflight(s):
    """Landmarks are Odyssey-only: without it every placement no-ops and every def is absent."""
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
        self.tiles = {i: {"water": i % 5 == 0, "landmark": "Cove" if i == 1 else None,
                          "mutators": ["Coast"] if i % 7 == 0 else []} for i in range(2000)}


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
    if tool == "jawa/get_defs":
        rows, nf = [], []
        for spec in str(p["defs"]).split(";"):
            ty, dn = spec.split("/")
            if ty != "LandmarkDef" or dn not in _DEFS:
                rows.append({"requested": spec, "found": False, "defName": dn})
                nf.append(spec)
                continue
            cat, comm, anchor, rest = _DEFS[dn]
            chances = [{"mutator": anchor, "chance": 1.0, "required": True}] + \
                      [{"mutator": m, "chance": 0.2, "required": False} for m in rest]
            if "shallow" in brk or not p.get("deep"):
                chances = ["MutatorChance"] * len(chances)
            pkg = "someone.else.landmarks" if ("wrong_pkg" in brk and dn == "RUT_LightlessSink") \
                else "mandrake.rut.ishkolandmarks"
            rows.append({"requested": spec, "found": True, "defName": dn, "defType": "LandmarkDef",
                         "packageId": pkg, "fields": {
                             "category": cat, "commonality": comm, "mutatorChances": chances,
                             "iconTexturePath": "World/Landmarks/Ashkarr/" + _ICON[dn]}})
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
                anchor = _DEFS[dn][2]
                if p.get("forced") and "no_anchor" not in brk and anchor not in w.tiles[i]["mutators"]:
                    w.tiles[i]["mutators"].append(anchor)
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
        for i in _ids(p):
            w.tiles[i]["mutators"] = [m for m in w.tiles[i]["mutators"] if m not in str(p.get("mutators")).split(",")]
        return {"success": True}
    return None
