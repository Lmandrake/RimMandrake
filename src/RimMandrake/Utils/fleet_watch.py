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
    """-> (tool_calls, activity, last_words, last_at) from a Claude transcript; tolerant of a torn tail.
    `activity` is a plain verb phrase ("running selftests", "editing relentless.py") or "" — never a command."""
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
                last_tool = activity(c.get("name"), c.get("input") or {})
            elif c.get("type") == "text" and c.get("text", "").strip():
                last_words = plain_said(c["text"])
        last_at = os.path.getmtime(path)
    return calls, last_tool, last_words, last_at


# ---- plain-words derivations for the owner's phone (FLEETWATCH_PAGE_SHRINK_LESS_BASH_MORE_MODS) ----------------------
# His card: no shell commands anywhere on the page; a short readable title; a second line only when stuck.

UPPER_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
PATHLIKE = re.compile(r"(?:[\w.~-]*/)+([\w.-]+)")
SHELLISH = re.compile(r"`|\|\||&&|\$\(|\s--?\w|[|;<>{}]|\bpython3?\b|\bgit\s|\bsudo\b|\bcd\s")
DOUBLE = {"run", "set", "get", "stop", "drop", "map", "plan", "grep", "ship", "pin", "cut", "put", "dig", "tag", "log",
          "chop", "swap", "trim", "skim", "scan", "spot", "strip", "wrap", "zip", "step", "prep", "fit", "split", "commit"}
KEEP_E = {"see", "free", "agree", "be"}


def ing(verb):
    v = verb.lower()
    if v.endswith("ing") and len(v) > 4:
        return v
    if v in DOUBLE:
        return v + v[-1] + "ing"
    if v.endswith("ie"):
        return v[:-2] + "ying"
    if v.endswith("e") and v not in KEEP_E:
        return v[:-1] + "ing"
    return v + "ing"


def de_id(text):
    """UPPER_SNAKE ids -> 'Upper snake' words; paths -> their basename."""
    text = PATHLIKE.sub(lambda m: m.group(1), text)
    return UPPER_ID.sub(lambda m: re.sub(r"_\d+$", "", m.group(0)).replace("_", " ").capitalize(), text)


GENERIC_HEADS = {"experiment", "question", "investigate", "investigation", "research", "follow-up", "followup",
                 "proposal", "decision", "cleanup", "regression", "feature", "finding", "harness"}


def title_short(title, n=28):
    """A rimflow title -> at most n readable chars: the head before the first ':', ' — ', '(' or ';' when that head is
    a phrase of its own, ids made words, cut at a word with '…'."""
    t = " ".join(str(title or "").split())
    t = re.sub(r"^(?:\[[A-Za-z -]{2,12}\]\s*)+", "", t)
    t = re.sub(r"^(?:Ops alarm|alarm|FINDING|finding|BUG|bug|MOD|SITE|HARNESS)(?:\s*:\s*|\s+)", "", t)
    if re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+", t):  # a bare snake_case name: make it words
        t = t.replace("_", " ").capitalize()
    parts = re.split(r"\s*(?::\s|\s[—–-]{1,2}\s|\(|;)\s*", t, maxsplit=1)
    if len(parts) == 2 and parts[0].lower() in GENERIC_HEADS:  # "Experiment: can we ..." -> "Can we ..."
        t = parts[1][:1].upper() + parts[1][1:]
        parts = re.split(r"\s*(?::\s|\s[—–-]{1,2}\s|\(|;)\s*", t, maxsplit=1)
    head = parts[0]
    if len(head) >= 8 and (" " in head or len(parts) == 1):  # a lone path/token head says nothing: keep the rest
        t = head
    t = de_id(t).strip(" .,:;-")
    if len(t) <= n:
        return t
    cut = t[: n - 1]
    if t[n - 1] != " " and " " in cut[n // 2:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,.:;-") + "…"


def _base(path):
    return os.path.basename(str(path).rstrip("/")) or str(path)


def _from_command(cmd):
    c = " ".join(str(cmd).split())
    rules = ((r"run_selftests|selftest_\w+\.py|pytest", "running selftests"), (r"\./publish|land\.sh", "publishing"),
             (r"git commit", "committing"), (r"git (?:log|show|diff|status|blame)", "reading git history"),
             (r"\bgit\b", "using git"), (r"winbuild|dotnet build|msbuild", "building the DLL"),
             (r"deploy_custom_mods", "deploying a mod"), (r"rimflow|cli\.py (?:show|note|close|file)", "updating the ledger"),
             (r"code_review_status", "marking code reviewed"), (r"modcheck", "running a mod check"),
             (r"Player\.log", "reading Player.log"), (r"\b(?:grep|rg|find)\b", "searching files"),
             (r"\bsleep\b|until ", "waiting"))
    for pat, phrase in rules:
        if re.search(pat, c):
            return phrase
    m = re.match(r"(?:\S+=\S+\s+)*(?:timeout\s+\d+\s+)?(?:cat|head|tail|sed -n \S+|less|wc(?: -\w)?)\s+(\S+)", c)
    if m:
        return "reading " + _base(m.group(1))
    m = re.search(r"python3?\s+(?:-\w\s+)*(\S+\.py)", c)
    if m:
        return "running " + _base(m.group(1))
    return ""


def activity(name, inp):
    """A tool call -> a plain verb phrase, or "" when there is nothing plain to say. Never echoes a command."""
    inp = inp if isinstance(inp, dict) else {}
    name = str(name or "")
    if name == "Bash":
        d = " ".join(str(inp.get("description") or "").split())
        if d and not SHELLISH.search(d):
            w = d.split(" ", 1)
            d = de_id(ing(w[0]) + (" " + w[1] if len(w) > 1 else ""))
            return d if len(d) <= 48 else d[:47].rsplit(" ", 1)[0] + "…"
        return _from_command(inp.get("command") or "")
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    simple = {"Read": "reading", "Edit": "editing", "Write": "writing", "NotebookEdit": "editing"}
    if name in simple:
        return "%s %s" % (simple[name], _base(path)) if path else simple[name] + " a file"
    table = {"Grep": "searching files", "Glob": "searching files", "WebFetch": "reading the web",
             "WebSearch": "searching the web", "Task": "briefing a helper", "Agent": "briefing a helper",
             "ArtifactData": "updating a board", "Artifact": "updating a page", "TodoWrite": "planning",
             "ToolSearch": "loading tools", "SendMessage": "messaging another agent"}
    if name in table:
        return table[name]
    if name == "Skill":
        return "reading the %s guide" % str(inp.get("skill") or "").split(":")[-1] if inp.get("skill") else "reading a guide"
    if name.startswith("mcp__"):
        return "using " + name.split("__")[1].replace("_", " ").replace("-", " ")
    return ""


def plain_said(text, n=140):
    """Last words, one line, with commands and code spans removed; "" if nothing plain is left."""
    t = re.sub(r"```.*?```", " ", str(text), flags=re.S)
    t = re.sub(r"`[^`]*`", "", t)
    t = de_id(" ".join(t.split()))
    t = re.sub(r"\s+([,.;:])", r"\1", t).strip()
    if not t or SHELLISH.search(t[:60]) and len(t) < 30:
        return ""
    return short(t, n)


SILENT_MIN = 10


def stuck(row, now, circling=None):
    """-> "" or a plain reason a live row is stuck: silent for SILENT_MIN+ minutes, or circling (Relentless saw the tree
    unchanged). Finished rows are never stuck."""
    if row.get("status") not in ("Building", "Checking"):
        return ""
    if circling:
        return "circling: " + de_id(str(circling))
    last = row.get("last_activity") or row.get("started") or now
    if now - last >= SILENT_MIN * 60:
        return "silent %dm" % int((now - last) / 60)
    return ""


GLYPH = {"Building": "▶", "Checking": "◎", "Done": "✓", "Ended": "■", "Stopped": "✗", "Failed": "✗", "Queued": "…"}


def unit_state(unit):
    return sh("systemctl", "--user", "is-active", unit) or "unknown"


def item_state(item):
    out = sh("python3", "src/RimMandrake/rimflow/cli.py", "show", item)
    first = out.splitlines()[0] if out else ""
    m = re.match(r"\S+\s+(\S+)", first)
    return m.group(1) if m else "unknown"


LEDGER_ONLY = re.compile(r"^(?:infrastructure/state/ledger/|conversations/|infrastructure/state/code_review/)")


def real_count(log_text):
    """`git log --format=@@%h --name-only` text -> commits that changed something besides the ledger and its echoes."""
    n, files = 0, None
    for line in log_text.splitlines() + ["@@end"]:
        if line.startswith("@@"):
            if files is not None and any(not LEDGER_ONLY.match(f) for f in files):
                n += 1
            files = []
        elif line.strip() and files is not None:
            files.append(line.strip())
    return n


def commits(item, since):
    """-> number of real commits on origin/main since `since` whose message names `item` (ledger-only excluded)."""
    out = sh("git", "log", "origin/main", "--since=@%d" % int(since), "--format=@@%h", "--name-only", "-F",
             "--grep=" + item)
    return real_count(out)


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
        row = {
            "id": r["unit"][-40:],
            "item": r["item"],
            "model": "" if r.get("model", "") in ("", "opus", "default") else r["model"],
            "status": status,
            "glyph": GLYPH.get(status, "·"),
            "unit": live,
            "item_state": st,
            "started": int(r["at"]),
            "elapsed_min": int((now - r["at"]) / 60),
            "tool_calls": calls,
            "now": tool,
            "said": words,
            "last_activity": int(last_at) if last_at else None,
            "commit_count": cs,
            "tokens": detached_tokens(r.get("out")),
        }
        row["stuck"] = stuck(row, now)
        if status != "Building":
            try:
                row["finished_at"] = int(os.path.getmtime(r["out"]))
            except (OSError, KeyError, TypeError):
                row["finished_at"] = int(last_at or r["at"])
        out.append(row)
    return out


RELENTLESS_ITEMS = os.path.expanduser("~/rm/relentless/store/items")
CIRCLING_FRESH_S = 45 * 60


def detached_tokens(out_path):
    """A finished detached helper's `claude -p --output-format json` result -> total tokens, or None (UNMEASURED)."""
    try:
        with open(out_path) as f:
            u = (json.load(f) or {}).get("usage") or {}
    except (OSError, ValueError, TypeError, AttributeError):
        return None
    n = sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                                          "cache_read_input_tokens"))
    return n or None


def circling_now(item_dir, gen, now):
    """The latest fresh circling HIT for this item's current gen, else "". Hits live in the store-level circling.jsonl
    ({item, gen, kind, reading, at}); the per-item file is only tree samples (hashes), never a verdict."""
    item = os.path.basename(item_dir.rstrip("/"))
    path = os.path.join(os.path.dirname(os.path.dirname(item_dir.rstrip("/"))), "circling.jsonl")
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 200000))
            lines = f.read().splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            c = json.loads(line)
        except ValueError:
            continue
        if not isinstance(c, dict) or c.get("item") != item or c.get("gen") != gen:
            continue
        if now - (c.get("at") or 0) > CIRCLING_FRESH_S:
            return ""
        return c.get("reading") or str(c.get("kind") or "").replace("_", " ")
    return ""


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
            status = "Checking" if phase == "blind check" else "Building"
            row = {
                "id": rec["unit"][-40:],
                "item": item,
                "title": item,
                "phase": phase,
                "model": "",
                "ga": "g%s·a%s" % (s.get("gen"), s.get("attempts")),
                "status": status,
                "glyph": GLYPH[status],
                "unit": "active",
                "item_state": "doing",
                "started": int(rec.get("at") or now),
                "elapsed_min": int((now - (rec.get("at") or now)) / 60),
                "tool_calls": calls,
                "now": tool,
                "said": words,
                "last_activity": int(last_at) if last_at else None,
                "commit_count": commits(item, s.get("enrolled_at") or rec.get("at") or now),
                "tokens": s.get("spent") or None,
                "relentless": True,
            }
            row["stuck"] = stuck(row, now, circling_now(os.path.dirname(p), s.get("gen"), now))
            out.append(row)
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
    for r in rs:
        r["short"] = title_short(r["title"])
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
