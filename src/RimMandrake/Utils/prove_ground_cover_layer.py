"""Proof for ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS: ground cover draws under the caps.

Owner, typed 2026-10-14: "Lower all such plants in all biomes. Small ground cover on the appropriate layer."
A plant on FloorEmplacement (7) draws under every LowPlant (11) plant (Plant.Print tilt 0.1 < layer
spacing 0.366; derivation in design/RimMandrake/plant_draw_layers_2026-10-14.md), so the draw order the
owner asked to look at follows from the layer the renderer reads.

  --offline [--from-json F]  (WSL python3, ~5 min) rebuild the census (plant_draw_layers.census, FULL list,
             repo mandrake.* mods + patches): every GROUND_COVER plant is FloorEmplacement, the Rot caps
             LowPlant, and the committed live list (LIST) equals the fresh census's GROUND_COVER names.
  (default)  (Windows python.exe, game up) jawa/get_defs reads the RESOLVED altitudeLayer of every plant in
             LIST plus the caps: every loaded one is FloorEmplacement, every mandrake-owned one is loaded,
             the caps are LowPlant.
  --write-list  (offline) rewrite LIST from the fresh census.

Exit 0 holds, 1 does not, 2 unmeasured.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIST = os.path.join(REPO, "infrastructure", "state", "live_proofs",
                    "ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS.ground_cover.txt")
LOW = "FloorEmplacement"
CAPS = ("RM_TollukCap", "RM_Wrinklecap", "RM_VioletWimple")   # the Rot caps of the doc's look list


def read_list():
    """[(defName, package)] from LIST; lines are `defName<TAB>package`, # comments."""
    out = []
    for ln in open(LIST, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            name, pkg = ln.split("\t")
            out.append((name, pkg))
    return out


def offline(argv):
    sys.path.insert(0, HERE)
    import plant_draw_layers as P
    if "--from-json" in argv:
        rows = json.load(open(argv[argv.index("--from-json") + 1]))["rows"]
    else:
        rows, _ = P.census()
    by = {r["defName"]: r for r in rows}
    gc = sorted((r["defName"], r["package"]) for r in rows if r["class"] == "GROUND_COVER")
    if len(gc) < 20 or len(rows) < 200:
        print("UNMEASURED: census saw %d plants, %d ground cover (instrument blind?)" % (len(rows), len(gc)))
        return 2
    bad = ["%s (%s) is %s" % (n, p, by[n]["altitudeLayer"]) for n, p in gc if by[n]["altitudeLayer"] != LOW]
    bad += ["cap %s is %s" % (c, by[c]["altitudeLayer"] if c in by else "absent")
            for c in CAPS if c not in by or by[c]["altitudeLayer"] != "LowPlant"]
    if "--write-list" in argv:
        with open(LIST, "w", encoding="utf-8") as f:
            f.write("# GROUND_COVER plants from plant_draw_layers.census(); regenerate with\n"
                    "# python3 src/RimMandrake/Utils/prove_ground_cover_layer.py --offline --write-list\n")
            f.writelines("%s\t%s\n" % x for x in gc)
    elif not os.path.exists(LIST) or read_list() != gc:
        bad.append("live list %s differs from the fresh census (rerun with --write-list)"
                   % os.path.relpath(LIST, REPO))
    print("offline: %d plants, %d ground cover, %d on %s; caps %s; %d problem(s)"
          % (len(rows), len(gc), sum(by[n]["altitudeLayer"] == LOW for n, _ in gc), LOW,
             [by.get(c, {}).get("altitudeLayer") for c in CAPS], len(bad)))
    for b in bad:
        print("  FAIL " + b)
    return 1 if bad else 0


def live():
    sys.path.insert(0, HERE)
    import rimbridge_client as rb
    gc = read_list()
    names = [n for n, _ in gc] + list(CAPS)
    try:
        host, port, token = rb.resolve_endpoint()
        b = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
        b.connect()
        r = b.call("jawa/get_defs", {"defs": ";".join("ThingDef/" + n for n in names),
                                     "fields": "altitudeLayer", "limit": 200}) or {}
    except Exception as ex:      # noqa: BLE001 -- any bridge failure is UNMEASURED, not a verdict
        print("UNMEASURED: bridge: %s" % ex)
        return 2
    if isinstance(r, dict) and r.get("content"):
        r = json.loads(r["content"][0]["text"])
    got = {d.get("defName"): (d.get("fields") or {}).get("altitudeLayer")
           for d in (r.get("defs") or []) if d.get("found", True)}
    if not any(c in got for c in CAPS):
        print("UNMEASURED: no Rot cap resolved (TheRot not loaded?): %s" % str(r)[:300])
        return 2
    bad = ["%s live %s" % (n, got[n]) for n, _ in gc if n in got and got[n] != LOW]
    bad += ["%s (%s) not loaded" % (n, p) for n, p in gc if p.startswith("mandrake.") and n not in got]
    bad += ["cap %s live %s" % (c, got.get(c, "not loaded")) for c in CAPS if got.get(c) != "LowPlant"]
    print("live: %d/%d ground cover loaded, caps %s; %d problem(s)"
          % (sum(n in got for n, _ in gc), len(gc), [got.get(c) for c in CAPS], len(bad)))
    for x in bad:
        print("  FAIL " + x)
    return 1 if bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(offline(a) if "--offline" in a else live())
