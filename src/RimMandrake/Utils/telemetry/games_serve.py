"""Runs ON the machine whose games are read (pull_games.py sends this text over ssh; cwd = that machine's
src/RimMandrake/Utils). Reads one JSON request on stdin, {"letters": [...], "have": {rel: [ino, size]}}; answers on
stdout with "RMTEL1 " + one JSON header line, then the bytes of header["send"], in order.

The folders come from that machine's own game_paths / game_instance / rmpaths; a game that cannot be found reads
`error` with its cause, one with no record folder reads `absent`. Files are matched to what the asker has by file id, so
a rename is a rename and only appended bytes travel. Page: design/specs/2026-11-23-telemetry-any-game/boundary.md."""
import glob
import json
import os
import subprocess
import sys
import time

CUT_AFTER = None        # the selftest cuts a transfer here
for k in ("RM_GAME_INSTANCE",):     # the first game is asked for by name; a shell's own choice must not move it
    os.environ.pop(k, None)
sys.path.insert(0, os.getcwd())
req = json.loads(sys.stdin.readline())
have, games, files = req.get("have") or {}, {}, []


def add(rel, path):
    try:
        st = os.stat(path)
        files.append({"rel": rel, "path": path, "ino": st.st_ino, "size": st.st_size, "mtime": st.st_mtime})
    except OSError:     # gone between the list and the stat: it is not there
        pass


def record(letter):
    if letter == "a":
        import game_paths
        return os.path.join(game_paths.LOCALLOW, "JawaBench")
    import game_instance
    return os.path.join(game_instance.data_dir(letter), "JawaBench")


for letter in req["letters"]:
    try:
        tps = os.path.join(record(letter), "tps")
        if not os.path.isdir(tps):
            games[letter] = {"state": "absent"}
            continue
        os.listdir(tps)         # an unreadable folder is an error, never an empty record
        for pat, sub in (("tps_*.jsonl", ""), ("flight_*.jsonl.gz", "flight"), ("exc_*.jsonl", "exc")):
            for p in glob.glob(os.path.join(glob.escape(tps), sub, pat)):
                add("/".join(x for x in (letter, "tps", sub, os.path.basename(p)) if x), p)
        games[letter] = {"state": "ok"}
    except Exception as e:
        games[letter] = {"state": "error", "error": "%s: %s" % (type(e).__name__, e)}
machine_error = None
try:
    import rmpaths
    calls = rmpaths.rm_str("scratch", "bridge_calls.jsonl")
    for p in (calls + ".1", calls):
        if os.path.exists(p):
            add("machine/" + os.path.basename(p), p)
except Exception as e:
    machine_error = "%s: %s" % (type(e).__name__, e)
pids, pids_error = None, None
try:
    r = subprocess.run(["/mnt/c/Windows/System32/tasklist.exe", "/FI", "IMAGENAME eq RimWorldWin64.exe", "/FO", "CSV",
                        "/NH"], capture_output=True, text=True, errors="replace", timeout=20)
    if r.returncode == 0 and r.stdout.strip():      # no match still prints an INFO line: silence is not "no game"
        pids = [int(ln.split('","')[1]) for ln in r.stdout.splitlines() if ln.startswith('"RimWorldWin64.exe"')]
    else:
        pids_error = "tasklist exit %d %s" % (r.returncode, r.stderr.strip()[:200])
except Exception as e:
    pids_error = "%s: %s" % (type(e).__name__, e)

by_ino = {v[0]: v[1] for v in have.values()}
files.sort(key=lambda f: (f["mtime"], f["rel"]))
send = []
for f in files:
    got = by_ino.get(f["ino"])
    off = got if got is not None and got <= f["size"] else 0
    f["off"] = off
    if f["size"] > off or got is None:
        send.append(f)
head = {"now": time.time(), "games": games, "pids": pids, "pids_error": pids_error, "machine_error": machine_error,
        "files": [{k: f[k] for k in ("rel", "ino", "size", "mtime", "off")} for f in files],
        "send": [[f["rel"], f["off"], f["size"] - f["off"]] for f in send]}
out = sys.stdout.buffer
out.write(b"RMTEL1 " + json.dumps(head, separators=(",", ":")).encode() + b"\n")
left = CUT_AFTER
for f in send:
    n = f["size"] - f["off"]
    with open(f["path"], "rb") as fh:
        fh.seek(f["off"])
        while n:
            b = fh.read(min(n, 1 << 20 if left is None else max(left, 1)))
            if not b:
                sys.exit("short read of " + f["path"])
            if left is not None:
                b = b[:left]
                left -= len(b)
                out.write(b)
                if left <= 0:
                    out.flush()
                    sys.exit(9)
            else:
                out.write(b)
            n -= len(b)
out.flush()
