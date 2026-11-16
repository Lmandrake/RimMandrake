#!/usr/bin/env python3
"""modledger_reader.py — read each mined ticket with judgement, once, for the mod-ledger backfill.

The independent judges failed the regex miner on what a regex cannot read (RIMMANDRAKE_FIX_MINER_JUDGE_FAILED_SLACK_
EIGHT_OF_TWENTY): which line is the defect, what a fix changed, which causes were ruled out under whatever wording, and
what a reader would get wrong. This module hands each ticket's whole record (prose, blind fault, fix record, rimflow
events less lifecycle) to `claude -p` (the project's only LLM transport) with the entry standard's rule 10 as its
prompt, a batch of tickets per call, under a dollar bound, and writes the answers to
`src/RimMandrake/rimflow/modledger_readings/<Mod>.json` (committed: every clone's re-mine reads the same readings, so
a re-run without `--read` never deletes what a reading found). The miner validates every answer (caps, locked bars,
paths that exist) and keeps its own deterministic state, shas and refs: a reading supplies words, never state.

    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod GimmeSomeSlack --read --read-budget 6
"""
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import time

PROMPT_VERSION = "2026-11-16.1"
LIFECYCLE = {"lease", "claim", "start", "reassign", "needs", "raise", "block", "unblock", "retarget", "spawn",
             "reclaim", "bridge", "game", "seat", "release", "priority", "park", "unpark"}
EVENT_CAP = 1600
PROSE_CAP = 9000
BATCH_CHARS = 36000

SYSTEM = """You read one software project's tickets and extract durable facts for a per-mod ledger. A holder picking \
the mod up in a month reads these entries instead of the tickets; every entry must change what that holder would do.
Rules (the ledger's entry standard, rule 10 and its field caps):
- Facts only, each stated in the record. Never invent a sha, path, number or cause. Never narrate (no "Started",
  "I", "We", "Now"), never write history or provenance ("found by GPT review", "fixed by the blind cycle's fixer",
  "closed at X by Y", "Producer re-plan", "detached run").
- defect: what is wrong, observable, in one or two sentences (<= 300 chars). For a task ticket, what it must achieve.
- proposed_fix: what to change, concretely (the ticket's Fix: line, spec, or smallest_fix) (<= 300 chars).
- accept: the acceptance test the ticket FILED: a command and its expected result, or a blind fault's would_pass;
  "none, <reason>" when it filed none (<= 230 chars).
- class: "polish" only when the record calls it polish; else "problem".
- bars: only ids from the BARS list given, and only those the record ties the defect to; else [].
- changed: when the record says it was fixed, what the change did, naming each cause it fixed in a clause (<= 300
  chars); null when the record states no fix.
- causes_refuted: every hypothesis the record RULED OUT, under any wording ("ruled out", "not the cause",
  "explained as", "Correction:", "turned out", "the fault was in the test", "no bug in the mod", "rather than X"):
  {"text": the hypothesis and what refuted it (<= 300), "depends_on": repo paths named in the record it rests on}.
  A cause the record says is NOT ruled out, or only suspects, is not refuted.
- traps: what a reader would otherwise get wrong (an instrument green for the wrong reason, a sha that no longer
  resolves, a test that reads less than it claims, a misleading name or setting): {"text": the mistake and the truth
  (<= 300), "where": the path, row or instrument (<= 150)}.
- The owner's words that only order work (scheduling, reassigning, stopping, pausing) are not facts about the mod.
Answer with ONE JSON object and nothing else: {"<TICKET_ID>": {"defect": ..., "proposed_fix": ..., "accept": ...,
"class": ..., "bars": [...], "changed": ... or null, "causes_refuted": [...], "traps": [...]}, ...} with one key per
ticket given."""


def _cap(t, n):
    t = " ".join(str(t or "").split())
    return t if len(t) <= n else t[:n] + " (cut)"   # cut-ok: this is model INPUT, the ticket on disk is whole


def record_text(name, title, state, prose, evs, fault=None, fixrec=None, prose_path=None):
    """One ticket's whole record as the reader sees it: lifecycle events left out, each text capped."""
    out = ["=== TICKET %s" % name, "TITLE: %s" % (title or "-"), "RIMFLOW STATE: %s" % (state or "-")]
    if prose:
        out.append("PROSE (%s):\n%s" % (prose_path or "item file", prose[:PROSE_CAP]))
    if fault:
        out.append("BLIND FAULT RECORD: " + _cap(json.dumps(fault, ensure_ascii=False), 4000))
    if fixrec:
        out.append("FIX RECORD: " + _cap(json.dumps(fixrec, ensure_ascii=False), 1500))
    lines = []
    for t in evs:
        e = t[2]
        k = e.get("event")
        if k in LIFECYCLE:
            continue
        body = {f: e.get(f) for f in ("title", "text", "why", "reason", "noCode", "config", "result", "sha", "criteria",
                                      "ownerSaid", "byCard", "live", "by") if e.get(f)}
        if not body:
            continue
        lines.append("[%s %s %s] %s" % (k, e.get("seat"), str(e.get("ts") or "")[:10],
                                        _cap(json.dumps(body, ensure_ascii=False), EVENT_CAP)))
    if lines:
        out.append("EVENTS:\n" + "\n".join(lines))
    return "\n".join(out)


def rec_hash(text):
    return hashlib.sha256((PROMPT_VERSION + "\n" + text).encode("utf-8")).hexdigest()[:16]


def _call(prompt, model, timeout=600):
    """-> (answer dict, usd). One `claude -p` call, no tools, no settings, no MCP; run from /tmp (no project files)."""
    r = subprocess.run(["claude", "-p", "--model", model, "--output-format", "json", "--strict-mcp-config", "--tools",
                        "", "--setting-sources", "", "--system-prompt", SYSTEM], input=prompt, capture_output=True,
                       text=True, timeout=timeout, cwd="/tmp")
    try:
        out = json.loads(r.stdout)
    except ValueError:
        raise RuntimeError("claude -p gave no JSON (rc %s): %s" % (r.returncode, (r.stderr or r.stdout)[:300]))
    usd = float(out.get("total_cost_usd") or 0)
    txt = out.get("result") or ""
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        return (json.loads(m.group(0)) if m else {}), usd
    except ValueError:
        return {}, usd


CALL = _call       # the selftest stands a fake in here


def batches(todo, limit=BATCH_CHARS):
    cur, size = [], 0
    for name, text in todo:
        if cur and size + len(text) > limit:
            yield cur
            cur, size = [], 0
        cur.append((name, text))
        size += len(text)
    if cur:
        yield cur


def read_tickets(path, records, bars, budget_usd, model="sonnet", workers=4, log=print):
    """Read every ticket in `records` ({name: record text}) whose reading is missing or was made from another text,
    a batch per call, `workers` at once, never starting a batch once the spend reaches `budget_usd` less the costliest
    batch so far. Writes `path` after every batch (an interrupted run keeps what it paid for). -> report dict."""
    d = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    tickets = d.setdefault("tickets", {})
    d["prompt_version"], d["model"] = PROMPT_VERSION, model
    todo = [(n, t) for n, t in sorted(records.items()) if (tickets.get(n) or {}).get("hash") != rec_hash(t)]
    spent, worst, done, failed, skipped = 0.0, 0.25, 0, [], 0     # 0.25: a first guess at a batch's cost
    bl = list(batches(todo))
    head = "BARS (the mod's locked bar ids): %s\n\n" % ", ".join(bars)

    def one(b):
        return b, CALL(head + "\n\n".join(t for _, t in b), model)

    pending = list(bl)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        running = set()
        while pending or running:
            while pending and len(running) < workers and spent + worst * (len(running) + 1) < budget_usd:
                running.add(ex.submit(one, pending.pop(0)))
            if not running:
                skipped = sum(len(b) for b in pending)
                break
            fin, running = concurrent.futures.wait(running, return_when=concurrent.futures.FIRST_COMPLETED)
            for f in fin:
                try:
                    b, (ans, usd) = f.result()
                except Exception as e:      # a failed call is counted and its tickets keep their old reading
                    failed.append(str(e)[:200])
                    continue
                spent += usd
                worst = max(worst, usd)
                for n, t in b:
                    a = ans.get(n)
                    if isinstance(a, dict):
                        tickets[n] = {"hash": rec_hash(t), "reading": a, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
                        done += 1
                    else:
                        failed.append("no answer for %s" % n)
                d["spent_usd_last_run"] = round(spent, 4)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path + ".tmp", "w", encoding="utf-8") as fh:
                    json.dump(d, fh, ensure_ascii=False, indent=0, sort_keys=True)
                os.replace(path + ".tmp", path)
                log("read %d of %d tickets, $%.2f spent" % (done, len(todo), spent))
    return {"asked": len(todo), "read": done, "failed": failed, "skipped_for_budget": skipped,
            "spent_usd": round(spent, 4), "batches": len(bl)}
