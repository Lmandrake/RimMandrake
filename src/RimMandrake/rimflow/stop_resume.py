#!/usr/bin/env python3
"""stop_resume: a detached run that a fleet stop killed is brought back by itself (RIMMANDRAKE_CHECKPOINT_HARD_STOP_NOT_KILL).

An account switch (`claude-account use`, the plan's or a hand's) and the plan's hard stop (`claude-account fleet-stop`)
SIGTERM every Claude process. A detached run dies with no result JSON; its finish and return steps record the kill
and bundle the clone, and until 2026-11-17 nothing relaunched it (the 03:35 hard stop killed a 3 h 40 min Fable run;
a hand relaunched it at 05:57). Forensics: D:\\ClaudeWork\\rimmandrake\\conductor\\mass_kill_20261117_0335.md.

  scan    read-only: each killed run on a stop and what the sweep would do with it
  sweep   resume each one (the same session when its transcript is there, else its saved brief plus a note), park it
          while no account has headroom (the plan's newest pass is soft, stop or stopped), mark one already relaunched
  kick    scan, and start `sweep` as its own unit when there is work (switching_plan.check calls this every pass)

A run is resumed when detached_helper.killed() says it was killed (a run that wrote its result never is), its end
falls on a stop (or it has no end and a stop came after its launch), no later run of its item exists, its item is
still open, it is not the maturation tick's (that tick retries the runs in its own books,
RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT) and its return step is done. A note never states spend,
a limit or what is left of one (Conductor brief 2026-11-17).

Not seen: a bare `claude-account fleet-stop` neither the plan nor `use` logged. With the plan's HOLD set or its timer
stopped nothing kicks a sweep (run `stop_resume.py sweep` by hand).
"""
import argparse
import datetime
import fcntl
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import failure_class as FC  # noqa: E402

REPO = DH.REPO
PLAN_DIR = os.environ.get("RM_SWITCH_PLAN_DIR", "/mnt/d/ClaudeWork/rimmandrake/switching_plan")   # switching_plan.OUT
ACCT_LOG = os.path.join(os.environ.get("RM_ACCOUNTS_DIR", os.path.expanduser("~/.claude-accounts")), "log.jsonl")
# a kill belongs to a stop logged up to 15 min after it: `use` logs after its stop AND the fleet relaunch, and the plan
# gives `use` 600 s (rimflow-operations skill, traps); the plan's own stop line came 2 s after the 03:35:15.9 kill
BEFORE_S = 900
AFTER_S = 120          # finish stamps `ended` once systemd has run it: after the kill, not before
# a hard stop stands until some account refills; every weekly cap refills within 7 d, so a run parked by a stop is
# still read on the first pass with headroom (32 h was the longest measured, 03:35 -> 11:59 next day)
STOP_LOOKBACK_S = 8 * 86400
LAUNCH_LOOKBACK_S = 10 * 86400   # runs launched longer ago are read only if their record was written since STOP_LOOKBACK_S
# stops before this landed were handled by hand (the 2026-11-17 morning kills were relaunched 05:57 and 06:04)
CUTOFF = datetime.datetime(2026, 11, 17, 16, 30, tzinfo=datetime.timezone.utc).timestamp()
FRESH_S = 20 * 60      # switching_plan.NOTICE_FRESH_S: an older reading means the plan's timer stopped
CLAIM_S = 900          # a claim older than this is a sweep that died mid-launch (the later-record check still holds)
MAX_TRIES = 3          # a resume refused this many times is said so, and then tried every REFUSED_WAIT_S
# the danger: a launch sent again on every pass into the same refusal (the night of 2026-11-20, REPAIR_LAUNCH_MOST)
REFUSED_WAIT_S = 3600
RETURN_GRACE_S = DH.RETURN_WAIT_S + 300     # a return not done by then is not waited for
# a run's own transcript begins within 64 s of its launch (427 runs on 2026-11-17, measured: clone sync, then claude)
SESSION_START_S = 300
# "grace": a switch is held a few minutes for the checkpoint signal (RIMMANDRAKE_CHECKPOINT_SIGNAL_BEFORE_SOFT_SWITCH):
# a run resumed then is killed again by it
NO_HEADROOM = ("soft", "stop", "stopped", "grace")
DECISIONS = ("normal", "soft", "switch", "stop", "stopped", "start", "hold", "poll", "passive", "grace")
ACTIONABLE = ("resume", "park", "mark", "refuse", "give_up", "say_refused")
SWEEP_UNIT = "rm-stop-resume"


def epoch(s):
    if isinstance(s, (int, float)):
        return float(s)
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def local(t):
    return time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(t))


def jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def stop_events(plan_dir=None, acct_log=None, now=None, cutoff=CUTOFF):
    """-> [{ts, kind: switch|stop, what}], oldest first: the plan's acted `use`/`fleet-stop` that returned 0 and
    claude-account's own `use` lines that changed the account (a hand switch shows only there)."""
    now = now or time.time()
    out = []
    for r in jsonl(os.path.join(plan_dir or PLAN_DIR, "log.jsonl")):
        if not r.get("acted") or r.get("dry"):
            continue
        # a failed switch off a spent account stops the fleet as its fallback; that stop is logged under `brake`
        for key, res in list((r.get("result") or {}).items()) + list((r.get("brake") or {}).items()):
            if key in ("use", "fleet-stop") and isinstance(res, list) and res and res[0] == 0:
                kind = "switch" if key == "use" else "stop"
                out.append({"ts": epoch(r.get("at")), "kind": kind,
                            "what": ("%s -> %s" % (r.get("live"), r.get("to"))) if kind == "switch" else (r.get("why") or "")})
    for r in jsonl(acct_log or ACCT_LOG):
        if r.get("op") == "use" and r.get("changed"):
            out.append({"ts": epoch(r.get("ts")), "kind": "switch", "what": "%s -> %s" % (r.get("from"), r.get("to"))})
    return sorted((e for e in out if e["ts"] and cutoff <= e["ts"] <= now + 60 and e["ts"] >= now - STOP_LOOKBACK_S),
                  key=lambda e: e["ts"])


def headroom(plan_dir=None, now=None):
    """-> (bool, why): may a killed run be relaunched now? No while the plan's newest pass (<= 20 min old) is soft, stop or
    stopped, or its act failed; with no fresh pass, the notice decides (state none and fresh)."""
    now = now or time.time()
    d = plan_dir or PLAN_DIR
    passes = [r for r in jsonl(os.path.join(d, "log.jsonl")) if r.get("do") in DECISIONS and not r.get("dry")]
    last = passes[-1] if passes else None
    t = epoch((last or {}).get("at"))
    if last and t and now - t <= FRESH_S and last.get("do") != "passive":
        do = last["do"]
        if do in NO_HEADROOM:
            return False, "the plan's pass at %s reads %s" % (local(t), do)
        bad = [k for k, v in (last.get("result") or {}).items() if isinstance(v, list) and v and v[0] != 0]
        if last.get("acted") and bad:
            return False, "the plan's %s at %s failed (%s)" % (do, local(t), ", ".join(bad))
        return True, "the plan's pass at %s reads %s" % (local(t), do)
    try:
        with open(os.path.join(d, "notice.json"), encoding="utf-8") as f:
            n = json.load(f)
    except (OSError, ValueError):
        n = {}
    nt = epoch(n.get("at"))
    if n.get("state") == "none" and nt and now - nt <= FRESH_S:
        return True, "the plan's notice at %s reads none" % local(nt)
    return False, "no fresh plan reading (newest pass %s, notice %s)" % (
        local(t) if t else "none", ("%s at %s" % (n.get("state"), local(nt))) if nt else "none")


def launched_at(name):
    m = re.search(r"-(\d{9,11})$", name)
    return int(m.group(1)) if m else None


def recent_records(root, now):
    d = DH.runs_dir(root)
    try:
        names = os.listdir(d)
    except OSError:
        return []
    out = []
    for n in names:
        u = DH.record_unit(n)       # a run record by name, never another writer's file (detached_helper.RECORD_NAME)
        if not u:
            continue
        t = launched_at(u)
        if t is not None and t < now - LAUNCH_LOOKBACK_S:
            try:     # an old launch is still read while its record was written within the stop lookback (a long run
                fresh = os.stat(os.path.join(d, n)).st_mtime >= now - STOP_LOOKBACK_S    # that died lately, or a parked one)
            except OSError:
                fresh = False
            if not fresh:
                continue
        rec = DH.read_record(u, root)
        if DH.is_record(rec, u) and rec.get("item"):
            out.append(rec)
    return out


def maturation_units(repo):
    """-> the text of every maturation book: a unit named in one is the maturation tick's to retry."""
    texts = []
    for p in glob.glob(os.path.join(repo, "design", "concepts", "*", "version", "stage_record.json")):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                texts.append(f.read())
        except OSError:
            continue
    return "\n".join(texts)


def item_closed(repo, item):
    items = os.path.join(repo, "infrastructure", "state", "items")
    return os.path.isfile(os.path.join(items, "closed", item + ".md")) and not os.path.isfile(os.path.join(items, item + ".md"))


def first_ts(path, lines=60):
    return opening(path, lines)[0]


def opening(path, lines=60):
    """-> (first timestamp, entrypoint, first user prompt) of a transcript, each None when its first `lines` lines lack
    it (the prompt is within them in 436 of 436 runs' own transcripts, measured)."""
    t = ep = prompt = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(lines):
                ln = f.readline()
                if not ln:
                    break
                try:
                    d = json.loads(ln)
                    t = t or epoch(d.get("timestamp"))
                    ep = ep or d.get("entrypoint")
                    if prompt is None and d.get("type") == "user":
                        c = (d.get("message") or {}).get("content")
                        if isinstance(c, list):
                            c = " ".join(str(x.get("text") or "") for x in c if isinstance(x, dict))
                        prompt = c if isinstance(c, str) else ""
                except (ValueError, AttributeError):
                    continue
                if t and ep and prompt is not None:
                    break
    except OSError:
        pass
    return t, ep, prompt


def brief_head(rec, n=200):
    """-> the opening of the brief the run was launched with, or None (runs launched before brief_src landed)."""
    try:
        with open(rec.get("brief_src") or "/nonexistent", encoding="utf-8", errors="replace") as f:
            return " ".join(f.read(4 * n).split())[:n] or None
    except OSError:
        return None


def session_of(rec, projects=None):
    """-> the run's session id whose transcript exists, or None: the record's own resume_session, else the transcript in
    its clone's project folder that began at its launch and whose first prompt is this run's: it names the run's item
    (the launch footer does; 436 of 436 runs' own transcripts did, and the 3 other sessions begun at a launch did not,
    measured 2026-11-17) and, where the brief was saved, opens with its brief. The earliest such."""
    sid = rec.get("resume_session")
    if sid and DH.find_transcript(sid, projects):
        return sid
    at, item, head = rec.get("at") or 0, rec.get("item") or "", brief_head(rec)
    best = None
    for p in glob.glob(os.path.join(DH.project_dir(rec.get("clone") or "/nonexistent", projects), "*.jsonl")):
        stem = os.path.basename(p)[:-6]
        t, ep, prompt = opening(p)
        if not DH.SESSION_RE.match(stem) or t is None or not (at - 2 <= t <= at + SESSION_START_S):
            continue
        if ep == "cli":  # an interactive window's session; a detached run's is "sdk-cli" (427 of 427 found, measured)
            continue
        flat = " ".join((prompt or "").split())
        if item not in flat or (head and head not in flat):
            continue     # another session begun in the clone at the launch (a hand's, a hook test's, another run's)
        if best is None or t < best[0]:
            best = (t, stem)
    return best[1] if best else None


def on_stop(rec, stops):
    """-> the stop that killed the run, or None."""
    end, at = rec.get("ended"), rec.get("at") or 0
    for s in stops:
        if end:
            if s["ts"] - BEFORE_S <= end <= s["ts"] + AFTER_S:
                return s
        elif s["ts"] > at:
            return s
    return None


def relaunch_of(rec, stop, siblings, victim=lambda x: False):
    """-> the unit of a run of the same item launched after this one died (a hand or sweep relaunch), or None. A run
    launched before the death is a second run that may have died at the same stop, a run `victim` says this stop
    killed too is a twin, never a relaunch, and one resumed from another stopped run is that run's relaunch."""
    died = rec.get("ended") or (stop["ts"] - BEFORE_S)
    later = sorted((x for x in siblings if x["unit"] != rec["unit"] and (x.get("at") or 0) > max(rec.get("at") or 0, died - 60)
                    and x.get("status") not in ("launch_failed", "refused") and x.get("resumed_from") in (None, rec["unit"])
                    and not victim(x)),
                   key=lambda x: x.get("at") or 0)
    return later[0]["unit"] if later else None


def classify(rec, stops, siblings, ctx, now):
    """-> None (nothing to do with it) or {unit, item, act, why, stop?}."""
    unit, item = rec["unit"], rec["item"]
    base = {"unit": unit, "item": item}
    if rec.get("resumed_by") or rec.get("resume_gave_up") or rec.get("resume_refused"):
        return None
    st = rec.get("status")
    if st == "finished" and not str(rec.get("result") or "").startswith("killed"):
        return None
    if st not in ("finished", "running", "launching"):
        return None
    stop = on_stop(rec, stops)
    if not stop:
        return None
    if not DH.killed(rec, ctx["runner"], now):
        return None
    base["stop"] = stop
    claims = [y["resume_claim"] for y in siblings if y["unit"] != unit and y.get("resume_claim") and not y.get("resumed_by")]
    taken = {y.get("resumed_by") for y in siblings if y["unit"] != unit}

    def victim(x):  # launched before this stop, killed by it: a twin that needs its own resume; or another stopped
        # run's relaunch: named as its successor, or launched after its claim that never got the successor's name (a
        # sweep that died mid-launch, before it could write resumed_from)
        if x["unit"] in taken or (not x.get("resumed_from") and any(c <= (x.get("at") or 0) for c in claims)):
            return True
        return ((x.get("at") or 0) < stop["ts"] and on_stop(x, [stop]) is stop and not x.get("resumed_from")
                and DH.killed(x, ctx["runner"], now))
    later = relaunch_of(rec, stop, siblings, victim)
    if later:
        return {**base, "act": "mark", "why": "already relaunched as %s" % later, "by": later}
    if unit in ctx["books"]:
        return {**base, "act": "skip", "why": "the maturation tick retries it (named in its books)"}
    if item_closed(ctx["repo"], item):
        return {**base, "act": "skip", "why": "%s is closed" % item}
    if st == "finished" and not rec.get("returned") and now - (rec.get("ended") or now) < RETURN_GRACE_S:
        return {**base, "act": "wait", "why": "its return step is not done yet"}
    claim = rec.get("resume_claim")
    if claim and now - claim < CLAIM_S:
        return {**base, "act": "wait", "why": "another sweep claimed it at %s" % local(claim)}
    n, last = int(rec.get("resume_attempts") or 0), str(rec.get("resume_last_refusal") or "")
    if n >= MAX_TRIES:
        why = "refused %d times (last: %s)" % (n, last)
        if FC.of_launch(last).counts:
            return {**base, "act": "give_up", "why": why}
        # a launch that never started spends no resume (failure_class): it is said once, then tried every REFUSED_WAIT_S
        if not rec.get("resume_refused_said"):
            return {**base, "act": "say_refused", "why": why}
        due = (rec.get("resume_refused_at") or 0) + REFUSED_WAIT_S
        if now < due:
            return {**base, "act": "wait", "why": "%s; the next try from %s" % (why, local(due))}
    sid = session_of(rec, ctx["projects"])
    brief = None
    if not sid:
        try:
            with open(rec.get("brief_src") or "/nonexistent", encoding="utf-8") as f:
                brief = f.read()
        except OSError:
            brief = None
        if not (brief or "").strip():
            return {**base, "act": "refuse", "why": "no transcript and no saved brief: it cannot be relaunched by "
                                                   "itself; relaunch it by hand"}
    if not ctx["headroom"][0]:
        if rec.get("parked"):
            return {**base, "act": "parked", "why": ctx["headroom"][1]}
        return {**base, "act": "park", "why": ctx["headroom"][1]}
    return {**base, "act": "resume", "session": sid, "brief": brief,
            "why": ("the same session %s" % sid) if sid else "its saved brief (no transcript)"}


def scan(now=None, root=None, plan_dir=None, acct_log=None, repo=None, projects=None, runner=subprocess.run,
         cutoff=CUTOFF, only=None):
    """-> [{unit, item, act, why, ...}] for every recent run a stop killed (or the one named `only`). Reads only."""
    now = now or time.time()
    stops = stop_events(plan_dir, acct_log, now, cutoff)
    if not stops:
        return []
    recs = recent_records(root, now)
    by_item = {}
    for r in recs:
        by_item.setdefault(r["item"], []).append(r)
    ctx = {"runner": runner, "repo": repo or REPO, "projects": projects, "books": maturation_units(repo or REPO),
           "headroom": headroom(plan_dir, now)}
    out = []
    for r in sorted(recs, key=lambda x: x.get("at") or 0):
        if only and r["unit"] != only:
            continue
        x = classify(r, stops, by_item[r["item"]], ctx, now)
        if x:
            out.append(x)
    return out


def how_stopped(stop):
    if stop["kind"] == "switch":
        return "an account switch (%s)" % stop["what"]
    return "a hard stop of the whole fleet (no account had headroom)"


def given_clone(rec):
    """-> the clone the stopped run was handed (`--clone`, kept by its return), or None: a pool clone is synced afresh."""
    c = rec.get("clone")
    return c if str(rec.get("clone_how") or "").startswith("given ") and c and os.path.isdir(c) else None


def note(rec, x, now):
    """The resume prompt (same session) or the head of the relaunch brief. Never a word on spend or its limit."""
    stop = x["stop"]
    parked = rec.get("parked")
    lines = ["RESUMED AFTER A FLEET STOP (stop_resume.py, %s)." % local(now),
             "Your run %s on %s was stopped at %s by %s%s. That was not your doing, and nothing is wrong with the work."
             % (rec["unit"], rec["item"], local(stop["ts"]), how_stopped(stop),
                (", and parked until an account had headroom again") if parked else "")]
    if given_clone(rec):
        where = "You are back in the clone you were given, %s, as it stood when you stopped." % rec["clone"]
    else:
        where = "Your clone now stands on origin/main: what you had not published is not in it."
    if x.get("session"):
        lines.append("This is the same session, resumed: everything above is your own earlier work. " + where)
    else:
        lines.append("This is a fresh session with no memory of the stopped one: its brief follows below this note, "
                     "unchanged. " + where)
    if rec.get("bundle"):
        lines.append("What the stopped run had not published was saved in %s: HEAD (the commit it stood on), "
                     "diff.patch (apply it with `git apply`), untracked.tar (`tar -xf` it in the clone) and deleted "
                     "(the paths it had removed). Restore what is still wanted." % rec["bundle"])
    elif rec.get("status") in ("running", "launching"):
        lines.append("Its return step never ran: its old clone may still stand at %s with unpublished work in it."
                     % rec.get("clone"))
    else:
        lines.append("Its return step saved no unpublished work.")
    lines.append("First read `git log --oneline -15` and `python3 src/RimMandrake/rimflow/cli.py show %s`; do not redo "
                 "work that is already published. Then carry on with %s from where it stopped." % (rec["item"], rec["item"]))
    text = "\n".join(lines) + "\n"
    if x.get("brief"):
        text += "\n---- the stopped run's brief ----\n" + x["brief"].rstrip() + "\n"
    return text


def with_card_text(item, text, repo):
    """A by-card item's brief must carry the picked option's words (detached_helper.card_refusal): add any missing."""
    try:
        import card_capture
        cards = card_capture.item_cards(item, events_dir=os.path.join(repo, DH.EVENTS_REL))
        missing = card_capture.brief_missing(text, cards)
    except Exception:  # noqa: BLE001  the launch's own gate still decides
        return text
    if missing:
        text += "\nWhat the card said:\n" + "\n".join("- " + m for m in missing) + "\n"
    return text


def say(text, now, path=None):
    try:
        DH.conductor_line(text, now, path=path, head="STOP RESUME")
    except Exception as e:  # noqa: BLE001  a log that cannot be written never stops a resume
        print("conductor log not written: %s" % e, file=sys.stderr)


def journal(root, row):
    try:
        with open(os.path.join(DH.runs_dir(root), "stop_resume.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError:
        pass


def resume(rec, x, now, root, repo, projects, launch_fn, log_path):
    unit = rec["unit"]
    rec["resume_claim"] = now
    DH.write_record(rec, root)
    brief = with_card_text(rec["item"], note(rec, x, now), repo)
    max_s = rec.get("max_s") or "none"
    try:
        code, text = launch_fn(rec.get("seat"), rec["item"], brief, rec.get("model"), max_s,
                               rec.get("budget_usd") or 0.0, now=now, env=rec.get("env") or None,
                               resume_session=x.get("session"), projects=projects, clone=given_clone(rec),
                               skip_launch_checks="resume of %s after a fleet stop: the same run, whose launch checks "
                                                  "already ran" % unit)
    except Exception as e:  # noqa: BLE001
        code, text = 1, "%s: %s" % (type(e).__name__, e)
    rec = DH.read_record(unit, root) or rec
    rec.pop("resume_claim", None)
    m = re.match(r"DETACHED (\S+)", text or "")
    if code == 0 and m:
        new = m.group(1)
        rec.update({"resumed_by": new, "resumed_at": now, "resume_how": "session" if x.get("session") else "brief"})
        DH.write_record(rec, root)
        nr = DH.read_record(new, root)
        if nr:
            nr["resumed_from"] = unit
            DH.write_record(nr, root)
        say("resumed %s (%s, stopped %s by %s) as %s, %s" % (unit, rec["item"], local(x["stop"]["ts"]),
                                                         how_stopped(x["stop"]), new, x["why"]), now, log_path)
        return {**x, "act": "resumed", "new": new}
    rec["resume_attempts"] = int(rec.get("resume_attempts") or 0) + 1
    rec["resume_last_refusal"] = str(text)
    rec["resume_refused_at"] = now
    DH.write_record(rec, root)
    return {**x, "act": "refused_launch", "why": str(text)}


def sweep(now=None, root=None, plan_dir=None, acct_log=None, repo=None, projects=None, launch_fn=None,
          runner=subprocess.run, cutoff=CUTOFF, log_path=None, dry=False, clock=None):
    """-> [{unit, act, why, ...}]: what each killed run got. One sweep at a time (a lock in the runs dir). `clock`
    gives the time of each per-run decision (the wall clock in a real sweep; a given `now` stands still in a test)."""
    clock = clock or ((lambda: now) if now else time.time)
    now = now or time.time()
    repo = repo or REPO
    launch_fn = launch_fn or DH.launch
    os.makedirs(DH.runs_dir(root), exist_ok=True)
    with open(os.path.join(DH.runs_dir(root), "stop_resume.lock"), "a") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return [{"unit": "-", "act": "busy", "why": "another sweep holds the lock"}]
        found = scan(now, root, plan_dir, acct_log, repo, projects, runner, cutoff)
        if dry:
            return found
        out = []
        for x in found:
            # decided afresh just before acting: a resume before it may have taken minutes, in which a hand relaunch
            # can appear or the plan can stop the fleet (one scan for the whole sweep would act on both stale)
            now = clock()  # a pass that has aged out since the sweep began is no headroom
            fresh = scan(now, root, plan_dir, acct_log, repo, projects, runner, cutoff, only=x["unit"])
            rec = DH.read_record(x["unit"], root)
            if not rec or not fresh:
                continue
            x = fresh[0]
            act = x["act"]
            if act == "mark":
                rec["resumed_by"] = x["by"]
                DH.write_record(rec, root)
            elif act == "park":
                rec["parked"] = {"at": now, "why": x["why"]}
                DH.write_record(rec, root)
                say("parked %s (%s), stopped %s by %s: %s; resumed by the first plan pass with headroom"
                    % (x["unit"], x["item"], local(x["stop"]["ts"]), how_stopped(x["stop"]), x["why"]), now, log_path)
            elif act == "refuse":
                rec["resume_refused"] = {"at": now, "why": x["why"]}
                DH.write_record(rec, root)
                say("NOT resumed %s (%s), stopped %s by %s: %s" % (x["unit"], x["item"], local(x["stop"]["ts"]),
                                                                   how_stopped(x["stop"]), x["why"]), now, log_path)
                x = {**x, "act": "refused"}
            elif act == "say_refused":
                rec["resume_refused_said"] = {"at": now, "why": x["why"]}
                DH.write_record(rec, root)
                say("resume of %s (%s) %s; it is tried again every %d min until the cause clears" % (
                    x["unit"], x["item"], x["why"], REFUSED_WAIT_S // 60), now, log_path)
            elif act == "give_up":
                rec["resume_gave_up"] = {"at": now, "why": x["why"]}
                DH.write_record(rec, root)
                say("gave up resuming %s (%s): %s; relaunch it by hand" % (x["unit"], x["item"], x["why"]), now, log_path)
                x = {**x, "act": "gave_up"}
            elif act == "resume":
                x = resume(rec, x, now, root, repo, projects, launch_fn, log_path)
            out.append(x)
            if x["act"] not in ("wait", "parked", "skip"):
                journal(root, {"at": DH.iso(now), **{k: v for k, v in x.items() if k != "brief"}})
        return out


def kick(now=None, runner=subprocess.run, **kw):
    """-> one line: scan, and start the sweep as its own transient unit when something is owed (the plan's pass stays
    short: a resume takes a clone, minutes). The fixed unit name keeps it to one at a time."""
    found = [x for x in scan(now=now, runner=runner, **kw) if x["act"] in ACTIONABLE]
    if not found:
        return "stop_resume: nothing owed"
    argv = ["--user", "--quiet", "--collect", "-p", "RuntimeMaxSec=10800",
            "--", "/usr/bin/python3", os.path.abspath(__file__), "sweep"]
    import control as C     # the one admission point (control.py)
    r = C.launch_unit(argv, {"family": "stop_resume", "unit": SWEEP_UNIT, "reuse_name": True}, runner=runner, capture_output=True, text=True,
                      timeout=60, stdin=subprocess.DEVNULL)
    return "stop_resume: %d owed (%s); sweep unit %s" % (
        len(found), ", ".join("%s %s" % (x["act"], x["unit"]) for x in found[:6]),
        "started" if r.returncode == 0 else "not started (%s)" % ((r.stderr or r.stdout or "").strip()[:200]))  # cut-ok: terminal display


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("scan", "sweep", "kick"))
    ap.add_argument("--dry-run", action="store_true", help="sweep: say what it would do, change nothing")
    a = ap.parse_args(argv)
    if a.cmd == "kick":
        print(kick())
        return 0
    rows = scan() if a.cmd == "scan" else sweep(dry=a.dry_run)
    stops = stop_events()
    print("stops read: %d (newest %s); headroom: %s" % (len(stops), local(stops[-1]["ts"]) if stops else "none",
                                                        "%s, %s" % headroom()))
    for x in rows:
        print("%-12s %s  %s  %s" % (x["act"], x["unit"], x.get("item", ""), x.get("why", "")))
    print("%d run(s)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
