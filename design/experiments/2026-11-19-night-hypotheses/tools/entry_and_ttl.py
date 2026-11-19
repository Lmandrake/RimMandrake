#!/usr/bin/env python3
"""Read-only, over the same transcripts as context_rent.py. Per session: (a) what the FIRST request wrote to the
cache and what it read from it (is the starting context shared between runs?); (b) a model of the same session
priced with a 5-minute cache life: every cache write at the 5m price, and every request that follows a silence
longer than 300 s re-writes its whole context instead of reading it.

    entry_and_ttl.py <repo_root> <since_epoch> <out.json> <projects_glob> [...]

Exit 0 = measured; 3 = could not look. Prints one VERDICT line last.
"""
import glob, json, os, sys
from datetime import datetime
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_rent as CR


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def analyse(path, RL):
    reqs = CR.requests_of(path)
    if not reqs:
        return None
    real = alt = Fraction(0)
    gaps, prev, gap_rewrite = 0, None, Fraction(0)
    for model, u, t in reqs:
        W = RL.model_weights(model)
        i, w5, w1, r, o = CR.fields(u)
        real += i * W["input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"] \
            + r * W["cache_read_input_tokens"] + o * W["output_tokens"]
        now = ts(t) if t else None
        miss = prev is not None and now is not None and now - prev > 300
        if miss:
            gaps += 1
            gap_rewrite += r * (W["cache_write_5m"] - W["cache_read_input_tokens"])
        alt += i * W["input_tokens"] + (w5 + w1) * W["cache_write_5m"] + o * W["output_tokens"] \
            + r * (W["cache_write_5m"] if miss else W["cache_read_input_tokens"])
        prev = now if now is not None else prev
    m0, u0, _ = reqs[0]
    W0 = RL.model_weights(m0)
    i, w5, w1, r, o = CR.fields(u0)
    return dict(path=path, model=m0, n_req=len(reqs), real=float(real), ttl5=float(alt), gaps_over_5m=gaps,
                gap_rewrite=float(gap_rewrite), first_write_tok=w5 + w1, first_read_tok=r,
                first_write_w=float(w5 * W0["cache_write_5m"] + w1 * W0["cache_write_1h"]),
                first_as_read_w=float((w5 + w1) * W0["cache_read_input_tokens"]))


def main(a):
    repo, since, out = a[1], float(a[2]), a[3]
    try:
        RL = CR.load_weights(repo)
    except Exception as e:
        print("VERDICT could-not-look: price table import failed: %r" % (e,))
        return 3
    paths = sorted({p for g in a[4:] for p in glob.glob(os.path.expanduser(g)) if os.path.getmtime(p) >= since})
    rows = [r for r in (analyse(p, RL) for p in paths) if r]
    if not rows:
        print("VERDICT could-not-look: %d files matched, none with usage" % len(paths))
        return 3
    json.dump(rows, open(out, "w"))
    print("VERDICT measured: %d sessions of %d files -> %s" % (len(rows), len(paths), out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
