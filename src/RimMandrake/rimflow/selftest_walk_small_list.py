#!/usr/bin/env python3
"""He walks a mod on its small list, on the game that holds the walk save (owner, 2026-11-24; page
design/specs/2026-11-24-full-list-walk-not-per-mod/boundary.md). Offline: every reading is a stand-in."""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_match as BM  # noqa: E402
import game_lock as GL  # noqa: E402
import maturation as M  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402
import small_list as SL  # noqa: E402

BAD, N = [], [0]


def check(ok, name):
    N[0] += 1
    if not ok:
        BAD.append(name)
    print("%s  %s" % ("ok   " if ok else "FAIL ", name))


B_SAVE = r"D:\ClaudeWork\rimmandrake\instances\b\Saves\X_WALK.rws"
A_SAVE = r"C:\Users\x\Saves\X_WALK.rws"


class Patch:
    def __init__(self, obj, **kw):
        self.obj, self.kw = obj, kw

    def __enter__(self):
        self.old = {k: getattr(self.obj, k) for k in self.kw}
        for k, v in self.kw.items():
            setattr(self.obj, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(self.obj, k, v)



BASE = ["ludeon.rimworld", *SL.DLC, "ray1203.simplecamerasetting", SL.CHARACTER_EDITOR, "our.mod"]
INST = {"other.mod": {"name": "Other Mod"}, "lite.mod": {"name": "Lite"}, "rare.mod": {"name": "Rare"}, "fold.mod": {"name": "Folded"}}
FULL = {"other.mod", "lite.mod", SL.BIOMES}


def j(need, tl=BASE, also=None, fold=frozenset()):
    return SL.judge(need, also, tl, INST, FULL, fold)


def tree(files):
    d = tempfile.mkdtemp()
    for rel, txt in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
    return d


def raises(fn, *a):
    try:
        fn(*a)
    except SL.CouldNotLook as e:
        return str(e)
    return None


def t_a_patched_mod_absent_from_the_list_fails():
    f, o = j({("id", "other.mod"): ["Defs/a.xml"]})
    check(len(f) == 1 and "other.mod" in f[0] and "Defs/a.xml" in f[0], "a-patched-mod-absent-from-the-list-fails")
    f, o = j({("id", "other.mod"): ["Defs/a.xml"]}, BASE + ["Other.Mod_steam"])
    check(not f and not o, "...and the same mod on the list passes (case and _steam do not matter)")
    d = tree({"About/About.xml": "<ModMetaData><modDependencies><li><packageId>Dep.Mod</packageId></li></modDependencies></ModMetaData>",
              "1.6/Patches/p.xml": '<Patch><Operation Class="PatchOperationFindMod"><mods><li>A</li><li>B</li></mods></Operation></Patch>',
              "Defs/d.xml": '<Defs><ThingDef MayRequire="X.Y,Z.W"/><ThingDef MayRequireAnyOf="P.Q,R.S"/></Defs>',
              "review/Defs/r.xml": '<Defs><ThingDef MayRequire="not.shipped"/></Defs>'})
    n = SL.needs(d)
    check(set(n) == {("id", "dep.mod"), ("name", "A\nB"), ("id", "x.y"), ("id", "z.w"), ("any", "p.q,r.s")},
          "...read from dependencies, FindMod and MayRequire (%s)" % sorted(n))


def t_a_mod_he_does_not_play_is_named_not_failed():
    f, o = j({("id", "rare.mod"): ["Defs/a.xml"]})
    check(not f and len(o) == 1 and "rare.mod" in o[0], "a-mod-he-does-not-play-is-named-not-failed")


def t_one_of_a_findmod_group_is_enough():
    f, o = j({("name", "Lite\nOther Mod"): ["Patches/p.xml"]}, BASE + ["lite.mod"])
    check(not f, "one-of-a-findmod-group-is-enough")
    check(len(j({("name", "Lite\nOther Mod"): ["Patches/p.xml"]})[0]) == 1, "...and none of it fails")
    check(not j({("any", "other.mod,rare.mod"): ["Defs/a.xml"]}, BASE + ["rare.mod"])[0], "...and one of a MayRequireAnyOf")


def t_a_findmod_name_that_no_mod_has_fails():
    f, o = j({("name", "Othr Mod"): ["Patches/p.xml"]})
    check(len(f) == 1 and "never match" in f[0], "a-findmod-name-that-no-mod-has-fails")


def t_a_folded_mod_is_held_by_baroque_biomes():
    f, o = j({("id", "fold.mod"): ["Defs/a.xml"]}, BASE + [SL.BIOMES], fold={"fold.mod"})
    check(not f and not o, "a-folded-mod-is-held-by-baroque-biomes")
    check(len(j({("id", "fold.mod"): ["Defs/a.xml"]}, fold={"fold.mod"})[0]) == 1, "...and without Baroque Biomes it fails")


def t_every_list_holds_all_five_expansions():
    for d in SL.DLC:
        f, o = j({}, [x for x in BASE if x != d])
        check(len(f) == 1 and d in f[0], "every-list-holds-all-five-expansions: %s" % d)


def t_every_list_holds_character_editor():
    # owner 2026-11-25: "Please add Character Editor to all smallmod lists, beside the Zoom requirement."
    f, o = j({}, [x for x in BASE if x != SL.CHARACTER_EDITOR])
    check(len(f) == 1 and "Character Editor" in f[0], "every-list-holds-character-editor")


def t_every_list_holds_the_zoom_mod():
    f, o = j({}, [x for x in BASE if x not in SL.ZOOMS])
    check(len(f) == 1 and "zoom" in f[0], "every-list-holds-the-zoom-mod")
    check(not j({}, [x for x in BASE if x not in SL.ZOOMS] + ["brrainz.cameraplus"])[0], "...and Camera+ is one")


def t_a_mod_the_code_reaches_is_needed_when_declared():
    f, o = j({}, also={"other.mod": "C# type"})
    check(len(f) == 1 and "C# type" in f[0], "a-mod-the-code-reaches-is-needed-when-declared")


def t_an_unreadable_patch_is_could_not_look():
    d = tree({"About/About.xml": "<ModMetaData/>", "Patches/p.xml": "<Patch><broken"})
    check("p.xml" in (raises(SL.needs, d) or ""), "an-unreadable-patch-is-could-not-look")


def t_an_about_that_fails_once_is_read_again():
    import modset_builder as MB
    calls, bad = [], [2]

    def flaky(*a, **k):
        calls.append(1)
        if len(calls) < bad[0]:
            sys.stderr.write("  ! could not parse /x/About.xml (OSError: no memory) -- this mod will read as NOT INSTALLED\n")
        return {"a": {"name": "A"}}
    with Patch(MB, scan=flaky):
        check(SL.scan() == {"a": {"name": "A"}} and len(calls) == 2, "an-about-that-fails-once-is-read-again")
        bad[0] = 99
        check("could not parse" in (raises(SL.scan) or ""), "...one that keeps failing is could not look, never not installed")


def t_could_not_look_exits_two():
    def blind():
        raise SL.CouldNotLook("planted: a scan that cannot read")
    with Patch(SL, scan=blind), contextlib.redirect_stdout(io.StringIO()) as out:
        rc = SL.main(["check", "--mod", "FlowWorks"])
    check(rc == 2 and "COULD NOT LOOK" in out.getvalue(), "could-not-look-exits-two (exit %s)" % rc)


def t_a_walk_save_on_the_small_list_passes():
    root = tree({"design/concepts/M/version/small_list.json": json.dumps({"tier": "bridge"}),
                 "design/concepts/K/version/small_list.json": "{"})
    with Patch(SL, resolve=lambda t, i: (["a.mod", "b.mod"], [])):
        check(SL.walk_save_why(root, "M", ["B.Mod", "a.mod_steam"], {}) is None, "a-walk-save-on-the-small-list-passes")
        w = SL.walk_save_why(root, "M", ["a.mod", "b.mod", "c.mod"], {})
        check(w and "has also c.mod" in w and "tier bridge" in w, "...one with more mods is refused with its repair")
        w = SL.walk_save_why(root, "M", ["a.mod"], {})
        check(w and "lacks b.mod" in w, "...one that lacks a mod is refused")
        check(SL.walk_save_why(root, "NoList", ["a.mod"], {}) is None, "...a mod with no list is not judged by its save")
        check(raises(SL.walk_save_why, root, "K", ["a.mod"], {}), "...an unreadable small list is could not look")
    with Patch(SL, resolve=lambda t, i: ([], ["missing z"])):
        check("cannot be built" in (SL.walk_save_why(root, "M", ["a.mod"], {}) or ""), "...a refused tier says so")


def t_the_walk_game_holds_the_save():
    import game_instance
    with Patch(game_instance, root=lambda: "/mnt/d/ClaudeWork/rimmandrake/instances"):
        check(BM.walk_letter(B_SAVE) == "b", "the-walk-game-holds-the-save: an ArchSmall save is walked on ArchSmall")
        check(BM.walk_letter(B_SAVE.replace("D:\\", "/mnt/d/").replace("\\", "/")) == "b", "...in the WSL spelling too")
        check(BM.walk_letter(A_SAVE) == "a" and BM.walk_letter(None) == "a" and BM.walk_letter("X_WALK.rws") == "a",
              "...an ArchBig save, no save and a bare name read ArchBig")
        check("instances/b/" in BM.walk_paths(B_SAVE)[0].replace("\\", "/"), "...and the Mods folder read is that game's own")
    with Patch(game_instance, root=lambda: (_ for _ in ()).throw(RuntimeError("no root"))):
        check(BM.walk_letter(B_SAVE) == "a", "...a machine with no instance root reads ArchBig")


def t_a_stale_walk_build_is_deployed_to_the_walk_game():
    calls, row = [], {"mod": "FlowWorks", "aut": "autodeploy", "steward_key": "k"}
    with Patch(M, walk_letter=lambda r, m: "b"):
        AUT.execute("/r", {}, {"mods": {"FlowWorks": {}}}, [row], ["FlowWorks"], 1.0, {
            "known": lambda: set(), "game_deploy": lambda mod, game, kind, purpose, seat="BENCH": (
                calls.append((mod, game, kind)) or (0, "STARTED", "rm-game-deploy-x"))})
    check(calls == [("FlowWorks", "b", "walk")] and row["decision"] == "live",
          "a-stale-walk-build-is-deployed-to-the-walk-game (%s)" % calls)


def t_his_hold_is_read_on_the_walk_game():
    asked = []
    with Patch(GL, query=lambda g, **k: asked.append(g) or {"code": GL.EX_HIS, "line": "HIS HOLD"}):
        got = AUT.walk_game("b")
    check(asked == ["b"] and got == "HIS HOLD", "his-hold-is-read-on-the-walk-game (%s)" % asked)


def t_a_visit_that_opened_before_the_ruling_keeps_its_save():
    walk = {"active_mods": ["a", "b"]}
    said = []
    with Patch(SL, list_faults=lambda r, m: [], walk_save_why=lambda r, m, mods: said.append(list(mods)) or "not on the small list"):
        for at, want in ((M.SMALL_LIST_FROM, True), ("2026-11-24T07:14:54-08:00", False)):
            with Patch(M, load=lambda r, m, at=at: {"moves": [{"to": "in_game", "at": at}]}):
                got = M.walk_small_list_why("/r", "M", 1, walk)
            check(bool(got) is want, "a-visit-that-opened-before-the-ruling-keeps-its-save: opened %s reads %s" % (at, got))
        with Patch(M, load=lambda r, m: {"moves": [{"to": "in_game", "at": M.SMALL_LIST_FROM}]}):
            check(M.walk_small_list_why("/r", "M", 1, dict(walk, standin="x")) is None
                  and M.walk_small_list_why("/r", "M", 1, None) is None, "...a stand-in and an absent reading are not judged")


def t_the_exit_reads_the_list_too():
    with Patch(SL, list_faults=lambda r, m: ["x.mod is needed"], walk_save_why=lambda r, m, mods: None), \
            Patch(M, load=lambda r, m: {"moves": [{"to": "in_game", "at": M.SMALL_LIST_FROM}]}):
        got = M.walk_small_list_why("/r", "M", 1, {"active_mods": ["a"]})
    check(got == "x.mod is needed", "the-exit-reads-the-list-too (%s)" % got)
    check(SL.list_faults("/nowhere", "M") == [], "...and a mod with no small list has no fault of it")


def t_an_opening_time_that_cannot_be_read_is_said():
    walk = {"active_mods": ["a", "b"]}
    with Patch(SL, list_faults=lambda r, m: [], walk_save_why=lambda r, m, mods: None):
        for at in (None, "yesterday"):
            with Patch(M, load=lambda r, m, at=at: {"moves": [{"to": "in_game", "at": at}]}):
                check("could not be read" in (M.walk_small_list_why("/r", "M", 1, walk) or ""),
                      "an-opening-time-that-cannot-be-read-is-said: %r" % at)


def t_a_list_that_cannot_be_read_is_said():
    walk = {"active_mods": ["a", "b"]}

    def boom(*a):
        raise SL.CouldNotLook("planted")
    with Patch(SL, list_faults=boom), Patch(M, load=lambda r, m: {"moves": [{"to": "in_game", "at": M.SMALL_LIST_FROM}]}):
        check("could not be read" in (M.walk_small_list_why("/r", "M", 1, walk) or ""), "a-list-that-cannot-be-read-is-said")


def main():
    for t in (t_a_patched_mod_absent_from_the_list_fails,
              t_a_mod_he_does_not_play_is_named_not_failed,
              t_one_of_a_findmod_group_is_enough,
              t_a_findmod_name_that_no_mod_has_fails,
              t_a_folded_mod_is_held_by_baroque_biomes,
              t_every_list_holds_all_five_expansions,
              t_every_list_holds_the_zoom_mod, t_every_list_holds_character_editor,
              t_a_mod_the_code_reaches_is_needed_when_declared,
              t_an_unreadable_patch_is_could_not_look,
              t_an_about_that_fails_once_is_read_again,
              t_could_not_look_exits_two,
              t_a_walk_save_on_the_small_list_passes,
              t_the_walk_game_holds_the_save,
              t_a_stale_walk_build_is_deployed_to_the_walk_game,
              t_his_hold_is_read_on_the_walk_game,
              t_a_visit_that_opened_before_the_ruling_keeps_its_save,
              t_the_exit_reads_the_list_too,
              t_an_opening_time_that_cannot_be_read_is_said,
              t_a_list_that_cannot_be_read_is_said):
        t()
    print("%d of %d checks failed" % (len(BAD), N[0]))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
