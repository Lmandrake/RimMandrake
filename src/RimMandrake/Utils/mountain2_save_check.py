"""Offline proof that a world save carries the second mountain pass (MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED).

    python3 src/RimMandrake/Utils/mountain2_save_check.py <save.rws> [--plan <plan.json>] [--base <RECORDLINKS.rws>]

Reads tileHilliness / tileElevation straight out of the save and checks every tile in
world/ASHKARR_MOUNTAINS2_2026-10-20_plan.json holds its planned value. It also checks the parts the pass
must not touch still have the item's counts: 326 river links, 1,242 road links, 96 surface settlements
(the item's 97 counted the orbital "Luminary Dock", id 155 on layer 1, which UNWANTED_FACTIONS_SILENCE_NOT_DELETED
removed on purpose; measured 97 = 96 + 1 in the RECORDLINKS base). `--base <RECORDLINKS.rws>` also compares
tileBiome and the surface settlement tiles against the pre-pass base.
Sanity probe first: the same comparison against the plan's `before` values must find mismatches on every
tile (0 is the right answer only if the instrument can see). Exit 0 = the pass is in the save.
"""
import argparse, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import worldmap, worldview  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(REPO, "world", "ASHKARR_MOUNTAINS2_2026-10-20_plan.json")
EXPECT_LINKS = {"river": 326, "road": 1242}
EXPECT_SETTLEMENTS = 96   # surface (layer 0) only


def read_save(path):
    g = worldmap.WorldGrid.__new__(worldmap.WorldGrid)
    g.save_path = path
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        g.text = fh.read()
    g._locate_surface()
    arr = {}
    for name in ("tileHilliness", "tileElevation", "tileBiome"):
        raw = g._read_array(name)
        w = worldmap.SCALARS[name]
        arr[name] = struct.unpack("<%d%s" % (len(raw) // w, "H" if w == 2 else "B"), raw)
    links = {}
    for kind in ("river", "road"):
        ob = g._read_array(worldview.LINKS[kind][0])
        links[kind] = 0 if ob is None else len(ob) // 4
    objs = worldmap.WorldObjects.__new__(worldmap.WorldObjects)
    objs.save_path, objs.text = path, g.text
    return arr, links, sorted(x["tile"] for x in objs.settlements() if x["layer"] == 0)


def mismatches(arr, hill, elev):
    H, E = arr["tileHilliness"], arr["tileElevation"]
    bad = [t for t, v in hill.items() if H[int(t)] != v]
    bad += [t for t, v in elev.items() if abs((E[int(t)] - 8192) - v) > 1]
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("save")
    ap.add_argument("--plan", default=PLAN)
    ap.add_argument("--base", help="pre-pass base save; biomes and surface settlement tiles must match it")
    a = ap.parse_args(argv)
    plan = json.load(open(a.plan))
    arr, links, settl = read_save(a.save)
    fails = []
    if len(arr["tileHilliness"]) != plan["expectTiles"]:
        fails.append("tiles %d != %d" % (len(arr["tileHilliness"]), plan["expectTiles"]))
    n = len(plan["hilliness"]) + len(plan["elevation"])
    probe = mismatches(arr, plan["before"], plan["elevationBefore"])
    if len(probe) != n:
        fails.append("sanity probe: only %d of %d tiles differ from `before` - the instrument cannot see" % (len(probe), n))
    bad = mismatches(arr, plan["hilliness"], plan["elevation"])
    if bad:
        fails.append("%d of %d plan tiles not at their planned value: %s" % (len(bad), n, bad[:10]))
    for k, v in EXPECT_LINKS.items():
        if links[k] != v:
            fails.append("%s links %d != %d" % (k, links[k], v))
    if len(settl) != EXPECT_SETTLEMENTS:
        fails.append("surface settlements %d != %d" % (len(settl), EXPECT_SETTLEMENTS))
    if a.base:
        barr, _, bsettl = read_save(a.base)
        nb = sum(x != y for x, y in zip(barr["tileBiome"], arr["tileBiome"]))
        print("vs base: %d biome tiles differ; surface settlement tiles %s" % (nb, "same" if bsettl == settl else "DIFFER"))
        if nb:
            fails.append("%d biome tiles differ from the base" % nb)
        if bsettl != settl:
            fails.append("surface settlement tiles differ from the base")
    print("plan tiles %d: %d mismatches (probe vs before: %d differ); rivers %d roads %d settlements %d"
          % (n, len(bad), len(probe), links["river"], links["road"], len(settl)))
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
