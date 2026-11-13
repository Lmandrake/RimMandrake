#!/usr/bin/env python3
"""Daily agent improvement pass: gather (no AI), Curator, Judge, apply, ramp.

Design: design/RimMandrake/daily_agent_improvement_2026-11-02.md (item AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS).

    python3 src/RimMandrake/Utils/agent_improve.py gather [--day YYYY-MM-DD] [--out DIR] [--dry-run]
    python3 src/RimMandrake/Utils/agent_improve.py run [--day D] [--apply] [--target T ...] [--force]
    python3 src/RimMandrake/Utils/agent_improve.py ramp                # the level, the rate, the next step
    python3 src/RimMandrake/Utils/agent_improve.py materialize <target> v<N> <dir>

Reads day D's evidence (lessons filed, Relentless reject reasons, learned lines and alarms, Operations alarms, owner
words), routes each piece to a target (a role, `relentless`, or a skill), and writes a packet for the Curator:
<out>/<D>/packet.json and packet.md. A target is SIGNALLED only on recurrence: at least RECUR pieces in the WINDOW_DAYS
ending on D (owner ruling LESSONS_RETIRE_INBOX_AS_QUEUE: promote on recurrence, never count the backlog). At most
MAX_TARGETS signalled targets go in the packet, most pieces first.

`run` is one pass: gather, then per signalled target a fresh Curator (`claude -p`, no tools) proposes at most one edit of
at most MAX_EDIT_LINES lines, citing the packet pieces that show the failure it fixes (survey rule 3) and preferring a code
check or tool, which it may only PROPOSE (rule 4); a different fresh Judge returns KEEP/REDO/UNSURE without seeing the
Curator's reasoning; with --apply each KEEP is checked (`git apply --check`, validate_skills, the target's selftests),
published with `Delegated: technical`, tagged agent/<target>/v<N>, and recorded in
infrastructure/state/agent_improve/changes/<target>_v<N>.json. Verdicts: infrastructure/state/delegated/<D>/. The ramp
level (design section 4.1) lives in <out>/state.json and sets gather's bar. The generalization check (4.3) lives in
agent_improve_general.py: `general <target> v<N>` runs it on an applied version, and at L2 it gates every apply.
"""
import argparse
import ast
import calendar
import difflib
import glob
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import lessons  # noqa: E402  (parse_name, home_of)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
import model  # noqa: E402  (parse_name: an item id's intent word is its task kind)

STORE = "/home/mandrake/rm/relentless/store"          # relentless.DEFAULT_ROOT + /store
OPS_ALARMS = "/mnt/d/ClaudeWork/rimmandrake/ops_watch/alarms.json"
OUT = "/mnt/d/ClaudeWork/rimmandrake/agent_improve"
WINDOW_DAYS = 7
RECUR = 2
MAX_TARGETS = 6
AGENTS = {"relentless", "operations", "designer"}    # the agents rank before skills and docs under the cap
MAX_PIECES = 25                                       # per target in the packet; the kinds line counts them all
OK_ENDS = {"finish", "done"}                          # an attempt end that is not a reject
LEARNED = re.compile(r"^- (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) gen \d+: (.*)$")


def day_bounds(day):
    t0 = calendar.timegm(time.strptime(day, "%Y-%m-%d"))
    return t0, t0 + 86400


def epoch(ts):
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def first_line(text, n=200):
    for ln in str(text or "").splitlines():
        ln = ln.strip().lstrip("#").strip()
        if ln:
            return ln[:n]
    return ""


def norm_target(home):
    """A lesson's `home:` to a target name: a skill name, or a doc path's basename; NONE is unrouted."""
    words = (home or "").replace("`", " ").split()
    if words and re.fullmatch(r"skills?:?", words[0], re.I):   # "skill foo", "skill: foo"
        words = words[1:]
    h = re.sub(r"^skills?:", "", words[0], flags=re.I) if words else ""
    if not h or h.upper() == "NONE":
        return None
    if "/" in h:
        parts = [p for p in h.split("/") if p]
        if "skills" in parts and parts.index("skills") + 1 < len(parts):
            return parts[parts.index("skills") + 1]
        return parts[-1]
    return h


def piece(target, kind, ts, path, text, item=None):
    """`text` is the first line, for the packet. The task kind (design 4.3) is the kind of `item`, the piece's own item
    when its source records one (a lesson's `item:` footer, a Relentless row's item, an ops alarm's name, an owner
    note's id; NONE or an id with no intent word gives no kind, never a guess from the text), else of the first item
    named in the whole text, so a lesson that names its item past its first 200 characters still names its kind."""
    return {"target": target, "kind": kind, "ts": ts, "path": path, "text": first_line(text),
            "task_kind": kind_of_text(item) if item else kind_of_text(text)}


def lesson_pieces(lessons_dir, lo, hi):
    out = []
    for p in sorted(glob.glob(os.path.join(lessons_dir, "*.md"))):
        t, _seat = lessons.parse_name(p)
        if t is None or not lo <= t < hi:
            continue
        try:
            body = open(p, encoding="utf-8").read()
        except OSError:
            continue
        out.append(piece(norm_target(lessons.home_of(p)), "lesson", t, p, body, item=lessons.item_of(p)))
    return out


def relentless_pieces(store, lo, hi):
    out = []
    for p in glob.glob(os.path.join(store, "items", "*", "attempts.jsonl")):
        item = os.path.basename(os.path.dirname(p))
        for ln in open(p, encoding="utf-8", errors="replace"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = epoch(r.get("at"))
            if t is None or not lo <= t < hi or not r.get("end") or r.get("end") in OK_ENDS:
                continue
            out.append(piece("relentless", "reject:%s" % r.get("end"), t, p,
                             "%s: %s" % (item, r.get("detail") or r.get("why") or r.get("end")), item=item))
    for p in glob.glob(os.path.join(store, "items", "*", "learned.md")):
        item = os.path.basename(os.path.dirname(p))
        for ln in open(p, encoding="utf-8", errors="replace"):
            m = LEARNED.match(ln.rstrip("\n"))
            t = epoch(m.group(1)) if m else None
            if t is not None and lo <= t < hi:
                out.append(piece("relentless", "learned", t, p, "%s: %s" % (item, m.group(2)), item=item))
    j = os.path.join(store, "journal.jsonl")
    if os.path.exists(j):
        for ln in open(j, encoding="utf-8", errors="replace"):
            if '"alarm"' not in ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            t = epoch(r.get("at"))
            if r.get("do") == "alarm" and t is not None and lo <= t < hi:
                item = r.get("item") or re.sub(r"\.q\d+$", "", os.path.basename(r.get("clone") or ""))   # clones/<item>[.qN]
                why = r.get("why") or r.get("kind")
                out.append(piece("relentless", "alarm:%s" % r.get("kind"), t, j, "%s: %s" % (item, why) if item else why,
                                 item=item or None))
    return out


def ops_pieces(alarms_path, lo, hi):
    try:
        d = json.load(open(alarms_path, encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = d.values() if isinstance(d, dict) else d
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        t = epoch(r.get("since") or r.get("filed"))
        if t is not None and lo <= t < hi:
            out.append(piece("operations", "alarm", t, alarms_path, "%s: %s" % (r.get("name"), r.get("title")),
                             item=r.get("name")))
    return out


def owner_pieces(owner_shard, lo, hi):
    out = []
    if not os.path.exists(owner_shard):
        return out
    for ln in open(owner_shard, encoding="utf-8", errors="replace"):
        if '"ownerSaid"' not in ln:
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        t = epoch(r.get("ts"))
        if t is not None and lo <= t < hi and r.get("ownerSaid"):
            out.append(piece(None, "owner_said", t, owner_shard, "%s: %s" % (r.get("id") or "-", r["ownerSaid"]),
                             item=r.get("id")))
    return out


def collect(lo, hi, src):
    return (lesson_pieces(src["lessons"], lo, hi) + relentless_pieces(src["store"], lo, hi)
            + ops_pieces(src["ops_alarms"], lo, hi) + owner_pieces(src["owner"], lo, hi))


def target_entry(t, window_count, ps):
    """Every kind counted; the pieces kept are the newest MAX_PIECES, spread over kinds (one of each kind first)."""
    kinds = {}
    for p in ps:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    newest = sorted(ps, key=lambda p: -p["ts"])
    keep, seen = [], set()
    for p in newest:
        if p["kind"] not in seen and len(keep) < MAX_PIECES:
            keep.append(p)
            seen.add(p["kind"])
    for p in newest:
        if len(keep) >= MAX_PIECES:
            break
        if p not in keep:
            keep.append(p)
    return {"target": t, "window_count": window_count, "today": len(ps), "kinds": kinds,
            "pieces": sorted(keep, key=lambda p: p["ts"])}


ITEM_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}\b")


def task_kind(p):
    """The intent word of the first item id named in a piece (BUILD, REPAIR, ...), else None. A collected piece carries
    it read from its whole text; a bare {"text": ...} is read from that text."""
    return p["task_kind"] if "task_kind" in p else kind_of_text(p.get("text"))


def kind_of_text(text):
    for tok in ITEM_TOKEN.findall(text or ""):
        parsed = model.parse_name(re.sub(r"_\d+$", "", tok))
        if parsed:
            return parsed[1]
    return None


def gather(day, src, lv=None, changes_dir=None):
    """lv: a LEVELS row (the ramp's bar); default L0, the constants above."""
    lv = lv or {"level": 0, "recur": RECUR, "window_days": WINDOW_DAYS, "min_task_kinds": 0, "need_recheck": False}
    lo, hi = day_bounds(day)
    today = collect(lo, hi, src)
    window = collect(hi - lv["window_days"] * 86400, hi, src)
    counts, tkinds = {}, {}
    for p in window:
        if p["target"]:
            counts[p["target"]] = counts.get(p["target"], 0) + 1
            k = task_kind(p)
            if k:
                tkinds.setdefault(p["target"], set()).add(k)
    by_target = {}
    for p in today:
        if p["target"]:
            by_target.setdefault(p["target"], []).append(p)
    held, recheck_only = {}, set()
    for t in by_target:
        if counts.get(t, 0) < lv["recur"]:
            continue
        if len(tkinds.get(t, ())) < lv["min_task_kinds"]:
            held[t] = "%d task kinds in window, bar %d" % (len(tkinds.get(t, ())), lv["min_task_kinds"])
            continue
        prior = last_change(t, changes_dir)
        if lv["need_recheck"] and prior and prior.get("recheck_result") != "pass" and not prior.get("revert_of"):
            # Not dropped: the Curator still runs to read the recheck (else nothing could ever record a pass),
            # and a change is refused unless that same reply reads it as pass.
            recheck_only.add(t)
            held[t] = "the recheck of %s is %s, not pass; Curator reads it, no change unless pass" % (
                prior.get("tag"), prior.get("recheck_result") or "unread")
    signalled = sorted((t for t in by_target if counts.get(t, 0) >= lv["recur"]
                        and (t not in held or t in recheck_only)),
                       key=lambda t: (t not in AGENTS, -counts[t], -len(by_target[t]), t))
    kept = signalled[:MAX_TARGETS]
    targets = []
    for t in kept:
        e = target_entry(t, counts[t], by_target[t])
        e["task_kinds"] = sorted(tkinds.get(t, ()))
        e["prior"] = last_change(t, changes_dir)
        e["recheck_only"] = t in recheck_only
        targets.append(e)
    return {
        "day": day, "level": lv["level"], "window_days": lv["window_days"], "recur": lv["recur"],
        "max_targets": MAX_TARGETS, "pieces_today": len(today),
        "targets": targets,
        "dropped_over_cap": signalled[MAX_TARGETS:],
        "held": held,
        "unsignalled": sorted(t for t in by_target if counts.get(t, 0) < lv["recur"]),
        "unrouted": [p for p in today if not p["target"]],
    }


def render(pk):
    L = ["# Agent improvement packet %s" % pk["day"], "",
         "%d pieces today; %d signalled targets (>= %d pieces in %d days), cap %d."
         % (pk["pieces_today"], len(pk["targets"]), pk["recur"], pk["window_days"], pk["max_targets"]), ""]
    for t in pk["targets"]:
        L.append("## %s (%d in window, %d today)" % (t["target"], t["window_count"], t["today"]))
        L.append("kinds: " + ", ".join("%s %d" % kv for kv in sorted(t["kinds"].items(), key=lambda kv: -kv[1])))
        if t["today"] > len(t["pieces"]):
            L.append("(showing %d of %d)" % (len(t["pieces"]), t["today"]))
        for p in t["pieces"]:
            L.append("- [%s] %s  (%s)" % (p["kind"], p["text"], p["path"]))
        L.append("")
    if pk["unrouted"]:
        L.append("## unrouted (the Curator routes these or leaves them)")
        L += ["- [%s] %s" % (p["kind"], p["text"]) for p in pk["unrouted"][-MAX_PIECES:]]
        if len(pk["unrouted"]) > MAX_PIECES:
            L.append("(showing the newest %d of %d)" % (MAX_PIECES, len(pk["unrouted"])))
        L.append("")
    for t, why in sorted(pk.get("held", {}).items()):
        L.append("Held at level L%d: %s (%s)" % (pk.get("level", 0), t, why))
    L.append("Not signalled today: %s" % (", ".join(pk["unsignalled"]) or "none"))
    if pk["dropped_over_cap"]:
        L.append("Over the cap, left for tomorrow: %s" % ", ".join(pk["dropped_over_cap"]))
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- targets, versions, ramp

DELEGATED = os.path.join(REPO, "infrastructure", "state", "delegated")
CHANGES = os.path.join(REPO, "infrastructure", "state", "agent_improve", "changes")
ROLES = os.path.join(REPO, "src", "RimMandrake", "rimflow", "roles")
SKILLS = os.path.join(REPO, "skills")
RELENTLESS = "src/RimMandrake/rimflow/relentless.py"
# rulings, grading and counting are never the pass's to edit (survey rule 4: grading parts go to a judge and a human);
# the Conductor's role carries the owner's authority. These get a proposal line only.
PROPOSAL_ONLY_ROLES = {"auditor", "conductor"}
MAX_EDIT_LINES = 15
LEVELS = [
    {"level": 0, "interval_days": 1, "recur": 2, "window_days": 7, "min_task_kinds": 0, "need_recheck": False,
     "need_general": False},
    {"level": 1, "interval_days": 3, "recur": 3, "window_days": 14, "min_task_kinds": 2, "need_recheck": True,
     "need_general": False},
    {"level": 2, "interval_days": 7, "recur": 5, "window_days": 28, "min_task_kinds": 3, "need_recheck": True,
     "need_general": True},
]
RAMP_PASSES, RAMP_UP_BELOW, RAMP_DOWN_ABOVE = 10, 0.3, 0.6
VERDICTS = ("KEEP", "REDO", "UNSURE")


def resolve_target(t):
    """-> {path (repo-relative), region (start marker, or None for the whole file), what} or None (proposal only)."""
    if t == "relentless":
        return {"path": RELENTLESS, "region": "def worker_prompt(", "what": "the Relentless worker brief"}
    if t in PROPOSAL_ONLY_ROLES:
        return None
    if re.fullmatch(r"[a-z][a-z0-9_-]*", t or "") and os.path.isfile(os.path.join(ROLES, t + ".md")):
        return {"path": "src/RimMandrake/rimflow/roles/%s.md" % t, "region": None, "what": "the %s role file" % t}
    if re.fullmatch(r"[a-z][a-z0-9-]*", t or "") and os.path.isfile(os.path.join(SKILLS, t, "SKILL.md")):
        return {"path": "skills/%s/SKILL.md" % t, "region": None, "what": "the repo skill %s" % t}
    return None


def region_of(text, start):
    """The editable slice: the top-level function `start` names ("def worker_prompt(") from its def line to its last
    line, by the AST, so nothing between it and the next definition is editable (the whole text when start is None)."""
    if start is None:
        return 0, len(text)
    name = re.fullmatch(r"(?:async )?def (\w+)\(", start)
    fn = [n for n in ast.parse(text).body if name and isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
          and n.name == name.group(1)]
    if len(fn) != 1:
        raise ValueError("region %r: %d top-level functions match" % (start, len(fn)))
    starts = [0]
    for ln in text.splitlines(True):
        starts.append(starts[-1] + len(ln))
    return starts[fn[0].lineno - 1], starts[min(fn[0].end_lineno, len(starts) - 1)]


def last_change(t, changes_dir=None):
    best = None
    for p in glob.glob(os.path.join(changes_dir or CHANGES, "%s_v*.json" % t)):
        m = re.search(r"_v(\d+)\.json$", p)
        try:
            rec = json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), rec)
    return best[1] if best else None


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git"] + list(args), cwd=cwd or REPO, capture_output=True, text=True, timeout=300)
    if check and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args[:2]), (r.stderr or r.stdout)))
    return r.stdout


def next_version(t, changes_dir=None, cwd=None):
    n = 0
    for tag in git("tag", "-l", "agent/%s/v*" % t, cwd=cwd, check=False).split():
        m = re.search(r"/v(\d+)$", tag)
        n = max(n, int(m.group(1))) if m else n
    prior = last_change(t, changes_dir)
    if prior and prior.get("version"):
        n = max(n, int(prior["version"]))
    return n + 1


def load_state(path):
    try:
        st = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    st.setdefault("level", 0)
    st.setdefault("passes_at_last_step", 0)
    st.setdefault("last_pass_day", None)
    return st


def ramp_reading(delegated_dir=None):
    """Acceptance rate over the last RAMP_PASSES passes that proposed anything, from the committed verdict files:
    each agent_improve_<target>.json is one proposed diff; applied when it carries applied_sha."""
    days = {}
    ddir = delegated_dir or DELEGATED
    # Committed verdicts only: a refused books publish leaves files that must not move the ramp. Outside a git
    # work tree (selftest fixtures) every file on disk counts.
    base = ddir   # the nearest existing folder: HEAD holds the verdicts even if the working folder was deleted
    while not os.path.isdir(base) and os.path.dirname(base) != base:
        base = os.path.dirname(base)
    sub = os.path.relpath(ddir, base)
    r = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "--full-name", "HEAD", "--", sub], cwd=base,
                       capture_output=True, text=True, timeout=120)
    if r.returncode == 0:   # iterate HEAD itself: a deleted or edited working copy changes nothing
        top = git("rev-parse", "--show-prefix", cwd=base).strip() + ("" if sub == "." else sub.rstrip("/") + "/")
        rels = [x[len(top):] for x in r.stdout.split("\0") if x.startswith(top)
                and re.fullmatch(r"[^/]+/agent_improve_[^/]+\.json", x[len(top):])]
        load = lambda rel: json.loads(git("show", "HEAD:%s%s" % (top, rel), cwd=base))   # noqa: E731
    else:
        rels = [os.path.relpath(x, ddir) for x in glob.glob(os.path.join(ddir, "*", "agent_improve_*.json"))]
        load = lambda rel: json.load(open(os.path.join(ddir, rel), encoding="utf-8"))   # noqa: E731
    for rel in rels:
        try:
            rec = load(rel)
        except (OSError, ValueError, RuntimeError):
            continue
        p = os.path.join(ddir, rel)
        d = days.setdefault(os.path.basename(os.path.dirname(p)), [0, 0])
        d[0] += 1
        d[1] += 1 if rec.get("applied_sha") else 0
    last = sorted(days)[-RAMP_PASSES:]
    proposed = sum(days[d][0] for d in last)
    applied = sum(days[d][1] for d in last)
    return {"passes": len(days), "window": last, "proposed": proposed, "applied": applied,
            "rate": (applied / proposed) if proposed else None}


def ramp_step(st, reading):
    """At most one step per RAMP_PASSES passes; up a level (stricter) below RAMP_UP_BELOW, down above RAMP_DOWN_ABOVE."""
    if reading["passes"] < RAMP_PASSES or reading["passes"] - st["passes_at_last_step"] < RAMP_PASSES \
            or reading["rate"] is None:
        return st, None
    lvl = st["level"]
    if reading["rate"] < RAMP_UP_BELOW and lvl < len(LEVELS) - 1:
        lvl += 1
    elif reading["rate"] > RAMP_DOWN_ABOVE and lvl > 0:
        lvl -= 1
    if lvl == st["level"]:
        return st, None
    step = "L%d -> L%d at rate %.2f over %d passes" % (st["level"], lvl, reading["rate"], RAMP_PASSES)
    st = dict(st, level=lvl, passes_at_last_step=reading["passes"])
    st.setdefault("steps", []).append({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "step": step})
    return st, step


def due(st, day):
    """The level's interval: a pass on `day` is due when the last pass is at least interval_days earlier."""
    if not st.get("last_pass_day"):
        return True
    gap = (day_bounds(day)[0] - day_bounds(st["last_pass_day"])[0]) // 86400
    return gap >= LEVELS[st["level"]]["interval_days"]


# ---------------------------------------------------------------- step 1, Curator; step 2, Judge

CURATOR_RULES = """Rules (from design/RimMandrake/daily_agent_improvement_2026-11-02.md and builder_agents_survey_2026-11-02.md):
1. Evidence, not opinion. A change must fix a real failure shown by the numbered pieces; cite their numbers. No cited
   failure, no change. "none" is a valid and common answer: most days have no change worth making.
2. Fix order: a code check (a gate that refuses the mistake) beats a tool, which beats prompt or skill text. When a code
   check or a tool is the right fix, answer "proposal" with fix_layer code or tool; never paper over it with text.
3. Pointer, not paste: a text change adds or sharpens a short line that points at the existing skill, doc or tool that
   holds the knowledge. At most %d changed lines in total. Deleting or tightening a line that misled beats adding one.
4. Never change a ruling, a gate, a cap, a schedule, or a grading or counting rule. Never fit one item's quirk: the
   failure must recur across the pieces.
5. An edit's "old" is an exact substring of the TARGET TEXT, unique in it; "new" replaces it. Keep the file's style.""" % MAX_EDIT_LINES

CURATOR_REPLY = """Reply with ONE JSON object and nothing else:
{"decision": "none" | "change" | "proposal",
 "reason": "ALWAYS, one line: for none, why no change is worth making (what you checked); for the others, the failure fixed",
 "cites": [piece numbers],
 "fix_layer": "code" | "tool" | "prompt",
 "why_text": "change only: why text and not a code check",
 "edits": [{"old": "...", "new": "..."}],
 "recheck": "change only: what the next days' evidence shows if this worked, in one line",
 "proposal": "proposal only: the code check or tool to build, one paragraph",
 "prior_recheck": "pass" | "fail" | "unknown"   (only when a PRIOR CHANGE is shown: did its recheck pass?)}"""


def pieces_block(entry):
    return "\n".join("%d. [%s] %s  (%s)" % (i, p["kind"], p["text"], p["path"]) for i, p in enumerate(entry["pieces"]))


def commits_since(path, day, repo=None, n=15):
    """Subjects of commits to the target since the evidence day began: a fix that landed after the evidence must not
    be proposed again (hand run 2026-11-01: the Curator proposed a contract gate that b909e8839d had already built)."""
    if not path:
        return []
    out = git("log", "--since=%sT00:00:00Z" % day, "-n", str(n), "--format=%h %cI %s", "--", path, cwd=repo,
              check=False)
    return [ln for ln in out.splitlines() if ln.strip()]


def curator_prompt(entry, res, text, since=()):
    t = entry["target"]
    head = ["You are the Curator of the RimMandrake daily agent-improvement pass. You have no tools: everything you may",
            "use is below. Target: %s (%s)." % (t, res["what"] if res else "not editable by this pass: "
                                               "answer none or proposal only"),
            "", "EVIDENCE PIECES (%d in the window, %d today; kinds %s; task kinds %s):"
            % (entry["window_count"], entry["today"], json.dumps(entry["kinds"]), entry.get("task_kinds") or "-"),
            pieces_block(entry), ""]
    if entry.get("prior"):
        pr = entry["prior"]
        head += ["PRIOR CHANGE %s (applied %s). Its recheck: %s" % (pr.get("tag"), pr.get("day"), pr.get("recheck")),
                 "Judge from the pieces whether that recheck passed; if it failed, reverting it is a valid change.", ""]
    if since:
        head += ["COMMITS TO %s SINCE THE EVIDENCE DAY BEGAN (a failure one of these already fixed needs no change "
                 "and no proposal; say so in proposal-free \"none\"):" % res["path"]] + ["  " + c for c in since] + [""]
    if res:
        head += ["TARGET TEXT (%s):" % res["path"], "<<<", text, ">>>", ""]
    return "\n".join(head + [CURATOR_RULES, "", CURATOR_REPLY]) + "\n"


JUDGE_ASK = """You are the Judge. A different agent proposed the change below to %s, from the evidence pieces shown. You
see the evidence, the target text and the diff, not the proposer's reasoning. Decide by these written constraints:
- It fixes a failure the cited pieces actually show, and that failure recurs (not one item's quirk). Cited: %s.
- A code check or tool would not clearly be the better fix (code check > tool > text).
- Pointer, not paste: short, points at where the knowledge lives; at most %d changed lines.
- It contradicts nothing else in the target text, changes no ruling, gate, cap, schedule or grading rule.
- The recheck is something the next days' evidence could actually show: "%s".
Reply with ONE JSON object and nothing else:
{"verdict": "KEEP" | "REDO" | "UNSURE", "reasons": "two or three sentences", "violated": "REDO only: the constraint"}
KEEP only if every constraint holds; UNSURE when the constraints do not decide it."""


def judge_prompt(entry, res, text, diff, cites, recheck):
    return "\n".join([JUDGE_ASK % (res["what"], cites, MAX_EDIT_LINES, recheck), "",
                      "EVIDENCE PIECES:", pieces_block(entry), "", "TARGET TEXT (%s):" % res["path"], "<<<", text,
                      ">>>", "", "DIFF:", diff]) + "\n"


def parse_json_reply(raw):
    """The first JSON object in a model reply (prose or a code fence around it is tolerated)."""
    s = str(raw or "")
    for i, ch in enumerate(s):
        if ch == "{":
            try:
                obj, _ = json.JSONDecoder().raw_decode(s[i:])
            except ValueError:
                continue
            if isinstance(obj, dict):
                return obj
    raise ValueError("no JSON object in the reply")


def claude_fresh(prompt, timeout=420, model_name="opus"):
    """One fresh, tool-less `claude -p` session in an empty temp dir: no repo context, no memory, no MCP."""
    with tempfile.TemporaryDirectory(prefix="agent_improve_") as d:
        r = subprocess.run([shutil.which("claude") or os.path.expanduser("~/.local/bin/claude"), "-p", "--model", model_name, "--tools", "", "--no-session-persistence",
                            "--strict-mcp-config"], input=prompt, capture_output=True, text=True, cwd=d,
                           timeout=timeout)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("claude -p exit %d: %s" % (r.returncode, (r.stderr or "")))
    return r.stdout


def build_change(entry, res, full, reply):
    """Validate a Curator reply against the packet and the target -> (new full text, diff, problems)."""
    probs = []
    cites = reply.get("cites") or []
    if not cites or not all(isinstance(c, int) and 0 <= c < len(entry["pieces"]) for c in cites):
        probs.append("cites must name piece numbers 0..%d (rule 3: a change cites the failure it fixes)"
                     % (len(entry["pieces"]) - 1))
    if reply.get("fix_layer") != "prompt":
        probs.append("fix_layer %r: a code check or tool is proposed, never written as text (rule 4)"
                     % reply.get("fix_layer"))
    if not str(reply.get("recheck") or "").strip():
        probs.append("no recheck line")
    edits = reply.get("edits") or []
    if not edits:
        probs.append("no edits")
    a, b = region_of(full, res["region"])
    region = full[a:b]
    for e in edits:
        old, new = (e or {}).get("old"), (e or {}).get("new")
        if not isinstance(old, str) or not isinstance(new, str) or not old:
            probs.append("an edit lacks old/new text")
            continue
        if region.count(old) != 1 or full.count(old) != 1:
            probs.append("old text not unique in the target (%d in region, %d in file): %r"
                         % (region.count(old), full.count(old), old[:80]))
            continue
        region = region.replace(old, new, 1)
    new_full = full[:a] + region + full[b:]
    if res["region"]:   # "new" must not move code out of the function either (a dedented global, a new def)
        try:
            a2, b2 = region_of(new_full, res["region"])
            inside = new_full[:a2] == full[:a] and new_full[b2:] == full[b:]
        except (SyntaxError, ValueError) as e:
            inside, probs = True, probs + ["the edited file does not parse: %s" % str(e)]
        if not inside:
            probs.append("the edit reaches outside %s" % res["region"])
    diff = "".join(difflib.unified_diff(full.splitlines(True), new_full.splitlines(True),
                                        "a/" + res["path"], "b/" + res["path"]))
    body = diff.splitlines()[2:]   # past the ---/+++ header pair; "++x" in the body is an added "+x"
    plus = sum(1 for ln in body if ln.startswith("+"))
    minus = sum(1 for ln in body if ln.startswith("-"))
    if max(plus, minus) > MAX_EDIT_LINES:   # the cap is per side: a 15-line rewrite is 15 lines
        probs.append("%d added / %d removed lines, cap %d" % (plus, minus, MAX_EDIT_LINES))
    if not diff and not probs:
        probs.append("the edits change nothing")
    return new_full, diff, probs


def curate_and_judge(entry, day, outdir, curator=None, judge=None, repo=None):
    """Steps 1 and 2 for one target -> a result row. Writes the Curator and Judge replies and the diff to outdir."""
    curator, judge, repo = curator or claude_fresh, judge or claude_fresh, repo or REPO
    t = entry["target"]
    res = resolve_target(t)
    full = open(os.path.join(repo, res["path"]), encoding="utf-8").read() if res else ""
    text = full[slice(*region_of(full, res["region"]))] if res else ""
    row = {"target": t, "day": day, "path": res["path"] if res else None, "decision": None}
    try:
        raw = curator(curator_prompt(entry, res, text, commits_since(res and res["path"], day, repo)))
        reply = parse_json_reply(raw)
    except (RuntimeError, ValueError, subprocess.SubprocessError) as e:
        row.update(decision="error", error="curator: %s" % str(e))
        return row
    with open(os.path.join(outdir, "%s.curator.json" % t), "w", encoding="utf-8") as f:
        json.dump({"reply": reply, "raw": raw}, f, indent=1)
    row["decision"] = reply.get("decision")
    row["prior_recheck"] = reply.get("prior_recheck") if entry.get("prior") else None
    row["prior_version"] = (entry.get("prior") or {}).get("version")   # the change the recheck is about
    if row["decision"] == "proposal":
        row["proposal"] = str(reply.get("proposal") or "")
        row["fix_layer"] = reply.get("fix_layer")
        return row
    if row["decision"] != "change":
        row["decision"] = "none"
        row["reason"] = first_line(str(reply.get("reason") or ""), 300)
        if not row["reason"]:   # a reasonless none cannot be told from a skim
            row.update(decision="error", error="curator: no reason given")
        return row
    if not res:
        row.update(decision="refused", problems=["target is proposal-only"])
        return row
    if entry.get("recheck_only") and row["prior_recheck"] != "pass":
        row.update(decision="refused", problems=["held: the prior change's recheck reads %r, not pass"
                                                 % row["prior_recheck"]])
        return row
    new_full, diff, probs = build_change(entry, res, full, reply)
    if probs:
        row.update(decision="refused", problems=probs)
        return row
    with open(os.path.join(outdir, "%s.diff" % t), "w", encoding="utf-8") as f:
        f.write(diff)
    row.update(diff=diff, cites=reply["cites"], recheck=str(reply["recheck"]), why_text=reply.get("why_text"),
               new_text=new_full)
    try:
        jraw = judge(judge_prompt(entry, res, text, diff, reply["cites"], row["recheck"]))
        jv = parse_json_reply(jraw)
    except (RuntimeError, ValueError, subprocess.SubprocessError) as e:
        jv, jraw = {"verdict": "UNSURE", "reasons": "judge failed: %s" % str(e)}, ""
    v = str(jv.get("verdict") or "").upper()
    row["verdict"] = v if v in VERDICTS else "UNSURE"
    row["judge"] = {"reasons": str(jv.get("reasons") or ""), "violated": str(jv.get("violated") or "")}
    with open(os.path.join(outdir, "%s.judge.json" % t), "w", encoding="utf-8") as f:
        json.dump({"reply": jv, "raw": jraw}, f, indent=1)
    return row


def verdict_record(row, entry):
    return {"subject": "agent_improve_%s" % row["target"], "item": "AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS",
            "day": row["day"], "target": row["target"], "path": row["path"],
            "maker": "agent_improve Curator (fresh claude -p opus, no tools)",
            "judge_model": "fresh claude -p opus, no tools, blind to the Curator's reasoning",
            "verdict": row["verdict"], "reasons": row["judge"]["reasons"], "violated": row["judge"]["violated"],
            "cites": [{"path": entry["pieces"][c]["path"], "text": entry["pieces"][c]["text"],
                       "task_kind": task_kind(entry["pieces"][c])} for c in row["cites"]],
            "recheck": row["recheck"], "diff": row["diff"], "applied_sha": None, "tag": None}


# ---------------------------------------------------------------- step 3, apply

def selftests_for(res, repo=None):
    """The target's selftests: the worker brief's own, else every selftest that names the target's path."""
    repo = repo or REPO
    if res["path"] == RELENTLESS:
        return ["src/RimMandrake/rimflow/selftest_relentless.py"]
    needle = res["path"] if res["path"].startswith("src/") else os.path.dirname(res["path"]) + "/"
    out = []
    for p in sorted(glob.glob(os.path.join(repo, "src", "RimMandrake", "**", "selftest_*.py"), recursive=True)):
        if os.path.basename(p).startswith("selftest_agent_improve"):
            continue   # this pass's own tests name targets as fixtures
        try:
            if needle in open(p, encoding="utf-8", errors="replace").read():
                out.append(os.path.relpath(p, repo))
        except OSError:
            pass
    return out


def run_checks(res, repo):
    """-> list of problems; empty means the applied change passed every check."""
    cmds = []
    if res["path"].endswith(".py"):
        cmds.append([sys.executable, "-m", "py_compile", res["path"]])
    if res["path"].startswith("skills/"):
        cmds.append([sys.executable, "skills/validate_skills.py", res["path"].split("/")[1]])
    tests = selftests_for(res, repo)
    if tests:
        cmds.append([sys.executable, "src/RimMandrake/Utils/run_selftests.py", "--only"] + tests)
    probs = []
    for c in cmds:
        r = subprocess.run(c, cwd=repo, capture_output=True, text=True, timeout=540)
        if r.returncode != 0:
            probs.append("%s exit %d: %s" % (" ".join(c[1:3]), r.returncode, (r.stdout + r.stderr)))
    return probs


def source_kinds(row, entry):
    return sorted({task_kind(entry["pieces"][c]) for c in row.get("cites") or ()} - {None})


def general_gate(row, entry, res, outdir, repo, general, changes_dir=None):
    """L2: the generalization check (4.3) on the HEAD text against the proposed one, before anything is applied.
    general(t, old_text, new_text, source_kinds) -> result (agent_improve_general.check). Its evidence is written to
    outdir (a refusal leaves nothing in the repo); _prepare_record copies it beside the change records (changes/../
    general/) so publish commits it with the change. -> (ok, detail)."""
    import agent_improve_general as G   # noqa: E402  (it imports this module)
    if general is None:
        return False, "this level needs a generalization check before apply; no checker was given"
    if not row.get("new_text"):
        return False, "generalization check: the row carries no proposed text"
    kinds = source_kinds(row, entry)
    if not kinds:   # nothing would be excluded from the sample: its "held-out" pairs are not held out
        return False, "generalization check: the cited pieces yield no source kinds, so nothing can be held out"
    old = open(os.path.join(repo, res["path"]), encoding="utf-8").read()
    try:
        g = general(row["target"], old, row["new_text"], kinds)
    except Exception as e:   # a crashed check is not a pass
        return False, "generalization check crashed: %s" % str(e)
    refs = {"old": "HEAD", "new": "proposed"}
    try:
        gpath, rel = G.write_evidence(g, "%s_proposed" % row["target"], outdir, repo, refs=refs)
    except Exception as e:
        return False, "generalization check: evidence not written: %s" % str(e)
    row["general"] = G.summary(g, rel, refs)
    row["general_path"] = gpath
    ok, why = G.gate_passes(g)
    if not ok:
        return False, "generalization check: %s (%s)" % (why, gpath)
    return True, why


def apply_change(row, entry, outdir, repo=None, publish=None, changes_dir=None, delegated_dir=None, pk_level=0,
                 general=None):
    """KEEP only. Check, apply, test, publish with `Delegated: technical`, tag, record. Any refusal reverses the diff
    and leaves it in outdir. At a level that needs it, `general` (the 4.3 check) must keep the change first.
    -> (ok, detail)."""
    repo = repo or REPO
    changes_dir, delegated_dir = changes_dir or CHANGES, delegated_dir or DELEGATED
    t, res = row["target"], resolve_target(row["target"])
    if git("status", "--porcelain", "--", res["path"], cwd=repo).strip():
        return False, "%s has uncommitted edits; refusing to mix" % res["path"]
    if LEVELS[pk_level]["need_general"]:   # after the clean check, so the gate's "old" text is HEAD's
        ok, why = general_gate(row, entry, res, outdir, repo, general, changes_dir)
        if not ok:
            return False, "level L%d: %s" % (pk_level, why)
    # Apply the diff the Judge saw (row["diff"]), never the outdir copy another run could have rewritten.
    fd, dpath = tempfile.mkstemp(suffix=".diff")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(row["diff"])
    try:
        return _apply_checked(row, entry, res, t, dpath, repo, publish, changes_dir, delegated_dir)
    finally:
        os.remove(dpath)


def _apply_checked(row, entry, res, t, dpath, repo, publish, changes_dir, delegated_dir):
    r = subprocess.run(["git", "apply", "--check", dpath], cwd=repo, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return False, "git apply --check: %s" % r.stderr
    git("apply", dpath, cwd=repo)
    try:
        probs = run_checks(res, repo)
    except Exception as e:   # a timeout or crash must not leave the edit applied
        probs = ["checks crashed: %s" % str(e)]
    if probs:
        git("apply", "-R", dpath, cwd=repo)
        return False, "; ".join(probs)
    try:
        head = git("rev-parse", "HEAD", cwd=repo).strip()
        n, tag, vrec, vpath, cpath, msg, paths = _prepare_record(row, entry, res, t, repo, changes_dir, delegated_dir)
    except Exception as e:   # nothing may stay applied or half-written before publish
        git("apply", "-R", dpath, cwd=repo, check=False)
        if row.get("repo_general_path") and os.path.isfile(row["repo_general_path"]):
            os.remove(row["repo_general_path"])
        return False, "preparing the change record failed: %s" % str(e)
    return _publish_and_tag(row, res, dpath, repo, publish, vrec, vpath, cpath, msg, paths, tag, head)


def _prepare_record(row, entry, res, t, repo, changes_dir, delegated_dir):
    n = next_version(t, changes_dir, cwd=repo)
    tag = "agent/%s/v%d" % (t, n)
    vrec = verdict_record(row, entry)
    vpath = row.get("verdict_file") or free_verdict_path(delegated_dir, row["day"], t)
    cpath = os.path.join(changes_dir, "%s_v%d.json" % (t, n))
    if row.get("general_path"):   # the gate's outdir evidence, copied into the repo only now that it is publishing
        import agent_improve_general as G   # noqa: E402
        g = json.load(open(row["general_path"], encoding="utf-8"))
        gdir = os.path.join(os.path.dirname(os.path.abspath(changes_dir)), "general")
        row["repo_general_path"], rel = G.write_evidence(g, "%s_v%d_proposed" % (t, n), gdir, repo)
        row["general"] = dict(row["general"], evidence=rel)
    change = {"target": t, "version": n, "tag": tag, "day": row["day"], "path": res["path"],
              "pieces": vrec["cites"], "source_kinds": source_kinds(row, entry),
              "diff": row["diff"], "verdict": os.path.relpath(vpath, repo), "recheck": row["recheck"],
              "recheck_result": None, "rechecks": [], "generalization": [row["general"]] if row.get("general") else []}
    os.makedirs(os.path.dirname(cpath), exist_ok=True)
    try:
        f = open(cpath, "x", encoding="utf-8")   # never overwrite a record someone left (e.g. an unpublished v<N>)
    except FileExistsError:
        raise RuntimeError("%s already exists; refusing to overwrite it" % cpath) from None
    try:
        with f:
            json.dump(change, f, indent=1)
    except Exception:
        os.remove(cpath)
        raise
    msg = ("AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS: %s v%d from %s evidence\n\n"
           "Delegated: technical — agent improvement %s\nJudge KEEP: %s\nChange record: %s\n"
           % (t, n, row["day"], t, os.path.relpath(vpath, repo), os.path.relpath(cpath, repo)))
    paths = [res["path"], os.path.relpath(cpath, repo)]
    if row.get("repo_general_path"):
        paths.append(os.path.relpath(row["repo_general_path"], repo))   # the gate's evidence travels (design 4.4)
    return n, tag, vrec, vpath, cpath, msg, paths


def _publish_and_tag(row, res, dpath, repo, publish, vrec, vpath, cpath, msg, paths, tag, head):
    try:
        ok, sha = (publish or publish_paths)(msg, paths, repo)
    except Exception as e:
        ok, sha = False, "crashed: %s" % str(e)
    if not ok:
        if git("rev-parse", "HEAD", cwd=repo).strip() != head:
            # ./publish refuses after committing and leaves the commit on HEAD: never rewrite it, say so.
            return False, "publish: %s (its commit is left on HEAD for a human)" % sha
        git("reset", "-q", "--", *paths, cwd=repo, check=False)   # unstage only these paths
        git("apply", "-R", dpath, cwd=repo)
        os.remove(cpath)
        if row.get("repo_general_path"):
            os.remove(row["repo_general_path"])
        return False, "publish: %s" % sha
    vrec.update(applied_sha=sha, tag=tag, change=os.path.relpath(cpath, repo))
    write_verdict(vpath, vrec)
    git("tag", tag, sha, cwd=repo, check=False)
    tagged = git("rev-parse", "-q", "--verify", "refs/tags/%s^{commit}" % tag, cwd=repo, check=False).strip()
    if not sha or not tagged.startswith(sha):
        return True, "%s published, but tag %s resolves to %r, not it" % (sha, tag, tagged)
    pushed = subprocess.run(["git", "push", "origin", "refs/tags/%s" % tag], cwd=repo, capture_output=True,
                            text=True, timeout=300).returncode == 0
    return True, "%s %s%s" % (tag, sha, "" if pushed else " (tag push FAILED; local tag only)")


def free_verdict_path(delegated_dir, day, t):
    """A verdict record is never overwritten: a forced rerun of the same day takes the next free name, and the ramp
    counts it as one more proposal."""
    base = os.path.join(delegated_dir or DELEGATED, day, "agent_improve_%s" % t)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    k, p = 1, base + ".json"
    while True:
        try:   # reserve the name: a concurrent pass can never pick the same file; this pass then owns it
            os.close(os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            return p
        except FileExistsError:
            k += 1
            p = "%s.run%d.json" % (base, k)


def write_verdict(vpath, vrec):
    os.makedirs(os.path.dirname(vpath), exist_ok=True)
    with open(vpath, "w", encoding="utf-8") as f:
        json.dump(vrec, f, indent=1)


def publish_paths(msg, paths, repo):
    """git add the named paths (new files need it), then ./publish -F; -> (ok, sha or the refusal)."""
    git("add", "--", *paths, cwd=repo)
    with tempfile.NamedTemporaryFile("w", suffix=".msg", delete=False) as f:
        f.write(msg + "\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    try:
        r = subprocess.run([os.path.join(repo, "publish"), "-F", f.name] + paths, cwd=repo, capture_output=True,
                           text=True, timeout=540)
    finally:
        os.unlink(f.name)
    m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", r.stdout + r.stderr)
    return (True, m.group(1)) if r.returncode == 0 and m else (False, (r.stdout + r.stderr))


def record_rechecks(rows, changes_dir=None, saved=None):
    """The Curator's read of each prior change's recheck, appended to that change record. -> the records touched."""
    touched = []
    for row in rows:
        if row.get("prior_recheck") not in ("pass", "fail", "unknown"):
            continue
        if not row.get("prior_version"):
            continue
        # The version the Curator was shown, never last_change(): a change applied in this same pass is newer.
        p = os.path.join(changes_dir or CHANGES, "%s_v%d.json" % (row["target"], row["prior_version"]))
        if os.path.exists(p) and git("status", "--porcelain", "--", os.path.basename(p), cwd=os.path.dirname(p),
                                     check=False).strip():
            continue   # someone's uncommitted edit: never fold it into the books commit
        try:
            old = open(p, encoding="utf-8").read()
            prior = json.loads(old)
        except (OSError, ValueError):
            continue
        if saved is not None:
            saved.setdefault(p, old)   # so a books publish that fails can put the record back
        prior.setdefault("rechecks", []).append({"day": row["day"], "result": row["prior_recheck"], "by": "curator"})
        if row["prior_recheck"] != "unknown":
            prior["recheck_result"] = row["prior_recheck"]
        tmp = p + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:   # atomic: a failed write never truncates the record
                json.dump(prior, f, indent=1)
            os.replace(tmp, p)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        touched.append(p)
    return touched


# ---------------------------------------------------------------- the pass

def run_pass(day, out, apply=False, only=None, curator=None, judge=None, repo=None, src=None, state_path=None,
             changes_dir=None, delegated_dir=None, publish=None, force=False, general=None, cadence=None):
    """cadence(day=, level=, repo=, changes_dir=, publish=) -> rows: the generalization step, after an --apply pass whose
    books published (default agent_improve_cadence.run_due, which spends model calls when a check is due)."""
    state_path = state_path or os.path.join(out, "state.json")
    st = load_state(state_path)
    if not force and not due(st, day):
        return {"day": day, "skipped": "level L%d runs every %d days; last pass %s"
                % (st["level"], LEVELS[st["level"]]["interval_days"], st["last_pass_day"])}
    pk = gather(day, src or default_src(), LEVELS[st["level"]], changes_dir)
    d = os.path.join(out, day)
    os.makedirs(d, exist_ok=True)
    rows = []
    # A dry run (no --apply) writes nothing the repo or the ramp reads: verdicts go to the scratch day folder.
    vdir = (delegated_dir or DELEGATED) if apply else os.path.join(d, "verdicts")
    for entry in pk["targets"]:
        if only and entry["target"] not in only:
            continue
        row = curate_and_judge(entry, day, d, curator, judge, repo)
        rows.append(row)
        if row.get("verdict"):
            vpath = free_verdict_path(vdir, day, row["target"])
            write_verdict(vpath, verdict_record(row, entry))
            row["verdict_file"] = vpath
        if apply and row.get("verdict") == "KEEP":
            row["applied"], row["apply_detail"] = apply_change(row, entry, d, repo, publish, changes_dir,
                                                               delegated_dir, st["level"], general or default_general)
    saved = {}
    head = git("rev-parse", "HEAD", cwd=repo or REPO).strip() if apply else None   # before anything is written
    try:
        touched = record_rechecks(rows, changes_dir, saved) if apply else []
    except Exception:   # put back what was written before the failure, then fail loudly
        for p, old in saved.items():
            with open(p, "w", encoding="utf-8") as f:
                f.write(old)
        raise
    books_ok = apply
    if apply:
        books = [r["verdict_file"] for r in rows if r.get("verdict_file")] + touched
        if books:
            rel = [os.path.relpath(b, repo or REPO) for b in books]
            try:
                ok, detail = (publish or publish_paths)(
                    "AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS: %s verdicts and rechecks\n\n"
                    "Delegated: technical — agent improvement verdicts %s\n" % (day, day), rel, repo or REPO)
            except Exception as e:
                ok, detail = False, "crashed: %s" % str(e)
            if not ok and git("rev-parse", "HEAD", cwd=repo or REPO).strip() == head:
                # nothing committed: an unpublished recheck must not lift an L1 hold, so put the records back
                git("reset", "-q", "--", *rel, cwd=repo or REPO, check=False)
                for p, old in saved.items():
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(old)
            rows.append({"target": "(books)", "decision": "published" if ok else "NOT published", "day": day,
                         "apply_detail": detail})
            books_ok = ok
    reading, step = ramp_reading(delegated_dir), None
    if books_ok:   # the ramp moves, and the pass counts as run, only once its verdicts are committed
        st, step = ramp_step(st, reading)
        st["last_pass_day"] = day
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=1)
    import agent_improve_cadence as C   # noqa: E402  (it imports this module)
    checks = []
    if books_ok and not only:   # a dry run, refused books or a hand run split by --target: the records keep what is due
        checks = (cadence or C.run_due)(day=day, level=st["level"], repo=repo or REPO,
                                        changes_dir=changes_dir or CHANGES, publish=publish)
    summary = {"day": day, "level": pk["level"], "targets": [e["target"] for e in pk["targets"]],
               "rows": [{k: v for k, v in r.items() if k not in ("new_text",)} for r in rows],
               "ramp": reading, "ramp_step": step, "checks": checks,
               "narrow": C.narrow_counts(changes_dir or CHANGES)}
    # a pass split by --target (a hand run inside a command time limit) writes one result file per target
    name = "pass_%s" % "_".join(sorted(only)) if only else "pass"
    with open(os.path.join(d, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(d, "packet.json"), "w", encoding="utf-8") as f:
        json.dump(pk, f, indent=1)
    with open(os.path.join(d, "packet.md" if not only else name + ".md"), "w", encoding="utf-8") as f:
        f.write((render(pk) if not only else "") + render_pass(summary))
    return summary


def render_pass(s):
    L = ["", "## Pass results (level L%d)" % s["level"]]
    for r in s["rows"]:
        line = "- %s: %s" % (r["target"], r["decision"])
        if r.get("reason"):
            line += " (%s)" % r["reason"]
        if r.get("error"):
            line += " [%s]" % r["error"]
        if r.get("verdict"):
            line += ", Judge %s (%s)" % (r["verdict"], r["judge"]["reasons"])
        if "applied" in r:
            line += ", applied: %s" % r["apply_detail"] if r["applied"] else ", NOT applied: %s" % r["apply_detail"]
        if r.get("problems"):
            line += ": " + "; ".join(r["problems"])
        L.append(line)
    props = [r for r in s["rows"] if r.get("decision") == "proposal"]
    if props:
        L += ["", "## Proposals (code checks, tools, non-editable targets: for the Conductor)"]
        L += ["- %s [%s]: %s" % (r["target"], r.get("fix_layer"), r.get("proposal")) for r in props]
    import agent_improve_cadence as C   # noqa: E402  (it imports this module)
    L += ["", "## Generalization checks"]
    L += [check_line(c) for c in s.get("checks") or ()] or ["- none due"]
    L += ["", C.narrow_line(s.get("narrow"))]
    return "\n".join(L) + "\n"


def check_line(c):
    line = "- %s v%d (%s): %s" % (c["target"], c["version"], c["why"], c.get("verdict") or c.get("detail"))
    if c.get("verdict") and not c.get("published"):
        line += ", NOT published: %s" % c.get("detail")
    if c.get("revert"):
        line += ", revert %s: %s" % (c["revert"], c.get("revert_detail"))
    return line


def materialize(t, version, dest, repo=None):
    """Write the target's file as of tag agent/<t>/v<N> under dest (a skill: its whole folder)."""
    repo = repo or REPO
    tag = "agent/%s/%s" % (t, version)
    res = resolve_target(t)
    if not res:
        raise ValueError("%s is not an editable target" % t)
    path = os.path.dirname(res["path"]) if res["path"].startswith("skills/") else res["path"]
    os.makedirs(dest, exist_ok=True)
    arch = subprocess.run(["git", "archive", tag, "--", path], cwd=repo, capture_output=True, timeout=120)
    if arch.returncode != 0:
        raise RuntimeError(arch.stderr.decode(errors="replace"))
    subprocess.run(["tar", "-x", "-C", dest], input=arch.stdout, check=True, timeout=120)
    return os.path.join(dest, path)


def default_general(t, old_text, new_text, kinds):
    import agent_improve_general as G   # noqa: E402  (it imports this module)
    return G.check(t, old_text, new_text, kinds)


def default_src():
    return {"lessons": os.path.join(REPO, "infrastructure", "state", "lessons"), "store": STORE,
            "ops_alarms": OPS_ALARMS, "owner": os.path.join(REPO, "infrastructure", "state", "ledger", "events",
                                                            "OWNER.jsonl")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gather")
    g.add_argument("--day", help="UTC day, default yesterday")
    g.add_argument("--out", default=OUT)
    g.add_argument("--dry-run", action="store_true", help="print the packet, write nothing")
    r = sub.add_parser("run", help="gather, Curator, Judge; --apply also applies each KEEP")
    r.add_argument("--day", help="UTC day, default yesterday")
    r.add_argument("--out", default=OUT)
    r.add_argument("--apply", action="store_true")
    r.add_argument("--target", action="append", help="only these targets (repeatable)")
    r.add_argument("--force", action="store_true", help="run even when the level's interval says not due")
    sub.add_parser("ramp", help="print the level, the acceptance rate and whether a step is due")
    m = sub.add_parser("materialize", help="write a target as of agent/<target>/v<N> into a dir")
    m.add_argument("target")
    m.add_argument("version")
    m.add_argument("dest")
    gn = sub.add_parser("general", help="the generalization check (4.3) on agent/<target>/v<N>, recorded")
    gn.add_argument("target")
    gn.add_argument("version")
    gn.add_argument("--days", type=int, default=14)
    gn.add_argument("--seed", type=int)
    gs = sub.add_parser("general-show", help="exit 0 when v<N> holds a judged generalization entry")
    gs.add_argument("target")
    gs.add_argument("version")
    a = ap.parse_args(argv)
    if a.cmd in ("general", "general-show"):
        import agent_improve_general as G   # noqa: E402
        if a.cmd == "general-show":
            rc, lines = G.show(a.target, a.version)
            print("\n".join(lines))
            return rc
        res, (epath, cpath) = G.run_for_version(a.target, a.version, seed=a.seed, days=a.days)
        print(json.dumps({k: res[k] for k in ("verdict", "keep", "held_out", "null_held_out", "source", "null_source", "seed")}))
        print("WROTE %s; appended to %s" % (epath, cpath))
        return 0
    if a.cmd == "ramp":
        st = load_state(os.path.join(OUT, "state.json"))
        rd = ramp_reading()
        print(json.dumps({"state": st, "reading": rd, "would_step": ramp_step(st, rd)[1]}, indent=1))
        return 0
    if a.cmd == "materialize":
        print(materialize(a.target, a.version, a.dest))
        return 0
    day = a.day or time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400))
    if a.cmd == "run":
        s = run_pass(day, a.out, apply=a.apply, only=set(a.target or ()), force=a.force)
        print(json.dumps({k: s.get(k) for k in ("day", "skipped", "level", "targets", "ramp_step")}))
        for row in s.get("rows", []):
            print("%s: %s %s %s" % (row["target"], row["decision"], row.get("verdict") or "",
                                    row.get("apply_detail") or "; ".join(row.get("problems") or [])))
        for c in s.get("checks", []):
            print(check_line(c))
        return 0
    lv = LEVELS[load_state(os.path.join(a.out, "state.json"))["level"]]
    pk = gather(day, default_src(), lv)
    md = render(pk)
    if a.dry_run:
        sys.stdout.write(md)
        return 0
    d = os.path.join(a.out, day)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "packet.json"), "w", encoding="utf-8") as f:
        json.dump(pk, f, indent=1)
    with open(os.path.join(d, "packet.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("WROTE %s (%d pieces, %d targets)" % (d, pk["pieces_today"], len(pk["targets"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
