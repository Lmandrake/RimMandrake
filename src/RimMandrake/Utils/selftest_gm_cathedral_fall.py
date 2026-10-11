"""selftest_gm_cathedral_fall.py -- the Cathedral completion chain in gm_blackboard_shadow.py, offline.

Every fall letter and mourning line passes cathedral_arc_lint.py at stage -1 (pre-reveal rules: the fall can come
before the reveal), with a planted control proving the gate can fail. The chain is driven through
ShadowBlackboard.advance_fall_chain with no bridge: no full discovery without a prior go-dark flip, no fire below
the threshold, one witnessed stage per poll, completion exactly once, the Hutt extraction priced, floored and
refusable, faction-13 never turned on the player, and --disable-cathedral-fall keeping the chain off.
CATHEDRAL_EXPOSURE_COMPLETION_1."""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []
RAN = []


def check(name, cond, detail=""):
    RAN.append(name)
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _poll(board, goodwill=0.0):
    record, fire = {}, []
    board.advance_fall_chain(record, fire, goodwill)
    return record, fire


def main():
    G = _load("gm_blackboard_shadow", os.path.join(HERE, "gm_blackboard_shadow.py"))
    lint = _load("cathedral_arc_lint", os.path.join(HERE, "..", "RustCathedral", "cathedral_arc_lint.py"))
    n_stages = len(G.CATHEDRAL_FALL_STAGES)

    # --- the strings: item 3's linter, pre-reveal rules
    for st in G.CATHEDRAL_FALL_STAGES:
        got = lint.findings(st["letter"], -1)
        check("lint: fall letter %s clean" % st["id"], not got, got)
    for i, line in enumerate(G.CATHEDRAL_MOURNING_REGISTER):
        got = lint.findings(line, -1)
        check("lint: mourning line %d clean" % i, not got, got)
    check("lint control: a place-naming fall letter is caught",
          bool(lint.findings("The Cathedral does not answer anymore.", -1)))
    check("lint control: 'living memory' is caught pre-reveal",
          bool(lint.findings("For the first time in living memory.", -1)))
    texts = [s["letter"] for s in G.CATHEDRAL_FALL_STAGES] + list(G.CATHEDRAL_MOURNING_REGISTER)
    check("strings: no line repeats", len(set(texts)) == len(texts))

    tmp = tempfile.mkdtemp()
    log = os.path.join(tmp, "log.jsonl")

    # --- ordering: no skip straight to the fall
    b = G.ShadowBlackboard(log, full_discovery_threshold=90.0)
    b.exposure_pressure = 999.0
    r, f = _poll(b)
    check("no go-dark yet: full discovery does not fire at any pressure", not b.full_discovery and r["fall_stage"] == -1)
    b.go_dark_flip_count = 1
    b.exposure_pressure = 89.9
    r, f = _poll(b)
    check("below threshold after go-dark: no fire", not b.full_discovery and not f)
    b.exposure_pressure = 90.0
    r, f = _poll(b)
    types = [e["type"] for e in f]
    check("at threshold after go-dark: fires, stage 0 witnessed", r["full_discovery_fired_this_poll"]
          and r["fall_stage"] == 0 and types == ["cathedral_full_discovery", "cathedral_fall_stage"], types)

    # --- one stage per poll, completion once
    completions = 0
    for k in range(1, n_stages + 3):
        r, f = _poll(b, goodwill=10.0)
        types = [e["type"] for e in f]
        completions += types.count("warzone_posture_flip")
        if k < n_stages:
            check("poll %d: exactly one stage advance (stage %d)" % (k, k),
                  r["fall_stage"] == k and types.count("cathedral_fall_stage") == 1, (r["fall_stage"], types))
        else:
            check("poll %d: no stage past the last, nothing re-fires" % k,
                  r["fall_stage"] == n_stages - 1 and not f, types)
        if k == n_stages - 1:
            check("final stage: mourning + warzone + extraction land together",
                  types.count("gravship_mourning_register") == len(G.CATHEDRAL_MOURNING_REGISTER)
                  and "warzone_posture_flip" in types and "hutt_extraction_offer" in types, types)
    check("completion fired exactly once", completions == 1, completions)
    check("full discovery fires once only", not r["full_discovery_fired_this_poll"])

    # --- warzone posture: faction-13 never turned on the player
    wz = G.compute_warzone_posture()
    f13 = [x for x in wz["faction_hostility_realignment"] if x.get("faction") == G.CATHEDRAL_FACTION]
    check("warzone: faction-13 player posture unchanged, perimeter only",
          len(f13) == 1 and f13[0]["posture_toward_player"] == "unchanged_vanilla_hysteresis"
          and f13[0]["perimeter_defense_only_toward_player"] is True, f13)
    check("warzone: no worldgen, no map regeneration", wz["no_worldgen"] and wz["no_map_regeneration"])

    # --- Hutt extraction: gated, priced, floored, refusable, not self-ratified
    lo = G.compute_hutt_extraction_offer(G.HUTT_EXTRACTION_MIN_INTEREST - 0.1, 0.0)
    check("extraction: closed below the fixer threshold", not lo["extraction_available"]
          and lo["extraction_price_silver"] is None, lo)
    a = G.compute_hutt_extraction_offer(30.0, 0.0)
    c = G.compute_hutt_extraction_offer(60.0, 20.0)
    check("extraction: price falls as Interest/goodwill rise",
          a["extraction_available"] and c["extraction_price_silver"] < a["extraction_price_silver"], (a, c))
    top = G.compute_hutt_extraction_offer(10_000.0, 10_000.0)
    check("extraction: never below the floor", top["extraction_price_silver"] == round(G.HUTT_EXTRACTION_PRICE_FLOOR), top)
    check("extraction: refusable, ratification left to CAMPAIGN_STORY_SITTING_1",
          a["refusable"] and a["ending_ratification_owner"] == "CAMPAIGN_STORY_SITTING_1")
    check("extraction: None goodwill reads as 0", G.compute_hutt_extraction_offer(30.0, None) == a)

    # --- the toggle
    off = G.ShadowBlackboard(log, full_discovery_threshold=1.0, fall_enabled=False)
    off.go_dark_flip_count = 3
    off.exposure_pressure = 999.0
    fired = []
    for _ in range(n_stages + 2):
        r, f = _poll(off)
        fired += f
    check("--disable-cathedral-fall: chain never starts, record says so",
          not fired and not off.full_discovery and r["cathedral_fall_enabled"] is False
          and r["fall_stage"] == -1 and r["warzone_posture"] is None, (fired, r))
    check("default: chain enabled", G.ShadowBlackboard(log).fall_enabled is True)
    check("no log written by the chain step", not os.path.exists(log))

    print("%d/%d checks passed" % (len(RAN) - len(FAILS), len(RAN)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
