#!/usr/bin/env python3
"""selftest_relentless_stale_nocode.py - two Relentless traps that turned a finished item into paperwork loops.

(a) STALE_BUILD_SCOPE_DEPLOYED_MODS_ONLY. relentless_live.stale_build counted every src/<tier>/<X>/ path of the build,
    including folders the game never loads. GIZKA_STOWAWAY_UNMEASURED_ROWS_1 gen 6 (e87b8495b8, proof files only) took
    its game files from an earlier commit citing the item (dbec8644b2), which also touched
    src/RimMandrake/Utils/modcheck/required_checks.json; GOLD_PANNING (576c7659a1) edited that file later and the build
    went back as game_stale_build. Now only a folder with About/About.xml (fx.deployable) counts.
(b) RELENTLESS_NOCODE_REBUILD_IMPLEMENTED_REFUSED. Gen 8 re-anchored on today's main with an item note only
    (ad2549a17d) under the warrant "nothing in the work changed"; `rimflow implemented` refused the ledger-only sha and
    the item went back as proof_owed. Now relentless_game.no_code_rebuild passes `implemented --no-code "<warrant>"`,
    which cli accepts only when a commit under the sha naming the item did the work.

Review of 930b960a8e (an adversarial read of the diff): About.xml at HEAD dropped a whole deleted mod from the
deleted-file guard and dropped folders that ship inside other mods (a compose source, _Shared/ C# a .csproj compiles);
--no-code took any item-named ancestor (a design note, reverted work); the warrant was read by substring. Now
relentless_live.reaches_game (Fx.game_input), cli._carried_work and the structured `unchanged` warrant field.

Real paths: relentless_live.Fx and the real cli.py as a subprocess on a throwaway ledger, both over a SYNTHETIC git
repo built here (no historical sha of this repo is needed).

    python3 src/RimMandrake/rimflow/selftest_relentless_stale_nocode.py [--case NAME]

Cases (each prints `FIXTURE_VERDICT: PASS|FAIL`; exit 0 on PASS, 1 on FAIL):
    stale-harness-file     (a) fake: only a non-loading folder's file changed later -> not stale
    stale-mod-file         (a) fake control: a deployed mod's file changed later -> still STALE
    stale-no-deployable    (a) fake control: a fake without `deployable` keeps the old scope (every src/ folder)
    stale-real             (a) real Fx, synthetic repo: Utils harness edit not stale (GIZKA); a mod def, a folded
                               compose source, a _Shared/ file a .csproj compiles: STALE; a deleted whole mod (About.xml
                               too) refused; a harness-only built commit still takes the cited mod work (build_shas)
    nocode-words           (b) the structured warrant: take_warrant sets unchanged only for `UNCHANGED:`;
                               no_code_rebuild gives words only for that, on a ledger-only candidate of the warrant's gen
    implemented-nocode     (b) planted: the GIZKA shape, built work + another item's harness edit + item note -> built
    implemented-refuses    (b) controls: no --no-code; no build on record (a design note only); reverted work; later
                               work naming the item; empty words
    constants              relentless_game.LEDGER_ONLY is cli._LEDGER_ONLY
No --case: every case.
"""
import ast, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
REPO = os.environ.get("SELFTEST_REPO") or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rimflow import model                                       # noqa: E402
import relentless_live as L                                     # noqa: E402
import relentless_game as G                                     # noqa: E402

GIZKA = "GIZKA_STOWAWAY_UNMEASURED_ROWS_1"

FAILS = []
TMP = tempfile.mkdtemp(prefix="relentless_stale_nocode_")
LEDGER = os.path.join(TMP, "events.jsonl")
ITEMS = os.path.join(TMP, "items")
os.makedirs(os.path.join(ITEMS, "closed"))


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


# ---------------------------------------------------------------- (a)

class StaleFx(object):
    """The build b1 touches only a proof; c1 cites the item and touched a harness file and a mod def."""
    UTILS = "src/RimMandrake/Utils/modcheck/required_checks.json"
    DEF = "src/RimStarWars/GizkaStowaway/Defs/Gizka.xml"

    def __init__(self, later, deployable=True):
        self.later = later
        if deployable:
            self.deployable = lambda tier, mod: mod != "Utils"

    def touched(self, sha):
        return {"b1": ["infrastructure/state/live_proofs/X.txt", "src/RimStarWars/GizkaStowaway/a2_live_proof.py"],
                "c1": [self.UTILS, self.DEF]}[sha]

    def deleted(self, sha):
        return []

    def cited(self, item_id, sha):
        return ["c1"]

    def shippable(self, rel):
        return not rel.endswith(".py")

    def changed_since(self, sha, paths):
        return [(p, "576c7659a1") for p in self.later if p in paths]


def case_stale_harness_file():
    print("-- (a) planted: another item edits a harness file under src/RimMandrake/Utils/ after the build")
    why, files = L.stale_build(StaleFx([StaleFx.UTILS]), "b1", GIZKA)
    check(why is None, "not stale: %s" % why)
    check(files == [("GizkaStowaway", "Defs/Gizka.xml")], "the game files are the mod's alone: %s" % files)


def case_stale_mod_file():
    print("-- (a) control: another item edits the build's own mod def after the build")
    why, _ = L.stale_build(StaleFx([StaleFx.DEF, StaleFx.UTILS]), "b1", GIZKA)
    check(bool(why) and why.startswith(L.STALE) and StaleFx.DEF in why and StaleFx.UTILS not in why,
          "stale, naming the def only: %s" % why)


def case_stale_no_deployable():
    print("-- (a) control: a fake without deployable keeps every src/ folder")
    why, _ = L.stale_build(StaleFx([StaleFx.UTILS], deployable=False), "b1", GIZKA)
    check(bool(why) and why.startswith(L.STALE), "stale as before: %s" % why)


SYN = os.path.join(TMP, "repo")


def sgit(*a, cwd=None):
    r = subprocess.run(["git", *a], cwd=cwd or SYN, capture_output=True, text=True, timeout=60,
                       stdin=subprocess.DEVNULL)
    if r.returncode:
        raise AssertionError("git %s: %s" % (" ".join(a), r.stderr[-300:]))
    return r.stdout.strip()


def repo(name):
    """A fresh synthetic repo under TMP: src/RimMandrake/{ModA (a mod), Gone (a mod), Folded (a compose source, no
    About.xml), _Shared (compiled by ModA's csproj), Utils (harness)}."""
    global SYN
    SYN = os.path.join(TMP, name)
    os.makedirs(SYN)
    sgit("init", "-q", "-b", "main")
    sgit("config", "user.email", "t@t")
    sgit("config", "user.name", "t")
    commit("base", {
        "src/RimMandrake/ModA/About/About.xml": "<ModMetaData/>",
        "src/RimMandrake/ModA/Defs/A.xml": "<Defs/>",
        "src/RimMandrake/ModA/Source/ModA.csproj":
            '<Project><ItemGroup><Compile Include="..\\..\\_Shared\\Kit\\Kit.cs" /></ItemGroup></Project>',
        "src/RimMandrake/Gone/About/About.xml": "<ModMetaData/>",
        "src/RimMandrake/Gone/Defs/G.xml": "<Defs/>",
        "src/RimMandrake/Folded/Defs/F.xml": "<Defs/>",
        "src/RimMandrake/Biomes.compose.json": '{"entries": [{"key": "Folded", "source": "Folded"}]}',
        "src/RimMandrake/_Shared/Kit/Kit.cs": "class K {}",
        "src/RimMandrake/Utils/modcheck/required_checks.json": "{}",
        "infrastructure/state/items/X.md": "x"})
    return L.Fx(books=SYN)


def commit(subject, files):
    for path, text in files.items():
        full = os.path.join(SYN, path)
        if text is None:
            sgit("rm", "-q", "-r", "--", path)
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        sgit("add", "--", path)
    sgit("commit", "-q", "-m", subject)
    return sgit("rev-parse", "HEAD")


def case_stale_real():
    print("-- (a) real Fx over a synthetic repo")
    it = "PROBE_ITEM_ONE"
    for name, cited_files, later, want in (
            ("gizka", {"src/RimMandrake/Utils/modcheck/required_checks.json": '{"a": 1}',
                       "src/RimMandrake/ModA/Defs/A.xml": "<Defs><a/></Defs>"},
             {"src/RimMandrake/Utils/modcheck/required_checks.json": '{"moved": 1}'}, None),
            ("moddef", {"src/RimMandrake/ModA/Defs/A.xml": "<Defs><a/></Defs>"},
             {"src/RimMandrake/ModA/Defs/A.xml": "<Defs><b/></Defs>"}, "src/RimMandrake/ModA/Defs/A.xml"),
            ("folded", {"src/RimMandrake/Folded/Defs/F.xml": "<Defs><a/></Defs>"},
             {"src/RimMandrake/Folded/Defs/F.xml": "<Defs><b/></Defs>"}, "src/RimMandrake/Folded/Defs/F.xml"),
            ("shared", {"src/RimMandrake/_Shared/Kit/Kit.cs": "class K { int a; }"},
             {"src/RimMandrake/_Shared/Kit/Kit.cs": "class K { int b; }"}, "src/RimMandrake/_Shared/Kit/Kit.cs")):
        fx = repo("stale_" + name)
        commit("%s: the work" % it, cited_files)
        built = commit("%s: proof line" % it, {"infrastructure/state/live_proofs/%s.txt" % it: "live-proof A2: x"})
        commit("OTHER_ITEM: elsewhere", later)
        why, _ = L.stale_build(fx, built, it)
        if want is None:
            check(why is None, "%s: a harness-only later edit is not stale: %s" % (name, why))
        else:
            check(bool(why) and why.startswith(L.STALE) and want in why, "%s: stale, naming %s: %s" % (name, want, why))
    fx = repo("stale_gone")
    built = commit("%s: retire the Gone mod" % it, {"src/RimMandrake/Gone": None})
    why, _ = L.stale_build(fx, built, it)
    check(bool(why) and "deleted" in why and "Gone/Defs/G.xml" in why, "a deleted whole mod is refused: %s" % why)
    fx = repo("stale_fallback")
    commit("%s: the def" % it, {"src/RimMandrake/ModA/Defs/A.xml": "<Defs><a/></Defs>"})
    built = commit("%s: harness fix" % it, {"src/RimMandrake/Utils/modcheck/required_checks.json": '{"b": 1}'})
    commit("OTHER_ITEM: def", {"src/RimMandrake/ModA/Defs/A.xml": "<Defs><z/></Defs>"})
    why, _ = L.stale_build(fx, built, it)
    check(bool(why) and "ModA/Defs/A.xml" in why, "a harness-only built commit keeps the cited mod work: %s" % why)
    check(L.reaches_game(fx, "RimMandrake", "Utils", ()) is False and L.reaches_game(fx, "RimMandrake", "Folded", ())
          and L.reaches_game(fx, "RimMandrake", "_Shared", ()), "Utils is harness; Folded and _Shared reach the game")


# ---------------------------------------------------------------- (b)

def st(changed, gen=8, sha="ad2549a17d94c66b82f12cbd7787f2b9a7dcaf8c", unchanged=True):
    w = {"gen": gen, "changed": changed, "after": "game_stale_build"}
    if unchanged:
        w["unchanged"] = True
    return {"candidate": {"sha": sha, "gen": 8}, "warrant": w}


def case_nocode_words():
    print("-- (b) the structured warrant and no_code_rebuild")
    import relentless_breakers as B
    for text, want in (("WARRANT: UNCHANGED: required_checks.json moved under it | a red A2 means the probe", True),
                       ("WARRANT: nothing in the work changed except the cooldown fix | x then y", False),
                       ("WARRANT: no code changes; replaced the textures and Defs | x then y", False),
                       ("WARRANT: the env is UNCHANGED: odd | x then y", False)):
        w = B.take_warrant({"warrant_owed": {"after": "game_stale_build"}, "gen": 8}, text, 8, 0)
        check(bool(w) and (w.get("unchanged") is True) == want, "%r -> unchanged %s" % (text[:50], want))
    item_md = ["infrastructure/state/items/%s.md" % GIZKA]
    w = "UNCHANGED: gen6's built sha went stale on required_checks.json"
    got = G.no_code_rebuild(st(w), "ad2549a17d", item_md)
    check(bool(got) and "UNCHANGED" in got, "the GIZKA shape gets words: %r" % got)
    check(G.no_code_rebuild(st("nothing in the work changed except the cooldown fix", unchanged=False), "ad2549a17d",
                            item_md) is None, "prose without the field gets none")
    check(G.no_code_rebuild(st(w), "ad2549a17d", item_md + ["src/RimStarWars/GizkaStowaway/a2_live_proof.py"]) is None,
          "a candidate touching code gets none (it is its own work)")
    check(G.no_code_rebuild(st(w, gen=7), "ad2549a17d", item_md) is None, "an older generation's warrant gets none")
    check(G.no_code_rebuild(st(w), "0123456789", item_md) is None, "a sha that is not the candidate gets none")
    check(G.no_code_rebuild(st(w), "ad2549a17d", None) is None, "unreadable paths get none")
    check(G.no_code_rebuild({"candidate": {"sha": "ad2549a17d", "gen": 8}}, "ad2549a17d", item_md) is None,
          "no warrant gets none")


def cli(*args, seat="BENCH"):
    env = {k: v for k, v in os.environ.items()
           if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=LEDGER, RIMFLOW_ITEMS=ITEMS, RIMFLOW_SEAT=seat, AGENT_SEAT=seat, RIMFLOW_GIT_CWD=SYN)
    r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def ok(*args):
    rc, out = cli(*args)
    if rc:
        raise AssertionError("%s -> %d: %s" % (" ".join(args), rc, out[-400:]))
    return out


def world():
    model.EVENTS = LEDGER
    return model.replay(model.read())


CRIT = os.path.join(TMP, "crit.txt")


def new(iid):
    """File, claim and start `iid` on the throwaway ledger. GIZKA's id predates the SUBJECT_INTENT_TWIST name rule, so
    the item is filed under a good name and its events are renamed in place (ids only; the reader re-reads the file)."""
    if iid not in world().items:
        stand_in = "PROBE_STANDIN_FIX_OLD_NAME_RENAMED"
        ok("file", stand_in, "--for", "BENCH", "--title", "fixture %s" % iid)
        ok("claim", stand_in)
        ok("start", stand_in)
        shards = os.path.join(TMP, model.SHARD_DIR)
        for name in ([LEDGER] if os.path.exists(LEDGER) else []) + [os.path.join(shards, n) for n in os.listdir(shards)]:
            with open(name, encoding="utf-8") as f:
                text = f.read()
            with open(name, "w", encoding="utf-8") as f:
                f.write(text.replace('"%s"' % stand_in, '"%s"' % iid))
        check(iid in world().items and stand_in not in world().items, "the fixture item reads as %s" % iid)
    with open(CRIT, "w", encoding="utf-8") as f:
        f.write("A1 L0: the offline proof passes\nA2 L2: the live proof passes\n")
    return iid


def implemented(iid, sha, *extra):
    return cli("implemented", iid, "--sha", sha, "--criteria-file", CRIT, "--why", "selftest", *extra)


def published():
    sgit("update-ref", "refs/remotes/origin/main", "HEAD")


def case_implemented_nocode():
    print("-- (b) planted: the GIZKA shape over a synthetic repo, implemented --no-code -> built")
    repo("cli_gizka")
    new(GIZKA)
    work = commit("%s: A2 live judge" % GIZKA, {"src/RimStarWars/GizkaStowaway/a2_live_proof.py": "print(1)"})
    commit("OTHER_ITEM: move the registry", {"src/RimMandrake/Utils/modcheck/required_checks.json": '{"m": 1}'})
    note = commit("%s: rebuild on current main" % GIZKA, {"infrastructure/state/items/%s.md" % GIZKA: "n"})
    published()
    rc, out = implemented(GIZKA, work)
    check(rc == 0, "the work is implemented first: %s" % out[-300:])
    rc, out = implemented(GIZKA, note, "--no-code", "gen 8 rebuild; UNCHANGED: required_checks.json moved")
    check(rc == 0, "accepted: %s" % out[-300:])
    it = world().items[GIZKA]
    check(it.state == "built" and model.same_sha(it.built_sha or "", note),
          "built at the rebuild sha: %s %s" % (it.state, it.built_sha))
    ev = [e for e in model.read() if e.get("event") == "implemented" and e.get("id") == GIZKA]
    check(bool(ev) and work[:12] in (ev[-1].get("why") or "") and "no-code" in (ev[-1].get("why") or ""),
          "the event names the carried work: %r" % (ev[-1].get("why") if ev else None))


def case_implemented_refuses():
    print("-- (b) controls over a synthetic repo")
    repo("cli_refuse")
    a, b, c, d = (new(i) for i in ("PROBE_CARRY_A", "PROBE_CARRY_B", "PROBE_CARRY_C", "PROBE_CARRY_D"))
    commit("%s: design note" % a, {"design/%s.md" % a: "plan"})
    na = commit("%s: rebuild" % a, {"infrastructure/state/items/%s.md" % a: "n"})
    wb = commit("%s: work" % b, {"src/RimMandrake/ModA/Defs/B.xml": "<Defs><b/></Defs>"})
    commit("OTHER_ITEM: revert", {"src/RimMandrake/ModA/Defs/B.xml": "<Defs/>"})
    nb = commit("%s: rebuild" % b, {"infrastructure/state/items/%s.md" % b: "n"})
    wc = commit("%s: work" % c, {"src/RimMandrake/ModA/Defs/C.xml": "<Defs><c/></Defs>"})
    commit("%s: more work" % c, {"src/RimMandrake/ModA/Defs/C2.xml": "<Defs><c/></Defs>"})
    nc = commit("%s: rebuild" % c, {"infrastructure/state/items/%s.md" % c: "n"})
    wd = commit("%s: work" % d, {"src/RimMandrake/ModA/Defs/D.xml": "<Defs><d/></Defs>"})
    nd = commit("%s: rebuild" % d, {"infrastructure/state/items/%s.md" % d: "n"})
    published()
    for iid, w in ((b, wb), (c, wc), (d, wd)):
        rc, out = implemented(iid, w)
        if rc:
            raise AssertionError("fixture: implemented %s %s: %s" % (iid, w[:10], out[-300:]))
    words = "UNCHANGED: only the environment moved"
    rc, out = implemented(d, nd)
    check(rc != 0 and "touches nothing but the ledger" in out, "no --no-code: refused as before: %s" % out[-200:])
    rc, out = implemented(a, na, "--no-code", words)
    check(rc != 0 and "no build on record" in out and world().items[a].state != "built",
          "a design note only (no build on record): refused: %s" % out[-200:])
    rc, out = implemented(b, nb, "--no-code", words)
    check(rc != 0 and "differ" in out and "B.xml" in out, "reverted work: refused: %s" % out[-200:])
    check(model.same_sha(world().items[b].built_sha or "", wb), "and the build stays %s" % wb[:10])
    rc, out = implemented(c, nc, "--no-code", words)
    check(rc != 0 and "changed more than the ledger after its build" in out,
          "later work naming the item: refused: %s" % out[-200:])
    rc, out = implemented(d, nd, "--no-code", "  ")
    check(rc != 0 and "needs the words" in out, "empty words: refused: %s" % out[-200:])
    rc, out = implemented(d, nd, "--no-code", words)
    check(rc == 0, "and the clean shape still carries: %s" % out[-200:])


def case_constants():
    print("-- relentless_game.LEDGER_ONLY is cli._LEDGER_ONLY")
    tree = ast.parse(open(CLI, encoding="utf-8").read())
    val = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and any(getattr(t, "id", "") == "_LEDGER_ONLY" for t in n.targets))
    check(tuple(val) == tuple(G.LEDGER_ONLY), "%s == %s" % (val, G.LEDGER_ONLY))


CASES = {"stale-harness-file": case_stale_harness_file, "stale-mod-file": case_stale_mod_file,
         "stale-no-deployable": case_stale_no_deployable, "stale-real": case_stale_real, "nocode-words": case_nocode_words,
         "implemented-nocode": case_implemented_nocode, "implemented-refuses": case_implemented_refuses,
         "constants": case_constants}


def main(argv):
    names = [argv[argv.index("--case") + 1]] if "--case" in argv else list(CASES)
    try:
        for n in names:
            try:
                CASES[n]()
            except AssertionError as e:
                check(False, "%s: %s" % (n, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("FIXTURE_VERDICT: %s" % ("FAIL" if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
