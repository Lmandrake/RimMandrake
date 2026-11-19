"""Phone push: one send per incident, red only, reopens after close, transport stubbed. Todoist posting is OFF by
default (owner, 2026-11-19: Todoist is retired as an alert route): no transport given and RM_TODOIST_ALARM_POSTS unset
means no HTTP call to Todoist is attempted at all."""
import os, sys, tempfile, types, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["RM_PHONE_PUSH_STATE"] = os.path.join(tempfile.mkdtemp(), "pp.json")
os.environ.pop("RM_TODOIST_ALARM_POSTS", None)
import phone_push as pp  # noqa: E402

sent = []
t = lambda title, body: sent.append((title, body))
red = {"key": "disk", "kind": "red", "label": "Disk"}
assert pp.send(red, t) is True and len(sent) == 1
assert pp.send(red, t) is False and len(sent) == 1, "same incident rang twice"
assert pp.send({"key": "x", "kind": "amber"}, t) is False
assert pp.send({"key": "tps", "kind": "red"}, t) is True and len(sent) == 2
pp.close("disk")
assert pp.send(red, t) is True and len(sent) == 3, "relapse after recovery must ring"

# Todoist retired: the default route attempts no HTTP call (a fake todoist_api and urlopen record any attempt).
calls = []


class _Api:
    def __init__(self, *a, **k):
        calls.append("todoist_api.Todoist()")

    def __getattr__(self, name):
        calls.append("todoist_api." + name)
        raise AssertionError("Todoist touched: " + name)


sys.modules["todoist_api"] = types.SimpleNamespace(Todoist=_Api)
_urlopen = urllib.request.urlopen
urllib.request.urlopen = lambda *a, **k: calls.append(("urlopen", a)) or (_ for _ in ()).throw(AssertionError("HTTP"))
try:
    fresh = {"key": "todoist-off", "kind": "red", "label": "Off"}
    assert pp.todoist_posting() is False, "Todoist posting must default off"
    assert pp.send(fresh) is False, "with Todoist off nothing goes out, so send reports False"
    assert calls == [], "an HTTP call to Todoist was attempted: %r" % calls
    assert "todoist-off" not in pp._load(), "an unsent alarm must not be recorded as sent"
    assert pp.route_off(), "route_off names why the phone route is off"
    os.environ["RM_TODOIST_ALARM_POSTS"] = "1"
    assert pp.todoist_posting() is True and pp.route_off() is None, "the one setting turns it back on"
    try:
        pp.send(fresh)
    except AssertionError:
        pass
    assert calls and calls[0] == "todoist_api.Todoist()", "with the setting on the Todoist route is used: %r" % calls
finally:
    os.environ.pop("RM_TODOIST_ALARM_POSTS", None)
    urllib.request.urlopen = _urlopen
    sys.modules.pop("todoist_api", None)
print("selftest_phone_push OK")
