"""modcheck.validity -- "validity before cause" (focused_testing_plan_2026-10-25 §3.1 and §3.5, option B).

Two harness-side guards a live run can arm (both OFF unless asked: `modcheck run --validity`, `--canary`):

VALIDITY CHECKS. `default_checks(fixtures)` returns callables for TestContext.validity_checks. suite._ComponentCtx._exit
runs them when a component would end FAIL, before `_on_finding` publishes; the first hit makes the row UNMEASURED with
validity "invalid", a suspected cause and confidence, and the FAIL text kept as the row's `lead` (never erased as noise).
Each check reads the game once and answers (reason, cause, confidence) or None:
  * menu_drop        programState is not Playing          -> UNKNOWN / high  (the map the row measured is gone)
  * colonists_zero   no live colonist on the roster        -> UNKNOWN / medium (the mod COULD have killed them: a lead)
  * hostile_arrival  a live hostile pawn the run did not spawn (not a declared fixture) -> SITE / medium
A read that fails is no verdict: the check answers None and the FAIL stands.

CANARY. `canary(session, anchor)` is a small vanilla-only probe run before the first chain: the game is Playing, a
colonist exists, a vanilla Steel stack spawned on an EMPTY cell at or near the anchor reads back there and is destroyed
again (only Items on that one cell: nothing it did not spawn). Red -> the
session is HARNESS: runner.run_suite records one UNMEASURED row per selected live chain (validity invalid, cause HARNESS)
and runs no live chain body (offline chains still run).
"""

CANARY_DEF = "Steel"          # vanilla Core; every list loads it
CANARY_ROW = "<canary red: HARNESS>"


def _program_state(session):
    return (session.call("rimworld/get_ui_state") or {}).get("programState")


def _pawns(session):
    import helpers as _h  # noqa: E402 - modcheck dir on sys.path (runner/cli)
    return _h, _h.read_pawns(session, health=False)


def menu_drop(ctx, comp):
    try:
        st = _program_state(ctx.session)
    except Exception:  # noqa: BLE001 - unreadable is not a verdict
        return None
    if st is not None and st != "Playing":
        return ("programState %s, not Playing: the game left the map the row measured" % st, "UNKNOWN", "high")
    return None


def colonists_zero(ctx, comp):
    try:
        h, rows = _pawns(ctx.session)
    except Exception:  # noqa: BLE001
        return None
    if not any(h.is_colonist(r) and not r.get("dead") for r in rows):
        return ("no live colonist on the map (colonist count 0)", "UNKNOWN", "medium")
    return None


def hostile_arrival(fixtures=()):
    """A check: a live hostile pawn that neither this chain (ctx.fixture_ids) nor the run (`fixtures`) spawned."""
    known = set(fixtures)

    def hostile_arrival(ctx, comp):
        try:
            h, rows = _pawns(ctx.session)
        except Exception:  # noqa: BLE001
            return None
        mine = known | set(getattr(ctx, "fixture_ids", ()) or ())
        foreign = [r for r in rows if h.is_hostile(r) and r.get("spawned", True) and r.get("id") not in mine]
        if foreign:
            return ("hostile arrival: %s not spawned by the run" % ", ".join(
                "%s (%s)" % (r.get("id"), r.get("kindDef") or r.get("kind") or "?") for r in foreign[:4]), "SITE", "medium")
        return None
    return hostile_arrival


def default_checks(fixtures=()):
    return [menu_drop, colonists_zero, hostile_arrival(fixtures)]


def _empty_cell(session, anchor, radius=12):
    """The first cell at or around `anchor` (Chebyshev rings out to `radius`) holding no thing at all, or None. The
    canary spawns and destroys only there, so its Item cleanup can remove nothing but its own stack."""
    x0, z0 = anchor
    for r in range(radius + 1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if max(abs(dx), abs(dz)) == r and not session.things_at(x0 + dx, z0 + dz):
                    return x0 + dx, z0 + dz
    return None


# live drivers this process saw leave the map with no live colonist (runner.ensure_live_colony): named in the canary's
# "no live colonist" so a red canary blames its cause (STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED)
COLONY_BREAKERS = []


def canary(session, anchor):
    """{"ok": bool, "problems": [..], "steps": [..]}. Never raises. Spawns only on a cell it read as EMPTY and destroys
    Items on that one cell, so nothing but its own stack can be removed."""
    out = {"ok": False, "problems": [], "steps": []}
    spawned = None
    try:
        x, z = anchor
        st = _program_state(session)
        out["steps"].append("programState %s" % st)
        if st != "Playing":
            out["problems"].append("programState %s, not Playing" % st)
            return out
        h, rows = _pawns(session)
        n = sum(1 for r in rows if h.is_colonist(r) and not r.get("dead"))
        out["steps"].append("%d live colonists" % n)
        if n == 0:
            out["problems"].append("no live colonist" + (
                " (left so by live driver(s) %s)" % ", ".join(COLONY_BREAKERS) if COLONY_BREAKERS else ""))
        cell = _empty_cell(session, (x, z))
        if cell is None:
            out["problems"].append("no empty cell within 12 of the anchor %d,%d: nothing spawned" % (x, z))
            return out
        x, z = cell
        r = session.call("jawa/spawn_batch", ops="%s:%d,%d" % (CANARY_DEF, x, z)) or {}
        spawned = cell
        out["steps"].append("spawn_batch %s at %d,%d: success=%r" % (CANARY_DEF, x, z, r.get("success")))
        if not r.get("success"):
            out["problems"].append("spawn_batch %s at %d,%d did not report success: %s" % (
                CANARY_DEF, x, z, str(r.get("message") or r)[:200]))
        got = session.things_at(x, z)
        if CANARY_DEF not in got:
            out["problems"].append("spawned %s did not read back at %d,%d (things_at: %s)" % (CANARY_DEF, x, z, got[:6]))
    except Exception as ex:  # noqa: BLE001 - a canary that cannot ask is red
        out["problems"].append("%s: %s" % (type(ex).__name__, ex))
    finally:
        if spawned is not None:
            x, z = spawned
            try:
                session.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x, z), categories="Item")   # never pawns
                left = session.things_at(x, z)
                out["steps"].append("destroyed; left at cell: %s" % left[:6])
                if CANARY_DEF in left:
                    out["problems"].append("canary %s still at %d,%d after destroy_batch" % (CANARY_DEF, x, z))
            except Exception as ex:  # noqa: BLE001
                out["problems"].append("cleanup %s: %s" % (type(ex).__name__, ex))
    out["ok"] = not out["problems"]
    return out


def canary_component(result):
    """The one row a chain records when the canary was red: UNMEASURED, invalid, cause HARNESS."""
    from suite import Component, UNMEASURED  # noqa: E402
    c = Component(CANARY_ROW, None, False)
    c.verdict, c.validity, c.suspected_cause, c.cause_confidence = UNMEASURED, "invalid", "HARNESS", "high"
    c.detail = "canary red, chain body not run -- the session is HARNESS, not a verdict on the mod: %s" % (
        "; ".join(result.get("problems") or ["?"]))[:400]
    c.evidence.append({"call": "canary", "result": result})
    return c
