#!/usr/bin/env python3
"""selftest_walk_stage.py - the pure parts of walk_stage.py (the one-call walk stager), no game, no bridge.

Promises: design/specs/2026-11-26-one-call-walk-stage/boundary.md. Each test is named for its promise.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_stage as W  # noqa: E402

FAILS = []
LIST = ["brrainz.harmony", "ludeon.rimworld", "brrainz.rimbridgeserver", "ray1203.simplecamerasetting",
        "void.charactereditor", "mandrake.rm.gimmesomeslack"]


def check(name, ok, detail=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, (": " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def raises_stop(fn, *a, **k):
    try:
        fn(*a, **k)
    except W.Stop as e:
        return e
    return None


def save(d, name, mods):
    os.makedirs(os.path.join(d, "Saves"), exist_ok=True)
    with open(os.path.join(d, "Saves", name + ".rws"), "w", encoding="utf-8") as f:
        f.write("<?xml version=\"1.0\"?>\n<savegame><meta><gameVersion>1.6</gameVersion><modIds>%s</modIds></meta>"
                "<game/></savegame>" % "".join("<li>%s</li>" % m for m in mods))


def t_a_missing_mod_is_named():
    spec = {"tier": "t", "requires": ["ludeon.rimworld"]}
    want, bad = W.list_verdict(spec, LIST, ["mandrake.rm.gone"], [])
    check("missing_mod_is_named", not want and any("mandrake.rm.gone" in b for b in bad), str(bad))
    spec = {"tier": "t", "requires": ["mandrake.rm.planted"], "also": {"some.other": "C# reaches it"}}
    want, bad = W.list_verdict(spec, LIST, [], [])
    check("named_mod_off_the_list_is_named", not want and any("mandrake.rm.planted" in b for b in bad)
          and any("some.other" in b for b in bad), str(bad))
    want, bad = W.list_verdict({"tier": "t", "requires": ["Ludeon.RimWorld"]}, LIST, [], [])
    check("clean_list_passes", want == LIST and not bad, str(bad))
    want, bad = W.list_verdict({"tier": "t"}, LIST, [], ["tier t is refused: x"])
    check("tier_refusal_stops", not want and bad == ["tier t is refused: x"], str(bad))


def t_the_save_is_loaded_only_on_the_list():
    d = tempfile.mkdtemp()
    try:
        S = os.path.join(d, "Saves")
        check("absent_save_rebuilds", W.save_decision(LIST, S, "WALK")[0] == "rebuild")
        save(d, "WALK", LIST)
        check("save_on_the_list_loads", W.save_decision(LIST, S, "WALK")[:2] == ("load", "WALK"))
        check("rebuild_asked_rebuilds", W.save_decision(LIST, S, "WALK", rebuild=True)[0] == "rebuild")
        save(d, "WALK", [m for m in LIST if m != "void.charactereditor"])
        a, n, why = W.save_decision(LIST, S, "WALK")
        check("save_lacking_only_harness_loads_and_resaves", (a, n) == ("load_resave", "WALK"), why)
        save(d, "WALK", [m for m in LIST if m != "mandrake.rm.gimmesomeslack"])
        a, n, why = W.save_decision(LIST, S, "WALK")
        check("save_lacking_the_mod_rebuilds", a == "rebuild" and "mandrake.rm.gimmesomeslack" in why, why)
        save(d, "WALK", LIST + ["other.mod"])
        a, n, why = W.save_decision(LIST, S, "WALK")
        check("save_with_an_extra_mod_rebuilds", a == "rebuild" and "other.mod" in why, why)
        save(d, "WALK_SMALL", LIST)
        check("resaved_copy_is_loaded_first", W.save_decision(LIST, S, "WALK")[:2] == ("load", "WALK_SMALL"))
        with open(os.path.join(S, "BROKEN.rws"), "w") as f:
            f.write("not a save")
        check("unreadable_header_rebuilds", W.save_decision(LIST, S, "BROKEN")[0] == "rebuild")
    finally:
        shutil.rmtree(d)


def t_a_game_on_the_list_is_reused():
    check("down_game_launches", W.restart_why(LIST, None, False) == "the game is down")
    check("new_deploy_restarts", "deploy" in (W.restart_why(LIST, LIST, True) or ""))
    check("other_list_restarts", "lacks void.charactereditor" in (W.restart_why(LIST, LIST[:-2] + LIST[-1:], False) or ""))
    check("same_list_reuses", W.restart_why(LIST, list(reversed(LIST)), False) is None)


def t_a_bad_config_is_refused_by_name():
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "walk_stage.json")
        e = raises_stop(W.load_config, "M", p)
        check("absent_config_stops", e is not None and e.code == W.EX_FAULT and "walk_stage.json" in e.why)
        with open(p, "w") as f:
            f.write("{not json")
        e = raises_stop(W.load_config, "M", p)
        check("unreadable_config_could_not_look", e is not None and e.code == W.EX_BLIND)
        good = {"save": "S", "stations": [{"name": "a", "rect": [1, 2, 3, 4]}],
                "rebuild": {"steps": [{"run": "x.py", "args": []}, {"ticks": 10}], "save_as": "R"}}
        json.dump(good, open(p, "w"))
        check("good_config_loads", raises_stop(W.load_config, "M", p) is None)
        for name, bad in (("no_save", dict(good, save="")),
                          ("bad_rect", dict(good, stations=[{"name": "a", "rect": [1, 2, 0, 4]}])),
                          ("dup_station", dict(good, stations=[{"name": "a", "rect": [1, 2, 3, 4]}] * 2)),
                          ("bad_step", dict(good, rebuild={"steps": [{"go": 1}], "save_as": "R"}))):
            json.dump(bad, open(p, "w"))
            e = raises_stop(W.load_config, "M", p)
            check("config_refuses_" + name, e is not None and e.code == W.EX_FAULT, str(e))
        real = W.load_config("GimmeSomeSlack")
        check("gss_config_has_38_stations", len(real["stations"]) == 38, str(len(real["stations"])))
        for s in real["rebuild"]["steps"]:
            if "run" in s:
                check("gss_rebuild_script_exists_" + os.path.basename(s["run"]), os.path.isfile(os.path.join(W.REPO, s["run"])))
    finally:
        shutil.rmtree(d)


def t_a_logged_exception_is_found():
    log = ("Mono path[0] = ...\n[JawaBench] first-exception tap armed (JawaBenchFirstException)\n"
           "Could not find def X\nNullReferenceException: Object reference not set\n  at Verse.Foo ()\n"
           "Exception in Verse.Bar: boom\n")
    check("first_log_exception_found", (W.first_log_exception(log) or "").startswith("NullReferenceException:"),
          str(W.first_log_exception(log)))
    check("clean_log_has_none", W.first_log_exception("Mono path\n[JawaBench] first-exception tap armed\n") is None)


def t_a_save_comes_with_its_labels():
    d = tempfile.mkdtemp()
    try:
        here, other = os.path.join(d, "b"), os.path.join(d, "a")
        save(other, "WALK", LIST)
        os.makedirs(os.path.join(other, "JawaBenchReviewSigns"))
        open(os.path.join(other, "JawaBenchReviewSigns", "WALK.txt"), "w").write("# map 0\n1|2|label\n")
        got = W.bring_save(["WALK_SMALL", "WALK"], here, [other])
        check("save_and_labels_copied_from_other_game",
              len(got) == 2 and os.path.exists(os.path.join(here, "Saves", "WALK.rws"))
              and os.path.exists(os.path.join(here, "JawaBenchReviewSigns", "WALK.txt")), str(got))
        save(here, "WALK", LIST[:1])
        check("save_here_never_overwritten", W.bring_save(["WALK"], here, [other]) == []
              and W.save_mods(os.path.join(here, "Saves", "WALK.rws")) == LIST[:1])
    finally:
        shutil.rmtree(d)


def t_the_model_watch_can_see():
    d = tempfile.mkdtemp()
    try:
        fake = os.path.join(d, "claude")
        os.symlink(sys.executable, fake)
        probe = os.path.join(d, "spawn.py")
        open(probe, "w").write("import subprocess,sys\nsubprocess.run([%r, '-c', 'import time; time.sleep(1.5)'], timeout=30)\n" % fake)
        rc, _, seen = W._watched([sys.executable, probe], os.path.join(d, "a.log"))
        check("model_watch_sees_a_claude_child", rc == 0 and len(seen) == 1, str(seen))
        open(probe, "w").write("import time\ntime.sleep(1)\n")
        rc, _, seen = W._watched([sys.executable, probe], os.path.join(d, "b.log"))
        check("model_watch_quiet_without_one", rc == 0 and seen == [], str(seen))
    finally:
        shutil.rmtree(d)


def t_no_step_names_a_model_door():
    src = open(os.path.join(HERE, "walk_stage.py"), encoding="utf-8").read()
    body = src.split('ACCEPT = "walk_stage_accept.json"')[0]
    bad = [w for w in ("anthropic", "gpt_consult", "role_launch", "detached_helper", "claude -p", '"claude"', "'claude'")
           if w in body]
    check("stager_names_no_model_door", not bad, str(bad))


def t_the_acceptance_verdict_needs_every_row():
    cfg = {"stations": [{"name": "a", "rect": [1, 1, 1, 1]}, {"name": "b", "rect": [1, 1, 1, 1]}]}
    good = {"planted": {"exit": 1, "names_mod": True, "model_processes": []},
            "real": {"exit": 0, "last": "READY M on ArchSmall: ...", "model_processes": []},
            "read": {"save": "S", "programState": "Playing", "paused": True, "hostiles": 0},
            "captures": {"a": "x.png", "b": "y.png"}}
    check("verdict_pass", W.verdict(good, cfg)["result"] == "PASS")
    for name, bad in (("planted_exit_0", dict(good, planted=dict(good["planted"], exit=0))),
                      ("planted_unnamed", dict(good, planted=dict(good["planted"], names_mod=False))),
                      ("real_not_ready", dict(good, real=dict(good["real"], exit=1, last="NOT READY"))),
                      ("not_paused", dict(good, read=dict(good["read"], paused=False))),
                      ("hostile_left", dict(good, read=dict(good["read"], hostiles=1))),
                      ("hostiles_unread", dict(good, read=dict(good["read"], hostiles=None))),
                      ("capture_missing", dict(good, captures={"a": "x.png", "b": None})),
                      ("model_ran", dict(good, real=dict(good["real"], model_processes=[(1, "claude")])))):
        check("verdict_fails_" + name, W.verdict(bad, cfg)["result"] == "FAIL")


def t_an_unknown_game_is_refused_by_name():
    p = subprocess.run([sys.executable, os.path.join(HERE, "walk_stage.py"), "GimmeSomeSlack", "--game", "NoSuchGame"],
                       capture_output=True, text=True, timeout=120)  # budget: danger=a hung import; measured need 1 s
    check("unknown_game_refused_by_name", p.returncode == W.EX_FAULT and "NoSuchGame" in p.stdout, p.stdout + p.stderr)


def main():
    for t in (t_a_missing_mod_is_named, t_the_save_is_loaded_only_on_the_list, t_a_game_on_the_list_is_reused,
              t_a_bad_config_is_refused_by_name, t_a_logged_exception_is_found, t_a_save_comes_with_its_labels,
              t_the_model_watch_can_see, t_no_step_names_a_model_door, t_the_acceptance_verdict_needs_every_row,
              t_an_unknown_game_is_refused_by_name):
        t()
    print("selftest_walk_stage: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
