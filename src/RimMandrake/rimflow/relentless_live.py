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
import hashlib
import json
import os
import posixpath
import re
import shlex
import signal
import subprocess
import sys
import time
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    import fulltext  # noqa: E402

import proof_lint  # noqa: E402  the live part moved there
from proof_lint import (  # noqa: E402,F401
    BOOKS, CONTROL_WORDS, CRIT_LINE, CUT_AT, DEFAULTS, DEFECT, DEFECT_HEAD, DIR_WORDS, EXIT1_HARNESS,
    EXIT1_RELOAD, EXIT1_UNLOADED, FAIL_ROW, FINAL, FULL_LIST, GAME_MODS, GUARD_REFUSAL, HERE, INTERP_NO_SCRIPT,
    INTERP_VALUED, KV_NONE, KV_VALUE, LIVE_LEVELS, LOOP_WORDS, MOD_ROW, NEGATED, NEGATED_AFTER,
    OPS_LONGEST_FIRST, OTHER_TREE, OWNER_LEDGER, PREFIX_WORDS, PYTHONS, READ_NOTHING, REDIRECTS, RELOAD,
    REPO_SCRIPT, REPRO_MISS_VERDICTS, RULES, SHELLS, SHELL_OPS, SITE_CMD, SRC_MOD, STALE, TB_END, TESTABLE,
    VERDICT_LINE, WRAPPERS, WSLPATH, _FOLDER_SEEN, asked_reload, build_shas, cause, cites, compose_shells,
    could_not_ask, fingerprint, flyer_word, game_files, is_package, last_line, lint_item, lint_lines, live_rules,
    marker_hit, missing_scripts, observed_fail, owed, preflight, proof_budget, proof_scripts, reaches_game,
    read_nothing, read_text, redirect_targets, refused_proof, refused_site, shell_words, side_lines, stale_build,
    tail_lines, unquoted, vehicle_item, whole_criterion, with_shell,)
FINAL_WAIT = "final verification waits for the full list"     # relentless_game reads this prefix: batch, never restage
FULL_TIER_SHARE = 0.5       # northstar_driver.preflight's: under half the full list running is another tier
PASS, FAIL = 0, 1
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
# GAMEENV_FIX_PROOFSITE_0DB67BE7_ITEMS_WAIT: a proof of a live-menu/live-toggle item measures only on a staging of its own
# (the menu step ran on it, on the side it needs), so its exit 2 is a request for that staging, never a dud or a defect.
# The words leave out "it did not measure" (relentless_game.RAN_DUD, relentless_live_round.SAME_GAME_DUD count that)
MENU_WAIT = RELOAD + ": a live-menu/live-toggle proof measures only on a staging of its own (its menu step, its side)"
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
# rimbridge_client.resolve_endpoint's refusal under WSL python3: the proof never reached the game. A proof that catches
# the RimBridgeError and prints only its own "bridge unreachable" line (tickburst_bench 2026-11-06: "UNMEASURED: bridge
# unreachable (RimBridgeError)" on five clauses, routed as a proof/site defect, GAMEENV_FIX_PROOFSITE_9BC0E9EE_ITEMS_WAIT)
# is the same refusal: under WSL python3 the Windows-loopback bridge is never reachable, so its python.exe rerun is owed
WSL_BRIDGE = ("cannot reach the bridge from WSL", "Re-run under Windows Python", "bridge unreachable",
              "cannot reach the bridge")
REPRO_MISS = "repro miss"
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


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------- pure checks

sys.path.insert(0, HERE)
import model                                   # noqa: E402  the ledger's own cap and criterion line, not a copy
import live_observe                            # noqa: E402  the RMOBS measurement protocol; the regexes are its fallback


# What every live proof runs under. The lane deployed and launched before the proof, so a prover that calls `modcheck
# run` must neither re-deploy (a DLL the running game holds fails the write: Errno 22, then 'modcheck wrote NO RESULTS',
# 4 runs of STILLSAND_DUNE_GALE_LIVE_1, LIVEPROOF_DOLLAR_FIX_REFUSED_AT_FILING) nor swap or compose ModsConfig, which
# names only the next load (modcheck runner: MODCHECK_SKIP_DEPLOY, keep_modlist).
PROOF_ENV = {"MODCHECK_SKIP_DEPLOY": "1", "MODCHECK_KEEP_MODLIST": "1"}


# a criterion that is his act, not the game's: "the owner has looked at the one review and kept it" (WATER_DEPTH_RESKIN_
# HE_LOOKS_FIRST L4, filed at L2, so no level says it). The owner words open the criterion: "each grown limb the owner
# keeps on the S1 sheet renders in all four facings" is the game's to show; "he sees" could be a pawn's
OWNER_ACT = re.compile(r"^\W*(the owner|owner|mandrake|lukas)('s)?\s+(has\s+|have\s+|will\s+)?(looked|looks?|look at|kept|"
                       r"keeps?|approved?|approves|signs? off|signed off|sees|saw|seen|judged?|judges|reviewed)\b", re.I)


def owner_look(crit, proof):
    """crit: a criterion {"id", "level", "text"} (or its text). -> why it is the owner's own act (a look, a keep, a
    sign-off) that no game can pass, or None. RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS: the game lane skips such a
    clause and routes the item to him once the rest pass, instead of failing it every round until he looks."""
    if OWNER_LEDGER.search(proof or ""):
        return "its proof reads his ledger (OWNER.jsonl)"
    c = crit if isinstance(crit, dict) else {"text": crit or ""}
    m = OWNER_ACT.search(c.get("text") or "")
    if m:
        return "its text names his act (%r)" % m.group(0).strip()
    import relentless_showing
    return "it is a look clause (his look)" if relentless_showing.look_clause(c) else None


def voids(row, item_id, sha):
    """True when `row` is a void row (relentless_game.void_rows) for `item_id` on `sha` (None: on any sha). The rows
    before it were read through an instrument or site since repaired, so no look-back counts them
    (GAMEENV_FIX_PROOFSITE_18CF717D_ITEMS_WAIT: the void of 2026-11-06T13:30:05Z was read past, and
    PLANET_ATMOSPHERE_CLOUD_COST_1's A1-A3 cited the game of 2026-11-03T12:50:51Z as "the same cause on two games")."""
    if not row.get("void") or row.get("item") != item_id:
        return False
    other = row.get("sha") or ""
    return sha is None or (bool(other) and bool(sha) and (other.startswith(sha) or sha.startswith(other)))


def since_void(rows, item_id, sha):
    """-> the rows written after the item's last void row on `sha` (all of them when there is none)."""
    for i in range(len(rows) - 1, -1, -1):
        if voids(rows[i], item_id, sha):
            return rows[i + 1:]
    return rows


def repeats(rows, item_id, criterion, sha, key, game):
    """runs.jsonl rows -> how many of the newest rows for (item, criterion, sha), running back, are UNMEASURED on `key`
    on the same game. Any other outcome, cause or game ends the run."""
    n = 0
    for row in reversed(rows):
        if voids(row, item_id, sha):
            break
        if (row.get("item"), row.get("criterion"), row.get("sha")) != (item_id, criterion, sha):
            continue
        if row.get("outcome") != "UNMEASURED" or row.get("game") != game or (row.get("cause") or cause(row.get("why"))) != key:
            break
        n += 1
    return n


def seen_on_other_game(rows, item_id, criterion, sha, key, game):
    """-> the earlier game on which (item, criterion, sha) was already UNMEASURED on `key`, or None. A cause that outlives
    a reload is the proof's or the site's, not a stale game's (LIVE_EXIT2_FIX_DEFECT_AFTER_TWO_GAMES: 74 of 76
    `exited 2` rows were five criteria rerun every 17 min and reloaded every third run on one unchanging cause). A void
    row ends the look-back (voids)."""
    for row in reversed(rows):
        if voids(row, item_id, sha):
            return None
        if ((row.get("item"), row.get("criterion"), row.get("sha")) == (item_id, criterion, sha)
                and row.get("outcome") == "UNMEASURED" and row.get("game") and game and row["game"] != game
                and (row.get("cause") or cause(row.get("why"))) == key):
            return row["game"]
    return None


def seen_on_other_build(rows, item_id, criterion, sha, key, proof):
    """-> the earlier build on which this same proof line of (item, criterion) ended UNMEASURED on `key`, or None. A new
    build earns one run, and the same line saying the same again means the build did not reach what stopped it
    (PLANET_ATMOSPHERE_CLOUD_COST_1 said "rides a later load" on three builds running). A void row of the item, on any
    build, ends the look-back: what stopped the earlier build was repaired since (voids)."""
    for row in reversed(rows):
        if voids(row, item_id, None):
            return None
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
    the running load, not deployed) is the game phase's to restage, never counted here. A void row ends it (voids)."""
    seen = {game} if game else set()
    for row in reversed(rows):
        if voids(row, item_id, sha):
            break
        if (row.get("item"), row.get("criterion"), row.get("sha")) != (item_id, criterion, sha):
            continue
        if verdict(row) != "INFRA":
            break
        if row.get("outcome") == "UNMEASURED" and row.get("game") and "health" in row:
            seen.add(row["game"])
    return len(seen)


# LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED: the round deployed mod folders only, never the JawaBench companion
# (BridgeTools/JawaBench, bridgetools/build.py), so BRIDGE_STALL_DIAGNOSTIC_1's companion-only fix e26a661423 read A1 FAIL
# twice on the hand-deployed d62e3e51 DLL (companion_identity STALE). A clause owes the companion when its proofs file
# says `live-companion: JawaBench` (relentless_live_round.LIVE_COMPANION) or its build touched the companion's sources;
# then the game folder's DLL must read FRESH against the built sha before any bridge is taken, else "not deployed"
# (the game phase restages; relentless_stage builds and deploys it in the shutdown window).
COMPANION_SRC = "src/RimMandrake/bridgetools/JawaBench.BridgeTools/"
COMPANION = "the JawaBench companion"


def companion_touched(fx, sha, item_id=None):
    """True when the build (build_shas: the built commit, or the commits citing the item when it holds no game file)
    touched a companion compile input (companion_identity.wanted). A fake without `touched` touches nothing."""
    if not hasattr(fx, "touched"):
        return False
    _bridgetools()
    import companion_identity as CI
    return any(p.startswith(COMPANION_SRC) and CI.wanted(p[len(COMPANION_SRC):])
               for s in build_shas(fx, sha, item_id) for p in fx.touched(s))


def _bridgetools():
    d = os.path.join(os.path.dirname(HERE), "bridgetools")
    if d not in sys.path:
        sys.path.insert(0, d)


def companion_gap(v, started=None):
    """companion_identity.verdict of the game folder's DLL (plus "mtime") -> None when the running game can hold the
    built sha's companion, else (why, game_stamped). game_stamped False: the identity could not be read (the harness's,
    retried later); True: the DLL is not the build's, so only a staging changes it (UNDEPLOYED)."""
    st = (v or {}).get("state")
    if st == "FRESH":
        if started is not None and v.get("mtime") is not None and started <= v["mtime"]:
            return ("%s: %s was deployed %s, after the game started %s: the running game loaded the one before it"
                    % (UNDEPLOYED[0], COMPANION, iso(v["mtime"]), iso(started))), True
        return None
    if st in (None, "UNMEASURED"):
        return "%s's identity could not be read (companion_identity %s)" % (COMPANION, st or "gave nothing"), False
    _bridgetools()
    import companion_identity as CI
    return "%s: %s in the game folder is not the build's: %s" % (UNDEPLOYED[0], COMPANION, CI.describe(v)), True


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


def violated(log, criterion):
    """True when the proof's log already holds a valid RMOBS violation of `criterion` (live_observe): that run's evidence
    stands, so it is never replaced by a rerun."""
    try:
        return live_observe.read_log(log, live_observe.run_id_of(log), criterion).status == "VIOLATED"
    except Exception:       # noqa: BLE001  an unreadable log holds no violation
        return False


def wsl_rerun(proof, log_text):
    """-> the proof under python.exe when it is a plain `python3 <script>` that died on the WSL bridge refusal, else None."""
    if not proof.startswith("python3 "):
        return None
    lines = (log_text or "").splitlines()
    hit = next((i for i, x in enumerate(lines) if any(s in x for s in WSL_BRIDGE)), None)
    if hit is None:
        return None
    # a verdict printed before the bridge was lost is the run's evidence: never replaced by a rerun (Codex cd905b round 2)
    if any(VERDICT_WORD.search(x) for x in lines[:hit] if not x.startswith("$ ")):
        return None
    return "python.exe " + proof[len("python3 "):]


VERDICT_WORD = re.compile(r"\b(PASS|FAIL)\b")


# GAMEENV_FIX_HARNESS_678B1B18_ITEMS_WAIT: WSL interop timed out launching the Windows process (HOSE_END A1 site,
# 2026-11-06T16:20Z: the site log held only "<3>WSL (870506 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110"), so
# nothing ran and nothing touched the game. Such a log (the "$ cmd" header and WSL's own error lines, nothing else) is
# safe to run again once; a log holding any line of the command's own output is never retried.
WSL_INTEROP_LINE = re.compile(r"^<\d+>WSL \(\d+ - [^)]*\) ERROR: UtilAcceptVsock:\d+: accept4 failed \d+$")
INTEROP_TRIES = 2


def interop_never_started(log_text):
    """-> True when a log shows only WSL interop failing to launch the command: no line of its own output."""
    lines = [x.strip() for x in (log_text or "").splitlines() if x.strip()]
    body = lines[1:] if lines and lines[0].startswith("$ ") else lines
    return bool(body) and all(WSL_INTEROP_LINE.match(x) for x in body)


def run_launched(fx, cmd, log, timeout):
    """fx.run_proof, run again (up to INTEROP_TRIES in all) while WSL interop never started the process."""
    code = None
    for _ in range(INTEROP_TRIES):
        code = fx.run_proof(cmd, log, timeout)
        if code == 0 or not interop_never_started(read_text(log)):
            break
    return code


def exit_reason(path):
    """-> the line of a proof's log that says why it stopped: the last one naming a reason, cut to 200. "VERDICT
    UNMEASURED" as the last line told the worker nothing and made every cause on that proof the same key."""
    lines = tail_lines(path)
    for line in reversed(lines):
        if not NO_REASON.match(line):
            return line
    return lines[-1] if lines else ""


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
            return line
    return exit_reason(path)


def broken_call(path):
    """-> the log line showing the proof's own call is wrong (BROKEN_CALL), or None."""
    for line in reversed(tail_lines(path)):
        if BROKEN_CALL.search(line):
            return line
    return None


def setup_refused(path, proof=None):
    """The guard's refusal line when a step of the proof was refused, else None. LIVETIER_PREFLIGHT_FIX_TRIPS_OWN_GUARD:
    PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET's `--live --fresh-map; --triplet` lost its scene build to the refusal and its next
    step judged whatever map stood: the exit is that step's, 0 as readily as 1, and neither says anything about the mod."""
    for line in reversed(side_lines(proof) + tail_lines(path)):
        if re.search(GUARD_REFUSAL, line):
            return line
    return None


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


PLAN_DRIFT_TAIL = "Drift found. Re-run with --apply to deploy."


def plan_failed(plan_rc, plan_text):
    """True when the deploy plan itself failed or timed out. A plan exits 1 when ANY mod drifts; that plan is still a
    reading (the drift that matters is this commit's files), so it is no failure. Pure."""
    return plan_rc != 0 and not (plan_rc == 1 and (plan_text or "").rstrip().endswith(PLAN_DRIFT_TAIL))


def deploy_gap(files, plan_rc, plan_text, trees=(), folded=None):
    """-> why the built commit's game files are not what the game folder holds, or None.
    folded: {source folder: (composed target, key)}; a compose plan prints the KEY, so a folded source is matched by it
    (LIVE_RUNS_FIX_MOSTLY_MEASURE_NOTHING: 16 runs 'does not cover Scarlands' on a plan that composed Warscar).
    trees: mod folders whose WHOLE tree the build owes the game (a `live-deploy:` line: RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY,
    a deploy item commits no mod file). Any file the deploy would write counts, not only .xml and .dll; a `-` line does not
    (--apply leaves a file the repo lacks alone without --prune, so no staging could ever clear it) nor an H (held on purpose)."""
    if plan_failed(plan_rc, plan_text):
        return "the deploy plan failed (exit %s): %s" % (plan_rc, plan_text)
    if "def guard" in plan_text and "REFUSED" in plan_text:
        return "the deploy plan refused: %s" % plan_text
    covered, drift, off = plan_sections(plan_text)
    named = {folded_key(folded, m): m for m in [m for m, _ in files] + list(trees)}
    files = [(folded_key(folded, m), rel) for m, rel in files]
    trees = [folded_key(folded, m) for m in trees]
    off = {m: why for m, why in off.items() if m in named}  # an off mod the build does not ship is not its gap (Codex cd905b)
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


def folded_dirs(mods_dir, mod, folded=None):
    """The game-folder dirs a folded source loads from: Mods/<target>/Biomes/<key> or Mods/<target>/Biomes/_Kits/<key>
    (biomes_compose.dest_rel); [] when the manifest does not fold it."""
    if mod not in (folded or {}):
        return []
    target, key = folded[mod]
    if key == target:       # a settings shell (with_shell): its files sit at the composed mod's root
        return [os.path.join(mods_dir, target)]
    return [os.path.join(mods_dir, target, "Biomes", key), os.path.join(mods_dir, target, "Biomes", "_Kits", key)]


def deployed_paths(mods_dir, mod, rel, folded=None):
    """Where a mod file sits in the game folder: Mods/<Mod>/<rel>, inside a composed mod Mods/*/*/<Mod>/<rel>, or for a
    folded source under its compose key, engine kits one level deeper (folded_dirs)."""
    got = [os.path.join(mods_dir, mod, rel)] + glob.glob(os.path.join(glob.escape(mods_dir), "*", "*", glob.escape(mod),
                                                                      glob.escape(rel)))
    got += [os.path.join(d, rel) for d in folded_dirs(mods_dir, mod, folded)]
    return [p for p in dict.fromkeys(got) if os.path.isfile(p)]


# ---------------------------------------------------------------- the one run

class Fx(proof_lint.Fx):  # the dead methods; the live class moved to proof_lint.py
    def last_commit(self, sha, paths):
        """-> the full sha of the newest commit after `sha` touching any of `paths`, or None."""
        r = subprocess.run(["git", "log", "-1", "--format=%H", "%s..HEAD" % sha, "--", *paths], cwd=self.books,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        return (r.stdout.strip() or None) if r.returncode == 0 else None

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

    def deploy_plan(self, args, timeout):
        try:
            r = subprocess.run(["python3", os.path.join(self.books, "src/RimMandrake/Utils/deploy_custom_mods.py"),
                                *shlex.split(args)], cwd=self.books, capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "the deploy plan took over %ds" % timeout
        return r.returncode, r.stdout + r.stderr

    def companion(self, sha):
        """companion_identity.verdict (cover: a clean build of a descendant holds it) of the game folder's JawaBench DLL
        against the companion sources at `sha`, plus the DLL's "mtime" (None when absent). The game root is the Mods
        folder's parent (build.py DEPLOY_DIR)."""
        _bridgetools()
        import companion_identity as CI
        dll = os.path.join(os.path.dirname(os.path.normpath(self.mods_dir)), "BridgeTools", "JawaBench", CI.DLL_NAME)
        v = CI.verdict(dll, self.books, sha, cover=True)    # a clean later build holds it (COMPANION_DEPLOY_LIVE_ROUND_FORGETS)
        bc = v.get("build_commit")
        if v.get("state") == "STALE" and bc and not CI.known(self.books, bc):
            # the stager builds at a freshly synced origin/main the books clone may not have fetched yet: fetch once,
            # or a just-deployed covering build reads STALE and the game phase restages forever
            subprocess.run(["git", "-C", self.books, "fetch", "-q", "origin", "main"], capture_output=True, timeout=120)
            v = CI.verdict(dll, self.books, sha, cover=True)
        v["mtime"] = os.path.getmtime(dll) if os.path.isfile(dll) else None
        return v

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
        self.last_running = (frozenset(running), dict(want))     # run() records it on the row (env["running"])
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
                    r.returncode, (r.stderr or r.stdout).strip())
                return out
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            out["ping"], out["why"] = None, "the bridge ping from python.exe did not finish: %s" % str(e)
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

    def wrapup_restore(self, timeout=None):
        """WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF: replay every setting the wrap-up register still owes (a killed
        proof's forced storyteller, threat scale, mod field) through the bridge this run holds, then sweep.
        python.exe: the one interpreter here that reaches the bridge. -> (exit or None on timeout, last line)."""
        script, timeout = os.path.join(HERE, "wrapup.py"), timeout or WRAPUP_RESTORE_S
        try:
            path = subprocess.run(["wslpath", "-w", script], capture_output=True, text=True, timeout=20).stdout.strip()
            r = subprocess.run(["python.exe", path or script, "restore"], capture_output=True, text=True,
                               timeout=timeout, stdin=subprocess.DEVNULL, cwd=self.books,
                               env=dict(model.bridge_holder.process_env(),
                                        PATH=windows_path(os.environ.get("PATH", ""))))
        except subprocess.TimeoutExpired:
            return None, "timed out after %ds" % timeout
        return r.returncode, last_text(r.stdout or r.stderr)

    def run_proof(self, proof, log, timeout):
        """-> the proof's exit code, or None when it outran `timeout`. Output goes to `log`."""
        with open(log, "w", encoding="utf-8") as f:
            f.write("$ %s\n" % proof)
            f.flush()
            p = subprocess.Popen(proof, shell=True, cwd=self.books, stdout=f, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, executable="/bin/bash", start_new_session=True,
                                 env=dict(model.bridge_holder.process_env(), **PROOF_ENV,
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


# ---- admission (LIVELANE_BUILD_PREFLIGHT_REFUSES_UNRUNNABLE, redesign_final 2026-11-06 G1) ------------------------------
# A run stopped before the bridge is taken spent no slot and measured nothing: it is NOT_ADMITTED with a cause, never
# UNMEASURED (stage 3 probe: 319 of 592 UNMEASURED rows were these). Its `why` keeps the old words, so every prefix
# reader (UNDEPLOYED, STALE, FINAL_WAIT, relentless_game.RESTAGE, relentless_envcause) still routes it to its action.
NOT_ADMITTED = "NOT_ADMITTED"
NO_VERDICT = ("UNMEASURED", NOT_ADMITTED)
# cause -> (the action the lane takes on it, transient). The action is relentless_game's prove phase: recarry =
# _carry or game_stale_build (decides), deploy = relentless_envcause's deploy route or a staging that applies it,
# wait_load = a restage / the next load, full_list = the full-list tier (BENCH lane), retry = the read again in
# the next round (no timer: PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE). A transient cause never waits on its key.
ADMIT = {"unreadable_build": ("retry", True), "stale": ("recarry", False), "deploy_plan": ("retry", True),
         "deploy_gap": ("deploy", False), "no_game": ("wait_load", True), "old_build": ("wait_load", False),
         "companion_unread": ("retry", True), "running_load": ("wait_load", False), "load_unread": ("retry", True),
         "full_list": ("full_list", False), "full_list_unread": ("retry", True), "bridge_busy": ("retry", True)}
ADMIT_PREFIX = (("cannot read the built commit", "unreadable_build"), (STALE, "stale"), ("the build deleted ", "stale"),
                ("not deployed: the deploy plan failed", "deploy_plan"), ("not in the running load", "running_load"),
                (UNDEPLOYED[0], "deploy_gap"), ("no running game to test", "no_game"), ("the game started ", "old_build"),
                ("cannot read whether the build owes", "companion_unread"),
                ("%s's identity could not be read" % COMPANION, "companion_unread"),
                ("the running load's mod list could not be read", "load_unread"),
                # before FINAL_WAIT, whose prefix it shares: an unread FULL.LATEST is the harness's read, so it retries
                # instead of holding its key until a new build (RELENTLESS_LIVE_HARDEN_ADMISSION_READING)
                ("%s: %s unreadable" % (FINAL_WAIT, os.path.basename(FULL_LIST)), "full_list_unread"),
                (FINAL_WAIT, "full_list"),
                ("bridge not taken", "bridge_busy"))
HARNESS_FILES = ("relentless_live.py", "live_observe.py", "relentless_live_round.py")
_HARNESS_REV = []


def no_verdict(row):
    """A runs.jsonl row with no verdict: UNMEASURED (it ran or held the bridge) or NOT_ADMITTED (it never did)."""
    return bool(row) and row.get("outcome") in NO_VERDICT


def admit_cause(why):
    """A pre-bridge why -> its ADMIT cause, or None. run() and the replay of old rows read the same table."""
    w = why or ""
    for head, c in ADMIT_PREFIX:
        if w.startswith(head):
            return c
    return None


def pre_bridge(row):
    """An old UNMEASURED row that never held the bridge: slot False (the running-load / full-list gap), or no release,
    no health check, no proof and no log. A gap row carries log None, so the log counts only when it names a file."""
    return (row.get("outcome") == "UNMEASURED" and not row.get("miss") and (row.get("slot") is False or (
        not row.get("log") and not any(k in row for k in ("released", "health", "proof_exit")))))


def harness_rev():
    """-> short hash of the live harness's own source: a repaired harness is a changed key, so its rows run again."""
    if not _HARNESS_REV:
        h = hashlib.sha1()
        for n in HARNESS_FILES:
            try:
                with open(os.path.join(HERE, n), "rb") as f:
                    h.update(f.read())
            except OSError:
                h.update(n.encode())
        _HARNESS_REV.append(h.hexdigest()[:12])
    return _HARNESS_REV[0]


def full_list_print(path=None):
    """-> short hash of FULL.LATEST's bytes, or None when it cannot be read: a full_list hold's key part, so a changed
    (or restored) full list runs the held criterion again."""
    try:
        with open(path or FULL_LIST, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:12]
    except OSError:
        return None


def admit_key(sha, load, site, cause=None):
    """(sha, load fingerprint, site fingerprint, harness rev[, full list]): a NOT_ADMITTED key runs again the moment one
    part moves. A full_list cause also keys on FULL.LATEST's content (full_list_print)."""
    k = {"sha": sha, "load": load, "site": hashlib.sha1((site or "").encode("utf-8")).hexdigest()[:12],
         "harness": harness_rev()}
    if cause == "full_list":
        k["full"] = full_list_print()
    return k


def admit_waits(last, sha, game, site=None):
    """-> why a NOT_ADMITTED `last` still stands on (sha, game, site), or None when it may run now. A transient cause, a
    row with no key or no load read, or any key part changed: None (due() then decides; a transient cause runs in the next round).
    site None: the caller did not read it, so only the other parts are compared."""
    k = last.get("key") or {}
    c = last.get("admit")
    if not k or c not in ADMIT or ADMIT[c][1] or k.get("load") is None:
        return None
    now = admit_key(sha, game, site, c)
    parts = [p for p in ("sha", "load", "harness") + (("site",) if site is not None else ()) + (
        ("full",) if c == "full_list" else ()) if k.get(p) != now[p]]
    if c == "full_list" and now.get("full") is None:
        return None     # the full list cannot be read now: no proof it still stands; due() routes it
    if parts:
        return None
    return "not admitted (%s): waits for a new build, load, site or harness" % c


def admission_replay(rows):
    """Old runs.jsonl rows -> {pre_bridge, by_cause, unclassified[...], not_admitted}: what each pre-bridge UNMEASURED row
    would read now. unclassified must be empty: every pre-bridge return of run() has a cause."""
    out = {"rows": len(rows), "pre_bridge": 0, "not_admitted": 0, "by_cause": {}, "unclassified": []}
    for row in rows:
        if row.get("outcome") == NOT_ADMITTED:
            out["not_admitted"] += 1
            continue
        if not pre_bridge(row):
            continue
        out["pre_bridge"] += 1
        c = admit_cause(row.get("why"))
        if c is None:
            out["unclassified"].append((row.get("why") or ""))
        else:
            out["by_cause"][c] = out["by_cause"].get(c, 0) + 1
    return out


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def live_slis(rows, now, built_at=None, window_s=86400, fired=None):
    """The four live SLIs (redesign_final 3.1) per distinct (item, criterion, sha) key for the newest load, plus the old
    row-level share. built_at(sha) -> epoch of the build or None. -> dict, printed by `relentless.py reading`.
    fired(row) -> True when the lane EXECUTED the NOT_ADMITTED row's action after it (its own record says so), False
    when that record was read and holds none, None when nothing can say: a row's `action` is the action ASSIGNED, never
    proof it ran, so an unread one counts in `unread`, never in `fired`."""
    rows = [x for x in rows if isinstance(x.get("at"), str)]    # one 2026 row carries an epoch: no load, no day

    def at(row):
        try:
            return calendar.timegm(time.strptime(row["at"], "%Y-%m-%dT%H:%M:%SZ"))
        except ValueError:
            return None
    loads = sorted({x["game"] for x in rows if isinstance(x.get("game"), str)})
    load = loads[-1] if loads else None
    mine = [x for x in rows if x.get("item") and (load is None or x["at"] >= load)]
    keys = {}
    for x in mine:
        keys.setdefault((x["item"], x.get("criterion"), x.get("sha")), []).append(x)
    na, slot_keys, slot_unm = {}, 0, 0
    for ks in keys.values():
        adm = [x for x in ks if x.get("outcome") == NOT_ADMITTED]
        # an old pre-bridge UNMEASURED row spent no slot either: it never hides the key's NOT_ADMITTED refusal
        spent = [x for x in ks if x.get("outcome") in ("PASS", "FAIL", "UNMEASURED") and not pre_bridge(x)]
        if adm and not spent:
            c = adm[-1].get("admit") or "?"
            e = na.setdefault(c, {"keys": 0, "action": ADMIT.get(c, ("?",))[0], "fired": 0, "unread": 0})
            e["keys"] += 1
            f = fired(adm[-1]) if fired else None
            if f is None:
                e["unread"] += 1
            elif f:
                e["fired"] += 1
        if spent:
            slot_keys += 1
            slot_unm += not any(x.get("outcome") in ("PASS", "FAIL") for x in spent)
    cut = now - window_s
    first = {}
    for x in rows:
        t = at(x)
        if x.get("outcome") in ("PASS", "FAIL") and t is not None and x.get("item"):
            k = (x["item"], x.get("criterion"), x.get("sha"))
            first[k] = min(first.get(k, t), t)
    done_day = sum(1 for t in first.values() if t >= cut) * 86400.0 / window_s
    lag, seen = [], {}
    for k, t in first.items():
        if built_at and k[2] and t >= cut and k[2] not in seen:
            seen[k[2]] = built_at(k[2])     # one read per build, however many clauses it has
        b = seen.get(k[2]) if t >= cut else None
        if b:
            lag.append(max(0.0, t - b))
    unm = sum(1 for x in rows if no_verdict(x))
    return {"load": load, "keys": len(keys), "not_admitted_by_cause": na,
            "slot_unmeasured_share": round(slot_unm / slot_keys, 3) if slot_keys else None, "slot_keys": slot_keys,
            "measured_keys_per_day": round(done_day, 1),
            "built_to_verdict_s": {"p50": _pct(lag, 0.5), "p95": _pct(lag, 0.95), "n": len(lag)},
            "rows_incl_repeats_and_admission": round(unm / len(rows), 3) if rows else None}


def commit_time(sha, repo=BOOKS):
    """-> the commit's epoch, or None when git cannot read it (live_slis' built_at)."""
    try:
        p = subprocess.run(["git", "-C", repo, "show", "-s", "--format=%ct", sha], capture_output=True, text=True,
                           timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return int(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip().isdigit() else None


def sli_lines(s):
    """live_slis' dict -> the lines `relentless.py reading` prints."""
    if not s or "unread" in s:
        return ["live SLIs: COULD NOT READ (%s)" % (s or {}).get("unread", "no reading")]
    na = s["not_admitted_by_cause"]
    lag = s["built_to_verdict_s"]
    hours = lambda v: "-" if v is None else "%.1f h" % (v / 3600.0)     # noqa: E731
    share = lambda v: "-" if v is None else "%.0f%%" % (100 * v)        # noqa: E731
    return ["live SLIs (load %s, %d distinct keys):" % (s["load"] or "?", s["keys"]),
            "  1 NOT_ADMITTED keys by cause: %s" % (", ".join("%s %d -> %s (fired %d%s)" % (
                c, e["keys"], e["action"], e["fired"], ", unread %d" % e["unread"] if e.get("unread") else "")
                for c, e in sorted(na.items())) or "none"),
            "  2 slot-spending UNMEASURED share: %s of %d keys (target <10%%)" % (share(s["slot_unmeasured_share"]),
                                                                                 s["slot_keys"]),
            "  3 measured completions (PASS+FAIL keys) per day: %s" % s["measured_keys_per_day"],
            "  4 built -> first measured verdict: p50 %s, p95 %s (n %d)" % (hours(lag["p50"]), hours(lag["p95"]), lag["n"]),
            "  old share, rows incl. repeats and admission: %s" % share(s["rows_incl_repeats_and_admission"])]


def cost(root, row, marks, environ=None):
    """The run's proof cost row (proof_cost.py), written as the run ends: never reconstructed later, and never able to
    cost the run its verdict (proof_cost.record does not raise). Source: `broker` when the broker's job launched the round
    (RELENTLESS_PROOF_SOURCE, relentless_broker._round), its queue wait counted from the item's queued_at; else `round`.
    tokens: the item's staging-worker spend since its last row (proof_cost.staging_tokens); a scripted proof's own LLM
    calls are not seen from here."""
    import proof_cost
    env = os.environ if environ is None else environ
    src = "broker" if env.get("RELENTLESS_PROOF_SOURCE") == "broker" else "round"
    m = dict(marks, ended=time.time())
    if src == "broker":
        try:
            with open(os.path.join(root, "store", "broker", "queue.json"), encoding="utf-8") as f:
                q = ((json.load(f).get("items") or {}).get(row.get("item")) or {}).get("queued_at")
            if isinstance(q, (int, float)):
                # a later clause of the same batch waited from the previous clause's end, not from the queue entry
                prev = [proof_cost.epoch(c.get("ended")) for c in proof_cost.read(os.path.join(root, proof_cost.LEDGER))
                        if c.get("source") == "broker" and c.get("item") == row.get("item")]
                m["queued"] = max([float(q)] + [t for t in prev if t is not None and t >= q])
        except (OSError, ValueError, AttributeError, TypeError):
            pass
    try:
        tok = proof_cost.staging_tokens(root, row.get("item"))
    except Exception:       # noqa: BLE001  an unread spend record is an UNMEASURED cost, never the run's failure
        tok = {"tokens": None}
    tokens = tok.pop("tokens", None)
    got = proof_cost.record(root, src, row.get("item"), row.get("criterion"), row.get("sha"), row.get("tier"),
                            row.get("outcome"), m, tokens=tokens, why=row.get("why"), **tok)
    if "unwritten" in got:
        row["cost_unwritten"] = got["unwritten"]
    return got


WRAPUP_RESTORE_S = 180


def last_text(text):
    lines = [x for x in (text or "").strip().splitlines() if x.strip()]
    return lines[-1] if lines else ""


def wrapup_restore(fx):
    """The settings the wrap-up register still owes go back before the bridge is released
    (WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF). Never a verdict: its outcome is recorded on the row and nothing else.
    A fake fx without the hook records that it was not asked. -> {"exit", "line"}"""
    hook = getattr(fx, "wrapup_restore", None)
    if hook is None:
        return {"exit": None, "line": "not asked: this fx has no wrapup_restore"}
    try:
        code, line = hook()
    except Exception as e:  # noqa: BLE001  the restore never stops the release
        code, line = None, "%s: %s" % (type(e).__name__, str(e))
    return {"exit": code, "line": line}


def running_ref(root, running, want, inferred=()):
    """The running load a row was admitted on -> {"n", "sha", "inferred_held"}: the sorted packageId list is written
    once per distinct load to <root>/live/loads/<sha>.json (a full list is ~300 ids; a row carries only its hash), and
    inferred_held says, for each mod the gate inferred, whether the running load held it at the pre-slot read
    (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: the effective mod list, so a verdict says what environment produced it)."""
    ids = sorted(running)
    h = hashlib.sha1("\n".join(ids).encode("utf-8")).hexdigest()[:12]
    d = os.path.join(root, "live", "loads")
    p = os.path.join(d, h + ".json")
    if not os.path.isfile(p):
        try:
            os.makedirs(d, exist_ok=True)
            with open(p + ".tmp", "w", encoding="utf-8") as f:
                json.dump(ids, f)
            os.replace(p + ".tmp", p)
        except OSError:
            pass        # the row still carries n and sha; a lost list file is never a verdict
    held = {a.get("mod"): (want.get(a.get("mod")) in running) if want.get(a.get("mod")) else
            (str(a.get("mod")).lower() in running) for a in inferred if a.get("mod")}
    return {"n": len(ids), "sha": h, "inferred_held": held}


def run(fx, root, item_id, criterion, proof, deploy, r, now=None, needs=(), site=None, trees=(), env=None,
        companion=False, menu=False):
    """-> the run's row (also appended to <root>/live/runs.jsonl). row["outcome"] is PASS, FAIL, UNMEASURED or REFUSED.
    needs: mod folders the proof declares (live_proofs `live-mods:`) beyond the ones the built commit changed; with
    those, each one's About.xml modDependencies must be in the RUNNING load, or the row is UNMEASURED (restage), never
    run. A FINAL (GREEN-FULL) criterion also needs the full-list tier up: else UNMEASURED FINAL_WAIT, never run.
    site: the item's `live-site` command for this criterion (refused_site), run with the bridge held before the proof.
    trees: mod folders of a `live-deploy:` line: a drifting tree is UNMEASURED "not deployed" (the game phase stages, whose
    worker applies it), never a run; `deploy` must cover them. It says what the folder holds, not when: unlike `files`, no
    per-file stamp proves the running game started after that deploy; the staging's restart is what loads it.
    companion: the proofs file has a `live-companion:` line; a build that touched the companion's sources owes it too
    (companion_touched). Owed, the game folder's JawaBench DLL must read FRESH against the build (companion_gap).
    menu: the proofs file has a `live-menu:` or `live-toggle:` line; an exit that is neither PASS nor FAIL is then
    MENU_WAIT, a restage (bounded by relentless_game.stage_tries, one per side), never a defect for another game."""
    now = time.time() if now is None else now
    lr = live_rules(r)
    row = {"at": iso(now), "item": item_id, "criterion": criterion, "proof": proof, "deploy": deploy}
    if env is not None:     # the effective mod list and every inferred addition with its evidence (LIVE_NEEDS_ENFORCE_...)
        row["env"] = env
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    marks = {"start": now}      # PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES: the wall clock split, written by done()

    def done(outcome, why, **kw):
        row.update(kw, outcome=outcome, why=why)
        row["verdict"] = ("INFRA" if "proof_exit" not in row else "FAIL" if row.get("observe", {}).get("status") ==
                          "VIOLATED" else "PASS" if row["proof_exit"] == PASS else "FAIL")
        if outcome in NO_VERDICT and "game" not in row and why.startswith(UNDEPLOYED):
            row["game"] = game_iso(fx)      # relentless_live_round.due retries an undeployed build on another game only
        cost(root, row, marks)     # first: a cost row that could not be written says so in the run's own row
        with open(os.path.join(root, "live", "runs.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def admit(why, **kw):
        """A return before the bridge: NOT_ADMITTED, its cause, the action the lane takes and the key it waits on."""
        c = admit_cause(why) or "bridge_busy"
        load = kw["game"] if "game" in kw else (iso(started) if started else game_iso(fx))
        if c in ("deploy_plan", "load_unread"):
            load = None     # the harness's read failed: no load stamp, so the key never holds it (transient)
        kw.setdefault("game", load)
        return done(NOT_ADMITTED, why, admit=c, action=ADMIT[c][0], slot=False, key=admit_key(sha, load, site, c), **kw)

    started = None
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
        return admit("cannot read the built commit: %s" % e)
    if why:
        return admit(why)
    if files or trees:
        rc, plan = fx.deploy_plan(deploy or "", lr["plan_max_s"])
        why = deploy_gap(files, rc, plan, trees, getattr(fx, "folded", dict)())
        if why:     # a plan that failed or timed out is the harness's: it may pass in a minute, so no game stamp; a plan
            # that read drift (exit 1) is a reading of THIS game's folder and keeps its game (Codex cd905b)
            return admit("not deployed: %s" % why, **({"game": None} if plan_failed(rc, plan) else {}))
    if files:
        stamps = [fx.mtime(mod, rel) for mod, rel in files]
        if None in stamps:
            lost = [("%s/%s" % f) for f, t in zip(files, stamps) if t is None]
            return admit("not deployed: no game copy of %s" % ", ".join(lost[:5]))
        started = fx.game_started()
        if started is None:
            return admit("no running game to test")
        if started <= max(stamps):
            return admit("the game started %s, before the build's files were deployed %s: it runs the old "
                         "build" % (iso(started), iso(max(stamps))))
        row.update(game_started=iso(started), deployed=iso(max(stamps)), files=len(files))
    else:       # no file stamps to hold, but the game's identity still is: a restart mid-proof is never this game's verdict
        stamps, started = [], fx.game_started()
    try:
        owes = companion or companion_touched(fx, sha, item_id)
    except (ValueError, OSError) as e:
        return admit("cannot read whether the build owes %s: %s" % (COMPANION, e))
    if owes:
        if not hasattr(fx, "companion"):
            return admit("%s's identity could not be read (no companion reader)" % COMPANION)
        v = fx.companion(sha) or {}
        row["companion"] = {k: (v.get(k) or "")[:12] if k != "state" else v.get(k) for k in ("state", "embedded", "want")}
        if v.get("covered_by"):
            row["companion"]["covered_by"] = v["covered_by"][:12]
        cg = companion_gap(v, fx.game_started() if v.get("state") == "FRESH" else None)
        if cg:
            return admit(cg[0], **({} if cg[1] else {"game": None}))
    # The build is deployed and older than the game, but the running list may not load its mod (or a mod it declares,
    # or their dependencies) at all (owner 2026-11-02: a game fits an item by its RUNNING mods, not ModsConfig); a FINAL
    # clause also needs the full-list tier. Read BEFORE the bridge is taken, one read each: a run the running game cannot
    # serve takes no slot (LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: 18:00-18:16Z 2026-11-03 GRAFFITI F1/F2 took the bridge
    # four times to read "48 mods, 40 of FULL.LATEST's 316"). row["slot"] False: no bridge, no proof, no game time.
    need = sorted({m for m, _ in files} | set(needs))
    if hasattr(fx, "last_running"):
        fx.last_running = None      # this row's read only, never another item's
    try:
        gap = (fx.running_load_gap(need) if need else None) or (fx.full_list_gap() if level == FINAL else None)
    except Exception as e:                          # noqa: BLE001  an unread list is the harness's, never a verdict
        gap = "the running load's mod list could not be read: %s: %s" % (type(e).__name__, str(e))
    if env is not None and getattr(fx, "last_running", None):
        row["env"] = dict(env, running=running_ref(root, *fx.last_running, inferred=env.get("inferred") or ()))
    log, code, crashed = None, None, gap
    if gap:     # NOT_ADMITTED: no repeat count, no reload, no ledger note; the key holds it until the load moves
        return admit(gap, **({"game": iso(started)} if started else {}))
    else:
        try:
            took = fx.rimflow("bridge", "take", "--idle-ok", "--for",
                              "relentless live test: %s %s (%s), read-only proof" % (item_id, criterion, level))
        except Exception as e:      # noqa: BLE001  a take that raised (timed out) may still have taken: give it back
            try:
                fx.rimflow("bridge", "release", "--mine")
            except Exception:       # noqa: BLE001  the stale-hold rule frees it in 45 minutes
                pass
            return admit("bridge not taken: the take raised %s: %s" % (type(e).__name__, str(e)))
        if took.returncode != 0:
            return admit("bridge not taken: %s" % (took.stderr or took.stdout).strip())
        marks["taken"] = time.time()
        crashed, exited = None, False    # exited: the last proof launch returned an exit (or timed out), never raised
        try:        # from the take on, every path ends in the release below (Codex cd905b: acquisition bypassed it)
            log, n = None, 0
            while log is None or os.path.exists(log):  # a retry in the same second must not overwrite the last evidence
                log = os.path.join(root, "live", "%s-%s-%s%s.log" % (item_id, criterion, time.strftime(
                    "%Y%m%dT%H%M%SZ", time.gmtime(now)), "" if not n else "-%d" % n))
                n += 1
            if started != fx.game_started() or (files and stamps != [fx.mtime(m, rel) for m, rel in files]):
                crashed = "the game or its deployed files changed while the bridge was being taken"
            if crashed is None:     # bridge held, nothing spent yet: is the game fit to judge the mod at all?
                try:
                    h = fx.health(files, sha, lr["health_max_s"]) or {}
                except Exception as e:      # noqa: BLE001  a health check that cannot run is no health
                    h = {"why": "the health check could not run: %s: %s" % (type(e).__name__, str(e))}
                row["health"] = {k: v for k, v in h.items() if k != "why"}
                row["health"]["ok"] = not h.get("why")
                if h.get("why"):
                    crashed = h["why"] if h["why"].startswith(UNDEPLOYED) else "%s: %s" % (UNHEALTHY, h["why"])
            if crashed is None and code is None and site:
                slog = log[:-len(".log")] + "-site.log"
                row["site_log"] = slog
                sc = run_launched(fx, site, slog, proof_budget(site, lr["site_max_s"]))
                if sc != 0:
                    crashed = asked_reload(slog) or "site not prepared: %s" % (
                        last_line(slog) or ("timed out" if sc is None else "exit %d" % sc))
            if crashed is None and code is None:
                row["proof_exit"] = None        # the proof starts: from here every outcome is the mod's (verdict)
                marks["proof_start"] = time.time()
                try:
                    code = run_launched(fx, proof, log, proof_budget(proof, lr["proof_max_s"]))
                    exited = True
                finally:        # a proof that raised still spent its time proving
                    marks["proof_s"] = time.time() - marks["proof_start"]
                row["proof_exit"] = code
                # a WSL traceback exits 1; a log whose RMOBS rows already hold a violation is never run again, or the
                # rerun's log would replace the evidence of it (Codex cd905b)
                again = wsl_rerun(proof, read_text(log)) if code != PASS and not violated(log, criterion) else None
                if again:
                    os.replace(log, log[:-len(".log")] + "-wsl.log")
                    row["rerun"] = again
                    t_again, exited = time.time(), False
                    try:
                        code = fx.run_proof(again, log, proof_budget(again, lr["proof_max_s"]))
                        exited = True
                    finally:
                        marks["proof_s"] += time.time() - t_again
                    row["proof_exit"] = code
                # every exit is checked, not only PASS/FAIL: a later RMOBS violation turns any exit into a FAIL, so a
                # proof whose game restarted under it must not reach that reading (Codex cd905b round 3)
                if (started != fx.game_started()
                                             or (files and stamps != [fx.mtime(m, rel) for m, rel in files])):
                    crashed, code = "the game or its deployed files changed while the proof ran", None
        except Exception as e:                          # the proof never ran to an exit code: no verdict, but the row stands
            crashed, code = "the proof could not run: %s: %s" % (type(e).__name__, str(e)), None
            if "proof_exit" in row and not exited:
                row.pop("proof_exit")   # a launch that raised gave no exit: the harness's (INFRA), never a FAIL verdict
        finally:
            if (row.get("health") or {}).get("ok"):     # a game that answered: pay what the register owes it first
                row["wrapup_restore"] = wrapup_restore(fx)
            try:
                gave = fx.rimflow("bridge", "release", "--mine")
                row["released"], gave_why = gave.returncode == 0, (gave.stderr or gave.stdout).strip()
            except Exception as e:                      # a timed-out release still leaves the row
                row["released"], gave_why = False, "%s: %s" % (type(e).__name__, str(e))
            marks["released"] = time.time()
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
        unable = could_not_ask(log, proof)
    if code == PASS and not crashed and not unable and log:
        refused = setup_refused(log, proof)
        if refused:
            unable = ("harness", refused)
            said = "%s: the proof exited 0 with a step refused, so its map was never prepared: %s" % (HARNESS, refused)
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
        note = fx.rimflow("note", item_id, "--text", fulltext.fit(("relentless live %s %s %s (%s)" % (criterion, level, why, log)), 400),
                          "--why", "relentless live tier: a repro miss, no verdict recorded")
        return done("UNMEASURED", why, log=log, game=game, miss=True, noted=note.returncode == 0)
    if code not in (PASS, FAIL) or unable:
        why = crashed or said or (asked_reload(log) if code is not None else None) or "the proof %s" % (
            "timed out" if code is None else "exited %d: it did not measure: %s" % (code, exit_reason(log)))
        # PLANET_ATMOSPHERE_CLOUD_COST_1 A2 said "rides a later load" on a game no staging of its own had served, and
        # "the same cause on another game" made it a defect routed as an environment repair: its own staging can help
        waits = bool(menu) and code is not None and not crashed and not unable and not why.startswith(RELOAD)
        if waits:
            why = "%s: %s" % (MENU_WAIT, exit_reason(log))
        if why.startswith(FINAL_WAIT):      # the expected state of a final clause on a small game: a row, no ledger note
            # its game: relentless_live_round.due runs it again only on another game (one row per game, not per round)
            return done("UNMEASURED", why, log=log, game=iso(started) if started else game_iso(fx))
        game = iso(started) if started else game_iso(fx)
        key = cause(why)
        rows = read_rows(os.path.join(root, "live", "runs.jsonl"))
        n = 1 + repeats(rows, item_id, criterion, sha, key, game)
        row.update(game=game, repeat=n, cause=key)
        # a proof that TIMED OUT (it ran, no crash) is compared across games too: else one that hangs on every game asks
        # for a reload on each, never reaching the defect cap (Codex cd905b)
        timed_out = code is None and not crashed and "proof_exit" in row
        before = (seen_on_other_game(rows, item_id, criterion, sha, key, game)
                  if (code is not None or timed_out) and not waits else None)
        # a reload request is left out of the two below: a new build always needs its own load
        ran = code is not None and not why.startswith(RELOAD)
        broken = broken_call(log) if ran else None
        earlier = seen_on_other_build(rows, item_id, criterion, sha, key, proof) if ran else None
        games = infra_games(rows, item_id, criterion, sha, game) if "proof_exit" not in row and "health" in row else 0
        box = bool(unable) and unable[0] == "harness"
        if games >= lr["infra_games"] or box:   # INFRA on healthy games, or a box fault: relentless_game._harness, no strike
            row["harness"] = True
            if any(x.get("harness") for x in since_void(rows, item_id, sha)
                   if (x.get("item"), x.get("criterion"), x.get("sha")) == (item_id, criterion, sha)):
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
        note = fx.rimflow("note", item_id, "--text", fulltext.fit("relentless live %s %s UNMEASURED: %s (%s)" % (criterion, level, why,
                                                                                                  log), 400),
                          "--why", "relentless live tier: no verdict, no run recorded")
        return done("UNMEASURED", why, log=log, noted=note.returncode == 0)
    result = "pass" if code == PASS else "fail"
    v = fx.rimflow("verify", item_id, "--criterion", criterion, "--level", level, "--sha", sha, "--result", result,
                   "--config", fulltext.fit(("relentless-live: %s" % proof), 300), "--evidence", log,
                   "--why", "relentless live tier: the running game, deployed build, supervisor-run proof")
    if v.returncode != 0:
        return done("UNMEASURED", "the verdict %s did not land: %s" % (result.upper(), (v.stderr or v.stdout)),
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
    q = sub.add_parser("admission-replay", help="old runs.jsonl -> what each pre-bridge UNMEASURED row reads now; "
                                                "exit 0 when every one has an admission cause")
    q.add_argument("runs", nargs="?", default="/home/mandrake/rm/relentless/live/runs.jsonl")
    a = ap.parse_args(argv)
    if a.cmd == "admission-replay":
        try:        # read_rows reads an unreadable file as empty: a replay of nothing is no replay (exit 2)
            with open(a.runs, encoding="utf-8", errors="replace"):
                pass
        except OSError as e:
            print("UNMEASURED: cannot read %s (%s)" % (a.runs, e))
            return 2
        out = admission_replay(read_rows(a.runs))
        print(json.dumps(out, indent=1, sort_keys=True))
        print("pre-bridge UNMEASURED rows left: %d of %d pre-bridge (%d rows)" % (
            len(out["unclassified"]), out["pre_bridge"], out["rows"]))
        return 0 if not out["unclassified"] else 1
    with open(os.environ.get("RELENTLESS_RULES") or RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    row = run(Fx(seat=r.get("seat") or "BENCH"), root, a.item, a.criterion, a.proof, a.deploy, r, site=a.site)
    print(json.dumps(row, indent=1, sort_keys=True))
    return {"PASS": 0, "FAIL": 1}.get(row["outcome"], 2 if row["outcome"] in NO_VERDICT else 3)


if __name__ == "__main__":
    sys.exit(main())
