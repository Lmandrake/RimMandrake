#!/usr/bin/env python3
"""maturation_trend.py: tickets by hour for the last five days, from the rimflow ledger. No model, no tokens.

Item RIMMANDRAKE_REDRAW_NONMOD_PAGE_HALF_SLEEK_SUMMARY_NOT_LOG_BARF. The owner, 2026-11-23: "of the tickets NOT held
(due to staleness, old mods, etc), not many are waiting, being worked, and have been completed as a function of hour for
the past five days would be a great start. ... waiting(mod), waiting(non-mod), opened(mod), opened(non-mod),
closed(mod), closed(non-mod)". Boundary page: design/specs/2026-11-23-ticket-trend-graph/boundary.md. Tests:
selftest_maturation_trend.py.

hours() folds the ledger once through rimflow's own model.replay and looks at every open ticket at the end of each clock
hour (Pacific). ops() lays the graph out as drawing primitives; svg() and the phone page each draw those primitives.
"""
import datetime as dt
import glob
import html
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import item_identity  # noqa: E402
from list_pipeline import epoch  # noqa: E402  a time from a number or an ISO text; None when it has none

PAC = ZoneInfo("America/Los_Angeles")
UNM = "UNMEASURED"
HOURS = 120          # five days of clock hours, as he asked
DAY = 86400
# A ticket nobody filed, took up or ran in this many days is left out as stale. Danger: the old backlog hides the week's
# change. Evidence: 2026-11-23, over 600 of 1,174 open non-mod tickets had no act in seven days.
# budget: danger=the old backlog hides the week's change; ends no work: the trend leaves the ticket out
STALE_DAYS = 7
CLASSES = ("nonmod", "mod")
GROUPS = ("held", "oldmod", "later", "parked", "stale")
GROUP_WORDS = {"held": "on a mod you hold", "oldmod": "on an old mod (not in the mod pipeline)",
               "later": "for a later version", "parked": "parked (blocked, or a date not come)",
               "stale": "stale (not filed or worked in %d days)" % STALE_DAYS}
# The acts that keep a ticket from being stale. A note, a re-homing or a program's re-check is not one: sweeps write
# those onto hundreds of old tickets at once.
WORK_ACTS = ("file", "spawn", "claim", "start", "implemented", "finding", "shape", "effect", "block", "unblock", "wait",
             "unwait", "verify", "reclaim")
PROGRAM_SEATS = ("RUNNER", "DISPATCHER")


def held_mods():
    """The mods on the owner's hold list (mod_owner_hold.py's mirror). Raises when it cannot be read."""
    with open(os.path.join(REPO, "src", "RimMandrake", "rimflow", "mod_owner_hold.json"), encoding="utf-8") as f:
        return {str(h["mod"]) for h in json.load(f)["holds"]}


def old_mods(page_mods, root=REPO):
    """Every mod folder with an About.xml that is not on the page."""
    return sorted({os.path.basename(os.path.dirname(os.path.dirname(p)))
                   for p in glob.glob(os.path.join(root, "src", "*", "*", "About", "About.xml"))} - set(page_mods))


def names_old_mod(iid, title, tokens):
    """Whether an id or a title holds an old mod's whole name (`tokens`: the squashed upper-case names)."""
    for words in ([w for w in str(iid or "").upper().split("_") if w],
                  re.findall(r"[A-Z0-9]+", str(title or "").upper())):
        for n in (1, 2, 3):
            for i in range(len(words) - n + 1):
                if "".join(words[i:i + n]) in tokens:
                    return True
    return False


# ---- the replay ---------------------------------------------------------------------------------------------------

class _Shadow(dict):
    """What hours() keeps of one ticket: state, open, target, block, wait, lease, last work act."""


def _snap(it, prev, t, acted):
    ls = it.lease if isinstance(it.lease, dict) else {}
    return _Shadow(open=bool(it.open), target=it.target, blocked=bool(it.blocked),
                   bkind=it.blocked_kind or ("item" if it.blocked_on else "other"), bon=it.blocked_on,
                   buntil=epoch(it.blocked_until) if it.blocked_until else None,
                   wait=epoch(it.wait_until) if it.wait_until else None, waits=bool(it.wait_until),
                   lease=None if (not ls or ls.get("released")) else epoch(ls.get("expires")),
                   act=t if (acted or prev is None) else prev["act"])


def left_out(s, klass, mod, old, held, t, is_open):
    """-> the group a ticket is left out under at time t, or None (it counts). First match wins, in GROUPS order."""
    if mod is not None and mod in held:
        return "held"
    if old:
        return "oldmod"
    if s["target"] not in (None, "v1"):
        return "later"
    if s["waits"] and (s["wait"] is None or s["wait"] > t):
        return "parked"
    if s["blocked"] and not (s["bkind"] == "item" and s["bon"] and not is_open(s["bon"])):
        return "parked"
    if t - s["act"] > STALE_DAYS * DAY:
        return "stale"
    return None


def hours(evs, now, mods, classify, run_mods=(), runs=None, held=(), old=(), replay=None, n=HOURS):
    """-> {"t0", "ends": [epoch], "waiting"/"opened"/"closed": {class: [int]}, "worked": [int] or UNMEASURED,
    "out": {class: {group: n}} now, "flow_out": {"opened": n, "closed": n}, "unclassed": n, "open": n, "mismatch": n}.

    evs: the ledger (model.read()); classify(iid, title, mods, run_mods) -> "mod" | "nonmod" | "unclassed"
    (maturation_nonmod.classify, the page's one rule); runs: [(item, start, end or None)] or None when the run records
    could not be read; held: the mods he holds; old: names of mods not on the page."""
    if replay is None:
        import model
        replay = model.replay
    top = now - (now % 3600)                  # Pacific is a whole number of hours off UTC
    t0 = top - n * 3600
    ends = [t0 + 3600 * (k + 1) for k in range(n)] + [now]          # the last bin is the hour in progress
    tokens = {o.upper().replace("_", "") for o in old}
    mods, held, run_mods = list(mods), set(held), set(run_mods)
    sh, kl, info = {}, {}, {}
    B = len(ends)
    waiting = {c: [0] * B for c in CLASSES}
    opened, closed = ({c: [0] * B for c in CLASSES} for _ in range(2))
    worked = [0] * B
    flow_out = {"opened": 0, "closed": 0}
    spans = {}
    if runs is not None:
        for iid, a, z in runs:
            spans.setdefault(iid, []).append((a, z))

    def klass(iid, it):
        if iid not in kl:
            kl[iid] = classify(iid, it.title, mods, run_mods)
            mod = item_identity.item_mod(iid, mods, it.title) if kl[iid] == "mod" else None
            info[iid] = (mod, kl[iid] == "nonmod" and names_old_mod(iid, it.title, tokens))
        return kl[iid]

    def is_open(iid):
        s = sh.get(iid)
        return s is None or s["open"]         # a blocker never filed here cannot be read as closed

    def out_of(iid, s, t):
        return left_out(s, kl[iid], info[iid][0], info[iid][1], held, t, is_open)

    def in_work(iid, s, t):
        if s["lease"] is not None and s["lease"] > t:
            return True
        return any(a <= t and (z is None or z > t) for a, z in spans.get(iid, ()))

    def sample(b):
        t = ends[b]
        grp = {c: {g: 0 for g in GROUPS} for c in CLASSES}
        for iid, s in sh.items():
            if not s["open"] or kl[iid] not in CLASSES:
                continue
            if in_work(iid, s, t):
                worked[b] += 1
                continue
            g = out_of(iid, s, t)
            if g:
                grp[kl[iid]][g] += 1
            else:
                waiting[kl[iid]][b] += 1
        return grp

    cur = [0]
    last = [None]

    def observe(ev, world, ok):
        t = epoch(ev.get("ts"))
        if t is None or t > now:
            return
        while cur[0] < B - 1 and t >= ends[cur[0]]:
            last[0] = sample(cur[0])
            cur[0] += 1
        iid = ev.get("name") if ev.get("event") == "spawn" else ev.get("id")
        it = world.items.get(iid)
        if it is None:
            return
        prev = sh.get(iid)
        acted = ok and ev.get("event") in WORK_ACTS and ev.get("seat") not in PROGRAM_SEATS
        s = _snap(it, prev, t, acted)
        if prev is not None and not prev["open"] and s["open"]:
            s["act"] = t                      # a reopening is an act, whoever did it
        k = klass(iid, it)
        sh[iid] = s
        was = prev is not None and prev["open"]
        if was == s["open"] or t < t0 or k not in CLASSES:
            return
        if s["open"]:
            # judged without its block or wait: a ticket filed and parked at once was still opened
            g = out_of(iid, dict(s, blocked=False, waits=False), t)
            (flow_out.__setitem__("opened", flow_out["opened"] + 1) if g else
             opened[k].__setitem__(cur[0], opened[k][cur[0]] + 1))
        else:
            g = None if in_work(iid, prev, t) else out_of(iid, prev, t)
            (flow_out.__setitem__("closed", flow_out["closed"] + 1) if g else
             closed[k].__setitem__(cur[0], closed[k][cur[0]] + 1))

    def to_come(e):
        t = epoch(e.get("ts"))
        return t is not None and t > now

    world = replay([e for e in evs if not to_come(e)], observe=observe)
    while cur[0] < B:
        last[0] = sample(cur[0])
        cur[0] += 1
    op = {i for i, x in world.items.items() if x.open}
    mine = {i for i, s in sh.items() if s["open"]}
    return {"t0": t0, "ends": ends, "waiting": waiting, "opened": opened, "closed": closed,
            "worked": UNM if runs is None else worked, "out": last[0], "flow_out": flow_out, "open": len(op),
            "unclassed": sum(1 for i in mine if kl[i] not in CLASSES), "mismatch": len(op ^ mine), "now": now}


def run_spans(records, live):
    """-> [(item, start, end or None)] of the run records; a run that ended with no end time is dropped (unknown)."""
    if records is None:
        return None
    out = []
    for r in records:
        a, z = r.get("at"), r.get("ended")
        if not isinstance(a, (int, float)) or not r.get("item"):
            continue
        if isinstance(z, (int, float)):
            out.append((r["item"], a, z))
        elif live(r):
            out.append((r["item"], a, None))
    return out


def safe(evs, now, mods, classify, run_mods, records, live, cause=None, root=REPO):
    """hours(), or {"state": "blind" | "failed", "cause"}: could not look and failed never read as a count."""
    if evs is None:
        return {"state": "blind", "cause": cause or "the ledger was not read"}
    try:
        d = hours(evs, now, mods, classify, run_mods, run_spans(records, live), held_mods(), old_mods(mods, root))
        d["state"] = "ok"
        return d
    except Exception as e:      # noqa: BLE001
        return {"state": "failed", "cause": "%s: %s" % (e.__class__.__name__, e)}


# ---- words ----------------------------------------------------------------------------------------------------------

NAME = {"nonmod": "non-mod", "mod": "mod"}


def _moved(x):
    return "up %d" % x if x > 0 else "down %d" % -x if x < 0 else "level"


def headline(d):
    """Gaining or losing, first."""
    x = {c: d["waiting"][c][-1] - d["waiting"][c][0] for c in CLASSES}
    now = sum(d["waiting"][c][-1] for c in CLASSES)
    return "%d tickets waiting, %s in five days: %s" % (now, _moved(sum(x.values())), ", ".join(
        "%s %d (%s)" % (NAME[c], d["waiting"][c][-1], _moved(x[c])) for c in CLASSES))


def flow_words(d):
    return " · ".join("%s: %d opened, %d closed" % (NAME[c], sum(d["opened"][c]), sum(d["closed"][c])) for c in CLASSES)


def out_total(d):
    return sum(sum(v.values()) for v in d["out"].values())


def rule_lines(d):
    g = {k: sum(d["out"][c][k] for c in CLASSES) for k in GROUPS}
    moved = []
    for c in CLASSES:
        x = d["waiting"][c][-1] - d["waiting"][c][0]
        moved.append("%s %+d in all, %+d from opened and closed" % (
            NAME[c], x, sum(d["opened"][c][1:]) - sum(d["closed"][c][1:])))
    L = ["Waiting here = open, nobody on it, and not left out; the List Pipeline's Waiting stage is a part of it. It also moves "
         "when a ticket goes stale, is parked, is taken up or comes back: %s." % "; ".join(moved),
         "Left out now: %d of %d open tickets. " % (out_total(d), d["open"])
         + " · ".join("%d %s" % (g[k], GROUP_WORDS[k]) for k in GROUPS) + ".",
         "Mod = the ticket's id or title names a mod on this page, or a run on it recorded that mod. "
         "Could not class: %d (in no line)." % d["unclassed"],
         "Closed = done, dropped or superseded. Also in five days, on left-out tickets and not drawn: %d opened, %d closed. "
         "The last hour is still running." % (d["flow_out"]["opened"], d["flow_out"]["closed"])]
    if d["mismatch"]:
        L.append("The hourly replay and the ledger disagree on %d tickets: read the graph with care." % d["mismatch"])
    return L


# ---- the drawing ------------------------------------------------------------------------------------------------------

BG, CARD, EDGE, TEXT, DIM, FAINT = "#171310", "#211b16", "#4a3d2e", "#efe7d9", "#b5a993", "#8f8470"
COL = {"nonmod": "#e0803a", "mod": "#62b0a4"}
MUTED = {"nonmod": "#b98a63", "mod": "#8fa9a2"}      # the closed bars
WORKED = "#e6c34e"


def nice(m):
    """A round axis top at or above m."""
    for s in (4, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120, 150, 200, 250, 300, 400, 500, 600, 800, 1000):
        if m <= s:
            return s
    return int(m * 1.1)


def ops(d, w=1040, fs=1.0):
    """-> (height, [primitive]): ("r", x, y, w, h, fill) · ("l", [(x, y)], colour, width, dash) · ("t", x, y, text, size,
    fill, bold, anchor). fs scales the type (the phone page draws about 2.6 times larger)."""
    P = []
    f = lambda k: k * fs      # noqa: E731
    small = fs > 1.5
    x0, x1 = f(40 if not small else 32), w - f(96 if not small else 84)
    n = len(d["ends"])
    X = lambda k: x0 + (x1 - x0) * k / float(n)                      # noqa: E731
    y = f(8)

    def text(x, yy, s, size=10.5, fill=DIM, bold=False, anchor="start"):
        P.append(("t", x, yy, s, f(size), fill, bold, anchor))

    def days(top, bot, labels):
        for k in range(n):
            t = dt.datetime.fromtimestamp(d["t0"] + 3600 * k, PAC)
            if t.hour == 0:
                P.append(("l", [(X(k), top), (X(k), bot)], EDGE, 1, None))
                if labels and X(k) + f(52) < x1 + f(20):
                    text(X(k) + f(3), bot + f(13), t.strftime("%a") if small else t.strftime("%a %b ") + str(t.day), 10.5, DIM)

    def grid(top, bot, hi, sign=1):
        for v in ((hi, hi // 2, 0) if sign else ()):
            yy = bot - (bot - top) * v / float(hi)
            P.append(("l", [(x0, yy), (x1, yy)], EDGE if v else FAINT, 1, None if not v else "2 4"))
            text(x0 - f(5), yy + f(3.5), str(v), 10, DIM, anchor="end")

    # panel 1: waiting
    hi = nice(max(max(d["waiting"][c]) for c in CLASSES) or 1)
    text(f(8), y + f(12), "WAITING at the end of each hour (tickets)", 11, TEXT, True)
    top, bot = y + f(26), y + f(26) + f(130)
    days(top, bot, False)
    grid(top, bot, hi)
    ends = []
    for c in CLASSES:
        pts = [(X(k + 1), bot - (bot - top) * v / float(hi)) for k, v in enumerate(d["waiting"][c])]
        P.append(("l", pts, COL[c], 2.4 * min(fs, 1.8), None))
        ends.append([pts[-1][1], c])
    ends.sort()
    if len(ends) == 2 and ends[1][0] - ends[0][0] < f(15):
        mid = (ends[0][0] + ends[1][0]) / 2
        ends[0][0], ends[1][0] = mid - f(7.5), mid + f(7.5)
    for yy, c in ends:
        text(x1 + f(6), yy + f(4), "%s %d" % (NAME[c], d["waiting"][c][-1]), 11.5, COL[c], True)
    y = bot + f(20)
    # panel 2: being worked (a thin strip of its own: single digits beside hundreds)
    text(f(8), y + f(12), "BEING WORKED" if small else "BEING WORKED at the end of each hour, mod and non-mod together", 11, TEXT, True)
    top, bot = y + f(24), y + f(24) + f(40)
    days(top, bot, False)
    if d["worked"] == UNM:
        text(x0, (top + bot) / 2, "UNMEASURED: the run records could not be read", 11, TEXT)
    else:
        hi = nice(max(d["worked"]) or 1)
        for v in (hi, 0):
            yy = bot - (bot - top) * v / float(hi)
            P.append(("l", [(x0, yy), (x1, yy)], EDGE if v else FAINT, 1, None if not v else "2 4"))
            text(x0 - f(5), yy + f(3.5), str(v), 10, DIM, anchor="end")
        for k, v in enumerate(d["worked"]):
            if v:
                hgt = (bot - top) * v / float(hi)
                P.append(("r", X(k) + 0.5, bot - hgt, max(1, X(k + 1) - X(k) - 1), hgt, WORKED))
        text(x1 + f(6), bot - f(6), "%d now" % d["worked"][-1], 11.5, WORKED, True)
    y = bot + f(20)
    # panels 3 and 4: opened up, closed down; one panel per class on one shared scale
    hu = nice(max([max(d["opened"][c]) for c in CLASSES] + [1]))
    hd = nice(max([max(d["closed"][c]) for c in CLASSES] + [1]))
    for c in CLASSES:
        text(f(8), y + f(12), ("%s: opened up, closed down" if small else "%s: OPENED (up) and CLOSED (down) in each hour "
                               "(tickets, one scale for both panels)") % NAME[c].upper(), 11, TEXT, True)
        top, hgt = y + f(24), f(112)
        bot = top + hgt
        s = hgt / float(hu + hd)
        zero = top + hu * s
        days(top, bot, c == CLASSES[-1])
        for v in (hu, -hd):
            P.append(("l", [(x0, zero - v * s), (x1, zero - v * s)], EDGE, 1, "2 4"))
            text(x0 - f(5), zero - v * s + f(3.5), str(abs(v)), 10, DIM, anchor="end")
        text(x0 - f(5), zero + f(3.5), "0", 10, DIM, anchor="end")
        for k in range(n):
            wd = max(1, X(k + 1) - X(k) - 1)
            if d["opened"][c][k]:
                P.append(("r", X(k) + 0.5, zero - d["opened"][c][k] * s, wd, d["opened"][c][k] * s, COL[c]))
            if d["closed"][c][k]:
                P.append(("r", X(k) + 0.5, zero, wd, d["closed"][c][k] * s, MUTED[c]))
        P.append(("l", [(x0, zero), (x1, zero)], TEXT, 1, None))
        text(x1 + f(6), zero - f(8), "%d opened" % sum(d["opened"][c]), 11.5, COL[c], True)
        text(x1 + f(6), zero + f(17), "%d closed" % sum(d["closed"][c]), 11.5, MUTED[c], True)
        y = bot + f(18)
    return bot + f(22), P


def esc(s):
    return html.escape(str(s), quote=True)


def svg(d, font="'Segoe UI',Helvetica,Arial,sans-serif"):
    """The graph as one line of SVG with no blank line in it (Typora)."""
    h, P = ops(d)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 %d" width="100%%" role="img" aria-label="%s" '
           'style="max-width:1040px;font-family:%s">' % (h, esc("Tickets by hour, five days. %s. %s." % (
               headline(d), flow_words(d))), font), '<rect width="1040" height="%d" rx="10" fill="%s"/>' % (h, BG)]
    for p in P:
        if p[0] == "r":
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % p[1:])
        elif p[0] == "l":
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (
                " ".join("%.1f,%.1f" % q for q in p[1]), p[2], p[3], ' stroke-dasharray="%s"' % p[4] if p[4] else ""))
        else:
            out.append('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s"%s%s>%s</text>' % (
                p[1], p[2], p[4], p[5], ' font-weight="700"' if p[6] else "",
                ' text-anchor="%s"' % p[7] if p[7] != "start" else "", esc(p[3])))
    return "".join(out) + "</svg>"


TITLE = "Tickets by hour, last five days"


def block(d):
    """The whole section as one line of HTML: the headline, the graph, and what it leaves out."""
    if d.get("state") != "ok":
        word = "COULD NOT LOOK" if d.get("state") == "blind" else "FAILED"
        return ('<div style="background:%s;border-radius:10px;padding:14px 18px;color:%s;font-size:14px"><b>%s:</b> the '
                'graph of tickets by hour was not drawn (%s). Every number in it is UNMEASURED.</div>'
                % (BG, TEXT, word, esc(d.get("cause"))))
    return ('<div style="background:%s;border-radius:10px;padding:12px 14px;color:%s;font-size:13px">'
            '<div style="font-size:16px;font-weight:600">%s</div><div style="color:%s;margin:2px 0 8px">In five days, %s.'
            '</div>%s<div style="color:%s;font-size:11.5px;line-height:1.5;margin-top:4px">%s</div></div>'
            % (BG, TEXT, esc(headline(d)), DIM, esc(flow_words(d)), svg(d), DIM,
               "<br>".join(esc(x) for x in rule_lines(d))))
