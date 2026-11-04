#!/usr/bin/env python3
"""status_board.py - the Relentless status board: what it is doing, what needs the owner, how each mod stands, and how
the last week went. Built by a script from readings other programs already write; it spends no AI tokens.

STATUS_PAGES_BUILD_REPLACE_RIMPULSE. Owner, by card 2026-11-03, on the hand-written mockup: "The English write-up you
provided here is superb." Every STUCK line says what is planned to unstick it and who it waits on; "Needs you (N)"
matches every needs-you tag below it; no cryptic lines; the project's dark 70s-brown look, not white ("The white is
glaring."); readable on a phone. RimPulse is retired for this page plus RUNNING_NOW.md (owner, 2026-11-03), carrying
its trend lines: errors handled and unhandled, output per day, live-test yield.

Sources (read-only): running_fleet.json (fleet_mods.gather: mods, stuck lines, Needs you; refreshed by running_now.py
every FLEET_EVERY seconds), the Relentless store (item states, journal.jsonl tick acts). running_now.py calls write()
right after each fleet refresh, so the board follows rm-running.timer; a browser tab on it reloads itself.

    python3 status_board.py            write STATUS_BOARD.html (atomic)
    python3 status_board.py --print    build it to stdout, write nothing
    python3 status_board.py --check    print its age; exit 1 when older than STALE_AFTER
"""
import argparse
import calendar
import collections
import glob
import json
import os
import sys
import time
from html import escape

AGENT = "/mnt/d/ClaudeWork/rimmandrake"
OUT_DIR = AGENT + "/conductor"
OUT = OUT_DIR + "/STATUS_BOARD.html"
FLEET_CACHE = OUT_DIR + "/running_fleet.json"
STORE = os.path.expanduser("~/rm/relentless/store")
STALE_AFTER = 3600
RELOAD_S = 300
DAYS = 7
SHOW = 5            # finished / in progress lines per mod before "and N more"

# Journal tick acts. A failure the machine caught and sent back for another try by itself is HANDLED; one that had to
# go to a person (a hold delivered to the Conductor or the owner, a jam or an alarm) is UNHANDLED.
HANDLED = ("blind_fail", "proof_weak", "proof_rework", "checker_lost", "close_retry")
UNHANDLED = ("held_delivered", "jam_alarm", "alarm")
GAME_ANSWER = ("game_implemented", "game_fail")
GAME_NO_ANSWER = ("game_unmeasured", "game_refused")
BUILDING = ("running", "candidate")
CHECKING = ("checking",)
CLOSING = ("closing",)

# warm 70s browns, the palette of project_maturity_dashboard.py (owner-approved look, 2026-09-08): red = blocked,
# yellow = waiting on him, otherwise a brown ramp.
CSS = """
:root{--bg:#171310;--panel:#211b16;--panel2:#1c1712;--line:#332a20;--ink:#efe7d9;--dim:#a99d89;--accent:#e0803a;
--f1:#63492e;--f3:#a37c49;--f5:#e6be7e;--red:#d05a3c;--yellow:#e0b13e;--green:#7fae5a;--blue:#8fb3d0}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--ink);font:15px/1.5 "IBM Plex Sans","Segoe UI",system-ui,sans-serif}
main{max-width:1060px;margin:0 auto;padding:18px 16px 60px}
.top{background:var(--panel);border:1px solid var(--line);border-left:6px solid var(--f5);border-radius:6px;padding:12px 16px}
.top.bad{border-left-color:var(--red)}
h1{font-size:20px;margin:0 0 6px}h2{font-size:16px;margin:26px 0 8px;color:var(--f5);border-bottom:1px solid var(--line);padding-bottom:4px}
h3{margin:0;font-size:16px}p{margin:5px 0}
.meta,.note{color:var(--dim);font-size:12.5px}
.box{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:8px 14px}
.needs{border-left:5px solid var(--yellow)}
ul{margin:4px 0;padding-left:20px}li{margin:4px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:10px 14px;margin:0 0 12px}
.ch{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.cnt{color:var(--dim);font-size:13.5px}
.bar{flex:0 0 140px;height:9px;background:var(--panel2);border:1px solid var(--line);border-radius:5px;overflow:hidden}
.bar span{display:block;height:100%;background:var(--f3)}
h4{margin:8px 0 2px;font-size:12.5px;text-transform:uppercase;letter-spacing:.05em}
.fin h4{color:var(--green)}.prog h4{color:var(--blue)}.stuck h4{color:var(--red)}
.who{color:var(--f5)}
.tag{font-size:11px;padding:1px 7px;border-radius:8px;white-space:nowrap;background:#4a3a12;color:var(--yellow)}
table{border-collapse:collapse;width:100%}td,th{padding:4px 8px;border-bottom:1px solid var(--line);text-align:left;font-size:13.5px}
th{color:var(--dim);font-weight:500}
.tb{display:inline-block;height:8px;background:var(--f3);border-radius:3px;vertical-align:middle;margin-right:5px}
.tb.u{background:var(--red)}.tb.h{background:var(--f1)}
details{margin-top:12px}summary{cursor:pointer;color:var(--dim)}
body{overflow-wrap:anywhere}.scroll{overflow-x:auto}
@media (max-width:640px){body{font-size:16px}main{padding:12px 8px 50px}.bar{flex-basis:100%}
.tb{display:none}td,th{padding:4px 4px;font-size:13px}}
"""


def n_words(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else (many or one + "s"))


def local_day(t):
    return time.strftime("%Y-%m-%d", time.localtime(t))


def _epoch(iso):
    try:
        return calendar.timegm(time.strptime(str(iso)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError):
        return None


def trends(journal_lines, now, days=DAYS):
    """-> [{"day", "done", "handled", "unhandled", "game_runs", "answers", "passed", "failed"}] oldest first, one row per
    local day of the last `days` (today last). Counts tick acts only (a standalone 'done' line repeats a tick's act)."""
    keys = [local_day(now - k * 86400) for k in range(days - 1, -1, -1)]
    rows = {k: collections.Counter() for k in keys}
    first = None
    for line in journal_lines:
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("do") != "tick" or not d.get("acts"):
            continue
        t = _epoch(d.get("at"))
        if t is not None and (first is None or t < first):
            first = t
        if t is None or local_day(t) not in rows:
            continue
        c = rows[local_day(t)]
        for a in d["acts"]:
            c[a.get("do")] += 1
    out = []
    for k in keys:
        c = rows[k]
        if first is None or k < local_day(first):
            out.append({"day": k, "none": True})      # before the journal's first tick: no record, never a zero
            continue
        out.append({"day": k, "done": c["done"], "handled": sum(c[x] for x in HANDLED),
                    "unhandled": sum(c[x] for x in UNHANDLED), "game_runs": c["game_prove"],
                    "answers": sum(c[x] for x in GAME_ANSWER), "passed": c["game_implemented"], "failed": c["game_fail"],
                    "no_answer": sum(c[x] for x in GAME_NO_ANSWER)})
    return out


def store_counts(store=STORE):
    """-> Counter of Relentless item statuses, or None when the store cannot be read."""
    paths = glob.glob(os.path.join(store, "items", "*", "state.json"))
    if not paths:
        return None
    c = collections.Counter()
    for p in paths:
        try:
            with open(p) as f:
                c[json.load(f).get("status")] += 1
        except (OSError, ValueError):
            c["unreadable"] += 1
    return c


def gather(now=None, cache=None, store=STORE):
    now = time.time() if now is None else now
    with open(cache or FLEET_CACHE) as f:
        fleet = json.load(f)
    try:
        with open(os.path.join(store, "journal.jsonl")) as f:
            tr = trends(f, now)
    except OSError:
        tr = None
    return {"now": now, "fleet": fleet, "states": store_counts(store), "trends": tr}


# ------------------------------------------------------------------------------------------------------------ render

def summary(d):
    """The two plain paragraphs at the top: what it is doing, and the one thing most worth knowing."""
    f = d["fleet"].get("factory") or {}
    st = d.get("states")
    lines = []
    if f.get("ok"):
        lines.append("Relentless is working: %s of %s workers busy right now." % (f.get("running", "?"), f.get("target", "?")))
    else:
        lines.append("Relentless is NOT working right now: %s." % (f.get("why") or "no reason on record"))
    if st:
        b, c, z, g = (sum(st[x] for x in BUILDING), sum(st[x] for x in CHECKING), sum(st[x] for x in CLOSING),
                      st["game"])
        lines.append("%s, %s by an independent agent, %s, %s in or waiting for the game. "
                     "%s in its queue, %s for a decision, %s on something else."
                     % (n_words(b, "item is being built", "items are being built"),
                        n_words(c, "is being checked", "are being checked"),
                        n_words(z, "has passed and is being recorded", "have passed and are being recorded"),
                        n_words(g, "item", "items"), n_words(st["queued"], "item waits", "items wait"),
                        n_words(st["held"], "is held", "are held"), n_words(st["blocked"], "waits", "wait")))
    else:
        lines.append("Its item states are UNMEASURED (the Relentless store could not be read).")
    worth = most_worth_knowing(d)
    return lines, worth


def most_worth_knowing(d):
    tr = d.get("trends")
    st = d.get("states") or collections.Counter()
    if tr and not tr[-1].get("none"):
        t = tr[-1]
        tried = t["answers"] + t["no_answer"]
        if tried >= 10 and t["answers"] * 2 < tried:
            return ("Most worth knowing: building is fast, proving things in the game is not. The game takes one test at a "
                    "time, and of %d game tests today only %d gave a real answer (%d passed, %d failed); the rest were "
                    "refused or measured nothing. Built work piles up waiting for the game."
                    % (tried, t["answers"], t["passed"], t["failed"]))
        if t["unhandled"] > max(5, t["handled"]):
            return ("Most worth knowing: more failures went to a person today (%d) than the machine handled itself (%d)."
                    % (t["unhandled"], t["handled"]))
    if st["held"] > max(10, st["queued"]):
        return ("Most worth knowing: %d items are held for the Conductor's decision, more than wait in the queue (%d)."
                % (st["held"], st["queued"]))
    f = d["fleet"].get("factory") or {}
    done = tr[-1]["done"] if tr and not tr[-1].get("none") else 0
    if st["queued"] and done:
        return ("Most worth knowing: nothing is jammed. The queue holds %d items; at today's pace (%d finished so far) "
                "that is about %s of work." % (st["queued"], done, n_words(max(1, int(round(st["queued"] / float(done)))),
                                                                            "day")))
    return "Most worth knowing: nothing is jammed%s." % ("" if f.get("ok") else ", but no worker is running")


def li(text, title=None):
    return "<li%s>%s</li>" % (' title="%s"' % escape(title) if title else "", text)


def mod_card(m):
    """One mod: counts, a progress bar, recently finished, in progress, stuck (each with plan and who it waits on)."""
    stuck = m.get("stuck") or []
    stuck_ids = {s["id"] for s in stuck}
    fin = [t for t in m.get("tasks") or [] if t.get("kind") in ("pass", "done")]
    prog = [t for t in m.get("tasks") or [] if t.get("kind") == "open" and t.get("id") not in stuck_ids]
    total = m.get("closed", 0) + m.get("open", 0) + m.get("parked", 0)
    pct = int(round(100.0 * m.get("closed", 0) / total)) if total else 0
    cnt = "%d done this week · %d open · %d stuck" % (m.get("closed", 0), max(0, m.get("open", 0) + m.get("parked", 0)
                                                                              - len(stuck)), len(stuck))
    out = ['<div class="card"><div class="ch"><h3>%s</h3><span class="cnt">%s</span>'
           '<div class="bar" title="%d%% of this week\'s items done"><span style="width:%d%%"></span></div></div>'
           % (escape(m["name"]), escape(cnt), pct, pct)]

    def block(cls, head, rows, more=0):
        if not rows:
            return
        out.append('<div class="%s"><h4>%s</h4><ul>%s%s</ul></div>' % (cls, head, "".join(rows),
                   "<li class=\"note\">and %d more</li>" % more if more else ""))
    block("fin", "Recently finished",
          [li(escape(t["title"]) + ("" if t.get("kind") == "pass" else ' <span class="note">(not yet re-checked by an '
                                    'independent agent)</span>'), t.get("id")) for t in fin[:SHOW]], max(0, len(fin) - SHOW))
    block("prog", "In progress", [li(escape(t["title"]), t.get("id")) for t in prog[:SHOW]], max(0, len(prog) - SHOW))
    block("stuck", "Stuck", [li(stuck_text(s), s.get("id")) for s in stuck])
    out.append("</div>")
    return "".join(out)


def stuck_text(s):
    tag = ' <span class="tag">needs you</span>' if s["waits"] == "you" else ""
    plan = s["plan"][:1].upper() + s["plan"][1:]
    return "%s%s<br><span class=\"note\">Planned: %s. Waits on: <span class=\"who\">%s</span>.</span>" % (
        escape(s["title"]), tag, escape(plan.rstrip(".")), escape(s["waits"]))


def mod_of_items(mods):
    out = {}
    for m in mods:
        for s in m.get("stuck") or []:
            out.setdefault(s["id"], m["name"])
    return out


def render(d):
    now = d["now"]
    fleet = d["fleet"]
    lines, worth = summary(d)
    f = fleet.get("factory") or {}
    needs = (fleet.get("needs") or {}).get("lines") or []
    mods = fleet.get("mods") or []
    where = mod_of_items(mods)
    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<meta http-equiv="refresh" content="%d">' % RELOAD_S,
         '<title>Relentless: what it is doing</title><style>%s</style></head><body><main>' % CSS,
         '<div class="top%s"><h1>%s</h1><p>%s</p><p>%s</p>' % ("" if f.get("ok") else " bad", escape(lines[0]),
                                                               escape(lines[1]), escape(worth))]
    age = now - (fleet.get("good_t") or fleet.get("t") or 0)
    h.append('<p class="meta">Built %s by a script from the Relentless records; no AI tokens. Mod data is %s old. '
             '"Finished" means an independent agent re-ran the item\'s proof and it passed, unless the line says it is '
             'not yet re-checked. This tab reloads itself every %d minutes. Hover a line for its internal name.</p></div>'
             % (time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(now)), ago(age), RELOAD_S // 60))
    if fleet.get("why"):
        h.append('<p class="note">The last mod refresh failed (%s); this shows the last good one.</p>' % escape(fleet["why"]))

    h.append('<h2>Needs you (%d)</h2><div class="box needs">' % len(needs))
    if needs:
        h.append("<ul>%s</ul>" % "".join(li("%s%s" % (escape(n["q"]), ' <span class="note">(%s)</span>' % escape(where[n["item"]])
                                                 if n["item"] in where else ""), n["item"]) for n in needs))
        h.append('<p class="note">Each comes to you as a question card from the Conductor. A <span class="tag">needs you'
                 '</span> tag below is always one of these.</p>')
    else:
        h.append("<p>Nothing waits on you.</p>")
    h.append("</div>")

    h.append(trend_table(d.get("trends")))

    real = [m for m in mods if not (m.get("infra") or m.get("cross"))]
    rest = [m for m in mods if m.get("infra") or m.get("cross")]
    h.append('<h2>By mod <span class="note">(touched in the last %d days)</span></h2>' % DAYS)
    h.extend(mod_card(m) for m in real)
    if rest:
        h.append("<details><summary>Tooling and cross-mod work (%d)</summary>%s</details>"
                 % (len(rest), "".join(mod_card(m) for m in rest)))
    h.append("</main></body></html>")
    return "\n".join(h)


def trend_table(tr):
    if not tr:
        return '<h2>The last week</h2><p class="note">UNMEASURED: the Relentless journal could not be read.</p>'
    top = max([1] + [max(r["done"], r["handled"], r["unhandled"]) for r in tr if not r.get("none")])
    bar = lambda n, cls="": '<span class="tb %s" style="width:%dpx"></span>' % (cls, int(60.0 * n / top))  # noqa: E731
    rows = []
    for r in tr:
        day = time.strftime("%a %-d %b", time.strptime(r["day"], "%Y-%m-%d"))
        if r.get("none"):
            rows.append('<tr><td>%s</td><td colspan="4" class="note">no record (the journal starts later)</td></tr>' % day)
            continue
        tried = r["answers"] + r["no_answer"]
        yld = "%d of %d (%d%%)" % (r["answers"], tried, int(round(100.0 * r["answers"] / tried))) if tried else "none run"
        rows.append("<tr><td>%s</td><td>%s%d</td><td>%s%d</td><td>%s%d</td><td>%s</td></tr>" % (
            day, bar(r["done"]), r["done"],
            bar(r["handled"], "h"), r["handled"], bar(r["unhandled"], "u"), r["unhandled"], yld))
    return ('<h2>The last week</h2><div class="box"><div class="scroll"><table><tr><th>Day</th><th>Finished</th><th>Errors handled</th>'
            '<th>Errors to a person</th><th>Game tests with a real answer</th></tr>%s</table></div>'
            '<p class="note">Finished: items that passed their independent check. Errors handled: failures the machine '
            'caught and sent back for another try by itself (a failed check, a weak proof, a lost checker). Errors to a '
            'person: holds handed to the Conductor or you, jams and alarms. A game test with no real answer was refused '
            'or measured nothing.</p></div>' % "".join(rows))


def ago(s):
    s = max(0, int(s))
    return "%d s" % s if s < 90 else "%d min" % (s // 60) if s < 5400 else "%.1f h" % (s / 3600.0)


def write(now=None, out=OUT, cache=None):
    page = render(gather(now, cache))
    tmp = "%s.tmp.%d" % (out, os.getpid())
    with open(tmp, "w") as f:
        f.write(page)
    os.replace(tmp, out)
    return out


def check(out=OUT):
    try:
        age = time.time() - os.stat(out).st_mtime
    except OSError as e:
        print("STATUS_BOARD.html: UNMEASURED (%s)" % e)
        return 1
    print("STATUS_BOARD.html is %s old%s" % (ago(age), "" if age <= STALE_AFTER else " - STALE (limit 1 h)"))
    return 0 if age <= STALE_AFTER else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--print", action="store_true", dest="show")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        return check()
    if a.show:
        sys.stdout.write(render(gather()))
        return 0
    print(write())
    return 0


if __name__ == "__main__":
    sys.exit(main())
