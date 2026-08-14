#!/usr/bin/env python3
"""Pull gene and xenotype icons out of every active mod's AssetBundles.

WHY: Biotech ships zero loose PNGs -- every vanilla gene icon lives inside
`Data/Biotech/AssetBundles/resources_biotech`, so a `find -name '*.png'` sweep
reports 1169 of 1422 genes as art-less. Same trap that made the mech and anomaly
registers go to the wiki for pictures. Bundles are readable; go to the source.

Writes a flat cache of PNGs named after the RimWorld texture path, so
genome_matrix_build.py can resolve `UI/Icons/Genes/Gene_Darkvision` whether the
art was a loose file or compiled into a bundle.

REQUIRES UnityPy, which Debian's PEP-668 python3 will not install into.
Run it with the project venv:

    ~/.venvs/rimart/bin/python src/RimMandrake/Utils/genome_art_cache.py

The cache is derived and gitignored -- regenerate it, do not commit it. What
gets committed is the HTML with the art already inlined.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import UnityPy
except ImportError:
    sys.exit("UnityPy is required. Run this with ~/.venvs/rimart/bin/python "
             "(see the module docstring).")

from game_paths import GAME_DATA, LOCAL_MODS, MODS_CONFIG, WORKSHOP  # noqa: E402

# Substring match, not prefix: every pack invents its own tree. Vanilla uses
# UI/Icons/Genes, Outer Rim uses OuterRim/XenotypeIcons and OuterRim/GeneIcons,
# Alpha Genes uses a bare GeneIcons/. A prefix list missed two of the three.
WANTED = ("gene", "xenotype")

CONTAINER_RE = re.compile(r"^assets/data/[^/]+/textures/(.*)$", re.I)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def rimworld_path(container: str) -> str:
    """'assets/data/<pkgid>/textures/ui/icons/genes/x.png' -> 'ui/icons/genes/x'."""
    c = container.replace("\\", "/").lower()
    m = CONTAINER_RE.match(c)
    rel = m.group(1) if m else c
    return os.path.splitext(rel)[0]


def active_package_ids() -> list[str]:
    import xml.etree.ElementTree as ET
    root = ET.parse(MODS_CONFIG).getroot()
    return [li.text.strip().lower() for li in root.findall("./activeMods/li") if li.text]


def bundle_files(mod_dir: Path) -> list[Path]:
    out = []
    for sub in (mod_dir, *(d for d in mod_dir.iterdir() if d.is_dir())) if mod_dir.is_dir() else []:
        bdir = sub / "AssetBundles"
        if bdir.is_dir():
            for f in bdir.iterdir():
                # The bundle is the extensionless file; .manifest is Unity's index.
                if f.is_file() and f.suffix.lower() not in (".manifest", ".meta"):
                    out.append(f)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="observed/genome/art_cache")
    ap.add_argument("--all-paths", action="store_true",
                    help="cache every texture, not just gene/xenotype icons")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    from build_packageid_index import read_about  # strips modDependencies first

    roots = [Path(GAME_DATA), Path(LOCAL_MODS), Path(WORKSHOP)]
    mod_dirs: dict[str, Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for d in root.iterdir():
            if not d.is_dir():
                continue
            about = d / "About" / "About.xml"
            if not about.is_file():
                continue
            _name, pid = read_about(str(about))
            if pid:
                mod_dirs.setdefault(str(pid).lower(), d)

    active = active_package_ids()
    log(f"{len(active)} active mods, {len(mod_dirs)} folders resolved")

    written = 0
    scanned = 0
    for pid in active:
        d = mod_dirs.get(pid)
        if not d:
            continue
        for bundle in bundle_files(d):
            try:
                env = UnityPy.load(str(bundle))
            except Exception as exc:  # a corrupt bundle costs that bundle, not the run
                log(f"  ! {bundle.name}: {exc}")
                continue
            scanned += 1
            for obj in env.objects:
                if obj.type.name != "Texture2D":
                    continue
                container = ""
                try:
                    container = obj.container or ""
                except Exception:
                    pass
                rw = rimworld_path(container) if container else ""
                if not rw:
                    continue
                if not args.all_paths and not any(w in rw for w in WANTED):
                    continue
                dest = out_dir / (rw.replace("/", "%") + ".png")
                if dest.exists():
                    continue
                try:
                    data = obj.read()
                    data.image.save(dest)
                    written += 1
                except Exception as exc:
                    log(f"  ! {rw}: {exc}")
    log(f"scanned {scanned} bundles, wrote {written} PNGs to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
