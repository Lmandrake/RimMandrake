"""Shared reader for the SteveDesktop study. Reads the lane's own records only. Window: 21 days to END (UTC)."""
import glob, json, os
from datetime import datetime, timedelta, timezone
Q = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
END = datetime(2026, 11, 24, 4, 30, tzinfo=timezone.utc)      # Mon 2026-11-23 8:30 PM PST
DAYS = int(os.environ.get("CENSUS_DAYS", "21"))
START = END - timedelta(days=DAYS)


def ts(s):
    if not s:
        return None
    t = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def records(states=("done", "quarantined")):
    """-> (list of records in the window, unreadable file names). Never drops an unreadable record silently."""
    out, bad = [], []
    for st in states:
        for f in glob.glob(os.path.join(Q, st, "*.json")):
            try:
                d = json.load(open(f, encoding="utf-8"))
                fin = ts(d.get("finished") or d.get("at") or (d.get("result") or {}).get("finished"))
                sub = ts((d.get("job") or {}).get("submitted"))
            except (OSError, ValueError, AttributeError) as e:
                bad.append((st, os.path.basename(f), str(e)[:60]))
                continue
            when = fin or sub
            if when is None:
                bad.append((st, os.path.basename(f), "no time"))
            elif START <= when <= END:
                d["_state"], d["_fin"], d["_sub"], d["_file"] = st, fin, sub, f
                out.append(d)
    out.sort(key=lambda d: d["_fin"] or d["_sub"])
    return out, bad
