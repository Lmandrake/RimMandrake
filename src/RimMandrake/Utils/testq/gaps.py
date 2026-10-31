"""testq/gaps.py -- the filler's evidence-gap order (TESTQ_FILL_RANK_BY_EVIDENCE_GAPS).

Spec: design/RimMandrake/work_allocation_framework_2026-10-26.md section 6.3. It replaces "the stalest chains of
FlowWorks first". When SteveDesktop's lane is idle, `testq.py fill MOD` queues the first non-empty rank, in this order:

  1. fix_landed   a chain whose latest valid run FAILED, and a fix has landed since then: a commit after that run's
                  runner_sha names the chain, one of its FAIL rows or the item the run was for, or it changes files
                  that modcheck's `--changed` maps to the chain. Queued with purpose "fix".
  2. item_owed    a built or validated rimflow item owing a live level a testq run can give (L1, L2 or GREEN-MIN),
                  linked to a chain of MOD the way `modcheck run --item` links them: the chain's source names the item,
                  or the item's ledger text names the chain or one of its rows. Purpose "guard", recorded against the
                  item through row_items.
  3. unmeasured   a chain whose latest valid run at the current identity has UNMEASURED or NOT_RUN rows, except a
                  DRY chain (its last two runs measured nothing; see testq.is_dry).
  4. never_run    a chain with no valid run at the current identity, stalest first.
  5. the sweep    is not the filler's: testq-sweep.timer queues it nightly (`testq.py sweep`).

ONE VERDICT PER CODE VERSION (owner ruling by card 2026-10-31, "Retest only after a code change"; retest.py): a chain
holding a verdict of any kind at its current code version is in NO rank: not a PASS, not a FAIL (a fix that changed no
code changed nothing), not a GAP (a row owed a live check stays owed however often it runs), not a flaky chain (it is
reported in the plan; the repeatability budget, which spent lane time at unchanged code, is gone). A run with no
chain_versions (from before the rule) counts at its identity; a stamped --rows job settles nothing: it ran a prefix. A
harness run is no verdict: its chains are HELD while the repair item for its cause is open, and run once it closes.

IDENTITY. A valid run is a DONE result. Its identity is result.deployed: each mod's dll and defs sha256 plus the
ModsConfig sha256, i.e. what was on the game's disk. The CURRENT identity is that of MOD's latest valid run, unless
MOD's source has changed since that run's runner_sha (the next run deploys a new build); then it is unknown and every
chain counts as never run at it. A run with no `deployed` block has no identity, so it never blocks a re-run.

modcheck (the chain catalogue, item links and `--changed`) is reached through gapprobe.py, a subprocess in this
checkout's src/RimMandrake/Utils/modcheck. A checkout without it, or without MOD's source, cannot see ranks 2 or the
file half of 1. The plan then says "blind: ..." in its text rather than pretending those ranks are empty.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import retest as R  # noqa: E402
import schema as S  # noqa: E402

RANKS = ("fix_landed", "item_owed", "unmeasured", "never_run")
PURPOSE = {"fix_landed": "fix", "item_owed": "guard", "unmeasured": "guard", "never_run": "guard"}
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN")       # the levels one testq run can give an item (minimal list, live)
SITE_HOLD_ROW = "<site hold"
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
GIT_TIMEOUT_S = 30
PROBE_TIMEOUT_S = 120


# ---------------------------------------------------------------- runs and identity

def identity_of(res):
    """-> a 12-hex identity of what a result ran against (result.deployed), or None when it has no deployed block."""
    dep = (res or {}).get("deployed") or {}
    mods = dep.get("mods") or {}
    if not mods:
        return None
    key = {"mods": {k: [(v or {}).get("dll_sha256"), (v or {}).get("defs_sha256")] for k, v in sorted(mods.items())},
           "modsconfig": dep.get("modsconfig_sha256_prerun")}
    return hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:12]


def chain_verdict(rows):
    """-> (verdict, fail_rows) for one chain's rows in one run. verdict: FAIL (a row FAILED), GAP (a row UNMEASURED or
    NOT_RUN, none FAILED), PASS (every row that ran PASSED or was SKIPped), or None (nothing ran but the site hold:
    the site, not the chain, so no verdict)."""
    real = [r for r in rows if not str(r.get("row") or "").startswith(SITE_HOLD_ROW)]
    ran = [r for r in real if r.get("verdict") not in ("NOT_RUN", "SKIP")]
    if not ran:
        return (None, []) if not real or all(r.get("verdict") == "SKIP" for r in real) else ("GAP", [])
    fails = [r.get("row") for r in ran if r.get("verdict") == "FAIL"]
    if fails:
        return "FAIL", fails
    if any(r.get("verdict") not in ("PASS", "SKIP") for r in real):
        return "GAP", []
    return "PASS", []


def valid_runs(mod, recs):
    """-> [{t, id, sha, ident, items, chains: {chain: (verdict, fail_rows)}, versions, partial, harness}] oldest first:
    MOD's DONE results. A harness chain is not in `chains`; it is in `harness`, {chain: cause}."""
    out = []
    for rec in recs:
        job, res = (rec or {}).get("job") or {}, (rec or {}).get("result") or {}
        if job.get("mod") != mod or res.get("outcome", "DONE") != "DONE" or not res.get("rows"):
            continue
        kept, _, causes = R.split_rows(res["rows"])
        by = {}
        for r in kept:
            if r.get("chain"):
                by.setdefault(r["chain"], []).append(r)
        chains = {c: v for c, v in ((c, chain_verdict(rows)) for c, rows in by.items()) if v[0]}
        items = sorted({i for i in [job.get("item")] + list((job.get("row_items") or {}).values()) if i})
        sel = job.get("selector") or {}
        harness = {c: why for c, why in causes.items() if c != R.ORPHAN}
        if R.ORPHAN in causes:      # the run died: a chain it was asked for and never reached is the same fault
            harness.update({c: causes[R.ORPHAN] for c in sel.get("chains") or [] if c not in by and c not in harness})
        died = causes.get(R.ORPHAN) if sel.get("full") else None    # its chains: every one, known to harness_last
        out.append({"t": S.parse_ts(rec.get("finished") or res.get("finished") or job["submitted"]),
                    "died": died, "reached": set(by), "id": job.get("id"), "sha": res.get("runner_sha") or job.get("source_sha"),
                    "ident": identity_of(res), "items": items, "chains": chains,
                    "versions": res.get("chain_versions"), "partial": bool(sel.get("rows")), "harness": harness})
    out.sort(key=lambda r: (r["t"], r["id"] or ""))
    return out


def verdict_versions(runs):
    """-> {chain: {code version}} with a verdict recorded."""
    out = {}
    for run in runs:
        if run["partial"] or not run["versions"]:
            continue
        for c in run["chains"]:
            if run["versions"].get(c):
                out.setdefault(c, set()).add(run["versions"][c])
    return out


def harness_last(mod, runs, recs, every=()):
    """-> {chain: cause}: chains whose latest attempt was a harness run. A job that left no sheet names its chains
    through its selector; a --full one stood for EVERY chain, or the sweep would repeat its death nightly."""
    events = [(run["t"], run["id"] or "", dict({c: run["died"] for c in every if c not in run["reached"]}, **run["harness"])
               if run.get("died") else run["harness"], set(run["chains"])) for run in runs]
    for rec in recs:
        job, res = (rec or {}).get("job") or {}, (rec or {}).get("result") or {}
        cause = R.job_cause(res) if job.get("mod") == mod else None
        if cause:
            sel = job.get("selector") or {}
            chains = every if sel.get("full") else sel.get("chains") or []
            events.append((S.parse_ts(rec.get("finished") or res.get("finished") or job["submitted"]),
                           job.get("id") or "", {c: cause for c in chains}, set()))
    last = {}
    for _, _, harness, measured in sorted(events, key=lambda e: e[:2]):
        for c in measured:
            last.pop(c, None)
        last.update(harness)
    return last


def chain_state(runs, ident):
    """-> {chain: {"last": (run, verdict, fail_rows), "at": (run, verdict) latest at IDENT or None, "flaky": bool,
    "age": t of its latest valid run}}. IDENT None (unknown) matches no run."""
    st = {}
    for run in runs:
        for c, (v, fails) in run["chains"].items():
            s = st.setdefault(c, {"last": None, "at": None, "seen": set(), "age": 0})
            s["last"], s["age"] = (run, v, fails), run["t"]
            if ident is not None and run["ident"] == ident:
                s["at"] = (run, v)
                s["seen"].add(v)
    for s in st.values():
        s["flaky"] = {"PASS", "FAIL"} <= s.pop("seen")
    return st


# ---------------------------------------------------------------- git (this checkout; injectable for selftests)

def repo_root():
    return os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def git(*args):
    """-> stdout, or None when git cannot answer (an unknown sha, no repo)."""
    try:
        r = subprocess.run(["git", "-C", repo_root()] + list(args), capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def mod_dir_rel(mod):
    for t in TIERS:
        rel = "src/%s/%s" % (t, mod)
        if os.path.isdir(os.path.join(repo_root(), rel)):
            return rel
    return None


def source_moved(mod, sha, g=git):
    """True when MOD's source differs between SHA and origin/main; None when that cannot be told."""
    rel = mod_dir_rel(mod)
    if not sha or not rel:
        return None
    out = g("diff", "--name-only", sha, "origin/main", "--", rel)
    return None if out is None else bool(out.strip())


def commits_since(sha, g=git):
    """-> [(short sha, message)] of commits after SHA up to origin/main, or None when git cannot answer."""
    if not sha:
        return None
    out = g("log", "--format=%h%x1f%B%x1e", "%s..origin/main" % sha)
    if out is None:
        return None
    return [tuple(c.strip("\n").split("\x1f", 1)) for c in out.split("\x1e") if c.strip()]


def names_in(text, name):
    """modcheck targeting._names_in: a name with an underscore or digit as a whole token; a one-word name only in
    backticks."""
    if "_" in name or any(ch.isdigit() for ch in name):
        return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name), text) is not None
    return ("`%s`" % name) in text


# ---------------------------------------------------------------- modcheck, through gapprobe.py

def probe(mod, items, since):
    """-> gapprobe.py's answer {"chains", "offline", "item_chains", "changed"}, or {"blind": why}."""
    script = os.path.join(HERE, "gapprobe.py")
    if not os.path.isfile(os.path.join(HERE, "..", "modcheck", "cli.py")):
        return {"blind": "no modcheck in this checkout (a sparse dispatch clone needs src/RimMandrake/Utils/modcheck)"}
    if not mod_dir_rel(mod):
        return {"blind": "no source for %s in this checkout" % mod}
    try:
        r = subprocess.run([sys.executable, script], input=json.dumps({"mod": mod, "items": items, "since": since}),
                           capture_output=True, text=True, timeout=PROBE_TIMEOUT_S, cwd=repo_root())
        out = json.loads((r.stdout or "").strip().splitlines()[-1])
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return {"blind": "gapprobe failed: %s" % ((r.stderr or "").strip()[-200:] if "r" in locals() else "no run")}
    return out


def ledger():
    """-> (model, events, world): the replayed ledger (production: every shard; a selftest: RIMFLOW_LEDGER)."""
    rf = os.path.abspath(os.path.join(HERE, "..", "..", "rimflow"))
    if os.path.dirname(rf) not in sys.path:
        sys.path.insert(0, os.path.dirname(rf))
    from rimflow import model
    model.EVENTS = os.environ.get("RIMFLOW_LEDGER") or model.EVENTS
    events = model.read()
    return model, events, model.replay(events)


def owed_items(world=None):
    """-> {item id: ledger text (title, note texts, prose file)} for built/validated items owing a level in
    LIVE_LEVELS, or None when the ledger cannot be read. WORLD is ledger()'s (model, events, world)."""
    try:
        model, events, w = world or ledger()
    except Exception:      # noqa: BLE001 - a ledger that cannot be read hides rank 2; the plan says so
        return None
    out = {}
    for iid, it in w.items.items():
        if it.state not in ("built", "validated") or not set(it.owed_levels()) & set(LIVE_LEVELS):
            continue
        text = [it.title or ""]
        for h in it.history:
            ev = events[h] if isinstance(h, int) and 0 <= h < len(events) else h
            if isinstance(ev, dict) and ev.get("text"):
                text.append(str(ev["text"]))
        p = os.path.join(getattr(model, "ITEMS", ""), iid + ".md")
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    text.append(fh.read())
            except OSError:
                pass
        out[iid] = "\n".join(text)
    return out


# ---------------------------------------------------------------- the order

def routed_ids(world):
    """-> {item ids} the Test Pilot rule routes (rimflow testpilot_route.routed over WORLD = ledger()), or set()."""
    if not world:
        return set()
    try:
        model, events, w = world
        rf = os.path.abspath(os.path.join(HERE, "..", "..", "rimflow"))
        if os.path.dirname(rf) not in sys.path:
            sys.path.insert(0, os.path.dirname(rf))
        from rimflow import testpilot_route
        return {v["id"] for v in testpilot_route.routed(w, events)}
    except Exception:      # noqa: BLE001 - no ledger, no routing
        return set()


def pilot_chains(world, st, pr):
    """-> {chain: item id} for chains tied to an item the Test Pilot rule routes (rimflow testpilot_route): the item's
    own owed chains (pr item_chains) and the chains its latest run was for. A Test Pilot, not another code-and-retest
    run, takes those; the filler, the sweep and submit all skip them. An unreadable ledger routes nothing."""
    routed = routed_ids(world)
    if not routed:
        return {}
    out = {}
    for iid, chains in (pr.get("item_chains") or {}).items():
        if iid in routed:
            out.update({c: iid for c in chains})
    for c, s in st.items():
        for iid in s["last"][0].get("items") or []:
            if iid in routed:
                out.setdefault(c, iid)
    return out


def settled(mod, recs, world=None, g=None, prober=None, items=None):
    """-> {"settled": chains with a verdict at their code version, "held": chains waiting for a repair item, "runs",
    "ident", "moved", "st", "pr", "items", "blind"}: the retest rule, for rank and for every other door (submit, sweep)."""
    g, prober = g or git, prober or probe
    runs = valid_runs(mod, recs)
    latest = runs[-1] if runs else None
    ident, moved = (latest or {}).get("ident"), None
    if latest and ident:
        moved = source_moved(mod, latest["sha"], g)
        if moved:
            ident = None
    st = chain_state(runs, ident)
    blind = []
    fails = {c: s["last"] for c, s in st.items() if s["last"][1] == "FAIL"}
    since = sorted({run["sha"] for run, _, _ in fails.values() if run["sha"]})
    try:
        world = world or ledger()
    except Exception:  # noqa: BLE001 - a ledger that cannot be read hides ranks and repairs; the plan says so
        world = None
    items = owed_items(world) if world else None
    if items is None:
        blind.append("the ledger could not be read (rank 2, repair holds)")
    pr = prober(mod, items or {}, since)
    if pr.get("blind"):
        blind.append(pr["blind"])
    now_v = pr.get("versions") or {}
    done_v = verdict_versions(runs)
    settled_set, by_identity = set(), set()
    for c in set(st) | set(now_v):
        v = now_v.get(c)
        at = (st.get(c) or {}).get("at")
        if v and v in done_v.get(c, ()):
            settled_set.add(c)
        elif at and not (v and (at[0]["versions"] or {}).get(c)) \
                and not (at[0]["partial"] and (v or (at[0]["versions"] or {}).get(c))):
            by_identity.add(c)      # a run from before chain_versions, or no version known: the identity decides. A
            #                         --rows run is a verdict on its prefix once a version can tell: only the old rule's
    settled_set |= by_identity
    skew = sorted(c for c, s in st.items() if latest and s["last"][0]["sha"] == latest["sha"] and not moved
                  and now_v.get(c) and (s["last"][0]["versions"] or {}).get(c) not in (None, now_v[c])
                  and latest["sha"] and g("rev-parse", "--short", "origin/main") is not None
                  and not g("diff", "--name-only", latest["sha"], "origin/main"))
    if skew:
        blind.append("code version skew: %s differ from the run at this very sha (host-dependent hash?)"
                     % ",".join(skew[:4]))
    w_items = getattr(world[2], "items", {}) if world else {}
    last = harness_last(mod, runs, recs, set(pr.get("chains") or []) | set(st))
    held = sorted(c for c, why in last.items() if c not in settled_set and R.repair_open(w_items, why))
    pilot = pilot_chains(world, st, pr)
    held = sorted(set(held) | set(pilot))
    return {"settled": settled_set, "held": held, "pilot": pilot, "runs": runs, "ident": ident, "moved": moved, "st": st, "pr": pr,
            "items": items, "blind": blind, "fails": fails, "harness": last, "by_identity": by_identity}


def rank(mod, n, now, recs, dry_of, world=None, g=None, prober=None, exclude=()):
    """-> {"rank", "purpose", "pick", "row_items", "dry", "held", "ident", "counts", "flaky", "blind", "text"}.

    RECS: finished records (testq records("done")). DRY_OF(chain) -> bool (testq.is_dry over its history).
    "rank" None means nothing may be queued as filler (every chain holds a verdict at its code version, is held for
    a repair, or is DRY): testq reports verdict "exhausted". EXCLUDE: chains never to pick (modcheck refused them
    this fill). G / PROBER: the git and modcheck answers (selftests pass fakes)."""
    g = g or git
    s0 = settled(mod, recs, world, g, prober)
    runs, ident, moved, st, pr, blind, fails = (s0["runs"], s0["ident"], s0["moved"], s0["st"], s0["pr"], s0["blind"],
                                                s0["fails"])
    done, held_now = s0["settled"], set(s0["held"])
    known = list(pr.get("chains") or [])
    offline = set(pr.get("offline") or [])
    names = [c for c in known if c not in offline] or sorted(st)
    if known:
        names += [c for c in sorted(st) if c not in known and c not in offline]     # modcheck dropped: submit decides
    names = [c for c in dict.fromkeys(names) if c not in set(exclude)]
    dry = sorted(c for c in names if dry_of(c))

    def fresh(c):
        """The one question every rank asks: may this chain be tested now?"""
        return c not in done and c not in held_now

    age = {c: st[c]["age"] if c in st else 0 for c in names}
    cand = {r: [] for r in RANKS}
    why, row_items = {}, {}
    # 1. FAILs with a fix since
    for c, (run, _, frows) in sorted(fails.items()):
        # A FAIL with no version on it is the one case a commit can reopen: only the version could have said "unchanged"
        if c not in names or c in held_now or (c in done and c not in s0["by_identity"]):
            continue
        hit = None
        msgs = commits_since(run["sha"], g)
        for h, msg in msgs or []:
            for nm in [c] + list(frows) + list(run["items"]):
                if names_in(msg, nm):
                    hit = "commit %s names %s" % (h, nm)
                    break
            if hit:
                break
        if not hit and c in ((pr.get("changed") or {}).get(run["sha"]) or []):
            hit = "files changed since %s map to it (modcheck --changed)" % run["sha"]
        if hit:
            cand["fix_landed"].append(c)
            why[c] = hit
            if run["items"]:
                row_items[c] = run["items"][0]          # the verification is recorded against the item it was for
    # 2. built/validated items owing a live level, linked to a chain
    for iid, chains in sorted((pr.get("item_chains") or {}).items()):
        for c in chains:
            if c in names and c not in cand["item_owed"] and fresh(c) and c not in dry:
                row_items[c] = iid
                cand["item_owed"].append(c)
                why[c] = "%s owes a live level" % iid
    # 3. UNMEASURED/NOT_RUN rows at the current identity, at a version with no verdict yet, not DRY
    for c in names:
        if c not in dry and fresh(c) and st.get(c) and st[c]["at"] and st[c]["at"][1] == "GAP":
            cand["unmeasured"].append(c)
    # 4. no verdict at the current version
    for c in names:
        if c not in dry and fresh(c) and c not in cand["unmeasured"]:
            cand["never_run"].append(c)
    flaky = sorted(c for c in names if st.get(c) and st[c]["flaky"])
    counts = {r: len(dict.fromkeys(cand[r])) for r in RANKS}
    counts["flaky"] = len(flaky)
    held = sorted(c for c in names if c in held_now)
    counts["held"] = len(held)
    out = {"dry": dry, "held": held, "ident": ident, "moved": moved, "counts": counts, "flaky": flaky, "blind": blind,
           "row_items": {}, "why": why, "all_dry": False}
    for r in RANKS:
        seq = sorted(dict.fromkeys(cand[r]), key=lambda c: (age[c], c))
        if seq:
            pick = seq[:n]
            ri = {c: row_items[c] for c in pick if c in row_items}
            return dict(out, rank=r, purpose=PURPOSE[r], pick=pick, row_items=ri,
                        text="%s: %s" % (r, ", ".join("%s (%s)" % (c, why[c]) if c in why else c for c in pick)))
    out["all_dry"] = bool(names) and set(dry) == set(names)
    return dict(out, rank=None, purpose=None, pick=[],
                text="exhausted: %d chain(s) hold a verdict at their code version, %d held for a repair, %d DRY%s%s"
                     % (sum(1 for c in names if c in done), len(held), len(dry),
                        "; %d flaky (reported, not repeated)" % len(flaky) if flaky else "",
                        "; blind: " + "; ".join(blind) if blind else ""))
