#!/usr/bin/env python3
"""Selftest for the post-event recovery mode design (OPS_RECOVERY_DESIGN_POST_EVENT_MODE).

The design is a doc, so this checks two things: its required parts are present, and the facts it states that the
repo itself holds are true:
  * relentless_rules.json carries the breaker numbers the 429 replay rests on (3 failures, 900 s, cap 1800 s);
  * the ledger's supersede/close rows for HARNESS_REPAIR_CAUSE_* match what §7.1 says the hand triage did.
A negative control runs the same checks on a copy with one part cut out and on a ledger with a target changed; both must
fail, so a green run cannot come from a checker that sees nothing.

    python3 src/RimMandrake/rimflow/selftest_recovery_design_doc.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DOC = os.path.join(ROOT, "design", "RimMandrake", "post_event_recovery_mode_2026-11-05.md")
RULES = os.path.join(ROOT, "src", "RimMandrake", "rimflow", "relentless_rules.json")
LEDGER = os.path.join(ROOT, "infrastructure", "state", "ledger", "events")

REQUIRED = [  # (what, regex) — each must match the doc
    ("incident record section", r"^## 2\. The incident record"),
    ("record field onset interval", r"`onset` \| `\{earliest, latest\}`"),
    ("record field sightings", r"`sightings\[\]`"),
    ("record field adjustments", r"`adjustments\[\]`"),
    ("record field probes bound", r"`probes` \| `\{used, max\}`"),
    ("state machine section", r"^## 3\. The state machine"),
] + [("phase row " + p, r"^\| \*\*%s\*\* \|" % p) for p in ("QUARANTINE", "RECONCILE", "VERIFY", "RAMP", "NORMAL", "STALLED")] + [
    ("STALLED age alarm", r"\*\*The STALLED age alarm\*\*"),
    ("STALLED alarm fixed id", r"OPS_RECOVERY_STALLED_<source>"),
    ("entry signals section", r"^## 4\. Entry signals"),
] + [("entry signal " + k, r"^\| \*\*%s\*\* \|" % k) for k in ("host_fault_wave", "account_wave", "harness_burst")] + [
    ("arbitration section", r"^## 5\. Per-sighting arbitration"),
] + [("disposition " + d, r"\| \*\*%s(, once)?\*\* \|" % d) for d in ("drop", "merge", "park", "keep")] + [
    ("park needs wake", r"A park with no `wake` is refused"),
    ("re-baseline section", r"^## 6\. Versioned re-baseline"),
    ("raw history kept", r"\*\*Raw history is never edited\.\*\*"),
    ("view versioned", r"`view_version`"),
    ("Steve replay", r"^### 7\.1 The Steve host fault wave"),
    ("429 replay", r"^### 7\.2 The 429 / account wave"),
    ("Steve replay cites windows", r"fault_windows\.json"),
    ("429 replay cites attempts", r"attempts\.jsonl"),
    ("pause left alone", r"It does \*\*not\*\* change the content pause"),
    ("design review section", r"^## 10\. Design review"),
]

# §7.1's claims about the hand triage (045724125c), as (ticket suffix, event, target or None)
TRIAGE = [("4D2C5B87", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("5495932D", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("8A6B00BD", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("FA96BB79", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("FCC08D84", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("4AFBF8A2", "supersede", "SITE_QUIET_FIX_COLONISTS_HURT_DOWNED_DEAD"),
          ("AC81755A", "supersede", "HARNESS_REPAIR_CAUSE_0CA2BE29"),
          ("C1644394", "supersede", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO"),
          ("99231A83", "supersede", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO"),
          ("0143E7AD", "supersede", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO"),
          ("4E52E202", "supersede", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO"),
          ("FC103899", "supersede", "COMPANION_STAGE_FIX_JOBS_ARRIVE_STALE"),
          ("2E27AD17", "close", None),
          ("3A38C661", "close", None)]
STILL_OPEN = ("0CA2BE29", "5F134E3C", "E0B6DA41", "EBC39CFA")
SPAWNED = 18


def doc_problems(text):
    out = [what for what, rx in REQUIRED if not re.search(rx, text, re.M)]
    review = text.split("## 10. Design review", 1)[-1]
    findings = re.findall(r"^- \*\*R\d+\b.*?(?=^- \*\*R\d+\b|\Z)", review, re.M | re.S)  # a bullet, wrapped lines too
    if not findings:
        out.append("design review records no finding (- **R1 ...)")
    out += ["review finding unanswered: " + f[:60] for f in findings if "Answer:" not in f]
    if "(filled in below by the review pass)" in review:
        out.append("design review placeholder still present")
    return out


PHASES = ("QUARANTINE", "RECONCILE", "VERIFY", "RAMP", "NORMAL", "STALLED")
TERMINAL = {"NORMAL"}  # NORMAL has no exit by design: the record stays open for relapse_h and a recurrence reopens it
TIMED = ("QUARANTINE", "RECONCILE", "VERIFY", "RAMP")  # the phases the doc gives a deadline
REPLAYS = (("7.1", r"^### 7\.1 ", 8), ("7.2", r"^### 7\.2 ", 5))  # (label, heading, min timed rows)
EMPTY = ("", "\u2014", "-", "--", "n/a", "tbd")


def _blank(cell):
    return cell.strip().lower() in EMPTY


def _section(text, head_rx):
    m = re.search(head_rx, text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^##+ ", rest, re.M)
    return rest[:n.start()] if n else rest


def _rows(block):
    """Body rows of every markdown table in block, as lists of cells (header and --- rule skipped)."""
    out, prev_rule = [], False
    for line in block.splitlines():
        if not line.startswith("|"):
            prev_rule = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            prev_rule = True
            continue
        if prev_rule or out and len(cells) == len(out[-1]):
            out.append(cells)
    return out


def structure_problems(text):
    """The phase table and both replay tables must carry content, not only their headings and keywords."""
    out = []
    table = {r[0].strip("* "): r for r in _rows(_section(text, r"^## 3\. The state machine")) if len(r) == 5}
    for ph in PHASES:
        r = table.get(ph)
        if not r:
            out.append("phase %s: no 5-cell row in the 3 table" % ph)
            continue
        for col, name in ((1, "Entry"), (2, "action"), (3, "Exit")):
            if _blank(r[col]) and not (name == "Exit" and ph in TERMINAL):
                out.append("phase %s: %s cell empty" % (ph, name))
        if ph in TIMED and not re.search(r"\d+\s*(min|h)\b", r[4]):
            out.append("phase %s: Deadline cell %r names no time" % (ph, r[4]))
    for label, head, need in REPLAYS:
        rows = [r for r in _rows(_section(text, head)) if len(r) == 4]
        if len(rows) < need:
            out.append("replay %s: %d table rows, need >= %d" % (label, len(rows), need))
        for r in rows:
            if _blank(r[0]):
                out.append("replay %s: a row with no time" % label)
            if len(r[2].strip()) < 20:
                out.append("replay %s %s: no action described" % (label, r[0][:24]))
            if _blank(r[3]):  # the contract: "each step citing a source"; the doc: "Each line cites its reading."
                out.append("replay %s %s: reading cell empty, the step cites no source" % (label, r[0][:24]))
    return out


def rules_problems(rules):
    want = {"launch_breaker": 3, "breaker_cool_s": 900, "breaker_cool_max_s": 1800}
    return ["rules %s=%r, doc says %r" % (k, rules.get(k), v) for k, v in want.items() if rules.get(k) != v]


def ledger_events(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    return rows


def ledger_problems(rows):
    pre = "HARNESS_REPAIR_CAUSE_"
    spawned = {r.get("name") for r in rows if r.get("event") == "spawn" and str(r.get("name", "")).startswith(pre)}
    out = [] if len(spawned) == SPAWNED else ["%d HARNESS_REPAIR_CAUSE_* spawned, doc says %d" % (len(spawned), SPAWNED)]
    ends = {}
    for r in sorted(rows, key=lambda r: r.get("tsn") or 0):
        i = r.get("id") or ""
        if i.startswith(pre) and r.get("event") in ("supersede", "close", "drop"):
            ends[i[len(pre):]] = (r["event"], r.get("by"))
    for t, ev, by in TRIAGE:
        got = ends.get(t)
        if not got or got[0] != ev or (by and got[1] != by):
            out.append("%s: ledger %r, doc says %s %s" % (t, got, ev, by or ""))
    out += ["%s: ledger ended it %r, doc says still open" % (t, ends[t]) for t in STILL_OPEN if t in ends]
    return out


def main():
    fails = []
    with open(DOC, encoding="utf-8") as f:
        text = f.read()
    with open(RULES, encoding="utf-8") as f:
        rules = json.load(f)
    rows = ledger_events(sorted(glob.glob(os.path.join(LEDGER, "*.jsonl"))))
    for name, probs in (("doc", doc_problems(text)), ("structure", structure_problems(text)), ("rules", rules_problems(rules)), ("ledger", ledger_problems(rows))):
        fails += ["%s: %s" % (name, p) for p in probs]

    # negative controls: the instrument must see a cut part, a changed number and a changed triage target
    if not doc_problems(text.replace("**The STALLED age alarm**", "the age alarm")):
        fails.append("control: a doc without the STALLED age alarm passed")
    if not doc_problems(text.replace("Answer:", "Reply-", 1)):
        fails.append("control: a review finding with its answer removed passed")
    # mutant A (checker, gen 3): every row of both replay tables deleted, headings and prose kept
    def _cut_replay_rows(t):
        keep, sec = [], None
        for line in t.splitlines(True):
            if line.startswith("### 7."):
                sec = True
            elif line.startswith("## ") or line.startswith("### "):
                sec = None
            if sec and line.startswith("|") and not line.startswith("| Time") and "---" not in line:
                continue
            keep.append(line)
        return "".join(keep)
    if not structure_problems(_cut_replay_rows(text)):
        fails.append("control: a doc with its replay table rows deleted passed")
    # mutant B (checker, gen 3): the Exit cell of every phase row blanked
    def _blank_exits(t):
        def sub(m):
            c = m.group(0).rstrip("\n").split("|")
            c[4] = " "
            return "|".join(c) + "\n"
        return re.sub(r"^\| \*\*(%s)\*\* \|.*\n" % "|".join(PHASES), sub, t, flags=re.M)
    if not structure_problems(_blank_exits(text)):
        fails.append("control: a doc with every phase Exit cell blanked passed")
    one = re.sub(r"(^### 7\.1 [\s\S]*?^\| 02:45Z \|[^\n]*\| )[^|\n]+( \|$)", "\\1\u2014\\2", text, count=1, flags=re.M)
    if one == text or not structure_problems(one):
        fails.append("control: a 7.1 step with its reading removed passed")
    if not rules_problems(dict(rules, breaker_cool_max_s=3600)):
        fails.append("control: a changed breaker cap passed")
    bent = [dict(r, by="SOMETHING_ELSE") if r.get("id") == "HARNESS_REPAIR_CAUSE_C1644394" and r.get("event") == "supersede"
            else r for r in rows]
    if not ledger_problems(bent):
        fails.append("control: a changed triage target passed")

    for f_ in fails:
        print("FAIL", f_)
    print("selftest_recovery_design_doc: %s (%d doc parts, %d triage rows, 7 controls)" % (
        "FAIL" if fails else "PASS", len(REQUIRED), len(TRIAGE)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
