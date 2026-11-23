#!/usr/bin/env python3
"""A sheet's prefill follows the owner's NEWEST keep, whatever stamp and subject key the ruling carries.

Page: design/specs/2026-11-22-art-sheet-prefill/boundary.md (one test per promise, named t_<promise>).

A ruling written by an art install carries only `ts`, names one `target.sha` and has an EMPTY subject_key; a ruling
ingested from a sheet carries `at` and `target.shas`. prefill_for sorted on `at` alone and read only `target.shas`, and
the builder handed it only subject_rulings(), so an install keep never counted: the 2026-11-22 FlowWorks look-options
sheet prefilled the Modern tank slot to the red render he kept on 2026-10-21 (column I) instead of the white leg tank he
picked by card on 2026-10-22 and that ships (column H). Returned untouched, that sheet would have reinstalled the red tank.
Seen red on base 9a3249183c (1 of 3, then graphic_rulings missing); green on the fix.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402

fails = 0


def check(cond, what):
    global fails
    print(("PASS " if cond else "FAIL ") + what)
    fails += 0 if cond else 1


RED = {"letter": "I", "kind": "artpipe", "faces": {"single": "red"}}
WHITE = {"letter": "H", "kind": "live", "faces": {"single": "white"}, "winner": True}
OLD_SHEET_KEEP = {"verdict": "keep", "trust": "ruled", "by": "owner", "at": "2026-10-21T23:27:12-0700",
                  "ts": "2026-10-21T23:27:35-0700", "target": {"shas": ["red"]}, "subject_key": "liquidtank"}
NEW_INSTALL_KEEP = {"verdict": "keep", "trust": "ruled", "by": "owner", "ts": "2026-10-22T20:13:09-0700",
                    "target": {"sha": "white"}, "subject_key": ""}


class FakeIndex:
    """The two artledger.Index lookups graphic_rulings reads."""

    def __init__(self, rulings):
        self.rulings = rulings
        self.rulings_by_sha = {}
        for r in rulings:
            t = r.get("target") or {}
            for sh in list(t.get("shas") or []) + ([t["sha"]] if t.get("sha") else []):
                self.rulings_by_sha.setdefault(sh, []).append(r)

    def subject_rulings(self, keys):
        return [r for r in self.rulings if (r.get("subject_key") or "") in keys]


def t_newest_keep_wins_whatever_stamp():
    letter, why, _ = A.prefill_for({"cols": [WHITE, RED]}, [OLD_SHEET_KEEP, NEW_INSTALL_KEEP])
    check(letter == "H", f"newer install keep (ts only, target.sha) beats an older sheet keep: got {letter} ({why})")
    letter, _, _ = A.prefill_for({"cols": [WHITE, RED]}, [OLD_SHEET_KEEP])
    check(letter == "I", f"with only the old keep, the old keep still prefills: got {letter}")
    newer = dict(OLD_SHEET_KEEP, at="2026-10-23T09:00:00-0700", ts="2026-10-23T09:00:01-0700")
    letter, _, _ = A.prefill_for({"cols": [WHITE, RED]}, [newer, NEW_INSTALL_KEEP])
    check(letter == "I", f"a sheet keep newer than the install keep still wins: got {letter}")


def t_install_keep_reaches_the_prefill():
    idx = FakeIndex([OLD_SHEET_KEEP, NEW_INSTALL_KEEP])
    rul = A.graphic_rulings(idx, idx.subject_rulings({"liquidtank"}), {"cols": [WHITE, RED]})
    letter, why, _ = A.prefill_for({"cols": [WHITE, RED]}, rul)
    check(letter == "H", f"an install keep with no subject_key still reaches the prefill: got {letter} ({why})")
    check(sum(1 for r in rul if r is OLD_SHEET_KEEP) == 1, "a ruling found both ways is listed once")


def t_live_modern_tank_prefills_what_ships():
    import artledger as L
    ship = "a7dd4a39e686b749c46438b1c7d6531fb193d968848c461fd0018eae3f4c50b3"
    red = "4735456ab540ba7657350f37e3f7645509185e791eeb40a66330a6288eda5d65"
    live = L.Index()
    if ship not in live.rulings_by_sha or red not in live.rulings_by_sha:
        check(False, "the 2026-10-21/22 Modern tank rulings are not in the art ledger (UNMEASURED)")
        return
    cols = [{"letter": "H", "kind": "live", "faces": {"single": ship}, "winner": True},
            {"letter": "I", "kind": "artpipe", "faces": {"single": red}}]
    rul = A.graphic_rulings(live, live.subject_rulings({"liquidtank"}), {"cols": cols})
    letter, why, _ = A.prefill_for({"cols": cols}, rul)
    check(letter == "H", f"live ledger: Modern tank prefill is the shipped white tank: got {letter} ({why})")


def t_newest_keep_wins_across_time_zones():
    # fresh reader 2026-11-22: sheet `at` stamps are UTC (Z), install `ts` stamps are local (-0700); a string compare
    # ranked a sheet keep at 23:00Z (16:00 local) above an install keep at 20:00 local, which is 4 hours newer
    sheet = dict(OLD_SHEET_KEEP, at="2026-10-21T23:00:00Z", ts="2026-10-21T16:00:05-0700")
    install = dict(NEW_INSTALL_KEEP, ts="2026-10-21T20:00:00-0700")
    letter, why, _ = A.prefill_for({"cols": [WHITE, RED]}, [sheet, install])
    check(letter == "H", f"newest-keep-wins-across-time-zones: a local-time install keep 4 h newer than a UTC sheet keep wins: got {letter} ({why})")


def t_released_keep_never_prefills():
    released = dict(NEW_INSTALL_KEEP, id="k_white")
    release = {"verdict": "release", "by": "owner", "releases": "k_white", "target": {"sha": "white"}, "subject_key": "",
               "ts": "2026-10-23T10:00:00-0700"}
    idx = FakeIndex([OLD_SHEET_KEEP, released, release])
    rul = A.graphic_rulings(idx, idx.subject_rulings({"liquidtank"}), {"cols": [WHITE, RED]})
    letter, why, _ = A.prefill_for({"cols": [WHITE, RED]}, rul)
    check(letter == "I", f"released-keep-never-prefills: a released newer keep is skipped, the older live keep prefills: got {letter} ({why})")


def main():
    t_newest_keep_wins_whatever_stamp()
    t_install_keep_reaches_the_prefill()
    t_live_modern_tank_prefills_what_ships()
    t_newest_keep_wins_across_time_zones()
    t_released_keep_never_prefills()
    print(f"{8 - fails}/8 passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
