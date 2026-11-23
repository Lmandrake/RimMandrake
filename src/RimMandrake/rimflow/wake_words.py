#!/usr/bin/env python3
"""wake_words.py: what the owner said since the previous wake, printed by a program at the Conductor's wake.

Item RIMMANDRAKE_SHOW_HIS_WORDS_AT_WAKE_FRESH_WINDOW_DENIED_A_MOD_PASS. Page:
design/specs/2026-11-23-wake-his-words/boundary.md. Tests: selftest_wake_words.py (one per promise) and
acceptance/wake_his_words_accept.py (the item's acceptance test).

The failure (2026-11-23): the Conductor window restarted at its 400k limit with no handoff. His "GSS walk full pass.
Looks great!" was on the OWNER shard; the wake printed none of his words, and the fresh window read a stale note and
told him the mod was not passed. A window at its context limit is the least reliable author, so nothing here is
written by a model: every line comes from records that already exist (the OWNER shard, the stage records, the hold
list, the window transcripts).

`seat_restart.py wake` calls Wake(...).first() before any other line, .sections() after the old window's last reply,
and .stamp() at its end. Every section keeps four answers apart: UNMEASURED (could not look, cause named), FAILED (the
code raised, cause named), "looked: none", and a list. A section that cannot look never stops the others.

No text cut and no count cap anywhere: his words are printed whole. The only number that shapes output is GROUP_AT
(a layout choice: above it, section 1 groups by item; every event is still printed).
"""
import datetime
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seat_restart as SR  # noqa: E402

try:
    from zoneinfo import ZoneInfo
    PAC = ZoneInfo("America/Los_Angeles")
except Exception:                                   # noqa: BLE001 - no tz database: say UTC, never a wrong offset
    PAC = None

SHARDS = os.path.join("infrastructure", "state", "ledger", "events")
CONCEPTS = os.path.join("design", "concepts")
RECORD = os.path.join("version", "stage_record.json")
GROUP_AT = 30           # layout only: more of his words than this print grouped by item, every one still printed
MATCH_BEFORE_S = 3600   # an event up to 1 h older than the message may hold it: the probe's rule (probe_his_words.py);
#                         a message typed while the window was mid-turn is stamped when it is delivered, after the
#                         window may already have recorded it
WORD_FIELDS = ("ownerSaid", "byCard")
ECHO_FIELDS = ("ownerSaid", "text", "why", "title", "byCard", "reason")
STAGE_LINE = {"intake": "Intake, ideas waiting", "designer": "Stage 1, the Designer", "preflight": "Stage 2, preflight",
              "offline_build": "Stage 3, offline build", "blind_challenge": "Stages 4 and 5, the blind challenge",
              "in_game": "Stage 6, in-game acceptance", "pre_human": "Stage 7, the walk brief",
              "his_walk": "Stage 8, his live walk", "passed": "Version passed"}


def pac(t):
    """epoch -> '2026-11-22 9:56 PM PST' (local Pacific, the owner's clock)."""
    if t is None:
        return "(no time)"
    d = datetime.datetime.fromtimestamp(t, PAC) if PAC else datetime.datetime.utcfromtimestamp(t)
    return "%s %s %s" % (d.strftime("%Y-%m-%d"), d.strftime("%I:%M %p").lstrip("0"), d.strftime("%Z") if PAC else "UTC")


class Unmeasured(Exception):
    """Could not look. The message is the cause, said to the reader by name."""


# ---- normalising and matching (the probe's rule, src/RimMandrake/Utils/probe_his_words.py) ---

def norm(s):
    s = re.sub(r"<system-reminder>.*?</system-reminder>", " ", str(s or ""), flags=re.S)
    s = re.sub(r"\[Image #\d+\]", " ", s)
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.findall(r"[a-z0-9']+", s.lower())


def grams(w, n=5):
    return {tuple(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def _near_run(words, other):
    """A message under five words is matched when its words, joined, are within a typo of a run of as many words in
    `other` (difflib ratio >= 0.85; 'Thin outlien' matches 'thin outline')."""
    import difflib
    flat, k = " ".join(words), len(words)
    for i in range(max(1, len(other) - k + 1)):
        run = " ".join(other[i:i + k])
        if run == flat or difflib.SequenceMatcher(None, flat, run).ratio() >= 0.85:
            return True
    return False


def home_of(words, said, echoes):
    """-> ("QUOTED", event) | ("ECHOED", event) | (None, None) for one typed message's normalised words.
    said: [(event, its ownerSaid words)] in the time window; echoes: [(event, words of all ECHO_FIELDS)].
    QUOTED, the owner-said match: an ownerSaid holds >= half of the message's 5-word runs, or a quote of 5+ words lies
    (>= 80% of its runs) inside the message, or (a message under five words) a run of the quote is within a typo of it.
    ECHOED: no owner-said match, but some field holds a quarter of its runs or 8 words in a row."""
    if not words:
        return None, None
    g = grams(words)
    n = len(words)
    union, best = set(), None
    for ev, w in said:
        if n < 5:
            if _near_run(words, w):
                return "QUOTED", ev
            continue
        eg = grams(w)
        hit = g & eg
        if eg and len(hit) >= 0.8 * len(eg):
            return "QUOTED", ev
        if hit and (best is None or len(hit) > best[0]):
            best = (len(hit), ev)
        union |= hit
    if g and len(union) >= 0.5 * len(g):
        return "QUOTED", best[1] if best else None
    g8 = grams(words, 8)
    union = set()
    for ev, w in echoes:
        eg = grams(w)
        if g8 and g8 & grams(w, 8):
            return "ECHOED", ev
        union |= (g & eg)
        if g and len(union) >= 0.25 * len(g):
            return "ECHOED", ev
    return None, None


# ---- the ledger: every shard read once ------------------------------------------------------------------------------

class Ledger(object):
    """events: every parsed event from every shard (with _ts epoch and _shard); titles: item id -> its newest title;
    bad: ["<shard> line N: why"] for lines that are not events (a torn last line included). Raises Unmeasured when the
    shard folder or the OWNER shard cannot be read."""

    def __init__(self, clone):
        self.dir = os.path.join(clone, SHARDS)
        self.owner_path = os.path.join(self.dir, "OWNER.jsonl")
        self.events, self.titles, self.bad = [], {}, []
        files = sorted(glob.glob(os.path.join(self.dir, "*.jsonl")))
        if not os.path.isfile(self.owner_path):
            raise Unmeasured("no OWNER shard at %s" % self.owner_path)
        for f in files:
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError as e:
                if f == self.owner_path:
                    raise Unmeasured("the OWNER shard %s cannot be read (%s)" % (f, type(e).__name__))
                self.bad.append("%s: unreadable (%s)" % (os.path.basename(f), type(e).__name__))
                continue
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    self.bad.append("%s line %d: not JSON%s" % (os.path.basename(f), i,
                                                                " (torn last line)" if i == len(lines) else ""))
                    continue
                if not isinstance(e, dict):
                    self.bad.append("%s line %d: not an event" % (os.path.basename(f), i))
                    continue
                e["_ts"] = SR._ts(e.get("ts"))
                e["_shard"] = os.path.basename(f)[:-len(".jsonl")]
                self.events.append(e)
                if e.get("id") and e.get("title"):
                    self.titles[e["id"]] = e["title"]
        self.events.sort(key=lambda e: (e["_ts"] or 0, e.get("tsn") or 0))

    def his_words(self, since=None):
        """-> OWNER-shard events that carry his words (ownerSaid or byCard), since `since` (epoch) when given, oldest
        first. An event with no readable time is kept (it may be recent) and said as such."""
        out = []
        for e in self.events:
            if e["_shard"] != "OWNER" or not any(e.get(k) for k in WORD_FIELDS):
                continue
            if since is not None and e["_ts"] is not None and e["_ts"] < since:
                continue
            out.append(e)
        return out

    def owner_bad(self):
        return [b for b in self.bad if b.startswith("OWNER.jsonl")]


def event_ref(e):
    return "%s:%s" % (e.get("_shard") or e.get("seat") or "?", e.get("tsn") or e.get("ts") or "?")


def words_lines(e, indent="    "):
    out = []
    if e.get("ownerSaid"):
        out.append('%ssaid: "%s"' % (indent, str(e["ownerSaid"]).strip()))
    if e.get("byCard"):
        out.append('%sby card: "%s"' % (indent, str(e["byCard"]).strip()))
    return out


# ---- mods -------------------------------------------------------------------------------------------------------------

def mod_terms(mod):
    """The spellings a ledger line uses for a mod: GimmeSomeSlack -> 'gimmesomeslack', 'gimme some slack' and, for a
    name of three or more capitals, its initials 'gss'."""
    parts = [p.lower() for p in re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", mod)]
    terms = {mod.lower(), " ".join(parts)}
    if len(parts) >= 3:
        terms.add("".join(p[0] for p in parts))
    return {t for t in terms if t}


def names_mod(text_words, terms):
    flat = " " + " ".join(text_words) + " "
    return any((" %s " % t) in flat for t in terms)


def event_names_mod(e, terms, titles):
    blob = " ".join(str(e.get(k) or "") for k in ("id", "text", "ownerSaid", "byCard", "why", "title"))
    blob += " " + str(titles.get(e.get("id")) or "")
    return names_mod(norm(blob.replace("_", " ")), terms)


def read_mods(clone):
    """-> [(mod, record or None, why unreadable or None)] for every design/concepts/*/version/stage_record.json.
    Raises Unmeasured when the concepts folder cannot be listed."""
    root = os.path.join(clone, CONCEPTS)
    try:
        names = sorted(os.listdir(root))
    except OSError as e:
        raise Unmeasured("the mod folders %s cannot be listed (%s)" % (root, type(e).__name__))
    out = []
    for m in names:
        p = os.path.join(root, m, RECORD)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                rec = json.load(f)
            out.append((m, rec if isinstance(rec, dict) else None, None if isinstance(rec, dict) else "not a record"))
        except (OSError, ValueError) as e:
            out.append((m, None, "%s: %s" % (type(e).__name__, p)))
    return out


def read_holds():
    """-> ({mod: hold}, None) or (None, cause). The hold list as every pipeline status reads it (file and control
    store)."""
    try:
        import mod_owner_hold as MOH
        return MOH.load(), None
    except Exception as e:                          # noqa: BLE001 - Unreadable or a broken import: said by name
        return None, "%s: %s" % (type(e).__name__, e)


def passes_since(mods, since):
    """-> [(mod, move)] for each stage-record move to `passed` at or after `since`."""
    out = []
    for m, rec, _ in mods:
        for mv in (rec or {}).get("moves") or []:
            if isinstance(mv, dict) and mv.get("to") == "passed":
                t = SR._ts(mv.get("at"))
                if since is None or (t is not None and t >= since):
                    out.append((m, mv))
    return out


# ---- transcripts ------------------------------------------------------------------------------------------------------

def first_ts(path):
    """-> the first record time in a transcript, or None."""
    try:
        with open(path, "rb") as f:
            for raw in f:
                try:
                    r = json.loads(raw)
                except ValueError:
                    continue
                t = SR._ts(r.get("timestamp")) if isinstance(r, dict) else None
                if t is not None:
                    return t
    except OSError:
        return None
    return None


def window_transcripts(cfg, since, me_sid=None, extra=()):
    """-> the transcripts of this seat's windows (is_window_of) written at or after `since`, the reader's own excluded,
    plus `extra` (the old window's path the wake already knows). Raises Unmeasured when the folder cannot be listed."""
    pdir = os.path.dirname(SR.transcript_path(cfg.get("clone") or SR.REPO, "x"))
    try:
        names = [n for n in os.listdir(pdir) if n.endswith(".jsonl")]
    except OSError as e:
        raise Unmeasured("the window transcripts folder %s cannot be listed (%s)" % (pdir, type(e).__name__))
    out = []
    for n in names:
        p = os.path.join(pdir, n)
        if me_sid and n[:-6] == me_sid:
            continue
        try:
            if since is not None and os.path.getmtime(p) < since:
                continue
        except OSError:
            continue
        if SR.is_window_of(p, cfg.get("session_name")):
            out.append(p)
    for p in extra:
        if p and p not in out and not (me_sid and os.path.basename(p)[:-6] == me_sid):
            out.append(p)
    return sorted(out)


def typed_since(paths, since):
    """-> (messages, blind): messages are {ts, text, window, words} for every message he typed in those transcripts at
    or after `since`, oldest first, one per message (a copy in two transcripts counted once); blind is
    ["<path>: why"] for a transcript that could not be read to its end."""
    msgs, blind, seen = [], [], set()
    for p in paths:
        sc = SR.cursor_scan(p, 0)
        if sc is None:
            blind.append("%s: unreadable" % p)
            continue
        if sc["malformed"]:
            blind.append("%s: %s (read up to that line)" % (p, sc["malformed"]))
        for r in sc["human"]:
            t = SR._ts(r.get("timestamp"))
            if since is not None and t is not None and t < since:
                continue
            text = re.sub(r"<system-reminder>.*?</system-reminder>", "", SR._text(r), flags=re.S).strip()
            words = norm(text)
            key = (r.get("uuid") or "", " ".join(words), int(t or 0) // 60)
            if (key[0] and key[0] in seen) or key[1:] in seen:
                continue
            seen.update({key[0], key[1:]} - {""})
            extra = SR._non_text(r)
            msgs.append({"ts": t, "text": text, "words": words, "window": os.path.basename(p)[:8],
                         "extra": extra})
    msgs.sort(key=lambda m: m["ts"] or 0)
    return msgs, blind


# ---- the wake ---------------------------------------------------------------------------------------------------------

def stamp_path(seat, root=None):
    return os.path.join(SR.restart_dir(root), "%s.wake_words.json" % seat)


class Wake(object):
    """One Conductor wake's reading. Built once at the top of cmd_wake; nothing in it raises out."""

    def __init__(self, seat, cfg, rec=None, me=None, root=None, old_tx=None, now=None):
        import time
        self.seat, self.cfg, self.rec, self.root = seat, cfg, rec or {}, root
        self.me = me or {}
        self.now = now if now is not None else time.time()
        self.clone = cfg.get("clone") or SR.REPO
        self.old_tx = old_tx
        self.ledger = self.ledger_err = None
        try:
            self.ledger = Ledger(self.clone)
        except Unmeasured as e:
            self.ledger_err = "UNMEASURED: %s" % e
        except Exception as e:                      # noqa: BLE001 - FAILED, said by name
            self.ledger_err = "FAILED: %s: %s" % (type(e).__name__, e)
        self.since, self.since_how = self._since()
        self.mods = self.mods_err = None
        try:
            self.mods = read_mods(self.clone)
        except Unmeasured as e:
            self.mods_err = "UNMEASURED: %s" % e
        except Exception as e:                      # noqa: BLE001
            self.mods_err = "FAILED: %s: %s" % (type(e).__name__, e)

    def _since(self):
        """-> (epoch or None, how it was read). The previous wake of this seat, from the stamp the last wake wrote;
        a window that never ended a turn after its wake did not tell him anything, so its own `since` carries back.
        The first time (no stamp), the start of the old window's transcript. The earlier of the two when both read."""
        cands = []
        st = SR._read_json(stamp_path(self.seat, self.root)) or {}
        self.repeat = None              # the time this window already printed the sections, or None
        if st.get("at"):
            if self.me.get("sessionId") and st.get("session") == self.me.get("sessionId"):
                self.repeat = pac(st["at"])
                cands.append((st.get("since") or st["at"], "this window's own earlier wake read from %s" % pac(
                    st.get("since") or st["at"])))
            elif st.get("tx") and not SR._turn_ended_since(st["tx"], st["at"]):
                cands.append((st.get("since") or st["at"], "the wake before last (the last woken window ended no turn)"))
            else:
                cands.append((st["at"], "the previous wake of %s" % self.seat))
        tx = self.old_tx or self.rec.get("tx_path")
        t0 = first_ts(tx) if tx else None
        if t0 is not None:
            cands.append((t0, "the start of the old window %s" % os.path.basename(tx)[:8]))
        if not cands:
            return None, None
        return min(cands, key=lambda c: c[0])

    # -- the first line of the whole wake --
    def first(self):
        """-> lines for the very top of the wake: every version passed since the previous wake, and his words since
        then on a mod that is at his walk (Stage 8): the two facts a fresh window must not get wrong."""
        try:
            return self._first()
        except Exception as e:                      # noqa: BLE001
            return ["== PASSES SINCE THE PREVIOUS WAKE: FAILED (%s: %s); read the stage records yourself" % (
                type(e).__name__, e)]

    def _first(self):
        if self.since is None:
            return ["== PASSES SINCE THE PREVIOUS WAKE: UNMEASURED: the time of the previous wake could not be read "
                    "(no wake stamp, no old transcript); read each mod's stage record before you tell him a mod's state"]
        if self.mods is None:
            return ["== PASSES SINCE THE PREVIOUS WAKE (%s): %s" % (pac(self.since), self.mods_err)]
        out = []
        for m, mv in passes_since(self.mods, self.since):
            rec = next(r for n, r, _ in self.mods if n == m)
            out.append("== PASSED SINCE THE PREVIOUS WAKE: %s %s passed at %s (by %s: %s)" % (
                m, (rec or {}).get("version") or "?", pac(SR._ts(mv.get("at"))), mv.get("by") or "?",
                mv.get("why") or ""))
        walk = []
        if self.ledger is not None:
            recent = self.ledger.his_words(self.since)
            for m, rec, _ in self.mods:
                if (rec or {}).get("stage") != "his_walk":
                    continue
                terms = mod_terms(m)
                for e in recent:
                    if event_names_mod(e, terms, self.ledger.titles):
                        walk.append("== HIS WORDS ON %s %s, WHICH IS AT HIS WALK (Stage 8), since the previous wake. "
                                    "Read them before you tell him its state: %s %s (%s)" % (
                                        m, rec.get("version") or "?", pac(e["_ts"]), e.get("id") or "-",
                                        event_ref(e)))
                        walk += words_lines(e)
        if not out and not walk:
            out.append("== PASSES SINCE THE PREVIOUS WAKE (%s): looked: none in the stage records" % pac(self.since))
        return out + walk

    # -- the three sections --
    def sections(self):
        out = []
        for f in (self._his_words, self._mods_now, self._homeless):
            try:
                out += f()
            except Exception as e:                  # noqa: BLE001 - a section that breaks never stops the others
                out.append("\n== %s: FAILED (%s: %s)" % (f.__name__.strip("_").replace("_", " ").upper(),
                                                         type(e).__name__, e))
        return out

    def since_text(self):
        return self._since_text()

    def _since_text(self):
        return "since %s, %s" % (pac(self.since), self.since_how)

    def _his_words(self):
        head = "\n== HIS WORDS SINCE THE PREVIOUS WAKE"
        if self.since is None:
            return [head + ": UNMEASURED: the time of the previous wake could not be read (no wake stamp, no old "
                    "transcript). Read the OWNER shard yourself before you tell him he has not said a thing."]
        if self.ledger is None:
            return [head + " (%s): %s" % (self._since_text(), self.ledger_err)]
        ev = self.ledger.his_words(self.since)
        out = [head + " (%s; from %s): %s, oldest first, word for word. These outrank any note about what he said." % (
            self._since_text(), self.ledger.owner_path, ("%d events" % len(ev)) if ev else "looked: none")]
        for b in self.ledger.owner_bad():
            out.append("UNMEASURED line: %s (its words, if any, are not shown)" % b)
        if len(ev) > GROUP_AT:
            order, by = [], {}
            for e in ev:
                k = e.get("id") or "(no item)"
                if k not in by:
                    order.append(k)
                    by[k] = []
                by[k].append(e)
            for k in order:
                out.append("- %s (%d):" % (k, len(by[k])))
                for e in by[k]:
                    out.append("  - %s (%s, %s)" % (pac(e["_ts"]), e.get("event") or "?", event_ref(e)))
                    out += words_lines(e, "      ")
        else:
            for e in ev:
                out.append("- %s %s (%s, %s)" % (pac(e["_ts"]), e.get("id") or "(no item)", e.get("event") or "?",
                                                 event_ref(e)))
                out += words_lines(e)
        return out

    def _mods_now(self):
        head = "\n== EACH MOD NOW (stage from its stage record; his newest words on an item that names it)"
        if self.mods is None:
            return [head + ": " + self.mods_err]
        holds, herr = read_holds()
        out = [head + ":"]
        if herr:
            out.append("UNMEASURED: the hold list could not be read (%s): every mod is listed, held or not" % herr)
        if self.ledger is None:
            out.append("his words: %s" % self.ledger_err)
        allw = self.ledger.his_words() if self.ledger is not None else []
        shown = 0
        for m, rec, why in self.mods:
            if holds is not None and m in holds:
                continue
            shown += 1
            if rec is None:
                out.append("- %s: stage UNMEASURED (%s)" % (m, why))
                continue
            st = rec.get("stage")
            line = "- %s %s: %s (since %s)" % (m, rec.get("version") or "?", STAGE_LINE.get(st, st or "?"),
                                              rec.get("since") or "?")
            if self.ledger is None:
                out.append(line)
                continue
            terms = mod_terms(m)
            mine = [e for e in allw if event_names_mod(e, terms, self.ledger.titles)]
            if not mine:
                out.append(line + "; his words on it: looked: none on the OWNER shard")
                continue
            e = mine[-1]
            new = self.since is not None and e["_ts"] is not None and e["_ts"] >= self.since
            out.append(line + "; his newest words on it%s: %s %s (%s)" % (
                " (NEW since the previous wake)" if new else "", pac(e["_ts"]), e.get("id") or "-", event_ref(e)))
            out += words_lines(e)
        if shown == 0:
            out.append("looked: none (every mod with a stage record is held)")
        return out

    def _homeless(self):
        head = "\n== HIS TYPED MESSAGES WITH NO HOME"
        if self.since is None:
            return [head + ": UNMEASURED: the time of the previous wake could not be read"]
        try:
            paths = window_transcripts(self.cfg, self.since, self.me.get("sessionId"),
                                       [self.old_tx or self.rec.get("tx_path")])
        except Unmeasured as e:
            return [head + ": UNMEASURED: %s" % e]
        if not paths:
            return [head + " (%s): UNMEASURED: no transcript of a %s window was written since then, so none was "
                    "read" % (self._since_text(), self.cfg.get("session_name"))]
        msgs, blind = typed_since(paths, self.since)
        out = []
        for b in blind:
            out.append("UNMEASURED transcript: %s" % b)
        if any(b.endswith(": unreadable") for b in blind) and len(blind) == len(paths):
            return [head + " (%s): UNMEASURED: no window transcript could be read" % self._since_text()] + out
        if self.ledger is None:
            return [head + " (%s): the ledger %s, so no message can be matched; his %d typed messages, word for "
                    "word:" % (self._since_text(), self.ledger_err, len(msgs))] + out + [
                        "- %s [window %s]: %s" % (pac(m["ts"]), m["window"], m["text"]) for m in msgs]
        lo = self.since - MATCH_BEFORE_S
        win = [e for e in self.ledger.events if e["_ts"] is None or e["_ts"] >= lo]
        rows = []
        for m in msgs:
            t = (m["ts"] or self.since) - MATCH_BEFORE_S
            said = [(e, norm(e["ownerSaid"])) for e in win if e.get("ownerSaid") and (e["_ts"] or 0) >= t]
            echoes = [(e, norm(" ".join(str(e.get(k) or "") for k in ECHO_FIELDS))) for e in win
                      if (e["_ts"] or 0) >= t]
            kind, ev = home_of(m["words"], said, echoes)
            if kind != "QUOTED":
                rows.append((m, kind, ev))
        out.insert(0, head + " (%s; read %d typed messages in %d window transcripts; a message has a home when an "
                   "--owner-said event from 1 h before it onward holds its words: half of its 5-word runs, or a "
                   "5+ word quote that lies inside it, or for a message under five words the same words within a "
                   "typo): %s" % (self._since_text(), len(msgs), len(paths),
                                  ("%d with no home, word for word" % len(rows)) if rows else "looked: none"))
        for m, kind, ev in rows:
            note = " (echoed, not as his words, in %s)" % (ev.get("id") or event_ref(ev)) if kind == "ECHOED" else ""
            extra = " (+ %s)" % ", ".join(m["extra"]) if m["extra"] else ""
            out.append("- %s [window %s]%s%s:\n%s" % (pac(m["ts"]), m["window"], extra, note, m["text"] or "(no text)"))
        if rows:
            out.append("Record each that states an instruction or decision on its item with `rimflow note <item> "
                       "--owner-said \"...\"`, or answer it.")
        return out

    def stamp(self):
        """Write this wake's time, so the next wake reads from here. Only a wake run by a named window stamps: a
        program or test without a session would move the next window's start past words it never showed."""
        sid = self.me.get("sessionId")
        if not sid:
            return False
        prev = SR._read_json(stamp_path(self.seat, self.root)) or {}
        since = self.since
        if prev.get("session") == sid and prev.get("since"):
            since = min(since or prev["since"], prev["since"])
        SR._write_json(stamp_path(self.seat, self.root), {
            "seat": self.seat, "at": self.now, "since": since, "session": sid,
            "tx": SR.transcript_for(self.me, self.cfg)})
        return True
