"""wrapup_debt -- the one door a live stager uses to put what it changed in the game on the wrap-up's debt register.

A stager (scenes/scenelib.py, stage_review.py, modcheck/helpers.SettingsTransaction) calls owe() BEFORE it forces a
setting or stages a scene, and paid() only AFTER its own undo read back clean. A run that crashes, is killed or forgets
its teardown leaves the debt on disk, and rimflow/wrapup.py files it when the agent ends (its census reads
debts_of(owner)) or, for an owner no wrap-up can name, once the debt is DEBT_AGE_S old.
AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED.

Best effort for the caller: no register (an import or write failure) returns None and never stops a stage or a proof.
Runs under python.exe too (wrapup.state_dir picks the Windows path).
"""
import os
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


def owe(kind, what, undo=None):
    """kind: setting | scene | other. -> token for paid(), or None when there is no register."""
    w = _wrapup()
    try:
        return w.owe(kind, what, undo) if w else None
    except Exception:  # noqa: BLE001
        return None


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

SETTING_TOOLS = ("jawa/mod_settings_field", "jawa/debug_settings", "jawa/difficulty_tune")


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
            if not same_value(before, after) and w:
                tok = w.owe("setting", "%s=%s (was %s)" % (key, after, before), undo,
                            extra={"key": key, "orig": before, "door": "rimbridge_client"})
                if tok:
                    acts.append(("owed", key))
    except Exception as e:  # noqa: BLE001  the register never breaks a bridge call
        sys.stderr.write("wrapup_debt: settings register skipped for %s: %s\n" % (tool, e))
    return acts
