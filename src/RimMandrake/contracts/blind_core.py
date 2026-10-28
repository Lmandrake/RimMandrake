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

The renderer is an ALLOWLIST, not a filter (BLINDVIEW_HARDEN_SIX_LEAKS_STILL_OPEN: four review rounds each found a
new kind of route through per-field deny checks). Every page is written through a Page, whose typed emitters accept
only: template words (code constants, no digits), labels of code-defined enum domains registered by identity, ledger
item ids passing the name grammar and the page identity, registered names, numbers of a declared measure (MEASURES),
times and dates in declared formats, and opaque handles. A sha or path is never emitted: it becomes a per-page handle
E<n>, and the E<n> -> value map rides on the returned Rendered str (.handles) for the caller to store_handles() where
only Operations reads. page_gate then checks the WHOLE finished page: only PAGE_PUNCT between tokens, every token's
count within what the emitters put out, no token and no line (tokens spanning) naming an account, and an unreadable
registry refuses the page. A
refused page raises PageRefused: nothing is shown (fails closed).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

MASK = "[…]"

# ---- account and model names (the same sources blind_view always read; never hard-coded beyond the built-in set)
ACCOUNT_NAMES = frozenset({"lukas", "steven", "system", "codex", "sonnet", "opus", "haiku"})
RULE_FILES = (os.path.join(SRC, "Utils", "slot_rules.json"), os.path.join(SRC, "Utils", "ops_watch_rules.json"))
_names_cache = {}


class RegistryUnavailable(RuntimeError):
    """An account rule file could not be read: no blind page may be built (the name set would be incomplete)."""


def _stamp():
    out = []
    for fn in RULE_FILES:
        try:
            st = os.stat(fn)
        except OSError as e:
            raise RegistryUnavailable("account rules unreadable: %s" % os.path.basename(fn)) from e
        out.append((fn, st.st_mtime_ns, st.st_size))
    return tuple(out)


def _registry():
    """Lower-case account and model names: ACCOUNT_NAMES plus every key of RULE_FILES' `lent_accounts` / `accounts`.
    Re-read whenever a rule file changes (path, mtime, size); a missing or unreadable file RAISES RegistryUnavailable:
    an incomplete name set never builds a page (fail closed)."""
    stamp = _stamp()
    if stamp not in _names_cache:
        names, keys = set(ACCOUNT_NAMES), set()
        for fn in RULE_FILES:
            try:
                with open(fn, encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError) as e:
                raise RegistryUnavailable("account rules unreadable: %s" % os.path.basename(fn)) from e
            if not isinstance(d, dict):
                raise RegistryUnavailable("account rules malformed: %s" % os.path.basename(fn))
            for k in ("lent_accounts", "accounts"):
                if k not in d:
                    continue
                v = d[k]
                if not isinstance(v, dict):          # null, a list, a string: malformed, never "no accounts"
                    raise RegistryUnavailable("account rules malformed: %s %s" % (os.path.basename(fn), k))
                for n in v:              # EVERY key, canonicalised (jane.smith, a-my): no grammar filters a name out
                    if not squash(n):
                        raise RegistryUnavailable("account rules malformed: %s %s key" % (os.path.basename(fn), k))
                    names.add(squash(n))
                    keys.add(squash(n))
        _names_cache.clear()
        _names_cache[stamp] = (frozenset(names), frozenset((set(ACCOUNT_NAMES) - MODEL_NAMES) | keys))
    return _names_cache[stamp]


def account_names():
    """-> every lower-case account and model name (see _registry)."""
    return _registry()[0]


def account_keys():
    """-> the names matched AS ACCOUNTS: the built-in account names that are not model names, plus EVERY registry
    key -- a registry key is never exempted for colliding with a model name (an account called opus is an
    account; r2 HIGH). Model names alone stay legal in closed fields (judges opus+gpt)."""
    return _registry()[1]


def squash(s):
    """The canonical form an account name is matched in: lower case, letters and digits only (sTeVeN, Jane-Smith,
    JANE_SMITH all -> one form)."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def account_in(s):
    """Does `s` name an account (not a model name), whatever its case and separators? A name of 4+ characters
    matches anywhere in the squashed form (Jane_Smith, jane.smith, JANESMITHreport); a shorter one matches a run of
    consecutive parts joined (amy, a_m_y, AMy, x_Amy) -- never inside a longer word (dreamy)."""
    q = squash(s)
    names = list(account_keys())
    if any(len(n) >= 4 and n in q for n in names):
        return True
    short = {n for n in names if n and len(n) < 4}
    if not short:
        return False
    ps = parts(s)
    for i in range(len(ps)):
        j = ""
        for p in ps[i:]:
            j += p
            if len(j) > 3:
                break
            if j in short:
                return True
    return False


# STRONG parts make an identifier unsafe on their own; matched as EXACT forms (BLINDVIEW_FIX_TOKEN_WORD_FALSE_WITHHOLDS:
# a prefix match withheld ACCOUNTED, SPENT, HEADROOM in their game senses). account_item_id still withholds any id
# with an ACCOUNT/TOKEN/QUOTA/SPEND part, and headroom/spent are soft (refused beside a digit).
STRONG_PARTS = frozenset({
    "account", "accounts", "acct", "accts", "token", "tokens", "tok", "toks", "kt", "quota", "quotas", "spend",
    "spends", "spending", "usage", "usages", "pct", "percent", "percents", "percentage", "thrift", "allowance",
    "allowances", "secret", "secrets", "bearer", "billing", "invoice", "invoices", "sk", "pk", "rk", "usd", "eur",
    "gbp", "dollar", "dollars", "cents"})
STRONG_PREFIXES = ("throttl", "passw", "apikey", "credential")
# SOFT parts are ordinary project words too (a wildlife cap, Burn weather, a frame budget, RM_RunwayBloom, this week's
# plan): unsafe only in an identifier that also carries a digit part, where they could state a figure.
SOFT_PREFIXES = ("week", "limit", "budget", "runway", "burn", "price", "cheap", "remaining", "economy", "economi",
                 "ratelimit", "headroom", "spent")
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


# a real clock only (hh 00-23, mm and ss 00-59): T999999 is a figure, not a time (review night r2)
_CLOCK = re.compile(r"(?<=\d{8}T)([01]\d|2[0-3])[0-5]\d([0-5]\d)?(?=Z?(?![0-9]))", re.I)


def unsafe_part(p, has_digits=False):
    """-> the reason a part is unsafe, or None. has_digits: the identifier also has a 2+ digit part (soft words count)."""
    if p in account_keys():
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
    if account_in(s):
        return "account_name"
    ps = parts(t)
    # soft words refuse beside ANY digit part, except one trailing single digit (a sequence suffix, THREE_WORDS_1)
    digits = any(p[:1].isdigit() for p in (ps[:-1] if ps and re.fullmatch(r"\d", ps[-1]) else ps))
    for p in ps:
        r = unsafe_part(p, digits)
        if r:
            return r
    return None


NAME_MAX_PARTS = 12


def name_problem(s, max_len=64):
    """-> None for a NAME a blind page may show (a verdict subject, an evidence file's stem): the strict grammar --
    letters, digits, _ and - only; at most NAME_MAX_PARTS parts; every part letters only (<= 16) or a short number
    (<= 2 digits, at most one letter after: r2, 1b); at most 3 digits in all -- and then every ident_problem rule,
    with soft words refused beside ANY digit. A figure (9500, 1.5, 45000), a long run (a key) or a dotted value never
    passes; a name that fails is dropped and counted, never shown."""
    if not isinstance(s, str) or not s:
        return "empty"
    if len(s) > max_len:
        return "too_long"
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", s):
        return "grammar"
    ps = parts(s)
    if len(ps) > NAME_MAX_PARTS:
        return "too_many_parts"
    for p in ps:
        if not (re.fullmatch(r"[a-z]{1,16}", p) or re.fullmatch(r"\d{1,2}[a-z]?", p)):
            return "name_part"
    if sum(c.isdigit() for c in s) > 3:
        return "number"
    if account_in(s):
        return "account_name"
    digits = any(p[:1].isdigit() for p in ps)
    for p in ps:
        r = unsafe_part(p, digits)
        if r:
            return r
    return None


# ---- the NAME registry: a subject or evidence file stem is never copied from its source. What shows is a defName
# (RM_/RSW_/RUT_) declared in the repo's own XML, or a ledger id the caller knows -- issued by a trusted registry, so
# a source-provided word (swordfish, cost_nine) has nowhere to go (gpt_review_blind_harden_r1 HIGH 1).
DEF_ROOT = os.path.dirname(SRC)          # the repo's src/: every mod's Defs live under it
DEF_MIN = 500                            # fewer defNames than this = the scan could not see the repo: fail closed
_DEFNAME_RE = re.compile(rb"<defName>\s*((?:RM|RSW|RUT)_[A-Za-z0-9_]{1,80})\s*</defName>")
_defs_cache = []


def def_names():
    """-> frozenset of every RM_/RSW_/RUT_ defName in DEF_ROOT's XML, read once per process. An unreadable tree or a
    count under DEF_MIN RAISES RegistryUnavailable: a page is never built against a registry that could not see."""
    if not _defs_cache:
        names = set()

        def fail(e):
            raise RegistryUnavailable("def registry unreadable: %s" % type(e).__name__) from e

        for dp, _dns, fns in os.walk(DEF_ROOT, onerror=fail):
            for fn in fns:
                if fn.endswith(".xml"):
                    try:
                        with open(os.path.join(dp, fn), "rb") as f:
                            names.update(m.decode("ascii") for m in _DEFNAME_RE.findall(f.read()))
                    except OSError as e:
                        fail(e)
        if len(names) < DEF_MIN:
            raise RegistryUnavailable("def registry saw %d defNames (< %d)" % (len(names), DEF_MIN))
        _defs_cache.append(frozenset(names))
    return _defs_cache[0]


# a stem's suffix after its registered root and "__": closed shapes only (round r2, stage s1r2, variant b, live)
STEM_SUFFIX_RE = re.compile(r"(?:[rRsSvV]\d{1,2}){1,2}[a-d]?|[A-Da-d]|live")


def registered_name(s, known=()):
    """-> (the registered root a page may show, or None; whether anything was dropped). The root is the longest
    leading run of `s`'s underscore parts that is a def_names() defName or a `known` ledger id (and passes
    name_problem). `RM_Chittik_n` -> (RM_Chittik, True); `RM_Fountain` -> (RM_Fountain, False); `swordfish`,
    `cost_nine` -> (None, True)."""
    if not isinstance(s, str) or not s or len(s) > 120 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", s):
        return None, True
    reg = def_names()
    ps = s.split("_")
    for k in range(len(ps), 0, -1):
        cand = "_".join(ps[:k]).rstrip("_")
        if cand and (cand in reg or cand in known) and not name_problem(cand):
            return cand, cand != s
    return None, True


def stem_ok(stem):
    """Is an evidence file's stem showable: a registered defName alone, or one + "__" + a STEM_SUFFIX_RE suffix?"""
    root, trimmed = registered_name(stem)
    if root is None:
        return False
    return not trimmed or (stem.startswith(root + "__") and bool(STEM_SUFFIX_RE.fullmatch(stem[len(root) + 2:])))


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


EVIDENCE_EXTS = ("json", "md", "png", "txt", "jsonl")
NAMED_ROOTS = ("infrastructure/state/delegated/", "/mnt/d/Luke/dev/RimMandrake/infrastructure/state/delegated/")
_DATE = re.compile(r"20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])")


def _posix(path):
    p = str(path).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/", p)
    if m:
        p = "/mnt/%s/%s" % (m.group(1).lower(), p[3:])
    return p


def _file_ok(seg, hidden=()):
    stem, dot, ext = seg.rpartition(".")
    if not dot or ext not in EVIDENCE_EXTS or name_problem(stem) or not stem_ok(stem):
        return False
    q = squash(stem)
    return not any(squash(h) and squash(h) in q for h in hidden)


def evidence_problem(path):
    """-> None for an evidence path a blind page may show: under one EVIDENCE_ROOTS root, then a date directory
    (YYYY-MM-DD), then at most one file whose stem passes name_problem with an EVIDENCE_EXTS extension (only under
    the delegated roots: a leftovers path shows its date directory alone). A path ending in / is the directory."""
    if not isinstance(path, str) or not path:
        return "empty"
    p = _posix(path)
    root = next((r for r in EVIDENCE_ROOTS if p.startswith(r)), None)
    if root is None:
        return "root"
    segs = p[len(root):].split("/")
    if len(segs) == 2 and segs[1] == "":
        segs = segs[:1]
    if not 1 <= len(segs) <= 2 or not _DATE.fullmatch(segs[0]):
        return "segments"
    if len(segs) == 2 and (root not in NAMED_ROOTS or not _file_ok(segs[1])):
        return "file_name"
    if account_in(evidence_native(path)) or account_in(p):   # the path AS DISPLAYED, root included (r3 HIGH)
        return "account_name"
    return None


def evidence_view(path, hidden=()):
    """A stored evidence path -> (the path the page may show, or None; whether a value was REFUSED). The date
    directory shows whenever the path has one; the file name only under the delegated roots, and only when its stem
    passes name_problem and names no hidden id (a leftovers archive name is never shown: by design, not counted)."""
    if not isinstance(path, str) or not path:
        return None, False
    p = _posix(path)
    root = next((r for r in EVIDENCE_ROOTS if p.startswith(r)), None)
    if root is None:
        return None, True
    segs = p[len(root):].split("/")
    if not _DATE.fullmatch(segs[0]):
        return None, True
    if root in NAMED_ROOTS and len(segs) == 2 and _file_ok(segs[1], hidden):
        return root + segs[0] + "/" + segs[1], False
    # the date directory itself (no file part) hides nothing: shown, not counted refused (review night r2)
    return root + segs[0] + "/", root in NAMED_ROOTS and bool("".join(segs[1:]))


def evidence_native(path):
    """A checked evidence path as the owner opens it on Windows."""
    p = _posix(path)
    for r, nat in EVIDENCE_ROOTS.items():
        if p.startswith(r):
            return nat + p[len(r):].replace("/", "\\")
    raise ValueError("not an evidence path")


SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")
CAND_RE = re.compile(r"^[0-9a-f]{7,40}$")


def git_resolver(root):
    """-> resolve(candidates) -> {candidate: full 40-hex commit sha} for each candidate naming exactly one commit of
    the repo at `root` (git cat-file --batch-check <c>^{commit}). A sha a blind page shows is ALWAYS one this
    returned: hex shape is never proof. Git unavailable -> {} (every sha refused, never shown)."""
    import subprocess

    def resolve(cands):
        cs = [c for c in dict.fromkeys(str(c).lower() for c in cands) if CAND_RE.match(c)]
        if not cs:
            return {}
        try:
            p = subprocess.run(["git", "-C", root, "cat-file", "--batch-check"],
                               input="".join("%s^{commit}\n" % c for c in cs), capture_output=True, text=True,
                               timeout=60)
        except (OSError, subprocess.SubprocessError):
            return {}
        lines = p.stdout.splitlines()
        if p.returncode != 0 or len(lines) != len(cs):
            return {}
        out = {}
        for c, line in zip(cs, lines):
            w = line.split()
            if len(w) >= 2 and w[1] == "commit" and re.fullmatch(r"[0-9a-f]{40}", w[0]) and w[0].startswith(c):
                out[c] = w[0]
        return out
    return resolve


# ---- the ALLOWLIST renderer (BLINDVIEW_HARDEN_SIX_LEAKS_STILL_OPEN). Four review rounds each found a new KIND of
# route past "check each field against the account/figure denylist" (a path holding a name, a sha prefix equal to an
# account key, a note never checked...). So a blind page is no longer checked-then-allowed: it is WRITTEN only
# through a Page, whose emitters accept nothing but closed sets, and a value no emitter accepts cannot be rendered:
#   lit     template text: every word in the caller's declared vocabulary (code constants, no digits)
#   enum    a label of a domain the caller registered (Literal args, fixed label tables)
#   item    an id the page's identity accepts (rimflow grammar, in the ledger, not hidden)
#   name    a registered name (a repo defName or a known ledger id) the page's identity accepts
#   num     a non-negative int of a declared MEASURE (a count the program computed)
#   time    an aware-UTC datetime in a declared format; date a YYYY-MM-DD string
#   handle  a sha or a path, NEVER shown: it becomes E1, E2 ... (first appearance, one per distinct value); the
#           mapping rides on the Rendered result and is stored by the caller where Operations reads it (store_handles)
# Then text() runs the whole-page gate, which fails CLOSED: every character outside a token is declared punctuation,
# every token occurs no more often than the emitters emitted it (a token two emissions run together, or text added
# after the fact, is outside the allowlist), and, as a second layer only, no token names an account (registry
# unreadable: refused).
import datetime as _dt
from collections import Counter as _Counter

_TOK = re.compile(r"[A-Za-z0-9_]+")
PAGE_PUNCT = frozenset(" \n`*|()[],;:.-+#/=?!")
COUNT_MAX = 10 ** 6
MEASURES = frozenset({
    "records", "malformed", "withheld", "fields_withheld", "all_time", "class_records", "section_items", "row",
    "notes_total", "notes_matching", "notes_shown", "events_total", "events_shown"})
TIME_FORMATS = {"iso": "%Y-%m-%dT%H:%M:%SZ", "hm": "%m-%d %H:%MZ"}
HANDLE_KINDS = ("sha", "path")
_DATE_RE = re.compile(r"20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])")


class PageRefused(ValueError):
    """A value outside the page's closed sets reached an emitter, or the finished page failed the gate."""


class Rendered(str):
    """A finished blind page (a str) with .handles = {"E1": {"kind": "sha"|"path", "value": ...}}: the mapping a
    blind reader never sees; the caller stores it with store_handles."""
    def __new__(cls, text, handles):
        o = str.__new__(cls, text)
        o.handles = dict(handles)
        return o


def page_gate(text, allowed):
    """-> None, or the closed reason the finished page is refused. allowed: Counter of the tokens the emitters put
    out. Independent of how the page was built: a renderer bug that formats a raw value fails here."""
    if not isinstance(text, str):
        return "type"
    if any(ch not in PAGE_PUNCT for ch in _TOK.sub("", text)):
        return "character"
    toks = _Counter(_TOK.findall(text))
    if any(n > allowed.get(w, 0) for w, n in toks.items()):
        return "token outside the page allowlist"
    try:
        # per line, not per token: an account spelled by adjacent allowed tokens ("IN PROGRESS", "delegated
        # record") is still an account on the page (GPT allowlist round 2026-10-27); account_in squashes separators
        if any(account_in(w) for w in toks) or any(account_in(line) for line in text.splitlines()):
            return "account_name"
    except RegistryUnavailable:
        return "registry unavailable"
    return None


class Page:
    """One blind page being written. vocab: the template words (frozenset, code constants); enums: the registered
    domains (tuples, matched by identity); item_ok / name_ok: the page identity's predicates (None: refuse all)."""

    def __init__(self, vocab, enums=(), item_ok=None, name_ok=None):
        self._vocab, self._enums = frozenset(vocab), tuple(enums)
        if any(c.isdigit() for w in self._vocab for c in w):
            raise PageRefused("a template word carries no digit")
        self._item_ok, self._name_ok = item_ok, name_ok
        self._parts, self._allowed = [], _Counter()
        self.handles, self._handle_of = {}, {}

    def _emit(self, s):
        self._parts.append(s)
        self._allowed.update(_TOK.findall(s))

    def lit(self, s):
        if type(s) is not str or any(w not in self._vocab for w in _TOK.findall(s)) or any(
                ch not in PAGE_PUNCT for ch in _TOK.sub("", s)):
            raise PageRefused("template text outside the vocabulary")
        self._emit(s)

    def enum(self, v, domain):
        if not any(domain is d for d in self._enums) or type(v) is not str or v not in domain:
            raise PageRefused("value outside its registered domain")
        self._emit(v)

    def item(self, iid):
        if type(iid) is not str or self._item_ok is None or not self._item_ok(iid):
            raise PageRefused("item id outside the page identity")
        self._emit(iid)

    def name(self, n):
        if type(n) is not str or self._name_ok is None or not self._name_ok(n):
            raise PageRefused("name outside the registry")
        self._emit(n)

    def num(self, n, measure):
        if measure not in MEASURES or type(n) is not int or not 0 <= n <= COUNT_MAX:
            raise PageRefused("number outside the declared measures")
        self._emit(str(n))

    def time(self, t, fmt):
        if (type(t) is not _dt.datetime or fmt not in TIME_FORMATS or t.tzinfo is None
                or t.utcoffset() != _dt.timedelta(0)):
            raise PageRefused("time outside the declared formats")
        self._emit(t.strftime(TIME_FORMATS[fmt]))

    def date(self, s):
        if type(s) is not str or not _DATE_RE.fullmatch(s):
            raise PageRefused("date")
        self._emit(s)

    def handle(self, kind, value):
        """A sha or a path -> its opaque handle E<n> on this page; the value itself is never emitted."""
        if kind not in HANDLE_KINDS or type(value) is not str or not value:
            raise PageRefused("handle")
        h = self._handle_of.get((kind, value))
        if h is None:
            h = "E%d" % (len(self.handles) + 1)
            self._handle_of[(kind, value)] = h
            self.handles[h] = {"kind": kind, "value": value}
        self._emit(h)
        return h

    def text(self):
        t = "".join(self._parts)
        r = page_gate(t, self._allowed)
        if r:
            raise PageRefused("blind page gate refused the page (%s)" % r)
        return Rendered(t, self.handles)


def store_handles(text, handles, directory):
    """Write a page's handle map to <directory>/<sha256(page)[:16]>.json (atomic) for Operations / the owner, never
    beside the page a blind role reads. -> the path, or None when the page has no handle."""
    if not handles:
        return None
    import hashlib
    sha = hashlib.sha256(str(text).encode("utf-8")).hexdigest()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, sha[:16] + ".json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"page_sha256": sha, "handles": handles}, f, indent=1, sort_keys=True)
    os.replace(tmp, path)
    return path


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
NOTE_OUTCOME_TEXTS = tuple(NOTE_OUTCOMES.values())
NOTE_VOCAB = frozenset({"dispatcher", "run"})


def note_problem(b):
    """-> None when `b` is a closed note record {role, outcome, mode?, unit?}, else a closed reason."""
    if not isinstance(b, dict) or set(b) - {"role", "outcome", "mode", "unit"}:
        return "shape"
    if not isinstance(b.get("role"), str) or b["role"] not in NOTE_ROLES:
        return "role"
    if not isinstance(b.get("outcome"), str) or b["outcome"] not in NOTE_OUTCOMES:   # a list is unhashable (r3)
        return "outcome"
    mode, unit = b.get("mode"), b.get("unit")
    if mode is not None and (not isinstance(mode, str) or mode not in NOTE_MODES):
        return "mode"
    if unit is not None and not re.match(r"rm-role-%s-[0-9]{1,12}\Z" % b["role"].lower(), str(unit)):
        return "unit"
    return None


def note_text(b):
    """Pure. -> the fixed text for a blind item, or None when the record is not closed (the note then goes to
    Operations' item, never to the blind one). "dispatcher: Conductor quick run: completed". The unit is checked
    but NEVER rendered: an epoch is a free 12-digit payload (review blind 2026-10-27 #6)."""
    if note_problem(b):
        return None
    mode = b.get("mode")
    # written through the allowlist Page: its gate also refuses a token naming an account and an unreadable
    # registry (GPT r4 H2), so the stdlib route fails closed exactly like a rendered page
    p = Page(NOTE_VOCAB, (NOTE_ROLES, NOTE_MODES, NOTE_OUTCOME_TEXTS))
    try:
        p.lit("dispatcher: ")
        p.enum(b["role"], NOTE_ROLES)
        if mode:
            p.lit(" ")
            p.enum(mode, NOTE_MODES)
        if mode or b.get("unit"):
            p.lit(" run")
        p.lit(": ")
        p.enum(NOTE_OUTCOMES[b["outcome"]], NOTE_OUTCOME_TEXTS)
        return str(p.text())
    except PageRefused:
        return None


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
        for mode in (None,) + NOTE_MODES:
            for unit in (None, "rm-role-%s-1" % toks[0].lower()):
                b = {"role": toks[0], "outcome": out}
                if mode:
                    b["mode"] = mode
                if unit:
                    b["unit"] = unit
                if note_text(b) == text:
                    return True
    return False
