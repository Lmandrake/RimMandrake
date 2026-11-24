"""proof_lint.py -- the proof-line lint rimflow runs at file, close and implemented, and the live-proof rules every mod proof reads (refused_proof, refused_site, proof_budget, live_rules).

Moved verbatim from rimflow/relentless_live.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import glob
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.dirname(os.path.realpath(os.path.join(HERE, "..", "..", "..", ".git")))     # a release tree's .git links to books
RULES = os.path.join(HERE, "run_rules.json")
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN", "GREEN-FULL")       # model.LEVEL_NEEDS says bridge; L3 is a judge, L4 a human
# PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02): "small mod lists should always be the way to test until a
# final verification pass on the whole huge mod list." Every live level but FINAL runs on any game that holds the item's
# mods and their dependencies; a FINAL clause is the full-list verification, run only when the full list is up.
FINAL = "GREEN-FULL"
FULL_LIST = os.path.join(BOOKS, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
TESTABLE = ("built", "validated")
DEFAULTS = {
    "flyer_re": r"\b(fly|flies|flying|flyers?|flight|wings?|airborne|takes? off|take-off)\b",
    # A vehicle's flight is no flyer's (SEABED_DESCENT_ASCENT_1, "Gravship flies..."; flyer_word). The creature words never
    # excuse: the standing ruling is about Pawn_FlightTracker creatures, and a doubt stays refused.
    "vehicle_re": r"\b(grav-?ships?|star-?ships?|space-?ships?|ships?|shuttles?|transport pods?|drop pods?)\b",
    "creature_re": r"\b(flyers?|fliers?|wings?|creatures?|animals?|birds?|insects?|bats?|mynocks?)\b"
                   r"|MaxFlightTime|FlightTracker|flyingAnimation",
    "forbid_re": r"modlist_swap|modcheck\s+run|deploy_custom_mods\.py\b.*--apply|(^|[\s/;&|()])game\s+(UP|DOWN|DEPLOYING|LOADING)\b"
                 r"|stop_game|launch_game|load_game|execute_debug_action|--yes-i-know-this-is-live",
    "proof_max_s": 600,
    "plan_max_s": 500,
    "gate_plan_max_s": 180,  # relentless_live_round._plan_into: deploy_custom_mods.py --gate, inside a supervisor tick
    "site_max_s": 480,
    "health_max_s": 120,
    "repeat_unmeasured": 3,
    "infra_games": 3,       # INFRA on this many games for one build: a harness fault, held, never a strike
}
RELOAD = "reload needed"        # relentless_game RESTAGE reads this prefix; the round skips it on the same game
STALE = "changed since the built commit"        # terminal for its build: no game can run it (relentless_live_round.due)
DEFECT = "proof or site defect"     # an UNMEASURED no rerun can change: terminal for its build, back to a worker
# Every DEFECT why ends "... cannot help: <the cause>", so cause() can read the cause back out of it.
DEFECT_HEAD = re.compile(r"^%s: .*? cannot help: " % DEFECT)
SITE_CMD = re.compile(r"^python\.exe src/RimMandrake/Utils/live_site\.py(?: --[a-z][a-z-]*(?: [A-Za-z0-9_.\-]+)?)+$")
# LIVE_EXIT1_INABILITY_READ_AS_MOD_FAIL (owner 2026-11-03: "the checker was unable to measure something, and interpreted
# that as a wrong value rather than an inability that should have been reported up"). Exit 1 is a FAIL only when the
# proof asked and the answer missed the bar. A Python traceback also exits 1, and so did proofs that printed their own
# UNMEASURED; 14 items churned on such rows read as game_fail strikes. could_not_ask() reads the log's tail; every
# pattern is from a real FAIL row of 2026-11-02..04 (relentless/live/*.log).
# The box or the instrument failed: no proof or mod change helps (relentless_game._harness: alarm, restage later, no strike)
GUARD_REFUSAL = r"ConcurrentBridgeClient: refusing "
EXIT1_HARNESS = re.compile(
    r"cannot reach the bridge from WSL|IndeterminateError|No space left on device|\[Errno 28\]|Wsl/Service/"
    r"|object has no attribute 'sendall'|UtilAcceptVsock|BrokenPipeError|ConnectionResetError|ConnectionRefusedError|ConnectionAbortedError"
    # PROOF_CRASH_FIX_READ_AS_MOD_FAILURE: modcheck's deploy died on a DLL the running game holds (STILLSAND 2026-11-05,
    # RuntimeError "deploy of Stillsand FAILED" then "NOT written ... locked by the running game"); the reader chained
    # after it judged an older run and printed "FAIL Stillsand", booked as the mod's FAIL
    r"|locked by the running game|NOTHING WAS WRITTEN, and the repo and game still DIFFER"
    # LIVETIER_PREFLIGHT_FIX_TRIPS_OWN_GUARD: bridge_concurrency_guard refused a step of the proof; see setup_refused
    r"|" + GUARD_REFUSAL)
# The running load is not the one the proof needs (wrong tier, a stale DLL): RELOAD, so the game phase restages
EXIT1_RELOAD = re.compile(r"^(?:WRONG_TIER|WRONG_LIST)\b|stale deploy|redeployed after launch")
# The same, as one row of a proof that may also have charged the mod: read only when no `FAIL MOD` row did (TITANIC's
# UNMEASURED SITE row "No loaded type 'LargePawns.Settings'" sat beside two real MOD FAILs)
EXIT1_UNLOADED = re.compile(r"No loaded type '|is not loaded in the running game|intended ids absent from the next load")
# A verdict-shaped line: the LAST one says what the proof itself concluded
VERDICT_LINE = re.compile(r"^(?:(?:VERDICT|LIVE)\s*:?\s*|RESULT\s+\S+\s+|[\w./-]+:\s+)?(PASS|FAIL|UNMEASURED|NOT REPRODUCED|NOT SHARED)\b")
# RELENTLESS_DIAGNOSE_REPRO_MISS_AS_GAME_FAIL: a defect-repro proof that ran on its site and did not see the defect says so
# in its own verdict (LEANINGSCRUB_STALL_SHARED_MOVE_1's repro_stall_move.py: "NOT REPRODUCED: neither animal moved",
# "NOT SHARED: the two net moves differ"). That is an answer, not a dud and never the mod's FAIL: 20 attempts and 4 live
# misses were booked game_fail or game_unmeasured and sent to new builders. Its why starts REPRO_MISS; relentless_game
# holds the item as not reproduced after repro_miss_limit of them on one build.
REPRO_MISS_VERDICTS = ("NOT REPRODUCED", "NOT SHARED")
# The instrument read nothing: `x=None`, `read None`, `site None` (HEALTH_CHECK, ACC_BIOMES, WEEPINGSTONES), or there was
# nothing on the map or world to measure (HORRORS: "no candidate tile on this world"), or the driver handed back nothing
# (EGROWTH "-> None" / "wrote no", ASHKARR "returned no fields", WASTELAND "no component", STILLSAND "0 matching rows")
READ_NOTHING = re.compile(r"(?:\bread\s+|[=:]\s*|->\s*|^\w+\s+)None\b|\bno (?:candidate|sample|results?|run JSON|component)\b"
                          r"|\bwrote no\b|\breturned no fields\b|\b0 matching rows\b")
KV_VALUE = re.compile(r"\b\w+=([^\s,;)]+)")
KV_NONE = re.compile(r"\b\w+=None\b")    # a `k=None` among real `k=v` reads is one empty field of an answer, not no answer
# A row the proof itself charged to the mod: `A2 FAIL MOD ...` (a row id, then the status and class), never prose that
# merely mentions the words ("Only FAIL MOD rows count" is no row)
MOD_ROW = re.compile(r"^\s*\[?(?=[\w./-]*[\d_])[\w./-]+\]?:?\s+FAIL\s+MOD\b")    # the id holds a digit or _
FAIL_ROW = re.compile(r"^\s*\[?(?=[\w./-]*[\d_])[\w./-]+\]?:?\s+FAIL\b")     # `T1 FAIL: ...`, a row the proof failed
# A harness or reload marker the line itself negates or passes: "no ConnectionRefusedError", "stale deploy=False",
# "PASS: ... not a stale deploy" report its absence
NEGATED = re.compile(r"\b(?:no|not|without|never)\s+(?:[\w-]+\s+)?$")     # lower case: "NOT READY: IndeterminateError" is a refusal
NEGATED_AFTER = re.compile(r"^\s*[=:]\s*(?:False|0|no|none)\b", re.I)
# The exception that ends a traceback: the first unindented line after it names its class (StopIteration and KeyboardInterrupt
# end in neither Error nor Exception)
TB_END = re.compile(r"^(?:[A-Za-z_]\w*\.)*([A-Za-z_]\w*)(?::|$)")
SRC_MOD = re.compile(r"^src/(Rim[A-Za-z]+)/([^/]+)/(.+)$", re.S)     # src/<tier>/<Mod>/<path in the mod>


def proof_budget(proof, default_s):
    """The harness limit for one proof: `default_s`, or its own `--max-seconds N` plus 120 s when that is longer (a proof that
    asks for 1800 s must not be killed at 600; GAMECOMP_STALL_HUNT_SEVEN_SECONDS A2 timed out twice). Pure."""
    m = re.search(r"--max-seconds[ =](\d+)", proof or "")
    return max(default_s, int(m.group(1)) + 120) if m else default_s


def live_rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


# ---------------------------------------------------------------- criterion and proof checks

sys.path.insert(0, HERE)
import model                                   # noqa: E402  the ledger's legacy cap and criterion line
import live_observe                            # noqa: E402  the RMOBS measurement protocol; the regexes are its fallback

CUT_AT = model.CRITERION_TEXT_MAX
CRIT_LINE = model.CRITERION_LINE_RE
CRIT_SPILL = re.compile(re.escape(model.CRITERION_SPILL_PREFIX) + r"([0-9a-f]{20}\.txt)\]\Z")


def whole_criterion(c, prose):
    """Read whole inline or spilled text. A legacy row at CUT_AT still needs its prose copy."""
    c, text = dict(c), c.get("text") or ""
    spill = CRIT_SPILL.search(text)
    if spill:
        path = os.path.join(fulltext.side_dir(), spill.group(1))
        try:
            whole = fulltext.read(path)
            if len(whole) <= CUT_AT or not whole.startswith(text[:spill.start()]):
                raise ValueError("the side file does not match the ledger preview")
            c["text"] = whole
            c.pop("text_error", None)
        except (OSError, ValueError) as e:
            c["text_error"] = "could not read spilled criterion text at %s (%s)" % (path, e)
        return c
    if len(text) != CUT_AT:
        return c
    for line in (prose or "").splitlines():
        m = CRIT_LINE.match(line)
        if m and m.group("cid") == c["id"] and m.group("level") == c["level"] and m.group("text").strip().startswith(text):
            c["text"] = m.group("text").strip()
            return c
        if m and m.group("cid") == c["id"]:
            c["retiered"] = True     # a line of that id says something else: the ledger holds an older criterion
    c["cut"] = True
    return c


def owed(item, criterion):
    """-> (level, text) of a live criterion the item owes, or raise ValueError saying why it is not one."""
    if item is None:
        raise ValueError("no such item")
    if item["state"] not in TESTABLE:
        raise ValueError("%s is %s: only a built or validated item has a build to test" % (item["id"], item["state"]))
    if not item.get("built_sha"):
        raise ValueError("%s has no built sha" % item["id"])
    crit = {c["id"]: c for c in item.get("criteria") or []}
    if criterion not in crit:
        raise ValueError("%s has no criterion %s" % (item["id"], criterion))
    if criterion not in (item.get("outstanding") or []):
        raise ValueError("%s %s is not owed" % (item["id"], criterion))
    level = crit[criterion]["level"]
    if crit[criterion].get("text_error"):
        raise ValueError("%s %s: %s" % (item["id"], criterion, crit[criterion]["text_error"]))
    if crit[criterion].get("cut") and crit[criterion].get("retiered"):
        raise ValueError("%s %s is cut at %d chars on the ledger and the item's criteria now say something else under "
                         "that id (re-tiered): re-record them (`rimflow implemented --criteria-file`, the supervisor's "
                         "verb) before a proof can be judged" % (item["id"], criterion, CUT_AT))
    if crit[criterion].get("cut"):
        raise ValueError("%s %s is cut at %d chars on the ledger and no prose holds the rest: a proof cannot be judged "
                         "against a criterion nobody can read whole" % (item["id"], criterion, CUT_AT))
    if level not in LIVE_LEVELS:
        raise ValueError("%s %s is %s, not a live level (%s)" % (item["id"], criterion, level, ", ".join(LIVE_LEVELS)))
    return level, crit[criterion].get("text") or ""


def vehicle_item(lr, title, *texts):
    """True when the item is about a vehicle's flight: its title's subject is the vehicle (named before any flight word, so
    "Mynock flies around the gravship" is not one) and no text of the item names a creature. Pure."""
    t = title or ""
    v = re.search(lr["vehicle_re"], t, re.I)
    if not v:
        return False
    f = re.search(lr["flyer_re"], t, re.I)
    if f and f.start() < v.start():
        return False
    return not any(re.search(lr["creature_re"], s or "", re.I) for s in (t,) + texts)


def flyer_word(lr, title, *texts):
    """-> (which text, the flight word) when the item names a flyer's flight, or None. texts: (what, text) pairs. Pure."""
    if vehicle_item(lr, title, *[s for _, s in texts]):
        return None
    for what, s in (("title", title),) + texts:
        m = re.search(lr["flyer_re"], s or "", re.I)
        if m:
            return what, m.group(0)
    return None


# `$(wslpath -w <literal path>)`: the one expansion a gate can still read, for its output is that path's Windows spelling.
# LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: all 17 '$' refusals since 7c16acb1 were this idiom. The path holds no quote, space,
# `$`, backtick, glob, brace or shell operator and never starts with `-` (an option: wslpath prints nothing), and the
# expansion is a whole word, so no command name can be spliced from it (`$(wslpath -w x)game UP`). Its output differs
# from its text (`\\wsl.localhost\...`), so refused_proof gates both the text with the path in and with it gone.
# Quotes around it are left in place (a swallowed lone `"` would let unquoted() misread every quote after it).
WSLPATH = re.compile(r"(?:(?<![^\s=])|(?<=^\")|(?<=[\s=]\"))\$\(\s*wslpath\s+-w\s+([A-Za-z0-9_./][A-Za-z0-9_./+-]*)\s*\)"
                     r"(?=[\s;|&<>]|$|\"(?:[\s;|&<>]|$))")


def unquoted(text):
    """`text` with the inside of every single-quoted span dropped: bash expands nothing there (`'{"a":1,"b":2}'` is no
    brace expansion, `'$x'` no variable). A `'` inside double quotes or after a backslash opens nothing. An unclosed
    span keeps its text, so the gate still reads it. Pure."""
    out, i, dq = [], 0, False
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            out.append(text[i:i + 2])
            i += 2
            continue
        if c == '"':
            dq = not dq
        elif c == "'" and not dq:
            j = text.find("'", i + 1)
            if j >= 0:
                out.append("''")
                i = j + 1
                continue
        out.append(c)
        i += 1
    return "".join(out)


# a live proof that reads the owner's own ledger shard measures his act (a look, a keep), which no game can show
OWNER_LEDGER = re.compile(r"\bOWNER\.jsonl\b")


def refused_proof(lr, title, text, proof):
    """-> why this run may not happen on the live game, or None."""
    hit = flyer_word(lr, title, ("criterion", text), ("proof", proof))
    if hit:
        return "flyer: the %s names %r; a flyer's flight is never live-tested (standing ruling)" % hit
    if OWNER_LEDGER.search(proof or ""):
        return ("owner act: the proof reads his ledger (OWNER.jsonl), not the running game, so every live round fails "
                "it until he acts (OPS_CHURN_DIAGNOSE_WATER_PPCC_FKGE); the game lane skips such a clause (owner_look) and "
                "holds the item on him once the rest PASS")
    gone = WSLPATH.sub(" ", proof or "")
    # unquoted() knows no comment or heredoc, either of which can end a quote on another line: such a proof is read raw
    scan = gone if ("\n" in gone or "<<" in gone) else unquoted(gone)
    m = re.search(r"\$|`|\\\n|\beval\b|\{[^}]*,[^}]*\}", scan)     # expansion: bash builds the command at run time
    if m:
        return "the proof text builds its command at run time (%r): a gate cannot read what bash will run" % m.group(0)
    m = next((m for m in (re.search(lr["forbid_re"], re.sub(r"[\'\"\\]", "", t))      # bash drops quotes: ap''ply is --apply
                          for t in (WSLPATH.sub(r"\1", proof or ""), gone)) if m), None)
    if m:
        return "the proof would change the running game (%r): a load or a mutation is not this tier" % m.group(0)
    return None


# PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN: a proof line naming a script the tree lacks ("can't open file", a plan nobody wrote)
# measured nothing on the game it took: the check is offline, so it is asked where the line is written, not at the round.
REPO_SCRIPT = re.compile(r"^(?:\./)?(?:src|skills|infrastructure|design|tools)/[^\s*?\[\]{}$`'\"]+\.(?:py|sh)$")
PYTHONS = re.compile(r"^(?:.*/)?(?:python(?:3(?:\.\d+)?)?|python3?\.exe|py)$")
# Runs the file named after it; `source`/`.` run it in this shell. An interpreter's -c or -m names no script (-ec too).
SHELLS = re.compile(r"^(?:(?:.*/)?(?:ba|z|da)?sh(?:\.exe)?|source|\.)$")
INTERP_NO_SCRIPT = re.compile(r"^(?:-|-[A-Za-z]*[cm])$")
INTERP_VALUED = re.compile(r"^-[A-Za-z]*[oWX]$")        # bash -o pipefail, python -W ignore / -X utf8
SHELL_OPS = {"&&", "||", ";", "|", "(", ")", "&", ";;", "|&", "\n"}
REDIRECTS = {">", ">>", "<", "<<", "<<<", "&>", ">&", "<&"}
OPS_LONGEST_FIRST = sorted(SHELL_OPS | REDIRECTS, key=len, reverse=True)
PREFIX_WORDS = {"if", "then", "elif", "else", "while", "until", "do", "fi", "done", "esac", "!", "{", "}"}
CONTROL_WORDS = (PREFIX_WORDS - {"!", "}"}) | {"for", "select"}
LOOP_WORDS = {"for", "select", "while", "until"}
DIR_WORDS = {"cd", "pushd", "popd", "eval", "trap", "source", "."}
WRAPPERS = {"env": {"-u", "--unset", "-C", "--chdir", "-S"}, "nice": {"-n"}, "nohup": set(), "exec": {"-a"}, "time": set(),
            "timeout": {"-k", "-s"}, "xargs": {"-I", "-n", "-P", "-L", "-d", "-a", "-s", "-E"}}
OTHER_TREE = re.compile(r"^(?:/|~|[A-Za-z]:)")


def shell_words(text):
    """-> [(word, is_operator)] as bash reads the line, so a quoted ';' stays an argument and a newline ends a command; a
    comment is dropped, and a redirect's file-descriptor digit (2>) with it. Raises ValueError on an open quote. Pure."""
    out, word, i, n = [], None, 0, len(text)

    def flush():
        nonlocal word
        if word is not None:
            out.append((word, False))
            word = None

    while i < n:
        c = text[i]
        if c in " \t\r":
            flush()
            i += 1
        elif c == "#" and word is None:
            while i < n and text[i] != "\n":
                i += 1
        elif c == "'":
            end = text.find("'", i + 1)
            if end < 0:
                raise ValueError("open quote")
            word = (word or "") + text[i + 1:end]
            i = end + 1
        elif c == '"':
            word, i = word or "", i + 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n and text[i + 1] in '"\\$`\n':
                    i += 1
                word += text[i]
                i += 1
            if i >= n:
                raise ValueError("open quote")
            i += 1
        elif c == "\\":
            if i + 1 >= n:
                raise ValueError("trailing escape")
            if text[i + 1] != "\n":
                word = (word or "") + text[i + 1]
            i += 2
        else:
            op = next((o for o in OPS_LONGEST_FIRST if text.startswith(o, i)), None)
            if op is None:
                word = (word or "") + c
                i += 1
                continue
            if word is not None and word.isdigit() and op[0] in "<>":
                word = None                   # 2>&1: the digit is part of the redirect, not an argument
            flush()
            out.append((op, True))
            i += len(op)
    flush()
    return out


def proof_scripts(proof):
    """-> the repo-relative scripts a proof line executes, in order, each once: a command word with a slash
    (`./src/.../x.sh`), the file an interpreter is given (`python3 <script>`, `bash <script>`, `source <script>`, past
    env/timeout/nice/nohup/exec/time/xargs), and a runner's `--plan <script>`. Any other argument is the command's data
    (`printf tools/gone.py`, `test ! -f src/x.py`, `python3 x.py src/y.py`): PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS.
    A `cd` is placed in one shape only: a plain command (`command`, `builtin` and `time` before it are fine), not negated, not
    a member of a pipeline, not right of `||`, before any group or compound on the line, with a relative in-tree argument, and
    followed by `&&`. Only that proves it ran, so it holds for the rest of its `&&` chain, past which (`;`, newline, `||`, `&`)
    the line's directory is unknown. Every other cd, `pushd`, `popd`, `eval`, `trap`, `env -C` or a sourced script also makes
    it unknown, and an unknown directory names nothing: never a false refusal. `( )` alone restores what it found. A `case`,
    a function definition (its `)` and its later call do not read in order) or a loop with a directory word anywhere after it
    (it reruns what came before that word) ends the naming outright, as a heredoc does.
    Absolute and Windows paths are another tree's and are not named; a line that cannot be split names
    none (refused_proof reads it). Pure."""
    try:
        toks = shell_words(WSLPATH.sub(" ", proof or ""))
    except ValueError:
        return []
    out, stack = [], []
    cwd, control, prev, chain = "", False, "", False    # cwd: repo-relative, None once not known; chain: inside a cd's && chain
    cmd, start, skip, wrap, interp, runner, plan, cd_args = None, True, False, None, False, False, False, None
    external, sourced, prefixed, negated = False, False, False, False   # external: past env/timeout/..., a child: its cd moves no shell

    def name(arg):
        if cwd is None or OTHER_TREE.match(arg):
            return
        rel = posixpath.normpath(posixpath.join(cwd, arg))
        if REPO_SCRIPT.match(rel) and rel not in out:
            out.append(rel)

    def moved(op):
        """Where this line stands once a finished `cd` (args in cd_args) is followed by op."""
        nonlocal chain
        args = [a for a in cd_args if a == "-" or not a.startswith("-")]
        if op != "&&" or prev in ("|", "|&", "||") or control or negated or cwd is None or "CDPATH" in proof \
                or len(args) != 1 or args[0] == "-" or OTHER_TREE.match(args[0]) or re.search(r"[$`*?\[{]", args[0]):
            return None
        chain = True
        rel = posixpath.normpath(posixpath.join(cwd, args[0]))
        return None if rel == ".." or rel.startswith("../") else ("" if rel == "." else rel)

    for i, (t, is_op) in enumerate(toks):
        if is_op and t in REDIRECTS:
            if t == "<<":
                break                         # what follows is the heredoc's text, not commands
            skip = True                       # a redirect's target is a file the line writes or reads, not a script
            continue
        if is_op:
            if start and t == "\n":
                continue                      # a blank line, or `&&` then a newline: the same list goes on
            if t == "(" and cmd is not None:
                return out                    # `f()`: its body runs at a call we do not follow
            if cd_args is not None:
                cwd = moved(t)
            if t == "(":
                stack.append((cwd, chain))
                chain = False
            elif t == ")" and stack:
                cwd, chain = stack.pop()
            elif t in (";", "\n", ";;", "&", "||"):
                if chain:
                    cwd = None                # what follows may run whether or not the chain's cd did
                chain = False
            prev = t
            cmd, start, skip, wrap, interp, runner, plan, cd_args = None, True, False, None, False, False, False, None
            external, sourced, prefixed, negated = False, False, False, False
            continue
        if skip:
            skip = False
            continue
        if start:
            if t in LOOP_WORDS and any(w in DIR_WORDS for w, _ in toks[i + 1:]):
                return out
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
                continue                      # VAR=value before the command
            if t in PREFIX_WORDS:
                control = control or t in CONTROL_WORDS
                negated = negated or t == "!"
                continue
            if t in WRAPPERS:
                wrap = WRAPPERS[t]
                external = external or t != "time"      # `time` is a keyword: what it times runs in this shell
                continue
            if t in ("command", "builtin") and not external:
                prefixed = True
                continue
            if t in ("-p", "--") and prefixed:
                continue                      # `command -p cd d`; `command -v x` falls through: x is not run
            if wrap is not None:
                if t.startswith("-"):
                    if t in ("-C", "--chdir") or t.startswith("--chdir="):
                        cwd = None
                    skip = t in wrap
                    continue
                if re.match(r"^\d+(?:\.\d+)?[smhd]?$", t):
                    continue                  # timeout's duration, nice's old -5 style
            if t in ("case", "function"):
                return out                    # a pattern's `)` closes no subshell; a function's body runs at its call
            start, cmd = False, t
            control = control or t in CONTROL_WORDS
            if t == "cd" and not external:
                cd_args = []
            elif t in ("pushd", "popd", "eval", "trap") and not external:
                cwd = None
            elif t in ("source", ".") and not external:
                sourced = interp = True
            elif PYTHONS.match(t) or SHELLS.match(t):
                interp = runner = True
            elif "/" in t:                    # no slash: bash looks on PATH, never in the working directory
                name(t)
                runner = True
            continue
        if cd_args is not None:
            cd_args.append(t)
        elif interp:
            if INTERP_NO_SCRIPT.match(t):
                interp = False
            elif INTERP_VALUED.match(t):
                skip = True
            elif not t.startswith("-"):
                interp = False
                name(t)
                if sourced:
                    cwd = None                # a sourced script may cd, and this shell stays there
        elif runner:
            if plan:
                name(t)
            elif t.startswith("--plan="):
                name(t.split("=", 1)[1])
            plan = t == "--plan"
    return out


def missing_scripts(proof, has):
    """has(rel) -> True when the tree the line will run in holds `rel`. -> why the line names a script that tree lacks,
    or None. Pure but for `has`."""
    gone = [s for s in proof_scripts(proof) if not has(s)]
    if gone:
        return "the proof names %s, which the tree it runs in does not hold: it can only end UNMEASURED" % (
            ", ".join(gone))
    return None


def lint_lines(lr, title, lines, has=None, texts=None):
    """The offline half of what the live lane would refuse, for every proof line of an item, asked where the line is
    written (rimflow file / implemented / close, `finish`, the game phase's preflight). lines: {cid: proof};
    texts: {cid: whole criterion text} where known; has: a file test on the tree the line runs in (None: no script
    check). -> [(cid, why)]; a flyer's or his own look's line is named too (the caller decides whether it refuses)."""
    out = []
    for cid in sorted(lines):
        proof = lines[cid]
        why = refused_proof(lr, title, (texts or {}).get(cid) or "", proof)
        if not why and has is not None:
            why = missing_scripts(proof, has)
        if why:
            out.append((cid, why))
    return out


def lint_item(lr, item, title, lines, has=None, prose=""):
    """lint_lines plus the criterion checks owed() makes that need no build: unreadable spill or legacy cut text.
    item: {"criteria": [{"id", "level", "text"}], "outstanding"?: [ids]} or None (a filing has none yet).
    -> [(cid, why)]."""
    texts, out = {}, []
    left = (item or {}).get("outstanding")       # None: every live clause (no ledger state yet); a list: only those owed
    for c in (item or {}).get("criteria") or []:
        w = whole_criterion(c, prose)
        texts[c["id"]] = w.get("text") or ""
        if c.get("level") not in LIVE_LEVELS or (left is not None and c["id"] not in left):
            continue
        if w.get("text_error"):
            out.append((c["id"], w["text_error"]))
        elif w.get("cut"):
            out.append((c["id"], "%s is cut at %d chars on the ledger and %s: a proof cannot be judged against it; write "
                        "the whole line in live_proofs/<ID>.criteria or the item's prose" % (
                            c["id"], CUT_AT, "a line of that id now says something else (re-tiered)"
                            if w.get("retiered") else "no prose holds the rest")))
    return out + lint_lines(lr, title, lines, has, texts)


def refused_site(site):
    """-> why a live-site command may not run, or None. Only live_site.py, plain arguments: the site step is the one
    change this tier makes to the game, so it is one reviewed tool, never a free command."""
    if site and not SITE_CMD.match(site.strip()):
        return "the live-site command %r is not `python.exe src/RimMandrake/Utils/live_site.py <plain args>`" % site
    return None


def cause(why):
    """An UNMEASURED why -> the key two runs share when the same thing stopped them: no paths, numbers or times."""
    w = DEFECT_HEAD.sub("", why or "")      # the head would eat the whole cap, and every defect would read alike
    # a number with its unit attached is still a number ("mean=50.176ms" made every run its own cause)
    w = re.sub(r"\([^()]*\.log\)|/\S+|\b\d[\d:.TZ-]*[A-Za-z]*\b", "", w)
    return re.sub(r"\s+", " ", w).strip()


def fingerprint(criterion, why, proof, text=""):
    """A refusal -> the key that stays the same while nothing a worker could change has changed: the criterion, the cause
    (no paths, numbers or times), the proof line and the criterion's whole text. The same key twice means the item came
    back unchanged, and running it again can only say the same thing (LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD)."""
    import hashlib
    raw = "\x1f".join([criterion or "", cause(why), proof or "", text or ""])
    return hashlib.sha1(raw.encode("utf-8", "replace")).hexdigest()[:16]


def cites(subject, item_id):
    """True when a commit subject names `item_id` as a whole token (FOO_1 is not FOO_12, nor XFOO_1)."""
    return bool(item_id) and re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(item_id), subject or "") is not None


def build_shas(fx, sha, item_id=None):
    """The commits whose game files are the build's -> [sha, ...]. Normally the built commit alone. When it touched no
    shippable mod file (a proof-only or harness-only fix landed last) and the item is known, every non-merge ancestor
    commit whose SUBJECT names the item joins it (fx.cited): those hold the item's mod files.
    PROOF_SHA_FIX_DEPLOYS_NOTHING_TWICE: GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS was built on 8f6c177 then 2e9ce47, which
    touched only proofs and lessons, so runs.jsonl read deploy='' and no running-load gap: A1 ran and FAILED twice on a
    game without GimmeSomeSlack. A fake without `cited` keeps the built commit alone. Only a path that can reach the game
    (reaches_game) makes the built commit a game build: a harness-only Utils/ edit landing last left the cited mod work
    out (review of 930b960a8e)."""
    if not item_id or not hasattr(fx, "cited"):
        return [sha]
    memo = {}
    for m in filter(None, (SRC_MOD.match(p) for p in fx.touched(sha))):
        if m.group(1, 2) not in memo:
            memo[m.group(1, 2)] = reaches_game(fx, m.group(1), m.group(2), (sha, sha + "^"))
    own = [m.group(0) for m in filter(None, (SRC_MOD.match(p) for p in fx.touched(sha))) if memo[m.group(1, 2)]]
    if game_files(own, fx.shippable):
        return [sha]
    return [sha] + [s for s in fx.cited(item_id, sha) if not (s.startswith(sha) or sha.startswith(s))]


def reaches_game(fx, tier, mod, revs=()):
    """True when a change under src/<tier>/<mod>/ can change what the game loads (stale_build, carry_scope):
    fx.game_input(tier, mod, revs) (the real fx: About/About.xml at HEAD or at any of `revs`, a compose source or shell, or
    compiled into another folder's .csproj), else a fake's fx.deployable(tier, mod), else True (every src/ folder).
    STALE_BUILD_SCOPE_DEPLOYED_MODS_ONLY review (930b960a8e): About.xml at HEAD alone let a commit deleting a whole mod
    skip the deleted-file guard, and dropped _Shared/ C# and BiomesShell, which ship inside other mods' outputs."""
    f = getattr(fx, "game_input", None)
    if callable(f):
        return f(tier, mod, tuple(revs))
    f = getattr(fx, "deployable", None)
    return f(tier, mod) if callable(f) else True


def stale_build(fx, sha, item_id=None):
    """-> (why or None, game files of the build). why says the game cannot run `sha`: it deleted a shipped file (a stale
    game copy cannot be told from the build), or a game file it touched changed in a later commit (STALE). Raises
    ValueError when the built commit cannot be read. item_id: a built commit with no game file stands for the game files
    of every commit citing the item (build_shas); staleness is still judged against `sha`, the build.
    Only a folder that can reach the game counts (reaches_game: a mod at HEAD, at a build sha or its parent, so deleting a
    whole mod still refuses; a compose source or shell; a folder another folder's .csproj compiles from, like _Shared/;
    a fake without fx.game_input/deployable counts every src/ folder, as before). STALE_BUILD_SCOPE_DEPLOYED_MODS_ONLY: GIZKA_STOWAWAY_UNMEASURED_ROWS_1 gen 6 (e87b8495b8) went
    back as game_stale_build because GOLD_PANNING (576c7659a1) edited src/RimMandrake/Utils/modcheck/required_checks.json,
    which an earlier commit citing the item had touched: Utils matches src/<tier>/<Mod>/ but deploys nothing, and the
    harness runs from the clone's HEAD whatever the build, so no game copy of it could be stale."""
    shas = build_shas(fx, sha, item_id)
    revs = [r for s in shas for r in (s, s + "^")]
    memo = {}

    def loads(p):
        m = SRC_MOD.match(p)
        if not m:
            return False
        if m.group(1, 2) not in memo:
            memo[m.group(1, 2)] = reaches_game(fx, m.group(1), m.group(2), revs)
        return memo[m.group(1, 2)]
    gone = [p for s in shas for p in fx.deleted(s) if SRC_MOD.match(p) and fx.shippable(SRC_MOD.match(p).group(3))
            and loads(p)]
    if gone:
        return "the build deleted %s: a stale game copy cannot be told from the build" % ", ".join(gone[:5]), []
    touched = [p for p in dict.fromkeys(p for s in shas for p in fx.touched(s)) if loads(p)]
    files = game_files(touched, fx.shippable)
    paths = [p for p in touched if SRC_MOD.match(p) and SRC_MOD.match(p).group(2, 3) in files]
    later = fx.changed_since(sha, paths) if paths else []
    if later:
        # the game folder holds today's bytes; a verdict on them is not a verdict on the built sha
        return "%s, so the game cannot run %s: %s" % (STALE, sha, ", ".join("%s (%s)" % pc for pc in later[:5])), files
    return None, files


def preflight(fx, lr, item_id, lines, sites=None):
    """What a live run of each line would refuse whatever the game does, asked before any game slot is spent
    (LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT, LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT). lines: {criterion: proof line}.
    -> [{"cid", "why", "fp", "kind"}]: kind "refused" (owed() or a proof/site refusal; a flyer is left to the game
    phase's own put-down) or "stale" (STALE, once for the build, cid None). A criterion no longer owed is skipped."""
    item = fx.item(item_id)
    out = []
    crit = {c["id"]: c for c in (item or {}).get("criteria") or []}
    for cid in sorted(lines):
        text = (crit.get(cid) or {}).get("text") or ""
        try:
            _level, text = owed(item, cid)
        except ValueError as e:
            if str(e).endswith(" is not owed"):
                continue
            out.append({"cid": cid, "why": str(e), "fp": fingerprint(cid, str(e), lines[cid], text), "kind": "refused"})
            continue
        why = refused_proof(lr, item["title"], text, lines[cid]) or refused_site((sites or {}).get(cid))
        if not why and getattr(fx, "has_file", None):
            # absent from the tree it runs in AND from the build: a books tree behind the build is a lag, not a defect
            why = missing_scripts(lines[cid], lambda rel: fx.has_file(rel) or bool(
                item.get("built_sha") and fx.has_file(rel, item["built_sha"])))
        if why and not why.startswith("flyer:"):
            out.append({"cid": cid, "why": why, "fp": fingerprint(cid, why, lines[cid], text), "kind": "refused"})
    if item and item.get("built_sha"):
        try:
            why, _files = stale_build(fx, item["built_sha"], item_id)
        except ValueError:
            why = None      # an unreadable commit is the run's to report, with its own row
        if why and why.startswith(STALE):
            out.append({"cid": None, "why": why, "fp": fingerprint("", why, item["built_sha"]), "kind": "stale"})
    return out


def last_line(path):
    """The last non-blank line of a log, cut to 200, or "" when it cannot be read."""
    lines = [x.strip() for x in read_text(path).splitlines() if x.strip()]
    return lines[-1] if lines else ""


def tail_lines(path):
    """The non-blank lines of a log: all of them (live_observe.whole cuts only past its LOG_MAX)."""
    return [x.strip() for x in live_observe.whole(read_text(path))[0].splitlines() if x.strip()]


def redirect_targets(proof):
    """-> the absolute files a proof command truncates its own output into (`> f`, `2> f`, `&> f`; never `>>`, whose
    file may hold an older run's lines, nor /dev/null), a `D:/` path as its /mnt/d twin; [] when it cannot be parsed.
    GAMEENV_FIX_PROOFCALL_B34890F8_ITEMS_WAIT: MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED A1 sent its runner's output to
    run.txt, where rimbridge_client's IndeterminateError sat; the live log held only the checker's FileNotFoundError on
    the json the runner never wrote, and the harness fault was booked UNKNOWN."""
    try:
        lx = shlex.shlex(proof or "", posix=True, punctuation_chars=True)
        lx.whitespace_split = True
        toks = list(lx)
    except ValueError:
        return []
    out = []
    for op, f in zip(toks, toks[1:]):
        if op not in (">", "&>") or f == "/dev/null":
            continue
        m = re.match(r"^([A-Za-z]):[/\\](.*)$", f)
        if m:
            f = "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
        if f.startswith("/") and f not in out:
            out.append(f)
    return out


def side_lines(proof):
    """The non-blank lines of every file the proof redirected its output into (redirect_targets), last 400 of each."""
    out = []
    for f in redirect_targets(proof):
        out += [x.strip() for x in read_text(f).splitlines() if x.strip()]
    return out


def could_not_ask(path, proof=None):
    """A proof that exited 1 and wrote no RMOBS rows -> (kind, line) when its log shows it could not ask, else None (a
    real FAIL). The regex reading is the migration aid of live_observe's protocol (LIVE_ROWS_FIX_STOP_GUESSING_LOGS).
    kind "harness": the box or instrument failed (EXIT1_HARNESS) - never the mod's, never the worker's;
    kind "reload": the running load is the wrong one for it (EXIT1_RELOAD, EXIT1_UNLOADED): a failed prerequisite, so
    the rows measured on it are no evidence;
    kind "miss": a defect-repro proof ran and did not reproduce the defect - its last verdict line is a REPRO_MISS_VERDICTS
    one (NOT REPRODUCED, NOT SHARED) and none says FAIL: an answer, never the mod's FAIL and never a dud;
    kind "dud": the proof measured nothing by its own word - every verdict line it wrote says UNMEASURED;
    kind "unknown": the log cannot say whether it measured - an uncaught exception (an AssertionError is the proof's own
    setup as often as the product, and any other exception may be the product's), or a None / zero-row read that may be
    the defect itself or a blind instrument.
    An observed violation is never erased (GPT test-tolerance advice 2026-11-04): a `FAIL MOD` row keeps the FAIL whatever
    else the run tripped over; any other FAIL row or verdict, anywhere in the whole log (never only the last verdict line,
    never an 8 KB tail), keeps it over a later UNMEASURED, a crash or a None read. Those still reach the worker as a
    FAIL, and the worker must explain them before any rebuild (relentless.DIAGNOSE_ENDS)."""
    lines = tail_lines(path)
    side = side_lines(proof)    # what the proof hid from its own log (redirect_targets) can still say it could not ask
    if any(MOD_ROW.match(x) for x in side + lines):
        return None             # an observed violation is never erased, whatever else the run tripped over
    for kind, rx in (("harness", EXIT1_HARNESS), ("reload", EXIT1_RELOAD)):
        for line in reversed(side + lines):
            if marker_hit(rx, line):
                return kind, line
    for line in reversed(lines):
        if marker_hit(EXIT1_UNLOADED, line):
            return "reload", line
    if any(observed_fail(x) for x in lines):
        return None             # a FAIL the proof reached, mixed rows or not: the worker explains it
    verdicts = [(i, m.group(1)) for i, m in ((i, VERDICT_LINE.match(x)) for i, x in enumerate(lines)) if m]
    at = verdicts[-1][0] if verdicts else -1
    tb = max((i for i, x in enumerate(lines) if x.startswith("Traceback (most recent call last)")), default=-1)
    if tb > at:
        ends = [m.group(1) for m in (TB_END.match(x) for x in lines[tb + 1:]
                                     if x and not x[0].isspace() and not x.startswith(("Traceback", "During handling")))
                if m]
        if ends:
            return "unknown", ("the proof crashed: %s (UNKNOWN: an exception names neither the product nor the "
                               "instrument)" % ends[-1])
    if verdicts and verdicts[-1][1] in REPRO_MISS_VERDICTS:
        return "miss", lines[at].strip()
    if verdicts and all(v == "UNMEASURED" for _, v in verdicts):
        return "dud", lines[at].strip()
    for line in reversed(lines):
        if read_nothing(line):
            return "unknown", ("UNKNOWN: a None or zero-row read (a measured absence or a blind instrument; RMOBS "
                               "absence says which): %s" % line)
    return None


def marker_hit(rx, line):
    """rx names a harness or reload fault on this line, and the line does not report its absence: a PASS line, or the
    marker after "no"/"not" or before "=False", says the fault did NOT happen (GPT review 2026-11-03)."""
    m = rx.search(line)
    if not m:
        return False
    v = VERDICT_LINE.match(line.strip())
    if v and v.group(1) == "PASS":
        return False
    return not (NEGATED.search(line[:m.start()]) or NEGATED_AFTER.match(line[m.end():]))


def observed_fail(line):
    """The proof's own FAIL verdict or row: an observed violation. A failed assert is not one (GPT 2026-11-04: proofs
    assert their own setup). A None on that line is what the proof saw (a setting that read None where `enabled` is
    wanted may be the defect), so it is never read as a dud."""
    v = VERDICT_LINE.match(line.strip())
    return bool(v and v.group(1) == "FAIL") or bool(FAIL_ROW.match(line))


def read_nothing(line):
    """READ_NOTHING on one line, except a `k=None` beside real `k=v` values: the instrument answered and one field is
    empty (BRIDGE_STALL_DIAGNOSTIC_1: `phaseStack=['update'] silentS=60.5 ... tickList=None` is the tool's own answer,
    and its FAIL is the mod's)."""
    if not READ_NOTHING.search(line):
        return False
    if any(v != "None" for v in KV_VALUE.findall(line)):
        return bool(READ_NOTHING.search(KV_NONE.sub("", line)))
    return True


def asked_reload(path):
    """A proof or site whose last line starts `reload needed:` asks for another load (the running one is the wrong list
    or save, which no rerun on it can change): that line is the row's why, so relentless_game restages (RESTAGE) instead
    of sending the item back as a proof that measured nothing (GENERATOR_MODS_PROVE_INERT_AFTER_CREATION: a list that
    must LACK two mods sat on a game holding them, ran twice, and went back to a worker). -> the line, or None."""
    ln = last_line(path)
    return ln if ln.startswith(RELOAD + ":") else None


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def game_files(paths, shippable):
    """The built commit's paths that ship to the game -> [(mod folder, path in the mod)]."""
    out = []
    for p in paths:
        m = SRC_MOD.match(p)
        if m and shippable(m.group(3)):
            out.append((m.group(2), m.group(3)))
    return out


_FOLDER_SEEN = {}


def is_package(name, folder=None):
    """A `live-mods:` name that is a workshop packageId (7f.alienworlds), not a mod folder of ours: it holds a dot and no
    mod folder has that exact name (modlist_swap.is_mod_folder: the game's Mods folder, a repo mod, a folded source or a
    compose target). OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK: the composed folder RimMandrake.Biomes, named on 9 live_proofs
    files, read as packageId 'rimmandrake.biomes' "installed in neither the Steam workshop folder nor the game's Mods
    folder", so OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN's gate could never pass (8.1M weighted tokens restaging).
    `folder` is injectable for the selftest. Only a folder is cached: is_mod_folder answers False on an unreadable repo
    (SystemExit from mod_dirs) or a folder not yet deployed, and a cached False would refuse that folder all process."""
    if "." not in (name or ""):
        return False
    if folder is not None:
        return not folder(name)
    if name not in _FOLDER_SEEN:
        import mod_names     # the one resolver (LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING); it caches no blind read
        if not mod_names.default_index().is_folder(name):
            return True
        _FOLDER_SEEN[name] = True
    return not _FOLDER_SEEN[name]


def with_shell(folded, shells):
    """deploy_custom_mods.folded() plus each compose manifest's settings-shell source as (target, target): the shell's
    files (BiomesShell/Assemblies/*.dll) land at Mods/<target>/<rel>, and the plan reports them under the target's own
    section (GAMEENV_FIX_DEPLOY_590E0C49_ITEMS_WAIT: a build touching only the shell DLL read 'the deploy plan does not
    cover BiomesShell' forever, deploy_args never composed it and no game copy was found). shells: {source: target}."""
    out = dict(folded or {})
    for src, target in (shells or {}).items():
        out.setdefault(src, (target, target))
    return out


def compose_shells(src_root):
    """{settings-shell source folder: composed target} from the compose manifest; {} when it is absent or unreadable
    (deploy_custom_mods.folded's rule: a broken manifest hides nothing it did not already hide)."""
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    try:
        import biomes_compose
        m = biomes_compose.load_manifest(src_root)
    except Exception:
        return {}
    src = ((m or {}).get("shell") or {}).get("source")
    return {src: m["target"]} if src and m.get("target") else {}


# ---------------------------------------------------------------- the one run

class Fx(object):
    """Everything that touches the world. The selftest swaps it."""

    def __init__(self, books=BOOKS, seat="BENCH", mods_dir=GAME_MODS):
        self.books, self.seat, self.mods_dir = books, seat, mods_dir
        # GAMEENV_FIX_HARNESS_09849AF1_ITEMS_WAIT: the health read and live_site.py are this one driver's processes,
        # not a concurrent client: one lineage for all of them (bridge_concurrency_guard.export_lineage)
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import bridge_concurrency_guard
        bridge_concurrency_guard.export_lineage()

    def item(self, item_id):
        sys.path.insert(0, HERE)
        import model
        it = model.replay(model.read()).items.get(item_id)
        if it is None:
            return None
        return {"id": it.id, "state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                "criteria": [whole_criterion(c, self.prose(it.id)) for c in it.criteria or []],
                "outstanding": list(it.outstanding or [])}

    def prose(self, item_id):
        """The item's prose, then its live_proofs/<ID>.criteria, which may hold whole lines for legacy cut rows."""
        out = []
        for d in ("infrastructure/state/items", "infrastructure/state/items/closed"):
            p = os.path.join(self.books, d, item_id + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    out.append(f.read())
                break
        p = os.path.join(self.books, "infrastructure/state/live_proofs", item_id + ".criteria")
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                out.append(f.read())
        return "\n".join(out)

    def has_file(self, rel, sha=None):
        """The proof runs with cwd = books (run_proof): a script it names must be a file there. With `sha`: a file of
        that commit (git cat-file), so a books tree that lags the build is not read as a missing script."""
        if sha is None:
            return os.path.isfile(os.path.join(self.books, rel))
        r = subprocess.run(["git", "cat-file", "-e", "%s:%s" % (sha, rel)], cwd=self.books, capture_output=True,
                           timeout=60, stdin=subprocess.DEVNULL)
        return r.returncode == 0

    def cited(self, item_id, sha):
        """-> the full shas of every non-merge commit up to and including `sha` whose subject names `item_id` (cites),
        newest first (build_shas). --grep reads the whole message; only the subject counts, so a body that merely
        mentions the item (a caused_by, a filing) adds nothing."""
        r = subprocess.run(["git", "log", "--no-merges", "-F", "--grep=%s" % item_id, "--format=%H%x09%s", sha],
                           cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git log %s: %s" % (sha, r.stderr))
        return [h for h, _, subj in (ln.partition("\t") for ln in r.stdout.splitlines()) if h and cites(subj, item_id)]


    def touched(self, sha):
        """Every path the built commit touched, including ones HEAD no longer has: changed_since sees those as changed."""
        return self._paths([], sha)

    def deleted(self, sha):
        """-> the paths the built commit DELETED: a stale game copy of one is still deployed and nothing else notices."""
        return self._paths(["--diff-filter=D"], sha)

    def _paths(self, extra, sha):
        """NUL-delimited, so a non-ASCII name is the real name and not git's quoted spelling. A merge is refused: its
        combined diff leaves out what only one parent changed."""
        r = subprocess.run(["git", "rev-list", "--parents", "-n", "1", sha], cwd=self.books, capture_output=True, text=True,
                           timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode or not r.stdout.strip():
            raise ValueError("git rev-list %s: %s" % (sha, r.stderr))
        if len(r.stdout.split()) > 2:
            raise ValueError("%s is a merge commit: its game files cannot be listed" % sha)
        r = subprocess.run(["git", "diff-tree", "-z", "--root", "--no-commit-id", "--name-only", "-r", *extra, sha],
                           cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff-tree %s: %s" % (sha, r.stderr))
        return [p for p in r.stdout.split("\0") if p.strip()]

    def deployable(self, tier, mod):
        """True when src/<tier>/<mod> is a mod the game loads: it has About/About.xml at HEAD."""
        r = subprocess.run(["git", "cat-file", "-e", "HEAD:src/%s/%s/About/About.xml" % (tier, mod)], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return r.returncode == 0

    def game_input(self, tier, mod, revs=()):
        """True when src/<tier>/<mod> can reach the game folder (reaches_game): it is a mod at HEAD or at any of `revs` (a
        build that deleted the whole mod, About.xml included, still deployed it), the compose manifest folds it in or
        builds its settings shell from it, or a .csproj in another folder compiles a file of it (_Shared/SettingsKit)."""
        if self.deployable(tier, mod):
            return True
        for rev in revs:
            r = subprocess.run(["git", "cat-file", "-e", "%s:src/%s/%s/About/About.xml" % (rev, tier, mod)],
                               cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            if r.returncode == 0:
                return True
        return mod in self.folded() or (tier, mod) in self.compose_inputs() or (tier, mod) in self.csproj_inputs()

    def compose_inputs(self):
        """{(tier, folder)} a compose manifest at HEAD names as a source: entries and the settings shell."""
        if getattr(self, "_compose_in", None) is None:
            out = set()
            for path in glob.glob(os.path.join(self.books, "src", "*", "*.compose.json")):
                tier = os.path.basename(os.path.dirname(path))
                try:
                    with open(path, encoding="utf-8") as f:
                        man = json.load(f)
                except (OSError, ValueError):
                    raise ValueError("compose manifest %s is unreadable: its inputs cannot be told" % path)
                out.update((tier, e.get("source")) for e in man.get("entries") or () if e.get("source"))
                if (man.get("shell") or {}).get("source"):
                    out.add((tier, man["shell"]["source"]))
            self._compose_in = out
        return self._compose_in

    def csproj_inputs(self):
        """{(tier, folder)} of every src/ folder a .csproj OUTSIDE it at HEAD names in an Include= or HintPath: that
        folder's files are compiled or copied into another folder's output (_Shared/ into each mod DLL)."""
        if getattr(self, "_csproj_in", None) is None:
            r = subprocess.run(["git", "ls-files", "-z", "--", "*.csproj"], cwd=self.books, capture_output=True,
                               text=True, timeout=60, stdin=subprocess.DEVNULL)
            if r.returncode:
                raise ValueError("git ls-files *.csproj: %s" % r.stderr)
            out = set()
            for proj in (x for x in r.stdout.split("\0") if x.strip()):
                own = SRC_MOD.match(proj)
                try:
                    with open(os.path.join(self.books, proj), encoding="utf-8", errors="replace") as f:
                        text = f.read()
                except OSError:
                    continue
                refs = re.findall(r"""Include\s*=\s*["']([^"']+)["']""", text) + re.findall(r"<HintPath>([^<]+)<", text)
                for ref in refs:
                    p = os.path.normpath(os.path.join(os.path.dirname(proj), ref.replace("\\", "/"))).replace(os.sep, "/")
                    m = SRC_MOD.match(p)
                    if m and (not own or own.group(1, 2) != m.group(1, 2)):
                        out.add(m.group(1, 2))
            self._csproj_in = out
        return self._csproj_in


    def changed_since(self, sha, paths):
        """-> [(path, newest commit touching it after sha)] for each path whose bytes differ from sha's."""
        r = subprocess.run(["git", "diff", "-z", "--name-only", sha, "HEAD", "--", *paths], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff %s: %s" % (sha, r.stderr))
        out = []
        for p in (x for x in r.stdout.split("\0") if x.strip()):
            c = subprocess.run(["git", "log", "-1", "--format=%h", "%s..HEAD" % sha, "--", p], cwd=self.books,
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            out.append((p, c.stdout.strip() or "?"))
        return out

    def shippable(self, rel):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return deploy_custom_mods.shippable(rel.replace("/", os.sep))


    def folded(self):
        """{source folder: (composed target, key)} from the compose manifest (deploy_custom_mods.folded)."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import deploy_custom_mods
        if getattr(self, "_folded", None) is None:      # one manifest read per run, not one per file
            self._folded = with_shell(deploy_custom_mods.folded(), compose_shells(deploy_custom_mods.SRC_ROOT))
        return self._folded




    def rimflow(self, *args, timeout=120):
        env = dict(os.environ, RIMFLOW_SEAT=self.seat, AGENT_SEAT=self.seat, CLAUDE_PROJECT_DIR=self.books,
                   **{model.BRIDGE_SEAT_ENV: model.RELENTLESS_HOLDER})
        return subprocess.run(["python3", os.path.join(HERE, "cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)





