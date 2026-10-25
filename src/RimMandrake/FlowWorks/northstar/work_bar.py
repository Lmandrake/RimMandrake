"""WORK_PRIORITY_FIX_ZERO_IGNORED_UNMANUAL: bar (or allow) a work type and PROVE it took.

jawa/set_work_priority writes Pawn_WorkSettings.SetPriority, but with Find.PlaySettings.useWorkPriorities OFF (a fresh
debug map) GetPriority answers 3 for every active work type: a "Hauling 0" does not stop hauling because the pawn is
still active, and the readBack of an active type is a constant 3. A live row that depends on a barred worker therefore
measured nothing. The tool takes manualPriorities=true to switch the flag on first; this helper passes it on every call
and reads the reply back. A reply that does not show manualPrioritiesOn true and readBack == the number written (an old
companion DLL ignores the parameter) is a failed bar: the caller makes its row UNMEASURED/HARNESS, never PASS.

`call` is the runner's bridge call (`B.call` or `t.bridge_call`).
"""


def check_reply(r, want):
    """-> (ok, detail) for one set_work_priority reply and the priority `want` it was asked to write."""
    r = r or {}
    if not r.get("success"):
        return False, "set_work_priority refused: %s" % str(r.get("error") or r.get("message") or r)[:200]
    if r.get("manualPrioritiesOn") is not True:
        return False, "manual priorities still OFF (readBack %r is the constant 3/0, not the bar); companion DLL lacks manualPriorities?" % (r.get("readBack"),)
    if r.get("readBack") != want:
        return False, "readBack %r != requested %r" % (r.get("readBack"), want)
    return True, "work priority %s read back" % want


def set_priority(call, pawn, work_type, priority):
    """-> (ok, detail). Write `priority` for `work_type` with manual priorities forced on, and verify the read-back."""
    r = call("jawa/set_work_priority", pawnId=pawn, workType=work_type, priority=priority, manualPriorities=True)
    ok, why = check_reply(r, priority)
    return ok, ("%s=%s: %s" % (work_type, priority, why))


def set_all(call, pawn, spec):
    """spec = [(work_type, priority), ...] -> (ok, first_failure_detail_or_ok_text)."""
    for wt, pr in spec:
        ok, why = set_priority(call, pawn, wt, pr)
        if not ok:
            return False, why
    return True, "all %d priorities read back" % len(spec)
