#!/usr/bin/env python3
"""Selftest for modledger.py — the per-mod ledger of the holder-pipeline fusion.

    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_modledger

Item RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE; spec design/specs/2026-11-15-holder-pipeline-fusion.md
§3.1-3.3. Every case runs against a throwaway repo root in a temp dir (never this repo's concept folders). The lint
must REFUSE: a hand-edited view, a shard that is not a strict extension of its published form, a HOLDER event with a
stale lease token, a holder writing into a JUDGE or OWNER shard, a finding with no proposed fix, a sealed judge shard
that grew. It must pass the clean shapes: empty ledger, single shard, many shards, a duplicate (idempotent) append, a
superseded event. The packet must stay inside its budget by dropping old closed material first, never an open finding,
a refuted cause or his answer, and must say what it left out.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402

CLI = os.path.join(HERE, "modledger.py")
FAIL = []
MOD = "TestMod"
T0 = "2026-11-15T20:00:00Z"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def refuses(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except M.ModLedgerError as e:
        return str(e)
    return None


def codes(findings):
    return sorted({f[0] for f in findings})


def fresh():
    root = tempfile.mkdtemp(prefix="modledger_self_")
    os.makedirs(os.path.join(root, "design", "concepts", MOD))
    return root


def ts(minute, sec=0):
    return "2026-11-15T20:%02d:%02dZ" % (minute, sec)


def git(root, *a):
    return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, check=True)


def git_repo(root):
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")


def commit_all(root, msg):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


roots = []

# ---- config: one place for the numbers ----------------------------------------------------------------------------
cfg = M.config()
check("config names the 400k holder ceiling (his 'Try 400k first.')", cfg.get("holder_context_ceiling_tokens") == 400000,
      cfg.get("holder_context_ceiling_tokens"))
check("config names the 15k packet budget", cfg.get("packet_budget_tokens") == 15000, cfg.get("packet_budget_tokens"))

# ---- empty ledger --------------------------------------------------------------------------------------------------
r = fresh(); roots.append(r)
check("empty ledger reads no events", M.read(r, MOD) == [])
st = M.reduce([])
check("empty ledger reduces to no stage, no findings", st["stage"] is None and st["findings"] == {})
txt, info = M.packet(r, MOD)
check("empty ledger packet prints and says it holds nothing", "no events" in txt and info["tokens"] > 0, txt[:200])
check("empty ledger lints clean (no views owed for no shards)", M.lint(r, MOD, base=None)[0] == [], M.lint(r, MOD, None))

# ---- single shard, idempotent append --------------------------------------------------------------------------------
eid, created = M.append(r, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0",
                        ts=ts(0))
check("first append creates", created)
eid2, created2 = M.append(r, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0",
                          ts=ts(1))
check("duplicate append (same content, same writer) is idempotent", eid2 == eid and not created2, (eid, eid2))
check("single shard holds one line", len(M.read(r, MOD)) == 1, M.read(r, MOD))
M.append(r, MOD, "DISPATCH", "stage.accepted", "stage", body={"to": 2, "from": 1}, ts=ts(2))
check("version is inherited from the ledger when not named", M.read(r, MOD)[-1]["version"] == "0.1.0")
check("single shard lints clean after append (views regenerated)", M.lint(r, MOD, base=None)[0] == [],
      M.lint(r, MOD, None)[0])
st = M.reduce(M.read(r, MOD))
check("stage read from the accepted move", st["stage"] == 2 and st["version"] == "0.1.0", (st["stage"], st["version"]))

# a union-merge duplicate line (byte-identical) collapses on read and lints clean
shard = M.shard_path(r, MOD, "DISPATCH")
with open(shard, encoding="utf-8") as fh:
    first = fh.readline()
with open(shard, "a", encoding="utf-8") as fh:
    fh.write(first)
check("a byte-identical union duplicate collapses on read", len(M.read(r, MOD)) == 2, len(M.read(r, MOD)))

# ---- many shards: leases, holder, judge, owner ----------------------------------------------------------------------
tok1 = M.grant(r, MOD, lease="L1", ts=ts(3))
check("first lease token is 1", tok1 == 1, tok1)
M.append(r, MOD, "HOLDER.L1", "cause.tried", "C_TICK", body={"text": "the comp ticks only TickLong"}, token=1,
         ts=ts(4), now=ts(4))
M.append(r, MOD, "HOLDER.L1", "cause.refuted", "C_TICK", body={"text": "ticks fine; refuted by the tick probe",
                                                                "depends_on": ["Source/Comp.cs"]},
         code_sha="abc123", token=1, ts=ts(5), now=ts(5))
fid, _ = M.append(r, MOD, "JUDGE.J1", "finding.open", "F_BLAST",
                  body={"text": "blast radius ignores walls",
                        "proposed_fix": "in Blast.cs, stop the ray at the first impassable cell (GenSight.LineOfSight)"},
                  run="J1", ts=ts(6))
M.append(r, MOD, "OWNER", "question.answer", "Q_RADIUS", body={"text": "Keep the radius at 4."},
         authority={"owner_said": "Keep the radius at 4."}, ts=ts(7))
M.append(r, MOD, "HOLDER.L1", "question.ask", "Q_KNOCK", body={"text": "Should knockback stun?",
                                                                "obvious": "no", "against": "the bar mentions a stun"},
         token=1, ts=ts(8), now=ts(8))
M.append(r, MOD, "HOLDER.L1", "session.id", "session", body={"session_id": "s-1", "context_tokens": 410000},
         token=1, ts=ts(9), now=ts(9))
evs = M.read(r, MOD)
shards = sorted({e["_shard"] for e in evs})
check("many shards: DISPATCH, HOLDER.L1, JUDGE.J1, OWNER", shards == ["DISPATCH", "HOLDER.L1", "JUDGE.J1", "OWNER"],
      shards)
check("merged read is in time order across shards", [e["ts"] for e in evs] == sorted(e["ts"] for e in evs))
check("seq is the line number in its own shard", all(e["_seq"] >= 1 for e in evs) and
      [e["_seq"] for e in evs if e["_shard"] == "HOLDER.L1"] == [1, 2, 3, 4])
st = M.reduce(evs)
check("open finding carries the finder's proposed fix", st["findings"]["F_BLAST"]["status"] == "open" and
      "LineOfSight" in st["findings"]["F_BLAST"]["proposed_fix"], st["findings"].get("F_BLAST"))
check("refuted cause is kept with what it was refuted on", st["causes"]["C_TICK"]["status"] == "refuted" and
      st["causes"]["C_TICK"]["code_sha"] == "abc123", st["causes"].get("C_TICK"))
check("rotation is due once the session passes the configured ceiling", st["session"]["rotate_due"] is True,
      st["session"])
check("many-shard ledger lints clean", M.lint(r, MOD, base=None)[0] == [], M.lint(r, MOD, None)[0])

# ---- refusals at append ---------------------------------------------------------------------------------------------
why = refuses(M.append, r, MOD, "JUDGE.J1", "finding.open", "F_NOFIX", body={"text": "something is off"}, run="J1",
              ts=ts(10))
check("finding with no proposed fix is refused at append", why and "proposed_fix" in why, why)
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "n", body={"text": "x"}, token=7, ts=ts(10), now=ts(10))
check("holder append with a token it was never granted is refused", why and "token" in why, why)
why = refuses(M.append, r, MOD, "HOLDER.L1", "finding.verified", "F_BLAST", body={"text": "fixed"}, token=1,
              ts=ts(10), now=ts(10))
check("a holder may not verify a finding (only a judge turns one green)", why and "may not" in why, why)
why = refuses(M.append, r, MOD, "JUDGE.J1", "note", "n", body={"text": "planted"}, run="J1", ts=ts(10),
              env_writer="HOLDER.L1")
check("a holder process (env writer) may not append to a JUDGE shard", why and "HOLDER.L1" in why, why)
why = refuses(M.append, r, MOD, "OWNER", "question.answer", "Q_X", body={"text": "yes"}, ts=ts(10),
              env_writer="HOLDER.L1")
check("a holder process may not append to the OWNER shard", why is not None, why)
why = refuses(M.append, r, MOD, "OWNER", "question.answer", "Q_X", body={"text": "yes"}, ts=ts(10))
check("an OWNER event without his words, card or ruling is refused", why and "authority" in why, why)
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "n", body={"text": "late"}, token=1, ts=ts(59), now=ts(59))
check("a lapsed lease (idle past the configured minutes) is refused", why and "lapsed" in why, why)

# a new grant fences the old holder
tok2 = M.grant(r, MOD, lease="L2", ts=ts(11))
check("the next lease token is higher", tok2 == 2, tok2)
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "n", body={"text": "stale"}, token=1, ts=ts(12), now=ts(12))
check("the old holder's token is stale after a newer grant", why and "stale" in why, why)
M.append(r, MOD, "HOLDER.L2", "finding.claimed_fixed", "F_BLAST",
         body={"text": "applied the proposed fix", "test": "selftest_blast.py"}, token=2, ts=ts(13), now=ts(13))
check("the new holder appends with the current token", M.reduce(M.read(r, MOD))["findings"]["F_BLAST"]["status"]
      == "claimed_fixed")

M.append(r, MOD, "HOLDER.L2", "lease.release", "HOLDER/%s" % MOD, body={"text": "stage done"}, token=2, ts=ts(13, 30),
         now=ts(13, 30))
why = refuses(M.append, r, MOD, "HOLDER.L2", "note", "n", body={"text": "after release"}, token=2, ts=ts(13, 40),
              now=ts(13, 40))
check("a released lease takes no more holder events", why and "released" in why, why)

# ---- refusals at lint (lines written by hand, bypassing append) ------------------------------------------------------
def handwrite(root, shard_name, ev):
    p = M.shard_path(root, MOD, shard_name)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, separators=(",", ":")) + "\n")


def base_ev(**kw):
    ev = {"id": "x:" + kw.get("subject", "s"), "key": "k-" + kw.get("subject", "s"), "ts": ts(14), "tsn": 1,
          "mod": MOD, "version": "0.1.0", "writer": "HOLDER.L1", "run": None, "kind": "note", "subject": "s",
          "body": {"text": "hand"}, "evidence": []}
    ev.update(kw)
    return ev


r2 = fresh(); roots.append(r2)
shutil.rmtree(os.path.join(r2, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r2, "design"))
handwrite(r2, "HOLDER.L1", base_ev(subject="stale1", token=1, writer="HOLDER.L1"))
check("lint refuses a HOLDER line carrying a stale fencing token", "STALE_TOKEN" in codes(M.lint(r2, MOD, None)[0]),
      M.lint(r2, MOD, None)[0])

r3 = fresh(); roots.append(r3)
shutil.rmtree(os.path.join(r3, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r3, "design"))
handwrite(r3, "JUDGE.J1", base_ev(subject="planted", writer="HOLDER.L2", token=2, kind="finding.claimed_fixed"))
handwrite(r3, "OWNER", base_ev(subject="forged", writer="HOLDER.L2", token=2, kind="note"))
f3 = M.lint(r3, MOD, None)[0]
check("lint refuses a holder's line in a JUDGE shard",
      any(c == "WRONG_SHARD" and p.endswith("JUDGE.J1.jsonl") for c, p, *_ in f3), f3)
check("lint refuses a holder's line in the OWNER shard",
      any(c == "WRONG_SHARD" and p.endswith("OWNER.jsonl") for c, p, *_ in f3), f3)

r4 = fresh(); roots.append(r4)
shutil.rmtree(os.path.join(r4, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r4, "design"))
handwrite(r4, "JUDGE.J1", base_ev(subject="F_HAND", writer="JUDGE.J1", run="J1", kind="finding.open",
                                  body={"text": "no fix written"}))
check("lint refuses a finding with no proposed fix", "NO_PROPOSED_FIX" in codes(M.lint(r4, MOD, None)[0]),
      M.lint(r4, MOD, None)[0])

# sealed judge shard
M.seal(r, MOD, "J1", ts=ts(15))
check("a sealed judge shard lints clean", M.lint(r, MOD, None)[0] == [], M.lint(r, MOD, None)[0])
why = refuses(M.append, r, MOD, "JUDGE.J1", "note", "late", body={"text": "after seal"}, run="J1", ts=ts(16))
check("append to a sealed judge shard is refused", why and "sealed" in why, why)
r5 = fresh(); roots.append(r5)
shutil.rmtree(os.path.join(r5, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r5, "design"))
handwrite(r5, "JUDGE.J1", base_ev(subject="late2", writer="JUDGE.J1", run="J1", kind="note"))
check("lint refuses a judge shard that changed after its seal", "SEALED_CHANGED" in codes(M.lint(r5, MOD, None)[0]),
      M.lint(r5, MOD, None)[0])

# ---- views: hand-edited and stale -----------------------------------------------------------------------------------
vdir = M.views_dir(r, MOD)
check("views exist after append", all(os.path.exists(os.path.join(vdir, v)) for v in M.VIEWS), os.listdir(vdir))
r6 = fresh(); roots.append(r6)
shutil.rmtree(os.path.join(r6, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r6, "design"))
sp = os.path.join(M.views_dir(r6, MOD), "state.md")
with open(sp, encoding="utf-8") as fh:
    body = fh.read()
with open(sp, "w", encoding="utf-8") as fh:
    fh.write(body.replace("blast radius ignores walls", "blast radius is fine"))
check("lint refuses a hand-edited view", "VIEW_EDITED" in codes(M.lint(r6, MOD, None)[0]), M.lint(r6, MOD, None)[0])
r7 = fresh(); roots.append(r7)
shutil.rmtree(os.path.join(r7, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r7, "design"))
M.append(r7, MOD, "STEWARD", "decision", "D_SCOPE", body={"text": "scope holds"}, authority={"why": "test"},
         ts=ts(17), views=False)
check("lint refuses a view built from older shards", "VIEW_STALE" in codes(M.lint(r7, MOD, None)[0]),
      M.lint(r7, MOD, None)[0])
M.write_views(r7, MOD)
check("regenerating views clears the stale view", M.lint(r7, MOD, None)[0] == [], M.lint(r7, MOD, None)[0])

# ---- superseded event -----------------------------------------------------------------------------------------------
did, _ = M.append(r, MOD, "STEWARD", "decision", "D_RADIUS", body={"text": "radius 6"}, authority={"why": "test"},
                  ts=ts(18))
M.append(r, MOD, "STEWARD", "decision", "D_RADIUS", body={"text": "radius 4, per his answer"},
         authority={"why": "test"}, supersedes=did, ts=ts(19))
st = M.reduce(M.read(r, MOD))
check("a superseded event no longer counts", st["decisions"]["D_RADIUS"]["text"] == "radius 4, per his answer" and
      did in st["superseded"], st["decisions"].get("D_RADIUS"))
why = refuses(M.append, r, MOD, "STEWARD", "decision", "D_X", body={"text": "x"}, authority={"why": "t"},
              supersedes="nope:000", ts=ts(20))
check("superseding an id the ledger does not hold is refused", why and "supersedes" in why, why)
mid, _ = M.append(r, MOD, "JUDGE.J9", "finding.open", "F_MISTAKE",
                  body={"text": "a wrong finding", "proposed_fix": "change nothing; this is the test's mistake"},
                  run="J9", ts=ts(21))
M.append(r, MOD, "JUDGE.J10", "note", "F_MISTAKE", body={"text": "withdrawn: wrong build"}, run="J10",
         supersedes=mid, ts=ts(22))
check("a superseded finding with no replacement drops out of the state",
      "F_MISTAKE" not in M.reduce(M.read(r, MOD))["findings"], M.reduce(M.read(r, MOD))["findings"].get("F_MISTAKE"))
check("ledger with a superseded event lints clean", M.lint(r, MOD, None)[0] == [], M.lint(r, MOD, None)[0])

# ---- not a strict extension of its published form (git) -------------------------------------------------------------
r8 = fresh(); roots.append(r8)
shutil.rmtree(os.path.join(r8, "design")); shutil.copytree(os.path.join(r, "design"), os.path.join(r8, "design"))
git_repo(r8)
commit_all(r8, "base")
git(r8, "branch", "published")
check("against its published form, an unchanged ledger lints clean", M.lint(r8, MOD, base="published")[0] == [],
      M.lint(r8, MOD, base="published")[0])
dp = M.shard_path(r8, MOD, "STEWARD")
with open(dp, encoding="utf-8") as fh:
    lines = fh.readlines()
with open(dp, "w", encoding="utf-8") as fh:
    fh.writelines(lines[1:])
check("lint refuses a shard that lost a published line", "NOT_APPEND" in codes(M.lint(r8, MOD, base="published")[0]),
      M.lint(r8, MOD, base="published")[0])
with open(dp, "w", encoding="utf-8") as fh:
    fh.writelines([lines[0].replace("radius 6", "radius 5")] + lines[1:])
check("lint refuses a published line edited in place",
      "NOT_APPEND" in codes(M.lint(r8, MOD, base="published")[0]), M.lint(r8, MOD, base="published")[0])

# ---- packet budget ------------------------------------------------------------------------------------------------
r9 = fresh(); roots.append(r9)
M.append(r9, MOD, "DISPATCH", "version.open", "version", body={"version": "0.2.0"}, version="0.2.0", ts=ts(0))
for i in range(60):
    j = "JUDGE.K%d" % i
    M.append(r9, MOD, j, "finding.open", "F_OLD_%02d" % i,
             body={"text": "old closed finding %d " % i + "padding " * 40, "proposed_fix": "fix %d " % i + "x " * 40},
             run="K%d" % i, ts=ts(1, i % 60), views=False)
    M.append(r9, MOD, "JUDGE.V%d" % i, "finding.verified", "F_OLD_%02d" % i, body={"text": "verified"},
             run="V%d" % i, ts=ts(2, i % 60), views=False)
M.append(r9, MOD, "JUDGE.N1", "finding.open", "F_STILL_OPEN",
         body={"text": "the open one", "proposed_fix": "the precise open fix"}, run="N1", ts=ts(3), views=False)
M.append(r9, MOD, "OWNER", "question.answer", "Q_KEEP", body={"text": "his kept answer"},
         authority={"by_card": "Keep? -> yes"}, ts=ts(4), views=False)
tok = M.grant(r9, MOD, lease="H1", ts=ts(5))
M.append(r9, MOD, "HOLDER.H1", "cause.refuted", "C_KEEP", body={"text": "the refuted cause"}, token=tok, ts=ts(6),
         now=ts(6), views=False)
full, finfo = M.packet(r9, MOD, budget=100000)
small, sinfo = M.packet(r9, MOD, budget=2500)
check("an unbounded packet leaves out nothing but the full history", finfo["dropped"] == {}, finfo["dropped"])
check("a packet over budget drops old closed findings first", sinfo["dropped"].get("closed findings", 0) > 0 and
      sinfo["tokens"] <= 2500, (sinfo["dropped"], sinfo["tokens"]))
check("the cut takes the OLDEST closed findings first", "F_OLD_59" in small and "F_OLD_00" not in small,
      small[-1500:])
check("the open finding, its fix, the refuted cause and his answer survive the cut",
      all(s in small for s in ("F_STILL_OPEN", "the precise open fix", "C_KEEP", "his kept answer")), small[-1500:])
check("the packet ends by naming what it left out", "## Left out" in small and "closed findings" in
      small.split("## Left out")[1], small[-600:])
LONG = "his long answer " + "word " * 400 + "THE_END"
M.append(r9, MOD, "OWNER", "question.answer", "Q_LONG", body={"text": LONG}, authority={"owner_said": "long"},
         ts=ts(7), views=False)
lp, _ = M.packet(r9, MOD, budget=100000)
line = [l for l in lp.split("\n") if l.startswith("- Q_LONG")][0]
check("a long text is clipped in the packet with a pointer to the command that prints it whole",
      "THE_END" not in line and "modledger.py show --mod %s Q_LONG" % MOD in line, line[-200:])
check("the ledger keeps the long text whole", any(e.get("subject") == "Q_LONG" and "THE_END" in (e["body"].get("text")
                                                                                         or "") for e in M.read(r9, MOD)))
tiny, tinfo = M.packet(r9, MOD, budget=50)
check("a packet whose must-keep part alone passes the budget says OVER BUDGET",
      tinfo["over_budget"] and "OVER BUDGET" in tiny, tinfo)

# ---- the CLI the way it is used ------------------------------------------------------------------------------------
env = dict(os.environ, RM_MODLEDGER_ROOT=r9)
p = subprocess.run([sys.executable, CLI, "packet", "--mod", MOD], capture_output=True, text=True, env=env)
check("CLI packet prints from the ledger", p.returncode == 0 and "F_STILL_OPEN" in p.stdout, p.stderr[-400:])
p = subprocess.run([sys.executable, CLI, "views", "--mod", MOD], capture_output=True, text=True, env=env)
p = subprocess.run([sys.executable, CLI, "lint", "--mod", MOD, "--base", ""], capture_output=True, text=True, env=env)
check("CLI lint is clean after views", p.returncode == 0, p.stdout[-400:] + p.stderr[-400:])
p = subprocess.run([sys.executable, CLI, "append", "--mod", MOD, "--writer", "JUDGE.Z", "--run", "Z", "--kind",
                    "finding.open", "--subject", "F_CLI", "--text", "no fix"], capture_output=True, text=True, env=env)
check("CLI append refuses a finding with no fix, exit 1", p.returncode == 1 and "proposed_fix" in p.stdout + p.stderr,
      (p.returncode, p.stdout[-300:], p.stderr[-300:]))
p = subprocess.run([sys.executable, CLI, "show", "--mod", MOD, "F_STILL_OPEN"], capture_output=True, text=True,
                   env=env)
check("CLI show prints one subject's events", p.returncode == 0 and "finding.open" in p.stdout, p.stdout[-300:])

for d in roots:
    shutil.rmtree(d, ignore_errors=True)
print("selftest_modledger: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
