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

Inputs (cross-checked against the specs that consume this blackboard):
  - kyber/mindstone sales           design/Jawa/kyber_trade_plot_spec.md §2/§3
  - Hutt Cartel goodwill            kyber_trade_plot_spec.md §4
  - Cathedral (faction 13) goodwill design/Jawa/cathedral_concealment_arc_spec.md §2
  - Cathedral-ground presence       cathedral_concealment_arc_spec.md §1/§2
  - dark-tile biome                 design/Jawa/build_plan.md §2/§4 ("the dark-tile pause")
  - anomaly (bolt-shed/eel) sales   cathedral_concealment_arc_spec.md §2 (card A5, by volume)
  - trader-pawn presence            corroborating evidence only (see _sale_heat's
                                     sold-vs-crafted caveat, restated below)
  - story-flag hooks (missions, restore choice, misdirection quest, the
    reveal beat) -- optional --story-flags-file; NO live bridge signal exists
    for any of these yet (items 2-8, item 7, are unbuilt), so in a run with no
    file passed they all sit at their honest default of "no signal" -- see
    the module-level KNOWN GAPS note near ShadowBlackboard.

State lives ONLY in this process's own JSONL log (`--log`), never in the save
-- which is also how this sidesteps `enrichment_agents.md` §7.1's reload-
survival unknown: an external blackboard has nothing to lose on reload,
because nothing was ever written into the save to begin with (M0's answer,
reused per this item's brief -- not re-derived).

Run:
    python.exe gm_blackboard_shadow.py --polls 20 --tick-step 2000
    python.exe gm_blackboard_shadow.py --polls 20 --exposure-godark-threshold 8   # demo the go-dark flip

Requires the bridge taken (`rimflow bridge take`) and a live game loaded.
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
})
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
# eel ThingDef confirmed at rust_cathedral_kit_spec.md §RUT_CoolantEel /
# RUT_BoltShedCuriosity).
ANOMALY_DEFNAMES = ["RUT_BoltShedCuriosity", "RUT_CoolantEel"]

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
CATHEDRAL_REGARD_GAIN_MISSION_COMPLETION = 4.0           # per Assailant-register mission (story flag; item 2's own build)
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
#   - Assailant-register mission completions (item 2, unbuilt)
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
        return defaults, False
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
    posture = previous_posture
    if posture == 0 and regard >= CATHEDRAL_STAGE_TOLERATED_REGARD_FLOOR \
            and clean_streak >= CATHEDRAL_REGARD_CLEAN_STREAK_TOLERATED_FLOOR:
        posture = 1
    if posture == 1 and regard >= CATHEDRAL_STAGE_VOUCHED_REGARD_FLOOR \
            and mission_completions >= CATHEDRAL_STAGE_VOUCHED_MISSIONS_REQUIRED:
        posture = 2
    if posture == 2 and regard < CATHEDRAL_STAGE_DEMOTE_VOUCHED_FLOOR:
        posture = 1
    if posture == 1 and regard < CATHEDRAL_STAGE_DEMOTE_TOLERATED_FLOOR:
        posture = 0
    return posture


class ShadowBlackboard:
    def __init__(self, log_path, orbital_timer_start=ORBITAL_TIMER_START_TICKS,
                 story_flags=None, exposure_godark_threshold=CATHEDRAL_EXPOSURE_GODARK_THRESHOLD,
                 pursuit_event_on_poll=None):
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
            n = things.get("countMatched", 0)
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
            n = things.get("countMatched", 0)
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
        # choice, not a copy of that ruling).
        regard_delta = 0.0
        if delta_lost > 0:
            regard_delta -= CATHEDRAL_REGARD_LOSS_PER_KYBER_SALE * delta_lost
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
        mission_completions_total = int(self.story_flags.get("assailant_mission_completions", 0))
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

        record["would_fire"] = would_fire
        self.would_fire_log.extend(would_fire)

        self.prev_kyber_total = kyber_total
        self.prev_anomaly_total = anomaly_total
        self.prev_hutt_goodwill = hutt_goodwill
        self.prev_cathedral_goodwill = cathedral_goodwill
        self.prev_cathedral_hostile = cathedral_hostile

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--polls", type=int, default=20, help="number of poll iterations")
    ap.add_argument("--tick-step", type=int, default=2000,
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
                          "misdirection_quest_success (bool), reveal_beat_fired (bool). No "
                          "live bridge signal exists for any of these yet (items 2/5/7 are "
                          "unbuilt) -- omit this flag for a real live run, which correctly "
                          "leaves every one of them at 0/False.")
    ap.add_argument("--exposure-godark-threshold", type=float, default=CATHEDRAL_EXPOSURE_GODARK_THRESHOLD,
                     help="§6.1 go-dark threshold -- a GM-tuning placeholder; lower it to "
                          "observe the demotion flip within a short demo run")
    ap.add_argument("--pursuit-event-on-poll", type=int, default=None,
                     help="SYNTHETIC demo/mechanism-testing hook only: fire a would-be "
                          "pursuit-spine-on-Cathedral-ground exposure bump on this poll "
                          "index. No live source for this exists (Act II+ pursuit events "
                          "are unbuilt); every record it touches is logged as synthetic.")
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

    host, port, token = resolve_endpoint()
    board = ShadowBlackboard(
        log_path, orbital_timer_start=args.orbital_timer_start,
        story_flags=story_flags, exposure_godark_threshold=args.exposure_godark_threshold,
        pursuit_event_on_poll=args.pursuit_event_on_poll,
    )
    print("gm_blackboard_shadow: shadow mode, read-only, logging to %s" % log_path)

    with RimBridge(host, port, token) as rb:
        for i in range(args.polls):
            record = board.poll(rb)
            print(
                "poll %2d  tick=%s  heat=%.2f  hutt=%.2f  regard=%.2f  stage=%-9s  "
                "exposure=%.2f  orbit=%s  dark=%s  kyber_total=%s  would_fire=%d"
                % (
                    record["poll"], record["ticksGame"], record["heat_after"],
                    record["hutt_interest_after"], record["cathedral_regard_after"],
                    record["effective_stage_label"], record["exposure_pressure_after"],
                    record["orbital_timer_after"], record["dark_tile"],
                    record["kyber_family_total"], len(record["would_fire"]),
                )
            )
            if i < args.polls - 1:
                safe_call(rb, "rimworld/step_game_ticks", {"ticks": args.tick_step})
                time.sleep(0.05)

    print("\n%d would-fire events logged; 0 incidents fired, 0 letters sent, "
          "0 saves written." % len(board.would_fire_log))
    print("Final: heat=%.2f hutt_interest=%.2f cathedral_regard=%.2f orbital_timer=%s "
          "stage=%s exposure_pressure=%.2f go_dark_flips=%d"
          % (board.heat, board.hutt_interest, board.cathedral_regard, board.orbital_timer,
             CATHEDRAL_STAGE_LABELS[3 if board.knowledge_revealed else board.conduct_posture],
             board.exposure_pressure, board.go_dark_flip_count))


if __name__ == "__main__":
    main()
