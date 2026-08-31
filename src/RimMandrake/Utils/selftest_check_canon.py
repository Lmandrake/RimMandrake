#!/usr/bin/env python3
"""Selftest for check_canon.py — run after ANY change to it or to canon.yml.

A canon checker fails in two directions and they cost very differently:

  FALSE MISS     it reports clean and the contradiction survives. Expensive, and
                 invisible — the whole point of the tool is that its silence means
                 something, so a false miss makes every future clean run worthless.
  FALSE POSITIVE it flags a line that was fine. Cheap: someone reads it, disagrees,
                 and adds `<!-- canon-ok: why -->`. Visible by construction.

⚠️ So where the two trade off, this file pins the FALSE-POSITIVE side. The clearest
case is `the_one_map.md:130`, a table row whose right cell strikes through a dead
citation while its left cell asserts a live target. Under the naive line-wide
exemption rule that row was silently skipped; under cell-scoping it is flagged.
Being flagged is correct here, and case "table row: strikethrough in the OTHER cell"
exists to keep it that way.

    python3 src/RimMandrake/Utils/selftest_check_canon.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "check_canon.py")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

HIT, CLEAN = True, False

# (name, markdown, expect_hit, rule key expected in the output or None)
CASES = [
    # ---- must FIRE: the values the 2026-08-20 audit found asserted live ---------
    ("water 25%", "Water is ~25% of tiles, accept 22-28%.", HIT, "water"),
    ("water 6.9%", "The planet measures 6.9% water.", HIT, "water"),
    ("settlements 66", "There are 66 settlements, all ours.", HIT, "settlements"),
    ("settlements 37", "37 settlements across the planet.", HIT, "settlements"),
    ("factions fourteen", "Fourteen NPC factions exist.", HIT, "factions"),
    ("factions 11", "raids drawn from 11 factions", HIT, "factions"),
    ("bestiary 78", "78 named creatures in the bestiary.", HIT, "bestiary"),
    ("latitude axis", "## Correction: LATITUDE IS THE AXIS.", HIT, "axis"),
    # ⚠️ ADVISORY since 2026-08-20, so it prints and exits 0. Since the correction the
    # RIGHT docs discuss −37 °C constantly — explaining it is the mod's and that a
    # worldgen-only patch cannot reach a frozen save. A rule that fires on correct
    # prose is worse than none, so this one flags for a human and never gates.
    ("our terminator -37 is advisory", "Our painted terminator runs -37 C.",
     CLEAN, None),
    ("lake cut", "`Lake` cut, `Ocean` kept.", HIT, "lake"),
    ("tiles 21873", "The planet grid is 21873 tiles.", HIT, "tiles"),

    # ---- must NOT fire: the number is not about the fact ------------------------
    # `66` is a settlement count, a BiomeDef count and a rainfall figure in three
    # different files. Without the context test this rule is a coin toss.
    ("66 BiomeDefs is not 66 settlements", "The owner reviewed all 66 BiomeDefs.",
     CLEAN, None),
    ("66 mm of rain is not 66 settlements", "The 58-80 arc band takes 66 mm.",
     CLEAN, None),
    ("14 in prose about something else", "She was fourteen when the ship fell.",
     CLEAN, None),
    ("mod -37 is the mod's, not ours", "The mod's curve reads -37 C at x=1.0.",
     CLEAN, None),

    # ---- must NOT fire: the cell DOCUMENTS the value ----------------------------
    ("strikethrough", "~~25% of tiles water~~ was the old spec.", CLEAN, None),
    ("superseded", "Water 25% — superseded by the 2026-08-18 ruling.", CLEAN, None),
    ("blockquote", "> Fourteen factions, as the old audit said.", CLEAN, None),
    ("code fence", "```\nFourteen factions here.\n```", CLEAN, None),
    ("escape same line",
     "Water is 25% of tiles. <!-- canon-ok: quoting the dead spec -->", CLEAN, None),
    ("escape line above",
     "<!-- canon-ok: quoting the dead spec -->\nWater is 25% of tiles.", CLEAN, None),

    # ---- the cell-scoping cases, both directions --------------------------------
    ("table row: strikethrough in the SAME cell",
     "| ~~25% water~~ dead | see canon |", CLEAN, None),
    ("table row: strikethrough in the OTHER cell",
     "| Water target ~8.6% of tiles | ~~worldgen_sea_spec req 1 (22-28%)~~ |",
     HIT, "water"),
    ("⛔ negates a placement, not the biome",
     "⛔ **Not** in Ocean/Lake — no fauna there.", CLEAN, None),

    # ---- a DENIAL is not an assertion -------------------------------------------
    ("denial: not 25%", "Water is 8.14% of tiles — not 25%.", CLEAN, None),
    ("denial: never fourteen", "There are 13 factions, never fourteen factions.",
     CLEAN, None),
    ("a denial does not cover a claim earlier in the cell",
     "Water is 25% of tiles, and the axis is not latitude.", HIT, "water"),

    # ---- advisory never fails the build -----------------------------------------
    ("undated mod count is advisory only", "The stack is 562 mods.", CLEAN, None),

    # ---- the modlist rule's own false positives ----------------------------------
    # ⚠️ Advisory means it never blocks, which makes noise MORE dangerous rather than
    # less: nobody investigates a warning they have learned is usually wrong, and the
    # real undated counts would then sit inside that noise forever. These five shapes
    # were all flagged on the real corpus.
    ("a DATED mod count is the point, not the defect",
     "the owner's real 578-mod list as of 2026-08-20", CLEAN, None),
    ("'since <date>' counts as dated",
     "575 mods since 2026-08-15.", CLEAN, None),
    ("a load-order POSITION is not a count",
     "that mod is deployed and enabled at position 557", CLEAN, None),
    ("'Active at 573' is a position too",
     "Active at 573. Swept the whole workshop tree.", CLEAN, None),
    ("a file:line citation is not a mod count",
     "`ship_distinctive_features.md:566` — from Afterlife, a mod", CLEAN, None),
    ("a count of PLANTS is not a count of mods",
     "a literal growDays for every plant — 566 of them across dozens of mods", CLEAN, None),
    ("…but a bare undated count still flags",
     "measured against the 573-mod stack.", CLEAN, "modlist_undated"),
    # ⚠️ Phrased WITHOUT "was" on purpose. The first draft of this case read "the stack
    # was 573 mods", which the HISTORICAL rule correctly exempts — the test was wrong,
    # not the checker. A past-tense count is documenting, which is exactly what we want.
    ("…and so does the space-separated form",
     "the stack runs 573 mods today.", CLEAN, "modlist_undated"),
]


CANON_LIVE = os.path.join(ROOT, "infrastructure", "state", "canon.yml")

# 🔴 SELFTEST_DRIFT_REPAIR_1: 9 of these CASES went red on 2026-08-30 with no code
# change of their own. check_canon.py grew `suspend_planet_rules()` on 2026-08-22
# (commit 3dc322c1, "There is no frozen world...") — while `canon.yml > planet.status`
# reads anything but `frozen`, every planet-derived rule (water, tiles, settlements,
# axis, lake, seas, named_regions, rivers, habitable_ring, start_tile) is downgraded
# to advisory (exit 0) even on a real hit. This file's CASES were last touched
# 2026-08-20, two days before that feature existed, and always assumed hard-fail.
# `planet.status` is legitimately `remaking` right now (owner, 2026-08-22/23: the
# freeze is a SAVEGAME — map ported through the live bridge, factions/leaders/
# ideoligions correct at initiation, THEN saved — and that has not happened yet;
# see canon.yml > planet.status_src and infrastructure/state/V1.md). So neither
# canon.yml nor the world-facts source is stale: the SELFTEST is, because its planet-
# derived cases are entangled with a live, intentionally-mutable status flag.
# ⇒ FIX: build a throwaway canon.yml with `planet.status` forced to `frozen` and run
# the rule-matching cases against THAT, decoupled from whatever the live flag says
# today. The suspend feature itself gets its own dedicated case below, run against
# a `remaking` fixture, so a future flip of the live flag can never silently change
# what this file asserts either way.
def _frozen_canon_root():
    """A temp ROOT whose infrastructure/state/canon.yml is the real one with
    `planet.status` forced to `frozen` — decouples the rule-matching CASES below
    from whatever the live status legitimately is today."""
    import yaml
    with open(CANON_LIVE, encoding="utf-8") as fh:
        canon = yaml.safe_load(fh)
    canon["planet"]["status"] = "frozen"
    d = tempfile.mkdtemp(prefix=".canon_frozen_", dir=os.path.dirname(os.path.dirname(HERE)))
    os.makedirs(os.path.join(d, "infrastructure", "state"), exist_ok=True)
    with open(os.path.join(d, "infrastructure", "state", "canon.yml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(canon, fh)
    return d


def _remaking_canon_root():
    """Same idea, forced the other way — for the one case that locks in the
    advisory-downgrade behaviour itself."""
    import yaml
    with open(CANON_LIVE, encoding="utf-8") as fh:
        canon = yaml.safe_load(fh)
    canon["planet"]["status"] = "remaking"
    d = tempfile.mkdtemp(prefix=".canon_remaking_", dir=os.path.dirname(os.path.dirname(HERE)))
    os.makedirs(os.path.join(d, "infrastructure", "state"), exist_ok=True)
    with open(os.path.join(d, "infrastructure", "state", "canon.yml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(canon, fh)
    return d


def run(md, project_dir=None):
    fd, path = tempfile.mkstemp(suffix=".md", prefix="canonprobe_", dir=ROOT)
    env = dict(os.environ)
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = project_dir
    else:
        env.pop("CLAUDE_PROJECT_DIR", None)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        p = subprocess.run([sys.executable, TOOL, path], capture_output=True,
                           text=True, cwd=ROOT, timeout=60, env=env)
        return p.returncode, p.stdout + p.stderr
    finally:
        os.unlink(path)


def main():
    if subprocess.run([sys.executable, "-c", "import yaml"],
                      capture_output=True).returncode:
        print("SKIP — PyYAML not installed, so nothing was measured.\n"
              "⚠️ UNMEASURED is not PASSED.", file=sys.stderr)
        return 2

    frozen_root = _frozen_canon_root()
    remaking_root = _remaking_canon_root()
    fails = 0
    try:
        for name, md, expect_hit, key in CASES:
            code, out = run(md, project_dir=frozen_root)
            # exit 1 = a hard contradiction. Advisory hits print but still exit 0.
            got_hit = code == 1
            ok = got_hit == expect_hit and (not key or ("[%s]" % key) in out)
            print("%-5s %s" % ("ok" if ok else "FAIL", name))
            if not ok:
                fails += 1
                print("        exit=%s expected_hit=%s\n        %s"
                      % (code, expect_hit, out.strip().replace("\n", "\n        ")[:600]))

        # ⭐ Locks in suspend_planet_rules() itself: a real hit on a planet-derived
        # fact, against a canon reading `remaking`, must print but NOT block.
        name = "planet.status=remaking downgrades a planet-derived hit to advisory"
        code, out = run("Water is 25% of tiles.", project_dir=remaking_root)
        ok = code == 0 and "advisory" in out and "[water]" in out
        print("%-5s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            fails += 1
            print("        exit=%s\n        %s"
                  % (code, out.strip().replace("\n", "\n        ")[:600]))
    finally:
        shutil.rmtree(frozen_root, ignore_errors=True)
        shutil.rmtree(remaking_root, ignore_errors=True)

    total = len(CASES) + 1
    print("\n%d/%d passed" % (total - fails, total))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
