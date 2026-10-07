#!/usr/bin/env python3
"""L1 batch manifest generator.

Reads `rimflow next --acceptance --seat FOUNDRY`, takes every L1 criterion, and maps it to the
"DefType/DefName" strings jawa/get_defs should resolve (get_defs takes `defs` as a STRING, never a
list). Names come from the criterion text (confidence NAMED) and, failing that, from the item prose
(confidence PROSE). Each name is cross-checked offline against src/ XML parsed as elements.

Usage: python3 src/RimMandrake/Utils/l1_batch_manifest.py [--json out.json] [--report out.md]
Parse failures are reported UNMEASURED, never as zero.
"""
import json, re, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ITEMS = ROOT / "infrastructure/state/items"
CRIT = re.compile(r"^\s+(\w+)\s+(L1)\s+(.*)$")
ITEM = re.compile(r"^([A-Z][A-Z0-9_]+_\d+)\s+\[")
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]{4,}")
OUR = re.compile(r"^(RM|RSW|RUT)_")
LIVE_HINTS = [("tool list", r"tool list|appear in the live|tools? (appear|answer)"),
              ("log", r"Player\.log|log shows|log is clean"),
              ("settings", r"Mod Settings|LassoSpawn"),
              ("state-read", r"state-read|debug_action_yielders|spawn_pawn|projectile_damage|shader|flora_spawns|checks? pass|cherrypicker")]


def build_index():
    idx, failed, nfiles = {}, [], 0
    for p in ROOT.joinpath("src").rglob("*.xml"):
        nfiles += 1
        try:
            root = ET.parse(p).getroot()
        except Exception as e:  # UNMEASURED, not zero
            failed.append((str(p.relative_to(ROOT)), str(e)[:80]))
            continue
        if root.tag != "Defs":
            continue
        for el in root:
            dn = el.find("defName")
            if dn is not None and dn.text:
                idx.setdefault(dn.text.strip(), []).append((el.tag, str(p.relative_to(ROOT))))
    return idx, failed, nfiles


def acceptance():
    out = subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/rimflow/cli.py"), "next",
                          "--acceptance", "--seat", "FOUNDRY"], capture_output=True, text=True, cwd=ROOT).stdout
    cur, rows, sec = None, [], None
    for line in out.splitlines():
        if line.startswith("## "):
            sec = line.split()[1]
            continue
        if sec != "L1":
            continue
        m = ITEM.match(line)
        if m:
            cur = m.group(1)
            continue
        m = CRIT.match(line)
        if m and cur:
            rows.append((cur, m.group(1), m.group(3).strip()))
    return rows


def main():
    idx, failed, nfiles = build_index()
    rows = acceptance()
    prose_cache, manifest = {}, []
    for item, cid, text in rows:
        if item not in prose_cache:
            f = ITEMS / f"{item}.md"
            prose_cache[item] = f.read_text(errors="replace") if f.exists() else None
        prose = prose_cache[item]
        named = sorted({t for t in TOKEN.findall(text) if t in idx})
        missing = sorted({t for t in TOKEN.findall(text) if OUR.match(t) and t not in idx})
        src, names = "NAMED", named
        if not named and prose:
            names = sorted({t for t in TOKEN.findall(prose) if t in idx and OUR.match(t)})[:40]
            src = "PROSE" if names else "NONE"
        elif not prose and not named:
            src = "NONE"
        defs = [f"{idx[n][0][0]}/{n}" for n in names]
        live = [h for h, rx in LIVE_HINTS if re.search(rx, text, re.I)]
        is_defs = bool(re.search(r"resolve|get_defs|defs?\b", text, re.I)) and not live
        if is_defs and defs and not missing:
            status = "OFFLINE_PRESENT" if src == "NAMED" else "OFFLINE_PRESENT_PROSE_DERIVED"
        elif is_defs and (missing or not defs):
            status = "DEFS_UNRESOLVED_OFFLINE" if missing else "DEFS_NO_NAMES_FOUND"
        else:
            status = "NEEDS_LIVE"
        manifest.append(dict(item=item, criterion=cid, text=text, status=status, source=src,
                             defs=defs, missing=missing, live_kind=live,
                             multi_type=[n for n in names if len({t for t, _ in idx[n]}) > 1]))
    # sanity probe
    probe = next((n for n in idx if n.startswith("RM_")), None)
    probe_ok = probe in idx and "RM_ZZZ_NOT_A_DEF" not in idx and len(idx) > 500
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else "Transient/l1_manifest.json"
    rp = args[args.index("--report") + 1] if "--report" in args else "Transient/l1_manifest_report.md"
    (ROOT / jp).write_text(json.dumps(manifest, indent=1))
    from collections import Counter
    c = Counter(m["status"] for m in manifest)
    L = ["# L1 manifest report", "",
         f"Criteria: {len(manifest)} across {len({m['item'] for m in manifest})} items. "
         f"Index: {len(idx)} defNames from {nfiles} XML files; {len(failed)} parse failures (UNMEASURED).",
         f"Sanity probe: {'PASS' if probe_ok else 'FAIL'} ({probe} present, fake name absent). "
         "get_defs call form: `defs` = single string \"DefType/DefName\" (one call per def).",
         "", "Offline-present means the def exists in src/ XML; the live get_defs read is still owed "
         "(deploy state unproven offline).", ""]
    for k, v in sorted(c.items()):
        L.append(f"- {k}: {v}")
    for st in ["OFFLINE_PRESENT", "OFFLINE_PRESENT_PROSE_DERIVED", "DEFS_UNRESOLVED_OFFLINE", "DEFS_NO_NAMES_FOUND", "NEEDS_LIVE"]:
        L += ["", f"## {st}"]
        for m in manifest:
            if m["status"] != st:
                continue
            extra = f" defs={len(m['defs'])}" if m["defs"] else ""
            extra += f" MISSING={m['missing']}" if m["missing"] else ""
            extra += f" live={m['live_kind']}" if m["live_kind"] else ""
            L.append(f"- {m['item']} {m['criterion']}{extra} — {m['text'][:90]}")
    if failed:
        L += ["", "## XML parse failures (UNMEASURED)"] + [f"- {a}: {b}" for a, b in failed[:40]]
    (ROOT / rp).write_text("\n".join(L) + "\n")
    print(dict(c), "probe", probe_ok, "parsefail", len(failed))


if __name__ == "__main__":
    main()
