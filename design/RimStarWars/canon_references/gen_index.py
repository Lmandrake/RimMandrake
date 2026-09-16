#!/usr/bin/env python3
"""Generate INDEX.md: one row per canon-reference entry, walking the real
directories on disk (never a hardcoded roster).

Category logic (the part most likely to rot):
  - droid    : directory name starts with "droid_" (chassis dirs).
  - species  : directory slug appears in RACES_TODO.md's roster table (the
               `slug` column, backtick-quoted, 3rd `|`-cell of a data row).
               That table is the shipped-xenotype roster of record; a slug
               is a species iff the owner's roster says so, not by any
               naming pattern of the directory itself.
  - creature : everything else — every entry that is neither a droid_ dir
               nor a roster slug.

defName parsing: description.md's "**defName**" line, plus every following
"- " bullet in the same paragraph (blank line ends it), each contributing
only its FIRST backtick-quoted token — because every sampled entry puts the
real defName first on the line and any later backtick span on the same line
is a texture-folder name, a file path, or a field value, never a second
defName. A token counts only if it is a bare identifier (letters/digits/
underscore/hyphen, no `/`, `.`, `=`, `"`), starts uppercase (RimWorld
defNames always do here) and is not ALL-CAPS (that shape belongs to queue
IDs like PYRELANDS_CREATURE_RERENDER_1, never a defName). This is a heuristic,
not a def-dump measurement: a few droid entries also pick up a shared
ModExtension class name (e.g. `DroidworksExtension`) alongside real defNames,
because it is quoted in the same bullet shape. Zero tokens found -> UNPARSED,
never a blank cell.

Ruling detection: "## ruling" is empty content, OR content starting with the
literal "(empty" placeholder used throughout this library for "not reviewed
yet". Anything else is a real ruling, no matter how short.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "INDEX.md"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

DEFNAME_TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def load_species_slugs():
    text = (ROOT / "RACES_TODO.md").read_text(encoding="utf-8")
    slugs = set()
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| ✓") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue
        m = re.match(r"^`([^`]+)`$", cells[2])
        if m:
            slugs.add(m.group(1))
    return slugs


def classify(slug, species_slugs):
    if slug.startswith("droid_"):
        return "droid"
    if slug in species_slugs:
        return "species"
    return "creature"


def section_lines(text, name):
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines):
        if l.strip() == f"## {name}":
            start = i + 1
            break
    if start is None:
        return None
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return lines[start:end]


def _defname_like(token):
    if not DEFNAME_TOKEN_RE.match(token):
        return False
    if not token[0].isupper():
        return False
    if token.isupper():
        return False
    return True


def _first_backtick(line):
    m = re.search(r"`([^`]+)`", line)
    return m.group(1) if m else None


def parse_defnames(text):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith("**defName**")), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and lines[end].strip() != "":
        end += 1
    block = lines[start:end]

    found = []
    tok = _first_backtick(block[0])
    if tok and _defname_like(tok):
        found.append(tok)
    for l in block[1:]:
        if l.startswith("- "):
            tok = _first_backtick(l)
            if tok and _defname_like(tok):
                found.append(tok)

    seen = set()
    uniq = [f for f in found if not (f in seen or seen.add(f))]
    return uniq


def is_ruled(text):
    lines = section_lines(text, "ruling")
    if lines is None:
        return None
    content = "\n".join(lines).strip()
    if content == "" or content.startswith("(empty"):
        return False
    return True


def must_show_count(text):
    lines = section_lines(text, "Must show")
    if lines is None:
        return None
    return sum(1 for l in lines if re.match(r"^- \[.\]", l.strip()))


def entry_rows(species_slugs):
    rows = []
    for entry_dir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        slug = entry_dir.name
        desc = entry_dir / "description.md"
        if not desc.is_file():
            continue
        text = desc.read_text(encoding="utf-8")
        category = classify(slug, species_slugs)
        defnames = parse_defnames(text)
        defname_cell = "; ".join(defnames) if defnames else "UNPARSED"
        donor_art = (entry_dir / "donor_current_sprite.png").is_file()
        images = sum(
            1 for f in entry_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS
        )
        ruled = is_ruled(text)
        must_show = must_show_count(text)
        rows.append(
            {
                "slug": slug,
                "category": category,
                "defname": defname_cell,
                "donor_art": donor_art,
                "images": images,
                "ruled": ruled,
                "must_show": must_show,
            }
        )
    rows.sort(key=lambda r: (r["category"], r["slug"]))
    return rows


def render(rows):
    total = len(rows)
    by_category = {}
    for r in rows:
        by_category.setdefault(r["category"], 0)
        by_category[r["category"]] += 1
    donor_count = sum(1 for r in rows if r["donor_art"])
    ruled_count = sum(1 for r in rows if r["ruled"])
    unparsed_ruled = sum(1 for r in rows if r["ruled"] is None)
    total_images = sum(r["images"] for r in rows)

    lines = []
    lines.append("<!-- generated by gen_index.py — do not edit -->")
    lines.append("# Canon reference library — index")
    lines.append("")
    lines.append(f"**Total entries: {total}**")
    for cat in sorted(by_category):
        lines.append(f"- {cat}: {by_category[cat]}")
    lines.append(f"- with donor art (`donor_current_sprite.png`): {donor_count} / {total}")
    ruled_line = f"- ruled (`## ruling` has real content): {ruled_count} / {total}"
    if unparsed_ruled:
        ruled_line += f" ({unparsed_ruled} UNPARSED — no `## ruling` section found)"
    lines.append(ruled_line)
    lines.append(f"- total reference images (.jpg/.jpeg/.png/.webp) across all entries: {total_images}")
    lines.append("")
    lines.append("Generated by `python3 design/RimStarWars/canon_references/gen_index.py`.")
    lines.append("")
    lines.append("| slug | category | defName(s) | donor art | images | ruled | must show |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in rows:
        donor = "yes" if r["donor_art"] else "no"
        if r["ruled"] is None:
            ruled = "UNPARSED"
        else:
            ruled = "yes" if r["ruled"] else "no"
        must_show = "UNPARSED" if r["must_show"] is None else str(r["must_show"])
        lines.append(
            f"| [{r['slug']}]({r['slug']}/description.md) | {r['category']} | "
            f"{r['defname']} | {donor} | {r['images']} | {ruled} | {must_show} |"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    species_slugs = load_species_slugs()
    rows = entry_rows(species_slugs)
    content = render(rows)
    if check:
        current = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else None
        if current != content:
            print("INDEX.md is stale — run gen_index.py to regenerate.")
            return 1
        print("INDEX.md is up to date.")
        return 0
    INDEX_PATH.write_text(content, encoding="utf-8")
    print(f"wrote {INDEX_PATH} ({len(rows)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
