#!/usr/bin/env python3
"""selftest_ikee_swap.py -- the ikee swap against a FAKE bridge (no game): order, assertions, and the stops."""
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ikee_swap as I  # noqa: E402

FAILS = []
N = [0]


def check(cond, what, extra=None):
    N[0] += 1
    print(("ok   " if cond else "FAIL ") + what + ("" if cond or extra is None else "  %s" % (extra,)))
    if not cond:
        FAILS.append(what)


class Fake(object):
    def __init__(self, saves, old_present=True, donor=False, extra_kill=False):
        self.saves, self.calls = saves, []
        self.old_present, self.donor, self.extra_kill = old_present, donor, extra_kill
        self.bond = I.OLD if old_present else None

    def call(self, tool, params):
        self.calls.append((tool, dict(params)))
        if tool == "rimworld/get_game_info":
            return {"success": True, "programState": "Playing"}
        if tool == "jawa/companion_handshake":
            return {"success": True, "profile": "test"}
        if tool == "jawa/running_mods":
            return {"success": True, "packageIds": ["ludeon.rimworld"] + (["sarg.alphabiomes"] if self.donor else [])}
        if tool == "jawa/pawn_get":
            pw = params["pawn"]
            if pw == I.YEKU:
                return {"success": True, "pawns": [{"id": I.YEKU, "name": "Yeku"}]}
            if pw == I.OLD:
                return {"success": True, "pawns": [{"id": I.OLD, "def": "AA_Eyeling",
                                                    "position": {"x": 175, "z": 134}}]} if self.old_present else \
                    {"success": False, "error": "no pawn"}
            return {"success": True, "pawns": [{"id": pw, "def": I.NEW_KIND, "name": I.NAME}]}
        if tool == "jawa/pawn_relations":
            if params["action"] == "remove":
                self.bond = None
                return {"success": True, "removed": 1}
            return {"success": True, "relations": [{"def": "Bond", "other": self.bond}] if self.bond else []}
        if tool == "jawa/kill_hostiles":
            ids = [{"id": I.OLD}] + ([{"id": "AA_Eyeling999"}] if self.extra_kill else [])
            return {"success": True, "killedPawns": ids, "dryRun": params.get("dryRun", False)}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "RSW_Ikee1"}]}
        if tool == "jawa/animal_bond":
            self.bond = params["animal"]
            return {"success": True, "bondedNow": True}
        if tool == "rimworld/save_game":
            open(os.path.join(self.saves, params["saveName"] + ".rws"), "w").write("<savegame>after</savegame>")
            return {"success": True}
        return {"success": True}


def run(fake, d):
    buf = io.StringIO()
    sw = I.Swap(True, fake, saves_dir=d, backups=os.path.join(d, "bak"), out=lambda s: buf.write(s + "\n"))
    try:
        sw.run()
        return "done", buf.getvalue()
    except I.Stop as exc:
        return "stop: %s" % exc, buf.getvalue()


def main():
    d = tempfile.mkdtemp()
    save = os.path.join(d, I.SAVE + ".rws")
    open(save, "w").write("<savegame>before</savegame>")

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = I.main([])
    out = buf.getvalue()
    check(code == 0 and "DRY RUN complete" in out and "--call jawa/spawn_pawn" in out,
          "the default is a dry run that prints every call", out[-300:])
    check("'{\"pawn\":\"Human470530\",\"animal\":\"<NEW_ID>\"" in out, "printed JSON is one single-quoted word "
                                                                        "(no shell splitting)")
    with redirect_stdout(io.StringIO()):
        check(I.main(["--live"]) == 2, "--live without --yes-i-know-this-is-live refuses")

    f = Fake(d)
    res, out = run(f, d)
    tools = [t for t, _ in f.calls]
    check(res == "done", "a healthy fake run completes", res + out[-400:])
    check(tools.index("jawa/pawn_relations") < tools.index("jawa/kill_hostiles") < tools.index("jawa/spawn_pawn"),
          "the old bond is dropped BEFORE the kill, the kill BEFORE the spawn", tools)
    check(("jawa/animal_bond", {"pawn": I.YEKU, "animal": "RSW_Ikee1", "chance": 1.0}) in f.calls,
          "the bond is made to the NEW pawn's id", f.calls)
    check(open(save).read() == "<savegame>after</savegame>" and os.listdir(os.path.join(d, "bak")),
          "the save was backed up first and then written")

    open(save, "w").write("<savegame>before</savegame>")
    f = Fake(d, old_present=False)
    res, out = run(f, d)
    check(res == "done" and not any(t == "jawa/kill_hostiles" for t, _ in f.calls),
          "if Scribe dropped the old ikee, no kill is attempted and the recorded cell is used", res)

    f = Fake(d, donor=True)
    res, out = run(f, d)
    check(res.startswith("stop") and not any(t == "jawa/spawn_pawn" for t, _ in f.calls),
          "BROKEN: a retired donor in the running list STOPS before anything changes", res)

    f = Fake(d, extra_kill=True)
    res, out = run(f, d)
    check(res.startswith("stop") and sum(1 for t, p in f.calls if t == "jawa/kill_hostiles") == 1,
          "BROKEN: a dry-run kill naming another pawn STOPS before the real kill", res)
    check(not any(t == "rimworld/save_game" for t, _ in f.calls), "a stopped run never saves")
    print("\n%d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
