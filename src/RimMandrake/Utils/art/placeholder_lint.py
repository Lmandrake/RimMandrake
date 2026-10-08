#!/usr/bin/env python3
"""placeholder_lint.py — no shipped def may draw a GEOMETRIC PLACEHOLDER texture.

Owner, 2026-10-07 22:33 PDT: "make sure that at no time can geometric placeholder art ever remain a viable Variant or
selection, ok?"

Every texPath-like element (`texPath`, `texPathFemale`, …, any tag containing "texPath", case-insensitive) in every
XML under src/<tier>/<mod>/{Defs,Patches} is resolved against every src/**/Textures root the way the game does:
the folder itself (Graphic_Random / Graphic_Collection / Graphic_Appearances — every PNG inside), the file, and the
Graphic_Multi facings (_south/_east/_north/_west). Masks (`…m.png`) and UI/ are flat by design and never judged.
Each resolved PNG goes through placeholder_detect.placeholder_reason.

The ALLOWLIST (placeholder_allowlist.json beside this file) holds the placeholders that were already shipping on the
day the rule was made, each naming the job that will replace it. It can only SHRINK: an entry dated after its
`frozen` date, an entry whose file no longer ships or is no longer a placeholder (STALE — delete it), and a shipped
placeholder not on the list all fail the lint.

    python3 src/RimMandrake/Utils/art/placeholder_lint.py            report; exit 1 on any failure
    python3 src/RimMandrake/Utils/art/placeholder_lint.py --json OUT write every shipped placeholder to OUT
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import placeholder_detect as PD  # noqa: E402

REPO = PD.REPO
SRC = REPO / "src"
ALLOWLIST = HERE / "placeholder_allowlist.json"
FACINGS = ("_south", "_east", "_north", "_west")
MASK = re.compile(r"m(_(south|east|north|west))?$|[Mm]ask")


def texture_roots():
    return sorted(p for p in SRC.glob("*/*/Textures") if p.is_dir()) + \
        sorted(p for p in SRC.glob("*/*/*/Textures") if p.is_dir())


def def_xml_files():
    out = []
    for mod in sorted(SRC.glob("*/*")):
        for sub in ("Defs", "Patches"):
            out += sorted((mod / sub).rglob("*.xml")) if (mod / sub).is_dir() else []
    return out


def texpaths():
    """{texPath: [xml file rel, ...]} over every def/patch XML in src."""
    out: dict = {}
    for f in def_xml_files():
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for el in root.iter():
            if isinstance(el.tag, str) and "texpath" in el.tag.lower() and (el.text or "").strip():
                out.setdefault(el.text.strip().replace("\\", "/"), set()).add(str(f.relative_to(REPO)))
    return {k: sorted(v) for k, v in out.items()}


def resolve(tp: str, roots) -> list[Path]:
    if tp.startswith("UI/"):
        return []
    hits = []
    for r in roots:
        base = r / tp
        if base.is_dir():
            hits += sorted(base.glob("*.png"))
        for suf in ("",) + FACINGS:
            p = Path(str(base) + suf + ".png")
            if p.is_file():
                hits.append(p)
    return [h for h in dict.fromkeys(hits) if not MASK.search(h.stem)]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def shipped_placeholders() -> dict:
    """{repo-relative png: {"reason", "texPath", "defs", "sha256"}} for every placeholder a shipped def draws."""
    roots = texture_roots()
    out = {}
    seen = set()
    for tp, files in texpaths().items():
        for p in resolve(tp, roots):
            rel = str(p.relative_to(REPO))
            if rel in seen:
                if rel in out:
                    out[rel]["defs"] = sorted(set(out[rel]["defs"]) | set(files))
                continue
            seen.add(rel)
            try:
                why = PD.placeholder_reason(p)
            except Exception as e:                       # noqa: BLE001
                why = f"UNMEASURED: unreadable ({type(e).__name__})"
            if why:
                out[rel] = {"reason": why, "texPath": tp, "defs": files, "sha256": sha256(p)}
    return out


def load_allowlist(path: Path = ALLOWLIST) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {"frozen": "", "entries": []}


def lint(found: dict | None = None, allow: dict | None = None) -> list[str]:
    found = shipped_placeholders() if found is None else found
    allow = load_allowlist() if allow is None else allow
    frozen = allow.get("frozen") or ""
    entries = {e["path"]: e for e in allow.get("entries", [])}
    fails = []
    for e in entries.values():
        if not frozen or (e.get("added") or "9999") > frozen:
            fails.append(f"ALLOWLIST GREW: {e['path']} added {e.get('added')!r} after the list froze on {frozen!r} — "
                         "the list may only shrink; replace the art instead")
        if not e.get("job") and not str(e.get("status", "")).startswith("OWED"):
            fails.append(f"ALLOWLIST entry {e['path']} names no queued job and is not marked OWED")
    for rel, f in sorted(found.items()):
        if rel not in entries:
            fails.append(f"PLACEHOLDER SHIPS: {rel} (texPath {f['texPath']}, {', '.join(f['defs'][:2])}) — {f['reason']}")
        elif entries[rel].get("sha256") and entries[rel]["sha256"] != f["sha256"]:
            fails.append(f"NEW PLACEHOLDER BYTES: {rel} changed since it was allowlisted and is still a placeholder")
    for rel in sorted(set(entries) - set(found)):
        fails.append(f"STALE ALLOWLIST ENTRY: {rel} no longer ships as a placeholder — delete it from {ALLOWLIST.name}")
    return fails


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    found = shipped_placeholders()
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(found, indent=1))
    fails = lint(found)
    allow = load_allowlist()
    owed = sum(1 for e in allow.get("entries", []) if str(e.get("status", "")).startswith("OWED"))
    print(f"{len(found)} shipped placeholder texture(s); {len(allow.get('entries', []))} allowlisted "
          f"(frozen {allow.get('frozen')}; {owed} with no job yet); {len(fails)} failure(s)")
    for f in fails:
        print("FAIL " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
