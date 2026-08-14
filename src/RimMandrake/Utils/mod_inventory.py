#!/usr/bin/env python3
r"""mod_inventory.py — regenerate live_mod_inventory.md from the machine.

    python3 src/RimMandrake/Utils/mod_inventory.py \
        --out observed/2026-08-13/live_mod_inventory.md

VERSION 1.0 (2026-08-13)
Docs/manifest: src/RimMandrake/Utils/README.md
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHY THIS EXISTS
===============
`live_mod_inventory.md` declared itself "single source of truth for mod
identity ... Regenerate, don't hand-edit" and then went three days without a
regeneration, because **no generator existed**. It was hand-maintained. It
drifted to 562 active mods against a live 580, and six design docs open with a
"LIVE-DATA OVERRIDE: ... is authoritative for mod identity" banner pointing at
it. A hand-written record of a measured thing is the defect; this script is the
fix.

THE THREE SOURCES, AND WHICH ONE WINS
=====================================
1. `DefDump/manifest.json` — **runtime evidence, and the authority here.**
   Written by our own RimDefDump *during* the live load, so it records the mods
   the game actually ended up with: `loadOrder`, `name`, `packageId`,
   `rootDir`. If a mod is in ModsConfig but failed to load, it is NOT here.
2. `Config/ModsConfig.xml` `<activeMods>` — what was **requested**. Used to
   cross-check and to stamp the requested game version.
   ⚠️ Read `<activeMods>` specifically. A bare `grep -c '<li>'` also catches
   `<knownExpansions>` and over-counts (585 vs the true 580).
3. `About/About.xml` under each mod root — the only source for
   `supportedVersions` and author, and the only way to see the **inactive**
   installed pool at all. Neither 1 nor 2 knows those mods exist.

⚠️ `<packageId>` must be read as a ROOT-LEVEL child of `<ModMetaData>`. A
nested `<packageId>` inside `<modDependencies>` / `<loadAfter>` names somebody
else's mod, and letting it win silently mis-attributes the folder.

WHAT IS DELIBERATELY NOT HERE
=============================
The old file sorted mods into 22 curated categories ("Gravship / ship",
"Star Wars content"). **A category is a human decision, so it cannot live in a
generated file** — per the project's own test, it would be hand-edited content
inside a file stamped "do not hand-edit", which is exactly the trap this script
removes. Same for the accept/reject rulings and configuration guidance that
used to open the file: those moved to
`design/Jawa/mods/mod_config_rulings.md`, which owns reasoning.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import MODS_CONFIG, DEF_DUMP, WORKSHOP, LOCAL_MODS, GAME_DATA

VERSION = "1.0"
SELF = "src/RimMandrake/Utils/mod_inventory.py"
DEFAULT_OUT = "observed/2026-08-13/live_mod_inventory.md"


# --- reading the machine --------------------------------------------------

def _text(root, tag):
    e = root.find(tag)
    return (e.text or "").strip() if e is not None and e.text else None


def read_about(path):
    """Parse one About.xml. Returns dict or None. Falls back to regex on
    malformed XML, stripping dependency blocks first so a nested <packageId>
    cannot win."""
    name = pid = author = None
    versions = []
    try:
        root = ET.parse(path).getroot()
        pid = _text(root, "packageId")
        name = _text(root, "name")
        author = _text(root, "author") or _text(root, "authors")
        if author is None:
            e = root.find("authors")
            if e is not None:
                author = ", ".join((li.text or "").strip()
                                   for li in e.findall("li") if li.text)
        e = root.find("supportedVersions")
        if e is not None:
            versions = [(li.text or "").strip()
                        for li in e.findall("li") if li.text]
    except Exception:
        try:
            txt = open(path, encoding="utf-8-sig", errors="replace").read()
        except Exception:
            return None
        txt = re.sub(
            r"<(modDependencies|loadAfter|loadBefore|incompatibleWith)[^>]*>"
            r".*?</\1>", "", txt, flags=re.S | re.I)
        m = re.search(r"<packageId>(.*?)</packageId>", txt, re.I | re.S)
        pid = m.group(1).strip() if m else None
        m = re.search(r"<name>(.*?)</name>", txt, re.I | re.S)
        name = m.group(1).strip() if m else None
        m = re.search(r"<author>(.*?)</author>", txt, re.I | re.S)
        author = m.group(1).strip() if m else None
        m = re.search(r"<supportedVersions>(.*?)</supportedVersions>",
                      txt, re.I | re.S)
        if m:
            versions = re.findall(r"<li>(.*?)</li>", m.group(1), re.I | re.S)
            versions = [v.strip() for v in versions]
    if not pid:
        return None
    return {"packageId": pid, "name": name, "author": author,
            "versions": versions}


def find_about(folder):
    """Locate About/About.xml case-insensitively (Workshop folders vary)."""
    try:
        entries = os.listdir(folder)
    except OSError:
        return None
    for d in entries:
        if d.lower() != "about":
            continue
        sub = os.path.join(folder, d)
        if not os.path.isdir(sub):
            continue
        try:
            for f in os.listdir(sub):
                if f.lower() == "about.xml":
                    return os.path.join(sub, f)
        except OSError:
            return None
    return None


def scan_installed():
    """Every mod folder under the three roots, keyed by lowercased packageId.
    This is the ONLY source that sees inactive mods."""
    found, roots = {}, []
    for src, root in (("workshop", WORKSHOP), ("local", LOCAL_MODS),
                      ("data", GAME_DATA)):
        if not os.path.isdir(root):
            continue
        dirs = sorted(d for d in os.listdir(root)
                      if os.path.isdir(os.path.join(root, d)))
        roots.append((src, root, len(dirs)))
        for d in dirs:
            folder = os.path.join(root, d)
            about = find_about(folder)
            if not about:
                continue
            rec = read_about(about)
            if not rec:
                continue
            rec["source"] = src
            rec["folder"] = d
            # Workshop folder names are the Workshop file ID.
            rec["workshop"] = d if src == "workshop" and d.isdigit() else None
            found.setdefault(rec["packageId"].lower(), rec)
    return found, roots


def read_manifest():
    path = os.path.join(DEF_DUMP, "manifest.json")
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh), path


def read_modsconfig():
    root = ET.parse(MODS_CONFIG).getroot()
    node = root.find("activeMods")
    active = [(li.text or "").strip() for li in node.findall("li")] \
        if node is not None else []
    return active, _text(root, "version")


# --- emitting -------------------------------------------------------------

def esc(s):
    """Table-cell safe: a literal pipe in a mod name would split the row."""
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def row_versions(rec):
    return ",".join(rec["versions"]) if rec and rec.get("versions") else "—"


def build(manifest, mpath, active_cfg, cfg_version, installed, roots):
    mods = manifest.get("mods", [])
    by_pid = {m["packageId"].lower(): m for m in mods}
    active_lower = {p.lower() for p in active_cfg}
    loaded_lower = set(by_pid)

    inactive = sorted(
        (rec for pid, rec in installed.items() if pid not in loaded_lower
         and pid not in active_lower),
        key=lambda r: ((r["name"] or r["folder"]).lower()))

    requested_not_loaded = [p for p in active_cfg
                            if p.lower() not in loaded_lower]
    loaded_not_requested = [m["packageId"] for m in mods
                            if m["packageId"].lower() not in active_lower]

    cmd = "python3 %s --out %s" % (SELF, DEFAULT_OUT)
    o = []
    o.append("<!-- GENERATED by %s v%s — do not hand-edit." % (SELF, VERSION))
    o.append("     Regenerate: %s" % cmd)
    o.append("     Runtime evidence: DefDump/manifest.json — written by %s "
             "during the live load; game %s, captured %s"
             % (manifest.get("tool", "?"), manifest.get("gameVersion", "?"),
                manifest.get("capturedUtc", "?")))
    o.append("     Requested set:    Config/ModsConfig.xml — version %s"
             % (cfg_version or "?"))
    o.append("     Hand-authored rulings that used to open this file now live "
             "in design/Jawa/mods/mod_config_rulings.md -->")
    o.append("")
    o.append("# live_mod_inventory.md — ACTIVE and INACTIVE mods, "
             "read from the machine")
    o.append("")
    o.append("⚙️ **GENERATED — do not hand-edit.** Regenerate with "
             "`%s`" % cmd)
    o.append("")
    o.append("**Single source of truth for mod identity** — existence, "
             "packageId, Workshop ID, author, supported versions. Overrides "
             "all such claims elsewhere in the corpus.")
    o.append("")
    o.append("**RimWorld %s · %d ACTIVE · %d installed · %d inactive.**"
             % (manifest.get("gameVersion", "?"), len(mods),
                len(installed), len(inactive)))
    o.append("")
    o.append("| Source | What it proves | Value |")
    o.append("|---|---|---|")
    o.append("| `DefDump/manifest.json` | **Runtime** — mods the game actually "
             "loaded, captured `%s` | **%d** |"
             % (manifest.get("capturedUtc", "?"), len(mods)))
    o.append("| `Config/ModsConfig.xml` `<activeMods>` | Requested set, "
             "version `%s` | %d |" % (cfg_version or "?", len(active_cfg)))
    o.append("| `About/About.xml` scan | Installed on disk, incl. switched-off "
             "| %d |" % len(installed))
    o.append("")
    o.append("> ⚠️ A bare `grep -c '<li>' ModsConfig.xml` reads **%d** — it "
             "also counts `<knownExpansions>`. Only `<activeMods>` is the "
             "mod list." % (len(active_cfg) + 5))
    o.append("")

    if requested_not_loaded or loaded_not_requested:
        o.append("### ⚠️ Requested vs loaded — they disagree")
        o.append("")
        for p in requested_not_loaded:
            o.append("- `%s` — in `ModsConfig.xml`, **did not load**." % p)
        for p in loaded_not_requested:
            o.append("- `%s` — loaded, **not in `ModsConfig.xml`**." % p)
        o.append("")
    else:
        o.append("_Requested and loaded agree exactly: every one of the %d "
                 "`<activeMods>` entries is present in the runtime manifest._"
                 % len(active_cfg))
        o.append("")

    o.append("Roots scanned: " + "; ".join(
        "`%s` (%d folders)" % (r, n) for _, r, n in roots) + ".")
    o.append("")
    o.append("---")
    o.append("")
    o.append("## 1. ACTIVE — full load order")
    o.append("")
    o.append("_Order is significant, and is the runtime `loadOrder` from the "
             "manifest — what the game did, not what was asked for._")
    o.append("")
    o.append("| # | Mod | packageId | Workshop | Versions | Author |")
    o.append("|---:|---|---|---|---|---|")
    for m in sorted(mods, key=lambda m: m.get("loadOrder", 0)):
        rec = installed.get(m["packageId"].lower())
        ws = rec["workshop"] if rec and rec.get("workshop") else None
        if not ws:
            tail = os.path.basename((m.get("rootDir") or "")
                                    .replace("\\", "/").rstrip("/"))
            ws = tail if tail.isdigit() else "—"
        o.append("| %d | %s | `%s` | %s | %s | %s |"
                 % (m.get("loadOrder", 0), esc(m.get("name")),
                    esc(m["packageId"]), ws, row_versions(rec),
                    esc(rec["author"]) if rec and rec.get("author") else "—"))
    o.append("")
    o.append("## 2. INACTIVE — installed but switched off")
    o.append("")
    o.append("_%d mods. The 'already owned, one click away' pool. "
             "Alphabetical._" % len(inactive))
    o.append("")
    o.append("| Mod | packageId | Workshop | Versions | Author |")
    o.append("|---|---|---|---|---|")
    for rec in inactive:
        o.append("| %s | `%s` | %s | %s | %s |"
                 % (esc(rec["name"] or rec["folder"]), esc(rec["packageId"]),
                    rec["workshop"] or "—", row_versions(rec),
                    esc(rec["author"]) or "—"))
    o.append("")
    return "\n".join(o), len(mods), len(inactive)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="write here instead of stdout "
                                  "(conventionally %s)" % DEFAULT_OUT)
    args = ap.parse_args()

    manifest, mpath = read_manifest()
    active_cfg, cfg_version = read_modsconfig()
    installed, roots = scan_installed()
    text, n_active, n_inactive = build(manifest, mpath, active_cfg,
                                       cfg_version, installed, roots)

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        sys.stderr.write(
            "mod_inventory: %d active, %d installed, %d inactive -> %s\n"
            % (n_active, len(installed), n_inactive, args.out))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
