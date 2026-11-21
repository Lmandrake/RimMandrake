#!/usr/bin/env python3
"""selftest_preflight.py - preflight.py (RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME) against the REAL modset_builder.

Cases: no marker; mid-swap valid (live == tier_md5: no refusal, marker untouched); marker whose before-copy is gone
(the 2026-11-12 stale marker) -> moved aside + noted, fix off -> refusal; live list neither tier nor before-copy (the
2026-11-06 case); stale marker with live == before-copy (not a refusal); a DLL that no longer matches its C# (temp git
repo); a proofs clause without its `live-proof` line; TESTQ_PREFLIGHT=0; and the worker: a refusal ends the job
REFUSED/PREFLIGHT with no attempt spawned. Each is meant to fail with the check removed (see MUTANT below).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
import preflight as P  # noqa: E402
import schema as S  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def tier_job(tier="pyrelands"):
    return {"id": "J1", "item": "X", "mod": "RM_Pyrelands", "profile": "tier:" + tier, "source_sha": "0" * 40,
            "selector": {"chains": ["a"]}}


MB = P.load_modset_builder(RUNNER)
check(MB is not None, "real modset_builder imports")


def world(kind):
    """-> (config, backups) for a swap scenario."""
    t = tempfile.mkdtemp(prefix="pf_world_")
    bk = os.path.join(t, "backups")
    os.makedirs(bk)
    cfg = os.path.join(t, "ModsConfig.xml")
    owner = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>owner.mod</li></activeMods></ModsConfigData>"
    tierl = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>tier.mod</li></activeMods></ModsConfigData>"
    other = "<ModsConfigData><activeMods><li>ludeon.rimworld</li><li>hand.edited</li></activeMods></ModsConfigData>"
    before = os.path.join(bk, "ModsConfig.before-tier-x.xml")
    open(before, "w").write(owner)
    tpath = os.path.join(t, "tier.xml")
    open(tpath, "w").write(tierl)
    marker = {"tier": "x", "before": os.path.basename(before), "md5": md5(before), "tier_md5": md5(tpath)}
    if kind == "none":
        os.remove(before)
        return cfg_w(cfg, owner), bk
    open(os.path.join(bk, MB.SWAP_MARKER), "w").write(json.dumps(marker))
    if kind == "mid":
        return cfg_w(cfg, tierl), bk
    if kind == "stale_owner_back":
        return cfg_w(cfg, owner), bk
    if kind == "before_gone":
        os.remove(before)
        return cfg_w(cfg, other), bk
    if kind == "neither":
        return cfg_w(cfg, other), bk
    raise ValueError(kind)


def cfg_w(cfg, text):
    open(cfg, "w").write(text)
    return cfg


def run_swap(kind, env=None):
    cfg, bk = world(kind)
    r = P.check_swap_marker(tier_job(), MB, cfg, bk, fix=(env or {}).get("fix", True))
    return r, bk


marker_of = lambda bk: os.path.join(bk, MB.SWAP_MARKER)  # noqa: E731
(r, bk) = run_swap("none")
check(r == (None, None), "no marker: nothing to do")
(r, bk) = run_swap("mid")
check(r == (None, None) and os.path.exists(marker_of(bk)), "mid-swap valid (live == tier list): no refusal, marker untouched")
(r, bk) = run_swap("stale_owner_back")
check(r == (None, None) and os.path.exists(marker_of(bk)), "stale marker but the owner's list is back: the real swap proceeds, no refusal")
(r, bk) = run_swap("before_gone")
check(r[0] is None and r[1] and "moved aside" in r[1] and not os.path.exists(marker_of(bk))
      and any(f.startswith(MB.SWAP_MARKER + ".stale-") for f in os.listdir(bk)),
      "before-copy gone (2026-11-12): marker moved aside to .stale-*, fix noted, no refusal")
(r, bk) = run_swap("neither")
check(r[0] is None and r[1] and not os.path.exists(marker_of(bk)), "live list neither tier nor before (2026-11-06): moved aside, noted")
(r, bk) = run_swap("before_gone", {"fix": False})
check(r[0] and "swap marker blocks" in r[0] and os.path.exists(marker_of(bk)), "fix off: refusal names the marker, marker left in place")
# an unreadable marker is also what take_before_copy refuses
cfg, bk = world("mid")
open(marker_of(bk), "w").write("{not json")
r = P.check_swap_marker(tier_job(), MB, cfg, bk, fix=True)
check(r[0] is None and r[1] and not os.path.exists(marker_of(bk)), "unreadable marker: moved aside")
# non-tier job: never looks
j = tier_job()
j["profile"] = "default"
cfg, bk = world("before_gone")
check(P.check_swap_marker(j, MB, cfg, bk) == (None, None) and os.path.exists(marker_of(bk)), "non-tier job: marker untouched")

# check(): whole-entry behaviour, env switches
cfg, bk = world("before_gone")
res = P.check(tier_job(), RUNNER, clone=tempfile.mkdtemp(), config=cfg, backups=bk, env={"TESTQ_PREFLIGHT": "0"})
check(res["refused"] == [] and os.path.exists(marker_of(bk)), "TESTQ_PREFLIGHT=0: nothing runs")
cfg, bk = world("before_gone")
res = P.check(tier_job(), RUNNER, clone=tempfile.mkdtemp(), config=cfg, backups=bk, env={"TESTQ_PREFLIGHT_MARKER_FIX": "0"})
check(any(n == "swap_marker" for n, _ in res["refused"]) and "swap_marker" in P.note_of(res), "marker fix off through check(): refused, named in note")
cfg, bk = world("before_gone")
res = P.check(tier_job(), RUNNER, clone=tempfile.mkdtemp(), config=cfg, backups=bk, env={})
check(not [x for x in res["refused"] if x[0] == "swap_marker"] and res["fixed"], "check(): marker fixed, listed in fixed")

# dll_current + proof_lines on a temp git repo
repo = tempfile.mkdtemp(prefix="pf_repo_")
G = ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t"]


def git(*a):
    return subprocess.run(G + list(a), capture_output=True, text=True, check=True).stdout.strip()


git("init", "-q", "-b", "main")
md = os.path.join(repo, "src", "RimMandrake", "M")
os.makedirs(os.path.join(md, "About"))
os.makedirs(os.path.join(md, "Source"))
os.makedirs(os.path.join(md, "Assemblies"))
os.makedirs(os.path.join(repo, "infrastructure", "state", "live_proofs"))
open(os.path.join(md, "About", "About.xml"), "w").write("<ModMetaData><packageId>mandrake.x.m</packageId></ModMetaData>")
open(os.path.join(md, "Source", "A.cs"), "w").write("class A{}\n")
open(os.path.join(md, "Source", "M.csproj"), "w").write(
    '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>M</AssemblyName></PropertyGroup></Project>\n')
open(os.path.join(md, "Assemblies", "M.dll"), "wb").write(b"MZ")
open(os.path.join(repo, "infrastructure", "state", "live_proofs", "X.txt"), "w").write("live-proof P1: do thing\n")
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils"))
import dll_source_stamp as D  # noqa: E402
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
STAMP = "src/RimMandrake/M/Assemblies/M.dll.srchash"
open(os.path.join(repo, STAMP), "w").write("# project: RimMandrake/M/Source/M.csproj\n# dll: %s\n%s A.cs\n" % (
    sha(b"MZ"), sha(b"class A{}\n")))
git("add", "-A")
git("commit", "-q", "-m", "base")
base = git("rev-parse", "HEAD")
job = {"id": "J2", "item": "X", "mod": "M", "profile": "default", "source_sha": base, "selector": {"chains": ["a"]}}
r = P.check_dll_current(job, repo)
check(r == (None, None), "dll_current: DLL matches its source -> no refusal (got %r)" % (r,))
open(os.path.join(md, "Source", "A.cs"), "w").write("class A{int x;}\n")
git("commit", "-q", "-am", "edit source, no rebuild")
job2 = dict(job, source_sha=git("rev-parse", "HEAD"))
r = P.check_dll_current(job2, repo)
check(r[0] and "older than its source" in r[0], "dll_current: edited C# without a rebuild -> refusal")
git("revert", "--no-edit", "HEAD")
open(os.path.join(md, "Source", "B.cs"), "w").write("class B{}\n")
git("add", "-A")
git("commit", "-q", "-m", "new source file")
r = P.check_dll_current(dict(job, source_sha=git("rev-parse", "HEAD")), repo)
check(r[0] and "older than its source" in r[0], "dll_current: new .cs file compiled but not in the stamp -> refusal")
r = P.check(dict(job2), RUNNER, clone=repo, config=os.path.join(tempfile.mkdtemp(), "none"), backups=tempfile.mkdtemp(), env={})
check(any(n == "dll_current" for n, _ in r["refused"]), "check(): dll_current refusal reaches the result")

# proof_lines
pj = {"id": "J3", "item": "X", "mod": "M", "profile": "default", "source_sha": base,
      "selector": {"proofs": ["P1"]}}
check(P.check_proof_lines(pj, repo) is None, "proof_lines: clause with its line -> ok")
pj2 = dict(pj, selector={"proofs": ["P1", "P9"]})
w = P.check_proof_lines(pj2, repo)
check(w and "P9" in w, "proof_lines: missing clause named")
check(P.check_proof_lines(dict(pj, item="NOPE"), repo), "proof_lines: no proofs file -> refusal")
check(P.check_proof_lines(job, repo) is None, "proof_lines: a chains job is not checked")


# audio_driver (RIMMANDRAKE_DISABLE_STEVE_SONIC_STUDIO_DRIVER_SOUND_IS_UNUSED): the Sonic Studio driver's silent return is refused
class Out:
    def __init__(self, rc, out, err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def fake_runner(reg, sc):
    return lambda argv, **kw: reg if argv[0].endswith("reg.exe") else sc


REG4 = Out(0, "\nHKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\AVoluteSS3Vad\n    Start    REG_DWORD    0x4\n\n")
REG3 = Out(0, REG4.stdout.replace("0x4", "0x3"))
REGNONE = Out(1, "", "ERROR: The system was unable to find the specified registry key or value.\n")
SCSTOP = Out(1062, "\nSERVICE_NAME: AVoluteSS3Vad\n        TYPE               : 1  KERNEL_DRIVER\n        STATE              : 1  STOPPED\n")
SCRUN = Out(0, SCSTOP.stdout.replace("1  STOPPED", "4  RUNNING"))
SCNONE = Out(1060, "[SC] EnumQueryServicesStatus:OpenService FAILED 1060:\n\nThe specified service does not exist as an installed service.\n")
check(P.read_driver(runner=fake_runner(REG4, SCSTOP)) == (4, "STOPPED"), "read_driver: Start=4, STOPPED")
check(P.read_driver(runner=fake_runner(REG3, SCRUN)) == (3, "RUNNING"), "read_driver: Start=3, RUNNING")
check(P.read_driver(runner=fake_runner(REGNONE, SCNONE)) == (None, "ABSENT"), "read_driver: no such service")
for bad, what in ((Out(5, "", "Access is denied."), "reg.exe error"), (Out(0, "garbage"), "reg.exe no Start line")):
    try:
        P.read_driver(runner=fake_runner(bad, SCSTOP))
        check(False, "read_driver raises on " + what)
    except ValueError:
        check(True, "read_driver raises on " + what)
try:
    P.read_driver(runner=fake_runner(REG4, Out(0, "nothing")))
    check(False, "read_driver raises on sc.exe with no STATE")
except ValueError:
    check(True, "read_driver raises on sc.exe with no STATE")
check([P.driver_verdict(*x) for x in ((4, "STOPPED"), (None, "ABSENT"), (3, "RUNNING"), (4, "RUNNING"), (3, "STOPPED"), (None, "STOPPED"))]
      == ["OFF", "ABSENT", "LOADED", "LOADED", "ENABLED", "ENABLED"], "driver_verdict table")
check(P.check_audio_driver(lambda: (4, "STOPPED")) == (None, None), "audio_driver: off -> no refusal")
check(P.check_audio_driver(lambda: (None, "ABSENT")) == (None, None), "audio_driver: no such driver (Archmagi) -> no refusal")
r = P.check_audio_driver(lambda: (3, "RUNNING"))
check(r[0] and "LOADED" in r[0] and "/d 4" in r[0], "audio_driver: loaded -> refusal naming the cure")
r = P.check_audio_driver(lambda: (3, "STOPPED"))
check(r[0] and "re-enabled" in r[0], "audio_driver: re-enabled, not yet loaded -> refusal")


def blind():
    raise OSError("no interop")


r = P.check_audio_driver(blind)
check(r[0] is None and r[1] and "cannot read" in r[1], "audio_driver: unreadable -> skipped, never refused")
nojob = {"id": "J2", "item": "X", "mod": "RM_Nothing", "profile": "full", "source_sha": "0" * 40, "selector": {"chains": ["a"]}}
noclone = tempfile.mkdtemp()
res = P.check(nojob, RUNNER, clone=noclone, env={}, audio_read=lambda: (3, "RUNNING"))
check(any(n == "audio_driver" for n, _ in res["refused"]) and "audio_driver" in P.note_of(res), "check(): a loaded driver is refused, named in note")
res = P.check(nojob, RUNNER, clone=noclone, env={"TESTQ_PREFLIGHT_AUDIO_DRIVER": "0"}, audio_read=lambda: (3, "RUNNING"))
check(not [x for x in res["refused"] if x[0] == "audio_driver"], "TESTQ_PREFLIGHT_AUDIO_DRIVER=0: the driver check does not run")
res = P.check(nojob, RUNNER, clone=noclone, env={}, audio_read=lambda: (4, "STOPPED"))
check(not [x for x in res["refused"] if x[0] == "audio_driver"], "check(): driver off -> no audio_driver refusal")
res = P.check(nojob, RUNNER, clone=noclone, env={}, audio_read=blind)
check(any(s.startswith("audio_driver: cannot read") for s in res["skipped"]), "check(): unreadable driver state is listed in skipped")

# worker: a refusal is a finished REFUSED/PREFLIGHT attempt, nothing spawned
check("PREFLIGHT" in S.CAUSES, "schema CAUSES has PREFLIGHT")
src = open(os.path.join(HERE, "worker.py")).read()
check('cause="PREFLIGHT"' in src and src.index("preflight_job(job, d)") < src.index("spawn("), "worker.cmd_start refuses before it spawns")
print("\n%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
