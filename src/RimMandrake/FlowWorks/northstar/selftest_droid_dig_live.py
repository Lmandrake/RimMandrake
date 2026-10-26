"""Offline mock of droid_dig_live.py (no bridge, no game): a fake bridge plays each scene and the rows must read right.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_droid_dig_live.py

Can-fails: the colonist cap leaking FAILs the control and voids the droid row; a droid not offered the job, or told it needs
a shovel, FAILs; Droidworks not running voids every row (HARNESS); an offered job with no cut is UNMEASURED/SITE, never PASS;
the run's settings are restored.
"""
import argparse
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import droid_dig_live as D  # noqa: E402
import work_bar  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="st_droid_dig_")


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class FakeV(object):
    @staticmethod
    def _wait_playing(B, leave_s=0):
        return True, None

    @staticmethod
    def site_calm(B):
        return {"ok": True}

    @staticmethod
    def prepare_site(B, plot, rows, rid):
        return True


class FakeB(object):
    """Scene knobs: colonist_offered, droid_offered, droid_needs, cut_after (ticks, None = never), running."""

    def __init__(self, colonist_offered=False, droid_offered=True, droid_needs="False", cut_after=1500,
                 running=(D.DROIDWORKS,), droid_spawns=True):
        self.k = dict(colonist_offered=colonist_offered, droid_offered=droid_offered, droid_needs=droid_needs,
                      cut_after=cut_after, droid_spawns=droid_spawns)
        self.running = list(running)
        self.settings = {k: "owner" for k in D.RUN_SETTINGS}
        self.depth, self.ticks, self.ordered_at, self.n, self.kinds = 0, 0, None, 0, {}

    def call(self, name, **kw):
        k = self.k
        if name == "jawa/companion_handshake":
            return {"effectiveProfile": "test"}
        if name == "jawa/running_mods":
            return {"packageIds": self.running}
        if name == "jawa/mod_settings_field":
            if kw["action"] == "set":
                self.settings[kw["field"]] = kw["value"]
                return {"success": True}
            return {"value": self.settings.get(kw["field"])}
        if name == "jawa/flowworks_excavation_drive":
            self.depth += kw.get("deepenLevels", 0)
            return {"success": True, "depth": self.depth}
        if name == "jawa/spawn_pawn":
            if kw["kindDef"] == D.DROID_KIND and not k["droid_spawns"]:
                return {"success": False}
            self.n += 1
            pid = "Thing_P%d" % self.n
            self.kinds[pid] = kw["kindDef"]
            return {"pawns": [{"id": pid}]}
        if name == "jawa/flowworks_job_probe":
            droid = self.kinds.get(kw["pawnId"]) == D.DROID_KIND
            offered = k["droid_offered"] if droid else k["colonist_offered"]
            return {"success": True, "workGiver": {"jobDef": D.JOB if offered else None},
                    "pawn": {"workTypeDisabled": False}}
        if name == "jawa/static_call":
            return {"success": True, "result": "has=False needs=%s ready=True" % k["droid_needs"]}
        if name == "jawa/ordered_job":
            self.ordered_at = self.ticks
            return {"success": True}
        if name == "rimworld/step_game_ticks":
            self.ticks += kw["ticks"]
            if self.ordered_at is not None and k["cut_after"] is not None and self.ticks - self.ordered_at >= k["cut_after"] \
                    and self.depth == D.CAP:
                self.depth += 1
            return {"success": True}
        if name == "jawa/list_pawns":
            return {"pawns": [{"id": "Thing_old", "isPlayer": True}]}
        return {"success": True}


def scene(name, **knobs):
    B = FakeB(**knobs)
    out = os.path.join(TMP, name + ".json")
    rc = D.run(B, FakeV, argparse.Namespace(origin="40,40", fresh_map=False), out)
    import json
    with open(out, encoding="utf-8") as f:
        res = json.load(f)
    return rc, {r["id"]: (r["status"], r["class"]) for r in res["rows"]}, res, B


def main():
    real = work_bar.set_all
    work_bar.set_all = lambda call, pid, spec: (True, "mock")
    try:
        rc, rows, res, B = scene("good")
        check(rc == 0 and rows == {"DD_colonist_held_at_2m": ("PASS", "MOD"), "DD_droid_digs_past_2m": ("PASS", "MOD")},
              "a held colonist and a droid cutting D4 -> D5 read PASS, PASS (rc %s, %s)" % (rc, rows))
        check(all(B.settings[k] == "owner" for k in D.RUN_SETTINGS), "the owner's settings are restored after the run")
        check(res["settings_run"]["maxDigDepth"] == "4" and res["settings_run"]["machineDigEnabled"] == "True",
              "the run reads back the 2 m colonist cap and machine digging on")

        rc, rows, _, _ = scene("leak", colonist_offered=True)
        check(rows.get("DD_colonist_held_at_2m") == ("FAIL", "MOD") and rows.get("DD_droid_digs_past_2m", ("",))[0] == "UNMEASURED",
              "a colonist offered the 2 m square FAILs and voids the droid row (%s)" % rows)
        rc, rows, _, _ = scene("refused", droid_offered=False)
        check(rows.get("DD_droid_digs_past_2m") == ("FAIL", "MOD") and rc == 1, "a droid not offered the job FAILs (%s)" % rows)
        rc, rows, _, _ = scene("shovel", droid_needs="True")
        check(rows.get("DD_droid_digs_past_2m") == ("FAIL", "MOD"), "a droid told it needs a shovel FAILs (%s)" % rows)
        rc, rows, _, _ = scene("nocut", cut_after=None)
        check(rows.get("DD_droid_digs_past_2m") == ("UNMEASURED", "SITE"), "offered but no cut is UNMEASURED/SITE (%s)" % rows)
        rc, rows, _, _ = scene("nodroid", droid_spawns=False)
        check(rows.get("DD_droid_digs_past_2m") == ("UNMEASURED", "SITE"), "a droid that will not spawn is SITE (%s)" % rows)
        rc, rows, _, B = scene("nodw", running=("mandrake.rm.flowworks",))
        check(rc == 2 and set(rows.values()) == {("UNMEASURED", "HARNESS")} and len(rows) == len(D.ROW_IDS),
              "Droidworks not running voids every row as HARNESS (%s)" % rows)
        check(B.n == 0, "with Droidworks absent nothing is spawned")
    finally:
        work_bar.set_all = real
        shutil.rmtree(TMP, True)
    print("%s: %d failing" % (os.path.basename(__file__), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
