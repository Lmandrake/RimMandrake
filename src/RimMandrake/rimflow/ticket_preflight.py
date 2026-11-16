#!/usr/bin/env python3
"""Ticket preflight, the spine (design/specs/2026-11-12-ticket-preflight-before-any-token.md, section 7 ticket 1).

Report-only: reads the declared facts of one ticket (`## refs` lines file:, new:, def:, tier: and the proof file's
live-tier: / live-mods: lines; prose is never read) and says PASS / FAIL / UNMEASURED per fact. It refuses nothing and
no door calls it yet. Index loading and every check run in ONE forked child with ONE deadline; a cut-off reads
UNMEASURED and `cut_off: true`. A door never builds an index: no cached def index reads UNMEASURED with the build command.

    run_text(text, proof_text="", *, item_id="ACCEPT", trigger="pickup", paths=None, defs=None, src=None,
             tiers=None, deadline_s=5.0, runs_path=None) -> {"item", "trigger", "run_id", "total_ms", "cut_off",
                                                              "checks": [{"id", "ref", "status", "ms", "evidence", "fix"}]}
Every run appends one timing line to runs_path (else $RIMFLOW_PREFLIGHT_RUNS, else
~/.local/state/rimmandrake/preflight/runs.jsonl); the write is best effort.
"""
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
KEYS = ("file", "new", "def", "tier")
BUILD_CMD = "python3 src/RimMandrake/Utils/defindex.py   # builds and caches the def index from the newest capture"
DEFAULT_RUNS = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "preflight", "runs.jsonl")


def parse(text, proof_text=""):
    """-> (decls [(key, value, lineno)], bad [(lineno, line, why)], live_tiers, live_mods). Only `## refs` is read."""
    decls, bad, in_refs = [], [], False
    for n, raw in enumerate((text or "").splitlines(), 1):
        line = raw.strip()
        if line.startswith("## "):
            in_refs = line[3:].strip().lower() == "refs"
            continue
        if not in_refs or not line:
            continue
        key, sep, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if not sep or " " in key:
            bad.append((n, line, "no `key:` before the value"))
        elif key not in KEYS:
            bad.append((n, line, "unknown key %r (known: %s)" % (key, ", ".join(KEYS))))
        elif not val:
            bad.append((n, line, "empty value for %s:" % key))
        else:
            decls.append((key, val, n))
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


def plan(decls, bad, live_tiers, live_mods):
    """The (id, ref) observations the child owes, so a cut-off can list every one of them UNMEASURED."""
    out = [("P0", "line %d" % n) for n, _l, _w in bad]
    for k, v, _n in decls:
        if k in ("file", "new"):
            out.append(("B1", v))
        elif k == "tier":
            out.append(("C1", v))
        else:
            out += [("B4", _split_def(v)[1]), ("C2", _split_def(v)[1])]
    for t in live_tiers:
        out.append(("C1", t))
    if any(k == "tier" for k, _v, _n in decls) or live_tiers or live_mods:
        out.append(("C10", None))
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


def _child(decls, bad, live_tiers, live_mods, paths, defs, src, tiers, emit):
    def obs(cid, ref, status, evidence="", fix="", t0=None):
        emit({"id": cid, "ref": ref, "status": status, "evidence": evidence, "fix": fix,
              "ms": round((time.perf_counter() - t0) * 1000, 1) if t0 else 0.0})

    for n, line, why in bad:
        obs("P0", "line %d" % n, "FAIL", "line %d `%s`: %s" % (n, line, why),
            "write the line as `file: <path>`, `new: <path>`, `def: [Type/]<defName>` or `tier: <name>`")

    t0 = time.perf_counter()
    tracked, why = _load("paths", paths, _git_paths)
    tracked = set(tracked) if tracked is not None else None
    tracked_dirs = {p.rsplit("/", 1)[0] for p in tracked if "/" in p} if tracked is not None else None
    for k, v, _n in decls:
        if k not in ("file", "new"):
            continue
        t = time.perf_counter()
        if tracked is None:
            obs("B1", v, "UNMEASURED", "could not list tracked paths (%s)" % why, t0=t)
        elif k == "file":
            if v in tracked:
                obs("B1", v, "PASS", "tracked", t0=t)
            else:
                near = sorted(p for p in tracked if p.rsplit("/", 1)[-1] == v.rsplit("/", 1)[-1])[:3]
                obs("B1", v, "FAIL", "`file: %s` is not a tracked path" % v,
                    ("did you mean %s? " % ", ".join(near) if near else "") +
                    "fix the path, or declare it `new:` if this ticket creates it", t0=t)
        else:
            parent = v.rsplit("/", 1)[0] if "/" in v else ""
            if v in tracked:
                obs("B1", v, "PASS", "declared new, and it already exists (fine once built)", t0=t)
            elif not parent or parent in tracked_dirs or any(d.startswith(parent + "/") for d in tracked_dirs):
                obs("B1", v, "PASS", "planned; its folder exists", t0=t)
            else:
                obs("B1", v, "UNMEASURED", "planned in a folder nothing tracked lives in (%s)" % parent, t0=t)

    # the mod list the defs are judged against: the proof file's live-tier / live-mods, else the ticket's tier: lines
    tier_names = live_tiers or [v for k, v, _n in decls if k == "tier"]
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

    defdecls = [(k, v) for k, v, _n in decls if k == "def"]
    raw = None
    undumped = []
    if defdecls or known_lists:
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
    if not defdecls:
        return
    if raw is None:
        for _k, v in defdecls:
            for cid in ("B4", "C2"):
                obs(cid, _split_def(v)[1], "UNMEASURED", "no def index: %s" % dwhy, BUILD_CMD)
        return
    srcmap, swhy = _load("src", src, _real_src)
    sys.path.insert(0, UTILS)
    import defindex
    ix = defindex.Index(raw)
    ms = defindex.ModSetDefs(ix, pkgs, srcmap or {})
    for _k, v in defdecls:
        t_decl, name = _split_def(v)
        t_norm = defindex.norm_type(t_decl) if t_decl else None
        t = time.perf_counter()
        in_dump = name in ix.by_name
        in_src = bool(srcmap) and name in srcmap
        if not in_dump and not in_src:
            if swhy:
                obs("B4", name, "UNMEASURED", "not in the dump and src/ could not be read (%s)" % swhy, t0=t)
            elif undumped:
                obs("B4", name, "UNMEASURED", "not in the dump, but the list holds mods the dump never saw (%s)"
                    % ", ".join(undumped), t0=t)
            else:
                obs("B4", name, "FAIL", "`%s` is in neither the def dump nor src/" % name,
                    "correct the defName, or declare what creates it", t0=t)
            obs("C2", name, "UNMEASURED", "def not known anywhere", t0=t)
            continue
        if in_dump:
            obs("B4", name, "PASS", "in the dump (%s)" % ", ".join(sorted({r[0] for r in ix.by_name[name]})), t0=t)
        else:
            obs("B4", name, "PASS", "defined in src/", t0=t)
            obs("B5", name, "PASS", "ours, not loaded yet (src/ only, not in the dump)", t0=t)
        t = time.perf_counter()
        if not known_lists:
            obs("C2", name, "UNMEASURED", "no tier: or live-tier: / live-mods: declared to judge it against", t0=t)
            continue
        got = ms.provided(name, t_norm)
        if got is True:
            obs("C2", name, "PASS", "provided by the list", t0=t)
        elif got is False and getattr(tier_map, "approx", False):
            obs("C2", name, "UNMEASURED", "`%s` is not in the tier's named mods (%s), but their dependencies were not "
                "resolved" % (name, ", ".join(ms.owner(name)) or "?"), BUILD_INSTALLED, t0=t)
        elif got is False:
            owners = ms.owner(name)
            obs("C2", name, "FAIL", "`%s` is real but its mod is off the list; owner: %s" % (name, ", ".join(owners) or "?"),
                "add %s to the tier or live-mods:, or pick a def the list provides" % (", ".join(owners) or "its mod"), t0=t)
        else:
            obs("C2", name, "UNMEASURED", "no offline source knows the name", t0=t)


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
             tiers=None, deadline_s=5.0, runs_path=None):
    t0 = time.perf_counter()
    decls, bad, live_tiers, live_mods = parse(text, proof_text)
    owed = plan(decls, bad, live_tiers, live_mods)
    checks, cut = [], False
    try:
        checks, cut = _supervise((decls, bad, live_tiers, live_mods, paths, defs, src, tiers), deadline_s)
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


def run_item(iid, trigger="pickup", **kw):
    """The ticket's live prose plus its proof file, from the repo the CLI runs in."""
    root = os.path.join(REPO, "infrastructure", "state")
    text = proof = ""
    for rel in ("items/%s.md" % iid, "items/closed/%s.md" % iid):
        try:
            text = open(os.path.join(root, rel), encoding="utf-8").read()
            break
        except OSError:
            continue
    try:
        proof = open(os.path.join(root, "live_proofs", iid + ".txt"), encoding="utf-8").read()
    except OSError:
        pass
    return run_text(text, proof, item_id=iid, trigger=trigger, **kw)


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
