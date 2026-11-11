def pond_depth_verdict(reads):
    """L8 (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD; owner by card 2026-10-16 "Yes, ponds shallow out"; design §10). reads = the
    pond's ProofPondDepth replies (parse_pond) in time order while a pump draws it. PASS = the surface fell (s rose by one or
    more), every square that was wet at the brim is still wet while s == 1 (it shallowed, it did not shrink), and at s >= 1
    the census shows part-depth stages (chest/shallow/thin) instead of only full original water. A shrinking wet count at
    s == 1, or s >= 1 with no part-depth square, is a MOD FAIL. The surface never moving is SITE (the pump drew nothing);
    the model not applying (moving water, another liquid, limitless) is SITE. Returns (status, class, detail)."""
    reads = [r for r in (reads or []) if r]
    if len(reads) < 2:
        return "UNMEASURED", "HARNESS", {"why": "fewer than two pond reads", "reads": len(reads)}
    first, last = reads[0], reads[-1]
    det = {"s": [r.get("s") for r in reads], "wet": [r.get("wet") for r in reads], "census": last.get("census"),
           "stock": [first.get("stock"), last.get("stock")]}
    if not all(r.get("applies") for r in reads):
        return "UNMEASURED", "SITE", dict(det, why="the depth model does not apply to this body (limitless, moving or not water)")
    if not (last.get("s", 0) > first.get("s", 0)):
        return "UNMEASURED", "SITE", dict(det, why="the surface never fell: the pump drew nothing")
    brim = [r for r in reads if r.get("s") == 0]
    one = [r for r in reads if r.get("s") == 1 and r.get("r", 0) == 0]
    if brim and one and min(r["wet"] for r in one) < max(r["wet"] for r in brim):
        return "FAIL", "MOD", dict(det, why="the wet count shrank one level down: the pond shrank instead of shallowing")
    c = last.get("census") or {}
    if last.get("s", 0) >= 1 and c.get("chest", 0) + c.get("shallow", 0) + c.get("thin", 0) + c.get("deep", 0) == 0:
        return "FAIL", "MOD", dict(det, why="the surface fell but no square shows a part-depth stage")
    return "PASS", "MOD", det
