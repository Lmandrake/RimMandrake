#!/usr/bin/env python3
"""Selftest for what is left of the pulse package's pulse.py and pulse_core.py: the deploy checkout's updater
(`pulse.py update`), the strict JSONL reader, and the owner-ask fold streams.py counts (owner_rulings, ask_class,
ask_addressee). The dashboard's own checks went with it (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES).
"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_pulse_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="pulse_selftest_")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse_core as pc  # noqa: E402

NOW = 1_791_500_000.0
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)




def le(ev, iid, ago, **kw):
    return {"event": ev, "id": iid, "seat": "FOUNDRY", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - ago)),
            "tsn": int((NOW - ago) * 1e9), **kw}


def fi(iid, ago, title=None, **kw):   # a `file` rimflow's replay accepts (the to-rule rows come from its fold)
    return le("file", iid, ago, title=title or iid.lower().replace("_", " ").rstrip(" 1"), kind="build",
              **{"for": "FOUNDRY", **kw})



def raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True



with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    check("strict jsonl: a missing log nobody wrote yet is a valid empty",
          pc.read_jsonl_tail(d / "none.jsonl", strict=True) == [])
    check("strict jsonl: a missing REQUIRED file raises", raises(lambda: pc.read_jsonl_tail(d / "none.jsonl", strict=True,
                                                                                          allow_missing=False)))
    (d / "junk.jsonl").write_text("not json\nnor this\n")
    check("strict jsonl: a file with lines but none parseable raises", raises(lambda: pc.read_jsonl_tail(d / "junk.jsonl", strict=True)))
    check("lenient jsonl (non-source reads) still answers empty", pc.read_jsonl_tail(d / "junk.jsonl") == [])
    (d / "torn.jsonl").write_text('{"a": 1}\n{"b": ')
    check("strict jsonl: one torn line beside good ones is skipped, not raised",
          pc.read_jsonl_tail(d / "torn.jsonl", strict=True) == [{"a": 1}])

# to rule = rimflow's own projection (open AND needs == owner)
TR = [fi("BUILT_1", 900), le("needs", "BUILT_1", 800, to="owner", reason="decide"),
      le("implemented", "BUILT_1", 700, sha="abc1234", criteria=[{"id": "A1", "level": "L2", "text": "t"}], needs="bridge"),
      fi("BORN_1", 600, needs="owner"),
      fi("DROPPED_1", 600, needs="owner"), le("drop", "DROPPED_1", 500, reason="moot"),
      fi("ASKED_TWICE_1", 5000), le("needs", "ASKED_TWICE_1", 4000, to="owner", reason="first"),
      le("note", "ASKED_TWICE_1", 3000, text="still thinking"),
      le("needs", "ASKED_TWICE_1", 2000, to="owner", reason="again")]
check("a clone holding the same event twice (merge=union) still folds to one item",
      pc.owner_rulings(pc._model().canonical_order(TR + TR)).keys() == pc.owner_rulings(TR).keys())

# a look or a fact never masquerades as a ruling
AQ = [fi("CARD_ANSWERED", 900), le("needs", "CARD_ANSWERED", 800, to="owner", reason="which look, A or B?"),
      le("note", "CARD_ANSWERED", 700, text="he picked B", byCard="Which look? → B"),
      fi("WORDS_ANSWERED", 900), le("needs", "WORDS_ANSWERED", 800, to="owner", reason="keep or cut?"),
      le("note", "WORDS_ANSWERED", 600, text="relay", ownerSaid="Cut it."),
      fi("REASKED", 900), le("needs", "REASKED", 800, to="owner", reason="first question"),
      le("note", "REASKED", 700, text="r", ownerSaid="yes"),
      le("needs", "REASKED", 600, to="owner", reason="a second question"),
      fi("OLD_WORDS", 900, ownerSaid="file this and ask me", needs="owner"),
      fi("PLAIN_RULE", 900), le("needs", "PLAIN_RULE", 800, to="owner", reason="decide the cap"),
      fi("A_LOOK", 900), le("needs", "A_LOOK", 800, to="owner", reason="only the L4 in-situ look remains (LOOK, not a ruling)", evidence="Transient/x_sheet.png"),
      fi("L4_ONLY", 900), le("implemented", "L4_ONLY", 800, sha="abc1234", needs="owner", evidence="Transient/y_sheet.png",
                             criteria=[{"id": "A1", "level": "L4", "text": "owner opens the rendered sheet and glances at it"}]),
      fi("A_FACT", 900, title="Second test PC: needs its name/address"),
      le("needs", "A_FACT", 800, to="owner", reason="waiting on him"),
      le("file", "A_DECISION", 900, kind="decision", title="walk the sheet and decide", **{"for": "FOUNDRY"}),
      le("needs", "A_DECISION", 800, to="owner", reason="sheet is up"),
      fi("PARKED", 900), le("needs", "PARKED", 800, to="owner", reason="review the list"),
      le("block", "PARKED", 700, reason="later, in the normalization pass", ownerSaid="(1) later"),
      fi("UNPARKED", 900), le("needs", "UNPARKED", 850, to="owner", reason="review it"),
      le("block", "UNPARKED", 800, reason="later"), le("unblock", "UNPARKED", 500)]
check("'LOOK, not a ruling' is a look by class (owner 2026-10-23)", pc.owner_rulings(AQ)["A_LOOK"]["class"] == "look",
      pc.owner_rulings(AQ).get("A_LOOK"))
check("an item owing only an L4 criterion is a look by class", pc.owner_rulings(AQ)["L4_ONLY"]["class"] == "look",
      pc.owner_rulings(AQ).get("L4_ONLY"))
_W = lambda **kw: type("I", (), {"title": kw.get("t", ""), "kind": kw.get("k", "art"), "owed_levels": lambda self: [],
                               "criteria": kw.get("c", []), "outstanding": {c["id"] for c in kw.get("c", [])}})()
check("a live in-game walkthrough is class 'walk', never a look (owner 2026-10-23)",
      pc.ask_class(_W(t="Walk the ponds in game with him"), {"reason": "joint walkthrough"})[0] == "walk"
      and pc.ask_class(_W(c=[{"id": "A4", "level": "L4", "text": "owner looks at both in game"}]), {"reason": ""})[0] == "walk",
      pc.ask_class(_W(t="Walk the ponds in game"), {"reason": ""}))
check("a sheet or picture to open stays a look", pc.ask_class(_W(t="Water art sheet"), {"reason": "look: sheet"})[0] == "look")
check("a verb is not a fact: 'address the drift' / 'provide feedback' stay rulings",
      [pc.ask_class(type("I", (), {"title": t, "kind": "task", "owed_levels": lambda self: []})(), {"reason": ""})[0]
       for t in ("address the drift", "provide feedback on X")] == ["rule", "rule"])

# a "later - until he asks" filed from his own card is no question
LT = [fi("LATER_CARD", 900, title="Later: what a weeping peak DOES - not started until he asks", byCard="Look only: they weep (wire the rules later)",
         needs="owner"),
      fi("CARD_ASK", 900, title="Pick the cap", byCard="Which cap? -> 3", needs="owner"),
      fi("LATER_REASKED", 900, title="Later: tooltip", byCard="Look only (later)", needs="owner"),
      le("needs", "LATER_REASKED", 800, to="owner", reason="now he asked for it")]
lr = pc.owner_rulings(LT)
check("an item filed from his card as 'later / until he asks' is not a to-rule row", "LATER_CARD" not in lr, sorted(lr))
check("a card-filed ask with no 'later' stays an ask; a fresh `needs --to owner` re-asks the later one",
      "CARD_ASK" in lr and "LATER_REASKED" in lr, sorted(lr))


# --- only asks addressed to HIM reach his list (owner 2026-10-25: "do NOT tell me about pending questions that
# aren't for the user"). needs=owner alone is not an address; unknown is counted in one dim line, never shown as his.
AD = [fi("ADDR_OWNER_WORDS", 900, title="Pick the herd cap", ownerSaid="ask me which cap", needs="owner"),
      fi("ADDR_OWNER_TEXT", 900), le("needs", "ADDR_OWNER_TEXT", 800, to="owner", reason="owner decides the cap"),
      fi("ADDR_AGENT", 900, title="Pipe bore: which width?", **{"for": "BENCH"}),
      le("needs", "ADDR_AGENT", 800, to="owner", reason="ask BENCH which bore the GSS spec wants", seat="BENCH"),
      fi("ADDR_JUDGE", 900), le("needs", "ADDR_JUDGE", 800, to="owner", reason="agent: delegated art judge call, round 2"),
      fi("ADDR_UNKNOWN", 900, title="Durrok widths uncarried"), le("needs", "ADDR_UNKNOWN", 800, to="owner",
                                                                   reason="measured drawSize 2 vs ruled 6"),
      fi("ADDR_MENTION", 900, title="Ladder text: art redrawn (owner 2026-10-23 redraw), def text still wood"),
      le("needs", "ADDR_MENTION", 800, to="owner", reason="reconcile")]
_has_addr = hasattr(pc, "ask_addressee")
ad_r = pc.owner_rulings(AD)
check("addressee: his words on the filing / 'owner decides' are his; 'ask BENCH' and 'agent:' are an agent's; "
      "nothing said (or a bare provenance mention of the owner) is unknown",
      {k: v.get("addressee") for k, v in ad_r.items()} == {"ADDR_OWNER_WORDS": "owner", "ADDR_OWNER_TEXT": "owner",
                                                           "ADDR_AGENT": "agent", "ADDR_JUDGE": "agent",
                                                           "ADDR_UNKNOWN": "unknown", "ADDR_MENTION": "unknown"},
      {k: (v.get("addressee"), v.get("addressee_why")) for k, v in ad_r.items()})
check("addressee: the OWNER seat, a --for OWNER item and an L4-only item are his by structure", _has_addr and
      pc.ask_addressee(_W(), {"seat": "OWNER"})[0] == "owner"
      and pc.ask_addressee(_W(), {"seat": "BENCH"}, {"for": "OWNER"})[0] == "owner"
      and pc.ask_addressee(type("I", (), {"title": "x", "owed_levels": lambda self: ["L4"]})(), {"seat": "BENCH"})[0] == "owner"
      and pc.ask_addressee(_W(), {"seat": "BENCH", "reason": "sheet up"})[0] == "unknown")

import pulse as pl  # noqa: E402
check("update refuses a seat clone (never pull another agent's working tree)",
      raises(lambda: pl.update_code(pc.CLONES[0])))

# --- PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT: a real git checkout whose pull outruns the budget -----------------
import subprocess as _sp  # noqa: E402
with tempfile.TemporaryDirectory() as d:
    origin, deploy, bindir = Path(d) / "origin", Path(d) / "deploy", Path(d) / "bin"
    def _g(cwd, *a):
        return _sp.run(["git", "-C", str(cwd), *a], check=True, capture_output=True, text=True).stdout.strip()
    origin.mkdir()
    _g(origin, "init", "-q", "-b", "main")
    _g(origin, "config", "user.email", "t@t"); _g(origin, "config", "user.name", "t")
    (origin / "f").write_text("1")
    _g(origin, "add", "f"); _g(origin, "commit", "-qm", "one")
    _sp.run(["git", "clone", "-q", str(origin), str(deploy)], check=True)
    real_git = _sp.run(["which", "git"], capture_output=True, text=True).stdout.strip()
    bindir.mkdir()
    (bindir / "git").write_text(f'#!/bin/sh\ncase " $* " in *" pull "*) exec sleep 5;; esac\nexec {real_git} "$@"\n')
    (bindir / "git").chmod(0o755)
    stamp = deploy / ".git" / pl.UPDATE_STAMP
    good = pl.update_code(deploy)
    check("a good pass reports the sha and stamps the checkout", good.get("changed") is False and stamp.exists(), good)
    path = os.environ["PATH"]
    os.environ["PATH"] = f"{bindir}:{path}"
    try:
        t0 = time.monotonic()
        skip = pl.update_code(deploy, timeout=1.5)
        took = time.monotonic() - t0
        check("a pull past its budget is a skip, not an exception", skip.get("skipped") is True and took < 4, (skip, took))
        os.utime(stamp, (time.time() - 7200, time.time() - 7200))
        check("a skip past the limit with no good pass fails loud (a silent skip would hide a dead deploy)",
              raises(lambda: pl.update_code(deploy, timeout=1.5)))
        stamp.unlink()
        check("a skip with no stamp at all fails loud", raises(lambda: pl.update_code(deploy, timeout=1.5)))
    finally:
        os.environ["PATH"] = path
    (bindir / "git").unlink()
    (origin / "f").write_text("2")
    _g(origin, "commit", "-qam", "two")
    moved = pl.update_code(deploy)
    check("the pass after a skip moves the checkout and restamps it", moved.get("changed") is True and stamp.exists(), moved)
    (bindir / "git").write_text(f'#!/bin/sh\ncase " $* " in *" pull "*) echo nope >&2; exit 1;; esac\nexec {real_git} "$@"\n')
    (bindir / "git").chmod(0o755)
    os.environ["PATH"] = f"{bindir}:{path}"
    try:
        check("a pull that fails (not a timeout) still fails the unit", raises(lambda: pl.update_code(deploy)))
    finally:
        os.environ["PATH"] = path
    # PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN: a pull that died mid-checkout left origin's blobs in the tree, HEAD unmoved
    (origin / "f").write_text("3"); (origin / "g").write_text("new"); (origin / "h").write_text("gone")
    _g(origin, "add", "g", "h"); _g(origin, "commit", "-qam", "three")
    pl.update_code(deploy)
    (origin / "f").write_text("4"); _g(origin, "rm", "-q", "h"); (origin / "k").write_text("k")
    _g(origin, "add", "k"); _g(origin, "commit", "-qam", "four")
    _g(deploy, "fetch", "-q", "origin")
    (deploy / "f").write_text("4"); (deploy / "h").unlink(); (deploy / "k").write_text("k")   # git's half of "four"
    (deploy / "junk.pyc").write_text("x")                                                    # untracked, not on origin
    before = _g(deploy, "rev-parse", "HEAD")
    landed = pl.update_code(deploy)
    check("a half-done fast-forward (every dirty path = its origin/main blob) cleans itself and lands",
          landed.get("changed") is True and _g(deploy, "rev-parse", "HEAD") == _g(origin, "rev-parse", "HEAD")
          and _g(deploy, "status", "--porcelain", "--untracked-files=no") == "" and (deploy / "junk.pyc").exists(),
          (before, landed))
    (origin / "f").write_text("5"); _g(origin, "commit", "-qam", "five")
    _g(deploy, "fetch", "-q", "origin")
    (deploy / "f").write_text("someone's edit")
    check("a dirty path that is NOT origin's blob is a real edit: the pull still fails loud and the edit stays",
          raises(lambda: pl.update_code(deploy)) and (deploy / "f").read_text() == "someone's edit")
    (deploy / "f").write_text("5"); (deploy / "g").write_text("stray")
    check("one real edit among landed blobs blocks the whole clean (nothing is put back)",
          raises(lambda: pl.update_code(deploy)) and (deploy / "f").read_text() == "5"
          and (deploy / "g").read_text() == "stray")
    (deploy / "g").write_text("new")                       # g back to HEAD; f still equals origin's blob
    (origin / "m").write_text("m"); _g(origin, "add", "m"); _g(origin, "commit", "-qm", "six")
    _g(deploy, "fetch", "-q", "origin")
    (deploy / "m").write_text("REAL")                      # untracked, on origin/main, but NOT its blob
    check("an untracked path origin/main has with other content is a real edit: the pull fails loud and it stays",
          raises(lambda: pl.update_code(deploy)) and (deploy / "m").read_text() == "REAL"
          and (deploy / "f").read_text() == "5")
    _p128 = _sp.CompletedProcess([], 128, "", "Updating files:  14% (1/7)\rUpdating files: 100% (7/7)\n"
                                 "fatal: Unable to create '/x/.git/index.lock': File exists.\n")
    check("the failure names git's reason, not its progress lines", "index.lock" in pl._git_err(_p128)
          and "Updating files" not in pl._git_err(_p128), pl._git_err(_p128))
    orig_uc = pl.update_code
    pl.update_code = lambda: {"skipped": True, "age": 5.0}
    try:
        rc = pl.main(["update"])
    finally:
        pl.update_code = orig_uc
    check("`pulse.py update` exits 0 on a skip, so the unit does not fail", rc == 0, rc)

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
sys.exit(1 if FAILS else 0)
