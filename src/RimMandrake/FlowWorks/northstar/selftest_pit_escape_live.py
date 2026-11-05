#!/usr/bin/env python3
"""Offline selftest of the pit ESCAPE row (pit_rescue_live.py --scene escape; PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN, the live row
for LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A6: a prisoner in a pit with a LOWERED ladder starts vanilla's escape and climbs out;
raised, he stays).

Two halves. (1) escape_verdict, the pure verdict, on hand-made phases: raised-stays + lowered-escapes PASS; a raised escape and
a lowered stay FAIL MOD (the row can fail both ways); a ladder not read back in the wanted state, a non-prisoner, a death or a
prisoner already out are UNMEASURED SITE; asleep through a quiet lowered phase is SITE, awake and quiet is MOD. (2) the driver
end to end against a fake bridge whose prisoner escapes exactly when the ladder is lowered (vanilla's rule as the design reads
it), and fault modes: a ladder that leaks when raised, a ladder that holds when lowered, a refused prisoner write, a ladder
that will not spawn. A mock verdict is evidence about the DRIVER only, never about the mod.
"""
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_pit_escape_live_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import pit_rescue_live as PRL  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="pit_escape_selftest_")
O = (30, 30)
PIT = {(O[0] + x, O[1] + z) for x in range(6, 9) for z in range(4, 7)}


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else str(detail)[:300]))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------------------ (1) the pure verdict
def ph(raised, in_pit=True, msgs=0, prisoner=True, dead=False, start=True, jobs=None, gone=False, present="True"):
    jobs = jobs or ["Wait_Wander"] * 4
    return {"ladder": {"present": present, "raised": str(raised)}, "prisoner": prisoner, "startInPit": start,
            "escapeMsgs": msgs, "may": {},
            "trail": [{"t": 250 * (i + 1), "inPit": in_pit if i == len(jobs) - 1 else True, "gone": gone and i == len(jobs) - 1,
                       "dead": dead, "job": j} for i, j in enumerate(jobs)]}


def verdict(r, l):
    return {rid: (st, cls) for rid, st, cls, _ in PRL.escape_verdict(r, l)}


S, E = PRL.ESCAPE_IDS
v = verdict(ph(True), ph(False, in_pit=False, msgs=1))
check("verdict: raised stays + lowered climbs out with the message -> both PASS", v == {S: ("PASS", "MOD"), E: ("PASS", "MOD")}, v)
v = verdict(ph(True), ph(False, gone=True, in_pit=False, msgs=1))
check("verdict: gone off the map counts as out", v[E] == ("PASS", "MOD"), v)
v = verdict(ph(True, in_pit=False, msgs=1), ph(False, in_pit=False, msgs=1))
check("verdict: out while raised -> FAIL MOD", v[S] == ("FAIL", "MOD"), v)
v = verdict(ph(True, msgs=1), ph(False, in_pit=False, msgs=1))
check("verdict: escape message while raised (even if held) -> FAIL MOD", v[S] == ("FAIL", "MOD"), v)
v = verdict(ph(True), ph(False))
check("verdict: lowered, no message, still in -> FAIL MOD", v[E] == ("FAIL", "MOD"), v)
v = verdict(ph(True), ph(False, in_pit=False))
check("verdict: out with neither the message nor the escape Goto -> FAIL MOD (not vanilla's escape)", v[E] == ("FAIL", "MOD"), v)
v = verdict(ph(True), dict(ph(False, in_pit=False), escapeJob=True))
check("verdict: out with the escape Goto sampled (message expired) -> PASS", v[E] == ("PASS", "MOD"), v)
v = verdict(dict(ph(True), escapeJob=True), ph(False, in_pit=False, msgs=1))
check("verdict: a lone Goto while raised (held, no message) is not an escape -> PASS", v[S] == ("PASS", "MOD"), v)
v = verdict(ph(True), ph(False, msgs=1))
check("verdict: message but never left the pit -> FAIL MOD", v[E] == ("FAIL", "MOD"), v)
v = verdict(ph(False), ph(True, in_pit=False, msgs=1))
check("verdict: ladder read back in the wrong state -> both UNMEASURED SITE",
      v == {S: ("UNMEASURED", "SITE"), E: ("UNMEASURED", "SITE")}, v)
v = verdict(ph(True, present="False"), ph(False, in_pit=False, msgs=1))
check("verdict: no ladder present -> UNMEASURED SITE", v[S] == ("UNMEASURED", "SITE"), v)
v = verdict(ph(True, prisoner=False), ph(False, prisoner=False, in_pit=False, msgs=1))
check("verdict: not a prisoner -> UNMEASURED SITE", v == {S: ("UNMEASURED", "SITE"), E: ("UNMEASURED", "SITE")}, v)
v = verdict(ph(True, dead=True), None)
check("verdict: dead prisoner -> SITE; phase never run -> HARNESS", v == {S: ("UNMEASURED", "SITE"), E: ("UNMEASURED", "HARNESS")}, v)
v = verdict(ph(True), ph(False, start=False, in_pit=False, msgs=1))
check("verdict: already out when the lowered phase began -> UNMEASURED SITE", v[E] == ("UNMEASURED", "SITE"), v)
v = verdict(ph(True), ph(False, jobs=["Wait_Wander", "LayDown", "LayDown", "LayDown"]))
check("verdict: asleep through a quiet lowered phase -> UNMEASURED SITE", v[E] == ("UNMEASURED", "SITE"), v)
v = verdict(ph(True), ph(False, jobs=["LayDown", "LayDown", "LayDown", "Wait_Wander"]))
check("verdict: awake at the end and still quiet -> FAIL MOD", v[E] == ("FAIL", "MOD"), v)
check("new_lines keeps repeats beyond their old count",
      PRL.new_lines(["a escaping", "b"], ["a escaping", "a escaping", "b"]) == ["a escaping"])
check("escape_lines finds nested message text",
      PRL.escape_lines({"messages": [{"text": "Bob is trying to escape!"}, {"text": "x"}]}) == ["Bob is trying to escape!"])


# ------------------------------------------------------------------ (2) the driver against a fake bridge
class FakeV:
    @staticmethod
    def _wait_playing(B, leave_s=0):
        return True, None

    @staticmethod
    def site_calm(B):
        return {"ok": True}

    @staticmethod
    def prepare_site(B, rect, rows, name):
        rows.append({"id": name, "status": "PASS"})


class FakeBridge:
    """A ladder with a raised flag, one prisoner on the pit floor, vanilla's escape: on the first think after the ladder lets
    him out he gets the message and climbs to the rim, then walks off the map."""

    def __init__(self, faults=()):
        self.faults = set(faults)
        self.ladder = None
        self.raised = False
        self.pawn = None
        self.messages = [{"text": "Old: Jo is trying to escape!"}]  # an older escape line: must not count
        self.escaping = 0
        self.calls = []

    def call(self, tool, **kw):
        self.calls.append(tool)
        return getattr(self, "t_" + tool.replace("/", "_"), lambda kw: {"success": True})(kw)

    def t_jawa_spawn_batch(self, kw):
        if "no_ladder" in self.faults:
            return {"success": True, "thingsPlaced": 0}
        d, c = kw["ops"].split(":")
        self.ladder = tuple(int(v) for v in c.split(","))
        return {"success": True, "thingsPlaced": 1}

    def t_jawa_spawn_pawn(self, kw):
        self.pawn = {"id": "Human7", "x": kw["x"], "z": kw["z"], "spawned": True, "dead": False}
        return {"success": True, "pawns": [{"id": "Human7"}]}

    def t_jawa_pawn_set_guest_status(self, kw):
        if "refuse_prisoner" in self.faults:
            return {"success": False, "guestStatusBefore": "None", "guestStatusAfter": "None", "hostFactionAfter": None}
        return {"success": True, "guestStatusBefore": "None", "guestStatusAfter": "Prisoner", "hostFactionAfter": "Colony"}

    def t_jawa_pawn_force_incapacitate(self, kw):
        if kw.get("action") == "vanish" and self.pawn:
            self.pawn = None
        return {"success": True}

    def t_jawa_static_call(self, kw):
        m, arg = kw["method"], kw["args"]
        if m == "ProofLadder":
            op = arg.split(",")[2]
            if self.ladder is None:
                return {"success": True, "result": "LADDER cell=%s present=False raised=None inspect=none" % arg}
            if op in ("raise", "lower"):
                self.raised = op == "raise"
            return {"success": True, "result": "LADDER cell=%d,%d present=True raised=%s want=%s" % (
                self.ladder + (self.raised, self.raised))}
        if m == "ProofLadderParity":
            for f in arg.split(":", 1)[1].split(","):
                if not f.strip().lstrip("-").isdigit():  # the C#: int.TryParse on every field
                    return {"success": True, "result": "REFUSED: bad number '%s'" % f}
            return {"success": True, "result": "ladder=RM_Ladder faction=none mayClimb=True letsOut=%s" % self.lets_out()}
        return {"success": True, "result": ""}

    def lets_out(self):
        if "leaks" in self.faults:
            return True
        if "holds" in self.faults:
            return False
        return not self.raised

    def t_rimworld_step_game_ticks(self, kw):
        p = self.pawn
        if not p or kw["ticks"] < 250:
            return {"success": True}
        if self.escaping:
            self.escaping += 1
            if self.escaping == 2:
                p["x"], p["z"] = O[0] + 4, O[1] + 5   # on the rim beside the ladder
            elif self.escaping >= 3:
                self.pawn = None                       # off the map edge
        elif self.lets_out():
            self.messages.append({"text": "%s is trying to escape!" % p["id"]})
            self.escaping = 1
        return {"success": True}

    def t_jawa_list_pawns(self, kw):
        return {"success": True, "pawns": [dict(self.pawn)] if self.pawn else []}

    def t_jawa_attack_target_probe(self, kw):
        return {"success": True, "curJob": "Goto" if self.escaping else "Wait_Wander"}

    def t_rimworld_list_messages(self, kw):
        return {"success": True, "messages": list(self.messages)}


def drive(faults=(), extra=()):
    out = os.path.join(TMP, "escape_%s.json" % ("_".join(sorted(faults)) or "ok"))
    B = FakeBridge(faults)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = PRL.main([out, "--scene", "escape", "--ticks", "3000", "--raised-ticks", "1500"] + list(extra), bridge=B,
                      validation=FakeV)
    res = json.load(open(out))
    return rc, {r["id"]: (r["status"], r["class"]) for r in res["rows"]}, res, B


rc, rows, res, B = drive()
check("driver: lowered escapes, raised holds -> both PASS, exit 0",
      rc == 0 and rows == {S: ("PASS", "MOD"), E: ("PASS", "MOD")}, (rc, rows))
check("driver: rows name this item", all(r["item"] == "PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN" for r in res["rows"]))
check("driver: the old escape line in the ring is not counted in the raised phase",
      res["phases"]["raised"]["escapeMsgs"] == 0, res["phases"]["raised"].get("escapeText"))
check("driver: may: read in each phase (letsOut False raised, True lowered)",
      res["phases"]["raised"]["may"].get("letsOut") == "False" and res["phases"]["lowered"]["may"].get("letsOut") == "True",
      (res["phases"]["raised"]["may"], res["phases"]["lowered"]["may"]))
check("driver: escape job seen while lowered, not while raised",
      res["phases"]["lowered"]["escapeJob"] and not res["phases"]["raised"]["escapeJob"])
check("driver: the lowered phase stops once he is out", len(res["phases"]["lowered"]["trail"]) < 12,
      len(res["phases"]["lowered"]["trail"]))
check("driver: the prisoner is vanished at the end", B.pawn is None)
rc, rows, _, _ = drive({"leaks"})
check("driver: a raised ladder that lets him out -> raised FAIL MOD, lowered UNMEASURED SITE (already out)",
      rc == 1 and rows[S] == ("FAIL", "MOD") and rows[E] == ("UNMEASURED", "SITE"), (rc, rows))
rc, rows, _, _ = drive({"holds"})
check("driver: a lowered ladder that holds him -> lowered FAIL MOD", rc == 1 and rows == {S: ("PASS", "MOD"), E: ("FAIL", "MOD")},
      (rc, rows))
rc, rows, _, _ = drive({"refuse_prisoner"})
check("driver: a refused prisoner write -> both UNMEASURED SITE",
      rc == 1 and rows == {S: ("UNMEASURED", "SITE"), E: ("UNMEASURED", "SITE")}, (rc, rows))
rc, rows, _, _ = drive({"no_ladder"})
check("driver: no ladder placed -> both UNMEASURED SITE, exit 2",
      rc == 2 and rows == {S: ("UNMEASURED", "SITE"), E: ("UNMEASURED", "SITE")}, (rc, rows))

print("OK" if not FAILS else "FAILED", len(FAILS), "fail")
sys.exit(1 if FAILS else 0)
