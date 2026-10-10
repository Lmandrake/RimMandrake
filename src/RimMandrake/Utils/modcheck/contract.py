"""modcheck.contract -- run validity under the owner's visitor rule, and action receipts.

VISITOR_DETECTORS_MEND_NAME_THE_STRANGER (map awareness phase 1). Design and reviews:
Transient/foundry_map_awareness_design_20261010.md, ..._review_opus_..., ..._review_gpt_... (sections 3, 5, 7).

THE OWNER'S RULE (decision taken by question card, 2026-10-10), binding over GPT's "withhold PASS on any unexpected
arrival": when a validation or north-star run meets an unexpected visitor, RECORD it, REMOVE it, carry on. A redo is
owed only on EVIDENCE that the visitor disrupted the criterion. So validity has three values, and it is a second
dimension beside the criterion's own PASS / FAIL / UNMEASURED:

    CLEAN          no visitor, or every visitor recorded + removed with no evidence of disruption (a note says so)
    DISRUPTED      evidence that a visitor attacked / targeted / hunted a protected pawn (a colonist or a test
                   subject); the run aborts and is UNMEASURED: only THIS needs a redo
    INDETERMINATE  an observation the verdict depends on failed (a truncated or failed pawn/letter read, no
                   damage/census read while judging a visitor): cleanliness cannot be certified

Evidence this module can see, and what it cannot (stated, never assumed):
  * damage_log rows whose instigator is a visitor and whose victim is protected        -> "attacked"
  * pawn_census enemyTarget / meleeThreat / prey / job targetA pointing at a protected pawn -> "targeted"
  * NOT seen: competing for food or a bed, blocking a path, scaring, a psychic effect. A visitor removed
    before any of those is visible leaves the run CLEAN-with-note, which is the owner's efficiency trade.

Nothing here claims where a visitor came from. A visitor is "origin unknown" until a recorder says otherwise
(GPT review s3 forbidden-upgrade table).
"""

CLEAN, DISRUPTED, INDETERMINATE = "CLEAN", "DISRUPTED", "INDETERMINATE"

# detectors whose subject is an unexpected PAWN (or a raid letter announcing pawns): the owner's rule applies
VISITOR_DETECTORS = ("hostile_pawns", "strangers_near_anchor", "wildlife_near_colonist", "player_joiner",
                     "raid_arrived")
# sources whose failure makes a visitor verdict uncertifiable
REQUIRED_SOURCES = ("list_pawns", "letter_list")
JUDGEMENT_SOURCES = ("damage_log", "pawn_census")


def visitor_ids(hits):
    out = []
    for h in hits:
        for pid in (h.evidence or {}).get("ids") or []:
            if pid not in out:
                out.append(pid)
    return out


def disruption_evidence(snap, visitors, protected):
    """-> list of {kind, visitor, subject, detail}. Pure. `visitors`/`protected` are id collections."""
    vs, ps = set(visitors), set(protected)
    out = []
    for e in snap.get("damage_events") or []:
        if e.get("instigatorId") in vs and (e.get("victimId") in ps or e.get("victimColonist")):
            out.append({"kind": "attacked", "visitor": e.get("instigatorId"), "subject": e.get("victimId"),
                        "detail": "%s %s at tick %s (damage_log seq %s)" % (e.get("damageDef"), e.get("amount"),
                                                                              e.get("tick"), e.get("seq"))})
    for p in snap.get("pawns") or []:
        if p.get("id") not in vs:
            continue
        for field, kind in (("enemyTargetId", "targeted"), ("meleeThreatId", "targeted"),
                            ("preyId", "hunted"), ("jobTargetA", "targeted")):
            t = p.get(field)
            if t and t in ps:
                out.append({"kind": kind, "visitor": p["id"], "subject": t,
                            "detail": "pawn_census %s=%s (job %s)" % (field, t, p.get("job"))})
                break
    return out


class RunValidity(object):
    """What a Watch learned about whether its run stayed valid. One per chain."""

    def __init__(self):
        self.visitors = []              # {id, kind, faction, state, detectors, tick, removed, note}
        self.letters = []               # visitor-class letters with no pawn to remove yet
        self.disruptions = []           # disruption_evidence rows
        self.observation_failures = []  # {source, why, tick}
        self.aborted_by = None          # the non-visitor surprise that ended the run, if any (criterion matter)

    def note_visitor(self, row):
        if not any(v["id"] == row["id"] for v in self.visitors):
            self.visitors.append(row)

    def note_letter(self, row):
        if row not in self.letters:
            self.letters.append(row)

    def note_disruption(self, rows):
        for r in rows:
            if r not in self.disruptions:
                self.disruptions.append(r)

    def note_observation_failure(self, source, why, tick=None):
        row = {"source": source, "why": why, "tick": tick}
        if not any(f["source"] == source and f["why"] == why for f in self.observation_failures):
            self.observation_failures.append(row)

    @property
    def verdict(self):
        if self.disruptions:
            return DISRUPTED
        if self.observation_failures:
            return INDETERMINATE
        return CLEAN

    def note_text(self):
        v = self.verdict
        if v == DISRUPTED:
            return "DISRUPTED: " + "; ".join("%s %s %s (%s)" % (d["visitor"], d["kind"], d["subject"], d["detail"])
                                             for d in self.disruptions[:4]) + " -- a redo is owed"
        if v == INDETERMINATE:
            return "INDETERMINATE: " + "; ".join("%s: %s" % (f["source"], f["why"]) for f in self.observation_failures[:4])
        if self.visitors or self.letters:
            return ("CLEAN with %d visitor(s) recorded and removed, no evidence of disruption (origin unknown): %s"
                    % (len(self.visitors), ", ".join("%s %s" % (v["id"], v.get("kind")) for v in self.visitors[:6])))
        return "CLEAN: no visitor observed"

    def as_dict(self):
        return {"verdict": self.verdict, "note": self.note_text(), "visitors": list(self.visitors),
                "letters": list(self.letters), "disruptions": list(self.disruptions),
                "observationFailures": list(self.observation_failures), "abortedBy": self.aborted_by}


def worst(verdicts):
    """Aggregate several chains: DISRUPTED > INDETERMINATE > CLEAN; None when nothing was judged."""
    vs = [v for v in verdicts if v]
    for v in (DISRUPTED, INDETERMINATE, CLEAN):
        if v in vs:
            return v
    return None


# ---------------------------------------------------------------------------------- action receipts

def spawn_receipt(action_id, tool, requested_kind, result, read_rows):
    """A receipt for a pawn-spawning bridge action: requested kind, what the tool said it made, and what an
    INDEPENDENT map read says is there (E5: 4 of 80 spawn_pawn calls delivered a vanilla Colonist while the
    caller kept the requested kind). `read_rows` is a list_pawns pawns list taken after the call."""
    rows = (result or {}).get("pawns") or []
    ids = [r.get("id") for r in rows if r.get("id")]
    tool_kinds = [r.get("kindActual") if "kindActual" in r else None for r in rows if r.get("id")]
    by_id = {p.get("id"): p for p in (read_rows or [])}
    read_kinds = [((by_id.get(i) or {}).get("kindDef") or (by_id.get(i) or {}).get("kind")) for i in ids]
    missing = [i for i in ids if i not in by_id]
    mismatch = bool([k for k in read_kinds if k is not None and k != requested_kind]) or \
        bool([k for k in tool_kinds if k is not None and k != requested_kind])
    return {"actionId": action_id, "tool": tool, "requestedKind": requested_kind, "returnedIds": ids,
            "toolKinds": tool_kinds, "readBackKinds": read_kinds, "missingOnReadBack": missing,
            "mismatch": mismatch, "toolSuccess": (result or {}).get("success")}


def receipt_problems(receipts):
    out = []
    for r in receipts or []:
        if r.get("mismatch"):
            out.append("%s: asked %s, got %s (read back %s)" % (r["actionId"], r["requestedKind"], r["toolKinds"],
                                                                r["readBackKinds"]))
        if r.get("missingOnReadBack"):
            out.append("%s: ids %s not on the map after the call" % (r["actionId"], r["missingOnReadBack"]))
    return out
