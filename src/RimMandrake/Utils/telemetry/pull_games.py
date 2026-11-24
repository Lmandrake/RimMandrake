#!/usr/bin/env python3
"""Copy the telemetry record of every game on another machine into <inbox>/games/<machine>/ (rm-telemetry-pull.timer,
each minute, on the store's machine under WSL). One ssh call per machine; only new bytes travel.

Which games: game_names.GAMES. How a machine is reached: host_guard.SSH_TARGETS, and host_guard.RUNNER_DIR is the clone
there that knows its folders. State, one entry per machine, in <state>/games_pull.json: last_try, last_ok, error (the
cause, None when the last look was good), skew (its clock less ours), pids, each game's state and last good look,
and the files' ids.
A machine that could not be read keeps its last good look and never reads as an empty one (games.look).

    pull_games.py               every other machine; exit 0 all read, 3 one or more could not be (the cause on stdout)
Page: design/specs/2026-11-23-telemetry-any-game/boundary.md; tests: selftest_telemetry_games.py.
"""
from __future__ import annotations

import glob
import json
import os
import shlex
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import games  # noqa: E402
from tcommon import cfg, read_json, write_json_atomic  # noqa: E402

HANG_S = 900        # hang guard. Danger: an ssh that never ends would hold the timer's unit for good (robocopy held a run
#                     3.6 h on 2026-11-02, tool_traps.md). The first pull of 156 MB is the largest a run carries.
KEEP_DAYS = 7       # a copy whose original the game already deleted: the inbox's own line (wsl_export), raw/ has the rows


def ssh_argv(machine: str) -> list[str] | None:
    import host_guard
    target = host_guard.SSH_TARGETS.get(machine)
    if not target:
        return None
    env = "infrastructure/stevedesktop/testcentre_env.sh"   # host_guard.remote_argv's rule: that clone's own env file
    src = open(os.path.join(HERE, "games_serve.py"), encoding="utf-8").read()
    cmd = "cd %s && if test -f %s; then . %s; fi; cd src/RimMandrake/Utils && exec python3 -c %s" % (
        host_guard.RUNNER_DIR, env, env, shlex.quote(src))
    return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ServerAliveInterval=15",
            "-o", "LogLevel=ERROR", target, cmd]


def _apply(root: str, head: dict, stream, ids: dict) -> int:
    """Renames first (a rotation), then each slice onto its file. Raises on a short stream; what arrived stays."""
    by_ino = {v: k for k, v in ids.items()}
    moves = []
    for f in head["files"]:
        was = by_ino.get(f["ino"])
        if was and was != f["rel"] and os.path.exists(os.path.join(root, was)):
            moves.append((was, f["rel"]))
    for was, _rel in moves:         # through a side name, so a swap or a chain never overwrites a file not yet moved
        os.replace(os.path.join(root, was), os.path.join(root, was) + ".moving")
        ids.pop(was, None)
    for was, rel in moves:
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.replace(os.path.join(root, was) + ".moving", dst)
    for f in head["files"]:
        if any(rel == f["rel"] for _w, rel in moves):
            ids[f["rel"]] = f["ino"]
    meta = {f["rel"]: f for f in head["files"]}
    n_bytes = 0
    for rel, off, n in head["send"]:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if off == 0 and os.path.exists(p):      # another file under this name: the copy goes, whole
            os.remove(p)
        ids[rel] = meta[rel]["ino"]
        with open(p, "ab") as out:
            if out.tell() != off:
                raise OSError(f"{rel}: the copy holds {out.tell()} bytes, the answer starts at {off}")
            while n:
                b = stream.read(min(n, 1 << 20))
                if not b:
                    raise OSError(f"the transfer was cut in {rel}, {n} bytes short")
                out.write(b)
                n -= len(b)
                n_bytes += len(b)
        os.utime(p, (meta[rel]["mtime"], meta[rel]["mtime"]))    # ingest reads files in time order
    for rel in [r for r in ids if r not in meta]:
        del ids[rel]
    for p in glob.glob(os.path.join(glob.escape(root), "**", "*"), recursive=True):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if os.path.isfile(p) and rel not in meta and time.time() - os.path.getmtime(p) > KEEP_DAYS * 86400:
            os.remove(p)
    return n_bytes


def pull(machine: str, argv: list[str] | None = None, cwd: str | None = None) -> dict:
    """One look at `machine`. -> its new state entry plus `bytes`, the bytes copied."""
    sp = os.path.join(cfg()["state"], games.PULL_STATE)
    all_state = read_json(sp, {}) or {}
    st = all_state.get(machine) or {}
    root = os.path.join(cfg()["inbox"], "games", machine)
    ids = dict(st.get("ids") or {})
    have = {}
    for rel, ino in ids.items():
        try:
            have[rel] = [ino, os.path.getsize(os.path.join(root, rel))]
        except OSError:
            continue
    t0 = time.time()
    st.update(last_try=t0)
    head, n_bytes, err = None, 0, None
    argv = argv or ssh_argv(machine)
    if not argv:
        err = "no ssh route to this machine (host_guard.SSH_TARGETS)"
    else:
        try:
            p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        except OSError as e:
            p, err = None, f"{type(e).__name__}: {e}"
        if p is not None:
            guard = threading.Timer(HANG_S, p.kill)
            guard.start()
            errs: list[bytes] = []
            drain = threading.Thread(target=lambda: errs.append(p.stderr.read()), daemon=True)
            drain.start()
            try:
                try:
                    p.stdin.write(json.dumps({"letters": [g[3] for g in games.all_games() if g[2] == machine],
                                              "have": have}).encode() + b"\n")
                    p.stdin.close()
                except OSError:
                    pass        # it ended before reading: the exit code and its stderr say why
                line = p.stdout.readline()
                t_head = time.time()
                if line.startswith(b"RMTEL1 ") and line.endswith(b"\n"):
                    head = json.loads(line[7:])
                    n_bytes = _apply(root, head, p.stdout, ids)
            except (OSError, ValueError, KeyError) as e:
                err = f"{type(e).__name__}: {e}"
            finally:
                if head is None or err:
                    p.stdout.close()
                rc = p.wait()
                guard.cancel()
                drain.join(5)
            tail = (errs[0] if errs else b"").decode(errors="replace").strip()[-300:]
            if rc != 0:
                err = (err + "; " if err else "") + f"exit {rc}" + (f": {tail}" if tail else "")
            elif head is None:
                err = err or f"the answer is not a reading (it starts {line[:60]!r})"
    looked_at = time.time() if err is None else None
    if head is not None:
        previous = st.get("games") or {}
        outcomes = {}
        for letter, g in head["games"].items():
            last_ok = games.last_good(st, previous.get(letter) or {})
            if looked_at is not None and g["state"] in ("ok", "absent"):
                last_ok = looked_at
            outcomes[letter] = {**g, "last_ok": last_ok}
        st.update(skew=round(head["now"] - t_head, 1), pids=head.get("pids"), pids_error=head.get("pids_error"),
                  games=outcomes, machine_error=head.get("machine_error"))
    st.update(ids=ids, error=err, seconds=round(time.time() - t0, 1))
    if looked_at is not None:
        st["last_ok"] = looked_at
    all_state[machine] = st
    write_json_atomic(sp, all_state)
    return {**st, "bytes": n_bytes}


def main() -> int:
    if not os.path.isdir(cfg()["root"]):
        print(f"telemetry root {cfg()['root']} absent: nothing pulled (UNMEASURED)", file=sys.stderr)
        return 2
    import fcntl
    lock = open(os.path.join(cfg()["state"], "games_pull.lock"), "a")
    fcntl.flock(lock, fcntl.LOCK_EX)       # a hand run beside the timer's would append the same bytes twice
    rc = 0
    for m in sorted({g[2] for g in games.all_games()} - {games.here()}):
        r = pull(m)
        print(f"{m}: " + (f"COULD NOT LOOK: {r['error']}" if r["error"] else
                          f"read, {r['bytes']} new bytes in {r['seconds']} s, games "
                          + ", ".join(f"{k} {v['state']}" for k, v in sorted((r.get('games') or {}).items()))))
        rc = 3 if r["error"] else rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
