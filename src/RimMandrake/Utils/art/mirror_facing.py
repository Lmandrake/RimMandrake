#!/usr/bin/env python3
"""mirror_facing.py — write <stem>_west.png as the horizontal mirror of <stem>_east.png, through the art ledger.

Use when a creature's east facing was replaced and an old hand-drawn west would otherwise keep showing the
retired picture. RimWorld mirrors east for west only when no _west file exists; deleting the file is not a
ledger act, so this writes the mirror instead.

    python3 src/RimMandrake/Utils/art/mirror_facing.py <path/to/Stem_east.png> [--dry-run]
"""
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger  # noqa: E402

WRITER = "script:src/RimMandrake/Utils/art/mirror_facing.py"


def main(argv):
    if not argv or not argv[0].endswith("_east.png"):
        sys.exit("usage: mirror_facing.py <Stem_east.png> [--dry-run]")
    east = Path(argv[0])
    west = east.with_name(east.name[: -len("_east.png")] + "_west.png")
    buf = io.BytesIO()
    Image.open(east).transpose(Image.FLIP_LEFT_RIGHT).save(buf, "PNG")
    print(artledger.install_bytes(west.resolve(), buf.getvalue(), reason=WRITER,
                                  provenance={"kind": "derived", "transform": "mirror_east"},
                                  dry_run="--dry-run" in argv))


if __name__ == "__main__":
    main(sys.argv[1:])
