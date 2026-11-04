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
