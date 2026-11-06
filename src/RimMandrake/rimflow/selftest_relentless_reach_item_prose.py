#!/usr/bin/env python3
"""A passed items reach repair puts infrastructure/state/items into the Marker's tree (CHECKER_REACH_FIX_OTHER_STILL_DARK, gen 3).

The instance: walls.marker.tree_exclude keeps infrastructure/state/items out of every box. NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_
DARK's Judge ran a selftest that reads two live item files and said so; the text classed `other`, whose repair binds HOST read
paths, the probe had nothing to read, and the re-check was blind again: no bind puts a file into the exported tree. Rows:
  (1) the NIGHTSIDE text classes as `items` (not `other`), its seed proposal carries the item_prose grant, a Judge may
      propose it by name, and the stored `other` proposal gains it from its blind text when it re-probes (refreshed());
  (2) make_box with the grant: tree/infrastructure/state/items holds the items at the candidate, read only; conversations stay out; the prompt says the folder is there and is filers' prose;
  (3) no grant, no items folder and no such prompt line; a grant at a commit with no item file leaves the plain box,
      never a crash;
  (4) the sweep hands the grant to the probe and the applied overlay holds it;
  (5) the probe of the grant reads an item file inside the wall, and fails at a sha with no items;
  (6) CHECKER_REACH_FIX_ITEMS_STILL_DARK: a candidate that edits an item file (WORLD_BEAUTY_VERIFY_OFFLINE_BEAT_THE_GAME's
      rewrote a closed item's verify clause) shows the candidate's text in the box, and the reach probe grants the very
      rev make_box does. Before: the box read the parent, the probe the candidate; the probe passed and the Judge was blind.
Rows 1-4 fail on the code before the grant (no items class, GRANTS held git_history alone)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_reachfix as RF    # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
GRANT = getattr(W, "ITEM_GRANT", "item_prose")
ITEMS = "infrastructure/state/items"
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
NIGHTSIDE = ("its repair passed the probe, yet the Judge is still blind: infrastructure/state/items/UMBRA_TITAN_POPULATE_"
             "BURNS_TO_WALK.md and CHILL_TITAN_POPULATE_WAX_GIANT_TOO_SMALL.md (whole items dir absent in export; ls -> No "
             "such file or directory); the selftest's two 'is live' checks need them")


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, env=ENV)


def repo(root):
    """-> (repo, bare sha with no items, sha whose parent holds items). The candidate edits code only, as a build does."""
    rp = Path(root, "repo")
    git(root, "init", "-q", str(rp))
    Path(rp, "a.py").write_text("one\n", encoding="utf-8")
    git(rp, "add", "-A")
    git(rp, "commit", "-qm", "root")
    bare = git(rp, "rev-parse", "HEAD").stdout.strip()
    Path(rp, ITEMS).mkdir(parents=True)
    Path(rp, ITEMS, "UMBRA_TITAN_POPULATE_BURNS_TO_WALK.md").write_text("# umbra\n", encoding="utf-8")
    Path(rp, "conversations").mkdir()
    Path(rp, "conversations/x.md").write_text("withheld\n", encoding="utf-8")
    git(rp, "add", "-A")
    git(rp, "commit", "-qm", "items filed")
    Path(rp, "a.py").write_text("two\n", encoding="utf-8")
    git(rp, "commit", "-qam", "the candidate")
    return rp, bare, git(rp, "rev-parse", "HEAD").stdout.strip()


def prof(root, box_root=None):
    return {"enforce": True, "box_root": box_root or str(Path(root, "boxes")), "deny": [], "deny_children": [root],
            "tmpfs": [], "tree_exclude": ["conversations", ITEMS], "read_through": []}


def test_reach():
    r = json.loads(Path(HERE, "relentless_rules.json").read_text(encoding="utf-8"))
    cls = RF.classify(r, [NIGHTSIDE])
    check("(1) the NIGHTSIDE text classes as items, not other", cls["class"] == "items", cls)
    prop = RF.propose(r, cls, [], [], NIGHTSIDE)
    check("(1) its seed proposal carries the item_prose grant", GRANT in prop.get("grants", []), prop)
    check("(1) item_prose is a box grant", GRANT in W.GRANTS, W.GRANTS)
    prop = RF.propose(r, cls, [GRANT], [], NIGHTSIDE)
    check("(1) a Judge may propose it by name", prop.get("grants") == [GRANT] and not prop["refused"], prop)
    old = {"adapters": [], "paths": [], "by": "seed", "refused": {}}
    st = {"reach": {"class": "other", "proposal": old, "still_blind": NIGHTSIDE}, "blind": None}
    check("(1) the stored other proposal gains the grant on the re-probe", GRANT in RF.refreshed(r, st).get("grants", []),
          RF.refreshed(r, st))


def test_box(root):
    rp, bare, sha = repo(root)
    p = prof(root)
    try:
        box = W.make_box(p, str(rp), sha, "i1", grants=[GRANT])
    except (TypeError, AttributeError) as e:
        check("(2) make_box takes the item_prose grant", False, e)
        return None
    f = Path(box, "tree", ITEMS, "UMBRA_TITAN_POPULATE_BURNS_TO_WALK.md")
    check("(2) the item file is in the tree", f.is_file() and f.read_text(encoding="utf-8") == "# umbra\n", f)
    check("(2) read only", f.is_file() and not (f.stat().st_mode & 0o222), oct(f.stat().st_mode) if f.exists() else "-")
    check("(2) conversations stay out", not Path(box, "tree/conversations").exists())
    check("(2) the code is the candidate's", Path(box, "tree/a.py").read_text(encoding="utf-8") == "two\n")
    check("(2) at the candidate", W.item_reads(box).get("rev") == sha, W.item_reads(box))
    txt = W.marker_prompt({"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": "x"}}, "ITEM", box)
    check("(2) the prompt says the folder is there and is filers' prose", ITEMS in txt and "filers'" in txt, txt[:300])
    plain = W.make_box(p, str(rp), sha, "i2")
    check("(3) no grant, no items folder", not Path(plain, "tree", ITEMS).exists())
    txt = W.marker_prompt({"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": "x"}}, "ITEM", plain)
    check("(3) no grant, no items line in the prompt", "filers'" not in txt)
    early = W.make_box(p, str(rp), bare, "i3", grants=[GRANT])
    check("(3) a commit with no item file: the plain box and a note, never a crash",
          not Path(early, "tree", ITEMS).exists() and Path(early, "item_grant_failed").exists())
    for b in (box, plain, early):
        W.remove_box(b)
    test_edited(rp, p)
    return rp, bare, sha


def test_edited(rp, p):
    """(6) the instance: the candidate itself rewrites an item's prose; box and probe must agree on what reads."""
    rel = ITEMS + "/closed/PLANETARY_LOADSCREEN_RENDERS_2.md"
    Path(rp, rel).parent.mkdir(parents=True, exist_ok=True)
    Path(rp, rel).write_text("verify: old clause\n", encoding="utf-8")
    git(rp, "add", "-A")
    git(rp, "commit", "-qm", "item filed")
    Path(rp, rel).write_text("verify: the candidate's clause\n", encoding="utf-8")
    git(rp, "commit", "-qam", "the candidate edits the verify clause")
    sha = git(rp, "rev-parse", "HEAD").stdout.strip()
    box = W.make_box(p, str(rp), sha, "i6", grants=[GRANT])
    try:
        f = Path(box, "tree", rel)
        check("(6) the box shows the candidate's item text", f.is_file() and "candidate's clause" in f.read_text(encoding="utf-8"),
              f.read_text(encoding="utf-8") if f.is_file() else "absent")
        made_rev = W.item_reads(box).get("rev")
    finally:
        W.remove_box(box)
    import relentless as R
    seen, real = [], W.grant_items

    def spy(b, source, rev):
        seen.append(rev)
        raise RuntimeError("spy: stop before the unit")
    W.grant_items = spy
    try:
        fx = R.Effects.__new__(R.Effects)
        fx.books = str(rp)
        broot = tempfile.mkdtemp(prefix="iprobe6", dir=str(Path(rp).parent))
        fx._probe_items({"walls": {"marker": prof(str(Path(rp).parent), box_root=broot)}}, {"sha": sha, "repo": str(rp)}, broot)
    finally:
        W.grant_items = real
    check("(6) the probe grants the rev the box grants", seen == [made_rev] and made_rev == sha, (seen, made_rev, sha))


def skip_live(why):
    if os.environ.get("RELENTLESS_UNIT_PROBE_REQUIRED"):
        check("(5) live probe ran where it is required", False, why)
    else:
        print("skip (5) live probe: %s" % why)


def test_sweep_and_probe(made, base):
    import selftest_relentless_reachfix as SR
    x = SR.rig(probe=(True, "ok"))
    seen = []
    x.w.reach_probe = lambda r, paths, adapters, values, store_root, grants=(): (seen.append(list(grants)) or (True, "ok"))
    SR.B.to_check(x, "I0")
    SR.blind(x, "I0", what=NIGHTSIDE)
    x.tick()
    check("(4) the sweep hands the item_prose grant to the probe", seen and GRANT in seen[0], seen)
    check("(4) the applied overlay holds it", GRANT in RF.grants(x.st("I0")), x.st("I0").get("reach"))
    x.done()
    if not made or not os.path.exists("/usr/bin/systemd-run") or os.environ.get("RELENTLESS_NO_UNIT_PROBE"):
        skip_live("no systemd-run here")
        return
    import selftest_relentless_reach_git_grant as G
    nest = G.nested_unit_refused(base)
    if nest:
        skip_live("a user unit cannot see this sandbox's own files (%s); the offbox reading "
                  "unit_probe_selftests_candidate runs it outside the wall" % nest)
        return
    import relentless as R
    rp, bare, sha = made
    fx = R.Effects.__new__(R.Effects)
    fx.books = str(rp)
    broot = tempfile.mkdtemp(prefix="iprobe", dir=base)
    sroot = tempfile.mkdtemp(prefix="istore", dir=base)
    try:
        r = {"walls": {"marker": prof(os.path.dirname(str(rp)), box_root=broot)}}
        good, why = fx.reach_probe(r, [], [], {"sha": sha, "repo": str(rp)}, sroot, grants=[GRANT])
        if "probe unit" in why or "Failed to" in why or "bus" in why.lower():
            skip_live("no user systemd here (%s)" % why[:120])
            return
        check("(5) the grant's probe reads an item file inside the wall", good and "UMBRA" in why, why)
        bad, why = fx.reach_probe(r, [], [], {"sha": bare, "repo": str(rp)}, sroot, grants=[GRANT])
        check("(5) a sha with no items fails its probe", not bad, why)
    finally:
        shutil.rmtree(broot, ignore_errors=True)
        shutil.rmtree(sroot, ignore_errors=True)


def main():
    import selftest_relentless_reach_git_grant as G
    base = G.fixture_base()     # never under the unit's /tmp (exit 226), the git grant test's own trap
    root = tempfile.mkdtemp(prefix="itemgrant", dir=base)
    try:
        test_reach()
        made = test_box(root)
        test_sweep_and_probe(made, base)
    except Exception as e:  # noqa: BLE001 - a crash on the old code is a red row, not a traceback
        check("no crash", False, "%s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
