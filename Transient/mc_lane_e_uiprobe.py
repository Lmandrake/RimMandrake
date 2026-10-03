import sys, json
sys.path.insert(0, r"src/RimMandrake/Utils")
try:
    import rimbridge_client as rb
    h, p, t = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=t, timeout=20.0); S.connect()
    r = S.call("rimworld/get_ui_state", {}, check=False)
    txt = r["content"][0]["text"] if isinstance(r, dict) and r.get("content") else str(r)
    print("UP", str(txt)[:160].replace("\n"," "))
except Exception as e:
    print("DOWN", repr(e)[:120])
