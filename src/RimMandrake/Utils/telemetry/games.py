#!/usr/bin/env python3
"""Which game a telemetry row is about, and what a reading of one game is worth now.

Page: design/specs/2026-11-23-telemetry-any-game/boundary.md. The games come from game_names.GAMES and nowhere else. A
game on the store's machine is read from its own folder (cfg game_dirs); a game on another machine from the copy
pull_games.py keeps under <inbox>/games/<machine>/<letter>/.

    python3 games.py store      "local", or the ssh target of the machine that holds the store (the `telemetry` wrapper)
"""
from __future__ import annotations

import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
for _p in (os.path.dirname(HERE), os.path.join(os.path.dirname(os.path.dirname(HERE)), "rimflow")):
    if _p not in sys.path:      # last: rimflow has a cli.py of its own
        sys.path.append(_p)
import game_names  # noqa: E402
from tcommon import cfg, read_json  # noqa: E402

EX_UNKNOWN, EX_COULD_NOT_LOOK, EX_NO_DATA = 2, 3, 4
BASE_PORT = 5174        # game_instance.BASE_PORT: a game's bridge port is this plus its letter's place
LOOK_S = 300            # a look older than this is not a look: the pull runs each minute, the daemon's heartbeat each pass.
#                         Danger: a dead timer or daemon whose last reading reads as today's (heartbeat missing 2026-10)
STALE_S = 90            # analysis.RULES tps_blind_s: a running game writes a window every 5 s
PULL_STATE = "games_pull.json"
SEG = re.compile(r"tps_\w+?_[0-9A-Za-z.]+_(\d+)_\d+\.jsonl$")


def split(key: str) -> tuple[str, str]:
    """bridge key -> (machine, letter)."""
    m, _, letter = key.partition(".")
    return m, letter or "a"


def all_games() -> list[tuple[str, str, str, str]]:
    return list(game_names.GAMES)


def resolve(text) -> tuple[str, str]:
    """A game as typed -> (name, key). An unknown one raises game_names.GameNameError naming it and the known games."""
    k = game_names.key(text)
    if k is None or k not in [g[1] for g in all_games()]:
        raise game_names.GameNameError("no game %r (games: %s)" % (text, game_names.known()))
    return game_names.show_key(k), k


def here() -> str:
    """The store's machine, as game_names reads it."""
    return game_names.machine()


def is_local(key: str) -> bool:
    return split(key)[0] == here()


def record_dir(key: str) -> str:
    """The folder that holds this game's tps/ (its JawaBench folder, or the pulled copy of it)."""
    d = (cfg().get("game_dirs") or {}).get(key)
    if d:
        return d
    m, letter = split(key)
    if m != here():
        return os.path.join(cfg()["inbox"], "games", m, letter)
    if letter == "a" and os.environ.get("RM_GAME_INSTANCE", "").strip().lower() in ("", "a"):
        return cfg()["jawabench"]
    import game_instance
    if letter == "a":       # from a shell that names another game: that shell's LOCALLOW is the other game's
        return os.path.join(os.path.dirname(game_instance.a_player_log()), "JawaBench")
    return os.path.join(game_instance.data_dir(letter), "JawaBench")


def machine_dir(machine: str) -> str:
    return os.path.join(cfg()["inbox"], "games", machine, "machine")


def home_key() -> str:
    """The first game of the store's machine: its sources keep the names `tps` and `bridge` (their cursors are named by
    them), and the rows written before rows carried a game are its."""
    return here()


def source_name(kind: str, key: str) -> str:
    return kind if key == home_key() else f"{kind}.{key}"


def source_key(name: str) -> str | None:
    """`tps.archmagi.b` -> its key, `tps` -> the home game's; None for a source that is no game's record."""
    kind, _, key = name.partition(".")
    return (key or home_key()) if kind == "tps" else None


def game_of_endpoint(machine: str, endpoint) -> str | None:
    """'127.0.0.1:5175' of a call made on `machine` -> the game's name; None when the row names no game port."""
    m = re.search(r":(\d+)$", str(endpoint or ""))
    i = int(m.group(1)) - BASE_PORT if m else -1
    if not 0 <= i < 26:
        return None
    return game_names.show_key(machine if i == 0 else f"{machine}.{chr(ord('a') + i)}")


def unlabelled(name: str) -> bool:
    """Rows with no game were all written when the store read the home game's record only."""
    return game_names.key(name) == home_key()


def label_re(name: str) -> str:
    return ("|" if unlabelled(name) else "") + re.escape(name)


def selector(name: str) -> str:
    return '{game=~"%s"}' % label_re(name)


def sql_game(name: str, src_col: str | None = None) -> tuple[str, list]:
    """WHERE text and args for rows of this game. src_col: rows with no game count only when they are the TPS record's
    (the events table also holds deploys, alerts and ledger rows, which are no game's)."""
    if unlabelled(name):
        return "(game=? OR (game IS NULL%s))" % (f" AND {src_col}='tps'" if src_col else ""), [name]
    return "game=?", [name]


def pid_of(path: str) -> int | None:
    m = SEG.search(os.path.basename(path))
    return int(m.group(1)) if m else None


def age_s(s: float) -> str:
    return f"{s:.0f}s" if s < 120 else f"{s / 60:.0f}m" if s < 3600 else f"{s / 3600:.1f}h" if s < 172800 \
        else f"{s / 86400:.1f}d"


def look(key: str, now: float, daemon: bool = True) -> dict:
    """Could this game be looked at? {at: last good look or None, error: cause or None, pids, skew, absent}.
    daemon False: the asker reads the record files themselves, so a dead telemetryd hides nothing from it."""
    st = cfg()["state"]
    hb = read_json(os.path.join(st, "heartbeat.json")) or {}
    out = {"at": hb.get("at"), "error": None, "pids": None, "skew": 0.0, "absent": False}
    if not daemon:
        pass
    elif not hb.get("at"):
        out["error"] = "telemetryd has written no heartbeat (telemetry up)"
    elif now - hb["at"] > LOOK_S:
        out["error"] = f"telemetryd heartbeat {age_s(now - hb['at'])} old (telemetry up)"
    if is_local(key):
        if not out["error"]:
            import host
            p = host.process_pids({"rimworldwin64.exe"})
            out["pids"] = p.get("rimworldwin64.exe", []) if p else ([] if os.name == "nt" else None)
        out["absent"] = not os.path.isdir(os.path.join(record_dir(key), "tps"))
        return out
    m, letter = split(key)
    p = (read_json(os.path.join(st, PULL_STATE)) or {}).get(m)
    if not p:
        out.update(at=None, error=out["error"] or f"the pull of {m} has never run (rm-telemetry-pull.timer)")
        return out
    g = (p.get("games") or {}).get(letter) or {}
    out.update(at=p.get("last_ok"), pids=p.get("pids"), skew=p.get("skew") or 0.0, absent=g.get("state") == "absent")
    if out["error"]:
        return out
    if p.get("error"):
        out["error"] = f"{m}: {p['error']}"
    elif now - (p.get("last_ok") or 0) > LOOK_S:
        out["error"] = f"the pull of {m} has not run for {age_s(now - (p.get('last_ok') or 0))} (rm-telemetry-pull.timer)"
    elif not g or g.get("state") == "error":
        out["error"] = f"{m}: {g.get('error') or 'the pull did not read this game'}"
    return out


def status(con, text, now: float | None = None) -> dict:
    """One game's reading: {name, key, rc, state, line}. rc 0 a reading exists; 3 could not look; 4 no data yet."""
    import store
    now = now or time.time()
    name, key = resolve(text)
    lk = look(key, now)
    row = store.kv_get(con, "game:" + name) if con is not None else None
    lookage = f"last look {age_s(max(0, now - lk['at']))} ago" if lk["at"] else "no good look yet"
    newest = None
    if row and row.get("ts"):
        a = max(0.0, now - (row["ts"] - lk["skew"]))
        newest = f"newest row {age_s(a)} ago"
    if lk["error"]:
        line = f"{name}: COULD NOT LOOK ({lk['error']}) · {lookage}" + (
            f" · held from before: {newest}" if newest else " · nothing held from before")
        return {"name": name, "key": key, "rc": EX_COULD_NOT_LOOK, "state": "could_not_look", "line": line,
                "held": newest is not None}
    if newest is None:
        why = "it has no record folder" if lk["absent"] else "no row of its record has been read yet"
        return {"name": name, "key": key, "rc": EX_NO_DATA, "state": "no_data", "held": False,
                "line": f"{name}: no data yet ({why}) · {lookage}"}
    pid = row.get("pid")
    if lk["pids"] is None or pid is None:
        up, proc = None, "process unread"
    elif pid in lk["pids"]:
        up, proc = True, f"up (pid {pid})"
    else:
        up, proc = False, f"down (pid {pid}, which wrote the newest row, is gone)"
    stale = " · STALE (a game that is up writes every 5 s)" if up and a > STALE_S + 60 * (not is_local(key)) else ""
    return {"name": name, "key": key, "rc": 0, "state": {True: "up", False: "down", None: "unread"}[up], "held": True,
            "line": f"{name}: {proc} · {newest} · {lookage}{stale}"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["store"]:
        print("local" if os.path.isdir(cfg()["root"]) else cfg()["store_ssh"])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
