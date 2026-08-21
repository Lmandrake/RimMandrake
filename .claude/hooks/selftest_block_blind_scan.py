#!/usr/bin/env python3
"""Selftest for block_blind_scan.py.

⭐ The failure mode this guards against is not "the hook misses a scan" — it is
**"the hook refuses something legitimate and gets switched off."** The analysis
said it plainly: enforcement without a cheap alternative is an obstacle, and
obstacles get routed around. So most of the cases below are ALLOW cases.

    python3 .claude/hooks/selftest_block_blind_scan.py
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "block_blind_scan.py")
# three levels: .claude/hooks/<file> -> .claude/hooks -> .claude -> the repo
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS, FAIL = [], []

DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
        "RimWorld by Ludeon Studios/DefDump")


def run(cmd, env=None, cwd=None):
    e = dict(os.environ)
    e.pop("MEASURE_ALLOW_SCAN", None)
    e["CLAUDE_PROJECT_DIR"] = REPO
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd},
                          **({"cwd": cwd} if cwd else {})}),
        capture_output=True, text=True, env=e)
    if not p.stdout.strip():
        return None
    return json.loads(p.stdout)


def case(name, fn):
    try:
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))


def denied(cmd, env=None, cwd=None):
    out = run(cmd, env, cwd)
    assert out is not None, "allowed, should have been denied: %s" % cmd
    return out["hookSpecificOutput"]["permissionDecisionReason"]


def allowed(cmd, env=None, cwd=None):
    out = run(cmd, env, cwd)
    assert out is None, "DENIED, should have been allowed: %s\n%s" % (
        cmd, out["hookSpecificOutput"]["permissionDecisionReason"][:300])


# --------------------------------------------------------------------------
# the three scans that actually produced wrong numbers
# --------------------------------------------------------------------------

def t_grep_on_a_savegame_is_refused():
    why = denied("grep -c Desert '/x/Saves/Ash.rws'")
    assert "compressed grid" in why, why
    assert "savemap.py" in why, why


def t_strings_on_an_assembly_is_refused():
    why = denied("strings -a -el src/x/1.6/Assemblies/JawaBench.dll | wc -l")
    assert "metadata" in why, why


def t_grep_on_the_def_dump_is_refused():
    why = denied("grep -o AbilityDef '%s/defs/ThingDef.json' | wc -l" % DUMP)
    assert "measure count" in why, why


def t_a_refusal_always_names_the_instrument_to_use_instead():
    for cmd in ("grep x '/a/b.rws'",
                "wc -l world/ASHKARR_WORLDMAP_tiles.csv",
                "grep -c Error /x/Player.log"):
        why = denied(cmd)
        assert "Use instead:" in why, (cmd, why)


# --------------------------------------------------------------------------
# ALLOW — the cases that decide whether anyone leaves this hook switched on
# --------------------------------------------------------------------------

def t_ordinary_greps_are_untouched():
    for cmd in ("grep -rn 'weaponTags' src/Jawa",
                "grep TODO README.md",
                "rg --files-with-matches Jawa src/",
                "wc -l infrastructure/state/V1.md",
                "cat CLAUDE.md | grep owner"):
        allowed(cmd)


def t_the_real_instruments_may_name_the_artifact():
    allowed("python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py count ThingDef")
    allowed("measure count ThingDef")
    allowed("python3 src/RimMandrake/Utils/rimbench/savemap.py '/x/Ash.rws'")
    allowed("python3 src/RimMandrake/Utils/harvest_log.py /x/Player.log")


def t_an_explicit_override_gets_through():
    allowed("grep -c Desert '/x/Saves/Ash.rws'", env={"MEASURE_ALLOW_SCAN": "1"})
    allowed("MEASURE_ALLOW_SCAN=1 grep -c Desert '/x/Saves/Ash.rws'")


def t_a_pattern_is_never_mistaken_for_a_path():
    """`grep -e '*.rws' file.txt` searches for a STRING, and must not be denied."""
    allowed("grep -e 'Ash.rws' notes.txt")
    allowed("grep --include=*.rws -rn foo src/")


def t_non_scanners_are_untouched():
    for cmd in ("ls -la '/x/Saves/Ash.rws'",
                "cp '/x/Saves/Ash.rws' /backup/",
                "du -sh '%s'" % DUMP,
                "stat /x/Player.log"):
        allowed(cmd)


def t_a_non_bash_tool_is_ignored():
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_name": "Read",
                          "tool_input": {"file_path": "/x/Ash.rws"}}),
        capture_output=True, text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    assert not p.stdout.strip(), p.stdout


def t_it_fails_open_on_garbage():
    p = subprocess.run([sys.executable, HOOK], input="not json at all",
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO))
    assert p.returncode == 0, p.returncode
    assert not p.stdout.strip(), p.stdout


def t_a_compound_command_is_caught_in_any_position():
    denied("cd /tmp && grep -c foo '/x/Ash.rws'")
    denied("echo hi; strings /x/y.dll")


# --------------------------------------------------------------------------
# red team, 2026-08-21 — nine scans got through and three legitimate commands
# were refused. Every one of them is pinned here.
# --------------------------------------------------------------------------

def t_evasions_that_used_to_work_are_closed():
    denied("grep -rc Desert '%s/'" % DUMP)                 # -r over the directory
    denied("grep -c foo /x/save.RWS")                      # uppercase extension
    denied("strings /x/Mods/J.DLL")                        # uppercase extension
    denied('bash -c "grep -c biome /x/save.rws"')          # one quote deep
    denied("zgrep -c foo /x/save.rws")                     # not a listed scanner
    denied("cat /x/save.rws | grep -c biome")              # path and tool split
    denied("grep -c biome /x/save.rws # per rimbench")     # comment as an alibi


def t_a_relative_path_is_resolved_against_the_shell_cwd():
    """`cd DefDump && grep -c X defs/ThingDef.json` names no absolute path.

    Without the shell's cwd the hook cannot classify it, and this was the
    easiest evasion of all — it is what a person naturally types."""
    denied("grep -c ThingDef defs/ThingDef.json", cwd=DUMP)


def t_a_search_pattern_is_never_mistaken_for_the_target():
    """These refusals were UNEARNED, and unearned refusals get a guard turned
    off. The pattern only LOOKS like a path."""
    allowed('grep -c "world/tiles.csv" /home/u/notes.txt')
    allowed('grep "*.dll" README.md')
    allowed("wc -l my_notes_about_Player.log")
    allowed("grep -c 'save.rws' CHANGELOG.md")


def t_the_instrument_allowlist_matches_tokens_not_substrings():
    """A trailing comment naming a tool must not wave a scan through, but the
    real tool must still be allowed."""
    allowed("python3 src/RimMandrake/Utils/rimbench/savemap.py '/x/Ash.rws'")
    denied("grep -c biome /x/save.rws  # rimbench says 233")


def t_a_bare_filename_with_no_directory_is_still_the_artifact():
    """`strings Assembly-CSharp.dll` evaded the guard: "looks like a path" was
    defined as "has a separator", so the commonest way people actually type it
    walked straight through. Found while fixing the skills that teach it."""
    denied("strings -a Assembly-CSharp.dll | grep QuestParts")
    denied("grep -c biome save.rws")
    denied("wc -l Player.log")
    # …but a bare name with no registered extension is still nobody's business
    allowed("wc -l notes.txt")
    allowed("grep -c TODO README.md")


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.startswith("t_"):
            case(k[2:], v)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
