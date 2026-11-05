#!/usr/bin/env python3
"""Refuse a commit that adds a companion [Tool] the committed snapshot lacks (NIGHTLY_COP_FIX_RED_LMTEZQ_YAXX).

    python3 tool_snapshot_guard.py --staged [ROOT]          git pre-commit: staged .cs vs staged tool_schemas.json
    python3 tool_snapshot_guard.py --pair CS_DIR SNAPSHOT    any directory of .cs against any snapshot file

selftest_lint_calls.py goes red the night after a [Tool] lands in
src/RimMandrake/bridgetools/JawaBench.BridgeTools/ without `tool_schemas.py --supplement-only` (26 tools on
2026-10-10, 2 on 2026-10-26, jawa/debug_action_menu on 2026-11-03): each time a nightly red, an alarm item and
a hand refresh. This moves the check to the commit that causes it. Only the [Tool]s declared in the STAGED .cs
files are checked (a tool already on main is the nightly's business), against the STAGED snapshot.
Exit 0 clean, 1 refused, 2 usage. A crash fails open in the hook (exit > 1).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tool_schemas as T  # noqa: E402

CS_DIR = "src/RimMandrake/bridgetools/JawaBench.BridgeTools/"
SNAP = "src/RimMandrake/Utils/northstar_driver/tool_schemas.json"
FIX = ("python3 src/RimMandrake/Utils/northstar_driver/tool_schemas.py --supplement-only "
       "src/RimMandrake/bridgetools/JawaBench.BridgeTools && git add " + SNAP)


def missing(cs_texts, snapshot_tools):
    """{path: C# text}, set of snapshot tool names -> sorted [(tool, path)] declared in the C# but absent."""
    out = []
    for path, text in sorted(cs_texts.items()):
        out += [(name, path) for name in T.parse_csharp(text) if name not in snapshot_tools]
    return sorted(out)


def _git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, check=True).stdout


def staged(root):
    names = _git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode("utf-8").split("\0")
    cs = [n for n in names if n.startswith(CS_DIR) and n.endswith(".cs")]
    if not cs:
        return []
    texts = {n: _git(root, "show", ":" + n).decode("utf-8", "replace") for n in cs}
    try:
        snap = json.loads(_git(root, "show", ":" + SNAP).decode("utf-8"))
    except subprocess.CalledProcessError:
        snap = {"tools": {}}
    return missing(texts, set(snap.get("tools", {})))


def pair(cs_dir, snapshot):
    texts = {}
    for fn in sorted(os.listdir(cs_dir)):
        if fn.endswith(".cs"):
            with open(os.path.join(cs_dir, fn), encoding="utf-8", errors="replace") as f:
                texts[fn] = f.read()
    with open(snapshot, encoding="utf-8") as f:
        return missing(texts, set(json.load(f).get("tools", {})))


def report(found):
    if not found:
        return 0
    print("pre-commit: REFUSED - %d companion [Tool](s) staged without a tool_schemas.json entry:" % len(found),
          file=sys.stderr)
    for name, path in found[:20]:
        print("  %s  (%s)" % (name, path), file=sys.stderr)
    print("  The nightly selftest_lint_calls.py goes red on this. Refresh the snapshot and stage it:\n    " + FIX,
          file=sys.stderr)
    return 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "--staged":
        return report(staged(argv[2] if len(argv) > 2 else "."))
    if len(argv) == 4 and argv[1] == "--pair":
        return report(pair(argv[2], argv[3]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
