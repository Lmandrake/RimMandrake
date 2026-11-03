#!/usr/bin/env python3
"""Live proof L2 of MIASMA_WARDEN_MOTHER_ART_1: a debug-aged warden mother draws the aged graphic.

    python.exe src/RimMandrake/Miasma/tests/warden_mother_live_proof.py L2

On the CURRENT map of a quicktest colony that loads RM_WardenMother (Miasma, standalone or folded into the biome
composite), through the JawaBench bridge:
  1. jawa/spawn_pawn RM_WardenMother, faction none, at the map centre.
  2. If she generated at or past ELDER_MIN_AGE, age her DOWN to ADULT_AGE (raw setter), so step 3 crosses the boundary.
  3. Read her life stage and body texPath (jawa/thing_explain): must be an adult stage drawing ADULT_TEX.
  4. jawa/set_pawn_age biologicalYears=AGED_AGE (DebugSetAge: birthdays fire, the life stage recalculates).
  5. Jump the camera to her, wait for a draw, read again: the life stage must be RM_WardenMotherElder, the body
     texPath AGED_TEX (not ADULT_TEX), a running mod must hold that path, and the RENDERED body texture must be
     that pack's texture (thing_explain label OBSERVED). A resolved render tree drawing anything else is a FAIL.
Exit 0 = the clause holds, 1 = a reading refutes it, 2 = no reading (no bridge, no map, the render tree never
resolved): never a verdict. It writes only a wild pawn onto the quicktest map (every save but the canonical world
saves is disposable) and never the world. Not a flyer: no flight is touched.

verdict() is pure and offline-tested by test_warden_mother_live_verdict.py, including the gen-1 checker's mutant
(elder texPath set back to the adult art), which must exit 1.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))

KIND = "RM_WardenMother"
ELDER_STAGE = "RM_WardenMotherElder"
ADULT_TEX = "Things/Pawn/Animal/Miasma/WardenMother/WardenMother"
AGED_TEX = "Things/Pawn/Animal/Miasma/WardenMother/WardenMotherAged"
ELDER_MIN_AGE = 38.0    # RM_WardenMother.xml lifeStageAges, last entry (the offline test pins it)
ADULT_AGE = 20.0
AGED_AGE = 40.0
DRAW_WAITS = 6          # x 0.5 s for the render tree to resolve after the jump


def body_row(explain):
    """The 'body' appearance row of a thing_explain reply, or None."""
    for row in ((explain or {}).get("appearance") or {}).get("paths") or []:
        if row.get("role") == "body":
            return row
    return None


def verdict(pre_stage, pre_explain, post_stage, post_explain):
    """(code, line). code 0 PASS, 1 FAIL, 2 UNMEASURED. Pure: readings in, verdict out."""
    pre, post = body_row(pre_explain), body_row(post_explain)
    if pre is None or post is None:
        return 2, "UNMEASURED: no body appearance row (pre=%r post=%r)" % (pre, post)
    if pre_stage == ELDER_STAGE:
        return 2, "UNMEASURED: she was still %s before ageing; the boundary was not crossed" % ELDER_STAGE
    if pre.get("texPath") != ADULT_TEX:
        return 1, "FAIL adult stage %s draws %r, expected %r" % (pre_stage, pre.get("texPath"), ADULT_TEX)
    if post_stage != ELDER_STAGE:
        return 1, "FAIL aged to %s years she is in stage %r, expected %s" % (AGED_AGE, post_stage, ELDER_STAGE)
    tex = post.get("texPath")
    if tex != AGED_TEX:
        return 1, "FAIL elder stage draws %r, expected %r (adult art is %r)" % (tex, AGED_TEX, ADULT_TEX)
    if not post.get("packsHoldingPath"):
        return 1, "FAIL no running mod holds %r: she would draw magenta" % tex
    limits = ((post_explain or {}).get("appearance") or {}).get("limits") or ""
    if post.get("label") != "OBSERVED":
        if "not resolved" in limits or "unreadable" in limits:
            return 2, "UNMEASURED: elder texPath right, but the rendered texture was not readable (%s)" % limits
        return 1, "FAIL the rendered body texture is not the %s texture (label %r, %s)" % (
            AGED_TEX, post.get("label"), post.get("note"))
    return 0, "PASS %s -> %s: draws %s from %s (OBSERVED)" % (pre_stage, post_stage, tex, post.get("provider"))


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("%s refused: %r" % (what, r))
    return r


def run(c):
    mi = _ok(c.call("jawa/map_info", {}), "map_info")
    size = mi.get("mapSize") or {}
    sx = mi.get("sizeX") or size.get("x")
    sz = mi.get("sizeZ") or size.get("z")
    if not sx or not sz:
        return 2, "UNMEASURED: map_info gave no size: %r" % sorted(mi)
    cx, cz = int(sx) // 2, int(sz) // 2
    sp = _ok(c.call("jawa/spawn_pawn", {"kindDef": KIND, "x": cx, "z": cz, "faction": "none"}), "spawn_pawn")
    rows = sp.get("pawns") or []
    if not rows or not rows[0].get("ok"):
        return 2, "UNMEASURED: spawn_pawn landed no %s: %r" % (KIND, sp.get("message"))
    pid = rows[0]["id"]
    print("  spawned %s at %s,%s" % (pid, rows[0].get("x"), rows[0].get("z")), flush=True)
    age = _ok(c.call("jawa/set_pawn_age", {"pawn": pid, "biologicalYears": ADULT_AGE, "allowBackwards": True}),
              "set_pawn_age down")
    pre_stage = (age.get("after") or {}).get("lifeStage")
    pre_explain = _ok(c.call("jawa/thing_explain", {"id": pid}), "thing_explain pre")
    print("  pre: stage %s body %s" % (pre_stage, (body_row(pre_explain) or {}).get("texPath")), flush=True)
    age = _ok(c.call("jawa/set_pawn_age", {"pawn": pid, "biologicalYears": AGED_AGE}), "set_pawn_age up")
    post_stage = (age.get("after") or {}).get("lifeStage")
    post_explain = None
    for _ in range(DRAW_WAITS):
        x = (post_explain or {}).get("what") or {}
        c.call("rimworld/jump_camera_to_cell", {"x": x.get("x", cx), "z": x.get("z", cz)})
        time.sleep(0.5)
        post_explain = _ok(c.call("jawa/thing_explain", {"id": pid}), "thing_explain post")
        if (body_row(post_explain) or {}).get("label") == "OBSERVED":
            break
    print("  post: stage %s body %r" % (post_stage, body_row(post_explain)), flush=True)
    return verdict(pre_stage, pre_explain, post_stage, post_explain)


def main(argv):
    if len(argv) != 2 or argv[1] != "L2":
        print(__doc__)
        return 2
    try:
        import rimbridge_client as rb
        h, p, tok = rb.resolve_endpoint()
        c = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
        c.connect()
        code, line = run(c)
    except Exception as e:  # noqa: BLE001 -- any bridge failure is an instrument error, never a verdict
        print("L2 UNMEASURED: %s: %s" % (type(e).__name__, e))
        return 2
    print("L2 " + line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
