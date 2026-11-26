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

  init     <dir> --mod M [--item ID] [--alias GSS]... [--cap N] [--reserve N] [--runner claude|codex] [--draft F]   start a concept's state
  open     <dir> --run U [--run-cap N]     the launcher: refuse or return the stage packet (stdout) and reserve budget
  close    <dir> --run U [--tokens N]      the launcher: charge the run, validate result.json, advance or not
  charge   <dir> --tokens N --kind K --ref R   a helper, review or consult outside the run's own transcript
  land     <dir> [--run U]                 land stage.json and the result files on origin/main (close does it itself)
  check    <dir>                           validate result.json now, write nothing (the Designer's dry run)
  status   <dir>                           stage, budget, staleness, open recovery
  spend    <dir>...                        per-stage weighted spend against the default cap (the cap's measurement)
  scene-begin <dir> --scene S --recovery TEXT | scene-end <dir> --scene S | scene-hold <dir> --scene S --until TEXT
  exam-control <dir> --leaf L [--strip PHRASE]...   write the Stage 4 control copy (never edited by hand)
  manifest                                 the stage -> packet files table, with hashes
  showcases <dir>                          the showcase set: per showcase new coverage and overlap, what is uncovered
  turns [--root R]                         every turn that waits on him: waiting_owner, no OWNER event since it closed
  repin <dir> --source OWNER:<tsn>[@<commit>]|TEXT@<commit>... --why W   a LOCKED version changed by his card or by scene test text only: re-pin, no reopen

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
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import exam_retake as ER  # noqa: E402

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
SCOPE = ("approved", "not_opened", "opened_by_owner", "opened_by_conductor", "open_question", "later", "out")
# Who opened a built thing's scope (RIMMANDRAKE_LABEL_CONDUCTOR_OPENED_SCOPE_NOT_HIS_WORDS, design decision 2026-11-18):
# he did, in his own words (scope_source OWNER:<tsn>, an event carrying ownerSaid or byCard), or the Conductor did under
# its standing authority (scope_source CONDUCTOR:<tsn>, an OWNER-shard event per-ruling CONDUCTOR_AUTHORITY and carrying
# none of his words). The Conductor's opening is never stored under his name.
OPENED_SCOPES = ("opened_by_owner", "opened_by_conductor")
CONDUCTOR_AUTHORITY = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
SPEAKERS = ("owner", "conductor", "agent")
OWNER_ONLY = ("root", "exam_waived", "floor_disable", "locked_change", "waiver", "his_words")
# The Evidence-for-Ask rule (owner, 2026-11-15, item below): the root and the flagship pick may instead be approved by a
# recorded delegated call: an OWNER.jsonl event per-ruling that item, why "delegated: evidence-for-ask: ..." (so it
# reaches his daily digest) and about this concept, cited as CONDUCTOR:<tsn> and stored speaker conductor, delegated
# "evidence-for-ask", never as his. An ask carrying evidence_against still waits for him.
EVIDENCE_FOR_ASK = "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME"
EFA_WHY = "delegated: evidence-for-ask"
# Only five acts stay his (owner 2026-11-19, conductor_acts.py): every OWNER_ONLY kind but his_words may instead be the
# Conductor window's act: speaker conductor, delegated "conductor-act", citing CONDUCTOR:<tsn>, an OWNER.jsonl event
# under that ruling about this concept (conductor_acts.is_conductor_event). A waiver, exam waiver or floor disable drops
# a requirement, so its why names lost: and undo:. his_words records his words: only he writes it. An ask carrying
# evidence_against still waits for him (the card rule beside Evidence-for-Ask).
CONDUCTOR_ACT = "conductor-act"
MINDFUL_KINDS = ("exam_waived", "floor_disable", "waiver")
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
EXAM_FROZEN = ("tree", "sheet")     # the inputs exam.json is frozen against (exam_errors); a repin never re-pins over them
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
    his words not yet taken in. A reply he gives adds one; the Designer citing it (OWNER:<tsn>) takes it out again.
    A caused_by link alone records a dependency, without adding design input on its parent item.
    Evidence-for-Ask calls share that shard but are cited as CONDUCTOR:<tsn>, never as his words. Recognize those
    citations only for recorded delegated calls, so recording a call inside a run does not invalidate that run.
    None = the shard is unreadable."""
    if not item:
        return None
    lines = CT.owner_lines(repo, clone_of(d))     # working trees AND origin/main: a stale clone is not his silence
    if lines is None:
        return None
    tsns, delegated = [], set()
    named = _names_id(item)
    for ln in lines:
        if item not in ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("tsn"):
            input_fields = dict(ev)
            input_fields.pop("caused_by", None)
            if not named.search(json.dumps(input_fields)):     # X is not named by an event on X_EXTRA
                continue
            tsn = str(ev["tsn"])
            tsns.append(tsn)
            if ev.get("perRuling") == EVIDENCE_FOR_ASK and str(ev.get("why") or "").startswith(EFA_WHY):
                delegated.add(tsn)
            elif (ev.get("perRuling") == "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"
                  and str(ev.get("why") or "").startswith("delegated: conductor act:")):
                delegated.add(tsn)          # the Conductor's act, cited CONDUCTOR:<tsn> (conductor_acts.py)
    cited = ""
    for name in ("record.json", "tree.json"):
        try:
            with open(os.path.join(d or "", name), encoding="utf-8", errors="replace") as f:
                cited += f.read()
        except OSError:
            pass
    return sorted(t for t in tsns if not re.search(r"(?<![A-Za-z0-9_])OWNER:%s(?![0-9])" % re.escape(t), cited)
                  and not (t in delegated and re.search(r"CONDUCTOR:%s(?![0-9])" % re.escape(t), cited)))


def _names_id(item):
    """A whole ledger id: X, never the X inside X_EXTRA or OLD_X (RIMMANDRAKE_FIX_DESIGNER_STAGE_CODEX_REVIEW_FINDINGS
    finding 1: a substring match pulled another item's events into this concept's owner feed)."""
    return re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(item))


def owner_elsewhere(repo, d, st=None):
    """{tsn: item} of his words (ownerSaid or byCard) on ANY of the mod's items, its own included, that neither
    record.json nor tree.json cites as OWNER:<tsn> (RIMMANDRAKE_HARVEST_OWNER_WORDS_OFF_CONCEPT_ITEM_FOURTH_ASK: his
    2026-11-09 slope rule for Gimme Some Slack sat on a build item and never became a bar of its 0.1.0). A mod's item
    is one of its own (concept_tree.mod_items), an id under its prefix (mod_prefixes), one whose cause chain reaches
    its own (as concept_tree.caused_by_mod walks it, to any depth), or one whose filed title starts with the mod's name
    (a title merely mentioning it is not enough: the six-mod hold item named every held mod; a name of four letters or
    fewer matches no title, "Pyre" would claim every Pyrelands one). Causes and titles are read from the same clones
    as his words. Words owner_uncited also holds stay listed: that feed freezes stages, this list does not. Not part
    of owner_feed: no stage freezes this list, so these words never reopen an accepted stage or relaunch a run; the
    packet lists them and the lock (stage 5 done) refuses until each is cited.
    None = the OWNER shard, or a ledger shard the mapping reads, is unreadable."""
    st = st if isinstance(st, dict) else (read_json(state_path(d)) if d else None) or {}
    lines = CT.owner_lines(repo, clone_of(d))
    if lines is None:
        return None
    own = CT.mod_items(d) | ({st["item"]} if CT.txt(st.get("item")) else set())
    prefixes = tuple(mod_prefixes(st.get("mod") or os.path.basename(os.path.abspath(d)), st.get("aliases")))
    key = re.sub(r"[^a-z0-9]", "", (st.get("mod") or os.path.basename(os.path.abspath(d))).split("/")[-1].lower())
    words = {}
    for ln in lines:
        if '"ownerSaid"' not in ln and '"byCard"' not in ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("tsn") and CT.txt(ev.get("id")) and CT.his_word(ev):
            words[str(ev["tsn"])] = ev["id"]
    meta = None
    ours = {}
    for it in sorted(set(words.values())):
        if it in own or (prefixes and it.upper().startswith(prefixes)):
            ours[it] = True
            continue
        meta = _ledger_meta((repo, clone_of(d)), set(words.values())) if meta is None else meta   # one fold
        if meta is False:
            return None                  # a shard the mapping needs could not be read: unknown, never "not ours"
        causes, titles = meta
        chain, up = [], it
        while isinstance(up, str) and up and up not in chain and up not in own:     # the cycle check ends it
            chain.append(up)
            up = causes.get(up)
        ours[it] = up in own or (len(key) > 4 and re.sub(r"[^a-z0-9]", "", titles.get(it, "").lower()).startswith(key))
    cited = ""
    for name in ("record.json", "tree.json"):
        try:
            with open(os.path.join(d or "", name), encoding="utf-8", errors="replace") as f:
                cited += f.read()
        except OSError:
            pass
    return {t: it for t, it in sorted(words.items()) if ours.get(it)
            and not re.search(r"(?<![A-Za-z0-9_])OWNER:%s(?![0-9])" % re.escape(t), cited)}   # NOTOWNER: is no citation


def concept_start(st):
    """Epoch seconds of the concept's first history row (its init), or None."""
    for h in (st or {}).get("history") or []:
        if isinstance(h, dict) and h.get("at"):
            return _epoch(h["at"])
    return None


def elsewhere_binding(repo, d, st):
    """(owner_elsewhere, the tsns of it the lock refuses on): his words newer than the concept's start. Older words
    reach stage 0 through built_evidence's items; words given after it began are the ones a Designer can miss (the
    GSS slope rule came four days after its init). (None, None) = the OWNER shard is unreadable."""
    u = owner_elsewhere(repo, d, st)
    if u is None:
        return None, None
    t0 = concept_start(st)
    # whole seconds against nanoseconds, in integers: a word in the concept's first second binds (a float drops it)
    return u, sorted(t for t in u if t.isdigit() and (t0 is None or int(t) >= int(t0) * 10 ** 9))


def elsewhere_section(repo, d, st, cap=40):
    """The packet's list of owner_elsewhere: every binding word in full, older ones by reference up to `cap`."""
    u, bind = elsewhere_binding(repo, d, st)
    head = ["", "## His words on the mod's items, not yet cited (designer_stage.py owner_elsewhere)"]
    if u is None:
        return head + ["UNMEASURED: OWNER.jsonl could not be read; these words are unknown, not absent."]
    if not u:
        return head + ["- none: every word of his on the mod's items is cited in record.json or tree.json."]
    ev = CT.owner_events(repo, clone_of(d))
    out = head + ["Take each in where it bears on the design, and cite it as OWNER:<tsn> in record.json (a bar, a "
                  "decision, or `owner_elsewhere_reviewed` [{\"source\": \"OWNER:<tsn>\", \"not_design_input\": <why>}]). "
                  "The lock (stage 5 done) refuses while one given after this concept began is uncited "
                  "(%d of %d here)." % (len(bind), len(u))]
    for t in bind:
        e = ev.get(t) or {}
        w = " ".join(str(CT.his_word(e) or e.get("text") or "").split())
        out.append("- OWNER:%s on %s (%s): %s" % (t, u[t], e.get("ts") or "?", w))     # in full: these must be read
    older = [t for t in sorted(u) if t not in set(bind)]
    if older:
        out.append("Older than this concept (read; the lock does not refuse on them): %d%s" % (
            len(older), "" if len(older) <= cap else ", first %d" % cap))
        out += ["- OWNER:%s on %s" % (t, u[t]) for t in older[:cap]]
    return out


# ---------------------------------------------------------------- the universal-mechanics conversion, owed at next version
# Owner 2026-11-21 (GUIDING_PRINCIPLES.md entry 1; item RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES):
# each existing mod converts its biome-confined mechanics when it next advances, as a planned change for its next
# version; no current version's bars move. Page: design/specs/2026-11-21-guiding-principles/boundary.md.
CONVERSION_LIST = "design/specs/2026-11-21-guiding-principles/conversion_list.md"
CONVERSION_BASE = re.compile(r"^- Version on 2026-11-21: `([^`]+)`", re.M)


def conversion_sections(text):
    """-> {heading: body} for each `## ` section of the list (a heading inside a code fence is not one)."""
    out, cur, buf, fenced = {}, None, [], False
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and ln.startswith("## "):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur, buf = ln[3:].strip(), []
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def _semver3(v):
    m = re.fullmatch(r"\s*(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.+-]*)?\s*", str(v))
    return tuple(int(x) for x in m.groups()) if m else None


def conversion_base(body):
    """-> (base, why): base is "none" or a (major, minor, patch) tuple; (None, cause) when no single readable line."""
    found = CONVERSION_BASE.findall(body or "")
    if len(found) != 1:
        return None, "%d version line(s), not one" % len(found)
    if found[0].strip() == "none":
        return "none", None
    b = _semver3(found[0])
    return (b, None) if b else (None, "version line %r is not MAJOR.MINOR.PATCH" % found[0])


def conversion_owed(repo, d, st):
    """-> (state, why, section): state is owed | not_yet | none | unmeasured. owed: the concept's version is newer than
    the mod's version on 2026-11-21 (or that was `none`); not_yet: it is the same version, whose bars do not move."""
    path = os.path.join(repo, CONVERSION_LIST)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return "unmeasured", "%s is absent" % CONVERSION_LIST, None
    except (OSError, UnicodeDecodeError) as e:
        return "unmeasured", "%s could not be read: %s" % (CONVERSION_LIST, e), None
    st = st if isinstance(st, dict) else {}
    names = [n for n in [st.get("mod") or (os.path.basename(os.path.abspath(d)) if d else None)]
             + list(st.get("aliases") or []) if CT.txt(n)]
    secs = conversion_sections(text)
    head = next((n for n in names if n in secs), None)
    if head is None:
        return "none", "%s names no section for %s" % (CONVERSION_LIST, " or ".join(names) or "this mod"), None
    body = secs[head]
    base, why = conversion_base(body)
    if base is None:
        return "unmeasured", "%s §%s: %s" % (CONVERSION_LIST, head, why), None
    vp = os.path.join(d, "version", "VERSION.json") if d else None
    try:
        v = read_json(vp) if vp else None
    except Refused as e:
        return "unmeasured", "VERSION.json does not parse: %s" % e, None
    cur = _semver3((v or {}).get("version")) if v is not None else (0, 1, 0)
    if cur is None:
        return "unmeasured", "VERSION.json names no MAJOR.MINOR.PATCH version (%r)" % (v or {}).get("version"), None
    label = "%s §%s (version on 2026-11-21: %s; this version: %s)" % (
        CONVERSION_LIST, head, base if base == "none" else ".".join(map(str, base)), ".".join(map(str, cur)))
    if base == "none" or cur > base:
        return "owed", label, "## %s\n%s" % (head, body)
    return "not_yet", label, "## %s\n%s" % (head, body)


def conversion_section(repo, d, st):
    """The packet's section for the conversion list: the rows in full when this version owes them."""
    state, why, sec = conversion_owed(repo, d, st)
    out = ["", "## Owed input: the universal-mechanics conversion (GUIDING_PRINCIPLES.md entry 1)"]
    if state == "unmeasured":
        return out + ["UNMEASURED: %s. Whether this version owes a conversion is unknown, not absent." % why]
    if state == "none":
        return out + ["- none: %s names no row for this mod. Each new mechanic is still written as conditions." % (
            CONVERSION_LIST)]
    if state == "not_yet":
        return out + ["- %s lists this mod's biome-confined mechanics. They convert at its next version, never in this "
                      "one: no current bar moves." % why]
    return out + ["This version converts the rows below (%s). A code gate becomes a physical condition; a design or bar "
                  "line is reworded as a condition; a switch \"Enable outside this biome\" becomes a plain on/off for "
                  "its mechanic, default on, with no biome in it. In-game tests run on the home biome; no other test is "
                  "owed for the conversion. A mechanic that is a heavy load where it is not active may stay unloaded "
                  "outside its parent biome, as an exception written in the design with its reason. Rows under \"Not "
                  "ruled yet\" wait for his card: do not convert them." % why, sec]


def _ledger_meta(repos, ids):
    """-> ({item: its cause}, {item: its filed title for `ids`}) over every ledger shard of each clone in `repos`
    (concept_tree.ledger_causes' rule: a file event's caused_by, a spawn's from, `ITEM/run-N` is ITEM), or False when a
    shard that exists could not be read. A missing shard is no reading (events.jsonl may be absent); a bad line spoils
    itself only."""
    causes, titles = {}, {}
    for repo in dict.fromkeys(r for r in repos if r):
        for p in CT.ledger_files(repo):
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if '"file"' not in line and '"spawn"' not in line:
                            continue
                        try:
                            ev = json.loads(line)
                        except (ValueError, RecursionError):
                            continue
                        if not isinstance(ev, dict):
                            continue
                        kind = ev.get("event")
                        iid, cause = ((ev.get("id"), ev.get("caused_by")) if kind == "file" else
                                      (ev.get("name"), ev.get("from")) if kind == "spawn" else (None, None))
                        if not isinstance(iid, str):
                            continue
                        if isinstance(cause, str) and cause.strip():
                            causes.setdefault(iid, cause.split("/run-")[0])
                        if kind == "file" and iid in ids and isinstance(ev.get("title"), str):
                            titles.setdefault(iid, ev["title"])
            except FileNotFoundError:
                continue
            except OSError:
                return False
    return causes, titles


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


INPUT_FILES = {"root": "record.json", "sheet": "sheet.md", "tree": "tree.json", "scenes": "scenes.json",
               "floor": "floor.json", "exam": "exam.json"}


def input_hash(d, key):
    """The current hash of one file input (None = absent). tree.json by its tree hash, so the coverage judge's
    signature (coverage) does not count as a change; record.json by its root only (stage 1 freezes the root)."""
    if key == "tree":
        try:
            tree = CT.load(d)
            return CT.tree_hash(tree) if isinstance(tree, dict) else sha_file(os.path.join(d, "tree.json"))
        except FileNotFoundError:
            return None
        except ValueError:
            return sha_file(os.path.join(d, "tree.json"))
    if key == "root":
        try:
            rec = read_json(os.path.join(d, "record.json"))
            return CT.sha(rec.get("root")) if isinstance(rec, dict) and rec.get("root") is not None else None
        except Refused:
            return sha_file(os.path.join(d, "record.json"))
    return sha_file(os.path.join(d, INPUT_FILES[key]))


def inputs(d, st, repo=REPO):
    """The current hash of every input a stage can depend on (None = absent): input_hash per file, and the owner feed."""
    out = {k: input_hash(d, k) for k in INPUT_FILES}
    out["owner"] = owner_feed(repo, st.get("item"), d)
    return out


def stale_stage(d, st, repo=REPO):
    """(earliest stage whose accepted result no longer matches its inputs, [changed input names]) or (None, [])."""
    cur = inputs(d, st, repo)
    uncited = owner_uncited(repo, st.get("item"), d)
    for r in sorted(accepted(st), key=lambda r: r["stage"]):
        changed = [k for k in DEPS[r["stage"]] if r["inputs"].get(k) != cur.get(k)
                   and not (k == "owner" and _owner_only_taken_in(r, uncited))]
        if changed:
            return r["stage"], changed
    return None, []


def _owner_only_taken_in(r, uncited):
    """True when the owner feed moved only because words the stage froze uncited were cited since (a later stage took
    them in): nothing new for that stage (RIMMANDRAKE_KEEP_STAGE_TWO_WHEN_CITED_WORDS_ARE_OLD). An unreadable
    shard, or a result that never recorded its frozen words, is still a change."""
    frozen = r.get("owner_uncited")
    return uncited is not None and frozen is not None and not set(uncited) - set(frozen)


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
    if st.get("status") == "blocked":
        # a block holds the concept as it is: the reopen used to set it ready before open_run read the block, so a
        # blocked concept with a changed input opened anyway (ExplosiveKnockback 2026-11-13). `unblock`, then the
        # next open reopens it.
        return None
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

def on_origin_main(repo, path):
    """-> True when origin/main holds `path`, False when it does not, None when origin/main could not be read. A cited
    file the run's clone lacks but origin/main holds is not missing (4 of 16 rejected stage runs 2026-11-04..15:
    RIMMANDRAKE_CHECK_DESIGNER_RESULT_BEFORE_EXIT_EIGHT_REJECTED)."""
    try:
        if subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", "origin/main"], capture_output=True,
                          timeout=20).returncode:
            return None
        return subprocess.run(["git", "-C", repo, "cat-file", "-e", "origin/main:" + path], capture_output=True,
                              timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None


ITEMS_DIR = "infrastructure/state/items/"


def closed_item_path(path):
    """items/<ID>.md -> items/closed/<ID>.md, where an item's prose moves on close; None for any other path
    (RIMMANDRAKE_FOLLOW_CLOSED_ITEM_PROSE_SWEEP_BROKE_TWO_SOURCES: a ticket sweep closed two cited items and every
    Pyrelands stage-4 check refused its record)."""
    rest = path[len(ITEMS_DIR):] if path.startswith(ITEMS_DIR) else ""
    return ITEMS_DIR + "closed/" + rest if rest.endswith(".md") and "/" not in rest else None


def source_errors(src, where, repo, owner_ev, on_origin=None):
    """A repo path missing in `repo` is asked of on_origin(path) (default on_origin_main): True = it exists, no error;
    False = "does not exist"; None = "does not exist" plus "origin/main could not be read"."""
    if on_origin is None:
        on_origin = lambda p: on_origin_main(repo, p)  # noqa: E731
    errs = []
    srcs = src if isinstance(src, list) else [src]
    if not srcs or not all(isinstance(s, str) and s.strip() for s in srcs):
        return ["%s: no source (every entry links to where it came from)" % where]
    for s in srcs:
        if not SOURCE.fullmatch(s.strip()):
            errs.append("%s: source %r is not OWNER:<tsn>, CONDUCTOR:<tsn>, ITEM:<id>, log.md#L<n> or a repo path" % (
                where, s))
        elif s.startswith("OWNER:") and owner_ev is not None and getattr(owner_ev, "unread", not owner_ev):
            # RIMMANDRAKE_SPLIT_UNREADABLE_LEDGER_FROM_FORGED_SOURCE_CITATION: CT.owner_events returns {} (not None) for an
            # unreadable shard, which called every real citation of his forged. Could-not-look is its own answer: the
            # citation is not judged either way, and the caller refuses on this error as on any other. Its reading says
            # which it was (OwnerEvents.unread: a READ shard with no events still calls a citation absent); a plain empty
            # dict cannot say, so it is taken as unread. None stays "not asked" (record_errors' default; every production
            # caller passes CT.owner_events' reading).
            errs.append("%s: %s UNMEASURED: OWNER.jsonl could not be read here, so this citation is neither verified nor "
                        "called forged; validate where the ledger is present" % (where, s))
        elif s.startswith("OWNER:") and owner_ev is not None and s[6:] not in owner_ev:
            errs.append("%s: %s finds no event in OWNER.jsonl" % (where, s))
        elif not s.startswith(("OWNER:", "CONDUCTOR:", "ITEM:", "log.md#")):
            path = s.split(":")[0]
            if not os.path.exists(os.path.join(repo, path)):
                held = on_origin(path)
                moved = closed_item_path(path)
                if held is not True and moved:
                    held = True if os.path.exists(os.path.join(repo, moved)) else (on_origin(moved) or held)
                if held is False:
                    errs.append("%s: source path %s does not exist" % (where, path))
                elif held is None:
                    errs.append("%s: source path %s does not exist here (origin/main could not be read)" % (where, path))
    return errs


def concept_of(st, d=None):
    """The concept a state names, for about_concept; None (no check) when there is no state."""
    if not isinstance(st, dict):
        return None
    return {"mod": st.get("mod") or (os.path.basename(os.path.abspath(d)) if d else None), "item": st.get("item"),
            "aliases": list(st.get("aliases") or [])}


def about_concept(ev, concept):
    """An OWNER event is about this concept: filed on its item, or its words name the mod or an alias."""
    if not concept:
        return True
    if CT.txt(concept.get("item")) and ev.get("id") == concept["item"]:
        return True
    said = " ".join(str(ev.get(k) or "") for k in ("ownerSaid", "byCard", "text", "why"))
    return any(CT.in_words(n, said) for n in [concept.get("mod")] + list(concept.get("aliases") or []) if CT.txt(n))


def efa_problem(owner_ev, srcs, concept):
    """Why no CONDUCTOR:<tsn> in srcs is a recorded Evidence-for-Ask call about this concept, or None."""
    if owner_ev is None:
        return "an Evidence-for-Ask delegation cannot be checked blind (OWNER.jsonl unread)"
    for s in [s for s in srcs if isinstance(s, str) and s.startswith("CONDUCTOR:")]:
        ev = owner_ev.get(s.split(":", 1)[1])
        if (isinstance(ev, dict) and ev.get("perRuling") == EVIDENCE_FOR_ASK
                and str(ev.get("why") or "").startswith(EFA_WHY) and about_concept(ev, concept)):
            return None
    return ("cites no recorded Evidence-for-Ask call about this concept: a CONDUCTOR:<tsn> whose OWNER.jsonl event is "
            "per-ruling %s, why \"%s: ...\", naming %s" % (EVIDENCE_FOR_ASK, EFA_WHY,
                                                           (concept or {}).get("mod") or "the concept"))


def conductor_act_problem(owner_ev, srcs, concept, kind):
    """Why no CONDUCTOR:<tsn> in srcs is the Conductor window's act under the five-acts ruling about this concept, or
    None (owner 2026-11-19)."""
    import conductor_acts as CA
    if owner_ev is None:
        return "a Conductor act cannot be checked blind (OWNER.jsonl unread)"
    last = "cites no CONDUCTOR:<tsn>"
    for s in [s for s in srcs if isinstance(s, str) and s.startswith("CONDUCTOR:")]:
        ev = owner_ev.get(s.split(":", 1)[1])
        ok, why = CA.is_conductor_event(ev, act="loosen a bar" if kind in MINDFUL_KINDS else "designer " + kind)
        if ok and about_concept(ev, concept):
            return None
        last = "%s: %s" % (s, why if not ok else "not about %s" % ((concept or {}).get("mod") or "the concept"))
    return ("is not a recorded Conductor act about this concept (%s): a CONDUCTOR:<tsn> whose OWNER.jsonl event is "
            "per-ruling %s from the Conductor window" % (last, CA.RULING))


def ask_waits(rec, ans):
    """Why the ask `ans` cannot be answered by delegation, or None."""
    a = next((a for a in (rec or {}).get("asks") or [] if isinstance(a, dict) and a.get("id") == ans), None)
    if a is None:
        return "names the ask it answers (answers: an ask id in record.asks)"
    if a.get("evidence_against"):
        return "ask %s carries evidence against the obvious answer (evidence_against), so it waits for him" % ans
    return None


def owner_root_errors(e, where, owner_ev, concept):
    """An owner root cites an event of his (ownerSaid or byCard) about THIS concept, not any OWNER:<tsn>."""
    srcs = e.get("source") if isinstance(e.get("source"), list) else [e.get("source")]
    evs = [owner_ev.get(s[6:]) for s in srcs if isinstance(s, str) and s.startswith("OWNER:")]
    evs = [x for x in evs if isinstance(x, dict)]     # an absent event is refused by source_errors
    if not evs:
        return []
    his = [x for x in evs if x.get("ownerSaid") or x.get("byCard")]
    if not his:
        return ["%s: its OWNER event carries none of his words (no ownerSaid or byCard); a per-ruling event is the "
                "Conductor's: record it as a delegated Evidence-for-Ask root instead" % where]
    if not any(about_concept(x, concept) for x in his):
        return ["%s: its OWNER event is not about %s (not filed on %s, and naming neither it nor an alias)" % (
            where, concept.get("mod"), concept.get("item"))]
    return []


def authority_errors(e, where, owner_ev, concept=None, rec=None):
    """Who said it, and may they. Conductor text is never stored as his quotation; owner-only kinds need his words,
    except a root approved by a recorded Evidence-for-Ask call."""
    errs = []
    sp = e.get("speaker", "agent")
    if sp not in SPEAKERS:
        return ["%s: speaker %r is not one of %s" % (where, sp, "/".join(SPEAKERS))]
    srcs = e.get("source") if isinstance(e.get("source"), list) else [e.get("source")]
    owner_src = [s for s in srcs if isinstance(s, str) and s.startswith("OWNER:")]
    if sp == "owner" and not owner_src:
        errs.append("%s: speaker owner needs an OWNER:<tsn> source (Conductor text is never his quotation)" % where)
    elif sp == "owner" and owner_ev:
        # RIMMANDRAKE_REQUIRE_HIS_WORDS_BEHIND_SPEAKER_OWNER_RULING_PASSED: the OWNER shard also holds the Conductor's
        # per-ruling events; one of them is not his voice. An absent event is source_errors' to refuse.
        evs = [owner_ev.get(s[6:]) for s in owner_src]
        evs = [x for x in evs if isinstance(x, dict)]
        if evs and not any(x.get("ownerSaid") or x.get("byCard") for x in evs):
            errs.append("%s: speaker owner cites only OWNER events carrying none of his words (no ownerSaid or "
                        "byCard); a per-ruling event is the Conductor's: speaker conductor" % where)
    if e.get("quote") and sp != "owner":
        errs.append("%s: a quotation is his words only; %s text is never quoted as his" % (where, sp))
    if e.get("kind") in OWNER_ONLY:
        if e["kind"] == "root" and sp == "conductor" and e.get("delegated") == "evidence-for-ask":
            why = efa_problem(owner_ev, srcs, concept)
            if why:
                errs.append("%s: %s" % (where, why))
            why = ask_waits(rec, e.get("answers"))
            if why:
                errs.append("%s: a delegated root %s" % (where, why))
        elif e["kind"] != "his_words" and sp == "conductor" and e.get("delegated") == CONDUCTOR_ACT:
            why = conductor_act_problem(owner_ev, srcs, concept, e["kind"])
            if why:
                errs.append("%s: %s %s" % (where, e["kind"], why))
            why = ask_waits(rec, e.get("answers")) if e.get("answers") else None
            if why:
                errs.append("%s: a Conductor act %s" % (where, why))
        elif sp != "owner" or not owner_src:
            errs.append("%s: %s is owner-only (his words on an OWNER event), not %s; the Conductor window may do it as "
                        "its act (speaker conductor, delegated \"%s\", source CONDUCTOR:<tsn> per-ruling %s), "
                        "except his_words, which is his quotation" % (where, e["kind"], sp, CONDUCTOR_ACT,
                                                                      "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS"))
        else:
            if owner_ev is not None and e.get("words"):
                why = CT.his_words_problem(owner_ev, owner_src[0], e["words"])
                if why:
                    errs.append("%s: %s" % (where, why))
            if e["kind"] == "root" and owner_ev is not None:
                errs += owner_root_errors(e, where, owner_ev, concept)
    return errs


def record_errors(rec, repo=REPO, owner_ev=None, concept=None):
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
            errs += authority_errors(dict(root, kind="root"), "root", owner_ev, concept, rec)
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
    if e.get("scope") in OPENED_SCOPES:
        errs += scope_source_errors(e, w, owner_ev)
    return errs


def lst(v):
    return v if isinstance(v, list) else ([v] if v else [])


def _is_id(v):
    return isinstance(v, str) and bool(v.strip())


def _ids(v):
    """-> (the string ids of a list field, a short repr of each entry that is not one). A run's result.json can carry
    any JSON: a dict id used to reach a set or dict lookup and crash close_run, leaving the run open
    (RIMMANDRAKE_REFUSE_MALFORMED_IDS_CLOSE_RUN_CRASHES_INSTEAD); a non-string id is a rejection reason instead."""
    good, bad = [], []
    for x in lst(v):
        (good if _is_id(x) else bad).append(x)
    return good, [_clip_repr(x) for x in bad]


def _clip_repr(x, n=60):
    r = json.dumps(x, sort_keys=True, default=str) if not isinstance(x, str) else repr(x)
    return r if len(r) <= n else r[:n - 3] + "..."


def _ledger_unread(owner_ev):
    """None (never read), CT.owner_events' reading of an unreadable shard (OwnerEvents.unread), or a plain empty dict,
    which cannot say which it was and is taken as unread (as source_errors takes it)."""
    return owner_ev is None or bool(getattr(owner_ev, "unread", not owner_ev))


def scope_source_errors(e, w, owner_ev):
    """Why an inventory entry's opened scope (OPENED_SCOPES) is not opened by the event it cites, or [].
    RIMMANDRAKE_CHECK_SCOPE_SOURCE_EVENT_EXISTS_FAKE_ID_OPENS: a prefix is not an event, so OWNER:999999 used to open a
    built capability's scope. The cited event must EXIST in the ledger this validator can ALREADY read: no git call,
    because a stalled `git show` would turn a real id into a forgery. Legacy records store several citations inside one
    space-separated string (design/concepts/ExplosiveKnockback/record.json), so split.
    Owner 2026-11-17: found / not-found-in-a-read-ledger / ledger-unreadable are three different answers.
    opened_by_owner: at least one cited OWNER event carries his words (an OWNER-shard event with none of them is the
    Conductor's or a seat's). opened_by_conductor: every citation is CONDUCTOR:<tsn>, each an event per-ruling
    CONDUCTOR_AUTHORITY that carries none of his words (his words are stored as his: opened_by_owner)."""
    scope = e.get("scope")
    toks = [t for s in lst(e.get("scope_source")) if isinstance(s, str) for t in s.split()]
    if scope == "opened_by_owner":
        cited = [t for t in toks if re.fullmatch(r"OWNER:[0-9]+", t)]
        if not cited:
            return ["%s: opened_by_owner needs scope_source OWNER:<tsn> (only his words open a built thing's scope "
                    "under his name; a Conductor event opens it as opened_by_conductor, CONDUCTOR:<tsn>)" % w]
        if _ledger_unread(owner_ev):
            return ["%s: opened_by_owner cites %s, UNMEASURED: OWNER.jsonl was not read here, so the scope stays "
                    "shut and no citation is called forged; close this where the ledger is present" % (
                        w, ", ".join(cited))]
        gone = [t for t in cited if t[6:] not in owner_ev]
        if gone:
            return ["%s: opened_by_owner scope_source %s finds no event in OWNER.jsonl (only an event of his "
                    "opens a built thing's scope)" % (w, ", ".join(gone))]
        if not any(_his_word(owner_ev.get(t[6:])) for t in cited):
            return ["%s: opened_by_owner scope_source %s carries none of his words (no ownerSaid or byCard): an "
                    "OWNER-shard event without them is not his opening; a Conductor event per-ruling %s opens it as "
                    "opened_by_conductor with scope_source CONDUCTOR:<tsn>" % (w, ", ".join(cited), CONDUCTOR_AUTHORITY)]
        return []
    cited = [t for t in toks if re.fullmatch(r"CONDUCTOR:[0-9]+", t)]
    other = [t for t in toks if t not in cited]
    if not cited or other:
        return ["%s: opened_by_conductor needs scope_source CONDUCTOR:<tsn> and nothing else%s (the OWNER-shard event, "
                "per-ruling %s, by which the Conductor opened it)" % (
                    w, " (read %s)" % ", ".join(other) if other else "", CONDUCTOR_AUTHORITY)]
    if _ledger_unread(owner_ev):
        return ["%s: opened_by_conductor cites %s, UNMEASURED: OWNER.jsonl was not read here, so the scope stays shut "
                "and no citation is called forged; close this where the ledger is present" % (w, ", ".join(cited))]
    errs = []
    for t in cited:
        ev = owner_ev.get(t[10:])
        if not isinstance(ev, dict):
            errs.append("%s: opened_by_conductor scope_source %s finds no event in OWNER.jsonl" % (w, t))
        elif _his_word(ev):
            errs.append("%s: opened_by_conductor scope_source %s carries his own words: they are stored as his "
                        "(opened_by_owner, OWNER:%s), never as the Conductor's" % (w, t, t[10:]))
        elif ev.get("perRuling") != CONDUCTOR_AUTHORITY:
            errs.append("%s: opened_by_conductor scope_source %s is not per-ruling %s (read %r): only the Conductor's "
                        "standing authority opens a built thing's scope for it" % (
                            w, t, CONDUCTOR_AUTHORITY, ev.get("perRuling")))
    return errs


# ---------------------------------------------------------------- what is already built (stage 0 must account for it)

LIVE_PROOFS = os.path.join("infrastructure", "state", "live_proofs")


def done_items(repo):
    """{item id: title} of the ledger's done items, or None when the ledger cannot be read (UNMEASURED, never 'none
    built'). Only the real repo has a ledger model can fold; a test repo patches this function."""
    if os.path.realpath(repo) != os.path.realpath(REPO):
        return None
    try:
        import model  # noqa: E402  (rimflow's ledger fold, beside this file)
        # one fold per ledger state: a Designer launch built its packet twice in a Dispatcher beat, each calling this
        # twice, so four ~1.7 s replays inside the 20 s beat (RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT)
        stamp = tuple((f, s.st_size, s.st_mtime_ns) for f in model.ledger_files() for s in (os.stat(f),))
        if _DONE_MEMO.get("stamp") != stamp:
            w = model.replay(model.read())
            _DONE_MEMO.clear()
            _DONE_MEMO.update(stamp=stamp, done={i: (getattr(it, "title", "") or "") for i, it in w.items.items()
                                                 if it.state == "done"},
                              closed={i: it.state for i, it in w.items.items() if it.state in CLOSED_STATES})
    except Exception:  # an unreadable ledger is reported as UNMEASURED by the caller
        _DONE_MEMO.clear()
        return None
    return dict(_DONE_MEMO["done"])


_DONE_MEMO = {}
CLOSED_STATES = ("done", "dropped", "superseded")     # model.TERMINAL


def closed_items(repo):
    """{item id: its terminal state (CLOSED_STATES)} from the same ledger fold as done_items, or None when the ledger
    cannot be read (UNMEASURED, never 'nothing closed'). A test repo patches this function."""
    if done_items(repo) is None or "closed" not in _DONE_MEMO:
        return None
    return dict(_DONE_MEMO["closed"])


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
    except FileNotFoundError:
        names = []      # no proofs filed at all
    except OSError as e:    # could not look is not "no proofs" (RIMMANDRAKE_NOTE_UNREADABLE_LIVE_PROOFS_AS_UNMEASURED)
        names = []
        notes.append("live proofs UNMEASURED: %s unreadable (%s)" % (LIVE_PROOFS, e.__class__.__name__))
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
    ids = {e.get("id") for e in inv if isinstance(e.get("id"), str)}    # a bad id is record_errors' to refuse
    seen = json.dumps(inv)
    for r in lst((rec or {}).get("built_reviewed")):
        if isinstance(r, dict) and CT.txt(r.get("ref")) and (
                (isinstance(r.get("covered_by"), str) and r["covered_by"] in ids) or CT.txt(r.get("not_a_capability"))):
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
    present capability unless its scope was opened (OPENED_SCOPES); carries a structured review by someone other than its author."""
    w = "ask[%s]" % ask.get("id")
    errs = []
    if not CT.txt(ask.get("text")):
        errs.append("%s: no text" % w)
    if not CT.txt(ask.get("decision")):
        errs.append("%s: names no unresolved decision it settles" % w)
    inv = {e.get("id"): e for e in rec.get("inventory") or [] if isinstance(e, dict) and _is_id(e.get("id"))}
    about, bad = _ids(ask.get("about"))
    errs += ["%s: about entry %s is not an inventory id (a string)" % (w, b) for b in bad]
    if not about and not lst(ask.get("owner_cites")):
        errs.append("%s: cites neither an inventory entry nor his statements" % w)
    for a in about:
        e = inv.get(a)
        if e is None:
            errs.append("%s: about %s is not in the inventory" % (w, a))
        elif (ask.get("offers_removal") or keep_or_remove(ask.get("text"))) and e.get("impl") == "present" \
                and e.get("scope") not in OPENED_SCOPES:
            errs.append("%s: offers to remove or shrink %s, which is built and whose scope nobody has opened; ask what "
                        "correct behaviour is, or how to show it, instead" % (w, a))
    if not about and keep_or_remove(ask.get("text")):
        errs.append("%s: asks whether to keep or remove something without naming its inventory entry (about); "
                    "find out first whether it is already built" % w)
    rv = ask.get("review")
    if not isinstance(rv, dict) or rv.get("verdict") not in ("pass", "struck"):
        errs.append("%s: no structured review result (verdict pass|struck)" % w)
    elif not CT.txt(ask.get("author")):
        errs.append("%s: names no author, so nothing shows its review is someone else's" % w)
    elif not CT.txt(rv.get("by")) or rv.get("by") == ask.get("author") or (
            same_agent(rv["by"], ask["author"]) or same_agent(ask["author"], rv["by"])):   # by id, as the exam's readers
        # (RIMMANDRAKE_MATCH_ASK_REVIEWER_TO_AUTHOR_BY_AGENT_ID)
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
        leaves = {x.get("id") for x in CT.lst(tree.get("leaves")) if isinstance(x, dict) and _is_id(x.get("id"))}
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
        field = "requirement" if s["kind"] == "acceptance" else "features"
        reqs, bad = _ids(s.get(field))
        errs += ["%s: %s entry %s is not a leaf id (a string)" % (w, field, b) for b in bad]
        if not reqs and not bad:
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
    for s in [s for s in sc["scenes"] if isinstance(s, dict) and s.get("kind") == "interaction" and CT.txt(s.get("id"))]:
        for f in _ids(s.get("features"))[0]:
            if f not in own:
                errs.append("scene[%s]: feature %s has no acceptance scene of its own; an interaction scene never "
                            "stands in for one" % (s["id"], f))
    if isinstance(tree, dict):
        for x in [x for x in CT.lst(tree.get("leaves")) if isinstance(x, dict)]:
            if x.get("leaf_kind") in ("experience", "walk") and x.get("tier_proposed") not in (None, "offline") \
                    and x.get("id") not in own:
                errs.append("leaf %s: a %s leaf off the offline tier has no acceptance scene" % (
                    x.get("id"), x.get("leaf_kind")))
            elif "says" in x and x.get("live_only") is True and x.get("id") not in own:    # a six-part bar
                errs.append("bar %s: a live-only bar has no acceptance scene" % x.get("id"))
    return errs


# ---------------------------------------------------------------- the showcase set
# Owner, 2026-11-05: several showcases, as orthogonal as possible; each later one features ONLY very different
# functionality, until efficient coverage is had. Doctrine: roles/designer_scene_contract.md "The showcase set".

SHOWCASE_RULES = os.path.join(HERE, "showcase_rules.json")
UNIT_SCOPES = ("approved",) + OPENED_SCOPES


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


def showcase_table(sc, rec, tree=None, owner_ev=None, repo=REPO, rules=None, concept=None):
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
            csrc = [x for x in lst(s.get("source")) if isinstance(x, str) and x.startswith("CONDUCTOR:")]
            if dec.get("speaker") == "conductor" and dec.get("delegated") == "evidence-for-ask" and csrc:
                # the Evidence-for-Ask rule: his pick by a recorded delegated call, stored as the Conductor's
                why = efa_problem(owner_ev, csrc, concept) or (
                    ask_waits(rec, dec.get("answers")) if dec.get("answers") else None)
                if why:
                    errs.append("%s: showcase 1 %s" % (w, why))
                if not set(csrc) & set(dsrc) or dec.get("flagship") != s["id"]:
                    errs.append("%s: showcase 1 names no record.json decision (decision) of the delegated pick: "
                                "flagship: \"%s\" citing the same CONDUCTOR event" % (w, s["id"]))
            else:
                if not src:
                    errs.append("%s: showcase 1 is the flagship he picked; source needs his OWNER:<tsn>, or a "
                                "delegated Evidence-for-Ask CONDUCTOR:<tsn>" % w)
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


def showcase_check(sc, rec, tree, owner_ev, repo=REPO, rules=None, concept=None):
    """showcase_table's errs; an unreadable rules file is a refusal reason, never a pass."""
    try:
        return showcase_table(sc, rec, tree, owner_ev, repo, rules, concept)[1]
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


# An agent named in exam.json is free text ("rm-judge a9c647383a06be32f (sonnet)"), so identity is the id a string names,
# never its words: a free-text author cannot be told from a labelled Reader, so everyone in the exam must name an id.
# Agent helpers use a-prefixed hex ids; fresh Claude CLI processes return session UUIDs.
_HELPER_ID = re.compile(r"(?<![\w-])(?:a[0-9a-f]{16}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?![\w-])")
_RUN_ID = re.compile(r"(?<![\w-])rm-role-[a-z-]+-\d+(?![\w-])")
_ROLE = r"self[- ]?read\w*|designer|author|examiner|challenger"
_DENIED_ROLE = re.compile(r"(?<![\w-])not (?:a |an |the )?(?:%s)(?![\w-])" % _ROLE)
_DECLARED_ROLE = re.compile(r"(?<![\w-])(?:%s)(?![\w-])" % _ROLE)


def agent_ids(who):
    """The agent a Reader string names: its helper id, or its run id when it names no helper."""
    w = who.casefold()
    return _HELPER_ID.findall(w) or _RUN_ID.findall(w)


def _no_ids(who):
    return " ".join(_RUN_ID.sub(" ", _HELPER_ID.sub(" ", who.casefold())).split())


def bare_name(who):
    """The words left once the ids, the (annotations), an agent: tag and a leading article are gone."""
    w = " ".join(re.sub(r"\([^)]*\)", " ", _no_ids(who)).replace("agent:", " ").split())
    return re.sub(r"^(the|a|an) ", "", w)


def _names_words(words, text):
    return bool(words) and bool(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(words), text))


def same_agent(reader, other):
    """Does the Reader string name an agent the other string also names? `other` may name several.
    Words decide only where a side names no id: two unnamed Readers, or an open run under a plain name."""
    mine = agent_ids(reader)
    o = other.casefold()
    theirs = _HELPER_ID.findall(o) + _RUN_ID.findall(o)
    if mine and theirs:
        return bool(set(mine) & set(theirs))
    return _names_words(bare_name(other), _no_ids(reader)) or _names_words(bare_name(reader), _no_ids(other))


def declared_role(reader):
    """The role a Reader's own words give it ("agent:a... (the designer, self-read)"), a denial ("not the author") aside."""
    m = _DECLARED_ROLE.search(_DENIED_ROLE.sub(" ", _no_ids(reader)))
    return m.group(0) if m else None


def reader_errors(ex, st):
    """designer_exam.md step 4: two fresh Readers, neither the tree's author nor anyone who saw `expect`."""
    rd = ex.get("readers")
    named = [r for r in rd if CT.txt(r)] if isinstance(rd, list) else []
    if len(named) < 2 or len(named) != len(rd):
        return ["exam: readers needs two named fresh agents (found %d named)" % len(named)]
    errs = []
    if any(same_agent(a, b) or same_agent(b, a) for i, a in enumerate(named) for b in named[i + 1:]):
        errs.append("exam: two readers are the same agent; a scenario is right only when two Readers agree")
    if not CT.txt(ex.get("author")):
        errs.append("exam: author is needed to show no reader is the tree's author")
    for role in ("author", "examiner", "challenger"):
        who = ex.get(role)
        if CT.txt(who) and not (_HELPER_ID.search(who.casefold()) or _RUN_ID.search(who.casefold())):
            errs.append("exam: %s %r names no agent id, so nothing shows no reader is the %s" % (role, who, role))
    running = st.get("running") if isinstance(st, dict) and isinstance(st.get("running"), dict) else {}
    seen = [("author", ex.get("author")), ("examiner", ex.get("examiner")), ("challenger", ex.get("challenger")),
            ("open run", running.get("run"))]
    for r in named:
        ids = agent_ids(r)
        if not ids:
            errs.append("exam: reader %r names no agent id, so nothing shows it is a fresh agent" % r)
        elif ids[0].startswith("rm-role-designer-"):
            errs.append("exam: reader %r is a Designer run; a Designer has seen the log and the record" % r)
        role = declared_role(r)
        if role:
            errs.append("exam: reader %r declares itself %s; a Reader is fresh and never sees expect" % (r, role))
        for role, who in seen:
            if CT.txt(who) and same_agent(r, who):
                errs.append("exam: reader %r is the %s; a Reader is fresh and never sees expect" % (r, role))
    return errs


# designer_exam.md step 5, made by the program (RIMMANDRAKE_RUN_DESIGNER_EXAM_BY_LAUNCHER): `exam-control` writes the
# control Reader's copy, the tree and sheet with one leaf and every line naming it removed, and the gate reads that copy
# rather than a self-reported "removed".
CONTROL_DIR = "exam_control"


def _names_leaf(lid):
    return re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(lid))


def _leaf_ids(tree):
    leaves = tree.get("leaves") if isinstance(tree, dict) else None
    return [x["id"] for x in (leaves if isinstance(leaves, list) else []) if isinstance(x, dict)
            and isinstance(x.get("id"), str)]


def _scrub(v, rx):
    """v with every list entry that names the leaf dropped and every other mention of it blanked out."""
    if isinstance(v, dict):
        return {k: _scrub(x, rx) for k, x in v.items()}
    if isinstance(v, list):
        return [_scrub(x, rx) for x in v if not (isinstance(x, str) and rx.search(x))]
    return rx.sub("(removed)", v) if isinstance(v, str) else v


def _phrase_rx(phrase):
    """A stripped phrase, matched whatever its case and spacing."""
    return re.compile(r"\s+".join(re.escape(w) for w in phrase.split()), re.I)


def _strip_units(v, rx):
    """v with a paraphrase stripped in whole units: a list entry holding it is dropped, any other text holding it
    becomes exactly "(removed)". Never a word cut out of a sentence: that is how a rule gets reversed."""
    if isinstance(v, dict):
        return {k: _strip_units(x, rx) for k, x in v.items()}
    if isinstance(v, list):
        return [_strip_units(x, rx) for x in v if not (isinstance(x, str) and rx.search(x))]
    return "(removed)" if isinstance(v, str) and rx.search(v) else v


def control_copy(tree, sheet_text, leaf, strip=()):
    """Pure. -> (the control tree, the control sheet's lines) for `leaf`: the leaf gone, coverage dropped, every list
    entry and sheet line naming its id gone and any other mention blanked; then each `strip` phrase taken out in whole
    units (_strip_units; every sheet line holding it dropped). exam_control writes this and control_copy_errors
    regenerates it, so the copy on disk is the program's or it is refused."""
    rx = _names_leaf(leaf)
    bad = {k: v for k, v in tree.items() if k != "coverage"}
    bad["leaves"] = [x for x in bad["leaves"] if not (isinstance(x, dict) and x.get("id") == leaf)]
    bad = _scrub(bad, rx)
    sheet = [ln for ln in (sheet_text or "").splitlines() if not rx.search(ln)]
    for ph in strip or ():
        prx = _phrase_rx(ph)
        bad = _strip_units(bad, prx)
        sheet = [ln for ln in sheet if not prx.search(ln)]
    return bad, sheet


def strip_errors(tree, leaf, strip):
    """Why a strip list cannot be applied ([] = it can): each phrase is text with a word in it, and none is found in a
    retained leaf's `id` or `experience` (stripping there would blank the very rule the control must keep)."""
    if not isinstance(strip, (list, tuple)):
        return ["strip is not a list of phrases"]
    errs = []
    kept = [x for x in tree.get("leaves") or [] if isinstance(x, dict) and x.get("id") != leaf]
    for ph in strip:
        if not isinstance(ph, str) or not ph.strip():
            errs.append("strip phrase %r is not text with a word in it" % (ph,))
            continue
        prx = _phrase_rx(ph)
        hit = [str(x.get("id")) for x in kept if any(isinstance(x.get(k), str) and prx.search(x[k])
                                                     for k in ("id", "experience"))]
        if hit:
            errs.append("strip phrase %r is in the id or experience of retained leaf %s: a retained rule is never "
                        "stripped (pick a phrase only the removed rule's paraphrases hold)" % (ph, ", ".join(hit)))
    return errs


def _read_sheet(d):
    try:
        with open(os.path.join(d, "sheet.md"), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def exam_control(d, leaf, strip=None):
    """Write the control copy for `leaf` (control_copy): CONTROL_DIR/tree.json, CONTROL_DIR/sheet.md, and
    CONTROL_DIR/copy.json recording which leaf, from which tree, and the `strip` phrases. A paraphrase of the removed
    rule is named in `strip` and taken out by the program, never by hand
    (RIMMANDRAKE_GUARD_CONTROL_COPY_RETAINED_RULES_ONE_WORD_REVERSES): the gate regenerates the copy from the tree and
    that list and refuses any difference. -> the copy.json record."""
    try:
        tree = CT.load(d)
    except (FileNotFoundError, ValueError) as e:
        raise Refused("exam-control: tree.json cannot be read (%s)" % e)
    if leaf not in _leaf_ids(tree):
        raise Refused("exam-control: %r is not a leaf of the tree" % leaf)
    strip = list(strip or [])
    errs = strip_errors(tree, leaf, strip)
    if errs:
        raise Refused("exam-control: %s" % "; ".join(errs))
    bad, sheet = control_copy(tree, _read_sheet(d), leaf, strip)
    out = os.path.join(d, CONTROL_DIR)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "tree.json"), "w", encoding="utf-8") as f:
        json.dump(bad, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(out, "sheet.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(sheet) + "\n")
    rec = {"leaf": leaf, "base_tree": input_hash(d, "tree"), "base_sheet": input_hash(d, "sheet"),
           "by": "designer_stage.py exam-control", "strip": strip,
           "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(out, "copy.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    return rec


# The control copies hand-stripped before 2026-11-18, when the Designer still stripped paraphrases by hand: (sha256 of
# exam_control/tree.json, of exam_control/sheet.md), CRLF-normalised (sha_file). They are not newly refused for differing
# from the generated copy; any change to one, or to its tree, takes it off this list for good.
HAND_STRIPPED = frozenset((
    ("d32d058c3d2597913d83e489aa306804ee1944bb067853a9e2dd53db6a03295f",
     "23d34bb6cea76e14abb3a3f59b49777761b84e854a33f308c4c0168a5176d65e"),     # GelatinousSlime
    ("5d517802380a6774d3cfe86a3569f67b84027d4b5de1502eb0e6ee8772e8c388",
     "3b555c751fe6e57149beb2494ca657a16abb3e9413c4459fcb33b5108c3b8898"),     # Graffiti
    ("c250db30582277d2e24bac928002e2188448cecfd793b0e38aa332ce7e00eebd",
     "640fb4e1afb5f4930a4244cc993158ce67277501afd3ecc82a041222f40be6db"),     # Stillsand
))


def control_copy_errors(d, leaf, ids):
    """The control copy on disk is the one the program generates from the current tree with `leaf` removed and the
    recorded phrases stripped, or the reasons it is not."""
    how = "make it with `designer_stage.py exam-control %s --leaf %s` and rerun the control Reader on it" % (d, leaf)
    try:
        rec = read_json(os.path.join(d, CONTROL_DIR, "copy.json"))
    except Refused as e:    # a rejection of the run, never a crash that leaves it open
        return ["exam: the control copy's %s; %s" % (e, how)]
    if not isinstance(rec, dict) or rec.get("leaf") != leaf:
        return ["exam: no control copy with %r removed (%s/copy.json); %s" % (leaf, CONTROL_DIR, how)]
    errs = []
    if rec.get("base_tree") != input_hash(d, "tree"):
        errs.append("exam: the control copy was made from another tree than the current one; %s" % how)
    try:
        bad = CT.load(os.path.join(d, CONTROL_DIR))
    except (FileNotFoundError, ValueError):
        return errs + ["exam: the control copy %s/tree.json cannot be read; %s" % (CONTROL_DIR, how)]
    if sorted(_leaf_ids(bad)) != sorted(i for i in ids if i != leaf):
        errs.append("exam: the control copy's leaves are not the tree's minus %r (it removed %s, added %s); %s" % (
            leaf, sorted(set(ids) - set(_leaf_ids(bad)) - {leaf}) or "nothing else",
            sorted(set(_leaf_ids(bad)) - set(ids)) or "nothing", how))
    rx = _names_leaf(leaf)
    if rx.search(CT.canon(bad)):
        errs.append("exam: the control copy's tree still names %r; %s" % (leaf, how))
    sheet_path = os.path.join(d, CONTROL_DIR, "sheet.md")
    try:
        with open(sheet_path, encoding="utf-8") as f:
            sheet_now = f.read()
    except (OSError, ValueError):
        return errs + ["exam: the control copy has no readable sheet.md; %s" % how]
    if rx.search(sheet_now):
        errs.append("exam: the control copy's sheet.md still names %r; %s" % (leaf, how))
    # the retained rules: the copy is the program's own output, byte for byte, or a hand edit could reverse one
    # ("must not climb" -> "must climb") and the control Reader's miss would prove nothing
    if (sha_file(os.path.join(d, CONTROL_DIR, "tree.json")), sha_file(sheet_path)) in HAND_STRIPPED:
        return errs
    if rec.get("base_tree") != input_hash(d, "tree"):
        return errs     # made from another tree (said above): comparing it with this tree's copy would say nothing new
    strip = rec.get("strip") if "strip" in rec else []
    try:
        tree = CT.load(d)
    except (FileNotFoundError, ValueError):
        tree = None
    serr = strip_errors(tree, leaf, strip) if isinstance(tree, dict) and leaf in _leaf_ids(tree) else [
        "the current tree.json cannot be read, or no longer has the leaf"]
    if serr:
        return errs + ["exam: the control copy cannot be regenerated to compare (%s); %s" % ("; ".join(serr), how)]
    want, want_sheet = control_copy(tree, _read_sheet(d), leaf, strip)
    more = " --strip ..." if strip else ""
    if json.loads(json.dumps(want)) != bad:
        errs.append("exam: the control copy's tree.json is not the copy the program generates from the current tree%s "
                    "(edited by hand, or a strip the record does not name); name a paraphrase with --strip, never edit "
                    "the copy; %s%s" % (" and the %d recorded phrase(s)" % len(strip) if strip else "", how, more))
    # the sheet is compared only against the sheet the copy was made from: an exam carried past a sheet-only repair
    # (exam_retake) keeps its control copy, and a copy made before base_sheet was recorded cannot say which sheet that was
    if rec.get("base_sheet") == input_hash(d, "sheet") and sheet_now.replace("\r\n", "\n") != "\n".join(want_sheet) + "\n":
        errs.append("exam: the control copy's sheet.md is not the copy the program generates from the current sheet%s "
                    "(edited by hand, or a strip the record does not name); name a paraphrase with --strip, never edit "
                    "the copy; %s%s" % (" and the %d recorded phrase(s)" % len(strip) if strip else "", how, more))
    return errs


def _source_ok(src, ids, owner_ev):
    src = CT.txt(src)
    if src.startswith("OWNER:"):
        return src[len("OWNER:"):] in owner_ev
    return (src[len("leaf:"):] if src.startswith("leaf:") else src) in ids


EXAM_VERDICTS = ("accept", "reject")


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
    ids = _leaf_ids(tree)
    owner_ev = None
    seen_id, seen_text = {}, {}
    for i, s in enumerate(sc):
        if not isinstance(s, dict) or not CT.txt(s.get("expect")) or not CT.txt(s.get("expect_source")):
            errs.append("exam: scenario %d needs expect and expect_source (a leaf id or OWNER:<tsn>)" % i)
            continue
        if not CT.txt(s.get("id")) or not CT.txt(s.get("text")):
            errs.append("exam: scenario %d needs an id and its text" % i)
            continue
        if CT.txt(s["expect"]).split(":", 1)[0].strip().casefold() not in EXAM_VERDICTS:
            errs.append("exam: scenario %s's expect %r carries no verdict word; it must begin with 'accept' or "
                        "'reject' (then ':' and the reason), or the score has no defined right answer"
                        % (s["id"], CT.txt(s["expect"])))
        norm = " ".join(CT.txt(s["text"]).casefold().split())
        for key, seen, what in ((CT.txt(s["id"]), seen_id, "id"), (norm, seen_text, "text")):
            if key in seen:
                errs.append("exam: scenario %d has the same %s as scenario %d; every scenario is a different "
                            "situation" % (i, what, seen[key]))
            seen.setdefault(key, i)
        if CT.txt(s["expect_source"]).startswith("OWNER:") and owner_ev is None:
            owner_ev = CT.owner_events(repo, clone_of(d))
        if not _source_ok(s["expect_source"], ids, owner_ev or {}):
            errs.append("exam: scenario %s's expect_source %r is neither a leaf of the tree nor one of his OWNER "
                        "events" % (s["id"], s["expect_source"]))
    cur = inputs(d, st, repo)
    fr = ex.get("inputs") if isinstance(ex.get("inputs"), dict) else {}
    for k in ("tree", "sheet"):
        if fr.get(k) != cur.get(k):
            errs.append("exam: run against another %s than the current one; rerun it" % k)
    score = ex.get("score") if isinstance(ex.get("score"), dict) else {}
    right, total = score.get("right"), score.get("total")
    if not (type(right) is int and type(total) is int and right >= 0     # type(): bool is an int in Python
            and total >= EXAM_MIN and total == len(sc)):
        errs.append("exam: score needs right and total, total = the number of scenarios")
    elif right > total:
        errs.append("exam: %d/%d has right above total; no exam scores more than it asked" % (right, total))
    elif right < EXAM_PASS * total:
        errs.append("exam: %d/%d is under %d%%" % (right, total, EXAM_PASS * 100))
    if type(ex.get("accept_where_reject_core")) is not int or ex.get("accept_where_reject_core") != 0:
        errs.append("exam: accept_where_reject_core must be 0")
    # by agent id, as the readers are (RIMMANDRAKE_MATCH_EXAMINER_TO_AUTHOR_BY_ID_NOT_LABEL): one id under two labels
    # is one agent
    au = ex.get("author")
    if not CT.txt(ex.get("examiner")) or ex.get("examiner") == au or (
            CT.txt(au) and (same_agent(ex["examiner"], au) or same_agent(au, ex["examiner"]))):
        errs.append("exam: the examiner is not the tree's author")
    errs += reader_errors(ex, st)
    # designer_exam.md step 3: a Challenger, a fresh agent, wrote scenarios that joined the set before the freeze
    ch = CT.txt(ex.get("challenger"))
    mine = {CT.txt(s.get("id")) for s in sc if isinstance(s, dict) and s.get("by") == "challenger"}
    if not ch:
        errs.append("exam: no challenger named; a fresh Challenger writes the scenarios most likely to make a Reader "
                    "accept what a core line rejects")
    else:
        for role in ("author", "examiner"):
            if CT.txt(ex.get(role)) and (same_agent(ch, ex[role]) or same_agent(ex[role], ch)):
                errs.append("exam: the challenger is the %s; the Challenger is a fresh agent" % role)
    if not mine:
        errs.append('exam: no scenario is the Challenger\'s (mark them "by": "challenger" before the freeze)')
    for m in lst(ex.get("challenger_misses")):
        if not isinstance(m, dict) or not CT.txt(m.get("accounted")):
            errs.append("exam: every challenger miss is accounted for")
        elif CT.txt(m.get("id")) not in mine:
            errs.append("exam: challenger miss %r is not one of the Challenger's scenarios" % m.get("id"))
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
        else:
            by_id = {CT.txt(s.get("id")): s for s in sc if isinstance(s, dict)}
            miss = [x for x in lst(ctl.get("missed_ids")) if CT.txt(x)]
            if not miss or any(x not in by_id for x in miss):
                errs.append("exam: control missed_ids must name the scenarios the control Reader got wrong (read %r)"
                            % ctl.get("missed_ids"))
            elif not any(_source_ok(by_id[x].get("expect_source"), [ctl["broken_leaf"]], {}) for x in miss):
                errs.append("exam: no control miss is a scenario sourced on %r; a miss elsewhere is not the removal's"
                            % ctl["broken_leaf"])
        if ctl.get("broken_leaf") in ids:
            errs += control_copy_errors(d, ctl["broken_leaf"], ids)
    # RIMMANDRAKE_RETAKE_ONLY_TOUCHED_EXAM_SCENARIOS_CARD_ASKED_TWICE: an answer carried from an earlier exam stands only
    # while its scenario and every unit of the tree and sheet it read are as they were when it was answered
    errs += ER.carry_errors(ex, d)
    return errs


# ---------------------------------------------------------------- results

def quick_look_errors(res, rec):
    """E (owner, OWNER.jsonl:1794527688430451936: "If we can insert an owner quick-look to settle a difficult or several
    questions swiftly, offer that loudly."): once code exists, a result that asks him something says whether a look
    would settle it, {"offer": true, "settles": [ids], "scene": ...} or {"offer": false, "why": ...}. -> errors."""
    if not code_present(rec):
        return []
    ql = res.get("quick_look")
    if not isinstance(ql, dict) or not isinstance(ql.get("offer"), bool):
        return ["code exists (%s): a result that asks him carries quick_look, {offer: true, settles, scene} or "
                "{offer: false, why}" % ", ".join(code_present(rec)[:5])]
    if ql["offer"]:
        settles = [x for x in lst(ql.get("settles")) if CT.txt(x)]
        return ([] if settles else ["quick_look offer names nothing it settles (settles)"]) + (
            [] if CT.txt(ql.get("scene")) else ["quick_look offer says nothing of what he would see (scene)"])
    return [] if CT.txt(ql.get("why")) else ["quick_look declined without why"]


def _run_file(d, name, errs):
    """A run's own file, or None with its parse failure added to errs: a rejection, never a crash that leaves the run
    open (RIMMANDRAKE_REJECT_MALFORMED_RUN_FILES_SECOND_PASS_EXAM_SCENES)."""
    try:
        return read_json(os.path.join(d, name))
    except Refused as e:
        errs.append(str(e))
        return None


def result_errors(res, d, st, repo=REPO):
    """Why this run's result.json cannot be accepted, or []."""
    if not isinstance(res, dict):
        return [NO_RESULT + " (a closing message is not a result)"]
    out, stage = res.get("outcome"), st["stage"]
    if res.get("stage") != stage:
        return ["result is for stage %r; the state is at stage %d" % (res.get("stage"), stage)]
    if res.get("run") != (st.get("running") or {}).get("run"):
        return ["result names run %r, not the open run %r" % (res.get("run"), (st.get("running") or {}).get("run"))]
    if out not in OUTCOMES:
        return ["outcome %r is not one of %s" % (out, "/".join(OUTCOMES))]
    owner_ev = CT.owner_events(repo, clone_of(d))
    try:
        rec = read_json(os.path.join(d, "record.json"))
    except Refused as e:    # the run's own file: a rejection, never a crash (RIMMANDRAKE_REJECT_MALFORMED_DESIGNER_RESULTS_NOT_CRASH)
        return [str(e)]
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
        return quick_look_errors(res, rec) if CT.txt(res.get("question")) else []
    # Dispatcher closes a package written in another clone. Resolve its artifacts beside the concept,
    # while owner_events above continues to merge evidence from both clones.
    artifact_repo = clone_of(d) or repo
    errs = record_errors(rec, artifact_repo, owner_ev, concept_of(st, d))
    if rec is not None and (not isinstance(rec, dict) or any(not isinstance(rec.get(k, []), list) for k in (
            "scope", "decisions", "asks", "inventory", "contradictions"))):
        return errs     # record_errors named the shape; the checks below would only crash on it
    if out == "waiting_owner":
        if stage not in DIALOGUE:
            return ["only stages 1-2 send him questions; stage %d returns to stage 2 with the question" % stage]
        errs += quick_look_errors(res, rec)
        if not st.get("item"):
            # his answers are read on the concept's item: with none, the wait could never see one
            errs.append("waiting_owner needs the concept's item (stage.json item): his answers are read on it")
        elif owner_feed(repo, st.get("item"), d) is None:
            # the wait's baseline: a null one never moves, so he would answer into a concept that waits for good
            # (RIMMANDRAKE_REFUSE_WAITING_RESULT_WITHOUT_FEED_BASELINE)
            errs.append("waiting_owner UNMEASURED: his feed (OWNER.jsonl) could not be read here, so the wait has no "
                        "baseline to see his answer against; close it where the ledger is readable")
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
        lint_errs, _ = CT.lint(d, artifact_repo)
        errs += ["lint: %s" % e for e in lint_errs]
        tree = CT.load(d) if not lint_errs else None
        sc3 = _run_file(d, "scenes.json", errs)
        errs += scene_errors(sc3, tree, artifact_repo)
        errs += ["showcases: %s" % e for e in showcase_check(sc3, rec, tree, owner_ev, artifact_repo,
                                                              concept=concept_of(st, d))]
        errs += floor_errors(_run_file(d, "floor.json", errs), tree, owner_ev=owner_ev)
    elif stage == 4:
        errs += exam_errors(_run_file(d, "exam.json", errs), d, st, repo)
    elif stage == 5:
        # the judge signs concept=<its path in the concept's own clone>: the Dispatcher closing from its clone reads that one
        gate_errs, _ = CT.gate(d, clone_of(d) or repo)
        errs += ["gate: %s" % e for e in gate_errs]
        # the lock refuses while a capability is exercised by no showcase and no scene (record.json can move after
        # stage 3: an inventory line added since then is caught here)
        try:
            tree = CT.load(d)
        except (FileNotFoundError, ValueError):
            tree = None
        sc5 = _run_file(d, "scenes.json", errs)
        # the showcase set names scenes, so the scenes it leans on must still meet the contract at the lock (a scene
        # added after stage 3 is checked here, not trusted by its id)
        # judged in the concept's own clone, as stage 3 judges them (RIMMANDRAKE_ALIGN_STAGE5_SCENE_CHECK_CLONE_READ_WRONG_TREE)
        errs += ["scenes: %s" % e for e in scene_errors(sc5, tree, artifact_repo)]
        errs += ["showcases: %s" % e for e in showcase_check(sc5, rec, tree, owner_ev, artifact_repo,
                                                              concept=concept_of(st, d))]
        # his words on the mod's items given since the concept began must be taken in before it locks
        # (RIMMANDRAKE_HARVEST_OWNER_WORDS_OFF_CONCEPT_ITEM_FOURTH_ASK)
        _, bind = elsewhere_binding(repo, d, st)
        if bind is None:
            errs.append("lock: his words on the mod's items could not be read (OWNER.jsonl or a ledger shard unread): "
                        "not locked blind")
        elif bind:
            errs.append("lock: %d of his words on the mod's items, given since this concept began, are not cited "
                        "in record.json or tree.json: %s" % (len(bind), ", ".join("OWNER:" + t for t in bind[:15]) +
                                                             ("" if len(bind) <= 15 else ", ...")))
    return errs


# ---------------------------------------------------------------- the launcher's verbs

def state_path(d):
    return os.path.join(d, "stage.json")


def load_state(d):
    st = read_json(state_path(d))
    if not isinstance(st, dict):
        raise Refused("no stage.json in %s (designer_stage.py init)" % d)
    upgrade_cap(st)
    import run_void     # a VOID run's looks, results and retries count nothing (RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT)
    return run_void.sync_stage(st)


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


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def draft_line(st):
    """The packet's line naming a draft another model made, given as input to VERIFY (never the run's output), with
    its sha checked now. None when the concept has no draft (item RIMMANDRAKE_SEED_DESIGNER_WITH_A_DRAFT_TO_VERIFY)."""
    dr = st.get("draft_input")
    if not isinstance(dr, dict) or st.get("stage") not in (0, 1, 2, 3):
        return None
    try:
        now = file_sha(dr["path"])
    except (OSError, KeyError, TypeError):
        now = None
    state = ("sha256 %s, unchanged since init" % dr.get("sha256", "")[:12] if now == dr.get("sha256") else
             "UNREADABLE now: treat it as absent" if now is None else
             "CHANGED since init (sha256 now %s): treat every line as unverified" % now[:12])
    return ("A DRAFT TO VERIFY, not your output: %s (%s; made by %s). Another model drafted this pass. Use it only "
            "as a map of what to check: confirm every claim, file:line, defName and quote against the source yourself "
            "before you rely on it, record nothing from it you did not verify, and cite the source, never the draft. "
            "Where it is wrong or missing something, say so in record.json." % (
                dr.get("path"), state, dr.get("by") or "another model"))


def helper_line(st):
    """A Codex Designer at the exam cannot spawn Claude subagents, and its examiners must not be its own model: the
    packet tells it how to start them on Claude (item RIMMANDRAKE_START_CODEX_DESIGNER_EXAMINERS_ON_CLAUDE). None else."""
    if st.get("runner") != "codex" or st.get("stage") != 4:
        return None
    return ("You run on Codex; your exam helpers do not. The Examiner, Challenger, both Readers and the Control are Claude "
            "(Opus), so the maker and its examiners are different models. Start each as its own fresh process from the "
            "repo root: `src/RimMandrake/Utils/claude_bounded.sh -p --model opus --effort high --output-format json "
            "--dangerously-skip-permissions \"<its brief>\"`, "
            "give it only the files its rule allows, name it in exam.json by the session_id its JSON returns, and charge "
            "its usage with `designer_stage.py charge --kind helper`. Never play a helper yourself.")


def init(d, mod, item=None, cap=DEFAULT_CAP, reserve=DEFAULT_RESERVE, aliases=(), runner=None, draft=None,
         draft_by=None):
    """runner: the concept's own runner (claude|codex), read by every later launch of it, the tick's orphan sweep and
    chain included (item RIMMANDRAKE_DRAFT_BIOME_DESIGNER_PASSES_WITH_CODEX_BEFORE_RESET); None = the role's default."""
    if runner not in (None, "claude", "codex"):
        raise Refused("runner must be claude or codex")
    if os.path.exists(state_path(d)):
        raise Refused("stage.json already exists in %s" % d)
    if not (0 < reserve < cap):
        raise Refused("reserve must be above 0 and below the cap")
    os.makedirs(d, exist_ok=True)
    st = {"schema": 1, "mod": mod, "item": item, "aliases": list(aliases or []), "stage": 0, "status": "ready",
          "budget": {"cap": cap, "reserve": reserve, "spent": 0, "charges": []},
          "running": None, "results": [], "recovery": [], "history": []}
    if runner:
        st["runner"] = runner
    if draft:
        if not os.path.isfile(draft):
            raise Refused("--draft %s is not a readable file" % draft)
        st["draft_input"] = {"path": os.path.abspath(draft), "sha256": file_sha(draft), "by": draft_by,
                             "use": "input to verify, never the output"}
    hist(st, "init", "stage 0, budget %d (reserve %d)%s" % (cap, reserve, ", runner %s" % runner if runner else ""))
    write_json(state_path(d), st)
    return st


def pin_scale(st):
    """-> the price ratio of the builder model pin of st's mod (mod_model.cap_scale, a Fraction; 1 when unpinned), read
    from the control store at each use, so a pin set or lifted later moves the budget at once (item
    RIMMANDRAKE_PRICE_CEILING_AND_DESIGNER_TOKENS_FOR_PINNED_MODEL). DEFAULT_CAP was measured on Opus runs and a token
    is weighed at its model's price (role_launch.MODEL_PRICES), so a pinned mod's task gets the same work. A store that
    cannot be read, or a pin with no price, gives 1: the shipped budget, the stricter (control refuses that mod's
    launch anyway, design/specs/2026-11-19-mod-model-pin/boundary.md)."""
    import control as C
    import mod_model as MM
    try:
        alias = MM.read_pins().get(C.key(st.get("mod")))
        return MM.cap_scale(alias) if alias else 1
    except (C.Unreadable, KeyError):
        return 1


def task_cap(st, x=None):
    """-> the task's weighted-token budget now: its recorded cap times pin_scale (x, when the caller read it already)."""
    x = pin_scale(st) if x is None else x
    return int(int((st.get("budget") or {}).get("cap") or DEFAULT_CAP) * x)


def remaining(st):
    return task_cap(st) - st["budget"]["spent"]


def run_budget(st, run_cap=None):
    """-> (the next run's budget, over): what the task has left past its reserve, at most the run's cap; both scaled by
    pin_scale (the Designer's run_token_cap is an Opus figure too). Over the task budget the run goes on with a whole
    task's room, advisory (owner 2026-11-04: "These budgets make no sense. All they do is stop work")."""
    x = pin_scale(st)
    cap, reserve = task_cap(st, x), st["budget"]["reserve"]
    left = cap - st["budget"]["spent"] - reserve
    over = left <= 0
    if over:
        left = cap - reserve
    run_cap = int(run_cap * x) if run_cap else run_cap
    return (min(left, run_cap) if run_cap else left), over


def open_run(d, run, run_cap=None, repo=REPO, manifest=MANIFEST, commit=True, parent=None):
    """-> (packet text, this run's budget). Refuses (Refused) when a scene's
    recovery is open, the concept is locked, or it waits on him or a dependency. commit=False is the launcher's
    preview (its decide step): the same checks and packet, nothing written."""
    st = load_state(d)
    if st.get("running"):
        # the last run never closed: it is a retry now, and what it reserved is charged (conservative)
        prev = st["running"]
        if prev.get("runner") == "codex":
            st.setdefault("runner_spend", []).append({"runner":"codex", "run":prev.get("run"), "usage":"UNMEASURED"})
            hist(st, "retry", "Codex run %s never closed; usage UNMEASURED" % prev.get("run"))
        else:
            charge_state(st, prev.get("reserved", 0), "unmeasured", "run %s never closed" % prev.get("run"))
            hist(st, "retry", "run %s never closed; its reservation %d is charged" % (prev.get("run"), prev.get("reserved", 0)))
        st["running"] = None
    lift_closed_block(st, repo)     # a block whose item closed is read again; commit writes the lift with the rest
    why = reopen_if_stale(d, st, repo)
    try:
        if st.get("status") == "locked":
            raise Refused("LOCKED: changing a locked tree is his word only (an amendment comes back as a new concept)")
        if st.get("status") == "blocked":
            raise Refused("BLOCKED on %s: nothing runs until it ends (clear it with `unblock`)" % st.get("blocked_on"))
        lift_park(st, d, repo)    # his word since the park, or since the loop crossed its ceiling, lifts it
        if isinstance(st.get("park"), dict):
            raise Refused("PARKED (%s): %s; nothing opens until his word on %s (he reads %s)" % (
                st["park"].get("kind"), st["park"].get("why"), st.get("item"), os.path.join(d, PARK_FILE)))
        ceil = loop_ceiling(st)
        if ceil:    # the judge-and-rework loop's hard ceiling (card: "Twice the item's cap, then park")
            if commit:
                park(d, "ceiling", ceil, repo, st)
            raise Refused("PARKED (ceiling): %s; nothing opens until his word on %s" % (ceil, st.get("item")))
        if st.get("status") == "waiting_owner" and not owner_moved(st, d, repo):
            raise Refused("WAITING_OWNER: no new owner event since the asks went out; silence never advances")
        opn = [r for r in st.get("recovery") or [] if r.get("state") == "open"]
        if opn:
            raise Refused("RECOVERY_PENDING: scene(s) %s changed persistent state and never restored; restore them "
                          "(scene-end) before any further work" % ", ".join(r["scene"] for r in opn))
    except Refused as e:
        if commit:
            if st.get("status") not in ("locked",):
                hist(st, "refused", str(e))
            write_json(state_path(d), st)
        raise
    budget, over = run_budget(st, run_cap)
    if over:        # advisory, never a stop (run_budget)
        hist(st, "over_budget", "%d of %d spent; run %s goes on with %d (advisory)" % (
            st["budget"]["spent"], task_cap(st), run, budget))
    hashes = manifest_hashes(st["stage"], manifest)
    retries = stage_retries(st)
    st["running"] = {"run": run, "stage": st["stage"], "manifest": hashes, "reserved": budget, "at": now_iso(),
                     "inputs": inputs(d, st, repo), "owner_uncited": owner_uncited(repo, st.get("item"), d)}
    if st.get("status") == "waiting_owner":
        st["status"] = "ready"
    hist(st, "open", "run %s, stage %d, budget %d" % (run, st["stage"], budget))
    if parent:      # the detached run that asked for it (role_launch.with_parent): run_void.children reads it
        st["running"]["parent"] = st["history"][-1]["parent"] = parent
    # built before the run is saved: a packet that raises leaves no run that never launched to be charged at the next
    # open (RIMMANDRAKE_BUILD_PACKET_BEFORE_SAVING_OPEN_RUN_PHANTOM_CHARGE)
    text = packet(d, st, hashes, budget, why, retries, manifest, repo)
    if commit:
        write_json(state_path(d), st)
    return text, budget


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
    if w is None:
        return False
    now = owner_feed(repo, st.get("item"), d)
    if now is None:     # could not look is not his answer (RIMMANDRAKE_REFUSE_UNREADABLE_OWNER_FEED_BLIND_IS_NO_REPLY)
        raise Refused("WAITING_OWNER UNMEASURED: the OWNER shard could not be read here, so whether he answered is "
                      "unknown; nothing opens blind (rerun where OWNER.jsonl is readable)")
    return now != w


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


# RELAPSE_QUEUES_FIX_DIED_TWICE: the Dispatcher's orphan sweep (role_launch.chain_sweep) skipped EVERY concept whose
# last result was rejected while ops_watch's queues.designer stall reader counted every ready concept, so the stall
# alarm rang (incident queues-20261105210826, three acks whose fixes died) on concepts nothing would ever move: GSS
# stage 2 sat 6 h after the coverage_verdict.json its rejection cited had landed. One rule now serves both readers:
# a rejected-last concept is PARKED (no retry helps; the stage_rejected alarm and its route own it) or it is due a
# retry (the sweep re-chains it with the reasons; the stall alarm counts it until that run opens).
MISSING_PATH_RX = re.compile(r"source path (.+?) does not exist")
PARK_CLASSES = ("check", "bar", "environment")   # role_launch.CAUSE_ROUTE sends these to the Setter or the cause book
_PARK_MASK = re.compile(r"rm-role-[a-z]+-\d+|\b\d{6,}\b")

# the history rows that take a stopped or blocked concept's cause away (rejection_parked: a retry is due after one)
RELEASE_KINDS = ("coverage_release", "unblock")


NO_RESULT = "no result.json"     # result_errors' reason when the run left none


def stage_retries(st):
    """-> the rejected or unclosed runs at the current stage, a void_system one (void_rejection) not counted."""
    return sum(1 for h in st.get("history") or [] if isinstance(h, dict) and h.get("what") == "retry"
               and h.get("stage") == st.get("stage") and not h.get("void_system"))


def void_rejection(d, run, cause):
    """RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS (run_void.py; owner 2026-11-18: "I will not accept ANY
    system that pointlessly expends such statistical measurements based on failed system calls or behavior"): run's
    rejected result was the machine's, not the run's (role_launch.void_cause: killed at run_max_s, or the unit ended
    with no claude result of its own), so its rejection row and its retry row are marked `void_system` with the cause:
    no retry in the packet, no rejection for rejection_parked. Only a rejection whose every reason is NO_RESULT is
    marked (a result the run did write was judged on its merits). -> True when marked, False when there is nothing to
    mark."""
    st = load_state(d)
    res = [r for r in st.get("results") or [] if isinstance(r, dict) and r.get("run") == run
           and r.get("outcome") == "rejected"]
    why = [str(w) for w in (res[-1].get("why") or [])] if res else []
    if not why or not all(w.startswith(NO_RESULT) for w in why) or res[-1].get("void_system"):
        return False
    res[-1]["void_system"] = cause
    pat = re.compile(r"run %s result rejected" % re.escape(run))
    for h in st.get("history") or []:
        if isinstance(h, dict) and h.get("what") == "retry" and pat.match(str(h.get("why") or "")):
            h["void_system"] = cause
    hist(st, "void_system", "run %s: %s; its rejection spends no retry" % (run, cause))
    write_json(state_path(d), st)
    return True


def rejection_parked(st, repo=REPO):
    """Pure but for os.path.exists. -> why a ready concept whose last result is REJECTED is parked (a retry cannot
    help), or None when it is not parked (no rejected last result, or the rejection's cause is gone so a retry is due).
    Parked: a reason labelled [cause:check|bar|environment] (routed to the Setter or the cause book, never to the
    builder); a cited source path that still does not exist under `repo` (close_run judges against designer_stage.
    REPO); or, when no path is cited, the last two
    results are rejections at the same stage with the same reasons, run names masked (a retry already met it: the
    identical-rejection route goes to the arbiter). Every cited path landed after the rejection = not parked, even
    after two identical rejections (GSS: rejected 09:14Z and 10:13Z for the file that landed at 10:12Z)."""
    res = [r for r in (st or {}).get("results") or [] if isinstance(r, dict) and not r.get("void_system")]
    if not res or res[-1].get("outcome") != "rejected":
        return None
    why = [str(w) for w in (res[-1].get("why") or [])]
    tags = {m for w in why for m in re.findall(r"\[cause:([a-z]+)\]", w)} & set(PARK_CLASSES)
    if tags:
        return "rejection labelled %s: routed to %s, not to a retry" % (
            "+".join(sorted(tags)), "the Setter" if tags - {"environment"} else "the cause book")
    cited = sorted({m.group(1) for w in why for m in MISSING_PATH_RX.finditer(w)})
    if cited:
        missing = [c for c in cited if not os.path.exists(os.path.join(repo, c))]
        if missing:
            return "the rejection cites %s, still missing" % ", ".join(missing)
        # close_run judged the same repo and found them missing, so every one has landed since: the cause is gone.
        # No mtime test (a copy that keeps mtimes would park a fixed concept for good); chain_ask's daily cap bounds it.
        return None
    if len(res) >= 2 and res[-2].get("outcome") == "rejected" and res[-2].get("stage") == res[-1].get("stage"):
        # a release after the rejection (coverage_judge release, designer_stage unblock) took its cause away: Contagion's
        # two stage-5 rejections were the judge's own stop, and the owner's one more look (16:03Z) came after them
        # (RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING)
        last_at = _epoch(res[-1].get("at"))
        if last_at is not None and any(isinstance(h, dict) and h.get("what") in RELEASE_KINDS
                                       and (_epoch(h.get("at")) or 0) > last_at for h in st.get("history") or []):
            return None
        sig = lambda r: sorted(_PARK_MASK.sub("#", str(w)) for w in r.get("why") or [])  # noqa: E731
        if sig(res[-2]) == sig(res[-1]):
            return "rejected twice in a row for the same reasons: the arbiter's, not a third run"
    return None


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


# ---------------------------------------------------------------- parked for him: away, and the loop ceiling
# RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS and RIMMANDRAKE_CEIL_JUDGE_LOOPS_AT_TWICE_CAP (owner note
# OWNER.jsonl:1794527688430451936, card OWNER.jsonl:1794527885746395760, on
# RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS). ExplosiveKnockback's night: nine coverage verdicts and their
# rework runs in three and a half hours, while he slept, against a 4M cap. Now, when he is away, a Designer step that
# ends in his certification and the SECOND refusal of a concept both PARK it: status waiting_owner, a one-page plain
# summary for him (park_summary.md), and nothing opens again, no Designer run, no judge, until his own word (ownerSaid
# or byCard) names the item. And a judge-and-rework loop parks the same way at twice the item's cap, attended or not
# (the card: "Twice the item's cap, then park"); building work outside such a loop stays advisory (owner 2026-11-04).
LOOP_CEILING_FACTOR = 2
PARK_FILE = "park_summary.md"
PARK_KINDS = ("second_refusal", "certification", "ceiling")
JUDGE_REF = "rm-coverage-judge-"     # coverage_judge.UNIT_PREFIX (that module imports this one)


def owner_away():
    """-> (away?, why). Away when $RIMFLOW_MODE is afk, or his last
    deliberate interaction (an OWNER ledger act, ./bridge, a chat prompt or card answer; owner_interaction.py) is 45+
    min old (no sitting), or that cannot be measured: parking is the safe side. Never his keyboard or input clock."""
    try:
        import cli
        mode = str(os.environ.get("RIMFLOW_MODE") or "").strip().lower()
        if mode == "afk":
            return True, "RIMFLOW_MODE is afk"
        takeable, text = cli._owner_verdict([])
    except Exception as e:  # noqa: BLE001 - an unreadable presence parks, it never runs on
        return True, "his presence could not be read (%s): treated as away" % e
    if takeable:
        return True, "no sitting: %s" % text
    if str(text).startswith("his last interaction is UNMEASURED"):
        return True, "%s: treated as away" % text
    return False, text


def code_present(rec):
    """Enough code exists to look at (E, owner note 1794527688430451936: the Designer often runs on a mod not written
    yet): record.json's inventory has a capability with impl `present`. -> the ids, [] when none."""
    inv = rec.get("inventory") if isinstance(rec, dict) else None
    return [e.get("id") for e in (inv if isinstance(inv, list) else [])
            if isinstance(e, dict) and e.get("impl") == "present" and e.get("id")]


def loop_void_refs(st):
    """-> the charge refs whose spend is void (owner 2026-11-18: no system failure spends a counter): a hand-voided run's
    or judge's (run_void.sync_stage's spend_refs), a void_system judge round's and its second reader's
    (coverage_judge.void_cause), a second reader that died, and a Designer run whose rejection is void_system
    (void_rejection). Their spend is true spend, shown apart; the loop ceiling counts none of it."""
    import coverage_judge as CJ
    import run_void
    refs = set(run_void.stage_spend_refs(st))
    for r in st.get("coverage_rounds") or []:
        if isinstance(r, dict) and r.get("judge"):
            if CJ.void_cause(r):
                refs |= {r["judge"], r["judge"] + CJ.READER_SUFFIX}
            elif r.get("reader_void_system"):
                refs.add(r["judge"] + CJ.READER_SUFFIX)
    refs |= {"run %s" % r["run"] for r in st.get("results") or [] if isinstance(r, dict) and r.get("run")
             and r.get("void_system")}
    return refs


def _loop_charges(st, void=False):
    """-> the budget charges the loop counts (void=True: the void ones instead)."""
    refs = loop_void_refs(st)
    return [c for c in (st.get("budget") or {}).get("charges") or []
            if isinstance(c, dict) and (str(c.get("ref") or "") in refs) == void]


def loop_start(st):
    """-> epoch the current judge-and-rework loop began, or None when no judge has run (no loop: advisory budget). It
    begins at the first judge round (or the first judge charge, before rounds were recorded) and restarts when his word
    lifts a park. A void judge round or charge (loop_void_refs) begins none."""
    import coverage_judge as CJ
    ats = [epoch(r.get("at")) for r in st.get("coverage_rounds") or [] if isinstance(r, dict) and not CJ.void_cause(r)]
    ats += [epoch(c.get("at")) for c in _loop_charges(st) if str(c.get("ref") or "").startswith(JUDGE_REF)]
    ats = [a for a in ats if a is not None]
    if not ats:
        return None
    return max([min(ats)] + [a for a in [epoch(st.get("loop_since"))] if a is not None])


def loop_spend(st):
    """-> tokens charged since the loop began: every stage, retry, helper, review and judge run (an unmeasured run at
    its reservation), or None when there is no loop. A void run's charge counts nothing (loop_void_spend shows it)."""
    start = loop_start(st)
    if start is None:
        return None
    return sum(int(c.get("tokens") or 0) for c in _loop_charges(st) if (epoch(c.get("at")) or 0) >= start)


def loop_void_spend(st):
    """-> tokens of void charges since his word last lifted a park (all of them before any): true spend, shown apart."""
    since = epoch(st.get("loop_since")) or 0
    return sum(int(c.get("tokens") or 0) for c in _loop_charges(st, void=True) if (epoch(c.get("at")) or 0) >= since)


def loop_ceiling(st):
    """-> why the loop has reached LOOP_CEILING_FACTOR x the item's cap, or None."""
    spent = loop_spend(st)
    ceil = LOOP_CEILING_FACTOR * task_cap(st)
    if spent is None or spent < ceil:
        return None
    void = loop_void_spend(st)
    return "the judge-and-rework loop has spent %d tokens since %s, past its ceiling of %d (%dx the cap)%s" % (
        spent, datetime.datetime.fromtimestamp(loop_start(st), datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ceil, LOOP_CEILING_FACTOR, "; void spend %d shown apart, not counted" % void if void else "")


def refusals_since_loop(st):
    """not_covered judge rounds since the loop began (or since his word last lifted a park); a round judged on inputs
    that changed mid-judge (stale_inputs) is no refusal."""
    since = epoch(st.get("loop_since")) or 0
    return sum(1 for r in st.get("coverage_rounds") or [] if isinstance(r, dict)
               and r.get("verdict") == "not_covered" and not r.get("stale_inputs")   # coverage_judge.is_refusal
               and (epoch(r.get("at")) or 0) >= since)


# RIMMANDRAKE_UNPARK_DESIGNER_WHEN_IT_CAN_FIX_GAPS_ALONE (owner card 2026-11-15 on Graffiti, "Rework, and stop parking
# for these"): a refusal whose every gap the Designer can fix alone (return_to 3, no criterion called flawed) is rework,
# not a question for him, so the second one while he is away does not park, and a park written over such gaps before
# the rule no longer stands. The brake on runaway rounds stays: coverage_judge.stop_reason stops judging at its
# NOT_COVERED_LIMIT with the one fixed-id alarm (refusal_contract.ALARM_ID), and the loop still parks at its ceiling.
VERDICT = "coverage_verdict.json"   # coverage_judge.VERDICT_FILE


def designer_can_fix(rec):
    """-> True when a not_covered verdict's gaps are all the Designer's alone: at least one gap, each returning to
    stage 3 (a stage-2 gap needs his answer), and none whose criterion the judge calls flawed (the criteria fixer's)."""
    gaps = rec.get("gaps") if isinstance(rec, dict) else None
    return bool(isinstance(gaps, list) and gaps and rec.get("verdict") == "not_covered"
                and not rec.get("criteria_suspect")
                and all(isinstance(g, dict) and g.get("return_to") == 3 and not _criterion_suspect(g) for g in gaps))


def _criterion_suspect(g):
    """A gap whose criterion the judge calls flawed or unattainable: the neutral criteria fixer's, never the Designer's
    rework (RIMMANDRAKE_ROUTE_FLAWED_CRITERION_GAPS_OFF_DESIGNER_REWORK; park_summary routes it the same way)."""
    return g.get("criterion_verdict") in ("flawed", "unattainable")


def fixable_park(st, d):
    """A second_refusal park over a verdict the Designer can fix alone (it parked before the rule above)."""
    park = st.get("park")
    return (isinstance(park, dict) and park.get("kind") == "second_refusal"
            and designer_can_fix(read_json(os.path.join(d, VERDICT))))


def standing_park(st, d, repo=REPO, lines=None):
    """-> the park still waiting on him, or None: lifted by his own word (ownerSaid or byCard on an OWNER event
    naming the item) or the Conductor window's act under the five-acts ruling (owner 2026-11-19) after it was written,
    or, for a second refusal, by every gap being the Designer's alone (designer_can_fix). A seat's note, another
    --per-ruling act or a rework helper never lifts it. An unreadable OWNER shard
    keeps a park needing him standing."""
    park = st.get("park")
    if not isinstance(park, dict):
        return None
    if his_word_since_park(st, d, repo, lines) or fixable_park(st, d):
        return None
    return park


def his_word_since_park(st, d, repo=REPO, lines=None):
    park = st.get("park")
    if not isinstance(park, dict) or not st.get("item"):
        return False
    if lines is None:
        lines = CT.owner_lines(repo, clone_of(d))
    return bool(lines is not None and his_answers(lines, st["item"], epoch(park.get("at")) or 0))


def ceiling_crossed_at(st):
    """-> epoch of the charge that took the current loop's spend to its ceiling, or None (not reached, or no loop)."""
    start = loop_start(st)
    if start is None:
        return None
    ceil, tot = LOOP_CEILING_FACTOR * task_cap(st), 0
    for at, tokens in sorted((epoch(c.get("at")) or 0, int(c.get("tokens") or 0)) for c in _loop_charges(st)):
        if at >= start:
            tot += tokens
            if tot >= ceil:
                return at
    return None


def word_past_ceiling(st, d, repo=REPO):
    """The loop is past its ceiling with no park written yet, and his word on the item (ownerSaid or byCard) came
    after it crossed: the park would have been written at the crossing and lifted by that word, so it is lifted now
    (Pyrelands 2026-11-14: his card came before any open wrote the park, which then waited for another word). -> his
    latest tsn, or None."""
    if isinstance(st.get("park"), dict) or not st.get("item") or not loop_ceiling(st):
        return None
    at = ceiling_crossed_at(st)
    lines = CT.owner_lines(repo, clone_of(d)) if at is not None else None
    words = his_answers(lines, st["item"], at) if lines is not None else []
    return words[-1] if words else None


def lift_park(st, d, repo=REPO):
    """His word arrived: the park moves to `parks`, the loop restarts from now, the concept is ready. -> True when
    lifted (st changed; the caller writes it). A ceiling no park was written for yet lifts the same way when his word
    came after the loop crossed it (word_past_ceiling)."""
    tsn = word_past_ceiling(st, d, repo)
    if tsn:
        st["park"] = {"kind": "ceiling", "why": loop_ceiling(st), "by": "lift_park: OWNER:%s after the crossing" % tsn,
                      "at": datetime.datetime.fromtimestamp(ceiling_crossed_at(st), datetime.timezone.utc).strftime(
                          "%Y-%m-%dT%H:%M:%SZ")}
    if not isinstance(st.get("park"), dict) or standing_park(st, d, repo):
        return False
    his = his_word_since_park(st, d, repo)
    park = dict(st.pop("park"), lifted_at=now_iso())
    if his:
        st["loop_since"] = park["lifted_at"]
    else:   # no word of his: the loop, its brake count and its ceiling, run on
        park["lifted_by"] = "designer_can_fix"
    st.setdefault("parks", []).append(park)
    if st.get("status") == "waiting_owner":
        st["status"] = "ready"
    hist(st, "park_lifted", "his word on %s lifts the %s park" % (st.get("item"), park.get("kind")) if his else
         "every gap of the %s park is the Designer's to fix alone: rework, not his question" % park.get("kind"))
    return True


def _gap_lines(gaps, advisory=False):
    out = []
    for i, g in enumerate(gaps or []):
        if isinstance(g, dict):
            route = ("neutral criteria fixer" if g.get("criterion_verdict") in ("flawed", "unattainable") else
                     ("advisory: proposed stage %s" if advisory else "returns to stage %s") % g.get("return_to"))
            out.append("%d. %s (%s; ids %s; %s)" % (
                i + 1, " ".join(str(g.get("what") or "").split()), " ".join(str(g.get("where") or "").split()),
                ", ".join(g.get("ids") or []) or "none", route))
    return out


def park_summary(d, st, kind, why):
    """The one page he reads: what is settled, what is refused and why, the smallest fixes, what he must decide, and,
    when enough code exists, a loud offer of a quick look."""
    try:
        rec = read_json(os.path.join(d, "record.json")) or {}
    except Refused:
        rec = {}
    rec = rec if isinstance(rec, dict) else {}      # a malformed record is the run's to repair, never a crash here
    rec = dict(rec, **{k: [] for k in ("asks", "decisions", "inventory") if not isinstance(rec.get(k), list)})
    if not isinstance(rec.get("root"), dict):
        rec["root"] = {}
    verdict = read_json(os.path.join(d, "coverage_verdict.json")) or {}
    mod = st.get("mod") or os.path.basename(os.path.abspath(d))
    done = sorted({r.get("stage") for r in st.get("results") or [] if isinstance(r, dict) and r.get("outcome") == "done"})
    gaps = [g for g in verdict.get("gaps") or [] if isinstance(g, dict)] if verdict.get("verdict") == "not_covered" else []
    cov_line = CT.coverage_summary(d, clone_of(d) or REPO)
    owner_passed = cov_line.startswith("passed on the owner's word")
    advisory = bool(verdict.get("advisory") or (verdict.get("contract") or {}).get("advisory"))
    if owner_passed:
        gaps = []       # his certificate stands past them: they are not refusals, and the line below says so
    sent = [a for a in rec.get("asks") or [] if isinstance(a, dict) and a.get("status") == "sent"]
    rejected = [r for r in st.get("results") or [] if isinstance(r, dict) and r.get("outcome") == "rejected"
                and not r.get("void_system")]
    code = code_present(rec)
    L = ["# %s: parked for you (%s)" % (mod, kind), "",
         "%s. Nothing runs on it, no Designer run and no judge, until your word on %s. Item %s, stage %s (%s)." % (
             why, st.get("item"), st.get("item"), st.get("stage"), STAGE_NAMES.get(st.get("stage"), "?")), ""]
    if code:
        L += ["## QUICK LOOK OFFERED", "",
              "Enough code exists (%d built capabilities: %s). A short look in game could settle %s at once." % (
                  len(code), ", ".join(code), "the questions below"), ""]
        for a in sent:
            look = a.get("quick_look") if isinstance(a.get("quick_look"), dict) else {}
            if look.get("offer") and CT.txt(look.get("scene")):
                L += [" ".join(look["scene"].split()), ""]
    L += ["## Settled", "",
          "- Stages accepted: %s." % (", ".join("%s %s" % (s, STAGE_NAMES.get(s, "?")) for s in done) or "none"),
          "- Root: %s" % (" ".join(str((rec.get("root") or {}).get("text") or "not yet approved").split())),
          "- %d decisions on record, %d tree leaves, %d inventory capabilities." % (
              len(rec.get("decisions") or []), len((read_json(os.path.join(d, "tree.json")) or {}).get("leaves") or []),
              len(rec.get("inventory") or [])), ""]
    L += ["## Refused, and why", ""]
    if owner_passed:
        L += ["Coverage: %s." % cov_line]
    elif gaps:
        if advisory:
            L += ["Coverage findings from %s are advisory, not a binding refusal (%s). All findings are retained:" % (
                verdict.get("judge"), (verdict.get("contract") or {}).get("calibration") or
                verdict.get("advisory"))] + _gap_lines(gaps, advisory=True)
        else:
            L += ["The coverage judge (%s) says not covered: %s" % (verdict.get("judge"), " ".join(
                str(verdict.get("reasons") or "").split()))] + _gap_lines(gaps)
    elif rejected:
        L += ["The last rejected result (%s): %s" % (rejected[-1].get("run"), "; ".join(
            str(w) for w in rejected[-1].get("why") or []))]
    else:
        L += ["Nothing refused; this step ends in your certification."]
    L += ["", "## Smallest fixes", ""]
    suspect = [g for g in gaps if g.get("criterion_verdict") in ("flawed", "unattainable")]
    fix = [g for g in gaps if g.get("return_to") == 3 and g not in suspect]
    if fix:
        ids = ", ".join(str(i + 1) for i, g in enumerate(gaps) if g in fix)
        L += (["- The Designer can review %d advisory Stage 3 correction candidates without an owner choice: %s." % (
            len(fix), ids)] if advisory else ["- The Designer can fix %d gap(s) at stage 3 without you: %s." % (
                len(fix), ids)])
    else:
        L += ["- No Stage 3 corrections listed."]
    if suspect:
        L += ["- Flawed or unattainable criteria go to the neutral criteria fixer, not an owner question: %s." %
              ", ".join(str(i + 1) for i, g in enumerate(gaps) if g in suspect)]
    L += ["", "## What you must decide", ""]
    for i, g in enumerate(gaps):
        if not advisory and g not in suspect and g.get("return_to") == 2:
            L.append("- Gap %d needs your answer: %s" % (i + 1, " ".join(str(g.get("what") or "").split())))
    for a in sent:
        L.append("- Ask %s: %s" % (a.get("id"), " ".join(str(a.get("text") or "").split())))
    if sent:
        L += ["- Reply on %s to the question above; no answer or certification is inferred." % st.get("item"), ""]
    else:
        L += ["- Then one note on %s (your words, or a card): rework it, certify it as it stands, waive a gap, or stop." %
              st.get("item"), ""]
    return "\n".join(L)


def lock_summary(d, st, run):
    """The page that replaces a park page when the concept locks: locked, by which run, and how coverage passed."""
    mod = st.get("mod") or os.path.basename(os.path.abspath(d))
    done = sorted({r.get("stage") for r in st.get("results") or [] if isinstance(r, dict) and r.get("outcome") == "done"})
    return "\n".join([
        "# %s: locked (stage 5)" % mod, "",
        "Locked %s by run %s. Item %s. Stages accepted: %s." % (
            now_iso(), run, st.get("item"), ", ".join("%s %s" % (s, STAGE_NAMES.get(s, "?")) for s in done)), "",
        "Coverage: %s." % CT.coverage_summary(d, clone_of(d) or REPO), "",
        "Earlier parks on this concept: %d (stage.json `parks`)." % len(st.get("parks") or []), ""])


def park(d, kind, why, repo=REPO, st=None):
    """Park the concept for him (see the block comment). -> the state (written when st was not given)."""
    if kind not in PARK_KINDS:
        raise Refused("park kind %r is not one of %s" % (kind, "/".join(PARK_KINDS)))
    own = st is None
    st = load_state(d) if own else st
    path = os.path.join(d, PARK_FILE)
    rec = read_json(os.path.join(d, "record.json")) or {}
    with open(path, "w", encoding="utf-8") as f:
        f.write(park_summary(d, st, kind, why))
    st["park"] = {"at": now_iso(), "kind": kind, "why": why, "summary": PARK_FILE,
                  "quick_look": bool(code_present(rec))}
    st["status"], st["waiting_owner_feed"] = "waiting_owner", owner_feed(repo, st.get("item"), d)
    hist(st, "park", "%s: %s (%s)" % (kind, why, PARK_FILE))
    if own:
        write_json(state_path(d), st)
    return st


def program_result(st, verdict, run):
    """Pure. The result.json a stage-5 Designer run would write when the coverage verdict leaves nothing to decide, or
    None (a Designer run is needed, as today). RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS: ten Designer runs,
    USD 8.39, wrote down only what the verdict said (cheap-guards spec 3.3). not_covered with every gap returning to
    stage 3 -> return to 3; covered and signed -> done. A gap returning elsewhere (his answer), an unsigned, malformed,
    advisory or missing verdict, or a verdict on another tree than st["tree_now"] -> None."""
    if not isinstance(st, dict) or st.get("stage") != 5 or st.get("status") == "locked":
        return None
    if not isinstance(verdict, dict) or verdict.get("advisory") or verdict.get("error"):
        return None
    if isinstance(verdict.get("contract"), dict) and verdict["contract"].get("advisory"):
        return None     # advisory where park_summary and coverage_judge also read it
    if verdict.get("criteria_suspect"):     # as designer_can_fix (RIMMANDRAKE_HONOUR_CRITERIA_SUSPECT_IN_PROGRAM_RESULT_TOO)
        return None
    if verdict.get("tree") and st.get("tree_now") and verdict["tree"] != st["tree_now"]:
        return None
    judge = verdict.get("judge") or "the coverage judge"
    gaps = verdict.get("gaps")
    if verdict.get("verdict") == "covered":
        if verdict.get("signed") is not True or gaps:
            return None
        return {"run": run, "stage": 5, "outcome": "done", "by": "program",
                "summary": "locked by program: %s returned covered and signed the tree" % judge}
    if verdict.get("verdict") != "not_covered" or not isinstance(gaps, list) or not gaps:
        return None
    if not all(isinstance(g, dict) and g.get("return_to") in (3, "3") and CT.txt(g.get("gid") or g.get("id"))
               and CT.txt(g.get("what")) and not _criterion_suspect(g) for g in gaps):
        return None
    return {"run": run, "stage": 5, "outcome": "return", "to": 3, "by": "program",
            "decision": "%s returned not_covered; every gap returns to stage 3: %s" % (judge, "; ".join(
                "%s: %s" % (g.get("gid") or g.get("id"), " ".join(str(g["what"]).split())) for g in gaps))}


def close_run(d, run, tokens=None, repo=REPO, runner="claude", usage=None, transport_error=None):
    """The launcher, after the run ends: charge it (UNMEASURED = its whole reservation), then validate result.json
    and advance only on a valid result. -> (accepted?, reasons)."""
    st = load_state(d)
    r = st.get("running")
    if not r or r.get("run") != run:
        raise Refused("run %s is not the open run (%s)" % (run, (r or {}).get("run")))
    st["runner"] = runner
    if runner == "codex":
        st.setdefault("runner_spend", []).append({"runner": "codex", "run": run,
                                                 "usage": usage if usage is not None else "UNMEASURED"})
    elif runner == "claude":
        charge_state(st, tokens if tokens is not None else r.get("reserved", 0),
                     "stage" if tokens is not None else "unmeasured", "run %s" % run)
    else:
        raise Refused("runner must be claude or codex")
    try:
        res = read_json(os.path.join(d, "result.json"))
    except Refused as e:    # an unparseable result.json is a rejected result, charged, never a run left open
        res, unparsed = None, str(e)
    else:
        unparsed = None
        if not isinstance(res, dict) and os.path.exists(os.path.join(d, "result.json")):
            # written but not a result: refused on its merits, never NO_RESULT (that names an absent file, which
            # role_launch.void_cause may class void_system)
            unparsed = "result.json holds %s, not a JSON object: a written result that is no result" % (
                "null" if res is None else type(res).__name__)
    try:
        errs = [unparsed] if unparsed else result_errors(res, d, st, repo)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError) as e:
        # a result.json shape no rule above names (RIMMANDRAKE_REFUSE_MALFORMED_IDS_CLOSE_RUN_CRASHES_INSTEAD): a crash
        # here left `running` set, so the next open charged the reservation as a retry; it is a rejection instead
        errs = ["result.json has a shape the validator cannot read (%s: %s)" % (type(e).__name__, _clip_repr(str(e), 160))]
    if transport_error:
        errs.append("Codex transport failed: %s" % str(transport_error))
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
        st["results"].append(dict({"stage": st["stage"], "outcome": "rejected", "run": run, "at": now_iso(),
                                   "why": errs[:20]}, **({"parent": r["parent"]} if r.get("parent") else {})))
        hist(st, "retry", "run %s result rejected: %s" % (run, "; ".join(errs[:3])))
        if os.path.exists(os.path.join(d, "result.json")):
            os.replace(os.path.join(d, "result.json"), os.path.join(d, "result.%s.rejected.json" % safe(run)))
        write_json(state_path(d), st)
        return False, errs
    out, stage = res["outcome"], st["stage"]
    entry = {"stage": stage, "outcome": out, "run": run, "at": now_iso(), "inputs": inputs(d, st, repo),
             "owner_uncited": owner_uncited(repo, st.get("item"), d), "manifest": r["manifest"]}
    if r.get("parent"):
        entry["parent"] = r["parent"]
    # RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED: an accepted stage is a pin, so it records its anchor
    # too. These bytes land in a commit at or after this HEAD (land_state commits after this), so the window
    # [HEAD, HEAD-then] starts at the landing of exactly these bytes instead of at a later revert to them.
    # read in the concept's own clone, where these bytes land (land_state) and repin traces them
    # (RIMMANDRAKE_ANCHOR_PIN_IN_CONCEPT_CLONE_NOT_DISPATCHER), not in the Dispatcher's clone that judges the close
    # A HEAD that cannot be read is recorded as PIN_UNREAD, never left out: a pin with no anchor is a legacy pin to
    # input_changes (the last occurrence), and this one is new (RIMMANDRAKE_HARDEN_PIN_ANCHOR_THREE_EDGES_CODEX_FOUND)
    pin_at = (_git(clone_of(d) or repo, "rev-parse", "--verify", "HEAD^{commit}") or b"").decode().strip()
    if out == "done":
        entry["pinned_at"] = {k: pin_at or PIN_UNREAD for k in INPUT_FILES}
    if out == "done" and stage == 2:
        st.pop("must_cite", None)
    for k in ("to", "decision", "on", "question", "summary", "quick_look", "by"):
        if k in res:
            entry[k] = res[k]
    st["results"].append(entry)
    if out == "done":
        # a return's decision is the work of the stage it went back to: once that stage is done it is settled, and a later
        # reopen must not re-send it as missing (RIMMANDRAKE_CLEAR_SETTLED_RETURN_DECISION_RESENT_TWO_DAYS_LATE)
        st.pop("pending_decision", None)
        if stage == 5:
            st["status"] = "locked"
            if os.path.exists(os.path.join(d, PARK_FILE)):
                # the page he reads must not still say "parked for you" over a locked concept
                with open(os.path.join(d, PARK_FILE), "w", encoding="utf-8") as f:
                    f.write(lock_summary(d, st, run))
        else:
            st["stage"] = stage + 1
            lift_block(st)      # a ready concept has no block: an older writer's leftover reason goes too
    elif out == "waiting_owner":
        st["status"], st["waiting_owner_feed"] = "waiting_owner", owner_feed(repo, st.get("item"), d)
    elif out == "return":
        st["stage"] = res["to"]
        lift_block(st)
        st["pending_decision"] = res["decision"]
    elif out == "blocked":
        st["status"], st["blocked_on"] = "blocked", res["on"]
    hist(st, "close", "run %s: stage %d %s" % (run, stage, out))
    if out == "done" and stage == 4:
        # the read map of the exam just accepted, recorded while the tree is the one it examined, so a retake after a
        # coverage repair re-runs only the scenarios the repair touched (exam_retake.py); no map means a whole retake
        rm = ER.record(d, repo=repo)
        hist(st, "exam_map", "read map recorded for %d scenarios" % len(rm["scenarios"]) if "error" not in rm
             else "no read map (a later retake is whole): %s" % rm["error"])
    if out == "waiting_owner" or (out == "return" and res.get("question")):
        away, why_away = owner_away()   # a step that ends in his certification, while he is away, parks
        if away:
            park(d, "certification", "stage %d ends in your answer (%s) while you are away: %s" % (
                stage, "%d ask(s) sent" % len([a for a in (read_json(os.path.join(d, "record.json")) or {}).get(
                    "asks") or [] if isinstance(a, dict) and a.get("status") == "sent"]) if out == "waiting_owner"
                else "question: %s" % res.get("question"), why_away), repo, st)
    os.replace(os.path.join(d, "result.json"), os.path.join(d, "result.%s.json" % safe(run)))
    write_json(state_path(d), st)
    return True, []


LAND = os.path.join(os.path.dirname(HERE), "Utils", "land.sh")


def state_paths(d, repo):
    """The harvest's own files in a concept folder, relative to its clone: stage.json, park_summary.md (park and lock
    write it), every result*.json there, and
    result.json when origin/main still has it after close renamed it away (a deletion lands too)."""
    rel = os.path.relpath(os.path.abspath(d), repo)
    out = [os.path.join(rel, "stage.json")] if os.path.isfile(os.path.join(d, "stage.json")) else []
    out += [os.path.join(rel, PARK_FILE)] if os.path.isfile(os.path.join(d, PARK_FILE)) else []
    out += sorted(os.path.join(rel, n) for n in os.listdir(d) if re.match(r"result(\..+)?\.json$", n))
    gone = os.path.join(rel, "result.json")
    import subprocess
    if gone not in out:
        r = subprocess.run(["git", "-C", repo, "ls-tree", "--name-only", "origin/main", "--", gone],
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            out.append(gone)
    # RIMMANDRAKE_LAND_DESIGNER_WORK_HARVEST_STRANDED_TWICE: the run's own work in the folder (record, tree, sheet,
    # scenes, exam.json, exam_control/, exam_evidence/ ...) lands too, but only files this clone changed (modified or
    # untracked, on disk): a file it left alone is never reverted over a peer's newer copy on origin/main
    r = subprocess.run(["git", "-C", repo, "status", "--porcelain", "-z", "--untracked-files=all", "--", rel],
                       capture_output=True, text=True, timeout=120)
    fields = r.stdout.split("\0") if r.returncode == 0 else []
    i = 0
    while i < len(fields):
        e, i = fields[i], i + 1
        if len(e) < 4:
            continue
        if e[0] in "RC" or e[1] in "RC":
            i += 1                         # -z: a rename or copy is "XY dest\0source"; the source field is skipped
        p = e[3:]
        if p not in out and os.path.isfile(os.path.join(repo, p)):
            out.append(p)
    return out


def land_state(d, run, timeout=21600):  # budget: class=publish
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
           "Landed by designer_stage.land_state (DESIGNER_STAGE_FIX_COMMIT_ITS_OWN_STATE): stage.json, park_summary.md, result files "
           "and the concept-folder files this clone changed."
           % (mod, last.get("stage", st.get("stage")), last.get("outcome", st.get("status")), run))
    p = subprocess.run([LAND, "-m", msg] + paths, cwd=repo, capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, LAND_REPO=repo))
    if p.returncode == 0:
        return p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "PUBLISHED ?"
    if "nothing to land" in p.stderr:
        return "nothing to land"
    raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()))


def safe(run):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(run))


def lift_block(st):
    """A block lifts with its reason (RIMMANDRAKE_CLEAR_STALE_BLOCK_REASON_ON_LIFT): a 'ready' concept still holding
    blocked_on showed a stop that had been released as the Designer's why. The reason stays in history. -> the reason."""
    st["status"] = "ready"
    return st.pop("blocked_on", None)


_BLOCK_ITEM = re.compile(r"^\s*([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\s*(?::|$)")


def closed_blocker(st, closed):
    """-> (item, its state) when the concept is blocked on a ledger item that is closed, else None
    (RIMMANDRAKE_UNBLOCK_CONCEPTS_WHOSE_BLOCKER_CLOSED_DAYS_AGO: FlowWorks and PyrelandsMechanics sat blocked a week on
    items closed on the ledger, because nothing re-read a block when its item closed). The item is the block reason's
    leading id (`ITEM: why`, as a Designer result's `on` names it). None, and the block stands, when the ledger was not
    read (closed is None), when the reason names an owner hold (his word lifts it), the coverage stop (the alarm id
    refusal_contract.ALARM_ID, or a standing coverage_stop: `coverage_judge.py release` lifts it) or a cleanse block."""
    if not isinstance(st, dict) or st.get("status") != "blocked" or not isinstance(closed, dict):
        return None
    on = str(st.get("blocked_on") or "")
    m = _BLOCK_ITEM.match(on)
    if not m or "OWNER HOLD" in on or st.get("coverage_stop") or st.get("cleanse"):
        return None
    import refusal_contract as RC
    item = m.group(1)
    if item == RC.ALARM_ID or item not in closed:
        return None
    return item, closed[item]


def lift_closed_block(st, repo=REPO, closed=None):
    """In memory: lift a block whose item closed (closed_blocker), its history naming the item and its state, so the
    gate is read again (it refuses with its own words if something is still owed). -> the item, or None."""
    cb = closed_blocker(st, closed_items(repo) if closed is None else closed)
    if not cb:
        return None
    on = lift_block(st)
    hist(st, "unblock", "its block's item %s is %s on the ledger: the block lifts and the gate is read again (was "
                        "blocked on %s)" % (cb[0], cb[1], on))
    return cb[0]


def unblock_closed(root, repo=REPO, apply=False):
    """-> [(concept dir, item)] of every concept under root blocked on a closed item; apply writes each lift. Raises
    Refused when the ledger cannot be read (could not look: nothing is lifted)."""
    closed = closed_items(repo)
    if closed is None:
        raise Refused("UNMEASURED: the ledger could not be read; no block is lifted")
    out = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isfile(state_path(d)):
            continue
        st = load_state(d)
        item = lift_closed_block(st, repo, closed)
        if item:
            out.append((d, item))
            if apply:
                write_json(state_path(d), st)
    return out


def unblock(d, why):
    """Lift a block; on a concept already lifted by an older writer that left its reason, take the stale reason off."""
    st = load_state(d)
    if st.get("status") != "blocked":
        if st.get("status") == "ready" and st.get("blocked_on"):
            hist(st, "unblock", "%s (stale reason taken off a ready concept: %s)" % (why, st.pop("blocked_on")))
            write_json(state_path(d), st)
            return
        raise Refused("not blocked")
    on = lift_block(st)
    hist(st, "unblock", "%s (was blocked on %s)" % (why, on) if on else why)
    write_json(state_path(d), st)


# ---------------------------------------------------------------- a locked version changed by his card

VERSION_FILE = os.path.join("version", "VERSION.json")
_HEX = re.compile(r"\b[0-9a-f]{7,40}\b")
_REPIN_SOURCE = re.compile(r"^OWNER:([0-9]+)(?:@([0-9A-Za-z^~._/-]+))?$")
_TEXT_SOURCE = re.compile(r"^TEXT@([0-9A-Za-z^~._/-]+)$")
# RIMMANDRAKE_REPAIR_FLOWWORKS_REPIN_REFUSAL_AND_ESCAPE_WARNING: the fields of a scene that are its test text. A commit
# that changes only these, in scenes.json only, changes no bar (the bars are tree.json's leaves and sheet.md), so it
# needs no card of his: a re-pin cites it as TEXT@<sha>, a note, never a refusal (CLAUDE.md §A fault of form).
SCENE_TEXT_KEYS = ("start", "action", "expect", "control", "restore")


def _git(repo, *a):
    import subprocess
    r = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def ledger_events(repo):
    """Every parsed event of every ledger shard in the clone's working tree (a bad line spoils itself only)."""
    out = []
    evd = os.path.join(repo, os.path.dirname(CT.OWNER_SHARD))
    for name in sorted(os.listdir(evd)) if os.path.isdir(evd) else []:
        if not name.endswith(".jsonl"):
            continue
        with open(os.path.join(evd, name), encoding="utf-8", errors="replace") as f:
            for ln in f:
                try:
                    ev = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(ev, dict):
                    out.append(ev)
    return out


def test_text_only(d, commit, repo):
    """-> (True, "") when `commit` (a full sha) changed, of this concept's frozen input files, scenes.json alone, and in
    it only the test text of scenes and showcases (SCENE_TEXT_KEYS): the same scene ids, and every other field of each
    (its requirement, kind, hold, members) and every other top-level key equal. -> (False, why) otherwise, or when the
    commit or either side of the file cannot be read (UNMEASURED is never test text)."""
    rel = os.path.relpath(d, repo).replace(os.sep, "/")
    rc, out = _git_rc(repo, "diff", "--name-only", "%s^" % commit, commit, "--",
                      *["%s/%s" % (rel, fn) for fn in INPUT_FILES.values()])
    if rc != 0:
        return False, "UNMEASURED: the files %s changed cannot be read (no parent, or git failed)" % commit[:10]
    names = sorted(set(out.decode("utf-8", "replace").split()))
    if names != ["%s/scenes.json" % rel]:
        return False, "it changed %s, not scenes.json alone" % (", ".join(n.rsplit("/", 1)[-1] for n in names) or
                                                                 "no frozen input")
    sides = []
    for c in ("%s^" % commit, commit):
        blob, err = _blob_at(repo, c, "%s/scenes.json" % rel)
        try:
            sides.append(json.loads(blob.decode("utf-8")) if blob is not None else None)
        except ValueError:
            sides.append(None)
        if err or not isinstance(sides[-1], dict):
            return False, "UNMEASURED: scenes.json at %s cannot be read as an object" % c[:11]
    a, b = sides

    def rows(x, k):
        v = x.get(k) or []
        if not isinstance(v, list) or not all(isinstance(r, dict) and r.get("id") for r in v):
            return None
        return {r["id"]: {f: r[f] for f in r if f not in SCENE_TEXT_KEYS} for r in v}
    if {k: v for k, v in a.items() if k not in ("scenes", "showcases")} != \
            {k: v for k, v in b.items() if k not in ("scenes", "showcases")}:
        return False, "it changed a top-level key of scenes.json other than scenes and showcases"
    for k in ("scenes", "showcases"):
        ra, rb = rows(a, k), rows(b, k)
        if ra is None or rb is None:
            return False, "UNMEASURED: scenes.json %s is not a list of scenes with ids" % k
        if set(ra) != set(rb):
            return False, "it added or dropped %s: %s" % (k, ", ".join(sorted(set(ra) ^ set(rb))))
        moved = sorted(i for i in ra if ra[i] != rb[i])
        if moved:
            return False, "it changed a field outside the test text (%s) of %s" % ("/".join(SCENE_TEXT_KEYS),
                                                                                  ", ".join(moved))
    return True, ""


def change_tied(ev, commit, repo, events):
    """His card `ev` made the change `commit` (a full sha) when the commit cites the event (OWNER:<tsn> or its item id
    in the message), or a ledger event on the card's item names the commit (its sha field, or a 7+ hex prefix in its
    text): the close or note the change was landed under."""
    msg = (_git(repo, "log", "-1", "--format=%B", commit) or b"").decode("utf-8", "replace")
    if re.search(r"OWNER:%s(?![0-9])" % re.escape(str(ev.get("tsn"))), msg) or (ev.get("id") and ev["id"] in msg):
        return True
    for e in events:
        if e.get("id") != ev.get("id"):
            continue
        if CT.txt(e.get("sha")) and len(e["sha"]) >= 7 and commit.startswith(e["sha"]):
            return True
        for h in _HEX.findall(" ".join(str(e.get(k) or "") for k in ("text", "reason", "why"))):
            if commit.startswith(h):
                return True
    return False


PIN_UNREAD = "unread-at-pin:?"     # a pin whose recording commit could not be read (never a git revision: `?` and `:`)


def _git_rc(repo, *a):
    """-> (exit code, stdout) of one git call; (None, b"") when it could not be run or ran past its time."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", repo] + list(a), capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None, b""
    return r.returncode, r.stdout


def _blob_at(repo, commit, rel):
    """-> (bytes, None) the file at a commit; (None, None) when the commit has no such file (asked of its tree, a
    reading); (None, why) when that could not be read. A failed read is never the file's absence."""
    rc, out = _git_rc(repo, "ls-tree", "-z", commit, "--", rel)
    if rc != 0:
        return None, "git ls-tree %s -- %s failed" % (commit[:10], rel)
    if not out.strip(b"\0"):
        return None, None
    blob = _git(repo, "show", "%s:%s" % (commit, rel))
    if blob is None:
        return None, "git show %s:%s failed" % (commit[:10], rel)
    return blob, None


def _window_cut(repo, full):
    """Why the history window [full, HEAD] cannot be read whole, or None. The anchor must be an ancestor of HEAD, and in
    a shallow clone no commit of the window may be a shallow boundary (its parents are missing, so `git log` stops there
    and a change behind it is not listed)."""
    rc, _ = _git_rc(repo, "merge-base", "--is-ancestor", full, "HEAD")
    if rc != 0:
        return ("is not an ancestor of HEAD here" if rc == 1 else "could not be compared with HEAD") + \
            " (a shallow or rewritten history)"
    rc, out = _git_rc(repo, "rev-parse", "--is-shallow-repository")
    if rc != 0:
        return "whether this clone is shallow could not be read"
    if out.strip() != b"true":
        return None
    rc, path = _git_rc(repo, "rev-parse", "--git-path", "shallow")
    rc2, win = _git_rc(repo, "rev-list", "%s..HEAD" % full)
    if rc != 0 or rc2 != 0:
        return "this clone is shallow and its boundary could not be read"
    try:
        p = path.decode().strip()
        with open(p if os.path.isabs(p) else os.path.join(repo, p), encoding="utf-8") as f:
            cut = set(f.read().split())
    except (OSError, ValueError) as e:
        return "this clone is shallow and its boundary file could not be read (%s)" % e.__class__.__name__
    hit = cut & set(win.decode().split())
    return "this clone is shallow and its history is cut at %s, inside the window" % sorted(hit)[0][:10] if hit else None


def input_changes(d, key, repo, pinned, anchor=None):
    """-> (commits, why): the commits (oldest first) that moved file input `key` from its pinned hash to the committed
    one, or (None, why) when that cannot be traced.

    RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED: `anchor` is the commit that RECORDED the pin, written at
    pin time (a result's `pinned_at[key]`), never read from a commit date. With it, the history read is the window
    [anchor, HEAD], so an input that went A->B->A->C after the pin owes a source for the B change too. Without it (a
    pin made before the field existed) the last occurrence of the pinned hash is still the start, as before, until that
    stage's next pin records an anchor.
    The pin's own occurrence in the window is the anchor commit itself (a re-pin records HEAD with the bytes committed),
    or the first commit after it that changes the input (an accepted stage records HEAD at close and its bytes land in
    the next commit, land_state). Every other case is UNMEASURED, (None, why), never a list, which would read as "this
    is all that changed since the pin" and let a re-pin pass unexamined
    (RIMMANDRAKE_HARDEN_PIN_ANCHOR_THREE_EDGES_CODEX_FOUND): the recorded anchor is PIN_UNREAD or does not resolve; it
    is not an ancestor of HEAD, or a shallow clone cuts the window; another change landed between the anchor and the
    pinned bytes; the pinned hash is in no commit of the window; a commit's file could not be read (which is not the
    file's absence in that commit)."""
    rel = os.path.relpath(os.path.join(d, INPUT_FILES[key]), repo).replace(os.sep, "/")
    first = False
    if anchor:
        if anchor == PIN_UNREAD:
            return None, ("UNMEASURED: the commit that recorded the pinned %s could not be read when the pin was made, "
                          "so the change since the pin cannot be read, and that is not 'no change'" % key)
        full = (_git(repo, "rev-parse", "--verify", "%s^{commit}" % anchor) or b"").decode().strip()
        if not full:
            return None, ("UNMEASURED: the commit that recorded the pinned %s (%s) does not resolve in this clone "
                          "(rewritten history, or a shallow clone): the change since the pin cannot be read, and that "
                          "is not 'no change'" % (key, str(anchor)[:10]))
        cut = _window_cut(repo, full)
        if cut:
            return None, ("UNMEASURED: the commit that recorded the pinned %s (%s) %s: the history since the pin "
                          "cannot be read whole, and a partial list is not the change" % (key, full[:10], cut))
        log = _git(repo, "log", "--reverse", "--format=%H", "%s..HEAD" % full, "--", rel)
        if log is None:
            return None, "UNMEASURED: git log of %s from the recorded pin %s failed" % (rel, full[:10])
        order, first = [full] + log.decode().split(), True
    else:
        log = _git(repo, "log", "--reverse", "--format=%H", "--", rel)
        if log is None:
            return None, "git log of %s failed" % rel
        order = log.decode().split()
    import tempfile
    seen = []                       # (commit, hash after it)
    with tempfile.TemporaryDirectory(prefix="repin-", dir=os.path.dirname(os.path.abspath(state_path(d)))) as t:
        for c in order:
            blob, err = _blob_at(repo, c, rel)
            if err:
                return None, "UNMEASURED: %s: %s at that commit cannot be read, which is not its absence" % (err, key)
            p = os.path.join(t, INPUT_FILES[key])
            if blob is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(blob)
            seen.append((c, input_hash(t, key)))
    at = [i for i, (_, h) in enumerate(seen) if h == pinned]
    if not at:
        if first:
            return None, ("UNMEASURED: the pinned %s (%s) is in no commit of %s at or after the commit that recorded "
                          "the pin (%s): the change since the pin cannot be read, and that is not 'no change'" % (
                              key, str(pinned)[:10], rel, seen[0][0][:10] if seen else "?"))
        return None, "the pinned %s (%s) is in no commit of %s: the change cannot be traced" % (
            key, str(pinned)[:10], rel)
    start = at[0] if first else at[-1]
    if first and any(h != seen[0][1] for _, h in seen[:start]):
        moved = next(c for c, h in seen[:start] if h != seen[0][1])
        return None, ("UNMEASURED: %s changed %s after the commit that recorded the pin (%s) and before the pinned "
                      "bytes (%s) landed in %s: which change the pin followed cannot be read, and leaving that commit "
                      "out is not 'no change'" % (moved[:10], key, seen[0][0][:10], str(pinned)[:10], seen[start][0][:10]))
    return [c for i, (c, h) in enumerate(seen) if i > start and h != seen[i - 1][1]], ""


REPIN_CLAUSE = "locked_change_cites_his_cards"
REPIN_WOULD_PASS = ("every commit since an accepted stage's pin that moved one of its frozen inputs is tied to the card "
                    "of his it carries out (designer_stage.change_tied: its message cites OWNER:<tsn> of his byCard or "
                    "ownerSaid event, or names that card's item, or a ledger event on the card's item names its sha), "
                    "no change is uncommitted, and his new words on the item are taken in")


def _commit_time(repo, commit):
    out = (_git(repo, "log", "-1", "--format=%ct", commit) or b"").decode().strip()
    return int(out) if out.isdigit() else None


def _his_word(ev):
    return isinstance(ev, dict) and bool(CT.txt(ev.get("ownerSaid")) or CT.txt(ev.get("byCard")))


def commit_cards(commit, repo, owner_ev, events):
    """-> the tsns of his cards (byCard or ownerSaid events) a commit carries out, by the first tie that finds any, in the
    order of change_tied: its message cites OWNER:<tsn>; its message names a card's item; a ledger event on a card's item
    names the commit. A card given after the commit was made is not what the commit carried out and is never cited,
    with one exception (RIMMANDRAKE_CITE_LATE_APPROVAL_CARD_NOTE_FIX_NEVER_PASSED): his card approving a fix that had
    already landed is cited by the last tie only, when a ledger event on its item names the commit and was written
    AFTER the card (the record that this card approves it), and no card given before the commit ties. A note older
    than the card cannot record it, so a later card never borrows an earlier note.
    Every tsn returned passes change_tied, so repin accepts exactly what a hand re-pin citing it would."""
    msg = (_git(repo, "log", "-1", "--format=%B", commit) or b"").decode("utf-8", "replace")
    made = _commit_time(repo, commit)

    def tsn_of(t, ev):
        v = str(ev.get("tsn") or t)
        return int(v) if v.isdigit() else None
    words = {t: ev for t, ev in owner_ev.items() if _his_word(ev)}
    cards = {t: ev for t, ev in words.items() if made is None or tsn_of(t, ev) is None or tsn_of(t, ev) // 10 ** 9 <= made}
    named = {}                      # item id -> the tsns (ints, or None unreadable) of the events on it naming the commit
    for e in events:
        if not e.get("id"):
            continue
        hexes = _HEX.findall(" ".join(str(e.get(k) or "") for k in ("text", "reason", "why")))
        if (CT.txt(e.get("sha")) and len(e["sha"]) >= 7 and commit.startswith(e["sha"])) or \
                any(commit.startswith(h) for h in hexes):
            v = str(e.get("tsn") or "")
            named.setdefault(e["id"], []).append(int(v) if v.isdigit() else None)
    late = [t for t, ev in words.items() if t not in cards and ev.get("id") in named and tsn_of(t, ev) is not None
            and any(n is not None and n > tsn_of(t, ev) for n in named[ev["id"]])]
    tiers = ([t for t in re.findall(r"OWNER:([0-9]+)(?![0-9])", msg) if t in cards],
             [t for t, ev in cards.items() if ev.get("id") and ev["id"] in msg],
             [t for t, ev in cards.items() if ev.get("id") in named],
             late)
    for tier in tiers:
        tied = sorted(dict.fromkeys(t for t in tier if change_tied(words[t], commit, repo, events)))
        if tied:
            return tied
    return []


def repin_sources(d, repo=None):
    """RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE -> (sources, refusal): the sources a re-pin of this LOCKED concept cites,
    found the way a hand re-pin finds them (each commit since a stale stage's pin that moved one of its frozen inputs,
    and the cards of his each one carries out: commit_cards), and None; or the sources found so far and a refusal
    record (clause, evidence, observed, would_pass, smallest_fix) when a re-pin citing only his cards cannot pass. His
    new words on the item are never cited for him: whether they are taken in is a reader's call, so they refuse.
    The dry repin (repin(..., dry=True)) is the last word: whatever it refuses, this refuses. Writes nothing."""
    repo = repo or clone_of(d) or REPO
    rel = os.path.relpath(d, repo).replace(os.sep, "/")

    def refusal(evidence, observed, fix, cost="edit"):
        return {"clause": REPIN_CLAUSE, "evidence": evidence, "observed": observed, "would_pass": REPIN_WOULD_PASS,
                "smallest_fix": {"what": fix, "attainable": "yes", "cost": cost}}
    st = load_state(d)
    ver = read_json(os.path.join(d, VERSION_FILE)) or {}
    if ver.get("state") != "locked":
        return [], refusal(["%s/%s state %r" % (rel, VERSION_FILE, ver.get("state"))],
                           "the version is not locked: an unlocked concept's changed inputs reopen its stages, and "
                           "no re-pin is owed", "none here: nothing waits on a re-pin of an unlocked concept")
    owner_ev = CT.owner_events(repo, clone_of(d))
    events = ledger_events(repo)
    cur = inputs(d, st, repo)
    frozen_now = owner_uncited(repo, st.get("item"), d)
    commits, words, bad = [], [], []
    for r in sorted(accepted(st), key=lambda r: r["stage"]):
        for k in DEPS[r["stage"]]:
            if r["inputs"].get(k) == cur.get(k):
                continue
            if k == "owner":
                new = sorted(set(frozen_now or []) - set(r.get("owner_uncited") or []))
                if frozen_now is None:
                    bad.append("stage %d: the OWNER shard is unreadable" % r["stage"])
                words += [t for t in new if t not in words]
                continue
            got, err = input_changes(d, k, repo, r["inputs"].get(k), (r.get("pinned_at") or {}).get(k))
            if got is None:
                bad.append("stage %d: %s" % (r["stage"], err))
                continue
            commits += [c for c in got if c not in commits]
    if bad:
        return [], refusal(bad, "the changes since the pin cannot be traced", "repair what each line names, then the "
                           "next tick tries again", "rerun")
    sources, uncited = [], []
    for c in commits:
        tsns = commit_cards(c, repo, owner_ev, events)
        if not tsns:
            text, not_text = test_text_only(d, c, repo)
            if text:                # no bar changed: cited as a note of its own, needing no card of his
                sources.append("TEXT@%s" % c)
                continue
            subj = (_git(repo, "log", "-1", "--format=%s", c) or b"").decode("utf-8", "replace").strip()
            conductor = re.findall(r"CONDUCTOR:[0-9]+", (_git(repo, "log", "-1", "--format=%B", c) or b"").decode(
                "utf-8", "replace"))
            uncited.append("%s %s: %s" % (c, subj, "%s; and not test text only: %s" % (
                                              "cites %s, a delegated call, never his word" % ", ".join(conductor)
                                              if conductor else "cites no card of his, and no ledger event on a card's "
                                              "item names it", not_text)))
        sources += ["OWNER:%s@%s" % (t, c) for t in tsns]
    if uncited:
        return sources, refusal(uncited, "%d of %d commits that moved a frozen input carry out no card of his that a "
                                "re-pin can cite" % (len(uncited), len(commits)),
                                "for each commit named, a ledger event on the item of the card of his it carries out "
                                "naming its sha (`rimflow note <card item> --text \"carried out by <sha>\"`), or a hand "
                                "`designer_stage.py repin %s --source OWNER:<tsn>@<sha> ...`; never a CONDUCTOR "
                                "source" % rel)
    if words:
        return sources, refusal(["OWNER:%s (on %s, not cited by record.json or tree.json)" % (t, st.get("item"))
                                 for t in words],
                                "his new words on the item since the pin are not taken in; the pipeline never cites "
                                "them for him", "the Designer takes them in (cites OWNER:<tsn> in record.json or "
                                "tree.json), or a hand repin cites them once a reader confirms they are taken in")
    try:
        repin(d, sources, "dry run", repo=repo, dry=True)
    except Refused as e:
        return sources, refusal(["designer_stage.repin refused: %s" % e], str(e),
                                "repair what the refusal names; the next tick tries again")
    return sources, None


def repin(d, sources, why, repo=None, dry=False):
    """His card changed a LOCKED version (version/VERSION.json state locked): re-pin the accepted results' frozen
    inputs to the current hashes so the stage machine does not reopen stage 1 to re-argue what he decided. `sources`
    are "OWNER:<tsn>@<commit>" (his card and the commit that carried it out) or "OWNER:<tsn>" (his word on the item,
    taken in with no file change). Every source is his word (byCard or ownerSaid) on the OWNER shard; every commit is
    tied to its card (change_tied); every commit since a stage's pin that moved one of its file inputs is cited; every
    owner event on the item new since that pin is cited; no change is uncommitted. Refused otherwise, stage.json
    untouched. -> the re-pinned stages. `dry` runs every check and writes nothing (-> the stages it would re-pin or
    void): the Maturation tick's own re-pin is judged by this same checker before it acts."""
    repo = repo or clone_of(d) or REPO
    if not CT.txt(why):
        raise Refused("a repin says why")
    st = load_state(d)
    ver = read_json(os.path.join(d, VERSION_FILE)) or {}
    if ver.get("state") != "locked":
        raise Refused("%s is not locked (state %r): an unlocked concept's changed inputs reopen its stages" % (
            VERSION_FILE, ver.get("state")))
    if not sources:
        raise Refused("no source: a locked change cites his OWNER event (OWNER:<tsn>@<commit>)")
    owner_ev = CT.owner_events(repo, clone_of(d))
    events = ledger_events(repo)
    cited, words = {}, set()          # full commit -> tsn; every tsn cited
    for sv in sources:
        t = _TEXT_SOURCE.match(str(sv).strip())
        if t:
            full = (_git(repo, "rev-parse", "--verify", "%s^{commit}" % t.group(1)) or b"").decode().strip()
            if not full:
                raise Refused("commit %s does not resolve" % t.group(1))
            ok, why_not = test_text_only(d, full, repo)
            if not ok:
                raise Refused("%s is not a change of test text only (%s): a changed bar is his card, OWNER:<tsn>@%s" % (
                    sv, why_not, full[:10]))
            cited[full] = "TEXT"
            continue
        m = _REPIN_SOURCE.match(str(sv).strip())
        if not m:
            raise Refused("source %r is not OWNER:<tsn>[@<commit>] or TEXT@<commit>: a locked change is his word, or "
                          "a change of scene test text only (a Conductor instruction is not his quotation)" % sv)
        tsn, ref = m.group(1), m.group(2)
        ev = owner_ev.get(tsn)
        if not isinstance(ev, dict):
            raise Refused("OWNER:%s is not on the OWNER shard" % tsn)
        if not (CT.txt(ev.get("ownerSaid")) or CT.txt(ev.get("byCard"))):
            raise Refused("OWNER:%s carries no byCard or ownerSaid: it is not his word" % tsn)
        words.add(tsn)
        if ref:
            full = (_git(repo, "rev-parse", "--verify", "%s^{commit}" % ref) or b"").decode().strip()
            if not full:
                raise Refused("commit %s does not resolve" % ref)
            if not change_tied(ev, full, repo, events):
                raise Refused("commit %s is not tied to OWNER:%s (%s): neither cites the other, and no ledger event on "
                              "%s names the commit" % (full[:10], tsn, ev.get("id"), ev.get("id")))
            cited[full] = tsn
    cur = inputs(d, st, repo)
    rel = os.path.relpath(d, repo).replace(os.sep, "/")
    head = os.path.join(d, ".repin-head")
    os.makedirs(head, exist_ok=True)
    try:
        for fn in INPUT_FILES.values():
            blob, err = _blob_at(repo, "HEAD", "%s/%s" % (rel, fn))
            if err:
                raise Refused("UNMEASURED: %s: the committed %s cannot be read, so no change is called committed" % (
                    err, fn))
            if blob is not None:
                with open(os.path.join(head, fn), "wb") as f:
                    f.write(blob)
        committed = {k: input_hash(head, k) for k in INPUT_FILES}
    finally:
        import shutil
        shutil.rmtree(head, ignore_errors=True)
    used, plan, frozen_now = set(), {}, owner_uncited(repo, st.get("item"), d)
    for r in sorted(accepted(st), key=lambda r: r["stage"]):
        changed = [k for k in DEPS[r["stage"]] if r["inputs"].get(k) != cur.get(k)]
        if not changed:
            continue
        for k in changed:
            if k == "owner":
                new = sorted(set(frozen_now or []) - set(r.get("owner_uncited") or []))
                miss = [t for t in new if t not in words]
                if frozen_now is None or miss:
                    raise Refused("stage %d: his new words on %s are not cited: %s" % (
                        r["stage"], st.get("item"), ", ".join("OWNER:" + t for t in miss) or "the shard is unreadable"))
                continue
            if cur.get(k) != committed.get(k):
                raise Refused("stage %d: %s has an uncommitted change; a locked change is the committed one" % (
                    r["stage"], INPUT_FILES[k]))
            commits, err = input_changes(d, k, repo, r["inputs"].get(k), (r.get("pinned_at") or {}).get(k))
            if commits is None:
                raise Refused("stage %d: %s" % (r["stage"], err))
            miss = [c for c in commits if c not in cited]
            if miss:
                raise Refused("stage %d: %s was changed by %s, which no source cites" % (
                    r["stage"], k, ", ".join(c[:10] for c in miss)))
            used.update(commits)
        plan[r["stage"]] = changed
    if not plan:
        raise Refused("nothing to re-pin: no accepted stage is stale")
    # RIMMANDRAKE_REPIN_STAGE_FOUR_LEAVES_EXAM_VOID: the exam is frozen against a tree and a sheet (exam_errors compares
    # them). Re-pinning stage 4 over a changed tree or sheet read stage 4 accepted while its exam was void (Pyrelands,
    # repin @91a7c61989). So stage 4 is left stale instead: stale_stage reports 4 and the next open retakes the exam.
    voided = {4: plan.pop(4)} if set(plan.get(4) or ()) & set(EXAM_FROZEN) else {}
    idle = [c for c in cited if c not in used]
    if idle:
        raise Refused("cited commit(s) %s changed none of the stale inputs: not the change cited" % (
            ", ".join(c[:10] for c in idle)))
    if dry:                           # RIMMANDRAKE_REPIN_WHEN_GRANT_ITEMS_CLOSE: every check passed, nothing written
        return sorted(set(plan) | set(voided))
    at = now_iso()
    # RIMMANDRAKE_TRACE_REPIN_FROM_FIRST_PIN_B_CHANGE_SKIPPED: the anchor is RECORDED here, at pin time, so the next
    # trace reads the window [this commit, HEAD] instead of guessing which occurrence of the pinned hash was the pin.
    # HEAD is the right anchor: every file input was just checked equal to its committed blob (`committed` above).
    # unreadable now (it was read a moment ago for `committed`): recorded as PIN_UNREAD, never the stale older anchor
    pin_at = (_git(repo, "rev-parse", "--verify", "HEAD^{commit}") or b"").decode().strip() or PIN_UNREAD
    for r in accepted(st):
        if r["stage"] in plan:
            r["inputs"] = dict(r["inputs"], **{k: cur.get(k) for k in plan[r["stage"]]})
            r["pinned_at"] = dict(r.get("pinned_at") or {},
                                  **{k: pin_at for k in plan[r["stage"]] if k in INPUT_FILES})
            if "owner" in plan[r["stage"]]:
                r["owner_uncited"] = frozen_now
            r.setdefault("repinned", []).append({"at": at, "inputs": plan[r["stage"]], "sources": list(sources)})
    for r in accepted(st):
        if r["stage"] in voided:
            r.setdefault("voided", []).append({"at": at, "inputs": voided[r["stage"]], "sources": list(sources),
                                               "why": "its exam ran against another tree or sheet: retake it"})
    # RIMMANDRAKE_UNLOCK_REPIN_VOIDED_EXAM_NEXT_OPEN_REFUSED: a locked status refuses every open and owes no maturation
    # chain, so a voided exam on a locked concept could never be retaken. His card is the word that unlocks it; stage 5's
    # coverage signature locks it again after the retake.
    unlocked = bool(voided) and st.get("status") == "locked"
    if unlocked:
        st["status"] = "ready"
    hist(st, "locked_change", "%s; re-pinned %s%s%s; sources %s" % (why, "; ".join(
        "stage %d (%s)" % (s, ", ".join(ks)) for s, ks in sorted(plan.items())) or "nothing", "".join(
        "; stage %d left stale, its exam void (%s changed): the next open retakes it" % (s, ", ".join(ks))
        for s, ks in sorted(voided.items())), "; unlocked for the retake, stage 5 locks it again" if unlocked else "",
        ", ".join(sources)))
    write_json(state_path(d), st)
    return sorted(plan)


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
    try:
        rec = read_json(os.path.join(d, "record.json"), {}) or {}
    except Refused as e:    # the run that opens is the one to repair it, so it still gets its packet
        return "(%s: repair it first)" % e
    if not isinstance(rec, dict):
        return "(record.json is not an object: repair it first)"
    out = []
    if isinstance(rec.get("root"), dict):
        out.append("root: %s [%s]" % (rec["root"].get("text"), ",".join(map(str, lst(rec["root"].get("source"))))))
    for sect in ("scope", "decisions", "asks", "inventory", "contradictions"):
        rows = [e for e in rec.get(sect) or [] if isinstance(e, dict)] if isinstance(rec.get(sect), list) else []
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
                                             ",".join(map(str, lst(e.get("source"))))))
    if rec.get("failure_modes"):
        out.append("failure_modes: " + " | ".join(map(str, lst(rec["failure_modes"]))))
    return "\n".join(out) or "(empty: record.json has no entries yet)"


def packet(d, st, hashes, budget, why=None, retries=0, manifest=MANIFEST, repo=None):
    s = st["stage"]
    head = [
        "[designer_stage.py packet: concept %s, stage %d %s, run %s]" % (
            st.get("mod"), s, STAGE_NAMES[s], (st.get("running") or {}).get("run")),
        # no cap, spend or share figure (owner 2026-11-16, RIMMANDRAKE_HIDE_SPEND_FROM_BUILDERS_CAP_NAGGED_EVERY_TURN:
        # the agent is never told its spend); the launcher still charges the task, stage.json keeps the figures
        "Folder: %s. The launcher keeps this task's accounting; a fresh run does not reset it." % d,
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
    if draft_line(st):
        head.append(draft_line(st))
    if helper_line(st):
        head.append(helper_line(st))
    held = [r for r in st.get("recovery") or [] if r.get("state") == "held"]
    if held:
        head.append("Held for his review: %s." % ", ".join("%s (until %s)" % (r["scene"], r.get("until")) for r in held))
    body = ["", "## Working record (record.json)", working_record(d)]
    if s in (0,) + DIALOGUE:
        body += built_section(REPO if repo is None else repo, st)
    body += elsewhere_section(REPO if repo is None else repo, d, st)
    body += conversion_section(REPO if repo is None else repo, d, st)
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
    """The Designer role's clone (dispatcher_schedule.json), where its runs write design/concepts, or None. A clone
    that is not on disk (role_clones.py ensure makes it) is None too: concepts_root then reads this clone's own
    design/concepts, never an absent folder that would read as "no concepts"."""
    try:
        with open(schedule, encoding="utf-8") as f:
            sch = json.load(f)
    except (OSError, ValueError):
        return None
    for r in (sch.get("roles") if isinstance(sch, dict) else None) or []:
        if isinstance(r, dict) and r.get("stage_machine") == "designer_stage" and r.get("clone"):
            return r["clone"] if os.path.isdir(os.path.join(r["clone"], ".git")) else None
    return None


def concepts_root(schedule=SCHEDULE):
    return os.path.join(designer_clone(schedule) or REPO, "design", "concepts")


def epoch(iso):
    try:
        return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def his_answers(lines, item, since):
    """tsns of OWNER-shard events naming `item` after `since` (epoch s) that carry his own word (ownerSaid or byCard), or
    that are the Conductor window's act under the five-acts ruling (owner 2026-11-19: the Conductor reviews every card
    bound for him and acts when nothing argues against the obvious answer; conductor_acts.is_conductor_event): the answer
    that takes a waiting turn off his doorstep and lifts a park. A seat's lifecycle move or another --per-ruling note
    also lands on OWNER.jsonl, but it is not an answer to these asks."""
    import conductor_acts as CA
    out = []
    for ln in lines or []:
        if item not in ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if (not isinstance(ev, dict) or ev.get("id") != item or ev.get("event") in LIFECYCLE
                or not (CT.txt(ev.get("ownerSaid")) or CT.txt(ev.get("byCard")) or CA.is_conductor_event(ev)[0])):
            continue
        try:
            tsn = int(ev.get("tsn"))
        except (TypeError, ValueError):
            continue
        if tsn / 1e9 > since:
            out.append(str(tsn))
    return sorted(out)


def turn_file(d, entry):
    """The turn_NN.md the waiting result names, else the highest-numbered turn file in the folder, else None."""
    m = re.search(r"(?:[A-Za-z0-9_./-]*/)?turn_[0-9]+\.md", str((entry or {}).get("summary") or ""))
    if m and os.path.isfile(os.path.join(d, os.path.basename(m.group(0)))):
        return os.path.join(d, os.path.basename(m.group(0)))
    try:
        turns = sorted((n for n in os.listdir(d)
                        if re.fullmatch(r"turn_[0-9]+\.md", n) and os.path.isfile(os.path.join(d, n))),
                       key=lambda n: (int(n[5:-3]), n))
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
    pk = st.get("park") if isinstance(st.get("park"), dict) else None
    since = epoch((pk or last).get("at")) or 0
    if lines is None:
        lines = CT.owner_lines(repo, clone_of(d))
    if item and lines is not None and his_answers(lines, item, since):
        return None
    rec = read_json(os.path.join(d, "record.json")) or {}
    asks = [{"id": a.get("id"), "text": " ".join(str(a.get("text") or "").split()),
             "evidence": " ".join(str(a.get("evidence_against") or "").split())}
            for a in rec.get("asks") or [] if isinstance(a, dict) and a.get("status") == "sent"]
    if pk:      # a park's page is the turn, its reason the first ask
        asks = [{"id": "park", "text": "parked (%s): %s" % (pk.get("kind"), pk.get("why"))}] + asks
    return {"mod": st.get("mod") or os.path.basename(d), "item": item, "stage": st.get("stage"),
            "run": last.get("run"), "at": (pk or last).get("at"),
            "turn": os.path.join(d, pk.get("summary") or PARK_FILE) if pk else turn_file(d, last), "asks": asks,
            "dir": d, "owner_unread": lines is None, "quick_look": bool((pk or {}).get("quick_look")
                                                                        or (last.get("quick_look") or {}).get("offer"))}


def pending_turns(root=None, repo=REPO):
    """-> ([turn], [unreadable: "<dir>: why"]) over every concept folder under `root` (default: the Designer's clone).
    Skips `_`-prefixed folders and entries without a stage file. A failed stage stat names the folder as unreadable
    (`unsearchable_designer_folder_reads_as_empty`)."""
    root = root or concepts_root()
    out, bad = [], []
    try:
        names = sorted(os.listdir(root))
    except OSError as e:
        return [], ["%s: %s" % (root, e)]
    lines = None
    for n in names:
        d = os.path.join(root, n)
        if n.startswith("_"):
            continue
        try:
            if not stat.S_ISREG(os.stat(os.path.join(d, "stage.json")).st_mode):
                continue
        except (FileNotFoundError, NotADirectoryError):
            continue
        except OSError as e:
            bad.append("%s: %s" % (d, e))
            continue
        try:
            if lines is None:
                lines = CT.owner_lines(repo, clone_of(d))
            t = pending_turn(d, repo, lines)
        except Exception as e:      # noqa: BLE001 - one bad folder is said, never drops the rest
            bad.append("%s: %s" % (d, str(e)))
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
    return "%s%s Designer turn (stage %s) waits on you since %s: %d %s%s in %s%s" % (
        "QUICK LOOK OFFERED: " if t.get("quick_look") else "", t["mod"], t["stage"],
        (t.get("at") or "?").replace("T", " "), n, "ask" if n == 1 else "asks",
        " (%s)" % ", ".join(str(a["id"]) for a in t["asks"]) if n else "", owner_path(t.get("turn") or t["dir"]),
        "".join(" | %s: %s%s" % (a["id"], a["text"], ask_mark(a)) for a in t["asks"]))


def ask_mark(a):
    """Evidence-for-Ask (owner, 2026-11-15): an ask on his line says what argues against its obvious answer, or that
    nothing does and the Conductor takes it delegated (the park line carries no evidence field and no mark)."""
    if "evidence" not in a:
        return ""
    if a["evidence"]:
        return " [evidence against the obvious answer: %s]" % a["evidence"]
    return (" [no evidence against the obvious answer: the Conductor takes it delegated, --per-ruling %s]"
            % EVIDENCE_FOR_ASK)


def open_preview(d, run, run_cap=None):
    """`open --preview`: the open gate's own answer, read only. -> 0 would open, 1 refuses (the gate's words printed),
    126 could not look (launch_checks reads 126 as did-not-run, never a refusal)."""
    try:
        open_run(d, run, run_cap, commit=False)
    except Refused as e:
        print("REFUSED: %s" % e)
        return 1
    except Exception as e:      # an unreadable file or a fault in the gate: no answer, never a refusal or an open
        print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        return 126
    print("open: would open %s" % os.path.basename(os.path.abspath(d)))
    return 0


def status(d, repo=REPO):
    st = load_state(d)
    s, changed = stale_stage(d, st, repo)
    return {"mod": st.get("mod"), "stage": st["stage"], "status": st["status"], "spent": st["budget"]["spent"],
            "cap": task_cap(st), "reserve": st["budget"]["reserve"], "running": st.get("running"),
            "stale_from": s, "stale_inputs": changed, "coverage": CT.coverage_summary(d, repo),
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
    x.add_argument("--runner", choices=("claude", "codex"), help="the concept's runner for every launch (default: the role's)")
    x.add_argument("--draft", help="a first-touch draft another model made: named in the stage 0-3 packets as input to verify")
    x.add_argument("--draft-by", help="who made the draft (e.g. 'Codex, lane E 2026-11-15')")
    for name in ("open", "close"):
        x = sub.add_parser(name)
        x.add_argument("dir")
        x.add_argument("--run", required=True)
        # a hand close states its spend: with no --tokens close_run charges the whole reservation as unmeasured,
        # which a steward's hand exam does not spend (RIMMANDRAKE_REQUIRE_TOKENS_ON_HAND_CLOSE_PHANTOM_RESERVATION)
        x.add_argument("--run-cap" if name == "open" else "--tokens", type=int, required=name == "close")
        if name == "open":
            # RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_LAUNCH_CHECKS: the launcher's own preview, for a launch check
            x.add_argument("--preview", action="store_true", help="open_run(commit=False): exit 0 would open, 1 refuses "
                           "(its words printed), 126 could not look; no packet printed, nothing written")
    x = sub.add_parser("charge")
    x.add_argument("dir")
    x.add_argument("--tokens", type=int, required=True)
    x.add_argument("--kind", required=True, choices=CHARGE_KINDS)
    x.add_argument("--ref", required=True)
    for name in ("check", "status"):
        sub.add_parser(name).add_argument("dir")
    x = sub.add_parser("exam-control", help="write the Stage 4 control copy: the tree and sheet with one leaf removed")
    x.add_argument("dir")
    x.add_argument("--leaf", required=True)
    x.add_argument("--strip", action="append", default=[], metavar="PHRASE",
                   help="a paraphrase of the removed rule: the program drops every sheet line and list entry holding "
                        "it and blanks any other text holding it (repeatable; never edit the copy by hand)")
    x = sub.add_parser("land", help="land the concept's stage.json and result files on origin/main (close does it)")
    x.add_argument("dir")
    x.add_argument("--run", default="catch-up")
    x = sub.add_parser("unblock-closed", help="lift every block whose ledger item is closed (dry unless --apply)")
    x.add_argument("--root", help="the concepts folder (default: this clone's design/concepts)")
    x.add_argument("--apply", action="store_true")
    x = sub.add_parser("unblock")
    x.add_argument("dir")
    x.add_argument("--why", required=True)
    x = sub.add_parser("repin", help="a LOCKED version changed by his card: re-pin the accepted stages' inputs")
    x.add_argument("dir")
    x.add_argument("--source", action="append", default=[],
                   help="OWNER:<tsn>@<commit> (his card and the commit carrying it out), OWNER:<tsn> (his word, no file), or "
                        "TEXT@<commit> (a commit that changed only scene test text: no bar, no card)")
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
            init(a.dir, a.mod, a.item, a.cap, a.reserve, a.alias, a.runner, a.draft, a.draft_by)
            print("init %s: stage 0" % a.dir)
        elif a.cmd == "open" and a.preview:
            return open_preview(a.dir, a.run, a.run_cap)
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
            print("charged %d" % a.tokens)     # no task total: the Designer runs this (owner 2026-11-16; `status` shows it)
        elif a.cmd == "check":
            st = load_state(a.dir)
            errs = result_errors(read_json(os.path.join(a.dir, "result.json")), a.dir, st)
            print("\n".join(errs) if errs else "result.json would be accepted")
            return 1 if errs else 0
        elif a.cmd == "status":
            print(json.dumps(status(a.dir), indent=1))
        elif a.cmd == "exam-control":
            rec = exam_control(a.dir, a.leaf, a.strip)
            print("control copy in %s: %s removed (%s)" % (os.path.join(a.dir, CONTROL_DIR), rec["leaf"],
                                                           json.dumps(rec)))
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
        elif a.cmd == "unblock-closed":
            try:
                rows = unblock_closed(a.root or os.path.join(REPO, "design", "concepts"), apply=a.apply)
            except Refused as e:
                print("unblock-closed: %s" % e, file=sys.stderr)
                return 126
            for d, item in rows:
                print("%s %s: blocked on %s, which is closed" % ("lifted" if a.apply else "would lift",
                                                                  os.path.basename(d), item))
            if not rows:
                print("unblock-closed: no concept is blocked on a closed item (ledger read)")
        elif a.cmd == "unblock":
            unblock(a.dir, a.why)
        elif a.cmd == "repin":
            print("re-pinned stage(s) %s: %s" % (", ".join(map(str, repin(a.dir, a.source, a.why))), a.dir))
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
