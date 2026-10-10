#!/usr/bin/env python3
"""modaudit/merge_checks.py - apply the four checker groups' amendments onto the assessor rows, deterministically.

    python3 src/RimMandrake/Utils/modaudit/merge_checks.py            # writes MASTER_REGISTRY.jsonl + .csv, prints counts
    python3 src/RimMandrake/Utils/modaudit/merge_checks.py --check    # compute and print counts, write nothing

Reads  design/RimMandrake/mod_audit/assessments/batch_NN.jsonl   (stage 1, one row per mod)
       design/RimMandrake/mod_audit/checks/check_group_N.jsonl   (stage 2, one row per mod: corrections[{field, old, new, evidence}])
       design/RimMandrake/mod_audit/facts/mod_facts.jsonl        (name, class, dependants incl. dependants_detail when present)
       design/RimMandrake/mod_audit/merge_inputs.json            (hand-made: spot-checks of checker evidence, card + ticket map)
Writes design/RimMandrake/mod_audit/MASTER_REGISTRY.jsonl and MASTER_REGISTRY.csv

Decision rule (the whole point of this file):
  * a checker correction on field `verdict` is a PROPOSAL. It becomes the final decision only when merge_inputs.json
    `spotchecks[<pid>].result == "CONFIRMED"` (a human/agent opened the primary source the checker cited). Anything
    else (NOT_CONFIRMED, or never spot-checked) leaves the assessor's verdict standing with decision_status DISPUTED
    and both verdicts recorded. Nothing is ever auto-accepted.
  * every other correction is applied field by field (card_worthy, needs_owner/open_questions, fit, source.*,
    problem severities, retirement dependants); unparsed corrections are carried verbatim in `amendments`.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
AUDIT = os.path.join(ROOT, "design", "RimMandrake", "mod_audit")
OUT_JSONL = os.path.join(AUDIT, "MASTER_REGISTRY.jsonl")
OUT_CSV = os.path.join(AUDIT, "MASTER_REGISTRY.csv")
INPUTS = os.path.join(AUDIT, "merge_inputs.json")

VERDICTS = ("KEEP-TEMPORARILY-THEN-PHASE-OUT", "REPLACE-NOW-WITH-OUR-OWN", "ELIMINATE-COMPLETELY", "KEEP")
SHORT = {"KEEP": "KEEP", "KEEP-TEMPORARILY-THEN-PHASE-OUT": "PHASE-OUT", "REPLACE-NOW-WITH-OUR-OWN": "REPLACE",
         "ELIMINATE-COMPLETELY": "ELIMINATE"}
KINDS = ("memory", "tps", "log_noise", "interaction", "complexity", "size", "maintenance")
FITS = ("resonant", "neutral", "dissonant")
PATH_RX = re.compile(r"[\w./-]+\.(?:md|xml|cs|py|json|jsonl|csv)(?::\d+(?:-\d+)?)?")


def parse_verdict(text):
    """First verdict token at the START of a proposal ('KEEP (as framework)' -> KEEP). Longest names tested first."""
    t = str(text or "").strip().upper()
    for v in VERDICTS:
        if t.startswith(v):
            return v
    return None


def parse_card(val):
    """-> (bool|None, note). 'merged into ...' is False (the question rides another card)."""
    if isinstance(val, bool):
        return val, ""
    t = str(val or "").strip()
    lo = t.lower()
    if lo.startswith(("true", "one family card", "yes")):
        return True, t
    if lo.startswith(("false", "merged", "no", "none")):
        return False, t
    return None, t


def parse_sev(val):
    if isinstance(val, int) and not isinstance(val, bool):
        return val
    t = str(val or "").strip()
    if re.match(r"^U\b", t):
        return "U"
    m = re.search(r"(?<![\w.])([0-3])(?![\w.])", t)
    return int(m.group(1)) if m else None


def norm_questions(x):
    if x is None:
        return []
    if isinstance(x, str):
        return [x] if x.strip() else []
    return [str(q) for q in x if str(q).strip()]


ANSWERED_RX = re.compile(r"^\s*(\[\]|none\b|remove\b|answered\b|ruled\b|no\b:|drop\b|withdrawn\b)", re.I)


def answered(text):
    """A checker 'new' value that says the question is settled (cite kept in questions_answered_by_checker)."""
    return bool(ANSWERED_RX.match(str(text or "")))


def slot(field):
    f = (field or "").strip()
    if f == "verdict":
        return ("verdict", None)
    if f.startswith("card_worthy"):
        return ("card", None)
    if f.startswith("needs_owner"):
        return ("needs_owner", None)
    if f.startswith("open_questions"):
        return ("open_questions", None)
    if f == "fit" or f.startswith("fit "):
        return ("fit", None)
    if f.startswith("source"):
        sub = f.split(".", 1)[1] if "." in f else None
        return ("source", sub)
    if f.startswith("retirement_cost.dependants"):
        return ("dependants", None)
    if f.startswith("problems"):
        if f.endswith(".confidence"):
            return ("other", None)
        m = re.match(r"problems[\[.](\w+)", f)
        return ("problem", m.group(1) if m else None)
    return ("other", None)


def _sev_max(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if a == "U" or b == "U":
        return a if b == "U" else b if a == "U" else a
    return max(a, b)


def merge_row(a, c, inputs, facts):
    """One assessor row + its checker row -> one MASTER row. Pure (selftested)."""
    pid = a["packageId"]
    f = facts.get(pid) or {}
    spot = (inputs.get("spotchecks") or {}).get(pid)
    cards = (inputs.get("card_map") or {}).get(pid, [])
    tickets = (inputs.get("measure_map") or {}).get(pid, [])
    actions = (inputs.get("action_map") or {}).get(pid, [])
    ruled = (inputs.get("answered_map") or {}).get(pid)
    batch = int(a.get("batch") or 0)
    src = dict(a.get("source") or {})
    sev = {}
    for p in a.get("problems") or []:
        k = p.get("kind")
        if k in KINDS:
            s = p.get("severity")
            s = s if s == "U" else parse_sev(s)
            sev[k] = _sev_max(sev.get(k), s)
    needs = norm_questions(a.get("needs_owner"))
    openq = norm_questions(a.get("open_questions"))
    card = bool(a.get("card_worthy"))
    fit = a.get("fit")
    deps_fact = f.get("dependants") or []
    deps_detail = f.get("dependants_detail")
    deps_checker = []
    proposal, proposal_ev, amendments, answered_q = None, None, [], []
    evidence = {"assessments/batch_%02d.jsonl" % batch, "records/batch_%02d.md" % batch}
    if c:
        evidence.add("checks/%s" % c.get("_file", "check_group_?.jsonl"))
    for corr in (c or {}).get("corrections") or []:
        field, new, ev = corr.get("field"), corr.get("new"), corr.get("evidence")
        for pth in PATH_RX.findall(" ".join(str(x) for x in (ev, new) if x)):
            evidence.add(pth)
        s, sub = slot(field)
        if s == "verdict":
            v = parse_verdict(new)
            if v and v != a.get("verdict"):
                proposal, proposal_ev = v, "%s | evidence: %s" % (str(new)[:300], str(ev)[:300])
            else:
                amendments.append(corr)
        elif s == "card":
            b, _ = parse_card(new)
            if b is not None:
                card = b
            amendments.append(corr)
        elif s in ("needs_owner", "open_questions"):
            cur = needs if s == "needs_owner" else openq
            if answered(new):
                answered_q.append({"field": field, "was": corr.get("old"), "answer": new, "evidence": ev})
                cur[:] = []
            elif str(new).startswith("[") and "schema" in str(new):
                pass                                  # schema-only note: list form already applied by norm_questions
            else:
                cur[:] = [str(new)]
        elif s == "fit":
            t = str(new or "").strip().lower()
            fit = next((x for x in FITS if t.startswith(x)), fit)
            amendments.append(corr)
        elif s == "source":
            t = str(new or "")
            lo = t.lower()
            if sub in ("url", None) and (lo.startswith("none") or "false match" in lo and sub == "url"):
                src["url"], src["kind"] = None, "none"
            elif sub == "url":
                src["url"] = t
            if sub and "confidence" in sub:
                src["confidence"] = t.split()[0].strip("(),;") if t else src.get("confidence")
            if sub and "available" in sub:
                src["available"] = t.split()[0].strip("(),;/") if t else src.get("available")
            if sub is None:
                amendments.append(corr)
        elif s == "dependants":
            if isinstance(new, list):
                deps_checker.extend(str(x) for x in new)
            elif str(new).strip() not in ("", "[]"):
                deps_checker.append(str(new))
            if new == [] or str(new).strip() == "[]":
                deps_checker.append("(checker: assessor listed non-dependants; corrected to none)")
        elif s == "problem":
            kind = sub if sub in KINDS else next((k for k in KINDS if k in str(new).lower()), None)
            v = parse_sev(new)
            if kind and v is not None:
                sev[kind] = v
            amendments.append(corr)
        else:
            amendments.append(corr)
    if ruled:                                   # merge author found the ruling that answers the row's question
        card = False
        answered_q.append({"field": "needs_owner", "was": (needs or openq or [None])[0], "answer": ruled,
                           "evidence": "merge_inputs.json answered_map"})
    av = a.get("verdict")
    if proposal:
        res = (spot or {}).get("result")
        if res == "CONFIRMED":
            final, status, changed = proposal, "CHANGED_BY_CHECKER", True
            reason = "checker %s -> %s; spot-checked %s: %s" % (av, proposal, spot.get("path"), spot.get("finding"))
        else:
            final, status, changed = av, "DISPUTED", False
            reason = ("checker proposes %s; %s" % (proposal, "spot-check NOT CONFIRMED: %s (%s)" % (
                spot.get("finding"), spot.get("path")) if spot else "evidence not spot-checked"))
    else:
        final, status, changed, reason = av, "AGREED", False, None
    if spot:
        evidence.add(str(spot.get("path")))
    ours = f.get("class") or ("OURS" if pid.startswith(("mandrake.rm.", "mandrake.rsw.", "mandrake.rut."))
                              else "CORE_DLC" if pid.startswith("ludeon.rimworld") else "THIRD_PARTY")
    return {
        "packageId": pid, "name": f.get("name") or a.get("name"), "class": ours,
        "membership": f.get("membership"), "batch": batch,
        "final_decision": final, "assessor_decision": av, "checker_proposed_decision": proposal,
        "decision_status": status, "decision_changed_by_checker": changed, "decision_change_reason": reason,
        "checker_proposal_evidence": proposal_ev, "spotcheck": spot,
        "checker_verdict": (c or {}).get("check_verdict"), "checker_confidence": (c or {}).get("confidence"),
        "fit": fit, "verdict_confidence": a.get("verdict_confidence"),
        "verdict_reason": a.get("verdict_reason"),
        "sev_memory": sev.get("memory"), "sev_tps": sev.get("tps"), "sev_log_noise": sev.get("log_noise"),
        "sev_interaction": sev.get("interaction"), "sev_complexity": sev.get("complexity"),
        "sev_size": sev.get("size"), "sev_maintenance": sev.get("maintenance"),
        "source_kind": src.get("kind"), "source_url": src.get("url"), "source_available": src.get("available"),
        "source_confidence": src.get("confidence"),
        "dependents": sorted(set(deps_fact)), "dependents_detail": deps_detail, "dependents_checker": deps_checker,
        "card_worthy": card, "needs_owner": needs, "open_questions": openq,
        "questions_answered_by_checker": answered_q, "owner_question_ids": cards, "measure_tickets": tickets,
        "action_ids": actions,
        "answered_by_ruling": ruled,
        "replacement_path": a.get("replacement_path"), "holds_it_in": a.get("holds_it_in"),
        "texture_decoded_mb_est": f.get("texture_decoded_mb_est"), "disk_mb": f.get("disk_mb"),
        "amendments": amendments, "evidence": sorted(evidence),
    }


def load(audit=AUDIT):
    A = {}
    for p in sorted(glob.glob(os.path.join(audit, "assessments", "batch_*.jsonl"))):
        for ln in open(p):
            if ln.strip():
                r = json.loads(ln)
                A[r["packageId"]] = r
    C = {}
    for p in sorted(glob.glob(os.path.join(audit, "checks", "check_group_*.jsonl"))):
        for ln in open(p):
            if ln.strip():
                r = json.loads(ln)
                r["_file"] = os.path.basename(p)
                C[r["packageId"]] = r
    F = {}
    fp = os.path.join(audit, "facts", "mod_facts.jsonl")
    for ln in open(fp):
        r = json.loads(ln)
        F[r["packageId"]] = r
    inputs = json.load(open(INPUTS)) if os.path.isfile(INPUTS) else {}
    return A, C, F, inputs


def counts(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items()))


CSV_COLS = ["packageId", "name", "class", "membership", "batch", "final_decision", "decision_status",
            "assessor_decision", "checker_proposed_decision", "decision_changed_by_checker", "checker_verdict", "fit",
            "sev_memory", "sev_tps", "sev_log_noise", "sev_interaction", "sev_complexity", "sev_size", "sev_maintenance",
            "source_kind", "source_url", "source_confidence", "verdict_confidence", "card_worthy", "owner_question_ids",
            "measure_tickets", "action_ids", "dependents", "texture_decoded_mb_est", "disk_mb", "decision_change_reason"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    A, C, F, inputs = load()
    missing_checks = sorted(set(A) - set(C))
    orphan_checks = sorted(set(C) - set(A))
    if orphan_checks:
        raise SystemExit("checker rows with no assessor row: %s" % orphan_checks[:5])
    order = sorted(A, key=lambda p: (int(A[p].get("batch") or 0), p))
    rows = [merge_row(A[p], C.get(p), inputs, F) for p in order]
    unused = sorted(set(inputs.get("spotchecks") or {}) - set(A))
    print("assessor decisions  :", counts([{"v": A[p]["verdict"]} for p in order], "v"))
    print("final decisions     :", counts(rows, "final_decision"))
    print("decision_status     :", counts(rows, "decision_status"))
    print("rows %d, unchecked %d, card_worthy %d, spot-checks %d (unused %s)" % (
        len(rows), len(missing_checks), sum(1 for r in rows if r["card_worthy"]),
        len(inputs.get("spotchecks") or {}), unused))
    if a.check:
        return
    with open(OUT_JSONL, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
    with open(OUT_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLS)
        for r in rows:
            w.writerow([" ".join(r[c]) if isinstance(r[c], list) and all(isinstance(x, str) for x in r[c])
                        else r[c] for c in CSV_COLS])
    print("wrote", os.path.relpath(OUT_JSONL, ROOT), "and", os.path.relpath(OUT_CSV, ROOT))


if __name__ == "__main__":
    sys.exit(main())
