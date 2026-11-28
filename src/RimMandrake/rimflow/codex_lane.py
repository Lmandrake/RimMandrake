#!/usr/bin/env python3
"""codex_lane.py: while the Claude room is short, test-proven list tickets go to Codex, and only a passing result lands.

Item RIMMANDRAKE_BUILD_CODEX_LANE_WHEN_CLAUDE_ROOM_IS_SHORT; page design/specs/2026-11-27-codex-lane/boundary.md; tests
selftest_codex_lane.py; settings: the `codex_lane` block of list_dispatch.json. A step of `list_dispatch.py tick`:

    plan()     which tickets the Codex lane takes this tick (pure); the Claude lane does not see them
    execute()  start one Codex work unit per sent ticket (family codex_lane), one Sonnet lander per passing result
    work()     the work unit: the gate, a scratch clone, Codex in it (agent_runner, Dispatch's door), the diff, the check

    python3 src/RimMandrake/rimflow/codex_lane.py room              the room and the Codex share, as the tick reads them
    python3 src/RimMandrake/rimflow/codex_lane.py status            each ticket the lane holds, with its state
    python3 src/RimMandrake/rimflow/codex_lane.py work --job DIR    one Codex work unit (the tick starts it)
    python3 src/RimMandrake/rimflow/codex_lane.py review PATH...    a code review by roles/code_review.md through Codex,
                                                                    judged by one Sonnet run
    exit 0 done; 2 could not look; 4 refused (Codex at its leave line)
"""
import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BUILD_CODEX_LANE_WHEN_CLAUDE_ROOM_IS_SHORT"
FAMILY = "codex_lane"
SHORT, AMPLE, COULD_NOT_LOOK = "SHORT", "AMPLE", "COULD_NOT_LOOK"
# account_plan.decide writes this phrase when no other Claude account can take over from the live one
# (selftest t_room_short_sends_a_proven_ticket_to_codex goes red if account_plan.py stops saying it)
NO_TAKEOVER = "no account can take over"
LANDER_MODEL = "sonnet"     # Agent_Policy ladder: a test proves the code, so Sonnet reads and lands it
SANDBOX_KEYS = ("RM_MATURATION_DISPATCH_DIR", "RM_DISPATCHER_STATE", "RM_LIST_DISPATCH_DIR")
CODE_REVIEW = os.path.join(HERE, "roles", "code_review.md")
DEFAULT_RX = r"^cmd:.*(selftest_|_accept\.py)"
# Hang guard (the class of call_deadline_lint.py) for one `systemctl --user is-active` read.
SYSTEMCTL_TIMEOUT_S = 60  # budget: class=hang
# Hang guard for the scratch clone and the diff (a git call on a 4 GB tree under load).
GIT_TIMEOUT_S = 3600  # budget: class=hang


def _one(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def lane_cfg(cfg):
    return cfg.get("codex_lane") or {}


def check_rx(cfg):
    return re.compile(lane_cfg(cfg).get("check_regex") or cfg.get("sonnet_if_check_regex") or DEFAULT_RX)


# ---- the readings ---------------------------------------------------------------------------------------------------

def room(notice, now):
    """-> (SHORT | AMPLE | COULD_NOT_LOOK, why) from the account plan's notice. Short: the fleet is stopped, the live
    account is at its line, or no other account can take over from it. A missing, stale or blind notice is could not
    look, and the lane then sends nothing."""
    import account_plan as AP
    if not isinstance(notice, dict) or not notice:
        return COULD_NOT_LOOK, "COULD NOT LOOK: no notice of the account plan could be read"
    at = AP.stamp(notice.get("at"))
    if at is None:
        return COULD_NOT_LOOK, "COULD NOT LOOK: the notice has no readable time"
    if now - at > AP.NOTICE_FRESH_S:
        return COULD_NOT_LOOK, "COULD NOT LOOK: the notice is %d min old" % ((now - at) // 60)
    if notice.get("could_not_look"):
        return COULD_NOT_LOOK, "COULD NOT LOOK: %s" % _one(notice.get("message") or notice.get("why"), 200)
    why = _one(notice.get("why"), 300)
    if notice.get("state") == "stop":
        return SHORT, "the fleet is stopped: %s" % why
    if notice.get("account_end"):
        return SHORT, "%s is at its line: %s" % (notice.get("account") or "the live account", why)
    if NO_TAKEOVER in str(notice.get("why") or ""):
        return SHORT, "%s is the last account: %s" % (notice.get("account") or "the live account", why)
    return AMPLE, "another account can take over: %s" % why


def read_notice():
    import account_plan as AP
    if os.environ.get("RM_UNDER_SELFTEST") and not os.environ.get("RM_SWITCH_PLAN_DIR"):
        return None     # a test child never reads the live machine's notice
    return AP.read_json(os.path.join(str(AP.notice_dir()), "notice.json"))


def share(adv):
    """-> (ok, why) from codex_advice.advice(): Codex is over its leave line (his share of the Codex week). A line that
    could not be read sends nothing: the lane is a bulk sender, and a blind meter could spend his share."""
    st = (adv or {}).get("state")
    if st == "OK":
        return True, adv.get("why") or "Codex is over its line"
    if st == "LINE":
        return False, "Codex is at its leave line: %s" % (adv.get("why") or "")
    return False, "COULD NOT LOOK at Codex's leave line: %s" % ((adv or {}).get("why") or "no advice")


def read_advice():
    import codex_advice
    return codex_advice.advice()


def unit_alive(unit):
    """-> True (active or activating), False (gone), None (could not look)."""
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", unit], capture_output=True, text=True,
                           timeout=SYSTEMCTL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    word = (r.stdout or "").strip()
    if word in ("active", "activating", "reloading", "deactivating"):
        return True
    if word in ("inactive", "failed", "unknown"):
        return False
    return None


# ---- which tickets (pure) -------------------------------------------------------------------------------------------

def eligible(it, rx, now):
    """-> (ok, why): a ticket of `list_home.py offer` (not parked, not one mod's work) whose outcome check fails now and
    runs a selftest or an acceptance script, and that only needs offline work."""
    import fresh_reader as FR

    mw = it.get("mod_work") or {}
    if mw.get("mod") or mw.get("unreadable") or it.get("mod") or str(it.get("home") or "").startswith("mod:"):
        return False, "one mod's work, or its mod reading could not be made: it waits for that mod's pipeline"
    if FR.is_reader(it):
        return False, "its check reads review records; the Claude lane supplies the fresh-reader brief"
    if not rx.search(str(it.get("effect") or "")):
        return False, "its check runs no selftest or acceptance script"
    if it.get("verdict") != "fails":
        return False, "its check does not fail now"
    if it.get("off") or it.get("off_unreadable"):
        return False, "switched off"
    if it.get("blocked") or (it.get("wait_until") and it["wait_until"] > now):
        return False, "parked: a block or a dated wait"
    if it.get("claimed"):
        return False, "claimed: %s" % it["claimed"]
    if it.get("judge") or it.get("shape_due") or it.get("route"):
        return False, "a judge or a Shape route is its next step"
    if (it.get("needs") or "offline") != "offline":
        return False, "it needs %s, not only offline work" % it["needs"]
    return True, "its check fails and runs a test"


def result_of(job):
    try:
        with open(os.path.join(job, "result.json"), encoding="utf-8") as f:
            r = json.load(f)
        return r if isinstance(r, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def plan(cfg, cst, facts, now, room_r, share_r, account, alive):
    """-> {"take", "send", "land", "rows"}. Pure over its arguments; edits cst (the lane's own state). take: the ids
    the Claude lane does not see this tick; send: new Codex jobs; land: built results whose lander starts now."""
    c = lane_cfg(cfg)
    out = {"take": [], "send": [], "land": [], "rows": []}
    if not c.get("enabled"):
        return out
    recs = cst.setdefault("items", {})
    items = facts.get("items") or {}
    max_live = int(c.get("max_live", 2))
    max_voids = int(c.get("max_voids_per_item", 2))

    def row(iid, decision, why):
        out["rows"].append({"item": iid, "decision": decision, "why": why})

    live = 0
    for iid in sorted(recs):
        r = recs[iid]
        if r.get("state") == "sent":
            res = result_of(r.get("job") or "")
            if res and res.get("state") in ("built", "failed", "void"):
                r.update(state=res["state"], why=res.get("why"), at=now)
                if res["state"] == "void":
                    # a refusal at his leave line is no system failure: it spends no try and is no strike
                    r["voids"] = int(r.get("voids") or 0) + (0 if res.get("refused") else 1)
            elif alive(r.get("unit")) is False:
                r.update(state="void", why="its unit %s is gone with no result" % r.get("unit"), at=now,
                         voids=int(r.get("voids") or 0) + 1)
            else:
                live += 1
                out["take"].append(iid)
                row(iid, "codex_live", "Codex works it in its unit %s" % r.get("unit"))
                continue
        if r.get("state") in ("void", "void_seen") and int(r.get("voids") or 0) >= max_voids:
            r["state"] = "stopped"      # two system failures in a row: the Claude lane takes it; the record says why
            row(iid, "codex_stopped", "%d Codex tries in a row ended with no result, the last: %s; the Claude lane "
                "takes it" % (r["voids"], _one(r.get("why"), 200)))
            continue
        if r.get("state") == "void" and iid in items:
            out["take"].append(iid)       # a void try is sent again by a later tick, not by Claude in the same one
            row(iid, "codex_void", "its Codex try ended with no result (%s); no try is spent" % _one(r.get("why"), 200))
            r["state"] = "void_seen"
            continue
        if r.get("state") == "built" and iid not in items:
            r.update(state="gone", why="the ticket is no longer open with a failing check: no lander", at=now)
            continue
        if r.get("state") == "built":
            out["take"].append(iid)
            if account[0]:
                out["land"].append(iid)
                row(iid, "codex_land", "Codex's result passes its check: one Sonnet lander reads and lands it")
            else:
                row(iid, "codex_built", "Codex's result passes its check; the lander waits for the account gate: %s"
                    % _one(account[1], 200))
    if room_r[0] != SHORT or not share_r[0]:
        why = room_r[1] if room_r[0] != SHORT else share_r[1]
        cst["last"] = {"at": now, "sends": False, "why": why}
        return out
    cst["last"] = {"at": now, "sends": True, "why": "%s; %s" % (room_r[1], share_r[1])}
    rx = check_rx(cfg)
    runs = facts.get("runs")
    for iid, it in items.items():
        if iid in out["take"]:
            continue
        # a live bundle's member or a live run's item is that run's work, and runs that could not be read may hold it:
        # the Claude lane says which (in_bundle, live, blind). RIMMANDRAKE_KEEP_CODEX_LANE_OFF_LIVE_BUNDLE_MEMBERS: four
        # members of a live bundle went to Codex on 2026-11-27 and two builds of each met on the same files.
        run = (runs or {}).get(iid) or {}
        if runs is None or run.get("bundle") or run.get("live"):
            continue
        r = recs.get(iid) or {}
        if r.get("state") not in (None, "void_seen"):
            continue        # one try: failed, stopped and landing are final here; the Claude lane or the lander carries it
        ok, _why = eligible(it, rx, now)
        if not ok:
            continue
        out["take"].append(iid)
        if live >= max_live:
            row(iid, "codex_waits", "the room is short; it waits for a Codex slot (%d of %d live)" % (live, max_live))
            continue
        live += 1
        out["send"].append(iid)
        row(iid, "codex_send", "the room is short (%s): Codex builds it; its check decides" % _one(room_r[1], 160))
    return out


def take_out(facts, ids):
    """-> facts with the Codex lane's tickets left out, so the Claude lane neither launches nor bundles them."""
    if not ids:
        return facts
    ids = set(ids)
    f = dict(facts)
    f["items"] = {i: v for i, v in (facts.get("items") or {}).items() if i not in ids}
    if isinstance(facts.get("systems"), dict):
        f["systems"] = {i: v for i, v in facts["systems"].items() if i not in ids}
    if isinstance(facts.get("join"), dict):
        f["join"] = {i: v for i, v in facts["join"].items() if i not in ids}
    return f


# ---- the acts -------------------------------------------------------------------------------------------------------

def lane_dir():
    import list_dispatch as LD
    d = os.path.join(LD.sdir(), "codex_lane")
    os.makedirs(d, exist_ok=True)
    return d


def launch_work(iid, job):
    """One Codex work unit through control's one door. -> (rc, text, unit)."""
    import control as C
    unit = "rm-codex-lane-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", iid.lower())[:40].strip("-"), int(time.time()))
    args = ["--user", "--quiet", "--collect", "--working-directory", REPO, "--",
            sys.executable, os.path.abspath(__file__), "work", "--job", job]
    r = C.launch_unit(args, {"family": FAMILY, "unit": unit, "item": iid, "model": "codex"},
                      capture_output=True, text=True, timeout=GIT_TIMEOUT_S, stdin=subprocess.DEVNULL)
    if getattr(r, "refused", False):
        return 75, r.why or "refused by control", None
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip(), unit if r.returncode == 0 else None


def launch_lander(iid, brief, cfg=None):
    import list_dispatch as LD
    cfg = cfg or LD.load_cfg()
    cap = cfg.get("%s_cap_usd" % LANDER_MODEL) or LD._shipped().get("%s_cap_usd" % LANDER_MODEL)
    return LD.launch(iid, LANDER_MODEL, cap, brief, cfg.get("seat", "BENCH"), None)


LANDER = """Land a Codex result for list item {item} (the Codex lane, codex_lane.py; page
design/specs/2026-11-27-codex-lane/boundary.md). Codex built it in its own scratch clone while the Claude room was
short. You are the Claude run that reads it, judges it and lands it. You are Sonnet because a test proves the code.

Title: {title}
Its outcome check, which failed before Codex:   {check}
The check held in Codex's clone after its change: {out}
Codex's change, as one patch:  {patch}
Codex's own last words:        {answer}

Steps:
0. Start the item: python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "Codex lane lander" --publish
1. Apply the patch in YOUR clone: git apply --3way {patch_q}
   If it does not apply on origin/main, port it by hand; the patch is the design, your clone is the truth.
2. Run the check in your clone until it reads holds:
   python3 src/RimMandrake/rimflow/list_effect.py check {check_q}
   If it does not hold and you cannot make it hold, land NOTHING: end with a note on the item that starts
   `LEFT OPEN: Codex lane: the check does not hold in the lander's clone:` and names what you saw.
3. Read each file that the patch changes, with its boundary page and its tests, by
   src/RimMandrake/rimflow/roles/code_review.md. Judge each change of Codex's by its significance rule: a Problem is
   a broken promise or a failure with a concrete case. Fix each Problem test first (red, then green). A finding that is
   not significant is polish of a file you changed: do it now. Codex calls rare inputs Problems; you judge them.
4. Check that the change does what the item asks, not only what the check reads. A check that passes while the need
   stays unmet is wrong: say so in a note and do not close.
5. Land with ./publish -m "{item}: <what> (built by Codex, read by Sonnet)" <explicit paths>, then close:
   python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --seat BENCH --why "Codex lane: the check holds at <sha>" --publish
6. File the fresh reader of the fix: python3 src/RimMandrake/rimflow/fresh_reader.py file --fix <sha> <paths>
"""


def lander_brief(iid, rec, it):
    job = rec.get("job") or ""
    res = result_of(job) or {}
    patch = os.path.join(job, "patch.diff")
    return LANDER.format(item=iid, title=(it or {}).get("title") or res.get("title") or "-",
                         check=res.get("effect") or (it or {}).get("effect"),
                         check_q=shlex.quote(res.get("effect") or (it or {}).get("effect") or ""),
                         out=_one(res.get("out"), 400) or "(nothing)", patch=patch, patch_q=shlex.quote(patch),
                         answer=_one(res.get("answer"), 600) or "(none)")


def execute(cfg, cst, out, facts, now, fx=None):
    """Start what plan() chose; edits out["rows"] and cst. Never raises for one ticket's failure."""
    fx = fx or {}
    do_work = fx.get("codex_launch", launch_work)
    do_land = fx.get("codex_lander") or (lambda iid, brief: launch_lander(iid, brief, cfg))
    recs = cst.setdefault("items", {})
    items = facts.get("items") or {}
    rows = {r["item"]: r for r in out["rows"]}
    for iid in out["send"]:
        it = items.get(iid) or {}
        job = os.path.join(lane_dir(), "jobs", "%s-%d" % (iid, int(now)))
        os.makedirs(job, exist_ok=True)
        with open(os.path.join(job, "job.json"), "w", encoding="utf-8") as f:
            json.dump({"item": iid, "effect": it.get("effect"), "title": it.get("title"), "out": _one(it.get("out"), 2000),
                       "at": now}, f, indent=1)
        try:
            rc, text, unit = do_work(iid, job)
        except Exception as e:  # noqa: BLE001 - one launch that broke is said on its row
            rc, text, unit = 99, "%s: %s" % (type(e).__name__, e), None
        r = recs.get(iid) or {}
        if rc == 0 and unit:
            recs[iid] = dict(r, state="sent", job=job, unit=unit, at=now)
            rows[iid].update(decision="codex_sent", unit=unit)
        else:
            recs[iid] = dict(r, state="void_seen", why="never started: " + _one(text, 300), at=now,
                             voids=int(r.get("voids") or 0) + 1)
            rows[iid].update(decision="codex_launch_failed", why=_one(text, 300) or "rc %s" % rc)
    for iid in out["land"]:
        rec = recs[iid]
        try:
            rc, text, unit = do_land(iid, lander_brief(iid, rec, items.get(iid)))
        except Exception as e:  # noqa: BLE001
            rc, text, unit = 99, "%s: %s" % (type(e).__name__, e), None
        if rc == 0 and unit:
            rec.update(state="landing", lander=unit, at=now)
            rows[iid].update(decision="codex_landing", unit=unit)
        else:
            rows[iid].update(decision="codex_lander_failed", why=_one(text, 300) or "rc %s" % rc)


DRY = {"codex_send": "would_codex", "codex_land": "would_land"}


def step(cfg, st, facts, now, fx, apply, account):
    """The tick's call. -> (facts for the Claude lane, the lane's rows). A lane that broke never stops the Claude lane:
    its row says so and every ticket stays with Claude."""
    fx = fx or {}
    try:
        cst = st.setdefault("codex_lane", {})
        if not lane_cfg(cfg).get("enabled"):
            return facts, []
        room_r = room((fx["codex_notice"] if "codex_notice" in fx else read_notice)(), now)
        share_r = share((fx["codex_advice"] if "codex_advice" in fx else read_advice)())
        out = plan(cfg, cst, facts, now, room_r, share_r, account, fx.get("codex_alive", unit_alive))
        if apply:
            execute(cfg, cst, out, facts, now, fx)
        else:
            for r in out["rows"]:
                r["decision"] = DRY.get(r["decision"], r["decision"])
        return take_out(facts, out["take"]), out["rows"]
    except Exception as e:  # noqa: BLE001
        return facts, [{"item": "-codex-lane", "decision": "blind",
                        "could_not_look": "the Codex lane raised %s: %s" % (type(e).__name__, _one(e, 300)),
                        "why": "the Codex lane could not look; every ticket stays with the Claude lane"}]


# ---- the work unit --------------------------------------------------------------------------------------------------

PROMPT = """You are a Codex builder for RimMandrake, in a scratch clone that is yours alone ({clone}).
Make this list ticket's outcome check hold, by a real fix of what the ticket asks.

Ticket: {item}
Title: {title}
Its outcome check (run from the clone's root): {check}
What the check prints now (it fails): {out}

Rules:
- Read the check first, then the code it exercises, and the boundary page under design/specs/ that names that code.
- Tests first: if the check's test is missing a case the ticket names, add it and see it fail before you fix.
- Fix the cause in the code. Never weaken, skip or delete a test or a check to make it pass.
- Run the check until it passes: {check_cmd}
- Never run ./publish, git commit, git push or any rimflow / cli.py command, and never write the ledger
  (infrastructure/state/). The Claude run that reads your work lands it.
- Never touch real pipeline state: work only inside this clone. The state paths in your environment point at a sandbox.
- End with a short plain summary: what you changed, why, and the check's last line.
"""


def codex_prompt(job, clone):
    eff = job.get("effect") or ""
    return PROMPT.format(clone=clone, item=job.get("item"), title=job.get("title") or "-", check=eff,
                         out=_one(job.get("out"), 1500) or "(nothing)",
                         check_cmd=eff[4:] if eff.startswith("cmd:") else eff)


def make_clone(iid, job):
    name = "cx-%s-%d" % (re.sub(r"[^a-z0-9]+", "-", iid.lower())[:30].strip("-"), int(time.time()))
    r = subprocess.run([sys.executable, os.path.join(UTILS, "scratch_clone.py"), "clone", "codex lane " + iid,
                        "--name", name, "--slim"], capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
                       stdin=subprocess.DEVNULL, cwd=REPO, env=dict(os.environ, RM_SEAT=os.environ.get("RM_SEAT") or "BENCH"))
    path = (r.stdout or "").strip().splitlines()[-1:] if r.returncode == 0 else []
    if not path or not os.path.isdir(path[0]):
        raise RuntimeError("scratch_clone.py clone exit %s: %s" % (r.returncode, _one(r.stderr or r.stdout, 300)))
    return path[0]


def free_clone(clone):
    """Delete a Codex scratch clone (a `cx-` folder under a scratch root). The patch and the answer live in the job
    folder, so the clone is dead weight; left behind, its staged files read as stranded work to the pool alarm."""
    if clone and os.path.basename(clone.rstrip("/")).startswith("cx-") and os.path.isdir(os.path.join(clone, ".git")):
        shutil.rmtree(clone, ignore_errors=True)


def make_diff(clone, path):
    """-> the patch text (also written to path): every change in the clone against its HEAD, new files included."""
    subprocess.run(["git", "-C", clone, "add", "-A", "--", ".", ":!**/__pycache__/**"], check=True,
                   capture_output=True, timeout=GIT_TIMEOUT_S)
    r = subprocess.run(["git", "-C", clone, "diff", "--cached", "--binary", "HEAD"], check=True, capture_output=True,
                       text=True, errors="replace", timeout=GIT_TIMEOUT_S)
    with open(path, "w", encoding="utf-8") as f:
        f.write(r.stdout)
    return r.stdout


def run_codex(cwd, prompt, result, events, spend):
    import agent_runner as AR
    return AR.run(cwd, prompt, result, events, spend, sandbox="workspace-write", effort="high")


def run_check(effect, root):
    import list_effect as LE
    return LE.run(effect, root)


def note(iid, text):
    r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "note", iid, "--text", text, "--seat", "BENCH",
                        "--why", "pipeline act (codex_lane work unit)", "--publish"], cwd=REPO, capture_output=True,
                       text=True, timeout=GIT_TIMEOUT_S, stdin=subprocess.DEVNULL,
                       env=dict(os.environ, RIMFLOW_SEAT="BENCH",
                                RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or "rm-codex-lane"))
    return r.returncode


def gate():
    """0 = go. Codex over its leave line goes; at the line the plan's gate refuses and records it (exit 4); a line that
    cannot be read sends nothing here (exit 2): the lane is a bulk sender, and a blind meter could spend his share."""
    import codex_advice
    adv = codex_advice.advice()
    if adv["state"] == "OK":
        return 0
    if adv["state"] == "LINE":
        return codex_advice.gate("codex_lane", adv=adv)
    print("[codex_lane] %s: no Codex job is sent" % adv.get("why"), file=sys.stderr)
    return 2


def work(job_dir, fx=None):
    """One Codex try of one ticket. Writes <job>/result.json last: {"state": built | failed | void, "why", ...}."""
    fx = fx or {}
    with open(os.path.join(job_dir, "job.json"), encoding="utf-8") as f:
        job = json.load(f)
    iid = job["item"]
    res = {"item": iid, "effect": job.get("effect"), "title": job.get("title"), "at": time.time()}

    def done(state, why, **more):
        res.update(state=state, why=why, **more)
        with open(os.path.join(job_dir, "result.json.tmp"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        os.replace(os.path.join(job_dir, "result.json.tmp"), os.path.join(job_dir, "result.json"))
        (fx.get("free") or free_clone)(res.get("clone"))
        if state == "failed":
            try:
                (fx.get("note") or note)(iid, "CODEX LANE: Codex's try is not landed: %s. The Claude lane takes the "
                                              "item again. Job: %s" % (why, job_dir))
            except Exception as e:  # noqa: BLE001 - the result stands; the note is said in it
                res["note_failed"] = "%s: %s" % (type(e).__name__, e)
        return res

    if (fx.get("gate") or gate)():
        return done("void", "refused before Codex ran: Codex is at its leave line (his share of the week)",
                    refused=True)
    try:
        clone = (fx.get("clone") or make_clone)(iid, job_dir)
    except Exception as e:  # noqa: BLE001 - no clone is a system failure, not the ticket's
        return done("void", "no scratch clone: %s: %s" % (type(e).__name__, _one(e, 300)))
    res["clone"] = clone
    # the Codex child has full file access: its state paths point at a sandbox of this job (lesson of 2026-11-17)
    sandbox, saved = os.path.join(job_dir, "sandbox"), {k: os.environ.get(k) for k in SANDBOX_KEYS}
    for k in SANDBOX_KEYS:
        os.makedirs(os.path.join(sandbox, k.lower()), exist_ok=True)
        os.environ[k] = os.path.join(sandbox, k.lower())
    try:
        r = (fx.get("codex") or run_codex)(clone, codex_prompt(job, clone), os.path.join(job_dir, "answer.md"),
                                           os.path.join(job_dir, "events.jsonl"), os.path.join(job_dir, "spend.json"))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    res["answer"] = _one((r or {}).get("result"), 2000)
    if not r or r.get("is_error"):
        return done("void", "Codex gave no answer: %s" % _one((r or {}).get("result"), 300))
    try:
        diff = (fx.get("diff") or make_diff)(clone, os.path.join(job_dir, "patch.diff"))
    except Exception as e:  # noqa: BLE001
        return done("void", "the diff could not be made: %s: %s" % (type(e).__name__, _one(e, 300)))
    if not diff.strip():
        return done("failed", "Codex changed nothing in its clone")
    verdict, out = (fx.get("check") or run_check)(job.get("effect"), clone)
    res["out"] = _one(out, 2000)
    if verdict != "holds":
        return done("failed", "its check reads %s in Codex's clone: %s" % (verdict, _one(out, 300)))
    return done("built", "the check holds in Codex's clone")


# ---- the review route -----------------------------------------------------------------------------------------------

REVIEW_ASK = """Review the code files below against their boundary page, by the brief that follows. Return one JSON
object per finding, one per line, as the brief's "What you return" says. You cannot write the clone: return your
Problems, and the run that launched you fixes them.

"""

JUDGE = """Judge a Codex code review (the Codex lane's review route, codex_lane.py review; page
design/specs/2026-11-27-codex-lane/boundary.md). You are Sonnet: each fix you make is proven by a test.

Files reviewed: {files}
Codex's findings, one JSON object per line: {out}

Steps:
1. Read src/RimMandrake/rimflow/roles/code_review.md. Codex does not apply its significance rule by itself: it calls
   rare inputs Problems. Judge each finding that Codex calls a problem by that rule, against the page and the code
   of now.
2. Fix each finding that is a Problem: a test first (red), then the fix (green). Do the polish of each file you
   change. Write each other finding as one line on the polish.md beside the page, or drop it with its reason.
3. Land with ./publish -m "codex lane review: <what>" <explicit paths>. For each file with no Problem left, record
   the read: python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path> --gpt-job {job}
4. File the fresh reader of each fix: python3 src/RimMandrake/rimflow/fresh_reader.py file --fix <sha> <paths>
"""


def page_of(rel):
    """-> the boundary pages whose Code: sentence names rel (code_review_status.code_files), in order."""
    import glob
    import code_review_status as CRS
    out = []
    for page in sorted(glob.glob(os.path.join(REPO, "design", "specs", "*", "boundary.md"))):
        try:
            if rel in CRS.code_files(page):
                out.append(os.path.relpath(page, REPO).replace(os.sep, "/"))
        except Exception:  # noqa: BLE001 - an unreadable page names nothing here
            continue
    return out


def consult(argv):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=REPO, stdin=subprocess.DEVNULL,
                       timeout=GIT_TIMEOUT_S)
    return r.returncode, ((r.stderr or "").strip().splitlines() or [""])[-1]


def review(paths, fx=None):
    """Send one review of `paths` by roles/code_review.md to Codex (gpt_consult.py), then one Sonnet judge on its
    answer. -> {"state": refused | failed | judging, ...}."""
    fx = fx or {}
    if (fx.get("gate") or gate)():
        return {"state": "refused", "why": "Codex is at its leave line (his share of the week): no review is sent"}
    rels = [os.path.relpath(os.path.abspath(p), REPO).replace(os.sep, "/") if os.path.isabs(p) else p for p in paths]
    files = []
    for rel in rels:
        files.append(rel)
        files += [p for p in page_of(rel) if p not in files]
    jobs = fx.get("jobs") or os.path.join(lane_dir(), "reviews")
    job = os.path.join(jobs, "review-%d" % int(time.time() * 1000))
    os.makedirs(job, exist_ok=True)
    ask = os.path.join(job, "ask.md")
    with open(CODE_REVIEW, encoding="utf-8") as f:
        brief = f.read()
    with open(ask, "w", encoding="utf-8") as f:
        f.write(REVIEW_ASK + brief)
    out = os.path.join(job, "findings.jsonl")
    argv = [sys.executable, os.path.join(UTILS, "gpt_consult.py"), "--prompt-file", ask, "--out", out,
            "--round", "codex-lane-review-%s" % os.path.basename(job), "--lockdown"]
    for p in files:
        argv += ["-f", p]
    rc, last = (fx.get("consult") or consult)(argv)
    if rc != 0 or not os.path.isfile(out):
        return {"state": "failed", "why": "gpt_consult exit %s: %s" % (rc, last), "job": job}
    brief = JUDGE.format(files=", ".join(rels), out=out, job=os.path.basename(job))
    rc, text, unit = (fx.get("lander") or (lambda iid, b: launch_lander(iid, b)))(fx.get("item") or ITEM, brief)
    if rc != 0 or not unit:
        return {"state": "failed", "why": "the Sonnet judge did not start: %s" % _one(text, 300), "out": out}
    return {"state": "judging", "out": out, "unit": unit, "job": job}


# ---- the commands ---------------------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("room")
    sub.add_parser("status")
    w = sub.add_parser("work")
    w.add_argument("--job", required=True)
    r = sub.add_parser("review")
    r.add_argument("paths", nargs="+")
    r.add_argument("--item", help="the ledger item the judge run works under (default: this lane's item)")
    a = ap.parse_args(argv)
    if a.cmd == "room":
        rr = room(read_notice(), time.time())
        sr = share(read_advice())
        print("room: %s: %s" % rr)
        print("Codex share: %s: %s" % ("left" if sr[0] else "not sent", sr[1]))
        print("the lane sends: %s" % ("yes" if rr[0] == SHORT and sr[0] else "no"))
        return 2 if rr[0] == COULD_NOT_LOOK else 0
    if a.cmd == "status":
        import list_dispatch as LD
        st = LD._read(os.path.join(LD.sdir(create=False), "state.json"), None)
        if st is None:
            print("COULD NOT LOOK: no state file of the ticket lane at %s" % LD.sdir(create=False))
            return 2
        cst = st.get("codex_lane") or {}
        recs = cst.get("items") or {}
        print("the Codex lane holds %d tickets; last tick: %s" % (len(recs), json.dumps(cst.get("last"))))
        for iid in sorted(recs):
            x = recs[iid]
            print("    %-64s %-10s %s" % (iid, x.get("state"), _one(x.get("why") or x.get("unit"), 120)))
        return 0
    if a.cmd == "work":
        res = work(a.job)
        print(json.dumps({k: res.get(k) for k in ("item", "state", "why")}))
        return 0
    res = review(a.paths, {"item": a.item} if a.item else None)
    print(json.dumps(res))
    return {"refused": 4, "failed": 1}.get(res["state"], 0)


if __name__ == "__main__":
    sys.exit(main())
