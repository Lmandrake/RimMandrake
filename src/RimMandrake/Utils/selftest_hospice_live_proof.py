"""selftest_hospice_live_proof.py -- WARSCAR_HOSPICE_DESERTERS_1: the A2 live driver judges the load before the wake.

The 2026-11-05 A2 run (relentless/live/WARSCAR_HOSPICE_DESERTERS_1-A2-20261105T192358Z.log) FAILED a sound build: the
load carried the RUT campaign swap (spec 7), so the cradle woke a Droidworks droid by design and the standalone mech
checks read it as broken. Scarlands/hospice_live_proof.py is driven here against a fake bridge (no game) and must:

1. swap live (RM_HospiceWakeExtension on RM_HospiceCradle): end on a `reload needed:` line relentless_live reads as a
   restage (asked_reload), exit 2, call no hook (nothing written to the map), print no FAIL (could_not_ask keeps one);
2. the cradle def unreadable (refused, no extra block, odd modExtensions): exit 2, no hook, never "no swap";
3. no swap: a hook PASS waking RM_AncientServitor with the haul offered exits 0; one waking another kind exits 1;
   a PASS whose haul offer went unchecked exits 2; a hook FAIL exits 1 (the replayed 2026-11-05 line included);
4. A3 is untouched: PASS 0, FAIL 1, and it never reads the cradle def.

HOSPICE_PROOF=<path> runs the same cases against another copy of the driver (the mutant probe: the pre-repair driver
goes red on 1, 2 and 3).
"""
import contextlib
import importlib.util
import io
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.environ.get("HOSPICE_PROOF") or os.path.join(HERE, "..", "Scarlands", "hospice_live_proof.py")
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
import relentless_live  # noqa: E402

SERVITOR_PASS = ("PASS haul offered; Unit 4410 (RM_DH_Litany) woke as RM_AncientServitor, colony mech, no mechanitor, "
                 "2 modification hediffs present, lights dark->lit, etchant absent")
DROID_PASS = SERVITOR_PASS.replace("RM_AncientServitor", "RSW_DW_OuterRim_ImperialLaborDroid")
UNCHECKED_PASS = SERVITOR_PASS.replace("haul offered", "haul UNCHECKED (no colonist to haul)")
REAL_FAIL = "FAIL woken RSW_DW_OuterRim_ImperialLaborDroid Unit 6175: not a colony mech; cannot haul"
CRADLE_PLAIN = {"success": True, "defName": "RM_HospiceCradle",
                "extra": {"thingClass": "Building_HospiceCradle", "modExtensions": None}}
CRADLE_SWAP = {"success": True, "defName": "RM_HospiceCradle",
               "extra": {"thingClass": "Building_HospiceCradle", "modExtensions": ["RM_HospiceWakeExtension"]}}


class FakeBridge:
    def __init__(self, get_def, hook):
        self.get_def, self.hook_line, self.calls = get_def, hook, []

    def connect(self):
        return None

    def call(self, tool, params=None, check=True):
        self.calls.append((tool, dict(params or {})))
        if tool == "jawa/get_def":
            return self.get_def
        if tool == "jawa/static_call":
            return {"success": True, "result": self.hook_line}
        raise AssertionError("unexpected tool " + tool)


def run(clause, get_def, hook):
    fake = FakeBridge(get_def, hook)
    rb = types.ModuleType("rimbridge_client")
    rb.resolve_endpoint = lambda *a, **k: ("127.0.0.1", 1, "t")
    rb.RimBridge = lambda **k: fake
    sys.modules["rimbridge_client"] = rb
    spec = importlib.util.spec_from_file_location("hospice_live_proof_under_test", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        spec.loader.exec_module(mod)
        code = mod.main(["hospice_live_proof.py", clause])
    text = out.getvalue()
    hooks = [p.get("method") for t, p in fake.calls if t == "jawa/static_call"]
    defs = [p.get("defName") for t, p in fake.calls if t == "jawa/get_def"]
    return code, text, hooks, defs


fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def last(text):
    lines = [x for x in text.splitlines() if x.strip()]
    return lines[-1] if lines else ""


# 1. a live swap is a reload, decided before the hook writes anything
for hook in (REAL_FAIL, SERVITOR_PASS):
    code, text, hooks, defs = run("A2", CRADLE_SWAP, hook)
    check(code == 2, "swap live: exit %r, want 2 (%s)" % (code, last(text)))
    check(last(text).startswith(relentless_live.RELOAD + ":"), "swap live: last line is not a reload ask: %r" % last(text))
    check("mandrake.rsw.droidworks" in last(text), "swap live: the reload line names no mod to drop: %r" % last(text))
    check(not hooks, "swap live: the Revival hook ran anyway (%s)" % hooks)
    check("FAIL" not in text, "swap live: the log carries a FAIL, which could_not_ask keeps as a verdict: %r" % text)
    check(defs == ["RM_HospiceCradle"], "swap live: the cradle def was not read (%s)" % defs)

# 2. an unreadable def is blind, never "no swap"
for name, gd in (("refused", {"success": False, "message": "no def"}),
                 ("not a dict", None),
                 ("no extra", {"success": True, "defName": "RM_HospiceCradle"}),
                 ("extra without thingClass", {"success": True, "extra": {"modExtensions": None}}),
                 ("modExtensions not a list", {"success": True, "extra": {"thingClass": "X", "modExtensions": "RM_HospiceWakeExtension"}})):
    code, text, hooks, _ = run("A2", gd, SERVITOR_PASS)
    check(code == 2, "def %s: exit %r, want 2 (%s)" % (name, code, last(text)))
    check(not hooks, "def %s: the hook ran on an unread load (%s)" % (name, hooks))
    check("UNMEASURED" in last(text), "def %s: last line does not say UNMEASURED: %r" % (name, last(text)))

# 3. no swap: the standalone verdict, with the driver's own kind and haul checks on top of the hook's
for name, hook, want in (("servitor PASS", SERVITOR_PASS, 0),
                         ("droid PASS", DROID_PASS, 1),
                         ("haul unchecked", UNCHECKED_PASS, 2),
                         ("PASS naming no kind", "PASS haul offered; something happened", 1),
                         ("hook FAIL", "FAIL the cradle did not empty after waking", 1),
                         ("replayed 2026-11-05 FAIL", REAL_FAIL, 1)):
    code, text, hooks, _ = run("A2", CRADLE_PLAIN, hook)
    check(code == want, "no swap, %s: exit %r, want %d (%s)" % (name, code, want, last(text)))
    check(hooks == ["Revival"], "no swap, %s: hooks %s, want [Revival]" % (name, hooks))
    if want == 1:
        check("FAIL" in last(text), "no swap, %s: a failing exit without a FAIL line: %r" % (name, last(text)))

# 4. A3 untouched
for hook, want in (("PASS failed wreck 'Failed chassis (Unit 2262)' keeps the name", 0), ("FAIL no RM_FailedChassis named Unit 1", 1)):
    code, text, hooks, defs = run("A3", CRADLE_SWAP, hook)
    check(code == want, "A3 %s: exit %r, want %d" % (hook[:20], code, want))
    check(hooks == ["Failure"] and not defs, "A3: calls %s / defs %s" % (hooks, defs))

print("hospice live driver: %s" % os.path.relpath(DRIVER, os.path.join(HERE, "..", "..", "..")))
if fails:
    for f in fails[:30]:
        print("FAIL " + f)
    sys.exit(1)
print("PASS")
