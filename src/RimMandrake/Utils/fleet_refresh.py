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
import fleet_mods  # noqa: E402
import fleet_watch  # noqa: E402

BOARD_URL = "https://claude.ai/artifact/PGnwP9teyQWPszjJzxJpr8"
HOURS = 3
HEARTBEAT = 20 * 60
MODS_EVERY = 30 * 60
LIVE = ("Building", "Checking")
MAX_WRITES = 40  # ArtifactData batch refuses more than 50 writes (MEASURED 2026-11-02); every write is echoed as output
FEED_MAX = 8
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


def doc_path(rows_dir, collection, doc_id):
    return os.path.join(rows_dir, doc_id + ".json") if collection == "parts" else \
        os.path.join(rows_dir, collection, doc_id + ".json")


def plan(rows, prev, now, rows_dir, docs=(), mods_due=False):
    """Pure: -> (writes, facts, board_version, new_state). `prev` is state.json's content ({} on the first run).
    Only rows whose content changed (ignoring elapsed minutes) or whose version is unknown are written. `docs` are
    extra (collection, doc_id, data): `mods` docs ride only when `mods_due`; board/factory rides on any run that writes
    anything else, or when its ok/running/target changed (its token count alone never wakes the model).
    The board refuses an overwrite without `if_version`, so every write to a doc we know carries its version."""
    old, versions = prev.get("status", {}), prev.get("versions", {})
    old_rh, old_dh = prev.get("row_hashes", {}), prev.get("doc_hashes", {})
    writes, facts, changes = [], [], []
    rh, dh = {}, dict(old_dh)

    def put(collection, doc_id):
        w = {"op": "set", "collection": collection, "doc_id": doc_id, "file_path": doc_path(rows_dir, collection, doc_id)}
        if "%s/%s" % (collection, doc_id) in versions:
            w["if_version"] = versions["%s/%s" % (collection, doc_id)]
        writes.append(w)

    for r in rows:
        h = row_hash([r])
        if h != old_rh.get(r["item"]) or "parts/" + r["item"] not in versions:
            if len(writes) < MAX_WRITES - FEED_MAX - 1:  # over the cap: left unhashed, so the next run writes it
                put("parts", r["item"])
                rh[r["item"]] = h
            elif r["item"] in old_rh:
                rh[r["item"]] = old_rh[r["item"]]
        else:
            rh[r["item"]] = h
        was = old.get(r["item"])
        if old and was != r["status"]:
            name = r.get("short") or fleet_watch.short(r["title"], 90)
            if was:
                what = "%s → %s" % (was, r["status"])
            else:
                what = "finished %s" % r.get("glyph", "") if r["status"] not in LIVE else "started (%s)" % r["status"]
            changes.append("%s: %s" % (name, what.strip()))
    for i, text in enumerate(changes[:FEED_MAX]):
        writes.append({"op": "set", "collection": "feed", "doc_id": "t%d-%d" % (now, i), "data": {"at": now, "text": text}})
    side = []
    for collection, doc_id, data in docs:
        key = "%s/%s" % (collection, doc_id)
        if collection == "mods" and not mods_due:
            continue
        h = row_hash([{k: v for k, v in data.items() if k not in ("tokens_today", "at")}])
        if collection != "board" and h == old_dh.get(key) and key in versions:
            continue
        side.append((collection, doc_id, h, h != old_dh.get(key)))
    side.sort(key=lambda x: x[0] != "board")  # the factory doc first, then mods
    mods_left = False
    if writes or any(c != "board" or changed for c, _, _, changed in side):
        for collection, doc_id, h, _ in side:
            if len(writes) >= MAX_WRITES:
                mods_left = mods_left or collection == "mods"
                continue
            put(collection, doc_id)
            dh["%s/%s" % (collection, doc_id)] = h
    by = {}
    for r in rows:
        by.setdefault(r["status"], []).append(r.get("short") or fleet_watch.short(r["title"], 90))
    for status in ("Building", "Checking", "Stopped", "Ended", "Done"):
        if by.get(status):
            facts.append("%s (%d): %s" % (status, len(by[status]), "; ".join(by[status][:6])))
    facts += ["changed since last refresh: " + c for c in changes[:8]]
    if len(changes) > 8:
        facts.append("and %d more changes" % (len(changes) - 8))
    if not rows:
        facts.append("nothing is running and nothing finished today")
    state = {"status": {r["item"]: r["status"] for r in rows}, "hash": row_hash(rows), "row_hashes": rh,
             "doc_hashes": dh, "mods_at": now if mods_due and not mods_left else prev.get("mods_at", 0),
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
    got = written_versions(result_text(res))
    want = {"%s/%s" % (w["collection"], w["doc_id"]) for w in writes} | {"board/summary"}
    if not want <= set(got):
        return False, "result confirms %d of %d writes: %s" % (len(want & set(got)), len(want), result_text(res)[:200]), use
    return True, (extra[0]["data"]["headline"], got), use


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
                       'collection "mods", then action "list" on collection "board". Then reply OK.' % BOARD_URL, rows_dir, system=SYSTEM_LIST)
    calls, results, use = read_stream(lines)
    v = parse_versions(calls, results)
    return (v if "board/summary" in v else None), use


def dedup(rows):
    """One row per item, the newest run winning: two rows on one doc_id in one batch is a version_mismatch every run
    (a re-dispatched item has two run files; a Relentless worker can share an item with a detached helper)."""
    best = {}
    for r in rows:
        if r["item"] not in best or r.get("started", 0) >= best[r["item"]].get("started", 0):
            best[r["item"]] = r
    return [r for r in rows if best[r["item"]] is r]


def ended(prev, current, rows_dir):
    """Rows that left the window while Building/Checking: rewritten once as Ended, or they freeze on the board."""
    out = []
    for item, status in prev.get("status", {}).items():
        if item in current or status not in ("Building", "Checking"):
            continue
        r = load(os.path.join(rows_dir, item + ".json"), None)
        if isinstance(r, dict) and r.get("item") == item:
            out.append(dict(r, status="Ended", unit="inactive", glyph="■", stuck="", finished_at=int(time.time())))
    return out


def collect(root, rows_dir, prev, now=None):
    """-> (rows, gathered). Live rows (helpers building, Relentless workers) plus receipts for items finished since
    local midnight; `gathered` is fleet_mods.gather()'s {factory, receipts, mods}."""
    now = now or int(time.time())
    titles = load(os.path.join(root, "titles.json"), {})
    hours = max(HOURS, int((now - fleet_mods.local_midnight(now)) / 3600) + 1)
    det = fleet_watch.rows(hours)
    for r in det:
        r["title"] = titles.get(r["item"]) or ledger_title(r["item"]) or r["item"]
    rel = fleet_watch.relentless_rows()
    for r in rel:
        r["title"] = titles.get(r["item"]) or ledger_title(r["item"]) or r["item"]
    live = dedup(rel + [r for r in det if r["status"] == "Building"])
    got = fleet_mods.gather(now, detached_done=[r for r in det if r["status"] != "Building"])
    have = {r["item"] for r in live}
    rows = live + [dict(r, title=titles.get(r["item"]) or r.get("title") or r["item"])
                   for r in got["receipts"] if r["item"] not in have]
    rows = dedup(rows)
    rows += ended(prev, {r["item"] for r in rows}, rows_dir)
    for i, r in enumerate(rows):
        r["short"] = fleet_watch.title_short(r["title"])
        r["order"] = i
    return rows, got


def add_use(rec, use):
    for k, x in use.items():
        rec[k] = round((rec.get(k) or 0) + (x or 0), 6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the prompt; no model call, no state change")
    ap.add_argument("--force", action="store_true", help="write even if nothing changed")
    ap.add_argument("--heartbeat", type=int, default=HEARTBEAT)
    ap.add_argument("--mods-every", type=int, default=MODS_EVERY, help="seconds between `mods` collection writes")
    a = ap.parse_args()
    root = storage_root()
    rows_dir = os.path.join(root, "rows")
    os.makedirs(rows_dir, exist_ok=True)
    now = int(time.time())
    fleet_watch.sh("git", "fetch", "-q", "origin")
    rows = None
    prev = load(os.path.join(root, "state.json"), {})
    try:
        rows, got = collect(root, rows_dir, prev, now)
    except Exception as e:  # one malformed run file must leave a FAILED line, not a silent dead timer
        rows, crash = None, "row collection crashed: %s: %s" % (type(e).__name__, e)
    if rows is None:
        rec = {"at": now, "outcome": "FAILED", "detail": crash}
        with open(os.path.join(root, "runs.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))
        return 1
    docs = [("mods", m["id"], m) for m in got["mods"]] + [("board", "factory", got["factory"])]
    due = a.force or now - prev.get("mods_at", 0) >= a.mods_every
    writes, facts, board_version, state = plan(rows, prev, now, rows_dir, docs, due)
    if a.dry_run:
        print(prompt(writes, facts, now, board_version))
        return 0
    rec = {"at": now, "rows": len(rows), "writes": len(writes),
           "mods": sum(1 for w in writes if w["collection"] == "mods")}
    if not a.force and not writes and now - prev.get("last_write", 0) < a.heartbeat:
        rec["outcome"] = "skipped: unchanged"
    else:
        if not writes:  # heartbeat: the board's `updated` moves so the page can tell stale from quiet
            dh = {k: v for k, v in prev.get("doc_hashes", {}).items() if k != "board/factory"}
            writes, facts, board_version, state = plan(rows, dict(prev, doc_hashes=dh), now, rows_dir, docs, due)
        for r in rows:
            dump(doc_path(rows_dir, "parts", r["item"]), r)
        for collection, doc_id, data in docs:
            os.makedirs(os.path.dirname(doc_path(rows_dir, collection, doc_id)), exist_ok=True)
            dump(doc_path(rows_dir, collection, doc_id), data)
        ok, why = False, "versions unknown"
        for attempt in (1, 2):
            if attempt == 2 or "versions" not in prev:
                # first run, or someone else (the Conductor) wrote since: re-read every version, re-plan, retry once
                try:
                    v, use = sync_versions(rows_dir)
                except (subprocess.TimeoutExpired, OSError):
                    v, use = None, {}
                add_use(rec, use)
                if v is None:
                    why = "version sync failed"
                    break
                prev = dict(prev, versions=v)
                writes, facts, board_version, state = plan(rows, prev, now, rows_dir, docs, due)
            try:
                ok, why, use = judge(run_claude(prompt(writes, facts, now, board_version), rows_dir), writes, board_version)
            except (subprocess.TimeoutExpired, OSError) as e:
                ok, why, use = False, "claude -p did not run: %s" % type(e).__name__, {}
            add_use(rec, use)
            if ok or "version_mismatch" not in why:
                break
        # a sync re-plan or a heartbeat may have changed the batch: record what was actually sent
        rec.update(outcome="written" if ok else "FAILED", detail=why, attempt=attempt, writes=len(writes),
                   mods=sum(1 for w in writes if w["collection"] == "mods"))
        if ok:
            why, confirmed = why
            rec["detail"] = why
            state["last_write"] = now
            state["versions"].update(confirmed)
            dump(os.path.join(root, "state.json"), state)
            dump(os.path.join(root, "last_write.json"), {"at": now, "rows": len(rows), "headline": why})
    with open(os.path.join(root, "runs.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    return 0 if rec["outcome"] != "FAILED" else 1


if __name__ == "__main__":
    sys.exit(main())
