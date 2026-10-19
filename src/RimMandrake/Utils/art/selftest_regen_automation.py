#!/usr/bin/env python3
"""selftest_regen_automation.py — one regression case per finding of the GPT review of the dregen_ automation
(Transient/gpt_review_art_automation_2026-10-19.txt, 18 findings), against regen_eligibility.py, donor_regen_jobs.py and
donor_regen_install_hourly.py. Every case was first run against the pre-fix code and failed there.

Gate (#1-#7, #17): any-case StandIn/ on Windows; the eventual destination of an external job; regeneration history
before any file match; the TARGET def must draw the path; a fresh gate at publish time; every copy/facing judged;
kind=install history; an XML parse failure fails the gate. Requeue/submit (#12-#16, #18): manifest archived before
the job is visible; no-replace publication; per-row cap; the backoff re-read in submit; 429 read from the worker's
error fields; as_posix. Installer (#8-#11 + timeouts): only the run's own lines/edits are committed, from a private
index by compare-and-swap; literal paths; publish only its own commits; a hung child times out.

INSTALLER_UNDER_TEST=<path to a donor_regen_install_hourly.py> runs the installer cases against that file instead
(it is copied into the fake repo and run as a script) — how the pre-fix version was shown to fail.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PureWindowsPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A  # noqa: E402
import regen_eligibility as RE  # noqa: E402
import donor_regen_jobs as DJ  # noqa: E402
import selftest_regen_eligibility as T  # noqa: E402  (fake repo, synthetic ledger, stub game lookups)

FAILS = []
M = T.M


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:500]}]"))
    if not cond:
        FAILS.append(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def add_def(root, name, texpath, extra=""):
    (root / M / "Defs" / f"{name}.xml").write_text(
        f"<Defs><ThingDef><defName>{name}</defName><graphicData><texPath>{texpath}</texPath></graphicData>"
        f"</ThingDef>{extra}</Defs>")


def put(root, rel, b, mod=M):
    p = root / mod / "Textures" / (rel + ".png")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
    return p


def verdict(g, r):
    try:
        return g.classify(r)
    except Exception as e:                                    # noqa: BLE001
        return {"verdict": f"ERROR {type(e).__name__}: {e}", "eligible": None, "reason": ""}


def gate_or_error(root, **kw):
    try:
        return T.gate(root, **kw), None
    except Exception as e:                                    # noqa: BLE001
        return None, e


# ─────────────────────────────────────────────────────────────────── gate ──

def gate_cases():
    # 1: Textures/standin/Foo (lower case) is the owner-kept Textures/StandIn/Foo on Windows
    root = T.build_repo()
    add_def(root, "RM_Ci", "StandIn/Things/RM_Ci")
    put(root, "StandIn/Things/RM_Ci", T.B["kept"])
    v = verdict(T.gate(root), T.row("RM_Ci", install_to=f"{M}/Textures/standin/Things/RM_Ci.png"))
    check(v["verdict"] == "REFUSED_KEPT", "#1 a lower-case standin/ destination finds the owner-kept StandIn/ file", v)

    # 2: an external job whose eventual destination (own_path) already holds kept / unknown art
    def gc(res):
        return {"cat": "VANILLA", "by": "ludeon.rimworld"} if res.startswith("Foo/") else T.game_classify(res)
    root = T.build_repo()
    add_def(root, "RM_Ext", "Foo/Body")
    put(root, "Foo/RM_Ext/RM_Ext", T.B["kept"])
    v = verdict(T.gate(root, game_classify=gc), T.row("RM_Ext", target_texpath="Foo/Body"))
    check(v["verdict"] == "REFUSED_KEPT", "#2 external job: owner-kept art at its eventual destination refuses it", v)
    root = T.build_repo()
    add_def(root, "RM_Ext", "Foo/Body")
    put(root, "Foo/RM_Ext/RM_Ext", T.B["unknown"])
    v = verdict(T.gate(root, game_classify=gc), T.row("RM_Ext", target_texpath="Foo/Body"))
    check(v["verdict"] == "REFUSED_UNCONFIRMED", "#2 external job: unknown bytes at its eventual destination refuse it", v)

    # 3: a donor file at the destination does not hide regeneration history
    root = T.build_repo()
    add_def(root, "RM_Db", "Things/RM_Db")
    put(root, "Things/RM_Db", T.B["donor"])
    ev = T.events() + [T.var(30, "d" * 64, kind="artpipe", job="dregen_RM_Db_v1"),
                       {"type": "binding", "id": "b30", "sha": "d" * 64, "subject": "RM_Db", "texpath": "Things/RM_Db",
                        "job": "dregen_RM_Db_v1"}]
    v = verdict(T.gate(root, idx=A.Index(ev)), T.row("RM_Db", install_to=T.it("Things/RM_Db")))
    check(v["verdict"] == "REFUSED_REGEN", "#3 donor file present + a finished render bound to the def+path: refused", v)
    root = T.build_repo()
    add_def(root, "RM_Rs", "Things/RM_Rs")
    put(root, "Things/RM_Rs", T.B["donor"])
    ev = T.events() + [T.var(31, "c" * 64, kind="artpipe", job="texregen_RM_Rs_v1", res="Things/RM_Rs")]
    v = verdict(T.gate(root, idx=A.Index(ev)), T.row("RM_Rs", install_to=T.it("Things/RM_Rs")))
    check(v["verdict"] == "REFUSED_REGEN", "#3 donor bytes restored at a path a render was registered at: refused", v)

    # 4: another def still drawing the old path does not make a stale job for THIS def eligible
    root = T.build_repo()
    add_def(root, "RM_New", "New/Body")
    add_def(root, "RM_OldUser", "Old/Body")
    put(root, "New/Body", T.B["newregen"])
    put(root, "Old/Body", T.B["donor"])
    v = verdict(T.gate(root), T.row("RM_New", install_to=T.it("Old/Body")))
    check(v["verdict"] == "REFUSED_REGEN", "#4 stale job: target def now draws a render; another def's reference "
          "does not pass it", v)
    root = T.build_repo()
    add_def(root, "RM_Kind", "Things/RM_KindBody",
            extra="<PawnKindDef><defName>RM_KindKind</defName><race>RM_Kind</race><lifeStages><li><bodyGraphicData>"
                  "<texPath>Things/RM_KindAdult</texPath></bodyGraphicData></li></lifeStages></PawnKindDef>")
    v = verdict(T.gate(root), T.row("RM_Kind", install_to=T.it("Things/RM_KindAdult")))
    check(v["verdict"] == "NONE", "#4 a texture drawn by the def's own PawnKindDef counts as drawn by the def", v)

    # 5: a render installed after the gate was built is caught at publish time
    root = T.build_repo()
    EV = T.events()
    g, err = gate_or_error(root, idx=lambda: A.Index(list(EV)))
    r = T.row("RM_None", install_to=T.it("Things/RM_None/RM_None"))
    if g is None:
        check(False, "#5 a gate takes a ledger factory and rebuilds fresh", err)
    else:
        v0 = g.classify(r)
        put(root, "Things/RM_None/RM_None", b"late-render")
        EV.append(T.var(50, sha(b"late-render"), kind="artpipe", job="dregen_RM_None_v1"))
        try:
            ok, gone = g.recheck([r])
            check(v0["verdict"] == "NONE" and not ok and gone and gone[0]["verdict"] == "REFUSED_REGEN",
                  "#5 recheck with a fresh gate refuses a destination that got a render after the run began",
                  (v0["verdict"], gone))
        except Exception as e:                                # noqa: BLE001
            check(False, "#5 recheck with a fresh gate refuses a destination that got a render after the run began", e)
        art = new_art()
        jf = art / "jobs.json"
        jf.write_text(json.dumps({"rows": [r]}))
        calls = []
        with patched(ART=art, in_flight=lambda: 0, queue_view=lambda: ({}, set()),
                     run=lambda *a, **k: calls.append(a) or subprocess.CompletedProcess(a, 0, "", "")):
            try:
                DJ.submit_one(jf, 40, False, g)
            except Exception as e:                            # noqa: BLE001
                calls.append(("raised", e))
        check(not calls, "#5 submit_one files nothing that a publish-time fresh gate refuses", calls)

    # 6: every facing / copy is judged, not the first
    root = T.build_repo()
    add_def(root, "RM_Gs", "Things/RM_Gs")
    dep = Path(tempfile.mkdtemp(prefix="dep_"))
    (dep / "RM_Gs_east.png").write_bytes(T.B["donor"])
    (dep / "RM_Gs_south.png").write_bytes(T.B["kept"])

    def gc6(res):
        return {"cat": "OURS", "by": "mandrake.rm.fake"} if res == "Things/RM_Gs" else T.game_classify(res)
    gf = lambda res: [("mandrake.rm.fake", str(dep / "RM_Gs_east.png")), ("mandrake.rm.fake", str(dep / "RM_Gs_south.png"))]  # noqa: E731
    g = T.gate(root, game_classify=gc6, game_file=gf)
    v = verdict(g, T.row("RM_Gs", target_texpath="Things/RM_Gs", facing="south"))
    check(v["verdict"] == "REFUSED_KEPT", "#6 a south job is judged on the deployed SOUTH copy, not the first (east)", v)
    root = T.build_repo()
    add_def(root, "RM_Two", "Things/RM_Two")
    put(root, "Things/RM_Two_south", T.B["donor"], mod="src/RimMandrake/AAA")
    put(root, "Things/RM_Two_south", T.B["kept"], mod="src/RimMandrake/ZZZ")
    v = verdict(T.gate(root), T.row("RM_Two", target_texpath="Things/RM_Two", facing="south"))
    check(v["verdict"] == "REFUSED_KEPT", "#6 two mods of ours ship the path: the kept copy refuses it", v)

    # 7: installed art (kind=install) is history even after its file moved away
    root = T.build_repo()
    add_def(root, "RM_Inst", "Things/RM_Inst")
    ev = T.events() + [T.var(70, "a" * 64, kind="install", loc=f"{M}/Textures/Things/RM_Inst.png"),
                       {"type": "binding", "id": "b70", "sha": "a" * 64, "subject": "RM_Inst",
                        "texpath": "Things/RM_Inst", "job": "dregen_RM_Inst_v1"}]
    v = verdict(T.gate(root, idx=A.Index(ev)), T.row("RM_Inst", install_to=T.it("Things/RM_Inst")))
    check(v["verdict"] == "REFUSED_REGEN", "#7 a binding of installed (kind=install) art refuses the moved-away path", v)
    root = T.build_repo()
    add_def(root, "RM_Inst2", "Things/RM_Inst2")
    ev = T.events() + [T.var(71, "b" * 64, kind="install", loc=f"{M}/Textures/Things/RM_Inst2.png")]
    v = verdict(T.gate(root, idx=A.Index(ev)), T.row("RM_Inst2", install_to=T.it("Things/RM_Inst2")))
    check(v["verdict"] == "REFUSED_REGEN", "#7 an install registered by loc only (no res) is history too", v)

    # 17: a malformed XML file makes the gate fail closed
    root = T.build_repo()
    (root / M / "Defs" / "broken.xml").write_text("<Defs><ThingDef><defName>RM_Broken</defName></Defs>")
    g, err = gate_or_error(root)
    check(g is None and isinstance(err, RE.GateError), "#17 an unparseable XML file raises GateError (files nothing)",
          err or "gate built")


# ─────────────────────────────────────────────────────────── submit/requeue ──

def new_art():
    art = Path(tempfile.mkdtemp(prefix="regen_art_"))
    for d in ("pending", "active", "failed", "_refs"):
        (art / d).mkdir()
    return art


class patched:
    """Swap DJ globals (ART, in_flight, queue_view, subprocess.run, eligible_failed, shutil.move, _after_publish)."""

    def __init__(self, **kw):
        self.kw, self.old = kw, {}

    def __enter__(self):
        for k, v in self.kw.items():
            if k == "run":
                self.old[k] = DJ.subprocess.run
                DJ.subprocess.run = v
            elif k == "move":
                self.old[k] = shutil.move
                shutil.move = v
            else:
                self.old[k] = getattr(DJ, k, None)
                setattr(DJ, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            if k == "run":
                DJ.subprocess.run = v
            elif k == "move":
                shutil.move = v
            else:
                setattr(DJ, k, v)


RL = {"status": "failed", "worker_status": "worker_error", "elapsed_s": "12.5",
      "worker_stderr_tail": "ERROR: exceeded retry limit, last status: 429 Too Many Requests"}


def failjob(art, jid, man=None, dn="RM_Donor"):
    j = T.row(dn, id=jid, install_to=T.it(f"Things/{dn}"))
    (art / "failed" / f"{jid}.json").write_text(json.dumps(j))
    (art / "failed" / f"{jid}.manifest.json").write_text(json.dumps(man or RL))
    return j


def requeue_cases():
    root = T.build_repo()
    g = T.gate(root)

    # 12: the old failure manifest is archived before the job is visible; a fast worker's new failure survives
    art = new_art()
    jid = "dregen_RM_Donor_race_v1"
    failjob(art, jid, dict(RL, marker="FIRST"))

    def worker(dst):
        dst = Path(dst)
        os.replace(dst, art / "failed" / dst.name)
        (art / "failed" / f"{jid}.manifest.json").write_text(json.dumps(dict(RL, marker="SECOND")))
    real_move = shutil.move

    def move(src, dst):                                       # the pre-fix code published with shutil.move
        out = real_move(src, dst)
        if "/pending/" in str(dst):
            worker(dst)
        return out
    with patched(move=move, _after_publish=worker):
        DJ.requeue(art, 40, 10, False, g, journal=lambda: 0)
    parked = [json.loads(p.read_text()).get("marker") for p in (art / "_requeued_manifests").glob("*.json")]
    man = art / "failed" / f"{jid}.manifest.json"
    check(parked == ["FIRST"] and man.is_file() and json.loads(man.read_text()).get("marker") == "SECOND",
          "#12 the first failure manifest is archived and the worker's new failure manifest is kept",
          (parked, man.is_file()))

    # 13: a pending job created by someone else after the pool was built is never replaced
    art = new_art()
    jid = "dregen_RM_Donor_dup_v1"
    failjob(art, jid)
    real_ef = DJ.eligible_failed

    def ef(a, gg):
        out = real_ef(a, gg)
        (a / "pending" / f"{jid}.json").write_text(json.dumps({"id": jid, "marker": "OTHER"}))
        return out
    with patched(eligible_failed=ef):
        DJ.requeue(art, 40, 10, False, g, journal=lambda: 0)
    pj = json.loads((art / "pending" / f"{jid}.json").read_text())
    check(pj.get("marker") == "OTHER" and (art / "failed" / f"{jid}.json").is_file()
          and (art / "failed" / f"{jid}.manifest.json").is_file(),
          "#13 requeue never replaces a concurrently created pending job, and restores its own to failed/", pj)

    # 14: the first row's facings count against the cap too
    art = new_art()
    jf = art / "jobs.json"
    jf.write_text(json.dumps({"rows": [T.row("RM_None", install_to=T.it("Things/RM_None/RM_None_{facing}"),
                                             facings=["east", "south", "north"])]}))
    calls = []
    with patched(ART=art, in_flight=lambda: 39, queue_view=lambda: ({}, set()),
                 run=lambda *a, **k: calls.append(a) or subprocess.CompletedProcess(a, 0, "", "")):
        DJ.submit_one(jf, 40, False, g)
    check(not calls, "#14 with 39 in flight and cap 40, a three-facing row is not filed", calls)

    # 15: a 429 that arrives during the submits stops the requeue that follows
    art = new_art()
    failjob(art, "dregen_RM_Donor_bk_v1")
    seq = iter([0, 3, 3, 3])
    with patched(ART=art, in_flight=lambda: 0):
        DJ.submit([], 40, False, gate=g, journal=lambda: next(seq), requeue_pool=True)
    check(not list((art / "pending").iterdir()), "#15 submit's requeue re-reads the journal and backs off",
          list((art / "pending").iterdir()))

    # 16: "429" inside elapsed_s / a request id is not a rate limit
    art = new_art()
    failjob(art, "dregen_RM_Donor_403_v1", {"status": "failed", "worker_status": "worker_error",
                                            "elapsed_s": "43.64297429705039",
                                            "worker_stderr_tail": "HTTP 403 Forbidden (request id req_84291)"})
    failjob(art, "dregen_RM_Donor_429_v1")
    pool = {j["id"] for j, _ in DJ.eligible_failed(art, g)}
    check(pool == {"dregen_RM_Donor_429_v1"}, "#16 only a real 429 (worker error fields) qualifies for requeue", pool)

    # 18: repo-relative paths are POSIX on every OS
    try:
        r = DJ.rel_posix(PureWindowsPath(r"C:\r\src\RimMandrake\X\Defs\a.xml"), PureWindowsPath(r"C:\r"))
    except Exception as e:                                    # noqa: BLE001
        r = e
    check(r == "src/RimMandrake/X/Defs/a.xml" and "/Defs/" in r, "#18 a Windows path is matched as src/.../Defs/...", r)


# ─────────────────────────────────────────────────────────────── installer ──

FAKE_TOOL = r'''
import json, os, sys, time
from pathlib import Path
spec = json.loads(Path(os.environ["FAKE_SPEC"]).read_text())
cmd = sys.argv[1]
if spec.get("hang"):
    time.sleep(60)
if cmd == "plan":
    out = Path(sys.argv[sys.argv.index("--out") + 1])
    out.write_text(json.dumps({"rows": [{"dest": d} for d in spec["install"]], "retire": [],
                               "repoint": [{"xml": [spec["xml"]]}]}))
    sys.exit(0)
plan = Path(sys.argv[sys.argv.index("--plan") + 1])
root = Path.cwd()
for d in spec["install"]:
    (root / d).parent.mkdir(parents=True, exist_ok=True)
    (root / d).write_bytes(("render " + d).encode())
x = root / spec["xml"]
x.write_text(x.read_text().replace(spec["old"], spec["new"]))
with (root / spec["events"]).open("a") as fh:
    fh.write(json.dumps({"type": "live", "rel": spec["install"][0]}) + "\n")
log = plan.with_suffix(".applied.json")
log.write_text(json.dumps({"installed": spec["install"], "repointed": [spec["xml"]], "retired": [], "refused": []}))
print("log:", log)
'''

FAKE_PUBLISH = r'''
import subprocess, sys
from pathlib import Path
with open(Path(sys.argv[1]), "a") as fh:
    fh.write("published\n")
r = subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], capture_output=True, text=True)
print("PUBLISHED" if r.returncode == 0 else r.stderr)
sys.exit(r.returncode)
'''

EVT = "infrastructure/state/art/events/FOUNDRY.jsonl"
XML = "src/M/Defs/a.xml"


def g(repo, *a, check_rc=True, env=None):
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                GIT_COMMITTER_EMAIL="t@t", **(env or {})))
    if check_rc and r.returncode:
        raise RuntimeError(f"git {a}: {r.stderr}")
    return r.stdout


def fake_repo():
    base = Path(tempfile.mkdtemp(prefix="hourly_"))
    origin, work = base / "origin.git", base / "work"
    g(base, "init", "-q", "--bare", "-b", "main", str(origin))
    g(base, "init", "-q", "-b", "main", str(work))
    g(work, "remote", "add", "origin", str(origin))
    (work / "src/M/Defs").mkdir(parents=True)
    (work / "src/M/Textures").mkdir(parents=True)
    (work / XML).write_text("<Defs>\n<ThingDef>\n<description>old words</description>\n<x/>\n<y/>\n<z/>\n"
                            "<texPath>Old/Tex</texPath>\n</ThingDef>\n</Defs>\n")
    (work / "src/M/Textures/Icon1.png").write_bytes(b"icon1")
    (work / EVT).parent.mkdir(parents=True)
    (work / EVT).write_text('{"type": "first"}\n')
    (work / ".gitignore").write_text("Transient/\n")
    (work / "Transient").mkdir()
    paths = [XML, "src/M/Textures/Icon1.png", EVT, ".gitignore"]
    g(work, "update-index", "--add", "--", *paths)
    g(work, "commit", "-q", "-m", "init")
    g(work, "push", "-q", "origin", "main")
    (base / "tool.py").write_text(FAKE_TOOL)
    (base / "publish.py").write_text(FAKE_PUBLISH)
    return base, work


def run_installer(base, work, spec):
    (base / "spec.json").write_text(json.dumps(dict({"events": EVT, "xml": XML, "old": "Old/Tex", "new": "New/Tex"},
                                                    **spec)))
    os.environ["FAKE_SPEC"] = str(base / "spec.json")
    marker = base / "published.txt"
    under = os.environ.get("INSTALLER_UNDER_TEST")
    if under:                                                 # a previous version, run as a script in the fake repo
        d = work / "src/RimMandrake/Utils/art"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(under, d / "donor_regen_install_hourly.py")
        shutil.copy(base / "tool.py", d / "bulk_accept_renders.py")
        (work / "publish").write_text(f"#!/bin/sh\nexec {sys.executable} {base / 'publish.py'} {marker}\n")
        (work / "publish").chmod(0o755)
        subprocess.run([sys.executable, str(d / "donor_regen_install_hourly.py")], cwd=work, capture_output=True,
                       timeout=120, env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                                             GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))
        return
    import donor_regen_install_hourly as H
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        H.main([], repo=work, tool=str(base / "tool.py"), publish=(sys.executable, str(base / "publish.py"), str(marker)),
               events=EVT)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def published(base):
    m = base / "published.txt"
    return m.read_text().count("published") if m.exists() else 0


def installer_cases():
    base, work = fake_repo()
    # someone else's uncommitted work, made before the hourly run
    xml = (work / XML).read_text().replace("old words", "OWNER EDIT")
    (work / XML).write_text(xml)
    with (work / EVT).open("a") as fh:
        fh.write('{"type": "foreign"}\n')
    (work / "src/M/Textures/Icon1.png").write_bytes(b"icon1 foreign edit")
    (work / "src/M/staged.txt").write_text("staged by someone\n")
    g(work, "update-index", "--add", "--", "src/M/staged.txt")
    head0 = g(work, "rev-parse", "HEAD").strip()
    run_installer(base, work, {"install": ["src/M/Textures/Icon[1].png", "src/M/Textures/New.png"]})
    head1 = g(work, "rev-parse", "HEAD").strip()
    files = g(work, "diff", "--name-only", head0, head1).split() if head1 != head0 else []
    cx = g(work, "show", f"{head1}:{XML}", check_rc=False)
    ce = g(work, "show", f"{head1}:{EVT}", check_rc=False)
    check(head1 != head0 and "New/Tex" in cx and "old words" in cx and "OWNER EDIT" not in cx,
          "#8 the repointed XML commits only the installer's edit, not the owner's description edit", cx[:200])
    check('"foreign"' not in ce and '"live"' in ce and '"first"' in ce,
          "#8 the events shard commits only the lines this run appended", ce)
    check("OWNER EDIT" in (work / XML).read_text() and '"foreign"' in (work / EVT).read_text(),
          "#8 the owner's uncommitted edits stay in the worktree")
    check("src/M/Textures/Icon1.png" not in files and "src/M/Textures/Icon[1].png" in files,
          "#11 Icon[1].png is committed literally; the foreign Icon1.png edit is not", files)
    check("src/M/staged.txt" not in files, "#9 a file someone else staged does not ride along", files)
    staged = g(work, "diff", "--cached", "--name-only").split()
    check(staged == ["src/M/staged.txt"], "#9 the shared index keeps their staged file and shows no reversion of ours",
          staged)
    pub = published(base)
    check(pub == 1, "#10 publish runs when the only unpublished commit is the installer's own", pub)

    # 10: a foreign local commit ahead of origin/main -> the installer commits but does not publish
    (work / "src/M/other.txt").write_text("someone else's commit\n")
    g(work, "update-index", "--add", "--", "src/M/other.txt")
    g(work, "commit", "-q", "-m", "someone else's unpublished commit", "--", "src/M/other.txt")
    run_installer(base, work, {"install": ["src/M/Textures/Later.png"], "old": "New/Tex", "new": "Newer/Tex"})
    pub2 = published(base)
    remote = g(work, "ls-remote", "origin", "main").split()[0]
    check(pub2 == 1 and remote == head1, "#10 a foreign unpublished commit blocks publish (logged, skipped)",
          (pub2, remote[:9], head1[:9]))

    # 9: a commit that fails (here: a refusing pre-commit hook) must not leave the run's paths staged in the shared index
    base, work = fake_repo()
    hook = work / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    run_installer(base, work, {"install": ["src/M/Textures/H.png"]})
    staged = g(work, "diff", "--cached", "--name-only").split()
    check(staged == [], "#9 after the hourly run nothing of its own is left staged in the shared index", staged)

    # timeouts: a hung child ends the run, nothing committed
    if not os.environ.get("INSTALLER_UNDER_TEST"):
        import donor_regen_install_hourly as H
        base, work = fake_repo()
        head0 = g(work, "rev-parse", "HEAD").strip()
        old = H.TIMEOUT["tool"]
        H.TIMEOUT["tool"] = 2
        try:
            run_installer(base, work, {"install": ["src/M/Textures/X.png"], "hang": True})
        finally:
            H.TIMEOUT["tool"] = old
        log = (work / "Transient/donor_regen_install.log").read_text()
        check(g(work, "rev-parse", "HEAD").strip() == head0 and "TIMEOUT" in log,
              "timeouts: a hung bulk_accept child is killed and logged; nothing committed", log[-200:])

        # compare-and-swap: someone commits while the hourly commit is being built -> theirs stays, ours waits
        base, work = fake_repo()

        class Racy(H.Run):
            def commit(self, head, changes, n):
                (self.repo / "src/M/race.txt").write_text("race\n")
                g(self.repo, "update-index", "--add", "--", "src/M/race.txt")
                g(self.repo, "commit", "-q", "-m", "racer", "--", "src/M/race.txt")
                return super().commit(head, changes, n)
        (base / "spec.json").write_text(json.dumps({"events": EVT, "xml": XML, "old": "Old/Tex", "new": "New/Tex",
                                                    "install": ["src/M/Textures/R.png"]}))
        os.environ["FAKE_SPEC"] = str(base / "spec.json")
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        os.environ.update(env)
        R = Racy(repo=work, tool=str(base / "tool.py"), publish=("true",), events=EVT)
        try:
            R.main()
        except H.Stop as e:
            R.log(f"STOP: {e}")
        msg = g(work, "log", "-1", "--format=%s")
        check(msg.strip() == "racer" and g(work, "diff", "--cached", "--name-only").strip() == "",
              "#9 a commit that lands mid-run is never reverted; the hourly commit is refused and nothing is staged",
              msg)


def main() -> int:
    gate_cases()
    requeue_cases()
    installer_cases()
    print(f"\n{'FAILED' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
