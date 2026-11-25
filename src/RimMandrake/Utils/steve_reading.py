#!/usr/bin/env python3
"""steve_reading.py: read SteveDesktop once each PROBE_EVERY seconds and write conductor/running_steve.json.

The reader of that file is Augur's fleet page (`D:\\ClaudeWork\\augur\\dashboard\\FLEET_NOW.md`, config `remote_hosts`): the file's
`view` block (schema augur.remote_host/1) holds SteveDesktop's machine figures, its two games with their drivers, and the
test-lane jobs by name. One ssh each time, no model, no tokens; it never calls the game bridge. A source that cannot be
read is {"unknown": cause} or a null list with its cause, never 0 or empty. Run by rm-steve-reading.timer each minute;
a run inside PROBE_EVERY of the last probe does nothing.
Promises: design/specs/2026-11-24-fleet-now-stevedesktop/boundary.md.

    python3 steve_reading.py          probe when due, write the file
    python3 steve_reading.py --check  print the file's age and its view's verdict; exit 1 when old or unreadable
"""
import calendar
import json
import os
import re
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(HERE), "rimflow"), HERE]   # game_names: the one map of game names
import rmpaths  # noqa: E402

OUT_DIR = str(rmpaths.rm_path("conductor"))
STEVE_CACHE = OUT_DIR + "/running_steve.json"
TESTQ = str(rmpaths.rm_path("testq"))
PROBE_EVERY = 180           # ssh to SteveDesktop at most this often
# budget: danger=an old figure reads as current; evidence=ten missed 180 s probes; ends no work: withholds old machine, game and service readings
STEVE_STALE = 1800
STEVE_SSH = "stevedesktop-wsl"
STEVE_TS_PEER = "stevedesktop"
STEVE_LAN = "192.168.86.62"
STEVE_SCRIPT = r"""
echo up=$(cut -d" " -f1 /proc/uptime)
echo load=$(cut -d" " -f1 /proc/loadavg)
echo cores=$(nproc)
echo stat=$(grep "^cpu " /proc/stat)
free -m | awk '/^Mem:/{print "ram="$3" "$2}'
df -BG / | awk 'NR==2{gsub("G","",$2);gsub("G","",$4);print "disk="$4" "$2}'
echo claude=$(pgrep -c -x claude)
if t=$(timeout 5 /mnt/c/Windows/System32/tasklist.exe /FO CSV /NH /FI "IMAGENAME eq RimWorldWin64.exe" </dev/null 2>/dev/null); then echo "game=$(printf "%s\n" "$t" | grep -c RimWorldWin64)"; fi
timeout 5 /usr/lib/wsl/lib/nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits </dev/null 2>/dev/null | head -1 | tr -d "\r" | sed s/^/gpu=/
python3 - <<'PY'
import json, os, subprocess
os.environ['RM_HOST'] = 'stevedesktop'
runner = os.path.expanduser('~/rm/runner')
# The enclosing ssh's existing 20 s budget bounds these reads: danger is a hung Windows process-list call blocking the next probe.
for key, argv in (
    ('locks_json', ['python3', 'src/RimMandrake/rimflow/game_lock.py', 'query', 'all', '--json']),
    ('status_json', ['python3', 'src/RimMandrake/Utils/game_instance.py', 'status']),
    ('services_json', ['systemctl', '--user', 'list-units', '--type=service', '--state=running', '--no-pager', '--plain', '--no-legend'])):
    try:
        r = subprocess.run(argv, cwd=None if key == 'services_json' else runner, capture_output=True, text=True)
        d = {'out': r.stdout} if r.returncode == 0 else {'why': '%s exited %s: %s' % (argv[0], r.returncode, (r.stderr or r.stdout).strip())}
    except Exception as e:
        d = {'why': '%s: %s' % (type(e).__name__, e)}
    print(key + '=' + json.dumps(d))
PY
"""


class Unmeasured(Exception):
    """A source could not be read: the file says unknown and why, never a 0."""


# --------------------------------------------------------------------------- the real world (a selftest swaps this)
class Env:
    def now(self):
        return time.time()

    def run(self, argv, timeout=20):
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout

    def read_json(self, path):
        with open(path) as f:
            return json.load(f)

    def listdir(self, path):
        return os.listdir(path)

    def steve_probe(self):
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", STEVE_SSH, "bash -s"], input=STEVE_SCRIPT,
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            raise Unmeasured("ssh exited %d: %s" % (r.returncode, r.stderr.strip()[:80]))
        return r.stdout

    def tailscale_status(self):
        rc, out = self.run(["tailscale", "status", "--json"], timeout=5)
        if rc != 0:
            raise Unmeasured("tailscale status exited %d" % rc)
        return json.loads(out)

    def port_open(self, host, port=22):
        with socket.create_connection((host, port), timeout=1.5):
            return True

    def write_atomic(self, path, text):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)


def guarded(fn, *a):
    """-> (value, None) or (None, why). Every source goes through here so one dead source never kills the page."""
    try:
        return fn(*a), None
    except Unmeasured as e:
        return None, str(e)
    except Exception as e:      # noqa: BLE001 - any failure is "could not read", with its reason
        return None, "%s: %s" % (type(e).__name__, str(e))


def ago(sec):
    sec = int(max(sec, 0))
    if sec < 90:
        return "%d s" % sec
    if sec < 5400:
        return "%d min" % round(sec / 60)
    if sec < 172800:
        return "%.1f h" % (sec / 3600)
    return "%.1f d" % (sec / 86400)


def iso_epoch(t):
    return calendar.timegm(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))


def parse_probe(text):
    out = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def probe_steve(env):
    """Refreshes the cache file; a failed ssh keeps the last good numbers with their age."""
    now = env.now()
    try:
        cache = env.read_json(STEVE_CACHE)
        if not isinstance(cache, dict):
            cache = {}
    except Exception:       # noqa: BLE001 - first run or torn cache
        cache = {}
    if isinstance(cache.get("t"), (int, float)) and now - cache["t"] < PROBE_EVERY:
        return cache
    cache["t"] = now
    routes = {}
    ts, why = guarded(env.tailscale_status)
    if ts is not None:
        peers = [p for p in (ts.get("Peer") or {}).values() if str(p.get("HostName", "")).lower() == STEVE_TS_PEER]
        routes["tailscale"] = bool(peers and peers[0].get("Online"))
    lan, why = guarded(env.port_open, STEVE_LAN)
    routes["lan"] = bool(lan)
    raw, why = guarded(env.steve_probe)
    routes["wsl"] = raw is not None
    cache["routes"] = routes
    if raw is None:
        cache["why"] = why
    else:
        cache.pop("why", None)
        d = parse_probe(raw)
        d["cpu_pct"] = None
        st = [int(x) for x in d.get("stat", "").split()[1:] if x.isdigit()]
        prev = cache.get("stat")
        if not isinstance(prev, list) or any(not isinstance(x, int) for x in prev):
            prev = None
        if st and prev and len(st) >= 8 and len(prev) >= 8 and sum(st[:8]) > sum(prev[:8]):     # guest time is inside user time; I/O wait is not busy
            d["cpu_pct"] = round(100 * (1 - (st[3] + st[4] - prev[3] - prev[4]) / (sum(st[:8]) - sum(prev[:8]))))
        cache["stat"] = st
        cache["good"] = d
        cache["good_t"] = now
    view, why = guarded(steve_view_block, env, cache, now)
    cache["view"] = view if view is not None else {"schema": VIEW_SCHEMA, "host": "SteveDesktop", "written_at": now, "unknown": "view not decoded: " + why}
    env.write_atomic(STEVE_CACHE, json.dumps(cache))
    return cache


VIEW_SCHEMA = "augur.remote_host/1"


def steve_view_block(env, cache, now):
    """The decoded block another dashboard reads (Augur's FLEET_NOW page, promise steve-view-for-augur). Written only with the
    probe, so the file's age still says how old the ssh readings are. Each part has its reading time or {"unknown": cause}."""
    jobs = steve_jobs(env)
    g = collect_steve_games(cache, now, jobs)
    good = cache.get("good") if isinstance(cache.get("good"), dict) else {}
    if g["machine_why"]:
        machine = {"unknown": g["machine_why"], "last_at": cache.get("good_t")}
        games = {"unknown": g["machine_why"]}
    else:
        m = g["machine"]
        machine = {"observed_at": cache["good_t"], "issues": list(g["machine_issues"]), "last_error": cache.get("why")}
        if "load" in m and "cores" in m:
            machine.update(load1=float(m["load"]), ncpu=int(m["cores"]))
        if "ram" in m and int(m["ram"].split()[1]) > 0:
            used, total = (int(x) for x in m["ram"].split())
            machine.update(mem_free_pct=round(100.0 * (total - used) / total, 1), mem_total_mb=total)
        if "disk" in m and int(m["disk"].split()[1]) > 0:
            free, total = (int(x) for x in m["disk"].split())
            machine.update(disk_free_pct=round(100.0 * free / total, 1), disk_free_gb=free)
        if "gpu" in m:
            parts = [x.strip() for x in m["gpu"].split(",")]
            machine.update(gpu_name=parts[0], gpu_pct=float(parts[1]))
        machine["cpu_pct"] = m.get("cpu_pct")
        machine["up_s"] = float(m["up"]) if "up" in m else None
        machine["agents"] = int(good["claude"]) if str(good.get("claude", "")).isdigit() else None
        games = {"observed_at": cache["good_t"], "rows": [
            {"name": r["game"], "up": r["up"], "up_why": r["up_why"], "driver_state": r["driver_state"], "driver": r["driver"],
             "driver_why": r["driver_why"], "for": r["for"], "job": r["job"]} for r in g["games"]]}

    def mine(rows, folder):
        if rows is None:
            return None
        keep = [r for r in rows if (str(r["host"]).startswith("stevedesktop") if folder == "running" else r["lane"] in ("stevedesktop", "any", None))]    # no lane: shown as "lane UNMEASURED", not hidden
        return [{"name": r["desc"], "where": r["where"], "since": r["since"], "id": r["id"]} for r in keep]
    return {"schema": VIEW_SCHEMA, "host": "SteveDesktop", "written_at": now, "machine": machine, "games": games,
            "services": g["services"], "services_why": g["services_why"],      # by unit name, without the lane's own jobs and dbus
            "claude_runs": ({"unknown": g["machine_why"]} if g["machine_why"] else
                            {"unknown": g["services_why"] or "no service list"} if g["claude_runs"] is None else
                            {"observed_at": cache["good_t"], "rows": g["claude_runs"]}),
            "jobs": {"observed_at": now, "running": mine(jobs["running_jobs"], "running"), "running_why": jobs["running_why"],
                     "queued": mine(jobs["pending_jobs"], "pending"), "queued_why": jobs["pending_why"]}}


def steve_jobs(env):
    """Fresh local folder reads: each job by name. A partial read cannot claim a complete list."""
    import game_names
    out = {"job_lookup": {}}
    for folder in ("running", "pending"):
        rows, why = [], None
        try:
            path = TESTQ + "/" + folder
            for name in sorted(n for n in env.listdir(path) if n.endswith(".json")):
                rec = env.read_json(path + "/" + name)
                job = rec.get("job", rec)
                if not isinstance(job, dict) or not all(job.get(k) for k in ("id", "mod", "purpose")) or not isinstance(job.get("selector"), dict):
                    raise Unmeasured("%s has a broken job record" % name)
                stamp = rec.get("sent") if folder == "running" else job.get("submitted")
                if not stamp or not iso_epoch(stamp):
                    raise Unmeasured("%s has no readable %s time" % (name, "sent" if folder == "running" else "submitted"))
                sel = job["selector"]
                if any(not isinstance(sel[k], list) for k in ("chains", "rows", "proofs", "checks", "item") if sel.get(k)):
                    raise Unmeasured("%s has a broken selector" % name)
                runs = "; ".join("%s %s" % (k, ",".join(map(str, sel[k]))) for k in ("chains", "rows", "proofs", "checks", "item") if sel.get(k))
                if sel.get("full"):
                    runs = (runs + "; " if runs else "") + "full suite"
                desc = "%s %s; %s" % (job["mod"], job["purpose"], runs or "selector UNMEASURED: empty selector")
                host = rec.get("host") or job.get("lane") or "stevedesktop"
                if folder == "pending":     # a waiting job's lane names the machine: either of its games may take it
                    game = {"stevedesktop": "either game", "any": "any machine"}.get(job.get("lane"), "lane %s" % (job.get("lane") or "UNMEASURED"))
                else:
                    game = game_names.show_key(host) if host in ("stevedesktop", "stevedesktop.b", "archmagi", "archmagi.b") else host
                rows.append({"desc": desc, "id": job["id"], "attempt": rec.get("attempt"), "where": game, "since": iso_epoch(stamp),
                             "host": host if folder == "running" else None, "lane": job.get("lane")})
        except Exception as e:      # noqa: BLE001 - missing/broken files are a cause, never an empty queue
            rows, why = None, "%s: %s" % (folder, e)
        out[folder + "_jobs"], out[folder + "_why"] = rows, why
        for r in rows or []:
            if folder == "running":
                for key in (r["id"], r["attempt"]):
                    if key:
                        out["job_lookup"][key] = r["desc"]
    return out


def collect_steve_games(cache, now, jobs):
    """Decode the remote readings independently. Omission means DOWN only after a successful, nonempty status."""
    import game_names
    good = cache.get("good") or {}
    age = now - cache["good_t"] if isinstance(cache.get("good_t"), (int, float)) else None
    out = {"machine": good, "machine_why": None, "games": []}
    if not isinstance(good, dict):
        good, out["machine"] = {}, {}
        out["machine_why"] = "broken machine reading"
    if age is None or age > STEVE_STALE:
        cause = "no successful probe" if age is None else "probe reading %s old exceeds STEVE_STALE: %s" % (ago(age), cache.get("why") or "probe stopped refreshing")
        out["machine"], out["machine_why"] = {}, cause
    machine = dict(out["machine"])
    issues = []
    for key in ("up", "load", "cores", "ram", "disk", "gpu", "game", "cpu_pct"):
        val = machine.get(key)
        if key in ("ram", "disk"):
            valid = isinstance(val, str) and len(val.split()) == 2 and all(x.isdigit() for x in val.split())
        elif key == "gpu":
            parts = str(val).split(",")
            valid = len(parts) == 4 and all(x.strip().isdigit() for x in parts[1:])
        else:
            valid = val is not None and re.fullmatch(r"\d+" if key in ("cores", "game") else r"\d+(\.\d+)?", str(val))
        if not valid:
            machine.pop(key, None)
            issues.append("%s UNMEASURED: %s" % (key, "probe did not report a readable value" if key != "cpu_pct" else "two readable CPU samples are needed"))
    if "cpu_pct" in machine:
        machine["cpu_pct"] = float(machine["cpu_pct"])
    out["machine"], out["machine_issues"] = machine, issues

    def read(key):
        if out["machine_why"]:
            raise Unmeasured(out["machine_why"])
        d = json.loads(good.get(key, "{}"))
        if not isinstance(d, dict):
            raise Unmeasured("broken " + key + ": expected an object")
        if d.get("why"):
            raise Unmeasured(str(d["why"]))
        if not isinstance(d.get("out"), str):
            raise Unmeasured("probe did not report readable " + key)
        return d["out"]

    def statuses():
        text = read("status_json")
        rows = dict(re.findall(r"^(Steve[12])\s+(running\b[^\n|]*|stopped\b[^\n|]*)", text, re.M))
        if not rows:
            raise Unmeasured("game status succeeded but no game line was read")
        return rows

    def locks():
        d = json.loads(read("locks_json"))
        rows = d["games"]
        if not isinstance(rows, list) or any(not isinstance(r, dict) or r.get("game") not in ("a", "b") or r.get("state") not in ("HELD", "FREE", "UNKNOWN", "HIS_HOLD")
                or any(r.get(k) is not None and not isinstance(r[k], str) for k in ("seat", "purpose", "cause", "line")) for r in rows):
            raise Unmeasured("broken game lock JSON")
        if len({r["game"] for r in rows}) != len(rows):
            raise Unmeasured("broken game lock JSON: duplicate game")
        return {r["game"]: r for r in rows}

    status, status_why = guarded(statuses)
    drivers, driver_why = guarded(locks)
    for letter in ("a", "b"):
        name = game_names.show(letter, "stevedesktop")
        up = None if status is None else status.get(name, "stopped").startswith("running")
        driver = (drivers or {}).get(letter)
        who_why = driver_why or ("probe omitted the driver lock" if driver is None else None)
        if driver and driver["state"] == "UNKNOWN":
            who_why = driver.get("cause") or driver.get("line") or "driver lock UNKNOWN"
        purpose = (driver or {}).get("purpose") or ""
        job = None
        for key, desc in jobs["job_lookup"].items():
            if re.search(r"(?<![\w.-])" + re.escape(key) + r"(?![\w.-])", purpose):
                job = desc
                break
        if "testq " in purpose and jobs.get("running_why"):
            job = "UNMEASURED: " + jobs["running_why"]
        out["games"].append({"game": name, "up": up,
                             "up_why": status_why if up is None else None, "driver_why": who_why,
                             "driver_state": None if who_why else driver["state"], "driver": None if who_why else driver.get("seat"),
                             "for": None if who_why else driver.get("purpose"), "job": job})
    services, why = guarded(read, "services_json")
    out["services"], out["services_why"] = None, why
    if services is not None:
        units = [line.split()[0] for line in services.splitlines() if line.strip()]
        if any(not u.endswith(".service") for u in units):
            out["services_why"] = "broken systemctl service list"
        else:
            out["services"] = sorted(u for u in units if u != "dbus.service" and not u.startswith("testq-"))
            out["claude_runs"] = sorted((claude_run(line) for line in services.splitlines()
                                         if line.split() and line.split()[0].startswith("rm-detached-")), key=lambda r: r["unit"])
    out.setdefault("claude_runs", None)
    return out


def claude_run(line):
    """One detached Claude run from its systemctl line: the unit, and the item, seat and model that detached_helper.py put
    in the claude argv (--name "DETACHED <SEAT> <ITEM>", --model). The unit name ends in its launch epoch. A part the line
    does not carry is null, never guessed."""
    unit = line.split()[0]
    name = re.search(r'--name\s+\\?"DETACHED\s+(\S+)\s+([A-Za-z0-9_]+)', line)
    model = re.search(r"--model\s+([\w.\-\[\]]+)", line)
    since = re.search(r"-(\d{9,11})(?:-\d+)?\.service$", unit)
    return {"unit": unit, "item": name.group(2) if name else None, "seat": name.group(1) if name else None,
            "model": model.group(1) if model else None, "since": int(since.group(1)) if since else None}


def check(path=None):
    """Print the file's age and its view's verdict. 0: fresh and decoded; 1: old, absent or not decoded."""
    path = path or STEVE_CACHE
    try:
        age = time.time() - os.stat(path).st_mtime
        with open(path) as f:
            view = json.load(f).get("view") or {"unknown": "no view block"}
    except (OSError, ValueError, AttributeError) as e:
        print("running_steve.json: UNMEASURED (%s: %s)" % (type(e).__name__, e))
        return 1
    old = age > STEVE_STALE
    why = view.get("unknown") or (view.get("machine") or {}).get("unknown")
    print("running_steve.json is %s old%s; %s" % (ago(age), " - STALE (limit %s)" % ago(STEVE_STALE) if old else "",
                                                    "UNMEASURED: " + why if why else "machine, games and jobs decoded"))
    return 1 if old or why else 0


def main(argv):
    if "--check" in argv:
        return check()
    os.makedirs(OUT_DIR, exist_ok=True)
    out, why = guarded(probe_steve, Env())
    if out is None:
        print("steve_reading FAILED: %s" % why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
