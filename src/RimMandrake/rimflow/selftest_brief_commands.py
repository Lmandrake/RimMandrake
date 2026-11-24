#!/usr/bin/env python3
"""selftest_brief_commands.py - the filled commands in each detached brief (brief_commands.py, detached_helper.brief_message).

Item RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES; page design/specs/2026-11-23-brief-commands/boundary.md
(each t_ function is one promise of it, by name). Offline. Written before the code; seen failing on the base.
"""
import argparse
import inspect
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
FAILS = []
IT = "RIMMANDRAKE_SOME_ITEM_FOR_THIS_TEST_ONLY"
LEDGER = ("claim", "note", "wait", "close", "verify", "file")
OWNER = ("--owner-said", "--by-card", "--per-ruling")
SPEND = re.compile(r"\$\s?\d|\bweighted\b|\bbudget|\bcap.usd\b|\bspend|\b\d[\d,.]*\s*[kM]?\s*tokens?\b", re.I)


def chk(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def BC():
    import brief_commands
    return brief_commands


def subs(p):
    return next(a for a in p._actions if isinstance(a, argparse._SubParsersAction)).choices


def words(text, verb):
    ln = next(x for x in text.splitlines() if re.search(r"cli\.py %s\b" % verb, x) and "could not look" not in x.lower())
    w = shlex.split(ln.strip().strip("`"))
    return w[w.index(verb) + 1:]


def fake(drop=None, lose=None, add=None, help_=None, n_other=0):
    """A small ledger parser. drop: a verb left out; lose: (verb, flag) left out; add: (verb, flag) required."""
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd")
    for v in LEDGER:
        if v == drop:
            continue
        q = sp.add_parser(v)
        q.add_argument("id")
        for o in ("--seat", "--why", "--text", "--sha", "--evidence", "--title", "--caused-by", "--effect") + OWNER:
            if lose != (v, o):
                q.add_argument(o)
        for o in {"wait": ("--until", "--reason"), "verify": ("--result", "--config"), "file": ("--for",)}.get(v, ()):
            q.add_argument(o, required=True)
        q.add_argument("--publish", action="store_true")
        if add and add[0] == v:
            q.add_argument(add[1], required=True)
        if help_:
            q.add_argument("--zz-helped", help=help_)
        for i in range(n_other):
            q.add_argument("--zz-other-%03d" % i, help="some long words about this flag " * 5)
    return p


def got(**k):
    return BC().filled(IT, "BENCH", **k)


class Broken:
    def __getattr__(self, n):
        raise RuntimeError("parser cannot be read")


def t_lines_come_from_the_parser():
    import cli

    def real(v):
        sp = subs(cli.build_parser())[v]
        w = words(got()["text"], v)
        opts = [x for x in w if x.startswith("--")]
        owed = [a for a in sp._actions if a.option_strings and a.required and not set(a.option_strings) & set(opts)]
        return all(o in sp._option_string_actions for o in opts) and not owed
    for v in LEDGER:
        chk(lambda v=v: real(v), "lines-come-from-the-parser: the %s line has every required flag and no unknown one" % v)
    chk(lambda: "--zz-new" in words(got(parsers={"rimflow": fake(add=("close", "--zz-new"))})["text"], "close")
        and "--zz-new" not in got(parsers={"rimflow": fake()})["text"],
        "lines-come-from-the-parser: a new required flag shows in that verb's line")

    def positional():
        p = fake()
        subs(p)["note"].add_argument("second")
        return any("SECOND" in x.upper() for x in words(got(parsers={"rimflow": p})["text"], "note"))
    chk(positional, "lines-come-from-the-parser: a new required positional shows")
    chk(lambda: got()["could_not_look"] == [], "lines-come-from-the-parser: the four real tools are all read")
    chk(lambda: all(s in got()["text"] for s in ("./publish -m", "maturation.py red-seen", "lessons.py add", "--patch")),
        "lines-come-from-the-parser: publish, red-seen and lessons are there")


def t_could_not_look_is_said():
    def lost_verb():
        r = got(parsers={"rimflow": fake(drop="note")})
        return (any("note" in c for c in r["could_not_look"]) and re.search(r"could not look: .*note", r["text"])
                and words(r["text"], "close"))
    chk(lost_verb, "could-not-look-is-said: a lost verb is named, and the other lines stay")

    def broken():
        r = got(parsers={"rimflow": Broken()})
        return (r["could_not_look"] and "run `python3 src/RimMandrake/rimflow/cli.py --help`" in r["text"]
                and "./publish -m" in r["text"] and "cli.py note" not in r["text"])
    chk(broken, "could-not-look-is-said: a parser that raises is said with its --help, no guessed line, the others stay")

    def lost_flag():
        r = got(parsers={"rimflow": fake(lose=("note", "--text"))})
        return any("--text" in c and "note" in c for c in r["could_not_look"]) and "--text" not in words(r["text"], "note")
    chk(lost_flag, "could-not-look-is-said: a wanted flag the parser lost is named, and is not in the line")

    def every_tool():
        r = got(parsers={k: Broken() for k in ("rimflow", "maturation", "lessons", "publish")})
        return len(r["could_not_look"]) == 4 and r["text"].lower().count("could not look") >= 4
    chk(every_tool, "could-not-look-is-said: four unreadable parsers are four lines, never an empty text")


def t_item_and_seat_are_filled():
    t = got()["text"]
    for v in LEDGER:
        chk(lambda v=v: IT in words(t, v) and words(t, v)[words(t, v).index("--seat") + 1] == "BENCH"
            and "--publish" in words(t, v), "item-and-seat-are-filled: the %s line" % v)

    def refused(*a):
        try:
            BC().filled(*a)
        except ValueError:
            return True
        return False
    chk(lambda: all(refused(*a) for a in (("", "BENCH"), (None, "BENCH"), ("  ", "BENCH"), (IT, ""), (IT, None))),
        "item-and-seat-are-filled: an empty item or seat is a ValueError")


def t_judgement_stays_a_blank():
    t = got()["text"]

    def blank(v, flag):
        w = words(t, v)
        return re.fullmatch(r"<[^<>]+>", w[w.index(flag) + 1]) is not None
    for v, f in (("note", "--text"), ("wait", "--reason"), ("wait", "--until"), ("close", "--evidence"), ("close", "--sha"),
                 ("close", "--why"), ("verify", "--result"), ("verify", "--config"), ("file", "--title")):
        chk(lambda v=v, f=f: blank(v, f), "judgement-stays-a-blank: %s %s" % (v, f))
    chk(lambda: not any(re.search(r"[<>|]", re.sub(r'"[^"]*"', "", ln)) for ln in t.splitlines()
                         if re.search(r"^  `(python3|\./)", ln)),
        "judgement-stays-a-blank: a blank is always inside quotes (a bare < is a shell redirect)")
    chk(lambda: not any(b in x for ln in t.splitlines() if re.search(r"^  `(python3|\./)", ln)
                        for x in [ln.strip().strip("`")] for b in ("`", "$")),
        "judgement-stays-a-blank: no backtick and no dollar inside a line")


def t_no_owner_flag():
    chk(lambda: not any(o in got()["text"] for o in OWNER), "no-owner-flag: the real tools")
    chk(lambda: not any(o in got(parsers={"rimflow": fake()})["text"] for o in OWNER), "no-owner-flag: a fake parser")

    def required():
        r = got(parsers={"rimflow": fake(add=("note", "--said-x"))})
        p = fake()
        a = subs(p)["note"]._option_string_actions["--by-card"]
        a.required = True
        r = got(parsers={"rimflow": p})
        return "--by-card" not in r["text"].replace("\n", " ") and any("owner" in c for c in r["could_not_look"])
    chk(required, "no-owner-flag: one that became required is said as could not look, and is not a line")


def t_no_spend_in_the_text():
    chk(lambda: not SPEND.search(got()["text"]), "no-spend-in-the-text: the real tools")
    chk(lambda: not SPEND.search(got(parsers={"rimflow": fake(help_="the budget of the run, 40k tokens")})["text"]),
        "no-spend-in-the-text: a help text with a figure is left out")
    chk(lambda: "a plain word" in got(parsers={"rimflow": fake(help_="a plain word")})["text"],
        "no-spend-in-the-text: a plain help text stays")


def t_the_text_stays_short():
    chk(lambda: 0 < len(got()["text"]) <= BC().MAX_CHARS == 12000, "the-text-stays-short: the real tools")

    def many():
        r = got(parsers={"rimflow": fake(n_other=120)})
        return len(r["text"]) <= BC().MAX_CHARS and all(words(r["text"], v) for v in LEDGER)
    chk(many, "the-text-stays-short: a parser with many flags loses its lists, never a filled line")


def t_every_detached_launch_carries_the_lines():
    import detached_helper as DH
    chk(lambda: got()["text"] in DH.brief_message("Do the work.", IT, "BENCH", "/tmp/clone"),
        "every-detached-launch-carries-the-lines: brief_message holds them")
    chk(lambda: DH.brief_message("Do the work.", IT, "BENCH", "/tmp/clone").startswith("Do the work.")
        and "Wall-time bound: 60 s" in DH.brief_message("x", IT, "BENCH", "/c", 60)
        and "no wall-time bound" in DH.brief_message("x", IT, "BENCH", "/c"),
        "every-detached-launch-carries-the-lines: the brief comes first and the bound is said")
    chk(lambda: "brief_message(" in inspect.getsource(DH._launch_locked) and "FOOTER" not in
        inspect.getsource(DH._launch_locked), "every-detached-launch-carries-the-lines: _launch_locked calls it")
    chk(lambda: not re.search(r"cli\.py (%s) |\./publish -m" % "|".join(LEDGER), DH.FOOTER),
        "every-detached-launch-carries-the-lines: FOOTER holds no second copy of a command")


def t_a_launch_never_fails_on_the_lines():
    import detached_helper as DH

    def raised():
        real = BC().filled
        BC().filled = lambda *a, **k: 1 / 0
        try:
            m = DH.brief_message("Do the work.", IT, "BENCH", "/tmp/clone")
        finally:
            BC().filled = real
        return "Do the work." in m and "could not look" in m and "ZeroDivisionError" in m and "cli.py --help" in m
    chk(raised, "a-launch-never-fails-on-the-lines: filled raised, the brief went out and says so")


def main():
    for t in (t_lines_come_from_the_parser, t_could_not_look_is_said, t_item_and_seat_are_filled,
              t_judgement_stays_a_blank, t_no_owner_flag, t_no_spend_in_the_text, t_the_text_stays_short,
              t_every_detached_launch_carries_the_lines, t_a_launch_never_fails_on_the_lines):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            chk(lambda: False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
