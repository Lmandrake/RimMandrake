#!/usr/bin/env python3
"""
gm_blackboard_shadow.py -- GM_BLACKBOARD_SHADOW_M4_1

M4's "external blackboard" (`design/Jawa/build_plan.md` §4), SHADOW MODE ONLY:
a Python state machine, driven by polled bridge reads, that tracks Imperial
Heat, the orbital-detection timer, and the dark-tile pause -- and logs what
each WOULD fire. It fires nothing: no incident, no letter, no save write, no
debug action. Read-only by construction (see READ_TOOLS / safe_call below),
not by discipline.

Inputs (cross-checked against the specs that consume this blackboard):
  - kyber/mindstone sales           design/Jawa/kyber_trade_plot_spec.md §2/§3
  - Hutt Cartel goodwill            kyber_trade_plot_spec.md §4
  - Cathedral (faction 13) goodwill design/Jawa/cathedral_concealment_arc_spec.md §2
  - Cathedral-ground presence       cathedral_concealment_arc_spec.md §1/§2
  - dark-tile biome                 design/Jawa/build_plan.md §2/§4 ("the dark-tile pause")

State lives ONLY in this process's own JSONL log (`--log`), never in the save
-- which is also how this sidesteps `enrichment_agents.md` §7.1's reload-
survival unknown: an external blackboard has nothing to lose on reload,
because nothing was ever written into the save to begin with (M0's answer,
reused per this item's brief -- not re-derived).

Run:
    python.exe gm_blackboard_shadow.py --polls 20 --tick-step 2000

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
})
TIME_TOOLS = frozenset({"rimworld/step_game_ticks"})
ALLOWED_TOOLS = READ_TOOLS | TIME_TOOLS


def safe_call(rb, tool, params=None):
    if tool not in ALLOWED_TOOLS:
        raise RuntimeError(
            "gm_blackboard_shadow refuses to call %r -- not in the "
            "read-only/time-advance allowlist. Shadow mode is read-only "
            "by construction; extend ALLOWED_TOOLS deliberately, never "
            "ad hoc." % tool
        )
    return rb.call(tool, params or {})


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

# GM tuning constants -- placeholders for shadow-mode observation only.
# Exact constants are explicitly "M4 GM-layer tuning" per kyber spec §3;
# nothing here is a ruled number, just enough to produce a legible log.
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


def _sale_heat(delta_lost):
    """Sublinear Heat bump for a quantity apparently lost from the colony
    ledger -- kyber spec §3: 'scale with quantity, sublinearly.'"""
    if delta_lost <= 0:
        return 0.0
    return HEAT_PER_KYBER_SOLD * (delta_lost ** 0.5)


class ShadowBlackboard:
    def __init__(self, log_path, orbital_timer_start=ORBITAL_TIMER_START_TICKS):
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
        record["would_fire"] = would_fire
        self.would_fire_log.extend(would_fire)

        self.prev_kyber_total = kyber_total
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
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    log_path = Path(args.log) if args.log else (
        repo_root / "infrastructure" / "state" / "facts" /
        "gm_blackboard_shadow_log_2026-09-13.jsonl"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    host, port, token = resolve_endpoint()
    board = ShadowBlackboard(log_path, orbital_timer_start=args.orbital_timer_start)
    print("gm_blackboard_shadow: shadow mode, read-only, logging to %s" % log_path)

    with RimBridge(host, port, token) as rb:
        for i in range(args.polls):
            record = board.poll(rb)
            print(
                "poll %2d  tick=%s  heat=%.2f  hutt=%.2f  regard=%.2f  "
                "orbit=%s  dark=%s  kyber_total=%s  would_fire=%d"
                % (
                    record["poll"], record["ticksGame"], record["heat_after"],
                    record["hutt_interest_after"], record["cathedral_regard_after"],
                    record["orbital_timer_after"], record["dark_tile"],
                    record["kyber_family_total"], len(record["would_fire"]),
                )
            )
            if i < args.polls - 1:
                safe_call(rb, "rimworld/step_game_ticks", {"ticks": args.tick_step})
                time.sleep(0.05)

    print("\n%d would-fire events logged; 0 incidents fired, 0 letters sent, "
          "0 saves written." % len(board.would_fire_log))
    print("Final: heat=%.2f hutt_interest=%.2f cathedral_regard=%.2f orbital_timer=%s"
          % (board.heat, board.hutt_interest, board.cathedral_regard, board.orbital_timer))


if __name__ == "__main__":
    main()
