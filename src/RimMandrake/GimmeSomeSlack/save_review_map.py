"""save_review_map.py -- save the live review map as a keeper savegame and file the sheet beside the mod.

    python.exe src/RimMandrake/GimmeSomeSlack/save_review_map.py [--name RM_gss_review_YYYYMMDD]   (from the repo root)

Owner 2026-10-05: the human review sheet is saved inside the mod's own folder (src/RimMandrake/GimmeSomeSlack/review/) for
quick review later, with a savegame of the review map. Saves stay until he says delete. rimworld/save_game has silently
written the CURRENT slot instead of saveName, so this stats the Saves folder before and after: exactly one NEW file and no
changed one, or it exits 1. Run `human_review.py --build --fresh-map` first (it sweeps hostile pawns off the map).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SHEET_SRC = os.path.join(ROOT, "Transient", "mc_human_review")
REVIEW_DIR = os.path.join(HERE, "review")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="RM_gss_review_%s" % time.strftime("%Y%m%d"))
    a = ap.parse_args()
    B = V.Bridge()
    before = V._saves_stat()
    if a.name + ".rws" in before:
        print("REFUSED: %s.rws already exists (saves stay until he says delete; pass --name)" % a.name)
        return 1
    r = B.call("rimworld/save_game", saveName=a.name)
    time.sleep(3.0)
    after = V._saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    gone = sorted(set(before) - set(after))
    ok = new == [a.name + ".rws"] and not changed and not gone
    print("save: tool=%s new=%s changed=%s gone=%s %s" % (r.get("success"), new, changed, gone, "OK" if ok else "FAIL"))
    if not ok:
        return 1
    os.makedirs(REVIEW_DIR, exist_ok=True)
    for f in ("KEYSHEET.md", "keysheet.html"):
        shutil.copy2(os.path.join(SHEET_SRC, f), os.path.join(REVIEW_DIR, f))
    with open(os.path.join(REVIEW_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write("# GimmeSomeSlack human review\n\nSheet: `keysheet.html` (open it) / `KEYSHEET.md`. Review map savegame: `%s.rws` in the game's "
                "Saves folder (kept until the owner says delete). Rebuild the map with `python.exe src/RimMandrake/GimmeSomeSlack/"
                "human_review.py --build --fresh-map` from the repo root, then `save_review_map.py`.\nSaved %s.\n"
                % (a.name, time.strftime("%Y-%m-%d %H:%M")))
    print("sheet filed: %s" % REVIEW_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
