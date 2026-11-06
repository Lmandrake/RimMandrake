#!/usr/bin/env python3
"""relentless_live_round.py -- one game-up sitting of the live tier: every built item that has a written proof for a
live criterion it owes gets relentless_live.run(), several per sitting (RA_S09_LIVE_WIRE_ONE_REAL_LEAF).

    python3 src/RimMandrake/rimflow/relentless_live_round.py eligible        # what a round would try, and why not the rest
    python3 src/RimMandrake/rimflow/relentless_live_round.py round [--max N]   # default: every eligible proof
    python3 src/RimMandrake/rimflow/relentless_live_round.py census [--last 300]   # runs.jsonl sorted by cause

The supervisor (relentless.py tick, live_tick) starts `round` detached, at most one at a time, at every tick that finds none
running and no other live user: no clock and no cap (PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE, owner 2026-11-06: "of course we
should drop all this pacing control crap... the LLM's pace things slowly all by themselves"). A round that ran a proof wakes
the supervisor's game pass (wake_supervisor), so the next proof starts now and not at the next tick.

WHERE A PROOF COMES FROM: a line in infrastructure/state/live_proofs/<ID>.txt, one per criterion:

    live-proof A2: python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_PaleMoss

A proof that needs mods its build did not change (a harness item, a proof over another mod) names them on one line, so
the round runs it on any game holding them and their About.xml dependencies, and UNMEASURED ("not in the running load",
which the game phase restages) on any other (PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS):

    live-mods: Graffiti, SacredGraffiti

An item whose whole job is a deploy commits no mod file, so no commit says what to deploy, and a worker may not --apply
(live.forbid_re). It names the trees it owes the game, which also makes them live-mods:

    live-deploy: Armoury, StarWarsPatches
    live-proof A1: python3 src/RimMandrake/rimflow/relentless_live_round.py deployed --item <ID>

A drifting tree reads UNMEASURED "not deployed", so the game phase stages and its staging worker applies them; `deployed
--lint` is the offline proof (RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY).

A proof that needs an EXACT list (a perf toll measured on one tier, a "the running load IS this set" bar) names a
modset_builder.py tier, for every clause of the file or for named ones (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD: VITALS A1 wanted
ratchet_pilot's ~23 mods and got 39, WRONG_TIER every run):

    live-tier: gizkastowaway
    live-tier A1: ratchet_pilot

A proof that calls JawaBench tools runs against whatever companion DLL is in the game folder (BridgeTools/JawaBench), which
no mod deploy writes. Its file says so, and the clause then waits for that DLL to read FRESH against the build
(companion_identity; a build touching src/RimMandrake/bridgetools/JawaBench.BridgeTools owes it without the line); the
game phase's staging builds and deploys it in the shutdown window (LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED):

    live-companion: JawaBench

Such a clause never runs on Archmagi's game: the owner made SteveDesktop the exact-tier host (by card, 2026-11-05), so the
game phase sends it to testq as a job of profile tier:<name> (relentless_game.steve_sync), Steve loads that tier as the
whole list and runs the line, and its verdict comes back as a runs.jsonl row (source testq). This round skips it.

A criterion at level GREEN-FULL is the FINAL verification on the whole full list: it runs only when that tier is up.

Not the item's prose: the Marker's box leaves infrastructure/state/items out (walls.marker.tree_exclude), so a proof kept
there could never be checked blind. The prose keeps the why; the .txt holds only the lines.

Nothing here turns a criterion's English into a proof: a guessed proof would pass criteria nobody proved. A criterion with
no line is counted as `no proof` in `eligible` and waits for one.

A round, in order:
  1. no running game -> one rounds.jsonl row and nothing else (no bridge, no plan);
  1b. the canaries (relentless_canary.py), run here in the service's own process and cached by environment fingerprint:
     interop, the game's identity, our bridge identity, a bridge round trip, the load's identity, a known observation and
     a wrong expectation rejected. Sick -> one rounds.jsonl row "stopped: canary <name>: ..." and no proof spends a slot;
  2. candidates: built/validated, built sha, an owed criterion at a live level with a live-proof line, of any owner and
     any mod (FlowWorks and Gimme Some Slack included: FOUNDRY retired 2026-11-02, owner by card, and its acceptance
     sweeps became this lane);
  3. history (live/runs.jsonl): a criterion already PASS, FAIL or REFUSED on the same built sha is not run again (a FAIL
     stands until a new build; a refusal of a criterion cut on the ledger stands until its prose holds it whole);
     an UNMEASURED or NOT_ADMITTED row has no timer: it routes by cause (due()). The bridge's or the harness's transient
     read runs again in the next round; anything else waits for what it names to move: a new build, another game (the
     load, the deploy, the site a staging makes), a final clause the full-list tier; never on its build at all once the
     row is a `defect` (relentless_live's cap);
  4. each run is relentless_live.run(): flyer and forbidden-proof refusal, files changed since the build, the deploy plan
     (args derived from the item's own mods, one plan per args per round), the game started after the deploy, the bridge
     taken with --idle-ok and released at once after each proof, the verdict a `rimflow verify` on the built sha;
  5. the round stops early when the game went away or the bridge is held by someone else.
"""
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_live as L     # noqa: E402

# Bare, or wrapped whole in one pair of Markdown backticks; a bare command keeps its own backticks (echo `date`).
LINE = (r"^\s*(?:[-*]\s+)?(?:`{verb}\s+(?P<cid1>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd1>[^`\s][^`]*?)`"
        r"|{verb}\s+(?P<cid2>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd2>\S.*?))\s*$")
PROOF_LINE = re.compile(LINE.format(verb="live-proof"))
# `live-site <CID>: <cmd>`: what makes the map or save the proof reads, run first with the bridge held (relentless_live)
SITE_LINE = re.compile(LINE.format(verb="live-site"))
PROOFS_DIR = "infrastructure/state/live_proofs"
# No pacing (PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE): round_max 6, round_every_s 1800 and unmeasured_retry_s 6 h are gone;
# nothing reads them from a rules file. `max_items` (round --max) remains a caller's own bound, never a default.
DEFAULTS = {}
STOP = ("no running game to test", "bridge not taken")
# LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART: a cause that is the bridge's or the running game's, not the clause's, holds
# for every clause after it in the same round, so the round ends at the first one. Every pattern is from a run of
# 2026-11-05/06 (relentless/live/runs.jsonl): one UNKNOWN-outcome mutating call made rimbridge_client refuse
# LONGSHADE_SCENE_LIVECHECK_1 A8..A11 in turn ("IndeterminateError ... --reconcile"); five clauses each waited out
# "the running load's mod list could not be read" (14 min); "bridge unreachable", a health ping with no answer.
BRIDGE_DUD = re.compile(r"IndeterminateError|rimbridge_client\.py --reconcile|bridge unreachable"
                        r"|the running load's mod list could not be read|the bridge does not answer")
# a proof that ran on the game and measured nothing (relentless_game.RAN_DUD's words), or a site that would not prepare:
# rerun on the same game and build it can only say the same again
SAME_GAME_DUD = re.compile(r"the proof (exited \d+: it did not measure|timed out)|^site not prepared")
WAITS_TIER, DUD_HERE = "waits for the full-list tier", "measured nothing on this game"    # due()'s, relentless_game reads


# GAMEENV_FIX_PROOFSITE_FB127191_ITEMS_WAIT: a clause with no `live-site` line of its own gets this one, so no proof meets
# a game a staging left on the main menu (PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES A1-A3 and RINDCOAT's A1 each read "the game
# is not Playing" and measured nothing; RINDCOAT's own `--game` line fixed only that instance). It leaves a map that is
# up alone (two bridge reads) and starts a quicktest only when there is none. Not for a file whose proofs want the main
# menu or a load pair (live-menu, live-toggle) or that is only a deploy (live-deploy): those keep no site.
DEFAULT_SITE = "python.exe src/RimMandrake/Utils/live_site.py --game"


def site_for(text, cid):
    """-> the `live-site` command a criterion runs before its proof: its own line, else DEFAULT_SITE, else None."""
    own = proof_lines(text, SITE_LINE).get(cid)
    if own:
        return own
    try:
        menu = live_menu(text) or live_toggle(text)
    except ValueError:      # a malformed line is the game phase's to hold (menu_bound); no site is added to it
        return None
    return None if menu or live_deploy(text) else DEFAULT_SITE


def proof_lines(prose, pattern=PROOF_LINE):
    """An item's prose -> {criterion id: proof command}. A second line for the same criterion is ignored (first wins).
    pattern=SITE_LINE reads the `live-site` lines the same way."""
    out = {}
    for line in (prose or "").splitlines():
        m = pattern.match(line)
        if m:
            cid, cmd = (m.group("cid1"), m.group("cmd1")) if m.group("cid1") else (m.group("cid2"), m.group("cmd2"))
            out.setdefault(cid, cmd.strip())
    return out


LIVE_MODS = re.compile(r"^\s*(?:[-*]\s+)?`?live-(?:mods|deploy)\s*:\s*(?P<mods>[^`]*)`?\s*$")
LIVE_DEPLOY = re.compile(r"^\s*(?:[-*]\s+)?`?live-deploy\s*:\s*(?P<mods>[^`]*)`?\s*$")
# the proof drives a JawaBench tool, so the game folder's companion must be the build's (LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED)
LIVE_COMPANION = re.compile(r"^\s*(?:[-*]\s+)?`?live-companion\s*:\s*(?P<what>[^`#]*?)`?\s*(?:#.*)?$")
# the mods a proof intends to run WITHOUT (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT): never loaded by it, never inferred
LIVE_WITHOUT = re.compile(r"^\s*(?:[-*]\s+)?`?live-without\s*:\s*(?P<mods>[^`]*)`?\s*$")
# STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS: `live-menu: <cmd>` is run by the staging once the load reaches the main menu
# (the bridge token) and BEFORE any game starts: a sample a map would spoil (VRAM, private bytes). `{toggle}` in it is
# this staging's live-toggle side. `live-toggle: <mod>` asks for a pair of loads, one with the mod and one without it:
# the item's stagings alternate sides (toggle_side), it stages alone, and the without side refuses a list holding the mod.
LIVE_MENU = re.compile(r"^\s*(?:[-*]\s+)?(?:`live-menu\s*:\s*(?P<cmd1>[^`\s][^`]*?)`|live-menu\s*:\s*(?P<cmd2>\S.*?))\s*$")
LIVE_TOGGLE = re.compile(r"^\s*(?:[-*]\s+)?`?live-toggle\s*:\s*(?P<mods>[^`#]*?)`?\s*(?:#.*)?$")
TOGGLE_SIDES = ("with", "without")
TOGGLE_MARK = "{toggle}"


def live_menu(text):
    """A live_proofs file -> the commands of its `live-menu:` lines (in order, no repeats), templates unfilled."""
    out = []
    for line in (text or "").splitlines():
        m = LIVE_MENU.match(line)
        if m:
            cmd = (m.group("cmd1") or m.group("cmd2") or "").strip()
            if cmd and cmd not in out:
                out.append(cmd)
    return out


def live_toggle(text):
    """A live_proofs file -> the one mod its `live-toggle:` lines name, or None. ValueError on a line naming more or
    less than one mod, or two lines naming different mods: one pair of loads differs by one mod."""
    got = None
    for line in (text or "").splitlines():
        m = LIVE_TOGGLE.match(line)
        if not m:
            continue
        words = m.group("mods").replace(",", " ").split()
        if len(words) != 1:
            raise ValueError("a live-toggle line names exactly one mod, not %r" % m.group("mods"))
        if got and got.lower() != words[0].lower():
            raise ValueError("live-toggle names two mods (%s, %s): a pair of loads differs by one mod" % (got, words[0]))
        got = words[0]
    return got


def toggle_side(stages):
    """The side of the next staging of a live-toggle item that has staged `stages` times: with, without, with, ..."""
    return TOGGLE_SIDES[int(stages or 0) % 2]


def menu_cmds(text, side=None):
    """live_menu with `{toggle}` filled by `side`. ValueError when a command asks for the side and the file names no
    live-toggle (or the caller has no side): it would run with a literal {toggle}."""
    out = []
    for cmd in live_menu(text):
        if TOGGLE_MARK in cmd:
            if side not in TOGGLE_SIDES:
                raise ValueError("live-menu %r asks for {toggle} but this staging has no live-toggle side" % cmd[:120])
            cmd = cmd.replace(TOGGLE_MARK, side)
        out.append(cmd)
    return out


LIVE_TIER = re.compile(r"^\s*(?:[-*]\s+)?`?live-tier(?P<cids>(?:\s+[A-Za-z][A-Za-z0-9_]*,?)*)\s*:\s*(?P<tier>[^`#]*?)`?\s*"
                       r"(?:#.*)?$")
ALL = "*"       # live_tiers: the tier of every clause no line of its own names


def live_tiers(text):
    """A live_proofs file -> {clause id or ALL: modset_builder.py tier}. `live-tier: X` is every clause's,
    `live-tier A1, A2: X` those clauses'. ValueError on a line naming more or less than one tier, or a clause (or the
    whole file) given two different tiers: one load is one whole list."""
    got = {}
    for line in (text or "").splitlines():
        m = LIVE_TIER.match(line)
        if not m:
            continue
        words = m.group("tier").replace(",", " ").split()
        if len(words) != 1:
            raise ValueError("a live-tier line names exactly one modset_builder tier, not %r" % m.group("tier"))
        for cid in m.group("cids").replace(",", " ").split() or [ALL]:
            if got.get(cid, words[0]) != words[0]:
                raise ValueError("live-tier gives %s two tiers (%s, %s): one load is one whole list"
                                 % ("the file" if cid == ALL else cid, got[cid], words[0]))
            got[cid] = words[0]
    return got


def clause_tier(text, cid, tiers=None):
    """The tier clause `cid` must run on, or None (any load holding its mods, on Archmagi). ValueError as live_tiers.
    A GREEN-FULL clause is the full list's final check: its callers never send it to a tier."""
    t = live_tiers(text) if tiers is None else tiers
    return t.get(cid) or t.get(ALL)


# LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT (design/RimMandrake/lightspeed_2026-11-06.md section 4 row 2): a clause with no
# live-tier line goes to SteveDesktop too, on a tier named by its mods (modset_builder mods__<tokens>: the build's mods,
# the file's live-mods, the bridge, Gimme Some Slack, all five DLC), so its verdict is a testq row and no staging or LLM
# touches it. Not inferred: a GREEN-FULL clause (the full list's final check), and a file with a live-site line (the
# site is staged with Archmagi's bridge) or a live-without line (a load that must lack a mod: an exclusion no mods__
# name carries). The worker resolves the tier at the job's source_sha, so only a build whose modset_builder knows the
# mods__ form (MODS_TIER_MARK) is inferred; an older build, an unresolvable mod name, or SteveDesktop measuring nothing in
# steve_tries jobs leaves the clause to Archmagi's round (the fallback file, relentless_game.steve_sync).
INFERRED_TIER = "inferred tier: SteveDesktop runs it through testq"
MODS_TIER = "mods__"
MODS_TIER_BASE = MODS_TIER + "base"
MODS_TIER_MARK = "MODS_TIER_PREFIX"     # modset_builder.py at a sha that resolves mods__ tiers holds this name
MODS_TIER_ALWAYS = ("brrainz.rimbridgeserver", "mandrake.rm.gimmesomeslack")    # modset_builder.MODS_TIER_ALWAYS
MODS_TIER_MAX = 160
FALLBACK = os.path.join("live", "steve_fallback.json")


def mods_tier(pids):
    """packageIds -> (the mods__ tier name modset_builder.tier_def decodes back to them, None), or (None, why not).
    Pure. A packageId outside [a-z0-9._], or one whose token would hold `__`, cannot be named."""
    toks = set()
    for p in pids:
        p = str(p).lower()
        if p in MODS_TIER_ALWAYS:
            continue
        if not re.match(r"^[a-z0-9][a-z0-9._]*[a-z0-9]$", p) or "__" in p.replace(".", "_"):
            return None, "packageId %r has no mods__ token" % p
        toks.add(p.replace(".", "_"))
    name = MODS_TIER + "__".join(sorted(toks)) if toks else MODS_TIER_BASE
    if len(name) > MODS_TIER_MAX:
        return None, "%d mods make a tier name of %d chars (max %d)" % (len(toks), len(name), MODS_TIER_MAX)
    return name, None


def inferable(text, cid, level, tiers=None):
    """True when clause `cid` of this live_proofs file goes to SteveDesktop on an inferred tier (the block comment
    above): no tier of its own, not GREEN-FULL, no live-site, live-without, live-menu or live-toggle line in the file.
    ValueError as live_tiers."""
    if level == L.FINAL:
        return False
    if clause_tier(text, cid, tiers):
        return False
    for line in (text or "").splitlines():     # a menu step or a with/without pair is a staging only Archmagi runs
        if SITE_LINE.match(line) or LIVE_WITHOUT.match(line) or LIVE_MENU.match(line) or LIVE_TOGGLE.match(line):
            return False
    return True


def read_fallback(root):
    """{item: {"sha", "clauses", "why", "at"}}: the inferred clauses SteveDesktop gave back to Archmagi for a build."""
    try:
        with open(os.path.join(root, FALLBACK), encoding="utf-8") as f:
            got = json.load(f)
        return got if isinstance(got, dict) else {}
    except (OSError, ValueError):
        return {}


def fell_back(fb, item, sha, cid):
    v = (fb or {}).get(item) or {}
    return bool(v.get("sha")) and (v["sha"].startswith(sha or "-") or (sha or "").startswith(v["sha"])) \
        and bool({cid, "*"} & set(v.get("clauses") or []))     # "*": the build's mods name no tier at all


_INFERS = {}


def sha_infers(books, sha):
    """True when modset_builder.py at `sha` resolves mods__ tiers (MODS_TIER_MARK); cached per sha."""
    if not sha:
        return False
    if sha not in _INFERS:
        r = subprocess.run(["git", "show", "%s:src/RimMandrake/Utils/modset_builder.py" % sha], cwd=books,
                           capture_output=True, text=True, timeout=60)
        _INFERS[sha] = r.returncode == 0 and MODS_TIER_MARK in r.stdout
    return _INFERS[sha]


def text_at(books, item, sha):
    r = subprocess.run(["git", "show", "%s:%s/%s.txt" % (sha, PROOFS_DIR, item)], cwd=books, capture_output=True,
                       text=True, timeout=60)
    return r.stdout if r.returncode == 0 else ""


def in_game(root, item):
    """The game clauses of `item` when the Relentless store holds it in its game phase at prove or stage, not a
    full-list sitting (the only place relentless_game.steve_sync runs, over those clauses only), else []."""
    try:
        with open(os.path.join(root, "store", "items", item, "state.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError):
        return []
    g = st.get("game") or {}
    ok = st.get("status") == "game" and g.get("phase") in ("prove", "stage") and not g.get("full")
    return list(g.get("clauses") or []) if ok else []


def steve_routes(books, root, enabled=True, read_at=None, game_of=None):
    """The predicate candidates() skips with: (item, cid, text, tiers, level) -> True when the clause is SteveDesktop's
    on an inferred tier, judged exactly as steve_sync judges it: the proofs file at the build (steve_sync reads
    proofs_at(item, sha)), the build's modset_builder, the fallback file, and the item in its game phase (an item
    outside one is never sent, so the round keeps it). None when inference is off. read_at/game_of: tests' seams."""
    if not enabled:
        return None
    fb = read_fallback(root)
    read_at = read_at or (lambda item, sha: text_at(books, item, sha))
    game_of = game_of or (lambda item: in_game(root, item))

    def routed(it, cid, text, tiers, level):
        sha = it["built_sha"]
        if fell_back(fb, it["id"], sha, cid) or cid not in game_of(it["id"]) or not sha_infers(books, sha):
            return False
        at = read_at(it["id"], sha)
        try:
            return inferable(at, cid, level)
        except ValueError:
            return False    # a malformed tier at the build: steve_sync holds the item with the reason
    return routed


def live_mods(text, pattern=LIVE_MODS):
    """A live_proofs file -> the mod folders its `live-mods:` and `live-deploy:` lines name (every line, in order, no
    repeats): what the running game must load. pattern=LIVE_DEPLOY: only what it must also hold whole."""
    out = []
    for line in (text or "").splitlines():
        m = pattern.match(line)
        if m:     # a `# ...` tail is a comment, never mod names (LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING review)
            for x in re.split(r"[\s,]+", m.group("mods").split("#", 1)[0]):
                if x and x not in out:
                    out.append(x)
    return out


def companion_line(text):
    """True when a live_proofs file has a `live-companion: JawaBench` line: its proofs call JawaBench tools, so the game
    folder's companion DLL must be built from the build's sources (relentless_live.companion_gap). A build that touched
    the companion's sources owes it without the line (relentless_live.companion_touched). ValueError on a line naming
    anything but JawaBench: the one companion build.py deploys."""
    got = False
    for line in (text or "").splitlines():
        m = LIVE_COMPANION.match(line)
        if m:
            if m.group("what").strip() != "JawaBench":
                raise ValueError("a live-companion line names JawaBench, the one companion, not %r" % m.group("what"))
            got = True
    return got


def names_check(fx, names):
    """relentless_names.check on fx.names_index() -> {"mods", "refused", ...}: every name resolved once, folded sources
    normalised to their composed mod. A fake without names_index passes the names through unchecked."""
    index = fx.names_index() if hasattr(fx, "names_index") else None
    if index is None:
        return {"mods": list(names), "refused": [], "normalized": [], "unverified": []}
    import relentless_names
    return relentless_names.check(names, index)


def infer(fx, text, named, build):
    """relentless_names.needs for the gate (LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT): derived at each gate from the books'
    proofs text and the scripts it runs, never written into the proof. -> the needs dict, or None for a fake without
    names_index (it infers nothing). fx.read_books / fx.read_head, when present, read the scripts and save headers."""
    index = fx.names_index() if hasattr(fx, "names_index") else None
    if index is None:
        return None
    import relentless_names as N
    scripts = N.gather_scripts(text, getattr(fx, "read_books", None) or N.read_books)
    saves = N.gather_saves(text, getattr(fx, "read_head", None) or N.read_head)
    nd = N.needs(text, scripts, named, build, index, saves=saves)
    for a in nd["add"]:     # one of our packageIds plans as its folder: deployed and enabled, as live-mods would have it
        a["mod"] = index.repo_pids.get(str(a["mod"]).lower(), a["mod"])
    return nd


def inferred_rows(nd):
    """needs() -> the run row's record of what the gate added and why: [{"mod", "src", "at"}]."""
    return [{"mod": a["mod"], "src": a["src"], "at": a["at"]} for a in (nd or {}).get("add") or []]


def is_package(name):
    """A `live-mods:` entry that names a mod by packageId (7f.alienworlds, ferny.worldbuilder), not a repo mod folder:
    packageIds always hold a dot; a mod folder rarely does.
    LIVE_MODS_FIX_WORKSHOP_UNNAMEABLE: TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING's clause needed Alien Worlds and
    Worldbuilder, workshop mods a folder-only line could not name, and read "Type not found: PlanetTypeManager" 20 times.
    A packageId is enabled with its dependency closure across the workshop and the game's Mods folder
    (modset_builder.package_closure) and checked in the running load; it is never deployed (it is no tree of ours).
    The dot rule alone read the composed folder RimMandrake.Biomes as a packageId; a dotted name some mod folder holds
    is a folder (relentless_live.is_package, OPS_CHURN_DIAGNOSE_OLLOPOM_JLHV_AJHK)."""
    return L.is_package(name)


def loadable(dirs, mods, shells):
    """The src/<tier>/<dir> names a commit touched -> the mod folders a load must hold. A repo mod or folded source keeps
    its name; a compose shell (BiomesShell) stands for its composed mod (RimMandrake.Biomes); any other dir (Utils,
    bridgetools, rimflow: tooling, no About.xml) is no mod. OPS_CHURN_DIAGNOSE_PLAYER_YGLE_IHKT: 20 game-phase items
    named Utils, bridgetools or BiomesShell, and modlist_swap --enable refused every batch load one of them rode
    ("no About.xml with a packageId"), so PLAYER_START_SITE_1 was held on its riders' names. Pure."""
    return sorted({shells.get(d, d) for d in dirs if d in mods or d in shells})


def folders(mods):
    """The repo mod folders of a mod list: what a deploy plan may name (a packageId is no tree of ours)."""
    return [m for m in mods if not is_package(m)]


def live_deploy(text):
    """A live_proofs file -> the mod folders whose whole tree the build owes the game folder (`live-deploy:`); a
    packageId there owes no tree (is_package) and is only loaded, as on a `live-mods:` line."""
    return folders(live_mods(text, LIVE_DEPLOY))


TERMINAL = ("PASS", "FAIL", "REFUSED")
# OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: relentless_live.run's deploy and running-load gates read the item's mods and
# its build, never the clause, so a clause stopped there speaks for every clause of that build on that game (2026-11-05:
# TAOZIN L1-L3 wrote one "no readable packageId" three times in 17 s, a third of live_measured_pct's window never ran)
ITEM_GATED = "a sibling clause stopped at the item's deploy or load gate"


def item_gate(row):
    """True when a runs.jsonl row stopped at an ITEM-level gate (relentless_live.UNDEPLOYED): no proof ran."""
    return bool(row) and row.get("outcome") in L.NO_VERDICT and "proof_exit" not in row and (
        row.get("why") or "").startswith(L.UNDEPLOYED)


def history(rows):
    """runs.jsonl rows -> {(item, criterion, sha): the row that decides}: a terminal row (PASS, FAIL, REFUSED) stands for
    its build whatever came after it; otherwise the newest row. A void row (relentless_attrib.resume: those rows were
    read through an instrument since repaired) ends every earlier row of its item on its sha."""
    out = {}
    for row in rows:
        if row.get("void") and row.get("item") and row.get("sha"):
            for k in [k for k in out if k[0] == row["item"] and k[2] and (k[2] == row["sha"] or (
                    len(k[2]) >= 7 and len(row["sha"]) >= 7 and (k[2].startswith(row["sha"]) or row["sha"].startswith(k[2]))))]:
                del out[k]
            continue
        if row.get("item") and row.get("criterion"):
            k = (row["item"], row["criterion"], row.get("sha"))
            last = out.get(k, {})
            if not decides(last) or last.get("cut"):     # a cut refusal yields to a later row
                out[k] = row
    return out


def decides(row):
    """A row that stands for its build whatever comes after: PASS, FAIL, REFUSED, a build the game can never run
    (relentless_live.STALE) and a cause that outlived a reload (row `defect`). Rerunning any of them on the same sha can
    only write the same row again (LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD: 18 stale-build rows reran six-hourly)."""
    return bool(row) and (row.get("outcome") in TERMINAL or bool(row.get("defect"))
                          or (row.get("outcome") in L.NO_VERDICT and (row.get("why") or "").startswith(L.STALE)))


def due(last, sha, now, cron=True, game=None, per_game=True, site=None):
    """-> None when this criterion may run now, else why not. `last` is its deciding runs.jsonl row on `sha`, or None.
    cron: the supervisor's own round (truthy) rather than a game phase's round for one item, which has just staged.
    `now` is kept for the callers' shape: no wait here is a clock (PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE).
    game: the running game's start (relentless_live.iso); a reload request made on it stands until another game runs.
    per_game: an undeployed build waits for another game (the cron round); a game phase's own round passes False, its
    staging is what deploys it. site: the clause's `live-site` command, a part of a NOT_ADMITTED row's key
    (relentless_live.admit_waits); None when the caller did not read it."""
    if not last or last.get("sha") != sha:
        return None
    if last.get("outcome") in TERMINAL:
        return "judged on this build"
    if decides(last):
        return "no game can measure this build"
    if per_game and (last.get("why") or "").startswith(L.UNDEPLOYED) and game and last.get("game") == game:
        return "not deployed on this game"      # only a load (the game phase's staging) deploys and enables it
    if (last.get("why") or "").startswith(L.RELOAD) and game and last.get("game") == game:
        return "reload needed"
    # LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: the same game and the same build can only say the same thing again. A final
    # clause read FINAL_WAIT, or a proof that RAN and measured nothing, waits for a new build (a new sha: another `last`)
    # or another game; a game phase's round is no exception (2026-11-03 17:47-18:16Z: GRAFFITI A2/F1/F2 and GENERATOR A2
    # re-ran every 15 min on one game, six UNMEASURED runs that could not differ)
    if game and last.get("outcome") in L.NO_VERDICT:
        why, on = last.get("why") or "", last.get("game")
        if why.startswith(L.FINAL_WAIT) and (on == game or (not on and last.get("at", "") >= game)):
            return WAITS_TIER       # a row before 2026-11-03 has no game: written after this game started, it is its
        if on == game and SAME_GAME_DUD.search(why):
            return DUD_HERE
    # redesign_final G1(c): a NOT_ADMITTED row waits on its key (sha, load, site, harness) and runs the moment one part
    # moves, never later and never never; a transient cause (the harness's read) runs again at once. A game
    # phase's own round (per_game False) stages a deploy gap itself, so only the other causes hold it there
    if game and last.get("outcome") == L.NOT_ADMITTED and (per_game or last.get("admit") != "deploy_gap"):
        held = L.admit_waits(last, sha, game, site)
        if held:
            return held
        if not L.ADMIT.get(last.get("admit"), ("", True))[1]:
            return None
    return route(last, game) if cron and per_game else None     # a game phase's round has just restaged


def route(last, game):
    """The coded route of an UNMEASURED row with no rule above, in place of the 6 h unmeasured_retry_s nap
    (UNMEASURED_ROUTES_WIRE_NO_SIX_HOUR_NAPS): the bridge's or the round's own wall (STOP, BRIDGE_DUD) is not the
    clause's, so it runs in the next round; any other cause the proof wrote on this game and this build can only be
    written again, so it waits for another game (a load, a deploy, a staging) or a new build (another `last`).
    A row with no `game` (before 2026-11-03) counts as this game's when it was written after this game started."""
    if last.get("outcome") not in L.NO_VERDICT or not game:
        return None
    why = last.get("why") or ""
    if any(why.startswith(s) for s in STOP) or BRIDGE_DUD.search(why):
        return None
    on = last.get("game")
    if on == game or (not on and last.get("at", "") >= game):
        return DUD_HERE
    return None


EXACT_TIER = "exact tier: SteveDesktop runs it through testq"


def candidates(items, proofs_of, hist, now, cron=True, game=None, steve=None):
    """-> (todo [(item id, criterion, proof, built sha)], counts {why skipped: n}). Pure apart from proofs_of.
    cron: truthy for the supervisor's round, falsy (0) for a game phase's round for one item, which has just staged.
    proofs_of(item id) -> the text of its live_proofs file, empty when it has none.
    `items` are ledger items in relentless_live.Fx.item's shape (criteria already whole or marked cut)."""
    todo, counts = [], {}

    def skip(why):
        counts[why] = counts.get(why, 0) + 1

    for it in items:
        if it["state"] not in L.TESTABLE or not it.get("built_sha"):
            continue
        crit = {c["id"]: c for c in it.get("criteria") or []}
        owed = [c for c in it.get("outstanding") or [] if c in crit and crit[c]["level"] in L.LIVE_LEVELS]
        if not owed:
            continue
        text = proofs_of(it["id"])
        proofs = proof_lines(text)
        try:
            tiers = live_tiers(text)
        except ValueError:
            tiers = {ALL: "?"}      # malformed: it runs nowhere here; the game phase holds the item with the reason
        # a sibling's item-level gate on this build and this game holds every clause, as it would hold the clause itself
        # (due: "not deployed on this game"); a game phase's round (cron 0) has just staged, so it runs again
        gated = bool(cron) and game and any(
            k[0] == it["id"] and k[2] == it["built_sha"] and item_gate(v) and v.get("game") == game
            for k, v in hist.items())
        for cid in owed:
            if cid not in proofs:
                skip("no proof")
                continue
            if L.owner_look(crit[cid], proofs[cid]):
                skip("owner look")      # his act, not the game's: no run can pass it (..._GAME_LANE_OWNER_LOOK_FAILS)
                continue
            if crit[cid]["level"] != L.FINAL and clause_tier(text, cid, tiers):
                skip(EXACT_TIER)    # SteveDesktop's, through testq: never this game, whatever list it runs
                continue
            if steve and steve(it, cid, text, tiers, crit[cid]["level"]):
                skip(INFERRED_TIER)     # SteveDesktop's on the tier its mods name (steve_routes)
                continue
            last = hist.get((it["id"], cid, it["built_sha"]))
            if last and last.get("cut") and not crit[cid].get("cut"):
                last = None     # refused while cut on the ledger; its prose now holds it whole: run it
            if gated and not decides(last):
                skip("not deployed on this game")
                continue
            why = due(last, it["built_sha"], now, bool(cron), game, per_game=bool(cron),   # a game phase restages
                      site=site_for(text, cid) or "")
            if why:
                skip(why)
                continue
            todo.append((it["id"], cid, proofs[cid], it["built_sha"]))
    return todo, counts


def deploy_args(mods, folded):
    """The item's mod folders -> deploy_custom_mods.py plan arguments covering each. A folder folded into the composed
    biomes mod is planned through --compose biomes, the rest beside it with --with, or alone with --mod."""
    mods = sorted(set(mods))
    targets = {t for t, _k in folded.values()}      # RimMandrake.Biomes itself: the composed mod, planned by --compose
    if any(m in folded or m in targets for m in mods):
        return " ".join(["--compose biomes"] + ["--with %s" % m for m in mods if m not in folded and m not in targets])
    return " ".join("--mod %s" % m for m in mods)


def item_mods(fx, item_id, sha):
    """The build's mod folders: those of the built commit, or, when it touched no shippable mod file, those of every
    commit citing the item (relentless_live.build_shas, PROOF_SHA_FIX_DEPLOYS_NOTHING_TWICE: a proof-only fix landed
    last deployed nothing and checked no running-load gap). Raises ValueError as mods_of does."""
    if item_id is None or not hasattr(fx, "cited"):
        return list(fx.mods_of(sha))
    return sorted({m for s in L.build_shas(fx, sha, item_id) for m in fx.mods_of(s)})


def mod_gap(fx, sha, text, running=True, item=None):
    """What a run of this build would find missing from the game, asked BEFORE a game slot is spent
    (LIVE_MODLIST_ENFORCE_BEFORE_SLOT: 6 of 28 live runs were HORRORS 'UtinniPatches not enabled in ModsConfig',
    GRAFFITI 'not in the running load', DRAWBRIDGE a stale FlowWorks DLL). The build's mods plus its `live-mods:` are
    planned once (deploy_custom_mods.py, read only). -> {"mods", "off": {folder: flag} (NOT DEPLOYED / not enabled in
    ModsConfig), "dll": [stale or missing DLLs in the game folder], "running": why the RUNNING load lacks them or None,
    "error": why the plan could not be read or None}. running=False skips the bridge read (no game, or a staging).
    item: the item built at `sha`, so a proof-only built commit stands for its item's mods (item_mods)."""
    out = {"mods": [], "off": {}, "dll": [], "running": None, "error": None, "unknown": None, "inferred": [], "warn": [],
           "without": [], "conflict": None}
    chk = names_check(fx, live_mods(text))
    out["unknown"] = _refusal(chk["refused"])     # left out of the plan; relentless_game._preflight refuses the item
    try:
        build = item_mods(fx, item, sha)
    except ValueError as e:
        out["error"] = str(e)[:200]
        return out
    nd = infer(fx, text, chk["mods"], build)
    mods = sorted(set(build) | set(chk["mods"]) | {a["mod"] for a in (nd or {}).get("add") or []})
    if nd is not None:
        import relentless_names as N
        out.update(inferred=inferred_rows(nd), warn=[a["mod"] for a in nd["warn"]], without=nd["without"],
                   conflict=N.without_conflict(nd))
    out["mods"] = mods
    if not mods:
        return out
    _plan_into(fx, mods, out)
    if running and not out["error"]:
        out["running"] = fx.running_load_gap(mods)
    return out


def batch_gap(fx, builds):
    """mod_gap for every build riding one load, for ONE deploy plan over their union: [(sha, proofs text[, item])] -> one gap.
    A staging needs only the union (enable_set, dll_mods); planned per item, 17 riders took 17 sequential plans of
    about 140 s over the Windows mount before the tick's 20-minute kill (TICK_SPEED_FIX_GAME_IDLES_WAITING). A build whose
    mods cannot be read rides without them and says so in `error`; the others still plan."""
    out = {"mods": [], "off": {}, "dll": [], "running": None, "error": None, "refused": [], "split": [], "inferred": {},
           "without": []}
    mods, without = set(), {}      # without: {mod: the item that is live-without it}
    for pos, b in enumerate(builds):
        sha, text, item = (tuple(b) + (None,))[:3]
        # LIVE_MODS_ENFORCE_ROLL_CALL_BEFORE_BOARDING: each build's names are resolved BEFORE the union. A rider naming
        # what no mod is drops itself alone (OPS_CHURN_DIAGNOSE_TITANIC_WYZE_DMPL: one rider's RimMandrake.FlowWorks
        # refused the whole batched enable); the leader (pos 0) rides on its valid names, its own preflight refuses it
        chk = names_check(fx, live_mods(text))
        if chk["refused"]:
            out["refused"].append({"item": item, "pos": pos, "why": _refusal(chk["refused"])})
            if pos:
                continue
        try:
            build = item_mods(fx, item, sha)
        except ValueError as e:
            out["error"] = str(e)[:200]
            continue
        nd = infer(fx, text, chk["mods"], build)
        own = set(build) | set(chk["mods"]) | {a["mod"] for a in (nd or {}).get("add") or []}
        mine = set((nd or {}).get("without") or [])
        # LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: a rider needing X never rides with one that is live-without X; staging
        # only enables, so it waits for a load of its own (the leader rides first; its own conflict is its preflight's)
        clash = sorted((own & set(without)) | (mine & mods)) if pos else []
        if clash:
            out["split"].append({"item": item, "pos": pos, "why": "live-without conflict on %s with %s" % (
                ", ".join(clash), ", ".join(sorted({without.get(m) or "the load's other riders" for m in clash})))})
            continue
        mods |= own
        for m in mine:
            without.setdefault(m, item)
        if nd is not None and nd["add"]:
            out["inferred"][item or str(pos)] = inferred_rows(nd)
    out["mods"] = sorted(mods)
    out["without"] = sorted(without)    # the load must LACK these: the staging takes them off (modlist_swap --disable)
    if mods:
        _plan_into(fx, out["mods"], out)
    return out


def _refusal(refused):
    if not refused:
        return None
    import relentless_names
    return relentless_names.refusal(refused)


def _plan_into(fx, mods, out):
    """The one plan over `mods` into a gap's off, dll and error. Headers and DLLs are all a gap reads, so --gate: 35 s
    where the full plan's byte compare and def guard took 260 s of a supervisor tick. A run still gates on the full plan
    (relentless_live.run), so other drifting files are caught there."""
    mods = folders(mods)        # a packageId is loaded (modlist_enable, running_load_gap), never planned
    if not mods:
        return
    rc, plan = fx.deploy_plan(deploy_args(mods, fx.folded()) + " --gate", L.live_rules({})["gate_plan_max_s"])
    if rc not in (0, 1):
        out["error"] = "the deploy plan failed (exit %s): %s" % (rc, (plan or "")[-200:])
        return
    _covered, drift, off = L.plan_sections(plan)
    out["off"] = off
    out["dll"] = sorted({"%s/%s" % (sec, e) if not e.startswith(sec + "/") else e
                         for sec, flag, e in drift if flag != "H" and e.lower().endswith(".dll")})


class RoundFx(L.Fx):
    """relentless_live.Fx plus what a round needs: every item, one plan per args, the lane and the compose manifest."""

    def __init__(self, *a, **kw):
        L.Fx.__init__(self, *a, **kw)
        self._plans = {}

    def canary(self, root, r, now):
        """The live harness's canaries, cached by environment fingerprint (relentless_canary.gate) -> None or why not."""
        import relentless_canary
        return relentless_canary.gate(relentless_canary.ShellFx(self), root, r, now)

    def items(self):
        import model
        out = []
        for it in model.replay(model.read()).items.values():
            if it.state not in L.TESTABLE:
                continue
            out.append({"id": it.id, "state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                        "criteria": [L.whole_criterion(c, self.prose(it.id)) for c in it.criteria or []],
                        "outstanding": list(it.outstanding or [])})
        return out

    def proofs(self, item_id):
        p = os.path.join(self.books, PROOFS_DIR, item_id + ".txt")
        if not os.path.isfile(p):
            return ""
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()

    def deploy_plan(self, args, timeout):
        if args not in self._plans:
            self._plans[args] = L.Fx.deploy_plan(self, args, timeout)
        return self._plans[args]

    def folded(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return L.with_shell(deploy_custom_mods.folded(), L.compose_shells(deploy_custom_mods.SRC_ROOT))

    def has_mod(self, mod):
        """A mod folder the repo ships, by the deploy tool's own discovery (a folded mod counts: `--compose` plans it)."""
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return mod in deploy_custom_mods.folded() or mod in deploy_custom_mods.mod_dirs()

    def mod_names(self):
        """-> ({repo mod folder or folded source}, {compose shell source: composed target}), read once per RoundFx."""
        if getattr(self, "_mod_names", None) is None:
            sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
            import biomes_compose
            import deploy_custom_mods as D
            m = biomes_compose.load_manifest(D.SRC_ROOT) or {}
            shells = {m["shell"]["source"]: m["target"]} if (m.get("shell") or {}).get("source") else {}
            self._mod_names = (set(D.mod_dirs()) | set(D.folded()), shells)
        return self._mod_names

    def names_index(self):
        """relentless_names.default_index: what this machine can load, for the one name resolver."""
        import relentless_names
        return relentless_names.default_index()

    def mods_of(self, sha):
        return loadable({m for m, _ in L.game_files(self.touched(sha), self.shippable)}, *self.mod_names())


def read_rows(path):
    rows = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    return rows


def plan(fx, root, r, now, only=None, game=None):
    """-> (todo, counts) for this moment. Read-only. `only`: one item, the supervisor's game phase for it
    (relentless_game.py): it has just staged the game, so an UNMEASURED row is no reason to wait."""
    hist = history(read_rows(os.path.join(root, "live", "runs.jsonl")))
    items = [it for it in fx.items() if only is None or it["id"] == only]
    import relentless_game
    c = relentless_game.cfg(r)
    steve = (steve_routes(fx.books, root, c.get("steve_infer") and c.get("enabled"))
             if getattr(fx, "books", None) else None)
    return candidates(items, fx.proofs, hist, now, 0 if only else 1, game, steve)


def run_round(fx, root, r, now=None, max_items=None, run=L.run, only=None):
    """One sitting. -> the round's summary row (also appended to <root>/live/rounds.jsonl)."""
    now = time.time() if now is None else now
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    summary = {"at": L.iso(now), "runs": []}

    def done(why):
        summary["why"] = why
        summary["ended"] = L.iso(max(now, time.time()))     # `at` is the start: bottleneck_measure reads both
        with open(os.path.join(root, "live", "rounds.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, sort_keys=True) + "\n")
        return summary

    started = fx.game_started()
    if started is None:
        return done("no running game")
    sick = fx.canary(root, r, now) if hasattr(fx, "canary") else None     # in THIS process: the service's own context
    if sick:
        summary["canary"] = sick
        return done("stopped: %s" % sick[:300])
    todo, counts = plan(fx, root, r, now, only, L.iso(started))
    summary.update(eligible=len(todo), skipped=counts, **({"only": only} if only else {}))
    folded, ran, cap, gated = None, 0, len(todo) if max_items is None else max_items, set()
    for k, (item_id, cid, proof, sha) in enumerate(todo):     # the cap counts runs: a skip never starves the items behind it
        if ran >= cap:
            break
        if (item_id, sha) in gated:     # its gate is the build's, not the clause's: one row says it for all
            summary["skipped"][ITEM_GATED] = summary["skipped"].get(ITEM_GATED, 0) + 1
            continue
        try:
            mods = item_mods(fx, item_id, sha)
        except ValueError as e:
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "UNMEASURED", "why": str(e)[:200]})
            continue
        if folded is None:
            folded = fx.folded()
        ran += 1
        text = fx.proofs(item_id)
        trees = live_deploy(text)
        declared = live_mods(text)
        nd = infer(fx, text, names_check(fx, declared)["mods"], mods)
        need = declared + [a["mod"] for a in (nd or {}).get("add") or [] if a["mod"] not in declared]
        env = {"mods": sorted(set(mods) | set(need)), "inferred": inferred_rows(nd),
               "without": (nd or {}).get("without") or []}     # what environment produced this verdict
        try:
            comp = {"companion": True} if companion_line(text) else {}
        except ValueError as e:
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "UNMEASURED", "why": str(e)[:200]})
            continue
        try:    # GAMEENV_FIX_PROOFSITE_0DB67BE7_ITEMS_WAIT: its exit 2 asks for its own staging (relentless_live.MENU_WAIT)
            if live_menu(text) or live_toggle(text):
                comp["menu"] = True
        except ValueError:      # a malformed line: the game phase holds it (relentless_game.menu_bound); it is bound
            comp["menu"] = True
        row = run(fx, root, item_id, cid, proof, deploy_args(list(mods) + trees, folded), r, now=time.time(),
                  needs=need, site=site_for(text, cid), trees=trees,
                  **dict(comp, **({"env": env} if nd is not None else {})))
        summary["runs"].append({k: row.get(k) for k in ("item", "criterion", "outcome", "why", "sha")})
        if item_gate(row):
            gated.add((item_id, sha))
        why = row.get("why") or ""
        if row["outcome"] in L.NO_VERDICT and (any(why.startswith(s) for s in STOP) or BRIDGE_DUD.search(why)):
            summary["left"] = len(todo) - k - 1     # clauses this round did not run into the same wall: the next round has them
            return done("stopped: %s" % why[:200])
    return done("done")


def deployed(fx, item_id, text, lint=False):
    """`deployed --item`: the proof of a deploy item -> (exit, line). 0 every `live-deploy:` tree is what the game folder
    holds; 1 one is not; 2 it could not measure (no such line, or a plan that did not read). lint reads no game folder, for
    the blind offline check: the line names mods the repo has, and the file has a proof line that runs this."""
    trees = live_deploy(text)
    if not trees:
        return 2, "%s/%s.txt has no live-deploy line" % (PROOFS_DIR, item_id)
    if lint:
        lost = [m for m in trees if not fx.has_mod(m)]
        if lost:
            return 1, "no such mod in the repo: %s" % ", ".join(lost)
        if not [c for c in proof_lines(text).values() if "relentless_live_round.py deployed" in c]:
            return 1, "no live-proof line runs `relentless_live_round.py deployed`"
        return 0, "OK %s names %s" % (item_id, ", ".join(trees))
    rc, plan = fx.deploy_plan(deploy_args(trees, fx.folded()), L.live_rules({})["plan_max_s"])
    why = L.deploy_gap([], rc, plan, trees, fx.folded())
    if why:
        return (2 if why.startswith("the deploy plan") else 1), why
    return 0, "OK the game folder holds %s" % ", ".join(trees)


def census(rows):
    """runs.jsonl rows -> what they spent and why (PROOF_RERUNS_TAME_UNMEASURED_REPEATS). `took_bridge` is the rows that
    held the game (a log exists); `repeats` the UNMEASURED rows that said what their (item, criterion, build) had already
    said, the waste the cap exists to end, so it should fall to near 0 on rows written since the cap."""
    out = {"rows": len(rows), "from": rows[0].get("at") if rows else None, "to": rows[-1].get("at") if rows else None,
           "outcomes": {}, "took_bridge": 0, "took_bridge_verdict": 0, "unmeasured": 0, "repeats": 0}
    causes, items, seen = {}, {}, set()
    for row in rows:
        o = row.get("outcome") or "?"
        out["outcomes"][o] = out["outcomes"].get(o, 0) + 1
        if row.get("log"):
            out["took_bridge"] += 1
            out["took_bridge_verdict"] += o in ("PASS", "FAIL")
        if o != "UNMEASURED":
            continue
        out["unmeasured"] += 1
        key = row.get("cause") or L.cause(row.get("why"))
        causes[key] = causes.get(key, 0) + 1
        one = (row.get("item"), row.get("criterion"), row.get("sha"), key)
        if one in seen:
            out["repeats"] += 1
            items[row.get("item")] = items.get(row.get("item"), 0) + 1
        seen.add(one)
    out["causes"] = sorted(([n, k] for k, n in causes.items()), key=lambda x: (-x[0], x[1]))
    out["repeating_items"] = sorted(([n, k or "?"] for k, n in items.items()), key=lambda x: (-x[0], x[1]))
    return out


def wake_supervisor(root, spawn=subprocess.Popen):
    """The round is over and the game is free: mark it, and start `relentless.py game-next`. The mark is what a running tick
    takes between its steps. Never the round's failure: a wake that does not happen costs the wait for the next tick."""
    try:
        os.makedirs(os.path.join(root, "store"), exist_ok=True)
        with open(os.path.join(root, "store", "game_wake"), "w", encoding="utf-8") as f:
            f.write(L.iso(time.time()))
        spawn(["python3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless.py"), "game-next"],
              env=dict(os.environ, RELENTLESS_ROOT=root), stdin=subprocess.DEVNULL, start_new_session=True)
    except (OSError, ValueError) as e:
        print("wake_supervisor: %s" % e)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("eligible", help="what a round would try now, and the counts of what it would skip")
    p = sub.add_parser("round", help="one sitting: run every due criterion that has a proof (--max bounds it)")
    p.add_argument("--max", type=int, default=None)
    p.add_argument("--item", help="this item only, no unmeasured wait: the supervisor's game phase")
    p = sub.add_parser("deployed", help="the proof of a deploy item: exit 0 its live-deploy trees are in the game folder")
    p.add_argument("--item", required=True)
    p.add_argument("--lint", action="store_true", help="offline: the line names real mods and a proof line runs this")
    p = sub.add_parser("census", help="runs.jsonl sorted by cause: what the rows spent, what repeated")
    p.add_argument("--last", type=int, default=300, help="the newest N rows")
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or L.RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    if a.cmd == "census":
        path = os.path.join(root, "live", "runs.jsonl")
        if not os.path.exists(path):        # never "no rows": this instrument cannot see
            print("UNMEASURED: no %s" % path, file=sys.stderr)
            return 2
        print(json.dumps(census(read_rows(path)[-a.last:]), indent=1, sort_keys=True))
        return 0
    fx = RoundFx(seat=r.get("seat") or "BENCH")
    if a.cmd == "deployed":
        code, line = deployed(fx, a.item, fx.proofs(a.item), a.lint)
        print(line)
        return code
    if a.cmd == "eligible":
        started = fx.game_started()     # the round's own view: what this game already said stays skipped
        todo, counts = plan(fx, root, r, time.time(), game=L.iso(started) if started else None)
        print(json.dumps({"eligible": [list(t[:3]) for t in todo], "skipped": counts}, indent=1, sort_keys=True))
        return 0
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    with open(os.path.join(root, "live", "round.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("a round is running")
            return 0
        summary = run_round(fx, root, r, max_items=a.max, only=a.item)
        print(json.dumps(summary, indent=1, sort_keys=True), flush=True)
    if summary.get("runs"):     # a round that ran nothing held no game: the next tick is its wake (no empty-round loop)
        wake_supervisor(root)   # outside round.lock: the proof it starts takes that lock
    return 0


if __name__ == "__main__":
    sys.exit(main())
