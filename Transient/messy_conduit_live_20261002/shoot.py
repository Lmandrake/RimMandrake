"""One-off: frame + screenshot the Messy Conduit live scene (validation.py's scene). python.exe only."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "RimMandrake", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw, check=False) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
cmd = sys.argv[1]
if cmd == "info":
    print(json.dumps(call("jawa/time_clock"))[:600]); print(json.dumps(call("rimworld/get_camera_state"))[:400])
elif cmd == "call":
    out = json.dumps(call(sys.argv[2], **json.loads(sys.argv[3])))
    print(out if len(sys.argv) > 4 else out[:1500])
elif cmd == "shot":
    x, z, root, name = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    call("jawa/clear_ui", all=True)
    call("rimworld/set_camera_zoom", rootSize=root)
    time.sleep(1.0)
    call("rimworld/jump_camera_to_cell", x=int(x), z=int(z))
    time.sleep(2.5)
    print(json.dumps(call("rimworld/get_camera_state").get("rootSize")))
    print(json.dumps(call("jawa/take_screenshot", fileName=name))[:600])
