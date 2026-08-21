#!/usr/bin/env python3
"""
lint_links.py — pre-flight `world/ASHKARR_WORLDMAP_links.csv` OFFLINE, before it
costs a game load.

WHY. `jawa/world_links_import` refuses a row it cannot lay — "not adjacent", an
unknown def, a tile id off the grid — and it refuses them ONE AT A TIME, inside a
live window that cost ~25 minutes to open. Every refusal this script catches is a
refusal that does not happen in front of the owner.

WHAT IT CANNOT TELL YOU. Whether the world in the game is the world this CSV was
authored against. That is `expectTiles` on the importer and `jawa/world_tile_validate`
afterwards; a clean lint here is a statement about the FILE, never about the game.

    python3 src/RimMandrake/Utils/lint_links.py
"""
import argparse, csv, json, os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import DEF_DUMP  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
LINKS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv")
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
DUMP = os.path.join(DEF_DUMP, "defs")


# Above this class a river is a TRUNK and owes the sea an outlet; at or below it may
# end in a playa. Thresholds are the producer's: HugeRiver acc>3000, LargeRiver >1200.
TRUNKS = ("LargeRiver", "HugeRiver")


def defnames(kind):
    """RiverDef/RoadDef names from the frozen capture. UNMEASURED if absent."""
    p = os.path.join(DUMP, kind + ".json")
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return None
    rows = d if isinstance(d, list) else d.get("defs") or d.get("items") or []
    out = set()
    for r in rows:
        if isinstance(r, dict) and r.get("defName"):
            out.add(r["defName"])
    return out or None


def mouth_first(river_rows, adj, water, elev):
    """
    Re-order and re-orient river links so the file is MOUTH FIRST.

    🔴 WHY THIS IS NEEDED, and why nothing would have told us. `ashkarr_paint.py`
    emits rivers by walking `np.nonzero(w["chan"])[0]` — ascending TILE ID — and
    writes (tile, downhill_neighbour). `jawa/world_links_import` applies rivers
    IN FILE ORDER, and `WorldGrid.OverlayRiver` sets
    `riverDist = max(riverDist, previous + 1)`. So importing the producer's file
    lays every river upside-down and in scattered order: the importer refuses
    NOTHING, logs NOTHING, and the planet comes out with wrong riverDist on all
    238 links. A silent wrong answer, which is the only kind this project fears.

    ⛔ This changes ORDER and ORIENTATION only. The SET of links is identical —
    the same tiles are joined by the same defs, so the accepted planet is not
    altered. That is deliberate: the map was accepted for v1 on 2026-08-20 and an
    agent must not repaint it.
    """
    down = {}                      # a -> b, as the producer wrote it (a is upstream)
    for a, b, d in river_rows:
        down[a] = (b, d)
    ups = collections.defaultdict(list)
    for a, (b, d) in down.items():
        ups[b].append(a)

    # A MOUTH is a downstream endpoint that is not itself upstream of anything —
    # it drains into sea, or off the end of the channel network.
    mouths = sorted({b for _, (b, _) in down.items()} - set(down.keys()))
    out, seen = [], set()
    for m in mouths:
        stack = [m]
        while stack:                       # BFS outward from the mouth = upstream
            cur = stack.pop(0)
            for a in sorted(ups.get(cur, ())):
                if (a, cur) in seen:
                    continue
                seen.add((a, cur))
                _, d = down[a]
                out.append((cur, a, d))    # ⇐ FLIPPED: downstream first, then upstream
                stack.append(a)
    # Anything left is a cycle or an orphan the walk never reached — keep it rather
    # than drop it, and let the lint say so. Silently losing a river is worse.
    for a, (b, d) in sorted(down.items()):
        if (a, b) not in seen:
            out.append((b, a, d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the links CSV mouth-first. Order and orientation "
                         "only; the SET of links is untouched.")
    args = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import world_graph
    nbr, _lat, _lon, _vec = world_graph.load()   # list[list[int]] — see its docstring
    adj = [set(int(j) for j in row if int(j) >= 0) for row in nbr]

    water, elev = {}, {}
    with open(TILES, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            t = int(r["tile"])
            water[t] = (r.get("water") or "").strip().lower() in ("1", "true", "yes")
            try:
                elev[t] = float(r.get("elev_m") or 0)
            except ValueError:
                elev[t] = 0.0

    rivers = defnames("RiverDef")
    roads = defnames("RoadDef")

    bad = collections.Counter()
    examples = collections.defaultdict(list)

    def flag(tag, msg):
        bad[tag] += 1
        if len(examples[tag]) < 3:
            examples[tag].append(msg)

    n = 0
    river_rows = []
    with open(LINKS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            n += 1
            kind = (r["kind"] or "").strip().lower()
            try:
                a, b = int(r["a"]), int(r["b"])
            except ValueError:
                flag("unparseable tile id", str(r)); continue
            d = (r["def"] or "").strip()

            if kind not in ("river", "road"):
                flag("kind is not river/road", kind)
            if a >= len(adj) or b >= len(adj) or a < 0 or b < 0:
                flag("tile id off the grid", "%d,%d" % (a, b)); continue
            if a == b:
                flag("self link", str(a))
            elif b not in adj[a]:
                flag("NOT ADJACENT — the importer will refuse this row", "%d -> %d" % (a, b))

            pool = rivers if kind == "river" else roads
            if pool is None:
                flag("def UNMEASURED (%s.json absent from the capture)"
                     % ("RiverDef" if kind == "river" else "RoadDef"), d)
            elif d not in pool:
                flag("no such def in the frozen capture", d)

            if kind == "river":
                river_rows.append((a, b, d))

    # 🔴 MOUTH FIRST. OverlayRiver sets riverDist = max(riverDist, prev+1), so a river
    # applied upstream-first gets wrong distances SILENTLY — no refusal, no error, just
    # a wrong planet. File order IS the semantics here, which is why it is linted.
    seen = set()
    for i, (a, b, d) in enumerate(river_rows):
        if i == 0 or a in seen:
            pass
        elif d in TRUNKS and not (water.get(a) or any(water.get(x) for x in adj[a])):
            # 🔑 TRUNKS ONLY, and the linter must know which — owner's ruling, 2026-08-17:
            # "BOTH. High-accumulation trunks MUST reach a sea; low-accumulation rivers
            # MAY die in playas / salt pans. So 'reaches no sea' is a defect only above
            # the trunk threshold - the linter must know which."
            # A linter that flags every Creek dying in a salt pan is reporting the
            # owner's own design as a defect, and would be silenced rather than fixed.
            flag("TRUNK river does not reach water — it must", 
                 "row %d: %d -> %d (%s)" % (i + 2, a, b, d))
        seen.add(a); seen.add(b)

    up = sum(1 for a, b, _ in river_rows if elev.get(b, 0) > elev.get(a, 0))
    print("rows           %d  (%d river, %d road)"
          % (n, len(river_rows), n - len(river_rows)))
    print("river uphill   %d of %d rows run a->b uphill  (mouth-first expects a MAJORITY;"
          % (up, len(river_rows)))
    print("               the remainder are flat ties, not defects)")
    print("def source     %s / %s"
          % ("RiverDef ok" if rivers else "RiverDef UNMEASURED",
             "RoadDef ok" if roads else "RoadDef UNMEASURED"))
    print()
    if args.fix:
        fixed = mouth_first(river_rows, adj, water, elev)
        if len(fixed) != len(river_rows):
            print("REFUSING to write: reorder produced %d river rows from %d. A "
                  "reorder that changes the COUNT has lost or duplicated a river."
                  % (len(fixed), len(river_rows)))
            return 1
        roadrows = []
        with open(LINKS, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if (r["kind"] or "").strip().lower() == "road":
                    roadrows.append((r["a"], r["b"], r["def"]))
        with open(LINKS, "w", newline="", encoding="utf-8") as fh:
            wr = csv.writer(fh)
            wr.writerow(["kind", "a", "b", "def"])
            for a, b, d in fixed:
                wr.writerow(["river", a, b, d])
            for a, b, d in roadrows:
                wr.writerow(["road", a, b, d])
        print("rewrote %s mouth-first: %d river rows re-ordered, %d road rows "
              "unchanged." % (os.path.basename(LINKS), len(fixed), len(roadrows)))
        print("Re-run without --fix to confirm it lints clean.")
        return 0

    if not bad:
        print("PASS — every row is adjacent, in range, and names a def the capture knows.")
        print("⚠️ This says nothing about the world in the GAME. Pass expectTiles=21872")
        print("   to jawa/world_links_import and run jawa/world_tile_validate after.")
        return 0
    print("FAIL")
    for tag, cnt in bad.most_common():
        print("  %-58s %d" % (tag, cnt))
        for e in examples[tag]:
            print("      e.g. %s" % e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
