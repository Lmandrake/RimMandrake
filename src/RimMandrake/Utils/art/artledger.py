#!/usr/bin/env python3
"""artledger.py — the ONE reader/writer of the art ledger (ART_VERSION_WRANGLING_1).

Design: design/RimMandrake/art_ledger_design_2026-10-04.md. This module is the library;
`art.py` is the CLI over it. Nothing else parses the shards.

Three stores, kept apart on purpose:
  * events  — infrastructure/state/art/events/<SEAT>.jsonl, git-tracked, append-only,
              merge=union (like the rimflow ledger). Facts about art; no pixels.
  * bytes   — the content-addressed art store, D:\\Luke\\dev\\_artstore\\<sha[:2]>\\<sha>.png,
              outside git. Every displaced or shown picture lands here BEFORE anything
              overwrites it. Writes are copy -> fsync -> re-hash -> rename.
  * index   — infrastructure/state/art/index.json, a gitignored projection, rebuilt on read.

Identity: a VARIANT is one image, keyed by sha256 of its PNG bytes. A RESOURCE is the
texPath stem a file serves (`swanimals/Nuna/Nuna_f`) plus a facing. Roles come from the
def field the texPath sits in (`dessicatedBodyGraphicData` -> dessicated), never from the
filename — except the `m` mask suffix, which IS a filename convention of the engine.

Owner rulings 2026-10-04 that this code enforces (item notes):
  * replaced art goes to the store by fingerprint before any overwrite (install archives first);
  * the owner can simply DELETE an erroneous render: `purge` removes its bytes from the store
    and every later sheet filters it out (a `purge` event; registration skips purged shas);
  * only an owner `keep` with plumbing/typed provenance PROTECTS; flawed-sheet, prefill and
    legacy-unresolved rulings are shown but protect nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STORE_DEFAULT = Path("/mnt/d/Luke/dev/_artstore")


def ledger_dir() -> Path:
    return Path(os.environ.get("ART_LEDGER_DIR") or REPO_ROOT / "infrastructure" / "state" / "art")


def store_dir() -> Path:
    return Path(os.environ.get("ARTSTORE") or STORE_DEFAULT)


def src_root() -> Path:
    return Path(os.environ.get("ART_SRC_ROOT") or REPO_ROOT / "src")


class NoSeat(SystemExit):
    """Raised at WRITE time when nothing names the running seat. Reads never need one."""


def seat() -> str:
    """-> the shard this process appends to: RIMFLOW_SEAT, ART_SEAT, AGENT_SEAT, then this
    session's .claude/session_roles/$CLAUDE_SESSION_ID — rimflow's order. Refuses rather
    than guesses (ART_LEDGER_SEAT_DEFAULT_1): the old silent "BENCH" fallback ignored
    AGENT_SEAT, so FOUNDRY's salvage wave-2 events landed in BENCH.jsonl, permanently."""
    for val in (os.environ.get("RIMFLOW_SEAT"), os.environ.get("ART_SEAT"),
                os.environ.get("AGENT_SEAT")):
        if val and val.strip():
            v = val.strip().upper()
            if not re.fullmatch(r"[A-Z0-9_]+", v):
                raise NoSeat(f"art ledger: seat {val!r} is not a shard name")
            return v
    sid = os.environ.get("CLAUDE_SESSION_ID")
    if sid:
        try:
            words = (REPO_ROOT / ".claude" / "session_roles" / sid).read_text(
                encoding="utf-8").replace("-", " ").split()
        except OSError:
            words = []
        for w in words:
            if w.upper() in ("BENCH", "FOUNDRY", "OWNER", "DECIDE", "BUILD", "CHECK", "REP"):
                return w.upper()
    raise NoSeat("REFUSED: art ledger cannot tell which seat is writing, and will not guess.\n"
                 "  Set RIMFLOW_SEAT=<SEAT> (or ART_SEAT / AGENT_SEAT) and re-run.")


# ───────────────────────────────────────────────────────────────── hashing ──

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dhash(png_bytes: bytes, size: int = 16) -> tuple[str, int, int]:
    """16x16 difference hash over alpha-composited luminance -> (hex, w, h).
    A comparison aid for the sheet ONLY; never authorises anything (GPT #3)."""
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(png_bytes))
    w, h = im.size
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (128, 128, 128, 255))
    bg.alpha_composite(im)
    g = bg.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for y in range(size):
        row = px[y * (size + 1):(y + 1) * (size + 1)]
        for x in range(size):
            bits = (bits << 1) | (1 if row[x] > row[x + 1] else 0)
    return f"{bits:0{size * size // 4}x}", w, h


def hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")


# ─────────────────────────────────────────────────────────────── the store ──

def store_path(sha: str) -> Path:
    return store_dir() / sha[:2] / f"{sha}.png"


def store_has(sha: str) -> bool:
    return store_path(sha).is_file()


def store_put_bytes(b: bytes, sha: str | None = None) -> str:
    """Copy bytes into the store, verified. Idempotent. Returns the sha."""
    sha = sha or sha256_bytes(b)
    dst = store_path(sha)
    if dst.is_file():
        return sha
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dst.parent, prefix=".put-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(b)
            fh.flush()
            os.fsync(fh.fileno())
        if sha256_file(Path(tmp)) != sha:
            raise IOError(f"store write of {sha} re-hashed differently — refusing to record it")
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return sha


def store_put_file(p: Path) -> str:
    return store_put_bytes(Path(p).read_bytes())


def store_get(sha: str) -> bytes:
    return store_path(sha).read_bytes()


# ──────────────────────────────────────────────────────────────── events ──

def shard_path(s: str | None = None) -> Path:
    return ledger_dir() / "events" / f"{s or seat()}.jsonl"


def det_id(*parts) -> str:
    """Deterministic event id: a re-run or a union-merge duplicate is idempotent."""
    return hashlib.sha1(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:20]


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def read_events() -> list[dict]:
    out, seen = [], set()
    d = ledger_dir() / "events"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError as exc:
                    raise ValueError(f"{f}:{n}: unparseable ledger line ({exc})") from None
                if ev.get("id") in seen:
                    continue
                seen.add(ev.get("id"))
                out.append(ev)
    return out


class Writer:
    """Buffered appender that skips ids already present (idempotent backfill)."""

    def __init__(self, known_ids: set | None = None):
        self.known = known_ids if known_ids is not None else {e["id"] for e in read_events()}
        self.buf: list[dict] = []

    def add(self, ev: dict) -> bool:
        ev.setdefault("id", uuid.uuid4().hex[:20])
        if ev["id"] in self.known:
            return False
        ev.setdefault("ts", now())
        ev.setdefault("seat", seat())
        self.known.add(ev["id"])
        self.buf.append(ev)
        if len(self.buf) >= 500:
            self.flush()
        return True

    def flush(self):
        if not self.buf:
            return
        p = shard_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as fh:
            for ev in self.buf:
                fh.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
        self.buf.clear()


def append(ev: dict) -> dict:
    w = Writer()
    w.add(ev)
    w.flush()
    return ev


# ─────────────────────────────────────────────────────── resource naming ──

FACING_RE = re.compile(r"^(?P<stem>.+?)_(?P<facing>north|east|south|west)(?P<mask>m?)$")


def parse_texfile(rel: str) -> dict:
    """'swanimals/Nuna/Nuna_f_eastm.png' -> {res, facing, mask}. rel is under Textures/."""
    rel = rel.replace("\\", "/")
    base = rel[:-4] if rel.lower().endswith(".png") else rel
    m = FACING_RE.match(base)
    if m:
        return {"res": m["stem"], "facing": m["facing"], "mask": bool(m["mask"])}
    return {"res": base, "facing": "single", "mask": False}


def split_texture_path(path: str) -> tuple[str, str] | None:
    """'src/RimStarWars/SWBestiary/Textures/x/y.png' -> ('src/RimStarWars/SWBestiary', 'x/y.png')."""
    p = path.replace("\\", "/")
    i = p.find("/Textures/")
    if i < 0:
        return None
    return p[:i], p[i + len("/Textures/"):]


# ────────────────────────────────────────────────── slots from our defs ──

GRAPHIC_ROLE = {
    "bodyGraphicData": "body", "femaleGraphicData": "body",
    "dessicatedBodyGraphicData": "dessicated", "rottingGraphicData": "dessicated",
    "swimmingGraphicData": "swimming", "graphicData": "body",
    "leaflessGraphicData": "plant_leafless", "immatureGraphicData": "plant_immature",
    "wornGraphicPath": "apparel_worn",
}


def scan_def_slots(root: Path | None = None) -> dict:
    """texPath -> list of {subject, role, field, file}. Parsed XML, never text-matched."""
    root = root or src_root()
    out = defaultdict(list)
    for f in root.rglob("*.xml"):
        if "/Defs/" not in str(f) and "/Patches/" not in str(f):
            continue
        try:
            tree = ET.parse(f)
        except (ET.ParseError, OSError):
            continue
        for d in tree.getroot().iter():
            dn = d.find("defName")
            if dn is None or not (dn.text or "").strip():
                continue
            name = dn.text.strip()
            for parent in d.iter():
                for ch in list(parent):
                    tag = ch.tag if isinstance(ch.tag, str) else ""
                    if tag in GRAPHIC_ROLE:
                        tp = ch.find("texPath") if tag != "wornGraphicPath" else ch
                        if tp is not None and (tp.text or "").strip():
                            role = GRAPHIC_ROLE[tag]
                            sub = name + ("#f" if tag == "femaleGraphicData" else "")
                            out[tp.text.strip()].append({"subject": sub, "role": role,
                                                         "field": tag, "file": str(f.relative_to(root))})
                    elif tag in ("flyingAnimationFramePathPrefix", "flyingAnimationFramePathPrefixFemale"):
                        if (ch.text or "").strip():
                            out[ch.text.strip()].append({"subject": name, "role": "flying",
                                                         "field": tag, "file": str(f.relative_to(root))})
    return dict(out)


def role_of(res: str, mask: bool, slots: dict) -> str:
    if mask:
        return "mask"
    for s in slots.get(res, []):
        if s["role"] != "body":
            return s["role"]
    if slots.get(res):
        return "body"
    low = res.lower()
    if "dessicated" in low or "desiccated" in low or low.endswith("_corpse"):
        return "dessicated"
    return "body"


# ─────────────────────────────────────────────────────────── projection ──

TRUST_PROTECTS = {"ruled"}
KEEP_VERBS = {"keep", "approve", "right", "ok", "current", "yes", "better", "good", "works"}
REDO_VERBS = {"redo", "redraw", "regen", "revise", "improve", "rerender", "resize"}
REJECT_VERBS = {"cut", "reject", "drop", "no", "mud"}


def normalise_verdict(raw: str) -> str:
    r = (raw or "").strip().lower()
    if r in KEEP_VERBS:
        return "keep"
    if r in REDO_VERBS:
        return "redo"
    if r == "replace":
        return "replace-donor"      # NOT reject: means "replace the donor with our own"
    if r in REJECT_VERBS:
        return "reject"
    if r in ("hold", "defer", "pending"):
        return "hold"
    if r.startswith("col:"):
        return "keep"
    if r == "purge":
        return "purge"
    return r or ""


class Index:
    """Folded view of every shard. Cheap enough to rebuild on each CLI call."""

    def __init__(self, events: list[dict] | None = None):
        self.events = read_events() if events is None else events
        self.variants = defaultdict(list)      # sha -> [variant events]
        self.by_res = defaultdict(set)         # res -> {sha}
        self.rulings = []                      # ruling events
        self.rulings_by_sha = defaultdict(list)
        self.live = {}                         # (mod, rel) -> live event (latest by causal prev)
        self.purged = {}                       # sha -> purge event
        self.rejected = defaultdict(list)      # sha -> [rejected events: bytes an owner redo/reject named]
        self.snapshots = []
        for ev in self.events:
            self._take(ev)

    def add(self, ev: dict):
        """Fold one more event in (an install's own appends, without re-reading the shards)."""
        self.events.append(ev)
        self._take(ev)

    def _take(self, ev: dict):
        t = ev.get("type")
        if t == "variant":
            self.variants[ev["sha"]].append(ev)
            if ev.get("res"):
                self.by_res[ev["res"]].add(ev["sha"])
        elif t == "ruling":
            self.rulings.append(ev)
            tgt = ev.get("target") or {}
            for s in tgt.get("shas", []) + ([tgt["sha"]] if tgt.get("sha") else []):
                self.rulings_by_sha[s].append(ev)
        elif t == "live":
            self._fold_live(ev)
        elif t == "purge":
            self.purged[ev["sha"]] = ev
        elif t == "rejected":
            self.rejected[ev["sha"]].append(ev)
        elif t == "snapshot":
            self.snapshots.append(ev)

    def _fold_live(self, ev):
        key = (ev["mod"], ev["rel"])
        cur = self.live.get(key)
        if cur is None or ev.get("prev") == cur.get("sha") or ev.get("ts", "") >= cur.get("ts", ""):
            if ev.get("sha") is None:           # retire: the file was archived and removed
                self.live.pop(key, None)
            else:
                self.live[key] = ev

    def protected(self, sha: str) -> list[dict]:
        """Owner keeps with real provenance that name this sha and are not released."""
        keeps = [r for r in self.rulings_by_sha.get(sha, [])
                 if r.get("verdict") == "keep" and r.get("by") == "owner"
                 and r.get("trust") in TRUST_PROTECTS]
        released = {r.get("releases") for r in self.rulings if r.get("releases")}
        return [k for k in keeps if k["id"] not in released]

    def is_purged(self, sha: str) -> bool:
        return sha in self.purged

    def subject_rulings(self, keys: set[str]) -> list[dict]:
        """Rulings on these subjects, following renames: an alias and its canonical key share history."""
        keys = {canonical_subject(k) for k in keys}
        return [r for r in self.rulings if canonical_subject(r.get("subject_key") or "") in keys]

    def rejection(self, sha: str) -> list[dict]:
        """The owner redo/reject verdicts that named these very bytes, unless he has since kept them."""
        if self.protected(sha):
            return []
        return self.rejected.get(sha, [])

    def live_anywhere(self, sha: str) -> list[str]:
        return [f"{m}/Textures/{r}" for (m, r), ev in self.live.items() if ev.get("sha") == sha]


_IDX: dict = {"sig": None, "idx": None}


def _shard_sig() -> tuple:
    d = ledger_dir() / "events"
    if not d.is_dir():
        return (str(d),)
    return (str(d),) + tuple((f.name, f.stat().st_size, f.stat().st_mtime_ns) for f in sorted(d.glob("*.jsonl")))


def cached_index() -> "Index":
    """An Index reused across installs in one process (a port script installs hundreds of
    files); rebuilt whenever a shard changed under it (another writer, another ledger dir)."""
    s = _shard_sig()
    if _IDX["sig"] != s or _IDX["idx"] is None:
        _IDX.update(sig=s, idx=Index())
    return _IDX["idx"]


def _absorb(evs: list[dict]):
    """Fold this process's own appends into the cached Index and re-sign it."""
    if _IDX["idx"] is None:
        return
    for ev in evs:
        _IDX["idx"].add(ev)
    _IDX["sig"] = _shard_sig()


def subject_key(raw: str) -> str:
    """Normalise a sheet row key to a creature key: 'A_Nuna'/'RSW_Nuna'/'nuna_f' -> 'nuna'."""
    k = raw.strip()
    k = re.sub(r"^(A_|RSW_|RM_|RUT_|BMT_|AA_|ZB_)", "", k, flags=re.I)
    k = re.sub(r"(_[fm]|_v\d+|#.*)$", "", k, flags=re.I)
    return k.lower()


# A def rename or a new def for the same creature gets a new subject key ('ikee' -> 'contagionikee'). The
# alias file maps the new key to the creature's canonical one, so its rulings and rejections follow it.
ALIASES_FILE = "subject_aliases.json"
_ALIASES: dict = {"sig": None, "map": {}}


def subject_aliases() -> dict:
    p = ledger_dir() / ALIASES_FILE
    try:
        sig = (str(p), p.stat().st_mtime_ns)
    except OSError:
        return {}
    if _ALIASES["sig"] != sig:
        raw = json.loads(p.read_text()).get("aliases", {})
        _ALIASES.update(sig=sig, map={k.lower(): v.lower() for k, v in raw.items()})
    return _ALIASES["map"]


def canonical_subject(key: str) -> str:
    k, seen, al = (key or "").lower(), set(), subject_aliases()
    while k in al and k not in seen:
        seen.add(k)
        k = al[k]
    return k


def subject_of_rel(rel: str) -> str:
    """The creature a Textures path belongs to, by its folder: '.../RM_Ikee/RM_Ikee_east.png' -> 'ikee'."""
    parent = Path(rel).parent.name or Path(rel).stem
    return canonical_subject(subject_key(parent))


def rejection_refusal(idx: "Index", rel: str, sha: str) -> str | None:
    """Why a MECHANICAL install of `sha` at `rel` would bring back a picture he rejected, else None.
    reject: never, anywhere. redo: only as the same creature's current picture being moved — a redo'd
    picture that is live nowhere is being resurrected, and one copied to another creature is spreading."""
    rej = idx.rejection(sha)
    if not rej:
        return None
    r = rej[-1]
    said = f" (he said: {r.get('said')!r})" if r.get("said") else ""
    if any(normalise_verdict(x.get("verdict")) == "reject" for x in rej):
        return f"{sha[:12]} was REJECTED by the owner on {Path(r.get('via') or '').name}{said}"
    subjects = {canonical_subject(x.get("subject_key") or "") for x in rej}
    if not idx.live_anywhere(sha):
        return (f"{sha[:12]} is a picture the owner sent back for redo on {Path(r.get('via') or '').name}{said}, "
                f"and it is live nowhere — installing it resurrects it")
    tgt = subject_of_rel(rel)
    if tgt not in subjects:
        return (f"{sha[:12]} was sent back for redo as {'/'.join(sorted(subjects))}{said}; copying it onto "
                f"{tgt} spreads a rejected picture (if {tgt} is a rename, add it to {ALIASES_FILE})")
    return None


# ─────────────────────────────────────────────────────────── installing ──

class Refused(Exception):
    pass


MECHANICAL_REASONS = ("artpipe-collect", "script:")   # a --reason must start with one of these


def is_mechanical_reason(reason: str | None) -> bool:
    if not reason:
        return False
    for p in MECHANICAL_REASONS:
        if reason == p and not p.endswith(":"):
            return True
        if p.endswith(":") and reason.startswith(p) and len(reason) > len(p):
            return True
    return False


PLACEHOLDER_RULE = ('owner, 2026-10-07 22:33 PDT: "make sure that at no time can geometric placeholder art ever '
                    'remain a viable Variant or selection, ok?"')


def placeholder_refusal(rel: str, data: bytes) -> str:
    """'' when `data` may be installed at `rel`; else why not. A geometric placeholder (placeholder_detect) is never
    installed by ANY authorisation — not his keep, not his words, not a mechanical tag. Masks and UI chrome are
    flat by design and are not judged."""
    r = rel.replace("\\", "/")
    if r.startswith("UI/") or parse_texfile(r).get("mask"):
        return ""
    try:
        import placeholder_detect as PD
        why = PD.placeholder_reason(data)
    except Exception as e:                             # noqa: BLE001
        return f"UNMEASURED: placeholder check could not read the picture ({type(e).__name__}: {e}) — not installed"
    return f"{rel}: {why} — a placeholder is never installed ({PLACEHOLDER_RULE})" if why else ""


def install(mod: str, rel: str, sha: str, *, ruling_id: str | None = None,
            owner_said: str | None = None, reason: str | None = None,
            provenance: dict | None = None, dry_run: bool = False) -> dict:
    """The only sanctioned writer into src/**/Textures. Ledger-checked; saves the old
    picture into the store FIRST; atomic write; appends a `live` event.

    Authorization, one of:
      * ruling_id: an owner keep (trust=ruled) naming the incoming sha;
      * owner_said: his typed words, recorded as an owner keep ruling;
      * reason: a mechanical tag (`artpipe-collect`, `script:<repo path>`) for a writer
        installing without an owner decision. REFUSED when the displaced picture is
        protected by an owner keep — only his selection may replace a kept picture.
    """
    idx = cached_index()
    if idx.is_purged(sha):
        raise Refused(f"{sha[:12]} was purged by the owner — it cannot be installed")
    if not store_has(sha):
        raise Refused(f"{sha[:12]} is not in the art store ({store_dir()}) — put it there first")
    if "/Textures/" in "/" + rel.replace("\\", "/") or rel.startswith("/"):
        raise Refused(f"rel must be the path UNDER Textures/, got {rel}")
    why_ph = placeholder_refusal(rel, store_get(sha))
    if why_ph:
        raise Refused(why_ph)
    target = src_root().parent / mod / "Textures" / rel if not Path(mod).is_absolute() else Path(mod) / "Textures" / rel
    ruling = None
    if ruling_id:
        ruling = next((r for r in idx.rulings if r["id"] == ruling_id), None)
        if not ruling:
            raise Refused(f"no ruling {ruling_id} in the ledger")
        tg = ruling.get("target") or {}
        if sha not in (tg.get("shas") or []) + ([tg["sha"]] if tg.get("sha") else []):
            raise Refused(f"ruling {ruling_id} does not name {sha[:12]}")
        if ruling.get("by") != "owner" or ruling.get("trust") not in TRUST_PROTECTS \
                or normalise_verdict(ruling.get("verdict")) != "keep":
            raise Refused(f"ruling {ruling_id} is {ruling.get('by')}/{ruling.get('trust')}/"
                          f"{ruling.get('verdict')} — only an owner keep with real provenance authorises")
    elif owner_said:
        pass
    elif reason:
        if not is_mechanical_reason(reason):
            raise Refused(f"reason {reason!r} is not a mechanical tag (allowed: "
                          f"{', '.join(MECHANICAL_REASONS)}<name>)")
        why = rejection_refusal(idx, rel, sha)
        if why:
            raise Refused(why + " — only his ruling can bring it back (--ruling <keep id> or --owner-said)")
    else:
        raise Refused("install needs an owner keep ruling id, the owner's typed words, "
                      "or a mechanical reason (artpipe-collect | script:<path>)")
    old_sha = sha256_file(target) if target.is_file() else None
    if old_sha == sha:
        return {"status": "already-live", "path": str(target), "new": sha}
    old_protected = bool(old_sha and idx.protected(old_sha))
    if old_protected and not (ruling or owner_said):
        raise Refused(f"{target} holds {old_sha[:12]}, an owner-KEPT picture — a mechanical "
                      f"install ({reason}) may not displace it; it needs his ruling "
                      f"(art.py install {mod} {rel} <sha> --ruling <keep id>)")
    plan = {"status": "planned", "path": str(target), "old": old_sha, "new": sha,
            "old_protected": old_protected}
    if dry_run:
        return plan
    w = Writer({e["id"] for e in idx.events})
    if sha not in idx.variants:
        pt = parse_texfile(rel)
        try:
            ph, wd, ht = dhash(store_get(sha))
        except Exception:
            ph, wd, ht = "", 0, 0
        w.add({"type": "variant", "id": det_id("variant", "install", sha, f"{mod}/Textures/{rel}"),
               "sha": sha, "ph": ph, "w": wd, "h": ht, "kind": (provenance or {}).get("kind", "install"),
               "loc": f"{mod}/Textures/{rel}", "date": time.strftime("%Y-%m-%d"), "mod": str(mod),
               "res": pt["res"], "facing": pt["facing"], "mask": pt["mask"],
               "provenance": provenance or {}, "subjects": []})
    if owner_said:
        ruling = {"id": det_id("ruling-cli", sha, owner_said), "type": "ruling",
                  "target": {"sha": sha}, "verdict": "keep", "by": "owner", "said": owner_said,
                  "via": "art install (owner words)", "trust": "ruled", "subject_key": ""}
        w.add(ruling)
    if old_sha:
        store_put_file(target)                       # archive BEFORE writing
        if not store_has(old_sha):
            raise Refused("archive of the displaced picture did not verify — nothing written")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".art-install-")
    with os.fdopen(fd, "wb") as fh:
        fh.write(store_get(sha))
    os.replace(tmp, target)
    live = {"type": "live", "mod": str(Path(mod)), "rel": rel, "sha": sha, "prev": old_sha}
    if ruling:
        live.update(ruling_id=ruling["id"], reason="install")
    else:
        live.update(reason=reason)
    w.add(live)
    added = list(w.buf)
    w.flush()
    _absorb(added)
    plan["status"] = "installed"
    return plan


def locate(dest) -> tuple[str, str]:
    """A path (absolute, or relative to the clone root) to a file under some mod's
    Textures/ -> (mod, rel) as the ledger keys them ('src/X/Mod', 'a/b.png')."""
    root = src_root().parent.resolve()
    p = Path(dest)
    p = (p if p.is_absolute() else root / p).resolve()
    try:
        relp = p.relative_to(root).as_posix()
    except ValueError:
        raise Refused(f"{dest} is not inside this clone ({root})") from None
    sp = split_texture_path(relp)
    if not sp or not relp.startswith("src/"):
        raise Refused(f"{dest} is not under src/**/Textures/")
    return sp


def install_bytes(dest, data: bytes, *, reason: str, provenance: dict | None = None,
                  dry_run: bool = False) -> dict:
    """The writer-side entry every art script calls INSTEAD of Image.save / shutil.copy
    into Textures: put `data` in the store, then `install` it at `dest` on a mechanical
    reason (refused over an owner-kept picture)."""
    mod, rel = locate(dest)
    if dry_run:
        sha = sha256_bytes(data)
        if not store_has(sha):
            return {"status": "planned", "path": str(dest), "new": sha}
    else:
        sha = store_put_bytes(data)
    return install(mod, rel, sha, reason=reason, provenance=provenance, dry_run=dry_run)


def install_file(dest, src_png, **kw) -> dict:
    return install_bytes(dest, Path(src_png).read_bytes(), **kw)


def install_image(dest, img, **kw) -> dict:
    """PIL Image -> PNG bytes -> install_bytes."""
    import io
    b = io.BytesIO()
    img.save(b, "PNG")
    return install_bytes(dest, b.getvalue(), **kw)


def retire(dest, *, reason: str | None = None, owner_said: str | None = None) -> dict:
    """Remove a Textures file through the ledger: archive, delete, `live` with sha None."""
    mod, rel = locate(dest)
    target = src_root().parent / mod / "Textures" / rel
    if not target.is_file():
        return {"status": "absent", "path": str(target)}
    idx = cached_index()
    old = sha256_file(target)
    if idx.protected(old) and not owner_said:
        raise Refused(f"{target} is owner-kept ({old[:12]}) — retiring it needs his words")
    if not (owner_said or is_mechanical_reason(reason)):
        raise Refused("retire needs the owner's words or a mechanical reason")
    store_put_file(target)
    if not store_has(old):
        raise Refused("archive did not verify — nothing removed")
    target.unlink()
    ev = {"type": "live", "mod": mod, "rel": rel, "sha": None, "prev": old, "reason": reason or "retire"}
    if owner_said:
        ev["said"] = owner_said
    append(ev)
    _absorb([ev])
    return {"status": "retired", "path": str(target), "old": old}


# ─────────────────────────────────────────────────────────────── purging ──

def purge(sha: str, *, owner_said: str, via: str = "art purge", release_keep: bool = False,
          live_paths: list[str] | None = None) -> dict:
    """Reject+purge: the owner deletes an erroneous render so it stops polluting option
    space. Removes the bytes from the store and records a `purge` event; every sheet and
    every later registration skips the sha. Refuses a picture that is live in a mod
    (install something else first) or one he kept, unless release_keep."""
    if not owner_said or not owner_said.strip():
        raise Refused("purge is the owner's act — needs his typed words or a sheet ruling")
    idx = Index()
    if live_paths is None:
        live_paths = [f"{m}/Textures/{r}" for (m, r), ev in idx.live.items() if ev.get("sha") == sha]
    if live_paths:
        kept = [k for k in idx.protected(sha) if k.get("subject_key")]
        under = f"; he KEPT these bytes as {kept[0]['subject_key']} ({Path(kept[0].get('via') or '').name})" if kept else ""
        raise Refused(f"{sha[:12]} is live at {len(live_paths)} slot(s): {', '.join(live_paths[:4])}"
                      f"{' …' if len(live_paths) > 4 else ''}{under} — install a replacement first")
    prot = idx.protected(sha)
    w = Writer({e["id"] for e in idx.events})
    if prot and not release_keep:
        raise Refused(f"{sha[:12]} carries an owner keep ({prot[0]['id']}) — pass release_keep")
    for k in prot:
        w.add({"type": "ruling", "id": det_id("release", k["id"], sha), "target": {"sha": sha},
               "verdict": "release", "releases": k["id"], "by": "owner", "said": owner_said,
               "trust": "ruled", "via": via})
    removed = False
    p = store_path(sha)
    if p.is_file():
        p.unlink()
        removed = True
    w.add({"type": "purge", "id": det_id("purge", sha), "sha": sha, "by": "owner",
           "said": owner_said, "via": via, "bytes_removed": removed})
    w.flush()
    return {"sha": sha, "bytes_removed": removed}


# ─────────────────────────────────────────── sheet snapshots: stable letters ──
# A sheet's decisions name COLUMN LETTERS; the snapshot maps row -> letter -> {facing: sha}. A rebuild keeps
# every letter on the same set (art_sheet._assign_letters), so what must match between the snapshot the owner
# ruled on and today's is only the letters his decisions actually use.

SHEET_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def snapshot_by_id(snap_path: Path, snapshot_id: str | None) -> dict | None:
    """The snapshot with this snapshotId: the file on disk, else the newest git revision of it that has it."""
    import subprocess
    snap_path = Path(snap_path)
    if not snapshot_id:
        return None
    if snap_path.is_file():
        cur = json.loads(snap_path.read_text())
        if cur.get("snapshotId") == snapshot_id:
            return cur
    try:
        rel = snap_path.resolve().relative_to(REPO_ROOT).as_posix()
        revs = subprocess.run(["git", "-C", str(REPO_ROOT), "log", "--format=%H", "--", rel],
                              capture_output=True, text=True, check=True).stdout.split()
    except (ValueError, subprocess.CalledProcessError, OSError):
        return None
    for h in revs:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{h}:{rel}"], capture_output=True, text=True)
        if r.returncode:
            continue
        try:
            s = json.loads(r.stdout)
        except ValueError:
            continue
        if s.get("snapshotId") == snapshot_id:
            return s
    return None


def decision_letters(v: dict) -> set[str]:
    """The column letters one row of a decisions file refers to: its decision, extra-graphic picks, variants."""
    if not isinstance(v, dict):
        return set()
    out = {(v.get("decision") or "").strip()} | set((v.get("picks") or {}).values()) | set(v.get("variants") or [])
    return {x for x in out if isinstance(x, str) and len(x) == 1 and x in SHEET_LETTERS}


def letter_mismatches(decisions: dict, ruled: dict, now: dict) -> list[tuple[str, str]]:
    """(row, letter) pairs whose set differs between the RULED snapshot and NOW, over used letters only.
    A letter the ruled snapshot never had is not checked (nothing was ruled through it)."""
    bad = []
    for row, v in sorted(((decisions or {}).get("decisions") or {}).items()):
        rc = ((ruled.get("rows") or {}).get(row) or {}).get("columns") or {}
        nc = ((now.get("rows") or {}).get(row) or {}).get("columns") or {}
        for l in sorted(decision_letters(v)):
            if l in rc and rc[l] != nc.get(l):
                bad.append((row, l))
    return bad
