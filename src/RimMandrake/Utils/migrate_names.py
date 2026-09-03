#!/usr/bin/env python3
"""Phase 2 migrator for NAMING_SCHEME_EXECUTION_1.

Reads infrastructure/state/naming_rename_map.csv (the single source of truth)
and applies it in stages. Default is DRY RUN (a report, no writes).

  --stage text      def/packageId/namespace/path replacements across src/
  --stage folders   emit + optionally run the git mv list
  --stage modsconfig  swap packageIds in the live ModsConfig.xml
  --apply           actually write (otherwise report only)

Rows with new == old or new == TBD_SPLIT are skipped (Phase 3 owns the split).
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAP = ROOT / "infrastructure/state/naming_rename_map.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from game_paths import MODS_CONFIG  # noqa: E402

MODSCONFIG = Path(MODS_CONFIG)
EXTS = {".xml", ".cs", ".py", ".md", ".sh", ".csproj", ".lua"}
SKIP_DIRS = {".git", "obj", "bin", "runs"}

def load():
    rows = {"def": [], "packageId": [], "namespace": [], "mod": []}
    with open(MAP, newline="") as f:
        for r in csv.DictReader(f):
            if r["new"] in ("TBD_SPLIT", "") or r["new"] == r["old"]:
                continue
            rows.setdefault(r["kind"], []).append((r["old"], r["new"]))
    for k in rows:
        rows[k].sort(key=lambda p: -len(p[0]))  # longest-first
    return rows

def src_files():
    for p in sorted((ROOT / "src").rglob("*")):
        if p.is_file() and p.suffix in EXTS and not (set(p.parts) & SKIP_DIRS):
            yield p

def build_patterns(rows):
    pats = []
    for old, new in rows["def"]:
        pats.append((re.compile(r"\b%s\b" % re.escape(old)), new, "def"))
    for old, new in rows["packageId"]:
        pats.append((re.compile(re.escape(old), re.I), new, "pkg"))
    for old, new in rows["mod"]:  # path strings in tools/docs
        pats.append((re.compile(re.escape(old)), new, "path"))
    return pats

def ns_patterns(rows):
    return [(re.compile(r"\b%s\b" % re.escape(old)), new)
            for old, new in rows["namespace"]]

def stage_text(apply):
    rows = load()
    pats, nspats = build_patterns(rows), ns_patterns(rows)
    touched, hits = 0, {"def": 0, "pkg": 0, "path": 0, "ns": 0}
    for p in src_files():
        s = orig = p.read_text(encoding="utf-8", errors="replace")
        for rx, new, kind in pats:
            s, n = rx.subn(new, s)
            hits[kind] += n
        if p.suffix == ".cs":
            for rx, new in nspats:
                s, n = rx.subn(new, s)
                hits["ns"] += n
        if s != orig:
            touched += 1
            if apply:
                p.write_text(s, encoding="utf-8")
    print(f"text: {touched} files changed; hits {hits} ({'APPLIED' if apply else 'dry'})")

def stage_folders(apply):
    rows = load()
    for old, new in sorted(rows["mod"]):
        src, dst = ROOT / old, ROOT / new
        if not src.exists():
            print(f"  SKIP (missing) {old}")
            continue
        print(f"  git mv {old} -> {new}")
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, check=True)
    print(f"folders: {'APPLIED' if apply else 'dry'}")

def stage_modsconfig(apply):
    rows = load()
    s = orig = MODSCONFIG.read_text(encoding="utf-8")
    n = 0
    for old, new in rows["packageId"]:
        s, k = re.subn(re.escape(old), new, s, flags=re.I)
        n += k
    print(f"modsconfig: {n} id swaps ({'APPLIED' if apply else 'dry'})")
    if apply and s != orig:
        MODSCONFIG.write_text(s, encoding="utf-8")

if __name__ == "__main__":
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "text"
    apply = "--apply" in sys.argv
    {"text": stage_text, "folders": stage_folders,
     "modsconfig": stage_modsconfig}[stage](apply)
