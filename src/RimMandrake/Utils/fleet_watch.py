#!/usr/bin/env python3
"""fleet_watch.py — what every detached helper is doing right now, as JSON rows for the owner's Fleet Watch board.

One row per detached helper run (dispatcher/detached/*.json) started within --hours: unit alive or not, elapsed,
the helper's latest tool call and latest words (from its own transcript), its tool-call count, commits on
origin/main whose subject names its item, and its item's ledger state. The Conductor writes these rows to the
board's `parts` collection; the page renders them live.

    python3 src/RimMandrake/Utils/fleet_watch.py [--hours 12] [--fetch]
"""
import argparse
import glob
import json
import os
import re
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DETACHED = "/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached"
PROJECTS = os.path.expanduser("~/.claude/projects")


def sh(*a, cwd=REPO):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True).stdout.strip()


def project_dir(clone):
    return os.path.join(PROJECTS, re.sub(r"[^A-Za-z0-9]", "-", clone))


def latest_transcript(clone):
    fs = glob.glob(os.path.join(project_dir(clone), "*.jsonl"))
    return max(fs, key=os.path.getmtime) if fs else None


def short(s, n=160):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def read_transcript(path):
    """-> (tool_calls, last_tool, last_words, last_at) from a Claude transcript; tolerant of a torn tail."""
    calls, last_tool, last_words, last_at = 0, "", "", 0.0
    try:
        with open(path, "rb") as f:
            lines = f.read().replace(b"\0", b"").splitlines()
    except OSError:
        return calls, last_tool, last_words, last_at
    for raw in lines:
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        msg = e.get("message") or {}
        if e.get("type") != "assistant" or not isinstance(msg.get("content"), list):
            continue
        for c in msg["content"]:
            if c.get("type") == "tool_use":
                calls += 1
                inp = c.get("input") or {}
                what = inp.get("description") or inp.get("command") or inp.get("file_path") or inp.get("pattern") or ""
                last_tool = short("%s: %s" % (c.get("name"), what))
            elif c.get("type") == "text" and c.get("text", "").strip():
                last_words = short(c["text"], 240)
        last_at = os.path.getmtime(path)
    return calls, last_tool, last_words, last_at


def unit_state(unit):
    return sh("systemctl", "--user", "is-active", unit) or "unknown"


def item_state(item):
    out = sh("python3", "src/RimMandrake/rimflow/cli.py", "show", item)
    first = out.splitlines()[0] if out else ""
    m = re.match(r"\S+\s+(\S+)", first)
    return m.group(1) if m else "unknown"


def commits(item, since):
    out = sh("git", "log", "origin/main", "--since=@%d" % int(since), "--format=%h %s", "-F", "--grep=" + item)
    return [l for l in out.splitlines() if l]


def rows(hours):
    now = time.time()
    out = []
    for p in sorted(glob.glob(os.path.join(DETACHED, "*.json"))):
        if p.endswith(".out.json"):
            continue
        try:
            r = json.load(open(p))
        except (OSError, ValueError):
            continue
        if now - r.get("at", 0) > hours * 3600:
            continue
        live = unit_state(r["unit"])
        t = latest_transcript(r["clone"])
        calls, tool, words, last_at = read_transcript(t) if t else (0, "", "", 0.0)
        cs = commits(r["item"], r["at"])
        st = item_state(r["item"])
        if st in ("closed", "done", "implemented", "validated"):
            status = "Done"
        elif live in ("active", "activating"):
            status = "Building"
        else:
            status = "Stopped" if not cs else "Ended"
        out.append({
            "id": r["unit"][-40:],
            "item": r["item"],
            "model": r.get("model", ""),
            "status": status,
            "unit": live,
            "item_state": st,
            "started": int(r["at"]),
            "elapsed_min": int((now - r["at"]) / 60),
            "tool_calls": calls,
            "now": tool,
            "said": words,
            "last_activity": int(last_at) if last_at else None,
            "commits": cs[:8],
            "commit_count": len(cs),
        })
    return out


RELENTLESS_ITEMS = os.path.expanduser("~/rm/relentless/store/items")


def relentless_rows():
    """One row per Relentless worker or blind checker whose unit is alive right now."""
    now = time.time()
    out = []
    for p in glob.glob(os.path.join(RELENTLESS_ITEMS, "*", "state.json")):
        try:
            s = json.load(open(p))
        except (OSError, ValueError):
            continue
        for phase, rec, clone in (("worker", s.get("run"), s.get("clone")),
                                  ("blind check", s.get("check"), (s.get("check") or {}).get("clone"))):
            if not isinstance(rec, dict) or not rec.get("unit"):
                continue
            if unit_state(rec["unit"]) not in ("active", "activating"):
                continue
            t = latest_transcript(clone) if clone else None
            calls, tool, words, last_at = read_transcript(t) if t else (0, "", "", 0.0)
            item = s.get("item") or os.path.basename(os.path.dirname(p))
            out.append({
                "id": rec["unit"][-40:],
                "item": item,
                "title": "Relentless %s: %s" % (phase, item),
                "model": "relentless gen %s, attempt %s" % (s.get("gen"), s.get("attempts")),
                "status": "Checking" if phase == "blind check" else "Building",
                "unit": "active",
                "item_state": "doing",
                "started": int(rec.get("at") or now),
                "elapsed_min": int((now - (rec.get("at") or now)) / 60),
                "tool_calls": calls,
                "now": tool,
                "said": words,
                "last_activity": int(last_at) if last_at else None,
                "commits": [],
                "commit_count": 0,
                "relentless": True,
            })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--fetch", action="store_true", help="git fetch origin first")
    ap.add_argument("--titles", help="JSON {item: plain title} merged into each row")
    ap.add_argument("--out-dir", help="also write one <item>.json per row here (for ArtifactData file_path writes)")
    a = ap.parse_args()
    if a.fetch:
        sh("git", "fetch", "-q", "origin")
    titles = json.load(open(a.titles)) if a.titles else {}
    rs = rows(a.hours)
    for r in rs:
        r["title"] = titles.get(r["item"], r["item"])
    rs = relentless_rows() + rs
    for i, r in enumerate(rs):
        r["order"] = i
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
        for r in rs:
            with open(os.path.join(a.out_dir, r["item"] + ".json"), "w") as f:
                json.dump(r, f)
    print(json.dumps({"at": int(time.time()), "rows": rs}, indent=1))


if __name__ == "__main__":
    main()
