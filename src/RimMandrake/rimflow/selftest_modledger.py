#!/usr/bin/env python3
"""Selftest for modledger.py — the per-mod ledger of the holder-pipeline fusion, under the entry standard.

    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_modledger

Items RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE and RIMMANDRAKE_ADOPT_ENTRY_STANDARD_IN_MODLEDGER_FOURTEEN_OWED;
specs design/specs/2026-11-15-holder-pipeline-fusion.md §3.1-3.3 and design/specs/2026-11-15-mod-ledger-entry-standard.md.
Every case runs against a throwaway repo root in a temp dir (never this repo's concept folders). The lint must REFUSE: a
hand-edited view, a line changed in place, a HOLDER event with a stale lease token, a holder writing into a JUDGE or
OWNER shard, a finding with no proposed fix, a sealed judge shard that grew, a hand-written line that breaks the
standard, a `sha:` ref not on the base. Append must REFUSE every rule of the standard's sheet, each refusal saying what
was measured, what would pass and the smallest fix: oversize fields and lines, a missing per-kind field, a pasted log or
newline, more than 6 or untyped refs, an unknown bar or facet, a subject outside the classes, a near-duplicate subject
without a reason, the same text again, a no-change test result, a lifecycle kind from a miner, narration. Nothing is
spilled to a side file. The packet stays inside its budget dropping old closed material first, never an open finding,
a trap, a refuted cause or his answer; closed subjects are one line; notes are never in it; it ends with its cursor.
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
FB = "finding:RIMMANDRAKE_STOP_BLAST_AT_WALLS_RAY_IGNORED"
FM = "finding:RIMMANDRAKE_WITHDRAW_WRONG_BUILD_FINDING_FIXTURE"
FSO = "finding:RIMMANDRAKE_KEEP_STILL_OPEN_FINDING_IN_PACKET"
CT = "cause:comp-ticks-only-ticklong"
BAR = "blast_stops_at_walls"
LOCK = {"text": "a thrown pawn stops at the first wall"}


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:600]))
    if not ok:
        FAIL.append(name)


def refuses(fn, *a, **kw):
    """-> the refusal text, None if it passed. Any other exception is a refusal for the fail-first run on the base
    commit (a missing verb or keyword is a FAIL there, not a crash)."""
    try:
        fn(*a, **kw)
    except Exception as e:                       # noqa: BLE001
        return "%s: %s" % (type(e).__name__, e)
    return None


def put(*a, **kw):
    """A fixture append. On the base commit (the fail-first run) a kind or keyword the old tool lacks is one FAIL here
    and the run goes on, so every later check is seen failing on its own."""
    try:
        return M.append(*a, **kw)
    except Exception as e:                       # noqa: BLE001
        check("fixture append %s %s" % (a[3:5], kw.get("ts", "")), False, "%s: %s" % (type(e).__name__, e))
        return None, False


def std_refusal(why, field):
    """A refusal in the standard's shape: REFUSED <field>: <measured> · would pass: … · smallest fix: …"""
    return bool(why) and ("REFUSED %s:" % field) in why and "would pass:" in why and "smallest fix:" in why


def codes(findings):
    return sorted({f[0] for f in findings})


def fresh():
    root = tempfile.mkdtemp(prefix="modledger_self_")
    os.makedirs(os.path.join(root, "design", "concepts", MOD))
    os.makedirs(os.path.join(root, "Source"))
    for f in ("Source/Blast.cs", "x"):              # the files the fixtures' path: refs cite
        with open(os.path.join(root, f), "w", encoding="utf-8") as fh:
            fh.write("fixture\n")
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


def finding(text, fix="in Blast.cs, stop the ray at the first impassable cell (GenSight.LineOfSight)",
            bars=(BAR,), **kw):
    b = {"class": "problem", "bars": list(bars) if isinstance(bars, (list, tuple)) else bars, "text": text,
         "proposed_fix": fix, "accept": "selftest_blast.py exit 0 (row WALL_STOP PASS)"}
    b.update(kw)
    return b


def letters(i):
    return chr(65 + i // 26) + chr(65 + i % 26)


roots = []

# ---- config: one place for the numbers ----------------------------------------------------------------------------
cfg = M.config()
check("config names the 400k holder ceiling (his 'Try 400k first.')", cfg.get("holder_context_ceiling_tokens") == 400000,
      cfg.get("holder_context_ceiling_tokens"))
check("config names the 15k packet budget", cfg.get("packet_budget_tokens") == 15000, cfg.get("packet_budget_tokens"))
S = cfg.get("standard") or {}
caps = S.get("caps") or {}
check("config holds the standard's caps (text/fix 320, accept 240, said 600, line 1536, 6 refs x 160)",
      (caps.get("text"), caps.get("proposed_fix"), caps.get("accept"), caps.get("said"), S.get("line_bytes"),
       S.get("evidence_max"), S.get("evidence_ref_chars")) == (320, 320, 240, 600, 1536, 6, 160),
      (caps, S.get("line_bytes")))
check("config holds the eight facets", sorted(S.get("facets") or []) == sorted(
    ["code", "instrument", "test", "live", "settings", "art", "perf", "other-mod"]), S.get("facets"))
check("the spill to a side file is gone (no SPILL_HEAD, no _spill)", not hasattr(M, "SPILL_HEAD") and
      not hasattr(M, "_spill"))

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
put(r, MOD, "DISPATCH", "stage.accepted", "stage", body={"to": 2, "from": 1}, ts=ts(2))
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

# ---- many shards: bars, leases, holder, judge, owner ----------------------------------------------------------------
put(r, MOD, "OWNER", "bar.locked", "bar:" + BAR, body=LOCK, authority={"by_card": "Lock the bars? -> yes"},
         ts=ts(2, 30))
tok1 = M.grant(r, MOD, lease="L1", ts=ts(3))
check("first lease token is 1", tok1 == 1, tok1)
fid, _ = M.append(r, MOD, "JUDGE.J1", "finding.open", FB, body=finding("blast radius ignores walls"),
                  evidence=["path:Source/Blast.cs"], run="J1", ts=ts(3, 30))
put(r, MOD, "HOLDER.L1", "cause.tried", CT, body={"text": "the comp ticks only TickLong", "finding": FB,
                                                       "decides": "a tick probe counting CompTick calls"},
         token=1, ts=ts(4), now=ts(4))
put(r, MOD, "HOLDER.L1", "cause.refuted", CT, body={"text": "ticks fine; refuted by the tick probe", "finding": FB,
                                                         "depends_on": ["Source/Comp.cs"]},
         code_sha="abc123", token=1, ts=ts(5), now=ts(5))
put(r, MOD, "OWNER", "question.answer", "q:blast-radius", body={"said": "Keep the radius at 4."},
         authority={"owner_said": "Keep the radius at 4."}, ts=ts(7))
put(r, MOD, "HOLDER.L1", "question.ask", "q:knockback-stuns", body={"text": "Should knockback stun?",
                                                                         "obvious": "no",
                                                                         "against": "the bar mentions a stun"},
         token=1, ts=ts(8), now=ts(8))
put(r, MOD, "HOLDER.L1", "session.id", "session", body={"session_id": "s-1", "context_tokens": 410000},
         token=1, ts=ts(9), now=ts(9))
evs = M.read(r, MOD)
shards = sorted({e["_shard"] for e in evs})
check("many shards: DISPATCH, HOLDER.L1, JUDGE.J1, OWNER", shards == ["DISPATCH", "HOLDER.L1", "JUDGE.J1", "OWNER"],
      shards)
check("merged read is in time order across shards", [e["ts"] for e in evs] == sorted(e["ts"] for e in evs))
check("seq is the line number in its own shard", all(e["_seq"] >= 1 for e in evs) and
      [e["_seq"] for e in evs if e["_shard"] == "HOLDER.L1"] == [1, 2, 3, 4])
st = M.reduce(evs)
check("open finding carries the finder's proposed fix and accept", st["findings"][FB]["status"] == "open" and
      "LineOfSight" in st["findings"][FB]["proposed_fix"] and "WALL_STOP" in (st["findings"][FB].get("accept") or ""),
      st["findings"].get(FB))
check("refuted cause is kept with what it was refuted on", st["causes"][CT]["status"] == "refuted" and
      st["causes"][CT]["code_sha"] == "abc123", st["causes"].get(CT))
check("his answer is read from `said`, verbatim", st["answers"].get("q:blast-radius", {}).get("answer") ==
      "Keep the radius at 4.", st["answers"])
check("rotation is due once the session passes the configured ceiling", st["session"]["rotate_due"] is True,
      st["session"])
check("many-shard ledger lints clean", M.lint(r, MOD, base=None)[0] == [], M.lint(r, MOD, None)[0])

# ---- refusals at append (the writer rules) --------------------------------------------------------------------------
NF = "finding:RIMMANDRAKE_FIND_FIXTURE_THING_WITH_NO_FIX"
why = refuses(M.append, r, MOD, "JUDGE.J1", "finding.open", NF,
              body={"class": "problem", "bars": [BAR], "text": "something is off", "accept": "none, fixture"},
              evidence=["path:x"], run="J1", ts=ts(10))
check("finding with no proposed fix is refused at append", why and "proposed_fix" in why, why)
NOTE = {"text": "x marks it", "about": "stage"}
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "stage", body=NOTE, token=7, ts=ts(10), now=ts(10))
check("holder append with a token it was never granted is refused", why and "token" in why, why)
why = refuses(M.append, r, MOD, "HOLDER.L1", "finding.verified", FB, body={"text": "fixed"}, code_sha="abc123",
              token=1, ts=ts(10), now=ts(10))
check("a holder may not verify a finding (only a judge turns one green)", why and "may not" in why, why)
why = refuses(M.append, r, MOD, "JUDGE.J1", "note", "stage", body={"text": "planted", "about": "stage"}, run="J1",
              ts=ts(10), env_writer="HOLDER.L1")
check("a holder process (env writer) may not append to a JUDGE shard", why and "HOLDER.L1" in why, why)
why = refuses(M.append, r, MOD, "OWNER", "question.answer", "q:x", body={"said": "yes"}, ts=ts(10),
              env_writer="HOLDER.L1")
check("a holder process may not append to the OWNER shard", why is not None, why)
why = refuses(M.append, r, MOD, "OWNER", "question.answer", "q:x", body={"said": "yes"}, ts=ts(10))
check("an OWNER event without his words, card or ruling is refused", why and "authority" in why, why)
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "stage", body={"text": "late note", "about": "stage"}, token=1,
              ts=ts(59), now=ts(59))
check("a lapsed lease (idle past the configured minutes) is refused", why and "lapsed" in why, why)

# a new grant fences the old holder
tok2 = M.grant(r, MOD, lease="L2", ts=ts(11))
check("the next lease token is higher", tok2 == 2, tok2)
why = refuses(M.append, r, MOD, "HOLDER.L1", "note", "stage", body={"text": "stale note", "about": "stage"}, token=1,
              ts=ts(12), now=ts(12))
check("the old holder's token is stale after a newer grant", why and "stale" in why, why)
put(r, MOD, "HOLDER.L2", "finding.claimed_fixed", FB,
         body={"text": "applied the proposed fix", "test": "selftest_blast.py rc 1 then rc 0"}, code_sha="def456",
         token=2, ts=ts(13), now=ts(13))
check("the new holder appends with the current token", M.reduce(M.read(r, MOD))["findings"][FB]["status"]
      == "claimed_fixed")
_pk = M.packet(r, MOD)[0].split("\n")
_at = next(i for i, l in enumerate(_pk) if l.startswith("- " + FB + " "))
_fb = [l for l in _pk[_at + 1:] if l.startswith("  ")][:3]
check("a claimed-fixed finding prints its accept and its claim, not its spent proposed fix (the packet line rule)",
      not any(l.startswith("  proposed fix:") for l in _fb) and any(l.startswith("  holder: applied") for l in _fb), _fb)
put(r, MOD, "HOLDER.L2", "lease.release", "lease", body={"text": "stage done"}, token=2, ts=ts(13, 30),
         now=ts(13, 30))
why = refuses(M.append, r, MOD, "HOLDER.L2", "note", "stage", body={"text": "after release", "about": "stage"},
              token=2, ts=ts(13, 40), now=ts(13, 40))
check("a released lease takes no more holder events", why and "released" in why, why)


# ---- refusals at lint (lines written by hand, bypassing append) ------------------------------------------------------
def handwrite(root, shard_name, ev):
    p = M.shard_path(root, MOD, shard_name)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, separators=(",", ":")) + "\n")


def base_ev(**kw):
    ev = {"id": "x:" + kw.get("subject", "s"), "key": "k-" + kw.get("subject", "s"), "ts": ts(14), "tsn": 1,
          "mod": MOD, "version": "0.1.0", "writer": "HOLDER.L1", "run": None, "kind": "note", "subject": "stage",
          "body": {"text": "hand", "about": "stage"}, "evidence": []}
    ev.update(kw)
    return ev


def clone(src):
    d = fresh()
    roots.append(d)
    shutil.rmtree(d)
    shutil.copytree(src, d)
    return d


r2 = clone(r)
handwrite(r2, "HOLDER.L1", base_ev(subject="stage", token=1, writer="HOLDER.L1", key="k-stale1", id="x:stale1"))
check("lint refuses a HOLDER line carrying a stale fencing token", "STALE_TOKEN" in codes(M.lint(r2, MOD, None)[0]),
      M.lint(r2, MOD, None)[0])

r3 = clone(r)
handwrite(r3, "JUDGE.J1", base_ev(subject=FB, writer="HOLDER.L2", token=2, kind="finding.claimed_fixed", key="k-pl",
                                  id="x:pl"))
handwrite(r3, "OWNER", base_ev(subject="stage", writer="HOLDER.L2", token=2, kind="note", key="k-fo", id="x:fo"))
f3 = M.lint(r3, MOD, None)[0]
check("lint refuses a holder's line in a JUDGE shard",
      any(c == "WRONG_SHARD" and p.endswith("JUDGE.J1.jsonl") for c, p, *_ in f3), f3)
check("lint refuses a holder's line in the OWNER shard",
      any(c == "WRONG_SHARD" and p.endswith("OWNER.jsonl") for c, p, *_ in f3), f3)

r4 = clone(r)
handwrite(r4, "JUDGE.J1", base_ev(subject="finding:RIMMANDRAKE_HAND_WRITE_FINDING_NO_FIX", writer="JUDGE.J1",
                                  run="J1", kind="finding.open", body={"text": "no fix written"}, key="k-h", id="x:h"))
check("lint refuses a finding with no proposed fix", "NO_PROPOSED_FIX" in codes(M.lint(r4, MOD, None)[0]),
      M.lint(r4, MOD, None)[0])
check("lint re-runs the standard over a hand-written line (missing class, bars, accept, evidence)",
      "STANDARD" in codes(M.lint(r4, MOD, None)[0]), M.lint(r4, MOD, None)[0])

# sealed judge shard
M.seal(r, MOD, "J1", ts=ts(15))
check("a sealed judge shard lints clean", M.lint(r, MOD, None)[0] == [], M.lint(r, MOD, None)[0])
why = refuses(M.append, r, MOD, "JUDGE.J1", "note", "stage", body={"text": "after seal", "about": "stage"}, run="J1",
              ts=ts(16))
check("append to a sealed judge shard is refused", why and "sealed" in why, why)
r5 = clone(r)
handwrite(r5, "JUDGE.J1", base_ev(writer="JUDGE.J1", run="J1", kind="note", key="k-l2", id="x:l2"))
check("lint refuses a judge shard that changed after its seal", "SEALED_CHANGED" in codes(M.lint(r5, MOD, None)[0]),
      M.lint(r5, MOD, None)[0])

# ---- views: hand-edited and stale -----------------------------------------------------------------------------------
vdir = M.views_dir(r, MOD)
check("views exist after append", all(os.path.exists(os.path.join(vdir, v)) for v in M.VIEWS), os.listdir(vdir))
r6 = clone(r)
sp = os.path.join(M.views_dir(r6, MOD), "state.md")
with open(sp, encoding="utf-8") as fh:
    body = fh.read()
with open(sp, "w", encoding="utf-8") as fh:
    fh.write(body.replace("blast radius ignores walls", "blast radius is fine"))
check("lint refuses a hand-edited view", "VIEW_EDITED" in codes(M.lint(r6, MOD, None)[0]), M.lint(r6, MOD, None)[0])
r7 = clone(r)
put(r7, MOD, "STEWARD", "decision", "q:scope", body={"text": "scope holds"}, authority={"why": "test"},
         ts=ts(17), views=False)
check("lint refuses a view built from older shards", "VIEW_STALE" in codes(M.lint(r7, MOD, None)[0]),
      M.lint(r7, MOD, None)[0])
M.write_views(r7, MOD)
check("regenerating views clears the stale view", M.lint(r7, MOD, None)[0] == [], M.lint(r7, MOD, None)[0])

# ---- superseded event, withdrawn finding ----------------------------------------------------------------------------
did, _ = M.append(r, MOD, "STEWARD", "decision", "q:radius-decision", body={"text": "radius 6"},
                  authority={"why": "test"}, ts=ts(18))
put(r, MOD, "STEWARD", "decision", "q:radius-decision", body={"text": "radius 4, per his answer"},
         authority={"why": "test"}, supersedes=did, ts=ts(19))
st = M.reduce(M.read(r, MOD))
check("a superseded event no longer counts", st["decisions"]["q:radius-decision"]["text"] == "radius 4, per his answer"
      and did in st["superseded"], st["decisions"].get("q:radius-decision"))
why = refuses(M.append, r, MOD, "STEWARD", "decision", "q:x-decision", body={"text": "x"}, authority={"why": "t"},
              supersedes="nope:000", ts=ts(20))
check("superseding an id the ledger does not hold is refused", why and "supersedes" in why, why)
mid, _ = M.append(r, MOD, "JUDGE.J9", "finding.open", FM,
                  body=finding("a wrong finding about a build that never shipped",
                               fix="change nothing; this is the fixture's planted mistake"),
                  evidence=["run:J9"], run="J9", ts=ts(21))
put(r, MOD, "JUDGE.J10", "finding.withdrawn", FM, body={"text": "not a defect: the judge read a wrong build",
                                                            "how_checked": "repro"},
         code_sha="abc123", run="J10", ts=ts(22))
st = M.reduce(M.read(r, MOD))
check("finding.withdrawn reduces to status withdrawn (no free note)", st["findings"].get(FM, {}).get("status") ==
      "withdrawn", st["findings"].get(FM))
check("ledger with a superseded event lints clean", M.lint(r, MOD, None)[0] == [], M.lint(r, MOD, None)[0])

# ---- traps ----------------------------------------------------------------------------------------------------------
put(r, MOD, "JUDGE.J11", "trap.noted", "trap:geometry-check-reads-seven-scenes",
         body={"text": "the geometry check is green while reading only the 7 oracle scenes; green proves nothing about "
                       "random sites", "where": "T_CORD_GEOMETRY_OFFLINE", "tags": ["test", "instrument"]},
         run="J11", ts=ts(23))
put(r, MOD, "JUDGE.J11", "trap.noted", "trap:dead-sha-at-landing",
         body={"text": "a sha cited before publish can vanish; cite only the one PUBLISHED prints", "where": "./publish"},
         run="J11", ts=ts(23, 10))
put(r, MOD, "JUDGE.J11", "trap.cleared", "trap:dead-sha-at-landing",
         body={"text": "publish now prints the landed sha and the lint checks sha: refs", "where": "./publish"},
         run="J11", ts=ts(23, 20))
st = M.reduce(M.read(r, MOD))
check("trap.noted / trap.cleared reduce to traps{}", st.get("traps", {}).get("trap:geometry-check-reads-seven-scenes",
                                                                             {}).get("status") == "noted" and
      st["traps"].get("trap:dead-sha-at-landing", {}).get("status") == "cleared", st.get("traps"))
pk, _ = M.packet(r, MOD)
check("the packet lists live traps and not cleared ones", "## Traps" in pk and "geometry-check-reads-seven" in pk and
      "dead-sha-at-landing" not in pk.split("## Traps")[-1].split("\n## ")[0], pk[-1500:])

# ---- the entry standard: refusals at append ------------------------------------------------------------------------
rs = fresh(); roots.append(rs)
put(rs, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0", ts=ts(0))
put(rs, MOD, "OWNER", "bar.locked", "bar:" + BAR, body=LOCK, authority={"by_card": "Lock? -> yes"}, ts=ts(1))
G = "finding:RIMMANDRAKE_LOCK_GOOD_FINDING_FOR_STANDARD"


def try_open(subject=G, body=None, evidence=("path:Source/Blast.cs",), **kw):
    return refuses(M.append, rs, MOD, "JUDGE.S1", "finding.open", subject, body=body, evidence=list(evidence),
                   run="S1", ts=ts(2), **kw)


T320 = "w" * 316 + " end"
check("a text of exactly 320 chars passes", try_open(body=finding(T320)) is None, try_open(body=finding(T320)))
why = refuses(M.append, rs, MOD, "JUDGE.S2", "finding.open", "finding:RIMMANDRAKE_SIZE_OVERSIZE_TEXT_ONE_TOO_MANY",
              body=finding(T320 + "x"), evidence=["path:x"], run="S2", ts=ts(3))
check("oversize text (321 chars) is refused in the standard's shape", std_refusal(why, "text") and "321" in (why or ""),
      why)
check("an oversize refusal names the split, and nothing is spilled to ledger/text/", why and "split" in why and
      not os.path.isdir(os.path.join(M.ledger_dir(rs, MOD), "text")), why)
why = try_open(subject="finding:RIMMANDRAKE_SIZE_OVERSIZE_FIX_FIELD_CHECK", body=finding("fix too long", fix="f" * 321))
check("oversize proposed_fix is refused", std_refusal(why, "proposed_fix"), why)
why = try_open(subject="finding:RIMMANDRAKE_SIZE_OVERSIZE_ACCEPT_FIELD_CHECK",
               body=finding("accept too long", accept="a" * 241))
check("oversize accept (241 > 240) is refused", std_refusal(why, "accept"), why)
why = refuses(M.append, rs, MOD, "OWNER", "question.answer", "q:long-said", body={"said": "s" * 601},
              authority={"owner_said": "s"}, ts=ts(3))
check("his `said` past 600 chars is refused (keep the deciding sentence, cite the rest)", std_refusal(why, "said"), why)
why = try_open(subject="finding:RIMMANDRAKE_SIZE_WHOLE_LINE_PAST_THE_CAP",
               body=finding("t" * 300, fix="f" * 300, accept="a" * 230),
               evidence=["path:" + "p" * 150 + str(i) for i in range(6)])
check("a line past 1536 bytes is refused even with every field under its cap", std_refusal(why, "line"), why)
# missing per-kind fields, and the empty / optional / nested / invalid shapes
why = try_open(subject="finding:RIMMANDRAKE_MISS_ACCEPT_ON_A_FINDING_CHECK",
               body={"class": "problem", "bars": [BAR], "text": "no accept", "proposed_fix": "a precise enough fix"})
check("finding.open with no accept is refused", std_refusal(why, "accept"), why)
why = try_open(subject="finding:RIMMANDRAKE_MISS_EVERYTHING_EMPTY_BODY_CHECK", body={})
check("an empty body is refused naming a missing field", why and "REFUSED" in why and "missing" in why, why)
why = try_open(subject="finding:RIMMANDRAKE_MISS_EVERYTHING_NONE_BODY_CHECK", body=None)
check("a None body is refused like an empty one", why and "REFUSED" in why and "missing" in why, why)
why = try_open(subject="finding:RIMMANDRAKE_NEST_TEXT_INSIDE_A_DICT_CHECK", body=finding({"nested": "text"}))
check("a nested (non-string) text is refused", std_refusal(why, "text"), why)
why = try_open(subject="finding:RIMMANDRAKE_TYPE_BARS_AS_A_STRING_CHECK", body=finding("bars is a string", bars=BAR))
check("bars given as a string, not a list, is refused", std_refusal(why, "bars"), why)
why = try_open(subject="finding:RIMMANDRAKE_LEAVE_BARS_EMPTY_WITHOUT_FACET", body=finding("no bar, no facet", bars=()))
check("empty bars with no facet tag is refused", std_refusal(why, "bars"), why)
check("empty bars with a facet tag passes (a miner that cannot tell)",
      try_open(subject="finding:RIMMANDRAKE_LEAVE_BARS_EMPTY_WITH_A_FACET",
               body=finding("no bar but an instrument facet", bars=(), tags=["instrument"])) is None)
why = try_open(subject="finding:RIMMANDRAKE_TAG_UNKNOWN_FACET_ON_FINDING", body=finding("bad tag", tags=["vibes"]))
check("an unknown facet tag is refused", std_refusal(why, "tags"), why)
why = try_open(subject="finding:RIMMANDRAKE_BAR_UNKNOWN_ID_ON_FINDING_CHECK",
               body=finding("unknown bar", bars=("no_such_bar",)))
check("an unknown bar id is refused (bars come from the mod's locked bars)", std_refusal(why, "bars") and
      "no_such_bar" in why, why)
why = try_open(subject="finding:RIMMANDRAKE_CLASS_NOT_IN_THE_CLOSED_SET", body=finding("bad class", **{"class": "bug"}))
check("a class outside problem/polish is refused", std_refusal(why, "class"), why)
# pasted logs, newlines, narration
why = try_open(subject="finding:RIMMANDRAKE_PASTE_NEWLINE_INTO_FINDING_TEXT", body=finding("line one\nline two"))
check("a newline in text is refused", std_refusal(why, "text"), why)
why = try_open(subject="finding:RIMMANDRAKE_PASTE_STACK_INTO_FINDING_TEXT",
               body=finding("Crash at Verse.ContentFinder`1.TryFindAssetInModBundles(String path)"))
check("a pasted stack frame in text is refused", std_refusal(why, "text") and "cite" in why, why)
why = try_open(subject="finding:RIMMANDRAKE_PASTE_FENCE_INTO_FINDING_TEXT", body=finding("see ```code``` here"))
check("a code fence in text is refused", std_refusal(why, "text"), why)
why = try_open(subject="finding:RIMMANDRAKE_NARRATE_STARTED_LOOKING_FINDING",
               body=finding("Started looking at the bend again; nothing new yet"))
check("narration ('Started…') is refused", std_refusal(why, "text") and "narration" in why, why)
# evidence
why = try_open(subject="finding:RIMMANDRAKE_CITE_SEVEN_REFS_ON_FINDING", body=finding("seven refs"),
               evidence=["item:X%d" % i for i in range(7)])
check("more than 6 refs is refused", std_refusal(why, "evidence") and "7" in why, why)
check("6 refs pass", try_open(subject="finding:RIMMANDRAKE_CITE_SIX_REFS_ON_FINDING", body=finding("six refs"),
                              evidence=["item:X%d" % i for i in range(6)]) is None)
why = try_open(subject="finding:RIMMANDRAKE_CITE_UNTYPED_REF_ON_FINDING", body=finding("untyped"),
               evidence=["see the log"])
check("an untyped ref is refused", std_refusal(why, "evidence"), why)
why = try_open(subject="finding:RIMMANDRAKE_CITE_LONG_REF_ON_FINDING", body=finding("long ref"),
               evidence=["path:" + "p" * 160])
check("a ref past 160 chars is refused", std_refusal(why, "evidence"), why)
why = try_open(subject="finding:RIMMANDRAKE_CITE_NESTED_REF_ON_FINDING", body=finding("nested ref"),
               evidence=[{"path": "x"}])
check("a nested (non-string) ref is refused", std_refusal(why, "evidence"), why)
why = try_open(subject="finding:RIMMANDRAKE_CITE_NOTHING_ON_A_FINDING", body=finding("no refs"), evidence=())
check("a finding with no evidence ref is refused", std_refusal(why, "evidence"), why)
# code_sha and results
why = refuses(M.append, rs, MOD, "BACKFILL", "finding.claimed_fixed", G, body={"text": "Fixed.", "test": "rc 0"},
              evidence=["item:X"], ts=ts(4))
check("a claimed_fixed with no code_sha is refused", std_refusal(why, "code_sha"), why)
why = refuses(M.append, rs, MOD, "BACKFILL", "test.run", "bar:" + BAR, body={"result": "GREEN", "command": "t.py",
                                                                           "bar": BAR},
              evidence=["test:t.py"], code_sha="abc123", ts=ts(4))
check("a result outside PASS/FAIL/UNMEASURED/UNRUN is refused", std_refusal(why, "result"), why)
why = refuses(M.append, rs, MOD, "BACKFILL", "live.run", "bar:" + BAR, body={"result": "PASS", "command": "proof.py",
                                                                           "bar": BAR},
              evidence=["run:J1"], ts=ts(4))
check("a PASS live run with no code_sha is refused", std_refusal(why, "code_sha"), why)
check("an UNRUN live run needs no code_sha, only its command",
      refuses(M.append, rs, MOD, "BACKFILL", "live.run", "bar:" + BAR,
              body={"result": "UNRUN", "command": "proof.py --scene wall", "bar": BAR}, evidence=["item:X"],
              ts=ts(4)) is None)
# subjects
why = try_open(subject="F_BLAST", body=finding("bare subject"))
check("a subject outside the classes (bar:/finding:/cause:/trap:/q: or a singleton) is refused",
      std_refusal(why, "subject"), why)
why = try_open(subject="finding:F_BLAST", body=finding("bad finding name"))
check("a finding: name that fails the project namecheck is refused", std_refusal(why, "subject"), why)
# most tickets have no prose file: their rimflow `file` event is the whole record, and their legacy name stays valid
os.makedirs(os.path.join(rs, "infrastructure", "state", "ledger", "events"), exist_ok=True)
with open(os.path.join(rs, "infrastructure", "state", "ledger", "events", "BENCH.jsonl"), "a", encoding="utf-8") as fh:
    fh.write(json.dumps({"event": "file", "id": "THIRST_BUILD_OWN_BOTTLES_DUBS", "title": "t"}) + "\n")
why = try_open(subject="finding:THIRST_BUILD_OWN_BOTTLES_DUBS", body=finding("a ledger-only ticket"))
check("a finding named for a ticket filed in the rimflow ledger (no prose file, legacy name) passes", why is None, why)
why = refuses(M.append, rs, MOD, "BACKFILL", "trap.noted", "trap:Not A Slug", body={"text": "t", "where": "w"},
              evidence=["item:X"], ts=ts(4))
check("a trap: subject that is not a kebab slug is refused", std_refusal(why, "subject"), why)
why = refuses(M.append, rs, MOD, "BACKFILL", "live.run", "bar:no_such_bar",
              body={"result": "UNRUN", "command": "proof.py"}, evidence=["item:X"], ts=ts(4))
check("a bar: subject naming no locked bar is refused", std_refusal(why, "subject"), why)
# duplicates and no-change
put(rs, MOD, "BACKFILL", "trap.noted", "trap:z-log-budget-charges-stackless-errors",
         body={"text": "Z_log_budget charges an error with no stack to the mod by design: a null texture error is not "
                       "evidence against the mod", "where": "proof_all.py#Z_log_budget"}, evidence=["item:X"], ts=ts(5))
why = refuses(M.append, rs, MOD, "BACKFILL", "trap.noted", "trap:log-budget-blames-stackless",
              body={"text": "Z_log_budget charges an error with no stack to the mod by design; a null texture error is "
                            "not evidence against the mod", "where": "proof_all.py"}, evidence=["item:Y"], ts=ts(6))
check("a new subject matching a live one is refused, naming the candidate", std_refusal(why, "subject") and
      "trap:z-log-budget-charges-stackless-errors" in why and "--new-subject" in why, why)
check("--new-subject '<why>' lets it through and records the why in the body",
      refuses(M.append, rs, MOD, "BACKFILL", "trap.noted", "trap:log-budget-blames-stackless",
              body={"text": "Z_log_budget charges an error with no stack to the mod by design; a null texture error is "
                            "not evidence against the mod", "where": "proof_all.py"}, evidence=["item:Y"], ts=ts(6),
              new_subject="this one is the L2 lane's copy of the budget") is None and
      any(e.get("body", {}).get("new_subject_why") for e in M.read(rs, MOD)
          if e["subject"] == "trap:log-budget-blames-stackless"))
why = refuses(M.append, rs, MOD, "BACKFILL", "note", "trap:z-log-budget-charges-stackless-errors",
              body={"text": "Z_log_budget charges an error with no stack to the mod by design: a null texture error "
                            "is not evidence against the mod.", "about": "trap:z-log-budget-charges-stackless-errors"},
              evidence=["item:Z"], ts=ts(7))
check("the same text again on the same subject is refused (restating)", std_refusal(why, "text") and "restat" in why,
      why)
put(rs, MOD, "BACKFILL", "test.run", "bar:" + BAR, body={"result": "PASS", "command": "t.py --all", "bar": BAR},
         evidence=["test:t.py"], code_sha="abc123", ts=ts(8))
why = refuses(M.append, rs, MOD, "BACKFILL", "test.run", "bar:" + BAR,
              body={"result": "PASS", "command": "t.py --all", "bar": BAR, "text": "again"}, evidence=["test:t.py"],
              code_sha="abc123", ts=ts(9))
check("a test.run identical in command, sha and result to the last is refused (no change)",
      std_refusal(why, "result") and "no change" in why, why)
check("the same test with a new result is a real change and passes",
      refuses(M.append, rs, MOD, "BACKFILL", "test.run", "bar:" + BAR,
              body={"result": "FAIL", "command": "t.py --all", "bar": BAR}, evidence=["test:t.py"], code_sha="abc123",
              ts=ts(10)) is None)
# lifecycle noise and closed kinds
why = refuses(M.append, rs, MOD, "BACKFILL", "lease.grant", "lease", body={"lease": "X", "token": 9},
              evidence=["item:X"], ts=ts(11))
check("a miner writing a lifecycle kind (lease.grant) is refused as lifecycle noise", std_refusal(why, "kind") and
      "lifecycle" in why, why)
why = refuses(M.append, rs, MOD, "BACKFILL", "reassign", "stage", body={"text": "to BENCH"}, evidence=["item:X"],
              ts=ts(11))
check("a rimflow lifecycle kind (reassign) is refused as lifecycle noise", std_refusal(why, "kind") and
      "lifecycle" in why, why)
why = refuses(M.append, rs, MOD, "BACKFILL", "finding.bogus", G, body={"text": "x"}, evidence=["item:X"], ts=ts(11))
check("an unknown kind is refused", std_refusal(why, "kind"), why)
why = refuses(M.append, rs, MOD, "HOLDER.H1", "finding.withdrawn", G, body={"text": "not a bug", "how_checked": "reading"},
              code_sha="abc123", token=1, ts=ts(11), now=ts(11))
check("a holder's withdrawal needs a test (how_checked), before any lease check", why is not None and
      "how_checked" in why, why)
why = refuses(M.append, rs, MOD, "BACKFILL", "finding.withdrawn", G, body={"text": "not a bug", "how_checked": "vibes"},
              code_sha="abc123", evidence=["item:X"], ts=ts(11))
check("how_checked outside test/repro/reading is refused", std_refusal(why, "how_checked"), why)
why = refuses(M.append, rs, MOD, "BACKFILL", "note", "stage", body={"text": "a note about nothing", "about": "q:nope"},
              evidence=["item:X"], ts=ts(11))
check("a note about a subject the ledger does not hold is refused", std_refusal(why, "about"), why)

# the CLI says it the standard's way, exit 2
env = dict(os.environ, RM_MODLEDGER_ROOT=rs)
p = subprocess.run([sys.executable, CLI, "append", "--mod", MOD, "--writer", "JUDGE.Z", "--run", "Z", "--kind",
                    "finding.open", "--subject", "finding:RIMMANDRAKE_FIND_CLI_FIXTURE_WITH_NO_FIX", "--text", "no fix",
                    "--body", json.dumps({"class": "problem", "bars": [BAR], "accept": "none, fixture"}),
                    "--evidence", "path:x"], capture_output=True, text=True, env=env)
check("CLI append refuses a finding with no fix in the standard's shape, exit 2",
      p.returncode == 2 and std_refusal(p.stdout, "proposed_fix"), (p.returncode, p.stdout[-300:], p.stderr[-300:]))

# ---- the lint re-runs the standard on new lines, and checks sha:/path: refs against the base ------------------------
rl = clone(rs)
git_repo(rl)
commit_all(rl, "base")
git(rl, "branch", "published")
landed = git(rl, "rev-parse", "HEAD").stdout.strip()
check("against its published form, a clean ledger lints clean", M.lint(rl, MOD, base="published")[0] == [],
      M.lint(rl, MOD, base="published")[0])
put(rl, MOD, "BACKFILL", "trap.noted", "trap:sha-ref-on-base", body={"text": "a landed sha", "where": "x"},
         evidence=["sha:" + landed[:10]], ts=ts(12))
check("a sha: ref that resolves on the base lints clean", M.lint(rl, MOD, base="published")[0] == [],
      M.lint(rl, MOD, base="published")[0])
put(rl, MOD, "BACKFILL", "trap.noted", "trap:theft-fix-first-build-rewritten",
    body={"text": "the theft fix's first build was rebased at landing", "where": "y"},
         evidence=["sha:101e561a6e06"], ts=ts(13))
check("a sha: ref not on the base is refused (the theft fix's rewritten sha)",
      "SHA_NOT_ON_BASE" in codes(M.lint(rl, MOD, base="published")[0]), M.lint(rl, MOD, base="published")[0])
M.delete(rl, MOD, [e["id"] for e in M.read(rl, MOD) if e["subject"] == "trap:theft-fix-first-build-rewritten"])
put(rl, MOD, "BACKFILL", "trap.noted", "trap:path-ref-missing", body={"text": "a path that is not there",
                                                                          "where": "z"},
         evidence=["path:src/nowhere.py#L3"], ts=ts(14))
check("a path: ref that does not exist is refused", "PATH_MISSING" in codes(M.lint(rl, MOD, base="published")[0]),
      M.lint(rl, MOD, base="published")[0])
M.delete(rl, MOD, [e["id"] for e in M.read(rl, MOD) if e["subject"] == "trap:path-ref-missing"])
handwrite(rl, "BACKFILL", dict(base_ev(writer="BACKFILL", subject="stage", key="k-big", id=M.derive_id("BACKFILL",
                                                                                                    "k-big")),
                               body={"text": "x" * 700, "about": "stage"}, evidence=["item:X"]))
lf = M.lint(rl, MOD, base="published")[0]
check("a hand-written oversize line (skipping append) is caught by the lint", "STANDARD" in codes(lf), lf)
check("old lines on the base are not re-judged (only the new line is)",
      [l for c, _p, l, _d in lf if c == "STANDARD"] and all(
          l == len(M._shard_bytes(rl, MOD, "BACKFILL").splitlines()) for c, _p, l, _d in lf if c == "STANDARD"), lf)

# ---- index and queries ----------------------------------------------------------------------------------------------
has_find = hasattr(M, "find")
rows = M.find(r, MOD, "comp ticks TickLong", cls="cause") if has_find else []
check("find --class cause returns the refuted cause with its status now", rows and rows[0]["subject"] == CT and
      rows[0]["status"] == "refuted", rows)
rows = M.find(r, MOD, "radius", his=True) if has_find else []
check("find --his returns his words verbatim with authority", rows and rows[0]["said"] == "Keep the radius at 4." and
      rows[0]["authority"], rows)
rows = M.find(r, MOD, None, cls="trap", path="T_CORD_GEOMETRY_OFFLINE") if has_find else []
check("find --class trap --path returns live traps whose where is under the path",
      [x["subject"] for x in rows] == ["trap:geometry-check-reads-seven-scenes"], rows)
check("find hides a withdrawn finding by default", has_find and not [
    x for x in M.find(r, MOD, "wrong build", cls="finding") if x["subject"] == FM])
check("find --all includes the withdrawn finding (reopen, never re-file)", has_find and [
    x for x in M.find(r, MOD, "wrong build", cls="finding", all_=True) if x["subject"] == FM and
    x["status"] == "withdrawn"])
check("find on an empty query and no filters returns nothing, not everything", has_find and M.find(r, MOD, "") == [])
check("find survives FTS5 syntax in the query", has_find and isinstance(M.find(r, MOD, 'AND "( * NEAR'), list))
ip = M.index_path(r, MOD) if has_find else ""
check("the index is a throwaway SQLite under /tmp, never the repo", ip.startswith("/tmp/") and os.path.exists(ip) and
      not ip.startswith(r), ip)
if has_find:
    os.remove(ip)
check("deleting the index loses nothing (rebuilt on the next query)", has_find and
      M.find(r, MOD, "comp ticks", cls="cause") and os.path.exists(ip))
put(r, MOD, "JUDGE.J12", "finding.open", "finding:RIMMANDRAKE_REBUILD_INDEX_WHEN_SHARDS_GROW",
         body=finding("an index built before this line must be rebuilt for it", fix="compare shard offsets on query"),
         evidence=["run:J12"], run="J12", ts=ts(24))
check("the index rebuilds when the shards' offsets change", has_find and M.find(r, MOD, "index built before this line",
                                                                                 cls="finding"))
op = M.open_findings(r, MOD, bar=BAR) if hasattr(M, "open_findings") else []
check("open --bar lists open and claimed-fixed findings on that bar with fix and accept",
      {x["subject"] for x in op} >= {FB} and all(x["status"] in ("open", "claimed_fixed") for x in op) and
      all("proposed_fix" in x and "accept" in x for x in op), op)
check("open --bar leaves out withdrawn findings", op and FM not in {x["subject"] for x in op}, op)
pk, _ = M.packet(r, MOD)
cur = [l for l in pk.strip().split("\n") if l.startswith("cursor: ")]
check("the packet's last line is its cursor", pk.strip().split("\n")[-1].startswith("cursor: "), pk[-300:])
put(r, MOD, "JUDGE.J13", "finding.verified", FB, body={"text": "verified by WALL_STOP PASS"}, code_sha="def456",
         run="J13", ts=ts(25))
ch = M.since(r, MOD, cur[0].split()[1]) if cur and hasattr(M, "since") else []
check("since <cursor> prints only what changed after it, by subject", [c["subject"] for c in ch] == [FB] and
      ch[0]["status"] == "verified", ch)
check("since with an unreadable cursor is refused, naming the forms", hasattr(M, "since") and
      refuses(M.since, r, MOD, "garbage") is not None)

# ---- packet: closed one line, notes never, stale causes --------------------------------------------------------------
pk, _ = M.packet(r, MOD)
check("a closed finding is one line: subject, status, sha", ("- %s verified def456" % FB) in pk, pk[-2500:])
put(r, MOD, "STEWARD", "note", "stage", body={"text": "NOTE_SHOULD_NOT_PRINT anywhere in the packet",
                                                   "about": "stage"}, ts=ts(26))
pk, _ = M.packet(r, MOD)
check("notes are never in the packet", "NOTE_SHOULD_NOT_PRINT" not in pk)
check("notes are searchable", has_find and M.find(r, MOD, "NOTE_SHOULD_NOT_PRINT"))
pk = refuses(M.packet, r, MOD, stale=lambda c: True) or M.packet(r, MOD, stale=lambda c: True)[0]
check("a refuted cause whose files changed since its sha shows as stale, not refuted",
      "## Causes stale" in pk and CT in pk.split("## Causes stale")[1].split("\n## ")[0], pk[:3000])
cv = os.path.join(M.views_dir(r, MOD), "closed_0.1.0.md")
check("the closed_<version> view lists what closed in that version",
      os.path.exists(cv) and FB in open(cv, encoding="utf-8").read())
check("the whole fixture ledger still lints clean", M.lint(r, MOD, None)[0] == [], M.lint(r, MOD, None)[0])

# ---- delete on sight (git) ------------------------------------------------------------------------------------------
r8 = clone(r)
git_repo(r8)
commit_all(r8, "base")
git(r8, "branch", "published")
check("against its published form, an unchanged ledger lints clean", M.lint(r8, MOD, base="published")[0] == [],
      M.lint(r8, MOD, base="published")[0])
# Delete on sight (his ruling 2026-11-15 ~10:16 PM PST, via the Conductor: "Delete on sight. I really don't think
# that's going to be abused to pass a judge. But we can monitor."): a whole-line deletion by any writer passes the lint;
# a line changed in place is still refused (a correction is delete + append).
dp = M.shard_path(r8, MOD, "STEWARD")
with open(dp, encoding="utf-8") as fh:
    lines = fh.readlines()
i6 = [i for i, l in enumerate(lines) if "radius 6" in l][0]
with open(dp, "w", encoding="utf-8") as fh:
    fh.writelines([l.replace("radius 6", "radius 5") if i == i6 else l for i, l in enumerate(lines)])
check("lint refuses a published line edited in place", "EDITED_IN_PLACE" in codes(M.lint(r8, MOD, base="published")[0]),
      M.lint(r8, MOD, base="published")[0])
e0 = json.loads(lines[i6])
with open(dp, "w", encoding="utf-8") as fh:
    fh.writelines([l.replace("radius 6", "radius 5").replace(e0["ts"], ts(40)) if i == i6 else l
                   for i, l in enumerate(lines)])
check("lint refuses an in-place edit that also moved its timestamp",
      "EDITED_IN_PLACE" in codes(M.lint(r8, MOD, base="published")[0]), M.lint(r8, MOD, base="published")[0])
with open(dp, "w", encoding="utf-8") as fh:
    fh.writelines(lines)
dead = [e for e in M.read(r8, MOD) if e["kind"] == "decision" and e["subject"] == "q:radius-decision" and
        "radius 6" in e["body"]["text"]][0]["id"]
gone = M.delete(r8, MOD, [dead])
check("delete removes the named entry (a superseded one here)", gone and gone[0]["id"] == dead, gone)
check("the reducer treats a supersedes of a deleted id as absent",
      M.reduce(M.read(r8, MOD))["decisions"]["q:radius-decision"]["text"] == "radius 4, per his answer")
check("a deletion lints clean against the published form", M.lint(r8, MOD, base="published")[0] == [],
      M.lint(r8, MOD, base="published")[0])
blast = [e for e in M.read(r8, MOD) if e["kind"] == "finding.open" and e["subject"] == FB][0]["id"]
os.environ["RM_MODLEDGER_WRITER"] = "HOLDER.L2"
try:
    gone = M.delete(r8, MOD, [blast])
finally:
    del os.environ["RM_MODLEDGER_WRITER"]
check("any writer may delete anyone's entry: a holder deletes a sealed judge's finding", gone and
      gone[0]["shard"] == "JUDGE.J1", gone)
check("a deletion from a sealed judge shard is not SEALED_CHANGED", "SEALED_CHANGED" not in
      codes(M.lint(r8, MOD, base="published")[0]), M.lint(r8, MOD, base="published")[0])
check("a deletion commit by any writer passes the lint (causes naming a deleted finding included)",
      M.lint(r8, MOD, base="published")[0] == [], M.lint(r8, MOD, base="published")[0])
grant_id = [e for e in M.read(r8, MOD) if e["kind"] == "lease.grant"][0]["id"]
why = refuses(M.delete, r8, MOD, [grant_id])
check("delete refuses the fencing bookkeeping (a lease.grant)", why and "lease.grant" in why, why)
why = refuses(M.delete, r8, MOD, ["DISPATCH:0000000000000000"])
check("delete of an id the ledger does not hold is refused", why and "no entry" in why, why)
commit_all(r8, "holder deletes a judge finding and a superseded decision")
dl = M.deletions(r8, since=None)
rows = {(x["shard"], x["subject"]): x for x in dl["deleted"]}
check("the monitor sees both deletions from git", ("JUDGE.J1", FB) in rows and ("STEWARD", "q:radius-decision") in rows,
      sorted(rows))
check("the monitor flags the judge finding (another writer's) for the digest", rows.get(("JUDGE.J1", FB), {}).get("flag"),
      rows.get(("JUDGE.J1", FB)))
check("the monitor does not flag a steward's own decision",
      not rows.get(("STEWARD", "q:radius-decision"), {}).get("flag"), rows.get(("STEWARD", "q:radius-decision")))
check("the monitor counts deletions per mod and per writer", dl["counts"].get(MOD, {}).get("JUDGE") == 1 and
      dl["counts"][MOD].get("STEWARD") == 1, dl["counts"])
ans = [e for e in M.read(r8, MOD) if e["kind"] == "question.answer"][0]["id"]
M.delete(r8, MOD, [ans])
dpp = M.shard_path(r8, MOD, "DISPATCH")
with open(dpp, encoding="utf-8") as fh:
    dl_lines = fh.readlines()
with open(dpp, "w", encoding="utf-8") as fh:
    fh.writelines(list(reversed(dl_lines)))         # every line moved, none deleted
commit_all(r8, "his answer deleted; dispatch lines reordered")
dl = M.deletions(r8, since=None)
check("the monitor flags a deleted OWNER answer for the digest",
      any(x["shard"] == "OWNER" and x["kind"] == "question.answer" and x["flag"] for x in dl["deleted"]), dl["deleted"])
check("a line moved within its commit is not a deletion", not any(x["shard"] == "DISPATCH" for x in dl["deleted"]),
      [x for x in dl["deleted"] if x["shard"] == "DISPATCH"])
with open(M.shard_path(r8, MOD, "JUDGE.J1"), "a", encoding="utf-8") as fh:
    fh.write(json.dumps(dict(json.loads(open(M.shard_path(r8, MOD, "DISPATCH"), encoding="utf-8").readline()),
                             writer="JUDGE.J1", run="J1", kind="note", subject="stage")) + "\n")
check("a line added to a sealed judge shard is still SEALED_CHANGED", "SEALED_CHANGED" in
      codes(M.lint(r8, MOD, base="published")[0]), M.lint(r8, MOD, base="published")[0])
r8b = fresh(); roots.append(r8b)
git_repo(r8b)
put(r8b, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0", ts=ts(0))
put(r8b, MOD, "OWNER", "bar.locked", "bar:" + BAR, body=LOCK, authority={"by_card": "Lock? -> yes"}, ts=ts(1))
put(r8b, MOD, "JUDGE.J1", "finding.open", FB, body=finding("open when deleted"), evidence=["run:J1"], run="J1",
         ts=ts(2))
commit_all(r8b, "an open finding")
M.delete(r8b, MOD, [e["id"] for e in M.read(r8b, MOD) if e["kind"] == "finding.open"])
commit_all(r8b, "the open finding deleted")
x = [d for d in M.deletions(r8b)["deleted"] if d["subject"] == FB]
check("the monitor marks a finding deleted while open", x and x[0]["was_open"] is True and x[0]["flag"], x)

# ---- packet budget ------------------------------------------------------------------------------------------------
r9 = fresh(); roots.append(r9)
put(r9, MOD, "DISPATCH", "version.open", "version", body={"version": "0.2.0"}, version="0.2.0", ts=ts(0))
put(r9, MOD, "OWNER", "bar.locked", "bar:" + BAR, body=LOCK, authority={"by_card": "Lock? -> yes"}, ts=ts(0, 30))
OLD = ["finding:RIMMANDRAKE_CLOSE_OLD_FINDING_" + letters(i) for i in range(60)]
for i in range(60):
    M.append(r9, MOD, "JUDGE.K%d" % i, "finding.open", OLD[i],
             body=finding("old closed finding %s about %s" % (letters(i), " ".join(letters(i + k) for k in range(30))),
                          fix="fix %s " % letters(i) + "x " * 40),
             evidence=["run:K%d" % i], run="K%d" % i, ts="2026-11-15T21:%02d:00Z" % i, views=False)
    M.append(r9, MOD, "JUDGE.V%d" % i, "finding.verified", OLD[i], body={"text": "verified"}, code_sha="abc%04d" % i,
             run="V%d" % i, ts="2026-11-15T21:%02d:30Z" % i, views=False)
put(r9, MOD, "JUDGE.N1", "finding.open", FSO, body=finding("the open one", fix="the precise open fix"),
         evidence=["run:N1"], run="N1", ts=ts(3), views=False)
put(r9, MOD, "OWNER", "question.answer", "q:keep", body={"said": "his kept answer"},
         authority={"by_card": "Keep? -> yes"}, ts=ts(4), views=False)
tok = M.grant(r9, MOD, lease="H1", ts=ts(5))
put(r9, MOD, "HOLDER.H1", "cause.refuted", "cause:the-refuted-cause",
         body={"text": "the refuted cause", "finding": FSO, "depends_on": ["Source/A.cs"]}, code_sha="abc123",
         token=tok, ts=ts(6), now=ts(6), views=False)
full, finfo = M.packet(r9, MOD, budget=100000)
SMALL = finfo["tokens"] - 300
small, sinfo = M.packet(r9, MOD, budget=SMALL)
check("an unbounded packet leaves out nothing but the full history", finfo["dropped"] == {}, finfo["dropped"])
check("closed findings are one line each, not their text", "old closed finding" not in full and
      ("- %s verified abc0059" % OLD[59]) in full, full[-800:])
check("a packet over budget drops old closed findings first", sinfo["dropped"].get("closed findings", 0) > 0 and
      sinfo["tokens"] <= SMALL, (sinfo["dropped"], sinfo["tokens"]))
check("the cut takes the OLDEST closed findings first", OLD[59] in small and OLD[0] not in small, small[-1500:])
check("the open finding, its fix, the refuted cause and his answer survive the cut",
      all(s in small for s in (FSO, "the precise open fix", "cause:the-refuted-cause", "his kept answer")),
      small[-1500:])
check("the packet ends by naming what it left out, then its cursor", "## Left out" in small and "closed findings" in
      small.split("## Left out")[1] and small.strip().split("\n")[-1].startswith("cursor: "), small[-600:])
LONG = "his long answer " + "word " * 100 + "THE_END"
put(r9, MOD, "OWNER", "question.answer", "q:long", body={"said": LONG}, authority={"owner_said": "long"},
         ts=ts(7), views=False)
lp, _ = M.packet(r9, MOD, budget=100000)
line = ([l for l in lp.split("\n") if l.startswith("- q:long")] or [""])[0]
check("a long said is clipped in the packet with a pointer to the command that prints it whole",
      line and "THE_END" not in line and "modledger.py show --mod %s q:long" % MOD in line, line[-200:])
check("the ledger keeps the said whole", any(e.get("subject") == "q:long" and "THE_END" in (e["body"].get("said") or "")
                                             for e in M.read(r9, MOD)))
tiny, tinfo = M.packet(r9, MOD, budget=50)
check("a packet whose must-keep part alone passes the budget says OVER BUDGET",
      tinfo["over_budget"] and "OVER BUDGET" in tiny, tinfo)

# ---- the CLI the way it is used ------------------------------------------------------------------------------------
env = dict(os.environ, RM_MODLEDGER_ROOT=r9)
p = subprocess.run([sys.executable, CLI, "packet", "--mod", MOD], capture_output=True, text=True, env=env)
check("CLI packet prints from the ledger", p.returncode == 0 and FSO in p.stdout, p.stderr[-400:])
p = subprocess.run([sys.executable, CLI, "views", "--mod", MOD], capture_output=True, text=True, env=env)
p = subprocess.run([sys.executable, CLI, "lint", "--mod", MOD, "--base", ""], capture_output=True, text=True, env=env)
check("CLI lint is clean after views", p.returncode == 0, p.stdout[-400:] + p.stderr[-400:])
p = subprocess.run([sys.executable, CLI, "show", "--mod", MOD, FSO], capture_output=True, text=True, env=env)
check("CLI show prints one subject's events", p.returncode == 0 and "finding.open" in p.stdout, p.stdout[-300:])
p = subprocess.run([sys.executable, CLI, "find", "--mod", MOD, "--class", "cause", "refuted cause"],
                   capture_output=True, text=True, env=env)
check("CLI find prints the cause with its status", p.returncode == 0 and "cause:the-refuted-cause" in p.stdout and
      "refuted" in p.stdout, (p.returncode, p.stdout[-300:], p.stderr[-300:]))
p = subprocess.run([sys.executable, CLI, "find", "--mod", "all", "--his", "kept"], capture_output=True, text=True,
                   env=env)
check("CLI find --mod all searches every mod ledger", p.returncode == 0 and "his kept answer" in p.stdout,
      (p.returncode, p.stdout[-300:], p.stderr[-300:]))
p = subprocess.run([sys.executable, CLI, "open", "--mod", MOD, "--bar", BAR], capture_output=True, text=True, env=env)
check("CLI open --bar prints the open finding with its fix", p.returncode == 0 and FSO in p.stdout and
      "the precise open fix" in p.stdout, (p.returncode, p.stdout[-300:], p.stderr[-300:]))
p = subprocess.run([sys.executable, CLI, "since", "--mod", MOD, "2026-11-15T20:06:30Z"], capture_output=True,
                   text=True, env=env)
check("CLI since <time> prints the changes after it", p.returncode == 0 and "q:long" in p.stdout and
      "cause:the-refuted-cause" not in p.stdout, (p.returncode, p.stdout[-300:], p.stderr[-300:]))

for d in roots:
    shutil.rmtree(d, ignore_errors=True)
print("selftest_modledger: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
