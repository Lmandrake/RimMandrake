"""Phone push for RimPulse: a Todoist task with a due time a minute out, which the Todoist app he already has
rings on his phone. No install from him. Route chosen 2026-11-01 (no Remote Control push tool exists; Todoist
token at ~/.config/todoist/token, client ~/dev/PersonalComms/bin/todoist_api.py).

One send per incident: a cause key (the pulse row key) that is already open sends nothing; it reopens only
after `close(key)` (the row went back to green). Emergency (red) only; amber waits for the OP4 4 h rule.
transport is injectable: transport(title, body) -> None.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from pathlib import Path

STATE = Path(os.environ.get("RM_PHONE_PUSH_STATE", os.path.expanduser("~/.local/state/rm-dashboard/phone_push.json")))
PERSONALCOMMS = os.path.expanduser("~/dev/PersonalComms/bin")


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
    st = _load()
    if key in st:
        return False
    title = f"{label}RimMandrake: {row.get('label') or key} is red"
    body = f"{row.get('detail') or row.get('text') or ''}".strip() or f"pulse row {key} turned red"
    (transport or todoist_transport)(title, body)
    st[key] = _dt.datetime.now().isoformat(timespec="seconds")
    _save(st)
    return True


def close(key: str) -> None:
    st = _load()
    if st.pop(key, None) is not None:
        _save(st)
