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


def seat() -> str:
    return os.environ.get("RIMFLOW_SEAT") or os.environ.get("ART_SEAT") or "BENCH"


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
        self.snapshots = []
        for ev in self.events:
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
            elif t == "snapshot":
                self.snapshots.append(ev)

    def _fold_live(self, ev):
        key = (ev["mod"], ev["rel"])
        cur = self.live.get(key)
        if cur is None or ev.get("prev") == cur.get("sha") or ev.get("ts", "") >= cur.get("ts", ""):
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
        keys = {k.lower() for k in keys}
        return [r for r in self.rulings if (r.get("subject_key") or "").lower() in keys]


def subject_key(raw: str) -> str:
    """Normalise a sheet row key to a creature key: 'A_Nuna'/'RSW_Nuna'/'nuna_f' -> 'nuna'."""
    k = raw.strip()
    k = re.sub(r"^(A_|RSW_|RM_|RUT_|BMT_|AA_|ZB_)", "", k, flags=re.I)
    k = re.sub(r"(_[fm]|_v\d+|#.*)$", "", k, flags=re.I)
    return k.lower()


# ─────────────────────────────────────────────────────────── installing ──

class Refused(Exception):
    pass


def install(mod: str, rel: str, sha: str, *, ruling_id: str | None = None,
            owner_said: str | None = None, dry_run: bool = False) -> dict:
    """The only sanctioned writer into src/**/Textures. Ledger-checked; saves the old
    picture into the store FIRST; atomic write; appends a `live` event.

    Authorization: the incoming sha needs an owner ruling (trust=ruled) naming it, given
    as --ruling <id>, or the owner's typed words (--owner-said), which are recorded as a
    ruling. If the displaced sha is protected, the incoming one must be the owner's
    selection — always true when authorised as above, so the rule reduces to: never
    without an owner ruling for the incoming bytes.
    """
    idx = Index()
    if idx.is_purged(sha):
        raise Refused(f"{sha[:12]} was purged by the owner — it cannot be installed")
    if not store_has(sha):
        raise Refused(f"{sha[:12]} is not in the art store ({store_dir()}) — put it there first")
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
    elif not owner_said:
        raise Refused("install needs --ruling <owner keep id> or --owner-said \"<his typed words>\"")
    old_sha = sha256_file(target) if target.is_file() else None
    if old_sha == sha:
        return {"status": "already-live", "path": str(target)}
    plan = {"status": "planned", "path": str(target), "old": old_sha, "new": sha,
            "old_protected": bool(old_sha and idx.protected(old_sha))}
    if dry_run:
        return plan
    w = Writer({e["id"] for e in idx.events})
    if owner_said:
        ruling = {"id": det_id("ruling-cli", sha, owner_said), "type": "ruling",
                  "target": {"sha": sha}, "verdict": "keep", "by": "owner", "said": owner_said,
                  "via": "art install --owner-said", "trust": "ruled", "subject_key": ""}
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
    rel_mod = str(Path(mod))
    w.add({"type": "live", "mod": rel_mod, "rel": rel, "sha": sha, "prev": old_sha,
           "ruling_id": ruling["id"], "reason": "install"})
    w.flush()
    plan["status"] = "installed"
    return plan


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
        raise Refused(f"{sha[:12]} is live at {live_paths[0]} — install a replacement first")
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
