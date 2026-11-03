#!/usr/bin/env python3
"""expectations_l2.py - the L2 (behaviour gauntlet) half of the ONE manifest format.

MASS_VALIDATION_LADDER_1, criterion 1: "A batch of builds validates through L2 in one
bridge sitting, zero restarts." VALIDATION_LADDER.md's L2: "One quicktest map per
batch: spawn everything new, step ticks once, harvest the log once, screenshot once.
Catches NREs, missing/magenta art, eaten defs. Art presence is proven HERE, by machine."

THE SECTION
===========
A manifest (expectations_manifest.py) may carry an optional "l2" object:

    "l2": {
      "spawn": [{"pawnKind": "RSW_Moornak", "count": 2},
                {"thing": "RSW_TelluroxShell", "count": 1}],
      "ticks": 600
    }

`pawnKind` spawns a WILD pawn (faction none, so nothing fights the colony on purpose)
through jawa/spawn_pawn; `thing` spawns through jawa/spawn_batch (`count` is a STACK
size there, not a repeat - see that tool's description). `ticks` is how long the batch
runs after spawning; the batch runs the LONGEST ticks any of its manifests asks for.

The runner (`run_expectations.py --l2`) puts EVERY manifest's spawns on ONE map in one
pass, steps the ticks once, reads the log once (a LogTap, so nothing scrolls out of the
1,000-entry journal ring unseen), screenshots the batch rect once and counts magenta
pixels in it. One sitting, zero restarts: the runner records the map id and the game
tick at start and FAILS the batch if either moved backwards or changed under it.

Everything in this module except `run_l2_live` is pure and offline-tested
(selftest_expectations_l2.py). A verdict is never `success:true` from a spawn call: each
subject is counted on the map by a READBACK before and after.

STATUSES (per subject, then per batch)
  PASS          on the map alive after the ticks, no warn+/error line naming it
  NOT-SPAWNED   readback found fewer than asked right after the spawn
  GONE          spawned, but not on the map alive after the ticks (died, despawned)
  LOG           a warning/error/exception line names the def (word-boundary match)
  LOG-UNATTRIBUTED  an error/exception during the batch that names no subject (batch row)
  LOG-BLIND     logging was not proven alive, or the tap lost entries: UNMEASURED (batch row)
  ART           magenta pixels over the limit in the batch screenshot (batch row)
  ART-BLIND     no readable screenshot: UNMEASURED (batch row)
  RESTARTED     map id changed or the game clock ran backwards during the sitting (batch row)
Exit 0 only when every row is PASS.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

DEFAULT_TICKS = 600
MAX_TICKS = 20000
MAX_COUNT = 10
# RimWorld draws a texture it could not load as BaseContent.BadTex, pure magenta. A
# missing sprite on a 1080p capture is hundreds of pixels; UI chrome holds none.
MAGENTA_MAX_PIXELS = 40
LOG_SENTINEL_PREFIXES = ("[proof log sentinel]",)  # validation_core.LOG_SENTINEL


@dataclass
class Spawn:
    kind: str       # "pawn" | "thing"
    defName: str
    count: int = 1


@dataclass
class L2Spec:
    spawn: list[Spawn]
    ticks: int = DEFAULT_TICKS


@dataclass
class Planned:
    item: str
    kind: str
    defName: str
    count: int
    x: int
    z: int


@dataclass
class Row:
    scope: str      # an item id, or "BATCH"
    subject: str    # "pawn:RSW_Moornak", or the batch check's name
    status: str
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


def parse_l2(raw: Any) -> L2Spec:
    """Validate a manifest's "l2" object. Raises ValueError on anything malformed."""
    if not isinstance(raw, dict):
        raise ValueError("l2 must be an object")
    unknown = set(raw) - {"spawn", "ticks", "note"}
    if unknown:
        raise ValueError("l2 has unknown keys %s" % sorted(unknown))
    sp = raw.get("spawn")
    if not isinstance(sp, list) or not sp:
        raise ValueError("l2.spawn must be a non-empty list")
    out = []
    for i, s in enumerate(sp):
        if not isinstance(s, dict):
            raise ValueError("l2.spawn[%d] is not an object" % i)
        kinds = [k for k in ("pawnKind", "thing") if k in s]
        if len(kinds) != 1:
            raise ValueError("l2.spawn[%d] needs exactly one of pawnKind / thing" % i)
        extra = set(s) - {"pawnKind", "thing", "count"}
        if extra:
            raise ValueError("l2.spawn[%d] has unknown keys %s" % (i, sorted(extra)))
        name = s[kinds[0]]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise ValueError("l2.spawn[%d] defName %r is not a defName" % (i, name))
        n = s.get("count", 1)
        if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= MAX_COUNT:
            raise ValueError("l2.spawn[%d] count must be an int 1..%d" % (i, MAX_COUNT))
        out.append(Spawn("pawn" if kinds[0] == "pawnKind" else "thing", name, n))
    t = raw.get("ticks", DEFAULT_TICKS)
    if not isinstance(t, int) or isinstance(t, bool) or not 1 <= t <= MAX_TICKS:
        raise ValueError("l2.ticks must be an int 1..%d" % MAX_TICKS)
    return L2Spec(out, t)


def batch_ticks(manifests) -> int:
    return max([m.l2.ticks for m in manifests if m.l2] or [0])


def plan_batch(manifests, map_size: tuple[int, int], spacing: int = 6, cols: int = 8,
               margin: int = 10) -> list[Planned]:
    """Lay every L2 spawn of every manifest on one grid centred on the map, one cell per
    spawn op, row-major. Raises ValueError when the grid does not fit inside the margin."""
    ops = [(m.item, s) for m in manifests if m.l2 for s in m.l2.spawn]
    if not ops:
        return []
    w, h = map_size
    ncols = min(cols, len(ops))
    nrows = (len(ops) + ncols - 1) // ncols
    gw, gh = (ncols - 1) * spacing, (nrows - 1) * spacing
    x0, z0 = w // 2 - gw // 2, h // 2 - gh // 2
    if x0 < margin or z0 < margin or x0 + gw > w - margin or z0 + gh > h - margin:
        raise ValueError("a %dx%d grid at spacing %d does not fit a %dx%d map" % (ncols, nrows, spacing, w, h))
    return [Planned(item, s.kind, s.defName, s.count, x0 + (i % ncols) * spacing, z0 + (i // ncols) * spacing)
            for i, (item, s) in enumerate(ops)]


def batch_rect(plan: list[Planned], pad: int = 4) -> tuple[int, int, int, int]:
    xs = [p.x for p in plan]
    zs = [p.z for p in plan]
    x0, z0 = min(xs) - pad, min(zs) - pad
    return x0, z0, max(xs) + pad - x0 + 1, max(zs) + pad - z0 + 1


def _name_re(name: str):
    return re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name))


def attribute_logs(entries: Iterable[dict], defnames: Iterable[str]):
    """Split warn+/error journal entries by the def they name. A defName matches on word
    boundaries only, so RSW_Moornak does not claim a line about RSW_MoornakUnsettled.
    Returns ({defName: [message, ...]}, [unattributed error/exception message, ...]).
    An unattributed WARNING is dropped (a quicktest map warns about plenty that is not
    ours); an unattributed ERROR is kept: on one batch map an error is a batch fault until
    something proves otherwise. The run's own log-alive sentinels are ignored."""
    names = sorted(set(defnames), key=len, reverse=True)
    pats = [(n, _name_re(n)) for n in names]
    by_def: dict[str, list[str]] = {}
    unattributed: list[str] = []
    for e in entries:
        lvl = str(e.get("Level", "")).lower()
        if lvl not in ("warning", "error", "exception"):
            continue  # an info line naming a def is not a fault
        msg = str(e.get("Message", ""))
        if any(p in msg for p in LOG_SENTINEL_PREFIXES):
            continue
        hit = [n for n, rx in pats if rx.search(msg)]
        for n in hit:
            by_def.setdefault(n, []).append(msg[:300])
        if not hit and lvl in ("error", "exception"):
            unattributed.append(msg[:300])
    return by_def, unattributed


def is_magenta(r: int, g: int, b: int) -> bool:
    return r >= 200 and b >= 200 and g <= 60


def magenta_count(pixels: Iterable[tuple]) -> int:
    return sum(1 for p in pixels if is_magenta(p[0], p[1], p[2]))


def magenta_in_png(path: str) -> int:
    """Magenta pixel count of an image file (needs Pillow; python.exe has it)."""
    from PIL import Image  # local: only the live path and its selftest need it
    with Image.open(path) as im:
        return magenta_count(im.convert("RGB").getdata())


def count_on_map(rows: Iterable[dict], kind: str, defName: str) -> int:
    """Readback count of one subject: pawns by `kind` (PawnKindDef), spawned and not dead;
    things by `def`, summing stackCount."""
    n = 0
    for r in rows:
        if kind == "pawn":
            if r.get("kind") == defName and r.get("spawned", True) and not r.get("dead"):
                n += 1
        elif r.get("def") == defName:
            n += int(r.get("stackCount") or 1)
    return n


def verdict(plan: list[Planned], before: dict, placed: dict, after: dict,
            by_def: dict, unattributed: list, *, log_alive: bool, tap_lost: int,
            magenta: int | None, restarted: str | None) -> list[Row]:
    """`before`/`placed`/`after` map (kind, defName) -> readback count before the spawn,
    right after it, and after the ticks. Several plan ops may share a subject; their
    counts add up."""
    want: dict = {}
    for p in plan:
        want[(p.kind, p.defName)] = want.get((p.kind, p.defName), 0) + p.count
    rows: list[Row] = []
    seen = set()
    for p in plan:
        key = (p.kind, p.defName)
        subj = "%s:%s" % key
        if key in seen:
            continue
        seen.add(key)
        b, pl, a = before.get(key, 0), placed.get(key, 0), after.get(key, 0)
        if pl - b < want[key]:
            # a pawn op scatters `count` pawns; a thing op's count is a stack size, so a
            # non-stackable thing reads back 1 however large the count - ask for 1.
            rows.append(Row(p.item, subj, "NOT-SPAWNED", "asked %d, readback %d more than before" % (want[key], pl - b)))
        elif a < pl:
            rows.append(Row(p.item, subj, "GONE", "%d on the map after spawn, %d after the ticks" % (pl, a)))
        elif by_def.get(p.defName):
            rows.append(Row(p.item, subj, "LOG", " | ".join(by_def[p.defName][:3])))
        else:
            rows.append(Row(p.item, subj, "PASS"))
    if restarted:
        rows.append(Row("BATCH", "one-sitting", "RESTARTED", restarted))
    else:
        rows.append(Row("BATCH", "one-sitting", "PASS"))
    if not log_alive or tap_lost:
        rows.append(Row("BATCH", "log", "LOG-BLIND", "log alive=%s, journal entries lost=%d" % (log_alive, tap_lost)))
    elif unattributed:
        rows.append(Row("BATCH", "log", "LOG-UNATTRIBUTED", " | ".join(unattributed[:3])))
    else:
        rows.append(Row("BATCH", "log", "PASS"))
    if magenta is None:
        rows.append(Row("BATCH", "art", "ART-BLIND", "no readable screenshot"))
    elif magenta > MAGENTA_MAX_PIXELS:
        rows.append(Row("BATCH", "art", "ART", "%d magenta pixels (limit %d)" % (magenta, MAGENTA_MAX_PIXELS)))
    else:
        rows.append(Row("BATCH", "art", "PASS", "%d magenta pixels" % magenta))
    return rows


def sitting_broken(start: dict, now: dict, want_ticks: int = 0) -> str | None:
    """`start`/`now`: {"mapId", "ticksGame"}. A different map or a clock that ran backwards
    is a new game: the batch did not stay in one sitting. With `want_ticks`, a clock that
    advanced less than that means the ticks the verdict leans on never ran."""
    if start.get("mapId") is None or start.get("mapId") != now.get("mapId"):
        return "map changed %s -> %s" % (start.get("mapId"), now.get("mapId"))
    t0, t1 = start.get("ticksGame"), now.get("ticksGame")
    if not isinstance(t0, int) or not isinstance(t1, int):
        return "clock unreadable %r -> %r" % (t0, t1)
    if t1 < t0:
        return "clock ran backwards %s -> %s" % (t0, t1)
    if t1 - t0 < want_ticks:
        return "clock advanced %d of %d ticks" % (t1 - t0, want_ticks)
    return None


def flyer_refusals(kind_fields: dict, race_fields: dict) -> list[Row]:
    """A flyer is never live-tested without the owner present (owner, standing ruling), so
    an L2 batch refuses one BEFORE spawning anything. `kind_fields`: {pawnKind: get_defs
    fields or None}; `race_fields`: {race ThingDef: fields or None}. A kind whose race or
    statBases cannot be read is refused too (FLYER-UNKNOWN): unreadable is not "not a flyer"."""
    rows = []
    for kind, kf in sorted(kind_fields.items()):
        race = (kf or {}).get("race")
        rf = race_fields.get(race) if race else None
        stats = (rf or {}).get("statBases")
        if not isinstance(stats, list):
            rows.append(Row("BATCH", "pawn:" + kind, "FLYER-UNKNOWN", "race %r statBases unreadable" % race))
            continue
        ft = [st.get("value") for st in stats if isinstance(st, dict) and st.get("stat") == "MaxFlightTime"]
        if any((v or 0) > 0 for v in ft):
            rows.append(Row("BATCH", "pawn:" + kind, "FLYER", "race %s MaxFlightTime %s: never live-tested" % (race, max(v or 0 for v in ft))))
    return rows


# ---------------------------------------------------------------- live (python.exe only)

def _get_defs(B, defType, names, fields) -> dict:
    r = B.call("jawa/get_defs", defs=";".join("%s/%s" % (defType, n) for n in sorted(names)),
               fields=fields, deep=True)
    return {row.get("defName"): (row.get("fields") if row.get("found") else None) for row in r.get("defs") or []}


def _feed(B, plan) -> int:
    """Fill every spawned subject's Food need: a hungry wild predator (RM_Cindermare) would
    otherwise hunt another subject during the ticks and read as a false GONE."""
    kinds = {p.defName for p in plan if p.kind == "pawn"}
    fed = 0
    for r in B.call("jawa/list_pawns", limit=2000).get("pawns") or []:
        if r.get("kind") in kinds and not r.get("dead"):
            fed += bool(B.call("jawa/pawn_need", pawn=r.get("id"), action="need", need="Food", level=1.0).get("success"))
    return fed


def _readback(B, plan) -> dict:
    out = {}
    pawns = [p.defName for p in plan if p.kind == "pawn"]
    things = sorted({p.defName for p in plan if p.kind == "thing"})
    prow = (B.call("jawa/list_pawns", limit=5000).get("pawns") or []) if pawns else []
    trow = (B.call("jawa/list_things", defName=",".join(things), limit=5000).get("things") or []) if things else []
    if len(prow) >= 5000 or len(trow) >= 5000:
        raise RuntimeError("readback hit its row limit: a count from it would be a floor, not a count")
    for p in plan:
        out[(p.kind, p.defName)] = count_on_map(prow if p.kind == "pawn" else trow, p.kind, p.defName)
    return out


def _clock(B) -> dict:
    mi = B.call("jawa/map_info")
    gi = B.call("rimworld/get_game_info")
    return {"mapId": mi.get("mapId"), "ticksGame": gi.get("ticksGame"), "size": mi.get("mapSize") or {}}


def _open_near(B, x, z, tries=12):
    import stage_review as sr  # noqa: E402  same directory
    for dx in range(tries):
        for cx in (x + dx, x - dx):
            try:
                ok, _ = sr.cell_open(B, cx, z)
            except RuntimeError:
                ok = False
            if ok:
                return cx, z
    return x, z


class _RB(object):
    """stage_review's helpers call rb.call(tool, {args}); validation_core's Bridge takes kwargs."""

    def __init__(self, B):
        self.B = B

    def call(self, tool, args=None):
        return self.B.call(tool, **(args or {}))


def run_l2_live(manifests, *, shot_name="l2_batch", log=print) -> list[Row]:
    """The one L2 sitting: one map, every manifest's spawns, one tick run, one log read,
    one screenshot. Needs a live bridge (python.exe on WSL) and a game at Playing."""
    import os
    import validation_core as vc  # noqa: E402  same directory

    B = vc.Bridge()
    if (B.call("rimworld/get_ui_state").get("programState")) != "Playing":
        log("no game in progress: starting a quicktest map")
        try:
            B.call("rimworld/start_debug_game_ready", timeoutMs=900000, readiness="mapData", pauseIfNeeded=True)
        except Exception as e:  # noqa: BLE001  the socket may drop while the map generates
            log("quicktest call ended: %s" % str(e)[:200])
            B = vc.Bridge()
    kinds = {p.defName for p in plan_batch(manifests, (250, 250)) if p.kind == "pawn"}
    if kinds:
        kf = _get_defs(B, "PawnKindDef", kinds, "race")
        races = {(f or {}).get("race") for f in kf.values()} - {None}
        rf = _get_defs(B, "ThingDef", races, "statBases") if races else {}
        refused = flyer_refusals({k: kf.get(k) for k in kinds}, rf)
        if refused:
            return refused  # nothing spawned: a flyer (or an unreadable race) stops the batch
    start = _clock(B)
    size = (int(start["size"].get("x") or 0), int(start["size"].get("z") or 0))
    plan = plan_batch(manifests, size)
    rb = _RB(B)
    for p in plan:
        p.x, p.z = _open_near(rb, p.x, p.z)
    tap = vc.tap_start(B)
    alive = vc.log_revive(B).get("alive", False)
    before = _readback(B, plan)
    for p in plan:
        if p.kind == "pawn":
            r = B.call("jawa/spawn_pawn", kindDef=p.defName, x=p.x, z=p.z, count=p.count, faction="none")
        else:
            r = B.call("jawa/spawn_batch", ops="%s:%d,%d,%d" % (p.defName, p.x, p.z, p.count))
        log("spawn %s %s @%d,%d x%d -> %s" % (p.kind, p.defName, p.x, p.z, p.count, r.get("success")))
    placed = _readback(B, plan)
    log("fed %d subject pawns" % _feed(B, plan))
    x, z, w, h = batch_rect(plan)
    magenta = None
    try:
        B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (x, z, w, h))
        B.call("jawa/clear_ui")
        B.call("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + h // 2)
        B.call("rimworld/frame_cell_rect", x=x, z=z, width=w, height=h, paddingCells=3)
        B.call("jawa/clear_ui")
        time.sleep(1.0)
        path = B.call("rimworld/take_screenshot", fileName=shot_name, suppressMessage=True).get("path")
        for _ in range(20):
            if path and os.path.exists(path) and os.path.getsize(path) > 0:
                break
            time.sleep(0.5)
        log("screenshot %s" % path)
        magenta = magenta_in_png(path) if path and os.path.exists(path) else None
    except Exception as e:  # noqa: BLE001  an unreadable shot is ART-BLIND, never a pass
        log("screenshot failed: %s" % str(e)[:200])
    ticks = batch_ticks(manifests)
    done = 0
    broken = None
    while done < ticks and not broken:
        n = min(250, ticks - done)
        B.call("rimworld/step_game_ticks", ticks=n)  # tap_after polls the journal after each step
        done += n
        broken = sitting_broken(start, _clock(B))  # a restart mid-run must not hide behind a later clock
    after = _readback(B, plan)
    entries = tap.since()
    by_def, unattributed = attribute_logs(entries, [p.defName for p in plan])
    restarted = broken or sitting_broken(start, _clock(B), want_ticks=ticks)
    return verdict(plan, before, placed, after, by_def, unattributed, log_alive=alive,
                   tap_lost=tap.lost, magenta=magenta, restarted=restarted)
