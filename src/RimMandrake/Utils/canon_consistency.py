#!/usr/bin/env python3
"""canon_consistency.py — Phase 1 of the canon-storage plan: a checker over the
Phase 0 tagged-claim index (`doc_claims.py --tag`).

design/CANON_STORAGE_ARCHITECTURE_options.md, "Phase 1 (the self-healing engine)":
    a checker over that claim index — contradiction (same entity+attribute,
    disagreeing values across docs) and gap (entities with thin coverage), plus
    the dependency flag (a changed ruling lists its dependent claims). This is
    the thing that converts CANON_DRAIN from a periodic heroic event into a
    standing green/red signal.

    python3 src/RimMandrake/Utils/canon_consistency.py <path-or-dir>...
    python3 src/RimMandrake/Utils/canon_consistency.py <path-or-dir>... --update-baseline
    python3 src/RimMandrake/Utils/canon_consistency.py --out report.json <path>...

WHY A NEW FILE, NOT AN EXTENSION OF check_canon.py
===================================================
`check_canon.py` is a different machine solving a different problem: it holds a
hand-curated ground truth (`infrastructure/state/canon.yml`) and a hand-written
`Rule` object PER FACT (water %, tile count, faction count, ...), each with its
own bespoke regex and context test, and checks design-doc PROSE against that
fixed truth. A human decides the canon value and writes the rule; the tool never
infers a fact from a document. That is correct for a small number of
load-bearing numbers, and this file does not touch it.

Phase 1 is the opposite shape: fully mechanical, no hand-curated ground truth,
comparing claims EXTRACTED by `doc_claims.py --tag` AGAINST EACH OTHER across
the whole corpus, keyed by the generic `(entity, attribute)` pair the tagger
guesses — never a per-fact rule a human wrote. Bolting that onto `check_canon.py`
would mean grafting a generic cross-doc comparator onto a file whose entire
design is "one Rule per known fact"; the two don't share a data model
(canon.yml's typed sub-tree vs. tagged_claims()'s list of dicts) or a matching
strategy (per-fact regex vs. generic entity/attribute grouping). They are
complementary and both stay: check_canon guards the handful of numbers the
owner has explicitly blessed as canon; this file finds contradictions and gaps
NOBODY has written a rule for yet, which is the entire point of Phase 1.

The architecture doc's own open question 3 ("extend doc_claims.py / measure DB,
or a small new store?") is about the CLAIM INDEX's storage, not this checker —
Phase 0 answered it by extending doc_claims.py (additive `--tag`). This file
consumes that index; it does not re-extend doc_claims.py itself, and it is not
check_canon.py's business model (a curated allowlist of facts) either.

WHAT THIS FILE DOES
====================
1. CONTRADICTION: groups prose claims with a non-null entity AND attribute by
   `(entity, attribute)` (case/whitespace normalized). Flags a group where two
   claims from DIFFERENT docs carry different normalized `value`s. Severity is
   the certainty of the disagreeing pair, per the architecture doc's own
   ranking ("Bedrock ... a contradiction is an automatic error"; "two RULED
   claims disagreeing is the real alarm"):
       BEDROCK_VIOLATION   > RULED_VS_RULED > RULED_VS_UNCONFIRMED > UNCONFIRMED
   Same-doc restatements are not flagged — that is elaboration, not drift
   across docs, and this corpus restates itself constantly within one file.

2. THIN COVERAGE: entities backed by exactly one RULED or BEDROCK claim
   anywhere in the scanned corpus. The architecture doc does not name a
   threshold (open question territory) — "1" is the judgment call made here,
   documented rather than hidden: a decided fact stated exactly once has
   nothing to cross-check it against, which is precisely the gap Phase 1 is
   for. Raising the bar to "≤2" produced too much noise on this corpus (mostly
   correct one-off facts) to be a usable signal; see the test evidence in the
   item file.

3. CHANGED-RULING WORKLIST: reuses the content-hash-baseline pattern already in
   this repo (`code_review_status.py`'s CLEAN/DIRTY hash, `codebase_health_publish.py`'s
   git fingerprint) rather than inventing a third way to notice "this changed" —
   fingerprint over timestamp, per this repo's own standing lesson. A baseline
   JSON records each doc's SHA-256 and the set of its RULED/BEDROCK
   `(entity, attribute, value)` triples. On a later run, any doc whose hash no
   longer matches the baseline is diffed at the triple level: triples that
   vanished are the worklist (something that used to be ruled no longer reads
   that way — find what cited it); triples that appeared are a lighter note
   (a new ruling landed — nothing to fix, just awareness). A doc never
   previously baselined is reported once as "no baseline yet", never
   fabricated into a worklist entry.

Certainty and gap thresholds are judgment calls, stated here rather than left
implicit. Whether this ever becomes a commit hook is architecture-doc open
question 4, explicitly NOT decided by the owner as of this writing — this file
is an on-demand tool only; nothing wires it into git hooks.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doc_claims  # noqa: E402

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(HERE)))
DEFAULT_BASELINE = os.path.join(
    ROOT, "infrastructure", "state", "canon_consistency_baseline.json")

RANK = {"BEDROCK": 3, "RULED": 2, "TENTATIVE": 1, None: 0}


def norm_entity(e):
    if not e:
        return None
    e = e.strip().strip("*`_").strip()
    return e.lower() or None


# Sentence-initial pronouns/function words get capitalized by ordinary English
# grammar, so doc_claims.py's Title-Case fallback (bold/code span absent) picks
# them up as if they were proper nouns — "Both resolve today.", "I have counted
# losses..." doc_claims.py's own _STOP_ENTITY list catches some of these but not
# all (it protects the FIRST word of a run, not every one-word entity); rather
# than touch Phase 0's already-closed, already-tested extraction, filter here.
_PRONOUN_ENTITY = {
    "both", "i", "you", "we", "he", "she", "they", "it", "this", "that",
    "these", "those", "there", "here", "none", "all", "some", "many", "much",
    "more", "most", "other", "others", "such", "same", "so", "also", "well",
    "now", "then", "still", "just", "only", "even", "too", "very", "one",
    "two", "few", "several", "who", "what", "which", "whose", "whom",
}


def plausible_entity(e):
    """A quality gate on top of Phase 0's known-noisy entity field.

    Phase 0's own docstring flags entity extraction as lexical, not semantic,
    and says refining it is exactly what Phase 1 usage would pressure-test —
    and it did: a first full-corpus run of this checker (see the item file's
    test evidence) produced ~1,900 "thin coverage" hits, almost all of them
    the heading-fallback path (`_guess_entity` gives up on bold/code/Title-Case
    and returns the nearest markdown heading verbatim) firing on numbered
    outline headings like "2. what the owner ruled, verbatim, in order" — a
    section title, not a subject. Those are real strings doc_claims.py
    produced, honestly, on prose that doesn't decompose into a clean subject;
    forcing them into the entity index anyway would make every long heading
    "thin by construction" and drown the real gaps in noise. So: keep them out
    of grouping/counting here (this file, not doc_claims.py — the tagging
    stays honest about what it can and can't extract; this is the consumer
    deciding what counts as a usable subject for cross-doc comparison).
    """
    if len(e) > 40 or len(e.split()) > 6:
        return False
    if re.search(r"[—·]|:\s|\.\s", e):
        return False
    if e in _PRONOUN_ENTITY:
        return False
    return True


def norm_attr(a):
    if not a:
        return None
    a = re.sub(r"\s+", " ", a.strip().lower())
    return a or None


def norm_value(v):
    v = (v or "").strip().strip("*`_").strip()
    v = re.sub(r"\s+", " ", v).rstrip(".")
    return v.lower()


def rel(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def collect_docs(paths):
    """Expand files/dirs into a sorted list of .md file paths."""
    out = []
    for p in paths:
        p = os.path.join(ROOT, p) if not os.path.isabs(p) else p
        if os.path.isdir(p):
            for dirpath, _dirs, files in os.walk(p):
                out += [os.path.join(dirpath, f) for f in files if f.endswith(".md")]
        elif os.path.isfile(p):
            out.append(p)
    return sorted(set(out))


def extract_all(doc_paths):
    """-> {doc_path: (sha256_hex, [tagged claim dicts])}."""
    out = {}
    for p in doc_paths:
        try:
            data = Path(p).read_bytes()
        except OSError:
            continue
        text = data.decode("utf-8", errors="replace")
        cs = doc_claims.tagged_claims(text, rel(p))
        out[p] = (hashlib.sha256(data).hexdigest(), cs)
    return out


# ---------------------------------------------------------------------------
# 1. Contradictions
# ---------------------------------------------------------------------------

def find_contradictions(extracted):
    groups = {}  # (entity, attribute) -> list of (claim, doc)
    for doc, (_h, claims) in extracted.items():
        for c in claims:
            if c["kind"] != "prose":
                continue
            e, a = norm_entity(c["entity"]), norm_attr(c["attribute"])
            if not e or not a or not plausible_entity(e):
                continue
            groups.setdefault((e, a), []).append(c)

    findings = []
    for (e, a), members in groups.items():
        # bucket by normalized value
        buckets = {}
        for c in members:
            buckets.setdefault(norm_value(c["value"]), []).append(c)
        if len(buckets) < 2:
            continue
        vals = list(buckets.items())
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                v1, cs1 = vals[i]
                v2, cs2 = vals[j]
                docs1 = {c["provenance"]["doc"] for c in cs1}
                docs2 = {c["provenance"]["doc"] for c in cs2}
                if not (docs1 - docs2) and not (docs2 - docs1):
                    continue  # same doc(s) only on both sides — not cross-doc drift
                best1 = max(cs1, key=lambda c: RANK[c["certainty"]])
                best2 = max(cs2, key=lambda c: RANK[c["certainty"]])
                r1, r2 = RANK[best1["certainty"]], RANK[best2["certainty"]]
                if r1 == 3 or r2 == 3:
                    severity = "BEDROCK_VIOLATION"
                elif r1 == 2 and r2 == 2:
                    severity = "RULED_VS_RULED"
                elif max(r1, r2) == 2:
                    severity = "RULED_VS_UNCONFIRMED"
                else:
                    severity = "UNCONFIRMED_DISAGREEMENT"
                findings.append({
                    "severity": severity,
                    "entity": e, "attribute": a,
                    "value_a": v1, "certainty_a": best1["certainty"],
                    "doc_a": best1["provenance"]["doc"], "line_a": best1["provenance"]["line_start"],
                    "value_b": v2, "certainty_b": best2["certainty"],
                    "doc_b": best2["provenance"]["doc"], "line_b": best2["provenance"]["line_start"],
                })
    order = {"BEDROCK_VIOLATION": 0, "RULED_VS_RULED": 1,
             "RULED_VS_UNCONFIRMED": 2, "UNCONFIRMED_DISAGREEMENT": 3}
    findings.sort(key=lambda f: (order[f["severity"]], f["entity"], f["attribute"]))
    return findings


# ---------------------------------------------------------------------------
# 2. Thin coverage
# ---------------------------------------------------------------------------

def find_thin_coverage(extracted, threshold=1):
    per_entity = {}  # norm_entity -> list of claim (any RULED/BEDROCK, any attribute)
    for doc, (_h, claims) in extracted.items():
        for c in claims:
            if c["kind"] != "prose" or c["certainty"] not in ("RULED", "BEDROCK"):
                continue
            e = norm_entity(c["entity"])
            if not e or not plausible_entity(e):
                continue
            per_entity.setdefault(e, []).append(c)

    thin = []
    for e, cs in per_entity.items():
        if len(cs) <= threshold:
            c = cs[0]
            thin.append({
                "entity": e, "mentions": len(cs), "certainty": c["certainty"],
                "doc": c["provenance"]["doc"], "line": c["provenance"]["line_start"],
                "text": c["text"][:160],
            })
    thin.sort(key=lambda t: t["entity"])
    return thin


def _triple_key(t):
    return (t[0], t[1] or "", t[2])


# ---------------------------------------------------------------------------
# 3. Changed-ruling worklist (content-hash baseline, cf. code_review_status.py)
# ---------------------------------------------------------------------------

def ruled_triples(claims):
    out = set()
    for c in claims:
        if c["kind"] != "prose" or c["certainty"] not in ("RULED", "BEDROCK"):
            continue
        e, a = norm_entity(c["entity"]), norm_attr(c["attribute"])
        if not e or not plausible_entity(e):
            continue
        out.add((e, a, norm_value(c["value"])))
    return out


def load_baseline(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {"docs": {}}


def build_worklist(extracted, baseline):
    base_docs = baseline.get("docs", {})
    worklist = []
    unbaselined = []
    for doc, (h, claims) in extracted.items():
        key = rel(doc)
        entry = base_docs.get(key)
        if entry is None:
            unbaselined.append(key)
            continue
        if entry.get("hash") == h:
            continue  # unchanged since baseline
        old = {tuple(t) for t in entry.get("ruled_triples", [])}
        new = ruled_triples(claims)
        removed = old - new
        added = new - old
        if removed:
            worklist.append({
                "doc": key, "kind": "RULING_CHANGED_OR_REMOVED",
                "triples": sorted(removed, key=_triple_key),
                "note": "these RULED/BEDROCK facts no longer read this way in the "
                        "doc — find and review anything that cited them",
            })
        if added:
            worklist.append({
                "doc": key, "kind": "NEW_RULING",
                "triples": sorted(added, key=_triple_key),
                "note": "new since baseline — awareness only, nothing to fix",
            })
    return worklist, unbaselined


def save_baseline(path, extracted):
    docs = {}
    for doc, (h, claims) in extracted.items():
        docs[rel(doc)] = {
            "hash": h,
            "ruled_triples": sorted(ruled_triples(claims), key=_triple_key),
        }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"docs": docs}, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*",
                     help="files or dirs to scan (default: design/Jawa/)")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--update-baseline", action="store_true",
                     help="after reporting, write the current run as the new baseline")
    ap.add_argument("--thin-threshold", type=int, default=1)
    ap.add_argument("--out", help="write full JSON report here")
    ap.add_argument("--strict", action="store_true",
                     help="exit 1 if any RULED_VS_RULED or BEDROCK_VIOLATION found")
    ap.add_argument("--all-severities", action="store_true",
                     help="print every UNCONFIRMED_DISAGREEMENT too, not just the "
                          "two alarm tiers (see module docstring: at full-corpus "
                          "scale these are mostly copula-split noise, not real "
                          "drift — full-corpus test evidence in the item file)")
    a = ap.parse_args()

    paths = a.paths or [os.path.join(ROOT, "design", "Jawa")]
    docs = collect_docs(paths)
    if not docs:
        print("canon_consistency: no .md files found under %r" % (paths,), file=sys.stderr)
        return 2

    extracted = extract_all(docs)
    contradictions = find_contradictions(extracted)
    thin = find_thin_coverage(extracted, a.thin_threshold)
    baseline = load_baseline(a.baseline)
    worklist, unbaselined = build_worklist(extracted, baseline)

    report = {
        "docs_scanned": len(docs),
        "contradictions": contradictions,
        "thin_coverage": thin,
        "changed_ruling_worklist": worklist,
        "unbaselined_docs": unbaselined,
    }
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, ensure_ascii=False)

    print("canon_consistency: %d doc(s) scanned" % len(docs))
    alarm = [f for f in contradictions if f["severity"] in ("BEDROCK_VIOLATION", "RULED_VS_RULED")]
    shown = contradictions if a.all_severities else alarm
    if shown:
        print("\nCONTRADICTIONS — %d shown of %d total" % (len(shown), len(contradictions)))
        for f in shown:
            print("  [%s] %s / %s" % (f["severity"], f["entity"], f["attribute"]))
            print("      %s:%s (%s) = %r" % (f["doc_a"], f["line_a"], f["certainty_a"], f["value_a"][:100]))
            print("      %s:%s (%s) = %r" % (f["doc_b"], f["line_b"], f["certainty_b"], f["value_b"][:100]))
    else:
        print("\nno BEDROCK/RULED-vs-RULED contradictions found.")
    if not a.all_severities and len(contradictions) > len(alarm):
        print("  (+%d lower-severity RULED_VS_UNCONFIRMED/UNCONFIRMED_DISAGREEMENT "
              "hits not shown — --all-severities or --out to see them; per the "
              "architecture doc, two RULED claims disagreeing is the real alarm)"
              % (len(contradictions) - len(alarm)))

    if thin:
        print("\nTHIN COVERAGE (<=%d ruled/bedrock mention(s)) — %d entities" % (a.thin_threshold, len(thin)))
        for t in thin[:40]:
            print("  %-30s %s:%s (%s)" % (t["entity"], t["doc"], t["line"], t["certainty"]))
        if len(thin) > 40:
            print("  ... and %d more (see --out for the full list)" % (len(thin) - 40))
    else:
        print("\nno thin-coverage entities found at threshold %d." % a.thin_threshold)

    if worklist:
        print("\nCHANGED-RULING WORKLIST — %d doc(s) changed since baseline" % len(worklist))
        for w in worklist:
            print("  %s: %s (%d triple(s))" % (w["doc"], w["kind"], len(w["triples"])))
    if unbaselined:
        print("\n%d doc(s) have no baseline yet (first run, or new file)." % len(unbaselined))

    if a.update_baseline:
        save_baseline(a.baseline, extracted)
        print("\nbaseline updated: %s" % rel(a.baseline))

    if a.strict and any(f["severity"] in ("BEDROCK_VIOLATION", "RULED_VS_RULED") for f in contradictions):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
