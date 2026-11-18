"""proof_lines.py -- the live-proof lines of an item (proof_lines, site_for, live_mods, folders, clause_tier, mods_tier): what each mod proof and modcheck reads to know which proof runs on which mod list.

Moved verbatim from rimflow/relentless_live_round.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proof_lint as L     # noqa: E402

# Bare, or wrapped whole in one pair of Markdown backticks; a bare command keeps its own backticks (echo `date`).
LINE = (r"^\s*(?:[-*]\s+)?(?:`{verb}\s+(?P<cid1>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd1>[^`\s][^`]*?)`"
        r"|{verb}\s+(?P<cid2>[A-Z]{{1,3}}\d{{1,3}})\s*:\s*(?P<cmd2>\S.*?))\s*$")
PROOF_LINE = re.compile(LINE.format(verb="live-proof"))
# `live-site <CID>: <cmd>`: what makes the map or save the proof reads, run first with the bridge held (relentless_live)
SITE_LINE = re.compile(LINE.format(verb="live-site"))
PROOFS_DIR = "infrastructure/state/live_proofs"


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
# STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS: `live-menu: <cmd>` is run by the staging once the load reaches the main menu
# (the bridge token) and BEFORE any game starts: a sample a map would spoil (VRAM, private bytes). `{toggle}` in it is
# this staging's live-toggle side. `live-toggle: <mod>` asks for a pair of loads, one with the mod and one without it:
# the item's stagings alternate sides (toggle_side), it stages alone, and the without side refuses a list holding the mod.
LIVE_MENU = re.compile(r"^\s*(?:[-*]\s+)?(?:`live-menu\s*:\s*(?P<cmd1>[^`\s][^`]*?)`|live-menu\s*:\s*(?P<cmd2>\S.*?))\s*$")
LIVE_TOGGLE = re.compile(r"^\s*(?:[-*]\s+)?`?live-toggle\s*:\s*(?P<mods>[^`#]*?)`?\s*(?:#.*)?$")


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
MODS_TIER = "mods__"
MODS_TIER_BASE = MODS_TIER + "base"
MODS_TIER_MARK = "MODS_TIER_PREFIX"     # modset_builder.py at a sha that resolves mods__ tiers holds this name
MODS_TIER_ALWAYS = ("brrainz.rimbridgeserver", "mandrake.rm.gimmesomeslack")    # modset_builder.MODS_TIER_ALWAYS
MODS_TIER_MAX = 160


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


def folders(mods):
    """The repo mod folders of a mod list: what a deploy plan may name (a packageId is no tree of ours)."""
    return [m for m in mods if not is_package(m)]


def live_deploy(text):
    """A live_proofs file -> the mod folders whose whole tree the build owes the game folder (`live-deploy:`); a
    packageId there owes no tree (is_package) and is only loaded, as on a `live-mods:` line."""
    return folders(live_mods(text, LIVE_DEPLOY))
