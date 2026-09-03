"""Which defs TRANSMIT on a network, read from the def dump.

🔴 Why this exists. Power has two joining rules and they are not the same:

  * a TRANSMITTER (`CompProperties_Power.transmitsPower == true`) joins a net
    only by CARDINAL cell adjacency - conduits, but ALSO SolarGenerator and
    Battery, which surprise people;
  * a CONNECTOR (transmitsPower false - Cooler, most machines) binds to the
    nearest transmitter within `PowerConnectionMaker.ConnectMaxDist = 6`.

A connector binds AT SPAWN. A transmitter that appears later does not
retroactively claim it. Measured 2026-08-26: coolers painted before their
conduit bus read `Grid excess: 0 W` even after the bus was energised and the
game ticked; destroying and re-placing the same two coolers, nothing else
changed, took them to 1700 W.

⇒ the compiler must emit every transmitter before any connector.

🔑 This is READ, never guessed. The dump carries `transmitsPower` inside each
ThingDef's json. If the dump cannot be read we return None and the caller keeps
its previous ordering rather than inventing one - an unmeasured answer is not a
licence to make one up.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from game_paths import DUMP_ROOT  # noqa: E402

DUMP_SQLITE = Path(DUMP_ROOT) / "defs.sqlite"

# PipeSystem (Vanilla Expanded Framework) and Rimefeller pipes carry their
# resource the same way a conduit carries power: the pipe piece IS the
# transmitter, and producers/consumers hang off it. Same ordering rule applies.
_PIPE_COMPS = ("PipeSystem.CompProperties_Resource",
               "Rimefeller.CompProperties_Pipe")

_cache: dict[str, bool] = {}


def transmitters(defnames) -> set[str] | None:
    """The subset of `defnames` that transmit on some network.

    Returns None if the dump is unreadable - meaning UNMEASURED, not "none".
    """
    want = sorted({str(d) for d in defnames})
    if not want:
        return set()
    unknown = [d for d in want if d not in _cache]
    if unknown:
        if not DUMP_SQLITE.exists():
            return None
        try:
            con = sqlite3.connect(f"file:{DUMP_SQLITE}?mode=ro", uri=True)
            try:
                qs = ",".join("?" * len(unknown))
                rows = con.execute(
                    f"SELECT def_name, json FROM defs "
                    f"WHERE def_type='ThingDef' AND def_name IN ({qs})",
                    unknown).fetchall()
            finally:
                con.close()
        except sqlite3.Error:
            return None
        found = {}
        for name, blob in rows:
            found[name] = _reads_as_transmitter(blob)
        for d in unknown:
            # absent from the dump is not "does not transmit" - but for ORDERING
            # a false is the safe answer: it only means "emit it later", and a
            # thing emitted late still gets placed.
            _cache[d] = found.get(d, False)
    return {d for d in want if _cache[d]}


def _reads_as_transmitter(blob: str) -> bool:
    try:
        j = json.loads(blob)
    except (ValueError, TypeError):
        return False
    for comp in _iter_comps(j):
        if comp.get("transmitsPower") is True:
            return True
        if str(comp.get("$type", "")) in _PIPE_COMPS:
            return True
        if str(comp.get("compClass", "")) in _PIPE_COMPS:
            return True
    return False


def _iter_comps(j):
    # ⚠️ The dump nests every ThingDef field under a "fields" object; `comps`
    # is NOT a top-level key. Reading it from the root returns None silently,
    # which reads as "nothing transmits" - a clean wrong answer.
    comps = (j.get("fields") or {}).get("comps")
    if isinstance(comps, list):
        for c in comps:
            if isinstance(c, dict):
                yield c
