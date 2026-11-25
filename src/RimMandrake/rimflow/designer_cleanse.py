#!/usr/bin/env python3
"""Designer Cleanse: the launcher of the cleansing pass that redefines a mod before it is built further.

Item RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED. Spec design/specs/2026-11-16-designer-cleanse-and-bar-
definition.md (§4 the run and the whole-mod check, §5 this build plan). The run's brief is roles/designer_cleanse.md,
everything below its `---` line, followed by the CASE this program writes. The owner, 2026-11-16: "implement the thing
and dispatch it on every remaining biome other than Pyrelands! Every single one... let this thing go crazy."

  designer_cleanse.py case <Mod>                      print the CASE section a run receives
  designer_cleanse.py run <Mod> [--runner codex|claude] [--model M] [--effort E]
        a pool clone; the brief plus the CASE to the agent (Codex through agent_runner and its weekly quota gate: a
        refusal is a wait and a retry, never a failure and never a fall back to Claude); the self-check, one shape-fix
        pass when it refuses; then THIS program, not the agent, commits only design/concepts/<Mod>/cleanse/ and
        publishes it. No wall-clock limit.
  designer_cleanse.py check <dir>                     the proposal's mechanical shape (exit 0 passes, 1 refuses)
  designer_cleanse.py review <Mod> [--author codex|claude]
        the whole-mod check (spec §4): a fresh reviewer on the OTHER model, read-only, given his words and the source
        before the proposal; it sorts each bar's pictures blind; one fix run by the author, one second look; what the
        second look still refuses goes on his pages in the reviewer's words and result.json reads applyable false.
  designer_cleanse.py converge <Mod>
        the converge round (Conductor 2026-11-17): the latest verdict's open records only, to the author for a fix and
        fixes.json; a read-only verifier on the other model judges each record against its would_pass, shown only the
        entries the fix changed; a finding on an entry the fix did not change is advisory_late (the earlier look's
        miss), never open. Stranger records are sorted cold again, self_check records are the self-check's. At most two
        rounds; converge.json is the verdict; applyable = nothing open and the check passes.
  designer_cleanse.py fleet --all-biomes-but Pyrelands [--parallel 4] [--only A,B] [--runner codex] [--converge]
        detached in its own systemd user unit (--foreground runs it here); resumable; status in
        D:\\ClaudeWork\\rimmandrake\\designer_cleanse\\status.json and status.md, per-mod logs beside them. --converge
        runs the converge round on every reviewed mod, fewest open records first.
  designer_cleanse.py apply <Mod> [--repo R]
        dry run: what applying the converged proposal would write into design/concepts/<Mod>/ (tree.json, sheet.md,
        stage.json held blocked, version/VERSION.json 0.1.0, later_version.md's one next-version section), or why not.
        Exit 0 WOULD_WRITE, 3 NOTHING_TO_APPLY, 1 REFUSED, 4 COULD_NOT_LOOK. --write installs it, all or none, once
        the owner's plan (cleanse_plan.py) reads APPROVED: exit 0 WROTE, 5 WRITE_FAILED (ROLLED_BACK, or
        ROLLBACK_INCOMPLETE naming what it could not restore).
  designer_cleanse.py gather      every mod's pages, questions and retirements in one ALL_BIOMES.md beside the status
  designer_cleanse.py status

The owner's hold (mod_owner_hold.json) stays on builds; `run` refuses a held mod unless its hold row carries his words
for a design-only pass (mod_owner_hold.py allow-design). Nothing here launches a build, a chain or a Dispatch run.
Selftest: selftest_designer_cleanse.py.
"""
import effort as EF  # the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
import argparse
import concurrent.futures
import contextlib
import datetime
import fcntl
import json
import os
import random
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bar_rule            # noqa: E402
import fulltext  # noqa: E402
import failure_class as FC  # noqa: E402
import mod_owner_hold as MH  # noqa: E402

try:                       # the real gate's refusal, so a caught Refused is the gate's own
    from agent_runner import Refused   # noqa: E402
except Exception:          # noqa: BLE001  agent_runner needs the image skill's scripts; the check must run without them
    class Refused(RuntimeError):
        pass

BRIEF = os.path.join("src", "RimMandrake", "rimflow", "roles", "designer_cleanse.md")
SPEC = os.path.join("design", "specs", "2026-11-16-designer-cleanse-and-bar-definition.md")
COMPOSE = os.path.join("src", "RimMandrake", "Biomes.compose.json")
ME = "src/RimMandrake/rimflow/designer_cleanse.py"
FILES = ("owner_pages.md", "definition.md", "census.json", "ambiguities.md", "bars.json", "models.md",
         "next_version.md", "tickets.md", "result.json")
BLOCKED_FILES = ("owner_pages.md", "result.json")
FATES = ("land", "life", "signature", "needed_by", "dependency", "next_version", "recommend_retire")
KEPT = ("land", "life", "signature", "needed_by", "dependency")
BUILT = ("present", "absent", "unknown")
PROVEN = ("current", "stale", "missing", "unknown")
OLD_TO = ("kept", "merged", "check", "rule", "moved", "dropped")
HOLDS = ("argued", "measured", "unknown")
COUNT_KEYS = ("capabilities", "kept", "next_version", "recommend_retire", "old_bars", "bars", "live_only_bars",
              "checks", "rules", "unknown_pairs", "models", "tickets", "questions")
PAGE_WORDS = 950        # bar: the brief's "at most two pages (about 900 words)"; 950 is the Conductor's limit for check
QUESTIONS = 5           # bar: the brief's "the questions, at most five"
STILL_REFUSED_HEAD = "## Still refused after the second look (the reviewer's words)"
# the concept-folder six first, in the Conductor's order (brief 2026-11-16), then the rest of the biomes
CONCEPT_FIRST = ("LeaningScrub", "Contagion", "Cauldron", "FeverWood", "Stillsand", "GelatinousSlime")
LORE = ("CLAUDE.md", "design/RimMandrake/biome_rulings.md", "design/RimMandrake/standing_rulings.md",
        "design/RimMandrake/biome_mod_architecture.md", "design/NAMING_SCHEME_PLAN.md",
        "design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md", "design/Jawa/worldbuilding/the_one_map.md",
        "design/Jawa/worldbuilding/Alien_Bestiary.md")
# a bare numeral in a bar: not a version string (0.1.0) and not a digit inside a name (RM_Vent2, B1)
NUMERAL = re.compile(r"(?<![\w.])[-\u2212+]?\d+(?:[.,]\d+)?(?!\w|[.,]\d)|\bper ?cent\b", re.I)
QUOTA = re.compile(r"usage.?limit|quota|rate.?limit|too many requests|\b429\b|Refused: Codex weekly", re.I)
QUOTA_WAIT_S = 1800     # a fact of the gate: the weekly meter moves slowly; half an hour between readings
HEADS = {   # spec §4, the whole-mod check's heads, and only these (plus the launcher's own blind-sort score)
    "cannot_hold_together": "two bars, or a bar and a rule, that cannot hold together",
    "kept_mechanic_undefined": "a kept mechanic with no definition",
    "reads_with_mechanic_off": "an instrument or scene that would read with a mechanic off or the sky locked",
    "number_in_bar": "a number, count or \"every field\" in a bar",
    "figurative_unmarked": "a figurative word unmarked",
    "check_or_rule_as_bar": "a rule or check dressed as a bar",
    "no_range": "a bar with no range",
    "extra_without_argument": "an extra left in the first version without its needed_by deletion argument",
    "contradicts_ruling_or_lore": "a contradiction with a standing ruling or the lore",
    "moved_extra_relied_on": "a moved extra still relied on by a kept bar",
    "core_promise_weakened": "a sourced core promise omitted or weakened",
    "evidence_cannot_tell": "evidence that cannot tell success from a plausible false pass",
    "authority_unsourced": "a claim of his authority with no source",
    "stranger": "a cold reader sorted a bar's pictures differently from the proposal (the Stranger test: repair)",
    "self_check": "after the author's fix the self-check refuses the proposal's shape",
    "regression": "the converge fix broke an entry it changed (the verifier's words)",
}
LAUNCHER_HEADS = ("stranger", "self_check")     # written by this program from its own readings, never by the reviewer
CONVERGE_HEADS = ("regression",)                # written only from a converge verifier's answer
CONVERGE_ROUNDS = 2     # the Conductor 2026-11-17: "At most two converge rounds per mod"


def rel_out(mod):
    return "design/concepts/%s/cleanse/" % mod


def status_dir():
    """The fleet's status, logs and ALL_BIOMES.md: RM_CLEANSE_STATUS_DIR, else the agent-storage helper's folder."""
    if os.environ.get("RM_CLEANSE_STATUS_DIR"):
        return os.environ["RM_CLEANSE_STATUS_DIR"]
    import rmpaths
    return str(rmpaths.rm_path("designer_cleanse"))


def _read(path, default=None):
    """-> the file's text, or `default` when it cannot be opened. Bytes that are not UTF-8 read as U+FFFD (check_dir
    refuses such a file by name; nothing else crashes on it)."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return default


def _not_utf8(path):
    try:
        with open(path, encoding="utf-8") as f:
            f.read()
        return False
    except UnicodeDecodeError:
        return True
    except OSError:
        return False


def _json_text(text):
    """-> the parsed value, or _ABSENT when `text` is None or is not JSON (a nesting too deep to parse included)."""
    if text is None:
        return _ABSENT
    try:
        return json.loads(text)
    except (ValueError, RecursionError):
        return _ABSENT


def _json_file(path):
    return _json_text(_read(path))


def _blank(v):
    return not (isinstance(v, str) and v.strip())


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def _headings(text):
    return [h.strip() for h in re.findall(r"^##\s+(.+?)\s*$", text or "", re.M)]


def page_words(text):
    return len(re.findall(r"\S+", text or ""))


def open_records(out):
    """-> the reviewer's records still open on this proposal: the latest verdict's (converge.json's open, else
    review.json's remaining), or None when neither file holds a list of records."""
    cv = _json_file(os.path.join(out, "converge.json"))
    if isinstance(cv, dict) and isinstance(cv.get("open"), list):
        rem = cv["open"]
    else:
        rv = _json_file(os.path.join(out, "review.json"))
        rem = rv.get("remaining") if isinstance(rv, dict) else None
    return rem if isinstance(rem, list) and all(isinstance(r, dict) for r in rem) else None


def page_body(out, pages):
    """-> (the run's own part of his pages, defect or None). The reviewer's still-refused block is cut off only when it is
    exactly what the latest verdict's open records write (converge.json's open, else review.json's remaining: it is the
    reviewer's, not the run's); any other text under that heading is the run's and counts, and the heading itself is then
    a defect (an author cannot hide words under it)."""
    i = (pages or "").find(STILL_REFUSED_HEAD)
    if i < 0:
        return pages or "", None
    rem = open_records(out)
    if rem and pages[i:].strip() == _still_refused_block(rem).strip():
        return pages[:i], None
    return pages, ("his pages hold the heading %r but what follows it is not the latest verdict's open records word for "
                   "word" % STILL_REFUSED_HEAD)


# ------------------------------------------------------------------------------------------------ check


def bar_number(text):
    """-> the matched words when `text` pins a number, a count of variants or every field; None otherwise. bar_rule's
    detector patterns (shared with the coverage judge) plus a bare numeral or a percentage, which bar_rule does not
    catch ("30%": spec §5.3)."""
    for _kind, pats in bar_rule.DETECT:
        for p in pats:
            m = p.search(text or "")
            if m:
                return m.group(0)
    m = NUMERAL.search(text or "")
    return m.group(0) if m else None


def check_dir(out):
    """-> (refusals, stats). A refusal is {rule, where, what, would_pass}; stats are what was read and the worst value
    beside its limit. Mechanical shape only: whether the bars are good is the reviewer's."""
    refs, stats = [], {}

    def refuse(rule, where, what, would_pass):
        refs.append({"rule": rule, "where": where, "what": what, "would_pass": would_pass})

    def load_json(name):
        """-> the parsed value, or _ABSENT when the file is missing or does not parse (JSON null is a value)."""
        text = _read(os.path.join(out, name))
        if text is None:
            return _ABSENT
        try:
            return json.loads(text)
        except (ValueError, RecursionError) as e:
            refuse("files", name, "%s does not parse: %s" % (name, str(e)), "%s is valid JSON" % name)
            return _ABSENT

    result = load_json("result.json")
    blocked = isinstance(result, dict) and result.get("outcome") == "blocked"
    want = BLOCKED_FILES if blocked else FILES
    for name in FILES:
        if _not_utf8(os.path.join(out, name)):
            refuse("files", name, "%s is not UTF-8 text" % name, "%s written as UTF-8" % name)
    for name in want:
        t = _read(os.path.join(out, name))
        if t is None or not t.strip():
            refuse("files", name, "%s is %s" % (name, "missing" if t is None else "empty"),
                   "%s present in %s with its contents (the brief's file table)" % (name, out))
    stats["files"] = "%d of %d present" % (sum(1 for n in want if (_read(os.path.join(out, n)) or "").strip()), len(want))
    pages, block_bad = page_body(out, _read(os.path.join(out, "owner_pages.md")) or "")
    if block_bad:
        refuse("reviewer_block", "owner_pages.md", block_bad, "no such heading on his pages (only the review writes it, "
               "from review.json)")
    words = page_words(pages)
    stats["page_words"], stats["page_limit"] = words, PAGE_WORDS
    if words > PAGE_WORDS:
        refuse("owner_pages_length", "owner_pages.md", "his pages run %d words; the limit is %d (two pages)"
               % (words, PAGE_WORDS), "owner_pages.md at most %d words; detail moves to the other files" % PAGE_WORDS)
    if not isinstance(result, dict):
        if result is not _ABSENT:
            refuse("counts", "result.json", "result.json is %s, not an object" % type(result).__name__,
                   "result.json as the brief's table shapes it")
        return refs, stats
    if result.get("outcome") not in ("proposed", "blocked"):
        refuse("counts", "result.json outcome", "outcome %r is not proposed or blocked" % result.get("outcome"),
               "outcome \"proposed\" or \"blocked\"")
    if blocked:
        if _blank(result.get("blocked_on")):
            refuse("counts", "result.json blocked_on", "a blocked run does not say what blocked it",
                   "blocked_on names what stopped the run and what would unblock it")
        stats["outcome"] = "blocked"
        return refs, stats
    census = load_json("census.json")
    bars_doc = load_json("bars.json")
    models_md = _read(os.path.join(out, "models.md")) or ""
    tickets_md = _read(os.path.join(out, "tickets.md")) or ""
    models = _headings(models_md)
    tickets = _headings(tickets_md)

    rows = census.get("rows") if isinstance(census, dict) else census
    rows = rows if isinstance(rows, list) else []
    if census is not _ABSENT and not rows:
        refuse("census_fate", "census.json", "the census holds no rows", "census.json {\"rows\": [...]}, one per capability")
    stats["census_rows"] = len(rows)
    ticket_sections = dict(_sections(tickets_md))
    for i, r in enumerate(rows):
        r = r if isinstance(r, dict) else {}
        where = "census.json row %d (%s)" % (i + 1, r.get("id") or "no id")
        if r.get("fate") not in FATES:
            refuse("census_fate", where, "fate %r is not one of %s" % (r.get("fate"), ", ".join(FATES)),
                   "fate one of %s" % ", ".join(FATES))
        for k in ("id", "what", "why", "evidence", "called_by", "serves"):
            if _blank(r.get(k)) and (k in ("id", "fate") or not _text_list(r.get(k))):    # a list of paths is filled
                refuse("census_row", where, "%s is blank" % k, "%s filled (the brief's census columns; `none` and why, "
                       "when there is none)" % k)
        if r.get("built") not in BUILT:
            refuse("census_row", where, "built %r is not one of %s" % (r.get("built"), ", ".join(BUILT)),
                   "built one of %s, with the file that shows it in evidence" % ", ".join(BUILT))
        if r.get("proven") not in PROVEN:
            refuse("census_row", where, "proven %r is not one of %s" % (r.get("proven"), ", ".join(PROVEN)),
                   "proven one of %s" % ", ".join(PROVEN))
        if r.get("fate") == "needed_by" and (_blank(r.get("needed_by")) or _blank(r.get("why"))):
            refuse("needed_by_argument", where, "a needed_by row with no %s" % (
                "needed_by (which of land, life or the signature)" if _blank(r.get("needed_by")) else "deletion argument in why"),
                "needed_by names what needs it and why says what deleting its player-facing behaviour would defeat")
        if r.get("fate") == "next_version" and r.get("built") == "present":
            t = str(r.get("ticket") or "").strip()
            sec = _ticket_section(ticket_sections, t) if t else None
            if not t or sec is None:
                refuse("ticket", where, "a built extra moved to the next version %s" % (
                    "with no ticket" if not t else "names ticket %r, which tickets.md has no ## heading for" % t),
                    "ticket names a `## %s...` section of tickets.md, its switch-off ticket" % (t or "<ID>"))
    for h, body in ticket_sections.items():
        bad = _acceptance_defect(body)
        if bad:
            refuse("ticket", "tickets.md %s" % h[:80], "the ticket %s" % bad,
                   "the ticket says `Acceptance test: <the test>` (or `Acceptance test: none, <the reason>`)")

    _bars_shape(bars_doc, refuse)
    doc = bars_doc if isinstance(bars_doc, dict) else {}
    bars = _dicts(doc.get("bars"))
    stats["bars"] = len(bars)
    if bars_doc is not _ABSENT and not bars:
        refuse("bar_part", "bars.json", "bars.json holds no bars", "bars.json {\"bars\": [...]} with the whole bar")
    worst_num = None
    for b in bars:
        where = "bar %s" % (b.get("id") or "no id")
        _bar_parts(b, where, refuse)
        texts = [("says", b.get("says"))] + [("accept", x) for x in _strs(b.get("accept"))] + \
                [("reject", x) for x in _strs(b.get("reject"))] + \
                [("figurative accept", f.get("accept")) for f in _dicts(_dict(b.get("meant")).get("figurative"))]
        for part, text in texts:
            hit = bar_number(text if isinstance(text, str) else "")
            if hit:
                worst_num = worst_num or "%s %s: %r" % (where, part, hit)
                refuse("bar_number", "%s %s" % (where, part), "%r pins a number, a count or every field (%r)"
                       % (text, hit), "the comparison a player sees instead; numbers go in range or sees, or a check")
    stats["bar_numbers"] = worst_num or "none"
    ids = [b.get("id") if isinstance(b.get("id"), str) else "" for b in bars]
    if len(set(ids)) != len(ids) or any(_blank(i) for i in ids):
        refuse("bar_part", "bars.json", "bar ids are blank or repeated: %s" % ids, "every bar a unique id")
    wholes = set(x for x in [doc.get("whole")] if not _blank(x)) | {i for i, b in zip(ids, bars) if b.get("whole") is True}
    if len(wholes) != 1 or not wholes <= set(ids):
        refuse("whole", "bars.json whole", "%s whole bars (%s)%s" % (len(wholes), sorted(wholes),
               "" if wholes <= set(ids) else ", not all of them bars"),
               "exactly one whole bar: bars.json `whole` names one bar id, and no other bar says whole")
    _meetings(doc, bars, models, refuse, stats)
    old = _old_bars(out)
    mapped = doc.get("old_bars") if isinstance(doc.get("old_bars"), dict) else {}
    idset = lambda xs: {x["id"].strip() for x in xs if isinstance(x.get("id"), str)}    # noqa: E731
    became = {"kept": ("bar", idset(bars)), "merged": ("bar", idset(bars)),
              "check": ("check", idset(_dicts(doc.get("checks")))), "rule": ("rule", idset(_dicts(doc.get("rules"))))}
    stats["old_bars"] = "%d mapped of %d in tree.json" % (len([o for o in old if o in mapped]), len(old))
    for o in old:
        m = mapped.get(o)
        if not isinstance(m, dict) or m.get("to") not in OLD_TO or _blank(m.get("why")):
            refuse("old_bar", "old_bars %s" % o, "old bar %s is %s" % (o, "unmapped" if m is None else
                   "mapped without a `to` from %s or a why" % ", ".join(OLD_TO)),
                   "old_bars[%r] = {\"to\": one of %s, \"as\": the new id, \"why\": ...}" % (o, ", ".join(OLD_TO)))
        elif m.get("to") in became and _blank(m.get("as")):
            refuse("old_bar", "old_bars %s" % o, "old bar %s went to %s without naming as what" % (o, m.get("to")),
                   "`as` names the bar, check or rule it became")
        elif m.get("to") in became and m.get("as").strip() not in became[m.get("to")][1]:
            refuse("old_bar", "old_bars %s" % o, "old bar %s went to %s as %r, which is no %s id of bars.json"
                   % (o, m.get("to"), m.get("as"), became[m.get("to")][0]),
                   "`as` is one id of bars.json %ss: %s" % (became[m.get("to")][0], sorted(became[m.get("to")][1])[:12]))
    extra = sorted(set(mapped) - set(old))
    if extra:
        refuse("old_bar", "old_bars", "old_bars maps ids the concept's tree.json does not hold: %s" % extra,
               "old_bars maps exactly the ids of tree.json's leaves (empty when there is no tree)")
    _counts(result, rows, bars, doc, models, tickets, pages, mapped, refuse, stats)
    return refs, stats


def _strs(v):
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


def _dicts(v):
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _dict(v):
    return v if isinstance(v, dict) else {}


_ABSENT = object()      # load_json: the file is missing or does not parse (JSON null is a value, refused as such)
_PAGE_LABELS = {"capabilities": r"\bcapabilit(?:y|ies)\b",
                "live_only_bars": r"\blive[- ]only bars?\b|\bbars only the live game can decide\b",
                "bars": r"(?<!live-only )(?<!live only )(?<!old )\bbars?\b(?! only the live)"}
_CLAUSE_END = r";|\n|\.(?:\s|$)"


def page_states(page, key, n):
    """Whether `page` states count `n` beside its name `key`: the digits after the name in the same clause (up to `;`,
    a line end, a sentence end or the next counted name), or just before it ("3 capabilities"). A bare digit elsewhere
    on the page is not a statement of the count (two counts swapped would pass a page-wide search)."""
    num = r"(?<![\w.])%d(?!\w|[.,]\d)" % n
    other = re.compile("|".join("(?:%s)" % v for v in _PAGE_LABELS.values()), re.I)
    for m in re.finditer(_PAGE_LABELS[key], page or "", re.I):
        seg = re.split(_CLAUSE_END, page[m.end():], maxsplit=1)[0]
        nxt = other.search(seg)
        if re.search(num, seg[:nxt.start()] if nxt else seg):
            return True
        if re.search(num + r"[^\d;\n]{0,3}$", re.split(_CLAUSE_END, page[max(0, m.start() - 12):m.start()])[-1]):
            return True
    return False


def _sections(md):
    """-> [(heading, text under it)] for every `## ` heading."""
    parts = re.split(r"^##\s+(.+?)\s*$", md or "", flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def _ticket_section(sections, tid):
    for h, body in sections.items():
        if re.match(r"%s(?![\w-])" % re.escape(tid), h):
            return body
    return None


_ACCEPTANCE = re.compile(r"^[ \t>*_-]*acceptance test[*_]*[ \t]*:[*_]*\s*(\S[^\n]*)?", re.I | re.M)


def _acceptance_defect(body):
    """-> why a ticket's section fails the brief's "Acceptance test: ..." line, or None."""
    m = _ACCEPTANCE.search(body or "")
    if not m or not (m.group(1) or "").strip():
        return "has no acceptance test (a line `Acceptance test: ...` with the test after it)"
    v = m.group(1).strip().strip("*_ ")
    if re.match(r"none\b", v, re.I) and not re.match(r"none\b[\W_]*\w", v, re.I):
        return "says its acceptance test is none without the reason"
    return None


_SHAPE_LISTS = (("bars", ()), ("checks", ("id", "what")), ("rules", ("id", "rule")),
                ("meetings", ("thing", "holds_together")))


def _bars_shape(bdoc, refuse):
    """bars.json's containers as SHAPE fixes them: an object; bars, checks, rules and meetings lists of objects ([] when
    there are none), each with its named text fields; a rule's touches and a meeting's members lists of text; old_bars an
    object ({} when there is no tree)."""
    if bdoc is _ABSENT:
        return
    if not isinstance(bdoc, dict):
        refuse("shape", "bars.json", "bars.json is %s, not an object" % type(bdoc).__name__, "bars.json as SHAPE says")
        return
    for key, need in _SHAPE_LISTS:
        v = bdoc.get(key)
        if not isinstance(v, list) or any(not isinstance(x, dict) for x in v):
            refuse("shape", "bars.json %s" % key, "%s is %s" % (key, "missing" if v is None else
                   "not a list of objects (%s)" % type(v).__name__ if not isinstance(v, list) else "a list holding a non-object"),
                   "%s a list of objects ([] when there are none)" % key)
            continue
        for i, x in enumerate(v):
            where = "bars.json %s %d (%s)" % (key, i + 1, str(x.get("id") or x.get("thing") or "no id")[:60])
            for f in need:
                if _blank(x.get(f)):
                    refuse("shape", where, "%s is blank or not text" % f, "%s filled with text" % f)
            for f in {"rules": ("touches",), "meetings": ("members",)}.get(key, ()):
                if not _text_list(x.get(f)):
                    refuse("shape", where, "%s is not a non-empty list of text" % f, "%s a list of ids or things" % f)
    if not isinstance(bdoc.get("old_bars"), dict):
        refuse("shape", "bars.json old_bars", "old_bars is %s, not an object" % type(bdoc.get("old_bars")).__name__,
               "old_bars an object ({} when the concept has no tree.json)")


def _text_list(v):
    """True when `v` is a non-empty list of non-blank strings and nothing else."""
    return isinstance(v, list) and bool(v) and all(isinstance(x, str) and x.strip() for x in v)


def _bar_parts(b, where, refuse):
    miss = []
    meant = b.get("meant") if isinstance(b.get("meant"), dict) else None
    rng = b.get("range") if isinstance(b.get("range"), dict) else None
    sees = b.get("sees") if isinstance(b.get("sees"), dict) else None
    if _blank(b.get("says")):
        miss.append("says")
    if meant is None or _blank(meant.get("intent")):
        miss.append("meant.intent (the intent behind the bar)")
    if meant is None or _blank(meant.get("source")):
        miss.append("meant.source (his words by event, a standing ruling, or `delegated: from what`)")
    fig = (meant or {}).get("figurative")
    if not isinstance(fig, list) or any(not isinstance(f, dict) or any(_blank(f.get(k)) for k in
                                         ("word", "stands_for", "accept")) for f in fig):
        miss.append("meant.figurative (a list; each {word, stands_for, accept}; [] when no word is figurative)")
    acc, rej = _strs(b.get("accept")), _strs(b.get("reject"))
    for k in ("accept", "reject", "touches"):
        if not _text_list(b.get(k)):
            miss.append("%s (a non-empty list of pictures or things, each text)" % k)
    lazy = b.get("lazy")
    if _blank(lazy):
        miss.append("lazy")
    elif not re.match(r"none\s*:\s*\S", lazy.strip(), re.I) and _norm(lazy) not in {_norm(x) for x in rej}:
        miss.append("lazy (the laziest build, word for word one of the reject pictures; or `none: <why the words are "
                    "tight>`)")
    if rng is None or _blank(rng.get("varies")) or _blank(rng.get("left_out")):
        miss.append("range {varies, left_out}")
    for k in ("instrument", "start", "on", "control", "reset"):
        if sees is None or _blank(sees.get(k)):
            miss.append("sees.%s" % k)
    if b.get("live_only") is True and _blank((sees or {}).get("live_only_why")) and _blank(b.get("live_only_why")):
        miss.append("sees.live_only_why (a live-only bar says why nothing cheaper can see it)")
    if not isinstance(b.get("live_only"), bool):
        miss.append("live_only (true or false)")
    for m in miss:
        refuse("bar_part", where, "%s is missing or blank" % m, "%s filled as the brief's bar parts say" % m.split(" (")[0])


def _meetings(doc, bars, models, refuse, stats):
    touchers = {}
    for b in bars:
        for t in _strs(b.get("touches")):
            touchers.setdefault(_norm(t), set()).add(str(b.get("id")))
    for r in _dicts(doc.get("rules")):
        for t in _strs(r.get("touches")):
            touchers.setdefault(_norm(t), set()).add(str(r.get("id")))
    meets = _dicts(doc.get("meetings"))
    by_thing = {}
    for m in meets:
        by_thing.setdefault(_norm(m.get("thing")), []).append(m)
    shared = {t: s for t, s in touchers.items() if t and len(s) >= 2}
    stats["shared_things"], stats["meetings"] = len(shared), len(meets)
    for t, who in sorted(shared.items()):
        ms = by_thing.get(t) or []
        members = set()
        for m in ms:
            members |= set(_strs(m.get("members")))
        if not ms:
            refuse("meeting", "touches %r" % t, "%s touch %r and no meeting names it" % (sorted(who), t),
                   "one meeting {thing: %r (spelled as in touches), members: %s, holds_together, why}" % (t, sorted(who)))
        elif not who <= members:
            refuse("meeting", "meeting %r" % t, "its members leave out %s, which touch it" % sorted(who - members),
                   "members list every bar and rule that touches %r" % t)
    models_n = {_norm(h) for h in models}
    for m in meets:
        where = "meeting %r" % m.get("thing")
        h = m.get("holds_together")
        if h not in HOLDS:
            refuse("meeting", where, "holds_together %r is not one of %s" % (h, ", ".join(HOLDS)),
                   "holds_together argued (say it), measured (cite it) or unknown (name the model)")
        elif _blank(m.get("why")):
            refuse("meeting", where, "an %s meeting with no %s in why" % (h, {"argued": "argument", "measured": "citation",
                   "unknown": "reason it is not known"}[h]),
                   "why holds the argument (argued), the reading it cites (measured) or what is not known (unknown)")
        if h == "unknown":
            mod = _norm(m.get("model"))
            # the heading itself, or its id: "M1" names "## M1: gas spread"; "gas" names no heading it is only inside
            if not mod or not any(mod == x or re.match(re.escape(mod) + r"(?![\w-])", x) for x in models_n):
                refuse("unknown_model", where, "an unknown meeting names model %r, which models.md has no ## heading for"
                       % m.get("model"), "model names a `## ` heading of models.md that would settle it")


def _old_bars(out):
    """The old tree's leaf ids the proposal maps: tree.json's leaves, or, once an apply has replaced that tree, the
    record it kept of them (tree.json cleanse.old_leaf_ids) while the proposal is the one applied (cleanse.digest), so a
    retry still checks the original mapping and a later proposal maps the tree as it now stands."""
    tree = os.path.join(os.path.dirname(os.path.normpath(out)), "tree.json")
    try:
        with open(tree, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return []
    rec = doc.get("cleanse") if isinstance(doc, dict) else None
    if (isinstance(rec, dict) and isinstance(rec.get("old_leaf_ids"), list)
            and rec.get("digest") == proposal_digest(out)):     # a retry of the very proposal applied, never a new one
        return [x for x in rec["old_leaf_ids"] if isinstance(x, str)]
    leaves = doc.get("leaves") if isinstance(doc, dict) else None
    return [x["id"] for x in leaves if isinstance(x, dict) and isinstance(x.get("id"), str)] if isinstance(leaves, list) else []


def _counts(result, rows, bars, doc, models, tickets, pages, mapped, refuse, stats):
    fates = [r.get("fate") for r in rows if isinstance(r, dict)]
    questions = re.findall(r"^\s*(?:[-*]\s*)?\**Q\d+\.", pages, re.M)
    have = {"capabilities": len(rows), "kept": sum(1 for f in fates if f in KEPT),
            "next_version": fates.count("next_version"), "recommend_retire": fates.count("recommend_retire"),
            "old_bars": len(mapped), "bars": len(bars), "live_only_bars": sum(1 for b in bars if b.get("live_only") is True),
            "checks": len(_dicts(doc.get("checks"))), "rules": len(_dicts(doc.get("rules"))),
            "unknown_pairs": sum(1 for m in _dicts(doc.get("meetings")) if m.get("holds_together") == "unknown"),
            "models": len(models), "tickets": len(tickets), "questions": len(questions)}
    stats["questions"], stats["question_limit"] = len(questions), QUESTIONS
    counts = result.get("counts") if isinstance(result.get("counts"), dict) else {}
    for k in COUNT_KEYS:
        if type(counts.get(k)) is not int or counts.get(k) != have[k]:     # True and 1.0 are not the count 1
            refuse("counts", "result.json counts.%s" % k, "counts.%s reads %r; the files hold %d" % (k, counts.get(k), have[k]),
                   "counts.%s = %d (%s)" % (k, have[k], _COUNT_HOW[k]))
    if len(questions) > QUESTIONS:
        refuse("counts", "owner_pages.md", "%d questions; at most %d" % (len(questions), QUESTIONS),
               "at most %d questions, each a line starting Q<n>." % QUESTIONS)
    for k in ("capabilities", "bars", "live_only_bars"):
        if not page_states(pages, k, have[k]):
            refuse("counts", "owner_pages.md", "his pages do not state the %s count %d beside its name"
                   % (k.replace("_", "-"), have[k]), "page one says `%s %d` (the name, then the digits, in one clause; "
                   "a before-and-after pair may sit in it), the number in result.json" % (k.replace("_", "-"), have[k]))
    for k in ("mod", "run", "signature"):
        if _blank(result.get(k)):
            refuse("counts", "result.json %s" % k, "%s is blank" % k, "%s filled (the brief's result.json)" % k)


_COUNT_HOW = {"capabilities": "census rows", "kept": "census rows whose fate is land, life, signature, needed_by or "
              "dependency", "next_version": "rows with fate next_version", "recommend_retire": "rows with fate "
              "recommend_retire", "old_bars": "entries in bars.json old_bars", "bars": "entries in bars.json bars",
              "live_only_bars": "bars with live_only true", "checks": "entries in bars.json checks", "rules": "entries in "
              "bars.json rules", "unknown_pairs": "meetings whose holds_together is unknown", "models": "## headings in "
              "models.md", "tickets": "## headings in tickets.md", "questions": "lines of owner_pages.md starting Q<n>."}


def check_report(out):
    refs, stats = check_dir(out)
    lines = ["check %s: read %s" % (out, ", ".join("%s %s" % (k, v) for k, v in stats.items()))]
    lines.append("worst: owner_pages %s words of limit %d; questions %s of limit %d; first number in a bar: %s" % (
        stats.get("page_words"), PAGE_WORDS, stats.get("questions", "-"), QUESTIONS, stats.get("bar_numbers", "-")))
    for r in refs:
        lines.append("REFUSED [%s] %s: %s. Would pass: %s" % (r["rule"], r["where"], r["what"], r["would_pass"]))
    lines.append("PASS: the proposal's shape holds" if not refs else "REFUSED: %d refusal(s)" % len(refs))
    return refs, "\n".join(lines)


# ------------------------------------------------------------------------------------------------ the CASE


def compose(repo):
    with open(os.path.join(repo, COMPOSE), encoding="utf-8") as f:
        return json.load(f)["entries"]


def entry(repo, mod):
    for e in compose(repo):
        if e.get("key") == mod:
            return e
    raise KeyError("%s is not an entry of %s" % (mod, COMPOSE))


# his card answers of 2026-11-10, one ANSWERS_OWNER.md per rehearsal folder; a folder is a mod's when it bears the mod's
# key or source folder name, or is named here (each mapping read from the folder's own notes, which name the source:
# NightsideIce -> src/RimMandrake/SleepingIce, Wasteland -> src/RimMandrake/Wastes; the three sea-floor folders are
# TerminalBiomes' seas). A folder no mod claims is reported by name, never dropped
# (RIMMANDRAKE_FEED_CLEANSE_OWNER_ANSWERS_SCALD_CARD_SAT_UNREAD: the Scald's three answers never reached its cleanse).
ANSWERS_DIR = "design/RimMandrake/designer_codex_2026-11-09"
ANSWERS_FILE = "ANSWERS_OWNER.md"
ANSWERS_OF = {"NightsideIce": "SleepingIce", "Wasteland": "Wastes", "TheScaldFloor": "TerminalBiomes",
              "TheChillFloor": "TerminalBiomes", "PropaneLakesShore": "TerminalBiomes"}


def owner_answers(repo):
    """-> ({mod key: [repo-relative ANSWERS_OWNER.md, ...]}, [folders no compose entry claims]), or None when the
    answers folder cannot be listed (could not look is not "none")."""
    try:
        folders = sorted(n for n in os.listdir(os.path.join(repo, ANSWERS_DIR))
                         if os.path.isfile(os.path.join(repo, ANSWERS_DIR, n, ANSWERS_FILE)))
    except OSError:
        return None
    owner = {}
    for e in compose(repo):
        for n in {e["key"], e.get("source") or e["key"]}:
            owner.setdefault(n, e["key"])
    got, unclaimed = {}, []
    for f in folders:
        mod = ANSWERS_OF.get(f) or owner.get(f)
        if mod is None or ANSWERS_OF.get(f) and ANSWERS_OF[f] not in owner.values():
            unclaimed.append(f)
            continue
        got.setdefault(mod, []).append("%s/%s/%s" % (ANSWERS_DIR, f, ANSWERS_FILE))
    return got, unclaimed


def _caps(name):
    return {name.upper(), re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).upper()}


def items_of(repo, mod, source):
    prefixes = tuple(p + "_" for p in _caps(mod) | _caps(source))
    out = {"open": [], "closed": []}
    for state, d in (("open", "infrastructure/state/items"), ("closed", "infrastructure/state/items/closed")):
        try:
            names = sorted(os.listdir(os.path.join(repo, d)))
        except OSError:
            continue
        out[state] = ["%s/%s" % (d, n) for n in names if n.endswith(".md") and n.startswith(prefixes)]
    return out


def docs_naming(repo, mod, source, skip):
    """design/ files that name the mod (word match), most mentions first."""
    pat = re.compile(r"\b(%s)\b" % "|".join(re.escape(x) for x in sorted({mod, source})))
    hits = []
    base = os.path.join(repo, "design")
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in files:
            if not f.endswith((".md", ".json", ".txt")):
                continue
            p = os.path.join(d, f)
            r = os.path.relpath(p, repo)
            if r.startswith(skip):
                continue
            try:
                if os.path.getsize(p) > 2_000_000:
                    continue
                with open(p, encoding="utf-8", errors="replace") as fh:     # a few design files are not UTF-8
                    n = len(pat.findall(fh.read()))
            except OSError:
                continue
            if n:
                hits.append((n, r))
    hits.sort(key=lambda x: (-x[0], x[1]))
    return hits


SHAPE = """The shape the self-check reads (the brief's table, with the field names fixed):
- census.json: {"rows": [{"id", "what", "built": present|absent|unknown, "evidence", "proven": current|stale|missing|unknown,
  "called_by", "serves", "fate": land|life|signature|needed_by|dependency|next_version|recommend_retire, "why",
  "needed_by", "ticket"}]}; id, what, evidence, called_by, serves and why are never blank (write "none" and why when
  there is none). A needed_by row names what needs it in "needed_by" and gives the deletion argument in "why".
  A built (present) row moved to next_version names its switch-off ticket in "ticket".
- bars.json: {"bars": [{"id", "says", "meant": {"intent", "source", "figurative": [{"word", "stands_for", "accept"}]},
  "accept": [...], "reject": [...], "lazy": one of the reject pictures word for word, or "none: <why the words are tight>",
  "range": {"varies", "left_out"}, "sees": {"instrument", "start", "on", "control", "reset", "live_only_why"},
  "live_only": true|false, "touches": [...]}], "whole": "<the whole bar's id>", "checks": [{"id", "what"}],
  "rules": [{"id", "rule", "touches": [...]}], "meetings": [{"thing", "members": [bar and rule ids], "holds_together":
  argued|measured|unknown, "why", "model"}], "old_bars": {"<old id>": {"to": kept|merged|check|rule|moved|dropped,
  "as": "<new id>", "why"}}}. A meeting's "thing" is spelled exactly as in "touches"; one meeting per thing touched by
  two or more bars and rules, its members all of them. An unknown meeting's "model" is a "## " heading of models.md.
  No digit, percentage, count of variants or "every field" in says, accept or reject: those belong in range, sees or a
  check.
- models.md and tickets.md: one "## " heading per model or ticket (a ticket heading starts with its id, e.g.
  "## T1: ..."), each ticket with a line "Acceptance test: ..." (or "Acceptance test: none, <reason>").
- owner_pages.md: at most %d words; questions are lines starting "Q1.", "Q2." (at most %d); page one states each of
  the capabilities, bars and live-only bars counts as digits beside its name in one clause, the same numbers as
  result.json, e.g. "Capabilities 14 before, 9 after; bars 18 before, 7 after; live-only bars 2."
- result.json: {"mod", "run", "outcome": "proposed"|"blocked", "signature", "counts": {%s}, "blocked_on"}, each count
  equal to the files (kept = rows whose fate is land, life, signature, needed_by or dependency; unknown_pairs = unknown
  meetings; models and tickets = their "## " headings; old_bars = entries of old_bars). A blocked run writes at least
  owner_pages.md and result.json, with blocked_on saying what stopped it.""" % (PAGE_WORDS, QUESTIONS, ", ".join(COUNT_KEYS))


def case_text(repo, mod):
    e = entry(repo, mod)
    source = e.get("source") or mod
    concept = "design/concepts/%s/" % mod
    out = rel_out(mod)
    L = ["## CASE", "", "Mod: %s (%s). Source folder: src/RimMandrake/%s/." % (mod, e.get("label") or mod, source)]
    if e.get("blurb"):
        L.append("Its line in Biomes.compose.json: %s" % e["blurb"])
    L.append("")
    if os.path.isdir(os.path.join(repo, concept)):
        names = sorted(n for n in os.listdir(os.path.join(repo, concept)) if not n.startswith("."))
        old = _old_bars(os.path.join(repo, out))
        L.append("Concept folder: %s (%s)." % (concept, ", ".join(names)))
        L.append("Its tree.json holds %d old bars; map every one of them in bars.json old_bars: %s."
                 % (len(old), ", ".join(old)) if old else "It holds no tree.json leaves: old_bars is empty ({}).")
    else:
        L.append("This mod has no concept folder (%s does not exist). Make the census from the source alone; there "
                 "are no old bars, so old_bars is empty ({}). Your output folder below is still where you write." % concept)
    its = items_of(repo, mod, source)
    L += ["", "Ledger items of the mod (open: %d, closed: %d):" % (len(its["open"]), len(its["closed"]))]
    L += ["- open: %s" % p for p in its["open"]] + ["- closed: %s" % p for p in its["closed"]]
    if not its["open"] and not its["closed"]:
        L.append("- none found under its name")
    hits = docs_naming(repo, mod, source, skip=concept)
    L += ["", "Design documents that name it (mentions, most first):"]
    L += ["- %s (%d)" % (r, n) for n, r in hits[:60]] or ["- none"]
    if len(hits) > 60:
        L.append("- and %d more: grep -rlw %s design/" % (len(hits) - 60, mod))
    ans = owner_answers(repo)
    L += ["", "His card answers on this mod (2026-11-10; his words: where they differ from the brief's defaults, they "
              "win, and the read basis cites each file):"]
    L += (["- could not look: %s cannot be listed" % ANSWERS_DIR] if ans is None else
          ["- %s" % p for p in ans[0].get(mod, [])] or ["- none found under %s" % ANSWERS_DIR])
    L += ["", "Lore and rulings to read before you define anything:"]
    L += ["- %s" % p for p in LORE if os.path.exists(os.path.join(repo, p))]
    L += ["", "Shared engines (dependencies: name what the mod needs from each; do not redesign them):"]
    L += ["- %s: src/RimMandrake/%s/" % (x["key"], x.get("source") or x["key"]) for x in compose(repo)
          if x.get("group") == "engine"]
    L += ["", "Output folder: %s (create it). Every file of the brief's table goes there." % out,
          "Self-check, run it last and fix what it refuses: python3 %s check %s" % (ME, out.rstrip("/")), "",
          SHAPE, "",
          "Working rules (no hooks guard you here):",
          "- Write ONLY inside %s. Nothing else in the tree is yours to change." % out,
          "- Run no git command that writes (no add, commit, push, checkout, reset, stash); the launcher commits your "
          "folder after you finish.",
          "- Start no game, use no bridge, deploy nothing.",
          "- Ask nothing and wait for nothing: where his words do not settle it, take your stated default and go on."]
    return "\n".join(L) + "\n"


def brief_body(repo):
    text = _read(os.path.join(repo, BRIEF)) or ""
    m = re.search(r"^---\s*$", text, re.M)
    return (text[m.end():] if m else text).strip()


def prompt_for(repo, mod):
    return brief_body(repo) + "\n\n" + case_text(repo, mod)


# ------------------------------------------------------------------------------------------------ effects


def _git(c, *a, timeout=300):
    r = subprocess.run(["git", "-C", c] + list(a), capture_output=True, text=True, timeout=timeout,
                       stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), (r.stderr or r.stdout).strip()))
    return r.stdout


def pool_root():
    return os.environ.get("RM_DETACHED_POOL") or os.path.expanduser("~/rm/relentless")


def claude_tool_args(tools):
    """tools=None: the writing author (no permission prompts); "": no tool at all; "Read,Grep,Glob": only those."""
    if tools is None:
        return ["--dangerously-skip-permissions"]
    if tools == "":
        return ["--tools", ""]
    return ["--tools", tools, "--allowedTools", tools]


class Busy(RuntimeError):
    pass


@contextlib.contextmanager
def mod_lock(mod):
    """One invocation per mod at a time (run, review and a fleet's mod share the clone cleanse-<Mod>): an exclusive,
    non-blocking flock on <pool>/clones/.cleanse-<Mod>.lock (ext4, beside the clone), released when the holder exits or
    dies. A second taker raises Busy instead of syncing, writing or publishing over the first."""
    d = os.path.join(pool_root(), "clones")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, ".cleanse-%s.lock" % mod), "a") as fh:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise Busy("another designer_cleanse invocation holds %s (its run, review or fleet is live)" % mod)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


class Effects:
    """The real world: pool clones, the quota gate, Codex and Claude, git and ./publish. The selftest swaps this."""

    def __init__(self, status=None):
        self.st = status or Status(status_dir())
        self._lock = threading.Lock()

    def log(self, mod, line):
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        d = os.path.join(self.st.dir, "logs")
        os.makedirs(d, exist_ok=True)
        with self._lock, open(os.path.join(d, mod + ".log"), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (stamp, line))
        print("%s %s: %s" % (stamp, mod, line), flush=True)

    def status(self, mod, state, why=""):
        self.st.set(mod, state, why)

    def clone(self, mod):
        """-> a pool clone <pool>/clones/cleanse-<Mod>: reused and synced, or made by scratch_clone.py (sparse: the
        default cone, design/, the mod's source and the engines' sources)."""
        dest = os.path.join(pool_root(), "clones", "cleanse-" + mod)
        try:
            e = entry(ROOT, mod)
            dirs = ["design", "src/RimMandrake/" + (e.get("source") or mod)] + [
                "src/RimMandrake/" + (x.get("source") or x["key"]) for x in compose(ROOT) if x.get("group") == "engine"]
        except (OSError, KeyError, ValueError):
            dirs = ["design", "src/RimMandrake/" + mod]
        if os.path.isdir(os.path.join(dest, ".git")):
            r = subprocess.run(["./sync"], cwd=dest, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
            if r.returncode:
                raise RuntimeError("reused %s but its ./sync failed (exit %d): %s" % (dest, r.returncode,
                                   ((r.stdout or "") + (r.stderr or "")).strip()))
            self.log(mod, "reused and synced %s" % dest)
        else:
            env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
            r = subprocess.run(["python3", os.path.join(UTILS, "scratch_clone.py"), "clone", "designer cleanse " + mod,
                                "--name", "cleanse-" + mod, "--fetch", "--sparse"] + dirs,
                               env=env, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
            if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
                raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode,
                                   ((r.stdout or "") + (r.stderr or "")).strip()))
            self.log(mod, "made %s" % dest)
        sparse = subprocess.run(["git", "-C", dest, "config", "--get", "core.sparseCheckout"], capture_output=True,
                                text=True, timeout=60, stdin=subprocess.DEVNULL)
        if sparse.returncode == 0 and sparse.stdout.strip() == "true":
            _git(dest, "sparse-checkout", "add", *dirs, timeout=540)    # a reused sparse clone may lack the mod's source
        return dest

    def gate(self):
        import agent_runner
        return agent_runner.quota_gate()

    def codex(self, cwd, prompt, base, model=None, effort=None, sandbox=None, **_):
        import agent_runner
        os.makedirs(os.path.dirname(base), exist_ok=True)
        return agent_runner.run(cwd, prompt, base + ".last.txt", base + ".events.jsonl", base + ".spend.json",
                                model=model, effort=effort, sandbox=sandbox, timeout=None)

    def claude(self, cwd, prompt, base, model="opus", tools=None, **_):
        """claude -p in claude_bounded.sh; tools=None is a writing author (no permission prompts), a tool list is a
        read-only reviewer, "" is no tool at all (the blind sort). No spend cap is passed and none is told: the run is
        never told its spend."""
        os.makedirs(os.path.dirname(base), exist_ok=True)
        bounded = os.path.join(cwd, "src", "RimMandrake", "Utils", "claude_bounded.sh")
        if not os.path.exists(bounded):
            bounded = os.path.join(UTILS, "claude_bounded.sh")
        cmd = [bounded, "-p", "--model", model or "opus", "--output-format", "json"] + EF.effort_args(model or "opus")
        cmd += claude_tool_args(tools)
        env = dict(os.environ)
        env.setdefault("AGENT_SEAT", "BENCH")
        env.setdefault("RIMFLOW_SEAT", env["AGENT_SEAT"])
        with open(base + ".json", "w", encoding="utf-8") as out, open(base + ".err", "w", encoding="utf-8") as err:
            # timeout=None on purpose: the Conductor's brief (owner authority) says no wall-clock limit on a run
            p = subprocess.run(cmd, input=prompt, cwd=cwd, stdout=out, stderr=err, text=True, env=env, timeout=None)
        raw = _read(base + ".json") or ""
        try:
            res = json.loads(raw)
        except ValueError:
            output = raw + (_read(base + ".err") or "")
            return {"runner": "claude", "is_error": True, "result": output,
                    "read_result": output[-2000:],  # cut-ok: existing quota search and reviewer parsing window
                    "returncode": p.returncode}
        res = res if isinstance(res, dict) else {"result": str(res)}
        res.setdefault("runner", "claude")
        res["is_error"] = bool(res.get("is_error")) or p.returncode != 0
        return res

    def changed(self, cwd):
        out = []
        for line in _git(cwd, "status", "--porcelain", "--untracked-files=all", timeout=300).splitlines():
            p = line[3:]
            p = p.split(" -> ")[-1].strip().strip('"')
            out.append(p)
        return out

    def head_text(self, cwd, rel):
        """-> the file as the clone's HEAD holds it (the published proposal), or None when HEAD has no such file."""
        r = subprocess.run(["git", "-C", cwd, "show", "HEAD:" + rel], capture_output=True, timeout=120,
                           stdin=subprocess.DEVNULL)
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None

    def publish(self, cwd, paths, msg):
        _git(cwd, "add", "--", *paths, timeout=300)
        r = subprocess.run(["./publish", "-m", msg] + list(paths), cwd=cwd, capture_output=True, text=True,
                           timeout=540, stdin=subprocess.DEVNULL)
        said = (r.stdout or "") + (r.stderr or "")
        m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", said)
        if r.returncode or not m:
            raise RuntimeError("./publish exit %d: %s" % (r.returncode, said.strip()))
        return m.group(1)

    def sleep(self, s):
        time.sleep(s)

    def release(self, clone):
        """Remove the finished mod's clone when nothing in it is unpushed, untracked or in use; otherwise keep it.
        Conversation records (conversations/*.md, which the conversation hook writes inside the clone) are carried out
        first by publishing them, when they are the clone's only dirt: kept clones of nothing but records filled the
        pool 16 of 16 and crashed the converge fleet, 2026-11-17 (RIMMANDRAKE_RELEASE_CLEANSE_CLONES_RECORDS_PIN_POOL_
        FULL). A failed carry keeps the clone and says why. Not relentless_disk.park: the Relentless warm shelf hands
        its clones to builders that need a full checkout, and this one is sparse (relentless.py removes a tracked-files-
        only tree rather than park it, for that reason)."""
        try:
            import shutil
            import scratch_clone as SC
            from pathlib import Path
            if SC.clone_unpushed(Path(clone), strict=True) or SC.clone_in_use(Path(clone)):
                return "kept at %s (unpushed, uncommitted or in use)" % clone
            dirt = self.changed(clone)
            records = [p for p in dirt if p.startswith("conversations/") and p.endswith(".md")
                       and os.path.isfile(os.path.join(clone, p))]        # a deleted record is other dirt: kept
            if dirt and len(records) == len(dirt):
                try:
                    sha = self.publish(clone, records, "conversations: %d record(s) carried out of cleanse clone %s"
                                       % (len(records), os.path.basename(clone)))
                except Exception as e:  # noqa: BLE001
                    return "kept at %s (carrying %d conversation record(s) out failed: %s)" % (clone, len(records), e)
                if SC.clone_unpushed(Path(clone), strict=True) or self.changed(clone):
                    return "kept at %s (records published %s, but the clone still reads unpushed or dirty)" % (clone, sha)
                shutil.rmtree(clone)
                return "removed %s (its %d conversation record(s) published %s)" % (clone, len(records), sha)
            if dirt:
                return "kept at %s (unpushed, uncommitted or in use)" % clone
            shutil.rmtree(clone)
            return "removed %s (everything in it is on origin/main)" % clone
        except Exception as e:     # noqa: BLE001  releasing is housekeeping: a failure keeps the clone, never loses it
            return "kept at %s (%s: %s)" % (clone, type(e).__name__, e)


# ------------------------------------------------------------------------------------------------ run


def _usage(res):
    if not isinstance(res, dict):
        return None
    if res.get("runner") == "codex" or "codex_usage" in res:
        return {"codex_tokens": res.get("codex_usage")}
    try:
        import role_launch
        return {"claude_weighted_tokens": role_launch.run_tokens(res)}
    except Exception:          # noqa: BLE001
        return {"claude_usage": res.get("usage")}


def _agent_answer(res):
    res = res or {}
    return res.get("read_result", res.get("result"))


def _agent(fx, mod, runner, cwd, prompt, base, **kw):
    """One agent run, waiting out the quota: a gate refusal or a quota error is a wait and a retry, never a failure and
    never a fall back to the other runner."""
    n = 0
    while True:
        if runner == "codex":
            try:
                fx.gate()
            except Refused as e:
                fx.log(mod, "quota gate refused (%s); waiting %d s and retrying" % (e, QUOTA_WAIT_S))
                fx.status(mod, "running", "waiting for the Codex weekly quota: %s" % e)
                fx.sleep(QUOTA_WAIT_S)
                continue
            n += 1
            fx.log(mod, "codex run %d starts (%s)" % (n, os.path.basename(base)))
            res = fx.codex(cwd, prompt, base + ".%d" % n, **kw)
        else:
            n += 1
            fx.log(mod, "claude run %d starts (%s)" % (n, os.path.basename(base)))
            res = fx.claude(cwd, prompt, base + ".%d" % n, **kw)
        text = str((res or {}).get("result") or "")
        if (res or {}).get("is_error") and QUOTA.search(str(_agent_answer(res) or "")):
            fx.log(mod, "the agent hit its quota (%s); waiting %d s and retrying" % (text, QUOTA_WAIT_S))
            fx.status(mod, "running", "waiting for the %s quota" % runner)
            fx.sleep(QUOTA_WAIT_S)
            continue
        fx.log(mod, "%s run %d ended: %s" % (runner, n, "error: " + text if (res or {}).get("is_error") else "done"))
        return res


def _hold_refusal(mod):
    try:
        h = MH.held(mod, MH.load(os.environ.get("RM_OWNER_HOLD_FILE") or MH.PATH))
    except MH.Unreadable as e:
        return "the owner's hold file is unreadable (%s): nothing runs on a mod it cannot prove allowed" % e
    if h and not MH.design_allowed(h):
        return ("held by the owner (%s) and its hold row carries no design-only allowance: "
                "python3 src/RimMandrake/rimflow/mod_owner_hold.py allow-design %s --said \"<his words>\"" % (h["said"], mod))
    return None


def _refusal_text(refs):
    return "\n".join("- [%s] %s: %s. Would pass: %s" % (r["rule"], r["where"], r["what"], r["would_pass"]) for r in refs)


def _write_json(path, doc):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def unreview(out):
    """A run that writes the proposal again makes every earlier review of it stale: review.json and review_attempt.json
    go (their deletion is committed with the new proposal), the reviewer's block leaves his pages and applyable leaves
    result.json. Nothing then reads the old verdict as this proposal's."""
    for name in ("review.json", "review_attempt.json", "converge.json", "fixes.json"):
        p = os.path.join(out, name)
        if os.path.exists(p):
            os.unlink(p)
    pp = os.path.join(out, "owner_pages.md")
    pages = _read(pp)
    if pages is not None and STILL_REFUSED_HEAD in pages:
        with open(pp, "w", encoding="utf-8") as f:
            f.write(pages.split(STILL_REFUSED_HEAD)[0].rstrip() + "\n")
    res = _json_file(os.path.join(out, "result.json"))
    if isinstance(res, dict) and "applyable" in res:
        res.pop("applyable")
        _write_json(os.path.join(out, "result.json"), res)


def proposal_digest(out):
    """sha256 over the proposal's files as the run wrote them: his pages cut at the reviewer's heading, result.json
    without applyable (both are the review's own writes). A review records it; resume trusts a review only of the same
    bytes."""
    import hashlib
    h = hashlib.sha256()
    for name in FILES:
        text = _read(os.path.join(out, name))
        if name == "owner_pages.md" and text is not None:
            text = text.split(STILL_REFUSED_HEAD)[0].rstrip()
        if name == "result.json":
            doc = _json_text(text)
            if isinstance(doc, dict):
                text = json.dumps({k: v for k, v in doc.items() if k != "applyable"}, sort_keys=True)
        h.update(name.encode() + b"\0" + ("\x01" if text is None else text).encode("utf-8", "replace") + b"\0")
    return h.hexdigest()


def run_mod(mod, fx, runner="codex", model=None, effort=None):
    """One cleansing run of `mod`. -> the run record {state, why, ...}; state proposed or blocked."""
    t0 = time.time()
    why = _hold_refusal(mod)
    if why:
        fx.status(mod, "blocked", why)
        fx.log(mod, "refused: " + why)
        return {"mod": mod, "state": "blocked", "why": why}
    fx.status(mod, "running", "taking a pool clone")
    clone = fx.clone(mod)
    out_rel = rel_out(mod)
    out = os.path.join(clone, out_rel)
    os.makedirs(out, exist_ok=True)
    base = os.path.join(status_dir(), "runs", mod, time.strftime("%Y%m%d-%H%M%S") + ".author")
    unreview(out)
    before = set(fx.changed(clone))
    prompt = prompt_for(clone, mod)
    fx.status(mod, "running", "%s writing the proposal" % runner)
    kw = {"model": model, "effort": effort} if runner == "codex" else {"model": model or "opus"}
    runs = [_agent(fx, mod, runner, clone, prompt, base, **kw)]
    refs, stats = check_dir(out)
    first = refs
    if refs:
        fx.log(mod, "self-check refused %d; one shape-fix pass" % len(refs))
        fix = (prompt + "\n\n---\n\n## SELF-CHECK REFUSED YOUR PROPOSAL\n\nYour proposal in %s is written. The self-check "
               "refused it on the points below. Fix only these, in that folder, keeping everything else; then run the "
               "self-check again.\n\n%s\n" % (out_rel, _refusal_text(refs)))
        runs.append(_agent(fx, mod, runner, clone, fix, base + ".fix", **kw))
        refs, stats = check_dir(out)
    result = _json_file(os.path.join(out, "result.json"))
    outcome = result.get("outcome") if isinstance(result, dict) else None
    if refs:
        state, why = "blocked", "the self-check still refuses after one fix pass (%d refusals: %s)" % (
            len(refs), "; ".join("%s %s" % (r["rule"], r["where"]) for r in refs[:4]))
    elif outcome == "blocked":
        state, why = "blocked", "the run says: %s" % result.get("blocked_on")
    else:
        state, why = "proposed", "check passes (%s bars, %s census rows, %s words on his pages)" % (
            stats.get("bars"), stats.get("census_rows"), stats.get("page_words"))
    after = fx.changed(clone)
    stray = sorted(p for p in set(after) - before if not p.startswith(out_rel))
    if stray:
        fx.log(mod, "the agent wrote outside its folder (recorded, not committed): %s" % stray[:20])
    rec = {"mod": mod, "state": state, "why": why, "runner": runner, "model": model, "effort": effort,
           "started": datetime.datetime.fromtimestamp(t0).isoformat(timespec="seconds"),
           "seconds": int(time.time() - t0), "agent_runs": len(runs), "first_check": first, "check": refs,
           "check_stats": stats, "stray": stray, "usage": [_usage(r) for r in runs],
           "agent_errors": [str(r.get("result")) for r in runs if (r or {}).get("is_error")]}
    _write_json(os.path.join(out, "run.json"), rec)
    paths = sorted(p for p in fx.changed(clone) if p.startswith(out_rel))
    if paths:
        rec["sha"] = fx.publish(clone, paths, "designer cleanse: %s proposal (%s)" % (mod, state))
        fx.log(mod, "published %s (%d files)" % (rec["sha"], len(paths)))
    fx.status(mod, state, why)
    rec["clone"] = clone
    return rec


# ------------------------------------------------------------------------------------------------ review


def reviewer_for(author):
    """The reviewer is always on the other model from the author."""
    return ("claude", "opus") if author == "codex" else ("codex", None)


def his_words(repo, mod):
    L = []
    brief = _read(os.path.join(repo, BRIEF)) or ""
    m = re.search(r"^## Why you were called.*?(?=^## )", brief, re.M | re.S)
    if m:
        L.append(m.group(0).strip())
    spec = _read(os.path.join(repo, SPEC)) or ""
    m = re.search(r"^## 1\..*?(?=^## 2\.)", spec, re.M | re.S)
    if m:
        L.append(m.group(0).strip())
    rec = "design/concepts/%s/record.json" % mod
    if os.path.exists(os.path.join(repo, rec)):
        L.append("His words on this mod by event, and his decisions and waivers: %s (read its decisions)." % rec)
    return "\n\n".join(L) or "(no recorded words were found beyond the brief and the rulings below)"


def blind(bars, rng):
    """-> (items for the reviewer, truth {(bar, n): accept|reject}). Each bar's accept and reject pictures, shuffled and
    numbered, with no label."""
    items, truth = [], {}
    for b in bars:
        pics = [(x, "accept") for x in _strs(b.get("accept"))] + [(x, "reject") for x in _strs(b.get("reject"))]
        rng.shuffle(pics)
        ps = []
        for n, (text, lab) in enumerate(pics, 1):
            ps.append({"n": n, "text": text})
            truth[(b.get("id"), n)] = (lab, text)
        items.append({"bar": b.get("id"), "says": b.get("says"), "pictures": ps})
    return items, truth


def review_prompt(repo, mod):
    e = entry(repo, mod)
    out = rel_out(mod)
    src = ["src/RimMandrake/%s/" % (e.get("source") or mod)]
    if os.path.isdir(os.path.join(repo, "design/concepts/%s" % mod)):
        src.append("design/concepts/%s/ (record.json, sheet.md, tree.json: the mod's earlier definition)" % mod)
    lore = [p for p in LORE if os.path.exists(os.path.join(repo, p))]
    heads = "\n".join("- %s: %s" % (k, v) for k, v in HEADS.items() if k not in LAUNCHER_HEADS + CONVERGE_HEADS)
    return """You are the fresh reviewer of one mod's cleansing proposal, the whole-mod check. You did not write it. You
read and refuse; you change no file and run nothing that writes. Read in this order.

## HIS WORDS (the owner's, before anything else)

%s

## SOURCE (the mod as built, and the world it lives in)

Source: %s
Rulings and lore: %s
The brief the author followed: %s (what a bar is, the fate of an extra, the file table).

## THE PROPOSAL

The folder %s: owner_pages.md, definition.md, census.json, ambiguities.md, bars.json, models.md, next_version.md,
tickets.md, result.json. Read all of it against his words, the source and the brief.

Refuse only under these heads:
%s

Each refusal names its evidence (a file and the words or code), what would pass, and the smallest fix. Then name one
capability the census missed, and one loop or three-way meeting among the bars and rules; for either you may answer
"looked, none" when you looked and found none. Do not invent a quotation, an event or a path.

Your last message is one JSON object and nothing else:
{"refusals": [{"head": "<one of the heads above>", "where": "<file and bar, row or line>", "evidence": "...",
  "would_pass": "...", "smallest_fix": "..."}],
 "missed_capability": "...", "loop_or_three_way": "..."}
""" % (his_words(repo, mod), "; ".join(src), "; ".join(lore), BRIEF, out, heads)


def blind_prompt(items):
    """The Stranger test's cold sort: only each bar's words and its pictures, shuffled and unlabelled. It is asked in a
    call of its own, with no tool and an empty folder, so the labels in bars.json are out of its reach."""
    return """You are a cold reader. Below, each bar says what a player should find in a RimWorld mod, and lists pictures:
short descriptions of builds of it, shuffled and unlabelled. Sort each picture as `accept` (a build the owner would take
as this bar met) or `reject` (one he would refuse), from the words alone. You have no files; do not ask for any.

BLIND PICTURES:
%s
END BLIND PICTURES

Your last message is one JSON object and nothing else:
{"blind_sort": [{"bar": "<id>", "n": <picture number>, "sorted": "accept" or "reject"}]}
""" % json.dumps(items, indent=1, ensure_ascii=False)


def parse_review(text):
    text = str(text or "")
    m = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    cands = m[::-1] + [text[text.find("{"):text.rfind("}") + 1]] if "{" in text else m[::-1]
    for c in cands:
        try:
            doc = json.loads(c)
        except ValueError:
            continue
        if isinstance(doc, dict):
            return doc
    return None


def validate_review(doc):
    """-> the review record's defects ([] when whole). A defect is the reviewer's, never a refusal of the proposal."""
    bad = []
    if not isinstance(doc, dict):
        return ["the reviewer's last message is not one JSON object"]
    refs = doc.get("refusals")
    if not isinstance(refs, list):
        bad.append("refusals is not a list")
    for i, r in enumerate(refs if isinstance(refs, list) else []):
        if not isinstance(r, dict):
            bad.append("refusal %d is not an object" % (i + 1))
            continue
        head = r.get("head")
        if not isinstance(head, str) or head not in HEADS or head in LAUNCHER_HEADS + CONVERGE_HEADS:
            bad.append("refusal %d: head %r is not one of the spec's heads" % (i + 1, head))
        for k in ("where", "evidence", "would_pass", "smallest_fix"):
            if not isinstance(r.get(k), str) or _blank(r.get(k)):
                bad.append("refusal %d: %s is blank or not text" % (i + 1, k))
    for k in ("missed_capability", "loop_or_three_way"):
        if _blank(doc.get(k)):
            bad.append("%s is blank (say what you found, or \"looked, none\")" % k)
    return bad


def score_blind(sort, truth):
    """-> (stranger rows, refusals): each picture's label beside the reviewer's sort; a bar with any picture sorted
    differently, or left unsorted, is a Stranger refusal (repair, as the brief's Stranger test says)."""
    got = {}
    for s in sort if isinstance(sort, list) else []:
        if isinstance(s, dict) and isinstance(s.get("bar"), str) and not isinstance(s.get("n"), bool):
            try:
                got[(s.get("bar"), int(s.get("n")))] = s.get("sorted")
            except (TypeError, ValueError):
                continue
    rows, by_bar = [], {}
    for (bar, n), (lab, text) in sorted(truth.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        g = got.get((bar, n))
        mis = g != lab
        rows.append({"bar": bar, "n": n, "text": text, "labelled": lab, "sorted": g, "mismatch": mis})
        if mis:
            by_bar.setdefault(bar, []).append((text, lab, g))
    refs = []
    for bar, ms in by_bar.items():
        refs.append({"head": "stranger", "where": "bars.json %s" % bar,
                     "evidence": "; ".join("a cold reader sorted %r as %s; the proposal labels it %s" % (t, g or "unsorted", l)
                                           for t, l, g in ms),
                     "would_pass": "pictures a cold reader sorts as the proposal does",
                     "smallest_fix": "rewrite those pictures, or the bar's says, so the line between accept and reject "
                                     "is plain from the words alone"})
    return rows, refs


def _blind_sort(fx, mod, rv_runner, rv_model, items, base):
    """The cold sort, sealed before the reviewer may open the proposal: its own call in an empty temporary folder, no
    tool for Claude, a read-only sandbox for Codex, the prompt holding only the bars' words and shuffled pictures.
    -> (sort list or None, the call's usage)."""
    if not items:
        return [], None
    cwd = tempfile.mkdtemp(prefix="cleanse-blind-")
    kw = {"model": rv_model, "tools": ""} if rv_runner == "claude" else {"sandbox": "read-only"}
    prompt, res, sort = blind_prompt(items), None, None
    try:
        for attempt in (1, 2):
            p = prompt if attempt == 1 else prompt + "\n\nYour last answer was not the one JSON object asked for. " \
                                                     "Answer again with it only.\n"
            res = _agent(fx, mod, rv_runner, cwd, p, base + (".blind.retry" if attempt == 2 else ".blind"), **kw)
            doc = parse_review(_agent_answer(res))
            if isinstance(doc, dict) and isinstance(doc.get("blind_sort"), list):
                sort = doc["blind_sort"]
                break
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    return sort, _usage(res)


def _look(fx, mod, clone, rv_runner, rv_model, base, rng):
    """One look by the reviewer: the cold sort first, in its own sealed call, then the review of the proposal.
    -> the round's record."""
    out = os.path.join(clone, rel_out(mod))
    bars = _dicts(_dict(_json_file(os.path.join(out, "bars.json"))).get("bars"))
    items, truth = blind(bars, rng)
    sort, blind_usage = _blind_sort(fx, mod, rv_runner, rv_model, items, base)
    if sort is None:
        bad = ["the cold sort's answer was unreadable twice"]
        fx.log(mod, "the reviewer's cold sort is still unreadable after one retry")
        return {"runner": rv_runner, "model": rv_model, "refusals": [], "reviewer_refusals": 0, "stranger": [],
                "missed_capability": None, "loop_or_three_way": None, "defects": bad, "usage": None,
                "blind_usage": blind_usage}
    prompt = review_prompt(clone, mod)
    kw = {"model": rv_model, "tools": "Read,Grep,Glob"} if rv_runner == "claude" else {"sandbox": "read-only"}
    doc, bad, res = None, None, None
    for attempt in (1, 2):      # a malformed review is asked once more, with what was wrong; nothing loops past that
        p = prompt if attempt == 1 else prompt + ("\n\nYour last answer could not be read as the record: %s. Answer "
                                                  "again with the one JSON object only.\n" % "; ".join(bad))
        res = _agent(fx, mod, rv_runner, clone, p, base + (".retry" if attempt == 2 else ""), **kw)
        doc = parse_review(_agent_answer(res))
        bad = validate_review(doc)
        if not bad:
            break
    if bad:     # the reviewer's record is unreadable: no reading of the proposal, so no refusal of it
        fx.log(mod, "the reviewer's record is still unreadable after one retry: %s" % "; ".join(bad))
        return {"runner": rv_runner, "model": rv_model, "refusals": [], "reviewer_refusals": 0, "stranger": [],
                "missed_capability": None, "loop_or_three_way": None, "defects": bad, "usage": _usage(res),
                "blind_usage": blind_usage}
    rows, stranger = score_blind(sort, truth)
    refusals = [r for r in doc.get("refusals") or [] if isinstance(r, dict)]
    return {"runner": rv_runner, "model": rv_model, "refusals": refusals + stranger, "reviewer_refusals": len(refusals),
            "stranger": rows, "missed_capability": (doc or {}).get("missed_capability"),
            "loop_or_three_way": (doc or {}).get("loop_or_three_way"), "defects": bad or [], "usage": _usage(res),
            "blind_usage": blind_usage}


def _still_refused_block(remaining):
    L = [STILL_REFUSED_HEAD, "", "The proposal cannot be applied until each of these is resolved or you accept it.", ""]
    for r in remaining:
        L.append("- %s (%s). %s Would pass: %s Smallest fix: %s" % (
            HEADS.get(r.get("head"), r.get("head")), r.get("where"), r.get("evidence"), r.get("would_pass"),
            r.get("smallest_fix")))
    return "\n".join(L) + "\n"


def _reviewer_failed(fx, mod, clone, rounds, t0, fix_rec=None):
    """The reviewer gave no readable record: the mod is blocked on its review, nothing about the proposal is decided,
    and review.json is not written (so a resumed fleet looks again). The attempt is kept in review_attempt.json."""
    out_rel = rel_out(mod)
    why = "the reviewer's record was unreadable twice (%s); the proposal is unreviewed" % "; ".join(rounds[-1]["defects"])
    _write_json(os.path.join(clone, out_rel, "review_attempt.json"), {
        "mod": mod, "rounds": rounds, "fix_run": fix_rec, "seconds": int(time.time() - t0),
        "at": datetime.datetime.now().isoformat(timespec="seconds")})
    paths = sorted(p for p in fx.changed(clone) if p.startswith(out_rel))
    sha = fx.publish(clone, paths, "designer cleanse: %s review attempt (reviewer unreadable)" % mod) if paths else None
    fx.log(mod, "review blocked: %s (published %s)" % (why, sha))
    fx.status(mod, "blocked", why)
    return {"mod": mod, "state": "blocked", "why": why, "sha": sha, "clone": clone}


def review_mod(mod, fx, author="codex", author_model=None, effort=None, clone=None):
    """The whole-mod check of spec §4. -> {state: reviewed | refused-after-second-look | blocked, ...}."""
    t0 = time.time()
    why = _hold_refusal(mod)
    if why:
        fx.status(mod, "blocked", why)
        fx.log(mod, "review refused: " + why)
        return {"mod": mod, "state": "blocked", "why": why}
    clone = clone or fx.clone(mod)
    out_rel = rel_out(mod)
    out = os.path.join(clone, out_rel)
    refs, _ = check_dir(out)
    result = _json_file(os.path.join(out, "result.json"))
    if refs or not isinstance(result, dict):
        why = "no proposal that passes the self-check to review (%d refusals)" % len(refs)
        fx.status(mod, "blocked", why)
        return {"mod": mod, "state": "blocked", "why": why}
    if result.get("outcome") != "proposed":
        why = "the run is blocked: %s" % result.get("blocked_on")
        fx.status(mod, "blocked", why)
        return {"mod": mod, "state": "blocked", "why": why}
    pre = dict(result)
    rv_runner, rv_model = reviewer_for(author)
    fx.status(mod, "running", "review: %s %s first look" % (rv_runner, rv_model or ""))
    base = os.path.join(status_dir(), "runs", mod, time.strftime("%Y%m%d-%H%M%S") + ".review")
    rng = random.Random("%s %s" % (mod, time.time()))
    rounds = [_look(fx, mod, clone, rv_runner, rv_model, base + ".look1", rng)]
    if rounds[0]["defects"]:
        return _reviewer_failed(fx, mod, clone, rounds, t0)
    fix_rec = None
    if rounds[0]["refusals"] and _hold_refusal(mod):
        why = _hold_refusal(mod)       # the hold changed during the first look: no writing author runs
        fx.status(mod, "blocked", why)
        fx.log(mod, "review fix refused: " + why)
        return {"mod": mod, "state": "blocked", "why": why, "clone": clone}
    if rounds[0]["refusals"]:
        fx.log(mod, "the first look refused %d; one fix run by the author" % len(rounds[0]["refusals"]))
        fx.status(mod, "running", "review: author fixing %d refusals" % len(rounds[0]["refusals"]))
        recs = json.dumps(rounds[0]["refusals"], indent=1, ensure_ascii=False)
        fix = (prompt_for(clone, mod) + "\n\n---\n\n## THE REVIEWER REFUSED PARTS OF YOUR PROPOSAL\n\nYour proposal in "
               "%s is written. A fresh reviewer on another model refused the points below. Fix each in that folder "
               "(keep everything else, keep result.json's counts equal to the files), then run the self-check again. "
               "Where you are sure the reviewer is wrong, say why in ambiguities.md instead of changing the proposal."
               "\n\n%s\n" % (out_rel, recs))
        kw = {"model": author_model, "effort": effort} if author == "codex" else {"model": author_model or "opus"}
        res = _agent(fx, mod, author, clone, fix, base + ".fix", **kw)
        after, _ = check_dir(out)
        fix_rec = {"usage": _usage(res), "check_after": after,
                   "error": str(res.get("result")) if (res or {}).get("is_error") else None}
        fx.status(mod, "running", "review: second look")
        rounds.append(_look(fx, mod, clone, rv_runner, rv_model, base + ".look2", rng))
        if rounds[-1]["defects"]:
            return _reviewer_failed(fx, mod, clone, rounds, t0, fix_rec)
    remaining = list(rounds[-1]["refusals"])
    result = _json_file(os.path.join(out, "result.json"))
    if not isinstance(result, dict):     # the fix broke result.json: its bytes stay beside, the counts before it return
        bad_p = os.path.join(out, "result.json")
        if os.path.exists(bad_p):
            os.replace(bad_p, os.path.join(out, "result.broken-by-fix.txt"))
        result = dict(pre)
        result["note"] = "result.json as it stood before the review's fix run: the fix left it unreadable " \
                         "(kept as result.broken-by-fix.txt)"
    if result.get("outcome") != "proposed":
        remaining.append({"head": "self_check", "where": "result.json", "evidence": "after the fix the outcome is "
                          "%r, not proposed" % result.get("outcome"), "would_pass": "outcome proposed",
                          "smallest_fix": "restore the proposal, or say in ambiguities.md why it cannot be one"})
    if fix_rec and fix_rec["check_after"]:
        remaining = remaining + [{"head": "self_check", "where": r["where"], "evidence": "after the fix the "
                                  "self-check refuses: " + r["what"], "would_pass": r["would_pass"],
                                  "smallest_fix": r["would_pass"]} for r in fix_rec["check_after"]]
    pages_p = os.path.join(out, "owner_pages.md")
    pages = (_read(pages_p) or "").split(STILL_REFUSED_HEAD)[0].rstrip() + "\n"
    if remaining:
        pages += "\n" + _still_refused_block(remaining)
    with open(pages_p, "w", encoding="utf-8") as f:
        f.write(pages)
    result["applyable"] = not remaining
    _write_json(os.path.join(out, "result.json"), result)
    state = "reviewed" if not remaining else "refused-after-second-look"
    review = {"mod": mod, "author": author, "reviewer": {"runner": rv_runner, "model": rv_model}, "rounds": rounds,
              "fix_run": fix_rec, "remaining": remaining, "applyable": not remaining,
              "digest": proposal_digest(out),
              "seconds": int(time.time() - t0), "at": datetime.datetime.now().isoformat(timespec="seconds")}
    _write_json(os.path.join(out, "review.json"), review)
    paths = sorted(p for p in fx.changed(clone) if p.startswith(out_rel))
    sha = fx.publish(clone, paths, "designer cleanse: %s review (%s)" % (mod, state)) if paths else None
    why = "first look %d refusals%s; %s" % (len(rounds[0]["refusals"]), ", second look %d" % len(remaining)
                                           if len(rounds) > 1 else "", "applyable" if not remaining else "not applyable")
    fx.log(mod, "review %s: %s (published %s)" % (state, why, sha))
    fx.status(mod, state, why)
    return {"mod": mod, "state": state, "why": why, "sha": sha, "clone": clone, "review": review}


# ------------------------------------------------------------------------------------------------ converge


ENTRY_CAP = 6000        # our own rule: one changed entry shown to the verifier at most this many characters (it can Read)
ENTRIES_CAP = 120000    # our own rule: all the changed entries shown at most this many (the real proposals: 157 to 349
#                         entries each, measured 2026-11-17; a fix touching every census row would pass 100k)


def _entries(name, text):
    """-> {entry name: text} of one proposal file. A JSON file splits per list item with an id ("bars.json bars/B1"),
    per value of a dict of objects ("bars.json old_bars/<id>") and per other top-level key; markdown splits per heading.
    The launcher's own writes (his pages' reviewer block, result.json's applyable) are no entry."""
    if text is None:
        return {}
    E = {}

    def put(key, val):
        k, n = key, 1
        while k in E:
            n += 1
            k = "%s (%d)" % (key, n)
        E[k] = val

    if name.endswith(".json"):
        doc = _json_text(text)
        if not isinstance(doc, dict):
            put(name, text)
            return E
        dump = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False, indent=1)     # noqa: E731
        for k, v in doc.items():
            if name == "result.json" and k == "applyable":
                continue
            if isinstance(v, list) and v and all(isinstance(x, dict) and isinstance(x.get("id"), str) for x in v):
                for x in v:
                    put("%s %s/%s" % (name, k, x["id"]), dump(x))
            elif isinstance(v, dict) and v and all(isinstance(x, dict) for x in v.values()):
                for kk, x in v.items():
                    put("%s %s/%s" % (name, k, kk), dump(x))
            else:
                put("%s %s" % (name, k), dump(v))
        return E
    if name == "owner_pages.md":
        text = text.split(STILL_REFUSED_HEAD)[0].rstrip() + "\n"
    head, buf = "(top)", []
    for line in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if m:
            if head != "(top)" or "".join(buf).strip():
                put("%s %s" % (name, head), "\n".join(buf).strip())
            head, buf = m.group(1), [line]
        else:
            buf.append(line)
    if head != "(top)" or "".join(buf).strip():
        put("%s %s" % (name, head), "\n".join(buf).strip())
    return E


def proposal_entries(get):
    """-> every entry of the proposal, `get(name)` giving a file's text or None."""
    E = {}
    for name in FILES:
        E.update(_entries(name, get(name)))
    return E


def changed_entries(before, after):
    """-> [(entry, before text or None, after text or None)] for every entry added, removed or changed."""
    return [(k, before.get(k), after.get(k)) for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)]


def _entry_key(s):
    s = _norm(s).strip("`'\" ")
    m = re.match(r"^(\S+\.(?:json|md))[:\s]*(.*)$", s)
    if not m:
        return ("", s)
    rest = m.group(2).strip()
    return (m.group(1), rest.split("/")[-1].strip() if rest else "")


def entry_changed(name, changed):
    """-> the changed entry `name` names (exactly, or the same file and last path part), or None."""
    k = _entry_key(name)
    for c in changed:
        if _norm(c) == _norm(name) or _entry_key(c) == k:
            return c
    return None


def _bar_of(rec, bars):
    """-> the id of the bar a stranger record names, or None when no bar of bars.json is named in its where."""
    where = str(rec.get("where") or "")
    for b in bars:
        bid = b.get("id")
        if isinstance(bid, str) and bid and re.search(r"(?<![\w])%s(?![\w])" % re.escape(bid), where):
            return bid
    return None


def check_records(refs, outcome, prefix):
    """-> the self-check's refusals as self_check records, one per rule (a rule refusing 82 census rows is one record
    naming them, so the author's prompt and his pages stay readable)."""
    recs, by = [], {}
    if outcome != "proposed":
        recs.append({"head": "self_check", "where": "result.json", "evidence": "the outcome is %r, not proposed"
                     % outcome, "would_pass": "outcome proposed", "smallest_fix": "restore the proposal"})
    for f in refs:
        by.setdefault(f["rule"], []).append(f)
    for rule, fs in by.items():
        shown = "; ".join("%s: %s" % (f["where"], f["what"]) for f in fs[:12])
        more = " (and %d more of the same rule)" % (len(fs) - 12) if len(fs) > 12 else ""
        recs.append({"head": "self_check", "where": ", ".join(sorted({f["where"].split(" row ")[0].split(" ")[0]
                                                                       for f in fs})),
                     "evidence": "the self-check refuses %d (%s): %s%s" % (len(fs), rule, shown, more),
                     "would_pass": fs[0]["would_pass"], "smallest_fix": fs[0]["would_pass"]})
    return [_record("%s.%d" % (prefix, i), r) for i, r in enumerate(recs, 1)]


def _record(rid, r):
    return {"id": rid, "head": r.get("head"), "where": r.get("where"), "evidence": r.get("evidence"),
            "would_pass": r.get("would_pass"), "smallest_fix": r.get("smallest_fix")}


def converge_fix_prompt(mod, records, rnd):
    out = rel_out(mod)
    return """CONVERGE FIX, round %d of at most %d, of the cleansing proposal of %s.

Your proposal in %s is written and published. A reviewer on another model refused the records below; they are all that
stands between it and the owner's look. Fix each record in that folder and change nothing a record does not need: every
entry you change is read again, and a change that breaks an entry is refused as a regression. Each record says what
would pass (would_pass) and the smallest fix (smallest_fix). Where you are sure a record is wrong, change nothing for it
and say why in fixes.json and in ambiguities.md; the verifier weighs that.

The brief you followed is %s (what a bar is, the fate of an extra, the file table); read it again where a record needs
it. Keep result.json's counts equal to the files. Do not write review.json or converge.json, and do not write the
heading "%s" on owner_pages.md: the launcher writes those. Write nothing outside the folder. Then run the self-check:
python3 src/RimMandrake/rimflow/designer_cleanse.py check %s

RECORDS:
%s
END RECORDS

Last, write %sfixes.json, one object:
{"fixes": [{"id": "<record id>", "changed": "<what you changed, or why you changed nothing>",
  "where": "<file and entry>"}]}
with one fix per record.
""" % (rnd, CONVERGE_ROUNDS, mod, out, BRIEF, STILL_REFUSED_HEAD, out, json.dumps(records, indent=1,
                                                                              ensure_ascii=False), out)


def converge_verify_prompt(mod, records, fixes_text, changed, rnd):
    heads = "\n".join("- %s: %s" % (k, v) for k, v in HEADS.items() if k not in LAUNCHER_HEADS + CONVERGE_HEADS)
    shown, room = [], ENTRIES_CAP
    for name, b, a in changed:
        if room <= 0:
            shown.append("### %s\n(not shown: the changed entries pass %d characters; Read the file)\n" % (name, ENTRIES_CAP))
            continue
        room -= len(b or "") + len(a or "")
        cut = lambda t: "(absent)" if t is None else (t if len(t) <= ENTRY_CAP else t[:ENTRY_CAP] +   # noqa: E731
                                                      "\n... (cut; Read the file for the rest)")
        shown.append("### %s\nBEFORE:\n%s\nAFTER:\n%s\n" % (name, cut(b), cut(a)))
    return """VERIFY THE FIX, converge round %d, of the cleansing proposal of %s. You did not write it. You read and judge;
you change no file and run nothing that writes.

A reviewer refused the records below. The author was asked to fix them in %s and to change nothing else. Judge each
record: "fixed" when the proposal now does what its would_pass says (or when the author's account shows the record does
not stand), "not_fixed" otherwise. Your evidence names the file and the words.

RECORDS:
%s
END RECORDS

THE AUTHOR'S ACCOUNT (fixes.json):
%s

THE ENTRIES THE FIX CHANGED (each before, then after; no other entry changed):
%s
A regression is a change above that breaks its own entry under one of these heads:
%s
Name a regression's entry exactly as it is headed above. A gap you notice in an entry the fix did not change is not a
regression: it is the earlier look's miss; put it in advisory_late, which blocks nothing. Do not invent a quotation, an
event or a path.

Your last message is one JSON object and nothing else:
{"verdicts": [{"id": "<record id>", "verdict": "fixed" or "not_fixed", "evidence": "..."}],
 "regressions": [{"entry": "<a changed entry as headed above>", "evidence": "...", "would_pass": "...",
   "smallest_fix": "..."}],
 "advisory_late": [{"what": "...", "reason": "..."}]}
""" % (rnd, mod, rel_out(mod), json.dumps(records, indent=1, ensure_ascii=False),
       fulltext.clip(fixes_text or "(the author wrote no fixes.json)", 8000, rel_out(mod) + "fixes.json"), "\n".join(shown) or "(none)\n", heads)


def _verify(fx, mod, clone, rv_runner, rv_model, records, fixes_text, changed, rnd, base):
    """The verifier's answer. -> (verdicts {id: {verdict, evidence}}, regressions, advisory_late, defects). A record the
    verifier gives no readable verdict for after one retry has no entry in verdicts: nobody looked (failure_class)."""
    prompt = converge_verify_prompt(mod, records, fixes_text, changed, rnd)
    kw = {"model": rv_model, "tools": "Read,Grep,Glob"} if rv_runner == "claude" else {"sandbox": "read-only"}
    ids = [r["id"] for r in records]
    got, regs, late, missing = {}, [], [], ids
    for attempt in (1, 2):
        p = prompt if attempt == 1 else prompt + ("\n\nYour last answer gave no readable verdict for %s. Answer again "
                                                  "with the one JSON object only, a verdict for every record.\n"
                                                  % ", ".join(missing))
        res = _agent(fx, mod, rv_runner, clone, p, base + (".verify.retry" if attempt == 2 else ".verify"), **kw)
        doc = parse_review(_agent_answer(res))
        if isinstance(doc, dict):
            for v in _dicts(doc.get("verdicts")):
                if v.get("id") in ids and v.get("verdict") in ("fixed", "not_fixed"):
                    got[v["id"]] = {"verdict": v["verdict"], "evidence": str(v.get("evidence") or "")}
            regs = _dicts(doc.get("regressions")) or regs
            late = [x for x in (doc.get("advisory_late") or []) if isinstance(x, (dict, str))] or late
        missing = [i for i in ids if i not in got]
        if not missing:
            break
    defects = ["no readable verdict for %s after one retry" % ", ".join(missing)] if missing else []
    return got, regs, late, defects


def converge_done(repo, mod):
    """Resume: converged, or two rounds behind it, or blocked; of these very bytes."""
    out = os.path.join(repo, rel_out(mod))
    res = _json_file(os.path.join(out, "result.json"))
    if isinstance(res, dict) and res.get("outcome") == "blocked":
        return True
    name, doc = latest_verdict(out)
    if doc is None or not verdict_current(out, doc):
        return False
    if name == "converge.json":
        return doc.get("open") == [] or len(_dicts(doc.get("rounds"))) >= CONVERGE_ROUNDS
    # a first look only, even a clean one: round 0 still writes converge.json, the one verdict apply and the owner's
    # plan check read (a clean review.json left "already done" with no converge.json could never be applied)
    return False


def _converge_state(name, doc):
    if name == "converge.json":
        return "converged" if doc.get("applyable") is True else "open-after-converge"
    return "converged" if not doc.get("remaining") else "open-after-converge"


def converge_mod(mod, fx, clone=None):
    """The converge round. -> {state: converged | open-after-converge | blocked, ...}."""
    t0 = time.time()
    why = _hold_refusal(mod)
    if why:
        fx.status(mod, "blocked", why)
        fx.log(mod, "converge refused: " + why)
        return {"mod": mod, "state": "blocked", "why": why}
    clone = clone or fx.clone(mod)
    out_rel = rel_out(mod)
    out = os.path.join(clone, out_rel)

    def blocked(why):
        fx.status(mod, "blocked", why)
        fx.log(mod, "converge blocked: " + why)
        return {"mod": mod, "state": "blocked", "why": why, "clone": clone}

    result = _json_file(os.path.join(out, "result.json"))
    if not isinstance(result, dict) or result.get("outcome") != "proposed":
        return blocked("no proposed result.json to converge (%s)" % (result.get("outcome") if isinstance(result, dict)
                                                                     else "unreadable or missing"))
    name, doc = latest_verdict(out)
    if doc is None:
        return blocked("no readable first look (review.json) to converge from: review it first")
    if not verdict_current(out, doc):
        return blocked("%s is a verdict of other bytes (its digest is not the proposal's): stale; review it again"
                       % name)
    key = "open" if name == "converge.json" else "remaining"
    if not isinstance(doc.get(key), list) or not all(isinstance(r, dict) for r in doc[key]):
        # an unreadable record list is not zero open records: it never converges as clean
        return blocked("%s %s is %s, not a list of records: the verdict cannot be read; review it again"
                       % (name, key, type(doc.get(key)).__name__))
    if converge_done(clone, mod):
        state = _converge_state(name, doc)
        fx.status(mod, state, "already done (resumed): %s%s" % (out_rel, name))
        return {"mod": mod, "state": state, "why": "already done", "clone": clone}
    run = _dict(_json_file(os.path.join(out, "run.json")))
    if name == "converge.json":
        cv = doc
        rounds, open_ = list(_dicts(cv.get("rounds"))), list(_dicts(cv.get("open")))
        author, late = cv.get("author") or "codex", list(cv.get("advisory_late") or [])
    else:
        cv, rounds, late = {}, [], []
        open_ = [_record("R%d" % i, r) for i, r in enumerate(_dicts(doc.get("remaining")), 1)
                 if r.get("head") != "self_check"]
        pre_refs, pre_stats = check_dir(out)       # what today's check refuses is open before any fix: round one's
        open_ += check_records(pre_refs, "proposed", "C0")
        author = doc.get("author") if doc.get("author") in ("codex", "claude") else run.get("runner") or "codex"
    a_model, a_effort = (run.get("model"), run.get("effort")) if run.get("runner") == author else (None, None)
    akw = {"model": a_model, "effort": a_effort} if author == "codex" else {"model": a_model or "opus"}
    rv_runner, rv_model = reviewer_for(author)
    base = os.path.join(status_dir(), "runs", mod, time.strftime("%Y%m%d-%H%M%S") + ".converge")
    rng = random.Random("%s %s" % (mod, time.time()))
    sha = None
    final_refs = []
    def finish(rnd, open_, late, rounds, sha):
        """His pages' block, converge.json, result.json's applyable, and one publish of the cleanse folder."""
        pages_p = os.path.join(out, "owner_pages.md")
        pages = (_read(pages_p) or "").split(STILL_REFUSED_HEAD)[0].rstrip() + "\n"
        if open_:
            pages += "\n" + _still_refused_block(open_)
        with open(pages_p, "w", encoding="utf-8") as f:
            f.write(pages)
        cv = {"mod": mod, "author": author, "verifier": {"runner": rv_runner, "model": rv_model},
              "first_look": "review.json", "rounds": rounds, "open": open_, "advisory_late": late}
        _write_json(os.path.join(out, "converge.json"), cv)
        final_refs, _ = check_dir(out)
        cur = _dict(_json_file(os.path.join(out, "result.json")))
        cur["applyable"] = not open_ and not final_refs
        _write_json(os.path.join(out, "result.json"), cur)
        cv.update(applyable=cur["applyable"], digest=proposal_digest(out), seconds=int(time.time() - t0),
                  at=datetime.datetime.now().isoformat(timespec="seconds"))
        _write_json(os.path.join(out, "converge.json"), cv)
        paths = sorted(p for p in fx.changed(clone) if p.startswith(out_rel))
        sha = fx.publish(clone, paths, "designer cleanse: %s converge round %d (%d open)" % (mod, rnd, len(open_))) \
            if paths else sha
        fx.log(mod, "converge round %d: %d open, %d advisory late, check %s (published %s)"
               % (rnd, len(open_), len(late), "refuses" if final_refs else "passes", sha))
        return cv, sha

    if not open_ and not rounds:     # nothing stands open from the first look (its only records were the self-check's)
        cv, sha = finish(0, open_, late, rounds, sha)
    while len(rounds) < CONVERGE_ROUNDS and open_:
        why = _hold_refusal(mod)
        if why:
            return blocked(why)
        rnd = len(rounds) + 1
        fx.status(mod, "running", "converge round %d: author fixing %d records" % (rnd, len(open_)))
        before = proposal_entries(lambda n: fx.head_text(clone, out_rel + n))
        pre = _dict(_json_file(os.path.join(out, "result.json"))) or dict(result)
        fp = os.path.join(out, "fixes.json")
        if os.path.exists(fp):
            os.unlink(fp)
        res = _agent(fx, mod, author, clone, converge_fix_prompt(mod, open_, rnd), base + ".r%d.fix" % rnd, **akw)
        now = _json_file(os.path.join(out, "result.json"))
        if not isinstance(now, dict):      # the fix broke result.json: its bytes stay beside, the counts before return
            bad_p = os.path.join(out, "result.json")
            if os.path.exists(bad_p):
                os.replace(bad_p, os.path.join(out, "result.broken-by-fix.txt"))
            now = dict(pre)
            now["note"] = "result.json as it stood before converge round %d: the fix left it unreadable (kept as " \
                          "result.broken-by-fix.txt)" % rnd
            _write_json(os.path.join(out, "result.json"), now)
        fixes_text = _read(fp)
        changed = changed_entries(before, proposal_entries(lambda n: _read(os.path.join(out, n))))
        names = [c[0] for c in changed]
        if (res or {}).get("is_error") and not names and fixes_text is None:
            # it changed nothing: a run that died spends no round (failure_class); the same round runs on the next start
            return blocked("converge round %d is not spent: the author run %s (%s)" % (
                rnd, FC.KILLED, " ".join(str(res.get("result")).split())))
        refs, _ = check_dir(out)
        verdicts = {}
        bars = _dicts(_dict(_json_file(os.path.join(out, "bars.json"))).get("bars"))
        to_verify = []
        for r in open_:
            if r.get("head") == "self_check":
                continue           # the self-check's own: superseded by this round's reading below
            bar = _bar_of(r, bars) if r.get("head") == "stranger" else None
            if r.get("head") == "stranger" and bar:
                items, truth = blind([b for b in bars if b.get("id") == bar], rng)
                sort, _u = _blind_sort(fx, mod, rv_runner, rv_model, items, base + ".r%d.%s" % (rnd, r["id"]))
                if sort is None:
                    return blocked("converge round %d is not spent: %s (could not look): the cold sort was unreadable "
                                   "twice" % (rnd, FC.LK.NO_LOOK))
                _rows, srefs = score_blind(sort, truth)
                verdicts[r["id"]] = {"verdict": "not_fixed" if srefs else "fixed",
                                     "evidence": srefs[0]["evidence"] if srefs else "a cold reader sorts every picture "
                                     "of %s as the proposal labels it" % bar, "by": "cold sort"}
                if srefs:
                    r = dict(r, evidence=srefs[0]["evidence"])
                    verdicts[r["id"]]["record"] = r
            else:
                to_verify.append(r)
        regs, defects = [], []
        if to_verify:
            fx.status(mod, "running", "converge round %d: verifier on %d records" % (rnd, len(to_verify)))
            got, regs, rlate, defects = _verify(fx, mod, clone, rv_runner, rv_model, to_verify, fixes_text, changed,
                                                rnd, base + ".r%d" % rnd)
            if len(got) < len(to_verify):
                return blocked("converge round %d is not spent: %s (could not look): %s" % (
                    rnd, FC.LK.NO_LOOK, "; ".join(defects)))
            verdicts.update(got)
            for x in rlate:
                late.append(dict(x, round=rnd) if isinstance(x, dict) else {"what": x, "round": rnd})
        new_open = []
        for r in open_:
            v = verdicts.get(r["id"])
            if r.get("head") != "self_check" and v and v["verdict"] != "fixed":
                new_open.append(v.get("record") or r)
        k = 0
        for g in regs:
            hit = entry_changed(str(g.get("entry") or g.get("where") or ""), names)
            if hit and not _blank(g.get("evidence")):
                k += 1
                new_open.append({"id": "G%d.%d" % (rnd, k), "head": "regression", "where": hit,
                                 "evidence": g.get("evidence"), "would_pass": g.get("would_pass") or "the entry as "
                                 "it stood before the fix, with the record's fix kept",
                                 "smallest_fix": g.get("smallest_fix") or g.get("would_pass") or "undo the break"})
            else:
                late.append({"round": rnd, "entry": g.get("entry") or g.get("where"), "what": g.get("evidence"),
                             "would_pass": g.get("would_pass"), "reason": "named as a regression on an entry the fix "
                             "did not change: the earlier look's miss"})
        cur = _dict(_json_file(os.path.join(out, "result.json")))
        new_open += check_records(refs, cur.get("outcome"), "C%d" % rnd)
        rounds.append({"n": rnd, "records": open_, "fixes": _json_text(fixes_text) if fixes_text else None,
                       "verdicts": verdicts, "changed_entries": names, "verifier_defects": defects,
                       "author_usage": _usage(res), "author_error": str(res.get("result"))
                       if (res or {}).get("is_error") else None, "open_after": new_open})
        open_ = new_open
        cv, sha = finish(rnd, open_, late, rounds, sha)
    state = "converged" if cv.get("applyable") is True else "open-after-converge"
    why = "%d rounds; %d open; %d advisory late; %s" % (len(rounds), len(open_), len(late),
                                                       "applyable" if state == "converged" else "not applyable")
    fx.status(mod, state, why)
    return {"mod": mod, "state": state, "why": why, "sha": sha, "clone": clone, "converge": cv}


# ------------------------------------------------------------------------------------------------ gather


def page_questions(pages):
    """-> his questions on one mod's pages: each `Q<n>.` line (bold or not) with the lines that follow it up to a blank
    line or a heading, joined into one line."""
    qs, cur = [], None
    for line in (pages or "").split(STILL_REFUSED_HEAD)[0].splitlines():
        s = line.strip()
        m = re.match(r"^(?:[-*>]\s+)?(?:\*\*|__)?Q(\d+)\.(?:\*\*|__)?\s*(.*)$", s)
        if m:
            if cur:
                qs.append(cur)
            cur = [m.group(2)]
        elif cur is not None:
            if not s or s.startswith("#"):
                qs.append(cur)
                cur = None
            else:
                cur.append(s)
    if cur:
        qs.append(cur)
    return [t for t in (" ".join(x).strip() for x in qs) if t]


def gather(repo):
    """-> (text, totals): every mod's cleanse in one page, ALL_BIOMES.md in the status folder. A top table (applyable and
    the reviewer's open records per mod), every question numbered once with its mod, every recommended retirement in
    words (no id he has not been shown), then each mod's two pages in full."""
    root = os.path.join(repo, "design", "concepts")
    mods = sorted(m for m in os.listdir(root) if os.path.exists(os.path.join(root, m, "cleanse", "result.json"))) \
        if os.path.isdir(root) else []
    rows, qlines, rlines, parts = [], [], [], []
    tot = {"mods": len(mods), "applyable": 0, "questions": 0, "retirements": 0, "open": 0}
    for m in mods:
        out = os.path.join(root, m, "cleanse")
        res = _dict(_json_file(os.path.join(out, "result.json")))
        c = _dict(res.get("counts"))
        name, doc = latest_verdict(out)
        rem = open_records(out)
        if doc is None:
            ap = "not reviewed"
        elif not verdict_current(out, doc):
            ap = "stale review"
        else:
            ap = "yes" if res.get("applyable") is True else "no"
        tot["applyable"] += ap == "yes"
        tot["open"] += len(rem or [])
        pages = _read(os.path.join(out, "owner_pages.md")) or ""
        qs = page_questions(pages)
        for q in qs:
            tot["questions"] += 1
            qlines.append("%d. **%s**: %s" % (tot["questions"], m, q))
        census = _dicts(_dict(_json_file(os.path.join(out, "census.json"))).get("rows"))
        for r in census:
            if r.get("fate") == "recommend_retire":
                tot["retirements"] += 1
                rlines.append("- **%s**: %s. Why: %s" % (m, str(r.get("what") or "").rstrip("."),
                                                         str(r.get("why") or "").strip()))
        rows.append("| %s | %s | %s -> %s | %s | %s | %d | %s | %s |" % (
            m, res.get("outcome") or "?", c.get("old_bars", "?"), c.get("bars", "?"), c.get("next_version", "?"),
            c.get("recommend_retire", "?"), len(qs), ap, "-" if rem is None else len(rem)))
        parts.append("## %s\n\n(%s)\n\n%s" % (m, os.path.join("design", "concepts", m, "cleanse", "owner_pages.md"),
                                              pages.strip()))
    text = "\n".join([
        "# Designer Cleanse: every biome (gathered %s)" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "",
        "%d mods; %d applyable; %d open reviewer records; %d questions; %d recommended retirements." % (
            tot["mods"], tot["applyable"], tot["open"], tot["questions"], tot["retirements"]), "",
        "| mod | outcome | bars before -> after | next version | retire | questions | applyable | open |",
        "|---|---|---|---|---|---|---|---|"] + rows + [
        "", "## Every question", ""] + (qlines or ["(none)"]) + [
        "", "## Every recommended retirement", ""] + (rlines or ["(none)"]) + [""] + [p + "\n" for p in parts])
    os.makedirs(status_dir(), exist_ok=True)
    with open(os.path.join(status_dir(), "ALL_BIOMES.md"), "w", encoding="utf-8") as f:
        f.write(text)
    return text, tot


# ------------------------------------------------------------------------------------------------ fleet and status


class Status:
    """status.json (per mod: state, why, at) and a plain status.md, one line per mod. Writers lock the file."""

    def __init__(self, d):
        self.dir = d
        os.makedirs(d, exist_ok=True)
        self.json = os.path.join(d, "status.json")
        self.md = os.path.join(d, "status.md")
        self._t = threading.Lock()

    @contextlib.contextmanager
    def _locked(self):
        with self._t, open(self.json + ".lock", "a+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def read(self):
        try:
            with open(self.json, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, ValueError):
            doc = {}
        doc.setdefault("mods", {})
        return doc

    def set(self, mod, state, why=""):
        with self._locked():
            doc = self.read()
            doc["mods"][mod] = {"state": state, "why": why, "at": datetime.datetime.now().isoformat(timespec="seconds")}
            doc["updated"] = doc["mods"][mod]["at"]
            tmp = self.json + ".tmp"
            _write_json(tmp, doc)
            os.replace(tmp, self.json)
            lines = ["# Designer Cleanse status (updated %s)" % doc["updated"], ""]
            w = max(len(m) for m in doc["mods"])
            for m, r in doc["mods"].items():
                lines.append("%-*s  %-26s %s  %s" % (w, m, r["state"], r["at"], r.get("why") or ""))
            with open(self.md + ".tmp", "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            os.replace(self.md + ".tmp", self.md)


def fleet_order(repo, but=(), only=None):
    """Every biome of the compose file but `but`: the concept-folder six first, in the Conductor's order, then the rest
    in the file's order. `only` narrows it."""
    biomes = [e["key"] for e in compose(repo) if e.get("group") == "biome" and e["key"] not in set(but)]
    first = [m for m in CONCEPT_FIRST if m in biomes]
    order = first + [m for m in biomes if m not in first]
    return [m for m in order if m in set(only)] if only else order


def latest_verdict(out):
    """-> (name, doc) of the latest verdict on the proposal: converge.json when it exists, else review.json; doc None when
    neither reads as an object."""
    for name in ("converge.json", "review.json"):
        if os.path.exists(os.path.join(out, name)):
            doc = _json_file(os.path.join(out, name))
            return name, doc if isinstance(doc, dict) else None
    return None, None


def verdict_current(out, doc):
    """A verdict of these very bytes: its digest equals the proposal's. A verdict with no digest at all was written by the
    launcher before 2026-11-17 (the 23 first looks of 445c1012a5): the Conductor, 2026-11-17, rules it the first look, not
    stale ("an old review with no digest is accepted as the first look for converge")."""
    if not isinstance(doc, dict):
        return False
    if "digest" not in doc:
        return True
    return doc.get("digest") == proposal_digest(out)


def done(repo, mod):
    """Resume: a mod whose proposal passes check and whose latest verdict (converge.json, else review.json) is of these
    very bytes, or that says it is blocked, is skipped. A verdict whose digest is of other bytes is stale; one with no
    digest is an older launcher's first look and is kept (verdict_current)."""
    out = os.path.join(repo, rel_out(mod))
    if not os.path.exists(os.path.join(out, "result.json")):
        return False
    refs, stats = check_dir(out)
    if refs:
        return False
    if stats.get("outcome") == "blocked":
        return True
    return verdict_current(out, latest_verdict(out)[1])


def fleet_unit_argv(args, unit):
    """The detached unit: its own systemd user unit, no wall-time bound, surviving every window."""
    try:
        import detached_helper as DH
        path = DH.unit_path(os.environ.get("PATH"), DH.claude_bin())
    except Exception:       # noqa: BLE001
        path = os.environ.get("PATH", "/usr/bin:/bin")
    env = ["--setenv", "PATH=" + path]
    for k in ("CODEX_SANDBOX", "CODEX_MODEL", "CODEX_EFFORT", "CODEX_HOME", "AGENT_SEAT", "RIMFLOW_SEAT",
              "RM_CLEANSE_STATUS_DIR", "RM_DETACHED_POOL", "RM_OWNER_HOLD_FILE", "HOME"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    if not os.environ.get("AGENT_SEAT"):
        env += ["--setenv", "AGENT_SEAT=BENCH", "--setenv", "RIMFLOW_SEAT=BENCH"]
    log = os.path.join(status_dir(), "fleet.log")
    return ["--user", "--collect", "-p", "WorkingDirectory=" + ROOT,     # control.launch_unit names the unit
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log] + env + [
            "--", "python3", os.path.abspath(__file__), "fleet"] + list(args) + ["--foreground"]


def fleet(mods, fx_for, runner="codex", parallel=4, model=None, effort=None, converge=False):
    st = Status(status_dir())
    keep = ("converged", "open-after-converge", "running") if converge else (
        "reviewed", "refused-after-second-look", "running")
    for m in mods:     # a running line may be another invocation's live mod: its owner rewrites it, not this queue
        if (st.read()["mods"].get(m) or {}).get("state") not in keep:
            st.set(m, "queued", "")

    def one(mod):
        fx = fx_for(mod)
        try:
            with mod_lock(mod):
                return _one(mod, fx)
        except Busy as e:
            fx.log(mod, "skipped: %s" % e)
            return mod, "busy"

    def _one(mod, fx):
        clone = None
        try:
            clone = fx.clone(mod)
            out = os.path.join(clone, rel_out(mod))
            if converge and latest_verdict(out)[0]:
                return mod, converge_mod(mod, fx, clone=clone)["state"]
            if done(clone, mod):
                prev = _dict(_json_file(os.path.join(out, "review.json")))
                state = "reviewed" if prev.get("applyable") is True else (
                    "refused-after-second-look" if prev else "blocked")
                fx.status(mod, state, "already done (resumed): %s" % (rel_out(mod)))
                return mod, state
            refs, _ = check_dir(out)
            has = os.path.exists(os.path.join(out, "result.json"))
            author, a_model, a_effort = runner, model, effort
            if not has or refs:
                rec = run_mod(mod, fx, runner=runner, model=model, effort=effort)
                if rec["state"] != "proposed":
                    return mod, rec["state"]
            else:      # resuming a proposal written earlier: its own author answers the review, whoever runs now
                ran = _dict(_json_file(os.path.join(out, "run.json")))
                if ran.get("runner") in ("codex", "claude"):
                    author, a_model, a_effort = ran["runner"], ran.get("model"), ran.get("effort")
            rec = review_mod(mod, fx, author=author, author_model=a_model, effort=a_effort, clone=clone)
            if converge and rec["state"] in ("reviewed", "refused-after-second-look"):
                return mod, converge_mod(mod, fx, clone=clone)["state"]
            return mod, rec["state"]
        except Exception as e:      # noqa: BLE001  one mod's crash is its own line, never the fleet's end
            import traceback
            fx.log(mod, "crashed: %s" % traceback.format_exc())
            fx.status(mod, "blocked", "the launcher crashed: %s: %s" % (type(e).__name__, e))
            return mod, "blocked"
        finally:
            if clone:
                fx.log(mod, "clone %s" % fx.release(clone))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        res = list(ex.map(one, mods))
    print("fleet done: %s" % ", ".join("%s %s" % r for r in res), flush=True)
    return res


# ------------------------------------------------------------------------------------------------ apply (dry run)
# item RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS. apply_plan works out what applying a converged proposal
# would write into its concept folder and refuses what must not be applied; it writes nothing. Writing it is
# RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED; the owner's plan check is cleanse_plan.py.

APPLY_ANSWERS = ("WOULD_WRITE", "NOTHING_TO_APPLY", "REFUSED", "COULD_NOT_LOOK")
APPLY_EXIT = {"WOULD_WRITE": 0, "NOTHING_TO_APPLY": 3, "REFUSED": 1, "COULD_NOT_LOOK": 4}
NEXT_BEGIN, NEXT_END = "<!-- cleanse:next_version begin -->", "<!-- cleanse:next_version end -->"
APPLY_BLOCK = ("Designer Cleanse applied: Design Version 0.1.0 is the cleansed tree (cleanse/ digest %s). The concept "
               "is held until the Designer is scheduled on it again (designer_stage.py unblock).")
# what an apply reads beside cleanse/: the concept's files the stage reader and the plan read
APPLY_CONCEPT_FILES = ("tree.json", "sheet.md", "stage.json", "record.json", "scenes.json", "floor.json", "exam.json",
                       "later_version.md", os.path.join("version", "VERSION.json"))


def _apply_out(answer, cause="", path="", files=None, changed=(), detail=""):
    return {"answer": answer, "cause": cause, "path": path, "files": files or {}, "changed": sorted(changed),
            "detail": detail}


def _apply_read(path):
    """-> text, or None when absent. OSError (a parent that denies search included) and bad UTF-8 raise: a file that is
    there but cannot be read is never treated as absent."""
    try:
        os.lstat(path)
    except FileNotFoundError:
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _semver(v):
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", v) if isinstance(v, str) else None
    return tuple(int(x) for x in m.groups()) if m else None


def _dump(doc):
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def _his_words(sheet):
    """The old sheet's `## his words` section above its `## does`, verbatim (the owner's words never leave with a
    rewrite), or ""."""
    head = re.split(r"^## does[ \t]*$", sheet or "", maxsplit=1, flags=re.M)[0]
    m = re.search(r"^## his words[ \t]*\n.*?(?=^## |\Z)", head, re.M | re.S)
    return m.group(0).rstrip() if m else ""


def apply_plan(repo, mod):
    """-> {answer: WOULD_WRITE | NOTHING_TO_APPLY | REFUSED | COULD_NOT_LOOK, cause, path, files {relpath under
    design/concepts/<mod>/: full text}, changed [the files that differ from disk]}. Writes nothing; the same inputs give
    the same files. Order: reads, then PYRELANDS, NO_PROPOSAL, ZERO_KEPT, CHECK_FAILED, CONVERGE_MISSING, CONVERGE_EMPTY,
    NOT_CONVERGED, STALE_CONVERGENCE, RESULT_NOT_APPLYABLE, DESIGNER_RUN_OPEN, VERSION_DOWNGRADE (and BAD_MOD,
    VERSION_INVALID, STAGE_INVALID, LATER_VERSION_MARKERS: inputs the plan cannot build on)."""
    import designer_stage as DS
    if not isinstance(mod, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]*", mod):
        return _apply_out("REFUSED", "BAD_MOD")
    concept = os.path.join(os.path.abspath(repo), "design", "concepts", mod)
    out = os.path.join(concept, "cleanse")
    # 1. reads: every input that exists is read now, so "cannot read" is never mistaken for "absent" or "changed"
    text = {}
    names = [os.path.join("cleanse", n) for n in FILES + ("converge.json", "review.json", "review_attempt.json",
                                                         "fixes.json")] + list(APPLY_CONCEPT_FILES)
    for rel in names:
        p = os.path.join(concept, rel)
        try:
            text[rel] = _apply_read(p)
        except (OSError, UnicodeDecodeError) as e:
            return _apply_out("COULD_NOT_LOOK", "UNREADABLE", p + " (%s)" % type(e).__name__)
    try:
        have_out = os.path.isdir(out) and os.listdir(out) is not None
    except OSError as e:
        return _apply_out("COULD_NOT_LOOK", "UNREADABLE", out + " (%s)" % type(e).__name__)
    parsed = {}
    for rel in ("tree.json", "stage.json", os.path.join("version", "VERSION.json")):
        if text[rel] is not None:
            doc = _json_text(text[rel])
            if not isinstance(doc, dict) or (rel == "tree.json" and not isinstance(doc.get("leaves", []), list)):
                return _apply_out("COULD_NOT_LOOK", "UNPARSED", os.path.join(concept, rel))     # old bars unseeable
            parsed[rel] = doc
    # 2. refusals, in order
    if mod.casefold() == "pyrelands":
        return _apply_out("REFUSED", "PYRELANDS")
    if not have_out or text[os.path.join("cleanse", "result.json")] is None:
        return _apply_out("REFUSED", "NO_PROPOSAL")
    census = _json_text(text[os.path.join("cleanse", "census.json")])
    listed = census.get("rows") if isinstance(census, dict) else census     # both forms check_dir reads
    rows = [r for r in listed if isinstance(r, dict)] if isinstance(listed, list) else []
    kept = [r for r in rows if r.get("fate") in KEPT]
    if isinstance(listed, list) and not kept:
        return _apply_out("REFUSED", "ZERO_KEPT")
    refs, _stats = check_dir(out)
    if refs:
        return _apply_out("REFUSED", "CHECK_FAILED", detail="check_dir refuses: %s" % ", ".join(sorted({r["rule"] for r in refs})))
    raw = text[os.path.join("cleanse", "converge.json")]
    if raw is None:
        return _apply_out("REFUSED", "CONVERGE_MISSING")
    cv = _json_text(raw)
    if not raw.strip() or cv == {}:
        return _apply_out("REFUSED", "CONVERGE_EMPTY")
    if not isinstance(cv, dict) or cv.get("applyable") is not True or cv.get("open") != []:
        return _apply_out("REFUSED", "NOT_CONVERGED")
    digest = proposal_digest(out)
    if cv.get("digest") != digest:
        return _apply_out("REFUSED", "STALE_CONVERGENCE")
    result = _json_text(text[os.path.join("cleanse", "result.json")])
    if not isinstance(result, dict) or result.get("applyable") is not True:
        return _apply_out("REFUSED", "RESULT_NOT_APPLYABLE")
    stage = parsed.get("stage.json")
    if stage is not None and stage.get("running") is not None:
        return _apply_out("REFUSED", "DESIGNER_RUN_OPEN")
    vrel = DS.VERSION_FILE
    ver = parsed.get(vrel)
    if ver is not None and ver.get("version") is not None:
        sv = _semver(ver.get("version"))
        if sv is None:
            return _apply_out("REFUSED", "VERSION_INVALID", os.path.join(concept, vrel))
        if sv > (0, 1, 0):
            return _apply_out("REFUSED", "VERSION_DOWNGRADE")
    if stage is not None and not (stage.get("stage") in DS.STAGES and isinstance(stage.get("budget"), dict)):
        return _apply_out("REFUSED", "STAGE_INVALID", os.path.join(concept, "stage.json"))
    # 3. the plan
    old_tree = parsed.get("tree.json")
    if old_tree is None:
        old_ids = []
    else:
        old_ids = _old_bars(out)        # a retry of the applied proposal reads its record of the tree it mapped
    bdoc = _json_text(text[os.path.join("cleanse", "bars.json")])
    bars = _dicts(bdoc.get("bars"))
    whole = bdoc.get("whole") if not _blank(bdoc.get("whole")) else next(b["id"] for b in bars if b.get("whole") is True)
    tree = {k: old_tree[k] for k in ("schema_version", "authored_by", "root_ref", "root_state", "root_hash", "floor",
                                     "exam_waived", "waived", "advisory") if old_tree and k in old_tree}
    tree.update(subject=mod, kind="mod", coverage=None, design_version="0.1.0", signature=result.get("signature"),
                whole=whole, capabilities=kept, leaves=[dict(b, experience=b.get("says")) for b in bars],
                checks=_dicts(bdoc.get("checks")), rules=_dicts(bdoc.get("rules")),
                meetings=_dicts(bdoc.get("meetings")),
                cleanse={"digest": digest, "old_leaf_ids": old_ids, "old_bars": bdoc.get("old_bars") or {}})
    files = {"tree.json": _dump(tree)}
    sheet = ["# %s" % mod, ""]
    words = _his_words(text["sheet.md"])
    if words:
        sheet += [words, ""]
    sheet += ["## does", ""] + ["- [leaf:%s] %s" % (b.get("id"), " ".join(str(b.get("says") or "").split())) for b in bars]
    sheet += ["", "## kept capabilities", ""] + ["- %s: %s" % (r.get("id"), " ".join(str(r.get("what") or "").split()))
                                                 for r in kept]
    definition = (text[os.path.join("cleanse", "definition.md")] or "").strip()
    if definition:
        sheet += ["", "## definition", "", definition]
    files["sheet.md"] = "\n".join(sheet).rstrip() + "\n"
    why = APPLY_BLOCK % digest[:12]
    if stage is None:
        # designer_stage.init's shape (init writes; this plans), born blocked; no timestamps, so a re-plan is equal
        st = {"schema": 1, "mod": mod, "item": None, "aliases": [], "stage": 0, "status": "blocked",
              "budget": {"cap": DS.DEFAULT_CAP, "reserve": DS.DEFAULT_RESERVE, "spent": 0, "charges": []},
              "running": None, "results": [], "recovery": [], "history": []}
    else:
        st = json.loads(json.dumps(stage))
    prev = st.get("cleanse") if isinstance(st.get("cleanse"), dict) else {}
    was = prev.get("was") if prev.get("digest") == digest else (stage or {}).get("status")   # a re-plan keeps it
    st.update(status="blocked", running=None, blocked_on=why, cleanse={"digest": digest, "was": was})
    files["stage.json"] = _dump(st)
    if (ver is not None and ver.get("proposal_digest") == digest and ver.get("version") == "0.1.0"
            and ver.get("mod") == mod and "replaces" in ver):
        nv = ver                                                      # a re-plan: this digest's record stands
    else:
        nv = {"mod": mod, "version": "0.1.0", "state": "open", "proposal_digest": digest, "replaces": ver,
              "why": "Designer Cleanse of the owner's approved plan (design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md)"}
    files[vrel] = _dump(nv)
    moved = [r for r in rows if r.get("fate") == "next_version"]
    prior = text["later_version.md"] or ""
    if prior.count(NEXT_BEGIN) != prior.count(NEXT_END) or prior.count(NEXT_BEGIN) > 1 or (
            NEXT_BEGIN in prior and prior.index(NEXT_END) < prior.index(NEXT_BEGIN)):
        return _apply_out("REFUSED", "LATER_VERSION_MARKERS", os.path.join(concept, "later_version.md"),
                          detail="later_version.md holds %d begin and %d end markers; the plan owns exactly one section"
                          % (prior.count(NEXT_BEGIN), prior.count(NEXT_END)))
    if moved:
        sec = [NEXT_BEGIN, "## Design Version 0.2.0: moved by the Designer Cleanse (digest %s)" % digest[:12], ""]
        sec += ["- %s (0.2.0): %s\n  %s" % (r.get("id"), " ".join(str(r.get("what") or "").split()),
                                             " ".join(str(r.get("why") or "").split())) for r in moved]
        sec += [NEXT_END]
        if NEXT_BEGIN in prior:
            head, rest = prior.split(NEXT_BEGIN, 1)
            later = head + "\n".join(sec) + rest.split(NEXT_END, 1)[1]
        else:
            later = prior + ("\n" if prior and not prior.endswith("\n") else "") + ("\n" if prior else "") + "\n".join(sec) + "\n"
        files["later_version.md"] = later
    changed = [rel for rel, t in files.items() if text.get(rel) != t]
    if not changed:
        return _apply_out("NOTHING_TO_APPLY", files=files)
    return _apply_out("WOULD_WRITE", files=files, changed=changed)


WRITE_EXIT = {"WROTE": 0, "NOTHING_TO_APPLY": 3, "REFUSED": 1, "COULD_NOT_LOOK": 4, "WRITE_FAILED": 5}
APPLY_FAULT = None      # the CLI's test seam: fault(phase, rel), phases "locked", "install", "cleanup"


def _write_out(answer, cause="", path="", files=(), cleanup_failed=(), detail=""):
    return {"answer": answer, "cause": cause, "path": path, "files": list(files), "cleanup_failed": list(cleanup_failed),
            "detail": detail}


APPLY_BEFORE_PLAN = ("BAD_MOD", "PYRELANDS", "NO_PROPOSAL")     # what the plan check cannot speak to: these decide first


def _gate(repo, mod):
    """apply_plan's reads and identity (COULD_NOT_LOOK, BAD_MOD, PYRELANDS, NO_PROPOSAL), then the owner's plan
    (cleanse_plan.plan_check: an edited or unreviewed proposal is NOT_APPROVED, the truer answer than the check or
    converge refusal it also earns), then apply_plan's other answers. -> (None, the plan) to write, or (the answer, None)."""
    p = apply_plan(repo, mod)
    stop = _write_out(p["answer"], p["cause"], p["path"], detail=p.get("detail", ""))
    if p["answer"] == "COULD_NOT_LOOK" or p["cause"] in APPLY_BEFORE_PLAN:
        return stop, None
    import cleanse_plan
    c = cleanse_plan.plan_check(repo, mod)
    if c["answer"] == "COULD_NOT_LOOK":
        return _write_out("COULD_NOT_LOOK", "PLAN_UNREADABLE", c["path"]), None
    if c["answer"] != "APPROVED":
        return _write_out("REFUSED", "NOT_APPROVED", c["path"], detail="the owner's plan reads %s%s" % (
            c["answer"], " (%s)" % ", ".join(c["ids"]) if c["ids"] else "")), None
    if p["answer"] != "WOULD_WRITE":
        return stop, None
    return None, p


def apply_write(repo, mod, fault=None):
    """Install apply_plan's files into design/concepts/<mod>/, all or none (RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_
    UNTOUCHED). -> {answer: WROTE | NOTHING_TO_APPLY | REFUSED | COULD_NOT_LOOK | WRITE_FAILED, cause, path, files (the
    relpaths written), cleanup_failed}. Order: _gate (the plan's reads and identity, the owner's plan, the plan's other
    answers); then, under an exclusive flock on the concept folder, the plan is made again (a Designer run opened
    meanwhile refuses) and each file goes in by a temp file and os.replace, its prior bytes and mode kept in memory. A
    failure before the last file is in rolls every file back (WRITE_FAILED); a cleanup failure after it is WROTE with
    cleanup_failed. Touches nothing outside the concept folder: not the owner's hold, the plan, or the mod's source."""
    fault = fault or (lambda phase, rel: None)
    early, _ = _gate(repo, mod)
    if early:
        return early
    concept = os.path.join(os.path.abspath(repo), "design", "concepts", mod)
    try:
        fd = os.open(concept, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        return _write_out("COULD_NOT_LOOK", "UNREADABLE", concept + " (%s)" % type(e).__name__)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return _write_out("REFUSED", "BUSY", concept, detail="another apply holds the concept folder")
        prior, made_dirs, done, strays = {}, [], [], []
        try:
            fault("locked", None)
            early, plan = _gate(repo, mod)      # under the lock: what changed while it waited decides
            if early:
                return early
            files = plan["files"]
            unsafe = _unsafe_paths(concept, files)
            if unsafe:
                return _write_out("REFUSED", "UNSAFE_PATH", concept, detail="not a plain file or folder inside the "
                                  "concept folder: %s" % ", ".join(unsafe))
            for rel in sorted(files):
                dst = os.path.join(concept, rel)
                if os.path.lexists(dst):
                    st = os.lstat(dst)
                    if not stat.S_ISREG(st.st_mode):
                        raise OSError("%s is not a regular file" % rel)
                    with open(dst, "rb") as f:
                        prior[rel] = (f.read(), stat.S_IMODE(st.st_mode))
                else:
                    prior[rel] = None
            for rel in sorted(files):
                fault("install", rel)
                dst = os.path.join(concept, rel)
                parent = os.path.dirname(dst)
                if not os.path.lexists(parent):
                    made_dirs.append(parent)        # before the mkdir: an interrupt between the two still removes it
                    os.mkdir(parent)
                if _unsafe_paths(concept, {rel: None}):     # again at the moment of writing, not only before
                    raise OSError("%s: a link or a non-plain file appeared on its path during the install" % rel)
                done.append(rel)        # before the replace: an interrupt between the two still rolls this file back
                _replace(dst, files[rel].encode("utf-8"), prior[rel][1] if prior[rel] else None, strays)
        except BaseException as e:  # noqa: BLE001  any failure, an interrupt included, before the last file is in
            unrestored = _rollback(concept, prior, done, made_dirs, strays)
            if not isinstance(e, Exception):
                raise           # an interrupt still stops the process, after the rollback
            if unrestored:
                return _write_out("WRITE_FAILED", "ROLLBACK_INCOMPLETE", concept, done,
                                  detail="%s: %s; NOT restored: %s" % (type(e).__name__, e, "; ".join(unrestored)))
            return _write_out("WRITE_FAILED", "ROLLED_BACK", concept, (),
                              detail="%s: %s; every file restored to its prior bytes and mode" % (type(e).__name__, e))
        cleanup = []
        try:
            fault("cleanup", None)
            for d in sorted({os.path.dirname(os.path.join(concept, rel)) for rel in files}):
                dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
        except Exception as e:      # noqa: BLE001  every file is in: the write stands, the cleanup is reported apart
            cleanup.append("%s: %s" % (type(e).__name__, e))
        return _write_out("WROTE", files=sorted(files), cleanup_failed=cleanup)
    finally:
        os.close(fd)


def _unsafe_paths(concept, files):
    """-> the planned relpaths whose file or any folder on the way is a link or not a plain file/folder (a write through
    one would land outside the concept folder)."""
    bad = []
    for rel in sorted(files):
        p = concept
        parts = rel.split(os.sep)
        for i, part in enumerate(parts):
            p = os.path.join(p, part)
            try:
                st = os.lstat(p)
            except FileNotFoundError:
                break
            if not (stat.S_ISREG(st.st_mode) if i == len(parts) - 1 else stat.S_ISDIR(st.st_mode)):
                bad.append(rel)
                break
    return bad


def _replace(dst, data, mode, strays=None):
    """data into dst by a temp file beside it and os.replace; mode kept when given. A temp file it could not remove is
    added to `strays`."""
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(prefix=".apply-", dir=os.path.dirname(dst))
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, dst)
    except BaseException:
        try:
            if tmp is not None:
                os.unlink(tmp)
        except OSError:
            if strays is not None:
                strays.append(tmp)
        raise


def _rollback(concept, prior, done, made_dirs, strays):
    """Each installed file back to its prior bytes and mode (or gone, when it was new); new folders removed; temp files
    removed. -> what could not be restored (a stray temp file included)."""
    bad = []
    for rel in reversed(done):
        dst = os.path.join(concept, rel)
        try:
            if prior[rel] is None:
                with contextlib.suppress(FileNotFoundError):    # marked done, interrupted before its replace
                    os.unlink(dst)
            else:
                _replace(dst, prior[rel][0], prior[rel][1], strays)
        except OSError as e:
            bad.append("%s (%s)" % (rel, e))
    for tmp in list(strays):
        try:
            os.unlink(tmp)
            strays.remove(tmp)
        except OSError as e:
            bad.append("%s (temp file left: %s)" % (os.path.relpath(tmp, concept), e))
    for d in reversed(made_dirs):
        try:
            with contextlib.suppress(FileNotFoundError):       # marked, interrupted before its mkdir
                os.rmdir(d)
        except OSError as e:
            bad.append("%s (%s)" % (os.path.relpath(d, concept), e))
    return bad


def apply_cli(repo, mod, write=False):
    """`apply <Mod> [--write]`: per-file lines, then `APPLY <Mod> <ANSWER> [CAUSE]` (--write: `APPLY <Mod> CLEANUP_FAILED
    <detail>` first when the cleanup failed). -> exit code."""
    if write:
        w = apply_write(repo, mod, fault=APPLY_FAULT)
        for rel in w["files"]:
            print("WROTE %s" % rel)
        for c in w["cleanup_failed"]:
            print("APPLY %s CLEANUP_FAILED %s" % (mod, c))
        if w["answer"] == "WROTE":
            print("APPLY %s WROTE %d files" % (mod, len(w["files"])))
        else:
            print(("APPLY %s %s %s %s" % (mod, w["answer"], w["cause"], w["detail"] or w["path"])).rstrip())
        return WRITE_EXIT[w["answer"]]
    r = apply_plan(repo, mod)
    for rel in sorted(r["files"]):
        print("%s %s" % ("WOULD_WRITE" if rel in r["changed"] else "SAME", rel))
    if r["answer"] == "WOULD_WRITE":
        print("APPLY %s WOULD_WRITE %d files" % (mod, len(r["changed"])))
    else:
        print(("APPLY %s %s %s %s" % (mod, r["answer"], r["cause"], r["path"] or r["detail"])).rstrip())
    return APPLY_EXIT[r["answer"]]


def _main_one(o):
    """run or review of one mod, its lock held by main."""
    if o.cmd == "run":
        rec = run_mod(o.mod, Effects(), runner=o.runner, model=o.model, effort=o.effort)
        print(json.dumps({k: rec.get(k) for k in ("mod", "state", "why", "sha", "seconds", "stray")}, indent=1))
        return 0 if rec["state"] in ("proposed", "blocked") else 1
    if o.cmd == "converge":
        rec = converge_mod(o.mod, Effects())
        print(json.dumps({k: rec.get(k) for k in ("mod", "state", "why", "sha")}, indent=1))
        return 0 if rec["state"] in ("converged", "open-after-converge") else 1
    rec = review_mod(o.mod, Effects(), author=o.author, author_model=o.model, effort=o.effort)
    print(json.dumps({k: rec.get(k) for k in ("mod", "state", "why", "sha")}, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("case").add_argument("mod")
    rp = sub.add_parser("run")
    rp.add_argument("mod")
    rp.add_argument("--runner", choices=("codex", "claude"), default="codex")
    rp.add_argument("--model")
    rp.add_argument("--effort")
    sub.add_parser("check").add_argument("dir")
    vp = sub.add_parser("review")
    vp.add_argument("mod")
    vp.add_argument("--author", choices=("codex", "claude"), default="codex")
    vp.add_argument("--model", help="the author's model for its fix run")
    vp.add_argument("--effort")
    fp = sub.add_parser("fleet")
    fp.add_argument("--all-biomes-but", nargs="+", default=["Pyrelands"])
    fp.add_argument("--parallel", type=int, default=4)
    fp.add_argument("--only", default="")
    fp.add_argument("--runner", choices=("codex", "claude"), default="codex")
    fp.add_argument("--model")
    fp.add_argument("--effort")
    fp.add_argument("--foreground", action="store_true", help="run here (the detached unit runs this)")
    fp.add_argument("--converge", action="store_true", help="the converge round on every reviewed mod")
    sub.add_parser("converge").add_argument("mod")
    ap_ = sub.add_parser("apply")
    ap_.add_argument("mod")
    ap_.add_argument("--repo", default=ROOT)
    ap_.add_argument("--write", action="store_true", help="install the plan, all or none, once the owner's plan approves it")
    sub.add_parser("gather")
    sub.add_parser("status")
    o = ap.parse_args(argv)
    if o.cmd == "apply":
        return apply_cli(o.repo, o.mod, o.write)
    if o.cmd == "case":
        print(case_text(ROOT, o.mod), end="")
        return 0
    if o.cmd == "check":
        refs, text = check_report(o.dir)
        print(text)
        return 1 if refs else 0
    if o.cmd == "gather":
        text, tot = gather(ROOT)
        print("%s (%s)" % (os.path.join(status_dir(), "ALL_BIOMES.md"), ", ".join("%s %s" % kv for kv in tot.items())))
        return 0
    if o.cmd in ("run", "review", "converge"):
        try:
            with mod_lock(o.mod):
                return _main_one(o)
        except Busy as e:
            print("refused: %s" % e)
            return 1
    if o.cmd == "fleet":
        only = [x for x in o.only.split(",") if x.strip()]
        mods = fleet_order(ROOT, but=o.all_biomes_but, only=only)
        if o.converge:     # fewest open records first: the most likely to converge take the quota first
            mods.sort(key=lambda m: len(open_records(os.path.join(ROOT, rel_out(m))) or []))
        if not o.foreground:
            args = ["--all-biomes-but"] + o.all_biomes_but + ["--parallel", str(o.parallel), "--runner", o.runner]
            args += ["--converge"] if o.converge else []
            args += (["--only", o.only] if only else []) + (["--model", o.model] if o.model else []) + (
                ["--effort", o.effort] if o.effort else [])
            unit = "rm-designer-cleanse-fleet-%s" % time.strftime("%Y%m%d-%H%M%S")
            os.makedirs(status_dir(), exist_ok=True)
            import control as C     # the one admission point: a held or switched-off mod refuses the fleet
            r = C.launch_unit(fleet_unit_argv(args, unit), {"family": "designer_cleanse", "unit": unit, "mods": mods},
                              capture_output=True, text=True, timeout=60)
            print((r.stdout + r.stderr).strip())
            print("fleet of %d (%s) in unit %s; status: %s" % (len(mods), ", ".join(mods), unit,
                                                                os.path.join(status_dir(), "status.md")))
            return r.returncode
        st = Status(status_dir())
        fleet(mods, lambda m: Effects(st), runner=o.runner, parallel=o.parallel, model=o.model, effort=o.effort,
              converge=o.converge)
        return 0
    if o.cmd == "status":
        print(_read(os.path.join(status_dir(), "status.md")) or "no status yet: %s" % status_dir(), end="")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
