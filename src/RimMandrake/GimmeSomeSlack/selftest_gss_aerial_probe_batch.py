#!/usr/bin/env python3
"""validation_aerial.A.ap over jawa/mod_settings_fields (RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE).

The aerial probe was at least five single-field calls a probe (get serial, set request, poll serial, get result, re-read
serial) plus a 0.3 s sleep per missed poll: after validation_core.probe_of moved to the batch tool, it was most of GSS
proof_all's 3,402 remaining single reads. Through the batch tool it is two calls: (read serial + post request, one
main-thread pass) and (read serial + result, one pass, so the result cannot belong to a later frame). A companion without
the tool falls back to the old calls once and stays there. Every check the old path made still refuses: unreadable or
negative serial (raises), failed set, failed read, mismatched command or net coordinates.

Offline: a fake game whose probe mailbox services a posted request before the next call, as a frame would."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_BRIDGE_SPLIT", "0")
import validation_aerial as A  # noqa: E402
import validation as V  # noqa: E402

BATCH = "jawa/mod_settings_fields"
SINGLE = "jawa/mod_settings_field"
fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


class Game(object):
    """AerialProbe's static serial/request/result. `answer(cmd)` is the reply a frame writes; `lag` frames pass first."""

    def __init__(self, batch=True, serial="9", answer=None, lag=0, fail_set=False):
        self.batch, self.lag, self.fail_set = batch, lag, fail_set
        self.f = {"serial": serial, "request": "", "result": ""}
        self.answer = answer or (lambda cmd: {"success": True, "cmd": cmd})
        self.pending, self.wait = None, 0
        self.sent = []

    def frame(self):
        if self.pending is None:
            return
        if self.wait > 0:
            self.wait -= 1
            return
        cmd, self.pending = self.pending, None
        self.f["result"] = json.dumps(self.answer(cmd))
        self.f["serial"] = str(int(self.f["serial"]) + 1)

    def post(self, value):
        self.f["request"] = value
        self.pending, self.wait = value, self.lag

    def __call__(self, tool, kw):
        self.frame()
        self.sent.append((tool, dict(kw)))
        if kw.get("typeName") != A.APROBE:
            return {"success": False, "error": "wrong type %r" % kw.get("typeName")}
        if tool == SINGLE:
            if kw.get("action") == "set":
                if self.fail_set:
                    return {"success": False, "error": "set refused"}
                self.post(kw["value"])
                return {"success": True}
            v = self.f.get(kw["field"])
            return {"success": True, "value": v} if v is not None else {"success": False, "error": "no field"}
        if tool == BATCH and self.batch:
            names = [n.strip() for n in (kw.get("fields") or "").split(",") if n.strip()]
            values = {n: self.f[n] for n in names if self.f.get(n) is not None}
            missing = {n: "no field" for n in names if self.f.get(n) is None}
            out = {"success": not missing, "values": values, "missing": missing, "ticksGame": 1}
            if kw.get("setField"):
                if missing or self.fail_set:
                    out["success"] = False
                    out["error"] = "set NOT applied"
                else:
                    out["set"] = {"field": kw["setField"], "valueBefore": self.f["request"], "valueAfter": kw["setValue"]}
                    self.post(kw["setValue"])
            return out
        return {"success": False, "error": "Unknown tool '%s'" % tool}


def bridge(game):
    b = object.__new__(A.A)
    b._raw = lambda tool, kw: game(tool, kw)
    return b


def tools(game):
    return [t for t, _ in game.sent]


def run(name, fn):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001 - a crash is a failed row, named
        check(False, name, "raised %s: %s" % (type(ex).__name__, str(ex)[:160]))


def batched_probe_is_two_calls():
    g = Game()
    r = bridge(g).ap("census", wait_s=2.0)
    check(r.get("success") is True and r.get("cmd") == "census" and r.get("_probeSerial") == 10,
          "batched_ap_answers_with_serial", str(r)[:160])
    check(tools(g) == [BATCH, BATCH], "batched_ap_two_batch_calls", str(tools(g)))
    first = g.sent[0][1] if g.sent else {}
    check(first.get("fields") == "serial" and first.get("setField") == "request" and first.get("setValue") == "census",
          "serial_read_and_request_posted_in_one_call", str(first))
    second = g.sent[1][1] if len(g.sent) > 1 else {}
    check(set((second.get("fields") or "").split(",")) == {"serial", "result"} and not second.get("setField"),
          "poll_reads_serial_and_result_together", str(second))


def slow_frame_polls_without_long_sleeps():
    g = Game(lag=3)
    t0 = time.time()
    r = bridge(g).ap("cprocess", wait_s=5.0)
    took = time.time() - t0
    check(r.get("success") is True and tools(g).count(SINGLE) == 0, "slow_frame_still_answers", str(r)[:120])
    check(took < 0.75, "three_missed_polls_under_0.75s", "%.2f s" % took)


def net_reply_checks_coordinates():
    good = {"success": True, "cmd": "net", "x": 117, "z": 187, "things": []}
    g = Game(answer=lambda cmd: good)
    check(bridge(g).ap("net:117,187", wait_s=1.0).get("success") is True, "net_echo_accepted_batched")
    for edit in ({"x": 118}, {"z": 188}, {"x": "117"}, {"x": 117.0}, {"x": None}, {"cmd": "census"}):
        g = Game(answer=lambda cmd, e=edit: dict(good, **e))
        check(bridge(g).ap("net:117,187", wait_s=0.5).get("success") is not True, "net_mismatch_refused_%s" % edit)


def mismatched_or_bad_result_refused():
    for name, answer in (("other_cmd", lambda c: {"success": True, "cmd": "other"}),
                         ("not_a_dict", lambda c: [1, 2])):
        g = Game(answer=answer)
        check(bridge(g).ap("census", wait_s=0.5).get("success") is not True, "batched_refuses_%s" % name)


def unreadable_serial_raises_and_posts_nothing():
    for batch in (True, False):
        for serial in (None, "-1", "x"):
            g = Game(batch=batch, serial=serial)
            b = bridge(g)
            raised = False
            try:
                b.ap("census", wait_s=0.5)
            except ValueError:
                raised = True
            # the batch tool reads and posts in one pass: it refuses to post only on a MISSING serial; a present but
            # malformed one (an int field cannot hold one) is posted, then refused here
            posted_ok = g.f["request"] == "" or (batch and serial is not None)
            check(raised and posted_ok, "unreadable_serial_%r_%s" % (serial, "batch" if batch else "single"),
                  "raised=%s request=%r" % (raised, g.f["request"]))


def failed_set_refused():
    for batch in (True, False):
        g = Game(batch=batch, fail_set=True)
        r = bridge(g).ap("census", wait_s=0.5)
        check(r.get("success") is False and "set failed" in str(r.get("error")), "failed_set_%s" % batch, str(r)[:120])


def old_companion_falls_back_once():
    g = Game(batch=False)
    b = bridge(g)
    r = b.ap("census", wait_s=2.0)
    check(r.get("success") is True and r.get("_probeSerial") == 10, "fallback_same_answer", str(r)[:120])
    del g.sent[:]
    r = b.ap("cstyles", wait_s=2.0)
    check(r.get("success") is True and BATCH not in tools(g), "fallback_remembered_no_retry", str(tools(g)))


def timeout_reported():
    g = Game(lag=10 ** 6)
    r = bridge(g).ap("census", wait_s=0.3)
    check(r.get("success") is False and "timed out" in str(r.get("error")), "timeout_reported", str(r)[:120])


def gss_mailbox_probe_polls_fast():
    check(getattr(V.Bridge, "probe_poll_s", 0.3) <= 0.1 and getattr(V.SuiteBridge, "probe_poll_s", 0.3) <= 0.1,
          "gss_probe_poll_at_most_0.1s", str(getattr(V.Bridge, "probe_poll_s", None)))


def matrix_live_bridge_batches():
    # northstar_matrix/run_live.LiveBridge (gravship_scene, proof_all's matrix block) had its own four-call mailbox:
    # 88 single reads on one gravship_scene run on SteveDesktop, 2026-11-12
    sys.path.insert(0, os.path.join(HERE, "northstar_matrix"))
    import run_live as RL
    check(RL.APROBE == A.APROBE, "matrix_aprobe_is_the_aerial_probe", RL.APROBE)
    for batch, want in ((True, [BATCH, BATCH]), (False, None)):
        g = Game(batch=batch)
        b = object.__new__(RL.LiveBridge)
        b.n = 0
        b.call = lambda tool, **kw: g(tool, kw)
        r = b.ap("census", wait_s=2.0)
        check(r.get("success") is True and r.get("cmd") == "census", "matrix_ap_answers_%s" % batch, str(r)[:120])
        if want:
            check(tools(g) == want, "matrix_ap_two_batch_calls", str(tools(g)))
        else:
            check(BATCH in tools(g)[:1] and tools(g).count(SINGLE) == 4, "matrix_ap_falls_back_to_four", str(tools(g)))
    g = Game(serial=None)
    b = object.__new__(RL.LiveBridge)
    b.call = lambda tool, **kw: g(tool, kw)
    r = b.ap("census", wait_s=0.3)
    check(r.get("success") is False and g.f["request"] == "", "matrix_unreadable_serial_posts_nothing", str(r)[:120])


if __name__ == "__main__":
    for fn in (batched_probe_is_two_calls, slow_frame_polls_without_long_sleeps, net_reply_checks_coordinates,
               mismatched_or_bad_result_refused, unreadable_serial_raises_and_posts_nothing, failed_set_refused,
               old_companion_falls_back_once, timeout_reported, gss_mailbox_probe_polls_fast, matrix_live_bridge_batches):
        run(fn.__name__, fn)
    print("%s: %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)
