"""Offline selftest for deepfire_log_check.py against a model of Verse.LogMessageQueue (decompiled rw16:
1000 entries, oldest dropped, newest combines identical messages up to 99 repeats) and of jawa/health's
log block. Every blind case must ABORT (SystemExit), every real new mod error must be reported, and an
old error must not be (BRIDGE_PROOFS_W50_LOG_CHECK_ROLLOVER_AND_REPEAT_CAP)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deepfire_log_check as dlc  # noqa: E402


class FakeGame:
    def __init__(self):
        self.q = []            # [type, text, repeats]
        self.count = 0         # Verse.Log.messageCount
        self.resets = 0
        self.state = "emitting"
        self.headroom_ok = True
        self.drain_broken = None

    def log(self, typ, text, times=1):
        for _ in range(times):
            if self.q and self.q[-1][0] == typ and self.q[-1][1] == text:
                if self.q[-1][2] >= 99:
                    continue                      # repeatsCapped: not counted, not posted
                self.q[-1][2] += 1
            else:
                self.q.append([typ, text, 1])
                if len(self.q) > dlc.MAXQ:
                    self.q.pop(0)
            self.count += 1

    def clear(self):
        self.q = []
        self.count = 0

    def __call__(self, tool, **a):
        if tool == "jawa/drain_log":
            if self.drain_broken is not None:
                return self.drain_broken
            assert a.get("errorsOnly") is False and a.get("limit", 0) >= dlc.MAXQ
            rows = [{"type": t, "text": x, "repeats": r} for t, x, r in self.q]
            return {"success": True, "totalInBuffer": len(self.q), "messages": rows[-a["limit"]:]}
        if tool == "jawa/health":
            hr = ("%d messages before the Verse.Log cap" % (dlc.VERSE_CAP - self.count)) if self.headroom_ok \
                else "unavailable: Verse.Log messageCount unreadable"
            return {"success": True, "log": {"state": self.state, "text": self.state, "headroom": hr,
                                             "capResets": self.resets}}
        raise AssertionError(tool)


FAILS = []


def case(name, setup, during, expect):
    """expect: 'blind', or a set of texts that must be reported."""
    g = FakeGame()
    setup(g)
    try:
        base = dlc.baseline(g)
        during(g)
        got = set(dlc.new_mod_errors(g, base))
        verdict = got
    except SystemExit as e:
        verdict = "blind"
        got = str(e)[:140]
    ok = verdict == expect
    print("%s  %-44s -> %s" % ("ok  " if ok else "FAIL", name, got if verdict != "blind" else "blind: " + got))
    if not ok:
        FAILS.append(name)


E1 = "Exception in Deepfire.CompGlow tick"
E2 = "Deepfire: missing def LuminousPigment_X"


def nothing(g):
    pass


def old_error(g):
    g.log("Error", E1)
    g.log("Message", "noise")


def full_with_old_error_oldest(g):
    g.log("Error", E1)
    for i in range(dlc.MAXQ - 1):
        g.log("Message", "m%d" % i)


case("clean: no errors at all", nothing, lambda g: g.log("Message", "[Deepfire] {}"), set())
case("old error not reported", old_error, lambda g: g.log("Message", "x"), set())
case("new error reported", old_error, lambda g: g.log("Error", E2), {E2})
case("repeat of old error (new entry) reported", old_error, lambda g: g.log("Error", E1), {E1})
case("repeat combining into newest entry reported", lambda g: g.log("Error", E1), lambda g: g.log("Error", E1), {E1})
case("warning naming mod not counted", nothing, lambda g: g.log("Warning", E1), set())
case("unrelated error not counted", nothing, lambda g: g.log("Error", "Other mod broke"), set())

# rollover: oldest baseline error dropped and the same text logged again -> the old count check saw equal counts
case("rollover equal loss/gain: repeat reported", full_with_old_error_oldest,
     lambda g: (g.log("Error", E1)), {E1})
case("rollover drops old error, nothing new", full_with_old_error_oldest,
     lambda g: g.log("Message", "y"), set())
case("more than a buffer logged -> blind", nothing,
     lambda g: (g.log("Error", E2), [g.log("Message", "z%d" % i) for i in range(dlc.MAXQ + 5)]), "blind")
case("Log.Clear then regrow -> blind", old_error,
     lambda g: (g.log("Error", E2), g.clear(), [g.log("Message", "w%d" % i) for i in range(5)]), "blind")
case("Log.Clear, count fell -> blind", lambda g: [g.log("Message", "a%d" % i) for i in range(50)],
     lambda g: (g.log("Error", E2), g.clear()), "blind")
case("capResets moved -> blind", nothing, lambda g: setattr(g, "resets", 1), "blind")
case("full buffer, headroom unreadable -> blind", full_with_old_error_oldest,
     lambda g: setattr(g, "headroom_ok", False), "blind")
case("repeat cap at baseline -> blind", lambda g: g.log("Error", E1, 99), lambda g: g.log("Error", E1, 5), "blind")
case("repeat cap reached during proof reported", lambda g: g.log("Error", E1, 98), lambda g: g.log("Error", E1, 5), {E1})
case("log suppressed -> blind", nothing, lambda g: setattr(g, "state", "suppressed"), "blind")
case("log state unknown -> blind", nothing, lambda g: setattr(g, "state", "unknown"), "blind")
case("drain_log error reply -> blind", nothing,
     lambda g: setattr(g, "drain_broken", {"success": False, "message": "boom"}), "blind")
case("drain_log empty reply -> blind", nothing, lambda g: setattr(g, "drain_broken", {}), "blind")
case("drain_log capped read -> blind", lambda g: [g.log("Message", "a%d" % i) for i in range(10)],
     lambda g: setattr(g, "drain_broken", {"success": True, "totalInBuffer": 10, "messages": []}), "blind")


def periodic(g):
    for i in range(dlc.MAXQ // 2):
        g.log("Error", E1)
        g.log("Message", "tick")


# a periodic full buffer fits several drop counts (the message counter only bounds from above): honest blind
case("periodic full buffer, same pattern again -> blind", periodic,
     lambda g: (g.log("Error", E1), g.log("Message", "tick")), "blind")
case("periodic full buffer, nothing logged", periodic, nothing, set())

if FAILS:
    print("FAILED: %s" % FAILS)
    sys.exit(1)
print("all deepfire_log_check cases pass")
