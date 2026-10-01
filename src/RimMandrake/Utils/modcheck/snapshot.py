"""Snapshot normalisation for the modcheck situational detectors.

Plan: design/RimMandrake/northstar_helpers_plan.md  (section 2 real result shapes,
section 10 binding revisions).

A Snapshot is ONE plain dict of bridge reads taken together, so every detector
is a pure function over it and runs identically on a recorded fixture.

    normalize(raw_reads) -> Snapshot      pure; no bridge access
    take_snapshot(session, tier)          the only function that calls the bridge
    Baseline                              a Snapshot plus the derived sets that
                                          detectors diff against

Stdlib only; runs under python3 and Windows python.exe.

LAW: a failed or unread source is NEVER an empty source.  Every source carries
`read` / `complete` / `error`; detectors consult them before raising any
absence-based hit.  Per-pawn `hediffs` is None (unknown) when health was not
requested, and [] only when health was read and the pawn has none.
"""

from collections import Counter

SCHEMA_VERSION = 1

TOOLS_TRIPWIRE = ("time_clock", "story_stats", "list_pawns", "letter_list")
TOOLS_FULL = ("time_clock", "story_stats", "list_pawns", "letter_list",
              "alerts_list", "weather_get", "list_things", "drain_log",
              "window_list_close", "map_info")
ALL_SOURCES = TOOLS_FULL


def _short(tool):
    """'jawa/list_pawns' -> 'list_pawns'."""
    return tool.split("/")[-1] if isinstance(tool, str) else tool


def _label_text(label):
    """Letter labels are TaggedString objects: {'RawText': ..., 'Length': ..}."""
    if isinstance(label, dict):
        return str(label.get("RawText", ""))
    return "" if label is None else str(label)


def _src(read=False, complete=False, source_tick=None, error=None):
    return {"read": read, "complete": complete,
            "source_tick": source_tick, "error": error}


# ---- per-source normalisers -------------------------------------------------

def _norm_pawn(p):
    health = p.get("health")
    if isinstance(health, dict):
        hed = []
        for h in health.get("hediffs") or []:
            hed.append({"def": h.get("def"), "label": h.get("label"),
                        "part": h.get("part"), "severity": h.get("severity")})
        bleed = health.get("bleedRate")
        pain = health.get("painTotal")
    else:
        hed, bleed, pain = None, None, None
    return {
        "id": p.get("id"), "name": p.get("name"),
        "kindDef": p.get("kindDef"), "def": p.get("def"),
        "faction": p.get("faction"),            # None == wild
        "isPlayer": bool(p.get("isPlayer")),
        "hostile": bool(p.get("hostile")),
        "dead": bool(p.get("dead")), "downed": bool(p.get("downed")),
        "spawned": bool(p.get("spawned", True)),
        "x": p.get("x"), "z": p.get("z"),
        "intelligence": p.get("intelligence"),
        "isMechanoid": bool(p.get("isMechanoid")),
        # GUESS: roles are not in list_pawns today (gap G9); read if present.
        "isColonist": p.get("isColonist"), "isSlave": p.get("isSlave"),
        "isPrisoner": p.get("isPrisoner"),
        # GUESS: no mentalState field today (gap G1); read if present.
        "mentalState": p.get("mentalState"),
        "hediffs": hed, "bleedRate": bleed, "painTotal": pain,
    }


def _norm_pawns(res, src):
    rows = [_norm_pawn(p) for p in (res.get("pawns") or [])]
    msg = str(res.get("message") or "")
    truncated = ("beyond the limit" in msg) or bool(res.get("truncated"))
    if res.get("isCompleteList") is False:
        truncated = True
    src["complete"] = not truncated
    src["truncated_count"] = res.get("truncated")
    src["total"] = res.get("totalOnMap")
    return rows


def _norm_letters(res, src):
    out = []
    for l in res.get("letters") or []:
        label = _label_text(l.get("label"))
        d = {"defName": l.get("defName"), "label": label,
             "arrivalTick": l.get("arrivalTick"),
             # GUESS: jawa/letter_list carries no mapId (rimworld/list_letters does).
             "mapId": l.get("mapId")}
        d["fingerprint"] = (d["defName"], label, d["arrivalTick"])
        out.append(d)
    src["complete"] = True
    return out


def _norm_things(res, src):
    rows = [{"id": t.get("id"), "def": t.get("def"),
             "stackCount": t.get("stackCount") or 1,
             "x": t.get("x"), "z": t.get("z"), "faction": t.get("factionName")}
            for t in (res.get("things") or [])]
    comp = res.get("isCompleteList")
    src["complete"] = (comp is not False) and not res.get("truncated")
    return rows


def _totals(rows):
    c = Counter()
    for r in rows:
        c[r["def"]] += r["stackCount"]
    return dict(c)


def normalize(raw_reads):
    """raw_reads: tool name (with or without 'jawa/') -> raw result dict.

    Optional reserved keys: `_errors` {tool: message} for reads that failed,
    `_epoch` int, `_map_id`, `_fire_def` (unused).  A tool absent from both
    raw_reads and _errors is UNREAD (skipped tier), not failed.
    """
    raw = {_short(k): v for k, v in (raw_reads or {}).items() if not k.startswith("_")}
    errors = {_short(k): v for k, v in (raw_reads or {}).get("_errors", {}).items()}
    snap = {"schema_version": SCHEMA_VERSION,
            "epoch": (raw_reads or {}).get("_epoch", 0),
            "map_id": (raw_reads or {}).get("_map_id"),
            "tick": None,
            "sources": {n: _src() for n in ALL_SOURCES},
            "pawns": [], "letters": [], "alerts": [], "conditions": [],
            "weather": None, "story": {}, "things": [], "item_totals": {},
            "log_errors": [], "windows": [], "map_info": None,
            # defName filter the list_things read used; item/fire detectors only
            # compare reads made with the SAME query (different query != vanished)
            "things_query": (raw_reads or {}).get("_things_query"),
            "settings": dict((raw_reads or {}).get("_settings") or {})}

    for name in ALL_SOURCES:
        if name in errors:
            snap["sources"][name] = _src(read=True, complete=False, error=str(errors[name]))
            continue
        res = raw.get(name)
        if res is None:
            continue
        if not isinstance(res, dict) or res.get("success") is False:
            msg = res.get("message") if isinstance(res, dict) else "non-dict result"
            snap["sources"][name] = _src(read=True, complete=False,
                                         error="success=false: %s" % msg)
            continue
        src = _src(read=True, complete=True, source_tick=res.get("ticksGame"))
        snap["sources"][name] = src
        if name == "list_pawns":
            snap["pawns"] = _norm_pawns(res, src)
        elif name == "letter_list":
            snap["letters"] = _norm_letters(res, src)
        elif name == "story_stats":
            # keys per plan section 2: numRaidsEnemy, numThreatBigs, colonistsKilled, ...
            snap["story"] = {k: v for k, v in res.items()
                             if isinstance(v, (int, float)) and not isinstance(v, bool)}
        elif name == "alerts_list":
            # GUESS (unmeasured shape): alerts[{type,label,priority,explanation}]
            snap["alerts"] = [{"type": a.get("type"), "label": a.get("label"),
                               "priority": a.get("priority")} for a in res.get("alerts") or []]
        elif name == "weather_get":
            snap["weather"] = res.get("weather")
            snap["conditions"] = [{"def": c.get("def"), "scope": c.get("scope"),
                                   "affectsThisMap": c.get("affectsThisMap"),
                                   "permanent": c.get("permanent")}
                                  for c in res.get("conditions") or []]
            if res.get("readErrors"):       # non-empty readErrors == unread, not zero
                src["complete"] = False
                src["error"] = "readErrors: %s" % (res.get("readErrors"),)
        elif name == "list_things":
            snap["things"] = _norm_things(res, src)
            snap["item_totals"] = _totals(snap["things"])
        elif name == "drain_log":
            # real shape: messages[{type,text,repeats}]
            snap["log_errors"] = [{"type": m.get("type"), "text": m.get("text"),
                                   "repeats": m.get("repeats", 1)}
                                  for m in res.get("messages") or []
                                  if str(m.get("type")) in ("Error", "Exception")]
        elif name == "window_list_close":
            # GUESS: windows[{index,type,optionalTitle,isDebug,forcePause}]
            snap["windows"] = [{"type": w.get("type"), "title": w.get("optionalTitle"),
                                "isDebug": bool(w.get("isDebug")),
                                "forcePause": bool(w.get("forcePause"))}
                               for w in res.get("windows") or []]
        elif name == "map_info":
            # GUESS: mapParent{defName,faction}, plus an id key we cannot name yet
            snap["map_info"] = {"mapParent": res.get("mapParent"),
                                "mapBiome": res.get("mapBiome")}
            if snap["map_id"] is None:
                snap["map_id"] = res.get("mapId", res.get("id"))

    tclk = raw.get("time_clock")
    if isinstance(tclk, dict) and tclk.get("ticksGame") is not None:
        snap["tick"] = tclk["ticksGame"]
    else:
        ticks = [s["source_tick"] for s in snap["sources"].values()
                 if s["source_tick"] is not None]
        snap["tick"] = max(ticks) if ticks else None
    return snap


# ---- the one function that touches the bridge ---------------------------------

def take_snapshot(session, tier="tripwire", epoch=0, map_id=None, anchor_rect=None,
                  list_things_def="Fire", limit=500):
    """Read the bridge via session.call(tool, **params) and normalise.

    A failed read becomes complete=False + error; it never raises and is never
    treated as an empty listing.  tier 'tripwire' reads TOOLS_TRIPWIRE (pawns
    WITHOUT health), 'full' reads TOOLS_FULL (pawns WITH health and corpses).
    """
    if tier not in ("tripwire", "full"):
        raise ValueError("tier must be 'tripwire' or 'full'")
    full = tier == "full"
    plan = [("time_clock", {}),
            ("story_stats", {}),
            ("list_pawns", dict(includeHealth=full, includeCorpses=full, limit=limit)),
            ("letter_list", {})]
    if full:
        plan += [("alerts_list", {}), ("weather_get", {}),
                 ("list_things", dict(defName=list_things_def)),
                 ("drain_log", dict(errorsOnly=True, limit=50)),
                 ("window_list_close", dict(action="list")),
                 ("map_info", {})]
    raw, errs = {}, {}
    for tool, params in plan:
        try:
            raw[tool] = session.call("jawa/" + tool, **params)
        except Exception as e:  # noqa: BLE001 - a failed read must be recorded, not raised
            errs[tool] = "%s: %s" % (type(e).__name__, e)
    raw["_errors"] = errs
    raw["_epoch"] = epoch
    raw["_map_id"] = map_id
    raw["_things_query"] = list_things_def if full else None
    snap = normalize(raw)
    snap["tier"] = tier
    return snap


# ---- baseline ---------------------------------------------------------------

def hediff_key(pawn_id, h):
    return (pawn_id, h.get("def"), h.get("part"))


class Baseline(object):
    """A Snapshot plus the sets detectors diff against.

    Hediffs are INSTANCES keyed (pawn_id, def, part) -> severity, never
    def-only (a new Burn on another part is a new injury).
    """

    def __init__(self, snap):
        self.snap = snap
        self.tick = snap.get("tick")
        self.epoch = snap.get("epoch")
        self.map_id = snap.get("map_id")
        self.letters = Counter(l["fingerprint"] for l in snap["letters"])
        self.hediffs = {}
        for p in snap["pawns"]:
            for h in p["hediffs"] or []:
                self.hediffs[hediff_key(p["id"], h)] = h.get("severity") or 0.0
        self.hediff_known = {p["id"] for p in snap["pawns"] if p["hediffs"] is not None}
        self.story = dict(snap["story"])
        self.conditions = {c["def"] for c in snap["conditions"]}
        self.alerts = {a["type"] for a in snap["alerts"]}
        self.pawn_ids = {p["id"] for p in snap["pawns"]}
        self.dead_ids = {p["id"] for p in snap["pawns"] if p["dead"]}
        self.item_totals = dict(snap["item_totals"])
        self.settings = dict(snap.get("settings") or {})

    @classmethod
    def from_snapshot(cls, snap):
        return cls(snap)
