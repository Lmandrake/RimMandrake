#!/usr/bin/env python3
"""artwrite.py — what an art SCRIPT uses instead of writing into src/**/Textures directly.

    import sys; sys.path.insert(0, "<repo>/src/RimMandrake/Utils/art")
    from artwrite import TextureWriter
    tw = TextureWriter(__file__)                 # reason = script:<repo-relative path of the caller>
    tw.copy(src_png, dest)                       # was shutil.copy2(src_png, dest)
    tw.save(img, dest)                           # was img.save(dest)
    tw.put(png_bytes, dest)                      # was Path(dest).write_bytes(...)
    tw.sync(textures_dir)                        # was shutil.rmtree(textures_dir) before regenerating:
                                                 #   retires PNGs under it this run did not write
    tw.report()                                  # one line; returns the refusal count

Every PNG goes through `artledger.install_bytes` (ART_VERSION_WRANGLING_1): the displaced picture
is archived in the art store first, a `live` event is appended to the ledger, and an OWNER-KEPT
picture is never replaced or retired — that file is left as it is and counted as `kept`. A non-PNG
file, or a file outside src/**/Textures/ (a preview sheet), is written plainly — the guard only
governs texture PNGs — so a script can route every write through it. A PNG aimed at some other
repo's Textures/ is refused.

Commit the ledger shard (infrastructure/state/art/events/<SEAT>.jsonl) with the art, or the
texture guard refuses the commit.
"""
from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artledger as L  # noqa: E402


class TextureWriter:
    def __init__(self, script: str, *, provenance: dict | None = None, dry_run: bool = False, quiet: bool = True):
        p = Path(script).resolve()
        try:
            name = p.relative_to(L.REPO_ROOT).as_posix()
        except ValueError:
            name = p.name
        self.reason = f"script:{name}"
        self.provenance = {"kind": "derived", "script": name, **(provenance or {})}
        self.dry_run = dry_run
        self.quiet = quiet
        self.written: set[Path] = set()
        self.counts = {"installed": 0, "unchanged": 0, "kept": 0, "retired": 0, "plain": 0}
        self.refusals: list[str] = []

    def _done(self, dest: Path, r: dict | None):
        self.written.add(dest.resolve())
        if r is None:
            return
        st = r.get("status")
        self.counts["unchanged" if st == "already-live" else "installed"] += 1

    def _ledgered(self, dest: Path) -> bool:
        """True for a PNG under this clone's src/**/Textures/ (goes through the ledger).
        A PNG under some OTHER Textures/ (a stale path to another repo) is refused; any
        other file (a preview sheet, a JPEG, a .dds) is written plainly."""
        if not str(dest).lower().endswith(".png"):
            return False
        try:
            L.locate(dest)
            return True
        except L.Refused:
            if "/Textures/" in str(dest).replace("\\", "/"):
                raise
            return False

    def put(self, data: bytes, dest) -> bool:
        dest = Path(dest)
        try:
            ledgered = self._ledgered(dest)
        except L.Refused as e:
            self.counts["kept"] += 1
            self.refusals.append(f"{dest}: {e}")
            print(f"art ledger REFUSED {dest}: {e}")
            return False
        if not ledgered:
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
            self.counts["plain"] += 1
            self.written.add(dest.resolve())
            return True
        try:
            r = L.install_bytes(dest, data, reason=self.reason, provenance=self.provenance, dry_run=self.dry_run)
        except L.Refused as e:
            self.written.add(dest.resolve())          # never retire what we were refused on
            self.counts["kept"] += 1
            self.refusals.append(f"{dest}: {e}")
            if not self.quiet:
                print(f"art ledger KEPT {dest}: {e}")
            return False
        self._done(dest, r)
        return True

    def copy(self, src, dest) -> bool:
        return self.put(Path(src).read_bytes(), dest)

    def save(self, img, dest, fmt: str | None = None, **kw) -> bool:
        """Drop-in for `img.save(dest, fmt, **kw)`."""
        dest = Path(dest)
        if (fmt or "PNG").upper() != "PNG" or not str(dest).lower().endswith(".png"):
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                img.save(dest, fmt, **kw) if fmt else img.save(dest, **kw)
            self.counts["plain"] += 1
            self.written.add(dest.resolve())
            return True
        b = io.BytesIO()
        img.save(b, "PNG", **kw)
        return self.put(b.getvalue(), dest)

    def sync(self, root) -> int:
        """Retire every PNG under `root` this writer did not produce (the ledger-safe form of
        rmtree-then-regenerate). Owner-kept pictures stay and are counted as kept."""
        root = Path(root)
        if not root.is_dir():
            return 0
        n = 0
        for f in sorted(root.rglob("*")):
            if not f.is_file() or f.resolve() in self.written:
                continue
            if f.suffix.lower() != ".png":
                if not self.dry_run:
                    f.unlink()
                continue
            if self.dry_run:
                n += 1
                continue
            try:
                L.retire(f, reason=self.reason)
                n += 1
            except L.Refused as e:
                self.counts["kept"] += 1
                self.refusals.append(f"{f}: {e}")
        self.counts["retired"] += n
        return n

    def report(self) -> int:
        c = self.counts
        if not any(c.values()):
            return 0
        print(f"art ledger ({self.reason}): {c['installed']} installed, {c['unchanged']} unchanged, "
              f"{c['retired']} retired, {c['kept']} left as owner-kept/refused"
              + (f", {c['plain']} non-PNG copied" if c["plain"] else "")
              + (f" — commit infrastructure/state/art/events/{L.seat()}.jsonl with the art"
                 if (c["installed"] or c["retired"]) and not self.dry_run else ""))
        for r in self.refusals[:10]:
            print(f"  kept: {r}")
        return len(self.refusals)
