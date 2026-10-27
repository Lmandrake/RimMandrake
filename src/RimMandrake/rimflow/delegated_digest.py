#!/usr/bin/env python3
"""delegated_digest.py — the owner's daily digest of delegated calls, built by a program (delegation_policy.md §5).

No AI. Once a day, as the Conductor's pre-step (dispatcher_schedule.json `pre_launch`), this writes
`Transient/delegated_digest_<YYYY-MM-DD>.md`: every delegated call since the last digest, grouped by class, newest
first, with counts MEASURED from the records. The Conductor delivers it (conductor.md, scheduled check (d)); it never
assembles one by hand. Item DELEGATED_DIGEST_FIX_NEVER_WRITTEN.

Sources (each read whole, filtered to the window since < t <= cut):
  ledger      every event whose `why` starts `delegated:` (rimflow model.read(), all shards). The class is the logged
              label after `delegated:`; one line per (class, item); events with no item (a `bridge` take, a `game`
              state the bridge-idle path set, §2.6) are a line each.
  verdicts    the judge records infrastructure/state/delegated/<date>/*.json (§4); t = the commit that added the file
              (git), or its mtime while untracked. Art verdicts are grouped by subject.
  commits     `git log --grep '^Delegated:'` (§5).
  art marks   artledger.marks_digest(since) (§2.3, class `art marks`).
  art installs  the art ledger's live events whose `why` starts `delegated:` (other than art marks): art-eval keeps
              going live, geometric corrections (§2.3).
  leftovers   D:\\ClaudeWork\\backups\\leftovers\\acts.jsonl (§2.2): one line per deletion with its archive.

🔴 TOKEN-BLIND BY CONSTRUCTION (owner 2026-10-27; the Conductor reads this file). Built from an ALLOW-list of fields,
never a deny-list: each source names the fields it copies (ALLOWED below) and nothing else of a record is ever
read into the output — a record's cost, seconds, account or any field added later cannot reach the page. The judge
is named only by a model FAMILY from a closed set. Every copied string then passes blind_view.redact() (numbers
near account/token/cap words, unit numbers like 80k / 6% / $0.33, numbers >= 10,000, account-named ids) and
account names are masked. Items blind_view withholds (about accounts) are counted, never named.
selftest_delegated_digest.py injects an account id, a token figure and a cost into every source and proves none
appears.

The window: `since` is the previous digest's cut, kept in a state file a program reads (scratch, never the repo):
D:\\ClaudeWork\\rimmandrake\\delegated_digest\\state.json. No state = since the beginning. One digest per date: if
today's file exists the run does nothing. A dry run (--dry-run) writes where --out-dir says and never moves the
state. A digest with zero calls is checked against the instrument first (§5): it says how many delegated events the
sources see in all time, so a blind instrument is never reported as "nothing delegated".

--pre-launch: a pre-step's non-zero exit stops the Conductor (role_launch.launch_argv), and a missing digest must
not cost the owner his Conductor: in this mode any failure writes `delegated_digest_<date>.FAILED.md` beside the
digest (the reason only) and exits 0.

Usage:
  python3 src/RimMandrake/rimflow/delegated_digest.py                  # build today's, advance the state
  python3 src/RimMandrake/rimflow/delegated_digest.py --dry-run --out-dir /mnt/d/ClaudeWork/.../sample
  python3 src/RimMandrake/rimflow/delegated_digest.py --since 2026-10-26T00:00:00Z --dry-run --out-dir ...
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SRC))
for p in (SRC, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
import blind_view as B  # noqa: E402

DELEGATED_DIR = os.path.join(ROOT, "infrastructure", "state", "delegated")
OUT_DIR = os.path.join(ROOT, "Transient")
STATE = "/mnt/d/ClaudeWork/rimmandrake/delegated_digest/state.json"
LEFTOVERS = "/mnt/d/ClaudeWork/backups/leftovers/acts.jsonl"
EPOCH = "1970-01-01T00:00:00Z"
MAXLEN = 180                     # one decision's text on a line

# the policy's class names (§1 table, §2 delegations); longest first so `art marks` wins over `art`
POLICY_CLASSES = sorted(["technical", "scope", "design", "art", "cosmetic", "art geometric correction",
                         "art marks", "bridge idle", "leftovers"], key=len, reverse=True)
# a judge is named by model family only, from this closed set; anything else reads "judge"
JUDGE_FAMILIES = ("opus", "sonnet", "haiku", "gpt", "gemini", "nemotron", "human")
# 🔑 THE ALLOW-LIST. The only fields of each source this program reads into the page.
ALLOWED = {
    "ledger": ("ts", "seat", "event", "id", "why", "title", "text", "to", "sha", "state", "ranBy", "purpose",
               "idleProbe", "reason"),
    "verdict": ("subject", "item", "class", "decision", "verdict", "overall", "final", "recommended_pick"),
    "verdict_judge": ("judge_model",),          # keys only, matched against JUDGE_FAMILIES
    "leftover": ("ts", "kind", "path", "archive"),
    "commit": ("sha", "ts", "subject"),
    "art_install": ("type", "ts", "seat", "why", "mod", "rel", "sha"),
}
SKIP_VERBS = {"lease", "renew", "release"}    # lease bookkeeping a claim already shows


# ------------------------------------------------------------------------------------------------ blind text ----
def _account_names():
    return {n for n in B.account_names() if n not in JUDGE_FAMILIES and n not in B.SOFT_NAMES
            and n not in ("codex",)}


# a secret-shaped word (sk-..., key-..., Bearer ...) never reaches the page even if a why carries one
_KEYLIKE = re.compile(r"(?i)\b(?:sk|pk|rk|key|api[_-]?key|token)[-_][A-Za-z0-9_-]{4,}|\bBearer\s+\S+")


def blind(text, hide=(), keep=()):
    """Every string that reaches the page passes here: redact(), then account names masked."""
    out = B.redact(str(text or ""), hide, keep)
    names = _account_names()
    if names:
        out = re.sub(r"(?i)(?<![A-Za-z])(%s)(?![a-z])" % "|".join(re.escape(n) for n in sorted(names, key=len,
                                                                                              reverse=True)),
                     B.MASK, out)
    out = _KEYLIKE.sub(B.MASK, out)
    return re.sub(r"\s+", " ", out).strip()


def short(text, n=MAXLEN):
    return text if len(text) <= n else text[:n - 1].rstrip() + "…"


MIRROR = "D:\\Luke\\dev\\RimMandrake"     # the owner's read-only mirror of the repo: a tracked file's native path


def native(p):
    """A path as the owner opens it on Windows."""
    if not p:
        return ""
    m = re.match(r"^/mnt/([a-z])/(.*)$", p)
    if m:
        return "%s:\\%s" % (m.group(1).upper(), m.group(2).replace("/", "\\"))
    if p.startswith("/"):
        return "\\\\wsl.localhost\\%s%s" % (os.environ.get("WSL_DISTRO_NAME") or "Ubuntu", p.replace("/", "\\"))
    return p


# ------------------------------------------------------------------------------------------------- time ------
def utc(ts):
    """ISO text -> aware UTC datetime; a naive time is local (leftovers' acts.jsonl). None if unreadable."""
    if not ts:
        return None
    try:
        d = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.astimezone()
    return d.astimezone(dt.timezone.utc)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def in_window(t, since, cut):
    return t is not None and since < t <= cut


# ----------------------------------------------------------------------------------------------- classes -----
def class_of(why):
    """`delegated: art facing judge 2026-10-26, table…` -> ('art facing judge', 'art'). The label is what was
    logged (cut at the first — ; , ( : [ or ' per '); the policy class is the longest policy name it starts with,
    or None when the label names no policy class."""
    rest = str(why or "")
    while rest.lower().startswith("delegated:"):          # "delegated: delegated: art" was logged too
        rest = rest[len("delegated:"):].strip()
    label = re.split(r"\s+[—–-]\s+|--|[—–;,(:\[]|\.\s|\s+per\s+|\s+\d{4}-\d{2}-\d{2}", rest,
                     maxsplit=1)[0].strip().rstrip(".").lower()
    label = " ".join(label.split()[:5]) or "(no class)"
    for c in POLICY_CLASSES:
        if label == c or re.match(re.escape(c) + r"[\s/\-]", label):
            return label, c
    return label, None


# ------------------------------------------------------------------------------------------------ sources -----
def ledger_calls(events, since, cut, hide, keep):
    """-> (calls, withheld_count). One call per event; grouping happens in render."""
    out, n_hidden = [], 0
    for raw in events:
        ev = {k: raw.get(k) for k in ALLOWED["ledger"] if k in raw}
        why = str(ev.get("why") or "")
        if not why.startswith("delegated:") or ev.get("event") in SKIP_VERBS:
            continue
        t = utc(ev.get("ts"))
        if not in_window(t, since, cut):
            continue
        iid = ev.get("id") or ""
        if iid and (iid in hide or B._account_item_id(iid)):
            n_hidden += 1
            continue
        label, cls = class_of(why)
        verb = ev.get("event") or "?"
        if verb == "file":
            what = "filed: %s" % (ev.get("title") or "")
        elif verb in ("close", "implemented"):
            what = "%s at %s" % ("closed" if verb == "close" else "implemented", str(ev.get("sha") or "")[:10])
        elif verb == "note":
            what = "note: %s" % (ev.get("text") or "")
        elif verb in ("needs", "reassign", "retarget"):
            what = "%s → %s" % (verb, ev.get("to") or "")
        elif verb == "game":
            what = "game %s" % (ev.get("state") or "")
        elif verb == "bridge":
            what = "bridge %s%s" % (ev.get("state") or "", (" for " + str(ev["purpose"])) if ev.get("purpose") else "")
            if ev.get("idleProbe"):
                what += " (probe: %s)" % ev["idleProbe"]
        elif verb in ("drop", "supersede", "block"):
            what = "%s%s" % (verb, (": " + str(ev["reason"])) if ev.get("reason") else "")
        else:
            what = verb
        by = ev.get("ranBy") or ev.get("seat") or "?"
        detail = re.split(r"[—–]", why, maxsplit=1)
        out.append({"src": "ledger", "t": t, "cls": cls, "label": label, "item": iid, "verb": verb,
                    "what": blind(what, hide, keep), "why": blind(detail[1] if len(detail) > 1 else "", hide, keep),
                    "by": blind(by), "evidence": _paths_in(why + " " + str(ev.get("text") or ""))})
    return out, n_hidden


_PATH_RE = re.compile(r"(infrastructure/state/delegated/[\w./-]+\.json|[A-Z]:\\\\?ClaudeWork\\[^\s,;)\]'\"]+)")


def _paths_in(text):
    return sorted({m.group(1).rstrip(".:") for m in _PATH_RE.finditer(text or "")})


def judge_of(rec):
    jm = rec.get(ALLOWED["verdict_judge"][0])
    fams = []
    if isinstance(jm, dict):
        for k in jm:
            fam = next((f for f in JUDGE_FAMILIES if str(k).lower().startswith(f)), None)
            if fam and fam not in fams:
                fams.append(fam)
    return "+".join(fams) if fams else "judge"


def _decided(rec):
    for k in ("decision", "verdict", "overall", "final", "recommended_pick"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, dict):
            for kk in ("decision", "verdict", "pick"):
                if isinstance(v.get(kk), str):
                    return v[kk]
    return "(structured verdict: see file)"


def git_added_times(root, rel_dir):
    """-> {repo-relative path: aware UTC datetime of the commit that added it}. One git call."""
    try:
        r = subprocess.run(["git", "-C", root, "log", "--diff-filter=A", "--name-only", "--format=@%cI", "--",
                            rel_dir], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return {}
    out, cur = {}, None
    for line in r.stdout.splitlines():
        if line.startswith("@"):
            cur = utc(line[1:])
        elif line.strip() and cur is not None:
            out.setdefault(line.strip(), cur)     # newest first: an add after a delete keeps the newest add
    return out


def verdict_calls(root, ddir, since, cut, hide, keep, added=None):
    rel_dir = os.path.relpath(ddir, root)
    added = git_added_times(root, rel_dir) if added is None else added
    out, n_hidden, unreadable = [], 0, 0
    for f in sorted(glob.glob(os.path.join(ddir, "*", "*.json"))):
        rel = os.path.relpath(f, root)
        t = added.get(rel)
        if t is None:
            t = dt.datetime.fromtimestamp(os.path.getmtime(f), dt.timezone.utc)
        if not in_window(t, since, cut):
            continue
        try:
            raw = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            unreadable += 1
            continue
        if not isinstance(raw, dict):
            unreadable += 1
            continue
        rec = {k: raw.get(k) for k in ALLOWED["verdict"] + ALLOWED["verdict_judge"] if k in raw}
        item = rec.get("item") if isinstance(rec.get("item"), str) else ""
        if item and (item in hide or B._account_item_id(item)):
            n_hidden += 1
            continue
        is_art = "image_sha256" in raw          # the art-eval pipeline's record shape (key presence only)
        if is_art:
            label, pcls = "art", "art"
        elif isinstance(rec.get("class"), str) and rec["class"].strip():
            label, pcls = class_of("delegated: " + rec["class"])
        else:
            label, pcls = "judge verdict", None
        subject = rec.get("subject") if isinstance(rec.get("subject"), str) else os.path.basename(f)[:-5]
        out.append({"src": "verdict", "t": t, "cls": pcls, "label": label, "item": blind(item, hide, keep),
                    "subject": blind(subject, hide, keep), "art": is_art,
                    "what": blind(_decided(rec), hide, keep), "by": judge_of(rec), "evidence": [rel]})
    return out, n_hidden, unreadable


def commit_calls(root, since, cut, hide, keep):
    try:
        r = subprocess.run(["git", "-C", root, "log", "--grep=^Delegated:", "--format=%H%x1f%cI%x1f%s"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return []
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        sha, ts, subj = parts
        t = utc(ts)
        if not in_window(t, since, cut):
            continue
        out.append({"src": "commit", "t": t, "cls": None, "label": "commit", "item": "",
                    "what": blind(subj, hide, keep), "by": "git", "evidence": [sha[:10]]})
    return out


def _artledger():
    sys.path.insert(0, os.path.join(SRC, "Utils", "art"))
    import artledger  # noqa: E402
    return artledger


def marks_calls(since, hide, keep, lines=None):
    """art.py marks-digest's lines (already newest first). None from the art ledger = the source is UNMEASURED."""
    if lines is None:
        try:
            lines = _artledger().marks_digest(iso(since))
        except Exception as e:  # noqa: BLE001 — a broken source is reported, never fatal
            return None, "%s: %s" % (type(e).__name__, str(e)[:120])
    return [{"src": "marks", "t": None, "cls": "art marks", "label": "art marks", "item": "",
             "what": blind(l, hide, keep), "by": "art.py enact", "evidence": []} for l in lines], None


def art_install_calls(since, cut, hide, keep, events=None):
    """Delegated installs in the art ledger (`why` starting `delegated:`, other than `art marks`, which
    marks_calls lists): an art-eval keep going live, a geometric correction (§2.3). None = UNMEASURED."""
    if events is None:
        try:
            L = _artledger()
            events, marks_why = L.cached_index().events, L.MARKS_WHY
        except Exception as e:  # noqa: BLE001
            return None, "%s: %s" % (type(e).__name__, str(e)[:120])
    else:
        marks_why = "delegated: art marks"
    out = []
    for raw in events:
        ev = {k: raw.get(k) for k in ALLOWED["art_install"] if k in raw}
        why = str(ev.get("why") or "")
        if ev.get("type") != "live" or not why.startswith("delegated:") or why.startswith(marks_why):
            continue
        t = utc(ev.get("ts"))
        if not in_window(t, since, cut):
            continue
        label, cls = class_of(why)
        where = "%s/%s" % (str(ev.get("mod") or "").rsplit("/", 1)[-1], ev.get("rel") or "")
        out.append({"src": "art_install", "t": t, "cls": cls, "label": label, "item": "",
                    "subject": blind(where, hide, keep),
                    "what": "installed %s" % str(ev.get("sha") or "")[:12], "by": blind(ev.get("seat") or "?"),
                    "evidence": _paths_in(why)})
    return out, None


def leftover_calls(path, since, cut, hide, keep):
    if not os.path.exists(path):
        return None
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            raw = json.loads(line)
        except ValueError:
            continue
        rec = {k: raw.get(k) for k in ALLOWED["leftover"] if k in raw}
        t = utc(rec.get("ts"))
        if not in_window(t, since, cut):
            continue
        out.append({"src": "leftovers", "t": t, "cls": "leftovers", "label": "leftovers", "item": "",
                    "what": blind("deleted %s %s" % (rec.get("kind") or "?", native(str(rec.get("path") or ""))),
                                  hide, keep),
                    "by": "leftovers.py", "evidence": [blind(native(str(rec.get("archive") or "")), hide, keep)]})
    return out


# ------------------------------------------------------------------------------------------------- render -----
def _hm(t):
    return t.strftime("%m-%d %H:%MZ") if t else "—"


def _ev(paths, root_native):
    out = []
    for p in paths:
        if p.startswith("infrastructure/"):
            out.append(root_native + "\\" + p.replace("/", "\\"))
        else:
            out.append(p)
    return " · ".join(out)


def render(date, since, cut, calls, counts, notes, root_native):
    """-> markdown. counts: dict of MEASURED numbers; notes: lines about sources (UNMEASURED, withheld)."""
    groups = {}
    for c in calls:
        key = c["cls"] or c["label"]
        groups.setdefault(key, []).append(c)
    total = len(calls)
    head = ["# Delegated calls — digest %s" % date, "",
            "Every call an agent took without you under delegation_policy.md, from %s to %s (UTC), grouped by "
            "class, newest first. Built by a program from the records; every count below is measured from them. "
            "To overturn a line, say so in any words." % ("the beginning" if since.year < 2000 else iso(since),
                                                         iso(cut)), ""]
    head.append("**%d delegated call record(s)**: %d ledger event(s), %d judge verdict file(s), %d `Delegated:` "
                "commit(s), %d art-mark act(s), %d delegated art install(s), %d leftover deletion(s)." % (
                    total, counts["ledger"], counts["verdict"], counts["commit"], counts["marks"], counts["inst"],
                    counts["leftovers"]))
    for n in notes:
        head.append("- " + n)
    head.append("")
    if total == 0:
        head += ["No delegated call in this window. Instrument check (policy §5): the sources see %d delegated "
                 "ledger event(s) and %d verdict file(s) in all time, the newest at %s." % (
                     counts["all_ledger"], counts["all_verdict"], counts["all_newest"] or "—"), ""]
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    head.append("| class | records | items or subjects named |")
    head.append("|---|---|---|")
    body = []
    for k in order:
        cs = groups[k]
        policy = cs[0]["cls"] is not None
        subj = {c.get("item") or c.get("subject") or "" for c in cs} - {""}
        head.append("| %s%s | %d | %d |" % (k, "" if policy else " (not a policy class)", len(cs), len(subj)))
        body += ["", "## %s — %d record(s)%s" % (k, len(cs), "" if policy else
                                                 " — logged label names no policy class")]
        body += _group_lines(cs, root_native)
    return "\n".join(head + body) + "\n"


def _group_lines(cs, root_native):
    lines = []
    # ledger events: one line per item; events without an item, one line each
    by_item, rest, art = {}, [], {}
    for c in cs:
        if c["src"] == "ledger" and c["item"]:
            by_item.setdefault(c["item"], []).append(c)
        elif c["src"] == "verdict" and c.get("art"):
            art.setdefault(c["subject"], []).append(c)
        else:
            rest.append(c)
    rows = []
    for iid, evs in by_item.items():
        evs.sort(key=lambda c: c["t"], reverse=True)
        last = evs[0]
        verbs = ", ".join(e["verb"] for e in reversed(evs))
        seats = "/".join(sorted({e["by"] for e in evs}))
        why = next((e["why"] for e in evs if e["why"]), "")
        ev = sorted({p for e in evs for p in e["evidence"]})
        txt = "- %s **%s** (%s; %d event(s): %s) — %s%s%s" % (
            _hm(last["t"]), iid, seats, len(evs), verbs, short(last["what"]),
            (" · why: " + short(why, 120)) if why else "", (" · evidence: " + _ev(ev, root_native)) if ev else "")
        rows.append((last["t"], txt))
    for subj, vs in art.items():
        vs.sort(key=lambda c: c["t"], reverse=True)
        tally = {}
        for v in vs:
            tally[v["what"]] = tally.get(v["what"], 0) + 1
        txt = "- %s **%s** (%s; %d verdict(s): %s) — latest %s · evidence: %s" % (
            _hm(vs[0]["t"]), subj, vs[0]["by"], len(vs), ", ".join("%s×%d" % kv for kv in sorted(tally.items())),
            vs[0]["what"], _ev(vs[0]["evidence"], root_native) + (" (+%d more)" % (len(vs) - 1) if len(vs) > 1 else ""))
        rows.append((vs[0]["t"], txt))
    for c in rest:
        who = c["by"]
        lead = ("**%s** " % (c.get("item") or c.get("subject"))) if (c.get("item") or c.get("subject")) else ""
        txt = "- %s %s(%s) — %s%s%s" % (_hm(c["t"]), lead, who, short(c["what"], 240),
                                         (" · why: " + short(c.get("why") or "", 120)) if c.get("why") else "",
                                         (" · evidence: " + _ev(c["evidence"], root_native)) if c["evidence"] else "")
        rows.append((c["t"], txt))
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    rows.sort(key=lambda r: r[0] or epoch, reverse=True)
    return [r[1] for r in rows]


# --------------------------------------------------------------------------------------------------- build ----
def load_state(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
        return utc(d.get("last_cut")) if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def build(date, since, cut, events, root=ROOT, ddir=DELEGATED_DIR, leftovers=LEFTOVERS, world=None,
          added=None, marks_lines=None, art_events=None, commits=True):
    """-> markdown text. All sources injectable for the selftest."""
    hide = B.hidden_ids(world) if world is not None else set()
    keep = B.known_ids(world) if world is not None else set()
    notes = []
    led, h1 = ledger_calls(events, since, cut, hide, keep)
    ver, h2, bad = verdict_calls(root, ddir, since, cut, hide, keep, added)
    com = commit_calls(root, since, cut, hide, keep) if commits else []
    marks, merr = marks_calls(since, hide, keep, marks_lines)
    inst, ierr = art_install_calls(since, cut, hide, keep, art_events)
    left = leftover_calls(leftovers, since, cut, hide, keep)
    if h1 + h2:
        notes.append("%d record(s) about accounts withheld (Operations' alone)." % (h1 + h2))
    if bad:
        notes.append("%d verdict file(s) unreadable (not JSON objects), not counted." % bad)
    if marks is None:
        notes.append("art marks UNMEASURED: the art ledger did not read (%s)." % blind(merr))
        marks = []
    if inst is None:
        notes.append("art installs UNMEASURED: the art ledger did not read (%s)." % blind(ierr))
        inst = []
    if left is None:
        notes.append("leftovers UNMEASURED: %s is absent." % native(leftovers))
        left = []
    calls = led + ver + com + marks + inst + left
    counts = {"ledger": len(led), "verdict": len(ver), "commit": len(com), "marks": len(marks), "inst": len(inst),
              "leftovers": len(left), "all_ledger": 0, "all_verdict": 0, "all_newest": ""}
    if not calls:
        epoch = utc(EPOCH)
        far = cut + dt.timedelta(days=36500)
        al, _ = ledger_calls(events, epoch, far, hide, keep)
        av, _, _ = verdict_calls(root, ddir, epoch, far, hide, keep, added)
        counts["all_ledger"], counts["all_verdict"] = len(al), len(av)
        ts = [c["t"] for c in al + av if c["t"]]
        counts["all_newest"] = iso(max(ts)) if ts else ""
    return render(date, since, cut, calls, counts, notes, MIRROR)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, local)")
    ap.add_argument("--since", help="ISO start (default: the state file's last cut, else the beginning)")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--state", default=STATE)
    ap.add_argument("--dry-run", action="store_true", help="write the digest, never move the state")
    ap.add_argument("--force", action="store_true", help="rebuild even if today's digest exists")
    ap.add_argument("--pre-launch", action="store_true", help="never exit non-zero (the Conductor's pre-step)")
    a = ap.parse_args(argv)
    date = a.date or dt.date.today().isoformat()
    out = os.path.join(a.out_dir, "delegated_digest_%s.md" % date)
    try:
        if os.path.exists(out) and not a.force:
            print("delegated_digest: %s exists; one digest per day, nothing done" % native(out))
            return 0
        cut = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        since = utc(a.since) if a.since else (load_state(a.state) or utc(EPOCH))
        if since is None:
            raise ValueError("--since %r is not an ISO time" % a.since)
        evs, world = B._load()
        text = build(date, since, cut, evs, world=world)
        os.makedirs(a.out_dir, exist_ok=True)
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, out)
        if not a.dry_run:
            os.makedirs(os.path.dirname(a.state), exist_ok=True)
            with open(a.state + ".tmp", "w", encoding="utf-8") as f:
                json.dump({"last_cut": iso(cut), "last_digest": out}, f)
            os.replace(a.state + ".tmp", a.state)
        print("delegated_digest: wrote %s (%s)" % (native(out), text.split("\n")[4][:160]))
        return 0
    except Exception as e:  # noqa: BLE001
        if not a.pre_launch:
            raise
        try:
            os.makedirs(a.out_dir, exist_ok=True)
            with open(os.path.join(a.out_dir, "delegated_digest_%s.FAILED.md" % date), "w", encoding="utf-8") as f:
                f.write("# Delegated digest %s NOT BUILT\n\n%s\n" % (date, blind("%s: %s" % (type(e).__name__, e))))
        except OSError:
            pass
        print("delegated_digest: FAILED (%s); the Conductor starts anyway" % type(e).__name__, file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
