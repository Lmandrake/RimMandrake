#!/usr/bin/env python3
"""host_facts.py - what SteveDesktop has, read once an hour over ssh, kept with its age (RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS).

  read(path, now) -> {"age_s", "stale", "facts"}   no file, unreadable file, or older than MAX_AGE_S: stale, never facts
  lacks(need, facts, stale) -> [(kind, name, word)]  word is "absent" (looked, not there) or "could not look" (stale/no facts)
  collect(run) -> facts                              `run(cmd) -> stdout`; raises on ssh failure (nothing is written)
  logins_low(facts, now, days=3) -> [account]        logins with under `days` left
CLI: host_facts.py refresh | show   (exit 0 read, 4 could not look)
"""
import json
import os
import subprocess
import sys
import time

MAX_AGE_S = 2 * 3600
PATH = os.path.join(os.environ.get("TESTQ_HOME") or os.path.expanduser("~/.testq"), "host_facts.json")
KINDS = ("mods", "saves", "python", "companion")

PROBE = r"""
import json,os,glob,time,shutil,importlib.util
mods=os.environ.get('RM_MODS') or r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods'
out={'mods':[],'saves':[],'python':{},'companions':[],'free_gb':None,'logins':{}}
for d in glob.glob(os.path.join(mods,'*','About','About.xml')):
    import re
    m=re.search(r'<packageId>([^<]+)</packageId>',open(d,encoding='utf-8',errors='replace').read())
    if m: out['mods'].append(m.group(1).strip().lower())
for p in glob.glob(os.path.expanduser(r'~\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\*.rws')):
    out['saves'].append(os.path.basename(p)[:-4])
for mod in ('numpy','lxml','PIL','yaml'):
    out['python'][mod]=importlib.util.find_spec(mod) is not None
out['free_gb']=shutil.disk_usage('C:\\').free//2**30
for p in glob.glob(os.path.expanduser(r'~\.claude-accounts\*\.credentials.json')):
    try:
        e=json.load(open(p))['claudeAiOauth']['expiresAt']/1000
        out['logins'][os.path.basename(os.path.dirname(p))]=int(e-time.time())
    except Exception: pass
print(json.dumps(out))
"""


def read(path=PATH, now=None):
    now = time.time() if now is None else now
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        at, facts = float(d["at"]), d["facts"]
    except (OSError, ValueError, KeyError, TypeError):
        return {"age_s": None, "stale": True, "facts": None}
    age = now - at
    return {"age_s": age, "stale": age > MAX_AGE_S or age < 0, "facts": facts}


def lacks(need, facts, stale):
    out = []
    for kind in KINDS:
        want = need.get(kind)
        if not want:
            continue
        want = [want] if isinstance(want, str) else list(want)
        for name in want:
            if stale or not isinstance(facts, dict):
                out.append((kind, name, "could not look"))
                continue
            if kind == "python":
                have = facts.get("python", {}).get(name) is True
            elif kind == "companion":
                have = name in facts.get("companions", [])
            else:
                have = name in facts.get(kind, [])
            if not have:
                out.append((kind, name, "absent"))
    return out


def logins_low(facts, days=3):
    return sorted(a for a, s in (facts or {}).get("logins", {}).items() if s < days * 86400)


def collect(run):
    return json.loads(run(PROBE).strip().splitlines()[-1])


def refresh(path=PATH, run=None, now=None):
    if run is None:
        host = os.environ.get("TESTQ_STEVE_HOST", "stevedesktop")
        def run(code):
            r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, "python", "-c", '"%s"' % code.replace('"', '\\"')],
                               capture_output=True, text=True, timeout=120)
            if r.returncode:
                raise OSError(r.stderr.strip()[-200:] or "ssh exit %d" % r.returncode)
            return r.stdout
    facts = collect(run)
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"at": time.time() if now is None else now, "facts": facts}, f)
    os.replace(tmp, path)
    return facts


def main(argv=None):
    cmd = (argv or sys.argv[1:] or ["show"])[0]
    try:
        if cmd == "refresh":
            f = refresh()
        else:
            r = read()
            if r["facts"] is None or r["stale"]:
                print("COULD NOT LOOK: host facts %s" % ("missing or unreadable" if r["age_s"] is None else "stale (%d s old)" % r["age_s"]))
                return 4
            f = r["facts"]
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        print("COULD NOT LOOK: %s" % e)
        return 4
    low = logins_low(f)
    print(json.dumps(f)[:400])
    if low:
        print("ALARM: login of %s has under 3 days left" % ", ".join(low))
    return 0


if __name__ == "__main__":
    sys.exit(main())
