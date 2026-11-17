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
  designer_cleanse.py fleet --all-biomes-but Pyrelands [--parallel 4] [--only A,B] [--runner codex]
        detached in its own systemd user unit (--foreground runs it here); resumable; status in
        D:\\ClaudeWork\\rimmandrake\\designer_cleanse\\status.json and status.md, per-mod logs beside them.
  designer_cleanse.py status

The owner's hold (mod_owner_hold.json) stays on builds; `run` refuses a held mod unless its hold row carries his words
for a design-only pass (mod_owner_hold.py allow-design). Nothing here launches a build, a chain or a Dispatch run.
Selftest: selftest_designer_cleanse.py.
"""
import argparse
import concurrent.futures
import contextlib
import datetime
import fcntl
import json
import os
import random
import re
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bar_rule            # noqa: E402
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
}
LAUNCHER_HEADS = ("stranger", "self_check")     # written by this program from its own readings, never by the reviewer


def rel_out(mod):
    return "design/concepts/%s/cleanse/" % mod


def status_dir():
    return os.environ.get("RM_CLEANSE_STATUS_DIR") or "/mnt/d/ClaudeWork/rimmandrake/designer_cleanse"


def _read(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return default


def _blank(v):
    return not (isinstance(v, str) and v.strip())


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def _headings(text):
    return [h.strip() for h in re.findall(r"^##\s+(.+?)\s*$", text or "", re.M)]


def page_words(text):
    """Words on his pages, the reviewer's still-refused block excluded (it is the reviewer's, not the run's)."""
    return len(re.findall(r"\S+", (text or "").split(STILL_REFUSED_HEAD)[0]))


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
        text = _read(os.path.join(out, name))
        if text is None:
            return None
        try:
            return json.loads(text)
        except ValueError as e:
            refuse("files", name, "%s does not parse: %s" % (name, e), "%s is valid JSON" % name)
            return None

    result = load_json("result.json")
    blocked = isinstance(result, dict) and result.get("outcome") == "blocked"
    want = BLOCKED_FILES if blocked else FILES
    for name in want:
        t = _read(os.path.join(out, name))
        if t is None or not t.strip():
            refuse("files", name, "%s is %s" % (name, "missing" if t is None else "empty"),
                   "%s present in %s with its contents (the brief's file table)" % (name, out))
    stats["files"] = "%d of %d present" % (sum(1 for n in want if (_read(os.path.join(out, n)) or "").strip()), len(want))
    pages = _read(os.path.join(out, "owner_pages.md")) or ""
    words = page_words(pages)
    stats["page_words"], stats["page_limit"] = words, PAGE_WORDS
    if words > PAGE_WORDS:
        refuse("owner_pages_length", "owner_pages.md", "his pages run %d words; the limit is %d (two pages)"
               % (words, PAGE_WORDS), "owner_pages.md at most %d words; detail moves to the other files" % PAGE_WORDS)
    if not isinstance(result, dict):
        if result is not None:
            refuse("counts", "result.json", "result.json is not an object", "result.json as the brief's table shapes it")
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
    if census is not None and not rows:
        refuse("census_fate", "census.json", "the census holds no rows", "census.json {\"rows\": [...]}, one per capability")
    stats["census_rows"] = len(rows)
    ticket_sections = dict(_sections(tickets_md))
    for i, r in enumerate(rows):
        r = r if isinstance(r, dict) else {}
        where = "census.json row %d (%s)" % (i + 1, r.get("id") or "no id")
        if r.get("fate") not in FATES:
            refuse("census_fate", where, "fate %r is not one of %s" % (r.get("fate"), ", ".join(FATES)),
                   "fate one of %s" % ", ".join(FATES))
        for k in ("id", "what", "why"):
            if _blank(r.get(k)):
                refuse("census_row", where, "%s is blank" % k, "%s filled (the brief's census columns)" % k)
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
            elif not re.search(r"acceptance test\s*:", sec, re.I):
                refuse("ticket", "tickets.md %s" % t, "the switch-off ticket has no acceptance test",
                       "the ticket says `Acceptance test: ...` (or `Acceptance test: none, <reason>`)")

    doc = bars_doc if isinstance(bars_doc, dict) else {}
    bars = [b for b in doc.get("bars") or [] if isinstance(b, dict)]
    stats["bars"] = len(bars)
    if bars_doc is not None and not bars:
        refuse("bar_part", "bars.json", "bars.json holds no bars", "bars.json {\"bars\": [...]} with the whole bar")
    worst_num = None
    for b in bars:
        where = "bar %s" % (b.get("id") or "no id")
        _bar_parts(b, where, refuse)
        texts = [("says", b.get("says"))] + [("accept", x) for x in _strs(b.get("accept"))] + \
                [("reject", x) for x in _strs(b.get("reject"))] + \
                [("figurative accept", (f or {}).get("accept")) for f in (b.get("meant") or {}).get("figurative") or []
                 if isinstance(f, dict)]
        for part, text in texts:
            hit = bar_number(text if isinstance(text, str) else "")
            if hit:
                worst_num = worst_num or "%s %s: %r" % (where, part, hit)
                refuse("bar_number", "%s %s" % (where, part), "%r pins a number, a count or every field (%r)"
                       % (text, hit), "the comparison a player sees instead; numbers go in range or sees, or a check")
    stats["bar_numbers"] = worst_num or "none"
    ids = [b.get("id") for b in bars]
    if len(set(ids)) != len(ids) or any(_blank(i) for i in ids):
        refuse("bar_part", "bars.json", "bar ids are blank or repeated: %s" % ids, "every bar a unique id")
    wholes = set(x for x in [doc.get("whole")] if not _blank(x)) | {b.get("id") for b in bars if b.get("whole") is True}
    if len(wholes) != 1 or not wholes <= set(ids):
        refuse("whole", "bars.json whole", "%s whole bars (%s)%s" % (len(wholes), sorted(wholes),
               "" if wholes <= set(ids) else ", not all of them bars"),
               "exactly one whole bar: bars.json `whole` names one bar id, and no other bar says whole")
    _meetings(doc, bars, models, refuse, stats)
    old = _old_bars(out)
    mapped = doc.get("old_bars") if isinstance(doc.get("old_bars"), dict) else {}
    stats["old_bars"] = "%d mapped of %d in tree.json" % (len([o for o in old if o in mapped]), len(old))
    for o in old:
        m = mapped.get(o)
        if not isinstance(m, dict) or m.get("to") not in OLD_TO or _blank(m.get("why")):
            refuse("old_bar", "old_bars %s" % o, "old bar %s is %s" % (o, "unmapped" if m is None else
                   "mapped without a `to` from %s or a why" % ", ".join(OLD_TO)),
                   "old_bars[%r] = {\"to\": one of %s, \"as\": the new id, \"why\": ...}" % (o, ", ".join(OLD_TO)))
        elif m.get("to") in ("kept", "merged", "check", "rule") and _blank(m.get("as")):
            refuse("old_bar", "old_bars %s" % o, "old bar %s went to %s without naming as what" % (o, m.get("to")),
                   "`as` names the bar, check or rule it became")
    extra = sorted(set(mapped) - set(old))
    if extra:
        refuse("old_bar", "old_bars", "old_bars maps ids the concept's tree.json does not hold: %s" % extra,
               "old_bars maps exactly the ids of tree.json's leaves (empty when there is no tree)")
    _counts(result, rows, bars, doc, models, tickets, pages, mapped, refuse, stats)
    return refs, stats


def _strs(v):
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


def _sections(md):
    """-> [(heading, text under it)] for every `## ` heading."""
    parts = re.split(r"^##\s+(.+?)\s*$", md or "", flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def _ticket_section(sections, tid):
    for h, body in sections.items():
        if re.match(r"%s(?![\w-])" % re.escape(tid), h):
            return body
    return None


def _bar_parts(b, where, refuse):
    miss = []
    meant = b.get("meant") if isinstance(b.get("meant"), dict) else None
    rng = b.get("range") if isinstance(b.get("range"), dict) else None
    sees = b.get("sees") if isinstance(b.get("sees"), dict) else None
    if _blank(b.get("says")):
        miss.append("says")
    if meant is None or _blank(meant.get("source")):
        miss.append("meant.source (his words by event, a standing ruling, or `delegated: from what`)")
    fig = (meant or {}).get("figurative")
    if not isinstance(fig, list) or any(not isinstance(f, dict) or any(_blank(f.get(k)) for k in
                                         ("word", "stands_for", "accept")) for f in fig):
        miss.append("meant.figurative (a list; each {word, stands_for, accept}; [] when no word is figurative)")
    acc, rej = _strs(b.get("accept")), _strs(b.get("reject"))
    if not [x for x in acc if x.strip()]:
        miss.append("accept")
    if not [x for x in rej if x.strip()]:
        miss.append("reject")
    lazy = b.get("lazy")
    if _blank(lazy):
        miss.append("lazy")
    elif not re.match(r"none\s*:\s*\S", lazy.strip(), re.I) and _norm(lazy) not in {_norm(x) for x in rej}:
        miss.append("lazy (the laziest build, word for word one of the reject pictures; or `none: <why the words are "
                    "tight>`)")
    if rng is None or _blank(rng.get("varies")) or _blank(rng.get("left_out")):
        miss.append("range {varies, left_out}")
    for k in ("instrument", "start", "on", "control"):
        if sees is None or _blank(sees.get(k)):
            miss.append("sees.%s" % k)
    if b.get("live_only") is True and _blank((sees or {}).get("live_only_why")) and _blank(b.get("live_only_why")):
        miss.append("sees.live_only_why (a live-only bar says why nothing cheaper can see it)")
    if not isinstance(b.get("live_only"), bool):
        miss.append("live_only (true or false)")
    if not [t for t in _strs(b.get("touches")) if t.strip()]:
        miss.append("touches")
    for m in miss:
        refuse("bar_part", where, "%s is missing or blank" % m, "%s filled as the brief's bar parts say" % m.split(" (")[0])


def _meetings(doc, bars, models, refuse, stats):
    touchers = {}
    for b in bars:
        for t in _strs(b.get("touches")):
            touchers.setdefault(_norm(t), set()).add(b.get("id"))
    for r in doc.get("rules") or []:
        if isinstance(r, dict):
            for t in _strs(r.get("touches")):
                touchers.setdefault(_norm(t), set()).add(r.get("id"))
    meets = [m for m in doc.get("meetings") or [] if isinstance(m, dict)]
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
        elif h in ("argued", "measured") and _blank(m.get("why")):
            refuse("meeting", where, "an %s meeting with no argument or citation in why" % h,
                   "why holds the argument (argued) or the reading it cites (measured)")
        elif h == "unknown":
            mod = _norm(m.get("model"))
            if not mod or not any(mod == x or x.startswith(mod) or mod in x for x in models_n):
                refuse("unknown_model", where, "an unknown meeting names model %r, which models.md has no ## heading for"
                       % m.get("model"), "model names a `## ` heading of models.md that would settle it")


def _old_bars(out):
    tree = os.path.join(os.path.dirname(os.path.normpath(out)), "tree.json")
    try:
        with open(tree, encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return []
    leaves = doc.get("leaves") if isinstance(doc, dict) else None
    return [x["id"] for x in leaves or [] if isinstance(x, dict) and isinstance(x.get("id"), str)]


def _counts(result, rows, bars, doc, models, tickets, pages, mapped, refuse, stats):
    fates = [r.get("fate") for r in rows if isinstance(r, dict)]
    questions = re.findall(r"^\s*(?:[-*]\s*)?\**Q\d+\.", pages, re.M)
    have = {"capabilities": len(rows), "kept": sum(1 for f in fates if f in KEPT),
            "next_version": fates.count("next_version"), "recommend_retire": fates.count("recommend_retire"),
            "old_bars": len(mapped), "bars": len(bars), "live_only_bars": sum(1 for b in bars if b.get("live_only") is True),
            "checks": len([c for c in doc.get("checks") or [] if isinstance(c, dict)]),
            "rules": len([r for r in doc.get("rules") or [] if isinstance(r, dict)]),
            "unknown_pairs": sum(1 for m in doc.get("meetings") or [] if isinstance(m, dict)
                                 and m.get("holds_together") == "unknown"),
            "models": len(models), "tickets": len(tickets), "questions": len(questions)}
    stats["questions"], stats["question_limit"] = len(questions), QUESTIONS
    counts = result.get("counts") if isinstance(result.get("counts"), dict) else {}
    for k in COUNT_KEYS:
        if counts.get(k) != have[k]:
            refuse("counts", "result.json counts.%s" % k, "counts.%s reads %r; the files hold %d" % (k, counts.get(k), have[k]),
                   "counts.%s = %d (%s)" % (k, have[k], _COUNT_HOW[k]))
    if len(questions) > QUESTIONS:
        refuse("counts", "owner_pages.md", "%d questions; at most %d" % (len(questions), QUESTIONS),
               "at most %d questions, each a line starting Q<n>." % QUESTIONS)
    for k in ("capabilities", "bars", "live_only_bars"):
        if not re.search(r"(?<![\w.])%d(?!\w|[.,]\d)" % have[k], pages.split(STILL_REFUSED_HEAD)[0]):
            refuse("counts", "owner_pages.md", "his pages do not state the %s count %d" % (k.replace("_", "-"), have[k]),
                   "page one states %s as the digits %d, the number in result.json" % (k.replace("_", "-"), have[k]))
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
  "needed_by", "ticket"}]}. A needed_by row names what needs it in "needed_by" and gives the deletion argument in "why".
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
- owner_pages.md: at most %d words; questions are lines starting "Q1.", "Q2." (at most %d); page one states the
  capabilities, bars and live-only bars counts as digits, the same numbers as result.json.
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
                                   ((r.stdout or "") + (r.stderr or "")).strip()[-600:]))
            self.log(mod, "reused and synced %s" % dest)
        else:
            env = dict(os.environ, RM_SCRATCH_ROOT=pool_root(), RM_SEAT="clones")
            r = subprocess.run(["python3", os.path.join(UTILS, "scratch_clone.py"), "clone", "designer cleanse " + mod,
                                "--name", "cleanse-" + mod, "--fetch", "--sparse"] + dirs,
                               env=env, capture_output=True, text=True, timeout=540, stdin=subprocess.DEVNULL)
            if r.returncode or not os.path.isdir(os.path.join(dest, ".git")):
                raise RuntimeError("scratch_clone failed (exit %d): %s" % (r.returncode,
                                   ((r.stdout or "") + (r.stderr or "")).strip()[-600:]))
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
        read-only reviewer. No spend cap is passed and none is told: the run is never told its spend."""
        os.makedirs(os.path.dirname(base), exist_ok=True)
        bounded = os.path.join(cwd, "src", "RimMandrake", "Utils", "claude_bounded.sh")
        if not os.path.exists(bounded):
            bounded = os.path.join(UTILS, "claude_bounded.sh")
        cmd = [bounded, "-p", "--model", model or "opus", "--output-format", "json"]
        cmd += ["--tools", tools, "--allowedTools", tools] if tools else ["--dangerously-skip-permissions"]
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
            return {"runner": "claude", "is_error": True, "result": (raw + (_read(base + ".err") or ""))[-2000:],
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

    def publish(self, cwd, paths, msg):
        _git(cwd, "add", "--", *paths, timeout=300)
        r = subprocess.run(["./publish", "-m", msg] + list(paths), cwd=cwd, capture_output=True, text=True,
                           timeout=540, stdin=subprocess.DEVNULL)
        said = (r.stdout or "") + (r.stderr or "")
        m = re.search(r"PUBLISHED ([0-9a-f]{7,40})", said)
        if r.returncode or not m:
            raise RuntimeError("./publish exit %d: %s" % (r.returncode, said.strip()[-800:]))
        return m.group(1)

    def sleep(self, s):
        time.sleep(s)

    def release(self, clone):
        """Remove the finished mod's clone when nothing in it is unpushed, untracked or in use; otherwise keep it.
        Not relentless_disk.park: the Relentless warm shelf hands its clones to builders that need a full checkout,
        and this one is sparse (relentless.py removes a tracked-files-only tree rather than park it, for that reason)."""
        try:
            import shutil
            import scratch_clone as SC
            from pathlib import Path
            if SC.clone_unpushed(Path(clone), strict=True) or SC.clone_in_use(Path(clone)) or self.changed(clone):
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
        if (res or {}).get("is_error") and QUOTA.search(text):
            fx.log(mod, "the agent hit its quota (%s); waiting %d s and retrying" % (text[:160], QUOTA_WAIT_S))
            fx.status(mod, "running", "waiting for the %s quota" % runner)
            fx.sleep(QUOTA_WAIT_S)
            continue
        fx.log(mod, "%s run %d ended: %s" % (runner, n, "error: " + text[:200] if (res or {}).get("is_error") else "done"))
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
    result = json.loads(_read(os.path.join(out, "result.json")) or "null") if not [
        r for r in refs if r["where"] == "result.json" and r["rule"] == "files"] else None
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
           "agent_errors": [str(r.get("result"))[:400] for r in runs if (r or {}).get("is_error")]}
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


def review_prompt(repo, mod, items):
    e = entry(repo, mod)
    out = rel_out(mod)
    src = ["src/RimMandrake/%s/" % (e.get("source") or mod)]
    if os.path.isdir(os.path.join(repo, "design/concepts/%s" % mod)):
        src.append("design/concepts/%s/ (record.json, sheet.md, tree.json: the mod's earlier definition)" % mod)
    lore = [p for p in LORE if os.path.exists(os.path.join(repo, p))]
    heads = "\n".join("- %s: %s" % (k, v) for k, v in HEADS.items() if k not in LAUNCHER_HEADS)
    return """You are the fresh reviewer of one mod's cleansing proposal, the whole-mod check. You did not write it. You
read and refuse; you change no file and run nothing that writes. Read in this order.

## HIS WORDS (the owner's, before anything else)

%s

## SOURCE (the mod as built, and the world it lives in)

Source: %s
Rulings and lore: %s
The brief the author followed: %s (what a bar is, the fate of an extra, the file table).

## The pictures, blind (do this before you open the proposal)

For each bar below you see what it says and its pictures, shuffled and unlabelled. Sort each picture as `accept` (a
build the owner would take as this bar met) or `reject` (one he would refuse), as a cold reader would.

BLIND PICTURES:
%s
END BLIND PICTURES

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
 "blind_sort": [{"bar": "<id>", "n": <picture number>, "sorted": "accept" or "reject"}],
 "missed_capability": "...", "loop_or_three_way": "..."}
""" % (his_words(repo, mod), "; ".join(src), "; ".join(lore), BRIEF, json.dumps(items, indent=1, ensure_ascii=False),
       out, heads)


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
        r = r if isinstance(r, dict) else {}
        if r.get("head") not in HEADS or r.get("head") in LAUNCHER_HEADS:
            bad.append("refusal %d: head %r is not one of the spec's heads" % (i + 1, r.get("head")))
        for k in ("where", "evidence", "would_pass", "smallest_fix"):
            if _blank(r.get(k)):
                bad.append("refusal %d: %s is blank" % (i + 1, k))
    if not isinstance(doc.get("blind_sort"), list):
        bad.append("blind_sort is not a list")
    for k in ("missed_capability", "loop_or_three_way"):
        if _blank(doc.get(k)):
            bad.append("%s is blank (say what you found, or \"looked, none\")" % k)
    return bad


def score_blind(sort, truth):
    """-> (stranger rows, refusals): each picture's label beside the reviewer's sort; a bar with any picture sorted
    differently, or left unsorted, is a Stranger refusal (repair, as the brief's Stranger test says)."""
    got = {}
    for s in sort if isinstance(sort, list) else []:
        if isinstance(s, dict):
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


def _look(fx, mod, clone, rv_runner, rv_model, base, rng):
    """One look by the reviewer. -> the round's record."""
    out = os.path.join(clone, rel_out(mod))
    bars = [b for b in (json.loads(_read(os.path.join(out, "bars.json")) or "{}").get("bars") or []) if isinstance(b, dict)]
    items, truth = blind(bars, rng)
    prompt = review_prompt(clone, mod, items)
    kw = {"model": rv_model, "tools": "Read,Grep,Glob"} if rv_runner == "claude" else {"sandbox": "read-only"}
    doc, bad, res = None, None, None
    for attempt in (1, 2):      # a malformed review is asked once more, with what was wrong; nothing loops past that
        p = prompt if attempt == 1 else prompt + ("\n\nYour last answer could not be read as the record: %s. Answer "
                                                  "again with the one JSON object only.\n" % "; ".join(bad))
        res = _agent(fx, mod, rv_runner, clone, p, base + (".retry" if attempt == 2 else ""), **kw)
        doc = parse_review((res or {}).get("result"))
        bad = validate_review(doc)
        if not bad:
            break
    if bad:     # the reviewer's record is unreadable: no reading of the proposal, so no refusal of it
        fx.log(mod, "the reviewer's record is still unreadable after one retry: %s" % "; ".join(bad))
        return {"runner": rv_runner, "model": rv_model, "refusals": [], "reviewer_refusals": 0, "stranger": [],
                "missed_capability": None, "loop_or_three_way": None, "defects": bad, "usage": _usage(res)}
    rows, stranger = score_blind(doc.get("blind_sort"), truth)
    refusals = [r for r in doc.get("refusals") or [] if isinstance(r, dict)]
    return {"runner": rv_runner, "model": rv_model, "refusals": refusals + stranger, "reviewer_refusals": len(refusals),
            "stranger": rows, "missed_capability": (doc or {}).get("missed_capability"),
            "loop_or_three_way": (doc or {}).get("loop_or_three_way"), "defects": bad or [], "usage": _usage(res)}


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
    why = "the reviewer's record was unreadable twice (%s); the proposal is unreviewed" % "; ".join(rounds[-1]["defects"])[:300]
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
    clone = clone or fx.clone(mod)
    out_rel = rel_out(mod)
    out = os.path.join(clone, out_rel)
    refs, _ = check_dir(out)
    if refs or not os.path.exists(os.path.join(out, "result.json")):
        why = "no proposal that passes the self-check to review (%d refusals)" % len(refs)
        fx.status(mod, "blocked", why)
        return {"mod": mod, "state": "blocked", "why": why}
    result = json.loads(_read(os.path.join(out, "result.json")))
    if result.get("outcome") == "blocked":
        why = "the run is blocked: %s" % result.get("blocked_on")
        fx.status(mod, "blocked", why)
        return {"mod": mod, "state": "blocked", "why": why}
    rv_runner, rv_model = reviewer_for(author)
    fx.status(mod, "running", "review: %s %s first look" % (rv_runner, rv_model or ""))
    base = os.path.join(status_dir(), "runs", mod, time.strftime("%Y%m%d-%H%M%S") + ".review")
    rng = random.Random("%s %s" % (mod, time.time()))
    rounds = [_look(fx, mod, clone, rv_runner, rv_model, base + ".look1", rng)]
    if rounds[0]["defects"]:
        return _reviewer_failed(fx, mod, clone, rounds, t0)
    fix_rec = None
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
                   "error": str(res.get("result"))[:400] if (res or {}).get("is_error") else None}
        fx.status(mod, "running", "review: second look")
        rounds.append(_look(fx, mod, clone, rv_runner, rv_model, base + ".look2", rng))
        if rounds[-1]["defects"]:
            return _reviewer_failed(fx, mod, clone, rounds, t0, fix_rec)
    remaining = rounds[-1]["refusals"]
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
    result = json.loads(_read(os.path.join(out, "result.json")) or "{}")
    result["applyable"] = not remaining
    _write_json(os.path.join(out, "result.json"), result)
    state = "reviewed" if not remaining else "refused-after-second-look"
    review = {"mod": mod, "author": author, "reviewer": {"runner": rv_runner, "model": rv_model}, "rounds": rounds,
              "fix_run": fix_rec, "remaining": remaining, "applyable": not remaining,
              "seconds": int(time.time() - t0), "at": datetime.datetime.now().isoformat(timespec="seconds")}
    _write_json(os.path.join(out, "review.json"), review)
    paths = sorted(p for p in fx.changed(clone) if p.startswith(out_rel))
    sha = fx.publish(clone, paths, "designer cleanse: %s review (%s)" % (mod, state)) if paths else None
    why = "first look %d refusals%s; %s" % (len(rounds[0]["refusals"]), ", second look %d" % len(remaining)
                                           if len(rounds) > 1 else "", "applyable" if not remaining else "not applyable")
    fx.log(mod, "review %s: %s (published %s)" % (state, why, sha))
    fx.status(mod, state, why)
    return {"mod": mod, "state": state, "why": why, "sha": sha, "clone": clone, "review": review}


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


def done(repo, mod):
    """Resume: a mod whose proposal passes check and has a review (or says it is blocked) is skipped."""
    out = os.path.join(repo, rel_out(mod))
    if not os.path.exists(os.path.join(out, "result.json")):
        return False
    refs, stats = check_dir(out)
    return not refs and (os.path.exists(os.path.join(out, "review.json")) or stats.get("outcome") == "blocked")


def fleet_unit_argv(args, unit):
    """The detached unit: its own systemd user unit, no wall-time bound, surviving every window."""
    try:
        import detached_helper as DH
        path = DH.unit_path(os.environ.get("PATH"), DH.claude_bin())
    except Exception:       # noqa: BLE001
        path = os.environ.get("PATH", "/usr/bin:/bin")
    env = ["--setenv", "PATH=" + path]
    for k in ("CODEX_SANDBOX", "CODEX_MODEL", "CODEX_EFFORT", "CODEX_HOME", "AGENT_SEAT", "RIMFLOW_SEAT",
              "RM_CLEANSE_STATUS_DIR", "RM_DETACHED_POOL", "HOME"):
        if os.environ.get(k):
            env += ["--setenv", "%s=%s" % (k, os.environ[k])]
    if not os.environ.get("AGENT_SEAT"):
        env += ["--setenv", "AGENT_SEAT=BENCH", "--setenv", "RIMFLOW_SEAT=BENCH"]
    log = os.path.join(status_dir(), "fleet.log")
    return ["systemd-run", "--user", "--collect", "--unit", unit, "-p", "WorkingDirectory=" + ROOT,
            "-p", "StandardOutput=append:" + log, "-p", "StandardError=append:" + log] + env + [
            "python3", os.path.abspath(__file__), "fleet"] + list(args) + ["--foreground"]


def fleet(mods, fx_for, runner="codex", parallel=4, model=None, effort=None):
    st = Status(status_dir())
    for m in mods:
        if (st.read()["mods"].get(m) or {}).get("state") not in ("reviewed", "refused-after-second-look"):
            st.set(m, "queued", "")

    def one(mod):
        fx = fx_for(mod)
        clone = None
        try:
            clone = fx.clone(mod)
            if done(clone, mod):
                prev = json.loads(_read(os.path.join(clone, rel_out(mod), "review.json")) or "{}")
                state = "reviewed" if prev.get("applyable") else (
                    "refused-after-second-look" if prev else "blocked")
                fx.status(mod, state, "already done (resumed): %s" % (rel_out(mod)))
                return mod, state
            refs, _ = check_dir(os.path.join(clone, rel_out(mod)))
            has = os.path.exists(os.path.join(clone, rel_out(mod), "result.json"))
            if not has or refs:
                rec = run_mod(mod, fx, runner=runner, model=model, effort=effort)
                if rec["state"] != "proposed":
                    return mod, rec["state"]
            rec = review_mod(mod, fx, author=runner, author_model=model, effort=effort, clone=clone)
            return mod, rec["state"]
        except Exception as e:      # noqa: BLE001  one mod's crash is its own line, never the fleet's end
            import traceback
            fx.log(mod, "crashed: %s" % traceback.format_exc()[-1500:])
            fx.status(mod, "blocked", "the launcher crashed: %s: %s" % (type(e).__name__, e))
            return mod, "blocked"
        finally:
            if clone:
                fx.log(mod, "clone %s" % fx.release(clone))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        res = list(ex.map(one, mods))
    print("fleet done: %s" % ", ".join("%s %s" % r for r in res), flush=True)
    return res


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
    sub.add_parser("status")
    o = ap.parse_args(argv)
    if o.cmd == "case":
        print(case_text(ROOT, o.mod), end="")
        return 0
    if o.cmd == "check":
        refs, text = check_report(o.dir)
        print(text)
        return 1 if refs else 0
    if o.cmd == "run":
        rec = run_mod(o.mod, Effects(), runner=o.runner, model=o.model, effort=o.effort)
        print(json.dumps({k: rec.get(k) for k in ("mod", "state", "why", "sha", "seconds", "stray")}, indent=1))
        return 0 if rec["state"] in ("proposed", "blocked") else 1
    if o.cmd == "review":
        rec = review_mod(o.mod, Effects(), author=o.author, author_model=o.model, effort=o.effort)
        print(json.dumps({k: rec.get(k) for k in ("mod", "state", "why", "sha")}, indent=1))
        return 0
    if o.cmd == "fleet":
        only = [x for x in o.only.split(",") if x.strip()]
        mods = fleet_order(ROOT, but=o.all_biomes_but, only=only)
        if not o.foreground:
            args = ["--all-biomes-but"] + o.all_biomes_but + ["--parallel", str(o.parallel), "--runner", o.runner]
            args += (["--only", o.only] if only else []) + (["--model", o.model] if o.model else []) + (
                ["--effort", o.effort] if o.effort else [])
            unit = "rm-designer-cleanse-fleet-%s" % time.strftime("%Y%m%d-%H%M%S")
            os.makedirs(status_dir(), exist_ok=True)
            r = subprocess.run(fleet_unit_argv(args, unit), capture_output=True, text=True, timeout=60)
            print((r.stdout + r.stderr).strip())
            print("fleet of %d (%s) in unit %s; status: %s" % (len(mods), ", ".join(mods), unit,
                                                                os.path.join(status_dir(), "status.md")))
            return r.returncode
        st = Status(status_dir())
        fleet(mods, lambda m: Effects(st), runner=o.runner, parallel=o.parallel, model=o.model, effort=o.effort)
        return 0
    if o.cmd == "status":
        print(_read(os.path.join(status_dir(), "status.md")) or "no status yet: %s" % status_dir(), end="")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
