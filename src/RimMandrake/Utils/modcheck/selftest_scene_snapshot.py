#!/usr/bin/env python3
"""RIMMANDRAKE_SAVE_RELOAD_AROUND_EVERY_TEST_SCENE: offline proof of scene_snapshot.py with a fake bridge that records
every call.

  1. the save happens before the body's first call, under the scene's prefix;
  2. the reload happens after the body, on a normal exit and when the body raises (the body's own error still propagates);
  3. two scenes get different save names;
  4. a failed reload is an error, never swallowed: a normal exit raises SceneRestoreError, a raising body carries the
     restore errors on its exception and prints them; a load that raises is recorded the same way;
  5. a save that fails reloads nothing (there is nothing to go back to) and the body never runs;
  6. take(reload=True) reloads the snapshot before the body and stops the scene when that reload fails;
  7. restore() reloads once, however often it is called;
  8. load_save, the default loader: main menu first, then load_game, a Playing map reads verified, a broken-load journal
     line or a load that never reaches Playing reads unverified with the cause;
  9. the default save is test_site_saves.save_site into saves_dir (a new <name>.rws, never an overwrite);
 10. wind_burn_live.py and showcase_common.LiveSite run through scene_snapshot, and LiveSite no longer keeps its own
     save/reload copy.
Exit 0 all hold, 1 any fails.
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene_snapshot as SS  # noqa: E402

SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
N = [0, 0]


def check(name, ok, detail=""):
    N[0] += 1
    N[1] += 0 if ok else 1
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else ": %s" % (detail,)))
    return ok


class Fake(object):
    """Records every call as (tool, kwargs). save/load stand in for the injected save and loader."""

    def __init__(self, load_ok=True, load_raises=False, save_raises=False):
        self.calls, self.load_ok, self.load_raises, self.save_raises = [], load_ok, load_raises, save_raises

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        return {}

    def save(self, call, name):
        call("fake/save", name=name)
        if self.save_raises:
            raise RuntimeError("save refused")
        return {"path": name + ".rws"}

    def load(self, call, name):
        call("fake/load", name=name)
        if self.load_raises:
            raise RuntimeError("bridge dropped")
        return {"verified": self.load_ok, "problems": [] if self.load_ok else ["no Playing map"]}

    def tools(self):
        return [t for t, _ in self.calls]

    def first(self, tool):
        return self.tools().index(tool)

    def last(self, tool):
        return len(self.calls) - 1 - self.tools()[::-1].index(tool)


def snap(f, prefix="scene_t_", **kw):
    return SS.scene_snapshot(f.call, prefix, save=f.save, load=f.load, **kw)


def main():
    # 1 + 2 normal exit
    f = Fake()
    with snap(f) as s:
        f.call("body/a")
        f.call("body/b")
    t = f.tools()
    check("save before the body's first call", t.index("fake/save") < t.index("body/a"), t)
    check("save name carries the prefix", s.name.startswith("scene_t_") and len(s.name) > len("scene_t_"), s.name)
    check("save and reload use the same name", f.calls[f.first("fake/save")][1]["name"] == s.name
          == f.calls[f.last("fake/load")][1]["name"], f.calls)
    check("reload after the body on a normal exit", f.last("fake/load") > f.last("body/b"), t)
    check("one reload on a normal exit", t.count("fake/load") == 1, t)
    check("evidence names the snapshot and the reload's verified", s.evidence.get("name") == s.name
          and (s.evidence.get("restore_load") or {}).get("verified") is True and s.evidence.get("restore_errors") == [],
          s.evidence)

    # 2 raising body
    f = Fake()
    raised = None
    try:
        with snap(f):
            f.call("body/a")
            raise ValueError("scene broke")
    except ValueError as ex:
        raised = ex
    except Exception as ex:  # noqa: BLE001
        raised = ex
    t = f.tools()
    check("the body's own error propagates", isinstance(raised, ValueError), repr(raised))
    check("reload after the body when it raises", "fake/load" in t and f.last("fake/load") > f.last("body/a"), t)

    # 3 unique names
    a, b = Fake(), Fake()
    with snap(a) as s1:
        pass
    with snap(b) as s2:
        pass
    check("two scenes get different save names", s1.name != s2.name, (s1.name, s2.name))

    # 4 failed reload, normal exit
    f = Fake(load_ok=False)
    raised = None
    try:
        with snap(f) as s:
            f.call("body/a")
    except SS.SceneRestoreError as ex:
        raised = ex
    check("failed reload on a normal exit raises SceneRestoreError", isinstance(raised, SS.SceneRestoreError), repr(raised))
    check("failed reload names the snapshot", raised is not None and s.name in str(raised), str(raised))
    check("failed reload recorded in evidence", bool(s.evidence.get("restore_errors")), s.evidence)

    # 4 failed reload, raising body
    f = Fake(load_ok=False)
    raised, err = None, io.StringIO()
    with contextlib.redirect_stderr(err):
        try:
            with snap(f) as s:
                raise ValueError("scene broke")
        except Exception as ex:  # noqa: BLE001
            raised = ex
    check("failed reload under a raising body keeps the body's error", isinstance(raised, ValueError), repr(raised))
    check("the body's error carries the restore errors", bool(getattr(raised, "scene_restore_errors", None)),
          getattr(raised, "scene_restore_errors", None))
    check("the restore failure is printed", "SCENE RESTORE FAILED" in err.getvalue() and s.name in err.getvalue(),
          err.getvalue())

    # 4 a load that raises
    f = Fake(load_raises=True)
    raised = None
    try:
        with snap(f) as s:
            pass
    except SS.SceneRestoreError as ex:
        raised = ex
    check("a raising load is a restore error, not swallowed", isinstance(raised, SS.SceneRestoreError)
          and "bridge dropped" in " ".join(s.evidence.get("restore_errors") or []), (repr(raised), s.evidence))

    # 5 failed save
    f = Fake(save_raises=True)
    raised, ran = None, []
    try:
        with snap(f):
            ran.append(1)
    except RuntimeError as ex:
        raised = ex
    check("a failed save propagates", raised is not None and "save refused" in str(raised), repr(raised))
    check("a failed save runs no body and reloads nothing", not ran and "fake/load" not in f.tools(), (ran, f.tools()))

    # 6 baseline reload
    f = Fake()
    with snap(f, reload=True) as s:
        f.call("body/a")
    t = f.tools()
    check("take(reload=True) reloads before the body", t.index("fake/load") < t.index("body/a") and t.count("fake/load") == 2,
          t)
    check("baseline load recorded", (s.evidence.get("baseline_load") or {}).get("verified") is True, s.evidence)
    f = Fake(load_ok=False)
    raised, ran = None, []
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            with snap(f, reload=True):
                ran.append(1)
        except SS.SceneRestoreError as ex:
            raised = ex
    check("a failed baseline reload stops the scene", isinstance(raised, SS.SceneRestoreError) and not ran, (repr(raised), ran))

    # 7 idempotent restore
    f = Fake()
    s = SS.SceneSnapshot(f.call, "scene_t_", save=f.save, load=f.load)
    s.take()
    e1, e2 = s.restore(), s.restore()
    check("restore() reloads once", f.tools().count("fake/load") == 1 and e1 == [] and e2 == [], (f.tools(), e1, e2))
    s = SS.SceneSnapshot(f.call, "scene_t_", save=f.save, load=f.load)
    check("restore() before take() reloads nothing", s.restore() == [] and f.tools().count("fake/load") == 1, f.tools())

    # 8 load_save, the default loader
    class Game(object):
        def __init__(self, state="Playing", reach=True, broken=None):
            self.state, self.reach, self.broken, self.calls = state, reach, broken or [], []

        def call(self, tool, **kw):
            self.calls.append(tool)
            if tool == "rimworld/get_ui_state":
                return {"programState": self.state}
            if tool == "rimworld/go_to_main_menu":
                self.state = "Entry"
            elif tool == "rimworld/load_game":
                self.saved_name = kw.get("saveName")
                if self.reach:
                    self.state = "Playing"
            elif tool == "jawa/map_info":
                return {"tile": 7}
            elif tool == "rimbridge/list_logs":
                if kw.get("minimumLevel") == "error":
                    return {"logs": [{"Sequence": 9, "Message": m} for m in self.broken]}
                return {"logs": [{"Sequence": 5}]}
            return {}

    g = Game()
    r = SS.load_save(g.call, "scene_t_x", budget_s=2, sleep=lambda s: None)
    check("load_save goes to the main menu before load_game",
          g.calls.index("rimworld/go_to_main_menu") < g.calls.index("rimworld/load_game"), g.calls)
    check("load_save loads the name asked", getattr(g, "saved_name", None) == "scene_t_x", getattr(g, "saved_name", None))
    check("load_save reads a Playing map as verified", r.get("verified") is True and r.get("save") == "scene_t_x", r)
    g = Game(broken=["Error in Map.FinalizeLoading: boom"])
    r = SS.load_save(g.call, "scene_t_x", budget_s=2, sleep=lambda s: None)
    check("load_save: a broken-load journal line is unverified", r.get("verified") is False
          and "FinalizeLoading" in " ".join(r.get("problems")), r)
    g = Game(reach=False)
    r = SS.load_save(g.call, "scene_t_x", budget_s=0.05, sleep=lambda s: None)
    check("load_save: no Playing map is unverified with the cause", r.get("verified") is False
          and "no Playing map" in " ".join(r.get("problems")), r)

    class Blind(Game):
        """The first state read fails, then the old map reads Playing again; load_game is rejected and changes nothing."""

        def __init__(self):
            Game.__init__(self, reach=False)
            self.reads = 0

        def call(self, tool, **kw):
            if tool == "rimworld/get_ui_state":
                self.reads += 1
                if self.reads == 1:
                    raise RuntimeError("bridge busy")
            if tool == "rimworld/go_to_main_menu":
                self.calls.append(tool)
                return {}                        # the menu request goes nowhere: still Playing
            return Game.call(self, tool, **kw)

    g = Blind()
    r = SS.load_save(g.call, "scene_t_x", budget_s=0.05, sleep=lambda s: None)
    check("load_save: an unread state never loads over the old map as verified", r.get("verified") is False
          and "rimworld/load_game" not in g.calls, (r, g.calls))

    for answer in ({"success": False, "error": "journal offline"}, None, {}, [], {"logs": None}):
        class JournalDown(Game):
            def call(self, tool, **kw):
                if tool == "rimbridge/list_logs" and kw.get("minimumLevel") == "error":
                    self.calls.append(tool)
                    return answer
                return Game.call(self, tool, **kw)

        g = JournalDown()
        r = SS.load_save(g.call, "scene_t_x", budget_s=2, sleep=lambda s: None)
        check("load_save: an unreadable journal (%r) is unverified, never a clean load" % (answer,),
              r.get("verified") is False and "unreadable" in " ".join(r.get("problems")), r)

    # 9 default save into saves_dir
    d = tempfile.mkdtemp(prefix="scene_snap_")
    try:
        import test_site_saves as T
        made = []

        def gcall(tool, **kw):
            if tool == "rimworld/save_game":
                made.append(kw["saveName"])
                with open(os.path.join(d, kw["saveName"] + ".rws"), "w") as fh:
                    fh.write("<savegame/>")
            return {}
        orig = T.save_uncompress.expand_fresh
        T.save_uncompress.expand_fresh = lambda p, extra=None: {"bytes": os.path.getsize(p)}
        try:
            s = SS.SceneSnapshot(gcall, "scene_t_", saves_dir=d, load=lambda c, n: {"verified": True}, sleep=lambda x: None)
            s.take()
        finally:
            T.save_uncompress.expand_fresh = orig
        check("default save writes <name>.rws into saves_dir via save_site", made == [s.name]
              and os.path.isfile(os.path.join(d, s.name + ".rws")) and (s.evidence.get("save") or {}).get("path"),
              (made, s.evidence))
    except Exception as ex:  # noqa: BLE001
        check("default save writes <name>.rws into saves_dir via save_site", False, repr(ex))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # 9b a scene snapshot is reloaded in the same session on the same list, so it is never made portable: a map whose
    # compressed grid holds a modded compressible def (live, ArchSmall 2026-11-26: hash 64117 on the
    # explosiveknockback_visit tier) still snapshots, and the save stays on disk with its grid as the game wrote it.
    d = tempfile.mkdtemp(prefix="scene_snap_")
    try:
        import save_uncompress as SU
        text = ("<savegame><nextThingID>5</nextThingID><compressedThingMapDeflate>%s</compressedThingMapDeflate>"
                "<things></things></savegame>") % SU.write_grid([64117, 0, 0, 0])

        def mcall(tool, **kw):
            if tool == "rimworld/save_game":
                with open(os.path.join(d, kw["saveName"] + ".rws"), "w") as fh:
                    fh.write(text)
            return {}
        s = SS.SceneSnapshot(mcall, "scene_t_", saves_dir=d, load=lambda c, n: {"verified": True}, sleep=lambda x: None)
        try:
            s.take()
            err = None
        except Exception as ex:  # noqa: BLE001
            err = repr(ex)
        p = os.path.join(d, (s.name or "") + ".rws")
        kept = os.path.isfile(p) and open(p).read() == text
        check("a snapshot of a map with a modded compressible def saves, kept as written (no portability expand)",
              err is None and kept, (err, kept))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # 10 the two users
    w = open(os.path.join(SRC, "Pyrelands", "wind_burn_live.py"), encoding="utf-8").read()
    c = open(os.path.join(SRC, "HugeThings", "northstar", "showcase_common.py"), encoding="utf-8").read()
    live_site = c[c.index("class LiveSite"):]
    check("wind_burn_live.py runs through scene_snapshot", "scene_snapshot(" in w and "save_game" not in w, "")
    check("LiveSite runs through scene_snapshot", "SceneSnapshot(" in live_site, "")
    check("LiveSite keeps no save/reload copy of its own", "save_site" not in live_site and "uuid" not in live_site, "")
    check("wind_burn_live.py exits non-zero on FAIL", "sys.exit(main())" in w and "return 0 if" in w, "")
    check("wind_burn_live.py reads an unreadable fire count as an error, never 0",
          'get("countMatched") or 0' not in w and "list_things unreadable" in w, "")
    check("wind_burn_live.py puts back every setting even when one write fails", "settings_restore_errors" in w, "")

    print("%s: %d of %d checks pass" % ("PASS" if not N[1] else "FAIL", N[0] - N[1], N[0]))
    return 0 if not N[1] else 1


if __name__ == "__main__":
    sys.exit(main())
