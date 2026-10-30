#!/usr/bin/env python3
"""Selftest for per-arm metering (ARENA_METER_BUILD_SPEND_BY_CLONE_PATH): forced failures, all offline."""
import json, os, sys, tempfile, subprocess, time, shutil, multiprocessing
from datetime import datetime
from pathlib import Path
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "sim"))
import spend_census as S  # noqa: E402
import gpt_consult as G   # noqa: E402

fails = 0
def check(ok, name):
    global fails
    print(("PASS " if ok else "FAIL ") + name); fails += (not ok)

ROOT = "/home/mandrake/rm/arena"
T = tempfile.mkdtemp()
proj = os.path.join(T, "projects")
def transcript(slug, name, mid, out_tok, sub=False, model="claude-opus-FAKE-test-only", ts="2026-10-29T10:00:00Z"):
    d = os.path.join(proj, slug, "sess", "subagents") if sub else os.path.join(proj, slug)
    os.makedirs(d, exist_ok=True)
    rec = {"type": "assistant", "timestamp": ts, "isSidechain": sub,
           "message": {"id": mid, "model": model,
                       "usage": {"input_tokens": 100, "output_tokens": out_tok, "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}}
    open(os.path.join(d, name), "w").write(json.dumps(rec) + "\n")
# known ITE: opus weight 1, 100 in + 5*out
transcript(S.path_slug(ROOT + "/ralph_a"), "a.jsonl", "m1", 200)                    # 100+1000 = 1100
transcript(S.path_slug(ROOT + "/ralph_a"), "h.jsonl", "m2", 20, sub=True)           # helper: 100+100 = 200
transcript(S.path_slug(ROOT + "/trio"), "t.jsonl", "m3", 40)                        # 300
transcript(S.path_slug(ROOT + "/judge"), "j.jsonl", "m4", 60)                       # 400 -> harness
transcript(S.path_slug("/home/mandrake/rm/foundry"), "f.jsonl", "m5", 10)           # not arena
arms = ["ralph_a", "trio"]
cl = S.claude_spend_by_arm(proj, arms, ROOT)
check(abs(cl["ralph_a"]["ite"] - 1300) < 1e-6, "sanity probe: known transcript + helper recovered from slug (1300 ITE) -> %s" % cl.get("ralph_a"))
check(cl["ralph_a"]["files"] == 2, "helper transcript attributed to the arm's clone path")
check(abs(cl["trio"]["ite"] - 300) < 1e-6, "second arm separate")
check(abs(cl.get(S.HARNESS, {}).get("ite", 0) - 400) < 1e-6 and "judge" not in cl, "judge path bills to harness, not an arm")
check(S.UNATTRIBUTED in cl and "ralph_a" not in S.UNATTRIBUTED, "non-arena cwd is UNATTRIBUTED, not an arm")
check(S.arm_of_slug(S.path_slug(ROOT + "/judge/sub"), arms, ROOT) == S.HARNESS, "judge subdir is harness")
check(S.arm_of_slug(S.path_slug(ROOT + "/ralph_a/src/x"), arms, ROOT) == "ralph_a", "deeper cwd still the arm")

# gpt_consult tagging: drive the real _log_call
def call(env):
    log = os.path.join(T, "gpt.jsonl")
    old = {k: os.environ.get(k) for k in ("RM_ARM", "RM_GPT_CALL_LOG")}
    os.environ.pop("RM_ARM", None); os.environ["RM_GPT_CALL_LOG"] = log
    os.environ.update(env)
    try:
        G._log_call("job", "m", "x" * 400, "y" * 40, 0)
    finally:
        for k, v in old.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    return log
log = call({"RM_ARM": "trio"})
g = S.gpt_spend_by_arm(log)
check(g.get("trio", {}).get("calls") == 1 and abs(g["trio"]["ite_est"] - (100 + 5 * 10)) < 1e-6, "call under RM_ARM=trio billed to trio: %s" % g)
os.remove(log); log = call({})
g = S.gpt_spend_by_arm(log)
check("UNTAGGED" in g and "trio" not in g, "untagged call flagged UNTAGGED")
rep = S.arm_report(ran=["ralph_a"], arms=arms, projects=proj, arena_root=ROOT, gpt_log=log, since=0.0)
check(any("untagged" in f for f in rep["flags"]), "report carries the untagged flag")
check(rep["arms"]["ralph_a"]["claude_ite"] >= 1300, "arm_report ITE nonzero for ran arm")
try:
    S.arm_report(ran=["ralph_a", "ghost"], arms=arms + ["ghost"], projects=proj, arena_root=ROOT, gpt_log=log, since=0.0)
    check(False, "zero spend for an arm that ran is refused")
except S.ZeroSpendRefused:
    check(True, "zero spend for an arm that ran is refused")
# a blind meter (wrong root): real arm transcripts land UNATTRIBUTED -> ran arm sees zero -> refused
try:
    S.arm_report(ran=["ralph_a"], arms=arms, projects=proj, arena_root="/elsewhere", gpt_log=os.path.join(T, "none"), since=0.0)
    check(False, "blind meter (wrong clone root) refused")
except S.ZeroSpendRefused:
    check(True, "blind meter (wrong clone root) refused")

# ---------------- round 1 (window, atomic log, declared arms, exact arm parse, real tokens) ----------------
import gpt_call_log as L  # noqa: E402
def epoch(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()

def _par_call(i):
    G._log_call("job%d" % i, "m", "x" * 40, "y" * 8, 0)
def parallel(n, env):
    os.environ.pop("RM_ARM", None); os.environ.update(env)
    with multiprocessing.get_context("fork").Pool(16) as pool:
        pool.map(_par_call, range(n), chunksize=1)
# (1) 60 parallel calls => exactly 60 readable records: single-file mode on ext4 tmp, and per-file mode
ext_tmp = tempfile.mkdtemp(dir=os.path.expanduser("~"))   # ext4 home
os.environ["RM_GPT_CALL_LOG"] = os.path.join(ext_tmp, "one.jsonl")
parallel(60, {}); recs, bad = L.read_records(os.environ["RM_GPT_CALL_LOG"])
check(len(recs) == 60 and bad == 0, "60 parallel calls -> 60 readable records (single file, ext4): %d/%d bad" % (len(recs), bad))
os.environ["RM_GPT_CALL_LOG"] = os.path.join(ext_tmp, "perfile") + "/"
parallel(60, {}); recs, bad = L.read_records(os.path.join(ext_tmp, "perfile"))
nfiles = len(list(Path(ext_tmp, "perfile").glob("*.jsonl")))
check(len(recs) == 60 and bad == 0 and nfiles == 60, "60 parallel calls -> 60 records in 60 distinct files (per-file mode): %d/%d bad/%d files" % (len(recs), bad, nfiles))
d_on_drvfs = os.path.join("/mnt/d/ClaudeWork/rimmandrake/arena", "selftest_meter_%d" % os.getpid())
if os.path.isdir("/mnt/d/ClaudeWork"):
    os.environ["RM_GPT_CALL_LOG"] = d_on_drvfs + "/"
    parallel(60, {}); recs, bad = L.read_records(d_on_drvfs)
    check(len(recs) == 60 and bad == 0, "60 parallel calls on drvfs per-file mode -> 60 readable: %d/%d bad" % (len(recs), bad))
    shutil.rmtree(d_on_drvfs, ignore_errors=True)
os.environ.pop("RM_GPT_CALL_LOG", None)
# default target: ext4 root -> file; non-ext4 root -> directory (simulated), override still honoured
real_fs = L.fs_type
L.fs_type = lambda p: "drvfs"
check(L.default_target(ext_tmp)[1] == "dir", "default log on a non-ext4 storage root is a per-call directory")
L.fs_type = lambda p: "ext4"
check(L.default_target(ext_tmp)[1] == "file", "default log on an ext4 storage root is one file")
L.fs_type = real_fs
os.environ["RM_GPT_CALL_LOG"] = os.path.join(ext_tmp, "ovr.jsonl")
check(L.resolve_target() == (os.path.join(ext_tmp, "ovr.jsonl"), "file"), "RM_GPT_CALL_LOG override honoured")
os.environ.pop("RM_GPT_CALL_LOG", None)
# a corrupt fragment is counted and flagged, not dropped
open(os.path.join(ext_tmp, "one.jsonl"), "a").write('{"t": 1, "arm\n')
rp = S.arm_report(ran=["ralph_a"], arms=arms, projects=proj, arena_root=ROOT, gpt_log=os.path.join(ext_tmp, "one.jsonl"), since=0.0)
check(any("unreadable gpt" in f for f in rp["flags"]), "unreadable gpt log line is flagged")

# (2) run window: stale transcript excluded; arm with only stale spend refused (Claude and GPT)
W0, W1 = epoch("2026-10-29T12:00:00Z"), epoch("2026-10-29T13:00:00Z")
transcript(S.path_slug(ROOT + "/newarm"), "n.jsonl", "n1", 10, ts="2026-10-29T12:30:00Z")   # 150, in window
transcript(S.path_slug(ROOT + "/oldarm"), "o.jsonl", "o1", 10, ts="2026-10-29T09:00:00Z")   # stale
cl = S.claude_spend_by_arm(proj, ["newarm", "oldarm"], ROOT, since=W0, until=W1)
check(abs(cl["newarm"]["ite"] - 150) < 1e-6 and "oldarm" not in cl, "transcript older than the window is excluded")
glog = os.path.join(ext_tmp, "w.jsonl")
open(glog, "w").write(json.dumps({"t": W0 - 3600, "arm": "oldarm", "in_tok_est": 10, "out_tok_est": 1}) + "\n" +
                      json.dumps({"t": W0 + 5, "arm": "newarm", "tokens_used": 777}) + "\n")
try:
    S.arm_report(ran=["oldarm"], arms=["newarm", "oldarm"], projects=proj, arena_root=ROOT, gpt_log=glog, since=W0, until=W1)
    check(False, "arm with only stale (Claude+GPT) spend is refused")
except S.ZeroSpendRefused:
    check(True, "arm with only stale (Claude+GPT) spend is refused")
g = S.gpt_spend_by_arm(glog, W0, W1)
check("oldarm" not in g and g["newarm"]["ite"] == 777, "GPT spend honours the window")
check(S.arm_report(ran=["newarm"], arms=["newarm", "oldarm"], projects=proj, arena_root=ROOT, gpt_log=glog, since=W0, until=W1)["arms"]["newarm"]["total_ite_mixed"] == 150 + 777, "in-window arm passes with both sides")
r = subprocess.run([sys.executable, os.path.join(HERE, "sim", "spend_census.py"), "--arm-report", "--ran", "oldarm", "--arms", "newarm", "oldarm",
                    "--projects", proj, "--arena-root", ROOT, "--gpt-log", glog, "--since", "2026-10-29T12:00:00Z", "--until", "2026-10-29T13:00:00Z"],
                   capture_output=True, text=True)
check(r.returncode == 2 and "REFUSED" in r.stdout, "CLI --since/--until refuses a stale-only arm (exit 2)")

# (3) GPT rows alone do not satisfy a Claude arm; declared GPT-only / idle; no arms -> refuse
glog3 = os.path.join(ext_tmp, "g3.jsonl")
open(glog3, "w").write(json.dumps({"t": W0 + 1, "arm": "gonly", "tokens_used": 50}) + "\n")
kw = dict(arms=["gonly", "idl", "newarm"], projects=proj, arena_root=ROOT, gpt_log=glog3, since=W0, until=W1)
try:
    S.arm_report(ran=["gonly"], **kw); check(False, "arm with zero Claude spend + GPT rows is refused as a Claude arm")
except S.ZeroSpendRefused:
    check(True, "arm with zero Claude spend + GPT rows is refused as a Claude arm")
check("gonly" in S.arm_report(gpt_only_arms=["gonly"], **kw)["arms"], "declared GPT-only arm passes on GPT rows")
try:
    S.arm_report(gpt_only_arms=["idl"], **kw); check(False, "declared GPT-only arm with no GPT rows is refused")
except S.ZeroSpendRefused:
    check(True, "declared GPT-only arm with no GPT rows is refused")
check(S.arm_report(idle_arms=["idl"], **kw)["flags"] is not None, "declared idle arm with zero spend is accepted")
try:
    S.arm_report(**kw); check(False, "no declared arms is refused")
except S.ZeroSpendRefused:
    check(True, "no declared arms is refused")
r = subprocess.run([sys.executable, os.path.join(HERE, "sim", "spend_census.py"), "--arm-report"], capture_output=True, text=True)
check(r.returncode == 2 and "no arms declared" in r.stdout, "CLI with --ran omitted refuses with a clear message")

# (4) exact arm parse against the real directory listing / explicit list
AR = tempfile.mkdtemp(dir=ext_tmp) + "/"        # trailing slash on purpose
for dname in ("ralph", "ralph/a", "ralph-a", "trio/2", "trio", "arm-3", "arm_3", "solo", "judge-2", "zz"):
    os.makedirs(os.path.join(AR, dname), exist_ok=True)
sl = lambda rel: S.path_slug(AR.rstrip("/") + "/" + rel)
c = lambda rel, **k: S.classify_slug(sl(rel), arena_root=AR, **k)
check(c("solo")[0] == "solo" and c("solo/src/x")[0] == "solo", "FS listing: plain arm and deeper cwd resolve (root with trailing slash)")
check(c("ralph/a")[1] == "ambiguous" and c("ralph-a")[1] == "ambiguous", "ralph/a vs ralph-a -> UNATTRIBUTED ambiguous, not folded")
check(c("trio/2") == ("trio", ""), "trio/2 where only trio/2 exists resolves to trio via the real tree")
os.makedirs(os.path.join(AR, "trio-2")); os.makedirs(os.path.join(AR, "trio/2/x"), exist_ok=True)
check(c("trio/2")[1] == "ambiguous", "trio/2 vs trio-2 both existing -> ambiguous")
check(c("arm-3")[1] == "ambiguous" and c("arm_3")[1] == "ambiguous", "arm-3 vs arm_3 -> ambiguous")
check(c("judge-2")[0] == "judge-2" and c("judge/sub")[0] == S.HARNESS, "judge-2 arm is an arm, /judge is the harness")
check(c("ralph/zzz")[0] == "ralph", "ralph/zzz (dir absent) is only ralph's -> ralph")
check(S.classify_slug(S.path_slug("/home/mandrake/rm/arena-old/trio"), arena_root="/home/mandrake/rm/arena") == (S.UNATTRIBUTED, "unlisted"),
      "arena-old/trio is not under arena (unlisted, flagged)")
check(S.classify_slug(S.path_slug(AR.rstrip("/") + "-old/trio"), arena_root=AR)[1] == "unlisted", "arena-old sibling: unlisted, flagged")
check(S.classify_slug(sl("nope/x"), arena_root=AR) == (S.UNATTRIBUTED, "unlisted"), "unlisted arm subdir is unattributed, not folded as 'nope-x'")
# explicit list (no directory)
NR = "/nonexistent-arena-root/arena/"
e = lambda rel, arms: S.classify_slug(S.path_slug(NR.rstrip("/") + "/" + rel), arms, NR)
check(e("ralph/a", ["ralph"])[0] == "ralph" and e("ralph", ["ralph"])[0] == "ralph", "explicit list: sub-path of a listed arm resolves to it")
check(e("ralph-a", ["ralph", "ralph-a"])[1] == "ambiguous", "explicit list: ralph + ralph-a with slug ralph-a -> ambiguous")
check(e("zed/src", ["ralph"]) == (S.UNATTRIBUTED, "unlisted"), "explicit list: unlisted arm unattributed")
check(e("arm-3", ["arm_3", "arm-3"])[1] == "ambiguous", "explicit list: arm-3 / arm_3 ambiguous")
transcript(S.path_slug(NR.rstrip("/") + "/zed"), "z.jsonl", "z1", 10, ts="2026-10-29T12:30:00Z")
transcript("-other-place", "q.jsonl", "q1", 10, ts="2026-10-29T12:30:00Z")
rp = S.arm_report(ran=["newarm"], arms=["newarm"], projects=proj, arena_root=ROOT, gpt_log=glog, since=W0, until=W1)
check(any("UNATTRIBUTED" in f for f in rp["flags"]), "unattributed spend is counted and flagged in the report (not dropped)")

# (5) real tokens from the codex log, labelled estimate otherwise
check(G.real_tokens("blah\ntokens used\n6,261\nfoo") == 6261 and G.real_tokens("no figure here") is None, "real_tokens parses codex 'tokens used'")
rl = os.path.join(ext_tmp, "rt.jsonl"); os.environ["RM_GPT_CALL_LOG"] = rl; os.environ["RM_ARM"] = "trio"
G._log_call("j", "m", "x" * 4186, "y" * 87, 0, "tokens used\n6,261\n")
G._log_call("j", "m", "x" * 400, "y" * 40, 0, "no tokens line")
os.environ.pop("RM_GPT_CALL_LOG"); os.environ.pop("RM_ARM")
g = S.gpt_spend_by_arm(rl)["trio"]
check(g["ite"] == 6261 and g["ite_est"] == 150 and g["est_calls"] == 1 and g["calls"] == 2, "real tokens -> gpt_ite; chars/4 only as labelled gpt_ite_est fallback: %s" % g)
rp = S.arm_report(ran=["newarm"], arms=["newarm"], projects=proj, arena_root=ROOT, gpt_log=rl, since=0.0)
check("gpt_ite_est" in rp["arms"]["trio"] and rp["arms"]["trio"]["gpt_ite"] == 6261, "report carries gpt_ite and gpt_ite_est separately")

# LOW: unreadable transcript counted+flagged; cross-arm dup id deterministic + flagged; no-id calls do not collapse
bad = os.path.join(proj, S.path_slug(ROOT + "/newarm"), "bad.jsonl"); os.makedirs(os.path.dirname(bad), exist_ok=True)
os.symlink("/nonexistent/target", bad)        # dangling symlink: listed, open() raises -> unreadable
dg = {}; S.claude_spend_by_arm(proj, ["newarm"], ROOT, diag=dg)
check(len(dg["unreadable_files"]) == 1, "unreadable transcript is counted")
os.unlink(bad)
P2 = os.path.join(T, "p2"); 
def tr2(slug, name, mid, mt):
    d = os.path.join(P2, slug); os.makedirs(d, exist_ok=True); f = os.path.join(d, name)
    rec = {"type": "assistant", "timestamp": "2026-10-29T12:10:00Z", "message": {"id": mid, "model": "claude-opus-FAKE-test-only", "usage": {"input_tokens": 100, "output_tokens": 0}}}
    open(f, "w").write(json.dumps(rec) + "\n"); os.utime(f, (mt, mt))
tr2(S.path_slug(ROOT + "/trio"), "b.jsonl", "dup", 2000); tr2(S.path_slug(ROOT + "/ralph_a"), "a.jsonl", "dup", 1000)
dg = {}; cl = S.claude_spend_by_arm(P2, ["trio", "ralph_a"], ROOT, diag=dg)
check("ralph_a" in cl and "trio" not in cl and dg["id_conflicts"], "same message id under two arms: earliest mtime wins, conflict flagged")
for i in range(3):
    d = os.path.join(P2, S.path_slug(ROOT + "/noid")); os.makedirs(d, exist_ok=True)
    rec = {"type": "assistant", "timestamp": "2026-10-29T12:1%d:00Z" % i, "message": {"model": "claude-opus-FAKE-test-only", "usage": {"input_tokens": 100 + i, "output_tokens": 0}}}
    open(os.path.join(d, "n.jsonl"), "a").write(json.dumps(rec) + "\n")
cl = S.claude_spend_by_arm(P2, ["noid"], ROOT)
check(cl["noid"]["calls"] == 3, "calls with no message id do not collapse to one")
# builder's owed item: a 1-pass job in a fresh arm clone, simulated (no paid call) by a COPIED real small transcript
# placed under a temp arena root's project slug
FX = "/mnt/d/ClaudeWork/rimmandrake/foundry_arena/fixtures/small_real_transcript.jsonl"
check(os.path.isfile(FX), "fixture transcript present (missing => FAIL, never a silent skip): " + FX)
if os.path.isfile(FX):
    TA = tempfile.mkdtemp(dir=ext_tmp); os.makedirs(os.path.join(TA, "freshclone"))
    P3 = os.path.join(T, "p3", S.path_slug(TA + "/freshclone"), "sess", "subagents"); os.makedirs(P3)
    with open(FX) as fi, open(os.path.join(P3, "agent-real.jsonl"), "w") as fo:       # re-home the recorded cwd into the temp clone
        for ln in fi:
            try:
                dd = json.loads(ln)
                if "cwd" in dd: dd["cwd"] = TA + "/freshclone"
                ln = json.dumps(dd) + "\n"
            except Exception: pass
            fo.write(ln)
    cl = S.claude_spend_by_arm(os.path.join(T, "p3"), [], TA)
    check(cl.get("freshclone", {}).get("ite", 0) > 0, "copied real transcript, temp arena root -> nonzero ITE: %s" % cl.get("freshclone"))
print("OWED: the literal criterion 'a 1-pass job in a fresh arm clone' is a LIVE probe (one paid run in a real "
      "arena clone, then --arm-report); the copied-transcript check above only proves the slug/ITE path, not that probe.")

# ---- fix round 2 (GPT review) ----
# (6) explicit window required with --ran
try:
    S.arm_report(ran=["newarm"], arms=["newarm"], projects=proj, arena_root=ROOT, gpt_log=glog); check(False, "(6) --ran without a window is refused")
except S.ZeroSpendRefused as e:
    check("window" in str(e), "(6) arm_report(ran=...) without since is refused with a clear message")
r = subprocess.run([sys.executable, os.path.join(HERE, "sim", "spend_census.py"), "--arm-report", "--ran", "newarm", "--arms", "newarm",
                    "--projects", proj, "--arena-root", ROOT, "--gpt-log", glog], capture_output=True, text=True)
check(r.returncode == 2 and "--since" in r.stdout, "(6) CLI --ran without --since refuses (exit 2)")
# (8) GPT record with no numeric t is excluded and counted unreadable
g8 = os.path.join(ext_tmp, "g8.jsonl")
open(g8, "w").write(json.dumps({"arm": "newarm", "tokens_used": 999}) + "\n" + json.dumps({"t": "yesterday", "arm": "newarm", "tokens_used": 5}) + "\n" +
                    json.dumps({"t": W0 + 1, "arm": "newarm", "tokens_used": 7}) + "\n")
d8 = {}; g = S.gpt_spend_by_arm(g8, W0, W1, d8)
check(g["newarm"]["ite"] == 7 and d8["gpt_unreadable"] == 2, "(8) GPT records without numeric t are excluded and counted unreadable: %s %s" % (g, d8))
# (9) a failing file must not leave its ids in seen
P9 = os.path.join(T, "p9"); os.makedirs(os.path.join(P9, S.path_slug(ROOT + "/trio")))
os.makedirs(os.path.join(P9, S.path_slug(ROOT + "/newarm")))
def rec9(mid, tsv): return json.dumps({"type": "assistant", "timestamp": tsv, "message": {"id": mid, "model": "claude-opus-FAKE-test-only", "usage": {"input_tokens": 100, "output_tokens": 0}}}) + "\n"
fa = os.path.join(P9, S.path_slug(ROOT + "/trio"), "a.jsonl")
open(fa, "w").write(rec9("x1", "2026-10-29T12:10:00Z") + "{not json\n" + rec9("x2", "NOT-A-TIME"))
fb = os.path.join(P9, S.path_slug(ROOT + "/newarm"), "b.jsonl")
open(fb, "w").write(rec9("x1", "2026-10-29T12:10:00Z"))
os.utime(fa, (1000, 1000)); os.utime(fb, (2000, 2000))
d9 = {}; cl = S.claude_spend_by_arm(P9, ["trio", "newarm"], ROOT, diag=d9)
check(len(d9["unreadable_files"]) == 1 and cl.get("newarm", {}).get("ite") == 100, "(9) ids of a failed file are not 'seen': the copy in another file still counts: %s" % cl)
open(fa, "w").write(rec9("y1", "2026-10-29T12:10:00Z") + "{not json\n" + rec9("y2", "2026-10-29T12:11:00Z"))
d9 = {}; cl = S.claude_spend_by_arm(P9, ["trio", "newarm"], ROOT, diag=d9)
check(cl["trio"]["ite"] == 200 and d9.get("bad_lines"), "(9) malformed line mid-file: later records still counted and the bad line flagged")
# (7) short / lost write to an override file is warned about
import io, contextlib, gpt_call_log as L7
real_write = os.write
os.write = lambda fd, b: real_write(fd, b[: len(b) // 2])
buf = io.StringIO()
try:
    with contextlib.redirect_stderr(buf):
        L7.write_record({"t": 1, "arm": "x"}, target=os.path.join(ext_tmp, "short.jsonl"), mode="file")
finally:
    os.write = real_write
check("WARNING" in buf.getvalue(), "(7) short write to an override file is detected and warned: %r" % buf.getvalue()[:80])
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    L7.write_record({"t": 1, "arm": "x"}, target=os.path.join(ext_tmp, "okw.jsonl"), mode="file")
check(buf.getvalue() == "", "(7) a good write warns nothing")
# (1) slug collisions refused at declaration; transcript's recorded cwd cross-checked
try:
    S.arm_report(ran=["solo", "solo-b"], arms=["a/b", "a-b", "solo"], projects=proj, arena_root=ROOT, since=0.0); check(False, "(1) colliding arm names refused")
except S.ZeroSpendRefused:
    check(False, "(1) wrong exception class")
except S.ArmNameCollision as e:
    check("a-b" in str(e) and "a/b" in str(e), "(1) arm names whose slugs collide are refused at declaration: %s" % e)
P1 = os.path.join(T, "p1"); d1 = os.path.join(P1, S.path_slug(ROOT + "/solo")); os.makedirs(d1)
def rec1(mid, cwd): return json.dumps({"type": "assistant", "cwd": cwd, "timestamp": "2026-10-29T12:10:00Z", "message": {"id": mid, "model": "claude-opus-FAKE-test-only", "usage": {"input_tokens": 100, "output_tokens": 0}}}) + "\n"
open(os.path.join(d1, "ok.jsonl"), "w").write(rec1("c1", ROOT + "/solo/src"))
open(os.path.join(d1, "bad.jsonl"), "w").write(rec1("c2", ROOT + "-solo"))
d1d = {}; cl = S.claude_spend_by_arm(P1, ["solo"], ROOT, diag=d1d)
check(cl["solo"]["ite"] == 100 and cl[S.UNATTRIBUTED]["ite"] == 100 and cl[S.UNATTRIBUTED]["reasons"] == {"cwd_mismatch": 100.0}
      and d1d["cwd_mismatch"], "(1) recorded cwd outside the arm path => UNATTRIBUTED cwd_mismatch + flag: %s" % cl)
# (2) separate units, mixed total only with an explicit note
glog2 = os.path.join(ext_tmp, "u2.jsonl")
open(glog2, "w").write(json.dumps({"t": W0 + 5, "arm": "newarm", "tokens_used": 777}) + "\n")
a2 = S.arm_report(ran=["newarm"], arms=["newarm"], projects=proj, arena_root=ROOT, gpt_log=glog2, since=W0, until=W1)["arms"]["newarm"]
check(a2["claude_ite"] == 150 and a2["gpt_ite"] == 777 and "ite" not in a2 and a2["total_ite_mixed"] == 927
      and "RAW" in a2["unit_note"] and "open" in a2["unit_note"], "(2) claude_ite and gpt_ite separate; total_ite_mixed carries a unit_note, no bare 'ite'")
shutil.rmtree(ext_tmp, ignore_errors=True)
print("FAILS", fails)
sys.exit(1 if fails else 0)
