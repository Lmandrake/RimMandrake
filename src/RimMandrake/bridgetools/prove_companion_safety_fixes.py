#!/usr/bin/env python3
"""Live proof of the 2026-11-15 companion safety fixes (RIMMANDRAKE_DEPLOY_COMPANION_SAFETY_FIXES_FOUR_COMMITS_WAIT).

Run under Windows python.exe, after build.py --gm --apply and a restart, on a TEST-profile quicktest map (never a
campaign save; never a flyer). Every row is a refusal the new companion must give, so nothing is written:
  arg_guard_own_strict     bridge_arg_report reports ownStrict=true
  undeclared_key_refused   set_fog with an undeclared dry_run key errors instead of running (check=False skips
                           the client's own check, so the companion's refusal is what is measured)
  settings_set_non_modsettings_refused   mod_settings_field set on Verse.DebugSettings.godMode refuses "does not derive"
  settings_list_non_modsettings_reads    mod_settings_field list on Verse.DebugSettings succeeds (it threw before)
  terrain_batch_unknown_map_refused      set_terrain_batch mapId=999999 refuses "No loaded map"
  excavation_levels_capped               flowworks_excavation_drive deepenLevels=1000 refuses 0..64
  cache_range_capped                     world_cache_audit range 0-2147483647 lists a refusal, finishes
  framehist_json_parses                  health's frameHist parses as JSON
  profile_reads_save                     companion_handshake names the profile and why (informational)
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED (no bridge or no map).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

rows = []


def row(name, verdict, detail):
    rows.append((name, verdict))
    print("%-38s %-10s %s" % (name, verdict, str(detail)[:220]))


def main():
    host, port, token = rb.resolve_endpoint()
    if not token:
        print("UNMEASURED: no bridge token in Player.log")
        return 2
    S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
    S.connect()

    def call(tool, check=True, **p):
        try:
            r = S.call(tool, p, check=check) or {}
        except Exception as e:  # noqa: BLE001 - a refusal may arrive as a transport error; it is the reading
            return {"_error": "%s: %s" % (type(e).__name__, e)}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                pass
        return r if isinstance(r, dict) else {"_raw": r}

    hs = call("jawa/companion_handshake")
    row("profile_reads_save", "INFO", {k: hs.get(k) for k in ("profile", "profileWhy", "game")})
    mi = call("jawa/map_info")
    if not mi.get("success", True) or mi.get("_error"):
        print("UNMEASURED: no map (%s)" % mi)
        return 2

    r = call("jawa/bridge_arg_report")
    row("arg_guard_own_strict", "PASS" if r.get("ownStrict") is True and r.get("installed") else "FAIL", r.get("ownStrict"))

    r = call("jawa/set_fog", check=False, action="unfog", rect="0,0,1,1", dry_run=True)  # argcheck-ok
    txt = json.dumps(r)
    row("undeclared_key_refused", "PASS" if ("does not declare" in txt and r.get("success") is not True) else "FAIL", txt)

    # Verse.Prefs.DevMode is a PROPERTY, so it refused on "No public field" before the type check was reached. A real
    # public static field on a non-ModSettings type, set to its current value, reaches the check and changes nothing.
    r = call("jawa/mod_settings_field", typeName="Verse.DebugSettings", action="get", field="godMode")
    cur = str(r.get("value", "False")).lower()
    r = call("jawa/mod_settings_field", typeName="Verse.DebugSettings", action="set", field="godMode", value=cur)
    row("settings_set_non_modsettings_refused", "PASS" if r.get("success") is False and "does not derive" in json.dumps(r) else "FAIL", r)

    r = call("jawa/mod_settings_field", typeName="Verse.DebugSettings", action="list")
    row("settings_list_non_modsettings_reads", "PASS" if r.get("success") is True and r.get("count", 0) > 0 else "FAIL", r)

    r = call("jawa/set_terrain_batch", ops="Sand:0,0,1,1", mapId=999999)
    row("terrain_batch_unknown_map_refused", "PASS" if r.get("success") is False and "No loaded map" in json.dumps(r) else "FAIL", r)

    r = call("jawa/flowworks_excavation_drive", x=1, z=1, deepenLevels=1000)
    row("excavation_levels_capped", "PASS" if r.get("success") is False and "0..64" in json.dumps(r) else "FAIL", r)

    r = call("jawa/world_cache_audit", range="0-2147483647", limit=1)
    row("cache_range_capped", "PASS" if "more than 100000" in json.dumps(r) else "FAIL", {k: r.get(k) for k in ("success", "refused")})

    r = call("jawa/health")
    blob = json.dumps(r)
    ok = None
    for v in (r.get("frameHist"), (r.get("window") or {}).get("frameHist") if isinstance(r.get("window"), dict) else None):
        if isinstance(v, (dict, list)):
            ok = True
        elif isinstance(v, str):
            try:
                json.loads(v)
                ok = True
            except ValueError:
                ok = False
    row("framehist_json_parses", "PASS" if ok else ("UNMEASURED" if ok is None else "FAIL"),
        "frameHist found" if ok is not None else blob[:200])

    fails = [n for n, v in rows if v == "FAIL"]
    print("companion safety fixes: %d row(s), %d FAIL" % (len(rows), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
