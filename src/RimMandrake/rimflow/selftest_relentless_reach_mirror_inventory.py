#!/usr/bin/env python3
"""The Marker's box shows the D: mirror's game inventory read only (CHECKER_REACH_FIX_OTHER_STILL_DARK, gen 5).

The instance: walls.marker.deny holds /mnt/d/Luke/dev, so /mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures
(gametex.BUNDLES, untracked extracted game art) was EACCES in every box. ART_LEDGER_VET_PURGE_BAN_REVIEW_OWED's Judge
(selftest_facing_scale_lint) and NIGHTLY_COP_FIX_RED_AQJSGV_CFVH's (selftest_art_eval) saw their tests crash with
PermissionError; the `other` repair passed its probe and they stayed blind, since no read path may open a denied root and
a bind beneath an InaccessiblePaths parent is still EACCES. Rows:
  (1) the live rules' Marker profile names the inventory in read_always;
  (2) denied() carves around it (no deny entry is it or an ancestor of it), the rest of the mirror and of ~/dev stays
      denied, and readonly() binds it read only;
  (3) relentless_reach.hidden says the box sees it and still hides the rest of the mirror and another repo;
  (4) relentless_reachfix.uncovered counts the ART_LEDGER blind text covered by its stored proposal, and a blind on
      another /mnt/d/Luke/dev path still uncovered;
  (5) live: a systemd-run --user unit with the wall's real props reads index.csv, cannot write there, and cannot read
      the mirror's CLAUDE.md. Skips where no unit can be made (inside a box: exit 226) unless
      RELENTLESS_UNIT_PROBE_REQUIRED is set; the offbox adapter unit_probe_selftests_candidate runs it outside the wall.
Rows 1-4 fail on the code before read_always. Row 1's ART_EVAL_WORK joined in the same generation: selftest_art_eval, past the inventory,
stopped on 'agent storage root unknown (agent_storage.py failed)' in a real box (Lodestar's lib is walled)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_reach as RR       # noqa: E402
import relentless_reachfix as RF    # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
INV = "/mnt/d/Luke/dev/RimMandrake/observed/inventory"
CSV = INV + "/bundle_textures/index.csv"

ART_LEDGER = ("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/index.csv (read by selftest_facing_scale_lint "
              "via gametex.BUNDLES): ls of that dir -> Permission denied, so the test crashes before its verdict")
STORED = {"adapters": ["git_stat_candidate", "git_log_candidate", "unit_probe_selftests_candidate"], "by": "judge",
          "grants": ["item_prose"],
          "paths": ["/home/mandrake/rm/bench/infrastructure/state/items/ROT_KEPT_ART_JUDGE_FOR_OWNER_DIGEST.md"]}


def check(name, cond, detail=""):
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, "" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def under(p, root):
    return p == root or p.startswith(root.rstrip("/") + "/")


def rules():
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        return json.load(f)


def test_offline(r):
    prof = W.profile(r)
    ra = getattr(W, "read_always", lambda p: [])(prof)
    check("(1) the Marker profile names the mirror's inventory in read_always", INV in ra, ra)
    check("(1) the box sets ART_EVAL_WORK, so art_eval never runs the walled Lodestar agent_storage.py",
          (prof.get("env") or {}).get("ART_EVAL_WORK") == "/mnt/d/ClaudeWork/rimmandrake/art_eval", prof.get("env"))
    d = W.denied(prof)
    check("(2) no deny entry is the inventory or an ancestor of it",
          not [x for x in d if under(INV, os.path.realpath(x)) or under(INV, x)],
          [x for x in d if under(INV, os.path.realpath(x)) or under(INV, x)][:5])
    if os.path.isdir("/mnt/d/Luke/dev/RimMandrake"):
        check("(2) the rest of the mirror stays denied", "/mnt/d/Luke/dev/RimMandrake/CLAUDE.md" in d
              and "/mnt/d/Luke/dev/RimMandrake/design" in d, [x for x in d if "RimMandrake" in x][:8])
        check("(2) readonly() binds the inventory read only", INV in W.readonly(prof), W.readonly(prof)[-5:])
    else:
        print("skip (2) host rows: no D: mirror here")
    check("(3) the box is said to see index.csv", not RR.hidden(CSV, prof))
    check("(3) the rest of the mirror and another repo stay hidden",
          RR.hidden("/mnt/d/Luke/dev/RimMandrake/design/x.md", prof) and RR.hidden("/mnt/d/Luke/dev/Lodestar/x", prof)
          and RR.hidden("/home/mandrake/dev/Lodestar/x", prof))
    check("(4) the ART_LEDGER blind text is covered by its stored proposal", RF.uncovered(r, STORED, [ART_LEDGER]) == [],
          RF.uncovered(r, STORED, [ART_LEDGER]))
    other = "selftest_x needs /mnt/d/Luke/dev/Lodestar/bin/lib/genai_env.py: Permission denied"
    check("(4) a blind on another /mnt/d/Luke/dev path stays uncovered",
          RF.uncovered(r, STORED, [other]) == ["/mnt/d/Luke/dev/Lodestar/bin/lib/genai_env.py"],
          RF.uncovered(r, STORED, [other]))


def skip_live(why):
    if os.environ.get("RELENTLESS_UNIT_PROBE_REQUIRED"):
        check("(5) live probe ran where it is required", False, why)
    else:
        print("skip (5) live probe: %s" % why)


def test_live(r, base):
    if not os.path.exists("/usr/bin/systemd-run") or os.environ.get("RELENTLESS_NO_UNIT_PROBE"):
        return skip_live("no systemd-run here")
    if not os.path.isfile(CSV):
        return skip_live("no %s on this host" % CSV)
    import selftest_relentless_reach_git_grant as G
    nest = G.nested_unit_refused(base)
    if nest:
        return skip_live("a user unit cannot be made here (%s); unit_probe_selftests_candidate runs it outside" % nest)
    prof = dict(W.profile(r))
    box = tempfile.mkdtemp(prefix="mirrorinv", dir=base)
    prof["box_root"] = box
    try:
        for sub in ("projects", "tmp"):
            os.makedirs(os.path.join(box, sub), exist_ok=True)
        body = ('head -c 9 -- "$1" && echo && { touch -- "$2" 2>/dev/null && echo WROTE; true; } && '
                '{ head -c 1 -- "$3" >/dev/null 2>&1 && echo READ_MIRROR; true; }')
        argv = (["systemd-run", "--user", "--wait", "--pipe", "--collect", "--quiet"] + W.props(prof, box)
                + ["--", "/bin/sh", "-c", body, "sh", CSV, INV + "/bundle_textures/.walltest",
                   "/mnt/d/Luke/dev/RimMandrake/CLAUDE.md"])
        p = subprocess.run(argv, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
        out = (p.stdout or "") + (p.stderr or "")
        if "Failed to" in out and "bus" in out.lower():
            return skip_live("no user systemd here (%s)" % out[:120])
        check("(5) a unit with the wall's props reads index.csv", p.returncode == 0 and out.startswith("sourceKey"),
              "exit %d: %s" % (p.returncode, out[-300:]))
        check("(5) it cannot write the inventory", "WROTE" not in out, out[-200:])
        check("(5) it cannot read the rest of the mirror", "READ_MIRROR" not in out, out[-200:])
    finally:
        shutil.rmtree(box, ignore_errors=True)
        try:
            os.unlink(INV + "/bundle_textures/.walltest")
        except OSError:
            pass


def main():
    import selftest_relentless_reach_git_grant as G
    base = G.fixture_base()     # never under the unit's /tmp (exit 226), the git grant test's own trap
    try:
        r = rules()
        test_offline(r)
        test_live(r, base)
    except Exception as e:  # noqa: BLE001 - a crash on the old code is a red row, not a traceback
        check("no crash", False, "%s: %s" % (type(e).__name__, e))
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
