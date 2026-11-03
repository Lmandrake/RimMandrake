"""modcheck.spoil_gate -- a spoiled run never grades a blanket GREEN (PROOF_SPOILED_RUNS_BUILD_NO_BLANKET_GREEN).

GPT bridge review s7 row 14: "Unknown blocking window, visitor-sensitive gap, empty rows, DRAFT status, capped list,
log blindness: cannot produce blanket GREEN." Owner, by card 2026-10-24 ("How should visitor-disturbed checks be
graded? -> Can't tell for need/mood/job only"): need/mood/job criteria go INDETERMINATE when visitor interference was
not observed well enough; every other criterion stays clean-with-note (contract.py, the 2026-10-10 visitor rule).

grade(summary, situational) reads a runner summary ({"chains": [...]}; each chain's `components`, `situational`
(watch.summary()) and `modal_check` (run_identity.modal_sweep)) and returns, per criterion (chain/component):

    PASS           the row passed and nothing that row depends on was spoiled (a note may say a visitor came and went)
    FAIL           the row failed (a DISRUPTED chain's FAIL is UNMEASURED: the visitor, not the mod, may have caused it)
    INDETERMINATE  the row passed, but a spoil it depends on means the pass cannot be certified
    UNMEASURED     nothing was measured (empty row, empty chain, not-run, disrupted run)

and an overall: RED (any FAIL) > UNMEASURED > INDETERMINATE > GREEN. GREEN only when every criterion is PASS and no
run-level spoil exists. The spoil classes, and the evidence each is read from (only what the record holds):

  unknown_blocking_window  situational chain with no modal_check, or one whose sweep errored, read no dialog, or left
                           a dialog unread
  blocking_window_open     modal_check.found_open, or a modal surprise / modal_open detail (a force-pause dialog was up)
  visitor_gap              runValidity holds a visitor, a visitor letter, or an observation failure. contract.py's
                           instruments do not see food/bed competition, scaring or psychic effects, so for need/mood/job
                           rows interference is unobserved unless the visitor row says `interferenceObserved: true`.
                           A situational chain with no situational record / runValidity observed no visitor at all
  disrupted                runValidity DISRUPTED: every row of the chain is UNMEASURED (a redo is owed)
  empty_rows               a chain with no executed component, a component with no verdict, or a run with no chain
                           (a chain or component record that is not a dict counts as an empty row)
  partial_run              a chain that ran some rows and not others (execution not_run): not a whole-run GREEN
  draft_status             a verdict naming DRAFT, or summary["checklist_state"] present and not VALIDATED
  capped_list              a listing_truncated hit, or hits_seen at its own cap (watch keeps the last HITS_CAP) --
                           what fell off the end of a capped list is unseen
  log_blind                situational.companion false (detectors off), or `log_alive: false` on the chain or summary
                           (runner summaries carry neither summary-level key; a caller that has them passes them in)

NOT a spoil: low TPS or a slow chain. "Slow is not hung. Low TPS alone should not fail a tick-semantic check."

ENVELOPE OFF. A chain run without the situational envelope has no modal_check and no Watch: its blocking window is
unknown, so with situational=False every chain grades `envelope_off` and the overall cannot be GREEN. runner.py records
this grade as summary["acceptance"] on every run but lets it veto all_green only when the run was --situational, so a
non-situational run's recorded status is unchanged until the situational default flips (NORTHSTAR_SITUATIONAL_ROLLOUT_1,
live_queue/rollout_gate.py). Pure; no I/O.
"""
import json
import re

PASS, FAIL, INDETERMINATE, UNMEASURED = "PASS", "FAIL", "INDETERMINATE", "UNMEASURED"
GREEN, RED = "GREEN", "RED"
HITS_CAP = 40            # watch.Watch.summary keeps seen_hits[-40:]

# Fallback when a component declares no `criterion_class`: name tokens that mark a need/mood/job row. A false match
# only makes a row stricter (INDETERMINATE under a visitor gap), never greener.
SENSITIVE_CLASSES = ("need", "mood", "job")
_SENSITIVE_TOKENS = {"need", "needs", "mood", "moods", "job", "jobs", "hunger", "rest", "joy", "thought", "thoughts"}


def criterion_class(comp):
    c = comp.get("criterion_class")
    if c:
        return str(c).lower()
    toks = set(t for t in re.split(r"[^a-z]+", str(comp.get("name") or "").lower()) if t)
    for cls in SENSITIVE_CLASSES:
        if cls in toks or cls + "s" in toks:
            return cls
    if toks & _SENSITIVE_TOKENS:
        return "need"
    return "other"


def _is_pass(v):
    return isinstance(v, str) and v.startswith("PASS")


def _blocking(chain, situational):
    """-> list of (spoil, why) about force-pause dialogs."""
    out = []
    mc = chain.get("modal_check")
    if not situational:
        out.append(("envelope_off", "run without the situational envelope: blocking window and visitors unobserved"))
    elif mc is None:
        out.append(("unknown_blocking_window", "no modal check recorded for this chain"))
    if mc is not None and (not isinstance(mc, dict) or not isinstance(mc.get("dialogs"), dict) or not mc["dialogs"]):
        out.append(("unknown_blocking_window", "modal check unreadable or read no dialog: %r" % (mc,)))
    elif mc is not None:
        if mc.get("errors") or any(v is None for v in mc["dialogs"].values()):
            out.append(("unknown_blocking_window", "modal sweep errored: %s" % "; ".join(str(e) for e in (mc.get("errors") or ["dialog unread"]))))
        if mc.get("found_open"):
            out.append(("blocking_window_open", "a force-pause dialog was open: %s" % (mc.get("dialogs"),)))
    sit = chain.get("situational")
    if isinstance(sit, dict) and any("modal" in json.dumps(s, default=str) for s in sit.get("surprises") or []):
        out.append(("blocking_window_open", "a modal surprise was captured"))
    if any("modal_open" in str(c.get("detail") or "") for c in _dicts(chain.get("components"))):
        out.append(("blocking_window_open", "a component detail names modal_open"))
    return out


def _dicts(xs):
    return [x for x in (xs if isinstance(xs, list) else []) if isinstance(x, dict)]


def _observation(chain, summary, situational):
    """-> (chain-wide spoils, visitor-gap note or None, disrupted bool)."""
    out, gap, disrupted = [], None, False
    sit = chain.get("situational")
    if situational and not (isinstance(sit, dict) and isinstance(sit.get("runValidity"), dict)):
        gap = "no situational record / runValidity for this chain: visitors were not observed at all"
    if isinstance(sit, dict):
        if sit.get("companion") is False:
            out.append(("log_blind", "companion detectors off: the log and its detectors were not read"))
        hits = _dicts(sit.get("hits_seen"))
        trunc = [h for h in hits if h.get("detector") == "listing_truncated"]
        if trunc:
            out.append(("capped_list", "listing truncated: %s" % trunc[0].get("summary")))
        if len(hits) >= HITS_CAP:
            out.append(("capped_list", "hits_seen at its cap (%d): earlier hits fell off the list" % HITS_CAP))
        rv = sit.get("runValidity") if isinstance(sit.get("runValidity"), dict) else {}
        if rv.get("verdict") == "DISRUPTED":
            disrupted = True
            out.append(("disrupted", rv.get("note") or "a visitor disrupted a protected pawn"))
        else:
            unobs = [v for v in rv.get("visitors") or [] if not (isinstance(v, dict) and v.get("interferenceObserved"))]
            if unobs or rv.get("letters") or rv.get("observationFailures") or rv.get("verdict") == "INDETERMINATE":
                gap = ("visitor interference with needs/mood/jobs was not observed (%d visitor(s), %d letter(s), "
                       "%d observation failure(s)); %s" % (len(unobs), len(rv.get("letters") or []),
                                                           len(rv.get("observationFailures") or []),
                                                           rv.get("note") or ""))
    for scope in (chain, summary):
        if scope.get("log_alive") is False:
            out.append(("log_blind", "log_alive false: Verse.Log stopped writing (cap) or the log was stale"))
            break
    return out, gap, disrupted


def grade_chain(chain, situational, summary=None):
    summary = summary or {}
    spoils = _blocking(chain, situational)
    obs, gap, disrupted = _observation(chain, summary, situational)
    spoils += obs
    chain_spoiled = [s for s in spoils if s[0] != "disrupted"]
    allc = _dicts(chain.get("components"))
    if len(allc) != len(chain.get("components") or []):
        spoils.append(("empty_rows", "a component record is not a dict"))
    comps = [c for c in allc if c.get("execution") != "not_run"]
    skipped = [c for c in allc if c.get("execution") == "not_run"]
    if not comps:
        spoils.append(("empty_rows", "chain recorded no executed component"))
    if skipped and comps:
        spoils.append(("partial_run", "%d row(s) not run (e.g. %s): the run is not whole" % (
            len(skipped), skipped[0].get("name"))))
    rows = []
    for c in comps:
        v, cls, notes = c.get("verdict"), criterion_class(c), []
        if not v:
            g = UNMEASURED
            spoils.append(("empty_rows", "%s has no verdict" % c.get("name")))
            notes.append("empty row")
        elif "DRAFT" in str(v).upper():
            g = INDETERMINATE
            spoils.append(("draft_status", "%s verdict %s" % (c.get("name"), v)))
            notes.append("draft verdict")
        elif disrupted:
            g = UNMEASURED
            notes.append("disrupted run: redo owed")
        elif v == FAIL:
            g = FAIL
        elif _is_pass(v):
            g = PASS
            if chain_spoiled:
                g = INDETERMINATE
                notes += ["%s: %s" % s for s in chain_spoiled]
            if gap:
                if cls in SENSITIVE_CLASSES:
                    g = INDETERMINATE
                    notes.append("visitor_gap (%s criterion): %s" % (cls, gap))
                else:
                    notes.append("clean-with-note: " + gap)
        else:
            g = UNMEASURED
        rows.append({"row": "%s/%s" % (chain.get("name"), c.get("name")), "verdict": v, "class": cls,
                     "grade": g, "notes": notes})
    if gap and any(r["class"] in SENSITIVE_CLASSES and r["grade"] == INDETERMINATE for r in rows):
        spoils.append(("visitor_gap", gap))
    return {"chain": chain.get("name"), "rows": rows, "spoils": [{"class": k, "why": w} for k, w in spoils]}


def grade(summary, situational=True):
    """The acceptance grade of a runner summary. -> {"overall", "rows", "spoils", "counts"}."""
    summary = summary if isinstance(summary, dict) else {}
    raw = summary.get("chains") or []
    chains = [grade_chain(ch, situational, summary) for ch in _dicts(raw)]
    rows = [r for ch in chains for r in ch["rows"]]
    spoils = [dict(s, chain=ch["chain"]) for ch in chains for s in ch["spoils"]]
    if not chains or len(chains) != len(raw if isinstance(raw, list) else [0]):
        spoils.append({"class": "empty_rows", "why": "run recorded no chain, or a chain record is not a dict",
                       "chain": None})
    cs = summary.get("checklist_state")
    if "checklist_state" in summary and cs != "VALIDATED":
        spoils.append({"class": "draft_status", "why": "north-star checklist is %s, not VALIDATED" % cs, "chain": None})
    counts = {g: sum(1 for r in rows if r["grade"] == g) for g in (PASS, FAIL, INDETERMINATE, UNMEASURED)}
    if counts[FAIL]:
        overall = RED
    elif counts[UNMEASURED] or any(s["class"] in ("empty_rows", "disrupted") for s in spoils):
        overall = UNMEASURED
    elif counts[INDETERMINATE] or spoils:
        overall = INDETERMINATE
    else:
        overall = GREEN
    return {"overall": overall, "rows": rows, "spoils": spoils, "counts": counts,
            "classes": sorted(set(s["class"] for s in spoils))}
