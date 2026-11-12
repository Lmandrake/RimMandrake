#!/usr/bin/env python3
"""
gm_blackboard_shadow.py -- GM_BLACKBOARD_SHADOW_M4_1 + CATHEDRAL_REGARD_BLACKBOARD_1

M4's "external blackboard" (`design/Jawa/build_plan.md` §4), SHADOW MODE ONLY:
a Python state machine, driven by polled bridge reads, that tracks Imperial
Heat, the orbital-detection timer, and the dark-tile pause -- and logs what
each WOULD fire. It fires nothing: no incident, no letter, no save write, no
debug action. Read-only by construction (see READ_TOOLS / safe_call below),
not by discipline.

CATHEDRAL_REGARD_BLACKBOARD_1 extends this SAME process/poll (not a sibling
script) with the Cathedral Regard counter, the WARY/TOLERATED/VOUCHED/
REVEALED stage machine, and the §6.1 exposure-pressure number --
`design/Jawa/cathedral_concealment_arc_spec.md` §0/§1/§2/§4/§6.1. Extending
in place, rather than forking a sibling reading this file's JSONL log, was a
deliberate choice: Regard's Heat-near-Cathedral input needs the EXACT same
Heat float this file already computes per poll, in the same tick window --
a sibling tailing the log would either duplicate the Heat computation
(drift risk) or lag a full poll behind it. The spec's own phrasing ("GM
external blackboard alongside Imperial Heat and Hutt Interest") reads as
one blackboard, more fields, not two blackboards.

CATHEDRAL_EXPOSURE_COMPLETION_1 extends the SAME process/poll again (item 8
of the same build decomposition) with the completion chain that items 1-7
only set up the pressure for: a full-discovery threshold ABOVE go-dark that
can only fire after at least one go-dark flip this run (structural sequencing
guard, not a flag -- go-dark resets exposure_pressure to 0.0 the poll it
fires, so full discovery always needs a later poll's re-accumulation, which
is what makes "demotion/dark precedes it" true by construction); a small
ordered "losing battle" fall-stage register, one witnessed stage advanced per
poll (§P register, no §GM truth -- bans 1/2/3/6 checked line-by-line, same
discipline RUST_CATHEDRAL_MECHANICS_1's own droid-commentary pass used before
item 3's linter existed); a warzone posture flip (Card 1, owner-ruled
2026-09-13) reconciled against faction-13's own bans/hysteresis by SCOPE, not
by softening either ruling (see compute_warzone_posture's docstring); a
priced, refusable Hutt-extraction mechanism riding the kyber §4 fixer lane's
existing hutt_interest/hutt_goodwill numbers (mechanism only -- ending
ratification is CAMPAIGN_STORY_SITTING_1's); and a gravship mourning
register, ship-adjacent text kin to A1's dead-Rakatan-band receiver lore.
Every fall and mourning string is gated by item 3's linter
(src/RimMandrake/RustCathedral/cathedral_arc_lint.py) at stage -1, the
pre-reveal rules, since the fall can come before or after the reveal:
selftest_gm_cathedral_fall.py runs it. --disable-cathedral-fall turns the
whole completion chain off; the rest of the blackboard is unchanged.

CATHEDRAL_MISSION_BOON_OFFERS_1 adds the Cathedral's favours to the same poll
(advance_cathedral_offers): Assailant-register missions offered at TOLERATED
and up through the enclave and Utinni channels, gravtech boons at VOUCHED
only while Heat is under each boon's own ceiling, both closed (and held shut
for CATHEDRAL_FAVOURS_DARK_HOLD_TICKS) by a go-dark flip. The offers, their
text and the boons' Heat ceilings are read from the shipped defs in
src/RimUtinni/CathedralPass (load_cathedral_offer_catalogue); mission
completions are read off the quest list (jawa/quest_lifecycle, list only)
and feed Regard, never Heat (K2). The offer path calls no LLM.
selftest_rustcathedral_offers.py drives it; cathedral_offer_letters.py turns
a log into the letters the player would read.

Inputs (cross-checked against the specs that consume this blackboard):
  - kyber/mindstone sales           design/Jawa/kyber_trade_plot_spec.md §2/§3
  - Hutt Cartel goodwill            kyber_trade_plot_spec.md §4
  - Cathedral (faction 13) goodwill design/Jawa/cathedral_concealment_arc_spec.md §2
  - Cathedral-ground presence       cathedral_concealment_arc_spec.md §1/§2
  - dark-tile biome                 design/Jawa/build_plan.md §2/§4 ("the dark-tile pause")
  - anomaly (bolt-shed/eel) sales   cathedral_concealment_arc_spec.md §2 (card A5, by volume)
  - trader-pawn presence            corroborating evidence only (see _sale_heat's
                                     sold-vs-crafted caveat, restated below)
  - Cathedral mission quests        jawa/quest_lifecycle action=list (ended
                                     RUT_CathedralAssailantMission_* quests)
  - story-flag hooks (missions completed BEFORE this run, restore choice,
    misdirection quest, the reveal beat) -- optional --story-flags-file; NO
    live bridge signal exists for the last three yet, so in a run with no
    file passed they sit at their honest default of "no signal" -- see the
    module-level KNOWN GAPS note near ShadowBlackboard.

State lives ONLY in this process's own JSONL log (`--log`), never in the save
-- which is also how this sidesteps `enrichment_agents.md` §7.1's reload-
survival unknown: an external blackboard has nothing to lose on reload,
because nothing was ever written into the save to begin with (M0's answer,
reused per this item's brief -- not re-derived).

Run:
    python.exe gm_blackboard_shadow.py --polls 20 --tick-step 2000
    python.exe gm_blackboard_shadow.py --polls 20 --exposure-godark-threshold 8   # demo the go-dark flip
    python3 gm_blackboard_shadow.py --fixture fixtures/cathedral_offers_ordinary_play.json --log /tmp/x.jsonl

A live run requires the bridge taken (`rimflow bridge take`) and a live game
loaded; --fixture (offline/fixture mode, FixtureBridge) needs neither.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

# ---------------------------------------------------------------------------
# Read-only-by-construction gate. Any tool name not in READ_TOOLS is refused
# by safe_call() before the bridge is even asked -- this is the mechanism
# that makes "shadow mode" a property of the code, not a promise about it.
# TIME_TOOLS is a separate, explicitly-authorized category: step_game_ticks
# advances simulation ticks WITHOUT unpausing (rimbridge skill, capability-
# matrix.md: "advances it without unpausing -- no raid risk") so the state
# machine can observe real signal across a stretch of play. It writes no
# save, fires no incident, sends no letter -- it only lets time pass, which
# is what a paused game sitting idle would eventually need anyway.
# ---------------------------------------------------------------------------
READ_TOOLS = frozenset({
    "rimworld/get_game_info",
    "jawa/map_info",
    "jawa/list_factions",
    "jawa/list_things",
    "jawa/get_defs",
    # CATHEDRAL_REGARD_BLACKBOARD_1: read-only "in effect" (JawaBenchTradeProbeTools.cs
    # own header -- opens a headless TradeSession, reads prices, closes it again before
    # returning, exactly as vanilla closes a dialog; refuses rather than clobbers when a
    # real trade dialog is open). Used only as corroborating evidence for whether a trade
    # partner was even present on a poll where a kyber/anomaly count dropped -- it does
    # NOT resolve the sold-vs-crafted ambiguity (no trade-transaction-log tool exists on
    # the bridge; confirmed absent -- see JawaBenchTradeExecuteTools.cs, which EXECUTES
    # trades and is correctly excluded from this allowlist entirely, dryRun default or not).
    "jawa/trade_price_probe",
    # CATHEDRAL_MISSION_BOON_OFFERS_1: the quest list, for which Cathedral missions were accepted and which ended
    # in success (a completion is a Regard input). The same tool also accepts and ends quests, so it is allowed
    # ONLY with action='list' (READ_ONLY_PARAMS below); safe_call refuses any other action before the bridge is asked.
    "jawa/quest_lifecycle",
})
# A tool that both reads and acts is read-only here only with these exact parameter values.
READ_ONLY_PARAMS = {"jawa/quest_lifecycle": {"action": "list"}}
TIME_TOOLS = frozenset({"rimworld/step_game_ticks"})
ALLOWED_TOOLS = READ_TOOLS | TIME_TOOLS


def safe_call(rb, tool, params=None, check=True):
    if tool not in ALLOWED_TOOLS:
        raise RuntimeError(
            "gm_blackboard_shadow refuses to call %r -- not in the "
            "read-only/time-advance allowlist. Shadow mode is read-only "
            "by construction; extend ALLOWED_TOOLS deliberately, never "
            "ad hoc." % tool
        )
    for key, required in READ_ONLY_PARAMS.get(tool, {}).items():
        if (params or {}).get(key) != required:
            raise RuntimeError("gm_blackboard_shadow refuses %s with %s=%r -- only %s=%r is read-only."
                               % (tool, key, (params or {}).get(key), key, required))
    return rb.call(tool, params or {}, check=check)


# ---------------------------------------------------------------------------
# Tracked inputs -- defNames confirmed live against the current mod list
# (2026-09-13; kyber donor mod active, mindstone not yet absorbed -- see
# kyber_trade_plot_spec.md §1). RUT_Mindstone is polled defensively: if it
# resolves later (post-absorption), it starts contributing with no code
# change needed here.
# ---------------------------------------------------------------------------
KYBER_FAMILY_DEFNAMES = ["Force_KyberCrystal", "RUT_Mindstone"]
HUTT_CARTEL_FACTION = "RUT_Jawa_HuttCartel"
CATHEDRAL_FACTION = "Mechanoid"  # faction 13, "the Forgotten Arsenal" (patch, label only)

# v1 heuristic dark-biome set -- perpetual-night / covered biomes that pause
# the orbital-detection clock per build_plan.md §2/§4's "dark-tile pause".
# Confirmed resolvable BiomeDefs on the current mod list (2026-09-13).
DARK_BIOMES = {
    "Glowforest",
    "BMT_CrystalCaverns",
    "BMT_EarthenDepths",
    "BMT_FungalForest",
}

# CATHEDRAL_REGARD_BLACKBOARD_1 -- the "anomaly" sold by volume, not buyer
# (cathedral spec §2 card A5): bolt-shed curiosities + eel-catch, both
# "salable, both watched" (kit spec, the_rust_cathedral.md §"watched"; the
# eel ThingDef confirmed at rust_cathedral_kit_spec.md §RM_CoolantEelCatch /
# RM_BoltShedCuriosity).
ANOMALY_DEFNAMES = ["RM_BoltShedCuriosity", "RM_CoolantEelCatch"]

# GM tuning constants -- placeholders for shadow-mode observation only.
# Exact constants are explicitly "M4 GM-layer tuning" per kyber spec §3;
# nothing here is a ruled number, just enough to produce a legible log.
# CATHEDRAL_REGARD_BLACKBOARD_1's own additions below inherit the same
# "GM tuning owns numbers" disclaimer (this item's own criteria line).
HEAT_PER_KYBER_SOLD = 8.0          # sublinear via sqrt(qty), see _sale_heat()
HEAT_DECAY_PER_POLL = 0.4          # slow cool-down absent new sales
HUTT_INTEREST_PER_KYBER_SOLD = 3.0
HUTT_INTEREST_DECAY_PER_POLL = 0.15
CATHEDRAL_REGARD_DECAY_TOWARD_ZERO = 0.05
CATHEDRAL_REGARD_LOSS_PER_KYBER_SALE = 5.0   # origin canon: every sale is exposure
CATHEDRAL_REGARD_LOSS_HEAT_NEAR = 0.5        # per poll, when Heat is high AND on Cathedral ground
CATHEDRAL_REGARD_GAIN_LOW_HEAT_NEAR = 0.2    # per poll, when Heat is low/falling AND on Cathedral ground
HEAT_HIGH_BAND = 40.0
HEAT_LOW_BAND = 10.0
ORBITAL_TIMER_START_TICKS = 60_000           # ~1 game day, placeholder
ORBITAL_TIMER_DRAIN_PER_POLL_HIGH_HEAT = 3_000
ORBITAL_TIMER_DRAIN_PER_POLL_LOW_HEAT = 200

# --- CATHEDRAL_REGARD_BLACKBOARD_1: Regard §2 additions (up) -----------------
CATHEDRAL_REGARD_GAIN_MANNERS_PROXY_PER_CLEAN_POLL = 0.1
# "sustained good conduct on Cathedral ground" per arc §2/§1 -- the true input
# is the kit's band history (RM_MapComponent_BiomeAttitude.currentBand), which
# NO bridge [Tool] exposes today (checked JawaBenchMapInfoTools.cs and every
# other BridgeTools file -- no Attitude/Band tool exists). This is a
# documented, honestly-labeled PROXY (consecutive clean polls: no sale, no
# goodwill drop), not the kit signal itself -- see KNOWN GAPS below and the
# record's own "manners_proxy_used" field, always true while this gap stands.
CATHEDRAL_REGARD_CLEAN_STREAK_TOLERATED_FLOOR = 5
CATHEDRAL_REGARD_GAIN_ZERO_SALE_CREDIT_PER_POLL = 0.05   # arc §2: zero sales IS a standing credit, distinct from "no loss"
CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION = 4.0           # per Assailant-register mission (quest list, or story flag for earlier ones)
CATHEDRAL_REGARD_GAIN_RESTORE_CHOICE = 30.0              # arc §2: "the single largest gain"; §4 pricing owned elsewhere
CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS = 6.0         # item 5's own beat (card A4)
# --- Regard §2 additions (down) ---------------------------------------------
CATHEDRAL_REGARD_LOSS_SACRILEGE_GOODWILL_RATIO = 1.0     # "one act, two ledgers" -- mirrors a goodwill DROP 1:1
CATHEDRAL_REGARD_LOSS_ANOMALY_BULK_SALE = 3.0            # per bulk-volume threshold crossing (A5)
CATHEDRAL_ANOMALY_BULK_VOLUME_THRESHOLD = 20             # cumulative units before "bulk" draws eyes (A5 placeholder)
# --- Stage machine (§1) thresholds ------------------------------------------
CATHEDRAL_STAGE_TOLERATED_REGARD_FLOOR = 15.0
CATHEDRAL_STAGE_VOUCHED_REGARD_FLOOR = 40.0
CATHEDRAL_STAGE_VOUCHED_MISSIONS_REQUIRED = 3
CATHEDRAL_STAGE_DEMOTE_VOUCHED_FLOOR = 30.0   # regard below this: VOUCHED -> TOLERATED
CATHEDRAL_STAGE_DEMOTE_TOLERATED_FLOOR = 10.0  # regard below this: TOLERATED -> WARY
CATHEDRAL_STAGE_LABELS = ["WARY", "TOLERATED", "VOUCHED", "REVEALED"]
# --- Exposure pressure (§6.1) ------------------------------------------------
CATHEDRAL_EXPOSURE_GAIN_HEAT_NEAR = 1.0
CATHEDRAL_EXPOSURE_GAIN_SALE_VOLUME_PER_KYBER = 0.5
CATHEDRAL_EXPOSURE_GAIN_ANOMALY_BULK_CROSSING = 4.0
CATHEDRAL_EXPOSURE_GAIN_PURSUIT_EVENT = 15.0   # Act II+ pursuit event resolving on Cathedral ground (no live signal; demo hook only)
CATHEDRAL_EXPOSURE_DECAY_PER_POLL = 0.3
CATHEDRAL_EXPOSURE_GODARK_THRESHOLD = 50.0     # placeholder; --exposure-godark-threshold overrides for a cheap demo run

# --- CATHEDRAL_EXPOSURE_COMPLETION_1 (item 8): full-discovery + fall chain +
# warzone flip + priced Hutt extraction + mourning register. Every numeric
# constant here is GM tuning, same disclaimer as every constant above it --
# nothing is a ruled number, only the RULED SHAPE (A6, Card 1) is authored.
CATHEDRAL_FULL_DISCOVERY_THRESHOLD = 90.0   # must exceed the go-dark threshold; --exposure-full-discovery-threshold overrides
# The "losing battle" register -- §P discipline (observed behaviour only,
# never §GM truth): no line asserts the Cathedral is alive, explains the
# droids' mercy (ban 2), tells a Sentinel-raid-against-the-player story
# (ban 3), or describes the deep-drill response (ban 6). Checked line by
# line by cathedral_arc_lint.py (selftest_gm_cathedral_fall.py). One witnessed
# stage fires per poll once full discovery starts -- "witnessed, not
# narrated" (item 8's own spec line).
CATHEDRAL_FALL_STAGES = [
    {
        "id": "first_tremors",
        "letter": "Word comes in fragments: distant detonations out past "
                  "the rust plates, then silence, then more. Nobody who was "
                  "near it says exactly what they saw.",
    },
    {
        "id": "roads_empty",
        "letter": "The droid pilgrims that once crossed toward the old "
                  "works on schedule simply stop. The road sits empty for "
                  "the first time anyone can remember.",
    },
    {
        "id": "hum_silent",
        "letter": "For the first time anyone can recall there is no hum at "
                  "all -- not the calm drone, not the alarm, nothing. The "
                  "silence is worse than any of the bands ever were.",
    },
    {
        "id": "the_fall",
        "letter": "The rust plates do not answer anymore. Whatever held on "
                  "out there has stopped holding on. The planet is a "
                  "warzone again, and nobody profits from asking why.",
    },
]
# The gravship mourning register (item 8's own bullet) -- ship-adjacent
# surfaces only, kin to A1's dead-Rakatan-band receiver lore (the Utinni
# "feels" a frequency nobody else listens on); same §P discipline as the
# fall stages above -- observed ship behaviour, never an explanation of what
# it means or confirmation that anything out there was ever alive.
CATHEDRAL_MOURNING_REGISTER = [
    "The ship's comms scan a frequency it has watched for months. Nothing "
    "answers back anymore.",
    "For the first night since planetfall the gravdrive runs a half-tone "
    "flat, and no engineer aboard can find why.",
    "Something the crew never had a word for used to sit in the static. It "
    "isn't there now.",
]
# --- CATHEDRAL_MISSION_BOON_OFFERS_1 (arc §1/§3 bullet 3): the offer gate. Missions open at TOLERATED (1) and up,
# gravtech boons at VOUCHED (2) and up, each boon only while Imperial Heat is at or under its own heatCeiling (read
# from the boon's def, RUT_CathedralBoonExtension), both closed by the conduct posture a go-dark flip forces to WARY.
# Gated on the CONDUCT posture, never on effective_stage: the reveal is knowledge, not standing. Cadence numbers are
# GM tuning in game ticks, so a poll's tick step does not change how often the player is asked.
CATHEDRAL_MISSION_MIN_POSTURE = 1
CATHEDRAL_BOON_MIN_POSTURE = 2
CATHEDRAL_MISSION_OFFER_EXPIRY_TICKS = 3 * 60_000   # = the quests' expireDaysRange floor (3~4 days)
CATHEDRAL_MISSION_REOFFER_GAP_TICKS = 5 * 60_000    # quiet days between one request resolving and the next
CATHEDRAL_BOON_ANY_GAP_TICKS = 3 * 60_000           # never two gifts within three days, whichever they are
# A gift is the place answering the clan's conduct, not a fee for a cull: none lands within two days of a completed
# mission, so the two never arrive together and read as payment (second-model test pass, 2026-11-11).
CATHEDRAL_BOON_AFTER_COMPLETION_GAP_TICKS = 2 * 60_000
# (each boon's own re-offer interval is its def's reofferDays: the rarer the gift, the longer it waits)
# After a go-dark flip the stage machine lets posture re-climb as soon as Regard and a short clean streak allow
# (item 1's hysteresis: Regard is not erased), which on its own would reopen every favour a day or two after the
# Empire landed on Cathedral ground. Arc §6.1: "it hides from the player again". So the favours stay shut for
# this long after the flip, whatever the posture does meanwhile.
CATHEDRAL_FAVOURS_DARK_HOLD_TICKS = 10 * 60_000
CATHEDRAL_MISSION_QUEST_PREFIX = "RUT_CathedralAssailantMission_"
CATHEDRAL_FAVOUR_DEFS = (
    Path(__file__).resolve().parents[2] / "RimUtinni" / "CathedralPass" / "Defs" / "QuestScriptDefs"
    / "RUT_CathedralAssailantMissions.xml",
    Path(__file__).resolve().parents[2] / "RimUtinni" / "CathedralPass" / "Defs" / "IncidentDefs"
    / "RUT_CathedralFavours.xml",
)

HUTT_EXTRACTION_MIN_INTEREST = 20.0              # gates the offer on the fixer channel existing (kyber §4b/c)
HUTT_EXTRACTION_BASE_PRICE = 100_000.0           # silver, GM-tuning placeholder
HUTT_EXTRACTION_PRICE_DISCOUNT_PER_INTEREST = 400.0
HUTT_EXTRACTION_PRICE_DISCOUNT_PER_GOODWILL = 300.0
HUTT_EXTRACTION_PRICE_FLOOR = 20_000.0           # "for the right price" -- never free, never good


def _fall_stage_would_fire_event(stage_index):
    stage = CATHEDRAL_FALL_STAGES[stage_index]
    return {
        "type": "cathedral_fall_stage",
        "detail": "SHADOW MODE: would post a stage-transition §P letter (id=%s) -- %r -- "
                   "fired nothing." % (stage["id"], stage["letter"]),
    }


def compute_warzone_posture():
    """A6 / Card 1 RULED (owner, bench sitting 2026-09-13, via
    CATHEDRAL_ARC_OPEN_CARDS_1): 'And the mechanoids go all out hostile,
    plus all of the above.' Returns the four-part posture the card names --
    (a) GM layer + existing pursuit/raid pacing surfaces, (b) named-faction
    hostility re-alignments (scoped, reversible), (c) a harsher storyteller/
    difficulty swap, (d) mechanoid factions at large go all-out hostile.

    The named edge (item 8's own escalation clause): faction-13 conduct is
    ALSO bound, forever, by bans 2/3/6 and the ruled -75/0 goodwill
    hysteresis (no authored Sentinel-raid/pursuit story against the player,
    in any register, at any posture -- 'perimeter defense only... not
    manhunts'). This function reconciles the two rulings by SCOPE, not by
    softening either one: Card 1's 'all-out hostile' is modelled as
    faction-13's stance toward the EMPIRE -- the war the Cathedral is
    fighting and losing -- and never as a new consequence path against the
    player's own goodwill ledger. Toward the player, faction-13 stays
    exactly the vanilla hysteresis, perimeter-defense-only, same as every
    other posture. This is THIS PASS's OWN resolution, not literally
    specced by either card; it is not escalated to the owner because ban 3
    already answers the only part of Card 1 that could otherwise conflict
    (a raid/pursuit story against the player), so nothing here contradicts
    a named ruling -- flagged in the item's progress note for a sanity
    check, not blocked on.
    """
    return {
        "warzone_active": True,
        "gm_layer_and_pursuit_pacing": {
            "pursuit_pacing_multiplier": 1.5,  # GM tuning; reuses the existing surface, invents no new one
            "reuses_existing_surface": "kyber_trade_plot_spec.md §3 pursuit spine",
        },
        "faction_hostility_realignment": [
            {"faction": "Empire", "posture": "open_war_with_mechanoid_factions_at_large", "reversible": True},
            {
                "faction": CATHEDRAL_FACTION,
                "posture_toward_empire": "all_out_hostile",
                "posture_toward_player": "unchanged_vanilla_hysteresis",
                "perimeter_defense_only_toward_player": True,
                "reversible": True,
            },
        ],
        "storyteller_difficulty_swap": {
            "threat_scale_multiplier": 1.25,  # GM-tuning placeholder, not a ruled number
            "note": "harsher storyteller/difficulty swap per Card 1; which storyteller def "
                    "and by how much is a build-time GM-tuning choice, not authored here",
        },
        "mechanoid_all_out_hostile": {
            "scope": "mechanoid factions at large -- Card 1's own 'plus all of the above' "
                     "excludes no faction by name",
            "faction_13_carve_out": "toward the player only; see faction_hostility_realignment above",
        },
        "no_worldgen": True,
        "no_map_regeneration": True,
    }


def compute_hutt_extraction_offer(hutt_interest, hutt_goodwill):
    """A6 / §6.1 RULED: 'the Hutts might still be able to get the players
    offworld... for the right price.' Rides the kyber §4 fixer lane -- gated
    on Hutt Interest having crossed at least the fixer-beat threshold (kyber
    spec §4 threshold (b), the standing-buyer fixer who is 'the discovery
    channel' this extraction rides); price falls as Interest and standing
    rise (kyber §4: 'Interest is not friendship... it moves access: better
    prices'), floored so it is never free -- 'it won't feel very good.'
    Mechanism only: registering this as a RATIFIED campaign ending is
    CAMPAIGN_STORY_SITTING_1's job (item 8's own Depends-on line), not
    this function's."""
    goodwill = hutt_goodwill if hutt_goodwill is not None else 0.0
    available = hutt_interest >= HUTT_EXTRACTION_MIN_INTEREST
    price = HUTT_EXTRACTION_BASE_PRICE
    price -= HUTT_EXTRACTION_PRICE_DISCOUNT_PER_INTEREST * hutt_interest
    price -= HUTT_EXTRACTION_PRICE_DISCOUNT_PER_GOODWILL * max(0.0, goodwill)
    price = max(HUTT_EXTRACTION_PRICE_FLOOR, price)
    return {
        "extraction_available": available,
        "extraction_price_silver": round(price) if available else None,
        "hutt_interest_at_offer": round(hutt_interest, 3),
        "hutt_goodwill_at_offer": goodwill,
        "refusable": True,
        "ending_ratification_owner": "CAMPAIGN_STORY_SITTING_1",
    }


def _game_text(raw):
    """A def string as a letter shows it: RimWorld turns the two characters \\n into a line break."""
    return (raw or "").strip().replace("\\n", "\n")


def load_cathedral_offer_catalogue(paths=CATHEDRAL_FAVOUR_DEFS):
    """CATHEDRAL_MISSION_BOON_OFFERS_1: every mission and boon the blackboard can offer, with the text the player
    will read, parsed from the shipped defs so no string or heat ceiling has a second home. Missions pair each
    RUT_CathedralAssailantMission_* QuestScriptDef with the GiveQuest IncidentDef that fires it; boons are the
    IncidentDefs carrying a RUT_CathedralBoonExtension. Refuses (raises) on an empty catalogue: a blackboard that
    offers nothing because it could not read the defs must not look like one that has nothing to offer."""
    import xml.etree.ElementTree as ET
    quests, givers, boons, named = {}, {}, [], {}
    for path in paths:
        for el in ET.parse(path).getroot():
            if el.tag == "QuestScriptDef" and el.get("Name"):
                named[el.get("Name")] = el
    for path in paths:
        for el in ET.parse(path).getroot():
            name = (el.findtext("defName") or "").strip()
            if el.tag == "QuestScriptDef" and name.startswith(CATHEDRAL_MISSION_QUEST_PREFIX):
                rules = lambda tag: [li.text.split("->", 1)[1] for li in el.findall(tag + "/rulesStrings/li")]
                root, parent = el.find("root"), el.get("ParentName")
                while root is None and parent in named:   # the channel parent carries the quest and its letters
                    root, parent = named[parent].find("root"), named[parent].get("ParentName")
                if root is None:
                    raise RuntimeError("cathedral offers: quest %s has no root, own or inherited" % name)
                quests[name] = {
                    "quest_def": name,
                    "channel": el.get("ParentName"),
                    "quest_names": [_game_text(t) for t in rules("questNameRules")],
                    "quest_description": _game_text((rules("questDescriptionRules") or [""])[0]),
                    "arrival_letter": {"label": _game_text(root.findtext(".//customLetterLabel")),
                                       "text": _game_text(root.findtext(".//customLetterText"))},
                    "success_letter": {"label": _game_text(root.findtext(".//li[@Class='QuestNode_Letter']/label")),
                                       "text": _game_text(root.findtext(".//li[@Class='QuestNode_Letter']/text"))},
                }
            elif el.tag == "IncidentDef" and el.findtext("questScriptDef"):
                givers[el.findtext("questScriptDef").strip()] = (name, _game_text(el.findtext("letterLabel")))
            elif el.tag == "IncidentDef":
                ext = el.find("modExtensions/li[@Class='RimMandrake.Utinni.CathedralPass.RUT_CathedralBoonExtension']")
                if ext is None:
                    continue
                boons.append({
                    "incident_def": name,
                    "letter_label": _game_text(el.findtext("letterLabel")),
                    "letter_text": _game_text(el.findtext("letterText")),
                    "gifts": {g.tag: int(g.text) for g in ext.find("gifts")},
                    "heat_ceiling": float(ext.findtext("heatCeiling")),
                    "reoffer_ticks": int(float(ext.findtext("reofferDays")) * 60_000),
                })
    missions = []
    for qdef in quests:   # file order: the order requests are offered in (the channels alternate)
        if qdef not in givers:
            raise RuntimeError("cathedral offers: quest %s has no GiveQuest IncidentDef to fire it" % qdef)
        missions.append(dict(quests[qdef], incident_def=givers[qdef][0], offer_letter_label=givers[qdef][1]))
    if not missions or not boons:
        raise RuntimeError("cathedral offers: catalogue read %d missions and %d boons from %s -- refusing to run "
                           "an offer gate that can offer nothing" % (len(missions), len(boons), [str(p) for p in paths]))
    boons.sort(key=lambda b: -b["heat_ceiling"])
    return {"missions": missions, "boons": boons}


def compute_cathedral_offer_gate(conduct_posture, heat, boons):
    """The pure gate (arc §1/§3): which favours MAY be offered this poll. Missions at TOLERATED+, boons at VOUCHED+
    and each only at Heat <= its own ceiling ("when the Empire is looking, it does not act"). A go-dark flip needs
    no clause here: it forces the conduct posture to WARY on the same poll, which closes both."""
    missions_open = conduct_posture >= CATHEDRAL_MISSION_MIN_POSTURE
    boon_rows = []
    for b in boons:
        if conduct_posture < CATHEDRAL_BOON_MIN_POSTURE:
            state = "closed_stage"
        elif heat > b["heat_ceiling"]:
            state = "withheld_heat"
        else:
            state = "open"
        boon_rows.append({"incident_def": b["incident_def"], "heat_ceiling": b["heat_ceiling"], "state": state})
    return missions_open, boon_rows


def quest_root(row, catalogue):
    """The root QuestScriptDef of one jawa/quest_lifecycle row: the row's own `root` (companion builds from
    CATHEDRAL_MISSION_BOON_OFFERS_1 on), else matched by the quest's generated name, which for these quests is a
    fixed string (no grammar tokens). Returns (defName or None, how)."""
    if row.get("root"):
        return row["root"], "root"
    for m in catalogue["missions"]:
        if row.get("name") in m["quest_names"]:
            return m["quest_def"], "name"
    return None, None


def _count_matched(things, defname):
    """countMatched of a list_things reply. A reply without it (tool refused / failed) is UNMEASURED, never 0:
    a false 0 reads as the whole stock being sold on that poll and bumps Heat/Regard."""
    n = things.get("countMatched") if isinstance(things, dict) else None
    if not isinstance(n, int):
        raise RuntimeError("jawa/list_things %s returned no countMatched (UNMEASURED): %r" % (defname, str(things)[:160]))
    return n


def _sale_heat(delta_lost):
    """Sublinear Heat bump for a quantity apparently lost from the colony
    ledger -- kyber spec §3: 'scale with quantity, sublinearly.'"""
    if delta_lost <= 0:
        return 0.0
    return HEAT_PER_KYBER_SOLD * (delta_lost ** 0.5)


# ---------------------------------------------------------------------------
# CATHEDRAL_REGARD_BLACKBOARD_1 -- KNOWN GAPS, stated once here rather than
# scattered: as of this build (2026-09-13) there is no live bridge signal for
# --
#   - manners / band-history (kit's RM_MapComponent_BiomeAttitude.currentBand
#     -- private field, no [Tool] exposes it; a "manners_proxy" substitutes,
#     see CATHEDRAL_REGARD_GAIN_MANNERS_PROXY_PER_CLEAN_POLL above)
#   - (Assailant-register mission completions: BUILT since
#     CATHEDRAL_MISSION_BOON_OFFERS_1 -- read off jawa/quest_lifecycle; the
#     story flag now only carries completions from before the run)
#   - the §4 restore choice (already specced elsewhere, but no quest exists
#     yet to fire it)
#   - the misdirection-quest success beat (item 5, unbuilt, card A4)
#   - pursuit-spine events resolving on Cathedral ground (Act II+, unbuilt)
#   - the reveal beat itself (item 7's own beat; deliberately NEVER wired
#     into this file's own computation -- see compute_conduct_posture below)
# --story-flags-file lets a human or a later item supply these once they
# exist; absent the file, every one of them is 0/False -- an honest "no
# signal", not a silent zero standing in for a real negative reading.
# ---------------------------------------------------------------------------
def load_story_flags(path):
    defaults = {
        "assailant_mission_completions": 0,
        "restore_choice_made": False,
        "misdirection_quest_success": False,
        "reveal_beat_fired": False,
    }
    if not path:
        return defaults, False
    p = Path(path)
    if not p.exists():
        # a path that was NAMED but is missing must not read as "no flags file" (would run on defaults silently)
        raise SystemExit("gm_blackboard_shadow: --story-flags-file %s does not exist" % path)
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    defaults.update({k: v for k, v in data.items() if k in defaults})
    return defaults, True


def compute_conduct_posture(regard, clean_streak, mission_completions, previous_posture):
    """WARY(0)/TOLERATED(1)/VOUCHED(2) ONLY -- the return type is structurally
    incapable of producing 3 (REVEALED). Climb uses the higher §1 floors plus
    the manners-proxy streak / mission count; fall uses lower demote floors
    (arc §1: 'Regard loss demotes conduct-stages (2->1->0-in-posture)') --
    hysteresis margin between climb and demote floors, same shape as the
    kit's own band hysteresis. previous_posture anchors both directions so
    a single poll's regard reading cannot skip a rung."""
    # Each branch is gated on previous_posture, never on the already-updated
    # local `posture` -- gating on the local would let one poll's reading
    # satisfy a climb AND the next climb's floor at once (or a demote and the
    # next demote's floor at once), promoting/demoting two rungs in a single
    # poll. That contradicts this function's own contract above, and was
    # found doing exactly that in code review, 2026-09-17.
    posture = previous_posture
    if previous_posture == 0 and regard >= CATHEDRAL_STAGE_TOLERATED_REGARD_FLOOR \
            and clean_streak >= CATHEDRAL_REGARD_CLEAN_STREAK_TOLERATED_FLOOR:
        posture = 1
    elif previous_posture == 1 and regard >= CATHEDRAL_STAGE_VOUCHED_REGARD_FLOOR \
            and mission_completions >= CATHEDRAL_STAGE_VOUCHED_MISSIONS_REQUIRED:
        posture = 2
    elif previous_posture == 2 and regard < CATHEDRAL_STAGE_DEMOTE_VOUCHED_FLOOR:
        posture = 1
    elif previous_posture == 1 and regard < CATHEDRAL_STAGE_DEMOTE_TOLERATED_FLOOR:
        posture = 0
    return posture


class ShadowBlackboard:
    def __init__(self, log_path, orbital_timer_start=ORBITAL_TIMER_START_TICKS,
                 story_flags=None, exposure_godark_threshold=CATHEDRAL_EXPOSURE_GODARK_THRESHOLD,
                 pursuit_event_on_poll=None,
                 full_discovery_threshold=CATHEDRAL_FULL_DISCOVERY_THRESHOLD,
                 fall_enabled=True, offer_catalogue=None, missions_enabled=True, boons_enabled=True):
        self.log_path = log_path
        self.heat = 0.0
        self.hutt_interest = 0.0
        self.cathedral_regard = 0.0
        self.orbital_timer_start = orbital_timer_start
        self.orbital_timer = orbital_timer_start
        self.prev_kyber_total = None
        self.prev_hutt_goodwill = None
        self.prev_cathedral_goodwill = None
        self.prev_cathedral_hostile = None
        self.poll_index = 0
        self.would_fire_log = []

        # CATHEDRAL_REGARD_BLACKBOARD_1
        self.story_flags = story_flags or {}
        self.story_flags_pending_applied = False  # one-time discrete beats, applied on poll 1 only
        self.clean_streak = 0
        self.prev_anomaly_total = None
        self.anomaly_cumulative_sold_volume = 0
        self.conduct_posture = 0  # WARY -- f(Regard, goodwill, story flags); see compute_conduct_posture
        self.knowledge_revealed = bool(self.story_flags.get("reveal_beat_fired", False))
        self.exposure_pressure = 0.0
        self.exposure_godark_threshold = exposure_godark_threshold
        self.pursuit_event_on_poll = pursuit_event_on_poll
        self.go_dark_flip_count = 0

        # CATHEDRAL_EXPOSURE_COMPLETION_1 (item 8)
        self.fall_enabled = fall_enabled  # --disable-cathedral-fall: the completion chain never starts
        self.full_discovery_threshold = full_discovery_threshold
        self.full_discovery = False
        self.fall_stage = -1  # -1 = not started; index into CATHEDRAL_FALL_STAGES once full_discovery fires
        self.warzone_posture = None
        self.hutt_extraction_offer = None

        # CATHEDRAL_MISSION_BOON_OFFERS_1: the favours (see advance_cathedral_offers)
        self.offer_catalogue = offer_catalogue or load_cathedral_offer_catalogue()
        self.missions_enabled = missions_enabled  # mirrors the mod's cathedralMissionsEnabled setting
        self.boons_enabled = boons_enabled        # mirrors cathedralBoonsEnabled
        self.mission_rotation = 0
        self.mission_offer = None              # the request currently posted or in progress, if any
        self.mission_last_resolved_tick = None
        self.mission_quest_ids_seen = set()
        self.mission_completed_quest_ids = set()
        self.mission_completions_observed = 0
        self.boon_last_given_tick = {}
        self.boon_any_last_tick = None
        self.boons_given = 0
        self.last_go_dark_tick = None
        self.last_completion_tick = None
        self.record_extra = {}  # merged into every record before it is logged (fixture mode marks its records)

    def advance_fall_chain(self, record, would_fire, hutt_goodwill):
        """CATHEDRAL_EXPOSURE_COMPLETION_1 (item 8): one poll's step of the
        full-discovery -> witnessed fall -> completion chain. Pure state on
        self (no bridge), so selftest_gm_cathedral_fall.py drives it directly.
        With fall_enabled False the chain never starts and the record says so."""
        record["cathedral_fall_enabled"] = self.fall_enabled
        if not self.fall_enabled:
            record["full_discovery"] = False
            record["full_discovery_fired_this_poll"] = False
            record["fall_stage"] = -1
            record["fall_stage_label"] = None
            record["warzone_posture"] = None
            record["hutt_extraction_offer"] = None
            return
        # --- CATHEDRAL_EXPOSURE_COMPLETION_1 (item 8): full discovery can
        # only fire after >=1 go-dark flip THIS RUN, and go-dark always
        # resets exposure_pressure to 0.0 the same poll it fires -- so this
        # can never trip on the same poll as a go-dark flip; it structurally
        # requires a later poll's re-accumulation past the higher threshold.
        # That is the "demotion/dark precedes it" ordering guarantee, built
        # into the arithmetic rather than asserted by a flag.
        full_discovery_fired_this_poll = False
        if (not self.full_discovery and self.go_dark_flip_count >= 1
                and self.exposure_pressure >= self.full_discovery_threshold):
            full_discovery_fired_this_poll = True
            self.full_discovery = True
            self.fall_stage = 0
            would_fire.append({
                "type": "cathedral_full_discovery",
                "detail": "exposure pressure %.2f reached the full-discovery threshold "
                           "(%.2f) after at least one prior go-dark flip -- SHADOW MODE: "
                           "would begin the witnessed fall chain (item 8); the knowledge "
                           "gate is untouched (opens for nobody but the player, per arc "
                           "law); fired nothing." % (self.exposure_pressure, self.full_discovery_threshold),
            })
            would_fire.append(_fall_stage_would_fire_event(self.fall_stage))
        elif self.full_discovery and self.fall_stage < len(CATHEDRAL_FALL_STAGES) - 1:
            # one witnessed stage per poll -- "witnessed, not narrated" (item 8 spec)
            self.fall_stage += 1
            would_fire.append(_fall_stage_would_fire_event(self.fall_stage))

        record["full_discovery"] = self.full_discovery
        record["full_discovery_fired_this_poll"] = full_discovery_fired_this_poll
        record["fall_stage"] = self.fall_stage
        record["fall_stage_label"] = (
            CATHEDRAL_FALL_STAGES[self.fall_stage]["id"] if self.fall_stage >= 0 else None)

        # Completion: fires exactly once, the poll the fall chain reaches its
        # final stage -- warzone posture flip + priced Hutt extraction +
        # gravship mourning register all land together, since all three gate
        # on the same "the fall completes" event (item 8's own bullets).
        if (self.full_discovery and self.warzone_posture is None
                and self.fall_stage == len(CATHEDRAL_FALL_STAGES) - 1):
            self.warzone_posture = compute_warzone_posture()
            self.hutt_extraction_offer = compute_hutt_extraction_offer(self.hutt_interest, hutt_goodwill)
            for line in CATHEDRAL_MOURNING_REGISTER:
                would_fire.append({
                    "type": "gravship_mourning_register",
                    "detail": "SHADOW MODE: would post ship-adjacent §P-register text -- "
                               "%r -- fired nothing." % line,
                })
            would_fire.append({
                "type": "warzone_posture_flip",
                "detail": "SHADOW MODE: would apply the Card-1-ruled warzone posture "
                           "(pursuit pacing + faction realignment + storyteller swap + "
                           "mechanoid-all-out-hostile); faction-13's stance toward the "
                           "PLAYER stays the ruled vanilla hysteresis, never a new raid/"
                           "pursuit story (bans 2/3/6); fired nothing.",
            })
            would_fire.append({
                "type": "hutt_extraction_offer",
                "detail": "SHADOW MODE: would open the priced, refusable Hutt extraction "
                           "window (%s); ending ratification belongs to "
                           "CAMPAIGN_STORY_SITTING_1, not this blackboard; fired "
                           "nothing." % self.hutt_extraction_offer,
            })

        record["warzone_posture"] = self.warzone_posture
        record["hutt_extraction_offer"] = self.hutt_extraction_offer

    def observe_mission_quests(self, rows, ticks, would_fire):
        """Read the quest list (jawa/quest_lifecycle action=list) for Cathedral missions: a row newly in EndedSuccess
        is a completion (a Regard input, never a Heat one -- K2), and the posted request is tracked from offer
        through acceptance to its end. Returns this poll's completion count."""
        completed_now = 0
        mission_rows = []
        for row in rows or []:
            root, how = quest_root(row, self.offer_catalogue)
            if not root or not root.startswith(CATHEDRAL_MISSION_QUEST_PREFIX):
                continue
            mission_rows.append({"id": row.get("id"), "quest_def": root, "state": row.get("state"), "matched_by": how})
            qid, state = row.get("id"), row.get("state")
            if state == "EndedSuccess" and qid not in self.mission_completed_quest_ids:
                self.mission_completed_quest_ids.add(qid)
                completed_now += 1
                would_fire.append({
                    "type": "cathedral_mission_completed", "quest_id": qid, "quest_def": root,
                    "detail": "mission quest %s (%s) ended in success -- SHADOW MODE: would gain %.2f Regard; "
                              "Imperial Heat is not an input of a completion (K2) and does not move; fired nothing."
                              % (qid, root, CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION)})
            offer = self.mission_offer
            if offer and offer["quest_def"] == root and qid not in offer["quest_ids_before_offer"]:
                offer["quest_id"] = qid
                if state == "Ongoing" and offer["status"] == "posted":
                    offer["status"] = "in_progress"
                    offer["accepted_tick"] = ticks
                elif state and state.startswith("Ended"):
                    would_fire.append({"type": "cathedral_mission_resolved", "quest_id": qid, "quest_def": root,
                                       "detail": "the posted request ended %s; the next one waits %d ticks." %
                                                 (state, CATHEDRAL_MISSION_REOFFER_GAP_TICKS)})
                    self.mission_offer = None
                    self.mission_last_resolved_tick = ticks
            self.mission_quest_ids_seen.add(qid)
        self.mission_completions_observed += completed_now
        if completed_now:
            self.last_completion_tick = ticks
        return completed_now, mission_rows

    def advance_cathedral_offers(self, record, would_fire, ticks, go_dark_fired):
        """CATHEDRAL_MISSION_BOON_OFFERS_1: one poll of the favours, after the stage machine and the go-dark flip
        have set this poll's conduct posture. Posts at most one request at a time (alternating the enclave and
        Utinni channels), withdraws a posted request the moment missions close, lets an ignored one lapse at the
        quests' own expiry, and leaves at most one gravtech gift a day among the boons whose Heat ceiling is
        clear. Pure state on self (no bridge): selftest_rustcathedral_offers.py drives it through poll()."""
        cat = self.offer_catalogue
        if go_dark_fired:
            self.last_go_dark_tick = ticks
        dark_hold = self.last_go_dark_tick is not None and ticks - self.last_go_dark_tick < CATHEDRAL_FAVOURS_DARK_HOLD_TICKS
        missions_open, boon_rows = compute_cathedral_offer_gate(self.conduct_posture, self.heat, cat["boons"])
        if go_dark_fired:
            closed_reason = "go_dark"
        elif dark_hold:
            closed_reason = "dark_hold"
        elif not self.missions_enabled:
            closed_reason = "missions_disabled"
        else:
            closed_reason = None if missions_open else "stage_below_TOLERATED"
        missions_open = missions_open and self.missions_enabled and not dark_hold

        offer = self.mission_offer
        if offer and offer["status"] == "posted" and not missions_open:
            would_fire.append({"type": "cathedral_mission_offer_withdrawn", "quest_def": offer["quest_def"],
                               "reason": closed_reason,
                               "detail": "missions closed (%s) while %s was on offer -- SHADOW MODE: would let the "
                                         "offer lapse with no letter (the request simply is not repeated); fired "
                                         "nothing." % (closed_reason, offer["quest_def"])})
            self.mission_offer, self.mission_last_resolved_tick = None, ticks
        elif offer and offer["status"] == "posted" and ticks - offer["posted_tick"] >= CATHEDRAL_MISSION_OFFER_EXPIRY_TICKS:
            would_fire.append({"type": "cathedral_mission_offer_lapsed", "quest_def": offer["quest_def"],
                               "detail": "the request went unanswered for %d ticks and lapses (the quest's own "
                                         "expiry); fired nothing." % (ticks - offer["posted_tick"])})
            self.mission_offer, self.mission_last_resolved_tick = None, ticks

        if (missions_open and self.mission_offer is None and (self.mission_last_resolved_tick is None
                or ticks - self.mission_last_resolved_tick >= CATHEDRAL_MISSION_REOFFER_GAP_TICKS)):
            m = cat["missions"][self.mission_rotation % len(cat["missions"])]
            self.mission_rotation += 1
            self.mission_offer = {"quest_def": m["quest_def"], "incident_def": m["incident_def"], "posted_tick": ticks,
                                  "status": "posted", "quest_id": None,
                                  "quest_ids_before_offer": sorted(self.mission_quest_ids_seen)}
            would_fire.append({
                "type": "cathedral_mission_offer", "incident_def": m["incident_def"], "quest_def": m["quest_def"],
                "letter": {"label": m["offer_letter_label"], "quest_name": m["quest_names"][0],
                           "text": m["quest_description"]},
                "detail": "SHADOW MODE: would fire %s through jawa/storyteller_fire (dryRun=false); fired nothing."
                          % m["incident_def"]})

        given = None
        for row in boon_rows:
            boon = next(b for b in cat["boons"] if b["incident_def"] == row["incident_def"])
            last = self.boon_last_given_tick.get(row["incident_def"])
            row["next_eligible_tick"] = None if last is None else last + boon["reoffer_ticks"]
            if dark_hold:
                row["state"] = "closed_go_dark"
            elif not self.boons_enabled and row["state"] == "open":
                row["state"] = "boons_disabled"
            if row["state"] != "open" or given is not None:
                continue
            if last is not None and ticks - last < boon["reoffer_ticks"]:
                continue
            if self.boon_any_last_tick is not None and ticks - self.boon_any_last_tick < CATHEDRAL_BOON_ANY_GAP_TICKS:
                continue
            if (self.last_completion_tick is not None
                    and ticks - self.last_completion_tick < CATHEDRAL_BOON_AFTER_COMPLETION_GAP_TICKS):
                row["state_note"] = "waiting: a mission ended within two days"
                continue
            given = boon
            self.boon_last_given_tick[boon["incident_def"]] = ticks
            self.boon_any_last_tick = ticks
            self.boons_given += 1
            row["given_this_poll"] = True
            would_fire.append({
                "type": "cathedral_boon_offer", "incident_def": boon["incident_def"], "gifts": boon["gifts"],
                "heat_at_offer": round(self.heat, 3), "heat_ceiling": boon["heat_ceiling"],
                "letter": {"label": boon["letter_label"], "text": boon["letter_text"]},
                "detail": "SHADOW MODE: would fire %s through jawa/storyteller_fire (dryRun=false); fired nothing."
                          % boon["incident_def"]})

        offer = self.mission_offer
        record["cathedral_offers"] = {
            "imperial_heat": round(self.heat, 3),
            "conduct_posture": CATHEDRAL_STAGE_LABELS[self.conduct_posture],
            "dark_hold_until_tick": (self.last_go_dark_tick + CATHEDRAL_FAVOURS_DARK_HOLD_TICKS) if dark_hold else None,
            "missions": {"open": missions_open, "closed_reason": closed_reason,
                         "current": None if offer is None else {k: offer[k] for k in
                                                                ("quest_def", "status", "posted_tick", "quest_id")}},
            "boons": boon_rows,
            "text_source": "shipped defs (fallback text); the offer path calls no LLM",
        }

    def poll(self, rb):
        self.poll_index += 1
        game_info = safe_call(rb, "rimworld/get_game_info")
        map_info = safe_call(rb, "jawa/map_info")
        factions = safe_call(rb, "jawa/list_factions", {"includeHidden": True})
        fac_rows = factions.get("factions", factions)
        fac_by_def = {f.get("defName"): f for f in fac_rows if isinstance(f, dict)}

        hutt = fac_by_def.get(HUTT_CARTEL_FACTION, {})
        hutt_goodwill = hutt.get("goodwill")
        cathedral = fac_by_def.get(CATHEDRAL_FACTION, {})
        cathedral_goodwill = cathedral.get("goodwill")
        cathedral_hostile = cathedral.get("hostile")

        kyber_total = 0
        kyber_per_def = {}
        for defname in KYBER_FAMILY_DEFNAMES:
            things = safe_call(rb, "jawa/list_things", {"defName": defname})
            n = _count_matched(things, defname)
            kyber_per_def[defname] = n
            kyber_total += n

        biome = map_info.get("mapBiome") or map_info.get("tileInfo", {}).get("biome")
        dark_tile = biome in DARK_BIOMES

        # --- Cathedral-ground presence: best-effort proxy only. No Cathedral
        # tile/landmark id is authored/documented yet (checked: the_rust_
        # cathedral.md and worldbuilding/ carry no tile number), so this
        # input degrades honestly to "unknown / not detected" rather than
        # guessing. Flagged as a real gap for the live-injection build, not
        # papered over here.
        settlement_label = (map_info.get("mapParent") or {}).get("label", "")
        cathedral_ground = "cathedral" in settlement_label.lower() or "cathedral" in str(biome).lower()
        cathedral_ground_confidence = "heuristic-label-match" if cathedral_ground else "no-marker-found"

        # --- CATHEDRAL_REGARD_BLACKBOARD_1: anomaly (bolt-shed/eel) counts,
        # same delta-lost trick as kyber, same sold-vs-crafted caveat (a drop
        # could be a sale OR a crafting/consumption event -- no bridge tool
        # distinguishes them, per the kyber spec's own build note, §2).
        anomaly_total = 0
        anomaly_per_def = {}
        for defname in ANOMALY_DEFNAMES:
            things = safe_call(rb, "jawa/list_things", {"defName": defname})
            n = _count_matched(things, defname)
            anomaly_per_def[defname] = n
            anomaly_total += n

        # --- Corroborating evidence only (does NOT gate the math below): was
        # a trade partner even present on the map this poll? read-only "in
        # effect" per jawa/trade_price_probe's own header. "No trader pawn
        # found" is the tool's own success:false result, not a transport
        # error (rimbridge_client's `check` param guards unknown ARGUMENTS,
        # not a tool's own success flag) -- so this returns normally either way.
        trader_probe = safe_call(rb, "jawa/trade_price_probe", {})
        trader_pawn_present = bool(trader_probe.get("success"))
        trader_probe_reason = trader_probe.get("error") or trader_probe.get("reason") or None

        # CATHEDRAL_MISSION_BOON_OFFERS_1: the quest list (read-only: action='list' is enforced in safe_call). A
        # reply without a quests list is UNMEASURED, never "no quests": a false empty list would lapse a request
        # the player had accepted.
        quest_reply = safe_call(rb, "jawa/quest_lifecycle", {"action": "list"})
        quest_rows = quest_reply.get("quests") if isinstance(quest_reply, dict) else None
        if not isinstance(quest_rows, list):
            raise RuntimeError("jawa/quest_lifecycle list returned no quests[] (UNMEASURED): %r" % str(quest_reply)[:160])

        record = {
            "poll": self.poll_index,
            "ticksGame": game_info.get("ticksGame"),
            "tile": map_info.get("tile"),
            "mapBiome": biome,
            "settlement": settlement_label,
            "kyber_family_counts": kyber_per_def,
            "kyber_family_total": kyber_total,
            "hutt_goodwill": hutt_goodwill,
            "cathedral_goodwill": cathedral_goodwill,
            "cathedral_hostile": cathedral_hostile,
            "dark_tile": dark_tile,
            "cathedral_ground_presence": cathedral_ground,
            "cathedral_ground_confidence": cathedral_ground_confidence,
            "anomaly_family_counts": anomaly_per_def,
            "anomaly_family_total": anomaly_total,
            "trader_pawn_present_this_poll": trader_pawn_present,
            "trader_probe_reason": trader_probe_reason,
        }

        # --- Heat: kyber-family count DECREASE since last poll is read as a
        # possible sale (kyber spec §2's own caveat: a count-diff cannot yet
        # distinguish sold from crafted-away -- logged as such, not trusted
        # as fact; that reconciliation is explicitly future build work, not
        # this item's exit bar).
        delta_lost = 0
        if self.prev_kyber_total is not None:
            delta_lost = max(0, self.prev_kyber_total - kyber_total)
        sale_heat = _sale_heat(delta_lost)
        self.heat = max(0.0, self.heat - HEAT_DECAY_PER_POLL + sale_heat)
        record["kyber_delta_lost"] = delta_lost
        record["heat_bump_this_poll"] = sale_heat
        record["heat_after"] = round(self.heat, 3)

        # --- Hutt Interest: fed by kyber sales to any buyer (word gets
        # around) -- same delta_lost signal.
        hutt_bump = HUTT_INTEREST_PER_KYBER_SOLD * delta_lost
        self.hutt_interest = max(0.0, self.hutt_interest - HUTT_INTEREST_DECAY_PER_POLL + hutt_bump)
        record["hutt_interest_bump_this_poll"] = hutt_bump
        record["hutt_interest_after"] = round(self.hutt_interest, 3)

        # --- Cathedral Regard: kyber/mindstone sales cost Regard always
        # (origin canon §5 C2, cathedral spec §2 "Down"); Heat near Cathedral
        # ground costs or credits Regard depending on band; drifts toward
        # zero absent signal (no drift-to-baseline was ruled OUT for the
        # satiation vector specifically -- Regard is a different number and
        # a slow pull toward neutral is a deliberate, documented shadow-mode
        # choice, not a copy of that ruling). Computed ONCE, in the
        # consolidated §2 fold below (CATHEDRAL_REGARD_BLACKBOARD_1) -- this
        # used to be a separate mini-computation applied here AND folded again
        # into the larger one below, which double-applied the kyber-sale loss,
        # the heat-near-Cathedral term and the decay-toward-zero term every
        # poll (found and fixed in code review, 2026-09-17).

        # --- Orbital-detection timer: drains faster at high Heat, pauses on
        # a dark tile (build_plan.md's "dark-tile pause"), never drains
        # below zero (a would-fire event logs and resets it for continued
        # observation instead of stopping the run).
        would_fire = []
        if dark_tile:
            drain = 0
            record["orbital_timer_paused_reason"] = "dark_tile"
        elif self.heat >= HEAT_HIGH_BAND:
            drain = ORBITAL_TIMER_DRAIN_PER_POLL_HIGH_HEAT
        else:
            drain = ORBITAL_TIMER_DRAIN_PER_POLL_LOW_HEAT
        self.orbital_timer -= drain
        if self.orbital_timer <= 0:
            would_fire.append({
                "type": "orbital_detection",
                "detail": "orbital-detection timer reached zero -- SHADOW MODE: "
                           "logged only, nothing fired, no incident queued.",
            })
            self.orbital_timer = self.orbital_timer_start
        record["orbital_timer_drain_this_poll"] = drain
        record["orbital_timer_after"] = self.orbital_timer

        if delta_lost > 0:
            would_fire.append({
                "type": "heat_bump",
                "detail": "kyber-family count dropped by %d -- SHADOW MODE: "
                           "would raise Heat by %.2f and Hutt Interest by %.2f; "
                           "fired nothing." % (delta_lost, sale_heat, hutt_bump),
            })

        # =====================================================================
        # CATHEDRAL_REGARD_BLACKBOARD_1: Regard §2 additions, the stage
        # machine (§1), and exposure pressure (§6.1). Everything above this
        # block (Heat, Hutt Interest, the two-input cathedral_regard delta) is
        # M4's own territory, untouched.
        # =====================================================================

        # --- anomaly (bolt-shed/eel) volume, cumulative and monotonic --
        # A5: "occasional curiosities are safe with any buyer; selling IN
        # BULK is what draws eyes" -- so this is a running total that only
        # ever grows, and only CROSSING a bulk threshold moves Regard/
        # exposure, never the raw per-poll drop.
        anomaly_delta_lost = 0
        if self.prev_anomaly_total is not None:
            anomaly_delta_lost = max(0, self.prev_anomaly_total - anomaly_total)
        prev_cumulative = self.anomaly_cumulative_sold_volume
        self.anomaly_cumulative_sold_volume += anomaly_delta_lost
        prev_crossings = prev_cumulative // CATHEDRAL_ANOMALY_BULK_VOLUME_THRESHOLD
        new_crossings = self.anomaly_cumulative_sold_volume // CATHEDRAL_ANOMALY_BULK_VOLUME_THRESHOLD
        anomaly_bulk_crossings_this_poll = int(new_crossings - prev_crossings)
        record["anomaly_delta_lost"] = anomaly_delta_lost
        record["anomaly_cumulative_sold_volume"] = self.anomaly_cumulative_sold_volume
        record["anomaly_bulk_crossings_this_poll"] = anomaly_bulk_crossings_this_poll
        if anomaly_bulk_crossings_this_poll > 0:
            would_fire.append({
                "type": "anomaly_bulk_exposure",
                "detail": "cumulative bolt-shed/eel-catch sold volume crossed a bulk "
                           "threshold (%d) %d time(s) -- SHADOW MODE: would cost Regard "
                           "and raise exposure pressure; fired nothing." %
                           (CATHEDRAL_ANOMALY_BULK_VOLUME_THRESHOLD, anomaly_bulk_crossings_this_poll),
            })

        # --- sacrilege mirror: a cathedral (faction 13) goodwill DROP mirrors
        # into Regard at the same moment -- "one act, two ledgers, no double
        # machinery" (arc §2). A goodwill RISE is not itself a Regard input
        # here (the actual Up inputs are the separately-named §2 list).
        cathedral_goodwill_delta = None
        if self.prev_cathedral_goodwill is not None and cathedral_goodwill is not None:
            cathedral_goodwill_delta = cathedral_goodwill - self.prev_cathedral_goodwill
        sacrilege_regard_loss = 0.0
        if cathedral_goodwill_delta is not None and cathedral_goodwill_delta < 0:
            sacrilege_regard_loss = CATHEDRAL_REGARD_LOSS_SACRILEGE_GOODWILL_RATIO * (-cathedral_goodwill_delta)
            would_fire.append({
                "type": "sacrilege_mirror",
                "detail": "cathedral goodwill dropped %.1f -- SHADOW MODE: would mirror "
                           "%.2f Regard loss (one act, two ledgers); fired nothing." %
                           (-cathedral_goodwill_delta, sacrilege_regard_loss),
            })
        record["cathedral_goodwill_delta"] = cathedral_goodwill_delta
        record["sacrilege_regard_loss_this_poll"] = round(sacrilege_regard_loss, 3)

        # --- manners proxy + zero-sale standing credit. A "clean" poll is one
        # with no detected kyber sale and no goodwill drop -- the best signal
        # obtainable without the kit's band history (see KNOWN GAPS above).
        clean_poll = delta_lost == 0 and (cathedral_goodwill_delta is None or cathedral_goodwill_delta >= 0)
        self.clean_streak = self.clean_streak + 1 if clean_poll else 0
        manners_proxy_gain = CATHEDRAL_REGARD_GAIN_MANNERS_PROXY_PER_CLEAN_POLL if clean_poll else 0.0
        zero_sale_credit = CATHEDRAL_REGARD_GAIN_ZERO_SALE_CREDIT_PER_POLL if delta_lost == 0 else 0.0
        record["manners_proxy_used"] = True
        record["manners_proxy_clean_streak"] = self.clean_streak
        record["manners_proxy_gain_this_poll"] = round(manners_proxy_gain, 3)
        record["zero_sale_credit_this_poll"] = round(zero_sale_credit, 3)

        # --- one-time discrete story beats (mission completions, the §4
        # restore choice, the misdirection-quest success). Static per run
        # (read once from --story-flags-file), so applied ONCE on poll 1,
        # never re-added every poll -- these are discrete events, not rates.
        # All default to 0/False, so a run with no --story-flags-file
        # correctly contributes 0 here, every poll -- see KNOWN GAPS above.
        story_gain = 0.0
        if not self.story_flags_pending_applied:
            missions = int(self.story_flags.get("assailant_mission_completions", 0))
            if missions > 0:
                bump = CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION * missions
                story_gain += bump
                would_fire.append({"type": "mission_completions", "detail":
                    "%d Assailant-register mission(s) (story flag) -- SHADOW MODE: "
                    "would gain %.2f Regard; fired nothing." % (missions, bump)})
            if self.story_flags.get("restore_choice_made"):
                story_gain += CATHEDRAL_REGARD_GAIN_RESTORE_CHOICE
                would_fire.append({"type": "restore_choice", "detail":
                    "§4 restore choice (story flag) -- SHADOW MODE: would gain %.2f "
                    "Regard, the single largest §2 gain; fired nothing." %
                    CATHEDRAL_REGARD_GAIN_RESTORE_CHOICE})
            if self.story_flags.get("misdirection_quest_success"):
                story_gain += CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS
                would_fire.append({"type": "misdirection_quest_success", "detail":
                    "item 5's misdirection beat (story flag) -- SHADOW MODE: would "
                    "gain %.2f Regard; fired nothing." % CATHEDRAL_REGARD_GAIN_MISDIRECTION_SUCCESS})
            self.story_flags_pending_applied = True
        record["story_beat_gain_this_poll"] = round(story_gain, 3)

        # --- CATHEDRAL_MISSION_BOON_OFFERS_1: missions completed THIS poll, read off the quest list. Each one is
        # a Regard gain; none is a Heat input (K2 anti-laundering: no term below lets a mission scrub Heat).
        completions_now, mission_rows = self.observe_mission_quests(quest_rows, game_info.get("ticksGame") or 0,
                                                                    would_fire)
        mission_gain = CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION * completions_now
        record["mission_quests"] = mission_rows
        record["mission_completions_this_poll"] = completions_now
        record["mission_completions_observed_total"] = self.mission_completions_observed
        record["mission_completion_regard_gain_this_poll"] = round(mission_gain, 3)

        # --- Regard: fold every §2 input into one delta this poll. Never-
        # movers (bulk salvage, provoked-Sentinel kills, anything unknowable)
        # are correctly absent from this sum by construction -- no term below
        # reads a salvage/mining count or a combat/kill log; nothing to zero
        # out because nothing was ever added.
        regard_delta = (
            -CATHEDRAL_REGARD_LOSS_PER_KYBER_SALE * delta_lost
            - sacrilege_regard_loss
            - CATHEDRAL_REGARD_LOSS_ANOMALY_BULK_SALE * anomaly_bulk_crossings_this_poll
            + manners_proxy_gain
            + zero_sale_credit
            + story_gain
            + mission_gain
        )
        if cathedral_ground:
            if self.heat >= HEAT_HIGH_BAND:
                regard_delta -= CATHEDRAL_REGARD_LOSS_HEAT_NEAR
            elif self.heat <= HEAT_LOW_BAND:
                regard_delta += CATHEDRAL_REGARD_GAIN_LOW_HEAT_NEAR
        if self.cathedral_regard > 0:
            regard_delta -= min(self.cathedral_regard, CATHEDRAL_REGARD_DECAY_TOWARD_ZERO)
        elif self.cathedral_regard < 0:
            regard_delta += min(-self.cathedral_regard, CATHEDRAL_REGARD_DECAY_TOWARD_ZERO)
        self.cathedral_regard += regard_delta
        record["cathedral_regard_delta_this_poll"] = round(regard_delta, 3)
        record["cathedral_regard_after"] = round(self.cathedral_regard, 3)

        # --- exposure pressure (§6.1): its own number, its own inputs
        # (Heat-near-Cathedral, sales volume, pursuit events resolving on
        # Cathedral ground) -- NOT the same accumulator as Regard, per the
        # item's own "this item owns only the number and the dark flip."
        exposure_delta = -min(self.exposure_pressure, CATHEDRAL_EXPOSURE_DECAY_PER_POLL)
        if cathedral_ground and self.heat >= HEAT_HIGH_BAND:
            exposure_delta += CATHEDRAL_EXPOSURE_GAIN_HEAT_NEAR
        exposure_delta += CATHEDRAL_EXPOSURE_GAIN_SALE_VOLUME_PER_KYBER * delta_lost
        exposure_delta += CATHEDRAL_EXPOSURE_GAIN_ANOMALY_BULK_CROSSING * anomaly_bulk_crossings_this_poll
        # Demo/mechanism-testing hook ONLY (mirrors M4's own --orbital-timer-start
        # pattern) -- no live pursuit-spine event exists to read (Act II+ is
        # unbuilt), so this never fires unless --pursuit-event-on-poll names
        # THIS poll index explicitly, and it is always logged as synthetic.
        pursuit_event_this_poll = self.pursuit_event_on_poll == self.poll_index
        if pursuit_event_this_poll:
            exposure_delta += CATHEDRAL_EXPOSURE_GAIN_PURSUIT_EVENT
            would_fire.append({"type": "pursuit_event_on_cathedral_ground", "detail":
                "SYNTHETIC demo trigger (--pursuit-event-on-poll), not a live signal -- "
                "SHADOW MODE: would raise exposure pressure by %.2f; fired nothing." %
                CATHEDRAL_EXPOSURE_GAIN_PURSUIT_EVENT})
        self.exposure_pressure = max(0.0, self.exposure_pressure + exposure_delta)
        record["exposure_pressure_delta_this_poll"] = round(exposure_delta, 3)
        record["exposure_pressure_synthetic_pursuit_event"] = pursuit_event_this_poll

        # --- stage machine (§1): conduct posture is f(Regard, clean_streak,
        # mission_completions) and can ONLY be 0/1/2 -- see
        # compute_conduct_posture's own docstring for why REVEALED cannot
        # come out of this call. Go-dark (§6.1) can force a DEMOTION of
        # posture but never sets knowledge_revealed and never touches Regard,
        # mission counts, or the streak's history beyond this poll's own
        # reset -- "demotes posture without erasing history" (item criteria).
        previous_posture = self.conduct_posture
        # the story flag is completions from before this run; the quest list supplies the rest
        mission_completions_total = (int(self.story_flags.get("assailant_mission_completions", 0))
                                     + self.mission_completions_observed)
        record["mission_completions_total"] = mission_completions_total
        posture = compute_conduct_posture(
            self.cathedral_regard, self.clean_streak, mission_completions_total, previous_posture)

        go_dark_fired = self.exposure_pressure >= self.exposure_godark_threshold
        if go_dark_fired:
            would_fire.append({
                "type": "cathedral_go_dark",
                "detail": "exposure pressure %.2f reached the go-dark threshold (%.2f) -- "
                           "SHADOW MODE: would demote posture to WARY and flatten the hum "
                           "baseline; Regard and mission history are NOT erased; "
                           "fired nothing." % (self.exposure_pressure, self.exposure_godark_threshold),
            })
            posture = 0
            self.clean_streak = 0  # the manners-proxy streak restarts; the relationship broke
            self.exposure_pressure = 0.0  # reset-and-continue, same shape as the orbital timer
            self.go_dark_flip_count += 1

        if posture != previous_posture:
            would_fire.append({
                "type": "stage_transition",
                "detail": "conduct posture %s -> %s -- SHADOW MODE: would feed the kit's "
                           "RM_BiomeAttitudeDef hum baseline; fired nothing." %
                           (CATHEDRAL_STAGE_LABELS[previous_posture], CATHEDRAL_STAGE_LABELS[posture]),
            })
        self.conduct_posture = posture
        effective_stage = 3 if self.knowledge_revealed else posture
        record["conduct_posture"] = posture
        record["conduct_posture_label"] = CATHEDRAL_STAGE_LABELS[posture]
        record["knowledge_revealed"] = self.knowledge_revealed
        record["effective_stage"] = effective_stage
        record["effective_stage_label"] = CATHEDRAL_STAGE_LABELS[effective_stage]
        record["exposure_pressure_after"] = round(self.exposure_pressure, 3)
        record["go_dark_fired_this_poll"] = go_dark_fired
        record["go_dark_flip_count"] = self.go_dark_flip_count

        self.advance_cathedral_offers(record, would_fire, game_info.get("ticksGame") or 0, go_dark_fired)
        self.advance_fall_chain(record, would_fire, hutt_goodwill)

        record["would_fire"] = would_fire
        self.would_fire_log.extend(would_fire)

        self.prev_kyber_total = kyber_total
        self.prev_anomaly_total = anomaly_total
        self.prev_hutt_goodwill = hutt_goodwill
        self.prev_cathedral_goodwill = cathedral_goodwill
        self.prev_cathedral_hostile = cathedral_hostile

        record.update(self.record_extra)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record


class FixtureBridge:
    """Offline/fixture mode (--fixture): answers the blackboard's read tools from a scripted JSON world instead of a
    live game, so the whole poll -- Heat, Regard, the stage machine, go-dark, the favours -- runs with no bridge and
    no RimWorld. Shape of the file:

      {"about": "...", "polls": 200, "tick_step": 15000, "start_tick": 0,
       "state":   {"mapBiome": "...", "tile": 678, "settlement": "...", "trader_present": false,
                   "kyber": {"Force_KyberCrystal": 4, "RUT_Mindstone": 0},
                   "anomaly": {"RM_BoltShedCuriosity": 0, "RM_CoolantEelCatch": 0},
                   "factions": {"Mechanoid": {"goodwill": 0, "hostile": false},
                                "RUT_Jawa_HuttCartel": {"goodwill": 0, "hostile": false}}},
       "changes": {"<poll>": {<any state keys, merged from that poll on>}},
       "player":  {"mission_responses": ["complete", "ignore", "fail", ...],
                   "accept_after_ticks": 30000, "finish_after_ticks": 60000}}

    "player" is a SIMULATED player, and every quest row it makes is marked simulated: in shadow mode nothing is
    fired, so no request ever reaches a real quest list; the simulation stands in for what the live firer would
    do (fire the GiveQuest incident on a cathedral_mission_offer), and for the player answering it -- complete,
    fail, or ignore until the offer lapses -- one response per request in order (the last repeats). A request the
    blackboard withdraws (missions closed) lapses in the quest list too."""

    QUEST_NAMES = None

    def __init__(self, fixture):
        self.fx = fixture
        self.tick = int(fixture.get("start_tick", 0))
        self.state = json.loads(json.dumps(fixture["state"]))
        self.poll_no = 0
        self.quests = []
        self.next_quest_id = 1000
        self.offers_seen = 0
        self.catalogue = None
        player = fixture.get("player") or {}
        self.responses = player.get("mission_responses") or ["ignore"]
        self.accept_after = int(player.get("accept_after_ticks", 30_000))
        self.finish_after = int(player.get("finish_after_ticks", 60_000))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def _merge(self, dst, src):
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                self._merge(dst[k], v)
            else:
                dst[k] = v

    def _advance_quests(self):
        for q in self.quests:
            if q["state"] == "NotYetAccepted" and q["_response"] in ("complete", "fail") \
                    and self.tick - q["_made"] >= self.accept_after:
                q["state"] = "Ongoing"
            elif q["state"] == "Ongoing" and self.tick - q["_made"] >= self.accept_after + self.finish_after:
                q["state"] = "EndedSuccess" if q["_response"] == "complete" else "EndedFailed"
            elif q["state"] == "NotYetAccepted" and self.tick - q["_made"] >= CATHEDRAL_MISSION_OFFER_EXPIRY_TICKS:
                q["state"] = "EndedOfferExpired"

    def observe(self, record, catalogue):
        """After each poll: the simulated firer and player react to what the blackboard would have fired."""
        names = {m["quest_def"]: m["quest_names"][0] for m in catalogue["missions"]}
        for ev in record["would_fire"]:
            if ev["type"] == "cathedral_mission_offer":
                resp = self.responses[min(self.offers_seen, len(self.responses) - 1)]
                self.offers_seen += 1
                self.quests.append({"id": self.next_quest_id, "name": names[ev["quest_def"]], "root": ev["quest_def"],
                                    "state": "NotYetAccepted", "historical": False, "simulated": True,
                                    "_made": self.tick, "_response": resp})
                self.next_quest_id += 1
            elif ev["type"] == "cathedral_mission_offer_withdrawn":
                for q in self.quests:
                    if q["root"] == ev["quest_def"] and q["state"] == "NotYetAccepted":
                        q["state"] = "EndedOfferExpired"

    def call(self, tool, params, check=True):
        st = self.state
        if tool == "rimworld/get_game_info":
            self.poll_no += 1
            change = (self.fx.get("changes") or {}).get(str(self.poll_no))
            if change:
                self._merge(st, change)
            self._advance_quests()
            return {"ticksGame": self.tick, "fixture_poll": self.poll_no}
        if tool == "jawa/map_info":
            return {"mapBiome": st.get("mapBiome"), "tile": st.get("tile"),
                    "mapParent": {"label": st.get("settlement", "")}}
        if tool == "jawa/list_factions":
            return {"factions": [dict(v, defName=k) for k, v in st.get("factions", {}).items()]}
        if tool == "jawa/list_things":
            d = params.get("defName")
            pool = st.get("kyber", {}) if d in st.get("kyber", {}) else st.get("anomaly", {})
            return {"countMatched": int(pool.get(d, 0))}
        if tool == "jawa/trade_price_probe":
            return {"success": bool(st.get("trader_present"))} if st.get("trader_present") else \
                {"success": False, "error": "fixture: no trader pawn on the map"}
        if tool == "jawa/quest_lifecycle":
            rows = [{k: v for k, v in q.items() if not k.startswith("_")} for q in self.quests]
            return {"success": True, "action": "list", "count": len(rows), "quests": rows}
        if tool == "rimworld/step_game_ticks":
            self.tick += int(params.get("ticks", 0))
            return {"success": True}
        raise RuntimeError("FixtureBridge: no fixture answer for %s" % tool)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--polls", type=int, default=None, help="number of poll iterations (default 20, or the fixture's)")
    ap.add_argument("--tick-step", type=int, default=None,
                     help="game ticks to advance between polls via step_game_ticks "
                          "(paused throughout -- see capability-matrix.md)")
    ap.add_argument("--log", default=None, help="output JSONL path (default: "
                     "infrastructure/state/facts/gm_blackboard_shadow_log_<date>.jsonl)")
    ap.add_argument("--orbital-timer-start", type=int, default=ORBITAL_TIMER_START_TICKS,
                     help="starting tick budget for the orbital-detection timer -- a "
                          "GM-tuning placeholder (kyber spec §3: 'exact constants are "
                          "M4 GM-layer tuning'); lower it to observe a would-fire event "
                          "within a short demo run without touching game state")
    ap.add_argument("--story-flags-file", default=None,
                     help="CATHEDRAL_REGARD_BLACKBOARD_1: optional JSON file with "
                          "assailant_mission_completions (int), restore_choice_made (bool), "
                          "misdirection_quest_success (bool), reveal_beat_fired (bool). "
                          "assailant_mission_completions counts missions completed BEFORE this "
                          "run (later ones are read off the quest list); the other three have "
                          "no live bridge signal yet (items 5/7 unbuilt) -- omit this flag for "
                          "a real live run, which correctly leaves them at 0/False.")
    ap.add_argument("--exposure-godark-threshold", type=float, default=CATHEDRAL_EXPOSURE_GODARK_THRESHOLD,
                     help="§6.1 go-dark threshold -- a GM-tuning placeholder; lower it to "
                          "observe the demotion flip within a short demo run")
    ap.add_argument("--pursuit-event-on-poll", type=int, default=None,
                     help="SYNTHETIC demo/mechanism-testing hook only: fire a would-be "
                          "pursuit-spine-on-Cathedral-ground exposure bump on this poll "
                          "index. No live source for this exists (Act II+ pursuit events "
                          "are unbuilt); every record it touches is logged as synthetic.")
    ap.add_argument("--exposure-full-discovery-threshold", type=float,
                     default=CATHEDRAL_FULL_DISCOVERY_THRESHOLD,
                     help="CATHEDRAL_EXPOSURE_COMPLETION_1 (item 8): the full-discovery "
                          "threshold ABOVE go-dark -- lower it (together with "
                          "--exposure-godark-threshold) to observe the whole completion "
                          "chain within a short demo run.")
    ap.add_argument("--fixture", default=None,
                     help="OFFLINE/FIXTURE MODE: replay a scripted world from this JSON file instead of a live "
                          "bridge (see FixtureBridge's docstring for the shape). Needs no game and no bridge; "
                          "--polls and --tick-step default to the fixture's own. Quest rows the fixture's "
                          "simulated player makes are marked simulated in every record.")
    ap.add_argument("--disable-cathedral-missions", action="store_true",
                     help="CATHEDRAL_MISSION_BOON_OFFERS_1: mirrors the mod setting cathedralMissionsEnabled "
                          "off -- no request is ever offered.")
    ap.add_argument("--disable-cathedral-boons", action="store_true",
                     help="CATHEDRAL_MISSION_BOON_OFFERS_1: mirrors cathedralBoonsEnabled off -- no gift.")
    ap.add_argument("--disable-cathedral-fall", action="store_true",
                     help="CATHEDRAL_EXPOSURE_COMPLETION_1 off: no full discovery, no fall "
                          "letters, no warzone flip, no Hutt extraction, no mourning. "
                          "Go-dark and everything else run unchanged.")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    log_path = Path(args.log) if args.log else (
        repo_root / "infrastructure" / "state" / "facts" /
        "gm_blackboard_shadow_log_2026-09-13.jsonl"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    story_flags, story_flags_from_file = load_story_flags(args.story_flags_file)
    if story_flags_from_file:
        print("gm_blackboard_shadow: story flags loaded from %s: %s" % (args.story_flags_file, story_flags))
    else:
        print("gm_blackboard_shadow: no --story-flags-file -- mission/restore-choice/"
              "misdirection/reveal inputs all sit at their honest 0/False default this run.")

    fixture = None
    if args.fixture:
        with open(args.fixture, encoding="utf-8") as f:
            fixture = json.load(f)
    polls = args.polls or (fixture or {}).get("polls") or 20
    # a fixture may carry the demo hooks its scenario needs ("board"); an explicit CLI value still wins
    for key, val in ((fixture or {}).get("board") or {}).items():
        if getattr(args, key) == ap.get_default(key):
            setattr(args, key, val)
    tick_step = args.tick_step or (fixture or {}).get("tick_step") or 2000
    board = ShadowBlackboard(
        log_path, orbital_timer_start=args.orbital_timer_start,
        story_flags=story_flags, exposure_godark_threshold=args.exposure_godark_threshold,
        pursuit_event_on_poll=args.pursuit_event_on_poll,
        full_discovery_threshold=args.exposure_full_discovery_threshold,
        fall_enabled=not args.disable_cathedral_fall,
        missions_enabled=not args.disable_cathedral_missions,
        boons_enabled=not args.disable_cathedral_boons,
    )
    print("gm_blackboard_shadow: shadow mode, read-only, logging to %s" % log_path)

    if fixture is not None:
        print("gm_blackboard_shadow: FIXTURE MODE (%s) -- no bridge, no game: %s"
              % (args.fixture, fixture.get("about", "")))
        bridge = FixtureBridge(fixture)
        board.record_extra = {"fixture": {"file": str(args.fixture), "simulated_player": bool(fixture.get("player"))}}
    else:
        host, port, token = resolve_endpoint()
        bridge = RimBridge(host, port, token)
    with bridge as rb:
        for i in range(polls):
            record = board.poll(rb)
            if fixture is not None:
                rb.observe(record, board.offer_catalogue)
            print(
                "poll %2d  tick=%s  heat=%.2f  hutt=%.2f  regard=%.2f  stage=%-9s  "
                "exposure=%.2f  orbit=%s  dark=%s  kyber_total=%s  would_fire=%d  %s"
                % (
                    record["poll"], record["ticksGame"], record["heat_after"],
                    record["hutt_interest_after"], record["cathedral_regard_after"],
                    record["effective_stage_label"], record["exposure_pressure_after"],
                    record["orbital_timer_after"], record["dark_tile"],
                    record["kyber_family_total"], len(record["would_fire"]),
                    " ".join(e["type"].replace("cathedral_", "") for e in record["would_fire"]
                             if e["type"].startswith("cathedral_m") or e["type"].startswith("cathedral_b")),
                )
            )
            if i < polls - 1:
                safe_call(rb, "rimworld/step_game_ticks", {"ticks": tick_step})
                if fixture is None:
                    time.sleep(0.05)

    print("\n%d would-fire events logged; 0 incidents fired, 0 letters sent, "
          "0 saves written." % len(board.would_fire_log))
    print("Final: heat=%.2f hutt_interest=%.2f cathedral_regard=%.2f orbital_timer=%s "
          "stage=%s exposure_pressure=%.2f go_dark_flips=%d"
          % (board.heat, board.hutt_interest, board.cathedral_regard, board.orbital_timer,
             CATHEDRAL_STAGE_LABELS[3 if board.knowledge_revealed else board.conduct_posture],
             board.exposure_pressure, board.go_dark_flip_count))
    print("Favours: %d mission request(s) posted, %d completed (%d Regard), %d gravtech gift(s) left"
          % (board.mission_rotation, board.mission_completions_observed,
             board.mission_completions_observed * CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION, board.boons_given))
    print("Item 8: full_discovery=%s fall_stage=%s warzone_active=%s hutt_extraction=%s"
          % (board.full_discovery,
             CATHEDRAL_FALL_STAGES[board.fall_stage]["id"] if board.fall_stage >= 0 else None,
             bool(board.warzone_posture and board.warzone_posture.get("warzone_active")),
             board.hutt_extraction_offer))


if __name__ == "__main__":
    main()
