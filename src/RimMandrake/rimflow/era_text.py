#!/usr/bin/env python3
"""era_text: which instruction and record files may name a retired era, and how (RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS).

Read by the era gate (selftest_retired_era_gone.py, at ./publish) and by the marker (Utils/era_history_mark.py). The owner,
2026-11-18: "Nothing of that era should remain. No more collisions or confusion. I do not want to lose the wisdom, just
remove all future confusion please." The rule and its reasons are in the block comment below; the index of what was
retired is design/RimMandrake/retired_eras_index_2026-11-18.md.
"""
import fnmatch
import re

INDEX = "design/RimMandrake/retired_eras_index_2026-11-18.md"

# --- Text: a live instruction may not send a reader to a retired thing (RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS).
# The path check above was green while rm-builder.md opened "In the Relentless Pipeline (relentless.py) you fill a
# place" and a skill told provers to satisfy relentless_live.py: it read names, never contents. So: every line that
# names a retired era or a deleted module must say on that line that it is past (retired, removed, was, history...).
# A line that is NAME ONLY (a kept path or env name, a ticket id, a ledger shard, an owner quote, a dated attribution)
# is read with those spans taken out. Files that are a record rather than an instruction (design docs, skill
# references, lessons, facts) may instead open with HISTORY_MARK; files every agent is handed (LIVE_ALWAYS) may not.
HISTORY_MARK = "HISTORY: retired era"
HISTORY_HEAD = 5                          # the mark counts only in a file's first lines
HISTORY_LINE = ("HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of "
                "Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer "
                "runs); the rest is as current as its own status says.")
LESSON_PREFIX = "HISTORY: retired era (see design/RimMandrake/retired_eras_index_2026-11-18.md; what it names no longer runs). "
# The era words as NAMES: capitalized, all caps, or glued to a path or module (relentless_live, whittle/, ralph-gss), or
# "relentless" before one of the tick's nouns. Plain English ("few, elite, relentless"; "whittle it down") is not one.
ERA_TEXT = re.compile(r"\b(?:Relentless|RELENTLESS|Artisan|ARTISAN|Whittle|WHITTLE|Ralph|RALPH)\b"
                      r"|\b(?:relentless|artisan|whittle|ralph)(?=[_./-]\w)"
                      r"|\brelentless (?:pipeline|tick|workers?|round|live|checker|store|pool|build|generation)\b"
                      r"|(?i:rimpulse|fleet ?watch|rimflow[ _-]?v3)|FOUNDRY|Foundry|\bfoundry\b")
PAST = re.compile(r"\b(retired|removed|deleted|gone|histor(y|ical)|formerly|former|old|was|were|used to|"
                  r"no longer|predates?|before the Maturation|replaced|renamed)\b", re.I)
NAME_ONLY = re.compile(
    r'\*".*?"\*|\*".*$|^[^"]*?"\*|"[^"\n]*"|“[^”]*”'     # an owner quote keeps his words (one may span lines)
    r"|\([^()]*\b20\d\d-\d\d-\d\d[^()]*\)"               # a dated attribution: (FOUNDRY 2026-09-12, ...)
    r"|`?git show [^`]*`?"                                # a git-archive pointer
    r"|[~/\w.-]*rm/relentless[\w./*-]*"                    # the kept store and pool paths
    r"|\b[A-Z0-9]+(?:_[A-Z0-9]+)+\b"                       # ticket ids and env names (RELENTLESS_ROOT)
    r"|\b\w+\.jsonl\b"                                     # ledger shards (FOUNDRY.jsonl)
    r"|\b20\d\d-\d\d-\d\d\b,?\s*FOUNDRY\b|\bFOUNDRY\b,?\s*20\d\d-\d\d-\d\d\b"  # "Measured 2026-09-01, FOUNDRY."
    r"|\bFoundry Hive\b"                                  # lore (the Geonosian faction), not the seat
    r"|\brelentless_states\b|\bfamily:relentless\b|\bralph/flowworks\b|\bpulse-deploy\b")
# Bounded, so an unclosed quote hides nothing far away; `: "` is how a dated owner quote opens ("The owner, 2026-10-27: "...").
QUOTE_SPAN = re.compile(r'\*"(?:(?!"\*).){0,2000}?"\*|(?<=: )"[^"]{0,2000}"', re.S)
LIVE_ALWAYS = ("CLAUDE.md", "PURPOSE.md", ".claude/agents/*.md", "src/RimMandrake/rimflow/roles/*.md",
               "infrastructure/agents/*.md", "infrastructure/*.md", "skills/*/SKILL.md", "design/RimMandrake/standing_rulings.md",
               "design/RimMandrake/delegation_policy.md", "design/RimMandrake/biome_rulings.md",
               "design/RimMandrake/debug_process.md", "design/RimMandrake/GIT_WORKFLOW.md",
               "infrastructure/GAME_STATE_WORKFLOW.md", "infrastructure/state/facts/instrument_traps.md",
               "infrastructure/state/facts/tool_traps.md", "design/specs/2026-11-13-maturation-pipeline.md")
MARKABLE = ("skills/*", "design/*", "infrastructure/state/lessons/*", "infrastructure/state/facts/*")
TEXT_SKIP = (INDEX, "design/RimMandrake/retired_loops_2026-11-13.md", "design/INDEX.md",
             "design/Jawa/*", "design/concepts/*", "design/RimStarWars/*", "design/RimUtinni/*")


def text_scope(p):
    """'live' (must be fixed line by line), 'mark' (a HISTORY head also answers), or None (not read)."""
    if not p.endswith(".md") or any(fnmatch.fnmatchcase(p, g) for g in TEXT_SKIP):
        return None
    if any(fnmatch.fnmatchcase(p, g) and p.count("/") == g.count("/") for g in LIVE_ALWAYS):
        return "live"             # one level only: fnmatch's * crosses "/", and infrastructure/*.md is not its subtree
    if any(fnmatch.fnmatchcase(p, g) for g in MARKABLE):
        return "mark"
    return None


def body_start(lines):
    """Index of the first line after YAML front matter (0 when there is none)."""
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            return end + 1
    return 0


def has_history_mark(text):
    lines = text.splitlines()
    at = body_start(lines)
    return any(HISTORY_MARK in ln for ln in lines[at:at + HISTORY_HEAD])


def era_lines(text):
    """[(lineno, line)] naming a retired era or deleted module with no past marker on the line."""
    out = []
    # His words quoted over several lines (*"... "*): blank them first, newlines kept, so a middle line reads as quote.
    unquoted = QUOTE_SPAN.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text).splitlines()
    for n, ln in enumerate(text.splitlines(), 1):
        if not ERA_TEXT.search(ln) or PAST.search(ln) or ln.lstrip().startswith(">"):
            continue                      # a past marker, or a blockquote (his words quoted whole)
        rest = NAME_ONLY.sub(" ", unquoted[n - 1] if n - 1 < len(unquoted) else ln)
        if ERA_TEXT.search(rest):
            out.append((n, ln))
    return out


def check_text(p, text):
    """-> [problem lines] for one tracked file; [] when it passes or is out of scope."""
    scope = text_scope(p)
    if scope is None:
        return []
    if scope == "mark" and has_history_mark(text):
        return []
    return [f"{p}:{n}: {ln.strip()[:160]}" for n, ln in era_lines(text)]  # cut-ok: terminal display


def mark_text(p, text):
    """-> text with the HISTORY head added (a record file only; None for any other scope, or when already marked).

    A design doc or skill reference gets HISTORY_LINE as a blockquote first line (after YAML front matter); a lesson
    gets LESSON_PREFIX on its first line, which lessons.py strips again when it compares first lines."""
    if text_scope(p) != "mark" or has_history_mark(text):
        return None
    if p.startswith("infrastructure/state/lessons/"):
        return LESSON_PREFIX + text
    lines = text.split("\n")
    at = body_start(lines)
    lines[at:at] = ["> " + HISTORY_LINE, ""]
    return "\n".join(lines)
