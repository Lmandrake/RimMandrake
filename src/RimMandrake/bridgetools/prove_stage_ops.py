"""Live proof of RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO: the four staging tools reply from a read-back made in the
same main-thread hop as the write (the `readBack` block, JawaBenchStageReadBack.cs). Page:
design/specs/2026-11-23-bridge-v2/boundary.md §THE STAGE READ-BACK.

    python.exe src/RimMandrake/bridgetools/prove_stage_ops.py [--src-hash HASH] [--log PATH] < /dev/null

Needs a throwaway Playing map (a quicktest) and the companion built at or after this item. With --src-hash, the loaded
companion's srcHash (jawa/running_mods loadedOf=ours) must equal it, or there is no verdict. Five rows:
  R1 a 400-cell station with 10 pawns is cleaned and built, and the time is printed; every reply's block is ok and its
     write and read share one frame;
  R2 the same plan built twice gives equal read-back digests (terrain, structures, pawns);
  R3 a spawn that the game answered otherwise is reported from the read-back. The game on this list never replaces a
     kind (forceGenerateNewPawn), so the case staged is a xenotype the game does not give to an animal; the replaced
     kind itself is the offline check a_replaced_pawn_kind_is_reported_as_made;
  R4 a station built after a deliberately dirty scene (a corpse, a fire, a stray wall) reads back as the fresh one: its
     clean names no thing left, and its digests equal R1's;
  R5 a station that cannot be cleaned (a steam geyser, which the game cannot destroy) is named by the clean, and the
     script retires it.
Exit 0 = every row held, 1 = a row failed, 2 = no verdict (no bridge, no map, another companion).
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

KIND = "Muffalo"
SIDE = 20


def call(c, tool, args):
    r = c.call(tool, args, check=False)
    return r if isinstance(r, dict) else {"success": False, "raw": str(r)[:300]}


def block(r):
    b = r.get("readBack")
    return b if isinstance(b, dict) else {}


def plan(x0, z0):
    """The station plan: terrain over 400 cells, a wall ring, 10 pawns on fixed cells inside."""
    terrain = "Concrete:%d,%d,%d,%d" % (x0, z0, SIDE, SIDE)
    ring = [(x0 + i, z0) for i in range(SIDE)] + [(x0 + i, z0 + SIDE - 1) for i in range(SIDE)] + \
           [(x0, z0 + j) for j in range(1, SIDE - 1)] + [(x0 + SIDE - 1, z0 + j) for j in range(1, SIDE - 1)]
    walls = ";".join("Wall:%d,%d" % p for p in ring)
    pawns = [(x0 + 3 + 2 * i, z0 + 5 + (i % 2) * 6) for i in range(10)]
    return terrain, walls, pawns


def clean(c, x0, z0, notes):
    rect = "%d,%d,%d,%d" % (x0, z0, SIDE, SIDE)
    lp = call(c, "jawa/list_pawns", {"rect": rect})
    for p in lp.get("pawns") or []:
        if isinstance(p, dict) and p.get("id"):
            call(c, "jawa/pawn_force_incapacitate", {"pawn": p["id"], "action": "vanish"})
    d = call(c, "jawa/destroy_batch", {"rects": rect, "categories": "All"})
    left = call(c, "jawa/list_pawns", {"rect": rect}).get("pawns") or []
    notes.append("clean %s: destroyed %s, block ok=%s left=%s kept=%s sameFrame=%s, pawns after %d" % (
        rect, d.get("destroyed"), block(d).get("ok"), block(d).get("leftBlocking"), block(d).get("leftKept"),
        block(d).get("sameFrame"), len(left)))
    return d, left


def build(c, x0, z0):
    terrain, walls, pawns = plan(x0, z0)
    t = call(c, "jawa/set_terrain_batch", {"ops": terrain})
    b = call(c, "jawa/build_batch", {"ops": walls, "stuff": "Steel"})
    s = [call(c, "jawa/spawn_pawn", {"kindDef": KIND, "x": x, "z": z, "faction": "none"}) for x, z in pawns]
    return t, b, s


def blocks_ok(replies):
    """-> the first reply whose block is missing, not ok, or not in one frame, else None."""
    for name, r in replies:
        bk = block(r)
        if not bk:
            return "%s has no readBack block: %s" % (name, str(r)[:200])
        if bk.get("ok") is not True or bk.get("sameFrame") is not True or bk.get("frameOpen") != bk.get("frameReply"):
            return "%s block ok=%s sameFrame=%s frames %s/%s faults=%s wrong=%s left=%s" % (
                name, bk.get("ok"), bk.get("sameFrame"), bk.get("frameOpen"), bk.get("frameReply"), bk.get("faults"),
                str(bk.get("wrong"))[:200], str(bk.get("left"))[:200])
        if r.get("success") is not True:
            return "%s success=%s with an ok block: %s" % (name, r.get("success"), str(r)[:200])
    return None


def digests(t, b, s):
    return (block(t).get("digest"), block(b).get("digest"), tuple(block(x).get("digest") for x in s))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-hash")
    ap.add_argument("--log")
    a = ap.parse_args(argv)
    out = []

    def say(s):
        print(s, flush=True)
        out.append(s)

    h, p, tok = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=180)
    c.connect()
    rm = call(c, "jawa/running_mods", {"loadedOf": "ours"})
    comp = ((rm.get("loaded") or {}).get("companion") or {}) if isinstance(rm.get("loaded"), dict) else {}
    say("companion: srcHash=%s mvid=%s" % (comp.get("srcHash"), comp.get("mvid")))
    if a.src_hash and comp.get("srcHash") != a.src_hash:
        say("NO VERDICT: the loaded companion is %s, want %s" % (comp.get("srcHash"), a.src_hash))
        return 2
    mi = call(c, "jawa/map_info", {})
    sx, sz = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0)
    if sx < 120 or sz < 120:
        say("NO VERDICT: no usable map: %s" % str(mi)[:200])
        return 2
    xa, za = sx // 2 + 15, sz // 2 + 15          # station A
    xb, zb = sx // 2 - 45, sz // 2 + 15          # station B (R5)
    rows = []

    # R1: build once (a station with 10 pawns), then clean and build it again, timed
    notes = []
    build(c, xa, za)
    t0 = time.time()
    d, left = clean(c, xa, za, notes)
    t1 = time.time()
    t, b, s = build(c, xa, za)
    t2 = time.time()
    fresh = digests(t, b, s)
    bad = blocks_ok([("destroy_batch", d), ("set_terrain_batch", t), ("build_batch", b)] + [("spawn_pawn#%d" % i, x) for i, x in enumerate(s)])
    if not bad and left:
        bad = "%d pawn(s) left after the clean" % len(left)
    if not bad and block(t).get("rows") != SIDE * SIDE:
        bad = "set_terrain_batch read back %s cells, want %d" % (block(t).get("rows"), SIDE * SIDE)
    rows.append(("R1 400-cell station, 10 pawns, cleaned and built", bad,
                 "clean %.2f s, build %.2f s; %s" % (t1 - t0, t2 - t1, notes[-1])))

    # R2: the same plan again: equal digests
    notes = []
    d2, _ = clean(c, xa, za, notes)
    t, b, s = build(c, xa, za)
    again = digests(t, b, s)
    bad = blocks_ok([("destroy_batch", d2), ("set_terrain_batch", t), ("build_batch", b)])
    if not bad and again != fresh:
        bad = "digests differ: %s vs %s" % (again, fresh)
    rows.append(("R2 the same plan twice gives equal digests", bad, "terrain %s, walls %s, pawns %s" % (fresh[0], fresh[1], fresh[2][0])))

    # R3: a spawn the game answers otherwise
    cx, cz = xa + 10, za + 10
    r3 = call(c, "jawa/spawn_pawn", {"kindDef": KIND, "x": cx, "z": cz, "faction": "none", "xenotype": "Hussar"})
    bk = block(r3)
    wrong = bk.get("wrong") or []
    keys = [(w.get("key"), w.get("want"), w.get("got")) for row in wrong if isinstance(row, dict) for w in (row.get("wrong") or [])]
    bad = None
    if not bk:
        bad = "no readBack block: %s" % str(r3)[:300]
    elif bk.get("ok") is not False or r3.get("success") is not False:
        bad = "a Muffalo asked as Hussar gave ok=%s success=%s" % (bk.get("ok"), r3.get("success"))
    elif not any(k[0] in ("xenotype", "spawned") and k[2] != "Hussar" for k in keys):
        bad = "the wrong row does not name the game's answer: %s" % keys
    rows.append(("R3 a spawn the game answered otherwise is reported", bad, "wrong keys %s; made %s" % (keys, str(bk.get("made"))[:160])))

    # R4: a dirty scene (a corpse, a fire, a stray wall) cleaned and rebuilt reads as the fresh station
    notes = []
    lp = call(c, "jawa/list_pawns", {"rect": "%d,%d,%d,%d" % (xa, za, SIDE, SIDE)}).get("pawns") or []
    killed = [call(c, "jawa/pawn_force_incapacitate", {"pawn": q["id"], "action": "kill"}) for q in lp[:2] if isinstance(q, dict)]
    fire = call(c, "jawa/build_batch", {"ops": "Fire:%d,%d" % (xa + 8, za + 8)})
    stray = call(c, "jawa/build_batch", {"ops": "Wall:%d,%d" % (xa + 9, za + 9), "stuff": "WoodLog"})
    dirt = call(c, "jawa/list_things", {"rect": "%d,%d,%d,%d" % (xa, za, SIDE, SIDE)})
    corpses = [x for x in (dirt.get("things") or []) if isinstance(x, dict) and "Corpse" in str(x.get("def") or x.get("defName"))]
    d4, left = clean(c, xa, za, notes)
    t, b, s = build(c, xa, za)
    after = digests(t, b, s)
    bad = blocks_ok([("destroy_batch", d4), ("set_terrain_batch", t), ("build_batch", b)] + [("spawn_pawn#%d" % i, x) for i, x in enumerate(s)])
    if not bad and not corpses:
        bad = "the dirty scene had no corpse to clean (kill replies %s)" % [k.get("success") for k in killed]
    if not bad and after != fresh:
        bad = "the rebuilt station's digests differ from the fresh one: %s vs %s" % (after, fresh)
    rows.append(("R4 a station after a dirty scene reads as fresh", bad,
                 "dirt: %d corpse(s), fire placed=%s, stray wall placed=%s (a reservation was not staged); %s"
                 % (len(corpses), fire.get("placed"), stray.get("placed"), notes[-1])))

    # R5: a station the game cannot clean is named, then retired
    notes = []
    gz = call(c, "jawa/build_batch", {"ops": "SteamGeyser:%d,%d" % (xb + 5, zb + 5)})
    d5, _ = clean(c, xb, zb, notes)
    named = [l for l in (block(d5).get("left") or []) if isinstance(l, dict) and l.get("def") == "SteamGeyser"]
    bad = None
    if gz.get("placed") != 1:
        bad = "could not place the geyser: %s" % str(gz)[:200]
    elif not named:
        bad = "the clean did not name the geyser it left: %s" % str(block(d5))[:300]
    rows.append(("R5 a station that cannot be cleaned is retired", bad,
                 ("station %d,%d RETIRED: the clean left %s (%s)" % (xb, zb, named[0].get("id"), named[0].get("why"))) if named else ""))

    # leave station A clean
    clean(c, xa, za, [])
    fails = 0
    for name, bad, info in rows:
        fails += bad is not None
        say("%s %s: %s" % ("PASS" if bad is None else "FAIL", name, bad or info))
    say("prove_stage_ops: %d of %d rows held" % (len(rows) - fails, len(rows)))
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
