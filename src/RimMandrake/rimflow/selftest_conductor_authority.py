#!/usr/bin/env python3
"""CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM stays made "everywhere": every rule file a seat or helper reads names the
ruling, and each tool gate that took only his typed words takes the ruling with the Conductor's text in --why, while a
bare agent reason and any other ruling are still refused."""
import ast
import contextlib
import inspect
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UTILS = ROOT / "src/RimMandrake/Utils"
sys.path.insert(0, str(UTILS))
import conductor_authority as CA  # noqa: E402
import repair_torn_ledger as RTL  # noqa: E402

fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


FILES = ["CLAUDE.md", "design/RimMandrake/standing_rulings.md", "design/RimMandrake/delegation_policy.md",
         "infrastructure/agents/CHARTER.md", "infrastructure/agents/CONDUCTOR.md"]  # FOUNDRY.md: seat retired; BENCH.md folded into CONDUCTOR.md

# A judge brief whose reader only returns a verdict and is calibrated at the brief's hash: no instruction reaches its reader,
# and an edit here would stale its calibration (set_down_judge.py, refusal_contract.status).
VERDICT_ONLY_BRIEFS = {"src/RimMandrake/rimflow/roles/set_down_judge.md"}
FILES += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "src/RimMandrake/rimflow/roles").glob("*.md")
                if str(p.relative_to(ROOT)) not in VERDICT_ONLY_BRIEFS)
FILES += sorted(str(p.relative_to(ROOT)) for p in (ROOT / ".claude/agents").glob("rm-*.md"))
check(len(FILES) >= 19, "the census sees the role and agent files (%d)" % len(FILES))
for f in FILES:
    check(CA.RULING in (ROOT / f).read_text(encoding="utf-8"), f + " names the ruling")

check(CA.carried(CA.RULING, "do it"), "the ruling with the Conductor's text is carried")
check(not CA.carried(CA.RULING, "  "), "the ruling without the Conductor's text is not")
check(not CA.carried("SOME_OTHER_RULING", "do it"), "another ruling is not")
check(not CA.carried(None, "do it"), "a bare agent reason is not")



# The parsers, on a nonexistent sha: a refused-by-authority line must not appear when the route is taken.
for verb in ("unpurge", "unban"):
    h = subprocess.run([sys.executable, str(UTILS / "art/art.py"), verb, "-h"], capture_output=True, text=True)
    check("--per-ruling" in h.stdout and "--why" in h.stdout, "art.py %s takes --per-ruling and --why" % verb)
h = subprocess.run([sys.executable, str(UTILS / "slot_allocator.py"), "set", "--n", "3", "--why", "my reason"],
                   capture_output=True, text=True, env=dict(os.environ))
check(h.returncode == 2 and CA.RULING in h.stderr, "slot_allocator set refuses a bare reason and names the route")
with tempfile.TemporaryDirectory() as tmp:
    h = subprocess.run([sys.executable, str(UTILS / "slot_allocator.py"), "set", "--n", "3", "--hours", "1", "--per-ruling",
                        CA.RULING, "--why", "run three"], capture_output=True, text=True,
                       env=dict(os.environ, RM_STREAMS_DIR=tmp))
    ov = Path(tmp) / "slot_override.json"
    check(h.returncode == 0 and ov.exists() and CA.RULING in ov.read_text(encoding="utf-8"),
          "slot_allocator set takes the Conductor's instruction and says so on the override")

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "shard.jsonl"
    p.write_text('{"a": 1}\n{torn\n', encoding="utf-8")
    bak = Path(tmp) / "bak"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = RTL.repair(p, apply=True, owner_said=None, backup_dir=bak, why="my reason")
    check(rc == 1, "repair_torn_ledger --apply refuses a bare reason")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = RTL.repair(p, apply=True, owner_said=None, backup_dir=bak, per_ruling=CA.RULING, why="repair it")
    check(rc == 0 and CA.RULING in out.getvalue(), "repair_torn_ledger --apply takes the Conductor's instruction")


# The census: no hand list of gates, so a new gate cannot be missed. Every tracked Python tool is parsed; a parser that
# takes his words (--owner-said, --said, a HIS_WORDS metavar) must offer --per-ruling beside it, and a refusal that
# demands his words must name the route. EXEMPT is the only way out, each with the reason it is not a gate.
EXEMPT = {
    "src/RimMandrake/Utils/look_notes.py": "`pin --said` records his pass at his walk, one of his five acts "
                                           "(CLAUDE.md §Only five acts stay his); the Conductor cannot give that pass",
    "src/RimMandrake/rimflow/red_dispatch.py": "builder_start only excludes OWNER start events from a builder count; it grants nothing",
    "src/RimMandrake/Utils/art/facing_scale_lint.py": "--owner-said is optional; without it the install runs under a "
                                                      "script reason, nothing is refused",
    "src/RimMandrake/Utils/art/sheet_to_artifact.py": "the demand is about a question's wording, not an authority",
    "src/RimMandrake/Utils/modcheck/l1_donor_off_round.py": "--owner-present states he is physically there for a flyer "
                                                            "test (never without him); a fact, not an authority",
    # hold and allow-design take his words alone; lift takes his words or the Conductor's own route,
    # --per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_LIFT_HOLD_NOT_HIM_ALONE (owner, by card 2026-11-19)
    "src/RimMandrake/rimflow/mod_owner_hold.py": "OWNER ONLY for hold and allow-design (owner 2026-11-16, \"And stop "
                                                 "the new biome mods work. Only Pyrelands as a biome mod right now.\"); "
                                                 "lift also takes the Conductor's lift by its own ruling (owner "
                                                 "2026-11-19, \"Conductor should also be able to lift a Hold.\")",
    # optional provenance beside a required --why: nothing is refused for want of his words
    "src/RimMandrake/rimflow/maturation_dispatch.py": "void/unvoid: --why is required, --owner-said is optional "
                                                      "provenance; nothing is refused without it",
    "src/RimMandrake/rimflow/pipeline_control.py": "pipe: --why is required, --owner-said is optional provenance "
                                                   "(act records it); the grant gate's route is control.py's",
    "src/RimMandrake/rimflow/run_void.py": "void/unvoid record --owner-said when given; --why is what they require",
}
DEMAND = re.compile(r"(needs?|requires?|must|only)\b.{0,40}(his (typed |exact |verbatim )?words|--owner-said|--said\b)", re.I)
ROUTE = re.compile(r"per.ruling|Conductor|ROUTE|standing ruling|--why")


def _flags(call):
    return [a.value for a in call.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]


def _kw(call, name):
    for k in call.keywords:
        if k.arg == name and isinstance(k.value, ast.Constant):
            return k.value.value
    return None


def parser_gaps(src):
    """Parsers in `src` taking his words with no --per-ruling. A name rebound to a new parser is a new parser."""
    tree = ast.parse(src)
    gen, groups = {}, {}
    nodes = sorted((n for n in ast.walk(tree) if hasattr(n, "lineno")), key=lambda n: (n.lineno, n.col_offset))
    for n in nodes:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            gen[n.targets[0].id] = gen.get(n.targets[0].id, 0) + 1
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "add_argument" \
                and isinstance(n.func.value, ast.Name):
            v = n.func.value.id
            g = groups.setdefault((v, gen.get(v, 0)), {"line": n.lineno, "takes": False, "route": False})
            fl = _flags(n)
            g["takes"] |= any(f in ("--owner-said", "--said") for f in fl) or _kw(n, "metavar") == "HIS_WORDS"
            g["route"] |= "--per-ruling" in fl
    return ["line %d (%s)" % (g["line"], k[0]) for k, g in groups.items() if g["takes"] and not g["route"]]


def refusal_gaps(src):
    """Statements that demand his words without naming any other route."""
    tree = ast.parse(src)
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, (ast.Raise, ast.Return, ast.Expr)) or (isinstance(n, ast.Expr) and not isinstance(n.value, ast.Call)):
            continue
        seg = ast.get_source_segment(src, n) or ""
        if DEMAND.search(" ".join(seg.split())) and not ROUTE.search(seg):
            out.append("line %d" % n.lineno)
    return out


check(parser_gaps('p = s.add_parser("a")\np.add_argument("--owner-said")\np = s.add_parser("b")\np.add_argument("--per-ruling")\n')
      == ["line 2 (p)"], "the census catches a parser with his words and no route")
check(not parser_gaps('p.add_argument("--owner-said")\np.add_argument("--per-ruling")\n'), "the census passes a parser with the route")
check(parser_gaps('p.add_argument("--x", metavar="HIS_WORDS")\n') == ["line 1 (p)"], "the census sees a HIS_WORDS metavar")
check(refusal_gaps('raise Refused("this needs his words")\n') == ["line 1"], "the census catches a bare refusal")
check(not refusal_gaps('raise Refused("this needs his words or " + CA.ROUTE)\n'), "the census passes a refusal with the route")

tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.py"], capture_output=True, text=True).stdout.split()
seen = gaps = 0
takers = set()
for rel in tracked:
    if "selftest" in rel or "/test_" in rel or not (ROOT / rel).exists():
        continue
    try:
        src = (ROOT / rel).read_text(encoding="utf-8")
        ast.parse(src)
    except (SyntaxError, UnicodeDecodeError, ValueError):
        continue
    seen += 1
    if "--owner-said" in src:
        takers.add(rel)
    bad = parser_gaps(src) + refusal_gaps(src)
    if bad and rel not in EXEMPT:
        gaps += 1
        check(False, "%s: his words with no route: %s" % (rel, ", ".join(bad)))
check(seen > 200 and len(takers) > 10, "the census read the tree (%d files, %d naming --owner-said)" % (seen, len(takers)))
check(gaps == 0, "every his-words gate offers the Conductor's route")
for rel, why in EXEMPT.items():
    check((ROOT / rel).exists(), "exempt file exists: %s (%s)" % (rel, why))

# Each gate named in the blind check, run: the route passes, a bare reason and another ruling do not.
sys.path.insert(0, str(UTILS / "art"))
sys.path.insert(0, str(UTILS / "art_eval"))
sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))


def run(*cmd, **kw):
    return subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True, **kw)


RIGHT = ["--per-ruling", CA.RULING, "--why", "the Conductor said so"]
WRONG = ["--per-ruling", "SOME_OTHER_RULING", "--why", "the Conductor said so"]
BARE = ["--why", "my own reason"]

with tempfile.TemporaryDirectory() as tmp:
    sheet, dec = Path(tmp) / "s.html", Path(tmp) / "d.json"
    sheet.write_text('<script id="ITEMS" type="application/json">[{"id": "r1"}]</script>', encoding="utf-8")
    dec.write_text("{}", encoding="utf-8")
    base = [UTILS / "apply_blanket_ruling.py", "--decisions", dec, "--sheet", sheet, "--decision", "keep", "--apply"]
    check(run(*base, *BARE).returncode != 0 and run(*base, *WRONG).returncode != 0, "apply_blanket_ruling refuses a bare reason and another ruling")
    check(run(*base, *RIGHT).returncode == 0 and CA.RULING in dec.read_text(encoding="utf-8"), "apply_blanket_ruling takes the Conductor's instruction, tagged")

    d = Path(tmp) / "dv.json"
    d.write_text(json.dumps({"savedBy": "x", "writeCount": 1, "decisions": {}}), encoding="utf-8")
    dv2 = UTILS / "art/decisions_v2.py"
    check(run(dv2, d, "--returned", *BARE, "--apply").returncode != 0, "decisions_v2 --returned refuses a bare reason")
    check(run(dv2, d, "--accept-looks", *WRONG, "--apply").returncode != 0, "decisions_v2 --accept-looks refuses another ruling")
    check(run(dv2, d, "--returned", *RIGHT, "--apply").returncode == 0 and CA.RULING in d.read_text(encoding="utf-8"), "decisions_v2 --returned takes the Conductor's instruction")
    h = run(dv2, "-h").stdout
    check("--per-ruling" in h, "decisions_v2 offers the route to --accept-looks too")

import ledger as AEL  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "cl.jsonl"
    try:
        AEL.add("s", "t", "owner_override", "m", "d", CA.words(None, None, "my own reason"), path=p)
        check(False, "art_eval ledger refuses a bare reason")
    except SystemExit:
        check(True, "art_eval ledger refuses a bare reason")
    AEL.add("s", "t", "owner_override", "m", "d", CA.words(None, CA.RULING, "do it"), path=p)
    check(CA.RULING in p.read_text(encoding="utf-8"), "art_eval ledger takes the Conductor's instruction")

import fauna_drive as FD  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    FD.RS.OWNER_PROMPTS = Path(tmp) / "op.jsonl"
    with contextlib.redirect_stdout(io.StringIO()):
        args = dict(defname="D", text="t", source="chat", owner_said=None, by_card=None)
        rc1 = FD.cmd_owner_prompt(types.SimpleNamespace(per_ruling=None, why="mine", **args))
        rc2 = FD.cmd_owner_prompt(types.SimpleNamespace(per_ruling=CA.RULING, why="do it", **args))
    check(rc1 == 2 and rc2 == 0 and CA.RULING in FD.RS.OWNER_PROMPTS.read_text(encoding="utf-8"), "fauna_drive owner-prompt: bare reason refused, the route taken")

import artledger as AL  # noqa: E402
src = (UTILS / "art/artledger.py").read_text(encoding="utf-8")
sig = inspect.signature(AL.retire).parameters
check("per_ruling" in sig and "why" in sig, "artledger.retire takes the route")

mc = UTILS / "modcheck/cli.py"
r = run(mc, "review", "NoSuchMod", *BARE)
check(r.returncode != 0 and CA.RULING in r.stderr, "modcheck review refuses a bare reason and names the route")
check("--per-ruling" in run(mc, "validate", "-h").stdout, "modcheck validate offers the route")

check("CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM" in (ROOT / "src/RimMandrake/rimflow/model.py").read_text(encoding="utf-8"),
      "the seat refusal names the Conductor's route")

# An item under his name never refuses the Conductor (owner, 2026-11-03); another seat's item still refuses it.
sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
import model as M  # noqa: E402
_it = lambda owner: types.SimpleNamespace(id="I0", owner=owner, state="doing")  # noqa: E731
for verb in ("verify", "claim", "start"):
    ev = {"event": verb, "seat": "BENCH", "id": "I0"}
    check(M._who_refusal(ev, _it("OWNER")) is None, "BENCH may `%s` an item owned by OWNER" % verb)
    check(M._who_refusal(ev, _it("DESIGNER")) is not None, "BENCH still may not `%s` another seat's item" % verb)
# A retired seat's open item belongs to its heir (owner by card 2026-11-02, FOUNDRY -> BENCH): the Workshop lane hands
# such items to BENCH helpers, and the refusal stopped GOODBYE_CANCEL_FIX_PEER_ATE_THE_NIGHT at its first claim.
for verb in ("lease", "claim", "start", "verify"):     # `close` is any seat's already
    ev = {"event": verb, "seat": "BENCH", "id": "I0"}
    check(M._who_refusal(ev, _it("FOUNDRY")) is None, "BENCH may `%s` an item of the retired seat FOUNDRY" % verb)
    check(M._who_refusal(dict(ev, seat="DESIGNER"), _it("FOUNDRY")) is not None,
          "DESIGNER still may not `%s` a FOUNDRY item (only the heir inherits)" % verb)

# The function-level census. The parser census above sees only argparse flags; the two gates that escaped (a refusal of
# BENCH on an item owned by OWNER; the lease guard reading argv for --owner-said) sat in plain functions. So: every
# function, in every tracked tool, that CONDITIONS on his words (owner_said / ownerSaid / "--owner-said" in an argv
# test) must also mention the Conductor's route (per_ruling, perRuling, --per-ruling, conductor_authority, CA.) in the
# same function; every file that COMPARES a seat or an item owner to "OWNER" must mention it somewhere in the file.
# OWNER_ONLY is the only way out: file -> the ruling that keeps it his, and why.
ROUTE_WORDS = re.compile(r"per.?ruling|conductor_authority|CONDUCTOR_AUTHORITY|\bCA\.|\bcarried\(")
SAID_NAMES = ("owner_said", "ownerSaid")
OWNER_ONLY = {
    "src/RimMandrake/rimflow/cli.py": "bridge give / the OWNER bridge hold 45-min rule (owner by card 2026-10-30), `played` "
                                      "rung (PROJECT_MATURITY_DASHBOARD_1); any ruling already resolves seat OWNER at _resolve",
    "src/RimMandrake/rimflow/driver_lock.py": "OWNER bridge hold 45-min rule (owner by card 2026-10-30)",
    "src/RimMandrake/rimflow/wrapup.py": "never auto-releases his OWNER bridge hold (owner by card 2026-10-30); grants nothing",
    "src/RimMandrake/rimflow/host_guard.py": "OWNER bridge hold 45-min rule (owner by card 2026-10-30)",
    "src/RimMandrake/rimflow/game_lock.py": "reads his OWNER bridge hold as exit 3 and leaves its 45-min rule to "
                                            "host_guard (owner by card 2026-10-30); the Conductor's cut is cli.py's",
    "src/RimMandrake/Utils/fake_two_games.py": "a test fixture that plants an OWNER lock, authorizes nothing",
    "src/RimMandrake/rimflow/owner_interaction.py": "measures HIS activity clock, authorizes nothing",
    "src/RimMandrake/rimflow/incident.py": "routes a needs=owner alarm to the OWNER seat, authorizes nothing",
    "src/RimMandrake/Utils/broadcast.py": "OWNER ONLY broadcast skill: announce to every window is his",
    "src/RimMandrake/Utils/mod_completion.py": "reads ledger history for evidence, authorizes nothing",
    "src/RimMandrake/Utils/look_changed_labels.py": "reads stage records to date his last look (his moves out of his_walk), authorizes nothing",
    "src/RimMandrake/Utils/owner_queue.py": "reads his notes, authorizes nothing",
    "src/RimMandrake/Utils/ops_core/ops_ledger.py": "display of whose event it was, authorizes nothing",
    "src/RimMandrake/Utils/artpipe/fill_queue.py": "verifies a recorded card ruling of his (evidence), authorizes nothing new",
    "src/RimMandrake/Utils/rimflow_metrics.py": "counts provenance, authorizes nothing",
    "src/RimMandrake/rimflow/conductor_closeout.py": "reads his words from the ledger, authorizes nothing",
    "src/RimMandrake/rimflow/wrapup.py": "never releases his OWNER bridge hold at an agent's end (owner by card "
                                         "2026-10-30); authorizes nothing",
    "src/RimMandrake/Utils/art/backfill.py": "reads a decisions doc's provenance, authorizes nothing",
    "src/RimMandrake/rimflow/delegated_digest.py": "lists the open items he owns, with age and waiters, for his daily "
                                                   "digest (OWNER_ASKS_MEASURE_AGE_IN_DIGEST); authorizes nothing",
    "src/RimMandrake/rimflow/modledger_backfill.py": "counts OWNER-seat bulk `implemented` stamps in the ledger shards "
                                                     "(evidence for a backfill), authorizes nothing",
    "src/RimMandrake/Utils/modcheck/northstar.py": "record_validation only persists the words its caller (modcheck/cli, "
                                                   "via CA.words) already gated",
    "src/RimMandrake/bridgetools/build.py": "reads the game's driver lock holder (his OWNER hold) to refuse a deploy; "
                                            "authorizes nothing",
    "src/RimMandrake/rimflow/item_packet.py": "picks which notes a launch packet keeps whole (his words are never "
                                              "dropped); authorizes nothing",
    "src/RimMandrake/rimflow/wake_words.py": "reads OWNER-shard events that carry his words from the ledger; "
                                             "authorizes nothing",
    "design/RimStarWars/canon_references/gpt_review/check_review_complete.py": "compares a review row's disposition "
                                                                              "'OWNER' (a work verdict), not a seat",
}


def _is_owner_str(n):
    return isinstance(n, ast.Constant) and n.value == "OWNER"


def function_gaps(src):
    """-> (said_gaps, owner_lines): said_gaps are function names that test his words with no route in their text;
    owner_lines are line numbers of OWNER comparisons (a file-level finding, resolved by the caller)."""
    tree = ast.parse(src)
    said, owner = [], []
    for f in ast.walk(tree):
        if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        seg = ast.get_source_segment(src, f) or ""
        tests = []
        for n in ast.walk(f):
            if isinstance(n, (ast.If, ast.IfExp, ast.Assert, ast.While)):
                tests.append(n.test)
            elif isinstance(n, ast.BoolOp):
                tests.extend(n.values)
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
                tests.append(n.operand)
        hit = False
        for t in tests:
            for x in ast.walk(t):
                if isinstance(x, ast.Name) and x.id in SAID_NAMES:
                    hit = True
                if isinstance(x, ast.Attribute) and x.attr in SAID_NAMES:
                    hit = True
                if isinstance(x, ast.Constant) and isinstance(x.value, str) and x.value.startswith("--owner-said"):
                    hit = True
        if hit and not ROUTE_WORDS.search(seg):
            said.append(f.name)
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare) and (_is_owner_str(n.left) or any(_is_owner_str(c) for c in n.comparators)):
            owner.append(n.lineno)
    return said, owner


check(function_gaps('def g(owner_said):\n    if not owner_said:\n        return 1\n')[0] == ["g"],
      "the function census catches a gate on his words with no route")
check(not function_gaps('def g(owner_said, per_ruling):\n    if not owner_said:\n        return 1\n')[0],
      "the function census passes a gate that names the route")
check(function_gaps('def g(seat):\n    return seat == "OWNER"\n')[1] == [2], "the function census sees an OWNER comparison")
check(function_gaps('def g(argv):\n    if any(a == "--owner-said" for a in argv):\n        return 1\n')[0] == ["g"],
      "the function census sees an argv test for --owner-said")

fn_gaps = 0
owner_files = set()
for rel in tracked:
    if "selftest" in rel or "/test_" in rel or not (ROOT / rel).exists():
        continue
    try:
        src = (ROOT / rel).read_text(encoding="utf-8")
        said, owner = function_gaps(src)
    except (SyntaxError, UnicodeDecodeError, ValueError):
        continue
    if said and rel not in OWNER_ONLY and rel not in EXEMPT:
        fn_gaps += 1
        check(False, "%s: function(s) gate on his words with no Conductor route: %s" % (rel, ", ".join(said)))
    if owner:
        owner_files.add(rel)
        if rel not in OWNER_ONLY and not ROUTE_WORDS.search(src) and rel not in EXEMPT:
            fn_gaps += 1
            check(False, "%s: compares to \"OWNER\" (lines %s) in a file with no Conductor route and no OWNER_ONLY entry"
                  % (rel, ",".join(map(str, owner))))
check(len(owner_files) > 10, "the function census saw OWNER comparisons (%d files)" % len(owner_files))
check(fn_gaps == 0, "every function gate on his words or OWNER carries the Conductor route or is OWNER_ONLY with a ruling")
for rel, why in OWNER_ONLY.items():
    check((ROOT / rel).exists() and len(why) > 20, "owner-only file exists with its reason: %s" % rel)
print("%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
