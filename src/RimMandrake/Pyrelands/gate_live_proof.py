"""Live proof of the Pyrelands mechanics gate (PYRELANDS_SHIP_READINESS_1, clauses A1 and A2).

Read-only: three getter calls through jawa/static_call, no setting is changed.
  A1  RimMandrake.Pyrelands.PyrelandsMechanicsGate.get_ShellPresent -> True (the composed mod's shell was found
      by reflection) and get_On -> True (shipped defaults: "Mod enabled" on, the Baroque Biomes "Pyrelands" toggle on).
  A2  get_ShellOn equals RimMandrake.Biomes.RM_BiomesSettings.Enabled("Pyrelands") (the gate reads the shell's switch).
Exit 0 = the clause holds, 1 = the game answered and it does not, 2 = UNMEASURED (no bridge, a refusal, no result).
Runs from WSL as `python.exe <this file> A1|A2`; `--selftest` checks the verdict kernel offline.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))

GATE = "RimMandrake.Pyrelands.PyrelandsMechanicsGate"
SHELL = "RimMandrake.Biomes.RM_BiomesSettings"
CALLS = {
    "present": (GATE, "get_ShellPresent", ""),
    "on": (GATE, "get_On", ""),
    "shellOn": (GATE, "get_ShellOn", ""),
    "enabled": (SHELL, "Enabled", "Pyrelands"),
}


def as_bool(reply):
    """A static_call reply (dict) -> True/False, or None when it did not answer a bool."""
    if not isinstance(reply, dict) or reply.get("success") is False:
        return None
    r = str(reply.get("result", "")).strip().lower()
    return {"true": True, "false": False}.get(r)


def verdict(clause, got):
    """-> (exit code, line). `got` maps CALLS keys to True/False/None. Pure, checked offline by --selftest."""
    need = {"A1": ("present", "on"), "A2": ("shellOn", "enabled")}.get(clause)
    if need is None:
        return 2, "unknown clause %r" % clause
    missing = [k for k in need if got.get(k) is None]
    if missing:
        return 2, "UNMEASURED %s: no bool from %s" % (clause, ", ".join(missing))
    if clause == "A1":
        ok = got["present"] and got["on"]
        return (0 if ok else 1), "A1 ShellPresent=%s On=%s" % (got["present"], got["on"])
    ok = got["shellOn"] == got["enabled"]
    return (0 if ok else 1), "A2 ShellOn=%s RM_BiomesSettings.Enabled(Pyrelands)=%s" % (got["shellOn"], got["enabled"])


def selftest():
    import rimbridge_client as R
    unreviewed = [(t, m) for t, m, _ in CALLS.values() if R.read_only_static({"type": t, "method": m})]
    if unreviewed:
        print("SELFTEST FAIL: not reviewed read-only in rimbridge_client:", unreviewed)
        return 1
    cases = [
        ("A1", {"present": True, "on": True}, 0),
        ("A1", {"present": False, "on": True}, 1),
        ("A1", {"present": True, "on": False}, 1),
        ("A1", {"present": True, "on": None}, 2),
        ("A2", {"shellOn": True, "enabled": True}, 0),
        ("A2", {"shellOn": False, "enabled": False}, 0),
        ("A2", {"shellOn": True, "enabled": False}, 1),
        ("A2", {"shellOn": None, "enabled": True}, 2),
        ("B9", {}, 2),
    ]
    bad = [(c, g, w, verdict(c, g)) for c, g, w in cases if verdict(c, g)[0] != w]
    assert as_bool({"success": True, "result": "True"}) is True
    assert as_bool({"success": True, "result": "False"}) is False
    assert as_bool({"success": False, "result": "True"}) is None
    assert as_bool({"result": "7"}) is None and as_bool(None) is None
    for b in bad:
        print("SELFTEST FAIL", b)
    print("selftest %d/%d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    clause = argv[0] if argv else "A1"
    try:
        import rimbridge_client as R
        host, port, token = R.resolve_endpoint()
        if not token:
            print("UNMEASURED: no bridge token")
            return 2
        got = {}
        with R.RimBridge(host, port, token, timeout=60) as rb:
            rb.static_reads = True   # every pair in CALLS is in rimbridge_client.READ_ONLY_STATIC_CALLS
            for key, (ty, meth, args) in CALLS.items():
                got[key] = as_bool(rb.call("jawa/static_call", {"type": ty, "method": meth, "args": args}))
    except Exception as ex:  # any transport failure means the proof could not see
        print("UNMEASURED: bridge call failed: %s" % str(ex)[:300])
        return 2
    code, line = verdict(clause, got)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
