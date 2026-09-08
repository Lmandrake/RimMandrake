import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
lay = call("rimworld/get_ui_layout")
s = json.dumps(lay, default=str)
i = s.find('"OK"')
print("layout has OK at", i, ":", s[max(0,i-300):i+120] if i>=0 else s[:600])
print(json.dumps(call("rimworld/click_ui_target", targetId="ui-element:1:4:10"), default=str)[:400])
