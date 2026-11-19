"""Phone push: one fixed-template alarm per incident, with no AI in the path (deadman_check, login_watch,
switching_plan call it). Its only route was a Todoist task due a minute out (token ~/.config/todoist/token, client
~/dev/PersonalComms/bin/todoist_api.py), and that route is RETIRED: owner, 2026-11-19, "So Todoist is officially retired
as any kind of alert: it just doesn't work in a timely manner. It's really only to maintain to do lists, as it says."
Those tasks never rang (no reminder attached, free plan; RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING).

So the default route sends nothing and attempts no HTTP call: send() returns False and records nothing, and route_off()
names why. RM_TODOIST_ALARM_POSTS=1 is the one setting that switches the Todoist post back on. Until the new alert
route is built (his open choice on that item), no alarm reaches the phone; each caller's alarm still goes to its own
log, alarms file and ledger. The in-session PushNotification tool exists but needs an AI in the loop, so it is not
this module's route.

One send per incident: a cause key (the alarm row key) that is already open sends nothing; it reopens only
after `close(key)` (the row went back to green). Emergency (red) only.
transport is injectable: transport(title, body) -> None; an explicit transport is not Todoist and always runs.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path

STATE = Path(os.environ.get("RM_PHONE_PUSH_STATE", os.path.expanduser("~/.local/state/rm-dashboard/phone_push.json")))
PERSONALCOMMS = os.path.expanduser("~/dev/PersonalComms/bin")


TODOIST_SETTING = "RM_TODOIST_ALARM_POSTS"


def todoist_posting() -> bool:
    """The Todoist post is off unless RM_TODOIST_ALARM_POSTS=1 (read at call time)."""
    return os.environ.get(TODOIST_SETTING) == "1"


def route_off() -> str | None:
    """-> why the default phone route sends nothing, or None while it is on."""
    if todoist_posting():
        return None
    return "Todoist retired as an alert route (owner, 2026-11-19); %s=1 turns it back on" % TODOIST_SETTING


def todoist_transport(title: str, body: str) -> None:
    sys.path.insert(0, PERSONALCOMMS)
    import todoist_api as td
    api = td.Todoist()
    proj = api.project("Inbox")
    due = (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    api._request("POST", "/tasks", body={"content": title, "description": body, "project_id": proj["id"],
                                         "priority": 4, "due_datetime": due})


def _load() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def _save(d: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d))


def send(row: dict, transport=None, label: str = "") -> bool:
    """True if a message went out. Same open key sends nothing."""
    key = row.get("key", "?")
    if row.get("kind") != "red":
        return False
    if transport is None and not todoist_posting():
        return False
    st = _load()
    if key in st:
        return False
    title = row.get("title") or f"{label}RimMandrake: {row.get('label') or key} is red"
    body = f"{row.get('detail') or row.get('text') or ''}".strip() or f"pulse row {key} turned red"
    (transport or todoist_transport)(title, body)
    st[key] = _dt.datetime.now().isoformat(timespec="seconds")
    _save(st)
    return True


def close(key: str) -> None:
    st = _load()
    if st.pop(key, None) is not None:
        _save(st)
