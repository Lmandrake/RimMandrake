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


def _last(rec):
    """A red or green record is one dict or a list of them (one per commit it ran on): the last is the one that counts."""
    if isinstance(rec, list):
        rec = rec[-1] if rec else {}
    return rec if isinstance(rec, dict) else {}


SHA_RE = re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}\b")
PATH_RE = re.compile(r"(?<![\w/.-])((?:src|design|infrastructure|skills)/[\w./-]*\w\.[A-Za-z]{1,5})\b")
# a sentence that STATES a refutation ('False theory: X', 'D7 refuted', 'was refuted', 'refuted by'), never the
# adjective ('a refuted cause')
REFUTED_RE = re.compile(r"(?i:false theor(?:y|ies)\s*:)|\b(?i:is|was|were|are|been|now)\s+(?i:refuted)\b|"
                        r"\b[A-Z][A-Za-z0-9_]*\)?\s+refuted\b|\b(?i:refuted)\s*(?:by|at|on|:)")
NOT_REFUTED_RE = re.compile(r"\b(?:not|never|un)[- ]?refuted\b", re.I)


def ticket_events(root, names):
    """-> {ticket id: [(shard path, line number, event)]} for the rimflow ledger events on those tickets, in tsn order."""
    out = {}
    for sp in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl"))):
        with open(sp, encoding="utf-8", errors="replace") as fh:
            for ln, line in enumerate(fh, 1):
                m = re.search(r'"id": ?"([A-Z0-9_]+)"', line)
                if not m or m.group(1) not in names:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("id") in names:
                    out.setdefault(e["id"], []).append((sp, ln, e))
    for v in out.values():
        v.sort(key=lambda t: t[2].get("tsn") or 0)
    return out


def _sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.;])\s+(?=[A-Z(])", " ".join(str(text or "").split())) if x.strip()]


def _words(mod):
    """CamelCase -> the spaced name ('ExplosiveKnockback' -> 'Explosive Knockback') and the item-name word."""
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", mod)
    return spaced, spaced.split()[-1].upper()


def fit(text, cap):
    """One paragraph of at most `cap` chars. A longer text keeps its leading sentences and ends with ' […]': the
    whole is in the old file every backfilled event cites, so the cut loses nothing (standard rule 3)."""
    t = " ".join(str(text or "").split())
    if len(t) <= cap:
        return t
    head = t[:cap - 4]   # cut-ok: the event cites the old file that holds the whole text
    stop = max(head.rfind(". "), head.rfind("; "))
    head = head[:stop + 1] if stop > cap // 2 else head[:head.rfind(" ")] if " " in head else head
    return head.rstrip() + " […]"


def slug(text, words=6):
    return "-".join(re.findall(r"[a-z0-9]+", str(text or "").lower())[:words]) or "untitled"


QUOTE_RE = re.compile(r"[\"“]([^\"”]{2,})[\"”]")


def _said(text):
    """His words from a line that quotes them: the quoted parts, verbatim, joined by ' · ' (the journal's own
    separator); the line itself when it quotes nothing."""
    q = QUOTE_RE.findall(text or "")
    return " · ".join(x.strip() for x in q) if q else " ".join(str(text or "").split())


def _tags(prose):
    p = prose.lower()
    out = [t for t, words in (("live", ("live", "in-game", "in game", "bridge")), ("test", ("selftest", "proof", "test")),
                              ("settings", ("setting",)), ("perf", ("perf", "tick budget")),
                              ("art", ("sprite", "texture", " art ")), ("other-mod", ("flowworks", "cauldron")))
           if any(w in p for w in words)]
    return out or ["code"]


def item_titles(root):
    """-> {item id: the one-line title its filer wrote}: rimflow's `file` events (a title is the filer's own statement
    of the item; an item's first paragraph is often shared boilerplate, e.g. 'Step N of plan.md (...)')."""
    out = {}
    for sp in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl"))):
        with open(sp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"file"' not in line or '"title"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("event") == "file" and isinstance(e.get("id"), str) and isinstance(e.get("title"), str):
                    out[e["id"]] = e["title"]
    return out


def other_mod_words(root, mod):
    """The item-name words that name ANOTHER concept mod (its squashed name, its last CamelCase word when it is 5+
    letters): an item named for another mod is that mod's, even when it cites this one as a precedent."""
    out = set()
    for m in os.listdir(os.path.join(root, "design", "concepts")) if os.path.isdir(
            os.path.join(root, "design", "concepts")) else []:
        if m == mod or not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", m):
            continue
        out.add(m.upper().replace("_", ""))
        last = _words(m)[1]
        if len(last) >= 5:
            out.add(last)
    return out


def _mine_finding(add, name, prose, titles, locked, S, src):
    """One ticket's finding.open: its filer's title, its spec as the proposed fix, its acceptance test."""
    paras = [x.strip() for x in prose.split("\n\n") if x.strip() and not x.lstrip().startswith("#")]
    m = re.search(r"^## spec\s*\n(.*?)(?=^## |\Z)", prose, re.S | re.M)
    fix = (m.group(1).strip() if m and m.group(1).strip() else
           "not written by its filer: read item:%s" % name)
    acc = re.search(r"Acceptance test:\s*(.+)", prose) or re.search(r"^## verify\s*\n(.*?)(?=^## |\Z)", prose,
                                                                     re.S | re.M)
    named_bars = [b for b in locked if re.search(r"\b%s\b" % re.escape(b), prose)][:3]
    add("finding.open", "finding:" + name, {
        "class": "polish" if re.search(r"\bpolish\b", prose, re.I) and not re.search(r"\bproblem\b", prose, re.I)
        else "problem", "bars": named_bars, "tags": [] if named_bars else _tags(prose),
        "text": fit(titles.get(name) or (paras[0] if paras else name), S["text"]),
        "proposed_fix": fit(fix, S["proposed_fix"]),
        "accept": fit(acc.group(1).strip() if acc else "none, not written at filing", S["accept"])},
        src)           # the old file first: evidence[0] is what the backfill came from


def _final_state(name, evs, S):
    """-> (kind, body, sha, ledger ref pattern) for a ticket's last state change in the rimflow ledger, or None.
    close with noCode -> finding.withdrawn (by reading, or a test when it names one); close or implemented with a sha ->
    finding.claimed_fixed, its test the last verify's command (a verify is lifecycle: it is read, never mined); a reopen
    after them, a drop or a supersede states nothing a finding can carry."""
    term, verify = None, None
    for t in evs:
        k = t[2].get("event")
        if k in ("close", "implemented", "drop", "supersede", "reopen"):
            term = t
        elif k == "verify" and t[2].get("result") == "pass":
            verify = t[2]
    if not term:
        return None
    e = term[2]
    sha = e.get("sha") if isinstance(e.get("sha"), str) and re.match(r"^[0-9a-f]{7,40}$", e.get("sha")) else None
    if e["event"] not in ("close", "implemented") or not sha:
        return None
    ref = "ledger:%%s:%d" % term[1]
    if e.get("noCode"):
        nc = str(e["noCode"])
        how = "reading+test" if re.search(r"\b(selftest|test)\b", nc, re.I) else "reading"
        return ("finding.withdrawn", {"text": fit("No defect at %s: %s" % (sha, nc), S["text"]), "how_checked": how},
                sha, ref)
    if e["event"] == "implemented":
        crit = "; ".join("%s %s" % (c.get("id"), c.get("text")) for c in e.get("criteria") or [] if isinstance(c, dict))
        text = "Implemented at %s (%s); not closed. Criteria: %s" % (sha, e.get("seat"), crit or "none recorded")
        test = crit or "none recorded with the implemented event"
    else:
        text = "Closed at %s by %s: %s" % (sha, e.get("seat"), e.get("reason") or e.get("why") or "no reason recorded")
        test = ("%s (verify pass, %s)" % (verify.get("config"), verify.get("seat")) if verify and verify.get("config")
                else "none recorded at close (live: %s)" % (e.get("live") or "-"))
    return ("finding.claimed_fixed", {"text": fit(text, S["text"]), "test": fit(test, S["test"])}, sha, ref)


def ref_path(state, tev, name):
    """The shard path of the event a final state came from (the pattern carries its line)."""
    line = int(state[3].rsplit(":", 1)[1])
    return next(t[0] for t in tev.get(name, []) if t[1] == line)


def plan(root, mod):
    """-> ([(kind, subject, body, evidence, authority, code_sha)], notes). A pure read of the old stores, mined under
    the entry standard (design/specs/2026-11-15-mod-ledger-entry-standard.md): facts, not history; one fact per entry;
    every text fitted to its cap with the old file cited for the whole; subjects from the classes; lifecycle never.
    Left out on purpose, and counted in the notes: the derived per-bar test summaries (no command, no sha), a
    checkpoint whose `next` the stores never recorded, fault status notes, live rows that decide no locked bar, his
    words already quoted under another source, and an item that only repeats a blind fault of the same name."""
    cdir = os.path.join(root, "design", "concepts", mod)
    vdir = os.path.join(cdir, "version")
    S = M.config()["standard"]["caps"]
    ev, notes, said_seen = [], [], []

    def add(kind, subject, body, evidence, authority=None, code_sha=None):
        ev.append((kind, subject, body, [e for e in evidence if e][:6], authority, code_sha))

    def his(said):
        n = " ".join(re.findall(r"[a-z0-9]+", said.lower()))
        if any(n in o or o in n for o in said_seen):
            return False
        said_seen.append(n)
        return True

    def P(path, row=None):
        rel = _rel(root, path)
        return "path:%s%s" % (rel, ("#%s" % row) if row is not None else "")

    vj = _load(os.path.join(vdir, "VERSION.json"))
    vjp = os.path.join(vdir, "VERSION.json")
    if vj:
        add("version.open", "version", {"version": vj.get("version"), "text": fit(
            "Design Version %s, %s on %s by %s; %s of %s bars met at the lock" % (
                vj.get("version"), vj.get("state"), vj.get("locked_on"), vj.get("locked_by"), vj.get("bars_met"),
                vj.get("bars_total")), S["text"])}, [P(vjp)])
        if vj.get("owner_words"):
            said = fit(_said(vj["owner_words"]), S["said"])
            his(said)
            add("decision", "version", {"said": said}, [P(vjp)], {"owner_said": said})
        if vj.get("tokens_spent"):
            add("spend", "spend", {"tokens": vj["tokens_spent"], "run": "designer and judging, to the lock"}, [P(vjp)])
    else:
        notes.append("version/VERSION.json absent")
    srp = os.path.join(vdir, "stage_record.json")
    sr = _load(srp)
    if sr:
        for i, mv in enumerate(sr.get("moves") or []):
            add("stage.accepted", "stage", {"from": mv.get("from"), "to": mv.get("to"), "by": mv.get("by"),
                                            "text": fit("%s -> %s: %s" % (mv.get("from"), mv.get("to"),
                                                                          mv.get("why") or ""), S["text"]),
                                            "as_of": mv.get("at")}, [P(srp, "moves[%d]" % i)])
        add("stage.enter", "stage", {"stage": sr.get("stage"), "text": fit("%s since %s (%s)" % (
            sr.get("stage_label"), sr.get("since"), sr.get("since_from")), S["text"]), "as_of": sr.get("since")},
            [P(srp)])
        notes.append("left out: the checkpoint (the stores never recorded a next step)")
    else:
        notes.append("version/stage_record.json absent")
    ttp = os.path.join(vdir, "test_table.json")
    tt = _load(ttp) or {}
    lbp = os.path.join(vdir, "locked_bars.json")
    lb = _load(lbp) or {}
    bars = {b["id"]: b for b in tt.get("bars") or [] if isinstance(b, dict) and b.get("id")}
    locked = list(lb.get("ids") or sorted(bars))
    decider = {}
    for bid in locked:
        b = bars.get(bid, {})
        for d in b.get("decides") or []:
            decider.setdefault(d, bid)
        add("bar.locked", "bar:" + bid, {"text": fit("%s bar from %s, proves at stage %s" % (
            b.get("kind"), b.get("source"), b.get("proves_at")), S["text"]),
            "decides": fit("; ".join(b.get("decides") or []), S["decides"])}, [P(lbp), P(ttp, "bars.%s" % bid)])
    if not lb:
        notes.append("version/locked_bars.json absent")
    if bars:
        notes.append("left out: %d derived per-bar test summaries (no command, no sha; test_table.json is the artifact)"
                     % len(locked))
    # live results: the last row per scene per visit, on the first locked bar the scene decides
    no_bar = no_sha = 0
    for vp in sorted(glob.glob(os.path.join(vdir, "in_game", "visit_*", "rows.jsonl"))):
        visit = os.path.basename(os.path.dirname(vp))
        last = {}
        for i, row in enumerate(_jsonl(vp), 1):
            if row.get("test"):
                last[row["test"]] = (i, row)
        for test, (i, row) in sorted(last.items()):
            bid = decider.get(test)
            if not bid:
                no_bar += 1
                continue
            res = row.get("verdict") if row.get("verdict") in ("PASS", "FAIL", "UNMEASURED", "UNRUN") else "UNMEASURED"
            sha = (row.get("mod_sha") or "")[:12] or None
            if not sha and res != "UNRUN":
                no_sha += 1
                continue
            add("live.run", "bar:" + bid, {"result": res, "bar": bid,
                                           "command": fit("%s · scene %s" % (row.get("command") or "?", test),
                                                          S["command"]),
                                           "text": fit("%s %s %s (runner %s)" % (visit, test, row.get("verdict"),
                                                                                row.get("runner_verdict")), S["text"])},
                [P(vp, i)], None, sha)
    if no_sha:
        notes.append("left out: %d live rows that record no mod sha (a result without the code it ran on)" % no_sha)
    if no_bar:
        notes.append("left out: %d live rows whose scene decides no locked bar (the visit rows keep them)" % no_bar)
    # blind challenge faults: the finder's smallest_fix IS the proposed fix; its criterion is the acceptance
    fault_ids, noted = set(), 0
    for fp in sorted(glob.glob(os.path.join(vdir, "blind_challenge", "cycle_*", "lane2", "faults.json"))):
        d = _load(fp)
        faults = d if isinstance(d, list) else (d or {}).get("faults") or []
        fxp = os.path.join(os.path.dirname(fp), "fixes.jsonl")
        fixes = {x.get("fault"): x for x in _jsonl(fxp)}
        for i, f in enumerate(faults):
            if not isinstance(f, dict) or not f.get("id"):
                continue
            src = [P(fp, i), "item:%s" % f["id"]]
            fix = f.get("smallest_fix") or "not written by its finder; read the fault record"
            if not isinstance(fix, str):
                fix = json.dumps(fix, ensure_ascii=False)
            if len(fix.strip()) < M.config()["proposed_fix_min_chars"]:
                fix = "%s (the finder's smallest_fix as written, a pointer rather than a fix; read the fault record)" % fix
            seen = (f.get("evidence") or [""])[0] if isinstance(f.get("evidence"), list) else f.get("evidence")
            bar = f.get("bar") if f.get("bar") in locked else None
            add("finding.open", "finding:" + f["id"], {
                "class": "polish" if str(f.get("class")).lower() == "polish" else "problem",
                "bars": [bar] if bar else [], "tags": [] if bar else _tags(json.dumps(f)),
                "text": fit(seen or f.get("criterion") or f["id"], S["text"]),
                "proposed_fix": fit(fix, S["proposed_fix"]),
                "accept": fit(f.get("criterion") or "none, the fault record names no criterion", S["accept"])}, src)
            fault_ids.add(f["id"])
            st = f.get("status") or ""
            if st.startswith("FIXED"):
                sha = (st.split() + [None])[1]
                x = fixes.get(f["id"]) or {}
                red, green = _last(x.get("red")), _last(x.get("green"))
                test = "red rc %s, green rc %s: %s" % (red.get("rc"), green.get("rc"), red.get("command") or
                                                       red.get("cmd") or green.get("command") or "see fixes.jsonl")
                add("finding.claimed_fixed", "finding:" + f["id"], {
                    "text": "fixed by the blind cycle's fixer; no later judge verdict is recorded",
                    "test": fit(test, S["test"])}, [P(fxp) if os.path.exists(fxp) else P(fp, i), "item:%s" % f["id"],
                                                    "sha:%s" % sha if sha else None], None, sha)
            elif st.startswith("NOTED"):
                noted += 1
    if noted:
        notes.append("left out: %d fault status notes (NOTED_*: the finding.open carries the fact)" % noted)
    # criterion repairs: a decision on the bar whose scene was repaired
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
        scene = re.sub(r"_\d{4}-\d\d-\d\d$", "", os.path.basename(cp))
        bid = decider.get(scene) or next((b for b in locked if b == scene), None)
        add("decision", "bar:" + bid if bid else "q:criterion-repair-" + slug(scene, 8),
            {"text": fit(txt or "criterion repair of %s (files: %s)" % (scene, ", ".join(sorted(os.listdir(cp)))),
                         S["text"])}, [P(cp)], {"why": "backfill: a criterion repair recorded in its folder"})
    # spend
    sp = os.path.join(vdir, "run_spend.jsonl")
    for i, row in enumerate(_jsonl(sp), 1):
        usd = row.get("usd") if isinstance(row.get("usd"), (int, float)) else None
        add("spend", "spend", {"usd": usd, "tokens": row.get("tokens"), "stage": row.get("stage"),
                               "run": str(row.get("unit") or i)}, [P(sp, i)])
    # his words, as the journal lists them
    jp = os.path.join(cdir, "journal.md")
    if os.path.exists(jp):
        with open(jp, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        start = next((i for i, l in enumerate(lines) if l.startswith("### His words")), None)
        bullets, cur, at = [], [], None
        if start is not None:
            for i in range(start + 1, len(lines)):
                l = lines[i]
                if l.startswith("#"):
                    break
                if l.startswith("- "):
                    if cur:
                        bullets.append((at, " ".join(cur)))
                    cur, at = [l[2:].strip()], i + 1
                elif cur and l.strip():
                    cur.append(l.strip())
            if cur:
                bullets.append((at, " ".join(cur)))
            for at, b in bullets:
                said = fit(_said(b), S["said"])
                if his(said):
                    add("decision", "q:" + slug(said), {"said": said}, ["path:%s:%d" % (_rel(root, jp), at)],
                        {"owner_said": said})
        else:
            notes.append("journal.md has no 'His words' section")
        ostart = next((i for i, l in enumerate(lines) if l.startswith("### Oddities")), None)
        odd, cur = [], None
        for i in range(ostart + 1, len(lines)) if ostart is not None else []:
            l = lines[i]
            if l.startswith("#"):
                break
            mo = re.match(r"^\d+\.\s+(.*)", l)
            if mo:
                cur = [i + 1, mo.group(1).strip()]
                odd.append(cur)
            elif cur and l.strip():
                cur[1] += " " + l.strip()
        for at, b in odd:
            head = re.match(r"\*\*(.+?)\*\*", b)
            where = re.search(r"`([^`]{2,160})`", b)
            add("trap.noted", "trap:" + slug(head.group(1) if head else b, 8),
                {"text": fit(b.replace("**", ""), S["text"]), "where": where.group(1) if where else
                 "%s:%d" % (_rel(root, jp), at), "tags": ["instrument"]}, ["path:%s:%d" % (_rel(root, jp), at)])
    # live items naming the mod: each mines to at most one finding.open (standard rule 10)
    spaced, word = _words(mod)
    words = M.config().get("backfill_item_words", {}).get(mod, [])
    items, dup_fault, elsewhere = [], 0, 0
    titles = item_titles(root)
    others = other_mod_words(root, mod) - set(words) - {word, mod.upper()}
    idir = os.path.join(root, "infrastructure", "state", "items")
    cands = [(p, False) for p in sorted(glob.glob(os.path.join(idir, "*.md")))] + \
        [(p, True) for p in sorted(glob.glob(os.path.join(idir, "closed", "*.md")))]
    tev = ticket_events(root, {os.path.basename(p)[:-3] for p, _ in cands})
    sha_ok = {}

    def resolves(sha):
        """A sha cited must resolve on origin/main (a pre-landing sha can be rewritten at landing): checked when the
        root is a git checkout, taken as written otherwise (a fixture)."""
        if not os.path.exists(os.path.join(root, ".git")):
            return True
        if sha not in sha_ok:
            sha_ok[sha] = M._sha_on(root, sha, "origin/main")
        return sha_ok[sha]

    claimed = {s for k, s, *_ in ev if k == "finding.claimed_fixed"}
    closed_unstated, sha_dead, refuted_no_sha, causes_seen = [], 0, 0, set()
    for ip, is_closed in cands:
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
        if set(name.split("_")) & set(M.config().get("backfill_item_skip_words", [])):
            continue
        if set(name.split("_")) & others and not (mod.upper() in name or set(name.split("_")) & (set(words) | {word})):
            elsewhere += 1
            continue
        state = _final_state(name, tev.get(name, []), S)
        if state and state[2] and not resolves(state[2]):
            sha_dead += 1
            state = None
        if is_closed and not state:
            closed_unstated.append(name)
            continue
        items.append(name)
        src = [P(ip), "item:" + name]
        if name in fault_ids:
            dup_fault += 1
        else:
            _mine_finding(add, name, prose, titles, locked, S, src)
        if state and "finding:" + name not in claimed:
            kind, body, sha, ref = state
            add(kind, "finding:" + name, body, src + ["sha:" + sha, ref % _rel(root, ref_path(state, tev, name))],
                None, sha)
        # refuted causes: a 'False theory:' or 'X refuted' sentence in the ticket or its notes (rule 10: every cause)
        texts = [(None, prose)] + [(t, e.get("text") or e.get("reason") or e.get("noCode") or "")
                                   for t in tev.get(name, []) for e in [t[2]] if e.get("event") in
                                   ("note", "close", "drop", "implemented")]
        for t, txt in texts:
            for sen in _sentences(txt):
                if not REFUTED_RE.search(sen) or NOT_REFUTED_RE.search(sen):
                    continue
                key = " ".join(re.findall(r"[a-z0-9]+", sen.lower()))
                if key in causes_seen:
                    continue
                causes_seen.add(key)
                shas = [x for x in SHA_RE.findall(txt) if resolves(x)] or ([state[2]] if state else [])
                if not shas:
                    refuted_no_sha += 1
                    continue
                paths = PATH_RE.findall(sen) or PATH_RE.findall(txt) or [
                    _rel(root, d) for d in [os.path.join(root, "src", "RimMandrake", mod)] if os.path.isdir(d)] or [
                    _rel(root, ip)]
                add("cause.refuted", "cause:" + slug(re.sub(r"(?i)^.*?false theor(?:y|ies):\s*", "", sen), 8),
                    {"text": fit(sen, S["text"]), "finding": "finding:" + name, "depends_on": paths[:4]},
                    src + (["ledger:%s:%d" % (_rel(root, t[0]), t[1])] if t else []), None, shas[0])
    if dup_fault:
        notes.append("left out: %d items that only repeat the blind fault of the same name" % dup_fault)
    if closed_unstated:
        notes.append("left out: %d closed tickets whose closing the ledger does not state with a sha on origin/main "
                     "(a drop, a supersede, or no close event; no sha to withdraw on), so none is left looking open"
                     % len(closed_unstated))
    if sha_dead:
        notes.append("left out: %d ticket final states whose sha does not resolve on origin/main" % sha_dead)
    if refuted_no_sha:
        notes.append("left out: %d refuted causes with no sha to pin them to" % refuted_no_sha)
    if elsewhere:
        notes.append("left out: %d items named for another mod that cite this one" % elsewhere)
    # his words and cards in the OWNER ledger shards, on the finding they bear on when it is one of ours
    mined = {s for k, s, *_ in ev if k == "finding.open"}
    mined_items = set(items)
    for sp_ in sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER*.jsonl"))):
        for i, e in enumerate(_jsonl(sp_), 1):
            blob = json.dumps(e, ensure_ascii=False)
            if mod not in blob and spaced not in blob and e.get("id") not in mined_items:
                continue
            said, card = e.get("ownerSaid"), e.get("byCard")
            if not (said or card):
                continue
            card = card if isinstance(card, str) or card is None else json.dumps(card, ensure_ascii=False)
            words_ = fit(said or card, S["said"])
            if not his(words_):
                continue
            iid = e.get("id") if isinstance(e.get("id"), str) else None
            subj = ("finding:" + iid) if iid and "finding:" + iid in mined else "q:" + slug(iid or words_, 12)
            auth = {"owner_said": words_} if said else {"by_card": words_}
            add("decision", subj, {"said": words_} if said else {"text": words_},
                ["path:%s:%d" % (_rel(root, sp_), i), ("item:" + iid) if iid else None], auth)
    return ev, notes


def run(root, mod, dry=False):
    """Write the plan through `modledger.append` (the standard's refusals included). An event the standard still
    refuses is left out and counted, never forced. A BACKFILL line already in the shard that the plan no longer holds
    is deleted (delete on sight: it failed the standard, or the old stores no longer say it); a line the plan still
    holds is kept as it is (same key, same id)."""
    ev, notes = plan(root, mod)
    if dry:
        return {"planned": len(ev), "written": 0, "already": 0, "deleted": 0, "refused": [], "near_duplicates": [],
                "notes": notes}
    version = next((b.get("version") for k, s, b, *_ in ev if k == "version.open"), None)
    want = set()
    for kind, subject, body, evidence, auth, sha in ev:
        e = {"kind": kind, "subject": subject, "version": version, "body": body, "evidence": evidence,
             "supersedes": None, "code_sha": sha, "run": None, "token": None,
             "authority": {k: v for k, v in (auth or {}).items() if v} or None}
        want.add(M.derive_key(e))
    old = [e for e in M.read(root, mod) if e.get("_shard") == W and e.get("key") not in want]
    if old:
        M.delete(root, mod, [e["id"] for e in old])
    written = already = 0
    refused, near = [], []
    for kind, subject, body, evidence, auth, sha in ev:
        try:
            _, created = M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                                  authority=auth, code_sha=sha, views=False)
        except M.Refusal as r:
            if r.field == "subject" and "looks like" in r.measured:
                near.append((subject, r.measured))
                try:
                    _, created = M.append(root, mod, W, kind, subject, body=body, version=version, evidence=evidence,
                                          authority=auth, code_sha=sha, views=False,
                                          new_subject="a separate source record (%s); the near-duplicate is listed in "
                                                      "the backfill report" % (evidence[0] if evidence else "?"))
                except M.Refusal as r2:
                    refused.append((kind, subject, str(r2)))
                    continue
            else:
                refused.append((kind, subject, str(r)))
                continue
        written += created
        already += not created
    M.write_views(root, mod)
    return {"planned": len(ev), "written": written, "already": already, "deleted": len(old), "refused": refused,
            "near_duplicates": near, "notes": notes}


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
        for kind, subject, why in res["refused"]:
            print("refused, left out: %s %s: %s" % (kind, subject, why))
        for subject, why in res["near_duplicates"]:
            print("near-duplicate, kept with --new-subject: %s" % why)
        print("backfill %s: %d planned, %d written, %d already there, %d old lines deleted, %d refused, %d "
              "near-duplicates" % (o.mod, res["planned"], res["written"], res["already"], res["deleted"],
                                   len(res["refused"]), len(res["near_duplicates"])))
    else:
        rows = compare(root, o.mod)
        for what, old, new, ok in rows:
            print("%-6s %s\n       old: %s\n       ledger: %s" % ("agree" if ok else "DIFF", what, old, new))
        print("compare %s: %d of %d agree" % (o.mod, sum(1 for r_ in rows if r_[3]), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
