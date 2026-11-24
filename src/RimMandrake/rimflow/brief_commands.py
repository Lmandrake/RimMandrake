#!/usr/bin/env python3
"""brief_commands.py: the commands of a detached run, filled in with its item and seat, made from each tool's own argparse
parser when the run is launched. No model, no tokens.

Item RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES. Page design/specs/2026-11-23-brief-commands/boundary.md;
selftest selftest_brief_commands.py. `detached_helper.brief_message` puts the text in every detached brief.

    python3 src/RimMandrake/rimflow/brief_commands.py ITEM [--seat BENCH]    print the text a run of ITEM would carry
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

MAX_CHARS = 12000   # the text is read again on every turn of a run; a longer one loses its lists of other flags
HELP_CHARS = 300    # one flag's help (cli.py file --effect, the longest one that a run needs whole, is 260); cut above it
OWNER_FLAGS = ("--owner-said", "--by-card", "--per-ruling")     # never offered to a run
NOISE = ("--help", "--target", "--mode", "--row", "--target-field")     # a detached run never uses them
COULD_NOT = "could not look"
HEAD = ("- The commands of this run, filled in from each tool's own parser at launch, so you need no `--help` for them. "
        "Copy a line;\n  a `<...>` is yours to write. `help` says what a blank takes; `also` names the other flags.\n")


def _rimflow():
    import cli
    return cli.build_parser()


def _maturation():
    import maturation
    return maturation.build_parser()


def _lessons():
    import lessons
    return lessons.build_parser()


def _publish():
    import publish
    return publish.build_parser()


# tool -> (the command as a run types it, its parser)
TOOLS = {"rimflow": ("python3 src/RimMandrake/rimflow/cli.py", _rimflow),
         "maturation": ("python3 src/RimMandrake/rimflow/maturation.py", _maturation),
         "lessons": ("python3 src/RimMandrake/Utils/lessons.py", _lessons),
         "publish": ("./publish", _publish)}
IT, SEAT, AUTO = object(), object(), "detached run"
# (tool, verb, what it is for, {positional: value}, [(wanted flag, value)]). A value: IT, SEAT, text, or None for a switch.
# A required positional or flag that is not named here is added from the parser, as a blank.
SPEC = (
    ("rimflow", "claim", "claim your item, first of all", {"id": IT}, [("--seat", SEAT), ("--why", AUTO), ("--publish", None)]),
    ("rimflow", "note", "write a note on your item", {"id": IT},
     [("--text", "<text>"), ("--seat", SEAT), ("--why", AUTO), ("--publish", None)]),
    ("rimflow", "wait", "put a dated wait on your item", {"id": IT},
     [("--until", "<YYYY-MM-DD>"), ("--reason", "<who acts next and on what>"), ("--seat", SEAT), ("--why", AUTO),
      ("--publish", None)]),
    ("rimflow", "close", "close your item", {"id": IT},
     [("--sha", "<sha that ./publish printed>"), ("--evidence", "<what ran and its result>"), ("--seat", SEAT),
      ("--why", "<your reason>"), ("--publish", None)]),
    ("rimflow", "verify", "record one run of your item's test", {"id": IT},
     [("--result", None), ("--config", "<what it ran on>"), ("--evidence", "<path of the log>"), ("--seat", SEAT),
      ("--why", "<your reason>"), ("--publish", None)]),
    ("rimflow", "file", "file a new item found on this run",
     {"id": "<NEW ITEM: RIMMANDRAKE_VERB_INTENTION_TWIST>"},
     [("--for", SEAT), ("--title", "<title>"), ("--caused-by", IT),
      ("--effect", "<outcome check that fails now; none exists: drop --effect>"), ("--seat", SEAT), ("--why", "<your reason>"), ("--publish", None)]),
    ("maturation", "red-seen", "record that a deciding test was seen red on a planted fault",
     {"mod": "<Mod>", "test": "<test id>"}, [("--patch", "<the planted fault's patch>")]),
    ("lessons", "add", "file one lesson", {"text": "<the lesson>"}, [("--seat", SEAT), ("--item", IT)]),
    ("publish", None, "land files (explicit paths)", {"paths": "<path>"}, [("-m", "{item}: <what>")]),
)


def _blank(a):
    """-> the named blank of one parser action: its choices, or its metavar or name."""
    if a.choices:
        return "<%s>" % "|".join(str(c) for c in a.choices)
    name = a.metavar if isinstance(a.metavar, str) else a.dest
    name = "".join(c for c in str(name) if c not in "\"'`$<>\\").strip()
    return "<%s>" % (name if name.strip(".… ") else a.dest)


def _word(value, item, seat):
    if value is IT:
        return item
    if value is SEAT:
        return seat
    return '"%s"' % value.replace("{item}", item)


def _flag_takes_value(a):
    return a.nargs != 0


def _verb_parser(parser, verb):
    """-> the subparser of `verb` (the parser itself when the tool has no verbs), None when the parser lost it."""
    if verb is None:
        parser._actions     # noqa: B018 - an unreadable parser raises here
        return parser
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            return a.choices.get(verb)
    return None


def _line(cmd, verb, p, posn, wanted, item, seat):
    """-> (the filled command, [(flag, why) that could not be put in it], the actions it used)."""
    words, lost, used, last = [cmd] + ([verb] if verb else []), [], [], []
    for a in p._actions:            # the positionals, in the parser's order
        if a.option_strings or isinstance(a, argparse._SubParsersAction):
            continue
        if a.nargs in ("?", "*") and a.dest not in posn:
            continue
        (last if a.nargs in ("*", "+") else words).append(_word(posn.get(a.dest, _blank(a)), item, seat))
        used.append(a)
    for d in posn:
        if d not in [a.dest for a in used]:
            lost.append((d, "the parser has no positional `%s`" % d))
    for flag, value in wanted:
        a = p._option_string_actions.get(flag)
        if a is None:
            lost.append((flag, "the parser has no `%s`" % flag))
            continue
        words.append(flag)
        used.append(a)
        if _flag_takes_value(a):
            words.append(_word(value if value is not None else _blank(a), item, seat))
    for a in p._actions:            # what the parser requires and SPEC does not name
        if not (a.option_strings and a.required) or a in used:
            continue
        if set(a.option_strings) & set(OWNER_FLAGS):
            lost.append(("an owner flag", "the parser now requires an owner flag; not yours to give"))
            continue
        words.append(a.option_strings[-1])
        used.append(a)
        if _flag_takes_value(a):
            words.append(_word(_blank(a), item, seat))
    return " ".join(words + last), lost, used


def _help(a):
    """-> one flag's help on one line, cut at HELP_CHARS; "" when it has none, or states a spend."""
    import spend_talk
    h = " ".join(str(a.help or "").replace("%%", "%").replace("`", "").split())
    if spend_talk.is_spend(h) or "weighted" in h.lower():
        return ""
    return h if len(h) <= HELP_CHARS else h[:HELP_CHARS].rsplit(" ", 1)[0] + "…"


def _also(p, used, blanks, level):
    """-> the help of the line's blanks and the list of other flags. level 2: with help; 1: without; 0: nothing."""
    import spend_talk
    out, told = [], []
    for a in used if level == 2 else ():
        if a.option_strings and a.option_strings[-1] in blanks and _help(a):
            told.append("%s = %s" % (a.option_strings[-1], _help(a)))
    for a in p._actions if level else ():
        if not a.option_strings or a in used or a.help is argparse.SUPPRESS \
                or set(a.option_strings) & set(OWNER_FLAGS + NOISE):
            continue
        flag = a.option_strings[-1] + (" " + _blank(a) if _flag_takes_value(a) else "")
        if spend_talk.is_spend(flag):
            continue
        out.append(flag + (" (%s)" % _help(a) if level == 2 and _help(a) else ""))
    return "".join("    %s: %s\n" % (k, "; ".join(v)) for k, v in (("help", told), ("also", out)) if v)


def _render(read, item, seat, level):
    """read: {tool: (parser, why it could not be read)} -> (text, could_not_look)."""
    text, could_not = HEAD, []

    def say(what, cmd, why):
        could_not.append("%s: %s" % (what, why))
        return "- %s: %s: run `%s --help` (%s)\n" % (COULD_NOT, what, cmd, why)

    said = set()
    for tool, verb, title, posn, wanted in SPEC:
        cmd, _ = TOOLS[tool]
        name = (cmd.split("/")[-1] + " " + verb) if verb else cmd
        parser, why = read[tool]
        try:
            if why:
                raise RuntimeError(why)
            p = _verb_parser(parser, verb)
            line, lost, used = (None, [], []) if p is None else _line(cmd, verb, p, posn, wanted, item, seat)
            filled_in = [f for f, v in wanted if v in (IT, SEAT, AUTO)]
            more = "" if p is None else _also(p, used, [a.option_strings[-1] for a in used if a.option_strings and _flag_takes_value(a)
                                                        and not set(a.option_strings) & set(filled_in + ["--why"])], level)
        except Exception as e:  # noqa: BLE001 - an unreadable parser is said, never guessed at
            if tool not in said:
                said.add(tool)
                text += say(cmd, cmd, "%s: %s" % (type(e).__name__, e) if not why else why)
            continue
        if p is None:
            text += say(name, cmd, "the parser has no `%s`" % verb)
            continue
        text += "- %s:\n  `%s`\n%s" % (title[:1].upper() + title[1:], line, more)
        for flag, w in lost:
            text += say("%s %s" % (name, flag), (cmd + " " + verb) if verb else cmd, w)
    return text, could_not


def filled(item, seat, parsers=None):
    """-> {"text": the filled lines, "could_not_look": [what could not be read, and why]}. ValueError on no item or seat."""
    for what, v in (("item", item), ("seat", seat)):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("brief_commands.filled: no %s" % what)
    read = {}
    for tool, (_, make) in TOOLS.items():
        if parsers and tool in parsers:
            read[tool] = (parsers[tool], None)
            continue
        try:
            read[tool] = (make(), None)
        except (Exception, SystemExit) as e:  # noqa: BLE001
            read[tool] = (None, "%s: %s" % (type(e).__name__, e))
    for level in (2, 1, 0):
        text, could_not = _render(read, item, seat, level)
        if len(text) <= MAX_CHARS:
            break
    return {"text": text, "could_not_look": could_not}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("item")
    ap.add_argument("--seat", default="BENCH")
    a = ap.parse_args(argv)
    r = filled(a.item, a.seat)
    print(r["text"], end="")
    return 2 if r["could_not_look"] else 0


if __name__ == "__main__":
    sys.exit(main())
