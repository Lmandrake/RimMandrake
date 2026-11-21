#!/usr/bin/env python3
"""Sum one Claude Code session transcript (.jsonl) into a context-burn table, without reading it whole.

Usage: burn_table.py <session.jsonl> [--top N] [--json out.json]

Per API request (deduped by message id): input, cache write, cache read, output, context size
(input + cache write + cache read) and weighted_v2 spend (role_launch.model_weights).
Per tool result: its size in characters, its tokens (characters / the session's measured chars-per-token,
calibrated from the context growth the API reported), images, and its CARRIED cost: tokens x the number of
later requests that re-read it from the cache, priced at the cache-read weight. A tool result's share of the
cache-read bill is its carried cost over the session's measured cache-read spend.
Groups: tool name; command family (a Bash command's script or program); file path for Read.
"""
import base64
import collections
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
from role_launch import model_weights  # noqa: E402


def img_dims(b64):
    try:
        raw = base64.b64decode(b64[:400] + "=" * (-len(b64[:400]) % 4))
    except Exception:
        return None
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", raw[16:24])
    if raw[:2] == b"\xff\xd8":  # JPEG: scan for SOF in the full payload
        raw = base64.b64decode(b64)
        i = 2
        while i < len(raw) - 9:
            if raw[i] != 0xFF:
                i += 1
                continue
            m = raw[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", raw[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", raw[i + 2:i + 4])[0]
    return None


def img_tokens(dims):
    """Claude vision cost: long edge scaled to <= 1568 px, tokens = w*h/750 (Anthropic docs). Unknown dims -> 1600."""
    if not dims:
        return 1600
    w, h = dims
    s = min(1.0, 1568.0 / max(w, h))
    return int(w * s * h * s / 750)


FAMILY_SKIP = {"cd", "set", "export", "eval", "source", ".", "timeout", "env", "time", "nice", "true"}


def family(cmd):
    """The script or program a Bash command runs: the first non-setup segment's python script basename or argv0."""
    for seg in re.split(r"\s*(?:&&|\|\||;|\n)\s*", cmd or ""):
        seg = seg.strip()
        if not seg or seg.startswith("#"):
            continue
        toks = seg.split()
        while toks and (re.match(r"^\w+=", toks[0]) or toks[0] in ("timeout", "env", "time", "nice")):
            toks = toks[1:]
            if toks and re.match(r"^\d+[smh]?$", toks[0]):
                toks = toks[1:]
        if not toks or toks[0] in FAMILY_SKIP:
            continue
        t0 = os.path.basename(toks[0])
        if t0.startswith("python"):
            for t in toks[1:]:
                if t in ("-", "-c") or t.startswith("<<"):
                    return "python3 (inline)"
                if not t.startswith("-"):
                    return os.path.basename(t.strip("\"'"))
            return "python3"
        return t0
    return "(setup only)"


def result_text(c):
    if isinstance(c, str):
        return c, []
    txt, imgs = [], []
    for x in c or []:
        if not isinstance(x, dict):
            continue
        if x.get("type") == "text":
            txt.append(x.get("text", ""))
        elif x.get("type") == "image":
            imgs.append(img_dims(x.get("source", {}).get("data", "")))
    return "\n".join(txt), imgs


def analyse(path):
    """-> dict: reqs (one per API request), pieces (what entered the context, when, how big), segments."""
    reqs, seen, uses, pieces, segs = [], set(), {}, [], []
    for line in open(path):
        d = json.loads(line)
        t = d.get("type")
        if t == "assistant":
            m = d.get("message", {})
            for b in m.get("content", []):
                if b.get("type") == "tool_use":
                    uses[b["id"]] = (b.get("name"), b.get("input", {}))
            mid = m.get("id")
            if mid in seen or not m.get("usage") or m.get("model") == "<synthetic>":
                continue  # "<synthetic>" turns are CLI-made, spend nothing
            seen.add(mid)
            u = m["usage"]
            cc = u.get("cache_creation") or {}
            reqs.append(dict(ts=d.get("timestamp"), model=m.get("model"),
                             inp=u.get("input_tokens", 0), cw=u.get("cache_creation_input_tokens", 0),
                             w5=cc.get("ephemeral_5m_input_tokens", 0), w1=cc.get("ephemeral_1h_input_tokens", 0),
                             cr=u.get("cache_read_input_tokens", 0), out=u.get("output_tokens", 0)))
        elif t == "user":
            c = d.get("message", {}).get("content")
            if isinstance(c, str):
                segs.append(dict(at=len(reqs), ts=d.get("timestamp"), chars=len(c)))
                pieces.append(dict(kind="prompt", key="prompt (brief or resume)", at=len(reqs), chars=len(c),
                                   imgs=[], label=c[:60]))
                continue
            for x in c or []:
                if isinstance(x, dict) and x.get("type") == "tool_result":
                    txt, imgs = result_text(x.get("content"))
                    pieces.append(dict(kind="tool", id=x.get("tool_use_id"), at=len(reqs), chars=len(txt),
                                       imgs=imgs))
                elif isinstance(x, dict) and x.get("type") == "text":
                    pieces.append(dict(kind="other", key="user text in a turn", at=len(reqs),
                                       chars=len(x.get("text", "")), imgs=[]))
        elif t == "attachment":
            n = sum(len(r.get("content", "")) for r in d.get("rendered") or [] if isinstance(r, dict))
            if n:
                pieces.append(dict(kind="other", key="attachments (system reminders)", at=len(reqs), chars=n,
                                   imgs=[]))
    n = len(reqs)
    for r in reqs:
        r["ctx"] = r["inp"] + r["cw"] + r["cr"]
        W = model_weights(r["model"])
        split = r["w5"] + r["w1"] == r["cw"]
        w5, w1 = (r["w5"], r["w1"]) if split else (0, r["cw"])
        r["wt"] = float(r["inp"] * W["input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"]
                        + r["cr"] * W["cache_read_input_tokens"] + r["out"] * W["output_tokens"])
        r["w_read"] = float(r["cr"] * W["cache_read_input_tokens"])
        r["w_write"] = float(w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"] + r["inp"] * W["input_tokens"])
        r["w_out"] = float(r["out"] * W["output_tokens"])
        r["rw"] = float(W["cache_read_input_tokens"])
        r["ww"] = float(W["cache_write_1h"])
        r["ow"] = float(W["output_tokens"])
    # reads_after[k] = sum of read weights of requests k+1 .. n-1 (a piece written at request k is read by those)
    reads_after = [0.0] * (n + 1)
    for k in range(n - 1, -1, -1):
        reads_after[k] = reads_after[k + 1] + (reqs[k + 1]["rw"] if k + 1 < n else 0.0)
    # Tokens of each piece are MEASURED from the API: the context growth between request k-1 and k, less the
    # output of k-1 (which re-enters the context), is split over the pieces that entered at k by their characters.
    # Request 0 has no predecessor: its whole context is one measured bucket ("start context").
    at = collections.defaultdict(list)
    for p in pieces:
        at[p["at"]].append(p)
    ratios = []
    for k in range(1, n):
        ps = at.get(k, [])
        ch = sum(p["chars"] for p in ps)
        delta = reqs[k]["ctx"] - reqs[k - 1]["ctx"] - reqs[k - 1]["out"]
        for p in ps:
            p["tok"] = delta * p["chars"] / ch if ch and delta > 0 else 0.0
        if ch > 2000 and delta > 0 and all(p["kind"] == "tool" and not p["imgs"] for p in ps):
            ratios.append(ch / delta)
    ratios.sort()
    cpt = ratios[len(ratios) // 2] if ratios else float("nan")
    cpt_flag = "" if ratios else " (no clean step to measure)"
    for p in at.get(0, []) + at.get(n, []):
        p["tok"] = 0.0  # request 0's pieces live in the start bucket; pieces after the last request cost nothing
    for p in pieces:
        if p["kind"] == "tool":
            name, inp = uses.get(p["id"], ("?", {}))
            p["tool"] = name
            p["key"] = family(inp.get("command", "")) if name == "Bash" else name
            p["file"] = inp.get("file_path") if name == "Read" else None
            p["label"] = (inp.get("command") or inp.get("file_path") or name or "")[:200]
        k = min(p["at"], n - 1)
        p["w_write"] = p["tok"] * reqs[k]["ww"]
        p["w_reads"] = p["tok"] * reads_after[k]
        p["w"] = p["w_write"] + p["w_reads"]
        p["later"] = n - 1 - k
    # the start context: request 0's whole context (system prompt, tools, CLAUDE.md files, skill list, the brief)
    base_tok = reqs[0]["ctx"]
    base = dict(tok=base_tok, w=base_tok * reqs[0]["ww"] + base_tok * reads_after[0],
                brief_chars=sum(p["chars"] for p in at.get(0, []) if p["kind"] == "prompt"),
                att_chars=sum(p["chars"] for p in at.get(0, []) if p["kind"] != "prompt"))
    # assistant turns: generation (output weight) + the turn re-read later (it stays in the context)
    gen = sum(r["w_out"] for r in reqs)
    turns_carry = sum(reqs[k]["out"] * (reqs[k + 1]["ww"] + reads_after[k + 1]) for k in range(n - 1))
    # rewrites: a cache write of >= 50k tokens after the first request (a resume past the cache, or a model switch)
    rewrites = [dict(at=k, ts=r["ts"], cw=r["cw"], w=r["w_write"], model=r["model"],
                     prev=reqs[k - 1]["model"]) for k, r in enumerate(reqs) if k > 0 and r["cw"] >= 50000]
    return dict(reqs=reqs, pieces=pieces, segs=segs, cpt=cpt, cpt_flag=cpt_flag, base=base, gen=gen,
                turns_carry=turns_carry, rewrites=rewrites, n=n)


def run_split(A, a, b):
    """Decompose requests a..b-1 (one run) by where the spend went, charging each piece only inside the run."""
    reqs, pieces = A["reqs"], A["pieces"]
    rs = reqs[a:b]
    total = sum(r["wt"] for r in rs)
    reads = [r["rw"] for r in rs]
    after = [sum(reads[j + 1:]) for j in range(len(rs))]
    start = rs[0]["w_write"] + rs[0]["ctx"] * after[0] + rs[0]["w_read"]  # what the run inherits or starts with
    tools = other = 0.0
    for x in pieces:
        if a < x["at"] < b:
            j = x["at"] - a
            c = x["tok"] * rs[j]["ww"] + x["tok"] * after[j]
            if x["kind"] == "tool":
                tools += c
            else:
                other += c
    gen = sum(r["w_out"] for r in rs)
    carry = sum(rs[j]["out"] * (rs[j + 1]["ww"] + after[j + 1]) for j in range(len(rs) - 1))
    return {"start context": start, "tool results": tools, "other context added": other, "output generated": gen,
            "output re-read": carry, "total": total}


BRIDGE_RE = re.compile(r"game_instance|rimflow/cli.py\"? bridge|\bbridge (who|take|release)|rimbridge|JawaBench|"
                       r"testpilot_reload|Player\.log|screenshot|gabp|concept_scenes.py\b.*--|northstar/.*\.py ")
CODE_RE = re.compile(r"\.(cs|py|xml|md|json|csproj)\b")
CAP = 8000  # characters: the size above which the levers table counts a tool result as "large"


def classify(x):
    """bridge/driver output, code or text read, or other (ledger, git, own scripts' output)."""
    lab = x.get("label") or ""
    if x.get("tool", "").startswith("mcp__rimsage") or x.get("tool") == "Read":
        return "code or text read"
    if BRIDGE_RE.search(lab):
        return "bridge or game driver output"
    fam = x.get("key")
    if fam in ("sed", "cat", "grep", "head", "tail", "awk", "wc", "for", "ls") and CODE_RE.search(lab):
        return "code or text read"
    return "other (ledger, git, own scripts and logs)"


def levers(A, a, b, role_tail_frac):
    """Run-scoped costs (requests a..b-1) of the candidate levers, in weighted_v2."""
    reqs, pieces = A["reqs"], A["pieces"]
    rs = reqs[a:b]
    reads = [r["rw"] for r in rs]
    after = [sum(reads[j + 1:]) for j in range(len(rs))]

    def cost(x, frac=1.0):
        j = x["at"] - a
        return frac * x["tok"] * (rs[j]["ww"] + after[j])
    mine = [x for x in pieces if x["kind"] == "tool" and a < x["at"] < b]
    out = collections.OrderedDict()
    cls = collections.defaultdict(float)
    for x in mine:
        cls[classify(x)] += cost(x)
    for k in sorted(cls, key=lambda k: -cls[k]):
        out["tool results: " + k] = cls[k]
    big = [x for x in mine if x["chars"] > CAP]
    out["tool results over %d characters (%d calls), whole" % (CAP, len(big))] = sum(cost(x) for x in big)
    out["  ... of which the characters past %d" % CAP] = sum(cost(x, (x["chars"] - CAP) / x["chars"]) for x in big)
    role = [x for x in mine if (x.get("file") or "").endswith("rm-testpilot.md")]
    out["the role file rm-testpilot.md, read whole"] = sum(cost(x) for x in role)
    out["  ... of which its section that repeats CLAUDE.md"] = sum(cost(x, role_tail_frac) for x in role)
    out["run total"] = sum(r["wt"] for r in rs)
    return out


CLONE_RE = re.compile(r"/home/mandrake/rm/[a-z]+/clones/[^/ ;\"']+?\.det/?|-home-mandrake-rm-[a-z]+-clones-[^/ ;\"']+")


def short(label):
    """A label without the run's clone or transcript folder (long, and not what the reader needs)."""
    return CLONE_RE.sub("<clone>/", label)


def table(path, top=12):
    A = analyse(path)
    reqs, pieces, n = A["reqs"], A["pieces"], A["n"]
    T = {k: sum(r[k] for r in reqs) for k in ("inp", "cw", "cr", "out", "wt", "w_read", "w_write", "w_out")}
    tot = T["wt"]
    out = []
    p = out.append

    def pct(x):
        return "%.1f%%" % (100.0 * x / tot)
    p("## Session `%s`" % os.path.basename(path).split(".")[0])
    p("")
    p("%d requests · models: %s · %.2f characters per token (median of measured steps)%s" % (
        n, ", ".join("%s x%d" % kv for kv in collections.Counter(r["model"] for r in reqs).items()),
        A["cpt"], A["cpt_flag"]))
    p("")
    p("Usage: input %d · cache write %d · cache read %d · output %d tokens." % (T["inp"], T["cw"], T["cr"], T["out"]))
    p("Spend %.0f weighted_v2 = cache reads %.0f (%s) + cache writes and input %.0f (%s) + output %.0f (%s)." % (
        tot, T["w_read"], pct(T["w_read"]), T["w_write"], pct(T["w_write"]), T["w_out"], pct(T["w_out"])))
    p("")
    p("| run (prompt) | start (UTC) | requests | minutes | context at start | median context | context at end | "
      "weighted_v2 |")
    p("|---|---|---:|---:|---:|---:|---:|---:|")
    segs = A["segs"] + [dict(at=n, ts=None)]
    from datetime import datetime
    for i, s in enumerate(segs[:-1]):
        a, b = s["at"], segs[i + 1]["at"]
        rs = reqs[a:b]
        if not rs:
            continue
        t0 = datetime.fromisoformat(rs[0]["ts"].replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(rs[-1]["ts"].replace("Z", "+00:00"))
        p("| %d (%d chars) | %s | %d | %.0f | %d | %d | %d | %.0f |" % (
            i + 1, s["chars"], rs[0]["ts"][11:19], len(rs), (t1 - t0).total_seconds() / 60, rs[0]["ctx"],
            sorted(r["ctx"] for r in rs)[len(rs) // 2], rs[-1]["ctx"], sum(r["wt"] for r in rs)))
    bands = collections.Counter(min(r["ctx"] // 50000, 6) for r in reqs)
    p("")
    p("Requests by context size: " + " · ".join(
        "%s %d" % ("%d-%dk" % (b * 50, b * 50 + 50) if b < 6 else "300k+", bands[b]) for b in sorted(bands))
      + " (median %d tokens)." % sorted(r["ctx"] for r in reqs)[n // 2])
    nimg = sum(len(x["imgs"]) for x in pieces)
    p("Images: %d (%.0f tokens)." % (nimg, sum(img_tokens(i) for x in pieces for i in x["imgs"])))
    p("")
    # the decomposition
    rows = [("start context: system prompt, tools, CLAUDE.md files, skill list and the brief (%d tokens, of which "
             "the brief is %d characters and the instruction attachments %d; read by every request)"
             % (A["base"]["tok"], A["base"]["brief_chars"], A["base"]["att_chars"]), A["base"]["w"])]
    kinds = collections.defaultdict(float)
    for x in pieces:
        kinds["tool results" if x["kind"] == "tool" else x["key"]] += x["w"]
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
        rows.append((k + " (written once, then re-read by each later request)", v))
    rows.append(("assistant output: generating it", A["gen"]))
    rows.append(("assistant output: re-read by each later request", A["turns_carry"]))
    for rw in A["rewrites"]:
        rows.append(("full cache rewrite at %s, %d tokens (%s -> %s)" % (rw["ts"][11:19], rw["cw"], rw["prev"],
                                                                      rw["model"]), rw["w"]))
    acc = sum(v for _, v in rows)
    p("| where the spend went | weighted_v2 | share |")
    p("|---|---:|---:|")
    for k, v in rows:
        p("| %s | %.0f | %s |" % (k, v, pct(v)))
    p("| not attributed (estimate error; negative = over-attributed) | %.0f | %s |" % (tot - acc, pct(tot - acc)))
    # per run: the watchdog's cap is per run, so the run that hit it is decomposed on its own requests
    p("")
    p("Per run (each run's spend split by where it went; a piece is charged its write and its re-reads inside the "
      "run only):")
    p("")
    cols = []
    for i, s in enumerate(A["segs"]):
        a = s["at"]
        b = A["segs"][i + 1]["at"] if i + 1 < len(A["segs"]) else n
        if a >= b:
            continue
        cols.append((i + 1, run_split(A, a, b)))
    keys = ["start context", "tool results", "other context added", "output generated", "output re-read",
            "total"]
    p("| run | " + " | ".join(keys) + " |")
    p("|---" * (len(keys) + 1) + "|")
    for i, d in cols:
        p("| %d | " % i + " | ".join("%.0f (%.0f%%)" % (d[k], 100 * d[k] / d["total"]) if k != "total" else
                                      "%.0f" % d[k] for k in keys) + " |")
    role_md = os.path.join(ROOT, ".claude", "agents", "rm-testpilot.md")
    try:
        txt = open(role_md, encoding="utf-8").read()
        i, j = txt.find("## Project rules you would otherwise get"), txt.find("## Repo hygiene")
        frac = (j - i) / len(txt) if 0 <= i < j else 0.0
    except OSError:
        frac = 0.0
    first_end = A["segs"][1]["at"] if len(A["segs"]) > 1 else n
    L = levers(A, 0, first_end, frac)
    p("")
    p("Levers in run 1 (the run the watchdog stopped), charged inside run 1:")
    p("")
    p("| lever | weighted_v2 | share of run 1 |")
    p("|---|---:|---:|")
    for k, v in L.items():
        p("| %s | %.0f | %.1f%% |" % (k, v, 100 * v / L["run total"]))
    cost_of = {}

    def group(keyf, label):
        g = collections.defaultdict(lambda: [0, 0, 0.0, 0.0, 0])
        for x in pieces:
            if x["kind"] != "tool":
                continue
            k = keyf(x)
            if k is None:
                continue
            e = g[k]
            e[0] += 1
            e[1] += x["chars"]
            e[2] += x["tok"]
            e[3] += x["w"]
            e[4] = max(e[4], x["chars"])
        cost_of[label] = g
        p("")
        p("| %s | calls | characters | tokens | largest result (chars) | weighted_v2 | share |" % label)
        p("|---|---:|---:|---:|---:|---:|---:|")
        for k, e in sorted(g.items(), key=lambda kv: -kv[1][3])[:top]:
            p("| `%s` | %d | %d | %.0f | %d | %.0f | %s |" % (short(str(k)), e[0], e[1], e[2], e[4], e[3], pct(e[3])))
    group(lambda x: x["tool"], "tool")
    group(lambda x: x["key"] if x["tool"] == "Bash" else None, "Bash command family")
    rc = collections.Counter(x["file"] for x in pieces if x.get("file"))
    cc = collections.Counter(x["label"] for x in pieces if x["kind"] == "tool" and x["tool"] == "Bash")
    p("")
    p("Re-reads: files opened by Read more than once: %s. Identical Bash commands run again: %d extra runs." % (
        ", ".join("%s x%d" % (os.path.basename(f), c) for f, c in rc.items() if c > 1) or "none",
        sum(c - 1 for c in cc.values() if c > 1)))
    p("")
    p("| largest single tool results | family | chars | tokens | later requests | share |")
    p("|---|---|---:|---:|---:|---:|")
    for x in sorted((x for x in pieces if x["kind"] == "tool"), key=lambda x: -x["w"])[:top]:
        p("| `%s` | %s | %d | %.0f | %d | %s |" % (
            short(x["label"])[:100].replace("|", "/").replace("\n", " ").replace("`", "'"), x["key"], x["chars"], x["tok"],
            x["later"], pct(x["w"])))
    return "\n".join(out), A


if __name__ == "__main__":
    args = sys.argv[1:]
    top = 12
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        del args[i:i + 2]
    for a in args:
        txt, _ = table(a, top)
        print(txt)
        print()
