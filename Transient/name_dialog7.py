import sys, json, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lay = rb.call("rimworld/get_ui_layout", {})
    s = json.dumps(lay)
    i = s.find("NamePlayerGravship")
    chunk = s[i:i+4000]
    for m in re.finditer(r'"targetId":\s*"(ui-element:[^"]+)"[^}]*?"kind":\s*"(\w+)"[^}]*?"label":\s*(null|"[^"]*")[^}]*?"valueText":\s*(null|"[^"]*")[^}]*?"actionable":\s*(\w+)', chunk):
        print(m.group(1), m.group(2), "label:", m.group(3)[:40], "value:", m.group(4)[:30], "actionable:", m.group(5))
