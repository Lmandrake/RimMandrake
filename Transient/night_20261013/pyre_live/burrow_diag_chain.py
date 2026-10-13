

# ---- NIGHT 2026-10-13 DIAG (scratch copy only, never in the repo's validation.py) ----
# PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE: grazer job sampled every 10 ticks for 300 ticks, repeated, plus a 13-14 cell control.
DIAG_OUT = os.environ.get("BURROW_DIAG_OUT", "burrow_diag.json")
DIAG_NEAR = int(os.environ.get("BURROW_NEAR", "6"))
DIAG_CTRL = int(os.environ.get("BURROW_CTRL", "3"))


@suite.chain("burrowers_diag")
@_teardown(fire=True)
def burrowers_diag(t):
    _pad(t, PAD_BURROW)
    t.clear_area(size=TEST_SIZE)
    rect = _rect(t)
    x, z = t.anchor
    out = {"anchor": [x, z], "rect": rect, "trials": []}
    with _comp(t, "burrowers_dive_diag", shows=[]):
        _set(t, {"burrowOnFireEnabled": True})
        _firebreak(t, rect)
        plan = [("near", x + 5)] * DIAG_NEAR + [("ctrl", x + 16)] * DIAG_CTRL
        for i, (kind, gx) in enumerate(plan):
            _extinguish(t)
            import northstar_driver.site as _site
            _site.despawn_pawns_in(t.session, (x - 30, z - 30, 60, 60)) if _live(t) else None
            _soil(t, rect)
            _plants(t, "RM_FE_Plant_EmberGrass", rect)
            g = _spawn_wild(t, "RM_Ashwallow", gx, z)
            _fire(t, (x - 3, z - 3, 6, 6))
            samples = []
            seen = None
            for k in range(30):
                _wait(t, 10)
                j = _job_of(t, g)
                samples.append(j)
                if seen is None and j and "Burrow" in str(j):
                    seen = (k + 1) * 10
            row = _pawn_row(t, g, health=True)
            tr = {"i": i, "kind": kind, "grazerX": gx, "jobs": samples, "burrowedAt": seen,
                  "burrowedHediffEnd": _has_hediff(row, "RM_Burrowed"),
                  "firstFlee": next(((k + 1) * 10 for k, j in enumerate(samples) if j and "Flee" in str(j)), None),
                  "pos": [(row or {}).get("x"), (row or {}).get("z")]}
            out["trials"].append(tr)
            print("[diag] " + json.dumps(tr), flush=True)
            with open(DIAG_OUT, "w") as f:
                json.dump(out, f, indent=1, default=str)
        _extinguish(t)
        _note(t, "burrow diag", out)
