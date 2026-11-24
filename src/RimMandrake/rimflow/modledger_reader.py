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
import shutil
import subprocess
import time

PROMPT_VERSION = "2026-11-16.2"
LIFECYCLE = {"lease", "claim", "start", "reassign", "needs", "raise", "block", "unblock", "retarget", "spawn",
             "reclaim", "bridge", "game", "seat", "release", "priority", "park", "unpark"}
EVENT_CAP = 1600
# a test-queue quarantine or re-queue note is pipeline lifecycle (the round-3 judge, GSS 74): never handed to a reader
QUARANTINE_RE = re.compile(r"(?i)\bquarantin\w*\b[^.]*?(?:\bre-?queued?\b|\bno verdict\b|\bnot (?:a )?pass)|"
                           r"\bre-?queued?\b[^.]*\bquarantin")
PROSE_CAP = 9000
BATCH_CHARS = 36000

SYSTEM = """You read one software project's tickets and extract durable facts for a per-mod ledger. A holder picking \
the mod up in a month reads these entries instead of the tickets; every entry must change what that holder would do.
Rules (the ledger's entry standard, rule 10 and its field caps):
- Facts only, each stated in the record. Never invent a sha, path, number or cause. Never narrate (no "Started",
  "I", "We", "Now"), never write history or provenance ("found by GPT review", "fixed by the blind cycle's fixer",
  "closed at X by Y", "Producer re-plan", "detached run").
- defect: what is wrong, observable, in one or two sentences (<= 300 chars): the failure MECHANISM the record states
  (what loops, re-queues, is refused, stranded or misread, and where in the code), never a paraphrase of the title's
  requirement list. For a task ticket with no defect, what it must achieve.
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
- Never state a judgement the record does not state ("the pass is weaker than it reads"): a text cut mid-sentence
  is read for what it says, never for what its cut seems to imply.
- A card's QUESTION (the part before "→") is the premise he was asked about, never a fact: mine his answer, not it.
- A trap or limit ("cannot", "until X", "no X exists") is mined only when no later event in the record says it was
  done, reworded or lifted.
- The owner's words that only order work (scheduling, reassigning, stopping, pausing) are not facts about the mod.
Answer with ONE JSON object and nothing else: {"<TICKET_ID>": {"defect": ..., "proposed_fix": ..., "accept": ...,
"class": ..., "bars": [...], "changed": ... or null, "causes_refuted": [...], "traps": [...]}, ...} with one key per
ticket given."""


OWNER_SYSTEM = """You sort a project owner's words attached to software tickets. For each ticket you get its title and \
his words, numbered. Return the numbers of the words that state a durable ruling about the MOD named: its behaviour, \
scope, design, art, settings, tests or acceptance bars, or a verdict on a fix. Leave out words that only order or \
schedule work (including which mod goes first), assign or stop agents, talk about tokens, budgets, quotas or staffing, \
chat, rule on the pipeline or process as a whole rather than on this mod, or mean nothing without the question they \
answer ("1 agree.", "Yes all", "(2)"). Answer with ONE JSON object and nothing else: {"<TICKET_ID>": [numbers]}, \
one key per ticket given (an empty list when none qualify)."""


KEEP_SYSTEM = """You prune a per-mod ledger. A holder picks the mod up in a month and reads these entries before \
working on it. For each ticket you get its title, its defect and its candidate entries, numbered (T = a trap: what a \
reader would get wrong; C = a ruled-out cause). KEEP every entry that would make that holder read a result, a test or \
the code differently: an instrument, test, proof or harness that reads green or red for the wrong reason (a live FAIL \
that is not a mod defect, a degraded or partial test run, a check that reads less than it claims), a sha that no longer \
resolves or a close that was wrong, a misleading name or setting, a mechanism a reader would misjudge, a cause already \
ruled out. DROP only: agent workflow trivia (which helper, branch, clone, queue window or machine slot ran it, who may \
certify, how screenshots were captured, design-process rules for agents), bare status lines (UNRUN, still owed, not yet \
built, waits for X) that hold no reading a holder could get wrong, and restatements of the ticket's own defect or fix. \
When unsure, keep. Answer with ONE JSON object and nothing else: {"<TICKET_ID>": [kept numbers]}, one key per ticket."""


CURRENT_SYSTEM = """You check whether old statements about a software mod are still true. For each ticket you get \
its title and statements from it, numbered, each with the date it was stated, LATER work that may bear on it \
(commits on the main branch with their message, the ticket's own fix commits, closes and notes on the mod's tickets, \
each with its date) and TODAY lines: what the mod's files say now, at the path and line given. Return the numbers of the \
statements the later work plainly made false: the thing said impossible, missing, blocked or broken was done, added, \
staged or fixed; the wording, bar, test or setting it describes was changed; the count or state it gives was \
superseded; a today line contradicts it (the scene it calls missing exists, the criterion it quotes now reads \
otherwise, the known-red entry it cites is gone). Keep (leave out of your answer) a statement the later work restates, confirms, only mentions, works around \
for one run, or does not clearly address, and every lasting fact about how a tool, test or instrument behaves or what \
a past run showed. When unsure, keep. Answer with ONE JSON object and nothing else: {"<TICKET_ID>": [numbers made \
false]}, one key per ticket (an empty list when none)."""


def current_text(name, title, items):
    """One ticket's trap sentences as the currency reader sees them: [n] (stated <date>) text, then its later work,
    then today's lines of the mod's files. `items` are (date, text, later lines[, today lines])."""
    return "=== CURRENT %s\nTITLE: %s\n%s" % (name, title or "-", "\n".join(
        "[%d] (stated %s) %s\n%s" % (i + 1, str(it[0])[:10] or "?", " ".join(str(it[1]).split()), "\n".join(
            ["    later: " + " ".join(str(c).split()) for c in it[2]] +
            ["    today: " + " ".join(str(c).split()) for c in (it[3] if len(it) > 3 else ())]))
        for i, it in enumerate(items)))


def keep_text(name, title, defect, items):
    """One ticket's candidate traps and causes as the keep reader sees them: [n] T|C text (where)."""
    return "=== KEEP %s\nTITLE: %s\nDEFECT: %s\n%s" % (name, title or "-", defect or "-", "\n".join(
        "[%d] %s %s%s" % (i + 1, k, " ".join(str(t).split()), (" (%s)" % w) if w else "")
        for i, (k, t, w) in enumerate(items)))


def owner_text(name, title, mod, words):
    """One ticket's owner words as the owner reader sees them: [n] numbered, verbatim."""
    return "=== OWNER WORDS %s\nMOD: %s\nTITLE: %s\n%s" % (name, mod, title or "-", "\n".join(
        "[%d] %s" % (i + 1, " ".join(str(w).split())) for i, w in enumerate(words)))


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
        if QUARANTINE_RE.search(str(e.get("text") or "")):
            continue
        body = {f: e.get(f) for f in ("title", "spec", "text", "why", "reason", "noCode", "config", "result", "sha",
                                      "criteria", "ownerSaid", "byCard", "live", "by") if e.get(f)}
        if not body:
            continue
        lines.append("[%s %s %s] %s" % (k, e.get("seat"), str(e.get("ts") or "")[:10],
                                        _cap(json.dumps(body, ensure_ascii=False), EVENT_CAP)))
    if lines:
        out.append("EVENTS:\n" + "\n".join(lines))
    return "\n".join(out)


FIELD_VERSION = {"reading": PROMPT_VERSION, "owner": "owner-2026-11-16.2", "keep": "keep-2026-11-16.2",
                 "current": "current-2026-11-19.5b"}


def rec_hash(text, field="reading"):
    """The record's hash under its field's prompt version (a changed prompt re-reads only that field)."""
    return hashlib.sha256((FIELD_VERSION[field] + "\n" + text).encode("utf-8")).hexdigest()[:16]


# budget: danger=a model call that never returns holds the reader; longest=49s (every session run from /tmp (336), an upper
# budget: bound; agent transcripts, 14 days to 2026-11-24)
def _call(prompt, model, timeout=600, system=None):
    """-> (answer dict, usd). One `claude -p` call, no tools, no settings, no MCP; run from /tmp (no project files)."""
    claude = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")   # systemd's PATH lacks ~/.local/bin
    r = subprocess.run([claude, "-p", "--model", model, "--output-format", "json", "--strict-mcp-config", "--tools",
                        "", "--setting-sources", "", "--system-prompt", system or SYSTEM], input=prompt, capture_output=True,
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
# danger: one currency question, asked as written in the same batch, read [] in the round-5 EK re-mine and [1] twice
# when asked again (EK 125, the storeroom-mortar trap a later commit repaired); a kept false trap is a WRONG entry.
# So the currency reader reads each batch twice and a statement either pass found false leaves.
PASSES = {"current": 2}


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


def read_tickets(path, records, bars, budget_usd, model="sonnet", workers=4, log=print, field="reading", system=None):
    """Read every ticket in `records` ({name: record text}) whose reading is missing or was made from another text,
    a batch per call, `workers` at once, never starting a batch once the spend reaches `budget_usd` less the costliest
    batch so far. Writes `path` after every batch (an interrupted run keeps what it paid for). -> report dict."""
    d = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    tickets = d.setdefault("tickets", {})
    d["prompt_version"], d["model"] = PROMPT_VERSION, model
    hkey = "hash" if field == "reading" else field + "_hash"
    todo = [(n, t) for n, t in sorted(records.items()) if (tickets.get(n) or {}).get(hkey) != rec_hash(t, field)]
    spent, worst, done, failed, skipped = 0.0, 0.25, 0, [], 0     # 0.25: a first guess at a batch's cost
    bl = list(batches(todo))
    head = "BARS (the mod's locked bar ids): %s\n\n" % ", ".join(bars) if field == "reading" else ""

    def one(b):
        text = head + "\n\n".join(t for _, t in b)
        if system is None:
            return b, CALL(text, model)
        ans, usd = CALL(text, model, system=system)
        for _ in range(PASSES.get(field, 1) - 1):      # a statement any pass found false is false (PASSES)
            a2, u2 = CALL(text, model, system=system)
            usd += u2
            for n, v in (a2 or {}).items():
                if isinstance(v, list) and isinstance(ans.get(n, []), list):
                    ans[n] = sorted(set(ans.get(n) or []) | set(v))
        return b, (ans, usd)

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
                    if field == "reading" and isinstance(a, dict):
                        tickets[n] = dict(tickets.get(n) or {}, hash=rec_hash(t), reading=a,
                                          at=time.strftime("%Y-%m-%dT%H:%M:%S"))
                        done += 1
                    elif field != "reading" and isinstance(a, list):
                        tickets[n] = dict(tickets.get(n) or {}, **{field: a, hkey: rec_hash(t, field)})
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
