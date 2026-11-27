#!/usr/bin/env python3
"""Selftest: the scene entry points of validation.py against design/concepts/WreckedMachines/scenes.json.

Item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL. Its criteria, each a check here:
  registered   every acceptance and interaction scene whose entry point is validation.py::scene_<x> is a chain of the suite
  start_first  the scene's first component is start_<x>, and START_MARK (the asserted start) is called inside it
  control      the scene declares a control_ component (the foil), run in the same chain
  no_forbidden after START_MARK, no scene (nor a module helper it calls) finishes research, finishes a study, sets a level or
               places a machine, except where its row says so (ALLOWED_AFTER_START, PLACES_AFTER_START below)
  no_proof     on a fake game whose proof type does not answer, every live scene fails its start naming the proof type
  no_crash     on a fake game whose proof type answers, no component ends in a Python error (a harness bug, not a verdict)
  no_stall     on a fake game whose world never changes (no machine is taken apart, no repair delivers), a component that waits
               for such a change reads UNMEASURED, never PASS (a wait that ran out is "could not look", not "found none")
Each check is shown red on a planted fault (--plants, default on). No game, no bridge.
Run: python3 src/RimMandrake/WreckedMachines/selftest_wm_scenes.py [--no-plants]"""
import ast
import inspect
import json
import os
import re
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
SCENES = os.path.join(REPO, "design", "concepts", "WreckedMachines", "scenes.json")

# Rows whose words place a machine after the start (scenes.json "control" or "action"):
PLACES_AFTER_START = {"sc_forge_plasteel": "control: the factory mod's own forge, placed with the forge's line switched off",
                      "sc_cannery_tier": "action: spawn the cannery's Wrecked, Kludged and Refurbished levels and the factory "
                                         "mod's own cannery (after the research reads)"}
FORBIDDEN = [
    (r"research_finish_project|_finish_first\(", "finishes research"),
    (r"research_progress", "moves research progress"),
    (r"research_bulk", "finishes every project"),
    (r"\b(SetLevel|FinishStudy|CompleteRepair)\b", "sets a level or finishes a study by command"),
    (r"_build\(|_staged_wreck\(|_ground_wreck\(|jawa/build_batch", "places a machine"),
]
PY_ERRORS = ("TypeError", "KeyError", "IndexError", "AttributeError", "ValueError", "NameError", "ZeroDivisionError",
             "UnboundLocalError", "AssertionError")


def load(path=None):
    """Import validation.py (or a planted copy at `path`) as a fresh module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("wm_validation_under_test", path or os.path.join(HERE, "validation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scene_rows():
    with open(SCENES, encoding="utf-8") as f:
        s = json.load(f)
    return [x for x in s["scenes"] if x.get("kind") != "exploration"
            and str(x.get("entry_point", "")).startswith("src/RimMandrake/WreckedMachines/validation.py::")]


def _fn_source(mod, name):
    fn = getattr(mod, name, None)
    if fn is None:
        return None
    fn = getattr(fn, "__wrapped__", fn)
    try:
        return textwrap.dedent(inspect.getsource(fn))
    except (OSError, TypeError):
        return None


def _after_start(src):
    i = src.find("START_MARK(")
    if i < 0:
        return None
    j = src.find("\n", i)
    return src[j:]


def _called_helpers(mod, text, seen):
    """Module-level functions named in `text`, and the ones they name, to a fixpoint."""
    out = []
    for name in sorted(set(re.findall(r"\b(_[a-z][a-z0-9_]*)\(", text))):
        if name in seen or not callable(getattr(mod, name, None)):
            continue
        seen.add(name)
        src = _fn_source(mod, name) or ""
        out.append((name, src))
        out.extend(_called_helpers(mod, src, seen))
    return out


def structure(mod):
    """registered, start_first, control, no_forbidden -> list of failures."""
    bad = []
    chains = dict(mod.suite.chains)
    for row in scene_rows():
        sid = row["id"]
        fname = row["entry_point"].split("::", 1)[1]
        if fname not in chains:
            bad.append("registered: %s is not a chain of the suite (%s)" % (sid, fname))
            continue
        from suite import _DeclarationProbe
        p = _DeclarationProbe()
        chains[fname](p)
        names = [c.name for c in p.components]
        short = fname[len("scene_"):]
        if not names or names[0] != "start_" + short:
            bad.append("start_first: %s's first component is %r, want start_%s" % (sid, names[:1], short))
        if not any(n.startswith("control_") for n in names):
            bad.append("control: %s declares no control_ component (%s)" % (sid, names))
        src = _fn_source(mod, fname) or ""
        k = src.find('t.component("start_')
        m = src.find("START_MARK(")
        nxt = src.find("t.component(", k + 1)
        if m < 0 or not (k < m < (nxt if nxt > 0 else len(src))):
            bad.append("start_first: %s does not call START_MARK inside its start component" % sid)
            continue
        after = _after_start(src)
        texts = [(fname, after)] + _called_helpers(mod, after, set())
        allowed = set(getattr(mod, "ALLOWED_AFTER_START", {}).get(sid, ()))
        for pat, what in FORBIDDEN:
            if what == "places a machine" and sid in PLACES_AFTER_START:
                continue
            if any(re.search(pat, a) for a in allowed):
                continue
            hits = [n for n, tx in texts if re.search(pat, tx or "")]
            if hits:
                bad.append("no_forbidden: %s %s after its start (in %s)" % (sid, what, hits[:3]))
    return bad


class FakeSession(object):
    """A game that answers every call. proof=False: the mod's proof type is absent (static_call refuses)."""

    def __init__(self, proof):
        self.proof = proof
        self.calls = []

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/static_call":
            if not self.proof:
                return {"success": False, "error": "type not found"}
            return {"success": True, "result": self.answer(kw.get("method"), kw.get("args"))}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"id": "Thing_X1", "x": 500, "z": 500, "stackCount": 1, "def": kw.get("defName")}]}
        if tool == "jawa/spawn_pawn":
            return {"success": True, "pawns": [{"id": "Pawn_1"}]}
        if tool == "jawa/thing_set_sample":
            if kw.get("kind") == "list":
                return {"success": True, "thingSetMakers": [{"defName": "Reward_ItemsStandard", "mod": "ludeon.rimworld"}],
                        "traders": [{"defName": "Orbital_Exotic", "mod": "ludeon.rimworld.odyssey"}]}
            return {"success": True, "rows": [{"def": "Steel", "runsWith": 3}]}
        if tool == "jawa/drain_log":
            return {"success": True, "messages": []}
        return {"success": True}

    def answer(self, method, args):
        ms = ["MACHINE %s | on true | wrecked RM_%s_W | kludged RM_%s_K | refurbished RM_%s_R | original %s" % (k, k, k, k, v)
              for k, v in (("smelter", "VFEFactory_AutomatedSmelter"), ("autoloom", "VFEFactory_Autoloom"),
                           ("alloyforge", "VFEFactory_AutomatedAlloyForge"), ("drill", "VFEFactory_AutomatedDrillPlatform"),
                           ("powercell", "VanometricPowerCell"), ("emanator", "PsychicEmanator"))]
        return {
            "Loaded": "LOADED version 0.1.0 | lines 20",
            "Machines": "\n".join(ms),
            "Settings": "SETTING kludgedRatio | value 0.1 | shipped 0.1",
            "Projects": "\n".join("PROJECT RM_P_%s_%s | line %s | step %s" % (k, s, k, s)
                                  for k in ("smelter", "autoloom", "alloyforge", "drill", "powercell", "emanator") for s in "12"),
            "Level": "LEVEL Wrecked | line smelter | def RM_smelter_W",
            "Repair": "REPAIR none | next Kludged | delivered  | work 0/100",
            "SignalLog": "",
            "Placement": "PLACE RM_smelter_W | where ruin",
            "InRuinRoom": "ROOM true",
            "Speed": "SPEED 1.0",
        }.get(method, "OK")


def run_fake(mod, proof):
    """Every live scene chain on a fake game -> {chain: [(component, verdict, detail)]}."""
    from suite import TestContext
    out = {}
    marks = []
    mod.START_MARK = lambda t, sid: marks.append(sid)
    for name, fn in mod.suite.chains:
        if not name.startswith("scene_") or name == "scene_text_names_no_setting":
            continue
        t = TestContext(FakeSession(proof))
        t.feed = False
        t.wait_ticks = lambda n, **kw: None          # the fake has no clock
        t.screenshot = lambda *a, **kw: None         # never an OS capture from a selftest (it fell back to the desktop)
        t.mark_log = lambda: None
        try:
            fn(t)
        except Exception as e:   # a chain that throws outside its components is itself a harness bug
            out[name] = [("(chain)", "ERROR", "%s: %s" % (type(e).__name__, e))]
            continue
        out[name] = [(c.name, c.verdict, str(c.detail or "")) for c in t.components]
    return out, marks


def fakes(mod):
    bad = []
    got, _ = run_fake(mod, proof=False)
    for name, comps in got.items():
        first = comps[0] if comps else ("", "", "")
        if not first[0].startswith("start_") or "proof type does not answer" not in first[2]:
            bad.append("no_proof: %s did not fail its start on the missing proof type: %s" % (name, first))
    got, marks = run_fake(mod, proof=True)
    for name, comps in got.items():
        for c, v, d in comps:
            if any(re.search(r"(^|\W)%s: " % e, d[:80]) for e in PY_ERRORS):
                bad.append("no_crash: %s/%s ended in a Python error: %s" % (name, c, d[:160]))
    return bad


def text_scene(mod):
    """The offline scene runs whole on the shipped mod; its control (planted texts) must be found."""
    from suite import TestContext
    t = TestContext(None)
    t.session = None
    fn = dict(mod.suite.chains)["scene_text_names_no_setting"]
    fn(t)
    rows = [(c.name, c.verdict, c.detail) for c in t.components]
    ctl = [r for r in rows if r[0].startswith("control_")]
    if not ctl or ctl[0][1] != "PASS":
        return ["text: the planted texts were not found: %s" % rows]
    return []


class StalledSession(FakeSession):
    """A game that answers every call but whose world never moves: a Deconstruct order takes nothing apart, a repair is ordered
    and never delivers. The reads that a start needs answer as a healthy game would."""

    def call(self, tool, **kw):
        if tool == "jawa/thing_set_sample" and kw.get("kind") == "list":
            self.calls.append((tool, kw))
            mods = ("ludeon.rimworld", "ludeon.rimworld.ideology", "ludeon.rimworld.odyssey", "ludeon.rimworld.anomaly")
            return {"success": True, "thingSetMakers": [{"defName": "G_%d" % i, "mod": m} for i, m in enumerate(mods)],
                    "traders": [{"defName": "T_0", "mod": mods[0]}]}
        if tool == "jawa/get_defs":
            self.calls.append((tool, kw))
            return {"success": True, "defs": [{"defName": "Recipe_Plain", "fields": {"products": "Steel"}}]}
        if tool == "jawa/list_things" and kw.get("defName") == "RM_WM_AncientComponent":
            self.calls.append((tool, kw))
            return {"success": True, "things": []}
        if tool == "jawa/set_terrain_batch":         # the ground a scene lays is the ground it reads back
            self.calls.append((tool, kw))
            self.laid = kw.get("terrainDef")
            return {"success": True}
        if tool == "jawa/get_terrain_batch":
            self.calls.append((tool, kw))
            laid = getattr(self, "laid", None) or "Soil"
            return {"success": True, "distinctTerrains": [laid], "ops": "%s:%s" % (laid, kw.get("rects"))}
        if tool == "rimworld/list_selected_gizmos":
            self.calls.append((tool, kw))
            return {"success": True, "gizmos": [{"label": "Repair", "disabled": False, "gizmoId": "g_repair"},
                                                {"label": "Cancel repair", "disabled": False, "gizmoId": "g_cancel"}]}
        return FakeSession.call(self, tool, **kw)


# (chain, the component that waits for a change of the world)
STALL_WAITERS = (("scene_no_handouts", "machines_taken_apart_leave_no_component"),
                 ("scene_repair_cancelled", "cancel_never_loses_the_machine"))


def stalls(mod):
    from suite import TestContext
    bad = []
    chains = dict(mod.suite.chains)
    mod.START_MARK = lambda t, sid: None
    for chain, comp in STALL_WAITERS:
        t = TestContext(StalledSession(True))
        t.feed = False
        t.wait_ticks = lambda n, **kw: None
        t.screenshot = lambda *a, **kw: None
        t.mark_log = lambda: None
        try:
            chains[chain](t)
        except Exception as e:
            bad.append("no_stall: %s threw outside its components: %s: %s" % (chain, type(e).__name__, e))
            continue
        rows = {c.name: c for c in t.components}
        c = rows.get(comp)
        if c is None:
            bad.append("no_stall: %s has no component %s" % (chain, comp))
        elif c.verdict != "UNMEASURED":
            bad.append("no_stall: %s/%s read %s on a world that never changed (want UNMEASURED): %s"
                       % (chain, comp, c.verdict, str(c.detail or "")[:120]))
    return bad


PLANTS = [
    # (old, new, the check that must go red)
    ('            START_MARK(t, "sc_repair_on_machine")\n', '            START_MARK(t, "sc_repair_on_machine")\n            _finish_first(t, "autoloom")\n',
     "no_forbidden"),
    ('    with t.component("control_wall_uninstall_refused"):', '    with t.component("wall_uninstall_refused"):', "control"),
    ('            START_MARK(t, "sc_component_gate")\n', '', "start_first"),
    ('@suite.chain("scene_marks_agree")', '@suite.chain("scene_marks_agree_renamed")', "registered"),
    ('        raise ExpectationFailed("the mod\'s proof type does not answer %s(%s): %s" % (method, args, str(r)[:200]))',
     '        return []', "no_proof"),
    ('    return rows[0]["_word"] if rows else None\n', '    return rows[5]["_word"]\n', "no_crash"),
    ('            elif f.endswith(".cs") and "SelfTest" not in rel and "Kernel" not in rel:',
     '            elif False:', "text"),
    ("                if standing:       # a wait that ran out", "                if False:       # a wait that ran out", "no_stall"),
    ("                else:              # a cancel at the wrong stage", "                if False:              # a cancel at the wrong stage",
     "no_stall"),
]


def checks(mod):
    return structure(mod) + fakes(mod) + stalls(mod) + text_scene(mod)


def main(argv):
    mod = load()
    bad = checks(mod)
    for b in bad:
        print("  FAIL " + b)
    plants_bad = []
    if "--no-plants" not in argv:
        import tempfile
        src = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
        for old, new, check in PLANTS:
            if old not in src:
                plants_bad.append("plant for %s no longer matches validation.py (%r)" % (check, old[:50]))
                continue
            d = tempfile.mkdtemp(prefix="wm_plant_")
            p = os.path.join(d, "validation.py")
            with open(p, "w", encoding="utf-8") as f:
                f.write(src.replace(old, new, 1))
            try:
                pm = load(p)
                pm.HERE = HERE
                got = checks(pm)
            except Exception as e:      # a plant that breaks the import is not a red of its check
                got = ["import: %s" % e]
            if not any(g.startswith(check + ":") for g in got):
                plants_bad.append("plant for %s stayed green (%s)" % (check, got[:2]))
        for b in plants_bad:
            print("  FAIL " + b)
    n = len(scene_rows())
    ok = not bad and not plants_bad
    print("selftest_wm_scenes: %s (%d scenes, %d plants)" % ("PASS" if ok else "FAIL", n, 0 if "--no-plants" in argv else len(PLANTS)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
