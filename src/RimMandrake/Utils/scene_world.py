"""scene_world.py - everything outside the scene library that a name touches: the driver lock, the bridge, the repo, the disk.

Page: design/specs/2026-11-23-scene-library/boundary.md. The tests put scene_fake.FakeWorld in its place (scene.WORLD)."""
import glob
import json
import os
import re
import subprocess
import sys
import time

import time_budget  # noqa: E402

from scene_core import CallFailed, Fault, ReplyLost

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
# budget: danger=a bridge call that never answers holds the scene and its game; never reached in the 14 days to 2026-11-24; no
# budget: record of its run
CALL_TIMEOUT_S = 600.0      # a hang guard (boundary.md LIMITS): the older layers use the same


def _unc(p):
    return p.lower().startswith(("\\\\wsl.localhost\\", "\\\\wsl$\\"))


def _import(name, *dirs):
    for d in dirs:
        if d not in sys.path:
            sys.path.append(d)
    return __import__(name)


LOCK_CHILD_DROPS = ("RM_GAME_INSTANCE", "RIMFLOW_DRIVER_LOCK")


def lock_child_env(environ, gen_var):
    """The environment of the WSL child that holds a lock for a Windows driver: without this process's generation and the game pins.
    A dropped name leaves WSLENV too: WSL passes a name that WSLENV lists and this process lacks as an EMPTY value, and an empty
    RIMFLOW_DRIVER_LOCK reads as "no lock path" (game_lock.lock_path), so ArchBig's lock could not be taken (2026-11-24)."""
    drop = (gen_var,) + LOCK_CHILD_DROPS
    env = {k: v for k, v in environ.items() if k not in drop}
    if "WSLENV" in env:
        env["WSLENV"] = ":".join(w for w in env["WSLENV"].split(":") if w and w.split("/")[0] not in drop)
    return env


class RealBridge(object):
    """One bridge socket to one named game. A lost reply is told apart from an answered error."""

    def __init__(self, letter):
        gi = _import("game_instance", HERE)
        os.environ.update(gi.env(letter))           # the client's own guards (driver lock, log folder) follow the named game
        if letter == gi.DEFAULT:
            for k in ("RM_GAME_INSTANCE", "RIMFLOW_DRIVER_LOCK", "GABP_SERVER_PORT", "GABP_TOKEN", "RM_GAME_USERDATA", "RM_GAME_LOGDIR"):
                os.environ.pop(k, None)
        self.rb = _import("rimbridge_client", HERE)
        if letter == gi.DEFAULT:
            self.where = self.rb.resolve_endpoint()
        else:
            self.where = ("127.0.0.1", gi.port(letter), gi.read_token(letter))
        self.S = None
        self._open()

    def _open(self):
        host, port, token = self.where
        if not token:
            raise Fault("NO_GAME", detail="no bridge token for that game: it is not up")
        self.S = self.rb.RimBridge(host=host, port=port, token=token, timeout=CALL_TIMEOUT_S, client_name="scene.py")
        try:
            self.S.connect()
        except self.rb.RimBridgeError as e:
            raise Fault("NO_GAME", detail="the bridge did not answer (python.exe, not WSL python, reaches it): %s" % e)

    def tools(self):
        try:
            return self.S.list_tools()
        except self.rb.RimBridgeError as e:
            raise CallFailed("tools/list: %s" % e)

    def call(self, tool, args):
        if self.S is None or self.S.sock is None:
            self._open()
        try:
            out = self.S.call(tool, args, check=True)
        except (self.rb.DriverHeldError, self.rb.DeadlineError, self.rb.UnknownParameterError, self.rb.RetiredToolError,
                self.rb.IndeterminateError) as e:
            raise CallFailed("%s: %s" % (type(e).__name__, e))     # refused before it was sent
        except self.rb.RimBridgeError as e:
            if " failed: " in str(e):
                raise CallFailed(str(e))
            self.close()                                           # a timed-out connection is never used again
            cid = getattr(e, "indeterminate_cid", None)
            reconcile = (lambda note: self.rb.reconcile_resolve(cid, "applied", note)) if cid else None
            raise ReplyLost("%s: %s" % (tool, e), reconcile=reconcile)
        d = self.rb._reply_dict(out)[0]
        if not isinstance(d, dict):
            raise CallFailed("%s: the reply is not an object: %r" % (tool, str(d)))
        return d

    def close(self):
        if self.S is not None:
            self.S.close()
            self.S = None


class RealWorld(object):
    sleep = staticmethod(time.sleep)
    clock = staticmethod(time.time)

    # ---- the driver lock
    def lock_take(self, letter, purpose):
        """-> {code: 0 | 75 | 3 | 2, line, inherited}. `inherited`: this process drives under a take that is not its own.
        A Windows python cannot claim (rimflow's model needs fcntl), so a WSL child of this process holds the lock: it is
        `game_lock.py run <g> -- cat`, and its input closes when this process ends, however it ends."""
        gl, hg = _import("game_lock", RIMFLOW), _import("host_guard", RIMFLOW)
        q = gl.query(letter)
        if q["state"] == "HELD" and q["code"] != gl.EX_HIS:
            cur, _problem = gl.driver_lock._read(gl.lock_path(letter))
            mine = os.environ.get(hg.ENV_GEN) and cur and str(cur.get("generation")) == os.environ[hg.ENV_GEN]
            # a take of this clone's window is ours to drive under; the take of another scene of this clone is not: it ends with it
            window = os.name == "nt" and cur and hg._windows_in_holders_clone(cur) and not str(cur.get("purpose")).startswith("scene.open ")
            if cur is None:                         # freed between the two reads
                q = gl.query(letter)
            elif mine or q.get("mine") or window:
                return {"code": 0, "line": "drives under the take of %s" % q["line"], "inherited": True}
        if q["code"] != 0:
            return {"code": q["code"], "line": q["line"], "inherited": False}
        if os.name != "nt":
            r = gl.claim(letter, purpose, identity=hg.self_identity())
            if r["code"] == 0 and r.get("generation") is not None:
                os.environ[hg.ENV_GEN] = str(r["generation"])
            return {"code": r["code"], "line": r["line"], "inherited": bool(r.get("reentrant"))}
        distro = gl.driver_lock._wsl_distro()
        if not distro:
            return {"code": 2, "line": "the WSL distro that holds the lock records is not known from here", "inherited": False}
        if _unc(RIMFLOW):
            script = "/" + os.path.join(RIMFLOW, "game_lock.py")[2:].split("\\", 2)[2].replace("\\", "/")
        else:
            # budget: danger=a hung wsl.exe (interop) holds the lock take, and so the scene; never reached in the 14 days to
            # budget: 2026-11-24; no record of its run
            script = subprocess.run(["wsl.exe", "-d", distro, "wslpath", "-u", os.path.join(RIMFLOW, "game_lock.py")], capture_output=True, text=True, timeout=60).stdout.strip()
        env = lock_child_env(os.environ, hg.ENV_GEN)
        p = subprocess.Popen(["wsl.exe", "-d", distro, "python3", script, "run", letter, "--for", purpose, "--", "cat"], stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env)
        said = p.stderr.readline().strip()          # one line: held, or the refusal; an end of file is a child that died
        m = re.search(r"held for .*\(gen (\d+)", said)
        if m:
            self._holder = p
            os.environ[hg.ENV_GEN] = m.group(1)
            return {"code": 0, "line": said, "inherited": "inherited" in said}
        p.stdin.close()
        rc = p.wait(60)                             # 60 s: a hang guard on a child that has already said why it ends
        return {"code": rc if rc in (75, 3, 2) else 2, "line": said or "the lock holder ended with exit %s and said nothing" % rc, "inherited": False}

    def lock_release(self, letter):
        gl, hg = _import("game_lock", RIMFLOW), _import("host_guard", RIMFLOW)
        os.environ.pop(hg.ENV_GEN, None)
        if os.name == "nt":
            p, self._holder = getattr(self, "_holder", None), None
            if p is None:
                return "already free"
            p.stdin.close()
            try:
                p.wait(60)
            except subprocess.TimeoutExpired:
                p.kill()
                return "NOT RELEASED: the holder did not end in 60 s and was killed"
            q = gl.query(letter)
            return "released" if q["code"] == 0 or q.get("generation") is not None and q["state"] == "HELD" and not q.get("mine") else "NOT RELEASED: %s" % q["line"]
        path = gl.lock_path(letter)
        cur, problem = gl.driver_lock._read(path)
        if problem or not cur:
            return "already free" if not problem else "COULD NOT LOOK: %s" % problem
        r = gl.driver_lock.release(path, cur.get("seat"), hg.self_identity())
        return "released" if r.get("ok") else "NOT RELEASED: %s" % r.get("why")

    def connect(self, letter):
        return RealBridge(letter)

    def game_health(self, letter):
        return _import("game_watcher", HERE).read(letter)

    # ---- who drives
    def me(self):
        return _import("host_guard", RIMFLOW).self_identity()

    def alive(self, ident):
        """True, False, or None (cannot inspect)."""
        return _import("driver_lock", RIMFLOW).process_alive(ident or {})

    # ---- the repo
    def wanted(self, mods):
        """-> [(name, packageId, part, {dll: [paths]} or None)]. An unknown tier or mod raises KeyError naming it."""
        if isinstance(mods, str):
            msb = _import("modset_builder", HERE)
            if mods not in msb.TIERS:
                raise KeyError("%r is no tier (modset_builder.py --list)" % mods)
            by = self._folders()
            out = []
            for pid in msb.TIERS[mods]["want"]:
                f = by.get(pid.lower())
                out.append((f or pid, pid.lower(), None, self._dlls(f) if f else {}))
            return out
        bm = _import("build_match", RIMFLOW)
        out = []
        for m in mods:
            pid = bm.mod_package_id(REPO, m)
            if not pid:
                raise KeyError("%r is no mod folder under src/RimMandrake with an About.xml" % m)
            comp = bm.composed_into(REPO, m)
            if comp == bm.COMPOSE_UNREADABLE:
                raise Fault("COULD_NOT_LOOK", detail="Biomes.compose.json could not be read: whether %s is composed is unknown" % m)
            out.append((m, (comp[0] if comp else pid).lower(), m if comp else None, self._dlls(m)))
        return out

    def _folders(self):
        bm = _import("build_match", RIMFLOW)
        top = os.path.join(REPO, "src", "RimMandrake")
        out = {}
        for m in sorted(os.listdir(top)):
            pid = bm.mod_package_id(REPO, m) if os.path.isdir(os.path.join(top, m, "About")) else None
            if pid:
                out[pid.lower()] = m
        return out

    def _dlls(self, mod):
        return _import("loaded_build", RIMFLOW).dlls(os.path.join(REPO, "src", "RimMandrake", mod))

    def judge_loaded(self, reply, pid, dlls, key, part):
        """loaded_build's verdict with the source at this commit on both sides and the running list as the expected list."""
        lb = _import("loaded_build", RIMFLOW)
        return lb.judge(reply, pid, dlls, dlls, expected_ids=reply.get("packageIds"), expected_game=key, part=part)

    def canonical(self):
        cs = _import("canonical_saves", HERE)
        try:
            return cs.read(REPO)
        except cs.Unreadable as e:
            raise Fault("COULD_NOT_LOOK", detail=str(e))

    def companion_hash(self):
        return _import("companion_identity", os.path.join(REPO, "src", "RimMandrake", "bridgetools")).srchash_worktree(REPO)

    def git(self, *args):
        """-> (exit code, stdout). Cannot run: raises Fault COULD_NOT_LOOK."""
        repo = REPO
        cmd = ["git", "-C", repo]
        if os.name == "nt" and _unc(repo):
            distro, _, rest = repo[2:].split("\\", 1)[1].partition("\\")      # the clone lives in WSL: its own git reads it
            cmd = ["wsl.exe", "-d", distro, "git", "-C", "/" + rest.replace("\\", "/")]
        try:
            # budget: danger=a hung git (interop, drvfs) holds the scene and its game; never reached in the 14 days to
            # budget: 2026-11-24; no record of its run
            p = subprocess.run(cmd + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        except (OSError, subprocess.SubprocessError) as e:
            raise Fault("COULD_NOT_LOOK", detail="git could not be run: %s" % e)
        return p.returncode, p.stdout if p.returncode == 0 else p.stdout + p.stderr

    # ---- the disk
    def run_dir(self, label):
        import rmpaths
        base = (rmpaths.rm_win if os.name == "nt" else rmpaths.rm_str)("scratch", "scene_runs")
        d = os.path.join(base, "%s_%s_%d" % (time.strftime("%Y%m%dT%H%M%S"), "".join(c if c.isalnum() else "_" for c in label), os.getpid()))
        os.makedirs(d, exist_ok=True)
        return d

    def save(self, path, text, append=False):
        with open(path, "a" if append else "w", encoding="utf-8") as f:
            f.write(text)

    def picture_path(self, run_dir, name):
        """-> where the game writes a picture of this run: an absolute path in the game's own spelling (python.exe: Windows)."""
        p = os.path.join(run_dir, name + ".png")
        if os.name != "nt":
            try:
                p = subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, timeout=time_budget.CALL_S).stdout.strip() or p
            except (OSError, subprocess.SubprocessError):
                pass
        return p

    def file_stamp(self, path):
        """-> (size, mtime) of a file this machine can read, or None when there is none."""
        if os.name != "nt" and re.match(r"^[A-Za-z]:\\", path):
            path = "/mnt/%s/%s" % (path[0].lower(), path[3:].replace("\\", "/"))
        try:
            st = os.stat(path)
            return st.st_size, st.st_mtime_ns
        except OSError:
            return None

    def read_trace(self, folder, writer, run):
        """-> the records of one run in seq order, or [] (looked, none yet). An unreadable folder raises Fault."""
        out = []
        if not folder or not os.path.isdir(folder):
            raise Fault("COULD_NOT_LOOK", detail="the game's record folder could not be read: %r" % folder)
        for p in sorted(glob.glob(os.path.join(folder, "tps_*_%s_*.jsonl" % writer))):
            with open(p, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    if '"kind":"scene"' not in ln:
                        continue
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        continue                    # a line being written; a lost one shows as a gap in n
                    if r.get("run") == run:
                        out.append(r)
        return sorted(out, key=lambda r: r["seq"])
