"""Provenance for the standalone live drivers (thirst_live.py, sprinkler_live.py): what validation.py's driver_rows_at needs
before it will read a result -- mode 'live', the mod, the mod hash of the repo tree at run start (modcheck status.mod_hash,
the same hash `modcheck record` checks) and what the GAME is running: the live mod list and the sha256 of the FlowWorks
assembly it loaded (jawa/type_probe; None unless the loaded MVID matches the file on disk). The repo hash alone cannot say
the deployed DLL is the repo's: a run against an undeployed fix would otherwise certify that fix. Never raises; a field it
cannot read is None with the reason beside it."""
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
    except Exception as ex:  # noqa: BLE001
        env["running"], env["running_why"] = None, repr(ex)
    # the sha256 both tools report is of the file on disk NOW; only mvidMatchesFile says the process loaded that file
    # (a redeploy after launch changes the file, not the loaded code) -- the validation_v2 assembly_identity rule
    env["assembly_sha256"] = None
    try:
        tp = call("jawa/type_probe", typeName="RimMandrake.FlowWorks.RM_MapComponent_Excavation") or {}
        if tp.get("mvidMatchesFile") is True and tp.get("assemblyFileSha256"):
            env["assembly_sha256"] = tp["assemblyFileSha256"]
        else:
            env["assembly_why"] = "type_probe: mvidMatchesFile=%r sha=%r error=%r" % (
                tp.get("mvidMatchesFile"), tp.get("assemblyFileSha256"), tp.get("identityError"))
    except Exception as ex:  # noqa: BLE001
        env["assembly_why"] = repr(ex)
    return res
