import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status")
    s = st.get("state", {})
    print("STATE:", s.get("programState"), "entry:", s.get("inEntryScene"))

    got = None
    for args in (
        {"defType": "VBE.BackgroundImageDef", "defNames": ["RUT_BG_ShellIshkoGate"]},
        {"defType": "BackgroundImageDef", "defNames": ["RUT_BG_ShellIshkoGate"]},
        {"defType": "VBE.BackgroundImageDef", "defName": "RUT_BG_ShellIshkoGate"},
    ):
        try:
            r = rb.call("jawa/get_defs", args)
            txt = json.dumps(r)
            print("get_defs", list(args.values())[0], "->", txt[:300])
            if "RUT_BG_ShellIshkoGate" in txt and "error" not in txt.lower()[:80]:
                got = True
                break
        except Exception as e:
            print("get_defs attempt failed:", str(e)[:120])
    print("DEF_PRESENT:", "MEASURED yes" if got else "UNMEASURED (see raw above)")

    try:
        shot = rb.call("rimworld/take_screenshot", {})
        print("SCREENSHOT:", json.dumps(shot)[:400])
    except Exception as e:
        print("screenshot failed:", str(e)[:150])
