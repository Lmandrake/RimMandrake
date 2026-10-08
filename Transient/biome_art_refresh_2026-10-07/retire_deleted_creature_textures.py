#!/usr/bin/env python3
"""Retire (archive + delete via the art ledger) the textures of the creatures deleted from the game
2026-10-08 (decision taken by question card), when no surviving def still points at the same texPath.
Owner-kept pictures are refused by the ledger and listed instead.  Usage: --dry-run | --apply"""
import json, re, subprocess, sys, glob
from pathlib import Path
from lxml import etree
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import artledger as L
DEAD = json.loads((Path(__file__).with_name("deleted_defs_2026-10-08.json")).read_text())
BASE = "2fd0ca3a6"  # last commit with the defs present (passed via env if needed)

def texpaths_in(xml_text, names):
    out = {}
    root = etree.fromstring(xml_text.encode())
    for d in root:
        if not isinstance(d.tag, str): continue
        n = d.findtext("defName")
        if n in names:
            for e in d.iter():
                if isinstance(e.tag, str) and e.tag in ("texPath", "dessicatedBodyTexPath") and e.text:
                    out.setdefault(e.text.strip(), set()).add(n)
    return out

def main(apply):
    base = sys.argv[2] if len(sys.argv) > 2 else BASE
    tex = {}
    for f in sorted({f for _, _, f in DEAD["defs"]}):
        txt = subprocess.run(["git", "-C", str(REPO), "show", f"{base}:src/{f}"], capture_output=True, text=True).stdout
        for k, v in texpaths_in(txt, {n for _, n, _ in DEAD["defs"]}).items():
            tex.setdefault(k, set()).update(v)
    # texPaths still named by any surviving def/patch anywhere in src
    alive = set()
    for p in glob.glob(str(REPO / "src/**/*.xml"), recursive=True):
        alive.update(t.strip() for t in re.findall(r"<(?:texPath|dessicatedBodyTexPath)>([^<]+)<", open(p, encoding="utf-8", errors="replace").read()))
    report = {"retired": [], "kept_shared": [], "refused": []}
    for tp, owners in sorted(tex.items()):
        if tp in alive or "/Item/" in tp:   # items: shared stack-count folders, never retired here
            report["kept_shared"].append(tp); continue
        files = [Path(p) for p in glob.glob(str(REPO / "src/**/Textures" / (tp + "*.png")), recursive=True)
                 if re.fullmatch(re.escape(Path(tp).name) + r"(_(north|south|east|west|[a-z]|m|[a-z]m|northm|southm|eastm|westm))?\.png", Path(p).name)]
        for p in files:
            if not apply:
                report["retired"].append(str(p.relative_to(REPO))); continue
            try:
                r = L.retire(str(p), reason=f"script:Transient/biome_art_refresh_2026-10-07/{Path(__file__).name}")
                report["retired"].append(str(p.relative_to(REPO)))
            except L.Refused as e:
                report["refused"].append(f"{p.relative_to(REPO)}: {e}")
    print(json.dumps(report, indent=1))

if __name__ == "__main__":
    main(sys.argv[1] == "--apply")
