#!/usr/bin/env python3
"""ruling_fast.py - land the fast part of an owner ruling in one call, with no model; file the slow part as one item.

Item RIMMANDRAKE_BUILD_RULING_FAST_PATH_SENTENCE_TOOK_NINETY_MINUTES; page design/specs/2026-11-26-ruling-fast-path/boundary.md;
selftest selftest_ruling_fast.py. The owner, 2026-11-26: "Yes please build the automated script that would accelerate
the small fast part independently of the larger items of work." (his one-sentence ruling of that day took a model
worker about 40 min, and its landing then waited over 50 min in the publish line).

    python3 src/RimMandrake/rimflow/ruling_fast.py <ITEM> --said "<his words>" --section "<heading>" \\
        [--hold <Mod>]... [--park <ID>]... [--title "<a short lead, our text>"] [--why "<the Conductor's order>"]
    python3 src/RimMandrake/rimflow/ruling_fast.py <ITEM> --per-ruling <item-id|event> --why "<the Conductor's order>" \\
        --section "<heading>" [--park <ID>]...      the Conductor's route: the act cites a standing ruling, not his words;
                                                    it holds no mod (a hold is his act alone)

The acts, in this order (each one an existing part; none is copied here):
  1. his words on ITEM:            rimflow note ITEM --owner-said "<words>"
  2. each named mod held:          mod_owner_hold.py hold <Mod> --said "<words>"   (the control store binds at once)
     each named ticket parked:     rimflow block <ID> --kind owner --owner-said "<words>"
     then acts 1 and 2 land:       ./publish --ledger OWNER.jsonl <seat shard>
  3. his words, word for word, with the date of act 1's ledger event, as one bullet at the end of the section of
     design/RimMandrake/standing_rulings.md whose heading is --section; it lands by ./publish of that file alone (a
     text-only commit takes the text door, no tree-check slot: publish.py text_door)
  4. one follow-up item of kind owed (rimflow file), caused by ITEM, for the slow part: the rule line in CLAUDE.md, the
     lines that say the opposite, the tickets he did not name, and the publish of the hold mirror when a mod was held.
It acts only on what the call names: no --hold and no --park means nothing is held or parked. A bad call (blank words,
an unknown item, ticket or mod, a heading that matches no section or two, uncommitted edits in standing_rulings.md) is
refused before the first act. It prints at most 5 lines. Exit 0 done, 2 refused (nothing done), 1 an act failed (the
acts before it stay done; the undo line says how to take each back).
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import time_budget  # noqa: E402

RULES = os.path.join("design", "RimMandrake", "standing_rulings.md")
EVENTS = os.path.join("infrastructure", "state", "ledger", "events")
CLI = os.path.join(HERE, "cli.py")
HOLD = os.path.join(HERE, "mod_owner_hold.py")
WIDTH = 120
PACIFIC = "America/Los_Angeles"


class Refused(Exception):
    """A bad call: nothing was done. The text names what is wrong and its repair."""


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("item", help="the ledger item his words are on")
    ap.add_argument("--said", default="", help="his words, as he typed them")
    ap.add_argument("--per-ruling", default="", metavar="ID|EVENT",
                    help="the Conductor's route in place of his words: the standing ruling the act stands on, with --why")
    ap.add_argument("--section", required=True, help="the heading of the standing_rulings.md section for his words")
    ap.add_argument("--hold", action="append", default=[], metavar="MOD", help="a mod his words hold (repeat)")
    ap.add_argument("--park", action="append", default=[], metavar="ID", help="a ticket his words park (repeat)")
    ap.add_argument("--title", default="", help="a short bold lead for the bullet (our text, not his)")
    ap.add_argument("--why", default="",
                    help="the caller's reason (a helper: the Conductor's order); required with --per-ruling")
    ap.add_argument("--follow-up", default="", help="the follow-up item's name (default: made from ITEM)")
    return ap.parse_args(argv)


# ------------------------------------------------------------------ the section and the bullet (pure)

HEAD_RX = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def headings(lines):
    """-> [(index, level, text)] of the Markdown headings outside code fences."""
    out, fence = [], False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        m = None if fence else HEAD_RX.match(ln)
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def _norm(t):
    return " ".join(t.replace("§", "").split()).casefold()


def find_section(lines, want):
    """-> (start, end): the heading line of the one section whose heading is `want` (an exact match first, else the one
    heading that starts with it), and the line where the section ends (the next heading of its level or above, or the
    end). Raises Refused naming the candidates."""
    hs, w = headings(lines), _norm(want)
    hits = [h for h in hs if _norm(h[2]) == w] or [h for h in hs if _norm(h[2]).startswith(w)]
    if len(hits) != 1:
        if not hits:
            raise Refused("no heading of %s reads %r; repair: give --section the exact text of one heading" % (RULES, want))
        raise Refused("%d headings of %s start with %r (%s); repair: give --section the whole heading of one"
                      % (len(hits), RULES, want, "; ".join(repr(h[2]) for h in hits[:4])))
    i, level, _t = hits[0]
    end = next((j for j, lv, _ in hs if j > i and lv <= level), len(lines))
    return i, end


def when_pacific(ts):
    """'2026-11-26T20:45:58Z' -> 'Thu 2026-11-26 12:45 PM PST'."""
    from zoneinfo import ZoneInfo
    t = datetime.datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
    p = t.astimezone(ZoneInfo(PACIFIC))
    return p.strftime("%a %Y-%m-%d ") + p.strftime("%I:%M %p %Z").lstrip("0")


def bullet(words, event, item, title="", holds=(), parks=(), per_ruling="", why=""):
    """-> the bullet's lines: his words exactly, the event's Pacific time, tsn and item; wrapped at WIDTH. On the
    Conductor's route (per_ruling): the ruling and the reason, which are our text, so they are never quoted as his."""
    lead = "**%s** " % title.strip() if title.strip() else ""
    if per_ruling:
        text = "- %s(the Conductor's act per standing ruling `%s`, %s, OWNER event `%s` on `%s`): %s" % (
            lead, per_ruling, when_pacific(event["ts"]), event.get("tsn") or "?", item, " ".join(why.split()))
    else:
        text = "- %s(owner, %s, OWNER event `%s` on `%s`): *\"%s\"*" % (lead, when_pacific(event["ts"]),
                                                                       event.get("tsn") or "?", item,
                                                                       " ".join(words.split()))
    done = []
    if holds:
        done.append("`mod_owner_hold.py hold` holds %s" % ", ".join("`%s`" % m for m in holds))
    if parks:
        done.append("`rimflow block --kind owner` parks %s" % ", ".join("`%s`" % t for t in parks))
    if done:
        text += " Carried at once: %s." % "; ".join(done)
    return textwrap.wrap(text, width=WIDTH, subsequent_indent="  ", break_long_words=False, break_on_hyphens=False)


def insert(lines, start, end, new):
    """-> the file's lines with `new` after the last non-blank line of the section [start, end). A section that ends in
    prose, not a list, gets a blank line first."""
    last = max((j for j in range(start, end) if lines[j].strip()), default=start)
    tail = lines[last]
    gap = [] if (last != start and (tail.lstrip().startswith(("-", "*")) or tail.startswith(" "))) else [""]
    return lines[:last + 1] + gap + new + lines[last + 1:]


def follow_up_name(item, taken):
    """-> RIMMANDRAKE_SPREAD_SLOW_PART_OF_<the item's words after its project and verb>, at most 9 words and 64 chars; a
    name that `taken(name)` says exists gets AGAIN."""
    ws = [w for w in item.split("_") if w]
    tail = [w for w in (ws[2:] if len(ws) > 3 else ws) if not w.isdigit()]
    name = ["RIMMANDRAKE", "SPREAD", "SLOW", "PART", "OF"]
    for w in tail:
        if len(name) >= 9 or len("_".join(name + [w])) > 64:
            break
        name.append(w)
    n = "_".join(name)
    if taken(n):
        n = "_".join(name[:8] + ["AGAIN"])[:64].rstrip("_")
    return n


def follow_up_title(item, event, words, section, holds, parks):
    t = ("Carry the slow part of his ruling on %s (OWNER event %s, %s; his words: \"%s\"; its fast part landed by "
         "ruling_fast.py): write the rule line in CLAUDE.md that points at design/RimMandrake/standing_rulings.md §%s; "
         "search the repo for lines that say the opposite and fix each; search the list for tickets that he did not "
         "name and that his words touch, and park or change each" % (item, event.get("tsn") or "?",
                                                                    when_pacific(event["ts"]), " ".join(words.split()),
                                                                    section))
    if holds:
        t += ("; publish the hold mirror src/RimMandrake/rimflow/mod_owner_hold.json (python3 "
              "src/RimMandrake/rimflow/mod_owner_hold.py mirror, then ./publish it): the hold of %s binds now in the "
              "control store" % ", ".join(holds))
    if parks:
        t += "; already parked: %s" % ", ".join(parks)
    return t + ". Acceptance test: none, a reading of the rules and the list against his words"


def undo_line(item, holds, parks, text_sha, follow):
    parts = ["the ledger keeps his words on %s (a note can say they were withdrawn)" % item]
    parts += ["mod_owner_hold.py lift %s --said \"<his words>\"" % m for m in holds]
    parts += ["rimflow unblock %s" % t for t in parks]
    if text_sha:
        parts.append("git revert %s, then ./publish" % text_sha[:12])
    if follow:
        parts.append("rimflow drop %s --reason \"...\"" % follow)
    return "UNDO: " + "; ".join(parts)


# ------------------------------------------------------------------ the command

def check_call(o, doors, rules_path):
    """Refuse a bad call before any act. -> (lines, start, end) of the rules file."""
    bad = []
    said, route = o.said.strip(), o.per_ruling.strip()
    if bool(said) == bool(route):
        bad.append("give his words (--said) or the Conductor's route (--per-ruling <item-id|event> with --why), one of "
                   "them; repair: pass exactly one")
    if route and not o.why.strip():
        bad.append("the Conductor's route carries its reason; repair: add --why with the Conductor's order")
    if route and o.hold:
        bad.append("a hold is his act alone (mod_owner_hold.py hold, OWNER ONLY): the Conductor's route holds no mod; "
                   "repair: drop --hold, or pass his words with --said")
    for iid in [o.item] + list(o.park):
        if not doors.item_exists(iid):
            bad.append("the ledger has no item %s; repair: name an item that `rimflow show` knows" % iid)
    for m in o.hold:
        if not doors.mod_exists(m):
            bad.append("no mod %s (design/concepts/%s is absent); repair: name a mod by its folder" % (m, m))
    if doors.dirty(rules_path):
        bad.append("%s has uncommitted edits; repair: publish or undo them first, so that the commit holds the new bullet alone" % RULES)
    try:
        lines = open(rules_path, encoding="utf-8").read().split("\n")
        start, end = find_section(lines, o.section)
    except Refused as e:
        bad.append(str(e))
        lines, start, end = None, 0, 0
    except OSError as e:
        bad.append("%s cannot be read (%s); repair: run from a clone of this repo" % (RULES, e))
        lines, start, end = None, 0, 0
    if bad:
        raise Refused("; ".join(bad))
    return lines, start, end


def run(o, doors, rules_path=None, out=None):
    out = out or sys.stdout
    rules_path = rules_path or os.path.join(REPO, RULES)
    say = lambda s: print(s, file=out, flush=True)      # noqa: E731
    holds, parks = list(dict.fromkeys(o.hold)), list(dict.fromkeys(o.park))
    try:
        lines, start, end = check_call(o, doors, rules_path)
    except Refused as e:
        say("REFUSED (nothing done): %s" % e)
        return 2
    step, done, text_sha, follow = "record his words", [], None, ""
    try:
        why = o.why.strip() or "ruling_fast.py: the fast part of his ruling, carried at once"
        route = o.per_ruling.strip()
        event = doors.note(o.item, o.said, "his ruling, carried by ruling_fast.py", why, per_ruling=route or None)
        done.append("his words on %s" % o.item)
        date = when_pacific(event["ts"]).split()[1]
        for m in holds:
            step = "hold %s" % m
            doors.hold(m, o.said, date)
            done.append("held %s" % m)
        reason = ("Parked by his word (owner, %s: \"%s\"). Lifts on his word." % (date, " ".join(o.said.split()))
                  if not route else "Parked by the Conductor per standing ruling %s (%s): %s"
                  % (route, date, " ".join(why.split())))
        for t in parks:
            step = "park %s" % t
            doors.park(t, o.said, reason, why, per_ruling=route or None)
            done.append("parked %s" % t)
        step = "land his words on the ledger"
        sha1, s1 = doors.publish_ledger("ledger: %s his words%s (ruling_fast.py)"
                                        % (o.item, "; holds and parks" if holds or parks else ""))
        when = when_pacific(event["ts"])
        say("LANDED %s on %s (OWNER event %s, %s)%s%s: PUBLISHED %s (ledger door, %.1f s)"
            % ("his words" if not route else "the act per %s" % route, o.item, event.get("tsn") or "?", when, "; held %s (binds now in the control store; its mirror "
               "mod_owner_hold.json is written here, unpublished)" % ", ".join(holds) if holds else "",
               "; parked %s" % ", ".join(parks) if parks else "", sha1[:12], s1))
        step = "write his words into %s" % RULES
        new = insert(lines, start, end, bullet(o.said, event, o.item, o.title, holds, parks, route, why))
        with open(rules_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new))
        local = doors.local_commits()
        step = "land %s" % RULES
        text_sha, s2 = doors.publish_text(rules_path, "%s: his words into standing_rulings.md §%s (ruling_fast.py)"
                                          % (o.item, lines[start].lstrip("# ").strip()))
        say("LANDED his words in %s §%s: PUBLISHED %s (%.1f s%s)"
            % (RULES, lines[start].lstrip("# ").strip(), text_sha[:12], s2,
               "; %d earlier local commit(s) of this clone rode with it" % len(local) if local else ""))
        step = "file the follow-up"
        follow = o.follow_up or follow_up_name(o.item, doors.item_exists)
        doors.file(follow, follow_up_title(o.item, event, o.said or "per standing ruling %s: %s" % (route, why),
                                           lines[start].lstrip("# ").strip(), holds, parks), o.item, why)
        sha3, _s3 = doors.publish_ledger("ledger: %s filed for the slow part of his ruling on %s" % (follow, o.item))
        say("FOLLOW-UP %s (owed, caused by %s): the CLAUDE.md rule line, lines that say the opposite, tickets he did not "
            "name%s: PUBLISHED %s" % (follow, o.item, ", the hold mirror" if holds else "", sha3[:12]))
    except Exception as e:      # noqa: BLE001  any failure of an act stops the rest and is named
        why = " ".join(str(e).split())[:400]     # cut-ok: one output line; the cause's head names it
        say("FAILED at %s: %s: %s. Done before it: %s" % (step, type(e).__name__, why, ", ".join(done) or "nothing"))
        say(undo_line(o.item, [d[5:] for d in done if d.startswith("held ")],
                      [d[7:] for d in done if d.startswith("parked ")], text_sha, follow if step != "file the follow-up"
                      else ""))
        return 1
    say(undo_line(o.item, holds, parks, text_sha, follow))
    return 0


# ------------------------------------------------------------------ the real doors

def _seat():
    return (os.environ.get("AGENT_SEAT") or os.environ.get("RIMFLOW_SEAT") or "BENCH").upper()


class Doors:
    """The parts the command composes, each called as its own command line from the repo top."""

    def __init__(self, repo=REPO):
        self.repo, self.seat = repo, _seat()

    def _run(self, argv, timeout):
        r = subprocess.run(argv, cwd=self.repo, capture_output=True, text=True, timeout=timeout)
        if r.returncode:
            raise RuntimeError("%s exit %d: %s" % (os.path.basename(argv[1] if argv[0] == sys.executable else argv[0]),
                                                   r.returncode, (r.stderr or r.stdout).strip()[-400:]))  # cut-ok: message
        return r

    def item_exists(self, iid):
        r = subprocess.run([sys.executable, CLI, "show", iid], cwd=self.repo, capture_output=True, text=True,
                           timeout=time_budget.RIMFLOW_S)  # budget: class=rimflow
        return r.returncode == 0

    def mod_exists(self, mod):
        return os.path.isdir(os.path.join(self.repo, "design", "concepts", os.path.basename(mod.rstrip("/"))))

    def dirty(self, path):
        r = subprocess.run(["git", "status", "--porcelain", "--", path], cwd=self.repo, capture_output=True, text=True,
                           timeout=time_budget.CALL_S)  # budget: class=call
        return bool(r.stdout.strip()) or r.returncode != 0

    def local_commits(self):
        r = subprocess.run(["git", "log", "--format=%h", "origin/main..HEAD"], cwd=self.repo, capture_output=True,
                           text=True, timeout=time_budget.CALL_S)  # budget: class=call
        return r.stdout.split() if not r.returncode else []

    def note(self, item, said, text, why, per_ruling=None):
        auth = ["--per-ruling", per_ruling] if per_ruling else ["--owner-said", said]
        self._run([sys.executable, CLI, "note", item, *auth, "--text", text, "--seat", self.seat, "--why", why],
                  time_budget.RIMFLOW_S)  # budget: class=rimflow
        ev = self._event(item, said, per_ruling)
        if ev is None:
            raise RuntimeError("rimflow note exited 0, but OWNER.jsonl holds no note on %s with %s" % (
                item, "the ruling %s" % per_ruling if per_ruling else "his words"))
        return ev

    def _event(self, item, said, per_ruling=None):
        p = os.path.join(self.repo, EVENTS, "OWNER.jsonl")
        want = " ".join(said.split())
        with open(p, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for ln in reversed(lines):
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            if e.get("event") != "note" or e.get("id") != item:
                continue
            if (e.get("perRuling") == per_ruling) if per_ruling else (" ".join((e.get("ownerSaid") or "").split()) == want):
                return e
        return None

    def hold(self, mod, said, date):
        r = subprocess.run([sys.executable, HOLD, "hold", mod, "--said", said, "--date", date], cwd=self.repo,
                           capture_output=True, text=True, timeout=time_budget.RIMFLOW_S)  # budget: class=rimflow
        if r.returncode not in (0, 5):      # 5: the store holds it, its mirror alarm is raised (mod_owner_hold.py)
            raise RuntimeError("mod_owner_hold.py hold exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-400:]))  # cut-ok: message

    def park(self, iid, said, reason, why, per_ruling=None):
        auth = ["--per-ruling", per_ruling] if per_ruling else ["--owner-said", said]
        self._run([sys.executable, CLI, "block", iid, "--kind", "owner", *auth, "--reason", reason, "--why", why],
                  time_budget.RIMFLOW_S)  # budget: class=rimflow

    def file(self, name, title, caused_by, why):
        self._run([sys.executable, CLI, "file", name, "--for", self.seat, "--kind", "owed", "--title", title,
                   "--caused-by", caused_by, "--seat", self.seat, "--why", why], time_budget.RIMFLOW_S)  # budget: class=rimflow

    def _publish(self, args):
        t0 = time.monotonic()
        r = subprocess.run([os.path.join(self.repo, "publish")] + args, cwd=self.repo, capture_output=True, text=True,
                           timeout=time_budget.PUBLISH_S)  # budget: class=publish
        m = re.search(r"^PUBLISHED ([0-9a-f]{40})", r.stdout, re.M)
        if r.returncode or not m:
            raise RuntimeError("./publish exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-400:]))  # cut-ok: message
        return m.group(1), time.monotonic() - t0

    def publish_ledger(self, msg):
        shards = sorted({os.path.join(EVENTS, "OWNER.jsonl"), os.path.join(EVENTS, "%s.jsonl" % self.seat)})
        return self._publish(["--ledger", "-m", msg] + shards)

    def publish_text(self, path, msg):
        return self._publish(["-m", msg, os.path.relpath(path, self.repo)])


def main(argv=None):
    return run(parse(argv), Doors())


if __name__ == "__main__":
    sys.exit(main())
