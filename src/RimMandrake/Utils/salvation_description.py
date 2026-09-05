#!/usr/bin/env python3
"""The Salvation's player-facing description: ONE source, three generated copies.

The text used to be maintained by hand in four places - the doc, this package's
`build_salvation_rid.py`, the faction def, and the committed `.rid` - which is
three chances to drift and no way to notice.

    SOURCE  design/Jawa/worldbuilding/ideoligion/the_salvation_description.md
            (the "## The text" section; the owner reviews it there, and it is the
            only copy anybody edits)

    GENERATED
        src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaTribes.xml  <ideoDescription>
        src/Jawa/ideoligion/The Salvation.rid   <description> + <descriptionTemplate>
        build_salvation_rid.py imports `text()` instead of holding a literal

Run `--check` to verify the copies match the source (exit 1 if not); no flag
writes them. Idempotent: running it twice changes nothing the first run did not.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

REPO = Path(__file__).resolve().parents[3]
SOURCE = REPO / "design/Jawa/worldbuilding/ideoligion/the_salvation_description.md"
FACTION_XML = REPO / "src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaTribes.xml"
RID = REPO / "src/Jawa/ideoligion/The Salvation.rid"


def _strip_markdown(line: str) -> str:
    line = re.sub(r"^>\s?", "", line)          # blockquote epigraph
    line = line.replace("**", "").replace("*", "")
    line = line.replace("—", "-")         # em dash -> plain, as the game has it
    return line


def text() -> str:
    """The description as RimWorld wants it: plain, real newlines between paragraphs."""
    body = SOURCE.read_text(encoding="utf-8")
    m = re.search(r"^## The text\s*$(.*?)^---\s*$", body, re.M | re.S)
    if not m:
        raise SystemExit(f"could not find the '## The text' section in {SOURCE}")
    paragraphs = []
    for chunk in m.group(1).strip().split("\n\n"):
        joined = " ".join(_strip_markdown(l).strip() for l in chunk.splitlines())
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs)


def inline() -> str:
    """Same text on one line, with literal backslash-n - what XML and .rid hold."""
    return text().replace("\n", "\\n")


def _sub_tag(blob: str, tag: str, value: str) -> tuple[str, int]:
    return re.subn(rf"(<{tag}>)(.*?)(</{tag}>)",
                   lambda m: m.group(1) + value + m.group(3), blob, flags=re.S)


def sync(write: bool) -> bool:
    """Push the source into every generated copy. True when everything already matched."""
    # Found in the 2026-09-05 code review wave: inline() is substituted straight into
    # XML tags below with no escaping. An ampersand or angle bracket in the source
    # markdown would silently write malformed XML into JawaTribes.xml/The Salvation.rid
    # with nothing here to catch it.
    want_inline = _xml_escape(inline())
    clean = True
    for path, tags in ((FACTION_XML, ("ideoDescription",)),
                       (RID, ("description", "descriptionTemplate"))):
        blob = original = path.read_text(encoding="utf-8")
        for tag in tags:
            blob, n = _sub_tag(blob, tag, want_inline)
            if not n:
                raise SystemExit(f"no <{tag}> in {path}")
        if blob != original:
            clean = False
            print(f"{'wrote' if write else 'STALE'}  {path.relative_to(REPO)}")
            if write:
                path.write_text(blob, encoding="utf-8")
        else:
            print(f"ok     {path.relative_to(REPO)}")
    return clean


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify only; exit 1 if a copy has drifted")
    ap.add_argument("--print", action="store_true", help="print the source text and exit")
    args = ap.parse_args()
    if args.print:
        print(text())
        return 0
    clean = sync(write=not args.check)
    if args.check and not clean:
        print("\nDrift. Run without --check to regenerate from the source doc.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
