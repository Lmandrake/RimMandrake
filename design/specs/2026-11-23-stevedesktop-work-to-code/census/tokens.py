#!/usr/bin/env python3
"""tokens.py PRICES.json [--dump OUT.json] - weighted_v2 of the model turns whose tool call is SteveDesktop work, in the 7
days to END, over ~/.claude/projects of THIS machine (run it over ssh on SteveDesktop too: `ssh HOST python3 - < tokens.py`
with PRICES inlined, see README). One turn = one message id, counted once across files. First rule that matches wins."""
import collections, glob, json, os, re, sys
PR = json.loads(os.environ["PRICES"]) if os.environ.get("PRICES") else json.load(open(sys.argv[1]))
W = {m: {k: float(v) / 4.0 for k, v in p.items()} for m, p in PR.items()}
LO, HI = os.environ.get("LO", "2026-11-17T04:30:00"), os.environ.get("HI", "2026-11-24T04:30:00")
SKIP = ("STUDY-STEVEDESKTOP-WORK-SETUP", "FIND-AGENT-WORK-THAT-PYTHON")
def cost(model, u):
    m = W.get(model) or W.get(re.sub(r"\[.*\]", "", model or ""))
    if not m: return None
    cc = u.get("cache_creation") or {}
    w5, w1 = cc.get("ephemeral_5m_input_tokens") or 0, cc.get("ephemeral_1h_input_tokens") or 0
    tot = u.get("cache_creation_input_tokens") or 0
    if w5 + w1 != tot: w5, w1 = 0, tot
    return ((u.get("input_tokens") or 0) * m["input_tokens"] + w5 * m["cache_write_5m"] + w1 * m["cache_write_1h"]
            + (u.get("cache_read_input_tokens") or 0) * m["cache_read_input_tokens"] + (u.get("output_tokens") or 0) * m["output_tokens"])
STEVE = re.compile(r"testq|stevedesktop|\bsteve[12]?\b|rm/runner(_b)?\b|remote_modcheck|rw_game\.sh|sync_test_mods|companion_stage|fault_monitor|J20261\d{3}T\d{6}Z-", re.I)
CODE = re.compile(r"run_selftests|selftest_|git (add|commit|diff|log|show|status|grep|blame)|publish -m|\./publish|apply_patch|design/specs|code_review_status")
RULES = [
    ("submit a job", re.compile(r"testq\.py\s+(submit|sweep|fill\b)")),
    ("lane control (pause, resume, cancel)", re.compile(r"testq\.py\s+(pause|resume|cancel|maintenance)|steve2\.(on|stop)|archmagi\.stop|fill\.stop")),
    ("wait for a job", re.compile(r"(sleep|until |while |waitfor|Monitor)[\s\S]{0,400}(testq|J20261|stevedesktop|running/|done/)|(testq|J20261)[\s\S]{0,400}(sleep \d|waitfor)")),
    ("read a job or the lane", re.compile(r"testq\.py\s+(show|list|steward|visit-feed)|testq/(done|running|pending|tick\.log|quarantined|steward)|invalid_census|steve_results|J20261\d{3}T\d{6}Z-|steve_games|modcheck\.log")),
    ("set up (companion, mods, deploy, install, game)", re.compile(r"companion_stage|sync_test_mods|remote_modcheck|rw_game\.sh|bridgetools/build\.py|game_instance\.py|deploy_custom_mods|modset_builder|modlist_swap|testq_blocks")),
    ("reach the machine over ssh", re.compile(r"\bssh\b|\bscp\b|\brsync\b|sps\.sh|verify_from_archmagi")),
    ("machine fault work", re.compile(r"fault_monitor|fault_watch|regprobe|steve_cpu|soak|heat")),
]
LEDGER = re.compile(r"cli\.py (note|close|file|wait|claim|verify)|rimflow ")
EXEC = re.compile(r"testq\.py\s+\w|\bssh\b|\bscp\b|rw_game\.sh|remote_modcheck|sync_test_mods|companion_stage|testq/(done|running|pending|tick\.log|quarantined|steward)|J20261\d{3}T\d{6}Z-")
seen = set(); A = collections.defaultdict(lambda: [0, 0.0]); S = collections.defaultdict(float); n = 0; allw = 0.0; unk = collections.Counter(); ex = {}; M = collections.Counter(); X = collections.Counter()
fs = [f for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")) + glob.glob(os.path.expanduser("~/.claude/projects/*/*/subagents/*.jsonl")) if not any(s in f for s in SKIP)]
unread = 0
for f in fs:
    if os.path.getmtime(f) < 1794889800: continue
    n += 1; msgs = {}; order = []
    try: fh = open(f, errors="replace")
    except OSError: unread += 1; continue
    for line in fh:
        if '"assistant"' not in line: continue
        try: d = json.loads(line)
        except ValueError: continue
        if d.get("type") != "assistant": continue
        t = (d.get("timestamp") or "")[:19]
        if not LO <= t <= HI: continue
        m = d.get("message") or {}; i = m.get("id")
        if i not in msgs: msgs[i] = [m.get("model"), m.get("usage") or {}, []]; order.append(i)
        r = msgs[i]; u = m.get("usage") or {}
        if (u.get("output_tokens") or 0) >= (r[1].get("output_tokens") or 0): r[1] = u
        for x in m.get("content") or []:
            if isinstance(x, dict) and x.get("type") == "tool_use":
                p = x.get("input") or {}
                r[2].append((x.get("name"), " ".join(str(p.get(k) or "") for k in ("command", "file_path", "pattern", "path"))[:6000]))
    for i in order:
        if i in seen or msgs[i][0] in (None, "<synthetic>"): continue
        seen.add(i); c = cost(msgs[i][0], msgs[i][1])
        if c is None: unk[msgs[i][0]] += 1; continue
        allw += c
        cmd = " ".join(t for nme, t in msgs[i][2])
        # the folder name of a clone is in many paths: drop it before matching
        cmd2 = re.sub(r"/home/mandrake/rm/[\w./-]*clones/[\w.-]+", "", cmd)
        if not STEVE.search(cmd2): continue
        edit = any(nme in ("Edit", "Write") for nme, _ in msgs[i][2])
        if LEDGER.search(cmd2) and not re.search(r"testq\.py\s+\w|\bssh\b", cmd2): k = "ledger or note text that names it"
        elif edit or CODE.search(cmd2) and not re.search(r"testq\.py\s+(submit|show|list)|\bssh\b", cmd2): k = "lane code and page work"
        else:
            k = next((nm for nm, rx in RULES if rx.search(cmd2)), "other text that names it")
        A[k][0] += 1; A[k][1] += c; M[msgs[i][0]] += c
        g = "fault or audio diagnosis runs" if re.search(r"AUDIO|SONIC|DRIVER-SET|LIGHTING|CPU|SOAK|REGISTER|HYPERVISOR|STEVE-FAULT", f.split("projects/")[1]) else "Conductor and role windows" if re.search(r"rm-bench/|rm-bench\b|rm-roles", f.split("projects/")[1].split("/")[0]) else "other runs"
        X[(k, g)] += c
        S[os.path.relpath(f, os.path.expanduser("~/.claude/projects")).split("/")[0].split("clones-")[-1][:70]] += c
        ex.setdefault(k, []).append(cmd2[:150].replace("\n", " "))
print("files", n, "unreadable", unread, "unpriced", dict(unk), "all turns M", round(allw / 1e6, 1))
for k, v in sorted(A.items(), key=lambda z: -z[1][1]): print("%7.2fM %6d %s" % (v[1] / 1e6, v[0], k))
for (k, g), v in sorted(X.items(), key=lambda z: -z[1]): print("      %6.2fM %s | %s" % (v / 1e6, k, g))
print("by model", {k: round(v / 1e6, 1) for k, v in M.items()})
for k, v in sorted(S.items(), key=lambda z: -z[1])[:30]: print("   %6.2fM %s" % (v / 1e6, k))
if os.environ.get("EX"):
    import random
    random.seed(4)
    for k, v in ex.items():
        print("==", k)
        for x in random.sample(v, min(10, len(v))): print("    ", x)
