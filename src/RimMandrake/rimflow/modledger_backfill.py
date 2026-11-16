#!/usr/bin/env python3
"""modledger_backfill.py — import one mod's state from today's stores into its mod ledger, in SHADOW mode.

Spec design/specs/2026-11-15-holder-pipeline-fusion.md §3.8 steps 2-3; plan step 3. Every event is written by the
`BACKFILL` writer and cites the old file (and the row or line) it came from. Nothing old is redirected, archived or
deleted: the views are generated beside the old files, and `compare` prints where the old files disagree with each
other or with the ledger.

    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback        # writes the ledger
    python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback --dry  # counts only
    python3 src/RimMandrake/rimflow/modledger_backfill.py compare --mod ExplosiveKnockback    # shadow disagreements

Stores read (each optional; a missing one is said, never guessed): version/VERSION.json, version/stage_record.json,
version/locked_bars.json, version/test_table.json, version/in_game/visit_*/rows.jsonl,
version/blind_challenge/cycle_*/lane2/faults.json, version/criterion_repairs/*/, version/run_spend.jsonl,
journal.md ("His words on this mod"), the live rimflow items naming the mod, and the OWNER ledger shards' events naming
the mod that carry his words (ownerSaid) or a card (byCard). Run twice, it writes nothing new (idempotent keys).
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402

W = "BACKFILL"


def _rel(root, p):
    return os.path.relpath(p, root)


def _load(p):
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _jsonl(p):
    out = []
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def _words(mod):
    """CamelCase -> the spaced name ('ExplosiveKnockback' -> 'Explosive Knockback') and the item-name word."""
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", mod)
    return spaced, spaced.split()[-1].upper()


def plan(root, mod):
    """-> ([(kind, subject, body, evidence, authority)], notes). Pure read of the old stores; writes nothing."""
    cdir = os.path.join(root, "design", "concepts", mod)
    vdir = os.path.join(cdir, "version")
    ev, notes = [], []

    def add(kind, subject, body, evidence, authority=None):
        ev.append((kind, subject, body, evidence, authority))

    vj = _load(os.path.join(vdir, "VERSION.json"))
    if vj:
        p = _rel(root, os.path.join(vdir, "VERSION.json"))
        add("version.open", "version", {"version": vj.get("version"), "text": "Design Version %s, %s on %s by %s; "
                                        "%s of %s bars met at the lock" % (vj.get("version"), vj.get("state"),
                                                                          vj.get("locked_on"), vj.get("locked_by"),
                                                                          vj.get("bars_met"), vj.get("bars_total")),
                                        "as_of": vj.get("locked_on")}, [p])
        if vj.get("owner_words"):
            add("decision", "version_lock", {"text": vj["owner_words"], "as_of": vj.get("locked_on")}, [p],
                {"owner_said": vj["owner_words"]})
        if vj.get("tokens_spent"):
            add("spend", "designer_tokens", {"tokens": vj["tokens_spent"], "usd": None,
                                             "text": "Designer and judging tokens to the lock (%s)"
                                             % "; ".join(vj.get("caveats") or [])}, [p])
    else:
        notes.append("version/VERSION.json absent")
    sr = _load(os.path.join(vdir, "stage_record.json"))
    if sr:
        p = _rel(root, os.path.join(vdir, "stage_record.json"))
        for i, mv in enumerate(sr.get("moves") or []):
            add("stage.accepted", "stage", {"from": mv.get("from"), "to": mv.get("to"), "by": mv.get("by"),
                                            "text": mv.get("why") or "", "as_of": mv.get("at")},
                ["%s#moves[%d]" % (p, i)])
        add("stage.enter", "stage", {"stage": sr.get("stage"), "text": "%s since %s (%s)"
                                     % (sr.get("stage_label"), sr.get("since"), sr.get("since_from")),
                                     "as_of": sr.get("since")}, [p])
        last = (sr.get("moves") or [{}])[-1]
        add("session.checkpoint", "checkpoint",
            {"done": "last stage move (%s, %s -> %s): %s" % (last.get("at"), last.get("from"), last.get("to"),
                                                            last.get("why")),
             "next": "not recorded in the old stores (journal.md 'Waiting on' reads 'not yet written for this stage')",
             "ruled_out": "none recorded in a readable store", "as_of": last.get("at")}, [p])
    else:
        notes.append("version/stage_record.json absent")
    tt = _load(os.path.join(vdir, "test_table.json")) or {}
    lb = _load(os.path.join(vdir, "locked_bars.json")) or {}
    ttp = _rel(root, os.path.join(vdir, "test_table.json"))
    bars = {b["id"]: b for b in tt.get("bars") or [] if isinstance(b, dict) and b.get("id")}
    for bid in lb.get("ids") or sorted(bars):
        b = bars.get(bid, {})
        add("bar.locked", bid, {"text": "%s bar from %s, proves at stage %s" % (b.get("kind"), b.get("source"),
                                                                                b.get("proves_at")),
                                "decides": b.get("decides") or []},
            [_rel(root, os.path.join(vdir, "locked_bars.json")), "%s#bars.%s" % (ttp, bid)])
    if not lb:
        notes.append("version/locked_bars.json absent")
    # live results, last row per scene per visit
    live = {}
    for vp in sorted(glob.glob(os.path.join(vdir, "in_game", "visit_*", "rows.jsonl"))):
        visit = os.path.basename(os.path.dirname(vp))
        last = {}
        for i, row in enumerate(_jsonl(vp), 1):
            if row.get("test"):
                last[row["test"]] = (i, row)
        for test, (i, row) in sorted(last.items()):
            live[test] = (visit, row.get("verdict"))
            add("live.run", test, {"result": row.get("verdict"), "visit": visit,
                                   "text": "%s %s (runner %s)" % (visit, row.get("verdict"), row.get("runner_verdict"))},
                ["%s:%d" % (_rel(root, vp), i)], None)
    for bid in lb.get("ids") or sorted(bars):
        b = bars.get(bid, {})
        dec = [d for d in b.get("decides") or [] if d in live]
        if dec:
            ok = sum(1 for d in dec if live[d][1] == "PASS")
            res = "live %d of %d deciding scenes PASS (%s)" % (ok, len(dec), live[dec[0]][0])
        else:
            res = "offline green today" if b.get("offline_green_today") else "no deciding run green"
        add("test.run", "bar:" + bid, {"bar": bid, "result": res, "text": "from %s and the visit rows"
                                       % ttp, "as_of": tt.get("made")}, ["%s#bars.%s" % (ttp, bid)])
    # blind challenge faults: the finder's smallest_fix IS the proposed fix
    for fp in sorted(glob.glob(os.path.join(vdir, "blind_challenge", "cycle_*", "lane2", "faults.json"))):
        d = _load(fp)
        faults = d if isinstance(d, list) else (d or {}).get("faults") or []
        cyc = fp.split(os.sep)[-3]
        for i, f in enumerate(faults):
            if not isinstance(f, dict) or not f.get("id"):
                continue
            src = ["%s#%d" % (_rel(root, fp), i)]
            fix = f.get("smallest_fix") or "not written by its finder (backfill; see the fault record)"
            if not isinstance(fix, str):
                fix = json.dumps(fix, ensure_ascii=False)
            if len(fix.strip()) < M.config()["proposed_fix_min_chars"]:
                fix = "%s (the finder's smallest_fix as written, a pointer rather than a fix; read the fault record)" % fix
            ev_txt = (f.get("evidence") or [""])[0] if isinstance(f.get("evidence"), list) else f.get("evidence")
            add("finding.open", f["id"], {"text": "%s [%s, bar %s, %s] %s" % (f.get("criterion") or "",
                                                                                f.get("class"), f.get("bar"), cyc,
                                                                                ev_txt or ""),
                                          "proposed_fix": fix, "cycle": cyc, "class": f.get("class"),
                                          "bar": f.get("bar")}, src)
            st = f.get("status") or ""
            if st.startswith("FIXED"):
                add("finding.claimed_fixed", f["id"], {"text": "%s (fixed by the blind cycle's fixer under the "
                                                       "11-13 rule; no later judge verdict is recorded)" % st},
                    src)
            elif st.startswith("NOTED"):
                add("note", f["id"], {"text": "fault status %s" % st}, src)
    # criterion repairs
    for cp in sorted(glob.glob(os.path.join(vdir, "criterion_repairs", "*"))):
        if not os.path.isdir(cp):
            continue
        txt = ""
        for name in ("RECERTIFY.md", "FINDINGS.md"):
            q = os.path.join(cp, name)
            if os.path.exists(q):
                with open(q, encoding="utf-8") as fh:
                    paras = [x.strip() for x in fh.read().split("\n\n") if x.strip() and not x.startswith("#")]
                txt = paras[0] if paras else ""
                break
        add("decision", "criterion_repair:" + os.path.basename(cp),
            {"text": txt or "criterion repair folder (files: %s)" % ", ".join(sorted(os.listdir(cp)))},
            [_rel(root, cp)], {"why": "backfill: a criterion repair recorded in its folder"})
    # spend
    sp = os.path.join(vdir, "run_spend.jsonl")
    for i, row in enumerate(_jsonl(sp), 1):
        usd = row.get("usd") if isinstance(row.get("usd"), (int, float)) else None
        add("spend", "run:%s" % (row.get("unit") or i), {"usd": usd, "tokens": row.get("tokens"), "stage":
                                                         row.get("stage"), "text": "%s tokens, usd %s"
                                                         % (row.get("tokens"), row.get("usd"))},
            ["%s:%d" % (_rel(root, sp), i)])
    # his words, as the journal lists them
    jp = os.path.join(cdir, "journal.md")
    if os.path.exists(jp):
        with open(jp, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        start = next((i for i, l in enumerate(lines) if l.startswith("### His words")), None)
        if start is not None:
            cur, at = [], None
            for i in range(start + 1, len(lines)):
                l = lines[i]
                if l.startswith("#"):
                    break
                if l.startswith("- "):
                    if cur:
                        add("decision", "his_words:%d" % at, {"text": " ".join(cur)},
                            ["%s:%d" % (_rel(root, jp), at)], {"owner_said": " ".join(cur)})
                    cur, at = [l[2:].strip()], i + 1
                elif cur and l.strip():
                    cur.append(l.strip())
            if cur:
                add("decision", "his_words:%d" % at, {"text": " ".join(cur)}, ["%s:%d" % (_rel(root, jp), at)],
                    {"owner_said": " ".join(cur)})
        else:
            notes.append("journal.md has no 'His words' section")
    # live items naming the mod
    spaced, word = _words(mod)
    words = M.config().get("backfill_item_words", {}).get(mod, [])
    for ip in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "items", "*.md"))):
        name = os.path.basename(ip)[:-3]
        with open(ip, encoding="utf-8") as fh:
            prose = fh.read()
        head = "\n".join(prose.split("\n")[:6])
        named = mod.upper() in name or mod in head or spaced in head
        # a short word (KNOCKBACK, SLACK) alone is too wide (SLACK also names SlackMaster work): it counts only when the
        # mod's configured item words list it, or the mod is named somewhere in the prose
        if not named and not (set(name.split("_")) & set(words) or
                              (word in name.split("_") and (mod in prose or spaced in prose))):
            continue
        paras = [x.strip() for x in prose.split("\n\n") if x.strip() and not x.lstrip().startswith("#")]
        m = re.search(r"^## spec\s*\n(.*?)(?=^## |\Z)", prose, re.S | re.M)
        fix = (m.group(1).strip() if m and m.group(1).strip() else
               "not written by its filer (backfilled from the item prose; read the item)")
        add("finding.open", name, {"text": paras[0] if paras else name, "proposed_fix": " ".join(fix.split()),
                                   "source": "rimflow item"}, [_rel(root, ip)])
    # his words and cards in the OWNER ledger shards
    for sp_ in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER*.jsonl"))):
        for i, e in enumerate(_jsonl(sp_), 1):
            blob = json.dumps(e, ensure_ascii=False)
            if mod not in blob and spaced not in blob:
                continue
            said, card = e.get("ownerSaid"), e.get("byCard")
            if not (said or card):
                continue
            auth = {"owner_said": said} if said else {"by_card": card if isinstance(card, str) else json.dumps(card)}
            add("decision", "owner:%s" % (e.get("tsn") or e.get("ts")), {"text": said or (card if isinstance(card, str)
                                                                                         else json.dumps(card)),
                                                                        "item": e.get("id"), "as_of": e.get("ts")},
                ["%s:%d" % (_rel(root, sp_), i)], auth)
    return ev, notes


def run(root, mod, dry=False):
    ev, notes = plan(root, mod)
    if dry:
        return {"planned": len(ev), "written": 0, "already": 0, "notes": notes}
    version = None
    for kind, subject, body, evidence, auth in ev:
        if kind == "version.open":
            version = body.get("version")
            break
    written = already = 0
    for kind, subject, body, evidence, auth in ev:
        _, created = M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                              authority=auth, views=False)
        written += created
        already += not created
    M.write_views(root, mod)
    return {"planned": len(ev), "written": written, "already": already, "notes": notes}


def compare(root, mod):
    """-> [(what, old store says, ledger says, agree?)]: the shadow check the cutover waits on."""
    cdir = os.path.join(root, "design", "concepts", mod)
    st = M.reduce(M.read(root, mod))
    out = []
    sr = _load(os.path.join(cdir, "version", "stage_record.json")) or {}
    out.append(("stage (version/stage_record.json)", sr.get("stage"), st["stage"], sr.get("stage") == st["stage"]))
    sj = _load(os.path.join(cdir, "stage.json")) or {}
    out.append(("stage.json key 'stage' (the Designer's inner step, a homonym)", sj.get("stage"), st["stage"],
                sj.get("stage") == st["stage"]))
    out.append(("stage.json blocked_on", sj.get("blocked_on") or "none", "version %s, stage %s"
                % (st["version"], st["stage"]), not sj.get("blocked_on")))
    jp = os.path.join(cdir, "journal.md")
    jt = open(jp, encoding="utf-8").read() if os.path.exists(jp) else ""
    m = re.search(r"\*\*Stage now:\*\* (.*)", jt)
    out.append(("journal.md 'Stage now'", m.group(1).strip() if m else None, st["stage"],
                bool(m) and (st["stage"] or "").replace("_", " ") in m.group(1).lower().replace("-", " ")))
    unrun = "Every in-game scene is UNRUN" in jt
    lives = [t for t in st["tests"] if t["kind"] == "live.run"]
    out.append(("journal.md stands: in-game scenes", "every scene UNRUN" if unrun else "not claimed UNRUN",
                "%d live rows backfilled from the visit records" % len(lives), not (unrun and lives)))
    wait = re.search(r"\*\*Waiting on:\*\* (.*)", jt)
    out.append(("journal.md 'Waiting on'", wait.group(1).strip() if wait else None,
                "checkpoint next: %s" % ((st["checkpoint"] or {}).get("next")),
                bool(wait) and "not yet written" not in wait.group(1)))
    vj = _load(os.path.join(cdir, "version", "VERSION.json")) or {}
    out.append(("bars_total (VERSION.json)", vj.get("bars_total"), len(st["bars"]), vj.get("bars_total") ==
                len(st["bars"])))
    claimed = [k for k, f in st["findings"].items() if f["status"] == "claimed_fixed"]
    out.append(("blind faults marked FIXED in faults.json", len(claimed), "claimed_fixed, no judge verdict", False
                if claimed else True))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="verb", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mod", required=True)
    r.add_argument("--dry", action="store_true")
    c = sub.add_parser("compare")
    c.add_argument("--mod", required=True)
    o = ap.parse_args(argv)
    root = o.root or M.default_root()
    if o.verb == "run":
        res = run(root, o.mod, o.dry)
        for n in res["notes"]:
            print("note: " + n)
        print("backfill %s: %d planned, %d written, %d already there" % (o.mod, res["planned"], res["written"],
                                                                          res["already"]))
    else:
        rows = compare(root, o.mod)
        for what, old, new, ok in rows:
            print("%-6s %s\n       old: %s\n       ledger: %s" % ("agree" if ok else "DIFF", what, old, new))
        print("compare %s: %d of %d agree" % (o.mod, sum(1 for r_ in rows if r_[3]), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
