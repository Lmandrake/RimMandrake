#!/usr/bin/env python3
"""relentless_live.py -- Relentless's live tier: one built item's live criterion, proved on the running game.

Owner ruling by card, 2026-11-02 (ledger note on PLANNING_BUILD_DAYS_OF_ORDERS_NO_HOME): "Relentless learns live testing
(Foundry stays paused, the 512 built items wait on that build)". Design relentless_agent_design_2026-11-01.md section 13
step 9: "A real live leaf closes through a testq or pilot receipt on the deployed hash".

    python3 src/RimMandrake/rimflow/relentless_live.py run --item ID --criterion A2 \\
        --proof "python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_Chittik=CompProperties_WoundLink" \\
        --deploy "--compose biomes --with SWBestiary"

ONE RUN, in this order. Every refusal before step 5 leaves the item untouched and the bridge where it was:
  1. the item is built or validated and still owes the criterion, at a live level (LIVE_LEVELS);
  2. not a flyer: a title, criterion or proof naming flight is refused (standing ruling: never live-test a flyer's flight);
  3. the build is deployed: deploy_custom_mods.py's plan (with --deploy's args) covers every mod the built commit changed,
     lists none of its game files as drift or held, and the running game started after the newest of them was written;
  3b. the running load holds the build's mods, its `live-mods:` and their dependencies, and a FINAL clause finds the
     full-list tier up; read BEFORE the bridge is taken, so a run this game cannot serve is a row with slot False and
     takes no slot (LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT);
  4. the bridge: `rimflow bridge take --idle-ok`; refused means busy, and nothing runs;
  4a. the health check (LIVE_VERDICT_BUILD_INFRA_NOT_FAIL), bridge held: Fx.health pings the bridge from python.exe and
     reads every game file the build changed against the built commit's bytes. A failure is the row's why, and the
     proof does not run;
  4b. the site (RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED): a `live-site <CID>: <cmd>` line in the item's
     live_proofs file is run first, bridge held. It may only be Utils/live_site.py (SITE_CMD), which makes the map the
     proof reads (a biome on the scratch quicktest tile) or loads a named save; exit non-0 is UNMEASURED "site not
     prepared", and the proof does not run. Before it, HORIZON_CARAVAN ran its Stillsand probe on a Leaning Scrub map
     eight times and LEANINGSCRUB_STALL_SHARED_MOVE_1 ran on the very biome its criteria exclude;
  5. the proof runs (exit 0 PASS, 1 FAIL, anything else or a timeout UNMEASURED) and the bridge is released (--mine)
     whatever happened, before anything is written to the ledger. A `python3 ...` proof that dies on the bridge's
     "cannot reach the bridge from WSL" (RimBridge binds Windows loopback) is rerun once under python.exe;
  6. PASS or FAIL is a `verify --criterion --level --sha <built sha>`, so a pass drops the criterion and a fail stands;
     UNMEASURED is a note, never a run. Every outcome, refusals too, is a row in <RELENTLESS_ROOT>/live/runs.jsonl.
     The same cause UNMEASURED `repeat_unmeasured` times running on one game is a RELOAD request, said once in the
     ledger: the row's why starts RELOAD, relentless_game restages on it, and the round skips it until the game changes.
     The repeats between are rows only (eight identical ledger notes in an hour was the old behaviour).
     A proof or site that KNOWS the running game is the wrong load says so itself: its last line `reload needed: ...`
     is the row's why at once (asked_reload), so the restage needs no repeats.
     THE CAP (PROOF_RERUNS_TAME_UNMEASURED_REPEATS): a proof that ran and measured nothing gets a `defect` row, terminal
     for its build, which relentless_game returns to a worker with the exit reason and the log. It takes one run when the
     proof's own call is broken (broken_call: no game changes a wrong call), one run per build when the same proof line
     gave the same cause on an earlier build (seen_on_other_build), two games otherwise (seen_on_other_game).

VERDICT. Every row also carries `verdict` (VERDICTS), set by construction: INFRA when the proof never started (a
refusal, a health check, a site, a harness error before the proof), and then no verify is written and relentless_game
charges no strike; once the proof started, exit 0 is PASS and anything else FAIL. INFRA rows that held the bridge on
`infra_games` games for one build end in a `harness` row: relentless_game._harness alarms and restages, never a strike.

Proofs here are the item's own read of the game. Nothing in this file changes the game; a proof that would restart it or
swap the mod list is refused (rules live.forbid_re): the running game is the owner's, and a load is another tier. The
one change allowed is the site step above, through one reviewed tool that refuses a game past two in-game days.
"""
import argparse
import calendar
import glob
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RULES = os.path.join(HERE, "relentless_rules.json")
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN", "GREEN-FULL")       # model.LEVEL_NEEDS says bridge; L3 is a judge, L4 a human
# PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02): "small mod lists should always be the way to test until a
# final verification pass on the whole huge mod list." Every live level but FINAL runs on any game that holds the item's
# mods and their dependencies; a FINAL clause is the full-list verification, run only when the full list is up.
FINAL = "GREEN-FULL"
FINAL_WAIT = "final verification waits for the full list"     # relentless_game reads this prefix: batch, never restage
FULL_LIST = os.path.join(BOOKS, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
FULL_TIER_SHARE = 0.5       # northstar_driver.preflight's: under half the full list running is another tier
TESTABLE = ("built", "validated")
PASS, FAIL = 0, 1
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
# LIVE_VERDICT_BUILD_INFRA_NOT_FAIL (design build_system_practices_2026-11-03.md top-5 #1): every row's `verdict`, set by
# construction in run's done(), never by a worker. INFRA: the proof never started (a refusal, the health check, the site,
# a harness exception before the proof); it charges no strike and writes no verify. Once the proof started, exit 0 is
# PASS and anything else FAIL: a mod can crash the game or the bridge, so nothing after that step is the harness's.
VERDICTS = ("PASS", "FAIL", "INFRA")
UNHEALTHY = "health check failed"       # the health step's why; never a DEFECT, it counts to infra_games instead
HARNESS = "harness fault"               # the row that ends an INFRA streak: relentless_game._harness, no strike


def verdict(row):
    """A runs.jsonl row -> PASS, FAIL or INFRA. A row written before the verdict existed keeps its outcome's meaning:
    FAIL was a proof exit 1, PASS an exit 0, the rest never a verdict on the mod."""
    if row.get("verdict") in VERDICTS:
        return row["verdict"]
    return row.get("outcome") if row.get("outcome") in ("PASS", "FAIL") else "INFRA"
RELOAD = "reload needed"        # relentless_game RESTAGE reads this prefix; the round skips it on the same game
STALE = "changed since the built commit"        # terminal for its build: no game can run it (relentless_live_round.due)
DEFECT = "proof or site defect"     # an UNMEASURED no rerun can change: terminal for its build, back to a worker
# Every DEFECT why ends "... cannot help: <the cause>", so cause() can read the cause back out of it.
DEFECT_HEAD = re.compile(r"^%s: .*? cannot help: " % DEFECT)
# A proof whose own call is wrong: no reload, site or rerun can change these, so one run is enough. The log's tail decides,
# and only for a proof that exited neither 0 nor 1. Every pattern is from a real row (2026-11-03, runs.jsonl): GRAFFITI_V1
# six clauses "No public static CleanRead with 0 params"; SETTLEMENT_VERBS six "Type not found" (a wrong name, or a mod its
# `live-mods:` line does not name: both the worker's); HEAVY_TEXTURES and TIDAL_LOCK a tool demanding the flag the live
# tier forbids (forbid_re), so it could never run. The rest are the shell and Python saying the same of a command line.
BROKEN_CALL = re.compile(
    r"No public static \S+ with \d+ params|Type not found:|--yes-i-know-this-is-live|can't open file|command not found"
    r"|: error: (?:unrecognized arguments|the following arguments are required|argument )"
    r"|\b(?:ModuleNotFoundError|ImportError|SyntaxError|NameError):")
# A last line that names no reason: the reason is on a line above it
NO_REASON = re.compile(r"^(?:\$ .*|(?:(?:VERDICT|LIVE|RESULT)\s*:?\s*)?UNMEASURED\.?)$")
# The readers above read the WHOLE log (live_observe.whole): an 8 KB tail dropped decisive rows above it (GPT 2026-11-04)
UNDEPLOYED = ("not deployed", "not in the running load")    # retried on another game only (relentless_live_round.due)
SITE_CMD = re.compile(r"^python\.exe src/RimMandrake/Utils/live_site\.py(?: --[a-z][a-z-]*(?: [A-Za-z0-9_.\-]+)?)+$")
# rimbridge_client.resolve_endpoint's refusal under WSL python3: the proof never reached the game
WSL_BRIDGE = ("cannot reach the bridge from WSL", "Re-run under Windows Python")
# LIVE_EXIT1_INABILITY_READ_AS_MOD_FAIL (owner 2026-11-03: "the checker was unable to measure something, and interpreted
# that as a wrong value rather than an inability that should have been reported up"). Exit 1 is a FAIL only when the
# proof asked and the answer missed the bar. A Python traceback also exits 1, and so did proofs that printed their own
# UNMEASURED; 14 items churned on such rows read as game_fail strikes. could_not_ask() reads the log's tail; every
# pattern is from a real FAIL row of 2026-11-02..04 (relentless/live/*.log).
# The box or the instrument failed: no proof or mod change helps (relentless_game._harness: alarm, restage later, no strike)
EXIT1_HARNESS = re.compile(
    r"cannot reach the bridge from WSL|IndeterminateError|No space left on device|\[Errno 28\]|Wsl/Service/"
    r"|object has no attribute 'sendall'|UtilAcceptVsock|BrokenPipeError|ConnectionResetError|ConnectionRefusedError|ConnectionAbortedError")
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
REPRO_MISS = "repro miss"
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
DRIFT = re.compile(r"^\s{2,6}([~+\-H])\s+(\S.*?)(?:\s{2,}\(.*\))?\s*$")
SECTION = re.compile(r"^(\S+)\s+(mandrake\.\S+)(.*)$")      # deploy_custom_mods prints one per mod, drift or not
COMPOSED = re.compile(r"^\s*compose\s+(\S+)\s+(mandrake\.\S+)\s.*->\s*(\S+)\s*$")


WINDOWS_DIRS = ("/mnt/c/WINDOWS/system32", "/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0")


def windows_path(path):
    """`path` plus the Windows tools a live read needs (powershell.exe finds the game, tasklist/netstat measure it,
    python.exe reaches the bridge). The systemd unit's PATH has none of them, so from the tick every game read was None
    ("no running game") while the game ran: ten game-phase items held on the owner for it
    (RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD)."""
    have = path.split(os.pathsep) if path else []
    extra = [d for d in WINDOWS_DIRS + tuple(sorted(glob.glob("/mnt/c/Users/*/AppData/Local/Microsoft/WindowsApps")))
             if d not in have and os.path.isdir(d)]
    return os.pathsep.join(have + extra)


def proof_budget(proof, default_s):
    """The harness limit for one proof: `default_s`, or its own `--max-seconds N` plus 120 s when that is longer (a proof that
    asks for 1800 s must not be killed at 600; GAMECOMP_STALL_HUNT_SEVEN_SECONDS A2 timed out twice). Pure."""
    m = re.search(r"--max-seconds[ =](\d+)", proof or "")
    return max(default_s, int(m.group(1)) + 120) if m else default_s


def live_rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- pure checks

sys.path.insert(0, HERE)
import model                                   # noqa: E402  the ledger's own cap and criterion line, not a copy
import live_observe                            # noqa: E402  the RMOBS measurement protocol; the regexes are its fallback

CUT_AT = model.CRITERION_TEXT_MAX
CRIT_LINE = model.CRITERION_LINE_RE


def whole_criterion(c, prose):
    """The ledger cuts a criterion's text at CUT_AT; the item's prose may hold the whole line. -> a copy with the
    whole text, or marked `cut` when the ledger copy is at the cap and no prose line extends it."""
    c, text = dict(c), c.get("text") or ""
    if len(text) < CUT_AT:
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
                "it until he acts (OPS_CHURN_DIAGNOSE_WATER_PPCC_FKGE); take the clause out of the game clauses "
                "(rebind) and wait on him: snag --class blocked_by_predecessor --blocker owner")
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


def refused_site(site):
    """-> why a live-site command may not run, or None. Only live_site.py, plain arguments: the site step is the one
    change this tier makes to the game, so it is one reviewed tool, never a free command."""
    if site and not SITE_CMD.match(site.strip()):
        return "the live-site command %r is not `python.exe src/RimMandrake/Utils/live_site.py <plain args>`" % site[:200]
    return None


def cause(why):
    """An UNMEASURED why -> the key two runs share when the same thing stopped them: no paths, numbers or times."""
    w = DEFECT_HEAD.sub("", why or "")      # the head would eat the whole cap, and every defect would read alike
    # a number with its unit attached is still a number ("mean=50.176ms" made every run its own cause)
    w = re.sub(r"\([^()]*\.log\)|/\S+|\b\d[\d:.TZ-]*[A-Za-z]*\b", "", w)
    return re.sub(r"\s+", " ", w).strip()[:120]


def repeats(rows, item_id, criterion, sha, key, game):
    """runs.jsonl rows -> how many of the newest rows for (item, criterion, sha), running back, are UNMEASURED on `key`
    on the same game. Any other outcome, cause or game ends the run."""
    n = 0
    for row in reversed(rows):
        if (row.get("item"), row.get("criterion"), row.get("sha")) != (item_id, criterion, sha):
            continue
        if row.get("outcome") != "UNMEASURED" or row.get("game") != game or (row.get("cause") or cause(row.get("why"))) != key:
            break
        n += 1
    return n


def seen_on_other_game(rows, item_id, criterion, sha, key, game):
    """-> the earlier game on which (item, criterion, sha) was already UNMEASURED on `key`, or None. A cause that outlives
    a reload is the proof's or the site's, not a stale game's (LIVE_EXIT2_FIX_DEFECT_AFTER_TWO_GAMES: 74 of 76
    `exited 2` rows were five criteria rerun every 17 min and reloaded every third run on one unchanging cause)."""
    for row in reversed(rows):
        if ((row.get("item"), row.get("criterion"), row.get("sha")) == (item_id, criterion, sha)
                and row.get("outcome") == "UNMEASURED" and row.get("game") and game and row["game"] != game
                and (row.get("cause") or cause(row.get("why"))) == key):
            return row["game"]
    return None


def seen_on_other_build(rows, item_id, criterion, sha, key, proof):
    """-> the earlier build on which this same proof line of (item, criterion) ended UNMEASURED on `key`, or None. A new
    build earns one run, and the same line saying the same again means the build did not reach what stopped it
    (PLANET_ATMOSPHERE_CLOUD_COST_1 said "rides a later load" on three builds running)."""
    for row in reversed(rows):
        other = row.get("sha") or ""
        if ((row.get("item"), row.get("criterion"), row.get("proof")) == (item_id, criterion, proof)
                and other and not other.startswith(sha) and not sha.startswith(other)
                and row.get("outcome") == "UNMEASURED" and (row.get("cause") or cause(row.get("why"))) == key):
            return other
    return None


def infra_games(rows, item_id, criterion, sha, game):
    """-> how many distinct games (this one included) held the bridge for (item, criterion, sha) and still ended INFRA
    (the health check or the site refused, a row carrying `health`), since its last PASS or FAIL. The design's cap:
    INFRA retries on the next healthy game at most twice, then it is a harness item. A row that took no slot (not in
    the running load, not deployed) is the game phase's to restage, never counted here."""
    seen = {game} if game else set()
    for row in reversed(rows):
        if (row.get("item"), row.get("criterion"), row.get("sha")) != (item_id, criterion, sha):
            continue
        if verdict(row) != "INFRA":
            break
        if row.get("outcome") == "UNMEASURED" and row.get("game") and "health" in row:
            seen.add(row["game"])
    return len(seen)


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


PROOFS = "infrastructure/state/live_proofs/"     # the build's proof lines; the ledger and lessons it touched are books
ASSEMBLY_OUT = re.compile(r"/Assemblies/[^/]+\.(?:dll|pdb)(?:\.srchash)?$")     # a compiled output, never a source


SOURCE_IN_MOD = re.compile(r"^Source/")
SCOPE_ALL = False       # selftest_relentless_carry_chain --pre-scope: the scope as before (every src/ path the build touched)


def carry_scope(fx, sha, paths):
    """The build's paths a carry must find unchanged -> [path]: its proofs (live_proofs/), and under src/<tier>/<Mod>/
    only what can reach the game: a folder that deploys or ships inside a mod (reaches_game), and inside it, a Source/
    file only when an assembly of the mod compiles it (listed in one of its .srchash files at `sha` or HEAD, or the
    project's own .csproj, fx.compiled). A mod with no .srchash keeps every Source/ path. A fake without those methods
    keeps every src/ path, as before.
    OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT, 5th bounce (2026-11-05 18:16Z): SUMP_TAR_FIRE_NETWORK_1's build shas include the
    supervisor fix 6cfce056d6 (its subject cites the item), so src/RimMandrake/rimflow/relentless_game.py read as a mod
    path and another item's later edit to it refused the carry; so did PLANK's edit to FlowWorks/Source/SelfTest/
    Program.cs, a separate net8 test project absent from the DLL's Compile list. Neither can reach the game."""
    out, memo = [], {}
    for p in dict.fromkeys(paths):
        if p.startswith(PROOFS):
            out.append(p)
            continue
        m = SRC_MOD.match(p)
        if not m:
            continue
        if SCOPE_ALL or not (hasattr(fx, "game_input") or hasattr(fx, "deployable")):
            out.append(p)
            continue
        if m.group(1, 2) not in memo:
            memo[m.group(1, 2)] = reaches_game(fx, m.group(1), m.group(2), (sha, sha + "^"))
        if not memo[m.group(1, 2)]:
            continue
        if SOURCE_IN_MOD.match(m.group(3)) and not ASSEMBLY_OUT.search(p):
            compiled = fx.compiled(m.group(1), m.group(2), sha)
            if compiled is not None and p not in compiled:
                continue
        out.append(p)
    return out


def carry(fx, sha, item_id=None):
    """-> (newer sha, why) when `sha` is stale only because another commit REBUILT a shared assembly the build ships, or
    None. Every later change to the build's paths is a compiled output (ASSEMBLY_OUT), and every other path the build
    touched under src/ or live_proofs/ (its sources, proofs, defs) holds the built bytes at HEAD: the newer commit's assembly was compiled from a tree
    holding the build's own sources unchanged, so the build is redeployed there, not rebuilt. Anything else, or a fake
    without `last_commit`, is None and the stale build goes back to a worker as before.
    OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT: SUMP_TAR_FIRE_NETWORK_1 (Judge PASS 7/7) went back twice as game_stale_build because
    SPREADING_FUEL_FIX_IRRIGATES_CROPS rebuilt RimMandrakeFlowWorks.dll 27 min after its candidate; that DLL took ~36
    commits in 72 h, so every FlowWorks item waiting over an hour for the game was sent to a worker who could change
    nothing."""
    if not hasattr(fx, "last_commit"):
        return None
    shas = build_shas(fx, sha, item_id)
    if any(fx.deleted(s) for s in shas):
        return None
    touched = carry_scope(fx, sha, (p for s in shas for p in fx.touched(s)))
    later = fx.changed_since(sha, touched) if touched else []
    if not later or any(not ASSEMBLY_OUT.search(p) for p, _ in later):
        return None
    new = fx.last_commit(sha, [p for p, _ in later])
    if not new or new.startswith(sha) or sha.startswith(new):
        return None
    try:
        again, _files = stale_build(fx, new)
    except ValueError:
        return None
    if again:
        return None
    return new, "only rebuilt assemblies changed since %s (%s); the build's own sources are unchanged at %s" % (
        sha[:12], ", ".join("%s (%s)" % pc for pc in later[:4]), new[:12])


def carry_blockers(fx, sha, item_id=None):
    """-> [(path, commit)]: the later changes on the build's paths that are NOT a compiled output, i.e. why carry()
    refused (empty when it would carry, or cannot say). Named in the game_stale_build detail so the worker learns what
    to re-verify. OPS_CHURN_DIAGNOSE_PIT_XGUR_QNTR: PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES went back on 2026-11-05 naming
    only the rebuilt RimMandrakeFlowWorks.dll (judged against the carried sha); the real cause, PLANK_COVER_REDRAW's edit
    of its own RM_PitLipOcclusion.cs (0bc4a2aac5), was nowhere in the return."""
    shas = build_shas(fx, sha, item_id)
    touched = carry_scope(fx, sha, (p for s in shas for p in fx.touched(s)))
    later = fx.changed_since(sha, touched) if touched else []
    return [(p, c) for p, c in later if not ASSEMBLY_OUT.search(p)]


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


def wsl_rerun(proof, log_text):
    """-> the proof under python.exe when it is a plain `python3 <script>` that died on the WSL bridge refusal, else None."""
    if proof.startswith("python3 ") and any(s in (log_text or "") for s in WSL_BRIDGE):
        return "python.exe " + proof[len("python3 "):]
    return None


def last_line(path):
    """The last non-blank line of a log, cut to 200, or "" when it cannot be read."""
    lines = [x.strip() for x in read_text(path).splitlines() if x.strip()]
    return lines[-1][:200] if lines else ""


def tail_lines(path):
    """The non-blank lines of a log: all of them (live_observe.whole cuts only past its LOG_MAX)."""
    return [x.strip() for x in live_observe.whole(read_text(path))[0].splitlines() if x.strip()]


def exit_reason(path):
    """-> the line of a proof's log that says why it stopped: the last one naming a reason, cut to 200. "VERDICT
    UNMEASURED" as the last line told the worker nothing and made every cause on that proof the same key."""
    lines = tail_lines(path)
    for line in reversed(lines):
        if not NO_REASON.match(line):
            return line[:200]
    return lines[-1][:200] if lines else ""


def last_verdict(path):
    """-> the proof log's last verdict-shaped line (VERDICT_LINE, or a `T1 FAIL ...` row), else its exit reason, cut to
    200; "" when the log cannot be read. A game_fail's detail carries it beside the log path
    (RELENTLESS_DIAGNOSE_REPRO_MISS_AS_GAME_FAIL: across 9 items the bare "A1 FAIL on the running game (<log>)" hid 9
    different causes)."""
    if not path:
        return ""
    lines = tail_lines(path)
    for line in reversed(lines):
        if VERDICT_LINE.match(line) or FAIL_ROW.match(line):
            return line[:200]
    return exit_reason(path)


def broken_call(path):
    """-> the log line showing the proof's own call is wrong (BROKEN_CALL), or None."""
    for line in reversed(tail_lines(path)):
        if BROKEN_CALL.search(line):
            return line[:200]
    return None


def could_not_ask(path):
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
    if any(MOD_ROW.match(x) for x in lines):
        return None             # an observed violation is never erased, whatever else the run tripped over
    for kind, rx in (("harness", EXIT1_HARNESS), ("reload", EXIT1_RELOAD)):
        for line in reversed(lines):
            if marker_hit(rx, line):
                return kind, line[:200]
    for line in reversed(lines):
        if marker_hit(EXIT1_UNLOADED, line):
            return "reload", line[:200]
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
                               "instrument)" % ends[-1])[:200]
    if verdicts and verdicts[-1][1] in REPRO_MISS_VERDICTS:
        return "miss", lines[at].strip()[:200]
    if verdicts and all(v == "UNMEASURED" for _, v in verdicts):
        return "dud", lines[at].strip()[:200]
    for line in reversed(lines):
        if read_nothing(line):
            return "unknown", ("UNKNOWN: a None or zero-row read (a measured absence or a blind instrument; RMOBS "
                               "absence says which): %s" % line)[:200]
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


def read_rows(path):
    """runs.jsonl -> its rows; a torn line is skipped."""
    out = []
    for line in read_text(path).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def game_iso(fx):
    """The running game's start as the row's `game` key, or None when it cannot be read."""
    try:
        t = fx.game_started()
    except Exception:       # noqa: BLE001  a fake or a failing read: the key is only a grouping
        return None
    return iso(t) if t else None


def refused_deploy(deploy):
    """-> why the --deploy arguments may not run before the bridge is held, or None. They are a PLAN: anything that writes
    the game folder is another tier."""
    m = re.search(r"(^|\s)(--apply|--pull|--yes\S*|--force\S*)(\s|=|$)", re.sub(r"[\'\"\\]", "", deploy or ""))
    return "--deploy %r would write the game folder (%s): the plan only reads" % (deploy, m.group(2)) if m else None


def game_files(paths, shippable):
    """The built commit's paths that ship to the game -> [(mod folder, path in the mod)]."""
    out = []
    for p in paths:
        m = SRC_MOD.match(p)
        if m and shippable(m.group(3)):
            out.append((m.group(2), m.group(3)))
    return out


def plan_sections(text):
    """deploy_custom_mods.py's plan -> ({mod folder it covers}, [(section folder, flag, entry)] drifting or held,
    {section folder: why it is not live}: a header flagged NOT DEPLOYED or not enabled)."""
    covered, drift, section, off = set(), [], None, {}
    for line in text.splitlines():
        c = COMPOSED.match(line)
        if c:
            covered.add(c.group(1))
            continue
        s = SECTION.match(line)
        if s:
            section = s.group(1)
            covered.add(section)
            for flag in ("NOT DEPLOYED", "not enabled in ModsConfig"):
                if flag in s.group(3):
                    off[section] = flag
            continue
        d = DRIFT.match(line)
        if d and section:
            drift.append((section, d.group(1), d.group(2)))
    return covered, drift, off


def folded_key(folded, mod):
    """A source folder's name in the game folder and in a compose plan: its compose key when a manifest folds it in
    (Scarlands -> Warscar), else itself. folded: deploy_custom_mods.folded(), {source: (target, key)}."""
    return ((folded or {}).get(mod) or (None, mod))[1]


def deploy_gap(files, plan_rc, plan_text, trees=(), folded=None):
    """-> why the built commit's game files are not what the game folder holds, or None.
    folded: {source folder: (composed target, key)}; a compose plan prints the KEY, so a folded source is matched by it
    (LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: 16 runs 'does not cover Scarlands' on a plan that composed Warscar).
    trees: mod folders whose WHOLE tree the build owes the game (a `live-deploy:` line: RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY,
    a deploy item commits no mod file). Any file the deploy would write counts, not only .xml and .dll; a `-` line does not
    (--apply leaves a file the repo lacks alone without --prune, so no staging could ever clear it) nor an H (held on purpose)."""
    # a plan exits 1 when ANY mod drifts; that plan is still read, the drift that matters is this commit's files
    drift_only = plan_rc == 1 and plan_text.rstrip().endswith("Drift found. Re-run with --apply to deploy.")
    if plan_rc != 0 and not drift_only:
        return "the deploy plan failed (exit %s): %s" % (plan_rc, plan_text[-300:])
    if "def guard" in plan_text and "REFUSED" in plan_text:
        return "the deploy plan refused: %s" % plan_text[-300:]
    covered, drift, off = plan_sections(plan_text)
    named = {folded_key(folded, m): m for m in [m for m, _ in files] + list(trees)}
    files = [(folded_key(folded, m), rel) for m, rel in files]
    trees = [folded_key(folded, m) for m in trees]
    if off:
        return "the plan says %s" % "; ".join("%s: %s" % kv for kv in sorted(off.items()))
    missing = sorted(named[m] for m in ({mod for mod, _ in files} | set(trees)) - covered)
    if missing:
        return "the deploy plan does not cover %s: name it in --deploy" % ", ".join(missing)
    for mod, rel in files:
        for section, flag, entry in drift:
            if (section == mod and entry == rel) or entry.endswith("/%s/%s" % (mod, rel)) or entry == "%s/%s" % (mod, rel):
                return "%s/%s is %s in the game folder (%s): the build is not what the game holds" % (
                    named.get(mod, mod), rel, "held" if flag == "H" else "out of date", section)
    for mod in sorted({m for m, _ in files}):      # a file this commit did not touch, in a mod it ships, may be the one it needs
        for section, flag, entry in drift:      # an untouched H file is held out of the game on purpose (DEPLOY_HOLD.txt)
            if flag != "H" and entry.lower().endswith((".xml", ".dll")) and (section == mod or entry.startswith(mod + "/")
                                                              or ("/%s/" % mod) in entry):
                return "%s has %s drift in the game folder (%s %s): the build is not what the game holds" % (
                    named.get(mod, mod), "held" if flag == "H" else "out-of-date", section, entry)
    for mod in sorted(set(trees)):
        for section, flag, entry in drift:
            if flag in "~+" and (section == mod or entry.startswith(mod + "/") or ("/%s/" % mod) in entry):
                return "%s has drift in the game folder (%s %s): the live-deploy tree is not what the game holds" % (
                    named.get(mod, mod), section, entry)
    return None


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
        import relentless_names     # the one resolver (LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING); it caches no blind read
        if not relentless_names.default_index().is_folder(name):
            return True
        _FOLDER_SEEN[name] = True
    return not _FOLDER_SEEN[name]


def folded_dirs(mods_dir, mod, folded=None):
    """The game-folder dirs a folded source loads from: Mods/<target>/Biomes/<key> or Mods/<target>/Biomes/_Kits/<key>
    (biomes_compose.dest_rel); [] when the manifest does not fold it."""
    if mod not in (folded or {}):
        return []
    target, key = folded[mod]
    return [os.path.join(mods_dir, target, "Biomes", key), os.path.join(mods_dir, target, "Biomes", "_Kits", key)]


def deployed_paths(mods_dir, mod, rel, folded=None):
    """Where a mod file sits in the game folder: Mods/<Mod>/<rel>, inside a composed mod Mods/*/*/<Mod>/<rel>, or for a
    folded source under its compose key, engine kits one level deeper (folded_dirs)."""
    got = [os.path.join(mods_dir, mod, rel)] + glob.glob(os.path.join(glob.escape(mods_dir), "*", "*", glob.escape(mod),
                                                                      glob.escape(rel)))
    got += [os.path.join(d, rel) for d in folded_dirs(mods_dir, mod, folded)]
    return [p for p in dict.fromkeys(got) if os.path.isfile(p)]


# ---------------------------------------------------------------- the one run

class Fx(object):
    """Everything that touches the world. The selftest swaps it."""

    def __init__(self, books=BOOKS, seat="BENCH", mods_dir=GAME_MODS):
        self.books, self.seat, self.mods_dir = books, seat, mods_dir

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
        """The item's prose, then its live_proofs/<ID>.criteria: the game mode adds its clauses to the ledger from that
        file (`rimflow implemented`), which cuts them at CUT_AT; the file still holds each whole line. Without it every
        long game clause read as cut and each round was REFUSED before the bridge (RELENTLESS_LIVE_REPAIR_QUITS_BEFORE_THE_LOAD)."""
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

    def cited(self, item_id, sha):
        """-> the full shas of every non-merge commit up to and including `sha` whose subject names `item_id` (cites),
        newest first (build_shas). --grep reads the whole message; only the subject counts, so a body that merely
        mentions the item (a caused_by, a filing) adds nothing."""
        r = subprocess.run(["git", "log", "--no-merges", "-F", "--grep=%s" % item_id, "--format=%H%x09%s", sha],
                           cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git log %s: %s" % (sha, r.stderr[-200:]))
        return [h for h, _, subj in (ln.partition("\t") for ln in r.stdout.splitlines()) if h and cites(subj, item_id)]

    def last_commit(self, sha, paths):
        """-> the full sha of the newest commit after `sha` touching any of `paths`, or None."""
        r = subprocess.run(["git", "log", "-1", "--format=%H", "%s..HEAD" % sha, "--", *paths], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return (r.stdout.strip() or None) if r.returncode == 0 else None

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
            raise ValueError("git rev-list %s: %s" % (sha, r.stderr[-200:]))
        if len(r.stdout.split()) > 2:
            raise ValueError("%s is a merge commit: its game files cannot be listed" % sha)
        r = subprocess.run(["git", "diff-tree", "-z", "--root", "--no-commit-id", "--name-only", "-r", *extra, sha],
                           cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff-tree %s: %s" % (sha, r.stderr[-200:]))
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
                raise ValueError("git ls-files *.csproj: %s" % r.stderr[-200:])
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

    def compiled(self, tier, mod, sha):
        """-> {repo path} of every source an assembly of the mod is built from: each Assemblies/*.srchash at `sha` and at
        HEAD lists `<hash> <path under its project dir>` after a `# project: <tier>/<mod>/.../X.csproj` line; the project
        file itself counts. None when the mod has no .srchash (nothing measured: keep every source)."""
        out, seen = set(), False
        for rev in (sha, "HEAD"):
            r = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", rev, "--", "src/%s/%s/Assemblies/" % (tier, mod)],
                               cwd=self.books, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            for f in (x for x in r.stdout.split("\0") if x.endswith(".srchash")):
                t = subprocess.run(["git", "show", "%s:%s" % (rev, f)], cwd=self.books, capture_output=True, text=True,
                                   timeout=60, stdin=subprocess.DEVNULL)
                if t.returncode:
                    continue
                seen, base = True, None
                for ln in t.stdout.splitlines():
                    if ln.startswith("# project:"):
                        proj = "src/" + ln.split(":", 1)[1].strip()
                        out.add(proj)
                        base = proj.rsplit("/", 1)[0] + "/"
                    elif base and not ln.startswith("#") and " " in ln.strip():
                        out.add(base + ln.strip().split(" ", 1)[1].strip())
        return out if seen else None

    def changed_since(self, sha, paths):
        """-> [(path, newest commit touching it after sha)] for each path whose bytes differ from sha's."""
        r = subprocess.run(["git", "diff", "-z", "--name-only", sha, "HEAD", "--", *paths], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        if r.returncode:
            raise ValueError("git diff %s: %s" % (sha, r.stderr[-200:]))
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

    def deploy_plan(self, args, timeout):
        try:
            r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/deploy_custom_mods.py"),
                                *shlex.split(args)], cwd=self.books, capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "the deploy plan took over %ds" % timeout
        return r.returncode, r.stdout + r.stderr

    def folded(self):
        """{source folder: (composed target, key)} from the compose manifest (deploy_custom_mods.folded)."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import deploy_custom_mods
        if getattr(self, "_folded", None) is None:      # one manifest read per run, not one per file
            self._folded = deploy_custom_mods.folded()
        return self._folded

    def mtime(self, mod, rel):
        got = deployed_paths(self.mods_dir, mod, rel, self.folded())
        return max(os.path.getmtime(p) for p in got) if got else None

    def game_started(self):
        """The running RimWorld's start, epoch seconds; None when none runs or it cannot be read."""
        try:
            r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                "Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | ForEach-Object "
                                "{ $_.StartTime.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }"],
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, PATH=windows_path(os.environ.get("PATH", ""))))
            lines = [x.strip() for x in r.stdout.splitlines() if x.strip()]
            if len(lines) != 1:      # two games: the bridge may answer from either, so neither start time is the answer's
                return None
            return calendar.timegm(time.strptime(lines[0], "%Y-%m-%dT%H:%M:%SZ"))
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None

    def rimflow(self, *args, timeout=120):
        env = dict(os.environ, RIMFLOW_SEAT=self.seat, AGENT_SEAT=self.seat, CLAUDE_PROJECT_DIR=self.books,
                   **{model.BRIDGE_SEAT_ENV: model.RELENTLESS_HOLDER})
        return subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/rimflow/cli.py"), *args],
                              cwd=self.books, env=env, capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    def running_load_gap(self, mods):
        """None when the RUNNING load holds every mod folder in `mods` (its packageId read from the deployed About.xml,
        checked against jawa/running_mods: the running load's own list, never ModsConfig.xml, which names the NEXT load);
        else why not. Asked before the bridge is taken (run): a change of game after it is caught by run's
        game-start check once the bridge is held."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import live_def_check
        want, folded = {}, self.folded()
        # a dotted folder in THIS Fx's game folder is a folder too, whatever the machine's Mods folder holds
        pkg = {m for m in mods if is_package(m) and not os.path.isfile(os.path.join(self.mods_dir, m, "About", "About.xml"))}
        pkgs = sorted({m.lower() for m in pkg})     # a workshop mod, never a dotted folder of ours
        if pkgs:
            import modset_builder
            closure, missing = modset_builder.package_closure(pkgs)
            if missing:
                return ("not in the running load: %s installed in neither the Steam workshop folder nor the game's Mods "
                        "folder" % ", ".join(missing[:5]))
            for p in closure:
                want.setdefault(p if p in pkgs else "%s needs %s" % ("+".join(pkgs), p), p)
        for mod in sorted(set(m for m in mods if m not in pkg)):
            text = ""
            # a folder folded into a composed mod (Stillsand -> RimMandrake.Biomes/Biomes/Stillsand) loads under the
            # composed mod's About.xml; its own folder is absent from the game (LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING)
            for about in [os.path.join(self.mods_dir, mod, "About", "About.xml")] + sorted(
                    os.path.join(os.path.dirname(os.path.dirname(d)), "About", "About.xml") for d in
                    glob.glob(os.path.join(glob.escape(self.mods_dir), "*", "*", glob.escape(mod))) if os.path.isdir(d)) + [
                    # a folded source loads under its compose key, kits under Biomes/_Kits (Scarlands, CreatureBehaviors)
                    os.path.join(self.mods_dir, folded[mod][0], "About", "About.xml") for _ in [0]
                    if any(os.path.isdir(d) for d in folded_dirs(self.mods_dir, mod, folded))]:
                try:
                    with open(about, encoding="utf-8-sig") as f:
                        text = f.read()
                    break
                except OSError:
                    continue
            m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", text, re.I)
            if not m:
                return "not in the running load: %s has no readable packageId in its deployed About.xml" % mod
            want[mod] = m.group(1).lower()
            deps = re.search(r"<modDependencies>(.*?)</modDependencies>", text, re.S | re.I)   # its dependencies too
            for d in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", deps.group(1) if deps else "", re.I):
                want.setdefault("%s needs %s" % (mod, d.lower()), d.lower())
        running = live_def_check.call_running_mods(60)
        if running is None:
            return "the running load's mod list could not be read (jawa/running_mods)"
        lost = ["%s (%s)" % (m, p) for m, p in sorted(want.items()) if p not in running]
        return ("not in the running load: %s" % ", ".join(lost[:5])) if lost else None

    def full_list_gap(self):
        """None when the RUNNING load is the full-list tier (at least FULL_TIER_SHARE of FULL.LATEST's ids running); else
        why not, starting FINAL_WAIT. Whether it EQUALS the list is the final proof's own question, never this gate's."""
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import live_def_check
        import modmanifest
        try:
            full = [i.lower() for i in modmanifest.read_modsconfig(FULL_LIST)]
        except Exception as e:      # noqa: BLE001  an unread list is no reason to call the game the full list
            return "%s: %s unreadable (%s)" % (FINAL_WAIT, os.path.basename(FULL_LIST), e)
        running = live_def_check.call_running_mods(60)
        if running is None:
            return "the running load's mod list could not be read (jawa/running_mods)"
        held = sum(1 for i in full if i in running)
        if held < FULL_TIER_SHARE * len(full):
            return "%s: the running game has %d mods, %d of FULL.LATEST's %d" % (FINAL_WAIT, len(running), held, len(full))
        return None

    def health(self, files, sha, timeout):
        """The health check before a proof, bridge held (LIVE_VERDICT_BUILD_INFRA_NOT_FAIL) -> {"why": None or why the
        game cannot judge the build, "ping": ..., "hashed": n, "unhashed": n}. Two reads, each one the proof depends on:
          1. the bridge answers rimbridge/ping from python.exe: RimBridge binds Windows loopback, so python.exe is the one
             interpreter on this host that drives it (a `python3` proof reaches it through python.exe, or reruns under it);
          2. every game file the built commit changed holds the built commit's bytes. A direct copy (Mods/<Mod>/<rel>)
             must match; a composed copy (Mods/*/*/<Mod>/<rel>) may be rewritten by biomes_compose (MayRequire), so one
             that differs is counted `unhashed`, never a failure (run's mtime check still covers it)."""
        import hashlib
        out = {"why": None, "hashed": 0, "unhashed": 0}
        client = os.path.join(os.path.dirname(HERE), "Utils", "rimbridge_client.py")
        try:
            path = subprocess.run(["wslpath", "-w", client], capture_output=True, text=True, timeout=20).stdout.strip()
            r = subprocess.run(["python.exe", path or client, "--timeout", str(min(timeout, 60)), "--call", "rimbridge/ping"],
                               capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
                               env=dict(os.environ, PATH=windows_path(os.environ.get("PATH", ""))))
            out["ping"] = r.returncode
            if r.returncode:
                out["why"] = "the bridge does not answer rimbridge/ping from python.exe (exit %d): %s" % (
                    r.returncode, (r.stderr or r.stdout).strip()[-200:])
                return out
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            out["ping"], out["why"] = None, "the bridge ping from python.exe did not finish: %s" % str(e)[:200]
            return out
        src = os.path.join(self.books, "src")
        tiers = sorted(d for d in os.listdir(src) if d.startswith("Rim") and os.path.isdir(os.path.join(src, d)))
        for mod, rel in files:
            blob = None
            for t in tiers:
                g = subprocess.run(["git", "cat-file", "blob", "%s:src/%s/%s/%s" % (sha, t, mod, rel)], cwd=self.books,
                                   capture_output=True, timeout=60, stdin=subprocess.DEVNULL)
                if g.returncode == 0:
                    blob = hashlib.sha256(g.stdout).hexdigest()
                    break
            if blob is None:
                out["why"] = "%s/%s: the built commit %s has no such file under src/<tier>/" % (mod, rel, sha)
                return out
            direct = os.path.join(self.mods_dir, mod, rel)
            copies = deployed_paths(self.mods_dir, mod, rel, self.folded())
            digests = {}
            for c in copies:
                with open(c, "rb") as f:
                    digests[c] = hashlib.sha256(f.read()).hexdigest()
            if direct in digests and digests[direct] != blob:
                out["why"] = "%s: %s/%s in the game folder is not the built commit's bytes (sha256 %s, built %s)" % (
                    UNDEPLOYED[0], mod, rel, digests[direct][:12], blob[:12])
                return out
            if blob in digests.values():
                out["hashed"] += 1
            else:
                out["unhashed"] += 1
        return out

    def run_proof(self, proof, log, timeout):
        """-> the proof's exit code, or None when it outran `timeout`. Output goes to `log`."""
        with open(log, "w", encoding="utf-8") as f:
            f.write("$ %s\n" % proof)
            f.flush()
            p = subprocess.Popen(proof, shell=True, cwd=self.books, stdout=f, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, executable="/bin/bash", start_new_session=True,
                                 env=dict(model.bridge_holder.process_env(),
                                          **{live_observe.RUN_ENV: live_observe.run_id_of(log)}))
            try:
                return p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                f.write("\nTIMEOUT after %ds\n" % timeout)
                p.kill()
                p.wait()
                return None
            finally:
                try:
                    os.killpg(p.pid, signal.SIGKILL)       # the whole group, exit or timeout: no probe child outlives the release
                except OSError:
                    pass


def run(fx, root, item_id, criterion, proof, deploy, r, now=None, needs=(), site=None, trees=(), env=None):
    """-> the run's row (also appended to <root>/live/runs.jsonl). row["outcome"] is PASS, FAIL, UNMEASURED or REFUSED.
    needs: mod folders the proof declares (live_proofs `live-mods:`) beyond the ones the built commit changed; with
    those, each one's About.xml modDependencies must be in the RUNNING load, or the row is UNMEASURED (restage), never
    run. A FINAL (GREEN-FULL) criterion also needs the full-list tier up: else UNMEASURED FINAL_WAIT, never run.
    site: the item's `live-site` command for this criterion (refused_site), run with the bridge held before the proof.
    trees: mod folders of a `live-deploy:` line: a drifting tree is UNMEASURED "not deployed" (the game phase stages, whose
    worker applies it), never a run; `deploy` must cover them. It says what the folder holds, not when: unlike `files`, no
    per-file stamp proves the running game started after that deploy; the staging's restart is what loads it."""
    now = time.time() if now is None else now
    lr = live_rules(r)
    row = {"at": iso(now), "item": item_id, "criterion": criterion, "proof": proof, "deploy": deploy}
    if env is not None:     # the effective mod list and every inferred addition with its evidence (LIVE_NEEDS_ENFORCE_...)
        row["env"] = env
    os.makedirs(os.path.join(root, "live"), exist_ok=True)

    def done(outcome, why, **kw):
        row.update(kw, outcome=outcome, why=why)
        row["verdict"] = ("INFRA" if "proof_exit" not in row else "FAIL" if row.get("observe", {}).get("status") ==
                          "VIOLATED" else "PASS" if row["proof_exit"] == PASS else "FAIL")
        if outcome == "UNMEASURED" and "game" not in row and why.startswith(UNDEPLOYED):
            row["game"] = game_iso(fx)      # relentless_live_round.due retries an undeployed build on another game only
        with open(os.path.join(root, "live", "runs.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    try:
        item = fx.item(item_id)
        if item and item.get("built_sha"):
            # LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: a refusal row with no sha was never terminal on its build
            # (relentless_live_round.history keys by sha), so 95 of 263 runs re-refused one cut criterion every round
            row["sha"] = item["built_sha"]
            if (({c["id"]: c for c in item.get("criteria") or []}.get(criterion) or {}).get("cut")):
                row["cut"] = True       # stands until the criterion reads whole (relentless_live_round.candidates)
        level, text = owed(item, criterion)
    except ValueError as e:
        return done("REFUSED", str(e))
    sha = item["built_sha"]
    row.update(sha=sha, level=level)
    why = refused_proof(lr, item["title"], text, proof)
    if why:
        return done("REFUSED", why)
    why = refused_deploy(deploy) or refused_site(site)
    if why:
        return done("REFUSED", why)
    if site:
        row["site"] = site
    try:
        why, files = stale_build(fx, sha, item_id)
    except ValueError as e:
        return done("UNMEASURED", "cannot read the built commit: %s" % e)
    if why:
        return done("UNMEASURED", why)
    if files or trees:
        rc, plan = fx.deploy_plan(deploy or "", lr["plan_max_s"])
        why = deploy_gap(files, rc, plan, trees, getattr(fx, "folded", dict)())
        if why:     # a plan that failed or timed out is the harness's: it may pass in a minute, so no game stamp
            return done("UNMEASURED", "not deployed: %s" % why, **({"game": None} if rc != 0 else {}))
    if files:
        stamps = [fx.mtime(mod, rel) for mod, rel in files]
        if None in stamps:
            lost = [("%s/%s" % f) for f, t in zip(files, stamps) if t is None]
            return done("UNMEASURED", "not deployed: no game copy of %s" % ", ".join(lost[:5]))
        started = fx.game_started()
        if started is None:
            return done("UNMEASURED", "no running game to test")
        if started <= max(stamps):
            return done("UNMEASURED", "the game started %s, before the build's files were deployed %s: it runs the old "
                                      "build" % (iso(started), iso(max(stamps))))
        row.update(game_started=iso(started), deployed=iso(max(stamps)), files=len(files))
    else:
        stamps, started = [], None
    # The build is deployed and older than the game, but the running list may not load its mod (or a mod it declares,
    # or their dependencies) at all (owner 2026-11-02: a game fits an item by its RUNNING mods, not ModsConfig); a FINAL
    # clause also needs the full-list tier. Read BEFORE the bridge is taken, one read each: a run the running game cannot
    # serve takes no slot (LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: 18:00-18:16Z 2026-11-03 GRAFFITI F1/F2 took the bridge
    # four times to read "48 mods, 40 of FULL.LATEST's 316"). row["slot"] False: no bridge, no proof, no game time.
    need = sorted({m for m, _ in files} | set(needs))
    try:
        gap = (fx.running_load_gap(need) if need else None) or (fx.full_list_gap() if level == FINAL else None)
    except Exception as e:                          # noqa: BLE001  an unread list is the harness's, never a verdict
        gap = "the running load's mod list could not be read: %s: %s" % (type(e).__name__, str(e)[:200])
    log, code, crashed = None, None, gap
    if gap:
        row["slot"] = False
    else:
        took = fx.rimflow("bridge", "take", "--idle-ok", "--for",
                          "relentless live test: %s %s (%s), read-only proof" % (item_id, criterion, level))
        if took.returncode != 0:
            return done("UNMEASURED", "bridge not taken: %s" % (took.stderr or took.stdout).strip()[-300:])
        log, n = None, 0
        while log is None or os.path.exists(log):  # a retry in the same second must not overwrite the last evidence
            log = os.path.join(root, "live", "%s-%s-%s%s.log" % (item_id, criterion, time.strftime(
                "%Y%m%dT%H%M%SZ", time.gmtime(now)), "" if not n else "-%d" % n))
            n += 1
        crashed = None
        try:
            if files and (started != fx.game_started() or stamps != [fx.mtime(m, rel) for m, rel in files]):
                crashed = "the game or its deployed files changed while the bridge was being taken"
            if crashed is None:     # bridge held, nothing spent yet: is the game fit to judge the mod at all?
                try:
                    h = fx.health(files, sha, lr["health_max_s"]) or {}
                except Exception as e:      # noqa: BLE001  a health check that cannot run is no health
                    h = {"why": "the health check could not run: %s: %s" % (type(e).__name__, str(e)[:200])}
                row["health"] = {k: v for k, v in h.items() if k != "why"}
                row["health"]["ok"] = not h.get("why")
                if h.get("why"):
                    crashed = h["why"] if h["why"].startswith(UNDEPLOYED) else "%s: %s" % (UNHEALTHY, h["why"])
            if crashed is None and code is None and site:
                slog = log[:-len(".log")] + "-site.log"
                row["site_log"] = slog
                sc = fx.run_proof(site, slog, lr["site_max_s"])
                if sc != 0:
                    crashed = asked_reload(slog) or "site not prepared: %s" % (
                        last_line(slog) or ("timed out" if sc is None else "exit %d" % sc))
            if crashed is None and code is None:
                row["proof_exit"] = None        # the proof starts: from here every outcome is the mod's (verdict)
                code = fx.run_proof(proof, log, proof_budget(proof, lr["proof_max_s"]))
                row["proof_exit"] = code
                again = wsl_rerun(proof, read_text(log)) if code != PASS else None     # a WSL traceback exits 1
                if again:
                    os.replace(log, log[:-len(".log")] + "-wsl.log")
                    row["rerun"] = again
                    code = fx.run_proof(again, log, proof_budget(again, lr["proof_max_s"]))
                    row["proof_exit"] = code
                if code in (PASS, FAIL) and files and (started != fx.game_started()
                                                       or stamps != [fx.mtime(m, rel) for m, rel in files]):
                    crashed, code = "the game or its deployed files changed while the proof ran", None
        except Exception as e:                          # the proof never ran to an exit code: no verdict, but the row stands
            crashed, code = "the proof could not run: %s: %s" % (type(e).__name__, str(e)[:200]), None
        finally:
            try:
                gave = fx.rimflow("bridge", "release", "--mine")
                row["released"], gave_why = gave.returncode == 0, (gave.stderr or gave.stdout).strip()[-200:]
            except Exception as e:                      # a timed-out release still leaves the row
                row["released"], gave_why = False, "%s: %s" % (type(e).__name__, str(e)[:150])
        if not row["released"]:
            return done("UNMEASURED", "the bridge release failed (%s), so no verdict is written" % gave_why, log=log)
    reading = live_observe.read_log(log, live_observe.run_id_of(log), criterion) if log and not crashed and (
        "proof_exit" in row) else None
    said, unable = None, None
    if reading is not None and reading.status != live_observe.NONE:
        # the proof said what it measured (RMOBS): its rows decide, never its exit code or a verdict-shaped line
        row["observe"] = reading.summary()
        ended = "timed out" if code is None else "exited %d" % code
        if reading.status == "VIOLATED":
            code = FAIL         # a valid violation stands over an exit 0, a later PASS line or a malformed row
        elif reading.status == "SATISFIED" and code == PASS:
            pass
        else:
            st = reading.status if reading.status != "SATISFIED" else live_observe.INVALID
            why = reading.why if reading.status != "SATISFIED" else "every row SATISFIED but the proof %s" % ended
            if st == "UNREACHED" and reading.stage in live_observe.HARNESS_STAGES:
                unable = ("harness", "%s: %s" % (st, why))
                said = "%s: the proof %s and could not ask: %s: %s" % (HARNESS, ended, st, why)
            else:
                unable = ("dud" if st == "UNREACHED" else "unknown", "%s: %s" % (st, why))
                said = "the proof %s: it did not measure: %s: %s" % (ended, st, why)
    elif code == FAIL and not crashed:
        unable = could_not_ask(log)
    if unable:
        row["unable"] = unable[0]
    if unable and said is None:      # LIVE_EXIT1_INABILITY_READ_AS_MOD_FAIL: an exit 1 that could not ask is no FAIL and no verify
        said = {"harness": "%s: the proof exited 1 and could not ask: %%s" % HARNESS,
                "reload": "%s: the proof exited 1 on a load it cannot judge: %%s" % RELOAD,
                "dud": "the proof exited 1: it did not measure: %s",
                "unknown": "the proof exited 1: it did not measure: %s",
            "miss": "%s"}[unable[0]] % unable[1]
    if unable and unable[0] == "miss" and not crashed:
        # an answer from the site the proof asked for: no verify (the defect neither held nor failed), no reload, no
        # defect. The round may run it again; relentless_game holds the item after repro_miss_limit of these
        why = "%s: the defect-repro proof ran on its site and did not reproduce the defect: %s" % (REPRO_MISS, unable[1])
        game = iso(started) if started else game_iso(fx)
        note = fx.rimflow("note", item_id, "--text", ("relentless live %s %s %s (%s)" % (criterion, level, why, log))[:400],
                          "--why", "relentless live tier: a repro miss, no verdict recorded")
        return done("UNMEASURED", why, log=log, game=game, miss=True, noted=note.returncode == 0)
    if code not in (PASS, FAIL) or unable:
        why = crashed or said or (asked_reload(log) if code is not None else None) or "the proof %s" % (
            "timed out" if code is None else "exited %d: it did not measure: %s" % (code, exit_reason(log)))
        if why.startswith(FINAL_WAIT):      # the expected state of a final clause on a small game: a row, no ledger note
            # its game: relentless_live_round.due runs it again only on another game (one row per game, not per round)
            return done("UNMEASURED", why, log=log, game=iso(started) if started else game_iso(fx))
        game = iso(started) if started else game_iso(fx)
        key = cause(why)
        rows = read_rows(os.path.join(root, "live", "runs.jsonl"))
        n = 1 + repeats(rows, item_id, criterion, sha, key, game)
        row.update(game=game, repeat=n, cause=key)
        before = seen_on_other_game(rows, item_id, criterion, sha, key, game) if code is not None else None
        # a reload request is left out of the two below: a new build always needs its own load
        ran = code is not None and not why.startswith(RELOAD)
        broken = broken_call(log) if ran else None
        earlier = seen_on_other_build(rows, item_id, criterion, sha, key, proof) if ran else None
        games = infra_games(rows, item_id, criterion, sha, game) if "proof_exit" not in row and "health" in row else 0
        box = bool(unable) and unable[0] == "harness"
        if games >= lr["infra_games"] or box:   # INFRA on healthy games, or a box fault: relentless_game._harness, no strike
            row["harness"] = True
            if any(x.get("harness") for x in rows if (x.get("item"), x.get("criterion"), x.get("sha"))
                   == (item_id, criterion, sha)):
                return done("UNMEASURED", why, log=log)
            if not box:
                why = "%s: INFRA on %d games for this build, so no game can judge it until the harness is fixed: %s" % (
                    HARNESS, games, why)
        elif broken or before or earlier:   # no further load or rerun of this build can say anything else
            row["defect"] = True
            if n > 1:
                return done("UNMEASURED", why, log=log)
            if broken:
                if broken not in why:   # the line that shows it, when the exit reason is another line
                    why = "%s (%s)" % (why, broken)
                head = "the proof's own call is broken, so a rerun or a reload cannot help"
            elif before:
                head = "the same cause on the game of %s and on this one (%s), so a reload cannot help" % (before, game)
            else:
                head = "the same proof line said the same on build %s, so another rerun cannot help" % earlier
            why = "%s: %s: %s" % (DEFECT, head, why)
        elif n == lr["repeat_unmeasured"]:
            why = "%s: the same cause %d times on this game (%s): %s" % (RELOAD, n, game, why)
        elif n > 1:     # said once already, or the reload request stands: a row, no ledger note
            return done("UNMEASURED", why, log=log)
        note = fx.rimflow("note", item_id, "--text", "relentless live %s %s UNMEASURED: %s (%s)" % (criterion, level, why,
                                                                                                  log)[:400],
                          "--why", "relentless live tier: no verdict, no run recorded")
        return done("UNMEASURED", why, log=log, noted=note.returncode == 0)
    result = "pass" if code == PASS else "fail"
    v = fx.rimflow("verify", item_id, "--criterion", criterion, "--level", level, "--sha", sha, "--result", result,
                   "--config", ("relentless-live: %s" % proof)[:300], "--evidence", log,
                   "--why", "relentless live tier: the running game, deployed build, supervisor-run proof")
    if v.returncode != 0:
        return done("UNMEASURED", "the verdict %s did not land: %s" % (result.upper(), (v.stderr or v.stdout)[-300:]),
                    log=log)
    return done("PASS" if code == PASS else "FAIL", reading.why if row.get("observe") else "proof exit %d" % code,
                log=log, **({"verdict_line": last_verdict(log)} if code == FAIL else {}))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run", help="one live criterion of one built item")
    p.add_argument("--item", required=True)
    p.add_argument("--criterion", required=True)
    p.add_argument("--proof", required=True, help="a shell command run from the repo root; exit 0 PASS, 1 FAIL")
    p.add_argument("--deploy", default="", help="deploy_custom_mods.py plan arguments covering the item's mods")
    p.add_argument("--site", default=None, help="a live_site.py command run, bridge held, before the proof")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    row = run(Fx(seat=r.get("seat") or "BENCH"), root, a.item, a.criterion, a.proof, a.deploy, r, site=a.site)
    print(json.dumps(row, indent=1, sort_keys=True))
    return {"PASS": 0, "FAIL": 1}.get(row["outcome"], 2 if row["outcome"] == "UNMEASURED" else 3)


if __name__ == "__main__":
    sys.exit(main())
