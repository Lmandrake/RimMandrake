"""wrapup_debt -- the one door a live stager uses to put what it changed in the game on the wrap-up's debt register.

A stager (scenes/scenelib.py, stage_review.py, modcheck/helpers.SettingsTransaction) calls owe() BEFORE it forces a
setting or stages a scene, and paid() only AFTER its own undo read back clean. A run that crashes, is killed or forgets
its teardown leaves the debt on disk, and rimflow/wrapup.py files it when the agent ends (its census reads
debts_of(owner)) or, for an owner no wrap-up can name, once the debt is DEBT_AGE_S old.
AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED.

Best effort for the caller: no register (an import or write failure) returns None and never stops a stage or a proof.
Runs under python.exe too (wrapup.state_dir picks the Windows path).
"""
import ast
import os
import re
import sys

_W = []


def _wrapup():
    if not _W:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rimflow"))
            import wrapup
            _W.append(wrapup)
        except Exception:  # noqa: BLE001  the register is best effort
            _W.append(None)
    return _W[0]


def owe(kind, what, undo=None, extra=None):
    """kind: setting | scene | other. `extra` adds fields (a restore `plan`). -> token for paid(), or None when there
    is no register."""
    w = _wrapup()
    try:
        return w.owe(kind, what, undo, extra=extra) if w else None
    except Exception:  # noqa: BLE001
        return None


def amend(token, extra):
    """Update an owed debt's fields (a SettingsTransaction's plan grows with every value it forces). -> True when
    found."""
    w = _wrapup()
    try:
        return bool(w and token and w.amend(token, extra))
    except Exception:  # noqa: BLE001
        return False


def paid(token):
    """The debt is undone (call only after the undo read back clean). -> True when it was on the register."""
    w = _wrapup()
    try:
        return bool(w and token and w.paid(token))
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- the bridge door: every forced setting, by construction
# Gens 1-3 asked each stager to owe(); ~90 per-mod validation.py scripts force settings straight through
# rimdrive.Session.call and owed nothing. So the ONE Python door to the game, rimbridge_client.RimBridge.call, hands
# every answered settings write here (the northstar transport's pipelined batch, the only other tools/call sender,
# carries read-only calls only: a mutating call always goes through RimBridge.call).
# The reply carries the value before and after the write, so no caller has to say anything:
#   the first write that CHANGES a key owes it, undo = set it back to the value it had then (`orig`);
#   a later write, by any process, that lands the key back on `orig` pays it.
# A setting the game itself resets (a restart) is void once the game relaunches: wrapup.void_debt reads Player-prev.log.
# rimworld/set_god_mode (core RimBridge, writes DebugSettings.godMode) is not read: its reply shape is not ours.
# A stager that owes its own coarser row (scenelib.setting, SettingsTransaction, validation_v2.sset) still does: a run
# killed inside one files that row too, beside the door's exact per-field rows.

SETTING_TOOLS = ("jawa/mod_settings_field", "jawa/mod_settings_fields", "jawa/debug_settings", "jawa/difficulty_tune")
# >0 while wrapup.restore replays plans in this process: its writes still PAY what they put back, but never OWE the
# reverse change (a legacy plan's difficulty write, with no keyed debt left open, would otherwise owe the forced value
# back and the next restore would force it again)
RESTORING = [0]


def _norm(v):
    return "" if v is None else str(v).strip().lower()


def same_value(a, b):
    a, b = _norm(a), _norm(b)
    if a == b:
        return True
    try:
        fa, fb = float(a), float(b)
    except ValueError:
        return False
    return abs(fa - fb) <= 1e-4 * max(1.0, abs(fb))


def setting_changes(tool, params, out):
    """-> [(key, before, after, undo)] for one answered settings write; [] for anything else."""
    params = params or {}
    if tool not in SETTING_TOOLS or not isinstance(out, dict) or out.get("success") is not True:
        return []
    if tool == "jawa/mod_settings_field":
        if _norm(params.get("action")) != "set" or "valueBefore" not in out:
            return []
        t, f = params.get("typeName"), params.get("field")
        return [("mod_settings_field:%s.%s" % (t, f), out.get("valueBefore"), out.get("valueAfter"),
                 "jawa/mod_settings_field typeName=%s action=set field=%s value=%s" % (t, f, out.get("valueBefore")))]
    if tool == "jawa/mod_settings_fields":
        # the batched form: its one optional set, same key and undo as the single-field tool's
        st = out.get("set")
        if not isinstance(st, dict) or "valueBefore" not in st:
            return []
        t, f = params.get("typeName"), st.get("field") or params.get("setField")
        return [("mod_settings_field:%s.%s" % (t, f), st.get("valueBefore"), st.get("valueAfter"),
                 "jawa/mod_settings_field typeName=%s action=set field=%s value=%s" % (t, f, st.get("valueBefore")))]
    if tool == "jawa/debug_settings":
        if _norm(params.get("action")) != "set" or "valueBefore" not in out:
            return []
        f = params.get("field")
        return [("debug_settings:%s" % f, out.get("valueBefore"), out.get("valueAfter"),
                 "jawa/debug_settings action=set field=%s value=%s" % (f, out.get("valueBefore")))]
    before, after = out.get("before"), out.get("after")         # jawa/difficulty_tune
    if not isinstance(before, dict) or not isinstance(after, dict):
        return []
    return [("difficulty_tune:%s" % k, before.get(k), after.get(k),
             "jawa/difficulty_tune %s=%s" % (k, before.get(k))) for k in sorted(params) if k in before]


def settings_write(tool, params, out):
    """The door's hook: owe or pay what this answered call did to a setting. -> [(act, key)]. Never raises."""
    if tool not in SETTING_TOOLS:
        return []
    w = _wrapup()
    acts = []
    try:
        for key, before, after, undo in setting_changes(tool, params, out):
            open_ = w.debts_keyed(key) if w else []
            if open_:
                if same_value(after, open_[0].get("orig")):
                    for d in open_:
                        w.paid(d.get("token"))
                    acts.append(("paid", key))
                continue
            if not same_value(before, after) and w and not RESTORING[0]:
                tok = w.owe("setting", "%s=%s (was %s)" % (key, after, before), undo,
                            extra={"key": key, "orig": before, "door": "rimbridge_client",
                                   "plan": key_plan(key, before)})
                if tok:
                    acts.append(("owed", key))
    except Exception as e:  # noqa: BLE001  the register never breaks a bridge call
        sys.stderr.write("wrapup_debt: settings register skipped for %s: %s\n" % (tool, e))
    return acts


# ---------------------------------------------------------------- the restore plan: an undo a machine can replay
# WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF: an undo written as prose ("set it back to its pre-run value") waits for a
# human; 11 rows stood on that. A setting debt carries `plan` = [{"tool", "params"}], the exact bridge writes that put
# the game back, and wrapup.restore() replays it at Relentless's next bridge hold, checking each reply (step_ok).

def step(tool, expect=None, **params):
    """One bridge write of a plan. `expect` = {reply field: value} the reply must carry (a tool with no valueAfter)."""
    st = {"tool": tool, "params": params}
    if expect:
        st["expect"] = expect
    return st


def check_not(field, forced):
    """A read step: the debug field must no longer read the value a run forced (a legacy debt kept no pre-value)."""
    return {"tool": "jawa/debug_settings", "params": {"action": "list"}, "not": {"field": field, "value": forced}}


_LEGACY = re.compile(r"^SettingsTransaction forced debug (\w+)=(\S+)$")
_LEGACY_DIFF = re.compile(r"difficulty was (\{[^}]*\})")


def legacy_plan(debt):
    """A SettingsTransaction debt owed before plans (its undo is prose): its pre-run difficulty is exact in the undo
    text (repr of pre_difficulty), so that is written back; the debug field it names kept no pre-value, so the plan
    only CHECKS it no longer reads the forced value (the door's keyed debt for it, replayed first, holds the exact
    one). -> [] when the debt is not one."""
    m = _LEGACY.match(str(debt.get("what") or ""))
    if not m:
        return []
    plan = []
    d = _LEGACY_DIFF.search(str(debt.get("undo") or ""))
    try:
        pre = ast.literal_eval(d.group(1)) if d else {}
    except (ValueError, SyntaxError):
        pre = {}
    if isinstance(pre, dict) and pre:
        plan.append(step("jawa/difficulty_tune", **pre))
    forced = {"true": True, "false": False}.get(m.group(2).lower(), m.group(2))
    plan.append(check_not(m.group(1), forced))
    return plan


def key_plan(key, orig):
    """The door's key + the value it had -> the plan that writes it back ([] when there is nothing to write)."""
    if orig is None or not key or ":" not in key:
        return []
    kind, name = key.split(":", 1)
    if kind == "debug_settings":
        return [step("jawa/debug_settings", action="set", field=name, value=orig)]
    if kind == "difficulty_tune":
        return [step("jawa/difficulty_tune", **{name: orig})]
    if kind == "mod_settings_field" and "." in name:
        t, f = name.rsplit(".", 1)          # the type name is dotted (its namespace); a field name never is
        return [step("jawa/mod_settings_field", typeName=t, action="set", field=f, value=orig)]
    return []


def plan_of(debt):
    """A debt's restore plan: its own, else (a door debt written before plans) derived from key + orig."""
    plan = debt.get("plan")
    if isinstance(plan, list) and plan:
        return plan
    if debt.get("key"):
        return key_plan(debt.get("key"), debt.get("orig"))
    return legacy_plan(debt)


def step_ok(st, out):
    """Did this answered write put the value back? -> None when it did, else why not."""
    if not isinstance(out, dict) or out.get("success") is not True:
        return "%s did not succeed: %s" % (st["tool"], str(out))
    prm = st.get("params") or {}
    if st.get("not"):                                   # a read: the forced value must be gone
        f, v = st["not"].get("field"), st["not"].get("value")
        vals = dict((x.get("name"), x.get("value")) for x in out.get("fields") or [] if isinstance(x, dict))
        if f not in vals:
            return "debug field %s not in the list" % f
        return "debug %s still reads the forced %r" % (f, v) if same_value(vals[f], v) else None
    if st.get("expect"):
        bad = [k for k, v in st["expect"].items() if not same_value(out.get(k), v)]
        return "%s read back %s, wanted %s" % (st["tool"], dict((k, out.get(k)) for k in bad),
                                               dict((k, st["expect"][k]) for k in bad)) if bad else None
    if st["tool"] == "jawa/difficulty_tune":
        after = out.get("after")
        if not isinstance(after, dict):
            return "difficulty_tune gave no `after`"
        bad = [k for k, v in prm.items() if not same_value(after.get(k), v)]
        return "difficulty %s read back %s" % (bad, [after.get(k) for k in bad]) if bad else None
    if "valueAfter" not in out:
        return "%s gave no valueAfter" % st["tool"]
    if not same_value(out.get("valueAfter"), prm.get("value")):
        return "%s %s read back %r, wanted %r" % (st["tool"], prm.get("field"), out.get("valueAfter"), prm.get("value"))
    return None
