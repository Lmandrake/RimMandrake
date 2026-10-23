#!/usr/bin/env python3
"""artledger.py — the ONE reader/writer of the art ledger (ART_VERSION_WRANGLING_1).

Design: design/RimMandrake/art_ledger_design_2026-10-04.md. This module is the library;
`art.py` is the CLI over it. Nothing else parses the shards.

Three stores, kept apart on purpose:
  * events  — infrastructure/state/art/events/<SEAT>.jsonl, git-tracked, append-only,
              merge=union (like the rimflow ledger). Facts about art; no pixels. Older events
              may sit in write-once events/archive/<SEAT>.<NNNN>.<from>_<to>.jsonl (`art.py
              rotate`); read them only through shard_files()/read_events(), never a glob.
  * bytes   — the content-addressed art store, D:\\ClaudeWork\\rimmandrake\\artstore\\<sha[:2]>\\<sha>.png,
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
  * his newer, explicit words can bring a purged picture back (2026-10-15): an `unpurge` event
    reverses the latest purge of that sha — append-only, owner words required, never usable by a
    mechanical install;
  * only an owner `keep` with plumbing/typed provenance PROTECTS; flawed-sheet, prefill and
    legacy-unresolved rulings are shown but protect nothing.
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
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
STORE_DEFAULT = Path(rm_str("artstore"))


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


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def put_file_checked(p) -> str:
    """`art.py put` / `install --file`: a supported way to get bytes into the store. The file must be a regular
    file (not a symlink), resolve inside this clone, and be a PNG. Returns the sha."""
    raw = Path(p)
    root = src_root().resolve().parent        # this clone (a fixture's root under ART_SRC_ROOT)
    if raw.is_symlink():
        raise Refused(f"{p} is a symlink — put the real file")
    rp = raw.resolve()
    try:
        rp.relative_to(root)
    except ValueError:
        raise Refused(f"{p} resolves to {rp}, outside this clone ({root}) — copy it into the clone first "
                      f"(Transient/ is fine)") from None
    if not rp.is_file():
        raise Refused(f"{p} is not a file")
    b = rp.read_bytes()
    if not b.startswith(PNG_MAGIC):
        raise Refused(f"{p} is not a PNG")
    return store_put_bytes(b)


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


# ── rotation (LOG_ROTATION, owner 2026-10-11: "we will need to rotate logs as needed") ──
# A seat's live shard events/<SEAT>.jsonl stays append-only. `rotate` MOVES a byte-exact prefix
# of it into events/archive/<SEAT>.<NNNN>.<YYYYMMDD>_<YYYYMMDD>.jsonl — written ONCE, never
# rewritten — so that concat(archives in seq order, live tail) == the old live file, byte for
# byte. Every reader therefore reads, per seat, archives (by seq) THEN the live tail, seats in the
# order the old `sorted(glob("*.jsonl"))` gave. Nothing else may glob the events dir.
ARCHIVE = "archive"
_ARCH_RE = re.compile(r"^(?P<seat>[^./]+)\.(?P<seq>\d{4})\.(?P<lo>\d{8})_(?P<hi>\d{8})\.jsonl$")
ROTATE_MIN_TAIL_LINES = 50          # union-merge context for a clone still holding the old file
ROTATE_MAX_CHUNK = 30 * 1024 * 1024  # each archive stays well under the 50 MB per-file rule


def order_shard_names(names) -> list[str]:
    """Order shard paths (relative or absolute; '/'-separated) for folding. Live `<SEAT>.jsonl`
    and `archive/<SEAT>.<seq>.<lo>_<hi>.jsonl`; anything else under events/ is an ERROR, never
    silently skipped (a skipped file is lost events)."""
    keyed = []
    for n in names:
        parts = str(n).replace("\\", "/").split("/")
        base, parent = parts[-1], (parts[-2] if len(parts) > 1 else "")
        if parent == ARCHIVE:
            m = _ARCH_RE.match(base)
            if not m:
                raise ValueError(f"{n}: not an art-ledger archive name (<SEAT>.<NNNN>.<from>_<to>.jsonl)")
            keyed.append(((m["seat"] + ".jsonl", 0, int(m["seq"])), n))
        elif base.endswith(".jsonl"):
            keyed.append(((base, 1, 0), n))
    return [n for _, n in sorted(keyed)]


def shard_files(d: Path | None = None) -> list[Path]:
    """Every event file under events/ (archives included), in fold order."""
    d = d or ledger_dir() / "events"
    if not d.is_dir():
        return []
    files = list(d.glob("*.jsonl"))
    if (d / ARCHIVE).is_dir():
        files += [p for p in (d / ARCHIVE).iterdir() if p.is_file()]
    return order_shard_names(files)


def read_events() -> list[dict]:
    out, seen = [], set()
    d = ledger_dir() / "events"
    if not d.is_dir():
        return out
    for f in shard_files(d):
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


def _day(line: bytes) -> str:
    try:
        return (json.loads(line).get("ts") or "")[:10].replace("-", "")
    except ValueError:
        return ""


def rotate_plan(seat_name: str, *, before: str | None = None, keep_bytes: int | None = None,
                d: Path | None = None) -> dict:
    """Plan moving a PREFIX of events/<seat>.jsonl into new archive files. Pure: writes nothing.
    `before`: move the longest prefix whose every event has ts < before (ISO, compared as text).
    `keep_bytes`: move the shortest prefix leaving a tail of at most keep_bytes.
    Always keeps ROTATE_MIN_TAIL_LINES lines live. The plan carries the exact bytes and proves
    concat(chunks) + tail == the original, so applying it can only ever be a pure move."""
    d = d or ledger_dir() / "events"
    live = d / f"{seat_name}.jsonl"
    raw = live.read_bytes()
    lines = raw.splitlines(keepends=True)
    if lines and not lines[-1].endswith(b"\n"):
        raise SystemExit(f"{live}: last line has no newline — a writer may be mid-append; retry")
    cap = max(0, len(lines) - ROTATE_MIN_TAIL_LINES)
    k = 0
    if before is not None:
        while k < cap:
            ln = lines[k]
            if ln.strip():
                try:
                    ts = json.loads(ln).get("ts") or ""
                except ValueError:
                    raise SystemExit(f"{live}:{k+1}: unparseable line; refusing to rotate") from None
                if not ts or ts >= before:
                    break
            k += 1
    elif keep_bytes is not None:
        tail = len(raw)
        while k < cap and tail > keep_bytes:
            tail -= len(lines[k])
            k += 1
    else:
        raise SystemExit("rotate: give --before or --keep-mb")
    seqs = [int(m["seq"]) for p in ((d / ARCHIVE).iterdir() if (d / ARCHIVE).is_dir() else [])
            if (m := _ARCH_RE.match(p.name)) and m["seat"] == seat_name]
    seq = max(seqs, default=0)
    chunks, cur, size = [], [], 0
    for ln in lines[:k]:
        if cur and size + len(ln) > ROTATE_MAX_CHUNK:
            chunks.append(cur); cur, size = [], 0
        cur.append(ln); size += len(ln)
    if cur:
        chunks.append(cur)
    archives = []
    for c in chunks:
        seq += 1
        days = sorted(x for x in (_day(ln) for ln in c if ln.strip()) if x) or ["00000000"]
        name = f"{seat_name}.{seq:04d}.{days[0]}_{days[-1]}.jsonl"
        archives.append({"name": name, "bytes": b"".join(c), "lines": len(c)})
    tail = b"".join(lines[k:])
    pure = b"".join(a["bytes"] for a in archives) + tail == raw
    return {"seat": seat_name, "live": live, "orig_sha": hashlib.sha256(raw).hexdigest(),
            "orig_bytes": len(raw), "orig_lines": len(lines), "moved_lines": k,
            "archives": archives, "tail": tail, "tail_lines": len(lines) - k, "pure_move": pure}


def rotate_apply(plan: dict) -> list[Path]:
    """Write the plan's archives (create-exclusive, fsync'd) then swap in the tail — only if the
    live file is still byte-identical to what was planned (a concurrent append refuses)."""
    if not plan["pure_move"]:
        raise SystemExit("rotate: plan is not a pure move — refusing")
    if not plan["archives"]:
        return []
    live: Path = plan["live"]
    adir = live.parent / ARCHIVE
    adir.mkdir(parents=True, exist_ok=True)
    if hashlib.sha256(live.read_bytes()).hexdigest() != plan["orig_sha"]:
        raise SystemExit(f"rotate: {live} changed since the plan (a writer appended) — re-plan")
    written = []
    for a in plan["archives"]:
        p = adir / a["name"]
        with open(p, "xb") as fh:          # never overwrite an archive
            fh.write(a["bytes"]); fh.flush(); os.fsync(fh.fileno())
        written.append(p)
    tmp = live.with_suffix(".jsonl.rotating")
    with open(tmp, "wb") as fh:
        fh.write(plan["tail"]); fh.flush(); os.fsync(fh.fileno())
    if hashlib.sha256(live.read_bytes()).hexdigest() != plan["orig_sha"]:
        tmp.unlink()
        for p in written:
            p.unlink()
        raise SystemExit(f"rotate: {live} changed during the rotation — rolled back, re-plan")
    os.replace(tmp, live)
    return written + [live]


# ─────────────────────────────────────────────────────── resource naming ──

FACING_RE = re.compile(r"^(?P<stem>.+?)_(?P<facing>north|east|south|west)(?P<mask>m?)$")


def parse_texfile(rel: str) -> dict:
    """'swanimals/Nuna/Nuna_f_eastm.png' -> {res, facing, mask}. rel is under Textures/."""
    rel = rel.replace("\\", "/")
    base = rel[:-4] if rel.lower().endswith(".png") else rel
    m = FACING_RE.match(base)
    if m:
        return {"res": m["stem"], "facing": m["facing"], "mask": bool(m["mask"])}
    # Graphic_Single's mask is <path>_m (Verse.Graphic_Single.MaskSuffix; Graphic_Collection skips "_m" files too)
    if base.endswith("_m"):
        return {"res": base[:-2], "facing": "single", "mask": True}
    return {"res": base, "facing": "single", "mask": False}


# ── mod / rel spelling (ART_LEDGER_REVIEW 2026-10-15 fix B) ──
# 58 `live` events were keyed under 17 non-canonical mod spellings ('SWBestiary', 'RimMandrake/FlowWorks', an
# absolute BENCH path …): the guard could not find them, `status` printed false SHADOWED flags. History is never
# rewritten: every READER folds keys through mod_key()/rel_key() (string rules + the explicit alias file), and every
# WRITER goes through canonical_mod(), which resolves on disk and refuses anything outside this clone's src/.
MOD_ALIASES_FILE = "mod_aliases.json"
_MOD_ALIASES: dict = {"sig": None, "map": {}}
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni", "Jawa")


def mod_aliases() -> dict:
    p = ledger_dir() / MOD_ALIASES_FILE
    try:
        sig = (str(p), p.stat().st_mtime_ns)
    except OSError:
        return {}
    if _MOD_ALIASES["sig"] != sig:
        _MOD_ALIASES.update(sig=sig, map=dict(json.loads(p.read_text()).get("aliases", {})))
    return _MOD_ALIASES["map"]


def mod_key(mod) -> str:
    """READ-side canonical key of a mod as written in any event: pure string rules plus the alias file.
    'SWBestiary' -> 'src/RimStarWars/SWBestiary' (alias), 'RimMandrake/FlowWorks' -> 'src/RimMandrake/FlowWorks',
    '/home/mandrake/rm/bench/src/RimMandrake/Abyss' -> 'src/RimMandrake/Abyss'."""
    m = str(mod or "").replace("\\", "/").rstrip("/")
    while m.startswith("./"):
        m = m[2:]
    if m.endswith("/Textures"):
        m = m[: -len("/Textures")]
    al = mod_aliases()
    if m in al:
        return al[m]
    if m.startswith("/"):
        i = m.rfind("/src/")
        if i >= 0:
            m = m[i + 1:]
    if m.split("/", 1)[0] in TIERS:
        m = "src/" + m
    return al.get(m, m)


def rel_key(rel) -> str:
    """READ-side canonical rel: forward slashes, no './', no leading 'Textures/'."""
    r = str(rel or "").replace("\\", "/")
    while r.startswith("./"):
        r = r[2:]
    if r.startswith("Textures/"):
        r = r[len("Textures/"):]
    return r


def canonical_mod(mod) -> str:
    """WRITE-side: any accepted spelling of a mod -> 'src/<Tier>/<Mod>' as the ledger keys it, resolved on disk.
    Accepts 'SWBestiary', 'RimStarWars/SWBestiary', 'src/RimStarWars/SWBestiary', a known alias, or an absolute
    path INSIDE this clone's src/. Refuses traversal, symlink escapes, other clones' paths and unknown mods."""
    raw = str(mod or "").strip()
    if not raw:
        raise Refused("no mod given")
    sroot = src_root().resolve()
    p = Path(raw.replace("\\", "/"))
    if p.is_absolute():
        cand = p.resolve()
    else:
        key = mod_key(raw)
        if key.startswith("src/"):
            cand = (sroot.parent / key).resolve()
        else:                                     # a bare mod name: exactly one src/<Tier>/<name> (or src/<name>)
            hits = [d for d in list(sroot.glob(f"*/{key}")) + [sroot / key] if d.is_dir()]
            if len(hits) != 1:
                raise Refused(f"mod {raw!r}: {len(hits)} folders under {sroot} match "
                              f"({', '.join(str(h) for h in hits[:4]) or 'none'}) — give src/<Tier>/<Mod>")
            cand = hits[0].resolve()
    if cand.name == "Textures":
        cand = cand.parent
    try:
        relp = cand.relative_to(sroot)
    except ValueError:
        raise Refused(f"mod {raw!r} resolves to {cand}, outside this clone's {sroot}") from None
    if not relp.parts or (cand.exists() and not cand.is_dir()):
        raise Refused(f"mod {raw!r} is not a mod folder under {sroot}")
    return f"{sroot.name}/{relp.as_posix()}"


IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tga", ".psd", ".dds", ".bmp")


def canonical_rel(rel) -> str:
    """WRITE-side rel: accepts 'a/b.png' or 'Textures/a/b.png'; refuses absolute paths and '..', and a name with
    no image extension (a rel without `.png` wrote 44 extension-less twins beside the PNGs, 2026-10-18)."""
    r = rel_key(rel)
    if r and not r.lower().endswith(IMAGE_EXTS):
        raise Refused(f"rel {rel!r} has no image extension ({'/'.join(IMAGE_EXTS)}) — install the file as its .png")
    if not r or r.startswith("/") or "/Textures/" in "/" + r or ".." in r.split("/"):
        raise Refused(f"rel must be the path UNDER Textures/, got {rel}")
    return r


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
        self._retired = {}                     # (mod, rel) -> the retire that emptied it (ordering tombstone)
        self.purged = {}                       # sha -> purge event, while a purge is its latest purge/unpurge
        self.unpurged = {}                     # sha -> unpurge event, while an unpurge is its latest (owner words)
        self.purge_history = defaultdict(list) # sha -> every purge/unpurge event, fold order (history kept whole)
        self.rejected = defaultdict(list)      # sha -> [rejected events: bytes an owner redo/reject named]
        self.snapshots = []
        self.bindings = defaultdict(list)      # sha -> [binding events: a job's target_def tied a render to a subject]
        self.bindings_by_subject = defaultdict(list)
        self.provenance_fixes = {}             # ruling id -> the latest provenance_fix correcting its authority fields
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
        elif t in ("purge", "unpurge"):
            self._fold_purge(ev)
        elif t == "rejected":
            self.rejected[ev["sha"]].append(ev)
        elif t == "snapshot":
            self.snapshots.append(ev)
        elif t == "binding":
            self.bindings[ev["sha"]].append(ev)
            self.bindings_by_subject[ev["subject"]].append(ev)
        elif t == "provenance_fix":
            cur = self.provenance_fixes.get(ev.get("corrects"))
            if cur is None or ev.get("ts", "") >= cur.get("ts", ""):
                self.provenance_fixes[ev.get("corrects")] = ev

    def authority(self, ruling: dict) -> dict:
        """A ruling's owner-authority fields (said / by_card / per_ruling) as corrected by the latest
        provenance_fix naming it. Past events are never edited; the correction is an appended event. It changes
        WHICH field records his authority, never whether the keep protects (verdict, by, trust stay)."""
        out = {k: ruling.get(k) for k in AUTHORITY_FIELDS if ruling.get(k)}
        fx = self.provenance_fixes.get(ruling.get("id"))
        if fx:
            out = {k: fx.get(k) for k in AUTHORITY_FIELDS if fx.get(k)}
        return out

    def _fold_live(self, ev):
        key = (mod_key(ev["mod"]), rel_key(ev["rel"]))      # history keeps its spelling; the fold does not
        # a retired slot keeps its retire as a tombstone: shards fold one seat after another, so an older install
        # read from a later shard must not resurrect a slot a newer retire emptied (BENCH retired Brightbell_p3a,
        # FOUNDRY's 01:00 install of it folded afterwards and read it live again, 2026-10-10)
        cur = self.live.get(key) or self._retired.get(key)
        follows = cur is not None and cur.get("sha") is not None and ev.get("prev") == cur.get("sha")
        if cur is None or follows or ev.get("ts", "") >= cur.get("ts", ""):
            if ev.get("sha") is None:           # retire: the file was archived and removed
                self.live.pop(key, None)
                self._retired[key] = ev
            else:
                self.live[key] = ev
                self._retired.pop(key, None)

    def _fold_purge(self, ev):
        """The latest of purge/unpurge is the state. Shards fold one seat after another, so 'latest' is causal first
        (an event whose `follows` names the current one comes after it; one the current names came before it), then
        by ts; a tie goes to the purge (fail safe: a picture stays deleted unless his later words clearly win)."""
        sha = ev["sha"]
        self.purge_history[sha].append(ev)
        cur = self.purged.get(sha) or self.unpurged.get(sha)
        if cur is not None:
            if cur.get("follows") == ev.get("id"):
                return                          # an older event folded late: the current one already follows it
            ts, cts = ev.get("ts", ""), cur.get("ts", "")
            if not (ev.get("follows") == cur.get("id") or ts > cts or (ts == cts and ev["type"] == "purge")):
                return
        if ev["type"] == "purge":
            self.purged[sha] = ev
            self.unpurged.pop(sha, None)
        else:
            self.unpurged[sha] = ev
            self.purged.pop(sha, None)

    def was_purged(self, sha: str) -> bool:
        """Ever purged, including a purge his later words reversed: a mechanical install may not bring it back."""
        return any(e.get("type") == "purge" for e in self.purge_history.get(sha, ()))

    def protected(self, sha: str) -> list[dict]:
        """Owner keeps with real provenance that name this sha and are not released."""
        keeps = [r for r in self.rulings_by_sha.get(sha, [])
                 if r.get("verdict") == "keep" and r.get("by") == "owner"
                 and r.get("trust") in TRUST_PROTECTS]
        # a release is per PICTURE: purging one facing of a kept column must not unprotect its siblings (it did:
        # 20 kept pictures, 7 of them live, lost their keep that way before 2026-10-09)
        released = {r.get("releases") for r in self.rulings if r.get("releases")
                    and (r.get("target") or {}).get("sha") in (None, sha)}
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

    def kept_but_purged(self) -> list[dict]:
        """Pictures whose bytes the owner purged while an owner keep on them is still active: the projection claims a
        protection that cannot be installed. REPORTED (art.py kept-purged), never auto-released or deleted."""
        out = []
        for sha, pev in sorted(self.purged.items()):
            keeps = self.protected(sha)
            if keeps:
                out.append({"sha": sha, "purge": pev, "keeps": keeps, "bytes_in_store": store_has(sha),
                            "live_at": self.live_anywhere(sha)})
        return out

    def live_anywhere(self, sha: str) -> list[str]:
        return [f"{m}/Textures/{r}" for (m, r), ev in self.live.items() if ev.get("sha") == sha]


_IDX: dict = {"sig": None, "idx": None}


def _shard_sig() -> tuple:
    d = ledger_dir() / "events"
    if not d.is_dir():
        return (str(d),)
    return (str(d),) + tuple((str(f), f.stat().st_size, f.stat().st_mtime_ns) for f in shard_files(d))


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


def script_writer(reason: str | None) -> Path | None:
    """The repo file a `script:<path> [note]` reason names, when it exists inside this clone; else None."""
    if not reason or not reason.startswith("script:"):
        return None
    tok = reason[len("script:"):].strip().split()
    if not tok:
        return None
    root = REPO_ROOT.resolve()
    p = (root / tok[0]).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None
    return p if p.is_file() else None


def mechanical_refusal(reason: str | None) -> str | None:
    """None when `reason` is a VERIFIABLE mechanical tag (2026-10-15 review fix C): `artpipe-collect`, or
    `script:<repo path> [note]` whose path is a file in this clone. Free text after `script:` ('decision taken by
    question card …', 'retire-duplicate') hid owner authority inside a mechanical tag, where protection does not
    apply — owner authority goes through --ruling / --owner-said instead."""
    if not is_mechanical_reason(reason):
        return (f"reason {reason!r} is not a mechanical tag (allowed: artpipe-collect | script:<repo path of the "
                f"writer>); an owner decision goes through --ruling <keep id> or --owner-said")
    if reason.startswith("script:") and script_writer(reason) is None:
        return (f"reason {reason!r} does not name a writer file in this clone (script:<repo-relative path> [note]); "
                f"an owner decision goes through --ruling <keep id> or --owner-said")
    return None


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
    except Exception:                                  # noqa: BLE001  not a readable image: not this gate's call
        return ""
    return f"{rel}: {why} — a placeholder is never installed ({PLACEHOLDER_RULE})" if why else ""


def case_twin_refusal(target: Path, stop: Path) -> str | None:
    """A path component of `target` (below `stop`) whose folder already holds a DIFFERENT entry with the
    same name ignoring case. Windows and the Mac are case-insensitive: git there cannot hold both, so a
    case-twin breaks every non-Linux clone (PaleTree_B beside the kept PaleTree_b, re-added by
    bulk_accept_renders.py 2026-10-19 after its retirement). Refused here, the lowest writer, so no caller can."""
    try:
        parts = target.relative_to(stop).parts
    except ValueError:
        return None
    cur = stop
    for name in parts:
        if cur.is_dir():
            low = name.casefold()
            for e in os.listdir(cur):
                if e != name and e.casefold() == low:
                    return (f"CASE-TWIN REFUSED: {cur / name} would sit beside existing {cur / e} — the same path "
                            f"on Windows and macOS, so git cannot hold both there. Install into the existing "
                            f"spelling ({e}) or retire it first; never write both.")
        cur = cur / name
    return None


AUTHORITY_FIELDS = ("said", "by_card", "per_ruling")


def correct_provenance(ruling_id: str, *, why: str, owner_said: str | None = None, by_card: str | None = None,
                       per_ruling: str | None = None, dry_run: bool = False) -> dict:
    """ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING: append a `provenance_fix` re-stating which field carries the owner's
    authority on an existing owner ruling (a card pick recorded under `said`, before install had --by-card). The
    fix states the WHOLE corrected set (a field it omits is no longer claimed); the original event is untouched."""
    idx = cached_index()
    r = next((x for x in idx.rulings if x.get("id") == ruling_id), None)
    if r is None:
        raise Refused(f"no ruling {ruling_id} in the ledger")
    if r.get("by") != "owner":
        raise Refused(f"ruling {ruling_id} is by {r.get('by')!r}, not the owner — nothing to re-attribute")
    if not (owner_said or by_card or per_ruling):
        raise Refused("a provenance fix must name the corrected authority (--owner-said / --by-card / --per-ruling)")
    if not why or not why.strip():
        raise Refused("a provenance fix needs --why: what was wrong")
    ev = {"type": "provenance_fix", "corrects": ruling_id, "was": {k: r.get(k) for k in AUTHORITY_FIELDS if r.get(k)},
          "why": why}
    for k, v in (("said", owner_said), ("by_card", by_card), ("per_ruling", per_ruling)):
        if v:
            ev[k] = v
    ev["id"] = det_id("provenance_fix", ruling_id, {k: ev.get(k) for k in AUTHORITY_FIELDS})
    if dry_run or ev["id"] in {e.get("id") for e in idx.events}:
        return {"status": "planned" if dry_run else "already-recorded", "event": ev}
    w = Writer({e["id"] for e in idx.events})
    w.add(ev)
    added = list(w.buf)
    w.flush()
    _absorb(added)
    return {"status": "recorded", "event": ev}


def owner_keep_ruling(sha: str, *, owner_said: str | None = None, by_card: str | None = None,
                      per_ruling: str | None = None) -> dict:
    """The owner keep an install records, one field per kind of his authority (CLAUDE.md "Owner authority on the
    ledger"): `said` = his words only, `by_card` = a card decision (our option label), `per_ruling` = a standing
    ruling cited by reference. The id is unchanged for a words-only keep (`ruling-cli`, sha, words) so a re-run
    stays idempotent against every keep recorded before these fields existed."""
    if owner_said and not by_card and not per_ruling:
        rid, via = det_id("ruling-cli", sha, owner_said), "art install (owner words)"
    else:
        rid = det_id("ruling-cli", sha, owner_said or "", "card", by_card or "", "per", per_ruling or "")
        via = "art install (by card)" if by_card else "art install (per ruling)"
    r = {"id": rid, "type": "ruling", "target": {"sha": sha}, "verdict": "keep", "by": "owner", "via": via,
         "trust": "ruled", "subject_key": ""}
    if owner_said:
        r["said"] = owner_said
    if by_card:
        r["by_card"] = by_card
    if per_ruling:
        r["per_ruling"] = per_ruling
    return r


def install(mod: str, rel: str, sha: str, *, ruling_id: str | None = None,
            owner_said: str | None = None, reason: str | None = None,
            provenance: dict | None = None, dry_run: bool = False,
            by_card: str | None = None, per_ruling: str | None = None, why: str | None = None) -> dict:
    """The only sanctioned writer into src/**/Textures. Ledger-checked; saves the old
    picture into the store FIRST; atomic write; appends a `live` event.

    Authorization, one of:
      * ruling_id: an owner keep (trust=ruled) naming the incoming sha;
      * owner_said: his typed words, recorded as an owner keep ruling;
      * by_card: a decision he took by question card ("question → picked option"; the label is OUR text, so
        it never goes in owner_said), recorded as an owner keep ruling carrying `by_card`;
      * per_ruling: a standing ruling of his cited by item id or ledger event, recorded as an owner keep ruling
        carrying `per_ruling` (ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING; rimflow's four provenance fields);
      * why: the acting agent's own reason (a delegated call: "delegated: art <verdict file>"). It grants NO
        owner authority: alone it installs under the mechanical guards (never over a kept, purged or
        rejected picture); beside an owner field it is recorded on the live event;
      * reason: a mechanical tag (`artpipe-collect`, `script:<repo path>`) for a writer
        installing without an owner decision. REFUSED when the displaced picture is
        protected by an owner keep — only his selection may replace a kept picture.
    """
    idx = cached_index()
    if idx.is_purged(sha):
        raise Refused(f"{sha[:12]} was purged by the owner — it cannot be installed")
    if not store_has(sha):
        raise Refused(f"{sha[:12]} is not in the art store ({store_dir()}) — put it there first "
                      f"(art.py put <png>, or art.py install ... --file <png>)")
    mod, rel = canonical_mod(mod), canonical_rel(rel)
    why_ph = placeholder_refusal(rel, store_get(sha))
    if why_ph:
        raise Refused(why_ph)
    target = src_root().resolve().parent / mod / "Textures" / rel
    try:
        target.parent.resolve().relative_to((src_root().resolve().parent / mod).resolve())
    except ValueError:
        raise Refused(f"{target} resolves outside {mod} (a symlinked folder?) — refusing to write through it") from None
    why_twin = case_twin_refusal(target, src_root().resolve().parent)
    if why_twin:
        raise Refused(why_twin)
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
    elif owner_said or by_card or per_ruling:
        if by_card is not None and not by_card.strip():
            raise Refused("--by-card needs the card's text: \"question → picked option\"")
        if per_ruling is not None and not per_ruling.strip():
            raise Refused("--per-ruling needs the ruling's item id or ledger event")
    elif reason or why:
        if reason:
            bad = mechanical_refusal(reason)
            if bad:
                raise Refused(bad + " (or --by-card / --per-ruling; an agent's own reason goes in --why)")
        elif not why.strip():
            raise Refused("--why needs the agent's reason in its own words")
        tag = reason or "agent --why"
        if idx.was_purged(sha):
            raise Refused(f"{sha[:12]} was purged by the owner (since unpurged by his words) — a mechanical install "
                          f"({tag}) may not bring it back; it needs his ruling (--ruling <keep id> or --owner-said)")
        bad = rejection_refusal(idx, rel, sha)
        if bad:
            raise Refused(bad + " — only his ruling can bring it back (--ruling <keep id> or --owner-said)")
    else:
        raise Refused("install needs an owner keep ruling id, the owner's typed words (--owner-said), his card pick "
                      "(--by-card), a standing ruling of his (--per-ruling), a mechanical reason "
                      "(artpipe-collect | script:<path>) or the agent's own reason (--why)")
    owner_kw = dict(owner_said=owner_said, by_card=by_card, per_ruling=per_ruling)
    owner_auth = bool(owner_said or by_card or per_ruling)
    old_sha = sha256_file(target) if target.is_file() else None
    if old_sha == sha:
        if owner_auth and not ruling_id and not dry_run and not idx.protected(sha):
            # his words / card / standing ruling about the picture already in place: record the ruling, write nothing
            w = Writer({e["id"] for e in idx.events})
            rl = owner_keep_ruling(sha, **owner_kw)
            w.add(rl)
            added = list(w.buf)
            w.flush()
            _absorb(added)
            return {"status": "already-live-ruled", "path": str(target), "new": sha, "ruling": rl["id"]}
        return {"status": "already-live", "path": str(target), "new": sha}
    old_protected = bool(old_sha and idx.protected(old_sha))
    if old_protected and not (ruling or owner_auth):
        raise Refused(f"{target} holds {old_sha[:12]}, an owner-KEPT picture — a mechanical "
                      f"install ({reason or 'agent --why'}) may not displace it; it needs his ruling "
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
    if owner_auth:
        ruling = owner_keep_ruling(sha, **owner_kw)
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
    live = {"type": "live", "mod": mod, "rel": rel, "sha": sha, "prev": old_sha}
    if ruling:
        live.update(ruling_id=ruling["id"], reason="install")
    else:
        live.update(reason=reason or "agent-why")
    if why:
        live["why"] = why
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


def held_elsewhere(idx, sha: str, key) -> bool:
    """True when another LIVE slot (not `key`) holds exactly this picture: retiring the duplicate slot
    loses no kept picture, so it needs no owner words (the 44 extension-less twins, 2026-10-18)."""
    return any(k != tuple(key) and ev.get("sha") == sha for k, ev in idx.live.items())


def retire(dest, *, reason: str | None = None, owner_said: str | None = None) -> dict:
    """Remove a Textures file through the ledger: archive, delete, `live` with sha None."""
    mod, rel = locate(dest)
    target = src_root().parent / mod / "Textures" / rel
    if not target.is_file():
        return {"status": "absent", "path": str(target)}
    idx = cached_index()
    old = sha256_file(target)
    if idx.protected(old) and not owner_said and not held_elsewhere(idx, old, (mod, rel)):
        raise Refused(f"{target} is owner-kept ({old[:12]}) — retiring it needs his words")
    if not owner_said:
        if not reason:
            raise Refused("retire needs the owner's words or a mechanical reason")
        why = mechanical_refusal(reason)
        if why:
            raise Refused(why)
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

def purge(sha: str, *, owner_said: str, via: str = "art purge", release_keep=False,
          release_from_sheet: tuple[str, str] | None = None, live_paths: list[str] | None = None) -> dict:
    """Reject+purge: the owner deletes an erroneous render so it stops polluting option
    space. Removes the bytes from the store and records a `purge` event; every sheet and
    every later registration skips the sha. Refuses a picture that is live in a mod
    (install something else first) or one he kept — never a silent release (2026-10-15 review: 79 purged pictures
    still carried an active keep). A keep is released only when NAMED:
      * release_keep=True — the owner's explicit `art purge --release-keep` (his words recorded on the release);
      * release_keep={keep ids} — exactly those keeps (enact: the keeps this same sheet row minted);
      * release_from_sheet=(via, row) — the keeps that same sheet row minted (ingest).
    Any other keep on the picture refuses the purge."""
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
    if release_keep is True:
        others = []
    else:
        named = set(release_keep or ())
        if release_from_sheet:
            sv, srow = release_from_sheet
            named |= {k["id"] for k in prot if k.get("via") == sv and (k.get("target") or {}).get("row") == srow}
        others = [k for k in prot if k["id"] not in named]
    if others:
        k = others[0]
        raise Refused(f"{sha[:12]} carries an owner keep ({k['id']}, {Path(k.get('via') or '').name or 'his words'}"
                      f"{': ' + repr(k.get('said'))[:80] if k.get('said') else ''}) — a purge never silently releases "
                      f"a keep; ask him, then `art.py purge {sha[:12]} --owner-said \"…\" --release-keep`")
    for k in prot:
        w.add({"type": "ruling", "id": det_id("release", k["id"], sha), "target": {"sha": sha},
               "verdict": "release", "releases": k["id"], "by": "owner", "said": owner_said,
               "trust": "ruled", "via": via})
    removed = False
    p = store_path(sha)
    if p.is_file():
        p.unlink()
        removed = True
    pev = {"type": "purge", "id": det_id("purge", sha), "sha": sha, "by": "owner",
           "said": owner_said, "via": via, "bytes_removed": removed}
    un = idx.unpurged.get(sha)
    if un:                                       # a re-purge after his unpurge: a new id (not deduped), ordered after it
        pev.update(id=det_id("purge", sha, un["id"]), follows=un["id"])
    w.add(pev)
    w.flush()
    return {"sha": sha, "bytes_removed": removed}


def unpurge(sha: str, *, owner_said: str, via: str = "art unpurge") -> dict:
    """Reverse the latest purge of `sha` on the owner's newer, explicit words (2026-10-15: he accepted on a later
    sheet a picture he had purged on an earlier one). Appends an `unpurge` event naming the purge it reverses; the
    purge stays in history. It restores nothing else: no keep (an install with --owner-said / --ruling records one),
    no bytes (put them in the store first if the purge deleted them), and a MECHANICAL install of a once-purged
    picture stays refused (install: was_purged). Owner words are the only authorisation — there is no mechanical or
    sheet route."""
    if not owner_said or not owner_said.strip():
        raise Refused("unpurge is the owner's act — it needs his typed words (--owner-said \"…\")")
    idx = Index()
    pev = idx.purged.get(sha)
    if not pev:
        raise Refused(f"{sha[:12]} is not purged — nothing to unpurge"
                      + (" (already unpurged)" if sha in idx.unpurged else ""))
    ev = {"type": "unpurge", "id": det_id("unpurge", sha, pev["id"]), "sha": sha, "by": "owner",
          "said": owner_said.strip(), "via": via, "follows": pev["id"], "bytes_in_store": store_has(sha)}
    w = Writer({e["id"] for e in idx.events})
    w.add(ev)
    w.flush()
    _absorb([ev])
    return {"sha": sha, "reverses": pev["id"], "bytes_in_store": ev["bytes_in_store"]}


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
    import decisions_v2 as DV        # schema 2 names letters in slots/pool/reject/retire/assign/asks too
    return {x for x in DV.letters(v) if x in SHEET_LETTERS}


def snapshot_versions(snap_path: Path) -> list[tuple]:
    """[(built datetime, snapshot dict)] for the file on disk and every git revision of it, oldest first."""
    import subprocess
    import datetime as _dt
    snap_path = Path(snap_path)

    def _ts(x):
        try:
            d = _dt.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
        except ValueError:
            return None
        return d if d.tzinfo else d.replace(tzinfo=_dt.timezone.utc)
    docs = []
    if snap_path.is_file():
        docs.append(json.loads(snap_path.read_text()))
    try:
        rel = snap_path.resolve().relative_to(REPO_ROOT).as_posix()
        revs = subprocess.run(["git", "-C", str(REPO_ROOT), "log", "--format=%H", "--", rel],
                              capture_output=True, text=True, check=True).stdout.split()
    except (ValueError, subprocess.CalledProcessError, OSError):
        revs = []
    for h in revs:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{h}:{rel}"], capture_output=True, text=True)
        if r.returncode:
            continue
        try:
            docs.append(json.loads(r.stdout))
        except ValueError:
            continue
    out = [(_ts(d.get("built")), d) for d in docs]
    return sorted((x for x in out if x[0]), key=lambda x: x[0])


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
