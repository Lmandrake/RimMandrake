"""Phone push: one send per incident, red only, reopens after close, transport stubbed."""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["RM_PHONE_PUSH_STATE"] = os.path.join(tempfile.mkdtemp(), "pp.json")
import phone_push as pp  # noqa: E402
import pulse  # noqa: E402

sent = []
t = lambda title, body: sent.append((title, body))
red = {"key": "disk", "kind": "red", "label": "Disk"}
assert pp.send(red, t) is True and len(sent) == 1
assert pp.send(red, t) is False and len(sent) == 1, "same incident rang twice"
assert pp.send({"key": "x", "kind": "amber"}, t) is False
assert pp.send({"key": "tps", "kind": "red"}, t) is True and len(sent) == 2
pp.close("disk")
assert pp.send(red, t) is True and len(sent) == 3, "relapse after recovery must ring"
assert pulse.PHONE_PUSH_ENABLED is True
print("selftest_phone_push OK")
