#!/usr/bin/env python3
"""RIMMANDRAKE_RETIRE_OLD_PIPELINE_REMNANTS_TEN_SLIPPED_INTO_LANES: the pipelines before the Maturation Pipeline stay gone.

The owner, 2026-11-18: "Nothing of that era should remain. No more collisions or confusion. I do not want to lose the
wisdom, just remove all future confusion please."

Fails on any tracked path, or any systemd user unit that is not masked, whose name belongs to a retired era (the
Relentless Pipeline, the Artisan/Ralph loops, the Whittle loops, the FOUNDRY seat, RimPulse, Fleet Watch, rimflow v3),
unless a row of the index's "Phase 2: renames" or "Kept on purpose" table allows it with a reason. An allow row that
matches nothing fails too (a stale row is its own confusion). The index is the one record of what went and where it
lived: design/RimMandrake/retired_eras_index_2026-11-18.md.

Answers, kept apart: rc 0 = looked, nothing left outside the allow-list; rc 1 = remnants found (each named);
rc 2 = could not look (git or the index unreadable). The unit check reads `systemctl --user`; where that cannot be read
the line says UNITS UNMEASURED with its cause and the path check still decides (a missing reading is not a pass of the
units, and is said so). Not scanned, on purpose (the owner's order keeps them): history (ledger shards, lessons,
closed-item prose, handoffs, evidence and code-review records, transcripts, Transient/) and mod content and its design
(src/ outside rimflow/, Utils/ and bridgetools/; design/Jawa, design/concepts, design/RimStarWars, design/RimUtinni),
where "foundry" or "pulse" are lore and feature words. Probes first: the checker must see a planted remnant before its verdict on the tree counts.

Text too (RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS, 2026-11-19): the path check above read green
while rm-builder.md told every builder "In the Relentless Pipeline (relentless.py) you fill a place", because it never
read a file. Now every instruction file (CLAUDE.md, agent definitions, roles, SKILL.md files, seat files, the standing
rulings) must say, on the line, that a retired era or deleted module it names is past; a record file (design doc, skill
reference, lesson, fact) may instead open with the HISTORY head that Utils/era_history_mark.py writes. The rule is
rimflow/era_text.py. Watched red on the pre-fix tree: 2011 era text lines (evidence:
D:\ClaudeWork\rimmandrake\conductor\era_finish_20261119\gate_prefix_run.txt).

Retired roles too (RIMMANDRAKE_RETIRE_INNOVATOR_ROLE_HE_FORGOT_IT_WAS_THERE): the owner, 2026-11-23, "Role is retired."
RIMMANDRAKE_REMOVE_RETIRED_V3_ROLES_FROM_ACTIVE_RULES_STILL_LISTED, the same day: "Those are old v3 roles we retired!"
(Producer and Auditor; the Arbiter and the Setter went before them). Watched red on that item's parent: 92 ROLE lines.
A role of RETIRED_ROLES fails on a machinery path named for it, on its word in a file that could launch or count it
(ROLE_FILES), and on a line of a live instruction file that names it without "retired" on that line. The idea list
design/RimMandrake/innovations.md is not the role.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
INDEX = os.path.join("design", "RimMandrake", "retired_eras_index_2026-11-18.md")
ALLOW_HEADINGS = ("## Phase 2: renames", "## Kept on purpose")

# Era words anywhere in a path, in the scopes below.
ERA = re.compile(r"relentless|artisan|whittle|ralph|rimpulse|fleet[ _-]?watch|rimflow[ _-]?v3|process_model_v2_v3", re.I)
# Words too common to match everywhere: only in machinery scopes, and only in these shapes.
MACHINERY_ONLY = re.compile(r"foundry|(^|/)pulse(/|$)|(^|/)rm-pulse\.", re.I)
MACHINERY = ("src/RimMandrake/rimflow/", "src/RimMandrake/Utils/", ".claude/", "skills/", "infrastructure/agents/",
             "infrastructure/whittle_claude/", "design/RimMandrake/", "design/specs/", "design/plans/", "tickets/",
             "ralph/", "whittle/")
# History and content: never era machinery, never deleted by this item (ledger shards, lessons, closed-item prose,
# handoffs, evidence and review records, transcripts, mod content and its design).
EXEMPT = ("infrastructure/state/ledger/", "infrastructure/state/lessons/", "infrastructure/state/items/closed/",
          "infrastructure/state/handoffs/", "infrastructure/state/evidence/", "infrastructure/state/code_review/",
          "conversations/", "Transient/", "design/Jawa/", "design/concepts/", "design/RimStarWars/",
          "design/RimUtinni/", "src/RimStarWars/", "src/RimUtinni/")
MOD_SRC = re.compile(r"^src/RimMandrake/(?!rimflow/|Utils/|bridgetools/)")


def era_path(p):
    """True when a tracked path names a retired era (outside the history and content scopes)."""
    if p.startswith(EXEMPT) or MOD_SRC.match(p):
        return False
    if ERA.search(p):
        return True
    toplevel = "/" not in p
    return bool((p.startswith(MACHINERY) or toplevel) and MACHINERY_ONLY.search(p))


def era_unit(name):
    return bool(ERA.search(name) or re.match(r"rm-pulse\.", name) or re.search(r"foundry", name, re.I))


MASKED = ("masked", "masked-runtime")

# --- Retired roles: name -> whose word. A role that comes back needs its owner's word and its entry here removed.
RETIRED_ROLES = {"Innovator": "the owner, 2026-11-23", "Producer": "the owner, 2026-11-23", "Auditor": "the owner, 2026-11-23",
                 "Artist": "the owner by card, 2026-11-23",
                 "Arbiter": "CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED",
                 "Setter": "RIMMANDRAKE_RETIRE_SETTER_ARBITER_SEAMS_EVERY_LAUNCH_REFUSED"}
COMMON_WORDS = ("Producer", "Auditor", "Artist", "Arbiter", "Setter")   # plain English in lower case ("a pipe producer")
NOT_THE_ROLE = (("skills/telemetry/SKILL.md", "Producer writes JSONL"),)    # any program that writes a series
ROLE_LIVE_TOO = ("src/RimMandrake/Utils/findings_judge_prompt.md", "src/RimMandrake/Utils/findings_judge_friday.md")
ROLE_PATHS = ("src/", ".claude/", "skills/", "infrastructure/agents/")
SCHEDULE = "src/RimMandrake/rimflow/dispatcher_schedule.json"
ROLE_FILES = (SCHEDULE, "src/RimMandrake/Utils/ops_watch_rules.json", "src/RimMandrake/rimflow/live_baseline.txt")


def role_rx(name, text=False):
    """text: a live instruction line, where a COMMON_WORDS name counts only capitalised."""
    return re.compile(r"\b%ss?\b" % re.escape(name),      # "_" is a word character: an id INNOVATOR_X is not the role
                      0 if text and name in COMMON_WORDS else re.I)


def check_roles(paths, files, live):
    """-> remnants of RETIRED_ROLES. paths: tracked paths; files: {ROLE_FILES path: text}; live: [(path, text)] of the
    live instruction files."""
    out = []
    for name in RETIRED_ROLES:
        rx = role_rx(name)
        out += [f"role {name}: {p}" for p in paths
                if p.startswith(ROLE_PATHS) and re.search(name, os.path.basename(p), re.I)
                and (name not in COMMON_WORDS or p.startswith(("src/RimMandrake/rimflow/", "src/RimMandrake/Utils/", ".claude/",
                                                               "infrastructure/agents/")))]    # mod content: plain words
        for p, text in files.items():
            if p == SCHEDULE:
                sch = json.loads(text)
                out += [f"role {name}: a row of roles in {p}" for r in sch.get("roles") or [] if rx.search(str(r.get("name")))]
                out += [f"role {name}: named in golive.roles of {p}"
                        for r in (sch.get("golive") or {}).get("roles") or [] if rx.search(str(r))]
            out += [f"role {name}: {p}:{n}" for n, ln in enumerate(text.splitlines(), 1) if rx.search(ln)]
        out += [f"role {name}: {p}:{n}: {ln.strip()[:160]}" for p, text in live
                for n, ln in enumerate(text.splitlines(), 1)
                if role_rx(name, True).search(ln) and not re.search(r"\bretired\b", ln, re.I)
                and not any(p == q and w in ln for q, w in NOT_THE_ROLE)]
    return out

# --- Text: the rule lives in era_text.py (shared with Utils/era_history_mark.py).
from era_text import HISTORY_LINE, HISTORY_MARK, check_text, mark_text, text_scope  # noqa: E402


def read_allow(text):
    """Allow rows from the index: [(glob, reason)]; None when the index has no allow table at all."""
    rows, inside, seen = [], False, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() in ALLOW_HEADINGS
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "path":
            seen = True      # a table's header row: an empty table is a table, a heading alone is not
            continue
        m = re.fullmatch(r"`([^`]+)`", cells[0]) if cells else None
        if not m:
            continue
        rows.append((m.group(1), cells[1] if len(cells) > 1 else ""))
    return rows if seen else None


def allowed(p, glob):
    return fnmatch.fnmatchcase(p, glob)


def check_tree(paths, units, allow):
    """-> (remnants, problems). paths: tracked paths; units: [(unit, state)] or None (unread); allow: rows."""
    problems = [f"allow row `{g}` has no reason" for g, why in allow if not why]
    remnants, used = [], set()
    for p in paths:
        if not era_path(p):
            continue
        hits = {g for g, _ in allow if allowed(p, g)}
        if not hits:
            remnants.append(p)
        used |= hits
    for name, state in units or ():
        if not era_unit(name) or state in MASKED:
            continue
        if state == "transient":     # a live run's systemd-run unit carries its item's name; it is not installed and ends with the run
            continue
        hits = {g for g, _ in allow if g == "unit:" + name}
        if not hits:
            remnants.append(f"unit:{name} ({state})")
        used |= hits
    if units is not None:
        problems += [f"allow row `{g}` matches nothing" for g, _ in allow if g not in used]
    else:
        problems += [f"allow row `{g}` matches nothing" for g, _ in allow if g not in used and not g.startswith("unit:")]
    return remnants, problems


def read_units():
    """[(unit, state)] from systemctl --user, or (None, cause)."""
    try:
        r = subprocess.run(["systemctl", "--user", "list-unit-files", "--no-legend", "--no-pager"],
                           capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"systemctl not runnable: {e}"
    if r.returncode != 0:
        return None, f"systemctl rc {r.returncode}: {r.stderr.strip()[:200]}"
    out = []
    for line in r.stdout.splitlines():
        f = line.split()
        if len(f) >= 2:
            out.append((f[0], f[1]))
    return out, ""      # rc 0 with no rows is a measured empty list, not "could not look"


def probes():
    """The checker must reject planted remnants and accept what the allow-list names."""
    fails = []

    def want(ok, what):
        print(("ok   " if ok else "FAIL ") + "probe: " + what)
        if not ok:
            fails.append(what)

    allow = [("src/RimMandrake/rimflow/relentless.py", "live, phase 2"), ("unit:rm-keep.timer", "kept")]
    r, p = check_tree(["src/RimMandrake/rimflow/relentless.py", "ralph/PROMPT.md"], [], allow[:1])
    want(r == ["ralph/PROMPT.md"] and not p, "a planted ralph/ file is a remnant; an allowed path is not")
    r, _ = check_tree(["skills/whittle/SKILL.md", "src/RimMandrake/Utils/pulse/pulse.py", "pulse",
                       "design/RimMandrake/rimflow_v3_x.md", ".claude/hooks/foundry_x.py",
                       "infrastructure/state/items/RELENTLESS_X.md"], [], [])
    want(len(r) == 6, f"six planted era paths are six remnants (got {len(r)})")
    r, _ = check_tree(["infrastructure/state/lessons/x-whittle.md", "infrastructure/state/ledger/events/x.jsonl",
                       "src/RimUtinni/UtinniPatches/Defs/RUT_FoundryFloor.xml", "src/RimMandrake/FlowWorks/pulse/x.py",
                       "src/RimMandrake/bridgetools/prove_flowworks_pulse.py", "conversations/relentless.md",
                       "design/Jawa/fauna/sprites/BMT_FoundryBeetle.png"], [], [])
    want(r == [], f"lessons, ledger, mod content and transcripts are not remnants (got {r})")
    r, _ = check_tree([], [("rm-relentless.timer", "enabled"), ("rm-artisan-now.timer", "masked"),
                           ("whittle-claude@.service", "static"), ("rm-pulse.service", "disabled")], [])
    want(r == ["unit:rm-relentless.timer (enabled)", "unit:whittle-claude@.service (static)",
               "unit:rm-pulse.service (disabled)"], f"an unmasked era unit is a remnant, a masked one is not (got {r})")
    r, _ = check_tree([], [("rm-detached-bench-rimmandrake-remove-relentless-now-page-c-1.service", "transient"),
                           ("claude-seat-BENCH-rm-detached-bench-remove-relentless-now-1.scope", "transient"),
                           ("rm-relentless.timer", "enabled")], [])
    want(r == ["unit:rm-relentless.timer (enabled)"],
         f"a live run's transient unit named for its item is not a remnant; an installed era unit is (got {r})")
    r, p = check_tree([], [("rm-keep.timer", "enabled")], [("unit:rm-keep.timer", "")])
    want(any("no reason" in x for x in p), "an allow row without a reason is a problem")
    _, p = check_tree(["src/RimMandrake/rimflow/cli.py"], [], allow[:1])
    want(any("matches nothing" in x for x in p), "a stale allow row is a problem")
    _, p = check_tree([], None, allow[1:])
    want(p == [], "with units unread, a unit allow row is not called stale")
    want(read_allow("# x\n## Other\n| `a` | b |\n") is None, "an index with no allow table reads as no table")
    want(read_allow("## Kept on purpose\nprose only\n") is None, "a heading with no table is no table")
    want(read_allow("## Kept on purpose\n| path | why |\n|---|---|\n") == [], "an empty table is an empty allow list")
    want(read_allow("## Kept on purpose\n| path | why |\n|---|---|\n| `a/**` | b |\n") == [("a/**", "b")],
         "an allow table row is read")
    want(read_allow("## Kept on purpose — rejected\n| path | why |\n| `ralph/**` | no |\n") is None,
         "a heading that only starts like an allow heading grants nothing")
    want(allowed("whittle/x/y", "whittle/**") and not allowed("whittlex/y", "whittle/**"), "a dir glob is a prefix")
    want(allowed("skills/a/whittle/x.py", "skills/*/whittle/**"), "a glob with a wildcard before /** matches")
    _, p = check_tree(["ralph/a.md"], [], [("ralph/**", "x"), ("ralph/a.md", "y")])
    want(p == [], f"two allow rows matching one path are both used (got {p})")
    r, _ = check_tree(["design/RimMandrake/Fleet Watch.md", "design/RimMandrake/rimflow v3.md"],
                      [("rm-foundry.service", "enabled"), ("rm-whittle.timer", "masked-runtime")], [])
    want(r == ["design/RimMandrake/Fleet Watch.md", "design/RimMandrake/rimflow v3.md", "unit:rm-foundry.service (enabled)"],
         f"spaced era names and a foundry unit are remnants; masked-runtime is masked (got {r})")
    # The text check (step-1 class): the pre-fix lines that sent a fresh agent to a deleted thing must be refused.
    bad = {".claude/agents/rm-builder.md": "In the Relentless Pipeline (`src/RimMandrake/rimflow/relentless.py`) you "
                                           "fill a place as a Relentless-style Builder from MandrakeWorkflows.",
           "infrastructure/agents/BUILD.md": "This seat's work moved to Relentless (`CLAUDE.md`, \"Relentless builds "
                                             "and accepts the work that needs building\") (owner's ruling, 2026-08-27).",
           "skills/live-debugging-proof-harness/SKILL.md": "tier. `hot_reload_defs` is not a speed path. "
                                                           "`relentless_live.py` refuses proof lines",
           "src/RimMandrake/rimflow/roles/designer_lock.md": "The Producer admits it. Relentless runs `gate` at the pool",
           "CLAUDE.md": "./bridge [conductor|foundry|free]                   his override"}
    for path, line in bad.items():
        want(len(check_text(path, "# t\n" + line + "\n")) == 1, f"the pre-fix line in {path} is refused")
    want(check_text(".claude/agents/rm-builder.md", HISTORY_LINE + "\n" + bad[".claude/agents/rm-builder.md"]) != [],
         "a HISTORY head does not excuse a file every agent is handed")
    want(check_text("design/RimMandrake/x_2026-10-01.md", "# t\n" + HISTORY_LINE + "\nRelentless runs the gate.\n") == [],
         "a record file with a HISTORY head passes")
    want(check_text("design/RimMandrake/x_2026-10-01.md", "# t\n\n\n\n\n" + HISTORY_LINE + "\nRelentless runs.\n") != [],
         "a HISTORY mark below the head is not a head")
    want(check_text("infrastructure/state/lessons/20261101T000000Z-BENCH-x.md", "Relentless reaps clones.\n") != [],
         "an unmarked lesson naming a retired era is refused")
    doc = "---\nname: x\n---\n# t\nRelentless runs the gate.\n"
    marked = mark_text("design/RimMandrake/x_2026-10-01.md", doc)
    want(marked is not None and marked.startswith("---\nname: x\n---\n> " + HISTORY_LINE) and
         check_text("design/RimMandrake/x_2026-10-01.md", marked) == [], "the marker heads a record after its front matter")
    want(mark_text("design/RimMandrake/x_2026-10-01.md", marked) is None, "a marked record is not marked twice")
    lesson = mark_text("infrastructure/state/lessons/20261101T000000Z-BENCH-x.md", "Relentless reaps clones.\nhome: x\n")
    want(lesson is not None and lesson.endswith("Relentless reaps clones.\nhome: x\n") and
         check_text("infrastructure/state/lessons/20261101T000000Z-BENCH-x.md", lesson) == [],
         "a lesson's first line takes the prefix and its footer is untouched")
    want(mark_text(".claude/agents/rm-builder.md", "Relentless runs.\n") is None, "the marker never touches a live file")
    want(text_scope("infrastructure/VALIDATION_LADDER.md") == "live" and
         text_scope("infrastructure/state/lessons/20261101T000000Z-BENCH-x.md") == "mark" and
         text_scope("skills/x/references/y.md") == "mark" and text_scope("skills/x/SKILL.md") == "live",
         "a live pattern is one directory level; a record pattern is its subtree")
    good = ["The Relentless Pipeline was retired 2026-11-13.", "the store `/home/mandrake/rm/relentless/store` stays",
            "env `RELENTLESS_ROOT` and item `RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES`",
            'his words: *"Yes relentless fixes itself first."* Any fault goes first.',
            "a trap the seat hit (FOUNDRY 2026-09-12, `RSW_Anooba`).", "> This is becoming a new Pipeline, better than Relentless",
            "shards `FOUNDRY.jsonl` and `RELENTLESS.jsonl` replay", "`git show f2ce40bac8:whittle/x.md`",
            "Measured 2026-09-01, FOUNDRY. `map_drop` on a map", "| 8 | Geonosian Foundry Hive | 4 |",
            "**Distinct-from Jawa:** few, elite, relentless vs. many, ragged", "whittle the list down to five"]
    for line in ["the relentless_live module refuses it", "the Relentless checker says yes", "rimpulse_x.md is read",
                 "a relentless pipeline run builds it"]:
        want(check_text("src/RimMandrake/rimflow/roles/x.md", line + "\n") != [], f"an era name is refused: {line[:40]}")
    want(check_text("src/RimMandrake/rimflow/roles/x.md", 'he said *"first line\nthen writes it out for Relentless.\n'
                    'end of it"* and so') == [], "the middle line of a quote spanning lines is his words")
    want(check_text("src/RimMandrake/rimflow/roles/x.md", 'an open *"quote\n' + "x\n" * 5 + "pad " * 600 +
                    '\nRelentless runs the gate.\n') != [], "an unclosed quote does not hide a line far below it")
    want(check_text("src/RimMandrake/rimflow/roles/auditor.md", "the week's Relentless `retire` decisions\n") != [],
         "the verb 'retire' is not a past marker")
    for line in good:
        want(check_text("src/RimMandrake/rimflow/roles/x.md", line + "\n") == [], f"a past or name-only line passes: {line[:40]}")
    want(check_text("src/RimMandrake/rimflow/x.py", "relentless.py runs\n") == [] and
         check_text("design/Jawa/x.md", "Foundry floor\n") == [], "code and lore are not read by the text check")
    # Retired roles: a planted return of each kind is refused; the idea list, an id and a "retired" line are not.
    clean = json.dumps({"golive": {"roles": ["Conductor"]}, "roles": [{"name": "Operations"}]}, indent=1)
    row = json.dumps({"golive": {"roles": []}, "roles": [{"name": "Innovator", "enabled": False}]}, indent=1)
    live = json.dumps({"golive": {"roles": ["Innovator"]}, "roles": []}, indent=1)
    want(any("a row of roles" in x for x in check_roles([], {SCHEDULE: row}, [])),
         "a planted return of the schedule row is a remnant, switched off too")
    want(any("golive.roles" in x for x in check_roles([], {SCHEDULE: live}, [])), "a return in golive.roles is a remnant")
    want(len(check_roles(["src/RimMandrake/rimflow/roles/innovator.md", ".claude/agents/rm-innovator.md",
                          "src/RimMandrake/Utils/systemd/rm-innovator.timer"], {}, [])) == 3,
         "a role file, an agent definition and a unit named for the role are remnants")
    want(len(check_roles([], {ROLE_FILES[1]: '  "roles": ["auditor", "innovator"],\n', ROLE_FILES[2]: "role=Innovator max_age=6d\n"},
                         [])) == 3, "a word-list entry and a live promise are remnants")
    want(len(check_roles([], {}, [("src/RimMandrake/rimflow/roles/x.md", "and the proposals of the Innovator\n")])) == 1,
         "a live instruction line that names the role as running is a remnant")
    want(check_roles(["design/RimMandrake/innovations.md", "infrastructure/state/items/closed/INNOVATOR_X.md"],
                     {SCHEDULE: clean, ROLE_FILES[2]: "role=Operations max_age=3d\n"},
                     [("CLAUDE.md", "The Innovator role was retired 2026-11-23.\nGet inventive. Innovate.\n`INNOVATOR_X_Y` is closed.\n")])
         == [], "the idea list, a closed item, an id and a line that says retired are not remnants")
    for name in ("Producer", "Auditor", "Artist"):
        back = json.dumps({"golive": {"roles": []}, "roles": [{"name": name, "enabled": False}]}, indent=1)
        want(any("a row of roles" in x for x in check_roles([], {SCHEDULE: back}, [])), f"a planted {name} schedule row is a remnant")
        want(check_roles([f"src/RimMandrake/rimflow/roles/{name.lower()}.md"], {}, []) != [], f"a returned {name} role file is a remnant")
        want(check_roles([], {}, [("CLAUDE.md", f"Hand it to the {name}.\n")]) != [], f"a rule line that sends work to the {name} is a remnant")
    want(check_roles([], {}, [("CLAUDE.md", "The Setter binds oracles.\n")]) != [], "a rule line with the Setter acting is a remnant")
    want(check_roles([], {}, [("skills/rimworld-layout-layers/SKILL.md", "a path from a producer to this consumer\n"),
                              ("skills/rimworld-debug-testing/SKILL.md", "in-game info card is the arbiter\n"), NOT_THE_ROLE[0]]) == [],
         "the plain English words are not the roles")
    return fails


def role_problems(paths):
    """-> (remnants, "") or (None, cause) when a file it must read could not be read."""
    files, live = {}, []
    try:
        for p in ROLE_FILES:
            with open(os.path.join(REPO, p), encoding="utf-8") as f:
                files[p] = f.read()
        for p in paths:
            if (text_scope(p) == "live" or p in ROLE_LIVE_TOO) and os.path.exists(os.path.join(REPO, p)):
                with open(os.path.join(REPO, p), encoding="utf-8") as f:
                    live.append((p, f.read()))
        return check_roles(paths, files, live), ""
    except (OSError, ValueError) as e:              # ValueError: not UTF-8, or the schedule is not JSON
        return None, str(e)


def text_problems(paths):
    """-> (problems, files read) over the tracked paths in text scope."""
    out, n = [], 0
    for p in paths:
        if text_scope(p) is None:
            continue
        try:
            with open(os.path.join(REPO, p), encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            continue                      # tracked but deleted in this working tree: nothing to read
        except (OSError, UnicodeError) as e:
            out.append(f"{p}: UNREADABLE ({e})")
            continue
        n += 1
        out += check_text(p, text)
    return out, n


# --- Retired things (the Conductor, 2026-11-23, design/specs/2026-11-23-retire-census/census.md Tables 1 and 2): paths,
# units and instruction words that stay gone. A thing that comes back needs a word that says so and its row here removed.
CENSUS = "the Conductor, 2026-11-23, retire census"
RETIRED_PATHS = (                     # fnmatch globs of tracked paths
    ".claude/hooks/bench_mode.py", ".claude/hooks/warn_unclosed_queue_item.py", "infrastructure/state/MODE",
    "src/RimMandrake/Utils/*agent_improve*", "infrastructure/state/agent_improve/*",    # the owner by card, 2026-11-23
    "final.md", "claude_sha.txt", ".bridge.eld", "GLOBAL_CLAUDE.md", "Fable_Review/*", "src/RimMandrake/rimflow/docs/*",
    "infrastructure/agents/POLICY.md", "infrastructure/agents/REP.md", "infrastructure/agents/CODEX_PROPOSAL_*",
    "infrastructure/REFRESH.md", "infrastructure/state/queue/HUMAN.md",
    "infrastructure/state/IDEOLOGY_REBUILD_TRIAL.md", "infrastructure/state/WORLDGEN_RUN.md",
    "infrastructure/state/REBOOT_HANDOFF_2026-09-02.md", "infrastructure/state/BENCH_HANDOFF.md",
    "infrastructure/state/WORLDPAINT_REHEARSAL.md", "infrastructure/state/LOAD_PROCEDURE.md",
    "infrastructure/state/haiku_census_2026-10-31.md", "infrastructure/state/live_proof_triage.tsv",
    "infrastructure/state/lightspeed_unmatched.tsv",
    "infrastructure/dashboards/*", "infrastructure/state/GOAL_SHEET.md", "src/RimMandrake/Utils/project_maturity_dashboard.py",
    "src/RimMandrake/Utils/ops_health.py", "src/RimMandrake/Utils/selftest_ops_health*.py",
    "src/RimMandrake/rimflow/priority_list.py", "infrastructure/state/priority_list.json",
    "src/RimMandrake/rimflow/selftest_idle_bringback.py", "src/RimMandrake/rimflow/selftest_focus_cap.py",
    "src/RimMandrake/Utils/prove_scratch_reap_refused_day.py", "src/RimMandrake/Utils/codebase_health_publish.py", "src/RimMandrake/Utils/codebase_health_artifact.tmpl.html",
)
RETIRED_UNITS = (                     # unit file names; a tracked copy in the one home, or an installed unmasked one
    "rm-agent-improve.timer", "rm-agent-improve.service",
    "steve-cpu-retest.timer", "steve-cpu-retest.service", "testq-sweep.timer", "testq-sweep.service",
    "rm-codebase-health.timer", "rm-codebase-health.service", "rm-dispatcher.timer", "rm-ops-watch.timer",
    "rm-ops-watch.service", "rm-restart-reconcile.timer", "rm-restart-reconcile.service",
)
RETIRED_WORDS = (                     # regexes refused on a live instruction line that does not say "retired"
    r"\bbench_mode\.py\b", r"infrastructure/state/MODE\b", r"\bGOAL_SHEET\.md\b", r"queue/HUMAN\.md\b", r"\bGLOBAL_CLAUDE\.md\b",
    r"\bproject_maturity_dashboard\b", r"\bcodebase_health_publish\b", r"\bagent_improve|rm-agent-improve\b",
    r"daily agent[- ]improvement", r"\b(testq-sweep|rm-codebase-health|steve-cpu-retest)\b",
    r"\bpriority_list\b", r"\bidle_bringback\b", r"\bbusy_waiting\b", r"\bfocus_cap\b", r"[Tt]hrottle:? (runway )?bands?\b", r"\bquick_cap_x\b",
    r"\bops_health\b", r"\b[Hh]ealth verdict\b(?!, its budgets)", r"\bV3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE\b", r"[Ii]nnovations list", r"\bRULINGS_BUILD_STATE_RECONCILER",

)
UNIT_HOME = "src/RimMandrake/Utils/systemd/"


def check_things(paths, units, live):
    """-> remnants of the retired things. units: [(unit, state)] or None (unread: the tracked copies still count)."""
    out = [f"thing: {p}" for p in paths for g in RETIRED_PATHS if fnmatch.fnmatchcase(p, g)]
    out += [f"unit: {UNIT_HOME}{u}" for u in RETIRED_UNITS if UNIT_HOME + u in set(paths)]
    out += [f"unit installed: {n} ({st})" for n, st in units or () if n in RETIRED_UNITS and st not in MASKED]
    return out + [f"words: {p}:{n}: {ln.strip()[:160]}" for p, text in live for n, ln in enumerate(text.splitlines(), 1)
                  if not re.search(r"\bretired\b", ln, re.I) and any(re.search(w, ln) for w in RETIRED_WORDS)]


def things_probes():
    """The checker must see a planted return of each kind, and pass a line that says retired."""
    fails = []
    for ok, what in (
            (check_things(["infrastructure/state/MODE"], [], []) == ["thing: infrastructure/state/MODE"], "a returned path is a remnant"),
            (check_things([], [], [("CLAUDE.md", "Read infrastructure/state/MODE first.")]) != [], "a rule line that uses a retired thing is a remnant"),
            (check_things(["infrastructure/state/MODELS.md"], None, [("CLAUDE.md", "The file infrastructure/state/MODE is retired.")]) == [],
             "a longer name and a line that says retired are not"),
            (all(check_things([UNIT_HOME + u], None, []) and check_things([], [(u, "disabled")], []) for u in RETIRED_UNITS)
             and all(check_things([], [(u, "masked")], []) == [] for u in RETIRED_UNITS), "a returned unit is a remnant, a masked one is not")):
        print(("ok   " if ok else "FAIL ") + "probe: " + what)
        fails += [] if ok else [what]
    return fails


def things_problems(paths, units):
    """-> remnants, reading the live instruction files; a file that cannot be read is named, never skipped."""
    live, bad = [], []
    for p in paths:
        if text_scope(p) == "live" and os.path.exists(os.path.join(REPO, p)):
            try:
                with open(os.path.join(REPO, p), encoding="utf-8") as f:
                    live.append((p, f.read()))
            except (OSError, UnicodeError) as e:
                bad.append(f"{p}: UNREADABLE ({e})")
    return bad + check_things(paths, units, live)


def main():
    fails = probes() + things_probes()
    if fails:
        print(f"FAIL: {len(fails)} probe(s) failed: the checker is not trustworthy, so its verdict on the tree does not count")
        return 1
    try:
        raw = subprocess.run(["git", "-C", REPO, "ls-files", "-z"], capture_output=True, check=True,
                             timeout=60).stdout
        paths = [os.fsdecode(x) for x in raw.split(b"\0") if x]   # -z: real paths, never git's quoted display form
    except (OSError, subprocess.SubprocessError) as e:
        print(f"COULD NOT LOOK: git ls-files failed: {e}")
        return 2
    if not paths:
        print("COULD NOT LOOK: git ls-files listed no paths, so this is not the repo (this file is tracked)")
        return 2
    try:
        with open(os.path.join(REPO, INDEX), encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeError) as e:
        print(f"COULD NOT LOOK: index unreadable ({INDEX}): {e}")
        return 2
    allow = read_allow(text)
    if allow is None:
        print(f"COULD NOT LOOK: {INDEX} has no '{ALLOW_HEADINGS[0]}' or '{ALLOW_HEADINGS[1]}' table")
        return 2
    units, cause = read_units()
    remnants, problems = check_tree(paths, units, allow)
    texts, nread = text_problems(paths)
    roles, cause_roles = role_problems(paths)
    if roles is None:
        print(f"COULD NOT LOOK: retired roles unread: {cause_roles}")
        return 2
    things = things_problems(paths, units)
    for x in things:
        print("RETIRED THING " + x)
    if things:
        print(f"FAIL: {len(things)} retired thing(s) back ({CENSUS}): delete it, or say 'retired' on the line")
        return 1
    for x in remnants:
        print("REMNANT " + x)
    for x in roles:
        print("ROLE " + x)
    for x in problems:
        print("PROBLEM " + x)
    for x in texts:
        print("ERA TEXT " + x)
    units_line = f"UNITS UNMEASURED: {cause}" if units is None else f"units read: {len(units)}"
    print(units_line + f"; text files read: {nread}")
    if nread == 0:
        print("COULD NOT LOOK: no instruction or record file was read, so the text check saw nothing")
        return 2
    if remnants or problems or texts or roles:
        print(f"FAIL: {len(remnants)} retired-era remnant(s), {len(roles)} retired-role remnant(s) (a ROLE line: delete what "
              f"names the role, or say 'retired' on the line; {RETIRED_ROLES}), {len(problems)} allow-list problem(s), {len(texts)} "
              f"era text line(s). A remnant: delete it (git is the archive; add its row to {INDEX}) or allow it "
              f"there with a reason. An era text line: say on the line that the thing is retired (or rewrite it to "
              f"what runs today); a design doc, skill reference, lesson or fact may instead open with "
              f"'{HISTORY_MARK}' (src/RimMandrake/Utils/era_history_mark.py adds it).")
        return 1
    print(f"PASS: no retired-era path outside the {len(allow)} allow rows in {INDEX}, and no era text line in "
          f"{nread} instruction and record files; retired roles gone: {', '.join(RETIRED_ROLES)}" + ("" if units is not None else "; units UNMEASURED"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
