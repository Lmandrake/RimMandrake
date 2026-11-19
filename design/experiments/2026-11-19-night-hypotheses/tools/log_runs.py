#!/usr/bin/env python3
"""Read-only parse of the Conductor log: runs, relaunches, escalations; join each run to its transcript.

    log_runs.py <repo_root> <log.md> <since ISO Z> <out.json>

Exit 0 = measured, 3 = could not look (log unreadable or no run line since the date). VERDICT line last.
"""
import glob, json, os, re, sys
from datetime import datetime
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_rent as CR

RUN = re.compile(r"^(\S+Z) — DETACHED RUN ENDED: (\S+) on (\S+) \((\w+) seat\): (.*?), (\d+) s, ([\d,]+|UNMEASURED) weighted tokens\. ?(.*)$")
ECHO = re.compile(r"^(\S+Z) — DETACHED RUN ENDED: (\S+) on (\S+): clone ")
CONT = re.compile(r"^(\S+Z) — LEFT OPEN CONTINUE: (\S+) on (\S+) ended with work left.*?(continued as (\S+) on (\S+)|REFUSED)")
ESC = re.compile(r"^(\S+Z) — DISPATCHER ESCALATION \(([^)]*)\)")
HEAD = re.compile(r"^(\d{4}-\d\d-\d\dT\S+Z|\d{4}-\d\d-\d\d \d\d:\d\d [AP]M PST) — ([A-Z][A-Z ]+?)[:( ]")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def session_costs(repo):
    RL = CR.load_weights(repo)
    cache = {}

    def get(item):
        if item in cache:
            return cache[item]
        d = os.path.expanduser("~/.claude/projects/-home-mandrake-rm-relentless-clones-%s-det" % item.replace("_", "-"))
        sess = []
        for p in glob.glob(d + "/*.jsonl"):
            pts = []
            for model, u, t in CR.requests_of(p):
                if not t:
                    continue
                W = RL.model_weights(model)
                i, w5, w1, r, o = CR.fields(u)
                pts.append((ts(t), float(i * W["input_tokens"] + w5 * W["cache_write_5m"] + w1 * W["cache_write_1h"]
                                         + r * W["cache_read_input_tokens"] + o * W["output_tokens"])))
            if pts:
                sess.append((os.path.basename(p), pts))
        cache[item] = sess
        return sess
    return get


def main(a):
    repo, log, since, out = a[1], a[2], ts(a[3]), a[4]
    try:
        lines = open(log, errors="replace").read().split("\n")
    except OSError as e:
        print("VERDICT could-not-look: %r" % (e,))
        return 3
    runs, conts, escs, echoes, other = [], [], [], 0, {}
    for ln in lines:
        m = RUN.match(ln)
        if m and ts(m.group(1)) >= since:
            runs.append(dict(end=ts(m.group(1)), unit=m.group(2), item=m.group(3), outcome=m.group(5),
                             secs=int(m.group(6)), tokens=None if m.group(7) == "UNMEASURED" else int(m.group(7).replace(",", "")),
                             said=m.group(8)[:330]))
            continue
        m = ECHO.match(ln)
        if m and ts(m.group(1)) >= since:
            echoes += 1
            continue
        m = CONT.match(ln)
        if m and ts(m.group(1)) >= since:
            conts.append(dict(t=ts(m.group(1)), frm=m.group(2), item=m.group(3), to=m.group(5), to_item=m.group(6),
                              refused=m.group(4) == "REFUSED"))
            continue
        m = ESC.match(ln)
        if m and ts(m.group(1)) >= since:
            escs.append(dict(t=ts(m.group(1)), key=m.group(2), self_clearing="goes by itself" in ln or True and False))
            continue
        m = HEAD.match(ln)
        if m and m.group(1).endswith("Z") and ts(m.group(1)) >= since:
            other[m.group(2).strip()] = other.get(m.group(2).strip(), 0) + 1
    if not runs:
        print("VERDICT could-not-look: no run line since %s in %s" % (a[3], log))
        return 3
    # the line after an escalation carries "It goes by itself once this clears."
    txt = "\n".join(lines)
    for e in escs:
        pass
    get = session_costs(repo)
    for r in runs:
        r["cum"] = r["win"] = r["session"] = None
        for name, pts in get(r["item"]):
            if pts[0][0] - 120 <= r["end"] and pts[0][0] <= r["end"] + 5 and any(abs(t - r["end"]) < 90 or t < r["end"] for t, _ in pts) \
                    and min(abs(t - r["end"]) for t, _ in pts) < 120:
                start = r["end"] - r["secs"] - 20
                r["cum"] = sum(c for t, c in pts if t <= r["end"] + 5)
                r["win"] = sum(c for t, c in pts if start <= t <= r["end"] + 5)
                r["session"] = name
                r["session_started_before_run"] = pts[0][0] < start - 60
                break
    json.dump(dict(runs=runs, conts=conts, escs=escs, echoes=echoes, other=other), open(out, "w"))
    print("VERDICT measured: %d runs, %d relaunch lines, %d escalations, %d clone-returned echoes -> %s"
          % (len(runs), len(conts), len(escs), echoes, out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
