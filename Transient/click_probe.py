import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try: rb.call("rimworld/click_cell", {"zzz": 1})
    except Exception as e: print("click_cell:", str(e).split("Declared:")[-1].strip())
    # try engine cell with jump + slight settle + click
    rb.call("rimworld/jump_camera_to_cell", {"x": 187, "z": 150})
    time.sleep(0.8)
    c = rb.call("rimworld/click_cell", {"x": 187, "z": 150})
    time.sleep(0.5)
    s = rb.call("rimworld/get_selection_semantics", {})
    print("engine click ->", s.get("hasSelection"), s.get("selectedKinds"))
