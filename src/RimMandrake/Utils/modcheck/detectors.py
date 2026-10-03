"""Pure detectors over a Snapshot (see snapshot.py).  No bridge access here.

Plan: design/RimMandrake/northstar_helpers_plan.md section 3 (catalogue) as
overridden by section 10 (binding revisions).

    sweep(snap, baseline, expectations=None, anchor=None) -> [Hit]

Rules that hold across every detector:
  * evidence_truncated_or_stale runs FIRST; any absence-based hit from a source
    it marks incomplete is suppressed (E3: truncation is not a vanished pawn).
  * Expectations suppress only the PRESENCE alarm of the matching entity;
    expected_contract_broken fires if an expected entity died / despawned /
    changed faction.
  * Letters are diffed as a FINGERPRINT MULTISET against the baseline, never by
    "arrivalTick > t0" (letters persist and share ticks).
  * Several corroborating signals for one death are ONE colonist_died event.
  * Severity lives in SEVERITY / LETTER_SEVERITY below and nowhere else.
"""

import re
from collections import Counter
from dataclasses import dataclass, field

INFO, WARN, SURPRISE, FATAL = "INFO", "WARN", "SURPRISE", "FATAL"
SEV_RANK = {INFO: 0, WARN: 1, SURPRISE: 2, FATAL: 3}

# ---- the ONE severity table ----------------------------------------------------
SEVERITY = {
    "listing_truncated": WARN,
    "evidence_stale": WARN,
    "colonist_died": FATAL,
    "colonist_downed": SURPRISE,
    "colonist_injured_unexpectedly": SURPRISE,
    "health_progression": WARN,
    "hostile_pawns": SURPRISE,
    "wildlife_near_colonist": WARN,       # SURPRISE when the animal is NEW since the baseline
    "raid_arrived": SURPRISE,
    "mental_break": SURPRISE,
    "fire_on_map": SURPRISE,
    "item_vanished": SURPRISE,
    "condition_unexpected": WARN,
    "modal_open": SURPRISE,
    "log_errors": WARN,
    "strangers_near_anchor": WARN,
    "map_context_changed": WARN,
    "settings_drift": WARN,
    "pawn_roster_transition": WARN,
    "expected_contract_broken": SURPRISE,
    "letter_unexpected": WARN,          # default; per-LetterDef below
    # direct reads from the companion tools (pawn_census / damage_log / incident_queue_peek)
    "predator_hunting": SURPRISE,
    "colonist_damaged": SURPRISE,
    "incident_queued": WARN,            # SURPRISE for a threat incident (THREAT_INCIDENT_WORDS)
}
LETTER_SEVERITY = {"NeutralEvent": INFO, "PositiveEvent": INFO, "NegativeEvent": WARN,
                   "Death": SURPRISE, "ThreatBig": SURPRISE, "ThreatSmall": SURPRISE}
SURPRISE_CONDITION_WORDS = ("toxic", "flashstorm", "eclipse")   # condition defs that escalate
AGGRESSIVE_MENTAL = ("berserk", "manhunter", "murderousrage", "slaughterer")
THREAT_INCIDENT_WORDS = ("raid", "manhunter", "infestation", "siege", "mechcluster", "ambush")

# hediff def -> cause class.  Honest 'unknown' when absent (not in table).
HEDIFF_CAUSE = {
    "Burn": "fire", "Bite": "animal", "Scratch": "animal",
    "Gunshot": "weapon", "Cut": "weapon", "Stab": "weapon", "Shredded": "weapon",
    "Crush": "collapse", "Malnutrition": "starvation", "Starvation": "starvation",
    "Heatstroke": "heat", "Hypothermia": "cold", "Frostbite": "cold",
    "ToxicBuildup": "toxic", "Flu": "disease", "Plague": "disease",
    "Malaria": "disease", "FoodPoisoning": "disease",
}
WEAPON_CAUSES = ("weapon",)
# Hediffs that a mod's own AMBIENT WEATHER / game condition applies to every exposed colonist by design (TheRot's
# Sheen weathers, BlueDesert's Haze, LeaningScrub's Gale). Their arrival is the mechanic working, never an injury:
# listing them as colonist_injured_unexpectedly aborted every later component of a chain (2026-10-03, WeepingStones/
# Cauldron/LeaningScrub/BlueDesert). A chain that TESTS one asserts it with its own component.
AMBIENT_WEATHER_HEDIFFS = frozenset(("RM_SheenCoating", "RM_HazeFilm", "RM_GaleDeafened"))
HOSTILE_NEAR_CELLS = 30
FAR_CELLS = 40
RAID_WINDOW_TICKS = 600
STALE_TICKS = 120
PROGRESSION_DELTA = 0.1
STRANGER_RADIUS = 30

MENTAL_LABEL_RE = re.compile(
    r"(spree|berserk|mental break|tantrum|binge|sad wander|fire-starting|"
    r"slaughter|murderous|catatonic|giving up|wander)", re.I)
COMPANION_LABEL_RE = re.compile(r"opportunity for (.+?)\s*$")
DEATH_LABEL_RE = re.compile(r"^\s*Death:\s*(.+?)\s*$")


@dataclass
class Hit:
    detector: str
    severity: str
    summary: str
    evidence: dict = field(default_factory=dict)
    suggest: list = field(default_factory=list)
    focus: tuple = None
    fingerprint: str = ""


def _hit(detector, summary, evidence=None, suggest=(), focus=None, fp=None, severity=None):
    return Hit(detector, severity or SEVERITY[detector], summary, evidence or {},
               list(suggest), focus, fp if fp is not None else detector)


# ---- expectations ---------------------------------------------------------------

PAWN_KINDS = ("hostile", "pawn")        # kinds whose contract can break


class _Exp(object):
    def __init__(self, kind, matcher, until_tick, phase):
        self.kind, self.matcher, self.until_tick, self.phase = kind, matcher, until_tick, phase
        self.bound = {}                 # pawn id -> faction when first seen (contract)

    def match(self, entity):
        m = self.matcher
        if callable(m):
            return bool(m(entity))
        for k, v in m.items():
            if k == "label_contains":
                if v not in (entity.get("label") or ""):
                    return False
            elif entity.get(k) != v:
                return False
        return True


class Expectations(object):
    """What a chain declares it caused itself.

    kinds: 'hostile' | 'pawn' (presence alarms of that entity), 'letter',
    'condition', 'fire', 'litter' (a sacrificial colonist whose death is the
    test's own act), 'mental' (a pawn the test drove into a mental state; the matcher is tried against the
    pawn row, which carries `id`/`name`, AND against the break's letter, which carries `label`, so a callable
    can serve both), 'incident' (a queue row {defName, fireTick} the test scheduled itself), 'raid' (the test
    fires a raid itself: its threat letter and the raid counter stop being a `raid_arrived` signal; the
    raiders still need their own 'hostile' declaration, best bounded by `phase` so the test may kill them
    afterwards).  matcher: dict of field==value (letters also take
    'label_contains') or a callable(entity)->bool.  until_tick / phase bound the
    lifetime; expired or other-phase expectations match nothing.
    """

    def __init__(self):
        self.items = []
        self.phase = None

    def expect(self, kind, matcher, until_tick=None, phase=None):
        e = _Exp(kind, matcher, until_tick, phase)
        self.items.append(e)
        return e

    def set_phase(self, phase):
        self.phase = phase

    def _live(self, e, tick):
        if e.until_tick is not None and tick is not None and tick > e.until_tick:
            return False
        return e.phase is None or e.phase == self.phase

    def live(self, kinds, tick):
        return [e for e in self.items if e.kind in kinds and self._live(e, tick)]

    # A 'fixture' is something the TEST ITSELF spawned (a walker, a droid, a trap victim): exempt from the
    # presence/death/downed alarms of the kinds below, and deliberately NOT in PAWN_KINDS, so its death or
    # containment is never an `expected_contract_broken` (tests kill and capture their own subjects).
    FIXTURE_EXEMPT = ("hostile", "pawn", "litter", "fixture")

    def matches(self, kind, entity, tick=None):
        kinds = (kind, "fixture") if kind in self.FIXTURE_EXEMPT else (kind,)
        return any(e.match(entity) for e in self.live(kinds, tick))


# ---- shared helpers -----------------------------------------------------------------

def is_colonist(p):
    """isPlayer != colonist (plan 10.6): animals/mechs of the player faction are not.
    Uses isColonist if the bridge ever supplies it, else the roster heuristic."""
    if not p["isPlayer"] or p["isMechanoid"] or p.get("isSlave") or p.get("isPrisoner"):
        return False
    if p.get("isColonist") is not None:
        return bool(p["isColonist"])
    return p.get("intelligence") == "Humanlike"


def _focus(p):
    return (p["x"], p["z"]) if p.get("x") is not None else None


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _pawns_by_id(snap):
    return {p["id"]: p for p in snap["pawns"]}


def new_letters(snap, baseline):
    """Letters in snap beyond the baseline MULTISET, with multiplicity.
    Returns list of (letter, extra_count) per distinct fingerprint."""
    cur = Counter(l["fingerprint"] for l in snap["letters"])
    out = []
    seen = set()
    for l in snap["letters"]:
        fp = l["fingerprint"]
        if fp in seen:
            continue
        seen.add(fp)
        extra = cur[fp] - baseline.letters.get(fp, 0)
        if extra > 0:
            out.append((l, extra))
    return out


def death_name(label):
    m = DEATH_LABEL_RE.match(label or "")
    return m.group(1) if m else None


def _source_usable(snap, name):
    s = snap["sources"][name]
    return s["read"] and s["complete"]


# ---- 1. evidence_truncated_or_stale (runs FIRST) -----------------------------------------

def evidence_truncated_or_stale(snap, baseline):
    """-> (hits, suppressed) where suppressed = source names that must not feed
    absence-based hits.  Unread sources (skipped by tier) are not reported."""
    hits, suppressed = [], set()
    for name, s in snap["sources"].items():
        if not s["read"]:
            suppressed.add(name)                 # unread: silence, but no hit
            continue
        if s["error"]:
            suppressed.add(name)
            hits.append(_hit("evidence_stale",
                             "source %s failed to read (%s); absence-based checks on it are off"
                             % (name, s["error"]),
                             {"source": name, "error": s["error"]},
                             fp="evidence_stale:%s:err" % name))
        elif not s["complete"]:
            suppressed.add(name)
            hits.append(_hit("listing_truncated",
                             "%s listing is truncated (%s of %s returned); nothing is reported missing from it"
                             % (name, s.get("truncated_count") and "beyond the limit" or "partial",
                                s.get("total") if s.get("total") is not None else "?"),
                             {"source": name, "truncated": s.get("truncated_count"),
                              "totalOnMap": s.get("total")},
                             suggest=["re-read with a rect or a higher limit"],
                             fp="listing_truncated:%s" % name))
        st = s.get("source_tick")
        if st is not None and snap["tick"] is not None and abs(snap["tick"] - st) > STALE_TICKS:
            suppressed.add(name)
            hits.append(_hit("evidence_stale",
                             "source %s was read at tick %s but the snapshot is tick %s" %
                             (name, st, snap["tick"]),
                             {"source": name, "source_tick": st, "tick": snap["tick"]},
                             fp="evidence_stale:%s:tick" % name))
    return hits, suppressed


# ---- deaths (aggregated) -----------------------------------------------------------------

def colonist_died(snap, baseline, exps, ctx):
    """One FATAL hit per dead colonist, merging row / Death-letter / story_stats signals."""
    events = {}          # key -> {"names","ticks","sources","ids","focus"}
    tick = snap["tick"]
    excluded = set()     # declared-sacrificial (litter) victims: still counted by story_stats

    def ev(key):
        return events.setdefault(key, {"name": key, "ticks": set(), "sources": set(),
                                       "ids": set(), "focus": None})

    for p in snap["pawns"]:
        if is_colonist(p) and p["dead"] and p["id"] not in baseline.dead_ids:
            if exps.matches("litter", p, tick):
                excluded.add(p["name"] or p["id"])
                continue
            e = ev(p["name"] or p["id"])
            e["sources"].add("pawn_row_dead")
            e["ids"].add(p["id"])
            e["focus"] = _focus(p)
    for l, extra in new_letters(snap, baseline):
        if l["defName"] != "Death":
            continue
        nm = death_name(l["label"]) or l["label"]
        if re.search(r"\([^)]+\)", nm):
            # MEASURED live 2026-10-01 (Antiquities, 95000-tick chain): the colony dog's death letter
            # "Marina (husky) (bonded)" read as a COLONIST death and aborted the chain. A human's death
            # letter is the bare name; an animal's carries its species in parentheses. Not a colonist.
            ctx["consumed"].add(l["fingerprint"])
            continue
        if exps.matches("litter", {"name": nm}, tick):
            excluded.add(nm)
            ctx["consumed"].add(l["fingerprint"])
            continue
        e = ev(nm)
        e["sources"].add("death_letter")
        e["ticks"].add(l["arrivalTick"])
        ctx["consumed"].add(l["fingerprint"])
    if _damage_ok(ctx, snap):
        by_id = _pawns_by_id(snap)
        for d in snap["damage_events"]:
            if d.get("kind") != "kill" or not d.get("victimColonist"):
                continue
            p = by_id.get(d.get("victimId")) or {"id": d.get("victimId"), "name": None}
            key = p.get("name") or p["id"]
            if key in excluded or exps.matches("litter", p, tick) or exps.matches("fixture", p, tick):
                excluded.add(key)
                continue
            e = ev(key)
            e["sources"].add("damage_log_kill")
            e["ids"].add(p["id"])
            if d.get("tick") is not None:
                e["ticks"].add(d["tick"])
    # a death also emits a companion NeutralEvent "... opportunity for <name>" (real, E1 + probe):
    # it belongs to the death, never a second hit
    for l, extra in new_letters(snap, baseline):
        m = COMPANION_LABEL_RE.search(l["label"] or "")
        if l["defName"] == "NeutralEvent" and m and m.group(1) in events:
            ctx["consumed"].add(l["fingerprint"])
    delta = (snap["story"].get("colonistsKilled", 0) - baseline.story.get("colonistsKilled", 0)
             if "colonistsKilled" in snap["story"] and "colonistsKilled" in baseline.story else 0)
    for i in range(max(0, delta - len(events) - len(excluded))):
        e = ev("unattributed#%d" % (i + 1))
        e["sources"].add("story_stats_delta")
    hits = []
    for key in sorted(events):
        e = events[key]
        if "story_stats_delta" in e["sources"] and len(e["sources"]) == 1 and \
                not events[key]["ids"] and not events[key]["ticks"]:
            fp = "colonist_died:" + key
        else:
            fp = "colonist_died:" + key
        hits.append(_hit("colonist_died",
                         "colonist %s died (%s)" % (key, "+".join(sorted(e["sources"]))),
                         {"name": key, "ticks": sorted(t for t in e["ticks"] if t is not None),
                          "sources": sorted(e["sources"]), "ids": sorted(e["ids"]),
                          "colonistsKilled_delta": delta},
                         suggest=["restore_colonists"], focus=e["focus"], fp=fp))
    return hits


def colonist_downed(snap, baseline, exps, ctx):
    base = _pawns_by_id(baseline.snap)
    hits = []
    for p in snap["pawns"]:
        if not is_colonist(p) or p["dead"] or not p["spawned"]:
            continue
        if exps.matches("fixture", p, snap["tick"]):
            continue
        b = base.get(p["id"])
        was_down = b["downed"] if b else False
        was_bleed = (b["bleedRate"] or 0) > 0 if b else False
        bleeding = (p["bleedRate"] or 0) > 0
        if (p["downed"] and not was_down) or (bleeding and not was_bleed):
            hits.append(_hit("colonist_downed",
                             "colonist %s is %s" % (p["name"], "downed" if p["downed"] else "bleeding"),
                             {"id": p["id"], "name": p["name"], "downed": p["downed"],
                              "bleedRate": p["bleedRate"], "painTotal": p["painTotal"]},
                             suggest=["restore_colonists"], focus=_focus(p),
                             fp="colonist_downed:%s:%s" % (p["id"], p["downed"])))
    return hits


def _cause_for(defn, pawn, snap):
    c = HEDIFF_CAUSE.get(defn)
    if c is None:
        return "unknown"
    if c in WEAPON_CAUSES and pawn.get("x") is not None:
        for h in snap["pawns"]:
            if h["hostile"] and not h["dead"] and h.get("x") is not None and \
                    _dist((h["x"], h["z"]), (pawn["x"], pawn["z"])) <= HOSTILE_NEAR_CELLS:
                return "raid"
    return c


def colonist_injured_unexpectedly(snap, baseline, exps, ctx):
    hits = []
    for p in snap["pawns"]:
        if not is_colonist(p) or p["dead"] or p["hediffs"] is None:
            continue
        if p["id"] not in baseline.hediff_known:
            continue        # no baseline health for this pawn: cannot diff, never guess
        new, grown = [], []
        explained = set()
        for e in (ctx.get("damaged") or {}).get(p["id"], []):
            explained.add(e.get("damageDef"))
            explained.update(e.get("hediffsAdded") or [])
        for h in p["hediffs"]:
            key = (p["id"], h["def"], h["part"])
            if key not in baseline.hediffs:
                if h["def"] in explained:
                    continue          # colonist_damaged already reported it, with the real cause
                if h["def"] in AMBIENT_WEATHER_HEDIFFS:
                    continue          # a mod's ambient weather working as designed, not an injury
                new.append(h)
            elif (h["severity"] or 0) - baseline.hediffs[key] >= PROGRESSION_DELTA:
                grown.append({"def": h["def"], "part": h["part"],
                              "before": baseline.hediffs[key], "after": h["severity"]})
        if new:
            causes = sorted({_cause_for(h["def"], p, snap) for h in new})
            known = [c for c in causes if c != "unknown"]
            # one known class wins (unmapped defs, e.g. a Crack fracture riding a Cut, are listed
            # in evidence); several known classes -> 'mixed'; none -> honest 'unknown'
            hint = known[0] if len(known) == 1 else ("mixed:" + ",".join(known) if known else "unknown")
            hits.append(_hit("colonist_injured_unexpectedly",
                             "colonist %s gained %d new hediff(s) (%s); cause_hint=%s" %
                             (p["name"], len(new), ",".join(sorted({h["def"] for h in new})), hint),
                             {"id": p["id"], "name": p["name"], "new_hediffs": new,
                              "cause_hint": hint, "causes": causes,
                              "unmapped_defs": sorted({h["def"] for h in new if h["def"] not in HEDIFF_CAUSE})},
                             suggest=["restore_colonists"], focus=_focus(p),
                             fp="colonist_injured:%s:%s" % (p["id"], ",".join(
                                 sorted("%s@%s" % (h["def"], h["part"]) for h in new)))))
        if grown:
            hits.append(_hit("health_progression",
                             "colonist %s: %d existing hediff(s) worsened" % (p["name"], len(grown)),
                             {"id": p["id"], "name": p["name"], "grown": grown},
                             focus=_focus(p),
                             fp="health_progression:%s:%s" % (p["id"], ",".join(
                                 sorted("%s@%s" % (g["def"], g["part"]) for g in grown)))))
    return hits


def hostile_pawns(snap, baseline, exps, ctx, anchor=None):
    base = _pawns_by_id(baseline.snap)
    rows = [p for p in snap["pawns"] if p["hostile"] and not p["dead"] and p["spawned"]
            and not exps.matches("hostile", p, snap["tick"])]
    if not rows:
        return []
    ctx["hostiles"] = rows
    sev = SURPRISE
    if anchor is not None and all(p["x"] is not None and _dist((p["x"], p["z"]), anchor) > FAR_CELLS and
                                  p["id"] in base and (base[p["id"]]["x"], base[p["id"]]["z"]) == (p["x"], p["z"])
                                  for p in rows):
        sev = WARN
    return [_hit("hostile_pawns",
                 "%d hostile-flagged pawn(s) outside the expected set (hostile != confirmed threat)" % len(rows),
                 {"pawns": [{"id": p["id"], "kindDef": p["kindDef"], "faction": p["faction"],
                             "x": p["x"], "z": p["z"]} for p in rows], "threat_confirmed": False},
                 suggest=["kill_hostiles"], focus=_focus(rows[0]), severity=sev,
                 fp="hostile_pawns:" + ",".join(sorted(p["id"] for p in rows)))]


WILDLIFE_RADIUS = 12   # cells (Chebyshev) from any living colonist

def wildlife_near_colonist(snap, baseline, exps, ctx):
    """Predator detection that does NOT rely on `hostile` (MEASURED 2026-10-01: a factionless wolf reads
    hostile:false). Any wild animal (faction None, intelligence Animal, spawned, alive) within
    WILDLIFE_RADIUS of a living colonist is reported: WARN if it was already on the map at the baseline,
    SURPRISE if it arrived after. On a bland map there should be none. Intent is NOT inferred here: with the
    pawn census read, each row carries the direct `hunting` flag and predator_hunting raises the hunt
    itself; without the census `hunting` is None (unmeasured)."""
    cols = [p for p in snap["pawns"] if is_colonist(p) and not p["dead"] and p["spawned"] and p["x"] is not None]
    if not cols:
        return []
    out_rows, new_ids = [], set()
    for p in snap["pawns"]:
        if (p["faction"] is not None or p["intelligence"] != "Animal" or p["dead"] or not p["spawned"]
                or p["x"] is None or exps.matches("hostile", p, snap["tick"]) or exps.matches("pawn", p, snap["tick"])):
            continue
        d = min(_dist((p["x"], p["z"]), (c["x"], c["z"])) for c in cols)
        if d <= WILDLIFE_RADIUS:
            out_rows.append((p, d))
            if p["id"] not in baseline.pawn_ids:
                new_ids.add(p["id"])
    if not out_rows:
        return []
    out_rows.sort(key=lambda r: r[1])
    return [_hit("wildlife_near_colonist",
                 "%d wild animal(s) within %d cells of a colonist (%d new since baseline); proximity only, "
                 "hunting intent unmeasured" % (len(out_rows), WILDLIFE_RADIUS, len(new_ids)),
                 {"animals": [{"id": p["id"], "kindDef": p["kindDef"], "x": p["x"], "z": p["z"], "dist": d,
                               "new": p["id"] in new_ids,
                               "hunting": p.get("isPredatorHunting") if p.get("census") else None}
                              for p, d in out_rows[:10]]},
                 suggest=["kill_wildlife"], focus=_focus(out_rows[0][0]),
                 severity=SURPRISE if new_ids else WARN,
                 fp="wildlife_near_colonist:" + ",".join(sorted(p["id"] for p, _ in out_rows)))]


def raid_arrived(snap, baseline, exps, ctx):
    sig = []
    declared = bool(exps.live(("raid",), snap["tick"]))    # t.expect("raid", {}): the TEST fired this raid
    for l, extra in new_letters(snap, baseline):
        if l["defName"] in ("ThreatBig", "ThreatSmall"):
            if exps.matches("letter", l, snap["tick"]):
                continue
            ctx["consumed"].add(l["fingerprint"])
            if declared:
                continue
            sig.append(("letter", l["arrivalTick"], l["label"]))
    cur, base = snap["story"].get("numRaidsEnemy"), baseline.story.get("numRaidsEnemy")
    if cur is not None and base is not None and cur > base and not declared:
        sig.append(("story_stats", baseline.tick, "numRaidsEnemy %s->%s" % (base, cur)))
    if not sig:
        return []
    first = min(s[1] for s in sig if s[1] is not None) if any(s[1] is not None for s in sig) else baseline.tick
    hostiles = ctx.get("hostiles") or [p for p in snap["pawns"] if p["hostile"] and not p["dead"]]
    open_ = not hostiles and (snap["tick"] is None or first is None or snap["tick"] - first < RAID_WINDOW_TICKS)
    return [_hit("raid_arrived",
                 "raid signal(s): %s; %s" % ("; ".join(s[2] for s in sig),
                                             "hostiles seen" if hostiles else
                                             ("open, awaiting arrivals" if open_ else "window passed, no hostiles seen")),
                 {"signals": [list(s) for s in sig], "open": open_, "hostiles_seen": len(hostiles)},
                 suggest=["kill_hostiles"],
                 fp="raid_arrived:" + "|".join("%s@%s" % (s[0], s[1]) for s in sig))]


def _ms_def(ms):
    """A census mentalState is a dict {def, isAggro, ...}; an older/guessed field may be a bare string."""
    return ms.get("def") if isinstance(ms, dict) else ms


def mental_break(snap, baseline, exps, ctx):
    """With the pawn census read, `mentalState` is a DIRECT read and aggression is the game's own
    `isAggro`; without it the field is absent from list_pawns and only the letter path speaks."""
    hits = []
    base = _pawns_by_id(baseline.snap)
    for p in snap["pawns"]:
        ms = p.get("mentalState")
        if ms and not (base.get(p["id"]) or {}).get("mentalState"):
            if exps.matches("fixture", p, snap["tick"]) or exps.matches("mental", p, snap["tick"]):
                continue
            d = _ms_def(ms)
            aggro = ms.get("isAggro") if isinstance(ms, dict) else any(w in str(ms).lower() for w in AGGRESSIVE_MENTAL)
            sev = FATAL if aggro and is_colonist(p) else None
            hits.append(_hit("mental_break", "%s entered mental state %s%s" % (p["name"], d, " (aggro)" if aggro else ""),
                             {"id": p["id"], "mentalState": d, "isAggro": bool(aggro),
                              "via": "pawn_census" if isinstance(ms, dict) else "list_pawns"},
                             suggest=["calm_colonists"], focus=_focus(p), severity=sev,
                             fp="mental_break:%s:%s" % (p["id"], d)))
    for l, extra in new_letters(snap, baseline):
        if l["defName"] == "NegativeEvent" and MENTAL_LABEL_RE.search(l["label"]) \
                and not exps.matches("letter", l, snap["tick"]):
            if exps.matches("mental", l, snap["tick"]):
                ctx["consumed"].add(l["fingerprint"])       # the induced break's own letter: consumed, not a hit
                continue
            ctx["consumed"].add(l["fingerprint"])
            if hits:            # the census already named the break; the letter is its echo, not a second event
                continue
            hits.append(_hit("mental_break", "mental-break letter: %s" % l["label"],
                             {"label": l["label"], "arrivalTick": l["arrivalTick"], "count": extra, "via": "letter"},
                             suggest=["calm_colonists"], fp="mental_break:letter:%r" % (l["fingerprint"],)))
    return hits


def predator_hunting(snap, baseline, exps, ctx):
    """DIRECT read (pawn_census isPredatorHunting + preyId): a predator whose prey is a player pawn.
    Replaces proximity inference for intent; wildlife_near_colonist still reports proximity."""
    if "pawn_census" in ctx["suppressed"]:
        return []
    by_id = _pawns_by_id(snap)
    hits = []
    for p in snap["pawns"]:
        if not p.get("isPredatorHunting") or p["dead"]:
            continue
        prey = by_id.get(p.get("preyId"))
        if prey is None or not prey["isPlayer"]:
            continue
        if exps.matches("fixture", prey, snap["tick"]) or exps.matches("hostile", p, snap["tick"]):
            continue
        hits.append(_hit("predator_hunting", "%s (%s) is hunting player pawn %s" % (p["name"], p["kindDef"], prey["name"]),
                         {"predator": p["id"], "kindDef": p["kindDef"], "preyId": prey["id"],
                          "preyIsColonist": is_colonist(prey), "via": "pawn_census"},
                         suggest=["kill_wildlife"], focus=_focus(p),
                         fp="predator_hunting:%s:%s" % (p["id"], prey["id"])))
    return hits


def _damage_ok(ctx, snap):
    return "damage_log" not in ctx["suppressed"] and snap.get("damage_next_seq") is not None


def colonist_damaged(snap, baseline, exps, ctx):
    """DIRECT read (damage_log): every damage event on a colonist since the baseline, with the game's
    own damageDef / instigator / weapon. The cause is read, never guessed from a hediff table."""
    if not _damage_ok(ctx, snap):
        return []
    by_id = _pawns_by_id(snap)
    rows = {}
    for e in snap["damage_events"]:
        if e.get("kind") != "damage" or not e.get("victimColonist"):
            continue
        vid = e.get("victimId")
        p = by_id.get(vid) or {"id": vid, "name": vid}
        if exps.matches("fixture", p, snap["tick"]) or exps.matches("litter", p, snap["tick"]):
            continue
        rows.setdefault(vid, []).append(e)
        ctx.setdefault("damaged", {}).setdefault(vid, []).append(e)
    hits = []
    for vid in sorted(rows):
        evs = rows[vid]
        p = by_id.get(vid) or {}
        causes = sorted({"%s by %s" % (e.get("damageDef"), e.get("instigatorDef") or e.get("instigatorId") or "nobody")
                         for e in evs})
        hits.append(_hit("colonist_damaged", "colonist %s took %d damage event(s): %s"
                         % (p.get("name") or vid, len(evs), "; ".join(causes)),
                         {"id": vid, "events": [{k: e.get(k) for k in ("seq", "tick", "damageDef", "amount", "instigatorId",
                                                                      "instigatorDef", "weapon", "hediffsAdded")}
                                                for e in evs[:10]], "via": "damage_log"},
                         suggest=["restore_colonists"], focus=_focus(p) if p.get("x") is not None else None,
                         fp="colonist_damaged:%s:%s" % (vid, ",".join(str(e.get("seq")) for e in evs))))
    return hits


def incident_queued(snap, baseline, exps, ctx):
    """DIRECT read (incident_queue_peek): an incident queued since the baseline -- seen BEFORE it fires."""
    if "incident_queue_peek" in ctx["suppressed"] or not snap["sources"]["incident_queue_peek"]["read"]:
        return []
    base = Counter(baseline.incident_queue)
    hits = []
    for q in snap["incident_queue"]:
        key = (q["defName"], q["fireTick"])
        if base[key] > 0:
            base[key] -= 1
            continue
        if exps.matches("incident", q, snap["tick"]):
            continue
        threat = any(w in (q["defName"] or "").lower() for w in THREAT_INCIDENT_WORDS)
        hits.append(_hit("incident_queued", "incident %s queued to fire in %s ticks"
                         % (q["defName"], q.get("ticksUntilFire")),
                         dict(q, via="incident_queue_peek", threat=threat), suggest=["clear_incident_queue"],
                         severity=SURPRISE if threat else None,
                         fp="incident_queued:%s:%s" % key))
    return hits


def fire_on_map(snap, baseline, exps, ctx):
    if "list_things" in ctx["suppressed"] or snap.get("things_query") != "Fire":
        return []
    fires = [t for t in snap["things"] if t["def"] == "Fire" and not exps.matches("fire", t, snap["tick"])]
    base_n = baseline.item_totals.get("Fire", 0) if baseline.snap.get("things_query") == "Fire" else 0
    if len(fires) <= base_n:
        return []
    return [_hit("fire_on_map", "%d fire(s) on the map outside the expected set" % len(fires),
                 {"fires": [{"x": t["x"], "z": t["z"]} for t in fires]}, suggest=["extinguish"],
                 focus=(fires[0]["x"], fires[0]["z"]),
                 fp="fire_on_map:%d" % len(fires))]


def item_vanished(snap, baseline, exps, ctx):
    """Compares TOTAL quantity per def (a vanished id may just be a stack merge)."""
    if "list_things" in ctx["suppressed"]:
        return []
    bs = baseline.snap["sources"]["list_things"]
    if not (bs["read"] and bs["complete"]) or snap.get("things_query") != baseline.snap.get("things_query"):
        return []
    hits = []
    for d, was in sorted(baseline.item_totals.items()):
        now = snap["item_totals"].get(d, 0)
        if now < was:
            hits.append(_hit("item_vanished",
                             "total %s dropped %s -> %s (cause unknown: not hauled/merged within the listing)"
                             % (d, was, now), {"def": d, "before": was, "after": now, "cause_hint": "unknown"},
                             suggest=["forbid_and_wall"], fp="item_vanished:%s:%s" % (d, now)))
    return hits


_LETTER_DONE = ("Death", "ThreatBig", "ThreatSmall")


def letter_unexpected(snap, baseline, exps, ctx):
    hits = []
    for l, extra in new_letters(snap, baseline):
        if l["fingerprint"] in ctx["consumed"] or exps.matches("letter", l, snap["tick"]):
            continue
        sev = LETTER_SEVERITY.get(l["defName"], SEVERITY["letter_unexpected"])
        hits.append(_hit("letter_unexpected",
                         "new letter [%s] %s%s" % (l["defName"], l["label"], " x%d" % extra if extra > 1 else ""),
                         {"defName": l["defName"], "label": l["label"], "arrivalTick": l["arrivalTick"],
                          "count": extra, "known_defName": l["defName"] in LETTER_SEVERITY},
                         severity=sev, fp="letter_unexpected:%r" % (l["fingerprint"],)))
    return hits


def condition_unexpected(snap, baseline, exps, ctx):
    if "weather_get" in ctx["suppressed"]:
        return []
    hits = []
    for c in snap["conditions"]:
        if c["def"] in baseline.conditions or not c.get("affectsThisMap", True) \
                or exps.matches("condition", c, snap["tick"]):
            continue
        sev = SURPRISE if any(w in (c["def"] or "").lower() for w in SURPRISE_CONDITION_WORDS) else None
        hits.append(_hit("condition_unexpected", "game condition %s began" % c["def"],
                         {"def": c["def"], "scope": c["scope"]}, suggest=["end_conditions"],
                         severity=sev, fp="condition_unexpected:%s" % c["def"]))
    return hits


def modal_open(snap, baseline, exps, ctx):
    if "window_list_close" in ctx["suppressed"]:
        return []
    ws = [w for w in snap["windows"] if w["forcePause"] and not w["isDebug"]
          # MEASURED live 2026-10-01: a quicktest/founded colony re-raises Dialog_NamePlayerFactionAndSettlement /
          # Dialog_NamePlayerSettlement every ~600 ticks until named, closing it never sticks, and it blocks nothing
          # the harness drives (ticks advance). Colony-naming prompts are not a surprise.
          and "Dialog_NamePlayer" not in str(w["type"])]
    if not ws:
        return []
    return [_hit("modal_open", "%d force-pause modal(s) open: %s" % (len(ws), ", ".join(str(w["type"]) for w in ws)),
                 {"windows": ws}, suggest=["close_modals"],
                 fp="modal_open:" + ",".join(sorted(str(w["type"]) for w in ws)))]


def log_errors(snap, baseline, exps, ctx):
    seen = {m["text"] for m in baseline.snap["log_errors"]}
    new = [m for m in snap["log_errors"] if m["text"] not in seen]
    if not new:
        return []
    return [_hit("log_errors", "%d new error message(s) in the log" % len(new),
                 {"messages": [{"text": (m["text"] or "")[:200], "repeats": m["repeats"]} for m in new]},
                 fp="log_errors:%d:%s" % (len(new), hash_text("".join(m["text"] or "" for m in new))))]


def hash_text(s):
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return "%08x" % h


def strangers_near_anchor(snap, baseline, exps, ctx, anchor=None, radius=STRANGER_RADIUS):
    if anchor is None or "list_pawns" in ctx["suppressed"]:
        return []
    rows = [p for p in snap["pawns"] if not p["isPlayer"] and not p["hostile"] and not p["dead"]
            and p["spawned"] and p["x"] is not None and _dist((p["x"], p["z"]), anchor) <= radius
            and not exps.matches("pawn", p, snap["tick"])]
    if not rows:
        return []
    return [_hit("strangers_near_anchor", "%d non-player pawn(s) within %d cells of the anchor" % (len(rows), radius),
                 {"pawns": [{"id": p["id"], "kindDef": p["kindDef"], "faction": p["faction"]} for p in rows]},
                 suggest=["clear_strangers"], focus=_focus(rows[0]),
                 fp="strangers:" + ",".join(sorted(p["id"] for p in rows)))]


def map_context_changed(snap, baseline):
    why = []
    if snap["epoch"] != baseline.epoch:
        why.append("epoch %s->%s" % (baseline.epoch, snap["epoch"]))
    if snap["map_id"] is not None and baseline.map_id is not None and snap["map_id"] != baseline.map_id:
        why.append("map %s->%s" % (baseline.map_id, snap["map_id"]))
    if snap["tick"] is not None and baseline.tick is not None and snap["tick"] < baseline.tick:
        why.append("tick went backwards %s->%s" % (baseline.tick, snap["tick"]))
    if not why:
        return []
    return [_hit("map_context_changed", "map context changed (%s); baseline diffs are off" % "; ".join(why),
                 {"reasons": why}, fp="map_context_changed:" + "|".join(why))]


def settings_drift(snap, baseline, exps, ctx):
    cur = snap.get("settings") or {}
    drift = {k: [baseline.settings[k], v] for k, v in cur.items()
             if k in baseline.settings and baseline.settings[k] != v}
    if not drift:
        return []
    return [_hit("settings_drift", "debug settings drifted: %s" % ", ".join(sorted(drift)),
                 {"drift": drift}, fp="settings_drift:" + ",".join(sorted(drift)))]


def pawn_roster_transition(snap, baseline, exps, ctx):
    if "list_pawns" in ctx["suppressed"]:
        return []
    bs = baseline.snap["sources"]["list_pawns"]
    if not (bs["read"] and bs["complete"]):
        return []
    base = _pawns_by_id(baseline.snap)
    cur = _pawns_by_id(snap)

    def tracked(p):          # wildlife churn is noise; players and humanlikes are the roster
        return p["isPlayer"] or p.get("intelligence") == "Humanlike"
    hits = []
    gone = [p for i, p in base.items() if i not in cur and tracked(p) and not exps.matches("pawn", p, snap["tick"])]
    came = [p for i, p in cur.items() if i not in base and tracked(p) and not p["hostile"]
            and not exps.matches("pawn", p, snap["tick"])]
    for p in gone:
        hits.append(_hit("pawn_roster_transition", "pawn %s (%s) left the roster" % (p["name"], p["id"]),
                         {"id": p["id"], "direction": "gone", "faction": p["faction"]},
                         fp="roster:gone:%s" % p["id"]))
    for p in came:
        hits.append(_hit("pawn_roster_transition", "pawn %s (%s) joined the roster" % (p["name"], p["id"]),
                         {"id": p["id"], "direction": "arrived", "faction": p["faction"]},
                         focus=_focus(p), fp="roster:arrived:%s" % p["id"]))
    return hits


def expected_contract_broken(snap, baseline, exps, ctx):
    hits = []
    tick = snap["tick"]
    cur = _pawns_by_id(snap)
    listing_ok = "list_pawns" not in ctx["suppressed"]
    for e in exps.live(PAWN_KINDS, tick):
        rows = [p for p in snap["pawns"] if e.match(p)]
        for p in rows:
            was = e.bound.setdefault(p["id"], p["faction"])
            why = None
            if p["dead"]:
                why = "died"
            elif not p["spawned"]:
                why = "despawned"
            elif p["faction"] != was:
                why = "changed faction %s->%s" % (was, p["faction"])
            if why:
                hits.append(_hit("expected_contract_broken",
                                 "expected %s %s %s" % (e.kind, p["id"], why),
                                 {"id": p["id"], "kind": e.kind, "why": why}, focus=_focus(p),
                                 fp="contract:%s:%s:%s" % (e.kind, p["id"], why.split()[0])))
        if not rows and e.bound and listing_ok:
            for pid in sorted(e.bound):
                if pid not in cur:
                    hits.append(_hit("expected_contract_broken",
                                     "expected %s %s no longer in a complete listing" % (e.kind, pid),
                                     {"id": pid, "kind": e.kind, "why": "missing"},
                                     fp="contract:%s:%s:missing" % (e.kind, pid)))
    return hits


# ---- sweep -----------------------------------------------------------------------------------

def sweep(snap, baseline, expectations=None, anchor=None):
    exps = expectations or Expectations()
    hits, suppressed = evidence_truncated_or_stale(snap, baseline)
    ctx = {"suppressed": suppressed, "consumed": set(), "damaged": {}}
    ctxhits = map_context_changed(snap, baseline)
    hits += ctxhits
    if ctxhits:
        # baseline diffs are meaningless across an epoch/map change: report only that.
        return _order(hits)
    # presence/absence of pawn rows depends on the pawns source being usable
    pawn_ok = "list_pawns" not in suppressed
    hits += colonist_damaged(snap, baseline, exps, ctx)    # first: injured_unexpectedly reads ctx["damaged"]
    if pawn_ok:
        hits += colonist_died(snap, baseline, exps, ctx)
        hits += colonist_downed(snap, baseline, exps, ctx)
        hits += colonist_injured_unexpectedly(snap, baseline, exps, ctx)
        hits += hostile_pawns(snap, baseline, exps, ctx, anchor)
        hits += wildlife_near_colonist(snap, baseline, exps, ctx)
        hits += predator_hunting(snap, baseline, exps, ctx)
        hits += mental_break(snap, baseline, exps, ctx)
        hits += strangers_near_anchor(snap, baseline, exps, ctx, anchor)
        hits += pawn_roster_transition(snap, baseline, exps, ctx)
        hits += expected_contract_broken(snap, baseline, exps, ctx)
    elif "letter_list" not in suppressed:
        hits += colonist_died(snap, baseline, exps, ctx)       # letters / stats still speak
        hits += mental_break(snap, baseline, exps, ctx)
    if "letter_list" not in suppressed:
        hits += raid_arrived(snap, baseline, exps, ctx)
        hits += letter_unexpected(snap, baseline, exps, ctx)
    hits += incident_queued(snap, baseline, exps, ctx)
    hits += fire_on_map(snap, baseline, exps, ctx)
    hits += item_vanished(snap, baseline, exps, ctx)
    hits += condition_unexpected(snap, baseline, exps, ctx)
    hits += modal_open(snap, baseline, exps, ctx)
    hits += log_errors(snap, baseline, exps, ctx)
    hits += settings_drift(snap, baseline, exps, ctx)
    return _order(hits)


def _order(hits):
    return sorted(hits, key=lambda h: -SEV_RANK[h.severity])


# ---- dedup ----------------------------------------------------------------------------------

class Dedup(object):
    """Suppresses repeat screenshots for an unchanged hit.

    New fingerprint -> capture.  Same fingerprint inside cooldown_ticks -> no.
    After the cooldown, capture only if the evidence changed."""

    def __init__(self, cooldown_ticks=3000):
        self.cooldown = cooldown_ticks
        self.seen = {}

    @staticmethod
    def _digest(hit):
        return repr(sorted((k, repr(v)) for k, v in hit.evidence.items()))

    def should_capture(self, hit, tick):
        d = self._digest(hit)
        prev = self.seen.get(hit.fingerprint)
        if prev is None:
            self.seen[hit.fingerprint] = (tick, d)
            return True
        last, pd = prev
        if tick is not None and last is not None and tick - last < self.cooldown:
            return False
        if d == pd:
            return False
        self.seen[hit.fingerprint] = (tick, d)
        return True
