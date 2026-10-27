#!/usr/bin/env python3
"""Friction census extractor: owner messages, question-card answers and selftest
Bash calls from top-level seat transcripts (Claude Code project jsonl).

Streams every file line by line with substring prefilters (the transcripts are
GBs); never loads a whole file.  Writes one JSONL of extracted events.

Usage:
  friction_census.py extract --since 2026-10-05 --out events.jsonl [DIR ...]
  friction_census.py classify events.jsonl --out classified.jsonl
"""
import argparse, glob, json, os, re, sys
from collections import Counter, defaultdict

DEFAULT_DIRS = [os.path.expanduser('~/.claude/projects/-home-mandrake-rm-bench'),
                os.path.expanduser('~/.claude/projects/-home-mandrake-rm-foundry')]
NOISE_PREFIX = ('<task-notification', '<command-', '<local-command', '<system-reminder',
                'Caveat:', '[Image', 'Base directory for this skill', 'This session is being continued',
                '<bash-', '<user-prompt-submit-hook', '[Request interrupted')
SELFTEST_RE = re.compile(r'run_selftests\.py|selftest_[a-z_]+\.py|SelfTest|selftests_nightly')
TUID_RE = re.compile(r'"tool_use_id":"(toolu_[A-Za-z0-9_]+)"')


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in content):
            return None
        return ' '.join(x.get('text', '') for x in content if isinstance(x, dict) and x.get('type') == 'text')
    return None


def extract(dirs, since, out):
    n_files = 0
    with open(out, 'w') as fo:
        for d in dirs:
            seat = 'FOUNDRY' if 'foundry' in d else 'BENCH'
            for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
                if os.path.getmtime(f) < __import__('time').mktime(__import__('time').strptime(since, '%Y-%m-%d')):
                    continue
                n_files += 1
                sess = os.path.basename(f)[:8]
                pending = {}   # tool_use_id -> (kind, ts, cmd)
                seen = set()
                with open(f, errors='replace') as fi:
                    for line in fi:
                        if '"isSidechain":true' in line[:300]:
                            continue
                        is_user = '"type":"user"' in line
                        is_att = '"queued_command"' in line
                        is_asst = '"type":"assistant"' in line and ('AskUserQuestion' in line or SELFTEST_RE.search(line))
                        has_tr = is_user and '"tool_result"' in line and pending and any(t in pending for t in TUID_RE.findall(line))
                        if not (is_user or is_att or is_asst):
                            continue
                        try:
                            d_ = json.loads(line)
                        except Exception:
                            continue
                        if d_.get('isSidechain'):
                            continue
                        ts = d_.get('timestamp', '')
                        if ts[:10] < since:
                            continue
                        if is_asst:
                            for c in d_.get('message', {}).get('content', []) or []:
                                if not isinstance(c, dict) or c.get('type') != 'tool_use':
                                    continue
                                if c.get('name') == 'AskUserQuestion':
                                    pending[c['id']] = ('ask', ts, json.dumps(c.get('input'))[:300])
                                elif c.get('name') == 'Bash':
                                    cmd = (c.get('input') or {}).get('command', '')
                                    if SELFTEST_RE.search(cmd):
                                        pending[c['id']] = ('selftest', ts, cmd[:400])
                            continue
                        if has_tr:
                            for c in d_.get('message', {}).get('content', []) or []:
                                if isinstance(c, dict) and c.get('type') == 'tool_result' and c.get('tool_use_id') in pending:
                                    kind, t0, cmd = pending.pop(c['tool_use_id'])
                                    res = c.get('content')
                                    res = res if isinstance(res, str) else ' '.join(x.get('text', '') for x in (res or []) if isinstance(x, dict))
                                    fo.write(json.dumps({'kind': kind, 'seat': seat, 'sess': sess, 'ts': t0, 'ts_end': ts,
                                                         'cmd': cmd, 'result': res[-600:], 'is_error': c.get('is_error')}) + '\n')
                            continue
                        if is_att and d_.get('type') == 'attachment':
                            a = d_.get('attachment', {})
                            if a.get('type') != 'queued_command' or (a.get('origin') or {}).get('kind') != 'human':
                                continue
                            txt = a.get('prompt') if isinstance(a.get('prompt'), str) else _text(a.get('prompt'))
                            key = (txt or '')[:80]
                            if not txt or key in seen:
                                continue
                            seen.add(key)
                            fo.write(json.dumps({'kind': 'owner', 'seat': seat, 'sess': sess, 'ts': ts, 'text': txt, 'via': 'queued'}) + '\n')
                            continue
                        if d_.get('type') != 'user' or d_.get('isMeta') or d_.get('isCompactSummary'):
                            continue
                        txt = _text(d_.get('message', {}).get('content'))
                        if not txt or not txt.strip():
                            continue
                        origin = (d_.get('origin') or {}).get('kind')
                        if origin and origin != 'human':
                            continue
                        if txt.lstrip().startswith(NOISE_PREFIX):
                            continue
                        key = txt[:80]
                        if key in seen:
                            continue
                        seen.add(key)
                        fo.write(json.dumps({'kind': 'owner', 'seat': seat, 'sess': sess, 'ts': ts, 'text': txt,
                                             'via': 'origin' if origin else 'heur'}) + '\n')
    print(f'files={n_files} out={out}')


WALL_RE = re.compile(r'PASS (\d+)/(\d+).*?\(wall ([\d.]+)s\)')


def selftests(dirs, since, out):
    """Every Bash tool call that runs a selftest, in top-level AND subagent transcripts."""
    import time
    cut = time.mktime(time.strptime(since, '%Y-%m-%d'))
    n = 0
    with open(out, 'w') as fo:
        for d in dirs:
            seat = 'FOUNDRY' if 'foundry' in d else 'BENCH'
            for f in glob.glob(os.path.join(d, '**', '*.jsonl'), recursive=True):
                if os.path.getmtime(f) < cut:
                    continue
                rel = os.path.relpath(f, d)
                sess = rel.split('/')[0][:8]
                agent = 'top' if '/' not in rel else os.path.basename(f)[:14]
                pending = {}
                with open(f, errors='replace') as fi:
                    for line in fi:
                        if '"type":"assistant"' in line and SELFTEST_RE.search(line):
                            try:
                                d_ = json.loads(line)
                            except Exception:
                                continue
                            for c in d_.get('message', {}).get('content', []) or []:
                                if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                                    inp = c.get('input') or {}
                                    cmd = inp.get('command', '')
                                    if SELFTEST_RE.search(cmd):
                                        pending[c['id']] = (d_.get('timestamp', ''), cmd[:400], bool(inp.get('run_in_background')))
                        elif pending and '"tool_result"' in line and any(t in pending for t in TUID_RE.findall(line)):
                            try:
                                d_ = json.loads(line)
                            except Exception:
                                continue
                            for c in d_.get('message', {}).get('content', []) or []:
                                if isinstance(c, dict) and c.get('type') == 'tool_result' and c.get('tool_use_id') in pending:
                                    t0, cmd, bg = pending.pop(c['tool_use_id'])
                                    if t0[:10] < since:
                                        continue
                                    res = c.get('content')
                                    res = res if isinstance(res, str) else ' '.join(x.get('text', '') for x in (res or []) if isinstance(x, dict))
                                    m = WALL_RE.search(res or '')
                                    fo.write(json.dumps({'seat': seat, 'sess': sess, 'agent': agent, 'ts': t0, 'ts_end': d_.get('timestamp', ''),
                                                         'bg': bg, 'cmd': cmd, 'wall': float(m.group(3)) if m else None,
                                                         'ntests': int(m.group(2)) if m else None, 'tail': (res or '')[-300:]}) + '\n')
                                    n += 1
    print(f'selftest calls={n} out={out}')


def ledger(root, since, now_iso):
    """Waiting/idle and rework measures from the sharded rimflow ledger."""
    from datetime import datetime, timedelta
    P = lambda t: datetime.fromisoformat(t.replace('Z', '+00:00'))
    now = P(now_iso)
    ev = []
    for f in glob.glob(os.path.join(root, 'events', '*.jsonl')):
        for l in open(f):
            try:
                d = json.loads(l)
            except Exception:
                continue
            if d.get('ts'):
                ev.append(d)
    ev.sort(key=lambda d: (d['ts'], str(d.get('tsn', ''))))
    win = [d for d in ev if d['ts'][:10] >= since]
    out = {}
    # seat idle gaps (all events by seat, window only)
    for seat in ('BENCH', 'FOUNDRY', 'OWNER', 'RUNNER'):
        ts = [P(d['ts']) for d in win if d.get('seat') == seat]
        gaps = sorted(((b - a).total_seconds() / 3600 for a, b in zip(ts, ts[1:])), reverse=True)
        out['gaps_' + seat] = {'events': len(ts), 'gaps_ge1h': sum(1 for g in gaps if g >= 1), 'gaps_ge4h': sum(1 for g in gaps if g >= 4),
                               'hours_in_ge1h_gaps': round(sum(g for g in gaps if g >= 1), 1), 'top5': [round(g, 1) for g in gaps[:5]]}
    # item lifecycle (whole history so state is right)
    st = {}; lease = {}; closes = defaultdict(int); reopen = defaultdict(int); vf = defaultdict(int); vp = defaultdict(int)
    needs_owner = {}; files = defaultdict(int); kinds = Counter()
    for d in ev:
        i = d.get('id'); e = d.get('event')
        if not i:
            continue
        inwin = d['ts'][:10] >= since
        if e == 'file':
            files[i] += 1
            if i in st and st[i][0] in ('close', 'drop') and inwin:
                kinds['refiled_same_id'] += 1
            st[i] = ('filed', d['ts'])
        elif e in ('claim', 'start'):
            if i in st and st[i][0] in ('close', 'drop', 'supersede') and inwin:
                reopen[i] += 1
            st[i] = ('doing', d['ts'])
        elif e in ('close', 'drop', 'supersede'):
            if inwin and e == 'close':
                closes[i] += 1
            st[i] = (e, d['ts']); needs_owner.pop(i, None)
        elif e == 'implemented':
            st[i] = ('implemented', d['ts'])
        elif e == 'lease':
            lease[i] = (d.get('action'), d.get('expires'), d['ts'])
        elif e == 'verify' and inwin:
            (vf if d.get('result') == 'fail' else vp)[i] += 1
        elif e == 'needs':
            if d.get('to') == 'owner':
                needs_owner[i] = d['ts']
            else:
                needs_owner.pop(i, None)
        elif e in ('unblock', 'reassign'):
            needs_owner.pop(i, None)
    doing = [i for i, (s_, t) in st.items() if s_ == 'doing']
    def leased(i):
        a = lease.get(i)
        return bool(a and a[0] in ('take', 'renew', 'extend') and a[1] and P(a[1]) > now)
    nolease = [i for i in doing if not leased(i)]
    ages = sorted(((now - P(st[i][1])).total_seconds() / 86400, i) for i in nolease)
    out['doing'] = {'n': len(doing), 'without_live_lease': len(nolease),
                    'age_days_median': round(ages[len(ages) // 2][0], 1) if ages else None,
                    'age_ge7d': sum(1 for a, _ in ages if a >= 7), 'oldest': [(round(a, 1), i) for a, i in ages[-5:]]}
    wo = sorted(((now - P(t)).total_seconds() / 86400, i) for i, t in needs_owner.items() if st.get(i, ('',))[0] not in ('close', 'drop', 'supersede'))
    out['needs_owner_open'] = {'n': len(wo), 'age_days_median': round(wo[len(wo) // 2][0], 1) if wo else None,
                               'age_ge7d': sum(1 for a, _ in wo if a >= 7), 'oldest': [(round(a, 1), i) for a, i in wo[-6:]]}
    # bridge holds
    holds = []; cur = None
    for d in ev:
        if d.get('event') != 'bridge':
            continue
        if d.get('state') == 'taken':
            cur = d
        elif d.get('state') in ('released', 'free') and cur:
            if cur['ts'][:10] >= since:
                h = (P(d['ts']) - P(cur['ts'])).total_seconds() / 3600
                busy = sum(1 for x in win if x.get('seat') == cur.get('seat') and cur['ts'] < x['ts'] < d['ts'] and x.get('event') in ('verify', 'game', 'note', 'finding'))
                holds.append((h, busy, cur.get('seat')))
            cur = None
    hs = sorted(h for h, _, _ in holds)
    out['bridge'] = {'holds': len(holds), 'hours_total': round(sum(hs), 1), 'median_h': round(hs[len(hs) // 2], 2) if hs else None,
                     'max_h': round(hs[-1], 1) if hs else None,
                     'holds_ge2h_with_<=1_game/verify/note_event': sum(1 for h, b, _ in holds if h >= 2 and b <= 1),
                     'hours_in_those': round(sum(h for h, b, _ in holds if h >= 2 and b <= 1), 1),
                     'states': Counter(d.get('state') for d in win if d.get('event') == 'bridge')}
    out['rework'] = {'items_reopened_after_close': len(reopen), 'reopen_events': sum(reopen.values()),
                     'items_closed_ge2_times': sum(1 for v in closes.values() if v >= 2), 'refiled_same_id': kinds['refiled_same_id'],
                     'items_with_verify_fail': len(vf), 'verify_fail_events': sum(vf.values()), 'verify_pass_events': sum(vp.values()),
                     'top_verify_fail': sorted(vf.items(), key=lambda x: -x[1])[:8], 'top_reopen': sorted(reopen.items(), key=lambda x: -x[1])[:8],
                     'closes_in_window': sum(closes.values()), 'files_in_window': sum(1 for d in win if d.get('event') == 'file')}
    print(json.dumps(out, indent=1, default=str))


TS_RE = re.compile(r'"timestamp":"([0-9T:.\-]+)Z"')


def turns(events_path, dirs, since, out):
    """Per owner message: how long the seat waited for him (gap since last assistant record) and how long
    it then ran on its own (until its last assistant record before his next message)."""
    from datetime import datetime
    P = lambda t: datetime.fromisoformat(t + '+00:00') if not t.endswith('+00:00') else datetime.fromisoformat(t)
    owner = defaultdict(list)
    for l in open(events_path):
        e = json.loads(l)
        if e['kind'] == 'owner':
            owner[(e['seat'], e['sess'])].append(e['ts'].rstrip('Z'))
    rows = []
    for d in dirs:
        seat = 'FOUNDRY' if 'foundry' in d else 'BENCH'
        for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
            sess = os.path.basename(f)[:8]
            own = sorted(owner.get((seat, sess), []))
            if not own:
                continue
            asst = []
            with open(f, errors='replace') as fi:
                for line in fi:
                    if '"type":"assistant"' in line and '"isSidechain":false' in line:
                        m = TS_RE.search(line)
                        if m:
                            asst.append(m.group(1))
            asst.sort()
            import bisect
            for k, t in enumerate(own):
                i = bisect.bisect_left(asst, t)
                wait = (P(t) - P(asst[i - 1])).total_seconds() if i > 0 else None
                nxt = own[k + 1] if k + 1 < len(own) else '9999'
                j = bisect.bisect_left(asst, nxt)
                run = (P(asst[j - 1]) - P(t)).total_seconds() if j - 1 >= i and j > 0 else 0.0
                rows.append({'seat': seat, 'sess': sess, 'ts': t, 'wait_s': wait, 'run_s': max(run, 0.0)})
    json.dump(rows, open(out, 'w'))
    runs = sorted(r['run_s'] for r in rows)
    waits = sorted(r['wait_s'] for r in rows if r['wait_s'] is not None)
    q = lambda v, p: round(v[int(p * (len(v) - 1))] / 60, 1)
    print(f"owner msgs={len(rows)} run-after-msg min: med {q(runs,.5)} p75 {q(runs,.75)} p90 {q(runs,.9)}; "
          f"share <5min {sum(r<300 for r in runs)/len(runs):.2f}; share >=60min {sum(r>=3600 for r in runs)/len(runs):.2f}")
    print(f"seat-waiting-for-owner min: med {q(waits,.5)} p90 {q(waits,.9)}; total h in waits<=8h {sum(w for w in waits if w<=28800)/3600:.1f}")


# Ordered rules; first hit wins.  Category letters per the census brief.
RULES = [
    ('g', r"\b(wake (bench|foundry|up)|^wake\b|handoff|hand off|subagents?|afk|going to bed|orchestrat|token reset|account token|light orchestrator|night shift)"),
    ('b', r"(^\s*(continue|go|proceed|go ahead|resume|keep going|carry on)\b|keep (going|working)|why (is|are|does|do|did)[^?]*(tak|slow|long|stuck|wait|still)|taking so long|so long\?|it'?s stuck|\bstuck\b|are you (done|still)|why did you stop|you stopped|\bhung\b|frozen|still running|interrupted)"),
    ('c', r"\b(that'?s (not|wrong)|wrong|incorrect|not true|you (said|claimed)|that is false|did(n'?t| not) (work|happen)|isn'?t (true|right)|still (broken|wrong|there|shows?|missing)|nope|not what i|ceremony|makes me (very )?nervous|trouble imagining|are you sure|really\?)"),
    ('d', r"\b(again|i (already|told|said)|as i said|i'?ve (said|told)|remember (we|that|i)|we (decided|agreed)|how many times|once more|already (ruled|decided|told|said|recommended)|were supposed to|no longer|never have to|stop (validating|doing|asking))"),
    ('h', r"\b(question cards?\b.*\?|any .* for me|rimpulse|to rule|sheets? (ready|laying|for me)|status\b|where (is|are)|what happened|any progress|re-?open)"),
    ('f', r"\b(bridge|game|loaded|restart|colony|save ?game|main menu|crash(ed)?|in[- ]game|player\.log)"),
    ('i', r"\b(screenshot|sprite|texture|looks? (strange|wrong|horrible|bad|off|weird)|redraw|perspective|graphics?|\[image)"),
    ('e', r"(^\s*(yes|ok|okay|sure|good|great|lgtm)\b|\b(approve|accept|enact|keep|cut|pick|picked|finished the .* sheet|go with|i like|i prefer|ship it|looks? (great|good)))"),
    ('a', r"."),
]
RULES_C = [(k, re.compile(p, re.I)) for k, p in RULES]


def classify(src, out):
    cnt = Counter()
    with open(src) as fi, open(out, 'w') as fo:
        for line in fi:
            e = json.loads(line)
            if e['kind'] != 'owner':
                continue
            t = e['text'].strip()
            for k, rx in RULES_C:
                if rx.search(t[:600]):
                    e['cat'] = k
                    break
            cnt[e['cat']] += 1
            fo.write(json.dumps(e) + '\n')
    tot = sum(cnt.values())
    for k in 'abcdefghi':
        print(k, cnt[k], f'{100*cnt[k]/max(tot,1):.1f}%')
    print('total', tot)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    e = sp.add_parser('extract'); e.add_argument('dirs', nargs='*'); e.add_argument('--since', required=True); e.add_argument('--out', required=True)
    t = sp.add_parser('selftests'); t.add_argument('dirs', nargs='*'); t.add_argument('--since', required=True); t.add_argument('--out', required=True)
    g = sp.add_parser('ledger'); g.add_argument('--root', default='infrastructure/state/ledger'); g.add_argument('--since', required=True); g.add_argument('--now', required=True)
    u = sp.add_parser('turns'); u.add_argument('events'); u.add_argument('dirs', nargs='*'); u.add_argument('--since', default=''); u.add_argument('--out', required=True)
    c = sp.add_parser('classify'); c.add_argument('src'); c.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'extract':
        extract(a.dirs or DEFAULT_DIRS, a.since, a.out)
    elif a.cmd == 'turns':
        turns(a.events, a.dirs or DEFAULT_DIRS, a.since, a.out)
    elif a.cmd == 'ledger':
        ledger(a.root, a.since, a.now)
    elif a.cmd == 'selftests':
        selftests(a.dirs or DEFAULT_DIRS, a.since, a.out)
    else:
        classify(a.src, a.out)


if __name__ == '__main__':
    main()
