#!/usr/bin/env python3
"""guiding_prose_calibration.py - the planted cases of the guiding-prose reader (family guiding_prose_reader).

The `model_check` of that row in infrastructure/state/judge_calibration.json: run only by `refusal_contract.py calibrate
--model guiding_prose_reader` (it spends: one Opus call per case, about 6 s each), never on a schedule. Each case is one
section, put to the real brief (guiding_prose_reader.md), the real glossary and the real model by guiding_prose.read_faults.
A `refuse` case came out as planted when the reader names the planted term; a `pass` case when the reader names nothing.
One {id, expect, got} row per case goes to $RM_CALIBRATION_RESULTS. A case that the reader could not answer writes no row.
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import guiding_prose as G  # noqa: E402

# (id, expect, planted term, file, text). The first cases are the owner's lines in their wording before de63778138e0, and
# real lines that the rewrite batch of 2026-11-23 listed under "Could not determine".
CASES = [
    ("his_line_d_f_primitive", "refuse", "D/F", "design/RimMandrake/standing_rulings.md",
     "## A pit is a SUPERDEEP cell\n\n- The ruling is made and fully specified.\n- A pit is depth 4 on the D/F primitive that "
     "rulings 18/19 already established.\n- Oil and poison are FluidDefs.\n"),
    ("his_line_the_belt", "refuse", "belt", "design/RimMandrake/standing_rulings.md",
     "## Git\n\n- The alarm does not count two kinds of commit:\n  - a trailing lesson/ledger commit (the belt carries those);\n"
     "  - a commit whose content origin/main already holds under another hash.\n"),
    ("his_line_revert_what", "refuse", "Revert", "design/RimMandrake/standing_rulings.md",
     "## Git\n\n- A pool clone with unpushed work is never reused.\n- The pool has one alarm. It reads the free space.\n"
     "- Revert if a clone strands work, or if the free space on `/` goes under the disk floor.\n"),
    ("real_coverage_park", "refuse", "coverage park", "design/RimMandrake/delegation_policy.md",
     "## The acts that stay his\n\n- A seat may do each of these acts:\n  - lift a coverage park;\n  - answer a card.\n"),
    ("real_cap_n", "refuse", "N", "design/RimMandrake/delegation_policy.md",
     "## What a seat may do\n\n- A seat may raise a cap, N or a stage ceiling. The seat logs the act.\n"),
    ("real_preflight_code", "refuse", "O13", "infrastructure/state/facts/tool_traps.md",
     "## Paths\n\n- The python.exe bridge scripts and preflight O13 need `RM_DATA_ROOT` on that one command.\n"),
    ("coined_the_kennel", "refuse", "kennel", "infrastructure/agents/CHARTER.md",
     "## Clones\n\n- A helper works in its own clone.\n- Give the clone back to the kennel before the run ends.\n"),
    ("coined_quiet_lane", "refuse", "quiet lane", "src/RimMandrake/rimflow/roles/operations.md",
     "## Alarms\n\n- Read each alarm. An alarm with no owner goes to the quiet lane.\n- Close an alarm only with a reading.\n"),
    ("synonym_warden_for_monitor", "refuse", "warden", "src/RimMandrake/rimflow/roles/operations.md",
     "## The lock monitor\n\n- The lock monitor is the program that reads the game's lock each minute.\n- The lock monitor frees a "
     "lock whose process is gone.\n- When the warden frees a lock, write one line in the log.\n"),
    ("no_object_release", "refuse", "Release", "infrastructure/agents/CHARTER.md",
     "## Holds\n\n- A hold stops a mod. A lock stops a game. A claim stops a second helper.\n- Release when the owner says so.\n"),
    ("repaired_pit", "pass", None, "design/RimMandrake/standing_rulings.md",
     "## A pit is a SUPERDEEP cell\n\n- The ruling is made and fully specified. Its item holds the state of the build; read the "
     "state there, with `rimflow show PIT_SUPERDEEP_COLLAPSE_1`: `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md`.\n"
     "- A pit is depth 4 on the D/F primitive that rulings 18/19 already established. D/F is depth and fill: each cell has a dug "
     "depth (D) and a fill of liquid (F). Rulings 18 and 19 are in `design/RimMandrake/flowworks_mod_definition.md` (§20 and §21).\n"),
    ("repaired_pool", "pass", None, "design/RimMandrake/standing_rulings.md",
     "## Git\n\nMore than 4 writers at one time may use a pool of reused clones (the pool). The disk floor is a figure in "
     "`src/RimMandrake/Utils/slot_rules.json`.\n\n- Revert the pool if a clone strands work, or if the free space on `/` goes under "
     "the disk floor. To revert the pool is to end the approval of reused clones for more than 4 writers, and to return to at most "
     "4 writers at one time.\n- A clone strands work when the clone holds a commit that is on no remote.\n"),
    ("plain_commands", "pass", None, "CLAUDE.md",
     "## Git\n\n- Work in the clone that your brief names. Commit explicit paths only.\n- Keep file writes and commits in separate "
     "Bash calls. Hooks refuse a compound command whole.\n- Never force a push.\n"),
    ("defined_in_the_section", "pass", None, "CLAUDE.md",
     "## The readiness list\n\n- The readiness list names every component that a mod will touch.\n- The readiness list marks each open "
     "ticket BLOCKS (the ticket stops the build), RARE (the fault seldom happens) or NOT ON PATH (the build never reads it).\n- Do not start a build of the mod before its readiness list has no BLOCKS ticket.\n"),
    ("rimworld_and_shell_words", "pass", None, "infrastructure/state/facts/instrument_traps.md",
     "## Ticks\n\n- `Plant` ticks only `TickLong()`. A comp on a plant overrides `CompTickLong()`.\n- A patch that matches nothing logs "
     "nothing. Read the first exception in `Player.log`, not the loudest one.\n- A quicktest map takes about 90 s.\n"),
    ("glossary_words", "pass", None, "infrastructure/agents/CONDUCTOR.md",
     "## Your place\n\n- The Conductor takes the bridge only when no hold of his stands on the game.\n- A bar that reads UNMEASURED is "
     "not a pass.\n- He walks the mod last.\n"),
    ("an_owner_quote", "pass", None, "design/RimMandrake/standing_rulings.md",
     "## His words\n\nThe owner, 2026-11-02: *\"Put it on the belt, use the kennel, and revert if the quiet lane says so.\"*\n\n"
     "- Ask him before a money spend.\n"),
    ("item_and_path_pointers", "pass", None, "design/RimMandrake/standing_rulings.md",
     "## Sun\n\n- Heat from the sun is one function of the sun's angle (`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`).\n"
     "- The migration is the item `RIMMANDRAKE_MOVE_SUN_HEAT_TO_ONE_FUNCTION_LAST`.\n- Before you build shade, read that file.\n"),
]


def run(ask=None):
    G.lint()
    lex = G.glossary()
    ask = ask or G.ask_model

    def one(c):
        cid, expect, term, path, text = c
        sents = G.sentences(text)
        fs, _dropped, why = G.read_faults(path, text, sents, lex, ask)
        if fs is None:
            return {"id": cid, "why": why}
        if expect == "refuse":
            got = "refuse" if any(G.squash(term).lower() in G.squash(f["term"]).lower() for f in fs) else "pass"
        else:
            got = "refuse" if fs else "pass"
        return {"id": cid, "expect": expect, "got": got, "named": [f["term"] for f in fs]}
    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(one, CASES))


def main():
    rows = run()
    for r in rows:
        print("%s %s: expect %s, got %s%s" % ("DID NOT RUN" if "why" in r else "ok" if r["got"] == r["expect"] else "WRONG", r["id"],
                                             r.get("expect"), r.get("got"), " (%s)" % (r.get("why") or r.get("named"))))
    out = os.environ.get("RM_CALIBRATION_RESULTS")
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"cases": [r for r in rows if "why" not in r]}, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
