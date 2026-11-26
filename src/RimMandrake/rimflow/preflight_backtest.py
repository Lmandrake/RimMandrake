#!/usr/bin/env python3
"""The ticket preflight's look back (design/specs/2026-11-12-ticket-preflight-before-any-token.md section 8; item
RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS). Read-only: it changes no ticket and writes one table.

    python3 src/RimMandrake/rimflow/preflight_backtest.py [--out PATH] [--days 60] [--timing-sample 40]

Four corpora, each ticket rebuilt as it stood at the moment the spec names:
  open           every open ticket, today's text (volume and timing; "today")
  closed_60d     closed, dropped or superseded in the last N days, text at the last mainline commit before the first
                 claim/start ("as it was"); never picked up -> the `unworked` row, at the commit before the end
  measured_week  the Relentless store's setup-class ends (the spec's STRICT end types), text at the generation's start
  labelled       the ledger's labelled terminal events (duplicate, already done, false premise, not on the list, no
                 such ...), mined by the spec's own mine_ledger.py rules, at pickup (else at the end)
Paths, item states and shas are "as it was" (git at that commit, ledger events before that moment); defs and tiers are
today's (a stand-in: one def dump exists). A ruling made after pickup is not used against a ticket: E12 and C4 (owner,
by card 2026-11-13) and the `## refs` grammar itself (E11, P0) count only for pickups from 2026-11-13 on.
The planted tickets prove the instrument can see: one per group, run through the same functions the doors call.
The audit (spec section 8 "False refusal") is a person's: `audited` 0 and `false` null until the Conductor reads
`audit_sample`. Output: infrastructure/state/evidence/preflight_backtest/<date>.json.
"""
import argparse
import bisect
import calendar
import collections
import glob
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model  # noqa: E402
import ticket_preflight as TP  # noqa: E402

REPO = TP.REPO
STORE = "/home/mandrake/rm/runs/store"
LABELS = "/mnt/d/ClaudeWork/rimmandrake/conductor/ticket_preflight_20261112/mine_ledger.json"
RULED = "2026-11-13"                      # E12, C4 and the refs grammar: the owner's card, 2026-11-13
RULED_CHECKS = ("E12", "C4", "E11", "P0")
REFUSING = ("B1", "B4", "B6", "B10", "B11", "C1", "C2", "C4", "E11", "E12")   # declared facts that may refuse (3.1)
STRICT = ("unmeasured", "proof_unrunnable", "rebind_proposed", "game_env_route", "game_env_fix", "game_unmeasured",
          "game_refused", "game_proof_unmeasured", "bad_candidate")
GATE_ENDS = ("game_refused", "proof_unrunnable", "rebind_proposed")          # a Relentless gate already stopped these
END_GROUPS = {"unmeasured": "EF", "proof_unrunnable": "F", "rebind_proposed": "F", "bad_candidate": "EF",
              "game_env_route": "CD", "game_env_fix": "CD", "game_unmeasured": "CD", "game_refused": "CDF",
              "game_proof_unmeasured": "CF"}
LABEL_GROUPS = {"duplicate": "A", "already_done": "A", "ref_not_real": "B", "mod_not_on_list": "C",
                "premise_false": "BE", "criteria_unattainable": "EF", "env_not_ready": "D", "wrong_seat_or_authority": "I"}
WEEK = ("2026-10-31", "2026-11-08")


def git(*a, **kw):
    kw.setdefault("timeout", 300)
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, **kw)


def epoch(ts):
    try:
        return calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


class History(object):
    """Mainline commits by time; file text and the tracked tree at any of them, each read once."""

    def __init__(self, since_days):
        out = git("log", "--first-parent", "--format=%H %ct", "--since=%d.days" % (since_days + 20), "origin/main").stdout
        rows = sorted((int(c), h) for h, c in (l.split() for l in out.splitlines()))
        self.times, self.shas = [r[0] for r in rows], [r[1] for r in rows]
        self.trees = {}

    def at(self, t):
        i = bisect.bisect_left(self.times, t) - 1          # the last commit strictly before t
        return self.shas[i] if i >= 0 else None

    def texts(self, pairs):
        """[(sha, path)] -> {(sha, path): text or ""}, one git cat-file process."""
        if not pairs:
            return {}
        req = "".join("%s:%s\n" % p for p in pairs).encode()
        p = subprocess.run(["git", "-C", REPO, "cat-file", "--batch"], input=req, capture_output=True, timeout=600)
        out, buf, i = {}, p.stdout, 0
        for pair in pairs:
            nl = buf.index(b"\n", i)
            head = buf[i:nl].decode()
            i = nl + 1
            if head.endswith("missing"):
                out[pair] = ""
                continue
            size = int(head.split()[-1])
            out[pair] = buf[i:i + size].decode("utf-8", "replace")
            i += size + 1
        return out

    def paths(self, sha):
        if sha not in self.trees:            # bound memory: ~60k paths a tree; cases are evaluated grouped by commit
            if len(self.trees) >= 2:
                self.trees.clear()
                TP._MEMO.clear()
            self.trees[sha] = git("ls-tree", "-r", "--name-only", sha).stdout.splitlines()
        return self.trees[sha]


def items_as_of(events, t):
    """{id: {"state", "successor"}} from the events before t: the B10 view of the ledger then."""
    st = {}
    for e in events:
        et = e.get("_t")
        if et is None or et >= t:
            continue
        iid = e.get("id")
        if not iid:
            continue
        v = e.get("event")
        if v == "file":
            st.setdefault(iid, {"state": "proposed", "successor": None})
        elif v in ("close", "drop", "supersede") and iid in st:
            st[iid] = {"state": {"close": "done", "drop": "dropped", "supersede": "superseded"}[v],
                       "successor": e.get("by") or e.get("successor")}
    return st


def load_events(evs):
    for e in evs:
        e["_t"] = epoch(e.get("ts") or "")
    evs.sort(key=lambda e: e["_t"] or 0)
    by = collections.defaultdict(list)
    for e in evs:
        if e.get("id"):
            by[e["id"]].append(e)
    return evs, by


def first(es, verbs):
    return next((e for e in es if e.get("event") in verbs and e.get("_t")), None)


def item_paths(iid):
    return ("infrastructure/state/items/%s.md" % iid, "infrastructure/state/items/closed/%s.md" % iid,
            "infrastructure/state/live_proofs/%s.txt" % iid)


def evaluate(cases, hist, events, shared, items_today, w):
    """cases: [{"item", "corpus", "t" (epoch) or None for today, ...}] -> each case gains "checks", "as_of"."""
    need = []
    for c in cases:
        if c["t"] is None:
            continue
        c["sha"] = hist.at(c["t"])
        if c["sha"]:
            need += [(c["sha"], p) for p in item_paths(c["item"])]
    got = hist.texts(sorted(set(need)))
    snap_cache = {}
    for c in sorted(cases, key=lambda c: (c.get("sha") or "", c["item"])):
        it = w.items.get(c["item"])
        kind, needs = (it.kind if it else None) or "task", (it.needs if it else None) or "offline"
        if c["t"] is None:
            p = item_paths(c["item"])
            text = TP._read(os.path.join(REPO, p[0])) or TP._read(os.path.join(REPO, p[1]))
            proof = TP._read(os.path.join(REPO, p[2]))
            kw = dict(paths=shared["paths"], items=items_today, as_of="today")
        elif not c.get("sha"):
            c["checks"], c["as_of"] = [], "no commit before that moment in the window"
            continue
        else:
            p = item_paths(c["item"])
            text = got.get((c["sha"], p[0])) or got.get((c["sha"], p[1])) or ""
            proof = got.get((c["sha"], p[2])) or ""
            day = time.strftime("%Y-%m-%d", time.gmtime(c["t"]))
            if day not in snap_cache:                 # B10's ledger view, as of that day's start (bounded cost)
                snap_cache[day] = items_as_of(events, calendar.timegm(time.strptime(day, "%Y-%m-%d")) + 86400)
            kw = dict(paths=hist.paths(c["sha"]), items=snap_cache[day], head=c["sha"], as_of="as it was")
        as_of = kw.pop("as_of")
        rep = TP.run_text(text, proof, item_id=c["item"], trigger="backtest", kind=kind, needs=needs, inline=True,
                          record=False, defs=shared["defs"], src=shared["src"], tiers=shared["tiers"], **kw)
        c["as_of"], c["has_refs"], c["checks"] = as_of, bool(re.search(r"^##\s*refs\s*$", text, re.M | re.I)), rep["checks"]
        c["ms"] = rep["total_ms"]
        c["day"] = time.strftime("%Y-%m-%d", time.gmtime(c["t"])) if c["t"] else time.strftime("%Y-%m-%d")
        c["text_found"] = bool(text)


def would_refuse(c):
    """The check ids that would have refused this case at pickup: declared, FAIL, a refusing check, and not a ruling
    made after the pickup."""
    out = set()
    for k in c.get("checks", ()):
        if k["status"] != "FAIL" or k.get("origin", "declared") != "declared" or k["id"] not in REFUSING:
            continue
        if k["id"] in RULED_CHECKS and c.get("day", "9999") < RULED:
            continue
        out.add(k["id"])
    return out


def store_cases():
    """Corpus 3: (item, gen) of the measured week whose generation ended in a STRICT end, at the generation's start,
    with the generation's spend (work + check) from spend-*.json, as mine_store.py mapped it."""
    if not os.path.isdir(os.path.join(STORE, "items")):
        return None, "store not found at %s" % STORE
    spend = {}
    for f in glob.glob(STORE + "/spend-*.json"):
        try:
            spend.update(json.load(open(f)).get("runs") or {})
        except ValueError:
            continue
    h2i = {}
    for line in open(STORE + "/journal.jsonl", errors="replace"):
        try:
            j = json.loads(line)
        except ValueError:
            continue
        for a in j.get("acts") or []:
            m = re.search(r"-(?:work|check)-([0-9a-f]{10})-g(\d+)", a.get("unit") or "")
            if m and a.get("item"):
                h2i[m.group(1)] = a["item"]
    gen_spend = collections.Counter()
    for u, t in spend.items():
        m = re.search(r"-(work|check)-([0-9a-f]{10})-g(\d+)", u)
        if m and m.group(2) in h2i:
            gen_spend[(h2i[m.group(2)], int(m.group(3)))] += t
    cases, seen = [], set()
    for d in sorted(glob.glob(STORE + "/items/*/attempts.jsonl")):
        it = os.path.basename(os.path.dirname(d))
        starts, ends = {}, []
        for line in open(d, errors="replace"):
            try:
                a = json.loads(line)
            except ValueError:
                continue
            g = a.get("gen")
            if g is None:
                continue
            if a.get("at") and (g not in starts or a["at"] < starts[g]):
                starts[g] = a["at"]
            if a.get("end") in STRICT:
                ends.append((g, a["end"], a.get("at") or ""))
        for g, end, at in ends:
            if it in seen or not (WEEK[0] <= at[:10] < WEEK[1]):
                continue
            seen.add(it)
            cases.append({"item": it, "corpus": "measured_week", "t": epoch(starts.get(g) or at), "gen": g, "end": end,
                          "tokens": gen_spend.get((it, int(g)), 0)})
    return cases, None


def label_cases(by, cutoff_t):
    try:
        rows = json.load(open(LABELS))["rows"]
    except (OSError, ValueError, KeyError) as e:
        return None, "labelled lists unreadable (%s)" % e
    cases, seen = [], set()
    for label, rs in sorted(rows.items()):
        for r in rs:
            iid = r[0]
            if (iid, label) in seen:
                continue
            seen.add((iid, label))
            es = by.get(iid, [])
            pick = first(es, ("claim", "start"))
            end = first(es, ("close", "drop", "supersede"))
            t = pick["_t"] if pick else (end["_t"] if end else None)
            if t is None:
                continue
            cases.append({"item": iid, "corpus": "labelled", "t": t, "label": label, "worked": bool(pick)})
    return cases, None


def closed_cases(by, cutoff_t):
    cases = []
    for iid, es in by.items():
        end = next((e for e in reversed(es) if e.get("event") in ("close", "drop", "supersede") and e.get("_t")), None)
        if not end or end["_t"] < cutoff_t:
            continue
        pick = first(es, ("claim", "start"))
        cases.append({"item": iid, "corpus": "closed_60d", "t": pick["_t"] if pick else end["_t"], "worked": bool(pick),
                      "ended": end["event"]})
    return cases


# --- the planted tickets: one known-bad per group, through the functions the doors call --------------------------
def planted(shared):
    """One known-bad ticket per group, each through the function its door calls, and beside it a good twin that must
    pass: a check that fires on everything would otherwise read as one that sees."""
    sys.path.insert(0, os.path.dirname(HERE))       # by package: the index loaders put Utils/ first, and it has a cli.py
    from rimflow import cli
    import detached_helper as DH
    out = []

    def add(group, cid, what, bad, good):
        """bad / good: (fired, evidence) of the planted ticket and of its good twin."""
        out.append({"group": group, "check": cid, "what": what, "caught": bool(bad[0]), "evidence": str(bad[1]),
                    "good_passes": not good[0], "good_evidence": str(good[1])})

    def tp(text, cid, proof="", **kw):
        r = TP.run_text(text, proof, item_id="PLANTED", inline=True, record=False, defs=shared["defs"], src=shared["src"],
                        tiers=shared["tiers"], paths=shared["paths"], **kw)
        hit = [c for c in r["checks"] if c["id"] == cid and c["status"] == "FAIL"]
        return bool(hit), (hit[0]["evidence"] if hit else [c["id"] + " " + c["status"] for c in r["checks"]])

    def mint(name):
        p = model.mint_problems(name, set())
        return bool(p), p

    add("A", "A1", "a name outside the PROJECT_VERB_INTENTION_TWIST grammar", mint("BADNAME_X"),
        mint("RIMMANDRAKE_PLANT_GOOD_NAME_FOR_THE_BACKTEST"))
    add("B", "B1", "a declared file that is not tracked", tp("## refs\nfile: src/RimMandrake/no_such_file_planted.py\n", "B1"),
        tp("## refs\nfile: src/RimMandrake/rimflow/cli.py\n", "B1"))
    good_def = next(iter(shared["defs"]["defs"]))[1] if isinstance(shared["defs"], dict) else "Steel"
    add("B", "B4", "a declared def known nowhere", tp("## refs\ndef: RM_NoSuchDefPlantedForBacktest\n", "B4"),
        tp("## refs\ndef: %s\n" % good_def, "B4"))
    add("C", "C1", "a tier modset_builder does not know", tp("## refs\ntier: no_such_tier_planted\n", "C1"),
        tp("## refs\ntier: %s\n" % shared["good_tier"], "C1"))
    add("C", "C4", "a Full Mod ask with no full-why: line", tp("## refs\ntier: full\nfile: src/RimMandrake/rimflow/cli.py\n", "C4"),
        tp("## refs\ntier: full\nfull-why: performance: a cost that only shows at full scale\n", "C4"))
    add("E", "E11", "a typo'd refs key that would silently switch a check off",
        tp("## refs\nfiel: src/RimMandrake/rimflow/cli.py\n", "E11"), tp("## refs\nfile: src/RimMandrake/rimflow/cli.py\n", "E11"))
    add("E", "E12", "a build ticket with no declared refs", tp("## spec\nbuild it\n", "E12", kind="build"),
        tp("## refs\nnone: names nothing checkable\n", "E12", kind="build"))

    def thin(iid):
        g = model._missing(type("It", (), {"id": iid})())
        return bool(g), g
    add("E", "E1", "a ticket with no spec, verify or criteria (the existing thin-item gate)", thin("RIMMANDRAKE_PLANTED_THIN"),
        thin("RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS"))
    tmp = tempfile.mkdtemp(prefix="pf_planted_")
    os.makedirs(os.path.join(tmp, "infrastructure", "state", "live_proofs"))
    os.makedirs(os.path.join(tmp, "infrastructure", "state", "items"))
    os.makedirs(os.path.join(tmp, "src"))
    open(os.path.join(tmp, "src", "prove.py"), "w").write("")

    def lint(iid, line):
        open(os.path.join(tmp, "infrastructure", "state", "live_proofs", iid + ".txt"), "w").write(line + "\n")
        open(os.path.join(tmp, "infrastructure", "state", "items", iid + ".md"), "w").write("## criteria\n- A1: it works\n")
        try:
            bad = cli.prooflint(iid, None, root=tmp)
            return bool(bad), bad
        except Exception as e:              # noqa: BLE001  an instrument that cannot run is not a catch
            return False, "prooflint did not run: %s: %s" % (type(e).__name__, e)
    add("F", "F3", "a live-proof line the lane refuses ($ substitution)",
        lint("RIMMANDRAKE_PLANTED_BAD_PROOF_LINE", "live-proof A1: python3 src/prove.py $(echo --clause) A1"),
        lint("RIMMANDRAKE_PLANTED_GOOD_PROOF_LINE", "live-proof A1: python3 src/prove.py --clause A1"))

    def blocked(block):
        evs = [{"seat": "BENCH", "event": "file", "id": i, "for": "BENCH", "title": "x", "kind": "task",
                "ts": "2026-11-15T00:00:0%dZ" % n} for n, i in enumerate(("RIMMANDRAKE_PLANTED_BLOCKER_FOR_G",
                                                                          "RIMMANDRAKE_PLANTED_BLOCKED_FOR_G"))]
        if block:
            evs.append({"seat": "BENCH", "event": "block", "id": "RIMMANDRAKE_PLANTED_BLOCKED_FOR_G", "kind": "item",
                        "on": "RIMMANDRAKE_PLANTED_BLOCKER_FOR_G", "reason": "planted", "ts": "2026-11-15T00:00:05Z"})
        try:
            b = model.replay(evs).items["RIMMANDRAKE_PLANTED_BLOCKED_FOR_G"].blocked
            return bool(b), "blocked: %s" % b
        except Exception as e:              # noqa: BLE001
            return False, "replay failed: %s" % e
    add("G", "G1", "a ticket picked up while blocked on an open item", blocked(True), blocked(False))

    def no_unit(*a, **kw):                  # a planted launch must never reach a clone or a unit
        raise RuntimeError("planted launch reached the runner")

    def launch(seat, mdl):
        try:
            rc, text = DH.launch(seat, "RIMMANDRAKE_PLANTED_LAUNCH", "planted brief", mdl, 600, 1, runner=no_unit,
                                 known={"RIMMANDRAKE_PLANTED_LAUNCH"}, events_dir=tempfile.mkdtemp(prefix="pf_planted_ev_"))
        except Exception as e:              # noqa: BLE001  the good twin runs on into origin_check, which the runner stops
            rc, text = None, "launch went past the seat and model gates (%s)" % e
        return rc == 2 and "is not one of" in text, text
    add("H", "H4", "a helper launched on a banned model (haiku)", launch("BENCH", "haiku"), launch("BENCH", "opus"))
    add("I", "I1", "a helper launched for the retired FOUNDRY seat", launch("FOUNDRY", "opus"), launch("BENCH", "opus"))
    return out


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else None


def door_timing(sample_ids, n, w):
    """Each door's preflight on real open tickets as the door runs it: a forked child with its deadline, indexes
    loaded cold each run (a door never shares a warm cache), kind, needs and items handed over from the world the
    door already replayed (as cli does), the existing gates excluded (they are the door's own)."""
    out = {}
    for door in ("file", "claim", "start", "helper_launch"):
        ms = []
        for iid in sample_ids[:n]:
            it = w.items.get(iid)
            s = TP.Shadow(door, iid, "BENCH", runs_path=os.devnull)
            kw = dict(kind=(it.kind if it else None) or "task", needs=(it.needs if it else None) or "offline",
                      items=TP.items_of(w))
            s.run(root=REPO, **kw) if door == "helper_launch" else s.run(**kw)
            ms.append(s.ms)
        out[door] = {"n": len(ms), "p50": round(statistics.median(ms), 1), "p95": round(pct(ms, 0.95), 1),
                     "max": round(max(ms), 1), "source": "shadow sample over %d open tickets, %s" % (len(ms), time.strftime("%Y-%m-%d"))}
    live = collections.defaultdict(list)
    try:
        for line in open(TP.DEFAULT_RUNS):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("door"):
                live[r["door"]].append(r.get("total_ms") or 0)
    except OSError:
        pass
    for d, ms in live.items():
        out["live_" + d] = {"n": len(ms), "p50": round(statistics.median(ms), 1), "p95": round(pct(ms, 0.95), 1),
                            "max": round(max(ms), 1), "source": "real door runs in %s" % TP.DEFAULT_RUNS}
    return out


OWNER_RULED = {"E12": "owner, by card 2026-11-13: refuses at pickup", "C4": "owner, by card 2026-11-13: refuses at pickup"}


def proposals(rows):
    """Criterion A3: each refusing check with its row, and what clears it for ticket 4 (spec 8: 30 audited, <= 1 false;
    E12 and C4 are the owner's and need no audit, spec 7 row 4)."""
    out = []
    for r in rows:
        if not r["refusing"]:
            continue
        worked = r["fires"].get("closed_60d", 0) + r["fires"].get("measured_week", 0)
        if r["id"] in OWNER_RULED:
            status = "enforce in ticket 4 (%s); these numbers say how many it will stop" % OWNER_RULED[r["id"]]
        elif r["audited"] >= 30 and (r["false"] or 0) <= 1:
            status = "cleared: may refuse in ticket 4"
        else:
            status = "stays WARN: %d audited of the 30 needed%s" % (r["audited"], "; it fired on no past ticket, so there is "
                                                                   "nothing to audit yet: the shadow doors collect" if not r["fires_total"] else "")
        out.append({"id": r["id"], "fires": r["fires"], "fires_on_worked": worked, "audited": r["audited"],
                    "false": r["false"], "status": status})
    return out


VERDICTS = ("fact_true", "fact_false")     # was the check's named fact true at pickup? fact_false = a false refusal


def apply_audit(table, audit):
    """Criterion A2: fold a reader's audit of `audit_sample` into the table. Per check named, audited = the sampled rows
    read and false = those whose named fact was false at pickup (re-applying replaces, never adds); a check the audit does
    not name keeps audited 0 and false null (unread). A3 is recomputed by proposals(). An audit row naming an item not
    in that check's sample, a verdict outside VERDICTS, a row with no reason, a sample read twice or an audit naming no
    reader raises ValueError, and nothing is changed. -> a new table."""
    import copy
    if not str(audit.get("reader") or "").strip():
        raise ValueError("an audit names its reader")
    sample = {c: {r.get("item") for r in rows} for c, rows in (table.get("audit_sample") or {}).items()}
    read = {}
    for c, rows in (audit.get("checks") or {}).items():
        seen = set()
        for r in rows:
            if r.get("item") not in sample.get(c, set()):
                raise ValueError("%s: %r is not in that check's audit_sample" % (c, r.get("item")))
            if r.get("item") in seen:
                raise ValueError("%s: %r is read twice" % (c, r.get("item")))
            if r.get("verdict") not in VERDICTS:
                raise ValueError("%s %s: verdict must be one of %s, got %r" % (c, r.get("item"), VERDICTS, r.get("verdict")))
            if not str(r.get("why") or "").strip():
                raise ValueError("%s %s: a verdict says why" % (c, r.get("item")))
            seen.add(r["item"])
        read[c] = rows
    out = copy.deepcopy(table)
    for r in out["checks"]:
        if r["id"] in read:
            r["audited"] = len(read[r["id"]])
            r["false"] = sum(1 for x in read[r["id"]] if x["verdict"] == "fact_false")
    out["proposed_for_ticket_4"] = proposals(out["checks"])
    out["audit"] = {"reader": audit["reader"], "at": audit.get("at"), "read": {c: len(v) for c, v in read.items()},
                    "file": audit.get("file")}
    return out


def answer(out, cases):
    """The one paragraph spec section 8 owes the owner, from the table's own numbers."""
    co, jb = out["corpora"], out["joint_false_block"]
    past = co["closed_60d"]["n"] + co["measured_week"]["n"] + co["labelled"]["n"]
    refs = co["closed_60d"]["with_refs_block"] + co["measured_week"]["with_refs_block"] + co["labelled"]["with_refs_block"]
    found = co["closed_60d"]["text_found"] + co["measured_week"]["text_found"] + co["labelled"]["text_found"]
    by = collections.Counter(i for c in cases if c["corpus"] != "open" and (c["corpus"] == "measured_week" or c.get("worked"))
                             for i in would_refuse(c))
    tok = sum(r["incremental_tokens_upper_bound"] for r in out["checks"])
    ended = collections.Counter(c.get("ended") for c in cases if c["corpus"] == "closed_60d" and c.get("worked") and would_refuse(c))
    tm = out["timing"]
    doors = [d for d in ("file", "claim", "start", "helper_launch") if d in tm]
    return ("Over %d past tickets (%d closed or dropped in %d days, %d from the measured Relentless week, %d from the "
            "labelled lists), each read as it stood at pickup, the preflight as built would have stopped %d worked tickets "
            "before any token (%s), worth at most %.1fM tokens; all were then worked to an end (%s). E12's fact (no "
            "declared line) is read off the ticket and cannot be false, so a person's audit (audit_sample) will find them "
            "true refusals, yet each is work that went fine without a refs block: that is the starving-gate cost to weigh, "
            "and the joint false-block share is bounded above by %.1f%%. "
            "It catches almost nothing in the past because it reads only declared `## refs` lines and almost no past "
            "ticket had any: %d of the %d with prose (%d had no prose file at all). The %.0fM-token measured week of "
            "setup-class ends shows %d fires of a refusing check. So what it would catch that today's gates do not is not "
            "in the history: it is the declared facts the refs rule makes tickets write from 2026-11-13 on, plus E12 itself, "
            "which as ruled would stop %d of %d open tickets today. The shadow doors (file, claim, start, helper launch, "
            "live since this build) are the measurement that counts; the planted tickets show the instrument sees "
            "(%d of %d caught, every good twin passed: %s). It is fast: at the doors, p95 %s ms."
            % (past, co["closed_60d"]["n"], 60, co["measured_week"]["n"], co["labelled"]["n"], jb["would_block"],
               ", ".join("%s %d" % kv for kv in sorted(by.items())) or "none", tok / 1e6,
               ", ".join("%s %d" % kv for kv in sorted(ended.items())) or "none",
               100 * (jb["would_block_share"] or 0), refs, found, past - found, co["measured_week"].get("tokens", 0) / 1e6,
               co["measured_week"]["would_refuse"], co["open"]["would_refuse"], co["open"]["n"],
               sum(p["caught"] for p in out["planted"]), len(out["planted"]),
               all(p["good_passes"] for p in out["planted"]),
               ", ".join("%s %.0f" % (d, tm[d]["p95"]) for d in doors)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out")
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--timing-sample", type=int, default=40)
    ap.add_argument("--apply-audit", metavar="AUDIT_JSON", help="fold a reader's audit of audit_sample into --table "
                    "(criterion A2), recompute A3, and stop; the backtest itself is not rerun")
    ap.add_argument("--table", help="the backtest table --apply-audit rewrites in place")
    a = ap.parse_args()
    if a.apply_audit:
        if not a.table:
            ap.error("--apply-audit needs --table")
        try:
            with open(a.table, encoding="utf-8") as f:
                tbl = json.load(f)
            with open(a.apply_audit, encoding="utf-8") as f:
                aud = json.load(f)
            aud.setdefault("file", os.path.relpath(a.apply_audit, REPO) if os.path.isabs(a.apply_audit) else a.apply_audit)
            new = apply_audit(tbl, aud)
        except (OSError, ValueError) as e:
            print("AUDIT REFUSED, table unchanged: %s" % e, file=sys.stderr)
            return 2
        tmp = a.table + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(new, f, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, a.table)
        for r in new["checks"]:
            if r["id"] in new["audit"]["read"]:
                print("%s audited %d, false %d" % (r["id"], r["audited"], r["false"]))
        return 0
    t0 = time.monotonic()
    raw = model.read()
    w = model.replay(raw)
    events, by = load_events(raw)
    items_today = {k: {"state": v.state, "successor": v.superseded_by} for k, v in w.items.items()}
    shared = {}
    for name, loader in (("paths", TP._git_paths), ("defs", TP._cached_defs), ("src", TP._real_src), ("tiers", TP._real_tiers)):
        try:
            shared[name] = loader()
        except Exception as e:                  # noqa: BLE001  each case then reads UNMEASURED with the reason
            shared[name] = TP._raiser(e)
    try:                                        # a real tier for the C1 good twin (there is no "small": the fix ticket)
        shared["good_tier"] = next(t for t in ("bench", "acc_green_min") if shared["tiers"].get(t) is not None)
    except Exception:                           # noqa: BLE001
        shared["good_tier"] = "bench"
    hist = History(a.days)
    cutoff = time.time() - a.days * 86400
    corpora, notes = {}, []
    cases = [{"item": i.id, "corpus": "open", "t": None} for i in w.items.values() if i.open]
    cases += closed_cases(by, cutoff)
    sc, why = store_cases()
    if why:
        notes.append(why)
    cases += sc or []
    lc, why = label_cases(by, cutoff)
    if why:
        notes.append(why)
    cases += lc or []
    evaluate(cases, hist, events, shared, items_today, w)
    for name in ("open", "closed_60d", "measured_week", "labelled"):
        cs = [c for c in cases if c["corpus"] == name]
        corpora[name] = {"n": len(cs), "with_refs_block": sum(1 for c in cs if c.get("has_refs")),
                         "text_found": sum(1 for c in cs if c.get("text_found")),
                         "as_of": sorted({c.get("as_of") for c in cs if c.get("as_of")}),
                         "would_refuse": sum(1 for c in cs if would_refuse(c))}
    corpora["closed_60d"]["unworked"] = sum(1 for c in cases if c["corpus"] == "closed_60d" and not c.get("worked"))
    corpora["measured_week"]["tokens"] = sum(c.get("tokens", 0) for c in cases if c["corpus"] == "measured_week")

    ids = sorted({k["id"] for c in cases for k in c.get("checks", ())} | set(REFUSING))
    rows, sample = [], {}
    for cid in ids:
        fires = collections.Counter()
        inc, inc_tok, ex = 0, 0, []
        for c in cases:
            hit = cid in would_refuse(c) if cid in REFUSING else any(
                k["id"] == cid and k["status"] == "FAIL" for k in c.get("checks", ()))
            if not hit:
                continue
            fires[c["corpus"]] += 1
            ex.append(c)
            grp = cid[0]
            if cid not in REFUSING:     # a warning or an annotation stops nothing, so it saves nothing: not a catch
                continue
            if c["corpus"] == "measured_week" and c["end"] not in GATE_ENDS and grp in END_GROUPS.get(c["end"], ""):
                inc += 1
                inc_tok += c.get("tokens", 0)
            elif c["corpus"] == "labelled" and grp in LABEL_GROUPS.get(c["label"], ""):
                inc += 1
        rows.append({"id": cid, "group": cid[0], "refusing": cid in REFUSING, "fires": dict(fires),
                     "fires_total": sum(fires.values()), "incremental": inc, "incremental_tokens_upper_bound": inc_tok,
                     "audited": 0, "false": None})
        if cid in REFUSING and ex:
            ex.sort(key=lambda c: (c["corpus"] == "open", not c.get("worked", c["corpus"] == "measured_week")))
            sample[cid] = [{"item": c["item"], "corpus": c["corpus"], "as_of": c.get("as_of"), "commit": c.get("sha"),
                            "day": c.get("day"), "evidence": [k["evidence"] for k in c["checks"]
                                                             if k["id"] == cid and k["status"] == "FAIL"][:2]}
                           for c in ex[:12]]
    worked = [c for c in cases if (c["corpus"] == "closed_60d" and c.get("worked")) or c["corpus"] == "measured_week"]
    blocked = [c for c in worked if would_refuse(c)]
    pl = planted(shared)
    timing = door_timing([c["item"] for c in cases if c["corpus"] == "open" and c.get("has_refs")] +
                         [c["item"] for c in cases if c["corpus"] == "open" and not c.get("has_refs")], a.timing_sample, w)
    bt_ms = [c["ms"] for c in cases if "ms" in c]
    timing["backtest_per_ticket_inline"] = {"n": len(bt_ms), "p50": round(statistics.median(bt_ms), 2),
                                            "p95": round(pct(bt_ms, 0.95), 2), "max": round(max(bt_ms), 1),
                                            "source": "this backtest, indexes preloaded (the sweep's cost, not a door's)"}
    out = {"date": time.strftime("%Y-%m-%d"), "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "head": git("rev-parse", "--short=10", "HEAD").stdout.strip(), "spec": "design/specs/2026-11-12-ticket-preflight-before-any-token.md section 8",
           "def_capture": (shared["defs"].get("capture") if isinstance(shared["defs"], dict) else "UNMEASURED"),
           "corpora": corpora, "checks": rows, "planted": pl,
           "joint_false_block": {"worked": len(worked), "would_block": len(blocked),
                                 "would_block_share": round(len(blocked) / len(worked), 4) if worked else None,
                                 "audited_false": None, "rate": None,
                                 "reading": "an UPPER BOUND on the joint false-block rate until each would-be refusal is "
                                            "read as of pickup; rate stays null until that audit"},
           "unworked_row": {"n": corpora["closed_60d"]["unworked"],
                            "would_refuse": sum(1 for c in cases if c["corpus"] == "closed_60d" and not c.get("worked") and would_refuse(c))},
           "timing": timing, "audit_sample": sample, "notes": notes,
           "rules": {"refusing": list(REFUSING), "ruled_after": {"checks": list(RULED_CHECKS), "from": RULED},
                     "gate_ends_excluded_from_incremental": list(GATE_ENDS)},
           "elapsed_s": round(time.monotonic() - t0, 1)}
    out["proposed_for_ticket_4"] = proposals(rows)
    out["answer"] = answer(out, cases)
    path = a.out or os.path.join(REPO, "infrastructure", "state", "evidence", "preflight_backtest", out["date"] + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    os.replace(path + ".tmp", path)
    print("BACKTEST %s: %s; planted %d/%d caught; %d of %d worked tickets would have been stopped; %.0f s"
          % (path, ", ".join("%s n=%d" % (k, v["n"]) for k, v in corpora.items()), sum(p["caught"] for p in pl), len(pl),
             len(blocked), len(worked), out["elapsed_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
