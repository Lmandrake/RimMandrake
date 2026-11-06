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

Real path for (b): the real cli.py as a subprocess on a throwaway ledger, real published commits of this repo.

    python3 src/RimMandrake/rimflow/selftest_relentless_stale_nocode.py [--case NAME]

Cases (each prints `FIXTURE_VERDICT: PASS|FAIL`; exit 0 on PASS, 1 on FAIL):
    stale-harness-file     (a) planted: only a non-loading folder's file changed later -> not stale
    stale-mod-file         (a) control: a deployed mod's file changed later -> still STALE
    stale-no-deployable    (a) control: a fake without `deployable` keeps the old scope (every src/ folder)
    nocode-words           (b) no_code_rebuild says words only for a ledger-only candidate of the warrant's gen
    implemented-nocode     (b) planted: the GIZKA instance, implemented --no-code at ad2549a17d -> built
    implemented-refuses    (b) controls: no --no-code; --no-code with no work under the sha; empty words
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
NOTE_SHA = "ad2549a17d"       # gen 8: the item note only
WORK_SHA = "e87b8495b8"       # gen 6: a2_live_proof.py + its selftest + the proof line

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


# ---------------------------------------------------------------- (b)

def st(changed, gen=8, sha="ad2549a17d94c66b82f12cbd7787f2b9a7dcaf8c"):
    return {"candidate": {"sha": sha, "gen": 8}, "warrant": {"gen": gen, "changed": changed, "after": "game_stale_build"}}


def case_nocode_words():
    print("-- (b) no_code_rebuild")
    item_md = ["infrastructure/state/items/%s.md" % GIZKA]
    w = "nothing in the work changed; the environment did: gen6's built sha went stale"
    got = G.no_code_rebuild(st(w), "ad2549a17d", item_md)
    check(bool(got) and "nothing in the work changed" in got, "the GIZKA instance gets words: %r" % got)
    check(G.no_code_rebuild(st("fixed the probe's cooldown reset"), "ad2549a17d", item_md) is None,
          "a warrant naming a code change gets none")
    check(G.no_code_rebuild(st(w), "ad2549a17d", item_md + ["src/RimStarWars/GizkaStowaway/a2_live_proof.py"]) is None,
          "a candidate touching code gets none (it is its own work)")
    check(G.no_code_rebuild(st(w, gen=7), "ad2549a17d", item_md) is None, "an older generation's warrant gets none")
    check(G.no_code_rebuild(st(w), "0123456789", item_md) is None, "a sha that is not the candidate gets none")
    check(G.no_code_rebuild(st(w), "ad2549a17d", None) is None, "unreadable paths get none")
    check(G.no_code_rebuild({"candidate": {"sha": "ad2549a17d", "gen": 8}}, "ad2549a17d", item_md) is None,
          "no warrant gets none")


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60).stdout.strip()


def full(sha):
    return git("rev-parse", "--verify", "--quiet", sha + "^{commit}")


def need(*shas):
    missing = [s for s in shas if not full(s)]
    if missing:
        raise SystemExit("UNMEASURED: %s not in this clone (git fetch origin)" % ", ".join(missing))


def cli(*args, seat="BENCH"):
    env = {k: v for k, v in os.environ.items()
           if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=LEDGER, RIMFLOW_ITEMS=ITEMS, RIMFLOW_SEAT=seat, AGENT_SEAT=seat, RIMFLOW_GIT_CWD=REPO)
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


def case_implemented_nocode():
    print("-- (b) planted: implemented --no-code on GIZKA's ledger-only rebuild")
    need(NOTE_SHA, WORK_SHA)
    new(GIZKA)
    rc, out = implemented(GIZKA, full(NOTE_SHA), "--no-code", "gen 8 rebuild; nothing in the work changed")
    check(rc == 0, "accepted: %s" % out[-300:])
    it = world().items[GIZKA]
    check(it.state == "built" and model.same_sha(it.built_sha or "", full(NOTE_SHA)),
          "built at the rebuild sha: %s %s" % (it.state, it.built_sha))
    ev = [e for e in model.read() if e.get("event") == "implemented" and e.get("id") == GIZKA]
    check(bool(ev) and WORK_SHA in (ev[-1].get("why") or "") and "no-code" in (ev[-1].get("why") or ""),
          "the event names the carried work: %r" % (ev[-1].get("why") if ev else None))


def case_implemented_refuses():
    print("-- (b) controls: the guard still refuses a genuinely empty claim")
    need(NOTE_SHA)
    new(GIZKA)
    rc, out = implemented(GIZKA, full(NOTE_SHA))
    check(rc != 0 and "touches nothing but the ledger" in out, "no --no-code: refused as before: %s" % out[-200:])
    iid = new("NOBODY_COMMITTED_THIS_PROBE_FIXTURE")
    rc, out = implemented(iid, full(NOTE_SHA), "--no-code", "nothing in the work changed")
    check(rc != 0 and "cannot stand for one" in out, "no work under the sha: refused: %s" % out[-200:])
    check(world().items[iid].state != "built", "and nothing was built")
    rc, out = implemented(GIZKA, full(NOTE_SHA), "--no-code", "  ")
    check(rc != 0 and "needs the words" in out, "empty words: refused: %s" % out[-200:])


def case_constants():
    print("-- relentless_game.LEDGER_ONLY is cli._LEDGER_ONLY")
    tree = ast.parse(open(CLI, encoding="utf-8").read())
    val = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and any(getattr(t, "id", "") == "_LEDGER_ONLY" for t in n.targets))
    check(tuple(val) == tuple(G.LEDGER_ONLY), "%s == %s" % (val, G.LEDGER_ONLY))


CASES = {"stale-harness-file": case_stale_harness_file, "stale-mod-file": case_stale_mod_file,
         "stale-no-deployable": case_stale_no_deployable, "nocode-words": case_nocode_words,
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
