#!/usr/bin/env python3
"""Rebuild and verify the two .bak-asimov-20260906 saves lost around 2026-09-09.

DROID_ASIMOV_SAVE_SCRUB_1 removed Asimov.Need_Energy blocks from two saves. The
backups vanished, but Backblaze had logged the SHA-1 of each file before and after
the scrub. A sibling save still holding the same blocks gives their text and
position (pawn id, then place in the needs list), so the originals rebuild exactly.
The logged hash is the proof; --rebuild refuses to write anything else.

  asimov_scrub_restore.py --rebuild --scrubbed-dir <dir holding the scrubbed saves>
  asimov_scrub_restore.py --verify
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from game_paths import SAVES  # noqa: E402

REPO = HERE.parents[2]
SUFFIX = ".bak-asimov-20260906"
BLOCK = re.compile(rb'[ \t]*<li Class="Asimov\.Need_Energy">.*?</li>\r?\n', re.S)
ID_LINE = re.compile(rb"^\s*<id>(.*?)</id>")

# Hashes and sizes are from Backblaze's bz_done log, rows of 2026-09-06.
PAIR = [
    {"name": "WORLDMAP_V1_original_c.rws", "blocks": 82, "size": 22976018,
     "sha1": "b32ee330c1f5bac3f305e95193272b5e49959fc8",
     "scrubbed_sha1": "057b3802cf9615e25438878b0e95f2194cc3f555",
     "donor": "world/WORLDMAP_V1_original.rws"},
    {"name": "gravship_scratch_d.rws", "blocks": 133, "size": 21831053,
     "sha1": "f157720a919affdf6fbf7da0bf5e1472020a09d1",
     "scrubbed_sha1": "86756b7b2585d869c2d25d4743c8586830cd6277",
     "donor": "{scrubbed_dir}/gravship_scratch_b.rws"},
]


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def indent(line: bytes) -> int:
    return len(line) - len(line.lstrip(b" \t"))


def backup_dir() -> Path:
    helper = Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
    root = subprocess.run([sys.executable, str(helper)], capture_output=True, text=True,
                          check=True).stdout.strip()
    return Path(root) / "rimmandrake" / "backups" / "asimov_scrub_20260906"


def rebuild(donor: bytes, scrubbed: bytes) -> bytes:
    """Put each of the donor's need blocks back into the scrubbed save."""
    src, dst = donor.split(b"\n"), scrubbed.split(b"\n")
    ids: dict[tuple[bytes, int], int] = {}
    for n, line in enumerate(dst):
        m = ID_LINE.match(line)
        if m:
            ids.setdefault((m.group(1), indent(line)), n)
    inserts: dict[int, list[bytes]] = {}
    for i, line in enumerate(src):
        if b'<li Class="Asimov.Need_Energy">' not in line:
            continue
        depth = indent(line)
        opener, place = i, 0
        while True:
            opener -= 1
            if indent(src[opener]) == depth - 1:
                break
            if indent(src[opener]) == depth and src[opener].lstrip().startswith(b"<li"):
                place += 1
        owner = opener
        while True:
            owner -= 1
            m = ID_LINE.match(src[owner])
            if m and indent(src[owner]) <= depth - 1:
                break
        at = ids[(m.group(1), indent(src[owner]))]
        while not (indent(dst[at]) == depth - 1 and dst[at].strip() == src[opener].strip()):
            at += 1
        at += 1
        seen = 0
        while True:
            if indent(dst[at]) == depth and dst[at].lstrip().startswith(b"<li"):
                if seen == place:
                    break
                seen += 1
            elif indent(dst[at]) == depth - 1 and dst[at].lstrip().startswith(b"</"):
                break
            at += 1
        inserts.setdefault(at, []).extend(src[i:i + 4])
    out: list[bytes] = []
    for n, line in enumerate(dst):
        out.extend(inserts.get(n, ()))
        out.append(line)
    return b"\n".join(out)


def do_rebuild(scrubbed_dir: Path) -> int:
    for item in PAIR:
        scrubbed = (scrubbed_dir / item["name"]).read_bytes()
        donor_path = item["donor"].format(scrubbed_dir=scrubbed_dir)
        donor = Path(donor_path) if Path(donor_path).is_absolute() else REPO / donor_path
        data = rebuild(donor.read_bytes(), scrubbed)
        if sha1(data) != item["sha1"]:
            print(f"REFUSED {item['name']}: rebuilt {sha1(data)}, logged {item['sha1']}")
            return 1
        for folder in (Path(SAVES), backup_dir()):
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (item["name"] + SUFFIX)).write_bytes(data)
        print(f"REBUILT {item['name']}{SUFFIX} {len(data)} bytes, sha1 {item['sha1']}")
    return 0


def do_verify() -> int:
    bad = 0
    for item in PAIR:
        for folder in (Path(SAVES), backup_dir()):
            path = folder / (item["name"] + SUFFIX)
            if not path.exists():
                print(f"FAIL missing {path}")
                bad += 1
                continue
            data = path.read_bytes()
            stripped, blocks = BLOCK.subn(b"", data)
            ok = (len(data) == item["size"] and sha1(data) == item["sha1"]
                  and blocks == item["blocks"] and sha1(stripped) == item["scrubbed_sha1"])
            print(f"{'OK  ' if ok else 'FAIL'} {path}: {len(data)} bytes, sha1 {sha1(data)[:12]}, "
                  f"{blocks} blocks, stripped sha1 {sha1(stripped)[:12]}")
            bad += not ok
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--scrubbed-dir", type=Path)
    a = ap.parse_args()
    if a.rebuild == a.verify or (a.rebuild and not a.scrubbed_dir):
        ap.error("pass --verify, or --rebuild with --scrubbed-dir")
    return do_rebuild(a.scrubbed_dir) if a.rebuild else do_verify()


if __name__ == "__main__":
    sys.exit(main())
