import json,collections,re
from datetime import datetime
P=lambda ts: datetime.fromisoformat(ts.replace('Z','+00:00')).timestamp()
import os
D=os.environ.get("SCAN_DIR","/home/mandrake/.seat-tmp/scan")+"/"
calls=[json.loads(l) for l in open(D+"calls.jsonl")]
turns=[json.loads(l) for l in open(D+"turns.jsonl")]
for c in calls: c['t']=P(c['ts'])
for t in turns: t['t']=P(t['ts'])
def kind(t):
    h=t['head']
    if 'Stop hook feedback' in h and 'run_end_wake' in h: return 'wake_run_end'
    if 'Stop hook feedback' in h: return 'stop_hook_other'
    if t['origin']=='human' and h.startswith('[RimFlow seat restart]'): return 'restart'
    if t['origin']=='human': return 'human'
    return str(t['origin'])
for t in turns: t['k']=kind(t)
# episodes: each turn -> calls until next turn in same session
bysid=collections.defaultdict(list)
for t in turns: bysid[t['sid']].append(t)
for c in calls: pass
cby=collections.defaultdict(list)
for c in calls: cby[c['sid']].append(c)
episodes=[]
for sid,ts in bysid.items():
    ts.sort(key=lambda t:t['t'])
    cs=sorted(cby[sid],key=lambda c:c['t'])
    j=0
    for i,t in enumerate(ts):
        end=ts[i+1]['t'] if i+1<len(ts) else 1e18
        ec=[c for c in cs if t['t']<=c['t']<end]
        episodes.append(dict(turn=t,calls=ec,end=end))
def bcmd(c): return c['inp'].get('command','') if c['name']=='Bash' else ''
CATS=[
 ('publish',r'\./publish|land\.sh|\./sync\b'),
 ('launch',r'detached_helper(\.py)?\s+launch'),
 ('helper_status',r'detached_helper(\.py)?\s+(status|show|tail|log|result)'),
 ('ledger_show',r'(cli\.py|rimflow)\s+show\b'),
 ('ledger_note',r'(cli\.py|rimflow)\s+note\b'),
 ('ledger_file',r'(cli\.py|rimflow)\s+(file|spawn)\b'),
 ('ledger_close',r'(cli\.py|rimflow)\s+(close|drop|supersede)\b'),
 ('ledger_wait_park',r'(cli\.py|rimflow)\s+(wait|park|rehome|home|release|claim|renew|ack)\b'),
 ('ledger_queue',r'(cli\.py|rimflow)\s+(queue|next|incidents|seat|sweep|bridge|namecheck|pilot|live|verify|list)\b'),
 ('pipe',r'\./pipe\b|control\.py'),
 ('mat_advance',r'maturation(_dispatch)?\.py'),
 ('git_check',r'\bgit\s+(-C\s+\S+\s+)?(log|show|cat-file|ls-remote|diff|status|rev-parse|branch|merge-base|fetch)\b'),
 ('owner_rulings',r'owner_rulings\.py|card_capture\.py'),
 ('handoff_wake',r'handoff\.py|seat_restart\.py'),
 ('game_acct',r'game_lock\.py|\./game\b|\./bridge\b|game_instance\.py|\./acct|account_'),
 ('selftest',r'run_selftests\.py|selftest'),
 ('file_read',r'^\s*(cat|ls|head|tail|sed|grep|rg|wc|find|stat|test|\[)\b|;\s*(cat|ls|head|tail|sed|grep|wc)\s'),
]
import re as _re
def cats(cmd):
    out=[n for n,r in CATS if _re.search(r,cmd)]
    return out or ['other']
