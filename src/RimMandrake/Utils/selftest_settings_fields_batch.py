"""speed_20261112 step 2a/2b: validation_core.probe_of over jawa/mod_settings_fields (the many-fields companion tool).

A probe was four single-field calls (get serial, set request, poll serial, get result); GSS proof_all made 1,600 of
them. Through the batched tool it is two: (read serial + post request, one main-thread pass) and (read serial + result).
A companion without the tool falls back to the four calls once and stays there. A failed serial read posts nothing.
The batched set is still owed and restored like a single-field set (wrapup_debt, modcheck's chain recorder).

Offline: a fake game with a probe mailbox (a request posted is serviced on the next call, as a frame would).
SELFTEST_SETTINGS_FIELDS_UTILS points the imports at another Utils copy (the fail-before run)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UT = os.environ.get("SELFTEST_SETTINGS_FIELDS_UTILS") or HERE
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, UT)
sys.path.insert(1, os.path.join(UT, "modcheck"))
os.environ["RM_BRIDGE_SPLIT"] = "0"
import validation_core as VC  # noqa: E402
import wrapup_debt as WD  # noqa: E402

PT = "RimMandrake.Test.ProbeSettings"
fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


class Game(object):
    """A probe mailbox: static fields serial/request/result. A posted request is serviced before the next call."""

    def __init__(self, batch=True, serial_readable=True):
        self.batch, self.serial_readable = batch, serial_readable
        self.f = {"serial": "7", "request": "", "result": ""}
        self.pending = None
        self.sent = []

    def frame(self):
        if self.pending is not None:
            cmd, self.pending = self.pending, None
            self.f["result"] = json.dumps({"success": True, "echo": cmd})
            self.f["serial"] = str(int(self.f["serial"]) + 1)

    def read(self, name):
        if name == "serial" and not self.serial_readable:
            return None
        return self.f.get(name)

    def __call__(self, tool, kw):
        self.frame()
        self.sent.append((tool, dict(kw)))
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "set":
                before = self.f.get(kw["field"])
                self.f[kw["field"]] = kw["value"]
                self.pending = kw["value"] if kw["field"] == "request" else self.pending
                return {"success": True, "valueBefore": before, "valueAfter": kw["value"]}
            v = self.read(kw["field"])
            return {"success": v is not None, "value": v} if v is not None else {"success": False, "error": "no field"}
        if tool == "jawa/mod_settings_fields" and self.batch:
            names = [n.strip() for n in (kw.get("fields") or "").split(",") if n.strip()]
            values, missing = {}, {}
            for n in names:
                v = self.read(n)
                if v is None:
                    missing[n] = "no field"
                else:
                    values[n] = v
            out = {"success": not missing, "values": values, "missing": missing, "ticksGame": 1}
            if kw.get("setField") and not missing:
                f = kw["setField"]
                out["set"] = {"field": f, "valueBefore": self.f.get(f), "valueAfter": kw["setValue"]}
                self.f[f] = kw["setValue"]
                if f == "request":
                    self.pending = kw["setValue"]
            elif kw.get("setField"):
                out["error"] = "set NOT applied: a read failed first"
            return out
        return {"success": False, "error": "Unknown tool '%s'" % tool}


class Bridge(VC._BridgeBase):
    probe_type = PT

    def __init__(self, game):
        self.game = game

    def _raw(self, tool, kw):
        return self.game(tool, kw)


def case(name, fn):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001 - a crash is a failed row, named
        check(False, name, "raised %s: %s" % (type(ex).__name__, str(ex)[:160]))


def batched_probe_is_two_calls():
    g = Game()
    r = Bridge(g).probe('{"op":"ping"}', wait_s=2.0)
    check(r.get("echo") == '{"op":"ping"}', "batched_probe_answers", str(r)[:160])
    check(len(g.sent) == 2 and all(t == "jawa/mod_settings_fields" for t, _ in g.sent),
          "batched_probe_two_calls", str([t for t, _ in g.sent]))
    first = g.sent[0][1] if g.sent else {}
    check(first.get("fields") == "serial" and first.get("setField") == "request",
          "serial_read_and_request_posted_in_one_call", str(first))


def old_companion_falls_back():
    g = Game(batch=False)
    b = Bridge(g)
    r = b.probe('{"op":"ping"}', wait_s=2.0)
    check(r.get("echo") == '{"op":"ping"}', "fallback_probe_same_answer", str(r)[:160])
    del g.sent[:]
    r = b.probe('{"op":"pong"}', wait_s=2.0)
    check(r.get("echo") == '{"op":"pong"}' and [t for t, _ in g.sent].count("jawa/mod_settings_fields") == 0,
          "fallback_remembered_no_retry", str([t for t, _ in g.sent]))


def unreadable_serial_posts_nothing():
    for batch in (True, False):
        g = Game(batch=batch, serial_readable=False)
        r = Bridge(g).probe('{"op":"x"}', wait_s=0.5)
        check(r.get("success") is False and "serial unreadable" in str(r.get("error")) and g.f["request"] == "",
              "unreadable_serial_posts_nothing_%s" % ("batch" if batch else "single"), str(r)[:160])


def batched_set_is_owed():
    out = {"success": True, "values": {"serial": "7"}, "set": {"field": "request", "valueBefore": "a", "valueAfter": "b"}}
    ch = WD.setting_changes("jawa/mod_settings_fields", {"typeName": PT, "fields": "serial", "setField": "request",
                                                        "setValue": "b"}, out)
    check(len(ch) == 1 and ch[0][0] == "mod_settings_field:%s.request" % PT and ch[0][1] == "a",
          "batched_set_on_debt_register", str(ch))
    import rimbridge_client as RB
    check("jawa/mod_settings_fields" in RB._SETTING_TOOLS, "client_routes_batched_set_to_register")
    suite = open(os.path.join(UT, "modcheck", "suite.py"), encoding="utf-8").read()
    check('"jawa/mod_settings_fields" and kw.get("setField")' in suite, "chain_recorder_remembers_batched_set")


def companion_source():
    p = os.path.join(REPO, "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchModSettingsFieldsBatchTools.cs")
    src = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    check('"jawa/mod_settings_fields"' in src, "companion_declares_batched_tool")
    i, j = src.find("foreach (string name in names)"), src.find("if (wantSet && missing.Count > 0)")
    check(0 < i < j, "companion_reads_before_set_and_failed_read_blocks_set")
    one = os.path.join(REPO, "src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchModSettingsFieldTools.cs")
    check('"jawa/mod_settings_field",' in open(one, encoding="utf-8").read(), "single_field_tool_kept")


for n, f in (("batched_probe_is_two_calls", batched_probe_is_two_calls), ("old_companion_falls_back", old_companion_falls_back),
             ("unreadable_serial_posts_nothing", unreadable_serial_posts_nothing), ("batched_set_is_owed", batched_set_is_owed),
             ("companion_source", companion_source)):
    case(n, f)
print("%d FAIL" % len(fails) if fails else "ALL OK")
sys.exit(1 if fails else 0)
