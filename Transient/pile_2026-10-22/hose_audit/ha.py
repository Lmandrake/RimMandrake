"""ha.py -- hose audit helper (BENCH, 2026-10-22). Run from the repo root with python.exe:
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py maps
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py usemap <mapId>
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py census
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py hose "<probe verb>"
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py things x z w h [defSubstr]
    python.exe Transient/pile_2026-10-22/hose_audit/ha.py shoot <name> cx cz rootSize
Read-only except usemap / camera moves. Never saves.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

HP = "RimMandrake.FlowWorks.Hose.HoseProbe"


def main():
    a = sys.argv[1:]
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t) as B:
        def call(n, **kw):
            try:
                return B.call(n, kw) or {}
            except Exception as e:  # noqa
                return {"success": False, "error": str(e)[:300]}

        def hose(cmd, wait=20.0):
            before = call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value")
            call("jawa/mod_settings_field", typeName=HP, action="set", field="request", value=cmd)
            t0 = time.time()
            while time.time() - t0 < wait:
                if call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value") != before:
                    return str(call("jawa/mod_settings_field", typeName=HP, action="get", field="result").get("value"))
                time.sleep(0.25)
            return '{"timeout":true}'

        v = a[0]
        if v == "maps":
            print(json.dumps(call("rimworld/get_game_info"), default=str)[:3000])
            print(json.dumps(call("rimworld/get_camera_state"), default=str)[:800])
        elif v == "usemap":
            print(json.dumps(call("jawa/set_current_map", mapId=int(a[1])), default=str)[:500])
        elif v == "census":
            print(hose("census"))
        elif v == "hose":
            print(hose(a[1]))
        elif v == "things":
            x, z, w, hh = (int(q) for q in a[1:5])
            sub = a[5] if len(a) > 5 else ""
            r = call("jawa/list_things", rect="%d,%d,%d,%d" % (x, z, w, hh), limit=2000)
            for th in r.get("things") or []:
                d = th.get("defName") or th.get("def") or str(th.get("id") or th.get("label") or "")
                if sub and sub.lower() not in d.lower():
                    continue
                print(d, th.get("x"), th.get("z"), th.get("rotation") or th.get("rot"), th.get("style") or "", th.get("id") or th.get("thingId") or "")
            if not r.get("things"):
                print(json.dumps(r, default=str)[:500])
        elif v == "shoot":
            name, x, z = a[1], int(a[2]), int(a[3])
            rs = float(a[4]) if len(a) > 4 else 11
            call("rimworld/jump_camera_to_cell", x=x, z=z)
            call("rimworld/set_camera_zoom", rootSize=rs)
            call("jawa/clear_ui")
            for _ in range(10):
                ws = call("jawa/window_list_close").get("windows") or []
                hit = [w for w in ws if w.get("forcePause")]
                if not hit:
                    break
                call("jawa/window_list_close", action="close", typeName=hit[0]["type"])
            time.sleep(2.5)
            cam = call("rimworld/get_camera_state")
            s = call("jawa/take_screenshot", fileName=name)
            fp = s.get("filePath") or ""
            for _ in range(40):
                if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
                    break
                time.sleep(0.25)
            print(json.dumps({"shot": fp or s, "cam": {k: cam.get(k) for k in ("viewRect", "mapId", "rootSize")}}, default=str))
        else:
            sys.exit("maps|usemap|census|hose|things|shoot")


if __name__ == "__main__":
    main()
