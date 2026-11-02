#!/usr/bin/env python3
"""fleet_refresh.py — refresh the owner's Fleet Watch board with no Claude window open (rm-fleetwatch.timer).

Fleet Watch is the claude.ai artifact BOARD_URL (collections `parts`, `board`, `feed`). The Conductor window used to
refresh it from a session cron; that died with the window (FLEETWATCH_REFRESH_BUILD_OUTLIVES_ITS_WINDOW). Now:

  1. Python does everything deterministic: fleet_watch.py's rows, one <item>.json per row under STATE/rows, a feed
     line per status change since the last run, a facts list for the headline.
  2. Only the write goes through a model: one headless `claude -p` (alias `sonnet`, resolved from the environment;
     no account named here) whose tools are Artifact + ArtifactData only, told to make ONE ArtifactData batch call
     with our writes plus a board/summary `update` carrying its own short headline. `needs_you` is never touched —
     that field is a human-facing agent's to write.
  3. Success is the TOOL RESULT, not the model's words: the call's input is checked against our writes (every part
     and feed write present, unchanged) and its tool_result must not be an error.

WHY THE ENV. Headless ArtifactData is off by default ("sdk_default_off" in the CLI's gate) and a child of a Claude
session inherits CLAUDE_CODE_ENTRYPOINT=sdk-cli; so CLAUDE_CODE_ARTIFACT=1 is set and the entrypoint unset.
ENABLE_TOOL_SEARCH=false keeps ArtifactData loaded up front (one turn fewer). ArtifactData disappears if Artifact is
disallowed, so Artifact stays in. A `parts` write by file_path counts as a Read, so Read is allowed for the
rows dir alone. 

COST GATE. A run whose rows match the last written rows (ignoring elapsed minutes) skips the model unless the last
write is older than --heartbeat (20 min); so an idle fleet costs ~3 calls an hour and `updated` never ages past
the live promise's 30 min.

    python3 src/RimMandrake/Utils/fleet_refresh.py [--dry-run] [--force]

State, under the agent storage root (agent_storage.py): rimmandrake/fleetwatch/
    titles.json       {item: plain title} — the Conductor's edits win; else the ledger title; else the id
    rows/<item>.json  the row each `parts` write reads by file_path
    state.json        last statuses, row hash, last write epoch
    last_write.json   written only after a verified board write — the live promise's reading
    runs.jsonl        one line per run: outcome, tokens, cost
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fleet_watch  # noqa: E402

BOARD_URL = "https://claude.ai/artifact/PGnwP9teyQWPszjJzxJpr8"
HOURS = 3
HEARTBEAT = 20 * 60
VOLATILE = ("elapsed_min",)
DISALLOWED = ("Task,Agent,ArtifactComments,Bash,CronCreate,CronDelete,CronList,DesignSync,Edit,EnterWorktree,"
              "ExitWorktree,ListAgents,Monitor,NotebookEdit,PushNotification,RemoteTrigger,ReportFindings,"
              "ScheduleWakeup,SendMessage,Skill,TaskStop,ToolSearch,WebSearch,WebFetch,Workflow,Write,Glob,Grep,"
              "TodoWrite")
SYSTEM = ("You relay one write to a claude.ai artifact. Make exactly ONE ArtifactData call: action \"batch\", the url "
          "given, and the writes given, unchanged and in order, plus the one board write described. Then reply OK. "
          "Never read, list or make any other call.")


def storage_root():
    out = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                         capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("fleet_refresh: agent_storage.py gave no root: " + out.stderr.strip())
    return os.path.join(out.stdout.strip(), "rimmandrake", "fleetwatch")


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def ledger_title(item):
    lines = fleet_watch.sh("python3", "src/RimMandrake/rimflow/cli.py", "show", item).splitlines()
    return lines[1].strip() if len(lines) > 1 and not lines[0].endswith("never been filed.") else ""


def row_hash(rows):
    slim = [{k: v for k, v in r.items() if k not in VOLATILE} for r in rows]
    return hashlib.sha1(json.dumps(slim, sort_keys=True).encode()).hexdigest()


def plan(rows, prev, now, rows_dir):
    """Pure: -> (writes, facts, board_version, new_state). `prev` is state.json's content ({} on the first run).
    The board refuses an overwrite without `if_version`, so every write to a doc we know carries its version."""
    old, versions = prev.get("status", {}), prev.get("versions", {})
    writes, facts, changes = [], [], []
    for r in rows:
        w = {"op": "set", "collection": "parts", "doc_id": r["item"],
             "file_path": os.path.join(rows_dir, r["item"] + ".json")}
        if "parts/" + r["item"] in versions:
            w["if_version"] = versions["parts/" + r["item"]]
        writes.append(w)
        was = old.get(r["item"])
        if old and was != r["status"]:
            changes.append("%s: %s" % (r["title"], ("%s → %s" % (was, r["status"])) if was else "started (%s)" % r["status"]))
    for i, text in enumerate(changes):
        writes.append({"op": "set", "collection": "feed", "doc_id": "t%d-%d" % (now, i), "data": {"at": now, "text": text}})
    by = {}
    for r in rows:
        by.setdefault(r["status"], []).append(fleet_watch.short(r["title"], 90))
    for status in ("Building", "Checking", "Stopped", "Ended", "Done"):
        if by.get(status):
            facts.append("%s (%d): %s" % (status, len(by[status]), "; ".join(by[status][:6])))
    facts += ["changed since last refresh: " + c for c in changes]
    if not rows:
        facts.append("no detached helper has run in the last %d hours" % HOURS)
    state = {"status": {r["item"]: r["status"] for r in rows}, "hash": row_hash(rows),
             "last_write": prev.get("last_write", 0), "versions": dict(versions)}
    return writes, facts, versions.get("board/summary"), state


WROTE = re.compile(r'^- \w+ "([^"]+)"/"([^"]+)" \(version (\d+)\)', re.M)


def written_versions(text):
    """{collection/doc_id: version} from a batch result's lines: - set "parts"/"X" (version 3)"""
    return {"%s/%s" % (c, d): int(v) for c, d, v in WROTE.findall(text)}


def prompt(writes, facts, now, board_version):
    board = '{"op":"update","collection":"board","doc_id":"summary","data":{"headline":<HEADLINE>,"updated":%d}%s}' % (
        now, "" if board_version is None else ',"if_version":%d' % board_version)
    return ("url: %s\n\nwrites (pass these unchanged, in order):\n%s\n\nboard write to append last: %s\n"
            "HEADLINE: one plain sentence, at most 30 words, for the owner glancing at his phone: what is being built "
            "and what just finished, from these facts (titles as given, no item ids, no jargon):\n- %s\n"
            % (BOARD_URL, json.dumps(writes), board, "\n- ".join(facts)))


def run_claude(text, rows_dir, system=SYSTEM, timeout=240):
    # CLAUDE.md and the skills list ride in the first user message, so any change in our text re-cached ~8k tokens a
    # run: both off. MEASURED 2026-11-02, cache_create 8.65k -> 0.82k a run.
    env = dict(os.environ, CLAUDE_CODE_ARTIFACT="1", ENABLE_TOOL_SEARCH="false", CLAUDE_CODE_DISABLE_CLAUDE_MDS="1")
    for k in ("CLAUDE_CODE_ENTRYPOINT", "CLAUDECODE"):
        env.pop(k, None)
    cmd = ["claude", "-p", "--model", "sonnet", "--no-session-persistence", "--output-format", "stream-json",
           "--verbose", "--strict-mcp-config", "--setting-sources", "user", "--disable-slash-commands", "--system-prompt", system,
           "--disallowedTools", DISALLOWED,
           # a `parts` write by file_path is a Read: allowed for the rows dir only (// = an absolute path)
           "--allowedTools", "ArtifactData,Read(/%s/**)" % rows_dir]
    p = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=timeout, env=env, cwd="/tmp")
    with open("/tmp/rm-fleetwatch.last.jsonl", "w") as f:  # the last run's stream, for a FAILED line's post-mortem
        f.write(p.stdout + p.stderr)
    return p.stdout.splitlines()


def read_stream(lines):
    """-> (tool_use blocks, {tool_use_id: tool_result}, usage) from a stream-json run."""
    calls, results, usage, cost = [], {}, {}, None
    for l in lines:
        try:
            e = json.loads(l)
        except ValueError:
            continue
        if not isinstance(e, dict):
            continue
        msg = e.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if e.get("type") == "assistant" and isinstance(content, list):
            calls += [c for c in content if isinstance(c, dict) and c.get("type") == "tool_use"]
        elif e.get("type") == "user" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    results[c.get("tool_use_id")] = c
        elif e.get("type") == "result":
            usage, cost = e.get("usage") or {}, e.get("total_cost_usd")
    use = {"input": usage.get("input_tokens", 0), "cache_create": usage.get("cache_creation_input_tokens", 0),
           "cache_read": usage.get("cache_read_input_tokens", 0), "output": usage.get("output_tokens", 0), "usd": cost}
    return calls, results, use


def result_text(res):
    c = res.get("content")
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


def judge(lines, writes, board_version):
    """-> (ok, why, usage). ok only if exactly one ArtifactData batch carried every write of ours unchanged plus one
    well-formed board write, and its tool_result was not an error."""
    calls, results, use = read_stream(lines)
    batch = [c for c in calls if c.get("name") == "ArtifactData" and (c.get("input") or {}).get("action") == "batch"]
    if len(calls) != 1 or len(batch) != 1:
        return False, "expected one ArtifactData batch call, saw %s" % [c.get("name") for c in calls], use
    inp = batch[0]["input"]
    sent = inp.get("writes") or []
    if inp.get("url") != BOARD_URL:
        return False, "wrong url %r" % inp.get("url"), use
    if sent[:len(writes)] != writes:
        return False, "writes altered in relay", use
    extra = sent[len(writes):]
    if len(extra) != 1 or extra[0].get("collection") != "board" or extra[0].get("doc_id") != "summary" \
            or set((extra[0].get("data") or {})) != {"headline", "updated"} or extra[0].get("if_version") != board_version:
        return False, "board write malformed: %s" % json.dumps(extra)[:200], use
    res = results.get(batch[0].get("id"))
    if res is None:
        return False, "no tool_result", use
    if res.get("is_error"):
        return False, "tool error: %s" % result_text(res)[:300], use
    return True, (extra[0]["data"]["headline"], written_versions(result_text(res))), use


SYSTEM_LIST = "Make exactly the ArtifactData calls the user asks for, nothing else, then reply OK."


def parse_versions(calls, results):
    """{collection/doc_id: version} from `list` tool results (one JSON doc per line between the DB markers)."""
    out = {}
    for c in calls:
        inp = c.get("input") or {}
        res = results.get(c.get("id"))
        if c.get("name") != "ArtifactData" or inp.get("action") != "list" or res is None or res.get("is_error"):
            continue
        for line in result_text(res).splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if isinstance(d, dict) and "id" in d and "version" in d:
                out["%s/%s" % (inp.get("collection"), d["id"])] = d["version"]
    return out


def sync_versions(rows_dir):
    """One model call that lists `parts` and `board`; -> (versions or None, usage)."""
    lines = run_claude('url %s. Call ArtifactData action "list" on collection "parts", then action "list" on '
                       'collection "board". Then reply OK.' % BOARD_URL, rows_dir, system=SYSTEM_LIST)
    calls, results, use = read_stream(lines)
    v = parse_versions(calls, results)
    return (v if "board/summary" in v else None), use


def add_use(rec, use):
    for k, x in use.items():
        rec[k] = round((rec.get(k) or 0) + (x or 0), 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the prompt; no model call, no state change")
    ap.add_argument("--force", action="store_true", help="write even if nothing changed")
    ap.add_argument("--heartbeat", type=int, default=HEARTBEAT)
    a = ap.parse_args()
    root = storage_root()
    rows_dir = os.path.join(root, "rows")
    os.makedirs(rows_dir, exist_ok=True)
    now = int(time.time())
    fleet_watch.sh("git", "fetch", "-q", "origin")
    titles = load(os.path.join(root, "titles.json"), {})
    rows = fleet_watch.rows(HOURS)
    for r in rows:
        r["title"] = titles.get(r["item"]) or ledger_title(r["item"]) or r["item"]
    rel = fleet_watch.relentless_rows()
    for r in rel:  # "Relentless worker: <ID>" -> "Relentless worker: <plain title>"
        r["title"] = "%s: %s" % (r["title"].split(": ")[0], titles.get(r["item"]) or ledger_title(r["item"]) or r["item"])
    rows = rel + rows
    for i, r in enumerate(rows):
        r["order"] = i
    prev = load(os.path.join(root, "state.json"), {})
    writes, facts, board_version, state = plan(rows, prev, now, rows_dir)
    if a.dry_run:
        print(prompt(writes, facts, now, board_version))
        return 0
    rec = {"at": now, "rows": len(rows), "writes": len(writes)}
    if not a.force and state["hash"] == prev.get("hash") and now - prev.get("last_write", 0) < a.heartbeat:
        rec["outcome"] = "skipped: unchanged"
    else:
        for r in rows:
            dump(os.path.join(rows_dir, r["item"] + ".json"), r)
        ok, why = False, "versions unknown"
        for attempt in (1, 2):
            if attempt == 2 or "versions" not in prev:
                # first run, or someone else (the Conductor) wrote since: re-read every version, re-plan, retry once
                try:
                    v, use = sync_versions(rows_dir)
                except subprocess.TimeoutExpired:
                    v, use = None, {}
                add_use(rec, use)
                if v is None:
                    why = "version sync failed"
                    break
                prev = dict(prev, versions=v)
                writes, facts, board_version, state = plan(rows, prev, now, rows_dir)
            try:
                ok, why, use = judge(run_claude(prompt(writes, facts, now, board_version), rows_dir), writes, board_version)
            except subprocess.TimeoutExpired:
                ok, why, use = False, "claude -p timed out", {}
            add_use(rec, use)
            if ok or "version_mismatch" not in why:
                break
        rec.update(outcome="written" if ok else "FAILED", detail=why, attempt=attempt)
        if ok:
            why, got = why
            rec["detail"] = why
            state["last_write"] = now
            state["versions"].update(got)
            dump(os.path.join(root, "state.json"), state)
            dump(os.path.join(root, "last_write.json"), {"at": now, "rows": len(rows), "headline": why})
    with open(os.path.join(root, "runs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    return 0 if rec["outcome"] != "FAILED" else 1


if __name__ == "__main__":
    sys.exit(main())
