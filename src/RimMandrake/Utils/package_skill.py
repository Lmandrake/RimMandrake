#!/usr/bin/env python3
"""package_skill.py — zip a skill folder into an installable .skill archive.

Skills in this repo live as source folders under `skills/`, but Claude Code
does not auto-discover that directory. They are installed from a `.skill`
archive, which is a plain zip with the skill folder at top level:

    rimworld-modding/SKILL.md
    rimworld-modding/references/...
    rimworld-modding/scripts/...

Writing the folder is therefore NOT shipping the skill - the same distinction
this project already makes between writing a mod file and deploying it.

    python src/RimMandrake/Utils/package_skill.py generating-images
    python src/RimMandrake/Utils/package_skill.py --all
    python src/RimMandrake/Utils/package_skill.py --all --check     # verify, write nothing

Exit codes: 0 ok, 1 a skill failed validation, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
SKILLS_DIR = REPO / "skills"

# Frontmatter limits from Anthropic's Agent Skills spec. A skill that violates
# them may be silently rejected at install time, which is worse than failing
# here.
NAME_MAX = 64
DESC_MAX = 1024
NAME_RE = re.compile(r"^[a-z0-9-]+$")
RESERVED = ("anthropic", "claude")

# Files that are workspace clutter rather than part of the skill.
EXCLUDE_DIRS = {"__pycache__", ".git"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md does not start with YAML frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("frontmatter is not terminated by a --- line")
    block = text[3:end]
    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key:  # folded continuation line
            fields[key] += " " + line.strip()
    body_lines = text[end:].count("\n")
    fields["_body_lines"] = str(body_lines)
    return fields


def validate(folder: Path) -> list[str]:
    problems: list[str] = []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return [f"no SKILL.md in {folder}"]

    try:
        fm = parse_frontmatter(skill_md)
    except ValueError as exc:
        return [str(exc)]

    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        problems.append("frontmatter has no `name`")
    else:
        if name != folder.name:
            problems.append(
                f"`name: {name}` does not match the folder name {folder.name}; "
                f"the archive path and the declared name must agree"
            )
        if len(name) > NAME_MAX:
            problems.append(f"name is {len(name)} chars, max {NAME_MAX}")
        if not NAME_RE.match(name):
            problems.append(f"name {name!r} must be lowercase letters, digits and hyphens")
        for word in RESERVED:
            if word in name:
                problems.append(f"name contains the reserved word {word!r}")

    if not desc:
        problems.append("frontmatter has no `description`")
    elif len(desc) > DESC_MAX:
        problems.append(f"description is {len(desc)} chars, max {DESC_MAX}")

    body_lines = int(fm.get("_body_lines", "0"))
    if body_lines > 500:
        problems.append(
            f"SKILL.md body is {body_lines} lines; the guidance is under 500 - "
            f"move detail into references/"
        )

    # A reference that does not exist is worse than no reference: the agent
    # goes looking and finds nothing.
    text = skill_md.read_text(encoding="utf-8")
    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if link.startswith(("http://", "https://", "#")):
            continue
        if not (folder / link).exists() and not (folder / link).resolve().exists():
            problems.append(f"SKILL.md links to {link}, which does not exist")

    return problems


def files_for(folder: Path) -> list[Path]:
    out = []
    for p in sorted(folder.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix in EXCLUDE_SUFFIXES:
            continue
        out.append(p)
    return out


def package(folder: Path, check_only: bool) -> bool:
    problems = validate(folder)
    for p in problems:
        print(f"  FAIL {p}", file=sys.stderr)
    if problems:
        return False

    members = files_for(folder)
    if check_only:
        print(f"  OK   {folder.name}: {len(members)} files, would package")
        return True

    archive = folder.parent / f"{folder.name}.skill"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in members:
            z.write(f, str(Path(folder.name) / f.relative_to(folder)))

    # Read the bytes back rather than trusting st_size: this repo has been
    # bitten by stale directory metadata on a synced mount.
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
    if bad:
        print(f"  FAIL archive is corrupt at {bad}", file=sys.stderr)
        return False

    size = len(archive.read_bytes())
    print(f"  OK   {archive.name}  {len(members)} files, {size:,} bytes")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("skill", nargs="*", help="skill folder name(s) under skills/")
    ap.add_argument("--all", action="store_true", help="package every skill folder")
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()

    if args.all:
        targets = sorted(p for p in SKILLS_DIR.iterdir()
                         if p.is_dir() and (p / "SKILL.md").is_file())
    elif args.skill:
        targets = [SKILLS_DIR / s for s in args.skill]
    else:
        ap.error("name at least one skill, or pass --all")
        return 2

    ok = True
    failed: list[str] = []
    for folder in targets:
        print(f"{folder.name}")
        if not folder.is_dir():
            print(f"  FAIL no such skill folder: {folder}", file=sys.stderr)
            ok = False
            failed.append(folder.name)
            continue
        if not package(folder, args.check):
            ok = False
            failed.append(folder.name)

    if not ok:
        # This used to read "Nothing was installed", which was FALSE and cost real
        # confusion: every skill that passed has already been written by the loop
        # above. A failing skill leaves its OWN archive stale, not the others.
        verb = "would be packaged" if args.check else "were packaged"
        print(
            "\n%d skill(s) FAILED and their archives are UNCHANGED (stale): %s"
            "\nThe other %d %s normally. Fix the failures and re-run."
            % (len(failed), ", ".join(failed), len(targets) - len(failed), verb),
            file=sys.stderr,
        )
        return 1
    if not args.check:
        print("\nArchives written. Install them in Claude Code to make the "
              "skills invocable - writing the folder does not do that.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
