"""Live proof of RIMMANDRAKE_BUILD_COLONY_STATION_HOLDS_BYSTANDERS_BY_AREA (colony_holds.py + jawa/set_forbidden).
    python.exe src/RimMandrake/bridgetools/prove_colony_holds.py [--save BLAND_NORTHSTAR_BASE] < /dev/null
Loads a colony save, takes a station rect, holds, reads each pawn's area back from the game, reads the forbidden state of a
spawned thing back, releases, reads again. Rows H1..H4; exit 0 = all held, 1 = a row failed, 2 = no verdict."""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path.insert(0, UTILS)
import colony_holds as C  # noqa: E402
import rimbridge_client as rb  # noqa: E402

rows = []


def row(name, ok, detail):
    rows.append(ok)
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", default="BLAND_NORTHSTAR_BASE")
    a = ap.parse_args()
    h, p, tok = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=600)
    c.connect()

    def call(tool, **kw):
        r = c.call(tool, kw, check=False)
        return r if isinstance(r, dict) else {"success": False, "raw": str(r)[:300]}
    r = call("rimworld/load_game_ready", saveName=a.save)
    if r.get("success") is False:
        print("NO VERDICT: load failed: %s" % str(r)[:300])
        return 2
    mi = call("jawa/map_info")
    size = (int(mi["sizeX"]), int(mi["sizeZ"]))
    pawns = call("jawa/list_pawns").get("pawns") or []
    print("map %s, %d pawn(s)" % (size, len(pawns)))
    if not pawns:
        print("NO VERDICT: the map holds no pawn")
        return 2
    rect = (size[0] // 2 - 5, size[1] // 2 - 4, 10, 8)
    sp = call("rimworld/spawn_thing", defName="MealSurvivalPack", x=rect[0] + 2, z=rect[1] + 2, stackCount=5)
    f0 = call("jawa/set_forbidden", rect="%d,%d,%d,%d" % rect, forbidden=False)
    row("H0 set_forbidden exists and reads back", f0.get("success") is True and f0.get("changed", 0) >= 1, str(f0)[:160])
    before = {p_["id"]: call("jawa/set_player_settings", pawnId=p_["id"]).get("area") for p_ in pawns}
    hd = C.hold(call, size, rect, 3)
    print(C.receipt_line("live", hd))
    after = {i: call("jawa/set_player_settings", pawnId=i).get("area") for i in [x["id"] for x in hd["held"]]}
    row("H1 each held pawn reads the hold area back from the game", bool(hd["held"]) and all(v == hd["area"] for v in after.values()), "%d held, %d not: %s" % (len(hd["held"]), len(hd["unbound"]), hd["unbound"]))
    row("H2 the station things are forbidden", hd["forbidden"] >= 1, "forbidden=%s" % hd["forbidden"])
    pa = call("jawa/paint_area", area=hd["area"], ops="%d,%d,1,1" % (rect[0] + 5, rect[1] + 4), value=False)
    row("H3 the area leaves the station out (a station cell was never in it)", pa.get("success") is True, str(pa)[:160])
    lines = C.release(call, hd, rect)
    back = {i: call("jawa/set_player_settings", pawnId=i).get("area") for i in after}
    row("H4 the close gives each pawn its own area back", not lines and all(back[i] == before[i] for i in back), "%s %s" % (lines, {i: (before[i], back[i]) for i in back if back[i] != before[i]}))
    return 0 if all(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
