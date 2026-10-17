"""Provenance for the standalone live drivers (thirst_live.py, sprinkler_live.py): what validation.py's driver_rows_at needs
before it will read a result -- mode 'live', the mod, the mod hash of the repo tree at run start (modcheck status.mod_hash,
the same hash `modcheck record` checks) and what the GAME is running: the live mod list and the sha256 of the FlowWorks
assembly it loaded. The repo hash alone cannot say the deployed DLL is the repo's: a run against an undeployed fix would
otherwise certify that fix. Never raises; a field it cannot read is None with the reason beside it."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(FW), "Utils")


def stamp(res, call):
    """Fill res['mode'|'mod'|'mod_hash'|'env'] in place. `call(name, **kw)` is the driver's bridge call."""
    res["mode"], res["mod"] = "live", "FlowWorks"
    try:
        if os.path.join(UTILS, "modcheck") not in sys.path:
            sys.path.insert(0, os.path.join(UTILS, "modcheck"))
        import status as _mc  # noqa: E402
        res["mod_hash"] = _mc.mod_hash(FW)
    except Exception as ex:  # noqa: BLE001 - recorded; validation.py then reads nothing from this result
        res["mod_hash"], res["mod_hash_error"] = None, repr(ex)
    env = res.setdefault("env", {})
    try:
        rm = call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
        env["running"] = [p.lower() for p in rm.get("packageIds") or []]
        ms = (rm.get("assembly") or {}).get("matches") or []
        env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
        if len(ms) != 1:
            env["assembly_why"] = "%d loaded assemblies match RimMandrakeFlowWorks" % len(ms)
    except Exception as ex:  # noqa: BLE001
        env["running"], env["assembly_sha256"], env["assembly_why"] = None, None, repr(ex)
    return res
