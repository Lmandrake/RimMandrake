#!/usr/bin/env python3
"""lightspeed_wire.py -- write live-proof lines for owed Relentless criteria that name a row of their mod's suite
(LIGHTSPEED_WIRE_PROOF_LINES_882_OWED; spec design/RimMandrake/lightspeed_2026-11-06.md section 4 row 5).

A built item's live criterion with no `live-proof` line in infrastructure/state/live_proofs/<ID>.txt can never run on
any lane (`relentless_live_round.py eligible` counts it `no proof`). Where the criterion's own text names a row id
(or an underscored chain name) of a modcheck suite of a mod the item touches or names, the proof is that row: a
targeted `modcheck/cli.py run <Mod> --rows ...` and `row_verdict.py --row ...` on its newest result. Nothing is
guessed: a criterion naming no row stays unmatched, with its reason, counted per mod.

    python3 src/RimMandrake/rimflow/lightspeed_wire.py scan      # read the ledger + suites -> snapshot and per-mod tsv
    python3 src/RimMandrake/rimflow/lightspeed_wire.py write     # scan, then append the matched lines (lint first)
    python3 src/RimMandrake/rimflow/lightspeed_wire.py check     # offline gate; exit 0 holds, 1 does not
    python3 src/RimMandrake/rimflow/lightspeed_wire.py lint <ID> # lint every live-proof line of one item (at filing)

Lint (the same checks the live round applies at run time, moved to filing; PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN):
relentless_live.owed() (built, owed, live level, not cut at 160 chars), refused_proof() (flyer wording, OWNER.jsonl,
run-time expansion, game-changing commands), owner_look() (a look gets no fake proof), every repo script the line
names exists, and the line parses back to its own clause.

`check` needs no git (the walled checker has none): the build's mod folders come from the committed snapshot
infrastructure/state/lightspeed_wire.json, which `scan` writes from git. It recomputes the match from the ledger,
the live_proofs files and the suites, and holds when (a) every criterion the snapshot matched has its line and the
line lints, (b) no still-unproved owed criterion matches a row, (c) the tsv is the snapshot's per-mod count.
"""
import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import relentless_live_round as R     # noqa: E402

L = R.L
MODCHECK = os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck")
SNAPSHOT = os.path.join(ROOT, "infrastructure", "state", "lightspeed_wire.json")
TSV = os.path.join(ROOT, "infrastructure", "state", "lightspeed_unmatched.tsv")
PROOFS = os.path.join(ROOT, R.PROOFS_DIR)
MARK = "# lightspeed_wire:"      # the comment above every line this tool wrote; check finds its lines by it
NO_MOD = "(no mod)"
SCRIPT = re.compile(r"(?<![\w./-])((?:src|infrastructure|skills)/[\w./-]+\.py)\b")
CMD = ("MODCHECK_SKIP_DEPLOY=1 MODCHECK_KEEP_MODLIST=1 WSLENV=MODCHECK_SKIP_DEPLOY:MODCHECK_KEEP_MODLIST "
       "python.exe src/RimMandrake/Utils/modcheck/cli.py run {mod} {sel} --gate off --purpose fix "
       "--item {mod}={item} --seat BENCH < /dev/null; python3 src/RimMandrake/Utils/modcheck/live_queue/row_verdict.py "
       "--max-age-min 30 --mod {mod} {rows}")


# ---------------------------------------------------------------- suites

def _cat_one(mod_dir):
    """Run in a child: one mod's catalogue as JSON (a validation.py import can be slow or hang; the parent times it)."""
    sys.path.insert(0, MODCHECK)
    import runner
    import targeting
    s = runner.load_validation(mod_dir)
    cat, inc = targeting.catalogue(s)
    return {"chains": cat, "incomplete": inc, "offline": sorted(getattr(s, "offline_chains", ()) or ())}


def mod_dirs():
    out = {}
    for tier in ("RimMandrake", "RimStarWars", "RimUtinni"):
        base = os.path.join(ROOT, "src", tier)
        for m in sorted(os.listdir(base)) if os.path.isdir(base) else ():
            if os.path.isfile(os.path.join(base, m, "validation.py")):
                out[m] = os.path.join(base, m)
    return out


def _key(mod_dir):
    h = hashlib.sha256()
    for p in (os.path.join(mod_dir, "validation.py"), os.path.join(MODCHECK, "suite.py"),
              os.path.join(MODCHECK, "targeting.py")):
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


def catalogues(mods=None, timeout=300, cache_dir=None):
    """-> {mod: {"chains", "incomplete", "offline"} or {"error"}}. Cached per validation.py hash in cache_dir."""
    dirs = mod_dirs()
    want = sorted(dirs if mods is None else (m for m in mods if m in dirs))
    cache_dir = cache_dir or os.path.join(os.environ.get("TMPDIR") or "/tmp", "lightspeed_wire_cat")
    os.makedirs(cache_dir, exist_ok=True)

    def one(m):
        p = os.path.join(cache_dir, "%s_%s.json" % (m, _key(dirs[m])))
        if os.path.isfile(p):
            with open(p) as f:
                return m, json.load(f)
        try:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "_cat", dirs[m]], capture_output=True,
                               text=True, timeout=timeout, cwd=ROOT)
            last = (r.stdout or "").strip().splitlines()[-1:] or [""]
            got = json.loads(last[0]) if r.returncode == 0 and last[0].startswith("{") else \
                {"error": ((r.stderr or r.stdout or "").strip().splitlines() or ["exit %d" % r.returncode])[-1][:200]}
        except subprocess.TimeoutExpired:
            got = {"error": "catalogue read timed out after %d s" % timeout}
        if "error" not in got:
            with open(p, "w") as f:
                json.dump(got, f)
        return m, got
    with ThreadPoolExecutor(8) as ex:
        return dict(ex.map(one, want))


# ---------------------------------------------------------------- matching (pure)

def _names_in(text, name):
    """targeting._names_in: a whole token; a name with no underscore or digit only in backticks."""
    if "_" in name or any(ch.isdigit() for ch in name):
        return re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name), text) is not None
    return ("`%s`" % name) in text


def names_mod(mod, iid, text):
    """targeting.names_mod."""
    return bool(mod) and (mod.lower() in (text or "").lower() or mod.upper() in (iid or "").replace("_", "").upper())


def match(item_id, text, build_mods, cats):
    """-> (selection or None, reason). selection = {"mod", "rows" [row ids the criterion names], "chains" [chains named
    whole, or the owners of the rows when the mod's catalogue cannot cut a prefix], "by" [why]}. Pure.
    Candidate mods: the build's, plus any suite mod the criterion or the item id names (targeting.names_mod)."""
    text = text or ""
    cands = [m for m in cats if m in build_mods or names_mod(m, item_id, text)]
    if not cands:
        return None, "no suite: the build touched no mod with a validation.py and the text names none"
    hits = {}
    for m in cands:
        c = cats[m]
        if "error" in c:
            continue
        off = set(c.get("offline") or ())
        rows, chains, offrows = [], [], []
        for ch, rs in c["chains"].items():
            if ("_" in ch or any(x.isdigit() for x in ch) or "`%s`" % ch in text) and _names_in(text, ch):
                (offrows if ch in off else chains).append(ch)
            for r in rs:
                if _names_in(text, r):
                    (offrows if ch in off else rows).append((ch, r))
        if rows or chains or offrows:
            hits[m] = (rows, chains, offrows)
    if not hits:
        bad = [m for m in cands if "error" in cats[m]]
        if bad and len(bad) == len(cands):
            return None, "suite unreadable: %s (%s)" % (", ".join(bad), cats[bad[0]]["error"][:80])
        return None, "names no row: the text names no row or chain id of %s" % ", ".join(sorted(cands))
    live = {m: h for m, h in hits.items() if h[0] or h[1]}
    if not live:
        return None, "offline rows only: %s rows it names run at T0, never live" % ", ".join(sorted(hits))
    score = sorted(live, key=lambda m: -(len(live[m][0]) + len(live[m][1])))
    if len(score) > 1 and len(live[score[0]][0]) + len(live[score[0]][1]) == len(live[score[1]][0]) + len(live[score[1]][1]):
        return None, "ambiguous mod: it names rows of %s equally" % ", ".join(score[:2])
    m = score[0]
    rows, chains, _ = live[m]
    c = cats[m]
    row_ids = sorted({r for _, r in rows})
    # several chains declaring one row, or an incomplete live catalogue anywhere: targeting refuses a row cut; run
    # the owning chains whole instead (row_verdict still reads only the named rows)
    blocking = set(c.get("incomplete") or {}) - set(c.get("offline") or ())
    whole = sorted(set(chains))
    if whole or blocking - set(whole):
        # --chains alone runs only the chains it names: a named row's own chain joins them, or its verdict reads NOT_RUN
        whole = sorted(set(whole) | {ch for ch, _ in rows})
    running = whole or sorted({ch for ch, _ in rows})
    twice = [r for r in row_ids if sum(r in c["chains"].get(ch, ()) for ch in running) > 1]
    if twice:
        return None, "ambiguous row: %s is declared by more than one chain the run would execute" % ", ".join(twice)
    by = ["row %s.%s named in the criterion" % (ch, r) for ch, r in rows] + ["chain %s named" % ch for ch in chains]
    if not row_ids:
        # a chain named whole decides by its rows: every row it declares must hold
        row_ids = sorted({r for ch in chains for r in c["chains"][ch]})
        if not row_ids:
            return None, "names an empty chain: %s" % ", ".join(chains)
    return {"mod": m, "rows": row_ids, "chains": whole, "by": by}, "matched"


def line(item_id, sel):
    if sel["chains"]:
        s = "--chains " + ",".join(sel["chains"])
    else:
        s = "--rows " + ",".join(sel["rows"])
    return CMD.format(mod=sel["mod"], sel=s, item=item_id, rows=" ".join("--row " + r for r in sel["rows"]))


# ---------------------------------------------------------------- lint

def preview_gap(mod, sel, root=ROOT):
    """-> why modcheck's own offline plan (`run <mod> <sel> --preview`, no game) would not execute every row the line
    reads, or None. The selection is the line's, so the plan is what the live run will do."""
    args = ["--chains", ",".join(sel["chains"])] if sel["chains"] else ["--rows", ",".join(sel["rows"])]
    try:
        r = subprocess.run([sys.executable, os.path.join(MODCHECK, "cli.py"), "run", mod] + args + ["--preview"],
                           capture_output=True, text=True, timeout=120, cwd=root)
    except (OSError, subprocess.SubprocessError) as e:
        return "preview could not run: %s" % e
    out = (r.stdout or "") + (r.stderr or "")
    for ln in out.splitlines():
        if ln.startswith("REFUSED"):
            return "modcheck refuses the selection: %s" % ln[:200]
        if ln.startswith("EXPECTED_ROWS "):
            got = json.loads(ln[len("EXPECTED_ROWS "):])
            miss = [x for x in sel["rows"] if x not in got]
            twice = [x for x in sel["rows"] if got.count(x) > 1]
            if miss:
                return "the plan does not run row(s) %s" % ", ".join(miss)
            # row_verdict needs exactly one component per --row: a row two chains run is an ambiguous read
            return ("the plan runs row(s) %s more than once" % ", ".join(twice)) if twice else None
    return "preview printed no plan: %s" % (out.strip().splitlines() or ["(nothing)"])[-1][:200]


def lint_line(lr, item, cid, proof, root=ROOT):
    """-> why this proof line may not be filed for (item, cid), or None. item: RoundFx.items() shape."""
    try:
        L.owed(item, cid)
    except ValueError as e:
        return "owed: %s" % e
    crit = {c["id"]: c for c in item.get("criteria") or []}[cid]
    why = L.refused_proof(lr, item.get("title") or "", crit.get("text") or "", proof)
    if why:
        return "refused: %s" % why
    why = L.owner_look(crit, proof)
    if why:
        return "owner look: %s" % why
    for p in SCRIPT.findall(proof):
        if not os.path.isfile(os.path.join(root, p)):
            return "missing script: %s" % p
    back = R.proof_lines("live-proof %s: %s" % (cid, proof))
    if back.get(cid) != proof.strip():
        return "does not parse back as live-proof %s" % cid
    return None


def lint_item(fx, lr, item_id):
    """-> [(cid, why or None)] for every live-proof line of the item's file."""
    items = {it["id"]: it for it in fx.items()}
    it = items.get(item_id)
    text = fx.proofs(item_id)
    out = []
    for cid, proof in R.proof_lines(text).items():
        if it is None:
            out.append((cid, "owed: no such built or validated item"))
            continue
        out.append((cid, lint_line(lr, it, cid, proof)))
    try:
        R.live_tiers(text)
    except ValueError as e:
        out.append(("live-tier", str(e)))
    return out


# ---------------------------------------------------------------- the owed set

def ours(text, cid):
    """True when the file's line for `cid` is one this tool wrote (its MARK comment names the clause)."""
    return any(ln.startswith("%s %s " % (MARK, cid)) for ln in (text or "").splitlines())


def owed_rows(fx, mods_of=None, mine=False):
    """-> [{item, cid, level, text, cut, title, mods}] for every owed live criterion with no proof line (the
    `no proof` set of relentless_live_round.candidates). mods_of(item) -> build mods; None reads no mods.
    mine=True also returns those whose only line is this tool's, so a rescan re-matches (and can rewrite) them."""
    out = []
    for it in fx.items():
        if it["state"] not in L.TESTABLE or not it.get("built_sha"):
            continue
        crit = {c["id"]: c for c in it.get("criteria") or []}
        owed = [c for c in it.get("outstanding") or [] if c in crit and crit[c]["level"] in L.LIVE_LEVELS]
        if not owed:
            continue
        text = fx.proofs(it["id"])
        proofs = R.proof_lines(text)
        for c in owed:
            if c in proofs and not (mine and ours(text, c)):
                continue
            out.append({"item": it["id"], "cid": c, "level": crit[c]["level"], "text": crit[c].get("text") or "",
                        "cut": bool(crit[c].get("cut")), "mods": mods_of(it) if mods_of else None})
    return out


def classify(fx, lr, rows, cats):
    """rows (owed_rows with mods) -> the snapshot entries: matched with its line, or unmatched with its reason."""
    items = {it["id"]: it for it in fx.items()}
    out = []
    for r in rows:
        e = {"item": r["item"], "cid": r["cid"], "level": r["level"], "mods": r["mods"]}
        sel, why = match(r["item"], r["text"], set(r["mods"] or ()), cats)
        if sel is None:
            e.update(status="unmatched", reason=why)
        else:
            proof = line(r["item"], sel)
            bad = lint_line(lr, items[r["item"]], r["cid"], proof) or preview_gap(sel["mod"], sel)
            if bad:
                e.update(status="unmatched", reason="lint refuses the row's line: " + bad, rows=sel["rows"],
                         mod=sel["mod"])
            else:
                e.update(status="matched", mod=sel["mod"], rows=sel["rows"], chains=sel["chains"], by=sel["by"],
                         proof=proof)
        out.append(e)
    return out


def per_mod(entries):
    """-> [(mod, owed, matched, unmatched, {reason class: n})]. A criterion counts against each build mod (or the
    matched mod), NO_MOD when it has none."""
    agg = collections.OrderedDict()
    for e in entries:
        mods = [e["mod"]] if e.get("status") == "matched" else (e.get("mods") or [NO_MOD])
        for m in mods:
            a = agg.setdefault(m, [0, 0, 0, collections.Counter()])
            a[0] += 1
            if e["status"] == "matched":
                a[1] += 1
            else:
                a[2] += 1
                a[3][e["reason"].split(":", 1)[0]] += 1
    return [(m, a[0], a[1], a[2], dict(a[3])) for m, a in sorted(agg.items())]


def tsv_text(entries):
    lines = ["mod\towed\tmatched\tunmatched\tunmatched_by_reason"]
    for m, o, mt, u, rs in per_mod(entries):
        lines.append("%s\t%d\t%d\t%d\t%s" % (m, o, mt, u, "; ".join("%s=%d" % kv for kv in sorted(rs.items()))))
    tot = (len(entries), sum(e["status"] == "matched" for e in entries), sum(e["status"] != "matched" for e in entries))
    lines.append("TOTAL (criteria, once each)\t%d\t%d\t%d\t" % tot)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- write / check

def drop_ours(text, cid):
    """`text` without this tool's block for `cid`: its MARK line, and the line straight after it only when that is
    `cid`'s own live-proof line. Another clause's line is never touched."""
    lines, keep, i = text.splitlines(), [], 0
    while i < len(lines):
        if lines[i].startswith("%s %s " % (MARK, cid)):
            nxt = R.proof_lines(lines[i + 1]) if i + 1 < len(lines) else {}
            i += 2 if cid in nxt else 1
            continue
        keep.append(lines[i])
        i += 1
    return "\n".join(keep) + ("\n" if keep else "")


def remove_line(item_id, cid, proofs_dir=PROOFS):
    """A rescan no longer matches our line for `cid`: drop it. A file left holding only `live-mods:` lines (all ours)
    is deleted. -> True when something was removed."""
    p = os.path.join(proofs_dir, item_id + ".txt")
    if not os.path.isfile(p):
        return False
    with open(p, encoding="utf-8") as f:
        old = f.read()
    if not ours(old, cid):
        return False
    new = drop_ours(old, cid)
    if not R.proof_lines(new) and all(R.LIVE_MODS.match(ln) or not ln.strip() for ln in new.splitlines()):
        os.remove(p)
    else:
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
    return True


def append_line(item_id, cid, entry, proofs_dir=PROOFS):
    p = os.path.join(proofs_dir, item_id + ".txt")
    old = ""
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as f:
            old = f.read()
    if cid in R.proof_lines(old):
        if not ours(old, cid) or R.proof_lines(old)[cid] == entry["proof"]:
            return False        # another author's line, or ours unchanged
        old = drop_ours(old, cid)
    add = []
    if entry["mod"] not in R.live_mods(old):
        add.append("live-mods: %s" % entry["mod"])
    add.append("%s %s from the %s suite (%s); generated by src/RimMandrake/rimflow/lightspeed_wire.py. The rows decide "
               "it; a row that does not cover the criterion's words makes this line wrong: delete it"
               % (MARK, cid, entry["mod"], "; ".join(entry["by"])[:300]))
    add.append("live-proof %s: %s" % (cid, entry["proof"]))
    with open(p, "w", encoding="utf-8") as f:
        f.write(old + ("" if not old or old.endswith("\n") else "\n") + "\n".join(add) + "\n")
    return True


def load_snapshot(path=SNAPSHOT):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check(fx, lr, snap, cats, tsv):
    """-> [problems]; empty holds. No git: mods come from the snapshot."""
    bad = []
    items = {it["id"]: it for it in fx.items()}
    entries = snap["entries"]
    if tsv != tsv_text(entries):
        bad.append("lightspeed_unmatched.tsv is not the snapshot's per-mod count (rerun scan)")
    mods = {(e["item"], e["cid"]): e.get("mods") or [] for e in entries}
    for e in entries:
        if e["status"] != "matched":
            if ours(fx.proofs(e["item"]), e["cid"]):
                bad.append("%s %s: unmatched now, but this tool's old line still runs (rerun write)" % (e["item"], e["cid"]))
            continue
        got = R.proof_lines(fx.proofs(e["item"])).get(e["cid"])
        if got is None:
            bad.append("%s %s: matched but has no live-proof line" % (e["item"], e["cid"]))
            continue
        it = items.get(e["item"])
        if it is not None and e["cid"] not in (it.get("outstanding") or []):
            continue        # proven (or no longer owed) since the scan: its line did its job
        why = "no such built or validated item" if it is None else lint_line(lr, it, e["cid"], got)
        if not why and got != e.get("proof"):
            why = "the line is not the one the snapshot matched (rerun scan)"
        if not why:
            why = preview_gap(e["mod"], {"chains": e.get("chains") or [], "rows": e["rows"]})
        if why:
            bad.append("%s %s: its line does not lint: %s" % (e["item"], e["cid"], why))
    for r in owed_rows(fx):
        key = (r["item"], r["cid"])
        if key not in mods:
            bad.append("%s %s: owed with no proof and not in the snapshot (rerun scan)" % key)
            continue
        sel, why = match(r["item"], r["text"], set(mods[key]), cats)
        if sel is not None and not (lint_line(lr, items[r["item"]], r["cid"], line(r["item"], sel))
                                    or preview_gap(sel["mod"], sel)):
            bad.append("%s %s: names suite row(s) %s of %s and lints, but has no line" % (key + (sel["rows"], sel["mod"])))
    return bad


def _fx():
    return R.RoundFx(seat="BENCH")


def _lr():
    with open(L.RULES, encoding="utf-8") as f:
        return L.live_rules(json.load(f))


def cmd_scan(fx, lr, write=False):
    def mods_of(it):
        try:
            return R.item_mods(fx, it["id"], it["built_sha"])
        except ValueError:
            return []
    rows = owed_rows(fx, mods_of, mine=True)
    cats = catalogues()
    entries = classify(fx, lr, rows, cats)
    wrote = dropped = 0
    if write:
        for e in entries:
            if e["status"] == "matched":
                wrote += append_line(e["item"], e["cid"], e)
            else:
                dropped += remove_line(e["item"], e["cid"])
    unreadable = sorted(m for m, c in cats.items() if "error" in c)
    snap = {"owed_no_proof_at_scan": len(rows), "suites": len(cats), "suites_unreadable": unreadable,
            "entries": entries}
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(TSV, "w", encoding="utf-8") as f:
        f.write(tsv_text(entries))
    m = sum(e["status"] == "matched" for e in entries)
    print("owed %d  matched %d  unmatched %d  lines written %d  dropped %d  suites %d (%d unreadable)"
          % (len(entries), m, len(entries) - m, wrote, dropped, len(cats), len(unreadable)))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    sub.add_parser("write")
    sub.add_parser("check")
    lp = sub.add_parser("lint")
    lp.add_argument("item")
    c = sub.add_parser("_cat")
    c.add_argument("mod_dir")
    a = p.parse_args(argv)
    if a.cmd == "_cat":
        print(json.dumps(_cat_one(a.mod_dir)))
        return 0
    fx, lr = _fx(), _lr()
    if a.cmd in ("scan", "write"):
        return cmd_scan(fx, lr, write=a.cmd == "write")
    if a.cmd == "lint":
        res = lint_item(fx, lr, a.item)
        for cid, why in res:
            print("%s %s" % (cid, "OK" if why is None else "REFUSED: " + why))
        return 1 if any(w for _, w in res) else 0
    snap = load_snapshot()
    with open(TSV, encoding="utf-8") as f:
        tsv = f.read()
    need = sorted({m for e in snap["entries"] for m in (e.get("mods") or [])} | set(mod_dirs()))
    probs = check(fx, lr, snap, catalogues(need), tsv)
    for x in probs[:40]:
        print("FAIL " + x)
    n = sum(e["status"] == "matched" for e in snap["entries"])
    print("%s: %d matched lines lint, %d unmatched filed per mod in %s" % (
        "FAIL" if probs else "PASS", n, len(snap["entries"]) - n, os.path.relpath(TSV, ROOT)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
