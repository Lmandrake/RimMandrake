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
units, and is said so). Probes first: the checker must see a planted remnant before its verdict on the tree counts.
"""
import fnmatch
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
INDEX = os.path.join("design", "RimMandrake", "retired_eras_index_2026-11-18.md")
ALLOW_HEADINGS = ("## Phase 2: renames", "## Kept on purpose")

# Era words anywhere in a path, in the scopes below.
ERA = re.compile(r"relentless|artisan|whittle|ralph|rimpulse|fleet[_-]?watch|rimflow_v3|process_model_v2_v3", re.I)
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
    return bool(ERA.search(name) or re.match(r"rm-pulse\.", name))


def read_allow(text):
    """Allow rows from the index: [(glob, reason)]; None when the index has no allow table at all."""
    rows, inside, seen = [], False, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip().startswith(ALLOW_HEADINGS)
            seen = seen or inside
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = re.fullmatch(r"`([^`]+)`", cells[0]) if cells else None
        if not m:
            continue
        rows.append((m.group(1), cells[1] if len(cells) > 1 else ""))
    return rows if seen else None


def allowed(p, glob):
    if glob.endswith("/**"):
        return p.startswith(glob[:-2])
    return fnmatch.fnmatchcase(p, glob)


def check_tree(paths, units, allow):
    """-> (remnants, problems). paths: tracked paths; units: [(unit, state)] or None (unread); allow: rows."""
    problems = [f"allow row `{g}` has no reason" for g, why in allow if not why]
    remnants, used = [], set()
    for p in paths:
        if not era_path(p):
            continue
        hit = next((g for g, _ in allow if allowed(p, g)), None)
        if hit is None:
            remnants.append(p)
        else:
            used.add(hit)
    for name, state in units or ():
        if not era_unit(name) or state == "masked":
            continue
        hit = next((g for g, _ in allow if g == "unit:" + name), None)
        if hit is None:
            remnants.append(f"unit:{name} ({state})")
        else:
            used.add(hit)
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
    if not out:
        return None, "systemctl listed no unit files at all"
    return out, ""


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
    r, p = check_tree([], [("rm-keep.timer", "enabled")], [("unit:rm-keep.timer", "")])
    want(any("no reason" in x for x in p), "an allow row without a reason is a problem")
    _, p = check_tree(["src/RimMandrake/rimflow/cli.py"], [], allow[:1])
    want(any("matches nothing" in x for x in p), "a stale allow row is a problem")
    _, p = check_tree([], None, allow[1:])
    want(p == [], "with units unread, a unit allow row is not called stale")
    want(read_allow("# x\n## Other\n| `a` | b |\n") is None, "an index with no allow table reads as no table")
    want(read_allow("## Kept on purpose\n| glob | why |\n|---|---|\n| `a/**` | b |\n") == [("a/**", "b")],
         "an allow table row is read")
    want(allowed("whittle/x/y", "whittle/**") and not allowed("whittlex/y", "whittle/**"), "a dir glob is a prefix")
    return fails


def main():
    fails = probes()
    if fails:
        print(f"FAIL: {len(fails)} probe(s): the checker cannot see a planted remnant; its verdict does not count")
        return 1
    try:
        paths = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True, check=True,
                               timeout=60).stdout.splitlines()
    except (OSError, subprocess.SubprocessError) as e:
        print(f"COULD NOT LOOK: git ls-files failed: {e}")
        return 2
    if not paths:
        print("COULD NOT LOOK: git ls-files listed no paths")
        return 2
    try:
        text = open(os.path.join(REPO, INDEX), encoding="utf-8").read()
    except OSError as e:
        print(f"COULD NOT LOOK: index unreadable ({INDEX}): {e}")
        return 2
    allow = read_allow(text)
    if allow is None:
        print(f"COULD NOT LOOK: {INDEX} has no '{ALLOW_HEADINGS[0]}' or '{ALLOW_HEADINGS[1]}' table")
        return 2
    units, cause = read_units()
    remnants, problems = check_tree(paths, units, allow)
    for x in remnants[:60]:
        print("REMNANT " + x)
    if len(remnants) > 60:
        print(f"REMNANT ... and {len(remnants) - 60} more")
    for x in problems:
        print("PROBLEM " + x)
    units_line = f"UNITS UNMEASURED: {cause}" if units is None else f"units read: {len(units)}"
    print(units_line)
    if remnants or problems:
        print(f"FAIL: {len(remnants)} retired-era remnant(s), {len(problems)} allow-list problem(s). Delete the "
              f"remnant (git is the archive; add its row to {INDEX}) or allow it there with a reason.")
        return 1
    print(f"PASS: no retired-era path outside the {len(allow)} allow rows in {INDEX}"
          + ("" if units is not None else "; units UNMEASURED"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
