#!/usr/bin/env python3
"""selftest_companion_cover_batchreads.py -- GAMEENV_FIX_PROOFSITE_02DE407A_ITEMS_WAIT: the instance guard, on the
repo's REAL history, for "Tool 'jawa/list_things_batch' not found".

BATCHREADS_BUILD_ROUND_TRIP_CUT (c086d59283, which adds jawa/list_things_batch) ran its live A1 at 2026-11-06T09:17Z on
a game started 08:32Z whose companion was build a9e5d1f6a3 (Player-prev.log: "[JawaBench] ready: 425 tools, build
a9e5d1f6a3f6"). a9e5d1f6a3 does not descend from c086d59283, so the tool was absent; the companion gate that refuses such
a run (LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED 73fd40d031) landed after it. The game started 14:50:07Z runs build
68300cf53fae (430 tools), deployed 14:49:47Z, which descends from c086d59283. What must hold:
  * a clean DLL stamped a9e5d1f6a3 reads STALE against c086d59283 with cover on, and companion_gap says "not deployed"
    (the game phase restages), game-stamped;
  * a clean DLL stamped 68300cf53fae reads FRESH covered_by it, and a game started after its deploy is admitted, one
    started before it is "not deployed".
Needs only git history (both commits are ancestors of every later main), no game folder.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bridgetools"))
import relentless_live as L     # noqa: E402
import companion_identity as CI     # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BUILT = "c086d59283a5cfbc67a236a2b5aeabd6459d155c"     # BATCHREADS_BUILD_ROUND_TRIP_CUT: adds jawa/list_things_batch
OLD = "a9e5d1f6a3f6217e7f671504946a54f9b2f9aca1"       # the 08:32Z game's companion
NEW = "68300cf53fae216f2f3976602097b10d1d399a8a"       # the 14:50Z game's companion
DEPLOYED_NEW, STARTED_NEW = 1793976587, 1793976607     # 14:49:47Z DLL mtime, 14:50:07Z game start
FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append((name, detail))


def fake_dll(d, stamp):
    """A clean build of `stamp`: its embedded hash is the companion sources' hash at that commit (build.py's mark)."""
    h = CI.srchash_at(REPO, stamp)
    p = os.path.join(d, "%s-%s" % (stamp[:8], CI.DLL_NAME))
    with open(p, "wb") as f:
        f.write(b"MZ\x00" + bytes([len(CI.META_KEY)]) + CI.META_KEY.encode() + b"\x40" + h.encode()
                + b"\x00" + ("1.0.0+%s" % stamp).encode("utf-16-le") + b"\x00")
    return p


def main():
    for rev in (BUILT, OLD, NEW):
        if not CI.known(REPO, rev):
            print("UNMEASURED: %s is not in this repo's history" % rev)
            return 2
    check("history: the old companion lacks the batch tools' commit", not CI.descends(REPO, BUILT, OLD))
    check("history: the new companion holds it", CI.descends(REPO, BUILT, NEW))
    with tempfile.TemporaryDirectory() as d:
        old = CI.verdict(fake_dll(d, OLD), REPO, BUILT, cover=True)
        check("old: build stamp read", old.get("build_commit") == OLD, old)
        check("old: STALE against the batch build, cover on", old.get("state") == "STALE" and not old.get("covered_by"),
              old)
        gap = L.companion_gap(dict(old, mtime=DEPLOYED_NEW - 3600), STARTED_NEW)
        check("old: the gate says not deployed, game-stamped (restage)",
              bool(gap) and gap[0].startswith(L.UNDEPLOYED[0]) and gap[1] is True, gap)
        new = CI.verdict(fake_dll(d, NEW), REPO, BUILT, cover=True)
        check("new: FRESH covered by 68300cf", new.get("state") == "FRESH" and new.get("covered_by") == NEW, new)
        check("new: game started after the deploy is admitted",
              L.companion_gap(dict(new, mtime=DEPLOYED_NEW), STARTED_NEW) is None)
        late = L.companion_gap(dict(new, mtime=DEPLOYED_NEW), DEPLOYED_NEW - 60)
        check("new: a game started before the deploy is not deployed",
              bool(late) and late[0].startswith(L.UNDEPLOYED[0]) and late[1] is True, late)
        nocover = CI.verdict(fake_dll(d, NEW), REPO, BUILT, cover=False)
        check("new: cover off reads STALE (the cover rule is what admits it)", nocover.get("state") == "STALE", nocover)
    print("%d failure(s)" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
