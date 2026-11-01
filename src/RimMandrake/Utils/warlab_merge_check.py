#!/usr/bin/env python3
"""Proof for ASSAILANT_WARLAB_BUILD_MERGE: one item owns the war lab site, the other is superseded by it, nothing live
still names the superseded id, and the gate order is written once."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SPEC = ROOT / "design/Jawa/worldbuilding/dungeons_arc_spec.md"
OWNER, GONE = "ANCIENT_WAR_LAB_1", "ASSAILANT_DUNGEON_BUILD_1"
# Records of what was true then; a dated log line or audit keeps the name it had.
HISTORY = ("design/RimMandrake/mod_audit/", "design/RimMandrake/gpt_reviews/", "design/RimMandrake/world_remake_2026-10-19/",
           "infrastructure/state/items/VAULT_DUNGEON_BUILD_1.md", "infrastructure/state/items/ASSAILANT_WARLAB_BUILD_MERGE.md",
           "src/RimMandrake/Utils/warlab_merge_check.py", "src/RimMandrake/Utils/pulse/time_ledger_replay/",
           "conversations/", "infrastructure/state/handoffs/", "infrastructure/state/reconcile_manifest_2026-10-07.md",
           f"infrastructure/state/items/{OWNER}.md")  # the last only names where its folded build came from
GATE_CELLS = ["**Reveal**", "**Garrison, if early**", "**The codes**", "**The core socket**"]


def defects(show_gone: str, show_owner: str, live_hits: list[str], spec: str, order_copies: list[str]) -> list[str]:
    out = []
    if "superseded" not in show_gone.splitlines()[0]:
        out.append(f"{GONE} is not superseded: {show_gone.splitlines()[0]}")
    if OWNER not in show_gone:
        out.append(f"{GONE} does not name {OWNER}")
    if "superseded" in show_owner.splitlines()[0] or "dropped" in show_owner.splitlines()[0]:
        out.append(f"{OWNER} is not live")
    if "## folded build" not in show_owner:
        out.append(f"{OWNER} does not carry the folded build")
    out += [f"live reference to {GONE}: {h}" for h in live_hits]
    at = [spec.find(c) for c in GATE_CELLS]
    if -1 in at or at != sorted(at):
        out.append(f"gate order table missing or out of order in the spec: {at}")
    if spec.count("**The gate order") != 1:
        out.append("the gate order heading is not in the spec exactly once")
    out += [f"gate order restated outside §2.3: {c}" for c in order_copies]
    return out


def main() -> int:
    show = lambda i: subprocess.run([sys.executable, "src/RimMandrake/rimflow/cli.py", "show", i], cwd=ROOT,
                                    capture_output=True, text=True).stdout
    grep = subprocess.run(["git", "grep", "-l", GONE], cwd=ROOT, capture_output=True, text=True).stdout.split()
    live = [f for f in grep if not f.startswith(HISTORY) and "/closed/" not in f and "ledger/" not in f
            and not f.startswith("infrastructure/state/queue")]
    copies = subprocess.run(["git", "grep", "-l", "-E", "garrison if early.{0,6}codes"], cwd=ROOT,
                            capture_output=True, text=True).stdout.split()
    copies = [f for f in copies if not f.endswith(("warlab_merge_check.py", "items/ASSAILANT_WARLAB_BUILD_MERGE.md"))
              and "ledger/" not in f
              and "/closed/" not in f and not f.startswith("infrastructure/state/queue")]
    found = defects(show(GONE), show(OWNER), live, SPEC.read_text(), copies)
    print(json.dumps({"defects": found}, indent=1))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
