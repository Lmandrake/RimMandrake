#!/usr/bin/env python3
# selftest-timeout: 540
"""The checker box carries the builder's toolchain (CHECKBOX_BUILD_BUILDER_TOOLCHAIN, redesign_final.md WP-02 row 02).

Owner 2026-11-06: a checker box with git + dotnet + cv2 is top priority. Rows, one per acceptance clause:
  (A) every box gets the read-only git history by default (relentless_box.json default_grants): tree/.git at the sha, the
      prompt says so and names the toolchain; a box built with an empty config is the old export (no .git);
  (B) the unit's PATH carries the checkbox venv (python3 imports cv2), and the box config's grants stay inside GRANTS;
  (C) relentless_reach.needs no longer calls served git history verbs or winbuild.py out of reach; refs, remotes and other
      Windows programs still are;
  (D) no reach class sits at `ticket` with a done ticket: a failed re-probe after the close files a successor
      (CHECKER_REACH_FIX_<CLASS>_DARK_<ORDINAL>), and so does the legacy book row probed at that close before the box
      changed, and the fully parked row (same close, same box) without another probe;
  (E) LIVE, in a fresh Marker box at the candidate (the clone's HEAD), run in the Marker's own walled unit against the
      export, never the clone: three history-dependent proofs pass and go red under a planted break -
        E1 `git rev-parse HEAD` == the candidate          (planted: the box's HEAD moved to the parent)
        E2 `git show <sha>:path` == the tree's file        (planted: the tree file tampered)
        E3 code-commit: `git log -1 --format=%H -- <path>` == the commit that last touched it (planted: HEAD moved
           before that commit);
      E4 a candidate C# build (winbuild.py ColdStorage.csproj) is green, and red with a planted syntax error;
      E5 toolchain_probe exits 0 on every relentless_box.json row (git, python_cv2, windows_build).
Rows A, C and D fail on the code before this item (no default grant, git/winbuild refused, a note and a wait forever).
Row E needs a user systemd and the Windows interop; where they are missing it prints the unmeasured phrase."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import relentless_reach as RR       # noqa: E402
import relentless_reachfix as RF    # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS, SKIPS = [], []
CSPROJ = "src/RimMandrake/ColdStorage/Source/ColdStorage.csproj"


def check(name, cond, got=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  got: %s" % str(got)[:400]))
    if not cond:
        FAILS.append(name)


def skip_live(why):
    SKIPS.append(why)
    print("skip %s" % why)


def git(*a, cwd=REPO):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=120).stdout.strip()


def rules():
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        return json.load(f)


def box_root():
    """The Marker's real box root when this process may write it, else a fixture dir off /tmp (the unit binds its own
    tmp over /tmp, so a box under it is gone inside the unit)."""
    real = W.profile(rules())["box_root"]
    if os.path.isdir(real) and os.access(real, os.W_OK):
        return real, None
    base = os.path.join(os.path.expanduser("~"), ".cache", "rm-selftest-checkbox")
    os.makedirs(base, exist_ok=True)
    d = tempfile.mkdtemp(prefix="cb", dir=base)
    return d, d


def t_default_box(prof, sha):
    box = W.make_box(prof, REPO, sha, "cbA" + os.urandom(4).hex())
    bare = W.make_box(prof, REPO, sha, "cbN" + os.urandom(4).hex(), cfg={})
    try:
        head = open(os.path.join(str(box), "tree", ".git", "HEAD"), encoding="utf-8").read().strip()
        check("(A) a default box binds the git history", bool(W.git_reads(box)), W.git_reads(box))
        check("(A) its HEAD is the candidate, detached", head == sha, head)
        check("(A) a box with an empty config is the old export (no .git)",
              not W.git_reads(bare) and not os.path.exists(os.path.join(str(bare), "tree", ".git")))
        st = {"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": ["x"]}}
        txt = W.marker_prompt(st, "THE ITEM", box)
        check("(A) the prompt says the history is there", "read-only git history" in txt and "no git history" not in txt)
        check("(A) the prompt names cv2 and the Windows build stage", "cv2" in txt and "winbuild.py" in txt)
        check("(A) the bare box's prompt still says no git history",
              "no git history" in W.marker_prompt(st, "THE ITEM", bare))
    finally:
        W.remove_box(bare)
    return box


def t_env():
    venv = os.path.expanduser("~/.local/venvs/checkbox/bin")
    env = W.unit_env({}, "/b")
    check("(B) the default grants are known grants", W.default_grants() == [W.GIT_GRANT], W.default_grants())
    check("(B) a bad grant in the config is dropped", W.default_grants({"default_grants": ["git_history", "rm -rf"]})
          == [W.GIT_GRANT])
    if os.path.isdir(venv):
        check("(B) the unit PATH starts with the checkbox venv", env.get("PATH", "").split(":")[0] == venv,
              env.get("PATH"))
    else:
        check("(B) no venv on this host: PATH is left alone, not pointed at nothing", venv not in env.get("PATH", ""))
    check("(B) an empty config adds nothing to PATH", "checkbox" not in W.unit_env({}, "/b", cfg={}).get("PATH", ""))


def t_needs(prof):
    hist = "git rev-parse HEAD; git show abc:src/x.py; git log -1 --format=%H -- src/x.py"
    check("(C) served git history verbs are not needs", RR.needs(hist, prof) == [], RR.needs(hist, prof))
    check("(C) unserved, they still are (the old wall)", len(RR.needs(hist, prof, serve=())) == 3)
    check("(C) winbuild.py is served", RR.needs("python3 src/RimMandrake/Utils/winbuild.py ColdStorage", prof) == [])
    refs = RR.needs("git fetch origin && git for-each-ref", prof)
    check("(C) refs and remotes stay needs", len(refs) == 2 and all(n.startswith("git refs") for n in refs), refs)
    check("(C) another Windows program stays a need", RR.needs("powershell.exe -Command Get-Date", prof) != [])


def t_successor():
    import selftest_relentless_reachfix as SR
    first = "CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"

    def ticketed():
        x = SR.rig(n=1)
        SR.B.to_check(x, "I0")
        SR.blind(x, "I0")
        x.tick()
        x.w.items[first] = "done"
        return x

    x = ticketed()
    n = len(x.w.probes)
    x.tick()
    book = RF.load(x.s)
    check("(D) done ticket, failed re-probe: a successor, not a wait on the done ticket",
          book["git"]["ticket"] == "CHECKER_REACH_FIX_GIT_DARK_SECOND" and len(x.w.probes) == n + 1
          and x.st("I0")["wait"]["on"] == "CHECKER_REACH_FIX_GIT_DARK_SECOND", (book["git"], x.w.tickets))
    x.w.items["CHECKER_REACH_FIX_GIT_DARK_SECOND"] = "done"
    x.tick()
    check("(D) the successor closing with the probe still failing files the next ordinal",
          RF.load(x.s)["git"]["ticket"] == "CHECKER_REACH_FIX_GIT_DARK_THIRD", RF.load(x.s)["git"])
    x.done()

    for label, fp in (("legacy row probed at this close before the box changed", None),
                      ("parked row: same close, same box", RF.box_fingerprint())):
        x = ticketed()
        led = x.w.item_state(first)
        book = RF.load(x.s)
        book["git"]["probed_event"] = "%s:%s:%s" % (led.get("state"), led.get("closed_sha"), led.get("event"))
        if fp:
            book["git"]["probed_box"] = fp
        RF.save(x.s, book)
        n = len(x.w.probes)
        x.tick()
        got = RF.load(x.s)["git"]
        check("(D) %s: a successor is filed" % label, got["status"] == "ticket"
              and got["ticket"] == "CHECKER_REACH_FIX_GIT_DARK_SECOND", got)
        check("(D) %s: probes %s" % (label, "once more" if fp is None else "nothing"),
              len(x.w.probes) == n + (1 if fp is None else 0), x.w.probes[n:])
        x.done()
    ent = {"successors": [{}] * 20}
    check("(D) past the last ordinal the last name is reused (reach_ticket reopens it)",
          RF.successor_id("windows_build", ent) == "CHECKER_REACH_FIX_WINDOWS_BUILD_DARK_TWELFTH")


def run_in_box(prof, box, cmds):
    """-> {name: (exit, out)}: each command in the Marker's walled unit from the box's tree (toolchain_probe)."""
    cfg = dict(W.box_config(), toolchain=[{"name": k, "cmd": v} for k, v in cmds.items()])
    return {r["name"]: (r["exit"], r["out"]) for r in W.toolchain_probe(prof, box, cfg=cfg, timeout=400)}


def t_live(prof, box, sha):
    if not shutil.which("systemd-run") or os.environ.get("RELENTLESS_NO_UNIT_PROBE"):
        skip_live("no systemd-run here")
        return
    tree = os.path.join(str(box), "tree")
    rows = W.toolchain_probe(prof, box)
    if any("Failed to" in r["out"] or "bus" in r["out"].lower() for r in rows if r["exit"] != 0) and \
            all(r["exit"] != 0 for r in rows):
        skip_live("no user systemd unit here: %s" % rows[0]["out"][-160:])
        return
    for r in rows:
        check("(E5) toolchain row %s exits 0 in the box" % r["name"], r["exit"] == 0, r["out"][-300:])
    path = "src/RimMandrake/rimflow/relentless_wall.py"
    last = git("log", "-1", "--format=%H", sha, "--", path)
    parent = git("rev-parse", sha + "^")
    proofs = {
        "rev": "test \"$(git rev-parse HEAD)\" = %s" % sha,
        "show": "git show %s:%s | cmp - %s" % (sha, path, path),
        "commit": "test \"$(git log -1 --format=%%H -- %s)\" = %s" % (path, last),
    }
    good = run_in_box(prof, box, proofs)
    for k, label in (("rev", "E1 rev-parse HEAD is the candidate"), ("show", "E2 git show sha:path is the tree's file"),
                     ("commit", "E3 the code-commit check finds the commit that last touched the file")):
        check("(%s) passes at the candidate" % label, good[k][0] == 0, good[k])
    head = os.path.join(tree, ".git", "HEAD")
    target = os.path.join(tree, path)
    with open(target, "rb") as f:
        orig = f.read()
    try:
        with open(head, "w", encoding="utf-8") as f:     # planted: HEAD at the parent (E1) / before the last touch (E3)
            f.write(parent + "\n")
        with open(target, "ab") as f:                    # planted: the tree file tampered (E2)
            f.write(b"\n# planted\n")
        before = git("rev-parse", last + "^")
        bad = run_in_box(prof, box, {"rev": proofs["rev"], "show": proofs["show"]})
        with open(head, "w", encoding="utf-8") as f:
            f.write(before + "\n")
        bad.update(run_in_box(prof, box, {"commit": proofs["commit"]}))
    finally:
        with open(head, "w", encoding="utf-8") as f:
            f.write(sha + "\n")
        with open(target, "wb") as f:
            f.write(orig)
    for k, label in (("rev", "E1 HEAD moved to the parent"), ("show", "E2 the tree file tampered"),
                     ("commit", "E3 HEAD moved before the last touch")):
        check("(%s) goes red" % label, bad[k][0] != 0, bad[k])
    # the unit's output tail is 600 chars and winbuild ends on a close-evidence warning in a walled box: keep the lines
    # that decide, and winbuild's own exit (pipefail, not $PIPESTATUS: systemd-run expands ${...} in the command itself)
    build = ("set -o pipefail; python3 src/RimMandrake/Utils/winbuild.py %s 2>&1 "
             "| { grep -E 'error CS|Build succeeded|BUILT' || true; } | tail -n 4" % CSPROJ)
    ok = run_in_box(prof, box, {"build": build})["build"]
    check("(E4) the candidate's C# builds in the box", ok[0] == 0 and "Build succeeded" in ok[1], ok[1][-400:])
    cs = sorted(n for n in os.listdir(os.path.join(tree, os.path.dirname(CSPROJ))) if n.endswith(".cs"))
    if not cs:
        check("(E4) the project has a .cs file to break", False, os.path.dirname(CSPROJ))
        return
    src = os.path.join(tree, os.path.dirname(CSPROJ), cs[0])
    with open(src, "rb") as f:
        keep = f.read()
    try:
        with open(src, "ab") as f:
            f.write(b"\nnamespace Planted { class Broken { void X( } }\n")
        red = run_in_box(prof, box, {"build": build})["build"]
    finally:
        with open(src, "wb") as f:
            f.write(keep)
    check("(E4) a planted syntax error turns the build red, on a compiler error", red[0] != 0 and "error CS" in red[1],
          red[1][-400:])


def main():
    sha = git("rev-parse", "HEAD")
    prof = W.profile(rules())
    root, made = box_root()
    prof = dict(prof, box_root=root)
    box = None
    for t in (lambda: t_env(), lambda: t_needs(prof), lambda: t_successor()):
        try:
            t()
        except Exception as e:      # a row that crashes is a red row, not a dead selftest
            check("row ran", False, "%s: %s" % (type(e).__name__, e))
    try:
        box = t_default_box(prof, sha)
        t_live(prof, box, sha)
    except Exception as e:
        check("live rows ran", False, "%s: %s" % (type(e).__name__, e))
    finally:
        if box:
            W.remove_box(box)
        if made:
            shutil.rmtree(made, ignore_errors=True)
    if SKIPS and not FAILS:
        print("UNMEASURED, not a pass or a fail: %s" % "; ".join(SKIPS))
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
