"""cap.py -- live hose proof captures (BENCH helper, 2026-10-22). python.exe, repo root.
    python.exe Transient/pile_2026-10-22/live_hose_proof/cap.py census OUT.json      # HoseProbe census of the current map
    python.exe Transient/pile_2026-10-22/live_hose_proof/cap.py shots LIST.txt         # lines: name cx cz rootSize
Each shot: jump camera, zoom, clear UI, take_screenshot; prints 'name cx cz rs path'. Read-only (camera only)."""
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

        def hose(cmd, wait=30.0):
            before = call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value")
            call("jawa/mod_settings_field", typeName=HP, action="set", field="request", value=cmd)
            t0 = time.time()
            while time.time() - t0 < wait:
                if call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value") != before:
                    return str(call("jawa/mod_settings_field", typeName=HP, action="get", field="result").get("value"))
                time.sleep(0.25)
            return '{"timeout":true}'

        if a[0] == "census":
            s = hose("census")
            open(a[1], "w", encoding="utf-8").write(s)
            print(a[1], len(s))
        elif a[0] == "shots":
            for line in open(a[1], encoding="utf-8"):
                q = line.split()
                if len(q) < 4 or q[0].startswith("#"):
                    continue
                name, x, z, rs = q[0], float(q[1]), float(q[2]), float(q[3])
                call("rimworld/jump_camera_to_cell", x=int(round(x)), z=int(round(z)))
                call("rimworld/set_camera_zoom", rootSize=rs)
                call("jawa/clear_ui")
                time.sleep(2.0)
                s = call("jawa/take_screenshot", fileName=name)
                fp = s.get("filePath") or ""
                for _ in range(40):
                    if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
                        break
                    time.sleep(0.25)
                print(name, int(round(x)), int(round(z)), rs, fp or json.dumps(s)[:200], flush=True)


if __name__ == "__main__":
    main()
