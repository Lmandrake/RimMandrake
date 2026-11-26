"""One scene-begin save and its reload, shared by the live scene runners that use it: scene_runner.py, LiveSite
(showcase_common.py) and wind_burn_live.py (RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE).

Owner, 2026-11-17: *"Just save the test in a file and reload... We shouldn't be judging Test Reset as a mod deliverable."*
(standing_rulings.md, "Resetting a test scene is harness housekeeping, never a mod deliverable"). So no scene puts its map
back by hand: it saves the game to a unique file before it changes anything and reloads that file after, on a normal exit
and when it raises.

    with scene_snapshot(call, "wind_burn_live_pre_") as snap:
        ...                                  # the scene; snap.name is the save, snap.evidence its record

`call(tool, **kw)` is the bridge (validation_core.Bridge.call, or a RimBridge client wrapped as
`lambda t, **kw: rb.call(t, kw)`). Mod SETTINGS are not in a save: a scene still puts back the settings it changed.

A failed reload is never swallowed: after a normal exit it raises SceneRestoreError; under a body that raised, the body's
own error propagates carrying `scene_restore_errors` and the failure is printed to stderr. Either way the snapshot stays on
disk, so the map can be reloaded by hand. LiveSite (HugeThings/northstar/showcase_common.py) drives SceneSnapshot directly,
loading through its registered site. Offline proof: selftest_scene_snapshot.py.
"""
import contextlib
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SceneRestoreError(RuntimeError):
    """The scene-begin snapshot could not be (re)loaded: the map is not known to be back where the scene began."""


def unique_name(prefix):
    return prefix + uuid.uuid4().hex[:12]


def load_save(call, name, budget_s=420, sleep=time.sleep):
    """Load `name` from the MAIN MENU (loading over a live game NREs in the teardown), wait for Playing + a current map and
    scan the journal for a broken load. -> receipt; receipt['verified']. test_site_saves.load_site does the same for a
    registered site and then re-applies that site's quiet profile; this is the site-free reload a scene needs."""
    import test_site_saves as T
    rec = {"save": name, "problems": []}
    t0 = time.time()
    menu = T._to_main_menu(call, sleep, min(180, budget_s))
    if menu:
        rec["problems"].append(menu)
        rec["verified"] = False
        return rec
    seq0 = T._journal_seq(call)
    try:
        call("rimworld/load_game", saveName=name, ignoreModCompatibility=True)
    except Exception as ex:                      # noqa: BLE001 - polled below, never resent
        rec["loadCallRaised"] = type(ex).__name__
    got = T._wait(lambda: T._state(call) == "Playing" and (call("jawa/map_info") or {}).get("tile") is not None,
                  budget_s, sleep)
    rec["load_s"] = round(time.time() - t0, 1)
    if got is None:
        rec["problems"].append("no Playing map within %ss of load_game %s" % (budget_s, name))
    else:
        broken = T._load_errors(call, seq0)
        if broken:
            rec["problems"].append("the load logged %s" % broken)
    rec["verified"] = not rec["problems"]
    return rec


class SceneSnapshot(object):
    """take(): save a unique snapshot (optionally reload it so the scene starts on the loaded state it will return to);
    restore(): reload it once -> error strings ([] = back). save(call, name) -> receipt and load(call, name) -> receipt
    with 'verified' default to test_site_saves.save_site into saves_dir (game_paths.SAVES) and load_save."""

    def __init__(self, call, prefix, saves_dir=None, save=None, load=None, sleep=time.sleep):
        self.call, self.prefix, self.sleep = call, prefix, sleep
        self.saves_dir, self._save, self._load = saves_dir, save, load
        self.name, self.saved, self.restored = None, False, False
        self.evidence = {}

    def _do_save(self, name):
        if self._save is not None:
            return self._save(self.call, name)
        import test_site_saves as T
        d = self.saves_dir
        if d is None:
            import game_paths as G
            d = G.SAVES
        return T.save_site(self.call, name, d, sleep=self.sleep, expand=False)   # same session, same list: no fixture

    def _do_load(self):
        if self._load is not None:
            return self._load(self.call, self.name)
        return load_save(self.call, self.name, sleep=self.sleep)

    def take(self, reload=False):
        self.name = unique_name(self.prefix)
        self.evidence["name"] = self.name
        self.evidence["save"] = self._do_save(self.name)
        self.saved = True
        if reload:
            bl = self._do_load() or {}
            self.evidence["baseline_load"] = dict(verified=bl.get("verified"), problems=bl.get("problems"))
            if bl.get("verified") is not True:
                raise SceneRestoreError("scene-begin reload of %s failed: %s" % (self.name, bl.get("problems")))
        return self.evidence

    def restore(self):
        if not self.saved or self.restored:
            return list(self.evidence.get("restore_errors") or [])
        self.restored = True
        errors = []
        try:
            rl = self._do_load() or {}
            self.evidence["restore_load"] = dict(verified=rl.get("verified"), problems=rl.get("problems"))
            if rl.get("verified") is not True:
                errors.append("reload of scene snapshot %s failed: %s" % (self.name, rl.get("problems")))
        except Exception as ex:                  # noqa: BLE001 - reported, never swallowed
            errors.append("reload of scene snapshot %s raised %r" % (self.name, ex))
        self.evidence["restore_errors"] = errors
        return errors


@contextlib.contextmanager
def scene_snapshot(call, prefix, reload=False, **kw):
    """Save before the body, reload after it (normal exit or raise). kw: saves_dir, save, load, sleep (SceneSnapshot)."""
    snap = SceneSnapshot(call, prefix, **kw)
    try:
        snap.take(reload=reload)
        yield snap
    except BaseException as ex:
        errors = snap.restore()
        if errors:
            ex.scene_restore_errors = errors
            if hasattr(ex, "add_note"):
                ex.add_note("SCENE RESTORE FAILED: %s" % "; ".join(errors))
            print("SCENE RESTORE FAILED (the scene also raised %s): %s" % (type(ex).__name__, "; ".join(errors)),
                  file=sys.stderr)
        raise
    errors = snap.restore()
    if errors:
        raise SceneRestoreError("; ".join(errors))
