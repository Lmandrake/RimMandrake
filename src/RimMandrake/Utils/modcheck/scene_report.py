#!/usr/bin/env python3
"""modcheck.scene_report -- the first-look scene report, batched over EXISTING bridge reads.

Map awareness phase 1c (VISITOR_DETECTORS_MEND_NAME_THE_STRANGER). Schema: GPT review section 4
(Transient/foundry_map_awareness_review_gpt_20261010.md). One call answers "who is on this map, where, of which
faction, in what state, threatening whom -- and what do we actually KNOW about why they are here".

    python.exe src/RimMandrake/Utils/modcheck/scene_report.py [--anchor X,Z] [--baseline FILE] [--out FILE] [--json]

Laws (each is a selftest row in selftest_awareness.py):
  * NOT ATOMIC. The reads are separate bridge calls; the report states its tick at the start and the end of
    acquisition. A pawn can move between reads.
  * COVERAGE IS DECLARED. jawa/list_pawns lists map.mapPawns.AllPawnsSpawned of the CURRENT map (plus corpses if
    asked). Held pawns (containers, holding platforms, cryptosleep, transporters, caravans, world pawns) are NOT
    covered; spawned dormant pawns are listed but not distinguished as dormant.
  * HOSTILE IS DECOMPOSED: faction relation, mental state / aggression reason, current target, capability.
    list_pawns' `hostile` is Faction.HostileTo(player) only -- a factionless manhunter reads false there.
  * `ourInvolvement` (confirmedDirectSpawn | confirmedIndirectAction | correlatedOnly | unknown) and
    `expectation` (expected | unexpected | unresolved) are INDEPENDENT fields.
  * ORIGIN IS UNKNOWN unless an origin recorder row says otherwise; a letter, a lord job or proximity is an
    ASSOCIATION, never a cause. letter_list's `lookTargets` is LookTargets.ToString(), which LookTargets does not
    override (VERIFIED in decompiled 1.6 via RimSage, 2026-10-10) -- so until the companion emits look-target ids
    the association is reported "unavailable", never guessed from a label.
  * A failed or unread source is never an empty one.
"""
import argparse
import json
import os
import sys
import uuid

SCHEMA_VERSION = 1
REQUIRED = ("time_clock", "list_pawns", "letter_list")
OPTIONAL = ("map_info", "weather_get", "incident_queue_peek")
COMPANION = ("pawn_census",)
RECORDERS = ("pawn_origin", "incident_journal")     # phase 2/3 companion tools; 'unavailable' until deployed

COVERAGE = {
    "spawned": "covered: map.mapPawns.AllPawnsSpawned of the current map",
    "dormant": "listed when spawned, but NOT distinguished as dormant (no dormancy field is read)",
    "held": "not covered: pawns in containers, holding platforms, cryptosleep, transporters, caravans and world "
            "pawns are absent from jawa/list_pawns",
    "otherMaps": "not covered: current map only",
    "corpses": "not covered (list_pawns includeCorpses=false)",
}
FOOTER = ("Every pawn without an origin row: origin unknown. A letter association, a lord job, a faction or "
          "proximity is an association, never a cause. Distance is Chebyshev cells: proximity, not reachability.")


def _call(session, tool, **p):
    try:
        r = session.call("jawa/" + tool, **p)
    except Exception as e:                                      # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)
    if not isinstance(r, dict) or r.get("success") is False:
        return None, "success=false: %s" % ((r or {}).get("message") if isinstance(r, dict) else r)
    return r, None


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _ms_def(ms):
    return ms.get("def") if isinstance(ms, dict) else ms


def _letter_text(label):
    return str(label.get("RawText", "")) if isinstance(label, dict) else ("" if label is None else str(label))


def _threat(p, c):
    """Hostility, decomposed (GPT s4). `c` is the census row or None (unread)."""
    if p.get("isPlayer"):
        rel = "player"
    elif p.get("faction") is None:
        rel = "no-faction"            # NOT automatically neutral: a predator or manhunter has no faction
    else:
        rel = "hostile" if p.get("hostile") else "non-hostile"
    ms = (c or {}).get("mentalState") if c is not None else None
    msd = _ms_def(ms)
    aggro = bool(ms.get("isAggro")) if isinstance(ms, dict) else False
    target = None
    if c is not None:
        job = c.get("job") or {}
        ta = job.get("targetA") if isinstance(job.get("targetA"), dict) else {}
        target = {"enemy": c.get("enemyTargetId"), "melee": c.get("meleeThreatId"), "prey": c.get("preyId"),
                  "job": job.get("def"), "jobTargetA": (ta or {}).get("thingId")}
    reasons = []
    if aggro:
        reasons.append("mental:%s" % msd)
    if rel == "hostile":
        reasons.append("faction")
    if c is not None and c.get("isPredatorHunting"):
        reasons.append("predator-hunt:%s" % c.get("preyId"))
    cap = "dead" if p.get("dead") else ("downed" if p.get("downed") else "active")
    if cap != "active":
        level = "inactive"
    elif aggro or (target and (target["enemy"] or target["melee"])) or (c is not None and c.get("isPredatorHunting")):
        level = "active-threat"
    elif rel == "hostile":
        level = "potential"
    elif c is None:
        level = "unknown"             # no census: aggression unread, not absent
    else:
        level = "none-observed"
    return {"factionRelationToPlayer": rel,
            "engineHostileToPlayer": "unread (list_pawns.hostile is Faction.HostileTo, not Pawn.HostileTo)",
            "mentalState": msd if c is not None else "unread",
            "aggressionReason": "mental:%s" % msd if aggro else (reasons[0] if reasons else None),
            "currentTarget": target if c is not None else "unread",
            "capabilityState": cap,
            "threatAssessment": {"level": level, "reasons": reasons,
                                 "scope": "this read only; dormancy and held threats not covered"}}


def _expectation(p, expectations, baseline_ids, tick):
    if baseline_ids is not None and p["id"] in baseline_ids:
        return "expected", "present at baseline"
    if expectations is None:
        return "unresolved", "no contract given"
    for kind in ("pawn", "hostile", "fixture", "litter"):
        for e in expectations.live((kind,), tick):
            if e.match(p):               # match(), never admits(): a report must not consume a bounded claim
                return "expected", "contract:%s" % kind
    return "unexpected", "matches no declared expectation"


def collect(session, anchor=None, receipts=(), expectations=None, baseline=None, companion=None, contract=None,
            limit=2000):
    """Read the bridge (separate calls, NOT atomic) and build the report. `baseline` is an earlier report (dict)."""
    reads, raw, failed = [], {}, []
    plan = [("time_clock", {}), ("map_info", {}), ("list_pawns", dict(limit=limit)), ("letter_list", {}),
            ("weather_get", {}), ("incident_queue_peek", {})]
    if companion is not False:
        plan.append(("pawn_census", dict(limit=min(limit, 2000))))
    for tool, p in plan:
        r, err = _call(session, tool, **p)
        raw[tool] = r
        reads.append({"tool": "jawa/" + tool, "ok": err is None, "ticksGame": (r or {}).get("ticksGame"), "error": err})
        if err and (tool in REQUIRED or (tool in COMPANION and companion)):
            failed.append(tool)
    tick0 = (raw.get("time_clock") or {}).get("ticksGame")
    pawns_r = raw.get("list_pawns") or {}
    rows = pawns_r.get("pawns") or []
    census = dict((c.get("id"), c) for c in ((raw.get("pawn_census") or {}).get("pawns") or []))
    ids = [p.get("id") for p in rows]
    rec = {}
    for tool in RECORDERS:
        r, err = _call(session, tool, ids=",".join(i for i in ids if i)) if tool == "pawn_origin" else _call(session, tool)
        rec[tool] = r if r else {"installed": False, "unavailable": err}
    origins = dict((o.get("id"), o) for o in ((rec["pawn_origin"] or {}).get("pawns") or []) if isinstance(o, dict))
    letters = []
    have_targets = False
    for l in (raw.get("letter_list") or {}).get("letters") or []:
        tids = l.get("lookTargetIds")
        if tids is not None:
            have_targets = True
        letters.append({"defName": l.get("defName"), "label": _letter_text(l.get("label")),
                        "arrivalTick": l.get("arrivalTick"), "lookTargetIds": tids})
    direct = {}
    for rc in receipts or ():
        for pid in rc.get("returnedIds") or []:
            direct[pid] = rc.get("actionId")
    base_ids = set(p["id"] for p in baseline["pawns"]) if baseline else None
    out_rows = []
    for p in rows:
        pid = p.get("id")
        c = census.get(pid) if raw.get("pawn_census") else None
        x, z = p.get("x"), p.get("z")
        dist = _dist((x, z), anchor) if anchor is not None and x is not None and x >= 0 else None
        assoc = ([{"defName": l["defName"], "label": l["label"], "arrivalTick": l["arrivalTick"],
                   "statement": "associated with this letter (not: created by it)"}
                  for l in letters if pid in (l.get("lookTargetIds") or []) or ("Thing_" + str(pid)) in (l.get("lookTargetIds") or [])]
                 if have_targets else "unavailable")
        org = origins.get(pid)
        if pid in direct:
            inv = "confirmedDirectSpawn"
        elif org and org.get("ourInvolvement") in ("confirmedIndirectAction", "correlatedOnly"):
            inv = org["ourInvolvement"]
        else:
            inv = "unknown"
        exp, why = _expectation({"id": pid, "kindDef": p.get("kindDef"), "faction": p.get("faction"),
                                 "name": p.get("name"), "def": p.get("def")}, expectations, base_ids, tick0)
        out_rows.append({
            "id": pid, "aliases": {"thingId": pid, "loadId": "Thing_%s" % pid}, "name": p.get("name"),
            "kindDef": p.get("kindDef") or p.get("kind"), "raceDef": p.get("def"),
            "position": {"spawned": p.get("spawned"), "x": x, "z": z, "distToAnchor": dist,
                         "distanceMetric": "chebyshev cells"},
            "control": {"faction": p.get("faction"), "isPlayer": p.get("isPlayer"),
                        "isColonist": (c or {}).get("isColonist") if c is not None else "unread",
                        "dead": p.get("dead"), "downed": p.get("downed")},
            "threat": _threat(p, c),
            "lord": (c or {}).get("lord") if c is not None else "unread",
            "duty": (c or {}).get("duty") if c is not None else "unread",
            "evidence": {"letters": assoc, "receipt": direct.get(pid),
                         "origin": org if org else "unknown (no origin row)"},
            "ourInvolvement": inv, "expectation": exp, "expectationRule": why})
    tick1 = None
    r, _ = _call(session, "time_clock")
    if r:
        tick1 = r.get("ticksGame")
    complete = bool(raw.get("list_pawns")) and not pawns_r.get("truncated") and pawns_r.get("isCompleteList") is not False
    diff = None
    if baseline:
        bmap = dict((p["id"], p) for p in baseline["pawns"])
        cmap = dict((p["id"], p) for p in out_rows)
        changed = []
        for pid in sorted(set(bmap) & set(cmap)):
            b, n = bmap[pid], cmap[pid]
            d = {}
            for k in ("faction", "isPlayer", "dead", "downed"):
                if b["control"].get(k) != n["control"].get(k):
                    d[k] = [b["control"].get(k), n["control"].get(k)]
            if b["threat"].get("mentalState") != n["threat"].get("mentalState"):
                d["mentalState"] = [b["threat"].get("mentalState"), n["threat"].get("mentalState")]
            if d:
                changed.append({"id": pid, "changes": d, "statement": "state change of a pawn already present"})
        diff = {"baselineReportId": baseline.get("reportId"), "added": sorted(set(cmap) - set(bmap)),
                "removed": sorted(set(bmap) - set(cmap)), "changed": changed,
                "warning": None if baseline.get("scope", {}).get("complete") and complete
                else "a side of the diff is incomplete: an absent id is not proof it left"}
    unresolved = [p["id"] for p in out_rows if p["expectation"] != "expected" and p["ourInvolvement"] == "unknown"]
    return {
        "schemaVersion": SCHEMA_VERSION, "reportId": uuid.uuid4().hex[:12],
        "acquisition": {"atomic": False, "tickStart": tick0, "tickEnd": tick1, "reads": reads, "failed": failed,
                        "paused": (raw.get("time_clock") or {}).get("paused")},
        "scope": {"map": (raw.get("map_info") or {}).get("mapId", (raw.get("map_info") or {}).get("id")),
                  "coverage": dict(COVERAGE), "complete": complete,
                  "truncated": pawns_r.get("truncated"), "anchor": list(anchor) if anchor else None},
        "environment": {"weather": (raw.get("weather_get") or {}).get("weather"),
                        "conditions": [c.get("def") for c in ((raw.get("weather_get") or {}).get("conditions") or [])]
                        if raw.get("weather_get") else "unread",
                        "incidentQueue": [q.get("defName") for q in ((raw.get("incident_queue_peek") or {}).get("queue") or [])]
                        if raw.get("incident_queue_peek") else "unread",
                        "quests": "unread (no quest read in this report)",
                        "suppression": contract if contract else "not declared"},
        "recorder": {k: (v if not isinstance(v, dict) or "pawns" not in v else
                         dict((kk, vv) for kk, vv in v.items() if kk != "pawns")) for k, v in rec.items()},
        "letters": letters if letters else [],
        "letterAssociation": "available" if have_targets else
        "unavailable: letter_list carries no look-target ids (LookTargets.ToString is not overridden)",
        "pawns": out_rows, "diff": diff, "unresolved": unresolved, "footer": FOOTER}


def render_text(rep):
    a = rep["acquisition"]
    lines = ["scene %s  ticks %s..%s  (not atomic)%s" % (rep["reportId"], a["tickStart"], a["tickEnd"],
                                                         "  FAILED READS: %s" % a["failed"] if a["failed"] else ""),
             "coverage: complete=%s; held pawns not covered; dormant not distinguished" % rep["scope"]["complete"]]
    rr = rep["recorder"]
    lines.append("recorders: " + ", ".join("%s=%s" % (k, "installed" if (v or {}).get("installed") else "off/unavailable")
                                           for k, v in rr.items()))
    if rep.get("diff"):
        d = rep["diff"]
        lines.append("since %s: added %s; removed %s; changed %s" % (d["baselineReportId"], d["added"] or "none",
                                                                      d["removed"] or "none",
                                                                      [c["id"] for c in d["changed"]] or "none"))
    lines.append("%-14s %-22s %-16s %-12s %-14s %-20s %-6s %-20s %s" % (
        "id", "kind", "faction", "relation", "capability", "aggression", "dist", "involvement", "expectation"))
    for p in rep["pawns"]:
        t = p["threat"]
        lines.append("%-14s %-22s %-16s %-12s %-14s %-20s %-6s %-20s %s" % (
            p["id"], (p["kindDef"] or "?")[:22], (p["control"]["faction"] or "-")[:16], t["factionRelationToPlayer"],
            t["capabilityState"], (t["aggressionReason"] or "-")[:20],
            p["position"]["distToAnchor"] if p["position"]["distToAnchor"] is not None else "-",
            p["ourInvolvement"], p["expectation"]))
    if rep["unresolved"]:
        lines.append("unresolved (not expected, not ours): %s" % ", ".join(rep["unresolved"][:20]))
    lines.append(rep["footer"])
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--anchor", help="x,z")
    ap.add_argument("--baseline", help="an earlier report JSON to diff against")
    ap.add_argument("--out", help="write the JSON report here")
    ap.add_argument("--json", action="store_true", help="print JSON instead of the table")
    a = ap.parse_args(argv)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimdrive.session import Session  # noqa: E402
    anchor = tuple(int(v) for v in a.anchor.split(",")) if a.anchor else None
    base = json.load(open(a.baseline)) if a.baseline else None
    with Session(lock=None, focus=False) as s:
        rep = collect(s, anchor=anchor, baseline=base)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rep, f, indent=1, default=str)
    print(json.dumps(rep, indent=1, default=str) if a.json else render_text(rep))
    return 1 if rep["acquisition"]["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
