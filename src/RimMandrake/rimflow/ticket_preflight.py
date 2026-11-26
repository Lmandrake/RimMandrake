#!/usr/bin/env python3
"""Ticket preflight, the spine (design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 1).

Report-only: reads the declared facts of one ticket (`## refs` lines file:, new:, def:, tier: and the proof file's
live-tier: / live-mods: lines; prose is never read) and says PASS / FAIL / UNMEASURED per fact. It refuses nothing;
since ticket 3 the doors (rimflow file / claim / start, detached_helper.launch) run it in shadow through `Shadow`. Index loading and every check run in ONE forked child with ONE deadline; a cut-off reads
UNMEASURED and `cut_off: true`. A door never builds an index: no cached def index reads UNMEASURED with the build command.

    run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
             tiers=None, deadline_s=DEADLINE_S, runs_path=None, kind="task", needs="offline", items=None, repo=None) -> {"item", "trigger", "run_id", "total_ms", "cut_off",
                                                              "checks": [{"id", "ref", "status", "ms", "evidence", "fix"}]}
Every run appends one timing line to runs_path (else $RIMFLOW_PREFLIGHT_RUNS, else
~/.local/state/rimmandrake/preflight/runs.jsonl); the write is best effort.

Ticket 2 (core kinds, ids, shas, Full reason) adds `## refs` keys race: pawnkind: biome: item: sha: full-why: new-def: none:
(mod:, symbol:, texture: are known keys, not yet checked), the strict parse E11, def kinds B6, item ids B10, shas B11, the
Full Mod reason C4 and the declared block E12, plus `sweep()` over every open ticket. A line ending `(auto)` is a tool's
guess: its observations carry origin "auto" (declared lines "declared"), and only declared ones may ever refuse.
`items` is {id: {"state", "successor"}} or a callable (None: the ledger replay); `repo` is the checkout sha checks run in.
"""
import difflib
import json
import os
import re
import select
import signal
import subprocess
import sys
import time
import uuid

try:
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(HERE, "..", "Utils")
KEYS = ("file", "new", "def", "tier", "race", "pawnkind", "biome", "item", "sha", "full-why", "new-def", "none",
        "mod", "symbol", "texture")
KIND_TYPES = {"race": "ThingDef", "pawnkind": "PawnKindDef", "biome": "BiomeDef"}
FULL_TIER = "full"         # RIMMANDRAKE_FIX_PREFLIGHT_TIER_FULL_ITS_OWN_REPAIR_FAILS: modset_builder has no such tier
FULL_REASONS = ("interaction", "load-order", "performance", "owner-save", "explicit")
LIVE_KINDS = ("build", "fix", "bug", "defect", "code", "feature")
LIVE_NEEDS = ("deploy", "game-up", "bridge", "harvest")
E12_FIX = ("add to the ticket a `## refs` section with at least one confirmed line (no `(auto)` mark), e.g.\n"
           "## refs\nfile: <a path this ticket changes>\ndef: <Type>/<a def it touches>\n"
           "tier: <a tier from python3 src/RimMandrake/Utils/modset_builder.py --list>\n"
           "or, when it names nothing checkable, one line `none: <why>`")
BUILD_CMD = "python3 src/RimMandrake/Utils/defindex.py   # builds and caches the def index from the newest capture"
# a hang guard, never a speed bar: the child is killed at it and every unfinished check reads UNMEASURED; the door opens
DEADLINE_S = 10.0  # budget: danger=a dead mount or stuck git call holds a door open (spec 5.2); evidence=Windows mounts stall (instrument_traps.md); longest=0.9s (runs.jsonl claim max 862.7 ms, 2026-11-26)
SWEEP_STOP_S = 40.0  # budget: danger=one stuck ticket holds the hand-run sweep of every open ticket; evidence=as DEADLINE_S; longest=3.7s (one measured run, 2026-11-26)
DEFAULT_RUNS = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "preflight", "runs.jsonl")


def parse(text, proof_text=""):
    """-> (decls [(key, value, lineno, origin, rel)], bad [(lineno, line, why, rel)], live_tiers, live_mods).
    Only `## refs` is read; `rel` is the line's number inside the refs block, `origin` is auto or declared."""
    decls, bad, in_refs, rel = [], [], False, 0
    for n, raw in enumerate((text or "").splitlines(), 1):
        line = raw.strip()
        if line.startswith("## "):
            in_refs, rel = line[3:].strip().lower() == "refs", 0
            continue
        if not in_refs or not line:
            continue
        rel += 1
        key, sep, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        origin = "declared"
        if val.endswith("(auto)"):
            origin, val = "auto", val[:-len("(auto)")].strip()
        if not sep or " " in key:
            bad.append((n, line, "no `key:` before the value", rel))
        elif key not in KEYS:
            near = difflib.get_close_matches(key, KEYS, n=1, cutoff=0.5)
            bad.append((n, line, "unknown key %r%s (known: %s)" % (key, "; nearest valid key: `%s:`" % near[0] if near else "",
                                                                   ", ".join(KEYS)), rel))
        elif not val:
            bad.append((n, line, "empty value for %s:" % key, rel))
        else:
            decls.append((key, val, n, origin, rel))
    live_tiers, live_mods = [], []
    for raw in (proof_text or "").splitlines():
        m = re.match(r"\s*(live-tier|live-mods)\s*:\s*(.*)$", raw)
        if m:
            vals = [v for v in re.split(r"[\s,]+", m.group(2).strip()) if v]
            (live_tiers if m.group(1) == "live-tier" else live_mods).extend(vals)
    return decls, bad, live_tiers, live_mods


def _split_def(val):
    t, _, n = val.rpartition("/")
    return t.strip() or None, n.strip()


def _asks_full(decls, live_tiers, text):
    crit = re.search(r"^##\s*criteria\s*$(.*?)(?=^##\s|\Z)", text or "", re.M | re.S | re.I)
    return (any(k == "tier" and v.lower() == "full" for k, v, *_ in decls) or "full" in [t.lower() for t in live_tiers]
            or bool(crit and "GREEN-FULL" in crit.group(1)))


def _owes_declared(kind, needs, proof_text):
    return kind in LIVE_KINDS or needs in LIVE_NEEDS or bool((proof_text or "").strip())


def plan(decls, bad, live_tiers, live_mods, asks_full=False, owes_declared=False):
    """The (id, ref) observations the child owes, so a cut-off can list every one of them UNMEASURED."""
    out = [("P0", "line %d" % n) for n, _l, _w, _r in bad] + [("E11", "line %d" % r) for _n, _l, _w, r in bad]
    keys = [(k, v) for k, v, *_ in decls]
    for k, v in keys:
        if k in ("file", "new"):
            out.append(("B1", v))
        elif k == "tier":
            out.append(("C1", v))
        elif k == "def":
            out += [("B4", _split_def(v)[1]), ("C2", _split_def(v)[1])]
        elif k in KIND_TYPES:
            out.append(("B6", v))
        elif k == "item":
            out.append(("B10", v))
        elif k == "sha":
            out.append(("B11", v))
    for t in live_tiers:
        out.append(("C1", t))
    if any(k == "tier" for k, _v in keys) or live_tiers or live_mods:
        out.append(("C10", None))
    if asks_full:
        out.append(("C4", None))
    if owes_declared:
        out.append(("E12", None))
    return out


def _call_s():
    """The one hang guard of a local command (Utils/time_budget.py). At a door the child's DEADLINE_S ends it first."""
    sys.path.insert(0, UTILS)
    import time_budget
    return time_budget.CALL_S


def _git_paths(repo=None):
    r = subprocess.run(["git", "ls-files"], cwd=repo or REPO, capture_output=True, text=True, timeout=_call_s())
    if r.returncode != 0:
        raise OSError("git ls-files exited %d: %s" % (r.returncode, r.stderr.strip()))
    return r.stdout.splitlines()


def _cached_defs():
    sys.path.insert(0, UTILS)
    import defindex
    import gzip
    try:
        names = sorted(n for n in os.listdir(defindex.CACHE) if n.endswith(".json.gz"))
    except OSError:
        names = []
    if not names:
        raise LookupError("no cached def index in %s; a door never builds one. Build: %s" % (defindex.CACHE, BUILD_CMD))
    with gzip.open(os.path.join(defindex.CACHE, names[-1]), "rt", encoding="utf-8") as fh:
        return json.load(fh)


def _real_src():
    sys.path.insert(0, UTILS)
    import defindex
    return defindex.src_defs()


INSTALLED_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "rimmandrake", "preflight", "installed.json")
BUILD_INSTALLED = "python3 src/RimMandrake/rimflow/cli.py preflight --build-index   # scans the installed mods, ~10 s"


def build_installed():
    """Run outside any door: the installed-mod scan the tier resolution needs (modset_builder.scan, ~10 s on drvfs)."""
    sys.path.insert(0, UTILS)
    import modset_builder as MB
    found = MB.scan()
    os.makedirs(os.path.dirname(INSTALLED_CACHE), exist_ok=True)
    with open(INSTALLED_CACHE + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(found, fh, default=str)
    os.replace(INSTALLED_CACHE + ".tmp", INSTALLED_CACHE)
    return len(found)


class _Tiers(object):
    """Tier name -> packageIds. With the prepared installed-mod scan the list is exactly what --apply would write;
    without it (a door never scans) it is the tier's named mods, `approx` is set, and a def that looks off the list
    reads UNMEASURED because a dependency of a named mod may provide it."""

    def __init__(self):
        sys.path.insert(0, UTILS)
        import modset_builder as MB
        self.MB = MB
        try:
            self.installed = json.load(open(INSTALLED_CACHE, encoding="utf-8"))
        except (OSError, ValueError):
            self.installed = None
        self.approx = self.installed is None

    def get(self, name, default=None):
        if self.MB.tier_def(name) is None:
            return default
        if self.installed is not None:
            return [p.lower() for p in self.MB.resolve_tier(name, self.installed)[0]]
        return [p.lower() for p in self.MB.tier_def(name)["want"]]


def _real_tiers():
    return _Tiers()


def _load(what, source, default):
    """-> (value, None) or (None, why): a callable is called, a value used, None means the real default."""
    try:
        v = (source if source is not None else default)
        return (v() if callable(v) else v), None
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, str(e))


_MEMO = {}


def _path_sets(paths):
    """(set of paths, set of their folders), built once per list: the sweep hands the same list to every ticket."""
    hit = _MEMO.get(("paths", id(paths)))
    if hit is None or hit[0] is not paths:
        tracked = set(paths)
        hit = (paths, tracked, {p.rsplit("/", 1)[0] for p in tracked if "/" in p})
        _MEMO[("paths", id(paths))] = hit
    return hit[1], hit[2]


def _index(raw):
    hit = _MEMO.get(("ix", id(raw)))
    if hit is None or hit[0] is not raw:
        import defindex
        hit = (raw, defindex.Index(raw))
        _MEMO[("ix", id(raw))] = hit
    return hit[1]


def _model():
    """The ledger module the caller already bound: the CLI loads it as `rimflow.model` and points it at a redirected
    ledger (RIMFLOW_LEDGER / RIMFLOW_ITEMS); a second, plain `import model` would be a fresh copy aimed at the real one."""
    m = sys.modules.get("rimflow.model")
    if m is None:
        import model as m
    return m


def _ledger_items():
    model = _model()
    return {iid: {"state": it.state, "successor": it.superseded_by} for iid, it in model.replay(model.read()).items.items()}


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, timeout=_call_s())


def _child(decls, bad, live_tiers, live_mods, paths, defs, src, tiers, ctx, emit):
    def obs(cid, ref, status, evidence="", fix="", t0=None, origin=None):
        o = {"id": cid, "ref": ref, "status": status, "evidence": evidence, "fix": fix,
             "ms": round((time.perf_counter() - t0) * 1000, 1) if t0 else 0.0}
        if origin:
            o["origin"] = origin
        emit(o)

    for n, line, why, rel in bad:
        obs("P0", "line %d" % n, "FAIL", "line %d `%s`: %s" % (n, line, why),
            "write the line as `file: <path>`, `new: <path>`, `def: [Type/]<defName>` or `tier: <name>`")
        obs("E11", "line %d" % rel, "FAIL", "refs line %d (file line %d) `%s`: %s" % (rel, n, line, why),
            "use one of: %s" % ", ".join(k + ":" for k in KEYS))
    tier_lines = [(v, n, r) for k, v, n, _o, r in decls if k == "tier"]
    for i, (v, n, r) in enumerate(tier_lines):
        other = next(((v2, n2, r2) for v2, n2, r2 in tier_lines[i + 1:] if v2.lower() != v.lower()), None)
        if other:
            obs("E11", "tier", "FAIL", "two tiers: refs line %d (file line %d) says `%s` and refs line %d (file line %d) says `%s`"
                % (r, n, v, other[2], other[1], other[0]), "keep one `tier:` line")
            break
    newdefs = {_split_def(v)[1]: (n, r) for k, v, n, _o, r in decls if k == "new-def"}
    for k, v, n, _o, r in decls:
        if k == "def" and _split_def(v)[1] in newdefs:
            n2, r2 = newdefs[_split_def(v)[1]]
            obs("E11", _split_def(v)[1], "FAIL", "`%s` is both existing (refs line %d, file line %d `def:`) and to be made "
                "(refs line %d, file line %d `new-def:`)" % (_split_def(v)[1], r, n, r2, n2),
                "keep `def:` if it exists today, `new-def:` if this ticket creates it")

    t0 = time.perf_counter()
    tracked, why = _load("paths", paths, _git_paths)
    tracked, tracked_dirs = _path_sets(tracked) if tracked is not None else (None, None)
    for k, v, _n, org, _r in decls:
        if k not in ("file", "new"):
            continue
        t = time.perf_counter()
        if tracked is None:
            obs("B1", v, "UNMEASURED", "could not list tracked paths (%s)" % why, t0=t, origin=org)
        elif k == "file":
            if v in tracked:
                obs("B1", v, "PASS", "tracked", t0=t, origin=org)
            else:
                near = sorted(p for p in tracked if p.rsplit("/", 1)[-1] == v.rsplit("/", 1)[-1])[:3]
                obs("B1", v, "FAIL", "`file: %s` is not a tracked path" % v,
                    ("did you mean %s? " % ", ".join(near) if near else "") +
                    "fix the path, or declare it `new:` if this ticket creates it", t0=t, origin=org)
        else:
            parent = v.rsplit("/", 1)[0] if "/" in v else ""
            if v in tracked:
                obs("B1", v, "PASS", "declared new, and it already exists (fine once built)", t0=t, origin=org)
            elif not parent or parent in tracked_dirs or any(d.startswith(parent + "/") for d in tracked_dirs):
                obs("B1", v, "PASS", "planned; its folder exists", t0=t, origin=org)
            else:
                obs("B1", v, "UNMEASURED", "planned in a folder nothing tracked lives in (%s)" % parent, t0=t, origin=org)

    # the mod list the defs are judged against: the proof file's live-tier / live-mods, else the ticket's tier: lines
    tier_names = live_tiers or [v for k, v, *_ in decls if k == "tier"]
    tier_map, twhy = (None, None)
    if tier_names:
        tier_map, twhy = _load("tiers", tiers, _real_tiers)
    pkgs, known_lists = set(p.lower() for p in live_mods), bool(live_mods)
    for name in dict.fromkeys(tier_names):
        t = time.perf_counter()
        if name.lower() == FULL_TIER:                # the owner's Full list: what C4 asks for, no modset_builder tier
            obs("C1", name, "PASS", "the Full list (the owner's; no offline list holds it, so defs read UNMEASURED "
                "against it)", t0=t)
            continue
        if tier_map is None:
            obs("C1", name, "UNMEASURED", "could not read the tiers (%s)" % twhy, t0=t)
            continue
        got = tier_map.get(name)
        if got is None:
            obs("C1", name, "FAIL", "`%s` is no tier modset_builder knows" % name,
                "name a tier from `python3 src/RimMandrake/Utils/modset_builder.py --list`", t0=t)
        else:
            obs("C1", name, "PASS", "%d packages%s" % (len(got), " (named mods only: " + BUILD_INSTALLED + ")"
                                                      if getattr(tier_map, "approx", False) else ""), t0=t)
            pkgs |= {p.lower() for p in got}
            known_lists = True

    defdecls = [(k, v, org) for k, v, _n, org, _r in decls if k == "def"]
    kinddecls = [(k, v, org) for k, v, _n, org, _r in decls if k in KIND_TYPES]
    state = {}
    _def_checks(obs, defdecls, kinddecls, known_lists, pkgs, tier_map, defs, src, state)
    _id_checks(obs, decls, ctx)
    _full_check(obs, decls, live_tiers, ctx, state)
    _declared_check(obs, decls, bad, ctx)


def _def_checks(obs, defdecls, kinddecls, known_lists, pkgs, tier_map, defs, src, state):
    raw = None
    undumped = []
    if defdecls or kinddecls or known_lists:
        raw, dwhy = _load("defs", defs, _cached_defs)
    if known_lists and raw is not None:
        t = time.perf_counter()
        undumped = sorted(pkgs - {m.lower() for m in raw.get("mods", [])})
        if undumped:
            obs("C10", None, "FAIL", "the dump of capture %s never held: %s" % (raw.get("capture"), ", ".join(undumped)),
                "re-dump with these mods on, or drop them from the list; defs they own read UNMEASURED", t0=t)
        else:
            obs("C10", None, "PASS", "every mod on the list is in capture %s" % raw.get("capture"), t0=t)
    elif known_lists:
        obs("C10", None, "UNMEASURED", "no def index (%s)" % dwhy)
    if not defdecls and not kinddecls:
        return
    if raw is None:
        for _k, v, org in defdecls:
            for cid in ("B4", "C2"):
                obs(cid, _split_def(v)[1], "UNMEASURED", "no def index: %s" % dwhy, BUILD_CMD, origin=org)
        for _k, v, org in kinddecls:
            obs("B6", v, "UNMEASURED", "no def index: %s" % dwhy, BUILD_CMD, origin=org)
        return
    srcmap, swhy = _load("src", src, _real_src)
    sys.path.insert(0, UTILS)
    import defindex
    ix = _index(raw)
    ms = defindex.ModSetDefs(ix, pkgs, srcmap or {})
    state["ms"], state["ix"] = ms, ix
    for k, v, org in kinddecls:
        t = time.perf_counter()
        types = {defindex.norm_type(r[0]) for r in ix.by_name.get(v, ())} | \
                {defindex.norm_type(r[0]) for r in (srcmap or {}).get(v, ())}
        want = KIND_TYPES[k]
        if not types:
            obs("B6", v, "UNMEASURED" if swhy or undumped else "FAIL",
                "`%s:` names `%s`, which is in neither the def dump nor src/" % (k, v) +
                (" (src/ unreadable: %s)" % swhy if swhy else ""), "" if swhy or undumped else "correct the defName", t0=t, origin=org)
        elif want not in types:
            obs("B6", v, "FAIL", "`%s:` needs a %s, but `%s` is a %s" % (k, want, v, ", ".join(sorted(types))),
                "use the key that matches: race: (a ThingDef with a race), pawnkind:, biome:, or `def: Type/%s`" % v, t0=t, origin=org)
        elif k == "race":
            obs("B6", v, "UNMEASURED", "`%s` is a ThingDef; the dump holds no race field to confirm it is a race" % v, t0=t, origin=org)
        else:
            obs("B6", v, "PASS", "`%s` is a %s" % (v, want), t0=t, origin=org)
    for _k, v, org in defdecls:
        t_decl, name = _split_def(v)
        t_norm = defindex.norm_type(t_decl) if t_decl else None
        t = time.perf_counter()
        in_dump = name in ix.by_name
        in_src = bool(srcmap) and name in srcmap
        if not in_dump and not in_src:
            if swhy:
                obs("B4", name, "UNMEASURED", "not in the dump and src/ could not be read (%s)" % swhy, t0=t, origin=org)
            elif undumped:
                obs("B4", name, "UNMEASURED", "not in the dump, but the list holds mods the dump never saw (%s)"
                    % ", ".join(undumped), t0=t, origin=org)
            else:
                obs("B4", name, "FAIL", "`%s` is in neither the def dump nor src/" % name,
                    "correct the defName, or declare what creates it", t0=t, origin=org)
            obs("C2", name, "UNMEASURED", "def not known anywhere", t0=t, origin=org)
            continue
        if in_dump:
            obs("B4", name, "PASS", "in the dump (%s)" % ", ".join(sorted({r[0] for r in ix.by_name[name]})), t0=t, origin=org)
        else:
            obs("B4", name, "PASS", "defined in src/", t0=t, origin=org)
            obs("B5", name, "PASS", "ours, not loaded yet (src/ only, not in the dump)", t0=t, origin=org)
        t = time.perf_counter()
        if not known_lists:
            obs("C2", name, "UNMEASURED", "no tier: or live-tier: / live-mods: declared to judge it against", t0=t, origin=org)
            continue
        got = ms.provided(name, t_norm)
        if got is True:
            obs("C2", name, "PASS", "provided by the list", t0=t, origin=org)
        elif got is False and getattr(tier_map, "approx", False):
            obs("C2", name, "UNMEASURED", "`%s` is not in the tier's named mods (%s), but their dependencies were not "
                "resolved" % (name, ", ".join(ms.owner(name)) or "?"), BUILD_INSTALLED, t0=t, origin=org)
        elif got is False:
            owners = ms.owner(name)
            obs("C2", name, "FAIL", "`%s` is real but its mod is off the list; owner: %s" % (name, ", ".join(owners) or "?"),
                "add %s to the tier or live-mods:, or pick a def the list provides" % (", ".join(owners) or "its mod"), t0=t, origin=org)
        else:
            obs("C2", name, "UNMEASURED", "no offline source knows the name", t0=t, origin=org)


def _id_checks(obs, decls, ctx):
    """B10 item ids and B11 shas."""
    ids = [(v, org) for k, v, _n, org, _r in decls if k == "item"]
    explicit = [v for k, v, *_ in decls if k == "full-why" and v.lower().startswith("explicit:")]
    items, iwhy = None, None
    if ids or explicit:
        items, iwhy = _load("items", ctx.get("items"), _ledger_items)
    for v, org in ids:
        t = time.perf_counter()
        if items is None:
            obs("B10", v, "UNMEASURED", "could not read the ledger (%s)" % iwhy, t0=t, origin=org)
            continue
        it = items.get(v)
        if it is None:
            near = difflib.get_close_matches(v, list(items), n=1, cutoff=0.8)
            obs("B10", v, "FAIL", "`%s` is no item the ledger knows" % v, ("did you mean %s?" % near[0]) if near else "", t0=t, origin=org)
        elif it.get("state") == "superseded":
            suc = it.get("successor")
            obs("B10", v, "FAIL", "`%s` was superseded%s" % (v, " by %s" % suc if suc else ""),
                "cite %s instead" % suc if suc else "cite the item that replaced it", t0=t, origin=org)
        elif it.get("state") == "dropped":
            obs("B10", v, "FAIL", "`%s` was dropped" % v, "cite a live item, or drop the line", t0=t, origin=org)
        else:
            obs("B10", v, "PASS", "%s (%s)" % (v, "open" if it.get("state") != "closed" and it.get("state") != "done" else "closed"),
                t0=t, origin=org)
    shas = [(v, org) for k, v, _n, org, _r in decls if k == "sha"]
    repo = ctx.get("repo") or REPO
    for v, org in shas:
        t = time.perf_counter()
        if not re.match(r"^[0-9a-fA-F]{7,40}$", v):
            obs("B11", v, "FAIL", "`%s` is not a 7 to 40 character hex sha" % v, "write the sha git log prints", t0=t, origin=org)
            continue
        try:
            r = _git(repo, "rev-parse", "--verify", "--quiet", v + "^{commit}")
            if r.returncode != 0:
                obs("B11", v, "FAIL", "`%s` does not resolve to a commit in %s" % (v, repo),
                    "check the sha, or fetch it if another clone holds it", t0=t, origin=org)
                continue
            full = r.stdout.strip()
            a = _git(repo, "merge-base", "--is-ancestor", full, ctx.get("head") or "HEAD")
            if a.returncode == 0:
                obs("B11", v, "PASS", "a landed commit (ancestor of HEAD)", t0=t, origin=org)
            elif a.returncode == 1:
                obs("B11", v, "FAIL", "`%s` resolves but is not an ancestor of HEAD: not landed" % v,
                    "cite the landed sha, or land it first", t0=t, origin=org)
            else:
                obs("B11", v, "UNMEASURED", "git merge-base failed: %s" % a.stderr.strip(), t0=t, origin=org)
        except (OSError, subprocess.SubprocessError) as e:
            obs("B11", v, "UNMEASURED", "git did not run: %s" % e, t0=t, origin=org)
    ctx["_items"] = items


def _full_check(obs, decls, live_tiers, ctx, state):
    """C4: a Full Mod ask owes one allowed reason (spec 2.1). Reports 'reason recorded', never 'justified'."""
    if not ctx.get("asks_full"):
        return
    t = time.perf_counter()
    whys = [(v, org) for k, v, _n, org, _r in decls if k == "full-why"]
    if not whys:
        ms = state.get("ms")
        defs = [_split_def(v)[1] for k, v, *_ in decls if k == "def"]
        owners = sorted({o for d in defs for o in (ms.owner(d) if ms else [])})
        cand = ("a candidate minimal list from %d declared def(s), no dependency closure: `live-mods: %s`" % (len(defs), " ".join(owners))
                if owners else "no declared def gave an owning mod to build a `live-mods:` list from; declare defs, or name a "
                "smaller tier from `python3 src/RimMandrake/Utils/modset_builder.py --list`")
        obs("C4", None, "FAIL", "the ticket asks for the Full list (`tier: full` or a GREEN-FULL criterion) with no `full-why:` line",
            "add `full-why: <%s>: <specifics>`, or use a smaller list; %s" % ("|".join(FULL_REASONS), cand), t0=t)
        return
    v, org = whys[0]
    word, _, rest = v.partition(":")
    word, rest = word.strip().lower(), rest.strip()
    if word not in FULL_REASONS:
        obs("C4", None, "FAIL", "`full-why: %s` starts with none of: %s" % (v[:60], ", ".join(FULL_REASONS)),
            "start the line with one of those words and a colon", t0=t, origin=org)
    elif not rest:
        obs("C4", None, "FAIL", "`full-why: %s:` has no specifics after the reason" % word, "say what, after the colon", t0=t, origin=org)
    elif word == "explicit":
        items = ctx.get("_items")
        if items is None:
            obs("C4", None, "UNMEASURED", "could not read the ledger to check the id `%s`" % rest.split()[0], t0=t, origin=org)
        elif rest.split()[0] not in items:
            obs("C4", None, "FAIL", "`explicit:` names `%s`, which is no ledger id" % rest.split()[0],
                "name the item or ruling id that says so", t0=t, origin=org)
        else:
            obs("C4", None, "PASS", "reason recorded: explicit, naming %s" % rest.split()[0], t0=t, origin=org)
    else:
        obs("C4", None, "PASS", "reason recorded: %s (shape only; a person judges it)" % word, t0=t, origin=org)


def _declared_check(obs, decls, bad, ctx):
    """E12: a build, fix or live ticket carries a confirmed `## refs` line or a `none: <why>` line."""
    if not ctx.get("owes_declared"):
        return
    t = time.perf_counter()
    confirmed = [k for k, _v, _n, org, _r in decls if org == "declared"]
    if confirmed:
        obs("E12", None, "PASS", "%d confirmed refs line(s)" % len(confirmed), t0=t)
    else:
        autos = sum(1 for d in decls if d[3] == "auto")
        obs("E12", None, "FAIL", "a build, fix or live ticket (kind %s, needs %s) has no confirmed `## refs` line%s"
            % (ctx.get("kind"), ctx.get("needs"), " (%d line(s) are only the tool's `(auto)` guesses)" % autos if autos else ""),
            E12_FIX, t0=t)


def _supervise(args, deadline_s):
    """Fork one child, read its observations as they arrive, kill it at the deadline. -> (observations, cut_off)."""
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        code = 0
        try:
            os.close(r)
            out = os.fdopen(w, "w")

            def emit(o):
                out.write(json.dumps(o) + "\n")
                out.flush()
            _child(*args, emit)
        except BaseException as e:
            code = 1
            try:
                out.write(json.dumps({"id": "CHILD", "ref": None, "status": "UNMEASURED", "ms": 0.0, "fix": "",
                                      "evidence": "preflight child crashed: %s: %s" % (type(e).__name__, str(e))}) + "\n")
                out.flush()
            except Exception:
                pass
        os._exit(code)
    os.close(w)
    got, buf, cut = [], b"", False
    end = time.monotonic() + deadline_s
    try:
        while True:
            left = end - time.monotonic()
            if left <= 0:
                cut = True
                break
            ready, _, _ = select.select([r], [], [], left)
            if not ready:
                continue
            chunk = os.read(r, 65536)
            if not chunk:
                break
            buf += chunk
            *lines, buf = buf.split(b"\n")
            for ln in lines:
                try:
                    got.append(json.loads(ln))
                except ValueError:
                    pass
    finally:
        if cut:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        os.close(r)
        try:
            os.waitpid(pid, 0)
        except OSError:
            pass
    return got, cut


def runs_file(runs_path=None):
    """The timing file: the caller's, else $RIMFLOW_PREFLIGHT_RUNS, else beside a redirected (sandbox) ledger, so a
    test's doors never count in the real metric, else ~/.local/state/rimmandrake/preflight/runs.jsonl."""
    if runs_path or os.environ.get("RIMFLOW_PREFLIGHT_RUNS"):
        return runs_path or os.environ["RIMFLOW_PREFLIGHT_RUNS"]
    led = os.environ.get("RIMFLOW_LEDGER")
    return os.path.join(os.path.dirname(os.path.abspath(led)), "preflight_runs.jsonl") if led else DEFAULT_RUNS


def _append_run(runs_path, line):
    path = runs_file(runs_path)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line) + "\n")
    except OSError as e:
        sys.stderr.write("preflight: timing line not written (%s)\n" % e)


def run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
             tiers=None, deadline_s=DEADLINE_S, runs_path=None,
             kind="task", needs="offline", items=None, repo=None, inline=False,
             head=None, run_id=None, record=True):
    if os.environ.get("RIMFLOW_PREFLIGHT_BREAK") == "1":      # the test hook: the runner raises at entry
        raise RuntimeError("RIMFLOW_PREFLIGHT_BREAK=1 (test hook)")
    t0 = time.perf_counter()
    decls, bad, live_tiers, live_mods = parse(text, proof_text)
    ctx = {"kind": kind, "needs": needs, "items": items, "repo": repo, "head": head,
           "asks_full": _asks_full(decls, live_tiers, text),
           "owes_declared": _owes_declared(kind, needs, proof_text)}
    owed = plan(decls, bad, live_tiers, live_mods, ctx["asks_full"], ctx["owes_declared"])
    checks, cut = [], False
    try:
        if inline:                                   # the sweep: indexes are preloaded, and it keeps its own hard stop
            _child(decls, bad, live_tiers, live_mods, paths, defs, src, tiers, ctx, checks.append)
        else:
            checks, cut = _supervise((decls, bad, live_tiers, live_mods, paths, defs, src, tiers, ctx), deadline_s)
    except Exception as e:                                   # the guard that cannot run says so and lets work through
        checks = [{"id": "CHILD", "ref": None, "status": "UNMEASURED", "ms": 0.0, "fix": "",
                   "evidence": "preflight did not run: %s: %s" % (type(e).__name__, e)}]
    if cut or not checks or checks[-1].get("id") == "CHILD":
        seen = {}
        for c in checks:
            seen[(c["id"], c.get("ref"))] = seen.get((c["id"], c.get("ref")), 0) + 1
        for cid, ref in owed:
            if seen.get((cid, ref), 0) > 0:
                seen[(cid, ref)] -= 1
            else:
                checks.append({"id": cid, "ref": ref, "status": "UNMEASURED", "ms": 0.0, "fix": "",
                               "evidence": "cut off at the %.1f s deadline" % deadline_s if cut else
                               "the preflight child died before reaching it"})
    rep = {"item": item_id, "trigger": trigger, "run_id": run_id or uuid.uuid4().hex[:12],
           "total_ms": round((time.perf_counter() - t0) * 1000, 1), "cut_off": cut, "checks": checks}
    if record:
            _append_run(runs_path, {"run_id": rep["run_id"], "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "item": item_id,
                                "trigger": trigger, "total_ms": rep["total_ms"], "cut_off": cut,
                                "checks": [{"id": c["id"], "ms": c.get("ms", 0.0), "status": c["status"]} for c in checks]})
    return rep


def _read(path):
    """-> the file's text; "" when it does not exist (no prose, no proof file: nothing declared). Any other failure to
    read raises: a ticket that could not be read is not a ticket with no refs, and at claim or start the raise becomes
    "preflight did not run", which stops nothing (Q6)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return ""


def run_item(iid, trigger="pickup", root=None, **kw):
    """The ticket's live prose plus its proof file, from the repo the CLI runs in (or the clone `root`: the helper-launch
    door reads the copy its run will use); kind, needs and item ids from the ledger. The CLI's redirected items folder
    (RIMFLOW_ITEMS, bound into model.ITEMS) is honoured, so a sandbox ledger's doors read the sandbox's prose."""
    state = os.path.join(root or REPO, "infrastructure", "state")
    items_dir = os.path.join(state, "items")
    if root is None:
        try:
            items_dir = _model().ITEMS
        except Exception:                           # noqa: BLE001  the repo's own folder, as before
            pass
    text = _read(os.path.join(items_dir, "%s.md" % iid)) or _read(os.path.join(items_dir, "closed", "%s.md" % iid))
    proof = _read(os.path.join(state, "live_proofs", iid + ".txt"))
    if root is not None:
        kw.setdefault("repo", root)
        kw.setdefault("paths", lambda: _git_paths(root))
    if "kind" not in kw or "items" not in kw:
        try:
            model = _model()
            its = model.replay(model.read()).items
            it = its.get(iid)
            if it is not None:
                kw.setdefault("kind", it.kind or "task")
                kw.setdefault("needs", it.needs or "offline")
            kw.setdefault("items", {k: {"state": v.state, "successor": v.superseded_by} for k, v in its.items()})
        except Exception as e:                      # the guard that cannot run says so: ids read UNMEASURED below
            sys.stderr.write("preflight: ledger not read (%s: %s)\n" % (type(e).__name__, e))
    return run_text(text, proof, item_id=iid, trigger=trigger, **kw)


def _raiser(e):
    def f():
        raise e
    return f


def sweep(hard_stop_s=SWEEP_STOP_S, per_ticket_s=2.0):
    """Every open ticket once, indexes loaded once, one timing line each (trigger "sweep"), inside the hard stop.
    -> {"tickets", "cut_off", "skipped", "task_with_verify", "e12", "c4", "worst"}; changes no ticket."""
    model = _model()
    t_start = time.monotonic()
    its = model.replay(model.read()).items
    items = {k: {"state": v.state, "successor": v.superseded_by} for k, v in its.items()}
    shared = {}
    for name, loader in (("paths", _git_paths), ("defs", _cached_defs), ("src", _real_src), ("tiers", _real_tiers)):
        try:
            shared[name] = loader()
        except Exception as e:                      # each ticket then reads UNMEASURED with the reason
            shared[name] = _raiser(e)
    root = os.path.join(REPO, "infrastructure", "state")
    todo = sorted((i for i in its.values() if i.open), key=lambda i: (not os.path.exists(os.path.join(model.ITEMS, i.id + ".md")), i.id))
    reps, skipped, twv = [], 0, 0
    for n, it in enumerate(todo):
        if time.monotonic() - t_start > hard_stop_s - per_ticket_s:
            skipped = len(todo) - n
            break
        text = _read(os.path.join(model.ITEMS, it.id + ".md"))
        proof = _read(os.path.join(root, "live_proofs", it.id + ".txt"))
        if (it.kind or "task") == "task" and re.search(r"^##\s*verify\s*\n\s*\S", text, re.M | re.I):
            twv += 1
        reps.append(run_text(text, proof, item_id=it.id, trigger="sweep", kind=it.kind or "task", needs=it.needs or "offline",
                             items=items, inline=True, **shared))

    def tally(cid):
        c = {"PASS": 0, "FAIL": 0, "UNMEASURED": 0}
        for r in reps:
            for ck in r["checks"]:
                if ck["id"] == cid:
                    c[ck["status"]] += 1
        return c
    worst = sorted(reps, key=lambda r: -r["total_ms"])[:10]
    return {"tickets": len(todo), "run": len(reps), "skipped": skipped, "cut_off": skipped > 0,
            "total_s": round(time.monotonic() - t_start, 1), "task_with_verify": twv, "e12": tally("E12"), "c4": tally("C4"),
            "with_a_fail": sum(1 for r in reps if any(c["status"] == "FAIL" for c in r["checks"])),
            "worst": [{"item": r["item"], "total_ms": r["total_ms"], "cut_off": r["cut_off"]} for r in worst]}


def render_sweep(sw):
    lines = ["PREFLIGHT SWEEP: %d open tickets, %d run in %.1f s%s; %d carry a FAIL" % (
        sw["tickets"], sw["run"], sw["total_s"], ", CUT OFF (%d not run)" % sw["skipped"] if sw["cut_off"] else "", sw["with_a_fail"]),
        "  E12 declared block: %(PASS)d pass, %(FAIL)d FAIL" % sw["e12"],
        "  C4 Full reason:     %(PASS)d pass, %(FAIL)d FAIL" % sw["c4"],
        "  task_with_verify:   %d open `task` tickets carry a `## verify` command (the gap E12 cannot see)" % sw["task_with_verify"],
        "  slowest:"]
    lines += ["    %8.1f ms  %s%s" % (w["total_ms"], w["item"], "  CUT OFF" if w["cut_off"] else "") for w in sw["worst"]]
    return "\n".join(lines)


def render(rep):
    lines = ["PREFLIGHT %s (%s, %.0f ms%s): %s" % (
        rep["item"], rep["trigger"], rep["total_ms"], ", CUT OFF" if rep["cut_off"] else "",
        ", ".join("%d %s" % (sum(1 for c in rep["checks"] if c["status"] == s), s)
                  for s in ("PASS", "FAIL", "UNMEASURED")))]
    for c in rep["checks"]:
        if c["status"] != "PASS":
            lines.append("  %-10s %s %s: %s%s" % (c["status"], c["id"], c.get("ref") or "", c.get("evidence", ""),
                                                  ("  FIX: " + c["fix"]) if c.get("fix") else ""))
    return "\n".join(lines)


# --- the doors (ticket 3 shadow, RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS; ticket 4 enforcement) -----------
# rimflow file / claim / start and detached_helper.launch run the preflight here: they print its lines and record them.
# Filing and the helper launch refuse nothing. claim and start STOP a launched run on a FAIL of a new declared-fact check
# (`enforce`): owner, by card 2026-11-13, Q1 "filing warns, pickup stops", Q3 (E12), Q4 (C4), Q5 "only the Conductor
# may bypass", Q6 "can't check -> go ahead". The refusal goes back to the same agent with its repair, which it makes and
# claims again (root CLAUDE.md §A fault of form is repaired where it is found); the Conductor and the owner pass with a
# NOTE (principal.form). The launch door does not stop: no agent is there yet to repair, and the run's first act, its
# claim or start, is the stop. An existing gate's authority stays in its own code. Not in Relentless (retired).
DOOR_TRIGGER = {"file": "create", "claim": "pickup", "start": "pickup", "helper_launch": "pickup"}
ENFORCING_DOORS = ("claim", "start")
SHOW_MAX = 8
STOP_HEAD = ("REFUSED at %s by the ticket preflight: a declared fact of %s is wrong (owner, by card 2026-11-13: "
             "filing warns, pickup stops). Repair infrastructure/state/items/%s.md (its `## refs` section) or its proof "
             "file as each FIX says, then %s again; `rimflow preflight %s` re-checks in about 0.1 s.")


class Shadow(object):
    """One door's preflight in shadow. `run(**kw)` runs the new checks (run_item's keywords); `gate(id, fn, *a,
    judge=None)` calls an existing gate exactly as the door did and records its answer and time: `judge(result)` ->
    (status, evidence), default PASS; a SystemExit (the gate refused) is recorded FAIL, the line is written, and it is
    re-raised unchanged. `fields()` -> the ledger event's preflight_run / preflight_ms / preflight; `finish()` writes the
    one timing line (door, seat, new checks and gates) and returns the text to show. A runner that throws is "preflight
    did not run"; an unwritable timing file is reported. The authority of every gate stays in its own code."""

    def __init__(self, door, item_id, seat=None, runs_path=None):
        self.door, self.item, self.seat, self.runs_path = door, item_id, seat, runs_path
        self.trigger = DOOR_TRIGGER.get(door, "pickup")
        self.run_id = uuid.uuid4().hex[:12]
        self.checks, self.gates, self.crash, self.cut, self.done = [], [], None, False, None
        self.ms = 0.0
        self.refused, self.override = [], None

    def run(self, **kw):
        t = time.perf_counter()
        try:
            kw.setdefault("deadline_s", DEADLINE_S)
            rep = run_item(self.item, trigger=self.trigger, run_id=self.run_id, record=False, **kw)
            self.checks, self.cut = rep["checks"], rep["cut_off"]
        except Exception as e:                          # noqa: BLE001  the door carries on
            self.crash = "%s: %s" % (type(e).__name__, str(e))
        self.ms += (time.perf_counter() - t) * 1000
        return self

    def gate(self, gid, fn, *a, **kw):
        judge = kw.pop("judge", None)
        t = time.perf_counter()
        try:
            res = fn(*a, **kw)
        except SystemExit as e:
            self._note(gid, "FAIL", "the existing gate refused at the door (exit %s)" % e.code, t)
            self.finish()
            raise
        except Exception as e:
            self._note(gid, "FAIL", "the existing gate raised %s: %s" % (type(e).__name__, str(e)), t)
            self.finish()
            raise
        try:
            status, ev = judge(res) if judge else ("PASS", "")
        except Exception as e:                          # noqa: BLE001  a judge that cannot read says so
            status, ev = "UNMEASURED", "could not read the gate's answer: %s" % e
        self._note(gid, status, ev, t)
        return res

    def _note(self, gid, status, evidence, t0):
        ms = round((time.perf_counter() - t0) * 1000, 1)
        self.ms += ms
        self.gates.append({"id": gid, "ref": None, "status": status, "evidence": evidence, "fix": "", "ms": ms,
                           "origin": "gate"})

    def stops(self):
        """-> the observations that stop a pickup: a FAIL of a new check on a line the ticket declared. A tool's own
        `(auto)` guess, an UNMEASURED check, a cut-off run and a runner that did not run stop nothing (Q6)."""
        if self.crash:
            return []
        return [c for c in self.checks if c["status"] == "FAIL" and c.get("origin", "declared") == "declared"]

    def enforce(self, seat=None, env=None):
        """At claim and start: refuse a launched run whose ticket fails a declared-fact check, with each repair; the
        Conductor window and the owner pass with a NOTE (principal.form). Any other door: nothing. Returns the note."""
        if self.door not in ENFORCING_DOORS:
            return None
        bad = self.stops()
        if not bad:
            return None
        ids = " ".join(sorted({c["id"] for c in bad}))
        lines = [STOP_HEAD % (self.door, self.item, self.item, self.door, self.item)]
        for c in bad:
            lines.append("  FAIL %s %s: %s" % (c["id"], c.get("ref") or "", c.get("evidence", "")))
            if c.get("fix"):
                lines.append("    FIX: " + c["fix"].replace("\n", "\n         "))
        import principal
        who = principal.who(env, seat)
        self.refused = sorted({c["id"] for c in bad})
        if who:
            self.override = who
        try:
            return principal.form("the ticket preflight would stop this %s (%s); passed for the %s"
                                  % (self.door, ids, "Conductor" if who == "conductor" else "owner"),
                                  refusal="\n".join(lines), env=env, seat=seat, code=2)
        except SystemExit:
            self.finish()
            raise

    def verdict(self):
        if self.crash:
            return "did not run"
        if self.refused:
            return ("passed by %s: " % self.override if self.override else "refused ") + " ".join(self.refused)
        fails = sorted({c["id"] for c in self.checks + self.gates if c["status"] == "FAIL"})
        return ("fail " + " ".join(fails)) if fails else "pass"

    def fields(self):
        return {"preflight_run": self.run_id, "preflight_ms": round(self.ms, 1), "preflight": self.verdict()}

    def finish(self):
        if self.done is not None:
            return self.done
        allc = self.checks + self.gates
        line = {"run_id": self.run_id, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "item": self.item,
                "trigger": self.trigger, "door": self.door, "seat": self.seat, "total_ms": round(self.ms, 1),
                "cut_off": self.cut, "verdict": self.verdict(), "crash": self.crash, "override": self.override,
                "checks": [{"id": c["id"], "ms": c.get("ms", 0.0), "status": c["status"],
                            "origin": c.get("origin", "declared")} for c in allc]}
        _append_run(self.runs_path, line)
        if self.crash:
            self.done = "preflight did not run (%s); the door carries on" % self.crash
            return self.done
        bad = [c for c in allc if c["status"] != "PASS"]
        mode = ("REFUSED" if self.refused and not self.override else "pickup stops a wrong declared fact"
                if self.door in ENFORCING_DOORS else "warns only")
        out = ["PREFLIGHT, %s (%s %s, %.0f ms%s): %d checks, %d not PASS" % (
            mode, self.door, self.item, self.ms, ", CUT OFF" if self.cut else "", len(allc), len(bad))]
        for c in bad[:SHOW_MAX]:
            where = "rimflow preflight %s" % self.item
            out.append("  %-10s %s %s: %s%s" % (c["status"], c["id"], c.get("ref") or "",
                                                fulltext.clip(c.get("evidence", ""), 220, where),
                                                ("  FIX: " + fulltext.clip(c["fix"], 160, where)) if c.get("fix")
                                                else ""))
        if len(bad) > SHOW_MAX:
            out.append("  ... %d more: rimflow preflight %s" % (len(bad) - SHOW_MAX, self.item))
        self.done = "\n".join(out)
        return self.done


TARGET_MS = {"create": 1000.0, "pickup": 1000.0}     # spec 5.2: the p95 a door's whole preflight should keep under


def _pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))] if v else None


def timing(runs_path=None, last=200):
    """-> the recorded run time per door over the last `last` lines of the timing file (spec 5.4): count, p50, p95,
    max, refusals, Conductor or owner passes, cut-offs, runs that did not run, and the five slowest checks."""
    path = runs_file(runs_path)
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for l in fh:
                try:
                    rows.append(json.loads(l))
                except ValueError:
                    continue
    except OSError as e:
        return {"path": path, "error": str(e), "doors": {}}
    rows = rows[-last:] if last else rows
    doors = {}
    for r in rows:
        d = r.get("door") or "hand:" + str(r.get("trigger"))
        g = doors.setdefault(d, {"n": 0, "ms": [], "added": [], "refused": 0, "passed": 0, "cut": 0, "crash": 0, "checks": {},
                                 "trigger": r.get("trigger")})
        g["n"] += 1
        g["ms"].append(float(r.get("total_ms") or 0.0))
        gates = sum(float(c.get("ms") or 0.0) for c in r.get("checks") or [] if c.get("origin") == "gate")
        g["added"].append(max(0.0, g["ms"][-1] - gates))       # the preflight's own cost, beside the gates it times
        v = str(r.get("verdict") or "")
        g["refused"] += v.startswith("refused")
        g["passed"] += v.startswith("passed by")
        g["cut"] += bool(r.get("cut_off"))
        g["crash"] += bool(r.get("crash")) or v == "did not run"
        for c in r.get("checks") or []:
            g["checks"].setdefault(c.get("id"), []).append(float(c.get("ms") or 0.0))
    out = {}
    for d, g in doors.items():
        slow = sorted(((cid, _pct(v, 0.95), max(v)) for cid, v in g["checks"].items()), key=lambda t: -t[1])[:5]
        out[d] = {"n": g["n"], "p50_ms": _pct(g["ms"], 0.5), "p95_ms": _pct(g["ms"], 0.95), "max_ms": max(g["ms"]),
                  "added_p95_ms": _pct(g["added"], 0.95),
                  "refused": g["refused"], "passed_by_principal": g["passed"], "cut_off": g["cut"],
                  "did_not_run": g["crash"], "target_p95_ms": TARGET_MS.get(g["trigger"]),
                  "slowest_checks": [{"id": c, "p95_ms": p, "max_ms": m} for c, p, m in slow]}
    return {"path": path, "runs": len(rows), "doors": out}


def render_timing(t):
    if t.get("error"):
        return "no timing lines read at %s (%s)" % (t["path"], t["error"])
    out = ["preflight run time, last %d runs (%s)" % (t["runs"], t["path"]),
           "%-16s %5s %9s %9s %9s %9s %7s %6s %4s %4s  slowest checks (p95 ms)" % (
               "door", "runs", "p50 ms", "p95 ms", "max ms", "added p95", "refused", "passed", "cut", "dnr")]
    for d, g in sorted(t["doors"].items()):
        over = ("  OVER the %.0f ms added-time target" % g["target_p95_ms"]
                if g["target_p95_ms"] and g["added_p95_ms"] > g["target_p95_ms"] else "")
        out.append("%-16s %5d %9.1f %9.1f %9.1f %9.1f %7d %6d %4d %4d  %s%s" % (
            d, g["n"], g["p50_ms"], g["p95_ms"], g["max_ms"], g["added_p95_ms"], g["refused"], g["passed_by_principal"], g["cut_off"],
            g["did_not_run"], ", ".join("%s %.0f" % (c["id"], c["p95_ms"]) for c in g["slowest_checks"]), over))
    out.append("(p50/p95/max: the whole door, the existing gates it times included, e.g. I6 at helper_launch; added p95: "
               "the preflight's own time, the spec 5.2 target; passed = the Conductor or the owner passed a stop; dnr = "
               "the preflight did not run)")
    return "\n".join(out)


def items_of(world):
    """-> a callable the child calls: the ledger's items as B10 reads them, from a world the door already replayed."""
    return lambda: {k: {"state": v.state, "successor": v.superseded_by} for k, v in world.items.items()}


if __name__ == "__main__":
    rep = run_item(sys.argv[1] if len(sys.argv) > 1 else "")
    print(render(rep))
