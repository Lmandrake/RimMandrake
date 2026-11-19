#!/usr/bin/env python3
"""The image skills live in MandrakeWorkflows and every reader here finds them through one route
(RIMMANDRAKE_MOVE_IMAGE_SKILLS_TO_WORKFLOWS_GPT_TOOL_BORROWS; owner, by card 2026-11-19: "Move to MandrakeWorkflows").

  resolver   image_skills.py honours $RM_IMAGE_SKILLS_ROOT, defaults to ~/dev/MandrakeWorkflows/skills, and
             require() fails by naming the variable.
  present    the scripts this repo runs exist under the resolved root (UNMEASURED, exit 2, when the root is
             absent on this machine: could not look is not a fail).
  remnant    no skills/generating-images or skills/editing-images folder here, and no tracked .py/.sh under src/
             or skills/ names either as a path inside this repo. The scanner is first run on a planted tree.

    python3 src/RimMandrake/Utils/selftest_image_skills.py
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import image_skills  # noqa: E402

NAMES = ("generating-images", "editing-images")
# a repo-relative path to either skill: `skills/<name>`, `"skills", "<name>"`, `../<name>`, `parents[N] / "<name>"`;
# `MandrakeWorkflows/skills/<name>` (the new home) is not one.
REPO_PATH = re.compile(r"(?<!MandrakeWorkflows/)skills[\"']?\s*[/,]\s*[\"']?(generating|editing)-images"
                       r"|\.\./(generating|editing)-images"
                       r"|\]\s*/\s*[\"'](generating|editing)-images")
NEEDED = ("generating-images/SKILL.md", "editing-images/SKILL.md", "generating-images/scripts/codex_image.py",
          "generating-images/scripts/pnglib.py", "generating-images/scripts/gemini_image.py",
          "generating-images/scripts/chroma_key.py", "editing-images/scripts/compare_images.py")
FAILS = []


def check(cond, what):
    print(("PASS  " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def remnants(root: Path, files):
    hits = []
    for name in NAMES:
        if (root / "skills" / name).exists():
            hits.append("folder skills/%s" % name)
    for rel in files:
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if REPO_PATH.search(line):
                hits.append("%s:%d" % (rel, n))
    return hits


def tracked_code():
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "--", "src/*.py", "src/*.sh", "skills/*.py",
                          "skills/*.sh"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f]


def resolver_in(env_extra):
    env = {k: v for k, v in os.environ.items() if k != image_skills.ENV}
    env.update(env_extra)
    r = subprocess.run([sys.executable, "-c", "import image_skills as I; print(I.ROOT); print(I.CODEX_IMAGE)"],
                       cwd=str(HERE), capture_output=True, text=True, env=env, timeout=30)
    return r.stdout.splitlines()


def main():
    # ---- resolver -----------------------------------------------------------------------------------
    got = resolver_in({})
    check(got[:1] == [os.path.expanduser("~/dev/MandrakeWorkflows/skills")], "default root is ~/dev/MandrakeWorkflows/skills (%s)" % got[:1])
    got = resolver_in({image_skills.ENV: "/tmp/elsewhere/skills"})
    check(got == ["/tmp/elsewhere/skills", "/tmp/elsewhere/skills/generating-images/scripts/codex_image.py"],
          "$%s overrides the root (%s)" % (image_skills.ENV, got))
    try:
        image_skills.require(Path("/nonexistent/generating-images"))
        check(False, "require() refuses an absent folder")
    except FileNotFoundError as exc:
        check(image_skills.ENV in str(exc), "require() refuses an absent folder, naming $%s" % image_skills.ENV)

    # ---- remnant scanner on a planted tree, then the real one ------------------------------------------
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        bad = {"a.py": 'sys.path.insert(0, str(ROOT / "skills/generating-images/scripts"))',
               "b.py": 'CHROMA = os.path.join(REPO, "skills", "generating-images", "scripts", "chroma_key.py")',
               "c.py": 'sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "editing-images" / "scripts"))',
               "d.sh": 'python3 $R/skills/generating-images/scripts/codex_image.py edit',
               "e.py": 'os.path.join(os.path.dirname(__file__), "../generating-images/scripts")'}
        good = {"f.py": 'IMAGE_SKILLS = Path(os.path.expanduser("~/dev/MandrakeWorkflows/skills"))\n'
                        'sys.path.insert(0, str(IMAGE_SKILLS / "generating-images/scripts"))',
                "g.sh": 'CI="${RM_IMAGE_SKILLS_ROOT:-$HOME/dev/MandrakeWorkflows/skills}/generating-images/scripts/codex_image.py"',
                "h.py": 'image_skills.add_to_path()  # generating-images lives in MandrakeWorkflows'}
        for name, body in {**bad, **good}.items():
            (root / name).write_text(body + "\n")
        flagged = {h.split(":")[0] for h in remnants(root, list(bad) + list(good))}
        check(flagged == set(bad), "scanner flags every planted repo path and nothing else (flagged %s)" % sorted(flagged))
        (root / "skills" / "editing-images").mkdir(parents=True)
        check("folder skills/editing-images" in remnants(root, []), "scanner flags a leftover skill folder")
    hits = remnants(REPO, tracked_code())
    check(not hits, "no reader in this repo names the old in-repo paths (%d: %s)" % (len(hits), hits[:8]))

    # ---- the moved scripts are where the resolver says ---------------------------------------------------
    if not image_skills.ROOT.is_dir():
        print("UNMEASURED  %s is absent on this machine: could not look for the moved scripts" % image_skills.ROOT)
        print("%s: %d failure(s), presence UNMEASURED" % ("FAIL" if FAILS else "UNMEASURED", len(FAILS)))
        return 1 if FAILS else 2
    missing = [n for n in NEEDED if not (image_skills.ROOT / n).is_file()]
    check(not missing, "the scripts this repo runs exist under %s (missing: %s)" % (image_skills.ROOT, missing))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
