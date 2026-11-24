#!/usr/bin/env python3
"""modledger.py — one append-only ledger per mod; every other per-mod record is a view printed from it.

Spec: design/specs/2026-11-15-holder-pipeline-fusion.md §3.1-3.3 (his card answers at its top); plan:
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 2; item RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE.

Layout. `design/concepts/<Mod>/ledger/<WRITER>.jsonl`, one shard per producer: `DISPATCH`, `OWNER`, `STEWARD`,
`BACKFILL`, `HOLDER.<lease>` (each holder lease its own shard), `JUDGE.<run>` (each blind run its own shard, sealed by
the dispatcher when it ends). Views (generated, never edited) in `ledger/views/`.

The entry standard (design/specs/2026-11-15-mod-ledger-entry-standard.md; his 2026-11-15 "so it is not arbitrary in
size and pedantic detail" and "we must resist unlimited provenance"): one fact per entry, every field capped, evidence by
typed reference, subjects from closed classes, bars and facets from closed sets, no narration, no restating, no
no-change status, no lifecycle noise. `append` refuses a breach (REFUSED <field>: <measured> · would pass: … · smallest
fix: …, exit 2), and `lint` re-runs the same checks over every line new since the base. Nothing is spilled to a side
file: long material lives in a file the event cites. `find`, `open` and `since` read a throwaway SQLite FTS5 index under
/tmp, rebuilt whenever the shards change.

Not a second ledger engine: the write is rimflow's (`model._dir_lock` + `model._append_locked`: flock, O_APPEND, the
PIPE_BUF bound), the merged read is `model.canonical_order`, and the per-shard append-only lint is
`ledger_lint.lint_blob` (MALFORMED, NO_NEWLINE, NOT_APPEND, DUP_DIFFERENT). What is new is per-mod: who may write which
kind, the holder's fencing token, sealed judge shards, the reducer, the packet and the views.

Delete on sight (his ruling 2026-11-15 ~10:16 PM PST, via the Conductor: "Delete on sight. I really don't think that's
going to be abused to pass a judge. But we can monitor."): any writer deletes a wrong or useless entry, anyone's, with
`delete`; the lint accepts whole-line deletions and refuses a line changed in place (a correction is delete + append);
`deletions` reads git and lists for the Conductor's digest every deleted JUDGE or OWNER entry and open finding.

Every number comes from `modledger.json` (the 400k holder ceiling, the 15k packet budget, the lease idle minutes, the
standard's caps).

    modledger.py append --mod M --writer W --kind K --subject S [--text T] [--fix F] [--token N] [--run R] ...
    modledger.py grant  --mod M --lease L            DISPATCH: a new holder lease, the next fencing token
    modledger.py seal   --mod M --run R              DISPATCH: seal JUDGE.R (its hash recorded)
    modledger.py show   --mod M [SUBJECT]            events, one line each
    modledger.py state  --mod M                      the reduced state, JSON
    modledger.py packet --mod M [--budget N] [--strict]
    modledger.py resume-plan --mod M                  B: resume the holder session, rotate, or start from the packet
    modledger.py views  --mod M                      regenerate the views (append does it by itself)
    modledger.py lint   [--mod M] [--base origin/main]   exit 0 clean, 1 findings, 2 could not run
    modledger.py delete --mod M --id ID [--id ...]   delete on sight: any writer, anyone's entry; git is the archive
    modledger.py deletions [--mod M] [--since DATE] [--json]   the monitor: what was deleted, what goes on the digest
    modledger.py index  --mod M                      (re)build the throwaway search index; queries do it by themselves
    modledger.py find   --mod M|all [QUERY] [--class C] [--kind K] [--his] [--path P] [--all]
    modledger.py open   --mod M|all [--bar B]        open and claimed-fixed findings, with fix and accept
    modledger.py since  --mod M CURSOR               what changed after the packet's cursor (or an event id, or a time)

Root: `--root`, else $RM_MODLEDGER_ROOT, else this repo. A process started as one writer sets
$RM_MODLEDGER_WRITER (the launcher does), and append refuses any other shard: a holder cannot write a judge's finding
or his answer. That is tamper-evidence plus the lint, not prevention: a shell can still write a file by hand, and the
lint is what catches it (spec §3.1, GPT objection 10).
"""
import argparse
import datetime
import fcntl
import glob
import hashlib
import json
import os
import re
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(os.path.dirname(HERE), "Utils"))
import fulltext  # noqa: E402
import model                                                     # noqa: E402  rimflow's shard writer and reader
import ledger_lint                                               # noqa: E402  the append-only shard lint

REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONFIG_PATH = os.path.join(HERE, "modledger.json")
REDUCER_VERSION = 1
VIEWS = ("state.md", "history.md", "state.json")
INDEX_VERSION = 2           # bump when the index's tables or statuses change: a cached index then rebuilds
WRITER_RE = re.compile(r"^(DISPATCH|OWNER|STEWARD|BACKFILL|(HOLDER|JUDGE)\.[A-Za-z0-9_-]{1,64})$")
MOD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
REQUIRED = ("id", "key", "ts", "mod", "version", "writer", "kind", "subject", "body")
AUTH_KEYS = ("owner_said", "by_card", "per_ruling", "why")
OWNER_AUTH = ("owner_said", "by_card", "per_ruling")
_UNSET = object()


class ModLedgerError(Exception):
    """A refused append or an unusable ledger. The message says why and what would pass."""


_CFG = {}


def config(path=CONFIG_PATH):
    if path not in _CFG:
        with open(path, encoding="utf-8") as fh:
            _CFG[path] = json.load(fh)
    return _CFG[path]


def default_root():
    return os.environ.get("RM_MODLEDGER_ROOT") or REPO_ROOT


def _check_mod(mod):
    if not isinstance(mod, str) or not MOD_RE.match(mod):
        raise ModLedgerError("mod %r is not a concept folder name (letters, digits, _)" % (mod,))


def _check_writer(writer):
    if not isinstance(writer, str) or not WRITER_RE.match(writer):
        raise ModLedgerError("writer %r is not one of DISPATCH, OWNER, STEWARD, BACKFILL, HOLDER.<lease>, "
                             "JUDGE.<run>" % (writer,))


def ledger_dir(root, mod):
    _check_mod(mod)
    return os.path.join(root, "design", "concepts", mod, "ledger")


def views_dir(root, mod):
    return os.path.join(ledger_dir(root, mod), "views")


def shard_path(root, mod, writer):
    _check_writer(writer)
    return os.path.join(ledger_dir(root, mod), writer + ".jsonl")


def writer_class(writer):
    return writer.split(".", 1)[0]


def writer_suffix(writer):
    return writer.split(".", 1)[1] if "." in writer else None


def kind_allowed(writer, kind):
    kinds = config()["writers"].get(writer_class(writer), [])
    return "*" in kinds or kind in kinds


def tokens(text):
    """The estimate: characters / chars_per_token (modledger.json, measured 2026-11-21 at 1.8 on a FlowWorks brief;
    the spec's bytes / 4 counted these texts about 2x low), rounded up. A config without the ratio fails by name."""
    try:
        r = float(config()["chars_per_token"])
    except KeyError:
        raise ModLedgerError("modledger.json has no chars_per_token: the token estimate cannot be made") from None
    return int(-(-len(text) // r))


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def derive_key(ev):
    fields = {k: ev.get(k) for k in ("kind", "subject", "version", "body", "evidence", "supersedes", "code_sha",
                                     "run", "token", "authority")}
    if ev.get("kind") == "lease.renew":
        # a renew's whole content is its time: without it the brief's same command, run again, read ALREADY and the
        # lease lapsed (RIMMANDRAKE_RENEW_LEASE_TWICE_SECOND_SAID_ALREADY, live 2026-11-16)
        fields["ts"] = ev.get("ts")
    return hashlib.sha256(_canon(fields).encode("utf-8")).hexdigest()[:16]


def derive_id(writer, key):
    return "%s:%s" % (writer, hashlib.sha256(("%s\0%s" % (writer, key)).encode("utf-8")).hexdigest()[:16])


def _when(ev):
    """Order key inside the ledger: (ts, tsn), as rimflow orders its own events."""
    tsn = ev.get("tsn")
    return (str(ev.get("ts") or ""), tsn if isinstance(tsn, int) and not isinstance(tsn, bool) else 0)


def _parse_ts(ts):
    return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


# ---- the entry standard ---------------------------------------------------------------------------------------------

class Refusal(ModLedgerError):
    """A breach of the entry standard, in the refusal ruling's shape: what was measured, what would pass, the smallest
    fix (owner 2026-11-12: "ANY refusals must be as detailed as the evidence they are rejecting and include the fixes
    and paths towards passing")."""

    def __init__(self, field, measured, would_pass, fix):
        self.field, self.measured, self.would_pass, self.fix = field, measured, would_pass, fix
        super().__init__("REFUSED %s: %s · would pass: %s · smallest fix: %s" % (field, measured, would_pass, fix))


def std():
    return config()["standard"]


STACK_RE = re.compile(r"```|^\s*at [\w.`<>\[\]]+\(|\bat [A-Z][\w.`]*\.[\w.`<>]+\(|Traceback \(most recent call last\)|"
                      r"^\s*File \"[^\"]+\", line \d+", re.M)
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BAR_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
WORD_RE = re.compile(r"[a-z0-9]+")


def subject_class(subject):
    """-> 'bar' / 'finding' / 'cause' / 'trap' / 'q', the singleton's own name, or None."""
    if not isinstance(subject, str):
        return None
    if subject in std()["singletons"]:
        return subject
    head, sep, _ = subject.partition(":")
    return head if sep and head in std()["subject_classes"] else None


_FILED = {}


def _filed_ids(root):
    """-> the ids of every ticket filed in the rimflow ledger (its `file` events), read once per root: most tickets
    have no prose file, their events are the whole record."""
    shards = sorted(glob.glob(os.path.join(root, "infrastructure", "state", "ledger", "events", "*.jsonl")))
    sig = tuple((sp, os.path.getsize(sp)) for sp in shards)        # an append grows a shard: re-read then
    if _FILED.get(root, (None,))[0] != sig:
        ids = set()
        for sp in shards:
            with open(sp, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if '"file"' in line:
                        m = re.search(r'"id": ?"([A-Za-z0-9_]+)"', line)
                        if m and re.search(r'"event": ?"file"', line):
                            ids.add(m.group(1))
        _FILED[root] = (sig, ids)
    return _FILED[root][1]


def cited_file_exists(root, ref):
    """A cited repo file exists: `ref` is a path, optionally typed `path:`, with a #locator or :line. An item prose file
    moves to items/closed/ when its item closes, so a citation of items/<ID>.md also resolves there."""
    ref = re.sub(r"^path:", "", ref).split("#")[0]
    ref = re.sub(r":\d+$", "", ref)
    if os.path.exists(os.path.join(root, ref)):
        return True
    d, f = os.path.split(ref)
    return d == "infrastructure/state/items" and os.path.exists(os.path.join(root, d, "closed", f))


def _blind_fault_ids(root):
    """The fault ids the blind challenge recorded for any mod (design/concepts/*/version/blind_challenge/cycle_*/lane*/
    faults.json): a recorded name, like a legacy id. An unreadable or malformed file records nothing (never a crash)."""
    ids = set()
    pat = os.path.join(root, "design", "concepts", "*", "version", "blind_challenge", "cycle_*", "lane*", "faults.json")
    # an earlier version's cycles are set aside by maturation.py next-version (version/previous/<version>/): still recorded
    old = os.path.join(root, "design", "concepts", "*", "version", "previous", "*", "blind_challenge", "cycle_*", "lane*",
                       "faults.json")
    for fp in glob.glob(pat) + glob.glob(old):
        try:
            with open(fp, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        faults = d if isinstance(d, list) else (d.get("faults") if isinstance(d, dict) else None)
        ids.update(f["id"] for f in faults or () if isinstance(f, dict) and isinstance(f.get("id"), str))
    return ids


def _finding_name_ok(name, root):
    """A finding keeps its ticket's name: any existing rimflow item (open or closed, with a prose file or filed in the
    rimflow ledger only), a fault id a blind challenge recorded, any legacy form, or a name the project namecheck would mint."""
    for r in {root, REPO_ROOT}:
        for sub in ("", "closed"):
            if os.path.exists(os.path.join(r, "infrastructure", "state", "items", sub, name + ".md")):
                return None
        if name in _filed_ids(r) or name in _blind_fault_ids(r):
            return None
    if model.NAMED_ID.match(name):
        return None
    probs = model.mint_problems(name, set())
    return "; ".join(probs) if probs else None


def _check_subject(subject, root):
    S = std()
    cls = subject_class(subject)
    classes = ", ".join("%s:<id>" % c for c in S["subject_classes"])
    if cls is None:
        return Refusal("subject", "%r is not a subject class" % (subject,),
                       "%s, or a singleton (%s)" % (classes, ", ".join(S["singletons"])),
                       "prefix it with its class (a finding keeps its ticket's name: finding:<NAME>); `modledger.py "
                       "find` the subject first")
    rest = subject.partition(":")[2]
    if cls == "finding":
        why = _finding_name_ok(rest, root)
        if why:
            return Refusal("subject", "finding name %r fails the project namecheck (%s)" % (rest, why),
                           "an existing rimflow item name, a legacy id, or a new PROJECT_VERB_INTENTION_TWIST name",
                           "use the ticket's own name, or check one: rimflow namecheck <NAME>")
    elif cls in ("cause", "trap", "q") and not SLUG_RE.match(rest):
        return Refusal("subject", "%r is not a kebab slug" % rest, "%s:<lowercase-words-joined-by-dashes>" % cls,
                       "write it as %s:%s" % (cls, "-".join(WORD_RE.findall(rest.lower())) or "a-short-slug"))
    elif cls == "bar" and not BAR_ID_RE.match(rest):
        return Refusal("subject", "%r is not a bar id" % rest, "bar:<the bar's locked id>", "copy the id from the "
                       "mod's locked bars (modledger.py state)")
    return None


def check_entry(writer, kind, subject, body, evidence, code_sha=None, authority=None, root=None):
    """-> [Refusal]: the standard's shape checks on one entry, pure (they read no ledger; the subject's finding name
    is checked against the rimflow items on disk). `append` raises the first; the lint reports them all."""
    S = std()
    caps = S["caps"]
    out = []

    def R(field, measured, would, fix):
        out.append(Refusal(field, measured, would, fix))

    if not isinstance(kind, str) or not kind:
        R("kind", "no kind", "one of modledger.json writers", "pass --kind")
        return out
    cls = writer_class(writer or "")
    if kind in S["lifecycle_kinds"] and not kind_allowed(writer, kind):
        R("kind", "%s is lifecycle noise for %s (claims, leases, reassignments, runs)" % (kind, writer),
          "a fact kind (modledger.json writers.%s)" % cls, "write nothing: the launcher records runs itself, and a "
          "miner never mines lifecycle events (standard rule 10)")
        return out
    if kind not in S["required"]:
        R("kind", "%r is not a kind of the mod ledger" % kind, "one of: %s" % ", ".join(sorted(S["required"])),
          "pick the kind that says what changed (a free remark is a note with `about`)")
        return out
    if not isinstance(body, dict):
        R("body", "a %s, not a JSON object" % type(body).__name__, "a JSON object of the kind's fields",
          "pass --body '{...}'")
        return out
    for f in S["required"][kind]:
        if f not in body or body[f] is None or body[f] == "":
            R(f, "missing (a %s carries %s)" % (kind, ", ".join(S["required"][kind])), "%s present" % f,
              "add %s to the body (--body '{\"%s\": ...}')" % (f, f))
    if kind in S["said_or_text"] and not (body.get("said") or body.get("text")):
        R("said", "missing: neither said (his words) nor text (a steward's decision)", "said or text present",
          "put his sentence, verbatim, in said; a steward decision in text")
    for f, v in body.items():
        cap = caps.get(f)
        if cap is None or v is None:
            continue
        if f == "decides" and isinstance(v, list):
            v = "; ".join(str(x) for x in v)
        if not isinstance(v, str):
            R(f, "a %s, not a string" % type(v).__name__, "one string of <= %d chars" % cap,
              "write %s as one plain sentence; structure goes in its own fields or a cited file" % f)
            continue
        if len(v) > cap:
            R(f, "%d chars > %d" % (len(v), cap), "<= %d chars" % cap,
              "split into two events (one fact each), or move the detail into a file and cite it with --evidence "
              "path:…" if f != "said" else "keep his deciding sentence verbatim in said and cite the whole with "
              "ledger:<id> or card:<id>")
        if f == "said":
            continue
        if "\n" in v or "\r" in v:
            R(f, "%d line breaks: a pasted log or several paragraphs" % (v.count("\n") + v.count("\r")),
              "one paragraph, no newline", "keep one sentence or two and cite the rest (path:, run:, test:)")
        elif STACK_RE.search(v):
            R(f, "a pasted stack, code fence or traceback (%r)" % STACK_RE.search(v).group(0)[:40],
              "the fact in words", "cite the log or code instead (path:…#row, run:<id>, test:<id>)")
        if f in ("text", "done") and any(v.startswith(o) for o in S["narration_openers"]):
            R(f, "narration (opens %r)" % v[:14], "the fact itself, not what you did",
              "state the fact (what is true, what changed, what was ruled out); git and the run log hold the doing")
    for f in ("bars", "tags", "depends_on"):
        if f in body and body[f] is not None and not (isinstance(body[f], list) and
                                                     all(isinstance(x, str) and x for x in body[f])):
            R(f, "a %s, not a list of names" % type(body[f]).__name__, "a JSON list of strings",
              "write %s as [\"a\", \"b\"]" % f)
    tags = body.get("tags") if isinstance(body.get("tags"), list) else []
    bad = [t for t in tags if t not in S["facets"]]
    if bad:
        R("tags", "unknown facet(s) %s" % ", ".join(map(str, bad)), "tags from %s" % ", ".join(S["facets"]),
          "use the nearest facet; there are no free tags")
    if kind == "finding.open" and isinstance(body.get("bars"), list) and not body["bars"] and not tags:
        R("bars", "empty, and no facet tag", "a bar id the finding bears on, or bars [] with a facet tag",
          "name the bar, or write bars [] and tags [\"instrument\"] (or the facet that fits) when no bar fits")
    for f in ("class", "how_checked"):
        if body.get(f) is not None and body[f] not in S["values"][f]:
            R(f, "%r" % (body[f],), "one of %s" % ", ".join(S["values"][f]), "pick the value that fits")
    if kind in ("test.run", "live.run") and body.get("result") not in S["values"]["result"]:
        R("result", "%r" % (body.get("result"),), "one of %s" % ", ".join(S["values"]["result"]),
          "record PASS, FAIL, UNMEASURED or UNRUN; a count goes in its own field (counts)")
    if kind in S["code_sha_required"] and not code_sha:
        R("code_sha", "missing on a %s" % kind, "the sha ./publish printed", "pass --code-sha <the PUBLISHED sha>")
    if kind in S["code_sha_unless_unrun"] and not code_sha and body.get("result") != "UNRUN":
        R("code_sha", "missing on a %s with result %s" % (kind, body.get("result")), "the sha the run tested",
          "pass --code-sha, or record result UNRUN with the command when it did not run")
    if kind == "finding.withdrawn" and cls == "HOLDER" and S["holder_withdrawn_needs"] not in \
            str(body.get("how_checked") or ""):
        R("how_checked", "%r: a holder withdraws a finding only with a test" % (body.get("how_checked"),),
          "how_checked naming %s" % S["holder_withdrawn_needs"], "write the test that shows it is not a defect, "
          "or let a JUDGE or STEWARD withdraw it")
    if kind in S["authority_required"] and not authority:
        R("authority", "none", "--owner-said, --by-card, --per-ruling or --why", "say whose decision this is")
    if not isinstance(evidence, list):
        R("evidence", "a %s, not a list" % type(evidence).__name__, "a list of typed refs", "pass --evidence per ref")
        evidence = []
    if len(evidence) > S["evidence_max"]:
        R("evidence", "%d refs > %d" % (len(evidence), S["evidence_max"]), "<= %d refs" % S["evidence_max"],
          "keep the refs that decide it; one file listing the rest is one ref")
    types = S["evidence_types"]
    for ref in evidence:
        if not isinstance(ref, str):
            R("evidence", "a %s, not a ref string" % type(ref).__name__, "<type>:<target>, type one of %s"
              % ", ".join(types), "write it as path:<repo path> (or sha:, ext:, …)")
            continue
        head, sep, tail = ref.partition(":")
        if not sep or head not in types or not tail.strip():
            R("evidence", "%r is untyped" % ref[:40], "<type>:<target>, type one of %s" % ", ".join(types),
              "prefix it (path:, sha:, ext:, test:, run:, item:, ledger:, card:); a description is not a ref")
        elif len(ref) > S["evidence_ref_chars"]:
            R("evidence", "a ref of %d chars > %d" % (len(ref), S["evidence_ref_chars"]),
              "<= %d chars" % S["evidence_ref_chars"], "cite the file, not its contents")
    if kind in S["evidence_required"] and not evidence:
        R("evidence", "no ref on a %s" % kind, ">= 1 typed ref", "cite where it was seen (path:, run:, item:, …)")
    if isinstance(subject, str) and subject.strip():
        bad = _check_subject(subject, root or REPO_ROOT)
        if bad:
            out.append(bad)
    else:
        R("subject", "none", "a subject (bar:, finding:, cause:, trap:, q:, or a singleton)", "pass --subject")
    return out


def _norm(text):
    return " ".join(WORD_RE.findall(str(text or "").lower()))


def _words(text):
    return {w for w in WORD_RE.findall(str(text or "").lower()) if len(w) >= 3}


def _body_text(ev):
    b = ev.get("body") or {}
    return b.get("said") or b.get("text") or ""


def locked_bars(events):
    return {e["subject"].partition(":")[2] for e in events if e.get("kind") in ("bar.locked", "bar.added")
            and isinstance(e.get("subject"), str) and e["subject"].startswith("bar:")}


def live_subjects(st):
    """-> {subject: status} of the subjects still live (not verified, withdrawn, cleared, answered or withdrawn)."""
    out = {}
    for k, f in st["findings"].items():
        if f["status"] not in ("verified", "withdrawn"):
            out[k] = f["status"]
    for k, c in st["causes"].items():
        out[k] = c["status"]
    for k, t in st.get("traps", {}).items():
        if t["status"] != "cleared":
            out[k] = t["status"]
    for k, q in st["questions"].items():
        if q.get("status") == "open":
            out[k] = "open"
    return out


def check_context(events, writer, kind, subject, body, code_sha=None, new_subject=None):
    """-> [Refusal]: the checks that need the ledger (`events`, the entries before this one): bar ids against the locked
    bars, `about`/`finding` naming subjects the ledger holds, the same text again, a no-change test result, a new
    subject matching a live one."""
    out = []
    body = body if isinstance(body, dict) else {}
    bars = locked_bars(events)
    cls = subject_class(subject)
    if cls == "bar" and kind not in ("bar.locked", "bar.added") and subject.partition(":")[2] not in bars:
        out.append(Refusal("subject", "%s names no locked bar of this mod" % subject, "bar:<one of %d locked ids>"
                           % len(bars), "copy the id from `modledger.py state` (bars), or write it on the finding"))
    named = [b for b in (body.get("bars") if isinstance(body.get("bars"), list) else []) if isinstance(b, str)]
    if isinstance(body.get("bar"), str):
        named.append(body["bar"])
    unknown = sorted(set(named) - bars)
    if unknown:
        out.append(Refusal("bars", "unknown bar id(s) %s (%d locked)" % (", ".join(unknown), len(bars)),
                           "ids from the mod's locked bars", "copy them from `modledger.py state`, or write bars [] "
                           "with a facet tag when none fits"))
    subjects = {e.get("subject") for e in events}
    if kind == "note" and isinstance(body.get("about"), str) and body["about"] not in subjects:
        out.append(Refusal("about", "%r: no entry of this mod has that subject" % body["about"],
                           "an existing subject", "`modledger.py find` it; a new fact is its own kind, not a note"))
    if kind.startswith("cause.") and isinstance(body.get("finding"), str) and body["finding"] not in subjects:
        out.append(Refusal("finding", "%r: no entry of this mod has that subject" % body["finding"],
                           "the finding subject this cause explains", "open the finding first, or name the right one"))
    text = _norm(_body_text({"body": body}))
    if text:
        same = [e for e in events if e.get("subject") == subject and _norm(_body_text(e)) == text]
        if same:
            out.append(Refusal("text", "restates %s (the same text on %s)" % (same[-1].get("id"), subject),
                               "a new fact", "write nothing; or delete the old entry if this one is the right value"))
    if kind in ("test.run", "live.run"):
        prior = [e for e in events if e.get("subject") == subject and e.get("kind") == kind]
        if prior:
            last = prior[-1]
            lb = last.get("body") or {}
            if (lb.get("command"), last.get("code_sha"), lb.get("result")) == (body.get("command"), code_sha,
                                                                             body.get("result")):
                out.append(Refusal("result", "no change: %s %s on %s, as %s already says" % (
                    body.get("command"), body.get("result"), code_sha, last.get("id")), "a different result, sha or "
                    "command", "write nothing: a run that changes nothing is not an entry"))
    if cls in ("finding", "cause", "trap", "q") and subject not in subjects and not new_subject:
        hit = _mint_duplicate(events, subject, cls, body)
        if hit:
            out.append(Refusal("subject", "%s looks like %s" % (subject, "; ".join(
                "%s (%s, %s)" % c for c in hit)), "a subject no live one already covers",
                "write to %s, or pass --new-subject \"<why it differs>\"" % hit[0][0]))
    return out


def _fts_query(text):
    words = sorted(_words(text))
    return " OR ".join('"%s"' % w for w in words) if words else None


def _mint_duplicate(events, subject, cls, body):
    """-> [(subject, status, writer#seq)] of live subjects of the same class this new one matches: FTS5 BM25 ranks the
    candidates, token containment >= standard.mint_duplicate_overlap decides (raw BM25 is not comparable across
    ledgers of different size)."""
    S = std()
    mine = _words(_body_text({"body": body})) | _words(subject.partition(":")[2].replace("_", " "))
    if len(mine) < S["mint_duplicate_min_tokens"]:
        return []
    live = live_subjects(reduce(events))
    first = {}
    for e in events:
        s = e.get("subject")
        if s in live and subject_class(s) == cls and s not in first:
            first[s] = e
    if not first:
        return []
    q = _fts_query(" ".join(sorted(mine)))
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE VIRTUAL TABLE f USING fts5(subject, text)")
        con.executemany("INSERT INTO f(subject, text) VALUES (?, ?)",
                        [(s, "%s %s" % (s.partition(":")[2].replace("_", " "), _body_text(e))) for s, e in first.items()])
        rows = con.execute("SELECT subject, text FROM f WHERE f MATCH ? ORDER BY bm25(f) LIMIT 5", (q,)).fetchall()
    finally:
        con.close()
    out = []
    for s, t in rows:
        theirs = _words(t)
        if theirs and len(mine & theirs) / min(len(mine), len(theirs)) >= S["mint_duplicate_overlap"]:
            e = first[s]
            out.append((s, live[s], "%s#%s" % (e.get("_shard") or e.get("writer"), e.get("_seq", "?"))))
    return out


# ---- read -----------------------------------------------------------------------------------------------------------

def shard_names(root, mod):
    d = ledger_dir(root, mod)
    try:
        return sorted(n[:-len(".jsonl")] for n in os.listdir(d) if n.endswith(".jsonl"))
    except OSError:
        return []


def read(root, mod):
    """-> every event of the mod, merged across shards in canonical order (rimflow's), each carrying `_shard` and
    `_seq` (its line number in its shard: shards only grow, so the number never moves). Unparsable lines are skipped
    here; the lint reports them."""
    where = {}
    raw_events = []
    for shard in shard_names(root, mod):
        path = os.path.join(ledger_dir(root, mod), shard + ".jsonl")
        for seq, line in enumerate(model._read_lines(path), 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if not isinstance(ev, dict):
                continue
            k = model.event_key(ev)
            if k not in where:
                where[k] = (shard, seq)
                raw_events.append(ev)
    out = []
    for ev in model.canonical_order(raw_events):
        shard, seq = where[model.event_key(ev)]
        out.append(dict(ev, _shard=shard, _seq=seq))
    return out


def _clean(ev):
    return {k: v for k, v in ev.items() if not k.startswith("_")}


# ---- leases and seals -----------------------------------------------------------------------------------------------

def leases(events):
    """-> {lease: {token, granted, last, released, void}} plus the current (highest-token, not void) lease, from DISPATCH
    grants and the holder's own activity. A lease DISPATCH revoked before its holder wrote a line (a run that never
    started, a packet over the line) is void: it fences no other lease (RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_
    STARTED: Explosive Knockback's live holder run-1794896914 was fenced by run-1794896974, which never started)."""
    by = {}
    current = None
    for ev in events:
        if ev.get("writer") == "DISPATCH" and ev.get("kind") == "lease.grant":
            b = ev.get("body") or {}
            lease, tok = b.get("lease"), b.get("token")
            if isinstance(lease, str) and isinstance(tok, int):
                by[lease] = {"lease": lease, "token": tok, "granted": _when(ev), "last": ev.get("ts"),
                             "released": False, "revoked": False, "void": False}
        elif ev.get("writer") == "DISPATCH" and ev.get("kind") == "lease.revoke":
            lease = (ev.get("body") or {}).get("lease")
            if lease in by:
                by[lease]["released"] = by[lease]["revoked"] = True
    wrote = {writer_suffix(ev["writer"]) for ev in events if writer_class(ev.get("writer") or "") == "HOLDER"
             and (by.get(writer_suffix(ev["writer"])) or {}).get("token") == ev.get("token")}
    for lease, g in by.items():
        g["void"] = g["revoked"] and lease not in wrote
        if not g["void"] and (current is None or g["token"] > by[current]["token"]):
            current = lease
    for ev in events:
        if writer_class(ev.get("writer") or "") == "HOLDER" and not fenced(ev, by):
            lease = writer_suffix(ev["writer"])
            if ev.get("kind") == "lease.release":
                by[lease]["released"] = True
            if ev.get("ts") and ev["ts"] > (by[lease]["last"] or ""):
                by[lease]["last"] = ev["ts"]
    return by, current


def fenced(ev, by):
    """-> a reason string when a HOLDER event does not count (no token, a token never granted to its lease, or a
    newer lease granted before it was written), else None. The reducer ignores such events; the lint names them."""
    lease = writer_suffix(ev.get("writer") or "")
    tok = ev.get("token")
    g = by.get(lease)
    if not isinstance(tok, int) or isinstance(tok, bool):
        return "a HOLDER event carries no fencing token"
    if g is None or g["token"] != tok:
        return "token %r was never granted to lease %r" % (tok, lease)
    if _when(ev) < g["granted"]:
        return "written before its lease was granted"
    newer = [o for o in by.values() if o["token"] > tok and o["granted"] <= _when(ev) and not o.get("void")]
    if newer:
        n = max(newer, key=lambda o: o["token"])
        return "stale token %d: lease %r (token %d) was granted before it" % (tok, n["lease"], n["token"])
    return None


def seals(events):
    """-> {judge shard name: latest judge.sealed body}, for the shards whose latest seal event is not a judge.unsealed
    (a voided run's seal reopened for its own lines: unseal)."""
    out = {}
    for ev in events:
        if ev.get("writer") == "DISPATCH" and ev.get("kind") in ("judge.sealed", "judge.unsealed"):
            b = ev.get("body") or {}
            if isinstance(b.get("shard"), str):
                if ev["kind"] == "judge.sealed":
                    out[b["shard"]] = b
                else:
                    out.pop(b["shard"], None)
    return out


def _shard_bytes(root, mod, shard):
    try:
        with open(os.path.join(ledger_dir(root, mod), shard + ".jsonl"), "rb") as fh:
            return fh.read()
    except OSError:
        return b""


# ---- append ---------------------------------------------------------------------------------------------------------

def _lock(root, mod, what):
    """An exclusive lock per (ledger, purpose), kept outside the tree so git never sees it. The shard's own flock is
    taken by model._append_locked; this one makes check-then-append (idempotency, lease) one step."""
    tag = hashlib.sha256(("%s\0%s" % (os.path.abspath(ledger_dir(root, mod)), what)).encode()).hexdigest()[:20]
    fd = os.open(os.path.join("/tmp", "modledger-%s.lock" % tag), os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _unlock(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _canon_line(ev):
    return json.dumps(ev, separators=(",", ":"), ensure_ascii=False) + "\n"


def append(root, mod, writer, kind, subject, body=None, version=None, evidence=(), supersedes=None, code_sha=None,
           token=None, run=None, key=None, authority=None, ts=None, now=None, env_writer=_UNSET, views=True,
           new_subject=None):
    """Validate and append one event to `writer`'s shard. -> (event id, created). An identical event already in the
    shard (same idempotency key) is not written again: (its id, False). Refusals raise ModLedgerError saying why; a
    breach of the entry standard raises Refusal (measured, would pass, smallest fix). `new_subject` is the writer's
    reason a new subject differs from the live one it resembles; it is kept in the body."""
    _check_mod(mod)
    _check_writer(writer)
    if env_writer is _UNSET:
        env_writer = os.environ.get("RM_MODLEDGER_WRITER") or None
    if env_writer and env_writer != writer:
        raise ModLedgerError("this process writes as %s; it may not append to the %s shard (a holder never writes a "
                             "judge's finding or his words)" % (env_writer, writer))
    cls = writer_class(writer)
    body = dict(body) if isinstance(body, dict) else ({} if body is None else body)
    evidence = list(evidence) if isinstance(evidence, (list, tuple)) else ([] if evidence is None else evidence)
    if new_subject and isinstance(body, dict):
        body["new_subject_why"] = new_subject
    authority = {k: v for k, v in (authority or {}).items() if v} or None
    probs = check_entry(writer, kind, subject, body, evidence, code_sha, authority, root)
    if probs:
        raise probs[0]
    if not kind_allowed(writer, kind):
        raise ModLedgerError("%s may not write %r (modledger.json writers.%s)%s"
                             % (writer, kind, cls, "; only a JUDGE turns a finding green"
                                if kind.startswith("finding.") else ""))
    if authority and set(authority) - set(AUTH_KEYS):
        raise ModLedgerError("authority keys are %s" % (AUTH_KEYS,))
    if kind == "finding.open":
        fix = body.get("proposed_fix")
        if not isinstance(fix, str) or len(fix.strip()) < config()["proposed_fix_min_chars"]:
            raise Refusal("proposed_fix", "%d chars" % len(fix.strip()) if isinstance(fix, str) else "missing",
                          ">= %d chars: the precise fix the finder would make (his card 2026-11-15: 'Anyone finding "
                          "anything documents precisely how they would fix it but it goes back to the holder fully "
                          "informed.')" % config()["proposed_fix_min_chars"], "pass --fix \"<file: the change>\"")
    if cls == "OWNER" and not (authority and any(authority.get(k) for k in OWNER_AUTH)):
        raise ModLedgerError("an OWNER event needs his authority: --owner-said, --by-card or --per-ruling")
    if kind == "decision" and not authority:
        raise ModLedgerError("a decision needs its provenance: --owner-said, --by-card, --per-ruling or --why")
    if cls == "BACKFILL" and not evidence:
        raise ModLedgerError("a BACKFILL event cites the old file it came from (--evidence)")
    if cls == "JUDGE":
        if run != writer_suffix(writer):
            raise ModLedgerError("a JUDGE.<run> shard is written by that run only: pass --run %s"
                                 % writer_suffix(writer))
    elif run is not None and not isinstance(run, str):
        raise ModLedgerError("run is a name")
    if cls == "HOLDER" and (not isinstance(token, int) or isinstance(token, bool)):
        raise ModLedgerError("a HOLDER event carries its lease's fencing token (--token)")
    if cls != "HOLDER" and token is not None:
        raise ModLedgerError("only HOLDER events carry a fencing token")
    lk = _lock(root, mod, "append")
    try:
        events = read(root, mod)
        if cls == "JUDGE" and writer in seals(events):
            raise ModLedgerError("%s is sealed (its run ended); a later judge writes its own shard" % writer)
        if cls == "HOLDER":
            by, current = leases(events)
            lease = writer_suffix(writer)
            g = by.get(lease)
            if g is None:
                raise ModLedgerError("lease %r was never granted (the dispatcher grants: modledger grant; a clone cut before its "
                                     "grant landed lacks it: ./sync, then retry)" % lease)
            if g["token"] != token:
                raise ModLedgerError("token %d is not lease %r's token" % (token, lease))
            if current is None:     # every lease is void (revoked before its holder wrote): none writes
                raise ModLedgerError("lease %r was revoked before its holder wrote (a run that never started); ask the "
                                     "dispatcher for a new one" % lease)
            if current != lease:
                raise ModLedgerError("stale token %d: lease %r (token %d) has fenced lease %r; this run must stop"
                                     % (token, current, by[current]["token"], lease))
            if g["released"]:
                raise ModLedgerError("lease %r was released; ask the dispatcher for a new one" % lease)
            idle = config()["lease_idle_minutes"]
            nowts = now or model.now()
            if g["last"] and (_parse_ts(nowts) - _parse_ts(g["last"])).total_seconds() > idle * 60:
                raise ModLedgerError("lease %r lapsed: idle since %s, more than %d minutes (modledger.json "
                                     "lease_idle_minutes)" % (lease, g["last"], idle))
        if supersedes is not None and supersedes not in {e.get("id") for e in events}:
            raise ModLedgerError("supersedes %r: no event of this mod has that id" % (supersedes,))
        if version is None:
            version = reduce(events)["version"]
        if not isinstance(version, str) or not version:
            raise ModLedgerError("this ledger names no Design Version yet: pass --version")
        ev = {"ts": ts or model.now(), "tsn": time.time_ns(), "mod": mod, "version": version, "writer": writer,
              "run": run, "kind": kind, "subject": subject, "body": body, "evidence": evidence}
        for k, v in (("supersedes", supersedes), ("code_sha", code_sha), ("token", token), ("authority", authority)):
            if v is not None:
                ev[k] = v
        ev["key"] = key or derive_key(ev)
        ev["id"] = derive_id(writer, ev["key"])
        for e in events:
            if e.get("_shard") == writer and e.get("key") == ev["key"]:
                return e["id"], False
        sup = {e["supersedes"] for e in events if isinstance(e.get("supersedes"), str)}
        probs = check_context([e for e in events if e.get("id") not in sup], writer, kind, subject, body, code_sha,
                              new_subject)
        if probs:
            raise probs[0]
        blob = _canon_line(ev).encode("utf-8")
        cap = min(std()["line_bytes"], model.PIPE_BUF - 1)
        if len(blob) > cap:
            big = max(((k, len(_canon(v).encode("utf-8"))) for k, v in list(body.items()) + [("evidence", evidence)]),
                      key=lambda t: t[1])
            raise Refusal("line", "%d bytes > %d (largest: %s, %d bytes)" % (len(blob), cap, big[0], big[1]),
                          "<= %d bytes" % cap, "shorten %s or cite it: one fact per entry, long material in a file "
                          "named with --evidence path:…" % big[0])
        path = shard_path(root, mod, writer)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dlock = model._dir_lock(os.path.dirname(path))
        try:
            model._append_locked(path, blob)
        finally:
            if dlock is not None:
                os.close(dlock)
    finally:
        _unlock(lk)
    if views:
        write_views(root, mod)
    return ev["id"], True


def grant(root, mod, lease, version=None, ts=None, views=True):
    """DISPATCH grants a holder lease with the next fencing token. -> the token. The new lease fences every older
    one at once: an older holder's next append is refused, and its later lines are ignored by the reducer."""
    if not re.match(r"^[A-Za-z0-9_-]{1,64}$", lease or ""):
        raise ModLedgerError("lease %r: letters, digits, _ and - only" % (lease,))
    lk = _lock(root, mod, "grant")
    try:
        by, _ = leases(read(root, mod))
        if lease in by:
            raise ModLedgerError("lease %r was already granted (token %d); a new run gets a new lease name"
                                 % (lease, by[lease]["token"]))
        tok = max([g["token"] for g in by.values()] + [0]) + 1
        append(root, mod, "DISPATCH", "lease.grant", "lease", body={"lease": lease, "token": tok},
               version=version, ts=ts, views=views)
    finally:
        _unlock(lk)
    return tok


def _origin_shard_bytes(root, mod, shard):
    """-> (bytes, cause): the shard on origin/main (fetched first), b"" when origin has none; or (None, cause) when git
    could not answer (not a git tree, no origin, no network). The caller then cannot tell, and does not refuse."""
    import subprocess
    cause, out = None, None
    try:
        rel = os.path.relpath(os.path.join(ledger_dir(root, mod), shard + ".jsonl"), root)
        subprocess.run(["git", "-C", root, "fetch", "-q", "origin", "main"], capture_output=True, timeout=60, check=True)  # budget: class=call
        r = subprocess.run(["git", "-C", root, "show", "origin/main:" + rel.replace(os.sep, "/")],
                           # budget: danger=a hung git holds the ledger read; longest=0.9s (180 local git calls sampled at load
                           # budget: 20 to 52, 2026-11-24)
                           capture_output=True, timeout=30)
        if r.returncode == 0:
            out = r.stdout
        elif b"exists on disk, but not in" in r.stderr or b"does not exist" in r.stderr:
            out = b""
        else:
            cause = "git show: " + r.stderr.decode("utf-8", "replace").strip()
    except (OSError, subprocess.SubprocessError) as e:
        cause = "%s: %s" % (type(e).__name__, e)
    return out, cause


def seal(root, mod, run, ts=None, views=True):
    """DISPATCH seals JUDGE.<run> when the run ends: its hash and line count, so a later edit is detectable."""
    shard = "JUDGE.%s" % run
    _check_writer(shard)
    data = _shard_bytes(root, mod, shard)
    if not data.strip():
        theirs, _could_not_look = _origin_shard_bytes(root, mod, shard)
        if theirs and theirs.strip():
            raise ModLedgerError("%s is empty here but origin/main holds %d bytes of it: this clone is behind; sync it "
                                 "before sealing (an empty seal makes the whole-tree lint refuse every publish)"
                                 % (shard, len(theirs)))
    body = {"shard": shard, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "lines": data.count(b"\n"), "line_sha": [_line_sha(l) for l in data.split(b"\n") if l.strip()]}
    if len(_canon(body).encode("utf-8")) > std()["line_bytes"] // 2:
        del body["line_sha"]          # too many lines to list: the seal then detects growth by count only
    eid, _ = append(root, mod, "DISPATCH", "judge.sealed", "judge", body=body, ts=ts, views=views)
    return eid


def unseal(root, mod, run, why, void=None, ts=None, views=True):
    """DISPATCH reopens the seal of JUDGE.<run> for that run's own lines: only for a run that was VOIDED (the caller
    checks: maturation_dispatch.reopen_void_judge), whose shard was sealed when its unit died. Its lines then append
    and lint; the next seal (the resumed run's end, or reopen_void_judge's own) closes it again
    (design/specs/2026-11-23-resume-voided-blind-judge/boundary.md). -> the event id, or None when it is not sealed."""
    shard = "JUDGE.%s" % run
    _check_writer(shard)
    if shard not in seals(read(root, mod)):
        return None
    eid, _ = append(root, mod, "DISPATCH", "judge.unsealed", "judge", ts=ts, views=views,
                    body={"shard": shard, "why": fulltext.fit(str(why), 300), "void": void})
    return eid


def holder_brief(mod, lease, token, role, stage, by_program=False):
    """-> the lines that follow the packet in a holder's brief: who it writes as and how it checkpoints. by_program:
    rm-run-alive.timer renews this run's lease from its process (run_alive.py), so the brief asks for no renewal."""
    me = "python3 src/RimMandrake/rimflow/modledger.py"
    w = "HOLDER.%s" % lease
    return "\n".join([
        "## You hold %s's ledger: run %s, role %s, stage %s" % (mod, lease, role, stage or UNM_STAGE),
        "",
        "The packet above is where this mod stands; start from it, not from ticket prose, and resume at stage %s "
        "(never stage 1). You write as `%s` with fencing token %d (RM_MODLEDGER_WRITER is set to it; any other shard "
        "refuses you). Every append carries `--writer %s --token %d`." % (stage or UNM_STAGE, w, token, w, token),
        "",
        "A program renews your lease while your process lives; append no lease.renew." if by_program else
        "Keep the lease alive (RIMMANDRAKE_RENEW_HOLDER_LEASE_BRIEF_NEVER_SAID_HOW): it lapses for good after %d minutes "
        "with no ledger event of yours (rimflow notes do not count), and a lapsed lease refuses every later append, "
        "your checkpoint included. In a long stretch (a game load, a live run) append "
        "`%s append --mod %s --writer %s --token %d --kind lease.renew --subject session` at least every %d minutes."
        % (config()["lease_idle_minutes"], me, mod, w, token, max(5, config()["lease_idle_minutes"] - 10)),
        "",
        "Before you stop, and at each natural boundary, write a checkpoint of the fixed shape; a run that ends "
        "without one is flagged NO_CHECKPOINT:",
        "",
        "    %s append --mod %s --writer %s --token %d --kind session.checkpoint --subject session \\"
        % (me, mod, w, token),
        "      --body '{\"done\": \"<what landed>\", \"next\": \"<one imperative>\", \"ruled_out\": \"<what you refuted>\"}'",
        "",
        "Findings, causes tried and refuted, traps and tests go in as their own kinds (`%s append --help`); "
        "`%s find --mod %s <words>` before you mint a subject." % (me, me, mod),
    ])


UNM_STAGE = "UNMEASURED"


def launch(root, mod, lease, role, stage=None, ts=None, views=True, budget=None, by_program=False):
    """DISPATCH starts a holder's stage run from the packet (spec §3.1, §3.3): grants `lease` (the next fencing token),
    records run.start naming the lease, the role, the stage the ledger stands at now (`stage` only when the ledger
    names none) and the packet's size, and -> {"token", "run", "brief", "stage", "writer"}; the brief begins with the
    packet text, then how the holder writes and checkpoints. The run is named for its lease. The packet AND the holder
    lines fit `budget` (packet_budget_tokens): the packet is trimmed to what the holder lines leave (FlowWorks launched
    at 15,093 against 15,000, RIMMANDRAKE_DISPATCH_PILOT_HOLDER_RUN_ITSELF_HAND_LAUNCHED_TWICE); one that still cannot
    fit raises, its lease revoked and no run.start written."""
    _check_mod(mod)
    budget = budget or config()["packet_budget_tokens"]
    tok = grant(root, mod, lease, ts=ts, views=False)
    events = read(root, mod)
    at = reduce(events).get("stage") or stage
    tail = "\n\n" + holder_brief(mod, lease, tok, role, at, by_program) + "\n"
    room = max(1, budget - tokens(tail) - 1)
    try:
        text, _info = packet_from(mod, events, budget=room, stale=stale_check(root))
    except Exception:                               # noqa: BLE001 — the git staleness check is a nicety, not the packet
        text, _info = packet_from(mod, events, budget=room)
    brief = text.rstrip("\n") + tail
    if tokens(brief) > budget:
        append(root, mod, "DISPATCH", "lease.revoke", "lease", body={"lease": lease}, ts=ts, views=views)
        raise ModLedgerError("packet over the line: %d tokens with the holder lines > packet_budget_tokens %d, and "
                             "nothing droppable is left; lease %r revoked, no run started" % (tokens(brief), budget,
                                                                                             lease))
    append(root, mod, "DISPATCH", "run.start", "run", run=lease, ts=ts, views=views,
           body={"run": lease, "lease": lease, "token": tok, "role": role, "stage": at, "packet_tokens": tokens(text)})
    return {"token": tok, "run": lease, "brief": brief, "stage": at, "writer": "HOLDER.%s" % lease}


def end_run(root, mod, run, status, ts=None, views=True):
    """DISPATCH records run.end with its status and -> its flags: NO_CHECKPOINT when that run's holder (not fenced)
    wrote no session.checkpoint with non-empty done, next and ruled_out after its run.start."""
    events = read(root, mod)
    starts = [e for e in events if e.get("writer") == "DISPATCH" and e.get("kind") == "run.start"
              and (e.get("body") or {}).get("run", e.get("run")) == run]
    if not isinstance(run, str) or not starts:
        raise ModLedgerError("run %r has no run.start in %s's ledger (modledger.launch records it)" % (run, mod))
    st = starts[-1]
    lease = (st.get("body") or {}).get("lease") or run
    by, _ = leases(events)
    ok = False
    for e in events:
        if (e.get("writer") == "HOLDER.%s" % lease and e.get("kind") == "session.checkpoint"
                and _when(e) >= _when(st) and not fenced(e, by)):
            b = e.get("body") or {}
            if all(isinstance(b.get(k), str) and b[k].strip() for k in ("done", "next", "ruled_out")):
                ok = True
    flags = [] if ok else ["NO_CHECKPOINT"]
    if str(status) == "never_started" and lease in by and not by[lease]["revoked"]:
        # a run that never started wrote nothing: its lease is revoked, void, and fences the live holder no more
        append(root, mod, "DISPATCH", "lease.revoke", "lease", body={"lease": lease, "why": "never_started"}, ts=ts,
               views=False)
    append(root, mod, "DISPATCH", "run.end", "run", run=run, ts=ts, views=views,
           body={"run": run, "lease": lease, "status": str(status), "flags": flags})
    return flags


def _line_sha(line):
    return hashlib.sha256(line.strip()).hexdigest()[:12]


def _edited_in_place(rel, data, base_data):
    """A line on the base whose event id now carries different content: a change in place (a correction is delete +
    append, so the old value never survives a union merge beside the new one)."""
    if not base_data:
        return []
    def by_id(blob):
        out = {}
        for l in (blob or b"").decode("utf-8", errors="replace").split("\n"):
            try:
                e = json.loads(l)
            except ValueError:
                continue
            if isinstance(e, dict) and isinstance(e.get("id"), str):
                out.setdefault(e["id"], set()).add(_canon(e))
        return out
    base, now = by_id(base_data), by_id(data)
    return [("EDITED_IN_PLACE", rel, 0, "entry %s changed in place; to correct it, delete it (modledger.py delete) and "
             "append the right value" % i) for i in sorted(now) if i in base and not now[i] & base[i]]


DELETE_REFUSED = ("lease.grant", "judge.sealed", "judge.unsealed")


def delete(root, mod, ids):
    """Delete on sight (his ruling 2026-11-15 ~10:16 PM PST: "Delete on sight. I really don't think that's going to be
    abused to pass a judge. But we can monitor."): any writer removes a wrong or useless entry, anyone's, physically;
    git history is the archive and `deletions` is the monitor. No event is written. -> [{id, shard, kind, subject}].
    Refused: an id the ledger does not hold, and the fencing bookkeeping (lease.grant, judge.sealed), which the lint's
    stale-token and seal checks stand on."""
    ids = list(ids)
    lk = _lock(root, mod, "append")
    try:
        evs = {e.get("id"): e for e in read(root, mod)}
        for i in ids:
            if i not in evs:
                raise ModLedgerError("no entry %r in %s's ledger" % (i, mod))
            if evs[i].get("kind") in DELETE_REFUSED:
                raise ModLedgerError("%s is a %s, the fencing bookkeeping the lint stands on; it is not deleted"
                                     % (i, evs[i]["kind"]))
        gone = []
        for shard in sorted({evs[i]["_shard"] for i in ids}):
            path = os.path.join(ledger_dir(root, mod), shard + ".jsonl")
            keep = []
            for line in model._read_lines(path):
                try:
                    e = json.loads(line)
                except ValueError:
                    e = None
                if isinstance(e, dict) and e.get("id") in ids:
                    continue
                keep.append(line if line.endswith("\n") else line + "\n")
            if keep:
                tmp = path + ".del%d" % os.getpid()
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.writelines(keep)
                os.replace(tmp, path)
            else:
                os.remove(path)
        for i in ids:
            gone.append({"id": i, "shard": evs[i]["_shard"], "kind": evs[i].get("kind"), "subject": evs[i].get("subject")})
    finally:
        _unlock(lk)
    write_views(root, mod)
    return gone


def _git_text(root, *args):
    r = ledger_lint._git(root, *args)
    if r.returncode != 0:
        raise ModLedgerError("git %s failed: %s" % (" ".join(args[:2]), r.stderr.decode(errors="replace").strip()))
    return r.stdout.decode("utf-8", errors="replace")


def _events_at(root, rev, mod):
    rel_d = os.path.relpath(ledger_dir(root, mod), root)
    out = []
    names = [p for p in _git_text(root, "ls-tree", "--name-only", rev, rel_d + "/").splitlines() if p.endswith(".jsonl")]
    for p in names:
        blob = ledger_lint.blob_at(root, rev, p) or b""
        for l in blob.decode("utf-8", errors="replace").split("\n"):
            try:
                e = json.loads(l)
            except ValueError:
                continue
            if isinstance(e, dict):
                out.append(e)
    return model.canonical_order(out)


def deletions(root, since=None, mod=None):
    """The monitor (his "But we can monitor"): every mod-ledger line deleted in git history, per mod and per writer of
    the deleted entry. `flag` marks what goes on the Conductor's daily digest: a deleted JUDGE or OWNER entry, and any
    deleted finding that was open. The deleter is the commit (git carries no seat; every commit has his git identity),
    so the commit's sha, time and subject are listed, with the shards that commit also wrote. Never a refusal.
    -> {"deleted": [...], "counts": {mod: {writer class: n}}, "flagged": [...]}"""
    spec = ":(glob)design/concepts/%s/ledger/*.jsonl" % (mod or "*")
    args = ["log", "--reverse", "--format=%x1e%H %ct %s", "-p", "--unified=0", "--no-renames"]
    if since:
        args.append("--since=%s" % since)
    text = _git_text(root, *args, "--", spec)
    out, counts = [], {}
    for chunk in text.split("\x1e")[1:]:
        head, _, body = chunk.partition("\n")
        sha, ct, subject = (head.split(" ", 2) + ["", ""])[:3]
        removed, added, wrote, cur = [], set(), set(), None
        for line in body.split("\n"):
            if line.startswith("diff --git "):
                m = re.search(r" b/(design/concepts/([^/]+)/ledger/([^/]+)\.jsonl)$", line)
                cur = (m.group(2), m.group(3)) if m else None
            elif cur and line.startswith("-") and not line.startswith("---"):
                removed.append((cur, line[1:]))
            elif cur and line.startswith("+") and not line.startswith("+++"):
                try:
                    added.add(json.loads(line[1:]).get("id"))
                except (ValueError, AttributeError):
                    pass
                wrote.add(cur[1])
        parent_state = {}
        for (m_, shard), raw in removed:
            try:
                e = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(e, dict) or e.get("id") in added:
                continue              # a line moved or rewritten in the same commit is not a deletion
            was_open = None
            if e.get("kind") == "finding.open":
                if m_ not in parent_state:
                    try:
                        parent_state[m_] = reduce(_events_at(root, sha + "^", m_))
                    except ModLedgerError:
                        parent_state[m_] = None
                f = (parent_state[m_] or {}).get("findings", {}).get(e.get("subject"))
                was_open = None if parent_state[m_] is None else bool(f and f["status"] not in CLOSED["finding"])
            cls = writer_class(shard)
            row = {"mod": m_, "shard": shard, "id": e.get("id"), "kind": e.get("kind"), "subject": e.get("subject"),
                   "was_open": was_open, "commit": sha, "time": int(ct or 0), "commit_subject": subject,
                   "commit_also_wrote": sorted(wrote - {shard}),
                   "flag": cls in ("JUDGE", "OWNER") or bool(was_open)}
            out.append(row)
            counts.setdefault(m_, {})
            counts[m_][cls] = counts[m_].get(cls, 0) + 1
    return {"deleted": out, "counts": counts, "flagged": [r for r in out if r["flag"]]}


# ---- reduce ---------------------------------------------------------------------------------------------------------

def _text(ev):
    return (ev.get("body") or {}).get("text") or ""


CLOSED = {"finding": ("verified", "withdrawn"), "trap": ("cleared",), "q": ("answered", "withdrawn")}


def reduce(events):
    """-> the mod's state now, a pure function of its events. Superseded events and fenced HOLDER events (stale
    tokens) do not count; both are listed."""
    events = [e for e in events if isinstance(e, dict)]
    superseded = sorted({e["supersedes"] for e in events if isinstance(e.get("supersedes"), str)})
    by, current = leases(events)
    st = {"reducer": REDUCER_VERSION, "version": None, "stage": None, "exit_claims": [], "bars": {}, "findings": {},
          "causes": {}, "traps": {}, "questions": {}, "answers": {}, "decisions": {}, "checkpoint": None,
          "session": None,
          "lease": None, "spend_usd": 0.0, "spend_tokens": 0, "tests": [], "notes": [], "superseded": superseded, "fenced": [],
          "events": len(events), "shards": sorted({e.get("_shard") or e.get("writer") for e in events})}
    sup = set(superseded)
    ceiling = config()["holder_context_ceiling_tokens"]
    opened_version = False
    for ev in events:
        if ev.get("id") in sup:
            continue
        w = ev.get("writer") or ""
        if writer_class(w) == "HOLDER":
            why = fenced(ev, by)
            if why:
                st["fenced"].append({"id": ev.get("id"), "why": why})
                continue
        k, s, b = ev.get("kind"), ev.get("subject"), ev.get("body") or {}
        when = ev.get("ts")
        if k == "version.open":
            st["version"] = b.get("version") or ev.get("version")
            opened_version = True
        elif ev.get("version") and not opened_version:
            st["version"] = ev["version"]
        # a line's own version is read beside its kind, never instead of it: in one elif chain every line above a late
        # version.open was skipped (RIMMANDRAKE_FIX_REDUCER_SKIPS_LINES_ABOVE_LATE_VERSION_OPEN)
        if k == "stage.enter":
            st["stage"] = b.get("stage")
        elif k == "stage.accepted":
            st["stage"] = b.get("to")
            st["exit_claims"] = []
        elif k == "stage.exit_claimed":
            st["exit_claims"].append({"by": w, "ts": when, "text": _text(ev), "evidence": ev.get("evidence")})
        elif k == "stage.rejected":
            st["exit_claims"] = [dict(c, rejected=_text(ev)) for c in st["exit_claims"]]
        elif k == "stage.exit_confirmed":
            st["exit_claims"] = [dict(c, confirmed_by=w) for c in st["exit_claims"]]
        elif k and k.startswith("bar."):
            bar = st["bars"].setdefault(s, {"verdict": None})
            bar.update({"status": k.split(".", 1)[1], "text": _text(ev) or bar.get("text"), "ts": when})
        elif k in ("test.run", "live.run"):
            st["tests"].append({"ts": when, "kind": k, "subject": s, "result": b.get("result"), "sha":
                                ev.get("code_sha"), "text": _text(ev), "by": w})
            if isinstance(b.get("bar"), str) and b["bar"]:
                st["bars"].setdefault("bar:" + b["bar"], {"verdict": None})["verdict"] = b.get("result")
        elif k == "finding.open":
            st["findings"][s] = {"status": "open", "text": _text(ev), "proposed_fix": b.get("proposed_fix"),
                                 "accept": b.get("accept"), "class": b.get("class"), "bars": b.get("bars") or [],
                                 "tags": b.get("tags") or [], "by": w, "ts": when, "claim": None, "code_sha": None,
                                 "version": ev.get("version")}
        elif k and k.startswith("finding.") and s in st["findings"]:
            f = st["findings"][s]
            f["status"] = {"finding.claimed_fixed": "claimed_fixed", "finding.disputed": "disputed",
                           "finding.verified": "verified", "finding.reopened": "open",
                           "finding.withdrawn": "withdrawn"}.get(k, f["status"])
            f["ts"] = when
            f["version"] = ev.get("version")
            if ev.get("code_sha"):
                f["code_sha"] = ev["code_sha"]
            if k == "finding.withdrawn":
                f["how_checked"] = b.get("how_checked")
                f["claim"] = _text(ev)
            if k in ("finding.claimed_fixed", "finding.disputed"):
                f["claim"] = _text(ev)
            if k == "finding.reopened" and _text(ev):
                f["text"] = "%s (reopened: %s)" % (f["text"], _text(ev))
        elif k in ("trap.noted", "trap.cleared"):
            st["traps"][s] = {"status": k.split(".", 1)[1], "text": _text(ev), "where": b.get("where"), "ts": when,
                              "by": w, "version": ev.get("version")}
        elif k == "cause.tried":
            st["causes"][s] = {"status": "tried", "text": _text(ev), "ts": when}
        elif k == "cause.refuted":
            st["causes"][s] = {"status": "refuted", "text": _text(ev), "ts": when, "code_sha": ev.get("code_sha"),
                               "depends_on": b.get("depends_on") or []}
        elif k == "cause.reopened":
            st["causes"][s] = {"status": "tried", "text": _text(ev), "ts": when}
        elif k == "question.ask":
            st["questions"][s] = {"status": "open", "text": _text(ev), "obvious": b.get("obvious"),
                                  "against": b.get("against"), "ts": when, "by": w}
        elif k == "question.answer":
            q = st["questions"].setdefault(s, {"text": b.get("question") or "", "ts": when})
            q.update({"status": "answered", "answer": _body_text(ev), "version": ev.get("version")})
            st["answers"][s] = {"question": q.get("text"), "answer": _body_text(ev), "ts": when,
                                "authority": ev.get("authority")}
        elif k == "question.withdrawn" and s in st["questions"]:
            st["questions"][s].update({"status": "withdrawn", "version": ev.get("version")})
        elif k == "decision":
            st["decisions"][s] = {"text": _body_text(ev), "by": w, "ts": when, "authority": ev.get("authority")}
            auth = ev.get("authority") or {}
            if w == "OWNER" or auth.get("owner_said") or auth.get("by_card"):
                st["answers"]["decision:" + s] = {"question": None, "answer": _body_text(ev), "ts": when,
                                                  "authority": ev.get("authority")}
        elif k == "session.id":
            ctx = b.get("context_tokens")
            st["session"] = {"session_id": b.get("session_id"), "context_tokens": ctx, "ceiling": ceiling,
                             "rotate_due": isinstance(ctx, int) and ctx >= ceiling, "ts": when}
        elif k == "session.checkpoint":
            st["checkpoint"] = {"ts": when, "by": w, "done": b.get("done") or _text(ev), "next": b.get("next"),
                                "ruled_out": b.get("ruled_out")}
        elif k == "spend":
            usd = b.get("usd")
            if isinstance(usd, (int, float)) and not isinstance(usd, bool):
                st["spend_usd"] = round(st["spend_usd"] + usd, 4)
            if isinstance(b.get("tokens"), int) and not isinstance(b.get("tokens"), bool):
                st["spend_tokens"] += b["tokens"]
        elif k == "note":
            st["notes"].append({"ts": when, "by": w, "subject": s, "text": _text(ev)})
    if current:
        g = by[current]
        st["lease"] = {"lease": current, "token": g["token"], "last": g["last"], "released": g["released"]}
    return st


# ---- packet ---------------------------------------------------------------------------------------------------------

def _one(text, where=None):
    """One line. With `where` (the command that prints the whole event), a text past the configured packet_line_chars
    is clipped with fulltext.clip, which says it is cut and where the rest is; the ledger keeps it whole."""
    t = " ".join(str(text or "").split())
    if where:
        try:
            from . import fulltext
        except ImportError:
            import fulltext  # noqa: E402
        t = fulltext.clip(t, config()["packet_line_chars"], where)
    return t


def cursor_of(events):
    """-> the packet's cursor: the latest (ts, tsn) it read, `t=<ts>.<tsn>`. A time, not shard offsets: delete on
    sight shifts offsets and line numbers, never a time. `since` takes it back."""
    if not events:
        return "t=0"
    ts_, tsn = max(_when(e) for e in events)
    return "t=%s.%d" % (ts_, tsn)


def packet_from(mod, events, budget=None, stale=None):
    """-> (text, info). The bounded read a holder starts from (spec §3.3, the standard §3). Never dropped: the open
    findings with their proposed fixes and accept commands, the live traps, the refuted causes, his answers, the open
    questions, the bars, the holder's last checkpoint (a finding claimed fixed prints its claim and accept, not its spent fix). Closed subjects are one line each and are dropped oldest-first
    when over budget, then decisions, causes tried, tests; notes are never printed (they are searchable). `stale(cause)`
    (the CLI passes a git check; views pass none, they are pure) moves a refuted cause whose files changed since its
    code_sha under "Causes stale". Ends with what it left out, then the cursor `since` reads."""
    budget = budget or config()["packet_budget_tokens"]
    st = reduce(events)

    def cl(text, subject):
        return _one(text, "modledger.py show --mod %s %s" % (mod, subject))

    keep = ["# %s — mod ledger packet" % mod,
            "version %s · stage %s · %d events in %d shards · reducer %d"
            % (st["version"] or "unknown", st["stage"] if st["stage"] is not None else "unknown", st["events"],
               len(st["shards"]), REDUCER_VERSION)]
    if not events:
        keep.append("This mod's ledger holds no events yet (no events).")
    if st["lease"]:
        L = st["lease"]
        keep.append("holder lease %s, token %d, last active %s%s" % (L["lease"], L["token"], L["last"],
                                                                    ", released" if L["released"] else ""))
    if st["session"]:
        S = st["session"]
        keep.append("holder session %s, context %s of ceiling %d%s" % (S["session_id"], S["context_tokens"],
                                                                      S["ceiling"], " — ROTATE DUE" if
                                                                      S["rotate_due"] else ""))
    for c in st["exit_claims"]:
        keep.append("exit claimed by %s at %s: %s%s" % (c["by"], c["ts"], cl(c["text"], "stage"),
                                                        " (confirmed by %s)" % c["confirmed_by"]
                                                        if c.get("confirmed_by") else ""))
    if st["checkpoint"]:
        C = st["checkpoint"]
        keep += ["", "## Last checkpoint (%s, %s)" % (C["by"], C["ts"]), "- done: " + cl(C["done"], "session"),
                 "- next: " + cl(C["next"], "session"), "- ruled out: " + cl(C["ruled_out"], "session")]
    opened = sorted(((k, f) for k, f in st["findings"].items() if f["status"] not in CLOSED["finding"]),
                    key=lambda t: t[1]["ts"])
    n_open = sum(1 for _, f in opened if f["status"] != "claimed_fixed")
    n_claimed = len(opened) - n_open

    def cut(text, n):
        t = " ".join(str(text or "").split())
        return t if len(t) <= n else t[:n - 1].rstrip() + "…"

    def findings_block(lv, K):
        """The line rule (spec §3.3: never drop an open finding). lv 0: every finding whole. lv 1: a claimed fix (its fix
        spent, a judge's work) on one line with its claim; lv 2: its name and sha only. lv >= 3: the K oldest open
        findings also on one line, text cut to 120 (60 at lv 5, none at lv 12: name, status, class and bars), their
        fix and accept one `show` away."""
        out, briefed = ["", "## Open findings (%d)" % len(opened)], 0
        if lv >= 1 and n_claimed:
            out.append("(claimed fixes, awaiting a judge, on one line each%s, named without their 'finding:': "
                       "`modledger.py show --mod %s finding:<NAME>`)"
                       % (" with the oldest %d open findings" % min(K, n_open) if lv >= 3 and K else "", mod))
        for k, f in opened:
            nm = k[len("finding:"):] if k.startswith("finding:") else k
            sha = (" on %s" % f["code_sha"]) if f.get("code_sha") else ""
            tags = "%s%s" % ((", " + f["class"]) if f.get("class") else "",
                             (" · bars " + ", ".join(f["bars"])) if f.get("bars") else "")
            if f["status"] == "claimed_fixed" and lv >= 1:
                out.append("- %s%s" % (nm, sha) + (": " + cut(f.get("claim") or f["text"], 100) if lv == 1 else ""))
                continue
            if f["status"] != "claimed_fixed" and lv >= 3 and briefed < K:
                briefed += 1
                out.append("- %s [%s%s]" % (nm, f["status"], tags) if lv >= 12 else
                           "- %s [%s%s]: %s" % (nm, f["status"], tags, cut(f["text"], 60 if lv >= 5 else 120)))
                continue
            out.append("- %s [%s%s] by %s, %s%s: %s" % (k, f["status"], (", " + f["class"]) if f.get("class") else "",
                                                         f["by"], f["ts"], (" · bars " + ", ".join(f["bars"]))
                                                         if f.get("bars") else "", cl(f["text"], k)))
            if f["status"] != "claimed_fixed":     # claimed done: the fix is spent; `show` keeps it, the packet shows
                out.append("  proposed fix: " + cl(f["proposed_fix"], k))      # the claim and the accept a judge runs
            if f.get("accept"):
                out.append("  accept: " + cl(f["accept"], k))
            if f.get("claim"):
                out.append("  holder: " + cl(f["claim"], k) + ((" (%s)" % f["code_sha"]) if f.get("code_sha") else ""))
        return out, briefed

    keep.append(("FINDINGS",))
    traps = sorted(((k, t) for k, t in st["traps"].items() if t["status"] != "cleared"), key=lambda x: x[1]["ts"])
    keep.append(("TRAPS",))
    refuted = sorted(((k, c) for k, c in st["causes"].items() if c["status"] == "refuted"), key=lambda t: t[1]["ts"])
    is_stale = {k for k, c in refuted if stale and stale(c)}

    def cause_line(k, c, lv=0):
        on = ", ".join(x for x in [("on %s" % c["code_sha"]) if c.get("code_sha") else "",
                                    ("depends on %s" % ", ".join(c["depends_on"])) if c.get("depends_on") and lv < 7
                                    else ""] if x)
        return "- %s: %s%s" % (k, cut(c["text"], 160 if lv == 7 else 80) if lv >= 7 else cl(c["text"], k),
                               (" (%s)" % on) if on else "")

    trap_item = {}
    for e in events:
        if e.get("kind") == "trap.noted":
            it = [r[5:] for r in e.get("evidence") or [] if isinstance(r, str) and r.startswith("item:")]
            trap_item[e.get("subject")] = it[0] if it else None

    def trap_on(k):
        """-> the status of the finding a trap was mined from (its item: ref), or None."""
        it = trap_item.get(k)
        return (st["findings"].get("finding:" + it) or {}).get("status") if it else None

    def traps_block(lv):
        """The live traps and refuted causes, every one; past everything else at its briefest (lv 7, 8) each text is
        cut (traps to 120 then 60 chars, causes to 160 then 80), the subject and where always kept. Past that (lv 9,
        10) the traps mined from a verified or withdrawn finding, then from a claimed-fixed one, are counted on one line
        with the search that lists them; at lv 11 the traps left print their subject only."""
        n = 60 if lv >= 8 else 120
        folded = ("verified", "withdrawn") + (("claimed_fixed",) if lv >= 10 else ()) if lv >= 9 else ()
        shown = [(k, t) for k, t in traps if trap_on(k) not in folded]
        out = ["", "## Traps (%d) — what a reader would otherwise get wrong%s" % (
            len(traps), (" (each cut to %d chars; `modledger.py show --mod %s <subject>` for the whole)" % (n, mod))
            if lv >= 7 and traps else "")]
        out += ["- %s" % k if lv >= 11 else
                "- %s (%s): %s" % (k, t.get("where") or "?", cut(t["text"], n) if lv >= 7 else cl(t["text"], k))
                for k, t in shown]
        if len(shown) < len(traps):
            out.append("- %d traps on closed or claimed findings (%s), not listed: `modledger.py find --mod %s --class "
                       "trap <words>`" % (len(traps) - len(shown), ", ".join(x for x in folded), mod))
        out += ["", "## Causes refuted (%d) — do not chase these again" % (len(refuted) - len(is_stale))]
        out += [cause_line(k, c, lv) for k, c in refuted if k not in is_stale]
        if is_stale:
            out += ["", "## Causes stale (%d) — refuted on an older commit; their files changed since: re-check"
                    % len(is_stale)]
            out += [cause_line(k, c, lv) for k, c in refuted if k in is_stale]
        return out
    def answers_block(lv):
        """His answers, every one; at lv >= 4 each cut to 160 chars (100 at lv 6), a decision named without its
        'decision:' (the ledger keeps his words whole)."""
        n = 100 if lv >= 6 else 160
        out = ["", "## His answers (%d)%s" % (len(st["answers"]), " (each cut to %d chars, a decision named without "
                                              "its 'decision:': `modledger.py show`)" % n if lv >= 4 else "")]
        for k, a in sorted(st["answers"].items(), key=lambda t: t[1]["ts"]):
            name = k[len("decision:"):] if lv >= 4 and k.startswith("decision:") else k
            out.append("- %s%s: %s" % (name, (" (Q: %s)" % cl(a["question"], k)) if a.get("question") else "",
                                       cut(a["answer"], n) if lv >= 4 else cl(a["answer"], k)))
        return out

    keep.append(("ANSWERS",))
    openq = [(k, q) for k, q in st["questions"].items() if q.get("status") == "open"]
    keep += ["", "## Open questions (%d)" % len(openq)]
    for k, q in openq:
        keep.append("- %s: %s (obvious answer: %s; against it: %s)" % (k, cl(q["text"], k), cl(q.get("obvious"), k),
                                                                      cl(q.get("against"), k)))
    def bars_block(lv):
        """Every bar; at lv >= 4 its text cut to 60 chars, at lv 13 its id, status and verdict only (when that is
        shorter: the level never grows the packet)."""
        def one(ids):
            out = ["", "## Bars (%d)%s" % (len(st["bars"]), " (ids only: `modledger.py show --mod %s <bar>` for the "
                                           "text)" % mod if ids else "")]
            for k, b in sorted(st["bars"].items()):
                out.append("- %s [%s] verdict %s%s" % (k, b.get("status") or "?", b.get("verdict") or "none",
                                                      (": " + (cut(b["text"], 60) if lv >= 4 else cl(b["text"], k)))
                                                      if b.get("text") and not ids else ""))
            return out
        cuts = one(False)
        if lv < 13:
            return cuts
        ids = one(True)
        return ids if tokens("\n".join(ids)) < tokens("\n".join(cuts)) else cuts

    keep.append(("BARS",))
    keep.append("")
    keep.append("spend recorded: USD %.2f, %d tokens" % (st["spend_usd"], st["spend_tokens"]))
    # droppable material: (ts, group, line)
    drop = []
    for k, f in st["findings"].items():
        if f["status"] in CLOSED["finding"]:
            drop.append((f["ts"], "closed findings", "- %s %s%s%s" % (
                k, f["status"], (" (%s)" % f["how_checked"]) if f.get("how_checked") else "",
                (" " + f["code_sha"]) if f.get("code_sha") else "")))
    for k, t in st["traps"].items():
        if t["status"] == "cleared":
            drop.append((t["ts"], "closed traps", "- %s cleared" % k))
    for k, d in st["decisions"].items():
        if "decision:" + k not in st["answers"]:          # his words are printed once, under his answers
            drop.append((d["ts"], "decisions", "- %s (%s, %s): %s" % (k, d["by"], d["ts"], cl(d["text"], k))))
    for k, c in st["causes"].items():
        if c["status"] == "tried":
            drop.append((c["ts"], "causes tried", "- %s: %s" % (k, cl(c["text"], k))))
    for t in st["tests"]:
        drop.append((t["ts"], "tests", "- %s %s %s: %s%s %s" % (t["ts"], t["kind"], t["subject"], t["result"],
                                                                (" on " + t["sha"]) if t.get("sha") else "",
                                                                cl(t["text"], t["subject"]))))
    drop.sort(key=lambda t: (t[0] or "", t[1], t[2]))
    groups = ("decisions", "closed findings", "closed traps", "causes tried", "tests")
    cursor = cursor_of(events)

    def render(k, lv=0, K=0):
        kept, gone = drop[k:], {}
        for _, g, _l in drop[:k]:
            gone[g] = gone.get(g, 0) + 1
        out, briefed = [], 0
        for x in keep:
            if x == ("FINDINGS",):
                lines, briefed = findings_block(lv, K)
                out += lines
            elif x == ("TRAPS",):
                out += traps_block(lv)
            elif x == ("ANSWERS",):
                out += answers_block(lv)
            elif x == ("BARS",):
                out += bars_block(lv)
            else:
                out.append(x)
        for g in groups:
            lines = [l for _, gg, l in kept if gg == g]
            if lines:
                out += ["", "## %s (%d%s)" % (g[0].upper() + g[1:], len(lines),
                                              ", %d older left out" % gone[g] if gone.get(g) else "")] + lines
        out += ["", "## Left out"]
        for g in groups:
            if gone.get(g):
                out.append("- %s: %d, oldest first (`modledger.py show --mod %s <subject>`)" % (g, gone[g], mod))
        if lv >= 1 and n_claimed:
            out.append("- claimed fixes in brief: %d on one line (%s), their claim, test and fix by `show`"
                       % (n_claimed, "name, sha, claim" if lv == 1 else "name and sha"))
        if briefed:
            out.append("- open findings in brief: the oldest %d on one line, their fix and accept by `modledger.py show "
                       "--mod %s <subject>`" % (briefed, mod))
        if lv >= 4:
            out.append("- his answers and the bars' texts in brief (cut at %d and 60 chars)" % (100 if lv >= 6 else 160))
        if lv >= 7 and (traps or refuted):
            out.append("- traps and refuted causes in brief (texts cut at %s chars)%s" % (
                "60 and 80" if lv >= 8 else "120 and 160", "; traps on closed findings counted, not listed" if lv >= 9
                else ""))
        if st["notes"]:
            out.append("- notes: %d, never printed here (`modledger.py find --mod %s <words>`)" % (len(st["notes"]), mod))
        if st["superseded"] or st["fenced"]:
            out.append("- superseded events: %d; fenced holder events (stale tokens): %d"
                       % (len(st["superseded"]), len(st["fenced"])))
        out.append("- the full history: %d events (views/history.md; never read whole)" % len(events))
        out += ["", "cursor: %s (modledger.py since --mod %s %s prints what changed after this packet)"
                % (cursor, mod, cursor)]
        return "\n".join(out) + "\n", gone

    def fewest(f, n):
        """The least x in 0..n with f(x) within budget (f shrinks as x grows), or None."""
        if tokens(f(n)[0]) > budget:
            return None
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if tokens(f(mid)[0]) <= budget:
                hi = mid
            else:
                lo = mid + 1
        return lo

    text, gone = render(0)
    if tokens(text) > budget:
        k = fewest(render, len(drop))                     # the fewest dropped closed lines that fit
        if k is not None:
            text, gone = render(k)
        else:                                             # all closed material gone: the line rule, never a drop
            k, done = len(drop), False
            for lv in (1, 2):
                text, gone = render(k, lv)
                if tokens(text) <= budget:
                    done = True
                    break
            for lv in (3, 4, 5, 6) if not done else ():
                K = fewest(lambda x: render(k, lv, x), n_open)
                if K is not None:
                    text, gone = render(k, lv, K)
                    break
            else:
                if not done:
                    # last: the traps' and causes' texts in brief, then counted; then the open findings by name
                    # (FlowWorks' 246 open findings held its packet at 14,694 tokens at lv 11, 2026-11-16), then bar ids
                    for lv in (6, 7, 8, 9, 10, 11, 12, 13):
                        text, gone = render(k, lv, n_open)
                        if tokens(text) <= budget:
                            break
    over = tokens(text) > budget
    if over:
        text = ("OVER BUDGET: %d tokens > %d, and nothing droppable is left (open findings, traps, refuted causes, his "
                "answers, open questions and bars are never dropped; the line rule is at its briefest)\n"
                % (tokens(text), budget)) + text
    return text, {"tokens": tokens(text), "budget": budget, "dropped": gone, "over_budget": over,
                  "events": len(events), "cursor": cursor}


def stale_check(root):
    """-> stale(cause): True when a file the refuted cause depends on changed in git after the commit it was refuted
    on. A cause with no code_sha or no paths, or a sha git does not know, is not called stale (unmeasured, not
    guessed)."""
    def stale(c):
        sha, paths = c.get("code_sha"), c.get("depends_on") or []
        if not sha or not paths:
            return False
        r = ledger_lint._git(root, "log", "--format=%H", "-1", "%s..HEAD" % sha, "--", *paths)
        return r.returncode == 0 and bool(r.stdout.strip())
    return stale


def designer_step_line(root, mod):
    """-> the `Designer step: ...` text for design/concepts/<Mod>/stage.json, the Designer stage machine's own state
    (a different thing from the pipeline stage the ledger holds). Four answers: `<0-5> (<status>)` plus `, blocked on
    <text>`; `none (no stage.json)`; `UNMEASURED (<cause>)`."""
    path = os.path.join(root, "design", "concepts", mod, "stage.json")
    if not os.path.exists(path):
        return "none (no stage.json)"
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        return "UNMEASURED (stage.json unreadable: %s)" % _one(str(e))
    if not isinstance(d, dict):
        return "UNMEASURED (stage.json is not an object)"
    step = d.get("stage")
    if isinstance(step, bool) or not isinstance(step, int) or not 0 <= step <= 5:
        return "UNMEASURED (stage.json has no step 0-5: %r)" % (step,)
    line = "%d (%s)" % (step, d.get("status", "no status"))
    if d.get("status") == "blocked" and d.get("blocked_on"):
        line += ", blocked on " + _one(str(d["blocked_on"]))
    return line


def packet(root, mod, budget=None, stale=None):
    """packet_from plus the Designer-step line under its head; the line is charged to the budget, so `tokens` and
    `over_budget` describe the text returned."""
    line = "Designer step: " + designer_step_line(root, mod) + "\n"
    cost = tokens(line)
    text, info = packet_from(mod, read(root, mod), (budget or config()["packet_budget_tokens"]) - cost, stale)
    head, _, rest = text.partition("\n")
    second, _, rest2 = rest.partition("\n")
    info["tokens"] += cost
    return head + "\n" + second + "\n" + line + rest2, info


# ---- views ----------------------------------------------------------------------------------------------------------

def _offsets(root, mod):
    return {s: len(_shard_bytes(root, mod, s)) for s in shard_names(root, mod)}


def _header(mod, offsets, body):
    return ("<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod %s)"
            " reducer=%d shards=%s body_sha256=%s -->\n"
            % (mod, REDUCER_VERSION, _canon(offsets), hashlib.sha256(body.encode("utf-8")).hexdigest()))


def render_views(root, mod):
    """-> {view name: full text}. A pure function of the shards: no clock, no git."""
    events = read(root, mod)
    offs = _offsets(root, mod)
    state_md = packet_from(mod, events)[0]
    hist = ["# %s — mod ledger history (%d events, merged across shards)" % (mod, len(events)), ""]
    for e in events:
        hist.append("- %s %s#%d %s %s v%s: %s" % (e.get("ts"), e["_shard"], e["_seq"], e.get("kind"),
                                                  e.get("subject"), e.get("version"), _one(_text(e))))
    hist_md = "\n".join(hist) + "\n"
    st = reduce(events)
    sj = json.dumps(st, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    out = {"state.md": _header(mod, offs, state_md) + state_md,
           "history.md": _header(mod, offs, hist_md) + hist_md,
           "state.json": json.dumps({"_view": {"reducer": REDUCER_VERSION, "shards": offs,
                                               "body_sha256": hashlib.sha256(sj.encode("utf-8")).hexdigest()},
                                     "state": st}, indent=1, sort_keys=True, ensure_ascii=False) + "\n"}
    for v, text in closed_views(mod, st, events).items():
        out["closed_%s.md" % v] = _header(mod, offs, text) + text
    return out


def closed_views(mod, st, events):
    """-> {version: text}: per Design Version opened, one line per subject closed in it (a finding verified or
    withdrawn, a trap cleared, a question answered or withdrawn), its final status and sha. A snapshot: it removes
    nothing, and `show` still prints each subject's trail (standard §3)."""
    versions = []
    for e in events:
        if e.get("kind") == "version.open":
            v = (e.get("body") or {}).get("version") or e.get("version")
            if isinstance(v, str) and re.match(r"^[0-9A-Za-z.+-]{1,40}$", v) and v not in versions:
                versions.append(v)
    out = {}
    for v in versions:
        rows = []
        for k, f in st["findings"].items():
            if f["status"] in CLOSED["finding"] and f.get("version") == v:
                rows.append((f["ts"], "- %s %s%s (%s)" % (k, f["status"], (" " + f["code_sha"]) if f.get("code_sha")
                                                          else "", f["ts"])))
        for k, t in st["traps"].items():
            if t["status"] == "cleared" and t.get("version") == v:
                rows.append((t["ts"], "- %s cleared (%s)" % (k, t["ts"])))
        for k, q in st["questions"].items():
            if q.get("status") in CLOSED["q"] and q.get("version") == v:
                rows.append((q.get("ts") or "", "- %s %s" % (k, q["status"])))
        rows.sort()
        out[v] = "\n".join(["# %s — closed in Design Version %s (%d)" % (mod, v, len(rows)), ""] +
                           [r for _, r in rows]) + "\n"
    return out


def write_views(root, mod):
    """Regenerate every view under one lock, reading the shards inside it (so the last writer saw every append)."""
    if not shard_names(root, mod):
        return []
    lk = _lock(root, mod, "views")
    try:
        d = views_dir(root, mod)
        os.makedirs(d, exist_ok=True)
        out = []
        for name, text in render_views(root, mod).items():
            p = os.path.join(d, name)
            tmp = p + ".tmp%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp, p)
            out.append(p)
        return out
    finally:
        _unlock(lk)


def _view_meta(name, text):
    """-> (recorded meta, body as written) or (None, None) when the view's header is unreadable."""
    try:
        if name.endswith(".json"):
            obj = json.loads(text)
            body = json.dumps(obj["state"], indent=1, sort_keys=True, ensure_ascii=False) + "\n"
            return obj["_view"], body
        first, body = text.split("\n", 1)
        m = re.search(r"reducer=(\d+) shards=(\{.*?\}) body_sha256=([0-9a-f]{64})", first)
        return {"reducer": int(m.group(1)), "shards": json.loads(m.group(2)), "body_sha256": m.group(3)}, body
    except (ValueError, KeyError, AttributeError, TypeError):
        return None, None


# ---- the search index (generated, disposable) -----------------------------------------------------------------------

def index_path(root, mod):
    """A program reads it, so /tmp, never the repo; one folder per root, so the clones never share an index."""
    _check_mod(mod)
    tag = hashlib.sha256(os.path.abspath(root).encode("utf-8")).hexdigest()[:12]
    return os.path.join("/tmp", "modledger-index", tag, mod + ".sqlite")


def _status_of(st, subject):
    cls = subject_class(subject)
    table = {"finding": st["findings"], "cause": st["causes"], "trap": st["traps"], "q": st["questions"],
             "bar": st["bars"]}.get(cls)
    if table is None or subject not in table:
        return "decided" if subject in st["decisions"] else None
    return table[subject].get("status")


def index(root, mod):
    """(Re)build the mod's index when the shards' offsets or the reducer differ from the ones it was built from.
    -> its path. Tables: ev (one row per event), subj (the reducer's state per subject), fts (FTS5 over subject, text,
    fix, said, evidence, content='ev'). Deleting it loses nothing."""
    path = index_path(root, mod)
    stamp = _canon({"offsets": _offsets(root, mod), "reducer": REDUCER_VERSION, "index": INDEX_VERSION})
    if os.path.exists(path):
        try:
            con = sqlite3.connect(path)
            try:
                if con.execute("SELECT v FROM meta WHERE k='stamp'").fetchone()[0] == stamp:
                    return path
            finally:
                con.close()
        except (sqlite3.Error, TypeError):
            pass
    events = read(root, mod)
    st = reduce(events)
    sup = set(st["superseded"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp%d" % os.getpid()
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    try:
        con.executescript("""
            CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT);
            CREATE TABLE ev(rowid INTEGER PRIMARY KEY, id TEXT, shard TEXT, seq INTEGER, ts TEXT, tsn INTEGER,
                writer TEXT, kind TEXT, subject TEXT, class TEXT, bars TEXT, tags TEXT, code_sha TEXT, authority TEXT,
                text TEXT, fix TEXT, accept TEXT, said TEXT, evidence TEXT, where_ TEXT, supersedes TEXT,
                superseded_by TEXT);
            CREATE TABLE subj(subject TEXT PRIMARY KEY, class TEXT, status TEXT, last_ts TEXT, last_id TEXT, bars TEXT);
            CREATE VIRTUAL TABLE fts USING fts5(subject, text, fix, said, evidence, content='ev', content_rowid='rowid');
        """)
        by_sup = {e["supersedes"]: e.get("id") for e in events if isinstance(e.get("supersedes"), str)}
        rows = []
        for i, e in enumerate(events, 1):
            b = e.get("body") if isinstance(e.get("body"), dict) else {}
            s_ = e.get("subject") if isinstance(e.get("subject"), str) else ""
            rows.append((i, e.get("id"), e["_shard"], e["_seq"], e.get("ts"), _when(e)[1], e.get("writer"),
                         e.get("kind"), s_, subject_class(s_), _canon(b.get("bars") or []),
                         _canon(b.get("tags") or []), e.get("code_sha"), _canon(e.get("authority") or {}),
                         str(b.get("text") or b.get("done") or ""), str(b.get("proposed_fix") or ""),
                         str(b.get("accept") or ""), str(b.get("said") or ""), " ".join(map(str, e.get("evidence")
                                                                                          or [])),
                         str(b.get("where") or ""), e.get("supersedes"), by_sup.get(e.get("id"))))
        con.executemany("INSERT INTO ev VALUES (%s)" % ",".join("?" * 22), rows)
        last = {}
        for e in events:
            if e.get("id") not in sup and isinstance(e.get("subject"), str):
                last[e["subject"]] = e
        con.executemany("INSERT INTO subj VALUES (?,?,?,?,?,?)", [
            (s_, subject_class(s_), _status_of(st, s_), e.get("ts"), e.get("id"),
             _canon((st["findings"].get(s_) or {}).get("bars") or [])) for s_, e in last.items()])
        con.execute("INSERT INTO fts(fts) VALUES('rebuild')")
        con.execute("INSERT INTO meta VALUES ('stamp', ?)", (stamp,))
        con.commit()
    finally:
        con.close()
    os.replace(tmp, path)
    return path


def _closed(cls, status):
    return status in CLOSED.get(cls, ())


def find(root, mod, query=None, cls=None, kind=None, his=False, path=None, all_=False, limit=None):
    """-> [{subject, status, kind, id, writer, text, said, authority, where}], best match first, one row per subject
    (its best-ranked event). `query` is plain words (FTS5 syntax in it is quoted away); `his` keeps OWNER events and
    events carrying his words or card; `path` keeps traps whose `where` or evidence is under that path; closed subjects
    (verified, withdrawn, cleared, answered) only with `all_` or `his`. No query and no filter returns nothing."""
    limit = limit or std()["find_limit"]
    q = _fts_query(query or "")
    if not q and not path and not his and not kind:
        return []
    con = sqlite3.connect(index(root, mod))
    try:
        if q:
            rows = con.execute("SELECT ev.*, bm25(fts) FROM fts JOIN ev ON ev.rowid = fts.rowid WHERE fts MATCH ? "
                               "ORDER BY bm25(fts)", (q,)).fetchall()
        else:
            rows = con.execute("SELECT ev.*, 0 FROM ev ORDER BY ts DESC, tsn DESC").fetchall()
        cols = [d[0] for d in con.execute("SELECT * FROM ev LIMIT 0").description] + ["rank"]
        status = dict(con.execute("SELECT subject, status FROM subj").fetchall())
    finally:
        con.close()
    out, seen = [], set()
    for row in rows:
        r = dict(zip(cols, row))
        if r["superseded_by"]:
            continue
        if cls and r["class"] != cls:
            continue
        if kind and r["kind"] != kind:
            continue
        auth = json.loads(r["authority"] or "{}")
        if his and not (writer_class(r["writer"] or "") == "OWNER" or auth.get("owner_said") or auth.get("by_card")):
            continue
        if path and not (path in (r["where_"] or "") or path in (r["evidence"] or "")):
            continue
        if path and r["class"] == "trap" and r["kind"] != "trap.noted":
            continue
        st_ = status.get(r["subject"])
        if not (all_ or his) and _closed(r["class"], st_):
            continue
        if r["subject"] in seen:
            continue
        seen.add(r["subject"])
        out.append({"mod": mod, "subject": r["subject"], "status": st_, "kind": r["kind"], "id": r["id"],
                    "writer": r["writer"], "ts": r["ts"], "text": r["text"], "said": r["said"] or None,
                    "authority": auth or None, "where": r["where_"] or None})
        if len(out) >= limit:
            break
    return out


def open_findings(root, mod, bar=None):
    """-> the open and claimed-fixed findings (on `bar`, when named), with proposed fix and accept."""
    st = reduce(read(root, mod))
    out = []
    for k, f in sorted(st["findings"].items(), key=lambda t: t[1]["ts"]):
        if f["status"] in CLOSED["finding"] or (bar and bar not in (f.get("bars") or [])):
            continue
        out.append({"mod": mod, "subject": k, "status": f["status"], "class": f.get("class"), "bars": f.get("bars"),
                    "text": f["text"], "proposed_fix": f.get("proposed_fix"), "accept": f.get("accept"),
                    "claim": f.get("claim"), "code_sha": f.get("code_sha")})
    return out


def _parse_cursor(root, mod, cursor, events):
    c = str(cursor or "").strip()
    m = re.match(r"^t=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\.(\d+)$", c)
    if m:
        return (m.group(1), int(m.group(2)))
    if c == "t=0":
        return ("", 0)
    if re.match(r"^\d{4}-\d\d-\d\d(T\d\d:\d\d:\d\dZ)?$", c):
        return (c if "T" in c else c + "T00:00:00Z", -1)
    for e in events:
        if e.get("id") == c:
            return _when(e)
    raise ModLedgerError("cursor %r is not t=<ts>.<tsn> (the packet's last line), an event id of this mod, or a time "
                         "(2026-11-15 or 2026-11-15T20:00:00Z)" % c)


def since(root, mod, cursor):
    """-> [{subject, status, kinds, last_ts}]: the subjects whose state moved after the cursor (notes and spend are not
    a change of state), in the order they last moved. A cursor is a time, so an entry another clone wrote before it and
    published after it is not listed (`show` has it)."""
    events = read(root, mod)
    at = _parse_cursor(root, mod, cursor, events)
    st = reduce(events)
    moved = {}
    for e in events:
        if _when(e) <= at or e.get("kind") in ("note", "spend") or not isinstance(e.get("subject"), str):
            continue
        m = moved.setdefault(e["subject"], {"mod": mod, "subject": e["subject"], "kinds": [], "last_ts": None})
        m["kinds"].append(e.get("kind"))
        m["last_ts"] = e.get("ts")
        m["status"] = _status_of(st, e["subject"]) or e.get("kind")
    return sorted(moved.values(), key=lambda m: m["last_ts"] or "")


# ---- resume (Option B) ----------------------------------------------------------------------------------------------
#
# Item RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME (spec §3.4; his card 2026-11-15: "Resumed session per
# mod" and "Try 400k first."). The holder's resumable session is its last `session.id`; the dispatcher resumes it while
# its recorded context is under holder_context_ceiling_tokens, rotates (a fresh holder from the packet) at or past it,
# and after a killed or lost run has the holder reconcile its clone, unpublished commits and the bridge first. A
# version.open does not end the holder: the session carries into the next Design Version.

RECONCILE_STATUSES = ("killed", "lost")
UNMEASURED = "UNMEASURED"


def resume_plan(root, mod, events=None):
    """-> {"action": "packet"|"resume"|"rotate", "session_id", "reconcile", "why", "context_tokens", "ceiling"}. The
    ceiling is read from modledger.json at call time. session_id is the session to resume (None unless "resume")."""
    events = read(root, mod) if events is None else events
    st = reduce(events)
    ceiling = config()["holder_context_ceiling_tokens"]
    ends = [e for e in events if e.get("writer") == "DISPATCH" and e.get("kind") == "run.end"]
    last_end = (ends[-1].get("body") or {}) if ends else {}
    reconcile = str(last_end.get("status") or "").lower().startswith(RECONCILE_STATUSES)     # "killed: ..." too
    S = st.get("session") or {}
    sid, ctx = S.get("session_id"), S.get("context_tokens")
    out = {"session_id": None, "reconcile": reconcile, "context_tokens": ctx, "ceiling": ceiling}
    rec = ("; the last run %s was %s: reconcile the clone, unpublished commits and the bridge first" % (
        last_end.get("run") or "?", last_end.get("status"))) if reconcile else ""
    if not isinstance(sid, str) or not sid:
        out.update(action="packet", why="no holder session recorded: start from the packet" + rec)
    elif isinstance(ctx, int) and not isinstance(ctx, bool) and ctx >= ceiling:
        out.update(action="rotate", rotated_from=sid, why="session %s at %d context tokens, at or past the %d ceiling: "
                   "a fresh holder starts from the packet%s" % (sid, ctx, ceiling, rec))
    else:
        out.update(action="resume", session_id=sid, why="resume session %s (%s of %d context tokens)%s" % (
            sid, ctx if isinstance(ctx, int) else UNMEASURED, ceiling, rec))
    return out



def record_session(root, mod, session_id, context_tokens, lease=None, ts=None, views=True):
    """DISPATCH records the holder's session (its id and context size, read from its transcript at the run's end) in
    its own shard, naming the run's lease (default: the current one), so the next launch can resume it. Never in the
    HOLDER shard: the dispatch clone writing a shard the holder publishes from its clone could overwrite its lines.
    -> (event id, created), or None when that lease was never granted."""
    by, current = leases(read(root, mod))
    current = lease or current
    if current not in by:
        return None
    body = {"session_id": session_id, "lease": current}
    if isinstance(context_tokens, int) and not isinstance(context_tokens, bool):
        body["context_tokens"] = context_tokens
    return append(root, mod, "DISPATCH", "session.id", "session", body=body, ts=ts, env_writer=None, views=views)


# ---- lint -----------------------------------------------------------------------------------------------------------

def mods_with_ledgers(root):
    base = os.path.join(root, "design", "concepts")
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return []
    return [n for n in names if MOD_RE.match(n) and os.path.isdir(os.path.join(base, n, "ledger"))]


def lint(root, mod=None, base="origin/main"):
    """-> (findings [(code, path, line, detail)], notes). The worktree against `base` (None/'' = no base: the
    append-only checks are UNMEASURED and said so)."""
    notes = []
    have_base = bool(base) and ledger_lint.ref_exists(root, base)
    if base and not have_base:
        notes.append("no base ref %r — NOT_APPEND checks UNMEASURED, structure only" % base)
    if not base:
        notes.append("no base given — NOT_APPEND checks UNMEASURED, structure only; the standard checks every line; "
                     "sha: refs UNMEASURED")
    out = []
    for m in ([mod] if mod else mods_with_ledgers(root)):
        out += _lint_mod(root, m, base if have_base else None)
    return out, notes


def _lint_mod(root, mod, base):
    out = []
    d = ledger_dir(root, mod)
    rel_d = os.path.relpath(d, root)
    names = shard_names(root, mod)
    if base:
        r = ledger_lint._git(root, "ls-tree", "--name-only", base, rel_d + "/")
        names = sorted(set(names) | {os.path.basename(p)[:-len(".jsonl")] for p in r.stdout.decode().splitlines()
                                     if p.endswith(".jsonl")})
    new_ids = set()
    for shard in names:
        rel = "%s/%s.jsonl" % (rel_d, shard)
        data = _shard_bytes(root, mod, shard) if os.path.exists(os.path.join(root, rel)) else None
        base_data = ledger_lint.blob_at(root, base, rel) if base else None
        old = {l.strip() for l in (base_data or b"").split(b"\n") if l.strip()}
        for l in (data or b"").split(b"\n"):
            if l.strip() and l.strip() not in old:
                try:
                    new_ids.add(json.loads(l).get("id"))
                except (ValueError, AttributeError):
                    pass
        # Delete on sight (his ruling 2026-11-15 ~10:16 PM PST): a whole line gone is allowed, so rimflow's NOT_APPEND
        # and DUP_DIFFERENT do not apply here; a line CHANGED in place is still refused (EDITED_IN_PLACE, below).
        out += [f for f in ledger_lint.lint_blob(rel, data, base_data) if f[0] not in ("NOT_APPEND", "DUP_DIFFERENT")]
        out += _edited_in_place(rel, data, base_data)
        if not WRITER_RE.match(shard):
            out.append(("BAD_SHARD_NAME", rel, 0, "a shard is named for its writer: DISPATCH, OWNER, STEWARD, "
                        "BACKFILL, HOLDER.<lease>, JUDGE.<run>"))
    events = read(root, mod)
    by, _ = leases(events)
    keys = {}
    for e in events:
        rel = "%s/%s.jsonl" % (rel_d, e["_shard"])
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            out.append(("MISSING_FIELD", rel, e["_seq"], "missing %s" % ", ".join(missing)))
            continue
        w = e["writer"]
        if w != e["_shard"]:
            out.append(("WRONG_SHARD", rel, e["_seq"], "an event written by %s sits in the %s shard (a writer "
                        "appends only to its own)" % (w, e["_shard"])))
        if e["mod"] != mod:
            out.append(("WRONG_MOD", rel, e["_seq"], "event names mod %r" % e["mod"]))
        if WRITER_RE.match(e["_shard"]) and not kind_allowed(e["_shard"], e["kind"]):
            out.append(("KIND_NOT_ALLOWED", rel, e["_seq"], "%s may not write %r" % (e["_shard"], e["kind"])))
        if e["id"] != derive_id(w, e["key"]):
            out.append(("ID_MISMATCH", rel, e["_seq"], "id is not derived from writer and key"))
        k = (e["_shard"], e["key"])
        if k in keys and keys[k] != model.event_key(_clean(e)):
            out.append(("DUP_KEY", rel, e["_seq"], "two different events share the idempotency key %s" % e["key"]))
        keys.setdefault(k, model.event_key(_clean(e)))
        if e["kind"] == "finding.open":
            fix = (e.get("body") or {}).get("proposed_fix")
            if not isinstance(fix, str) or len(fix.strip()) < config()["proposed_fix_min_chars"]:
                out.append(("NO_PROPOSED_FIX", rel, e["_seq"], "a finding carries the precise fix its finder would "
                            "make"))
        cls = writer_class(e["_shard"])
        if cls == "HOLDER" and w == e["_shard"]:
            why = fenced(e, by)
            if why:
                out.append(("STALE_TOKEN", rel, e["_seq"], why))
        if cls == "JUDGE" and e.get("run") != writer_suffix(e["_shard"]):
            out.append(("WRONG_SHARD", rel, e["_seq"], "a JUDGE.<run> shard holds that run's events only"))
        if cls == "OWNER" and not any((e.get("authority") or {}).get(a) for a in OWNER_AUTH):
            out.append(("NO_AUTHORITY", rel, e["_seq"], "an OWNER event carries his words, card or ruling"))
        if cls == "BACKFILL" and not e.get("evidence"):
            out.append(("NO_EVIDENCE", rel, e["_seq"], "a BACKFILL event cites the old file it came from"))
    out += _lint_standard(root, mod, events, new_ids, base)
    for shard, s in seals(events).items():
        data = _shard_bytes(root, mod, shard)
        if hashlib.sha256(data).hexdigest() == s.get("sha256"):
            continue
        lines = [l for l in data.split(b"\n") if l.strip()]
        sealed = set(s.get("line_sha") or [])
        grew = ([l for l in lines if _line_sha(l) not in sealed] if s.get("line_sha") is not None
                else (lines if len(lines) > s.get("lines", 0) else []))
        if grew:                      # a line deleted after the seal is allowed (delete on sight); one added is not
            out.append(("SEALED_CHANGED", "%s/%s.jsonl" % (rel_d, shard), 0, "%d line(s) in the judge shard are not "
                        "in its seal: added or changed after the run ended" % len(grew)))
    if names:
        out += _lint_views(root, mod)
    return out


def _lint_standard(root, mod, events, new_ids, base):
    """The entry standard over every line new since `base` (all lines when there is none): the append checks again, so
    a hand-written line that skipped `append` is caught; and every `sha:` ref and code_sha must resolve on the base
    (a sha cited before ./publish can be rewritten at landing), every `path:` ref must exist."""
    out = []
    rel_d = os.path.relpath(ledger_dir(root, mod), root)
    sup = {e["supersedes"] for e in events if isinstance(e.get("supersedes"), str)}
    shas = {}
    for i, e in enumerate(events):
        if e.get("id") not in new_ids:
            continue
        rel = "%s/%s.jsonl" % (rel_d, e["_shard"])
        b = e.get("body")
        probs = check_entry(e.get("writer"), e.get("kind"), e.get("subject"), b, e.get("evidence"), e.get("code_sha"),
                            e.get("authority"), root)
        if not probs:
            prior = [x for x in events[:i] if x.get("id") not in sup]
            probs = check_context(prior, e.get("writer"), e.get("kind"), e.get("subject"), b, e.get("code_sha"),
                                  (b or {}).get("new_subject_why") if isinstance(b, dict) else None)
        for pr in probs:
            out.append(("STANDARD", rel, e["_seq"], str(pr)))
        refs = [r for r in (e.get("evidence") or []) if isinstance(r, str)]
        cited = [r[4:] for r in refs if r.startswith("sha:")] + ([e["code_sha"]] if isinstance(e.get("code_sha"), str)
                                                                 else [])
        for sha in cited:
            if not base:
                continue
            if sha not in shas:
                shas[sha] = _sha_on(root, sha, base)
            if not shas[sha]:
                out.append(("SHA_NOT_ON_BASE", rel, e["_seq"], "REFUSED evidence: %s does not resolve on %s · would "
                            "pass: the sha ./publish printed · smallest fix: delete the entry and append it citing the "
                            "landed sha (git log --oneline -- <the files>)" % (sha, base)))
        for r in refs:
            if r.startswith("path:"):
                target = re.sub(r"(#.*|:\d+(-\d+)?)$", "", r[5:])
                if not os.path.exists(os.path.join(root, target)):
                    out.append(("PATH_MISSING", rel, e["_seq"], "REFUSED evidence: %s is not in the tree · would pass: a "
                                "repo path that exists (ext: for one outside git) · smallest fix: cite where it lives "
                                "now" % r))
    return out


def _sha_on(root, sha, base):
    if not re.match(r"^[0-9a-f]{6,40}$", sha):
        return False
    r = ledger_lint._git(root, "rev-parse", "--verify", "-q", sha + "^{commit}")
    if r.returncode != 0:
        return False
    full = r.stdout.decode().strip()
    return ledger_lint._git(root, "merge-base", "--is-ancestor", full, base).returncode == 0


def _lint_views(root, mod):
    out = []
    want = render_views(root, mod)
    vd = views_dir(root, mod)
    for name, text in want.items():
        p = os.path.join(vd, name)
        rel = os.path.relpath(p, root)
        try:
            with open(p, encoding="utf-8") as fh:
                have = fh.read()
        except OSError:
            out.append(("VIEW_MISSING", rel, 0, "regenerate: modledger.py views --mod %s" % mod))
            continue
        if have == text:
            continue
        meta, body = _view_meta(name, have)
        if meta is None or hashlib.sha256(body.encode("utf-8")).hexdigest() != meta.get("body_sha256"):
            out.append(("VIEW_EDITED", rel, 0, "the view was edited by hand; a view is printed from the ledger, "
                        "never written. Append the fact as an event, then: modledger.py views --mod %s" % mod))
        else:
            out.append(("VIEW_STALE", rel, 0, "built from shards %s (reducer %s), the ledger is now %s (reducer %d):"
                        " modledger.py views --mod %s" % (_canon(meta.get("shards")), meta.get("reducer"),
                                                          _canon(_offsets(root, mod)), REDUCER_VERSION, mod)))
    return out


# ---- CLI ------------------------------------------------------------------------------------------------------------

def _line(e):
    t = _one(_text(e))
    fix = (e.get("body") or {}).get("proposed_fix")
    return "%s %s#%d %s %s v%s%s: %s%s" % (e.get("ts"), e["_shard"], e["_seq"], e.get("kind"), e.get("subject"),
                                           e.get("version"), (" supersedes %s" % e["supersedes"])
                                           if e.get("supersedes") else "", t,
                                           (" — proposed fix: " + _one(fix)) if fix else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="verb", required=True)
    a = sub.add_parser("append")
    a.add_argument("--mod", required=True)
    a.add_argument("--writer", required=True)
    a.add_argument("--kind", required=True)
    a.add_argument("--subject", required=True)
    a.add_argument("--version")
    a.add_argument("--text")
    a.add_argument("--fix", help="the precise fix the finder would make (finding.open)")
    a.add_argument("--accept", help="finding.open: a runnable command and its expected result, or 'none, <reason>'")
    a.add_argument("--said", help="his words, verbatim (question.answer, decision)")
    a.add_argument("--bars", help="comma-separated locked bar ids")
    a.add_argument("--tags", help="comma-separated facets (modledger.json standard.facets)")
    a.add_argument("--new-subject", help="why this new subject differs from the live one it resembles")
    a.add_argument("--body", help="a JSON object merged into the body")
    a.add_argument("--evidence", action="append", default=[])
    a.add_argument("--supersedes")
    a.add_argument("--code-sha")
    a.add_argument("--token", type=int)
    a.add_argument("--run")
    a.add_argument("--key")
    # AUTH_KEYS, written out so the authority census reads the Conductor's route beside --said
    # (RIMMANDRAKE_ROUTE_MODLEDGER_OWNER_GATES_VIA_CONDUCTOR)
    a.add_argument("--owner-said")
    a.add_argument("--by-card")
    a.add_argument("--per-ruling", help="a standing ruling, e.g. CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM with the "
                   "Conductor's text in --why")
    a.add_argument("--why")
    a.add_argument("--no-views", action="store_true")
    g = sub.add_parser("grant")
    g.add_argument("--mod", required=True)
    g.add_argument("--lease", required=True)
    g.add_argument("--version")
    s = sub.add_parser("seal")
    s.add_argument("--mod", required=True)
    s.add_argument("--run", required=True)
    sh = sub.add_parser("show")
    sh.add_argument("--mod", required=True)
    sh.add_argument("subject", nargs="?")
    sh.add_argument("--kind")
    stp = sub.add_parser("state")
    stp.add_argument("--mod", required=True)
    p = sub.add_parser("packet")
    p.add_argument("--mod", required=True)
    p.add_argument("--budget", type=int)
    p.add_argument("--strict", action="store_true", help="exit 1 on an empty ledger or a packet over budget")
    rp = sub.add_parser("resume-plan", help="the holder's next launch: resume its session, rotate, or the packet")
    rp.add_argument("--mod", required=True)
    v = sub.add_parser("views")
    v.add_argument("--mod", required=True)
    de = sub.add_parser("delete", help="delete wrong or useless entries on sight (any writer, anyone's)")
    de.add_argument("--mod", required=True)
    de.add_argument("--id", action="append", required=True)
    dl = sub.add_parser("deletions", help="the deletion monitor: deleted entries from git, per mod and writer")
    dl.add_argument("--mod")
    dl.add_argument("--since", help="git --since (e.g. 2026-11-15)")
    dl.add_argument("--json", action="store_true")
    ix = sub.add_parser("index", help="(re)build the throwaway search index under /tmp")
    ix.add_argument("--mod", required=True)
    fd = sub.add_parser("find", help="search the ledger: words, a class, his words, a path")
    fd.add_argument("--mod", required=True, help="a mod, or 'all'")
    fd.add_argument("query", nargs="*")
    fd.add_argument("--class", dest="cls", choices=list(config()["standard"]["subject_classes"]))
    fd.add_argument("--kind")
    fd.add_argument("--his", action="store_true", help="his words and cards only")
    fd.add_argument("--path", help="traps (and entries) whose where or evidence names this path")
    fd.add_argument("--all", dest="all_", action="store_true", help="closed subjects too (verified, withdrawn, ...)")
    op = sub.add_parser("open", help="open and claimed-fixed findings, with fix and accept")
    op.add_argument("--mod", required=True, help="a mod, or 'all'")
    op.add_argument("--bar")
    sn = sub.add_parser("since", help="what changed after a cursor (the packet's last line), an event id or a time")
    sn.add_argument("--mod", required=True)
    sn.add_argument("cursor")
    li = sub.add_parser("lint")
    li.add_argument("--mod")
    li.add_argument("--base", default="origin/main", help="'' for none")
    o = ap.parse_args(argv)
    root = o.root or default_root()
    try:
        if o.verb == "append":
            body = json.loads(o.body) if o.body else {}
            if not isinstance(body, dict):
                raise ModLedgerError("--body is a JSON object")
            if o.text is not None:
                body["text"] = o.text
            if o.fix is not None:
                body["proposed_fix"] = o.fix
            for k in ("accept", "said"):
                if getattr(o, k) is not None:
                    body[k] = getattr(o, k)
            for k in ("bars", "tags"):
                if getattr(o, k) is not None:
                    body[k] = [x.strip() for x in getattr(o, k).split(",") if x.strip()]
            auth = {k: getattr(o, k) for k in AUTH_KEYS if getattr(o, k)}
            eid, created = append(root, o.mod, o.writer, o.kind, o.subject, body=body, version=o.version,
                                  evidence=o.evidence, supersedes=o.supersedes, code_sha=o.code_sha, token=o.token,
                                  run=o.run, key=o.key, authority=auth or None, views=not o.no_views,
                                  new_subject=o.new_subject)
            print(("APPENDED " if created else "ALREADY ") + eid)
        elif o.verb == "grant":
            print("TOKEN %d" % grant(root, o.mod, o.lease, version=o.version))
        elif o.verb == "seal":
            print("SEALED " + seal(root, o.mod, o.run))
        elif o.verb == "show":
            evs = [e for e in read(root, o.mod) if (not o.subject or e.get("subject") == o.subject)
                   and (not o.kind or e.get("kind") == o.kind)]
            for e in evs:
                print(_line(e))
            print("%d event%s" % (len(evs), "" if len(evs) == 1 else "s"))
        elif o.verb == "state":
            print(json.dumps(reduce(read(root, o.mod)), indent=1, sort_keys=True, ensure_ascii=False))
        elif o.verb == "packet":
            text, info = packet(root, o.mod, o.budget, stale=stale_check(root))
            sys.stdout.write(text)
            print("packet: %d tokens of budget %d; %d events; left out %s"
                  % (info["tokens"], info["budget"], info["events"], _canon(info["dropped"]) if info["dropped"]
                     else "nothing but the full history"), file=sys.stderr)
            if o.strict and (info["events"] == 0 or info["over_budget"]):
                return 1
        elif o.verb == "resume-plan":
            print(json.dumps(resume_plan(root, o.mod), sort_keys=True))
        elif o.verb == "views":
            for pth in write_views(root, o.mod):
                print("wrote " + os.path.relpath(pth, root))
        elif o.verb == "delete":
            for g in delete(root, o.mod, o.id):
                print("DELETED %s (%s %s) from %s" % (g["id"], g["kind"], g["subject"], g["shard"]))
        elif o.verb == "deletions":
            d = deletions(root, o.since, o.mod)
            if o.json:
                print(json.dumps(d, indent=1, sort_keys=True, ensure_ascii=False))
                return 0
            for m_, c in sorted(d["counts"].items()):
                print("%s: %s" % (m_, ", ".join("%s %d" % kv for kv in sorted(c.items()))))
            for r in d["flagged"]:
                print("FLAG %s %s %s %s%s, deleted in %s (%s)" % (r["mod"], r["shard"], r["kind"], r["subject"],
                                                                  " (open)" if r["was_open"] else "", r["commit"][:10],
                                                                  r["commit_subject"]))
            print("deletions: %d, %d for the digest" % (len(d["deleted"]), len(d["flagged"])))
        elif o.verb == "index":
            print("INDEX " + index(root, o.mod))
        elif o.verb in ("find", "open"):
            mods = mods_with_ledgers(root) if o.mod == "all" else [o.mod]
            rows = []
            for m_ in mods:
                rows += (find(root, m_, " ".join(o.query), o.cls, o.kind, o.his, o.path, o.all_) if o.verb == "find"
                         else open_findings(root, m_, o.bar))
            for x in rows:
                head = "%s%s [%s]" % ("%s " % x["mod"] if o.mod == "all" else "", x["subject"], x.get("status"))
                if o.verb == "open":
                    print("%s %s" % (head, _one(x["text"])))
                    print("  proposed fix: %s" % _one(x["proposed_fix"]))
                    print("  accept: %s" % _one(x["accept"]))
                    if x.get("claim"):
                        print("  holder: %s%s" % (_one(x["claim"]), (" (%s)" % x["code_sha"]) if x.get("code_sha")
                                                  else ""))
                elif x.get("said"):
                    print("%s %s %s: \"%s\" (authority %s)" % (head, x["kind"], x["id"], x["said"],
                                                             _canon(x["authority"] or {})))
                else:
                    print("%s %s %s: %s%s" % (head, x["kind"], x["id"], _one(x["text"]),
                                              (" (where: %s)" % x["where"]) if x.get("where") else ""))
            print("%d %s" % (len(rows), "match" if len(rows) == 1 else "matches") if o.verb == "find" else
                  "%d open finding%s" % (len(rows), "" if len(rows) == 1 else "s"))
        elif o.verb == "since":
            rows = since(root, o.mod, o.cursor)
            for x in rows:
                print("%s [%s] %s (%s)" % (x["subject"], x["status"], ", ".join(x["kinds"]), x["last_ts"]))
            print("%d subject%s moved" % (len(rows), "" if len(rows) == 1 else "s"))
        elif o.verb == "lint":
            findings, notes = lint(root, o.mod, o.base or None)
            for n in notes:
                print("note: " + n)
            for code, path, ln, detail in findings:
                print("%s %s:%s %s" % (code, path, ln, detail))
            print("modledger lint: %d finding%s" % (len(findings), "" if len(findings) == 1 else "s"))
            return 1 if findings else 0
    except Refusal as e:
        print(str(e))
        return 2
    except ModLedgerError as e:
        print("REFUSED: %s" % e)
        return 2 if o.verb == "append" else 1
    except Exception as e:                       # noqa: BLE001 — say so, exit 2
        print("modledger: could not run: %s: %s" % (type(e).__name__, e))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
