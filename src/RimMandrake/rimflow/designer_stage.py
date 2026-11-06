#!/usr/bin/env python3
"""designer_stage.py - the Designer's stage machine: the launcher, not the model, holds what must happen.

Spec: design/RimMandrake/designer_v4/gpt_review_2026-11-03.md §2-3 (owner by card 2026-11-03, "GPT's full design");
item DESIGNER_STAGES_REBUILD_LAUNCHER_HOLDS_LEASH. The Designer's prose is src/RimMandrake/rimflow/roles/designer*.md.

One concept folder, design/concepts/<Mod>/, holds the persisted state and the checked data:

  stage.json    the state (this program writes it; nobody else): stage 0-5, status, the task budget and its charges,
                the open run with the packet hashes it was given, every accepted result with its frozen input hashes,
                the scene recovery journal
  record.json   the working record (the Designer writes it): scope, decisions, asks, inventory, contradictions,
                failure modes, root; every entry source-linked. Replaces whole-log rereads: log.md stays the verbatim
                record and is never injected
  scenes.json   the proof-scene contract, checked data
  floor.json    per floor line: applicable / not_applicable (evidence) / disabled (an owner exception)
  exam.json     the Stage 4 record, frozen against the tree and sheet hashes
  result.json   what a run says it did; only `close` (the launcher) reads it and advances

  init     <dir> --mod M [--item ID] [--alias GSS]... [--cap N] [--reserve N]   start a concept's state
  open     <dir> --run U [--run-cap N]     the launcher: refuse or return the stage packet (stdout) and reserve budget
  close    <dir> --run U [--tokens N]      the launcher: charge the run, validate result.json, advance or not
  charge   <dir> --tokens N --kind K --ref R   a helper, review or consult outside the run's own transcript
  land     <dir> [--run U]                 land stage.json and the result files on origin/main (close does it itself)
  check    <dir>                           validate result.json now, write nothing (the Designer's dry run)
  status   <dir>                           stage, budget, staleness, open recovery
  spend    <dir>...                        per-stage weighted spend against the default cap (the cap's measurement)
  scene-begin <dir> --scene S --recovery TEXT | scene-end <dir> --scene S | scene-hold <dir> --scene S --until TEXT
  manifest                                 the stage -> packet files table, with hashes
  showcases <dir>                          the showcase set: per showcase new coverage and overlap, what is uncovered
  turns [--root R]                         every turn that waits on him: waiting_owner, no OWNER event since it closed

Exit: 0 ok, 1 refused (the reason on stderr), 2 unreadable.
What this cannot do, said plainly: injecting a packet proves it was supplied, not followed; the record's sources are
checked for shape and existence, not for whether they say what the entry claims; an owner event counts as taken in once
record.json or tree.json cites it, whether or not the citing entry really reflects it.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402

ROLES = os.path.join(HERE, "roles")
MANIFEST = os.path.join(ROLES, "designer_manifest.json")
STAGES = (0, 1, 2, 3, 4, 5)
STAGE_NAMES = {0: "Read", 1: "Argue the idea", 2: "Argue the edge", 3: "Write", 4: "Exam", 5: "Lock"}
OUTCOMES = ("done", "waiting_owner", "return", "blocked")
DIALOGUE = (1, 2)                       # only these stages send him questions
# The task's weighted-token budget across every stage, retry and helper (role_launch.TOKEN_WEIGHTS; advisory, owner
# 2026-11-04). MEASURED 2026-11-05 (DESIGNER_CAP_REMEASURE_STAGE_ZERO_ATE_IT, `designer_stage.py spend` over the four
# committed concepts): the charge is already weighted (rm-role-designer-1793864264: 495,103 weighted of 2,008,722
# raw); the per-stage spend of the 12 stages walked is 206k-1,009k, median ~520k, so ONE stage-0 read (495k-654k)
# ate the old 500,000 whole. The one full walk (FlowWorks, stages 0-5 with two stage-1 retries) spent 3,729,543.
# Cap = 6 stages x the ~520k median stage + ~25% for retries, rounded: a normal walk stays under it, a walk stuck in
# retries goes over_budget. Reserve = the largest measured review charge (50,157), rounded up.
DEFAULT_CAP = 4000000
DEFAULT_RESERVE = 60000                 # kept back for checkpointing: no new run eats into it
LEGACY_CAPS = {500000: 50000}           # cap -> reserve of states made before the measurement: upgraded at load
CHARGE_KINDS = ("stage", "retry", "review", "helper", "consult", "unmeasured")
IMPL = ("present", "absent", "unknown")
PROOF = ("current", "stale", "missing", "exercised_unrecorded")
SCOPE = ("approved", "not_opened", "opened_by_owner", "open_question", "later", "out")
SPEAKERS = ("owner", "conductor", "agent")
OWNER_ONLY = ("root", "exam_waived", "floor_disable", "locked_change", "waiver", "his_words")
SOURCE = re.compile(r"(OWNER|CONDUCTOR):[0-9]+|ITEM:[A-Za-z0-9_]+|log\.md#L[0-9]+|[A-Za-z0-9_./-]+(:[0-9]+)?")
SCENE_KINDS = ("acceptance", "exploration", "interaction")
STAGED_BY = ("script", "hand", "mock")
HOLDS = ("immediate", "owner_review")
FLOOR_STATUS = ("applicable", "not_applicable", "disabled")
EVIDENCE_MODES = ("measured", "compressed", "decomposed", "inferred")
# a floor line that applies to every mod: there is always settings, a log, a load order, names, text and a test list
ALWAYS_APPLIES = ("mod_settings", "log", "load_order", "naming", "text", "test_isolation", "dlc", "worldgen",
                  "multiplayer")
EXAM_MIN, EXAM_PASS = 10, 0.9
# what each stage's accepted result freezes; a later change to any of them reopens that stage
# (record.json itself evolves every stage, so a stage freezes only the part it settled: stage 1 the root)
DEPS = {0: (), 1: ("root",), 2: ("root", "owner"), 3: ("root", "sheet", "tree", "scenes", "floor"),
        4: ("sheet", "tree", "scenes", "floor", "exam", "owner"), 5: ("tree", "sheet")}


class Refused(Exception):
    pass


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha_file(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def read_json(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except (OSError, ValueError) as e:
        raise Refused("%s does not parse: %s" % (os.path.basename(p), e))


def write_json(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, p)


# ---------------------------------------------------------------- manifest and packets

def load_manifest(path=MANIFEST):
    m = read_json(path)
    if not isinstance(m, dict) or any("stage_%d" % s not in m for s in STAGES):
        raise Refused("designer_manifest.json names no packet list for every stage 0-5")
    return m


def manifest_hashes(stage, path=MANIFEST):
    """{file: sha256} of the packet files the launcher injects for `stage`. A missing file refuses: a packet that
    cannot be supplied is not supplied quietly short."""
    out = {}
    for name in load_manifest(path)["stage_%d" % stage]:
        h = sha_file(os.path.join(os.path.dirname(path), name))
        if h is None:
            raise Refused("packet file %s for stage %d is missing" % (name, stage))
        out[name] = h
    return out


# ---------------------------------------------------------------- inputs and staleness

def owner_uncited(repo, item, d=None):
    """tsns of the OWNER.jsonl events naming this concept's item that neither record.json nor tree.json cites yet:
    his words not yet taken in. A reply he gives adds one; the Designer citing it (OWNER:<tsn>) takes it out again,
    so recording his answer inside a run is not a change underneath that run. None = the shard is unreadable."""
    if not item:
        return None
    lines = CT.owner_lines(repo, clone_of(d))     # working trees AND origin/main: a stale clone is not his silence
    if lines is None:
        return None
    tsns = []
    for ln in lines:
        if item not in ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("tsn"):
            tsns.append(str(ev["tsn"]))
    cited = ""
    for name in ("record.json", "tree.json"):
        try:
            with open(os.path.join(d or "", name), encoding="utf-8", errors="replace") as f:
                cited += f.read()
        except OSError:
            pass
    return sorted(t for t in tsns if not re.search(r"OWNER:%s(?![0-9])" % re.escape(t), cited))


def clone_of(d):
    """The clone a concept folder lives in (the Designer writes in its own clone, the Dispatcher judges from another),
    or None: the nearest parent holding the ledger's events folder."""
    p = os.path.abspath(d) if d else None
    while p and os.path.dirname(p) != p:
        if os.path.isdir(os.path.join(p, os.path.dirname(CT.OWNER_SHARD))):
            return p
        p = os.path.dirname(p)
    return None


def owner_feed(repo, item, d=None):
    """sha of owner_uncited: what the stages that depend on his words freeze."""
    return _feed_of(owner_uncited(repo, item, d))


def _feed_of(u):
    return None if u is None else hashlib.sha256(",".join(u).encode("utf-8")).hexdigest()


def inputs(d, st, repo=REPO):
    """The current hash of every input a stage can depend on (None = absent). tree.json by its tree hash, so the
    coverage judge's signature (coverage) does not count as a change."""
    try:
        tree = CT.load(d)
        th = CT.tree_hash(tree) if isinstance(tree, dict) else sha_file(os.path.join(d, "tree.json"))
    except FileNotFoundError:
        th = None
    except ValueError:
        th = sha_file(os.path.join(d, "tree.json"))
    try:
        rec = read_json(os.path.join(d, "record.json"))
        root = CT.sha(rec.get("root")) if isinstance(rec, dict) and rec.get("root") is not None else None
    except Refused:
        root = sha_file(os.path.join(d, "record.json"))
    return {"root": root, "sheet": sha_file(os.path.join(d, "sheet.md")),
            "tree": th, "scenes": sha_file(os.path.join(d, "scenes.json")),
            "floor": sha_file(os.path.join(d, "floor.json")), "exam": sha_file(os.path.join(d, "exam.json")),
            "owner": owner_feed(repo, st.get("item"), d)}


def stale_stage(d, st, repo=REPO):
    """(earliest stage whose accepted result no longer matches its inputs, [changed input names]) or (None, [])."""
    cur = inputs(d, st, repo)
    for r in sorted(accepted(st), key=lambda r: r["stage"]):
        changed = [k for k in DEPS[r["stage"]] if r["inputs"].get(k) != cur.get(k)]
        if changed:
            return r["stage"], changed
    return None, []


def accepted(st):
    """The latest accepted `done` result per stage below the current stage."""
    last = {}
    for r in st.get("results") or []:
        if r.get("outcome") == "done":
            last[r["stage"]] = r
    return [r for s, r in last.items() if s < st.get("stage", 0) or st.get("status") == "locked"]


def reopen_if_stale(d, st, repo=REPO):
    if st.get("status") == "locked":
        return None          # a locked tree changes on his word only: open_run refuses it, status reports the drift
    s, changed = stale_stage(d, st, repo)
    if s is None:
        return None
    to = s
    if to >= st["stage"]:
        return None
    why = "inputs changed since stage %d was accepted: %s; back to stage %d" % (s, ", ".join(changed), to)
    if "owner" in changed:
        frozen = next((r.get("owner_uncited") for r in accepted(st) if r["stage"] == s), None) or []
        new = sorted(set(owner_uncited(repo, st.get("item"), d) or []) - set(frozen))
        st["must_cite"] = sorted(set(st.get("must_cite") or []) | set(new))
        why += " (his new words to take in: %s)" % ", ".join("OWNER:" + t for t in new)
    st["stage"], st["status"] = to, "ready"
    st["results"] = [r for r in st["results"] if not (r.get("outcome") == "done" and r["stage"] >= to)] + \
        [{"stage": to, "outcome": "invalidated", "at": now_iso(), "why": why}]
    hist(st, "invalidated", why)
    return why


def hist(st, what, why):
    st.setdefault("history", []).append({"at": now_iso(), "what": what, "why": why, "stage": st.get("stage")})


# ---------------------------------------------------------------- the working record

def source_errors(src, where, repo, owner_ev):
    errs = []
    srcs = src if isinstance(src, list) else [src]
    if not srcs or not all(isinstance(s, str) and s.strip() for s in srcs):
        return ["%s: no source (every entry links to where it came from)" % where]
    for s in srcs:
        if not SOURCE.fullmatch(s.strip()):
            errs.append("%s: source %r is not OWNER:<tsn>, CONDUCTOR:<tsn>, ITEM:<id>, log.md#L<n> or a repo path" % (
                where, s))
        elif s.startswith("OWNER:") and owner_ev is not None and s[6:] not in owner_ev:
            errs.append("%s: %s finds no event in OWNER.jsonl" % (where, s))
        elif not s.startswith(("OWNER:", "CONDUCTOR:", "ITEM:", "log.md#")):
            path = s.split(":")[0]
            if not os.path.exists(os.path.join(repo, path)):
                errs.append("%s: source path %s does not exist" % (where, path))
    return errs


def authority_errors(e, where, owner_ev):
    """Who said it, and may they. Conductor text is never stored as his quotation; owner-only kinds need his words."""
    errs = []
    sp = e.get("speaker", "agent")
    if sp not in SPEAKERS:
        return ["%s: speaker %r is not one of %s" % (where, sp, "/".join(SPEAKERS))]
    srcs = e.get("source") if isinstance(e.get("source"), list) else [e.get("source")]
    owner_src = [s for s in srcs if isinstance(s, str) and s.startswith("OWNER:")]
    if sp == "owner" and not owner_src:
        errs.append("%s: speaker owner needs an OWNER:<tsn> source (Conductor text is never his quotation)" % where)
    if e.get("quote") and sp != "owner":
        errs.append("%s: a quotation is his words only; %s text is never quoted as his" % (where, sp))
    if e.get("kind") in OWNER_ONLY:
        if sp != "owner" or not owner_src:
            errs.append("%s: %s is owner-only (his words on an OWNER event), not %s; a Conductor instruction "
                        "(per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM) carries decisions, but this is a "
                        "quotation" % (where, e["kind"], sp))
        elif owner_ev is not None and e.get("words"):
            why = CT.his_words_problem(owner_ev, owner_src[0], e["words"])
            if why:
                errs.append("%s: %s" % (where, why))
    return errs


def record_errors(rec, repo=REPO, owner_ev=None):
    if not isinstance(rec, dict):
        return ["record.json is missing or not an object"]
    errs = []
    for sect in ("scope", "decisions", "asks", "inventory", "contradictions"):
        if not isinstance(rec.get(sect, []), list):
            errs.append("record.%s is not a list" % sect)
    if errs:
        return errs
    ids = set()
    for sect in ("scope", "decisions", "asks", "inventory", "contradictions"):
        for i, e in enumerate(rec.get(sect) or []):
            where = "%s[%s]" % (sect, e.get("id", i) if isinstance(e, dict) else i)
            if not isinstance(e, dict) or not CT.txt(e.get("id")):
                errs.append("%s: not an object with an id" % where)
                continue
            if e["id"] in ids:
                errs.append("%s: duplicate id" % where)
            ids.add(e["id"])
            errs += source_errors(e.get("source"), where, repo, owner_ev)
            errs += authority_errors(e, where, owner_ev)
    for e in [e for e in rec.get("inventory") or [] if isinstance(e, dict)]:
        errs += inventory_errors(e, repo, owner_ev)
    root = rec.get("root")
    if root is not None:
        if not isinstance(root, dict) or not CT.txt(root.get("text")):
            errs.append("root: needs text")
        else:
            errs += source_errors(root.get("source"), "root", repo, owner_ev)
            errs += authority_errors(dict(root, kind="root"), "root", owner_ev)
    return errs


def inventory_errors(e, repo, owner_ev):
    """Built, proven and scope are three fields, never one 'built' word."""
    w, errs = "inventory[%s]" % e.get("id"), []
    if e.get("impl") not in IMPL:
        errs.append("%s: impl %r is not one of %s" % (w, e.get("impl"), "/".join(IMPL)))
    if e.get("impl") == "absent" and not CT.txt(e.get("search_scope")):
        errs.append("%s: absent needs search_scope (what was searched; missing evidence is not absence)" % w)
    if e.get("impl") == "present" and not e.get("impl_evidence"):
        errs.append("%s: present needs impl_evidence (a path or item)" % w)
    if e.get("proof") not in PROOF:
        errs.append("%s: proof %r is not one of %s" % (w, e.get("proof"), "/".join(PROOF)))
    if e.get("proof") == "current" and not e.get("proof_evidence"):
        errs.append("%s: proof current needs proof_evidence" % w)
    if e.get("scope") not in SCOPE:
        errs.append("%s: scope %r is not one of %s" % (w, e.get("scope"), "/".join(SCOPE)))
    if e.get("scope") == "opened_by_owner" and not any(
            isinstance(s, str) and s.startswith("OWNER:") for s in lst(e.get("scope_source"))):
        errs.append("%s: opened_by_owner needs scope_source OWNER:<tsn> (only he opens a built thing's scope)" % w)
    return errs


def lst(v):
    return v if isinstance(v, list) else ([v] if v else [])


# ---------------------------------------------------------------- what is already built (stage 0 must account for it)

LIVE_PROOFS = os.path.join("infrastructure", "state", "live_proofs")


def done_items(repo):
    """{item id: title} of the ledger's done items, or None when the ledger cannot be read (UNMEASURED, never 'none
    built'). Only the real repo has a ledger model can fold; a test repo patches this function."""
    if os.path.realpath(repo) != os.path.realpath(REPO):
        return None
    try:
        import model  # noqa: E402  (rimflow's ledger fold, beside this file)
        w = model.replay(model.read())
    except Exception:  # an unreadable ledger is reported as UNMEASURED by the caller
        return None
    return {i: (getattr(it, "title", "") or "") for i, it in w.items.items() if it.state == "done"}


def mod_prefixes(mod, aliases=()):
    """Item-id subject prefixes that name the mod: its folder in capitals (alphanumerics only) and each alias."""
    out = []
    for n in [(mod or "").split("/")[-1]] + list(aliases or []):
        n = re.sub(r"[^A-Za-z0-9]", "", n or "").upper()
        if n and n + "_" not in out:
            out.append(n + "_")
    return out


def built_evidence(repo, mod, aliases=()):
    """-> (refs, notes). What stage 0 must account for before it is done: the mod's src/ tree, every done ledger item
    whose id starts with the mod's subject prefix, and every live proof (infrastructure/state/live_proofs/<ID>.txt)
    filed under that prefix or under one of those items. `notes` names what could not be read (UNMEASURED).
    Bounded on purpose: an item merely mentioning the mod in its title is listed in the packet, not required."""
    refs, notes = [], []
    folder = (mod or "").split("/")[-1]
    cands = [os.path.join("src", mod)] if "/" in (mod or "") else []
    try:
        cands += [os.path.join("src", t, folder) for t in sorted(os.listdir(os.path.join(repo, "src")))]
    except OSError:
        notes.append("src/ unreadable")
    cands.append(os.path.join("src", folder))
    for c in cands:
        if folder and os.path.isdir(os.path.join(repo, c)) and c.replace(os.sep, "/") not in refs:
            refs.append(c.replace(os.sep, "/"))
    prefixes = tuple(mod_prefixes(mod, aliases))
    done = done_items(repo)
    if done is None:
        notes.append("ledger UNMEASURED: done items not read")
        done = {}
    items = sorted(i for i in done if prefixes and i.upper().startswith(prefixes))
    refs += ["ITEM:%s" % i for i in items]
    try:
        names = sorted(os.listdir(os.path.join(repo, LIVE_PROOFS)))
    except OSError:
        names = []
    for n in names:
        stem, ext = os.path.splitext(n)
        if ext == ".txt" and (stem in items or (prefixes and stem.upper().startswith(prefixes))):
            refs.append("%s/%s" % (LIVE_PROOFS.replace(os.sep, "/"), n))
    return refs, notes


def related_titles(repo, mod, aliases=(), cap=40):
    """Done items naming the mod in their title but not by prefix: the packet lists them so stage 0 reads them."""
    done = done_items(repo) or {}
    prefixes = tuple(mod_prefixes(mod, aliases))
    keys = [p[:-1].lower() for p in prefixes]
    out = [(i, t) for i, t in sorted(done.items()) if not (prefixes and i.upper().startswith(prefixes))
           and any(k in re.sub(r"[^a-z0-9]", "", t.lower()) for k in keys if len(k) > 4)]
    return out[:cap], len(out)


def unaccounted(rec, refs):
    """refs stage 0 has not accounted for. A ref is accounted when an inventory entry mentions it (impl_evidence,
    proof_evidence, source, anywhere in the entry), or record.json `built_reviewed` lists it with `covered_by` (an
    inventory id) or `not_a_capability` (why)."""
    inv = [e for e in (rec or {}).get("inventory") or [] if isinstance(e, dict)]
    ids = {e.get("id") for e in inv}
    seen = json.dumps(inv)
    for r in (rec or {}).get("built_reviewed") or []:
        if isinstance(r, dict) and CT.txt(r.get("ref")) and (
                r.get("covered_by") in ids or CT.txt(r.get("not_a_capability"))):
            seen += "\n" + json.dumps(r["ref"])
    out = []
    for ref in refs:
        if not re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(ref.split(":", 1)[-1]), seen):
            out.append(ref)
    return out


def built_section(repo, st):
    refs, notes = built_evidence(repo, st.get("mod"), st.get("aliases"))
    rel, n = related_titles(repo, st.get("mod"), st.get("aliases"))
    out = ["", "## What is already built (designer_stage.py built_evidence)",
           "Stage 0 is not done until record.json accounts for each line below: an inventory entry that cites it, or "
           "`built_reviewed` [{\"ref\", \"covered_by\": <inventory id> | \"not_a_capability\": <why>}]. Never ask "
           "him whether to keep any of it."]
    out += ["- %s" % r for r in refs] or ["- (nothing found under the mod's src/ tree, prefix or live proofs)"]
    out += ["UNMEASURED: %s" % x for x in notes]
    if rel:
        out += ["Done items naming the mod in their title (read; not required): %d%s" % (
            n, "" if n <= len(rel) else ", first %d" % len(rel))]
        out += ["- %s: %s" % (i, t) for i, t in rel]
    return out


# An ask that puts a thing up for keeping or removal, whatever its offers_removal flag says (owner 2026-11-02, GSS
# sitting 1 asked whether to keep poles, styles and save removal: *"Those were very strange questions given we already
# have these capabilities."*). A false hit is cheap: name the inventory entry, or ask about behaviour instead.
KEEP_REMOVE = re.compile(r"\b(keep|kept|remove|removal|removing|drop|dropping|cut|delete|deleting|retire|scrap|"
                         r"get rid of|do away with|still (want|need)|(do|should) (we|you|i) (need|want|have|bother)|"
                         r"worth keeping|necessary)\b", re.I)


def keep_or_remove(text):
    return bool(CT.txt(text) and KEEP_REMOVE.search(text))


def ask_errors(ask, rec):
    """An ask that may reach him. Cites the decision it settles and its evidence; never offers to remove or shrink a
    present capability unless he opened that scope; carries a structured review by someone other than its author."""
    w = "ask[%s]" % ask.get("id")
    errs = []
    if not CT.txt(ask.get("text")):
        errs.append("%s: no text" % w)
    if not CT.txt(ask.get("decision")):
        errs.append("%s: names no unresolved decision it settles" % w)
    inv = {e.get("id"): e for e in rec.get("inventory") or [] if isinstance(e, dict)}
    about = lst(ask.get("about"))
    if not about and not lst(ask.get("owner_cites")):
        errs.append("%s: cites neither an inventory entry nor his statements" % w)
    for a in about:
        e = inv.get(a)
        if e is None:
            errs.append("%s: about %s is not in the inventory" % (w, a))
        elif (ask.get("offers_removal") or keep_or_remove(ask.get("text"))) and e.get("impl") == "present" \
                and e.get("scope") != "opened_by_owner":
            errs.append("%s: offers to remove or shrink %s, which is built and whose scope he has not opened; ask what "
                        "correct behaviour is, or how to show it, instead" % (w, a))
    if not about and keep_or_remove(ask.get("text")):
        errs.append("%s: asks whether to keep or remove something without naming its inventory entry (about); "
                    "find out first whether it is already built" % w)
    rv = ask.get("review")
    if not isinstance(rv, dict) or rv.get("verdict") not in ("pass", "struck"):
        errs.append("%s: no structured review result (verdict pass|struck)" % w)
    elif not CT.txt(rv.get("by")) or rv.get("by") == ask.get("author"):
        errs.append("%s: reviewed by its own author" % w)
    elif rv.get("verdict") == "struck":
        errs.append("%s: struck by review (%s): it does not go to him" % (w, rv.get("why") or "no reason"))
    return errs


# ---------------------------------------------------------------- scenes and floor

def entry_point_exists(repo, ep):
    if not isinstance(ep, str) or "::" not in ep:
        return False
    path, name = ep.split("::", 1)
    p = os.path.join(repo, path)
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return False
    return bool(name) and re.search(r"\bdef\s+%s\b|['\"]%s['\"]" % (re.escape(name), re.escape(name)), text) is not None


def scene_errors(sc, tree=None, repo=REPO):
    if not isinstance(sc, dict) or not isinstance(sc.get("scenes"), list):
        return ["scenes.json is missing or has no scenes list"]
    errs, leaves = [], None
    if isinstance(tree, dict):
        leaves = {x.get("id") for x in CT.lst(tree.get("leaves")) if isinstance(x, dict)}
    own = {}
    for i, s in enumerate(sc["scenes"]):
        w = "scene[%s]" % (s.get("id", i) if isinstance(s, dict) else i)
        if not isinstance(s, dict) or not CT.txt(s.get("id")):
            errs.append("%s: not an object with an id" % w)
            continue
        if s.get("kind") not in SCENE_KINDS:
            errs.append("%s: kind %r is not one of %s" % (w, s.get("kind"), "/".join(SCENE_KINDS)))
            continue
        if s.get("staged_by") not in STAGED_BY:
            errs.append("%s: staged_by %r is not one of %s" % (w, s.get("staged_by"), "/".join(STAGED_BY)))
        if s["kind"] == "exploration":
            if not CT.txt(s.get("question")):
                errs.append("%s: an exploration scene names the question it explores" % w)
            continue
        if s.get("staged_by") != "script":
            errs.append("%s: a %s staged scene is exploration; it never accepts a leaf, however it is labelled" % (
                w, s.get("staged_by")))
        if not entry_point_exists(repo, s.get("entry_point")):
            if not CT.txt(s.get("entry_point_item")):
                errs.append("%s: entry_point %r is not in the proof script; file its implementation "
                            "(entry_point_item) before scheduling the review" % (w, s.get("entry_point")))
        for k in ("action", "expect", "restore"):
            if not CT.txt(s.get(k)):
                errs.append("%s: no %s" % (w, k))
        if not [c for c in lst(s.get("start")) if CT.txt(c)]:
            errs.append("%s: no asserted starting conditions (start)" % w)
        c = s.get("control")
        if not isinstance(c, dict) or not all(CT.txt(c.get(k)) for k in ("case", "expect", "rules_out")):
            errs.append("%s: control needs case, expect (the rejection or absence that passes) and rules_out (the "
                        "plausible alternative it excludes)" % w)
        if s.get("hold") not in HOLDS:
            errs.append("%s: hold %r is not one of %s" % (w, s.get("hold"), "/".join(HOLDS)))
        reqs = lst(s.get("requirement")) if s["kind"] == "acceptance" else lst(s.get("features"))
        if not reqs:
            errs.append("%s: %s" % (w, "no requirement (leaf id)" if s["kind"] == "acceptance"
                                     else "an interaction scene names the features (leaf ids) it joins"))
        if s["kind"] == "interaction" and len(reqs) < 2:
            errs.append("%s: an interaction scene joins two or more features" % w)
        if leaves is not None:
            for r in reqs:
                if r not in leaves:
                    errs.append("%s: %s is not a leaf of the tree" % (w, r))
        if s["kind"] == "acceptance":
            for r in reqs:
                own.setdefault(r, []).append(s["id"])
    for s in [s for s in sc["scenes"] if isinstance(s, dict) and s.get("kind") == "interaction"]:
        for f in lst(s.get("features")):
            if f not in own:
                errs.append("scene[%s]: feature %s has no acceptance scene of its own; an interaction scene never "
                            "stands in for one" % (s["id"], f))
    if isinstance(tree, dict):
        for x in [x for x in CT.lst(tree.get("leaves")) if isinstance(x, dict)]:
            if x.get("leaf_kind") in ("experience", "walk") and x.get("tier_proposed") not in (None, "offline") \
                    and x.get("id") not in own:
                errs.append("leaf %s: a %s leaf off the offline tier has no acceptance scene" % (
                    x.get("id"), x.get("leaf_kind")))
    return errs


# ---------------------------------------------------------------- the showcase set
# Owner, 2026-11-05: several showcases, as orthogonal as possible; each later one features ONLY very different
# functionality, until efficient coverage is had. Doctrine: roles/designer_scene_contract.md "The showcase set".

SHOWCASE_RULES = os.path.join(HERE, "showcase_rules.json")
UNIT_SCOPES = ("approved", "opened_by_owner")


def load_showcase_rules(path=None):
    path = path or SHOWCASE_RULES
    r = read_json(path)
    if not isinstance(r, dict):
        raise Refused("%s is missing or not an object" % path)
    mo, mn = r.get("max_overlap"), r.get("min_new_after_first")
    if isinstance(mo, bool) or not isinstance(mo, (int, float)) or not 0 <= mo < 1 \
            or isinstance(mn, bool) or not isinstance(mn, int) or mn < 1:
        raise Refused("%s needs max_overlap in [0, 1) and min_new_after_first >= 1" % path)
    return r


def coverage_units(rec):
    """The capabilities a showcase set must account for: every built inventory entry (whatever its scope: a built
    thing scoped out still ships until removed) and every unbuilt one in scope."""
    out = []
    for e in lst((rec if isinstance(rec, dict) else {}).get("inventory")):
        if not isinstance(e, dict) or not CT.txt(e.get("id")):
            continue
        if e.get("impl") == "present" or e.get("scope") in UNIT_SCOPES:
            out.append(e["id"])
    return out


def out_units(rec):
    return {CT.txt(e.get("id")) for e in lst((rec if isinstance(rec, dict) else {}).get("inventory"))
            if isinstance(e, dict) and e.get("scope") == "out"}


def showcase_table(sc, rec, tree=None, owner_ev=None, repo=REPO, rules=None):
    """-> (rows, errs). One row per showcase in order: new-coverage count, overlap share and the overlapped units;
    errs = why the showcase set cannot be accepted. The program checks what is countable (coverage, overlap, order,
    the stop criterion); whether a showcase's functionality is 'very different' in play is the reviewer's to read."""
    rules = rules or load_showcase_rules()
    limit, min_new = rules["max_overlap"], rules["min_new_after_first"]
    units = coverage_units(rec)
    uset, scoped_out = set(units), out_units(rec)
    decisions = {CT.txt(x.get("id")): x for x in lst((rec if isinstance(rec, dict) else {}).get("decisions"))
                 if isinstance(x, dict)}
    errs, rows = [], []
    if not isinstance(sc, dict):
        return rows, ["scenes.json is missing, so no showcase set"]
    if not isinstance(rec, dict) or not isinstance(rec.get("inventory"), list):
        # coverage is counted against the inventory: no readable inventory, no claim of coverage (an explicit empty
        # list is a real, readable inventory; an omitted one is not)
        return rows, ["record.json is missing or its inventory is absent or not a list, so coverage cannot be counted"]
    # a unit is decided by impl and scope: an entry without a readable id, impl and scope cannot be counted in or out
    unread = [str(i) for i, e in enumerate(rec["inventory"]) if not isinstance(e, dict) or not CT.txt(e.get("id"))
              or e.get("impl") not in IMPL or e.get("scope") not in SCOPE]
    if unread:
        return rows, ["record.json inventory entr%s %s need%s an id, impl (%s) and scope (%s), so coverage cannot be "
                      "counted" % ("y" if len(unread) == 1 else "ies", ", ".join(unread),
                                   "s" if len(unread) == 1 else "", "/".join(IMPL), "/".join(SCOPE))]
    scenes = {s.get("id") for s in lst(sc.get("scenes")) if isinstance(s, dict) and CT.txt(s.get("id"))}
    leaves = {CT.txt(x.get("id")) for x in CT.lst((tree or {}).get("leaves")) if isinstance(x, dict)} \
        if isinstance(tree, dict) else set()
    shows = sc.get("showcases")
    if not isinstance(shows, list) or not shows:
        if set(units) - scoped_out:
            errs.append("scenes.json names no showcases: the mod's face is an ordered list, showcase 1 his pick")
        shows = []
    seen = set()
    for i, s in enumerate(shows):
        w = "showcase[%s]" % (s.get("id", i + 1) if isinstance(s, dict) else i + 1)
        if not isinstance(s, dict) or not CT.txt(s.get("id")):
            errs.append("%s: not an object with an id" % w)
            continue
        refs = [r for r in lst(s.get("scenes")) if CT.txt(r)]
        if not refs:
            errs.append("%s: names no scenes (the scenes.json scene ids it is staged by)" % w)
        for r in refs:
            if r not in scenes:
                errs.append("%s: scene %s is not in scenes.json" % (w, r))
        if any(not CT.txt(u) for u in lst(s.get("exercises"))):
            errs.append("%s: exercises holds an entry that is not an inventory id (text)" % w)
        ex = [u for u in lst(s.get("exercises")) if CT.txt(u)]
        if len(set(ex)) != len(ex):
            errs.append("%s: exercises lists a capability twice" % w)
        ex = list(dict.fromkeys(ex))
        if not ex:
            errs.append("%s: exercises names no capability" % w)
        for u in ex:
            if u not in uset:
                errs.append("%s: exercises %s, which is not a built or in-scope inventory capability" % (w, u))
            elif u in scoped_out:
                errs.append("%s: exercises %s, which is scoped out: list it in coverage_rest (the check that covers "
                            "it until removal), never in a showcase" % (w, u))
        ex = [u for u in ex if u in uset]
        new = [u for u in ex if u not in seen]
        over = [u for u in ex if u in seen]
        share = (float(len(over)) / len(ex)) if ex else 0.0
        if i == 0:
            src = [x for x in lst(s.get("source")) if isinstance(x, str) and x.startswith("OWNER:")]
            dec = decisions.get(CT.txt(s.get("decision"))) or {}
            dsrc = [x for x in lst(dec.get("source")) if isinstance(x, str)]
            if not src:
                errs.append("%s: showcase 1 is the flagship he picked; source needs his OWNER:<tsn>" % w)
            else:
                errs += source_errors(src, w, repo, owner_ev)
            # binds his words to THIS showcase: the record.json decision (speaker owner) whose `flagship` field
            # names this showcase id and cites the same event. A root approval, or any owner decision that does
            # not name this showcase as his flagship, is not his pick.
            if dec.get("speaker") != "owner" or not set(src) & set(dsrc) or dec.get("flagship") != s["id"]:
                errs.append("%s: showcase 1 names no record.json decision (decision) of his picking it: an owner "
                            "decision with flagship: \"%s\" that cites the same OWNER event" % (w, s["id"]))
        else:
            if len(new) < min_new:
                errs.append("%s: newly exercises %d capabilit%s, under min_new_after_first %d; those belong in "
                            "coverage_rest as ordinary scene/leaf checks" % (w, len(new), "y" if len(new) == 1 else
                                                                             "ies", min_new))
            # greedy over the chosen set: when this one was picked, no later showcase offered more new coverage
            for j, t in enumerate(shows[i + 1:], i + 2):
                if isinstance(t, dict):
                    tn = len({u for u in lst(t.get("exercises")) if CT.txt(u) and u in uset} - seen)
                    if tn > len(new):
                        errs.append("%s: newly exercises %d, but showcase %d (%s) would have added %d here: the order "
                                    "is not greedy (most new coverage first)" % (w, len(new), j, t.get("id"), tn))
            if share > limit:
                why = s.get("overlap_why") if isinstance(s.get("overlap_why"), dict) else {}
                bare = [u for u in over if not CT.txt(why.get(u))]
                if bare:
                    errs.append("%s: overlap %.2f with earlier showcases is over the limit %.2f and %s ha%s no staging "
                                "reason in overlap_why" % (w, share, limit, ", ".join(bare),
                                                           "s" if len(bare) == 1 else "ve"))
        rows.append({"id": s["id"], "order": i + 1, "exercises": len(ex), "new": len(new), "overlap": round(share, 3),
                     "overlapped": over})
        seen.update(ex)
    rest = {}
    for i, c in enumerate(lst(sc.get("coverage_rest"))):
        w = "coverage_rest[%s]" % (c.get("capability", i) if isinstance(c, dict) else i)
        if not isinstance(c, dict) or not CT.txt(c.get("capability")):
            errs.append("%s: not an object with a capability" % w)
            continue
        u = c["capability"]
        if u not in uset:
            errs.append("%s: %s is not a built or in-scope inventory capability" % (w, u))
        elif u in seen:
            errs.append("%s: a showcase already exercises %s; coverage_rest lists only the rest" % (w, u))
        by = [b for b in lst(c.get("by")) if CT.txt(b)]
        if not by:
            errs.append("%s: by names no scene or leaf that checks it" % w)
        for b in by:
            if b not in scenes and b not in leaves:
                errs.append("%s: by %s is neither a scenes.json scene nor a tree leaf" % (w, b))
        if not CT.txt(c.get("why")):
            errs.append("%s: no why (why an ordinary check is the cheaper cover)" % w)
        rest[u] = by
    bare = [u for u in units if u not in seen and u not in rest]
    if bare:
        errs.append("coverage: %d capabilit%s exercised by no showcase and no scene: %s (a showcase or a "
                    "coverage_rest entry each; none is silently uncovered)" % (
                        len(bare), "y is" if len(bare) == 1 else "ies are", ", ".join(bare)))
    return rows, errs


def showcase_check(sc, rec, tree, owner_ev, repo=REPO, rules=None):
    """showcase_table's errs; an unreadable rules file is a refusal reason, never a pass."""
    try:
        return showcase_table(sc, rec, tree, owner_ev, repo, rules)[1]
    except Refused as e:
        return [str(e)]


def floor_errors(fl, tree=None, floor=None, owner_ev=None):
    floor = floor or CT.load_floor()[0]
    if not isinstance(fl, dict) or not isinstance(fl.get("lines"), dict):
        return ["floor.json is missing or has no lines object"]
    errs, lines = [], fl["lines"]
    byid = {ln["id"]: ln for ln in floor["lines"]}
    for k in lines:
        if k not in byid:
            errs.append("floor.json: %s is not a floor line" % k)
    off = {}
    if isinstance(tree, dict) and isinstance(tree.get("floor"), dict):
        off = {o.get("line"): o for o in CT.lst(tree["floor"].get("off")) if isinstance(o, dict)}
    for lid, ln in byid.items():
        e = lines.get(lid)
        w = "floor[%s]" % lid
        if not isinstance(e, dict):
            errs.append("%s: no status (applicable, not_applicable with evidence, or disabled)" % w)
            continue
        st = e.get("status")
        if st not in FLOOR_STATUS:
            errs.append("%s: status %r is not one of %s" % (w, st, "/".join(FLOOR_STATUS)))
        elif st == "not_applicable":
            if lid in ALWAYS_APPLIES:
                errs.append("%s: applies to every mod; it cannot be not_applicable" % w)
            elif not CT.txt(e.get("evidence")):
                errs.append("%s: not_applicable needs evidence that the object or behaviour does not exist" % w)
        elif st == "disabled":
            if ln.get("waivable") is False:
                errs.append("%s: a standing ruling cannot be disabled" % w)
            elif lid not in off:
                errs.append("%s: disabled with no matching floor.off in tree.json (his words)" % w)
            elif owner_ev is not None:
                why = CT.his_words_problem(owner_ev, off[lid].get("ref"), off[lid].get("words"))
                if why:
                    errs.append("%s: %s" % (w, why))
        elif st == "applicable" and ln.get("class") == "numeric":
            if e.get("evidence_mode", "measured") not in EVIDENCE_MODES:
                errs.append("%s: evidence_mode %r is not one of %s" % (w, e.get("evidence_mode"), "/".join(EVIDENCE_MODES)))
            if e.get("evidence_mode") in ("compressed", "decomposed", "inferred") and not CT.txt(e.get("establishes")):
                errs.append("%s: a %s run says which properties it establishes and which stay inferred" % (
                    w, e.get("evidence_mode")))
        if st != "disabled" and lid in off:
            errs.append("%s: tree.json floor.off names it but floor.json says %s" % (w, st))
    return errs


def exam_errors(ex, d, st, repo=REPO):
    try:
        tree = CT.load(d)
    except (FileNotFoundError, ValueError):
        tree = None
    if isinstance(tree, dict) and isinstance(tree.get("exam_waived"), dict) and tree["exam_waived"]:
        return []        # his words, checked by the gate (concept_tree.gate)
    if not isinstance(ex, dict):
        return ["no exam.json and no exam_waived"]
    errs = []
    sc = ex.get("scenarios")
    if not isinstance(sc, list) or len(sc) < EXAM_MIN:
        errs.append("exam: fewer than %d frozen scenarios" % EXAM_MIN)
        sc = sc if isinstance(sc, list) else []
    if ex.get("scenarios_hash") != CT.sha(sc):
        errs.append("exam: scenarios_hash does not match the scenarios (frozen before the readers saw them)")
    for i, s in enumerate(sc):
        if not isinstance(s, dict) or not CT.txt(s.get("expect")) or not CT.txt(s.get("expect_source")):
            errs.append("exam: scenario %d needs expect and expect_source (a leaf id or OWNER:<tsn>)" % i)
    cur = inputs(d, st, repo)
    fr = ex.get("inputs") if isinstance(ex.get("inputs"), dict) else {}
    for k in ("tree", "sheet"):
        if fr.get(k) != cur.get(k):
            errs.append("exam: run against another %s than the current one; rerun it" % k)
    score = ex.get("score") if isinstance(ex.get("score"), dict) else {}
    right, total = score.get("right"), score.get("total")
    if not (isinstance(right, int) and isinstance(total, int) and total >= EXAM_MIN and total == len(sc)):
        errs.append("exam: score needs right and total, total = the number of scenarios")
    elif right < EXAM_PASS * total:
        errs.append("exam: %d/%d is under %d%%" % (right, total, EXAM_PASS * 100))
    if ex.get("accept_where_reject_core") != 0:
        errs.append("exam: accept_where_reject_core must be 0")
    if not CT.txt(ex.get("examiner")) or ex.get("examiner") == ex.get("author"):
        errs.append("exam: the examiner is not the tree's author")
    for m in lst(ex.get("challenger_misses")):
        if not isinstance(m, dict) or not CT.txt(m.get("accounted")):
            errs.append("exam: every challenger miss is accounted for")
    # designer_exam.md step 5: a Reader on a copy with a core leaf removed must MISS, or the scenarios do not
    # discriminate (EXAM_CONTROL_ENFORCE_FOUR_NEVER_MISSED: four controls never missed and the gate still passed)
    ctl = ex.get("control")
    if not isinstance(ctl, dict) or not CT.txt(ctl.get("broken_leaf")):
        errs.append("exam: control needs broken_leaf, the core leaf removed for the control Reader")
    else:
        leaves = tree.get("leaves") if isinstance(tree, dict) else None
        ids = {x["id"] for x in (leaves if isinstance(leaves, list) else [])
               if isinstance(x, dict) and isinstance(x.get("id"), str)}
        if ctl.get("broken_leaf") not in ids:
            errs.append("exam: control broken_leaf %r is not a leaf of the tree" % ctl.get("broken_leaf"))
        if ctl.get("missed") is not True:
            errs.append("exam: the control Reader did not miss (missed must be true): the scenarios do not "
                        "discriminate; write scenarios the broken tree gets wrong and refreeze")
    return errs


# ---------------------------------------------------------------- results

def result_errors(res, d, st, repo=REPO):
    """Why this run's result.json cannot be accepted, or []."""
    if not isinstance(res, dict):
        return ["no result.json (a closing message is not a result)"]
    out, stage = res.get("outcome"), st["stage"]
    if res.get("stage") != stage:
        return ["result is for stage %r; the state is at stage %d" % (res.get("stage"), stage)]
    if res.get("run") != (st.get("running") or {}).get("run"):
        return ["result names run %r, not the open run %r" % (res.get("run"), (st.get("running") or {}).get("run"))]
    if out not in OUTCOMES:
        return ["outcome %r is not one of %s" % (out, "/".join(OUTCOMES))]
    owner_ev = CT.owner_events(repo, clone_of(d))
    rec = read_json(os.path.join(d, "record.json"))
    if out == "blocked":
        return [] if CT.txt(res.get("on")) else ["blocked names no dependency (on)"]
    if out == "return":
        to = res.get("to")
        if not (isinstance(to, int) and 0 <= to < stage):
            return ["return needs `to`, an earlier stage"]
        if not CT.txt(res.get("decision")):
            return ["return names no missing decision"]
        if stage > 2 and to < 2 and res.get("question"):
            return ["an owner question returns to stage 2, not %d" % to]
        return []
    errs = record_errors(rec, repo, owner_ev)
    if out == "waiting_owner":
        if stage not in DIALOGUE:
            return ["only stages 1-2 send him questions; stage %d returns to stage 2 with the question" % stage]
        sent = [a for a in (rec or {}).get("asks") or [] if isinstance(a, dict) and a.get("status") == "sent"]
        if not sent:
            errs.append("waiting_owner with no ask in status sent")
        for a in sent:
            errs += ask_errors(a, rec)
        return errs
    # done
    if stage == 0:
        if not (rec or {}).get("inventory"):
            errs.append("stage 0: no inventory")
        refs, notes = built_evidence(repo, st.get("mod"), st.get("aliases"))
        errs += ["stage 0: what is built could not be read (%s): not done until it can be (end blocked)" % x
                 for x in notes]
        miss = unaccounted(rec, refs)
        if miss:
            errs.append("stage 0: %d built thing(s) not accounted for in the inventory or built_reviewed: %s%s" % (
                len(miss), ", ".join(miss[:15]), "" if len(miss) <= 15 else ", ..."))
        if len([x for x in lst((rec or {}).get("failure_modes")) if CT.txt(x)]) < 3:
            errs.append("stage 0: name the three ways this mod could fail him (failure_modes)")
    elif stage == 1:
        if not isinstance((rec or {}).get("root"), dict):
            errs.append("stage 1: no root his words approve")
    elif stage == 2:
        left = set(st.get("must_cite") or []) & set(owner_uncited(repo, st.get("item"), d) or [])
        if left:
            errs.append("stage 2: his words that reopened it are not taken in yet: cite %s in record.json" % ", ".join(
                "OWNER:" + t for t in sorted(left)))
        for a in (rec or {}).get("asks") or []:
            if isinstance(a, dict) and a.get("status") == "sent":
                errs.append("stage 2: ask %s has no answer; silence never advances" % a.get("id"))
        for c in (rec or {}).get("contradictions") or []:
            if isinstance(c, dict) and c.get("core") and not c.get("resolved"):
                errs.append("stage 2: core contradiction %s is unresolved" % c.get("id"))
    elif stage == 3:
        lint_errs, _ = CT.lint(d, repo)
        errs += ["lint: %s" % e for e in lint_errs]
        tree = CT.load(d) if not lint_errs else None
        errs += scene_errors(read_json(os.path.join(d, "scenes.json")), tree, repo)
        errs += ["showcases: %s" % e for e in showcase_check(read_json(os.path.join(d, "scenes.json")), rec, tree,
                                                              owner_ev, repo)]
        errs += floor_errors(read_json(os.path.join(d, "floor.json")), tree, owner_ev=owner_ev)
    elif stage == 4:
        errs += exam_errors(read_json(os.path.join(d, "exam.json")), d, st, repo)
    elif stage == 5:
        gate_errs, _ = CT.gate(d, repo)
        errs += ["gate: %s" % e for e in gate_errs]
        # the lock refuses while a capability is exercised by no showcase and no scene (record.json can move after
        # stage 3: an inventory line added since then is caught here)
        try:
            tree = CT.load(d)
        except (FileNotFoundError, ValueError):
            tree = None
        sc5 = read_json(os.path.join(d, "scenes.json"))
        # the showcase set names scenes, so the scenes it leans on must still meet the contract at the lock (a scene
        # added after stage 3 is checked here, not trusted by its id)
        errs += ["scenes: %s" % e for e in scene_errors(sc5, tree, repo)]
        errs += ["showcases: %s" % e for e in showcase_check(sc5, rec, tree, owner_ev, repo)]
    return errs


# ---------------------------------------------------------------- the launcher's verbs

def state_path(d):
    return os.path.join(d, "stage.json")


def load_state(d):
    st = read_json(state_path(d))
    if not isinstance(st, dict):
        raise Refused("no stage.json in %s (designer_stage.py init)" % d)
    upgrade_cap(st)
    return st


def upgrade_cap(st):
    """A state still on a legacy default (LEGACY_CAPS: the 500,000 one stage-0 read spent) takes the measured
    defaults; the next write keeps it. A cap set by hand (any other value) is left alone. -> True when upgraded."""
    b = st.get("budget") or {}
    if b.get("cap") in LEGACY_CAPS and b.get("reserve") == LEGACY_CAPS[b["cap"]]:
        hist(st, "cap_reset", "legacy cap %d (reserve %d) -> measured %d (reserve %d); %d spent" % (
            b["cap"], b["reserve"], DEFAULT_CAP, DEFAULT_RESERVE, b.get("spent", 0)))
        b["cap"], b["reserve"] = DEFAULT_CAP, DEFAULT_RESERVE
        return True
    return False


def spend_by_stage(st):
    """Pure. -> {stage: {"total": weighted tokens, "runs": stage/retry/unmeasured charges, "other": review/helper/
    consult}} from the state's charges: the measurement the cap is set from."""
    out = {}
    for c in (st.get("budget") or {}).get("charges") or []:
        row = out.setdefault(c.get("stage"), {"total": 0, "runs": 0, "other": 0})
        row["total"] += c.get("tokens") or 0
        row["runs" if c.get("kind") in ("stage", "retry", "unmeasured") else "other"] += c.get("tokens") or 0
    return out


def init(d, mod, item=None, cap=DEFAULT_CAP, reserve=DEFAULT_RESERVE, aliases=()):
    if os.path.exists(state_path(d)):
        raise Refused("stage.json already exists in %s" % d)
    if not (0 < reserve < cap):
        raise Refused("reserve must be above 0 and below the cap")
    os.makedirs(d, exist_ok=True)
    st = {"schema": 1, "mod": mod, "item": item, "aliases": list(aliases or []), "stage": 0, "status": "ready",
          "budget": {"cap": cap, "reserve": reserve, "spent": 0, "charges": []},
          "running": None, "results": [], "recovery": [], "history": []}
    hist(st, "init", "stage 0, budget %d (reserve %d)" % (cap, reserve))
    write_json(state_path(d), st)
    return st


def remaining(st):
    b = st["budget"]
    return b["cap"] - b["spent"]


def open_run(d, run, run_cap=None, repo=REPO, manifest=MANIFEST, commit=True):
    """-> (packet text, this run's budget). Refuses (Refused) when a scene's
    recovery is open, the concept is locked, or it waits on him or a dependency. commit=False is the launcher's
    preview (its decide step): the same checks and packet, nothing written."""
    st = load_state(d)
    if st.get("running"):
        # the last run never closed: it is a retry now, and what it reserved is charged (conservative)
        prev = st["running"]
        charge_state(st, prev.get("reserved", 0), "unmeasured", "run %s never closed" % prev.get("run"))
        hist(st, "retry", "run %s never closed; its reservation %d is charged" % (prev.get("run"), prev.get("reserved", 0)))
        st["running"] = None
    why = reopen_if_stale(d, st, repo)
    try:
        if st.get("status") == "locked":
            raise Refused("LOCKED: changing a locked tree is his word only (an amendment comes back as a new concept)")
        if st.get("status") == "blocked":
            raise Refused("BLOCKED on %s: nothing runs until it ends (clear it with `unblock`)" % st.get("blocked_on"))
        if st.get("status") == "waiting_owner" and not owner_moved(st, d, repo):
            raise Refused("WAITING_OWNER: no new owner event since the asks went out; silence never advances")
        opn = [r for r in st.get("recovery") or [] if r.get("state") == "open"]
        if opn:
            raise Refused("RECOVERY_PENDING: scene(s) %s changed persistent state and never restored; restore them "
                          "(scene-end) before any further work" % ", ".join(r["scene"] for r in opn))
        left = remaining(st) - st["budget"]["reserve"]
    except Refused as e:
        if commit:
            if st.get("status") not in ("locked",):
                hist(st, "refused", str(e))
            write_json(state_path(d), st)
        raise
    if left <= 0:   # advisory, never a stop (owner 2026-11-04: "These budgets make no sense. All they do is stop work")
        left = st["budget"]["cap"] - st["budget"]["reserve"]
        hist(st, "over_budget", "%d of %d spent; run %s goes on with %d (advisory)" % (
            st["budget"]["spent"], st["budget"]["cap"], run, min(left, run_cap) if run_cap else left))
    budget = min(left, run_cap) if run_cap else left
    hashes = manifest_hashes(st["stage"], manifest)
    retries = sum(1 for h in st.get("history") or [] if h["what"] == "retry" and h.get("stage") == st["stage"])
    st["running"] = {"run": run, "stage": st["stage"], "manifest": hashes, "reserved": budget, "at": now_iso(),
                     "inputs": inputs(d, st, repo), "owner_uncited": owner_uncited(repo, st.get("item"), d)}
    if st.get("status") == "waiting_owner":
        st["status"] = "ready"
    hist(st, "open", "run %s, stage %d, budget %d" % (run, st["stage"], budget))
    if commit:
        write_json(state_path(d), st)
    return packet(d, st, hashes, budget, why, retries, manifest, repo), budget


def abort_run(d, run):
    """The launch never happened (systemd-run said no): the open run is dropped, nothing charged."""
    st = load_state(d)
    if (st.get("running") or {}).get("run") != run:
        return False
    st["running"] = None
    hist(st, "abort", "run %s never launched; nothing charged" % run)
    write_json(state_path(d), st)
    return True


def owner_moved(st, d, repo):
    w = st.get("waiting_owner_feed")
    return w is not None and owner_feed(repo, st.get("item"), d) != w


def owner_answered_at(st, d, repo=REPO):
    """A concept at waiting_owner whose owner has answered (owner_moved) waits on a run-now launch nobody schedules
    (DESIGNER_ANSWERED_MONITOR_WAITING_ON_NOBODY). -> epoch seconds it has waited since: the earliest uncited owner
    event newer than the wait began (its last history row), else the wait's start; None while he has not answered
    (no waiting_owner_feed recorded, or the feed unchanged). Refused when the OWNER shard is unreadable: blind, not
    silence."""
    w = st.get("waiting_owner_feed")
    if w is None:
        return None
    u = owner_uncited(repo, st.get("item"), d)
    if u is None:
        raise Refused("OWNER shard unreadable for %s" % st.get("item"))
    if _feed_of(u) == w:
        return None
    hs = [h for h in st.get("history") or [] if isinstance(h, dict)]
    began = _epoch(hs[-1].get("at")) if hs else None
    if began is None:
        raise Refused("waiting_owner concept with no readable history time")
    newer = [int(t) / 1e9 for t in u if t.isdigit() and int(t) / 1e9 > began]
    return min(newer) if newer else began


def _epoch(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def charge_state(st, tokens, kind, ref):
    if kind not in CHARGE_KINDS:
        raise Refused("charge kind %r is not one of %s" % (kind, "/".join(CHARGE_KINDS)))
    if not isinstance(tokens, int) or tokens < 0:
        raise Refused("tokens must be a whole number >= 0")
    st["budget"]["spent"] += tokens
    st["budget"]["charges"].append({"at": now_iso(), "tokens": tokens, "kind": kind, "ref": ref, "stage": st["stage"]})


def charge(d, tokens, kind, ref):
    st = load_state(d)
    charge_state(st, tokens, kind, ref)
    write_json(state_path(d), st)
    return st


def close_run(d, run, tokens=None, repo=REPO):
    """The launcher, after the run ends: charge it (UNMEASURED = its whole reservation), then validate result.json
    and advance only on a valid result. -> (accepted?, reasons)."""
    st = load_state(d)
    r = st.get("running")
    if not r or r.get("run") != run:
        raise Refused("run %s is not the open run (%s)" % (run, (r or {}).get("run")))
    charge_state(st, tokens if tokens is not None else r.get("reserved", 0),
                 "stage" if tokens is not None else "unmeasured", "run %s" % run)
    res = read_json(os.path.join(d, "result.json"))
    errs = result_errors(res, d, st, repo)
    # an input changed while the run worked (a late owner reply, an edited artifact it did not make): the result is
    # judged against what the run was given, so a done result whose dependencies moved underneath is refused
    if not errs and res.get("outcome") == "done":
        new = set(owner_uncited(repo, st.get("item"), d) or []) - set(r.get("owner_uncited") or [])
        if "owner" in DEPS[st["stage"]] and new:
            errs.append("an owner event arrived during the run and is not taken in (%s); stage %d reruns with it" % (
                ", ".join("OWNER:" + t for t in sorted(new)), st["stage"]))
        # the lock is final: an accepted stage's inputs (scenes.json and its showcase set, the tree, the record) edited
        # during the stage-5 run would lock a concept the exam never saw. Refused; the next open reopens that stage.
        if st["stage"] == 5:
            s_from, moved = stale_stage(d, st, repo)
            if s_from is not None:
                errs.append("stage %d's accepted inputs changed during the lock run (%s): not locked; the next run "
                            "reopens stage %d" % (s_from, ", ".join(moved), s_from))
    st["running"] = None
    if errs:
        st["results"].append({"stage": st["stage"], "outcome": "rejected", "run": run, "at": now_iso(),
                              "why": errs[:20]})
        hist(st, "retry", "run %s result rejected: %s" % (run, "; ".join(errs[:3])))
        if os.path.exists(os.path.join(d, "result.json")):
            os.replace(os.path.join(d, "result.json"), os.path.join(d, "result.%s.rejected.json" % safe(run)))
        write_json(state_path(d), st)
        return False, errs
    out, stage = res["outcome"], st["stage"]
    entry = {"stage": stage, "outcome": out, "run": run, "at": now_iso(), "inputs": inputs(d, st, repo),
             "owner_uncited": owner_uncited(repo, st.get("item"), d), "manifest": r["manifest"]}
    if out == "done" and stage == 2:
        st.pop("must_cite", None)
    for k in ("to", "decision", "on", "question", "summary"):
        if k in res:
            entry[k] = res[k]
    st["results"].append(entry)
    if out == "done":
        if stage == 5:
            st["status"] = "locked"
        else:
            st["stage"], st["status"] = stage + 1, "ready"
    elif out == "waiting_owner":
        st["status"], st["waiting_owner_feed"] = "waiting_owner", owner_feed(repo, st.get("item"), d)
    elif out == "return":
        st["stage"], st["status"] = res["to"], "ready"
        st["pending_decision"] = res["decision"]
    elif out == "blocked":
        st["status"], st["blocked_on"] = "blocked", res["on"]
    hist(st, "close", "run %s: stage %d %s" % (run, stage, out))
    os.replace(os.path.join(d, "result.json"), os.path.join(d, "result.%s.json" % safe(run)))
    write_json(state_path(d), st)
    return True, []


LAND = os.path.join(os.path.dirname(HERE), "Utils", "land.sh")


def state_paths(d, repo):
    """The harvest's own files in a concept folder, relative to its clone: stage.json, every result*.json there, and
    result.json when origin/main still has it after close renamed it away (a deletion lands too)."""
    rel = os.path.relpath(os.path.abspath(d), repo)
    out = [os.path.join(rel, "stage.json")] if os.path.isfile(os.path.join(d, "stage.json")) else []
    out += sorted(os.path.join(rel, n) for n in os.listdir(d) if re.match(r"result(\..+)?\.json$", n))
    gone = os.path.join(rel, "result.json")
    if gone not in out:
        import subprocess
        r = subprocess.run(["git", "-C", repo, "ls-tree", "--name-only", "origin/main", "--", gone],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            out.append(gone)
    return out


def land_state(d, run, timeout=120):
    """DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE: close_run advances stage.json and renames result.json in the Designer's
    clone; nothing committed them, so origin/main kept reading the old stage (3906e2b306 landed three by hand). This
    lands exactly those paths with land.sh -m (a temp index from origin/main: the clone's index, HEAD and a peer's
    staged or unstaged edits are never touched). -> "PUBLISHED <sha>" | "nothing to land" | "skipped: <why>".
    Raises RuntimeError on a refused landing (the caller alarms; the files stay on disk for the next close)."""
    import subprocess
    if os.environ.get("RM_STAGE_LAND") == "0":
        return "skipped: RM_STAGE_LAND=0"
    r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                       timeout=120)
    if r.returncode != 0 or not r.stdout.strip():
        return "skipped: %s is not in a git clone" % d
    repo = r.stdout.strip()
    rel = os.path.relpath(os.path.realpath(d), os.path.realpath(repo)).replace(os.sep, "/")
    if not re.match(r"design/concepts/[^/]+$", rel):
        # only a real concept folder lands: a selftest fixture (a temp dir, even inside some clone) never pushes
        return "skipped: %s is not design/concepts/<Mod> of its clone" % d
    paths = state_paths(os.path.realpath(d), os.path.realpath(repo))
    if not paths:
        return "skipped: no stage files in %s" % d
    st = read_json(os.path.join(d, "stage.json"), {}) or {}
    last = (st.get("results") or [{}])[-1]
    mod = st.get("mod") or os.path.basename(os.path.abspath(d))
    msg = ("Designer: %s stage %s %s (run %s), harvest lands its own state\n\n"
           "Landed by designer_stage.land_state (DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE): stage.json and result files only."
           % (mod, last.get("stage", st.get("stage")), last.get("outcome", st.get("status")), run))
    p = subprocess.run([LAND, "-m", msg] + paths, cwd=repo, capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, LAND_REPO=repo))
    if p.returncode == 0:
        return p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "PUBLISHED ?"
    if "nothing to land" in p.stderr:
        return "nothing to land"
    raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()[-300:]))


def safe(run):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(run))


def unblock(d, why):
    st = load_state(d)
    if st.get("status") != "blocked":
        raise Refused("not blocked")
    st["status"] = "ready"
    hist(st, "unblock", why)
    write_json(state_path(d), st)


# ---------------------------------------------------------------- scene recovery journal

def scene_begin(d, scene, recovery):
    if not CT.txt(recovery):
        raise Refused("scene-begin records how to restore BEFORE persistent state changes")
    st = load_state(d)
    st.setdefault("recovery", []).append({"scene": scene, "recovery": recovery, "state": "open", "at": now_iso()})
    write_json(state_path(d), st)


def scene_end(d, scene, held=False, until=None):
    st = load_state(d)
    hit = [r for r in st.get("recovery") or [] if r["scene"] == scene and r["state"] in ("open", "held")]
    if not hit:
        raise Refused("no open recovery for scene %s" % scene)
    for r in hit:
        r["state"], r["at_end"] = ("held", now_iso()) if held else ("restored", now_iso())
        if held:
            r["until"] = until
    write_json(state_path(d), st)


# ---------------------------------------------------------------- the packet

def working_record(d):
    """The compact view a run starts from: entries with their source ids. log.md is not injected; a run loads an
    original excerpt by its source id when it relies on it."""
    rec = read_json(os.path.join(d, "record.json"), {}) or {}
    out = []
    if isinstance(rec.get("root"), dict):
        out.append("root: %s [%s]" % (rec["root"].get("text"), ",".join(lst(rec["root"].get("source")))))
    for sect in ("scope", "decisions", "asks", "inventory", "contradictions"):
        rows = [e for e in rec.get(sect) or [] if isinstance(e, dict)]
        if not rows:
            continue
        out.append("%s:" % sect)
        for e in rows:
            extra = ""
            if sect == "inventory":
                extra = " impl=%s proof=%s scope=%s" % (e.get("impl"), e.get("proof"), e.get("scope"))
            elif sect == "asks":
                extra = " status=%s" % e.get("status")
            out.append("- %s: %s%s [%s]" % (e.get("id"), e.get("text") or e.get("what") or "", extra,
                                             ",".join(lst(e.get("source")))))
    if rec.get("failure_modes"):
        out.append("failure_modes: " + " | ".join(lst(rec["failure_modes"])))
    return "\n".join(out) or "(empty: record.json has no entries yet)"


def packet(d, st, hashes, budget, why=None, retries=0, manifest=MANIFEST, repo=None):
    s = st["stage"]
    head = [
        "[designer_stage.py packet: concept %s, stage %d %s, run %s]" % (
            st.get("mod"), s, STAGE_NAMES[s], (st.get("running") or {}).get("run")),
        "Folder: %s. Budget: task cap %d, spent %d, reserve %d; this run %d weighted tokens. The launcher charges "
        "it; a fresh run does not reset it." % (d, st["budget"]["cap"], st["budget"]["spent"],
                                                st["budget"]["reserve"], budget),
        "End by writing result.json in the folder: {\"run\": \"%s\", \"stage\": %d, \"outcome\": "
        "\"done|waiting_owner|return|blocked\", ...}. Check it with `designer_stage.py check <folder>`. The launcher "
        "validates it when the run ends; nothing else advances the stage." % ((st.get("running") or {}).get("run"), s),
    ]
    if why:
        head.append("REOPENED: %s." % why)
    if st.get("pending_decision"):
        head.append("Returned here for this missing decision: %s." % st["pending_decision"])
    if retries:
        head.append("This stage has had %d rejected or unclosed run(s); read the last rejection in stage.json." % retries)
    held = [r for r in st.get("recovery") or [] if r.get("state") == "held"]
    if held:
        head.append("Held for his review: %s." % ", ".join("%s (until %s)" % (r["scene"], r.get("until")) for r in held))
    body = ["", "## Working record (record.json)", working_record(d)]
    if s in (0,) + DIALOGUE:
        body += built_section(REPO if repo is None else repo, st)
    for name, h in hashes.items():
        with open(os.path.join(os.path.dirname(manifest), name), encoding="utf-8") as f:
            body += ["", "=== %s (sha256 %s) ===" % (name, h[:12]), f.read()]
    return "\n".join(head + body)


# ---------------------------------------------------------------- turns waiting on him (the doorstep)
# DESIGNER_TURNS_FIX_LEFT_ON_THE_DOORSTEP: FlowWorks turn 2 closed waiting_owner at 02:02Z on 2026-11-05 and sat five
# hours in turn_02.md until he asked "Did it ever happen?". A waiting turn is read from here by every surface he looks
# at (owner_queue.needs_you -> NEEDS YOU and RUNNING NOW, the Conductor's wake); role_launch escalates it on close.
SCHEDULE = os.path.join(HERE, "dispatcher_schedule.json")
LIFECYCLE = ("lease", "claim", "start", "release", "seat", "unclaim", "renew")   # a seat moving the item is not his answer


def designer_clone(schedule=SCHEDULE):
    """The Designer role's clone (dispatcher_schedule.json), where its runs write design/concepts, or None."""
    try:
        with open(schedule, encoding="utf-8") as f:
            sch = json.load(f)
    except (OSError, ValueError):
        return None
    for r in (sch.get("roles") if isinstance(sch, dict) else None) or []:
        if isinstance(r, dict) and r.get("stage_machine") == "designer_stage" and r.get("clone"):
            return r["clone"]
    return None


def concepts_root(schedule=SCHEDULE):
    return os.path.join(designer_clone(schedule) or REPO, "design", "concepts")


def epoch(iso):
    try:
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def his_answers(lines, item, since):
    """tsns of OWNER-shard events naming `item` after `since` (epoch s) that carry his own word (ownerSaid or byCard):
    the answer that takes a waiting turn off his doorstep. A seat's lifecycle move or a --per-ruling note also lands on
    OWNER.jsonl, but it is not his answer to these asks."""
    out = []
    for ln in lines or []:
        if item not in ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if (not isinstance(ev, dict) or ev.get("id") != item or ev.get("event") in LIFECYCLE
                or not (CT.txt(ev.get("ownerSaid")) or CT.txt(ev.get("byCard")))):
            continue
        try:
            tsn = int(ev.get("tsn"))
        except (TypeError, ValueError):
            continue
        if tsn / 1e9 > since:
            out.append(str(tsn))
    return sorted(out)


def turn_file(d, entry):
    """The turn_NN.md the waiting result names, else the newest one in the folder, else None (repo-relative when
    the summary names it)."""
    m = re.search(r"(?:[A-Za-z0-9_./-]*/)?turn_[0-9]+\.md", str((entry or {}).get("summary") or ""))
    if m and os.path.isfile(os.path.join(d, os.path.basename(m.group(0)))):
        return os.path.join(d, os.path.basename(m.group(0)))
    try:
        turns = sorted(n for n in os.listdir(d) if re.fullmatch(r"turn_[0-9]+\.md", n))
    except OSError:
        return None
    return os.path.join(d, turns[-1]) if turns else None


def pending_turn(d, repo=REPO, lines=None):
    """-> the turn in `d` that waits on him, or None: status waiting_owner and no answer of his (an OWNER event naming
    the concept's item, with ownerSaid or byCard) since the turn closed. {mod, item, stage, run, at, turn, asks: [{id, text}], dir}. A state
    that cannot be read raises (the caller says UNMEASURED, never "nothing waits")."""
    st = load_state(d)
    if st.get("status") != "waiting_owner":
        return None
    item = st.get("item")
    waits = [r for r in st.get("results") or [] if r.get("outcome") == "waiting_owner"]
    last = waits[-1] if waits else {}
    since = epoch(last.get("at")) or 0
    if lines is None:
        lines = CT.owner_lines(repo, clone_of(d))
    if item and lines is not None and his_answers(lines, item, since):
        return None
    rec = read_json(os.path.join(d, "record.json")) or {}
    asks = [{"id": a.get("id"), "text": " ".join(str(a.get("text") or "").split())}
            for a in rec.get("asks") or [] if isinstance(a, dict) and a.get("status") == "sent"]
    return {"mod": st.get("mod") or os.path.basename(d), "item": item, "stage": st.get("stage"),
            "run": last.get("run"), "at": last.get("at"), "turn": turn_file(d, last), "asks": asks, "dir": d,
            "owner_unread": lines is None}


def pending_turns(root=None, repo=REPO):
    """-> ([turn], [unreadable: "<dir>: why"]) over every concept folder under `root` (default: the Designer's clone).
    `_`-prefixed folders (the dry walk) are never real concepts."""
    root = root or concepts_root()
    out, bad = [], []
    try:
        names = sorted(os.listdir(root))
    except OSError as e:
        return [], ["%s: %s" % (root, e)]
    lines = None
    for n in names:
        d = os.path.join(root, n)
        if n.startswith("_") or not os.path.isfile(os.path.join(d, "stage.json")):
            continue
        try:
            if lines is None:
                lines = CT.owner_lines(repo, clone_of(d))
            t = pending_turn(d, repo, lines)
        except Exception as e:      # noqa: BLE001 - one bad folder is said, never drops the rest
            bad.append("%s: %s" % (d, str(e)[:160]))
            continue
        if t:
            out.append(t)
    return out, bad


MIRROR = "D:\\Luke\\dev\\RimMandrake"     # the owner reads paths in his read-only Windows mirror


def owner_path(p):
    """A path as the owner opens it: inside a clone, the same file in his mirror; anything else unchanged."""
    c = clone_of(os.path.dirname(p)) if p else None
    if not c:
        return p
    return MIRROR + "\\" + os.path.relpath(p, c).replace("/", "\\")


def turn_line(t):
    """One plain line for his queue, headline first (boards clip it): whose turn, how many asks, where to read them,
    then each ask."""
    n = len(t["asks"])
    return "%s Designer turn (stage %s) waits on you since %s: %d %s%s in %s%s" % (
        t["mod"], t["stage"], (t.get("at") or "?").replace("T", " "), n, "ask" if n == 1 else "asks",
        " (%s)" % ", ".join(str(a["id"]) for a in t["asks"]) if n else "", owner_path(t.get("turn") or t["dir"]),
        "".join(" | %s: %s" % (a["id"], a["text"][:160]) for a in t["asks"]))


def status(d, repo=REPO):
    st = load_state(d)
    s, changed = stale_stage(d, st, repo)
    return {"mod": st.get("mod"), "stage": st["stage"], "status": st["status"], "spent": st["budget"]["spent"],
            "cap": st["budget"]["cap"], "reserve": st["budget"]["reserve"], "running": st.get("running"),
            "stale_from": s, "stale_inputs": changed,
            "recovery_open": [r["scene"] for r in st.get("recovery") or [] if r["state"] == "open"],
            "recovery_held": [r["scene"] for r in st.get("recovery") or [] if r["state"] == "held"]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("init")
    x.add_argument("dir")
    x.add_argument("--mod", required=True)
    x.add_argument("--item")
    x.add_argument("--cap", type=int, default=DEFAULT_CAP)
    x.add_argument("--reserve", type=int, default=DEFAULT_RESERVE)
    x.add_argument("--alias", action="append", default=[], help="another item-id subject naming the mod (GSS)")
    for name in ("open", "close"):
        x = sub.add_parser(name)
        x.add_argument("dir")
        x.add_argument("--run", required=True)
        x.add_argument("--run-cap" if name == "open" else "--tokens", type=int)
    x = sub.add_parser("charge")
    x.add_argument("dir")
    x.add_argument("--tokens", type=int, required=True)
    x.add_argument("--kind", required=True, choices=CHARGE_KINDS)
    x.add_argument("--ref", required=True)
    for name in ("check", "status"):
        sub.add_parser(name).add_argument("dir")
    x = sub.add_parser("land", help="land the concept's stage.json and result files on origin/main (close does it)")
    x.add_argument("dir")
    x.add_argument("--run", default="catch-up")
    x = sub.add_parser("unblock")
    x.add_argument("dir")
    x.add_argument("--why", required=True)
    for name in ("scene-begin", "scene-end", "scene-hold"):
        x = sub.add_parser(name)
        x.add_argument("dir")
        x.add_argument("--scene", required=True)
        if name == "scene-begin":
            x.add_argument("--recovery", required=True)
        if name == "scene-hold":
            x.add_argument("--until", required=True)
    sub.add_parser("spend", help="per-stage weighted spend of each concept against the default cap").add_argument(
        "dirs", nargs="+")
    sub.add_parser("manifest")
    sub.add_parser("turns", help="every concept turn that waits on him (status waiting_owner, unanswered)").add_argument(
        "--root", default=None)
    sub.add_parser("showcases", help="per showcase: new coverage, overlap; the capabilities left uncovered").add_argument(
        "dir")
    a = p.parse_args(argv)
    try:
        if a.cmd == "turns":
            turns, bad = pending_turns(a.root)
            for t in turns:
                print(turn_line(t))
            for b in bad:
                print("UNMEASURED %s" % b)
            print("%d Designer turn(s) wait on him" % len(turns))
            return 1 if bad else 0
        if a.cmd == "spend":
            stages = []
            for d in a.dirs:
                st = read_json(state_path(d))
                if not isinstance(st, dict):
                    print("UNMEASURED %s: no stage.json" % d)
                    return 1
                rows = spend_by_stage(st)
                stages += [r["total"] for r in rows.values()]
                print("%-20s stage %s %-13s spent %9d  %s" % (
                    os.path.basename(os.path.normpath(d)), st.get("stage"), st.get("status"),
                    st["budget"]["spent"], "  ".join("s%s %d" % (k, rows[k]["total"]) for k in sorted(rows))))
            if not stages:
                print("UNMEASURED: no charges in %d concept(s)" % len(a.dirs))
                return 1
            stages.sort()
            med = stages[len(stages) // 2]
            print("%d stages walked: min %d, median %d, max %d; 6 stages x median = %d; default cap %d, reserve %d"
                  % (len(stages), stages[0], med, stages[-1], 6 * med, DEFAULT_CAP, DEFAULT_RESERVE))
            if DEFAULT_CAP < 6 * med or DEFAULT_CAP <= stages[-1]:
                print("CAP TOO LOW: the default cap does not hold a walk of median stages")
                return 1
            return 0
        if a.cmd == "manifest":
            print(json.dumps({"stage_%d" % s: manifest_hashes(s) for s in STAGES}, indent=1))
        elif a.cmd == "init":
            init(a.dir, a.mod, a.item, a.cap, a.reserve, a.alias)
            print("init %s: stage 0" % a.dir)
        elif a.cmd == "open":
            text, budget = open_run(a.dir, a.run, a.run_cap)
            print(text)
        elif a.cmd == "close":
            ok, errs = close_run(a.dir, a.run, a.tokens)
            try:
                print("landed: %s" % land_state(a.dir, a.run), file=sys.stderr)
            except (RuntimeError, OSError, ValueError, __import__("subprocess").SubprocessError) as e:
                print("NOT LANDED: %s" % e, file=sys.stderr)
            if not ok:
                print("REJECTED:\n" + "\n".join("  " + e for e in errs), file=sys.stderr)
                return 1
            print("accepted: %s" % json.dumps(status(a.dir)))
        elif a.cmd == "land":
            try:
                print(land_state(a.dir, a.run))
            except (RuntimeError, OSError, ValueError, __import__("subprocess").SubprocessError) as e:
                print("NOT LANDED: %s" % e, file=sys.stderr)
                return 1
        elif a.cmd == "charge":
            st = charge(a.dir, a.tokens, a.kind, a.ref)
            print("charged %d; spent %d of %d" % (a.tokens, st["budget"]["spent"], st["budget"]["cap"]))
        elif a.cmd == "check":
            st = load_state(a.dir)
            errs = result_errors(read_json(os.path.join(a.dir, "result.json")), a.dir, st)
            print("\n".join(errs) if errs else "result.json would be accepted")
            return 1 if errs else 0
        elif a.cmd == "status":
            print(json.dumps(status(a.dir), indent=1))
        elif a.cmd == "showcases":
            try:
                tree = CT.load(a.dir)
            except (FileNotFoundError, ValueError):
                tree = None
            rules = load_showcase_rules()
            rows, errs = showcase_table(read_json(os.path.join(a.dir, "scenes.json")),
                                        read_json(os.path.join(a.dir, "record.json")), tree, CT.owner_events(REPO),
                                        REPO, rules)
            print("limits: max_overlap %s, min_new_after_first %s (%s)" % (
                rules["max_overlap"], rules["min_new_after_first"], str(rules.get("status", ""))[:40]))
            for r in rows:
                print("%d %-28s exercises %2d  new %2d  overlap %.2f  %s" % (
                    r["order"], r["id"], r["exercises"], r["new"], r["overlap"], ",".join(r["overlapped"])))
            print("\n".join(errs) if errs else "showcase set accepted")
            return 1 if errs else 0
        elif a.cmd == "unblock":
            unblock(a.dir, a.why)
        elif a.cmd == "scene-begin":
            scene_begin(a.dir, a.scene, a.recovery)
        elif a.cmd in ("scene-end", "scene-hold"):
            scene_end(a.dir, a.scene, held=a.cmd == "scene-hold", until=getattr(a, "until", None))
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
