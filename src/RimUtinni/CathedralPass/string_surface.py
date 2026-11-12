"""string_surface.py -- the faction-visible string surface of the whole mod tree, and its diff between two commits.

CATHEDRAL_DESCENT_REVEAL_SITE_1 verify: "no faction-visible text changes anywhere (diff the string surface)". The reveal
is scoped to the player (arc spec §5): no faction text, trader chatter or codex-visible artifact may change. This tool
collects every player-facing string (cathedral_arc_lint's text tags, plus rulesStrings/rulesRaw lines) held by a
faction-visible def type, in Defs AND in patches whose xpath targets one, plus every Keyed language string, across src/;
then prints the strings added or removed between two git refs (or the working tree).

  python3 src/RimUtinni/CathedralPass/string_surface.py --base <ref> [--head <ref>|worktree] [--json out.json]
Exit 0 when the surface is unchanged, 1 when it changed (the changed strings are listed), 2 on a read error.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
# what a faction, a trader or a codex shows: faction names/descriptions and their namers, trader kinds and their
# stock labels, pawn kinds a faction fields, the Anomaly codex, research (the in-game knowledge screen), ideo text
FACTION_VISIBLE = {"FactionDef", "TraderKindDef", "PawnKindDef", "EntityCodexEntryDef", "EntityCategoryDef",
                   "ResearchProjectDef", "ResearchTabDef", "IdeoPresetDef", "IdeoPresetCategoryDef", "CultureDef",
                   "MemeDef", "PreceptDef", "RoyalTitleDef", "PawnGroupKindDef"}
NAMER_HINTS = ("faction", "trader", "namer", "settlement", "ideo", "culture")
TEXT_TAGS = {"label", "description", "text", "letterLabel", "letterText", "reportString", "baseInspectLine",
             "jobString", "customLabel", "messageText", "successMessage", "failMessage", "rejectInputMessage",
             "customLetterLabel", "customLetterText", "labelPlural", "pawnSingular", "pawnsPlural", "leaderTitle",
             "fixedName", "labelShort"}
LIST_PARENTS = {"rulesStrings", "rulesRaw", "lines"}


def git_files(ref):
    out = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", ref, "--", "src"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return [p for p in out if p.endswith(".xml")]


def worktree_files():
    out = subprocess.run(["git", "-C", REPO, "ls-files", "--cached", "--others", "--exclude-standard", "--", "src"],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return [p for p in out if p.endswith(".xml")]


def read(ref, path):
    if ref == "worktree":
        try:
            with open(os.path.join(REPO, path), "rb") as f:
                return f.read()
        except OSError:
            return None
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _strings(el, owner):
    parents = {c: p for p in el.iter() for c in p}
    for node in el.iter():
        if not isinstance(node.tag, str) or not (node.text or "").strip():
            continue
        if node.tag in TEXT_TAGS or (node.tag == "li" and parents.get(node) is not None
                                     and parents[node].tag in LIST_PARENTS):
            yield owner, node.tag, node.text.strip()


def surface_of(path, data):
    """[(owner, tag, string)] of one file's faction-visible strings."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []
    out = []
    low = path.lower()
    if "/languages/" in low and "/keyed/" in low:
        for node in root:
            if isinstance(node.tag, str) and (node.text or "").strip():
                out.append(("Keyed", node.tag, node.text.strip()))
        return out
    if root.tag == "Defs":
        for d in root:
            if not isinstance(d.tag, str):
                continue
            tag = d.tag.split(".")[-1]
            name = d.findtext("defName") or d.get("Name") or "?"
            namer = tag == "RulePackDef" and any(h in name.lower() for h in NAMER_HINTS)
            if tag in FACTION_VISIBLE or namer:
                out.extend(_strings(d, "%s/%s" % (tag, name)))
    elif root.tag == "Patch":
        for op in root.iter():
            xp = op.findtext("xpath") if isinstance(op.tag, str) else None
            if xp and any(t in xp for t in FACTION_VISIBLE):
                val = op.find("value")
                if val is not None:
                    out.extend(_strings(val, "patch:" + xp))
    return out


def surface(ref):
    files = worktree_files() if ref == "worktree" else git_files(ref)
    rows = set()
    for p in files:
        data = read(ref, p)
        if data:
            for owner, tag, s in surface_of(p, data):
                rows.add((p, owner, tag, s))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="worktree")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    try:
        base, head = surface(a.base), surface(a.head)
    except subprocess.CalledProcessError as e:
        print("string_surface: git failed: %s" % e, file=sys.stderr)
        return 2
    added, removed = sorted(head - base), sorted(base - head)
    digest = lambda rows: hashlib.sha256("\n".join("\t".join(r) for r in sorted(rows)).encode()).hexdigest()[:16]
    print("string_surface: base %s = %d faction-visible strings (sha %s); head %s = %d (sha %s)"
          % (a.base, len(base), digest(base), a.head, len(head), digest(head)))
    for tag, rows in (("+", added), ("-", removed)):
        for p, owner, t, s in rows:
            print("  %s %s %s <%s> %r" % (tag, p, owner, t, s[:90]))
    print("string_surface: %s (%d added, %d removed)" % ("UNCHANGED" if not added and not removed else "CHANGED",
                                                        len(added), len(removed)))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"base": a.base, "head": a.head, "base_count": len(base), "head_count": len(head),
                       "base_sha": digest(base), "head_sha": digest(head),
                       "added": added, "removed": removed}, f, indent=1)
    return 0 if not added and not removed else 1


if __name__ == "__main__":
    sys.exit(main())
