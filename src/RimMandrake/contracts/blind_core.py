"""contracts.blind_core -- the closed sets and identifier checks of the token-blind view, stdlib only.

Owner ruling 2026-10-27: only Operations is token-aware; every other role is token-blind. A blind page is built ONLY
from values that pass these checks: members of closed sets, identifiers that match a grammar AND name no account,
token, quota, cap or unit-number, hex shas, times and counts the program computed. There is no free-text field
anywhere: a reason is an enum, never prose (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF). contracts.blind wraps these in
the Pydantic models; this module is stdlib so the dispatcher's 2-minute tick (role_launch.blind_note, dispatcher
route_note) uses the SAME sets without paying for pydantic.

What an identifier check refuses (safe_ident): any part (split at _ . - / \\ space and camel case) that is an account
or model name (account_names: the built-in set plus the slot/ops rules' account keys, read at run time), a sensitive
word (token, quota, cap, budget, runway, burn, spend, usage, limit, week, pct, percent, economy, account, headroom,
allowance, pace, key, secret, bearer, cost, usd, price, bill...), a number with a unit (30k, 93pct, 5M), a digit run
of 5 or more that is not a date (YYYYMMDD) or a clock time after T (T235411), a key-shaped run (key_shaped: 16+ hex
mixing digits and letters, or 24+ characters mixing digits and both cases), and an id that withheld() would withhold
(OPS_*, OPERATIONS_*, any ACCOUNT/TOKEN/QUOTA/SPEND part). A refused value is withheld and COUNTED, never shown and
never mangled. Soft words (week, pct, share...) refuse only beside a 2+ digit part. The word list is a floor, not
the defence: no page field takes free text, so a phrasing nobody listed has nowhere to go (selftest_blind_contract's
properties plant secrets in every field). The dispatcher's blind notes are note_text / is_note_text over the closed
NOTE_ROLES / NOTE_MODES / NOTE_OUTCOMES.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

MASK = "[…]"

# ---- account and model names (the same sources blind_view always read; never hard-coded beyond the built-in set)
ACCOUNT_NAMES = frozenset({"lukas", "steven", "system", "codex", "sonnet", "opus", "haiku"})
_names_cache = []


def account_names():
    """Lower-case account and model names: ACCOUNT_NAMES plus every key of Utils/slot_rules.json and
    Utils/ops_watch_rules.json `lent_accounts` / `accounts`. Unreadable files add nothing (the built-in set stays)."""
    if not _names_cache:
        names = set(ACCOUNT_NAMES)
        utils = os.path.join(SRC, "Utils")
        for fn in ("slot_rules.json", "ops_watch_rules.json"):
            try:
                with open(os.path.join(utils, fn), encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            if not isinstance(d, dict):
                continue
            for k in ("lent_accounts", "accounts"):
                if isinstance(d.get(k), dict):
                    names |= {str(n).lower() for n in d[k]
                              if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{2,}", str(n)) and not str(n).startswith("_")}
        _names_cache.append(frozenset(names))
    return _names_cache[0]


# STRONG parts make an identifier unsafe on their own; matched as a PREFIX of the part ("tokens", "quotas")
STRONG_PREFIXES = ("account", "token", "quota", "spend", "spent", "usage", "pct", "percent", "throttl", "thrift", "headroom", "allowance", "secret", "bearer", "apikey", "credential", "passw",
                   "billing", "invoice")
STRONG_PARTS = frozenset({"acct", "tok", "toks", "kt", "sk", "pk", "rk", "usd", "eur", "gbp",
                          "dollar", "dollars", "cents"})
# SOFT parts are ordinary project words too (a wildlife cap, Burn weather, a frame budget, RM_RunwayBloom, this week's
# plan): unsafe only in an identifier that also carries a digit part, where they could state a figure.
SOFT_PREFIXES = ("week", "limit", "budget", "runway", "burn", "price", "cheap", "remaining", "economy", "economi",
                 "ratelimit")
SOFT_PARTS = frozenset({"cap", "caps", "capped", "capping", "capx", "wk", "wkly", "pace", "cost", "costs", "bill",
                        "bills", "rate", "share", "used", "left", "system", "key", "keys"})
# model names: soft (a judge family is a closed-set value on its own); every other account name is strong
MODEL_NAMES = frozenset({"opus", "sonnet", "haiku", "codex", "gpt", "gemini", "nemotron", "system"})
# an id with one of these upper-case parts is ABOUT accounts: withheld whole (blind_view.withheld's rule)
WITHHELD_ID_PREFIXES = ("OPS_", "OPERATIONS_")
WITHHELD_ID_PARTS = frozenset({"ACCOUNT", "ACCOUNTS", "TOKEN", "TOKENS", "QUOTA", "QUOTAS", "SPEND"})


def parts(word):
    """`daily_token_cap` -> [daily, token, cap]; `sessionWeekPct` -> [session, week, pct]; digit runs are parts."""
    out = []
    for p in re.split(r"[^A-Za-z0-9]+", str(word)):
        out += [q.lower() for q in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+[A-Za-z]*", p)]
    return out


def _digits_ok(part):
    """A part that starts with a digit: <= 4 digits plus an ordinary suffix (r2, 3d, 1st), a date YYYYMMDD, or a
    clock after T (handled by the caller). Never a number with a money/size unit (30k, 5m, 93pct)."""
    m = re.fullmatch(r"(\d+)([a-z]*)", part)
    if not m:
        return True
    digits, unit = m.groups()
    if unit in ("k", "m", "kt", "pct", "percent", "tok", "tokens", "usd", "bn"):
        return False
    if len(digits) <= 4:
        return True
    if len(digits) in (8, 12, 14) and unit in ("", "t", "tz", "z") and re.fullmatch(
            r"20\d\d(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(([01]\d|2[0-3])[0-5]\d([0-5]\d)?)?", digits):
        return True                                       # 20261027, 20261027T..., 202610182223, 20261018222326
    return False


_CLOCK = re.compile(r"(?<=\d{8}T)\d{4,6}(?=Z?(?![0-9]))", re.I)


def unsafe_part(p, has_digits=False):
    """-> the reason a part is unsafe, or None. has_digits: the identifier also has a 2+ digit part (soft words count)."""
    if p in account_names() and p not in MODEL_NAMES:
        return "account_name"
    if p in STRONG_PARTS or p.startswith(STRONG_PREFIXES):
        return "sensitive_word"
    if has_digits and (p in SOFT_PARTS or p in MODEL_NAMES or p.startswith(SOFT_PREFIXES)):
        return "sensitive_word_with_number"
    if p[:1].isdigit() and not _digits_ok(p):
        return "number"
    return None


def key_shaped(run):
    """An alphanumeric run shaped like a key or a digest: 16+ hex with digits and letters, or 24+ characters mixing
    digits, lower and upper case. (Ids, kinds and names are words; a run like this names a secret, never work.)"""
    if len(run) >= 16 and re.fullmatch(r"[0-9a-fA-F]+", run) and re.search(r"\d", run) and re.search(r"[a-fA-F]", run):
        return True
    return len(run) >= 24 and bool(re.search(r"\d", run) and re.search(r"[a-z]", run) and re.search(r"[A-Z]", run))


def ident_problem(s, max_len=120):
    """-> None if `s` is a safe identifier (a grammar AND no unsafe part), else a closed reason string."""
    if not isinstance(s, str) or not s:
        return "empty"
    if len(s) > max_len:
        return "too_long"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", s):
        return "grammar"
    t = _CLOCK.sub("", s)                                 # a T235411 clock after a YYYYMMDD date is a time
    for run in re.split(r"[^A-Za-z0-9]+", t):
        if key_shaped(run):
            return "key_shape"
    ps = parts(t)
    digits = any(re.match(r"\d\d", p) for p in ps)       # a 1-digit sequence suffix (THREE_WORDS_1) states nothing
    for p in ps:
        r = unsafe_part(p, digits)
        if r:
            return r
    return None


def safe_ident(s, max_len=120):
    return ident_problem(s, max_len) is None


def account_item_id(iid):
    """An id about accounts by its id alone (blind_view.withheld's id rule)."""
    u = str(iid or "").upper()
    return u.startswith(WITHHELD_ID_PREFIXES) or bool(set(re.split(r"[^A-Z]+", u)) & WITHHELD_ID_PARTS) or any(
        re.fullmatch(r"\d+K", p) for p in u.split("_"))


_ID_RE = []


def _id_re():
    if not _ID_RE:
        import sys
        if SRC not in sys.path:
            sys.path.insert(0, SRC)
        from rimflow import model                          # model.ID_RE is the ONLY statement of the id grammar
        _ID_RE.append(model.ID_RE)
    return _ID_RE[0]


def item_id_problem(iid):
    """-> None for an item id a blind page may name: the rimflow id grammar (model.ID_RE), not about accounts, and
    every part safe. Else a closed reason."""
    if not isinstance(iid, str) or not _id_re().match(iid):
        return "grammar"
    if account_item_id(iid):
        return "about_accounts"
    return ident_problem(iid, 140)


# ---- evidence paths: an allowed root, then safe segments only
REPO_NATIVE = "D:\\Luke\\dev\\RimMandrake"            # the owner's read-only mirror: how he opens a tracked file
EVIDENCE_ROOTS = {
    # repo-relative prefix (as stored) -> native prefix (as shown)
    "infrastructure/state/delegated/": REPO_NATIVE + "\\infrastructure\\state\\delegated\\",
    "/mnt/d/ClaudeWork/backups/leftovers/": "D:\\ClaudeWork\\backups\\leftovers\\",
    # the same delegated dir as the page shows it (native mirror path): the page guard re-checks rendered paths
    "/mnt/d/Luke/dev/RimMandrake/infrastructure/state/delegated/": REPO_NATIVE + "\\infrastructure\\state\\delegated\\",
}


def evidence_problem(path):
    """-> None for an evidence path a blind page may show: under one EVIDENCE_ROOTS root, 1..6 segments after it,
    each a safe identifier (dates and plain file names pass; an account name, a figure or a key-shaped word fails)."""
    if not isinstance(path, str) or not path:
        return "empty"
    p = path.replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/", p)
    if m:
        p = "/mnt/%s/%s" % (m.group(1).lower(), p[3:])
    root = next((r for r in EVIDENCE_ROOTS if p.startswith(r)), None)
    if root is None:
        return "root"
    segs = p[len(root):].split("/")
    if not 1 <= len(segs) <= 6 or any(s in ("", ".", "..") for s in segs):
        return "segments"
    for s in segs:
        r = ident_problem(s, 100)
        if r:
            return r
    return None


def evidence_native(path):
    """A checked evidence path as the owner opens it on Windows."""
    p = path.replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/", p)
    if m:
        p = "/mnt/%s/%s" % (m.group(1).lower(), p[3:])
    for r, nat in EVIDENCE_ROOTS.items():
        if p.startswith(r):
            return nat + p[len(r):].replace("/", "\\")
    raise ValueError("not an evidence path")


SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")


# ---- the dispatcher's notes for a token-blind role's ledger item (review dispatcher-full #2). One closed record:
# a known role, a known mode, a dispatcher unit name and a FIXED outcome. role_launch.blind_note and
# dispatcher.route_note both use these; contracts.blind.BlindNote is the same record as a Pydantic model.
NOTE_ROLES = ("Conductor", "Arbiter", "Auditor", "Operations", "Producer", "Innovator")
NOTE_MODES = ("quick", "run", "weekly", "economy", "event", "alarm")
NOTE_OUTCOMES = {
    "launched": "launched",
    "held_pause": "held by PAUSE, not launched",
    "held_off": "held by its off switch, not launched",
    "held_disabled": "held, the role is no longer enabled, not launched",
    "launch_failed": "launch failed, retried",
    "launch_unknown": "launch outcome unknown, the run stays tracked",
    "completed": "completed",
    "failed": "ended without a good result",
    "after_disabled": "not run, the role it runs after is not enabled",
    "schedule_unreadable": "not run, its schedule entry is unreadable",
    "events_unreadable": "not run, its event triggers are unreadable",
}


def note_problem(b):
    """-> None when `b` is a closed note record {role, outcome, mode?, unit?}, else a closed reason."""
    if not isinstance(b, dict) or set(b) - {"role", "outcome", "mode", "unit"}:
        return "shape"
    if b.get("role") not in NOTE_ROLES:
        return "role"
    if b.get("outcome") not in NOTE_OUTCOMES:
        return "outcome"
    mode, unit = b.get("mode"), b.get("unit")
    if mode is not None and mode not in NOTE_MODES:
        return "mode"
    if unit is not None and not re.match(r"rm-role-%s-[0-9]{1,12}\Z" % b["role"].lower(), str(unit)):
        return "unit"
    return None


def note_text(b):
    """Pure. -> the fixed text for a blind item, or None when the record is not closed (the note then goes to
    Operations' item, never to the blind one). "dispatcher: Conductor quick run rm-role-conductor-<epoch>:
    completed"."""
    if note_problem(b):
        return None
    mode, unit = b.get("mode"), b.get("unit")
    subject = " ".join(x for x in (b["role"], mode, "run" if (mode or unit) else None, unit) if x)
    return "dispatcher: %s: %s" % (subject, NOTE_OUTCOMES[b["outcome"]])


def is_note_text(text):
    """Is `text` EXACTLY a note note_text() renders from some closed record? (route_note's own check: a caller cannot
    hand it any other string for a blind item.) Tries every closed record the text could come from, so no parse
    ambiguity ("Conductor run ..." as mode or as the word run) can refuse a real note or pass a forged one."""
    if not isinstance(text, str) or not text.startswith("dispatcher: "):
        return False
    for out, words in NOTE_OUTCOMES.items():
        if not text.endswith(": " + words):
            continue
        toks = text[len("dispatcher: "):-len(words) - 2].split(" ")
        units = (None, toks[-1]) if toks and toks[-1].startswith("rm-role-") else (None,)
        for mode in (None,) + NOTE_MODES:
            for unit in units:
                b = {"role": toks[0], "outcome": out}
                if mode:
                    b["mode"] = mode
                if unit:
                    b["unit"] = unit
                if note_text(b) == text:
                    return True
    return False
