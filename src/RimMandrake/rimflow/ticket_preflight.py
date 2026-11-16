#!/usr/bin/env python3
"""Ticket preflight, the spine (design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 1).

Report-only: reads the declared facts of one ticket (`## refs` lines file:, new:, def:, tier: and the proof file's
live-tier: / live-mods: lines; prose is never read) and says PASS / FAIL / UNMEASURED per fact. It refuses nothing and
no door calls it yet. Index loading and every check run in ONE forked child with ONE deadline; a cut-off reads
UNMEASURED and `cut_off: true`. A door never builds an index: no cached def index reads UNMEASURED with the build command.

    run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
             tiers=None, deadline_s=5.0, runs_path=None, kind="task", needs="offline", items=None, repo=None) -> {"item", "trigger", "run_id", "total_ms", "cut_off",
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

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(HERE, "..", "Utils")
KEYS = ("file", "new", "def", "tier", "race", "pawnkind", "biome", "item", "sha", "full-why", "new-def", "none",
        "mod", "symbol", "texture")
KIND_TYPES = {"race": "ThingDef", "pawnkind": "PawnKindDef", "biome": "BiomeDef"}
FULL_REASONS = ("interaction", "load-order", "performance", "owner-save", "explicit")
LIVE_KINDS = ("build", "fix", "bug", "defect", "code", "feature")
LIVE_NEEDS = ("deploy", "game-up", "bridge", "harvest")
E12_FIX = ("add to the ticket a `## refs` section with at least one confirmed line (no `(auto)` mark), e.g.\n"
           "## refs\nfile: <a path this ticket changes>\ndef: <Type>/<a def it touches>\ntier: <small|wide>\n"
           "or, when it names nothing checkable, one line `none: <why>`")
BUILD_CMD = "python3 src/RimMandrake/Utils/defindex.py   # builds and caches the def index from the newest capture"
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


def _git_paths():
    r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise OSError("git ls-files exited %d: %s" % (r.returncode, r.stderr.strip()[:200]))
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
        return None, "%s: %s" % (type(e).__name__, str(e)[:240])


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


def _ledger_items():
    import model
    return {iid: {"state": it.state, "successor": it.superseded_by} for iid, it in model.replay(model.read()).items.items()}


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, timeout=5)


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
            a = _git(repo, "merge-base", "--is-ancestor", full, "HEAD")
            if a.returncode == 0:
                obs("B11", v, "PASS", "a landed commit (ancestor of HEAD)", t0=t, origin=org)
            elif a.returncode == 1:
                obs("B11", v, "FAIL", "`%s` resolves but is not an ancestor of HEAD: not landed" % v,
                    "cite the landed sha, or land it first", t0=t, origin=org)
            else:
                obs("B11", v, "UNMEASURED", "git merge-base failed: %s" % a.stderr.strip()[:160], t0=t, origin=org)
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
                if owners else "no declared def gave an owning mod to build a `live-mods:` list from; declare defs, or name `tier: small`")
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
                                      "evidence": "preflight child crashed: %s: %s" % (type(e).__name__, str(e)[:200])}) + "\n")
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


def _append_run(runs_path, line):
    path = runs_path or os.environ.get("RIMFLOW_PREFLIGHT_RUNS") or DEFAULT_RUNS
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line) + "\n")
    except OSError as e:
        sys.stderr.write("preflight: timing line not written (%s)\n" % e)


def run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
             tiers=None, deadline_s=5.0, runs_path=None, kind="task", needs="offline", items=None, repo=None, inline=False):
    t0 = time.perf_counter()
    decls, bad, live_tiers, live_mods = parse(text, proof_text)
    ctx = {"kind": kind, "needs": needs, "items": items, "repo": repo,
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
    rep = {"item": item_id, "trigger": trigger, "run_id": uuid.uuid4().hex[:12],
           "total_ms": round((time.perf_counter() - t0) * 1000, 1), "cut_off": cut, "checks": checks}
    _append_run(runs_path, {"run_id": rep["run_id"], "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "item": item_id,
                            "trigger": trigger, "total_ms": rep["total_ms"], "cut_off": cut,
                            "checks": [{"id": c["id"], "ms": c.get("ms", 0.0), "status": c["status"]} for c in checks]})
    return rep


def _read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def run_item(iid, trigger="pickup", **kw):
    """The ticket's live prose plus its proof file, from the repo the CLI runs in; kind, needs and item ids from the ledger."""
    root = os.path.join(REPO, "infrastructure", "state")
    text = _read(os.path.join(root, "items", "%s.md" % iid)) or _read(os.path.join(root, "items", "closed", "%s.md" % iid))
    proof = _read(os.path.join(root, "live_proofs", iid + ".txt"))
    if "kind" not in kw or "items" not in kw:
        try:
            import model
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


def sweep(hard_stop_s=30.0, per_ticket_s=2.0):
    """Every open ticket once, indexes loaded once, one timing line each (trigger "sweep"), inside the hard stop.
    -> {"tickets", "cut_off", "skipped", "task_with_verify", "e12", "c4", "worst"}; changes no ticket."""
    import model
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
    todo = sorted((i for i in its.values() if i.open), key=lambda i: (not os.path.exists(os.path.join(root, "items", i.id + ".md")), i.id))
    reps, skipped, twv = [], 0, 0
    for n, it in enumerate(todo):
        if time.monotonic() - t_start > hard_stop_s - per_ticket_s:
            skipped = len(todo) - n
            break
        text = _read(os.path.join(root, "items", it.id + ".md"))
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


if __name__ == "__main__":
    rep = run_item(sys.argv[1] if len(sys.argv) > 1 else "")
    print(render(rep))
