"""selftest_bridge_reconcile_read.py - BRIDGE_RECONCILE_WIRE_CLOSED_NOT_CURED. No game, no socket: a fake bridge journal.

reconcile_auto() reads no game, so a dead writer's rimworld/step_game_ticks or jawa/prioritized_work on the game still up
refused every proof until the next restart (9 of 40 live runs, 2026-11-06). call() now asks the bridge's own journal
(rimbridge/list_operations) before refusing. The replays below use the real markers; each other case holds one side of
what the journal may settle and what must still refuse. The journal rows are copied from the real bridge's reply (Status
an int, the tool name in Metadata.requestedId); `--journal-probe` is the live clause proving it still answers that way.
"""
import atexit
import json
import os
import shutil
import sys
import tempfile

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_bridge_reconcile_read_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
D = tempfile.mkdtemp()
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(D, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
os.environ["RIMBRIDGE_ALIVE_PROBE"] = "off"
os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(D, "no_driver_lock.json")
for _k in ("GABP_TOKEN", "GABP_SERVER_PORT", "RIMBRIDGE_HOST", "RIMBRIDGE_DEADLINE"):
    os.environ.pop(_k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402

DEAD_PID = 2 ** 22 + 12345          # above Linux pid_max default: no process holds it
T_CALL = "2026-11-06T12:27:50Z"
T_EPOCH = C._iso_epoch(T_CALL)
SAME_GAME = [T_EPOCH - 3600.0]       # the game that was running when the call went out
GOOD = []
REAL_BRIDGE = C.RimBridge
C.game_starts = lambda: SAME_GAME   # the game is still up: reconcile_auto cannot settle these


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, "" if cond else detail))
    GOOD.append(bool(cond))


def rows():
    with open(os.environ["RIMBRIDGE_EVIDENCE_LOG"], encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def last_reconciled():
    return [r for r in rows() if r.get("ev") == "reconciled"][-1]


def clear():
    for x in C.outstanding_indeterminate():
        C.reconcile_resolve(x["cid"], "not-applied", "selftest cleanup")
    C._UNRESOLVED.clear()


def marker(cid, tool, pid=DEAD_PID, status="in-flight", script="glow_tank_live.py", **kw):
    rec = dict({"ev": "start", "cid": cid, "t": T_CALL, "tool": tool, "mutating": True, "pid": pid, "os": os.name,
                "pid_start": None, "script": script, "status": status}, **kw)
    C._inflight_write(rec)
    return rec


STATUS_NUMBER = {"Pending": 0, "Running": 1, "Completed": 2, "Failed": 3, "TimedOut": 4, "Cancelled": 5}
REQUESTED = {}      # capability -> the tool name the client sent, as the live rows' Metadata.requestedId carries it


def op(cap, status, started=T_CALL.replace("Z", ".4821733+00:00"), success=None):
    """A row as the live bridge writes it (read 2026-11-06, 1000 of 1000 rows): Status is the enum's NUMBER."""
    ended_ok = status == "Completed" if success is None else success
    return {"OperationId": "op_" + cap.rsplit("/", 1)[-1], "CapabilityId": cap, "Status": STATUS_NUMBER.get(status, status),
            "Success": ended_ok, "StartedAtUtc": started, "HasResult": False, "ResultWasTruncated": False, "Warnings": [],
            "Metadata": {"requestedId": REQUESTED.get(cap, "unset/" + cap.rsplit("/", 1)[-1]),
                         "providerId": cap.rsplit("/", 1)[0], "arguments": {}}}


JAWA = "extension.global/global/jawa-bench.-bridge-tools/jawa-bench-terrain-tools/"
LISTOPS = "rimbridge.core/diagnostics/list-operations"
STEP = "rimbridge.core/time/step-game-ticks"
WORK = JAWA + "prioritized-work"
EXCAVATE = JAWA + "flow-works-excavation-drive"
REQUESTED.update({LISTOPS: "rimbridge/list_operations", STEP: "rimworld/step_game_ticks", WORK: "jawa/prioritized_work",
                  EXCAVATE: "jawa/flowworks_excavation_drive"})
SELF = op(LISTOPS, "Running", "2026-11-06T12:40:00.1+00:00")


class Fake:
    """A bridge: the journal reply is `journal` (a list of rows, or any reply; an exception is raised); it records calls."""

    def __init__(self, journal):
        self.journal, self.calls, self.timeouts = journal, [], []
        self.b = REAL_BRIDGE(token="t")
        self.b._request = self.request
        self.b._set_call_timeout = self.set_timeout

    def set_timeout(self, seconds):
        self.timeouts.append(seconds)
        self.b.timeout = seconds

    def request(self, method, params=None):
        self.calls.append(params)
        if params["name"] != C.JOURNAL_TOOL:
            return {"success": True}
        j = self.journal
        if isinstance(j, Exception):
            raise j
        return {"success": True, "operations": j} if isinstance(j, list) else j

    def attempt(self, tool="rimworld/go_to_main_menu"):
        try:
            self.b.call(tool, {}, check=False)
            return None
        except C.IndeterminateError as e:
            return str(e)


# 1 the replays: real markers, real next calls
clear()
marker("b14b956722714bdc", "rimworld/step_game_ticks")
f = Fake([SELF, op(STEP, "Completed")])
err = f.attempt()
case("HOSE_SAVELOAD replay: a dead writer's step_game_ticks, ended, no longer refuses the next proof's go_to_main_menu",
     err is None, err)
case("... recorded with the bridge's answer as 'applied', the operation named", last_reconciled().get("as") == "applied"
     and last_reconciled().get("cid") == "b14b956722714bdc" and "op_step-game-ticks" in last_reconciled().get("note", ""),
     last_reconciled())
case("... the marker is gone, and the journal read went first",
     not C.outstanding_indeterminate() and [c["name"] for c in f.calls] == [C.JOURNAL_TOOL, "rimworld/go_to_main_menu"],
     f.calls)
case("... the read asked for the whole journal, summary rows only",
     f.calls[0]["arguments"] == {"limit": 1000, "includeResults": False}, f.calls[0])
case("... and is not itself a mutation by the client's own reading", f.b.looks_read_only(C.JOURNAL_TOOL))

clear()
marker("6aa06241e8f843b2", "jawa/prioritized_work", status="INDETERMINATE", script="prove_glass_chain.py")
f = Fake([SELF, op(WORK, "Running")])
err = f.attempt()
case("prove_glass_chain replay: still Running on the game -> refused, reason named, nothing mutating sent",
     err and "6aa06241e8f843b2 jawa/prioritized_work" in err and "still running" in err
     and [c["name"] for c in f.calls] == [C.JOURNAL_TOOL], err)
f.journal = [SELF, op(WORK, "Completed")]
case("... the same marker settles once the journal says it ended: the proof after it runs",
     f.attempt() is None and last_reconciled().get("as") == "applied")

# 2 each ending, its verdict
for status, success, want in (("TimedOut", False, "partial"), ("Failed", False, "partial"), ("Cancelled", False, "partial"),
                              ("Completed", False, "not-applied")):
    clear()
    marker("v1", "rimworld/step_game_ticks")
    err = Fake([op(STEP, status, success=success)]).attempt()
    case("%s success=%s settles as %s" % (status, success, want), err is None and last_reconciled().get("as") == want,
         (err, last_reconciled()))

# 2b the bridge's real numbers against its enum, and the same names as words: both spell one status
for name, number in STATUS_NUMBER.items():
    case("Status %d reads as %s, and so does the word" % (number, name),
         C._journal_op(op(STEP, name))["status"] == name and C._journal_op(dict(op(STEP, name), Status=name))["status"] == name)
clear()
marker("real1", "rimworld/step_game_ticks")
real_row = {"OperationId": "op_0321e73ce26142309a852cf82c1968d9", "CapabilityId": "rimbridge.core/time/step-game-ticks", "Status": 2,
            "Success": True, "StartedAtUtc": "2026-11-06T12:27:50.9526528+00:00", "HasResult": False, "ResultWasTruncated": False,
            "Warnings": [], "Metadata": {"requestedId": "rimworld/step_game_ticks", "providerId": "rimbridge.core/time",
                                         "category": "time", "arguments": {"limit": 1000, "includeResults": False}}}
err = Fake([real_row]).attempt()
case("a row typed as the live bridge wrote it settles the marker (the first wiring refused this)",
     err is None and last_reconciled().get("as") == "applied", (err, last_reconciled()))

# 2c the row is matched on the tool the client sent, because the bridge renames some capabilities
clear()
marker("ren1", "jawa/flowworks_excavation_drive")
err = Fake([op(EXCAVATE, "Completed")]).attempt()
case("a tool whose capability has another name (flow-works-excavation-drive) is found, not called moot",
     err is None and last_reconciled().get("as") == "applied", (err, last_reconciled()))
clear()
marker("ren2", "jawa/debug_settings")
REQUESTED[JAWA + "debug-settings-tool"] = "jawa/debug_settings"
err = Fake([op(JAWA + "debug-settings-tool", "Failed", success=False)]).attempt()
case("... so is one whose capability carries a suffix (debug-settings-tool)",
     err is None and last_reconciled().get("as") == "partial", (err, last_reconciled()))
clear()
marker("ren3", "jawa/step_game_ticks")
err = Fake([op(STEP, "Completed")]).attempt()
case("a same-named capability of another tool is not this call", err is None
     and last_reconciled().get("as") == "moot", (err, last_reconciled()))
clear()
marker("ren4", "rimworld/step_game_ticks")
no_id = op(STEP, "Completed")
del no_id["Metadata"]["requestedId"]
err = Fake([no_id]).attempt()
case("a row with no requestedId falls back on the capability's last segment", err is None
     and last_reconciled().get("as") == "applied", (err, last_reconciled()))

# 3 not in the journal
clear()
marker("m1", "rimworld/step_game_ticks")
err = Fake([SELF, op(WORK, "Completed")]).attempt()
case("no row of it and nothing running: moot, the note saying what was read", err is None
     and last_reconciled().get("as") == "moot" and "no operation of it" in last_reconciled().get("note", ""),
     (err, last_reconciled()))
clear()
marker("m2", "rimworld/step_game_ticks")
err = Fake([op(STEP, "Running", "2026-11-06T12:20:00.0+00:00"), op(STEP, "Completed", "2026-11-06T12:21:00.0+00:00")]).attempt()
case("rows begun before the call are not it: a Running one does not block, a Completed one does not answer", err is None
     and last_reconciled().get("as") == "moot", (err, last_reconciled()))
clear()
marker("m3", "rimworld/step_game_ticks")
err = Fake([op(WORK, "Pending", "2026-11-06T12:29:00.0+00:00")]).attempt()
case("ANY other operation begun since the call and not ended still refuses (a capability name could differ)",
     err and "still running" in err, err)
clear()
marker("m4", "rimworld/step_game_ticks")
err = Fake([op(STEP, "Completed", "2026-11-06T12:27:49.1+00:00")]).attempt()
case("a row inside the slack of the marker's whole-second stamp is it", err is None
     and last_reconciled().get("as") == "applied", (err, last_reconciled()))
clear()
marker("m5", "rimworld/step_game_ticks")
err = Fake([op(STEP, "Completed", "2026-11-06T12:40:00.0+00:00"), op(STEP, "Failed", "2026-11-06T12:30:00.0+00:00", False)]).attempt()
case("of two rows since the call, the earliest answers", err is None and last_reconciled().get("as") == "partial", err)

# 4 fails closed: an instrument that cannot see settles nothing
for name, reply in (("no answer", C.RimBridgeError("timed out: deadline exceeded")),
                    ("an unexpected exception", KeyError("x")),
                    ("a reply with no operations list", {"success": False, "error": "nope"}),
                    ("operations not a list", {"operations": "many"}),
                    ("one row unreadable", [op(STEP, "Completed"), {"OperationId": "x"}]),
                    ("an unknown status", [op(STEP, "Sideways")]),
                    ("a timestamp with no zone", [op(STEP, "Completed", "2026-11-06T12:27:50")]),
                    ("a status number off the enum", [op(STEP, 6)]),
                    ("a negative status number", [op(STEP, -1)]),
                    ("a status that is a boolean", [op(STEP, True)]),
                    ("a status that is a float", [op(STEP, 2.0)]),
                    ("a status that is a numeral string", [op(STEP, "2")])):
    clear()
    marker("c1", "rimworld/step_game_ticks")
    f = Fake(reply)
    err = f.attempt()
    case("%s: still refused, marker kept, no mutation sent" % name,
         err and "journal could not be read" in err and [r["cid"] for r in C.outstanding_indeterminate()] == ["c1"]
         and [c["name"] for c in f.calls] == [C.JOURNAL_TOOL], err)

clear()
marker("c2", "rimworld/step_game_ticks", pid=os.getpid(), pid_start=C._proc_start(os.getpid()), status="INDETERMINATE")
err = Fake([op(STEP, "Completed")]).attempt()
case("a live writer may still retry: refused even with the journal saying Completed",
     err and "could still retry" in err, err)
clear()
marker("c3", "rimworld/step_game_ticks")
C._UNRESOLVED["c3"] = {"cid": "c3", "tool": "rimworld/step_game_ticks"}
err = Fake([op(STEP, "Completed")]).attempt()
case("a marker this process failed to write still refuses", err and "c3" in err, err)
clear()
with open(os.path.join(C._inflight_dir(), "c4.json"), "w", encoding="utf-8") as fh:
    fh.write("{not json")
err = Fake([op(STEP, "Completed")]).attempt()
case("an unreadable marker still refuses", err and "c4" in err, err)
clear()
marker("c5", "rimworld/step_game_ticks", status="INDETERMINATE", os="another-os")
err = Fake([op(STEP, "Completed")]).attempt()
case("a marker from another OS cannot have its writer checked: refused", err and "c5" in err, err)
clear()
marker("c6", "rimworld/step_game_ticks", t="sometime")
err = Fake([op(STEP, "Completed")]).attempt()
case("a marker with no readable time still refuses", err and "c6" in err, err)
clear()

# 5 one settles, one stays; the settled one does not come back
marker("s1", "rimworld/step_game_ticks")
marker("s2", "rimworld/step_game_ticks", pid=os.getpid(), pid_start=C._proc_start(os.getpid()), status="INDETERMINATE")
err = Fake([op(STEP, "Completed")]).attempt()
case("two markers: the dead writer's settles, the live writer's alone is named",
     err and "1 earlier" in err and "s2" in err and "s1" not in err
     and [r["cid"] for r in C.outstanding_indeterminate()] == ["s2"], err)
clear()

# 6 a verdict that cannot be recorded settles nothing
marker("w1", "rimworld/step_game_ticks")
real = C.reconcile_resolve


def no_disk(*a, **k):
    raise OSError("disk full")


C.reconcile_resolve = no_disk
err = Fake([op(STEP, "Completed")]).attempt()
C.reconcile_resolve = real
case("a verdict the evidence log refuses leaves the marker refusing", err and "could not be recorded" in err, err)
clear()

# 7 the read is bounded and puts the connection's timeout back, also after a failure
marker("t1", "rimworld/step_game_ticks")
f = Fake(C.RimBridgeError("timed out"))
f.b.timeout = 300.0
f.attempt()
case("the read waits at most 10 s, whatever the connection's timeout, and restores it after a failure",
     f.timeouts == [10.0, 300.0] and f.b.timeout == 300.0, f.timeouts)
clear()

# 8 reconcile_auto still goes first: a gone game costs no bridge call
marker("g1", "rimworld/step_game_ticks")
C.game_starts = lambda: []
f = Fake(C.RimBridgeError("must not be asked"))
err = f.attempt()
C.game_starts = lambda: SAME_GAME
case("a gone game settles with no journal read at all",
     err is None and [c["name"] for c in f.calls] == ["rimworld/go_to_main_menu"], (err, f.calls))

# 9 no marker, no read
f = Fake(C.RimBridgeError("must not be asked"))
case("nothing outstanding: no journal read", f.attempt() is None and [c["name"] for c in f.calls] == ["rimworld/go_to_main_menu"])

# 10 the bridge's timestamps and its MCP-wrapped reply
for text, want in (("2026-11-06T12:27:50.4821733+00:00", T_EPOCH + 0.4821733), ("2026-11-06T12:27:50Z", T_EPOCH),
                   ("2026-11-06T14:27:50+02:00", T_EPOCH), ("2026-11-06T07:27:50.5-05:00", T_EPOCH + 0.5)):
    got = C._iso_exact(text)
    case("timestamp %s" % text, got is not None and abs(got - want) < 1e-6, got)
for bad in ("2026-11-06T12:27:50", "", None, 7, "/Date(1793972505000)/"):
    case("timestamp %r is not read" % (bad,), C._iso_exact(bad) is None)
marker("r1", "rimworld/step_game_ticks")
f = Fake({"content": [{"type": "text", "text": json.dumps({"success": True, "operations": [op(STEP, "Completed")]})}]})
case("a reply wrapped as MCP content text parses too", f.attempt() is None and last_reconciled().get("as") == "applied")


# 11 the CLI: --journal-probe (the live clause) and --reconcile --auto
class FakeClient:
    """RimBridge for _main: the journal reply `reply`, or a connect that raises `refuse`."""
    reply, refuse = None, None

    def __init__(self, *a, **k):
        self.fake = Fake(FakeClient.reply)

    def connect(self):
        if FakeClient.refuse:
            raise FakeClient.refuse

    def close(self):
        pass

    def __enter__(self):
        self.connect()
        return self.fake.b

    def __exit__(self, *exc):
        return False

    def __getattr__(self, name):
        return getattr(self.fake.b, name)


real_endpoint = C.resolve_endpoint
C.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 5174, "t")


def probe(reply=None, refuse=None):
    FakeClient.reply, FakeClient.refuse = reply, refuse
    C.RimBridge = FakeClient
    try:
        return C._main(["--journal-probe"])
    finally:
        C.RimBridge = REAL_BRIDGE


case("--journal-probe: rows parsed, this read's row skipped, a real row settles -> 0", probe([SELF, op(STEP, "Completed")]) == 0)
case("--journal-probe: leaves no marker and no verdict behind",
     not C.outstanding_indeterminate() and not [r for r in rows() if r.get("cid") == "journal-probe"])
case("--journal-probe: a real-typed row with Status as the enum number -> 0", probe([dict(SELF, Status=1), real_row]) == 0)
case("--journal-probe: a Status number off the enum -> 1", probe([SELF, op(STEP, 9)]) == 1)
case("--journal-probe: only its own row, nothing ended to settle -> 2 UNMEASURED", probe([SELF]) == 2)
case("--journal-probe: something running since the row it settles against -> 2 UNMEASURED",
     probe([SELF, op(WORK, "Running", "2026-11-06T12:39:00.0+00:00"), op(STEP, "Completed")]) == 2)
real_settle = C._journal_settle
C._journal_settle = lambda rec, ops: ("moot", "pretend the row was not found")
case("--journal-probe: a row that does not answer for its own call -> 1", probe([SELF, op(STEP, "Completed")]) == 1)
C._journal_settle = real_settle
case("--journal-probe: a reply it cannot parse -> 1", probe({"operations": [{"id": 1}]}) == 1)
case("--journal-probe: no operations list -> 1", probe({"success": True}) == 1)
case("--journal-probe: an empty journal cannot be the truth -> 1", probe([]) == 1)
REQUESTED["rimbridge.core/other/list-operations"] = "rimbridge/list_operations"
case("--journal-probe: this read's own row is not skipped, so it would block itself -> 1",
     probe([op("rimbridge.core/other/list-operations", "Running")]) == 1)
case("--journal-probe: no connection -> 2 UNMEASURED", probe(refuse=C.RimBridgeError("connection refused")) == 2)
case("--journal-probe: the read gets no answer -> 2 UNMEASURED", probe(C.RimBridgeError("timed out")) == 2)
C.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 5174, None)
case("--journal-probe: no token -> 2 UNMEASURED", probe([SELF]) == 2)
C.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 5174, "t")

clear()
marker("x1", "rimworld/step_game_ticks")
FakeClient.reply, FakeClient.refuse = [op(STEP, "Completed")], None
C.RimBridge = FakeClient
rc = C._main(["--reconcile", "--auto"])
case("CLI: --reconcile --auto settles through the journal (exit 0)", rc == 0 and not C.outstanding_indeterminate(), rc)
marker("x2", "rimworld/step_game_ticks")
FakeClient.refuse = C.RimBridgeError("connection refused")
rc = C._main(["--reconcile", "--auto"])
C.RimBridge = REAL_BRIDGE
case("CLI: no bridge to ask: --auto reports it and exits 1 with the marker kept",
     rc == 1 and [r["cid"] for r in C.outstanding_indeterminate()] == ["x2"], rc)
C.resolve_endpoint = real_endpoint
clear()

ok = all(GOOD)
print("%s: %d/%d" % ("PASS" if ok else "FAIL", sum(GOOD), len(GOOD)))
sys.exit(0 if ok else 1)
