import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

st = call("rimworld/get_ui_state")
print("ui_state:", st.get("programState"))

print(call("rimworld/open_window_by_type", windowType="aRandomKiwi.RimThemes.Dialog_ThemesList"))
time.sleep(0.5)

def find_target(label):
    layout = call("rimworld/get_ui_layout")
    els = layout["surfaces"][1]["elements"]
    for i, e in enumerate(els):
        if e.get("label") == label:
            return els[i + 2]["targetId"], els[i + 2]
    return None, None

# control test: try clicking "Vanilla" instead, to see if ANY selection can ever be
# made this way, or whether click_ui_target is broken against this dialog entirely.
tid, e = find_target("Vanilla")
print("Vanilla target:", tid, e.get("screenRect") if e else None)
r = call("rimworld/click_ui_target", targetId=tid, timeoutMs=1500)
print("Vanilla click result:", json.dumps(r)[:250])

call("rimworld/take_screenshot", fileName="rimthemes_after_vanilla_click.png")
print("screenshot taken")
