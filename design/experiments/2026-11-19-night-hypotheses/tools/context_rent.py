#!/usr/bin/env python3
"""Read-only replay over Claude Code session transcripts: split each session's weighted_v2 spend into cache
reads ("context rent"), cache writes, uncached input and output; and model a cut at a context line.

    context_rent.py <repo_root> <since_epoch> <out.json> <projects_glob> [<projects_glob> ...]

Prints one verdict line last. Exit 0 = measured; 3 = could not look (no transcript matched, or the price table
could not be imported): nothing that could pass for an answer is written in that case.
"""
import glob, json, os, sys
from fractions import Fraction


def load_weights(repo):
    sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "rimflow"))
    import role_launch as RL
    return RL


def requests_of(path):
    """-> list of (model, usage) one per API request, in order. Deduplicated by message id (a request's content
    blocks are written as several lines carrying the same usage)."""
    seen, out = {}, []
    with open(path, errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "assistant" or d.get("isSidechain"):
                continue
            m = d.get("message") or {}
            u = m.get("usage")
            mid = m.get("id")
            if not isinstance(u, dict) or not mid or m.get("model") in (None, "<synthetic>"):
                continue
            if mid in seen:
                out[seen[mid]] = (m["model"], u, d.get("timestamp"))
            else:
                seen[mid] = len(out)
                out.append((m["model"], u, d.get("timestamp")))
    return out


def fields(u):
    cc = u.get("cache_creation") or {}
    w1 = cc.get("ephemeral_1h_input_tokens") or 0
    w5 = cc.get("ephemeral_5m_input_tokens") or 0
    cw = u.get("cache_creation_input_tokens") or 0
    if w1 + w5 != cw:
        w1, w5 = cw, 0
    return (u.get("input_tokens") or 0, w5, w1, u.get("cache_read_input_tokens") or 0, u.get("output_tokens") or 0)


def analyse(path, RL):
    reqs = requests_of(path)
    if not reqs:
        return None
    tot = dict(read=Fraction(0), write=Fraction(0), inp=Fraction(0), out=Fraction(0))
    ctx, rows = [], []
    for model, u, ts in reqs:
        try:
            W = RL.model_weights(model)
        except Exception:
            return {"unknown_model": model}
        i, w5, w1, r, o = fields(u)
        tot["read"] += r * W["cache_read_input_tokens"]
        tot["write"] += w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"]
        tot["inp"] += i * W["input_tokens"]
        tot["out"] += o * W["output_tokens"]
        ctx.append(i + w5 + w1 + r)
        rows.append((W, i, w5, w1, r, o))
    total = sum(tot.values())
    W0 = rows[0][0]
    base = ctx[0]
    # rulebook charge: the first request's context, re-read on every later request at the read price
    base_rent = sum(min(base, r) * W["cache_read_input_tokens"] for (W, i, w5, w1, r, o) in rows[1:])

    def cut(L, refrac, handoff=6000):
        """Model: when context passes L, restart at base+handoff+refrac*(dropped). Reads are re-priced on the
        shrunken context; each restart pays one 1h cache write of its starting context; writes, uncached input
        and output of the real session are kept as they were."""
        cost, shift, cuts = Fraction(0), 0, 0
        for k, (W, i, w5, w1, r, o) in enumerate(rows):
            c = ctx[k] - shift
            if c > L and k > 0:
                start = base + handoff + int(refrac * (c - base))
                shift = ctx[k] - start
                cuts += 1
                cost += start * W["cache_write_1h"]
                c = start
                rr = 0
            else:
                rr = max(0, r - shift)
            cost += rr * W["cache_read_input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"] \
                + i * W["input_tokens"] + o * W["output_tokens"]
        return float(cost), cuts

    res = dict(path=path, n_req=len(reqs), model=reqs[0][0], first=reqs[0][2], last=reqs[-1][2],
               total=float(total), base_ctx=base, max_ctx=max(ctx), base_rent=float(base_rent),
               **{k: float(v) for k, v in tot.items()})
    for L in (100000, 150000):
        for rf in (0, 0.25, 0.5):
            c, n = cut(L, rf)
            res["cut_%dk_r%s" % (L // 1000, rf)] = c
            res["cuts_%dk_r%s" % (L // 1000, rf)] = n
    return res


def main(a):
    if len(a) < 5:
        print(__doc__)
        return 2
    repo, since, out = a[1], float(a[2]), a[3]
    try:
        RL = load_weights(repo)
    except Exception as e:
        print("VERDICT could-not-look: price table import failed: %r" % (e,))
        return 3
    paths = sorted({p for g in a[4:] for p in glob.glob(os.path.expanduser(g)) if os.path.getmtime(p) >= since})
    rows, empty, unknown = [], 0, []
    for p in paths:
        r = analyse(p, RL)
        if r is None:
            empty += 1
        elif "unknown_model" in r:
            unknown.append((p, r["unknown_model"]))
        else:
            rows.append(r)
    if not rows:
        print("VERDICT could-not-look: %d transcript files matched, %d with no usage records, %d unknown-model"
              % (len(paths), empty, len(unknown)))
        return 3
    json.dump(dict(rows=rows, files_matched=len(paths), no_usage=empty, unknown_model=unknown), open(out, "w"))
    print("VERDICT measured: %d sessions with usage of %d files (%d no usage, %d unknown model) -> %s"
          % (len(rows), len(paths), empty, len(unknown), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
