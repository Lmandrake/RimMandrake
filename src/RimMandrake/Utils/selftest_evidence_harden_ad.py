#!/usr/bin/env python3
"""selftest_evidence_harden_ad.py -- GPT review AD of the close-evidence chain, one check group per finding
(item EVIDENCE_COVERS_HARDEN_REVIEW_AD_SIX_MORE). Each group failed before its fix.

  AD1 run_selftests runs a test with cwd = the TESTED checkout (its own clone), special invocations included
  AD2 a cached PASS (the test did not run) is never fresh close evidence: not in paths, not in covers
  AD3 a winbuild PASS covers the csproj and the compile items its own .srchash stamp lists (hash-checked), nothing else
  AD4 declared csproj covers honour Compile Remove / Exclude; Conditions, Imports, properties, legacy projects and a
      Directory.Build file that touches Compile fail closed (the csproj only)
  AD5 FAIL -> PASS -> FAIL written in the same second by the same process stays three records (per-record nonce)
  AD6 an abbreviated sha that is ambiguous in a clone, or that any clone could not answer for, is UNMEASURED

    python3 src/RimMandrake/Utils/selftest_evidence_harden_ad.py
"""
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import close_evidence as CE  # noqa: E402

SCRATCH = Path("/home/mandrake/rm/scratch/BENCH")
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(repo, *a, inp=None):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a], input=inp,
                          capture_output=True, text=True, check=True).stdout.strip()


def iso_mark(repo):
    """Stamp a fixture clone as an isolated checkout of its HEAD (what CE.make_isolated leaves behind)."""
    sha = git(repo, "rev-parse", "HEAD")
    (Path(repo) / ".git" / CE.ISOLATED_MARK).write_text(
        hmac.new(CE._key(create=True), CE._iso_msg(repo, sha), hashlib.sha256).hexdigest())
    return sha


def make_repo(root, files):
    repo = Path(root) / "clone"
    repo.mkdir()
    git(repo, "init", "-q")
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fixture")
    return repo, iso_mark(repo)


# ---------------------------------------------------------------------------------------------------- AD1
def ad1(root):
    import run_selftests as RS
    probe = ("import os, sys\nhere = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
             "print('CWD', os.getcwd())\nsys.exit(0 if os.path.realpath(os.getcwd()) == os.path.realpath(here) "
             "and os.path.exists('src/ONLY_IN_TESTED_CHECKOUT') else 1)\n")
    repo, _ = make_repo(root, {"src/selftest_cwd.py": probe, "src/ONLY_IN_TESTED_CHECKOUT": "x\n",
                               "src/selftest_special.py": "raise SystemExit(9)\n"})
    r = RS._run_one(repo / "src" / "selftest_cwd.py")
    check(r[1] == "PASS", "AD1 a test in another checkout runs with cwd = that checkout: %s %s" % (r[1], r[3][:160]))
    seen = []

    def special(root=None):
        seen.append(root)
        return [sys.executable, "-c", "import os; print('SPECIAL', os.getcwd())"], root
    real = RS.SPECIAL_INVOCATIONS
    RS.SPECIAL_INVOCATIONS = {"src/selftest_special.py": special}
    try:
        r = RS._run_one(repo / "src" / "selftest_special.py")
    finally:
        RS.SPECIAL_INVOCATIONS = real
    check(r[1] == "PASS" and seen and os.path.realpath(str(seen[0])) == os.path.realpath(repo),
          "AD1 a special invocation is looked up and built for the tested checkout: %s %r" % (r[1], seen))
    r = RS._run_one(RS.REPO_ROOT / "src" / "RimMandrake" / "Utils" / "selftest_evidence_harden_ad.py",
                    env=dict(os.environ, AD_CWD_PROBE="1"))
    check(r[1] == "PASS", "AD1 a test in the instrument clone still runs from the instrument clone: %s" % r[1])


# ---------------------------------------------------------------------------------------------------- AD2
def ad2(root, store):
    import run_selftests as RS
    import selftest_cache as SC
    repo, sha = make_repo(root, {"src/selftest_ran.py": "print('ok')\n", "src/selftest_hit.py": "print('ok')\n",
                                 "src/M.csproj": "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
                                 "src/A.cs": "class A {}\n"})
    t_ran, t_hit = repo / "src" / "selftest_ran.py", repo / "src" / "selftest_hit.py"
    real_decls = SC.DECLS
    SC.DECLS = dict(real_decls, **{"src/selftest_hit.py": {"csproj": "src/M.csproj"}})
    RS._OUTER[0] = True
    os.environ[RS.COVERS_ENV] = "1"
    try:
        RS._evidence_start([t_ran, t_hit])
        before = len(CE.read_all(folder=store))
        RS._record_evidence([(t_ran, "PASS", 1.0, ""), (t_hit, "PASS", 0.0, "cached")])
        new = CE.read_all(folder=store)[before:]
        rec = new[0] if new else {}
        check(len(new) == 1 and rec.get("paths") == ["src/selftest_ran.py"],
              "AD2 a cached PASS is not among the record's paths: %r" % (rec.get("paths"),))
        check(not CE.covered(rec, ["src/selftest_hit.py", "src/A.cs", "src/M.csproj"]),
              "AD2 nothing the cached test declares is covered: %r" % (rec.get("covers"),))
        check((rec.get("detail") or {}).get("not_run_cached") == ["src/selftest_hit.py"],
              "AD2 the cached test is named in detail.not_run_cached: %r" % ((rec.get("detail") or {}).keys(),))
        RS._evidence_start([t_hit])
        before = len(CE.read_all(folder=store))
        RS._record_evidence([(t_hit, "PASS", 0.0, "cached")])
        check(len(CE.read_all(folder=store)) == before, "AD2 an all-cached run writes no record at all")
        check(CE.lookup(sha=sha, paths=["src/selftest_hit.py"]) == [], "AD2 lookup finds no evidence for the cache hit")
    finally:
        SC.DECLS = real_decls
        RS._OUTER[0] = None
        os.environ.pop(RS.COVERS_ENV, None)


# ---------------------------------------------------------------------------------------------------- AD3
def ad3(root, store):
    files = {"src/Mod/Source/M.csproj": "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>\n",
             "src/Mod/Source/A.cs": "class A {}\n", "src/Mod/Source/B.cs": "class B {}\n",
             "src/Mod/Source/C.cs": "class C {}\n", "src/tool.py": "x = 1\n"}
    repo, sha = make_repo(root, files)
    h = lambda rel: hashlib.sha256((repo / rel).read_bytes()).hexdigest()
    import winbuild as W
    old = W.ROOT
    W.ROOT = os.path.realpath(repo)
    s0 = W._ce_snapshot(["src/"])          # the stage snapshot; the stamps below are the build's copy-back
    stamp = repo / "src" / "Mod" / "Assemblies" / "M.dll.srchash"
    stamp.parent.mkdir(parents=True)
    stamp.write_text("# project: Mod/Source/M.csproj\n# dll: %s\n%s A.cs\n%s B.cs\n%s ../../tool.py\n"
                     % ("0" * 64, h("src/Mod/Source/A.cs").upper(), "f" * 64, h("src/tool.py")))
    other = repo / "src" / "Mod" / "Assemblies" / "Other.dll.srchash"
    other.write_text("# project: Other/Other.csproj\n# dll: %s\n%s C.cs\n" % ("0" * 64, h("src/Mod/Source/C.cs")))
    try:
        before = len(CE.read_all(folder=store))
        W.evidence_report(str(repo / "src/Mod/Source/M.csproj"), 0, "Release",
                          {"staged": True, "ev_start": s0, "ev_end": s0, "ev_scope": ["src/"],
                           "outputs": ["src/Mod/Assemblies/M.dll.srchash", "src/Mod/Assemblies/Other.dll.srchash"]})
        new = CE.read_all(folder=store)[before:]
        rec = new[0] if new else {}
        check(rec.get("result") == "PASS" and CE.counts_as_evidence(rec), "AD3 the staged build is evidence")
        check(CE.covered(rec, ["src/Mod/Source/M.csproj", "src/Mod/Source/A.cs"])
              == ["src/Mod/Source/M.csproj", "src/Mod/Source/A.cs"],
              "AD3 the csproj and a stamped compile item (hash matches the clone) are covered: %r" % rec.get("covers"))
        for f, why in (("src/tool.py", "a .py under the staged dir"), ("src/Mod/Source/C.cs", "an unstamped .cs"),
                       ("src/Mod/Source/B.cs", "a stamped item whose hash is not the clone's"),
                       ("src/Mod/Source/Z.cs", "a file under the project folder")):
            check(not CE.covered(rec, [f]), "AD3 %s is NOT covered (%s)" % (f, why))
        W.evidence_report(str(repo / "src/Mod/Source/M.csproj"), 0, "Release",
                          {"staged": True, "ev_start": s0, "ev_end": s0, "ev_scope": ["src/"], "outputs": []})
        rec2 = CE.read_all(folder=store)[-1]
        check(CE.covered(rec2, ["src/Mod/Source/A.cs", "src/tool.py"]) == [],
              "AD3 a build with no stamp covers no source, only its csproj: %r" % rec2.get("covers"))
    finally:
        W.ROOT = old
    base = {"tool": "winbuild", "paths": ["src/Mod/Source/M.csproj"], "detail": {}}
    check(not CE.covered(dict(base, covers=["src/Mod/Source/M.csproj", "src"]), ["src/tool.py"]),
          "AD3 a winbuild covers FOLDER (old record, or forged) covers nothing beneath it")
    check(not CE.covered(dict(base, tool="validate_patch", covers=["Patches/a.xml", "src"]), ["src/tool.py"]),
          "AD3 any tool's covers entry beyond its paths matches only as itself")
    check(CE.covered(dict(base, tool="selftest", paths=["src"], covers=["src"]), ["src/a.py"]) == ["src/a.py"],
          "AD3 a path a non-build tool was pointed at still covers as a folder")


# ---------------------------------------------------------------------------------------------------- AD4
def ad4(root):
    import evidence_covers as EC
    repo = Path(root) / "csproj"
    SDK = "<Project Sdk=\"Microsoft.NET.Sdk\">\n%s\n</Project>\n"
    projects = {
        "remove": SDK % "<ItemGroup><Compile Remove=\"old/**\" /></ItemGroup>",
        "exclude": SDK % ("<PropertyGroup><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup>"
                          "<ItemGroup><Compile Include=\"*.cs\" Exclude=\"skip.cs\" /></ItemGroup>"),
        "cond_item": SDK % "<ItemGroup Condition=\"'$(Configuration)'=='Debug'\"><Compile Include=\"A.cs\" /></ItemGroup>",
        "cond_compile": SDK % "<ItemGroup><Compile Remove=\"A.cs\" Condition=\"'$(X)'=='1'\" /></ItemGroup>",
        "cond_prop": SDK % ("<PropertyGroup Condition=\"'$(X)'=='1'\"><EnableDefaultCompileItems>false"
                            "</EnableDefaultCompileItems></PropertyGroup>"),
        "prop_ref": SDK % "<ItemGroup><Compile Remove=\"$(Junk)/**\" /></ItemGroup>",
        "import": SDK % "<Import Project=\"extra.props\" />",
        "excludes_prop": SDK % "<PropertyGroup><DefaultItemExcludes>$(DefaultItemExcludes);x/**</DefaultItemExcludes></PropertyGroup>",
        "legacy": "<Project ToolsVersion=\"15.0\"><ItemGroup><Compile Include=\"A.cs\" /></ItemGroup></Project>\n",
        "legacy_nothing": "<Project ToolsVersion=\"15.0\"></Project>\n",
        "unparsable": "<Project Sdk=\"Microsoft.NET.Sdk\"><ItemGroup>\n",
        "conditioned_ref": SDK % ("<ItemGroup><Reference Include=\"H\" Condition=\"'$(H)'==''\" /></ItemGroup>"
                                  "<PropertyGroup Condition=\"'$(H)'==''\"><H>x</H></PropertyGroup>"),
    }
    for name, text in projects.items():
        d = repo / name
        (d / "old").mkdir(parents=True)
        (d / "OLD2").mkdir()
        (d / "bin").mkdir()
        (d / ".hidden").mkdir()
        for f in ("A.cs", "skip.cs", "old/O.cs", "OLD2/P.cs", "bin/G.cs", ".hidden/H.cs"):
            (d / f).write_text("class X {}\n")
        (d / ("%s.csproj" % name)).write_text(text)
    got = {n: sorted(x.split("/", 1)[1] for x in EC._csproj_sources(repo, "%s/%s.csproj" % (n, n))) for n in projects}
    print("     AD4 got: %s" % json.dumps(got, sort_keys=True))
    cs = lambda n: [x for x in got[n] if x.endswith(".cs")]
    check(cs("remove") == ["A.cs", "OLD2/P.cs", "skip.cs"], "AD4 Compile Remove=\"old/**\" drops old/O.cs: %r" % cs("remove"))
    check(cs("exclude") == ["A.cs"], "AD4 Include=\"*.cs\" Exclude=\"skip.cs\" drops skip.cs: %r" % cs("exclude"))
    for n in ("cond_item", "cond_compile", "cond_prop", "prop_ref", "import", "excludes_prop", "legacy", "unparsable"):
        check(got[n] == ["%s.csproj" % n], "AD4 %s fails closed (csproj only): %r" % (n, got[n]))
    check(cs("legacy_nothing") == [], "AD4 a non-SDK project gets no default **/*.cs: %r" % cs("legacy_nothing"))
    check(cs("conditioned_ref") == ["A.cs", "OLD2/P.cs", "old/O.cs", "skip.cs"],
          "AD4 a Condition on a Reference/unrelated property does not close the project: %r" % cs("conditioned_ref"))
    # case: Windows MSBuild matches Remove case-insensitively; so must we (a miss would over-credit)
    d = repo / "remove"
    (d / "remove.csproj").write_text(SDK % "<ItemGroup><Compile Remove=\"OLD/**;Skip.CS\" /></ItemGroup>")
    got2 = sorted(x.split("/", 1)[1] for x in EC._csproj_sources(repo, "remove/remove.csproj"))
    check(got2 == ["A.cs", "OLD2/P.cs", "remove.csproj"], "AD4 Remove matches case-insensitively, ';' lists (OLD/** is not OLD2/): %r" % got2)
    # a Directory.Build.props/targets between the project and the repo root that touches Compile closes it
    (repo / "Directory.Build.props").write_text("<Project><ItemGroup><Compile Remove=\"**/A.cs\" /></ItemGroup></Project>")
    got3 = sorted(EC._csproj_sources(repo, "remove/remove.csproj"))
    check(got3 == ["remove/remove.csproj"], "AD4 a Directory.Build file touching Compile fails closed: %r" % got3)


# ---------------------------------------------------------------------------------------------------- AD5
def ad5(root, store):
    import datetime
    repo, sha = make_repo(root, {"src/a.py": "x = 1\n"})
    fixed = datetime.datetime(2026, 10, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    real = CE.build_record
    CE.build_record = lambda *a, **k: real(*a, **dict(k, now=fixed))
    try:
        st = CE.snapshot(repo)
        for res in ("FAIL", "PASS", "FAIL"):
            CE.record("selftest", res, [repo / "src" / "a.py"], clone=repo, start=st)
    finally:
        CE.build_record = real
    got = CE.lookup(sha=sha, tool="selftest")
    check([r["result"] for r in got] == ["FAIL", "PASS", "FAIL"],
          "AD5 FAIL->PASS->FAIL in one second by one process stays three records: %r" % [r["result"] for r in got])
    check(CE.summarize(got).get("selftest") == "FAIL", "AD5 the last FAIL decides: %r" % CE.summarize(got))
    check(len({r.get("nonce") for r in got}) == 3 and all(isinstance(r.get("nonce"), str) and len(r["nonce"]) >= 32
                                                          for r in got), "AD5 each record carries its own nonce")
    day = store / ("%s.jsonl" % got[0]["ts"][:10])
    lines = day.read_text().splitlines()
    with open(day, "a") as f:
        f.write(lines[-2] + "\n")          # a replay of the PASS line: still deduped (review AC3)
    got = CE.lookup(sha=sha, tool="selftest")
    check([r["result"] for r in got] == ["FAIL", "PASS", "FAIL"], "AD5 a replayed line is still deduped by its mac")


# ---------------------------------------------------------------------------------------------------- AD6
def _ambiguous_repo(root):
    """A repo with two commits sharing a 4-hex prefix (deterministic: fixed content and dates)."""
    repo = Path(root) / "amb"
    repo.mkdir()
    git(repo, "init", "-q")
    stream = []
    for i in range(1, 801):
        msg = "c%d\n" % i
        stream.append("commit refs/heads/main\nmark :%d\ncommitter t <t@t> 1700000000 +0000\ndata %d\n%s%s\n"
                      % (i, len(msg), msg, "from :%d\n" % (i - 1) if i > 1 else ""))
    git(repo, "fast-import", "--quiet", inp="".join(stream))
    shas = git(repo, "rev-list", "main").split()
    seen = {}
    for s in shas:
        if s[:4] in seen:
            return repo, s[:4], seen[s[:4]], s
        seen[s[:4]] = s
    return repo, None, None, None


def ad6(root):
    import arbiter_tiers as AT
    repo, pre, s1, s2 = _ambiguous_repo(root)
    check(pre is not None, "AD6 fixture has an ambiguous 4-hex commit prefix: %r" % pre)
    if pre:
        check(AT._rev_one(pre, str(repo)) == AT.GIT_ERROR,
              "AD6 _rev_one: a prefix ambiguous inside one clone is GIT_ERROR, not 'absent': %r"
              % AT._rev_one(pre, str(repo)))
        check(AT._rev_one(s1[:12], str(repo)) == s1, "AD6 _rev_one: an unambiguous prefix resolves")
        check(AT._rev_one("1234567890ab", str(repo)) is None or AT._rev_one("1234567890ab", str(repo)) == AT.GIT_ERROR,
              "AD6 _rev_one: an unknown prefix is absent")
    full = "a" * 40
    rev = lambda answers: (lambda sha, repo: answers[repo])
    check(AT.resolve_sha_any(full[:10], repos=("x", "y"), rev=rev({"x": full, "y": AT.GIT_ERROR})) == AT.GIT_ERROR,
          "AD6 short sha found in one clone, ambiguous/erroring in another -> GIT_ERROR (UNMEASURED)")
    check(AT.resolve_sha_any(full[:10], repos=("x", "y"), rev=rev({"x": full, "y": None})) == full,
          "AD6 short sha found in one clone, absent in the other -> that commit")
    check(AT.resolve_sha_any(full, repos=("x", "y"), rev=rev({"x": full, "y": AT.GIT_ERROR})) == full,
          "AD6 a FULL sha cannot be ambiguous: one clone's error does not void it")


def main():
    if os.environ.get("AD_CWD_PROBE"):           # AD1's probe of the instrument clone: print the cwd and exit
        ok = os.path.realpath(os.getcwd()) == os.path.realpath(str(HERE.parents[2]))
        print("CWD", os.getcwd())
        return 0 if ok else 1
    base = SCRATCH if SCRATCH.is_dir() else None
    with tempfile.TemporaryDirectory(dir=base, prefix="selftest_ad_") as td:
        td = Path(td)
        store = td / "evidence"
        saved = {k: os.environ.get(k) for k in (CE.ENV_DIR, CE.KEY_ENV, "RIMFLOW_ITEM")}
        os.environ[CE.ENV_DIR] = str(store)
        os.environ[CE.KEY_ENV] = str(td / "close_evidence.key")     # never the user's real key
        os.environ.pop("RIMFLOW_ITEM", None)
        try:
            for name, fn, args in (("ad1", ad1, ()), ("ad2", ad2, (store,)), ("ad3", ad3, (store,)),
                                   ("ad4", ad4, ()), ("ad5", ad5, (store,)), ("ad6", ad6, ())):
                d = td / name
                d.mkdir()
                try:
                    fn(d, *args)
                except Exception as exc:  # noqa: BLE001 -- one group crashing is that group's FAIL
                    import traceback
                    traceback.print_exc()
                    check(False, "%s crashed: %s: %s" % (name, type(exc).__name__, exc))
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v
    print("%d failure(s)" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
