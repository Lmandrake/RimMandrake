#!/usr/bin/env python3
"""selftest_units_one_folder.py - the promises of design/specs/2026-11-22-units-one-folder/boundary.md, one test each.

Fixtures only: temp folders stand for the one home and the install dir, and a fake systemctl records calls. Nothing
here reads or writes ~/.config/systemd/user or calls systemctl.

    python3 src/RimMandrake/Utils/selftest_units_one_folder.py
"""
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
os.environ.pop("RM_OPS_DEPLOY", None)
import ops_clocks as OC  # noqa: E402

FAILS = []
TIMER = "[Unit]\nDescription=x every 15 min\n\n[Timer]\nOnCalendar=*:03/15\nPersistent=true\n"
SERVICE = "[Unit]\nDescription=x\n\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 /d/src/RimMandrake/Utils/x.py\n"
DROPIN = "[Service]\nEnvironment=RM_DATA_ROOT=/mnt/d/x\n"


def check(cond, msg, detail=""):
    print(("ok    " if cond else "FAIL  ") + msg + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(msg)


def tree(files):
    """{relative name: text | "MASK"} -> a temp dir holding them (MASK: a symlink to /dev/null)."""
    d = Path(tempfile.mkdtemp(prefix="units_"))
    for n, t in files.items():
        p = d / n
        p.parent.mkdir(parents=True, exist_ok=True)
        if t == "MASK":
            p.symlink_to("/dev/null")
        else:
            p.write_text(t, encoding="utf-8")
    return d


def verdict(folder, inst):
    return OC.judge_units(OC.folder_units(tree(folder)), OC.installed_units(tree(inst)))


def same():
    return {"rm-x.service": SERVICE, "rm-x.timer": TIMER, "rm-x.service.d/root.conf": DROPIN}


def t_a_unit_installed_only_here_is_named():
    inst = dict(same(), **{"timer-guard.timer": TIMER, "rm-y.service.d/w.conf": DROPIN})
    v = verdict(same(), inst)
    check(len(v) == 2 and all("installed only on this machine" in p for p in v)
          and any(p.startswith("timer-guard.timer") for p in v) and any(p.startswith("rm-y.service.d/w.conf") for p in v),
          "a unit and a drop-in installed only here are each named", v)
    check(verdict(same(), same()) == [], "the folder equal to the install dir reads clean", verdict(same(), same()))
    check(verdict(same(), dict(same(), **{"hestia.service": SERVICE})) == [], "another project's unit is not judged")


def t_an_installed_text_that_differs_is_named():
    moved = dict(same(), **{"rm-x.timer": TIMER.replace("*:03/15", "*:04/15")})
    v = verdict(moved, same())
    check(len(v) == 1 and v[0].startswith("rm-x.timer: installed text differs")
          and "ops_clocks.py install rm-x.timer --apply" in v[0], "a changed OnCalendar in the folder reads red", v)
    v = verdict(same(), dict(same(), **{"rm-x.service.d/root.conf": DROPIN + "\n"}))
    check(len(v) == 1 and "differs" in v[0], "a drop-in that differs by one byte reads red", v)


def t_a_folder_unit_not_installed_is_named():
    v = verdict(dict(same(), **{"rm-z.timer": TIMER}), same())
    check(len(v) == 1 and v[0].startswith("rm-z.timer: in the folder, not installed"), "a folder unit not installed", v)


def t_a_mask_is_not_a_definition():
    check(verdict(same(), dict(same(), **{"rm-relentless.timer": "MASK"})) == [], "a masked retired unit is not judged")
    v = verdict(dict(same(), **{"rm-relentless.timer": TIMER}), dict(same(), **{"rm-relentless.timer": "MASK"}))
    check(len(v) == 1 and "masked here" in v[0], "a folder copy of a masked unit is dead and named", v)


def t_embedded_unit_text_in_code_is_red():
    src = 'X = 1\nUNIT = """[Unit]\nDescription=y\n\n[Service]\nExecStart=/bin/true\n"""\n'
    check(OC.embedded_units(src) == [2], "a module string with a [Service] section is found at its line",
          OC.embedded_units(src))
    check(OC.embedded_units('T = "[Timer]\\nOnCalendar=daily\\n"\n') == [1], "a one-line [Timer] string is found")
    check(OC.embedded_units('D = "[Unit]\\nConditionPathExists=/p\\n"\n') == [], "a [Unit]-only drop-in text is not a unit")
    check(OC.embedded_units('# [Service]\nx = 1\n') == [], "a comment naming a section is not unit text")
    check(OC.embedded_units('s = "see the [Service] section"\n') == [], "a section name inside prose is not unit text")
    root = tree({"src/RimMandrake/Utils/inst.py": src, "src/RimMandrake/Utils/selftest_inst.py": src,
                 "src/RimMandrake/Utils/tests/fixture.py": src, "src/RimMandrake/Utils/clean.py": "x = 1\n"})
    v = OC.embedded_in_tree(root / "src/RimMandrake")
    check(len(v) == 1 and v[0].startswith("src/RimMandrake/Utils/inst.py:2:"), "only the non-test source is named", v)
    v = OC.embedded_in_tree(HERE.parent)
    check(v == [], "no source of this tree holds unit text", v)


def t_an_unreadable_install_dir_is_could_not_look():
    gone = Path(tempfile.mkdtemp(prefix="units_")) / "absent"
    inst = OC.installed_units(gone)
    v = OC.judge_units(OC.folder_units(tree(same())), inst, str(gone))
    check(inst is None and len(v) == 1 and "could not read" in v[0], "a missing install dir is one could-not-look", v)


class FakeSC:
    def __init__(self, rc=0):
        self.calls, self.rc = [], rc

    def __call__(self, *argv):
        self.calls.append(list(argv))
        return types.SimpleNamespace(returncode=self.rc, stderr="")


def t_install_writes_only_what_differs_and_never_over_a_mask():
    folder = tree(dict(same(), **{"rm-x.timer": TIMER.replace("03/15", "05/15"), "rm-dead.timer": TIMER}))
    dest = tree(dict(same(), **{"rm-dead.timer": "MASK"}))
    out, sc = [], FakeSC()
    check(OC.install(["rm-x"], apply=False, folder_dir=folder, dest=dest, sc=sc, out=out.append) == 0
          and sc.calls == [] and (dest / "rm-x.timer").read_text() == TIMER, "a plan writes nothing and calls nothing", out)
    check(any(l.startswith("would write") and l.endswith("rm-x.timer") for l in out)
          and any(l.startswith("unchanged") and l.endswith("rm-x.service") for l in out),
          "the plan says which file it would write and which is unchanged", out)
    out, sc = [], FakeSC()
    rc = OC.install(["rm-x"], apply=True, folder_dir=folder, dest=dest, sc=sc, out=out.append)
    check(rc == 0 and "05/15" in (dest / "rm-x.timer").read_text() and sc.calls == [["daemon-reload"]],
          "apply writes the file that differs and reloads once, enabling nothing", (rc, sc.calls))
    out, sc = [], FakeSC()
    rc = OC.install(["rm-x"], apply=True, enable=True, folder_dir=folder, dest=dest, sc=sc, out=out.append)
    check(rc == 0 and sc.calls == [["enable", "--now", "rm-x.timer"]],
          "nothing differs: no reload; --enable starts only the named timer", sc.calls)
    out, sc = [], FakeSC()
    rc = OC.install(["rm-dead"], apply=True, folder_dir=folder, dest=dest, sc=sc, out=out.append)
    check(rc == 2 and (dest / "rm-dead.timer").is_symlink() and sc.calls == [], "a masked name is refused, untouched", out)
    try:
        OC.install(["rm-nope"], folder_dir=folder, dest=dest, sc=FakeSC(), out=out.append)
        check(False, "a name not in the folder is refused")
    except SystemExit as e:
        check("not in" in str(e), "a name not in the folder is refused", e)
    rc = OC.install(["rm-x.timer"], apply=True, folder_dir=tree({"rm-x.timer": TIMER + "#\n"}), dest=dest,
                    sc=FakeSC(rc=1), out=out.append)
    check(rc == 1, "a failed daemon-reload fails the install")


def t_every_folder_clock_runs_from_the_deploy():
    conf = OC.load_conf()
    dep = conf["deploy"]
    folder = OC.folder_units()
    for name in sorted(conf["clocks"]):
        text = folder.get(name + ".service")
        drops = "".join(folder[k] for k in sorted(folder) if k.startswith(name + ".service.d/"))
        check(text is not None and OC.judge(text + drops, dep) == [],
              "the folder %s.service runs from the deploy" % name, text and OC.judge(text + drops, dep))
    check(OC.judge(SERVICE.replace("/d/", "/home/mandrake/rm/bench/"), "/d") != [],
          "a folder service that runs from a seat clone reads red")


def t_test_throwaway_units_are_not_judged():
    inst = dict(same(), **{"testq-selftestthrow-123.timer": TIMER, "rm-probe-r1-.service.d/50-p.conf": DROPIN})
    check(verdict(same(), inst) == [], "a selftest's throwaway unit and drop-in are not judged", verdict(same(), inst))


def t_deadman_rechecks_units_every_pass():
    import deadman_check as DM
    d = Path(tempfile.mkdtemp(prefix="units_"))
    os.environ["RM_OPS_WATCH_DIR"] = str(d)
    import json
    r = DM.units_arm(lambda: [])
    check(r == {"units": None} and json.loads((d / "units.json").read_text())["status"] == "ok",
          "a clean pass: no fault, reading ok", r)
    r = DM.units_arm(lambda: ["rm-x.timer: installed text differs from the folder"])
    rd = json.loads((d / "units.json").read_text())
    check(r["units"] and "rm-x.timer" in r["units"] and rd["status"] == "alarm" and rd["problems"],
          "a problem is a broken arm, and the reading says alarm", (r, rd))

    def boom():
        raise OSError("disk gone")
    r = DM.units_arm(boom)
    check(r["units"] and "could not look" in r["units"], "a measurer that fails is a broken arm, never clean", r)
    rows = [x for x in DM.sweep(0, None, {}, [], r, checker=lambda *a: (True, ""), sees=True)["broken"]
            if x["item"] == "LIVE_RESTORE_UNITS"]
    check(len(rows) == 1, "the broken arm is the one fixed item LIVE_RESTORE_UNITS", rows)
    src = (HERE / "deadman_check.py").read_text(encoding="utf-8")
    check("arms.update(units_arm())" in src, "every `run` pass calls the arm")


def main():
    t_a_unit_installed_only_here_is_named()
    t_an_installed_text_that_differs_is_named()
    t_a_folder_unit_not_installed_is_named()
    t_a_mask_is_not_a_definition()
    t_embedded_unit_text_in_code_is_red()
    t_an_unreadable_install_dir_is_could_not_look()
    t_install_writes_only_what_differs_and_never_over_a_mask()
    t_every_folder_clock_runs_from_the_deploy()
    t_test_throwaway_units_are_not_judged()
    t_deadman_rechecks_units_every_pass()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
