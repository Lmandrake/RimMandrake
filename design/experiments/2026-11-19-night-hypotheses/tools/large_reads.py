#!/usr/bin/env python3
"""Read-only replay for 06-large-reads.md: for each `Read` result over a size line, how much of it does the same
session later quote, edit or name?

    large_reads.py <repo_root> <since_epoch> <until_epoch> <out.json> <glob> [<glob> ...] [--big 20000]

Files: transcripts whose mtime >= since. Lines: those with a timestamp <= until (so a session still running
later is cut where the earlier run cut it). Sidechain lines are skipped. A tool result is counted once by its
tool_use_id. Exit 0 measured, 3 could not look. VERDICT line last.

"Used", per testable line of a large read (stripped, 15+ characters, 10+ letters or digits, not repeated in the
same result): a later
assistant block of the same session (text, or any string inside a tool call's input) holds a 30-character run of
it that no other line of the same read holds (whole line when 15-29 characters), whitespace collapsed; or the line holds a name (8+ characters with `_`,
`.`, `/` or an inner capital) that no earlier content of the session held and a later assistant block does.
"""
import glob, json, os, re, sys
from datetime import datetime

NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_./-]{7,}")
LINE = re.compile(r"^\s*(\d+)\t(.*)$")
SECOND = re.compile(r"second reader|fresh reader|fresh read|read (?:it|them|each|every(?: file)?|the whole \w+)[^.\n]{0,60}"
                    r"(?:in full|to the end|whole)|in full,? to the end|READ_IN_FULL|PAGE_FRESH|read in full", re.I)
WS = re.compile(r"\s+")


def is_name(t):
    return ("_" in t or "." in t.strip(".") or "/" in t or re.search(r"[a-z][A-Z]", t)) and not t.isdigit()


def ts(d):
    try:
        return datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def rtext(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    return ""


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def session(path, until, seen_ids, RL):
    """-> dict with ordered events. Event kinds: ('out', text) assistant output; ('in', text) other content;
    ('read', info) a Read result; ('req', model, usage) one API request (first line of each message id)."""
    ev, names, mids, brief = [], {}, set(), None
    for line in open(path, errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain") or d.get("type") not in ("user", "assistant"):
            continue
        t = ts(d)
        if t is not None and t > until:
            break
        m = d.get("message") or {}
        c = m.get("content")
        if d["type"] == "assistant":
            mid = m.get("id")
            if mid and mid not in mids and isinstance(m.get("usage"), dict) and m.get("model") not in (None, "<synthetic>"):
                mids.add(mid)
                ev.append(("req", m["model"], m["usage"]))
            for b in c if isinstance(c, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    ev.append(("out", b.get("text", "")))
                elif b.get("type") == "tool_use":
                    names[b.get("id")] = (b.get("name"), b.get("input") or {})
                    ev.append(("out", "\n".join(strings(b.get("input") or {}))))
            continue
        if isinstance(c, str):
            if brief is None:
                brief = c
            ev.append(("in", c))
            continue
        for b in c if isinstance(c, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                if brief is None:
                    brief = b.get("text", "")
                ev.append(("in", b.get("text", "")))
            elif b.get("type") == "tool_result":
                tid = b.get("tool_use_id")
                if tid in seen_ids:
                    continue
                seen_ids.add(tid)
                txt = rtext(b.get("content"))
                tool, inp = names.get(tid, ("?", {}))
                if tool == "Read":
                    ev.append(("read", dict(path=inp.get("file_path", ""), partial=bool(inp.get("offset") or inp.get("limit")),
                                            text=txt, chars=len(txt))))
                else:
                    ev.append(("tool", tool, txt))
    return ev, brief or ""


def analyse(ev, brief, big, RL):
    # assistant output, indexed by event position, and shingles -> last position
    sh30, sh15, nm_last = {}, {}, {}
    for i, e in enumerate(ev):
        if e[0] != "out":
            continue
        t = WS.sub(" ", e[1])
        for k in range(len(t) - 29):
            sh30[t[k:k + 30]] = i
        for k in range(len(t) - 14):
            sh15[t[k:k + 15]] = i
        for n in NAME.findall(e[1]):
            nm_last[n] = i
    seen_names, out = set(), []
    tool_chars = 0
    pending, reqs = [], []          # reads entered since the last request: [(row, chars)], pending other chars
    pend_other = 0
    for i, e in enumerate(ev):
        kind = e[0]
        if kind == "req":
            model, u = e[1], e[2]
            cw = u.get("cache_creation_input_tokens") or 0
            ctx = cw + (u.get("cache_read_input_tokens") or 0) + (u.get("input_tokens") or 0)
            tot = sum(c for _, c in pending) + pend_other
            for row, c in pending:
                row["entry_tok"] = cw * c / tot if tot else 0
                row["model"] = model
                row["req_index"] = len(reqs)
            reqs.append((model, ctx))
            pending, pend_other = [], 0
            continue
        text = e[1] if kind in ("out", "in") else (e[2] if kind == "tool" else e[1]["text"])
        if kind == "tool":
            tool_chars += len(text)
        if kind == "read":
            r = e[1]
            tool_chars += r["chars"]
            row = dict(path=r["path"], chars=r["chars"], partial=r["partial"], big=r["chars"] > big)
            if row["big"]:
                lines = []
                for ln in r["text"].split("\n"):
                    m = LINE.match(ln)
                    lines.append(m.group(2) if m else ln)
                norm = [WS.sub(" ", x).strip() for x in lines]
                counts = {}
                for x in norm:
                    counts[x] = counts.get(x, 0) + 1
                used_idx, used_q, test_chars, used_chars = [], [], 0, 0
                inread = {}       # a 30-run counts only if it occurs in one line of this read (no shared boilerplate)
                for x in norm:
                    for g in {x[k:k + 30] for k in range(len(x) - 29)}:
                        inread[g] = inread.get(g, 0) + 1
                for j, x in enumerate(norm):
                    if len(x) < 15 or counts[x] > 1 or sum(ch.isalnum() for ch in x) < 10:   # e.g. |---|---|
                        continue
                    test_chars += len(x)
                    if len(x) >= 30:
                        hit = any(sh30.get(x[k:k + 30], -1) > i and inread[x[k:k + 30]] == 1 for k in range(len(x) - 29))
                    else:
                        hit = all(sh15.get(x[k:k + 15], -1) > i for k in range(len(x) - 14))
                    if hit:
                        used_q.append(j)
                    if not hit:
                        hit = any(nm_last.get(n, -1) > i and n not in seen_names and is_name(n) for n in NAME.findall(x))
                    if hit:
                        used_idx.append(j)
                        used_chars += len(x)
                qblocks = {j // 100 for j in used_q}
                row["used_q_chars"] = sum(len(norm[j]) for j in used_q)
                row["by_part_q_chars"] = sum(len(lines[j]) + 1 for j in range(len(lines)) if j // 100 in qblocks)
                row["used_q_sample"] = [norm[j][:120] for j in used_q[:: max(1, len(used_q) // 3)][:3]]
                row["entry_chars_check"] = r["chars"]
                blocks = {j // 100 for j in used_idx}
                block_chars = sum(len(lines[j]) + 1 for j in range(len(lines)) if j // 100 in blocks)
                row.update(test_chars=test_chars, used_chars=used_chars, used_lines=len(used_idx),
                           n_lines=len(lines), by_part_chars=block_chars,
                           design=("/design/" in r["path"] or r["path"].startswith("design/")))
                pending.append((row, r["chars"]))
            out.append(row)
        else:
            if kind != "out":
                pend_other += len(text)
        for n in NAME.findall(text):
            seen_names.add(n)
    # rent: entry tokens re-read on every later request, until the context drops by half (a compaction)
    for row in out:
        if not row.get("big") or "req_index" not in row:
            continue
        k0, n = row["req_index"], 0
        for k in range(k0 + 1, len(reqs)):
            if reqs[k][1] < 0.5 * reqs[k - 1][1]:
                break
            n += 1
        W = RL.model_weights(row["model"])
        u = None
        row["later_requests"] = n
        row["entry_w"] = float(row["entry_tok"] * W["cache_write_1h"])
        row["rent_w"] = float(row["entry_tok"] * n * W["cache_read_input_tokens"])
    second = bool(SECOND.search(brief[:20000]))
    return out, tool_chars, second


def main(a):
    if len(a) < 6:
        print(__doc__)
        return 2
    repo, since, until, outp = a[1], float(a[2]), float(a[3]), a[4]
    big = int(a[a.index("--big") + 1]) if "--big" in a else 20000
    globs = [g for g in a[5:] if not g.startswith("--") and g != str(big)]
    sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "rimflow"))
    try:
        import role_launch as RL
    except Exception as e:
        print("VERDICT could-not-look: price table: %r" % (e,))
        return 3
    paths = sorted({p for g in globs for p in glob.glob(os.path.expanduser(g)) if os.path.getmtime(p) >= since})
    seen, rows, sess, tchars = set(), [], 0, 0
    for p in paths:
        ev, brief = session(p, until, seen, RL)
        if not ev:
            continue
        r, tc, second = analyse(ev, brief, big, RL)
        if not r and not tc:
            continue
        sess += 1
        tchars += tc
        for x in r:
            x["session"] = os.path.basename(p)
            x["second_reader"] = second
        rows += r
    if not tchars:
        print("VERDICT could-not-look: %d files, no tool result before the until time" % len(paths))
        return 3
    json.dump(rows, open(outp, "w"), indent=0)
    reads = [r for r in rows]
    bigs = [r for r in rows if r["big"]]
    print("sessions %d, tool-result chars %.1fM, Read results %d (%.1fM chars, %.1f%%), large reads %d (%.1fM chars, %.1f%% of all tool text)"
          % (sess, tchars / 1e6, len(reads), sum(r["chars"] for r in reads) / 1e6,
             100 * sum(r["chars"] for r in reads) / tchars, len(bigs), sum(r["chars"] for r in bigs) / 1e6,
             100 * sum(r["chars"] for r in bigs) / tchars))
    for label, sel in (("all large", lambda r: True), ("second-reader sessions", lambda r: r["second_reader"]),
                       ("other sessions", lambda r: not r["second_reader"]),
                       ("other, design files", lambda r: not r["second_reader"] and r["design"]),
                       ("other, not design", lambda r: not r["second_reader"] and not r["design"])):
        g = [r for r in bigs if sel(r)]
        if not g:
            print("%-24s none" % label)
            continue
        tc = sum(r["test_chars"] for r in g)
        print("%-24s reads %4d  chars %5.1fM  testable %5.1fM  used %5.1f%%  reads with nothing used %3d (%.0f%%)  "
              "100-line blocks holding the used lines %5.1f%% of chars  entry %.1fM w  rent %.1fM w\n%-24s quote-only: used %5.1f%%"
              "  nothing used %3d  blocks %5.1f%%  entry tokens per char %.3f"
              % (label, len(g), sum(r["chars"] for r in g) / 1e6, tc / 1e6,
                 100 * sum(r["used_chars"] for r in g) / tc if tc else 0,
                 sum(1 for r in g if not r["used_lines"]), 100 * sum(1 for r in g if not r["used_lines"]) / len(g),
                 100 * sum(r["by_part_chars"] for r in g) / sum(r["chars"] for r in g),
                 sum(r.get("entry_w", 0) for r in g) / 1e6, sum(r.get("rent_w", 0) for r in g) / 1e6, "",
                 100 * sum(r["used_q_chars"] for r in g) / tc if tc else 0, sum(1 for r in g if not r["used_q_chars"]),
                 100 * sum(r["by_part_q_chars"] for r in g) / sum(r["chars"] for r in g),
                 sum(r.get("entry_tok", 0) for r in g) / sum(r["chars"] for r in g)))
    print("VERDICT measured: %d sessions, %d large reads" % (sess, len(bigs)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
