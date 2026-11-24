#!/usr/bin/env python3
"""scene_empty_game.py: run an in-game scene against an empty game and list the rows that PASS on nothing.

A check that reads PASS when every bridge call answers a bare success and nothing is on the map tests nothing: FlowWorks
visit 1 (2026-11-15) drove three such rows live (RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED; guard SCENES_CAN_ASK,
part 2, design/specs/2026-11-15-cheap-guards-at-every-door.md section 3.4). No game, no bridge, no model.

    EmptyGame            a bridge stand-in: call(tool, **kw) and probe_of(...) -> {"success": True}; ticks(n) -> None.
    rows_on_empty(scene) -> [row]     one FlowWorks-style scene `scene(B, snapshot, reload_snapshot, receipt, ...)` on an
                         EmptyGame; an exception escaping it is one row {"id": <scene>, "status": "ERROR", "detail": ...}.
    vacuous(scenes)      -> [(scene name, row id)] for every row whose status is PASS on the empty game.
    flowworks_vacuous(root) -> (pairs, None) on FlowWorks' concept_scenes.py, or (None, why) when it could not run.
    suite_vacuous(suite, chains=None) -> [(chain, component)] for every component of a modcheck `Suite`'s live chains
                         (offline=True chains left out; `chains` narrows to those names) that reads PASS on a
                         TestContext over an EmptyGame. A chain an exception escapes lists nothing.
    suite_file_vacuous(root, path, chains=None) -> ({"vacuous": [...], "chains": [live chains run], "missing": [...]}, None)
                         for the module-level `suite` of a mod file (validation.py), or (None, why) when it could not run.

    python3 src/RimMandrake/Utils/scene_empty_game.py [--root DIR] [--json]   FlowWorks' vacuous rows; exit 0 none,
                         1 some, 2 did not run (--json: {"vacuous": [[scene, row], ...], "scenes": [every scene run]}
                         or {"did_not_run": why})
    ... --suite FILE [--chains a,b] [--json]   the same for a modcheck Suite file (--json: {"vacuous": [[chain, row]],
                         "chains": [...], "missing": [asked chains the suite lacks]} or {"did_not_run": why})

Two harnesses have an adapter: FlowWorks' scene harness (`_Stage` scenes in a STAGE3_SCENES table) and a modcheck `Suite`
(RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY). The certificate runs each in its own bounded process.
"""
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOWWORKS_SCENES = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
_LOADED = {}      # the scene names flowworks_vacuous last ran: a scene absent from them was never examined


class EmptyGame:
    """Every tool answers "done" with no data: nothing is on the map and nothing can be read."""
    stop_on = None

    def call(self, tool, **kw):
        return {"success": True}

    def probe_of(self, *a, **kw):
        return {"success": True}

    def ticks(self, n):
        return None


def rows_on_empty(scene):
    """-> the rows `scene` returns on an EmptyGame (its receipt's rows when it returns the receipt)."""
    name = getattr(scene, "__name__", "scene")
    receipt = {"calls": []}
    kw = {}
    try:
        params = inspect.signature(scene).parameters
    except (TypeError, ValueError):
        params = {}
    for k in ("save_mid", "load_mid"):
        if k in params:
            kw[k] = lambda: None
    try:
        out = scene(EmptyGame(), lambda: None, lambda: None, receipt, **kw)
    except Exception as e:  # noqa: BLE001  any escape is the scene failing to read an empty answer, never a pass
        return [{"id": name, "status": "ERROR", "detail": ("%s: %s" % (type(e).__name__, e))}]
    rows = out.get("rows") if isinstance(out, dict) else out
    if not isinstance(rows, list):
        return [{"id": name, "status": "ERROR", "detail": "the scene returned no rows: %r" % (out,)}]
    return [r for r in rows if isinstance(r, dict)]


def vacuous(scenes):
    """-> [(scene name, row id)] for every row that reads PASS on the empty game, in the table's order."""
    out = []
    for name, scene in (scenes or {}).items():
        for r in rows_on_empty(scene):
            if r.get("status") == "PASS":
                out.append((name, r.get("id")))
    return out


def flowworks_vacuous(root):
    """-> (vacuous pairs, None) for FlowWorks' STAGE3_SCENES under root, or (None, why) when the scenes cannot be loaded."""
    path = os.path.join(root, FLOWWORKS_SCENES)
    if not os.path.isfile(path):
        return None, "%s is not there" % FLOWWORKS_SCENES
    north = os.path.dirname(path)
    utils = os.path.join(root, "src/RimMandrake/Utils")
    added = [p for p in (north, utils, os.path.join(utils, "modcheck")) if p not in sys.path]
    sys.path[:0] = added
    import types
    m = types.ModuleType("concept_scenes_empty_game")
    m.__file__ = path
    try:
        with open(path, encoding="utf-8") as fh:
            exec(compile(fh.read(), path, "exec"), m.__dict__)  # noqa: S102  our own scene file, loaded as its runner does
    except Exception as e:  # noqa: BLE001
        return None, "%s did not load: %s: %s" % (FLOWWORKS_SCENES, type(e).__name__, str(e))
    finally:
        for p in added:
            if p in sys.path:
                sys.path.remove(p)
    scenes = getattr(m, "STAGE3_SCENES", None)
    if not isinstance(scenes, dict) or not scenes:
        return None, "%s has no STAGE3_SCENES table" % FLOWWORKS_SCENES
    _LOADED["scenes"] = list(scenes)
    return vacuous(scenes), None


class _VirtualClock:
    """Time on an empty game is free: sleep() advances the clock at once and every read moves it on 10 ms, so a chain
    waiting for a game state (Pyrelands' northstar_site._wait_state: 420 s of real polling) runs out its budget in
    milliseconds and reads as could-not-see, never as a pass. Installed only around a chain run, and put back after."""
    STEP = 0.01

    def __enter__(self):
        import time as T
        self.T, self.real = T, (T.time, T.monotonic, T.perf_counter, T.sleep)
        self.offset = 0.0

        def tick(real):
            def now():
                self.offset += self.STEP
                return real() + self.offset
            return now

        def sleep(sec):
            self.offset += max(0.0, float(sec or 0))
        T.time, T.monotonic, T.perf_counter = (tick(f) for f in self.real[:3])
        T.sleep = sleep
        return self

    def __exit__(self, *exc):
        self.T.time, self.T.monotonic, self.T.perf_counter, self.T.sleep = self.real
        return False


_SEALED = frozenset(("os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.symlink", "os.link", "os.truncate",
                     "os.chmod", "os.chown", "os.utime", "shutil.copyfile", "shutil.copytree", "shutil.rmtree",
                     "shutil.move", "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork",
                     "os.forkpty", "pty.spawn", "socket.connect"))
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
REFUSED = []      # every act the sandbox refused, "<event> <target>"


def sandbox():
    """Seal this process (an audit hook, never removed): a chain does its setup for real (Pyrelands'
    northstar_site.save_fixture copies the live Saves folder), so the --suite child refuses every write, delete,
    subprocess and connection with PermissionError and records it in REFUSED."""
    sys.dont_write_bytecode = True

    def hook(event, args):
        if event == "open":
            mode, flags = args[1], args[2] or 0
            if not ((isinstance(mode, str) and any(c in mode for c in "wax+")) or flags & _WRITE_FLAGS):
                return
        elif event not in _SEALED:
            return
        REFUSED.append("%s %s" % (event, str(args[0] if args else "")))
        raise PermissionError("scene_empty_game sandbox refused %s" % event)
    sys.addaudithook(hook)


def suite_vacuous(suite, chains=None):
    """-> [(chain name, component name)] for every component that reads PASS when its chain runs on an empty game."""
    sys.path[:0] = [p for p in (HERE, os.path.join(HERE, "modcheck")) if p not in sys.path]
    from modcheck.suite import TestContext, PASS
    out, offline = [], set(getattr(suite, "offline_chains", ()) or ())
    for name, fn in list(getattr(suite, "chains", ()) or ()):
        if name in offline or (chains is not None and name not in chains):
            continue
        t = TestContext(EmptyGame())
        try:
            with _VirtualClock():
                fn(t)
        except Exception:  # noqa: BLE001  a chain that cannot read an empty answer is not a vacuous pass
            continue
        out.extend((name, c.name) for c in t.components if c.verdict == PASS)
    return out


def suite_file_vacuous(root, path, chains=None):
    """-> (result, None) for the module-level modcheck `suite` in `path` (repo-relative), or (None, why)."""
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return None, "%s is not there" % path
    utils = os.path.join(root, "src/RimMandrake/Utils")
    added = [p for p in (os.path.dirname(full), utils, os.path.join(utils, "modcheck")) if p not in sys.path]
    sys.path[:0] = added
    import types
    m = types.ModuleType("suite_empty_game")
    m.__file__ = full
    try:
        with open(full, encoding="utf-8") as fh:
            exec(compile(fh.read(), full, "exec"), m.__dict__)  # noqa: S102  our own mod file, loaded as its runner does
    except BaseException as e:  # noqa: BLE001  SystemExit at import included: it did not load
        return None, "%s did not load: %s: %s" % (path, type(e).__name__, str(e))
    suite = getattr(m, "suite", None)
    if not hasattr(suite, "chains") or not hasattr(suite, "offline_chains"):
        return None, "%s has no module-level modcheck suite" % path
    have = [n for n, _ in suite.chains if n not in suite.offline_chains]
    ask = None if chains is None else [c for c in chains if c in have]
    return {"vacuous": [list(p) for p in suite_vacuous(suite, ask)], "chains": have if ask is None else ask,
            "missing": [] if chains is None else [c for c in chains if c not in have], "refused": REFUSED[:20]}, None


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--suite", help="a mod file with a module-level modcheck suite (repo-relative)")
    ap.add_argument("--chains", help="comma-separated chain names to run (default: every live chain)")
    a = ap.parse_args(argv)
    if a.suite:
        import json
        sandbox()
        res, why = suite_file_vacuous(a.root, a.suite, a.chains.split(",") if a.chains else None)
        if a.json:
            print(json.dumps({"did_not_run": why} if res is None else res))
        elif res is None:
            print("DID NOT RUN: %s" % why)
        else:
            for c, r in res["vacuous"]:
                print("VACUOUS %s %s" % (c, r))
            for act in res["refused"]:
                print("REFUSED %s" % act)
            print("%d row(s) pass on an empty game over %d chain(s)%s" % (
                len(res["vacuous"]), len(res["chains"]), "" if res["vacuous"] else " (looked, none)"))
        return 2 if res is None else 1 if res["vacuous"] else 0
    pairs, why = flowworks_vacuous(a.root)
    if a.json:
        import json
        names = sorted(_LOADED.get("scenes") or []) if pairs is not None else []
        print(json.dumps({"did_not_run": why} if pairs is None else {"vacuous": pairs, "scenes": names}))
        return 2 if pairs is None else 1 if pairs else 0
    if pairs is None:
        print("DID NOT RUN: %s" % why)
        return 2
    for s, r in pairs:
        print("VACUOUS %s %s" % (s, r))
    print("%d row(s) pass on an empty game%s" % (len(pairs), "" if pairs else " (looked, none)"))
    return 1 if pairs else 0


if __name__ == "__main__":
    sys.exit(main())
