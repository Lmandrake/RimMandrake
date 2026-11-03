#!/usr/bin/env python3
"""ROT_CARTOON_VARIANT_REPAINT_1 proof — needs no git history and no data root (runs in a clean export).

Exit 0 when all hold, 1 when any fails:
  1. none of the 23 retired cartoon variants (sha256 in cartoon_variants_retired.json) is on disk under ANY name;
  2. a retired file NAME on disk is one of the listed `reoccupied` slots and holds the bytes the art ledger records
     live there (owner sheet picks / accepted renders, never the old cartoon);
  3. `art.py guard worktree <Rot Textures>` is clean (in a git checkout: uncommitted changes vs HEAD; in an export:
     every PNG on disk against the folded ledger);
  4. every listed folder holds `min_variants`+ PNGs, each ledger-live (painted variants that survived review).

    python3 src/RimMandrake/TheRot/check_cartoon_variants_retired.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEX = "src/RimMandrake/TheRot/Textures"
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    man = json.loads((HERE / "cartoon_variants_retired.json").read_text(encoding="utf-8"))
    retired = {r["sha256"]: r["path"] for r in man["retired"]}
    names = {r["path"] for r in man["retired"]}
    bad = []
    if len(retired) != 23 or len(names) != 23:
        bad.append(f"manifest lists {len(retired)} retired blobs / {len(names)} names, expected 23")
    disk = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / TEX).rglob("*.png"))}
    if len(disk) < 40:
        print(f"UNMEASURED: only {len(disk)} PNGs under {TEX}")
        return 1
    for rel, h in disk.items():                                     # 1. retired bytes, any name
        if h in retired:
            bad.append(f"CARTOON LIVE: {retired[h]} bytes at {rel}")
    idx = L.Index()
    for rel in sorted(names & set(disk)):                           # 2. retired names
        why = man["reoccupied"].get(rel)
        live = idx.live.get(L.split_texture_path(rel))
        if not why:
            bad.append(f"RETIRED NAME LIVE: {rel} (not a listed reoccupied slot)")
        elif not live or live.get("sha") != disk[rel]:
            bad.append(f"RETIRED NAME LIVE: {rel} holds bytes the art ledger does not record live there")
        else:
            print(f"reoccupied ok: {rel.rsplit('/', 1)[1]} = {disk[rel][:12]} ({why})")
    g = subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/Utils/art/art.py"), "guard", "worktree", TEX],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)  # 3. guard
    print(g.stdout.strip().splitlines()[-1] if g.stdout.strip() else g.stderr.strip()[-300:])
    if g.returncode != 0:
        bad.append("art guard worktree not clean:\n" + (g.stdout + g.stderr).strip()[-1500:])
    n_var = 0
    for folder in man["folders"]:                                    # 4. variants per folder
        pngs = [r for r in disk if r.rsplit("/", 1)[0] == folder]
        livepngs = [r for r in pngs if (idx.live.get(L.split_texture_path(r)) or {}).get("sha") == disk[r]]
        n_var += len(livepngs)
        if len(livepngs) < man["min_variants"]:
            bad.append(f"TOO FEW: {folder} holds {len(livepngs)} ledger-live variants ({len(pngs)} PNGs)")
        else:
            print(f"{folder.rsplit('Plant/', 1)[-1]}: {len(livepngs)} variants")
    for b in bad:
        print(b)
    print(f"checked {len(retired)} retired blobs against {len(disk)} Rot PNGs; {len(man['folders'])} folders, "
          f"{n_var} live variants; bad={len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
