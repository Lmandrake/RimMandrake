#!/usr/bin/env python3
"""deploy-update installs every drifted unit text, and only reloads systemd (RIMMANDRAKE_INSTALL_UNIT_TEXTS_ON_DEPLOY_NOT_BY_HAND).

The instance: unit texts changed in src/RimMandrake/Utils/systemd reached ~/.config/systemd/user only by a hand
`ops_clocks.py install`, so LIVE_RESTORE_UNITS broke 3 times 2026-11-23..24. Now each rm-deploy-update pass, after a
good pull, writes every folder file whose installed copy differs and runs one daemon-reload. It never enables, starts or
restarts a unit (a unit may launch Claude), and never writes over a mask.

Fixtures only: temp folders stand for the folder and the install dir, and a fake systemctl records calls.
"""
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import deploy_update as DU  # noqa: E402

FAILS = []
TIMER = "[Unit]\nDescription=x\n\n[Timer]\nOnCalendar=hourly\n"
SERVICE = "[Unit]\nDescription=x\n\n[Service]\nType=oneshot\nExecStart=/bin/true\n"


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(name)


class R:
    def __init__(self, rc=0, err=""):
        self.returncode, self.stderr, self.stdout = rc, err, ""


class FakeSC:
    def __init__(self, rc=0):
        self.calls, self.rc = [], rc

    def __call__(self, *a):
        self.calls.append(a)
        return R(self.rc, "boom" if self.rc else "")


def tree(files, masks=()):
    d = Path(tempfile.mkdtemp(prefix="du_units_"))
    for n, t in files.items():
        (d / n).parent.mkdir(parents=True, exist_ok=True)
        (d / n).write_text(t, encoding="utf-8")
    for n in masks:
        os.symlink("/dev/null", d / n)
    return d


def t_the_deploy_holds_the_unit_folder():
    check("the sparse deploy checkout holds src/RimMandrake/Utils/systemd",
          "src/RimMandrake/Utils/systemd" in DU.SPARSE_DIRS, DU.SPARSE_DIRS)


def t_a_drifted_text_is_installed_with_one_reload_and_no_start():
    folder = tree({"rm-x.timer": TIMER, "rm-x.service": SERVICE, "rm-x.service.d/a.conf": "[Service]\nNice=5\n"})
    dest = tree({"rm-x.timer": TIMER.replace("hourly", "daily"), "rm-x.service": SERVICE})
    sc = FakeSC()
    r = DU.install_units(folder_dir=folder, dest=dest, sc=sc)
    check("a drifted timer is written", (dest / "rm-x.timer").read_text() == TIMER)
    check("a drop-in missing from the install dir is written", (dest / "rm-x.service.d/a.conf").is_file())
    check("the result names exactly the written files",
          sorted(r["wrote"]) == ["rm-x.service.d/a.conf", "rm-x.timer"], r)
    check("the only systemctl call is one daemon-reload (never enable, start or restart)",
          sc.calls == [("daemon-reload",)], sc.calls)


def t_no_drift_touches_nothing():
    folder = tree({"rm-x.timer": TIMER})
    dest = tree({"rm-x.timer": TIMER})
    sc = FakeSC()
    r = DU.install_units(folder_dir=folder, dest=dest, sc=sc)
    check("no drift: nothing written and systemctl never called", r["wrote"] == [] and sc.calls == [], (r, sc.calls))


def t_a_mask_is_skipped_and_the_rest_still_installs():
    folder = tree({"rm-dead.timer": TIMER, "rm-x.timer": TIMER})
    dest = tree({}, masks=("rm-dead.timer",))
    sc = FakeSC()
    r = DU.install_units(folder_dir=folder, dest=dest, sc=sc)
    check("a masked name stays a mask", (dest / "rm-dead.timer").is_symlink()
          and os.path.realpath(dest / "rm-dead.timer") == "/dev/null")
    check("the masked name is reported, the other unit is written",
          r["masked"] == ["rm-dead.timer"] and r["wrote"] == ["rm-x.timer"], r)
    check("one daemon-reload only", sc.calls == [("daemon-reload",)], sc.calls)


def t_a_missing_folder_or_failed_reload_fails_loudly():
    try:
        DU.install_units(folder_dir=Path(tempfile.mkdtemp()) / "gone", dest=tree({}), sc=FakeSC())
        check("a missing unit folder raises", False, "no raise")
    except RuntimeError as e:
        check("a missing unit folder raises, naming it", "gone" in str(e), e)
    try:
        DU.install_units(folder_dir=tree({"rm-x.timer": TIMER}), dest=tree({}), sc=FakeSC(rc=1))
        check("a failed daemon-reload raises", False, "no raise")
    except RuntimeError as e:
        check("a failed daemon-reload raises", "daemon-reload" in str(e), e)


def t_main_installs_after_a_good_pull_and_not_after_a_skip():
    calls = []
    real_up, real_in = DU.update_code, DU.install_units
    try:
        DU.install_units = lambda **k: calls.append("install") or {"wrote": ["rm-x.timer"], "masked": []}
        DU.update_code = lambda: calls.append("update") or {"old": "a", "new": "b", "changed": True}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = DU.main(["update"])
        check("a good pass pulls, then installs", rc == 0 and calls == ["update", "install"], calls)
        check("the pass prints what it installed", "units: wrote 1 (rm-x.timer)" in buf.getvalue(), buf.getvalue())
        calls.clear()
        DU.update_code = lambda: calls.append("update") or {"skipped": True, "age": 5.0}
        with redirect_stdout(io.StringIO()):
            DU.main(["update"])
        check("a skipped pass (git timed out) installs nothing", calls == ["update"], calls)
    finally:
        DU.update_code, DU.install_units = real_up, real_in


def main():
    t_the_deploy_holds_the_unit_folder()
    t_a_drifted_text_is_installed_with_one_reload_and_no_start()
    t_no_drift_touches_nothing()
    t_a_mask_is_skipped_and_the_rest_still_installs()
    t_a_missing_folder_or_failed_reload_fails_loudly()
    t_main_installs_after_a_good_pull_and_not_after_a_skip()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
